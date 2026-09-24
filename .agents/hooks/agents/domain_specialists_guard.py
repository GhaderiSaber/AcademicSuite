#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/agents/domain_specialists_guard.py

Dedicated Lifecycle Hook Guard for Domain Specialist Subagents:
- data-curator
- qualitative-analyst
- intervention-designer
- journal-strategist
- meta-analyst
- longitudinal-modmed-expert

Enforces:
1. Directive 12 (Worker Delegation Guard): Specialists cannot spawn secondary subagents.
2. Raw Data Protection (data-curator): Raw inputs are immutable.
3. Tool Permission Boundaries: Execution revocation for non-execution specialists (journal-strategist, intervention-designer).
4. Directive 23 (Clean Workspace Root): Forbids writing executable scripts into root.
5. Directive 6 & Directive 4: ASCII filenames, leading zero preservation, and p = .000 ban.
"""

import sys
import os
import re
import json
import argparse
from typing import Dict, Any

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HOOKS_DIR, "..", "..", ".."))
for p in (ROOT_DIR, os.path.join(ROOT_DIR, ".agents", "hooks")):
    if p not in sys.path:
        sys.path.insert(0, p)

NO_EXEC_SPECIALISTS = {
    "journal-strategist",
    "intervention-designer"
}


def resolve_caller(payload: Dict[str, Any]) -> str:
    caller = (payload.get("caller") or "").strip().lower()
    if not caller:
        try:
            from contracts.hook_identity_contract import resolve_hook_identity
            ident = resolve_hook_identity(payload)
            if ident and ident.agent_name and ident.agent_name != "unknown":
                caller = ident.agent_name.strip().lower()
        except Exception:
            pass
    return caller


def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get("toolCall", {})
    tool_name = (tool_call.get("name") or "").strip().lower()
    args = tool_call.get("args", {})
    caller = resolve_caller(payload)

    # 1. Directive 12: Worker Delegation Guard
    if tool_name in ("invoke_subagent", "define_subagent"):
        return {
            "decision": "deny",
            "reason": (
                f"CONSTITUTIONAL VIOLATION (Directive 12 — Worker Delegation Guard): "
                f"Specialist worker '{caller or 'domain-specialist'}' is forbidden from spawning subagents."
            )
        }

    # 2. Shell Execution Revocation for non-exec specialists
    if (caller in NO_EXEC_SPECIALISTS or any(s in caller for s in NO_EXEC_SPECIALISTS)) and tool_name == "run_command":
        return {
            "decision": "deny",
            "reason": (
                f"CONSTITUTIONAL VIOLATION (Capability Boundary): "
                f"Agent '{caller}' lacks execution privileges and is forbidden from running shell commands directly."
            )
        }

    # 3. Raw Data Protection (data-curator)
    target = args.get("TargetFile") or args.get("file_path") or args.get("path") or ""
    if "01_raw_inputs" in target and tool_name in ("write_to_file", "replace_file_content", "edit_file"):
        return {
            "decision": "deny",
            "reason": (
                f"CONSTITUTIONAL VIOLATION (Raw Data Protection Invariant): "
                f"Mutating raw inputs in '01_raw_inputs/' is strictly forbidden. "
                f"Curation artifacts must be exported to '01_raw_inputs/curated/' or 'data/processed/'."
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
                        f"Dropping executable scripts ('{os.path.basename(clean_target)}') into repository root is forbidden."
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

        if not last_resp:
            return {"decision": "allow"}

        # 1. Directive 4: Prohibition of p = .000
        if re.search(r'\b[pP]\s*=\s*\.?000\b', last_resp) or re.search(r'[pP]\s*=\s*۰\.۰۰۰', last_resp):
            return {
                "decision": "continue",
                "reason": (
                    "CONSTITUTIONAL VIOLATION (Directive 4 — Prohibition of p = .000): "
                    "Reporting p = .000 is strictly forbidden. Report p < .001 or ۰.۰۰۱ > p."
                )
            }

        # 2. Directive 4: Persian Leading Zero Standard
        if re.search(r'(?<![۰-۹0-9])\.[۰-۹]+', last_resp):
            return {
                "decision": "continue",
                "reason": (
                    "CONSTITUTIONAL VIOLATION (Directive 4 — Persian Leading Zero Standard): "
                    "Detected naked decimal in Persian text (e.g. '.۰۵'). "
                    "You must strictly preserve the leading zero in Persian ('۰.۰۵')."
                )
            }

    except Exception:
        pass

    return {"decision": "allow"}


def main():
    parser = argparse.ArgumentParser(description="Domain Specialists Lifecycle Guard")
    parser.add_argument("--event", type=str, default="PreToolUse", choices=["PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"])
    args, _ = parser.parse_known_args()

    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[domain_specialists_guard] Error reading stdin: {e}\n")

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
