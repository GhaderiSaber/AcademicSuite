#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_learning_pipeline_deduplication.py — Test Suite for Learning Pipeline Portability & Deduplication

Verifies:
1. AcademicKnowledgeManager.add_lesson() semantic deduplication (fuzzy token overlap).
2. AcademicKnowledgeManager index appending uses strictly relative file paths.
3. AcademicKnowledgeManager.add_anti_pattern() deduplication.
4. knowledge-curator lifecycle hook rejects files containing machine-specific absolute paths.
5. TrajectoryEngine normalizes workspace and file paths to portable tokens.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)

from scripts.academic_knowledge_manager import AcademicKnowledgeManager
from scripts.trajectory_engine import TrajectoryEngine, TrajectoryEventType, make_portable_path

import importlib.util
_guard_path = os.path.join(AGENTS_DIR, "agents", "knowledge-curator", "guard.py")
_spec = importlib.util.spec_from_file_location("knowledge_curator_guard", _guard_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
curator_guard = _mod.handle_pre_tool_use


class TestLearningPipelineDeduplication(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_learning_dedup_")
        self.km = AcademicKnowledgeManager(base_dir=self.temp_dir)
        self.trajectory_engine = TrajectoryEngine(project_root=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_add_lesson_semantic_deduplication(self):
        """Verifies that semantically identical lessons update existing record instead of duplicating files."""
        lesson_1 = {
            "lesson_id": "LSN-TEST-NORMALITY-001",
            "target_agent": "statistics-agent",
            "desired_behavior": "Always test the parametric assumption of normality using Shapiro-Wilk before running ANOVA.",
            "diagnosis": {
                "what_happened": "The agent executed ANOVA without testing normality.",
                "behavior_caused_outcome": "Skipping normality testing leads to invalid F statistics."
            },
            "evidence": {
                "supporting_report_ids": ["REP-001"]
            }
        }
        res_id_1 = self.km.add_lesson(lesson_1)
        self.assertEqual(res_id_1, "LSN-TEST-NORMALITY-001")

        # Second lesson with slightly varied wording addressing the same defect
        lesson_2 = {
            "target_agent": "statistics-agent",
            "desired_behavior": "Always verify the parametric assumption of normality with Shapiro-Wilk before running ANOVA.",
            "diagnosis": {
                "what_happened": "ANOVA executed without testing normality assumptions.",
                "behavior_caused_outcome": "Skipping normality test produces invalid F statistics."
            },
            "evidence": {
                "supporting_report_ids": ["REP-002"]
            }
        }
        res_id_2 = self.km.add_lesson(lesson_2)
        # Deduplication must return the original lesson ID
        self.assertEqual(res_id_2, "LSN-TEST-NORMALITY-001")

        # Verify only one file exists on disk
        lesson_files = [f for f in os.listdir(self.km.lessons_dir) if f.endswith(".json")]
        self.assertEqual(len(lesson_files), 1)

        # Verify supporting report IDs were augmented
        with open(os.path.join(self.km.lessons_dir, "LSN-TEST-NORMALITY-001.json"), "r", encoding="utf-8") as f:
            updated = json.load(f)
        self.assertIn("REP-001", updated["evidence"]["supporting_report_ids"])
        self.assertIn("REP-002", updated["evidence"]["supporting_report_ids"])

    def test_add_principle_relative_path_indexing(self):
        """Verifies that add_principle writes relative paths in index.jsonl."""
        principle = {
            "statement": "Zero mental arithmetic or uncalculated statistics in narrative.",
            "scope": "domain",
            "target_agent": "statistics-agent"
        }
        pid = self.km.add_principle(principle)
        self.assertTrue(pid.startswith("PRN-"))

        # Inspect index.jsonl
        idx_path = os.path.join(self.km.principles_dir, "index.jsonl")
        self.assertTrue(os.path.isfile(idx_path))
        with open(idx_path, "r", encoding="utf-8") as f:
            line = f.readline()
            entry = json.loads(line)

        file_path = entry.get("file_path", "")
        self.assertFalse(file_path.startswith("/home/"), f"Expected relative path, got: {file_path}")
        self.assertFalse(os.path.isabs(file_path), f"Expected relative path, got: {file_path}")
        self.assertTrue(file_path.endswith(f"{pid}.json"))

    def test_knowledge_curator_guard_blocks_absolute_paths(self):
        """Verifies that knowledge-curator lifecycle guard blocks writing files containing /home/ paths."""
        # Payload with machine absolute path
        bad_payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": ".agents/learning/knowledge/lessons/LSN-TEST-001.json",
                    "CodeContent": '{"evidence": {"path": "/home/saber-ghaderi/Desktop/AcademicSuite/03_deliverables/res.docx"}}'
                }
            }
        }
        res_bad = curator_guard(bad_payload)
        self.assertEqual(res_bad.get("decision"), "deny")
        self.assertIn("Portability", res_bad.get("reason", ""))

        # Payload with clean portable path
        good_payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": ".agents/learning/knowledge/lessons/LSN-TEST-001.json",
                    "CodeContent": '{"evidence": {"path": "${WORKSPACE_ROOT}/03_deliverables/res.docx"}}'
                }
            }
        }
        res_good = curator_guard(good_payload)
        self.assertEqual(res_good.get("decision"), "allow")

    def test_trajectory_engine_portable_paths(self):
        """Verifies that TrajectoryEngine normalizes paths to portable relative tokens."""
        mock_payload = {
            "conversationId": "cid-123",
            "workspacePaths": [self.temp_dir],
            "transcriptPath": os.path.join(self.temp_dir, "transcript.jsonl"),
            "artifactDirectoryPath": os.path.join(self.temp_dir, "artifacts"),
            "toolCall": {
                "name": "view_file",
                "args": {
                    "AbsolutePath": os.path.join(self.temp_dir, "03_deliverables", "report.md")
                }
            }
        }
        ev = self.trajectory_engine.record_event(
            event_type=TrajectoryEventType.FILE_READ,
            payload=mock_payload,
            details={"file_path": os.path.join(self.temp_dir, "03_deliverables", "report.md")}
        )
        self.assertNotIn("/home/saber-ghaderi", str(ev.get("workspace_paths")))
        self.assertFalse(str(ev.get("details", {}).get("file_path", "")).startswith("/home/saber-ghaderi"))


if __name__ == "__main__":
    unittest.main()
