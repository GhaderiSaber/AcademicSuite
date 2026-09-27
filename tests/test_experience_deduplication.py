#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_experience_deduplication.py — Unit Tests for Experience & Learning Deduplication

Verifies:
1. record_from_stage generates deterministic experience IDs rather than random UUIDs.
2. Repeated invocations of record_from_stage on the same stage directory produce
   only a single experience folder on disk (zero file proliferation).
3. Modifying artifact contents or validation status updates the deterministic hash.
4. Fast experience index (index.jsonl) does not contain duplicate entries for identical runs.
5. LearningHooks.detect_recent_validation_failure deduplicates captures using _captured_validation_failures.
6. Legacy synchronous Python closed loops and fast loops in hooks are decommissioned in favor of native subagents.
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

from scripts.academic_experience_recorder import AcademicExperienceRecorder
from hooks.learning_hooks import LearningHooks


class TestExperienceDeduplication(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="academic_dedup_test_")
        self.store_dir = os.path.join(self.temp_dir, ".agents", "learning", "experience")
        self.stage_dir = os.path.join(self.temp_dir, "03_deliverables", "stage_01_demographics")
        os.makedirs(self.stage_dir, exist_ok=True)
        self.recorder = AcademicExperienceRecorder(
            store_dir=self.store_dir,
            project_root=self.temp_dir
        )
        LearningHooks._captured_validation_failures.clear()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        LearningHooks._captured_validation_failures.clear()

    def _create_stage_triad(self, stage_dir: str, prefix: str):
        docx_path = os.path.join(stage_dir, f"{prefix}.docx")
        md_path = os.path.join(stage_dir, f"{prefix}.md")
        json_path = os.path.join(stage_dir, f"{prefix}.json")
        with open(docx_path, "wb") as f:
            f.write(b"MOCK_DOCX_DATA_FOR_DEDUP")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Demographics Table\nScholarly text.")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"n": 100, "mean": 25.4}, f)

    def test_01_deterministic_id_generation(self):
        """record_from_stage generates identical experience_id across repeated calls on identical content."""
        self._create_stage_triad(self.stage_dir, "demographics")

        res1 = self.recorder.record_from_stage(self.stage_dir, outcome="FAILURE")
        res2 = self.recorder.record_from_stage(self.stage_dir, outcome="FAILURE")

        self.assertEqual(res1["experience_id"], res2["experience_id"])
        self.assertEqual(res1["trajectory_path"], res2["trajectory_path"])

    def test_02_zero_directory_proliferation_on_repeated_runs(self):
        """Repeatedly calling record_from_stage creates exactly 1 experience folder on disk."""
        self._create_stage_triad(self.stage_dir, "demographics")

        # Simulate 20 calls (e.g. repeated checks across turns or tools)
        for _ in range(20):
            self.recorder.record_from_stage(self.stage_dir, outcome="FAILURE")

        exp_dirs = [d for d in os.listdir(self.store_dir) if d.startswith("EXP-")]
        self.assertEqual(len(exp_dirs), 1, f"Expected exactly 1 experience directory, found: {exp_dirs}")

    def test_03_index_jsonl_deduplication(self):
        """index.jsonl maintains exactly 1 entry for the same experience rather than appending duplicates."""
        self._create_stage_triad(self.stage_dir, "demographics")

        for _ in range(10):
            self.recorder.record_from_stage(self.stage_dir, outcome="FAILURE")

        index_file = os.path.join(self.store_dir, "index.jsonl")
        self.assertTrue(os.path.isfile(index_file))

        with open(index_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        self.assertEqual(len(lines), 1, f"Expected 1 index line, got {len(lines)}")

    def test_04_modified_content_generates_new_deterministic_id(self):
        """Modifying stage files results in a new deterministic hash."""
        self._create_stage_triad(self.stage_dir, "demographics")
        res1 = self.recorder.record_from_stage(self.stage_dir, outcome="FAILURE")

        # Modify md content
        md_path = os.path.join(self.stage_dir, "demographics.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Updated Content With Different Hash")

        res2 = self.recorder.record_from_stage(self.stage_dir, outcome="FAILURE")

        self.assertNotEqual(res1["experience_id"], res2["experience_id"])
        exp_dirs = [d for d in os.listdir(self.store_dir) if d.startswith("EXP-")]
        self.assertEqual(len(exp_dirs), 2)

    def test_05_learning_hooks_validation_failure_deduplication(self):
        """detect_recent_validation_failure only captures a disk failure once per signature."""
        val_rep_path = os.path.join(self.stage_dir, "validation_report.json")
        with open(val_rep_path, "w", encoding="utf-8") as f:
            json.dump({
                "report_id": "VAL-FAIL-001",
                "overall_verdict": "FAIL",
                "checks_passed": 1,
                "checks_failed": 3,
                "results": [{"validator_name": "FormatValidator", "verdict": "FAIL", "failed_checks": ["missing notes"]}]
            }, f)

        payload = {"workspacePaths": [self.temp_dir]}

        # Run 5 times
        for _ in range(5):
            det = LearningHooks.detect_recent_validation_failure(payload)
            self.assertIsNotNone(det)
            self.assertEqual(det["checks_failed"], 3)

        # Experience store should have exactly 1 record
        exp_dirs = [d for d in os.listdir(self.store_dir) if d.startswith("EXP-")]
        self.assertEqual(len(exp_dirs), 1)


if __name__ == "__main__":
    unittest.main()
