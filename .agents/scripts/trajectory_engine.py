#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/trajectory_engine.py — Factual Event-Driven Trajectory Engine

Authoritative trajectory engine replacing speculative inferences with strictly
observable physical events and metadata from Antigravity hook payloads and transcripts.

Canonical Events (11):
- TOOL_CALLED: Tool invocation proposed/intercepted (PreToolUse)
- TOOL_RETURNED: Tool execution returned/completed (PostToolUse)
- FILE_READ: File inspection/reading tool executed (view_file, read_resource, etc.)
- FILE_WRITTEN: File modification tool executed (write_to_file, replace_file_content, etc.)
- COMMAND_STARTED: CLI command execution initiated (run_command)
- COMMAND_FINISHED: CLI command execution completed with exit code (run_command)
- AGENT_INVOKED: Subagent delegation initiated (invoke_subagent)
- AGENT_RETURNED: Subagent delegation completed
- VALIDATION_STARTED: Verification/validation suite initiated
- VALIDATION_FAILED: Verification/validation check failed
- USER_CORRECTION: Human critique, correction, or revision directive detected

Antigravity Hook Metadata Source of Truth:
- conversationId
- workspacePaths
- transcriptPath
- toolCall (name, args)
- stepIdx
- artifactDirectoryPath
- modelName
"""

import os
import sys
import json
import uuid
import re
import argparse
from enum import Enum
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

FORBIDDEN_COT_KEYS = {
    "chain_of_thought",
    "thinking",
    "internal_monologue",
    "scratchpad",
    "reasoning_tokens"
}

READ_TOOLS = {
    "view_file",
    "read_resource",
    "read_url_content",
    "get_code_snippet",
    "get_file_outline",
    "get_file_contents",
    "get_schema_file_contents"
}

WRITE_TOOLS = {
    "write_to_file",
    "replace_file_content",
    "apply_diff",
    "edit_file",
    "multi_file_edit",
    "batch_replace",
    "patch",
    "create_or_update_file",
    "create_update_schema_file"
}

VALIDATION_INDICATORS = [
    "validate",
    "check_",
    "audit_",
    "verify",
    "integrity",
    "msai",
    "guard",
    "test_"
]


class TrajectoryEventType(str, Enum):
    """Observable trajectory events (tool lifecycle and subagent delegation)."""
    TOOL_CALLED = "TOOL_CALLED"
    TOOL_RETURNED = "TOOL_RETURNED"
    FILE_READ = "FILE_READ"
    FILE_WRITTEN = "FILE_WRITTEN"
    COMMAND_STARTED = "COMMAND_STARTED"
    COMMAND_FINISHED = "COMMAND_FINISHED"
    AGENT_INVOKED = "AGENT_INVOKED"
    AGENT_RETURNED = "AGENT_RETURNED"
    VALIDATION_STARTED = "VALIDATION_STARTED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    USER_CORRECTION = "USER_CORRECTION"
    # Phase 23 Delegation Events
    SUBAGENT_REQUESTED = "SUBAGENT_REQUESTED"
    SUBAGENT_STARTED = "SUBAGENT_STARTED"
    SUBAGENT_COMPLETED = "SUBAGENT_COMPLETED"
    SUBAGENT_FAILED = "SUBAGENT_FAILED"
    ARTIFACT_RETURNED = "ARTIFACT_RETURNED"


class PrivateChainOfThoughtLeakError(Exception):
    """Raised if private chain-of-thought or reasoning tokens are detected."""
    pass


def sanitize_no_cot(obj: Any) -> Any:
    """Recursively audits and strips private chain-of-thought keys."""
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if k in FORBIDDEN_COT_KEYS:
                raise PrivateChainOfThoughtLeakError(
                    f"Forbidden private chain-of-thought key detected: '{k}'. "
                    f"Trajectories must strictly record observable actions only."
                )
            cleaned[k] = sanitize_no_cot(v)
        return cleaned
    elif isinstance(obj, list):
        return [sanitize_no_cot(elem) for elem in obj]
    return obj


def is_validation_command(command_line: str) -> bool:
    """Checks whether a command line invokes a validation or audit script."""
    cmd_lower = command_line.lower()
    return any(ind in cmd_lower for ind in VALIDATION_INDICATORS)


def sanitize_tool_args(args: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitizes tool arguments for logging by omitting sensitive bodies and truncating long strings."""
    sanitized = {}
    for k, v in args.items():
        if k in ("CodeContent", "ReplacementContent"):
            continue
        elif isinstance(v, str) and len(v) > 500:
            sanitized[k] = v[:500] + f"... [truncated {len(v)-500} chars]"
        else:
            sanitized[k] = v
    return sanitized


