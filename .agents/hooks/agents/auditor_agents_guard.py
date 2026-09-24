#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/agents/auditor_agents_guard.py

Dedicated Lifecycle Hook Guard for Auditor & Challenger Subagents:
- evidence-auditor
- results-auditor
- statistical-auditor
- academic-challenger
- final-judge
- validation-agent

Enforces:
1. Directive 12 (Worker Delegation Guard): Auditors cannot spawn secondary subagents.
2. Auditor Read-Only Invariant: Read-only auditors cannot mutate files or run shell commands.
3. Directive 22 & Domain Validation Gates: Rejects verbal PASS without verified reports.
4. Directive 4 & APA 7 Precision: Enforces leading zero, p != .000, and statistical symbol conventions.
5. Anti-Sycophancy & Zero Grade Inflation: Enforces adversarial posture, deduction ledgers, and Human Gate Cards.
"""

import sys
import os
import re
import json
import argparse
from typing import Dict, Any, List, Optional

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HOOKS_DIR, "..", "..", ".."))
for p in (ROOT_DIR, os.path.join(ROOT_DIR, ".agents", "hooks")):
    if p not in sys.path:
        sys.path.insert(0, p)

READ_ONLY_AUDITORS = {
    "evidence-auditor",
    "results-auditor",
    "academic-challenger",
    "final-judge"
}

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
    args = tool_call.get("args", {})
    caller = resolve_caller(payload)

    # 1. Directive 12: Worker Delegation Guard
    if tool_name in ("invoke_subagent", "define_subagent"):
        return {
            "decision": "deny",
            "reason": (
                f"CONSTITUTIONAL VIOLATION (Directive 12 — Worker Delegation Guard): "
                f"Auditor subagent '{caller or 'auditor'}' is strictly an adversarial checker "
                f"and is forbidden from spawning secondary subagents."
            )
        }

    # 2. Read-Only Invariant for evaluative auditors
    if caller in READ_ONLY_AUDITORS or any(a in caller for a in READ_ONLY_AUDITORS):
        if tool_name in MUTATION_TOOLS:
            return {
                "decision": "deny",
                "reason": (
                    f"CONSTITUTIONAL VIOLATION (Auditor Read-Only Invariant): "
                    f"Auditor subagent '{caller}' is strictly an evaluative critic "
                    f"and is forbidden from mutating files directly."
                )
            }
        if tool_name == "run_command":
            return {
                "decision": "deny",
                "reason": (
                    f"CONSTITUTIONAL VIOLATION (Auditor Execution Revocation): "
                    f"Auditor subagent '{caller}' lacks execution privileges "
                    f"and is forbidden from executing shell commands directly."
                )
            }

    # 3. statistical-auditor mutation boundary (cannot edit deliverables directly)
    if "statistical-auditor" in caller and tool_name in MUTATION_TOOLS:
        target = args.get("TargetFile") or args.get("file_path") or args.get("path") or ""
        if "03_deliverables" in target or target.endswith((".docx", ".pptx")):
            return {
                "decision": "deny",
                "reason": (
                    f"CONSTITUTIONAL VIOLATION (Auditor Mutation Boundary): "
                    f"statistical-auditor is an independent auditor and cannot mutate deliverable files "
                    f"('{os.path.basename(target)}'). Direct edits belong to academic-writer."
                )
            }

    return {"decision": "allow"}


def handle_stop(payload: Dict[str, Any]) -> Dict[str, Any]:
    caller = resolve_caller(payload)
    transcript_path = payload.get("transcriptPath")
    last_response = ""

    if transcript_path and os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as tf:
                records = [json.loads(l) for l in tf if l.strip()]
            for rec in reversed(records):
                if rec.get("type") == "PLANNER_RESPONSE" and rec.get("content"):
                    last_response = rec.get("content", "")
                    break
        except Exception:
            pass

    if not last_response:
        return {"decision": "allow"}

    # 1. results-auditor checks: APA 7 precision and Persian typography
    if "results-auditor" in caller or "results" in caller:
        # Check forbidden p = .000
        if re.search(r'\b[pP]\s*=\s*\.?000\b', last_response) or re.search(r'[pP]\s*=\s*۰\.۰۰۰', last_response):
            return {
                "decision": "continue",
                "reason": (
                    "CONSTITUTIONAL VIOLATION (Directive 4 — Prohibition of p = .000): "
                    "results-auditor must enforce reporting p < .001 (or ۰.۰۰۱ > p). Reporting p = .000 is strictly forbidden."
                )
            }

        # Check naked Persian decimals (.۰۵ instead of ۰.۰۵)
        if re.search(r'(?<![۰-۹0-9])\.[۰-۹]+', last_response):
            return {
                "decision": "continue",
                "reason": (
                    "CONSTITUTIONAL VIOLATION (Directive 4 — Persian Leading Zero Standard): "
                    "Detected naked decimal in Persian text (e.g. '.۰۵'). "
                    "You must strictly preserve the leading zero in Persian ('۰.۰۵')."
                )
            }

    # 2. academic-challenger checks: Anti-Sycophancy & Falsification
    if "academic-challenger" in caller or "challenger" in caller:
        rubber_stamp_patterns = [
            r"everything looks (?:great|perfect|fine)",
            r"no methodology flaws? (?:found|detected|identified)",
            r"approved without (?:any )?(?:questions?|reservations?|challenges?)",
            r"کاملاً بدون نقص",
            r"هیچ ایرادی مشاهده نشد"
        ]
        for pat in rubber_stamp_patterns:
            if re.search(pat, last_response, re.IGNORECASE):
                return {
                    "decision": "continue",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Anti-Sycophancy & Falsification Mandate): "
                        "academic-challenger cannot issue rubber-stamp or sycophantic approvals. "
                        "You must actively interrogate methodology, sample selection, p-hacking, or unmeasured confounding, "
                        "and provide adversarial cross-examination challenges."
                    )
                }

    # 3. final-judge checks: Zero Grade Inflation & Deduction Ledgers
    if "final-judge" in caller or "judge" in caller:
        # Check naive 20/20 score
        naive_20_patterns = [
            r"نمره\s*۲۰\s*(?:از\s*۲۰)?(?:\s*عالی)?",
            r"\bgrade:\s*20\b",
            r"\bscore:\s*20(?:/20)?\b",
            r"\b20/20\b"
        ]
        has_naive_20 = any(re.search(pat, last_response, re.IGNORECASE) for pat in naive_20_patterns)
        has_publication_proof = any(w in last_response.lower() for w in ("indexed journal", "acceptance letter", "مقاله isi", "پذیرش مقاله", "scopus"))
        if has_naive_20 and not has_publication_proof:
            return {
                "decision": "continue",
                "reason": (
                    "CONSTITUTIONAL VIOLATION (Anti-Sycophancy & Zero Grade Inflation): "
                    "Awarding a naive 20/20 defense grade is strictly forbidden without verified acceptance "
                    "of an indexed journal publication. In Iranian academic defense, base scores must reflect "
                    "itemized deductions (typically -1.0 to -1.5 withheld for publication)."
                )
            }

        # Check Human Gate Card requirement
        if any(w in last_response.lower() for w in ("clearance_granted", "defense_approved", "verdict:")):
            if "124911145" not in last_response and "saber" not in last_response.lower():
                return {
                    "decision": "continue",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Directive 11 — Human Gate Card Required): "
                        "Final defense clearance decisions must format a structured Human Gate Card "
                        "for Saber Ghaderi's Admin Desk (124911145) detailing deductions, grade, and overall verdict."
                    )
                }

    # 4. evidence-auditor checks: Citation Concordance & Ghost Citations
    if "evidence-auditor" in caller or "evidence" in caller:
        claims_pass = any(w in last_response.lower() for w in ("concordance verified", "citations approved", "references verified", "verdict: pass"))
        if claims_pass:
            if "ghost citation" in last_response.lower() or "unverified reference" in last_response.lower():
                return {
                    "decision": "continue",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Directive 14 — Zero Ghost Citations): "
                        "evidence-auditor cannot approve deliverables containing ghost or unverified citations. "
                        "All bibliographic citations must be verified against academic databases (CrossRef/PubMed/SID)."
                    )
                }

    # 5. statistical-auditor checks: Heywood cases & Assumption Gating
    if "statistical-auditor" in caller:
        if re.search(r'error variance\s*=\s*-\d', last_response, re.I) or re.search(r'variance\s*<\s*0', last_response, re.I):
            return {
                "decision": "continue",
                "reason": (
                    "CONSTITUTIONAL VIOLATION (Mathematical Admissibility Gate): "
                    "statistical-auditor detected a Heywood case (negative error variance). "
                    "Model cannot be approved without explicit defect reporting and remediation."
                )
            }

    return {"decision": "allow"}


def main():
    parser = argparse.ArgumentParser(description="Auditor Subagents Lifecycle Guard")
    parser.add_argument("--event", type=str, default="PreToolUse", choices=["PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"])
    args, _ = parser.parse_known_args()

    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[auditor_agents_guard] Error reading stdin: {e}\n")

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
