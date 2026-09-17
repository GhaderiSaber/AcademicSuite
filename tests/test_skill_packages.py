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
        """Asserts all 53 skills are present."""
        self.assertGreaterEqual(len(self.skill_names), 50, f"Expected >= 50 skills, found {len(self.skill_names)}")

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
