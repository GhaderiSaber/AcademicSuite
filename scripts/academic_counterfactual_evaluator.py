#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_counterfactual_evaluator.py — Counterfactual Evaluation Engine

Performs counterfactual comparisons:
    CURRENT BASELINE vs. CANDIDATE (or multiple candidates: Baseline vs A vs B vs C)

Evaluates candidates on:
1. Original failure case (the case motivating the candidate)
2. Related cases (development and curriculum cases testing the capability)
3. Regression cases (permanent baseline suite guarding past fixes)
4. Adversarial cases (stress tests and edge cases where appropriate)
5. Held-out cases (cryptographically frozen validation scenarios)

Key Capabilities:
- Identifies:
    * what changed
    * what improved
    * what regressed
    * which behavior changed
    * which failure disappeared
    * which new failure appeared
- Multi-candidate support: Baseline vs A vs B vs C.
- Retains complementary candidates via Pareto dominance instead of forcing single scalar rankings.
- Enforces the Minimum Improvement Policy:
    Candidate must improve its target capability AND must not regress protected capabilities.
- Produces counterfactual comparison reports stored under `learning/evaluations/reports/`.
"""

import os
import sys
import json
import uuid
import hashlib
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Set

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

from scripts.academic_evaluation_lab import AcademicEvaluationLab, HeldoutTamperingError


class CounterfactualEvaluationError(Exception):
    """Raised when counterfactual evaluation encounters an invalid state."""
    pass


class AcademicCounterfactualEvaluator:
    """
    Evaluates candidate improvements counterfactually against current baselines
    across diverse benchmark suites and independent evaluation dimensions.
    """

    DIMENSIONS = AcademicEvaluationLab.DIMENSIONS

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or ROOT_DIR)
        self.eval_root = os.path.join(self.base_dir, "learning", "evaluations")
        self.reports_dir = os.path.join(self.eval_root, "reports")
        self.candidates_dir = os.path.join(self.base_dir, "learning", "candidates")
        self.lab = AcademicEvaluationLab(base_dir=self.base_dir)

        os.makedirs(self.reports_dir, exist_ok=True)

    def load_evaluation_suites(
        self,
        target_capability: str,
        original_case_id: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Loads test cases organized into 5 functional suites:
        - original_failure: the specific case motivating the candidate
        - related: cases testing the same capability
        - regression: all active permanent regression cases
        - adversarial: adversarial stress cases
        - heldout: cryptographically frozen cases
        """
        all_cases = self.lab.load_cases(include_retired=False)

        suites: Dict[str, List[Dict[str, Any]]] = {
            "original_failure": [],
            "related": [],
            "regression": [],
            "adversarial": [],
            "heldout": []
        }

        for c in all_cases:
            cid = c.get("case_id")
            st = c.get("suite_type")
            cap = c.get("capability", "").lower()

            if original_case_id and cid == original_case_id:
                suites["original_failure"].append(c)
            elif st == "regression":
                suites["regression"].append(c)
            elif st == "adversarial":
                suites["adversarial"].append(c)
            elif st == "heldout":
                suites["heldout"].append(c)
            elif cap == target_capability.lower() or target_capability.lower() in str(c.get("tags", [])).lower():
                suites["related"].append(c)

        # If original_failure was not found by exact ID, use first related or regression case as representative
        if not suites["original_failure"]:
            if suites["regression"]:
                suites["original_failure"].append(suites["regression"][0])
            elif suites["related"]:
                suites["original_failure"].append(suites["related"][0])

        return suites

    def compare_single_candidate(
        self,
        candidate_id: str,
        target_capability: str,
        baseline_payload: Dict[str, Any],
        candidate_payload: Dict[str, Any],
        original_case_id: Optional[str] = None,
        custom_suites: Optional[Dict[str, List[Dict[str, Any]]]] = None
    ) -> Dict[str, Any]:
        """
        Executes counterfactual evaluation of a single candidate against baseline
        across all test partitions.
        """
        # 1. Cryptographic held-out verification before running tests
        heldout_valid, heldout_errors = self.lab.verify_heldout_integrity()
        if not heldout_valid:
            raise HeldoutTamperingError(f"Heldout integrity violated: {heldout_errors}")

        suites = custom_suites or self.load_evaluation_suites(target_capability, original_case_id)

        all_diffs = []
        what_improved = []
        what_regressed = []
        disappeared_failures = []
        new_failures = []
        behavior_changes = []

        baseline_case_results = {}
        candidate_case_results = {}

        total_cases = 0
        baseline_passes = 0
        candidate_passes = 0

        target_failures_baseline = 0
        target_failures_candidate = 0

        protected_regressions = 0

        # Evaluate across all partitions
        for suite_name, cases in suites.items():
            for case in cases:
                total_cases += 1
                cid = case.get("case_id", "UNKNOWN")

                # Run baseline
                res_base = self.lab.evaluate_candidate_on_case(
                    candidate_id="BASELINE",
                    case=case,
                    candidate_artifacts=baseline_payload
                )
                baseline_case_results[cid] = res_base
                if res_base["verdict"] == "PASS":
                    baseline_passes += 1

                # Run candidate
                res_cand = self.lab.evaluate_candidate_on_case(
                    candidate_id=candidate_id,
                    case=case,
                    candidate_artifacts=candidate_payload,
                    baseline_artifacts=baseline_payload
                )
                candidate_case_results[cid] = res_cand
                if res_cand["verdict"] == "PASS":
                    candidate_passes += 1

                # Extract failure types
                base_failures = set(d["failure_type"] for d in res_base["diagnostics"])
                cand_failures = set(d["failure_type"] for d in res_cand["diagnostics"])

                # Check improvements (failures present in baseline that disappeared in candidate)
                resolved = base_failures - cand_failures
                for r in resolved:
                    what_improved.append(f"[{cid}] Resolved defect: {r}")
                    disappeared_failures.append(r)

                # Check regressions (failures present in candidate that were NOT in baseline)
                regressed = cand_failures - base_failures
                for rg in regressed:
                    what_regressed.append(f"[{cid}] New regression: {rg}")
                    new_failures.append(rg)
                    if suite_name in ["regression", "heldout"]:
                        protected_regressions += 1

                # Track target capability progress
                if suite_name in ["original_failure", "related"]:
                    target_failures_baseline += len(base_failures)
                    target_failures_candidate += len(cand_failures)

                # Behavior trajectory changes
                if res_base["verdict"] != res_cand["verdict"] or resolved or regressed:
                    behavior_changes.append({
                        "case_id": cid,
                        "suite": suite_name,
                        "baseline_verdict": res_base["verdict"],
                        "candidate_verdict": res_cand["verdict"],
                        "resolved_failures": list(resolved),
                        "introduced_failures": list(regressed)
                    })

        # Multi-Dimensional Metrics Compilation
        dimensional_summary = {}
        for dim in self.DIMENSIONS:
            base_dim_fails = sum(
                1 for r in baseline_case_results.values()
                if r.get("dimensional_evaluations", {}).get(dim, {}).get("verdict") == "FAIL"
            )
            cand_dim_fails = sum(
                1 for r in candidate_case_results.values()
                if r.get("dimensional_evaluations", {}).get(dim, {}).get("verdict") == "FAIL"
            )
            dimensional_summary[dim] = {
                "baseline_failures": base_dim_fails,
                "candidate_failures": cand_dim_fails,
                "improved": cand_dim_fails < base_dim_fails,
                "regressed": cand_dim_fails > base_dim_fails
            }

        # Minimum Improvement Policy Evaluation
        target_improved = (target_failures_candidate < target_failures_baseline) or len(disappeared_failures) > 0
        zero_regressions = protected_regressions == 0 and len(what_regressed) == 0
        adversarial_clear = all(
            r["verdict"] == "PASS" for cid, r in candidate_case_results.items()
            if cid in [c.get("case_id") for c in suites.get("adversarial", [])]
        ) if suites.get("adversarial") else True

        promotion_eligible = target_improved and zero_regressions and adversarial_clear

        report = {
            "contract_version": "1.0.0",
            "report_id": f"CCR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
            "candidate_id": candidate_id,
            "target_capability": target_capability,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary_metrics": {
                "total_cases_evaluated": total_cases,
                "baseline_pass_rate": baseline_passes / total_cases if total_cases else 1.0,
                "candidate_pass_rate": candidate_passes / total_cases if total_cases else 1.0,
                "total_resolved_defects": len(disappeared_failures),
                "total_new_regressions": len(new_failures),
                "protected_suite_regressions": protected_regressions
            },
            "counterfactual_analysis": {
                "what_changed": f"Evaluated across {total_cases} test cases spanning 5 suites. Candidate altered outcomes in {len(behavior_changes)} cases.",
                "what_improved": what_improved,
                "what_regressed": what_regressed,
                "which_behavior_changed": behavior_changes,
                "which_failure_disappeared": list(set(disappeared_failures)),
                "which_new_failure_appeared": list(set(new_failures))
            },
            "dimensional_comparison": dimensional_summary,
            "minimum_improvement_policy": {
                "target_capability_improved": target_improved,
                "zero_regressions_verified": zero_regressions,
                "adversarial_clearance": adversarial_clear,
                "promotion_eligible": promotion_eligible,
                "policy_decision": "ELIGIBLE_FOR_PROMOTION" if promotion_eligible else "PROMOTION_BLOCKED"
            }
        }

        return report

    def compare_multiple_candidates(
        self,
        target_capability: str,
        baseline_payload: Dict[str, Any],
        candidate_payloads: Dict[str, Dict[str, Any]],
        original_case_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compares Baseline vs Candidate A vs Candidate B vs Candidate C.
        Identifies complementary candidates across the 8 dimensions instead of forcing
        every candidate into a single scalar ranking.
        """
        multi_report_id = f"CCR-MULTI-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        suites = self.load_evaluation_suites(target_capability, original_case_id)

        candidate_reports = {}
        for cand_id, payload in candidate_payloads.items():
            rep = self.compare_single_candidate(
                candidate_id=cand_id,
                target_capability=target_capability,
                baseline_payload=baseline_payload,
                candidate_payload=payload,
                original_case_id=original_case_id,
                custom_suites=suites
            )
            candidate_reports[cand_id] = rep

        # Compute Complementary Candidates & Pareto Front
        pareto_front, complementary_profiles = self._compute_pareto_and_complementary(candidate_reports)

        multi_report = {
            "contract_version": "1.0.0",
            "multi_report_id": multi_report_id,
            "target_capability": target_capability,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "candidates_evaluated": list(candidate_payloads.keys()),
            "candidate_reports": candidate_reports,
            "pareto_front": pareto_front,
            "complementary_candidates": complementary_profiles,
            "retained_candidates": list(set(pareto_front + [c["candidate_id"] for c in complementary_profiles]))
        }

        return multi_report

    def save_report(self, report_data: Dict[str, Any]) -> str:
        """Saves evaluation comparison report to learning/evaluations/reports/<report_id>.json."""
        rep_id = report_data.get("report_id") or report_data.get("multi_report_id") or f"CCR-{uuid.uuid4().hex[:6].upper()}"
        file_path = os.path.join(self.reports_dir, f"{rep_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        return file_path

    def _compute_pareto_and_complementary(
        self,
        candidate_reports: Dict[str, Dict[str, Any]]
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Computes Pareto non-dominated candidates across the 8 dimensions
        and identifies complementary candidates specializing in different dimensions.
        """
        dim_strengths = {}
        for cid, rep in candidate_reports.items():
            dims = rep.get("dimensional_comparison", {})
            dim_strengths[cid] = {
                d: 1 if dims.get(d, {}).get("improved") and not dims.get(d, {}).get("regressed") else 0
                for d in self.DIMENSIONS
            }

        pareto_candidates = []
        for c1 in candidate_reports.keys():
            dominated = False
            for c2 in candidate_reports.keys():
                if c1 == c2:
                    continue
                # c2 dominates c1 if c2 is >= c1 on all dims and > on at least one
                s1 = dim_strengths[c1]
                s2 = dim_strengths[c2]
                if all(s2[d] >= s1[d] for d in self.DIMENSIONS) and any(s2[d] > s1[d] for d in self.DIMENSIONS):
                    # Also check regressions count
                    reg1 = candidate_reports[c1]["summary_metrics"]["total_new_regressions"]
                    reg2 = candidate_reports[c2]["summary_metrics"]["total_new_regressions"]
                    if reg2 <= reg1:
                        dominated = True
                        break
            if not dominated:
                pareto_candidates.append(c1)

        # Identify complementary specializations (candidates excelling on different dimensions)
        complementary = []
        for dim in self.DIMENSIONS:
            best_cands = [
                cid for cid, s in dim_strengths.items()
                if s.get(dim, 0) == 1 and candidate_reports[cid]["minimum_improvement_policy"]["zero_regressions_verified"]
            ]
            for bc in best_cands:
                if bc not in [c["candidate_id"] for c in complementary]:
                    complementary.append({
                        "candidate_id": bc,
                        "specialized_dimension": dim,
                        "rationale": f"Candidate excelling on dimension '{dim}' without regressions."
                    })

        return pareto_candidates, complementary


def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Counterfactual Evaluation CLI")
    parser.add_argument("--candidate", default="CAND-TEST-001", help="Candidate ID")
    parser.add_argument("--capability", default="statistical-data-analyst", help="Target capability")
    parser.add_argument("--multi-demo", action="store_true", help="Run multi-candidate demonstration (Baseline vs A vs B vs C)")
    args = parser.parse_args()

    evaluator = AcademicCounterfactualEvaluator()

    if args.multi_demo:
        baseline_payload = {
            "statistics": {
                "f_value": 4.1,
                "p_value": "p = .04",
                "assumptions_checked": ["normality"]
            },
            "narrative": "تحلیل واریانس نشان داد اثر معنادار است."
        }
        cand_a_payload = {
            "statistics": {
                "estimand": "Treatment effect estimand",
                "effect_size": 0.22,
                "confidence_interval": [0.08, 0.36],
                "artifact_path": "03_lmm.json",
                "assumptions_checked": ["homogeneity of slopes", "normality"]
            },
            "reasoning": {
                "repeated_measures_structure": "Within-subject 3 waves",
                "missingness": "Little MCAR evaluated",
                "imbalance": "Balanced cell sizes",
                "covariance_structure": "Compound symmetry tested",
                "estimand": "Fixed treatment effect",
                "candidate_model_comparison": "LMM vs RM-ANOVA evaluated"
            },
            "narrative": "مقایسه مدل‌ها نشان داد ساختار تکرارسنجش و داده‌های گمشده بررسی شدند (۰.۰۱ > p)."
        }
        cand_b_payload = {
            "statistics": {
                "estimand": "ATE estimand",
                "effect_size": 0.20,
                "confidence_interval": [0.05, 0.35],
                "artifact_path": "03_checkpoint.json"
            },
            "reasoning": {
                "repeated_measures_structure": "Repeated measures structure",
                "missingness": "Missingness evaluated",
                "imbalance": "Imbalance evaluated",
                "covariance_structure": "Covariance structure evaluated",
                "estimand": "Target estimand",
                "candidate_model_comparison": "Candidate model comparison performed"
            },
            "narrative": "ملاحظات ساختار داده و مقایسه مدل‌ها ارزیابی گردید (۰.۰۵ > p)."
        }

        multi_rep = evaluator.compare_multiple_candidates(
            target_capability=args.capability,
            baseline_payload=baseline_payload,
            candidate_payloads={"Candidate_A_DecisionTree": cand_a_payload, "Candidate_B_VerificationGate": cand_b_payload}
        )
        rep_path = evaluator.save_report(multi_rep)
        print(f"Multi-candidate counterfactual comparison report saved to: {rep_path}")
        print(json.dumps(multi_rep["retained_candidates"], indent=2))


if __name__ == "__main__":
    main()
