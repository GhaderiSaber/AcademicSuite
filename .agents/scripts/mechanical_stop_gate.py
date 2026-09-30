#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/scripts/mechanical_stop_gate.py — Antigravity 2.18.1 Mechanical Stop Verification Gate

Deterministic Stop lifecycle completion gate:
1. Subagent Safety: Subagents always terminate cleanly with decision: "allow".
2. Benchmark / Verification Release Gate: When a formal validation run is active,
   verifies that validation_report.json reports overall_verdict == "PASS" and zero checks failed.
3. Interactive Turns: Allows clean termination without infinite loops.
"""

import sys
import os
import json
from typing import Dict, Any


def evaluate_stop(payload: Dict[str, Any]) -> Dict[str, Any]:
    # 1. Subagents are always allowed to finish cleanly
    if payload.get("isSubagent") or payload.get("parentConversationId") or payload.get("parentConversationIds"):
        return {"decision": "allow"}

    caller = str(payload.get("caller") or payload.get("agentName") or "").lower().strip()
    if caller and caller not in ("academic-orchestrator", "default", "main"):
        # Specialized subagents stop cleanly
        return {"decision": "allow"}

    # 2. Check for active validation report in artifacts or workspace
    search_dirs = []
    art_dir = payload.get("artifactDirectoryPath")
    if art_dir and os.path.isdir(art_dir):
        search_dirs.append(art_dir)

    for ws in payload.get("workspacePaths", []):
        if ws and os.path.isdir(ws):
            search_dirs.append(ws)
            # Also check results/ subdir
            cand_results = os.path.join(ws, "evals", "results")
            if os.path.isdir(cand_results):
                search_dirs.append(cand_results)

    report_path = None
    for d in search_dirs:
        cand = os.path.join(d, "validation_report.json")
        if os.path.isfile(cand):
            report_path = cand
            break

    # Only enforce stop refusal if explicitly in benchmark / evaluation mode
    strict_eval_mode = (
        os.environ.get("ANTIGRAVITY_VERIFICATION_MODE") == "1" or
        os.environ.get("ACADEMIC_EVAL_MODE") == "1" or
        payload.get("verificationMode") is True
    )

    if report_path and strict_eval_mode:
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
            verdict = str(report.get("overall_verdict", "")).upper()
            failed_count = report.get("checks_failed", 0)
            if verdict != "PASS" or failed_count > 0:
                return {
                    "decision": "continue",
                    "reason": f"Gate Refusal: validation_report.json reports {failed_count} failures (verdict: {verdict}). Correct defects before concluding."
                }
        except Exception as e:
            sys.stderr.write(f"[mechanical_stop_gate] Note on validation report parsing: {e}\n")

    # Clean exit
    return {"decision": "allow"}


def main():
    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception:
        pass

    result = evaluate_stop(payload)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
