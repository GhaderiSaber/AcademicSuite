#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_vertical_slice_moderation.py — End-to-End Moderation & Conditional Process Analysis Integration Test

Verifies the complete Moderation (PROCESS Model 1) and First-Stage Moderated Mediation (PROCESS Model 7) pipeline:
Dataset (N=320) → Data Audit → Hierarchical Regression → Simple Slopes & Johnson-Neyman →
Bootstrap Moderated Mediation (5,000 resamples) → Master Validators → Synchronized Triad Artifacts
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


class TestVerticalSliceModeration(unittest.TestCase):
    cand_proj = os.path.join(ROOT_DIR, "tests", "fixtures", "study_vertical_slice_moderation")
    PROJECT_DIR = cand_proj if os.path.isdir(cand_proj) else os.path.join(ROOT_DIR, "projects", "study_vertical_slice_moderation")
    STATE_DIR = os.path.join(PROJECT_DIR, "academic-state")
    OUTPUTS_DIR = os.path.join(STATE_DIR, "outputs")

    def test_01_dataset_integrity(self):
        """Raw dataset must exist and contain N=320 observations and all required instruments."""
        xlsx_path = os.path.join(self.PROJECT_DIR, "01_raw_inputs", "data_raw.xlsx")
        self.assertTrue(os.path.exists(xlsx_path), f"Dataset missing: {xlsx_path}")

        import pandas as pd
        df = pd.read_excel(xlsx_path)
        self.assertEqual(len(df), 320, "Sample size must be exactly 320")

        # Check composite scales
        composites = ["job_demands", "psy_capital", "emotional_exhaustion", "turnover_intention"]
        for comp in composites:
            self.assertIn(comp, df.columns, f"Missing composite variable: {comp}")

        # Check Likert items
        for i in range(1, 6):
            self.assertIn(f"dem_{i}", df.columns)
            self.assertIn(f"cap_{i}", df.columns)
            self.assertIn(f"exh_{i}", df.columns)
            self.assertIn(f"turn_{i}", df.columns)

    def test_02_data_audit_and_integrity_validation(self):
        """Data audit report must be present and pass data integrity validation."""
        audit_file = os.path.join(self.STATE_DIR, "data", "data_quality.json")
        self.assertTrue(os.path.exists(audit_file), f"Audit report missing: {audit_file}")

        with open(audit_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data.get("sample_n") or data.get("total_rows"), 320)
        self.assertEqual(data.get("missing_cells"), 0)
        self.assertEqual(data.get("quality_verdict"), "PASS")

        res = validate_data(audit_file)
        self.assertEqual(res["verdict"], "PASS")

    def test_03_moderation_model1_hierarchical_estimation(self):
        """Model 1 estimation must report hierarchical steps, delta R2, simple slopes, and JN points."""
        stats_file = os.path.join(self.STATE_DIR, "analysis", "moderation_model1.json")
        self.assertTrue(os.path.exists(stats_file), f"Moderation stats missing: {stats_file}")

        with open(stats_file, "r", encoding="utf-8") as f:
            stats = json.load(f)

        self.assertEqual(stats.get("model_type"), "PROCESS Model 1 (Simple Moderation)")
        self.assertEqual(stats.get("sample_size"), 320)

        # Hierarchical models
        h_models = stats.get("hierarchical_models", {})
        step1 = h_models.get("step1_main_effects", {})
        step2 = h_models.get("step2_interaction", {})
        comp = h_models.get("model_comparison", {})

        self.assertAlmostEqual(step1.get("r2"), 0.333, places=2)
        self.assertAlmostEqual(step2.get("r2"), 0.361, places=2)
        self.assertAlmostEqual(comp.get("delta_r2"), 0.028, places=2)
        self.assertGreater(comp.get("f_change"), 10.0)
        self.assertTrue(comp.get("significant"))

        # Interaction coefficient
        coefs = stats.get("coefficients", {})
        self.assertIn("job_demands_x_psy_capital", coefs)
        int_coef = coefs["job_demands_x_psy_capital"]
        self.assertLess(int_coef["b"], 0.0, "Interaction must be negative (buffering)")
        self.assertLess(int_coef["t"], -2.0)
        self.assertLessEqual(int_coef["p_value"], 0.05)

        # Simple slopes
        slopes = stats.get("simple_slopes", [])
        self.assertEqual(len(slopes), 3)
        slope_low = slopes[0]["simple_slope"]
        slope_mean = slopes[1]["simple_slope"]
        slope_high = slopes[2]["simple_slope"]

        # In buffering moderation, slope decreases as moderator increases
        self.assertGreater(slope_low, slope_mean)
        self.assertGreater(slope_mean, slope_high)

        # Johnson-Neyman technique
        jn = stats.get("johnson_neyman", {})
        self.assertTrue(jn.get("has_points"))
        self.assertGreaterEqual(len(jn.get("transition_points", [])), 1)

    def test_04_modmed_model7_bootstrap_estimation(self):
        """Model 7 estimation must report conditional indirect effects and significant index of moderated mediation."""
        stats_file = os.path.join(self.STATE_DIR, "analysis", "modmed_model7.json")
        self.assertTrue(os.path.exists(stats_file), f"ModMed stats missing: {stats_file}")

        with open(stats_file, "r", encoding="utf-8") as f:
            stats = json.load(f)

        self.assertEqual(stats.get("model_type"), "PROCESS Model 7 (First-Stage Moderated Mediation)")
        self.assertEqual(stats.get("sample_size"), 320)
        self.assertEqual(stats.get("bootstrap_samples"), 5000)

        # Stage equations
        eq_m = stats.get("stage1_mediator_equation", {})
        eq_y = stats.get("stage2_outcome_equation", {})
        self.assertAlmostEqual(eq_m.get("r2"), 0.361, places=2)
        self.assertAlmostEqual(eq_y.get("r2"), 0.226, places=2)

        # Conditional indirect effects
        cond_effects = stats.get("conditional_indirect_effects", [])
        self.assertEqual(len(cond_effects), 3)
        for eff in cond_effects:
            self.assertTrue(eff.get("significant"))
            self.assertGreater(eff.get("conditional_indirect_effect"), 0.0)

        # Index of moderated mediation
        imm = stats.get("index_of_moderated_mediation", {})
        self.assertLess(imm.get("index"), 0.0)
        self.assertLess(imm.get("ci_upper"), 0.0, "Upper bound of 95% BCa CI must be negative (excluding zero)")
        self.assertTrue(imm.get("significant"))

    def test_05_triad_artifact_invariant_stages(self):
        """Stages 05_moderation_macro, 06, 07, and 08 must each produce complete synchronized triads."""
        stages = [
            "05_moderation_macro",
            "06_hypothesis_1_interaction",
            "07_hypothesis_2_simple_slopes",
            "08_hypothesis_3_modmed"
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

    def test_06_deterministic_validators_overall_pass(self):
        """Master validator suite must report PASS across all stage outputs."""
        report = run_suite(self.OUTPUTS_DIR)
        self.assertEqual(report["overall_verdict"], "PASS", f"Suite failed: {report}")

        for res in report["results"]:
            self.assertNotEqual(res["verdict"], "FAIL", f"Sub-validator failed: {res}")

    def test_07_academic_state_schema_conformity(self):
        """All state files in academic-state must conform 100% to JSON schemas."""
        report = asm.validate_state(self.PROJECT_DIR)
        self.assertEqual(report["overall_verdict"], "PASS", f"State validation failed: {report.get('errors')}")
        self.assertGreaterEqual(len(report["validated_files"]), 9)


if __name__ == "__main__":
    unittest.main()
