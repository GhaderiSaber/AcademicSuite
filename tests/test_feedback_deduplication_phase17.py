#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_feedback_deduplication_phase17.py — Phase 17 Verification Suite

Verifies:
1. USER_FEEDBACK_DETECTED event emission with unique event_id.
2. Calling process_user_turn() twice with identical turn context -> second call returns IGNORED_DUPLICATE.
3. Running scan_transcript() twice on same transcript -> second scan produces 0 duplicate records.
4. Cross-calling scan_transcript() followed by process_user_turn() on same turn -> duplicate ignored.
5. Cross-calling process_user_turn() followed by scan_transcript() on same turn -> duplicate ignored.
6. Persistent processed_event_ids.json on disk survives instance recreation.
7. Different turn indices with identical text generate distinct event IDs and are both processed.
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

from contracts.contract_validator import validate_feedback
from scripts.academic_correction_detector import AcademicCorrectionDetector
from scripts.academic_integrated_learning_hub import AcademicIntegratedLearningHub
from scripts.academic_feedback_router import FeedbackRouter, FeedbackEventTracker


class TestFeedbackDeduplicationPhase17(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_phase17_test_")
        self.feedback_dir = os.path.join(self.temp_dir, "learning", "experience", "feedback")
        os.makedirs(self.feedback_dir, exist_ok=True)
        self.state_dir = os.path.join(self.temp_dir, "state")
        os.makedirs(self.state_dir, exist_ok=True)

        self.tracker = FeedbackEventTracker(store_dir=self.feedback_dir, project_root=self.temp_dir)
        self.detector = AcademicCorrectionDetector(store_dir=self.feedback_dir, project_root=self.temp_dir)
        self.hub = AcademicIntegratedLearningHub(base_dir=self.temp_dir)
        self.hub.mode = "simulation"

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_user_feedback_detected_has_unique_event_id(self):
        """USER_FEEDBACK_DETECTED must contain a unique event_id conforming to EVT-FDB-* pattern."""
        text = "This writing is too robotic and superficial. Revise the prose tone."
        meta = {"turn_index": 1, "conversation_id": "conv-test-001"}
        res = self.hub.process_user_turn(user_text=text, metadata=meta)

        self.assertTrue(res["is_correction"])
        self.assertEqual(res["action"], "FAST_LOOP_TRIGGERED")
        self.assertIn("event_id", res)
        self.assertTrue(res["event_id"].startswith("EVT-FDB-"))

        # Verify tracker recorded the event_id
        self.assertTrue(self.tracker.is_event_processed(res["event_id"]))

    def test_02_process_user_turn_twice_ignores_duplicate(self):
        """Calling process_user_turn twice with identical turn context must ignore second call."""
        text = "You forgot to check missingness with Little MCAR before running regression."
        meta = {"turn_index": 2, "conversation_id": "conv-test-002"}

        # First call: processed
        res1 = self.hub.process_user_turn(user_text=text, metadata=meta)
        self.assertTrue(res1["is_correction"])
        self.assertEqual(res1["action"], "FAST_LOOP_TRIGGERED")
        event_id1 = res1["event_id"]

        # Second call: must be ignored
        res2 = self.hub.process_user_turn(user_text=text, metadata=meta)
        self.assertFalse(res2["is_correction"])
        self.assertEqual(res2["action"], "IGNORED_DUPLICATE")
        self.assertEqual(res2["status"], "ALREADY_PROCESSED")
        self.assertEqual(res2["event_id"], event_id1)

    def test_03_scan_transcript_twice_produces_zero_duplicates(self):
        """Running scan_transcript twice on the same transcript produces zero duplicate records."""
        transcript_file = os.path.join(self.temp_dir, "test_transcript.jsonl")
        lines = [
            {"step_index": 1, "source": "USER_EXPLICIT", "type": "USER_INPUT", "content": "Start the analysis."},
            {"step_index": 2, "source": "MODEL", "type": "PLANNER_RESPONSE", "content": "Running analysis."},
            {"step_index": 3, "source": "USER_EXPLICIT", "type": "USER_INPUT", "content": "This method is not appropriate here. Threats to internal validity exist."},
            {"step_index": 4, "source": "MODEL", "type": "PLANNER_RESPONSE", "content": "Acknowledged."}
        ]
        with open(transcript_file, "w", encoding="utf-8") as f:
            for item in lines:
                f.write(json.dumps(item) + "\n")

        # First scan: records 1 feedback
        detected1 = self.detector.scan_transcript(transcript_file, mark_recorded=True)
        self.assertEqual(len(detected1), 1)

        # Second scan: must find 0 new items because event was already processed
        detected2 = self.detector.scan_transcript(transcript_file, mark_recorded=True)
        self.assertEqual(len(detected2), 0)

        # Feedback files on disk should be exactly 1
        all_feedback = self.detector.list_feedback()
        self.assertEqual(len(all_feedback), 1)

    def test_04_scan_transcript_then_process_user_turn_deduplicates(self):
        """When scan_transcript runs first on a turn, subsequent process_user_turn on that turn is ignored."""
        transcript_file = os.path.join(self.temp_dir, "test_transcript.jsonl")
        turn_text = "Where is the citation for this claim? The reference doesn't support this finding."
        lines = [
            {"step_index": 5, "source": "USER_EXPLICIT", "type": "USER_INPUT", "content": turn_text, "conversation_id": "conv-test-004"}
        ]
        with open(transcript_file, "w", encoding="utf-8") as f:
            for item in lines:
                f.write(json.dumps(item) + "\n")

        # 1. scan_transcript runs
        detected = self.detector.scan_transcript(transcript_file, mark_recorded=True)
        self.assertEqual(len(detected), 1)

        # 2. process_user_turn called with same context
        meta = {
            "turn_index": 5,
            "conversation_id": "conv-test-004",
            "source_transcript_path": transcript_file
        }
        res = self.hub.process_user_turn(user_text=turn_text, metadata=meta)
        self.assertEqual(res["action"], "IGNORED_DUPLICATE")
        self.assertFalse(res["is_correction"])

    def test_05_process_user_turn_then_scan_transcript_deduplicates(self):
        """When process_user_turn runs first, subsequent scan_transcript on that turn is ignored."""
        turn_text = "You forgot the leading zero in Persian and APA 7 requires a three-line table."
        meta = {"turn_index": 8, "conversation_id": "conv-test-005"}

        # 1. process_user_turn runs
        res = self.hub.process_user_turn(user_text=turn_text, metadata=meta)
        self.assertTrue(res["is_correction"])
        self.assertEqual(res["action"], "FAST_LOOP_TRIGGERED")

        # 2. scan_transcript runs on transcript containing that turn
        transcript_file = os.path.join(self.temp_dir, "test_transcript.jsonl")
        lines = [
            {"step_index": 8, "source": "USER_EXPLICIT", "type": "USER_INPUT", "content": turn_text, "conversation_id": "conv-test-005"}
        ]
        with open(transcript_file, "w", encoding="utf-8") as f:
            for item in lines:
                f.write(json.dumps(item) + "\n")

        detected = self.detector.scan_transcript(transcript_file, mark_recorded=True)
        self.assertEqual(len(detected), 0)

    def test_06_processed_event_ids_survives_instance_recreation(self):
        """processed_event_ids.json persisted on disk must survive re-instantiation."""
        event_id = "EVT-FDB-PERSIST-TEST-999"
        self.tracker.mark_event_processed(event_id, metadata={"test": True})

        # Re-create tracker from same directory
        new_tracker = FeedbackEventTracker(store_dir=self.feedback_dir, project_root=self.temp_dir)
        self.assertTrue(new_tracker.is_event_processed(event_id))
        self.assertIn(event_id, new_tracker.get_processed_event_ids())

    def test_07_different_turn_indices_generate_distinct_events(self):
        """Identical critique on different turns generates distinct event IDs and both are processed."""
        critique = "You should have verified G*Power sample size and experimental design before sampling."

        # Turn 1
        meta1 = {"turn_index": 1, "conversation_id": "conv-test-007"}
        res1 = self.hub.process_user_turn(user_text=critique, metadata=meta1)
        self.assertTrue(res1["is_correction"])
        self.assertEqual(res1["action"], "FAST_LOOP_TRIGGERED")

        # Turn 2 with same text
        meta2 = {"turn_index": 2, "conversation_id": "conv-test-007"}
        res2 = self.hub.process_user_turn(user_text=critique, metadata=meta2)
        self.assertTrue(res2["is_correction"])
        self.assertEqual(res2["action"], "FAST_LOOP_TRIGGERED")

        # Both event IDs must be different
        self.assertNotEqual(res1["event_id"], res2["event_id"])
        self.assertTrue(self.tracker.is_event_processed(res1["event_id"]))
        self.assertTrue(self.tracker.is_event_processed(res2["event_id"]))


if __name__ == "__main__":
    unittest.main()
