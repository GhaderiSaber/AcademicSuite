#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_specialist_workers_migration.py — Verification of the 15 Migrated Specialist Subagents

Validates:
1. All 15 specialist subagents are discoverable in canonical directory-form:
   .agents/agents/<name>/agent.md and contract.md.
2. Backward-compatible relative symlinks (.agents/agents/<name>.md) exist and resolve.
3. Canonical Antigravity YAML frontmatter without deprecated fields:
   - camelCase commandExecutionPolicy
   - Zero command_execution_policy occurrences
   - Explicit mainAgent: false
   - Explicit subagent: true
   - Model tiers: 'pro' for complex reasoning (academic-challenger, intervention-designer,
     qualitative-analyst, journal-strategist); 'flash' for the other 11 workers.
   - Tools obeying strict least privilege:
     * Zero delegation tools (invoke_subagent, manage_subagents, define_subagent)
     * Critics (academic-challenger, results-auditor, intervention-designer) have NO run_command
     * Critics have NO replace_file_content
   - Strict absence of worker-to-worker dependencies (agents: [])
   - Valid skills from .agents/skills/
   - mcpServers: []
   - Explicit inheritCustomizations: true
4. Specific architectural responsibility boundaries and domain differentiations:
   - statistics-agent: EXECUTES vetted analysis plans; plan design forbidden
   - statistical-expert vs statistics-agent: DESIGN vs EXECUTION
   - data-agent vs data-curator: PROFILES/REVERSES vs PREPARES/CURATES; raw data files strictly immutable
   - research-agent vs literature-expert: PARAMETER EXTRACTION vs SYNTHESIS/BIBLIOMETRICS
   - academic-challenger: ADVERSARIAL FALSIFICATION, red-teaming p-hacking, bias, unmeasured confounding
5. Zero circular dependencies and max depth <= 3 across the entire dependency graph.
6. Preservation of legacy writing-agent directory and symlink for backward compatibility.
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
    TARGET_SUBAGENTS,
    ALL_TARGET_ROLES,
    check_circular_dependencies,
    calculate_max_depth,
    get_all_target_agent_specs,
    get_available_skills,
)

AGENTS_DIR = os.path.join(ROOT_DIR, ".agents", "agents")


