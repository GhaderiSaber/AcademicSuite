# -*- coding: utf-8 -*-
"""
test_skill_guards.py — Tests for Directive 18 Skill Modularity and Lifecycle Hook Gatekeeper
"""

import os
import sys
import unittest
import shutil

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VERIF_DIR = os.path.join(REPO_ROOT, ".agents", "verification")
if VERIF_DIR not in sys.path:
    sys.path.insert(0, VERIF_DIR)

from skill_size_guard import audit_skill_sizes, MAX_LINES_LIMIT, MAX_BYTES_LIMIT
import transcript_and_rule_guard


class TestSkillGuards(unittest.TestCase):

    def test_all_27_skills_within_limits(self):
        """Asserts all 27 repository skills satisfy Directive 18 ceilings (<= 500 lines, <= 40KB)."""
        skills_dir = os.path.join(REPO_ROOT, ".agents", "skills")
        res = audit_skill_sizes(skills_dir)
        
        self.assertTrue(res["passed"], f"Skill size violations found: {res.get('violations')}")
        self.assertEqual(res["total_checked"], 27, f"Expected 27 skills, found {res['total_checked']}")
        self.assertEqual(len(res["violations"]), 0)

    def test_skill_size_guard_detects_oversized_file(self):
        """Asserts that skill_size_guard catches skills that exceed limits."""
        dummy_dir = os.path.join(REPO_ROOT, ".agents", "skills", "_test_dummy_oversized")
        os.makedirs(dummy_dir, exist_ok=True)
        dummy_file = os.path.join(dummy_dir, "SKILL.md")
        
        try:
            with open(dummy_file, "w", encoding="utf-8") as f:
                f.write("# Dummy Oversized Skill\n" * (MAX_LINES_LIMIT + 50))
            
            skills_dir = os.path.join(REPO_ROOT, ".agents", "skills")
            res = audit_skill_sizes(skills_dir)
            
            self.assertFalse(res["passed"])
            violator_names = [v["skill"] for v in res["violations"]]
            self.assertIn("_test_dummy_oversized", violator_names)
        finally:
            if os.path.exists(dummy_dir):
                shutil.rmtree(dummy_dir)

    def test_transcript_guard_stop_clean_workspace(self):
        """Asserts that transcript_and_rule_guard allows termination on clean workspace."""
        payload = {"workspacePaths": [REPO_ROOT], "event": "Stop"}
        res = transcript_and_rule_guard.handle_stop(payload)
        self.assertEqual(res.get("decision"), "allow")


if __name__ == "__main__":
    unittest.main()
