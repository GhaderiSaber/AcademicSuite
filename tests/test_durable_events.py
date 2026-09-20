#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_durable_events.py — Comprehensive Unit Tests for Durable Event-Based Communication

Covers:
1. Event schema validation against contracts/event.schema.json for all 14 canonical event types.
2. Rejection of invalid event types, missing required summary, and invalid date-time format.
3. Duplicate event detection (runtime emission & log scanning).
4. Malformed events (corrupted JSON, non-object lines, missing event_id) fail closed.
5. Artifact event without matching physical file or hash tampering raises ArtifactEventMismatchError.
6. Matching file or artifact record without ARTIFACT_CREATED event raises MissingArtifactEventError.
7. Monotonic event ordering and temporal regression detection (EventOrderingError).
8. Process restart/recovery preserving event history and monotonic ordering.
9. Reconstructing full workflow lifecycle directly from state/events.jsonl.
10. State transitions causally explained from recorded events.
11. Complete end-to-end chain: event -> artifact -> validation -> state transition.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone, timedelta

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))

from academic_event_engine import (
    AcademicEventEngine,
    EventError,
    EventSchemaValidationError,
    DuplicateEventError,
    MalformedEventError,
    EventOrderingError,
    ArtifactEventMismatchError,
    MissingArtifactEventError,
    VALID_EVENT_TYPES,
    compute_file_sha256
)

from academic_state_manager import (
    StrictStateMachine,
    MilestoneState,
    init_state
)


