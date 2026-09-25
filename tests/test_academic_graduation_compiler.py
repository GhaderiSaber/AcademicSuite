#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_graduation_compiler.py — Unit Tests for Immediate Graduation Compiler ("The Hands")

Verifies:
1. Target resolution (global rules vs capability-specific SKILL.md files).
2. Markdown synthesis obeying Safety Rule 1 (synthesis, not stacking / semantic deduplication).
3. Directive 18 ceiling compliance, automated offloading to references/, and atomic rollback on overflow.
4. Full integration with AcademicHumanMentor (Track 1 immediate graduation vs Track 2 scoped episodic quarantine).
5. Git lifecycle handling and dry-run safety.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
for p in [ROOT_DIR, AGENTS_DIR, os.path.join(AGENTS_DIR, "scripts")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from scripts.academic_graduation_compiler import AcademicGraduationCompiler
from scripts.academic_human_mentor import AcademicHumanMentor
from hooks.dynamic_invariant_guard import DynamicInvariantGuard


class TestAcademicGraduationCompiler(unittest.TestCase):
    """Authoritative test suite for AcademicGraduationCompiler ('The Hands')."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_grad_")
        self.agents_dir = os.path.join(self.test_dir, ".agents")
        self.skills_dir = os.path.join(self.agents_dir, "skills")
        self.rules_dir = os.path.join(self.agents_dir, "plugins", "academic-suite", "rules")
        self.snapshots_dir = os.path.join(self.agents_dir, "learning", "snapshots", "skills")
        os.makedirs(self.skills_dir, exist_ok=True)
        os.makedirs(self.rules_dir, exist_ok=True)
        os.makedirs(self.snapshots_dir, exist_ok=True)

        # Create mock global rules/AGENTS.md
        self.rules_file = os.path.join(self.rules_dir, "AGENTS.md")
        with open(self.rules_file, "w", encoding="utf-8") as f:
            f.write("# Academic Suite Consolidated Domain Rules\n\n## 1. Radical Honesty & Pipeline Enforcement\n- **Directive 0**: Honesty.\n")

        # Create mock skill SKILL.md
        self.ch5_dir = os.path.join(self.skills_dir, "persian-discussion-builder")
        os.makedirs(self.ch5_dir, exist_ok=True)
        self.ch5_file = os.path.join(self.ch5_dir, "SKILL.md")
        with open(self.ch5_file, "w", encoding="utf-8") as f:
            f.write("---\nname: persian-discussion-builder\n---\n\n# Persian Discussion Builder\n\n## 1. Scope\nDraft Chapter 5.\n")

        self.compiler = AcademicGraduationCompiler(base_dir=self.test_dir)
        self.mentor = AcademicHumanMentor(base_dir=self.test_dir)

    def tearDown(self):
        if os.path.isdir(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_target_resolution(self):
        """Verify target resolution correctly maps capabilities to SKILL.md and global invariants to rules."""
        # Capability resolution
        targets_ch5 = self.compiler.resolve_targets(capability="chapter5")
        self.assertIn(self.ch5_file, targets_ch5)

        # Global resolution
        targets_global = self.compiler.resolve_targets(is_global=True)
        self.assertIn(self.rules_file, targets_global)

    def test_02_synthesize_markdown_rule_first_addition(self):
        """Verify adding an invariant to a skill creates the section and bullet."""
        res = self.compiler.synthesize_markdown_rule(
            file_path=self.ch5_file,
            item_id="PRN-2026-CH5-001",
            statement="Chapter 5 must be 100% continuous narrative prose with zero tables.",
            category="Principle"
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "GRADUATED_SUCCESS")

        with open(self.ch5_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("## 🧠 Active Learned Behavioral Invariants", content)
        self.assertIn("PRN-2026-CH5-001", content)
        self.assertIn("zero tables", content)

    def test_03_safety_rule_1_synthesis_not_stacking(self):
        """Verify that adding a related rule consolidates and merges instead of blindly stacking duplicate bullets."""
        # Initial rule
        self.compiler.synthesize_markdown_rule(
            file_path=self.ch5_file,
            item_id="PRN-2026-CH5-001",
            statement="Chapter 5 must be continuous narrative prose without statistical tables.",
            category="Principle"
        )
        with open(self.ch5_file, "r", encoding="utf-8") as f:
            lines_after_first = f.read().splitlines()

        # Follow-up related rule with overlapping keywords (chapter, continuous, narrative, tables)
        res2 = self.compiler.synthesize_markdown_rule(
            file_path=self.ch5_file,
            item_id="PRN-2026-CH5-002",
            statement="Chapter 5 discussion narrative must strictly contain zero tables.",
            category="Principle"
        )
        self.assertTrue(res2["success"])

        with open(self.ch5_file, "r", encoding="utf-8") as f:
            lines_after_second = f.read().splitlines()

        # Line count should remain essentially identical because it merged in-place
        self.assertEqual(len(lines_after_first), len(lines_after_second))
        with open(self.ch5_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("PRN-2026-CH5-002", content)
        self.assertNotIn("PRN-2026-CH5-001", content)  # Replaced by strengthened version

    def test_04_safety_rule_2_offload_when_approaching_ceiling(self):
        """Verify that approaching 470 lines automatically offloads details to references/."""
        # Pad mock skill file to 475 lines
        padding = "\n".join([f"- Item {i}" for i in range(475)])
        with open(self.ch5_file, "w", encoding="utf-8") as f:
            f.write(f"---\nname: persian-discussion-builder\n---\n\n# Skill\n\n{padding}\n")

        res = self.compiler.synthesize_markdown_rule(
            file_path=self.ch5_file,
            item_id="PRN-CH5-OVERFLOW-TEST",
            statement="Always elaborate psychological mechanisms using the 4-element cognitive model.",
            category="Principle"
        )
        self.assertTrue(res["success"])
        self.assertTrue(res["offloaded"])

        # Check references file was generated
        refs_file = os.path.join(self.ch5_dir, "references", "learned_invariants.md")
        self.assertTrue(os.path.isfile(refs_file))
        with open(refs_file, "r", encoding="utf-8") as rf:
            self.assertIn("PRN-CH5-OVERFLOW-TEST", rf.read())

    def test_05_safety_rule_2_atomic_rollback_on_overflow(self):
        """Verify that exceeding 500 lines triggers an atomic rollback leaving the file pristine."""
        # Pad mock skill file to 492 lines (total 497 lines with header)
        padding = "\n".join([f"- Item {i}" for i in range(492)])
        initial_content = f"---\nname: persian-discussion-builder\n---\n\n# Skill\n\n{padding}\n"
        with open(self.ch5_file, "w", encoding="utf-8") as f:
            f.write(initial_content)

        # Attempt to synthesize an addition that pushes it to 501+ lines even with compact bullet
        huge_statement = "Excessive rule content that overflows."
        res = self.compiler.synthesize_markdown_rule(
            file_path=self.ch5_file,
            item_id="PRN-HUGE-FAIL",
            statement=huge_statement,
            category="Principle"
        )
        # Should detect overflow past 500 lines and roll back to original content
        self.assertEqual(res["status"], "OVERFLOW_ROLLED_BACK")
        self.assertFalse(res["success"])

        with open(self.ch5_file, "r", encoding="utf-8") as f:
            restored = f.read()

        self.assertEqual(restored, initial_content)
        self.assertLessEqual(len(restored.splitlines()), 500)

    def test_06_end_to_end_mentor_track1_graduation(self):
        """Verify AcademicHumanMentor.teach() runs Track 1 graduation and returns receipt badge."""
        res = self.mentor.teach(
            category="principle",
            statement="Chapter 5 must be 100% continuous narrative prose with zero tables.",
            rationale="Methodological law established by Saber Ghaderi.",
            capability="chapter5",
            scope="cross-project",
            auto_commit=False
        )
        self.assertEqual(res["track"], 1)
        self.assertIsNotNone(res["grad_info"])
        self.assertTrue(res["grad_info"]["all_passed"])
        self.assertIn("Track 1 Full Graduation Applied (The Hands)", res["badge"])
        self.assertIn("Directive 18 Size Guard", res["badge"])

        # Check physical SKILL.md file
        with open(self.ch5_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Active Learned Behavioral Invariants", content)
        self.assertIn("zero tables", content)

    def test_07_end_to_end_mentor_track2_case_specific_quarantine(self):
        """Verify AcademicHumanMentor.teach_from_natural_language() routes case-specific facts to Track 2 without touching SKILL.md."""
        res = self.mentor.teach_from_natural_language(
            text="In DASS-21, items 3, 5, 10 measure stress.",
            default_capability="chapter5",
            scope="cross-project",
            auto_commit=False
        )
        self.assertEqual(res["track"], 2)
        self.assertIsNone(res["grad_info"])
        self.assertIn("Track 2: Scoped Episodic Memory Stored", res["badge"])
        self.assertNotIn("Track 1 Full Graduation Applied", res["badge"])

        # Physical SKILL.md should NOT contain DASS-21 items
        with open(self.ch5_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("DASS-21", content)

    def test_08_graduate_from_json_file(self):
        """Verify graduate_from_json_file reads lesson JSON, updates SKILL.md, and marks status GRADUATED."""
        import json
        lesson_data = {
            "contract_version": "1.0.0",
            "lesson_id": "LSN-2026-CH5-FOOTNOTES-001",
            "desired_behavior": "Mandate native OpenXML footnotes in Word docx for Chapter 5.",
            "related_skills": ["persian-discussion-builder"],
            "graduation_track": "TRACK_1_IMMEDIATE_GRADUATION",
            "graduation_status": "PENDING_GRADUATION"
        }
        json_path = os.path.join(self.test_dir, "lesson_test.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(lesson_data, f, indent=2)

        res = self.compiler.graduate_from_json_file(json_path, auto_commit=False)
        self.assertTrue(res["all_passed"])
        self.assertIn(self.ch5_file, res["targets"])

        # Check SKILL.md
        with open(self.ch5_file, "r", encoding="utf-8") as f:
            skill_content = f.read()
        self.assertIn("LSN-2026-CH5-FOOTNOTES-001", skill_content)
        self.assertIn("Mandate native OpenXML footnotes", skill_content)

        # Check JSON was updated to GRADUATED
        with open(json_path, "r", encoding="utf-8") as f:
            updated_json = json.load(f)
        self.assertEqual(updated_json["graduation_status"], "GRADUATED")
        self.assertIn("graduated_at", updated_json)

    def test_09_compile_all_pending(self):
        """Verify compile_all_pending scans knowledge directories and graduates all pending items."""
        import json
        lessons_dir = os.path.join(self.agents_dir, "learning", "knowledge", "lessons")
        os.makedirs(lessons_dir, exist_ok=True)

        lesson_data = {
            "contract_version": "1.0.0",
            "lesson_id": "LSN-2026-BATCH-TEST-001",
            "desired_behavior": "Enforce explicit right alignment on all Persian headings.",
            "related_skills": ["persian-discussion-builder"],
            "graduation_status": "PENDING_GRADUATION"
        }
        json_path = os.path.join(lessons_dir, "LSN-2026-BATCH-TEST-001.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(lesson_data, f, indent=2)

        results = self.compiler.compile_all_pending(auto_commit=False)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]["all_passed"])

        with open(self.ch5_file, "r", encoding="utf-8") as f:
            skill_content = f.read()
        self.assertIn("LSN-2026-BATCH-TEST-001", skill_content)

    def test_10_cross_workspace_compilation_and_sync(self):
        """Verify compile_all_pending scans external client workspaces and syncs graduated lessons to central store."""
        import json
        client_ws = tempfile.mkdtemp(prefix="client_ws_")
        try:
            client_lessons_dir = os.path.join(client_ws, ".agents", "learning", "knowledge", "lessons")
            os.makedirs(client_lessons_dir, exist_ok=True)

            lesson_data = {
                "contract_version": "1.0.0",
                "lesson_id": "LSN-CLIENT-CROSS-001",
                "desired_behavior": "Enforce strict cross-workspace lesson synchronization.",
                "related_skills": ["persian-discussion-builder"],
                "graduation_status": "PENDING_GRADUATION"
            }
            client_json_path = os.path.join(client_lessons_dir, "LSN-CLIENT-CROSS-001.json")
            with open(client_json_path, "w", encoding="utf-8") as f:
                json.dump(lesson_data, f, indent=2)

            # Compile passing client_ws
            results = self.compiler.compile_all_pending(workspaces=[client_ws], auto_commit=False)
            self.assertEqual(len(results), 1)
            self.assertTrue(results[0]["all_passed"])

            # 1. Verify AcademicSuite skill was evolved
            with open(self.ch5_file, "r", encoding="utf-8") as f:
                skill_content = f.read()
            self.assertIn("LSN-CLIENT-CROSS-001", skill_content)

            # 2. Verify client workspace JSON status updated to GRADUATED
            with open(client_json_path, "r", encoding="utf-8") as f:
                client_d = json.load(f)
            self.assertEqual(client_d.get("graduation_status"), "GRADUATED")

            # 3. Verify central AcademicSuite store received the synchronized lesson JSON
            central_lesson_path = os.path.join(self.agents_dir, "learning", "knowledge", "lessons", "LSN-CLIENT-CROSS-001.json")
            self.assertTrue(os.path.isfile(central_lesson_path))
            with open(central_lesson_path, "r", encoding="utf-8") as f:
                central_d = json.load(f)
            self.assertEqual(central_d.get("graduation_status"), "GRADUATED")
        finally:
            shutil.rmtree(client_ws, ignore_errors=True)

    def test_11_candidate_compilation(self):
        """Compiler must promote improvement_candidate JSON and synthesize the rule into target component."""
        cand_data = {
            "candidate_id": "CAND-TEST-ALIGN-001",
            "target_component": ".agents/skills/persian-discussion-builder/SKILL.md",
            "rationale": "Universally remove <w:jc> under <w:bidi> tags for all headings.",
            "mutation": {
                "diff_type": "UNIFIED_DIFF",
                "content": "--- SKILL.md\n+++ SKILL.md\n@@ -1,2 +1,3 @@\n+Universally remove <w:jc> under <w:bidi> tags for all headings."
            },
            "status": "STAGED"
        }
        cand_path = os.path.join(self.test_dir, "CAND-TEST-ALIGN-001.json")
        with open(cand_path, "w", encoding="utf-8") as f:
            json.dump(cand_data, f, indent=2)

        res = self.compiler.graduate_candidate_from_json_file(cand_path, auto_commit=False)
        self.assertTrue(res.get("all_passed"))
        self.assertEqual(res.get("status"), "PROMOTED")

        # Verify skill was mutated
        with open(self.ch5_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("CAND-TEST-ALIGN-001", content)
        self.assertIn("Universally remove", content)

        # Verify candidate JSON was updated to PROMOTED
        with open(cand_path, "r", encoding="utf-8") as f:
            updated_cand = json.load(f)
        self.assertEqual(updated_cand.get("status"), "PROMOTED")

    def test_12_channel_2_hook_registration_and_enforcement(self):
        """Channel 2 must register mechanical rules in enforced_invariants.json and block violating tool calls."""
        from hooks.dynamic_invariant_guard import DynamicInvariantGuard
        ap_dir = os.path.join(self.agents_dir, "learning", "knowledge", "anti-patterns")
        os.makedirs(ap_dir, exist_ok=True)

        ap_data = {
            "contract_version": "1.0.0",
            "anti_pattern_id": "AP-TEST-LEAKAGE-001",
            "category": "execution",
            "defective_pattern": "Leaking subheadings into reference files.",
            "why_defective": "Corrupts bibliography artifacts.",
            "observed_symptoms": ["Subheadings appearing in bibliography"],
            "corrective_remedy": "Filter subheadings before reference export.",
            "detection_heuristic": {
                "trigger_rule": "Detect leaked subheadings",
                "regex_patterns": [r"(?m)^\s*(?:English References|فصل \d+)\s*$"],
                "file_pattern": r".*references.*\.txt",
                "check_type": "regex_ban",
                "event": "PreToolUse"
            },
            "target_agent": "academic-writer",
            "target_agents": ["academic-writer"],
            "related_skills": ["persian-discussion-builder"],
            "reusable": True,
            "graduation_status": "PENDING_GRADUATION"
        }
        ap_path = os.path.join(ap_dir, "AP-TEST-LEAKAGE-001.json")
        with open(ap_path, "w", encoding="utf-8") as f:
            json.dump(ap_data, f, indent=2)

        res = self.compiler.graduate_from_json_file(ap_path, auto_commit=False)
        self.assertTrue(res["all_passed"])
        self.assertTrue(res["hook_registered"], "Channel 2 hook must be registered")

        # Verify rule is present in mock enforced_invariants.json
        inv_file = os.path.join(self.agents_dir, "hooks", "rules", "enforced_invariants.json")
        self.assertTrue(os.path.isfile(inv_file))
        with open(inv_file, "r", encoding="utf-8") as f:
            invs = json.load(f).get("invariants", {})
        self.assertIn("AP-TEST-LEAKAGE-001", invs)
        self.assertEqual(invs["AP-TEST-LEAKAGE-001"]["check_type"], "regex_ban")

        # Test mechanical evaluation
        eval_res = DynamicInvariantGuard.evaluate_pre_tool_use(
            "academic-writer",
            {
                "toolCall": {
                    "name": "write_to_file",
                    "args": {
                        "TargetFile": "03_deliverables/references.txt",
                        "CodeContent": "English References\nSmith, J. (2020)."
                    }
                }
            }
        )
        self.assertEqual(eval_res.get("decision"), "deny")

    def test_13_companion_antipattern_resolution(self):
        """Graduating a lesson without explicit detection_heuristic must resolve companion anti-pattern heuristic."""
        ap_dir = os.path.join(self.agents_dir, "learning", "knowledge", "anti-patterns")
        lessons_dir = os.path.join(self.agents_dir, "learning", "knowledge", "lessons")
        os.makedirs(ap_dir, exist_ok=True)
        os.makedirs(lessons_dir, exist_ok=True)

        # Companion Anti-Pattern with regex_patterns
        ap_data = {
            "contract_version": "1.0.0",
            "anti_pattern_id": "AP-COMPANION-RESOLVE-TEST",
            "category": "execution",
            "defective_pattern": "Prohibited pattern.",
            "why_defective": "Defective.",
            "observed_symptoms": ["Symptom"],
            "corrective_remedy": "Remedy.",
            "detection_heuristic": {
                "trigger_rule": "Detect pattern",
                "regex_patterns": [r"prohibited_keyword"],
                "file_pattern": r".*\.txt",
                "check_type": "regex_ban"
            },
            "target_agent": "academic-writer",
            "target_agents": ["academic-writer"],
            "reusable": True
        }
        with open(os.path.join(ap_dir, "AP-COMPANION-RESOLVE-TEST.json"), "w", encoding="utf-8") as f:
            json.dump(ap_data, f, indent=2)

        # Lesson sharing slug
        lesson_data = {
            "contract_version": "1.0.0",
            "lesson_id": "LSN-COMPANION-RESOLVE-TEST-001",
            "desired_behavior": "Enforce strict companion resolution.",
            "related_skills": ["persian-discussion-builder"],
            "target_agents": ["academic-writer"],
            "graduation_status": "PENDING_GRADUATION"
        }
        lesson_path = os.path.join(lessons_dir, "LSN-COMPANION-RESOLVE-TEST-001.json")
        with open(lesson_path, "w", encoding="utf-8") as f:
            json.dump(lesson_data, f, indent=2)

        res = self.compiler.graduate_from_json_file(lesson_path, auto_commit=False)
        self.assertTrue(res["all_passed"])
        self.assertTrue(res["hook_registered"], "Channel 2 hook must be registered via companion anti-pattern")

    def test_14_graduate_script_candidate_with_unified_diff(self):
        """Verify candidate mutating a Python script applies unified diff cleanly without injecting markdown."""
        script_path = os.path.join(self.test_dir, "test_target_script.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write("def calculate_total(a, b):\n    return a + b\n")

        diff = (
            "--- test_target_script.py\n"
            "+++ test_target_script.py\n"
            "@@ -1,2 +1,4 @@\n"
            " def calculate_total(a, b):\n"
            "+    # Validate non-negative numbers\n"
            "+    assert a >= 0 and b >= 0\n"
            "     return a + b\n"
        )
        cand_data = {
            "candidate_id": "CAND-TEST-SCRIPT-001",
            "target_component": "test_target_script.py",
            "target_type": "SKILL_DETERMINISTIC_SCRIPT",
            "mutation": {
                "diff_type": "UNIFIED_DIFF",
                "content": diff
            },
            "status": "STAGED",
            "rationale": "Add assert non-negative"
        }
        cand_dir = os.path.join(self.agents_dir, "learning", "candidates")
        os.makedirs(cand_dir, exist_ok=True)
        cand_file = os.path.join(cand_dir, "CAND-TEST-SCRIPT-001.json")
        with open(cand_file, "w", encoding="utf-8") as f:
            json.dump(cand_data, f, indent=2)

        res = self.compiler.graduate_candidate_from_json_file(cand_file, auto_commit=False)
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "PROMOTED")

        # Verify script content
        with open(script_path, "r", encoding="utf-8") as f:
            updated_script = f.read()
        self.assertIn("assert a >= 0 and b >= 0", updated_script)
        self.assertNotIn("## 🧠 Active Learned Behavioral Invariants", updated_script)

    def test_15_graduate_candidate_with_mechanical_rule(self):
        """Verify candidate specifying mechanical rule registers invariant in enforced_invariants.json."""
        script_path = os.path.join(self.test_dir, "test_target_mech.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write("def parse(x):\n    return x\n")

        cand_data = {
            "candidate_id": "CAND-TEST-MECH-001",
            "target_component": "test_target_mech.py",
            "target_type": "SKILL_DETERMINISTIC_SCRIPT",
            "mutation": {
                "diff_type": "STRING_REPLACE",
                "target_content": "def parse(x):",
                "replacement_content": "def parse(x):\n    # safe parse"
            },
            "mechanical_rule": {
                "pattern": r"(?m)^prohibited_leak.*$",
                "file_pattern": r".*\.txt",
                "check_type": "regex_ban",
                "event": "PreToolUse",
                "violation_message": "Prohibited leak pattern detected."
            },
            "status": "STAGED"
        }
        cand_dir = os.path.join(self.agents_dir, "learning", "candidates")
        os.makedirs(cand_dir, exist_ok=True)
        cand_file = os.path.join(cand_dir, "CAND-TEST-MECH-001.json")
        with open(cand_file, "w", encoding="utf-8") as f:
            json.dump(cand_data, f, indent=2)

        res = self.compiler.graduate_candidate_from_json_file(cand_file, auto_commit=False)
        self.assertTrue(res["success"])
        self.assertTrue(res["hook_registered"])

        invs = DynamicInvariantGuard.load_invariants(self.test_dir)
        self.assertIn("CAND-TEST-MECH-001", invs)
        self.assertEqual(invs["CAND-TEST-MECH-001"]["pattern"], r"(?m)^prohibited_leak.*$")

    def test_16_compile_all_pending_scans_candidates(self):
        """Verify compile_all_pending scans candidates directory and graduates pending candidates."""
        script_path = os.path.join(self.test_dir, "test_batch_cand.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write("val = 1\n")

        cand_data = {
            "candidate_id": "CAND-BATCH-CAND-001",
            "target_component": "test_batch_cand.py",
            "target_type": "SKILL_DETERMINISTIC_SCRIPT",
            "mutation": {
                "diff_type": "STRING_REPLACE",
                "target_content": "val = 1",
                "replacement_content": "val = 2"
            },
            "status": "EVALUATION_PASSED"
        }
        cand_dir = os.path.join(self.agents_dir, "learning", "candidates")
        os.makedirs(cand_dir, exist_ok=True)
        cand_file = os.path.join(cand_dir, "CAND-BATCH-CAND-001.json")
        with open(cand_file, "w", encoding="utf-8") as f:
            json.dump(cand_data, f, indent=2)

        results = self.compiler.compile_all_pending(auto_commit=False)
        cand_res = [r for r in results if r.get("candidate_id") == "CAND-BATCH-CAND-001"]
        self.assertEqual(len(cand_res), 1)
        self.assertTrue(cand_res[0]["success"])

        with open(script_path, "r", encoding="utf-8") as f:
            self.assertIn("val = 2", f.read())


if __name__ == "__main__":
    unittest.main()


