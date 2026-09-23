#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chapter 5 Writing Skill Assembler Wrapper
"""
import os
import sys

TARGET_SCRIPT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    "../../persian-discussion-builder/scripts/assemble_chapter5.py"
))

if __name__ == "__main__":
    if os.path.exists(TARGET_SCRIPT):
        os.execv(sys.executable, [sys.executable, TARGET_SCRIPT] + sys.argv[1:])
    else:
        sys.stderr.write(f"Error: Target script not found: {TARGET_SCRIPT}\n")
        sys.exit(1)
