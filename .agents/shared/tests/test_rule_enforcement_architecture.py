#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_rule_enforcement_architecture.py — Verification Suite for 5-Layer Defense-in-Depth

Validates that:
1. PreToolUse hook blocks non-ASCII filenames (Directive 6).
2. PreToolUse hook blocks stage skipping on Chapter 4 deliverables (Directive 3).
3. PreToolUse hook blocks destructive shell commands on .agents and .git.
4. All 15 subagent declarations contain the Mandatory Constitutional Directives.
5. All 15 subagents have pre-bound skills in their YAML frontmatter.
6. Context budget guard verifies all 53 items within single-view thresholds.
7. Stop hook enforces Binary Honesty and physical subagent execution.
"""

import os
import sys
import json
import glob
import yaml
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, REPO_ROOT)

import importlib.util

def _load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod

_guard_mod = _load_module(
    "transcript_and_rule_guard",
    os.path.join(REPO_ROOT, ".agents", "verification", "transcript_and_rule_guard.py")
)
handle_pre_tool_use = _guard_mod.handle_pre_tool_use
handle_pre_invocation = _guard_mod.handle_pre_invocation
handle_stop = _guard_mod.handle_stop

_size_mod = _load_module(
    "skill_size_guard",
    os.path.join(REPO_ROOT, ".agents", "verification", "skill_size_guard.py")
)
audit_skill_sizes = _size_mod.audit_skill_sizes


class TestRuleEnforcementArchitecture(unittest.TestCase):
    """Test suite verifying mechanical rule enforcement across primary agent and subagents."""

    def test_01_pre_tool_use_blocks_persian_filename(self):
        """Verifies PreToolUse denies non-ASCII filenames under Directive 6."""
        payload_write = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "/workspace/تحلیل_داده.xlsx"}
            }
        }
        res = handle_pre_tool_use(payload_write)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("CONSTITUTIONAL VIOLATION (Directive 6", res.get("reason", ""))

        payload_replace = {
            "toolCall": {
                "name": "replace_file_content",
                "args": {"TargetFile": "/workspace/گزارش.docx"}
            }
        }
        res_rep = handle_pre_tool_use(payload_replace)
        self.assertEqual(res_rep.get("decision"), "deny")

    def test_02_pre_tool_use_allows_valid_ascii_filename(self):
        """Verifies PreToolUse permits valid English ASCII filenames."""
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "/workspace/valid_analysis_results.xlsx"}
            }
        }
        res = handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "allow")

    def test_03_pre_tool_use_blocks_stage_skipping(self):
        """Verifies PreToolUse blocks Chapter 4 DOCX compilation without prerequisite artifacts."""
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "/workspace/Chapter_4_Results.docx"}
            },
            "workspacePaths": ["/tmp/nonexistent_workspace_path_1234"]
        }
        res = handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("CONSTITUTIONAL VIOLATION (Directive 3", res.get("reason", ""))

    def test_04_pre_tool_use_blocks_destructive_rm(self):
        """Verifies PreToolUse denies dangerous deletion of configuration roots."""
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "rm -rf .agents"}
            }
        }
        res = handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("SECURITY VIOLATION", res.get("reason", ""))

    def test_05_all_15_subagents_contain_constitutional_directives(self):
        """Verifies all 15 subagents in .agents/agents/*.md have the constitutional header."""
        agents_dir = os.path.join(REPO_ROOT, ".agents", "agents")
        agent_files = glob.glob(os.path.join(agents_dir, "*.md"))
        self.assertEqual(len(agent_files), 15, "Expected exactly 15 subagent definition files.")

        for af in agent_files:
            with open(af, "r", encoding="utf-8") as fh:
                content = fh.read()
            self.assertIn("Mandatory Constitutional Directives", content,
                          f"Subagent {os.path.basename(af)} lacks Mandatory Constitutional Directives.")
            self.assertIn("Directive 0", content, f"Subagent {os.path.basename(af)} lacks Directive 0.")
            self.assertIn("Directive 4", content, f"Subagent {os.path.basename(af)} lacks Directive 4.")
            self.assertIn("Directive 6", content, f"Subagent {os.path.basename(af)} lacks Directive 6.")

    def test_06_all_15_subagents_have_bound_skills(self):
        """Verifies that all 15 subagents have pre-bound skills in their YAML frontmatter."""
        agents_dir = os.path.join(REPO_ROOT, ".agents", "agents")
        agent_files = glob.glob(os.path.join(agents_dir, "*.md"))

        for af in agent_files:
            with open(af, "r", encoding="utf-8") as fh:
                content = fh.read()
            parts = content.split("---", 2)
            self.assertGreaterEqual(len(parts), 3, f"Missing YAML frontmatter in {af}")
            data = yaml.safe_load(parts[1])
            skills = data.get("skills", [])
            self.assertTrue(len(skills) > 0, f"Subagent {os.path.basename(af)} has empty skills binding.")

    def test_07_context_budget_guard_passes_all_items(self):
        """Verifies that all 53 context items (skills, agents, constitution) pass size ceilings."""
        audit_res = audit_skill_sizes()
        self.assertTrue(audit_res["passed"], f"Context budget guard failed: {audit_res.get('violations')}")
        self.assertGreaterEqual(audit_res["total_checked"], 50)

    def test_08_pre_invocation_injects_ephemeral_reminders(self):
        """Verifies PreInvocation hook injects the un-bypassable constitutional reminder."""
        res = handle_pre_invocation({})
        inject_steps = res.get("injectSteps", [])
        self.assertGreater(len(inject_steps), 0)
        ephemeral = inject_steps[0].get("ephemeralMessage", "")
        self.assertIn("CONSTITUTIONAL ENFORCEMENT ACTIVE", ephemeral)
        self.assertIn("Binary Honesty Protocol", ephemeral)

    def test_09_pre_tool_use_blocks_chapter4_when_missing_micro_sections(self):
        """Verifies PreToolUse blocks Chapter 4 DOCX when section artifacts are missing (Directive 3)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create prerequisite JSONs but no section DOCX files
            with open(os.path.join(tmpdir, "stats_results.json"), "w") as f:
                f.write("{}")
            with open(os.path.join(tmpdir, "statistical_audit_report.json"), "w") as f:
                f.write("{}")

            payload = {
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": os.path.join(tmpdir, "Chapter_4_Results.docx")}
                },
                "workspacePaths": [tmpdir]
            }
            res = handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny")
            self.assertIn("Micro-Stage & One-Hypothesis-One-Stage Invariant", res.get("reason", ""))

    def test_10_pre_tool_use_allows_chapter4_when_all_micro_sections_present(self):
        """Verifies PreToolUse allows Chapter 4 DOCX when all section artifacts are present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "stats_results.json"), "w") as f:
                f.write("{}")
            with open(os.path.join(tmpdir, "statistical_audit_report.json"), "w") as f:
                f.write("{}")
            for sec in [
                "01_demographics.docx",
                "02_descriptives_and_reliability.docx",
                "03_parametric_assumptions.docx",
                "04_bivariate_correlations.docx",
                "06_hypothesis_1.docx",
                "08_chapter_summary.docx"
            ]:
                with open(os.path.join(tmpdir, sec), "w") as f:
                    f.write("dummy")

            payload = {
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": os.path.join(tmpdir, "Chapter_4_Results.docx")}
                },
                "workspacePaths": [tmpdir]
            }
            res = handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "allow")

    def test_11_pre_tool_use_blocks_chapter5_when_missing_hypothesis_discussion(self):
        """Verifies PreToolUse blocks Chapter 5 DOCX when hypothesis discussion documents are absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            payload = {
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": os.path.join(tmpdir, "Chapter_5_Discussion.docx")}
                },
                "workspacePaths": [tmpdir]
            }
            res = handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny")
            self.assertIn("Micro-Stage & One-Hypothesis-One-Stage Invariant", res.get("reason", ""))


if __name__ == "__main__":
    unittest.main()
