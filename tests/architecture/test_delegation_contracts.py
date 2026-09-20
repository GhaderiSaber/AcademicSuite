#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_delegation_contracts.py — Architecture Verification for Phase 22

Verifies Phase 22 Mandates:
1. Every delegated task must have a structured contract with 10 mandatory task fields:
   task_id, parent_agent, worker_agent, objective, inputs, required_artifacts,
   acceptance_criteria, constraints, verification_method, deadline.
2. Every worker return must have 6 structured fields:
   status, artifacts, evidence, validation, warnings, limitations.
3. Strict prohibition of informal anti-patterns:
   - Academic-Orchestrator: "Analyze this." -> BLOCKED
   - Worker: "Done." -> BLOCKED
   - Academic-Orchestrator: "Great." -> BLOCKED (without validator sign-off)
4. Formal execution chain:
   Academic-Orchestrator -> formal task contract -> worker -> formal evidence -> validator -> Academic-Orchestrator
5. Validation against formal JSON schemas:
   - contracts/delegation_contract.schema.json
   - contracts/worker_return_payload.schema.json
6. CLI and programmatic engine verification.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.delegation_contract_engine import (
    create_delegation_contract,
    validate_delegation_contract,
    create_worker_return,
    validate_worker_return,
    format_delegation_prompt,
    detect_informal_delegation,
    detect_informal_worker_return,
    detect_informal_closure,
    execute_contract_verification,
    InvalidTaskContractError,
    InvalidWorkerReturnContractError,
    InformalDelegationError,
    InformalWorkerReturnError,
    InformalClosureError,
    MANDATORY_TASK_FIELDS,
    MANDATORY_RETURN_FIELDS
)

hooks_dir = os.path.join(ROOT_DIR, ".agents", "hooks")
if hooks_dir not in sys.path:
    sys.path.insert(0, hooks_dir)

from safety_hooks import SafetyHooks


