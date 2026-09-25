#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/agents/project-organizer/guard.py

Dedicated Lifecycle Hook Guard for project-organizer:
Enforces:
1. Directive 12 (Worker Delegation Guard): project-organizer cannot spawn subagents.
2. Raw Data Protection: Forbids mutating or deleting files in 01_raw_inputs/.
3. Directive 23 (Clean Workspace Root): Forbids writing executable scripts into workspace root.
4. Directive 6 (English-Only Filenames): Strict ASCII filename enforcement.
5. Standard 4-Tier Project Taxonomy Scaffolding: Verifies 01_raw_inputs, 02_analysis_code, 03_deliverables, 04_references_and_lit, and project_meta.json.
"""

import sys
import os
import re
import json
import argparse
from typing import Dict, Any, List

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HOOKS_DIR, "..", "..", ".."))
for p in (ROOT_DIR, os.path.join(ROOT_DIR, ".agents", "hooks")):
    if p not in sys.path:
        sys.path.insert(0, p)

FOUR_TIER_DIRS = (
    "01_raw_inputs",
    "02_analysis_code",
    "03_deliverables",
    "04_references_and_lit"
)


def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get("toolCall", {})
    tool_name = (tool_call.get("name") or "").strip().lower()
    args = tool_call.get("args", {})

    # 1. Directive 12: Worker Delegation Guard
    if tool_name in ("invoke_subagent", "define_subagent"):
        return {
            "decision": "deny",
            "reason": (
                "CONSTITUTIONAL VIOLATION (Directive 12 — Worker Delegation Guard): "
                "project-organizer is an execution worker and is forbidden from spawning subagents."
            )
        }

    # 2. Extract targets
    target = args.get("TargetFile") or args.get("file_path") or args.get("path") or ""
    cmd = args.get("CommandLine") or ""

    # 3. Raw Data Protection (01_raw_inputs is immutable)
    if "01_raw_inputs" in target and tool_name in ("write_to_file", "replace_file_content", "edit_file", "patch"):
        # Allow initial creation of files if directory was empty, but deny mutation/overwrite of existing data
        if os.path.exists(target) and os.path.getsize(target) > 0 and args.get("Overwrite", False):
            return {
                "decision": "deny",
                "reason": (
                    f"CONSTITUTIONAL VIOLATION (Raw Data Protection Invariant): "
                    f"Overwriting files in '01_raw_inputs/' ('{os.path.basename(target)}') is strictly forbidden. "
                    f"Raw data inputs are immutable and read-only."
                )
            }

    if tool_name == "run_command" and cmd:
        if re.search(r'\b(?:rm|truncate|unlink|mv)\b.*01_raw_inputs', cmd):
            return {
                "decision": "deny",
                "reason": (
                    "CONSTITUTIONAL VIOLATION (Raw Data Protection Invariant): "
                    "Destructive shell commands targeting '01_raw_inputs/' are strictly blocked."
                )
            }

    # 4. Directive 23: Clean Workspace Root
    if target and tool_name in ("write_to_file", "replace_file_content", "edit_file"):
        clean_target = os.path.normpath(target)
        ws_paths = payload.get("workspacePaths", [ROOT_DIR])
        for ws in ws_paths:
            clean_ws = os.path.normpath(ws)
            parent = os.path.dirname(clean_target)
            if parent == clean_ws and clean_target.endswith((".py", ".sh", ".R", ".bash")):
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Directive 23 — Clean Workspace Root Standard): "
                        f"Dropping executable scripts ('{os.path.basename(clean_target)}') into repository root is forbidden. "
                        f"Route code strictly to '02_analysis_code/'."
                    )
                }

    # 5. Directive 6: English-Only Filenames
    if target and not re.match(r'^[a-zA-Z0-9_.\-/\\]+$', target):
        return {
            "decision": "deny",
            "reason": (
                f"CONSTITUTIONAL VIOLATION (Directive 6 — English-Only Filenames): "
                f"Path '{target}' contains non-ASCII characters. Use strictly English ASCII characters."
            )
        }

    return {"decision": "allow"}


def handle_stop(payload: Dict[str, Any]) -> Dict[str, Any]:
    transcript_path = payload.get("transcriptPath")
    if not transcript_path or not os.path.exists(transcript_path):
        return {"decision": "allow"}

    try:
        with open(transcript_path, "r", encoding="utf-8") as tf:
            records = [json.loads(l) for l in tf if l.strip()]

        last_resp = ""
        for rec in reversed(records):
            if rec.get("type") == "PLANNER_RESPONSE" and rec.get("content"):
                last_resp = rec.get("content", "")
                break

        claims_scaffold = any(w in last_resp.lower() for w in (
            "project scaffolded", "project initialized", "scaffolded the directory",
            "created project structure", "4-tier taxonomy created", "project structure initialized"
        ))

        if claims_scaffold:
            ws_paths = payload.get("workspacePaths", [ROOT_DIR])
            # Check for candidate project directories
            found_valid_project = False
            missing_tiers = []

            for ws in ws_paths:
                # Look in ws or projects/
                candidates = [ws]
                projects_dir = os.path.join(ws, "projects")
                if os.path.exists(projects_dir):
                    for d in os.listdir(projects_dir):
                        full = os.path.join(projects_dir, d)
                        if os.path.isdir(full):
                            candidates.append(full)

                for cand in candidates:
                    missing = [t for t in FOUR_TIER_DIRS if not os.path.exists(os.path.join(cand, t))]
                    if not missing:
                        # 4 tiers exist! Check project_meta.json
                        meta_file = os.path.join(cand, "project_meta.json")
                        if os.path.exists(meta_file):
                            found_valid_project = True
                            break
                        else:
                            missing_tiers.append("project_meta.json in " + cand)
                    else:
                        missing_tiers.append(f"{cand} missing {missing}")

            if not found_valid_project and missing_tiers:
                return {
                    "decision": "continue",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Standard 4-Tier Project Taxonomy Invariant): "
                        "Project initialization claimed, but 4-tier directory structure or 'project_meta.json' "
                        "is incomplete on disk. Required: 01_raw_inputs/, 02_analysis_code/, 03_deliverables/, "
                        "04_references_and_lit/, and project_meta.json."
                    )
                }

    except Exception:
        pass

    return {"decision": "allow"}


def main():
    parser = argparse.ArgumentParser(description="Project Organizer Lifecycle Guard")
    parser.add_argument("--event", type=str, default="PreToolUse", choices=["PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"])
    args, _ = parser.parse_known_args()

    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[project_organizer_guard] Error reading stdin: {e}\n")

    event = args.event
    if event == "PreToolUse":
        res = handle_pre_tool_use(payload)
    elif event == "Stop":
        res = handle_stop(payload)
    else:
        res = {"decision": "allow"}

    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
