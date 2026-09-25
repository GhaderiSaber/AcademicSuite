#!/usr/bin/env python3
"""
Regression test for ATK-03: Worker Invoking Unauthorized Worker.

Verifies that:
1. Specialist worker subagents do NOT declare invoke_subagent in their frontmatter tools list.
2. .agents/hooks.json includes invoke_subagent in PreToolUse and PostToolUse matchers.
3. transcript_and_rule_guard.py denies invoke_subagent calls from worker agents.
"""

import os
import sys
import json
import yaml
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)

from verification.transcript_and_rule_guard import handle_pre_tool_use


class TestAgentDelegationGuard(unittest.TestCase):

    def test_workers_lack_invoke_subagent_in_agent_md(self):
        """Worker agents must not declare invoke_subagent or manage_subagents (ATK-03)."""
        workers = ["academic-writer", "evidence-auditor", "final-judge"]
        for worker in workers:
            agent_path = os.path.join(ROOT_DIR, ".agents", "agents", worker, "agent.md")
            self.assertTrue(os.path.exists(agent_path), f"File not found: {agent_path}")

            with open(agent_path, "r", encoding="utf-8") as f:
                content = f.read()

            parts = content.split("---")
            self.assertGreaterEqual(len(parts), 3, f"YAML frontmatter missing in {worker}")
            frontmatter = yaml.safe_load(parts[1])
            tools = frontmatter.get("tools", [])

            self.assertNotIn("invoke_subagent", tools, f"{worker} must not possess invoke_subagent")
            self.assertNotIn("manage_subagents", tools, f"{worker} must not possess manage_subagents")

    def test_hooks_json_intercepts_invoke_subagent(self):
        """hooks.json must include invoke_subagent in PreToolUse and PostToolUse matchers (ATK-03)."""
        hooks_path = os.path.join(ROOT_DIR, ".agents", "hooks.json")
        self.assertTrue(os.path.exists(hooks_path), f"File not found: {hooks_path}")

        with open(hooks_path, "r", encoding="utf-8") as f:
            hooks = json.load(f)

        guard = hooks.get("track2-academic-orchestrator-guard") or hooks.get("constitutional-guard", {})
        pre_tool = guard.get("PreToolUse", [{}])[0].get("matcher", "")
        post_tool = guard.get("PostToolUse", [{}])[0].get("matcher", "")

        self.assertIn("invoke_subagent", pre_tool, "PreToolUse matcher must intercept invoke_subagent")
        self.assertIn("invoke_subagent", post_tool, "PostToolUse matcher must intercept invoke_subagent")

    def test_pre_tool_use_denies_worker_delegation(self):
        """handle_pre_tool_use denies invoke_subagent calls originating from worker subagents."""
        payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {"TypeName": "literature-expert", "Role": "Researcher", "Prompt": "Search lit"}
                    ]
                }
            },
            "agentName": "academic-writer",
            "workspacePaths": [ROOT_DIR]
        }
        res = handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("worker delegation guard", res.get("reason", "").lower())

    def test_pre_tool_use_denies_excessive_depth(self):
        """handle_pre_tool_use denies invoke_subagent calls when depth exceeds 3 (ATK-17)."""
        payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {"TypeName": "statistics-agent", "Role": "Statistician", "Prompt": "Run models"}
                    ]
                }
            },
            "agentName": "academic-orchestrator",
            "depth": 3,
            "workspacePaths": [ROOT_DIR]
        }
        res = handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("excessive nesting guard", res.get("reason", "").lower())


if __name__ == "__main__":
    unittest.main()
