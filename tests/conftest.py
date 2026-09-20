# -*- coding: utf-8 -*-
"""
tests/conftest.py — Global Pytest Configuration and Path Invariant

Ensures ROOT_DIR and all consolidated .agents/ directories
are always present in sys.path during test runs, eliminating
the need for root symlinks.
"""

import os
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(TESTS_DIR, ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")

RESOLVE_DIRS = [
    ROOT_DIR,
    AGENTS_DIR,
    os.path.join(AGENTS_DIR, "scripts"),
    os.path.join(AGENTS_DIR, "contracts"),
    os.path.join(AGENTS_DIR, "validators"),
    os.path.join(AGENTS_DIR, "factory"),
    os.path.join(AGENTS_DIR, "recovery"),
    os.path.join(AGENTS_DIR, "tools"),
    os.path.join(AGENTS_DIR, "tools", "python"),
    os.path.join(AGENTS_DIR, "learning"),
    os.path.join(AGENTS_DIR, "state"),
    os.path.join(AGENTS_DIR, "data"),
]

for p in reversed(RESOLVE_DIRS):
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

existing_pythonpath = os.environ.get("PYTHONPATH", "")
extra_paths = [p for p in RESOLVE_DIRS if os.path.isdir(p)]
if extra_paths:
    new_pythonpath = os.pathsep.join(extra_paths)
    if existing_pythonpath:
        new_pythonpath = new_pythonpath + os.pathsep + existing_pythonpath
    os.environ["PYTHONPATH"] = new_pythonpath
