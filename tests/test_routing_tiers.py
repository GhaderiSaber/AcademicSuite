#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_routing_tiers.py — Unit tests for Three-Tier Execution Routing Matrix
Tests:
1. Tier 1: Custom Subagents (bounded research micro-stages)
2. Tier 2: /boost (hard isolated reasoning dilemmas)
3. Tier 3: /teamwork-preview (huge long-running multi-chapter projects)
4. Quantitative scope triggers (chapter_count, file_count)
5. CLI execution integrity
"""

import os
import sys
import json
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))
import orchestrator_dependency_resolver as odr


class TestRoutingTiers(unittest.TestCase):

    def test_01_tier_1_custom_subagents(self):
        """Ordinary bounded tasks must route to Tier 1 Custom Subagents."""
        tasks = [
            ("Compute descriptive statistics for sample of 120 students", "statistics-agent"),
            ("Reverse-code items and screen missing data using MCAR", "data-agent"),
            ("Format APA 7 three-line table with Persian typography", "academic-writer"),
            ("Draft findings narrative for hypothesis 1", "academic-writer"),
            ("Audit degrees of freedom and check statistical consistency", "validation-agent")
        ]
        for query, expected_agent in tasks:
            res = odr.route_task(query)
            self.assertEqual(res["tier"], "tier_1_custom_subagents", f"Failed on: {query}")
            self.assertEqual(res["recommended_mechanism"], "invoke_subagent")
            self.assertEqual(res["assigned_subagent"], expected_agent)
            self.assertIsNone(res["slash_command"])

    def test_02_tier_2_boost(self):
        """Hard isolated reasoning dilemmas must route to Tier 2 /boost."""
        dilemmas = [
            "Derive identification equations for non-converging non-recursive SEM with feedback loops",
            "Resolve severe multicollinearity dilemma with singular matrix",
            "Address empirical underidentification in complex 3-way interaction",
            "Derive mathematical proof for non-linear latent growth curve",
            "Formulate Heckman selection correction with instrumental variable dilemma"
        ]
        for query in dilemmas:
            res = odr.route_task(query)
            self.assertEqual(res["tier"], "tier_2_boost", f"Failed on: {query}")
            self.assertEqual(res["recommended_mechanism"], "/boost")
            self.assertEqual(res["slash_command"], "/boost")
            self.assertIn("Boost Engine", res["primary_conductor"])

    def test_03_tier_3_teamwork(self):
        """Huge multi-chapter overhauls must route to Tier 3 /teamwork-preview."""
        huge_projects = [
            "Restructure 20-chapter monograph with thousands of source files",
            "Repository-wide full thesis overhaul across five dissertation volumes",
            "Multi-study repository migration and longitudinal multi-wave overhaul"
        ]
        for query in huge_projects:
            res = odr.route_task(query)
            self.assertEqual(res["tier"], "tier_3_teamwork", f"Failed on: {query}")
            self.assertEqual(res["recommended_mechanism"], "/teamwork-preview")
            self.assertEqual(res["slash_command"], "/teamwork-preview")
            self.assertIn("Teamwork", res["primary_conductor"])

    def test_04_quantitative_triggers(self):
        """Numeric scope thresholds must trigger Tier 3 regardless of text."""
        # 12 chapters
        res_ch = odr.route_task("Format results section", chapter_count=12)
        self.assertEqual(res_ch["tier"], "tier_3_teamwork")

        # 150 files
        res_fc = odr.route_task("Check dataset files", file_count=150)
        self.assertEqual(res_fc["tier"], "tier_3_teamwork")

        # Standard 1 chapter, 5 files -> Tier 1
        res_std = odr.route_task("Calculate regression coefficients", chapter_count=1, file_count=5)
        self.assertEqual(res_std["tier"], "tier_1_custom_subagents")


if __name__ == "__main__":
    unittest.main()
