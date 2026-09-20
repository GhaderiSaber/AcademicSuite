# -*- coding: utf-8 -*-
"""
tests/conftest.py — Global Pytest Configuration and Path Invariant

Ensures both the workspace root and the consolidated .agents/ directory
are always present in sys.path during test runs.
"""

import os
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(TESTS_DIR, ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")

for p in [ROOT_DIR, AGENTS_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)
