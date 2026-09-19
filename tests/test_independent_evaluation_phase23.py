#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_independent_evaluation_phase23.py — Test Suite for Phase 23: Independent Blinded A/B Evaluation

Tests:
1. test_blinded_token_assignment_and_sanitization:
   - Random assignment of Submission_A and Submission_B.
   - Candidate metadata (candidate_id, sandbox_id, version, self-assertions) cleanly stripped.
2. test_multi_task_panel_assembly:
   - Evaluates Baseline and Candidate across the exact same task panel (Task A, Task B, Task C).
3. test_blinded_evaluator_grades_without_identity:
   - Evaluator grades Submission_A and Submission_B across the 8 dimensions without agent identity.
4. test_unblinding_and_comparison_success:
   - Candidate resolves target defect and preserves baseline tasks -> PASS, defect_resolved: True.
5. test_regression_on_task_fails_independent_evaluation:
   - Candidate resolves target defect but regresses on regression task -> FAIL, zero_regressions: False.
6. test_self_asserted_candidate_evidence_blocked_at_promotion:
   - Promotion engine blocks candidates asserting self-evaluated improvement fail-closed.
7. test_schema_validation_independent_evaluation:
   - Complete independent evaluation report passes schema validation.
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

from scripts.academic_independent_evaluator import (
    AcademicIndependentEvaluator,
    SelfEvaluationBlockedError
)
from scripts.academic_promotion_engine import AcademicPromotionEngine
from contracts.contract_validator import validate_independent_evaluation


