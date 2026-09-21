#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_vertical_slices_phase38.py — Full Academic Vertical Slices Test Suite (Phase 38)

Proves the architecture works end-to-end across four complete canonical vertical slices:
  Vertical Slice A (Regression / GLM):
    Dataset → Descriptives → Assumptions → Analysis → Validation → Chapter 4 Paragraph
  Vertical Slice B (Experimental RCT):
    RCT → Repeated Measures → Effect Sizes → Follow-up → Validation → Results Package
  Vertical Slice C (Process Mediation):
    Mediation → Model Selection → Bootstrap → Indirect Effect → Interpretation → Writing Triad
  Vertical Slice D (Structural Equation Modeling):
    SEM → Measurement Model → Structural Model → Fit → Effects Decomposition → Reporting Triad

Enforces Directive 18 single-view context budget (<= 500 lines, <= 40,000 bytes).
"""

import os
import sys
import json
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        try:
            for entry in os.listdir(venv_lib):
                sp = os.path.join(venv_lib, entry, "site-packages")
                if os.path.isdir(sp) and sp not in sys.path:
                    sys.path.insert(0, sp)
        except OSError:
            pass

sys.path.insert(0, os.path.join(ROOT_DIR, ".agents"))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if os.path.join(ROOT_DIR, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))
if os.path.join(ROOT_DIR, "validators") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT_DIR, "validators"))

from scripts.academic_vertical_slice_runner import AcademicVerticalSliceRunner
from validators.run_all_validators import run_suite
from validators.data_integrity.validator import validate_data
from validators.numerical_consistency.validator import validate_numbers
from validators.reporting_consistency.validator import validate_reporting
from validators.result_consistency.validator import validate_results


class TestAcademicVerticalSlicesPhase38(unittest.TestCase):
    """End-to-End verification of the four complete canonical academic vertical slices."""

    @classmethod
    def setUpClass(cls):
        cls.runner = AcademicVerticalSliceRunner(root_dir=ROOT_DIR)

    def test_01_vertical_slice_a_dataset_to_chapter4_paragraph(self):
        """Vertical Slice A: Dataset → Descriptives → Assumptions → Analysis → Validation → Chapter 4 Paragraph."""
        res = self.runner.run_slice_a(verify_only=True)
        self.assertEqual(res["verdict"], "PASS", f"Vertical Slice A failed: {res}")
        steps = res["steps"]

        # 1. Dataset
        self.assertEqual(steps["1_dataset"]["status"], "PASS")
        self.assertEqual(steps["1_dataset"]["sample_size"], 100)

        # 2. Descriptives
        self.assertEqual(steps["2_descriptives"]["status"], "PASS")
        self.assertGreaterEqual(steps["2_descriptives"]["variables_count"], 3)

        # 3. Assumptions (Collinearity & Independence)
        self.assertEqual(steps["3_assumptions"]["status"], "PASS")
        self.assertTrue(steps["3_assumptions"]["collinearity_met"])
        self.assertTrue(steps["3_assumptions"]["independence_met"])
        self.assertLess(steps["3_assumptions"]["vif_max"], 5.0)

        # 4. Analysis
        self.assertEqual(steps["4_analysis"]["status"], "PASS")
        self.assertAlmostEqual(steps["4_analysis"]["r2"], 0.415, places=2)
        self.assertAlmostEqual(steps["4_analysis"]["adj_r2"], 0.403, places=2)
        self.assertGreater(steps["4_analysis"]["f_stat"], 30.0)

        # 5. Validation
        self.assertEqual(steps["5_validation"]["status"], "PASS")

        # 6. Chapter 4 Paragraph
        self.assertEqual(steps["6_chapter_4_paragraph"]["status"], "PASS")
        self.assertTrue(steps["6_chapter_4_paragraph"]["triad_present"])
        self.assertTrue(steps["6_chapter_4_paragraph"]["three_tables_standard"])

        cand_p = os.path.join(ROOT_DIR, "tests", "fixtures", "study_vertical_slice_regression")
        proj_dir = cand_p if os.path.isdir(cand_p) else os.path.join(ROOT_DIR, "projects", "study_vertical_slice_regression")
        out_dir = os.path.join(proj_dir, "academic-state", "outputs")
        md_file = os.path.join(out_dir, "06_hypothesis_1_regression.md")
        with open(md_file, "r", encoding="utf-8") as f:
            md_text = f.read()

        # Enforce Saber 5-part structure and Persian leading zero standard
        self.assertIn("بیان فرضیه", md_text)
        self.assertIn("تحلیل همبستگی", md_text)
        self.assertIn("خلاصه مدل رگرسیون", md_text)
        self.assertIn("ضرایب رگرسیون", md_text)
        self.assertIn("نتیجه‌گیری آماری", md_text)
        self.assertIn("۰.۰۰۱ > p", md_text)

    def test_02_vertical_slice_b_rct_to_results(self):
        """Vertical Slice B: RCT → Repeated Measures → Effect Sizes → Follow-up → Validation → Results Package."""
        res = self.runner.run_slice_b(verify_only=True)
        self.assertEqual(res["verdict"], "PASS", f"Vertical Slice B failed: {res}")
        steps = res["steps"]

        # 1. RCT Dataset (N=60, 2x3)
        self.assertEqual(steps["1_rct_dataset"]["status"], "PASS")
        self.assertEqual(steps["1_rct_dataset"]["sample_size"], 60)

        # 2. Repeated Measures Mixed ANOVA
        self.assertEqual(steps["2_repeated_measures"]["status"], "PASS")
        self.assertGreater(steps["2_repeated_measures"]["interaction_f"], 50.0)
        self.assertAlmostEqual(steps["2_repeated_measures"]["df_gg_adj"], 1.504, places=2)

        # 3. Effect Sizes
        self.assertEqual(steps["3_effect_sizes"]["status"], "PASS")
        self.assertGreater(steps["3_effect_sizes"]["partial_eta2_interaction"], 0.14)
        self.assertGreater(steps["3_effect_sizes"]["partial_eta2_post"], 0.14)
        self.assertEqual(steps["3_effect_sizes"]["effect_size_magnitude"], "LARGE")

        # 4. Follow-up Persistence (ANCOVA at 2-month follow-up)
        self.assertEqual(steps["4_follow_up"]["status"], "PASS")
        self.assertGreater(steps["4_follow_up"]["followup_f"], 100.0)
        self.assertAlmostEqual(steps["4_follow_up"]["followup_partial_eta2"], 0.698, places=2)
        self.assertEqual(steps["4_follow_up"]["persistence_verdict"], "SUPPORTED")

        # 5. Validation Cascade
        self.assertEqual(steps["5_validation"]["status"], "PASS")

        # 6. Results Deliverable Package
        self.assertEqual(steps["6_results_package"]["status"], "PASS")
        self.assertTrue(steps["6_results_package"]["master_docx"])
        self.assertTrue(steps["6_results_package"]["master_md"])
        self.assertTrue(steps["6_results_package"]["trajectory_plot"])

    def test_03_vertical_slice_c_mediation_to_writing(self):
        """Vertical Slice C: Mediation → Model Selection → Bootstrap → Indirect Effect → Interpretation → Writing Triad."""
        res = self.runner.run_slice_c(verify_only=True)
        self.assertEqual(res["verdict"], "PASS", f"Vertical Slice C failed: {res}")
        steps = res["steps"]

        # 1. Mediation Dataset (N=300)
        self.assertEqual(steps["1_mediation_dataset"]["status"], "PASS")
        self.assertEqual(steps["1_mediation_dataset"]["sample_size"], 300)

        # 2. Model Selection (PROCESS Model 6)
        self.assertEqual(steps["2_model_selection"]["status"], "PASS")
        self.assertIn("Model 6", steps["2_model_selection"]["selected_model"])

        # 3. Bootstrap (5,000 resamples)
        self.assertEqual(steps["3_bootstrap"]["status"], "PASS")
        self.assertEqual(steps["3_bootstrap"]["resamples"], 5000)
        self.assertEqual(steps["3_bootstrap"]["ci_method"], "BCa (Bias-Corrected and Accelerated)")

        # 4. Indirect Effect Decomposition & Mathematical Identity
        self.assertEqual(steps["4_indirect_effect"]["status"], "PASS")
        self.assertTrue(steps["4_indirect_effect"]["algebraic_identity_verified"])
        self.assertEqual(steps["4_indirect_effect"]["indirect_paths_count"], 4)
        self.assertAlmostEqual(steps["4_indirect_effect"]["total_c"], 0.483, places=2)
        self.assertAlmostEqual(steps["4_indirect_effect"]["direct_c_prime"], 0.225, places=2)
        self.assertAlmostEqual(steps["4_indirect_effect"]["total_indirect"], 0.258, places=2)

        # 5. Interpretation (BCa CIs exclude zero)
        self.assertEqual(steps["5_interpretation"]["status"], "PASS")
        self.assertTrue(steps["5_interpretation"]["all_bootstrap_cis_exclude_zero"])

        # 6. Writing Triads (One-Hypothesis-One-Stage)
        self.assertEqual(steps["6_writing_triad"]["status"], "PASS")
        self.assertTrue(steps["6_writing_triad"]["all_triads_present"])
        self.assertEqual(len(steps["6_writing_triad"]["hypotheses_triads"]), 3)

    def test_04_vertical_slice_d_sem_to_reporting(self):
        """Vertical Slice D: SEM → Measurement Model → Structural Model → Fit → Effects → Reporting Triad."""
        res = self.runner.run_slice_d(verify_only=True)
        self.assertEqual(res["verdict"], "PASS", f"Vertical Slice D failed: {res}")
        steps = res["steps"]

        # 1. SEM Dataset (N=250)
        self.assertEqual(steps["1_sem_dataset"]["status"], "PASS")
        self.assertEqual(steps["1_sem_dataset"]["sample_size"], 250)

        # 2. Measurement Model (CFA)
        self.assertEqual(steps["2_measurement_model"]["status"], "PASS")
        self.assertEqual(steps["2_measurement_model"]["factors_count"], 3)
        self.assertTrue(steps["2_measurement_model"]["cr_benchmark_met"])
        self.assertTrue(steps["2_measurement_model"]["ave_benchmark_met"])

        # 3. Structural Model
        self.assertEqual(steps["3_structural_model"]["status"], "PASS")
        self.assertEqual(steps["3_structural_model"]["structural_paths_count"], 3)

        # 4. Model Fit Indices (Hu & Bentler Cutoffs)
        self.assertEqual(steps["4_fit_indices"]["status"], "PASS")
        self.assertLessEqual(steps["4_fit_indices"]["chi2_df"], 3.0)
        self.assertGreaterEqual(steps["4_fit_indices"]["cfi"], 0.95)
        self.assertGreaterEqual(steps["4_fit_indices"]["tli"], 0.95)
        self.assertLessEqual(steps["4_fit_indices"]["rmsea"], 0.05)
        self.assertLessEqual(steps["4_fit_indices"]["srmr"], 0.05)
        self.assertIn(steps["4_fit_indices"]["verdict"], ["EXCELLENT", "ACCEPTABLE"])

        # 5. Effects Decomposition & Bootstrap Mediation
        self.assertEqual(steps["5_effects_decomposition"]["status"], "PASS")
        self.assertTrue(steps["5_effects_decomposition"]["bootstrap_ci_excludes_zero"])
        self.assertEqual(steps["5_effects_decomposition"]["bootstrap_samples"], 5000)

        # 6. Reporting Triads
        self.assertEqual(steps["6_reporting_triad"]["status"], "PASS")
        self.assertTrue(steps["6_reporting_triad"]["all_triads_present"])
        self.assertEqual(len(steps["6_reporting_triad"]["stages"]), 3)

    def test_05_runner_all_slices_and_isolation(self):
        """Verify AcademicVerticalSliceRunner executes all slices cleanly and maintains strict isolation."""
        full_report = self.runner.run_all(verify_only=True)
        self.assertEqual(full_report["overall_verdict"], "PASS")
        self.assertIn("A", full_report["slices"])
        self.assertIn("B", full_report["slices"])
        self.assertIn("C", full_report["slices"])
        self.assertIn("D", full_report["slices"])

        for s_id, s_data in full_report["slices"].items():
            self.assertEqual(s_data["verdict"], "PASS", f"Slice {s_id} failed in full report")

    def test_06_directive_18_single_view_budget(self):
        cand = os.path.join(ROOT_DIR, ".agents", "scripts", "academic_vertical_slice_runner.py")
        runner_path = cand if os.path.isfile(cand) else os.path.join(ROOT_DIR, "scripts", "academic_vertical_slice_runner.py")
        test_path = os.path.abspath(__file__)

        for path in [runner_path, test_path]:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            size = os.path.getsize(path)
            self.assertLessEqual(len(lines), 500, f"{path} exceeds 500 lines ({len(lines)})")
            self.assertLessEqual(size, 40000, f"{path} exceeds 40,000 bytes ({size})")


if __name__ == "__main__":
    unittest.main()
