#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_real_rollback_phase22.py — Unit tests for Phase 22:
Make Rollback Real (Immutable Versions V1, V2, V3 and Authentic Rollback Lifecycle).
"""

import os
import sys
import json
import shutil
import hashlib
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.academic_promotion_engine import (
    AcademicPromotionEngine,
    AcademicVersionStore,
    PromotionFailureError,
    PromotionHashMismatchError
)
from scripts.academic_behavior_drift_monitor import AcademicBehaviorDriftMonitor


class TestRealRollbackPhase22(unittest.TestCase):
    """Verifies immutable version management and authentic rollback (V3 -> V2 -> V1)."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.engine = AcademicPromotionEngine(base_dir=self.test_dir)
        self.version_store = self.engine.version_store

        # Setup a dummy skill target
        self.skill_name = "test-rollback-skill"
        self.skill_dir = os.path.join(self.test_dir, ".agents", "skills", self.skill_name)
        os.makedirs(self.skill_dir, exist_ok=True)
        self.skill_file = os.path.join(self.skill_dir, "SKILL.md")

        self.initial_content = (
            f"---\nname: {self.skill_name}\ndescription: Production skill spec.\n---\n\n"
            f"# {self.skill_name}\n\n"
            f"## Baseline Procedures\n"
            f"1. Execute primary analysis.\n"
            f"2. Report standard metrics.\n"
        )
        with open(self.skill_file, "w", encoding="utf-8") as f:
            f.write(self.initial_content)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_candidate_and_report(self, cand_id: str, mutation_content: str, parent_v: str = None):
        """Helper to create candidate and passing evaluation report."""
        cand_data = {
            "contract_version": "1.0.0",
            "candidate_id": cand_id,
            "target_component": f".agents/skills/{self.skill_name}/SKILL.md",
            "target_type": "SKILL_PROCEDURAL_SPECIFICATION",
            "mutation_type": "VERIFICATION_CHECKPOINT",
            "parent_version": parent_v,
            "mutation": {
                "diff_type": "UNIFIED_DIFF",
                "content": mutation_content,
                "checksum_sha256": hashlib.sha256(mutation_content.encode("utf-8")).hexdigest()
            },
            "status": "CANDIDATE",
            "created_at": "2026-09-19T12:00:00Z"
        }
        cand_path = os.path.join(self.engine.candidates_dir, f"{cand_id}.json")
        with open(cand_path, "w", encoding="utf-8") as f:
            json.dump(cand_data, f, indent=2)

        eval_report = {
            "contract_version": "1.0.0",
            "report_id": f"EVR-{cand_id}",
            "candidate_id": cand_id,
            "heldout_integrity_verified": True,
            "summary_metrics": {
                "total_cases_evaluated": 5,
                "target_capability_improved": True,
                "zero_regressions_verified": True,
                "adversarial_clearance": True,
                "protected_regressions": 0,
                "suite_pass_rates": {
                    "regression": 1.0,
                    "adversarial": 1.0,
                    "heldout": 1.0
                }
            },
            "minimum_improvement_policy": {
                "target_capability_improved": True,
                "zero_regressions_verified": True,
                "adversarial_clearance": True
            },
            "counterfactual_analysis": {
                "what_improved": ["p-value format compliant"],
                "what_regressed": [],
                "which_failure_disappeared": ["p_equals_zero_eliminated"]
            },
            "all_diagnostics": []
        }
        return cand_id, eval_report

    def test_first_promotion_initializes_v1_and_creates_v2(self):
        """First promotion on a component initializes immutable V1 and creates V2 with all 7 fields."""
        diff_v2 = (
            "--- a/SKILL.md\n+++ b/SKILL.md\n@@ -5,2 +5,4 @@\n"
            " 1. Execute primary analysis.\n"
            "+2. Verify p-value reporting: never report p = .000.\n"
            " 3. Report standard metrics.\n"
        )
        cid, report = self._create_candidate_and_report("CAND-001", diff_v2)

        approver = {"identity": "Saber Admin Desk 124911145"}
        result = self.engine.evaluate_and_promote(cid, report, approver=approver)

        self.assertEqual(result["decision"], "PROMOTED")
        self.assertEqual(result["status"], "ACTIVE")

        # 1. Verify V1 was initialized
        v1_dir = os.path.join(self.test_dir, "learning", "versions", self.skill_name, "V1")
        self.assertTrue(os.path.isdir(v1_dir))
        self.assertTrue(os.path.isfile(os.path.join(v1_dir, "SKILL.md")))
        self.assertTrue(os.path.isfile(os.path.join(v1_dir, "version.json")))

        with open(os.path.join(v1_dir, "version.json"), "r", encoding="utf-8") as f:
            v1_json = json.load(f)
        self.assertEqual(v1_json["version_id"], "V1")
        self.assertIsNone(v1_json["parent_version"])
        self.assertEqual(v1_json["evaluation_id"], "BASELINE")
        self.assertEqual(v1_json["promotion_id"], "BASELINE")
        self.assertEqual(v1_json["content_hash"], hashlib.sha256(self.initial_content.encode("utf-8")).hexdigest())

        # 2. Verify V2 was created with all 7 required fields
        v2_dir = os.path.join(self.test_dir, "learning", "versions", self.skill_name, "V2")
        self.assertTrue(os.path.isdir(v2_dir))
        self.assertTrue(os.path.isfile(os.path.join(v2_dir, "SKILL.md")))
        self.assertTrue(os.path.isfile(os.path.join(v2_dir, "version.json")))

        with open(os.path.join(v2_dir, "version.json"), "r", encoding="utf-8") as f:
            v2_json = json.load(f)

        required_7_fields = [
            "version_id",
            "parent_version",
            "content_hash",
            "artifact_hash",
            "evaluation_id",
            "promotion_id",
            "timestamp"
        ]
        for fld in required_7_fields:
            self.assertIn(fld, v2_json, f"Missing required field {fld} in V2 version.json")

        self.assertEqual(v2_json["version_id"], "V2")
        self.assertEqual(v2_json["parent_version"], "V1")
        self.assertEqual(v2_json["evaluation_id"], report["report_id"])
        self.assertEqual(v2_json["promotion_id"], result["promotion_id"])

        # 3. Verify disk file has V2 content and matches active_version in versions.json
        with open(self.skill_file, "r", encoding="utf-8") as f:
            active_content = f.read()
        self.assertEqual(hashlib.sha256(active_content.encode("utf-8")).hexdigest(), v2_json["content_hash"])

        index = self.version_store.get_versions_index(self.skill_name)
        self.assertEqual(index["active_version"], "V2")
        self.assertEqual(len(index["versions"]), 2)

    def test_sequential_promotions_produce_v1_v2_v3(self):
        """Sequential promotions produce immutable V1 -> V2 -> V3 with proper parent lineage."""
        # Promote V2
        diff_v2 = (
            "--- a/SKILL.md\n+++ b/SKILL.md\n@@ -5,2 +5,4 @@\n"
            " 1. Execute primary analysis.\n"
            "+2. Verify p-value reporting: never report p = .000.\n"
            " 3. Report standard metrics.\n"
        )
        cid1, rep1 = self._create_candidate_and_report("CAND-001", diff_v2)
        res1 = self.engine.evaluate_and_promote(cid1, rep1, approver={"identity": "Saber Admin Desk 124911145"})
        self.assertEqual(res1["decision"], "PROMOTED")

        # Promote V3
        diff_v3 = (
            "--- a/SKILL.md\n+++ b/SKILL.md\n@@ -5,3 +5,5 @@\n"
            " 1. Execute primary analysis.\n"
            " 2. Verify p-value reporting: never report p = .000.\n"
            "+3. Enforce Persian leading zero: report ۰.۰۵ instead of .۰۵.\n"
            " 4. Report standard metrics.\n"
        )
        cid2, rep2 = self._create_candidate_and_report("CAND-002", diff_v3)
        res2 = self.engine.evaluate_and_promote(cid2, rep2, approver={"identity": "Saber Admin Desk 124911145"})
        self.assertEqual(res2["decision"], "PROMOTED")

        # Verify V3 exists and points to V2
        v3_dir = os.path.join(self.test_dir, "learning", "versions", self.skill_name, "V3")
        self.assertTrue(os.path.isdir(v3_dir))
        with open(os.path.join(v3_dir, "version.json"), "r", encoding="utf-8") as f:
            v3_json = json.load(f)

        self.assertEqual(v3_json["version_id"], "V3")
        self.assertEqual(v3_json["parent_version"], "V2")

        index = self.version_store.get_versions_index(self.skill_name)
        self.assertEqual(index["active_version"], "V3")
        self.assertEqual(len(index["versions"]), 3)

    def test_rollback_v3_to_v2_physically_restores_v2(self):
        """Rollback V3 -> V2 physically restores immutable V2 content on disk and updates active version."""
        # Setup V1 -> V2 -> V3
        diff_v2 = (
            "--- a/SKILL.md\n+++ b/SKILL.md\n@@ -5,2 +5,4 @@\n"
            " 1. Execute primary analysis.\n"
            "+2. Verify p-value reporting: never report p = .000.\n"
            " 3. Report standard metrics.\n"
        )
        cid1, rep1 = self._create_candidate_and_report("CAND-001", diff_v2)
        self.engine.evaluate_and_promote(cid1, rep1, approver={"identity": "Admin"})

        diff_v3 = (
            "--- a/SKILL.md\n+++ b/SKILL.md\n@@ -5,3 +5,5 @@\n"
            " 1. Execute primary analysis.\n"
            " 2. Verify p-value reporting: never report p = .000.\n"
            "+3. Enforce Persian leading zero: report ۰.۰۵ instead of .۰۵.\n"
            " 4. Report standard metrics.\n"
        )
        cid2, rep2 = self._create_candidate_and_report("CAND-002", diff_v3)
        res_v3 = self.engine.evaluate_and_promote(cid2, rep2, approver={"identity": "Admin"})

        # Get V2 immutable content
        v2_record = self.version_store.get_version(self.skill_name, "V2")
        v2_expected_content = v2_record["content"]
        v2_expected_hash = v2_record["content_hash"]

        # Current state: active is V3
        self.assertEqual(self.version_store.get_active_version(self.skill_name), "V3")

        # Execute Rollback V3 -> V2 via promotion ID
        rollback_res = self.engine.rollback_promotion(res_v3["promotion_id"])
        self.assertEqual(rollback_res["status"], "ROLLED_BACK")
        self.assertEqual(rollback_res["to_version"], "V2")
        self.assertEqual(rollback_res["from_version"], "V3")

        # Check physical file on disk: MUST BE EXACTLY V2 CONTENT
        with open(self.skill_file, "r", encoding="utf-8") as f:
            disk_content = f.read()

        self.assertEqual(disk_content, v2_expected_content)
        self.assertEqual(hashlib.sha256(disk_content.encode("utf-8")).hexdigest(), v2_expected_hash)

        # Check active version in index is now V2
        self.assertEqual(self.version_store.get_active_version(self.skill_name), "V2")

    def test_rollback_v2_to_v1_physically_restores_v1(self):
        """Rollback V2 -> V1 physically restores baseline V1 content on disk."""
        diff_v2 = (
            "--- a/SKILL.md\n+++ b/SKILL.md\n@@ -5,2 +5,4 @@\n"
            " 1. Execute primary analysis.\n"
            "+2. Verify p-value reporting: never report p = .000.\n"
            " 3. Report standard metrics.\n"
        )
        cid1, rep1 = self._create_candidate_and_report("CAND-001", diff_v2)
        res1 = self.engine.evaluate_and_promote(cid1, rep1, approver={"identity": "Admin"})

        # Rollback directly to V1
        rollback_res = self.engine.rollback_to_version(self.skill_name, target_version="V1")
        self.assertEqual(rollback_res["status"], "ROLLED_BACK")
        self.assertEqual(rollback_res["to_version"], "V1")

        # Check disk file: MUST MATCH ORIGINAL INITIAL CONTENT
        with open(self.skill_file, "r", encoding="utf-8") as f:
            disk_content = f.read()

        self.assertEqual(disk_content, self.initial_content)
        self.assertEqual(self.version_store.get_active_version(self.skill_name), "V1")

    def test_tampered_version_artifact_fails_closed(self):
        """If an immutable version file on disk is modified/tampered, rollback fails closed."""
        diff_v2 = (
            "--- a/SKILL.md\n+++ b/SKILL.md\n@@ -5,2 +5,4 @@\n"
            " 1. Execute primary analysis.\n"
            "+2. Verify p-value reporting: never report p = .000.\n"
            " 3. Report standard metrics.\n"
        )
        cid1, rep1 = self._create_candidate_and_report("CAND-001", diff_v2)
        self.engine.evaluate_and_promote(cid1, rep1, approver={"identity": "Admin"})

        diff_v3 = (
            "--- a/SKILL.md\n+++ b/SKILL.md\n@@ -5,3 +5,5 @@\n"
            " 1. Execute primary analysis.\n"
            " 2. Verify p-value reporting: never report p = .000.\n"
            "+3. Enforce Persian leading zero: report ۰.۰۵ instead of .۰۵.\n"
            " 4. Report standard metrics.\n"
        )
        cid2, rep2 = self._create_candidate_and_report("CAND-002", diff_v3)
        self.engine.evaluate_and_promote(cid2, rep2, approver={"identity": "Admin"})

        # Tamper with immutable V2 file
        v2_file = os.path.join(self.test_dir, "learning", "versions", self.skill_name, "V2", "SKILL.md")
        with open(v2_file, "w", encoding="utf-8") as f:
            f.write("# TAMPERED CONTENT THAT DOES NOT MATCH CONTENT_HASH\n")

        # Rollback to V2 must fail closed
        with self.assertRaises(PromotionFailureError) as ctx:
            self.engine.rollback_to_version(self.skill_name, target_version="V2")

        self.assertIn("corrupted or tampered", str(ctx.exception))

        # Active version should remain V3, disk file should NOT be corrupted
        self.assertEqual(self.version_store.get_active_version(self.skill_name), "V3")

    def test_drift_monitor_triggers_immutable_rollback(self):
        """Drift monitor detecting regression triggers authentic rollback to parent immutable version."""
        diff_v2 = (
            "--- a/SKILL.md\n+++ b/SKILL.md\n@@ -5,2 +5,4 @@\n"
            " 1. Execute primary analysis.\n"
            "+2. Verify p-value reporting: never report p = .000.\n"
            " 3. Report standard metrics.\n"
        )
        cid1, rep1 = self._create_candidate_and_report("CAND-001", diff_v2)
        self.engine.evaluate_and_promote(cid1, rep1, approver={"identity": "Admin"})

        diff_v3 = (
            "--- a/SKILL.md\n+++ b/SKILL.md\n@@ -5,3 +5,5 @@\n"
            " 1. Execute primary analysis.\n"
            " 2. Verify p-value reporting: never report p = .000.\n"
            "+3. Enforce Persian leading zero: report ۰.۰۵ instead of .۰۵.\n"
            " 4. Report standard metrics.\n"
        )
        cid2, rep2 = self._create_candidate_and_report("CAND-002", diff_v3)
        self.engine.evaluate_and_promote(cid2, rep2, approver={"identity": "Admin"})

        v2_record = self.version_store.get_version(self.skill_name, "V2")

        # Run drift monitor execute_rollback
        monitor = AcademicBehaviorDriftMonitor(base_dir=self.test_dir)
        rb_res = monitor.execute_rollback(candidate_id=cid2, target_skill=self.skill_name, reason="Critical regression")

        self.assertEqual(rb_res["snapshot_id"], "VERSION_V2")
        self.assertEqual(self.version_store.get_active_version(self.skill_name), "V2")

        with open(self.skill_file, "r", encoding="utf-8") as f:
            disk_content = f.read()
        self.assertEqual(disk_content, v2_record["content"])


if __name__ == "__main__":
    unittest.main()
