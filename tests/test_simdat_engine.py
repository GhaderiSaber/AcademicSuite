# -*- coding: utf-8 -*-
"""
test_simdat_engine.py — Tests for Monte Carlo Psychometric Data Simulation
Verifies Likert quantization, realistic empirical decimal noise (Directive 9), and RCT models.
"""

import os
import sys
import unittest
import shutil
import numpy as np

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SIMDAT_DIR = os.path.join(REPO_ROOT, ".agents", "skills", "psychometric-data-simulator", "scripts")
if SIMDAT_DIR not in sys.path:
    sys.path.insert(0, SIMDAT_DIR)

import simdat_engine
from tests.conftest_data import get_sample_scale_items_df


class TestSimdatEngine(unittest.TestCase):

    def test_quantize_to_likert_discrete_bounds(self):
        """Asserts continuous latent scores quantize to discrete Likert integers in [1, 5]."""
        raw_vals = np.array([-5.0, -1.2, 0.0, 1.4, 3.2, 8.0])
        likert = simdat_engine.quantize_to_likert(raw_vals, min_val=1, max_val=5)
        
        self.assertTrue(np.issubdtype(likert.dtype, np.integer))
        self.assertTrue(np.all(likert >= 1))
        self.assertTrue(np.all(likert <= 5))
        self.assertEqual(len(likert), len(raw_vals))

    def test_rct_simulation_structure_and_directive9_noise(self):
        """Asserts RCT simulation generates expected columns and realistic decimal noise (Directive 9)."""
        payload = {
            "groups": ["Control", "Intervention"],
            "outcomes": [
                {
                    "name": "Anxiety",
                    "mean_baseline": 45.0,
                    "sd_baseline": 8.0,
                    "cohens_d_post": 0.80
                }
            ]
        }
        
        res = simdat_engine.run_rct_simulation(payload, n_per_group=30, seed=42)
        df = res["rct_dataset"]
        
        self.assertEqual(len(df), 60)
        self.assertIn("Subject_ID", df.columns)
        self.assertIn("Group", df.columns)
        self.assertIn("Anxiety_Pre", df.columns)
        self.assertIn("Anxiety_Post", df.columns)
        
        # Directive 9: Means must have realistic empirical decimal noise, not whole integers
        pre_mean = df["Anxiety_Pre"].mean()
        post_mean = df["Anxiety_Post"].mean()
        self.assertFalse(pre_mean.is_integer(), "Pre mean must not be a synthetic whole integer")
        self.assertFalse(post_mean.is_integer(), "Post mean must not be a synthetic whole integer")

    def test_cronbach_alpha_calculation(self):
        """Asserts Cronbach's alpha calculation on correlated items."""
        df_items = get_sample_scale_items_df()
        alpha = simdat_engine.compute_cronbach_alpha(df_items.values)
        
        self.assertGreater(alpha, 0.65)
        self.assertLess(alpha, 0.95)

    def test_rescale_function_notebook_standard(self):
        """Asserts rescale function matches Data Making notebook transformation."""
        scaled_vals = np.array([-1.0, 0.0, 1.0, 2.0])
        rescaled = simdat_engine.rescale(scaled_vals, target_mean=39.0, target_sd=3.0, round_to_int=True)
        # Expected: round([-1*3+39, 0*3+39, 1*3+39, 2*3+39]) = [36, 39, 42, 45]
        np.testing.assert_array_equal(rescaled, np.array([36.0, 39.0, 42.0, 45.0]))

    @unittest.skipIf(shutil.which("Rscript") is None, "Rscript is not installed on this system")
    def test_sem_preset_p13_delegation(self):
        """Asserts sem_p13_pies research preset executes and generates valid artifacts."""
        import tempfile
        tmp_dir = tempfile.mkdtemp(prefix="test_sem_simdat_")
        try:
            payload = simdat_engine.RESEARCH_PRESETS["sem_p13_pies"]
            payload["out_dir"] = tmp_dir
            res = simdat_engine.run_sem_simulation(payload, n=150, seed=451)
            self.assertIn("rescaled_data", res)
            df = res["rescaled_data"]
            self.assertEqual(len(df), 150)
            self.assertIn("AA", df.columns)
            self.assertIn("RQ", df.columns)
            fit = res.get("fit_indices", {})
            self.assertGreaterEqual(fit.get("cfi", 0.0), 0.90)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    @unittest.skipIf(shutil.which("Rscript") is None, "Rscript is not installed on this system")
    def test_sem_preset_p25_general_delegation_with_latents(self):
        """Asserts sem_p25_general preset runs with include_latents and WLSMV estimator."""
        import tempfile, shutil
        tmp_dir = tempfile.mkdtemp(prefix="test_p25_simdat_")
        try:
            payload = dict(simdat_engine.RESEARCH_PRESETS["sem_p25_general"])
            payload["out_dir"] = tmp_dir
            payload["include_latents"] = True
            res = simdat_engine.run_sem_simulation(payload, n=120, seed=451)
            self.assertIn("rescaled_data", res)
            self.assertIn("final_data_with_latents", res)
            df_final = res["rescaled_data"]
            df_lat = res["final_data_with_latents"]
            self.assertEqual(len(df_final), 120)
            self.assertEqual(len(df_lat), 120)
            self.assertIn("y1", df_final.columns)
            self.assertIn("ETA", df_lat.columns)
            self.assertIn("PHIA", df_lat.columns)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
