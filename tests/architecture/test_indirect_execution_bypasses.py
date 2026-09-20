#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_indirect_execution_bypasses.py — Indirect Execution Bypass Negative Test Suite

Phase 18: Verifies that removing run_command cannot be circumvented via indirect proxy execution:
1. MCP Tool Gate: academic-orchestrator and non-executors cannot call MCP tools or execution-capable MCP servers (posthog, supabase).
2. Dynamic Subagent Creation Gate: academic-orchestrator cannot define subagents or elevate write/run privileges.
3. Process Injection Gate: academic-orchestrator cannot send stdin input to background tasks via manage_task.
4. Scheduled Execution Gate: academic-orchestrator cannot schedule background commands via schedule.
5. Runner Skill Disassociation: academic-orchestrator does not declare batch runner skills (academic-suite-orchestrator).
6. Execution Taxonomy Separation: classify_execution_capabilities strictly distinguishes DIRECT vs. INDIRECT execution.
"""

import os
import sys
import unittest
import importlib.util

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

hooks_dir = os.path.join(ROOT_DIR, ".agents", "hooks")
if hooks_dir not in sys.path:
    sys.path.insert(0, hooks_dir)

from validators.agent_integrity import (
    parse_yaml_frontmatter,
    AGENTS_DIR,
)
from contracts.agents.capability_policy import (
    load_capability_policy,
    get_agent_policy,
    classify_execution_capabilities,
    DIRECT_EXECUTION_TOOLS,
    INDIRECT_EXECUTION_TOOLS,
    EXECUTION_CAPABLE_MCP_SERVERS,
    EXECUTION_CAPABLE_MCP_TOOLS,
    EXECUTION_RUNNER_SKILLS,
)

from safety_hooks import SafetyHooks


class TestIndirectExecutionBypasses(unittest.TestCase):
    """Negative architecture tests for indirect execution paths and capability boundaries."""

    @classmethod
    def setUpClass(cls):
        cls.policy = load_capability_policy()
        cls.hooks = SafetyHooks()

    def get_agent_frontmatter(self, agent_name: str) -> dict:
        """Reads and parses an agent's on-disk agent.md frontmatter."""
        path = os.path.join(AGENTS_DIR, agent_name, "agent.md")
        self.assertTrue(os.path.isfile(path), f"Agent file does not exist: {path}")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        fm, _, err = parse_yaml_frontmatter(content)
        self.assertIsNone(err, f"Error parsing frontmatter for {agent_name}: {err}")
        return fm

    def test_orchestrator_has_no_indirect_execution_tools(self):
        """Negative Test: academic-orchestrator must NOT declare any indirect execution tools."""
        fm = self.get_agent_frontmatter("academic-orchestrator")
        tools = set(fm.get("tools", []))

        for tool in INDIRECT_EXECUTION_TOOLS:
            self.assertNotIn(
                tool,
                tools,
                f"academic-orchestrator declares indirect execution tool '{tool}'!"
            )

    def test_orchestrator_has_no_batch_runner_skills(self):
        """Negative Test: academic-orchestrator must NOT declare batch runner skills ('academic-suite-orchestrator')."""
        fm = self.get_agent_frontmatter("academic-orchestrator")
        skills = set(fm.get("skills", []))

        for runner_skill in EXECUTION_RUNNER_SKILLS:
            self.assertNotIn(
                runner_skill,
                skills,
                f"academic-orchestrator declares batch execution runner skill '{runner_skill}'!"
            )

    def test_policy_forbids_indirect_execution_for_non_executors(self):
        """Negative Test: SSOT policy must forbid all indirect execution tools for non-executors."""
        agents = self.policy.get("agents", {})
        for name, spec in agents.items():
            if not spec.get("can_execute_code", True):
                forbidden = set(spec.get("forbidden", []))
                for indirect_tool in INDIRECT_EXECUTION_TOOLS:
                    self.assertIn(
                        indirect_tool,
                        forbidden,
                        f"Agent '{name}' (can_execute_code=False) does not forbid indirect tool '{indirect_tool}' in SSOT policy!"
                    )

    def test_hook_denies_orchestrator_mcp_calls(self):
        """Runtime Hook Gate: call_mcp_tool is blocked for academic-orchestrator."""
        payload = {
            "agentName": "academic-orchestrator",
            "toolCall": {
                "name": "call_mcp_tool",
                "args": {"ServerName": "posthog", "ToolName": "exec", "Arguments": {"cmd": "ls"}}
            }
        }
        res = self.hooks.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Indirect Execution Guard", res.get("reason", ""))

    def test_hook_denies_high_risk_mcp_tools_for_non_workers(self):
        """Runtime Hook Gate: high-risk execution MCP tools are blocked for unauthorized callers."""
        for tool in EXECUTION_CAPABLE_MCP_TOOLS:
            payload = {
                "agentName": "academic-writer",  # Writer is docgen only, not a general code worker
                "toolCall": {
                    "name": "call_mcp_tool",
                    "args": {"ServerName": "supabase", "ToolName": tool, "Arguments": {}}
                }
            }
            res = self.hooks.handle_pre_tool_use(payload)
            self.assertEqual(
                res.get("decision"),
                "deny",
                f"Expected MCP tool '{tool}' to be denied for caller 'academic-writer'"
            )

    def test_hook_denies_dynamic_subagent_creation_by_orchestrator(self):
        """Runtime Hook Gate: define_subagent is blocked for academic-orchestrator."""
        payload = {
            "agentName": "academic-orchestrator",
            "toolCall": {
                "name": "define_subagent",
                "args": {
                    "name": "proxy_worker",
                    "description": "Ad-hoc worker",
                    "system_prompt": "Run commands",
                    "enable_write_tools": True
                }
            }
        }
        res = self.hooks.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("define_subagent", res.get("reason", ""))

    def test_hook_denies_dynamic_privilege_elevation(self):
        """Runtime Hook Gate: define_subagent with enable_write_tools=True is blocked universally."""
        payload = {
            "agentName": "statistics-agent",
            "toolCall": {
                "name": "define_subagent",
                "args": {
                    "name": "elevated_proxy",
                    "description": "Proxy with elevated write privileges",
                    "system_prompt": "Execute arbitrary shell",
                    "enable_write_tools": True
                }
            }
        }
        res = self.hooks.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Dynamic elevation of write or subagent privileges", res.get("reason", ""))

    def test_hook_denies_background_task_input_injection(self):
        """Runtime Hook Gate: manage_task(Action='send_input') is blocked for non-executors."""
        payload = {
            "agentName": "academic-orchestrator",
            "toolCall": {
                "name": "manage_task",
                "args": {"Action": "send_input", "TaskId": "task-42", "Input": "rm -rf /"}
            }
        }
        res = self.hooks.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("injecting shell input into background tasks", res.get("reason", ""))

    def test_hook_denies_schedule_for_orchestrator(self):
        """Runtime Hook Gate: schedule is blocked for academic-orchestrator."""
        payload = {
            "agentName": "academic-orchestrator",
            "toolCall": {
                "name": "schedule",
                "args": {"DurationSeconds": 60, "Prompt": "Run background task"}
            }
        }
        res = self.hooks.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("scheduling background execution tasks", res.get("reason", ""))

    def test_taxonomy_classifier_identifies_direct_and_indirect(self):
        """Classification Test: classify_execution_capabilities accurately separates direct vs indirect."""
        # 1. Orchestrator
        orch_fm = self.get_agent_frontmatter("academic-orchestrator")
        orch_class = classify_execution_capabilities("academic-orchestrator", orch_fm, self.policy)
        self.assertFalse(orch_class["can_execute_code"])
        self.assertFalse(orch_class["has_direct_execution"])
        self.assertFalse(orch_class["has_indirect_execution"])
        self.assertEqual(orch_class["direct_execution"], [])
        self.assertEqual(orch_class["indirect_execution"], [])
        self.assertTrue(orch_class["is_compliant"])

        # 2. Statistics Agent
        stats_fm = self.get_agent_frontmatter("statistics-agent")
        stats_class = classify_execution_capabilities("statistics-agent", stats_fm, self.policy)
        self.assertTrue(stats_class["can_execute_code"])
        self.assertTrue(stats_class["has_direct_execution"])
        self.assertIn("run_command", stats_class["direct_execution"])
        self.assertFalse(stats_class["has_indirect_execution"])
        self.assertTrue(stats_class["is_compliant"])


if __name__ == "__main__":
    unittest.main()
