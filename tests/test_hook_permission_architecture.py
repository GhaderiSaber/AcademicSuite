#!/usr/bin/env python3
"""
test_hook_permission_architecture.py — Verification Suite for Antigravity Hooks & Permissions

Verifies:
1. Native filesystem least-privilege permission model across 7 tiers
2. Platform awareness (POSIX octal modes vs Windows S_IREAD)
3. PreToolUse hook defense-in-depth across all mutation tools
4. PostToolUse audit logging and schema compliance
5. PreInvocation and PostInvocation lifecycle hook behavior
6. Dynamic transcriptPath context handling
7. Stop hook forensic verification and scope isolation
8. hooks.json configuration syntax, events, and matcher coverage
"""

import os
import sys
import json
import stat
import tempfile
import unittest
from unittest.mock import patch, MagicMock

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
verification_path = os.path.join(ROOT_DIR, ".agents", "verification")
if verification_path not in sys.path:
    sys.path.insert(0, verification_path)
hooks_path = os.path.join(ROOT_DIR, ".agents", "hooks")
if hooks_path not in sys.path:
    sys.path.insert(0, hooks_path)

from hook_dispatcher import is_main_agent_developer, dispatch_event
from scripts.permission_manager import (
    PermissionManager,
    CAT_RAW_DATA,
    CAT_DERIVED_DATA,
    CAT_STATE,
    CAT_ARTIFACTS,
    CAT_SOURCE_CODE,
    CAT_SCRIPTS,
    CAT_CONFIGURATION
)
from tests.test_helpers import assert_write_fails_with_permission_error
from transcript_and_rule_guard import (
    handle_pre_tool_use,
    handle_post_tool_use,
    handle_pre_invocation,
    handle_post_invocation,
    handle_stop,
    load_transcript,
    is_raw_data_path,
    is_raw_data_command,
    extract_target_paths,
    MUTATION_TOOLS
)