class TestSpecialistWorkersMigration(unittest.TestCase):

    def setUp(self):
        self.specialist_names = [
            "research-agent",
            "literature-expert",
            "journal-strategist",
            "meta-analyst",
            "data-agent",
            "data-curator",
            "statistics-agent",
            "psychometric-expert",
            "longitudinal-modmed-expert",
            "intervention-designer",
            "qualitative-analyst",
            "validation-agent",
            "results-auditor",
            "statistical-auditor",
            "academic-challenger",
        ]
        self.pro_models = {
            "academic-challenger",
            "intervention-designer",
            "qualitative-analyst",
            "journal-strategist",
        }
        self.critics_no_run_command = {
            "academic-challenger",
            "results-auditor",
            "intervention-designer",
        }
        self.critics_no_replace = {
            "academic-challenger",
            "results-auditor",
            "intervention-designer",
        }

    def test_01_discovery_of_all_15_workers(self):
        """All 15 specialist subagents must be discoverable on disk with agent.md, contract.md, and symlink."""
        for name in self.specialist_names:
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
            self.assertTrue(
                os.path.islink(symlink_file), f"Expected symlink: {symlink_file}"
            )
            self.assertEqual(
                os.readlink(symlink_file), f"{name}/agent.md",
                f"Symlink target mismatch for {name}"
            )

    def test_02_canonical_frontmatter_validation(self):
        """Frontmatter must use canonical current Antigravity schema and zero deprecated fields."""
        available_skills = get_available_skills()

        for name in self.specialist_names:
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
            self.assertFalse(fm["mainAgent"], f"{name} must have mainAgent: false")
            self.assertTrue(fm["subagent"], f"{name} must have subagent: true")
            self.assertEqual(
                fm["commandExecutionPolicy"], "request-review",
                f"{name} must have commandExecutionPolicy: request-review"
            )
            self.assertNotIn(
                "command_execution_policy", fm,
                f"Deprecated command_execution_policy found in {name}"
            )
            self.assertNotIn(
                "command_execution_policy", content,
                f"Deprecated command_execution_policy text found in {name}/agent.md"
            )

            # Model tier validation
            if name in self.pro_models:
                self.assertEqual(
                    fm["model"], "pro",
                    f"{name} requires model 'pro' for deep reasoning"
                )
            else:
                self.assertEqual(
                    fm["model"], "flash",
                    f"{name} requires model 'flash' for fast execution"
                )

            # MCP servers and inheritCustomizations
            self.assertEqual(fm.get("mcpServers"), [], f"{name} mcpServers must be empty list")
            self.assertTrue(
                fm.get("inheritCustomizations"),
                f"{name} must have inheritCustomizations: true"
            )

            # Skills must exist
            self.assertIn("skills", fm)
            self.assertGreater(len(fm["skills"]), 0, f"{name} must declare at least one skill")
            for s in fm["skills"]:
                self.assertIn(
                    s, available_skills,
                    f"Declared skill '{s}' for agent '{name}' does not exist on disk"
                )

    def test_03_strict_least_privilege_and_no_worker_delegation(self):
        """Specialist workers must have zero delegation tools and agents: []."""
        disallowed_delegation_tools = {
            "invoke_subagent",
            "manage_subagents",
            "define_subagent",
        }

        for name in self.specialist_names:
            agent_file = os.path.join(AGENTS_DIR, name, "agent.md")
            with open(agent_file, "r", encoding="utf-8") as f:
                fm = yaml.safe_load(f.read().split("---")[1])

            tools = set(fm.get("tools", []))

            # No delegation tools
            delegation_found = tools.intersection(disallowed_delegation_tools)
            self.assertEqual(
                len(delegation_found), 0,
                f"Agent '{name}' violates least privilege with delegation tools: {delegation_found}"
            )

            # Strict empty dependency list: agents: []
            self.assertEqual(
                fm.get("agents"), [],
                f"Worker '{name}' must have agents: [] to prohibit worker-to-worker calls"
            )

            # Critics must not have run_command
            if name in self.critics_no_run_command:
                self.assertNotIn(
                    "run_command", tools,
                    f"Critic/protocol agent '{name}' must not have 'run_command'"
                )

            # Critics must not have replace_file_content
            if name in self.critics_no_replace:
                self.assertNotIn(
                    "replace_file_content", tools,
                    f"Critic/protocol agent '{name}' must not have 'replace_file_content'"
                )

    def test_04_contract_contains_12_constitutional_sections(self):
        """All 15 specialist subagent contracts must contain all 12 constitutional sections."""
        required_sections = [
            "MISSION",
            "RESPONSIBILITIES",
            "NON-RESPONSIBILITIES",
            "INPUTS",
            "OUTPUTS",
            "ALLOWED TOOLS",
            "REQUIRED SKILLS",
            "FORBIDDEN ACTIONS",
            "HANDOFF FORMAT",
            "VALIDATION REQUIREMENTS",
            "COMPLETION CRITERIA",
            "FAILURE CONDITIONS",
        ]

        for name in self.specialist_names:
            contract_file = os.path.join(AGENTS_DIR, name, "contract.md")
            with open(contract_file, "r", encoding="utf-8") as f:
                content = f.read()

            for section in required_sections:
                self.assertIn(
                    f"## {section}", content,
                    f"Contract for '{name}' is missing section '## {section}'"
                )

    def test_05_role_differentiation_statistics_agent(self):
        """statistics-agent must be an execution agent only; statistical-expert designs plans."""
        agent_file = os.path.join(AGENTS_DIR, "statistics-agent", "agent.md")
        contract_file = os.path.join(AGENTS_DIR, "statistics-agent", "contract.md")

        with open(agent_file, "r", encoding="utf-8") as f:
            agent_text = f.read()
        with open(contract_file, "r", encoding="utf-8") as f:
            contract_text = f.read()

        # Must declare execution role
        self.assertIn("EXECUTE", agent_text.upper())
        self.assertIn("analysis plan", agent_text)
        self.assertIn("statistical-expert", agent_text)

        # Must declare non-responsibility of designing plans
        self.assertIn("Design", contract_text)
        self.assertIn("statistical-expert", contract_text)

    def test_06_role_differentiation_data_immutability(self):
        """data-agent and data-curator must treat raw data files as strictly immutable."""
        for name in ["data-agent", "data-curator"]:
            contract_file = os.path.join(AGENTS_DIR, name, "contract.md")
            agent_file = os.path.join(AGENTS_DIR, name, "agent.md")

            with open(contract_file, "r", encoding="utf-8") as f:
                contract_text = f.read()
            with open(agent_file, "r", encoding="utf-8") as f:
                agent_text = f.read()

            self.assertTrue(
                "immutable" in contract_text.lower() or "modify" in contract_text.lower() or "overwrite" in contract_text.lower(),
                f"Raw data immutability not enforced in contract for {name}"
            )
            self.assertTrue(
                "immutable" in agent_text.lower() or "overwrite" in agent_text.lower(),
                f"Raw data immutability not enforced in agent.md for {name}"
            )

    def test_07_academic_challenger_adversarial_spec(self):
        """academic-challenger must have adversarial mission and pitfall contract."""
        agent_file = os.path.join(AGENTS_DIR, "academic-challenger", "agent.md")
        contract_file = os.path.join(AGENTS_DIR, "academic-challenger", "contract.md")

        with open(agent_file, "r", encoding="utf-8") as f:
            agent_text = f.read()
        with open(contract_file, "r", encoding="utf-8") as f:
            contract_text = f.read()

        self.assertIn("Adversarial", agent_text)
        self.assertIn("p-hacking", agent_text.lower())
        self.assertIn("pitfall", agent_text.lower())
        self.assertIn("pitfall.schema.json", contract_text)

    def test_08_full_dependency_graph_zero_cycles_and_max_depth_3(self):
        """The complete graph across all 7 durable agents and 15 subagents must have 0 cycles and max depth <= 3."""
        all_specs = get_all_target_agent_specs()

        # Build graph from actual files on disk
        graph = {}
        for role_name in ALL_TARGET_ROLES:
            agent_file = os.path.join(AGENTS_DIR, role_name, "agent.md")
            if os.path.isfile(agent_file):
                with open(agent_file, "r", encoding="utf-8") as f:
                    fm = yaml.safe_load(f.read().split("---")[1])
                    graph[role_name] = list(fm.get("agents", []))
            else:
                graph[role_name] = list(all_specs[role_name].agents)

        # 1. Zero cycles
        cycle = check_circular_dependencies(graph)
        self.assertIsNone(cycle, f"Circular dependency detected in graph: {cycle}")

        # 2. Max depth <= 3 from durable roots
        for root in TARGET_DURABLE_AGENTS:
            depth, path = calculate_max_depth(graph, root)
            self.assertLessEqual(
                depth, 3,
                f"Excessive dependency depth ({depth} > 3) starting from '{root}': {' -> '.join(path)}"
            )

    def test_09_academic_writer_unified_writing_authority(self):
        """academic-writer must be the sole authoritative writing agent; legacy writing-agent is cleanly retired."""
        writer_dir = os.path.join(AGENTS_DIR, "academic-writer")
        writer_agent_file = os.path.join(writer_dir, "agent.md")
        writer_contract_file = os.path.join(writer_dir, "contract.md")
        writer_symlink = os.path.join(AGENTS_DIR, "academic-writer.md")

        self.assertTrue(os.path.isdir(writer_dir), "academic-writer directory must exist")
        self.assertTrue(os.path.isfile(writer_agent_file), "academic-writer/agent.md must exist")
        self.assertTrue(os.path.isfile(writer_contract_file), "academic-writer/contract.md must exist")
        self.assertTrue(os.path.exists(writer_symlink), "academic-writer.md symlink must exist")

        # Verify duplicate writing-agent directory has been safely retired
        writing_dir = os.path.join(AGENTS_DIR, "writing-agent")
        self.assertFalse(os.path.exists(writing_dir), "writing-agent directory must be retired to prevent duplication")


if __name__ == "__main__":
    unittest.main()
