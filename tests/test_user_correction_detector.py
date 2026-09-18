#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_user_correction_detector.py — Comprehensive Unit Tests for User Correction Detector

Tests:
1. Canonical user correction examples classification & scoping:
   - "You forgot to check missingness." -> DATA_ANALYSIS_CORRECTION, REUSABLE_PROCEDURAL
   - "This method is not appropriate here." -> METHODOLOGY_CORRECTION, REUSABLE_PROCEDURAL
   - "You need to compare these two models." -> STATISTICAL_CORRECTION, REUSABLE_PROCEDURAL
   - "This writing is too superficial." -> WRITING_CORRECTION, REUSABLE_PROCEDURAL
   - "Don't say the treatment caused this unless the design supports it." -> POTENTIAL_GLOBAL_INVARIANT
   - "You need to verify the effect size." -> STATISTICAL_CORRECTION, REUSABLE_PROCEDURAL
   - "This table doesn't match the output." -> RESEARCH_INTEGRITY_CORRECTION, POTENTIAL_GLOBAL_INVARIANT
   - "Use this exact wording in this thesis." -> PROJECT_SPECIFIC
   - "Never report a statistic that cannot be traced to a reproducible execution artifact." -> POTENTIAL_GLOBAL_INVARIANT
2. Non-intrusive execution: no "/learn" or manual command required.
3. Does not directly mutate production skills.
4. Repetition detection: multiple similar corrections increment repetition_count.
5. False-positive tracking: flagging false positives updates status and rationale without record loss.
6. Transcript scanning: parses transcript.jsonl lines and extracts meaningful user corrections.
7. Full contract validation: generated feedback matches contracts/evolution/feedback.schema.json.
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

from scripts.academic_correction_detector import AcademicCorrectionDetector
from contracts.contract_validator import validate_feedback