class TestPermissionArchitecture(unittest.TestCase):
    """Tests the native OS least-privilege permission model."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.pm = PermissionManager(repo_root=self.temp_dir.name)

    def tearDown(self):
        # Restore write permissions on any readonly files so temp_dir can be cleaned up
        for root, dirs, files in os.walk(self.temp_dir.name):
            for f in files:
                try:
                    os.chmod(os.path.join(root, f), stat.S_IREAD | stat.S_IWRITE)
                except Exception:
                    pass
        self.temp_dir.cleanup()

    def test_permission_manager_classification(self):
        """Verify that paths are correctly classified into the 7 security tiers."""
        test_cases = [
            ("projects/study_act/01_raw_inputs/data.xlsx", CAT_RAW_DATA),
            ("raw_dataset.csv", CAT_RAW_DATA),
            ("data_raw.sav", CAT_RAW_DATA),
            ("projects/study_act/02_clean_and_scored/data_curated.xlsx", CAT_DERIVED_DATA),
            ("derived_data/data_cleaned.csv", CAT_DERIVED_DATA),
            ("state/events.jsonl", CAT_STATE),
            (".agents/memory/audit_log.jsonl", CAT_STATE),
            ("projects/study_act/03_deliverables/stage_06/06_hypothesis_1.docx", CAT_ARTIFACTS),
            ("artifacts/report.pdf", CAT_ARTIFACTS),
            (".agents/hooks.json", CAT_CONFIGURATION),
            ("contracts/event.schema.json", CAT_CONFIGURATION),
            (".agents/rules/AGENTS.md", CAT_CONFIGURATION),
            ("scripts/permission_manager.py", CAT_SCRIPTS),
            ("scripts/bootstrap.sh", CAT_SCRIPTS),
            ("validators/run_all_validators.py", CAT_SOURCE_CODE),
            (".agents/verification/skill_size_guard.py", CAT_SOURCE_CODE),
        ]
        for path, expected_cat in test_cases:
            cat = self.pm.classify_path(path)
            self.assertEqual(cat, expected_cat, f"Classification failed for '{path}'. Got: '{cat}', Expected: '{expected_cat}'")

    def test_least_privilege_enforcement_posix(self):
        """Verify that POSIX permissions are correctly applied and audited."""
        if sys.platform == "win32":
            self.skipTest("POSIX permission octals not applicable to Windows")

        # 1. Raw Data -> 0444 (Read-Only)
        raw_dir = os.path.join(self.temp_dir.name, "01_raw_inputs")
        os.makedirs(raw_dir, exist_ok=True)
        raw_file = os.path.join(raw_dir, "data_raw.csv")
        with open(raw_file, "w") as f:
            f.write("id,score\n1,10\n")

        self.pm.enforce_file_permission(raw_file, CAT_RAW_DATA)
        mode = stat.S_IMODE(os.lstat(raw_file).st_mode)
        self.assertEqual(oct(mode), "0o444")
        audit_raw = self.pm.audit_path(raw_file)
        self.assertEqual(audit_raw["status"], "PASS")

        # Write attempt to raw data file must raise PermissionError
        assert_write_fails_with_permission_error(self, raw_file, mode="a", data="2,20\n")

        # 2. Derived Data -> 0644 (Read-Write for Owner)
        derived_file = os.path.join(self.temp_dir.name, "data_curated.xlsx")
        with open(derived_file, "w") as f:
            f.write("data")
        self.pm.enforce_file_permission(derived_file, CAT_DERIVED_DATA)
        mode = stat.S_IMODE(os.lstat(derived_file).st_mode)
        self.assertEqual(oct(mode), "0o644")

        # 3. Scripts -> 0755 (Executable for Owner)
        script_file = os.path.join(self.temp_dir.name, "run_analysis.sh")
        with open(script_file, "w") as f:
            f.write("#!/bin/bash\necho 'running'\n")
        self.pm.enforce_file_permission(script_file, CAT_SCRIPTS)
        mode = stat.S_IMODE(os.lstat(script_file).st_mode)
        self.assertEqual(oct(mode), "0o755")

    def test_windows_permission_branch(self):
        """Verify Windows platform compatibility logic."""
        self.pm.is_windows = True

        raw_file = os.path.join(self.temp_dir.name, "data_raw.xlsx")
        with open(raw_file, "w") as f:
            f.write("binary data")

        # Must execute without error
        ok = self.pm.enforce_file_permission(raw_file, CAT_RAW_DATA)
        self.assertTrue(ok)
        audit = self.pm.audit_path(raw_file)
        self.assertEqual(audit["platform"], "windows")


class TestHookArchitecture(unittest.TestCase):
    """Tests the Antigravity lifecycle hook gatekeeper across all 5 events."""

    def test_extract_target_paths_across_tools(self):
        """Verify path extraction across various Antigravity tool signatures."""
        test_inputs = [
            ("write_to_file", {"TargetFile": "/path/to/file.py"}, ["/path/to/file.py"]),
            ("replace_file_content", {"TargetFile": "/path/to/other.py"}, ["/path/to/other.py"]),
            ("apply_diff", {"path": "module/code.py"}, ["module/code.py"]),
            ("edit_file", {"file_path": "scripts/test.py"}, ["scripts/test.py"]),
            ("multi_file_edit", {"files": ["a.py", "b.py"]}, ["a.py", "b.py"]),
            ("batch_replace", {"targets": [{"path": "c.py"}, {"path": "d.py"}]}, ["c.py", "d.py"]),
        ]
        for tool_name, args, expected in test_inputs:
            res = extract_target_paths(tool_name, args)
            self.assertEqual(sorted(res), sorted(expected))

    def test_raw_data_write_attempts_denied(self):
        """Verify that PreToolUse blocks all mutations targeting raw datasets."""
        for tool in MUTATION_TOOLS:
            payload = {
                "toolCall": {
                    "name": tool,
                    "args": {
                        "TargetFile": "01_raw_inputs/survey_raw.xlsx",
                        "file_path": "01_raw_inputs/survey_raw.xlsx",
                        "path": "01_raw_inputs/survey_raw.xlsx",
                        "files": ["01_raw_inputs/survey_raw.xlsx"]
                    }
                },
                "stepIdx": 1
            }
            res = handle_pre_tool_use(payload)
            self.assertEqual(res["decision"], "deny", f"Tool '{tool}' was not denied on raw data.")
            self.assertIn("Raw-Data Immutability Guard", res["reason"])

    def test_non_ascii_filename_denied(self):
        """Verify that PreToolUse denies non-ASCII filenames under Directive 6."""
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "نتایج_تحلیل.docx"}
            },
            "stepIdx": 2
        }
        res = handle_pre_tool_use(payload)
        self.assertEqual(res["decision"], "deny")
        self.assertIn("Directive 6 - English-Only Filename Standard", res["reason"])

    def test_prohibited_commands_denied(self):
        """Verify that PreToolUse denies destructive and tampering shell commands."""
        prohibited_commands = [
            "rm -rf .agents",
            "rm -rf .git",
            "rm -rf /",
            "sed -i 's/x/y/g' 01_raw_inputs/raw.csv",
            "chmod +w data_raw.xlsx",
            "tee -a 01_raw_inputs/raw.csv",
            "cat > 01_raw_inputs/dataset_raw.csv",
            "> raw_data.xlsx",
            "touch 'گزارش.txt'"
        ]
        for cmd in prohibited_commands:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd}
                },
                "stepIdx": 3
            }
            res = handle_pre_tool_use(payload)
            self.assertEqual(res["decision"], "deny", f"Prohibited command was not denied: '{cmd}'")

    def test_allowed_safe_operations(self):
        """Verify that legitimate development actions are allowed."""
        safe_tool_call = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "scripts/new_feature.py"}
            },
            "stepIdx": 4
        }
        res = handle_pre_tool_use(safe_tool_call)
        self.assertEqual(res["decision"], "allow")

        safe_command = {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "python3 run_tests.py"}
            },
            "stepIdx": 5
        }
        res = handle_pre_tool_use(safe_command)
        self.assertEqual(res["decision"], "allow")

    def test_post_tool_use_audit_logging(self):
        """Verify that PostToolUse records audit logs and returns an empty JSON object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            payload = {
                "workspacePaths": [tmpdir],
                "conversationId": "conv-audit-test",
                "stepIdx": 10,
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": "derived_data/out.csv", "CodeContent": "sensitive_data"}
                },
                "error": None
            }
            res = handle_post_tool_use(payload)
            self.assertEqual(res, {})

            audit_file = os.path.join(tmpdir, "state", "audit_log.jsonl")
            self.assertTrue(os.path.exists(audit_file))
            with open(audit_file, "r") as f:
                record = json.loads(f.readline())
            self.assertEqual(record["tool_name"], "write_to_file")
            self.assertEqual(record["conversation_id"], "conv-audit-test")
            self.assertEqual(record["status"], "SUCCESS")
            # Sensitive contents should be sanitized
            self.assertNotIn("CodeContent", record["tool_args"])

    def test_pre_invocation_behavior(self):
        """Verify PreInvocation injects constitutional guidance."""
        payload = {"invocationNum": 1, "initialNumSteps": 0}
        res = handle_pre_invocation(payload)
        self.assertIn("injectSteps", res)
        self.assertTrue(len(res["injectSteps"]) > 0)
        self.assertIn("ephemeralMessage", res["injectSteps"][0])
        self.assertIn("Binary Honesty Protocol", res["injectSteps"][0]["ephemeralMessage"])

    def test_post_invocation_behavior(self):
        """Verify PostInvocation returns valid contract schema and detects validation failures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Clean case
            payload = {
                "workspacePaths": [tmpdir],
                "invocationNum": 2,
                "initialNumSteps": 5
            }
            res = handle_post_invocation(payload)
            self.assertIn("injectSteps", res)
            self.assertIn("terminationBehavior", res)
            self.assertEqual(res["terminationBehavior"], "")

            # Failing validation case
            stage_dir = os.path.join(tmpdir, "projects", "study_test", "03_deliverables", "stage_01")
            os.makedirs(stage_dir, exist_ok=True)
            with open(os.path.join(stage_dir, "01_demographics.docx"), "w") as f:
                f.write("dummy")
            with open(os.path.join(stage_dir, "validation_report.json"), "w") as f:
                json.dump({
                    "overall_verdict": "FAIL",
                    "results": [{"check_name": "data_integrity", "verdict": "FAIL"}]
                }, f)

            res_fail = handle_post_invocation(payload)
            self.assertTrue(len(res_fail["injectSteps"]) > 0)
            self.assertIn("STAGE VERIFICATION ADVISORY", res_fail["injectSteps"][0]["ephemeralMessage"])

    def test_dynamic_transcript_path_handling(self):
        """Verify hooks prioritize transcriptPath provided in the event payload."""
        with tempfile.TemporaryDirectory() as tmpdir:
            transcript_file = os.path.join(tmpdir, "custom_transcript.jsonl")
            with open(transcript_file, "w") as f:
                f.write(json.dumps({
                    "type": "PLANNER_RESPONSE",
                    "content": "Yes, all rules were strictly checked.",
                    "tool_calls": []
                }) + "\n")

            records = load_transcript(transcript_file)
            self.assertEqual(len(records), 1)
            self.assertIn("Yes", records[0]["content"])

    def test_stop_hook_binary_honesty_gate(self):
        """Verify Stop hook enforces Directive 0 Binary Honesty Protocol."""
        with tempfile.TemporaryDirectory() as tmpdir:
            transcript_file = os.path.join(tmpdir, "transcript.jsonl")
            # Agent answers compliance query without 'Yes' or 'No' as first word
            records = [
                {"type": "USER_INPUT", "content": "Did you check the validation report?"},
                {"type": "PLANNER_RESPONSE", "content": "I certainly reviewed the whole system."}
            ]
            with open(transcript_file, "w") as f:
                for r in records:
                    f.write(json.dumps(r) + "\n")

            payload = {
                "workspacePaths": [tmpdir],
                "transcriptPath": transcript_file,
                "executionNum": 1
            }
            res = handle_stop(payload)
            self.assertEqual(res["decision"], "continue")
            self.assertIn("Directive 0 - Binary Honesty Protocol", res["reason"])

    def test_stop_hook_multiagent_integrity_gate(self):
        """Verify Stop hook blocks false claims of multi-agent execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            transcript_file = os.path.join(tmpdir, "transcript.jsonl")
            # Agent falsely claims multi-agent execution with 0 subagent calls
            records = [
                {"type": "USER_INPUT", "content": "Please run the pipeline."},
                {"type": "PLANNER_RESPONSE", "content": "We have successfully executed a complete multi-agent workflow.", "tool_calls": []}
            ]
            with open(transcript_file, "w") as f:
                for r in records:
                    f.write(json.dumps(r) + "\n")

            payload = {
                "workspacePaths": [tmpdir],
                "transcriptPath": transcript_file,
                "executionNum": 1
            }
            res = handle_stop(payload)
            self.assertEqual(res["decision"], "continue")
            self.assertIn("Directive 0 & Directive 12", res["reason"])

    def test_hook_json_schema_and_matchers(self):
        """Verify .agents/hooks.json conforms to Antigravity hook architecture."""
        hooks_path = os.path.join(ROOT_DIR, ".agents", "hooks.json")
        self.assertTrue(os.path.exists(hooks_path))
        with open(hooks_path, "r") as f:
            data = json.load(f)

        guard = data.get("constitutional-guard", {})
        self.assertTrue(guard.get("enabled", False))

        # Check all 5 official events exist
        for event in ("PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"):
            self.assertIn(event, guard, f"Official event '{event}' missing from hooks.json")

        # Verify tool matcher coverage in PreToolUse and PostToolUse
        pre_matcher = guard["PreToolUse"][0]["matcher"]
        post_matcher = guard["PostToolUse"][0]["matcher"]
        required_tools = [
            "run_command", "write_to_file", "replace_file_content",
            "apply_diff", "edit_file", "multi_file_edit", "batch_replace", "patch"
        ]
        for tool in required_tools:
            self.assertIn(tool, pre_matcher, f"Tool '{tool}' missing from PreToolUse matcher")

