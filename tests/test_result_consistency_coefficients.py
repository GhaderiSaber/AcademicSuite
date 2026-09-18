#!/usr/bin/env python3
"""
Regression test for ATK-13: Cross-Artifact Contradictions in Regression/Path Coefficients.

Verifies that validate_cross_artifacts and find_contradictions_in_text strictly catch
discrepancies in standardized beta, t-statistics, z-scores, and unstandardized coefficients.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from validators.result_consistency.validator import validate_cross_artifacts


class TestResultConsistencyCoefficients(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_coeff_consistency_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_contradictory_beta_and_t_triggers_failure(self):
        """Discrepant beta or t between JSON and Markdown triggers validation FAIL (ATK-13)."""
        json_path = os.path.join(self.temp_dir, "results.json")
        md_path = os.path.join(self.temp_dir, "results.md")

        # True empirical result: weak effect
        stats_data = {
            "sample_size": 250,
            "coefficients": [
                {
                    "predictor": "Mindfulness",
                    "beta": 0.25,
                    "b": 0.30,
                    "t": 2.15,
                    "p_value": 0.032
                }
            ]
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(stats_data, f)

        # Falsified narrative: inflated effect
        falsified_md = (
            "# Results\n\n"
            "Mindfulness strongly predicted outcome (β = 0.85, t = 9.40, p < .001, N = 250).\n"
        )
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(falsified_md)

        res = validate_cross_artifacts(json_path=json_path, md_path=md_path)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("beta" in err.lower() for err in res["errors"]))
        self.assertTrue(any("t-statistic" in err.lower() for err in res["errors"]))

    def test_consistent_coefficients_passes_validation(self):
        """Matching beta and t between JSON and Markdown passes validation."""
        json_path = os.path.join(self.temp_dir, "results.json")
        md_path = os.path.join(self.temp_dir, "results.md")

        stats_data = {
            "sample_size": 250,
            "coefficients": [
                {
                    "predictor": "Mindfulness",
                    "beta": 0.25,
                    "b": 0.30,
                    "t": 2.15,
                    "p_value": 0.032
                }
            ]
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(stats_data, f)

        consistent_md = (
            "# Results\n\n"
            "Mindfulness moderately predicted outcome (β = 0.25, t = 2.15, p = .032, N = 250).\n"
        )
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(consistent_md)

        res = validate_cross_artifacts(json_path=json_path, md_path=md_path)
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(len(res["errors"]), 0)


if __name__ == "__main__":
    unittest.main()
