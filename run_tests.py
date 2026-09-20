#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_tests.py — Master Test Runner for Digital Saber Academic Suite

Discovers and executes all mathematical, psychometric, and constitutional tests
in the tests/ directory with clean, colorized terminal reporting.
"""

import os
import sys
import time
import unittest

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

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
    os.path.join(ROOT_DIR, "webapp"),
]
for p in reversed(RESOLVE_DIRS):
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        try:
            for entry in os.listdir(venv_lib):
                sp = os.path.join(venv_lib, entry, "site-packages")
                if os.path.isdir(sp) and sp not in sys.path:
                    sys.path.insert(0, sp)
        except OSError:
            pass


def main():
    print("=" * 70)
    print("🏛️  Digital Saber Academic Suite — Master Test Runner")
    print("=" * 70)
    
    try:
        from scripts.generate_test_fixtures import ensure_fixtures_present
        ensure_fixtures_present()
    except Exception as e:
        print(f"[run_tests] Fixtures readiness check note: {e}")

    start_time = time.time()
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests", pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 70)
    print(f"Tests Run:      {result.testsRun}")
    print(f"Passed:         {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:       {len(result.failures)}")
    print(f"Errors:         {len(result.errors)}")
    print(f"Execution Time: {elapsed:.3f}s")
    print("=" * 70)
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED: Mathematical & constitutional invariants verified.")
        sys.exit(0)
    else:
        print("❌ TEST SUITE FAILED: See tracebacks above.")
        has_import_error = any("ModuleNotFoundError" in str(err) or "ImportError" in str(err) for _, err in result.errors)
        if has_import_error:
            print("\n💡 Tip: Missing dependencies detected in host Python environment.")
            print("   To install dependencies in a local venv, run:")
            print("     bash scripts/bootstrap_env.sh")
            print("   Or run with active venv: .venv/bin/python run_tests.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
