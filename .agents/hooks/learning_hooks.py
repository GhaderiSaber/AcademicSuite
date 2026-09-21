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
                    cand_agents = os.path.join(ws, ".agents", "state")
                    if os.path.isdir(cand_agents):
                        state_dir = cand_agents
                        break
                    cand = os.path.join(ws, "state")
                    if os.path.isdir(cand):
                        state_dir = cand
                        break
                    cand_alt = os.path.join(ws, "academic-state")
                    if os.path.isdir(cand_alt):
                        state_dir = cand_alt
                        break
                if not state_dir and workspaces:
                    cand_agents = os.path.join(workspaces[0], ".agents", "state")
                    state_dir = cand_agents if os.path.isdir(cand_agents) else os.path.join(workspaces[0], "state")
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
            "unspecified"
        )

    @staticmethod
    def _get_delegation_engine(payload: Dict[str, Any]):
        """Helper to obtain a DelegationEventEngine instance for the active workspace."""
        try:
            from scripts.delegation_event_engine import DelegationEventEngine
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
            return DelegationEventEngine(state_dir=state_dir, project_root=ROOT_DIR)
        except Exception as e:
            sys.stderr.write(f"[learning_hooks] Error initializing DelegationEventEngine: {e}\n")
            return None

    @staticmethod
    def _extract_delegation_fields(sa: Dict[str, Any], payload: Dict[str, Any], parent_agent: str) -> Dict[str, Any]:
        """Extracts the 8 mandatory delegation fields from subagent call."""
        prompt = sa.get("Prompt", "") if isinstance(sa, dict) else ""
        child_agent = sa.get("TypeName") or sa.get("Role") or payload.get("child_agent") or "specialist"

        task_id = None
        objective = None
        input_artifacts = []
        output_artifacts = []

        if prompt.strip().startswith("{") and prompt.strip().endswith("}"):
            try:
                data = json.loads(prompt)
                task_id = data.get("task_id")
                objective = data.get("objective")
                input_artifacts = data.get("inputs") or data.get("input_artifacts") or []
                output_artifacts = data.get("required_artifacts") or data.get("output_artifacts") or []
            except Exception:
                pass

        if not task_id:
            m_id = re.search(r"(?:task_id|Task ID|task):\s*([A-Za-z0-9_\-]+)", prompt, re.IGNORECASE)
            if m_id:
                task_id = m_id.group(1).strip()
            else:
                task_id = payload.get("taskId") or f"TSK-DEL-{str(child_agent).upper().replace('-', '_')}"

        if not objective:
            m_obj = re.search(r"(?:objective|Objective):\s*([^\n\r]+)", prompt, re.IGNORECASE)
            if m_obj:
                objective = m_obj.group(1).strip()
            else:
                first_line = prompt.split("\n")[0].strip() if prompt else ""
                objective = first_line[:150] if first_line else f"Execute {child_agent} workflow"

        if not input_artifacts:
            paths = re.findall(r"(?:[\w\-./]+(?:\.xlsx|\.csv|\.sav|\.json|\.parquet|\.txt|\.docx|\.md))", prompt)
            input_artifacts = list(dict.fromkeys(paths[:5]))

        if not output_artifacts:
            out_matches = re.findall(r"(?:expected|required|output|deliverable)[^\n:]*:\s*([^\n]+)", prompt, re.IGNORECASE)
            if out_matches:
                for om in out_matches:
                    p = re.findall(r"(?:[\w\-./]+(?:\.xlsx|\.csv|\.sav|\.json|\.parquet|\.txt|\.docx|\.md))", om)
                    output_artifacts.extend(p)
            output_artifacts = list(dict.fromkeys(output_artifacts[:5]))

        return {
            "parent_agent": parent_agent,
            "child_agent": child_agent,
            "task_id": task_id,
            "objective": objective,
            "input_artifacts": input_artifacts,
            "output_artifacts": output_artifacts
        }


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
                del_engine = LearningHooks._get_delegation_engine(payload)
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
                    # Phase 23: Record SUBAGENT_REQUESTED and SUBAGENT_STARTED
                    d_fields = LearningHooks._extract_delegation_fields(sa, payload, actor)
                    if del_engine:
                        try:
                            del_engine.record_subagent_requested(
                                parent_agent=d_fields["parent_agent"],
                                child_agent=d_fields["child_agent"],
                                task_id=d_fields["task_id"],
                                objective=d_fields["objective"],
                                input_artifacts=d_fields["input_artifacts"],
                                output_artifacts=d_fields["output_artifacts"],
                                details={"prompt_summary": sa.get("Prompt", "")[:200], "model": sa.get("Model", "")}
                            )
                            del_engine.record_subagent_started(
                                parent_agent=d_fields["parent_agent"],
                                child_agent=d_fields["child_agent"],
                                task_id=d_fields["task_id"],
                                objective=d_fields["objective"],
                                input_artifacts=d_fields["input_artifacts"],
                                output_artifacts=d_fields["output_artifacts"],
                                details={"prompt_summary": sa.get("Prompt", "")[:200], "model": sa.get("Model", "")}
                            )
                        except Exception as e_rec:
                            sys.stderr.write(f"[learning_hooks] Delegation record start error: {e_rec}\n")

        except Exception as e:
            sys.stderr.write(f"[learning_hooks] PreToolUse error: {e}\n")

        return {}

    @staticmethod
    def capture_user_correction(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scans user turn and transcript for corrections, critiques, or explicit instructions.
        Delegates to AcademicCorrectionDetector and AcademicIntegratedLearningHub, and records USER_CORRECTION event.
        Returns a dictionary with critique detection metadata.
        """
        transcript_path = payload.get("transcriptPath")
        cid = payload.get("conversationId")
        if not transcript_path and cid:
            cand = os.path.expanduser(f"~/.gemini/antigravity/brain/{cid}/.system_generated/logs/transcript.jsonl")
            if os.path.exists(cand):
                transcript_path = cand

        user_text = (
            payload.get("userMessage")
            or payload.get("prompt")
            or payload.get("message")
            or ""
        )
        last_step_idx = None

        if transcript_path and os.path.isfile(transcript_path):
            try:
                from scripts.academic_correction_detector import AcademicCorrectionDetector
                detector = AcademicCorrectionDetector(project_root=ROOT_DIR)
                detector.scan_transcript(transcript_path, mark_recorded=True)
            except Exception as e_det:
                sys.stderr.write(f"[learning_hooks] User correction scan note: {e_det}\n")

            records = load_transcript(transcript_path)
            for r in reversed(records):
                if r.get("type") == "USER_INPUT" and r.get("content"):
                    if not user_text:
                        user_text = r.get("content", "").strip()
                    last_step_idx = r.get("step_index")
                    break

        clean_user = re.sub(r"<[^>]+>", "", str(user_text)).strip()
        is_critique = False
        matched_term = None

        if clean_user:
            # Check for critique patterns
            critique_patterns = [
                r"\b(fix|wrong|incorrect|error|bug|fail|failed|failure|redo|re-run|reject|rejected|change|modify|correction|didn't trigger|did not trigger|problem)\b",
                r"اشتباه|غلط|اصلاح|تصحیح|مجدد|تکرار|رد شد|نادرست|خطا|مشکل"
            ]
            for pat in critique_patterns:
                m = re.search(pat, clean_user, re.IGNORECASE)
                if m:
                    is_critique = True
                    matched_term = m.group(0)
                    break

            if is_critique:
                engine = LearningHooks._get_engine(payload)
                if engine:
                    from scripts.trajectory_engine import TrajectoryEventType
                    engine.record_event(
                        TrajectoryEventType.USER_CORRECTION,
                        payload=payload,
                        details={"correction_text": clean_user[:500], "matched_term": matched_term},
                        actor="user"
                    )

            try:
                from scripts.academic_integrated_learning_hub import AcademicIntegratedLearningHub
                ws_paths = payload.get("workspacePaths", [])
                if ws_paths and os.path.isdir(ws_paths[0]):
                    base_ws = ws_paths[0]
                elif "PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules:
                    base_ws = None
                else:
                    base_ws = ROOT_DIR

                if base_ws:
                    hub = AcademicIntegratedLearningHub(base_dir=base_ws)
                    meta = {
                        "conversation_id": cid,
                        "source_transcript_path": transcript_path,
                        "turn_index": last_step_idx,
                        "workspace_paths": [base_ws]
                    }
                    hub.process_user_turn(user_text=clean_user, metadata=meta)
            except Exception as e_hub:
                sys.stderr.write(f"[learning_hooks] Hub user turn note: {e_hub}\n")

        return {
            "is_critique": is_critique,
            "text": clean_user,
            "matched_term": matched_term,
            "conversation_id": cid,
            "step_index": last_step_idx
        }

    @staticmethod
    def detect_recent_validation_failure(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Inspects trajectory events and recent reports for validation failures in the current session.
        """
        try:
            engine = LearningHooks._get_engine(payload)
            if engine:
                from scripts.trajectory_engine import TrajectoryEventType
                events = engine.load_events(event_types=[TrajectoryEventType.VALIDATION_FAILED.value])
                if events:
                    last_ev = events[-1]
                    details = last_ev.get("details", {})
                    return {
                        "validator_name": details.get("validator_name", "Validation Check"),
                        "summary": str(details.get("failed_checks") or details.get("error") or "Validation checks failed"),
                        "stage_dir": details.get("stage_dir", "")
                    }
        except Exception as e:
            sys.stderr.write(f"[learning_hooks] Detect validation failure note: {e}\n")
        return None

    @staticmethod
    def capture_validation_failure(stage_dir: str, validator_results: List[Dict[str, Any]]) -> None:
        """
        Records validation failure incidents in pitfalls registry, experience recorder,
        and trajectory_events.jsonl.
        """
        failed_results = [r for r in validator_results if str(r.get("verdict")).upper() == "FAIL"]
        if not failed_results:
            return

        cand_base = None
        if stage_dir:
            cand = os.path.dirname(os.path.abspath(stage_dir))
            while cand and cand != "/" and cand != ROOT_DIR:
                if "test_" in os.path.basename(cand) or "academic_" in os.path.basename(cand) or "tmp" in os.path.basename(cand) or os.path.isdir(os.path.join(cand, ".agents")):
                    cand_base = cand
                    break
                cand = os.path.dirname(cand)
        if not cand_base:
            if "PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules:
                cand_base = None
            else:
                cand_base = ROOT_DIR

        if not cand_base:
            return

        try:
            from scripts.trajectory_engine import TrajectoryEngine, TrajectoryEventType
            cand_state = os.path.join(os.path.dirname(stage_dir), "state")
            if not os.path.exists(cand_state):
                cand_state = os.path.join(cand_base, "state")
            if not os.path.exists(cand_state):
                cand_state = os.path.join(ROOT_DIR, "state")
            engine = TrajectoryEngine(state_dir=cand_state, project_root=cand_base)
            for fr in failed_results:
                engine.record_event(
                    TrajectoryEventType.VALIDATION_FAILED,
                    payload={"workspacePaths": [cand_base]},
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
            rec = AcademicExperienceRecorder(project_root=cand_base)
            rec.record_from_stage(stage_dir, outcome="FAILURE")
        except Exception as e_rec:
            sys.stderr.write(f"[learning_hooks] Experience recording note: {e_rec}\n")

        try:
            from scripts.academic_integrated_learning_hub import AcademicIntegratedLearningHub
            hub = AcademicIntegratedLearningHub(base_dir=cand_base)
            hub.process_validation_failure(
                stage_dir=stage_dir,
                validator_results=validator_results,
                is_challenger=False
            )
        except Exception as e_hub:
            sys.stderr.write(f"[learning_hooks] Hub validation failure note: {e_hub}\n")

    @staticmethod
    def capture_feedback_event(event_type: str, payload: Dict[str, Any], details: Optional[Dict[str, Any]] = None) -> None:
        """
        Secondary Enforcement (Feedback Event Detection):
        Records external feedback events (user corrections, validation failures, critic reviews)
        to trajectory event logs and learning registries.
        """
        try:
            engine = LearningHooks._get_engine(payload)
            if engine:
                actor = LearningHooks._extract_actor(payload)
                engine.record_event(
                    event_type=event_type,
                    payload=payload,
                    details=details or {},
                    actor=actor
                )
        except Exception as e:
            sys.stderr.write(f"[learning_hooks] Error capturing feedback event: {e}\n")

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
                    # Phase 23: Record SUBAGENT_COMPLETED / SUBAGENT_FAILED and ARTIFACT_RETURNED
                    subagents = tool_args.get("Subagents", [])
                    del_engine = LearningHooks._get_delegation_engine(payload)
                    if del_engine:
                        targets = subagents if subagents else [{"TypeName": payload.get("child_agent", "specialist"), "Prompt": ""}]
                        for sa in targets:
                            d_fields = LearningHooks._extract_delegation_fields(sa, payload, actor)
                            try:
                                if error:
                                    del_engine.record_subagent_failed(
                                        parent_agent=d_fields["parent_agent"],
                                        child_agent=d_fields["child_agent"],
                                        task_id=d_fields["task_id"],
                                        objective=d_fields["objective"],
                                        error_message=str(error),
                                        input_artifacts=d_fields["input_artifacts"],
                                        output_artifacts=d_fields["output_artifacts"],
                                        details={"error": error}
                                    )
                                else:
                                    del_engine.record_subagent_completed(
                                        parent_agent=d_fields["parent_agent"],
                                        child_agent=d_fields["child_agent"],
                                        task_id=d_fields["task_id"],
                                        objective=d_fields["objective"],
                                        output_artifacts=d_fields["output_artifacts"],
                                        input_artifacts=d_fields["input_artifacts"],
                                        details={"status": "SUCCESS"}
                                    )
                                    if d_fields["output_artifacts"]:
                                        del_engine.record_artifact_returned(
                                            parent_agent=d_fields["parent_agent"],
                                            child_agent=d_fields["child_agent"],
                                            task_id=d_fields["task_id"],
                                            objective=d_fields["objective"],
                                            output_artifacts=d_fields["output_artifacts"],
                                            input_artifacts=d_fields["input_artifacts"],
                                            details={"status": "RETURNED"}
                                        )
                            except Exception as e_ret:
                                sys.stderr.write(f"[learning_hooks] Delegation record return error: {e_ret}\n")

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
        if payload.get("track") == 1 or payload.get("mode") == "developer":
            return {}

        caller = (
            payload.get("agentName") or
            payload.get("agentRole") or
            payload.get("agent") or
            payload.get("caller") or ""
        ).lower().strip()

        # If caller is explicitly the Main Developer Agent, bypass academic reminders
        if caller and (caller in ("main", "main-agent", "mainagent", "default", "antigravity", "developer", "coding", "software-engineer", "code-agent") or payload.get("agent_type") == "main"):
            return {}

        critique_info = LearningHooks.capture_user_correction(payload)

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

        if critique_info and critique_info.get("is_critique"):
            clean_text = critique_info.get("text", "")[:300]
            critique_block = (
                "🧠 CONTINUOUS LEARNING TRIGGER ACTIVE (USER_FEEDBACK_DETECTED):\n"
                f"- User reported defect/critique: \"{clean_text}\"\n"
                "- Operational Mandate (Directive 19 & LEARNING_MULTI_AGENT_SPEC.md):\n"
                "  The user has reported a defect, error, or correction. You MUST trigger the diagnostic learning pipeline via native invoke_subagent:\n"
                f"  1. invoke_subagent(TypeName=\"trajectory-analyzer\", Prompt=\"Reconstruct observable actions, tool calls, and error trajectory for user critique: {clean_text}\")\n"
                "  2. invoke_subagent(TypeName=\"behavior-analyst\", Prompt=\"Perform causal root-cause analysis on the reconstructed trajectory to determine failure mechanism\")\n"
                "  3. invoke_subagent(TypeName=\"knowledge-curator\", Prompt=\"Catalog the diagnosed anti-pattern into state/pitfalls.jsonl\")\n"
                "- Prohibited Anti-Pattern: Do NOT perform silent, ad-hoc edits without executing the learning subagents."
            )
            ephemeral_blocks.append(critique_block)

        val_failure = LearningHooks.detect_recent_validation_failure(payload)
        if val_failure:
            val_summary = val_failure.get("summary", "Validation failed")[:300]
            val_block = (
                "⚠️ CONTINUOUS LEARNING TRIGGER ACTIVE (VALIDATION_FAILED):\n"
                f"- Recent Validation Failure: {val_summary}\n"
                "- Operational Mandate: If this failure indicates a systematic defect or exhausts the retry budget, "
                "you MUST invoke 'trajectory-analyzer' and 'behavior-analyst' to diagnose root cause and catalog the pitfall."
            )
            ephemeral_blocks.append(val_block)

        # Resolve transcript path for context analysis
        transcript_path = payload.get("transcriptPath")
        cid = payload.get("conversationId")
        if not transcript_path and cid:
            cand = os.path.expanduser(f"~/.gemini/antigravity/brain/{cid}/.system_generated/logs/transcript.jsonl")
            if os.path.exists(cand):
                transcript_path = cand

        # Model B: Deterministic Preflight Capability Routing for Academic Orchestrator
        # Executes academic_task_router.py offline/in-hook ("The Hands") to compile academic-state/routing_plan.json
        # and inject the deterministic capability plan into the orchestrator context.
        is_orchestrator = (
            caller in ("academic-orchestrator", "orchestrator")
            or not caller
        )
        if is_orchestrator:
            try:
                user_text = (
                    payload.get("userMessage")
                    or payload.get("prompt")
                    or payload.get("message")
                    or ""
                )
                if not user_text and transcript_path and os.path.isfile(transcript_path):
                    records = load_transcript(transcript_path)
                    for r in reversed(records):
                        if r.get("type") == "USER_INPUT" and r.get("content"):
                            user_text = r.get("content", "").strip()
                            break

                clean_prompt = re.sub(r"<[^>]+>", "", str(user_text)).strip()
                # Skip trivial queries or single words
                if clean_prompt and len(clean_prompt) >= 6:
                    from scripts.academic_task_router import route_and_persist_plan
                    routing_plan = route_and_persist_plan(
                        prompt=clean_prompt,
                        base_dir=ROOT_DIR
                    )
                    formula = routing_plan.get("capabilities_formula", "")
                    pipeline = routing_plan.get("pipeline", [])
                    steps_desc = "\n".join([
                        f"  Step {s['step']}: [{s['capability']}] -> {s['agent']} (Skill: {s['skill']}) [Output: {s['output_artifact']}]"
                        for s in pipeline
                    ])
                    plan_block = (
                        f"🧭 DETERMINISTIC CAPABILITY ROUTING PLAN (Model B / academic-state/routing_plan.json):\n"
                        f"- User Task: \"{clean_prompt[:120]}\"\n"
                        f"- Resolved Formula: {formula}\n"
                        f"- Ordered Execution Pipeline:\n{steps_desc}\n"
                        f"- Operational Invariant: academic-orchestrator is non-executing (Directive 20). Inspect 'academic-state/routing_plan.json' "
                        f"via view_file and delegate stages sequentially to specialist workers via invoke_subagent."
                    )
                    ephemeral_blocks.append(plan_block)
            except Exception as e_route:
                sys.stderr.write(f"[learning_hooks] PreInvocation task router note: {e_route}\n")

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
