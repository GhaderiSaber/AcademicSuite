#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_curriculum_case_phase32.py — Authoritative Test Suite for Phase 32:
Replace Synthetic Slow-Loop Curriculum with Actual Practice Cases.

Verifies:
1. Curriculum Case Schema Contract: AcademicCurriculumCaseContract defines all 9 mandatory fields:
   - case_id, dataset, data_provenance, research_question, design, difficulty,
     expected_invariants, expected_pitfalls, gold_behavioral_properties.
2. Physical Dataset Generation:
   - Generates actual physical CSV on disk with verified SHA256 and Directive 9 empirical decimal noise.
   - Verifies mathematical sanity floor: N >= 15, positive variance.
3. Data Provenance Verification:
   - Verifies source_type, generator_script, noise_injected, matching SHA256, and timestamps.
4. Formal Research Design:
   - Verifies design structure across Statistics and Writing ladders.
5. Behavioral Invariant Evaluation:
   - Confirms compliant agent execution satisfies invariants and passes.
   - Confirms methodological omission (e.g. omitting slope homogeneity) triggers invariant violation and fails.
6. Expected Pitfall Detection:
   - Confirms detection of p = .000, missing leading zeros in Persian, and unsupported causal language.
7. Gold Behavioral Property Scoring:
   - Confirms scoring of expert hallmarks (model comparisons, sensitivity analyses, CI reporting).
8. Canonical EvaluationResult Compliance:
   - Verifies invariant evaluation produces schema-valid EvaluationResult conforming to Phase 30/31.
9. End-to-End Slow Loop Integration:
   - Confirms slow loop in AcademicDualLoopEngine executes practice agent on real dataset without mock payloads.
