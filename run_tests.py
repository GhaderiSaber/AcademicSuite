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

def main():
    print("=" * 70)
    print("🏛️  Digital Saber Academic Suite — Master Test Runner")
    print("=" * 70)
    
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
        sys.exit(1)

if __name__ == "__main__":
    main()
