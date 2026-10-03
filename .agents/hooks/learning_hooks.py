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

HOOKS_DIR = os.path.dirname(os.path.realpath(__file__))
AGENTS_DIR = os.path.dirname(HOOKS_DIR)
ROOT_DIR = os.path.dirname(AGENTS_DIR)
for p in (ROOT_DIR, AGENTS_DIR, HOOKS_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from contracts.hook_identity_contract import resolve_transcript_path, is_main_agent_developer
    from contracts.critique_detection_contract import is_meaningful_user_critique, extract_clean_user_message
    from contracts.current_work_resolver import resolve_current_work_stage_dirs, get_current_work_validation_reports
except ImportError:
    try:
        from .contracts.hook_identity_contract import resolve_transcript_path, is_main_agent_developer
        from .contracts.critique_detection_contract import is_meaningful_user_critique, extract_clean_user_message
        from .contracts.current_work_resolver import resolve_current_work_stage_dirs, get_current_work_validation_reports
    except ImportError:
        def resolve_transcript_path(payload):
            return payload.get("transcriptPath") if isinstance(payload, dict) else None
        def is_main_agent_developer(payload):
            return payload.get("track") in (1, "1", "track_1", "developer") or payload.get("mode") == "developer"
        def is_meaningful_user_critique(user_text, **kw):
            return False, None
        def extract_clean_user_message(raw_text):
            return re.sub(r"<[^>]+>", "", str(raw_text)).strip()
        def resolve_current_work_stage_dirs(*args, **kwargs):
            return []
        def get_current_work_validation_reports(*args, **kwargs):
            return []


def load_transcript(transcript_path: Optional[str]) -> List[Dict[str, Any]]:
    """Loads and parses transcript safely, preferring untruncated transcript_full.jsonl if present."""
    if not transcript_path:
        return []
    target_path = transcript_path
    if os.path.basename(transcript_path) == "transcript.jsonl":
        full_candidate = os.path.join(os.path.dirname(transcript_path), "transcript_full.jsonl")
        if os.path.isfile(full_candidate) and os.path.getsize(full_candidate) > 0:
            target_path = full_candidate
    if not os.path.exists(target_path):
        target_path = transcript_path
    if not os.path.exists(target_path):
        return []
    records = []
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    except Exception as e:
        sys.stderr.write(f"[learning_hooks] Error reading transcript ({target_path}): {e}\n")
        if target_path != transcript_path and os.path.exists(transcript_path):
            try:
                with open(transcript_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            records.append(json.loads(line))
            except Exception:
                pass
    return records


class LearningHooks:
    """
    Class C: Learning Hooks
    Captures user corrections, validation failures, and agent trajectories for continuous learning.
    """
    _captured_validation_failures: Set[str] = set()

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
            if isinstance(tool_call, dict) and tool_call:
                tool_name = tool_call.get("name", "")
                tool_args = tool_call.get("args", {}) or {}
            else:
                tool_name = payload.get("tool_name", "") or payload.get("tool", "")
                tool_args = payload.get("args", {}) or payload.get("tool_args", {}) or {}
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
                parsed_sa = subagents
                if isinstance(subagents, str):
                    try:
                        parsed_sa = json.loads(subagents)
                    except Exception:
                        parsed_sa = []

                if isinstance(parsed_sa, list):
                    del_engine = LearningHooks._get_delegation_engine(payload)
                    for sa in parsed_sa:
                        if not isinstance(sa, dict):
                            continue
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

                # Phase 28: Execution Boundary Injection for Dispatched Subagents
                try:
                    from scripts.academic_adaptive_context_boundary import AcademicAdaptiveContextBoundary
                    boundary = AcademicAdaptiveContextBoundary(base_dir=ROOT_DIR)
                    enriched_subagents = boundary.enrich_subagent_dispatch(subagents, payload=payload)
                    if enriched_subagents and enriched_subagents != subagents:
                        return {
                            "decision": "allow",
                            "overwrite": {
                                "Subagents": enriched_subagents
                            }
                        }
                except Exception as e_enrich:
                    sys.stderr.write(f"[learning_hooks] invoke_subagent enrichment note: {e_enrich}\n")

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
        is_sub = (
            payload.get("isSubagent") is True
            or bool(payload.get("parentConversationId"))
            or bool(payload.get("parent_conversation_id"))
        )
        if is_sub:
            return {"is_critique": False, "text": "", "matched_term": None}

        caller = LearningHooks._extract_actor(payload).lower().strip()
        cid = payload.get("conversationId")
        transcript_path = resolve_transcript_path(payload)

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

        clean_user = extract_clean_user_message(user_text)
        is_critique, matched_term = is_meaningful_user_critique(
            clean_user,
            is_subagent=is_sub,
            caller=caller
        )

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

        if clean_user:
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
        Inspects trajectory events, workspace validation reports, and recent transcript
        for validation failures in the current session.
        """
        # Step 0: Check if learning was already completed across the conversation (Remediation Phase)
        transcript_path = resolve_transcript_path(payload)
        records = load_transcript(transcript_path) if transcript_path else []

        latest_eval_idx = -1
        latest_val_after_eval = False

        if records:
            for idx, r in enumerate(records):
                for tc in r.get("tool_calls", []):
                    if (tc.get("name") or "").lower() == "invoke_subagent":
                        subs = tc.get("args", {}).get("Subagents", [])
                        if isinstance(subs, str):
                            try:
                                subs = json.loads(subs)
                            except Exception:
                                subs = []
                        for s in (subs if isinstance(subs, list) else []):
                            if isinstance(s, dict):
                                t_name = (s.get("TypeName") or s.get("Role") or "").lower()
                                if "evaluation-agent" in t_name:
                                    latest_eval_idx = idx

            if latest_eval_idx >= 0:
                for idx in range(latest_eval_idx + 1, len(records)):
                    r = records[idx]
                    t = r.get("type", "")
                    src = r.get("source", "")
                    content = str(r.get("content", ""))

                    if t in ("EPHEMERAL_MESSAGE",) or src in ("SYSTEM_SDK",):
                        continue
                    if "File Path: `file:///" in content or "Total Lines:" in content:
                        continue
                    if content.strip().startswith('{"File":') and '"LineNumber":' in content:
                        continue

                    if any(k in content.lower() for k in ("validation_report.json", "overall_verdict", "checks_failed")):
                        has_fail = (
                            re.search(r'\boverall_verdict[\'":\s]+fail\b', content, re.IGNORECASE)
                            or re.search(r'\bverdict[\'":\s]+fail\b', content, re.IGNORECASE)
                            or re.search(r'\boverall_verdict\s+of\s+\*?\*?fail\*?\*?', content, re.IGNORECASE)
                            or re.search(r'checks_failed[\'":\s]+[1-9]\d*', content, re.IGNORECASE)
                        )
                        has_pass = (
                            re.search(r'\boverall_verdict[\'":\s]+pass\b', content, re.IGNORECASE)
                        ) and re.search(r'checks_failed[\'":\s]+0\b', content, re.IGNORECASE)
                        if has_fail and not has_pass:
                            latest_val_after_eval = True

        # Check pending candidates on disk
        has_pending_candidates = False
        cand_dir = os.path.join(ROOT_DIR, ".agents", "learning", "candidates")
        if os.path.isdir(cand_dir):
            for cf in os.listdir(cand_dir):
                if cf.endswith(".json") and not cf.startswith("."):
                    try:
                        with open(os.path.join(cand_dir, cf), "r", encoding="utf-8") as fc:
                            cd = json.load(fc)
                        if str(cd.get("status", "")).upper() in ("STAGED", "EVALUATED", "EVALUATION_PASSED") and str(cd.get("graduation_status", "")).upper() != "GRADUATED":
                            has_pending_candidates = True
                            break
                    except Exception:
                        pass

        # If evaluation completed, all candidates are graduated, and NO new validation failure occurred after eval,
        # then learning is already complete and the system is in REMEDIATION_PHASE. Suppress validation failure trigger.
        if latest_eval_idx >= 0 and not has_pending_candidates and not latest_val_after_eval:
            return None

        try:
            engine = LearningHooks._get_engine(payload)
            if engine:
                from scripts.trajectory_engine import TrajectoryEventType
                events = engine.load_events(event_types=[TrajectoryEventType.VALIDATION_FAILED.value])
                if events:
                    last_ev = events[-1]
                    details = last_ev.get("details", {})
                    failed_list = details.get("failed_checks", [])
                    cf = details.get("checks_failed") or (len(failed_list) if isinstance(failed_list, list) and failed_list else 1)
                    return {
                        "validator_name": details.get("validator_name", "Validation Check"),
                        "summary": str(details.get("failed_checks") or details.get("error") or "Validation checks failed"),
                        "stage_dir": details.get("stage_dir", ""),
                        "checks_failed": cf
                    }
        except Exception as e:
            sys.stderr.write(f"[learning_hooks] Detect validation failure note: {e}\n")

        # Suppress if learning or authoring remediation subagents were already launched in recent turns
        if records:
            for r in reversed(records[-15:]):
                for tc in r.get("tool_calls", []):
                    if (tc.get("name") or "").lower() == "invoke_subagent":
                        subs = tc.get("args", {}).get("Subagents", [])
                        if isinstance(subs, str):
                            try:
                                subs = json.loads(subs)
                            except Exception:
                                subs = []
                        for s in (subs if isinstance(subs, list) else []):
                            if isinstance(s, dict):
                                t_name = (s.get("TypeName") or s.get("Role") or "").lower()
                                if any(k in t_name for k in ("trajectory", "behavior", "curator", "evolver", "writer", "academic-writer")):
                                    return None

        # 2. Inspect on-disk validation_report.json strictly scoped to CURRENT WORK stage directories
        try:
            workspaces = payload.get("workspacePaths", [ROOT_DIR])
            active_stage_dirs = resolve_current_work_stage_dirs(
                workspaces=workspaces,
                payload=payload,
                records=records
            )
            cand_paths = []
            for sdir in active_stage_dirs:
                cp = os.path.join(sdir, "validation_report.json")
                if os.path.isfile(cp):
                    cand_paths.append(cp)
            for cp in cand_paths:
                    if os.path.isfile(cp):
                        try:
                            with open(cp, "r", encoding="utf-8") as vf:
                                v_data = json.load(vf)
                            verdict = str(v_data.get("overall_verdict", "")).strip().upper()
                            ev_sum = v_data.get("evidence_summary", {})
                            checks_failed = ev_sum.get("checks_failed", v_data.get("checks_failed", 0))
                            if verdict == "FAIL" or (isinstance(checks_failed, int) and checks_failed > 0):
                                s_dir = os.path.dirname(cp)
                                val_key = f"{s_dir}:{checks_failed}:{v_data.get('timestamp') or os.path.getmtime(cp)}"
                                if val_key not in LearningHooks._captured_validation_failures:
                                    LearningHooks._captured_validation_failures.add(val_key)
                                    try:
                                        fr_list = v_data.get("results") or [{"validator_name": "ValidationReport", "verdict": "FAIL", "failed_checks": [f"{checks_failed} checks failed"]}]
                                        for fr in fr_list:
                                            if isinstance(fr, dict) and "checks_failed" not in fr:
                                                fr["checks_failed"] = checks_failed
                                        LearningHooks.capture_validation_failure(
                                            stage_dir=s_dir,
                                            validator_results=fr_list
                                        )
                                    except Exception:
                                        pass
                                    return {
                                        "validator_name": v_data.get("validator_name", "ValidationReport"),
                                        "summary": f"Report in '{os.path.basename(s_dir)}' overall_verdict is FAIL ({checks_failed} checks failed)",
                                        "stage_dir": s_dir,
                                        "checks_failed": checks_failed
                                    }
                        except Exception:
                            pass
        except Exception as e_disk:
            sys.stderr.write(f"[learning_hooks] Disk validation failure note: {e_disk}\n")

        # 3. Inspect recent transcript messages for validation failures
        try:
            if records:
                for rec in reversed(records[-30:]):
                    t = rec.get("type", "")
                    src = rec.get("source", "")
                    if t in ("EPHEMERAL_MESSAGE",) or src in ("SYSTEM_SDK",):
                        continue
                    content = str(rec.get("content", ""))
                    if "File Path: `file:///" in content or "Total Lines:" in content:
                        continue
                    if content.strip().startswith('{"File":') and '"LineNumber":' in content:
                        continue
                    if any(k in content.lower() for k in ("validation_report.json", "overall_verdict", "checks_failed")):
                        has_fail = (
                            re.search(r'\boverall_verdict[\'":\s]+fail\b', content, re.IGNORECASE)
                            or re.search(r'\bverdict[\'":\s]+fail\b', content, re.IGNORECASE)
                            or re.search(r'\boverall_verdict\s+of\s+\*?\*?fail\*?\*?', content, re.IGNORECASE)
                            or re.search(r'checks_failed[\'":\s]+[1-9]\d*', content, re.IGNORECASE)
                        )
                        has_pass = (
                            re.search(r'\boverall_verdict[\'":\s]+pass\b', content, re.IGNORECASE)
                        ) and re.search(r'checks_failed[\'":\s]+0\b', content, re.IGNORECASE)
                        if has_pass:
                            break
                        if has_fail:
                            return {
                                "validator_name": "ValidationAgent",
                                "summary": "Validation cascade failed with overall_verdict: FAIL",
                                "stage_dir": ""
                            }
        except Exception as e_tr:
            sys.stderr.write(f"[learning_hooks] Transcript validation failure note: {e_tr}\n")

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
                        "checks_failed": fr.get("checks_failed") or len(fr.get("failed_checks", [])) or 1,
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

            transcript_path = resolve_transcript_path(payload)
            if not tool_name:
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
        # Track 1 software engineering is completely exempt from academic reminders/triggers
        if is_main_agent_developer(payload):
            return {}

        is_sub = (
            payload.get("isSubagent") is True
            or bool(payload.get("parentConversationId"))
            or bool(payload.get("parent_conversation_id"))
        )
        caller = LearningHooks._extract_actor(payload).lower().strip()
        if is_sub or (caller and caller not in ("", "unspecified", "academic-orchestrator", "orchestrator", "main", "default", "digital-saber")):
            # Specialist Subagent PreInvocation Context Rehydration
            sub_role = caller
            if not sub_role or sub_role in ("unspecified", "subagent"):
                try:
                    from contracts.hook_identity_contract import resolve_hook_identity
                    ident = resolve_hook_identity(payload)
                    if ident and ident.agent_name and ident.agent_name != "unknown":
                        sub_role = ident.agent_name.lower().strip()
                except Exception:
                    pass

            sub_blocks = [
                f"🚨 SUBAGENT CONSTITUTIONAL GOVERNANCE ACTIVE ({sub_role.upper()}):\n"
                f"- Role Scope: You are the specialized '{sub_role}' subagent operating in an isolated context.\n"
                "- Directive 6: All operational interaction, reasoning, and tool calls strictly in ASCII English.\n"
                "- Directive 12: You are a specialist worker and strictly forbidden from invoking secondary subagents (invoke_subagent)."
            ]

            if "writer" in sub_role:
                sub_blocks.append(
                    "📝 ACADEMIC WRITER DIRECTIVES:\n"
                    "- Directive 3.1: Chapter 5 (Discussion) must strictly contain ZERO tables (no markdown tables, no Word tables).\n"
                    "- Directive 4 & 5: Persian text in B Nazanin (13-14 pt), Headings in B Titr. Times New Roman for stats.\n"
                    "- Persian Leading Zero: Always keep leading zero in Persian (۰.۰۰۱, ۰.۰۵).\n"
                    "- Zero Robotic AI Clichés: Eliminate 'شایان ذکر است که', 'پرواضح است که', etc.\n"
                    "- True OpenXML Footnotes: Native footnote references; zero plain-text footnote paragraphs."
                )
            elif any(k in sub_role for k in ("stat", "data", "psychometric")):
                sub_blocks.append(
                    "📊 STATISTICAL & DATA INTEGRITY DIRECTIVES:\n"
                    "- Directive 2: Deterministic calculation invariant. Zero mental math or hallucinated numbers.\n"
                    "- Directive 9: Realistic decimal noise. Never output whole integer synthetic means.\n"
                    "- Directive 4: Exactly 2 decimals for M/SD, exactly 3 decimals for p-values (p < .001, never p = .000)."
                )
            elif any(k in sub_role for k in ("validation", "judge", "auditor")):
                sub_blocks.append(
                    "🔍 VALIDATION & AUDIT DIRECTIVES:\n"
                    "- Directive 22: Fail-closed mechanical validation gate. Emit physical validation_report.json.\n"
                    "- Never emit verbal PASS without 100% verified checks on disk."
                )

            try:
                from dynamic_invariant_guard import DynamicInvariantGuard
                invariants = DynamicInvariantGuard.load_invariants()
                tier1, tier2, tier3 = [], [], []
                for r_id, r_spec in invariants.items():
                    if not r_spec.get("enabled", True):
                        continue
                    target_agents = [a.lower().strip() for a in r_spec.get("target_agents", [])]
                    stmt = r_spec.get("statement", "")
                    remedy = r_spec.get("remedy", "")
                    if not stmt:
                        continue
                    line = f"- [{r_id}]: {stmt[:160]}" + (f" (Remedy: {remedy[:120]})" if remedy else "")

                    if sub_role in target_agents:
                        tier1.append(line)
                    elif any(t in sub_role for t in target_agents if t != "*"):
                        tier2.append(line)
                    elif "*" in target_agents:
                        tier3.append(line)

                role_pitfalls = (tier1 + tier2 + tier3)[:8]
                if role_pitfalls:
                    sub_blocks.append("⚠️ ACTIVE ROLE INVARIANTS & KNOWN ANTI-PATTERNS:\n" + "\n".join(role_pitfalls))
            except Exception:
                pass

            return {"injectSteps": [{"ephemeralMessage": "\n\n".join(sub_blocks)}]}

        # Resolve caller identity authoritatively
        if not caller or caller in ("unspecified", "default", "main"):
            try:
                from contracts.hook_identity_contract import resolve_hook_identity
                ident = resolve_hook_identity(payload)
                if ident and ident.is_main_developer:
                    return {}
                if ident and ident.agent_name and ident.agent_name != "unknown":
                    caller = ident.agent_name.lower().strip()
            except Exception:
                pass

        # Resolve transcript path for context analysis
        transcript_path = resolve_transcript_path(payload)

        is_orchestrator = caller in ("academic-orchestrator", "orchestrator", "unspecified", "unknown", "")
        if not is_orchestrator:
            # Check if user message explicitly requests academic orchestration or thesis pipelines
            u_msg = str(payload.get("userMessage") or payload.get("prompt") or payload.get("message") or "")
            if not u_msg and transcript_path and os.path.isfile(transcript_path):
                records = load_transcript(transcript_path)
                for r in reversed(records):
                    if r.get("type") == "USER_INPUT" and r.get("content"):
                        u_msg = r.get("content", "").strip()
                        break
            u_lower = u_msg.lower()
            academic_orch_triggers = (
                "academic-orchestrator", "orchestrate", "thesis", "dissertation",
                "chapter 4", "chapter 5", "فصل پنجم", "فصل چهارم", "structural equation",
                "scale validation", "cfa", "sem", "repeated measures", "rm-anova"
            )
            if any(k in u_lower for k in academic_orch_triggers):
                is_orchestrator = True

        # Non-orchestrator root sessions (Track 1 Developer Agent) are strictly exempt from academic injections
        if not is_orchestrator:
            return {}

        critique_info = LearningHooks.capture_user_correction(payload)

        reminder = (
            "🚨 CONSTITUTIONAL ENFORCEMENT ACTIVE (Directives 0, 3, 6, 11, 12.1 & 20):\n"
            "- Directive 0 (Binary Honesty Protocol): Compliance queries MUST begin with 'Yes' or 'No'. Multi-agent claims strictly require invoke_subagent calls.\n"
            "- Directive 3 (Artifact-Gated Stage Execution & Two-Tier Drafting): Monolithic drafting prohibited. Tier 1 micro-stages enforce the analytical dyad (.json + .md; .docx optional); Tier 2 consolidation enforces the monograph (.docx + .md); learning tasks require verified .json/.md artifacts.\n"
            "- Directive 6 (English Primary Interaction): All conversational interaction, planning, coordination, and reporting strictly in English. Persian is reserved strictly for academic deliverable content.\n"
            "- Directive 11 (Interactive Stage-Gate Protocol): Emit Stage Completion Report (what was done, what is next) and HALT for user confirmation before advancing.\n"
            "- Directive 12.1 (Sole Orchestrator Mandate): Antigravity is the sole agent conductor via invoke_subagent. Python execution loops/emulators strictly prohibited.\n"
            "- Directive 20 (Orchestrator Invariant): academic-orchestrator possesses invoke_subagent and strictly lacks code/mutation execution tools (pure conductor)."
        )

        ephemeral_blocks = [reminder]

        # Inject orchestrator-targeted invariants
        try:
            from dynamic_invariant_guard import DynamicInvariantGuard
            invariants = DynamicInvariantGuard.load_invariants()
            orch_pitfalls = []
            for r_id, r_spec in invariants.items():
                if not r_spec.get("enabled", True):
                    continue
                target_agents = [a.lower().strip() for a in r_spec.get("target_agents", [])]
                if "academic-orchestrator" in target_agents or "orchestrator" in target_agents:
                    stmt = r_spec.get("statement", "")
                    remedy = r_spec.get("remedy", "")
                    if stmt:
                        orch_pitfalls.append(f"- [{r_id}]: {stmt[:160]}" + (f" (Remedy: {remedy[:120]})" if remedy else ""))
            if orch_pitfalls:
                ephemeral_blocks.append("⚠️ ACTIVE ORCHESTRATOR INVARIANTS:\n" + "\n".join(orch_pitfalls[:6]))
        except Exception:
            pass

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
                "🧠 CONTINUOUS LEARNING TRIGGER ACTIVE (VALIDATION_FAILED):\n"
                f"- Recent Validation Failure: \"{val_summary}\"\n"
                "- Operational Mandate (Directive 21, AP-2026-PATCHING-WITHOUT-LEARNING & LEARNING_MULTI_AGENT_SPEC.md):\n"
                "  A deliverable has failed validation audit. You MUST trigger the diagnostic learning pipeline via native invoke_subagent:\n"
                f"  1. invoke_subagent(TypeName=\"trajectory-analyzer\", Prompt=\"Reconstruct observable actions, tool calls, and error trajectory for validation failure: {val_summary}\")\n"
                "  2. invoke_subagent(TypeName=\"behavior-analyst\", Prompt=\"Perform causal root-cause analysis on the failure trajectory to determine failure mechanism\")\n"
                "  3. invoke_subagent(TypeName=\"knowledge-curator\", Prompt=\"Catalog the diagnosed anti-pattern into persistent learning store\")\n"
                "  4. invoke_subagent(TypeName=\"skill-evolver\", Workspace=\"inherit\", Prompt=\"Synthesize candidate modification to evolve the skill/script and define companion mechanical rules\")\n"
                "  5. invoke_subagent(TypeName=\"evaluation-agent\", Workspace=\"inherit\", Prompt=\"Evaluate candidate and compile via academic_graduation_compiler.py\")\n"
                "- Prohibited Anti-Pattern: Do NOT invoke delivery workers (academic-writer, statistics-agent) before completing the learning cascade."
            )
            ephemeral_blocks.append(val_block)

        # Model B: Deterministic Preflight Capability Routing for Academic Orchestrator
        # Executes academic_task_router.py offline/in-hook ("The Hands") to compile academic-state/routing_plan.json
        # and inject the deterministic capability plan into the orchestrator context.
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
                    from contracts.canonical_paths import resolve_active_project_dir
                    target_project_dir = resolve_active_project_dir(prompt=clean_prompt, suite_root=ROOT_DIR, payload=payload)
                    from scripts.academic_task_router import route_and_persist_plan
                    routing_plan = route_and_persist_plan(
                        prompt=clean_prompt,
                        base_dir=target_project_dir
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


handle_pre_invocation = LearningHooks.handle_pre_invocation


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
