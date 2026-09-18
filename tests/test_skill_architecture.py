# -*- coding: utf-8 -*-
"""
test_skill_architecture.py — Verification of Antigravity Skill Architecture & Contracts

Validates:
1. Every skill in .agents/skills/ possesses a valid SKILL.md with frontmatter (name, description).
2. All skills conform to Directive 18 ceilings (<= 500 lines, <= 40,000 bytes).
3. Prioritized statistical skills implement the mandatory 8-section contract:
   - WHEN TO USE
   - WHEN NOT TO USE
   - REQUIRED DATA
   - ASSUMPTIONS
   - DECISION TREE
   - EXECUTION SCRIPT
   - OUTPUT CONTRACT
   - VALIDATION
4. Orchestration decoupling: academic-suite-orchestrator acts as a deterministic runner,
   while academic-orchestrator agent owns pipeline presets.
5. Consolidated alias skills (literature-review, network-analysis) include explicit consolidation notices.
"""

import os
import re
import unittest
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILLS_DIR = os.path.join(REPO_ROOT, ".agents", "skills")
AGENTS_DIR = os.path.join(REPO_ROOT, ".agents", "agents")

PRIORITIZED_STATISTICAL_SKILLS = [
    "cfa",
    "sem",
    "mediation",
    "moderation",
    "regression",
    "assumption-testing",
    "data-audit",
    "data-cleaning",
    "descriptive-statistics",
    "reliability-analysis",
    "statistical-data-analyst",
    "psychometric-scale-validator",
    "longitudinal-moderated-mediation",
    "gpower-sample-size-calculator",
    "systematic-review-meta-analyst",
    "apa-reporting",
    "psychometric-data-simulator"
]

MANDATORY_SECTIONS = [
    "WHEN TO USE",
    "WHEN NOT TO USE",
    "REQUIRED DATA",
    "ASSUMPTIONS",
    "DECISION TREE",
    "EXECUTION SCRIPT",
    "OUTPUT CONTRACT",
    "VALIDATION"
]


class TestSkillArchitecture(unittest.TestCase):

    def setUp(self):
        self.assertTrue(os.path.isdir(SKILLS_DIR), f"Skills directory not found: {SKILLS_DIR}")
        self.skill_folders = [
            d for d in os.listdir(SKILLS_DIR)
            if os.path.isdir(os.path.join(SKILLS_DIR, d)) and not d.startswith(".") and not d.startswith("_")
        ]

    def test_all_skills_have_valid_frontmatter_and_bounds(self):
        """Assert every skill has a valid SKILL.md with name, description, <= 500 lines, <= 40KB."""
        for folder in self.skill_folders:
            skill_md = os.path.join(SKILLS_DIR, folder, "SKILL.md")
            self.assertTrue(os.path.isfile(skill_md), f"Missing SKILL.md in skill: {folder}")

            with open(skill_md, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()

            # Directive 18 ceilings
            self.assertLessEqual(len(lines), 500, f"Skill '{folder}' exceeds 500 lines ({len(lines)})")
            self.assertLessEqual(len(content.encode("utf-8")), 40000, f"Skill '{folder}' exceeds 40KB ({len(content.encode('utf-8'))} bytes)")

            # Frontmatter check
            frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            self.assertIsNotNone(frontmatter_match, f"Skill '{folder}' missing YAML frontmatter (---)")
            
            fm_data = yaml.safe_load(frontmatter_match.group(1))
            self.assertIsInstance(fm_data, dict, f"Skill '{folder}' frontmatter not a dict")
            self.assertIn("name", fm_data, f"Skill '{folder}' missing 'name' in frontmatter")
            self.assertIn("description", fm_data, f"Skill '{folder}' missing 'description' in frontmatter")
            self.assertTrue(bool(fm_data["description"].strip()), f"Skill '{folder}' has empty description")

    def test_prioritized_statistical_skills_implement_8_section_contract(self):
        """Assert all prioritized statistical skills contain the 8 mandatory contract sections."""
        for skill_name in PRIORITIZED_STATISTICAL_SKILLS:
            skill_md = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
            self.assertTrue(os.path.isfile(skill_md), f"Prioritized skill '{skill_name}' missing SKILL.md")

            with open(skill_md, "r", encoding="utf-8") as f:
                content = f.read().upper()

            for section in MANDATORY_SECTIONS:
                self.assertIn(
                    section,
                    content,
                    f"Prioritized skill '{skill_name}' missing mandatory contract section '{section}'"
                )

    def test_orchestration_decoupling(self):
        """Assert academic-suite-orchestrator is decoupled and academic-orchestrator owns pipeline presets."""
        # 1. Skill check
        skill_md = os.path.join(SKILLS_DIR, "academic-suite-orchestrator", "SKILL.md")
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Batch Pipeline CLI Runner", content)
        self.assertIn("academic-orchestrator", content)
        self.assertIn("Sole Orchestrator Mandate", content)
        self.assertIn('"The Hands"', content)

        # 2. Agent check
        agent_md = os.path.join(AGENTS_DIR, "academic-orchestrator", "agent.md")
        with open(agent_md, "r", encoding="utf-8") as f:
            agent_content = f.read()

        self.assertIn("thesis_empirical", agent_content)
        self.assertIn("scale_validation", agent_content)
        self.assertIn("meta_analysis", agent_content)

    def test_consolidated_alias_skills(self):
        """Assert literature-review and network-analysis have explicit consolidation notices."""
        lit_md = os.path.join(SKILLS_DIR, "literature-review", "SKILL.md")
        with open(lit_md, "r", encoding="utf-8") as f:
            lit_content = f.read()
        self.assertIn("Skill Consolidation Notice", lit_content)
        self.assertIn("persian-literature-review-builder", lit_content)

        net_md = os.path.join(SKILLS_DIR, "network-analysis", "SKILL.md")
        with open(net_md, "r", encoding="utf-8") as f:
            net_content = f.read()
        self.assertIn("Skill Consolidation Notice", net_content)
        self.assertIn("bibliometric-network-analyst", net_content)


if __name__ == "__main__":
    unittest.main()
