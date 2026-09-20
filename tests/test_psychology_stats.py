# -*- coding: utf-8 -*-
"""
test_psychology_stats.py — Tests for Statistical Data Analysis Engine
Verifies APA 7 formatting, t-tests, ANCOVA, Cronbach's alpha, and effect sizes.
"""

import os
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATS_DIR = os.path.join(REPO_ROOT, ".agents", "skills", "statistical-data-analyst", "scripts")
if STATS_DIR not in sys.path:
    sys.path.insert(0, STATS_DIR)

import psychology_stats
from tests.conftest_data import get_sample_two_group_df, get_sample_scale_items_df


class TestPsychologyStats(unittest.TestCase):

    def setUp(self):
        self.df_groups = get_sample_two_group_df()
        self.df_items = get_sample_scale_items_df()

    def test_apa7_p_value_formatting(self):
        """Asserts APA 7 formatting: p < .001 for near-zero, exact 3 decimals, no leading zero in English."""
        self.assertEqual(psychology_stats.format_p_value(0.00005), "< .001")
        self.assertEqual(psychology_stats.format_p_value(0.0423), ".042")
        self.assertEqual(psychology_stats.format_p_value(0.500), ".500")
        self.assertNotIn("= .000", psychology_stats.format_p_value(0.00001))

    def test_independent_samples_ttest(self):
        """Asserts independent samples t-test computes correct t, df, p, and Cohen's d."""
        res = psychology_stats.analyze_group_comparison(self.df_groups, var_col="post_test", group_col="group")
        
        self.assertEqual(res["design"], "independent")
        self.assertEqual(res["n1"] + res["n2"], 60)
        self.assertEqual(res["df"], 58)  # N1 + N2 - 2
        self.assertGreater(abs(res["t"]), 2.0)
        self.assertLess(res["p"], 0.05)
        self.assertGreater(abs(res["cohen_d"]), 0.5)  # Expected intervention effect

    def test_scale_reliability_cronbach_alpha(self):
        """Asserts Cronbach's alpha on correlated Likert scale items."""
        res = psychology_stats.analyze_scale_reliability(self.df_items, item_cols=list(self.df_items.columns))
        
        self.assertEqual(res["n_items"], 5)
        self.assertEqual(res["n_cases"], 100)
        alpha = res["cronbach_alpha"]
        self.assertGreater(alpha, 0.65)
        self.assertLess(alpha, 0.95)
        self.assertEqual(len(res["item_diagnostics"]), 5)

    def test_ancova_f_statistic_and_partial_eta_squared(self):
        """Asserts ANCOVA model calculates F-ratio, degrees of freedom, and partial eta squared."""
        res = psychology_stats.analyze_ancova(
            self.df_groups, dv_col="post_test", group_col="group", covar_col="pre_test"
        )
        
        self.assertEqual(res["n_total"], 60)
        self.assertEqual(res["df_between"], 1)
        self.assertEqual(res["df_within"], 57)  # N - k - c = 60 - 2 - 1
        self.assertGreater(res["f_stat"], 10.0)
        self.assertLess(res["p"], 0.001)
        
        eta_p2 = res["partial_eta_squared"]
        self.assertGreater(eta_p2, 0.0)
        self.assertLess(eta_p2, 1.0)
        self.assertIn("control", res["adjusted_means"])
        self.assertIn("intervention", res["adjusted_means"])


    def test_repeated_measures_anova(self):
        """Asserts RM-ANOVA computes Mauchly sphericity, Greenhouse-Geisser epsilon, and pairwise tests."""
        import pandas as pd
        csv_path = os.path.join(REPO_ROOT, 'evals', 'benchmarks', 'datasets', 'bm_rm_anova_multitime.csv')
        df = pd.read_csv(csv_path)
        res = psychology_stats.analyze_repeated_measures_anova(
            df,
            subject_col='subject_id',
            time_cols=['Time_1', 'Time_2', 'Time_3', 'Time_4']
        )
        self.assertEqual(res['sample_size'], 60)
        self.assertTrue(res['mauchly_sphericity']['violated'])
        self.assertLess(res['epsilon']['greenhouse_geisser'], 0.75)
        self.assertEqual(res['correction_type'], 'Greenhouse-Geisser')
        self.assertGreater(res['primary_test']['f_statistic'], 50.0)
        self.assertLess(res['primary_test']['p_reported'], 0.001)
        self.assertEqual(len(res['pairwise_contrasts']), 6)
        self.assertTrue(all(p['significant_05'] for p in res['pairwise_contrasts']))


if __name__ == "__main__":
    unittest.main()
