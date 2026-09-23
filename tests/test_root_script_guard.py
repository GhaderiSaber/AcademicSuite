# -*- coding: utf-8 -*-
"""
test_root_script_guard.py — Tests for Directive 23 Clean Workspace Root Standard & Root Script Guard
"""

import os
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(REPO_ROOT, ".agents")
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)

from hooks.safety_hooks import SafetyHooks, is_root_script_target


class TestRootScriptGuard(unittest.TestCase):

    def test_is_root_script_target_helper(self):
        """Verifies is_root_script_target correctly identifies root scripts."""
        # Root scripts
        self.assertTrue(is_root_script_target("test_script.py")[0])
        self.assertTrue(is_root_script_target("./run_analysis.sh")[0])
        self.assertTrue(is_root_script_target(os.path.join(REPO_ROOT, "model.R"))[0])
        self.assertTrue(is_root_script_target(os.path.join(REPO_ROOT, "syntax.sps"))[0])

        # Whitelisted root scripts
        self.assertFalse(is_root_script_target("run_tests.py")[0])
        self.assertFalse(is_root_script_target("digital_saber.py")[0])
        self.assertFalse(is_root_script_target(os.path.join(REPO_ROOT, "run_tests.py"))[0])

        # Non-script root files
        self.assertFalse(is_root_script_target("README.md")[0])
        self.assertFalse(is_root_script_target(os.path.join(REPO_ROOT, "AGENTS.md"))[0])
        self.assertFalse(is_root_script_target("requirements.txt")[0])

        # Subdirectory scripts
        self.assertFalse(is_root_script_target(os.path.join(REPO_ROOT, "02_analysis_code", "model.py"))[0])
        self.assertFalse(is_root_script_target(os.path.join(REPO_ROOT, "tests", "test_foo.py"))[0])
        self.assertFalse(is_root_script_target(os.path.join(REPO_ROOT, ".agents", "scripts", "tool.py"))[0])

    def test_writing_script_to_root_is_denied(self):
        """PreToolUse hook blocks write_to_file for script files in workspace root."""
        for target in ["test_worker.py", "./debug_helper.sh", os.path.join(REPO_ROOT, "analysis.sps")]:
            payload = {
                "agentName": "data-agent",
                "workspacePaths": [REPO_ROOT],
                "toolCall": {
                    "name": "write_to_file",
                    "args": {
                        "TargetFile": target,
                        "CodeContent": "# Script content"
                    }
                }
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny", f"Target '{target}' should have been denied.")
            self.assertIn("Directive 23", res.get("reason", ""))
            self.assertIn("Clean Workspace Root Invariant", res.get("reason", ""))

    def test_writing_to_authorized_dirs_is_allowed(self):
        """PreToolUse hook allows write_to_file in proper subdirectories."""
        for target in [
            os.path.join(REPO_ROOT, "02_analysis_code", "data_clean.py"),
            os.path.join(REPO_ROOT, "tests", "test_new_feature.py"),
            os.path.join(REPO_ROOT, ".agents", "scripts", "academic_tool.py"),
        ]:
            payload = {
                "agentName": "data-agent",
                "workspacePaths": [REPO_ROOT],
                "toolCall": {
                    "name": "write_to_file",
                    "args": {
                        "TargetFile": target,
                        "CodeContent": "# Code content"
                    }
                }
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "allow", f"Target '{target}' should have been allowed.")

    def test_whitelisted_root_files_are_allowed(self):
        """PreToolUse hook permits modifying existing whitelisted root scripts."""
        for target in ["run_tests.py", os.path.join(REPO_ROOT, "digital_saber.py")]:
            payload = {
                "agentName": "main",
                "workspacePaths": [REPO_ROOT],
                "toolCall": {
                    "name": "write_to_file",
                    "args": {
                        "TargetFile": target,
                        "CodeContent": "# Whitelisted content"
                    }
                }
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "allow", f"Whitelisted '{target}' should have been allowed.")


if __name__ == "__main__":
    unittest.main()
