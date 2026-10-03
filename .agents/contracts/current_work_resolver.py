#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/contracts/current_work_resolver.py — Current Work Stage Resolution Contract

Resolves the active stage directories representing the 'current work' of the agent
or subagent, isolating validation and artifact checks to the work actively being executed.
Prevents cross-contamination from historical, archived, legacy, or unrelated stages.

Enforces:
1. Stage-Scoped Validation Gate: Hooks only analyze and block on validation reports
   belonging to the current work. Unrelated validation reports elsewhere in the
   workspace are strictly ignored.
2. Context Resolution Hierarchy:
   a. Active transcript tool calls (write_to_file, replace_file_content, run_command, invoke_subagent)
   b. Active user prompt / subagent descriptor CDE prompt
   c. Working directory (cwd) inside deliverables or projects
   d. Recently modified deliverable files (mtime / git status)
   e. Fallback for isolated unit tests without transcripts
"""

import os
import sys
import re
import json
import time
from typing import Dict, Any, List, Optional, Set, Tuple


GENERIC_EXCLUDED_STAGE_NAMES = {
    "stage_dir", "stage_id", "stage_name", "stage_type", "stage_status",
    "stage", "stages", "target_dir", "output_dir", "out_dir", "cwd"
}


def _clean_str(val: Any) -> str:
    if val is None:
        return ""
    return str(val).strip().strip("'\"")


def extract_active_turn_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extracts records belonging to the active turn.
    For main orchestrator transcripts with USER_INPUT, returns records from the latest USER_INPUT onward.
    For subagent transcripts (which lack USER_INPUT), returns all subagent records.
    """
    if not records or not isinstance(records, list):
        return []
    last_user_idx = -1
    for i, r in enumerate(records):
        if isinstance(r, dict) and r.get("type") == "USER_INPUT":
            last_user_idx = i
    if last_user_idx >= 0:
        return records[last_user_idx:]
    return records


def _is_ignored_path(path: str) -> bool:
    """Checks if a path should be ignored as non-deliverable infrastructure."""
    norm = path.replace("\\", "/").lower()
    segs = [s for s in norm.split("/") if s]
    ignored = {
        ".git", ".agents", ".venv", "node_modules", "archive",
        "legacy_validation", ".system_generated"
    }
    return any(ig in segs for ig in ignored)


