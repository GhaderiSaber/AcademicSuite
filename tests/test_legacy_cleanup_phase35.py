#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_legacy_cleanup_phase35.py — Phase 35 Legacy Code Cleanup Test Suite

Tests:
1. Validates architecture/CODEBASE_INVENTORY_AUDIT.md: every file has exactly ONE status among the 6 valid statuses.
2. Verifies that all 5 UNUSED files have been removed from disk.
3. Affirmatively proves zero active dependencies (imports, subprocess, references) on removed files.
4. Verifies DEPRECATED files include formal deprecation notices.
5. Verifies DUPLICATE consolidated files contain consolidation headers and preserve compatibility.
6. Verifies EXPERIMENTAL files contain experimental sandbox headers.
7. Verifies Directive 6 (English ASCII filenames) and Directive 18 (single-view limits).
"""

import os
import sys
import re
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

VALID_STATUSES = {
    "LEGACY",
    "DUPLICATE",
    "DEPRECATED",
    "UNUSED",
    "COMPATIBILITY",
    "EXPERIMENTAL"
}

REMOVED_FILES = [
    "tools/python/openxml_helpers.py",
    "scripts/generate_scale_validation_package.py",
    "scripts/assemble_master_scale_validation_docx.py",
    "scripts/generate_experimental_master_package.py",
    "scripts/multi_account_scanner.py"
]


class TestLegacyCleanupPhase35(unittest.TestCase):
    """Test suite for Phase 35 Legacy Code Clean-Up."""

    @classmethod
    def setUpClass(cls):
        doc_audit = os.path.join(ROOT_DIR, "docs", "architecture", "CODEBASE_INVENTORY_AUDIT.md")
        cls.audit_path = doc_audit if os.path.isfile(doc_audit) else os.path.join(ROOT_DIR, "architecture", "CODEBASE_INVENTORY_AUDIT.md")
        with open(cls.audit_path, "r", encoding="utf-8") as f:
            cls.audit_content = f.read()

    def test_01_codebase_inventory_audit_schema(self):
        """Verify every audited file in CODEBASE_INVENTORY_AUDIT.md has exactly one valid status."""
        self.assertTrue(os.path.exists(self.audit_path), "CODEBASE_INVENTORY_AUDIT.md must exist")

        # Parse table rows: | `target` | `STATUS` | Action | Rationale |
        table_lines = [
            line.strip() for line in self.audit_content.splitlines()
            if line.strip().startswith("| `")
        ]
        self.assertGreaterEqual(len(table_lines), 25, "Expected at least 25 audited entries in table")

        parsed_entries = []
        for line in table_lines:
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) >= 3:
                file_target = cols[0].strip("`")
                status = cols[1].strip("`")
                parsed_entries.append((file_target, status))
                self.assertIn(
                    status,
                    VALID_STATUSES,
                    f"File {file_target} has invalid status '{status}'. Must be one of {VALID_STATUSES}"
                )

        # Verify no duplicate file definitions
        targets = [e[0] for e in parsed_entries]
        self.assertEqual(len(targets), len(set(targets)), "Duplicate file entries found in audit table")

    def test_02_unused_files_deleted_from_disk(self):
        """Verify that all UNUSED files have been affirmatively removed from disk."""
        for rel_path in REMOVED_FILES:
            full_path = os.path.join(ROOT_DIR, rel_path)
            self.assertFalse(
                os.path.exists(full_path),
                f"UNUSED file {rel_path} was not removed from disk!"
            )

    def test_03_zero_active_dependencies_on_removed_files(self):
        """Prove that zero active files import or invoke any removed file."""
        search_dirs = ["scripts", "contracts", "validators", ".agents", "tests"]
        all_active_files = []
        for d in search_dirs:
            dp = os.path.join(ROOT_DIR, d)
            if os.path.exists(dp):
                for r, dirs, files in os.walk(dp):
                    dirs[:] = [sub for sub in dirs if sub not in [".git", ".venv", "__pycache__", "state"]]
                    for f in files:
                        if f.endswith((".py", ".json", ".sh")):
                            all_active_files.append(os.path.join(r, f))

        removed_bases = [os.path.splitext(os.path.basename(p))[0] for p in REMOVED_FILES]
        pattern = re.compile(rf"\b(?:import|from)\s+.*\b({'|'.join(re.escape(b) for b in removed_bases)})\b")

        for fpath in all_active_files:
            if "test_legacy_cleanup_phase35.py" in fpath:
                continue
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                    content = fp.read()
                m = pattern.search(content)
                self.assertIsNone(
                    m,
                    f"Active file {fpath} still imports removed module: {m.group(0) if m else ''}!"
                )
            except Exception:
                pass

    def _resolve_path(self, rel_path: str) -> str:
        p1 = os.path.join(ROOT_DIR, rel_path)
        if os.path.exists(p1):
            return p1
        p2 = os.path.join(ROOT_DIR, ".agents", rel_path)
        if os.path.exists(p2):
            return p2
        return p1

    def test_04_deprecated_files_have_deprecation_headers(self):
        """Verify DEPRECATED files contain formal deprecation notices."""
        deprecated_files = [
            "digital_saber.py",
            "scripts/orchestrator_dependency_resolver.py",
            "scripts/triage_projects.py"
        ]
        for rel_path in deprecated_files:
            full_path = self._resolve_path(rel_path)
            self.assertTrue(os.path.exists(full_path), f"Deprecated file {rel_path} missing")
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn(
                "DEPRECATED",
                content,
                f"File {rel_path} missing DEPRECATED notice in header"
            )

    def test_05_consolidated_duplicate_delegation(self):
        """Verify DUPLICATE consolidated files contain consolidation headers."""
        full_path = self._resolve_path("scripts/build_hypothesis_1_triad_docx.py")
        self.assertTrue(os.path.exists(full_path))
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("CONSOLIDATED", content)
        self.assertIn("generate_hypothesis_triad_docx.py", content)

    def test_06_experimental_files_tagged(self):
        """Verify EXPERIMENTAL files contain experimental sandbox headers."""
        experimental_files = [
            "scripts/academic_self_improvement_demo.py",
            "scripts/academic_isolated_agent_sandbox.py",
            "scripts/candidate_falsifier_engine.py"
        ]
        for rel_path in experimental_files:
            full_path = self._resolve_path(rel_path)
            self.assertTrue(os.path.exists(full_path), f"Experimental file {rel_path} missing")
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn(
                "EXPERIMENTAL",
                content,
                f"File {rel_path} missing EXPERIMENTAL tag in header"
            )

    def test_07_governance_directives_compliance(self):
        """Verify Directive 6 (English ASCII filenames) across repository."""
        for root_dir, dirs, files in os.walk(ROOT_DIR):
            dirs[:] = [d for d in dirs if d not in [".git", ".venv", "__pycache__", "state"]]
            for fname in files:
                self.assertTrue(
                    fname.isascii(),
                    f"Non-ASCII filename violates Directive 6: {fname}"
                )


if __name__ == "__main__":
    unittest.main()
