#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_raw_data_mutation_guard.py — Regression Test for Raw-Data Immutability & OS Permission Lock

Tests:
1. PermissionManager.lock_raw_data_directory enforces 0444 read-only on raw datasets.
2. Direct OS write via open(..., 'w') or open(..., 'ab') raises PermissionError.
3. PreToolUse hook denies write_to_file / replace_file_content on raw datasets.
4. PreToolUse hook actively locks down existing raw dataset files if they were writeable.
"""

import os
import sys
import stat
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)

from scripts.permission_manager import PermissionManager, CAT_RAW_DATA
from verification.transcript_and_rule_guard import handle_pre_tool_use, is_raw_data_path
from tests.test_helpers import assert_write_fails_with_permission_error


class TestRawDataMutationGuard(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_raw_guard_")
        self.raw_dir = os.path.join(self.temp_dir, "01_raw_inputs")
        os.makedirs(self.raw_dir, exist_ok=True)
        self.raw_file = os.path.join(self.raw_dir, "raw_data.xlsx")
        with open(self.raw_file, "wb") as f:
            f.write(b"RAW DATA CONTENT")

    def tearDown(self):
        import shutil
        try:
            os.chmod(self.raw_file, 0o666)
        except Exception:
            pass
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_permission_manager_locks_raw_directory(self):
        pm = PermissionManager(repo_root=self.temp_dir)
        locked_count = pm.lock_raw_data_directory(self.raw_dir)
        self.assertEqual(locked_count, 1)

        mode = stat.S_IMODE(os.stat(self.raw_file).st_mode)
        if sys.platform != "win32":
            self.assertEqual(mode, 0o444)
        else:
            self.assertFalse(bool(mode & stat.S_IWRITE))

        assert_write_fails_with_permission_error(self, self.raw_file, mode="ab", data=b"CORRUPTION")

    def test_hook_denies_and_locks_raw_file(self):
        os.chmod(self.raw_file, 0o664)
        self.assertTrue(os.access(self.raw_file, os.W_OK))

        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": self.raw_file,
                    "CodeContent": "MALICIOUS"
                }
            }
        }
        res = handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Raw-Data Immutability Guard", res.get("reason", ""))

        mode = stat.S_IMODE(os.stat(self.raw_file).st_mode)
        self.assertFalse(os.access(self.raw_file, os.W_OK))


if __name__ == "__main__":
    unittest.main()
