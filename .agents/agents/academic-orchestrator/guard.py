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
"""

import sys
import os
import re
import json
import argparse
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Tuple

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
        find_files_matching
    )
except ImportError:
    try:
        from canonical_pipelines import (
            verify_pipeline_stage_prerequisites,
            verify_capability_routing,
            find_files_matching
        )
    except ImportError:
        def verify_pipeline_stage_prerequisites(s, w):
            return True, "Pipeline validator unavailable"
        def verify_capability_routing(w, p, e=None):
            return True, "Capability validator unavailable"
        def find_files_matching(w, p):
            return []

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

CRITIQUE_PATTERNS = [
    r"\b(?:problem|error|bug|defect|issue|flaw|failure|discrepancy|mismatch)s?\b",
    r"\b(?:fix|wrong|incorrect|flawed|missing|redo|re-run|re-execute|reject|rejected)\b",
    r"\b(?:didn'?t|did\s+not)\s+(?:trigger|start|run|work|include|execute)\b",
    r"\b(?:there|it)\s+(?:isn'?t|is\s+not|wasn'?t|was\s+not|aren'?t|are\s+not)\b",
    r"\b(?:isn'?t|is\s+not|wasn'?t|was\s+not)\s+(?:the|what|any|working|correct)\b",
    r"\bnot\s+(?:working|correct|right|accurate)\b",
    r"اشتباه|اشتباهات|غلط|غلط‌ها|اصلاح|تصحیح|مجدد|تکرار|رد شد|نادرست|خطا|خطاها|مشکل|مشکلات|ایراد|ایرادات|نواقص|نقص|جا افتاده|حذف شده|وجود ندارد|نیست"
]


def is_user_critique_active(records: List[Dict[str, Any]]) -> Tuple[bool, str, List[Dict[str, Any]]]:
    last_user_idx = -1
    user_content = ""
    for idx, r in enumerate(records):
        if r.get("type") == "USER_INPUT":
            last_user_idx = idx
            user_content = str(r.get("content", ""))
    active_records = records[last_user_idx + 1:] if last_user_idx >= 0 else records
    clean_user = re.sub(r"<[^>]+>", "", user_content).strip()
    is_critique = any(re.search(pat, clean_user, re.IGNORECASE) for pat in CRITIQUE_PATTERNS)
    return is_critique, clean_user, active_records


def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get("toolCall", {})
    tool_name = (tool_call.get("name") or "").strip().lower()
    args = tool_call.get("args", {})

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

                is_valid, reason, env = (
                    validate_delegation_prompt(prompt, expected_worker=target_type)
                    if target_type in EXECUTION_SUBAGENTS
                    else (True, "", None)
                )

                # Capability Routing Verification (Directive 19 / Directive 12)
                ok_cap, cap_reason = verify_capability_routing(target_type, prompt, env)
                if not ok_cap:
                    return {
                        "decision": "deny",
                        "reason": cap_reason,
                        "message": cap_reason
                    }

                if target_type in EXECUTION_SUBAGENTS:
                    # Directive 21.1: Premature Remediation Guard under Active Critique
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
                                is_crit, crit_txt, active_recs = is_user_critique_active(t_records)
                                if is_crit:
                                    eval_completed = False
                                    for ar in active_recs:
                                        for atc in ar.get("tool_calls", []):
                                            if atc.get("name") == "invoke_subagent":
                                                asubs = atc.get("args", {}).get("Subagents", [])
                                                if isinstance(asubs, str):
                                                    try: asubs = json.loads(asubs, strict=False)
                                                    except: asubs = []
                                                for asa in (asubs if isinstance(asubs, list) else []):
                                                    if isinstance(asa, dict) and "evaluation-agent" in (asa.get("TypeName") or "").lower():
                                                        eval_completed = True
                                    if not eval_completed:
                                        msg = (
                                            f"CONSTITUTIONAL VIOLATION (Directive 21.1 — Premature Remediation Without Tool Evolution): "
                                            f"User critique is active ('{crit_txt[:80]}...'). You are strictly prohibited from invoking delivery worker "
                                            f"'{target_type}' before completing the continuous learning cascade via 'trajectory-analyzer' -> 'behavior-analyst' -> "
                                            f"'knowledge-curator' -> 'skill-evolver' -> 'evaluation-agent' to evolve canonical tools on disk."
                                        )
                                        return {
                                            "decision": "deny",
                                            "reason": msg,
                                            "message": msg
                                        }

                                    # Candidate graduation verification: ensure evaluated candidates are graduated on disk
                                    cand_dir = os.path.join(ROOT_DIR, ".agents", "learning", "candidates")
                                    pending_cands = []
                                    if os.path.isdir(cand_dir):
                                        for cf in os.listdir(cand_dir):
                                            if cf.endswith(".json") and not cf.startswith("."):
                                                try:
                                                    with open(os.path.join(cand_dir, cf), "r", encoding="utf-8") as f_c:
                                                        cd = json.load(f_c)
                                                    c_st = str(cd.get("status", "")).upper()
                                                    g_st = str(cd.get("graduation_status", "")).upper()
                                                    if c_st in ("STAGED", "EVALUATED", "EVALUATION_PASSED") and g_st != "GRADUATED":
                                                        pending_cands.append(cd.get("candidate_id") or cf)
                                                except Exception:
                                                    pass
                                    if pending_cands:
                                        msg = (
                                            f"CONSTITUTIONAL VIOLATION (Directive 21.1 — Premature Remediation Without Invariant Graduation): "
                                            f"Improvement candidate(s) {pending_cands} are evaluated but have not been graduated into canonical tools or mechanical rules. "
                                            f"The autonomous learning pipeline must compile candidates via 'academic_graduation_compiler.py compile-all' "
                                            f"before invoking delivery worker '{target_type}'."
                                        )
                                        return {
                                            "decision": "deny",
                                            "reason": msg,
                                            "message": msg
                                        }
                            except Exception:
                                pass

                    if not is_valid:
                        msg = (
                            f"CONSTITUTIONAL VIOLATION (Directive 19 / Directive 12 — Contractual Delegation Invariant): "
                            f"Delegation to execution worker '{target_type}' was rejected: {reason}\n"
                            f"You must embed a structured Contractual Delegation Envelope (CDE) in the prompt "
                            f"specifying 'task_id', 'worker_agent', 'inputs', 'required_artifacts', and 'objective'/'target_script'."
                        )
                        return {
                            "decision": "deny",
                            "reason": msg,
                            "message": msg
                        }

                    # Directive 3: Pipeline Stage Prerequisite Invariant (Zero Skipping)
                    stage_label = ""
                    if env:
                        stage_label = env.get("stage") or env.get("task_id") or ""
                    if not stage_label:
                        stage_label = prompt

                    workspaces = payload.get("workspacePaths", [ROOT_DIR])
                    ok_prereq, prereq_reason = verify_pipeline_stage_prerequisites(stage_label, workspaces)
                    if not ok_prereq:
                        return {
                            "decision": "deny",
                            "reason": prereq_reason,
                            "message": prereq_reason
                        }

    return {"decision": "allow"}


def handle_stop(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Check if there is a transcript available to verify Directive 0 or stage completion
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

                # Directive 21 & Directive 21.1: Continuous Learning Cascade Gate on Critique
                all_records = [json.loads(l) for l in lines]
                is_crit, crit_txt, active_recs = is_user_critique_active(all_records)
                if is_crit:
                    invoked_in_turn = []
                    for ar in active_recs:
                        for atc in ar.get("tool_calls", []):
                            if (atc.get("name") or "").lower() == "invoke_subagent":
                                asubs = atc.get("args", {}).get("Subagents", [])
                                if isinstance(asubs, str):
                                    try: asubs = json.loads(asubs, strict=False)
                                    except: asubs = []
                                for asa in (asubs if isinstance(asubs, list) else []):
                                    if isinstance(asa, dict):
                                        t_name = (asa.get("TypeName") or asa.get("Role") or "").lower().strip()
                                        if t_name:
                                            invoked_in_turn.append(t_name)
                    has_diagnostic = any(any(k in sa for k in ("trajectory-analyzer", "behavior-analyst", "knowledge-curator")) for sa in invoked_in_turn)
                    has_evolution = any(any(ev in sa for ev in ("skill-evolver", "evaluation-agent")) for sa in invoked_in_turn)
                    if not has_diagnostic or not has_evolution:
                        msg = (
                            f"CONSTITUTIONAL VIOLATION (Directive 21 & Directive 21.1 — Uninvoked Learning Pipeline on Critique):\n"
                            f"The user reported a defect or critique ('{crit_txt[:80]}...'), but the continuous learning cascade "
                            f"was NOT executed in this turn!\n"
                            f"Under Directive 21 and Directive 21.1, you are strictly prohibited from bypassing learning, attempting "
                            f"ad-hoc direct fixes, or delegating remediation without first running the full 5-stage cascade:\n"
                            f"1. trajectory-analyzer, 2. behavior-analyst, 3. knowledge-curator, 4. skill-evolver, 5. evaluation-agent.\n"
                            f"Please invoke 'trajectory-analyzer' now."
                        )
                        return {
                            "decision": "continue",
                            "reason": msg,
                            "message": msg
                        }

                # If this was a planner response answering a compliance question, verify Directive 0
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
                        return {
                            "decision": "continue",
                            "reason": msg,
                            "message": msg
                        }

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
                        return {
                            "decision": "continue",
                            "reason": msg,
                            "message": msg
                        }

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
                    return {
                        "decision": "continue",
                        "reason": msg,
                        "message": msg
                    }

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
                    return {
                        "decision": "continue",
                        "reason": msg,
                        "message": msg
                    }

                # Directive 11: Interactive Stage-Gate Protocol
                # If subagents were invoked in this turn, verify that orchestrator halted and requested user confirmation
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
                        return {
                            "decision": "continue",
                            "reason": msg,
                            "message": msg
                        }

                    # Directive 3: Triad Artifact Completion Audit on Stage Conclusion
                    workspaces = payload.get("workspacePaths", [ROOT_DIR])
                    for r in records:
                        for tc in r.get("tool_calls", []):
                            if (tc.get("name") or "").lower() == "invoke_subagent":
                                sub_list = tc.get("args", {}).get("Subagents", [])
                                if isinstance(sub_list, str):
                                    try: sub_list = json.loads(sub_list, strict=False)
                                    except: sub_list = []
                                if isinstance(sub_list, list):
                                    for sub in sub_list:
                                        if not isinstance(sub, dict):
                                            continue
                                        p_text = sub.get("Prompt", "")
                                        is_cde, _, env = validate_delegation_prompt(p_text, expected_worker=sub.get("TypeName"))
                                        if env and env.get("required_artifacts"):
                                            req_arts = env.get("required_artifacts", [])
                                            missing_arts = []
                                            empty_arts = []
                                            for art in req_arts:
                                                art_name = os.path.basename(art)
                                                found = find_files_matching(workspaces, re.escape(art_name))
                                                if not found:
                                                    missing_arts.append(art)
                                                elif all(os.path.getsize(f) == 0 for f in found):
                                                    empty_arts.append(art)
                                            if missing_arts or empty_arts:
                                                msg = (
                                                    f"CONSTITUTIONAL VIOLATION (Directive 3 — Triad Artifact Invariant):\n"
                                                    f"Stage declared completion, but required deliverables are missing or empty on disk.\n"
                                                    f"Missing artifacts: {missing_arts}\n"
                                                    f"Empty (0-byte) artifacts: {empty_arts}\n"
                                                    f"Every micro-stage must generate the complete synchronized triad on disk (.docx + .md + .json)."
                                                )
                                                return {
                                                    "decision": "continue",
                                                    "reason": msg,
                                                    "message": msg
                                                }

                    # Directive 3.1: Chapter 5 Table Ban Dual Gate
                    if any(k in model_text for k in ("chapter 5", "chapter_5", "ch5", "فصل پنجم", "فصل ۵", "discussion")):
                        for ws in workspaces:
                            if not os.path.exists(ws):
                                continue
                            for root, _, files in os.walk(ws):
                                if "scratch" in root or any(part.startswith(".") for part in root.split(os.sep) if part not in (".", "..")):
                                    continue
                                for f in files:
                                    if f.lower().endswith(".docx") and any(k in f.lower() for k in ("chapter_5", "chapter5", "ch5", "discussion")):
                                        fpath = os.path.join(root, f)
                                        try:
                                            with zipfile.ZipFile(fpath, "r") as zf:
                                                if "word/document.xml" in zf.namelist():
                                                    root_xml = ET.fromstring(zf.read("word/document.xml"))
                                                    tables = [elem for elem in root_xml.iter() if elem.tag.endswith("}tbl") or elem.tag == "tbl"]
                                                    if tables:
                                                        msg = (
                                                            f"CONSTITUTIONAL VIOLATION (Directive 3.1 — Chapter 5 Prose-Only Invariant):\n"
                                                            f"Chapter 5 Word deliverable '{f}' contains {len(tables)} table (<w:tbl>) element(s).\n"
                                                            f"Chapter 5 must strictly contain ZERO tables (100% continuous narrative prose). "
                                                            f"All statistical tables belong exclusively in Chapter 4."
                                                        )
                                                        return {
                                                            "decision": "continue",
                                                            "reason": msg,
                                                            "message": msg
                                                        }
                                        except Exception:
                                            pass

                    # Directive 5: Native OpenXML Footnotes Verification
                    for ws in workspaces:
                        if not os.path.exists(ws):
                            continue
                        for root, _, files in os.walk(ws):
                            if "scratch" in root or any(part.startswith(".") for part in root.split(os.sep) if part not in (".", "..")):
                                continue
                            for f in files:
                                if f.lower().endswith(".docx"):
                                    fpath = os.path.join(root, f)
                                    try:
                                        with zipfile.ZipFile(fpath, "r") as zf:
                                            if "word/document.xml" in zf.namelist():
                                                doc_xml = zf.read("word/document.xml")
                                                if b"<w:footnoteReference" in doc_xml:
                                                    if "word/footnotes.xml" not in zf.namelist():
                                                        msg = (
                                                            f"CONSTITUTIONAL VIOLATION (Directive 5 — Native OpenXML Footnotes):\n"
                                                            f"Word deliverable '{f}' contains footnote references (<w:footnoteReference>), "
                                                            f"but 'word/footnotes.xml' is missing from the OpenXML zip archive.\n"
                                                            f"Footnotes must be compiled as true native OpenXML elements."
                                                        )
                                                        return {
                                                            "decision": "continue",
                                                            "reason": msg,
                                                            "message": msg
                                                        }
                                    except Exception:
                                        pass
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