def find_enclosing_stage_dir(cand: str, workspaces: List[str]) -> Optional[str]:
    """
    Normalizes a candidate file path, directory path, or stage identifier
    into an enclosing canonical stage directory.
    Returns the absolute directory path if found and valid, otherwise None.
    """
    cleaned = _clean_str(cand)
    if not cleaned or _is_ignored_path(cleaned):
        return None

    if cleaned.lower() in GENERIC_EXCLUDED_STAGE_NAMES:
        return None

    ws_list = [os.path.abspath(ws) for ws in (workspaces or []) if ws and os.path.isdir(ws)]
    if not ws_list:
        ws_list = [os.path.abspath(os.getcwd())]

    # Pattern A: Pure stage identifier name, e.g. "stage_02_descriptives", "stage_01", "phase_4a"
    is_pure_identifier = bool(re.match(r'^(?:stage[_\-]?\w+|hypothesis[_\-]?\w+|demographics?|descriptives?|results?|chapter[_\-]?\w+|phase[_\-]?\w+)$', cleaned, re.I))
    if is_pure_identifier and not any(sep in cleaned for sep in ("/", "\\", ".")):
        for ws in ws_list:
            for rel in ("03_deliverables", "projects", "."):
                base_p = os.path.join(ws, rel)
                if not os.path.isdir(base_p):
                    continue
                for root, dirs, _ in os.walk(base_p):
                    if _is_ignored_path(root):
                        continue
                    if os.path.basename(root).lower() == cleaned.lower():
                        return os.path.abspath(root)

    # Pattern B: File path or directory path
    abs_candidates = []
    if os.path.isabs(cleaned):
        abs_candidates.append(cleaned)
    else:
        for ws in ws_list:
            abs_candidates.append(os.path.join(ws, cleaned))
            for rel in ("03_deliverables", "projects"):
                abs_candidates.append(os.path.join(ws, rel, cleaned))
        if not workspaces:
            abs_candidates.append(os.path.abspath(cleaned))

    for p in abs_candidates:
        target = p if os.path.isdir(p) else os.path.dirname(p)
        if not os.path.exists(target):
            continue

        norm_p = os.path.abspath(target).replace("\\", "/")
        norm_target = os.path.abspath(target)
        if norm_target in ws_list or norm_target == os.path.abspath(os.sep):
            continue

        parts = [seg for seg in norm_p.split("/") if seg]

        # Check for 03_deliverables
        if "03_deliverables" in parts:
            idx = parts.index("03_deliverables")
            # If there is a child stage folder under 03_deliverables:
            if len(parts) > idx + 1:
                stage_dir = "/" + "/".join(parts[:idx + 2])
                if os.path.isdir(stage_dir) and not _is_ignored_path(stage_dir) and os.path.abspath(stage_dir) not in ws_list:
                    return os.path.abspath(stage_dir)
            else:
                # Flat 03_deliverables
                stage_dir = "/" + "/".join(parts[:idx + 1])
                if os.path.isdir(stage_dir) and os.path.abspath(stage_dir) not in ws_list:
                    return os.path.abspath(stage_dir)

        # Check for projects/<name>/03_deliverables/<stage> or projects/<name>/<stage>
        if "projects" in parts:
            idx = parts.index("projects")
            if len(parts) > idx + 3 and parts[idx + 2] == "03_deliverables":
                stage_dir = "/" + "/".join(parts[:idx + 4])
                if os.path.isdir(stage_dir) and not _is_ignored_path(stage_dir) and os.path.abspath(stage_dir) not in ws_list:
                    return os.path.abspath(stage_dir)
            elif len(parts) > idx + 2:
                stage_dir = "/" + "/".join(parts[:idx + 3])
                if os.path.isdir(stage_dir) and not _is_ignored_path(stage_dir) and os.path.abspath(stage_dir) not in ws_list:
                    return os.path.abspath(stage_dir)

        # Direct deliverable stage directory (contains manifest or validation report or deliverables)
        if os.path.isdir(target) and not _is_ignored_path(target) and norm_target not in ws_list:
            try:
                entries = os.listdir(target)
                has_indicators = (
                    "validation_report.json" in entries or
                    "manifest.json" in entries or
                    "artifact_manifest.json" in entries or
                    any(re.search(r'\.(?:docx|md|json)$', f) for f in entries)
                )
                if has_indicators:
                    return os.path.abspath(target)
            except OSError:
                pass

    return None


