# -*- coding: utf-8 -*-
"""
test_simdat_engine.py — Tests for Monte Carlo Psychometric Data Simulation
Verifies Likert quantization, realistic empirical decimal noise (Directive 9), and RCT models.
"""

import os
import sys
import unittest
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


if __name__ == "__main__":
    unittest.main()
