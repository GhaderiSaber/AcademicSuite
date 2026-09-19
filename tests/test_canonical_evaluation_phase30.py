#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_canonical_evaluation_phase30.py — Phase 30 Canonical Evaluation Schema Unit Tests

Codified under ADR-035 (Phase 30):
Tests the canonical EvaluationResult contract, the canonicalization engine,
and the fail-closed promotion gate enforcement:
"No promotion is allowed without a schema-valid EvaluationResult."
"""

import os
import sys
import json
import uuid
import copy
import shutil
import tempfile
import unittest
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Auto-discovery shim for virtualenv packages
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

from contracts.contract_validator import validate_evaluation_result
from scripts.academic_canonical_evaluation import (
    CANONICAL_FIELDS,
    CANONICAL_DIMENSIONS,
    CanonicalEvaluationResultBuilder,
    build_canonical_evaluation_result,
    canonicalize_evaluation_result
)
from scripts.academic_evaluation_lab import AcademicEvaluationLab
from scripts.academic_independent_evaluator import AcademicIndependentEvaluator
from scripts.academic_promotion_engine import AcademicPromotionEngine


class TestCanonicalEvaluationPhase30(unittest.TestCase):
    """Test suite for Phase 30 Canonical EvaluationResult Schema and Promotion Gate."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_canonical_eval_test_")
        self.promotion_engine = AcademicPromotionEngine(base_dir=self.temp_dir)
        self.eval_lab = AcademicEvaluationLab(base_dir=self.temp_dir)
        self.indep_evaluator = AcademicIndependentEvaluator(base_dir=self.temp_dir)

        # Baseline valid canonical EvaluationResult fixture
        self.valid_canonical_eval = {
            "evaluation_id": "EVR-20260919-CANONICAL-001",
            "candidate_id": "CAND-APA-TYPOGRAPHY-001",
            "baseline_id": "git-baseline-v1.0",
            "task_id": "PANEL-HYPOTHESIS-TESTING-01",
            "dimensions": {
                "correctness": {"verdict": "PASS"},
                "methodology": {"verdict": "PASS"},
                "statistical_validity": {"verdict": "PASS"},
                "evidence_grounding": {"verdict": "PASS"},
                "integrity": {"verdict": "PASS"},
                "robustness": {"verdict": "PASS"},
                "consistency": {"verdict": "PASS"},
                "efficiency": {"verdict": "PASS"}
            },
            "baseline_metrics": {
                "total_runs": 10,
                "successful_runs": 8,
                "defects_detected": 2
            },
            "candidate_metrics": {
                "total_runs": 10,
                "successful_runs": 10,
                "defects_detected": 0
            },
            "regression_results": {
                "verdict": "PASS",
                "count": 0,
                "details": [],
                "fixes_original_mistake": True
            },
            "adversarial_results": {
                "verdict": "PASS",
                "creates_new_mistake": False,
                "details": []
            },
            "heldout_results": {
                "verdict": "PASS",
                "pass_rate": 1.0,
                "generalizes_to_different_case": True,
                "total_cases": 5
            },
            "contradictions": [],
            "evidence": [
                {
                    "artifact_path": "learning/evaluations/results/EVR-20260919-CANONICAL-001.json",
                    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                    "evidence_type": "STANDARDIZED_EVALUATION_REPORT"
                }
            ],
            "verdict": "PASS",
            "contract_version": "1.0.0",
            "evaluated_at": "2026-09-19T12:00:00Z"
        }

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # Test 1: Canonical Schema Validates 13 Fields
    # -------------------------------------------------------------------------
    def test_01_canonical_schema_validates_13_fields(self):
        """1. A complete EvaluationResult with all 13 canonical fields passes schema validation."""
        val = validate_evaluation_result(self.valid_canonical_eval)
        self.assertTrue(val["valid"], f"Valid EvaluationResult failed schema validation: {val.get('errors')}")
        self.assertEqual(len(val["errors"]), 0)

    # -------------------------------------------------------------------------
    # Test 2: Missing Any of the 13 Fields Fails Schema Validation
    # -------------------------------------------------------------------------
    def test_02_missing_any_of_13_fields_fails_schema_validation(self):
        """2. Omitting ANY of the 13 mandatory fields causes fail-closed schema rejection."""
        self.assertEqual(len(CANONICAL_FIELDS), 13)

        for field in CANONICAL_FIELDS:
            broken_eval = copy.deepcopy(self.valid_canonical_eval)
            del broken_eval[field]
            val = validate_evaluation_result(broken_eval)
            self.assertFalse(
                val["valid"],
                f"EvaluationResult must fail validation when mandatory field '{field}' is omitted."
            )
            self.assertTrue(
                any(field in err for err in val["errors"]),
                f"Error message must mention omitted field '{field}'"
            )

    # -------------------------------------------------------------------------
    # Test 3: Canonical Evaluation Builder
    # -------------------------------------------------------------------------
    def test_03_canonical_evaluation_builder(self):
        """3. CanonicalEvaluationResultBuilder cleanly constructs and validates an EvaluationResult."""
        builder = CanonicalEvaluationResultBuilder(
            candidate_id="CAND-REGRESSION-FIX",
            baseline_id="git-baseline-sha1",
            task_id="TASK-ANCOVA-SLOPE"
        )
        builder.set_metrics(
            baseline_metrics={"runs": 5, "passes": 3},
            candidate_metrics={"runs": 5, "passes": 5}
        )
        builder.set_suite_results(
            regression_results={"verdict": "PASS", "count": 0, "details": []},
            adversarial_results={"verdict": "PASS", "creates_new_mistake": False, "details": []},
            heldout_results={"verdict": "PASS", "pass_rate": 1.0, "generalizes_to_different_case": True}
        )
        builder.set_verdict("PASS")

        built = builder.build(validate=True)
        for f in CANONICAL_FIELDS:
            self.assertIn(f, built)
        self.assertEqual(built["verdict"], "PASS")
        self.assertEqual(built["candidate_id"], "CAND-REGRESSION-FIX")

    # -------------------------------------------------------------------------
    # Test 4: Canonicalize Independent Evaluator Output
    # -------------------------------------------------------------------------
    def test_04_canonicalize_independent_evaluator_output(self):
        """4. Independent blinded evaluation reports are cleanly transformed into valid EvaluationResult."""
        indep_report = {
            "contract_version": "1.0.0",
            "evaluation_id": "INDEP-EVL-20260919-MOCK01",
            "candidate_id": "CAND-LONGITUDINAL-LMM",
            "baseline_version": "git-baseline-v2",
            "capability": "statistical-data-analyst",
            "tasks": [{"task_id": "TASK-LMM-01", "name": "LMM Longitudinal", "type": "REGRESSION"}],
            "blinding": {
                "is_blinded": True,
                "blinded_tokens": ["Submission_A", "Submission_B"],
                "salt_hash": "a1b2c3d4e5"
            },
            "blinded_evaluations": {
                "Submission_A": {"passed_tasks_count": 1, "passed_tasks": ["TASK-LMM-01"]},
                "Submission_B": {"passed_tasks_count": 0, "passed_tasks": []}
            },
            "unblinded_comparison": {
                "candidate_token": "Submission_A",
                "baseline_token": "Submission_B",
                "candidate_passes": 1,
                "baseline_passes": 0,
                "defect_resolved": True,
                "candidate_outperformed_baseline": True,
                "zero_regressions_verified": True,
                "regression_result": {"verdict": "PASS", "fixes_original_mistake": True, "task_id": "TASK-LMM-01"},
                "adversarial_result": {"verdict": "PASS", "creates_new_mistake": False, "task_id": "TASK-ADV-01"},
                "heldout_result": {"verdict": "PASS", "generalizes_to_different_case": True, "task_id": "TASK-HELD-01"},
                "conditional_rule_verified": True,
                "independent_verdict": "PASS",
                "recommendation": "PROMOTE"
            },
            "evaluated_at": "2026-09-19T12:00:00Z"
        }

        canonical = canonicalize_evaluation_result(indep_report)
        val = validate_evaluation_result(canonical)
        self.assertTrue(val["valid"], f"Canonicalized independent report must be valid: {val.get('errors')}")
        self.assertEqual(canonical["evaluation_id"], "INDEP-EVL-20260919-MOCK01")
        self.assertEqual(canonical["candidate_id"], "CAND-LONGITUDINAL-LMM")
        self.assertEqual(canonical["baseline_id"], "git-baseline-v2")
        self.assertEqual(canonical["task_id"], "TASK-LMM-01")
        self.assertEqual(canonical["verdict"], "PASS")

        # Test helper method on AcademicIndependentEvaluator
        res_from_helper = self.indep_evaluator.to_canonical_evaluation_result(indep_report)
        self.assertTrue(validate_evaluation_result(res_from_helper)["valid"])

    # -------------------------------------------------------------------------
    # Test 5: Canonicalize Evaluation Lab Output
    # -------------------------------------------------------------------------
    def test_05_canonicalize_evaluation_lab_output(self):
        """5. Evaluation lab evaluate_suite outputs conform natively to the canonical EvaluationResult schema."""
        candidate_payload = {
            "statistics": {"df": 24, "p_value": 0.001},
            "narrative": "A standard ANCOVA was conducted with p < 0.001."
        }
        report = self.eval_lab.evaluate_suite(
            candidate_id="CAND-TEST-LAB",
            baseline_version="base-commit-xyz",
            suite_type="regression",
            candidate_payload=candidate_payload
        )

        val = validate_evaluation_result(report)
        self.assertTrue(val["valid"], f"Evaluation lab report must satisfy EvaluationResult schema: {val.get('errors')}")
        self.assertEqual(report["candidate_id"], "CAND-TEST-LAB")
        self.assertEqual(report["baseline_id"], "base-commit-xyz")
        self.assertIn("dimensions", report)
        self.assertIn("baseline_metrics", report)
        self.assertIn("candidate_metrics", report)

    # -------------------------------------------------------------------------
    # Test 6: Canonicalize Three-Way Evaluation Output
    # -------------------------------------------------------------------------
    def test_06_canonicalize_three_way_evaluation_output(self):
        """6. Three-way evaluation outputs are canonicalized into schema-valid EvaluationResult."""
        three_way_report = {
            "evaluation_id": "EVL-3WAY-20260919-001",
            "candidate_id": "CAND-3WAY-TEST",
            "target_capability": "longitudinal-modeling",
            "arms": {
                "baseline": {"verdict": "FAIL", "metrics": {"acc": 0.5}},
                "candidate": {"verdict": "PASS", "metrics": {"acc": 1.0}},
                "adversarial": {"verdict": "FAIL", "metrics": {"acc": 0.0}}
            },
            "comparison_summary": {
                "defect_resolved": True,
                "candidate_outperformed_baseline": True,
                "adversarial_resilience_verified": True,
                "zero_regressions_verified": True
            },
            "qc_verdict": "PASS",
            "dimensional_evaluations": {
                "correctness": {"verdict": "PASS"},
                "methodology": {"verdict": "PASS"}
            },
            "heldout_results": {
                "total_cases": 4,
                "pass_rate": 1.0,
                "overfitting_detected": False,
                "verdict": "PASS"
            }
        }

        canonical = canonicalize_evaluation_result(three_way_report)
        val = validate_evaluation_result(canonical)
        self.assertTrue(val["valid"], f"Canonicalized 3-way evaluation must be valid: {val.get('errors')}")
        self.assertEqual(canonical["candidate_id"], "CAND-3WAY-TEST")
        self.assertEqual(canonical["verdict"], "PASS")

    # -------------------------------------------------------------------------
    # Test 7: Promotion Engine Rejects Non-Schema-Valid Report
    # -------------------------------------------------------------------------
    def test_07_promotion_engine_rejects_non_schema_valid_report(self):
        """7. Promotion engine strictly rejects non-schema-valid evaluation reports fail-closed."""
        # Malformed report missing mandatory canonical fields
        invalid_report = {
            "not_an_evaluation_id": "xyz",
            "candidate_name": "unsupported",
            "summary_metrics": {"total_cases_evaluated": 5}
        }

        gates = self.promotion_engine.verify_evaluation_gates(invalid_report)
        self.assertFalse(gates["all_passed"], "Non-schema-valid report must fail evaluation gates.")
        self.assertFalse(gates["gate_results"]["canonical_schema"]["passed"])
        self.assertTrue(any("INVALID_EVALUATION_SCHEMA" in f for f in gates["failures"]))

    # -------------------------------------------------------------------------
    # Test 8: Promotion Engine Accepts Valid Canonical EvaluationResult
    # -------------------------------------------------------------------------
    def test_08_promotion_engine_accepts_valid_canonical_evaluation_result(self):
        """8. Promotion engine accepts and approves schema-valid canonical EvaluationResult."""
        gates = self.promotion_engine.verify_evaluation_gates(self.valid_canonical_eval)
        self.assertTrue(gates["all_passed"], f"Valid canonical evaluation must pass all gates: {gates['failures']}")
        self.assertTrue(gates["gate_results"]["canonical_schema"]["passed"])
        self.assertEqual(gates["gate_results"]["canonical_schema"]["verdict"], "PASS")

    # -------------------------------------------------------------------------
    # Test 9: Prohibition of Scalar Intelligence Scores
    # -------------------------------------------------------------------------
    def test_09_prohibition_of_scalar_intelligence_score(self):
        """9. Injecting scalar intelligence scores violates the constitutional schema constraint."""
        forbidden_names = ["overall_intelligence", "agent_iq", "general_intelligence_score", "smartness_rating"]
        for forbidden in forbidden_names:
            tainted = copy.deepcopy(self.valid_canonical_eval)
            tainted[forbidden] = 95.0
            val = validate_evaluation_result(tainted)
            self.assertFalse(
                val["valid"],
                f"EvaluationResult containing '{forbidden}' must fail schema validation."
            )

    # -------------------------------------------------------------------------
    # Test 10: Directive 18 Ceilings
    # -------------------------------------------------------------------------
    def test_10_directive_18_ceilings(self):
        """10. scripts/academic_canonical_evaluation.py strictly respects <= 500 lines and <= 40,000 bytes."""
        canonical_script = os.path.join(ROOT_DIR, "scripts", "academic_canonical_evaluation.py")
        self.assertTrue(os.path.isfile(canonical_script))

        with open(canonical_script, "r", encoding="utf-8") as f:
            content = f.read()

        line_count = len(content.splitlines())
        byte_count = len(content.encode("utf-8"))

        self.assertLessEqual(line_count, 500, f"Line count {line_count} exceeds 500 lines.")
        self.assertLessEqual(byte_count, 40000, f"Byte count {byte_count} exceeds 40,000 bytes.")


if __name__ == "__main__":
    unittest.main()