class TestIndependentEvaluationPhase23(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_indep_eval_")
        self.evaluator = AcademicIndependentEvaluator(base_dir=self.temp_dir)
        self.promotion_engine = AcademicPromotionEngine(base_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_blinded_token_assignment_and_sanitization(self):
        """Verify that blinding assigns Submission_A/Submission_B and strips all candidate identifiers."""
        candidate_raw = {
            "candidate_id": "CAND-2026-TEST-001",
            "sandbox_id": "SBX-CAND-001",
            "version": "V2",
            "improved": True,
            "self_verdict": "PASS",
            "statistics": {
                "artifact_path": "/path/to/learning/candidates/CAND-001/isolated_agent/out.json",
                "effect_size": 0.35,
                "confidence_interval": [0.15, 0.55],
                "assumptions_checked": ["homogeneity of slopes", "normality"]
            },
            "narrative": "تحلیل با رعایت استانداردها انجام شد (۰.۰۱ > p)."
        }
        baseline_raw = {
            "statistics": {
                "artifact_path": "legacy_output.json",
                "f_value": 3.42,
                "p_value": "p = .000"
            },
            "narrative": "تحلیل انجام شد (p = .000)."
        }

        blinded_subs, token_mapping, salt_hash = self.evaluator.blind_submissions(
            baseline_outputs=baseline_raw,
            candidate_outputs=candidate_raw,
            salt="test_salt_123"
        )

        # 1. Check tokens
        self.assertIn("Submission_A", blinded_subs)
        self.assertIn("Submission_B", blinded_subs)
        self.assertIn(token_mapping["candidate"], ["Submission_A", "Submission_B"])
        self.assertIn(token_mapping["baseline"], ["Submission_A", "Submission_B"])
        self.assertNotEqual(token_mapping["candidate"], token_mapping["baseline"])

        # 2. Check sanitization: candidate identifiers must be purged
        cand_payload = blinded_subs[token_mapping["candidate"]]
        self.assertNotIn("candidate_id", cand_payload)
        self.assertNotIn("sandbox_id", cand_payload)
        self.assertNotIn("version", cand_payload)
        self.assertNotIn("improved", cand_payload)
        self.assertNotIn("self_verdict", cand_payload)
        self.assertNotIn("isolated_agent", str(cand_payload))

    def test_multi_task_panel_assembly(self):
        """Verify standardized assembly of multi-task benchmark panel (Task A, Task B, Task C)."""
        panel = self.evaluator.build_task_panel(
            capability="chapter-4-writing",
            failure_signature="p_equals_point_zero_zero_zero"
        )
        self.assertEqual(len(panel), 3)

        task_ids = [t["task_id"] for t in panel]
        self.assertIn("TASK-A", task_ids)
        self.assertIn("TASK-B", task_ids)
        self.assertIn("TASK-C", task_ids)

        task_types = [t["type"] for t in panel]
        self.assertIn("TARGET_DEFECT", task_types)
        self.assertIn("RELATED_CAPABILITY", task_types)
        self.assertIn("REGRESSION_GUARD", task_types)

    def test_blinded_evaluator_grades_without_identity(self):
        """Verify that the evaluator grades Submission_A and Submission_B across 8 dimensions blindly."""
        panel = self.evaluator.build_task_panel(capability="statistical-data-analyst")

        cand_output = {
            "statistics": {
                "estimand": "Treatment Effect",
                "effect_size": 0.40,
                "confidence_interval": [0.20, 0.60],
                "artifact_path": "verified.json",
                "assumptions_checked": ["homogeneity of slopes", "normality"]
            },
            "reasoning": {
                "repeated_measures_structure": "Evaluated",
                "missingness": "Little MCAR evaluated",
                "candidate_model_comparison": "Compared"
            },
            "narrative": "تحلیل با دقت انجام شد (۰.۰۱ > p)."
        }
        base_output = {
            "statistics": {
                "artifact_path": "legacy.json",
                "p_value": "p = .000"
            },
            "narrative": "تحلیل انجام شد (p = .000)."
        }

        blinded_subs, token_mapping, salt_hash = self.evaluator.blind_submissions(
            baseline_outputs=base_output,
            candidate_outputs=cand_output
        )

        blinded_evals = self.evaluator.evaluate_blinded_panel(
            task_panel=panel,
            blinded_submissions=blinded_subs
        )

        # Both submissions evaluated
        self.assertIn("Submission_A", blinded_evals)
        self.assertIn("Submission_B", blinded_evals)

        for tok in ["Submission_A", "Submission_B"]:
            ev = blinded_evals[tok]
            self.assertIn("tasks", ev)
            self.assertIn("dimensional_evaluations", ev)
            self.assertIn("overall_verdict", ev)
            self.assertEqual(len(ev["dimensional_evaluations"]), 8)

    def test_unblinding_and_comparison_success(self):
        """Verify unblinding correctly decodes outcome when candidate outperforms baseline."""
        cand_output = {
            "statistics": {
                "estimand": "Treatment Effect",
                "effect_size": 0.40,
                "confidence_interval": [0.20, 0.60],
                "artifact_path": "verified.json",
                "assumptions_checked": ["homogeneity of slopes", "normality"]
            },
            "reasoning": {
                "repeated_measures_structure": "Evaluated",
                "missingness": "Little MCAR evaluated",
                "candidate_model_comparison": "Compared"
            },
            "narrative": "تحلیل با دقت انجام شد (۰.۰۱ > p)."
        }
        base_output = {
            "statistics": {
                "artifact_path": "legacy.json",
                "p_value": "p = .000"
            },
            "narrative": "تحلیل انجام شد (p = .000)."
        }

        report = self.evaluator.execute_independent_evaluation(
            candidate_id="CAND-SUCCESS-001",
            baseline_version="V1",
            capability="chapter-4-writing",
            baseline_outputs=base_output,
            candidate_outputs=cand_output,
            failure_signature="p_equals_point_zero_zero_zero"
        )

        unblinded = report["unblinded_comparison"]
        self.assertTrue(unblinded["defect_resolved"])
        self.assertTrue(unblinded["candidate_outperformed_baseline"])
        self.assertTrue(unblinded["zero_regressions_verified"])
        self.assertEqual(unblinded["independent_verdict"], "PASS")
        self.assertEqual(unblinded["recommendation"], "PROMOTE")
        self.assertGreater(unblinded["candidate_passes"], unblinded["baseline_passes"])

    def test_regression_on_task_fails_independent_evaluation(self):
        """Verify that a candidate introducing a regression fails independent evaluation."""
        # Candidate passes Task A (no p=.000) but fails Task C (missing reasoning properties)
        cand_output = {
            "statistics": {
                "estimand": "Treatment Effect",
                "effect_size": 0.30,
                "confidence_interval": [0.10, 0.50],
                "artifact_path": "verified.json",
                "assumptions_checked": ["homogeneity of slopes"]
            },
            # Missing reasoning -> will fail Task C
            "narrative": "تحلیل انجام شد (۰.۰۱ > p)."
        }
        # Baseline passes Task C but fails Task A (has p=.000)
        base_output = {
            "statistics": {
                "estimand": "Baseline Estimand",
                "effect_size": 0.25,
                "confidence_interval": [0.10, 0.40],
                "artifact_path": "legacy.json",
                "p_value": "p = .000"
            },
            "reasoning": {
                "repeated_measures_structure": "Evaluated",
                "missingness": "Evaluated",
                "candidate_model_comparison": "Compared"
            },
            "narrative": "تحلیل آماری انجام شد (۰.۰۵ > p)."
        }

        report = self.evaluator.execute_independent_evaluation(
            candidate_id="CAND-REGRESS-001",
            baseline_version="V1",
            capability="statistical-data-analyst",
            baseline_outputs=base_output,
            candidate_outputs=cand_output,
            failure_signature="p_equals_point_zero_zero_zero"
        )

        unblinded = report["unblinded_comparison"]
        # Baseline passed Task C, candidate failed Task C -> regression!
        self.assertFalse(unblinded["zero_regressions_verified"])
        self.assertEqual(unblinded["independent_verdict"], "FAIL")
        self.assertEqual(unblinded["recommendation"], "REJECT")

    def test_self_asserted_candidate_evidence_blocked_at_promotion(self):
        """Verify that promotion engine rejects candidates attempting self-evaluation."""
        # Candidate attempting self-evaluation without independent evaluation
        self_asserted_report = {
            "contract_version": "1.0.0",
            "report_id": "EVR-SELF-ASSERTED",
            "candidate_id": "CAND-SELF-001",
            "is_self_evaluated": True,
            "self_asserted": True,
            "summary_metrics": {
                "total_cases_evaluated": 5,
                "target_capability_improved": True,
                "zero_regressions_verified": True
            },
            "minimum_improvement_policy": {
                "target_capability_improved": True,
                "zero_regressions_verified": True
            }
        }

        # Create dummy candidate file
        cand_data = {
            "contract_version": "1.0.0",
            "candidate_id": "CAND-SELF-001",
            "target_component": "chapter-4-writing",
            "target_type": "SKILL_PROCEDURAL_SPECIFICATION",
            "mutation_type": "MISSING_STEP_ADDITION",
            "status": "CANDIDATE"
        }
        cand_path = os.path.join(self.temp_dir, "learning", "candidates", "CAND-SELF-001.json")
        os.makedirs(os.path.dirname(cand_path), exist_ok=True)
        with open(cand_path, "w", encoding="utf-8") as f:
            json.dump(cand_data, f)

        res = self.promotion_engine.evaluate_and_promote(
            candidate_id="CAND-SELF-001",
            evaluation_report=self_asserted_report
        )

        self.assertEqual(res["decision"], "REJECTED")
        self.assertIn("SELF_EVALUATION_PROHIBITED", res["reason"])

    def test_schema_validation_independent_evaluation(self):
        """Verify that generated independent_evaluation conforms 100% to JSON schema."""
        cand_output = {
            "statistics": {
                "estimand": "Treatment Effect",
                "effect_size": 0.40,
                "confidence_interval": [0.20, 0.60],
                "artifact_path": "verified.json",
                "assumptions_checked": ["homogeneity of slopes"]
            },
            "reasoning": {
                "repeated_measures_structure": "Evaluated",
                "missingness": "Evaluated",
                "candidate_model_comparison": "Compared"
            },
            "narrative": "تحلیل با دقت انجام شد (۰.۰۱ > p)."
        }
        base_output = {
            "statistics": {
                "artifact_path": "legacy.json",
                "p_value": "p = .000"
            },
            "narrative": "تحلیل انجام شد (p = .000)."
        }

        report = self.evaluator.execute_independent_evaluation(
            candidate_id="CAND-SCHEMA-001",
            baseline_version="V1",
            capability="chapter-4-writing",
            baseline_outputs=base_output,
            candidate_outputs=cand_output,
            failure_signature="p_equals_point_zero_zero_zero"
        )

        val = validate_independent_evaluation(report)
        self.assertTrue(val["valid"], f"Schema validation errors: {val.get('errors')}")


if __name__ == "__main__":
    unittest.main()
