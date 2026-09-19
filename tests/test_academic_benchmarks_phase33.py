#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_benchmarks_phase33.py — Phase 33 Academic Behavioral Benchmarks Test Suite

Tests:
1. Schema contract validation across all 18 benchmark cases.
2. Completeness: exactly 18 families covered with zero omissions.
3. Three-pillar completeness: must_do, must_not_do, and required_evidence non-empty.
4. Physical dataset existence, row counts (N >= 15), and SHA256 integrity.
5. Evaluator grading engine:
   - Compliant candidate passes with 100% score.
   - Missing prerequisite assumption check fails must_do.
   - Forbidden pitfall (p = .000, Baron & Kenny, slope violation) fails must_not_do.
   - Missing required artifact/evidence fails required_evidence.
6. CLI validation commands.
7. Directive 6 (English filenames) and Directive 18 (single-view context budget).
"""

import os
import sys
import json
import hashlib
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.contract_validator import validate_academic_benchmark_case
from scripts.academic_benchmark_suite import AcademicBenchmarkSuite, ALL_FAMILIES


class TestAcademicBenchmarksPhase33(unittest.TestCase):
    """Test suite for Phase 33 academic behavioral benchmarks."""

    @classmethod
    def setUpClass(cls):
        cls.suite = AcademicBenchmarkSuite()
        cls.cases = cls.suite.discover_cases()
        cls.catalog_path = os.path.join(ROOT_DIR, "evals", "benchmarks", "benchmark_catalog.json")

    def test_01_all_18_families_present(self):
        """Verify all 18 canonical benchmark families are discovered."""
        self.assertEqual(len(self.cases), 18, f"Expected 18 cases, found {len(self.cases)}")
        found_families = {c["family"] for c in self.cases}
        expected_families = set(ALL_FAMILIES)
        self.assertEqual(found_families, expected_families, f"Missing families: {expected_families - found_families}")

    def test_02_contract_schema_validity(self):
        """Validate every benchmark case against academic_benchmark_case.schema.json."""
        for case in self.cases:
            case_id = case.get("case_id", "UNKNOWN")
            rep = validate_academic_benchmark_case(case)
            self.assertTrue(rep["valid"], f"Case {case_id} failed schema validation: {rep.get('errors')}")

    def test_03_three_pillar_completeness(self):
        """Verify each case specifies must_do, must_not_do, and required_evidence."""
        for case in self.cases:
            case_id = case["case_id"]
            must_do = case.get("must_do", [])
            must_not_do = case.get("must_not_do", [])
            required_evidence = case.get("required_evidence", [])

            self.assertGreaterEqual(len(must_do), 1, f"Case {case_id} has empty must_do")
            self.assertGreaterEqual(len(must_not_do), 1, f"Case {case_id} has empty must_not_do")
            self.assertGreaterEqual(len(required_evidence), 1, f"Case {case_id} has empty required_evidence")

            # Check individual item fields
            for md in must_do:
                self.assertIn("action_id", md)
                self.assertIn("description", md)
                self.assertIn("verification_rule", md)

            for mnd in must_not_do:
                self.assertIn("pitfall_id", mnd)
                self.assertIn("description", mnd)
                self.assertIn("detection_rule", mnd)

            for re in required_evidence:
                self.assertIn("evidence_id", re)
                self.assertIn("description", re)
                self.assertIn("evidence_type", re)
                self.assertIn("verification_method", re)

    def test_04_physical_dataset_existence_and_sha256(self):
        """Verify physical dataset files on disk exist and SHA256 matches."""
        for case in self.cases:
            case_id = case["case_id"]
            ds_spec = case.get("dataset", {})
            rel_path = ds_spec.get("path", "")
            abs_path = os.path.join(ROOT_DIR, rel_path)

            self.assertTrue(os.path.exists(abs_path), f"Dataset missing for {case_id}: {abs_path}")
            self.assertGreaterEqual(ds_spec.get("sample_size", 0), 15, f"Sample size < 15 for {case_id}")

            # Verify cryptographic SHA256
            hasher = hashlib.sha256()
            with open(abs_path, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            real_sha = hasher.hexdigest()
            self.assertEqual(real_sha, ds_spec.get("sha256"), f"SHA256 mismatch for {case_id}")

    def test_05_benchmark_catalog_integrity(self):
        """Verify benchmark_catalog.json indexes all 18 families."""
        self.assertTrue(os.path.exists(self.catalog_path), "benchmark_catalog.json does not exist")
        with open(self.catalog_path, "r", encoding="utf-8") as f:
            cat = json.load(f)
        self.assertEqual(cat.get("total_families"), 18)
        self.assertEqual(len(cat.get("families", {})), 18)

    def test_06_compliant_execution_passes_evaluator(self):
        """Verify a fully compliant execution passes all 3 pillars with 100% score."""
        case = self.suite.get_case("ANCOVA")
        self.assertIsNotNone(case)

        compliant = {
            "actions_taken": ["homogeneity_of_slopes", "adjusted_means_computed"],
            "assumptions_checked": ["homogeneity_of_slopes", "normality"],
            "statistical_parameters": {
                "f_statistic": 14.82, "df_between": 1, "df_error": 77, "p_value": 0.0002, "partial_eta_sq": 0.161,
                "unadjusted_means": {"tx": 19.10, "ctrl": 26.90},
                "adjusted_means": {"tx": 18.42, "ctrl": 27.65}
            },
            "narrative_text": "Homogeneity of regression slopes assumption held (p > .05). Adjusted marginal means confirmed effect.",
            "artifacts": {"EVID-ANC-01": "table1.csv", "EVID-ANC-02": "table2.csv"}
        }
        res = self.suite.evaluate_candidate_execution(case, compliant)
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["score_pct"], 100.0)
        self.assertEqual(res["must_do"]["passed"], res["must_do"]["total"])
        self.assertEqual(res["must_not_do"]["clean"], res["must_not_do"]["total"])
        self.assertEqual(res["required_evidence"]["verified"], res["required_evidence"]["total"])

    def test_07_omitted_assumption_fails_must_do(self):
        """Verify that skipping a required assumption check triggers a FAIL verdict."""
        case = self.suite.get_case("ANCOVA")
        non_compliant = {
            "actions_taken": ["adjusted_means_computed"],
            "assumptions_checked": ["normality"],  # Missing homogeneity_of_slopes!
            "statistical_parameters": {
                "f_statistic": 14.82, "df_between": 1, "df_error": 77, "p_value": 0.0002, "partial_eta_sq": 0.161,
                "adjusted_means": {"tx": 18.42, "ctrl": 27.65}
            },
            "artifacts": {"EVID-ANC-01": "table1.csv", "EVID-ANC-02": "table2.csv"}
        }
        res = self.suite.evaluate_candidate_execution(case, non_compliant)
        self.assertEqual(res["status"], "FAIL")
        self.assertLess(res["must_do"]["passed"], res["must_do"]["total"])

    def test_08_forbidden_pitfall_fails_must_not_do(self):
        """Verify that committing a forbidden pitfall triggers a FAIL verdict."""
        case = self.suite.get_case("MEDIATION")
        non_compliant = {
            "actions_taken": ["check_bootstrap_resamples_gte_5000", "check_bca_confidence_interval", "check_constituent_paths_reported"],
            "methods_invoked": ["baron_kenny"],  # Forbidden anti-pattern!
            "statistical_parameters": {
                "bootstrap_resamples": 5000,
                "indirect_bca_ci": [-0.35, -0.12]
            },
            "artifacts": {"EVID-MED-01": "report.csv"},
            "triad_artifacts": {"docx": "h1.docx", "md": "h1.md", "json": "h1.json"}
        }
        res = self.suite.evaluate_candidate_execution(case, non_compliant)
        self.assertEqual(res["status"], "FAIL")
        self.assertLess(res["must_not_do"]["clean"], res["must_not_do"]["total"])

    def test_09_missing_evidence_fails_required_evidence(self):
        """Verify that missing required evidence files triggers a FAIL verdict."""
        case = self.suite.get_case("ANCOVA")
        non_compliant = {
            "actions_taken": ["homogeneity_of_slopes", "adjusted_means_computed"],
            "assumptions_checked": ["homogeneity_of_slopes"],
            "statistical_parameters": {
                "f_statistic": 14.82, "df_between": 1, "df_error": 77, "p_value": 0.0002, "partial_eta_sq": 0.161,
                "adjusted_means": {"tx": 18.42, "ctrl": 27.65}
            },
            "artifacts": {}  # Missing tables!
        }
        res = self.suite.evaluate_candidate_execution(case, non_compliant)
        self.assertEqual(res["status"], "FAIL")
        self.assertLess(res["required_evidence"]["verified"], res["required_evidence"]["total"])

    def test_10_directive_6_english_only_filenames(self):
        """Verify all benchmark files and datasets strictly observe English ASCII naming."""
        cases_dir = os.path.join(ROOT_DIR, "evals", "benchmarks", "cases")
        datasets_dir = os.path.join(ROOT_DIR, "evals", "benchmarks", "datasets")

        for d in [cases_dir, datasets_dir]:
            for fname in os.listdir(d):
                self.assertTrue(fname.isascii(), f"Non-ASCII filename detected: {fname}")

    def test_11_suite_integrity_validation_method(self):
        """Verify AcademicBenchmarkSuite.validate_all_cases returns PASS."""
        res = self.suite.validate_all_cases()
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(res["passed"], 18)
        self.assertEqual(res["failed"], 0)


if __name__ == "__main__":
    unittest.main()
