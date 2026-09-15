# -*- coding: utf-8 -*-
"""
test_gpower_engine.py — Tests for G*Power 3.1 Sample Size and Power Calculations
Based on Cohen (1988) and Faul et al. (2007, 2009).
"""

import os
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GPOWER_DIR = os.path.join(REPO_ROOT, ".agents", "skills", "gpower-sample-size-calculator", "scripts")
if GPOWER_DIR not in sys.path:
    sys.path.insert(0, GPOWER_DIR)

from gpower_engine import GPowerEngine


class TestGPowerEngine(unittest.TestCase):

    def test_ttest_independent_medium_effect(self):
        """Asserts independent t-test (d=0.50, alpha=.05, power=.80) yields N=128 (64 per group)."""
        res = GPowerEngine.calculate_ttest_independent(alpha=0.05, target_power=0.80, d=0.50, tails="two")
        
        self.assertEqual(res["total_sample_size"], 128)
        self.assertEqual(res["sample_size_per_group"], 64)
        self.assertGreaterEqual(res["actual_power"], 0.80)
        self.assertEqual(res["df"], 126)

    def test_ttest_tails_comparison(self):
        """Asserts one-tailed t-test requires smaller total sample size than two-tailed for same power."""
        res_two = GPowerEngine.calculate_ttest_independent(alpha=0.05, target_power=0.80, d=0.50, tails="two")
        res_one = GPowerEngine.calculate_ttest_independent(alpha=0.05, target_power=0.80, d=0.50, tails="one")
        
        self.assertLess(res_one["total_sample_size"], res_two["total_sample_size"])

    def test_ancova_sample_size(self):
        """Asserts ANCOVA (k=2 groups, 1 covariate, f=0.25, power=0.85) yields expected benchmark N."""
        res = GPowerEngine.calculate_ancova(alpha=0.05, target_power=0.85, f=0.25, k=2, c=1)
        
        self.assertIn(res["total_sample_size"], range(140, 155))
        self.assertGreaterEqual(res["actual_power"], 0.85)
        self.assertEqual(res["test_family"], "F-tests")

    def test_multiple_regression_sample_size(self):
        """Asserts Multiple Regression (3 predictors, f2=0.15, power=0.80) yields benchmark N."""
        res = GPowerEngine.calculate_regression(alpha=0.05, target_power=0.80, f2=0.15, num_predictors=3)
        
        self.assertIn(res["total_sample_size"], range(74, 82))
        self.assertGreaterEqual(res["actual_power"], 0.80)

    def test_repeated_measures_sample_size(self):
        """Asserts Repeated Measures ANOVA (2 groups, 3 measurements, f=0.25, power=0.85) benchmark."""
        res = GPowerEngine.calculate_repeated_measures(alpha=0.05, target_power=0.85, f=0.25, groups=2, measurements=3, r=0.5)
        
        self.assertIn(res["total_sample_size"], range(80, 100))
        self.assertGreaterEqual(res["actual_power"], 0.85)


if __name__ == "__main__":
    unittest.main()
