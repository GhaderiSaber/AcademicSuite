#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_synthetic_escape_route_elimination.py — Comprehensive Unit Tests for Phase 6

Verifies complete elimination of synthetic data escape routes and universal fail-closed policy:
1. Persian Defense Presentation Builder: Production mode strictly blocks silent sample fallback.
2. Intervention Protocol Compiler: Production mode strictly blocks sample fixtures and unprovided payloads.
3. Universal Script Execution Guard: Rejects synthetic flags, sample datasets, and internally tagged payloads in production.
4. Academic Dual Loop Engine: Production mode blocks synthetic mock experiences and fallback statistics.
5. Master Academic Orchestrator: Rejects sample/synthetic data in production and supports explicit simulation mode.
"""

import os
import sys
import json
import tempfile
import unittest
import subprocess
from pathlib import Path

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.script_execution_guard import (
    enforce_script_safety,
    ProductionSampleFallbackBlockedError,
    InvalidExecutionModeError
)
from scripts.academic_dual_loop_engine import (
    AcademicDualLoopEngine,
    MissingProductionDataError
)
import importlib.util

orchestrator_path = os.path.join(ROOT_DIR, ".agents", "skills", "academic-suite-orchestrator", "scripts", "orchestrator_cli.py")
spec = importlib.util.spec_from_file_location("orchestrator_cli", orchestrator_path)
orchestrator_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(orchestrator_mod)

MasterAcademicOrchestrator = orchestrator_mod.MasterAcademicOrchestrator
OrchestratorSampleBlockedError = orchestrator_mod.ProductionSampleFallbackBlockedError


class TestSyntheticEscapeRouteElimination(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_test_escape_routes_")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # 1. Script Execution Guard Tests
    # -------------------------------------------------------------------------
    def test_01_guard_blocks_sample_dataset_in_production(self):
        """Guard must raise ProductionSampleFallbackBlockedError if sample dataset is used in production."""
        sample_file = os.path.join(self.temp_dir, "sample_patients.csv")
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write("id,group,score\n1,ACT,24.5\n")

        with self.assertRaises(ProductionSampleFallbackBlockedError):
            enforce_script_safety(
                dataset_path=sample_file,
                mode="production",
                require_approved_plan=False
            )

    def test_02_guard_blocks_explicit_synthetic_flag_in_production(self):
        """Guard must raise ProductionSampleFallbackBlockedError if is_synthetic=True in production."""
        real_file = os.path.join(self.temp_dir, "real_patients.csv")
        with open(real_file, "w", encoding="utf-8") as f:
            f.write("id,group,score\n1,ACT,24.5\n")

        with self.assertRaises(ProductionSampleFallbackBlockedError):
            enforce_script_safety(
                dataset_path=real_file,
                mode="production",
                require_approved_plan=False,
                is_synthetic=True
            )

    def test_03_guard_blocks_internally_tagged_synthetic_json_in_production(self):
        """Guard must inspect JSON payloads and reject internal synthetic markers in production."""
        synth_json = os.path.join(self.temp_dir, "study_metrics.json")
        with open(synth_json, "w", encoding="utf-8") as f:
            json.dump({"data": [1, 2, 3], "is_synthetic": True}, f)

        with self.assertRaises(ProductionSampleFallbackBlockedError):
            enforce_script_safety(
                dataset_path=synth_json,
                mode="production",
                require_approved_plan=False
            )

    def test_04_guard_allows_synthetic_data_in_explicit_simulation_mode(self):
        """Guard must allow synthetic data when mode='simulation' is explicit."""
        synth_json = os.path.join(self.temp_dir, "simulation_data.json")
        with open(synth_json, "w", encoding="utf-8") as f:
            json.dump({"data": [1, 2, 3], "is_synthetic": True}, f)

        provenance = enforce_script_safety(
            dataset_path=synth_json,
            mode="simulation",
            require_approved_plan=False,
            is_synthetic=True
        )
        self.assertEqual(provenance["execution_mode"], "simulation")
        self.assertTrue(provenance["is_synthetic"])

    # -------------------------------------------------------------------------
    # 2. Persian Defense Presentation Builder Tests
    # -------------------------------------------------------------------------
    def test_05_presentation_builder_cli_blocks_sample_in_production(self):
        """CLI invocation of presentation builder must fail-closed in production when inputs are missing."""
        main_py = os.path.join(ROOT_DIR, ".agents", "skills", "persian-defense-presentation-builder", "main.py")
        cmd = [
            sys.executable,
            main_py,
            "--path", "html",
            "--mode", "production"
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=self.temp_dir)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("CRITICAL SAFETY VIOLATION", proc.stderr)
        self.assertIn("Silent fallback to sample data is strictly BLOCKED", proc.stderr)

    def test_06_presentation_builder_cli_blocks_sample_json_pointer_in_production(self):
        """CLI invocation of presentation builder must reject sample file pointers in production."""
        main_py = os.path.join(ROOT_DIR, ".agents", "skills", "persian-defense-presentation-builder", "main.py")
        sample_json = os.path.join(self.temp_dir, "sample_stats.json")
        with open(sample_json, "w", encoding="utf-8") as f:
            json.dump({"title": "Sample Study"}, f)

        cmd = [
            sys.executable,
            main_py,
            "--path", "pptx",
            "--json", sample_json,
            "--mode", "production"
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=self.temp_dir)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("CRITICAL SAFETY VIOLATION", proc.stderr)
        self.assertIn("cannot consume sample fixture", proc.stderr)

    # -------------------------------------------------------------------------
    # 3. Intervention Protocol Compiler Tests
    # -------------------------------------------------------------------------
    def test_07_intervention_compiler_blocks_missing_payload_in_production(self):
        """Intervention compiler CLI must fail-closed in production if --json is omitted."""
        compiler_py = os.path.join(
            ROOT_DIR,
            ".agents", "skills", "psychological-intervention-protocol-builder", "scripts", "compile_intervention_protocol.py"
        )
        cmd = [
            sys.executable,
            compiler_py,
            "--mode", "production"
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=self.temp_dir)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("MissingProductionDataError", proc.stderr)
        self.assertIn("CRITICAL SAFETY VIOLATION", proc.stderr)

    def test_08_intervention_compiler_blocks_sample_payload_in_production(self):
        """Intervention compiler CLI must reject sample fixture JSON in production mode."""
        compiler_py = os.path.join(
            ROOT_DIR,
            ".agents", "skills", "psychological-intervention-protocol-builder", "scripts", "compile_intervention_protocol.py"
        )
        sample_json = os.path.join(self.temp_dir, "sample_intervention.json")
        with open(sample_json, "w", encoding="utf-8") as f:
            json.dump({"meta": {"title": "Sample Intervention"}, "sessions": []}, f)

        cmd = [
            sys.executable,
            compiler_py,
            "--json", sample_json,
            "--mode", "production"
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=self.temp_dir)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("ProductionSampleFallbackBlockedError", proc.stderr)

    # -------------------------------------------------------------------------
    # 4. Dual Loop Evolution Engine Tests
    # -------------------------------------------------------------------------
    def test_09_dual_loop_blocks_missing_experience_in_production(self):
        """Fast loop in production must not synthesize mock fast_loop_project."""
        engine = AcademicDualLoopEngine(base_dir=self.temp_dir)
        with self.assertRaises(MissingProductionDataError) as ctx:
            engine.run_fast_loop(
                task_prompt="Production analysis",
                mode="production"
            )
        self.assertIn("requires an existing empirical experience_id", str(ctx.exception))

    def test_10_dual_loop_blocks_missing_artifacts_in_production(self):
        """Fast loop in production must not fall back to predefined statistics."""
        engine = AcademicDualLoopEngine(base_dir=self.temp_dir)
        with self.assertRaises(MissingProductionDataError) as ctx:
            engine.run_fast_loop(
                task_prompt="Production analysis",
                existing_experience_id="EXP-12345",
                artifacts=None,
                mode="production"
            )
        self.assertIn("requires real physical artifact outputs", str(ctx.exception))

    def test_11_dual_loop_allows_simulation_mode(self):
        """Fast loop with mode='simulation' explicitly allows synthetic artifacts."""
        engine = AcademicDualLoopEngine(base_dir=self.temp_dir)
        res = engine.run_fast_loop(
            task_prompt="Simulation analysis comparing candidate models.",
            user_correction="You forgot to report effect size and confidence intervals.",
            target_agent="statistics-agent",
            target_skill="statistical-data-analyst",
            capability="statistical-data-analyst",
            mode="simulation",
            artifacts={
                "narrative": "تحلیل شبیه‌سازی انجام شد (۰.۰۵ > p).",
                "statistics": {
                    "estimand": "Simulation Estimand",
                    "effect_size": 0.25,
                    "confidence_interval": [0.10, 0.40],
                    "artifact_path": "03_sim.json",
                    "assumptions_checked": ["homogeneity of slopes"],
                    "is_synthetic": True,
                    "data_mode": "simulation"
                }
            }
        )
        self.assertEqual(res["status"], "COMPLETED")
        self.assertIn("candidate_id", res)

    # -------------------------------------------------------------------------
    # 5. Master Academic Orchestrator Tests
    # -------------------------------------------------------------------------
    def test_12_orchestrator_blocks_sample_payload_in_production(self):
        """MasterAcademicOrchestrator must reject sample payload pointers in production."""
        sample_payload = os.path.join(self.temp_dir, "sample_input.json")
        with open(sample_payload, "w", encoding="utf-8") as f:
            json.dump({"title": "Sample Study"}, f)

        config_file = os.path.join(self.temp_dir, "project_config.json")
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump({
                "project_id": "PRJ-001",
                "steps": {
                    "proposal": {"payload": sample_payload}
                }
            }, f)

        orchestrator = MasterAcademicOrchestrator(
            config_path=config_file,
            out_dir=self.temp_dir,
            mode="production"
        )
        with self.assertRaises(OrchestratorSampleBlockedError):
            orchestrator._resolve_payload(
                step="proposal",
                step_conf={"payload": sample_payload}
            )

    def test_13_orchestrator_supports_explicit_simulation_mode(self):
        """MasterAcademicOrchestrator records is_synthetic=True when mode='simulation'."""
        orchestrator = MasterAcademicOrchestrator(
            config_path=None,
            out_dir=self.temp_dir,
            mode="simulation"
        )
        self.assertEqual(orchestrator.mode, "simulation")
        self.assertTrue(orchestrator.manifest["is_synthetic"])
        self.assertEqual(orchestrator.manifest["data_mode"], "simulation")


if __name__ == "__main__":
    unittest.main()
