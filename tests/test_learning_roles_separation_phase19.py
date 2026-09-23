#!/usr/bin/env python3
"""
Unit tests for Phase 19: Separation of Learning Roles across 6 Native Subagents.
Validates:
1. Exact presence of the Six Core Questions in agent definitions and contracts.
2. Least-privilege tool boundaries across all 6 learning roles.
3. Non-overlapping cognitive responsibilities.
4. Specification compliance in learning/LEARNING_MULTI_AGENT_SPEC.md.
"""

import os
import unittest
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

EXPECTED_ROLES = {
    "trajectory-analyzer": {
        "core_question": "What actually happened?",
        "tools": ["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file"],
        "has_run_command": False,
        "has_write_tools": True,
        "workspace_mode": "inherit",
    },
    "behavior-analyst": {
        "core_question": "What behavior was wrong?",
        "tools": ["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file"],
        "has_run_command": False,
        "has_write_tools": True,
        "workspace_mode": "inherit",
    },
    "knowledge-curator": {
        "core_question": "What generalizable lesson does this imply?",
        "tools": ["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file"],
        "has_run_command": False,
        "has_write_tools": True,
        "workspace_mode": "inherit",
    },
    "skill-evolver": {
        "core_question": "What candidate modification would change the behavior?",
        "tools": ["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file"],
        "has_run_command": False,
        "has_write_tools": True,
        "workspace_mode": "branch",
    },
    "evaluation-agent": {
        "core_question": "Did the modification actually improve behavior?",
        "tools": ["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file", "run_command"],
        "has_run_command": True,
        "has_write_tools": True,
        "workspace_mode": "branch",
    },
    "curriculum-builder": {
        "core_question": "What future task would test whether the lesson generalizes?",
        "tools": ["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file"],
        "has_run_command": False,
        "has_write_tools": True,
        "workspace_mode": "inherit",
    },
}


class TestLearningRolesSeparationPhase19(unittest.TestCase):

    def _parse_frontmatter(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        parts = content.split("---")
        self.assertGreaterEqual(len(parts), 3, f"File {file_path} missing frontmatter")
        data = yaml.safe_load(parts[1])
        return data, parts[2]

    def test_all_six_learning_agent_definitions_exist(self):
        """Verify that agent.md and contract.md exist for all 6 learning roles."""
        for role_name in EXPECTED_ROLES:
            agent_path = os.path.join(REPO_ROOT, ".agents", "agents", role_name, "agent.md")
            contract_path = os.path.join(REPO_ROOT, ".agents", "agents", role_name, "contract.md")
            mirror_path = os.path.join(REPO_ROOT, ".agents", "agents", f"{role_name}.md")

            self.assertTrue(os.path.exists(agent_path), f"Missing {agent_path}")
            self.assertTrue(os.path.exists(contract_path), f"Missing {contract_path}")
            self.assertTrue(os.path.exists(mirror_path), f"Missing {mirror_path}")

    def test_core_questions_in_agent_definitions_and_contracts(self):
        """Verify each agent definition and contract features its specific core question."""
        for role_name, spec in EXPECTED_ROLES.items():
            agent_path = os.path.join(REPO_ROOT, ".agents", "agents", role_name, "agent.md")
            contract_path = os.path.join(REPO_ROOT, ".agents", "agents", role_name, "contract.md")

            with open(agent_path, "r", encoding="utf-8") as f:
                agent_content = f.read()

            with open(contract_path, "r", encoding="utf-8") as f:
                contract_content = f.read()

            core_q = spec["core_question"]
            self.assertIn(
                core_q, agent_content,
                f"Agent {role_name} missing core question '{core_q}' in {agent_path}"
            )
            self.assertIn(
                core_q, contract_content,
                f"Contract for {role_name} missing core question '{core_q}' in {contract_path}"
            )

    def test_least_privilege_tool_boundaries(self):
        """Verify strict tool boundaries (read-only vs staging vs execution)."""
        for role_name, spec in EXPECTED_ROLES.items():
            agent_path = os.path.join(REPO_ROOT, ".agents", "agents", role_name, "agent.md")
            frontmatter, _ = self._parse_frontmatter(agent_path)

            tools = frontmatter.get("tools", [])
            expected_tools = spec["tools"]

            self.assertEqual(
                set(tools), set(expected_tools),
                f"Role {role_name} tools mismatch. Expected {expected_tools}, got {tools}"
            )

            if spec["has_run_command"]:
                self.assertIn("run_command", tools, f"{role_name} should have run_command")
            else:
                self.assertNotIn("run_command", tools, f"{role_name} must NOT have run_command")

            if spec["has_write_tools"]:
                self.assertIn("write_to_file", tools, f"{role_name} should have write_to_file")
            else:
                self.assertNotIn("write_to_file", tools, f"{role_name} must NOT have write_to_file")

    def test_subagent_flag_and_isolation(self):
        """Verify subagent: true and mainAgent: false for all learning roles."""
        for role_name in EXPECTED_ROLES:
            agent_path = os.path.join(REPO_ROOT, ".agents", "agents", role_name, "agent.md")
            frontmatter, _ = self._parse_frontmatter(agent_path)

            self.assertTrue(frontmatter.get("subagent", False), f"{role_name} must be a subagent")
            self.assertFalse(frontmatter.get("mainAgent", True), f"{role_name} must NOT be a mainAgent")
            self.assertEqual(frontmatter.get("agents", []), [], f"{role_name} must not have nested subagents")

    def test_learning_multi_agent_spec_exists_and_covers_all_roles(self):
        """Verify learning/LEARNING_MULTI_AGENT_SPEC.md exists and covers all 6 roles and core questions."""
        candidate = os.path.join(REPO_ROOT, ".agents", "learning", "LEARNING_MULTI_AGENT_SPEC.md")
        spec_path = candidate if os.path.exists(candidate) else os.path.join(REPO_ROOT, "learning", "LEARNING_MULTI_AGENT_SPEC.md")
        self.assertTrue(os.path.exists(spec_path), f"Missing {spec_path}")

        with open(spec_path, "r", encoding="utf-8") as f:
            content = f.read()

        for role_name, spec in EXPECTED_ROLES.items():
            self.assertIn(role_name, content, f"Spec missing role {role_name}")
            self.assertIn(spec["core_question"], content, f"Spec missing core question for {role_name}")

        self.assertIn("USER_FEEDBACK_DETECTED", content)
        self.assertIn("VALIDATION_FAILED", content)
        self.assertIn("Directive 12.1", content)
        self.assertIn("Directive 19", content)


if __name__ == "__main__":
    unittest.main()
