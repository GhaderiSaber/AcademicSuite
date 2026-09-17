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
from factory.meta_factory import run_preregistration_sandbox_test


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
        val_path = os.path.join(ROOT_DIR, "validators", "longitudinal_modmed", "validator.py")
        eval_path = os.path.join(ROOT_DIR, "evals", "mediation", "case_longitudinal_modmed_01.json")
        manifest_path = os.path.join(ROOT_DIR, "factory", "specialist_manifest.json")

        self.assertTrue(os.path.exists(agent_path), f"Missing agent: {agent_path}")
        self.assertTrue(os.path.exists(skill_path), f"Missing skill: {skill_path}")
        self.assertTrue(os.path.exists(val_path), f"Missing validator: {val_path}")
        self.assertTrue(os.path.exists(eval_path), f"Missing eval case: {eval_path}")
        self.assertTrue(os.path.exists(manifest_path), f"Missing manifest: {manifest_path}")

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        self.assertEqual(manifest["registration_status"], "CERTIFIED_AND_REGISTERED")
        self.assertEqual(manifest["preregistration_sandbox_test"]["overall_verdict"], "PASS")


if __name__ == '__main__':
    unittest.main()
