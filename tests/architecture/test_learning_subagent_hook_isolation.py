#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_learning_subagent_hook_isolation.py — Hook Isolation Test Suite

Verifies that Continuous Learning Subagents (evaluation-agent, behavior-analyst,
knowledge-curator, skill-evolver, trajectory-analyzer, curriculum-builder) and
Auditor Subagents (validation-agent, results-auditor, etc.) are strictly exempt
from thesis deliverable stop gates, missing chapter monograph checks, and validation FAIL gates,
while delivery workers (academic-writer, academic-orchestrator) remain strictly enforced.
"""

import os
import sys
import json
import zipfile
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

hooks_dir = os.path.join(ROOT_DIR, ".agents", "hooks")
if hooks_dir not in sys.path:
    sys.path.insert(0, hooks_dir)

from dynamic_invariant_guard import DynamicInvariantGuard
from integrity_hooks import IntegrityHooks
from contracts.hook_identity_contract import is_learning_subagent, is_auditor_agent, LEARNING_SUBAGENTS, AUDITOR_SUBAGENTS


class TestLearningSubagentHookIsolation(unittest.TestCase):
    """Verifies isolation of learning subagents and auditors from academic deliverable stop gates."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_learning_hook_iso_")
        self.deliverables_dir = os.path.join(self.temp_dir, "03_deliverables")
        os.makedirs(self.deliverables_dir, exist_ok=True)

        # Create a mock docx containing prohibited dual-sample terminology
        # that triggers CAND-2026-APA-SINGLE-SAMPLE-INVARIANT
        self.docx_path = os.path.join(self.deliverables_dir, "Chapter_4_Results.docx")
        with zipfile.ZipFile(self.docx_path, "w") as zf:
            mock_xml = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                '<w:body>'
                '<w:p><w:r><w:t>جدول ۴- ۱. نتایج نمونه اولیه و نمونه مهارشده.</w:t></w:r></w:p>'
                '</w:body>'
                '</w:document>'
            )
            zf.writestr("word/document.xml", mock_xml)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_identity_helpers(self):
        """Verifies canonical recognition of learning and auditor subagents."""
        for agent in LEARNING_SUBAGENTS:
            self.assertTrue(is_learning_subagent(agent), f"{agent} must be recognized as learning subagent")
            self.assertFalse(is_auditor_agent(agent), f"{agent} is not an auditor agent")

        for auditor in AUDITOR_SUBAGENTS:
            self.assertTrue(is_auditor_agent(auditor), f"{auditor} must be recognized as auditor agent")
            self.assertFalse(is_learning_subagent(auditor), f"{auditor} is not a learning subagent")

        self.assertFalse(is_learning_subagent("academic-writer"))
        self.assertFalse(is_auditor_agent("academic-writer"))
        self.assertFalse(is_learning_subagent("academic-orchestrator"))
        self.assertFalse(is_auditor_agent("academic-orchestrator"))

    def test_dynamic_invariant_stop_exempts_learning_agents(self):
        """DynamicInvariantGuard.evaluate_stop must allow learning subagents even with docx defects."""
        payload = {
            "agentName": "evaluation-agent",
            "workspacePaths": [self.temp_dir],
            "deliverables_dir": self.deliverables_dir,
        }
        res = DynamicInvariantGuard.evaluate_stop("evaluation-agent", payload)
        self.assertEqual(res.get("decision"), "allow", "evaluation-agent must not be blocked by deliverable defects")

        for agent in LEARNING_SUBAGENTS:
            payload["agentName"] = agent
            res = DynamicInvariantGuard.evaluate_stop(agent, payload)
            self.assertEqual(res.get("decision"), "allow", f"{agent} must not be blocked by deliverable defects")

    def test_dynamic_invariant_stop_exempts_auditors(self):
        """DynamicInvariantGuard.evaluate_stop must allow auditor subagents to report findings."""
        payload = {
            "agentName": "validation-agent",
            "workspacePaths": [self.temp_dir],
            "deliverables_dir": self.deliverables_dir,
        }
        res = DynamicInvariantGuard.evaluate_stop("validation-agent", payload)
        self.assertEqual(res.get("decision"), "allow", "validation-agent must not be blocked by deliverable defects")

    def test_dynamic_invariant_stop_blocks_academic_writer(self):
        """DynamicInvariantGuard.evaluate_stop MUST enforce deliverable defects on academic-writer."""
        payload = {
            "agentName": "academic-writer",
            "workspacePaths": [self.temp_dir],
            "deliverables_dir": self.deliverables_dir,
        }
        res = DynamicInvariantGuard.evaluate_stop("academic-writer", payload)
        self.assertEqual(res.get("decision"), "continue", "academic-writer MUST be blocked when deliverable has defects")
        self.assertIn("CAND-2026-APA-SINGLE-SAMPLE-INVARIANT", res.get("reason", ""))

    def test_integrity_missing_artifacts_exempts_learning_and_auditors(self):
        """Missing artifacts (Triad / monograph) must not block learning agents or auditors."""
        # Chapter_4_Results.docx exists without Chapter_4_Results.md in deliverables_dir
        # For academic-writer, verify_missing_artifacts must fail closed:
        ok_writer, reason_writer = IntegrityHooks.verify_missing_artifacts([self.temp_dir], caller="academic-writer")
        self.assertFalse(ok_writer, "academic-writer must fail missing artifact verification")
        self.assertIn("Chapter Monograph Invariant", reason_writer)

        # For evaluation-agent and other learning agents, verify_missing_artifacts must succeed:
        ok_ea, reason_ea = IntegrityHooks.verify_missing_artifacts([self.temp_dir], caller="evaluation-agent")
        self.assertTrue(ok_ea, "evaluation-agent must be exempt from chapter monograph missing artifact check")
        self.assertEqual(reason_ea, "")

        # For validation-agent, verify_missing_artifacts must succeed:
        ok_val, reason_val = IntegrityHooks.verify_missing_artifacts([self.temp_dir], caller="validation-agent")
        self.assertTrue(ok_val, "validation-agent must be exempt from chapter monograph missing artifact check")

    def test_integrity_post_analysis_exempts_learning_agents(self):
        """A failing validation report must not block learning agents from terminating."""
        val_rep_path = os.path.join(self.deliverables_dir, "validation_report.json")
        with open(val_rep_path, "w", encoding="utf-8") as f:
            json.dump({
                "overall_verdict": "FAIL",
                "evidence_summary": {"checks_failed": 3}
            }, f)

        # For academic-writer, post-analysis must fail:
        ok_writer, reason_writer = IntegrityHooks.verify_post_analysis([self.temp_dir], caller="academic-writer")
        self.assertFalse(ok_writer, "academic-writer must fail when validation_report is FAIL")

        # For evaluation-agent, post-analysis must pass:
        ok_ea, reason_ea = IntegrityHooks.verify_post_analysis([self.temp_dir], caller="evaluation-agent")
        self.assertTrue(ok_ea, "evaluation-agent must be exempt from post-analysis validation gate")

    def test_handle_stop_full_flow_for_evaluation_agent(self):
        """IntegrityHooks.handle_stop must allow evaluation-agent to terminate cleanly."""
        val_rep_path = os.path.join(self.deliverables_dir, "validation_report.json")
        with open(val_rep_path, "w", encoding="utf-8") as f:
            json.dump({
                "overall_verdict": "FAIL",
                "evidence_summary": {"checks_failed": 3}
            }, f)

        payload = {
            "agentName": "evaluation-agent",
            "workspacePaths": [self.temp_dir],
        }
        res = IntegrityHooks.handle_stop(payload)
        self.assertEqual(res.get("decision"), "allow", f"handle_stop must allow evaluation-agent: {res}")


if __name__ == "__main__":
    unittest.main()
