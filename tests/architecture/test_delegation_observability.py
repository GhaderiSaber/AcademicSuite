#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_delegation_observability.py — Architecture Tests for Phase 23 Observable Delegation

Verifies:
1. Canonical Delegation Events (5):
   SUBAGENT_REQUESTED, SUBAGENT_STARTED, SUBAGENT_COMPLETED, SUBAGENT_FAILED, ARTIFACT_RETURNED.
2. The 8 Mandatory Telemetry Fields:
   parent_agent, child_agent, task_id, timestamp, objective, input_artifacts, output_artifacts, status.
3. Strict Schema Validation against contracts/delegation_event.schema.json.
4. Factual Observation in TrajectoryEngine:
   Replaces speculative inference ("Probably statistics-agent was used")
   with direct physical observation: academic-orchestrator → invoke_subagent → statistics-agent.
5. Hook Lifecycle Interception:
   PreToolUse emits SUBAGENT_REQUESTED and SUBAGENT_STARTED.
   PostToolUse emits SUBAGENT_COMPLETED (or SUBAGENT_FAILED) and ARTIFACT_RETURNED.
6. Failure and Error Handling:
   Tool error triggers SUBAGENT_FAILED with status FAILED.
7. Anti-Deception & Speculative Inference Guard:
   Unobserved delegations raise UnobservedDelegationError.
