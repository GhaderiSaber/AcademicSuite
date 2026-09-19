#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_evidence_derived_promotion_phase31.py — Phase 31 Unit Tests

Verifies:
1. Missing adversarial evidence yields UNKNOWN status and blocks promotion.
2. Missing held-out evaluation yields UNKNOWN status and blocks promotion.
3. zero_regressions_verified cannot be asserted without actual regression results.
4. Actual regression results compute zero_regressions_verified deterministically.
5. Canonical evaluation marks unperformed suites as UNKNOWN with evidence_status MISSING.
6. Promotion requires all gates to be affirmatively PASS (zero UNKNOWN or FAIL).
7. Directive 18 ceilings (<= 500 lines, <= 40,000 bytes) are strictly maintained.
"""

import os
import sys
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

from scripts.academic_promotion_engine import AcademicPromotionEngine
from scripts.academic_canonical_evaluation import (
    CanonicalEvaluationResultBuilder,
    canonicalize_evaluation_result,
    validate_evaluation_result
)


class TestEvidenceDerivedPromotionPhase31(unittest.TestCase):
    """Authoritative test suite for Phase 31 evidence-derived promotion."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_phase31_test_")
        self.engine = AcademicPromotionEngine(base_dir=self.temp_dir)

        # Fully compliant canonical evaluation report with verified evidence across all suites
        self.fully_verified_report = {
            "contract_version": "1.0.0",
            "evaluation_id": "EVR-20260919-FULL001",
            "candidate_id": "CAND-VERIFIED-001",
            "baseline_id": "git-baseline-sha",
            "task_id": "PANEL-STANDARD",
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
            "baseline_metrics": {"total_runs": 10, "passes": 6},
            "candidate_metrics": {"total_runs": 10, "passes": 10},
            "regression_results": {
                "verdict": "PASS",
                "count": 0,
                "details": [],
                "fixes_original_mistake": True,
                "task_id": "TASK-REG-001",
                "evidence_status": "VERIFIED"
            },
            "adversarial_results": {
                "verdict": "PASS",
                "creates_new_mistake": False,
                "task_id": "TASK-ADV-001",
                "details": [],
                "evidence_status": "VERIFIED"
            },
            "heldout_results": {
                "verdict": "PASS",
                "pass_rate": 1.0,
                "generalizes_to_different_case": True,
                "overfitting_detected": False,
                "total_cases": 5,
                "task_id": "TASK-HELD-001",
                "evidence_status": "VERIFIED"
            },
            "contradictions": [],
            "evidence": [
                {
                    "artifact_path": "learning/evaluations/reports/EVR-20260919-FULL001.json",
                    "sha256": hashlib.sha256(b"verified_report_evidence_1").hexdigest(),
                    "evidence_type": "EVALUATION_REPORT"
                },
                {
                    "artifact_path": "learning/evaluations/raw/RUN-001.json",
                    "sha256": hashlib.sha256(b"verified_report_evidence_2").hexdigest(),
                    "evidence_type": "RAW_EXECUTION_TRACE"
                },
                {
                    "artifact_path": "learning/evaluations/raw/RUN-002.json",
                    "sha256": hashlib.sha256(b"verified_report_evidence_3").hexdigest(),
                    "evidence_type": "RAW_EXECUTION_TRACE"
                }
            ],
            "verdict": "PASS",
            "summary_metrics": {
                "total_cases_evaluated": 10,
                "target_capability_improved": True,
                "zero_regressions_verified": True,
                "adversarial_clearance": True,
                "protected_regressions": 0,
                "suite_pass_rates": {"regression": 1.0, "adversarial": 1.0, "heldout": 1.0}
            },
            "minimum_improvement_policy": {
                "target_capability_improved": True,
                "zero_regressions_verified": True,
                "adversarial_clearance": True
            },
            "counterfactual_analysis": {
                "what_improved": ["Resolved ANCOVA slope violation defect"],
                "what_regressed": [],
                "which_failure_disappeared": ["ancova_slope_heterogeneity"]
            },
            "all_diagnostics": []
        }

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _stage_candidate(self, candidate_id: str) -> dict:
        content = "### Valid exemplar for hypothesis testing"
        cand = {
            "contract_version": "1.0.0",
            "candidate_id": candidate_id,
            "target_component": ".agents/skills/chapter-4-writing/SKILL.md",
            "target_type": "SKILL_PROCEDURAL_SPECIFICATION",
            "target_skill": "chapter-4-writing",
            "parent_version": hashlib.sha256(b"parent").hexdigest(),
            "mutation_type": "EXEMPLAR_ADDITION",
            "mutation": {
                "diff_type": "UNIFIED_DIFF",
                "content": content,
                "checksum_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()
            },
            "rationale": "Empirical exemplar addition.",
            "expected_improvement": {"target_metric": "quality", "baseline_value": 0.5, "projected_value": 1.0},
            "affected_capabilities": ["chapter-4-writing"],
            "author_agent": "skill-evolver",
            "status": "CANDIDATE",
            "staged_at": datetime.now(timezone.utc).isoformat(),
            "source_lessons": ["LSN-001"],
            "associated_pitfall_id": "EXP-001",
            "testable_hypothesis": "Improves quality."
        }
        cand_file = os.path.join(self.engine.candidates_dir, f"{candidate_id}.json")
        with open(cand_file, "w", encoding="utf-8") as f:
            json.dump(cand, f, indent=2)
        return cand

    def test_01_missing_adversarial_evidence_yields_unknown_and_blocks_promotion(self):
        """1. Missing adversarial evidence yields UNKNOWN status and fail-closed promotion rejection."""
        report = json.loads(json.dumps(self.fully_verified_report))
        report["adversarial_results"] = {
            "verdict": "UNKNOWN",
            "evidence_status": "MISSING",
            "details": []
        }
        report["summary_metrics"].pop("adversarial_clearance", None)
        report["summary_metrics"]["suite_pass_rates"].pop("adversarial", None)
        report["minimum_improvement_policy"].pop("adversarial_clearance", None)

        gates = self.engine.verify_evaluation_gates(report)
        self.assertFalse(gates["all_passed"])
        self.assertEqual(gates["gate_results"]["adversarial_checks"]["status"], "UNKNOWN")
        self.assertFalse(gates["gate_results"]["adversarial_checks"]["passed"])
        self.assertTrue(any("Adversarial" in f and "UNKNOWN" in f for f in gates["failures"]))

        cid = "CAND-NO-ADV-001"
        self._stage_candidate(cid)
        res = self.engine.evaluate_and_promote(cid, report)
        self.assertEqual(res["decision"], "REJECTED")
        self.assertEqual(res["status"], "REJECTED_AND_ARCHIVED")

    def test_02_missing_heldout_evidence_yields_unknown_and_blocks_promotion(self):
        """2. Missing held-out evaluation yields UNKNOWN status and fail-closed promotion rejection."""
        report = json.loads(json.dumps(self.fully_verified_report))
        report["heldout_results"] = {
            "verdict": "UNKNOWN",
            "evidence_status": "MISSING",
            "pass_rate": 0.0
        }
        report["summary_metrics"]["suite_pass_rates"].pop("heldout", None)
        report.pop("heldout_integrity_verified", None)

        gates = self.engine.verify_evaluation_gates(report)
        self.assertFalse(gates["all_passed"])
        self.assertEqual(gates["gate_results"]["held_out_evaluation"]["status"], "UNKNOWN")
        self.assertFalse(gates["gate_results"]["held_out_evaluation"]["passed"])
        self.assertTrue(any("Held-out" in f and "UNKNOWN" in f for f in gates["failures"]))

        cid = "CAND-NO-HELD-001"
        self._stage_candidate(cid)
        res = self.engine.evaluate_and_promote(cid, report)
        self.assertEqual(res["decision"], "REJECTED")
        self.assertEqual(res["status"], "REJECTED_AND_ARCHIVED")

    def test_03_zero_regressions_cannot_be_asserted_without_actual_results(self):
        """3. zero_regressions_verified cannot be asserted without actual regression results."""
        report = json.loads(json.dumps(self.fully_verified_report))
        report["regression_results"] = {
            "verdict": "UNKNOWN",
            "evidence_status": "MISSING",
            "count": 0,
            "details": []
        }
        report["summary_metrics"]["suite_pass_rates"].pop("regression", None)
        report.pop("counterfactual_analysis", None)
        report.pop("regressions", None)
        report["minimum_improvement_policy"]["zero_regressions_verified"] = True
        report["summary_metrics"]["zero_regressions_verified"] = True

        gates = self.engine.verify_evaluation_gates(report)
        self.assertFalse(gates["all_passed"])
        self.assertEqual(gates["gate_results"]["existing_regression_suite"]["status"], "UNKNOWN")
        self.assertFalse(gates["gate_results"]["existing_regression_suite"]["passed"])
        self.assertTrue(any("Regression suite was not evaluated" in f for f in gates["failures"]))

        cid = "CAND-NO-REG-001"
        self._stage_candidate(cid)
        res = self.engine.evaluate_and_promote(cid, report)
        self.assertEqual(res["decision"], "REJECTED")

    def test_04_actual_regression_results_compute_zero_regressions_accurately(self):
        """4. Actual regression data deterministically calculates zero_regressions_verified."""
        report_clean = json.loads(json.dumps(self.fully_verified_report))
        report_clean["regression_results"] = {
            "verdict": "PASS",
            "count": 0,
            "details": [],
            "evidence_status": "VERIFIED"
        }
        gates_clean = self.engine.verify_evaluation_gates(report_clean)
        self.assertTrue(gates_clean["gate_results"]["existing_regression_suite"]["passed"])
        self.assertEqual(gates_clean["gate_results"]["existing_regression_suite"]["status"], "PASS")
        self.assertTrue(gates_clean["gate_results"]["existing_regression_suite"]["zero_regressions_verified"])

        report_regressed = json.loads(json.dumps(self.fully_verified_report))
        report_regressed["regression_results"] = {
            "verdict": "FAIL",
            "count": 2,
            "details": ["Regressed on ANOVA assumption", "Regressed on table formatting"],
            "evidence_status": "VERIFIED"
        }
        gates_reg = self.engine.verify_evaluation_gates(report_regressed)
        self.assertFalse(gates_reg["gate_results"]["existing_regression_suite"]["passed"])
        self.assertEqual(gates_reg["gate_results"]["existing_regression_suite"]["status"], "FAIL")
        self.assertFalse(gates_reg["gate_results"]["existing_regression_suite"]["zero_regressions_verified"])

    def test_05_canonical_evaluation_marks_missing_suites_as_unknown(self):
        """5. canonicalize_evaluation_result marks omitted suites as UNKNOWN with evidence_status MISSING."""
        incomplete_raw_report = {
            "report_id": "RAW-INCOMPLETE-001",
            "target_capability": "chapter-4-writing",
            "summary_metrics": {
                "total_cases_evaluated": 5
            }
        }
        canonical = canonicalize_evaluation_result(incomplete_raw_report, validate=True)
        self.assertEqual(canonical["regression_results"]["verdict"], "UNKNOWN")
        self.assertEqual(canonical["regression_results"]["evidence_status"], "MISSING")
        self.assertEqual(canonical["adversarial_results"]["verdict"], "UNKNOWN")
        self.assertEqual(canonical["adversarial_results"]["evidence_status"], "MISSING")
        self.assertEqual(canonical["heldout_results"]["verdict"], "UNKNOWN")
        self.assertEqual(canonical["heldout_results"]["evidence_status"], "MISSING")
        self.assertEqual(canonical["verdict"], "UNKNOWN")

        builder = CanonicalEvaluationResultBuilder(
            candidate_id="CAND-DEFAULT-001",
            baseline_id="base",
            task_id="task"
        )
        built = builder.build(validate=True)
        self.assertEqual(built["verdict"], "UNKNOWN")
        self.assertEqual(built["regression_results"]["verdict"], "UNKNOWN")

    def test_06_promotion_requires_all_gates_affirmatively_passed(self):
        """6. Promotion strictly requires all gates to be affirmatively PASS (zero UNKNOWN or FAIL)."""
        cid = "CAND-VERIFIED-AUTO-001"
        self._stage_candidate(cid)

        res = self.engine.evaluate_and_promote(cid, self.fully_verified_report)
        self.assertEqual(res["decision"], "PROMOTED")
        self.assertEqual(res["status"], "ACTIVE")

    def test_07_directive_18_ceilings(self):
        """7. Directive 18 ceilings (<= 500 lines, <= 40,000 bytes) are strictly respected."""
        files_to_check = [
            os.path.join(ROOT_DIR, "scripts", "academic_canonical_evaluation.py"),
            __file__
        ]
        for fpath in files_to_check:
            with open(fpath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            size = os.path.getsize(fpath)
            self.assertLessEqual(
                len(lines),
                500,
                f"{os.path.basename(fpath)} exceeds 500 lines ({len(lines)} lines)"
            )
            self.assertLessEqual(
                size,
                40000,
                f"{os.path.basename(fpath)} exceeds 40,000 bytes ({size} bytes)"
            )


if __name__ == "__main__":
    unittest.main()
