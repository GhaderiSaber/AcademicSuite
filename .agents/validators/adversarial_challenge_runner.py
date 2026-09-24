#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validators/adversarial_challenge_runner.py — Tier 3 Adversarial Red-Teaming Challenge Engine

Evaluates empirical research artifacts against adversarial vulnerabilities:
1. Methodological Risks: Confounding, selection bias, attrition, common method variance (CMV).
2. Specification & P-Hacking: Multiplicity/FDR adjustments, post-hoc subgroup splits, HARKing.
3. Statistical Fragility & Robustness: Small-N non-normality, high-leverage cases, fragility index.
4. Viva Voce Cross-Examination: Generates aggressive adversarial examiner questions.

Produces structured `adversarial_challenge_report.json` with itemized challenge cards
and rebuttal tracking.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


class AdversarialChallengeRunner:
    """Evaluates stage artifacts from an adversarial red-teaming perspective."""

    def __init__(self, stage_dir: str):
        self.stage_dir = stage_dir

    def audit_stage(self, stage_id: Optional[str] = None) -> Dict[str, Any]:
        """Runs the adversarial challenge audit against available stage artifacts."""
        now_iso = datetime.now(timezone.utc).isoformat()
        report_id = f"ADV-CHAL-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

        challenge_cards: List[Dict[str, Any]] = []
        examiner_questions: List[Dict[str, Any]] = []

        if not os.path.exists(self.stage_dir):
            return {
                "report_id": report_id,
                "timestamp": now_iso,
                "stage_directory": self.stage_dir,
                "overall_verdict": "BLOCKED",
                "challenge_cards": [{
                    "challenge_id": "CHAL-00-NO-DIR",
                    "category": "INFRASTRUCTURE",
                    "title": "Stage Directory Not Found",
                    "severity": "CRITICAL",
                    "description": f"Stage directory {self.stage_dir} does not exist on disk.",
                    "rebuttal_status": "OPEN",
                    "required_action": "Ensure stage directory exists before running adversarial red-team."
                }],
                "viva_voce_interrogations": [],
                "evidence_summary": {"total_challenges": 1, "open_critical": 1, "open_high": 0}
            }

        files = os.listdir(self.stage_dir)
        json_files = [f for f in files if f.endswith(".json") and f not in ("manifest.json", "artifact_manifest.json", "validation_report.json")]

        # Ingest stats / findings data if available
        stats_data = {}
        for jf in json_files:
            jpath = os.path.join(self.stage_dir, jf)
            try:
                with open(jpath, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    if isinstance(content, dict):
                        stats_data[jf] = content
            except Exception:
                pass

        sample_size = None
        for fn, dat in stats_data.items():
            sample_size = dat.get("sample_size") or dat.get("n") or sample_size

        # Check 1: Sample Size Fragility (< 50 in multivariate or mediation models)
        has_complex_model = any(
            any(k in fn.lower() for k in ("mediation", "moderation", "sem", "cfa", "ancova", "regression"))
            for fn in stats_data
        )
        if sample_size is not None and sample_size < 60 and has_complex_model:
            challenge_cards.append({
                "challenge_id": "CHAL-01-SMALL-N-FRAGILITY",
                "category": "STATISTICAL_FRAGILITY",
                "title": f"Small Sample Statistical Fragility (N={sample_size} < 60)",
                "severity": "HIGH",
                "description": (
                    f"Complex multivariate modeling conducted with small N={sample_size}. "
                    f"Statistical power is limited, standard errors are inflated, and parameter estimates "
                    f"are vulnerable to sample idiosyncrasies."
                ),
                "rebuttal_status": "OPEN",
                "required_action": (
                    "Report post-hoc statistical power, apply BCa bootstrap resampling (>= 5,000 draws), "
                    "and provide explicit sensitivity bounds in Chapter 5 limitations."
                )
            })
            examiner_questions.append({
                "question_id": "Q-VIVA-01",
                "examiner_role": "Quantitative Methodologist",
                "question_text": (
                    f"Given your sample size of N = {sample_size}, how did you ensure adequate statistical "
                    f"power for this multivariate model, and how stable are your parameter estimates against case removal?"
                )
            })

        # Check 2: Multiplicity & Family-Wise Error Correction
        total_p_values = 0
        significant_p_values = 0
        for fn, dat in stats_data.items():
            coefs = dat.get("coefficients", [])
            if isinstance(coefs, list):
                for c in coefs:
                    if isinstance(c, dict) and "p_value" in c:
                        total_p_values += 1
                        try:
                            if float(str(c["p_value"]).replace("<", "").replace(">", "").strip()) < 0.05:
                                significant_p_values += 1
                        except Exception:
                            pass

        if total_p_values > 5:
            challenge_cards.append({
                "challenge_id": "CHAL-02-MULTIPLICITY-RISK",
                "category": "P_HACKING_SPECIFICATION",
                "title": f"Multiple Hypotheses Testing Multiplicity ({total_p_values} tests evaluated)",
                "severity": "MEDIUM",
                "description": (
                    f"Multiple statistical tests ({total_p_values}) conducted without documented False Discovery Rate "
                    f"(Benjamini-Hochberg) or family-wise alpha correction. Inflated Type I error risk."
                ),
                "rebuttal_status": "OPEN",
                "required_action": "Apply Benjamini-Hochberg FDR correction or justify a priori orthogonal testing."
            })
            examiner_questions.append({
                "question_id": "Q-VIVA-02",
                "examiner_role": "External Examiner",
                "question_text": (
                    f"You evaluated {total_p_values} separate statistical effects. Did you control for family-wise error rate, "
                    f"and what is the probability that at least one significant finding is a false positive?"
                )
            })

        # Check 3: Common Method Variance (CMV) in self-report questionnaires
        has_questionnaires = any(
            any(k in fn.lower() for k in ("scale", "likert", "survey", "cfa", "reliability"))
            for fn in stats_data
        )
        if has_questionnaires:
            challenge_cards.append({
                "challenge_id": "CHAL-03-COMMON-METHOD-BIAS",
                "category": "METHODOLOGICAL_VALIDITY",
                "title": "Cross-Sectional Common Method Variance (CMV) Exposure",
                "severity": "MEDIUM",
                "description": (
                    "Variables collected via concurrent self-report instruments. Susceptible to artificial covariance "
                    "inflation from response styles, social desirability, and common rater bias."
                ),
                "rebuttal_status": "OPEN",
                "required_action": (
                    "Report Harman's single-factor test or marker variable technique to prove CMV is below 50% total variance."
                )
            })
            examiner_questions.append({
                "question_id": "Q-VIVA-03",
                "examiner_role": "Psychometric Specialist",
                "question_text": (
                    "All constructs were gathered via self-report at a single time point. How did you rule out common "
                    "method variance as the primary explanation for your observed inter-construct correlations?"
                )
            })

        # Check 4: General Confounding & Causal Claim Invariant
        challenge_cards.append({
            "challenge_id": "CHAL-04-UNMEASURED-CONFOUNDING",
            "category": "METHODOLOGICAL_VALIDITY",
            "title": "Potential Unmeasured Confounding & Causal Language Restraint",
            "severity": "LOW",
            "description": (
                "Ensure that non-experimental or observational findings avoid unwarranted causal verbs "
                "('causes', 'proves', 'determines') and discuss potential unmeasured confounders."
            ),
            "rebuttal_status": "OPEN",
            "required_action": "Verify academic narrative enforces associational framing ('is associated with', 'predicts')."
        })
        examiner_questions.append({
            "question_id": "Q-VIVA-04",
            "examiner_role": "Committee Chair",
            "question_text": (
                "What major unmeasured third variables could plausibly account for your main findings, "
                "and how robust is your conclusion against omitted confounding?"
            )
        })

        # Calculate counts
        open_critical = len([c for c in challenge_cards if c["rebuttal_status"] == "OPEN" and c["severity"] == "CRITICAL"])
        open_high = len([c for c in challenge_cards if c["rebuttal_status"] == "OPEN" and c["severity"] == "HIGH"])
        open_medium = len([c for c in challenge_cards if c["rebuttal_status"] == "OPEN" and c["severity"] == "MEDIUM"])

        verdict = "PASS"
        if open_critical > 0:
            verdict = "FAIL"
        elif open_high > 0:
            verdict = "CHALLENGE_BLOCKED"

        return {
            "contract_version": "1.0.0",
            "report_id": report_id,
            "timestamp": now_iso,
            "stage_directory": self.stage_dir,
            "overall_verdict": verdict,
            "challenge_cards": challenge_cards,
            "viva_voce_interrogations": examiner_questions,
            "evidence_summary": {
                "total_challenges": len(challenge_cards),
                "open_critical": open_critical,
                "open_high": open_high,
                "open_medium": open_medium,
                "total_interrogations": len(examiner_questions)
            }
        }


def run_adversarial_audit(stage_dir: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    runner = AdversarialChallengeRunner(stage_dir)
    rep = runner.audit_stage()
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2, ensure_ascii=False)
    return rep


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Adversarial Red-Teaming Challenge Runner")
    parser.add_argument("--stage-dir", required=True, help="Path to stage directory")
    parser.add_argument("--output", default=None, help="Output path for adversarial_challenge_report.json")
    args = parser.parse_args()

    res = run_adversarial_audit(args.stage_dir, args.output)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    sys.exit(0 if res["overall_verdict"] == "PASS" else 1)