def resolve_current_work_stage_dirs(
    workspaces: Optional[List[str]] = None,
    payload: Optional[Dict[str, Any]] = None,
    records: Optional[List[Dict[str, Any]]] = None,
    caller: str = ""
) -> List[str]:
    """
    Authoritatively resolves the active stage directories for the current work.
    Returns an ordered, deduplicated list of absolute directory paths.
    
    If current work touches no deliverable stage (e.g. asking conceptual questions,
    editing code/hooks, or running tests), returns an empty list, ensuring hooks
    do not evaluate or block on unrelated validation reports across the project.
    """
    ws_list = [os.path.abspath(ws) for ws in (workspaces or []) if ws and os.path.isdir(ws)]
    if payload and isinstance(payload, dict) and not ws_list:
        for p in payload.get("workspacePaths", []):
            if p and os.path.isdir(p):
                ws_list.append(os.path.abspath(p))
    if not ws_list:
        ws_list = [os.path.abspath(os.getcwd())]

    raw_candidates: Set[str] = set()

    # 1. Inspect Payload Context
    if payload and isinstance(payload, dict):
        cwd = payload.get("cwd")
        if cwd and isinstance(cwd, str) and os.path.isdir(cwd):
            raw_candidates.add(cwd)

        for key in ("stage_dir", "stage", "target_dir", "target_stage"):
            val = payload.get(key)
            if val and isinstance(val, str):
                raw_candidates.add(val)

        sub_desc = payload.get("subagentDescriptor") or {}
        if isinstance(sub_desc, dict):
            p_text = sub_desc.get("prompt") or ""
            if p_text:
                try:
                    p_json = json.loads(p_text) if isinstance(p_text, str) else p_text
                    if isinstance(p_json, dict):
                        for k in ("stage_dir", "stage", "output_dir", "target_dir"):
                            if p_json.get(k):
                                raw_candidates.add(str(p_json.get(k)))
                        for req_art in p_json.get("required_artifacts", []):
                            if isinstance(req_art, str):
                                raw_candidates.add(req_art)
                        for inp in p_json.get("inputs", []):
                            if isinstance(inp, str):
                                raw_candidates.add(inp)
                except Exception:
                    pass
                for m in re.finditer(r'(?:03_deliverables|projects)/[a-zA-Z0-9_\-./]+', str(p_text)):
                    raw_candidates.add(m.group(0))
                for m in re.finditer(r'\bstage[_\-][a-zA-Z0-9_-]+\b', str(p_text), re.I):
                    val = m.group(0)
                    if val.lower() not in GENERIC_EXCLUDED_STAGE_NAMES:
                        raw_candidates.add(val)

    # 2. Inspect Transcript Records
    turn_records = []
    if records is not None:
        turn_records = extract_active_turn_records(records)
    elif payload and isinstance(payload, dict):
        transcript_path = payload.get("transcriptPath")
        if transcript_path and os.path.exists(transcript_path):
            try:
                with open(transcript_path, "r", encoding="utf-8") as tf:
                    all_recs = [json.loads(line) for line in tf if line.strip()]
                turn_records = extract_active_turn_records(all_recs)
            except Exception:
                pass

    if turn_records:
        for r in turn_records:
            if not isinstance(r, dict):
                continue
            r_type = r.get("type", "")
            content = str(r.get("content", ""))

            # Scan USER_INPUT for target stage references
            if r_type == "USER_INPUT":
                for m in re.finditer(r'(?:03_deliverables|projects)/[a-zA-Z0-9_\-./]+', content):
                    raw_candidates.add(m.group(0))
                for m in re.finditer(r'\b(?:stage|hypothesis|chapter)[_\-][a-zA-Z0-9_-]+\b', content, re.I):
                    val = m.group(0)
                    if val.lower() not in GENERIC_EXCLUDED_STAGE_NAMES:
                        raw_candidates.add(val)

            # Scan tool calls
            for tc in r.get("tool_calls", []):
                if not isinstance(tc, dict):
                    continue
                t_name = tc.get("name") or ""
                t_args = tc.get("args") or {}
                if isinstance(t_args, str):
                    try:
                        t_args = json.loads(t_args)
                    except Exception:
                        t_args = {}

                # File writing / editing tools
                if t_name in ("write_to_file", "replace_file_content", "edit_file", "apply_diff", "patch", "multi_file_edit"):
                    for k in ("TargetFile", "path", "file_path", "target_file"):
                        if t_args.get(k):
                            raw_candidates.add(str(t_args.get(k)))

                # Command execution
                elif t_name == "run_command":
                    cmd_cwd = t_args.get("Cwd")
                    if cmd_cwd:
                        raw_candidates.add(str(cmd_cwd))
                    cmd_line = str(t_args.get("CommandLine", ""))
                    for m in re.finditer(r'--(?:stage-dir|output-json|output-dir|out-dir)\s+([^\s"\'&|;]+)', cmd_line):
                        raw_candidates.add(m.group(1))
                    for m in re.finditer(r'(?:03_deliverables|projects)/[a-zA-Z0-9_\-./]+', cmd_line):
                        raw_candidates.add(m.group(0))

                # Subagent delegation
                elif t_name == "invoke_subagent":
                    subs = t_args.get("Subagents", [])
                    if isinstance(subs, str):
                        try:
                            subs = json.loads(subs)
                        except Exception:
                            subs = []
                    if isinstance(subs, list):
                        for sa in subs:
                            if isinstance(sa, dict):
                                sa_prompt = str(sa.get("Prompt", ""))
                                for m in re.finditer(r'(?:03_deliverables|projects)/[a-zA-Z0-9_\-./]+', sa_prompt):
                                    raw_candidates.add(m.group(0))
                                for m in re.finditer(r'\bstage[_\-][a-zA-Z0-9_-]+\b', sa_prompt, re.I):
                                    val = m.group(0)
                                    if val.lower() not in GENERIC_EXCLUDED_STAGE_NAMES:
                                        raw_candidates.add(val)

                # Direct message communication
                elif t_name == "send_message":
                    msg = str(t_args.get("Message", ""))
                    for m in re.finditer(r'(?:03_deliverables|projects)/[a-zA-Z0-9_\-./]+', msg):
                        raw_candidates.add(m.group(0))
                    for m in re.finditer(r'\bstage[_\-][a-zA-Z0-9_-]+\b', msg, re.I):
                        val = m.group(0)
                        if val.lower() not in GENERIC_EXCLUDED_STAGE_NAMES:
                            raw_candidates.add(val)

                # File inspection under deliverables
                elif t_name == "view_file":
                    p = str(t_args.get("AbsolutePath", ""))
                    if any(k in p for k in ("03_deliverables", "projects")):
                        raw_candidates.add(p)

            # Check tool output for validation report references
            if "validation_report.json" in content or "run_all_validators.py" in content:
                for m in re.finditer(r'(?:[a-zA-Z0-9_\-./]+/)?03_deliverables/[a-zA-Z0-9_\-./]+', content):
                    raw_candidates.add(m.group(0))

    # 3. Resolve stage directories from collected candidates
    resolved_dirs: Set[str] = set()
    for raw in raw_candidates:
        sdir = find_enclosing_stage_dir(raw, ws_list)
        if sdir and os.path.isdir(sdir) and not _is_ignored_path(sdir):
            resolved_dirs.add(os.path.abspath(sdir))

    # 4. Recently modified files heuristic (if transcript gave no direct candidates)
    if not resolved_dirs and (turn_records or payload):
        now_ts = time.time()
        for ws in ws_list:
            for rel in ("03_deliverables", "projects"):
                base_dir = os.path.join(ws, rel)
                if not os.path.isdir(base_dir):
                    continue
                for root, dirs, files in os.walk(base_dir):
                    if _is_ignored_path(root):
                        continue
                    for f in files:
                        if f.endswith((".docx", ".md", ".json")) and f != "validation_report.json":
                            fp = os.path.join(root, f)
                            try:
                                # Modified within the last 15 minutes (900 seconds)
                                if (now_ts - os.path.getmtime(fp)) < 900:
                                    sdir = find_enclosing_stage_dir(root, ws_list)
                                    if sdir and os.path.isdir(sdir):
                                        resolved_dirs.add(os.path.abspath(sdir))
                                        break
                            except OSError:
                                pass

    # 5. Isolated Unit Test Fallback (when no transcript, tool calls, or active work exists)
    if not resolved_dirs and not turn_records and not raw_candidates:
        exclude_dirs = {".git", ".agents", ".venv", "node_modules", "archive", "legacy_validation", "tests", "evals"}
        for ws in ws_list:
            for rel_root in ("projects", "03_deliverables", "."):
                p_dir = os.path.join(ws, rel_root)
                if os.path.exists(p_dir):
                    for root, dirs, files in os.walk(p_dir):
                        dirs[:] = [d for d in dirs if d not in exclude_dirs]
                        if "validation_report.json" in files:
                            resolved_dirs.add(os.path.abspath(root))

    return sorted(list(resolved_dirs))


