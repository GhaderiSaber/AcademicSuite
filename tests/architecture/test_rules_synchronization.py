#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_rules_synchronization.py

Automated Architectural Verification Suite for Rules Synchronization
and Global Plugin Unification.

Verifies:
1. Master plugin rules file exists and strictly respects the 24,000-byte (24 KB) Antigravity ceiling.
2. Root AGENTS.md is a valid relative symlink to the master plugin rule file.
3. All 26 Constitutional Directives (0 through 25, plus sub-directives 3.1, 4.1, 7.1, 12.1) are present.
4. Chapter 4 and Chapter 5 (prose-only invariant) and Digital Saber specifications are present.
5. Global plugin installation path (~/.gemini/config/plugins/academic-suite/rules/AGENTS.md) resolves to the canonical file.
6. Workspace .agents/rules/ directory is clean and contains only canonical modular rules.
"""

import os
import re
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
PLUGIN_RULES_FILE = os.path.join(AGENTS_DIR, "plugins", "academic-suite", "rules", "AGENTS.md")
ROOT_AGENTS_FILE = os.path.join(ROOT_DIR, "AGENTS.md")
GLOBAL_PLUGIN_DIR = os.path.expanduser("~/.gemini/config/plugins/academic-suite")


def test_01_plugin_rules_file_exists_and_under_size_limit():
    """Assert master plugin AGENTS.md exists and is strictly <= 24,000 bytes."""
    assert os.path.isfile(PLUGIN_RULES_FILE), f"Missing plugin rule file: {PLUGIN_RULES_FILE}"
    byte_size = os.path.getsize(PLUGIN_RULES_FILE)
    max_bytes = 24000
    assert byte_size <= max_bytes, (
        f"Plugin AGENTS.md exceeds Antigravity per-file budget: {byte_size} bytes > {max_bytes} bytes"
    )
    assert byte_size > 5000, f"Plugin AGENTS.md is unexpectedly small: {byte_size} bytes"


def test_02_root_agents_md_symlink_integrity():
    """Assert repository root AGENTS.md is a symlink resolving to the master plugin rule."""
    assert os.path.exists(ROOT_AGENTS_FILE), "Root AGENTS.md must exist"
    assert os.path.islink(ROOT_AGENTS_FILE), "Root AGENTS.md must be a symlink to prevent rule drift"
    
    target_link = os.readlink(ROOT_AGENTS_FILE)
    expected_rel = ".agents/plugins/academic-suite/rules/AGENTS.md"
    assert target_link == expected_rel, f"Expected symlink target {expected_rel}, got: {target_link}"
    
    real_root = os.path.realpath(ROOT_AGENTS_FILE)
    real_plugin = os.path.realpath(PLUGIN_RULES_FILE)
    assert real_root == real_plugin, f"Root AGENTS.md ({real_root}) must resolve to {real_plugin}"


def test_03_all_26_constitutional_directives_present():
    """Assert all Constitutional Directives (0 through 25 + sub-directives) are present."""
    with open(PLUGIN_RULES_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify all primary directives from 0 through 25
    expected_directives = [
        "Directive 0",
        "Directive 1",
        "Directive 2",
        "Directive 3",
        "Directive 3.1",
        "Directive 4",
        "Directive 4.1",
        "Directive 5",
        "Directive 6",
        "Directive 7",
        "Directive 7.1",
        "Directive 8",
        "Directive 9",
        "Directive 10",
        "Directive 11",
        "Directive 12",
        "Directive 12.1",
        "Directive 13",
        "Directive 14",
        "Directive 15",
        "Directive 16",
        "Directive 17",
        "Directive 18",
        "Directive 19",
        "Directive 20",
        "Directive 21",
        "Directive 22",
        "Directive 23",
        "Directive 24",
        "Directive 25",
    ]

    missing = []
    for d in expected_directives:
        if d not in content:
            missing.append(d)

    assert not missing, f"Missing constitutional directives in plugin AGENTS.md: {missing}"


def test_04_chapter_and_consultancy_specifications_present():
    """Assert Chapter 4, Chapter 5 (prose-only), and Digital Saber specifications exist."""
    with open(PLUGIN_RULES_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    assert "## 1. Radical Honesty & Pipeline Enforcement" in content
    assert "## 2. Constitutional Directives (0 through 25)" in content
    assert "## 3. Persian Academic Typography & Font Standards" in content
    assert "## 4. Chapter 4 & 5 Empirical Specifications" in content
    assert "Chapter 4 (Findings" in content
    assert "Chapter 5 (Discussion" in content
    assert "Strict Prose-Only Invariant" in content
    assert "## 5. Digital Saber AI Twin & Consultancy Standards" in content


def test_05_global_plugin_symlink_validity():
    """Assert global plugin installation (~/.gemini/config/plugins/academic-suite) points to repo."""
    if os.path.exists(GLOBAL_PLUGIN_DIR):
        global_rule = os.path.join(GLOBAL_PLUGIN_DIR, "rules", "AGENTS.md")
        assert os.path.isfile(global_rule), f"Global plugin rule file must exist: {global_rule}"
        assert os.path.realpath(global_rule) == os.path.realpath(PLUGIN_RULES_FILE), (
            f"Global plugin rule {os.path.realpath(global_rule)} does not resolve to {os.path.realpath(PLUGIN_RULES_FILE)}"
        )


def test_06_clean_rules_directory():
    """Assert workspace .agents/rules/ contains only approved canonical modular files."""
    rules_dir = os.path.join(AGENTS_DIR, "rules")
    assert os.path.isdir(rules_dir), "Rules directory must exist"
    
    files = sorted(os.listdir(rules_dir))
    expected_files = {
        "01_core_governance_invariants.md",
        "02_git_and_workspace_lifecycle.md",
        "03_apa7_and_academic_typography.md",
        "04_persian_openxml_and_presentation.md",
        "05_multi_agent_orchestration_and_delegation.md",
        "06_chapter4_and_statistical_modeling.md",
        "07_chapter5_prose_and_theoretical_synthesis.md",
        "08_digital_saber_twin_consultancy.md",
        "academic-integrity.md",
        "data-integrity.md",
        "project-conventions.md",
    }
    
    actual_files = set(f for f in files if f.endswith(".md"))
    unexpected = actual_files - expected_files
    assert not unexpected, f"Unexpected/obsolete rule files in .agents/rules/: {unexpected}"
    missing = expected_files - actual_files
    assert not missing, f"Missing canonical rule files in .agents/rules/: {missing}"
