#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_teamwork_patterns_phase34.py — Phase 34 Academic Domain Teamwork Patterns Test Suite

Tests:
1. Schema contract validation for all registered academic teamwork patterns.
2. Conceptual role coverage: Explorer, Worker, Critic, Challenger, Auditor, Success Auditor.
3. Handoff sequencing and input/output artifact continuity across stages.
4. Antigravity dispatch plan formatting for native invoke_subagent.
5. Integration with teamwork_boundary_adapter and complexity level routing.
6. Directive 12.1 compliance (prohibition of Python agent dispatch emulation).
7. Directive 6 (English-only ASCII filenames) and Directive 18 (single-view context budget).
"""

import os
import sys
import json
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.contract_validator import validate_teamwork_pattern, validate_contract
from scripts.academic_teamwork_patterns import AcademicTeamworkPatterns, CONCEPTUAL_ROLES
from scripts.teamwork_boundary_adapter import (
    build_teamwork_boundary_package,
    generate_boundary_manifest,
    resolve_teamwork_pattern_id
)


class TestTeamworkPatternsPhase34(unittest.TestCase):
    """Test suite for Phase 34 Academic Domain Teamwork Patterns."""

    @classmethod
    def setUpClass(cls):
        cls.engine = AcademicTeamworkPatterns()
        cls.patterns = cls.engine.list_patterns()

    def test_01_all_canonical_patterns_registered_and_schema_valid(self):
        """Verify all 5 canonical patterns exist and pass contract schema validation."""
        self.assertEqual(len(self.patterns), 5, f"Expected 5 patterns, found {len(self.patterns)}")
        expected_ids = {
            "ATP-METHODOLOGY-INFERENCE-001",
            "ATP-CHAPTER-4-001",
            "ATP-CHAPTER-5-001",
            "ATP-SCALE-VALIDATION-001",
            "ATP-PROPOSAL-001"
        }
        found_ids = {p["pattern_id"] for p in self.patterns}
        self.assertEqual(found_ids, expected_ids, f"Mismatch in pattern IDs: {expected_ids ^ found_ids}")

        val_res = self.engine.validate_all_patterns()
        self.assertEqual(val_res["verdict"], "PASS")
        self.assertEqual(val_res["failed"], 0)
        self.assertEqual(len(val_res["errors"]), 0)

        for pat in self.patterns:
            res = validate_teamwork_pattern(pat)
            self.assertTrue(res["valid"], f"Pattern {pat['pattern_id']} failed validation: {res.get('errors')}")

    def test_02_all_six_conceptual_roles_utilized(self):
        """Verify that all 6 conceptual roles are utilized and correctly mapped."""
        roles_found = set()
        for pat in self.patterns:
            for role in pat["conceptual_roles"]:
                roles_found.add(role)

        self.assertEqual(
            roles_found,
            set(CONCEPTUAL_ROLES),
            f"Missing conceptual roles across patterns: {set(CONCEPTUAL_ROLES) - roles_found}"
        )

        for pat in self.patterns:
            stages = pat["workflow_stages"]
            stage_roles = [s["conceptual_role"] for s in stages]
            for cr in CONCEPTUAL_ROLES:
                self.assertIn(cr, stage_roles, f"Pattern {pat['pattern_id']} missing conceptual role {cr}")

    def test_03_handoff_sequencing_and_artifact_continuity(self):
        """Verify sequential ordering, handoff contracts, and artifact continuity."""
        for pat in self.patterns:
            pid = pat["pattern_id"]
            stages = pat["workflow_stages"]
            self.assertGreaterEqual(len(stages), 6, f"Pattern {pid} should have at least 6 stages")

            accumulated_outputs = set()
            for idx, stage in enumerate(stages):
                self.assertTrue(stage["stage_id"].startswith("STG-"), f"Invalid stage_id in {pid}")
                self.assertIn("stage_name", stage)
                self.assertIn("domain_specialization", stage)
                self.assertIn("assigned_agent", stage)
                self.assertIn("required_skills", stage)
                self.assertGreater(len(stage["required_skills"]), 0, f"No skills in stage {stage['stage_id']}")

                # Input / Output artifacts
                self.assertGreater(len(stage["input_artifacts"]), 0, f"No inputs in {stage['stage_id']}")
                self.assertGreater(len(stage["output_artifacts"]), 0, f"No outputs in {stage['stage_id']}")
                self.assertIn("handoff_contract", stage)
                self.assertIn("exit_criteria", stage)
                self.assertGreater(len(stage["exit_criteria"]), 0)

                # Later stages should consume earlier outputs or external inputs
                if idx > 0:
                    common = set(stage["input_artifacts"]).intersection(accumulated_outputs)
                    self.assertGreater(
                        len(common),
                        0,
                        f"Stage {stage['stage_id']} in {pid} does not consume any previous outputs! "
                        f"Inputs: {stage['input_artifacts']}, Prior outputs: {accumulated_outputs}"
                    )

                for out in stage["output_artifacts"]:
                    accumulated_outputs.add(out)

    def test_04_antigravity_dispatch_plan_formatting(self):
        """Verify Antigravity invoke_subagent dispatch plan generation."""
        for pat in self.patterns:
            pid = pat["pattern_id"]
            plan = self.engine.format_antigravity_dispatch_plan(pid)
            self.assertEqual(plan["pattern_id"], pid)
            self.assertEqual(plan["orchestrator"], "Google Antigravity (Native invoke_subagent)")
            self.assertEqual(len(plan["subagent_sequence"]), len(pat["workflow_stages"]))

            for step in plan["subagent_sequence"]:
                self.assertIn("invoke_subagent_params", step)
                params = step["invoke_subagent_params"]
                self.assertIn("TypeName", params)
                self.assertIn("Role", params)
                self.assertIn("Prompt", params)
                self.assertEqual(params["Model"], "inherit")
                self.assertIn(params["Workspace"], ["inherit", "branch", "share"])
                self.assertIn(step["conceptual_role"], CONCEPTUAL_ROLES)

    def test_05_boundary_adapter_integration(self):
        """Verify seamless boundary package generation and pattern routing."""
        # L0 query: no pattern
        pkg_l0 = build_teamwork_boundary_package("What is the difference between mediator and moderator?")
        self.assertEqual(pkg_l0["complexity_level"], "L0")
        self.assertIsNone(pkg_l0["teamwork_runtime"]["academic_teamwork_pattern"])

        # L1 calculation: no pattern
        pkg_l1 = build_teamwork_boundary_package("Calculate Cronbach alpha for 10 items in dataset.csv")
        self.assertEqual(pkg_l1["complexity_level"], "L1")
        self.assertIsNone(pkg_l1["teamwork_runtime"]["academic_teamwork_pattern"])

        # L2 multi-analysis: inference pattern
        pkg_l2 = build_teamwork_boundary_package("Run ANOVA and hierarchical regression across groups")
        self.assertEqual(pkg_l2["complexity_level"], "L2")
        self.assertEqual(pkg_l2["teamwork_runtime"]["academic_teamwork_pattern"], "ATP-METHODOLOGY-INFERENCE-001")

        # L3 Chapter 4: Chapter 4 findings pattern
        pkg_l3_ch4 = build_teamwork_boundary_package("Execute Chapter 4 findings with SEM and mediation hypotheses")
        self.assertEqual(pkg_l3_ch4["complexity_level"], "L3")
        self.assertEqual(pkg_l3_ch4["teamwork_runtime"]["academic_teamwork_pattern"], "ATP-CHAPTER-4-001")

        # L3 Chapter 5: Chapter 5 discussion pattern
        pkg_l3_ch5 = build_teamwork_boundary_package("Draft Chapter 5 discussion synthesizing psychological mechanisms")
        self.assertEqual(pkg_l3_ch5["complexity_level"], "L3")
        self.assertEqual(pkg_l3_ch5["teamwork_runtime"]["academic_teamwork_pattern"], "ATP-CHAPTER-5-001")

        # L3 Scale Validation: Scale validation pattern
        pkg_l3_scale = build_teamwork_boundary_package("Perform psychometric scale validation with CVR/CVI and CFA")
        self.assertEqual(pkg_l3_scale["complexity_level"], "L3")
        self.assertEqual(pkg_l3_scale["teamwork_runtime"]["academic_teamwork_pattern"], "ATP-SCALE-VALIDATION-001")

        # L3 Proposal: Proposal pattern
        pkg_l3_prop = build_teamwork_boundary_package("Draft dissertation proposal with G*Power and hypotheses")
        self.assertEqual(pkg_l3_prop["complexity_level"], "L3")
        self.assertEqual(pkg_l3_prop["teamwork_runtime"]["academic_teamwork_pattern"], "ATP-PROPOSAL-001")

        # Test alias generate_boundary_manifest
        manifest = generate_boundary_manifest("Execute Chapter 4 findings with SEM and mediation hypotheses")
        self.assertEqual(manifest["task_id"], pkg_l3_ch4["task_id"])
        self.assertEqual(manifest["complexity_level"], "L3")
        self.assertEqual(manifest["teamwork_runtime"]["academic_teamwork_pattern"], "ATP-CHAPTER-4-001")

        # Verify all generated packages pass schema validation
        for p in [pkg_l0, pkg_l1, pkg_l2, pkg_l3_ch4, pkg_l3_ch5, pkg_l3_scale, pkg_l3_prop, manifest]:
            res = validate_contract(p, "teamwork_boundary")
            self.assertTrue(res["valid"], f"Boundary package validation failed: {res.get('errors')}")

    def test_06_directive_12_1_no_python_agent_dispatch_emulation(self):
        """Verify strict compliance with Directive 12.1 (no Python agent dispatch emulators)."""
        cand = os.path.join(ROOT_DIR, ".agents", "scripts", "academic_teamwork_patterns.py")
        script_path = cand if os.path.isfile(cand) else os.path.join(ROOT_DIR, "scripts", "academic_teamwork_patterns.py")
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for forbidden concurrency/dispatch emulation patterns
        forbidden_tokens = [
            "threading.Thread",
            "multiprocessing.Process",
            "concurrent.futures",
            "asyncio.create_task",
            "class AgentDispatcher",
            "class SubagentExecutor",
            "def dispatch_agent",
            "def run_subagent"
        ]
        for token in forbidden_tokens:
            self.assertNotIn(
                token,
                content,
                f"Forbidden Python dispatch emulation token '{token}' found in {script_path}"
            )

    def test_07_governance_directives_compliance(self):
        """Verify Directive 6 (English ASCII filenames) and Directive 18 (single-view context budget)."""
        # Directive 6: evals/teamwork/ and contracts/ filenames must be ASCII only
        for dir_path in [os.path.join(ROOT_DIR, "evals", "teamwork"), os.path.join(ROOT_DIR, "contracts")]:
            if os.path.isdir(dir_path):
                for fname in os.listdir(dir_path):
                    self.assertTrue(
                        fname.isascii(),
                        f"Non-ASCII filename violates Directive 6: {fname}"
                    )

        cand = os.path.join(ROOT_DIR, ".agents", "scripts", "academic_teamwork_patterns.py")
        script_path = cand if os.path.isfile(cand) else os.path.join(ROOT_DIR, "scripts", "academic_teamwork_patterns.py")
        with open(script_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.assertLessEqual(
            len(lines),
            500,
            f"scripts/academic_teamwork_patterns.py ({len(lines)} lines) exceeds 500-line limit (Directive 18)"
        )


if __name__ == "__main__":
    unittest.main()
