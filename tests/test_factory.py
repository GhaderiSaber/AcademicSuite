#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_factory.py — Autonomous Agent & Skill Factory Unit Tests

Validates:
1. agent-factory produces constitutional subagent specifications.
2. skill-factory produces modular skills adhering to Directive 18 (<= 500 lines, <= 40 KB).
3. validator-factory produces deterministic validators with exit codes 0/1.
4. meta-factory executes pre-registration sandbox testing and rejects invalid components.
5. Demonstration specialist (longitudinal-modmed-expert) is certified and registered.
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

from factory.agent_factory import create_agent, generate_agent_markdown
from factory.skill_factory import create_skill, generate_skill_markdown, MAX_LINES, MAX_BYTES
from factory.validator_factory import create_validator
from factory.meta_factory import run_preregistration_sandbox_test, create_specialist


class TestFactoryMetaLayer(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="academic_suite_factory_test_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_agent_factory_generates_constitutional_spec(self):
        """agent_factory must generate compliant subagent definitions adhering to AGENTS.md."""
        res = create_agent(
            name="test-specialist",
            role="Test Methodological Specialist",
            description="Specialist for testing factory generation.",
            skills=["mediation", "apa-reporting"],
            mission="Execute test procedures.",
            decision_rules=["Rule 1: Always check assumptions.", "Rule 2: Never omit leading zero."],
            target_dir=self.temp_dir
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertTrue(os.path.exists(res["file_path"]))

        with open(res["file_path"], "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("name: test-specialist", content)
        self.assertIn("Directive 0 (Binary Honesty & Anti-Deception)", content)
        self.assertIn("Directive 4 (APA 7 & Persian Leading Zero Standard)", content)
        self.assertIn("Directive 5 (BiDi OpenXML & Persian Font Binding)", content)
        self.assertIn("Rule 1: Always check assumptions.", content)

    def test_02_skill_factory_enforces_directive_18(self):
        """skill_factory must enforce Directive 18 line and byte ceilings."""
        # 1. Valid skill creation
        res = create_skill(
            name="test-skill",
            description="Test skill description.",
            sections={"Overview": "Short overview text."},
            script_name="test_script.py",
            script_code="print('Hello from test script')",
            target_dir=self.temp_dir
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertTrue(os.path.exists(res["skill_file"]))
        self.assertLessEqual(res["lines"], MAX_LINES)
        self.assertLessEqual(res["bytes"], MAX_BYTES)

        # 2. Line limit violation test (> 500 lines)
        huge_lines = {f"Section {i}": f"Line content {i}\n" * 15 for i in range(40)}
        with self.assertRaises(ValueError) as ctx:
            create_skill(
                name="huge-line-skill",
                description="Violates line limit.",
                sections=huge_lines,
                target_dir=self.temp_dir
            )
        self.assertIn("Directive 18 Violation", str(ctx.exception))

    def test_03_validator_factory_produces_working_validator(self):
        """validator_factory must scaffold working validators returning PASS/FAIL."""
        res = create_validator(
            name="test_val",
            description="Test validator description.",
            target_dir=self.temp_dir
        )
        self.assertEqual(res["status"], "SUCCESS")
        val_file = res["file_path"]
        self.assertTrue(os.path.exists(val_file))

        # Test execution on a valid JSON file
        test_json = os.path.join(self.temp_dir, "sample.json")
        with open(test_json, "w") as f:
            json.dump({"sample": "data"}, f)

        import subprocess
        run_res = subprocess.run([sys.executable, val_file, "--input", test_json], capture_output=True, text=True)
        self.assertEqual(run_res.returncode, 0)
        self.assertIn('"verdict": "PASS"', run_res.stdout)

    def test_04_preregistration_sandbox_rejection_on_failure(self):
        """Pre-registration sandbox must reject specialist if script fails or produces invalid output."""
        # Create a failing script
        failing_script = os.path.join(self.temp_dir, "failing_script.py")
        with open(failing_script, "w") as f:
            f.write("import sys\nprint('Fatal syntax crash', file=sys.stderr)\nsys.exit(1)\n")

        dummy_data = os.path.join(self.temp_dir, "data.xlsx")
        with open(dummy_data, "w") as f:
            f.write("dummy")

        dummy_val = os.path.join(self.temp_dir, "val.py")
        with open(dummy_val, "w") as f:
            f.write("import sys\nsys.exit(0)\n")

        dummy_eval_case = {"test_id": "TEST", "domain": "mediation"}

        test_res = run_preregistration_sandbox_test(
            script_path=failing_script,
            data_path=dummy_data,
            validator_path=dummy_val,
            eval_case=dummy_eval_case
        )
        self.assertEqual(test_res["overall_verdict"], "FAIL")
        self.assertEqual(test_res["script_execution"], "FAIL")
        self.assertGreater(len(test_res["errors"]), 0)

    def test_05_registered_longitudinal_modmed_specialist_verified(self):
        """The Longitudinal Moderated Mediation specialist must exist, be certified, and pass checks."""
        agent_path = os.path.join(ROOT_DIR, ".agents", "agents", "longitudinal-modmed-expert.md")
        skill_path = os.path.join(ROOT_DIR, ".agents", "skills", "longitudinal-moderated-mediation", "SKILL.md")
        candidate_val = os.path.join(ROOT_DIR, ".agents", "validators", "longitudinal_modmed", "validator.py")
        val_path = candidate_val if os.path.exists(candidate_val) else os.path.join(ROOT_DIR, "validators", "longitudinal_modmed", "validator.py")
        eval_path = os.path.join(ROOT_DIR, "evals", "mediation", "case_longitudinal_modmed_01.json")
        candidate_manifest = os.path.join(ROOT_DIR, ".agents", "factory", "specialist_manifest.json")
        manifest_path = candidate_manifest if os.path.exists(candidate_manifest) else os.path.join(ROOT_DIR, "factory", "specialist_manifest.json")

        self.assertTrue(os.path.exists(agent_path), f"Missing agent: {agent_path}")
        self.assertTrue(os.path.exists(skill_path), f"Missing skill: {skill_path}")
        self.assertTrue(os.path.exists(val_path), f"Missing validator: {val_path}")
        self.assertTrue(os.path.exists(eval_path), f"Missing eval case: {eval_path}")
        self.assertTrue(os.path.exists(manifest_path), f"Missing manifest: {manifest_path}")

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        self.assertEqual(manifest["registration_status"], "CERTIFIED_AND_REGISTERED")
        self.assertEqual(manifest["preregistration_sandbox_test"]["overall_verdict"], "PASS")

    def test_06_create_specialist_generalized(self):
        """create_specialist must dynamically generate, sandbox, validate, and certify arbitrary specialists."""
        custom_spec = {
            "name": "synthetic-screener",
            "role": "Synthetic Data Quality Screener",
            "description": "Dynamic specialist for screening data quality in unit test.",
            "mission": "You screen data quality dynamically.",
            "decision_rules": [
                "Always check for missingness across all features.",
                "Enforce APA 7 formatting for summary tables."
            ],
            "skills": ["data-audit", "apa-reporting"],
            "skill_name": "synthetic-screener",
            "skill_description": "Executes screening on test payloads.",
            "skill_sections": {
                "Overview": "Dynamic screening capability.",
                "Execution Instructions": "Run via CLI with --data and --output."
            },
            "script_name": "run_synthetic_screening.py",
            "script_code": """#!/usr/bin/env python3
import json, argparse, sys

parser = argparse.ArgumentParser()
parser.add_argument('--data', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()

with open(args.data, 'r', encoding='utf-8') as f:
    payload = json.load(f)

res = {
    "screening_verdict": "PASS",
    "sample_size": payload.get("sample_size", 100),
    "records_audited": len(payload.get("data", []))
}

with open(args.output, 'w', encoding='utf-8') as f:
    json.dump(res, f, indent=2)
""",
            "validator_name": "synthetic_screener",
            "validator_description": "Validates screening output structure.",
            "validator_custom_logic": """    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            d = json.load(f)
        if d.get("screening_verdict") != "PASS":
            errors.append("Screening verdict was not PASS.")
        if d.get("sample_size", 0) <= 0:
            errors.append("Invalid sample size.")
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")""",
            "fixture_file_name": "synthetic_screener_data.json",
            "fixture_content": {"sample_size": 120, "data": [1, 2, 3, 4, 5]},
            "eval_domain": "reliability",
            "eval_case_filename": "case_synthetic_screener_01.json",
            "eval_case": {
                "test_id": "EVAL-REL-SYNTH-01",
                "domain": "reliability",
                "title": "Synthetic Screening Test",
                "version_target": "Academic Suite v2",
                "INPUT": {
                    "data_path": "evals/reliability/data/synthetic_screener_data.json",
                    "format": "json",
                    "sample_n": 120
                },
                "EXPECTED_ANALYSIS": {
                    "model_type": "Synthetic Screening",
                    "methodology": "Automated deterministic scan",
                    "standard_applied": "Academic Suite v2",
                    "tool_script": ".agents/skills/synthetic-screener/scripts/run_synthetic_screening.py"
                },
                "EXPECTED_N": 120,
                "EXPECTED_VARIABLES": ["x1", "x2"],
                "EXPECTED_KEY_STATISTICS": {
                    "screening_verdict": {"value": "PASS"}
                },
                "EXPECTED_TABLES": [
                    {"table_number": 1, "title": "Screening Results", "columns": 3, "format": "APA 7"}
                ],
                "EXPECTED_INTERPRETATION_CONSTRAINTS": {
                    "language": "Persian (Farsi)",
                    "paragraph_structure": "5-Part Epistemic Formula",
                    "leading_zero_persian": True,
                    "table_placement": "narrative_above_table",
                    "zero_citations_in_results": True,
                    "zero_ai_cliches": True,
                    "effect_size_reporting": True
                },
                "EXPECTED_VALIDATION": {
                    "data_integrity": "PASS",
                    "numerical_consistency": "PASS",
                    "reporting_consistency": "PASS"
                }
            },
            "update_primary_manifest": False
        }

        manifest = create_specialist(custom_spec, target_root=self.temp_dir, run_sandbox=True)

        self.assertEqual(manifest["specialist_name"], "synthetic-screener")
        self.assertEqual(manifest["registration_status"], "CERTIFIED_AND_REGISTERED")
        self.assertEqual(manifest["preregistration_sandbox_test"]["overall_verdict"], "PASS")

        # Verify artifacts exist on disk in isolated sandbox
        self.assertTrue(os.path.exists(manifest["agent"]["file_path"]))
        self.assertTrue(os.path.exists(manifest["skill"]["skill_file"]))
        self.assertTrue(os.path.exists(manifest["skill"]["script_path"]))
        self.assertTrue(os.path.exists(manifest["validator"]["file_path"]))
        self.assertTrue(os.path.exists(manifest["evaluation_case"]))
        self.assertTrue(os.path.exists(manifest["data_fixture"]))

        specific_manifest = os.path.join(self.temp_dir, "factory", "synthetic-screener_manifest.json")
        self.assertTrue(os.path.exists(specific_manifest))


if __name__ == '__main__':
    unittest.main()
