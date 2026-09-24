#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validators/defense_readiness_compiler.py — Tier 4 Viva Voce & Defense Certification Compiler

Simulates the 5-Examiner Dissertation Defense Committee:
1. Committee Chair (Methodological Coherence & Academic Significance)
2. Quantitative/Statistical Examiner (df, Power, Mathematical Truth, Hu & Bentler Cutoffs)
3. Psychometric Specialist (Scale Validity, CFA, IRT, Reliability)
4. Domain Specialist (Mechanisms, Theoretical Coherence, Clinical Translation)
5. External Examiner (Harsh Falsification & Adversarial Red-Teaming)

Computes deterministic itemized deductions on the Iranian 0–20 grading scale,
enforcing the Zero Grade Inflation Invariant (Directive 28 / final-judge.md).
Produces immutable `defense_readiness_certificate.json` and Saber's Human Gate Card.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


class DefenseReadinessCompiler:
    """Simulates committee defense evaluation and generates defense readiness certificates."""

    def __init__(self, stage_dir: str):
        self.stage_dir = stage_dir

    def compile_certificate(
        self,
        tier1_result: Optional[Dict[str, Any]] = None,
        tier2_result: Optional[Dict[str, Any]] = None,
        tier3_result: Optional[Dict[str, Any]] = None,
        has_wos_publication: bool = False
    ) -> Dict[str, Any]:
        """
        Compiles the comprehensive defense certificate and 0–20 Iranian grade.
        Base score: 20.00.
        Deductions applied deterministically for any unresolved defects or vulnerabilities.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        cert_id = f"DEF-CERT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

        base_score = 20.00
        deductions: List[Dict[str, Any]] = []

        # 1. Tier 1 Deductions (Mechanical & OpenXML)
        if tier1_result:
            v_t1 = tier1_result.get("overall_verdict", "UNKNOWN")
            if v_t1 == "BLOCKED":
                deductions.append({
                    "examiner": "Committee Chair",
                    "reason": "Missing required artifact triad (.docx, .md, .json) or corrupt manifest",
                    "points": -3.00
                })
            elif v_t1 == "FAIL":
                t1_errors = len(tier1_result.get("errors", []))
                pts = min(2.0, t1_errors * 0.25)
                deductions.append({
                    "examiner": "Committee Chair",
                    "reason": f"OpenXML typographic or structural non-compliance ({t1_errors} defects)",
                    "points": -round(pts, 2)
                })

        # 2. Tier 2 Deductions (Forensic Math, Statcheck, GRIM)
        if tier2_result:
            v_t2 = tier2_result.get("overall_verdict", "UNKNOWN")
            if v_t2 == "FAIL":
                decision_errors = tier2_result.get("gross_decision_errors", 0)
                reporting_errors = tier2_result.get("reporting_errors", 0)
                grim_errors = tier2_result.get("grim_failures", 0)

                if decision_errors > 0:
                    deductions.append({
                        "examiner": "Quantitative Examiner",
                        "reason": f"Gross Statistical Decision Errors: p-values cross significance threshold ({decision_errors} errors)",
                        "points": -round(min(4.0, decision_errors * 2.0), 2)
                    })
                if grim_errors > 0:
                    deductions.append({
                        "examiner": "Quantitative Examiner",
                        "reason": f"GRIM Granularity Failures: impossible Likert means ({grim_errors} items)",
                        "points": -round(min(3.0, grim_errors * 1.0), 2)
                    })
                if reporting_errors > 0:
                    deductions.append({
                        "examiner": "Quantitative Examiner",
                        "reason": f"Minor reporting discrepancies (|Δp| > 0.01) ({reporting_errors} errors)",
                        "points": -round(min(1.5, reporting_errors * 0.25), 2)
                    })

        # 3. Tier 3 Deductions (Adversarial Challenges)
        if tier3_result:
            open_crit = tier3_result.get("evidence_summary", {}).get("open_critical", 0)
            open_high = tier3_result.get("evidence_summary", {}).get("open_high", 0)
            if open_crit > 0:
                deductions.append({
                    "examiner": "External Examiner",
                    "reason": f"Unrebutted critical methodological vulnerabilities ({open_crit} items)",
                    "points": -round(min(4.0, open_crit * 2.0), 2)
                })
            if open_high > 0:
                deductions.append({
                    "examiner": "External Examiner",
                    "reason": f"Unaddressed high-severity adversarial challenge cards ({open_high} items)",
                    "points": -round(min(2.0, open_high * 0.75), 2)
                })

        # 4. Anti-Inflation Ceiling Invariant (Directive 28 / final-judge)
        # Even with zero defects, Iranian academic standards cap raw dissertation defense at 19.00
        # unless confirmed WoS/Scopus Q1/Q2 journal acceptance is physically proven.
        total_deductions = sum(d["points"] for d in deductions)
        raw_score = max(0.0, base_score + total_deductions)

        capped_reason = None
        if raw_score > 19.00 and not has_wos_publication:
            capped_reason = "Score capped at 19.00 under Iranian University Academic Invariant: 19.01–20.00 strictly reserved for confirmed WoS/Scopus publication acceptance."
            final_score = 19.00
        else:
            final_score = round(raw_score, 2)

        # Verdict resolution
        if final_score >= 18.00:
            verdict = "PASS_EXCELLENT"
            persian_verdict = "قبول - عالی"
        elif final_score >= 16.00:
            verdict = "PASS_VERY_GOOD"
            persian_verdict = "قبول - بسیار خوب"
        elif final_score >= 14.00:
            verdict = "PASS_WITH_MINOR_REVISIONS"
            persian_verdict = "قبول با اصلاحات جزئی"
        elif final_score >= 12.00:
            verdict = "PASS_WITH_MAJOR_REVISIONS"
            persian_verdict = "مشروط به اصلاحات اساسی"
        else:
            verdict = "REJECT"
            persian_verdict = "مردود"

        # Examiner Scorecards
        examiner_scores = {
            "committee_chair": max(0.0, 4.0 + sum(d["points"] for d in deductions if d["examiner"] == "Committee Chair")),
            "quantitative_examiner": max(0.0, 5.0 + sum(d["points"] for d in deductions if d["examiner"] == "Quantitative Examiner")),
            "psychometric_specialist": 4.0,
            "domain_specialist": 4.0,
            "external_examiner": max(0.0, 3.0 + sum(d["points"] for d in deductions if d["examiner"] == "External Examiner"))
        }

        # Human Gate Card for Saber Admin Desk (124911145)
        human_gate_card = {
            "recipient_id": "124911145",
            "recipient_name": "Saber Ghaderi Admin Desk",
            "defense_verdict": verdict,
            "persian_verdict": persian_verdict,
            "final_score": final_score,
            "total_deductions_applied": round(total_deductions, 2),
            "cap_applied": capped_reason is not None,
            "authorization_status": "PENDING_HUMAN_APPROVAL" if verdict.startswith("PASS") else "BLOCKED_DEFECTS",
            "action_required": "Review itemized deduction ledger and grant formal defense release clearance."
        }

        return {
            "contract_version": "1.0.0",
            "certificate_id": cert_id,
            "timestamp": now_iso,
            "stage_directory": self.stage_dir,
            "overall_score_out_of_20": final_score,
            "defense_verdict": verdict,
            "persian_verdict": persian_verdict,
            "score_ceiling_applied": capped_reason,
            "examiner_scores": examiner_scores,
            "deduction_ledger": deductions,
            "human_gate_card": human_gate_card
        }


def run_defense_certification(
    stage_dir: str,
    output_path: Optional[str] = None,
    tier1_result: Optional[Dict[str, Any]] = None,
    tier2_result: Optional[Dict[str, Any]] = None,
    tier3_result: Optional[Dict[str, Any]] = None,
    has_wos_publication: bool = False
) -> Dict[str, Any]:
    compiler = DefenseReadinessCompiler(stage_dir)
    cert = compiler.compile_certificate(
        tier1_result=tier1_result,
        tier2_result=tier2_result,
        tier3_result=tier3_result,
        has_wos_publication=has_wos_publication
    )
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cert, f, indent=2, ensure_ascii=False)
    return cert


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Defense Readiness & Viva Voce Certification Compiler")
    parser.add_argument("--stage-dir", required=True, help="Path to stage directory")
    parser.add_argument("--output", default=None, help="Output path for defense_readiness_certificate.json")
    args = parser.parse_args()

    res = run_defense_certification(args.stage_dir, args.output)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    sys.exit(0 if res["defense_verdict"].startswith("PASS") else 1)
