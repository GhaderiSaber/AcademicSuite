#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/scripts/normalize_portable_paths.py — Universal Machine-Path Normalization Engine

Constitutional Invariant (Directives 6, 19, 21, 25):
- Converts hardcoded local machine paths (/home/saber-ghaderi/..., /home/ghaderi-saber/...)
  into portable, machine-independent tokens (${WORKSPACE_ROOT}, ${REPO_ROOT}, ${APP_DATA_DIR}, .agents/...).
- Guarantees repository portability across different developer accounts, CI environments, and submodules.

Usage:
    python3 .agents/scripts/normalize_portable_paths.py --dry-run
    python3 .agents/scripts/normalize_portable_paths.py --execute
"""

import os
import sys
import re
import json
import argparse
from typing import Dict, Any, List, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
LEARNING_DIR = os.path.join(AGENTS_DIR, "learning")


def normalize_text_content(text: str) -> Tuple[str, int]:
    """
    Normalizes hardcoded machine paths in text to portable relative paths and environment tokens.
    Returns (normalized_text, total_replacement_count).
    """
    replacements = 0

    # 1. Any path containing .agents/
    pat_agents = re.compile(r'(?:file:///home/(?:saber-ghaderi|ghaderi-saber)|/home/(?:saber-ghaderi|ghaderi-saber))[^\s\"\'\`\)\>\]\\]*?\.agents/([^\s\"\'\`\)\>\]\\]*)')
    new_text, n = pat_agents.subn(r'.agents/\1', text)
    replacements += n

    # 2. Paths pointing into project taxonomy directories
    tier_dirs = "01_raw_inputs|02_analysis_code|03_deliverables|04_references_and_lit"
    pat_tiers = re.compile(rf'(?:file:///home/(?:saber-ghaderi|ghaderi-saber)|/home/(?:saber-ghaderi|ghaderi-saber))/My(?:%20|[ ])Work/[^/\"\'\`\)\>\]\\]+/((?:{tier_dirs})[^\s\"\'\`\)\>\]\\]*)')
    new_text, n = pat_tiers.subn(r'\1', new_text)
    replacements += n

    # 3. Brain session directory paths
    pat_gemini = re.compile(r'(?:file:///home/(?:saber-ghaderi|ghaderi-saber)|/home/(?:saber-ghaderi|ghaderi-saber))/\.gemini/([^\s\"\'\`\)\>\]\\]*)')
    new_text, n = pat_gemini.subn(r'${APP_DATA_DIR}/\1', new_text)
    replacements += n

    # 4. Repo root paths (AcademicSuite)
    pat_repo = re.compile(r'(?:file:///home/(?:saber-ghaderi|ghaderi-saber)|/home/(?:saber-ghaderi|ghaderi-saber))/Desktop/AcademicSuite/([^\s\"\'\`\)\>\]\\]*)')
    new_text, n = pat_repo.subn(r'\1', new_text)
    replacements += n

    # 5. Client workspace roots (My Work/Client or Desktop/Projects)
    pat_client = re.compile(r'(?:file:///home/(?:saber-ghaderi|ghaderi-saber)|/home/(?:saber-ghaderi|ghaderi-saber))/My(?:%20|[ ])Work/[^/\"\'\`\)\>\]\\]*')
    new_text, n = pat_client.subn(r'${WORKSPACE_ROOT}', new_text)
    replacements += n

    pat_mywork = re.compile(r'(?:file:///home/(?:saber-ghaderi|ghaderi-saber)|/home/(?:saber-ghaderi|ghaderi-saber))/My(?:%20|[ ])Work')
    new_text, n = pat_mywork.subn(r'${WORKSPACE_ROOT}', new_text)
    replacements += n

    pat_desktop = re.compile(r'(?:file:///home/(?:saber-ghaderi|ghaderi-saber)|/home/(?:saber-ghaderi|ghaderi-saber))/Desktop/[^\s\"\'\`\)\>\]\\]*')
    new_text, n = pat_desktop.subn(r'${WORKSPACE_ROOT}', new_text)
    replacements += n

    # 6. Any other remaining /home/(saber-ghaderi|ghaderi-saber) paths
    pat_remaining = re.compile(r'(?:file:///home/(?:saber-ghaderi|ghaderi-saber)|/home/(?:saber-ghaderi|ghaderi-saber))[^\s\"\'\`\)\>\]\\]*')
    new_text, n = pat_remaining.subn(r'${WORKSPACE_ROOT}', new_text)
    replacements += n

    return new_text, replacements


def process_file(file_path: str, dry_run: bool = True) -> Tuple[bool, int, str]:
    """Processes a single file. Returns (was_modified, replacement_count, error_msg)."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            original_content = f.read()
    except Exception as e:
        return False, 0, f"Read error: {e}"

    if "/home/saber-ghaderi" not in original_content and "/home/ghaderi-saber" not in original_content:
        return False, 0, ""

    normalized_content, count = normalize_text_content(original_content)
    if count == 0 or normalized_content == original_content:
        return False, 0, ""

    # JSON validation: if JSON, ensure normalized content parses cleanly
    if file_path.endswith(".json"):
        try:
            json.loads(normalized_content)
        except Exception as e_json:
            return False, 0, f"JSON parse error after normalization: {e_json}"

    if not dry_run:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(normalized_content)
        except Exception as e_write:
            return False, 0, f"Write error: {e_write}"

    return True, count, ""


