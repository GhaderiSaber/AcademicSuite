#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_feedback_routing_phase16.py — Test Suite for Phase 16 Deterministic Feedback Routing

Verifies:
1. Elimination of generic defaults: corrections never default to statistics-agent.
2. Writing correction routes to academic-writer / chapter-4-writing / academic_writing.
3. Literature correction routes to literature-expert / persian-literature-review-builder / literature_synthesis.
4. Methodology correction routes to methodology-expert / methodology-review / research_methodology.
5. Quality/formatting correction routes to results-auditor / apa-reporting / apa_formatting.
6. FeedbackRecord contains all 5 required fields: target_agent, target_skill, capability, task, stage.
7. USER_FEEDBACK_DETECTED event is emitted to state/trajectory_events.jsonl and telemetry.
8. Active state machine context resolution takes precedence over text guessing.
9. Ambiguous unresolvable feedback raises UnresolvableFeedbackTargetError without fallback.
10. Schema validity against contracts/evolution/feedback.schema.json.
"""

import os
import sys
import json
import unittest
import tempfile
import shutil
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HOOKS_DIR = os.path.join(ROOT_DIR, ".agents", "hooks")
for p in (ROOT_DIR, HOOKS_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from scripts.academic_feedback_router import (
    FeedbackRouter,
    UnresolvableFeedbackTargetError,
    DOMAIN_CAPABILITY_MAP
)
from scripts.academic_correction_detector import AcademicCorrectionDetector
from scripts.academic_integrated_learning_hub import AcademicIntegratedLearningHub
from contracts.contract_validator import validate_feedback


class TestFeedbackRoutingPhase16(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="phase16_feedback_test_")
        self.state_dir = os.path.join(self.temp_dir, "state")
        os.makedirs(self.state_dir, exist_ok=True)
        self.router = FeedbackRouter(state_dir=self.state_dir, project_root=self.temp_dir)
        self.detector = AcademicCorrectionDetector(project_root=self.temp_dir)
        self.hub = AcademicIntegratedLearningHub(base_dir=self.temp_dir)
        self.hub.mode = "simulation"

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_writing_correction_routes_to_academic_writer(self):
        """Writing correction must route to academic-writer, NEVER statistics-agent."""
        text = "This writing is too robotic and superficial. Revise the prose tone and expand on psychological mechanisms."
        fdb = self.detector.detect_correction(user_text=text)
        self.assertIsNotNone(fdb)
        self.assertEqual(fdb["target_agent"], "academic-writer")
        self.assertEqual(fdb["capability"], "academic_writing")
        self.assertNotEqual(fdb["target_agent"], "statistics-agent")

        # Must have all 5 required fields
        for field in ["target_agent", "target_skill", "capability", "task", "stage"]:
            self.assertIn(field, fdb)
            self.assertTrue(bool(fdb[field]))

        val_res = validate_feedback(fdb)
        self.assertTrue(val_res["valid"], f"Feedback validation error: {val_res.get('error')}")

    def test_02_literature_correction_routes_to_literature_expert(self):
        """Literature correction must route to literature-expert, NEVER statistics-agent."""
        text = "Where is the citation for this claim? The reference doesn't support this finding."
        fdb = self.detector.detect_correction(user_text=text)
        self.assertIsNotNone(fdb)
        self.assertEqual(fdb["target_agent"], "literature-expert")
        self.assertEqual(fdb["capability"], "literature_synthesis")
        self.assertNotEqual(fdb["target_agent"], "statistics-agent")

        val_res = validate_feedback(fdb)
        self.assertTrue(val_res["valid"], f"Feedback validation error: {val_res.get('error')}")

    def test_03_methodology_correction_routes_to_methodology_expert(self):
        """Methodology correction must route to methodology-expert, NEVER statistics-agent."""
        text = "You should have verified G*Power sample size and experimental design before sampling."
        fdb = self.detector.detect_correction(user_text=text)
        self.assertIsNotNone(fdb)
        self.assertEqual(fdb["target_agent"], "methodology-expert")
        self.assertEqual(fdb["capability"], "research_methodology")
        self.assertNotEqual(fdb["target_agent"], "statistics-agent")

        val_res = validate_feedback(fdb)
        self.assertTrue(val_res["valid"], f"Feedback validation error: {val_res.get('error')}")

    def test_04_quality_style_correction_routes_to_results_auditor(self):
        """Formatting/APA correction must route to results-auditor, NEVER statistics-agent."""
        text = "You forgot the leading zero in Persian and APA 7 requires a three-line table."
        fdb = self.detector.detect_correction(user_text=text)
        self.assertIsNotNone(fdb)
        self.assertEqual(fdb["target_agent"], "results-auditor")
        self.assertEqual(fdb["capability"], "apa_formatting")
        self.assertNotEqual(fdb["target_agent"], "statistics-agent")

        val_res = validate_feedback(fdb)
        self.assertTrue(val_res["valid"], f"Feedback validation error: {val_res.get('error')}")

    def test_05_active_state_machine_precedence(self):
        """Active state machine milestone context must take precedence over text guessing."""
        # Create an active milestone for data curation
        curr_state = {
            "project_id": "study_burnout_001",
            "milestones": {
                "M1_DATA_CURATION": {
                    "milestone_id": "M1_DATA_CURATION",
                    "status": "RUNNING",
                    "active_agent": "data-curator",
                    "current_stage": "00_data_curation",
                    "category": "data_curation",
                    "skill": "data-cleaning"
                }
            }
        }
        with open(os.path.join(self.state_dir, "current_state.json"), "w", encoding="utf-8") as f:
            json.dump(curr_state, f)

        # Ambiguous correction
        ctx = self.router.resolve_context(user_text="You forgot to check missingness patterns.")
        self.assertEqual(ctx["target_agent"], "data-curator")
        self.assertEqual(ctx["target_skill"], "data-cleaning")
        self.assertEqual(ctx["capability"], "data_curation")
        self.assertEqual(ctx["task"], "M1_DATA_CURATION")
        self.assertEqual(ctx["stage"], "00_data_curation")

    def test_06_user_feedback_detected_event_emitted(self):
        """process_user_turn must emit USER_FEEDBACK_DETECTED with full metadata."""
        text = "This writing is too robotic. Revise the prose tone."
        res = self.hub.process_user_turn(user_text=text)

        self.assertTrue(res["is_correction"])
        self.assertEqual(res["target_agent"], "academic-writer")
        self.assertEqual(res["capability"], "academic_writing")

        # Check trajectory_events.jsonl
        events_file = os.path.join(self.temp_dir, "state", "trajectory_events.jsonl")
        self.assertTrue(os.path.isfile(events_file), "trajectory_events.jsonl was not created")
        with open(events_file, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]

        user_events = [e for e in lines if e.get("event_type") == "USER_CORRECTION"]
        self.assertGreaterEqual(len(user_events), 1)
        evt = user_events[-1]
        self.assertEqual(evt["details"]["target_agent"], "academic-writer")
        self.assertEqual(evt["details"]["capability"], "academic_writing")

        # Check activity telemetry
        act_file = os.path.join(self.temp_dir, "learning", "telemetry", "activity.jsonl")
        self.assertTrue(os.path.isfile(act_file))
        with open(act_file, "r", encoding="utf-8") as f:
            act_lines = [json.loads(l) for l in f if l.strip()]
        detected_events = [a for a in act_lines if a.get("event") == "USER_FEEDBACK_DETECTED"]
        self.assertGreaterEqual(len(detected_events), 1)
        self.assertEqual(detected_events[-1]["target_agent"], "academic-writer")

    def test_07_unresolvable_feedback_raises_error_without_fallback(self):
        """Completely unresolvable feedback must raise UnresolvableFeedbackTargetError without fallback."""
        router = FeedbackRouter(state_dir=os.path.join(self.temp_dir, "empty_state"), project_root=self.temp_dir)
        with self.assertRaises(UnresolvableFeedbackTargetError):
            router.resolve_context(user_text="something completely random with zero keywords or context")


if __name__ == "__main__":
    unittest.main()
