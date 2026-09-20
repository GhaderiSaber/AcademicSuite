#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_native_antigravity_behavior.py — Native Antigravity Behavior Verification (Phase 29)

Mandate:
Verify the underlying capability-boundary architecture independently of AcademicSuite domain logic:
1. test-orchestrator:
   - invoke_subagent
   - view_file
   - ZERO execution tools (no run_command, no write_to_file, no replace_file_content, no edit_file)
2. test-worker:
   - view_file
   - run_command
   - write_to_file
3. Test flow:
   test-orchestrator
         ↓
   invoke_subagent
         ↓
   test-worker
         ↓
   run_command
4. Verifies that test-orchestrator cannot execute directly and must delegate to test-worker.
"""

import os
import sys
import json
import shutil
import tempfile
import subprocess
import unittest
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HOOKS_DIR = os.path.join(ROOT_DIR, ".agents", "hooks")
VERIF_DIR = os.path.join(ROOT_DIR, ".agents", "verification")
for p in (ROOT_DIR, HOOKS_DIR, VERIF_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from safety_hooks import SafetyHooks
from transcript_and_rule_guard import handle_pre_tool_use
from validators.agent_integrity import (
    parse_yaml_frontmatter,
    AgentCapabilityValidator,
    AGENTS_DIR,
)
from contracts.agents.capability_policy import (
    load_capability_policy,
    get_agent_policy,
    validate_agent_against_policy,
)
from scripts.capability_policy_gate import CapabilityPolicyGate, CapabilityPolicyViolationError
from scripts.immutable_capability_boundary_guard import NON_EXECUTING_AGENTS


class TestNativeAntigravityBehavior(unittest.TestCase):
    """Minimal Proof-of-Concept for Native Antigravity Behavior and Capability Boundary Isolation."""

    @classmethod
    def setUpClass(cls):
        cls.policy = load_capability_policy()
        cls.test_script_path = os.path.join(ROOT_DIR, "scripts", "run_test_task.py")
        assert os.path.isfile(cls.test_script_path), f"Test runner missing: {cls.test_script_path}"

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="phase29_poc_test_")
        self.input_file = os.path.join(self.temp_dir, "input_sample.txt")
        self.output_json = os.path.join(self.temp_dir, "output_result.json")
        with open(self.input_file, "w", encoding="utf-8") as f:
            f.write("SAMPLE_DATA_ROW_1\nSAMPLE_DATA_ROW_2\nSAMPLE_DATA_ROW_3\n")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def get_agent_frontmatter(self, agent_name: str) -> dict:
        agent_file = os.path.join(AGENTS_DIR, agent_name, "agent.md")
        with open(agent_file, "r", encoding="utf-8") as f:
            fm, _, err = parse_yaml_frontmatter(f.read())
            self.assertIsNone(err, f"Frontmatter error for {agent_name}: {err}")
            return fm

    # =========================================================================
    # Test 1: test-orchestrator toolset boundaries on disk
    # =========================================================================
    def test_01_test_orchestrator_toolset_boundaries(self):
        """Verifies test-orchestrator possesses invoke_subagent & view_file, and 0 execution tools."""
        fm = self.get_agent_frontmatter("test-orchestrator")
        tools = set(fm.get("tools", []))

        # Required tools
        self.assertIn("invoke_subagent", tools)
        self.assertIn("view_file", tools)

        # Strictly forbidden execution tools
        forbidden_execution = {"run_command", "write_to_file", "replace_file_content", "edit_file"}
        overlap = tools & forbidden_execution
        self.assertEqual(len(overlap), 0, f"test-orchestrator possesses forbidden execution tools: {overlap}")

        # Delegated subagents
        delegated = fm.get("agents", [])
        self.assertIn("test-worker", delegated)

        # Symlink check
        symlink_path = os.path.join(AGENTS_DIR, "test-orchestrator.md")
        self.assertTrue(os.path.islink(symlink_path))
        self.assertEqual(os.readlink(symlink_path), "test-orchestrator/agent.md")

        # Invariant set check
        self.assertIn("test-orchestrator", NON_EXECUTING_AGENTS)

    # =========================================================================
    # Test 2: test-worker toolset boundaries on disk
    # =========================================================================
    def test_02_test_worker_toolset_boundaries(self):
        """Verifies test-worker possesses view_file, run_command, write_to_file, and cannot delegate."""
        fm = self.get_agent_frontmatter("test-worker")
        tools = set(fm.get("tools", []))

        # Required execution tools
        self.assertIn("view_file", tools)
        self.assertIn("run_command", tools)
        self.assertIn("write_to_file", tools)

        # Leaf worker cannot delegate
        self.assertNotIn("invoke_subagent", tools)
        self.assertNotIn("manage_subagents", tools)

        # Symlink check
        symlink_path = os.path.join(AGENTS_DIR, "test-worker.md")
        self.assertTrue(os.path.islink(symlink_path))
        self.assertEqual(os.readlink(symlink_path), "test-worker/agent.md")

    # =========================================================================
    # Test 3: test-orchestrator cannot run_command directly
    # =========================================================================
    def test_03_test_orchestrator_cannot_run_command(self):
        """Verifies that test-orchestrator is blocked from executing run_command."""
        hook_payload = {
            "toolCall": {
                "name": "run_command",
                "args": {
                    "CommandLine": f"python3 {self.test_script_path} --input {self.input_file} --output {self.output_json}",
                    "Cwd": ROOT_DIR,
                }
            },
            "agentName": "test-orchestrator",
            "workspacePaths": [ROOT_DIR, self.temp_dir],
        }
        res = handle_pre_tool_use(hook_payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Orchestrator Non-Execution Invariant", res.get("reason", ""))

        # Capability policy verification also rejects frontmatter with run_command
        fm = self.get_agent_frontmatter("test-orchestrator").copy()
        fm["tools"] = list(set(fm.get("tools", [])) | {"run_command"})
        issues = validate_agent_against_policy("test-orchestrator", fm, self.policy)
        self.assertTrue(any("forbidden tools" in i for i in issues))

    # =========================================================================
    # Test 4: test-orchestrator cannot write_to_file directly
    # =========================================================================
    def test_04_test_orchestrator_cannot_write_files(self):
        """Verifies that test-orchestrator is blocked from mutating files directly."""
        hook_payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": self.output_json,
                    "CodeContent": "{\"illegal\": true}",
                    "Description": "Direct write attempt by test-orchestrator",
                }
            },
            "agentName": "test-orchestrator",
            "workspacePaths": [ROOT_DIR, self.temp_dir],
        }
        res = handle_pre_tool_use(hook_payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("strictly managerial and forbidden from writing", res.get("reason", ""))

    # =========================================================================
    # Test 5: CapabilityPolicyGate protects test-orchestrator boundary
    # =========================================================================
    def test_05_capability_policy_gate_protects_test_orchestrator(self):
        """Verifies CapabilityPolicyGate rejects candidate patches adding run_command to test-orchestrator."""
        illicit_candidate = {
            "id": "cand_test_illicit_001",
            "target": ".agents/agents/test-orchestrator/agent.md",
            "patch_type": "toolset_expansion",
            "diff": "tools:\n+  - run_command\n",
            "added_tools": ["run_command"],
            "rationale": "Allow test-orchestrator to run test tasks directly without delegating.",
        }
        verdict = CapabilityPolicyGate.evaluate_candidate_patch(illicit_candidate)
        self.assertEqual(verdict.decision, "REJECT")
        self.assertIn("CANNOT_ADD_EXECUTION_TOOLS_TO_NON_EXECUTING_AGENT", verdict.violations)
        self.assertIn("run_command", verdict.affected_tools)
        self.assertEqual(verdict.target_agent, "test-orchestrator")

        with self.assertRaises(CapabilityPolicyViolationError):
            CapabilityPolicyGate.enforce_capability_policy(illicit_candidate)

    # =========================================================================
    # Test 6: Full Native Antigravity Flow: test-orchestrator -> invoke_subagent -> test-worker -> run_command
    # =========================================================================
    def test_06_native_antigravity_delegation_flow_end_to_end(self):
        """
        Executes and validates the full proof-of-concept flow:
        test-orchestrator
              ↓
        invoke_subagent
              ↓
        test-worker
              ↓
        run_command
        """
        # Step 1: test-orchestrator receives computational task
        task_instruction = (
            f"Objective: Process sample input and produce deterministic output artifact.\n"
            f"Input: {self.input_file}\n"
            f"Output: {self.output_json}\n"
            f"Required CLI Command: python3 scripts/run_test_task.py --input {self.input_file} --output {self.output_json} --action transform\n"
            f"Acceptance Criteria: output JSON must exist, verify checks_passed=True, records_processed=100"
        )

        # Step 2: test-orchestrator delegates via invoke_subagent
        delegation_call = {
            "name": "invoke_subagent",
            "args": {
                "Subagents": [
                    {
                        "TypeName": "test-worker",
                        "Role": "Minimal Test Worker",
                        "Prompt": task_instruction,
                    }
                ]
            }
        }
        orchestrator_hook_payload = {
            "toolCall": delegation_call,
            "agentName": "test-orchestrator",
            "workspacePaths": [ROOT_DIR, self.temp_dir],
        }
        orch_res = handle_pre_tool_use(orchestrator_hook_payload)
        self.assertEqual(orch_res.get("decision"), "allow", f"Orchestrator delegation denied: {orch_res}")

        # Step 3: test-worker executes run_command
        worker_cmd = (
            f"python3 {self.test_script_path} "
            f"--input {self.input_file} "
            f"--output {self.output_json} "
            f"--action transform"
        )
        worker_call = {
            "name": "run_command",
            "args": {
                "CommandLine": worker_cmd,
                "Cwd": ROOT_DIR,
            }
        }
        worker_hook_payload = {
            "toolCall": worker_call,
            "agentName": "test-worker",
            "workspacePaths": [ROOT_DIR, self.temp_dir],
        }
        worker_hook_res = handle_pre_tool_use(worker_hook_payload)
        self.assertEqual(worker_hook_res.get("decision"), "allow", f"Worker execution denied: {worker_hook_res}")

        # Step 4: Deterministic computation executes
        proc = subprocess.run(
            [
                sys.executable,
                self.test_script_path,
                "--input", self.input_file,
                "--output", self.output_json,
                "--action", "transform",
            ],
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )
        self.assertEqual(proc.returncode, 0, f"Worker execution failed: {proc.stderr}")

        # Step 5: Verify physical artifact on disk
        self.assertTrue(os.path.isfile(self.output_json), f"Artifact missing on disk: {self.output_json}")
        with open(self.output_json, "r", encoding="utf-8") as f:
            artifact_data = json.load(f)

        self.assertEqual(artifact_data["status"], "COMPLETED")
        self.assertEqual(artifact_data["worker"], "test-worker")
        self.assertEqual(artifact_data["computed_metrics"]["action_executed"], "transform")
        self.assertEqual(artifact_data["computed_metrics"]["records_processed"], 100)
        self.assertTrue(artifact_data["verification"]["checks_passed"])

        # Step 6: test-worker returns structured result payload to test-orchestrator
        worker_return_payload = {
            "task_id": "TSK-TEST-POC-001",
            "status": "COMPLETED",
            "output_artifacts": [self.output_json],
            "computed_metrics": artifact_data["computed_metrics"],
            "checks_passed": True,
            "summary": "Completed deterministic task via test-worker execution.",
        }
        return_message_call = {
            "name": "send_message",
            "args": {
                "Recipient": "test-orchestrator",
                "Message": json.dumps(worker_return_payload),
            }
        }
        return_hook_payload = {
            "toolCall": return_message_call,
            "agentName": "test-worker",
            "workspacePaths": [ROOT_DIR, self.temp_dir],
        }
        return_res = handle_pre_tool_use(return_hook_payload)
        self.assertEqual(return_res.get("decision"), "allow", f"Worker return message denied: {return_res}")

    # =========================================================================
    # Test 7: test-worker cannot invoke secondary subagents
    # =========================================================================
    def test_07_test_worker_cannot_delegate(self):
        """Verifies that test-worker (leaf worker) cannot invoke secondary subagents."""
        secondary_call = {
            "name": "invoke_subagent",
            "args": {
                "Subagents": [
                    {
                        "TypeName": "test-worker",
                        "Role": "Secondary Worker",
                        "Prompt": "Secondary work",
                    }
                ]
            }
        }
        hook_payload = {
            "toolCall": secondary_call,
            "agentName": "test-worker",
            "workspacePaths": [ROOT_DIR, self.temp_dir],
        }
        res = handle_pre_tool_use(hook_payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Worker Delegation Guard", res.get("reason", ""))


if __name__ == "__main__":
    unittest.main()
