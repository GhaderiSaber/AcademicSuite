#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_learning_subagents_write_restrictions.py

Verifies:
1. All 6 continuous learning subagents possess write_to_file capability.
2. Learning subagents are permitted to write JSON (.json, .jsonl) and Markdown (.md) files.
3. Any attempt by learning subagents to write .doc, .docx, or non-documentation files is strictly DENIED by the safety hook.
4. Non-learning worker subagents (e.g. academic-writer) remain unrestricted by this guard.
5. All 6 learning subagents comply with the canonical capability policy in agent_capabilities.yaml.
"""

import os
import sys
import unittest
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AGENTS_DIR = os.path.join(REPO_ROOT, ".agents")
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)

from hooks.safety_hooks import SafetyHooks, LEARNING_SUBAGENTS, is_learning_subagent
from contracts.agents.capability_policy import load_capability_policy, get_agent_policy


class TestLearningSubagentsWriteRestrictions(unittest.TestCase):
    """Test suite for learning subagents file write capabilities and format restrictions."""

    def setUp(self):
        self.policy = load_capability_policy()
        self.learning_agents = [
            "behavior-analyst",
            "curriculum-builder",
            "evaluation-agent",
            "knowledge-curator",
            "skill-evolver",
            "trajectory-analyzer",
        ]

    def _parse_frontmatter(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        parts = content.split("---")
        self.assertGreaterEqual(len(parts), 3, f"File {file_path} missing frontmatter")
        return yaml.safe_load(parts[1])

    # =========================================================================
    # 1. Capability Policy & Agent Definition Verification
    # =========================================================================

    def test_all_six_learning_agents_have_write_to_file_in_policy(self):
        """All 6 continuous learning subagents must have can_write_files: true and write_to_file in policy."""
        for agent in self.learning_agents:
            spec = get_agent_policy(agent, self.policy)
            self.assertTrue(
                spec.get("can_write_files"),
                f"Agent '{agent}' must have can_write_files: true in agent_capabilities.yaml"
            )
            self.assertIn(
                "write_to_file",
                spec.get("required", []),
                f"Agent '{agent}' must list 'write_to_file' in required tools"
            )
            self.assertNotIn(
                "write_to_file",
                spec.get("forbidden", []),
                f"Agent '{agent}' must NOT list 'write_to_file' in forbidden tools"
            )

    def test_all_six_learning_agents_declare_write_to_file_in_frontmatter(self):
        """All 6 continuous learning subagents must declare write_to_file in their agent.md."""
        for agent in self.learning_agents:
            agent_md = os.path.join(AGENTS_DIR, "agents", agent, "agent.md")
            self.assertTrue(os.path.isfile(agent_md), f"agent.md missing for {agent}")
            fm = self._parse_frontmatter(agent_md)
            tools = fm.get("tools", [])
            self.assertIn(
                "write_to_file",
                tools,
                f"Agent '{agent}' must declare 'write_to_file' in its agent.md frontmatter"
            )

    def test_learning_subagents_helper_identifies_all_six_roles(self):
        """is_learning_subagent helper must return True for all 6 roles and False for others."""
        for agent in self.learning_agents:
            self.assertTrue(is_learning_subagent(agent), f"Expected {agent} to be recognized as learning subagent")
            self.assertTrue(is_learning_subagent(agent.upper()))
            self.assertTrue(is_learning_subagent(f"subagent_{agent}"))

        non_learning_agents = [
            "academic-writer",
            "statistics-agent",
            "data-agent",
            "academic-orchestrator",
            "research-agent",
        ]
        for agent in non_learning_agents:
            self.assertFalse(is_learning_subagent(agent), f"Agent {agent} must NOT be classified as learning subagent")

    # =========================================================================
    # 2. Positive Verification: JSON Files Allowed
    # =========================================================================

    def test_learning_subagents_allowed_to_write_json_files(self):
        """All 6 learning subagents must be allowed to write valid .json files."""
        for agent in self.learning_agents:
            payload = {
                "agentName": agent,
                "toolCall": {
                    "name": "write_to_file",
                    "args": {
                        "TargetFile": f"/workspace/evals/test_{agent}.json",
                        "CodeContent": "{\"status\": \"ok\"}",
                        "Description": "Writing test JSON",
                        "Overwrite": True
                    }
                },
                "workspacePaths": ["/workspace"]
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(
                res.get("decision"), "allow",
                f"Agent '{agent}' was unexpectedly denied writing a .json file: {res.get('reason')}"
            )

    # =========================================================================
    # 3. Negative Verification: .doc, .docx, .md Files Blocked
    # =========================================================================

    def test_learning_subagents_denied_writing_doc_files(self):
        """All 6 learning subagents must be denied writing .doc files."""
        for agent in self.learning_agents:
            payload = {
                "agentName": agent,
                "toolCall": {
                    "name": "write_to_file",
                    "args": {
                        "TargetFile": "/workspace/draft.doc",
                        "CodeContent": "binary content",
                        "Description": "Attempting to write doc file",
                        "Overwrite": True
                    }
                },
                "workspacePaths": ["/workspace"]
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny")
            reason = res.get("reason", "")
            self.assertIn("Learning Subagent File Restriction", reason)
            self.assertIn("restricted to writing JSON and Markdown files", reason)

    def test_learning_subagents_denied_writing_docx_files(self):
        """All 6 learning subagents must be denied writing .docx files."""
        for agent in self.learning_agents:
            payload = {
                "agentName": agent,
                "toolCall": {
                    "name": "write_to_file",
                    "args": {
                        "TargetFile": "/workspace/chapter_draft.docx",
                        "CodeContent": "binary docx",
                        "Description": "Attempting to write docx file",
                        "Overwrite": True
                    }
                },
                "workspacePaths": ["/workspace"]
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny")
            reason = res.get("reason", "")
            self.assertIn("Learning Subagent File Restriction", reason)
            self.assertIn("restricted to writing JSON and Markdown files", reason)

    def test_learning_subagents_allowed_to_write_md_files(self):
        """All 6 learning subagents must be allowed to write valid .md files (e.g. SKILL.md, reports)."""
        for agent in self.learning_agents:
            payload = {
                "agentName": agent,
                "toolCall": {
                    "name": "write_to_file",
                    "args": {
                        "TargetFile": f"/workspace/evals/test_{agent}.md",
                        "CodeContent": "# Notes and Reports",
                        "Description": "Writing markdown file",
                        "Overwrite": True
                    }
                },
                "workspacePaths": ["/workspace"]
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(
                res.get("decision"), "allow",
                f"Agent '{agent}' was unexpectedly denied writing a .md file: {res.get('reason')}"
            )

    def test_learning_subagents_denied_writing_other_non_json_extensions(self):
        """All 6 learning subagents must be denied writing other non-JSON formats (.py, .txt, .sh)."""
        forbidden_extensions = ["script.py", "output.txt", "run.sh", "data.csv"]
        for ext_file in forbidden_extensions:
            for agent in self.learning_agents:
                payload = {
                    "agentName": agent,
                    "toolCall": {
                        "name": "write_to_file",
                        "args": {
                            "TargetFile": f"/workspace/{ext_file}",
                            "CodeContent": "content",
                            "Description": "Attempting non-json write",
                            "Overwrite": True
                        }
                    },
                    "workspacePaths": ["/workspace"]
                }
                res = SafetyHooks.handle_pre_tool_use(payload)
                self.assertEqual(
                    res.get("decision"), "deny",
                    f"Agent '{agent}' was not denied writing '{ext_file}'"
                )
                self.assertIn("Learning Subagent File Restriction", res.get("reason", ""))

    # =========================================================================
    # 4. Non-Learning Workers Unaffected
    # =========================================================================

    def test_thesis_writer_can_write_md_and_docx(self):
        """Thesis writer (academic-writer) is NOT blocked by learning subagent restriction."""
        for ext_file in ["chapter_4.md", "chapter_4.docx"]:
            payload = {
                "agentName": "academic-writer",
                "toolCall": {
                    "name": "write_to_file",
                    "args": {
                        "TargetFile": f"/workspace/{ext_file}",
                        "CodeContent": "Scholarly text",
                        "Description": "Drafting chapter deliverable",
                        "Overwrite": True
                    }
                },
                "workspacePaths": ["/workspace"]
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(
                res.get("decision"), "allow",
                f"academic-writer was unexpectedly denied writing {ext_file}: {res.get('reason')}"
            )


if __name__ == "__main__":
    unittest.main()
