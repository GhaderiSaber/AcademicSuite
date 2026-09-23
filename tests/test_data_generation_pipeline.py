# -*- coding: utf-8 -*-
"""
test_data_generation_pipeline.py — Unit & Integration Tests for Data Generation Pipeline

Validates:
1. Task Router maps data creation intents to 'data_simulation' capability and 'data-agent'.
2. Orchestrator Dependency Resolver recognizes 'data_simulation' in registry and dependency graph.
3. Contractual Delegation Envelope generation for '00_data_generation' stage.
4. Orchestrator CLI supports turnkey '--pipeline data_generation'.
5. Micro-stage sequence documentation and architecture invariants.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
import subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, ".agents", "scripts"))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
sys.path.insert(0, os.path.join(REPO_ROOT, ".agents", "skills", "academic-suite-orchestrator", "scripts"))

from academic_task_router import CapabilityResolver, _GLOBAL_REGISTRY
import orchestrator_dependency_resolver as odr
from orchestrator_cli import PIPELINE_PRESETS, MasterAcademicOrchestrator


class TestDataGenerationPipeline(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_data_gen_pipe_")
        self.router = CapabilityResolver()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_registry_contains_data_simulation(self):
        """Verifies data_simulation capability is registered in capabilities.yaml and router registry."""
        cap = _GLOBAL_REGISTRY.get("data_simulation")
        self.assertIsNotNone(cap, "data_simulation capability must be defined in capabilities.yaml")
        self.assertEqual(cap.get("primary_agent"), "data-agent")
        self.assertIn("psychometric-data-simulator", cap.get("required_skills", []))
        self.assertEqual(cap.get("domain"), "data")

    def test_02_task_router_resolves_data_creation_prompts(self):
        """Verifies task router detects data_simulation for varied data generation intents."""
        test_prompts = [
            "Create data for SEM model with 200 participants",
            "Simulate survey dataset with 5 Likert scales",
            "Generate synthetic data for an RCT trial",
            "Make data based on P13 notebook"
        ]
        for prompt in test_prompts:
            plan = self.router.resolve(prompt)
            self.assertEqual(plan["status"], "RESOLVED", f"Failed for prompt: {prompt}")
            self.assertIn(
                "data_simulation",
                plan["required_capabilities"],
                f"'data_simulation' not found in required capabilities for prompt: {prompt}"
            )
            self.assertIn("data-agent", plan["required_subagents"]["primary_agents"])

    def test_03_dependency_resolver_mapping(self):
        """Verifies orchestrator_dependency_resolver resolves data_simulation capability."""
        res = odr.resolve_capability("Simulate psychometric dataset for structural equation modeling")
        self.assertEqual(res["capability"], "data_simulation")
        self.assertEqual(res["agent"], "data-agent")
        self.assertEqual(res["skill"], "psychometric-data-simulator")

    def test_04_stage_dependency_prerequisites_check(self):
        """Verifies 00_data_generation prerequisite checks in orchestrator_dependency_resolver."""
        # When required files are missing:
        empty_dir = os.path.join(self.temp_dir, "empty_state")
        os.makedirs(empty_dir, exist_ok=True)
        res_blocked = odr.check_prerequisites("00_data_generation", empty_dir)
        self.assertEqual(res_blocked["status"], "BLOCKED")
        self.assertIn("missing_files", res_blocked)

        # When project.json and requirements.json are present:
        ready_dir = os.path.join(self.temp_dir, "ready_state")
        os.makedirs(ready_dir, exist_ok=True)
        with open(os.path.join(ready_dir, "project.json"), "w", encoding="utf-8") as f:
            json.dump({"project_id": "test_sim_proj"}, f)
        with open(os.path.join(ready_dir, "requirements.json"), "w", encoding="utf-8") as f:
            json.dump({"sample_size": 250, "model": "sem"}, f)

        res_ready = odr.check_prerequisites("00_data_generation", ready_dir)
        self.assertEqual(res_ready["status"], "READY")
        self.assertEqual(res_ready["assigned_agent"], "data-agent")
        self.assertEqual(res_ready["required_skill"], "psychometric-data-simulator")

    def test_05_format_delegation_envelope_data_generation(self):
        """Verifies delegation envelope formatting for 00_data_generation stage."""
        ready_dir = os.path.join(self.temp_dir, "ready_envelope_state")
        os.makedirs(ready_dir, exist_ok=True)
        with open(os.path.join(ready_dir, "project.json"), "w", encoding="utf-8") as f:
            json.dump({"project_id": "test_envelope_proj"}, f)
        with open(os.path.join(ready_dir, "requirements.json"), "w", encoding="utf-8") as f:
            json.dump({"sample_size": 200}, f)

        envelope = odr.format_delegation_envelope(
            "00_data_generation",
            ready_dir,
            "Simulate SEM data with 10 manifest indicators and 3 latent variables."
        )
        self.assertEqual(envelope["status"], "READY")
        self.assertEqual(envelope["agent"], "data-agent")
        self.assertIn("subagent_invocation", envelope)

        inv = envelope["subagent_invocation"]
        self.assertEqual(inv["TypeName"], "data-agent")
        self.assertIn("psychometric-data-simulator", inv["Prompt"])
        self.assertIn("Directive 6", inv["Prompt"])

    def test_06_orchestrator_cli_supports_data_generation_preset(self):
        """Verifies orchestrator_cli recognizes and executes data_generation pipeline in dry-run."""
        self.assertIn("data_generation", PIPELINE_PRESETS)
        steps = PIPELINE_PRESETS["data_generation"]
        self.assertIn("simulation", steps)
        self.assertIn("audit", steps)

        orch = MasterAcademicOrchestrator(
            config_path=None,
            out_dir=self.temp_dir,
            pipeline_name="data_generation",
            dry_run=True
        )
        orch.execute()
        self.assertEqual(orch.manifest["status"], "COMPLETED")
        self.assertEqual(len(orch.manifest["steps_executed"]), len(steps))

    def test_07_micro_stage_sequences_documentation(self):
        """Verifies Section 7 Empirical Data Generation Pipeline is codified in MICRO_STAGE_SEQUENCES.md."""
        seq_path = os.path.join(REPO_ROOT, ".agents", "references", "MICRO_STAGE_SEQUENCES.md")
        with open(seq_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("## 7. Empirical Data Generation & Simulation Pipeline (Stages DS.1 – DS.5)", content)
        self.assertIn("Stage DS.1", content)
        self.assertIn("Stage DS.3", content)
        self.assertIn("Stage DS.5", content)
        self.assertIn("Directive 9 (Realistic Decimal Noise)", content)


if __name__ == "__main__":
    unittest.main()
