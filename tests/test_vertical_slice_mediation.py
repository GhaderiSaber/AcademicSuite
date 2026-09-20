#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_vertical_slice_mediation.py — End-to-End Serial Mediation (PROCESS Model 6) Vertical Slice Integration Test

Verifies the complete serial two-mediator bootstrap mediation vertical slice pipeline:
Dataset (N=300) → Data Audit → 3 Serial Regression Equations → Bootstrap Mediation (5,000 resamples) → Validation → Triad Artifacts
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


class TestVerticalSliceMediation(unittest.TestCase):
    cand_proj = os.path.join(ROOT_DIR, "tests", "fixtures", "study_vertical_slice_mediation")
    PROJECT_DIR = cand_proj if os.path.isdir(cand_proj) else os.path.join(ROOT_DIR, "projects", "study_vertical_slice_mediation")
    STATE_DIR = os.path.join(PROJECT_DIR, "academic-state")
    OUTPUTS_DIR = os.path.join(STATE_DIR, "outputs")

    def test_01_dataset_integrity(self):
        """Raw dataset must exist and contain N=300 observations and all required instruments."""
        xlsx_path = os.path.join(self.PROJECT_DIR, "01_raw_inputs", "data_raw.xlsx")
        self.assertTrue(os.path.exists(xlsx_path), f"Dataset missing: {xlsx_path}")

        import pandas as pd
        df = pd.read_excel(xlsx_path)
        self.assertEqual(len(df), 300, "Sample size must be exactly 300")

        # Check composite scales
        composites = ["trans_leadership", "psych_safety", "work_engagement", "innovative_behavior"]
        for comp in composites:
            self.assertIn(comp, df.columns, f"Missing composite variable: {comp}")

        # Check Likert items
        for i in range(1, 6):
            self.assertIn(f"lead_{i}", df.columns)
            self.assertIn(f"safe_{i}", df.columns)
            self.assertIn(f"eng_{i}", df.columns)
            self.assertIn(f"innov_{i}", df.columns)

    def test_02_data_audit_and_integrity_validation(self):
        """Data audit report must be present and pass data integrity validation."""
        audit_file = os.path.join(self.STATE_DIR, "data", "data_quality.json")
        self.assertTrue(os.path.exists(audit_file), f"Audit report missing: {audit_file}")

        with open(audit_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data.get("sample_n") or data.get("total_rows"), 300)
        self.assertEqual(data.get("missing_cells"), 0)
        self.assertEqual(data.get("quality_verdict"), "PASS")

        res = validate_data(audit_file)
        self.assertEqual(res["verdict"], "PASS")

    def test_03_serial_mediation_model6_estimation(self):
        """Model 6 estimation must report all 3 equations, effects decomposition, and bootstrap CIs."""
        stats_file = os.path.join(self.STATE_DIR, "analysis", "mediation_model6.json")
        self.assertTrue(os.path.exists(stats_file), f"Mediation stats missing: {stats_file}")

        with open(stats_file, "r", encoding="utf-8") as f:
            stats = json.load(f)

        self.assertEqual(stats.get("model_type"), "PROCESS Model 6 (Serial Two-Mediator Mediation)")
        self.assertEqual(stats.get("sample_size"), 300)
        self.assertEqual(stats.get("bootstrap_samples"), 5000)

        # Check equations
        eqs = stats.get("regression_equations", {})
        self.assertIn("equation_1_mediator_1", eqs)
        self.assertIn("equation_2_mediator_2", eqs)
        self.assertIn("equation_3_outcome_y", eqs)

        # Eq 1: M1 ~ X
        self.assertAlmostEqual(eqs["equation_1_mediator_1"]["coefficients"]["trans_leadership"]["b"], 0.425, places=2)
        self.assertAlmostEqual(eqs["equation_1_mediator_1"]["r2"], 0.204, places=2)

        # Eq 2: M2 ~ X + M1
        self.assertAlmostEqual(eqs["equation_2_mediator_2"]["coefficients"]["trans_leadership"]["b"], 0.266, places=2)
        self.assertAlmostEqual(eqs["equation_2_mediator_2"]["coefficients"]["psych_safety"]["b"], 0.353, places=2)
        self.assertAlmostEqual(eqs["equation_2_mediator_2"]["r2"], 0.292, places=2)

        # Eq 3: Y ~ X + M1 + M2
        self.assertAlmostEqual(eqs["equation_3_outcome_y"]["coefficients"]["trans_leadership"]["b"], 0.225, places=2)
        self.assertAlmostEqual(eqs["equation_3_outcome_y"]["coefficients"]["psych_safety"]["b"], 0.283, places=2)
        self.assertAlmostEqual(eqs["equation_3_outcome_y"]["coefficients"]["work_engagement"]["b"], 0.331, places=2)
        self.assertAlmostEqual(eqs["equation_3_outcome_y"]["r2"], 0.381, places=2)

        # Check effects
        eff = stats.get("effects_decomposition", {})
        total_c = eff.get("total_effect_c", {}).get("b")
        direct_cp = eff.get("direct_effect_c_prime", {}).get("b")
        ind_list = eff.get("indirect_effects", [])
        total_ind_obj = eff.get("total_indirect_effect", {})

        self.assertAlmostEqual(total_c, 0.483, places=2)
        self.assertAlmostEqual(direct_cp, 0.225, places=2)
        self.assertEqual(len(ind_list), 4)

        ind1 = ind_list[0]["point_estimate_b"]
        ind2 = ind_list[1]["point_estimate_b"]
        ind3 = ind_list[2]["point_estimate_b"]
        total_ind = ind_list[3]["point_estimate_b"]

        self.assertAlmostEqual(ind1, 0.120, places=2)
        self.assertAlmostEqual(ind2, 0.088, places=2)
        self.assertAlmostEqual(ind3, 0.050, places=2)
        self.assertAlmostEqual(total_ind, 0.258, places=2)

        # Verify mathematical identity: c = c' + ab
        self.assertAlmostEqual(direct_cp + total_ind, total_c, places=2)

        # Verify bootstrap confidence intervals exclude zero
        for item in ind_list:
            ci_low = item["ci_lower"]
            ci_high = item["ci_upper"]
            self.assertGreater(ci_low, 0.0, f"{item.get('label', 'total')} CI lower bound must be > 0")
            self.assertGreater(ci_high, ci_low, f"{item.get('label', 'total')} CI upper bound must exceed lower bound")
            self.assertTrue(item["significant"], f"{item.get('label', 'total')} must be significant")

    def test_04_triad_artifact_invariant_stages(self):
        """Stages 05_mediation_macro, 06, 07, and 08 must each produce complete synchronized triads."""
        stages = [
            "05_mediation_macro",
            "06_hypothesis_1_ind1",
            "07_hypothesis_2_ind2",
            "08_hypothesis_3_serial"
        ]

        for stage in stages:
            docx_path = os.path.join(self.OUTPUTS_DIR, f"{stage}.docx")
            md_path = os.path.join(self.OUTPUTS_DIR, f"{stage}.md")
            json_path = os.path.join(self.OUTPUTS_DIR, f"{stage}.json")

            self.assertTrue(os.path.exists(docx_path), f"Missing triad DOCX: {docx_path}")
            self.assertTrue(os.path.exists(md_path), f"Missing triad MD: {md_path}")
            self.assertTrue(os.path.exists(json_path), f"Missing triad JSON: {json_path}")

            self.assertGreater(os.path.getsize(docx_path), 5000, f"DOCX file {docx_path} is too small")
            self.assertGreater(os.path.getsize(md_path), 200, f"MD file {md_path} is too small")
            self.assertGreater(os.path.getsize(json_path), 100, f"JSON file {json_path} is too small")

    def test_05_deterministic_validators_overall_pass(self):
        """Master validator suite must report PASS across all stage outputs."""
        report = run_suite(self.OUTPUTS_DIR)
        self.assertEqual(report["overall_verdict"], "PASS", f"Suite failed: {report}")

        for res in report["results"]:
            self.assertNotEqual(res["verdict"], "FAIL", f"Sub-validator failed: {res}")

    def test_06_academic_state_schema_conformity(self):
        """All state files in academic-state must conform 100% to JSON schemas."""
        report = asm.validate_state(self.PROJECT_DIR)
        self.assertEqual(report["overall_verdict"], "PASS", f"State validation failed: {report.get('errors')}")
        self.assertGreaterEqual(len(report["validated_files"]), 9)


if __name__ == "__main__":
    unittest.main()
