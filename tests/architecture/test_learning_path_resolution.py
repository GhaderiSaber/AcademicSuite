#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_learning_path_resolution.py — Architectural Verification of Multi-Root & Multi-Machine Path Portability

Verifies:
1. AcademicGraduationCompiler resolves suite-relative targets (.agents/skills/...)
2. AcademicGraduationCompiler resolves project-relative targets (02_analysis_code/...) in external workspaces
3. AcademicGraduationCompiler resolves parameterized targets (${WORKSPACE_ROOT}, ${SUITE_ROOT})
4. AcademicGraduationCompiler resolves absolute targets without path truncation
5. All 31 subagent hooks.json use portable resolution without hardcoded host usernames
6. Context boundary injects dynamic directory anchors at dispatch
7. Continuous learning subagent prompts forbid recursive home scans
"""

import os
import sys
import json
import glob
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
for p in [ROOT_DIR, AGENTS_DIR, os.path.join(AGENTS_DIR, "scripts"), os.path.join(AGENTS_DIR, "hooks")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from scripts.academic_graduation_compiler import AcademicGraduationCompiler
from scripts.academic_adaptive_context_boundary import AcademicAdaptiveContextBoundary
from contracts.canonical_paths import resolve_canonical_repo_root, get_canonical_learning_dir


class TestLearningPathResolution(unittest.TestCase):
    """Authoritative test suite for learning subagents multi-root path discovery and portability."""

    def setUp(self):
        self.compiler = AcademicGraduationCompiler(base_dir=ROOT_DIR)
        self.boundary = AcademicAdaptiveContextBoundary()

    def test_01_compiler_resolves_suite_relative_target(self):
        """Compiler must resolve canonical skills and scripts within AcademicSuite repository."""
        target = ".agents/skills/apa-reporting/SKILL.md"
        resolved, scope = self.compiler.resolve_target_component_path(target)
        self.assertIsNotNone(resolved)
        self.assertTrue(os.path.isfile(resolved))
        self.assertIn("apa-reporting", resolved)
        self.assertIn(scope, ("SUITE_REPO", "SUITE_ROOT"))

    def test_02_compiler_resolves_project_relative_target(self):
        """Compiler must resolve workspace scripts located in an external client project directory."""
        with tempfile.TemporaryDirectory() as tmp_project:
            code_dir = os.path.join(tmp_project, "02_analysis_code")
            os.makedirs(code_dir, exist_ok=True)
            script_file = os.path.join(code_dir, "generate_report.py")
            with open(script_file, "w", encoding="utf-8") as f:
                f.write("# sample project script\n")

            # Resolve using active_project_dir parameter
            resolved, scope = self.compiler.resolve_target_component_path(
                "02_analysis_code/generate_report.py",
                active_project_dir=tmp_project
            )
            self.assertIsNotNone(resolved)
            self.assertEqual(os.path.abspath(resolved), os.path.abspath(script_file))
            self.assertEqual(scope, "PROJECT_WORKSPACE")

    def test_03_compiler_resolves_parameterized_targets(self):
        """Compiler must expand ${WORKSPACE_ROOT} and ${SUITE_ROOT} tokens."""
        with tempfile.TemporaryDirectory() as tmp_project:
            code_dir = os.path.join(tmp_project, "02_analysis_code")
            os.makedirs(code_dir, exist_ok=True)
            script_file = os.path.join(code_dir, "custom_calc.py")
            with open(script_file, "w", encoding="utf-8") as f:
                f.write("# custom code\n")

            resolved_ws, _ = self.compiler.resolve_target_component_path(
                "${WORKSPACE_ROOT}/02_analysis_code/custom_calc.py",
                active_project_dir=tmp_project
            )
            self.assertIsNotNone(resolved_ws)
            self.assertEqual(os.path.abspath(resolved_ws), os.path.abspath(script_file))

            resolved_suite, _ = self.compiler.resolve_target_component_path(
                "${SUITE_ROOT}/.agents/skills/apa-reporting/SKILL.md"
            )
            self.assertIsNotNone(resolved_suite)
            self.assertTrue(os.path.isfile(resolved_suite))

    def test_04_compiler_resolves_absolute_target(self):
        """Compiler must preserve and resolve existing absolute paths without stripping leading slashes."""
        with tempfile.NamedTemporaryFile(suffix=".py") as tf:
            tf.write(b"# temp script\n")
            tf.flush()

            resolved, scope = self.compiler.resolve_target_component_path(tf.name)
            self.assertIsNotNone(resolved)
            self.assertEqual(os.path.abspath(resolved), os.path.abspath(tf.name))
            self.assertEqual(scope, "ABSOLUTE_PATH")

    def test_05_all_agent_hooks_use_portable_resolution(self):
        """All 31 agent hooks.json must use dynamic portable path resolution without hardcoded host usernames."""
        hooks_files = sorted(glob.glob(os.path.join(ROOT_DIR, ".agents", "agents", "*", "hooks.json")))
        self.assertEqual(len(hooks_files), 31, "All 31 registered agents must possess hooks.json")

        for hf in hooks_files:
            agent_name = os.path.basename(os.path.dirname(hf))
            with open(hf, "r", encoding="utf-8") as f:
                content = f.read()

            # Must NOT contain hardcoded host path with /home/saber-ghaderi
            self.assertNotIn("/home/saber-ghaderi", content, f"Hardcoded path found in {hf}")

            # Must contain portable plugin expansion
            self.assertIn("~/.gemini/config/plugins/academic-suite/agents/", content,
                          f"Portable plugin candidate missing in {hf}")
            # Must support ACADEMIC_SUITE_REPO environment variable
            self.assertIn("ACADEMIC_SUITE_REPO", content, f"Environment variable fallback missing in {hf}")

    def test_06_subagent_dispatch_injects_dynamic_directory_anchors(self):
        """AcademicAdaptiveContextBoundary must inject dynamic directory anchors on subagent dispatch."""
        subagents = [{
            "TypeName": "trajectory-analyzer",
            "Role": "Observable Trajectory Reconstructor",
            "Prompt": "Reconstruct execution history"
        }]

        enriched = self.boundary.enrich_subagent_dispatch(subagents)
        self.assertEqual(len(enriched), 1)
        prompt = enriched[0]["Prompt"]

        self.assertIn("📂 ACTIVE ENVIRONMENT DIRECTORY ANCHORS:", prompt)
        self.assertIn("- **SUITE_REPO_DIR**:", prompt)
        self.assertIn("- **CANONICAL_LEARNING_DIR**:", prompt)
        self.assertIn("- **ACTIVE_PROJECT_DIR**:", prompt)
        self.assertIn("NEVER perform recursive scans (find_by_name) on $HOME", prompt)

        # Dynamic evaluated values, not empty placeholders
        suite_repo = resolve_canonical_repo_root()
        learning_dir = get_canonical_learning_dir()
        self.assertIn(suite_repo, prompt)
        self.assertIn(learning_dir, prompt)

    def test_07_learning_agent_prompts_forbid_recursive_home_scans(self):
        """All 5 learning subagents must explicitly forbid recursive searches on $HOME in agent.md."""
        learning_agents = [
            "trajectory-analyzer",
            "behavior-analyst",
            "knowledge-curator",
            "skill-evolver",
            "evaluation-agent"
        ]

        for agent in learning_agents:
            agent_md = os.path.join(ROOT_DIR, ".agents", "agents", agent, "agent.md")
            self.assertTrue(os.path.isfile(agent_md), f"agent.md missing for {agent}")
            with open(agent_md, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertIn("Ban on Recursive Home Directory Scans", content,
                          f"Ban on recursive home scans missing in {agent}/agent.md")
            self.assertIn("find_by_name", content,
                          f"find_by_name boundary missing in {agent}/agent.md")


if __name__ == "__main__":
    unittest.main()
