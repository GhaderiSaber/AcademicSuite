#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_learning_to_mechanical_rule_pipeline.py
Comprehensive End-to-End Test Suite for Learning-to-Mechanical-Rule Pipeline.

Verifies Directive 24 & Directive 25 invariants:
1. Candidate schema validation with mechanical_rule and STRING_REPLACE support.
2. Code mutation on deterministic Python scripts (SKILL_DETERMINISTIC_SCRIPT).
3. Companion mechanical rule compilation into enforced_invariants.json.
4. Active mechanical hook interception by DynamicInvariantGuard (fail-closed blocking).
5. Anti-placebo guard: rejects descriptive English prose from being registered as regex patterns.
6. Clean isolation: zero mass offloading of already-graduated historical items.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
import jsonschema

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
for p in (ROOT_DIR, AGENTS_DIR, os.path.join(AGENTS_DIR, "scripts"), os.path.join(AGENTS_DIR, "hooks")):
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

from academic_graduation_compiler import AcademicGraduationCompiler, _is_actionable_regex_pattern
from dynamic_invariant_guard import DynamicInvariantGuard


class TestLearningToMechanicalRulePipeline(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="agy_learning_pipeline_test_")
        self.schema_path = os.path.join(
            ROOT_DIR, ".agents", "contracts", "evolution", "improvement_candidate.schema.json"
        )
        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.candidate_schema = json.load(f)

        # Create temporary workspace mimicking AcademicSuite structure
        self.ws_agents = os.path.join(self.test_dir, ".agents")
        self.ws_skills = os.path.join(self.ws_agents, "skills")
        self.ws_candidates = os.path.join(self.ws_agents, "learning", "candidates")
        self.ws_invariants = os.path.join(self.ws_agents, "hooks", "rules", "enforced_invariants.json")
        os.makedirs(self.ws_skills, exist_ok=True)
        os.makedirs(self.ws_candidates, exist_ok=True)
        os.makedirs(os.path.dirname(self.ws_invariants), exist_ok=True)

        with open(self.ws_invariants, "w", encoding="utf-8") as f:
            json.dump({"contract_version": "1.0.0", "invariants": {}}, f)

        # Target Python script to evolve
        self.test_script_path = os.path.join(self.test_dir, "sample_tool_runner.py")
        with open(self.test_script_path, "w", encoding="utf-8") as f:
            f.write(
                "def calculate_metric(data):\n"
                "    # legacy computation\n"
                "    result = sum(data) / len(data)\n"
                "    return result\n"
            )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_candidate_schema_validates_script_mutation_and_mechanical_rule(self):
        """Validates that candidate JSON with script mutation and mechanical_rule satisfies contract schema."""
        candidate_data = {
            "contract_version": "1.0.0",
            "candidate_id": "CAND-2026-TEST-CODE-001",
            "target_component": "sample_tool_runner.py",
            "target_type": "SKILL_DETERMINISTIC_SCRIPT",
            "parent_version": "v1.0.0",
            "mutation": {
                "diff_type": "STRING_REPLACE",
                "content": "    # optimized computation\n    result = sum(data) / max(len(data), 1)",
                "target_content": "    # legacy computation\n    result = sum(data) / len(data)",
                "replacement_content": "    # optimized computation\n    result = sum(data) / max(len(data), 1)"
            },
            "rationale": "Prevents ZeroDivisionError on empty sample data slices.",
            "expected_improvement": {
                "target_metric": "ZeroDivisionError count",
                "baseline_value": "1.0",
                "projected_value": "0.0"
            },
            "affected_capabilities": ["statistical-data-analyst"],
            "author_agent": "skill-evolver",
            "status": "STAGED",
            "staged_at": "2026-09-25T19:00:00Z",
            "mechanical_rule": {
                "event": "PreToolUse",
                "tool_match": "write_to_file|replace_file_content",
                "file_pattern": ".*\\.py",
                "check_type": "regex_ban",
                "pattern": r"(?m)^\s*result = sum\(data\) / len\(data\)\s*$",
                "violation_message": "Unsafe zero division pattern detected in statistical script.",
                "remedy": "Use max(len(data), 1) to guard denominator.",
                "target_agents": ["*"]
            }
        }

        # Must validate against JSON schema without error
        jsonschema.validate(instance=candidate_data, schema=self.candidate_schema)

    def test_02_graduation_compiler_mutates_script_and_registers_mechanical_rule(self):
        """Tests that AcademicGraduationCompiler patches Python script and registers mechanical rule."""
        cand_file = os.path.join(self.ws_candidates, "CAND-2026-TEST-CODE-001.json")
        candidate_data = {
            "contract_version": "1.0.0",
            "candidate_id": "CAND-2026-TEST-CODE-001",
            "target_component": "sample_tool_runner.py",
            "target_type": "SKILL_DETERMINISTIC_SCRIPT",
            "parent_version": "v1.0.0",
            "mutation": {
                "diff_type": "STRING_REPLACE",
                "content": "    # optimized computation\n    result = sum(data) / max(len(data), 1)",
                "target_content": "    # legacy computation\n    result = sum(data) / len(data)",
                "replacement_content": "    # optimized computation\n    result = sum(data) / max(len(data), 1)"
            },
            "rationale": "Prevents ZeroDivisionError on empty sample data slices.",
            "expected_improvement": {
                "target_metric": "ZeroDivisionError count",
                "baseline_value": "1.0",
                "projected_value": "0.0"
            },
            "affected_capabilities": ["statistical-data-analyst"],
            "author_agent": "skill-evolver",
            "status": "STAGED",
            "staged_at": "2026-09-25T19:00:00Z",
            "mechanical_rule": {
                "event": "PreToolUse",
                "tool_match": "write_to_file|replace_file_content",
                "file_pattern": ".*\\.py",
                "check_type": "regex_ban",
                "pattern": r"result = sum\(data\) / len\(data\)",
                "violation_message": "Unsafe zero division pattern detected in statistical script.",
                "remedy": "Use max(len(data), 1) to guard denominator.",
                "target_agents": ["*"]
            }
        }
        with open(cand_file, "w", encoding="utf-8") as f:
            json.dump(candidate_data, f, indent=2)

        compiler = AcademicGraduationCompiler(base_dir=self.test_dir)
        res = compiler.graduate_candidate_from_json_file(cand_file, auto_commit=False, dry_run=False)

        self.assertTrue(res.get("all_passed"))
        self.assertEqual(res.get("status"), "PROMOTED")

        # 1. Verify code was updated on disk
        with open(self.test_script_path, "r", encoding="utf-8") as f:
            updated_code = f.read()
        self.assertIn("max(len(data), 1)", updated_code)
        self.assertNotIn("result = sum(data) / len(data)\n", updated_code)

        # 2. Verify candidate JSON was updated with graduation metadata
        with open(cand_file, "r", encoding="utf-8") as f:
            promoted_cand = json.load(f)
        self.assertEqual(promoted_cand.get("status"), "PROMOTED")
        self.assertEqual(promoted_cand.get("graduation_status"), "GRADUATED")

        # 3. Verify mechanical rule was registered into enforced_invariants.json
        with open(self.ws_invariants, "r", encoding="utf-8") as f:
            inv_data = json.load(f)
        self.assertIn("CAND-2026-TEST-CODE-001", inv_data["invariants"])
        rule = inv_data["invariants"]["CAND-2026-TEST-CODE-001"]
        self.assertEqual(rule["pattern"], r"result = sum\(data\) / len\(data\)")
        self.assertEqual(rule["check_type"], "regex_ban")

    def test_03_mechanical_rule_actively_blocks_violating_tool_use(self):
        """Verifies that DynamicInvariantGuard intercepts and blocks a violating tool call."""
        # Register a mechanical rule in the test invariants file
        rule_registered = DynamicInvariantGuard.register_invariant(
            item_id="BAN-2026-RAW-ZERO-DIV",
            category="Learned Mechanical Rule",
            statement="Unsafe division without len guard prohibited.",
            target_agents=["statistics-agent"],
            event="PreToolUse",
            tool_match="write_to_file|replace_file_content",
            file_pattern=".*\\.py",
            check_type="regex_ban",
            pattern=r"sum\(x\)\s*/\s*len\(x\)",
            violation_message="Zero-division vulnerability banned by mechanical hook.",
            remedy="Wrap len(x) with max(len(x), 1).",
            base_dir=self.test_dir
        )
        self.assertTrue(rule_registered)

        # Simulate a violating tool call from statistics-agent
        violating_payload = {
            "caller": "statistics-agent",
            "agentName": "statistics-agent",
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": os.path.join(self.test_dir, "subscale_aggregator.py"),
                    "CodeContent": "def mean(x): return sum(x) / len(x)\n"
                }
            }
        }
        res_violating = DynamicInvariantGuard.evaluate_pre_tool_use("statistics-agent", violating_payload)
        self.assertEqual(res_violating.get("decision"), "deny")
        self.assertIn("Zero-division vulnerability banned", res_violating.get("reason", ""))

        # Simulate a compliant tool call
        compliant_payload = {
            "caller": "statistics-agent",
            "agentName": "statistics-agent",
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": os.path.join(self.test_dir, "subscale_aggregator.py"),
                    "CodeContent": "def mean(x): return sum(x) / max(len(x), 1)\n"
                }
            }
        }
        res_compliant = DynamicInvariantGuard.evaluate_pre_tool_use("statistics-agent", compliant_payload)
        self.assertEqual(res_compliant.get("decision"), "allow")

    def test_04_anti_placebo_guard_rejects_prose_sentences(self):
        """Verifies that descriptive English prose is rejected from being registered as regex patterns."""
        prose_cases = [
            "Presence of bold styling applied to paragraph styles or runs explicitly acting as Table Captions.",
            "High density of colons (:) following short phrase prefixes within standard academic paragraphs.",
            "Detect any regression coefficients table with multiple 'ثابت' rows lacking a 'متغیر ملاک' column.",
            "Flag two-column tables where Col 0 repeats identical parent variable names on consecutive rows.",
            "USER_FEEDBACK containing negative critique or defect indicators MUST trigger learning pipeline.",
            "Absence of ANOVA sum of squares or Correlation matrix in regression reporting blocks."
        ]
        for prose in prose_cases:
            self.assertFalse(
                _is_actionable_regex_pattern(prose),
                f"Prose string falsely classified as actionable regex: {prose}"
            )

        actionable_cases = [
            r"\|[ \t]*-[ \t]*\|[ \t]*-[ \t]*\|",
            r"(?m)^\s*(?:[#\-*]+\s*)?(?:(?:الف|ب|ج)\)\s*منابع.*|English References)\s*$",
            r"<w:jc\s+w:val=\"right\"/>",
            r"(?m)^[^\n]\n#+\s",
            r"(?m)^.*re\.search\(r['\"]\d\{4\}['\"].*$"
        ]
        for actionable in actionable_cases:
            self.assertTrue(
                _is_actionable_regex_pattern(actionable),
                f"Actionable regex falsely rejected: {actionable}"
            )

    def test_05_compile_all_pending_does_not_churn_graduated_knowledge(self):
        """Verifies that compile_all_pending does not churn historical active knowledge files."""
        # Create an already-graduated or active knowledge item without pending flag
        active_lesson = os.path.join(self.ws_agents, "learning", "knowledge", "lessons", "LSN-2026-ACTIVE-001.json")
        os.makedirs(os.path.dirname(active_lesson), exist_ok=True)
        with open(active_lesson, "w", encoding="utf-8") as f:
            json.dump({
                "lesson_id": "LSN-2026-ACTIVE-001",
                "statement": "Already active lesson.",
                "is_active_behavior": True,
                "graduation_status": "GRADUATED"
            }, f)

        compiler = AcademicGraduationCompiler(base_dir=self.test_dir)
        results = compiler.compile_all_pending(auto_commit=False, dry_run=False)

        # Must NOT re-graduate the active lesson
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()
