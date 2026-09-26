#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_validation_evolution.py — Test Suite for 4-Tier Validation Architecture (4-TVA)

Verifies:
1. Statcheck exact concordance and p-value recalculation via scipy.stats
2. Statcheck reporting errors (|Δp| > 0.015)
3. Statcheck gross decision errors (significance threshold crossing)
4. GRIM test on valid vs. impossible Likert means (M * N ∈ ℤ)
5. SPRITE theoretical variance bounds on bounded scales
6. Correlation matrix admissibility and positive semi-definiteness
7. Actionable Repair Prescription (ARP) compilation and agent routing
8. 4-Tier cascade execution (--tier 1, --tier 2, --tier all)
9. Directive 22 fail-closed lifecycle hook enforcement (validation_agent_guard.py)
10. Defense readiness certification and 0-20 Iranian grading scorecard
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
for p in (ROOT_DIR, AGENTS_DIR, os.path.join(AGENTS_DIR, "validators"), os.path.join(AGENTS_DIR, "hooks", "agents")):
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

from validators.statcheck_grim_verifier import (
    verify_statcheck,
    verify_grim,
    verify_sprite_bounds,
    verify_correlation_matrix,
    create_actionable_repair_prescription
)
from validators.numerical_consistency.validator import validate_numbers
from validators.adversarial_challenge_runner import run_adversarial_audit
from validators.defense_readiness_compiler import run_defense_certification
from validators.run_all_validators import run_suite
import importlib.util
_val_guard_path = os.path.join(ROOT_DIR, ".agents", "agents", "validation-agent", "guard.py")
_spec = importlib.util.spec_from_file_location("validation_agent_guard", _val_guard_path)
_val_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_val_mod)
handle_stop = _val_mod.handle_stop


