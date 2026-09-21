#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_repository_syntax_integrity.py — Repository-Wide Python Syntax & AST Integrity

Verifies that every single Python file across the entire repository (440+ files)
is syntactically valid according to Python's AST parser and compileall engine,
with zero SyntaxErrors and zero invalid escape sequence warnings (SyntaxWarnings).
"""

import os
import sys
import ast
import time
import warnings
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXCLUDED_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "node_modules"}


class TestRepositorySyntaxIntegrity(unittest.TestCase):
    """Guarantees 100% Python syntax and AST integrity across all repository files."""

    @classmethod
    def setUpClass(cls):
        cls.py_files = []
        for root, dirs, files in os.walk(ROOT_DIR):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            for f in files:
                if f.endswith(".py"):
                    cls.py_files.append(os.path.join(root, f))
        cls.py_files.sort()

    def test_01_at_least_400_python_files_discovered(self):
        """Asserts that repository discovery found the expected comprehensive Python codebase."""
        self.assertGreater(
            len(self.py_files),
            400,
            f"Expected at least 400 Python files in repository, found {len(self.py_files)}",
        )

    def test_02_all_python_files_ast_parse_cleanly(self):
        """Asserts that every Python file in the repository parses into a valid AST without warnings or errors."""
        failures = []
        with warnings.catch_warnings(record=True) as recorded_warnings:
            warnings.filterwarnings("error")
            for py_path in self.py_files:
                try:
                    with open(py_path, "r", encoding="utf-8") as fh:
                        source = fh.read()
                    ast.parse(source, filename=py_path)
                except Exception as e:
                    rel_path = os.path.relpath(py_path, ROOT_DIR)
                    failures.append(f"{rel_path}: {type(e).__name__}: {e}")

        if failures:
            error_report = "\n".join(f"  • {fail}" for fail in failures)
            self.fail(
                f"AST parsing failed on {len(failures)} file(s) across the repository:\n{error_report}"
            )

    def test_03_all_python_files_compile_cleanly(self):
        """Asserts that py_compile successfully generates bytecode for every Python file."""
        import py_compile

        compile_failures = []
        for py_path in self.py_files:
            try:
                py_compile.compile(py_path, doraise=True)
            except Exception as e:
                rel_path = os.path.relpath(py_path, ROOT_DIR)
                compile_failures.append(f"{rel_path}: {type(e).__name__}: {e}")

        if compile_failures:
            error_report = "\n".join(f"  • {fail}" for fail in compile_failures)
            self.fail(
                f"Bytecode compilation failed on {len(compile_failures)} file(s):\n{error_report}"
            )


if __name__ == "__main__":
    unittest.main()
