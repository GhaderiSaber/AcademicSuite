#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/learning_hooks.py — Class C: Learning Hooks

Diagnostics, feedback capture, and lifecycle learning:
1. Capture user correction: Detects user critique and corrections from user turns and transcripts.
2. Capture validation failure: Intercepts validation failures and records causal incidents in pitfalls/experience logs.
3. Capture agent trajectory: Logs tool execution events and execution traces to state/audit_log.jsonl.

INVARIANT: Hooks are purely for interception, safety, diagnostics, and learning.
Hooks must NEVER act as the academic orchestrator.
"""

import os
import sys
import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def load_transcript(transcript_path: Optional[str]) -> List[Dict[str, Any]]:
    """Loads and parses transcript.jsonl safely."""
    if not transcript_path or not os.path.exists(transcript_path):
        return []
    records = []
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    except Exception as e:
        sys.stderr.write(f"[learning_hooks] Error reading transcript: {e}\n")
    return records


class LearningHooks:
    """
    Class C: Learning Hooks
    Captures user corrections, validation failures, and agent trajectories for continuous learning.
    """

    @staticmethod
    def _get_engine(payload: Dict[str, Any]):
        """Helper to obtain a TrajectoryEngine instance for the active workspace."""
        try:
            from scripts.trajectory_engine import TrajectoryEngine
            workspaces = payload.get("workspacePaths", [])
            state_dir = None
            if workspaces:
                for ws in workspaces:
                    cand = os.path.join(ws, "state")
                    if os.path.isdir(cand):
                        state_dir = cand
                        break
                    cand_alt = os.path.join(ws, "academic-state")
                    if os.path.isdir(cand_alt):
                        state_dir = cand_alt
                        break
                if not state_dir and workspaces:
                    state_dir = os.path.join(workspaces[0], "state")
            return TrajectoryEngine(state_dir=state_dir, project_root=ROOT_DIR)
        except Exception as e:
            sys.stderr.write(f"[learning_hooks] Error initializing TrajectoryEngine: {e}\n")
            return None

    @staticmethod
    def _extract_actor(payload: Dict[str, Any]) -> str:
        return (
            payload.get("agentName") or
            payload.get("agentRole") or
            payload.get("agent") or
            payload.get("caller") or
            "academic-orchestrator"
        )

    @staticmethod
    def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        PreToolUse hook: intercepts tool invocations before execution.
        Emits TOOL_CALLED, and specific events: FILE_READ, FILE_WRITTEN,
        COMMAND_STARTED, VALIDATION_STARTED, AGENT_INVOKED.
        """
        try:
            from scripts.trajectory_engine import (
                TrajectoryEventType,
                READ_TOOLS,
                WRITE_TOOLS,
                is_validation_command,
                sanitize_tool_args
            )
            engine = LearningHooks._get_engine(payload)
            if not engine:
                return {}

            tool_call = payload.get("toolCall", {})
            tool_name = tool_call.get("name", "") if isinstance(tool_call, dict) else ""
            tool_args = tool_call.get("args", {}) if isinstance(tool_call, dict) else {}
            sanitized_args = sanitize_tool_args(tool_args)
            actor = LearningHooks._extract_actor(payload)

            # 1. TOOL_CALLED
            engine.record_event(
                TrajectoryEventType.TOOL_CALLED,
                payload=payload,
                details={"arguments_summary": sanitized_args},
                actor=actor
            )

            # 2. Specific event classifications
            if tool_name in READ_TOOLS:
                file_path = tool_args.get("AbsolutePath") or tool_args.get("TargetFile") or tool_args.get("Url") or ""
                engine.record_event(
                    TrajectoryEventType.FILE_READ,
                    payload=payload,
                    details={"file_path": file_path, "arguments": sanitized_args},
                    actor=actor
                )

            elif tool_name in WRITE_TOOLS:
                file_path = tool_args.get("TargetFile") or tool_args.get("AbsolutePath") or ""
                engine.record_event(
                    TrajectoryEventType.FILE_WRITTEN,
                    payload=payload,
                    details={"file_path": file_path, "overwrite": tool_args.get("Overwrite", False)},
                    actor=actor
                )

            elif tool_name == "run_command":
                cmd_line = tool_args.get("CommandLine", "")
                engine.record_event(
                    TrajectoryEventType.COMMAND_STARTED,
                    payload=payload,
                    details={"command_line": cmd_line, "cwd": tool_args.get("Cwd", "")},
                    actor=actor
                )
                if is_validation_command(cmd_line):
                    engine.record_event(
                        TrajectoryEventType.VALIDATION_STARTED,
                        payload=payload,
                        details={"command_line": cmd_line, "validator_type": "script"},
                        actor=actor
                    )

            elif tool_name == "invoke_subagent":
                subagents = tool_args.get("Subagents", [])
                for sa in subagents:
                    engine.record_event(
                        TrajectoryEventType.AGENT_INVOKED,
                        payload=payload,
                        details={
                            "subagent_type": sa.get("TypeName", ""),
                            "subagent_role": sa.get("Role", ""),
                            "prompt_summary": sa.get("Prompt", "")[:200]
                        },
                        actor=actor
                    )

        except Exception as e:
            sys.stderr.write(f"[learning_hooks] PreToolUse error: {e}\n")

        return {}

    @staticmethod
    def capture_user_correction(payload: Dict[str, Any]) -> None:
        """
        Scans user turn and transcript for corrections, critiques, or explicit instructions.
        Delegates to AcademicCorrectionDetector and AcademicIntegratedLearningHub, and records USER_CORRECTION event.
        """
        transcript_path = payload.get("transcriptPath")
        cid = payload.get("conversationId")
        if not transcript_path and cid:
            cand = os.path.expanduser(f"~/.gemini/antigravity/brain/{cid}/.system_generated/logs/transcript.jsonl")
            if os.path.exists(cand):
                transcript_path = cand

        if transcript_path and os.path.isfile(transcript_path):
            try:
                from scripts.academic_correction_detector import AcademicCorrectionDetector
                detector = AcademicCorrectionDetector(project_root=ROOT_DIR)
                detector.scan_transcript(transcript_path, mark_recorded=True)
            except Exception as e_det:
                sys.stderr.write(f"[learning_hooks] User correction scan note: {e_det}\n")

            records = load_transcript(transcript_path)
            last_user_msg = ""
            last_step_idx = None
            for r in reversed(records):
                if r.get("type") == "USER_INPUT" and r.get("content"):
                    last_user_msg = r.get("content", "").strip()
                    last_step_idx = r.get("step_index")
                    break

            clean_user = re.sub(r"<[^>]+>", "", last_user_msg).strip()
            if clean_user:
                # Check for critique patterns
                critique_patterns = [
                    r"\b(fix|wrong|incorrect|error|bug|fail|redo|re-run|reject|change|modify|correction)\b",
                    r"اشتباه|غلط|اصلاح|تصحیح|مجدد|تکرار|رد شد|نادرست|خطا"
                ]
                if any(re.search(pat, clean_user, re.IGNORECASE) for pat in critique_patterns):
                    engine = LearningHooks._get_engine(payload)
                    if engine:
                        from scripts.trajectory_engine import TrajectoryEventType
                        engine.record_event(
                            TrajectoryEventType.USER_CORRECTION,
                            payload=payload,
                            details={"correction_text": clean_user[:500]},
                            actor="user"
                        )

                try:
                    from scripts.academic_integrated_learning_hub import AcademicIntegratedLearningHub
                    hub = AcademicIntegratedLearningHub(base_dir=ROOT_DIR)
                    meta = {
                        "conversation_id": cid,
                        "source_transcript_path": transcript_path,
                        "turn_index": last_step_idx,
                        "workspace_paths": payload.get("workspacePaths", [ROOT_DIR])
                    }
                    hub.process_user_turn(user_text=clean_user, metadata=meta)
                except Exception as e_hub:
                    sys.stderr.write(f"[learning_hooks] Hub user turn note: {e_hub}\n")

    @staticmethod
    def capture_validation_failure(stage_dir: str, validator_results: List[Dict[str, Any]]) -> None:
        """
        Records validation failure incidents in pitfalls registry, experience recorder,
        and trajectory_events.jsonl.
        """
        failed_results = [r for r in validator_results if str(r.get("verdict")).upper() == "FAIL"]
        if not failed_results:
            return

        try:
            from scripts.trajectory_engine import TrajectoryEngine, TrajectoryEventType
            cand_state = os.path.join(os.path.dirname(stage_dir), "state")
            if not os.path.exists(cand_state):
                cand_state = os.path.join(ROOT_DIR, "state")
            engine = TrajectoryEngine(state_dir=cand_state, project_root=ROOT_DIR)
            for fr in failed_results:
                engine.record_event(
                    TrajectoryEventType.VALIDATION_FAILED,
                    payload={"workspacePaths": [ROOT_DIR]},
                    details={
                        "validator_name": fr.get("validator_name", "Validator"),
                        "failed_checks": fr.get("failed_checks", []),
                        "stage_dir": stage_dir
                    },
                    actor="validation-agent"
                )
        except Exception as e_ev:
            sys.stderr.write(f"[learning_hooks] Trajectory validation failure note: {e_ev}\n")

        try:
            from scripts.academic_experience_recorder import AcademicExperienceRecorder
            rec = AcademicExperienceRecorder(project_root=ROOT_DIR)
            rec.record_from_stage(stage_dir, outcome="FAILURE")
        except Exception as e_rec:
            sys.stderr.write(f"[learning_hooks] Experience recording note: {e_rec}\n")

        try:
            from scripts.academic_integrated_learning_hub import AcademicIntegratedLearningHub
            hub = AcademicIntegratedLearningHub(base_dir=ROOT_DIR)
            hub.process_validation_failure(
                stage_dir=stage_dir,
                validator_results=validator_results,
                is_challenger=False
            )
        except Exception as e_hub:
            sys.stderr.write(f"[learning_hooks] Hub validation failure note: {e_hub}\n")

    @staticmethod
    def capture_agent_trajectory(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        PostToolUse hook: logs tool completion events, sanitized arguments,
        and exit status to trajectory_events.jsonl and audit_log.jsonl.
        Emits TOOL_RETURNED, and if applicable: COMMAND_FINISHED, AGENT_RETURNED.
        """
        try:
            from scripts.trajectory_engine import (
                TrajectoryEventType,
                is_validation_command,
                sanitize_tool_args
            )
            engine = LearningHooks._get_engine(payload)

            cid = payload.get("conversationId", "")
            error = payload.get("error")
            tool_call = payload.get("toolCall", {})

            tool_name = tool_call.get("name", "") if isinstance(tool_call, dict) else ""
            tool_args = tool_call.get("args", {}) if isinstance(tool_call, dict) else {}

            transcript_path = payload.get("transcriptPath")
            if not tool_name:
                if not transcript_path and cid:
                    cand = os.path.expanduser(f"~/.gemini/antigravity/brain/{cid}/.system_generated/logs/transcript.jsonl")
                    if os.path.exists(cand):
                        transcript_path = cand
                records = load_transcript(transcript_path) if transcript_path else []
                for r in reversed(records):
                    tcs = r.get("tool_calls", [])
                    if tcs:
                        last_tc = tcs[-1]
                        if isinstance(last_tc, dict):
                            tool_name = last_tc.get("name", "")
                            tool_args = last_tc.get("args", {})
                        break

            sanitized_args = sanitize_tool_args(tool_args)
            actor = LearningHooks._extract_actor(payload)

            if engine:
                # 1. TOOL_RETURNED
                engine.record_event(
                    TrajectoryEventType.TOOL_RETURNED,
                    payload=payload,
                    details={
                        "arguments_summary": sanitized_args,
                        "error": error,
                        "status": "ERROR" if error else "SUCCESS"
                    },
                    actor=actor
                )

                # 2. Specific completions
                if tool_name == "run_command":
                    cmd_line = tool_args.get("CommandLine", "")
                    engine.record_event(
                        TrajectoryEventType.COMMAND_FINISHED,
                        payload=payload,
                        details={
                            "command_line": cmd_line,
                            "error": error,
                            "status": "ERROR" if error else "SUCCESS"
                        },
                        actor=actor
                    )
                    if is_validation_command(cmd_line) and error:
                        engine.record_event(
                            TrajectoryEventType.VALIDATION_FAILED,
                            payload=payload,
                            details={
                                "command_line": cmd_line,
                                "error": error,
                                "validator_type": "script"
                            },
                            actor="validation-agent"
                        )

                elif tool_name == "invoke_subagent":
                    engine.record_event(
                        TrajectoryEventType.AGENT_RETURNED,
                        payload=payload,
                        details={
                            "error": error,
                            "status": "ERROR" if error else "SUCCESS"
                        },
                        actor=actor
                    )

        except Exception as e:
            sys.stderr.write(f"[learning_hooks] Error writing trajectory events: {e}\n")

        return {}

    @staticmethod
    def handle_pre_invocation(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        PreInvocation hook (Phase 28 Execution Boundary):
        1. Scans for user corrections.
        2. Injects constitutional reminder.
        3. Deterministically retrieves adaptive context (lessons, pitfalls, methodology rules)
           for detected academic tasks and injects it into ephemeral context before execution.
        """
        caller = (
            payload.get("agentName") or
            payload.get("agentRole") or
            payload.get("agent") or
            payload.get("caller") or ""
        ).lower()

        # If caller is explicitly the Main Developer Agent, bypass academic reminders
        if caller in ("main", "main-agent", "mainagent", "default", "antigravity", "developer", "coding", "software-engineer", "code-agent") or payload.get("agent_type") == "main":
            return {}

        LearningHooks.capture_user_correction(payload)

        reminder = (
            "🚨 CONSTITUTIONAL ENFORCEMENT ACTIVE (Directive 0, 3 & 11):\n"
            "1. Binary Honesty Protocol: If asked a compliance question, your response MUST begin with 'Yes' or 'No'.\n"
            "2. Micro-Stages, Triad Artifacts & One-Hypothesis-One-Stage Invariant (Directive 3): Monolithic drafting in one shot is prohibited. "
            "Every section and individual hypothesis must generate a synchronized triad of disk artifacts: .docx (Word), .md (Markdown), and .json (Data/Stats) before assembly.\n"
            "3. Interactive Stage-Gate Protocol (Directive 11): At the end of each stage, emit the Stage Completion Report "
            "(What was done + What will be done next), then STOP and wait for user confirmation before advancing.\n"
            "4. Multi-Agent Integrity: Under NO circumstance claim a multi-agent workflow unless you physically invoked "
            "subagents via 'invoke_subagent'.\n"
            "5. Sole Orchestrator Mandate (Directive 12.1): Antigravity is the sole agent runtime. Python scripts are strictly "
            "deterministic execution tools ('The Hands'). Never run agent emulators."
        )

        ephemeral_blocks = [reminder]

        # Phase 28: Deterministic Context Retrieval at the Execution Boundary
        try:
            from scripts.academic_adaptive_context_boundary import AcademicAdaptiveContextBoundary
            boundary = AcademicAdaptiveContextBoundary(base_dir=ROOT_DIR)
            briefing = boundary.retrieve_for_turn(payload)
            if briefing:
                ephemeral_blocks.append(briefing)
        except Exception as e_bnd:
            sys.stderr.write(f"[learning_hooks] Boundary adaptive context note: {e_bnd}\n")

        full_message = "\n\n---\n".join(ephemeral_blocks)

        return {
            "injectSteps": [
                {
                    "ephemeralMessage": full_message
                }
            ]
        }


def main():
    import json
    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[learning_hooks] Error parsing stdin JSON: {e}\n")

    event = payload.get("event", "PostToolUse")
    if event == "PreInvocation":
        res = LearningHooks.handle_pre_invocation(payload)
    else:
        res = LearningHooks.capture_agent_trajectory(payload)
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
