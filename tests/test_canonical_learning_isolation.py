#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_canonical_learning_isolation.py — Verification of Centralized Learning Isolation & Workspace Cleanliness

Validates:
1. Centralized repository resolution: Learning files strictly reside in the AcademicSuite central repository.
2. Canonical path redirection: Tool calls targeting .agents/learning or learning/ redirect to canonical repo.
3. Outside-workspace guard exemption: Central learning store writes permitted across all workspaces.
4. Client workspace purity: Client workspaces remain 100% free of local .agents/learning or learning/ directories.
"""

import os
import sys
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.canonical_paths import (
    resolve_canonical_repo_root,
    get_canonical_learning_dir,
    get_canonical_knowledge_dir,
    is_canonical_learning_path,
    redirect_learning_target_to_canonical,
    is_isolated_test_dir,
    resolve_learning_base_dir
)
from scripts.academic_knowledge_manager import AcademicKnowledgeManager
from hooks.safety_hooks import SafetyHooks, is_outside_workspace


class TestCanonicalLearningIsolation(unittest.TestCase):
    """Authoritative test suite for canonical learning isolation and workspace cleanliness."""

    def setUp(self):
        self.temp_test_dir = tempfile.mkdtemp(prefix="academic_isolation_test_")

    def tearDown(self):
        if os.path.isdir(self.temp_test_dir):
            shutil.rmtree(self.temp_test_dir, ignore_errors=True)

    def test_01_canonical_paths_resolution(self):
        """Verifies resolution of canonical repository root and learning directories."""
        repo_root = resolve_canonical_repo_root()
        learning_dir = get_canonical_learning_dir()
        knowledge_dir = get_canonical_knowledge_dir()

        self.assertTrue(os.path.isdir(repo_root))
        self.assertTrue(os.path.isdir(learning_dir))
        self.assertTrue(os.path.isdir(knowledge_dir))
        self.assertEqual(learning_dir, os.path.join(repo_root, ".agents", "learning"))
        self.assertEqual(knowledge_dir, os.path.join(repo_root, ".agents", "learning", "knowledge"))

    def test_02_is_canonical_learning_path_detection(self):
        """Verifies detection of learning paths across relative and absolute formats."""
        canonical_learning = get_canonical_learning_dir()

        # Should match
        self.assertTrue(is_canonical_learning_path(".agents/learning/knowledge/lessons/LSN-001.json"))
        self.assertTrue(is_canonical_learning_path(".agents/memory/skills/test.json"))
        self.assertTrue(is_canonical_learning_path("learning/knowledge/anti-patterns/AP-001.json"))
        self.assertTrue(is_canonical_learning_path("learning/experience/TRJ-001/trajectory.json"))
        self.assertTrue(is_canonical_learning_path(os.path.join(canonical_learning, "knowledge", "lessons", "LSN-001.json")))

        # Should NOT match
        self.assertFalse(is_canonical_learning_path("03_deliverables/Chapter_4_Results.docx"))
        self.assertFalse(is_canonical_learning_path("02_analysis_code/run_stats.py"))
        self.assertFalse(is_canonical_learning_path("data_cleaned.xlsx"))
        self.assertFalse(is_canonical_learning_path("deep_learning_model.py"))

    def test_03_redirect_learning_target_to_canonical(self):
        """Verifies authoritative redirection of relative learning paths to canonical repository."""
        canonical_learning = get_canonical_learning_dir()

        rel_lesson = ".agents/learning/knowledge/lessons/LSN-2026-TEST.json"
        redirected = redirect_learning_target_to_canonical(rel_lesson)
        expected = os.path.join(canonical_learning, "knowledge", "lessons", "LSN-2026-TEST.json")
        self.assertEqual(redirected, expected)

        plain_rel = "learning/knowledge/anti-patterns/AP-2026-TEST.json"
        redirected_plain = redirect_learning_target_to_canonical(plain_rel)
        expected_plain = os.path.join(canonical_learning, "knowledge", "anti-patterns", "AP-2026-TEST.json")
        self.assertEqual(redirected_plain, expected_plain)

        # Non-learning path should remain unchanged
        non_learning = "03_deliverables/Results.docx"
        self.assertEqual(redirect_learning_target_to_canonical(non_learning), non_learning)

    def test_04_isolated_test_directory_detection(self):
        """Verifies that temporary test fixtures are detected as isolated test directories."""
        self.assertTrue(is_isolated_test_dir(self.temp_test_dir))
        self.assertTrue(is_isolated_test_dir("/tmp/test_dir_123"))

        # Production workspaces are NOT test directories
        self.assertFalse(is_isolated_test_dir("/home/saber-ghaderi/My Work/Mohtasham Valiyanpur"))
        self.assertFalse(is_isolated_test_dir(resolve_canonical_repo_root()))

    def test_05_client_workspace_purity_with_knowledge_manager(self):
        """
        Verifies that initializing AcademicKnowledgeManager with a client workspace path
        anchors strictly to canonical repository and creates ZERO local learning directories.
        """
        client_project = "/home/saber-ghaderi/My Work/Mohtasham Valiyanpur"
        km = AcademicKnowledgeManager(base_dir=client_project)
        self.assertEqual(km.learning_dir, get_canonical_learning_dir())
        self.assertFalse(os.path.exists(os.path.join(client_project, "learning")))
        self.assertFalse(os.path.exists(os.path.join(client_project, ".agents", "learning")))

    def test_06_outside_workspace_guard_exempts_canonical_learning(self):
        """Verifies that Outside-Workspace Guard allows writing to canonical learning store from any workspace."""
        client_workspaces = ["/home/saber-ghaderi/My Work/Mohtasham Valiyanpur"]
        canonical_learning_target = os.path.join(get_canonical_learning_dir(), "knowledge", "lessons", "LSN-TEST.json")

        # Canonical learning path must NOT be considered outside workspace
        self.assertFalse(is_outside_workspace(canonical_learning_target, client_workspaces))

        # Arbitrary non-learning path outside workspace MUST be flagged
        outside_unauthorized = "/home/saber-ghaderi/Desktop/RandomFolder/file.py"
        self.assertTrue(is_outside_workspace(outside_unauthorized, client_workspaces))

    def test_07_handle_pre_tool_use_redirects_learning_target(self):
        """Verifies that handle_pre_tool_use redirects relative learning targets and allows execution."""
        valid_lesson_json = """{
            "contract_version": "1.0.0",
            "lesson_id": "LSN-2026-REDIRECT-TEST",
            "lesson_type": "WHAT_NOT_TO_DO",
            "trigger_source": "VALIDATOR_FAILURE",
            "source_experience_id": "BAN-20261001-REDIRECT-001",
            "diagnosis": {
                "what_happened": "Table formatting lacked standard column layout.",
                "behavior_caused_outcome": "The script failed to maintain strict hierarchical table structures.",
                "what_should_have_happened": "Tables must enforce standard column layout.",
                "rationale_why": "APA 7th Edition requires unambiguous separation."
            },
            "desired_behavior": "Enforce proper table formatting across all APA 7 tables.",
            "generalization": "Universal structural invariant: Table formatting must be correct.",
            "scope": "CROSS_PROJECT_UNIVERSAL",
            "generalization_stage": "LOCAL_LESSON",
            "confidence": 1.0,
            "evidence": {
                "metric_or_check": "TABLE_CHECK",
                "observed_value": "Incorrect format",
                "threshold_value": "Correct format",
                "supporting_report_ids": [
                    "BAN-20261001-REDIRECT-001"
                ],
                "supporting_artifact_paths": []
            },
            "related_skills": [
                "apa-reporting"
            ],
            "is_active_behavior": true,
            "status": "VALIDATED",
            "created_at": "2026-10-01T11:07:00Z",
            "derived_by": "knowledge-curator",
            "target_agent": "academic-writer",
            "target_agents": [
                "academic-writer"
            ]
        }"""
        payload = {
            "name": "write_to_file",
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": ".agents/learning/knowledge/lessons/LSN-2026-REDIRECT-TEST.json",
                    "CodeContent": valid_lesson_json,
                    "Overwrite": True
                }
            },
            "workspacePaths": ["/home/saber-ghaderi/My Work/Mohtasham Valiyanpur"],
            "agentName": "knowledge-curator"
        }

        res = SafetyHooks.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "allow")
        # TargetFile must be redirected to canonical repo
        self.assertIn("overwrite", res)
        redirected_target = res["overwrite"]["args"]["TargetFile"]
        expected_target = os.path.join(get_canonical_learning_dir(), "knowledge", "lessons", "LSN-2026-REDIRECT-TEST.json")
        self.assertEqual(redirected_target, expected_target)


if __name__ == "__main__":
    unittest.main()
