# -*- coding: utf-8 -*-
"""
test_msai_detector.py — Tests for Directive 10 Multi-Signal Anomaly Index (MSAI)
Verifies authentic vs flawed/synthetic empirical profiles.
"""

import os
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VERIF_DIR = os.path.join(REPO_ROOT, ".agents", "verification")
if VERIF_DIR not in sys.path:
    sys.path.insert(0, VERIF_DIR)

from multi_signal_anomaly_detector import MultiSignalAnomalyDetector
from tests.conftest_data import get_authentic_msai_payload, get_anomalous_msai_payload


class TestMSAIDetector(unittest.TestCase):

    def setUp(self):
        self.detector = MultiSignalAnomalyDetector()

    def test_authentic_payload_normal_empirical(self):
        """Asserts authentic empirical dataset yields NORMAL_EMPIRICAL with 0 signals."""
        payload = get_authentic_msai_payload()
        res = self.detector.evaluate_payload(payload)
        
        self.assertEqual(res["verdict"], "NORMAL_EMPIRICAL")
        self.assertEqual(res["active_signals_count"], 0)
        self.assertEqual(res["anomaly_index"], 0)
        self.assertEqual(len(res["signals"]), 0)

    def test_anomalous_payload_elevated_review_flag(self):
        """Asserts fabricated profile triggers multiple convergent signals and elevated review."""
        payload = get_anomalous_msai_payload()
        res = self.detector.evaluate_payload(payload)
        
        self.assertEqual(res["verdict"], "FLAG_FOR_REVIEW_ELEVATED")
        self.assertGreaterEqual(res["active_signals_count"], 5)
        self.assertGreaterEqual(res["anomaly_index"], 75)
        
        signal_ids = [s["signal_id"] for s in res["signals"]]
        self.assertIn("SIG_01_LARGE_EFFECT", signal_ids)
        self.assertIn("SIG_02_VARIANCE_DEFLATION", signal_ids)
        self.assertIn("SIG_03_PERFECT_SEPARATION", signal_ids)
        self.assertIn("SIG_04_EXCESSIVE_RELIABILITY", signal_ids)
        self.assertIn("SIG_06_PERFECT_NORMALITY", signal_ids)
        self.assertIn("SIG_10_NARRATIVE_MISMATCH", signal_ids)

    def test_critical_narrative_mismatch_flag(self):
        """Asserts narrative vs table mismatch triggers CRITICAL severity."""
        payload = get_authentic_msai_payload()
        payload["narrative_discrepancies"] = ["Discrepancy: narrative M=10, table M=20"]
        res = self.detector.evaluate_payload(payload)
        
        self.assertEqual(res["active_signals_count"], 1)
        narrative_sig = [s for s in res["signals"] if s["signal_id"] == "SIG_10_NARRATIVE_MISMATCH"][0]
        self.assertEqual(narrative_sig["severity"], "CRITICAL")


if __name__ == "__main__":
    unittest.main()
