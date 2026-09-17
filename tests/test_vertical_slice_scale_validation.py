#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_vertical_slice_scale_validation.py — End-to-End Scale Validation Vertical Slice Integration Test

Verifies the complete Scale Standardization & Psychometric Validation Pipeline (Stages V.1–V.9):
Raw Dataset (N=450, 20 items) → CVR/CVI Panel → Classical Item Analysis →
EFA Factor Extraction → CFA Model Fit & Standardized Loadings →
Construct Validity (AVE/CR/HTMT) → Reliability (Alpha/Omega/ICC) & Measurement Invariance →
Modern IRT (Samejima GRM & TIF) & ROC Diagnostics → Master Assembly & Defense Brief.
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


class TestVerticalSliceScaleValidation(unittest.TestCase):
    PROJECT_DIR = os.path.join(ROOT_DIR, "projects", "study_vertical_slice_scale_validation")
    STATE_DIR = os.path.join(PROJECT_DIR, "academic-state")
    OUTPUTS_DIR = os.path.join(STATE_DIR, "outputs")

    def test_01_dataset_integrity(self):
        """Raw dataset must exist and contain N=450 observations with 20 Likert items."""
        xlsx_path = os.path.join(self.PROJECT_DIR, "01_raw_inputs", "data_raw.xlsx")
        self.assertTrue(os.path.exists(xlsx_path), f"Dataset missing: {xlsx_path}")

        import pandas as pd
        df = pd.read_excel(xlsx_path)
        self.assertEqual(len(df), 450, "Sample size must be exactly 450")

        # Check gender balance
        self.assertIn("gender", df.columns)
        self.assertEqual(len(df[df["gender"] == 1]), 225, "Female sub-sample must have n=225")
        self.assertEqual(len(df[df["gender"] == 2]), 225, "Male sub-sample must have n=225")

        # Check 20 Likert items
        for i in range(1, 21):
            col = f"cav_{i}"
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].min() >= 1, f"Item {col} min must be >= 1")
            self.assertTrue(df[col].max() <= 5, f"Item {col} max must be <= 5")

    def test_02_academic_state_validity(self):
        """Academic state directory must satisfy all JSON schemas and return PASS."""
        report = asm.validate_state(self.PROJECT_DIR)
        self.assertEqual(report["overall_verdict"], "PASS", f"State validation failed: {report['errors']}")

    def test_03_stage_v1_content_validity_triad(self):
        """Stage V.1 CVR/CVI triad artifacts must exist and satisfy Lawshe/Lynn criteria."""
        for ext in [".docx", ".md", ".json"]:
            path = os.path.join(self.OUTPUTS_DIR, f"01_content_validity{ext}")
            self.assertTrue(os.path.exists(path), f"Missing Stage V.1 artifact: {path}")

        with open(os.path.join(self.OUTPUTS_DIR, "01_content_validity.json")) as f:
            data = json.load(f)

        self.assertEqual(data["expert_panel_size"], 12)
        self.assertEqual(data["lawshe_critical_cvr"], 0.56)
        self.assertEqual(data["cvr_pass_rate"], 100.0)
        self.assertGreaterEqual(data["s_cvi_ave"], 0.80)

    def test_04_stage_v2_item_analysis_triad(self):
        """Stage V.2 item analysis triad must exist and confirm discrimination power."""
        for ext in [".docx", ".md", ".json"]:
            path = os.path.join(self.OUTPUTS_DIR, f"02_item_analysis{ext}")
            self.assertTrue(os.path.exists(path), f"Missing Stage V.2 artifact: {path}")

        with open(os.path.join(self.OUTPUTS_DIR, "02_item_analysis.json")) as f:
            data = json.load(f)

        self.assertEqual(len(data["items"]), 20)
        for item in data["items"]:
            self.assertGreaterEqual(item["corrected_item_total_r"], 0.30)
            self.assertGreater(item["discrimination_t"], 10.0)
            self.assertEqual(item["discrimination_p"], "< .001")

    def test_05_stage_v3_efa_triad(self):
        """Stage V.3 EFA triad must demonstrate sampling adequacy and 2-factor simple structure."""
        for ext in [".docx", ".md", ".json"]:
            path = os.path.join(self.OUTPUTS_DIR, f"03_efa_results{ext}")
            self.assertTrue(os.path.exists(path), f"Missing Stage V.3 artifact: {path}")

        with open(os.path.join(self.OUTPUTS_DIR, "03_efa_results.json")) as f:
            data = json.load(f)

        self.assertGreater(data["kmo"], 0.80)
        self.assertEqual(data["bartlett_test"]["p_value"], "< .001")
        self.assertEqual(len(data["factors"]), 2)
        self.assertGreater(data["total_variance_explained"], 50.0)

    def test_06_stage_v4_cfa_triad(self):
        """Stage V.4 CFA triad must verify Hu & Bentler (1999) fit indices and factor loadings."""
        for ext in [".docx", ".md", ".json"]:
            path = os.path.join(self.OUTPUTS_DIR, f"04_cfa_results{ext}")
            self.assertTrue(os.path.exists(path), f"Missing Stage V.4 artifact: {path}")

        with open(os.path.join(self.OUTPUTS_DIR, "04_cfa_results.json")) as f:
            data = json.load(f)

        fit = data["fit_indices"]
        self.assertLessEqual(fit["chi2_df"], 3.0)
        self.assertGreaterEqual(fit["cfi"], 0.90)
        self.assertGreaterEqual(fit["tli"], 0.90)
        self.assertLessEqual(fit["rmsea"], 0.08)
        self.assertLessEqual(fit["srmr"], 0.08)

        for ld in data["standardized_loadings"]:
            self.assertGreaterEqual(ld["std_loading"], 0.50)
            self.assertGreater(ld["z"], 1.96)
            self.assertEqual(ld["p_value"], "< .001")

    def test_07_stage_v5_construct_validity_triad(self):
        """Stage V.5 construct validity must satisfy AVE >= 0.50, CR >= 0.70, and HTMT < 0.85."""
        for ext in [".docx", ".md", ".json"]:
            path = os.path.join(self.OUTPUTS_DIR, f"05_construct_validity{ext}")
            self.assertTrue(os.path.exists(path), f"Missing Stage V.5 artifact: {path}")

        with open(os.path.join(self.OUTPUTS_DIR, "05_construct_validity.json")) as f:
            data = json.load(f)

        self.assertTrue(data["convergent_validity"]["factor_1"]["ave_threshold_met"])
        self.assertTrue(data["convergent_validity"]["factor_1"]["cr_threshold_met"])
        self.assertTrue(data["convergent_validity"]["factor_2"]["ave_threshold_met"])
        self.assertTrue(data["convergent_validity"]["factor_2"]["cr_threshold_met"])
        self.assertTrue(data["discriminant_validity"]["fornell_larcker"]["fornell_larcker_met"])
        self.assertLess(data["discriminant_validity"]["htmt"]["htmt_ratio"], 0.85)

    def test_08_stage_v6_reliability_and_invariance_triad(self):
        """Stage V.6 reliability and invariance must establish alpha/omega and scalar invariance."""
        for ext in [".docx", ".md", ".json"]:
            path = os.path.join(self.OUTPUTS_DIR, f"06_reliability_inv{ext}")
            self.assertTrue(os.path.exists(path), f"Missing Stage V.6 artifact: {path}")

        with open(os.path.join(self.OUTPUTS_DIR, "06_reliability_inv.json")) as f:
            data = json.load(f)

        rel = data["reliability_coefficients"]
        self.assertGreaterEqual(rel["total_scale"]["cronbach_alpha"], 0.80)
        self.assertGreaterEqual(rel["total_scale"]["mcdonald_omega"], 0.80)
        self.assertGreaterEqual(rel["total_scale"]["retest_icc"], 0.75)

        inv = data["measurement_invariance_gender"]
        self.assertEqual(len(inv), 3)
        self.assertLessEqual(abs(inv[1]["delta_cfi"]), 0.010)
        self.assertLessEqual(abs(inv[2]["delta_cfi"]), 0.010)

    def test_09_stage_v7_irt_and_roc_triad(self):
        """Stage V.7 modern IRT and ROC must demonstrate high discrimination and clinical AUC."""
        for ext in [".docx", ".md", ".json"]:
            path = os.path.join(self.OUTPUTS_DIR, f"07_irt_roc{ext}")
            self.assertTrue(os.path.exists(path), f"Missing Stage V.7 artifact: {path}")

        with open(os.path.join(self.OUTPUTS_DIR, "07_irt_roc.json")) as f:
            data = json.load(f)

        self.assertGreaterEqual(data["irt_model_spec"]["mean_discrimination"], 1.70)
        roc = data["roc_diagnostics"]
        self.assertGreaterEqual(roc["auc"], 0.80)
        self.assertEqual(roc["optimal_cutoff"], 48.0)
        self.assertGreaterEqual(roc["sensitivity"], 80.0)
        self.assertGreaterEqual(roc["specificity"], 80.0)

    def test_10_stage_v8_master_assembled_package(self):
        """Stage V.8 master deliverables (DOCX, MD, Excel, PNGs) must exist and be fully populated."""
        docx_path = os.path.join(self.OUTPUTS_DIR, "Scale_Validation_Report.docx")
        md_path = os.path.join(self.OUTPUTS_DIR, "Scale_Validation_Report.md")
        xlsx_path = os.path.join(self.OUTPUTS_DIR, "psychometric_validation_matrix.xlsx")
        fig1_path = os.path.join(self.OUTPUTS_DIR, "scree_and_roc_plots.png")
        fig2_path = os.path.join(self.OUTPUTS_DIR, "irt_tif_and_ccc_plots.png")

        self.assertTrue(os.path.exists(docx_path))
        self.assertTrue(os.path.exists(md_path))
        self.assertTrue(os.path.exists(xlsx_path))
        self.assertTrue(os.path.exists(fig1_path))
        self.assertTrue(os.path.exists(fig2_path))

        # Check Excel 6 sheets
        import openpyxl
        wb = openpyxl.load_workbook(xlsx_path)
        expected_sheets = [
            "Overview & Metrics", "Item Analysis (CVR & CVI)",
            "EFA Factor Loadings", "CFA & Construct Validity",
            "IRT Graded Response Model", "Norms & ROC Cut-offs"
        ]
        for s in expected_sheets:
            self.assertIn(s, wb.sheetnames)

    def test_11_stage_v9_defense_brief_triad(self):
        """Stage V.9 defense brief must contain 4 scenarios and readiness score >= 95%."""
        for ext in [".docx", ".md", ".json"]:
            path = os.path.join(self.OUTPUTS_DIR, f"09_defense_brief{ext}")
            self.assertTrue(os.path.exists(path), f"Missing Stage V.9 artifact: {path}")

        with open(os.path.join(self.OUTPUTS_DIR, "09_defense_brief.json")) as f:
            data = json.load(f)

        self.assertEqual(len(data["committee_scenarios"]), 4)
        self.assertGreaterEqual(data["defense_readiness_score"], 95.0)
        self.assertEqual(data["verdict"], "SUPPORTED")

    def test_12_master_validator_suite(self):
        """Master validator suite must confirm overall PASS across all stage outputs."""
        report = run_suite(self.OUTPUTS_DIR)
        self.assertEqual(report["overall_verdict"], "PASS")


if __name__ == '__main__':
    unittest.main()
