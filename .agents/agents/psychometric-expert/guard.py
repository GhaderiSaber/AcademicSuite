#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/agents/psychometric_expert_guard.py

Dedicated Lifecycle Hook Guard for psychometric-expert:
Enforces:
1. Directive 12 (Worker Delegation Guard): psychometric-expert cannot spawn subagents.
2. Directive 1 (Pre-Flight Gate on CLI scripts): Mandatory view_file on skill specification before execution.
3. Raw Data Protection: Forbids mutating files in 01_raw_inputs/.
4. Directive 6 (English-Only Filenames): Strict ASCII filename enforcement.
5. Mathematical Admissibility & Heywood Case Gate: Negative variances and loadings > 1.0 blocked.
6. Directive 4 & Persian Leading Zero Standard: Naked decimals (.۰۵) and p = .000 strictly blocked.
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

    # 1. Directive 12: Worker Delegation Guard
    if tool_name in ("invoke_subagent", "define_subagent"):
        return {
            "decision": "deny",
            "reason": (
                "CONSTITUTIONAL VIOLATION (Directive 12 — Worker Delegation Guard): "
                "psychometric-expert is an execution worker and is forbidden from spawning subagents."
            )
        }

    # 2. Directive 1: Pre-Flight Gate on CLI Scripts
    if tool_name == "run_command":
        cmd = args.get("CommandLine", "")
        m = re.search(r'\.agents/skills/([\w-]+)/scripts/([\w-]+\.py)', cmd)
        if m:
            skill_name = m.group(1)
            target_skill_md = f".agents/skills/{skill_name}/SKILL.md"
            transcript_path = payload.get("transcriptPath")
            saw_view_file = False
            if transcript_path and os.path.exists(transcript_path):
                try:
                    with open(transcript_path, "r", encoding="utf-8") as tf:
                        for line in tf:
                            if not line.strip():
                                continue
                            rec = json.loads(line)
                            for tc in rec.get("tool_calls", []):
                                if tc.get("name") == "view_file":
                                    p = tc.get("args", {}).get("AbsolutePath", "")
                                    if target_skill_md in p or f"skills/{skill_name}/SKILL.md" in p:
                                        saw_view_file = True
                                        break
                            if saw_view_file:
                                break
                except Exception:
                    pass

            if not saw_view_file:
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Directive 1 — Mandatory Pre-Flight Gate): "
                        f"Attempted to execute CLI script '{m.group(2)}' without first inspecting "
                        f"the skill specification. You MUST explicitly call view_file on '{target_skill_md}' "
                        f"before executing its bundled deterministic scripts."
                    )
                }

    # 3. Raw Data Protection
    target = args.get("TargetFile") or args.get("file_path") or args.get("path") or ""
    if "01_raw_inputs" in target and tool_name in ("write_to_file", "replace_file_content", "edit_file"):
        return {
            "decision": "deny",
            "reason": (
                f"CONSTITUTIONAL VIOLATION (Raw Data Protection Invariant): "
                f"Mutating raw inputs in '01_raw_inputs/' is strictly forbidden."
            )
        }

    # 4. Directive 6: English-Only Filenames
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

        # 1. Heywood Cases & Mathematical Admissibility Gate
        # Negative error variance
        if re.search(r'(?:error\s+variance|unique\s+variance|\btheta\b)\s*[:=]\s*-\d', last_resp, re.I):
            return {
                "decision": "continue",
                "reason": (
                    "CONSTITUTIONAL VIOLATION (Mathematical Admissibility Gate): "
                    "Detected negative error variance (Heywood case) in psychometric results. "
                    "Inadmissible statistical models cannot be concluded without explicit correction."
                )
            }

        # Standardized factor loading > 1.0 (lambda > 1.0)
        loading_match = re.search(r'(?:factor\s+loading|standardized\s+loading|λ|lambda)\s*[:=]\s*([1-9]\d*\.\d+)', last_resp, re.I)
        if loading_match:
            val = float(loading_match.group(1))
            if val > 1.0:
                return {
                    "decision": "continue",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Mathematical Admissibility Gate): "
                        f"Detected standardized factor loading > 1.0 (λ = {val:.2f}). "
                        f"Standardized loadings must be bounded between -1.0 and +1.0."
                    )
                }

        # 2. Directive 4: Prohibition of p = .000
        if re.search(r'\b[pP]\s*=\s*\.?000\b', last_resp) or re.search(r'[pP]\s*=\s*۰\.۰۰۰', last_resp):
            return {
                "decision": "continue",
                "reason": (
                    "CONSTITUTIONAL VIOLATION (Directive 4 — Prohibition of p = .000): "
                    "Reporting p = .000 is strictly forbidden. Report p < .001 in English or ۰.۰۰۱ > p in Persian."
                )
            }

        # 3. Directive 4: Persian Leading Zero Standard
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
    parser = argparse.ArgumentParser(description="Psychometric Expert Lifecycle Guard")
    parser.add_argument("--event", type=str, default="PreToolUse", choices=["PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"])
    args, _ = parser.parse_known_args()

    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[psychometric_expert_guard] Error reading stdin: {e}\n")

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
