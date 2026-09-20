#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_three_suites_evaluation_phase24.py — Test Suite for Phase 24

Verifies:
1. Candidate Generator synthesizes conditional decision rules (WHEN X -> A, WHEN Y -> B, EXCEPT Z -> C)
   and strictly prohibits naive universal blanket instructions (UniversalInstructionProhibitedError).
2. Independent Evaluator assembles a standardized 3-category panel:
   - Regression: "Does it fix the original mistake?"
   - Adversarial: "Can the candidate create a new mistake?"
   - Held-out: "Does the lesson generalize to a different case?"
3. A naive candidate learning "Always use ANCOVA" passes regression but FAILS both adversarial
   (slope homogeneity violation) and held-out (3-group longitudinal trial) suites.
4. A candidate with conditional decision rules passes all 3 suites and receives PASS / PROMOTE.
5. Held-out cryptographic manifest integrity is verified.
6. Promotion engine gates fail closed if any of the three categories fail or universal instructions are used.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.academic_candidate_generator import (
    AcademicCandidateGenerator,
    UniversalInstructionProhibitedError,
    CandidateGenerationError
)
from scripts.academic_independent_evaluator import (
    AcademicIndependentEvaluator,
    SelfEvaluationBlockedError
)
from scripts.academic_evaluation_lab import AcademicEvaluationLab
from scripts.academic_promotion_engine import AcademicPromotionEngine
from contracts.contract_validator import validate_independent_evaluation


