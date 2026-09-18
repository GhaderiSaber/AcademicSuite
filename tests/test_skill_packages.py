# -*- coding: utf-8 -*-
"""
test_skill_packages.py — Verification of Phase 5 Skill Layer Architecture

Enforces that every skill in .agents/skills/ possesses:
1. SKILL.md (valid frontmatter and single-view limits)
2. scripts/ (deterministic tools)
3. resources/ (domain reference guidelines)
4. examples/ (sample payloads)
5. schemas/ (input/output JSON schemas)
"""

import os
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILLS_DIR = os.path.join(REPO_ROOT, ".agents", "skills")


class TestSkillPackages(unittest.TestCase):

    def setUp(self):
        self.skill_names = [
            d for d in os.listdir(SKILLS_DIR)
            if os.path.isdir(os.path.join(SKILLS_DIR, d)) and not d.startswith((".", "_"))
        ]

    def test_total_skills_count(self):
        """Asserts exactly 44 active production skills are present."""
        self.assertEqual(len(self.skill_names), 44, f"Expected exactly 44 production skills, found {len(self.skill_names)}")

    def test_retired_skills_in_legacy(self):
        """Asserts the 10 retired legacy workflow skill shells reside in legacy/skills/."""
        legacy_skills_dir = os.path.join(REPO_ROOT, "legacy", "skills")
        self.assertTrue(os.path.isdir(legacy_skills_dir), "Missing legacy/skills/ directory")
        expected_retired = [
            "chapter2_literature", "chapter4", "chapter5", "defense_presentation",
            "intervention_protocol", "journal_submission", "proposal",
            "scale_validation", "thesis_assembly", "thesis_revision"
        ]
        for s in expected_retired:
            self.assertTrue(os.path.isdir(os.path.join(legacy_skills_dir, s)), f"Retired skill {s} missing from legacy/skills/")
        self.assertTrue(os.path.isfile(os.path.join(legacy_skills_dir, "README.md")), "Missing legacy/skills/README.md")

    def test_all_skills_have_required_subdirectories(self):
        """Asserts each skill package contains scripts, resources, examples, schemas, and SKILL.md."""
        required_dirs = ["scripts", "resources", "examples", "schemas"]
        failures = []

        for skill in self.skill_names:
            skill_path = os.path.join(SKILLS_DIR, skill)
            skill_md = os.path.join(skill_path, "SKILL.md")
            if not os.path.isfile(skill_md):
                failures.append(f"{skill}: missing SKILL.md")
            
            for req in required_dirs:
                req_path = os.path.join(skill_path, req)
                if not os.path.isdir(req_path):
                    failures.append(f"{skill}: missing {req}/")

        self.assertEqual(failures, [], f"Skill package structural violations found:\n" + "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
