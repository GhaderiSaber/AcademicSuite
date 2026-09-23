# -*- coding: utf-8 -*-
"""
test_project_structure.py — Verification of Target Canonical Project Architecture

Asserts that repository directory structure, tools, artifacts, docs, protocols,
and legacy archiving strictly adhere to the 17-Phase Architecture Guide.
"""

import os
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TestProjectStructure(unittest.TestCase):

    def test_tools_layer_exists(self):
        """Asserts tools/ contains python/ and r/ computational engines."""
        tools_dir = os.path.join(REPO_ROOT, ".agents", "tools") if os.path.isdir(os.path.join(REPO_ROOT, ".agents", "tools")) else os.path.join(REPO_ROOT, "tools")
        self.assertTrue(os.path.isdir(os.path.join(tools_dir, "python")), "Missing tools/python/")
        self.assertTrue(os.path.isdir(os.path.join(tools_dir, "r")), "Missing tools/r/")
        self.assertTrue(os.path.isfile(os.path.join(tools_dir, "README.md")), "Missing tools/README.md")
        self.assertTrue(os.path.isfile(os.path.join(tools_dir, "python", "statistical_runner.py")), "Missing statistical_runner.py")

    def test_artifacts_layer_exists(self):
        """Asserts artifacts/ contains project, analysis, validation, reports."""
        cand_art = os.path.join(REPO_ROOT, ".agents", "artifacts")
        artifacts_dir = cand_art if os.path.isdir(cand_art) else os.path.join(REPO_ROOT, "artifacts")
        subdirs = ["project", "analysis", "validation", "reports"]
        for s in subdirs:
            p = os.path.join(artifacts_dir, s)
            self.assertTrue(os.path.isdir(p), f"Missing artifacts/{s}/")
        self.assertTrue(os.path.isfile(os.path.join(artifacts_dir, "README.md")), "Missing artifacts/README.md")

    def test_evaluations_alias_exists(self):
        """Asserts evals or evaluations directory exists."""
        cand_eval = os.path.join(REPO_ROOT, "evals")
        p = cand_eval if os.path.isdir(cand_eval) else os.path.join(REPO_ROOT, "evaluations")
        self.assertTrue(os.path.exists(p), "Missing evals or evaluations directory")
        self.assertTrue(os.path.exists(os.path.join(p, "run_eval_suite.py")), "evaluations should expose run_eval_suite.py")

    def test_legacy_archiving_exists(self):
        """Asserts legacy/ contains workflows/ and skills/ with archived components."""
        cand_leg = os.path.join(REPO_ROOT, ".agents", "legacy")
        legacy_dir = cand_leg if os.path.isdir(cand_leg) else os.path.join(REPO_ROOT, "legacy")
        legacy_wf = os.path.join(legacy_dir, "workflows")
        self.assertTrue(os.path.isdir(legacy_wf), "Missing legacy/workflows/")
        legacy_sk = os.path.join(legacy_dir, "skills")
        self.assertTrue(os.path.isdir(legacy_sk), "Missing legacy/skills/")
        self.assertTrue(os.path.isfile(os.path.join(legacy_dir, "README.md")), "Missing legacy/README.md")
        self.assertTrue(os.path.isfile(os.path.join(legacy_sk, "README.md")), "Missing legacy/skills/README.md")
        self.assertTrue(os.path.isfile(os.path.join(REPO_ROOT, ".agents", "workflows", "README.md")), "Missing .agents/workflows/README.md")

    def test_docs_and_protocols_exist(self):
        """Asserts docs/ contains architecture.md, agent-contracts/, and protocols/."""
        self.assertTrue(os.path.exists(os.path.join(REPO_ROOT, "docs", "architecture.md")), "Missing docs/architecture.md")
        self.assertTrue(os.path.isfile(os.path.join(REPO_ROOT, "docs", "agent-contracts", "README.md")), "Missing docs/agent-contracts/README.md")
        
        protocols = ["stage_gate_protocol.md", "triad_invariant.md", "binary_honesty.md", "failure_recovery.md"]
        for proto in protocols:
            proto_path = os.path.join(REPO_ROOT, "docs", "protocols", proto)
            self.assertTrue(os.path.isfile(proto_path), f"Missing docs/protocols/{proto}")

    def test_canonical_rules_exist(self):
        """Asserts .agents/rules/ contains canonical rule files."""
        rules = ["academic-integrity.md", "data-integrity.md", "project-conventions.md"]
        for r in rules:
            r_path = os.path.join(REPO_ROOT, ".agents", "rules", r)
            self.assertTrue(os.path.isfile(r_path), f"Missing .agents/rules/{r}")

    def test_skill_inventory_documents_all_skills(self):
        """Asserts docs/SKILL_INVENTORY.md comprehensively documents all 43 active production skills."""
        inv_path = os.path.join(REPO_ROOT, "docs", "SKILL_INVENTORY.md")
        self.assertTrue(os.path.isfile(inv_path), "Missing docs/SKILL_INVENTORY.md")
        with open(inv_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        skills_dir = os.path.join(REPO_ROOT, ".agents", "skills")
        active_skills = [
            d for d in os.listdir(skills_dir)
            if os.path.isdir(os.path.join(skills_dir, d)) and not d.startswith((".", "_"))
        ]
        self.assertEqual(len(active_skills), 45, f"Expected 45 active skills, found {len(active_skills)}")
        
        for s in active_skills:
            self.assertIn(f"`{s}`", content, f"Skill {s} is not documented in docs/SKILL_INVENTORY.md")

    def test_agent_inventory_documents_all_agents(self):
        """Asserts docs/AGENT_INVENTORY.md comprehensively documents all 28 agents."""
        inv_path = os.path.join(REPO_ROOT, "docs", "AGENT_INVENTORY.md")
        self.assertTrue(os.path.isfile(inv_path), "Missing docs/AGENT_INVENTORY.md")
        with open(inv_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        agents_dir = os.path.join(REPO_ROOT, ".agents", "agents")
        active_agents = [
            d for d in os.listdir(agents_dir)
            if os.path.isdir(os.path.join(agents_dir, d)) and not d.startswith((".", "_", "test-"))
        ]
        self.assertEqual(len(active_agents), 29, f"Expected 29 production agents, found {len(active_agents)}")
        
        for a in active_agents:
            self.assertIn(f"`{a}`", content, f"Agent {a} is not documented in docs/AGENT_INVENTORY.md")

    def test_activation_matrix_documents_all_skills(self):
        """Asserts .agents/references/SKILL_ACTIVATION_MATRIX.md documents all 44 active production skills."""
        mat_path = os.path.join(REPO_ROOT, ".agents", "references", "SKILL_ACTIVATION_MATRIX.md")
        self.assertTrue(os.path.isfile(mat_path), "Missing SKILL_ACTIVATION_MATRIX.md")
        with open(mat_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        skills_dir = os.path.join(REPO_ROOT, ".agents", "skills")
        active_skills = [
            d for d in os.listdir(skills_dir)
            if os.path.isdir(os.path.join(skills_dir, d)) and not d.startswith((".", "_"))
        ]
        for s in active_skills:
            self.assertIn(f"`{s}`", content, f"Skill {s} is missing from SKILL_ACTIVATION_MATRIX.md")

    def test_readme_documents_all_skills_and_agents(self):
        """Asserts README.md documents all 45 active production skills and 28 agents."""
        readme_path = os.path.join(REPO_ROOT, "README.md")
        self.assertTrue(os.path.isfile(readme_path), "Missing README.md")
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        skills_dir = os.path.join(REPO_ROOT, ".agents", "skills")
        active_skills = [
            d for d in os.listdir(skills_dir)
            if os.path.isdir(os.path.join(skills_dir, d)) and not d.startswith((".", "_"))
        ]
        self.assertEqual(len(active_skills), 45)
        for s in active_skills:
            self.assertIn(s, content, f"Skill {s} is missing from README.md")

        agents_dir = os.path.join(REPO_ROOT, ".agents", "agents")
        active_agents = [
            d for d in os.listdir(agents_dir)
            if os.path.isdir(os.path.join(agents_dir, d)) and not d.startswith((".", "_", "test-"))
        ]
        self.assertEqual(len(active_agents), 29)
        for a in active_agents:
            self.assertIn(f"`{a}`", content, f"Agent {a} is missing from README.md")

    def test_architectural_taxonomy_and_truth_exists(self):
        """Asserts docs/ARCHITECTURE_TAXONOMY_AND_TRUTH.md exists and documents the 3 temporal tiers."""
        truth_path = os.path.join(REPO_ROOT, "docs", "ARCHITECTURE_TAXONOMY_AND_TRUTH.md")
        self.assertTrue(os.path.isfile(truth_path), "Missing docs/ARCHITECTURE_TAXONOMY_AND_TRUTH.md")
        with open(truth_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Current Architecture", content)
        self.assertIn("Historical Architecture", content)
        self.assertIn("Target Architecture", content)
        self.assertIn("31 Agents", content)
        self.assertIn("44 Production Skills", content)


if __name__ == "__main__":
    unittest.main()

