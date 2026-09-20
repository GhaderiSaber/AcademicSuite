#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_capability_resolver.py — Unit tests for AcademicSuite Capability Resolver

Verifies:
1. Known capability resolution (ANCOVA, Mediation, LMM, etc.)
2. Multiple capability composite resolution (CFA + SEM, Literature + Meta-Analysis)
3. Ambiguous capability detection and candidate suggestion
4. Unknown / out-of-domain capability blocking (fail-closed, no silent misrouting)
5. Topological capability dependency resolution (e.g. thesis_chapter4 -> data_cleaning -> assumptions)
6. Reviewer assignment across domains
7. Challenger assignment across domains
8. Dynamic subagent worker scaling (no hard-coded counts, unneeded agents pruned)
9. Authoritative registry validity (config/capabilities.yaml)
10. Backwards compatibility preservation with legacy build_pipeline interface
"""

import os
import sys
import json
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))

from academic_task_router import (
    CapabilityResolver,
    CapabilityRegistry,
    build_pipeline,
    detect_capabilities
)


class TestCapabilityResolver(unittest.TestCase):

    def setUp(self):
        self.registry = CapabilityRegistry()
        self.resolver = CapabilityResolver(self.registry)

    def test_01_registry_integrity(self):
        """Verify that config/capabilities.yaml loads with all required schema fields."""
        caps = self.registry.all_capabilities()
        self.assertGreaterEqual(len(caps), 15, "Capability registry must contain at least 15 capabilities")

        required_keys = [
            "id", "domain", "description", "required_skills", "primary_agent",
            "execution_worker", "reviewer", "challenger", "required_artifacts",
            "output_artifacts", "validation_requirements", "dependencies"
        ]
        for cap_id, meta in caps.items():
            for key in required_keys:
                self.assertIn(key, meta, f"Capability '{cap_id}' missing mandatory key '{key}'")
            self.assertEqual(meta["id"], cap_id)
            self.assertIsInstance(meta["required_skills"], list)
            self.assertIsInstance(meta["dependencies"], list)

    def test_02_known_single_capability(self):
        """Verify single known capability resolves to correct agent, worker, and skills."""
        # ANCOVA
        res = self.resolver.resolve("Execute ANCOVA with baseline covariate adjustment")
        self.assertEqual(res["status"], "RESOLVED")
        self.assertIn("ancova", res["required_capabilities"])
        self.assertEqual(res["durable_agent"], "statistics-agent")
        self.assertIn("data-curator", res["required_subagents"]["execution_workers"])
        self.assertIn("statistical-expert", res["required_subagents"]["execution_workers"])
        self.assertIn("statistical-data-analyst", res["required_skills"])
        self.assertIn("assumption-testing", res["required_skills"])

        # Mediation
        res_med = self.resolver.resolve("Run Preacher & Hayes bootstrap mediation with 5000 resamples")
        self.assertEqual(res_med["status"], "RESOLVED")
        self.assertIn("mediation", res_med["required_capabilities"])
        self.assertIn("mediation", res_med["required_skills"])

        # Linear Mixed Model
        res_lmm = self.resolver.resolve("Fit a linear mixed model with random intercepts and slopes")
        self.assertEqual(res_lmm["status"], "RESOLVED")
        self.assertIn("linear_mixed_model", res_lmm["required_capabilities"])
        self.assertIn("longitudinal-modmed-expert", res_lmm["required_subagents"]["execution_workers"])

    def test_03_multiple_capabilities(self):
        """Verify composite tasks resolve all required capabilities without omission."""
        prompt = "Perform CFA measurement model and Structural Equation Modeling (SEM) path analysis"
        res = self.resolver.resolve(prompt)
        self.assertEqual(res["status"], "RESOLVED")
        self.assertIn("cfa", res["required_capabilities"])
        self.assertIn("sem", res["required_capabilities"])

        # Verify topological ordering: CFA must precede SEM
        topo = res["topological_capability_order"]
        self.assertIn("data_cleaning", topo)
        self.assertIn("cfa", topo)
        self.assertIn("sem", topo)
        self.assertLess(topo.index("cfa"), topo.index("sem"), "CFA must precede SEM in execution order")

    def test_04_ambiguous_capability(self):
        """Verify ambiguous tasks return AMBIGUOUS with candidate options and clarification."""
        # Ambiguous regression
        res_reg = self.resolver.resolve("Run regression")
        self.assertEqual(res_reg["status"], "AMBIGUOUS")
        self.assertIn("candidate_capabilities", res_reg)
        self.assertIn("regression", res_reg["candidate_capabilities"])
        self.assertIn("clarification_prompt", res_reg)

        # Ambiguous modeling
        res_mod = self.resolver.resolve("Perform advanced modeling")
        self.assertEqual(res_mod["status"], "AMBIGUOUS")
        self.assertIn("candidate_capabilities", res_mod)
        self.assertTrue(len(res_mod["candidate_capabilities"]) >= 2)

    def test_05_unknown_capability_blocked(self):
        """Verify unknown/out-of-domain requests are BLOCKED, not silently routed to an unrelated agent."""
        unknown_prompts = [
            "Predict cryptocurrency bitcoin prices with quantum deep learning",
            "Perform genetic DNA alignment and genome sequencing",
            "Write a weather forecasting bot for tomorrow's rain",
            "Execute an unsupported quantum neural network optimization"
        ]
        for p in unknown_prompts:
            res = self.resolver.resolve(p)
            self.assertEqual(
                res["status"], "BLOCKED",
                f"Unknown task was not BLOCKED: '{p}' (got status: {res.get('status')})"
            )
            self.assertTrue(res.get("escalation_required", False))
            self.assertIn("reason", res)
            self.assertEqual(res["required_capabilities"], [])

    def test_06_capability_dependency_resolution(self):
        """Verify that capability prerequisites are recursively resolved and topologically ordered."""
        # thesis_chapter4 depends on data_cleaning, descriptive_statistics, assumption_testing
        res = self.resolver.resolve("Draft Chapter 4 findings with results tables")
        self.assertEqual(res["status"], "RESOLVED")
        self.assertIn("thesis_chapter4", res["required_capabilities"])

        topo = res["topological_capability_order"]
        self.assertIn("data_cleaning", topo)
        self.assertIn("descriptive_statistics", topo)
        self.assertIn("assumption_testing", topo)
        self.assertIn("thesis_chapter4", topo)

        # Ensure prerequisites precede the final deliverable
        self.assertLess(topo.index("data_cleaning"), topo.index("thesis_chapter4"))
        self.assertLess(topo.index("descriptive_statistics"), topo.index("thesis_chapter4"))
        self.assertLess(topo.index("assumption_testing"), topo.index("thesis_chapter4"))

    def test_07_reviewer_assignment(self):
        """Verify each resolved capability assigns its designated auditor/reviewer."""
        # Statistics tasks must assign statistical-auditor
        res_stat = self.resolver.resolve("Execute ANCOVA")
        self.assertIn("statistical-auditor", res_stat["required_subagents"]["reviewers"])

        # Writing tasks must assign results-auditor
        res_write = self.resolver.resolve("Draft Chapter 4 findings")
        self.assertIn("results-auditor", res_write["required_subagents"]["reviewers"])

        # Qualitative tasks must assign evidence-auditor
        res_qual = self.resolver.resolve("Perform qualitative thematic analysis on interview transcripts")
        self.assertIn("evidence-auditor", res_qual["required_subagents"]["reviewers"])

    def test_08_challenger_assignment(self):
        """Verify each resolved capability assigns its designated challenger."""
        res = self.resolver.resolve("Execute ANCOVA with baseline covariate adjustment")
        self.assertIn("academic-challenger", res["required_subagents"]["challengers"])

    def test_09_no_hardcoded_worker_counts(self):
        """Verify worker count scales strictly according to the scope of the task."""
        # Simple data cleaning task should only require data-curator
        res_simple = self.resolver.resolve("Clean dataset and reverse-code Likert items")
        workers_simple = res_simple["required_subagents"]["execution_workers"]
        self.assertEqual(workers_simple, ["data-curator"])

        # Comprehensive Chapter 4 requires data-curator, statistical-expert, academic-writer
        res_complex = self.resolver.resolve("Write Chapter 4 findings")
        workers_complex = res_complex["required_subagents"]["execution_workers"]
        self.assertIn("data-curator", workers_complex)
        self.assertIn("statistical-expert", workers_complex)
        self.assertIn("academic-writer", workers_complex)

        # Ensure unneeded roles are NOT included (e.g. meta-analyst, qualitative-analyst)
        self.assertNotIn("meta-analyst", workers_complex)
        self.assertNotIn("qualitative-analyst", workers_complex)

    def test_10_backwards_compatibility_build_pipeline(self):
        """Verify legacy build_pipeline preserves exact existing format and formula."""
        res = build_pipeline("Analyze this dataset")
        self.assertEqual(res["capabilities_formula"], "DATA + STATISTICS")
        self.assertEqual(res["capabilities"], ["DATA", "STATISTICS"])
        self.assertEqual(len(res["pipeline"]), 2)
        self.assertIn("capability_resolution", res)
        self.assertEqual(res["capability_resolution"]["status"], "RESOLVED")


if __name__ == "__main__":
    unittest.main()
