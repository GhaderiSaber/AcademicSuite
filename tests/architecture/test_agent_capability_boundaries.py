#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_agent_capability_boundaries.py — Architecture Negative Capability Test Suite

Phase 14: Enforces negative capability tests across all agent tiers.
These tests verify that tools are physically absent from agent toolsets,
ensuring mechanical least-privilege enforcement rather than relying merely
on prompt/instruction obedience.

Tests:
1.  test_orchestrator_cannot_execute_commands()
2.  test_orchestrator_cannot_write_files()
3.  test_orchestrator_can_invoke_subagents()
4.  test_orchestrator_can_read_project()
5.  test_methodology_expert_cannot_execute()
6.  test_statistical_expert_cannot_execute()
7.  test_statistics_agent_can_execute()
8.  test_data_agent_can_execute()
9.  test_academic_writer_can_generate_documents()
10. test_final_judge_cannot_execute()
11. test_evidence_auditor_cannot_execute_shell()
12. test_evaluative_critics_cannot_execute()
13. test_read_only_analysts_cannot_write_or_execute()
14. test_execution_workers_cannot_delegate()
"""

import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from validators.agent_integrity import (
    parse_yaml_frontmatter,
    AGENTS_DIR,
)
from contracts.agents.capability_policy import (
    load_capability_policy,
    get_agent_policy,
)


class TestAgentCapabilityBoundaries(unittest.TestCase):
    """Architecture-level negative and positive capability boundary tests."""

    @classmethod
    def setUpClass(cls):
        cls.policy = load_capability_policy()

    def get_agent_frontmatter(self, agent_name: str) -> dict:
        """Reads and parses an agent's on-disk agent.md frontmatter."""
        path = os.path.join(AGENTS_DIR, agent_name, "agent.md")
        self.assertTrue(os.path.isfile(path), f"Agent file does not exist: {path}")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        fm, _, err = parse_yaml_frontmatter(content)
        self.assertIsNone(err, f"Error parsing frontmatter for {agent_name}: {err}")
        self.assertIsNotNone(fm, f"Frontmatter is empty for {agent_name}")
        return fm

    def get_agent_tools(self, agent_name: str) -> set:
        """Extracts the exact set of declared tools for an agent."""
        fm = self.get_agent_frontmatter(agent_name)
        return set(fm.get("tools", []))

    # =========================================================================
    # 1. Academic-Orchestrator Tests
    # =========================================================================

    def test_orchestrator_cannot_execute_commands(self):
        """Negative Capability Test: academic-orchestrator must NOT have execution tools."""
        tools = self.get_agent_tools("academic-orchestrator")
        self.assertNotIn("run_command", tools, "academic-orchestrator MUST NOT declare run_command")
        self.assertNotIn("manage_task", tools, "academic-orchestrator MUST NOT declare manage_task")
        self.assertNotIn("schedule", tools, "academic-orchestrator MUST NOT declare schedule")

        # SSOT Policy verification
        policy = get_agent_policy("academic-orchestrator", self.policy)
        self.assertFalse(policy.get("can_execute_code"))
        self.assertIn("run_command", policy.get("forbidden", []))

    def test_orchestrator_cannot_write_files(self):
        """Negative Capability Test: academic-orchestrator must NOT have file writing/editing tools."""
        tools = self.get_agent_tools("academic-orchestrator")
        self.assertNotIn("write_to_file", tools, "academic-orchestrator MUST NOT declare write_to_file")
        self.assertNotIn("replace_file_content", tools, "academic-orchestrator MUST NOT declare replace_file_content")
        self.assertNotIn("edit_file", tools, "academic-orchestrator MUST NOT declare edit_file")

        # SSOT Policy verification
        policy = get_agent_policy("academic-orchestrator", self.policy)
        self.assertFalse(policy.get("can_write_files"))
        self.assertIn("write_to_file", policy.get("forbidden", []))
        self.assertIn("replace_file_content", policy.get("forbidden", []))

    def test_orchestrator_can_invoke_subagents(self):
        """Positive Capability Test: academic-orchestrator MUST have subagent orchestration tools."""
        tools = self.get_agent_tools("academic-orchestrator")
        self.assertIn("invoke_subagent", tools, "academic-orchestrator MUST declare invoke_subagent")
        self.assertIn("manage_subagents", tools, "academic-orchestrator MUST declare manage_subagents")
        self.assertIn("send_message", tools, "academic-orchestrator MUST declare send_message")

        # SSOT Policy verification
        policy = get_agent_policy("academic-orchestrator", self.policy)
        self.assertTrue(policy.get("can_delegate"))
        self.assertIn("invoke_subagent", policy.get("required", []))

    def test_orchestrator_can_read_project(self):
        """Positive Capability Test: academic-orchestrator MUST have read/inspection tools."""
        tools = self.get_agent_tools("academic-orchestrator")
        self.assertIn("view_file", tools, "academic-orchestrator MUST declare view_file")
        self.assertIn("list_dir", tools, "academic-orchestrator MUST declare list_dir")
        self.assertIn("grep_search", tools, "academic-orchestrator MUST declare grep_search")
        self.assertIn("find_by_name", tools, "academic-orchestrator MUST declare find_by_name")

    # =========================================================================
    # 2. Specialist Planners Tests
    # =========================================================================

    def test_methodology_expert_cannot_execute(self):
        """Negative Capability Test: methodology-expert plans methodology but CANNOT execute shell/code."""
        tools = self.get_agent_tools("methodology-expert")
        self.assertNotIn("run_command", tools, "methodology-expert MUST NOT declare run_command")
        self.assertNotIn("manage_task", tools, "methodology-expert MUST NOT declare manage_task")

        # SSOT Policy verification
        policy = get_agent_policy("methodology-expert", self.policy)
        self.assertFalse(policy.get("can_execute_code"))
        self.assertIn("run_command", policy.get("forbidden", []))
        self.assertIn(policy.get("role"), ["planner", "advisor"])

    def test_statistical_expert_cannot_execute(self):
        """Negative Capability Test: statistical-expert decides estimands but CANNOT execute shell/code."""
        tools = self.get_agent_tools("statistical-expert")
        self.assertNotIn("run_command", tools, "statistical-expert MUST NOT declare run_command")
        self.assertNotIn("manage_task", tools, "statistical-expert MUST NOT declare manage_task")

        # SSOT Policy verification
        policy = get_agent_policy("statistical-expert", self.policy)
        self.assertFalse(policy.get("can_execute_code"))
        self.assertIn("run_command", policy.get("forbidden", []))
        self.assertIn(policy.get("role"), ["planner", "advisor"])

    # =========================================================================
    # 3. Execution Workers Tests
    # =========================================================================

    def test_statistics_agent_can_execute(self):
        """Positive Capability Test: statistics-agent is a Class A worker and MUST have run_command."""
        tools = self.get_agent_tools("statistics-agent")
        self.assertIn("run_command", tools, "statistics-agent MUST declare run_command")
        self.assertIn("write_to_file", tools, "statistics-agent MUST declare write_to_file")

        # SSOT Policy verification
        policy = get_agent_policy("statistics-agent", self.policy)
        self.assertTrue(policy.get("can_execute_code"))
        self.assertIn("run_command", policy.get("required", []))
        self.assertEqual(policy.get("role"), "execution_worker")

    def test_data_agent_can_execute(self):
        """Positive Capability Test: data-agent is a Class A worker and MUST have run_command."""
        tools = self.get_agent_tools("data-agent")
        self.assertIn("run_command", tools, "data-agent MUST declare run_command")
        self.assertIn("write_to_file", tools, "data-agent MUST declare write_to_file")

        # SSOT Policy verification
        policy = get_agent_policy("data-agent", self.policy)
        self.assertTrue(policy.get("can_execute_code"))
        self.assertIn("run_command", policy.get("required", []))
        self.assertEqual(policy.get("role"), "execution_worker")

    def test_academic_writer_can_generate_documents(self):
        """Capability & Boundary Test: academic-writer has execution strictly bounded to docgen."""
        tools = self.get_agent_tools("academic-writer")
        self.assertIn("run_command", tools, "academic-writer MUST declare run_command for docgen")
        self.assertIn("write_to_file", tools, "academic-writer MUST declare write_to_file")
        self.assertIn("replace_file_content", tools, "academic-writer MUST declare replace_file_content")
        self.assertNotIn("invoke_subagent", tools, "academic-writer MUST NOT declare invoke_subagent")

        # SSOT Policy verification
        policy = get_agent_policy("academic-writer", self.policy)
        self.assertTrue(policy.get("can_execute_code"))
        self.assertEqual(policy.get("execution_scope"), "docgen_only")
        self.assertIn("invoke_subagent", policy.get("forbidden", []))

    # =========================================================================
    # 4. Auditors & Reviewers Tests
    # =========================================================================

    def test_final_judge_cannot_execute(self):
        """Negative Capability Test: final-judge evaluates committee decisions but CANNOT execute code."""
        tools = self.get_agent_tools("final-judge")
        self.assertNotIn("run_command", tools, "final-judge MUST NOT declare run_command")
        self.assertNotIn("manage_task", tools, "final-judge MUST NOT declare manage_task")

        # SSOT Policy verification
        policy = get_agent_policy("final-judge", self.policy)
        self.assertFalse(policy.get("can_execute_code"))
        self.assertIn("run_command", policy.get("forbidden", []))
        self.assertEqual(policy.get("role"), "auditor")

    def test_evidence_auditor_cannot_execute_shell(self):
        """Negative Capability Test: evidence-auditor verifies citations via web/read but CANNOT execute shell."""
        tools = self.get_agent_tools("evidence-auditor")
        self.assertNotIn("run_command", tools, "evidence-auditor MUST NOT declare run_command")
        self.assertNotIn("manage_task", tools, "evidence-auditor MUST NOT declare manage_task")
        self.assertIn("search_web", tools, "evidence-auditor MUST have search_web")
        self.assertIn("read_url_content", tools, "evidence-auditor MUST have read_url_content")

        # SSOT Policy verification
        policy = get_agent_policy("evidence-auditor", self.policy)
        self.assertFalse(policy.get("can_execute_code"))
        self.assertIn("run_command", policy.get("forbidden", []))
        self.assertEqual(policy.get("role"), "auditor")

    def test_evaluative_critics_cannot_execute(self):
        """Negative Capability Test: results-auditor, academic-challenger, and journal-strategist cannot execute."""
        critics = ["results-auditor", "academic-challenger", "journal-strategist"]
        for critic in critics:
            tools = self.get_agent_tools(critic)
            self.assertNotIn("run_command", tools, f"{critic} MUST NOT declare run_command")
            policy = get_agent_policy(critic, self.policy)
            self.assertFalse(policy.get("can_execute_code"), f"{critic} policy can_execute_code must be False")
            self.assertIn("run_command", policy.get("forbidden", []), f"{critic} policy must forbid run_command")

    # =========================================================================
    # 5. Read-Only Analysts & Delegation Boundaries
    # =========================================================================

    def test_learning_analysts_capabilities_and_boundaries(self):
        """Capability Test: behavior-analyst and trajectory-analyzer can write JSON files but cannot execute code."""
        analysts = ["behavior-analyst", "trajectory-analyzer"]
        for analyst in analysts:
            tools = self.get_agent_tools(analyst)
            self.assertNotIn("run_command", tools, f"{analyst} MUST NOT declare run_command")
            self.assertIn("write_to_file", tools, f"{analyst} MUST declare write_to_file")
            self.assertNotIn("replace_file_content", tools, f"{analyst} MUST NOT declare replace_file_content")
            policy = get_agent_policy(analyst, self.policy)
            self.assertFalse(policy.get("can_execute_code"))
            self.assertTrue(policy.get("can_write_files"))

    def test_execution_workers_cannot_delegate(self):
        """Negative Capability Test: specialist execution workers CANNOT invoke subagents."""
        workers = [
            "statistics-agent", "data-agent", "data-curator", "psychometric-expert",
            "longitudinal-modmed-expert", "qualitative-analyst", "meta-analyst",
            "academic-writer"
        ]
        for worker in workers:
            tools = self.get_agent_tools(worker)
            self.assertNotIn("invoke_subagent", tools, f"{worker} MUST NOT declare invoke_subagent")
            self.assertNotIn("manage_subagents", tools, f"{worker} MUST NOT declare manage_subagents")
            policy = get_agent_policy(worker, self.policy)
            self.assertFalse(policy.get("can_delegate"), f"{worker} policy can_delegate must be False")

    def test_advisors_cannot_delegate(self):
        """Negative Capability Test: Control Plane advisors CANNOT invoke subagents."""
        advisors = ["methodology-expert", "statistical-expert"]
        for advisor in advisors:
            tools = self.get_agent_tools(advisor)
            self.assertNotIn("invoke_subagent", tools, f"{advisor} MUST NOT declare invoke_subagent")
            self.assertNotIn("manage_subagents", tools, f"{advisor} MUST NOT declare manage_subagents")
            policy = get_agent_policy(advisor, self.policy)
            self.assertFalse(policy.get("can_delegate"), f"{advisor} policy can_delegate must be False")

    def test_advisors_cannot_write_files(self):
        """Negative Capability Test: Control Plane advisors are consultative and CANNOT mutate files."""
        advisors = ["methodology-expert", "statistical-expert"]
        for advisor in advisors:
            tools = self.get_agent_tools(advisor)
            self.assertNotIn("write_to_file", tools, f"{advisor} MUST NOT declare write_to_file")
            self.assertNotIn("replace_file_content", tools, f"{advisor} MUST NOT declare replace_file_content")
            policy = get_agent_policy(advisor, self.policy)
            self.assertFalse(policy.get("can_write_files"), f"{advisor} policy can_write_files must be False")

    def test_critics_cannot_write_files(self):
        """Negative Capability Test: Validation Plane critics/auditors CANNOT mutate files."""
        critics = [
            "results-auditor",
            "academic-challenger",
            "final-judge",
            "evidence-auditor",
            "statistical-auditor",
        ]
        for critic in critics:
            tools = self.get_agent_tools(critic)
            self.assertNotIn("write_to_file", tools, f"{critic} MUST NOT declare write_to_file")
            self.assertNotIn("replace_file_content", tools, f"{critic} MUST NOT declare replace_file_content")
            policy = get_agent_policy(critic, self.policy)
            self.assertFalse(policy.get("can_write_files"), f"{critic} policy can_write_files must be False")


if __name__ == "__main__":
    unittest.main()
