#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_academic_state.py — Test suite for Academic State Management & Artifact Communication
Tests:
1. State directory initialization and structure
2. JSON Schema validation on all state artifacts
3. Decision recording and auditing
4. Stage advancement and project status
5. Real study state compliance (projects/study_act_burnout)
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))
import academic_state_manager as sm


class TestAcademicState(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="academic_state_test_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_init_structure(self):
        """Verify state directory hierarchy initialization."""
        res = sm.init_state(self.temp_dir, title="Test Project", methodology="sem", n=250)
        self.assertEqual(res["status"], "SUCCESS")

        state_dir = os.path.join(self.temp_dir, "academic-state")
        self.assertTrue(os.path.isdir(state_dir))
        self.assertTrue(os.path.isdir(os.path.join(state_dir, "data")))
        self.assertTrue(os.path.isdir(os.path.join(state_dir, "analysis")))
        self.assertTrue(os.path.isdir(os.path.join(state_dir, "validation")))
        self.assertTrue(os.path.isdir(os.path.join(state_dir, "outputs")))

        for expected in ["project.json", "requirements.json", "analysis_plan.json", "decisions.json"]:
            self.assertTrue(os.path.exists(os.path.join(state_dir, expected)), f"Missing {expected}")

    def test_02_schema_validation_initialized(self):
        """Initialized baseline files must pass schema validation."""
        sm.init_state(self.temp_dir, title="Schema Test", methodology="sem", n=200)
        val = sm.validate_state(self.temp_dir)
        self.assertEqual(val["overall_verdict"], "PASS", f"Validation failed: {val.get('errors')}")

    def test_03_record_decision(self):
        """Recording a decision appends an auditable record."""
        sm.init_state(self.temp_dir, title="Decision Test", methodology="sem", n=150)
        res = sm.record_decision(
            self.temp_dir,
            category="statistical_modeling",
            decision="Use WLSMV estimator for ordinal Likert indicators",
            rationale="Robust to non-normality and discrete categories",
            agent="statistical-expert"
        )
        self.assertEqual(res["status"], "RECORDED")
        self.assertTrue(res["decision_id"].startswith("DEC-"))

        # Check file directly
        with open(os.path.join(self.temp_dir, "academic-state", "decisions.json"), "r") as f:
            data = json.load(f)
        self.assertGreaterEqual(len(data["decisions"]), 2)

        # Ensure still schema-valid
        val = sm.validate_state(self.temp_dir)
        self.assertEqual(val["overall_verdict"], "PASS")

    def test_04_set_stage(self):
        """Updating stage gate enforces fail-closed DirectStageMutationBlockedError in production and works in test mode."""
        sm.init_state(self.temp_dir, title="Stage Test", methodology="sem", n=150)
        
        # In production mode (default), direct mutation is strictly blocked
        with self.assertRaises(sm.DirectStageMutationBlockedError):
            sm.set_stage(self.temp_dir, stage="04_bivariate_correlations", status="in_progress", mode="production")

        # In explicit test mode, direct mutation is allowed for testing
        res = sm.set_stage(self.temp_dir, stage="04_bivariate_correlations", status="in_progress", mode="test")
        self.assertEqual(res["status"], "UPDATED")
        self.assertEqual(res["current_stage"], "04_bivariate_correlations")

        summary = sm.get_status_summary(self.temp_dir)
        self.assertEqual(summary["current_stage"], "04_bivariate_correlations")

    def test_05_study_act_burnout_compliance(self):
        """The real study academic-state must be 100% valid against all schemas."""
        study_path = os.path.join(ROOT_DIR, "projects", "study_act_burnout")
        val = sm.validate_state(study_path)
        self.assertEqual(val["overall_verdict"], "PASS", f"Study state errors: {val.get('errors')}")
        self.assertGreaterEqual(len(val["validated_files"]), 8)


if __name__ == "__main__":
    unittest.main()
