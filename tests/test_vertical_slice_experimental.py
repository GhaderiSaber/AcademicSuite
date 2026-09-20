#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_vertical_slice_experimental.py — End-to-End Experimental RCT Vertical Slice Integration Test

Verifies the complete Experimental Multi-Group Repeated Measures & ANCOVA pipeline:
Dataset (N=60, 2 Groups x 3 Occasions) → Data Audit → Assumptions Verification →
One-Way ANCOVA (Post-Test & 2-Month Follow-Up) → 2x3 Mixed Repeated Measures ANOVA →
Master Validators → Synchronized Triad Artifacts (.docx + .md + .json).
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


class TestVerticalSliceExperimental(unittest.TestCase):
    cand_proj = os.path.join(ROOT_DIR, "tests", "fixtures", "study_vertical_slice_experimental")
    PROJECT_DIR = cand_proj if os.path.isdir(cand_proj) else os.path.join(ROOT_DIR, "projects", "study_vertical_slice_experimental")
    STATE_DIR = os.path.join(PROJECT_DIR, "academic-state")
    OUTPUTS_DIR = os.path.join(STATE_DIR, "outputs")

    def test_01_dataset_integrity(self):
        """Raw dataset must exist and contain N=60 observations with 2 groups and 3 occasions."""
        xlsx_path = os.path.join(self.PROJECT_DIR, "01_raw_inputs", "data_raw.xlsx")
        self.assertTrue(os.path.exists(xlsx_path), f"Dataset missing: {xlsx_path}")

        import pandas as pd
        df = pd.read_excel(xlsx_path)
        self.assertEqual(len(df), 60, "Sample size must be exactly 60")

        # Check groups
        self.assertIn("group", df.columns)
        self.assertEqual(len(df[df["group"] == 1]), 30, "Experimental group must have n=30")
        self.assertEqual(len(df[df["group"] == 2]), 30, "Control group must have n=30")

        # Check composite measures across occasions
        composites = [
            "anxiety_pre", "anxiety_post", "anxiety_followup",
            "inflex_pre", "inflex_post", "inflex_followup"
        ]
        for comp in composites:
            self.assertIn(comp, df.columns, f"Missing composite variable: {comp}")

        # Check Likert items (1 to 5)
        for occasion in ["pre", "post", "fup"]:
            for i in range(1, 6):
                col_bai = f"anx_{occasion}_{i}"
                col_aaq = f"inf_{occasion}_{i}"
                self.assertIn(col_bai, df.columns)
                self.assertIn(col_aaq, df.columns)
                self.assertTrue(df[col_bai].between(1, 5).all(), f"Likert violation in {col_bai}")
                self.assertTrue(df[col_aaq].between(1, 5).all(), f"Likert violation in {col_aaq}")

    def test_02_data_audit_and_state_validation(self):
        """Data audit report must be present, data integrity must pass, and academic state must be valid."""
        audit_file = os.path.join(self.STATE_DIR, "data", "data_quality.json")
        self.assertTrue(os.path.exists(audit_file), f"Audit report missing: {audit_file}")

        with open(audit_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data.get("sample_n"), 60)
        self.assertEqual(data.get("missing_rate"), 0.0)
        self.assertEqual(data.get("quality_verdict"), "PASS")

        res = validate_data(audit_file)
        self.assertEqual(res["verdict"], "PASS")

        state_res = asm.validate_state(self.PROJECT_DIR)
        self.assertEqual(state_res["overall_verdict"], "PASS", f"State validation failed: {state_res.get('errors')}")

    def test_03_parametric_and_covariance_assumptions(self):
        """Assumptions report must confirm normality, variance equality, Box's M, and sphericity."""
        assumptions_file = os.path.join(self.STATE_DIR, "analysis", "experimental_assumptions.json")
        self.assertTrue(os.path.exists(assumptions_file), f"Assumptions checkpoint missing: {assumptions_file}")

        with open(assumptions_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data.get("sample_size"), 60)
        self.assertEqual(data.get("overall_assumptions_verdict"), "SUPPORTED")

        # Normality (all p > .05)
        for occ in ["pre", "post", "followup"]:
            for grp in ["group_1", "group_2"]:
                sw = data["normality_shapiro_wilk"][occ][grp]
                self.assertTrue(sw["is_normal"])
                self.assertGreater(sw["p_value"], 0.05)

        # Levene's test (both p > .05)
        self.assertTrue(data["homogeneity_of_variance_levene"]["post_test"]["assumption_met"])
        self.assertTrue(data["homogeneity_of_variance_levene"]["follow_up"]["assumption_met"])

        # Box's M test (p > .001)
        self.assertTrue(data["box_m_test"]["assumption_met"])
        self.assertAlmostEqual(data["box_m_test"]["box_m"], 11.445, places=2)

        # Mauchly Sphericity and GG epsilon
        self.assertAlmostEqual(data["mauchly_sphericity_test"]["greenhouse_geisser_epsilon"], 0.752, places=2)

    def test_04_ancova_post_estimation(self):
        """Hypothesis 1 ANCOVA post-test must show significant group effect after baseline covariate control."""
        ancova_file = os.path.join(self.STATE_DIR, "analysis", "ancova_post.json")
        self.assertTrue(os.path.exists(ancova_file), f"ANCOVA post file missing: {ancova_file}")

        with open(ancova_file, "r", encoding="utf-8") as f:
            stats = json.load(f)

        self.assertEqual(stats.get("sample_size"), 60)
        self.assertEqual(stats.get("verdict"), "SUPPORTED")

        # Descriptives
        exp_adj = stats["adjusted_means"]["1"]["mean_adj"]
        ctl_adj = stats["adjusted_means"]["2"]["mean_adj"]
        self.assertLess(exp_adj, ctl_adj, "Experimental adjusted anxiety must be lower than control")
        self.assertAlmostEqual(exp_adj, 2.314, places=2)
        self.assertAlmostEqual(ctl_adj, 3.521, places=2)

        # Group effect
        grp_tab = stats["ancova_table"]["group"]
        self.assertEqual(grp_tab["df"], 1)
        self.assertGreater(grp_tab["f_stat"], 150.0)
        self.assertAlmostEqual(grp_tab["partial_eta_squared"], 0.78, places=2)

        num_res = validate_numbers(ancova_file, sample_n=60)
        self.assertEqual(num_res["verdict"], "PASS")

    def test_05_ancova_followup_estimation(self):
        """Hypothesis 2 ANCOVA follow-up must confirm long-term intervention maintenance."""
        ancova_fu_file = os.path.join(self.STATE_DIR, "analysis", "ancova_followup.json")
        self.assertTrue(os.path.exists(ancova_fu_file), f"ANCOVA followup file missing: {ancova_fu_file}")

        with open(ancova_fu_file, "r", encoding="utf-8") as f:
            stats = json.load(f)

        self.assertEqual(stats.get("sample_size"), 60)
        self.assertEqual(stats.get("verdict"), "SUPPORTED")

        exp_adj = stats["adjusted_means"]["1"]["mean_adj"]
        ctl_adj = stats["adjusted_means"]["2"]["mean_adj"]
        self.assertLess(exp_adj, ctl_adj)
        self.assertAlmostEqual(exp_adj, 2.362, places=2)
        self.assertAlmostEqual(ctl_adj, 3.433, places=2)

        grp_tab = stats["ancova_table"]["group"]
        self.assertGreater(grp_tab["f_stat"], 100.0)
        self.assertAlmostEqual(grp_tab["partial_eta_squared"], 0.698, places=2)

    def test_06_repeated_measures_mixed_anova(self):
        """Hypothesis 3 Mixed Repeated Measures must confirm significant group x time interaction."""
        rm_file = os.path.join(self.STATE_DIR, "analysis", "repeated_measures.json")
        self.assertTrue(os.path.exists(rm_file), f"Repeated measures file missing: {rm_file}")

        with open(rm_file, "r", encoding="utf-8") as f:
            stats = json.load(f)

        self.assertEqual(stats.get("sample_size"), 60)
        self.assertEqual(stats.get("interaction_verdict"), "SUPPORTED")

        anova_tab = stats["anova_table"]
        inter = anova_tab["interaction_group_time"]
        self.assertGreater(inter["f_stat"], 70.0)
        self.assertAlmostEqual(inter["partial_eta_squared"], 0.571, places=2)
        self.assertAlmostEqual(inter["df_gg_adj"], 1.504, places=2)

        # Pairwise within experimental
        pw_exp = stats["pairwise_bonferroni"]["within_experimental"]
        pre_vs_post = pw_exp[0]
        self.assertEqual(pre_vs_post["comparison"], "Pre-Test vs Post-Test")
        self.assertTrue(pre_vs_post["significant"])
        self.assertAlmostEqual(pre_vs_post["mean_diff"], 1.125, places=2)

        post_vs_fu = pw_exp[2]
        self.assertEqual(post_vs_fu["comparison"], "Post-Test vs Follow-Up")
        self.assertFalse(post_vs_fu["significant"], "Maintenance requires no significant change between post and follow-up")

    def test_07_synchronized_triad_artifacts_exist(self):
        """Micro-stage triads (.docx, .md, .json) must exist on disk for all 10 stages."""
        expected_triads = [
            "00_data_curation_report",
            "01_demographics",
            "02_descriptives_and_reliability",
            "03_experimental_assumptions",
            "04_bivariate_correlations",
            "06_hypothesis_1_ancova_post",
            "07_hypothesis_2_ancova_followup",
            "08_hypothesis_3_repeated_measures",
            "09_chapter_summary",
            "10_defense_brief"
        ]
        for base in expected_triads:
            docx_p = os.path.join(self.OUTPUTS_DIR, f"{base}.docx")
            md_p = os.path.join(self.OUTPUTS_DIR, f"{base}.md")
            json_p = os.path.join(self.OUTPUTS_DIR, f"{base}.json")
            self.assertTrue(os.path.exists(docx_p), f"Missing DOCX: {docx_p}")
            self.assertTrue(os.path.exists(md_p), f"Missing MD: {md_p}")
            self.assertTrue(os.path.exists(json_p), f"Missing JSON: {json_p}")
            self.assertGreater(os.path.getsize(docx_p), 1000)
            self.assertGreater(os.path.getsize(md_p), 500)
            self.assertGreater(os.path.getsize(json_p), 200)

    def test_08_run_all_deterministic_validators(self):
        """Master validator suite must evaluate outputs directory with overall PASS."""
        report = run_suite(self.OUTPUTS_DIR)
        self.assertEqual(report["overall_verdict"], "PASS")
        self.assertGreaterEqual(len(report["results"]), 10)

    def test_09_master_deliverable_package_exists(self):
        """Master deliverable package must exist with Word DOCX, Markdown, 6-sheet Excel, and 300-DPI plot."""
        pkg_dir = os.path.join(self.OUTPUTS_DIR, "08_master_package")
        self.assertTrue(os.path.isdir(pkg_dir), f"Missing master package dir: {pkg_dir}")

        docx_p = os.path.join(pkg_dir, "Experimental_Study_Report.docx")
        md_p = os.path.join(pkg_dir, "Experimental_Study_Report.md")
        xlsx_p = os.path.join(pkg_dir, "experimental_analysis_matrix.xlsx")
        png_p = os.path.join(pkg_dir, "experimental_trajectory_plots.png")

        self.assertTrue(os.path.exists(docx_p), f"Missing master DOCX: {docx_p}")
        self.assertTrue(os.path.exists(md_p), f"Missing master MD: {md_p}")
        self.assertTrue(os.path.exists(xlsx_p), f"Missing master Excel: {xlsx_p}")
        self.assertTrue(os.path.exists(png_p), f"Missing master plot: {png_p}")

        self.assertGreater(os.path.getsize(docx_p), 5000)
        self.assertGreater(os.path.getsize(md_p), 5000)
        self.assertGreater(os.path.getsize(xlsx_p), 5000)
        self.assertGreater(os.path.getsize(png_p), 10000)

    def test_10_defense_brief_simulation(self):
        """Defense brief must contain 4 viva voce examiner scenarios and readiness score >= 95%."""
        brief_json = os.path.join(self.OUTPUTS_DIR, "10_defense_brief.json")
        self.assertTrue(os.path.exists(brief_json), f"Missing defense brief JSON: {brief_json}")

        with open(brief_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data.get("stage_id"), "10_defense_brief")
        self.assertGreaterEqual(data.get("defense_readiness_score", 0), 95.0)
        self.assertEqual(data.get("verdict"), "SUPPORTED")
        scenarios = data.get("committee_scenarios", [])
        self.assertEqual(len(scenarios), 4)


if __name__ == '__main__':
    unittest.main()
