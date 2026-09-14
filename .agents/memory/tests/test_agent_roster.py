#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_agent_roster.py — Cognitive Subagent Roster & Architecture Verification
----------------------------------------------------------------------------
Validates:
  1. Existence and valid YAML frontmatter for all 14 subagents in .agents/agents/
  2. Cognitive subagent specifications across all 14 roles
  3. System prompts and persona definitions across all 14 roles
  4. Questionnaire registry path resolution (data/questionnaires/ & root symlink)
  5. Constitutional alignment in AGENTS.md and HYBRID_MULTI_AGENT_SPEC.md
"""

import os
import sys
import unittest
import json
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT_DIR)

# Dynamically import questionnaire_resolver
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "skills", "psychometric-scale-resolver", "scripts"))

from questionnaire_resolver import find_excel_registry, search_registry, get_scale_profile

AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
AGENTS_DEF_DIR = os.path.join(AGENTS_DIR, "agents")


class TestAgentRoster(unittest.TestCase):
    """Verifies the complete 14-agent cognitive architecture and directory restructuring."""

    EXPECTED_ROLES = [
        "digital-saber",
        "methodology-expert",
        "statistical-expert",
        "statistical-auditor",
        "results-auditor",
        "academic-writer",
        "literature-expert",
        "evidence-auditor",
        "final-judge",
        "psychometric-expert",
        "qualitative-analyst",
        "meta-analyst",
        "journal-strategist",
        "intervention-designer",
        "data-curator"
    ]

    def test_all_15_subagent_files_exist(self):
        """Verify that all 15 subagent markdown definitions exist in .agents/agents/."""
        self.assertTrue(os.path.isdir(AGENTS_DEF_DIR), f"Directory not found: {AGENTS_DEF_DIR}")
        for role in self.EXPECTED_ROLES:
            filepath = os.path.join(AGENTS_DEF_DIR, f"{role}.md")
            self.assertTrue(
                os.path.isfile(filepath),
                f"Missing agent definition file for '{role}': {filepath}"
            )

    def test_agent_frontmatter_and_content_structure(self):
        """Verify YAML frontmatter (name, description, role, skills) and non-empty body for each agent."""
        for role in self.EXPECTED_ROLES:
            filepath = os.path.join(AGENTS_DEF_DIR, f"{role}.md")
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertTrue(content.startswith("---"), f"{role}.md must start with YAML frontmatter delimiter '---'")
            parts = content.split("---", 2)
            self.assertGreaterEqual(len(parts), 3, f"{role}.md missing closing frontmatter delimiter '---'")

            frontmatter = parts[1]
            body = parts[2].strip()

            # Verify required frontmatter keys
            self.assertIn("name:", frontmatter, f"{role}.md frontmatter missing 'name'")
            self.assertIn("description:", frontmatter, f"{role}.md frontmatter missing 'description'")
            self.assertIn("role:", frontmatter, f"{role}.md frontmatter missing 'role'")
            self.assertIn("skills:", frontmatter, f"{role}.md frontmatter missing 'skills'")

            # Verify substantial markdown content
            self.assertGreater(len(body), 150, f"{role}.md body content is too short or empty")

    def test_agent_roles_count_and_parity(self):
        """Verify .agents/agents/ has exact 15 roles matching expected roster."""
        actual_files = [f.replace(".md", "") for f in os.listdir(AGENTS_DEF_DIR) if f.endswith(".md")]
        self.assertEqual(len(actual_files), 15)
        self.assertEqual(set(actual_files), set(self.EXPECTED_ROLES))

    def test_subagent_markdown_system_prompts(self):
        """Verify that each subagent specification defines clear cognitive directives and responsibilities."""
        for role in self.EXPECTED_ROLES:
            filepath = os.path.join(AGENTS_DEF_DIR, f"{role}.md")
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Subagents must define their role, responsibilities, and guidelines
            self.assertIn("# ", content, f"{role}.md missing top-level markdown heading")
            self.assertTrue(
                any(k.lower() in content.lower() for k in ["دستورالعمل", "directive", "responsibilities", "وظایف", "guidelines", "rule", "philosophy", "mission"]),
                f"{role}.md missing explicit behavioral directives"
            )

    def test_questionnaire_registry_resolution(self):
        """Verify questionnaire resolver finds Questionnaires.xlsx in data/questionnaires/."""
        resolved_path = find_excel_registry()
        self.assertIsNotNone(resolved_path, "Could not resolve Questionnaires.xlsx")
        self.assertTrue(os.path.isfile(resolved_path), f"Resolved path does not exist: {resolved_path}")

        # Query standard instruments (e.g. Beck Depression Inventory / افسردگی بک and BDI)
        results_persian = search_registry("افسردگی", excel_path=resolved_path)
        self.assertGreater(len(results_persian), 0, "Failed to search standard Persian scale 'افسردگی'")

        results_en = search_registry("Depression", excel_path=resolved_path)
        self.assertGreater(len(results_en), 0, "Failed to search standard English scale 'Depression'")

        profile = get_scale_profile("Beck Depression", excel_path=resolved_path)
        self.assertIsNotNone(profile, "Failed to get scale profile for 'Beck Depression'")

    def test_constitutional_documentation_references_all_14_agents(self):
        """Verify AGENTS.md and HYBRID_MULTI_AGENT_SPEC.md explicitly document all 14 roles."""
        agents_md_path = os.path.join(ROOT_DIR, "AGENTS.md")
        with open(agents_md_path, "r", encoding="utf-8") as f:
            agents_md = f.read()

        spec_path = os.path.join(AGENTS_DIR, "architecture", "HYBRID_MULTI_AGENT_SPEC.md")
        with open(spec_path, "r", encoding="utf-8") as f:
            spec_md = f.read()

        for role in self.EXPECTED_ROLES:
            self.assertIn(
                role,
                agents_md,
                f"AGENTS.md does not document role '{role}'"
            )
            self.assertIn(
                role,
                spec_md,
                f"HYBRID_MULTI_AGENT_SPEC.md does not document role '{role}'"
            )


if __name__ == "__main__":
    unittest.main()
