#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_evaluation_lab.py — Comprehensive Test Suite for AcademicSuite Evaluation Laboratory

Verifies:
1. Suite directory architecture across all 5 partitions (development, regression, adversarial, heldout, curriculum).
2. Schema compliance of evaluation test cases including difficulty, tags, and suite_type.
3. Deterministic statistics verifications (estimand, assumptions, effect size, CIs, p-value format, provenance).
4. Deterministic writing verifications (causal language guards, Persian leading zero, numerical concordance).
5. Deterministic evidence verifications (ghost citation / untraced reference detection).
6. Deterministic integrity verifications (raw data immutability, blocking production sample fallback).
7. Multidimensional diagnostic reporting (8 independent dimensions without scalar collapse).
8. Cryptographic held-out immutability guard (manifest verification, tampering detection, HeldoutTamperingError).
9. Candidate suite evaluation and schema-compliant evaluation_result generation with regression tracking.
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

from contracts.contract_validator import (
    validate_evaluation_case,
    validate_evaluation_result
)
from scripts.academic_evaluation_lab import (
    AcademicEvaluationLab,
    HeldoutTamperingError
)


class TestAcademicEvaluationLab(unittest.TestCase):
    """Authoritative test suite for the AcademicSuite Reusable Evaluation Laboratory."""

    @classmethod
    def setUpClass(cls):
        cls.lab = AcademicEvaluationLab(base_dir=ROOT_DIR)

    def test_01_laboratory_directory_layout_and_partitions(self):
        """All 5 evaluation partitions plus results directory must exist on disk."""
        eval_root = os.path.join(ROOT_DIR, "learning", "evaluations")
        self.assertTrue(os.path.isdir(eval_root), "learning/evaluations root must exist.")

        expected_partitions = ["development", "regression", "adversarial", "heldout", "curriculum", "results"]
        for partition in expected_partitions:
            p_dir = os.path.join(eval_root, partition)
            self.assertTrue(os.path.isdir(p_dir), f"Partition directory '{partition}' must exist.")

    def test_02_evaluation_cases_schema_compliance(self):
        """Seed evaluation cases in all suites must strictly satisfy evaluation_case.schema.json."""
        cases = self.lab.load_cases()
        self.assertGreaterEqual(len(cases), 5, "Must discover at least 5 seed evaluation cases.")

        suites_found = set()
        for case in cases:
            res = validate_evaluation_case(case)
            self.assertTrue(res["valid"], f"Case {case.get('case_id')} failed validation: {res.get('errors')}")
            self.assertIn("difficulty", case)
            self.assertIn("tags", case)
            self.assertIn("suite_type", case)
            suites_found.add(case["suite_type"])

        # Must have cases across all 5 suite types
        for s in AcademicEvaluationLab.SUITE_TYPES:
            self.assertIn(s, suites_found, f"Suite type '{s}' must have at least one test case.")

    def test_03_deterministic_statistics_verification(self):
        """Statistical verifier must deterministically catch missing estimands, assumptions, effect sizes, CIs, and bad p-values."""
        case = {
            "case_id": "EVAL-TEST-STAT-001",
            "capability": "chapter4",
            "task": {
                "hypothesis": "Non-directional hypothesis without effect",
                "research_question": "Does treatment work?"
            },
            "expected_properties": {
                "required_metrics": {
                    "effect_size_type": "partial_eta_squared",
                    "bca_confidence_interval_reported": True
                }
            },
            "forbidden_behaviors": [
                "omitting_homogeneity_of_slopes_test",
                "p_equals_point_zero_zero_zero"
            ]
        }

        # Flawed candidate output: missing estimand, missing slopes assumption, missing effect size, missing CI, p = .000
        flawed_output = {
            "f_value": 12.45,
            "p_value": "p = .000",
            "assumptions_checked": ["normality", "levene"]
        }

        diagnostics = self.lab.check_statistics(case, flawed_output)
        failure_types = [d["failure_type"] for d in diagnostics]

        self.assertIn("missing_estimand", failure_types)
        self.assertIn("omitted_critical_assumption", failure_types)
        self.assertIn("missing_effect_size", failure_types)
        self.assertIn("missing_confidence_interval", failure_types)
        self.assertIn("prohibited_p_value_formatting", failure_types)

        # Compliant candidate output
        compliant_output = {
            "estimand": "Average Treatment Effect (ATE)",
            "homogeneity_of_slopes_checked": True,
            "assumptions_checked": ["homogeneity of regression slopes", "normality", "levene"],
            "effect_size": 0.18,
            "partial_eta_squared": 0.18,
            "confidence_interval": [0.08, 0.28],
            "p_value": "p < .001",
            "artifact_path": "03_assumptions.json"
        }
        clean_diags = self.lab.check_statistics(case, compliant_output)
        self.assertEqual(len(clean_diags), 0, f"Compliant output should produce 0 diagnostics, got: {clean_diags}")

    def test_04_deterministic_writing_verification(self):
        """Writing verifier must detect unsupported causal claims, Persian leading zero violations, and numerical discordance."""
        case = {
            "case_id": "EVAL-TEST-WRITE-001",
            "inputs": {
                "spec_parameters": {
                    "design_type": "cross_sectional_correlational"
                }
            }
        }

        # Flawed narrative: causal claim in observational study, missing leading zero (.۰۵), mismatch with machine data
        flawed_narrative = "تحلیل رگرسیون اثبات کرد که استرس شغلی علت مستقیم فرسودگی شغلی است و ضریب رگرسیون در سطح .۰۵ معنادار شد."
        machine_data = {"f_value": 18.52, "beta": 0.44}

        diagnostics = self.lab.check_writing(case, flawed_narrative, machine_data)
        failure_types = [d["failure_type"] for d in diagnostics]

        self.assertIn("unsupported_causal_language", failure_types)
        self.assertIn("persian_leading_zero_omitted", failure_types)
        self.assertIn("text_data_discordance", failure_types)

        # Compliant narrative: associative wording, Persian leading zero ۰.۰۵, exact statistic present
        compliant_narrative = "یافته‌ها نشان داد استرس شغلی رابطه معناداری با فرسودگی شغلی دارد (18.52 = F، ۰.۰۵ > p)."
        clean_diags = self.lab.check_writing(case, compliant_narrative, machine_data)
        self.assertEqual(len(clean_diags), 0, f"Compliant writing should have 0 diagnostics, got: {clean_diags}")

    def test_05_deterministic_evidence_and_ghost_citation_check(self):
        """Evidence verifier must flag untraced ghost citations not present in bibliography."""
        case = {"case_id": "EVAL-TEST-EVID-001"}
        citations = ["Hayes_2018", "GhostAuthor_2024"]
        bibliographic_records = [
            {"citation_key": "Hayes_2018", "doi": "10.1111/xyz", "author": "Hayes", "year": 2018}
        ]

        diagnostics = self.lab.check_evidence(case, citations, bibliographic_records)
        self.assertEqual(len(diagnostics), 1)
        self.assertEqual(diagnostics[0]["failure_type"], "untraced_citation_ghost_reference")
        self.assertIn("GhostAuthor_2024", diagnostics[0]["evidence"])

    def test_06_deterministic_integrity_and_sample_fallback_blocking(self):
        """Integrity verifier must detect dataset tampering and block production sample-data fallback."""
        case = {"case_id": "EVAL-TEST-INTEG-001"}

        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tf:
            tf.write(b"REAL_RESEARCH_DATASET_V1")
            tf_path = tf.name

        try:
            expected_sha = hashlib.sha256(b"ORIGINAL_IMMUTABLE_DATA").hexdigest()
            exec_log = {"status": "SUCCESS", "mode": "sampleSimulatedDataFallback"}

            diagnostics = self.lab.check_integrity(
                case,
                execution_log=exec_log,
                raw_dataset_path=tf_path,
                expected_sha256=expected_sha
            )
            failure_types = [d["failure_type"] for d in diagnostics]

            self.assertIn("raw_data_mutation_detected", failure_types)
            self.assertIn("production_sample_data_fallback_blocked", failure_types)
        finally:
            if os.path.exists(tf_path):
                os.remove(tf_path)

    def test_07_eight_independent_dimensions_without_scalar_collapse(self):
        """Evaluations must report across 8 independent dimensions and forbid scalar overall intelligence scores."""
        case = self.lab.load_cases(suite_type="regression")[0]
        payload = {
            "statistics": {
                "estimand": "Direct effect",
                "assumptions_checked": ["normality"],  # Missing slope assumption
                "effect_size": 0.25,
                "partial_eta_squared": 0.25,
                "artifact_path": "03_assumptions.json"
            }
        }

        res = self.lab.evaluate_candidate_on_case("CAND-MOCK-001", case, payload)
        self.assertIn("dimensional_evaluations", res)
        dims = res["dimensional_evaluations"]

        for d in AcademicEvaluationLab.DIMENSIONS:
            self.assertIn(d, dims, f"Dimension '{d}' must be independently evaluated.")
            self.assertIn("verdict", dims[d])

        # statistical_validity should fail due to missing slope assumption in regression case
        self.assertEqual(dims["statistical_validity"]["verdict"], "FAIL")
        self.assertIn("omitted_critical_assumption", dims["statistical_validity"]["failure_types"])

    def test_08_heldout_immutability_guard_and_tampering_defense(self):
        """Held-out cases must be cryptographically protected from candidate generation tampering."""
        # 1. Intact held-out directory must pass
        valid, errors = self.lab.verify_heldout_integrity()
        self.assertTrue(valid, f"Intact held-out manifest must pass integrity: {errors}")

        # 2. Tampering test using an isolated temp lab
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_lab = AcademicEvaluationLab(base_dir=tmp_dir)
            heldout_dir = temp_lab.suite_dirs["heldout"]

            # Create a legitimate held-out case and manifest
            case_path = os.path.join(heldout_dir, "EVAL-CASE-TEMP-001.json")
            with open(case_path, "w", encoding="utf-8") as f:
                f.write('{"case_id": "EVAL-CASE-TEMP-001"}')

            with open(case_path, "rb") as f:
                h = hashlib.sha256(f.read()).hexdigest()

            manifest_path = os.path.join(heldout_dir, "manifest.sha256")
            with open(manifest_path, "w", encoding="utf-8") as f:
                f.write(f"{h}  learning/evaluations/heldout/EVAL-CASE-TEMP-001.json\n")

            # Check valid
            v, errs = temp_lab.verify_heldout_integrity()
            self.assertTrue(v)

            # Now tamper with the heldout case (simulate candidate modifying test to pass)
            with open(case_path, "w", encoding="utf-8") as f:
                f.write('{"case_id": "EVAL-CASE-TEMP-001", "tampered": true}')

            v_tampered, errs_tampered = temp_lab.verify_heldout_integrity()
            self.assertFalse(v_tampered, "Tampered held-out case must be detected.")
            self.assertTrue(any("has been modified" in e for e in errs_tampered))

            # Running evaluate_suite on tampered lab must raise HeldoutTamperingError
            with self.assertRaises(HeldoutTamperingError):
                temp_lab.evaluate_suite("CAND-TAMPERER", "v1.0.0", suite_type="heldout")

    def test_09_full_candidate_suite_evaluation_and_result_contract(self):
        """Evaluating candidate suite must generate a fully compliant evaluation_result artifact."""
        candidate_payload = {
            "statistics": {
                "estimand": "Indirect effect ab",
                "assumptions_checked": ["homogeneity of slopes", "normality"],
                "effect_size": 0.22,
                "partial_eta_squared": 0.22,
                "confidence_interval": [0.05, 0.40],
                "artifact_path": "03_assumptions.json"
            },
            "narrative": "تحلیل نشان داد اثر مداخله معنادار است (۰.۰۵ > p).",
            "citations": ["Hayes_2018"],
            "bibliographic_records": [{"citation_key": "Hayes_2018"}],
            "execution_log": {"status": "SUCCESS"}
        }

        report = self.lab.evaluate_suite(
            candidate_id="CAND-TEST-ALPHA",
            baseline_version="baseline-sha-12345",
            suite_type="regression",
            candidate_payload=candidate_payload
        )

        # Verify contract schema compliance
        val_res = validate_evaluation_result(report)
        self.assertTrue(val_res["valid"], f"Evaluation result contract failed: {val_res.get('errors')}")

        # Check structure
        self.assertEqual(report["candidate_id"], "CAND-TEST-ALPHA")
        self.assertIn("metrics", report)
        self.assertIn("dimensional_evaluations", report)
        self.assertIn("overall_verdict", report)

        # Verify artifact written to disk
        result_file = os.path.join(self.lab.results_dir, f"{report['evaluation_id']}.json")
        self.assertTrue(os.path.isfile(result_file), "Evaluation result JSON must be saved on disk.")


if __name__ == "__main__":
    unittest.main()
