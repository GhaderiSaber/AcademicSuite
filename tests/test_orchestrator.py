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
        self.assertEqual(apa_res["agent"], "writing-agent")

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

    def test_03_prerequisites_check_ready(self):
        """Verify that study_act_burnout passes prerequisite check for demographics."""
        study_state = os.path.join(ROOT_DIR, "projects", "study_act_burnout", "academic-state")
        res = odr.check_prerequisites("01_demographics", study_state)
        self.assertEqual(res["status"], "READY")
        self.assertEqual(res["assigned_agent"], "statistics-agent")
        self.assertEqual(res["required_skill"], "descriptive-statistics")

    def test_04_format_delegation_envelope(self):
        """Verify formatting of isolated context delegation envelopes."""
        study_state = os.path.join(ROOT_DIR, "projects", "study_act_burnout", "academic-state")
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


if __name__ == "__main__":
    unittest.main()
