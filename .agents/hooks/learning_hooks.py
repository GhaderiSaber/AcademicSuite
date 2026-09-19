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
    def capture_user_correction(payload: Dict[str, Any]) -> None:
        """
        Scans user turn and transcript for corrections, critiques, or explicit instructions.
        Delegates to AcademicCorrectionDetector and AcademicIntegratedLearningHub.
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
            for r in reversed(records):
                if r.get("type") == "USER_INPUT" and r.get("content"):
                    last_user_msg = r.get("content", "").strip()
                    break

            clean_user = re.sub(r"<[^>]+>", "", last_user_msg).strip()
            if clean_user:
                try:
                    from scripts.academic_integrated_learning_hub import AcademicIntegratedLearningHub
                    hub = AcademicIntegratedLearningHub(base_dir=ROOT_DIR)
                    hub.process_user_turn(user_text=clean_user)
                except Exception as e_hub:
                    sys.stderr.write(f"[learning_hooks] Hub user turn note: {e_hub}\n")

    @staticmethod
    def capture_validation_failure(stage_dir: str, validator_results: List[Dict[str, Any]]) -> None:
        """
        Records validation failure incidents in pitfalls registry and experience recorder.
        """
        failed_results = [r for r in validator_results if str(r.get("verdict")).upper() == "FAIL"]
        if not failed_results:
            return

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
        PostToolUse hook: logs tool call execution events and sanitized arguments to audit_log.jsonl.
        """
        try:
            workspaces = payload.get("workspacePaths", [])
            audit_dirs = []
            if workspaces:
                for ws in workspaces:
                    cand_state = os.path.join(ws, "state")
                    cand_mem = os.path.join(ws, ".agents", "memory")
                    if os.path.exists(cand_state):
                        audit_dirs.append(cand_state)
                    if os.path.exists(cand_mem):
                        audit_dirs.append(cand_mem)
                    if not audit_dirs:
                        audit_dirs.append(cand_state)
                        os.makedirs(cand_state, exist_ok=True)
            else:
                default_state = os.path.join(ROOT_DIR, "state")
                default_mem = os.path.join(ROOT_DIR, ".agents", "memory")
                if os.path.exists(default_state):
                    audit_dirs.append(default_state)
                if os.path.exists(default_mem):
                    audit_dirs.append(default_mem)
                if not audit_dirs:
                    audit_dirs.append(default_state)
                    os.makedirs(default_state, exist_ok=True)

            cid = payload.get("conversationId", "")
            step_idx = payload.get("stepIdx")
            error = payload.get("error")
            tool_call = payload.get("toolCall", {})

            tool_name = tool_call.get("name", "")
            tool_args = tool_call.get("args", {})

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

            sanitized_args = {k: v for k, v in tool_args.items() if k not in ("CodeContent", "ReplacementContent")}

            event_record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "conversation_id": cid,
                "step_index": step_idx,
                "tool_name": tool_name or "unknown",
                "tool_args": sanitized_args,
                "error": error,
                "status": "ERROR" if error else "SUCCESS"
            }

            record_line = json.dumps(event_record, ensure_ascii=False) + "\n"
            for ad in set(audit_dirs):
                audit_file = os.path.join(ad, "audit_log.jsonl")
                with open(audit_file, "a", encoding="utf-8") as f:
                    f.write(record_line)

        except Exception as e:
            sys.stderr.write(f"[learning_hooks] Error writing audit log: {e}\n")

        return {}

    @staticmethod
    def handle_pre_invocation(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        PreInvocation hook:
        1. Scans for user corrections.
        2. Injects constitutional reminder.
        """
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
        return {
            "injectSteps": [
                {
                    "ephemeralMessage": reminder
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
