#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/agents/advisory_agents_guard.py

Dedicated Lifecycle Hook Guard for Advisory & Control Plane Subagents:
- digital-saber
- methodology-expert
- statistical-expert

Enforces:
1. Directive 12 & Directive 20: Advisors cannot delegate (invoke_subagent is forbidden).
2. Read-Only Invariant: Advisors cannot mutate files (write_to_file, replace_file_content are forbidden).
3. Execution Revocation: Advisors cannot execute shell commands (run_command is forbidden).
4. Directive 13 (Anti-Sycophancy): Obsequious flattery is strictly blocked.
5. Human-in-the-Loop Admin Gate (digital-saber): Enforces routing pricing/quotations to Saber Admin Desk (124911145).
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

MUTATION_TOOLS = {
    "write_to_file",
    "replace_file_content",
    "multi_replace_file_content",
    "apply_diff",
    "edit_file",
    "multi_file_edit",
    "batch_replace",
    "patch"
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
    caller = resolve_caller(payload)

    # 1. Directive 12: Worker Delegation Guard
    if tool_name in ("invoke_subagent", "define_subagent"):
        return {
            "decision": "deny",
            "reason": (
                f"CONSTITUTIONAL VIOLATION (Directive 12 — Worker Delegation Guard): "
                f"Advisory agent '{caller or 'advisor'}' operates on the advisory plane and is forbidden from spawning subagents. "
                f"Delegation belongs exclusively to academic-orchestrator."
            )
        }

    # 2. Read-Only Invariant
    if tool_name in MUTATION_TOOLS:
        return {
            "decision": "deny",
            "reason": (
                f"CONSTITUTIONAL VIOLATION (Advisor Read-Only Invariant): "
                f"Advisory agent '{caller or 'advisor'}' provides high-level guidance only and cannot mutate files directly."
            )
        }

    # 3. Execution Revocation
    if tool_name == "run_command":
        return {
            "decision": "deny",
            "reason": (
                f"CONSTITUTIONAL VIOLATION (Advisor Execution Revocation): "
                f"Advisory agent '{caller or 'advisor'}' lacks execution privileges and cannot execute shell commands directly."
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

        # 1. Directive 13: Anti-Sycophancy
        flattery_patterns = [
            r"^(?:great|excellent|wonderful|fantastic)\s+question",
            r"^you\s+are\s+(?:absolutely|completely)\s+right",
            r"^what\s+an\s+(?:insightful|amazing)\s+point",
            r"^پرسش\s+بسیار\s+(?:عالی|فوق[‌ ]?العاده‌ای)",
            r"^کاملاً\s+درست\s+می[‌ ]?فرمایید"
        ]
        first_few_lines = "\n".join(last_resp.strip().splitlines()[:3]).lower()
        for pat in flattery_patterns:
            if re.search(pat, first_few_lines, re.IGNORECASE):
                return {
                    "decision": "continue",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Directive 13 — Anti-Sycophancy & Tone Sobriety): "
                        "Advisory agents must maintain objective, neutral academic sobriety. "
                        "Opening conversational flattery or sycophancy is strictly forbidden."
                    )
                }

        # 2. Directive 7 & Rule 11: Human Gate for Pricing (digital-saber)
        caller = resolve_caller(payload)
        if "digital-saber" in caller or "saber" in caller:
            is_pricing_or_quote = any(w in last_resp.lower() for w in (
                "قیمت", "تومان", "هزینه", "برآورد مالی", "quotation", "price estimate", "tomans"
            ))
            if is_pricing_or_quote and "124911145" not in last_resp and "admin desk" not in last_resp.lower():
                return {
                    "decision": "continue",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Directive 7 & Rule 11 — Human Gate Required): "
                        "All quotations and pricing proposals generated by digital-saber must explicitly "
                        "state that final release requires approval from Saber Ghaderi's Admin Desk (124911145)."
                    )
                }

    except Exception:
        pass

    return {"decision": "allow"}


def main():
    parser = argparse.ArgumentParser(description="Advisory Agents Lifecycle Guard")
    parser.add_argument("--event", type=str, default="PreToolUse", choices=["PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"])
    args, _ = parser.parse_known_args()

    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[advisory_agents_guard] Error reading stdin: {e}\n")

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
