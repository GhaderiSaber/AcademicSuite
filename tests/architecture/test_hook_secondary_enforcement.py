#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_hook_secondary_enforcement.py — Architecture Test Suite for Secondary Hook Enforcement

Phase 20: Verifies the Five-Layer Architectural Hierarchy and ensures that Hooks act strictly
as secondary enforcement without accumulating primary orchestration responsibilities.

Hierarchy:
1. Tool boundary (Physical availability in agent.md)
2. Agent contract (agent_capabilities.yaml SSOT)
3. State machine (StrictStateMachine & STAGE_LEGAL_TRANSITIONS)
4. Hook enforcement (Secondary passive anomaly detection)
5. Evaluation (Validators & continuous testing)

The 5 Hook Detection Categories:
- unauthorized tool attempt
- invalid state transition
- missing artifact
- invalid provenance
- feedback event

Negative Invariants:
- Hooks must NOT act as primary orchestrator
- Hooks must NOT simulate agent delegation
- Hooks must NOT replace invoke_subagent
- Hooks must NOT run the whole workflow
"""

import os
import sys
import json
import shutil
import hashlib
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

hooks_dir = os.path.join(ROOT_DIR, ".agents", "hooks")
if hooks_dir not in sys.path:
    sys.path.insert(0, hooks_dir)

from safety_hooks import SafetyHooks
from integrity_hooks import IntegrityHooks
from learning_hooks import LearningHooks
from hook_dispatcher import dispatch_event
from contracts.agents.capability_policy import load_capability_policy, get_agent_policy
from validators.agent_integrity import parse_yaml_frontmatter, AGENTS_DIR
from scripts.academic_state_manager import StrictStateMachine, StageState, STAGE_LEGAL_TRANSITIONS


def compute_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class TestHookSecondaryEnforcement(unittest.TestCase):
    """Architecture test suite for Phase 20 secondary hook enforcement."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_hook_secondary_")
        self.workspace = self.temp_dir

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # =========================================================================
    # 1. The Five-Layer Enforcement Order
    # =========================================================================

    def test_the_five_layer_enforcement_order(self):
        """Verifies the distinct, non-overlapping roles across all 5 architectural layers."""
        # Layer 1: Tool Boundary (Physical absence in agent.md)
        orch_path = os.path.join(AGENTS_DIR, "academic-orchestrator", "agent.md")
        with open(orch_path, "r", encoding="utf-8") as f:
            fm, _, _ = parse_yaml_frontmatter(f.read())
        orch_tools = set(fm.get("tools", []))
        self.assertNotIn("run_command", orch_tools, "Layer 1: run_command must be physically absent from orchestrator frontmatter")
        self.assertNotIn("write_to_file", orch_tools, "Layer 1: write_to_file must be physically absent from orchestrator frontmatter")

        # Layer 2: Agent Contract (agent_capabilities.yaml SSOT)
        policy = load_capability_policy()
        orch_policy = get_agent_policy("academic-orchestrator", policy)
        self.assertFalse(orch_policy.get("can_execute_code"), "Layer 2: Contract must forbid code execution")
        self.assertFalse(orch_policy.get("can_write_files"), "Layer 2: Contract must forbid file writing")
        self.assertIn("run_command", orch_policy.get("forbidden", []))

        # Layer 3: State Machine (StrictStateMachine authoritative gating)
        state_dir = os.path.join(self.workspace, "state")
        sm = StrictStateMachine(state_dir=state_dir, project_id="p1")
        sm.register_stage("01_demographics", "Demographics", initial_status=StageState.STAGE_LOCKED)
        self.assertEqual(sm.stages["01_demographics"]["status"], StageState.STAGE_LOCKED.value)

        # Layer 4: Hook Enforcement (Secondary passive interception)
        unauth_payload = {
            "agentName": "academic-orchestrator",
            "toolCall": {"name": "run_command", "args": {"CommandLine": "python3 script.py"}},
            "workspacePaths": [self.workspace]
        }
        res = SafetyHooks.handle_pre_tool_use(unauth_payload)
        self.assertEqual(res.get("decision"), "deny", "Layer 4: Hook must intercept unauthorized attempt as secondary defense")

        # Layer 5: Evaluation (Capability validator executable and verifiable)
        cand_val = os.path.join(ROOT_DIR, ".agents", "validators", "agent_capability_validator.py")
        validator_path = cand_val if os.path.isfile(cand_val) else os.path.join(ROOT_DIR, "validators", "agent_capability_validator.py")
        self.assertTrue(os.path.isfile(validator_path), "Layer 5: Capability validator must exist on disk")

    # =========================================================================
    # 2. Hooks Are NOT Primary Orchestrators & Do NOT Simulate Delegation
    # =========================================================================

    def test_hooks_are_secondary_enforcement_not_primary_orchestrator(self):
        """Negative Invariant: Hooks must never advance state machine stages or run workflow pipelines."""
        state_dir = os.path.join(self.workspace, "state")
        sm = StrictStateMachine(state_dir=state_dir, project_id="p1")
        sm.register_stage("01_demographics", "Demographics", initial_status=StageState.STAGE_LOCKED)

        # Running hook handlers must NEVER mutate state machine stages
        payload = {
            "workspacePaths": [self.workspace],
            "toolCall": {"name": "view_file", "args": {"AbsolutePath": "/dummy/file.txt"}}
        }
        SafetyHooks.handle_pre_tool_use(payload)
        IntegrityHooks.handle_stop(payload)
        LearningHooks.capture_agent_trajectory(payload)

        sm.load_from_disk()
        self.assertEqual(sm.stages["01_demographics"]["status"], StageState.STAGE_LOCKED.value)

    def test_hooks_do_not_simulate_agent_delegation(self):
        """Negative Invariant: Hooks must never fake or mock subagent responses."""
        payload = {
            "agentName": "academic-orchestrator",
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [{"TypeName": "statistics-agent", "Role": "Statistician", "Prompt": "Run ANOVA"}]
                }
            },
            "workspacePaths": [self.workspace]
        }
        # Hooks permit authorized delegation without synthesizing a mock result
        res = SafetyHooks.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "allow")
        self.assertNotIn("mock_result", res)
        self.assertNotIn("simulated_response", res)

    # =========================================================================
    # 3. Detection Category 1: Unauthorized Tool Attempt
    # =========================================================================

    def test_hooks_detect_unauthorized_tool_attempt_direct_execution(self):
        """Category 1: Detects direct execution attempt by non-executing agents."""
        non_executors = [
            "academic-orchestrator",
            "methodology-expert",
            "statistical-expert",
            "results-auditor",
            "final-judge",
            "evidence-auditor",
            "academic-challenger",
        ]
        for caller in non_executors:
            payload = {
                "agentName": caller,
                "toolCall": {"name": "run_command", "args": {"CommandLine": "ls -la"}},
                "workspacePaths": [self.workspace]
            }
            is_unauth, reason = SafetyHooks.check_unauthorized_tool_attempt(payload)
            self.assertTrue(is_unauth, f"Failed to detect unauthorized direct execution for {caller}")
            self.assertIn("CONSTITUTIONAL VIOLATION", reason)

    def test_hooks_detect_unauthorized_tool_attempt_indirect_execution(self):
        """Category 1: Detects indirect execution bypass attempts by non-executors."""
        non_executors = ["academic-orchestrator", "methodology-expert", "results-auditor", "final-judge"]
        indirect_tools = [
            ("call_mcp_tool", {"ServerName": "posthog", "ToolName": "exec"}),
            ("define_subagent", {"name": "escalated_worker", "enable_write_tools": True}),
            ("manage_task", {"Action": "send_input", "Input": "rm -rf"}),
            ("schedule", {"Prompt": "run bash", "DurationSeconds": 60}),
        ]
        for caller in non_executors:
            for tool_name, args in indirect_tools:
                payload = {
                    "agentName": caller,
                    "toolCall": {"name": tool_name, "args": args},
                    "workspacePaths": [self.workspace]
                }
                is_unauth, reason = SafetyHooks.check_unauthorized_tool_attempt(payload)
                self.assertTrue(is_unauth, f"Failed to block indirect execution tool {tool_name} for {caller}")

    def test_hooks_detect_unauthorized_tool_attempt_orchestrator_mutation(self):
        """Category 1: Detects direct file writing or editing by academic-orchestrator."""
        mutation_tools = [
            ("write_to_file", {"TargetFile": os.path.join(self.workspace, "Chapter_4.docx"), "CodeContent": "x"}),
            ("replace_file_content", {"TargetFile": os.path.join(self.workspace, "results.md")}),
        ]
        for tool_name, args in mutation_tools:
            payload = {
                "agentName": "academic-orchestrator",
                "toolCall": {"name": tool_name, "args": args},
                "workspacePaths": [self.workspace]
            }
            is_unauth, reason = SafetyHooks.check_unauthorized_tool_attempt(payload)
            self.assertTrue(is_unauth, f"Orchestrator mutation via {tool_name} was not blocked")
            self.assertIn("Orchestrator Code Guard", reason)

    def test_hooks_detect_unauthorized_tool_attempt_worker_delegation(self):
        """Category 1: Detects specialist workers attempting secondary subagent delegation."""
        workers = ["statistics-agent", "data-agent", "academic-writer", "data-curator"]
        for worker in workers:
            payload = {
                "agentName": worker,
                "toolCall": {
                    "name": "invoke_subagent",
                    "args": {"Subagents": [{"TypeName": "research", "Prompt": "do research"}]}
                },
                "workspacePaths": [self.workspace]
            }
            is_unauth, reason = SafetyHooks.check_unauthorized_tool_attempt(payload)
            self.assertTrue(is_unauth, f"Worker {worker} was allowed to invoke subagents")
            self.assertIn("Worker Delegation Guard", reason)

    # =========================================================================
    # 4. Detection Category 2: Invalid State Transition
    # =========================================================================

    def test_hooks_detect_invalid_state_transition_illegal_target(self):
        """Category 2: Detects illegal state transition recorded in current_state.json."""
        state_dir = os.path.join(self.workspace, "state")
        os.makedirs(state_dir, exist_ok=True)
        # Illegal jump: STAGE_LOCKED directly to STAGE_APPROVED (bypassing READY, RUNNING, VALIDATING)
        invalid_state = {
            "stages": {
                "01_demographics": {
                    "status": "STAGE_APPROVED",
                    "history": [
                        {"from_state": "STAGE_LOCKED", "to_state": "STAGE_APPROVED"}
                    ]
                }
            }
        }
        with open(os.path.join(state_dir, "current_state.json"), "w", encoding="utf-8") as f:
            json.dump(invalid_state, f)

        ok, reason = IntegrityHooks.verify_state_transitions([self.workspace])
        self.assertFalse(ok, "Failed to catch illegal state transition")
        self.assertIn("Invalid State Transition Guard", reason)
        self.assertIn("STAGE_LOCKED", reason)
        self.assertIn("STAGE_APPROVED", reason)

    def test_hooks_detect_invalid_state_transition_unapproved_stage(self):
        """Category 2: Detects STAGE_APPROVED status without explicit human approval in approvals.json."""
        state_dir = os.path.join(self.workspace, "state")
        os.makedirs(state_dir, exist_ok=True)
        valid_history_state = {
            "stages": {
                "01_demographics": {
                    "status": "STAGE_APPROVED",
                    "history": [
                        {"from_state": "STAGE_LOCKED", "to_state": "STAGE_READY"},
                        {"from_state": "STAGE_READY", "to_state": "STAGE_RUNNING"},
                        {"from_state": "STAGE_RUNNING", "to_state": "STAGE_VALIDATING"},
                        {"from_state": "STAGE_VALIDATING", "to_state": "STAGE_AWAITING_APPROVAL"},
                        {"from_state": "STAGE_AWAITING_APPROVAL", "to_state": "STAGE_APPROVED"},
                    ]
                }
            }
        }
        with open(os.path.join(state_dir, "current_state.json"), "w", encoding="utf-8") as f:
            json.dump(valid_history_state, f)

        # approvals.json is empty (no explicit approval recorded)
        with open(os.path.join(state_dir, "approvals.json"), "w", encoding="utf-8") as af:
            json.dump({"approvals": []}, af)

        ok, reason = IntegrityHooks.verify_state_transitions([self.workspace])
        self.assertFalse(ok, "Failed to catch STAGE_APPROVED missing human approval record")
        self.assertIn("Invalid State Transition Guard", reason)
        self.assertIn("approvals.json", reason)

    def test_hooks_detect_invalid_state_transition_cli_and_direct_ledger_bypass(self):
        """Category 2: Detects direct modification of state ledgers outside state manager."""
        payload_write = {
            "agentName": "statistics-agent",
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": os.path.join(self.workspace, "state", "current_state.json"), "CodeContent": "{}"}
            },
            "workspacePaths": [self.workspace]
        }
        res = SafetyHooks.handle_pre_tool_use(payload_write)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Invalid State Transition Guard", res.get("reason", ""))

        payload_cmd = {
            "agentName": "statistics-agent",
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "python3 scripts/academic_state_manager.py set_stage 01 --mode production"}
            },
            "workspacePaths": [self.workspace]
        }
        res_cmd = SafetyHooks.handle_pre_tool_use(payload_cmd)
        self.assertEqual(res_cmd.get("decision"), "deny")
        self.assertIn("Invalid State Transition Guard", res_cmd.get("reason", ""))

    # =========================================================================
    # 5. Detection Category 3: Missing Artifact
    # =========================================================================

    def test_hooks_detect_missing_artifact_triad(self):
        """Category 3: Detects missing triad component (.docx, .md, .json) in active stage."""
        stage_dir = os.path.join(self.workspace, "projects", "study1", "06_hypothesis_1")
        os.makedirs(stage_dir, exist_ok=True)
        # Create only .md and .json, omitting .docx
        with open(os.path.join(stage_dir, "06_hypothesis_1.md"), "w") as f:
            f.write("# Hypothesis 1")
        with open(os.path.join(stage_dir, "06_hypothesis_1.json"), "w") as f:
            f.write("{}")

        ok, reason = IntegrityHooks.verify_missing_artifacts([self.workspace])
        self.assertFalse(ok, "Failed to detect missing .docx artifact")
        self.assertIn("Triad Artifact Invariant", reason)
        self.assertIn("06_hypothesis_1.docx", reason)

    def test_hooks_detect_missing_artifact_manifest_deliverable(self):
        """Category 3: Detects declared deliverable missing on disk from manifest.json."""
        stage_dir = os.path.join(self.workspace, "projects", "study1", "01_demographics")
        os.makedirs(stage_dir, exist_ok=True)
        manifest = {
            "contract_version": "1.0.0",
            "stage_id": "01_demographics",
            "artifacts": [{"path": "demographics_table.docx"}]
        }
        with open(os.path.join(stage_dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f)

        # demographics_table.docx does not exist on disk
        ok, reason = IntegrityHooks.verify_missing_artifacts([self.workspace])
        self.assertFalse(ok, "Failed to detect missing declared deliverable in manifest")
        self.assertIn("Manifest Verification", reason)
        self.assertIn("demographics_table.docx", reason)

    # =========================================================================
    # 6. Detection Category 4: Invalid Provenance
    # =========================================================================

    def test_hooks_detect_invalid_provenance_input_hash_mismatch(self):
        """Category 4: Detects input artifact mutation after manifest generation."""
        stage_dir = os.path.join(self.workspace, "stage_01")
        os.makedirs(stage_dir, exist_ok=True)
        data_path = os.path.join(stage_dir, "data_cleaned.csv")
        with open(data_path, "wb") as f:
            f.write(b"original_content")

        manifest = {
            "stage_id": "stage_01",
            "inputs": [{"path": "data_cleaned.csv", "sha256": "fake_sha256_hash_that_differs"}],
            "hashes": {}
        }
        with open(os.path.join(stage_dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f)

        ok, reason = IntegrityHooks.verify_provenance([self.workspace])
        self.assertFalse(ok, "Failed to detect mutated input artifact")
        self.assertIn("Invalid Provenance Guard", reason)
        self.assertIn("Input artifact 'data_cleaned.csv'", reason)

    def test_hooks_detect_invalid_provenance_deliverable_hash_mismatch(self):
        """Category 4: Detects deliverable artifact hash mismatch (modified outside pipeline)."""
        stage_dir = os.path.join(self.workspace, "stage_02")
        os.makedirs(stage_dir, exist_ok=True)
        doc_path = os.path.join(stage_dir, "report.docx")
        with open(doc_path, "wb") as f:
            f.write(b"tampered_content")

        manifest = {
            "stage_id": "stage_02",
            "inputs": [],
            "hashes": {"report.docx": "expected_original_sha256_hash"}
        }
        with open(os.path.join(stage_dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f)

        ok, reason = IntegrityHooks.verify_provenance([self.workspace])
        self.assertFalse(ok, "Failed to detect tampered deliverable hash")
        self.assertIn("Invalid Provenance Guard", reason)
        self.assertIn("Deliverable artifact 'report.docx'", reason)

    def test_hooks_detect_invalid_provenance_uninvoked_multiagent_claim(self):
        """Category 4: Detects multi-agent execution claim when invoke_subagent was called 0 times."""
        mock_transcript = [
            {"type": "USER_INPUT", "content": "Execute Chapter 4 findings."},
            {
                "type": "PLANNER_RESPONSE",
                "content": "We have successfully completed a multi-agent workflow with all subagents executed.",
                "tool_calls": [{"name": "view_file", "args": {}}]  # 0 calls to invoke_subagent
            }
        ]
        ok, reason = IntegrityHooks.verify_multiagent_truthfulness(mock_transcript)
        self.assertFalse(ok, "Failed to block uninvoked multi-agent claim")
        self.assertIn("invoke_subagent' was called 0 times", reason)

    # =========================================================================
    # 7. Detection Category 5: Feedback Event
    # =========================================================================

    def test_hooks_detect_feedback_event_user_correction(self):
        """Category 5: Detects user critique or correction and emits USER_CORRECTION event."""
        state_dir = os.path.join(self.workspace, "state")
        os.makedirs(state_dir, exist_ok=True)
        transcript_file = os.path.join(self.workspace, "transcript.jsonl")
        with open(transcript_file, "w", encoding="utf-8") as f:
            json.dump({"step_index": 1, "type": "USER_INPUT", "content": "Please fix the ANCOVA table, the df is incorrect."}, f)
            f.write("\n")

        payload = {
            "conversationId": "test_conv_fb",
            "transcriptPath": transcript_file,
            "workspacePaths": [self.workspace]
        }
        # Run user correction capture
        LearningHooks.capture_user_correction(payload)

        # Check trajectory events
        events_file = os.path.join(state_dir, "trajectory_events.jsonl")
        self.assertTrue(os.path.isfile(events_file), "trajectory_events.jsonl was not created")
        with open(events_file, "r", encoding="utf-8") as f:
            events = [json.loads(line) for line in f if line.strip()]
        self.assertTrue(any(e.get("event_type") == "USER_CORRECTION" for e in events))

    def test_hooks_detect_feedback_event_validation_failure(self):
        """Category 5: Detects validation failure and emits VALIDATION_FAILED event."""
        stage_dir = os.path.join(self.workspace, "stage_03")
        os.makedirs(stage_dir, exist_ok=True)
        state_dir = os.path.join(self.workspace, "state")
        os.makedirs(state_dir, exist_ok=True)

        validator_results = [
            {"validator_name": "APA7Validator", "verdict": "FAIL", "failed_checks": ["p_value_leading_zero"]}
        ]
        LearningHooks.capture_validation_failure(stage_dir=stage_dir, validator_results=validator_results)

        events_file = os.path.join(state_dir, "trajectory_events.jsonl")
        self.assertTrue(os.path.isfile(events_file), "trajectory_events.jsonl was not created")
        with open(events_file, "r", encoding="utf-8") as f:
            events = [json.loads(line) for line in f if line.strip()]
        self.assertTrue(any(e.get("event_type") == "VALIDATION_FAILED" for e in events))


if __name__ == "__main__":
    unittest.main()
