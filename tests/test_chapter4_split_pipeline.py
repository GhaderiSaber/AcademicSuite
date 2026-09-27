#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_chapter4_split_pipeline.py — Comprehensive Test Suite for Decoupled Chapter 4 Pipeline

Validates:
1. Authoritative 4-Phase Decoupled Pipeline specification in MICRO_STAGE_SEQUENCES.md:
   - Phase 4A: Data Engineering & Curation (Stages 4A.0 – 4A.2)
   - Phase 4B: Exploratory Analysis & Assumptions (Stages 4B.1 – 4B.4)
   - Phase 4C: Core Inferential Modeling & Anomaly Audit (Stages 4C.1 – 4C.5)
   - Phase 4D: Scholarly Persian Drafting, QC & Monograph Assembly (Stages 4D.0 – 4D.11)
2. Three-Gate Checkpoint Architecture:
   - Gate 1: Data Curation & Reliability Passport
   - Gate 2: Assumption Compliance & Inferential Method Authorization
   - Gate 3: Mathematical Admissibility & MSAI Sign-Off Gate
3. Strict Cognitive Role Boundaries:
   - Computational immunity: Phases 4A–4C are strictly "The Hands" (zero Persian narrative prose).
   - Hallucination prevention: Phase 4D is strictly "The Voice" (bound to audited empirical JSON payload).
