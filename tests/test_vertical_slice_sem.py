#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_vertical_slice_sem.py — End-to-End SEM Vertical Slice Integration Test

Verifies the complete Structural Equation Modeling vertical slice pipeline:
Dataset → Data Audit → CFA Measurement Model → Macro SEM (11 Fit Indices) → Direct Structural Paths → Bootstrap Mediation → Validation → Triad Artifacts
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

sys.path.insert(0, os.path.join(ROOT_DIR, ".agents"))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, "validators"))

from validators.run_all_validators import run_suite
from validators.data_integrity.validator import validate_data
from validators.numerical_consistency.validator import validate_numbers
from validators.reporting_consistency.validator import validate_reporting
from validators.result_consistency.validator import validate_results
import academic_state_manager as asm


class TestVerticalSliceSEM(unittest.TestCase):
    cand_proj = os.path.join(ROOT_DIR, "tests", "fixtures", "study_vertical_slice_sem")
    PROJECT_DIR = cand_proj if os.path.isdir(cand_proj) else os.path.join(ROOT_DIR, "projects", "study_vertical_slice_sem")
    STATE_DIR = os.path.join(PROJECT_DIR, "academic-state")
    OUTPUTS_DIR = os.path.join(STATE_DIR, "outputs")

    def test_01_dataset_integrity(self):
        """Raw dataset must exist and be structurally valid (N=250)."""
        xlsx_path = os.path.join(self.PROJECT_DIR, "01_raw_inputs", "data_raw.xlsx")
        self.assertTrue(os.path.exists(xlsx_path), f"Dataset missing: {xlsx_path}")

        import pandas as pd
        df = pd.read_excel(xlsx_path)
        self.assertEqual(len(df), 250, "Dataset sample size must be 250")
        for i in range(1, 6):
            self.assertIn(f"mind_{i}", df.columns)
            self.assertIn(f"flex_{i}", df.columns)
            self.assertIn(f"well_{i}", df.columns)

    def test_02_data_audit_and_integrity_validation(self):
        """Data audit report must be valid and pass data integrity validator."""
        audit_file = os.path.join(self.STATE_DIR, "data", "data_quality.json")
        self.assertTrue(os.path.exists(audit_file), f"Audit report missing: {audit_file}")

        with open(audit_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data.get("sample_n") or data.get("total_rows") or data.get("sample_size"), 250)
        self.assertEqual(data.get("missing_cells"), 0)

        res = validate_data(audit_file)
        self.assertEqual(res["verdict"], "PASS")

    def test_03_cfa_measurement_model_validity(self):
        """CFA analysis must confirm construct reliability and fit indices."""
        cfa_file = os.path.join(self.STATE_DIR, "analysis", "cfa.json")
        self.assertTrue(os.path.exists(cfa_file), f"CFA artifact missing: {cfa_file}")

        with open(cfa_file, "r", encoding="utf-8") as f:
            cfa_data = json.load(f)

        self.assertEqual(cfa_data.get("sample_size"), 250)
        self.assertIn("factors", cfa_data)
        self.assertEqual(len(cfa_data["factors"]), 3)

        for factor in cfa_data["factors"]:
            self.assertIn("composite_reliability", factor)
            self.assertIn("average_variance_extracted", factor)
            self.assertGreaterEqual(factor["composite_reliability"], 0.70)
            self.assertEqual(len(factor["items"]), 5)

    def test_04_sem_macro_fit_indices(self):
        """SEM analysis must report all 11 fit indices evaluated against Hu & Bentler cutoffs."""
        sem_file = os.path.join(self.STATE_DIR, "analysis", "sem.json")
        self.assertTrue(os.path.exists(sem_file), f"SEM artifact missing: {sem_file}")

        with open(sem_file, "r", encoding="utf-8") as f:
            sem_data = json.load(f)

        fit = sem_data.get("fit_indices", {})
        self.assertIn("chi2", fit)
        self.assertIn("df", fit)
        self.assertIn("chi2_df", fit)
        self.assertIn("cfi", fit)
        self.assertIn("tli", fit)
        self.assertIn("rmsea", fit)
        self.assertIn("srmr", fit)

        self.assertLessEqual(fit["chi2_df"], 3.0)
        self.assertGreaterEqual(fit["cfi"], 0.95)
        self.assertLessEqual(fit["rmsea"], 0.05)
        self.assertIn(fit["model_fit_verdict"], ["EXCELLENT", "ACCEPTABLE"])

    def test_05_structural_paths_and_bootstrap_mediation(self):
        """SEM direct paths and bootstrap mediation confidence intervals must be valid."""
        sem_file = os.path.join(self.STATE_DIR, "analysis", "sem.json")
        with open(sem_file, "r", encoding="utf-8") as f:
            sem_data = json.load(f)

        paths = sem_data.get("paths", [])
        self.assertGreaterEqual(len(paths), 3)

        # Check indirect effects
        ind_effects = sem_data.get("indirect_effects", [])
        self.assertGreaterEqual(len(ind_effects), 1)
        ind = ind_effects[0]
        self.assertEqual(ind["bootstrap_samples"], 5000)
        self.assertGreater(ind["ci_lower"], 0.0, "Bootstrap CI must exclude zero for significant mediation")
        self.assertTrue(ind["significant"])

    def test_06_triad_artifact_invariant_stages(self):
        """Stages 05_macro_model, 06_hypothesis_1, and 07_hypothesis_2 must each produce complete triad."""
        stages = [
            "05_macro_model",
            "06_hypothesis_1_direct_path",
            "07_hypothesis_2_mediation"
        ]

        for stage in stages:
            docx_path = os.path.join(self.OUTPUTS_DIR, f"{stage}.docx")
            md_path = os.path.join(self.OUTPUTS_DIR, f"{stage}.md")
            json_path = os.path.join(self.OUTPUTS_DIR, f"{stage}.json")

            self.assertTrue(os.path.exists(docx_path), f"Missing triad DOCX: {docx_path}")
            self.assertTrue(os.path.exists(md_path), f"Missing triad MD: {md_path}")
            self.assertTrue(os.path.exists(json_path), f"Missing triad JSON: {json_path}")

            self.assertGreater(os.path.getsize(docx_path), 5000)
            self.assertGreater(os.path.getsize(md_path), 200)
            self.assertGreater(os.path.getsize(json_path), 100)

    def test_07_deterministic_validators_overall_pass(self):
        """Master validator suite must report PASS across all stage outputs."""
        report = run_suite(self.OUTPUTS_DIR)
        self.assertEqual(report["overall_verdict"], "PASS", f"Suite failed: {report}")

        for res in report["results"]:
            self.assertNotEqual(res["verdict"], "FAIL", f"Sub-validator failed: {res}")

    def test_08_academic_state_schema_conformity(self):
        """All state files in academic-state must conform 100% to JSON schemas."""
        report = asm.validate_state(self.PROJECT_DIR)
        self.assertEqual(report["overall_verdict"], "PASS", f"State validation failed: {report.get('errors')}")
        self.assertGreaterEqual(len(report["validated_files"]), 8)


if __name__ == "__main__":
    unittest.main()
