#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_agent_factory_modernized.py — Unit Tests for Modernized Agent Factory

Comprehensive verification of:
1. Canonical Antigravity frontmatter generation and absence of deprecated fields.
2. Canonical directory-form agent creation (.agents/agents/<name>/agent.md) without duplicate flat files.
3. Complete target architecture coverage (7 Durable Agents + 15 Specialist Subagents).
4. All 13 validation rules:
   - unique name
   - valid role
   - mainAgent/subagent consistency
   - valid model
   - rejection of unsupported frontmatter policies (commandExecutionPolicy / command_execution_policy)
   - valid tools and least-privilege tool isolation
   - valid skills
   - valid agent dependencies
   - valid MCP references
   - no self-dependency
   - no unauthorized worker-to-worker dependency
   - no circular dependencies
   - no excessive dependency depth (> 3)
"""

import os
import sys
import shutil
import tempfile
import unittest
import yaml

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from factory.agent_factory import (
    AgentSpec,
    AgentValidationError,
    validate_agent_spec,
    create_agent,
    render_frontmatter,
    get_all_target_agent_specs,
    TARGET_DURABLE_AGENTS,
    TARGET_SUBAGENTS,
    ALL_TARGET_ROLES,
    check_circular_dependencies,
    calculate_max_depth,
)


class TestModernizedAgentFactory(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="academic_suite_factory_modern_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_generate_temporary_test_agent_and_validate_markdown(self):
        """Prove factory by generating a temporary test agent and verifying canonical frontmatter."""
        test_spec = AgentSpec(
            name="temp-test-specialist",
            role="Temporary Test Specialist",
            description="A temporary agent proving the modernized factory generation.",
            model="pro",
            mainAgent=False,
            subagent=True,
            tools=["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file"],
            skills=["mediation", "apa-reporting"],
            agents=[],
            mcpServers=["academic-catalog"],
            inheritCustomizations=True,
            mission="Verify temporary agent generation without polluting workspace.",
            decision_rules=["Rule 1: Always verify parameters.", "Rule 2: Never calculate mentally."],
        )

        res = create_agent(spec=test_spec, target_dir=self.temp_dir)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["agent_name"], "temp-test-specialist")

        # 1. Canonical directory form verification: target_dir/<name>/agent.md
        expected_dir = os.path.join(self.temp_dir, "temp-test-specialist")
        expected_agent_file = os.path.join(expected_dir, "agent.md")
        expected_contract_file = os.path.join(expected_dir, "contract.md")
        flat_file = os.path.join(self.temp_dir, "temp-test-specialist.md")

        self.assertTrue(os.path.isdir(expected_dir), "Agent directory must exist.")
        self.assertTrue(os.path.isfile(expected_agent_file), "agent.md must exist in directory.")
        self.assertTrue(os.path.isfile(expected_contract_file), "contract.md must exist in directory.")
        self.assertFalse(os.path.exists(flat_file), "Duplicate flat .md must NOT be created.")

        # 2. Inspect generated agent.md
        with open(expected_agent_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check absence of deprecated fields
        self.assertNotIn("command_execution_policy", content)

        # Extract and parse YAML frontmatter
        self.assertTrue(content.startswith("---\n"))
        parts = content.split("---")
        self.assertGreaterEqual(len(parts), 3)
        frontmatter_yaml = parts[1]
        fm = yaml.safe_load(frontmatter_yaml)

        # Assert canonical metadata
        self.assertEqual(fm["name"], "temp-test-specialist")
        self.assertEqual(fm["role"], "Temporary Test Specialist")
        self.assertEqual(fm["model"], "pro")
        self.assertFalse(fm["mainAgent"])
        self.assertTrue(fm["subagent"])
        self.assertNotIn("commandExecutionPolicy", fm)
        self.assertNotIn("command_execution_policy", fm)
        self.assertIn("mediation", fm["skills"])
        self.assertIn("view_file", fm["tools"])
        self.assertIn("academic-catalog", fm["mcpServers"])
        self.assertTrue(fm["inheritCustomizations"])

        # Check constitutional body
        self.assertIn("Directive 0 (Binary Honesty & Anti-Deception)", content)
        self.assertIn("Directive 2 (Deterministic Calculations)", content)
        self.assertIn("Directive 4 (APA 7 & Persian Leading Zero Standard)", content)
        self.assertIn("Rule 1: Always verify parameters.", content)

    def test_02_all_22_target_agent_specs_validate_successfully(self):
        """All 22 target architecture specifications must be valid and conform to constraints."""
        specs = get_all_target_agent_specs()

        # Check counts: 7 durable, 15 subagents, total 22
        self.assertEqual(len(specs), 22)
        for d_name in TARGET_DURABLE_AGENTS:
            self.assertIn(d_name, specs)
        for s_name in TARGET_SUBAGENTS:
            self.assertIn(s_name, specs)

        # Ensure academic-challenger exists
        self.assertIn("academic-challenger", specs)
        challenger = specs["academic-challenger"]
        self.assertEqual(challenger.role, "Adversarial Methodology, Bias & Statistical Challenger")
        self.assertNotIn("run_command", challenger.tools)  # Read-only critic

        # Validate every spec against the full registry
        for name, spec in specs.items():
            try:
                validate_agent_spec(spec, existing_agents=specs, allow_name_collision=True)
            except AgentValidationError as e:
                self.fail(f"Validation failed for target agent '{name}': {str(e)}")

    def test_03_unique_name_validation(self):
        """Factory must reject invalid or duplicate agent names."""
        # Invalid format: uppercase
        with self.assertRaises(AgentValidationError) as ctx:
            validate_agent_spec(AgentSpec(name="InvalidName", role="Test Role", description="Desc"))
        self.assertIn("Invalid agent name", str(ctx.exception))

        # Invalid format: spaces
        with self.assertRaises(AgentValidationError) as ctx:
            validate_agent_spec(AgentSpec(name="invalid name", role="Test Role", description="Desc"))
        self.assertIn("Invalid agent name", str(ctx.exception))

        # Empty name
        with self.assertRaises(AgentValidationError):
            validate_agent_spec(AgentSpec(name="", role="Test Role", description="Desc"))

        # Collision check
        registry = {"existing-agent": AgentSpec(name="existing-agent", role="Role", description="Desc")}
        with self.assertRaises(AgentValidationError) as ctx:
            validate_agent_spec(
                AgentSpec(name="existing-agent", role="Role", description="Desc"),
                existing_agents=registry,
                allow_name_collision=False,
            )
        self.assertIn("already exists", str(ctx.exception))

    def test_04_valid_role_validation(self):
        """Factory must reject empty or out-of-bounds role strings."""
        with self.assertRaises(AgentValidationError) as ctx:
            validate_agent_spec(AgentSpec(name="test-agent", role="", description="Desc"))
        self.assertIn("Agent role must be a non-empty", str(ctx.exception))

        with self.assertRaises(AgentValidationError) as ctx:
            validate_agent_spec(AgentSpec(name="test-agent", role="x", description="Desc"))
        self.assertIn("Agent role length", str(ctx.exception))

    def test_05_mainagent_subagent_consistency(self):
        """Factory must reject inconsistent mainAgent and subagent combinations."""
        # Both False: An agent cannot be neither
        with self.assertRaises(AgentValidationError) as ctx:
            validate_agent_spec(
                AgentSpec(name="test-agent", role="Valid Role", description="Desc", mainAgent=False, subagent=False)
            )
        self.assertIn("mainAgent/subagent consistency failure", str(ctx.exception))

    def test_06_valid_model_validation(self):
        """Factory must enforce valid Antigravity model tiers."""
        valid_models = ["flash", "flash_lite", "pro", "inherit"]
        for m in valid_models:
            spec = AgentSpec(name="test-agent", role="Valid Role", description="Desc", model=m)
            validate_agent_spec(spec)

        with self.assertRaises(AgentValidationError) as ctx:
            validate_agent_spec(AgentSpec(name="test-agent", role="Valid Role", description="Desc", model="gpt-4"))
        self.assertIn("Invalid model 'gpt-4'", str(ctx.exception))

    def test_07_rejection_of_unsupported_frontmatter_policies(self):
        """Factory must reject commandExecutionPolicy and command_execution_policy in frontmatter to protect IDE agent discovery."""
        # Rejection of unsupported commandExecutionPolicy in from_dict
        with self.assertRaises(AgentValidationError) as ctx:
            AgentSpec.from_dict({
                "name": "test-agent",
                "role": "Role",
                "description": "Desc",
                "commandExecutionPolicy": "request-review",
            })
        self.assertIn("Unsupported field", str(ctx.exception))

        # Rejection of deprecated command_execution_policy in from_dict
        with self.assertRaises(AgentValidationError) as ctx:
            AgentSpec.from_dict({
                "name": "test-agent",
                "role": "Role",
                "description": "Desc",
                "command_execution_policy": "request-review",
            })
        self.assertIn("Unsupported field", str(ctx.exception))

        # Rejection of unsupported commandExecutionPolicy in create_agent
        with self.assertRaises(AgentValidationError) as ctx:
            create_agent(
                name="test-agent",
                role="Role",
                description="Desc",
                commandExecutionPolicy="request-review",
                target_dir=self.temp_dir,
            )
        self.assertIn("Unsupported field", str(ctx.exception))

        # Rejection of deprecated command_execution_policy keyword in create_agent
        with self.assertRaises(AgentValidationError) as ctx:
            create_agent(
                name="test-agent",
                role="Role",
                description="Desc",
                command_execution_policy="request-review",
                target_dir=self.temp_dir,
            )
        self.assertIn("Unsupported field", str(ctx.exception))

    def test_08_valid_tools_and_worker_privilege_isolation(self):
        """Factory must validate tools and prevent worker subagents from orchestrating."""
        # Unknown tool
        with self.assertRaises(AgentValidationError) as ctx:
            validate_agent_spec(
                AgentSpec(name="test-agent", role="Role", description="Desc", tools=["non_existent_tool"])
            )
        self.assertIn("Invalid tool 'non_existent_tool'", str(ctx.exception))

        # Worker subagent attempting to declare invoke_subagent
        with self.assertRaises(AgentValidationError) as ctx:
            validate_agent_spec(
                AgentSpec(
                    name="worker-subagent",
                    role="Worker Subagent",
                    description="Desc",
                    mainAgent=False,
                    subagent=True,
                    tools=["view_file", "invoke_subagent"],
                )
            )
        self.assertIn("Unauthorized delegation tool 'invoke_subagent'", str(ctx.exception))

        # Pure critic attempting to declare mutating run_command tool
        with self.assertRaises(AgentValidationError) as ctx:
            validate_agent_spec(
                AgentSpec(
                    name="academic-challenger",
                    role="Adversarial Challenger",
                    description="Desc",
                    mainAgent=False,
                    subagent=True,
                    tools=["view_file", "run_command"],
                    skills=["thesis-integrity-auditor", "methodology-review"],
                )
            )
        self.assertIn("Unauthorized tool 'run_command' for critic role", str(ctx.exception))

    def test_09_valid_skills_validation(self):
        """Factory must validate skills against workspace directory and built-ins."""
        # Valid skill from repository
        spec = AgentSpec(name="test-agent", role="Role", description="Desc", skills=["mediation", "sem"])
        validate_agent_spec(spec)

        # Fabricated/unknown skill
        with self.assertRaises(AgentValidationError) as ctx:
            validate_agent_spec(
                AgentSpec(name="test-agent", role="Role", description="Desc", skills=["fabricated-skill-xyz"])
            )
        self.assertIn("Unknown skill 'fabricated-skill-xyz'", str(ctx.exception))

    def test_10_valid_agent_dependencies_and_self_dependency(self):
        """Factory must validate agent dependencies and forbid self-dependency."""
        # Self-dependency
        with self.assertRaises(AgentValidationError) as ctx:
            validate_agent_spec(
                AgentSpec(
                    name="methodology-expert",
                    role="Methodology Expert",
                    description="Desc",
                    mainAgent=False,
                    subagent=True,
                    agents=["methodology-expert"],
                )
            )
        self.assertIn("Self-dependency detected", str(ctx.exception))

        # Unknown agent dependency
        with self.assertRaises(AgentValidationError) as ctx:
            validate_agent_spec(
                AgentSpec(
                    name="methodology-expert",
                    role="Methodology Expert",
                    description="Desc",
                    mainAgent=False,
                    subagent=True,
                    agents=["unknown-ghost-agent"],
                )
            )
        self.assertIn("Unknown agent dependency 'unknown-ghost-agent'", str(ctx.exception))

    def test_11_valid_mcp_references(self):
        """Factory must validate MCP server identifiers."""
        # Valid MCP
        spec = AgentSpec(name="test-agent", role="Role", description="Desc", mcpServers=["catalog-server_v1"])
        validate_agent_spec(spec)

        # Invalid MCP with spaces
        with self.assertRaises(AgentValidationError) as ctx:
            validate_agent_spec(
                AgentSpec(name="test-agent", role="Role", description="Desc", mcpServers=["invalid mcp server!"])
            )
        self.assertIn("Invalid MCP server reference", str(ctx.exception))

    def test_12_worker_to_worker_dependency_rejection(self):
        """Worker subagents must not declare dependencies on other subagents."""
        with self.assertRaises(AgentValidationError) as ctx:
            validate_agent_spec(
                AgentSpec(
                    name="data-agent",
                    role="Data Agent",
                    description="Desc",
                    mainAgent=False,
                    subagent=True,
                    agents=["statistics-agent"],
                )
            )
        self.assertIn("Unauthorized worker-to-worker dependency", str(ctx.exception))

    def test_13_circular_dependency_rejection(self):
        """Factory must detect and reject circular dependency graphs."""
        registry = {
            "lead-a": AgentSpec(name="lead-a", role="Lead A", description="Desc", agents=["lead-b"]),
            "lead-b": AgentSpec(name="lead-b", role="Lead B", description="Desc", agents=["lead-a"]),
        }

        # DFS check directly
        graph = {"lead-a": ["lead-b"], "lead-b": ["lead-a"]}
        cycle = check_circular_dependencies(graph)
        self.assertIsNotNone(cycle)
        self.assertIn("lead-a", cycle)
        self.assertIn("lead-b", cycle)

        # In validate_agent_spec with authorized durable leads
        existing = {
            "lead-a": AgentSpec(name="lead-a", role="Lead A", description="Desc", mainAgent=True, subagent=False, agents=["lead-b"])
        }
        spec_c = AgentSpec(name="lead-b", role="Lead B", description="Desc", mainAgent=True, subagent=False, agents=["lead-a"])
        with self.assertRaises(AgentValidationError) as ctx:
            validate_agent_spec(spec_c, existing_agents=existing, allow_name_collision=True)
        self.assertIn("Circular dependency detected", str(ctx.exception))

    def test_14_excessive_dependency_depth_rejection(self):
        """Factory must detect and reject dependency chains with depth > 3."""
        # Graph with depth 4: root -> tier1 -> tier2 -> tier3
        deep_graph = {
            "root": ["tier1"],
            "tier1": ["tier2"],
            "tier2": ["tier3"],
            "tier3": [],
        }
        depth, path = calculate_max_depth(deep_graph, "root")
        self.assertEqual(depth, 4)

        # When creating an agent that pushes depth to 4
        existing = {
            "root": AgentSpec(name="root", role="Root", description="Desc", mainAgent=True, agents=["tier1"]),
            "tier1": AgentSpec(name="tier1", role="Tier 1", description="Desc", agents=["tier2"]),
            "tier2": AgentSpec(name="tier2", role="Tier 2", description="Desc", agents=["tier3"]),
            "tier3": AgentSpec(name="tier3", role="Tier 3", description="Desc", agents=[]),
        }
        spec_root = AgentSpec(name="root", role="Root", description="Desc", mainAgent=True, agents=["tier1"])
        with self.assertRaises(AgentValidationError) as ctx:
            validate_agent_spec(spec_root, existing_agents=existing, allow_name_collision=True, max_dependency_depth=3)
        self.assertIn("Excessive dependency depth", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