class TestUserCorrectionDetector(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_correction_detector_")
        self.store_dir = os.path.join(self.temp_dir, "learning", "experience", "feedback")
        self.detector = AcademicCorrectionDetector(
            store_dir=self.store_dir,
            project_root=self.temp_dir
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_canonical_correction_examples(self):
        """All 7 canonical prompt examples and boundary scopes are correctly classified and scoped."""
        test_cases = [
            (
                "You forgot to check missingness.",
                "DATA_ANALYSIS_CORRECTION",
                "REUSABLE_PROCEDURAL"
            ),
            (
                "This method is not appropriate here.",
                "METHODOLOGY_CORRECTION",
                "REUSABLE_PROCEDURAL"
            ),
            (
                "You need to compare these two models.",
                "STATISTICAL_CORRECTION",
                "REUSABLE_PROCEDURAL"
            ),
            (
                "This writing is too superficial.",
                "WRITING_CORRECTION",
                "REUSABLE_PROCEDURAL"
            ),
            (
                "Don't say the treatment caused this unless the design supports it.",
                "METHODOLOGY_CORRECTION",
                "POTENTIAL_GLOBAL_INVARIANT"
            ),
            (
                "You need to verify the effect size.",
                "STATISTICAL_CORRECTION",
                "REUSABLE_PROCEDURAL"
            ),
            (
                "This table doesn't match the output.",
                "RESEARCH_INTEGRITY_CORRECTION",
                "REUSABLE_PROCEDURAL"
            ),
            (
                "Use this exact wording in this thesis.",
                "WRITING_CORRECTION",
                "PROJECT_SPECIFIC"
            ),
            (
                "Never report a statistic that cannot be traced to a reproducible execution artifact.",
                "RESEARCH_INTEGRITY_CORRECTION",
                "POTENTIAL_GLOBAL_INVARIANT"
            ),
        ]

        for text, expected_type, expected_scope in test_cases:
            res = self.detector.detect_correction(text)
            self.assertIsNotNone(res, f"Failed to detect correction in: '{text}'")
            self.assertEqual(res["type"], expected_type, f"Type mismatch for: '{text}'")
            self.assertEqual(res["scope"], expected_scope, f"Scope mismatch for: '{text}'")

            # Validate against schema
            val = validate_feedback(res)
            self.assertTrue(val["valid"], f"Contract validation failed for '{text}': {val.get('error')}")

            # Verify generalization candidate exists
            cand = res.get("generalization_candidate")
            self.assertIsNotNone(cand)
            self.assertEqual(cand["scope"], expected_scope)
            self.assertEqual(cand["evaluation_status"], "PENDING")

    def test_02_non_correction_text_ignored(self):
        """Standard chit-chat, procedural acknowledgments, and inquiries are not flagged as corrections."""
        benign_inputs = [
            "Hello, let's start the analysis.",
            "Can you explain the difference between CFA and EFA?",
            "Looks good to me, please proceed.",
            "What is the next stage in our Chapter 4 pipeline?",
            "Yes",
            "Please generate the Word document."
        ]
        for benign in benign_inputs:
            res = self.detector.detect_correction(benign)
            self.assertIsNone(res, f"False positive incorrectly detected on: '{benign}'")

    def test_03_no_direct_mutation_of_skills(self):
        """Detector records to learning/experience/feedback and never modifies .agents/skills/."""
        skills_dir = os.path.join(ROOT_DIR, ".agents", "skills")
        # Record mtimes of skills directory
        pre_mtimes = {f: os.path.getmtime(os.path.join(skills_dir, f)) for f in os.listdir(skills_dir)}

        prompt = "You need to verify the effect size."
        feedback = self.detector.detect_correction(prompt)
        self.assertIsNotNone(feedback)
        rec = self.detector.record_feedback(feedback)
        self.assertEqual(rec["status"], "RECORDED")

        # Verify skill mtimes are completely untouched
        for f in os.listdir(skills_dir):
            self.assertEqual(os.path.getmtime(os.path.join(skills_dir, f)), pre_mtimes[f])

        # Verify feedback written into learning/experience/feedback
        disk_file = os.path.join(self.store_dir, f"{rec['feedback_id']}.json")
        self.assertTrue(os.path.isfile(disk_file))

    def test_04_repetition_tracking(self):
        """Repeated corrections increment the repetition_count and are queryable."""
        text = "You forgot to check missingness."

        # First instance
        fb1 = self.detector.detect_correction(text)
        self.detector.record_feedback(fb1)
        self.assertEqual(fb1["generalization_candidate"]["repetition_count"], 1)

        # Second instance
        fb2 = self.detector.detect_correction(text)
        self.detector.record_feedback(fb2)
        self.assertEqual(fb2["generalization_candidate"]["repetition_count"], 2)

        # Third instance
        fb3 = self.detector.detect_correction(text)
        self.detector.record_feedback(fb3)
        self.assertEqual(fb3["generalization_candidate"]["repetition_count"], 3)

        repeated = self.detector.list_repeated_corrections(min_count=2)
        self.assertEqual(len(repeated), 1)
        self.assertEqual(repeated[0]["repetition_count"], 3)
        self.assertEqual(repeated[0]["category"], "DATA_ANALYSIS_CORRECTION")

    def test_05_false_positive_flagging(self):
        """False positive corrections can be flagged with rationale without deleting historical records."""
        fb = self.detector.detect_correction("This writing is too superficial.")
        rec = self.detector.record_feedback(fb)
        fid = rec["feedback_id"]

        flag_res = self.detector.flag_false_positive(fid, rationale="Subjective user preference; methodology was sound.")
        self.assertEqual(flag_res["status"], "FLAGGED")
        self.assertEqual(flag_res["evaluation_status"], "FLAGGED_FALSE_POSITIVE")

        # Verify persisted on disk
        with open(os.path.join(self.store_dir, f"{fid}.json"), "r", encoding="utf-8") as f:
            persisted = json.load(f)
        self.assertEqual(persisted["generalization_candidate"]["evaluation_status"], "FLAGGED_FALSE_POSITIVE")
        self.assertEqual(persisted["generalization_candidate"]["flag_rationale"], "Subjective user preference; methodology was sound.")

        # Verify index reflects the change
        indexed = self.detector.list_feedback(status="FLAGGED_FALSE_POSITIVE")
        self.assertEqual(len(indexed), 1)
        self.assertEqual(indexed[0]["feedback_id"], fid)

    def test_06_scan_transcript_extraction(self):
        """Scans transcript lines, detecting corrections while ignoring non-correction turns."""
        transcript_file = os.path.join(self.temp_dir, "test_transcript.jsonl")
        lines = [
            {"step_index": 1, "source": "USER_EXPLICIT", "type": "USER_INPUT", "content": "Please start the CFA analysis."},
            {"step_index": 2, "source": "MODEL", "type": "PLANNER_RESPONSE", "content": "Running CFA model..."},
            {"step_index": 3, "source": "USER_EXPLICIT", "type": "USER_INPUT", "content": "This method is not appropriate here."},
            {"step_index": 4, "source": "MODEL", "type": "PLANNER_RESPONSE", "content": "Understood. Switching method."},
            {"step_index": 5, "source": "USER_EXPLICIT", "type": "USER_INPUT", "content": "Looks good now."}
        ]
        with open(transcript_file, "w", encoding="utf-8") as f:
            for item in lines:
                f.write(json.dumps(item) + "\n")

        detected = self.detector.scan_transcript(transcript_file, mark_recorded=True)
        self.assertEqual(len(detected), 1)
        self.assertEqual(detected[0]["type"], "METHODOLOGY_CORRECTION")
        self.assertIn("This method is not appropriate here", detected[0]["correction"])

        # Check recorded on disk
        all_feedback = self.detector.list_feedback()
        self.assertEqual(len(all_feedback), 1)


if __name__ == "__main__":
    unittest.main()
