#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/agents/academic-orchestrator/guard.py

Dedicated Lifecycle Hook Guard for Academic Main Agent (academic-orchestrator).
Enforces:
1. Directive 20 (Orchestrator Non-Execution Invariant):
   academic-orchestrator is strictly managerial and forbidden from executing code (run_command)
   or directly mutating project files (write_to_file, replace_file_content, edit_file).
   Execution MUST be delegated to specialist subagents via invoke_subagent.
2. Directive 11 (Interactive Stage-Gate Protocol):
   Requires interactive confirmation pause between multi-stage workflows.
3. Directive 0 (Binary Honesty Protocol):
   First word must be unambiguous "Yes" or "No" on compliance questions.
4. Directive 21 & 21.1 (Autonomous Learning & Remediation Cascade):
   Prevents premature remediation prior to learning evaluation and invariant graduation.
5. Directive 3 & 3.1 (Triad Deliverables & Chapter 5 Prose-Only Standards).
"""

import sys
import os
import re
import json
import argparse
from typing import Dict, Any, List

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HOOKS_DIR, "..", "..", ".."))
for p in (ROOT_DIR, os.path.join(ROOT_DIR, ".agents"), os.path.join(ROOT_DIR, ".agents", "hooks"), os.path.join(ROOT_DIR, ".agents", "contracts")):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from contracts.delegation_envelope_parser import validate_delegation_prompt
except ImportError:
    try:
        from delegation_envelope_parser import validate_delegation_prompt
    except ImportError:
        def validate_delegation_prompt(p, expected_worker=None):
            return True, "Validator unavailable", None

try:
    from contracts.canonical_pipelines import (
        verify_pipeline_stage_prerequisites,
        verify_capability_routing,
        find_files_matching,
        verify_chapter4_gate3_clearance
    )
except ImportError:
    try:
        from canonical_pipelines import (
            verify_pipeline_stage_prerequisites,
            verify_capability_routing,
            find_files_matching,
            verify_chapter4_gate3_clearance
        )
    except ImportError:
        def verify_pipeline_stage_prerequisites(s, w): return True, "Pipeline validator unavailable"
        def verify_capability_routing(w, p, e=None, ws=None): return True, "Capability validator unavailable"
        def find_files_matching(w, p): return []
        def verify_chapter4_gate3_clearance(w): return True, "Gate 3 validator unavailable", []

try:
    from contracts.critique_detection_contract import is_meaningful_user_critique, extract_clean_user_message
except ImportError:
    try:
        from critique_detection_contract import is_meaningful_user_critique, extract_clean_user_message
    except ImportError:
        def is_meaningful_user_critique(user_text, **kw): return False, None
        def extract_clean_user_message(raw_text): return re.sub(r"<[^>]+>", "", str(raw_text)).strip()

try:
    from contracts.orchestrator_lifecycle_engine import (
        is_user_critique_active,
        is_validation_failure_active,
        get_defect_and_learning_lifecycle_state,
        audit_triad_artifacts_completion,
        audit_chapter5_docx_tables,
        audit_native_docx_footnotes
    )
except ImportError:
    from orchestrator_lifecycle_engine import (
        is_user_critique_active,
        is_validation_failure_active,
        get_defect_and_learning_lifecycle_state,
        audit_triad_artifacts_completion,
        audit_chapter5_docx_tables,
        audit_native_docx_footnotes
    )

FORBIDDEN_ORCHESTRATOR_TOOLS = {
    "run_command",
    "write_to_file",
    "replace_file_content",
    "edit_file",
    "patch",
    "multi_file_edit",
    "batch_replace",
    "apply_diff"
}

EXECUTION_SUBAGENTS = {
    "statistics-agent",
    "data-agent",
    "academic-writer",
    "validation-agent",
    "psychometric-expert",
    "results-auditor"
}


def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get("toolCall") or payload.get("tool_call") or {}
    tool_name = (tool_call.get("name") or payload.get("tool_name") or "").strip().lower()
    args = tool_call.get("args") or payload.get("args") or {}

    # Directive 20 / Directive 12.1: Non-Execution Invariant
    if tool_name in FORBIDDEN_ORCHESTRATOR_TOOLS:
        return {
            "decision": "deny",
            "reason": (
                f"CONSTITUTIONAL VIOLATION (Directive 20 / Directive 12.1 — Orchestrator Non-Execution Invariant): "
                f"Academic-Orchestrator is the Academic Main Agent (Conductor) and is strictly forbidden from "
                f"executing shell commands or mutating project files via '{tool_name}'. "
                f"All computational execution and file generation MUST be delegated to specialist subagents "
                f"(e.g., statistics-agent, academic-writer, data-agent) via invoke_subagent."
            )
        }

    # Directive 19 / Directive 12: Contractual Delegation Envelope & Capability Routing
    if tool_name == "invoke_subagent":
        subagents = args.get("Subagents", [])
        if isinstance(subagents, str):
            try:
                subagents = json.loads(subagents, strict=False)
            except Exception:
                subagents = []
        if isinstance(subagents, list):
            for sub in subagents:
                if not isinstance(sub, dict):
                    continue
                target_type = sub.get("TypeName", "")
                prompt = sub.get("Prompt", "")

                # 1. Directive 21.1: Premature Remediation Guard under Active Critique or Validation Failure
                if target_type in EXECUTION_SUBAGENTS:
                    transcript_path = payload.get("transcriptPath")
                    if not transcript_path:
                        try:
                            from contracts.hook_identity_contract import resolve_transcript_path
                            transcript_path = resolve_transcript_path(payload)
                        except Exception:
                            transcript_path = None
                    if transcript_path:
                        t_target = transcript_path
                        if os.path.basename(transcript_path) == "transcript.jsonl":
                            full_cand = os.path.join(os.path.dirname(transcript_path), "transcript_full.jsonl")
                            if os.path.isfile(full_cand) and os.path.getsize(full_cand) > 0:
                                t_target = full_cand
                        if os.path.exists(t_target):
                            try:
                                with open(t_target, "r", encoding="utf-8") as tf:
                                    t_records = [json.loads(tl.strip()) for tl in tf if tl.strip()]
                                workspaces = payload.get("workspacePaths", [ROOT_DIR])
                                state, pending_cands, defect_desc, defect_label = get_defect_and_learning_lifecycle_state(
                                    t_records, workspaces, ROOT_DIR
                                )
                                defect_type = "User critique" if defect_label == "Critique" else "Validation failure"
                                if state == "LEARNING_REQUIRED":
                                    msg = (
                                        f"CONSTITUTIONAL VIOLATION (Directive 21.1 / AP-2026-PATCHING-WITHOUT-LEARNING — Premature Remediation Without Tool Evolution): "
                                        f"{defect_type} is active ('{defect_desc[:80]}...'). You are strictly prohibited from invoking delivery worker "
                                        f"'{target_type}' before completing the continuous learning cascade via 'trajectory-analyzer' -> 'behavior-analyst' -> "
                                        f"'knowledge-curator' -> 'skill-evolver' -> 'evaluation-agent' to evolve canonical tools on disk."
                                    )
                                    return {"decision": "deny", "reason": msg}
                                elif state == "PENDING_GRADUATION":
                                    msg = (
                                        f"CONSTITUTIONAL VIOLATION (Directive 21.1 — Premature Remediation Without Invariant Graduation): "
                                        f"Improvement candidate(s) {pending_cands} are evaluated but have not been graduated into canonical tools or mechanical rules. "
                                        f"The autonomous learning pipeline must compile candidates via 'academic_graduation_compiler.py compile-all' "
                                        f"before invoking delivery worker '{target_type}'."
                                    )
                                    return {"decision": "deny", "reason": msg}
                            except Exception:
                                pass

                # 2. Directive 19 / Directive 12: Contractual Delegation Envelope Validation
                is_valid, reason, env = (
                    validate_delegation_prompt(prompt, expected_worker=target_type)
                    if target_type in EXECUTION_SUBAGENTS
                    else (True, "", None)
                )

                if not is_valid:
                    return {
                        "decision": "deny",
                        "reason": (
                            f"CONSTITUTIONAL VIOLATION (Directive 19 / Directive 12 — Contractual Delegation Invariant / Contractual Delegation Envelope Required):\n"
                            f"{reason}\n"
                            f"Academic-Orchestrator must provide a structured Contractual Delegation Envelope (CDE) specifying "
                            f"task_id, worker_agent, inputs, and required_artifacts."
                        )
                    }

                # 3. Capability Routing Verification & Gate Clearance
                workspaces = payload.get("workspacePaths")
                ok_cap, cap_reason = verify_capability_routing(target_type, prompt, env, workspaces)
                if not ok_cap:
                    return {"decision": "deny", "reason": cap_reason}

                # 4. Directive 19 / Directive 2: Statistical Immobility Invariant for Delegation to Academic-Writer
                if target_type == "academic-writer":
                    req_artifacts = (env.get("required_artifacts") if env else None) or []
                    if isinstance(req_artifacts, list):
                        forbidden_json_targets = []
                        for art in req_artifacts:
                            art_name = art.get("path", "") if isinstance(art, dict) else str(art)
                            if art_name.strip().lower().endswith(".json"):
                                forbidden_json_targets.append(art_name)
                        if forbidden_json_targets:
                            msg = (
                                f"CONSTITUTIONAL VIOLATION (Directive 19 / Directive 2 — Statistical Immobility Invariant):\n"
                                f"Delegation envelope for 'academic-writer' lists statistical/analytical JSON artifact(s) in 'required_artifacts': {forbidden_json_targets}.\n"
                                f"Academic-Writer is strictly 'The Voice' and produces ONLY scholarly narratives (.docx, .md). "
                                f"All numerical and analytical JSON files are immutable outputs of Phase 4A–4C and belong strictly under 'inputs' as read-only anchors."
                            )
                            return {"decision": "deny", "reason": msg}

                # 5. Directive 3: Pipeline Stage Prerequisite Invariant (Zero Skipping)
                stage_label = ""
                if env:
                    stage_label = env.get("stage") or env.get("task_id") or ""
                if not stage_label:
                    stage_label = prompt

                workspaces = payload.get("workspacePaths", [ROOT_DIR])
                ok_prereq, prereq_reason = verify_pipeline_stage_prerequisites(stage_label, workspaces)
                if not ok_prereq:
                    return {"decision": "deny", "reason": prereq_reason}

    return {"decision": "allow"}


def handle_stop(payload: Dict[str, Any]) -> Dict[str, Any]:
    transcript_path = payload.get("transcriptPath")
    if not transcript_path:
        try:
            from contracts.hook_identity_contract import resolve_transcript_path
            transcript_path = resolve_transcript_path(payload)
        except Exception:
            transcript_path = None

    if transcript_path and os.path.exists(transcript_path):
        try:
            t_target = transcript_path
            if os.path.basename(transcript_path) == "transcript.jsonl":
                full_cand = os.path.join(os.path.dirname(transcript_path), "transcript_full.jsonl")
                if os.path.isfile(full_cand) and os.path.getsize(full_cand) > 0:
                    t_target = full_cand
            with open(t_target, "r", encoding="utf-8") as tf:
                lines = [l.strip() for l in tf if l.strip()]
            if lines:
                last_record = json.loads(lines[-1])

                # Directive 21 & Directive 21.1: Continuous Learning Cascade Gate
                all_records = [json.loads(l) for l in lines]
                workspaces = payload.get("workspacePaths", [ROOT_DIR])
                state, pending_cands, defect_desc, defect_label = get_defect_and_learning_lifecycle_state(
                    all_records, workspaces, ROOT_DIR
                )

                if state == "LEARNING_REQUIRED":
                    msg = (
                        f"CONSTITUTIONAL VIOLATION (Directive 21 & Directive 21.1 — Uninvoked Learning Pipeline on {defect_label}):\n"
                        f"A defect was detected ('{defect_desc[:80]}...'), but the continuous learning cascade "
                        f"was NOT executed in this turn!\n"
                        f"Under Directive 21, Directive 21.1, and AP-2026-PATCHING-WITHOUT-LEARNING, you are strictly prohibited from bypassing learning, attempting "
                        f"ad-hoc direct fixes, or delegating remediation without first running the full 5-stage cascade:\n"
                        f"1. trajectory-analyzer, 2. behavior-analyst, 3. knowledge-curator, 4. skill-evolver, 5. evaluation-agent.\n"
                        f"Please invoke 'trajectory-analyzer' now."
                    )
                    return {"decision": "continue", "reason": msg}
                elif state == "PENDING_GRADUATION":
                    msg = (
                        f"CONSTITUTIONAL VIOLATION (Directive 21 — Incomplete Invariant Graduation):\n"
                        f"Improvement candidate(s) {pending_cands} are evaluated but have not been graduated into canonical tools or mechanical rules. "
                        f"The autonomous learning pipeline must compile candidates via 'academic_graduation_compiler.py compile-all' "
                        f"before concluding this turn."
                    )
                    return {"decision": "continue", "reason": msg}

                # Directive 0: Binary Honesty Protocol on Compliance Questions
                user_question = ""
                for rec_line in reversed(lines[:-1]):
                    rec = json.loads(rec_line)
                    if rec.get("type") == "USER_INPUT":
                        user_question = rec.get("content", "")
                        break

                is_compliance_q = any(
                    k in user_question.lower()
                    for k in ("did you check", "did you follow", "did you use", "have you checked", "is it compliant")
                )
                if is_compliance_q:
                    model_text = (last_record.get("content") or "").strip()
                    first_word = model_text.split()[0].rstrip(",.:;!?") if model_text.split() else ""
                    if first_word.lower() not in ("yes", "no"):
                        msg = (
                            "CONSTITUTIONAL VIOLATION (Directive 0 — Binary Honesty Protocol): "
                            "Compliance inquiries must begin with an unambiguous 'Yes' or 'No' as the very first word. "
                            "State the unvarnished factual answer before proposing explanations or remedies."
                        )
                        return {"decision": "continue", "reason": msg}

                # Directive 13: Anti-Sycophancy Invariant
                raw_model_text = (last_record.get("content") or "").strip()
                first_line = raw_model_text.split("\n")[0].strip() if raw_model_text else ""
                flattery_patterns = [
                    r"^(?:that(?:'s| is) a\s+)?(?:great|excellent|fantastic|wonderful|brilliant|insightful)\s+(?:question|point|observation|inquiry)",
                    r"^you(?:'re| are)\s+(?:absolutely\s+|completely\s+|entirely\s+)?right\b",
                    r"^(?:great|excellent|wonderful)\s+choice\b"
                ]
                for fp in flattery_patterns:
                    if re.search(fp, first_line, re.IGNORECASE):
                        msg = (
                            "CONSTITUTIONAL VIOLATION (Directive 13 — Anti-Sycophancy Invariant): "
                            "Sycophantic conversational openings ('Great question!', 'You are absolutely right!') are strictly forbidden. "
                            "Academic communication must remain strictly objective, neutral, and fact-based."
                        )
                        return {"decision": "continue", "reason": msg}

                # Directive 6: Strict English Orchestration Dialogue
                clean_text = re.sub(r'```[\s\S]*?```', '', raw_model_text)
                clean_text = re.sub(r'`[^`]*`', '', clean_text)
                clean_text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', clean_text)
                persian_chars = len(re.findall(r'[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]', clean_text))
                total_non_ws = len(re.sub(r'\s+', '', clean_text))
                if total_non_ws >= 40 and (persian_chars / total_non_ws) > 0.15:
                    msg = (
                        "CONSTITUTIONAL VIOLATION (Directive 6 — Strict English Orchestration Dialogue):\n"
                        "Meta-orchestration and user interaction must be conducted strictly in English.\n"
                        "Persian is strictly reserved for academic deliverables (.docx, .md, .json) and client messages.\n"
                        "Please translate your conversational response to English before concluding."
                    )
                    return {"decision": "continue", "reason": msg}

                # Directive 15: Temporal Reality Anchor (2026 / 1405 SH)
                anachronism_match = re.search(
                    r'\b(?:currently\s+in\s+202[345]|this\s+year\s+\(202[345]\)|in\s+the\s+present\s+year\s+202[345]|'
                    r'the\s+current\s+year\s+is\s+202[345]|future\s+research\s+in\s+202[45]|'
                    r'as\s+of\s+202[345]\s*,\s*the\s+current)\b',
                    raw_model_text,
                    re.IGNORECASE
                )
                if anachronism_match:
                    msg = (
                        f"CONSTITUTIONAL VIOLATION (Directive 15 — Temporal Reality Anchor):\n"
                        f"Detected temporal hallucination: '{anachronism_match.group(0)}'.\n"
                        f"The operative calendar year is 2026 (1405 SH). Recent empirical literature window is 2021–2026.\n"
                        f"Never refer to 2024 or 2025 as the current or future year."
                    )
                    return {"decision": "continue", "reason": msg}

                # Directive 11: Interactive Stage-Gate Protocol
                records = [json.loads(l) for l in lines]
                had_delegation = any(
                    any((tc.get("name") or "").lower() == "invoke_subagent" for tc in r.get("tool_calls", []))
                    for r in records
                )
                if had_delegation:
                    model_text = (last_record.get("content") or "").lower()
                    has_confirmation = any(k in model_text for k in ("confirm", "approve", "proceed", "shall we", "تایید", "ادامه", "pause", "wait", "halt"))
                    has_stage_report = any(k in model_text for k in ("what was done", "completed", "executed", "stage", "انجام شد", "مرحله"))
                    has_next_step = any(k in model_text for k in ("what will be done next", "next step", "next stage", "گام بعدی", "مرحله بعد", "next:"))
                    if not (has_confirmation or (has_stage_report and has_next_step)):
                        msg = (
                            "CONSTITUTIONAL VIOLATION (Directive 11 — Interactive Stage-Gate Protocol): "
                            "Following subagent execution, the Academic Orchestrator must report what was done, "
                            "what will be done next, and halt to request user confirmation before proceeding."
                        )
                        return {"decision": "continue", "reason": msg}

                    # Directive 3: Triad Artifact Completion Audit
                    workspaces = payload.get("workspacePaths", [ROOT_DIR])
                    ok_triad, triad_msg = audit_triad_artifacts_completion(records, workspaces)
                    if not ok_triad:
                        return {"decision": "continue", "reason": triad_msg}

                    # Directive 3.1: Chapter 5 Table Ban Dual Gate (Scoped to 03_deliverables/)
                    if any(k in model_text for k in ("chapter 5", "chapter_5", "ch5", "فصل پنجم", "فصل ۵", "discussion")):
                        ok_ch5, ch5_msg = audit_chapter5_docx_tables(workspaces)
                        if not ok_ch5:
                            return {"decision": "continue", "reason": ch5_msg}

                    # Directive 5: Native OpenXML Footnotes Verification (Scoped to 03_deliverables/)
                    ok_fn, fn_msg = audit_native_docx_footnotes(workspaces)
                    if not ok_fn:
                        return {"decision": "continue", "reason": fn_msg}
        except Exception:
            pass

    return {"decision": "allow"}


def main():
    parser = argparse.ArgumentParser(description="Academic Orchestrator Lifecycle Guard")
    parser.add_argument("--event", type=str, default="PreToolUse", choices=["PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"])
    args, _ = parser.parse_known_args()

    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[orchestrator_guard] Error reading stdin: {e}\n")

    event = args.event
    if event == "PreToolUse":
        res = handle_pre_tool_use(payload)
    elif event == "Stop":
        res = handle_stop(payload)
    elif event == "PostInvocation":
        res = {"injectSteps": [], "terminationBehavior": ""}
    else:
        res = {"decision": "allow"}

    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
