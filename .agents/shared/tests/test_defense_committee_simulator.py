#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Digital Saber Defense Committee Simulator
(test_defense_committee_simulator.py)
-------------------------------------------------------------------------------
Validates:
1. Flawless thesis with confirmed publication achieves 20.00 (Exceptional).
2. Standard defense without publication is legally capped at <= 19.00.
3. Sample size and power deficiencies apply deterministic deductions.
4. Statistical assumption breaches, df mismatches, and p = .000 violations deduct points.
5. MSAI anomalies trigger data plausibility penalties.
6. Persian leading zero and APA 7 typography defects are penalized.
7. Viva voce oral defense challenges are generated across all 5 distinct faculty roles.
8. Ensures zero naive or sycophantic 20/20 grading under default/typical conditions.
"""

import os
import sys
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

VERIF_DIR = os.path.join(ROOT_DIR, ".agents", "verification")
if VERIF_DIR not in sys.path:
    sys.path.insert(0, VERIF_DIR)

from defense_committee_simulator import DefenseCommitteeSimulator


class TestDefenseCommitteeSimulator(unittest.TestCase):
    """Test suite for rigorous, non-naive Iranian 20-point defense grading."""

    def setUp(self):
        self.sim = DefenseCommitteeSimulator()

    def test_01_flawless_defense_with_publication_reaches_20(self):
        """Flawless thesis with N >= 60 and publication letter achieves full 20.00."""
        metrics = {
            "has_publication_letter": True,
            "sample_size": 70,
            "statistical_power": 0.92,
            "total_assumptions": 5,
            "assumptions_passed": 5,
            "p_zero_violations": 0,
            "df_mismatch": False,
            "msai_anomaly_count": 0,
            "leading_zero_violations": 0,
            "apa_format_violations": 0,
            "unverified_citations_count": 0,
            "mechanism_depth_weak": False
        }
        res = self.sim.compute_defense_readiness_index(metrics)
        self.assertEqual(res["final_grade_out_of_20"], 20.00)
        self.assertEqual(res["total_deductions"], 0.00)
        self.assertEqual(res["clearance_status"], "CLEARANCE_GRANTED_EXCEPTIONAL")
        self.assertIn("استثنایی", res["overall_verdict"])
        self.assertEqual(len(res["deductions_ledger"]), 0)

    def test_02_standard_high_quality_without_publication_is_capped(self):
        """Standard high quality thesis without publication letter is capped at <= 19.00."""
        metrics = {
            "has_publication_letter": False,
            "sample_size": 70,
            "total_assumptions": 4,
            "assumptions_passed": 4,
            "msai_anomaly_count": 0
        }
        res = self.sim.compute_defense_readiness_index(metrics)
        # Deducts 1.00 for no publication letter -> 19.00
        self.assertEqual(res["final_grade_out_of_20"], 19.00)
        self.assertEqual(res["total_deductions"], 1.00)
        self.assertEqual(res["clearance_status"], "CLEARANCE_WITH_MINOR_REVISIONS")
        self.assertIn("بسیار خوب", res["overall_verdict"])
        self.assertEqual(len(res["deductions_ledger"]), 1)
        self.assertEqual(res["deductions_ledger"][0]["category"], "قوانین آموزشی و مقالات مستخرج")

    def test_03_underpowered_sample_size_penalties(self):
        """Validates progressive deductions for borderline and critically small samples."""
        # Case A: N = 40 (borderline power: -1.0 pt)
        res_40 = self.sim.compute_defense_readiness_index({"sample_size": 40, "has_publication_letter": True})
        self.assertEqual(res_40["final_grade_out_of_20"], 19.00)
        self.assertTrue(any("۴۰" in d["item"] or "40" in d["item"] for d in res_40["deductions_ledger"]))

        # Case B: N = 24 (underpowered: -2.0 pts)
        res_24 = self.sim.compute_defense_readiness_index({"sample_size": 24, "has_publication_letter": True})
        self.assertEqual(res_24["final_grade_out_of_20"], 18.00)

        # Case C: N = 14 (critical underpowered: -3.0 pts)
        res_14 = self.sim.compute_defense_readiness_index({"sample_size": 14, "has_publication_letter": True})
        self.assertEqual(res_14["final_grade_out_of_20"], 17.00)

    def test_04_statistical_assumptions_and_reporting_penalties(self):
        """Assumptions breaches (-1.50 per breach), df mismatch, and p=.000 reporting are penalized."""
        metrics = {
            "has_publication_letter": True,
            "sample_size": 60,
            "total_assumptions": 4,
            "assumptions_passed": 2,  # 2 failed -> -3.00
            "p_zero_violations": 1,   # -0.50
            "df_mismatch": True        # -1.50
        }
        res = self.sim.compute_defense_readiness_index(metrics)
        # Deductions: 3.00 + 0.50 + 1.50 = 5.00 -> 15.00
        self.assertEqual(res["final_grade_out_of_20"], 15.00)
        self.assertEqual(res["total_deductions"], 5.00)
        self.assertEqual(res["clearance_status"], "CONDITIONAL_SUBSTANTIAL_DEFECTS")
        self.assertIn("مشروط شدید", res["overall_verdict"])

    def test_05_msai_anomalies_and_data_plausibility(self):
        """MSAI anomaly signals reduce score and flag data fabrication risk."""
        # 1 anomaly: -1.50
        res_1 = self.sim.compute_defense_readiness_index({"has_publication_letter": True, "sample_size": 60, "msai_anomaly_count": 1})
        self.assertEqual(res_1["final_grade_out_of_20"], 18.50)

        # 3 anomalies: -5.00 (Critical fabrication flag)
        res_3 = self.sim.compute_defense_readiness_index({
            "has_publication_letter": False,  # -1.00
            "sample_size": 25,                # -2.00
            "msai_anomaly_count": 3           # -5.00
        })
        # Deductions: 1.00 + 2.00 + 5.00 = 8.00 -> 12.00
        self.assertEqual(res_3["final_grade_out_of_20"], 12.00)
        self.assertEqual(res_3["clearance_status"], "DEFENSE_REJECTED")
        self.assertIn("رد اولیه", res_3["overall_verdict"])

    def test_06_persian_leading_zero_and_apa_formatting_penalties(self):
        """Violations of Directive 4 (Persian leading zero) and APA 7 table formatting are penalized."""
        metrics = {
            "has_publication_letter": True,
            "sample_size": 60,
            "leading_zero_violations": 4,  # -1.00
            "apa_format_violations": 2     # -0.50
        }
        res = self.sim.compute_defense_readiness_index(metrics)
        self.assertEqual(res["final_grade_out_of_20"], 18.50)
        self.assertEqual(res["total_deductions"], 1.50)

    def test_07_viva_voce_five_roles_generation(self):
        """Cross-examination must generate challenges representing 5 distinct faculty roles."""
        prof = {
            "title": "اثربخشی شناخت‌درمانی مبتنی بر ذهن‌آگاهی بر ولع مصرف",
            "iv": "شناخت‌درمانی مبتنی بر ذهن‌آگاهی (MBCT)",
            "dv": "ولع مصرف مواد",
            "scale_name": "مقیاس ولع مصرف فرانکن (DDQ)",
            "sample_size": 32,
            "design": "ancova"
        }
        res = self.sim.generate_defense_cross_examination(prof)
        self.assertEqual(res["total_challenges"], 5)
        roles = [c["role_id"] for c in res["challenges"]]
        expected_roles = ["methodologist", "biostatistician", "clinical_theorist", "psychometrician", "jury_chair"]
        self.assertEqual(roles, expected_roles)
        for c in res["challenges"]:
            self.assertTrue(len(c["challenge_fa"]) > 20)
            self.assertTrue(len(c["model_answer_fa"]) > 20)
            self.assertTrue(len(c["apa7_evidence"]) > 5)

    def test_08_no_naive_twenty_under_default_conditions(self):
        """Passing default/empty profile must NEVER award a naive 20.00 score."""
        res_empty = self.sim.compute_defense_readiness_index({})
        self.assertLess(res_empty["final_grade_out_of_20"], 20.00)
        self.assertNotEqual(res_empty["clearance_status"], "CLEARANCE_GRANTED_EXCEPTIONAL")

        prof_default = {
            "title": "پژوهش نمونه",
            "sample_size": 30
        }
        res_default = self.sim.generate_defense_cross_examination(prof_default)
        self.assertLessEqual(res_default["final_grade_out_of_20"], 18.00)


if __name__ == "__main__":
    unittest.main()
