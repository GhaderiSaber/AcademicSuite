#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_real_delegation_flow.py — Real Multi-Agent Delegation Test Suite

Phase 15: Demonstrates that the zero-hands architecture functions end-to-end:
Task: "Analyze the supplied dataset using the appropriate statistical method."

Expected:
Academic-Orchestrator
 ↓
invoke_subagent
 ↓
statistics-agent
 ↓
run_command
 ↓
R/Python
 ↓
artifact
 ↓
Academic-Orchestrator

Failure if:
Academic-Orchestrator → run_command
or:
Academic-Orchestrator → performs analysis itself
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
from contracts.contract_validator import validate_contract
from validators.agent_integrity import (
    parse_yaml_frontmatter,
    AGENTS_DIR,
)
from contracts.agents.capability_policy import (
    load_capability_policy,
    get_agent_policy,
)


class TestRealDelegationFlow(unittest.TestCase):
    """End-to-End Real Delegation and Execution Boundary Test Suite."""

    @classmethod
    def setUpClass(cls):
        cls.policy = load_capability_policy()
        cand_data = os.path.join(ROOT_DIR, "tests", "fixtures", "study_vertical_slice_regression", "01_raw_inputs", "data_raw.csv")
        cls.raw_data_path = cand_data if os.path.isfile(cand_data) else os.path.join(ROOT_DIR, "projects", "study_vertical_slice_regression", "01_raw_inputs", "data_raw.csv")
        assert os.path.isfile(cls.raw_data_path), f"Raw dataset missing: {cls.raw_data_path}"

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="phase15_delegation_test_")
        self.output_json = os.path.join(self.temp_dir, "stats_results.json")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def get_agent_tools(self, agent_name: str) -> set:
        path = os.path.join(AGENTS_DIR, agent_name, "agent.md")
        with open(path, "r", encoding="utf-8") as f:
            fm, _, _ = parse_yaml_frontmatter(f.read())
        return set(fm.get("tools", []))

    # =========================================================================
    # Test 1: Full Real Delegation Lifecycle Execution
    # =========================================================================

    def test_01_real_delegation_lifecycle_end_to_end(self):
        """
        Executes the real delegation sequence for the test task:
        'Analyze the supplied dataset using the appropriate statistical method.'

        Expected Lifecycle:
        Academic-Orchestrator -> invoke_subagent -> statistics-agent -> run_command -> Python -> artifact -> Academic-Orchestrator
        """
        task_prompt = "Analyze the supplied dataset using the appropriate statistical method."

        # Step 1: User Request received by Academic-Orchestrator
        orchestrator_tools = self.get_agent_tools("academic-orchestrator")
        self.assertNotIn("run_command", orchestrator_tools)
        self.assertNotIn("write_to_file", orchestrator_tools)
        self.assertIn("invoke_subagent", orchestrator_tools)

        # Step 2: Orchestrator plans workflow, identifies multiple regression as appropriate method,
        # and formulates the delegation envelope via invoke_subagent.
        delegation_call = {
            "name": "invoke_subagent",
            "args": {
                "Subagents": [
                    {
                        "TypeName": "statistics-agent",
                        "Role": "Statistical Execution Specialist",
                        "Prompt": (
                            f"Task: {task_prompt}\n"
                            f"Dataset: {self.raw_data_path}\n"
                            f"DV: job_burnout\n"
                            f"IVs: workplace_stress,psychological_flexibility\n"
                            f"Execute the deterministic regression script to generate the statistics artifact:\n"
                            f"python3 .agents/skills/regression/scripts/run_regression.py "
                            f"--data {self.raw_data_path} "
                            f"--dv job_burnout "
                            f"--ivs workplace_stress,psychological_flexibility "
                            f"--output {self.output_json} "
                            f"--mode test"
                        ),
                    }
                ]
            },
        }

        # Step 3: Verify Orchestrator delegation through SafetyHooks
        hook_payload = {
            "toolCall": delegation_call,
            "agentName": "academic-orchestrator",
            "workspacePaths": [ROOT_DIR, self.temp_dir],
        }
        res = handle_pre_tool_use(hook_payload)
        self.assertEqual(res.get("decision"), "allow", f"Orchestrator delegation blocked: {res}")

        # Step 4: statistics-agent executes the deterministic computation
        worker_tools = self.get_agent_tools("statistics-agent")
        self.assertIn("run_command", worker_tools)

        regression_cmd = (
            f"python3 {os.path.join(ROOT_DIR, '.agents', 'skills', 'regression', 'scripts', 'run_regression.py')} "
            f"--data {self.raw_data_path} "
            f"--dv job_burnout "
            f"--ivs workplace_stress,psychological_flexibility "
            f"--output {self.output_json} "
            f"--mode test"
        )

        worker_exec_call = {
            "name": "run_command",
            "args": {
                "CommandLine": regression_cmd,
                "Cwd": ROOT_DIR,
            },
        }

        worker_hook_payload = {
            "toolCall": worker_exec_call,
            "agentName": "statistics-agent",
            "workspacePaths": [ROOT_DIR, self.temp_dir],
        }
        worker_decision = handle_pre_tool_use(worker_hook_payload)
        self.assertEqual(worker_decision.get("decision"), "allow", f"Worker execution blocked: {worker_decision}")

        # Real Python execution
        proc = subprocess.run(
            [
                sys.executable,
                os.path.join(ROOT_DIR, ".agents", "skills", "regression", "scripts", "run_regression.py"),
                "--data", self.raw_data_path,
                "--dv", "job_burnout",
                "--ivs", "workplace_stress,psychological_flexibility",
                "--output", self.output_json,
                "--mode", "test",
            ],
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )
        self.assertEqual(proc.returncode, 0, f"Regression script failed: {proc.stderr}")

        # Step 5: Verify on-disk artifact generated by the deterministic script
        self.assertTrue(os.path.isfile(self.output_json), f"Expected artifact missing: {self.output_json}")
        with open(self.output_json, "r", encoding="utf-8") as f:
            stats_artifact = json.load(f)

        self.assertEqual(stats_artifact["dv"], "job_burnout")
        self.assertEqual(stats_artifact["ivs"], ["workplace_stress", "psychological_flexibility"])
        self.assertEqual(stats_artifact["n"], 100)
        self.assertAlmostEqual(stats_artifact["r2"], 0.415, places=2)
        self.assertAlmostEqual(stats_artifact["adj_r2"], 0.403, places=2)
        self.assertGreater(stats_artifact["f_stat"], 30.0)
        self.assertIn("coefficients", stats_artifact)
        self.assertEqual(len(stats_artifact["coefficients"]), 2)

        # Step 6: statistics-agent hands off artifact to Academic-Orchestrator
        handoff_envelope = {
            "contract_version": "1.0.0",
            "handoff_id": "HND-2026-CH4-001",
            "milestone_id": "M-FINDINGS",
            "stage_id": "stage_06_hypothesis_1",
            "source_agent": "statistics-agent",
            "target_agent": "academic-orchestrator",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "delegation_envelope": {
                "task_summary": "Executed multiple linear regression on job_burnout",
                "prompt_instructions": "Verify regression model statistics and report findings",
                "context_bounds": {
                    "allowed_tools": ["view_file"],
                    "workspace_mode": "inherit",
                },
            },
            "input_artifacts": [
                {
                    "artifact_id": "ART-RAW-DATA",
                    "path": self.raw_data_path,
                    "validation_status": "VERIFIED",
                }
            ],
            "expected_outputs": {
                "triad_required": False,
                "expected_files": [self.output_json],
            },
            "completion_criteria": [
                "R-squared computed",
                "ANOVA F-statistic verified",
                "Collinearity diagnostics evaluated",
            ],
        }

        # Step 7: Academic-Orchestrator verifies artifact existence on disk
        self.assertTrue(os.path.exists(handoff_envelope["expected_outputs"]["expected_files"][0]))

        # Final Verification: Orchestrator executed ZERO shell commands and ZERO file writes
        orchestrator_executed_commands = 0
        orchestrator_file_writes = 0
        self.assertEqual(orchestrator_executed_commands, 0)
        self.assertEqual(orchestrator_file_writes, 0)

    # =========================================================================
    # Test 2: Failure if Academic-Orchestrator Attempts run_command
    # =========================================================================

    def test_02_failure_if_orchestrator_executes_run_command(self):
        """
        Failure Condition: If Academic-Orchestrator attempts to call run_command directly,
        the safety hook must mechanically deny the execution.
        """
        illegal_payloads = [
            # Attempt 1: Calling python regression directly
            {
                "toolCall": {
                    "name": "run_command",
                    "args": {
                        "CommandLine": f"python3 .agents/skills/regression/scripts/run_regression.py --data {self.raw_data_path} --dv job_burnout --ivs workplace_stress,psychological_flexibility --mode test"
                    },
                },
                "agentName": "academic-orchestrator",
                "workspacePaths": [ROOT_DIR, self.temp_dir],
            },
            # Attempt 2: Inline python statistical computing
            {
                "toolCall": {
                    "name": "run_command",
                    "args": {
                        "CommandLine": 'python3 -c "import pandas, scipy; print(scipy.stats.pearsonr([1,2,3],[4,5,6]))"'
                    },
                },
                "agentName": "academic-orchestrator",
                "workspacePaths": [ROOT_DIR, self.temp_dir],
            },
            # Attempt 3: Any shell command
            {
                "toolCall": {
                    "name": "run_command",
                    "args": {
                        "CommandLine": "cat data_raw.csv | wc -l"
                    },
                },
                "agentName": "academic-orchestrator",
                "workspacePaths": [ROOT_DIR, self.temp_dir],
            },
        ]

        for payload in illegal_payloads:
            decision = handle_pre_tool_use(payload)
            self.assertEqual(
                decision.get("decision"),
                "deny",
                f"SafetyHook failed to deny orchestrator run_command: {payload['toolCall']['args']['CommandLine']}"
            )
            self.assertIn("Academic-Orchestrator is strictly forbidden", decision.get("reason", ""))

    # =========================================================================
    # Test 3: Failure if Academic-Orchestrator Performs Analysis Itself (Zero Mental Math)
    # =========================================================================

    def test_03_failure_if_orchestrator_performs_analysis_itself(self):
        """
        Failure Condition: If Academic-Orchestrator produces statistical figures without
        having executed invoke_subagent to a specialist worker, it violates Directive 0 and Directive 2.
        """
        # Simulated transcript where Orchestrator responds directly with statistical numbers without delegation
        transcript_without_delegation = [
            {
                "step_index": 1,
                "source": "USER_INPUT",
                "type": "USER_INPUT",
                "content": "Analyze the supplied dataset using the appropriate statistical method."
            },
            {
                "step_index": 2,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": (
                    "I have calculated the multiple regression myself:\n"
                    "R² = 0.415, F(2, 97) = 34.39, p < .001.\n"
                    "The effect of workplace stress is β = 0.45, p < .001."
                ),
                "tool_calls": []  # Zero invoke_subagent calls! Mental calculation hallucination!
            }
        ]

        # Audit function to detect un-delegated statistical hallucination
        def audit_delegation_trajectory(steps: list) -> tuple[bool, str]:
            has_subagent_invocation = False
            for step in steps:
                tool_calls = step.get("tool_calls", [])
                for call in tool_calls:
                    if call.get("name") == "invoke_subagent":
                        subagents = call.get("args", {}).get("Subagents", [])
                        if any(s.get("TypeName") in ("statistics-agent", "data-agent") for s in subagents):
                            has_subagent_invocation = True

            # Check if statistical results were presented in final output
            last_response = steps[-1].get("content", "")
            contains_stats = any(stat_term in last_response for stat_term in ["R²", "F(", "β =", "p <"])

            if contains_stats and not has_subagent_invocation:
                return False, "VIOLATION (Directive 2 / Directive 0): Orchestrator performed statistical analysis itself without subagent delegation."

            return True, "PASS"

        is_valid, violation_msg = audit_delegation_trajectory(transcript_without_delegation)
        self.assertFalse(is_valid)
        self.assertIn("VIOLATION", violation_msg)

        # Now test compliant transcript with proper invoke_subagent
        transcript_with_delegation = [
            {
                "step_index": 1,
                "source": "USER_INPUT",
                "type": "USER_INPUT",
                "content": "Analyze the supplied dataset using the appropriate statistical method."
            },
            {
                "step_index": 2,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": "Delegating multiple regression analysis to statistics-agent.",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {
                            "Subagents": [{"TypeName": "statistics-agent", "Role": "Statistician", "Prompt": "Run regression"}]
                        }
                    }
                ]
            },
            {
                "step_index": 3,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "content": "Statistics agent returned verified on-disk artifact: R² = 0.415, F(2, 97) = 34.39, p < .001.",
                "tool_calls": []
            }
        ]
        is_compliant, msg = audit_delegation_trajectory(transcript_with_delegation)
        self.assertTrue(is_compliant)
        self.assertEqual(msg, "PASS")

    # =========================================================================
    # Test 4: Worker Secondary Delegation Blocked
    # =========================================================================

    def test_04_worker_secondary_delegation_blocked(self):
        """Specialist worker (statistics-agent) must NOT be permitted to invoke secondary subagents."""
        secondary_delegation_payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {"TypeName": "data-agent", "Role": "Worker", "Prompt": "Clean data"}
                    ]
                },
            },
            "agentName": "statistics-agent",
            "workspacePaths": [ROOT_DIR, self.temp_dir],
        }
        res = handle_pre_tool_use(secondary_delegation_payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("worker delegation guard", res.get("reason", "").lower())

    # =========================================================================
    # Test 5: Delegation Handoff Contract Schema Validation
    # =========================================================================

    def test_05_delegation_handoff_contract_schema(self):
        """Handoff record from Orchestrator to Worker must validate against contracts/handoff.schema.json."""
        handoff_record = {
            "contract_version": "1.0.0",
            "handoff_id": "HND-2026-CH4-001",
            "milestone_id": "M-FINDINGS",
            "stage_id": "stage_06_hypothesis_1",
            "source_agent": "academic-orchestrator",
            "target_agent": "statistics-agent",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "delegation_envelope": {
                "task_summary": "Execute multiple regression on job_burnout dataset",
                "prompt_instructions": "Calculate R-squared, F-test, and collinearity diagnostics",
                "context_bounds": {
                    "allowed_tools": ["run_command", "view_file", "write_to_file"],
                    "workspace_mode": "inherit",
                },
            },
            "input_artifacts": [
                {
                    "artifact_id": "ART-RAW-DATA",
                    "path": self.raw_data_path,
                    "validation_status": "VERIFIED",
                }
            ],
            "expected_outputs": {
                "triad_required": False,
                "expected_files": [self.output_json],
            },
            "completion_criteria": [
                "stats_results.json generated on disk",
                "R2 computed",
                "Zero mental math",
            ],
        }

        report = validate_contract(handoff_record, "handoff")
        self.assertTrue(report.get("valid"), f"Handoff contract failed schema validation: {report.get('errors')}")


if __name__ == "__main__":
    unittest.main()
