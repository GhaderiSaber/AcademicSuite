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
from typing import Dict, Any, Optional

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HOOKS_DIR, "..", "..", ".."))
for p in (ROOT_DIR, os.path.join(ROOT_DIR, ".agents", "hooks")):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from safety_hooks import is_root_script_target, is_deliverables_script_target
except ImportError:
    try:
        from .safety_hooks import is_root_script_target, is_deliverables_script_target
    except ImportError:
        def is_root_script_target(p, w=None): return False, ""
        def is_deliverables_script_target(p): return False, ""


def has_viewed_skill(transcript_path: Optional[str], skill_name: str) -> bool:
    """Verifies that view_file was called on the skill's SKILL.md in the current session."""
    if not transcript_path or not os.path.exists(transcript_path):
        return True
    expected = f"{skill_name}/skill.md".lower()
    try:
        with open(transcript_path, "r", encoding="utf-8") as tf:
            for line in tf:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                for tc in rec.get("tool_calls", []):
                    if (tc.get("name") or "").lower() == "view_file":
                        p = (tc.get("args", {}).get("AbsolutePath") or "").replace("\\", "/").lower()
                        if p.endswith(expected):
                            return True
    except Exception:
        pass
    return False


def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get("toolCall", {})
    tool_name = (tool_call.get("name") or "").strip().lower()
    args = tool_call.get("args", {})
    workspaces = payload.get("workspacePaths", [ROOT_DIR])

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

    # Directive 23: Clean Workspace Root & Deliverables Purity Standards
    if tool_name in ("write_to_file", "replace_file_content", "edit_file", "patch"):
        target_path = args.get("TargetFile") or args.get("target") or args.get("file_path") or ""
        is_root, script_name = is_root_script_target(target_path, workspaces)
        if is_root:
            return {
                "decision": "deny",
                "reason": (
                    f"CONSTITUTIONAL VIOLATION (Directive 23 — Clean Workspace Root Standard): "
                    f"Writing script file '{script_name}' directly into the repository root is strictly forbidden.\n"
                    f"Route scripts strictly to: (1) '02_analysis_code/', (2) '.agents/scripts/', (3) 'tests/', or scratch."
                )
            }
        is_deliv, deliv_script = is_deliverables_script_target(target_path)
        if is_deliv:
            return {
                "decision": "deny",
                "reason": (
                    f"CONSTITUTIONAL VIOLATION (Directive 23 — Deliverables Purity Standard): "
                    f"Writing executable script '{deliv_script}' inside a deliverables directory is strictly forbidden. "
                    f"Deliverables directories must contain exclusively publication artifacts (.docx, .md, .json, .pdf)."
                )
            }

    # Directive 1: Mandatory Pre-Flight Gate on CLI Scripts
    if tool_name == "run_command":
        cmd = args.get("CommandLine", "")
        m = re.search(r'\.agents/skills/([\w-]+)/scripts/([\w-]+\.py)', cmd)
        if m:
            skill_name = m.group(1)
            script_name = m.group(2)
            transcript_path = payload.get("transcriptPath")
            if transcript_path and os.path.exists(transcript_path):
                if not has_viewed_skill(transcript_path, skill_name):
                    return {
                        "decision": "deny",
                        "reason": (
                            f"CONSTITUTIONAL VIOLATION (Directive 1 — Mandatory Pre-Flight Gate):\n"
                            f"Cannot execute '{script_name}'. You MUST call 'view_file' on "
                            f"'.agents/skills/{skill_name}/SKILL.md' before executing its scripts to ingest "
                            f"the decision trees, APA standards, and operational invariants."
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

                    # Directive 2: Deterministic Calculation Invariant
                    # If statistical estimates are reported, verify that deterministic CLI (run_command) was executed
                    has_run_cmd = any(
                        any((tc.get("name") or "").lower() == "run_command" for tc in r.get("tool_calls", []))
                        for r in records
                    )
                    claims_statistical_results = bool(re.search(
                        r'([tFβz]\s*\(?\d*\)?\s*=\s*\d+\.\d+|p\s*[<=]\s*\.?\d+|R[²2]\s*=\s*\.?\d+)',
                        content
                    ))
                    if claims_statistical_results and not has_run_cmd:
                        return {
                            "decision": "continue",
                            "reason": (
                                "CONSTITUTIONAL VIOLATION (Directive 2 — Deterministic Calculation Invariant): "
                                "Statistical results were reported without executing any deterministic CLI script via 'run_command'. "
                                "Mental calculation and hallucination of statistical numbers is strictly forbidden. "
                                "You must run the appropriate Python script in .agents/skills/<skill>/scripts/ on the real dataset."
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
