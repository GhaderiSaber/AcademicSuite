#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/scripts/consolidate_learning_lessons.py — Consolidation and Archival Engine for Learning Lessons

Purges runaway duplicate lesson files and self-pollution artifacts from
.agents/learning/knowledge/lessons/, safely archiving them into structured archive directories
while preserving all semantic curated lessons and unique genuine feedback.

Usage:
    python3 .agents/scripts/consolidate_learning_lessons.py --dry-run
    python3 .agents/scripts/consolidate_learning_lessons.py --execute
"""

import os
import sys
import re
import json
import shutil
import argparse
from collections import defaultdict
from typing import Dict, Any, List, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LEARNING_DIR = os.path.join(ROOT_DIR, ".agents", "learning")
LESSONS_DIR = os.path.join(LEARNING_DIR, "knowledge", "lessons")
ARCHIVE_BASE = os.path.join(LEARNING_DIR, "archive")

ARCHIVE_VALIDATOR = os.path.join(ARCHIVE_BASE, "validator_fails_sept2026")
ARCHIVE_SELF_POLLUTION = os.path.join(ARCHIVE_BASE, "self_pollution_sept2026")
ARCHIVE_FEEDBACK_DUPS = os.path.join(ARCHIVE_BASE, "user_feedback_duplicates_sept2026")


def classify_lessons(lessons_dir: str) -> Dict[str, List[str]]:
    """Classifies all lesson JSON files into canonical categories."""
    categories = {
        "curated_semantic": [],
        "validator_fail_duplicates": [],
        "adaptive_context_self_pollution": [],
        "genuine_feedback": [],
        "corrupt": []
    }

    if not os.path.isdir(lessons_dir):
        return categories

    for fname in sorted(os.listdir(lessons_dir)):
        if not fname.endswith(".json") or fname.startswith("."):
            continue

        fpath = os.path.join(lessons_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            categories["corrupt"].append(fpath)
            continue

        # 1. Semantic curated lessons (e.g. LSN-2026-NAME)
        is_hashed_name = bool(re.match(r"^LSN-\d{8}-[a-zA-Z0-9]{6}\.json$", fname))
        if not is_hashed_name:
            categories["curated_semantic"].append(fpath)
            continue

        wh = data.get("what_happened", "")
        if not wh and "diagnosis" in data and isinstance(data["diagnosis"], dict):
            wh = data["diagnosis"].get("what_happened", "")
        wh_str = str(wh)

        # 2. Validator fail runaway duplicates
        if (
            "Stage Validator Gate" in wh_str
            or data.get("what_behavior_caused_outcome") == "GENERAL_METHODOLOGICAL_DEFECT"
            or (isinstance(data.get("diagnosis"), dict) and data["diagnosis"].get("behavior_caused_outcome") == "GENERAL_METHODOLOGICAL_DEFECT")
        ):
            categories["validator_fail_duplicates"].append(fpath)
            continue

        # 3. Adaptive context self-pollution
        if "DETERMINISTIC ADAPTIVE CONTEXT" in wh_str or "DETERMINISTIC ADAPTIVE CONTEXT" in json.dumps(data, ensure_ascii=False):
            categories["adaptive_context_self_pollution"].append(fpath)
            continue

        # 4. Genuine feedback or other unique lesson
        categories["genuine_feedback"].append(fpath)

    return categories


def deduplicate_feedback(feedback_paths: List[str]) -> Tuple[List[str], List[str]]:
    """Deduplicates genuine feedback lessons, keeping one exemplar per signature."""
    kept = []
    duplicates = []
    signatures = {}

    for fpath in feedback_paths:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            duplicates.append(fpath)
            continue

        wh = data.get("what_happened", "")
        if not wh and "diagnosis" in data and isinstance(data["diagnosis"], dict):
            wh = data["diagnosis"].get("what_happened", "")
        desired = data.get("desired_behavior", "")
        agent = data.get("target_agent", "")

        sig = (str(agent).strip(), str(desired).strip()[:120], str(wh).strip()[:120])
        if sig in signatures:
            duplicates.append(fpath)
        else:
            signatures[sig] = fpath
            kept.append(fpath)

    return kept, duplicates


def rebuild_index(lessons_dir: str, remaining_files: List[str]):
    """Rebuilds the index.jsonl with only currently active lessons in lessons_dir."""
    index_file = os.path.join(lessons_dir, "index.jsonl")
    entries = []

    for fpath in remaining_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            fname = os.path.basename(fpath)
            lesson_id = data.get("lesson_id") or os.path.splitext(fname)[0]
            entry = {
                "lesson_id": lesson_id,
                "lesson_type": data.get("lesson_type", "WHAT_NOT_TO_DO"),
                "trigger_source": data.get("trigger_source", "MANUAL"),
                "scope": data.get("scope", "DOMAIN_WIDE"),
                "related_skills": data.get("related_skills", []),
                "source_experience_id": data.get("source_experience_id", ""),
                "is_active_behavior": data.get("is_active_behavior", True),
                "status": data.get("status", "VALIDATED"),
                "created_at": data.get("created_at", ""),
                "filepath": os.path.relpath(fpath, ROOT_DIR)
            }
            entries.append(entry)
        except Exception:
            pass

    # Sort entries by lesson_id
    entries.sort(key=lambda x: x["lesson_id"])
    with open(index_file, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def execute_consolidation(dry_run: bool = True) -> Dict[str, Any]:
    """Executes the consolidation and archival protocol."""
    classified = classify_lessons(LESSONS_DIR)
    feedback_kept, feedback_dups = deduplicate_feedback(classified["genuine_feedback"])

    to_archive_validator = classified["validator_fail_duplicates"]
    to_archive_self_pollution = classified["adaptive_context_self_pollution"]
    to_archive_feedback_dups = feedback_dups
    curated_count = len(classified["curated_semantic"])
    kept_feedback_count = len(feedback_kept)

    total_initial = sum(len(v) for v in classified.values())
    total_to_archive = len(to_archive_validator) + len(to_archive_self_pollution) + len(to_archive_feedback_dups)
    total_remaining = curated_count + kept_feedback_count

    report = {
        "dry_run": dry_run,
        "total_initial_lessons": total_initial,
        "curated_semantic_kept": curated_count,
        "genuine_feedback_kept": kept_feedback_count,
        "total_active_remaining": total_remaining,
        "archived_validator_fails": len(to_archive_validator),
        "archived_self_pollution": len(to_archive_self_pollution),
        "archived_feedback_duplicates": len(to_archive_feedback_dups),
        "total_archived": total_to_archive
    }

    if dry_run:
        return report

    # Create target archive directories
    os.makedirs(ARCHIVE_VALIDATOR, exist_ok=True)
    os.makedirs(ARCHIVE_SELF_POLLUTION, exist_ok=True)
    os.makedirs(ARCHIVE_FEEDBACK_DUPS, exist_ok=True)

    # Move files safely
    for src in to_archive_validator:
        dst = os.path.join(ARCHIVE_VALIDATOR, os.path.basename(src))
        shutil.move(src, dst)

    for src in to_archive_self_pollution:
        dst = os.path.join(ARCHIVE_SELF_POLLUTION, os.path.basename(src))
        shutil.move(src, dst)

    for src in to_archive_feedback_dups:
        dst = os.path.join(ARCHIVE_FEEDBACK_DUPS, os.path.basename(src))
        shutil.move(src, dst)

    # Rebuild index.jsonl with remaining files
    remaining_files = classified["curated_semantic"] + feedback_kept
    rebuild_index(LESSONS_DIR, remaining_files)

    return report


def main():
    parser = argparse.ArgumentParser(description="Consolidate and Archive Duplicate Learning Lessons")
    parser.add_argument("--execute", action="store_true", help="Execute file moves (default is dry-run)")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Perform dry-run without mutations")
    args = parser.parse_args()

    dry_run = not args.execute
    print(f"=== Running Consolidation Engine (Dry-Run: {dry_run}) ===")
    report = execute_consolidation(dry_run=dry_run)
    print(json.dumps(report, indent=2))
    if dry_run:
        print("\nTo execute file moves, run with: python3 .agents/scripts/consolidate_learning_lessons.py --execute")


if __name__ == "__main__":
    main()
