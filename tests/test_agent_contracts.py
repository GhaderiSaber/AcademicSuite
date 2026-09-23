#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_agent_contracts.py — Unit Tests for Option 1 Subagent Packaging & Phase 4 Contracts

Validates:
1. All 22 subagents have a dedicated directory in .agents/agents/<role>/
2. Co-located agent.md runtime prompt exists.
3. Co-located contract.md exists and strictly contains all 12 constitutional sections from Phase 4.
4. Backward-compatible discovery symlink .agents/agents/<role>.md exists and points to <role>/agent.md.
"""

import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents", "agents")

REQUIRED_CONTRACT_SECTIONS = [
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
    "FAILURE CONDITIONS"
]

EXPECTED_ROLES = [
    "academic-challenger",
    "academic-orchestrator",
    "academic-writer",
    "data-agent",
    "data-curator",
    "digital-saber",
    "evidence-auditor",
    "final-judge",
    "intervention-designer",
    "journal-strategist",
    "literature-expert",
    "longitudinal-modmed-expert",
    "meta-analyst",
    "methodology-expert",
    "project-organizer",
    "psychometric-expert",
    "qualitative-analyst",
    "research-agent",
    "results-auditor",
    "statistical-auditor",
    "statistical-expert",
    "statistics-agent",
    "validation-agent"
]


class TestAgentContracts(unittest.TestCase):

    def test_01_all_expected_roles_exist_as_directories(self):
        self.assertTrue(os.path.isdir(AGENTS_DIR), f"Missing agents directory: {AGENTS_DIR}")
        for role in EXPECTED_ROLES:
            role_dir = os.path.join(AGENTS_DIR, role)
            self.assertTrue(os.path.isdir(role_dir), f"Missing subagent directory: {role_dir}")

    def test_02_all_subagents_have_colocated_agent_and_contract(self):
        for role in EXPECTED_ROLES:
            role_dir = os.path.join(AGENTS_DIR, role)
            agent_md = os.path.join(role_dir, "agent.md")
            contract_md = os.path.join(role_dir, "contract.md")
            
            self.assertTrue(os.path.isfile(agent_md), f"Missing agent.md for {role}: {agent_md}")
            self.assertTrue(os.path.isfile(contract_md), f"Missing contract.md for {role}: {contract_md}")
            self.assertGreater(os.path.getsize(agent_md), 100, f"agent.md too small for {role}")
            self.assertGreater(os.path.getsize(contract_md), 500, f"contract.md too small for {role}")

    def test_03_all_contracts_contain_12_constitutional_sections(self):
        for role in EXPECTED_ROLES:
            contract_md = os.path.join(AGENTS_DIR, role, "contract.md")
            with open(contract_md, "r", encoding="utf-8") as f:
                content = f.read()

            for section in REQUIRED_CONTRACT_SECTIONS:
                self.assertIn(
                    section,
                    content,
                    f"Subagent contract '{role}' is missing required Phase 4 section: '{section}'"
                )

    def test_04_all_backward_compatible_discovery_symlinks_exist(self):
        for role in EXPECTED_ROLES:
            symlink = os.path.join(AGENTS_DIR, f"{role}.md")
            self.assertTrue(os.path.islink(symlink), f"Expected symlink does not exist or is not a link: {symlink}")
            target = os.readlink(symlink)
            self.assertEqual(
                target,
                f"{role}/agent.md",
                f"Symlink {symlink} does not point to {role}/agent.md (points to {target})"
            )
            # Confirm link target is resolvable
            self.assertTrue(os.path.exists(symlink), f"Symlink {symlink} is broken!")


if __name__ == "__main__":
    unittest.main()
