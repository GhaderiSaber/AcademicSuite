#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_vertical_slice_regression.py — End-to-End Vertical Slice Integration Test

Verifies the complete vertical slice pipeline:
Dataset → Data Audit → Descriptives → Reliability → Regression → Validation → Chapter 4 Triad Artifacts
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
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, "validators"))

from validators.run_all_validators import run_suite
from validators.data_integrity.validator import validate_data
from validators.numerical_consistency.validator import validate_numbers
from validators.reporting_consistency.validator import validate_reporting
from validators.result_consistency.validator import validate_results
import academic_state_manager as asm


class TestVerticalSliceRegression(unittest.TestCase):
    PROJECT_DIR = os.path.join(ROOT_DIR, "projects", "study_vertical_slice_regression")
    STATE_DIR = os.path.join(PROJECT_DIR, "academic-state")
    OUTPUTS_DIR = os.path.join(STATE_DIR, "outputs")

    def test_01_dataset_integrity(self):
        """Raw dataset must exist and be structurally valid."""
        xlsx_path = os.path.join(self.PROJECT_DIR, "01_raw_inputs", "data_raw.xlsx")
        self.assertTrue(os.path.exists(xlsx_path), f"Dataset missing: {xlsx_path}")

        import pandas as pd
        df = pd.read_excel(xlsx_path)
        self.assertEqual(len(df), 100, "Dataset sample size must be 100")
        self.assertIn("workplace_stress", df.columns)
        self.assertIn("psychological_flexibility", df.columns)
        self.assertIn("job_burnout", df.columns)

    def test_02_data_audit_and_integrity_validation(self):
        """Data audit report must be valid and pass data integrity validator."""
        audit_file = os.path.join(self.STATE_DIR, "data", "data_quality.json")
        self.assertTrue(os.path.exists(audit_file), f"Audit report missing: {audit_file}")

        with open(audit_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["sample_n"], 100)
        self.assertEqual(data["missing_rate"], 0.0)
        self.assertEqual(data["status"], "AUDIT_PASSED")

        val_res = validate_data(audit_file)
        self.assertEqual(val_res["verdict"], "PASS")
        self.assertEqual(len(val_res["errors"]), 0)

    def test_03_descriptive_statistics(self):
        """Descriptive statistics must report valid parameters for all study variables."""
        desc_file = os.path.join(self.STATE_DIR, "analysis", "descriptive.json")
        self.assertTrue(os.path.exists(desc_file), f"Descriptives missing: {desc_file}")

        with open(desc_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["sample_size"], 100)
        var_names = [v["name"] for v in data["variables"]]
        self.assertIn("workplace_stress", var_names)
        self.assertIn("psychological_flexibility", var_names)
        self.assertIn("job_burnout", var_names)

        for v in data["variables"]:
            self.assertGreater(v["mean"], 1.0)
            self.assertLess(v["mean"], 5.0)
            self.assertGreater(v["sd"], 0.2)

    def test_04_scale_reliability(self):
        """Psychometric scales must demonstrate satisfactory internal consistency."""
        rel_file = os.path.join(self.STATE_DIR, "analysis", "reliability.json")
        self.assertTrue(os.path.exists(rel_file), f"Reliability missing: {rel_file}")

        with open(rel_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["sample_size"], 100)
        scale_names = [s["scale_name"] for s in data["scales"]]
        self.assertIn("Workplace Stress", scale_names)
        self.assertIn("Psychological Flexibility", scale_names)
        self.assertIn("Job Burnout", scale_names)

        # Stress and Burnout alphas must exceed standard 0.70 benchmark
        stress_scale = next(s for s in data["scales"] if s["scale_name"] == "Workplace Stress")
        self.assertGreaterEqual(stress_scale["cronbach_alpha"], 0.70)
        burnout_scale = next(s for s in data["scales"] if s["scale_name"] == "Job Burnout")
        self.assertGreaterEqual(burnout_scale["cronbach_alpha"], 0.70)

    def test_05_multiple_regression_results(self):
        """Regression model must produce statistically significant parameters."""
        reg_file = os.path.join(self.STATE_DIR, "analysis", "regression.json")
        self.assertTrue(os.path.exists(reg_file), f"Regression missing: {reg_file}")

        with open(reg_file, "r", encoding="utf-8") as f:
            reg = json.load(f)

        self.assertEqual(reg["n"], 100)
        self.assertEqual(reg["dv"], "job_burnout")
        self.assertGreater(reg["r2"], 0.30)
        self.assertGreater(reg["f_stat"], 20.0)
        self.assertEqual(reg["f_pvalue"], "< .001")

        # Check predictors
        stress_coef = next(c for c in reg["coefficients"] if c["predictor"] == "workplace_stress")
        self.assertGreater(stress_coef["beta"], 0.30)
        self.assertGreater(stress_coef["t"], 3.0)

        flex_coef = next(c for c in reg["coefficients"] if c["predictor"] == "psychological_flexibility")
        self.assertLess(flex_coef["beta"], -0.20)
        self.assertLess(flex_coef["t"], -3.0)

    def test_06_triad_artifacts_exist(self):
        """Chapter 4 subsection must generate synchronized triad (.docx, .md, .json) on disk."""
        base_name = "06_hypothesis_1_regression"
        json_path = os.path.join(self.OUTPUTS_DIR, f"{base_name}.json")
        md_path = os.path.join(self.OUTPUTS_DIR, f"{base_name}.md")
        docx_path = os.path.join(self.OUTPUTS_DIR, f"{base_name}.docx")

        self.assertTrue(os.path.exists(json_path), f"JSON triad missing: {json_path}")
        self.assertTrue(os.path.exists(md_path), f"MD triad missing: {md_path}")
        self.assertTrue(os.path.exists(docx_path), f"DOCX triad missing: {docx_path}")

        # Verify sizes
        self.assertGreater(os.path.getsize(json_path), 200)
        self.assertGreater(os.path.getsize(md_path), 500)
        self.assertGreater(os.path.getsize(docx_path), 1000)

    def test_07_deterministic_reporting_and_results_validation(self):
        """Artifacts must satisfy all reporting and result consistency checks."""
        suite_rep = run_suite(self.OUTPUTS_DIR)
        self.assertEqual(suite_rep["overall_verdict"], "PASS", f"Validator suite failed: {suite_rep}")

        # Direct validator checks
        md_path = os.path.join(self.OUTPUTS_DIR, "06_hypothesis_1_regression.md")
        rep_res = validate_reporting(md_path)
        self.assertEqual(rep_res["verdict"], "PASS")

        json_path = os.path.join(self.OUTPUTS_DIR, "06_hypothesis_1_regression.json")
        num_res = validate_numbers(json_path)
        self.assertEqual(num_res["verdict"], "PASS")

        res_check = validate_results(json_path, md_path)
        self.assertEqual(res_check["verdict"], "PASS")

    def test_08_academic_state_schema_compliance(self):
        """Entire academic-state directory must pass schema validation with PASS."""
        res = asm.validate_state(self.STATE_DIR)
        self.assertEqual(res["overall_verdict"], "PASS", f"Schema errors: {res.get('errors')}")
        self.assertEqual(len(res["errors"]), 0)

    def test_09_three_table_standard_compliance(self):
        """Regression deliverable must strictly comply with the institutional 3-Table Standard."""
        md_path = os.path.join(self.OUTPUTS_DIR, "06_hypothesis_1_regression.md")
        json_path = os.path.join(self.OUTPUTS_DIR, "06_hypothesis_1_regression.json")

        with open(md_path, "r", encoding="utf-8") as f:
            md_text = f.read()
        with open(json_path, "r", encoding="utf-8") as f:
            js_data = json.load(f)

        # 1. JSON must contain all 3 tables
        self.assertTrue(js_data.get("three_table_standard"))
        self.assertIn("table_1_correlations", js_data)
        self.assertIn("table_2_model_summary_anova", js_data)
        self.assertIn("table_3_coefficients", js_data)

        # 2. Markdown narrative must contain all 3 tables with appropriate headers
        self.assertIn("جدول ۱", md_text)
        self.assertIn("جدول ۲", md_text)
        self.assertIn("جدول ۳", md_text)

        # Table 1: Bivariate correlations
        self.assertIn("ماتریس همبستگی پیرسون", md_text)
        # Table 2: Model Summary & ANOVA
        self.assertIn("خلاصه مدل رگرسیون", md_text)
        self.assertIn("مجموع مجذورات", md_text)
        self.assertIn("دوربین-واتسون", md_text)
        # Table 3: Coefficients & Collinearity
        self.assertIn("ضرایب رگرسیون چندگانه", md_text)
        self.assertIn("تولرانس", md_text)
        self.assertIn("VIF", md_text)

        # 3. Validator must confirm PASS
        rep = validate_reporting(md_path)
        self.assertEqual(rep["verdict"], "PASS")


if __name__ == "__main__":
    unittest.main()
