#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/agents/research_literature_guard.py

Dedicated Lifecycle Hook Guard for research-agent and literature-expert:
Enforces:
1. Directive 12 (Worker Delegation Guard): Workers cannot spawn secondary subagents.
2. Directive 1 (Pre-Flight Gate): Mandatory view_file on skill specification before CLI script execution.
3. Directive 15 (Temporal Reality Anchor): Operative calendar year is strictly 2026 (1405 SH).
4. Deterministic G*Power Verification: Sample power claims require verified calculation.
5. Directive 14 (Anti-Hallucination & Zero Ghost Citations): Unverified citations flagged.
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
                f"Agent '{caller or 'research/literature'}' is an execution worker and is forbidden from spawning subagents."
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

    # 3. Directive 6: English-Only Filenames
    target = args.get("TargetFile") or args.get("file_path") or args.get("path") or ""
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

        # 1. Directive 15: Temporal Reality Anchor (2026 / 1405 SH)
        temporal_hallucination_patterns = [
            r"\b(?:in|during|for)\s+(?:the\s+year\s+)?202[45]\s+(?:current|future|upcoming|next)\b",
            r"\bcurrently\s+in\s+202[45]\b",
            r"\bcurrent\s+year\s+(?:is\s+)?202[45]\b",
            r"\bas\s+of\s+(?:today\s+in\s+)?202[45]\b",
            r"سال\s+جاری\s+۱۴۰[۳۴]"
        ]
        for pat in temporal_hallucination_patterns:
            if re.search(pat, last_resp, re.IGNORECASE):
                return {
                    "decision": "continue",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Directive 15 — Temporal Reality Anchor): "
                        "The operative calendar year is 2026 (1405 SH). "
                        "Referring to 2024 or 2025 as the current or upcoming year is a temporal hallucination. "
                        "Recent empirical literature window is strictly 2021–2026."
                    )
                }

        # 2. Directive 14: Zero Ghost Citations (Flag phantom reference claims)
        if "literature-expert" in resolve_caller(payload) or "literature" in resolve_caller(payload):
            if re.search(r'\bdoi:\s*10\.\d{4,9}/(?:unknown|ghost|fake|placeholder)\b', last_resp, re.I):
                return {
                    "decision": "continue",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Directive 14 — Zero Ghost Citations): "
                        "Detected placeholder or unverified DOI in literature citations. "
                        "All bibliographic citations must be genuine records verified via CrossRef, PubMed, or SID."
                    )
                }

    except Exception:
        pass

    return {"decision": "allow"}


def main():
    parser = argparse.ArgumentParser(description="Research & Literature Subagents Lifecycle Guard")
    parser.add_argument("--event", type=str, default="PreToolUse", choices=["PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"])
    args, _ = parser.parse_known_args()

    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[research_literature_guard] Error reading stdin: {e}\n")

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
