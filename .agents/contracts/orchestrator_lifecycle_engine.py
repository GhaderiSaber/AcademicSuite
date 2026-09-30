#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/contracts/orchestrator_lifecycle_engine.py

Headless lifecycle state machine, defect tracking, and deliverable integrity engine
for academic-orchestrator. Modularized from academic-orchestrator/guard.py to maintain
Directive 18 modularity standards and eliminate agent token burn.
"""

import os
import sys
import re
import json
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Tuple, Optional

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(ENGINE_DIR, "..", ".."))

try:
    from contracts.critique_detection_contract import is_meaningful_user_critique, extract_clean_user_message
except ImportError:
    try:
        from critique_detection_contract import is_meaningful_user_critique, extract_clean_user_message
    except ImportError:
        def is_meaningful_user_critique(user_text, **kw):
            return False, None
        def extract_clean_user_message(raw_text):
            return re.sub(r"<[^>]+>", "", str(raw_text)).strip()

try:
    from contracts.canonical_pipelines import find_files_matching
except ImportError:
    try:
        from canonical_pipelines import find_files_matching
    except ImportError:
        def find_files_matching(w, p):
            return []


def is_user_critique_active(records: List[Dict[str, Any]]) -> Tuple[bool, str, List[Dict[str, Any]]]:
    """Detects if an active user critique exists in the transcript."""
    last_user_idx = -1
    user_content = ""
    for idx, r in enumerate(records):
        if r.get("type") == "USER_INPUT":
            last_user_idx = idx
            user_content = str(r.get("content", ""))
    active_records = records[last_user_idx + 1:] if last_user_idx >= 0 else records
    clean_user = extract_clean_user_message(user_content)
    is_critique, _ = is_meaningful_user_critique(
        clean_user,
        is_subagent=False,
        caller="academic-orchestrator"
    )
    return is_critique, clean_user, active_records


def is_validation_failure_active(
    records: List[Dict[str, Any]],
    workspaces: Optional[List[str]] = None,
    root_dir: Optional[str] = None
) -> Tuple[bool, str, List[Dict[str, Any]]]:
    """Checks transcript and on-disk deliverables for active validation failure."""
    base_root = root_dir or ROOT_DIR
    last_user_idx = -1
    for idx, r in enumerate(records):
        if r.get("type") == "USER_INPUT":
            last_user_idx = idx
    active_records = records[last_user_idx + 1:] if last_user_idx >= 0 else records

    # 1. Check active records in transcript
    for rec in reversed(active_records):
        t = rec.get("type", "")
        src = rec.get("source", "")
        if t in ("EPHEMERAL_MESSAGE",) or src in ("SYSTEM_SDK",):
            continue
        content = str(rec.get("content", ""))
        if "File Path: `file:///" in content or "Total Lines:" in content:
            continue
        if content.strip().startswith('{"File":') and '"LineNumber":' in content:
            continue

        if any(k in content.lower() for k in ("validation_report.json", "overall_verdict", "checks_failed", "validation cascade", "validation audit")):
            has_fail = (
                re.search(r'\boverall_verdict[\'":\s]+fail\b', content, re.IGNORECASE)
                or re.search(r'\bverdict[\'":\s]+fail\b', content, re.IGNORECASE)
                or re.search(r'\boverall_verdict\s+of\s+\*?\*?fail\*?\*?', content, re.IGNORECASE)
                or re.search(r'checks_failed[\'":\s]+[1-9]\d*', content, re.IGNORECASE)
                or ("STAGE VERIFICATION ADVISORY" in content and "FAIL" in content)
            )
            has_pass = (
                re.search(r'\boverall_verdict[\'":\s]+pass\b', content, re.IGNORECASE)
                or re.search(r'\boverall_verdict\s+of\s+\*?\*?pass\*?\*?', content, re.IGNORECASE)
            ) and re.search(r'checks_failed[\'":\s]+0\b', content, re.IGNORECASE)

            if has_pass:
                return False, "", active_records
            if has_fail:
                summary = "Validation failed: overall_verdict is FAIL"
                m_failed = re.search(r'(\d+)\s+total\s+`?checks_failed`?|checks_failed[\'":\s]+(\d+)', content, re.IGNORECASE)
                if m_failed:
                    num = m_failed.group(1) or m_failed.group(2)
                    summary = f"Validation failed ({num} checks failed, overall_verdict: FAIL)"
                return True, summary, active_records

    # 2. Check on disk in workspaces
    ws_list = workspaces or [base_root]
    for ws in ws_list:
        if not ws or not os.path.exists(ws):
            continue
        candidate_paths = [
            os.path.join(ws, "03_deliverables", "validation_report.json"),
            os.path.join(ws, "validation_report.json")
        ]
        deliv_dir = os.path.join(ws, "03_deliverables")
        if os.path.isdir(deliv_dir):
            for sdir in os.listdir(deliv_dir):
                cand = os.path.join(deliv_dir, sdir, "validation_report.json")
                if os.path.exists(cand):
                    candidate_paths.append(cand)
        for cp in candidate_paths:
            if os.path.exists(cp):
                try:
                    with open(cp, "r", encoding="utf-8") as vf:
                        v_data = json.load(vf)
                    verdict = str(v_data.get("overall_verdict", "")).strip().upper()
                    ev_sum = v_data.get("evidence_summary", {})
                    checks_failed = ev_sum.get("checks_failed", v_data.get("checks_failed", 0))
                    if verdict == "FAIL" or (isinstance(checks_failed, int) and checks_failed > 0):
                        summary = f"Validation report '{os.path.basename(cp)}' overall_verdict is FAIL ({checks_failed} checks failed)"
                        return True, summary, active_records
                except Exception:
                    pass

    return False, "", active_records


def get_defect_and_learning_lifecycle_state(
    records: List[Dict[str, Any]],
    workspaces: Optional[List[str]] = None,
    root_dir: Optional[str] = None
) -> Tuple[str, List[str], str, str]:
    """
    Evaluates global multi-turn conversation state machine across turn boundaries.
    
    States:
    - 'NO_DEFECT': Zero active critique or validation failure.
    - 'LEARNING_REQUIRED': Critique or validation failure is active and has not completed evaluation.
    - 'PENDING_GRADUATION': Evaluation-agent ran, but candidates remain ungraduated on disk.
    - 'REMEDIATION_PHASE': Learning cascade completed and candidates are graduated. Delivery
      workers (academic-writer, data-agent, statistics-agent) are AUTHORIZED to recompile deliverables.
    """
    base_root = root_dir or ROOT_DIR
    latest_crit_idx = -1
    latest_crit_txt = ""
    latest_val_idx = -1
    latest_val_txt = ""
    latest_eval_idx = -1

    for idx, r in enumerate(records):
        t = r.get("type", "")
        src = r.get("source", "")
        content = str(r.get("content", ""))

        if t == "USER_INPUT":
            clean = extract_clean_user_message(content)
            is_crit, _ = is_meaningful_user_critique(clean, is_subagent=False, caller="academic-orchestrator")
            if is_crit:
                latest_crit_idx = idx
                latest_crit_txt = clean

        # Check for evaluation-agent invocation in this record
        for tc in r.get("tool_calls", []):
            if (tc.get("name") or "").lower() == "invoke_subagent":
                subs = tc.get("args", {}).get("Subagents", [])
                if isinstance(subs, str):
                    try:
                        subs = json.loads(subs, strict=False)
                    except Exception:
                        subs = []
                for s in (subs if isinstance(subs, list) else []):
                    if isinstance(s, dict) and "evaluation-agent" in (s.get("TypeName") or s.get("Role") or "").lower():
                        latest_eval_idx = idx

        # Check for validation failures in transcript
        if t in ("EPHEMERAL_MESSAGE",) or src in ("SYSTEM_SDK",):
            continue
        if "File Path: `file:///" in content or "Total Lines:" in content:
            continue
        if content.strip().startswith('{"File":') and '"LineNumber":' in content:
            continue

        if any(k in content.lower() for k in ("validation_report.json", "overall_verdict", "checks_failed", "validation cascade", "validation audit")):
            has_fail = (
                re.search(r'\boverall_verdict[\'":\s]+fail\b', content, re.IGNORECASE)
                or re.search(r'\bverdict[\'":\s]+fail\b', content, re.IGNORECASE)
                or re.search(r'\boverall_verdict\s+of\s+\*?\*?fail\*?\*?', content, re.IGNORECASE)
                or re.search(r'checks_failed[\'":\s]+[1-9]\d*', content, re.IGNORECASE)
                or ("STAGE VERIFICATION ADVISORY" in content and "FAIL" in content)
            )
            has_pass = (
                re.search(r'\boverall_verdict[\'":\s]+pass\b', content, re.IGNORECASE)
                or re.search(r'\boverall_verdict\s+of\s+\*?\*?pass\*?\*?', content, re.IGNORECASE)
            ) and re.search(r'checks_failed[\'":\s]+0\b', content, re.IGNORECASE)

            if has_pass:
                latest_val_idx = -1
                latest_val_txt = ""
            elif has_fail:
                latest_val_idx = idx
                summary = "Validation failed: overall_verdict is FAIL"
                m_failed = re.search(r'(\d+)\s+total\s+`?checks_failed`?|checks_failed[\'":\s]+(\d+)', content, re.IGNORECASE)
                if m_failed:
                    num = m_failed.group(1) or m_failed.group(2)
                    summary = f"Validation failed ({num} checks failed, overall_verdict: FAIL)"
                latest_val_txt = summary

    # Check on-disk validation failure
    disk_val_fail = False
    disk_val_summary = ""
    ws_list = workspaces or [base_root]
    for ws in ws_list:
        if not ws or not os.path.exists(ws):
            continue
        candidate_paths = [
            os.path.join(ws, "03_deliverables", "validation_report.json"),
            os.path.join(ws, "validation_report.json")
        ]
        deliv_dir = os.path.join(ws, "03_deliverables")
        if os.path.isdir(deliv_dir):
            for sdir in os.listdir(deliv_dir):
                cand = os.path.join(deliv_dir, sdir, "validation_report.json")
                if os.path.exists(cand):
                    candidate_paths.append(cand)
        for cp in candidate_paths:
            if os.path.exists(cp):
                try:
                    with open(cp, "r", encoding="utf-8") as vf:
                        v_data = json.load(vf)
                    verdict = str(v_data.get("overall_verdict", "")).strip().upper()
                    ev_sum = v_data.get("evidence_summary", {})
                    checks_failed = ev_sum.get("checks_failed", v_data.get("checks_failed", 0))
                    if verdict == "FAIL" or (isinstance(checks_failed, int) and checks_failed > 0):
                        disk_val_fail = True
                        disk_val_summary = f"Validation report '{os.path.basename(cp)}' overall_verdict is FAIL ({checks_failed} checks failed)"
                        break
                except Exception:
                    pass
        if disk_val_fail:
            break

    # Determine defect index
    defect_idx = -1
    defect_desc = ""
    defect_label = ""
    if latest_crit_idx >= 0:
        defect_idx = latest_crit_idx
        defect_desc = latest_crit_txt
        defect_label = "Critique"
    if latest_val_idx >= 0 and latest_val_idx >= defect_idx:
        defect_idx = latest_val_idx
        defect_desc = latest_val_txt
        defect_label = "Validation Failure"
    if disk_val_fail and defect_idx < 0:
        defect_idx = 0
        defect_desc = disk_val_summary
        defect_label = "Validation Failure"

    if defect_idx < 0 and not disk_val_fail:
        return "NO_DEFECT", [], "", ""

    # Check pending candidates on disk
    pending_cands = []
    cand_dir = os.path.join(base_root, ".agents", "learning", "candidates")
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

    # Compare evaluation timing with defect occurrence
    if latest_eval_idx >= 0 and latest_eval_idx >= defect_idx:
        if pending_cands:
            return "PENDING_GRADUATION", pending_cands, defect_desc, defect_label
        return "REMEDIATION_PHASE", [], defect_desc, defect_label

    return "LEARNING_REQUIRED", [], defect_desc, defect_label


def audit_triad_artifacts_completion(
    records: List[Dict[str, Any]],
    workspaces: List[str]
) -> Tuple[bool, str]:
    """Audits whether required artifacts from subagent delegation envelopes exist on disk."""
    for r in records:
        for tc in r.get("tool_calls", []):
            if (tc.get("name") or "").lower() == "invoke_subagent":
                sub_list = tc.get("args", {}).get("Subagents", [])
                if isinstance(sub_list, str):
                    try:
                        sub_list = json.loads(sub_list, strict=False)
                    except Exception:
                        sub_list = []
                if isinstance(sub_list, list):
                    for sub in sub_list:
                        if not isinstance(sub, dict):
                            continue
                        p_text = sub.get("Prompt", "")
                        try:
                            from contracts.delegation_envelope_parser import validate_delegation_prompt
                            _, _, env = validate_delegation_prompt(p_text, expected_worker=sub.get("TypeName"))
                        except Exception:
                            env = None
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
                                return False, msg
    return True, ""


def audit_chapter5_docx_tables(workspaces: List[str]) -> Tuple[bool, str]:
    """Audits Chapter 5 Word deliverables strictly in 03_deliverables/ for zero <w:tbl> elements."""
    for ws in workspaces:
        if not ws or not os.path.exists(ws):
            continue
        cand_dirs = [os.path.join(ws, "03_deliverables")] if os.path.isdir(os.path.join(ws, "03_deliverables")) else [ws]
        for c_dir in cand_dirs:
            for root, _, files in os.walk(c_dir):
                rel = os.path.relpath(root, ws) if ws else root
                if any(p in ("01_raw_inputs", "02_analysis_code", "04_references_and_lit", "scratch") or p.startswith(".") for p in rel.split(os.sep)):
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
                                        return False, msg
                        except Exception:
                            pass
    return True, ""


def audit_native_docx_footnotes(workspaces: List[str]) -> Tuple[bool, str]:
    """Audits Word deliverables strictly in 03_deliverables/ for native footnotes.xml."""
    for ws in workspaces:
        if not ws or not os.path.exists(ws):
            continue
        cand_dirs = [os.path.join(ws, "03_deliverables")] if os.path.isdir(os.path.join(ws, "03_deliverables")) else [ws]
        for c_dir in cand_dirs:
            for root, _, files in os.walk(c_dir):
                rel = os.path.relpath(root, ws) if ws else root
                if any(p in ("01_raw_inputs", "02_analysis_code", "04_references_and_lit", "scratch") or p.startswith(".") for p in rel.split(os.sep)):
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
                                            return False, msg
                        except Exception:
                            pass
    return True, ""
