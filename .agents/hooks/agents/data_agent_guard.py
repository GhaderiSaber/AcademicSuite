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
from typing import Dict, Any, Optional, List, Tuple

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HOOKS_DIR, "..", "..", ".."))
for p in (ROOT_DIR, os.path.join(ROOT_DIR, ".agents", "hooks")):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from safety_hooks import is_raw_data_path, is_raw_data_command, is_root_script_target, is_deliverables_script_target
except ImportError:
    def is_raw_data_path(p: str) -> bool:
        if not p: return False
        norm = p.replace("\\", "/").lower()
        return "01_raw_inputs" in norm or "raw_" in norm or norm.endswith((".sav", ".raw.csv", ".raw.xlsx"))

    def is_raw_data_command(c: str) -> bool:
        if not c: return False
        cl = c.lower()
        return any(k in cl for k in ("01_raw_inputs", "raw_data", "raw.xlsx", "raw.sav", "raw.csv")) and any(d in cl for d in ("rm ", "unlink ", "truncate ", "> ", ">> ", "shred "))

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
                "Specialist subagent 'data-agent' is a task execution worker and is "
                "strictly forbidden from spawning secondary subagents."
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


def check_simulation_decimal_noise(workspaces: List[str]) -> Tuple[bool, str]:
    """Audits simulated datasets for realistic bounded decimal noise (Directive 9)."""
    for ws in workspaces:
        if not ws or not os.path.exists(ws):
            continue
        for root, _, files in os.walk(ws):
            if "scratch" in root or any(part.startswith(".") for part in root.split(os.sep) if part not in (".", "..")):
                continue
            for f in files:
                if f.lower().startswith("simulated_") and f.lower().endswith((".xlsx", ".csv")):
                    fpath = os.path.join(root, f)
                    try:
                        import pandas as pd
                        df = pd.read_excel(fpath) if f.lower().endswith(".xlsx") else pd.read_csv(fpath)
                        num_cols = df.select_dtypes(include=["number"]).columns
                        if len(num_cols) >= 2:
                            means = df[num_cols].mean()
                            all_integer = all(abs(m - round(m)) < 1e-4 for m in means)
                            if all_integer:
                                sample_means = [round(float(m), 2) for m in means[:4]]
                                return False, (
                                    f"Simulated dataset '{f}' contains synthetic whole-integer column means {sample_means}. "
                                    f"Simulated data must exhibit realistic bounded empirical decimal noise "
                                    f"(mu = mu_target + delta, delta ~ Uniform(+-0.08, +-0.25))."
                                )
                    except Exception:
                        pass
    return True, ""


def handle_stop(payload: Dict[str, Any]) -> Dict[str, Any]:
    workspaces = payload.get("workspacePaths", [ROOT_DIR])
    ok, reason = check_simulation_decimal_noise(workspaces)
    if not ok:
        return {
            "decision": "continue",
            "reason": f"CONSTITUTIONAL VIOLATION (Directive 9 — Empirical Decimal Noise Invariant):\n{reason}"
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
    elif event == "Stop":
        res = handle_stop(payload)
    else:
        res = {"decision": "allow"}

    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