class TestValidationEvolution(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="academic_suite_4tva_test_")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # ==========================================================================
    # 1. Statcheck Tests
    # ==========================================================================
    def test_01_statcheck_exact_concordance(self):
        """Valid t(48) = 2.05 gives p = 0.0458. Matches reported p = 0.046."""
        res = verify_statcheck("t", 2.05, 48, reported_p=0.046)
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(res["severity"], "NONE")
        self.assertTrue(res["is_consistent"])
        self.assertFalse(res["is_decision_inconsistency"])

    def test_02_statcheck_reporting_error(self):
        """t(48) = 2.05 gives p = 0.0458. Reported p = 0.020 is inaccurate but both < .05."""
        res = verify_statcheck("t", 2.05, 48, reported_p=0.020)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertEqual(res["severity"], "REPORTING_ERROR")
        self.assertFalse(res["is_consistent"])
        self.assertFalse(res["is_decision_inconsistency"])

    def test_03_statcheck_gross_decision_error(self):
        """t(48) = 1.80 gives p = 0.0781. Reported p = 0.035 falsely claims significance!"""
        res = verify_statcheck("t", 1.80, 48, reported_p=0.035)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertEqual(res["severity"], "CRITICAL")
        self.assertTrue(res["is_decision_inconsistency"])
        self.assertIn("GROSS DECISION INCONSISTENCY", res["message"])

    def test_04_statcheck_f_test_recomputation(self):
        """F(2, 45) = 4.20 gives p = 0.0213. Matches reported p = 0.021."""
        res = verify_statcheck("f", 4.20, 2, 45, reported_p=0.021)
        self.assertEqual(res["verdict"], "PASS")
        self.assertFalse(res["is_decision_inconsistency"])

    # ==========================================================================
    # 2. GRIM Granularity Tests
    # ==========================================================================
    def test_05_grim_valid_likert_mean(self):
        """For N=30, Mean=3.20 -> Sum=96 (exact integer). Passes GRIM."""
        res = verify_grim(3.20, 30, items_count=1)
        self.assertTrue(res["grim_consistent"])
        self.assertEqual(res["verdict"], "PASS")

    def test_06_grim_impossible_mean(self):
        """For N=30, Mean=3.14 -> Sum=94.2. Impossible! Nearest are 3.13 and 3.17."""
        res = verify_grim(3.14, 30, items_count=1)
        self.assertFalse(res["grim_consistent"])
        self.assertEqual(res["verdict"], "FAIL")
        self.assertEqual(res["severity"], "CRITICAL")
        self.assertIn("MATHEMATICALLY IMPOSSIBLE", res["message"])

    # ==========================================================================
    # 3. SPRITE Bounds & Correlation Matrix Tests
    # ==========================================================================
    def test_07_sprite_variance_exceeded(self):
        """On 1-5 scale, Mean=4.8 has max SD = sqrt(0.2 * 3.8) = 0.872. Reported SD=1.20 fails."""
        res = verify_sprite_bounds(4.8, 1.20, scale_min=1.0, scale_max=5.0)
        self.assertFalse(res["sprite_consistent"])
        self.assertEqual(res["verdict"], "FAIL")
        self.assertEqual(res["severity"], "CRITICAL")

    def test_08_correlation_matrix_non_psd(self):
        """A matrix with r12=0.9, r13=0.9, r23=-0.9 has negative eigenvalue -> impossible."""
        bad_matrix = [
            [1.0, 0.9, 0.9],
            [0.9, 1.0, -0.9],
            [0.9, -0.9, 1.0]
        ]
        res = verify_correlation_matrix(bad_matrix)
        self.assertFalse(res["matrix_valid"])
        self.assertFalse(res["is_psd"])
        self.assertEqual(res["verdict"], "FAIL")

    # ==========================================================================
    # 4. Numerical Consistency Validator with Integrated ARPs
    # ==========================================================================
    def test_09_numerical_validator_detects_decision_error_and_generates_arp(self):
        """Numerical validator catches decision error and produces structured ARP for statistics-agent."""
        stats_file = os.path.join(self.test_dir, "test_stats.json")
        payload = {
            "sample_size": 50,
            "coefficients": [
                {
                    "predictor": "anxiety",
                    "t": 1.80,
                    "df": 48,
                    "p_value": 0.035
                }
            ]
        }
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(payload, f)

        res = validate_numbers(stats_file)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertEqual(res["gross_decision_errors"], 1)
        self.assertGreater(len(res["actionable_repair_prescriptions"]), 0)

        arp = res["actionable_repair_prescriptions"][0]
        self.assertEqual(arp["severity"], "CRITICAL")
        self.assertEqual(arp["responsible_agent"], "statistics-agent")
        self.assertEqual(arp["defect_type"], "GROSS_DECISION_INCONSISTENCY")

    # ==========================================================================
    # 5. Master Suite 4-Tier Execution & Tier Selection
    # ==========================================================================
    def test_10_master_suite_empty_stage_blocked_with_arp(self):
        """Empty directory in run_suite returns BLOCKED and issues project-organizer ARP."""
        report = run_suite(self.test_dir, tier="1")
        self.assertEqual(report["overall_verdict"], "BLOCKED")
        self.assertGreater(len(report["actionable_repair_prescriptions"]), 0)
        arp = report["actionable_repair_prescriptions"][0]
        self.assertEqual(arp["responsible_agent"], "project-organizer")
        self.assertEqual(arp["severity"], "CRITICAL")

    def test_11_defense_readiness_certification_and_grading_scorecard(self):
        """Defense readiness compiler generates 0-20 scorecard and Saber's Human Gate Card."""
        cert = run_defense_certification(self.test_dir, has_wos_publication=False)
        self.assertIn("overall_score_out_of_20", cert)
        self.assertLessEqual(cert["overall_score_out_of_20"], 19.00)  # Ceiling invariant
        self.assertIn("human_gate_card", cert)
        self.assertEqual(cert["human_gate_card"]["recipient_id"], "124911145")

    # ==========================================================================
    # 6. Directive 22 Lifecycle Hook Guard Enforcement
    # ==========================================================================
    def test_12_validation_agent_guard_blocks_unverified_pass_claim(self):
        """Guard blocks verbal PASS claim when no valid validation_report.json exists."""
        # Create transcript claiming PASS
        transcript_file = os.path.join(self.test_dir, "transcript.jsonl")
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "content": "Status: PASS! All checks passed and approved for release."
            }) + "\n")

        payload = {
            "transcriptPath": transcript_file,
            "workspacePaths": [self.test_dir]
        }
        res = handle_stop(payload)
        self.assertEqual(res["decision"], "continue")
        self.assertIn("Directive 22", res["reason"])

    def test_13_validation_agent_guard_blocks_pass_with_open_critical_arp(self):
        """Guard blocks PASS claim when validation_report.json contains open critical ARPs."""
        transcript_file = os.path.join(self.test_dir, "transcript.jsonl")
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "content": "Verdict: PASS."
            }) + "\n")

        val_report_file = os.path.join(self.test_dir, "validation_report.json")
        with open(val_report_file, "w", encoding="utf-8") as f:
            json.dump({
                "overall_verdict": "PASS",
                "evidence_summary": {
                    "total_evidence_items_evaluated": 5,
                    "total_checks_run": 5,
                    "checks_passed": 5,
                    "checks_failed": 0
                },
                "actionable_repair_prescriptions": [
                    {
                        "prescription_id": "ARP-01",
                        "severity": "CRITICAL",
                        "status": "OPEN",
                        "defect_type": "GROSS_DECISION_INCONSISTENCY",
                        "responsible_agent": "statistics-agent"
                    }
                ]
            }, f)

        payload = {
            "transcriptPath": transcript_file,
            "workspacePaths": [self.test_dir]
        }
        res = handle_stop(payload)
        self.assertEqual(res["decision"], "continue")
        self.assertIn("Actionable Repair Prescriptions", res["reason"])

    def test_14_validation_agent_guard_allows_fully_certified_pass(self):
        """Guard allows PASS claim when clean report with 0 failed and 0 open critical ARPs exists."""
        transcript_file = os.path.join(self.test_dir, "transcript.jsonl")
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "content": "Verdict: PASS."
            }) + "\n")

        val_report_file = os.path.join(self.test_dir, "validation_report.json")
        with open(val_report_file, "w", encoding="utf-8") as f:
            json.dump({
                "overall_verdict": "PASS",
                "evidence_summary": {
                    "total_evidence_items_evaluated": 5,
                    "total_checks_run": 5,
                    "checks_passed": 5,
                    "checks_failed": 0,
                    "checks_blocked": 0
                },
                "results": [],
                "actionable_repair_prescriptions": []
            }, f)

        payload = {
            "transcriptPath": transcript_file,
            "workspacePaths": [self.test_dir]
        }
        res = handle_stop(payload)
        self.assertEqual(res["decision"], "allow")


if __name__ == '__main__':
    unittest.main()
