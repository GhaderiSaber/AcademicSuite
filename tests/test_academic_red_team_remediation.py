#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_red_team_remediation.py — Authoritative Red-Team Regression Test Suite

Verifies deterministic remediation of all P0/P1 vulnerabilities documented in
docs/evolution/06_SELF_IMPROVEMENT_RED_TEAM.md under the principle:
"EXPERIENCE IS EVIDENCE, NOT TRUTH."

Coverage:
- ATK-01: Project-specific preference quarantined from global propagation.
- ATK-02: Bad Skill poisoning via discredited methodology (Sobel test) blocked.
- ATK-03: Automatic promotion blocked when evidence count is below threshold (< 3).
- ATK-04: Overfitting detected and blocks promotion.
- ATK-06: Contradictory lessons suppressed from pre-task briefing.
- ATK-07: Cross-domain isolation blocks quantitative rules from qualitative queries.
- ATK-10: Curriculum generator enforces complexity floor (Level >= 3).
- ATK-11: Curriculum generator validates synthetic mathematical/psychometric parameters.
- ATK-12: User conversational question not misclassified as binding correction.
- ATK-13: Unverified milestone approval denied exemplar promotion.
- ATK-14: Discredited methodology (post-hoc power) blacklisted.
- ATK-17: Malformed/corrupt JSON quarantined without crashing batch consolidation.
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

from scripts.academic_correction_detector import AcademicCorrectionDetector
from scripts.academic_promotion_engine import AcademicPromotionEngine
from scripts.academic_knowledge_manager import AcademicKnowledgeManager
from scripts.academic_counterfactual_evaluator import AcademicCounterfactualEvaluator
from scripts.academic_curriculum_builder import AcademicCurriculumBuilder, CurriculumBuilderError
from scripts.academic_behavior_consolidator import AcademicBehaviorConsolidator
from scripts.academic_integrated_learning_hub import AcademicIntegratedLearningHub


