#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/build_hypothesis_1_triad_docx.py — [CONSOLIDATED COMPATIBILITY WRAPPER]

Consolidated in Phase 35: Superseded by scripts/generate_hypothesis_triad_docx.py.
Retained as a thin backward-compatibility wrapper delegating directly to
generate_hypothesis_triad_docx.py for dynamic triad artifact generation.
Contains zero hardcoded mock studies or prepared narrative text.
"""
import os
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from generate_hypothesis_triad_docx import create_hypothesis_triad


def build_docx(out_dir_or_file: str):
    """Compatibility wrapper delegating to canonical generate_hypothesis_triad_docx."""
    target_dir = out_dir_or_file if os.path.isdir(out_dir_or_file) else os.path.dirname(os.path.abspath(out_dir_or_file))
    if not target_dir:
        target_dir = os.getcwd()
    create_hypothesis_triad(target_dir)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    build_docx(target)
