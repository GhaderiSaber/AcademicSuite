#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_task_router.py — Unit tests for Academic Task Router Engine ("The Hands")

Tests:
1. Canonical Pattern 1: "Analyze this dataset" -> DATA + STATISTICS
2. Canonical Pattern 2: "Write Chapter 4" -> STATISTICS + WRITING + VALIDATION
3. Canonical Pattern 3: "Find research gaps" -> RESEARCH + METHODOLOGY
4. Canonical Pattern 4: "Perform CFA and SEM" -> DATA + STATISTICS + VALIDATION
5. Canonical Pattern 5: "Analyze these network data" -> DATA + NETWORK-ANALYSIS + STATISTICS + VALIDATION
6. Strict pipeline ordering invariant: RESEARCH -> METHODOLOGY -> DATA -> NETWORK-ANALYSIS -> STATISTICS -> WRITING -> VALIDATION
7. Contextual invariant complements (e.g. drafting results implies statistics + validation)
8. Pipeline metadata and artifact contract completeness
9. CLI commands execution: route, explain, list-patterns
"""

import os
import sys
import json
import subprocess
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))
import academic_task_router as router


class TestAcademicTaskRouter(unittest.TestCase):

    def test_01_canonical_analyze_dataset(self):
        """Pattern 1: 'Analyze this dataset' -> DATA + STATISTICS."""
        prompts = [
            "Analyze this dataset",
            "Please analyze the data",
            "Explore dataset and clean it"
        ]
        for p in prompts:
            res = router.build_pipeline(p)
            self.assertEqual(res["capabilities"], ["DATA", "STATISTICS"], f"Failed on: {p}")
            self.assertEqual(res["capabilities_formula"], "DATA + STATISTICS")
            self.assertEqual(len(res["pipeline"]), 2)
            self.assertEqual(res["pipeline"][0]["agent"], "data-agent")
            self.assertEqual(res["pipeline"][1]["agent"], "statistics-agent")

    def test_02_canonical_write_chapter_4(self):
        """Pattern 2: 'Write Chapter 4' -> STATISTICS + WRITING + VALIDATION."""
        prompts = [
            "Write Chapter 4",
            "Draft Chapter 4 findings",
            "Generate results chapter"
        ]
        for p in prompts:
            res = router.build_pipeline(p)
            self.assertEqual(res["capabilities"], ["STATISTICS", "WRITING", "VALIDATION"], f"Failed on: {p}")
            self.assertEqual(res["capabilities_formula"], "STATISTICS + WRITING + VALIDATION")
            self.assertEqual(len(res["pipeline"]), 3)
            self.assertEqual(res["pipeline"][0]["agent"], "statistics-agent")
            self.assertEqual(res["pipeline"][1]["agent"], "academic-writer")
            self.assertEqual(res["pipeline"][2]["agent"], "validation-agent")

    def test_03_canonical_find_research_gaps(self):
        """Pattern 3: 'Find research gaps' -> RESEARCH + METHODOLOGY."""
        prompts = [
            "Find research gaps",
            "Identify research gaps in literature",
            "Formulate research questions from theoretical gaps"
        ]
        for p in prompts:
            res = router.build_pipeline(p)
            self.assertEqual(res["capabilities"], ["RESEARCH", "METHODOLOGY"], f"Failed on: {p}")
            self.assertEqual(res["capabilities_formula"], "RESEARCH + METHODOLOGY")
            self.assertEqual(len(res["pipeline"]), 2)
            self.assertEqual(res["pipeline"][0]["agent"], "research-agent")
            self.assertEqual(res["pipeline"][1]["agent"], "research-agent")

    def test_04_canonical_perform_cfa_sem(self):
        """Pattern 4: 'Perform CFA and SEM' -> DATA + STATISTICS + VALIDATION."""
        prompts = [
            "Perform CFA and SEM",
            "Run CFA and SEM modeling",
            "Execute SEM and CFA analysis"
        ]
        for p in prompts:
            res = router.build_pipeline(p)
            self.assertEqual(res["capabilities"], ["DATA", "STATISTICS", "VALIDATION"], f"Failed on: {p}")
            self.assertEqual(res["capabilities_formula"], "DATA + STATISTICS + VALIDATION")
            self.assertEqual(len(res["pipeline"]), 3)
            self.assertEqual(res["pipeline"][0]["agent"], "data-agent")
            self.assertEqual(res["pipeline"][1]["agent"], "statistics-agent")
            self.assertEqual(res["pipeline"][2]["agent"], "validation-agent")

    def test_05_canonical_analyze_network_data(self):
        """Pattern 5: 'Analyze these network data' -> DATA + NETWORK-ANALYSIS + STATISTICS + VALIDATION."""
        prompts = [
            "Analyze these network data",
            "Run network analysis on bibliometric data",
            "Explore co-occurrence network and compute centrality"
        ]
        for p in prompts:
            res = router.build_pipeline(p)
            self.assertEqual(
                res["capabilities"],
                ["DATA", "NETWORK-ANALYSIS", "STATISTICS", "VALIDATION"],
                f"Failed on: {p}"
            )
            self.assertEqual(
                res["capabilities_formula"],
                "DATA + NETWORK-ANALYSIS + STATISTICS + VALIDATION"
            )
            self.assertEqual(len(res["pipeline"]), 4)
            self.assertEqual(res["pipeline"][0]["agent"], "data-agent")
            self.assertEqual(res["pipeline"][1]["agent"], "statistics-agent")
            self.assertEqual(res["pipeline"][1]["skill"], "network-analysis")
            self.assertEqual(res["pipeline"][2]["agent"], "statistics-agent")
            self.assertEqual(res["pipeline"][3]["agent"], "validation-agent")

    def test_06_strict_execution_ordering_invariant(self):
        """Regardless of input token permutation, capabilities must adhere to EXECUTION_ORDER."""
        # Prompt mentioning validation first, writing second, data third, literature fourth
        p = "Validate and audit the writing of results after cleaning data and reviewing literature"
        res = router.build_pipeline(p)
        caps = res["capabilities"]
        
        # Canonical order: RESEARCH -> METHODOLOGY -> DATA -> NETWORK-ANALYSIS -> STATISTICS -> WRITING -> VALIDATION
        expected_order = [c for c in router.EXECUTION_ORDER if c in caps]
        self.assertEqual(caps, expected_order)
        # Ensure RESEARCH precedes DATA precedes WRITING precedes VALIDATION
        self.assertLess(caps.index("RESEARCH"), caps.index("DATA"))
        self.assertLess(caps.index("DATA"), caps.index("WRITING"))
        self.assertLess(caps.index("WRITING"), caps.index("VALIDATION"))

    def test_07_pipeline_step_metadata_integrity(self):
        """Every pipeline step must contain complete metadata and artifact contracts."""
        res = router.build_pipeline("Perform CFA and SEM")
        for step in res["pipeline"]:
            self.assertIn("step", step)
            self.assertIn("capability", step)
            self.assertIn("agent", step)
            self.assertIn("skill", step)
            self.assertIn("skill_path", step)
            self.assertIn("description", step)
            self.assertIn("input_artifact", step)
            self.assertIn("output_artifact", step)
            self.assertTrue(os.path.exists(os.path.join(ROOT_DIR, step["skill_path"])), f"Skill path missing: {step['skill_path']}")

    def test_08_cli_route(self):
        """CLI 'route' command should return valid JSON with correct formula."""
        cmd = [sys.executable, os.path.join(ROOT_DIR, "scripts", "academic_task_router.py"), "route", "Analyze this dataset"]
        out = subprocess.check_output(cmd, encoding="utf-8")
        data = json.loads(out)
        self.assertEqual(data["capabilities_formula"], "DATA + STATISTICS")
        self.assertEqual(data["total_steps"], 2)

    def test_09_cli_explain(self):
        """CLI 'explain' command should print human-readable summary."""
        cmd = [sys.executable, os.path.join(ROOT_DIR, "scripts", "academic_task_router.py"), "explain", "Write Chapter 4"]
        out = subprocess.check_output(cmd, encoding="utf-8")
        self.assertIn("Formula: STATISTICS + WRITING + VALIDATION", out)
        self.assertIn("Step 1: [STATISTICS]", out)
        self.assertIn("Step 2: [WRITING]", out)
        self.assertIn("Step 3: [VALIDATION]", out)

    def test_10_cli_list_patterns(self):
        """CLI 'list-patterns' command should list all 5 canonical patterns."""
        cmd = [sys.executable, os.path.join(ROOT_DIR, "scripts", "academic_task_router.py"), "list-patterns"]
        out = subprocess.check_output(cmd, encoding="utf-8")
        self.assertIn("Analyze this dataset", out)
        self.assertIn("Write Chapter 4", out)
        self.assertIn("Find research gaps", out)
        self.assertIn("Perform CFA and SEM", out)
        self.assertIn("Analyze these network data", out)


if __name__ == "__main__":
    unittest.main()
