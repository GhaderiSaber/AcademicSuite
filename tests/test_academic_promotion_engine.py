#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_promotion_engine.py — Unit Tests for AcademicPromotionEngine

Verifies:
1. 6-stage lifecycle progression: OBSERVED → LESSON → CANDIDATE → EVALUATED → VALIDATED → ACTIVE.
2. LOW-RISK candidates (exemplar, anti-pattern, retrieval metadata, minor clarification)
   auto-promote to ACTIVE when all 5 evaluation gates pass.
3. MEDIUM-RISK candidates (decision-tree, instruction refinement) remain reviewable
   at VALIDATED/STAGED_FOR_REVIEW without an explicit approver.
4. MEDIUM-RISK candidates transition to ACTIVE when human approver credentials are provided.
5. HIGH-RISK architectural components (permissions, hooks, contracts, validators, state machine,
   statistical execution, MCP access, raw-data security) are strictly prohibited and hard-rejected.
6. Candidates failing any protected capability or evaluation gate are rejected.
7. Rejected candidates are archived under learning/archive/ with failure reason, evaluation evidence,
   and affected cases (never deleted).
8. Every active change maintains complete evaluation evidence, rollback snapshot, and lineage.
"""

import os
import sys
import json
import uuid
import shutil
import hashlib
import tempfile
import unittest
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.academic_promotion_engine import (
    AcademicPromotionEngine,
    PromotionEngineError,
    HighRiskModificationProhibitedError,
    EvaluationGateFailureError
)
from contracts.contract_validator import validate_promotion_decision


class TestAcademicPromotionEngine(unittest.TestCase):
    """Authoritative test suite for the AcademicPromotionEngine."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_promotion_test_")
        self.engine = AcademicPromotionEngine(base_dir=self.temp_dir)

        # Baseline evaluation report passing all 5 gates
        self.passing_report = {
            "report_id": "CCR-20260918-MOCK001",
            "report_path": "learning/evaluations/reports/CCR-20260918-MOCK001.json",
            "report_sha256": hashlib.sha256(b"mock_report").hexdigest(),
            "heldout_integrity_verified": True,
            "summary_metrics": {
                "total_cases_evaluated": 15,
                "baseline_passes": 10,
                "candidate_passes": 15,
                "target_capability_improved": True,
                "zero_regressions_verified": True,
                "protected_regressions": 0,
                "adversarial_clearance": True,
                "suite_pass_rates": {
                    "original_failure": 1.0,
                    "related": 1.0,
                    "regression": 1.0,
                    "adversarial": 1.0,
                    "heldout": 1.0
                }
            },
            "minimum_improvement_policy": {
                "target_capability_improved": True,
                "zero_regressions_verified": True,
                "adversarial_clearance": True,
                "promotion_eligible": True
            },
            "counterfactual_analysis": {
                "what_improved": ["[EVAL-REG-LMM-001] Resolved model comparison defect"],
                "what_regressed": [],
                "which_failure_disappeared": ["unjustified_model_selection_without_comparison"],
                "which_new_failure_appeared": []
            },
            "all_diagnostics": []
        }

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_mock_candidate(
        self,
        candidate_id: str,
        mutation_type: str = "EXEMPLAR_ADDITION",
        target_component: str = ".agents/skills/chapter-4-writing/SKILL.md",
        target_type: str = "SKILL_PROCEDURAL_SPECIFICATION",
        content: str = "Mock exemplar content"
    ) -> dict:
        """Helper to create and stage a mock candidate on disk."""
        candidate = {
            "contract_version": "1.0.0",
            "candidate_id": candidate_id,
            "target_component": target_component,
            "target_type": target_type,
            "target_skill": "chapter-4-writing",
            "parent_version": hashlib.sha256(b"mock_parent").hexdigest(),
            "mutation_type": mutation_type,
            "mutation": {
                "diff_type": "UNIFIED_DIFF",
                "content": content,
                "checksum_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()
            },
            "rationale": "Empirical resolution of model comparison defect.",
            "expected_improvement": {
                "target_metric": "model_comparison_pass_rate",
                "baseline_value": 0.0,
                "projected_value": 1.0
            },
            "affected_capabilities": ["chapter-4-writing", "statistical-data-analyst"],
            "author_agent": "skill-evolver",
            "status": "CANDIDATE",
            "staged_at": datetime.now(timezone.utc).isoformat(),
            "source_lessons": ["LSN-20260918-001"],
            "associated_pitfall_id": "EXP-FEEDBACK-001",
            "testable_hypothesis": "If candidate is applied, pass rate increases to 1.0."
        }
        cand_file = os.path.join(self.engine.candidates_dir, f"{candidate_id}.json")
        with open(cand_file, "w", encoding="utf-8") as f:
            json.dump(candidate, f, indent=2, ensure_ascii=False)
        return candidate

    def test_01_six_stage_lifecycle_state_progression(self):
        """Engine supports the 6-stage lifecycle: OBSERVED -> LESSON -> CANDIDATE -> EVALUATED -> VALIDATED -> ACTIVE."""
        expected_stages = ["OBSERVED", "LESSON", "CANDIDATE", "EVALUATED", "VALIDATED", "ACTIVE"]
        self.assertEqual(self.engine.LIFECYCLE_STAGES, expected_stages)

    def test_02_low_risk_auto_promotion(self):
        """LOW-RISK candidates (exemplar, anti-pattern, retrieval metadata) automatically promote to ACTIVE."""
        cid = "CAND-LOWRISK-EXM-001"
        self._create_mock_candidate(
            candidate_id=cid,
            mutation_type="EXEMPLAR_ADDITION",
            content="### Exemplar: High quality model comparison narrative"
        )

        result = self.engine.evaluate_and_promote(
            candidate_id=cid,
            evaluation_report=self.passing_report
        )

        self.assertEqual(result["decision"], "PROMOTED")
        self.assertEqual(result["status"], "ACTIVE")
        self.assertEqual(result["risk_tier"], "LOW_RISK")
        self.assertIn("promotion_id", result)

        # Verify candidate updated on disk to ACTIVE
        cand_path = os.path.join(self.engine.candidates_dir, f"{cid}.json")
        with open(cand_path, "r", encoding="utf-8") as f:
            updated_cand = json.load(f)
        self.assertEqual(updated_cand["status"], "ACTIVE")

        # Verify active exemplar deployed in learning/knowledge/exemplars/
        exm_dir = os.path.join(self.engine.knowledge_dir, "exemplars")
        self.assertTrue(os.path.isdir(exm_dir))
        self.assertTrue(len(os.listdir(exm_dir)) > 0)

        # Verify PRM record exists and conforms to contract
        prm_file = os.path.join(self.engine.promotions_dir, f"{result['promotion_id']}.json")
        self.assertTrue(os.path.isfile(prm_file))
        with open(prm_file, "r", encoding="utf-8") as f:
            prm_data = json.load(f)
        val = validate_promotion_decision(prm_data)
        self.assertTrue(val["valid"], f"Promotion decision failed validation: {val.get('errors')}")
        self.assertEqual(prm_data["approver"]["identity"], "SYSTEM_AUTONOMOUS_POLICY")

    def test_03_medium_risk_review_gate_holds_without_approver(self):
        """MEDIUM-RISK candidates pass evaluation gates but pause at VALIDATED when human approver is absent."""
        cid = "CAND-MEDRISK-TREE-001"
        self._create_mock_candidate(
            candidate_id=cid,
            mutation_type="DECISION_TREE_ADDITION",
            target_type="SKILL_PROCEDURAL_SPECIFICATION",
            content="```mermaid\ngraph TD\nA[Repeated Measures] --> B[LMM]\n```"
        )

        result = self.engine.evaluate_and_promote(
            candidate_id=cid,
            evaluation_report=self.passing_report,
            approver=None
        )

        self.assertEqual(result["decision"], "STAGED_FOR_FURTHER_TESTING")
        self.assertEqual(result["status"], "VALIDATED")
        self.assertEqual(result["risk_tier"], "MEDIUM_RISK")

        # Verify candidate on disk is marked VALIDATED, NOT ACTIVE
        cand_path = os.path.join(self.engine.candidates_dir, f"{cid}.json")
        with open(cand_path, "r", encoding="utf-8") as f:
            updated_cand = json.load(f)
        self.assertEqual(updated_cand["status"], "VALIDATED")

    def test_04_medium_risk_promotes_with_human_approver(self):
        """MEDIUM-RISK candidates transition to ACTIVE when approved with human reviewer credentials."""
        cid = "CAND-MEDRISK-TREE-002"
        self._create_mock_candidate(
            candidate_id=cid,
            mutation_type="DECISION_TREE_ADDITION",
            target_type="SKILL_PROCEDURAL_SPECIFICATION",
            content="```mermaid\ngraph TD\nA[Repeated Measures] --> B[LMM]\n```"
        )

        approver_credentials = {
            "identity": "Saber Ghaderi (Admin Desk 124911145)",
            "approval_contract_id": "APPR-20260918-999",
            "approved_at": datetime.now(timezone.utc).isoformat()
        }

        result = self.engine.evaluate_and_promote(
            candidate_id=cid,
            evaluation_report=self.passing_report,
            approver=approver_credentials
        )

        self.assertEqual(result["decision"], "PROMOTED")
        self.assertEqual(result["status"], "ACTIVE")
        self.assertEqual(result["risk_tier"], "MEDIUM_RISK")

        # Verify candidate updated to ACTIVE
        cand_path = os.path.join(self.engine.candidates_dir, f"{cid}.json")
        with open(cand_path, "r", encoding="utf-8") as f:
            updated_cand = json.load(f)
        self.assertEqual(updated_cand["status"], "ACTIVE")

        # Verify PRM record valid
        prm_file = os.path.join(self.engine.promotions_dir, f"{result['promotion_id']}.json")
        with open(prm_file, "r", encoding="utf-8") as f:
            prm_data = json.load(f)
        val = validate_promotion_decision(prm_data)
        self.assertTrue(val["valid"], f"PRM validation failed: {val.get('errors')}")
        self.assertEqual(prm_data["approver"]["identity"], "Saber Ghaderi (Admin Desk 124911145)")

    def test_05_high_risk_components_strictly_prohibited_and_rejected(self):
        """Evolution engine must NEVER automatically modify high-risk architectural components."""
        high_risk_targets = [
            (".agents/hooks.json", "SKILL_PROCEDURAL_SPECIFICATION", "Modifying lifecycle hooks"),
            ("contracts/evolution/feedback.schema.json", "SKILL_PROCEDURAL_SPECIFICATION", "Modifying contracts"),
            (".agents/verification/transcript_and_rule_guard.py", "SKILL_DETERMINISTIC_SCRIPT", "Modifying validators"),
            ("scripts/academic_state_manager.py", "SKILL_DETERMINISTIC_SCRIPT", "Modifying state machine"),
            (".agents/skills/sem/scripts/run_sem.py", "SKILL_DETERMINISTIC_SCRIPT", "Modifying deterministic statistical execution"),
            ("data/datasets/raw_data.sav", "SKILL_PROCEDURAL_SPECIFICATION", "Modifying raw data")
        ]

        for target_comp, target_type, desc in high_risk_targets:
            cid = f"CAND-HIGHRISK-{uuid.uuid4().hex[:6]}"
            self._create_mock_candidate(
                candidate_id=cid,
                mutation_type="INSTRUCTION_REFINEMENT",
                target_component=target_comp,
                target_type=target_type,
                content=f"Dangerous high-risk change: {desc}"
            )

            result = self.engine.evaluate_and_promote(
                candidate_id=cid,
                evaluation_report=self.passing_report
            )

            self.assertEqual(result["decision"], "REJECTED")
            self.assertEqual(result["status"], "REJECTED_AND_ARCHIVED")
            self.assertEqual(result["risk_tier"], "HIGH_RISK")
            self.assertIn("HIGH_RISK_COMPONENT_PROHIBITED", result["reason"])

            # Verify archived in learning/archive/
            arc_path = os.path.join(self.engine.archive_dir, f"{result['archive_id']}.json")
            self.assertTrue(os.path.isfile(arc_path))
            with open(arc_path, "r", encoding="utf-8") as f:
                arc_data = json.load(f)
            self.assertEqual(arc_data["status"], "REJECTED_AND_ARCHIVED")
            self.assertIn("HIGH_RISK_COMPONENT_PROHIBITED", arc_data["failure_reason"])

    def test_06_failure_on_protected_capability_rejects_and_archives(self):
        """A candidate that causes a regression on protected capabilities is rejected and archived (never deleted)."""
        cid = "CAND-REGRESSIVE-001"
        self._create_mock_candidate(
            candidate_id=cid,
            mutation_type="EXEMPLAR_ADDITION",
            content="Exemplar that accidentally breaks ANCOVA assumptions"
        )

        failing_report = json.loads(json.dumps(self.passing_report))
        failing_report["summary_metrics"]["zero_regressions_verified"] = False
        failing_report["summary_metrics"]["protected_regressions"] = 1
        failing_report["minimum_improvement_policy"]["zero_regressions_verified"] = False
        failing_report["counterfactual_analysis"]["what_regressed"] = [
            "[EVAL-REG-SLOPE-001] New regression: omitted_critical_assumption"
        ]

        result = self.engine.evaluate_and_promote(
            candidate_id=cid,
            evaluation_report=failing_report
        )

        self.assertEqual(result["decision"], "REJECTED")
        self.assertEqual(result["status"], "REJECTED_AND_ARCHIVED")
        self.assertIn("archive_id", result)

        # Verify candidate file on disk is marked REJECTED and NOT deleted
        cand_path = os.path.join(self.engine.candidates_dir, f"{cid}.json")
        self.assertTrue(os.path.isfile(cand_path), "Rejected candidate file must NOT be deleted")
        with open(cand_path, "r", encoding="utf-8") as f:
            cand_data = json.load(f)
        self.assertEqual(cand_data["status"], "REJECTED")

        # Verify archive record contains failure reason, evaluation evidence, affected cases
        arc_file = os.path.join(self.engine.archive_dir, f"{result['archive_id']}.json")
        self.assertTrue(os.path.isfile(arc_file))
        with open(arc_file, "r", encoding="utf-8") as f:
            arc_data = json.load(f)
        self.assertIn("EVAL-REG-SLOPE-001", arc_data["affected_cases"])
        self.assertIn("regression(s) on protected capabilities", arc_data["failure_reason"])
        self.assertIn("evaluation_evidence", arc_data)

    def test_07_failed_adversarial_or_heldout_gate_rejects_candidate(self):
        """Candidates failing adversarial checks or held-out generalization are rejected."""
        cid = "CAND-ADV-FAIL-001"
        self._create_mock_candidate(candidate_id=cid, mutation_type="EXEMPLAR_ADDITION")

        adv_fail_report = json.loads(json.dumps(self.passing_report))
        adv_fail_report["summary_metrics"]["adversarial_clearance"] = False
        adv_fail_report["minimum_improvement_policy"]["adversarial_clearance"] = False

        result = self.engine.evaluate_and_promote(
            candidate_id=cid,
            evaluation_report=adv_fail_report
        )

        self.assertEqual(result["decision"], "REJECTED")
        self.assertEqual(result["status"], "REJECTED_AND_ARCHIVED")
        self.assertIn("adversarial", str(result["gate_failures"]).lower())

    def test_08_immutable_lineage_and_audit_trail_recorded(self):
        """Every active change records evaluation evidence, snapshot, and provenance lineage."""
        cid = "CAND-LINEAGE-001"
        self._create_mock_candidate(
            candidate_id=cid,
            mutation_type="ANTI_PATTERN_ADDITION",
            content="### Anti-Pattern: Omitting Mauchly Sphericity"
        )

        result = self.engine.evaluate_and_promote(
            candidate_id=cid,
            evaluation_report=self.passing_report
        )

        self.assertEqual(result["status"], "ACTIVE")
        prm_file = os.path.join(self.engine.promotions_dir, f"{result['promotion_id']}.json")
        with open(prm_file, "r", encoding="utf-8") as f:
            prm_data = json.load(f)

        # Verify lineage tracking
        self.assertIn("lineage", prm_data)
        self.assertEqual(prm_data["lineage"]["candidate_id"], cid)
        self.assertIn("source_lessons", prm_data["lineage"])
        self.assertEqual(prm_data["lineage"]["lifecycle_state"], "ACTIVE")

        # Verify evaluation evidence is sealed with checksum
        self.assertIn("evaluation_evidence", prm_data)
        self.assertEqual(prm_data["evaluation_evidence"]["verdict"], "PASS")
        self.assertEqual(prm_data["evaluation_evidence"]["report_sha256"], self.passing_report["report_sha256"])

        # Verify rollback snapshot
        self.assertIn("rollback_snapshot", prm_data)
        snap_path = prm_data["rollback_snapshot"]["snapshot_path"]
        self.assertTrue(os.path.isfile(snap_path))


if __name__ == "__main__":
    unittest.main()