4. Academic Orchestrator Task Routing & Sequence synchronization in agent.md.
"""

import os
import re
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MICRO_STAGES_PATH = os.path.join(REPO_ROOT, ".agents", "references", "MICRO_STAGE_SEQUENCES.md")
ORCHESTRATOR_AGENT_PATH = os.path.join(REPO_ROOT, ".agents", "agents", "academic-orchestrator", "agent.md")


class TestChapter4SplitPipeline(unittest.TestCase):

    def setUp(self):
        self.assertTrue(os.path.isfile(MICRO_STAGES_PATH), f"Missing {MICRO_STAGES_PATH}")
        with open(MICRO_STAGES_PATH, "r", encoding="utf-8") as f:
            self.micro_stages_content = f.read()

        self.assertTrue(os.path.isfile(ORCHESTRATOR_AGENT_PATH), f"Missing {ORCHESTRATOR_AGENT_PATH}")
        with open(ORCHESTRATOR_AGENT_PATH, "r", encoding="utf-8") as f:
            self.orchestrator_content = f.read()

    def test_01_chapter4_four_phases_documented(self):
        """Verifies Section 1 in MICRO_STAGE_SEQUENCES.md documents all 4 decoupled phases."""
        self.assertIn("## 1. Chapter 4: Decoupled Empirical Findings Pipeline (Phases 4A – 4D)", self.micro_stages_content)
        self.assertIn("Phase 4A: Data Engineering & Curation Gate", self.micro_stages_content)
        self.assertIn("Phase 4B: Exploratory Analysis & Assumptions Gate", self.micro_stages_content)
        self.assertIn("Phase 4C: Core Inferential Modeling & Anomaly Audit", self.micro_stages_content)
        self.assertIn("Phase 4D: Scholarly Persian Drafting, QC & Monograph Assembly", self.micro_stages_content)

    def test_02_three_gate_checkpoints_documented(self):
        """Verifies all 3 intermediate mathematical and methodological gates are documented."""
        self.assertIn("Gate 1: Data Curation Passport", self.micro_stages_content)
        self.assertIn("Gate 2: Assumption Compliance & Method Authorization", self.micro_stages_content)
        self.assertIn("Gate 3: Mathematical Admissibility & MSAI Sign-Off", self.micro_stages_content)

    def test_03_phase_4a_stages_and_roles(self):
        """Verifies Phase 4A stages (4A.0, 4A.1, 4A.2) and assigned subagents."""
        self.assertIn("Stage 4A.0", self.micro_stages_content)
        self.assertIn("Stage 4A.1", self.micro_stages_content)
        self.assertIn("Stage 4A.2", self.micro_stages_content)
        self.assertIn("data-curator", self.micro_stages_content)
        self.assertIn("psychometric-expert", self.micro_stages_content)
        self.assertIn("data_cleaned.xlsx", self.micro_stages_content)

    def test_04_phase_4b_stages_and_roles(self):
        """Verifies Phase 4B stages (4B.1 to 4B.4) and assumption certificate gate."""
        self.assertIn("Stage 4B.1", self.micro_stages_content)
        self.assertIn("Stage 4B.2", self.micro_stages_content)
        self.assertIn("Stage 4B.3", self.micro_stages_content)
        self.assertIn("Stage 4B.4", self.micro_stages_content)
        self.assertIn("01_demographics_payload.json", self.micro_stages_content)
        self.assertIn("03_assumptions_report.json", self.micro_stages_content)
        self.assertIn("04_correlations_payload.json", self.micro_stages_content)
        self.assertIn("Assumption Compliance Certificate", self.micro_stages_content)

    def test_05_phase_4c_stages_and_admissibility_gate(self):
        """Verifies Phase 4C stages (4C.1 to 4C.5), MSAI audit, and Gate 3 clearance."""
        self.assertIn("Stage 4C.1", self.micro_stages_content)
        self.assertIn("Stage 4C.2.1", self.micro_stages_content)
        self.assertIn("Stage 4C.3.1", self.micro_stages_content)
        self.assertIn("Stage 4C.4", self.micro_stages_content)
        self.assertIn("Stage 4C.5", self.micro_stages_content)
        self.assertIn("empirical_findings_payload.json", self.micro_stages_content)
        self.assertIn("statistical_audit_report.json", self.micro_stages_content)
        self.assertIn("structural_model_diagram.png", self.micro_stages_content)

    def test_06_phase_4d_stages_triads_and_voice_role(self):
        """Verifies Phase 4D drafting stages, triad outputs, and 3-table regression standard."""
        self.assertIn("Stage 4D.0", self.micro_stages_content)
        self.assertIn("Stage 4D.1", self.micro_stages_content)
        self.assertIn("Stage 4D.6.1", self.micro_stages_content)
        self.assertIn("Stage 4D.10", self.micro_stages_content)
        self.assertIn("Stage 4D.11", self.micro_stages_content)
        self.assertIn("academic-writer", self.micro_stages_content)
        self.assertIn("results-auditor", self.micro_stages_content)
        self.assertIn("final-judge", self.micro_stages_content)
        self.assertIn("Chapter_4_Results.docx", self.micro_stages_content)

    def test_07_decoupled_contract_invariants(self):
        """Verifies the core architectural invariants of the decoupled pipeline."""
        self.assertIn("Computational Immunity", self.micro_stages_content)
        self.assertIn("Hallucination Prevention", self.micro_stages_content)
        self.assertIn("One-Hypothesis-One-Stage Triad Invariant", self.micro_stages_content)
        self.assertIn("ZERO narrative text is drafted", self.micro_stages_content)
        self.assertIn("Emitting Persian narrative draft text in Phases 4A–4C is strictly prohibited", self.micro_stages_content)

    def test_08_academic_orchestrator_agent_synchronization(self):
        """Verifies academic-orchestrator/agent.md reflects the 4-phase decoupled pipeline."""
        self.assertIn("Phase 4A: DATA (data-curator)", self.orchestrator_content)
        self.assertIn("Phase 4B: ASSUMPTIONS (statistics-agent + statistical-expert)", self.orchestrator_content)
        self.assertIn("Phase 4D: DRAFTING (Tables First -> Dynamic Non-Template Narration -> Triad Assembly via academic-writer + results-auditor + final-judge)", self.orchestrator_content)
        self.assertIn("Chapter 4 Findings (Phases 4A–4D Decoupled)", self.orchestrator_content)
        self.assertIn("Phase 4D: Scholarly Drafting (Tables First -> Dynamic Non-Template Narration -> 4D.0–4D.11)", self.orchestrator_content)


    def test_09_writing_phase_internal_separation(self):
        """Verifies Phase 4D internally separates into Tables First and Dynamic Narration."""
        self.assertIn("The Internal Writing Phase Decoupling (Tables First", self.micro_stages_content)
        self.assertIn("Step 4D-1: Deterministic Table Scaffolding (Tables First)", self.micro_stages_content)
        self.assertIn("Step 4D-2: Dynamic Epistemic Narration Formulation", self.micro_stages_content)
        self.assertIn("Step 4D-3: Synchronized Triad Compilation & Monograph Assembly", self.micro_stages_content)
        self.assertIn("Zero narrative prose is written in this step", self.micro_stages_content)

    def test_10_zero_template_dynamic_narration_invariant(self):
        """Verifies that prewritten templates, canned boilerplate, and placeholders are strictly prohibited."""
        self.assertIn("Zero-Template Dynamic Narration Invariant", self.micro_stages_content)
        self.assertIn("Strict Zero-Template & Anti-Boilerplate Invariant", self.micro_stages_content)
        self.assertIn("Prewritten boilerplate, static placeholders", self.micro_stages_content)
        self.assertIn("mechanical fill-in-the-blank text are **strictly prohibited**", self.micro_stages_content)
        self.assertIn("refuse and fail any deliverable containing empty, canned, or template placeholder text", self.micro_stages_content)

    def test_11_mechanical_invariant_registered_in_hook_rules(self):
        """Verifies AP-2026-ZERO-TEMPLATE-DYNAMIC-NARRATION is registered and active in enforced_invariants.json."""
        import json
        invariants_path = os.path.join(REPO_ROOT, ".agents", "hooks", "rules", "enforced_invariants.json")
        self.assertTrue(os.path.isfile(invariants_path), f"Missing {invariants_path}")
        with open(invariants_path, "r", encoding="utf-8") as f:
            invariants_data = json.load(f)

        invariants = invariants_data.get("invariants", {})
        self.assertIn("AP-2026-ZERO-TEMPLATE-DYNAMIC-NARRATION", invariants)
        rule = invariants["AP-2026-ZERO-TEMPLATE-DYNAMIC-NARRATION"]
        self.assertTrue(rule.get("enabled"))
        self.assertEqual(rule.get("check_type"), "regex_ban")
        self.assertIn("در این بخش", rule.get("pattern", ""))


if __name__ == "__main__":
    unittest.main()
