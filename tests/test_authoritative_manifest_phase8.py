#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_authoritative_manifest_phase8.py — Comprehensive Unit Tests for Phase 8 Authoritative Stage Manifests

Verifies:
1. Generation and verification of authoritative stage manifest with Triad deliverables (.docx, .md, .json)
2. Missing manifest.json fails closed with MissingStageManifestError
3. Missing declared artifact fails closed with ManifestArtifactMissingError
4. Tampered artifact hash fails closed with ManifestHashMismatchError
5. Tampered input hash fails closed with ManifestInputMismatchError
6. Contradiction between JSON and Markdown/DOCX fails closed with ManifestCrossAgreementError
7. Upstream dependency manifest hash tampering fails closed with ManifestDependencyMismatchError
8. Triad Invariant enforcement for hypothesis micro-stages (ManifestTriadMissingError)
9. StrictStateMachine integration: transition gating and atomic manifest status update upon STAGE_APPROVED
10. CLI execution of scripts/stage_manifest_engine.py (build & verify)
"""

import os
import sys
import json
import shutil
import tempfile
import subprocess
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.stage_manifest_engine import (
    build_stage_manifest,
    verify_stage_manifest,
    compute_sha256,
    StageManifestError,
    MissingStageManifestError,
    MalformedStageManifestError,
    ManifestInputMismatchError,
    ManifestArtifactMissingError,
    ManifestTriadMissingError,
    ManifestHashMismatchError,
    ManifestDependencyMismatchError,
    ManifestCrossAgreementError,
)

from scripts.academic_state_manager import (
    StrictStateMachine,
    StageState,
    StateManagementError,
)


class TestAuthoritativeManifestPhase8(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="phase8_manifest_test_")
        self.state_dir = os.path.join(self.temp_dir, "academic-state")
        self.sm = StrictStateMachine(state_dir=self.state_dir, project_id="phase8_study")

        # Set up a sample stage deliverables directory
        self.stage_dir = os.path.join(self.temp_dir, "stage_06_hypothesis_1")
        os.makedirs(self.stage_dir, exist_ok=True)

        # Create input file
        self.input_file = os.path.join(self.temp_dir, "input_dataset.csv")
        with open(self.input_file, "w", encoding="utf-8") as f:
            f.write("id,group,score\n1,ACT,25.5\n2,Control,18.2\n")

        # Create Triad deliverables
        self.json_file = os.path.join(self.stage_dir, "06_hypothesis_1.json")
        self.md_file = os.path.join(self.stage_dir, "06_hypothesis_1.md")
        self.docx_file = os.path.join(self.stage_dir, "06_hypothesis_1.docx")

        self.sample_stats = {
            "hypothesis_id": "H1",
            "sample_size": 120,
            "f_stat": 14.52,
            "p_value": 0.001,
            "effect_size": 0.28,
            "coefficients": [
                {"predictor": "ACT_Intervention", "b": 7.32, "beta": 0.45, "t": 3.81, "p_value": ".001"}
            ]
        }
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(self.sample_stats, f, indent=2)

        self.sample_md = (
            "# Hypothesis 1 Results\n\n"
            "An analysis of covariance was conducted with N = 120 participants. "
            "The omnibus test was significant, F = 14.52, p < .001, eta_p^2 = 0.28. "
            "The standardized regression coefficient was beta = 0.45, t = 3.81, B = 7.32.\n"
        )
        with open(self.md_file, "w", encoding="utf-8") as f:
            f.write(self.sample_md)

        # Create mock DOCX file (zip containing word/document.xml)
        import zipfile
        with zipfile.ZipFile(self.docx_file, "w") as zf:
            xml_text = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                '<w:body><w:p><w:r><w:t>Hypothesis 1 Findings: N = 120, F = 14.52, p &lt; .001, beta = 0.45, t = 3.81, B = 7.32, eta_p2 = 0.28</w:t></w:r></w:p></w:body>'
                '</w:document>'
            )
            zf.writestr("word/document.xml", xml_text)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_build_and_verify_valid_stage_manifest_triad(self):
        """Tests successful generation and authoritative verification of Triad manifest."""
        manifest = build_stage_manifest(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="phase8_study",
            agent="statistics-agent",
            script_or_generator="scripts/statistical_pipeline_engine.py",
            command="python3 scripts/statistical_pipeline_engine.py --mode production",
            inputs=[{"path": self.input_file, "description": "Raw cleaned empirical data"}],
            cross_agreement_required=True,
            write_manifest=True
        )
        self.assertEqual(manifest["stage_id"], "06_hypothesis_1")
        self.assertEqual(manifest["status"], "VALIDATED")
        self.assertIn("06_hypothesis_1.json", manifest["hashes"])
        self.assertIn("06_hypothesis_1.md", manifest["hashes"])
        self.assertIn("06_hypothesis_1.docx", manifest["hashes"])

        manifest_path = os.path.join(self.stage_dir, "manifest.json")
        self.assertTrue(os.path.isfile(manifest_path))

        # Verify manifest
        res = verify_stage_manifest(manifest_path, fail_closed=True)
        self.assertEqual(res["verdict"], "PASS")

    def test_02_missing_manifest_fails_closed(self):
        """Tests that missing manifest.json raises MissingStageManifestError."""
        non_existent_manifest = os.path.join(self.temp_dir, "non_existent_manifest.json")
        with self.assertRaises(MissingStageManifestError):
            verify_stage_manifest(non_existent_manifest, fail_closed=True)

    def test_03_missing_declared_artifact_fails_closed(self):
        """Tests that a missing deliverable on disk raises ManifestArtifactMissingError."""
        build_stage_manifest(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="phase8_study",
            agent="statistics-agent",
            script_or_generator="scripts/statistical_pipeline_engine.py",
            inputs=[{"path": self.input_file}],
            cross_agreement_required=False,
            write_manifest=True
        )
        manifest_path = os.path.join(self.stage_dir, "manifest.json")

        # Delete docx file
        os.remove(self.docx_file)

        with self.assertRaises(ManifestArtifactMissingError):
            verify_stage_manifest(manifest_path, fail_closed=True)

    def test_04_tampered_artifact_hash_fails_closed(self):
        """Tests that modifying an artifact after manifest creation raises ManifestHashMismatchError."""
        build_stage_manifest(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="phase8_study",
            agent="statistics-agent",
            script_or_generator="scripts/statistical_pipeline_engine.py",
            inputs=[{"path": self.input_file}],
            cross_agreement_required=False,
            write_manifest=True
        )
        manifest_path = os.path.join(self.stage_dir, "manifest.json")

        # Tamper with markdown artifact
        with open(self.md_file, "a", encoding="utf-8") as f:
            f.write("\n<!-- Tampered content -->\n")

        with self.assertRaises(ManifestHashMismatchError):
            verify_stage_manifest(manifest_path, fail_closed=True)

    def test_05_tampered_input_file_fails_closed(self):
        """Tests that modifying an input dataset raises ManifestInputMismatchError."""
        build_stage_manifest(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="phase8_study",
            agent="statistics-agent",
            script_or_generator="scripts/statistical_pipeline_engine.py",
            inputs=[{"path": self.input_file}],
            cross_agreement_required=False,
            write_manifest=True
        )
        manifest_path = os.path.join(self.stage_dir, "manifest.json")

        # Tamper with input file
        with open(self.input_file, "a", encoding="utf-8") as f:
            f.write("3,ACT,30.0\n")

        with self.assertRaises(ManifestInputMismatchError):
            verify_stage_manifest(manifest_path, fail_closed=True)

    def test_06_cross_artifact_contradiction_fails_closed(self):
        """Tests that contradictory numbers across JSON and Markdown raise ManifestCrossAgreementError."""
        # Overwrite markdown with contradictory F-statistic
        with open(self.md_file, "w", encoding="utf-8") as f:
            f.write("# Contradictory Results\n\nN = 120, F = 99.99, p < .001, eta_p^2 = 0.28\n")

        with self.assertRaises(ManifestCrossAgreementError):
            build_stage_manifest(
                stage_dir=self.stage_dir,
                stage_id="06_hypothesis_1",
                project_id="phase8_study",
                agent="statistics-agent",
                script_or_generator="scripts/statistical_pipeline_engine.py",
                inputs=[{"path": self.input_file}],
                cross_agreement_required=True,
                write_manifest=True
            )

    def test_07_dependency_manifest_hash_tampering_fails_closed(self):
        """Tests that tampering with an upstream stage manifest raises ManifestDependencyMismatchError."""
        upstream_dir = os.path.join(self.temp_dir, "stage_05_macro_model")
        os.makedirs(upstream_dir, exist_ok=True)
        upstream_manifest_file = os.path.join(upstream_dir, "manifest.json")
        with open(upstream_manifest_file, "w", encoding="utf-8") as f:
            json.dump({"contract_version": "1.0.0", "stage_id": "05_macro_model", "status": "APPROVED"}, f)
        
        upstream_hash = compute_sha256(upstream_manifest_file)

        build_stage_manifest(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="phase8_study",
            agent="statistics-agent",
            script_or_generator="scripts/statistical_pipeline_engine.py",
            inputs=[{"path": self.input_file}],
            dependencies=[{
                "stage_id": "05_macro_model",
                "manifest_path": upstream_manifest_file,
                "manifest_hash": upstream_hash
            }],
            cross_agreement_required=False,
            write_manifest=True
        )
        manifest_path = os.path.join(self.stage_dir, "manifest.json")

        # Mutate upstream manifest
        with open(upstream_manifest_file, "w", encoding="utf-8") as f:
            json.dump({"contract_version": "1.0.0", "stage_id": "05_macro_model", "status": "TAMPERED"}, f)

        with self.assertRaises(ManifestDependencyMismatchError):
            verify_stage_manifest(manifest_path, fail_closed=True)

    def test_08_triad_invariant_enforcement_for_hypothesis_stages(self):
        """Tests that hypothesis micro-stages strictly enforce the .json + .md + .docx Triad."""
        os.remove(self.docx_file)

        with self.assertRaises(ManifestTriadMissingError):
            build_stage_manifest(
                stage_dir=self.stage_dir,
                stage_id="06_hypothesis_1",
                project_id="phase8_study",
                agent="statistics-agent",
                script_or_generator="scripts/statistical_pipeline_engine.py",
                inputs=[{"path": self.input_file}],
                cross_agreement_required=False,
                write_manifest=True
            )

    def test_09_state_machine_transition_gated_by_manifest(self):
        """Tests that StrictStateMachine requires authoritative manifest and updates its status upon approval."""
        manifest = build_stage_manifest(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="phase8_study",
            agent="statistics-agent",
            script_or_generator="scripts/statistical_pipeline_engine.py",
            inputs=[{"path": self.input_file}],
            cross_agreement_required=True,
            write_manifest=True
        )
        manifest_path = os.path.join(self.stage_dir, "manifest.json")

        # Create validation report
        val_report = os.path.join(self.state_dir, "06_hypothesis_1_validation.json")
        with open(val_report, "w", encoding="utf-8") as f:
            json.dump({"overall_verdict": "PASS", "verdict": "PASS"}, f)

        self.sm.register_stage(
            stage_id="06_hypothesis_1",
            title="Hypothesis 1 Testing",
            initial_status=StageState.STAGE_READY,
            dependencies=[],
            required_input_artifacts=[],
            required_output_artifacts=[os.path.relpath(self.json_file, self.state_dir)],
            requires_validation=True,
            requires_manifest=True
        )

        # Advance READY -> RUNNING
        self.sm.request_transition("06_hypothesis_1", StageState.STAGE_RUNNING)

        # Advance RUNNING -> VALIDATING passing manifest path
        res = self.sm.request_transition(
            "06_hypothesis_1",
            StageState.STAGE_VALIDATING,
            execution_info={"manifest_path": manifest_path}
        )
        self.assertEqual(res["to_state"], StageState.STAGE_VALIDATING.value)

        # Advance VALIDATING -> AWAITING_APPROVAL
        res = self.sm.request_transition(
            "06_hypothesis_1",
            StageState.STAGE_AWAITING_APPROVAL,
            execution_info={"manifest_path": manifest_path}
        )
        self.assertEqual(res["to_state"], StageState.STAGE_AWAITING_APPROVAL.value)

        # Grant human approval
        appr = self.sm.request_approval(
            milestone_id="06_hypothesis_1",
            category="hypothesis_1",
            requester_agent="statistics-agent",
            rationale="Verified results and concordance"
        )
        self.sm.grant_approval(
            approval_id=appr["approval_id"],
            approver_identity="Saber Admin Desk 124911145",
            digital_signature="SIG-124911145",
            comments="Approved"
        )

        # Advance AWAITING_APPROVAL -> APPROVED
        res = self.sm.request_transition(
            "06_hypothesis_1",
            StageState.STAGE_APPROVED,
            execution_info={"manifest_path": manifest_path}
        )
        self.assertEqual(res["to_state"], StageState.STAGE_APPROVED.value)

        # Verify that manifest status on disk was updated to APPROVED
        with open(manifest_path, "r", encoding="utf-8") as f:
            updated_manifest = json.load(f)
        self.assertEqual(updated_manifest["status"], "APPROVED")
        self.assertIsNotNone(updated_manifest["timestamps"].get("approved_at"))

    def test_10_cli_build_and_verify(self):
        """Tests the CLI build and verify subcommands via subprocess."""
        cmd_build = [
            sys.executable,
            os.path.join(ROOT_DIR, "scripts", "stage_manifest_engine.py"),
            "build",
            "--stage-dir", self.stage_dir,
            "--stage-id", "06_hypothesis_1",
            "--project-id", "phase8_study",
            "--agent", "statistics-agent",
            "--script", "scripts/statistical_pipeline_engine.py"
        ]
        res_build = subprocess.run(cmd_build, capture_output=True, text=True)
        self.assertEqual(res_build.returncode, 0, msg=res_build.stderr)

        manifest_path = os.path.join(self.stage_dir, "manifest.json")
        self.assertTrue(os.path.isfile(manifest_path))

        cmd_verify = [
            sys.executable,
            os.path.join(ROOT_DIR, "scripts", "stage_manifest_engine.py"),
            "verify",
            "--manifest", manifest_path
        ]
        res_verify = subprocess.run(cmd_verify, capture_output=True, text=True)
        self.assertEqual(res_verify.returncode, 0, msg=res_verify.stderr)
        self.assertIn('"verdict": "PASS"', res_verify.stdout)


if __name__ == "__main__":
    unittest.main()