class TestThreeSuitesEvaluationPhase24(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.lab = AcademicEvaluationLab(base_dir=ROOT_DIR)
        self.evaluator = AcademicIndependentEvaluator(base_dir=ROOT_DIR)
        self.generator = AcademicCandidateGenerator(base_dir=self.temp_dir)
        self.promotion_engine = AcademicPromotionEngine(base_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_conditional_rule_synthesis_enforces_when_except(self):
        """1. Candidate generator synthesizes WHEN/EXCEPT rules and prohibits universal blanket instructions."""
        reflection = {
            "root_cause": "Applied ANCOVA blindly without checking homogeneity of slopes.",
            "failure_mechanism": "VIOLATED_ASSUMPTION_IGNORED",
            "prescribed_behavior": "Verify slope homogeneity and branch to RM-ANOVA on change scores if violated.",
            "diagnosed_gap": "Missing conditional model selection rules."
        }

        # Verify DECISION_TREE_ADDITION produces WHEN / EXCEPT structure
        modified, rationale, benefit, downside, hyp = self.generator._build_mutation_content(
            mut_type="DECISION_TREE_ADDITION",
            target_skill="statistical-data-analyst",
            current_skill_content="# Statistical Analyst\n",
            reflection=reflection
        )

        self.assertIn("WHEN condition X", modified)
        self.assertIn("WHEN condition Y", modified)
        self.assertIn("EXCEPT condition Z", modified)
        self.assertIn("Prohibit universal blanket instructions", modified)

        # Verify that attempting a universal instruction raises UniversalInstructionProhibitedError
        bad_instruction = (
            "# Bad Skill\n"
            "## Procedure\n"
            "Always use ANCOVA for any pre-post data regardless of assumptions.\n"
        )
        with self.assertRaises(UniversalInstructionProhibitedError) as ctx:
            self.generator._verify_conditional_rule_structure(bad_instruction)
        self.assertIn("Always use", str(ctx.exception))

    def test_three_categories_panel_assembly(self):
        """2. Independent Evaluator assembles the standardized 3-category panel."""
        panel = self.evaluator.build_task_panel(
            capability="statistical-data-analyst",
            failure_signature="VIOLATED_ASSUMPTION_IGNORED"
        )

        self.assertEqual(len(panel), 3)

        # Task 1: Regression
        task_reg = panel[0]
        self.assertEqual(task_reg["category"], "regression")
        self.assertIn("Does it fix the original mistake?", task_reg["description"])

        # Task 2: Adversarial
        task_adv = panel[1]
        self.assertEqual(task_adv["category"], "adversarial")
        self.assertIn("Can the candidate create a new mistake?", task_adv["description"])

        # Task 3: Held-out
        task_held = panel[2]
        self.assertEqual(task_held["category"], "heldout")
        self.assertIn("Does the lesson generalize to a different case?", task_held["description"])

    def test_naive_universal_instruction_fails_adversarial_and_heldout(self):
        """3. Candidate learning 'Always use ANCOVA' fails adversarial and held-out suites."""
        panel = self.evaluator.build_task_panel(
            capability="statistical-data-analyst",
            failure_signature="VIOLATED_ASSUMPTION_IGNORED"
        )

        # Baseline: Fails regression (reported p = .000 or ignored slopes),
        # but passes or fails baseline checks
        baseline_outputs = {
            "TASK-REG": {
                "statistics": {"f_value": 4.12, "p_raw": "p = .000"},
                "narrative": "ANCOVA was conducted without checking slope homogeneity (p = .000)."
            },
            "TASK-ADV": {
                "reasoning": {"candidate_model_comparison": "Evaluated candidate models"},
                "statistics": {"slope_homogeneity_tested": True, "f_value": 2.15, "p_value": 0.14},
                "narrative": "Slope homogeneity was checked (۰.۱۴ = p)."
            },
            "TASK-HELD": {
                "reasoning": {
                    "repeated_measures_structure": "Within-subject 4 waves",
                    "missingness": "Little's MCAR missingness evaluated",
                    "candidate_model_comparison": "LMM compared to RM-ANOVA"
                },
                "statistics": {"lmm_random_intercept_estimated": True},
                "narrative": "Linear mixed model with random intercept was fitted (۰.۰۱ > p)."
            }
        }

        # Naive Candidate: learned "Always use ANCOVA"
        candidate_outputs = {
            "TASK-REG": {
                # Fixes regression task: reports proper p-value and applies ANCOVA on 2-wave balanced data
                "reasoning": {
                    "candidate_model_comparison": "ANCOVA selected for 2-wave pre-post",
                    "slope_homogeneity_verification": "Homogeneity of slopes verified",
                    "homogeneity_of_slopes": "Homogeneity of regression slopes verified",
                    "covariate_measurement_error": "Covariate measurement error verified and reliable",
                    "linear_relationship": "Linear relationship verified between baseline and post-test",
                    "estimand": "Average treatment effect on post-burnout controlling for baseline"
                },
                "statistics": {
                    "estimand": "Average treatment effect on post-burnout controlling for baseline",
                    "f_value": 4.12,
                    "effect_size": 0.18,
                    "partial_eta_squared": 0.18,
                    "assumptions_checked": ["homogeneity of regression slopes", "normality", "levene"],
                    "artifact_path": "03_parametric_assumptions.json"
                },
                "narrative": "تحلیل کوواریانس برای پیش‌آزمون و پس‌آزمون انجام شد (F = 4.12, ۰.۰۱ > p)."
            },
            "TASK-ADV": {
                # FAILS adversarial: slope homogeneity is violated (F=8.42, p=.004), but candidate says "Always use ANCOVA"
                "reasoning": {
                    "candidate_model_comparison": "Always use ANCOVA regardless of slopes",
                    "model_decision": "Always use ANCOVA"
                },
                "statistics": {
                    "estimand": "Treatment effect",
                    "f_value": 8.42,
                    "model_used": "ancova",
                    "artifact_path": "assumption_testing.json"
                },
                "narrative": "Because the rule is to always use ANCOVA, standard ANCOVA was used despite slope heterogeneity."
            },
            "TASK-HELD": {
                # FAILS held-out: 3-group 4-wave longitudinal trial with attrition, but candidate applies ANCOVA
                "reasoning": {
                    "candidate_model_comparison": "Always use ANCOVA for any group comparison",
                    "model_decision": "Always use ANCOVA"
                },
                "statistics": {
                    "estimand": "Treatment effect",
                    "model_used": "ancova",
                    "artifact_path": "lmm_longitudinal_results.json"
                },
                "narrative": "Always use ANCOVA was applied to the 4-wave longitudinal data with attrition."
            }
        }

        report = self.evaluator.execute_independent_evaluation(
            candidate_id="CAND-NAIVE-ANCOVA",
            baseline_version="V1",
            capability="statistical-data-analyst",
            baseline_outputs=baseline_outputs,
            candidate_outputs=candidate_outputs,
            task_panel=panel
        )

        unblinded = report["unblinded_comparison"]

        # Regression: Candidate passed (fixed original defect)
        self.assertTrue(unblinded["regression_result"]["fixes_original_mistake"])
        self.assertEqual(unblinded["regression_result"]["verdict"], "PASS")

        # Adversarial: Candidate FAILED (created new mistake under slope violation)
        self.assertTrue(unblinded["adversarial_result"]["creates_new_mistake"])
        self.assertEqual(unblinded["adversarial_result"]["verdict"], "FAIL")

        # Held-out: Candidate FAILED (failed to generalize to 3-group longitudinal trial)
        self.assertFalse(unblinded["heldout_result"]["generalizes_to_different_case"])
        self.assertEqual(unblinded["heldout_result"]["verdict"], "FAIL")

        # Conditional rule verification: FAILED
        self.assertFalse(unblinded["conditional_rule_verified"])

        # Overall verdict: FAIL, recommendation: REJECT
        self.assertEqual(unblinded["independent_verdict"], "FAIL")
        self.assertEqual(unblinded["recommendation"], "REJECT")

    def test_conditional_rule_passes_all_three_categories(self):
        """4. Candidate with conditional decision rules passes Regression, Adversarial, and Held-out suites."""
        panel = self.evaluator.build_task_panel(
            capability="statistical-data-analyst",
            failure_signature="VIOLATED_ASSUMPTION_IGNORED"
        )

        baseline_outputs = {
            "TASK-REG": {
                "statistics": {"f_value": 4.12, "p_raw": "p = .000"},
                "narrative": "Standard ANCOVA without checking slopes (p = .000)."
            },
            "TASK-ADV": {
                "statistics": {"f_value": 2.15},
                "narrative": "Adversarial test output."
            },
            "TASK-HELD": {
                "statistics": {"f_value": 3.10},
                "narrative": "Held-out test output."
            }
        }

        # Robust Candidate with conditional decision rules:
        # WHEN X (2-wave balanced) -> ANCOVA
        # WHEN Y (multi-wave/attrition) -> LMM
        # EXCEPT Z (slope violation) -> RM-ANOVA on change scores
        candidate_outputs = {
            "TASK-REG": {
                "reasoning": {
                    "candidate_model_comparison": "WHEN 2-wave pre-post balanced design -> use ANCOVA controlling for baseline",
                    "slope_homogeneity_verification": "Homogeneity of regression slopes verified",
                    "homogeneity_of_slopes": "Homogeneity of regression slopes verified",
                    "covariate_measurement_error": "Covariate measurement error verified and reliable",
                    "linear_relationship": "Linear relationship verified between baseline and post-test",
                    "estimand": "Average treatment effect on post-burnout controlling for baseline"
                },
                "statistics": {
                    "estimand": "Average treatment effect on post-burnout controlling for baseline",
                    "f_value": 4.12,
                    "effect_size": 0.18,
                    "partial_eta_squared": 0.18,
                    "assumptions_checked": ["homogeneity of regression slopes", "normality", "levene"],
                    "artifact_path": "03_parametric_assumptions.json"
                },
                "narrative": "تحلیل کوواریانس برای داده‌های پیش‌آزمون-پس‌آزمون دو مرحله‌ای اجرا شد (F = 4.12, ۰.۰۱ > p)."
            },
            "TASK-ADV": {
                "reasoning": {
                    "candidate_model_comparison": "EXCEPT when slope homogeneity is violated (F = 8.42, p = .004) -> branch to RM-ANOVA on change scores",
                    "slope_homogeneity_verification": "Homogeneity of slopes was formally tested and violated",
                    "conditional_branching_on_violation": "Switched to repeated-measures ANOVA on change scores"
                },
                "statistics": {
                    "estimand": "Treatment effect under heterogeneous slopes",
                    "slope_homogeneity_tested": True,
                    "standard_ancova_rejected_on_violation": True,
                    "alternative_approach_selected": True,
                    "artifact_path": "assumption_testing.json",
                    "f_value": 8.42
                },
                "narrative": "با توجه به نقض همگونی شیب‌های رگرسیون (F = 8.42)، به جای آنکووا از تحلیل واریانس با اندازه‌گیری‌های مکرر بر روی نمرات تغییر استفاده شد (۰.۰۱ > p)."
            },
            "TASK-HELD": {
                "reasoning": {
                    "repeated_measures_structure": "4 measurement waves with within-subject correlation",
                    "missingness": "18% attrition handled under MAR assumption",
                    "candidate_model_comparison": "WHEN 3 groups and 4 waves with attrition -> use Linear Mixed Models (LMM)"
                },
                "statistics": {
                    "estimand": "Rate of change across 4 waves in 3 groups",
                    "lmm_random_intercept_estimated": True,
                    "group_by_time_interaction_reported": True,
                    "missingness_mechanism_evaluated": True,
                    "artifact_path": "lmm_longitudinal_results.json"
                },
                "narrative": "برای تحلیل داده‌های طولی ۴ مرحله‌ای با افت آزمودنی‌ها، مدل خطی آمیخته (LMM) با عرض از مبدأ تصادفی برازش شد (۰.۰۰۱ > p)."
            }
        }


        report = self.evaluator.execute_independent_evaluation(
            candidate_id="CAND-CONDITIONAL-RULES",
            baseline_version="V1",
            capability="statistical-data-analyst",
            baseline_outputs=baseline_outputs,
            candidate_outputs=candidate_outputs,
            task_panel=panel
        )

        unblinded = report["unblinded_comparison"]

        # All 3 suites passed!
        self.assertTrue(unblinded["regression_result"]["fixes_original_mistake"])
        self.assertEqual(unblinded["regression_result"]["verdict"], "PASS")

        self.assertFalse(unblinded["adversarial_result"]["creates_new_mistake"])
        self.assertEqual(unblinded["adversarial_result"]["verdict"], "PASS")

        self.assertTrue(unblinded["heldout_result"]["generalizes_to_different_case"])
        self.assertEqual(unblinded["heldout_result"]["verdict"], "PASS")

        self.assertTrue(unblinded["conditional_rule_verified"])
        self.assertEqual(unblinded["independent_verdict"], "PASS")
        self.assertEqual(unblinded["recommendation"], "PROMOTE")

        # Verify report satisfies schema contract
        val = validate_independent_evaluation(report)
        self.assertTrue(val["valid"], f"Schema validation failed: {val.get('errors')}")

    def test_heldout_cryptographic_integrity_verified(self):
        """5. Held-out suite cryptographic manifest integrity is verified."""
        valid, errors = self.lab.verify_heldout_integrity()
        self.assertTrue(valid, f"Held-out integrity check failed: {errors}")
        self.assertEqual(len(errors), 0)

    def test_promotion_blocks_candidate_failing_any_of_three_suites(self):
        """6. Promotion engine gates block candidates failing any of the 3 suites or using universal rules."""
        # Simulated evaluation report with failing adversarial suite
        failing_adversarial_report = {
            "summary_metrics": {
                "total_cases_evaluated": 3,
                "target_capability_improved": True,
                "zero_regressions_verified": True,
                "adversarial_clearance": False,  # Red-team failed
                "suite_pass_rates": {"regression": 1.0, "adversarial": 0.0, "heldout": 1.0}
            },
            "minimum_improvement_policy": {
                "target_capability_improved": True,
                "zero_regressions_verified": True,
                "adversarial_clearance": False
            },
            "counterfactual_analysis": {
                "what_improved": ["Fixed ANCOVA reporting"],
                "what_regressed": []
            },
            "independent_evaluation": {
                "unblinded_comparison": {
                    "independent_verdict": "FAIL",
                    "defect_resolved": True,
                    "zero_regressions_verified": True,
                    "regression_result": {"verdict": "PASS", "fixes_original_mistake": True, "task_id": "TASK-REG"},
                    "adversarial_result": {"verdict": "FAIL", "creates_new_mistake": True, "task_id": "TASK-ADV"},
                    "heldout_result": {"verdict": "PASS", "generalizes_to_different_case": True, "task_id": "TASK-HELD"},
                    "conditional_rule_verified": False
                }
            }
        }

        gate_check = self.promotion_engine.verify_evaluation_gates(failing_adversarial_report)
        self.assertFalse(gate_check["all_passed"])
        self.assertFalse(gate_check["gate_results"]["adversarial_checks"]["passed"])
        self.assertFalse(gate_check["gate_results"]["independent_evaluation"]["passed"])
        self.assertTrue(any("Adversarial suite failed" in f for f in gate_check["failures"]))
        self.assertTrue(any("UNIVERSAL_INSTRUCTION_PROHIBITED" in f for f in gate_check["failures"]))


if __name__ == "__main__":
    unittest.main()
