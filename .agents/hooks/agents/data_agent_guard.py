#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/agents/data_agent_guard.py

Dedicated Lifecycle Hook Guard for Data Management Specialist Subagent (data-agent).
Enforces:
1. Raw Data Immutability:
   Prevents any modification, overwriting, truncation, or deletion of raw datasets
   in 01_raw_inputs/, *.sav, raw_*.xlsx, raw_*.csv.
2. Directive 12 (Worker Delegation Guard):
   Specialist worker subagent is forbidden from spawning secondary subagents.
3. Directive 6 (English ASCII Filename Standard):
   All output files and schemas must strictly use English ASCII characters.
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

try:
    from safety_hooks import is_raw_data_path, is_raw_data_command
except ImportError:
    def is_raw_data_path(p: str) -> bool:
        if not p: return False
        norm = p.replace("\\", "/").lower()
        return "01_raw_inputs" in norm or "raw_" in norm or norm.endswith((".sav", ".raw.csv", ".raw.xlsx"))

    def is_raw_data_command(c: str) -> bool:
        if not c: return False
        cl = c.lower()
        return any(k in cl for k in ("01_raw_inputs", "raw_data", "raw.xlsx", "raw.sav", "raw.csv")) and any(d in cl for d in ("rm ", "unlink ", "truncate ", "> ", ">> ", "shred "))


def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get("toolCall", {})
    tool_name = (tool_call.get("name") or "").strip().lower()
    args = tool_call.get("args", {})

    # Directive 12: Worker Delegation Guard
    if tool_name in ("invoke_subagent", "define_subagent"):
        return {
            "decision": "deny",
            "reason": (
                "CONSTITUTIONAL VIOLATION (Directive 12 — Worker Delegation Guard): "
                "Specialist subagent 'data-agent' is a task execution worker and is "
                "strictly forbidden from spawning secondary subagents."
            )
        }

    # Raw Data Immutability Guard on file mutations
    if tool_name in ("write_to_file", "replace_file_content", "edit_file", "patch"):
        target_file = args.get("TargetFile") or args.get("target") or args.get("file_path") or ""
        if is_raw_data_path(target_file):
            return {
                "decision": "deny",
                "reason": (
                    f"SAFETY VIOLATION (Raw Data Immutability Invariant): "
                    f"Target file '{target_file}' is in an immutable raw input directory. "
                    f"Overwriting or mutating raw data files is strictly prohibited. "
                    f"Save cleaned/processed datasets to '02_analysis_code/' or '02_analysis_code/cleaned/'."
                )
            }

    # Raw Data Immutability Guard on shell commands
    if tool_name == "run_command":
        cmd = args.get("CommandLine", "")
        if is_raw_data_command(cmd):
            return {
                "decision": "deny",
                "reason": (
                    f"SAFETY VIOLATION (Destructive Raw Data Command Guard): "
                    f"Command '{cmd}' appears to modify, truncate, or delete raw input data. "
                    f"Raw data files must remain permanently read-only and immutable."
                )
            }

    # Directive 6: ASCII Filename Guard
    for arg_val in args.values():
        if isinstance(arg_val, str) and any(ext in arg_val.lower() for ext in (".json", ".csv", ".xlsx", ".sav")):
            base = os.path.basename(arg_val)
            if base and not base.isascii():
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Directive 6 — English ASCII Filename Standard): "
                        f"Target filename '{base}' contains non-ASCII characters."
                    )
                }

    return {"decision": "allow"}


def main():
    parser = argparse.ArgumentParser(description="Data Subagent Lifecycle Guard")
    parser.add_argument("--event", type=str, default="PreToolUse", choices=["PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"])
    args, _ = parser.parse_known_args()

    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[data_agent_guard] Error reading stdin: {e}\n")

    event = args.event
    if event == "PreToolUse":
        res = handle_pre_tool_use(payload)
    else:
        res = {"decision": "allow"}

    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