"""

import os
import sys
import json
import unittest
import tempfile
import shutil
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HOOKS_DIR = os.path.join(ROOT_DIR, ".agents", "hooks")
for p in (ROOT_DIR, HOOKS_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from scripts.delegation_event_engine import (
    DelegationEventEngine,
    DelegationEventType,
    DelegationStatus,
    DelegationEventValidationError,
    UnobservedDelegationError,
    load_delegation_event_schema
)
from scripts.trajectory_engine import (
    TrajectoryEngine,
    TrajectoryEventType
)
from contracts.contract_validator import validate_delegation_event
from learning_hooks import LearningHooks


class TestDelegationObservability(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_del_obs_")
        self.state_dir = os.path.join(self.temp_dir, "state")
        os.makedirs(self.state_dir, exist_ok=True)
        self.del_engine = DelegationEventEngine(state_dir=self.state_dir, project_root=self.temp_dir)
        self.traj_engine = TrajectoryEngine(state_dir=self.state_dir, project_root=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_all_5_delegation_event_types_schema_valid(self):
        """Tests that all 5 canonical delegation event types validate against contracts/delegation_event.schema.json."""
        event_types = [
            (DelegationEventType.SUBAGENT_REQUESTED, DelegationStatus.REQUESTED),
            (DelegationEventType.SUBAGENT_STARTED, DelegationStatus.STARTED),
            (DelegationEventType.SUBAGENT_COMPLETED, DelegationStatus.COMPLETED),
            (DelegationEventType.SUBAGENT_FAILED, DelegationStatus.FAILED),
            (DelegationEventType.ARTIFACT_RETURNED, DelegationStatus.RETURNED),
        ]

        for etype, stat in event_types:
            evt = self.del_engine.emit_delegation_event(
                event_type=etype,
                parent_agent="academic-orchestrator",
                child_agent="statistics-agent",
                task_id="TSK-2026-CH4-001",
                objective="Calculate repeated-measures ANOVA on empirical clinical dataset",
                status=stat,
                input_artifacts=["01_data/raw_data.xlsx"],
                output_artifacts=["03_outputs/anova_results.json"],
                details={"scope": "unit_test"}
            )
            # Must contain all 8 mandatory fields
            self.assertEqual(evt["event_type"], etype.value)
            self.assertEqual(evt["parent_agent"], "academic-orchestrator")
            self.assertEqual(evt["child_agent"], "statistics-agent")
            self.assertEqual(evt["task_id"], "TSK-2026-CH4-001")
            self.assertIn("T", evt["timestamp"])
            self.assertEqual(evt["objective"], "Calculate repeated-measures ANOVA on empirical clinical dataset")
            self.assertEqual(evt["input_artifacts"], ["01_data/raw_data.xlsx"])
            self.assertEqual(evt["output_artifacts"], ["03_outputs/anova_results.json"])
            self.assertEqual(evt["status"], stat.value)

            # Contract validation helper must pass
            val_res = validate_delegation_event(evt)
            self.assertTrue(val_res.get("valid"), f"Schema validation failed for {etype.value}: {val_res.get('errors')}")

    def test_02_missing_mandatory_fields_fails_closed(self):
        """Schema validation must fail if any of the 8 mandatory fields are omitted."""
        base_event = {
            "contract_version": "1.0.0",
            "event_id": "EVT-TEST-001",
            "event_type": "SUBAGENT_REQUESTED",
            "parent_agent": "academic-orchestrator",
            "child_agent": "statistics-agent",
            "task_id": "TSK-TEST-01",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "objective": "Run ANOVA",
            "input_artifacts": ["data.csv"],
            "output_artifacts": ["out.json"],
            "status": "REQUESTED"
        }

        mandatory_fields = [
            "parent_agent", "child_agent", "task_id", "timestamp",
            "objective", "input_artifacts", "output_artifacts", "status"
        ]

        for field in mandatory_fields:
            corrupt = dict(base_event)
            del corrupt[field]
            val_res = validate_delegation_event(corrupt)
            self.assertFalse(val_res.get("valid"), f"Should have failed when '{field}' is missing")

    def test_03_invalid_event_type_fails_closed(self):
        """Unknown or hallucinated delegation event types must fail schema validation."""
        corrupt = {
            "contract_version": "1.0.0",
            "event_id": "EVT-TEST-002",
            "event_type": "SUBAGENT_HALLUCINATED",
            "parent_agent": "academic-orchestrator",
            "child_agent": "statistics-agent",
            "task_id": "TSK-TEST-02",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "objective": "Run ANOVA",
            "input_artifacts": [],
            "output_artifacts": [],
            "status": "REQUESTED"
        }
        val_res = validate_delegation_event(corrupt)
        self.assertFalse(val_res.get("valid"))

    def test_04_direct_observation_replaces_speculative_inference(self):
        """
        Verifies that TrajectoryEngine directly observes
        academic-orchestrator → invoke_subagent → statistics-agent
        without guessing or inferring.
        """
        # 1. Record observable delegation sequence
        task_id = "TSK-CH4-ANOVA-01"
        self.del_engine.record_subagent_requested(
            parent_agent="academic-orchestrator",
            child_agent="statistics-agent",
            task_id=task_id,
            objective="Execute repeated-measures ANOVA with Mauchly sphericity test",
            input_artifacts=["01_data/rct_dataset.xlsx"],
            output_artifacts=["03_outputs/anova_results.json"]
        )
        self.del_engine.record_subagent_started(
            parent_agent="academic-orchestrator",
            child_agent="statistics-agent",
            task_id=task_id,
            objective="Execute repeated-measures ANOVA with Mauchly sphericity test",
            input_artifacts=["01_data/rct_dataset.xlsx"],
            output_artifacts=["03_outputs/anova_results.json"]
        )
        self.del_engine.record_subagent_completed(
            parent_agent="academic-orchestrator",
            child_agent="statistics-agent",
            task_id=task_id,
            objective="Execute repeated-measures ANOVA with Mauchly sphericity test",
            output_artifacts=["03_outputs/anova_results.json", "03_outputs/anova_table.docx"],
            input_artifacts=["01_data/rct_dataset.xlsx"]
        )
        self.del_engine.record_artifact_returned(
            parent_agent="academic-orchestrator",
            child_agent="statistics-agent",
            task_id=task_id,
            objective="Execute repeated-measures ANOVA with Mauchly sphericity test",
            output_artifacts=["03_outputs/anova_results.json", "03_outputs/anova_table.docx"],
            input_artifacts=["01_data/rct_dataset.xlsx"]
        )

        # 2. Get observable delegation chain
        chains = self.del_engine.get_observable_delegation_chain(task_id=task_id)
        self.assertEqual(len(chains), 1)
        ch = chains[0]
        self.assertEqual(ch["transition"], "academic-orchestrator → invoke_subagent → statistics-agent")
        self.assertEqual(ch["status"], "COMPLETED")
        self.assertEqual(ch["parent_agent"], "academic-orchestrator")
        self.assertEqual(ch["child_agent"], "statistics-agent")
        self.assertIn("SUBAGENT_REQUESTED", ch["lifecycle_events"])
        self.assertIn("SUBAGENT_STARTED", ch["lifecycle_events"])
        self.assertIn("SUBAGENT_COMPLETED", ch["lifecycle_events"])
        self.assertIn("ARTIFACT_RETURNED", ch["lifecycle_events"])

        # 3. TrajectoryEngine builds trajectory directly from observed events
        events = self.traj_engine.load_events()
        trajectory = self.traj_engine.build_trajectory_from_events(
            events=events,
            project_id="PROJ-TEST",
            task_id=task_id,
            experience_id="EXP-TEST-001"
        )
        self.assertGreaterEqual(len(trajectory["subagent_delegations"]), 1)
        delegation = trajectory["subagent_delegations"][0]
        self.assertEqual(delegation["delegator"], "academic-orchestrator")
        self.assertEqual(delegation["delegatee"], "statistics-agent")
        self.assertEqual(delegation["status"], "COMPLETED")
        self.assertIn("anova_results.json", str(delegation.get("handoff_artifact_path") or delegation.get("output_artifacts")))

    def test_05_subagent_failed_event_recorded_on_error(self):
        """When a delegated subagent fails, SUBAGENT_FAILED must be recorded with status FAILED."""
        task_id = "TSK-FAIL-01"
        self.del_engine.record_subagent_requested(
            parent_agent="academic-orchestrator",
            child_agent="data-agent",
            task_id=task_id,
            objective="Clean unengaged Likert rows"
        )
        self.del_engine.record_subagent_started(
            parent_agent="academic-orchestrator",
            child_agent="data-agent",
            task_id=task_id,
            objective="Clean unengaged Likert rows"
        )
        self.del_engine.record_subagent_failed(
            parent_agent="academic-orchestrator",
            child_agent="data-agent",
            task_id=task_id,
            objective="Clean unengaged Likert rows",
            error_message="Missing required column 'ID' in raw data"
        )

        chains = self.del_engine.get_observable_delegation_chain(task_id=task_id)
        self.assertEqual(len(chains), 1)
        self.assertEqual(chains[0]["status"], "FAILED")
        self.assertIn("SUBAGENT_FAILED", chains[0]["lifecycle_events"])

    def test_06_unobserved_delegation_detection_fails_closed(self):
        """Claiming a subagent ran when no physical telemetry exists must raise UnobservedDelegationError."""
        with self.assertRaises(UnobservedDelegationError):
            self.del_engine.verify_no_speculative_inference(
                task_id="TSK-UNOBSERVED-99",
                claimed_child_agent="statistics-agent"
            )

    def test_07_learning_hooks_pre_and_post_tool_use_intercepts_invoke_subagent(self):
        """LearningHooks must emit SUBAGENT_REQUESTED/STARTED on PreToolUse and COMPLETED/ARTIFACT_RETURNED on PostToolUse."""
        mock_payload = {
            "conversationId": "convo-hook-obs-01",
            "workspacePaths": [self.temp_dir],
            "stepIdx": 5,
            "artifactDirectoryPath": os.path.join(self.temp_dir, "artifacts"),
            "modelName": "gemini-2.5-pro",
            "agentName": "academic-orchestrator",
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {
                            "TypeName": "methodology-expert",
                            "Role": "Methodology Architect",
                            "Prompt": json.dumps({
                                "task_id": "TSK-HOOK-001",
                                "parent_agent": "academic-orchestrator",
                                "worker_agent": "methodology-expert",
                                "objective": "Formulate 10-step statistical analysis plan for RCT",
                                "inputs": ["01_data/proposal.docx"],
                                "required_artifacts": ["02_plans/analysis_plan.json"],
                                "acceptance_criteria": ["Power >= 0.80"],
                                "constraints": ["Alpha = 0.05"],
                                "verification_method": "methodology_review",
                                "deadline": "2026-09-20T18:00:00Z"
                            })
                        }
                    ]
                }
            }
        }

        # 1. PreToolUse
        LearningHooks.handle_pre_tool_use(mock_payload)
        events_pre = self.del_engine.load_delegation_events(task_id="TSK-HOOK-001")
        pre_types = [e["event_type"] for e in events_pre]
        self.assertIn("SUBAGENT_REQUESTED", pre_types)
        self.assertIn("SUBAGENT_STARTED", pre_types)

        # 2. PostToolUse (success)
        LearningHooks.capture_agent_trajectory(mock_payload)
        events_post = self.del_engine.load_delegation_events(task_id="TSK-HOOK-001")
        post_types = [e["event_type"] for e in events_post]
        self.assertIn("SUBAGENT_COMPLETED", post_types)
        self.assertIn("ARTIFACT_RETURNED", post_types)

        # 3. Verify observable chain
        chains = self.del_engine.get_observable_delegation_chain(task_id="TSK-HOOK-001")
        self.assertEqual(len(chains), 1)
        self.assertEqual(chains[0]["transition"], "academic-orchestrator → invoke_subagent → methodology-expert")
        self.assertEqual(chains[0]["status"], "COMPLETED")


if __name__ == "__main__":
    unittest.main()
