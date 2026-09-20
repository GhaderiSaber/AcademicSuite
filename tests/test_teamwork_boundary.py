#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_teamwork_boundary.py — Unit Tests for AcademicSuite & Antigravity Teamwork Boundary Integration

Verifies:
1. Graduated complexity classification across L0, L1, L2, L3, and L4.
2. Quantitative scope triggers (chapter_count, file_count).
3. Dynamic Teamwork abstract role mapping (Explorer, Worker, Critic, Challenger, Auditor, Success Auditor).
4. Zero hard-coded worker counts (dynamic sizing).
5. Schema validation of generated boundary manifests against contracts/teamwork_boundary.schema.json.
6. Authoritative ownership boundary invariants (AcademicSuite governance vs. Teamwork runtime).
7. Integration with Capability Resolver and CLI execution.
"""

import os
import sys
import json
import unittest
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, "contracts"))

import teamwork_boundary_adapter as tba
from contract_validator import validate_contract
from academic_task_router import CapabilityResolver, _GLOBAL_REGISTRY


class TestTeamworkBoundaryIntegration(unittest.TestCase):

    def setUp(self):
        self.resolver = CapabilityResolver(_GLOBAL_REGISTRY)

    def test_01_complexity_classification_l0_to_l4(self):
        """Validates correct classification across all 5 graduated complexity levels."""
        # L0: Simple Question / Informational Query
        l0_queries = [
            "What is the APA 7 rule for reporting p-values?",
            "Explain the difference between mediation and moderation",
            "Define convergent validity and HTMT cutoff"
        ]
        for q in l0_queries:
            meta = tba.classify_complexity(q)
            self.assertEqual(meta["complexity_level"], "L0", f"Failed on: {q}")
            self.assertEqual(meta["team_formation_mode"], "none")
            self.assertFalse(meta["analysis_plan_required"])
            self.assertFalse(meta["isolated_workspaces"])

        # L1: Single Bounded Analysis
        l1_queries = [
            "Compute sample descriptive statistics and frequency tables for 120 nurses",
            "Calculate Cronbach's alpha and McDonald's omega for Burnout Inventory",
            "Run Shapiro-Wilk normality test on depression scores"
        ]
        for q in l1_queries:
            meta = tba.classify_complexity(q)
            self.assertEqual(meta["complexity_level"], "L1", f"Failed on: {q}")
            self.assertEqual(meta["team_formation_mode"], "bounded_single")
            self.assertTrue(meta["analysis_plan_required"])
            self.assertFalse(meta["isolated_workspaces"])

        # L2: Multi-Analysis Project
        l2_queries = [
            "Perform ANCOVA with Levene assumption test and bootstrap mediation",
            "Run CFA and SEM on latent burnout model with 5000 bootstrap resamples",
            "Execute multiple regression and check collinearity VIF with assumption testing"
        ]
        for q in l2_queries:
            meta = tba.classify_complexity(q)
            self.assertEqual(meta["complexity_level"], "L2", f"Failed on: {q}")
            self.assertEqual(meta["team_formation_mode"], "sequential_audited")
            self.assertTrue(meta["analysis_plan_required"])
            self.assertFalse(meta["isolated_workspaces"])

        # L3: Thesis/Paper Milestone
        l3_queries = [
            "Draft full Chapter 4 findings for thesis with 3 hypotheses and triad artifacts",
            "Conduct comprehensive Scale Validation study with EFA, CFA, and IRT",
            "Compile PRISMA 2020 systematic review and meta-analysis package"
        ]
        for q in l3_queries:
            meta = tba.classify_complexity(q)
            self.assertEqual(meta["complexity_level"], "L3", f"Failed on: {q}")
            self.assertEqual(meta["team_formation_mode"], "full_milestone_pipeline")
            self.assertTrue(meta["analysis_plan_required"])
            self.assertTrue(meta["human_approval_required"])

        # L4: Full Research Project / Native Teamwork
        l4_queries = [
            "Restructure 20-chapter monograph with thousands of source files",
            "Repository-wide full thesis overhaul across five dissertation volumes",
            "Multi-study repository migration and longitudinal multi-wave overhaul"
        ]
        for q in l4_queries:
            meta = tba.classify_complexity(q)
            self.assertEqual(meta["complexity_level"], "L4", f"Failed on: {q}")
            self.assertEqual(meta["team_formation_mode"], "dynamic_teamwork")
            self.assertTrue(meta["isolated_workspaces"])
            self.assertEqual(meta["recommended_slash_command"], "/teamwork-preview")
            self.assertTrue(meta["human_approval_required"])

    def test_02_quantitative_scope_triggers(self):
        """Validates that numerical chapter and file count triggers promote tasks to L3/L4."""
        # 20 chapters -> L4
        meta_ch = tba.classify_complexity("Review findings", chapter_count=20)
        self.assertEqual(meta_ch["complexity_level"], "L4")
        self.assertTrue(meta_ch["isolated_workspaces"])

        # 120 files -> L4
        meta_fc = tba.classify_complexity("Check data variables", file_count=120)
        self.assertEqual(meta_fc["complexity_level"], "L4")

        # 3 chapters -> L3
        meta_ch3 = tba.classify_complexity("Draft empirical sections", chapter_count=3)
        self.assertEqual(meta_ch3["complexity_level"], "L3")

        # 20 files -> L3
        meta_fc20 = tba.classify_complexity("Organize project files", file_count=20)
        self.assertEqual(meta_fc20["complexity_level"], "L3")

    def test_03_teamwork_role_roster_mapping(self):
        """Verifies abstract Teamwork roles map accurately to AcademicSuite cognitive specializations."""
        # L0: Empty roster
        r_l0 = tba.map_teamwork_roles("L0")
        self.assertEqual(len(r_l0), 0)

        # L1: Exactly 1 bounded Worker
        r_l1 = tba.map_teamwork_roles("L1")
        self.assertEqual(len(r_l1), 1)
        self.assertEqual(r_l1[0]["teamwork_role"], "Worker")
        self.assertEqual(r_l1[0]["workspace_mode"], "inherit")

        # L2: Explorer + Worker + Challenger + Auditor
        r_l2 = tba.map_teamwork_roles("L2", capabilities=[{
            "capability_id": "ancova",
            "execution_worker": "statistics-agent",
            "reviewer": "validation-agent",
            "challenger": "academic-challenger",
            "required_skills": ["statistical-data-analyst", "assumption-testing"]
        }])
        roles_l2 = [item["teamwork_role"] for item in r_l2]
        self.assertIn("Worker", roles_l2)
        self.assertIn("Challenger", roles_l2)
        self.assertIn("Auditor", roles_l2)

        # L4: Full suite with isolated workspace ('branch')
        r_l4 = tba.map_teamwork_roles("L4", capabilities=[
            {
                "capability_id": "sem",
                "execution_worker": "statistics-agent",
                "reviewer": "validation-agent",
                "challenger": "academic-challenger",
                "required_skills": ["sem", "cfa"]
            }
        ])
        roles_l4 = [item["teamwork_role"] for item in r_l4]
        self.assertIn("Explorer", roles_l4)
        self.assertIn("Worker", roles_l4)
        self.assertIn("Critic", roles_l4)
        self.assertIn("Challenger", roles_l4)
        self.assertIn("Auditor", roles_l4)
        self.assertIn("Success Auditor", roles_l4)
        for agent_spec in r_l4:
            self.assertEqual(agent_spec["workspace_mode"], "branch")

    def test_04_dynamic_sizing_no_hardcoded_worker_counts(self):
        """Confirms that worker count scales dynamically with resolved capabilities."""
        # Single capability -> 1 execution worker in Worker role
        caps_single = [{"capability_id": "ancova", "execution_worker": "statistics-agent", "required_skills": ["statistical-data-analyst"]}]
        roster_single = tba.map_teamwork_roles("L2", capabilities=caps_single)
        workers_single = [m for m in roster_single if m["teamwork_role"] == "Worker"]
        self.assertEqual(len(workers_single), 1)

        # Multiple capabilities with distinct workers -> dynamically scales
        caps_multi = [
            {"capability_id": "ancova", "execution_worker": "statistics-agent", "required_skills": ["statistical-data-analyst"]},
            {"capability_id": "thesis_chapter4", "execution_worker": "academic-writer", "required_skills": ["chapter-4-writing"]}
        ]
        roster_multi = tba.map_teamwork_roles("L3", capabilities=caps_multi)
        workers_multi = [m for m in roster_multi if m["teamwork_role"] == "Worker"]
        self.assertEqual(len(workers_multi), 2)
        worker_agents = [w["academicsuite_agent"] for w in workers_multi]
        self.assertIn("statistics-agent", worker_agents)
        self.assertIn("academic-writer", worker_agents)

    def test_05_boundary_package_schema_validation(self):
        """Verifies generated boundary packages pass validation against contracts/teamwork_boundary.schema.json."""
        tasks = [
            ("L1 Task", "Compute descriptives on dataset", 1, 1),
            ("L2 Task", "Run ANCOVA with Levene test and mediation", 1, 2),
            ("L3 Task", "Draft full Chapter 4 findings with triad artifacts", 1, 5),
            ("L4 Task", "Restructure 20-chapter monograph with thousands of source files", 20, 100)
        ]
        for label, desc, ch_cnt, f_cnt in tasks:
            pkg = tba.build_teamwork_boundary_package(
                task_description=desc,
                chapter_count=ch_cnt,
                file_count=f_cnt
            )
            report = validate_contract(pkg, "teamwork_boundary")
            self.assertTrue(report.get("valid", False), f"Schema validation failed for {label}: {report.get('errors')}")
            self.assertEqual(report.get("verdict"), "PASS")

    def test_06_authoritative_ownership_boundary_invariants(self):
        """Verifies strict separation: AcademicSuite owns domain governance, Teamwork owns runtime."""
        pkg = tba.build_teamwork_boundary_package(
            task_description="Restructure 20-chapter monograph with thousands of source files",
            chapter_count=20,
            file_count=150
        )
        # AcademicSuite Governance Checks
        gov = pkg["governance"]
        self.assertIn("analysis_plan", gov["research_contracts"])
        self.assertIn("execution_manifest", gov["research_contracts"])
        self.assertTrue(gov["analysis_plan_required"])
        self.assertTrue(gov["provenance_required"])
        self.assertEqual(gov["statistical_execution_contract"], "deterministic_hands_only")
        self.assertTrue(gov["human_approval_required"])
        self.assertTrue(any("MSAI" in c for c in gov["academic_acceptance_criteria"]))

        # Antigravity Teamwork Runtime Checks
        rt = pkg["teamwork_runtime"]
        self.assertEqual(rt["team_formation_mode"], "dynamic_teamwork")
        self.assertTrue(rt["isolated_workspaces"])
        self.assertEqual(rt["recommended_slash_command"], "/teamwork-preview")
        self.assertIsNone(rt["max_concurrent_workers"])  # Runtime manages concurrency dynamically

    def test_07_capability_resolver_integration(self):
        """Verifies that CapabilityResolver seamlessly attaches complexity_level and teamwork_boundary."""
        res = self.resolver.resolve("Run ANCOVA on 60 ICU nurses to test hypothesis 1")
        self.assertEqual(res["status"], "RESOLVED")
        self.assertIn("complexity_level", res)
        self.assertIn(res["complexity_level"], ["L1", "L2", "L3"])
        self.assertIn("teamwork_boundary", res)
        boundary = res["teamwork_boundary"]
        self.assertEqual(boundary["boundary_version"], "1.0.0")
        self.assertIn("governance", boundary)
        self.assertIn("teamwork_runtime", boundary)

    def test_08_cli_classify_and_package(self):
        """Verifies CLI commands for teamwork_boundary_adapter.py execute without errors."""
        cand = os.path.join(ROOT_DIR, ".agents", "scripts", "teamwork_boundary_adapter.py")
        adapter_script = cand if os.path.isfile(cand) else os.path.join(ROOT_DIR, "scripts", "teamwork_boundary_adapter.py")
        # Classify CLI
        cmd_classify = [
            sys.executable,
            adapter_script,
            "classify",
            "--description", "Restructure 20-chapter monograph with thousands of source files"
        ]
        out_c = subprocess.check_output(cmd_classify, text=True)
        data_c = json.loads(out_c)
        self.assertEqual(data_c["complexity_level"], "L4")

        # Package CLI
        cmd_pkg = [
            sys.executable,
            adapter_script,
            "package",
            "--description", "Run CFA and SEM on latent burnout model"
        ]
        out_p = subprocess.check_output(cmd_pkg, text=True)
        data_p = json.loads(out_p)
        self.assertEqual(data_p["complexity_level"], "L2")
        self.assertIn("governance", data_p)


if __name__ == "__main__":
    unittest.main()
