#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stop Lifecycle Hook Runner"""
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GUARD_PATH = os.path.join(REPO_ROOT, ".agents", "verification", "transcript_and_rule_guard.py")

if __name__ == "__main__":
    os.execv(sys.executable, [sys.executable, GUARD_PATH, "--event", "Stop"] + sys.argv[1:])
