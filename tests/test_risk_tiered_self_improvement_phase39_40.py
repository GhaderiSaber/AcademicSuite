#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_risk_tiered_self_improvement_phase39_40.py

Comprehensive tests for:
- Phase 39: 7-Stage Gated Self-Improvement Lifecycle
  OBSERVATION -> CANDIDATE -> SANDBOX -> EVALUATION -> PROMOTION_CANDIDATE -> HUMAN_QUALITY_GATE -> PRODUCTION
- Phase 40: 6-Tier Change-Risk Taxonomy (Levels 0–5)
  Level 0 — Formatting (Automatic)
  Level 1 — Retrieval/Context (Automatic after tests)
  Level 2 — Workflow Guidance (Evaluation required)
  Level 3 — Statistical Decision Logic (Independent + held-out + adversarial)
  Level 4 — Methodology Behavior (Strong validation + explicit human approval)
  Level 5 — Statistical Computation (Permanently blocked via prompt mutation; deterministic code only)
"""

import os
import json
import shutil
import tempfile
import hashlib
import unittest
from datetime import datetime, timezone

from scripts.academic_promotion_engine import (
    AcademicPromotionEngine,
    PromotionEngineError,
    Level5StatisticalComputationModificationBlockedError,
    HumanApprovalRequiredForMethodologyChangeError
)


class TestRiskTieredSelfImprovementPhase39And40(unittest.TestCase):
    """Test suite validating Phase 39 and Phase 40 invariants."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_p39_p40_")
        self.engine = AcademicPromotionEngine(base_dir=self.temp_dir)
        self.passing_report = {
            "report_id": "CCR-20260918-MOCK001",
            "report_path": "learning/evaluations/reports/CCR-20260918-MOCK001.json",
            "report_sha256": hashlib.sha256(b"mock_report").hexdigest(),
            "heldout_integrity_verified": True,
            "verdict": "PASS",
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

    def _create_candidate(self, cid, mutation_type="EXEMPLAR_ADDITION", target_comp=".agents/skills/apa-reporting/SKILL.md", target_type="SKILL_PROCEDURAL_SPECIFICATION", content="Content", rationale="Rationale", **kwargs):
        candidate = {
            "contract_version": "1.0.0",
            "candidate_id": cid,
            "target_component": target_comp,
            "target_type": target_type,
            "target_skill": "chapter-4-writing",
            "parent_version": hashlib.sha256(b"parent").hexdigest(),
            "mutation_type": mutation_type,
            "mutation": {"diff_type": "UNIFIED_DIFF", "content": content, "checksum_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()},
            "rationale": rationale,
            "expected_improvement": {"target_metric": "test_pass_rate", "baseline_value": 0.0, "projected_value": 1.0},
            "affected_capabilities": ["chapter-4-writing"],
            "author_agent": "skill-evolver",
            "status": "CANDIDATE",
            "staged_at": datetime.now(timezone.utc).isoformat()
        }
        candidate.update(kwargs)
        cand_path = os.path.join(self.engine.candidates_dir, f"{cid}.json")
        with open(cand_path, "w", encoding="utf-8") as f:
            json.dump(candidate, f, indent=2)
        return candidate

    def test_01_risk_level_classification_accuracy(self):
        """Confirms accurate classification across Levels 0 through 5."""
        # Level 0: Formatting / exemplar
        c0 = self._create_candidate("C-0", mutation_type="EXEMPLAR_ADDITION", content="### Exemplar: clear table")
        self.assertEqual(self.engine.classify_risk_level(c0), self.engine.LEVEL_0_FORMATTING)
        self.assertEqual(self.engine.classify_risk(c0), "LOW_RISK")

        # Level 1: Retrieval / Context
        c1 = self._create_candidate("C-1", mutation_type="RETRIEVAL_IMPROVEMENT", target_comp=".agents/skills/academic-adaptive-context/SKILL.md")
        self.assertEqual(self.engine.classify_risk_level(c1), self.engine.LEVEL_1_RETRIEVAL_CONTEXT)
        self.assertEqual(self.engine.classify_risk(c1), "LOW_RISK")

        # Level 2: Workflow Guidance
        c2 = self._create_candidate("C-2", mutation_type="MISSING_STEP_ADDITION", target_comp=".agents/skills/academic-orchestrator/SKILL.md", content="Stage 4.5 handoff")
        self.assertEqual(self.engine.classify_risk_level(c2), self.engine.LEVEL_2_WORKFLOW_GUIDANCE)
        self.assertEqual(self.engine.classify_risk(c2), "MEDIUM_RISK")

        # Level 3: Statistical Decision Logic
        c3 = self._create_candidate("C-3", mutation_type="DECISION_TREE_ADDITION", target_comp=".agents/skills/assumption-testing/SKILL.md", content="Normality threshold skewness cutoff 2.0")
        self.assertEqual(self.engine.classify_risk_level(c3), self.engine.LEVEL_3_STATISTICAL_DECISION_LOGIC)
        self.assertEqual(self.engine.classify_risk(c3), "MEDIUM_RISK")

        # Level 4: Methodology Behavior
        c4 = self._create_candidate("C-4", mutation_type="METHODOLOGY_CHANGE", target_comp=".agents/skills/methodology-review/SKILL.md", content="Causal inference validity checklist")
        self.assertEqual(self.engine.classify_risk_level(c4), self.engine.LEVEL_4_METHODOLOGY_BEHAVIOR)
        self.assertEqual(self.engine.classify_risk(c4), "HIGH_RISK")

        # Level 5: Statistical Computation
        c5 = self._create_candidate("C-5", mutation_type="INSTRUCTION_REFINEMENT", target_comp=".agents/skills/sem/scripts/run_sem.py", content="Alter matrix inversion calculation")
        self.assertEqual(self.engine.classify_risk_level(c5), self.engine.LEVEL_5_STATISTICAL_COMPUTATION)
        self.assertEqual(self.engine.classify_risk(c5), "HIGH_RISK")

    def test_02_level_0_formatting_automatic_promotion(self):
        """Level 0 formatting candidate promotes automatically to ACTIVE."""
        cid = "CAND-L0-FMT-001"
        self._create_candidate(cid, mutation_type="EXEMPLAR_ADDITION", content="### Exemplar: strict OpenXML table formatting")
        res = self.engine.evaluate_and_promote(cid, self.passing_report)

        self.assertEqual(res["decision"], "PROMOTED")
        self.assertEqual(res["status"], "ACTIVE")
        self.assertEqual(res["risk_level"], self.engine.LEVEL_0_FORMATTING)
        self.assertEqual(res["governance_gate"], "AUTOMATIC")

    def test_03_level_1_retrieval_context_automatic_after_tests(self):
        """Level 1 retrieval/context candidate promotes automatically after test pass."""
        cid = "CAND-L1-RET-001"
        self._create_candidate(cid, mutation_type="RETRIEVAL_IMPROVEMENT", target_comp=".agents/skills/academic-adaptive-context/SKILL.md", content="Filter query expansion")
        res = self.engine.evaluate_and_promote(cid, self.passing_report)

        self.assertEqual(res["decision"], "PROMOTED")
        self.assertEqual(res["status"], "ACTIVE")
        self.assertEqual(res["risk_level"], self.engine.LEVEL_1_RETRIEVAL_CONTEXT)
        self.assertEqual(res["governance_gate"], "AUTOMATIC_AFTER_TESTS")

    def test_04_level_2_workflow_guidance_requires_evaluation(self):
        """Level 2 workflow guidance requires evaluation; fails if gates fail, succeeds if passed."""
        cid = "CAND-L2-WKF-001"
        self._create_candidate(cid, mutation_type="MISSING_STEP_ADDITION", target_comp=".agents/skills/chapter-4-writing/SKILL.md", content="Verification step before final report")

        # Failing evaluation gate with regressions
        failing_report = dict(self.passing_report)
        failing_report["verdict"] = "FAIL"
        failing_report["regression_results"] = {"verdict": "FAIL", "count": 2, "details": ["Regressed on step 3"]}
        failing_report["summary_metrics"] = dict(self.passing_report["summary_metrics"], target_capability_improved=False, zero_regressions_verified=False, protected_regressions=2)
        failing_report["counterfactual_analysis"] = {"what_improved": [], "what_regressed": ["[CH4-001] Step broken"]}
        failing_report["minimum_improvement_policy"] = {"target_capability_improved": False, "zero_regressions_verified": False}
        res_fail = self.engine.evaluate_and_promote(cid, failing_report)
        self.assertEqual(res_fail["decision"], "REJECTED")

        # Passing evaluation with auto-promote authorized
        cid_pass = "CAND-L2-WKF-002"
        self._create_candidate(cid_pass, mutation_type="MISSING_STEP_ADDITION", target_comp=".agents/skills/chapter-4-writing/SKILL.md", content="Step 2 verification", auto_promote_on_evaluation_pass=True)
        res_pass = self.engine.evaluate_and_promote(cid_pass, self.passing_report)
        self.assertEqual(res_pass["decision"], "PROMOTED")
        self.assertEqual(res_pass["governance_gate"], "EVALUATION_VERIFIED")

    def test_05_level_3_statistical_decision_requires_heldout_and_adversarial(self):
        """Level 3 statistical decision logic requires held-out and adversarial gates."""
        cid = "CAND-L3-STAT-001"
        self._create_candidate(cid, mutation_type="DECISION_TREE_ADDITION", target_comp=".agents/skills/assumption-testing/SKILL.md", content="Normality cutoff skewness 2.0")

        # Adversarial failure rejects
        adv_fail_report = dict(self.passing_report)
        adv_fail_report["adversarial_results"] = {"verdict": "FAIL", "creates_new_mistake": True}
        adv_fail_report["summary_metrics"] = dict(self.passing_report["summary_metrics"], adversarial_clearance=False)
        res_adv_fail = self.engine.evaluate_and_promote(cid, adv_fail_report)
        self.assertEqual(res_adv_fail["decision"], "REJECTED")

        # When all pass and approver provided, promotes
        cid_pass = "CAND-L3-STAT-002"
        self._create_candidate(cid_pass, mutation_type="DECISION_TREE_ADDITION", target_comp=".agents/skills/assumption-testing/SKILL.md", content="Normality decision tree")
        res_pass = self.engine.evaluate_and_promote(cid_pass, self.passing_report, approver={"identity": "Saber Admin Desk 124911145"})
        self.assertEqual(res_pass["decision"], "PROMOTED")
        self.assertEqual(res_pass["governance_gate"], "INDEPENDENT_HELDOUT_ADVERSARIAL_VERIFIED")

    def test_06_level_4_methodology_blocks_without_human_approval(self):
        """Level 4 methodology behavior change blocks without human approval and succeeds with approval."""
        cid = "CAND-L4-METH-001"
        self._create_candidate(cid, mutation_type="METHODOLOGY_CHANGE", target_comp=".agents/skills/methodology-review/SKILL.md", content="Causal inference validity threats")

        # Gate holds without human approver
        res_hold = self.engine.evaluate_and_promote(cid, self.passing_report, approver=None)
        self.assertEqual(res_hold["decision"], "STAGED_FOR_FURTHER_TESTING")
        self.assertEqual(res_hold["status"], "VALIDATED")

        # Promotion succeeds with signed human approval
        res_approved = self.engine.evaluate_and_promote(cid, self.passing_report, approver={"identity": "Saber Admin Desk 124911145"})
        self.assertEqual(res_approved["decision"], "PROMOTED")
        self.assertEqual(res_approved["governance_gate"], "HUMAN_APPROVED")

    def test_07_level_5_statistical_computation_fatally_rejected(self):
        """Level 5 prompt-based calculation changes are fatally rejected and archived."""
        cid = "CAND-L5-COMP-001"
        self._create_candidate(cid, mutation_type="INSTRUCTION_REFINEMENT", target_comp=".agents/skills/sem/scripts/run_sem.py", content="Alter degrees of freedom formula calculation")

        # Fatal rejection even if human approver is supplied
        res = self.engine.evaluate_and_promote(cid, self.passing_report, approver={"identity": "Saber Admin Desk 124911145"})
        self.assertEqual(res["decision"], "REJECTED")
        self.assertEqual(res["status"], "REJECTED_AND_ARCHIVED")
        self.assertEqual(res["governance_gate"], "PROHIBITED_COMPUTATION")

        # Progressing candidate through lifecycle to HUMAN_QUALITY_GATE raises exception
        cid_life = "CAND-L5-LIFE-001"
        self._create_candidate(cid_life, mutation_type="INSTRUCTION_REFINEMENT", target_comp=".agents/skills/sem/scripts/run_sem.py", content="Alter degrees of freedom formula calculation")
        self.engine.progress_candidate_lifecycle(cid_life, "SANDBOX")
        self.engine.progress_candidate_lifecycle(cid_life, "EVALUATION")
        self.engine.progress_candidate_lifecycle(cid_life, "PROMOTION_CANDIDATE", evidence=self.passing_report)
        with self.assertRaises(Level5StatisticalComputationModificationBlockedError):
            self.engine.progress_candidate_lifecycle(cid_life, "HUMAN_QUALITY_GATE", evidence=self.passing_report)

    def test_08_seven_stage_lifecycle_progression(self):
        """Validates sequential 7-stage lifecycle progression and disallows skipping stages."""
        cid = "CAND-LIFE-001"
        self._create_candidate(cid, mutation_type="EXEMPLAR_ADDITION", content="### Exemplar: High quality writing")

        # Stage 1: OBSERVATION
        s1 = self.engine.progress_candidate_lifecycle(cid, "OBSERVATION")
        self.assertEqual(s1["status"], "OBSERVATION")

        # Stage 2: CANDIDATE
        s2 = self.engine.progress_candidate_lifecycle(cid, "CANDIDATE")
        self.assertEqual(s2["status"], "CANDIDATE")

        # Disallow skipping to PRODUCTION directly
        with self.assertRaises(PromotionEngineError) as ctx:
            self.engine.progress_candidate_lifecycle(cid, "PRODUCTION")
        self.assertIn("INVALID_LIFECYCLE_TRANSITION", str(ctx.exception))

        # Stage 3: SANDBOX
        s3 = self.engine.progress_candidate_lifecycle(cid, "SANDBOX")
        self.assertEqual(s3["status"], "SANDBOX")
        self.assertTrue(os.path.isdir(s3["sandbox_dir"]))

        # Stage 4: EVALUATION
        s4 = self.engine.progress_candidate_lifecycle(cid, "EVALUATION")
        self.assertEqual(s4["status"], "EVALUATION")

        # Stage 5: PROMOTION_CANDIDATE (requires passing report)
        s5 = self.engine.progress_candidate_lifecycle(cid, "PROMOTION_CANDIDATE", evidence=self.passing_report)
        self.assertEqual(s5["status"], "PROMOTION_CANDIDATE")

        # Stage 6: HUMAN_QUALITY_GATE
        s6 = self.engine.progress_candidate_lifecycle(cid, "HUMAN_QUALITY_GATE", evidence=self.passing_report)
        self.assertEqual(s6["status"], "HUMAN_QUALITY_GATE")

        # Stage 7: PRODUCTION
        s7 = self.engine.progress_candidate_lifecycle(cid, "PRODUCTION", evidence=self.passing_report)
        self.assertEqual(s7["status"], "PRODUCTION")

    def test_09_directive_18_single_view_budget(self):
        """Verifies this test file satisfies Directive 18 ceilings (<= 500 lines, <= 40,000 bytes)."""
        current_file = __file__
        with open(current_file, "r", encoding="utf-8") as f:
            content = f.read()
        lines = content.splitlines()
        self.assertLessEqual(len(lines), 500, f"Line count {len(lines)} exceeds 500 lines.")
        self.assertLessEqual(len(content.encode("utf-8")), 40000, f"Byte size {len(content.encode('utf-8'))} exceeds 40,000 bytes.")


if __name__ == "__main__":
    unittest.main()
