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
            "chapter2_literature",
            "chapter4",
            "proposal",
            "chapter5",
            "thesis_revision",
            "journal_submission",
            "defense_presentation",
            "thesis_assembly",
            "intervention_protocol",
            "scale_validation"
        ]

    def test_workflow_spec_files_exist(self):
        """Validates that all 10 core workflow markdown files exist and define cognitive roles."""
        for wf in self.expected_workflows:
            wf_file = os.path.join(WORKFLOWS_DIR, f"{wf}.md")
            self.assertTrue(os.path.exists(wf_file), f"Missing workflow specification: {wf_file}")
            with open(wf_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertGreater(len(content), 500, f"Workflow spec {wf} is too short.")
            self.assertTrue(
                "invoke_subagent" in content or "Subagent" in content or "Roles" in content or "subagent" in content,
                f"Workflow spec {wf} does not define cognitive subagent orchestration."
            )
            self.assertIn("124911145", content)  # Saber Human Gate Admin Desk ID

    def test_run_workflow_offline_rejection_enforces_directive_0_and_12(self):
        """Validates that standalone Python run_workflow raises NotImplementedError across all workflows."""
        for wf in self.expected_workflows:
            with self.assertRaises(NotImplementedError) as ctx:
                self.saber.run_workflow(wf)
            self.assertIn("cannot be executed by standalone Python", str(ctx.exception))
            self.assertIn("invoke_subagent", str(ctx.exception))

    def test_orchestrator_cli_presets_parity(self):
        """Verifies that orchestrator_cli.py provides deterministic CLI pipeline presets for research execution."""
        sys.path.insert(0, os.path.join(AGENTS_DIR, "skills", "academic-suite-orchestrator", "scripts"))
        from orchestrator_cli import PIPELINE_PRESETS, SKILL_REGISTRY
        self.assertGreater(len(PIPELINE_PRESETS), 0)
        self.assertIn("thesis_empirical", PIPELINE_PRESETS)
        self.assertIn("scale_validation", PIPELINE_PRESETS)
        self.assertIn("qualitative_study", PIPELINE_PRESETS)
        self.assertIn("meta_analysis", PIPELINE_PRESETS)
        self.assertGreater(len(SKILL_REGISTRY), 10)


if __name__ == "__main__":
    unittest.main()
