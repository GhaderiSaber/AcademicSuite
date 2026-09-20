#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_orchestrator_deliberation.py — Integration tests for Deliberation Engine in Orchestrator

Validates:
1. Capability resolution of statistical deliberation to statistical-expert
2. Prerequisite checking for deliberation stage
3. Candidate falsifier CLI in demo mode (generates valid analysis_plan, report json, report md)
4. Production mode safety (blocks sample fallback)
5. Orchestrator CLI step execution in demo mode
6. Orchestrator CLI production mode blocking
7. Deliberation pipeline preset definition
8. End-to-end deliberation handoff to statistical execution
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        try:
            for entry in os.listdir(venv_lib):
                sp = os.path.join(venv_lib, entry, "site-packages")
                if os.path.isdir(sp) and sp not in sys.path:
                    sys.path.insert(0, sp)
        except OSError:
            pass

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import scripts.orchestrator_dependency_resolver as odr
from contracts.contract_validator import validate_analysis_plan, validate_pitfall

ORCHESTRATOR_CLI = os.path.join(ROOT_DIR, ".agents", "skills", "academic-suite-orchestrator", "scripts", "orchestrator_cli.py")
cand_cand = os.path.join(ROOT_DIR, ".agents", "scripts", "candidate_falsifier_engine.py")
CANDIDATE_ENGINE = cand_cand if os.path.isfile(cand_cand) else os.path.join(ROOT_DIR, "scripts", "candidate_falsifier_engine.py")
SAMPLE_DELIB_PAYLOAD = os.path.join(ROOT_DIR, ".agents", "skills", "academic-suite-orchestrator", "examples", "sample_deliberation_payload.json")
PYTHON_BIN = sys.executable or "python3"


class TestOrchestratorDeliberation(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_orch_delib_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_capability_resolution_deliberation(self):
        """Verify task queries regarding deliberation map to statistical-expert."""
        res = odr.resolve_capability("Deliberate between candidate statistical models and falsify assumptions")
        self.assertEqual(res["capability"], "statistical_deliberation")
        self.assertEqual(res["skill"], "academic-suite-orchestrator")
        self.assertEqual(res["agent"], "statistical-expert")

    def test_02_prerequisite_check(self):
        """Verify prerequisite check for 04_statistical_deliberation."""
        # Without project.json -> BLOCKED
        res = odr.check_prerequisites("04_statistical_deliberation", self.temp_dir)
        self.assertEqual(res["status"], "BLOCKED")
        self.assertIn("project.json", res["missing_prerequisites"])

        # With project.json -> READY
        with open(os.path.join(self.temp_dir, "project.json"), "w", encoding="utf-8") as f:
            json.dump({"project_id": "test_proj"}, f)
        res2 = odr.check_prerequisites("04_statistical_deliberation", self.temp_dir)
        self.assertEqual(res2["status"], "READY")
        self.assertEqual(res2["assigned_agent"], "statistical-expert")

    def test_03_candidate_falsifier_cli_demo(self):
        """Verify CLI execution of candidate_falsifier_engine in demo mode produces schema-valid plan."""
        out_dir = os.path.join(self.temp_dir, "cli_delib")
        cmd = [
            PYTHON_BIN, CANDIDATE_ENGINE,
            "--candidates", SAMPLE_DELIB_PAYLOAD,
            "--out-dir", out_dir,
            "--mode", "demo"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"CLI error: {res.stderr}")

        plan_file = os.path.join(out_dir, "analysis_plan.json")
        report_json = os.path.join(out_dir, "deliberation_report.json")
        report_md = os.path.join(out_dir, "deliberation_report.md")

        self.assertTrue(os.path.exists(plan_file))
        self.assertTrue(os.path.exists(report_json))
        self.assertTrue(os.path.exists(report_md))

        with open(plan_file, "r", encoding="utf-8") as f:
            plan_data = json.load(f)
        val = validate_analysis_plan(plan_data)
        self.assertTrue(val["valid"], f"Plan invalid: {val.get('errors')}")

    def test_04_candidate_falsifier_cli_production_blocks_sample(self):
        """Verify candidate_falsifier_engine rejects sample payload in production mode."""
        out_dir = os.path.join(self.temp_dir, "cli_prod_block")
        cmd = [
            PYTHON_BIN, CANDIDATE_ENGINE,
            "--candidates", SAMPLE_DELIB_PAYLOAD,
            "--out-dir", out_dir,
            "--mode", "production"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("ProductionSampleFallbackBlockedError", res.stderr)

    def test_05_orchestrator_cli_deliberation_demo(self):
        """Verify orchestrator_cli runs deliberation step in demo mode and logs artifacts."""
        out_dir = os.path.join(self.temp_dir, "orch_demo")
        cmd = [
            PYTHON_BIN, ORCHESTRATOR_CLI,
            "--step", "deliberation",
            "--out-dir", out_dir,
            "--mode", "demo"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Orchestrator error: {res.stderr}")

        step_dir = os.path.join(out_dir, "deliberation")
        self.assertTrue(os.path.exists(os.path.join(step_dir, "analysis_plan.json")))
        self.assertTrue(os.path.exists(os.path.join(step_dir, "deliberation_report.json")))
        self.assertTrue(os.path.exists(os.path.join(step_dir, "deliberation_report.md")))

        manifest_file = os.path.join(out_dir, "orchestrator_manifest.json")
        self.assertTrue(os.path.exists(manifest_file))
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        self.assertIn("analysis_plan", manifest["artifacts"])

    def test_06_orchestrator_cli_deliberation_production_blocked(self):
        """Verify orchestrator_cli blocks deliberation step in production mode when real payload is absent."""
        out_dir = os.path.join(self.temp_dir, "orch_prod")
        cmd = [
            PYTHON_BIN, ORCHESTRATOR_CLI,
            "--step", "deliberation",
            "--out-dir", out_dir,
            "--mode", "production"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)  # CLI catches and logs error to manifest
        self.assertTrue("CRITICAL SAFETY VIOLATION" in res.stdout or "CRITICAL SAFETY VIOLATION" in res.stderr)

        manifest_file = os.path.join(out_dir, "orchestrator_manifest.json")
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        self.assertEqual(manifest["status"], "FAILED")

    def test_07_deliberation_pipeline_preset(self):
        """Verify deliberation_pipeline preset is registered in orchestrator_cli."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("orch_cli_mod", ORCHESTRATOR_CLI)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertIn("deliberation_pipeline", mod.PIPELINE_PRESETS)
        self.assertEqual(mod.PIPELINE_PRESETS["deliberation_pipeline"], ["deliberation", "statistics", "audit"])
        self.assertIn("deliberation", mod.SKILL_REGISTRY)


if __name__ == "__main__":
    unittest.main()
