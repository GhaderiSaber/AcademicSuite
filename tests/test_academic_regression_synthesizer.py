#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_regression_synthesizer.py — Unit Tests for Correction -> Lesson -> Regression Test Pipeline

Verifies:
1. Meaningful reusable user corrections automatically generate candidate regression cases.
2. Candidate regression cases test correct reasoning properties (repeated-measures structure,
   missingness, imbalance, covariance structure, estimand, candidate model comparison)
   without hard-coding a single answer.
3. Originating lesson, experience, capability, expected behavior, and forbidden behaviors are referenced.
4. Deterministic evaluation laboratory correctly fails flawed baselines and passes compliant candidates.
5. Validation gate promotes status from 'candidate' to permanent 'validated' regression asset.
6. Repeated mistakes accumulate into an institutionalized, growing regression suite (repeat_count incremented).
7. Old mistakes remain testable forever: regression cases are never deleted merely because they pass,
   and retirement requires explicit justification while preserving files on disk.
8. Scope containment: project-specific corrections are blocked from polluting global regression suites.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.contract_validator import (
    validate_evaluation_case,
    validate_feedback,
    validate_lesson
)
from scripts.academic_regression_synthesizer import (
    AcademicRegressionSynthesizer,
    RegressionSynthesisError
)
from scripts.academic_evaluation_lab import AcademicEvaluationLab