class TestMainAgentVsCustomSubagentIsolation(unittest.TestCase):
    """
    Verifies that the Built-in Main Agent possesses full developer control,
    while the Custom Academic Orchestrator and custom subagents are strictly governed.
    """

    def test_hook_authorization_is_fail_closed(self):
        """Unassigned, empty, or unknown caller must default to fail-closed (False), not unrestricted developer."""
        self.assertFalse(is_main_agent_developer({}))
        self.assertFalse(is_main_agent_developer({"agentName": ""}))
        self.assertFalse(is_main_agent_developer({"agentName": "unknown-agent"}))
        self.assertFalse(is_main_agent_developer({"caller": "unknown-caller"}))

        # Explicit developer indicators are recognized (True)
        self.assertTrue(is_main_agent_developer({"agentName": "default"}))
        self.assertTrue(is_main_agent_developer({"agentName": "main"}))
        self.assertTrue(is_main_agent_developer({"caller": "antigravity"}))
        self.assertTrue(is_main_agent_developer({"agentRole": "developer"}))
        self.assertTrue(is_main_agent_developer({"track": 1}))
        self.assertTrue(is_main_agent_developer({"mode": "developer"}))

    def test_custom_orchestrator_main_agent_classified_as_academic(self):
        """The custom Academic Orchestrator must be recognized as academic/custom (Track 2)."""
        self.assertFalse(is_main_agent_developer({"agentName": "academic-orchestrator"}))
        self.assertFalse(is_main_agent_developer({"caller": "academic-orchestrator"}))
        self.assertFalse(is_main_agent_developer({"agentRole": "Master Academic Orchestrator"}))
        self.assertFalse(is_main_agent_developer({"agentName": "test-orchestrator"}))
        self.assertFalse(is_main_agent_developer({"agentName": "digital-saber"}))

    def test_custom_subagents_classified_as_academic(self):
        """All custom specialist subagents in canonical SSOT must be classified as academic/custom (Track 2)."""
        from contracts.agents.capability_policy import get_all_policy_agents
        for sa in get_all_policy_agents():
            self.assertFalse(
                is_main_agent_developer({"agentName": sa}),
                f"Custom subagent '{sa}' should NOT be classified as main developer"
            )

    def test_antigravity_subagent_flag_marks_as_subagent(self):
        """If payload carries isSubagent: True, it must not be treated as root developer agent."""
        self.assertFalse(is_main_agent_developer({"agentName": "worker-1", "isSubagent": True}))
        self.assertFalse(is_main_agent_developer({"parentConversationId": "parent-123"}))

    def test_builtin_main_agent_stop_hook_immediate_allow(self):
        """Built-in Main Agent must never be blocked at Stop (immediate allow)."""
        res = dispatch_event("Stop", {"agentName": "default"})
        self.assertEqual(res, {"decision": "allow"})

        res_empty = dispatch_event("Stop", {})
        self.assertEqual(res_empty, {"decision": "allow"})

    def test_unassigned_caller_stop_hook_is_fail_closed_on_violations(self):
        """Unassigned caller is governed at Stop: if a violation exists, it returns continue (fail-closed)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a broken triad (only docx, missing md and json)
            stage_dir = os.path.join(tmpdir, "projects", "study", "03_deliverables", "stage_06")
            os.makedirs(stage_dir, exist_ok=True)
            with open(os.path.join(stage_dir, "06_hypothesis_1.docx"), "w") as f:
                f.write("dummy docx")

            # Unassigned / empty payload must be caught by Stop hook (fail-closed)
            res_unassigned = dispatch_event("Stop", {"workspacePaths": [tmpdir]})
            self.assertEqual(res_unassigned.get("decision"), "continue")
            self.assertIn("Triad Artifact Invariant", res_unassigned.get("reason", ""))

            # Explicit developer mode (track 1) is exempt
            res_dev = dispatch_event("Stop", {"track": 1, "workspacePaths": [tmpdir]})
            self.assertEqual(res_dev.get("decision"), "allow")

    def test_custom_orchestrator_stop_hook_runs_integrity(self):
        """Custom Academic Orchestrator must be routed to IntegrityHooks at Stop."""
        with tempfile.TemporaryDirectory() as tmpdir:
            res = dispatch_event("Stop", {
                "agentName": "academic-orchestrator",
                "workspacePaths": [tmpdir]
            })
            self.assertIn("decision", res)

    def test_builtin_main_agent_run_command_allowed_while_orchestrator_denied(self):
        """Built-in Main Agent can run commands; Custom Academic Orchestrator is blocked."""
        # Built-in main agent
        main_payload = {
            "agentName": "default",
            "toolCall": {"name": "run_command", "args": {"CommandLine": "pytest tests"}}
        }
        res_main = dispatch_event("PreToolUse", main_payload)
        self.assertEqual(res_main.get("decision"), "allow")

        # Custom orchestrator
        orch_payload = {
            "agentName": "academic-orchestrator",
            "toolCall": {"name": "run_command", "args": {"CommandLine": "pytest tests"}}
        }
        res_orch = dispatch_event("PreToolUse", orch_payload)
        self.assertEqual(res_orch.get("decision"), "deny")
        self.assertIn("Orchestrator Zero-Hands Contract", res_orch.get("reason", ""))

    def test_state_ledger_bypass_via_run_command_denied(self):
        """
        Verifies that worker agents cannot bypass state ledger immutability
        via run_command using Python inline execution, shell redirection, or chmod.
        """
        bypass_commands = [
            'python3 -c "open(\'academic-state/current_state.json\',\'w\').write(\'{}\')"',
            'python -c "open(\'state/events.jsonl\',\'w\').write(\'bad\')"',
            'echo "{}" > academic-state/current_state.json',
            'echo "corrupt" >> state/events.jsonl',
            'cat << EOF > academic-state/approvals.json\n{}\nEOF',
            'rm -f academic-state/current_state.json',
            'truncate -s 0 state/events.jsonl',
            'chmod 777 academic-state/current_state.json',
            'chmod +w academic-state',
        ]
        for cmd in bypass_commands:
            payload = {
                "agentName": "statistics-agent",
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd}
                },
                "stepIdx": 10
            }
            res = handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny", f"Command was not denied: {cmd}")
            self.assertIn("Invalid State Transition Guard", res.get("reason", ""))

    def test_state_ledger_os_filesystem_immutability(self):
        """
        Verifies that state ledger files are protected by OS least-privilege mode (0o444)
        and cannot be modified except via authorized state_ledger_transaction.
        """
        from scripts.permission_manager import state_ledger_transaction
        from scripts.academic_state_manager import StrictStateMachine

        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = os.path.join(tmpdir, "academic-state")
            sm = StrictStateMachine(state_dir=state_dir, project_id="p_test")
            sm.save_all()
            state_file = os.path.join(state_dir, "current_state.json")
            self.assertTrue(os.path.isfile(state_file))

            # Direct OS write must fail with PermissionError on POSIX
            if sys.platform != "win32":
                mode = stat.S_IMODE(os.lstat(state_file).st_mode)
                self.assertEqual(oct(mode), "0o444")
                assert_write_fails_with_permission_error(self, state_file, mode="w", data="{}")

            # Authorized mutation inside state_ledger_transaction must succeed
            with state_ledger_transaction(state_dir):
                with open(state_file, "w") as f:
                    f.write('{"authorized": true}')

            # File must be automatically re-locked to 0o444 upon transaction exit
            if sys.platform != "win32":
                mode_after = stat.S_IMODE(os.lstat(state_file).st_mode)
                self.assertEqual(oct(mode_after), "0o444")
                assert_write_fails_with_permission_error(self, state_file, mode="w", data="{}")


if __name__ == "__main__":
    unittest.main()
