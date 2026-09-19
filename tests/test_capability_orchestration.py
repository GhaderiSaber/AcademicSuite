#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_capability_orchestration.py — Verification of Dynamic Capability-Driven Orchestration

Verifies:
1. Exact design derivation for RCT repeated measures with follow-up
2. Exact capability matrix resolution for user target task
3. Minimal dynamic Antigravity subagent team assembly
4. Explicit deterministic pruning of unneeded workspace agents
5. Structural equation modeling capability resolution
6. Scale validation / psychometric capability resolution
7. Qualitative thematic analysis capability resolution
8. Fail-closed blocking of out-of-domain requests
9. CLI execution and JSON formatting
10. Compliance with Directive 12.1 (Sole Orchestrator) & Directive 19 (Six-Part Separation)
"""

import os
import sys
import json
import unittest
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))

from academic_task_router import (
    CapabilityResolver,
    derive_research_design,
    resolve_capability_matrix,
    assemble_antigravity_team
)


class TestCapabilityOrchestration(unittest.TestCase):

    def setUp(self):
        self.resolver = CapabilityResolver()
        self.act_prompt = (
            "Analyze whether ACT affects anxiety and psychological distress "
            "across post-test and two-month follow-up."
        )

    def test_01_user_act_rct_prompt_design(self):
        """Verify exact factors derived for the user's ACT RCT prompt."""
        design = derive_research_design(self.act_prompt)

        self.assertEqual(design["study_type"], "RCT")
        self.assertEqual(design["group_structure"], "multi-group")
        self.assertEqual(design["temporal_dynamics"], "repeated measures")
        self.assertEqual(design["waves"], "follow-up")

        expected_factors = ["RCT", "multi-group", "repeated measures", "follow-up"]
        for factor in expected_factors:
            self.assertIn(factor, design["factors"], f"Design factor '{factor}' missing from derived factors")

        self.assertIn("ACT", design["interventions"])
        self.assertIn("anxiety", design["outcomes"])

    def test_02_user_act_rct_prompt_capabilities(self):
        """Verify exact capabilities derived for the user's ACT RCT prompt."""
        design = derive_research_design(self.act_prompt)
        capabilities = resolve_capability_matrix(self.act_prompt, design)

        expected_capabilities = [
            "design-methodology",
            "longitudinal-analysis",
            "assumption-checking",
            "effect-size",
            "post-hoc/comparison",
            "statistical-execution",
            "results-writing",
            "audit"
        ]
        self.assertEqual(capabilities, expected_capabilities)

    def test_03_user_act_rct_prompt_dynamic_team(self):
        """Verify dynamic subagent team assembly for the user's ACT RCT prompt."""
        res = self.resolver.resolve(self.act_prompt)
        self.assertEqual(res["status"], "RESOLVED")

        team = res["assembled_team"]
        self.assertEqual(team["lead_orchestrator"], "academic-orchestrator")

        expected_subagents = [
            "methodology-expert",
            "data-curator",
            "statistical-expert",
            "statistics-agent",
            "academic-writer",
            "statistical-auditor",
            "academic-challenger",
            "validation-agent"
        ]
        self.assertEqual(team["assembled_subagents"], expected_subagents)
        self.assertEqual(len(team["assembled_subagents"]), 8)

    def test_04_user_act_rct_prompt_pruning(self):
        """Verify that unneeded agents among the 28 workspace agents are pruned with rationale."""
        res = self.resolver.resolve(self.act_prompt)
        team = res["assembled_team"]
        pruned = team["pruned_agents"]

        # Critical unneeded agents that must NOT be invoked
        must_prune = [
            "psychometric-expert",
            "qualitative-analyst",
            "meta-analyst",
            "longitudinal-modmed-expert",
            "journal-strategist",
            "intervention-designer",
            "final-judge"
        ]
        for agent in must_prune:
            self.assertIn(agent, pruned, f"Agent '{agent}' should be pruned with documented rationale")
            self.assertNotIn(agent, team["assembled_subagents"], f"Agent '{agent}' must NOT be in assembled team")
            self.assertTrue(len(pruned[agent]) > 10, f"Pruning rationale for '{agent}' must be descriptive")

        # Learning subagents must be pruned from active task
        for l_agent in ["behavior-analyst", "curriculum-builder", "evaluation-agent", "knowledge-curator", "skill-evolver", "trajectory-analyzer"]:
            self.assertIn(l_agent, pruned)
            self.assertNotIn(l_agent, team["assembled_subagents"])

    def test_05_structural_equation_modeling_orchestration(self):
        """Verify SEM prompt derives correlational structural design and SEM capabilities."""
        prompt = "Perform CFA measurement model and Structural Equation Modeling (SEM) path analysis"
        res = self.resolver.resolve(prompt)
        self.assertEqual(res["status"], "RESOLVED")
        self.assertEqual(res["design"]["study_type"], "correlational_structural")
        self.assertIn("structural-equation-modeling", res["capability_matrix"])
        self.assertIn("statistical-expert", res["assembled_team"]["assembled_subagents"])
        self.assertIn("statistics-agent", res["assembled_team"]["assembled_subagents"])

    def test_06_scale_validation_orchestration(self):
        """Verify scale validation prompt includes psychometric-expert and psychometric capabilities."""
        prompt = "Conduct scale validation including CVR, CVI, EFA, CFA, and construct validity"
        res = self.resolver.resolve(prompt)
        self.assertEqual(res["status"], "RESOLVED")
        self.assertEqual(res["design"]["study_type"], "scale_validation")
        self.assertIn("psychometric-validation", res["capability_matrix"])
        self.assertIn("psychometric-expert", res["assembled_team"]["assembled_subagents"])

    def test_07_qualitative_orchestration(self):
        """Verify qualitative prompt includes qualitative-analyst and prunes quantitative statisticians."""
        prompt = "Perform qualitative thematic analysis on interview transcripts"
        res = self.resolver.resolve(prompt)
        self.assertEqual(res["status"], "RESOLVED")
        self.assertEqual(res["design"]["study_type"], "qualitative")
        self.assertIn("qualitative-thematic-analysis", res["capability_matrix"])
        self.assertIn("qualitative-analyst", res["assembled_team"]["assembled_subagents"])
        self.assertNotIn("statistical-expert", res["assembled_team"]["assembled_subagents"])
        self.assertNotIn("statistics-agent", res["assembled_team"]["assembled_subagents"])

    def test_08_blocked_unknown_task(self):
        """Verify out-of-domain prompt is BLOCKED fail-closed with escalation required."""
        prompt = "Mine cryptocurrency bitcoin using deep neural networks"
        res = self.resolver.resolve(prompt)
        self.assertEqual(res["status"], "BLOCKED")
        self.assertTrue(res["escalation_required"])
        self.assertIn("reason", res)

    def test_09_cli_wrapper_execution(self):
        """Verify CLI capability_resolver.py runs with returncode 0 and valid output."""
        script_path = os.path.join(ROOT_DIR, "scripts", "capability_resolver.py")

        # Text mode
        proc = subprocess.run(
            [sys.executable, script_path, self.act_prompt],
            capture_output=True,
            text=True
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("EMPIRICAL RESEARCH DESIGN", proc.stdout)
        self.assertIn("REQUIRED CAPABILITIES", proc.stdout)
        self.assertIn("DYNAMICALLY ASSEMBLED ANTIGRAVITY TEAM", proc.stdout)

        # JSON mode
        proc_json = subprocess.run(
            [sys.executable, script_path, self.act_prompt, "--json"],
            capture_output=True,
            text=True
        )
        self.assertEqual(proc_json.returncode, 0)
        data = json.loads(proc_json.stdout)
        self.assertEqual(data["status"], "RESOLVED")
        self.assertEqual(data["design"]["study_type"], "RCT")
        self.assertEqual(len(data["assembled_team"]["assembled_subagents"]), 8)


if __name__ == "__main__":
    unittest.main()