class TestAcademicRegressionSynthesizer(unittest.TestCase):
    """Authoritative test suite for the Correction -> Lesson -> Regression Test pipeline."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_regression_test_")
        self.synthesizer = AcademicRegressionSynthesizer(base_dir=self.temp_dir)
        self.lab = AcademicEvaluationLab(base_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_user_correction_produces_candidate_regression_case(self):
        """User correction 'You should have compared LMM with repeated-measures ANOVA' generates a candidate case."""
        feedback = {
            "feedback_id": "FDB-20260918-LMM-001",
            "type": "METHODOLOGY_CORRECTION",
            "scope": "REUSABLE_PROCEDURAL",
            "severity": "HIGH",
            "correction": "You should have compared LMM with repeated-measures ANOVA.",
            "desired_behavior": "Before selecting a longitudinal model, compare LMM against RM-ANOVA.",
            "target_agent": "statistics-agent",
            "target_skill": "statistical-data-analyst",
            "context": {"experience_id": "EXP-20260918-LONGITUDINAL"}
        }
        lesson = {
            "lesson_id": "LSN-20260918-LMM-001",
            "scope": "DOMAIN_WIDE",
            "is_what_not_to_do": True,
            "target_capability": "statistical-data-analyst",
            "what_happened": "Repeated-measures ANOVA was used despite missing waves across timepoints.",
            "what_behavior_caused_outcome": "Selected RM-ANOVA blindly without comparing against LMM.",
            "what_should_have_happened": "Evaluate repeated-measures structure, missingness, imbalance, covariance structure, and estimand."
        }

        case = self.synthesizer.synthesize_from_correction_and_lesson(feedback, lesson)
        self.assertIsNotNone(case)

        # 1. Contract validation
        val_res = validate_evaluation_case(case)
        self.assertTrue(val_res["valid"], f"Synthesized case failed contract validation: {val_res.get('errors')}")

        # 2. Originating references
        self.assertEqual(case["originating_lesson_id"], "LSN-20260918-LMM-001")
        self.assertEqual(case["originating_feedback_id"], "FDB-20260918-LMM-001")
        self.assertEqual(case["originating_experience_id"], "EXP-20260918-LONGITUDINAL")
        self.assertEqual(case["capability"], "statistical-data-analyst")
        self.assertIn("expected_behavior", case)
        self.assertIn("forbidden_behavior", case)

        # 3. Initial lifecycle status
        self.assertEqual(case["status"], "candidate")
        self.assertEqual(case["repeat_count"], 1)

        # 4. Stored on disk under learning/evaluations/regression/
        case_path = os.path.join(self.synthesizer.regression_dir, f"{case['case_id']}.json")
        self.assertTrue(os.path.isfile(case_path), "Case must be saved to disk under learning/evaluations/regression/")

    def test_02_regression_case_tests_reasoning_properties_without_hardcoded_answer(self):
        """The regression case must test all 6 reasoning properties without hard-coding one model answer."""
        feedback = {
            "feedback_id": "FDB-20260918-LMM-002",
            "type": "METHODOLOGY_CORRECTION",
            "scope": "REUSABLE_PROCEDURAL",
            "severity": "HIGH",
            "correction": "You should have compared LMM with repeated-measures ANOVA.",
            "desired_behavior": "Explicitly evaluate candidate models against data structure.",
            "target_agent": "statistics-agent",
            "target_skill": "statistical-data-analyst"
        }
        lesson = {
            "lesson_id": "LSN-20260918-LMM-002",
            "scope": "DOMAIN_WIDE",
            "is_what_not_to_do": True,
            "target_capability": "statistical-data-analyst",
            "what_happened": "Unjustified model selection without comparison.",
            "what_behavior_caused_outcome": "Omitted candidate model comparison.",
            "what_should_have_happened": "Compare LMM vs RM-ANOVA against missingness, imbalance, covariance structure, and estimand."
        }

        case = self.synthesizer.synthesize_from_correction_and_lesson(feedback, lesson)
        req_props = case["expected_properties"]["required_reasoning_properties"]

        # Verify all 6 reasoning properties from the user prompt are present
        expected_properties = [
            "repeated_measures_structure",
            "missingness",
            "imbalance",
            "covariance_structure",
            "estimand",
            "candidate_model_comparison"
        ]
        for prop in expected_properties:
            self.assertIn(prop, req_props, f"Required reasoning property '{prop}' must be in test specification.")

        # Verify neither model is hard-coded as the only acceptable answer
        task_prompt = case["task"]["prompt"].lower()
        self.assertIn("lmm", task_prompt)
        self.assertIn("rm-anova", task_prompt)
        self.assertNotIn("lmm is the only correct answer", task_prompt)

    def test_03_deterministic_lab_catches_flawed_baseline_and_passes_compliant_candidate(self):
        """Evaluation lab must fail an analysis omitting model comparison and pass an analysis evaluating all properties."""
        feedback = {
            "feedback_id": "FDB-20260918-LMM-003",
            "type": "METHODOLOGY_CORRECTION",
            "scope": "REUSABLE_PROCEDURAL",
            "severity": "HIGH",
            "correction": "You should have compared LMM with repeated-measures ANOVA.",
            "desired_behavior": "Compare LMM against RM-ANOVA.",
            "target_agent": "statistics-agent",
            "target_skill": "statistical-data-analyst"
        }
        lesson = {
            "lesson_id": "LSN-20260918-LMM-003",
            "scope": "DOMAIN_WIDE",
            "is_what_not_to_do": True,
            "target_capability": "statistical-data-analyst",
            "what_happened": "Model selected blindly.",
            "what_behavior_caused_outcome": "Omitted comparison.",
            "what_should_have_happened": "Compare models."
        }
        case = self.synthesizer.synthesize_from_correction_and_lesson(feedback, lesson)

        # 1. Flawed Baseline: Runs RM-ANOVA blindly, ignores missingness and covariance structure
        flawed_output = {
            "narrative": "تحلیل واریانس اندازه‌گیری‌های مکرر انجام شد و اثر زمان معنادار گردید.",
            "statistics": {
                "f_value": 8.12,
                "p_value": "p = .002",
                "estimand": "Main effect of time",
                "effect_size": 0.14,
                "confidence_interval": [0.03, 0.25],
                "artifact_path": "03_rm_anova.json"
            }
        }
        res_flawed = self.lab.evaluate_candidate_on_case("CAND-FLAWED", case, flawed_output)
        self.assertEqual(res_flawed["verdict"], "FAIL")
        failures = [d["failure_type"] for d in res_flawed["diagnostics"]]
        self.assertIn("missing_reasoning_property", failures)
        self.assertIn("unjustified_model_selection_without_comparison", failures)

        # 2. Compliant Candidate: Evaluates all 6 reasoning properties
        compliant_output = {
            "narrative": (
                "به منظور انتخاب مدل بهینه برای ساختار داده‌های تکرارسنجش (repeated measures structure)، "
                "الگوی داده‌های گمشده (missingness) و عدم تعادل بین گروه‌ها (imbalance) بررسی شد. "
                "همچنین ساختار ماتریس کوواریانس (covariance structure) ارزیابی گردید. "
                "مقایسه مدل‌ها (candidate model comparison) میان مدل آمیخته خطی (LMM) و تحلیل واریانس "
                "نشان داد که با توجه به وجود ریزش آزمودنی‌ها در موج سوم، مدل LMM با برآوردگر (estimand) اثر ثابت "
                "مداخله بر خط‌سیر تغییرات فرسودگی برازش بهتری دارد (۰.۰۱ > p)."
            ),
            "reasoning": {
                "repeated_measures_structure": "3 waves within-subject",
                "missingness": "12% attrition at wave 3; Little MCAR chi2=4.12, p=.38",
                "imbalance": "Unequal sample sizes across waves",
                "covariance_structure": "Unstructured covariance matrix evaluated",
                "estimand": "Fixed treatment by time interaction effect",
                "candidate_model_comparison": "LMM vs RM-ANOVA AIC/BIC comparison"
            },
            "statistics": {
                "estimand": "Treatment by time interaction effect",
                "effect_size": 0.24,
                "confidence_interval": [0.08, 0.40],
                "artifact_path": "03_lmm_comparison.json"
            }
        }
        res_compliant = self.lab.evaluate_candidate_on_case("CAND-COMPLIANT", case, compliant_output)
        self.assertEqual(res_compliant["verdict"], "PASS", f"Compliant candidate should pass: {res_compliant['diagnostics']}")

    def test_04_validation_gate_promotes_candidate_to_permanent_regression_asset(self):
        """A candidate case becomes a permanent regression asset only after validation."""
        feedback = {
            "feedback_id": "FDB-20260918-VAL-001",
            "type": "METHODOLOGY_CORRECTION",
            "scope": "REUSABLE_PROCEDURAL",
            "severity": "HIGH",
            "correction": "You should have compared LMM with repeated-measures ANOVA.",
            "desired_behavior": "Compare LMM vs RM-ANOVA.",
            "target_agent": "statistics-agent",
            "target_skill": "statistical-data-analyst"
        }
        lesson = {
            "lesson_id": "LSN-20260918-VAL-001",
            "scope": "DOMAIN_WIDE",
            "is_what_not_to_do": True,
            "target_capability": "statistical-data-analyst",
            "what_happened": "Blind model adoption.",
            "what_behavior_caused_outcome": "Omitted comparison.",
            "what_should_have_happened": "Compare models against data structure."
        }
        case = self.synthesizer.synthesize_from_correction_and_lesson(feedback, lesson)
        self.assertEqual(case["status"], "candidate")

        # Promote via validation gate
        validated_case = self.synthesizer.validate_candidate_case(case["case_id"])
        self.assertEqual(validated_case["status"], "validated")
        self.assertIn("validation_evidence", validated_case)
        self.assertTrue(validated_case["validation_evidence"]["compliant_candidate_passed"])
        self.assertTrue(validated_case["validation_evidence"]["flawed_baseline_detected"])

        # Reload from disk and verify persistence
        loaded = self.synthesizer.load_cases(include_candidates=False)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["case_id"], case["case_id"])
        self.assertEqual(loaded[0]["status"], "validated")

    def test_05_repeated_mistakes_accumulate_into_growing_regression_suite(self):
        """Repeated occurrences of the same failure accumulate by incrementing repeat_count and updating last_seen_at."""
        feedback_1 = {
            "feedback_id": "FDB-20260918-REP-001",
            "type": "METHODOLOGY_CORRECTION",
            "scope": "REUSABLE_PROCEDURAL",
            "severity": "HIGH",
            "correction": "You should have compared LMM with repeated-measures ANOVA.",
            "desired_behavior": "Compare LMM vs RM-ANOVA.",
            "target_agent": "statistics-agent",
            "target_skill": "statistical-data-analyst"
        }
        lesson_1 = {
            "lesson_id": "LSN-20260918-REP-001",
            "scope": "DOMAIN_WIDE",
            "is_what_not_to_do": True,
            "target_capability": "statistical-data-analyst",
            "what_happened": "Blind model adoption.",
            "what_behavior_caused_outcome": "Omitted comparison.",
            "what_should_have_happened": "Compare models."
        }
        case_1 = self.synthesizer.synthesize_from_correction_and_lesson(feedback_1, lesson_1)
        self.assertEqual(case_1["repeat_count"], 1)

        # Later, another correction with the same repeated failure pattern occurs
        feedback_2 = {
            "feedback_id": "FDB-20260918-REP-002",
            "type": "METHODOLOGY_CORRECTION",
            "scope": "REUSABLE_PROCEDURAL",
            "severity": "HIGH",
            "correction": "You should have compared LMM with repeated-measures ANOVA in this longitudinal design.",
            "desired_behavior": "Compare LMM vs RM-ANOVA.",
            "target_agent": "statistics-agent",
            "target_skill": "statistical-data-analyst"
        }
        lesson_2 = {
            "lesson_id": "LSN-20260918-REP-002",
            "scope": "DOMAIN_WIDE",
            "is_what_not_to_do": True,
            "target_capability": "statistical-data-analyst",
            "what_happened": "Blind model adoption again.",
            "what_behavior_caused_outcome": "Omitted comparison.",
            "what_should_have_happened": "Compare models."
        }
        accumulated_case = self.synthesizer.synthesize_from_correction_and_lesson(feedback_2, lesson_2)

        self.assertEqual(accumulated_case["case_id"], case_1["case_id"])
        self.assertEqual(accumulated_case["repeat_count"], 2)

        # Still exactly 1 file on disk representing this institutionalized asset
        all_cases = self.synthesizer.load_cases(include_candidates=True)
        self.assertEqual(len(all_cases), 1)
        self.assertEqual(all_cases[0]["repeat_count"], 2)

    def test_06_old_mistakes_remain_testable_forever_and_never_deleted(self):
        """Old regression cases are never deleted merely because the agent passes them; retirement requires justification."""
        feedback = {
            "feedback_id": "FDB-20260918-RET-001",
            "type": "METHODOLOGY_CORRECTION",
            "scope": "REUSABLE_PROCEDURAL",
            "severity": "HIGH",
            "correction": "You should have compared LMM with repeated-measures ANOVA.",
            "desired_behavior": "Compare LMM vs RM-ANOVA.",
            "target_agent": "statistics-agent",
            "target_skill": "statistical-data-analyst"
        }
        lesson = {
            "lesson_id": "LSN-20260918-RET-001",
            "scope": "DOMAIN_WIDE",
            "is_what_not_to_do": True,
            "target_capability": "statistical-data-analyst",
            "what_happened": "Blind model adoption.",
            "what_behavior_caused_outcome": "Omitted comparison.",
            "what_should_have_happened": "Compare models."
        }
        case = self.synthesizer.synthesize_from_correction_and_lesson(feedback, lesson)
        case_id = case["case_id"]
        case_path = os.path.join(self.synthesizer.regression_dir, f"{case_id}.json")

        # Explicit retirement with justification
        justification = "Superseded by institutional 4-wave continuous-time differential equation model standard."
        retired_case = self.synthesizer.retire_case(case_id, justification)
        self.assertEqual(retired_case["status"], "retired")
        self.assertEqual(retired_case["retirement_reason"], justification)

        # Invariant: File MUST NOT be deleted from disk
        self.assertTrue(os.path.isfile(case_path), "Retired regression case must remain permanently on disk.")

        # Without include_retired, it is filtered out of active suites
        active_cases = self.synthesizer.load_cases(include_candidates=True, include_retired=False)
        self.assertEqual(len(active_cases), 0)

        # With include_retired, it remains discoverable and auditable
        all_cases = self.synthesizer.load_cases(include_candidates=True, include_retired=True)
        self.assertEqual(len(all_cases), 1)
        self.assertEqual(all_cases[0]["status"], "retired")

    def test_07_scope_containment_blocks_project_specific_corrections(self):
        """Project-specific corrections must never generate global regression cases."""
        feedback = {
            "feedback_id": "FDB-20260918-PROJ-001",
            "type": "METHODOLOGY_CORRECTION",
            "scope": "PROJECT_SPECIFIC",
            "severity": "HIGH",
            "correction": "In this thesis for Dr. Rezaei, name the supervisor in section 1.",
            "desired_behavior": "Follow supervisor specific preference.",
            "target_agent": "academic-writer",
            "target_skill": "chapter-4-writing"
        }
        lesson = {
            "lesson_id": "LSN-20260918-PROJ-001",
            "scope": "PROJECT_SPECIFIC",
            "is_what_not_to_do": True,
            "target_capability": "chapter-4-writing",
            "what_happened": "Omitted supervisor name.",
            "what_behavior_caused_outcome": "Generic template used.",
            "what_should_have_happened": "Include supervisor name."
        }

        res = self.synthesizer.synthesize_from_correction_and_lesson(feedback, lesson)
        self.assertIsNone(res, "Project-specific feedback must NOT generate a regression test case.")
        cases = self.synthesizer.load_cases(include_candidates=True)
        self.assertEqual(len(cases), 0)


if __name__ == "__main__":
    unittest.main()