def is_validation_report_for_current_work(report_path: str, current_stage_dirs: List[str]) -> bool:
    """Checks whether a given validation_report.json path belongs to the resolved current work."""
    if not report_path or not current_stage_dirs:
        return False
    norm_report = os.path.abspath(report_path)
    report_dir = os.path.dirname(norm_report)
    for sdir in current_stage_dirs:
        norm_sdir = os.path.abspath(sdir)
        if report_dir == norm_sdir:
            return True
        # If report is directly inside a subfolder of stage dir
        if report_dir.startswith(norm_sdir + os.sep):
            return True
    return False


def get_current_work_validation_reports(
    workspaces: Optional[List[str]] = None,
    payload: Optional[Dict[str, Any]] = None,
    records: Optional[List[Dict[str, Any]]] = None,
    caller: str = ""
) -> List[str]:
    """
    Returns existing validation_report.json file paths strictly belonging to the current work.
    Unrelated validation reports in other directories are excluded.
    """
    stage_dirs = resolve_current_work_stage_dirs(
        workspaces=workspaces,
        payload=payload,
        records=records,
        caller=caller
    )
    reports = []
    for sdir in stage_dirs:
        rep_p = os.path.join(sdir, "validation_report.json")
        if os.path.isfile(rep_p):
            reports.append(os.path.abspath(rep_p))
    return reports
