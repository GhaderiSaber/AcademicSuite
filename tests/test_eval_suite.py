#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_eval_suite.py — Unit tests for the Academic Suite Permanent Evaluation Corpus (evals/)

Validates that all 8 domains (descriptive, reliability, regression, mediation, cfa, sem, network, writing)
strictly follow the evaluation schema, have verified input fixtures, and execute cleanly through run_eval_suite.py.
"""

import os
import sys
import json
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "evals"))

from evals.run_eval_suite import load_schema, discover_test_cases, validate_test_cases, run_benchmark_suite


class TestEvalSuite(unittest.TestCase):
    EVALS_DIR = os.path.join(ROOT_DIR, "evals")
    REQUIRED_DOMAINS = [
        "descriptive", "reliability", "regression", "mediation",
        "cfa", "sem", "network", "writing"
    ]

    def test_01_schema_exists_and_is_valid(self):
        schema = load_schema()
        self.assertIsInstance(schema, dict)
        self.assertEqual(schema.get("title"), "AcademicSuiteEvaluationTestCaseSchema")
        self.assertIn("required", schema)
        
        # Check all 8 required fields
        required_fields = [
            "INPUT", "EXPECTED_ANALYSIS", "EXPECTED_N", "EXPECTED_VARIABLES",
            "EXPECTED_KEY_STATISTICS", "EXPECTED_TABLES",
            "EXPECTED_INTERPRETATION_CONSTRAINTS", "EXPECTED_VALIDATION"
        ]
        for field in required_fields:
            self.assertIn(field, schema["required"], f"Schema missing required field: {field}")

    def test_02_all_8_domains_have_test_cases(self):
        cases = discover_test_cases()
        self.assertGreaterEqual(len(cases), 8, f"Expected at least 8 test cases, found {len(cases)}")

        found_domains = set(c["domain"] for c in cases)
        for dom in self.REQUIRED_DOMAINS:
            self.assertIn(dom, found_domains, f"Domain missing from test cases: {dom}")

    def test_03_all_test_cases_conform_to_schema_and_have_data(self):
        schema = load_schema()
        cases = discover_test_cases()
        summary = validate_test_cases(schema, cases)
        self.assertEqual(summary["verdict"], "PASS", f"Validation errors: {summary.get('errors')}")
        self.assertEqual(summary["valid_cases"], len(cases))
        self.assertEqual(len(summary["errors"]), 0)

    def test_04_eval_runner_produces_passing_benchmark(self):
        report = run_benchmark_suite(version_name="Academic Suite v2 (Unit Test)")
        self.assertEqual(report["overall_verdict"], "PASS")
        self.assertGreaterEqual(report["overall_benchmark_score"], 95.0)
        self.assertEqual(report["passed_test_cases"], report["total_test_cases"])
        self.assertGreaterEqual(report["total_test_cases"], 8)

    def test_05_benchmark_reports_exist_on_disk(self):
        json_rep = os.path.join(self.EVALS_DIR, "results", "benchmark_report.json")
        md_rep = os.path.join(self.EVALS_DIR, "results", "benchmark_report.md")
        self.assertTrue(os.path.exists(json_rep), f"Missing JSON report: {json_rep}")
        self.assertTrue(os.path.exists(md_rep), f"Missing MD report: {md_rep}")
        self.assertGreater(os.path.getsize(json_rep), 500)
        self.assertGreater(os.path.getsize(md_rep), 500)


if __name__ == '__main__':
    unittest.main()