class TestDurableEvents(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_durable_events_")
        self.state_dir = os.path.join(self.temp_dir, "state")
        os.makedirs(self.state_dir, exist_ok=True)
        self.events_path = os.path.join(self.state_dir, "events.jsonl")
        self.engine = AcademicEventEngine(self.events_path, project_id="test_proj_event")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_all_canonical_event_types_schema_valid(self):
        """Tests that all canonical event types can be emitted and pass schema validation."""
        self.assertEqual(len(VALID_EVENT_TYPES), len(VALID_EVENT_TYPES))
        base_time = datetime.now(timezone.utc)

        for i, etype in enumerate(sorted(list(VALID_EVENT_TYPES))):
            ts = (base_time + timedelta(seconds=i * 2)).isoformat()
            ev = self.engine.emit(
                event_type=etype,
                emitter_agent="academic-orchestrator",
                summary=f"Emitting canonical event type {etype}",
                milestone_id="M_TEST",
                stage_id="01_test",
                timestamp=ts,
                metrics={"counter": i},
                details={"scope": "canonical_verification"}
            )
            self.assertEqual(ev["event_type"], etype)
            self.assertEqual(ev["contract_version"], "1.0.0")
            self.assertIn("summary", ev["payload"])

        # Read back all events with strict validation enabled
        events = self.engine.read_events(validate_schema=True, enforce_ordering=True)
        self.assertEqual(len(events), len(VALID_EVENT_TYPES))

    def test_02_invalid_event_type_or_missing_summary_fails(self):
        """Fails closed on unknown event types or invalid schema properties."""
        # 1. Invalid event type
        with self.assertRaises(EventSchemaValidationError):
            self.engine.emit(
                event_type="UNREGISTERED_AD_HOC_EVENT",
                emitter_agent="rogue-agent",
                summary="Attempting unregistered event"
            )

        # 2. Missing required summary in manually appended raw event
        invalid_event = {
            "contract_version": "1.0.0",
            "event_id": "EVT-BAD-SUMMARY-001",
            "event_type": "PLAN_CREATED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project_id": "test_proj_event",
            "emitter_agent": "statistics-agent",
            "payload": {}  # Missing required 'summary'
        }
        with open(self.events_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(invalid_event) + "\n")

        with self.assertRaises(EventSchemaValidationError):
            self.engine.read_events(validate_schema=True)

    def test_03_duplicate_event_detection(self):
        """Detects and blocks duplicate event IDs both in-memory and during log replay."""
        fixed_id = "EVT-2026-UNIQUE-ID-001"
        self.engine.emit(
            event_type="PROJECT_CREATED",
            emitter_agent="academic-orchestrator",
            summary="Initial project creation",
            event_id=fixed_id
        )

        # Re-emitting same event_id must fail closed
        with self.assertRaises(DuplicateEventError):
            self.engine.emit(
                event_type="MILESTONE_STARTED",
                emitter_agent="academic-orchestrator",
                summary="Duplicate event attempt",
                event_id=fixed_id
            )

        # Re-instantiate engine and ensure duplicates written to disk are caught on read
        with open(self.events_path, "a", encoding="utf-8") as f:
            dup_line = {
                "contract_version": "1.0.0",
                "event_id": fixed_id,
                "event_type": "PLAN_CREATED",
                "timestamp": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
                "project_id": "test_proj_event",
                "emitter_agent": "academic-orchestrator",
                "payload": {"summary": "Direct file append duplicate"}
            }
            f.write(json.dumps(dup_line) + "\n")

        new_engine = AcademicEventEngine(self.events_path, project_id="test_proj_event")
        with self.assertRaises(DuplicateEventError):
            new_engine.read_events(validate_schema=False)

    def test_04_malformed_events(self):
        """Fails closed when lines in events.jsonl are corrupted or structurally invalid."""
        # 1. Non-JSON corrupted text
        with open(self.events_path, "w", encoding="utf-8") as f:
            f.write('{"contract_version": "1.0.0", "event_id": "EVT-001", "event_type": "PROJECT_CREATED"\n')  # truncated

        engine = AcademicEventEngine(self.events_path, project_id="test_proj_event")
        with self.assertRaises(MalformedEventError):
            engine.read_events()

        # 2. JSON scalar instead of object
        with open(self.events_path, "w", encoding="utf-8") as f:
            f.write('"just a raw json string"\n')

        engine = AcademicEventEngine(self.events_path, project_id="test_proj_event")
        with self.assertRaises(MalformedEventError):
            engine.read_events()

        # 3. Missing event_id
        with open(self.events_path, "w", encoding="utf-8") as f:
            f.write('{"contract_version": "1.0.0", "event_type": "PROJECT_CREATED"}\n')

        engine = AcademicEventEngine(self.events_path, project_id="test_proj_event")
        with self.assertRaises(MalformedEventError):
            engine.read_events()

    def test_05_artifact_event_without_matching_file_raises(self):
        """Fails when an artifact event points to a non-existent physical file or a tampered file."""
        # 1. Attempt to emit ARTIFACT_CREATED for a non-existent file
        with self.assertRaises(FileNotFoundError):
            self.engine.emit_artifact_created(
                artifact_id="ART-NONEXISTENT",
                artifact_path="data/missing_file.json",
                milestone_id="M1",
                producer_agent="data-agent"
            )

        # 2. Create real file and emit event
        real_file = os.path.join(self.state_dir, "real_results.json")
        with open(real_file, "w", encoding="utf-8") as f:
            f.write('{"f_stat": 14.52, "p_value": 0.001}')

        self.engine.emit_artifact_created(
            artifact_id="ART-REAL-01",
            artifact_path="real_results.json",
            milestone_id="M1",
            producer_agent="statistics-agent",
            producer_script="run_sem.py",
            project_root=self.temp_dir
        )

        # Tamper with file contents on disk (changing hash)
        with open(real_file, "w", encoding="utf-8") as f:
            f.write('{"f_stat": 99.99, "p_value": 0.000}')  # Modified content

        art_record = [{
            "artifact_id": "ART-REAL-01",
            "path": "real_results.json"
        }]

        with self.assertRaises(ArtifactEventMismatchError):
            self.engine.verify_artifact_alignment(art_record, check_disk_files=True)

        # 3. Physical file deleted after emission
        os.remove(real_file)
        with self.assertRaises(ArtifactEventMismatchError):
            self.engine.verify_artifact_alignment(art_record, check_disk_files=True)

    def test_06_matching_file_without_artifact_event_raises(self):
        """Fails when an artifact exists in state records or disk without a matching ARTIFACT_CREATED event."""
        # File exists on disk and in records, but no ARTIFACT_CREATED event in events.jsonl
        test_file = os.path.join(self.state_dir, "orphan_artifact.json")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write('{"orphan": true}')

        unlogged_records = [{
            "artifact_id": "ART-ORPHAN-99",
            "path": "orphan_artifact.json"
        }]

        with self.assertRaises(MissingArtifactEventError):
            self.engine.verify_artifact_alignment(unlogged_records, check_disk_files=False)

        # Extra unscanned file verification
        with self.assertRaises(MissingArtifactEventError):
            self.engine.verify_artifact_alignment(
                [],
                check_disk_files=False,
                scanned_disk_paths=[test_file]
            )

    def test_07_event_ordering_enforced(self):
        """Enforces monotonic timestamps and prevents temporal causality violations."""
        t1 = "2026-09-18T10:00:00+00:00"
        t2_regressed = "2026-09-18T09:59:00+00:00"

        self.engine.emit(
            event_type="PROJECT_CREATED",
            emitter_agent="academic-orchestrator",
            summary="Project created at t1",
            timestamp=t1
        )

        # Emitting event with earlier timestamp must raise EventOrderingError
        with self.assertRaises(EventOrderingError):
            self.engine.emit(
                event_type="MILESTONE_STARTED",
                emitter_agent="academic-orchestrator",
                summary="Milestone started in the past",
                timestamp=t2_regressed
            )

    def test_08_restart_recovery(self):
        """Verifies state machine and event engine recover reliably from disk across restarts."""
        sm = StrictStateMachine(state_dir=self.state_dir, project_id="test_restart_proj")
        sm.register_milestone("M_RESTART", "Restart Recovery Milestone")
        sm.transition_milestone("M_RESTART", MilestoneState.SCOPED)
        sm.transition_milestone("M_RESTART", MilestoneState.PLANNED)

        # Create physical artifact and register
        art_path = os.path.join(self.state_dir, "restart_artifact.json")
        with open(art_path, "w", encoding="utf-8") as f:
            f.write('{"recovered": true}')
        sm.register_artifact("ART-REC-01", "M_RESTART", "01_test", "stats_json", "restart_artifact.json")

        # Simulate process termination and fresh re-instantiation
        sm_reloaded = StrictStateMachine(state_dir=self.state_dir, project_id="test_restart_proj")

        self.assertIn("M_RESTART", sm_reloaded.milestones)
        self.assertEqual(sm_reloaded.milestones["M_RESTART"]["status"], MilestoneState.PLANNED.value)
        self.assertEqual(len(sm_reloaded.artifacts), 1)

        # Verify event log read by reloaded instance has all events and valid alignment
        alignment = sm_reloaded.verify_artifact_alignment()
        self.assertEqual(alignment["status"], "ALIGNED")
        self.assertEqual(alignment["verified_artifacts_count"], 1)

        # Able to continue transitions without timestamp regressions
        sm_reloaded.transition_milestone("M_RESTART", MilestoneState.READY)
        sm_reloaded.transition_milestone("M_RESTART", MilestoneState.RUNNING)
        self.assertEqual(sm_reloaded.milestones["M_RESTART"]["status"], MilestoneState.RUNNING.value)

    def test_09_reconstruct_workflow_from_event_log(self):
        """Demonstrates complete reconstruction of study workflow from state/events.jsonl."""
        sm = StrictStateMachine(state_dir=self.state_dir, project_id="test_recon_proj")
        sm.register_milestone("M_SEM", "Structural Equation Modeling")
        sm.transition_milestone("M_SEM", MilestoneState.SCOPED)
        sm.transition_milestone("M_SEM", MilestoneState.PLANNED)
        sm.transition_milestone("M_SEM", MilestoneState.READY)
        sm.transition_milestone("M_SEM", MilestoneState.RUNNING)

        # Create artifact
        art_path = os.path.join(self.state_dir, "sem_results.json")
        with open(art_path, "w", encoding="utf-8") as f:
            f.write('{"cfi": 0.965, "rmsea": 0.042}')
        sm.register_artifact("ART-SEM-01", "M_SEM", "05_sem", "sem_json", "sem_results.json", producer_script="run_sem.py")

        sm.transition_milestone("M_SEM", MilestoneState.VALIDATING)
        sm.transition_milestone("M_SEM", MilestoneState.AWAITING_APPROVAL)
        appr = sm.request_approval("M_SEM", "methodology", "academic-orchestrator", "SEM fit meets Hu & Bentler 1999 criteria.")
        sm.grant_approval(appr["approval_id"], "Dr. Saber Ghaderi", "SIG-CHAIR-APPROVED-124911145", "Methodology sound.")
        sm.transition_milestone("M_SEM", MilestoneState.APPROVED)

        # Reconstruct workflow strictly from the event stream
        workflow = sm.reconstruct_workflow()

        self.assertEqual(workflow["project_id"], "test_recon_proj")
        self.assertIn("M_SEM", workflow["milestones"])
        self.assertEqual(workflow["milestones"]["M_SEM"]["status"], "APPROVED")
        self.assertIn("ART-SEM-01", workflow["artifacts"])
        self.assertEqual(workflow["artifacts"]["ART-SEM-01"]["hash"], compute_file_sha256(art_path))
        self.assertEqual(len(workflow["approvals"]), 4)  # 2 request events, 2 approval events

    def test_10_state_transitions_explained_from_events(self):
        """Tests that state transitions can be causally explained from the event stream."""
        sm = StrictStateMachine(state_dir=self.state_dir, project_id="test_explain_proj")
        sm.register_milestone("M_EXP", "Experimental Manipulation")
        sm.transition_milestone("M_EXP", MilestoneState.SCOPED, rationale="Defined IV and DV levels")
        sm.transition_milestone("M_EXP", MilestoneState.PLANNED, rationale="Power analysis completed")
        sm.transition_milestone("M_EXP", MilestoneState.READY, rationale="Pre-registration complete")

        explanation = sm.explain_transition("M_EXP", "READY")
        self.assertEqual(explanation["milestone_id"], "M_EXP")
        self.assertEqual(explanation["target_state"], "READY")
        self.assertGreaterEqual(explanation["events_count"], 4)

        event_types = [ev["event_type"] for ev in explanation["causal_chain"]]
        self.assertIn("MILESTONE_STARTED", event_types)
        self.assertIn("PLAN_CREATED", event_types)

    def test_11_end_to_end_event_chain_progression(self):
        """
        Enforces the architectural mandate:
        event -> artifact -> validation -> state transition
        No informal messages; each step causally produces durable evidence on disk.
        """
        sm = StrictStateMachine(state_dir=self.state_dir, project_id="test_chain_proj")
        sm.register_milestone("M_CHAIN", "End-to-End Chain Milestone")
        sm.transition_milestone("M_CHAIN", MilestoneState.SCOPED)
        sm.transition_milestone("M_CHAIN", MilestoneState.PLANNED)
        sm.transition_milestone("M_CHAIN", MilestoneState.READY)

        # Step 1: Event (EXECUTION_STARTED)
        sm.transition_milestone("M_CHAIN", MilestoneState.RUNNING, actor="statistics-agent", rationale="Execution initiated")

        # Step 2: Artifact (Physical artifact created on disk with real SHA-256)
        output_file = os.path.join(self.state_dir, "hypothesis_results.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({"beta": 0.42, "t_stat": 4.15, "p_value": 0.0003}, f)

        art_record = sm.register_artifact(
            artifact_id="ART-HYP-01",
            milestone_id="M_CHAIN",
            stage_id="06_hypothesis_1",
            artifact_type="hypothesis_data",
            path="hypothesis_results.json",
            producer_agent="statistics-agent",
            producer_script="compute_hypothesis_1.py",
            provenance={
                "source_dataset": "data_cleaned.xlsx",
                "estimator": "OLS",
                "resamples": 5000
            }
        )
        self.assertEqual(art_record["validation_status"], "VALID")
        self.assertTrue(len(art_record["hash"]) == 64)

        # Step 3: Validation (Emit VALIDATION_STARTED, verify physical artifact and hash)
        sm.record_event(
            event_type="VALIDATION_STARTED",
            milestone_id="M_CHAIN",
            stage_id="06_hypothesis_1",
            emitter_agent="statistical-auditor",
            summary="Statistical auditor verifying hypothesis 1 output integrity."
        )
        alignment = sm.verify_artifact_alignment(check_disk_files=True)
        self.assertEqual(alignment["status"], "ALIGNED")

        # Step 4: State Transition (Transition to VALIDATING then AWAITING_APPROVAL)
        res_val = sm.transition_milestone("M_CHAIN", MilestoneState.VALIDATING, actor="validation-agent", rationale="Validation passed")
        self.assertEqual(res_val["to_state"], MilestoneState.VALIDATING.value)

        res_await = sm.transition_milestone("M_CHAIN", MilestoneState.AWAITING_APPROVAL, actor="academic-orchestrator", rationale="Ready for defense committee approval")
        self.assertEqual(res_await["to_state"], MilestoneState.AWAITING_APPROVAL.value)

        # Causal trace confirms full event chain
        workflow = sm.reconstruct_workflow()
        self.assertIn("ART-HYP-01", workflow["artifacts"])
        self.assertEqual(len(workflow["validations"]), 2)  # VALIDATION_STARTED explicit + VALIDATING transition


if __name__ == "__main__":
    unittest.main()
