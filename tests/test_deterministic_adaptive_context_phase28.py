#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_deterministic_adaptive_context_phase28.py — Phase 28 Deterministic Adaptive Context Test Suite

Verifies that:
1. Context retrieval happens deterministically at the execution boundary (PreInvocation hook).
2. Intent detection accurately extracts academic capabilities and tasks across domains.
3. The boundary payload strictly delivers the 4-part contract:
   - relevant_lessons
   - known_pitfalls
   - applicable_methodology_rules
   - calibrated_defaults
4. Disputed contradictions are quarantined from retrieval until formally RESOLVED (Phase 27 integration).
5. Subagent dispatch boundary enriches subagent prompts with specialist context.
6. Non-academic turns (git commands, trivial greetings) bypass retrieval (Anti-Dump invariant).
7. Project scope containment strictly isolates local project lessons.
8. Directive 18 line and byte ceilings are observed across all implementation files.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.academic_knowledge_manager import AcademicKnowledgeManager
from scripts.academic_adaptive_context_boundary import AcademicAdaptiveContextBoundary
from scripts.academic_behavior_consolidator import AcademicBehaviorConsolidator
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "hooks"))
from learning_hooks import LearningHooks


class TestDeterministicAdaptiveContextPhase28(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="phase28_boundary_test_")
        self.km = AcademicKnowledgeManager(base_dir=self.test_dir)
        self.boundary = AcademicAdaptiveContextBoundary(base_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # Test 1: PreInvocation Hook Injects Adaptive Context Deterministically
    # -------------------------------------------------------------------------
    def test_01_pre_invocation_automatically_injects_context(self):
        """Proves PreInvocation hook automatically injects adaptive context for academic turns."""
        # Create a sample transcript with an academic modeling request
        transcript_path = os.path.join(self.test_dir, "transcript.jsonl")
        turn_event = {
            "step_index": 1,
            "type": "USER_INPUT",
            "content": "Please execute Preacher & Hayes bootstrap mediation for our Chapter 4 findings.",
            "created_at": "2026-09-19T12:00:00Z"
        }
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(turn_event) + "\n")

        payload = {
            "transcriptPath": transcript_path,
            "conversationId": "test-conv-001",
            "workspacePaths": [self.test_dir]
        }

        hook_res = LearningHooks.handle_pre_invocation(payload)
        self.assertIn("injectSteps", hook_res)
        steps = hook_res["injectSteps"]
        self.assertGreater(len(steps), 0)

        ephemeral = steps[0].get("ephemeralMessage", "")
        # Must contain constitutional reminder
        self.assertIn("CONSTITUTIONAL ENFORCEMENT ACTIVE", ephemeral)
        # Must contain deterministic adaptive context
        self.assertIn("DETERMINISTIC ADAPTIVE CONTEXT (BOUND AT EXECUTION BOUNDARY)", ephemeral)
        self.assertIn("Target Capability**: `MEDIATION`", ephemeral)
        self.assertIn("Known Pitfalls (Anti-Patterns to Avoid):", ephemeral)
        self.assertIn("Relevant Active Lessons:", ephemeral)
        self.assertIn("Applicable Methodology Rules & Boundary Conditions:", ephemeral)

    # -------------------------------------------------------------------------
    # Test 2: Accurate Academic Task Intent Detection
    # -------------------------------------------------------------------------
    def test_02_academic_task_intent_detection(self):
        """Verifies robust mapping of diverse academic prompts to canonical capabilities and agents."""
        cases = [
            ("Run PROCESS Model 4 bootstrap mediation with 5,000 resamples", "mediation", "statistics-agent"),
            ("Verify Mauchly sphericity and perform repeated-measures ANOVA", "longitudinal-analysis", "statistics-agent"),
            ("Execute CFA to evaluate convergent validity and construct reliability", "psychometrics", "psychometric-expert"),
            ("Draft Chapter 4 findings report adhering to APA 7 tables", "chapter4", "academic-writer"),
            ("Synthesize Chapter 5 discussion highlighting theoretical implications", "chapter5", "academic-writer"),
            ("Calculate G*Power sample size for ANCOVA with 2 covariates", "methodology", "methodology-expert"),
            ("Screen dataset for missing data patterns using Little MCAR test", "data_cleaning", "data-curator")
        ]

        for prompt, expected_cap, expected_agent in cases:
            intent = self.boundary.detect_task_intent(prompt)
            self.assertIsNotNone(intent, f"Failed to detect intent for prompt: {prompt}")
            self.assertEqual(intent["capability"], expected_cap, f"Mismatch for '{prompt}'")
            self.assertEqual(intent["primary_agent"], expected_agent, f"Agent mismatch for '{prompt}'")

    # -------------------------------------------------------------------------
    # Test 3: Structured 4-Part Boundary Payload
    # -------------------------------------------------------------------------
    def test_03_four_part_boundary_payload_structure(self):
        """Proves boundary context delivers lessons, pitfalls, methodology rules, and defaults."""
        # Seed test knowledge items
        self.km.add_lesson({
            "lesson_id": "LSN-TEST-01",
            "target_skill": "mediation",
            "desired_behavior": "Always report 95% BCa confidence intervals for indirect effects.",
            "generalization": "Never rely solely on p-values for indirect effects."
        })
        from datetime import datetime, timezone
        self.km.add_anti_pattern({
            "anti_pattern_id": "AP-TEST-01",
            "category": "statistical",
            "defective_pattern": "Assuming normal distribution for indirect effect products.",
            "why_defective": "Product of two normal coefficients is asymmetric and skewed in small-to-moderate samples.",
            "observed_symptoms": ["Inflated Type I error", "Artificially narrow confidence intervals"],
            "detection_heuristic": {
                "trigger_rule": "Check if Sobel z-test is reported instead of bootstrap percentile CIs."
            },
            "corrective_remedy": "Execute 5,000 bootstrap resamples.",
            "reusable": True,
            "updated_at": datetime.now(timezone.utc).isoformat()
        })

        b_data = self.boundary.retrieve_boundary_context(
            capability="mediation",
            task="bootstrap_mediation",
            agent="statistics-agent"
        )

        self.assertEqual(b_data["contract_version"], "1.0.0")
        self.assertEqual(b_data["target_capability"], "mediation")
        self.assertEqual(b_data["agent"], "statistics-agent")

        # Check lessons
        self.assertGreater(len(b_data["relevant_lessons"]), 0)
        self.assertEqual(b_data["relevant_lessons"][0]["lesson_id"], "LSN-TEST-01")

        # Check pitfalls
        self.assertGreater(len(b_data["known_pitfalls"]), 0)
        self.assertEqual(b_data["known_pitfalls"][0]["anti_pattern_id"], "AP-TEST-01")

        # Check methodology rules key exists
        self.assertIn("applicable_methodology_rules", b_data)
        self.assertIn("calibrated_defaults", b_data)

    # -------------------------------------------------------------------------
    # Test 4: Quarantine of Disputed Contradictions (Phase 27 Integration)
    # -------------------------------------------------------------------------
    def test_04_quarantine_of_disputed_contradictions(self):
        """Proves that active/unresolved contradictions filter out disputed lessons until resolved."""
        # Add two contradictory lessons
        self.km.add_lesson({
            "lesson_id": "LSN-RM-DISPUTED",
            "target_skill": "longitudinal-analysis",
            "desired_behavior": "Always use RM-ANOVA for longitudinal measurements.",
            "scope": "domain"
        })
        self.km.add_lesson({
            "lesson_id": "LSN-LMM-DISPUTED",
            "target_skill": "longitudinal-analysis",
            "desired_behavior": "Always use Linear Mixed Models LMM instead of RM-ANOVA.",
            "scope": "domain"
        })

        # Record active contradiction in CONFLICT_DETECTED status
        self.km.add_contradiction_record({
            "contradiction_id": "CTD-RM-LMM-01",
            "target_skill": "longitudinal-analysis",
            "lesson_a_id": "LSN-RM-DISPUTED",
            "lesson_b_id": "LSN-LMM-DISPUTED",
            "conflict_type": "MODEL_SPECIFICATION_CONFLICT",
            "stage": "CONFLICT_DETECTED",
            "status": "CONFLICT_DETECTED",
            "description": "Conflict between RM-ANOVA and LMM longitudinal modeling."
        })

        # Query boundary context: both disputed lessons must be quarantined!
        b_data = self.boundary.retrieve_boundary_context(capability="longitudinal-analysis")
        retrieved_ids = [l["lesson_id"] for l in b_data["relevant_lessons"]]
        self.assertNotIn("LSN-RM-DISPUTED", retrieved_ids, "Disputed lesson A must be quarantined.")
        self.assertNotIn("LSN-LMM-DISPUTED", retrieved_ids, "Disputed lesson B must be quarantined.")

        # Contradiction itself should be listed in applicable rules
        ctd_ids = [r["contradiction_id"] for r in b_data["applicable_methodology_rules"]]
        self.assertIn("CTD-RM-LMM-01", ctd_ids)

    # -------------------------------------------------------------------------
    # Test 5: Subagent Dispatch Enrichment
    # -------------------------------------------------------------------------
    def test_05_subagent_dispatch_enrichment(self):
        """Proves that invoke_subagent payload is enriched with subagent-specific context."""
        subagents = [
            {
                "TypeName": "statistics-agent",
                "Role": "Statistical Modeler",
                "Prompt": "Run multiple regression modeling on dataset.csv."
            },
            {
                "TypeName": "academic-writer",
                "Role": "Chapter Drafter",
                "Prompt": "Draft Chapter 4 findings with APA 7 tables."
            }
        ]

        enriched = self.boundary.enrich_subagent_dispatch(subagents)
        self.assertEqual(len(enriched), 2)

        # Check statistics-agent prompt was enriched
        sa1 = enriched[0]
        self.assertTrue(sa1.get("adaptive_context_bound"))
        self.assertIn("DETERMINISTIC ADAPTIVE CONTEXT", sa1["Prompt"])
        self.assertIn("Run multiple regression modeling", sa1["Prompt"])

        # Check academic-writer prompt was enriched
        sa2 = enriched[1]
        self.assertTrue(sa2.get("adaptive_context_bound"))
        self.assertIn("DETERMINISTIC ADAPTIVE CONTEXT", sa2["Prompt"])
        self.assertIn("Draft Chapter 4 findings", sa2["Prompt"])

    # -------------------------------------------------------------------------
    # Test 6: Non-Academic Turn Bypass (Anti-Dump Invariant)
    # -------------------------------------------------------------------------
    def test_06_non_academic_turn_bypass(self):
        """Proves pure operational turns do not trigger context retrieval, preserving context window."""
        bypass_messages = [
            "git status",
            "git commit -m 'feat: update docs'",
            "clean working tree",
            "hello",
            "ok",
            "proceed",
            "yes"
        ]

        for msg in bypass_messages:
            self.assertTrue(self.boundary.is_bypass_turn(msg), f"Failed to bypass: '{msg}'")
            intent = self.boundary.detect_task_intent(msg)
            self.assertIsNone(intent, f"Intent should be None for '{msg}'")

    # -------------------------------------------------------------------------
    # Test 7: Scope Containment Across Projects
    # -------------------------------------------------------------------------
    def test_07_scope_containment(self):
        """Proves project-specific lessons remain isolated to the designated project."""
        # Add project A lesson
        self.km.add_lesson({
            "lesson_id": "LSN-PROJ-A-ONLY",
            "target_skill": "mediation",
            "desired_behavior": "Enforce clinical cutoffs for BDI-II in Depression Study.",
            "scope": "project",
            "project_id": "PROJ-ALPHA"
        })

        # Query for Project Alpha
        alpha_data = self.boundary.retrieve_boundary_context(
            capability="mediation",
            project_id="PROJ-ALPHA"
        )
        alpha_ids = [l["lesson_id"] for l in alpha_data["relevant_lessons"]]
        self.assertIn("LSN-PROJ-A-ONLY", alpha_ids)

        # Query for Project Beta
        beta_data = self.boundary.retrieve_boundary_context(
            capability="mediation",
            project_id="PROJ-BETA"
        )
        beta_ids = [l["lesson_id"] for l in beta_data["relevant_lessons"]]
        self.assertNotIn("LSN-PROJ-A-ONLY", beta_ids, "Project Alpha lesson must not leak to Project Beta.")

    # -------------------------------------------------------------------------
    # Test 8: Directive 18 Compliance
    # -------------------------------------------------------------------------
    def test_08_directive_18_compliance(self):
        """Verifies boundary engine and SKILL.md observe Directive 18 ceilings (<= 500 lines, <= 40,000 bytes)."""
        cand = os.path.join(ROOT_DIR, ".agents", "scripts", "academic_adaptive_context_boundary.py")
        boundary_script = cand if os.path.isfile(cand) else os.path.join(ROOT_DIR, "scripts", "academic_adaptive_context_boundary.py")
        files_to_check = [
            boundary_script,
            os.path.join(ROOT_DIR, ".agents", "skills", "academic-adaptive-context", "SKILL.md")
        ]

        for file_path in files_to_check:
            self.assertTrue(os.path.isfile(file_path), f"File {file_path} must exist.")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            lines = content.splitlines()
            byte_size = len(content.encode("utf-8"))

            self.assertLessEqual(
                len(lines), 500,
                f"{os.path.basename(file_path)} exceeds 500 lines limit ({len(lines)} lines)."
            )
            self.assertLessEqual(
                byte_size, 40000,
                f"{os.path.basename(file_path)} exceeds 40,000 bytes limit ({byte_size} bytes)."
            )


if __name__ == "__main__":
    unittest.main()
