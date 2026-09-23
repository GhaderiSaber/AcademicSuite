#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_agent_discovery.py — Antigravity Agent Discovery & Compatibility Acceptance Suite

Tests the Phase 1 Antigravity Compatibility Boundary:
1. Agent Discovery: All 28 workspace agents are discoverable by Antigravity conventions.
2. Minimal Contract: Minimal frontmatter (only name + description) is fully valid.
3. Progressive Enhancement: Additional valid fields (tools, skills, agents, model) load cleanly.
4. Policy Sanitization: Rejects commandExecutionPolicy and command_execution_policy in frontmatter.
5. Tool Whitelist: Catches misspelled or unsupported tool names.
6. Skill Resolution: Catches missing or invalid skill references.
7. Subagent Invocation Readiness: Guarantees every delegatable agent has subagent: true.
8. Circular Delegation: Verifies detection of cycles in delegation graphs.
9. Full Workspace Integrity: Runs AgentIntegrityValidator across all 28 workspace agents with 0 errors.
"""

import os
import sys
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from validators.agent_integrity import (
    AgentIntegrityValidator,
    CANONICAL_ANTIGRAVITY_TOOLS,
    parse_yaml_frontmatter,
    detect_cycles_in_delegation,
)

AGENTS_DIR = os.path.join(ROOT_DIR, ".agents", "agents")

EXPECTED_AGENTS = [
    # Tier 1: Orchestrators & Digital Twin
    "digital-saber",
    "academic-orchestrator",
    # Tier 2: Domain Authorities
    "methodology-expert",
    "statistical-expert",
    "academic-writer",
    "evidence-auditor",
    "final-judge",
    # Tier 3: Execution Specialists
    "data-agent",
    "data-curator",
    "project-organizer",
    "statistics-agent",
    "psychometric-expert",
    "research-agent",
    "literature-expert",
    "intervention-designer",
    "qualitative-analyst",
    # Tier 4: Adversarial Reviewers & Critics
    "validation-agent",
    "statistical-auditor",
    "results-auditor",
    "academic-challenger",
    "journal-strategist",
    "meta-analyst",
    "longitudinal-modmed-expert",
    # Tier 5: Autonomous Learning Subagents
    "behavior-analyst",
    "curriculum-builder",
    "evaluation-agent",
    "knowledge-curator",
    "skill-evolver",
    "trajectory-analyzer",
    # Tier 6: Proof-of-Concept & Test Verification Agents (Phase 29)
    "test-orchestrator",
    "test-worker",
]


class TestAgentDiscoveryAndCompatibility(unittest.TestCase):
    """Verifies Antigravity agent discovery, minimal contracts, and execution readiness."""

    def test_01_all_expected_agents_exist_and_discoverable(self):
        """Every expected agent must exist in directory form and have a valid agent.md."""
        self.assertTrue(os.path.isdir(AGENTS_DIR), f"Missing agents directory: {AGENTS_DIR}")
        for agent_name in EXPECTED_AGENTS:
            agent_dir = os.path.join(AGENTS_DIR, agent_name)
            agent_file = os.path.join(agent_dir, "agent.md")
            self.assertTrue(os.path.isdir(agent_dir), f"Missing directory for agent: {agent_name}")
            self.assertTrue(os.path.isfile(agent_file), f"Missing agent.md for: {agent_name}")
            self.assertGreater(os.path.getsize(agent_file), 50, f"agent.md too small for: {agent_name}")

    def test_02_minimal_agent_contract(self):
        """Minimal agent containing only name and description must pass validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_agents = os.path.join(tmpdir, "agents")
            tmp_skills = os.path.join(tmpdir, "skills")
            os.makedirs(os.path.join(tmp_agents, "minimal-worker"), exist_ok=True)
            os.makedirs(tmp_skills, exist_ok=True)

            minimal_content = (
                "---\n"
                "name: minimal-worker\n"
                "description: A minimal test subagent that performs basic file reading.\n"
                "---\n\n"
                "# Minimal Worker\n"
                "Instructions go here.\n"
            )
            with open(os.path.join(tmp_agents, "minimal-worker", "agent.md"), "w") as f:
                f.write(minimal_content)

            validator = AgentIntegrityValidator(agents_dir=tmp_agents, skills_dir=tmp_skills)
            res = validator.run_validation()
            self.assertEqual(res["overall_verdict"], "PASS")
            self.assertEqual(res["errors"], 0)
            self.assertIn("minimal-worker", res["canonical_agents"])

    def test_03_progressive_enhancement_contract(self):
        """Agent with progressively added native capabilities (tools, model, subagent) must pass."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_agents = os.path.join(tmpdir, "agents")
            tmp_skills = os.path.join(tmpdir, "skills")
            os.makedirs(os.path.join(tmp_agents, "advanced-worker"), exist_ok=True)
            os.makedirs(os.path.join(tmp_skills, "test-skill"), exist_ok=True)
            with open(os.path.join(tmp_skills, "test-skill", "SKILL.md"), "w") as f:
                f.write("---\nname: test-skill\ndescription: Test skill\n---\n")

            content = (
                "---\n"
                "name: advanced-worker\n"
                "description: Advanced test worker with progressive capabilities.\n"
                "role: Test Execution Specialist\n"
                "model: pro\n"
                "mainAgent: false\n"
                "subagent: true\n"
                "tools:\n"
                "  - view_file\n"
                "  - write_to_file\n"
                "skills:\n"
                "  - test-skill\n"
                "---\n\n"
                "# Advanced Worker\n"
            )
            with open(os.path.join(tmp_agents, "advanced-worker", "agent.md"), "w") as f:
                f.write(content)

            validator = AgentIntegrityValidator(agents_dir=tmp_agents, skills_dir=tmp_skills)
            res = validator.run_validation()
            self.assertEqual(res["overall_verdict"], "PASS")
            self.assertEqual(res["errors"], 0)

    def test_04_rejection_of_command_execution_policy(self):
        """Frontmatter containing commandExecutionPolicy must fail integrity validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_agents = os.path.join(tmpdir, "agents")
            os.makedirs(os.path.join(tmp_agents, "bad-policy-agent"), exist_ok=True)

            bad_content = (
                "---\n"
                "name: bad-policy-agent\n"
                "description: Agent incorrectly attempting to declare commandExecutionPolicy.\n"
                "commandExecutionPolicy: request-review\n"
                "---\n"
            )
            with open(os.path.join(tmp_agents, "bad-policy-agent", "agent.md"), "w") as f:
                f.write(bad_content)

            validator = AgentIntegrityValidator(agents_dir=tmp_agents, skills_dir=tmpdir)
            res = validator.run_validation()
            self.assertEqual(res["overall_verdict"], "FAIL")
            self.assertTrue(any(i["check"] == "no_unsupported_policies" for i in res["issues"]))

    def test_05_invalid_tool_name_fails_closed(self):
        """Invalid or misspelled tool name must be caught immediately."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_agents = os.path.join(tmpdir, "agents")
            os.makedirs(os.path.join(tmp_agents, "typo-tool-agent"), exist_ok=True)

            content = (
                "---\n"
                "name: typo-tool-agent\n"
                "description: Agent with misspelled tool name.\n"
                "tools:\n"
                "  - view_files_misspelled\n"
                "---\n"
            )
            with open(os.path.join(tmp_agents, "typo-tool-agent", "agent.md"), "w") as f:
                f.write(content)

            validator = AgentIntegrityValidator(agents_dir=tmp_agents, skills_dir=tmpdir)
            res = validator.run_validation()
            self.assertEqual(res["overall_verdict"], "FAIL")
            self.assertTrue(any(i["check"] == "valid_tool_names" for i in res["issues"]))

    def test_06_invalid_skill_reference_fails_closed(self):
        """Nonexistent skill reference must trigger validation failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_agents = os.path.join(tmpdir, "agents")
            tmp_skills = os.path.join(tmpdir, "skills")
            os.makedirs(os.path.join(tmp_agents, "missing-skill-agent"), exist_ok=True)
            os.makedirs(tmp_skills, exist_ok=True)

            content = (
                "---\n"
                "name: missing-skill-agent\n"
                "description: Agent referencing non-existent skill.\n"
                "skills:\n"
                "  - non-existent-skill-xyz\n"
                "---\n"
            )
            with open(os.path.join(tmp_agents, "missing-skill-agent", "agent.md"), "w") as f:
                f.write(content)

            validator = AgentIntegrityValidator(agents_dir=tmp_agents, skills_dir=tmp_skills)
            res = validator.run_validation()
            self.assertEqual(res["overall_verdict"], "FAIL")
            self.assertTrue(any(i["check"] == "valid_skill_references" for i in res["issues"]))

    def test_07_subagent_invocation_readiness(self):
        """Any agent delegated to in 'agents:' must have subagent: true."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_agents = os.path.join(tmpdir, "agents")
            os.makedirs(os.path.join(tmp_agents, "parent-lead"), exist_ok=True)
            os.makedirs(os.path.join(tmp_agents, "blocked-child"), exist_ok=True)

            parent = (
                "---\n"
                "name: parent-lead\n"
                "description: Orchestrator attempting to delegate.\n"
                "agents:\n"
                "  - blocked-child\n"
                "---\n"
            )
            child = (
                "---\n"
                "name: blocked-child\n"
                "description: Child that set subagent to false.\n"
                "subagent: false\n"
                "---\n"
            )
            with open(os.path.join(tmp_agents, "parent-lead", "agent.md"), "w") as f:
                f.write(parent)
            with open(os.path.join(tmp_agents, "blocked-child", "agent.md"), "w") as f:
                f.write(child)

            validator = AgentIntegrityValidator(agents_dir=tmp_agents, skills_dir=tmpdir)
            res = validator.run_validation()
            self.assertEqual(res["overall_verdict"], "FAIL")
            self.assertTrue(any(i["check"] == "correct_mainAgent_subagent_semantics" for i in res["issues"]))

    def test_08_circular_delegation_detection(self):
        """Cyclic delegation graphs must be detected and blocked."""
        cycle_graph = {
            "agent-a": ["agent-b"],
            "agent-b": ["agent-c"],
            "agent-c": ["agent-a"],
        }
        cycle = detect_cycles_in_delegation(cycle_graph)
        self.assertIsNotNone(cycle)
        self.assertIn("agent-a", cycle)

        acyclic_graph = {
            "orchestrator": ["authority-1", "authority-2"],
            "authority-1": ["worker-1"],
            "authority-2": ["worker-2"],
            "worker-1": [],
            "worker-2": [],
        }
        self.assertIsNone(detect_cycles_in_delegation(acyclic_graph))

    def test_09_workspace_agent_integrity_pass(self):
        """All workspace agents (29 production + 2 test verification) must pass 100% of integrity checks."""
        validator = AgentIntegrityValidator(agents_dir=AGENTS_DIR, skills_dir=os.path.join(ROOT_DIR, ".agents", "skills"))
        result = validator.run_validation()
        self.assertEqual(result["overall_verdict"], "PASS", f"Validation failed with issues: {result['issues']}")
        self.assertEqual(result["errors"], 0)
        self.assertEqual(result["agents_validated"], 31)
        self.assertEqual(set(result["canonical_agents"]), set(EXPECTED_AGENTS))


if __name__ == "__main__":
    unittest.main()
