#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_trajectory_analyzer_delegation_prompts.py — Verification for Trajectory Analyzer Prompt & Guard Mechanics

Verifies:
1. Forensic Read-Only Inputs: trajectory-analyzer can receive deliverable paths and compiler scripts under `inputs`.
2. Deliverable Output Immutability: trajectory-analyzer cannot list deliverables in `required_artifacts`.
3. Mutation Directive Interception: Prompts commanding learning workers to patch, recompile, or clean up deliverables are blocked.
4. Capability Routing Exemption: Historical scripts referenced in learning envelopes do not trigger capability misrouting.
5. Non-Empty Inputs Mandate: Delegating to trajectory-analyzer requires non-empty inputs in the CDE envelope.
"""

import json
import os
import sys
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ORCH_GUARD_DIR = os.path.join(ROOT_DIR, ".agents", "agents", "academic-orchestrator")
CONTRACTS_DIR = os.path.join(ROOT_DIR, ".agents", "contracts")

if ORCH_GUARD_DIR not in sys.path:
    sys.path.insert(0, ORCH_GUARD_DIR)
if CONTRACTS_DIR not in sys.path:
    sys.path.insert(0, CONTRACTS_DIR)

import guard as orch_guard
from canonical_pipelines import verify_capability_routing


class TestTrajectoryAnalyzerDelegationPrompts:

    def test_01_trajectory_analyzer_allows_deliverable_and_script_inputs(self, tmp_path):
        """When trajectory-analyzer receives deliverable and script paths under inputs, it is allowed."""
        cde = {
            "task_id": "TSK-2026-LEARN-TRJ-001",
            "stage": "Continuous Learning Cascade - Step 1: Trajectory Reconstruction",
            "worker_agent": "trajectory-analyzer",
            "objective": "Reconstruct observable tool calls and error trajectory for Table 24 mediation layout",
            "target_script": "view_file / grep_search / write_to_file",
            "inputs": [
                "03_deliverables/Chapter_4_Results.docx",
                "03_deliverables/Chapter_4_Results.md",
                "02_analysis_code/compile_gold_standard_chapter4.py"
            ],
            "required_artifacts": [
                ".agents/learning/experience/TRJ-20261003-CH4-TABLE-001.json",
                ".agents/learning/experience/TRJ-20261003-CH4-TABLE-001.md"
            ]
        }

        payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {
                            "TypeName": "trajectory-analyzer",
                            "Role": "Trajectory Analyzer",
                            "Prompt": json.dumps(cde)
                        }
                    ]
                }
            },
            "workspacePaths": [str(tmp_path)]
        }

        res = orch_guard.handle_pre_tool_use(payload)
        assert res.get("decision") == "allow", f"Expected allow for read-only forensic inputs, got: {res}"

    def test_02_trajectory_analyzer_blocks_deliverables_in_required_artifacts(self, tmp_path):
        """trajectory-analyzer cannot list deliverables in required_artifacts."""
        cde = {
            "task_id": "TSK-2026-LEARN-TRJ-002",
            "stage": "Continuous Learning Cascade - Step 1: Trajectory Reconstruction",
            "worker_agent": "trajectory-analyzer",
            "objective": "Reconstruct trajectory and output deliverable",
            "target_script": "view_file / write_to_file",
            "inputs": [".agents/state/trajectory_events.jsonl"],
            "required_artifacts": [
                "03_deliverables/Chapter_4_Results.docx"
            ]
        }

        payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {
                            "TypeName": "trajectory-analyzer",
                            "Role": "Trajectory Analyzer",
                            "Prompt": json.dumps(cde)
                        }
                    ]
                }
            },
            "workspacePaths": [str(tmp_path)]
        }

        res = orch_guard.handle_pre_tool_use(payload)
        assert res.get("decision") == "deny"
        assert "Deliverable Immutability Invariant" in res.get("reason", "")

    def test_03_trajectory_analyzer_blocks_mutation_directives(self, tmp_path):
        """Prompts commanding learning workers to patch or clean up deliverables are blocked."""
        cde_patch = {
            "task_id": "TSK-2026-LEARN-TRJ-003",
            "stage": "Continuous Learning Cascade - Step 1: Trajectory Reconstruction",
            "worker_agent": "trajectory-analyzer",
            "objective": "Please patch compile_gold_standard_chapter4.py to fix errors",
            "inputs": ["02_analysis_code/compile_gold_standard_chapter4.py"],
            "required_artifacts": [".agents/learning/experience/TRJ-001.json"]
        }

        payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {
                            "TypeName": "trajectory-analyzer",
                            "Role": "Trajectory Analyzer",
                            "Prompt": json.dumps(cde_patch)
                        }
                    ]
                }
            },
            "workspacePaths": [str(tmp_path)]
        }

        res = orch_guard.handle_pre_tool_use(payload)
        assert res.get("decision") == "deny"
        assert "mutation directives" in res.get("reason", "")

    def test_04_capability_routing_allows_learning_workers_forensic_references(self):
        """verify_capability_routing allows learning workers to reference authoring scripts in inputs/objective."""
        cde = {
            "task_id": "TSK-2026-LEARN-TRJ-004",
            "stage": "Continuous Learning Cascade - Step 1: Trajectory Reconstruction",
            "worker_agent": "trajectory-analyzer",
            "objective": "Reconstruct observable execution of compile_gold_standard_chapter4.py and Table 24",
            "target_script": "view_file / grep_search / write_to_file",
            "inputs": ["02_analysis_code/compile_gold_standard_chapter4.py"]
        }

        prompt = json.dumps(cde)
        ok, reason = verify_capability_routing("trajectory-analyzer", prompt, cde)
        assert ok is True, f"Expected capability routing allow for learning worker, got reason: {reason}"

    def test_05_delegation_to_trajectory_analyzer_requires_non_empty_inputs(self, tmp_path):
        """Delegating to trajectory-analyzer with an empty inputs list is blocked."""
        cde = {
            "task_id": "TSK-2026-LEARN-TRJ-005",
            "stage": "Continuous Learning Cascade - Step 1: Trajectory Reconstruction",
            "worker_agent": "trajectory-analyzer",
            "objective": "Reconstruct errors in chapter 4",
            "target_script": "view_file / grep_search / write_to_file",
            "inputs": [],
            "required_artifacts": [".agents/learning/experience/TRJ-001.json"]
        }

        payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {
                            "TypeName": "trajectory-analyzer",
                            "Role": "Trajectory Analyzer",
                            "Prompt": json.dumps(cde)
                        }
                    ]
                }
            },
            "workspacePaths": [str(tmp_path)]
        }

        res = orch_guard.handle_pre_tool_use(payload)
        assert res.get("decision") == "deny"
        assert "Input Anchor Required for Trajectory Analyzer" in res.get("reason", "")

    def test_06_trajectory_analysis_report_resolved_in_repo_directory(self, tmp_path, monkeypatch):
        """When trajectory files are written to the central suite repository, handle_stop resolves them successfully."""
        project_ws = tmp_path / "client_project"
        project_ws.mkdir()
        repo_ws = tmp_path / "suite_repo"
        repo_ws.mkdir()

        # Set ACADEMIC_SUITE_REPO to mock repo
        monkeypatch.setenv("ACADEMIC_SUITE_REPO", str(repo_ws))

        # Create trajectory files ONLY in the suite repo
        exp_dir = repo_ws / ".agents" / "learning" / "experience" / "TRJ-TEST-001"
        exp_dir.mkdir(parents=True)
        traj_json = exp_dir / "trajectory.json"
        traj_md = exp_dir / "trajectory_report.md"
        traj_json.write_text('{"trajectory_id": "TRJ-TEST-001", "status": "COMPLETED"}')
        traj_md.write_text("# Trajectory Analysis Report\nObserved actions reconstructed.")

        sub_conv_id = "trj-subagent-999"
        cde = {
            "task_id": "TSK-2026-LEARN-TRJ-006",
            "stage": "Continuous Learning Cascade - Step 1: Trajectory Reconstruction",
            "worker_agent": "trajectory-analyzer",
            "objective": "Reconstruct error trajectory",
            "inputs": ["03_deliverables/validation_report.json"],
            "required_artifacts": [
                ".agents/learning/experience/TRJ-TEST-001/trajectory.json",
                ".agents/learning/experience/TRJ-TEST-001/trajectory_report.md"
            ]
        }

        records = [
            {"type": "USER_INPUT", "content": "Please diagnose the failure."},
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {
                            "Subagents": [
                                {
                                    "TypeName": "trajectory-analyzer",
                                    "Role": "Trajectory Analyzer",
                                    "Prompt": json.dumps(cde)
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
            {
                "type": "SYSTEM_MESSAGE",
                "content": f"[Message] timestamp=2026-10-03T12:00:00Z sender={sub_conv_id} priority=MESSAGE_PRIORITY_HIGH content=Trajectory reconstructed."
            },
            {
                "type": "PLANNER_RESPONSE",
                "content": "Stage completed: what was done was trajectory reconstruction. What will be done next is causal diagnosis with behavior-analyst. Please confirm to proceed.",
                "tool_calls": []
            }
        ]

        t_file = project_ws / "transcript.jsonl"
        with open(t_file, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

        payload = {
            "transcriptPath": str(t_file),
            "workspacePaths": [str(project_ws)],
            "isSubagent": False
        }

        res = orch_guard.handle_stop(payload)
        # Must NOT fail with "Missing artifacts"
        assert res.get("decision") != "continue" or "Missing artifacts" not in res.get("reason", ""), \
            f"Expected trajectory files resolved in repo dir, but got: {res}"

    def test_07_trajectory_analysis_report_missing_in_both_blocks_stage(self, tmp_path, monkeypatch):
        """When trajectory files are missing in both project and repo, handle_stop blocks with missing artifacts."""
        project_ws = tmp_path / "client_project"
        project_ws.mkdir()
        repo_ws = tmp_path / "empty_suite_repo"
        repo_ws.mkdir()

        monkeypatch.setenv("ACADEMIC_SUITE_REPO", str(repo_ws))

        sub_conv_id = "trj-subagent-888"
        cde = {
            "task_id": "TSK-2026-LEARN-TRJ-007",
            "stage": "Continuous Learning Cascade - Step 1: Trajectory Reconstruction",
            "worker_agent": "trajectory-analyzer",
            "objective": "Reconstruct error trajectory",
            "inputs": ["03_deliverables/validation_report.json"],
            "required_artifacts": [
                ".agents/learning/experience/TRJ-NONEXISTENT/trajectory.json"
            ]
        }

        records = [
            {"type": "USER_INPUT", "content": "Please diagnose the failure."},
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {
                            "Subagents": [
                                {
                                    "TypeName": "trajectory-analyzer",
                                    "Role": "Trajectory Analyzer",
                                    "Prompt": json.dumps(cde)
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
            {
                "type": "SYSTEM_MESSAGE",
                "content": f"[Message] timestamp=2026-10-03T12:00:00Z sender={sub_conv_id} priority=MESSAGE_PRIORITY_HIGH content=Trajectory reconstructed."
            },
            {
                "type": "PLANNER_RESPONSE",
                "content": "Stage completed: what was done was trajectory reconstruction. What will be done next is causal diagnosis with behavior-analyst. Please confirm to proceed.",
                "tool_calls": []
            }
        ]

        t_file = project_ws / "transcript.jsonl"
        with open(t_file, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

        payload = {
            "transcriptPath": str(t_file),
            "workspacePaths": [str(project_ws)],
            "isSubagent": False
        }

        res = orch_guard.handle_stop(payload)
        assert res.get("decision") == "continue"
        assert "Missing artifacts" in res.get("reason", "")
