#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_learning_trigger_wiring.py — Verification of Continuous Learning Trigger Wiring

Verifies:
1. academic-orchestrator frontmatter explicitly declares all 6 continuous learning subagents.
2. academic-orchestrator markdown body contains the Continuous Learning Trigger Protocol.
3. LearningHooks.capture_user_correction detects critique patterns and returns structured metadata.
4. LearningHooks.handle_pre_invocation injects actionable learning directives upon critique detection.
5. Invariants: academic-orchestrator retains strict Non-Execution Invariant (zero run_command, zero write_to_file).
"""

import os
import sys
import unittest
import yaml

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HOOKS_DIR = os.path.join(ROOT_DIR, ".agents", "hooks")
for p in (ROOT_DIR, HOOKS_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from learning_hooks import LearningHooks


class TestLearningTriggerWiring(unittest.TestCase):

    def setUp(self):
        self.orchestrator_path = os.path.join(
            ROOT_DIR, ".agents", "agents", "academic-orchestrator.md"
        )
        self.orchestrator_mirror_path = os.path.join(
            ROOT_DIR, ".agents", "agents", "academic-orchestrator", "agent.md"
        )
        self.learning_subagents = [
            "trajectory-analyzer",
            "behavior-analyst",
            "knowledge-curator",
            "skill-evolver",
            "evaluation-agent",
            "curriculum-builder",
        ]

    def _parse_frontmatter(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        parts = content.split("---")
        self.assertGreaterEqual(len(parts), 3, f"File {file_path} missing frontmatter")
        data = yaml.safe_load(parts[1])
        body = "---".join(parts[2:])
        return data, body

    def test_01_orchestrator_frontmatter_declares_all_learning_subagents(self):
        """Frontmatter of academic-orchestrator must declare all 6 learning subagents in agents:"""
        for path in (self.orchestrator_path, self.orchestrator_mirror_path):
            data, _ = self._parse_frontmatter(path)
            declared_agents = data.get("agents", [])
            for sa in self.learning_subagents:
                self.assertIn(
                    sa,
                    declared_agents,
                    f"academic-orchestrator frontmatter in {path} must declare subagent '{sa}' in 'agents:'",
                )

    def test_02_orchestrator_prompt_contains_learning_trigger_protocol(self):
        """Instructions in academic-orchestrator must codify the Continuous Learning Trigger Protocol."""
        for path in (self.orchestrator_path, self.orchestrator_mirror_path):
            _, body = self._parse_frontmatter(path)
            self.assertIn(
                "Continuous Learning Trigger Protocol",
                body,
                f"{path} missing Continuous Learning Trigger Protocol section",
            )
            self.assertIn(
                "USER_FEEDBACK_DETECTED",
                body,
                f"{path} missing USER_FEEDBACK_DETECTED trigger instructions",
            )
            self.assertIn(
                "trajectory-analyzer",
                body,
                f"{path} missing trajectory-analyzer delegation instruction",
            )
            self.assertIn(
                "behavior-analyst",
                body,
                f"{path} missing behavior-analyst delegation instruction",
            )
            self.assertIn(
                "knowledge-curator",
                body,
                f"{path} missing knowledge-curator delegation instruction",
            )

    def test_03_capture_user_correction_detects_critique_patterns(self):
        """capture_user_correction must detect critique keywords and return metadata."""
        critique_payload = {
            "userMessage": "So we have a problem. The table formatting is wrong and didn't trigger learning.",
            "caller": "academic-orchestrator",
            "conversationId": "test-conv-001",
        }
        res = LearningHooks.capture_user_correction(critique_payload)
        self.assertTrue(res.get("is_critique"), "Expected critique detection for problem/wrong text")
        self.assertIsNotNone(res.get("matched_term"))

        non_critique_payload = {
            "userMessage": "Please proceed with the correlation matrix calculation.",
            "caller": "academic-orchestrator",
            "conversationId": "test-conv-002",
        }
        res_non = LearningHooks.capture_user_correction(non_critique_payload)
        self.assertFalse(res_non.get("is_critique"), "Neutral message should not be classified as critique")

    def test_04_handle_pre_invocation_injects_learning_directive_on_critique(self):
        """handle_pre_invocation must inject a high-priority learning trigger into ephemeral context."""
        payload = {
            "userMessage": "The effect size in Table 3 is incorrect, please fix it.",
            "caller": "academic-orchestrator",
            "conversationId": "test-conv-003",
        }
        res = LearningHooks.handle_pre_invocation(payload)
        inject_steps = res.get("injectSteps", [])
        self.assertGreater(len(inject_steps), 0, "Expected injectSteps in handle_pre_invocation response")
        msg = inject_steps[0].get("ephemeralMessage", "")
        self.assertIn("CONTINUOUS LEARNING TRIGGER ACTIVE", msg)
        self.assertIn("trajectory-analyzer", msg)
        self.assertIn("behavior-analyst", msg)
        self.assertIn("knowledge-curator", msg)

    def test_05_orchestrator_non_execution_invariant_preserved(self):
        """Verifies academic-orchestrator still strictly satisfies Directive 20 (Non-Execution Invariant)."""
        data, _ = self._parse_frontmatter(self.orchestrator_path)
        tools = data.get("tools", [])
        forbidden = ["run_command", "write_to_file", "replace_file_content", "edit_file"]
        for fb in forbidden:
            self.assertNotIn(
                fb,
                tools,
                f"Directive 20 violation: academic-orchestrator must NOT possess '{fb}'",
            )
        self.assertIn("invoke_subagent", tools, "academic-orchestrator MUST possess invoke_subagent")


if __name__ == "__main__":
    unittest.main()
