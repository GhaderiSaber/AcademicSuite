#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_orchestrator_subagent_yielding_and_remediation.py — Tests for Academic Orchestrator Yielding & Remediation Phase

Verifies:
1. Subagent Yielding: When academic-orchestrator invokes a subagent and ends turn awaiting completion,
   handle_stop allows stop without demanding stage completion reports or asserting incomplete deliverables.
2. Truncation Resilience: When transcript.jsonl has truncated tool calls, evaluation-agent invocation is still
   reliably detected, ensuring state transitions to REMEDIATION_PHASE after graduation.
3. Actionable Repair Prescription (ARP): When validation-agent emits an ARP directing academic-writer to re-generate
   tables after candidates have graduated, lifecycle state remains REMEDIATION_PHASE (not reset to LEARNING_REQUIRED).
4. Delivery Worker Authorization: In REMEDIATION_PHASE, delegating to academic-writer is authorized.
5. Stage Completion Gate: When all subagents have completed and orchestrator presents final deliverable,
   Directive 11 stage reporting and Directive 3 artifact existence are properly enforced.
"""

import json
import os
import pytest
from typing import Dict, Any, List

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ORCH_GUARD_DIR = os.path.join(ROOT_DIR, ".agents", "agents", "academic-orchestrator")

import sys
if ORCH_GUARD_DIR not in sys.path:
    sys.path.insert(0, ORCH_GUARD_DIR)
import guard


class TestOrchestratorYieldingAndRemediation:

    def test_01_yielding_when_subagent_is_pending_allows_stop(self, tmp_path):
        """When a subagent was launched and has not sent a completion message, handle_stop must allow stop."""
        conv_id = "test-conv-001"
        sub_conv_id = "worker-sub-1234"
        
        # Prepare transcript where invoke_subagent was called, and orchestrator pauses awaiting completion
        records = [
            {
                "type": "USER_INPUT",
                "content": "Please format the chapter 4 tables."
            },
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {
                            "Subagents": [
                                {
                                    "TypeName": "academic-writer",
                                    "Role": "Master Academic Drafter",
                                    "Prompt": json.dumps({
                                        "task_id": "TSK-TEST-01",
                                        "stage": "Format Tables",
                                        "worker_agent": "academic-writer",
                                        "inputs": ["03_deliverables/Chapter_4_Results.md"],
                                        "required_artifacts": ["03_deliverables/NonExistentDeliverable.docx"]
                                    })
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "GENERIC",
                "source": "MODEL",
                "content": f'Created the following subagents:\n{{\n  "conversationId": "{sub_conv_id}"\n}}'
            },
            {
                "type": "PLANNER_RESPONSE",
                "content": "I have dispatched academic-writer to format the tables. Execution is paused awaiting worker completion.",
                "tool_calls": []
            }
        ]

        t_file = tmp_path / "transcript.jsonl"
        with open(t_file, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

        payload = {
            "transcriptPath": str(t_file),
            "workspacePaths": [str(tmp_path)],
            "isSubagent": False
        }

        res = guard.handle_stop(payload)
        assert res.get("decision") == "allow", f"Expected allow when yielding to subagent, got: {res}"

    def test_02_yielding_by_text_phrasing_allows_stop(self, tmp_path):
        """When orchestrator text explicitly states it is paused awaiting worker, handle_stop allows stop."""
        records = [
            {
                "type": "USER_INPUT",
                "content": "Begin analysis."
            },
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {"Subagents": [{"TypeName": "trajectory-analyzer", "Role": "Reconstructor", "Prompt": "task"}]}
                    }
                ]
            },
            {
                "type": "PLANNER_RESPONSE",
                "content": "I have initiated the Continuous Learning Cascade by delegating task TSK-001 to trajectory-analyzer. Execution is paused awaiting worker completion.",
                "tool_calls": []
            }
        ]

        t_file = tmp_path / "transcript.jsonl"
        with open(t_file, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

        payload = {
            "transcriptPath": str(t_file),
            "workspacePaths": [str(tmp_path)],
            "isSubagent": False
        }

        res = guard.handle_stop(payload)
        assert res.get("decision") == "allow", f"Expected allow when pausing awaiting worker, got: {res}"

    def test_03_truncation_resilient_evaluation_agent_detection(self):
        """When tool_calls is truncated in transcript, evaluation-agent is still detected."""
        # Simulated truncated record from transcript.jsonl
        truncated_record = {
            "type": "PLANNER_RESPONSE",
            "tool_calls": [
                {
                    "name": "invoke_subagent",
                    "args": {
                        "Subagents": '[{"Model":"inherit","Prompt":"Active context... Task: candidate_evaluation | Agent: evaluation-agent | Project: cross-project... (truncated)'
                    }
                }
            ],
            "truncated_fields": ["tool_calls"]
        }

        records = [
            {"type": "USER_INPUT", "content": "Initial prompt"},
            truncated_record
        ]

        state, pending_cands, desc, label = guard.get_defect_and_learning_lifecycle_state(records, [ROOT_DIR])
        # Since evaluation was detected and candidates on disk are graduated, state should be REMEDIATION_PHASE or NO_DEFECT
        assert state in ("REMEDIATION_PHASE", "NO_DEFECT"), f"Expected REMEDIATION_PHASE/NO_DEFECT, got: {state}"

    def test_04_actionable_repair_prescription_keeps_remediation_phase(self):
        """When validation-agent issues an ARP for academic-writer after graduation, state remains REMEDIATION_PHASE."""
        records = [
            {"type": "USER_INPUT", "content": "Tables are unaligned."},
            # Evaluation agent invocation
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {"Subagents": [{"TypeName": "evaluation-agent", "Role": "Evaluator", "Prompt": "evaluate"}]}
                    }
                ]
            },
            # Validation agent emits Actionable Repair Prescription for academic-writer
            {
                "type": "SYSTEM_MESSAGE",
                "content": (
                    "[Message] timestamp=2026-10-02T12:00:00Z sender=val-agent-uuid priority=MESSAGE_PRIORITY_HIGH content="
                    "REJECT / DEFECT HUNTING VERDICT: The deliverables are strictly FAILED due to corrupt markdown tokens.\n"
                    "Correction Required (academic-writer / apa-reporting): Re-generate Tables 15, 16, 18 using pristine array natively."
                )
            }
        ]

        state, pending_cands, desc, label = guard.get_defect_and_learning_lifecycle_state(records, [ROOT_DIR])
        assert state == "REMEDIATION_PHASE", f"Expected REMEDIATION_PHASE under ARP, got: {state}"

    def test_05_remediation_phase_authorizes_academic_writer(self, tmp_path):
        """In REMEDIATION_PHASE, pre_tool_use allows invoking academic-writer."""
        records = [
            {"type": "USER_INPUT", "content": "Tables are unaligned."},
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {"Subagents": [{"TypeName": "evaluation-agent", "Role": "Evaluator", "Prompt": "evaluate"}]}
                    }
                ]
            }
        ]

        t_file = tmp_path / "transcript.jsonl"
        with open(t_file, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

        # Fake input file and Gate 3 clearance payloads
        input_f = tmp_path / "input.md"
        input_f.write_text("# Input")

        deliv_dir = tmp_path / "03_deliverables"
        deliv_dir.mkdir(parents=True, exist_ok=True)
        (deliv_dir / "05_macro_model_payload.json").write_text('{"fit": "good"}')
        (deliv_dir / "06_hypothesis_1_payload.json").write_text('{"beta": 0.4}')
        (deliv_dir / "08_mediation_analysis_payload.json").write_text('{"indirect": 0.2}')
        (deliv_dir / "master_decision_matrix.json").write_text('{"decision": "accept"}')

        cde_envelope = {
            "task_id": "TSK-2026-RECOMPILE-DOCX",
            "stage": "Remediation Phase: Recompile Chapter 4 DOCX",
            "worker_agent": "academic-writer",
            "objective": "Recompile chapter 4 tables using 3-column format",
            "inputs": [str(input_f)],
            "required_artifacts": ["03_deliverables/Chapter_4_Results.docx"]
        }

        payload = {
            "tool_name": "invoke_subagent",
            "args": {
                "Subagents": [
                    {
                        "TypeName": "academic-writer",
                        "Role": "Master Academic Drafter",
                        "Prompt": json.dumps(cde_envelope)
                    }
                ]
            },
            "transcriptPath": str(t_file),
            "workspacePaths": [str(tmp_path)]
        }

        res = guard.handle_pre_tool_use(payload)
        assert res.get("decision") == "allow", f"Expected academic-writer allowed in REMEDIATION_PHASE, got: {res}"

    def test_06_stage_conclusion_enforces_directive_11_and_directive_3(self, tmp_path):
        """When all subagents have completed and orchestrator speaks to user without report, Directive 11 is enforced."""
        sub_conv_id = "worker-done-1234"
        
        records = [
            {"type": "USER_INPUT", "content": "Please generate chapter 4."},
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {
                            "Subagents": [
                                {
                                    "TypeName": "academic-writer",
                                    "Role": "Master Academic Drafter",
                                    "Prompt": json.dumps({
                                        "task_id": "TSK-01",
                                        "stage": "Write chapter",
                                        "worker_agent": "academic-writer",
                                        "inputs": ["03_deliverables/input.md"],
                                        "required_artifacts": ["03_deliverables/MissingDocx.docx"]
                                    })
                                }
                            ]
                        }
                    }
                ]
            },
            {
                "type": "GENERIC",
                "content": f'Created the following subagents:\n{{\n  "conversationId": "{sub_conv_id}"\n}}'
            },
            # Subagent message arrives (completed!)
            {
                "type": "SYSTEM_MESSAGE",
                "content": f"[Message] timestamp=2026-10-02T12:00:00Z sender={sub_conv_id} priority=MESSAGE_PRIORITY_HIGH content=Done generating."
            },
            # Orchestrator responds to user without stage report or confirmation request
            {
                "type": "PLANNER_RESPONSE",
                "content": "Here is the response.",
                "tool_calls": []
            }
        ]

        t_file = tmp_path / "transcript.jsonl"
        with open(t_file, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

        payload = {
            "transcriptPath": str(t_file),
            "workspacePaths": [str(tmp_path)],
            "isSubagent": False
        }

        res = guard.handle_stop(payload)
        # Should be blocked because subagent completed, but stage report / confirmation is missing
        assert res.get("decision") == "continue"
        assert "Directive 11" in res.get("reason", "")
