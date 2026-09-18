#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_standalone_script_safety.py — Regression Test for Standalone Script Execution Safety

Tests that standalone statistical CLI scripts:
1. Enforce mode checks ('production', 'demo', 'test', 'dry_run').
2. Reject sample/demo/synthetic data in production mode with ProductionSampleFallbackBlockedError.
3. Allow sample data in test/demo mode.
4. Enforce AnalysisPlan APPROVED status when plan is provided.
5. Exit cleanly in dry_run mode without empirical calculation.
"""

import os
import sys
import json
import tempfile
import subprocess
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.script_execution_guard import (
    enforce_script_safety,
    ProductionSampleFallbackBlockedError,
    InvalidExecutionModeError,
    UnauthorizedAnalysisPlanError,
    is_sample_or_demo_data
)


class TestStandaloneScriptSafety(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_script_safety_")
        self.real_data = os.path.join(self.temp_dir, "empirical_data.csv")
        with open(self.real_data, "w") as f:
            f.write("id,x,y\n1,10,20\n2,15,25\n")

        self.sample_data = os.path.join(self.temp_dir, "sample_data_test.csv")
        with open(self.sample_data, "w") as f:
            f.write("id,x,y\n1,1,2\n2,3,4\n")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_sample_detection(self):
        self.assertTrue(is_sample_or_demo_data("data/examples/my_data.csv"))
        self.assertTrue(is_sample_or_demo_data("sample_burnout.xlsx"))
        self.assertTrue(is_sample_or_demo_data("mock_payload.json"))
        self.assertFalse(is_sample_or_demo_data(self.real_data))

    def test_production_mode_blocks_sample_data(self):
        with self.assertRaises(ProductionSampleFallbackBlockedError):
            enforce_script_safety(dataset_path=self.sample_data, mode="production")

    def test_test_mode_allows_sample_data(self):
        res = enforce_script_safety(dataset_path=self.sample_data, mode="test")
        self.assertEqual(res["execution_mode"], "test")
        self.assertTrue(res["is_sample"])
        self.assertTrue(len(res["sha256"]) > 0)

    def test_invalid_mode_raises(self):
        with self.assertRaises(InvalidExecutionModeError):
            enforce_script_safety(dataset_path=self.real_data, mode="invalid_mode")

    def test_plan_approval_enforcement(self):
        draft_plan = os.path.join(self.temp_dir, "plan_draft.json")
        with open(draft_plan, "w") as f:
            json.dump({"plan_id": "P1", "status": "DRAFT"}, f)

        with self.assertRaises(UnauthorizedAnalysisPlanError):
            enforce_script_safety(dataset_path=self.real_data, mode="production", plan_path=draft_plan)

        approved_plan = os.path.join(self.temp_dir, "plan_approved.json")
        with open(approved_plan, "w") as f:
            json.dump({"plan_id": "P2", "status": "APPROVED"}, f)

        res = enforce_script_safety(dataset_path=self.real_data, mode="production", plan_path=approved_plan)
        self.assertEqual(res["execution_mode"], "production")

    def test_cli_regression_script_blocks_sample_in_production(self):
        script = os.path.join(ROOT_DIR, ".agents", "skills", "regression", "scripts", "run_regression.py")
        proc = subprocess.run(
            [sys.executable, script, "--data", self.sample_data, "--dv", "y", "--ivs", "x", "--mode", "production"],
            capture_output=True,
            text=True
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("ProductionSampleFallbackBlockedError", proc.stderr + proc.stdout)

    def test_cli_sem_script_blocks_sample_in_production(self):
        script = os.path.join(ROOT_DIR, ".agents", "skills", "sem", "scripts", "run_sem.py")
        proc = subprocess.run(
            [sys.executable, script, "--data", self.sample_data, "--spec", "y ~ x", "--mode", "production"],
            capture_output=True,
            text=True
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("ProductionSampleFallbackBlockedError", proc.stderr + proc.stdout)

    def test_production_mode_requires_approved_plan(self):
        # Missing plan in production mode must raise UnauthorizedAnalysisPlanError
        with self.assertRaises(UnauthorizedAnalysisPlanError):
            enforce_script_safety(dataset_path=self.real_data, mode="production", plan_path=None)

    def test_cli_regression_script_requires_plan_in_production(self):
        script = os.path.join(ROOT_DIR, ".agents", "skills", "regression", "scripts", "run_regression.py")
        proc = subprocess.run(
            [sys.executable, script, "--data", self.real_data, "--dv", "y", "--ivs", "x", "--mode", "production"],
            capture_output=True,
            text=True
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("UnauthorizedAnalysisPlanError", proc.stderr + proc.stdout)

    def test_cli_sem_script_requires_plan_in_production(self):
        script = os.path.join(ROOT_DIR, ".agents", "skills", "sem", "scripts", "run_sem.py")
        proc = subprocess.run(
            [sys.executable, script, "--data", self.real_data, "--spec", "y ~ x", "--mode", "production"],
            capture_output=True,
            text=True
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("UnauthorizedAnalysisPlanError", proc.stderr + proc.stdout)


if __name__ == "__main__":
    unittest.main()
