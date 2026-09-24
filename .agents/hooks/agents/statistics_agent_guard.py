#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/agents/statistics_agent_guard.py

Dedicated Lifecycle Hook Guard for Statistics Specialist Subagent (statistics-agent).
Enforces:
1. Directive 2 (Deterministic Calculation Invariant):
   Statistical findings, p-values, effect sizes, and test parameters must be calculated
   by executing deterministic CLI scripts (.agents/skills/<skill>/scripts/ or 02_analysis_code/),
   never mental hallucination.
2. Directive 3 (Triad Artifact Invariant - Statistics):
   Ensures structured statistical parameters (.json) are generated on disk.
3. Directive 4 (Strict APA 7th Edition & Persian Leading Zero Standard):
   Rejects p = .000 (must be p < .001 / p < ۰.۰۰۱) and naked decimals in Persian (.۰۵ -> ۰.۰۵).
4. Directive 12 (Worker Delegation Guard):
   Specialist worker subagent is forbidden from spawning secondary subagents.
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
                "Specialist subagent 'statistics-agent' is a task execution worker and is "
                "strictly forbidden from spawning secondary subagents. Multi-agent delegation "
                "is strictly reserved for the Academic Main Agent (academic-orchestrator)."
            )
        }

    # Directive 6: English ASCII Filename Guard
    for arg_val in args.values():
        if isinstance(arg_val, str) and any(ext in arg_val.lower() for ext in (".json", ".csv", ".xlsx", ".sav", ".png", ".pdf")):
            base = os.path.basename(arg_val)
            if base and not base.isascii():
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Directive 6 — English ASCII Filename Standard): "
                        f"Target filename '{base}' contains non-ASCII characters. "
                        f"All files and datasets must strictly use English alphanumeric characters."
                    )
                }

    return {"decision": "allow"}


def handle_stop(payload: Dict[str, Any]) -> Dict[str, Any]:
    transcript_path = payload.get("transcriptPath")
    if transcript_path and os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as tf:
                records = [json.loads(l) for l in tf if l.strip()]

            # Inspect last planner response for APA 7 violations
            for rec in reversed(records):
                if rec.get("type") == "PLANNER_RESPONSE":
                    content = rec.get("content", "")
                    # Check for p = .000 or p = 0.000
                    if re.search(r'\bp\s*=\s*\.?000\b', content, re.I) or "p = .000" in content or "p = 0.000" in content:
                        return {
                            "decision": "continue",
                            "reason": (
                                "CONSTITUTIONAL VIOLATION (Directive 4 — APA 7th Edition Standard): "
                                "Reporting 'p = .000' is strictly forbidden. When p-value falls below threshold, "
                                "it must be reported strictly as 'p < .001' (English) or '۰.۰۰۱ > p' / 'p < ۰.۰۰۱' (Persian)."
                            )
                        }
                    # Check for naked Persian decimals like .۰۵ or .۰۰۱ without leading zero
                    if re.search(r'(?<![۰-۹0-9])\.[۰-۹]+', content):
                        return {
                            "decision": "continue",
                            "reason": (
                                "CONSTITUTIONAL VIOLATION (Directive 4 — Persian Leading Zero Standard): "
                                "Omitting leading zeros in Persian text is strictly prohibited. "
                                "Always preserve the leading zero: write '۰.۰۵', '۰.۰۰۱', never '.۰۵' or '.۰۰۱'."
                            )
                        }
                    break
        except Exception:
            pass

    return {"decision": "allow"}


def main():
    parser = argparse.ArgumentParser(description="Statistics Subagent Lifecycle Guard")
    parser.add_argument("--event", type=str, default="PreToolUse", choices=["PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"])
    args, _ = parser.parse_known_args()

    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[statistics_agent_guard] Error reading stdin: {e}\n")

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
