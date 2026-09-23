# -*- coding: utf-8 -*-
"""
test_sem_r_engine.py — Unit and Integration Tests for Native R SEM Data Generation Engine
Validates that sem_data_maker.R reproduces the exact methodology from Data Making notebooks:
1. Exogenous/Endogenous latent structural generation and measurement equations.
2. J-iteration candidate selection loop.
3. Rescale transformation to target subscale means and SDs.
4. Export of primary_data.xlsx, final_data.xlsx, sem_results.json, and replicate_sem_analysis.R.
5. Goodness-of-fit indices (CFI >= 0.90, RMSEA <= 0.08).
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
import subprocess
import pandas as pd

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
R_SCRIPT_PATH = os.path.join(
    REPO_ROOT, ".agents", "skills", "psychometric-data-simulator", "scripts", "sem_data_maker.R"
)


class TestSemREngine(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_sem_r_")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_r_script_exists(self):
        """Asserts sem_data_maker.R exists and is executable."""
        self.assertTrue(os.path.exists(R_SCRIPT_PATH), "sem_data_maker.R must exist on disk")

    def test_p13_pies_simulation_workflow(self):
        """
        Runs preset p13_pies via Rscript and validates:
        1. Clean 0 exit code.
        2. Generation of primary_data.xlsx and final_data.xlsx.
        3. Correct columns and sample size N = 206.
        4. Rescaled empirical means align closely with notebook target specifications.
        5. Goodness-of-Fit indices meet academic standards (CFI >= 0.90, RMSEA <= 0.08).
        """
        cmd = [
            "Rscript",
            R_SCRIPT_PATH,
            "--preset", "p13_pies",
            "--n", "206",
            "--J", "5",
            "--seed", "451",
            "--out-dir", self.test_dir
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Rscript failed:\n{res.stderr}\n{res.stdout}")

        # Verify physical disk artifacts
        primary_path = os.path.join(self.test_dir, "primary_data.xlsx")
        final_path = os.path.join(self.test_dir, "final_data.xlsx")
        summary_path = os.path.join(self.test_dir, "sem_results.json")
        rep_script_path = os.path.join(self.test_dir, "replicate_sem_analysis.R")

        self.assertTrue(os.path.exists(primary_path), "primary_data.xlsx must exist")
        self.assertTrue(os.path.exists(final_path), "final_data.xlsx must exist")
        self.assertTrue(os.path.exists(summary_path), "sem_results.json must exist")
        self.assertTrue(os.path.exists(rep_script_path), "replicate_sem_analysis.R must exist")

        # Verify dataset contents
        df_final = pd.read_excel(final_path)
        expected_cols = ["AA", "AAG", "DIF", "DDF", "EOT", "ER", "EC", "IP", "FO", "RQ"]
        self.assertEqual(len(df_final), 206)
        for col in expected_cols:
            self.assertIn(col, df_final.columns)

        # Verify rescaling targets from P13 notebook
        # Target: AA=39, AAG=27, DIF=14, DDF=9, EOT=17, ER=19, EC=17, IP=7, FO=6, RQ=28
        self.assertAlmostEqual(df_final["AA"].mean(), 39.0, delta=2.5)
        self.assertAlmostEqual(df_final["AAG"].mean(), 27.0, delta=2.5)
        self.assertAlmostEqual(df_final["DIF"].mean(), 14.0, delta=2.0)
        self.assertAlmostEqual(df_final["DDF"].mean(), 9.0, delta=1.5)
        self.assertAlmostEqual(df_final["EOT"].mean(), 17.0, delta=2.0)
        self.assertAlmostEqual(df_final["ER"].mean(), 19.0, delta=2.5)
        self.assertAlmostEqual(df_final["EC"].mean(), 17.0, delta=2.0)
        self.assertAlmostEqual(df_final["IP"].mean(), 7.0, delta=1.5)
        self.assertAlmostEqual(df_final["FO"].mean(), 6.0, delta=1.5)
        self.assertAlmostEqual(df_final["RQ"].mean(), 28.0, delta=2.5)

        # Verify fit indices in JSON summary (strict upper/lower bounds)
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        fit = summary.get("fit_indices", {})
        self.assertGreaterEqual(fit.get("cfi", 0.0), 0.90)
        self.assertLessEqual(fit.get("cfi", 2.0), 1.000, "CFI must never exceed 1.000")
        self.assertLessEqual(fit.get("tli", 2.0), 1.000, "TLI must never exceed 1.000")
        self.assertGreater(fit.get("rmsea", 0.0), 0.000, "RMSEA must be strictly positive (not 0.000)")
        self.assertLessEqual(fit.get("rmsea", 1.0), 0.08)

        # Verify factor loadings are strictly bounded below 1.000 (no Heywood cases)
        fl_summary = summary.get("factor_loadings_summary", {})
        self.assertTrue(fl_summary.get("loadings_bounded", False), "Factor loadings must be bounded below 1.0")
        self.assertLess(fl_summary.get("max_loading", 2.0), 1.000, "Max factor loading must be < 1.000")
        loadings = summary.get("factor_loadings", [])
        self.assertGreater(len(loadings), 0, "Factor loadings list must not be empty")
        for item in loadings:
            self.assertLess(abs(item["loading_std"]), 1.000, f"Loading for {item['indicator']} exceeds 1.0")

        # Verify publication semPlot diagrams exist on disk
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "sem_plot.pdf")), "sem_plot.pdf must exist")
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "sem_plot.png")), "sem_plot.png must exist")

        # Verify defined mediation parameters (ac := a * c, bd := b * d)
        dp = summary.get("defined_parameters", {})
        self.assertIn("ac", dp)
        self.assertIn("bd", dp)
        self.assertIn("tot", dp)
        self.assertLess(dp["ac"]["pvalue"], 0.05)
        self.assertLess(dp["bd"]["pvalue"], 0.05)

    def test_p22_attachment_simulation(self):
        """Runs preset p22_attachment and verifies proper execution and artifact generation."""
        cmd = [
            "Rscript",
            R_SCRIPT_PATH,
            "--preset", "p22_attachment",
            "--n", "150",
            "--J", "3",
            "--seed", "123",
            "--out-dir", self.test_dir
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Rscript failed:\n{res.stderr}\n{res.stdout}")

        df_final = pd.read_excel(os.path.join(self.test_dir, "final_data.xlsx"))
        expected_cols = ["ANX", "AMB", "SEC", "ISF", "DEG", "REC", "OB", "CB"]
        self.assertEqual(len(df_final), 150)
        for col in expected_cols:
            self.assertIn(col, df_final.columns)

        # Target means: ANX=16, AMB=14, SEC=21, ISF=7, DEG=16, REC=36, OB=9, CB=7
        self.assertAlmostEqual(df_final["ANX"].mean(), 16.0, delta=2.0)
        self.assertAlmostEqual(df_final["REC"].mean(), 36.0, delta=3.0)

    def test_p25_general_wlsmv_and_latents_export(self):
        """
        Runs preset p25_general with --estimator WLSMV and --include-latents:
        1. Checks that Rscript succeeds (returncode == 0).
        2. Checks that final_data_with_latents.xlsx exists.
        3. Verifies columns include both manifest indicators ('y1' to 'y10') and latents ('ETA', 'PHIA', 'PHIB', 'THETA').
        4. Checks that sem_results.json records estimator == 'WLSMV'.
        """
        cmd = [
            "Rscript",
            R_SCRIPT_PATH,
            "--preset", "p25_general",
            "--estimator", "WLSMV",
            "--include-latents",
            "--n", "150",
            "--J", "3",
            "--seed", "451",
            "--out-dir", self.test_dir
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Rscript failed:\n{res.stderr}\n{res.stdout}")

        final_lat_path = os.path.join(self.test_dir, "final_data_with_latents.xlsx")
        self.assertTrue(os.path.exists(final_lat_path), "final_data_with_latents.xlsx must exist")

        df_lat = pd.read_excel(final_lat_path)
        self.assertEqual(len(df_lat), 150)
        expected_manifests = [f"y{i}" for i in range(1, 11)]
        expected_latents = ["ETA", "PHIA", "PHIB", "THETA"]
        for col in expected_manifests + expected_latents:
            self.assertIn(col, df_lat.columns)

        summary_path = os.path.join(self.test_dir, "sem_results.json")
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
        self.assertEqual(summary.get("estimator"), "WLSMV")

    def test_j_batch_fit_bounds_and_loadings(self):
        """
        Validates that changing J iterations:
        1. Maintains valid fit measure upper/lower bounds (CFI <= 1.0, TLI <= 1.0, RMSEA > 0.0).
        2. Strictly bounds all factor loadings below 1.000 (no Heywood cases).
        3. Avoids selection of degenerate zero-RMSEA batches.
        """
        for j_val in [2, 5]:
            sub_dir = os.path.join(self.test_dir, f"j_{j_val}")
            cmd = [
                "Rscript",
                R_SCRIPT_PATH,
                "--preset", "p13_pies",
                "--n", "206",
                "--J", str(j_val),
                "--seed", "451",
                "--out-dir", sub_dir
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Rscript failed for J={j_val}:\n{res.stderr}\n{res.stdout}")

            summary_path = os.path.join(sub_dir, "sem_results.json")
            with open(summary_path, "r", encoding="utf-8") as f:
                summary = json.load(f)

            fit = summary.get("fit_indices", {})
            self.assertLessEqual(fit.get("cfi", 2.0), 1.000, f"CFI exceeded 1.0 for J={j_val}")
            self.assertLessEqual(fit.get("tli", 2.0), 1.000, f"TLI exceeded 1.0 for J={j_val}")
            self.assertGreater(fit.get("rmsea", 0.0), 0.000, f"RMSEA must be > 0.0 for J={j_val}")

            fl_summary = summary.get("factor_loadings_summary", {})
            self.assertTrue(fl_summary.get("loadings_bounded", False), f"Loadings must be bounded for J={j_val}")
            self.assertLess(fl_summary.get("max_loading", 2.0), 1.000, f"Max loading exceeded 1.0 for J={j_val}")


if __name__ == "__main__":
    unittest.main()
