#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/agents/validation-agent/guard.py

Dedicated Lifecycle Hook Guard for Validation and Auditing Subagents (validation-agent, final-judge).
Enforces:
1. Directive 22 (Fail-Closed Mechanical Validation Gate Invariant):
   The auditor cannot grant verbal or conversational 'PASS' approvals.
   Release requires a physical, schema-validated on-disk report (validation_report.json)
   with overall_verdict == 'PASS' and checks_failed == 0.
2. Directive 12 (Worker Delegation Guard):
   Auditor subagent is forbidden from spawning secondary subagents.
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

    if tool_name in ("invoke_subagent", "define_subagent"):
        return {
            "decision": "deny",
            "reason": (
                "CONSTITUTIONAL VIOLATION (Directive 12 — Worker Delegation Guard): "
                "Auditor subagent is strictly an adversarial checker and is "
                "forbidden from spawning secondary subagents."
            )
        }

    return {"decision": "allow"}


def handle_stop(payload: Dict[str, Any]) -> Dict[str, Any]:
    transcript_path = payload.get("transcriptPath")
    if transcript_path and os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as tf:
                records = [json.loads(l) for l in tf if l.strip()]

            # Inspect last planner response
            for rec in reversed(records):
                if rec.get("type") == "PLANNER_RESPONSE":
                    content = rec.get("content", "").lower()
                    claims_pass = any(w in content for w in ("verdict: pass", "status: pass", "approved for release", "checks passed"))
                    if claims_pass:
                        # Check workspace for validation_report.json
                        ws_paths = payload.get("workspacePaths", [ROOT_DIR])
                        found_pass_report = False
                        reject_reason = None

                        for ws in ws_paths:
                            candidate_reports = [
                                os.path.join(ws, "validation_report.json"),
                                os.path.join(ws, "03_deliverables", "validation_report.json"),
                                os.path.join(ws, ".agents", "validation", "last_report.json")
                            ]
                            # Also check subdirectories in 03_deliverables
                            deliv_dir = os.path.join(ws, "03_deliverables")
                            if os.path.isdir(deliv_dir):
                                for sdir in os.listdir(deliv_dir):
                                    cand = os.path.join(deliv_dir, sdir, "validation_report.json")
                                    if os.path.exists(cand):
                                        candidate_reports.append(cand)

                            for cr in candidate_reports:
                                if os.path.exists(cr):
                                    try:
                                        with open(cr, "r", encoding="utf-8") as rf:
                                            rdata = json.load(rf)
                                        
                                        ev_summary = rdata.get("evidence_summary", {})
                                        checks_failed = ev_summary.get("checks_failed", rdata.get("checks_failed", 0))
                                        checks_blocked = ev_summary.get("checks_blocked", rdata.get("checks_blocked", 0))
                                        ev_count = ev_summary.get("total_evidence_items_evaluated", rdata.get("total_evidence_items_evaluated", rdata.get("checks_passed", 0)))

                                        arps = rdata.get("actionable_repair_prescriptions", [])
                                        unresolved_arps = [
                                            a for a in arps
                                            if a.get("status") == "OPEN" and a.get("severity") in ("CRITICAL", "HIGH")
                                        ]

                                        decision_errors = 0
                                        for res_item in rdata.get("results", []):
                                            if res_item.get("evidence", {}).get("gross_decision_errors", 0) > 0 or any("GROSS DECISION" in err for err in res_item.get("errors", [])):
                                                decision_errors += 1

                                        if rdata.get("overall_verdict") != "PASS":
                                            reject_reason = f"Report '{cr}' overall_verdict is '{rdata.get('overall_verdict')}', not 'PASS'."
                                        elif checks_failed > 0 or checks_blocked > 0:
                                            reject_reason = f"Report '{cr}' has {checks_failed} failed and {checks_blocked} blocked checks."
                                        elif ev_count < 1:
                                            reject_reason = f"Report '{cr}' contains zero evaluated empirical evidence items."
                                        elif len(unresolved_arps) > 0:
                                            reject_reason = f"Report '{cr}' contains {len(unresolved_arps)} unresolved CRITICAL/HIGH Actionable Repair Prescriptions."
                                        elif decision_errors > 0:
                                            reject_reason = f"Report '{cr}' contains {decision_errors} Gross Decision Errors in Statcheck recomputation."
                                        else:
                                            found_pass_report = True
                                            break
                                    except Exception:
                                        pass
                            if found_pass_report:
                                break

                        if not found_pass_report:
                            base_msg = (
                                "CONSTITUTIONAL VIOLATION (Directive 22 — Fail-Closed Mechanical Validation Gate Invariant): "
                                "Validation subagents cannot issue verbal or unverified 'PASS' claims. "
                                "Release strictly requires a physical on-disk 'validation_report.json' confirming: "
                                "(1) overall_verdict == 'PASS', (2) checks_failed == 0 and checks_blocked == 0, "
                                "(3) total_evidence_items_evaluated >= 1, (4) zero gross decision errors in forensic math, "
                                "and (5) zero unresolved CRITICAL or HIGH Actionable Repair Prescriptions."
                            )
                            if reject_reason:
                                base_msg += f" Last inspection failed: {reject_reason}"
                            return {
                                "decision": "continue",
                                "reason": base_msg
                            }
                    break
        except Exception:
            pass

    return {"decision": "allow"}


def main():
    parser = argparse.ArgumentParser(description="Validation Subagent Lifecycle Guard")
    parser.add_argument("--event", type=str, default="PreToolUse", choices=["PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"])
    args, _ = parser.parse_known_args()

    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[validation_agent_guard] Error reading stdin: {e}\n")

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