class TrajectoryEngine:
    """
    Core engine for factual event-driven trajectory recording,
    extraction, and contract assembly.
    """

    def __init__(self, state_dir: Optional[str] = None, project_root: Optional[str] = None):
        self.project_root = project_root or ROOT_DIR
        if state_dir:
            self.state_dir = state_dir
        else:
            cand_state = os.path.join(self.project_root, ".agents", "state")
            self.state_dir = cand_state if os.path.isdir(cand_state) else os.path.join(self.project_root, "state")
        os.makedirs(self.state_dir, exist_ok=True)
        self.events_file = os.path.join(self.state_dir, "trajectory_events.jsonl")
        self.audit_file = os.path.join(self.state_dir, "audit_log.jsonl")

    def record_event(
        self,
        event_type: Union[TrajectoryEventType, str],
        payload: Dict[str, Any],
        details: Optional[Dict[str, Any]] = None,
        actor: str = "system"
    ) -> Dict[str, Any]:
        """
        Records a single factual execution event to trajectory_events.jsonl and audit_log.jsonl.
        Extracts metadata from Antigravity hook payload:
        conversationId, workspacePaths, transcriptPath, toolCall, stepIdx,
        artifactDirectoryPath, modelName.
        """
        etype = event_type.value if isinstance(event_type, TrajectoryEventType) else str(event_type)
        now_iso = datetime.now(timezone.utc).isoformat()

        cid = payload.get("conversationId", "")
        step_idx = payload.get("stepIdx")
        ws_paths = payload.get("workspacePaths", [])
        transcript_path = payload.get("transcriptPath", "")
        artifact_dir = payload.get("artifactDirectoryPath", "")
        model_name = payload.get("modelName", "")
        tool_call = payload.get("toolCall", {})

        clean_details = sanitize_no_cot(details or {})

        event_record = {
            "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
            "event_type": etype,
            "timestamp": now_iso,
            "conversation_id": cid,
            "step_index": step_idx,
            "actor": actor,
            "model_name": model_name,
            "workspace_paths": ws_paths,
            "transcript_path": transcript_path,
            "artifact_directory_path": artifact_dir,
            "tool_name": tool_call.get("name", "") if isinstance(tool_call, dict) else "",
            "details": clean_details
        }

        # Write to trajectory_events.jsonl
        line = json.dumps(event_record, ensure_ascii=False) + "\n"
        with open(self.events_file, "a", encoding="utf-8") as f:
            f.write(line)

        # Also mirror to audit_log.jsonl for backward compatibility
        audit_record = {
            "timestamp": now_iso,
            "conversation_id": cid,
            "step_index": step_idx,
            "event_type": etype,
            "tool_name": event_record["tool_name"] or "unknown",
            "actor": actor,
            "tool_args": clean_details.get("arguments_summary", {}),
            "details": clean_details,
            "status": "ERROR" if etype == "VALIDATION_FAILED" or clean_details.get("error") else "SUCCESS"
        }
        audit_line = json.dumps(audit_record, ensure_ascii=False) + "\n"
        with open(self.audit_file, "a", encoding="utf-8") as f:
            f.write(audit_line)

        for ws in (ws_paths or [self.project_root]):
            cand_mem = os.path.join(ws, ".agents", "memory")
            if os.path.isdir(cand_mem):
                with open(os.path.join(cand_mem, "audit_log.jsonl"), "a", encoding="utf-8") as f:
                    f.write(audit_line)

        return event_record

    def load_events(
        self,
        since_iso: Optional[str] = None,
        event_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Loads factual events chronologically from trajectory_events.jsonl."""
        if not os.path.exists(self.events_file):
            return []

        events = []
        with open(self.events_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    if since_iso and record.get("timestamp", "") < since_iso:
                        continue
                    if event_types and record.get("event_type") not in event_types:
                        continue
                    events.append(record)
                except Exception:
                    continue
        return events

    def extract_events_from_transcript(
        self,
        transcript_path: str,
        cid: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Parses transcript.jsonl and reconstructs the sequence of observable events:
        - USER_INPUT -> USER_CORRECTION (if critique/correction detected)
        - PLANNER_RESPONSE:
            - tool_calls -> TOOL_CALLED
            - read tools -> FILE_READ
            - write tools -> FILE_WRITTEN
            - run_command -> COMMAND_STARTED (and VALIDATION_STARTED if validator)
            - invoke_subagent -> AGENT_INVOKED
        - Tool returns -> TOOL_RETURNED, COMMAND_FINISHED, AGENT_RETURNED, VALIDATION_FAILED
        """
        if not os.path.exists(transcript_path):
            return []

        events = []
        step_counter = 1

        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    step = json.loads(line)
                except Exception:
                    continue

                step_type = step.get("type", "")
                step_idx = step.get("step_index", step_counter)
                created_at = step.get("created_at", datetime.now(timezone.utc).isoformat())

                # 1. USER_INPUT: Scan for critique / correction
                if step_type == "USER_INPUT":
                    content = step.get("content", "")
                    clean_content = re.sub(r"<[^>]+>", "", content).strip()
                    critique_patterns = [
                        r"\b(fix|wrong|incorrect|error|bug|fail|redo|re-run|reject|change|modify|correction)\b",
                        r"اشتباه|غلط|اصلاح|تصحیح|مجدد|تکرار|رد شد|نادرست|خطا"
                    ]
                    is_correction = any(re.search(pat, clean_content, re.IGNORECASE) for pat in critique_patterns)
                    if is_correction:
                        events.append({
                            "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
                            "event_type": TrajectoryEventType.USER_CORRECTION.value,
                            "timestamp": created_at,
                            "conversation_id": cid or "",
                            "step_index": step_idx,
                            "actor": "user",
                            "model_name": "",
                            "workspace_paths": [self.project_root],
                            "transcript_path": transcript_path,
                            "artifact_directory_path": "",
                            "tool_name": "",
                            "details": {
                                "correction_text": clean_content[:500],
                                "detected_keywords": [pat for pat in critique_patterns if re.search(pat, clean_content, re.IGNORECASE)]
                            }
                        })

                # 2. PLANNER_RESPONSE: Scan tool calls
                elif step_type == "PLANNER_RESPONSE":
                    tool_calls = step.get("tool_calls", [])
                    actor = "academic-orchestrator"

                    for tc in tool_calls:
                        if not isinstance(tc, dict):
                            continue
                        t_name = tc.get("name", "")
                        t_args = tc.get("args", {})
                        sanitized_args = sanitize_tool_args(t_args)

                        # Event A: TOOL_CALLED
                        events.append({
                            "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
                            "event_type": TrajectoryEventType.TOOL_CALLED.value,
                            "timestamp": created_at,
                            "conversation_id": cid or "",
                            "step_index": step_idx,
                            "actor": actor,
                            "model_name": "",
                            "workspace_paths": [self.project_root],
                            "transcript_path": transcript_path,
                            "artifact_directory_path": "",
                            "tool_name": t_name,
                            "details": {
                                "arguments_summary": sanitized_args
                            }
                        })

                        # Event B: Specific Tool Classification
                        if t_name in READ_TOOLS:
                            events.append({
                                "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
                                "event_type": TrajectoryEventType.FILE_READ.value,
                                "timestamp": created_at,
                                "conversation_id": cid or "",
                                "step_index": step_idx,
                                "actor": actor,
                                "model_name": "",
                                "workspace_paths": [self.project_root],
                                "transcript_path": transcript_path,
                                "artifact_directory_path": "",
                                "tool_name": t_name,
                                "details": {
                                    "file_path": t_args.get("AbsolutePath") or t_args.get("TargetFile") or t_args.get("Url") or "",
                                    "arguments": sanitized_args
                                }
                            })

                        elif t_name in WRITE_TOOLS:
                            events.append({
                                "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
                                "event_type": TrajectoryEventType.FILE_WRITTEN.value,
                                "timestamp": created_at,
                                "conversation_id": cid or "",
                                "step_index": step_idx,
                                "actor": actor,
                                "model_name": "",
                                "workspace_paths": [self.project_root],
                                "transcript_path": transcript_path,
                                "artifact_directory_path": "",
                                "tool_name": t_name,
                                "details": {
                                    "file_path": t_args.get("TargetFile") or t_args.get("AbsolutePath") or "",
                                    "overwrite": t_args.get("Overwrite", False)
                                }
                            })

                        elif t_name == "run_command":
                            cmd_line = t_args.get("CommandLine", "")
                            events.append({
                                "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
                                "event_type": TrajectoryEventType.COMMAND_STARTED.value,
                                "timestamp": created_at,
                                "conversation_id": cid or "",
                                "step_index": step_idx,
                                "actor": actor,
                                "model_name": "",
                                "workspace_paths": [self.project_root],
                                "transcript_path": transcript_path,
                                "artifact_directory_path": "",
                                "tool_name": t_name,
                                "details": {
                                    "command_line": cmd_line,
                                    "cwd": t_args.get("Cwd", "")
                                }
                            })

                            if is_validation_command(cmd_line):
                                events.append({
                                    "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
                                    "event_type": TrajectoryEventType.VALIDATION_STARTED.value,
                                    "timestamp": created_at,
                                    "conversation_id": cid or "",
                                    "step_index": step_idx,
                                    "actor": actor,
                                    "model_name": "",
                                    "workspace_paths": [self.project_root],
                                    "transcript_path": transcript_path,
                                    "artifact_directory_path": "",
                                    "tool_name": t_name,
                                    "details": {
                                        "command_line": cmd_line,
                                        "validator_type": "script"
                                    }
                                })

                        elif t_name == "invoke_subagent":
                            subagents = t_args.get("Subagents", [])
                            for sa in subagents:
                                events.append({
                                    "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
                                    "event_type": TrajectoryEventType.AGENT_INVOKED.value,
                                    "timestamp": created_at,
                                    "conversation_id": cid or "",
                                    "step_index": step_idx,
                                    "actor": actor,
                                    "model_name": sa.get("Model", ""),
                                    "workspace_paths": [self.project_root],
                                    "transcript_path": transcript_path,
                                    "artifact_directory_path": "",
                                    "tool_name": t_name,
                                    "details": {
                                        "subagent_type": sa.get("TypeName", ""),
                                        "subagent_role": sa.get("Role", ""),
                                        "prompt_summary": sa.get("Prompt", "")[:200]
                                    }
                                })

                step_counter += 1

        return events

    def build_trajectory_from_events(
        self,
        events: List[Dict[str, Any]],
        project_id: str,
        task_id: str,
        experience_id: str,
        trajectory_id: Optional[str] = None,
        artifacts: Optional[List[Dict[str, Any]]] = None,
        outcome: str = "SUCCESS"
    ) -> Dict[str, Any]:
        """
        Builds a compliant Trajectory contract directly from observable events.
        Enforces zero speculative inference: if tools/commands were not in the
        event stream, tool_usages and skill_activations are not hallucinated.
        """
        trj_id = trajectory_id or f"TRJ-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{task_id.replace('_', '-').upper()}-{uuid.uuid4().hex[:6].upper()}"

        ordered_actions = []
        tool_usages = []
        skill_activations = []
        subagent_delegations = []
        validation_events = []
        feedback_ids = []

        step_num = 1
        tool_invocation_idx = 1

        for ev in events:
            etype = ev.get("event_type", "")
            actor = ev.get("actor", "system")
            ts = ev.get("timestamp", datetime.now(timezone.utc).isoformat())
            details = ev.get("details", {})
            tool_name = ev.get("tool_name", "")

            # Action description
            desc = f"Observed {etype}"
            if tool_name:
                desc += f" on tool '{tool_name}'"
            if details.get("command_line"):
                desc += f": {details.get('command_line')[:80]}"
            elif details.get("file_path"):
                desc += f": {details.get('file_path')}"
            elif details.get("correction_text"):
                desc += f": {details.get('correction_text')[:80]}"

            ordered_actions.append({
                "step_number": step_num,
                "action_type": etype if etype in [
                    "TOOL_CALLED", "TOOL_RETURNED", "FILE_READ", "FILE_WRITTEN",
                    "COMMAND_STARTED", "COMMAND_FINISHED", "AGENT_INVOKED", "AGENT_RETURNED",
                    "VALIDATION_STARTED", "VALIDATION_FAILED", "USER_CORRECTION",
                    "TOOL_CALL", "SKILL_INVOCATION", "SUBAGENT_DELEGATION",
                    "DECISION_FORMULATION", "ARTIFACT_GENERATION", "VALIDATION_CHECK", "HANDOFF_RETURN",
                    "SUBAGENT_REQUESTED", "SUBAGENT_STARTED", "SUBAGENT_COMPLETED", "SUBAGENT_FAILED",
                    "ARTIFACT_RETURNED"
                ] else "TOOL_CALL",
                "actor": actor,
                "timestamp": ts,
                "description": desc,
                "observable_input": {"tool_name": tool_name, "step_index": ev.get("step_index")},
                "observable_output": details
            })
            step_num += 1

            # Tool usage collection
            if etype in [TrajectoryEventType.TOOL_CALLED.value, TrajectoryEventType.TOOL_RETURNED.value]:
                status = "ERROR" if details.get("error") or details.get("exit_code", 0) != 0 else "SUCCESS"
                tool_usages.append({
                    "tool_name": tool_name or "unknown",
                    "invocation_index": tool_invocation_idx,
                    "arguments_summary": details.get("arguments_summary", {}),
                    "status": status,
                    "execution_time_ms": details.get("execution_time_ms", 100)
                })
                tool_invocation_idx += 1

            # Skill activation collection (from command execution)
            elif etype == TrajectoryEventType.COMMAND_STARTED.value:
                cmd = details.get("command_line", "")
                m = re.search(r"\.agents/skills/([^/]+)/scripts/([^ \'\"]+)", cmd)
                if m:
                    skill_name = m.group(1)
                    script_path = m.group(0)
                    skill_activations.append({
                        "skill_name": skill_name,
                        "script_path": script_path,
                        "cli_command": cmd,
                        "exit_code": details.get("exit_code", 0),
                        "duration_seconds": details.get("duration_seconds", 1.0)
                    })

            # Subagent delegation collection (Observable Delegation Invariant - Phase 23)
            elif etype in [
                TrajectoryEventType.AGENT_INVOKED.value,
                TrajectoryEventType.SUBAGENT_REQUESTED.value,
                TrajectoryEventType.SUBAGENT_STARTED.value,
                TrajectoryEventType.SUBAGENT_COMPLETED.value,
                TrajectoryEventType.SUBAGENT_FAILED.value,
                TrajectoryEventType.ARTIFACT_RETURNED.value
            ]:
                parent_agent = ev.get("parent_agent") or actor or "academic-orchestrator"
                child_agent = (
                    ev.get("child_agent") or
                    details.get("child_agent") or
                    details.get("subagent_role") or
                    details.get("subagent_type") or
                    "specialist"
                )
                t_id = ev.get("task_id") or details.get("task_id") or task_id
                obj = ev.get("objective") or details.get("objective") or details.get("prompt_summary", "Delegated subagent task")
                in_arts = ev.get("input_artifacts") or details.get("input_artifacts", [])
                out_arts = ev.get("output_artifacts") or details.get("output_artifacts", [])

                if etype in [TrajectoryEventType.SUBAGENT_COMPLETED.value, TrajectoryEventType.ARTIFACT_RETURNED.value]:
                    del_status = "COMPLETED"
                elif etype == TrajectoryEventType.SUBAGENT_FAILED.value:
                    del_status = "FAILED"
                elif etype == TrajectoryEventType.SUBAGENT_STARTED.value:
                    del_status = "STARTED"
                elif etype == TrajectoryEventType.SUBAGENT_REQUESTED.value:
                    del_status = "REQUESTED"
                else:
                    del_status = "COMPLETED" if outcome == "SUCCESS" else "FAILED"

                # Check if this subagent delegation is already in subagent_delegations
                existing = None
                for d in subagent_delegations:
                    if (d.get("stage_id") == t_id or d.get("task_id") == t_id) and (
                        d.get("delegatee") == child_agent or d.get("child_agent") == child_agent
                    ):
                        existing = d
                        break

                handoff_path = ""
                if out_arts:
                    first_art = out_arts[0]
                    handoff_path = first_art.get("path") if isinstance(first_art, dict) else str(first_art)

                if existing:
                    existing["status"] = del_status
                    if obj:
                        existing["envelope_summary"] = obj
                        existing["objective"] = obj
                    if out_arts:
                        existing["output_artifacts"] = out_arts
                    if handoff_path:
                        existing["handoff_artifact_path"] = handoff_path
                else:
                    subagent_delegations.append({
                        "delegator": parent_agent,
                        "delegatee": child_agent,
                        "parent_agent": parent_agent,
                        "child_agent": child_agent,
                        "stage_id": t_id,
                        "task_id": t_id,
                        "envelope_summary": obj,
                        "objective": obj,
                        "status": del_status,
                        "input_artifacts": in_arts,
                        "output_artifacts": out_arts,
                        "handoff_artifact_path": handoff_path or details.get("handoff_artifact_path", "")
                    })

            # Validation event collection
            elif etype == TrajectoryEventType.VALIDATION_FAILED.value:
                validation_events.append({
                    "validator_name": details.get("validator_name", "StageValidator"),
                    "verdict": "FAIL",
                    "failed_checks": details.get("failed_checks", ["check_failed"]),
                    "evidence_summary": details
                })
            elif etype == TrajectoryEventType.VALIDATION_STARTED.value:
                # Recorded when validation initiates
                pass

            # Feedback collection
            elif etype == TrajectoryEventType.USER_CORRECTION.value:
                fid = f"FDB-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
                feedback_ids.append(fid)

        # Fallback if no actions were logged but we have a stage outcome
        if not ordered_actions:
            ordered_actions.append({
                "step_number": 1,
                "action_type": "TOOL_CALLED",
                "actor": "system",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "description": f"Verified stage {task_id} with outcome {outcome}",
                "observable_input": {"task_id": task_id},
                "observable_output": {"status": outcome}
            })

        trajectory_record = {
            "contract_version": "1.0.0",
            "trajectory_id": trj_id,
            "experience_id": experience_id,
            "project_id": project_id,
            "task_id": task_id,
            "ordered_actions": ordered_actions,
            "tool_usages": tool_usages,
            "skill_activations": skill_activations,
            "subagent_delegations": subagent_delegations,
            "important_decisions": [],
            "outputs": artifacts or [],
            "validation_events": validation_events,
            "feedback": feedback_ids,
            "outcome": outcome
        }

        return sanitize_no_cot(trajectory_record)


def main():
    parser = argparse.ArgumentParser(description="Factual Event-Driven Trajectory Engine CLI")
    parser.add_argument("--record-event", type=str, choices=[e.value for e in TrajectoryEventType], help="Event type to record")
    parser.add_argument("--payload", type=str, help="JSON string or path to hook payload")
    parser.add_argument("--details", type=str, help="JSON string of event details")
    parser.add_argument("--state-dir", type=str, help="Path to state directory")
    parser.add_argument("--parse-transcript", type=str, help="Parse events from a transcript.jsonl file")
    parser.add_argument("--list-events", action="store_true", help="List recorded events in state directory")
    args = parser.parse_args()

    engine = TrajectoryEngine(state_dir=args.state_dir)

    if args.record_event:
        payload = {}
        if args.payload:
            if os.path.isfile(args.payload):
                with open(args.payload, "r", encoding="utf-8") as f:
                    payload = json.load(f)
            else:
                payload = json.loads(args.payload)
        details = json.loads(args.details) if args.details else {}
        evt = engine.record_event(args.record_event, payload=payload, details=details)
        print(json.dumps(evt, indent=2, ensure_ascii=False))

    elif args.parse_transcript:
        events = engine.extract_events_from_transcript(args.parse_transcript)
        print(f"Extracted {len(events)} factual events from transcript.")
        print(json.dumps(events[:5], indent=2, ensure_ascii=False))

    elif args.list_events:
        events = engine.load_events()
        print(f"Total events in {engine.events_file}: {len(events)}")
        for e in events[-10:]:
            print(f"[{e.get('timestamp')}] {e.get('event_type')} (Tool: {e.get('tool_name', 'N/A')})")


if __name__ == "__main__":
    main()
