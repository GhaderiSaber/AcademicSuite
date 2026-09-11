#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Antigravity-Native Multi-Agent Dissertation Workflows
Validates the complete 4-workflow graduate dissertation lifecycle:
  1. chapter4.md (Statistical Data Analysis & Findings)
  2. proposal.md (Academic Research Proposal Formulation)
  3. chapter5.md (Discussion, Theoretical Integration & Conclusion)
  4. thesis_revision.md (Supervisor & Examiner Feedback Resolution)
"""

import os
import sys
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT_DIR)

from digital_saber import DigitalSaber

AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
WORKFLOWS_DIR = os.path.join(AGENTS_DIR, "workflows")


class TestWorkflowsSuite(unittest.TestCase):
    """Test suite for Antigravity multi-agent workflows."""

    @classmethod
    def setUpClass(cls):
        cls.decisions_dir = os.path.join(AGENTS_DIR, "memory", "decisions")
        cls.initial_decisions = set(os.listdir(cls.decisions_dir)) if os.path.exists(cls.decisions_dir) else set()

    @classmethod
    def tearDownClass(cls):
        # Clean up any new test decisions created during test run
        if os.path.exists(cls.decisions_dir):
            current_decisions = set(os.listdir(cls.decisions_dir))
            for f in current_decisions - cls.initial_decisions:
                try:
                    os.remove(os.path.join(cls.decisions_dir, f))
                except Exception:
                    pass

    def setUp(self):
        self.saber = DigitalSaber()
        self.expected_workflows = [
            "chapter4",
            "proposal",
            "chapter5",
            "thesis_revision"
        ]

    def test_workflow_spec_files_exist(self):
        """Validates that all 4 core workflow markdown files exist."""
        for wf in self.expected_workflows:
            wf_file = os.path.join(WORKFLOWS_DIR, f"{wf}.md")
            self.assertTrue(os.path.exists(wf_file), f"Missing workflow specification: {wf_file}")
            with open(wf_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertGreater(len(content), 500, f"Workflow spec {wf} is too short.")
            self.assertIn("digital-saber", content)
            self.assertIn("academic-writer", content)
            self.assertIn("final-judge", content)
            self.assertIn("124911145", content)  # Saber Human Gate Admin Desk ID

    def test_chapter4_workflow_execution(self):
        """Tests end-to-end execution of Chapter 4 statistical workflow."""
        res = self.saber.run_workflow("chapter4")
        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["workflow"], "chapter4")
        self.assertIn("digital-saber", res["subagents_executed"])
        self.assertIn("statistical-expert", res["subagents_executed"])
        self.assertIn("statistical-auditor", res["subagents_executed"])
        self.assertIn("academic-writer", res["subagents_executed"])
        self.assertGreaterEqual(res["readiness_score"], 80.0)
        self.assertTrue(res["decision_id"].startswith("dec_"))

    def test_proposal_workflow_execution(self):
        """Tests end-to-end execution of Research Proposal workflow."""
        res = self.saber.run_workflow("proposal")
        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["workflow"], "proposal")
        self.assertIn("methodology-expert", res["subagents_executed"])
        self.assertIn("literature-expert", res["subagents_executed"])
        self.assertIn("academic-writer", res["subagents_executed"])
        self.assertTrue(any("پروپوزال_طرح_پژوهش.docx" in a for a in res["artifacts_generated"]))
        self.assertGreaterEqual(res["readiness_score"], 80.0)
        self.assertTrue(res["decision_id"].startswith("dec_"))

    def test_chapter5_workflow_execution(self):
        """Tests end-to-end execution of Chapter 5 discussion workflow."""
        res = self.saber.run_workflow("chapter5")
        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["workflow"], "chapter5")
        self.assertIn("statistical-expert", res["subagents_executed"])
        self.assertIn("literature-expert", res["subagents_executed"])
        self.assertIn("academic-writer", res["subagents_executed"])
        self.assertIn("final-judge", res["subagents_executed"])
        self.assertTrue(any("فصل_پنجم_بحث_و_نتیجه‌گیری.docx" in a for a in res["artifacts_generated"]))
        self.assertGreaterEqual(res["readiness_score"], 80.0)
        self.assertTrue(res["decision_id"].startswith("dec_"))

    def test_thesis_revision_workflow_execution(self):
        """Tests end-to-end execution of Thesis Revision & Rebuttal Table workflow."""
        res = self.saber.run_workflow("thesis_revision")
        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["workflow"], "thesis_revision")
        self.assertIn("results-auditor", res["subagents_executed"])
        self.assertIn("statistical-auditor", res["subagents_executed"])
        self.assertIn("academic-writer", res["subagents_executed"])
        self.assertIn("final-judge", res["subagents_executed"])
        self.assertTrue(any("جدول_پاسخ_به_نظرات_استاد_راهنما_و_داوران.docx" in a for a in res["artifacts_generated"]))
        self.assertGreaterEqual(res["readiness_score"], 80.0)
        self.assertTrue(res["decision_id"].startswith("dec_"))

    def test_unknown_workflow_returns_none(self):
        """Tests that an unregistered workflow name returns None gracefully."""
        res = self.saber.run_workflow("non_existent_workflow")
        self.assertIsNone(res)


if __name__ == "__main__":
    unittest.main()
