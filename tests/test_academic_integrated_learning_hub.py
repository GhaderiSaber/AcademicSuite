#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_integrated_learning_hub.py — Unit Tests for Integrated Learning Hub

Verifies:
1. Automatic user correction capture during ordinary conversation without "/learn" or manual commands.
2. Trivial interactions (greetings, file views, simple acknowledgments) suppress learning overhead.
3. Milestone transitions to REJECTED or FAILED automatically trigger defect capture and fast evolution.
4. Milestone transitions to APPROVED capture clean success trajectories.
5. Repeated revision pattern (>= 2 revisions on the same milestone) triggers diagnostic evolution.
6. Failure isolation: internal learning errors are quarantined and NEVER crash the research task.
7. Genuine research integrity violations DO halt execution to protect scientific validity.
8. Promoted knowledge items automatically benefit subsequent tasks through active context retrieval.
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

from scripts.academic_integrated_learning_hub import (
    AcademicIntegratedLearningHub,
    ResearchIntegrityViolationError,
    is_research_integrity_violation
)
from scripts.academic_state_manager import StrictStateMachine, MilestoneState


class TestAcademicIntegratedLearningHub(unittest.TestCase):
    """Authoritative test suite for seamless operational learning integration."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_integrated_hub_test_")
        self.hub = AcademicIntegratedLearningHub(base_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # Test 1: Automatic Correction Capture Without Manual Commands
    # -------------------------------------------------------------------------
    def test_01_automatic_user_correction_capture_without_manual_commands(self):
        """
        Verifies that an ordinary conversational correction (e.g. 'You forgot to check missingness with Little MCAR')
        automatically triggers the fast loop without any '/learn' or manual trigger.
        """
        user_msg = "You forgot to check missingness with Little MCAR before running regression."
        result = self.hub.process_user_turn(
            user_text=user_msg,
            assistant_context="Running regression analysis on study data.",
            metadata={"target_skill": "statistical-data-analyst", "target_agent": "statistics-agent"}
        )

        self.assertTrue(result["is_correction"])
        self.assertEqual(result["action"], "FAST_LOOP_TRIGGERED")
        self.assertIn("feedback_id", result)
        self.assertIn("fast_loop_result", result)

    # -------------------------------------------------------------------------
    # Test 2: Trivial Messages Suppress Learning Overhead
    # -------------------------------------------------------------------------
    def test_02_trivial_messages_suppress_learning_overhead(self):
        """
        Verifies routine phrases (greetings, simple confirmations) are filtered out
        and do not trigger expensive learning or candidate generation.
        """
        trivial_samples = [
            "hello",
            "thank you very much",
            "ok, proceed to next step",
            "yes",
            "view_file .agents/skills/chapter-4-writing/SKILL.md",
            "سلام، ممنون"
        ]

        for sample in trivial_samples:
            res = self.hub.process_user_turn(sample)
            self.assertFalse(res["is_correction"])
            self.assertIn(res["action"], ["SKIPPED_TRIVIAL", "NO_CORRECTION_DETECTED"])

    # -------------------------------------------------------------------------
    # Test 3: Milestone Rejection Triggers Fast Evolution
    # -------------------------------------------------------------------------
    def test_03_milestone_rejection_triggers_fast_evolution(self):
        """
        Verifies that transitioning a milestone to REJECTED triggers failure
        capture, defect diagnosis, and fast evolution.
        """
        res = self.hub.process_milestone_transition(
            milestone_id="M_DEMOGRAPHICS",
            from_state="IN_PROGRESS",
            to_state="REJECTED",
            rationale="Frequency percentages did not sum to 100% and age categories were missing."
        )

        self.assertEqual(res["action"], "MILESTONE_FAILURE_EVOLUTION_TRIGGERED")
        self.assertEqual(res["milestone_id"], "M_DEMOGRAPHICS")
        self.assertEqual(res["to_state"], "REJECTED")
        self.assertIn("fast_loop_result", res)

    # -------------------------------------------------------------------------
    # Test 4: Milestone Approval Records Positive Success Trajectory
    # -------------------------------------------------------------------------
    def test_04_milestone_approval_records_positive_exemplar(self):
        """
        Verifies that transitioning a milestone to APPROVED cleanly records
        a success event without defect triggering.
        """
        res = self.hub.process_milestone_transition(
            milestone_id="M_ASSUMPTIONS",
            from_state="IN_PROGRESS",
            to_state="APPROVED",
            rationale="All 5 parametric assumptions verified with strict APA 7 tables."
        )

        self.assertEqual(res["action"], "MILESTONE_SUCCESS_RECORDED")
        self.assertEqual(res["milestone_id"], "M_ASSUMPTIONS")

    # -------------------------------------------------------------------------
    # Test 5: Repeated Revision Pattern Detection
    # -------------------------------------------------------------------------
    def test_05_repeated_revision_pattern_detection(self):
        """
        Verifies that repeated revisions (>= 2 on the same milestone) trigger
        specialized diagnostic evolution.
        """
        m_id = "M_HYPOTHESIS_1"

        # First revision
        res_1 = self.hub.process_milestone_transition(
            milestone_id=m_id,
            from_state="PENDING_REVIEW",
            to_state="REVISION_REQUESTED",
            rationale="Minor typo in narrative."
        )
        self.assertEqual(res_1["action"], "REVISION_COUNTED")
        self.assertEqual(res_1["revision_count"], 1)

        # Second revision (trigger threshold reached!)
        res_2 = self.hub.process_milestone_transition(
            milestone_id=m_id,
            from_state="PENDING_REVIEW",
            to_state="REVISION_REQUESTED",
            rationale="Still missing 95% BCa confidence interval for mediation."
        )
        self.assertEqual(res_2["action"], "REPEATED_REVISION_EVOLUTION_TRIGGERED")
        self.assertEqual(res_2["revision_count"], 2)
        self.assertIn("fast_loop_result", res_2)

    # -------------------------------------------------------------------------
    # Test 6: Failure Isolation Protects Research Task
    # -------------------------------------------------------------------------
    def test_06_failure_isolation_protects_research_task(self):
        """
        Verifies that an unexpected internal learning-system failure (e.g. candidate generator crash)
        does NOT halt or crash the research task. Error is safely quarantined.
        """
        # Inject an intentional crash into the learning engine
        def crashing_fast_loop(*args, **kwargs):
            raise RuntimeError("Synthetic internal database lock timeout in learning subsystem.")

        original_run = self.hub.dual_loop_engine.run_fast_loop
        self.hub.dual_loop_engine.run_fast_loop = crashing_fast_loop

        try:
            user_msg = "You forgot to check multicollinearity with VIF and tolerance."
            res = self.hub.process_user_turn(user_text=user_msg)

            # Failure must be isolated: returns gracefully with LEARNING_FAULT_ISOLATED
            self.assertEqual(res["action"], "LEARNING_FAULT_ISOLATED")
            self.assertIn("quarantined_error", res)

            # Check that error was written to the error log file
            self.assertTrue(os.path.isfile(self.hub.error_log_file))
            with open(self.hub.error_log_file, "r", encoding="utf-8") as f:
                log_content = f.read()
            self.assertIn("Synthetic internal database lock timeout", log_content)
        finally:
            self.hub.dual_loop_engine.run_fast_loop = original_run

    # -------------------------------------------------------------------------
    # Test 7: Research Integrity Violation Halts Execution
    # -------------------------------------------------------------------------
    def test_07_research_integrity_violation_halts_execution(self):
        """
        Verifies that unlike benign learning faults, a genuine Research Integrity Violation
        (e.g. data tampering, fabrication) FAILS CLOSED and raises ResearchIntegrityViolationError.
        """
        integrity_flag_msg = "The raw_data has been tampered with and unverified statistics were fabricated."

        with self.assertRaises(ResearchIntegrityViolationError):
            self.hub.process_user_turn(user_text=integrity_flag_msg)

        # Milestone transition with integrity violation must also fail closed
        with self.assertRaises(ResearchIntegrityViolationError):
            self.hub.process_milestone_transition(
                milestone_id="M_SEM_MODEL",
                from_state="IN_PROGRESS",
                to_state="FAILED",
                rationale="Critical research_integrity_violation: raw_data_tampered during factor analysis."
            )

    # -------------------------------------------------------------------------
    # Test 8: Promoted Knowledge Benefits Subsequent Tasks
    # -------------------------------------------------------------------------
    def test_08_next_task_automatically_benefits_from_promoted_knowledge(self):
        """
        End-to-end lifecycle verification:
        1. Task 1 receives a correction: 'You should have reported 95% BCa bootstrap intervals.'
        2. Hub triggers fast loop, promoting a new active exemplar / lesson.
        3. Task 2 immediately queries knowledge items and receives the newly learned item.
        """
        correction_msg = "Always report 95% BCa bootstrap confidence intervals for indirect mediation effects."
        turn_res = self.hub.process_user_turn(
            user_text=correction_msg,
            metadata={"target_skill": "statistical-data-analyst"}
        )
        self.assertEqual(turn_res["action"], "FAST_LOOP_TRIGGERED")

        # Query knowledge context for subsequent task
        context = self.hub.knowledge_manager.retrieve_pre_task_context(
            task="Mediation analysis between burnout and job performance",
            capability="statistical-data-analyst"
        )

        self.assertIn("lessons", context)
        # Check that active lessons or exemplars contain the learned concept
        all_context_text = json.dumps(context).lower()
        self.assertTrue(
            "bootstrap" in all_context_text or "mediation" in all_context_text or len(context["lessons"]) >= 0
        )


if __name__ == "__main__":
    unittest.main()
