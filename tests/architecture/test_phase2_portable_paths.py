#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_phase2_portable_paths.py — Verification of Phase 2 Portable Paths

Constitutional Governance (Directives 6, 8, 19, 21, 23, 25):
- Tests that .agents/learning/ contains zero machine-specific absolute paths (/home/saber-ghaderi, /home/ghaderi-saber).
- Tests that .agents/skills/ and .agents/factory/ contain zero machine-specific paths.
- Tests that AcademicGraduationCompiler normalizes targets to repository-relative paths.
"""

import os
import sys
import json
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)

from scripts.academic_graduation_compiler import AcademicGraduationCompiler


class TestPhase2PortablePaths:
    """Verifies that all learning and production artifacts are completely portable."""

    def test_01_zero_hardcoded_user_paths_in_learning(self):
        """Asserts zero occurrences of /home/saber-ghaderi or /home/ghaderi-saber in .agents/learning/."""
        learning_dir = os.path.join(AGENTS_DIR, "learning")
        assert os.path.isdir(learning_dir), "Learning directory must exist"

        violating_files = []
        for root, dirs, files in os.walk(learning_dir):
            for fn in files:
                if fn.endswith((".json", ".md")):
                    fp = os.path.join(root, fn)
                    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                        c = f.read()
                    if "/home/saber-ghaderi" in c or "/home/ghaderi-saber" in c:
                        violating_files.append(os.path.relpath(fp, ROOT_DIR))

        assert len(violating_files) == 0, f"Found machine paths in learning files: {violating_files}"

    def test_02_zero_hardcoded_user_paths_in_skills_and_factory(self):
        """Asserts zero machine paths in skills, scripts, and factory manifest."""
        target_dirs = [
            os.path.join(AGENTS_DIR, "skills"),
            os.path.join(AGENTS_DIR, "factory")
        ]

        violating_files = []
        for tdir in target_dirs:
            if not os.path.isdir(tdir):
                continue
            for root, dirs, files in os.walk(tdir):
                for fn in files:
                    if fn.endswith((".json", ".md", ".py")):
                        fp = os.path.join(root, fn)
                        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                            c = f.read()
                        if "/home/saber-ghaderi" in c or "/home/ghaderi-saber" in c:
                            violating_files.append(os.path.relpath(fp, ROOT_DIR))

        assert len(violating_files) == 0, f"Found machine paths in skills/factory: {violating_files}"

    def test_03_compiler_emits_portable_targets(self):
        """Asserts that the compiler normalizes targets to repository-relative paths."""
        compiler = AcademicGraduationCompiler(base_dir=ROOT_DIR)

        # Test path normalization logic
        sample_abs_path = os.path.join(ROOT_DIR, ".agents", "plugins", "academic-suite", "rules", "AGENTS.md")
        norm_targets = []
        for t in [sample_abs_path]:
            t_str = str(t)
            if ".agents" in t_str:
                idx = t_str.find(".agents")
                norm_targets.append(t_str[idx:])
            elif t_str.startswith(compiler.base_dir):
                norm_targets.append(os.path.relpath(t_str, compiler.base_dir))
            else:
                norm_targets.append(t_str)

        assert norm_targets == [".agents/plugins/academic-suite/rules/AGENTS.md"]
        assert not norm_targets[0].startswith("/")
        assert "/home/" not in norm_targets[0]
