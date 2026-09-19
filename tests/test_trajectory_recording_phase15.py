#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_trajectory_recording_phase15.py — Test Suite for Phase 15 Factual Trajectory Recording

Verifies:
1. All 11 canonical event types:
   TOOL_CALLED, TOOL_RETURNED, FILE_READ, FILE_WRITTEN, COMMAND_STARTED,
   COMMAND_FINISHED, AGENT_INVOKED, AGENT_RETURNED, VALIDATION_STARTED,
   VALIDATION_FAILED, USER_CORRECTION.
2. Hook payload metadata extraction:
   conversationId, workspacePaths, transcriptPath, toolCall, stepIdx, artifactDirectoryPath, modelName.
3. Transcript parsing extracting actual events without guessing.
4. Zero speculative tool fabrication when no physical events exist.
5. Zero CoT leakage.
6. Schema validity of generated trajectories against contracts/evolution/trajectory.schema.json.
7. Hook dispatcher PreToolUse & PostToolUse lifecycle execution.
"""

import os
import sys
import json
import unittest
import tempfile
import shutil
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HOOKS_DIR = os.path.join(ROOT_DIR, ".agents", "hooks")
for p in (ROOT_DIR, HOOKS_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from scripts.trajectory_engine import (
    TrajectoryEngine,
    TrajectoryEventType,
    sanitize_no_cot,
    PrivateChainOfThoughtLeakError
)
from scripts.academic_experience_recorder import (
    AcademicExperienceRecorder,
    sanitize_no_cot as exp_sanitize_no_cot
)
from contracts.contract_validator import validate_trajectory
from learning_hooks import LearningHooks
from hook_dispatcher import dispatch_event


class TestTrajectoryRecordingPhase15(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="phase15_trajectory_test_")
        self.state_dir = os.path.join(self.temp_dir, "state")
        os.makedirs(self.state_dir, exist_ok=True)
        self.engine = TrajectoryEngine(state_dir=self.state_dir, project_root=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_all_11_event_types_recorded_and_loaded(self):
        """TrajectoryEngine must record and load all 11 canonical event types."""
        mock_payload = {
            "conversationId": "cid-test-11-events",
            "workspacePaths": [self.temp_dir],
            "stepIdx": 10,
            "artifactDirectoryPath": os.path.join(self.temp_dir, "artifacts"),
            "modelName": "gemini-2.5-pro",
            "transcriptPath": os.path.join(self.temp_dir, "transcript.jsonl")
        }

        for idx, etype in enumerate(TrajectoryEventType, 1):
            mock_payload["stepIdx"] = idx
            mock_payload["toolCall"] = {"name": f"tool_{etype.value.lower()}", "args": {"arg1": "val1"}}
            evt = self.engine.record_event(
                event_type=etype,
                payload=mock_payload,
                details={"custom_detail": f"info_{etype.value}"},
                actor="test-agent"
            )
            self.assertEqual(evt["event_type"], etype.value)
            self.assertEqual(evt["conversation_id"], "cid-test-11-events")
            self.assertEqual(evt["step_index"], idx)
            self.assertEqual(evt["model_name"], "gemini-2.5-pro")

        loaded = self.engine.load_events()
        self.assertEqual(len(loaded), 11)
        loaded_types = {e["event_type"] for e in loaded}
        for etype in TrajectoryEventType:
            self.assertIn(etype.value, loaded_types)

    def test_02_hook_payload_metadata_source_of_truth(self):
        """Metadata from Antigravity hook payload must be faithfully preserved."""
        payload = {
            "conversationId": "convo-source-of-truth-99",
            "workspacePaths": [self.temp_dir, "/another/path"],
            "stepIdx": 42,
            "artifactDirectoryPath": "/brain/convo-99",
            "modelName": "gemini-3.0-ultra",
            "transcriptPath": "/logs/convo-99/transcript.jsonl",
            "toolCall": {
                "name": "view_file",
                "args": {"AbsolutePath": "/home/user/paper.docx"}
            }
        }

        evt = self.engine.record_event(
            TrajectoryEventType.FILE_READ,
            payload=payload,
            details={"file_path": "/home/user/paper.docx"}
        )

        self.assertEqual(evt["conversation_id"], "convo-source-of-truth-99")
        self.assertEqual(evt["step_index"], 42)
        self.assertEqual(evt["artifact_directory_path"], "/brain/convo-99")
        self.assertEqual(evt["model_name"], "gemini-3.0-ultra")
        self.assertEqual(evt["transcript_path"], "/logs/convo-99/transcript.jsonl")
        self.assertEqual(evt["tool_name"], "view_file")

    def test_03_transcript_parsing_extracts_actual_events(self):
        """Parsing transcript.jsonl must extract actual observable events without inference."""
        transcript_path = os.path.join(self.temp_dir, "test_transcript.jsonl")
        with open(transcript_path, "w", encoding="utf-8") as f:
            # 1. User correction
            f.write(json.dumps({
                "step_index": 1,
                "type": "USER_INPUT",
                "content": "The beta coefficient is wrong, please fix the mediation model."
            }) + "\n")
            # 2. Planner tool calls
            f.write(json.dumps({
                "step_index": 2,
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {"name": "view_file", "args": {"AbsolutePath": "/workspace/result.json"}},
                    {"name": "write_to_file", "args": {"TargetFile": "/workspace/fixed.md"}},
                    {"name": "run_command", "args": {"CommandLine": "python3 .agents/skills/mediation/scripts/mediation.py"}},
                    {"name": "run_command", "args": {"CommandLine": "python3 scripts/validate_stage.py"}},
                    {"name": "invoke_subagent", "args": {"Subagents": [{"TypeName": "statistics-agent", "Role": "Statistical Modeler", "Prompt": "Run mediation"}]}}
                ]
            }) + "\n")

        events = self.engine.extract_events_from_transcript(transcript_path, cid="test-cid-trans")
        self.assertGreaterEqual(len(events), 6)

        event_types = [e["event_type"] for e in events]
        self.assertIn("USER_CORRECTION", event_types)
        self.assertIn("TOOL_CALLED", event_types)
        self.assertIn("FILE_READ", event_types)
        self.assertIn("FILE_WRITTEN", event_types)
        self.assertIn("COMMAND_STARTED", event_types)
        self.assertIn("VALIDATION_STARTED", event_types)
        self.assertIn("AGENT_INVOKED", event_types)

    def test_04_zero_speculative_fabrication_when_no_physical_events(self):
        """If no physical events occurred, tool_usages and skill_activations must be empty."""
        stage_dir = os.path.join(self.temp_dir, "01_demographics")
        os.makedirs(stage_dir, exist_ok=True)
        # Create artifacts on disk
        with open(os.path.join(stage_dir, "table.docx"), "wb") as f:
            f.write(b"DOCX")
        with open(os.path.join(stage_dir, "table.md"), "w") as f:
            f.write("# Demo Table\n")
        with open(os.path.join(stage_dir, "table.json"), "w") as f:
            json.dump({"n": 100}, f)

        # Empty state dir -> no recorded tool events
        rec = AcademicExperienceRecorder(store_dir=os.path.join(self.temp_dir, "learning"), project_root=self.temp_dir)
        res = rec.record_from_stage(stage_dir=stage_dir, project_id="test_no_fab", outcome="SUCCESS")

        trj_data = rec.get_trajectory(res["experience_id"])
        # tool_usages and skill_activations must be empty list, NOT hallucinated run_command
        self.assertEqual(trj_data["tool_usages"], [])
        self.assertEqual(trj_data["skill_activations"], [])
        self.assertEqual(trj_data["subagent_delegations"], [])

        # Still strictly schema compliant
        val_res = validate_trajectory(trj_data)
        self.assertTrue(val_res["valid"], f"Trajectory validation failed: {val_res.get('error')}")

    def test_05_trajectory_built_from_factual_events_is_schema_valid(self):
        """Trajectories built from actual events must validate against trajectory.schema.json."""
        events = [
            {
                "event_id": "EVT-1",
                "event_type": TrajectoryEventType.TOOL_CALLED.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": "academic-orchestrator",
                "tool_name": "view_file",
                "details": {"arguments_summary": {"AbsolutePath": "/workspace/data.csv"}}
            },
            {
                "event_id": "EVT-2",
                "event_type": TrajectoryEventType.FILE_READ.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": "academic-orchestrator",
                "tool_name": "view_file",
                "details": {"file_path": "/workspace/data.csv"}
            },
            {
                "event_id": "EVT-3",
                "event_type": TrajectoryEventType.COMMAND_STARTED.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": "statistics-agent",
                "tool_name": "run_command",
                "details": {
                    "command_line": "python3 .agents/skills/descriptive-statistics/scripts/descriptive_statistics.py",
                    "exit_code": 0,
                    "duration_seconds": 2.5
                }
            },
            {
                "event_id": "EVT-4",
                "event_type": TrajectoryEventType.AGENT_INVOKED.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": "academic-orchestrator",
                "tool_name": "invoke_subagent",
                "details": {
                    "subagent_type": "statistics-agent",
                    "subagent_role": "Statistical Analyst",
                    "prompt_summary": "Compute descriptives"
                }
            },
            {
                "event_id": "EVT-5",
                "event_type": TrajectoryEventType.VALIDATION_FAILED.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": "validation-agent",
                "tool_name": "run_command",
                "details": {
                    "validator_name": "DescriptivesValidator",
                    "failed_checks": ["kurtosis_excessive"]
                }
            },
            {
                "event_id": "EVT-6",
                "event_type": TrajectoryEventType.USER_CORRECTION.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": "user",
                "details": {"correction_text": "Please remove outliers before re-running."}
            }
        ]

        trj = self.engine.build_trajectory_from_events(
            events=events,
            project_id="test_schema_proj",
            task_id="01_descriptives",
            experience_id="EXP-TEST-001",
            outcome="FAILURE"
        )

        val_res = validate_trajectory(trj)
        self.assertTrue(val_res["valid"], f"Trajectory validation failed: {val_res.get('error')}")
        self.assertEqual(len(trj["ordered_actions"]), 6)
        self.assertEqual(len(trj["skill_activations"]), 1)
        self.assertEqual(trj["skill_activations"][0]["skill_name"], "descriptive-statistics")
        self.assertEqual(len(trj["subagent_delegations"]), 1)
        self.assertEqual(len(trj["validation_events"]), 1)
        self.assertEqual(len(trj["feedback"]), 1)

    def test_06_zero_cot_leakage_enforcement(self):
        """Any attempt to inject private CoT must raise PrivateChainOfThoughtLeakError."""
        bad_payload = {
            "conversationId": "cid-bad",
            "thinking": "Secret model reasoning tokens here",
            "toolCall": {"name": "run_command"}
        }

        with self.assertRaises(PrivateChainOfThoughtLeakError):
            self.engine.record_event(
                TrajectoryEventType.TOOL_CALLED,
                payload={"conversationId": "cid-bad"},
                details={"thinking": "illegal reasoning"}
            )

    def test_07_hook_dispatcher_pre_and_post_tool_use_events(self):
        """Hook dispatcher must emit TOOL_CALLED and TOOL_RETURNED via LearningHooks."""
        payload_pre = {
            "conversationId": "convo-hook-test",
            "workspacePaths": [self.temp_dir],
            "stepIdx": 1,
            "toolCall": {
                "name": "view_file",
                "args": {"AbsolutePath": "/workspace/doc.txt"}
            }
        }
        res_pre = dispatch_event("PreToolUse", payload_pre)
        self.assertEqual(res_pre.get("decision", "allow"), "allow")

        payload_post = {
            "conversationId": "convo-hook-test",
            "workspacePaths": [self.temp_dir],
            "stepIdx": 1,
            "toolCall": {
                "name": "view_file",
                "args": {"AbsolutePath": "/workspace/doc.txt"}
            },
            "error": None
        }
        dispatch_event("PostToolUse", payload_post)

        events = self.engine.load_events()
        event_types = [e["event_type"] for e in events]
        self.assertIn("TOOL_CALLED", event_types)
        self.assertIn("FILE_READ", event_types)
        self.assertIn("TOOL_RETURNED", event_types)


if __name__ == "__main__":
    unittest.main()
