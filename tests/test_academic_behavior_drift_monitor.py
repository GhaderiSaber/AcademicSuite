#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_behavior_drift_monitor.py — Unit Tests for Behavior-Drift Monitor

Verifies:
1. Behavioral profile maintains and tracks all 8 dimensions (correctness, methodology,
   statistical_validity, evidence_grounding, integrity, robustness, consistency, efficiency).
2. Cross-capability regression detection: TARGET CAPABILITY IMPROVED but OTHER CAPABILITY REGRESSED.
3. Methodological inconsistency detection on same evidence without design justification.
4. Justified differences (explainable by changed inputs/design) are NOT penalized.
5. Automatic candidate deactivation when protected capabilities fall below safety thresholds.
6. Snapshot rollback restores the last known-good version of canonical skills.
7. Drift audit reports are persisted under learning/reports/drift/ and pass schema validation.
8. End-to-end post-promotion guard halts harmful mutations and records complete audit trails.
"""

import os
import sys
import json
import uuid
import shutil
import tempfile
import unittest
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.academic_behavior_drift_monitor import (
    AcademicBehaviorDriftMonitor,
    DriftMonitoringError
)
from contracts.contract_validator import (
    validate_behavioral_profile,
    validate_drift_report
)


class TestAcademicBehaviorDriftMonitor(unittest.TestCase):
    """Authoritative test suite for the Behavior-Drift Monitoring System."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_drift_test_")
        self.monitor = AcademicBehaviorDriftMonitor(base_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # Test 1: 8-Dimension Behavioral Profile Tracking
    # -------------------------------------------------------------------------
    def test_01_behavioral_profile_tracks_eight_dimensions(self):
        """Verifies profile tracks all 8 dimensions, baselines, and validates against contract."""
        profile = self.monitor.get_or_create_profile(
            target_id="statistical-data-analyst",
            target_type="skill"
        )

        self.assertEqual(profile["target_id"], "statistical-data-analyst")
        self.assertEqual(profile["target_type"], "skill")
        self.assertIn("dimensions", profile)
        self.assertIn("dimension_baselines", profile)

        # Check all 8 dimensions exist and bounded
        expected_dims = [
            "correctness",
            "methodology",
            "statistical_validity",
            "evidence_grounding",
            "integrity",
            "robustness",
            "consistency",
            "efficiency"
        ]
        for dim in expected_dims:
            self.assertIn(dim, profile["dimensions"])
            val = profile["dimensions"][dim]
            self.assertGreaterEqual(val, 0.0)
            self.assertLessEqual(val, 1.0)

        val_res = validate_behavioral_profile(profile)
        self.assertTrue(val_res["valid"], f"Profile schema error: {val_res.get('errors')}")

    # -------------------------------------------------------------------------
    # Test 2: Cross-Capability Regression Detection
    # -------------------------------------------------------------------------
    def test_02_detect_target_improved_but_other_regressed(self):
        """
        Verifies detection of pattern: TARGET CAPABILITY IMPROVED but OTHER CAPABILITY REGRESSED.
        Target skill improves from 0.90 to 0.98, but protected assumption-testing drops from 0.95 to 0.88.
        """
        evaluations = {
            "chapter-4-writing": {
                "score": 0.98,
                "baseline": 0.90
            },
            "assumption-testing": {
                "score": 0.88,
                "baseline": 0.95
            }
        }

        report = self.monitor.audit_drift(
            target_id="chapter-4-writing",
            target_type="skill",
            current_evaluations=evaluations,
            trigger="POST_PROMOTION"
        )

        self.assertEqual(report["verdict"], "WARNING_DRIFT")
        self.assertEqual(len(report["cross_capability_regressions"]), 1)

        reg = report["cross_capability_regressions"][0]
        self.assertEqual(reg["target_capability"], "chapter-4-writing")
        self.assertEqual(reg["target_status"], "IMPROVED")
        self.assertEqual(reg["regressed_capability"], "assumption-testing")
        self.assertAlmostEqual(reg["delta"], -0.07, places=2)

    # -------------------------------------------------------------------------
    # Test 3: Unexplainable Inconsistency on Identical Evidence
    # -------------------------------------------------------------------------
    def test_03_detect_same_evidence_inconsistent_decision(self):
        """
        Verifies detection of unexplainable methodological flip on identical evidence.
        Baseline: Pearson correlation for bivariate linear data.
        Flip: Spearman rho without any non-normality or outlier violation.
        """
        evidence_hash = self.monitor.compute_evidence_fingerprint(
            sample_size=120,
            design="bivariate_correlation",
            assumptions={"normality": True, "linearity": True}
        )

        profile = self.monitor.get_or_create_profile("statistical-data-analyst", "skill")

        # First observation establishes baseline
        check_1 = self.monitor.evaluate_methodological_consistency(
            profile=profile,
            evidence_hash=evidence_hash,
            current_decision="Pearson r",
            inputs_summary="N=120, normal distributions",
            design="bivariate",
            rationale="Parametric bivariate normality verified"
        )
        self.assertEqual(check_1["verdict"], "CONSISTENT")

        # Second observation flips decision without inputs or design change
        check_2 = self.monitor.evaluate_methodological_consistency(
            profile=profile,
            evidence_hash=evidence_hash,
            current_decision="Spearman rho",
            inputs_summary="N=120, normal distributions",
            design="bivariate",
            rationale="Arbitrary non-parametric switch",
            inputs_changed=False,
            design_changed=False
        )
        self.assertEqual(check_2["verdict"], "UNEXPLAINABLE_INCONSISTENCY")
        self.assertFalse(check_2["explainable"])

    # -------------------------------------------------------------------------
    # Test 4: Justified Differences Are Allowed
    # -------------------------------------------------------------------------
    def test_04_allow_justified_methodological_differences(self):
        """
        Verifies that justified methodological differences (due to changed inputs/design)
        are flagged as JUSTIFIED_DIFFERENCE and NOT penalized.
        """
        evidence_hash = self.monitor.compute_evidence_fingerprint(
            sample_size=80,
            design="pre_post_treatment",
            assumptions={"sphericity": True}
        )

        profile = self.monitor.get_or_create_profile("statistical-data-analyst", "skill")

        # Baseline: RM-ANOVA
        self.monitor.evaluate_methodological_consistency(
            profile=profile,
            evidence_hash=evidence_hash,
            current_decision="RM-ANOVA",
            design="repeated_measures",
            rationale="Balanced complete cases"
        )

        # Shift to LMM justified by missing data attrition
        check_justified = self.monitor.evaluate_methodological_consistency(
            profile=profile,
            evidence_hash=evidence_hash,
            current_decision="Linear Mixed Models (LMM)",
            design="repeated_measures_with_attrition",
            rationale="Missing waves present, LMM avoids listwise deletion",
            inputs_changed=True,
            design_changed=False
        )
        self.assertEqual(check_justified["verdict"], "JUSTIFIED_DIFFERENCE")
        self.assertTrue(check_justified["explainable"])

    # -------------------------------------------------------------------------
    # Test 5: Automatic Candidate Deactivation on Critical Regression
    # -------------------------------------------------------------------------
    def test_05_automatic_candidate_deactivation_on_critical_regression(self):
        """
        Verifies that when a critical regression occurs (delta <= -0.10),
        the candidate is automatically deactivated in learning/candidates/.
        """
        # Create mock candidate file
        cid = "CAND-MUT-CRIT-001"
        c_file = os.path.join(self.monitor.candidates_dir, f"{cid}.json")
        with open(c_file, "w", encoding="utf-8") as f:
            json.dump({
                "candidate_id": cid,
                "status": "ACTIVE",
                "target_skill": "statistical-data-analyst",
                "mutation_type": "INSTRUCTION_REFINEMENT"
            }, f, indent=2)

        # Severe regression in protected capability (delta = -0.15)
        evaluations = {
            "statistical-data-analyst": {
                "score": 0.80,
                "baseline": 0.95
            }
        }

        report = self.monitor.audit_drift(
            target_id="statistical-data-analyst",
            target_type="skill",
            candidate_id=cid,
            current_evaluations=evaluations,
            trigger="POST_PROMOTION"
        )

        self.assertEqual(report["verdict"], "CRITICAL_REGRESSION_ROLLBACK")
        self.assertTrue(report["rollback_executed"])

        # Verify candidate file on disk is now DEACTIVATED_ROLLBACK
        with open(c_file, "r", encoding="utf-8") as f:
            updated_candidate = json.load(f)
        self.assertEqual(updated_candidate["status"], "DEACTIVATED_ROLLBACK")
        self.assertIn("deactivation_reason", updated_candidate)

    # -------------------------------------------------------------------------
    # Test 6: Snapshot Rollback Restores Last Known-Good Version
    # -------------------------------------------------------------------------
    def test_06_snapshot_rollback_restores_last_known_good_version(self):
        """
        Verifies that rollback restores canonical SKILL.md from the latest snapshot
        in learning/snapshots/skills/.
        """
        skill_name = "mock-skill"
        skill_dir = os.path.join(self.monitor.skills_dir, skill_name)
        os.makedirs(skill_dir, exist_ok=True)
        skill_file = os.path.join(skill_dir, "SKILL.md")

        # 1. Original known-good version
        good_content = "# Mock Skill Known-Good Baseline\n\nCanonical instructions.\n"
        snap_file = os.path.join(self.monitor.snapshots_dir, f"{skill_name}_v20260918_120000.md")
        with open(snap_file, "w", encoding="utf-8") as f:
            f.write(good_content)

        # 2. Mutated/degraded version currently in production
        bad_content = "# Degraded Skill Content\n\nFlawed instructions.\n"
        with open(skill_file, "w", encoding="utf-8") as f:
            f.write(bad_content)

        # 3. Trigger rollback
        cid = "CAND-REGRESSIVE-002"
        rollback_info = self.monitor.execute_rollback(
            candidate_id=cid,
            target_skill=skill_name,
            reason="Protected regression rollback"
        )

        # 4. Verify canonical file was restored to known-good baseline
        with open(skill_file, "r", encoding="utf-8") as f:
            restored_content = f.read()

        self.assertEqual(restored_content, good_content)
        self.assertEqual(rollback_info["snapshot_id"], os.path.basename(snap_file))

    # -------------------------------------------------------------------------
    # Test 7: Drift Report Persisted and Passes Schema
    # -------------------------------------------------------------------------
    def test_07_drift_report_persisted_and_contract_compliant(self):
        """Verifies drift audit reports written to disk pass validate_drift_report."""
        report = self.monitor.audit_drift(
            target_id="academic-writer",
            target_type="agent",
            trigger="PERIODIC_MONITOR"
        )

        self.assertTrue(report["report_id"].startswith("DRIFT-"))
        report_file = os.path.join(self.monitor.reports_dir, f"{report['report_id']}.json")
        self.assertTrue(os.path.isfile(report_file))

        val_res = validate_drift_report(report)
        self.assertTrue(val_res["valid"], f"Drift report schema error: {val_res.get('errors')}")

    # -------------------------------------------------------------------------
    # Test 8: End-to-End Post-Promotion Guard
    # -------------------------------------------------------------------------
    def test_08_end_to_end_post_promotion_guard(self):
        """
        Full integration test: A candidate improves target benchmark but introduces
        an unexplainable methodological inconsistency and causes a regression.
        The monitor flags the anomaly, halts rollout, and adjusts profile status.
        """
        cid = "CAND-COMPLEX-003"
        c_file = os.path.join(self.monitor.candidates_dir, f"{cid}.json")
        with open(c_file, "w", encoding="utf-8") as f:
            json.dump({"candidate_id": cid, "status": "ACTIVE"}, f)

        # Prepare evidence check with unjustified flip
        ev_hash = self.monitor.compute_evidence_fingerprint(200, "ancova", {"slope_homogeneity": True})
        sim_checks = [
            {
                "evidence_hash": ev_hash,
                "current_decision": "ANCOVA",
                "design": "ancova"
            },
            {
                "evidence_hash": ev_hash,
                "current_decision": "ANOVA",
                "design": "ancova",
                "inputs_changed": False,
                "design_changed": False
            }
        ]

        # Trigger drift audit
        report = self.monitor.audit_drift(
            target_id="statistical-data-analyst",
            target_type="skill",
            candidate_id=cid,
            current_evaluations={
                "statistical-data-analyst": {"score": 0.99, "baseline": 0.95},
                "data-audit": {"score": 0.83, "baseline": 0.95}  # Severe regression delta = -0.12
            },
            simulated_evidence_checks=sim_checks,
            trigger="POST_PROMOTION"
        )

        self.assertEqual(report["verdict"], "CRITICAL_REGRESSION_ROLLBACK")
        self.assertTrue(report["rollback_executed"])

        # Check profile status updated
        prof = self.monitor.get_or_create_profile("statistical-data-analyst", "skill")
        self.assertEqual(prof["status"], "DEGRADED")
        self.assertTrue(prof["last_drift_check"]["drift_detected"])


if __name__ == "__main__":
    unittest.main()