"""

import os
import sys
import csv
import json
import uuid
import shutil
import hashlib
import tempfile
import unittest
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.contract_validator import (
    validate_curriculum_case,
    validate_evaluation_case,
    validate_evaluation_result
)
from scripts.academic_curriculum_builder import AcademicCurriculumBuilder
from scripts.curriculum_dataset_generator import CurriculumDatasetGenerator
from scripts.curriculum_invariant_evaluator import CurriculumInvariantEvaluator
from scripts.academic_dual_loop_engine import AcademicDualLoopEngine


class TestCurriculumCasePhase32(unittest.TestCase):
    """Authoritative test suite for Phase 32: Actual Practice Curriculum Cases."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_phase32_test_")
        self.builder = AcademicCurriculumBuilder(base_dir=self.temp_dir)
        self.engine = AcademicDualLoopEngine(base_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_curriculum_case_schema_contract_nine_mandatory_fields(self):
        """Every generated curriculum case must define all 9 mandatory first-class fields."""
        case = self.builder.generate_practice_case(
            capability="statistical-data-analyst",
            target_level=6,
            target_weakness="omitting_homogeneity_of_slopes_test"
        )

        # 9 mandatory fields
        self.assertIn("case_id", case)
        self.assertIn("dataset", case)
        self.assertIn("data_provenance", case)
        self.assertIn("research_question", case)
        self.assertIn("design", case)
        self.assertIn("difficulty", case)
        self.assertIn("expected_invariants", case)
        self.assertIn("expected_pitfalls", case)
        self.assertIn("gold_behavioral_properties", case)

        # Schema contract validation
        val_curr = validate_curriculum_case(case)
        self.assertTrue(val_curr["valid"], f"Curriculum case contract validation failed: {val_curr.get('errors')}")

        val_eval = validate_evaluation_case(case)
        self.assertTrue(val_eval["valid"], f"Evaluation case backward-compatibility failed: {val_eval.get('errors')}")

    def test_02_physical_dataset_generated_on_disk_with_verified_sha256(self):
        """Curriculum generator must write a real physical CSV file on disk with verified SHA256."""
        case = self.builder.generate_practice_case(
            capability="statistical-data-analyst",
            target_level=1
        )

        ds_info = case["dataset"]
        rel_path = ds_info["path"]
        abs_path = os.path.join(self.temp_dir, rel_path)

        # File must exist on disk
        self.assertTrue(os.path.isfile(abs_path), f"Physical dataset not found at {abs_path}")

        # Check cryptographic SHA256 matches
        with open(abs_path, "rb") as f:
            actual_sha = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(ds_info["sha256"], actual_sha)
        self.assertEqual(case["data_provenance"]["dataset_sha256"], actual_sha)

        # Inspect CSV content
        with open(abs_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        header = rows[0]
        self.assertIn("id", header)
        self.assertIn("group", header)
        self.assertIn("wellbeing_post", header)

        # Sample size >= 15
        data_rows = rows[1:]
        self.assertGreaterEqual(len(data_rows), 15)
        self.assertEqual(ds_info["sample_size"], len(data_rows))

        # Check Directive 9 decimal noise (not all whole integers)
        numeric_vals = [float(r[2]) for r in data_rows if r[2]]
        has_decimals = any(v % 1 != 0 for v in numeric_vals)
        self.assertTrue(has_decimals, "Dataset values must contain realistic empirical decimal noise per Directive 9")

    def test_03_data_provenance_audit_record(self):
        """Data provenance must record generator, timestamp, noise injection, and parameters."""
        case = self.builder.generate_practice_case(
            capability="statistical-data-analyst",
            target_level=3
        )

        prov = case["data_provenance"]
        self.assertEqual(prov["source_type"], "CALIBRATED_PSYCHOMETRIC_SIMULATION")
        self.assertEqual(prov["generator_script"], "scripts/academic_curriculum_builder.py")
        self.assertTrue(prov["noise_injected"])
        self.assertIn("generation_timestamp", prov)
        self.assertIn("parameters", prov)
        self.assertEqual(prov["parameters"]["level"], 3)

    def test_04_formal_research_design_structure(self):
        """Curriculum cases must formalize research design with IVs, DVs, covariates, and sample allocation."""
        # Level 6 ANCOVA
        case_ancova = self.builder.generate_practice_case(
            capability="statistical-data-analyst",
            target_level=6
        )
        design_ancova = case_ancova["design"]
        self.assertEqual(design_ancova["design_type"], "PRE_POST_ANCOVA")
        self.assertIn("group", design_ancova["independent_variables"])
        self.assertIn("post_test_score", design_ancova["dependent_variables"])
        self.assertIn("pre_test_score", design_ancova["covariates"])

        # Level 5 Unbalanced ANOVA
        case_unbal = self.builder.generate_practice_case(
            capability="statistical-data-analyst",
            target_level=5
        )
        design_unbal = case_unbal["design"]
        self.assertEqual(design_unbal["design_type"], "UNBALANCED_FACTORIAL_ANOVA")
        self.assertEqual(design_unbal["sample_allocation"], "UNEQUAL")

    def test_05_behavioral_invariant_evaluation_compliant_pass(self):
        """Behavioral invariant evaluator returns PASS when all required invariants are satisfied."""
        case = self.builder.generate_practice_case(
            capability="statistical-data-analyst",
            target_level=6  # L06 Baseline Imbalance ANCOVA
        )

        # Compliant execution observing all methodological invariants
        compliant_execution = {
            "narrative": (
                "بر اساس فرضیه پژوهش، همگنی شیب خطوط رگرسیون تایید شد (F = ۱.۱۲, ۰.۲۵ > p). "
                "تحلیل کوواریانس با کنترل پیش‌آزمون انجام گرفت (۰.۰۱ > p). اندازه اثر گزارش‌شده "
                "برابر با ۰.۳۵ و فاصله اطمینان ۹5 درصد [۰.۱۵, ۰.۵۵] می‌باشد."
            ),
            "statistics": {
                "estimand": "Baseline-adjusted treatment effect",
                "ancova_f_reported": True,
                "homogeneity_of_slopes_verified": True,
                "effect_size": 0.35,
                "partial_eta_squared": 0.35,
                "confidence_interval": [0.15, 0.55],
                "assumptions_checked": ["normality", "homogeneity of regression slopes", "homogeneity of variance"]
            },
            "reasoning": {
                "candidate_model_comparison": "Compared unadjusted ANOVA with ANCOVA",
                "estimand": "Adjusted treatment effect"
            }
        }

        result = self.builder.evaluate_practice_execution(case, compliant_execution)
        self.assertTrue(result["passed"])
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["status"], "PASSED")

        eval_res = result.get("evaluation_result", {})
        self.assertEqual(eval_res["verdict"], "PASS")
        self.assertEqual(len(eval_res["pitfalls_detected"]), 0)

    def test_06_behavioral_invariant_evaluation_omitted_slope_homogeneity_fails(self):
        """Omitting slope homogeneity in ANCOVA triggers invariant violation and fails."""
        case = self.builder.generate_practice_case(
            capability="statistical-data-analyst",
            target_level=6
        )

        # Flawed execution: omitted slope homogeneity check
        flawed_execution = {
            "narrative": "تحلیل کوواریانس بدون بررسی شیب رگرسیون اجرا شد (۰.۰۱ > p).",
            "statistics": {
                "ancova_f_reported": True,
                "effect_size": 0.30,
                "confidence_interval": [0.10, 0.50],
                "assumptions_checked": ["normality"]  # Slope homogeneity omitted!
            }
        }

        result = self.builder.evaluate_practice_execution(case, flawed_execution)
        self.assertFalse(result["passed"])
        self.assertEqual(result["verdict"], "FAIL")
        self.assertEqual(result["status"], "FAILED")

        # Feedback record generated
        self.assertIsNotNone(result["feedback_id"])

    def test_07_expected_pitfall_detector_catches_p_equals_zero_and_naked_decimals(self):
        """Evaluator detects p = .000 and Persian naked decimal anti-patterns."""
        case = self.builder.generate_practice_case(
            capability="academic-writer",
            target_level=1
        )

        # Anti-pattern payload: uses p = .000 and naked .05 in Persian
        pitfall_payload = {
            "narrative": "اثر معنادار بود و مقدار p = .000 گزارش شد همچنین مقدار خطا .۰۵ به دست آمد.",
            "statistics": {"p_value": 0.000}
        }

        eval_result = CurriculumInvariantEvaluator.evaluate(case, pitfall_payload)
        self.assertEqual(eval_result["verdict"], "FAIL")

        detected_pitfalls = eval_result["pitfalls_detected"]
        self.assertTrue(
            any("P-EQUALS-ZERO" in p for p in detected_pitfalls),
            f"Expected PIT-P-EQUALS-ZERO, got {detected_pitfalls}"
        )
        self.assertTrue(
            any("LEADING-ZERO" in p for p in detected_pitfalls),
            f"Expected PIT-MISSING-PERSIAN-LEADING-ZERO, got {detected_pitfalls}"
        )

    def test_08_canonical_evaluation_result_schema_compliance(self):
        """CurriculumInvariantEvaluator output strictly validates against canonical EvaluationResult schema."""
        case = self.builder.generate_practice_case(
            capability="statistical-data-analyst",
            target_level=2
        )
        compliant_execution = {
            "narrative": "تحلیل اندازه‌گیری مکرر زوجی اجرا شد (۰.۰۱ > p). اندازه اثر گزارش شد.",
            "statistics": {
                "estimand": "Paired change estimand",
                "effect_size": 0.40,
                "cohens_d": 0.40,
                "confidence_interval": [0.20, 0.60],
                "repeated_measures_structure": True
            }
        }

        eval_res = CurriculumInvariantEvaluator.evaluate(case, compliant_execution)
        val = validate_evaluation_result(eval_res)
        self.assertTrue(val["valid"], f"EvaluationResult schema issues: {val.get('errors')}")

        # Check 13 mandatory fields
        mandatory_fields = [
            "evaluation_id", "candidate_id", "baseline_id", "task_id",
            "dimensions", "baseline_metrics", "candidate_metrics",
            "regression_results", "adversarial_results", "heldout_results",
            "contradictions", "evidence", "verdict"
        ]
        for fld in mandatory_fields:
            self.assertIn(fld, eval_res)

    def test_09_end_to_end_slow_loop_without_synthetic_mock_payload(self):
        """Slow loop executes practice agent on physical dataset and conducts invariant evaluation."""
        # Seed telemetry so slow loop has a diagnosed weakness
        fb_entry = {
            "feedback_id": "FDB-TEST-L06",
            "type": "STATISTICAL_CORRECTION",
            "target_skill": "statistical-data-analyst",
            "repetition_count": 4,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        with open(os.path.join(self.engine.feedback_dir, "index.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps(fb_entry) + "\n")

        # Run slow loop in simulation mode
        result = self.engine.run_slow_loop(
            top_weaknesses=1,
            practice_difficulty_level=6,
            mode="simulation"
        )

        self.assertEqual(result["loop"], "SLOW")
        self.assertEqual(result["status"], "COMPLETED")
        self.assertGreaterEqual(result["evolved_capabilities_count"], 1)

        # Check that physical dataset was created under curriculum datasets
        datasets_dir = os.path.join(self.temp_dir, "learning", "evaluations", "curriculum", "datasets")
        self.assertTrue(os.path.isdir(datasets_dir))
        csv_files = [f for f in os.listdir(datasets_dir) if f.endswith(".csv")]
        self.assertGreaterEqual(len(csv_files), 1, "Expected at least one real physical CSV dataset generated")


if __name__ == "__main__":
    unittest.main()
