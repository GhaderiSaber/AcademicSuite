#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_lesson_distiller.py — Comprehensive Unit Tests for Lesson Distillation

Tests:
1. Distills WHAT NOT TO DO lesson from user feedback.
2. Answers the 8 diagnostic questions (what happened, causal behavior, required behavior, why, generalization, applicability, exclusions, skills).
3. Distills WHAT NOT TO DO lesson from validator failures.
4. Distills WHAT WORKED WELL lesson from verified successful trajectories.
5. Anti-vague enforcement: detects and rejects/enriches superficial recommendations.
6. Scope preservation: PROJECT_SPECIFIC feedback never overgeneralizes to CROSS_PROJECT_UNIVERSAL.
7. Non-activation invariant: is_active_behavior is strictly False.
8. Multiple lessons per experience: experiences with multiple failure/critique signals produce multiple lessons.
9. Contract validation: all generated lessons strictly pass validate_lesson.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

from scripts.academic_lesson_distiller import (
    AcademicLessonDistiller,
    is_vague_lesson,
    VagueLessonError,
    LessonDistillationError
)
from contracts.contract_validator import validate_lesson


class TestAcademicLessonDistiller(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_lesson_distiller_")
        self.lessons_dir = os.path.join(self.temp_dir, "learning", "knowledge", "lessons")
        self.experience_dir = os.path.join(self.temp_dir, "learning", "experience")
        self.feedback_dir = os.path.join(self.experience_dir, "feedback")

        self.distiller = AcademicLessonDistiller(
            lessons_dir=self.lessons_dir,
            experience_dir=self.experience_dir,
            feedback_dir=self.feedback_dir,
            project_root=self.temp_dir
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_mock_experience(
        self,
        exp_id: str,
        outcome: str = "SUCCESS",
        skill: str = "statistical-data-analyst",
        val_events: list = None,
        feedback: dict = None
    ):
        """Creates a mock experience directory with experience.json, trajectory.json, and optional feedback.json."""
        target_dir = os.path.join(self.experience_dir, exp_id)
        os.makedirs(target_dir, exist_ok=True)

        exp_data = {
            "contract_version": "1.0.0",
            "experience_id": exp_id,
            "project_id": "study_test",
            "task_id": "06_hypothesis_1",
            "agent": "statistics-agent",
            "skill": skill,
            "start_time": "2026-09-18T10:00:00Z",
            "end_time": "2026-09-18T10:05:00Z",
            "duration_seconds": 300.0,
            "outcome": outcome,
            "artifact_references": [
                {"path": "table_4_1.docx", "sha256": "a" * 64, "type": "docx"},
                {"path": "stats.json", "sha256": "b" * 64, "type": "json"}
            ],
            "validation_status": {
                "verdict": "PASS" if outcome == "SUCCESS" else "FAIL",
                "report_id": f"REP-{exp_id}",
                "checks_passed": 5 if outcome == "SUCCESS" else 2,
                "checks_failed": 0 if outcome == "SUCCESS" else 1
            }
        }

        trj_data = {
            "contract_version": "1.0.0",
            "trajectory_id": f"TRJ-{exp_id}",
            "experience_id": exp_id,
            "project_id": "study_test",
            "task_id": "06_hypothesis_1",
            "ordered_actions": [
                {
                    "step_number": 1,
                    "action_type": "SKILL_INVOCATION",
                    "actor": "statistics-agent",
                    "timestamp": "2026-09-18T10:01:00Z",
                    "description": f"Executed skill {skill}",
                    "observable_input": {"stage": "06_hypothesis_1"},
                    "observable_output": {"status": outcome}
                }
            ],
            "tool_usages": [],
            "skill_activations": [],
            "subagent_delegations": [],
            "important_decisions": [],
            "outputs": [{"path": "table_4_1.docx", "sha256": "a" * 64}],
            "validation_events": val_events or [],
            "feedback": [feedback["feedback_id"]] if feedback else [],
            "outcome": outcome
        }

        with open(os.path.join(target_dir, "experience.json"), "w", encoding="utf-8") as f:
            json.dump(exp_data, f, indent=2)

        with open(os.path.join(target_dir, "trajectory.json"), "w", encoding="utf-8") as f:
            json.dump(trj_data, f, indent=2)

        if feedback:
            with open(os.path.join(target_dir, "feedback.json"), "w", encoding="utf-8") as f:
                json.dump(feedback, f, indent=2)

        return exp_data, trj_data

    def test_01_distill_from_user_feedback_and_8_questions(self):
        """Distills a WHAT NOT TO DO lesson answering the 8 diagnostic questions from user feedback."""
        fdb = {
            "contract_version": "1.0.0",
            "feedback_id": "FDB-LONG-MOD-001",
            "source": {"origin": "HUMAN_SUPERVISOR", "identifier": "GhaderiSaber"},
            "type": "STATISTICAL_CORRECTION",
            "target_agent": "statistics-agent",
            "target_skill": "longitudinal-moderated-mediation",
            "correction": "Proceeded with latent growth curve without comparing baseline autoregressive structures.",
            "desired_behavior": "Before selecting a longitudinal model, explicitly compare candidate models against study design, missingness, imbalance, covariance structure, and estimand.",
            "scope": "REUSABLE_PROCEDURAL",
            "severity": "HIGH",
            "timestamp": "2026-09-18T12:00:00Z",
            "context": {"project_id": "study_longitudinal", "stage_id": "06_modmed"}
        }

        exp_id = "EXP-LONG-001"
        self._create_mock_experience(exp_id, outcome="FAILURE", skill="longitudinal-moderated-mediation", feedback=fdb)

        lessons = self.distiller.distill_from_experience(exp_id)
        self.assertEqual(len(lessons), 1)
        lesson = lessons[0]

        # 1. Type and Source
        self.assertEqual(lesson["lesson_type"], "WHAT_NOT_TO_DO")
        self.assertEqual(lesson["trigger_source"], "USER_FEEDBACK")
        self.assertEqual(lesson["is_active_behavior"], False)
        self.assertEqual(lesson["source_experience_id"], exp_id)

        # 2. 8 Diagnostic Questions
        diag = lesson.get("diagnosis", {})
        self.assertIn("what_happened", diag)
        self.assertIn("behavior_caused_outcome", diag)
        self.assertIn("what_should_have_happened", diag)
        self.assertIn("rationale_why", diag)
        self.assertGreaterEqual(len(diag["rationale_why"]), 15)

        # Applicability & Exclusions
        self.assertGreaterEqual(len(lesson["applicability_conditions"]), 1)
        self.assertGreaterEqual(len(lesson["exclusions"]), 1)

        # Scope
        self.assertEqual(lesson["scope"], "DOMAIN_WIDE")

        # Related Skills
        self.assertIn("longitudinal-moderated-mediation", lesson["related_skills"])

        # Validate against schema
        val_res = validate_lesson(lesson)
        self.assertTrue(val_res["valid"], f"Lesson contract error: {val_res.get('error')}")

        # Check persisted to disk
        persisted = self.distiller.get_lesson(lesson["lesson_id"])
        self.assertEqual(persisted["lesson_id"], lesson["lesson_id"])

    def test_02_distill_from_validator_failure(self):
        """Distills a failure prevention lesson from a deterministic validator failure."""
        val_event = {
            "validator_name": "OpenXMLTypographyValidator",
            "verdict": "FAIL",
            "failed_checks": ["missing_leading_zero_persian", "unjustified_rtl_body"],
            "evidence_summary": {"detected_flaws": [".045 without leading zero"]}
        }
        exp_id = "EXP-VALFAIL-001"
        self._create_mock_experience(exp_id, outcome="FAILURE", skill="apa-reporting", val_events=[val_event])

        lessons = self.distiller.distill_from_experience(exp_id)
        self.assertEqual(len(lessons), 1)
        lesson = lessons[0]

        self.assertEqual(lesson["lesson_type"], "WHAT_NOT_TO_DO")
        self.assertEqual(lesson["trigger_source"], "VALIDATOR_FAILURE")
        self.assertIn("observed_failure", lesson)
        self.assertEqual(lesson["observed_failure"]["defect_type"], "REPORTING_OR_TYPOGRAPHY_DEFECT")
        self.assertEqual(lesson["scope"], "DOMAIN_WIDE")
        self.assertEqual(lesson.get("generalization_stage"), "LOCAL_LESSON")
        self.assertEqual(lesson["is_active_behavior"], False)

        val_res = validate_lesson(lesson)
        self.assertTrue(val_res["valid"], f"Lesson contract error: {val_res.get('error')}")

    def test_03_distill_from_successful_trajectory_what_worked_well(self):
        """Distills a positive WHAT WORKED WELL operational lesson from a successful trajectory."""
        val_event = {
            "validator_name": "TriadArtifactValidator",
            "verdict": "PASS",
            "failed_checks": [],
            "evidence_summary": {"docx": True, "md": True, "json": True}
        }
        exp_id = "EXP-SUCCESS-001"
        self._create_mock_experience(exp_id, outcome="SUCCESS", skill="mediation", val_events=[val_event])

        lessons = self.distiller.distill_from_experience(exp_id)
        self.assertEqual(len(lessons), 1)
        lesson = lessons[0]

        self.assertEqual(lesson["lesson_type"], "WHAT_WORKED_WELL")
        self.assertEqual(lesson["trigger_source"], "SUCCESSFUL_TRAJECTORY")
        self.assertEqual(lesson["is_active_behavior"], False)
        self.assertNotIn("observed_failure", lesson)

        val_res = validate_lesson(lesson)
        self.assertTrue(val_res["valid"], f"Success lesson contract error: {val_res.get('error')}")

    def test_04_anti_vague_lesson_rejection(self):
        """Rejects or detects empty and vague recommendations (e.g. 'Analyze better')."""
        vague_examples = [
            "Analyze better.",
            "Be careful.",
            "Fix bug.",
            "Improve quality.",
            "Make it right."
        ]
        for v in vague_examples:
            self.assertTrue(is_vague_lesson(v), f"Failed to identify vague lesson: '{v}'")

        concrete_example = "Before selecting a longitudinal model, explicitly compare candidate models against study design, missingness, imbalance, covariance structure, and estimand."
        self.assertFalse(is_vague_lesson(concrete_example), f"Incorrectly flagged concrete lesson: '{concrete_example}'")

    def test_05_scope_boundaries_prevent_overgeneralization(self):
        """Project-specific feedback is strictly preserved as PROJECT_SPECIFIC and never generalizes."""
        fdb_proj = {
            "contract_version": "1.0.0",
            "feedback_id": "FDB-PROJ-001",
            "source": {"origin": "HUMAN_SUPERVISOR", "identifier": "GhaderiSaber"},
            "type": "WRITING_CORRECTION",
            "target_agent": "academic-writer",
            "target_skill": "ai-academic-tone-polisher",
            "correction": "Use this exact wording for the opening paragraph in this thesis.",
            "desired_behavior": "Use this exact wording for the opening paragraph in this thesis per supervisor instructions.",
            "scope": "PROJECT_SPECIFIC",
            "severity": "MEDIUM",
            "timestamp": "2026-09-18T14:00:00Z",
            "context": {"project_id": "thesis_student_042", "stage_id": "01_intro"}
        }

        lesson = self.distiller.distill_from_feedback_payload(fdb_proj, source_exp_id="EXP-PROJ-001")
        self.assertEqual(lesson["scope"], "PROJECT_SPECIFIC")
        self.assertIn("thesis_student_042", lesson["applicability_conditions"][0])
        self.assertIn("Other research projects", lesson["exclusions"][0])

        val_res = validate_lesson(lesson)
        self.assertTrue(val_res["valid"], f"Project-specific lesson contract error: {val_res.get('error')}")

    def test_06_multiple_lessons_per_experience(self):
        """An experience containing both user feedback and a validator failure produces multiple distinct lessons."""
        val_event = {
            "validator_name": "AssumptionTestingValidator",
            "verdict": "FAIL",
            "failed_checks": ["regression_slope_heterogeneity"],
            "evidence_summary": {"p_value": 0.012}
        }
        fdb = {
            "contract_version": "1.0.0",
            "feedback_id": "FDB-MULTI-001",
            "source": {"origin": "HUMAN_SUPERVISOR", "identifier": "GhaderiSaber"},
            "type": "STATISTICAL_CORRECTION",
            "target_agent": "statistics-agent",
            "target_skill": "assumption-testing",
            "correction": "You forgot to test homogeneity of regression slopes.",
            "desired_behavior": "Always test Group x Pretest interaction for slope homogeneity before reporting standard ANCOVA.",
            "scope": "REUSABLE_PROCEDURAL",
            "severity": "HIGH",
            "timestamp": "2026-09-18T15:00:00Z"
        }

        exp_id = "EXP-MULTI-001"
        self._create_mock_experience(exp_id, outcome="FAILURE", skill="assumption-testing", val_events=[val_event], feedback=fdb)

        lessons = self.distiller.distill_from_experience(exp_id)
        self.assertEqual(len(lessons), 2)

        types = [l["trigger_source"] for l in lessons]
        self.assertIn("USER_FEEDBACK", types)
        self.assertIn("VALIDATOR_FAILURE", types)

        for l in lessons:
            val_res = validate_lesson(l)
            self.assertTrue(val_res["valid"], f"Multi-lesson error: {val_res.get('error')}")


if __name__ == "__main__":
    unittest.main()
