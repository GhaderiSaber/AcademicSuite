# -*- coding: utf-8 -*-
"""
test_project_structure.py — Verification of Target Canonical Project Architecture

Asserts that repository directory structure, tools, artifacts, docs, protocols,
and legacy archiving strictly adhere to the 17-Phase Architecture Guide.
"""

import os
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TestProjectStructure(unittest.TestCase):

    def test_tools_layer_exists(self):
        """Asserts tools/ contains python/ and r/ computational engines."""
        self.assertTrue(os.path.isdir(os.path.join(REPO_ROOT, "tools", "python")), "Missing tools/python/")
        self.assertTrue(os.path.isdir(os.path.join(REPO_ROOT, "tools", "r")), "Missing tools/r/")
        self.assertTrue(os.path.isfile(os.path.join(REPO_ROOT, "tools", "README.md")), "Missing tools/README.md")
        self.assertTrue(os.path.isfile(os.path.join(REPO_ROOT, "tools", "python", "statistical_runner.py")), "Missing statistical_runner.py")

    def test_artifacts_layer_exists(self):
        """Asserts artifacts/ contains project, analysis, validation, reports."""
        subdirs = ["project", "analysis", "validation", "reports"]
        for s in subdirs:
            p = os.path.join(REPO_ROOT, "artifacts", s)
            self.assertTrue(os.path.isdir(p), f"Missing artifacts/{s}/")
        self.assertTrue(os.path.isfile(os.path.join(REPO_ROOT, "artifacts", "README.md")), "Missing artifacts/README.md")

    def test_evaluations_alias_exists(self):
        """Asserts evaluations exists as directory or symlink pointing to evals."""
        p = os.path.join(REPO_ROOT, "evaluations")
        self.assertTrue(os.path.exists(p), "Missing evaluations alias/symlink")
        self.assertTrue(os.path.exists(os.path.join(p, "run_eval_suite.py")), "evaluations should expose run_eval_suite.py")

    def test_legacy_archiving_exists(self):
        """Asserts legacy/ contains workflows/ with archived workflows."""
        legacy_wf = os.path.join(REPO_ROOT, "legacy", "workflows")
        self.assertTrue(os.path.isdir(legacy_wf), "Missing legacy/workflows/")
        self.assertTrue(os.path.isfile(os.path.join(REPO_ROOT, "legacy", "README.md")), "Missing legacy/README.md")
        self.assertTrue(os.path.isfile(os.path.join(REPO_ROOT, ".agents", "workflows", "README.md")), "Missing .agents/workflows/README.md")

    def test_docs_and_protocols_exist(self):
        """Asserts docs/ contains architecture.md, agent-contracts/, and protocols/."""
        self.assertTrue(os.path.exists(os.path.join(REPO_ROOT, "docs", "architecture.md")), "Missing docs/architecture.md")
        self.assertTrue(os.path.isfile(os.path.join(REPO_ROOT, "docs", "agent-contracts", "README.md")), "Missing docs/agent-contracts/README.md")
        
        protocols = ["stage_gate_protocol.md", "triad_invariant.md", "binary_honesty.md", "failure_recovery.md"]
        for proto in protocols:
            proto_path = os.path.join(REPO_ROOT, "docs", "protocols", proto)
            self.assertTrue(os.path.isfile(proto_path), f"Missing docs/protocols/{proto}")

    def test_canonical_rules_exist(self):
        """Asserts .agents/rules/ contains canonical rule files."""
        rules = ["academic-integrity.md", "data-integrity.md", "project-conventions.md"]
        for r in rules:
            r_path = os.path.join(REPO_ROOT, ".agents", "rules", r)
            self.assertTrue(os.path.isfile(r_path), f"Missing .agents/rules/{r}")

    def test_lifecycle_hooks_exist(self):
        """Asserts .agents/hooks/ contains hook runner scripts."""
        hook_runners = ["pre_tool_use.py", "post_tool_use.py", "pre_invocation.py", "stop_guard.py"]
        for h in hook_runners:
            h_path = os.path.join(REPO_ROOT, ".agents", "hooks", h)
            self.assertTrue(os.path.isfile(h_path), f"Missing .agents/hooks/{h}")


if __name__ == "__main__":
    unittest.main()
