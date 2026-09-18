#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_durable_agents_migration.py — Verification of the 7 Migrated Durable Agents

Validates:
1. All 7 durable agents are discoverable in canonical directory-form:
   .agents/agents/<name>/agent.md and contract.md.
2. Backward-compatible symlinks (.agents/agents/<name>.md) exist and resolve.
3. Canonical Antigravity YAML frontmatter without deprecated fields:
   - camelCase commandExecutionPolicy
   - Zero command_execution_policy occurrences
   - Explicit mainAgent / subagent booleans
   - Model tier 'pro'
   - Whitelisted tools obeying least privilege
   - Allowed subagent dependencies
   - Explicit inheritCustomizations: true
4. Specific architectural responsibility boundaries and tool constraints:
   - digital-saber: user-facing consultant only; orchestrator bypass forbidden
   - academic-orchestrator: workflow coordination and milestone management
   - methodology-expert: research design and methodological reasoning
   - statistical-expert: statistical method selection; arbitrary code execution forbidden
   - academic-writer: writing from approved artifacts; statistical invention forbidden
   - evidence-auditor: integrity verification; ghost citations forbidden
   - final-judge: independent acceptance; silent artifact rewriting forbidden (no replace_file_content)
5. Zero circular dependencies and max depth <= 3 across the entire dependency graph.
"""

import os
import sys
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
    TARGET_DURABLE_AGENTS,
    ALL_TARGET_ROLES,
    check_circular_dependencies,
    calculate_max_depth,
)

AGENTS_DIR = os.path.join(ROOT_DIR, ".agents", "agents")


class TestDurableAgentsMigration(unittest.TestCase):

    def setUp(self):
        self.durable_names = [
            "digital-saber",
            "academic-orchestrator",
            "methodology-expert",
            "statistical-expert",
            "academic-writer",
            "evidence-auditor",
            "final-judge",
        ]

    def test_01_discovery_of_canonical_directory_and_files(self):
        """All 7 durable agents must be discoverable on disk with agent.md and contract.md."""
        for name in self.durable_names:
            agent_dir = os.path.join(AGENTS_DIR, name)
            agent_file = os.path.join(agent_dir, "agent.md")
            contract_file = os.path.join(agent_dir, "contract.md")
            symlink_file = os.path.join(AGENTS_DIR, f"{name}.md")

            self.assertTrue(os.path.isdir(agent_dir), f"Directory missing: {agent_dir}")
            self.assertTrue(os.path.isfile(agent_file), f"agent.md missing: {agent_file}")
            self.assertTrue(os.path.isfile(contract_file), f"contract.md missing: {contract_file}")
            self.assertTrue(
                os.path.exists(symlink_file), f"Backward-compatible symlink missing: {symlink_file}"
            )

    def test_02_canonical_frontmatter_validation(self):
        """Frontmatter must use canonical current Antigravity schema and zero deprecated fields."""
        for name in self.durable_names:
            agent_file = os.path.join(AGENTS_DIR, name, "agent.md")
            with open(agent_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Frontmatter separation
            parts = content.split("---")
            self.assertGreaterEqual(len(parts), 3, f"Invalid YAML frontmatter framing in {name}")
            fm_text = parts[1]
            fm = yaml.safe_load(fm_text)

            # Assert required canonical keys
            self.assertEqual(fm["name"], name)
            self.assertIn("description", fm)
            self.assertIn("role", fm)
            self.assertEqual(fm["model"], "pro")
            self.assertEqual(fm["commandExecutionPolicy"], "request-review")
            self.assertIsInstance(fm["mainAgent"], bool)
            self.assertIsInstance(fm["subagent"], bool)
            self.assertIsInstance(fm["tools"], list)
            self.assertIsInstance(fm["skills"], list)
            self.assertIsInstance(fm["agents"], list)
            self.assertTrue(fm["inheritCustomizations"])

            # Zero deprecated field occurrences
            self.assertNotIn("command_execution_policy", fm)
            self.assertNotIn("command_execution_policy", content)

    def test_03_mainagent_and_subagent_assignments(self):
        """All 7 Durable Authorities must have mainAgent=True and subagent=False for IDE Main Agent visibility."""
        for name in self.durable_names:
            agent_file = os.path.join(AGENTS_DIR, name, "agent.md")
            with open(agent_file, "r", encoding="utf-8") as f:
                fm = yaml.safe_load(f.read().split("---")[1])

            self.assertTrue(fm["mainAgent"], f"{name} should be mainAgent=True")
            self.assertFalse(fm["subagent"], f"{name} should be subagent=False")

    def test_04_least_privilege_and_silent_rewrite_prevention(self):
        """final-judge must NOT have replace_file_content tool to prevent silent rewriting."""
        judge_file = os.path.join(AGENTS_DIR, "final-judge", "agent.md")
        with open(judge_file, "r", encoding="utf-8") as f:
            fm = yaml.safe_load(f.read().split("---")[1])

        self.assertNotIn(
            "replace_file_content",
            fm["tools"],
            "final-judge must NOT have replace_file_content tool (silent rewriting forbidden).",
        )

    def test_05_responsibility_boundaries_in_narrative_and_contract(self):
        """All 7 agents must explicitly document their CAN/CANNOT boundaries in contract and prompt."""
        expected_boundaries = {
            "digital-saber": "Never bypass academic-orchestrator",
            "academic-orchestrator": "Never calculate statistical formulas",
            "methodology-expert": "Never fabricate sampling rationale",
            "statistical-expert": "Never silently execute arbitrary",
            "academic-writer": "Never invent missing statistics",
            "evidence-auditor": "Never approve manuscripts containing unverified or ghost citations",
            "final-judge": "Never silently rewrite candidate artifacts",
        }

        for name, phrase in expected_boundaries.items():
            agent_file = os.path.join(AGENTS_DIR, name, "agent.md")
            contract_file = os.path.join(AGENTS_DIR, name, "contract.md")

            with open(agent_file, "r", encoding="utf-8") as f:
                agent_text = f.read()
            with open(contract_file, "r", encoding="utf-8") as f:
                contract_text = f.read()

            self.assertIn(phrase, agent_text, f"Boundary phrase missing from {name}/agent.md")
            self.assertIn("## RESPONSIBILITIES", contract_text, f"Contract missing responsibilities for {name}")
            self.assertIn("## NON-RESPONSIBILITIES", contract_text, f"Contract missing non-responsibilities for {name}")
            self.assertIn("### CAN:", contract_text)
            self.assertIn("### CANNOT:", contract_text)

    def test_06_dependency_graph_acyclic_and_depth_bounded(self):
        """The dependency graph of the 7 durable agents must have 0 cycles and max depth <= 3."""
        graph = {}
        for name in self.durable_names:
            agent_file = os.path.join(AGENTS_DIR, name, "agent.md")
            with open(agent_file, "r", encoding="utf-8") as f:
                fm = yaml.safe_load(f.read().split("---")[1])
            graph[name] = fm.get("agents", [])

        # Ensure all declared dependencies exist in ALL_TARGET_ROLES
        for name, deps in graph.items():
            for d in deps:
                self.assertIn(d, ALL_TARGET_ROLES, f"Unknown dependency '{d}' in {name}")

        # Check 0 cycles
        cycle = check_circular_dependencies(graph)
        self.assertIsNone(cycle, f"Circular dependency detected: {cycle}")

        # Check depth from all roots
        roots = ["digital-saber", "academic-orchestrator"]
        for r in roots:
            depth, path = calculate_max_depth(graph, r)
            self.assertLessEqual(
                depth, 3, f"Excessive depth from root {r}: {depth} > 3 (Path: {' -> '.join(path)})"
            )


if __name__ == "__main__":
    unittest.main()
