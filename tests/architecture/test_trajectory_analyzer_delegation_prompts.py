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

    def test_08_trajectory_analysis_report_resolved_from_state_slug_in_experience_dir(self, tmp_path, monkeypatch):
        """When required_artifacts has state/trajectory_agent_role_bleed.json, it resolves to TRJ-...-AGENT-ROLE-BLEED-... in experience/."""
        project_ws = tmp_path / "client_project"
        project_ws.mkdir()
        repo_ws = tmp_path / "suite_repo"
        repo_ws.mkdir()

        monkeypatch.setenv("ACADEMIC_SUITE_REPO", str(repo_ws))

        # Create canonical experience file with semantic slug tokens
        exp_dir = repo_ws / ".agents" / "learning" / "experience"
        exp_dir.mkdir(parents=True)
        traj_json = exp_dir / "TRJ-20261003-AGENT-ROLE-BLEED-001.json"
        traj_md = exp_dir / "TRJ-20261003-AGENT-ROLE-BLEED-001.md"
        traj_json.write_text('{"trajectory_id": "TRJ-20261003-AGENT-ROLE-BLEED-001", "status": "COMPLETED"}')
        traj_md.write_text("# Trajectory Reconstruction\nObservable actions.")

        sub_conv_id = "trj-subagent-777"
        cde = {
            "task_id": "TSK-2026-LEARN-TRJ-008",
            "stage": "Continuous Learning Cascade - Step 1: Trajectory Reconstruction",
            "worker_agent": "trajectory-analyzer",
            "objective": "Reconstruct agent role bleed trajectory",
            "inputs": ["03_deliverables/validation_report.json"],
            "required_artifacts": [
                "state/trajectory_agent_role_bleed.json",
                "state/trajectory_agent_role_bleed.md"
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
        # Must resolve by semantic slug tokens and NOT fail with Missing artifacts
        assert res.get("decision") != "continue" or "Missing artifacts" not in res.get("reason", ""), \
            f"Expected slug resolution from experience dir, got: {res}"

    def test_09_anti_polling_circuit_breaker_blocks_alternating_transcript_inspection(self, tmp_path):
        """Alternating manage_subagents and view_file on subagent transcript triggers anti-polling circuit breaker."""
        project_ws = tmp_path / "client_project"
        project_ws.mkdir()

        # Build transcript with alternating manage_subagents and view_file on subagent logs
        records = []
        for i in range(12):
            records.append({
                "type": "PLANNER_RESPONSE",
                "tool_calls": [{"name": "manage_subagents", "args": {"Action": "list"}}]
            })
            records.append({
                "type": "GENERIC",
                "content": 'You have 1 active subagent: [{"conversationId": "sub-123"}]'
            })
            records.append({
                "type": "PLANNER_RESPONSE",
                "tool_calls": [{
                    "name": "view_file",
                    "args": {"AbsolutePath": "/home/user/.gemini/antigravity/brain/sub-123/.system_generated/logs/transcript.jsonl"}
                }]
            })
            records.append({
                "type": "GENERIC",
                "content": '{"step_index": 5, "content": "working"}'
            })

        t_file = project_ws / "transcript.jsonl"
        with open(t_file, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

        # 1. Attempting to view subagent transcript directly must be denied
        payload_view = {
            "transcriptPath": str(t_file),
            "workspacePaths": [str(project_ws)],
            "toolCall": {
                "name": "view_file",
                "args": {
                    "AbsolutePath": "/home/user/.gemini/antigravity/brain/sub-123/.system_generated/logs/transcript.jsonl"
                }
            }
        }
        res_view = orch_guard.handle_pre_tool_use(payload_view)
        assert res_view.get("decision") == "deny"
        assert "Zero Active Polling & Subagent Context Isolation" in res_view.get("reason", "")

        # 2. Repeated manage_subagents in window must also be denied by rolling window count
        payload_list = {
            "transcriptPath": str(t_file),
            "workspacePaths": [str(project_ws)],
            "toolCall": {
                "name": "manage_subagents",
                "args": {"Action": "list"}
            }
        }
        res_list = orch_guard.handle_pre_tool_use(payload_list)
        assert res_list.get("decision") == "deny"
        assert "Anti-Polling Circuit Breaker" in res_list.get("reason", "")

    def test_10_remediation_phase_bypasses_historical_learning_artifacts(self, tmp_path, monkeypatch):
        """When in REMEDIATION_PHASE, historical learning envelope path differences do not block stage completion."""
        project_ws = tmp_path / "client_project"
        project_ws.mkdir()
        repo_ws = tmp_path / "suite_repo"
        repo_ws.mkdir()

        monkeypatch.setenv("ACADEMIC_SUITE_REPO", str(repo_ws))

        sub_conv_id = "trj-subagent-555"
        # Historical CDE that listed non-existent artifact path
        cde_learning = {
            "task_id": "TSK-2026-LEARN-TRJ-010",
            "stage": "Continuous Learning Cascade - Step 1: Trajectory Reconstruction",
            "worker_agent": "trajectory-analyzer",
            "objective": "Reconstruct historical trajectory",
            "inputs": ["03_deliverables/validation_report.json"],
            "required_artifacts": [
                "state/unresolvable_historical_trajectory.json"
            ]
        }

        # Deliverable CDE for academic-writer
        deliv_dir = project_ws / "03_deliverables"
        deliv_dir.mkdir()
        docx_file = deliv_dir / "05_macro_model.docx"
        md_file = deliv_dir / "05_macro_model.md"
        json_file = deliv_dir / "05_macro_model.json"
        docx_file.write_text("DOCX")
        md_file.write_text("# Macro Model\nScholarly findings.")
        json_file.write_text('{"CFI": 0.94, "RMSEA": 0.04}')

        records = [
            {"type": "USER_INPUT", "content": "Fix the macro model."},
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
                                    "Prompt": json.dumps(cde_learning)
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
                "content": f"[Message] timestamp=2026-10-03T12:00:00Z sender={sub_conv_id} priority=MESSAGE_PRIORITY_HIGH content=Candidate graduated."
            },
            {
                "type": "PLANNER_RESPONSE",
                "content": "Stage completed: what was done was Stage 4.5 remediation. What will be done next is validation with validation-agent. Please confirm to proceed.",
                "tool_calls": []
            }
        ]

        # Simulate state ledger with REMEDIATION_PHASE
        state_dir = project_ws / ".agents" / "state"
        state_dir.mkdir(parents=True)
        (state_dir / "state_ledger.json").write_text(json.dumps({
            "current_state": "REMEDIATION_PHASE",
            "active_stage": "Stage 4.5"
        }))

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
        # In REMEDIATION_PHASE, unresolvable historical learning artifact does NOT block stop
        assert res.get("decision") != "continue" or "unresolvable_historical_trajectory" not in res.get("reason", ""), \
            f"Expected REMEDIATION_PHASE to bypass historical learning artifacts, but got: {res}"

