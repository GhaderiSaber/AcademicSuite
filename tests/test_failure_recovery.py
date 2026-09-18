#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_failure_recovery.py — Comprehensive Failure Recovery & Routing Unit Tests

Validates:
1. All 7 failure types in the taxonomy (DATA, TOOL, STATISTICAL, METHODOLOGICAL, VALIDATION, PERMISSION, AGENT).
2. The exact SEM failure scenarios requested:
   - R error → Tool recovery
   - Invalid data → Data Agent
   - Model issue → Methodology/Statistics Agent
   - Inconsistent output → Validator → Writing/Statistics Agent
3. Anti-Restart Invariant: Upstream stages are strictly preserved without resetting the entire task.
4. JSON Schema validation of incident records.
5. Incident lifecycle resolution (DETECTED → ROUTED → RECOVERED).
6. Academic State Manager integration and validation.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
scripts_dir = os.path.join(ROOT_DIR, "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from recovery.taxonomy import FailureType, FailureSeverity, RecoveryStrategy, IncidentStatus
from recovery.diagnostics import diagnose_failure
from recovery.router import route_failure, calculate_preserved_stages
from recovery.recovery_engine import (
    create_incident,
    resolve_incident,
    format_incident_markdown,
    load_incident_schema
)
import academic_state_manager as asm
import jsonschema


class TestFailureRecovery(unittest.TestCase):

    def setUp(self):
        self.schema = load_incident_schema()
        self.assertIsNotNone(self.schema, "incident_schema.json must load successfully")

    def test_01_all_seven_failure_types_diagnosed(self):
        """All 7 canonical failure types must be correctly diagnosed from characteristic signatures."""
        test_cases = [
            ("data_integrity failed: missing rate > 0 and straight-lining detected", FailureType.DATA),
            ("R error: Rscript command not found, exit code 127", FailureType.TOOL),
            ("optimizer failed: maximum iterations exceeded, did not converge, singular matrix", FailureType.STATISTICAL),
            ("degrees of freedom mismatch: df error in paired design", FailureType.METHODOLOGICAL),
            ("reporting_consistency: prohibited p = .000 found, missing 3-Table Standard", FailureType.VALIDATION),
            ("Permission denied: [Errno 13] Read-only file system", FailureType.PERMISSION),
            ("Subagent timeout: FAILED_PRECONDITION User location is not supported", FailureType.AGENT),
        ]

        for err_msg, expected_type in test_cases:
            diag = diagnose_failure(err_msg)
            self.assertEqual(
                diag["failure_type"],
                expected_type.value,
                f"Failed for message: '{err_msg}'. Expected {expected_type.value}, got {diag['failure_type']}"
            )

    def test_02_sem_failure_routing_scenarios(self):
        """The 4 canonical SEM failure scenarios must route precisely without task restarts."""
        stage = "05_macro_model"

        # Scenario A: R error -> Tool recovery
        res_tool = create_incident(
            stage_id=stage,
            error_message="R error: lavaan package failed with exit code 1",
            context={"model_type": "sem"}
        )
        self.assertEqual(res_tool["failure_type"], FailureType.TOOL.value)
        self.assertEqual(res_tool["routing_plan"]["assigned_handler"], "tool_recovery_runner")
        self.assertEqual(res_tool["routing_plan"]["strategy"], RecoveryStrategy.RETRY_TOOL_FALLBACK.value)
        self.assertIn("semopy", res_tool["routing_plan"]["remediation_action"])

        # Scenario B: Invalid data -> Data Agent
        res_data = create_incident(
            stage_id=stage,
            error_message="data_integrity error: missing rate > 0 and zero variance item in SEM indicators",
            context={"model_type": "sem"}
        )
        self.assertEqual(res_data["failure_type"], FailureType.DATA.value)
        self.assertEqual(res_data["routing_plan"]["assigned_handler"], "data-agent")
        self.assertEqual(res_data["routing_plan"]["strategy"], RecoveryStrategy.DELEGATE_DATA_AGENT.value)

        # Scenario C: Model issue -> Statistics/Methodology Agent
        res_stat = create_incident(
            stage_id=stage,
            error_message="optimizer failed: maximum iterations exceeded, non-positive definite covariance matrix and negative variance",
            context={"model_type": "sem"}
        )
        self.assertEqual(res_stat["failure_type"], FailureType.STATISTICAL.value)
        self.assertEqual(res_stat["routing_plan"]["assigned_handler"], "statistics-agent")
        self.assertEqual(res_stat["routing_plan"]["strategy"], RecoveryStrategy.DELEGATE_STATISTICS_AGENT.value)
        self.assertIn("robust", res_stat["routing_plan"]["remediation_action"].lower())

        # Scenario D: Inconsistent output -> Validator -> Writing/Statistics Agent
        res_val = create_incident(
            stage_id=stage,
            error_message="reporting_consistency: SEM Macro Reporting violation: Table A is missing and prohibited p = .000 found",
            context={"model_type": "sem"}
        )
        self.assertEqual(res_val["failure_type"], FailureType.VALIDATION.value)
        self.assertEqual(res_val["routing_plan"]["assigned_handler"], "academic-writer")
        self.assertEqual(res_val["routing_plan"]["strategy"], RecoveryStrategy.DELEGATE_WRITING_AGENT.value)

    def test_03_anti_restart_invariant(self):
        """Upstream stages must be strictly preserved on disk; do NOT restart the entire task."""
        stage = "05_macro_model"
        preserved = calculate_preserved_stages(stage)

        expected_preserved = [
            "00_data_curation",
            "01_demographics",
            "02_descriptives_and_reliability",
            "03_parametric_assumptions",
            "04_bivariate_correlations"
        ]
        self.assertEqual(preserved, expected_preserved)

        # Confirm incident record preserves them
        incident = create_incident(stage_id=stage, error_message="Singular matrix in SEM")
        self.assertEqual(incident["preserved_upstream_stages"], expected_preserved)

    def test_04_schema_conformance(self):
        """All created incident records must pass schema validation against incident_schema.json."""
        incident = create_incident(
            stage_id="06_hypothesis_1",
            error_message="Prohibited p = .000 found in hypothesis narrative"
        )
        # Validate instance against schema
        jsonschema.validate(instance=incident, schema=self.schema)
        self.assertEqual(incident["status"], IncidentStatus.ROUTED.value)

    def test_05_incident_resolution_lifecycle(self):
        """An incident transitions from ROUTED to RECOVERED upon successful verification."""
        incident = create_incident(
            stage_id="07_hypothesis_2",
            error_message="lavaan package not found",
            context={"model_type": "sem"}
        )
        self.assertEqual(incident["status"], IncidentStatus.ROUTED.value)

        # Resolve
        resolved = resolve_incident(
            incident=incident,
            verification_verdict="PASS",
            resolved_by="tool_recovery_runner",
            notes="Switched to Python semopy engine; numerical consistency confirmed."
        )
        self.assertEqual(resolved["status"], IncidentStatus.RECOVERED.value)
        self.assertEqual(resolved["resolution_details"]["verification_verdict"], "PASS")

        # Format markdown
        md = format_incident_markdown(resolved)
        self.assertIn("Failure Incident Diagnosed", md)
        self.assertIn("Targeted Remediation Plan", md)
        self.assertIn("Zero Whole-Task Restart Enforced", md)

    def test_06_state_manager_incident_integration(self):
        """AcademicStateManager logs incidents in academic-state/incidents/ and validate_state passes."""
        temp_dir = tempfile.mkdtemp(prefix="academic_suite_recovery_test_")
        try:
            asm.init_state(temp_dir, title="Recovery Integration Test", methodology="sem", n=150)

            # Log an incident
            inc = asm.log_incident(temp_dir, "05_macro_model", "R error: lavaan failed with code 1")
            self.assertIn("incident_id", inc)

            # List incidents
            incidents = asm.list_incidents(temp_dir)
            self.assertEqual(len(incidents), 1)
            self.assertEqual(incidents[0]["incident_id"], inc["incident_id"])

            # Validate state (must include incidents/ in validated_files)
            val_rep = asm.validate_state(temp_dir)
            self.assertEqual(val_rep["overall_verdict"], "PASS")
            inc_validated = [f for f in val_rep["validated_files"] if f["file"].startswith("incidents/")]
            self.assertEqual(len(inc_validated), 1)
            self.assertEqual(inc_validated[0]["status"], "VALID")

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
