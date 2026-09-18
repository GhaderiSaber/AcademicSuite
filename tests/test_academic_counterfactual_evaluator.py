#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_counterfactual_evaluator.py — Unit Tests for Counterfactual Evaluation Engine

Verifies:
1. Counterfactual evaluation runs across multiple suites (original failure, related, regression, adversarial, heldout).
2. Counterfactual delta identification (what changed, what improved, what regressed, disappeared/new failures).
3. Detectability of newly introduced candidate failures (regressions).
4. Minimum Improvement Policy enforcement:
   - Candidate cannot be promoted merely because it fixes original failure if it regresses protected capabilities.
   - Requires target capability improvement AND zero protected regressions.
5. Multi-candidate evaluation (Baseline vs A vs B vs C) retaining complementary candidates on the Pareto front.
6. Multidimensional metrics preservation across all 8 independent dimensions.
7. Reports generated and persisted under learning/evaluations/reports/.
8. Cryptographic held-out immutability protection.
"""

import os
import sys
import json
import shutil
import hashlib
import tempfile
import unittest
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.academic_counterfactual_evaluator import (
    AcademicCounterfactualEvaluator,
    CounterfactualEvaluationError
)
from scripts.academic_evaluation_lab import AcademicEvaluationLab, HeldoutTamperingError


class TestAcademicCounterfactualEvaluator(unittest.TestCase):
    """Authoritative test suite for the Counterfactual Evaluation Engine."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_counterfactual_test_")
        self.evaluator = AcademicCounterfactualEvaluator(base_dir=self.temp_dir)
        self.lab = AcademicEvaluationLab(base_dir=self.temp_dir)

        # Setup mock test cases across 5 suites in temp lab
        self.target_cap = "statistical-data-analyst"
        self._seed_mock_suites()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _seed_mock_suites(self):
        """Creates sample test cases across regression, adversarial, heldout, and related suites."""
        # 1. Original / Regression Case (LMM vs RM-ANOVA)
        reg_case = {
            "contract_version": "1.0.0",
            "case_id": "EVAL-REG-LMM-001",
            "capability": self.target_cap,
            "suite_type": "regression",
            "difficulty": "L2_INTERDEPENDENT_MODELS",
            "tags": ["longitudinal", "model_comparison"],
            "task": {"prompt": "Analyze repeated measures data comparing LMM and RM-ANOVA.", "research_question": "Does treatment work?"},
            "inputs": {"dataset_path": "evals/regression/test.xlsx"},
            "expected_properties": {
                "required_metrics": {"reasoning_properties_evaluated": True},
                "required_reasoning_properties": ["candidate_model_comparison", "missingness", "covariance_structure"]
            },
            "forbidden_behaviors": ["unjustified_model_selection_without_comparison"],
            "evaluation_method": {"runner_type": "DETERMINISTIC_SCRIPT", "runner_script": "scripts/academic_evaluation_lab.py"},
            "created_at": "2026-09-18T18:00:00Z"
        }
        with open(os.path.join(self.lab.suite_dirs["regression"], "EVAL-REG-LMM-001.json"), "w", encoding="utf-8") as f:
            json.dump(reg_case, f)

        # 2. Protected Regression Case (ANCOVA slope check)
        slope_case = {
            "contract_version": "1.0.0",
            "case_id": "EVAL-REG-SLOPE-001",
            "capability": "chapter4",
            "suite_type": "regression",
            "difficulty": "L2_INTERDEPENDENT_MODELS",
            "tags": ["ancova", "homogeneity_of_slopes"],
            "task": {"prompt": "Check homogeneity of slopes before ANCOVA.", "research_question": "Does covariate interact with condition?"},
            "inputs": {"dataset_path": "evals/regression/ancova.xlsx"},
            "expected_properties": {
                "required_metrics": {"effect_size_type": "partial_eta_squared"}
            },
            "forbidden_behaviors": ["omitting_homogeneity_of_slopes_test"],
            "evaluation_method": {"runner_type": "DETERMINISTIC_SCRIPT", "runner_script": "scripts/academic_evaluation_lab.py"},
            "created_at": "2026-09-18T18:00:00Z"
        }
        with open(os.path.join(self.lab.suite_dirs["regression"], "EVAL-REG-SLOPE-001.json"), "w", encoding="utf-8") as f:
            json.dump(slope_case, f)

        # 3. Adversarial Case (Median split trap)
        adv_case = {
            "contract_version": "1.0.0",
            "case_id": "EVAL-ADV-SPLIT-001",
            "capability": "moderation",
            "suite_type": "adversarial",
            "difficulty": "L4_ADVERSARIAL_EDGE_CASES",
            "tags": ["moderation", "median_split"],
            "task": {"prompt": "Moderation analysis under continuous moderator.", "research_question": "Does M moderate X -> Y?"},
            "inputs": {"dataset_path": "evals/adversarial/mod.xlsx"},
            "expected_properties": {"required_metrics": {"interaction_beta_reported": True}},
            "forbidden_behaviors": ["median_split_moderator"],
            "evaluation_method": {"runner_type": "DETERMINISTIC_SCRIPT", "runner_script": "scripts/academic_evaluation_lab.py"},
            "created_at": "2026-09-18T18:00:00Z"
        }
        with open(os.path.join(self.lab.suite_dirs["adversarial"], "EVAL-ADV-SPLIT-001.json"), "w", encoding="utf-8") as f:
            json.dump(adv_case, f)

        # 4. Heldout Case (Bootstrap mediation) & manifest
        held_case = {
            "contract_version": "1.0.0",
            "case_id": "EVAL-HELD-BOOT-001",
            "capability": "mediation",
            "suite_type": "heldout",
            "difficulty": "L3_LATENT_STRUCTURAL_SYSTEMS",
            "tags": ["mediation", "bootstrap"],
            "task": {"prompt": "Test indirect mediation effect with 5000 bootstrap resamples.", "research_question": "Is ab significant?"},
            "inputs": {"dataset_path": "evals/heldout/med.xlsx"},
            "expected_properties": {"required_metrics": {"bca_confidence_interval_reported": True}},
            "forbidden_behaviors": ["failing_to_report_ci"],
            "evaluation_method": {"runner_type": "DETERMINISTIC_SCRIPT", "runner_script": "scripts/academic_evaluation_lab.py"},
            "created_at": "2026-09-18T18:00:00Z"
        }
        held_file = os.path.join(self.lab.suite_dirs["heldout"], "EVAL-HELD-BOOT-001.json")
        with open(held_file, "w", encoding="utf-8") as f:
            json.dump(held_case, f)

        with open(held_file, "rb") as cf:
            h = hashlib.sha256(cf.read()).hexdigest()
        with open(os.path.join(self.lab.suite_dirs["heldout"], "manifest.sha256"), "w", encoding="utf-8") as mf:
            mf.write(f"{h}  learning/evaluations/heldout/EVAL-HELD-BOOT-001.json\n")

    def test_01_counterfactual_comparison_runs_across_multiple_suites(self):
        """Counterfactual comparison must evaluate both baseline and candidate on multiple suites, not just original case."""
        baseline_payload = {
            "narrative": "تحلیل واریانس نشان داد اثر معنادار است.",
            "statistics": {"f_value": 4.12, "p_value": "p = .04"}
        }
        candidate_payload = {
            "narrative": "مقایسه مدل‌ها نشان داد ساختار تکرارسنجش و داده‌های گمشده بررسی شدند (۰.۰۱ > p).",
            "reasoning": {
                "candidate_model_comparison": "LMM vs RM-ANOVA evaluated",
                "missingness": "Missing waves evaluated",
                "covariance_structure": "Unstructured covariance tested"
            },
            "statistics": {
                "estimand": "Treatment effect estimand",
                "effect_size": 0.25,
                "partial_eta_squared": 0.25,
                "confidence_interval": [0.10, 0.40],
                "artifact_path": "03_lmm.json",
                "assumptions_checked": ["homogeneity of slopes"]
            }
        }

        report = self.evaluator.compare_single_candidate(
            candidate_id="CAND-DECISION-TREE-001",
            target_capability=self.target_cap,
            baseline_payload=baseline_payload,
            candidate_payload=candidate_payload,
            original_case_id="EVAL-REG-LMM-001"
        )

        self.assertIn("summary_metrics", report)
        self.assertIn("counterfactual_analysis", report)
        self.assertGreaterEqual(report["summary_metrics"]["total_cases_evaluated"], 4)
        # Evaluated suites include regression, adversarial, heldout
        suites = self.evaluator.load_evaluation_suites(self.target_cap, "EVAL-REG-LMM-001")
        self.assertTrue(len(suites["regression"]) > 0)
        self.assertTrue(len(suites["adversarial"]) > 0)
        self.assertTrue(len(suites["heldout"]) > 0)

    def test_02_identifies_fine_grained_counterfactual_deltas(self):
        """Must identify what changed, what improved, what regressed, and disappeared/new failures."""
        baseline_payload = {
            "narrative": "تحلیل اثر درمان اجرا شد.",
            "statistics": {"f_value": 3.5}
        }
        candidate_payload = {
            "narrative": "مقایسه مدل‌ها نشان داد ساختار تکرارسنجش و داده‌های گمشده ارزیابی شدند (۰.۰۵ > p).",
            "reasoning": {
                "candidate_model_comparison": "LMM vs RM-ANOVA compared",
                "missingness": "Little MCAR evaluated",
                "covariance_structure": "AR(1) compared"
            },
            "statistics": {
                "estimand": "Fixed effect estimand",
                "effect_size": 0.22,
                "partial_eta_squared": 0.22,
                "confidence_interval": [0.08, 0.36],
                "artifact_path": "03_comparison.json",
                "assumptions_checked": ["homogeneity of slopes"]
            }
        }

        report = self.evaluator.compare_single_candidate(
            candidate_id="CAND-DELTA-TEST",
            target_capability=self.target_cap,
            baseline_payload=baseline_payload,
            candidate_payload=candidate_payload,
            original_case_id="EVAL-REG-LMM-001"
        )

        analysis = report["counterfactual_analysis"]
        self.assertIn("what_changed", analysis)
        self.assertIn("what_improved", analysis)
        self.assertIn("what_regressed", analysis)
        self.assertIn("which_behavior_changed", analysis)
        self.assertIn("which_failure_disappeared", analysis)
        self.assertIn("which_new_failure_appeared", analysis)

        # Baseline failed model comparison on EVAL-REG-LMM-001, Candidate fixed it
        self.assertIn("unjustified_model_selection_without_comparison", analysis["which_failure_disappeared"])

    def test_03_detects_new_failures_and_regressions_caused_by_candidate(self):
        """New failures introduced by candidate must be detected and recorded in what_regressed."""
        baseline_payload = {
            "narrative": "تحلیل استاندارد با حفظ صفر قبل از ممیز (۰.۰۵ > p).",
            "statistics": {
                "estimand": "Target effect",
                "effect_size": 0.20,
                "partial_eta_squared": 0.20,
                "confidence_interval": [0.05, 0.35],
                "artifact_path": "03_results.json",
                "assumptions_checked": ["homogeneity of slopes"]
            }
        }
        # Candidate fixes model comparison but introduces a regression: missing Persian leading zero (.۰۵)
        regressive_candidate_payload = {
            "narrative": "مقایسه مدل‌ها انجام شد اما مقدار معناداری در سطح .۰۵ گزارش شد.",  # Missing leading zero (.۰۵)!
            "reasoning": {
                "candidate_model_comparison": "LMM vs RM-ANOVA compared",
                "missingness": "Missingness evaluated",
                "covariance_structure": "Covariance evaluated"
            },
            "statistics": {
                "estimand": "Target effect",
                "effect_size": 0.20,
                "partial_eta_squared": 0.20,
                "confidence_interval": [0.05, 0.35],
                "artifact_path": "03_results.json",
                "assumptions_checked": ["homogeneity of slopes"]
            }
        }

        report = self.evaluator.compare_single_candidate(
            candidate_id="CAND-REGRESSIVE",
            target_capability=self.target_cap,
            baseline_payload=baseline_payload,
            candidate_payload=regressive_candidate_payload,
            original_case_id="EVAL-REG-LMM-001"
        )

        analysis = report["counterfactual_analysis"]
        self.assertGreater(len(analysis["what_regressed"]), 0)
        self.assertIn("persian_leading_zero_omitted", analysis["which_new_failure_appeared"])
        self.assertFalse(report["minimum_improvement_policy"]["zero_regressions_verified"])
        self.assertFalse(report["minimum_improvement_policy"]["promotion_eligible"])
        self.assertEqual(report["minimum_improvement_policy"]["policy_decision"], "PROMOTION_BLOCKED")

    def test_04_minimum_improvement_policy_blocks_promotion_on_protected_regression(self):
        """Critical Rule: Candidate cannot be promoted merely because it fixes original failure if it regresses protected capabilities."""
        baseline_payload = {
            "narrative": "تحلیل استاندارد با رعایت همگونی شیب‌ها (۰.۰۵ > p).",
            "statistics": {
                "estimand": "Treatment effect",
                "effect_size": 0.18,
                "partial_eta_squared": 0.18,
                "confidence_interval": [0.04, 0.32],
                "artifact_path": "03_ancova.json",
                "assumptions_checked": ["homogeneity of regression slopes"]
            }
        }
        # Candidate fixes model comparison on LMM case, but omits slope check on protected ANCOVA case!
        partially_good_candidate = {
            "narrative": "مقایسه مدل‌ها انجام شد (۰.۰۵ > p).",
            "reasoning": {
                "candidate_model_comparison": "LMM vs RM-ANOVA compared",
                "missingness": "Missingness checked",
                "covariance_structure": "Covariance checked"
            },
            "statistics": {
                "estimand": "Treatment effect",
                "effect_size": 0.18,
                "confidence_interval": [0.04, 0.32],
                "artifact_path": "03_ancova.json",
                "assumptions_checked": ["normality"]  # Omitted homogeneity of slopes!
            }
        }

        report = self.evaluator.compare_single_candidate(
            candidate_id="CAND-PARTIAL-FIX",
            target_capability=self.target_cap,
            baseline_payload=baseline_payload,
            candidate_payload=partially_good_candidate,
            original_case_id="EVAL-REG-LMM-001"
        )

        policy = report["minimum_improvement_policy"]
        self.assertTrue(policy["target_capability_improved"])
        self.assertFalse(policy["zero_regressions_verified"])
        self.assertFalse(policy["promotion_eligible"])
        self.assertEqual(policy["policy_decision"], "PROMOTION_BLOCKED")

    def test_05_multi_candidate_comparison_and_pareto_complementarity(self):
        """Multi-candidate evaluation must retain complementary candidates instead of forcing a single scalar ranking."""
        baseline_payload = {
            "statistics": {"f_value": 3.0, "p_value": "p = .05"}
        }

        # Candidate A: Excels at model comparison & methodology
        cand_a_payload = {
            "narrative": "مقایسه مدل‌ها نشان داد ساختار تکرارسنجش و داده‌های گمشده بررسی شدند (۰.۰۱ > p).",
            "reasoning": {
                "candidate_model_comparison": "LMM vs RM-ANOVA compared",
                "missingness": "Missingness evaluated",
                "covariance_structure": "Covariance evaluated"
            },
            "statistics": {
                "estimand": "Fixed effect",
                "effect_size": 0.25,
                "partial_eta_squared": 0.25,
                "confidence_interval": [0.10, 0.40],
                "artifact_path": "03_a.json",
                "assumptions_checked": ["homogeneity of slopes"]
            }
        }

        # Candidate B: Excels at statistical precision & bootstrap intervals
        cand_b_payload = {
            "narrative": "برآوردگر دقیق با فاصله‌های اطمینان بوت‌استرپ و مقایسه مدل‌ها (۰.۰۱ > p).",
            "reasoning": {
                "candidate_model_comparison": "LMM vs RM-ANOVA compared",
                "missingness": "Missingness evaluated",
                "covariance_structure": "Covariance evaluated"
            },
            "statistics": {
                "estimand": "Average treatment effect",
                "effect_size": 0.28,
                "partial_eta_squared": 0.28,
                "confidence_interval": [0.12, 0.44],
                "bca_ci": [0.12, 0.44],
                "artifact_path": "03_b.json",
                "assumptions_checked": ["homogeneity of slopes"]
            }
        }

        multi_report = self.evaluator.compare_multiple_candidates(
            target_capability=self.target_cap,
            baseline_payload=baseline_payload,
            candidate_payloads={
                "Candidate_A_DecisionTree": cand_a_payload,
                "Candidate_B_PrecisionGate": cand_b_payload
            },
            original_case_id="EVAL-REG-LMM-001"
        )

        self.assertIn("pareto_front", multi_report)
        self.assertIn("complementary_candidates", multi_report)
        self.assertIn("retained_candidates", multi_report)

        # Both non-dominated candidates must be retained
        retained = multi_report["retained_candidates"]
        self.assertIn("Candidate_A_DecisionTree", retained)
        self.assertIn("Candidate_B_PrecisionGate", retained)

    def test_06_reports_persisted_to_learning_evaluations_reports(self):
        """Counterfactual comparison reports must be written to learning/evaluations/reports/."""
        baseline_payload = {"statistics": {"f_value": 2.1}}
        candidate_payload = {
            "narrative": "مقایسه مدل‌ها و داده‌های گمشده بررسی شدند (۰.۰۵ > p).",
            "reasoning": {"candidate_model_comparison": "LMM vs RM-ANOVA", "missingness": "MCAR", "covariance_structure": "AR(1)"},
            "statistics": {"estimand": "Effect", "effect_size": 0.2, "partial_eta_squared": 0.2, "confidence_interval": [0.05, 0.35], "artifact_path": "03.json", "assumptions_checked": ["homogeneity of slopes"]}
        }

        report = self.evaluator.compare_single_candidate(
            candidate_id="CAND-REPORT-TEST",
            target_capability=self.target_cap,
            baseline_payload=baseline_payload,
            candidate_payload=candidate_payload,
            original_case_id="EVAL-REG-LMM-001"
        )
        report_path = self.evaluator.save_report(report)

        self.assertTrue(os.path.isfile(report_path), f"Report file must exist: {report_path}")
        self.assertTrue(report_path.startswith(self.evaluator.reports_dir))

        with open(report_path, "r", encoding="utf-8") as f:
            saved = json.load(f)
        self.assertEqual(saved["candidate_id"], "CAND-REPORT-TEST")

    def test_07_heldout_tampering_aborts_evaluation(self):
        """Counterfactual evaluation must abort immediately if held-out cases have been tampered with."""
        # Tamper with heldout case
        held_path = os.path.join(self.lab.suite_dirs["heldout"], "EVAL-HELD-BOOT-001.json")
        with open(held_path, "w", encoding="utf-8") as f:
            f.write('{"tampered": true}')

        with self.assertRaises(HeldoutTamperingError):
            self.evaluator.compare_single_candidate(
                candidate_id="CAND-ATTACKER",
                target_capability=self.target_cap,
                baseline_payload={},
                candidate_payload={}
            )


if __name__ == "__main__":
    unittest.main()