def run_normalization(dry_run: bool = True) -> Dict[str, Any]:
    """Runs path normalization across target directories."""
    target_dirs = [
        os.path.join(AGENTS_DIR, "learning"),
        os.path.join(AGENTS_DIR, "factory")
    ]
    target_specific_files = [
        os.path.join(AGENTS_DIR, "skills", "digital-twin-academic-consultant", "scripts", "bot_config.json"),
        os.path.join(AGENTS_DIR, "skills", "persian-literature-review-builder", "references", "learned_invariants.md")
    ]

    files_inspected = 0
    files_modified = []
    errors = []
    total_replacements = 0

    # Scan directories
    for tdir in target_dirs:
        if not os.path.isdir(tdir):
            continue
        for root, dirs, files in os.walk(tdir):
            if ".git" in root or "__pycache__" in root:
                continue
            for fn in files:
                if fn.endswith((".json", ".md")):
                    fpath = os.path.join(root, fn)
                    files_inspected += 1
                    mod, n, err = process_file(fpath, dry_run=dry_run)
                    if err:
                        errors.append((fpath, err))
                    elif mod:
                        files_modified.append(os.path.relpath(fpath, ROOT_DIR))
                        total_replacements += n

    # Scan specific standalone files
    for sf in target_specific_files:
        if os.path.isfile(sf):
            files_inspected += 1
            mod, n, err = process_file(sf, dry_run=dry_run)
            if err:
                errors.append((sf, err))
            elif mod:
                files_modified.append(os.path.relpath(sf, ROOT_DIR))
                total_replacements += n

    return {
        "dry_run": dry_run,
        "files_inspected": files_inspected,
        "files_modified_count": len(files_modified),
        "total_replacements": total_replacements,
        "sample_modified_files": files_modified[:15],
        "errors_count": len(errors),
        "errors": errors[:5]
    }


def main():
    parser = argparse.ArgumentParser(description="Universal Machine-Path Normalization Engine")
    parser.add_argument("--execute", action="store_true", help="Execute file mutations (default is dry-run)")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Perform dry-run")
    args = parser.parse_args()

    dry_run = not args.execute
    print(f"=== Universal Path Normalization Engine (Dry-Run: {dry_run}) ===")
    report = run_normalization(dry_run=dry_run)
    print(json.dumps(report, indent=2))
    if dry_run:
        print("\nTo apply file mutations, run: python3 .agents/scripts/normalize_portable_paths.py --execute")


if __name__ == "__main__":
    main()
