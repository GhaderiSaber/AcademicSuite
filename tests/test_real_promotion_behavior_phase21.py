#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_real_promotion_behavior_phase21.py — Acceptance Tests for Physical Promotion & Hash Verification (Phase 21)

Verifies:
1. Physical modification of target SKILL.md on disk upon promotion (H_active != H_baseline).
2. The Target Hash Verification Invariant: Zero-change mutations fail closed with PROMOTION FAILURE.
3. Rollback snapshot records exact baseline content and hash.
4. rollback_promotion() restores exact baseline content and hash H_baseline to disk.
5. Directive 18 ceiling enforcement (<= 500 lines, <= 40,000 bytes) blocks bloated activations.
6. Closed-loop evolution integration physically mutates target skill on disk upon promotion.
"""

import os
import sys
import json
import shutil
import hashlib
import tempfile
import unittest
from datetime import datetime, timezone
from typing import Dict, Any

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.contract_validator import validate_promotion_decision
from scripts.academic_promotion_engine import (
    AcademicPromotionEngine,
    PromotionFailureError,
    PromotionHashMismatchError
)
from scripts.academic_real_behavior_evolution import AcademicRealBehaviorEvolution


class TestRealPromotionBehaviorPhase21(unittest.TestCase):
    """Authoritative test suite for Phase 21: Physical Behavioral Promotion."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_phase21_test_")
        self.engine = AcademicPromotionEngine(base_dir=self.temp_dir)

        # Baseline target skill on disk
        self.target_skill = "apa-reporting"
        self.skill_rel = f".agents/skills/{self.target_skill}/SKILL.md"
        self.skill_path = os.path.join(self.temp_dir, self.skill_rel)
        os.makedirs(os.path.dirname(self.skill_path), exist_ok=True)

        self.initial_skill_content = (
            "---\n"
            f"name: {self.target_skill}\n"
            "description: Generate strictly formatted APA 7th Edition tables.\n"
            "---\n\n"
            f"# {self.target_skill}\n\n"
            "## Baseline Procedures\n"
            "1. Ingest dataset and format tables.\n"
            "2. Report test statistics and p-values.\n"
        )
        with open(self.skill_path, "w", encoding="utf-8") as f:
            f.write(self.initial_skill_content)

        self.initial_skill_hash = hashlib.sha256(self.initial_skill_content.encode("utf-8")).hexdigest()

        # Passing evaluation report
        self.passing_report = {
            "report_id": "EVR-PHASE21-001",
            "report_path": "evals/report.json",
            "report_sha256": hashlib.sha256(b"eval_report").hexdigest(),
            "heldout_integrity_verified": True,
            "summary_metrics": {
                "total_cases_evaluated": 10,
                "target_capability_improved": True,
                "zero_regressions_verified": True,
                "protected_regressions": 0,
                "adversarial_clearance": True,
                "suite_pass_rates": {"heldout": 1.0}
            },
            "minimum_improvement_policy": {
                "target_capability_improved": True,
                "zero_regressions_verified": True,
                "adversarial_clearance": True
            },
            "counterfactual_analysis": {
                "what_improved": ["Resolved p-value zero reporting"],
                "what_regressed": [],
                "which_failure_disappeared": ["REPORTING_P_ZERO"]
            },
            "all_diagnostics": []
        }

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_staged_candidate(
        self,
        candidate_id: str,
        mutation_type: str = "VERIFICATION_CHECKPOINT",
        diff_type: str = "UNIFIED_DIFF",
        content: str = ""
    ) -> Dict[str, Any]:
        candidate = {
            "contract_version": "1.0.0",
            "candidate_id": candidate_id,
            "target_component": self.skill_rel,
            "target_type": "SKILL_PROCEDURAL_SPECIFICATION",
            "target_skill": self.target_skill,
            "parent_version": self.initial_skill_hash,
            "mutation_type": mutation_type,
            "mutation": {
                "diff_type": diff_type,
                "content": content,
                "checksum_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()
            },
            "rationale": "Enforce strict p-value reporting without p = .000.",
            "expected_improvement": {
                "target_metric": "p_zero_errors",
                "baseline_value": 1.0,
                "projected_value": 0.0
            },
            "affected_capabilities": [self.target_skill],
            "author_agent": "skill-evolver",
            "status": "CANDIDATE",
            "staged_at": datetime.now(timezone.utc).isoformat(),
            "source_lessons": ["LSN-APA-001"],
            "testable_hypothesis": "If verification checkpoint is added, p = .000 errors drop to 0."
        }
        cand_path = os.path.join(self.engine.candidates_dir, f"{candidate_id}.json")
        with open(cand_path, "w", encoding="utf-8") as f:
            json.dump(candidate, f, indent=2, ensure_ascii=False)
        return candidate

    def test_01_physical_skill_modification_on_disk_upon_promotion(self):
        """Test 1: Real SKILL.md on disk is physically modified upon promotion (H_active != H_baseline)."""
        cid = "CAND-PHASE21-ACTIVATE-001"
        mutation_diff = (
            "--- a/.agents/skills/apa-reporting/SKILL.md\n"
            "+++ b/.agents/skills/apa-reporting/SKILL.md\n"
            "@@ -5,3 +5,4 @@\n"
            " ## Baseline Procedures\n"
            " 1. Ingest dataset and format tables.\n"
            " 2. Report test statistics and p-values.\n"
            "+3. Enforce p < .001 / ۰.۰۰۱ > p rule; never report p = .000.\n"
        )
        self._create_staged_candidate(
            candidate_id=cid,
            mutation_type="VERIFICATION_CHECKPOINT",
            diff_type="UNIFIED_DIFF",
            content=mutation_diff
        )

        approver = {
            "identity": "Saber Ghaderi (Admin Desk 124911145)",
            "approval_contract_id": "APPR-PHASE21-001",
            "approved_at": datetime.now(timezone.utc).isoformat()
        }

        result = self.engine.evaluate_and_promote(
            candidate_id=cid,
            evaluation_report=self.passing_report,
            approver=approver
        )

        self.assertEqual(result["decision"], "PROMOTED")
        self.assertEqual(result["status"], "ACTIVE")

        # Invariant 1: Physical file on disk must have changed
        with open(self.skill_path, "r", encoding="utf-8") as f:
            promoted_content = f.read()

        promoted_hash = hashlib.sha256(promoted_content.encode("utf-8")).hexdigest()
        self.assertNotEqual(
            promoted_hash,
            self.initial_skill_hash,
            "Target Skill hash did NOT change after promotion! Physical modification failed."
        )

        # Invariant 2: Mutated text must physically exist in SKILL.md on disk
        self.assertIn(
            "Enforce p < .001 / ۰.۰۰۱ > p rule; never report p = .000.",
            promoted_content,
            "Activated mutation content not found in physical SKILL.md!"
        )

        # Invariant 3: Deployment record contains distinct baseline and active hashes
        deployment = result["deployment"]
        self.assertEqual(deployment["baseline_component_hash"], self.initial_skill_hash)
        self.assertEqual(deployment["active_component_hash"], promoted_hash)

    def test_02_zero_change_mutation_triggers_promotion_failure(self):
        """Test 2: If target Skill hash did not change where a change was expected: PROMOTION FAILURE."""
        cid = "CAND-PHASE21-ZEROCHANGE-002"
        # Mutation that leaves content 100% unchanged
        empty_diff = ""
        self._create_staged_candidate(
            candidate_id=cid,
            mutation_type="VERIFICATION_CHECKPOINT",
            diff_type="UNIFIED_DIFF",
            content=empty_diff
        )

        approver = {
            "identity": "Saber Ghaderi (Admin Desk 124911145)",
            "approval_contract_id": "APPR-PHASE21-002",
            "approved_at": datetime.now(timezone.utc).isoformat()
        }

        result = self.engine.evaluate_and_promote(
            candidate_id=cid,
            evaluation_report=self.passing_report,
            approver=approver
        )

        # Must fail closed with PROMOTION_FAILED
        self.assertEqual(result["decision"], "REJECTED")
        self.assertEqual(result["status"], "PROMOTION_FAILED")
        self.assertIn("PROMOTION FAILURE", result["reason"])
        self.assertIn("hash did not change", result["reason"])

        # Invariant: Skill on disk remains 100% identical
        with open(self.skill_path, "r", encoding="utf-8") as f:
            current_content = f.read()
        current_hash = hashlib.sha256(current_content.encode("utf-8")).hexdigest()
        self.assertEqual(current_hash, self.initial_skill_hash)

    def test_03_snapshot_records_exact_original_content_and_hash(self):
        """Test 3: Rollback snapshot contains exact pre-promotion content and hash."""
        cid = "CAND-PHASE21-SNAP-003"
        mutation_diff = (
            "--- a/.agents/skills/apa-reporting/SKILL.md\n"
            "+++ b/.agents/skills/apa-reporting/SKILL.md\n"
            "@@ -5,3 +5,4 @@\n"
            " ## Baseline Procedures\n"
            " 1. Ingest dataset and format tables.\n"
            " 2. Report test statistics and p-values.\n"
            "+3. New procedure step for snapshot test.\n"
        )
        self._create_staged_candidate(
            candidate_id=cid,
            mutation_type="MISSING_STEP_ADDITION",
            diff_type="UNIFIED_DIFF",
            content=mutation_diff
        )

        result = self.engine.evaluate_and_promote(
            candidate_id=cid,
            evaluation_report=self.passing_report,
            approver={"identity": "Saber Admin"}
        )

        snap_path = result["deployment"]["snapshot"]["snapshot_path"]
        self.assertTrue(os.path.isfile(snap_path), f"Snapshot file not created at {snap_path}")

        with open(snap_path, "r", encoding="utf-8") as f:
            snap_data = json.load(f)

        self.assertEqual(snap_data["original_hash"], self.initial_skill_hash)
        self.assertEqual(snap_data["original_content"], self.initial_skill_content)
        self.assertEqual(snap_data["candidate_id"], cid)

    def test_04_rollback_promotion_restores_exact_baseline_content_and_hash(self):
        """Test 4: rollback_promotion() restores exact original content and hash H_baseline."""
        cid = "CAND-PHASE21-ROLLBACK-004"
        mutation_diff = (
            "--- a/.agents/skills/apa-reporting/SKILL.md\n"
            "+++ b/.agents/skills/apa-reporting/SKILL.md\n"
            "@@ -5,3 +5,4 @@\n"
            " ## Baseline Procedures\n"
            " 1. Ingest dataset and format tables.\n"
            " 2. Report test statistics and p-values.\n"
            "+3. Temporary step to be rolled back.\n"
        )
        self._create_staged_candidate(
            candidate_id=cid,
            mutation_type="MISSING_STEP_ADDITION",
            diff_type="UNIFIED_DIFF",
            content=mutation_diff
        )

        result = self.engine.evaluate_and_promote(
            candidate_id=cid,
            evaluation_report=self.passing_report,
            approver={"identity": "Saber Admin"}
        )
        prm_id = result["promotion_id"]

        # Verify promoted
        with open(self.skill_path, "r", encoding="utf-8") as f:
            promoted_content = f.read()
        self.assertIn("Temporary step to be rolled back.", promoted_content)

        # Execute Rollback
        rollback_res = self.engine.rollback_promotion(prm_id)
        self.assertEqual(rollback_res["status"], "ROLLED_BACK")
        self.assertEqual(rollback_res["restored_hash"], self.initial_skill_hash)

        # Verify disk restored to exact initial content and hash
        with open(self.skill_path, "r", encoding="utf-8") as f:
            restored_content = f.read()
        restored_hash = hashlib.sha256(restored_content.encode("utf-8")).hexdigest()

        self.assertEqual(restored_content, self.initial_skill_content)
        self.assertEqual(restored_hash, self.initial_skill_hash)

    def test_05_directive_18_ceiling_enforcement_during_promotion(self):
        """Test 5: Promotion aborts with PROMOTION_FAILED if mutated file exceeds Directive 18 ceilings."""
        cid = "CAND-PHASE21-CEILING-005"
        # Mutation that adds 510 lines
        giant_addition = "\n".join(f"- Bloated line {i}" for i in range(510))
        self._create_staged_candidate(
            candidate_id=cid,
            mutation_type="MISSING_STEP_ADDITION",
            diff_type="FULL_CONTENT_REPLACEMENT",
            content=self.initial_skill_content + "\n" + giant_addition
        )

        result = self.engine.evaluate_and_promote(
            candidate_id=cid,
            evaluation_report=self.passing_report,
            approver={"identity": "Saber Admin"}
        )

        self.assertEqual(result["decision"], "REJECTED")
        self.assertEqual(result["status"], "PROMOTION_FAILED")
        self.assertIn("Directive 18", result["reason"])

        # Verify file was NOT modified on disk
        with open(self.skill_path, "r", encoding="utf-8") as f:
            current_content = f.read()
        self.assertEqual(current_content, self.initial_skill_content)

    def test_06_closed_loop_evolution_modifies_skill_on_disk(self):
        """Test 6: End-to-end 13-stage evolution modifies target skill on disk upon promotion."""
        ev_runner = AcademicRealBehaviorEvolution(base_dir=self.temp_dir)

        trajectory = {
            "trajectory_id": "TRJ-PHASE21-E2E-001",
            "agent": "statistics-agent",
            "skill": self.target_skill,
            "capability": self.target_skill,
            "ordered_actions": [
                {
                    "step": 1,
                    "action": "execute",
                    "output": "Table generated with p = .000"
                }
            ]
        }

        feedback = {
            "target_agent": "statistics-agent",
            "target_skill": self.target_skill,
            "capability": self.target_skill,
            "correction": "p = .000 is prohibited. Use p < .001.",
            "desired_behavior": "Enforce APA 7 p-value reporting rules."
        }

        approver = {
            "identity": "Saber Ghaderi (Admin Desk 124911145)",
            "approval_contract_id": "APPR-E2E-001",
            "approved_at": datetime.now(timezone.utc).isoformat()
        }

        res = ev_runner.execute_closed_loop(
            trigger_type="USER_FEEDBACK",
            trigger_payload=feedback,
            trajectory_data=trajectory,
            approver=approver
        )

        self.assertEqual(res["status"], "COMPLETED")
        self.assertIsNotNone(res["promotion_result"])
        self.assertEqual(res["promotion_result"]["decision"], "PROMOTED")

        # Verify physical modification on disk
        with open(self.skill_path, "r", encoding="utf-8") as f:
            final_content = f.read()
        final_hash = hashlib.sha256(final_content.encode("utf-8")).hexdigest()

        self.assertNotEqual(final_hash, self.initial_skill_hash)
        self.assertTrue(len(final_content) > len(self.initial_skill_content))


if __name__ == "__main__":
    unittest.main()
