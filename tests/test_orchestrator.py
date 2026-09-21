#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_orchestrator.py — Unit tests for Master Academic Orchestrator
Tests:
1. Capability-to-Skill-to-Agent mapping
2. Artifact prerequisite dependency resolution
3. Delegation envelope formatting
4. Context isolation invariants
5. Orchestrator agent configuration compliance
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))
import orchestrator_dependency_resolver as odr


class TestAcademicOrchestrator(unittest.TestCase):

    def test_01_capability_mapping(self):
        """Verify mapping of task queries to skills and specialist agents."""
        sem_res = odr.resolve_capability("Run structural equation modeling with path analysis")
        self.assertEqual(sem_res["skill"], "sem")
        self.assertEqual(sem_res["agent"], "statistics-agent")

        clean_res = odr.resolve_capability("Reverse code survey items and handle missing data")
        self.assertEqual(clean_res["skill"], "data-cleaning")
        self.assertEqual(clean_res["agent"], "data-agent")

        apa_res = odr.resolve_capability("Format APA 7 three line tables with Persian font")
        self.assertEqual(apa_res["skill"], "apa-reporting")
        self.assertEqual(apa_res["agent"], "academic-writer")

        lit_res = odr.resolve_capability("Synthesize literature review from pubmed and crossref")
        self.assertEqual(lit_res["skill"], "literature-review")
        self.assertEqual(lit_res["agent"], "research-agent")

        val_res = odr.resolve_capability("Audit statistical consistency and check df")
        self.assertEqual(val_res["capability"], "validation_audit")
        self.assertEqual(val_res["agent"], "validation-agent")

    def test_02_prerequisites_check_blocked(self):
        """Verify that a stage is blocked if its required input artifacts are missing."""
        temp_dir = tempfile.mkdtemp(prefix="orch_prereq_test_")
        try:
            # Empty state directory
            res = odr.check_prerequisites("05_macro_model", temp_dir)
            self.assertEqual(res["status"], "BLOCKED")
            self.assertIn("missing_prerequisites", res)
            self.assertIn("analysis/descriptive.json", res["missing_prerequisites"])
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _create_ready_state_dir(self):
        temp_dir = tempfile.mkdtemp(prefix="orch_ready_state_")
        proj_data = {"project_id": "test_ready_proj", "completed_stages": ["00_data_curation"]}
        with open(os.path.join(temp_dir, "project.json"), "w", encoding="utf-8") as f:
            json.dump(proj_data, f)
        os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
        with open(os.path.join(temp_dir, "data", "data_dictionary.json"), "w", encoding="utf-8") as f:
            json.dump({"variables": ["group", "gender", "age"]}, f)
        return temp_dir

    def test_03_prerequisites_check_ready(self):
        """Verify that a valid project passes prerequisite check for demographics."""
        study_state = self._create_ready_state_dir()
        try:
            res = odr.check_prerequisites("01_demographics", study_state)
            self.assertEqual(res["status"], "READY")
            self.assertEqual(res["assigned_agent"], "statistics-agent")
            self.assertEqual(res["required_skill"], "descriptive-statistics")
        finally:
            shutil.rmtree(study_state, ignore_errors=True)

    def test_04_format_delegation_envelope(self):
        """Verify formatting of isolated context delegation envelopes."""
        study_state = self._create_ready_state_dir()
        try:
            env = odr.format_delegation_envelope(
                "01_demographics",
                study_state,
                "Compute frequency distributions for group, gender, and age."
            )
            self.assertEqual(env["status"], "READY")
            self.assertEqual(env["agent"], "statistics-agent")
            self.assertIn("subagent_invocation", env)

            invocation = env["subagent_invocation"]
            self.assertEqual(invocation["TypeName"], "statistics-agent")
            self.assertIn("Contractual Delegation Envelope", invocation["Prompt"])
            self.assertIn("descriptive-statistics", invocation["Prompt"])
            self.assertIn("Directive 6", invocation["Prompt"])
        finally:
            shutil.rmtree(study_state, ignore_errors=True)

    def test_05_orchestrator_agent_definition(self):
        """Verify academic-orchestrator agent prompt and tools configuration."""
        orch_path = os.path.join(ROOT_DIR, ".agents", "agents", "academic-orchestrator.md")
        self.assertTrue(os.path.exists(orch_path), "academic-orchestrator.md missing")

        with open(orch_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("name: academic-orchestrator", content)
        self.assertIn("invoke_subagent", content)
        self.assertIn("Directive 12.1", content)
        self.assertIn("Conceptual Decision Pipeline", content)
        self.assertIn("Capability-to-Skill-to-Agent Registry", content)

    def test_06_prerequisites_check_blocked_by_unapproved_state_machine_stage(self):
        """Directive 19: check_prerequisites blocks when prerequisite stage is not STAGE_APPROVED in current_state.json."""
        temp_dir = tempfile.mkdtemp(prefix="orch_state_test_")
        try:
            # Create required files for 01_demographics
            with open(os.path.join(temp_dir, "project.json"), "w", encoding="utf-8") as f:
                json.dump({"project_id": "test_proj"}, f)
            os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
            with open(os.path.join(temp_dir, "data", "data_dictionary.json"), "w", encoding="utf-8") as f:
                json.dump({"variables": []}, f)

            # current_state.json has 00_data_curation in STAGE_LOCKED
            with open(os.path.join(temp_dir, "current_state.json"), "w", encoding="utf-8") as f:
                json.dump({
                    "stages": {
                        "00_data_curation": {"status": "STAGE_LOCKED"}
                    }
                }, f)

            res = odr.check_prerequisites("01_demographics", temp_dir)
            self.assertEqual(res["status"], "BLOCKED")
            self.assertTrue(any("STAGE_LOCKED" in s for s in res["unmet_stages"]))
            self.assertIn(res["unmet_stages"][0], res["missing_prerequisites"])

            # Now test STAGE_RUNNING
            with open(os.path.join(temp_dir, "current_state.json"), "w", encoding="utf-8") as f:
                json.dump({
                    "stages": {
                        "00_data_curation": {"status": "STAGE_RUNNING"}
                    }
                }, f)

            res_running = odr.check_prerequisites("01_demographics", temp_dir)
            self.assertEqual(res_running["status"], "BLOCKED")
            self.assertTrue(any("STAGE_RUNNING" in s for s in res_running["unmet_stages"]))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_07_prerequisites_check_ready_when_state_machine_stage_approved(self):
        """Directive 19: check_prerequisites succeeds when prerequisite stage is STAGE_APPROVED in current_state.json."""
        temp_dir = tempfile.mkdtemp(prefix="orch_state_ready_")
        try:
            with open(os.path.join(temp_dir, "project.json"), "w", encoding="utf-8") as f:
                json.dump({"project_id": "test_proj"}, f)
            os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
            with open(os.path.join(temp_dir, "data", "data_dictionary.json"), "w", encoding="utf-8") as f:
                json.dump({"variables": []}, f)

            # current_state.json has 00_data_curation in STAGE_APPROVED
            with open(os.path.join(temp_dir, "current_state.json"), "w", encoding="utf-8") as f:
                json.dump({
                    "stages": {
                        "00_data_curation": {"status": "STAGE_APPROVED"}
                    }
                }, f)

            res = odr.check_prerequisites("01_demographics", temp_dir)
            self.assertEqual(res["status"], "READY")
            self.assertEqual(res["assigned_agent"], "statistics-agent")
            self.assertEqual(res["satisfied_stage"], "00_data_curation")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_08_prerequisites_check_blocked_when_project_json_stage_is_earlier(self):
        """check_prerequisites blocks when project.json indicates current stage is earlier than prerequisite stage."""
        temp_dir = tempfile.mkdtemp(prefix="orch_stage_order_")
        try:
            # Stage 05_macro_model requires 03_parametric_assumptions, but project is at 00_data_curation
            with open(os.path.join(temp_dir, "project.json"), "w", encoding="utf-8") as f:
                json.dump({
                    "project_id": "test_proj",
                    "current_stage": "00_data_curation",
                    "status": "running"
                }, f)
            os.makedirs(os.path.join(temp_dir, "analysis"), exist_ok=True)
            os.makedirs(os.path.join(temp_dir, "validation"), exist_ok=True)
            with open(os.path.join(temp_dir, "analysis", "descriptive.json"), "w", encoding="utf-8") as f:
                json.dump({}, f)
            with open(os.path.join(temp_dir, "validation", "statistical_validation.json"), "w", encoding="utf-8") as f:
                json.dump({}, f)

            res = odr.check_prerequisites("05_macro_model", temp_dir)
            self.assertEqual(res["status"], "BLOCKED")
            self.assertTrue(any("earlier than prerequisite stage '03_parametric_assumptions'" in s for s in res["unmet_stages"]))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_09_prerequisites_check_blocked_by_rejection_event_in_events_jsonl(self):
        """check_prerequisites blocks when events.jsonl records a STAGE_FAILED event for prerequisite stage."""
        temp_dir = tempfile.mkdtemp(prefix="orch_event_test_")
        try:
            with open(os.path.join(temp_dir, "project.json"), "w", encoding="utf-8") as f:
                json.dump({"project_id": "test_proj"}, f)
            os.makedirs(os.path.join(temp_dir, "data"), exist_ok=True)
            with open(os.path.join(temp_dir, "data", "data_dictionary.json"), "w", encoding="utf-8") as f:
                json.dump({"variables": []}, f)

            with open(os.path.join(temp_dir, "events.jsonl"), "w", encoding="utf-8") as f:
                f.write(json.dumps({
                    "stage_id": "00_data_curation",
                    "event_type": "STAGE_FAILED",
                    "timestamp": "2026-09-21T00:00:00Z"
                }) + "\n")

            res = odr.check_prerequisites("01_demographics", temp_dir)
            self.assertEqual(res["status"], "BLOCKED")
            self.assertTrue(any("STAGE_FAILED" in s for s in res["unmet_stages"]))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_10_capability_registry_synchronized_with_yaml(self):
        """Verify that CAPABILITY_REGISTRY includes core capabilities and stays synchronized."""
        self.assertIn("data_cleaning", odr.CAPABILITY_REGISTRY)
        self.assertIn("sem", odr.CAPABILITY_REGISTRY)
        self.assertIn("statistical_deliberation", odr.CAPABILITY_REGISTRY)
        self.assertEqual(odr.CAPABILITY_REGISTRY["sem"]["agent"], "statistics-agent")
        self.assertEqual(odr.CAPABILITY_REGISTRY["chapter_4_writing"]["agent"], "academic-writer")


if __name__ == "__main__":
    unittest.main()