class TestAcademicRedTeamRemediation(unittest.TestCase):
    """Authoritative test suite verifying red-team vulnerability remediations."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_redteam_test_")
        self.detector = AcademicCorrectionDetector(base_dir=self.temp_dir)
        self.km = AcademicKnowledgeManager(base_dir=self.temp_dir)
        self.promotion_engine = AcademicPromotionEngine(base_dir=self.temp_dir)
        self.curriculum = AcademicCurriculumBuilder(base_dir=self.temp_dir)
        self.consolidator = AcademicBehaviorConsolidator(base_dir=self.temp_dir)
        self.evaluator = AcademicCounterfactualEvaluator(base_dir=self.temp_dir)
        self.hub = AcademicIntegratedLearningHub(base_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # ATK-01: Project-specific preference quarantined
    # -------------------------------------------------------------------------
    def test_atk01_department_rule_quarantined_as_project_specific(self):
        """ATK-01: Departmental or committee rules are scoped as PROJECT_SPECIFIC and isolated."""
        user_input = "You need to follow our department guidelines: require 1.5 line spacing and bold table titles."
        detection = self.detector.detect_correction(user_input, current_agent="academic-writer")

        self.assertIsNotNone(detection)
        self.assertTrue(detection.get("is_correction"))
        self.assertEqual(detection["scope"], "PROJECT_SPECIFIC")
        self.assertTrue(detection["is_project_specific"])

        # Check knowledge manager quarantine: item with project_id cannot leak to other projects
        item = {
            "item_id": "EX-PROJ-001",
            "scope": "PROJECT_SPECIFIC",
            "metadata": {"project_id": "PROJECT_ALPHA"},
            "domain": "academic-writer"
        }
        self.assertFalse(self.km.is_in_scope(item, query_project_id="PROJECT_BETA"))
        self.assertTrue(self.km.is_in_scope(item, query_project_id="PROJECT_ALPHA"))

    # -------------------------------------------------------------------------
    # ATK-02 & ATK-14: Discredited methodology blacklisted & rejected
    # -------------------------------------------------------------------------
    def test_atk02_sobel_mediation_blacklisted_and_rejected(self):
        """ATK-02: Sobel test mediation correction is intercepted and rejected with methodological citation."""
        user_input = "Use the Sobel test to calculate the significance of the indirect mediation effect."
        detection = self.detector.detect_correction(user_input, current_agent="statistics-agent")

        self.assertIsNotNone(detection)
        self.assertTrue(detection.get("is_correction"))
        self.assertTrue(detection.get("is_discredited_methodology", False))
        self.assertIn("Sobel", detection.get("discredited_citation", ""))

        # Hub must reject and deny fast-loop dispatch
        hub_res = self.hub.process_user_turn(user_input)
        self.assertEqual(hub_res.get("action"), "DISCREDITED_METHODOLOGY_REJECTED")
        self.assertFalse(hub_res.get("fast_loop_dispatched", False))

    def test_atk14_post_hoc_power_blacklisted(self):
        """ATK-14: Post-hoc power calculation is intercepted and rejected as mathematically fallacious."""
        user_input = "Whenever a t-test is non-significant, always calculate post-hoc power."
        detection = self.detector.detect_correction(user_input, current_agent="statistics-agent")

        self.assertIsNotNone(detection)
        self.assertTrue(detection.get("is_correction"))
        self.assertTrue(detection.get("is_discredited_methodology", False))
        self.assertIn("Hoenig & Heisey", detection.get("discredited_citation", ""))

    # -------------------------------------------------------------------------
    # ATK-03: Promotion blocked when evidence count < 3
    # -------------------------------------------------------------------------
    def test_atk03_promotion_blocked_when_evidence_count_below_three(self):
        """ATK-03: Candidate cannot be promoted with fewer than 3 evaluated cases."""
        eval_report_scant = {
            "target_candidate": "CAND-001",
            "target_capability": "statistical-data-analyst",
            "evaluations": {
                "regression": {"pass_rate": 1.0, "total_cases": 1, "failed_cases": 0},
                "heldout": {"pass_rate": 1.0, "total_cases": 1, "failed_cases": 0}
            },
            "counterfactual_analysis": {
                "what_improved": ["Checks missingness before ANOVA"],
                "what_regressed": [],
                "target_capability_improved": True,
                "zero_protected_regressions": True
            },
            "minimum_improvement_policy": {"eligible": True}
        }

        gates = self.promotion_engine.verify_evaluation_gates(
            evaluation_report=eval_report_scant
        )

        self.assertFalse(gates["all_passed"])
        self.assertIn("evidence_quantity", gates["gate_results"])
        self.assertFalse(gates["gate_results"]["evidence_quantity"]["passed"])
        self.assertEqual(gates["gate_results"]["evidence_quantity"]["minimum_required"], 3)
        self.assertTrue(any("INSUFFICIENT_EVALUATION_EVIDENCE" in f for f in gates.get("failures", [])))

    # -------------------------------------------------------------------------
    # ATK-04: Overfitting detected and blocks promotion
    # -------------------------------------------------------------------------
    def test_atk04_overfitting_detected_and_blocks_promotion(self):
        """ATK-04: Overfitting guard detects high training score but low held-out score and blocks promotion."""
        is_overfitted, reason = self.evaluator.check_overfitting(
            training_pass_rate=1.0,
            heldout_pass_rate=0.40,
            heldout_total=5
        )
        self.assertTrue(is_overfitted)
        self.assertIn("[OVERFITTING_DETECTED]", reason)

        # Well-generalizing candidate is not flagged
        is_overfitted_clean, _ = self.evaluator.check_overfitting(
            training_pass_rate=0.90,
            heldout_pass_rate=0.85,
            heldout_total=5
        )
        self.assertFalse(is_overfitted_clean)

    # -------------------------------------------------------------------------
    # ATK-06: Contradictory lessons suppressed from pre-task briefing
    # -------------------------------------------------------------------------
    def test_atk06_contradictory_lessons_suppressed_from_pre_task_briefing(self):
        """ATK-06: Unresolved contradictory lessons are filtered out of pre-task briefing."""
        # Add both lessons to memory first so link_items can resolve them
        self.km.add_lesson({
            "lesson_id": "LSN-CONFLICT-A",
            "item_id": "LSN-CONFLICT-A",
            "category": "lesson",
            "capability": "statistical-data-analyst",
            "is_active": True,
            "is_active_behavior": True,
            "statement": "Always use RM-ANOVA."
        })
        self.km.add_lesson({
            "lesson_id": "LSN-CONFLICT-B",
            "item_id": "LSN-CONFLICT-B",
            "category": "lesson",
            "capability": "statistical-data-analyst",
            "is_active": True,
            "is_active_behavior": True,
            "statement": "Always use LMM."
        })

        # Record valid contradiction record adhering to schema
        ctd_id = f"CTD-TEST-{uuid.uuid4().hex[:6].upper()}"
        self.km.add_contradiction_record({
            "contract_version": "1.0.0",
            "contradiction_id": ctd_id,
            "target_skill": "statistical-data-analyst",
            "lesson_a_id": "LSN-CONFLICT-A",
            "lesson_b_id": "LSN-CONFLICT-B",
            "conflict_type": "MODEL_SPECIFICATION_CONFLICT",
            "description": "Conflict between RM-ANOVA and LMM",
            "reconciliation_strategy": "CONTEXTUAL_DISAMBIGUATION",
            "applicability_conditions": {
                "condition_for_a": "Balanced cell sizes and complete follow-up.",
                "condition_for_b": "Subject attrition and missing longitudinal waves."
            },
            "stage": "CONFLICT_DETECTED",
            "status": "UNRESOLVED"
        })

        briefing = self.km.retrieve_pre_task_context(
            task_description="Analyze repeated measures longitudinal trial",
            capability="statistical-data-analyst"
        )

        injected_ids = [item.get("item_id") for item in briefing.get("lessons", [])]
        self.assertNotIn("LSN-CONFLICT-A", injected_ids)
        self.assertNotIn("LSN-CONFLICT-B", injected_ids)

    # -------------------------------------------------------------------------
    # ATK-07: Cross-domain isolation blocks quantitative rules from qualitative queries
    # -------------------------------------------------------------------------
    def test_atk07_qualitative_task_excludes_quantitative_lessons(self):
        """ATK-07: Qualitative task strictly excludes lessons tagged quantitative."""
        item = {
            "item_id": "LSN-QUANT-001",
            "domain": "statistical-data-analyst",
            "scope": "GLOBAL",
            "tags": ["quantitative", "sphericity", "mauchly"]
        }

        # Query in qualitative domain must be rejected
        self.assertFalse(self.km.is_in_scope(item, target_capability="qualitative-data-analyst"))
        # Query in quantitative domain must be accepted
        self.assertTrue(self.km.is_in_scope(item, target_capability="statistical-data-analyst"))

    # -------------------------------------------------------------------------
    # ATK-10 & ATK-11: Curriculum complexity floor & mathematical validity
    # -------------------------------------------------------------------------
    def test_atk10_curriculum_complexity_floor_blocks_trivial_tasks(self):
        """ATK-10: Production certification requires complexity Level >= 3; trivial tasks are rejected."""
        with self.assertRaises(CurriculumBuilderError):
            self.curriculum.generate_practice_case(
                capability="statistical-data-analyst",
                target_level=1,
                enforce_complexity_floor=True
            )

        # Default generation under floor enforcement generates Level >= 3
        case = self.curriculum.generate_practice_case(
            capability="statistical-data-analyst",
            enforce_complexity_floor=True
        )
        self.assertGreaterEqual(case["curriculum_level"], 3)

    def test_atk11_curriculum_mathematical_parameter_validation(self):
        """ATK-11: Synthetic dataset parameters must pass psychometric and mathematical sanity checks."""
        # Degenerate sample size
        valid, err = self.curriculum.validate_synthetic_parameters({"n": 5, "variance": 1.0})
        self.assertFalse(valid)
        self.assertIn("minimum floor", err)

        # Negative variance
        valid, err = self.curriculum.validate_synthetic_parameters({"n": 30, "variance": -0.5})
        self.assertFalse(valid)
        self.assertIn("variance", err)

        # Excessive attrition rate (> 40%)
        valid, err = self.curriculum.validate_synthetic_parameters({"n": 30, "variance": 1.0, "attrition": 0.75})
        self.assertFalse(valid)
        self.assertIn("attrition", err)

        # Non-positive definite covariance (negative eigenvalue)
        valid, err = self.curriculum.validate_synthetic_parameters({"n": 30, "variance": 1.0, "eigenvalues": [1.5, -0.2]})
        self.assertFalse(valid)
        self.assertIn("Non-positive definite", err)

        # Valid parameters pass cleanly
        valid, err = self.curriculum.validate_synthetic_parameters({
            "n": 50,
            "variance": 1.25,
            "attrition": 0.15,
            "eigenvalues": [1.8, 0.4]
        })
        self.assertTrue(valid)
        self.assertIsNone(err)

    # -------------------------------------------------------------------------
    # ATK-12: Conversational question not misclassified as correction
    # -------------------------------------------------------------------------
    def test_atk12_conversational_question_not_misclassified_as_correction(self):
        """ATK-12: Rhetorical inquiry ending in ? is not misclassified as a binding correction."""
        inquiry = "This is great, but don't you think the reviewer might ask about the sample size?"
        detection = self.detector.detect_correction(inquiry, current_agent="academic-writer")
        self.assertIsNone(detection)

    # -------------------------------------------------------------------------
    # ATK-13: Unverified milestone approval denied exemplar promotion
    # -------------------------------------------------------------------------
    def test_atk13_unverified_milestone_approval_denied_exemplar_promotion(self):
        """ATK-13: Approving a milestone with unverified/flawed deliverable is quarantined and denied exemplar promotion."""
        flawed_deliverable = {
            "deliverable_type": "chapter-4-draft",
            "content": "تحلیل انجام شد بدون آزمون همگنی شیب‌های رگرسیون.",
            "diagnosed_defect": "unverified_assumption_violation"
        }

        res = self.hub.process_milestone_transition(
            milestone_id="MS-TEST-001",
            from_state="IN_PROGRESS",
            to_state="APPROVED",
            deliverable_payload=flawed_deliverable
        )

        self.assertFalse(res.get("exemplar_promoted", False))
        self.assertEqual(res.get("action"), "APPROVAL_QUARANTINED_UNVERIFIED")

    # -------------------------------------------------------------------------
    # ATK-17: Malformed experience JSON quarantined without crashing batch
    # -------------------------------------------------------------------------
    def test_atk17_corrupt_json_quarantined_without_crashing_batch(self):
        """ATK-17: Corrupt/truncated JSON file is isolated to quarantine without crashing consolidator batch."""
        corrupt_file = os.path.join(self.consolidator.lessons_dir, "EXP-CORRUPT-TEST.json")
        with open(corrupt_file, "w", encoding="utf-8") as f:
            f.write("{ truncated_json: true, invalid_syntax: ")

        # Loading must not raise an exception; must return None
        result = self.consolidator.safe_load_json(corrupt_file)
        self.assertIsNone(result)

        # File must be quarantined
        self.assertFalse(os.path.exists(corrupt_file))
        quarantined_files = os.listdir(self.consolidator.quarantine_dir)
        self.assertTrue(any("CORRUPT_" in fn and "EXP-CORRUPT-TEST" in fn for fn in quarantined_files))

        # Error log must record the event
        self.assertTrue(os.path.isfile(self.consolidator.error_log_path))
        with open(self.consolidator.error_log_path, "r", encoding="utf-8") as elf:
            content = elf.read()
            self.assertIn("JSONDecodeError", content)


if __name__ == "__main__":
    unittest.main()