class TestDelegationContracts(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="phase22_test_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # 1. Full Formal Chain: Orchestrator -> task -> worker -> validator -> Orch
    # -------------------------------------------------------------------------
    def test_01_full_formal_delegation_chain_happy_path(self):
        """Tests the complete verified flow: Orchestrator -> contract -> worker -> validator -> Orchestrator."""
        # 1. Orchestrator creates formal 10-field contract
        contract = create_delegation_contract(
            task_id="TSK-2026-CH4-001",
            parent_agent="academic-orchestrator",
            worker_agent="statistics-agent",
            objective="Calculate univariate sample descriptive statistics and demographic frequency distributions for Chapter 4.",
            inputs=["data/cleaned_data.xlsx", "requirements.json"],
            required_artifacts=[
                "outputs/01_demographics.docx",
                "outputs/01_demographics.md",
                "outputs/01_demographics.json"
            ],
            acceptance_criteria=[
                "Report N, Mean, SD, Skewness, Kurtosis with 2 decimal places",
                "APA 7 3-line table with Persian leading zero format (۰.۰۰۱)",
                "Zero missing values across analysis columns"
            ],
            constraints=[
                "Never calculate statistics in LLM memory. Run deterministic scripts via run_command.",
                "Strictly use English ASCII filenames (Directive 6).",
                "Enforce B Nazanin 13pt body font and Times New Roman for Latin statistics."
            ],
            verification_method="statistical-auditor",
            deadline="2026-09-20T18:00:00Z"
        )
        self.assertEqual(contract["task_id"], "TSK-2026-CH4-001")
        self.assertEqual(contract["worker_agent"], "statistics-agent")

        # 2. Format delegation prompt
        prompt = format_delegation_prompt(contract)
        self.assertIn("Contractual Delegation Envelope (Phase 22 Contract)", prompt)
        self.assertIn("TSK-2026-CH4-001", prompt)
        self.assertIn("01_demographics.docx", prompt)
        self.assertIn("statistical-auditor", prompt)

        # 3. Worker completes execution and produces formal 6-field WorkerReturn
        worker_return = create_worker_return(
            status="SUCCESS",
            artifacts=[
                "outputs/01_demographics.docx",
                "outputs/01_demographics.md",
                "outputs/01_demographics.json"
            ],
            evidence={
                "n_total": 300,
                "female_pct": 58.3,
                "mean_age": 34.25,
                "sd_age": 6.82,
                "skew_age": 0.31,
                "kurt_age": -0.15
            },
            validation={
                "verdict": "PASS",
                "overall_verdict": "PASS",
                "checks_passed": 10,
                "checks_failed": 0
            },
            warnings=["Age skewness is slightly positive (0.31) but well within [-2, +2] normality bounds."],
            limitations=["Cross-sectional demographic data restricts causal conclusions regarding age trends."],
            task_id="TSK-2026-CH4-001",
            worker_agent="statistics-agent"
        )
        self.assertEqual(worker_return["status"], "SUCCESS")

        # 4. Validator issues independent verification report
        validator_report = {
            "verdict": "PASS",
            "overall_verdict": "PASS",
            "auditor": "statistical-auditor",
            "report_path": "validation/01_demographics_audit.json",
            "checks_passed": 12,
            "checks_failed": 0
        }

        # 5. Contract verification
        res = execute_contract_verification(contract, worker_return, validator_report)
        self.assertTrue(res["verified"])
        self.assertEqual(res["verdict"], "APPROVED")
        self.assertEqual(res["task_id"], "TSK-2026-CH4-001")

    # -------------------------------------------------------------------------
    # 2. Anti-Pattern 1: Orchestrator -> 'Analyze this.'
    # -------------------------------------------------------------------------
    def test_02_rejection_of_informal_delegation_analyze_this(self):
        """Orchestrator attempting informal delegation 'Analyze this.' is strictly blocked."""
        informal_prompts = [
            "Analyze this.",
            "Analyze this",
            "Do this.",
            "Calculate this.",
            "Please analyze this data",
            "Handle this right away."
        ]
        for p in informal_prompts:
            is_inf, reason = detect_informal_delegation(p)
            self.assertTrue(is_inf, f"Failed to detect informal prompt: '{p}'")
            self.assertIn("INFORMAL DELEGATION BLOCKED", reason)

            # Check SafetyHook interception
            hook_res = SafetyHooks.handle_pre_tool_use({
                "agentName": "academic-orchestrator",
                "toolCall": {
                    "name": "invoke_subagent",
                    "args": {"Subagents": [{"TypeName": "statistics-agent", "Prompt": p}]}
                },
                "workspacePaths": [self.temp_dir]
            })
            self.assertEqual(hook_res["decision"], "deny")
            self.assertIn("Phase 22 - Delegation Contract Invariant", hook_res["reason"])

    # -------------------------------------------------------------------------
    # 3. Anti-Pattern 2: Worker -> 'Done.'
    # -------------------------------------------------------------------------
    def test_03_rejection_of_informal_worker_return_done(self):
        """Worker returning simply 'Done.' or 'Completed.' is strictly rejected."""
        informal_returns = [
            "Done.",
            "done",
            "Completed.",
            "finished",
            "All done.",
            "ok",
            "All set."
        ]
        for ret in informal_returns:
            is_inf, reason = detect_informal_worker_return(ret)
            self.assertTrue(is_inf, f"Failed to detect informal return: '{ret}'")
            self.assertIn("INFORMAL WORKER RETURN BLOCKED", reason)

            # Check SafetyHook interception on send_message
            hook_res = SafetyHooks.handle_pre_tool_use({
                "agentName": "statistics-agent",
                "toolCall": {
                    "name": "send_message",
                    "args": {"Recipient": "academic-orchestrator", "Message": ret}
                },
                "workspacePaths": [self.temp_dir]
            })
            self.assertEqual(hook_res["decision"], "deny")
            self.assertIn("Worker Return Invariant", hook_res["reason"])

    # -------------------------------------------------------------------------
    # 4. Anti-Pattern 3: Orchestrator -> 'Great.'
    # -------------------------------------------------------------------------
    def test_04_rejection_of_informal_orchestrator_closure_great(self):
        """Orchestrator attempting informal closure 'Great.' is strictly blocked."""
        informal_closures = [
            "Great.",
            "great",
            "Looks good.",
            "perfect",
            "Awesome.",
            "Good job.",
            "approved",
            "Thanks!"
        ]
        for closure in informal_closures:
            is_inf, reason = detect_informal_closure(closure)
            self.assertTrue(is_inf, f"Failed to detect informal closure: '{closure}'")
            self.assertIn("INFORMAL ORCHESTRATOR CLOSURE BLOCKED", reason)

            # Check SafetyHook interception on send_message
            hook_res = SafetyHooks.handle_pre_tool_use({
                "agentName": "academic-orchestrator",
                "toolCall": {
                    "name": "send_message",
                    "args": {"Recipient": "statistics-agent", "Message": closure}
                },
                "workspacePaths": [self.temp_dir]
            })
            self.assertEqual(hook_res["decision"], "deny")
            self.assertIn("Formal Delegation Contract Invariant", hook_res["reason"])

    # -------------------------------------------------------------------------
    # 5. Contract 10 Mandatory Fields Enforcement
    # -------------------------------------------------------------------------
    def test_05_contract_missing_mandatory_task_fields(self):
        """Test that missing any of the 10 mandatory task fields raises an error."""
        base_contract = {
            "contract_version": "1.0.0",
            "task_id": "TSK-001",
            "parent_agent": "academic-orchestrator",
            "worker_agent": "statistics-agent",
            "objective": "Calculate sample statistics and verify normality assumptions.",
            "inputs": ["data.xlsx"],
            "required_artifacts": ["outputs/results.json"],
            "acceptance_criteria": ["Report M, SD"],
            "constraints": ["Zero mental calculation"],
            "verification_method": "statistical-auditor",
            "deadline": "2026-09-20T18:00:00Z"
        }

        for field in MANDATORY_TASK_FIELDS:
            corrupt = dict(base_contract)
            del corrupt[field]
            res = validate_delegation_contract(corrupt, fail_closed=False)
            self.assertFalse(res["valid"], f"Expected invalid when missing '{field}'")
            self.assertTrue(any(field in err for err in res["errors"]))

            with self.assertRaises(InvalidTaskContractError):
                validate_delegation_contract(corrupt, fail_closed=True)

    # -------------------------------------------------------------------------
    # 6. Worker Return 6 Mandatory Fields Enforcement
    # -------------------------------------------------------------------------
    def test_06_worker_return_missing_mandatory_return_fields(self):
        """Test that missing any of the 6 mandatory worker return fields raises an error."""
        base_return = {
            "status": "SUCCESS",
            "artifacts": ["outputs/results.json"],
            "evidence": {"M": 24.3, "SD": 4.1},
            "validation": {"verdict": "PASS"},
            "warnings": [],
            "limitations": []
        }

        for field in MANDATORY_RETURN_FIELDS:
            corrupt = dict(base_return)
            del corrupt[field]
            res = validate_worker_return(corrupt, fail_closed=False)
            self.assertFalse(res["valid"], f"Expected invalid when missing '{field}'")
            self.assertTrue(any(field in err for err in res["errors"]))

            with self.assertRaises(InvalidWorkerReturnContractError):
                validate_worker_return(corrupt, fail_closed=True)

    # -------------------------------------------------------------------------
    # 7. Schema Validation against delegation_contract.schema.json
    # -------------------------------------------------------------------------
    def test_07_schema_validation_against_delegation_contract_schema(self):
        """Tests that compliant delegation contract satisfies contracts/delegation_contract.schema.json."""
        contract = create_delegation_contract(
            task_id="TSK-2026-CFA-002",
            parent_agent="academic-orchestrator",
            worker_agent="statistics-agent",
            objective="Perform Confirmatory Factor Analysis (CFA) to evaluate measurement model fit.",
            inputs=["data/scored_scales.xlsx"],
            required_artifacts=["outputs/cfa_model.json", "outputs/cfa_report.docx"],
            acceptance_criteria=["CFI >= 0.90", "RMSEA <= 0.08", "All standardized factor loadings >= 0.40"],
            constraints=["Execute semopy via deterministic script", "Directive 6 ASCII filenames"],
            verification_method="statistical-auditor",
            deadline="2026-09-20T20:00:00Z"
        )
        res = validate_delegation_contract(contract, fail_closed=True)
        self.assertTrue(res["valid"])
        self.assertEqual(res["errors"], [])

    # -------------------------------------------------------------------------
    # 8. Schema Validation against worker_return_payload.schema.json
    # -------------------------------------------------------------------------
    def test_08_schema_validation_against_worker_return_schema(self):
        """Tests that Phase 22 worker return satisfies worker_return_payload.schema.json."""
        ret = create_worker_return(
            status="SUCCESS",
            artifacts=["outputs/cfa_model.json", "outputs/cfa_report.docx"],
            evidence={"CFI": 0.942, "TLI": 0.931, "RMSEA": 0.048, "SRMR": 0.042},
            validation={"verdict": "PASS", "overall_verdict": "PASS", "checks_passed": 8, "checks_failed": 0},
            warnings=[],
            limitations=["Sample size N=300 is adequate but multi-group invariance was not tested."]
        )
        res = validate_worker_return(ret, fail_closed=True)
        self.assertTrue(res["valid"])
        self.assertEqual(res["errors"], [])

    # -------------------------------------------------------------------------
    # 9. CLI Interface for delegation_contract_engine.py
    # -------------------------------------------------------------------------
    def test_09_cli_interface_delegation_contract_engine(self):
        """Tests CLI commands: validate-contract, validate-return, format-prompt, verify."""
        contract_file = os.path.join(self.temp_dir, "test_contract.json")
        return_file = os.path.join(self.temp_dir, "test_return.json")
        validator_file = os.path.join(self.temp_dir, "test_validator.json")

        contract = {
            "contract_version": "1.0.0",
            "task_id": "TSK-CLI-001",
            "parent_agent": "academic-orchestrator",
            "worker_agent": "statistics-agent",
            "objective": "Execute repeated-measures ANOVA on trial outcomes.",
            "inputs": ["data.xlsx"],
            "required_artifacts": ["outputs/rm_anova.docx", "outputs/rm_anova.json"],
            "acceptance_criteria": ["Report F, df, p, partial eta squared"],
            "constraints": ["Zero mental calculation", "Directive 6"],
            "verification_method": "statistical-auditor",
            "deadline": "2026-09-20T22:00:00Z"
        }
        with open(contract_file, "w", encoding="utf-8") as f:
            json.dump(contract, f)

        ret = {
            "status": "SUCCESS",
            "artifacts": ["outputs/rm_anova.docx", "outputs/rm_anova.json"],
            "evidence": {"F": 14.82, "df": [2, 58], "p": 0.0001, "partial_eta_sq": 0.338},
            "validation": {"verdict": "PASS"},
            "warnings": [],
            "limitations": ["Sphericity assumption violated; Greenhouse-Geisser epsilon applied."]
        }
        with open(return_file, "w", encoding="utf-8") as f:
            json.dump(ret, f)

        val_report = {"verdict": "PASS"}
        with open(validator_file, "w", encoding="utf-8") as f:
            json.dump(val_report, f)

        cand = os.path.join(ROOT_DIR, ".agents", "scripts", "delegation_contract_engine.py")
        engine_script = cand if os.path.isfile(cand) else os.path.join(ROOT_DIR, "scripts", "delegation_contract_engine.py")

        # 1. validate-contract CLI
        proc1 = subprocess.run([
            sys.executable,
            engine_script,
            "validate-contract",
            contract_file
        ], capture_output=True, text=True)
        self.assertEqual(proc1.returncode, 0)
        self.assertIn('"valid": true', proc1.stdout)

        # 2. validate-return CLI
        proc2 = subprocess.run([
            sys.executable,
            engine_script,
            "validate-return",
            return_file
        ], capture_output=True, text=True)
        self.assertEqual(proc2.returncode, 0)
        self.assertIn('"valid": true', proc2.stdout)

        # 3. format-prompt CLI
        proc3 = subprocess.run([
            sys.executable,
            engine_script,
            "format-prompt",
            contract_file
        ], capture_output=True, text=True)
        self.assertEqual(proc3.returncode, 0)
        self.assertIn("Contractual Delegation Envelope", proc3.stdout)

        # 4. verify CLI
        proc4 = subprocess.run([
            sys.executable,
            engine_script,
            "verify",
            "--contract", contract_file,
            "--return", return_file,
            "--validator", validator_file
        ], capture_output=True, text=True)
        self.assertEqual(proc4.returncode, 0)
        self.assertIn('"verified": true', proc4.stdout)
        self.assertIn('"verdict": "APPROVED"', proc4.stdout)

    # -------------------------------------------------------------------------
    # 10. Orchestrator Dependency Resolver Integration
    # -------------------------------------------------------------------------
    def test_10_orchestrator_dependency_resolver_generates_formal_contract(self):
        """format_delegation_envelope produces a formal 10-field contract and prompt."""
        from scripts.orchestrator_dependency_resolver import format_delegation_envelope
        cand_state = os.path.join(ROOT_DIR, "tests", "fixtures", "study_act_burnout", "academic-state")
        study_state = cand_state if os.path.isdir(cand_state) else os.path.join(ROOT_DIR, "projects", "study_act_burnout", "academic-state")
        env = format_delegation_envelope(
            "01_demographics",
            study_state,
            "Compute univariate demographic parameters."
        )
        self.assertEqual(env["status"], "READY")
        self.assertIn("contract", env)
        contract = env["contract"]
        # Verify all 10 fields are present and valid
        for field in MANDATORY_TASK_FIELDS:
            self.assertIn(field, contract)
        self.assertEqual(contract["parent_agent"], "academic-orchestrator")
        self.assertEqual(contract["worker_agent"], "statistics-agent")
        self.assertIn("Contractual Delegation Envelope (Phase 22 Contract)", env["subagent_invocation"]["Prompt"])

    # -------------------------------------------------------------------------
    # 11. Verification Fails When Required Artifact is Missing
    # -------------------------------------------------------------------------
    def test_11_verification_fails_when_required_artifact_missing(self):
        """Verification fails when a required artifact was not produced by the worker."""
        contract = {
            "contract_version": "1.0.0",
            "task_id": "TSK-002",
            "parent_agent": "academic-orchestrator",
            "worker_agent": "statistics-agent",
            "objective": "Calculate regression model and generate docx/json outputs.",
            "inputs": ["data.xlsx"],
            "required_artifacts": ["outputs/regression.docx", "outputs/regression.json"],
            "acceptance_criteria": ["R2 > 0.15"],
            "constraints": ["Deterministic calculation"],
            "verification_method": "statistical-auditor",
            "deadline": "2026-09-20T18:00:00Z"
        }
        # Worker return missing regression.docx
        worker_return = {
            "status": "SUCCESS",
            "artifacts": ["outputs/regression.json"],
            "evidence": {"R2": 0.28, "F": 11.4, "p": 0.001},
            "validation": {"verdict": "PASS"},
            "warnings": [],
            "limitations": []
        }
        res = execute_contract_verification(contract, worker_return)
        self.assertFalse(res["verified"])
        self.assertEqual(res["verdict"], "REJECTED")
        self.assertTrue(any("regression.docx" in err for err in res["errors"]))

    # -------------------------------------------------------------------------
    # 12. Verification Fails When Validator Issues FAIL Verdict
    # -------------------------------------------------------------------------
    def test_12_verification_fails_when_validator_verdict_fails(self):
        """Verification rejects task when validator report has FAIL verdict."""
        contract = {
            "contract_version": "1.0.0",
            "task_id": "TSK-003",
            "parent_agent": "academic-orchestrator",
            "worker_agent": "statistics-agent",
            "objective": "Calculate mediation model with 5,000 bootstrap resamples.",
            "inputs": ["data.xlsx"],
            "required_artifacts": ["outputs/mediation.json"],
            "acceptance_criteria": ["Report indirect effect and 95% BCa CI"],
            "constraints": ["Bootstrap 5000"],
            "verification_method": "statistical-auditor",
            "deadline": "2026-09-20T18:00:00Z"
        }
        worker_return = {
            "status": "SUCCESS",
            "artifacts": ["outputs/mediation.json"],
            "evidence": {"indirect_effect": 0.14, "bca_ci": [-0.02, 0.31]},
            "validation": {"verdict": "FAIL"},
            "warnings": ["Bootstrap confidence interval crosses zero."],
            "limitations": []
        }
        res = execute_contract_verification(contract, worker_return)
        self.assertFalse(res["verified"])
        self.assertEqual(res["verdict"], "REJECTED")
        self.assertTrue(any("Validator report verdict is not PASS" in err for err in res["errors"]))


if __name__ == "__main__":
    unittest.main()
