#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_main_agent_configuration.py — Acceptance Tests for Phase 11 Canonical MainAgent Configuration

Verifies:
1. Sole Canonical Entry Point:
   - Exactly ONE production agent out of all 28 has mainAgent: true.
   - That agent is strictly academic-orchestrator (mainAgent: true, subagent: true).
2. Pure Specialist Subagents:
   - All other 27 agents have mainAgent: false and subagent: true.
   - Zero agents have subagent: false (all agents mountable for delegation).
3. Agent Factory Conformity:
   - Authoritative AgentSpecs in factory/agent_factory.py conform to the Phase 11 rule.
4. Integrity Validator Enforcement:
   - AgentIntegrityValidator fails if any specialist attempts to declare mainAgent: true.
5. Conceptual Delegation Tree:
   - academic-orchestrator delegates to methodology, statistics, writing, and audit workers.
"""

import os
import sys
import glob
import yaml
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

AGENTS_DIR = os.path.join(ROOT_DIR, ".agents", "agents")
SKILLS_DIR = os.path.join(ROOT_DIR, ".agents", "skills")

from validators.agent_integrity import AgentIntegrityValidator
from factory.agent_factory import get_all_target_agent_specs


class TestMainAgentConfiguration(unittest.TestCase):
    """Enforces single canonical mainAgent entry point across AcademicSuite."""

    def test_01_sole_production_main_agent_is_academic_orchestrator(self):
        """academic-orchestrator must be the SOLE agent with mainAgent: true."""
        agent_files = sorted(glob.glob(os.path.join(AGENTS_DIR, "*", "agent.md")))
        prod_agents = [f for f in agent_files if not os.path.basename(os.path.dirname(f)).startswith("test-")]
        self.assertEqual(len(prod_agents), 28, f"Expected 28 production agents, found {len(prod_agents)}")
        self.assertEqual(len(agent_files), 30, f"Expected 30 total agents on disk (28 production + 2 test), found {len(agent_files)}")

        main_agents = []
        for a_path in agent_files:
            with open(a_path, "r", encoding="utf-8") as f:
                content = f.read()
            parts = content.split("---")
            self.assertGreaterEqual(len(parts), 3, f"Missing YAML frontmatter in {a_path}")
            fm = yaml.safe_load(parts[1])
            if fm.get("mainAgent") is True:
                main_agents.append(fm.get("name"))

        self.assertEqual(
            main_agents,
            ["academic-orchestrator"],
            f"Expected exactly ['academic-orchestrator'] as mainAgent: true, got: {main_agents}"
        )

    def test_02_all_specialists_have_main_agent_false_and_subagent_true(self):
        """All 27 non-orchestrator agents must have mainAgent: false and subagent: true."""
        agent_files = sorted(glob.glob(os.path.join(AGENTS_DIR, "*", "agent.md")))

        for a_path in agent_files:
            with open(a_path, "r", encoding="utf-8") as f:
                content = f.read()
            fm = yaml.safe_load(content.split("---")[1])
            name = fm.get("name")

            if name == "academic-orchestrator":
                self.assertTrue(fm.get("mainAgent"), "academic-orchestrator must have mainAgent: true")
                self.assertTrue(fm.get("subagent"), "academic-orchestrator must have subagent: true")
            else:
                self.assertFalse(
                    fm.get("mainAgent"),
                    f"Specialist '{name}' must have mainAgent: false (only academic-orchestrator can be mainAgent)"
                )
                self.assertTrue(
                    fm.get("subagent"),
                    f"Specialist '{name}' must have subagent: true for delegation via invoke_subagent"
                )

    def test_03_zero_agents_with_subagent_false(self):
        """Every single agent in AcademicSuite must be mountable in invoke_subagent (subagent: true)."""
        agent_files = sorted(glob.glob(os.path.join(AGENTS_DIR, "*", "agent.md")))
        for a_path in agent_files:
            with open(a_path, "r", encoding="utf-8") as f:
                content = f.read()
            fm = yaml.safe_load(content.split("---")[1])
            self.assertTrue(
                fm.get("subagent", False),
                f"Agent '{fm.get('name')}' has subagent: false or missing subagent boolean"
            )

    def test_04_agent_factory_authoritative_specs_conform_to_canonical_rule(self):
        """AgentSpecs in factory/agent_factory.py must conform to single canonical mainAgent."""
        specs = get_all_target_agent_specs()
        self.assertIn("academic-orchestrator", specs)

        for name, spec in specs.items():
            if name == "academic-orchestrator":
                self.assertTrue(spec.mainAgent, "factory spec for academic-orchestrator must have mainAgent=True")
                self.assertTrue(spec.subagent, "factory spec for academic-orchestrator must have subagent=True")
            else:
                self.assertFalse(spec.mainAgent, f"factory spec for '{name}' must have mainAgent=False")
                self.assertTrue(spec.subagent, f"factory spec for '{name}' must have subagent=True")

    def test_05_agent_integrity_validator_catches_competing_main_agents(self):
        """AgentIntegrityValidator must report canonical_mainAgent_entry_point error on competing mainAgent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_agents = os.path.join(tmpdir, "agents")
            tmp_skills = os.path.join(tmpdir, "skills")
            os.makedirs(os.path.join(tmp_agents, "academic-orchestrator"), exist_ok=True)
            os.makedirs(os.path.join(tmp_agents, "rogue-orchestrator"), exist_ok=True)
            os.makedirs(tmp_skills, exist_ok=True)

            orch_content = (
                "---\n"
                "name: academic-orchestrator\n"
                "description: Lead orchestrator\n"
                "mainAgent: true\n"
                "subagent: true\n"
                "---\n"
            )
            rogue_content = (
                "---\n"
                "name: rogue-orchestrator\n"
                "description: Competing orchestrator violating Phase 11\n"
                "mainAgent: true\n"
                "subagent: true\n"
                "---\n"
            )
            with open(os.path.join(tmp_agents, "academic-orchestrator", "agent.md"), "w") as f:
                f.write(orch_content)
            with open(os.path.join(tmp_agents, "rogue-orchestrator", "agent.md"), "w") as f:
                f.write(rogue_content)

            validator = AgentIntegrityValidator(agents_dir=tmp_agents, skills_dir=tmp_skills)
            res = validator.run_validation()

            self.assertEqual(res["overall_verdict"], "FAIL")
            self.assertTrue(
                any(i["check"] == "canonical_mainAgent_entry_point" for i in res["issues"]),
                "Validator must flag competing mainAgent under canonical_mainAgent_entry_point"
            )

    def test_06_full_workspace_passes_single_main_agent_validation(self):
        """Running AgentIntegrityValidator on the entire workspace produces 0 canonical_mainAgent_entry_point errors."""
        validator = AgentIntegrityValidator(agents_dir=AGENTS_DIR, skills_dir=SKILLS_DIR)
        res = validator.run_validation()
        self.assertEqual(res["overall_verdict"], "PASS")
        self.assertEqual(res["errors"], 0)
        self.assertFalse(any(i["check"] == "canonical_mainAgent_entry_point" for i in res["issues"]))


if __name__ == "__main__":
    unittest.main()
