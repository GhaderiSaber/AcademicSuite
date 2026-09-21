#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_dynamic_context_token_budgeting.py — Dynamic Context Token Budgeting Unit Tests

Verifies Phase 41:
1. Deterministic Token Estimator: Accuracy on English, Persian text, code blocks, and markdown.
2. Strict Ceiling Enforcement: Briefings strictly adhere to max_token_budget across varying limits (250, 500, 800, 1500).
3. Priority-Weighted Selection: Pitfalls and critical mandates prioritized over exemplars under tight budgets.
4. Dual Compression Modes: COMPACT mode activated below 500 tokens; STANDARD mode at or above 500 tokens.
5. Telemetry Contract: budget_telemetry includes max_token_budget, estimated_tokens_used, utilization ratio, and pruned details.
6. Execution Boundary Integration: Turn pre-flight (800) and subagent dispatch (500) budgets verified.
7. CLI Tool Verification: retrieve_adaptive_context.py supports --max-tokens and formats budget badges.
8. Directive 18 Ceilings: Scripts and SKILL.md strictly observe line and byte limits.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
for p in [ROOT_DIR, AGENTS_DIR, os.path.join(AGENTS_DIR, "scripts")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from scripts.academic_context_token_budgeter import (
    AcademicContextTokenBudgeter,
    estimate_tokens
)
from scripts.academic_knowledge_manager import AcademicKnowledgeManager
from scripts.academic_adaptive_context_boundary import AcademicAdaptiveContextBoundary


class TestDynamicContextTokenBudgeting(unittest.TestCase):
    """Authoritative test suite for Phase 41 Dynamic Context Token Budgeting."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_token_budgeting_")
        self.km = AcademicKnowledgeManager(base_dir=self.test_dir)
        self.boundary = AcademicAdaptiveContextBoundary(base_dir=self.test_dir)
        self.budgeter = AcademicContextTokenBudgeter()
        self.cli_script = os.path.join(
            ROOT_DIR,
            ".agents",
            "skills",
            "academic-adaptive-context",
            "scripts",
            "retrieve_adaptive_context.py"
        )

        # Seed realistic knowledge items
        self._seed_sample_knowledge()

    def tearDown(self):
        if os.path.isdir(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def _seed_sample_knowledge(self):
        """Populate isolated test knowledge store with varied items."""
        # 1. Anti-Pattern 1
        ap1_data = {
            "contract_version": "1.0.0",
            "anti_pattern_id": "AP-MED-001",
            "category": "statistical",
            "capability": "mediation",
            "defective_pattern": "Relying on the normal-theory Sobel test for indirect effects.",
            "why_defective": "Sobel test assumes symmetric sampling distribution which is violated for products of coefficients.",
            "observed_symptoms": ["Type II error inflation", "Symmetric standard error assumption violated"],
            "corrective_remedy": "Execute Preacher & Hayes bootstrap mediation with 5,000 resamples and 95% BCa CIs.",
            "detection_heuristic": {
                "trigger_rule": "Check mediation analysis script for Sobel test formulas."
            },
            "reusable": True,
            "status": "VALIDATED",
            "updated_at": "2026-09-19T12:00:00Z"
        }
        with open(os.path.join(self.km.anti_patterns_dir, "AP-MED-001.json"), "w", encoding="utf-8") as f:
            json.dump(ap1_data, f, indent=2)

        # 2. Anti-Pattern 2
        ap2_data = {
            "contract_version": "1.0.0",
            "anti_pattern_id": "AP-MED-002",
            "category": "typography",
            "capability": "mediation",
            "defective_pattern": "Reporting p = .000 or omitting Persian leading zero (.05 instead of ۰.۰۵).",
            "why_defective": "APA 7 forbids p = .000 and Persian academic typography mandates leading zero before dot.",
            "observed_symptoms": ["Leading zero omitted", "p = .000 detected"],
            "corrective_remedy": "Enforce strict APA 7 leading zero: ۰.۰۰۱ > p and ۰.۰۵.",
            "detection_heuristic": {
                "trigger_rule": "Regex scan for .000 or .\\d in Persian text."
            },
            "reusable": True,
            "status": "VALIDATED",
            "updated_at": "2026-09-19T12:00:00Z"
        }
        with open(os.path.join(self.km.anti_patterns_dir, "AP-MED-002.json"), "w", encoding="utf-8") as f:
            json.dump(ap2_data, f, indent=2)

        # 3. Lesson 1
        lsn1_data = {
            "contract_version": "1.0.0",
            "lesson_id": "LSN-MED-001",
            "source_experience_id": "EXP-MED-001",
            "lesson_type": "WHAT_TO_DO",
            "trigger_source": "MANUAL_CURATION",
            "capability": "mediation",
            "desired_behavior": "Verify regression slope homogeneity and normality of residuals prior to mediation.",
            "generalization": "Parametric assumption testing must precede inferential path estimation.",
            "confidence": 0.90,
            "scope": "domain",
            "status": "VALIDATED",
            "created_at": "2026-09-19T12:00:00Z",
            "updated_at": "2026-09-19T12:00:00Z"
        }
        with open(os.path.join(self.km.lessons_dir, "LSN-MED-001.json"), "w", encoding="utf-8") as f:
            json.dump(lsn1_data, f, indent=2)

        # 4. Lesson 2
        lsn2_data = {
            "contract_version": "1.0.0",
            "lesson_id": "LSN-MED-002",
            "source_experience_id": "EXP-MED-002",
            "lesson_type": "WHAT_TO_DO",
            "trigger_source": "MANUAL_CURATION",
            "capability": "mediation",
            "desired_behavior": "Report standardized indirect effect path coefficients alongside unstandardized estimates.",
            "generalization": "Comprehensive APA 7 mediation reporting requires both B and beta metrics.",
            "confidence": 0.85,
            "scope": "domain",
            "status": "VALIDATED",
            "created_at": "2026-09-19T12:00:00Z",
            "updated_at": "2026-09-19T12:00:00Z"
        }
        with open(os.path.join(self.km.lessons_dir, "LSN-MED-002.json"), "w", encoding="utf-8") as f:
            json.dump(lsn2_data, f, indent=2)

        # 5. Exemplar
        exm_data = {
            "contract_version": "1.0.0",
            "exemplar_id": "EXM-MED-001",
            "domain": "mediation",
            "capability": "mediation",
            "task_type": "bootstrap_mediation",
            "why_exemplary": "Complete Chapter 4 mediation table with 3-line borders, decoupled LTR statistics, and explicit BCa confidence intervals.",
            "status": "VALIDATED",
            "created_at": "2026-09-19T12:00:00Z",
            "updated_at": "2026-09-19T12:00:00Z"
        }
        with open(os.path.join(self.km.exemplars_dir, "EXM-MED-001.json"), "w", encoding="utf-8") as f:
            json.dump(exm_data, f, indent=2)

        # 6. Reconciled Contradiction / Rule
        ctd_data = {
            "contract_version": "1.0.0",
            "contradiction_id": "CTD-MED-001",
            "conflict_type": "METHODOLOGY_PARADIGM",
            "description": "Baron & Kenny causal steps vs Preacher & Hayes bootstrap estimation.",
            "applicability_conditions": {
                "condition_for_a": "Baron & Kenny strictly limited to historical pedagogical replication.",
                "condition_for_b": "Preacher & Hayes bootstrap mandated for all empirical graduate dissertations."
            },
            "status": "RESOLVED",
            "capability": "mediation"
        }
        with open(os.path.join(self.km.contradictions_dir, "CTD-MED-001.json"), "w", encoding="utf-8") as f:
            json.dump(ctd_data, f, indent=2)

    # -------------------------------------------------------------------------
    # 1. Deterministic Token Estimator Accuracy Tests
    # -------------------------------------------------------------------------
    def test_01_token_estimator_accuracy(self):
        """Token estimator accurately estimates English, Persian, and formatting tokens."""
        # Empty text
        self.assertEqual(estimate_tokens(""), 0)
        self.assertEqual(estimate_tokens(None), 0)

        # English sentence
        en_text = "Execute Preacher & Hayes bootstrap mediation with 5,000 resamples."
        en_tokens = estimate_tokens(en_text)
        self.assertGreater(en_tokens, 8)
        self.assertLess(en_tokens, 20)

        # Persian academic sentence
        fa_text = "ضرایب مسیر غیرمستقیم با استفاده از روش بوت‌استرپ ۵۰۰۰ نمونه‌ای برآورد گردید."
        fa_tokens = estimate_tokens(fa_text)
        self.assertGreater(fa_tokens, 10)
        self.assertLess(fa_tokens, 35)

        # Markdown table & block formatting
        md_text = """### 🧠 Active Learned Behavioral Context (MEDIATION)
- **Target Capability**: `MEDIATION` | **Task**: `bootstrap_mediation`
#### ⚠️ Critical Anti-Patterns to Avoid:
- **[AP-MED-001] Avoid**: Relying on the normal-theory Sobel test for indirect effects.
"""
        md_tokens = estimate_tokens(md_text)
        self.assertGreater(md_tokens, 25)
        self.assertLess(md_tokens, 100)

    # -------------------------------------------------------------------------
    # 2. Strict Budget Ceiling Enforcement
    # -------------------------------------------------------------------------
    def test_02_strict_budget_ceiling_enforcement(self):
        """Briefing tokens must never exceed the allocated max_token_budget."""
        budgets_to_test = [200, 350, 500, 800, 1200]

        for b in budgets_to_test:
            briefing = self.km.retrieve_pre_task_context(
                capability="mediation",
                task="bootstrap_mediation",
                max_token_budget=b
            )

            telem = briefing.get("budget_telemetry")
            self.assertIsNotNone(telem, f"Budget telemetry missing for budget {b}")
            self.assertEqual(telem["max_token_budget"], b)

            used = telem["estimated_tokens_used"]
            self.assertLessEqual(
                used,
                b,
                f"Briefing token count {used} exceeded max_token_budget {b}"
            )
            self.assertGreater(used, 0)
            self.assertLessEqual(telem["budget_utilization_ratio"], 1.0)

    # -------------------------------------------------------------------------
    # 3. Dual Compression Modes (STANDARD vs COMPACT)
    # -------------------------------------------------------------------------
    def test_03_dual_compression_modes(self):
        """Activates COMPACT mode when budget < 500, STANDARD mode when >= 500."""
        # Tight budget -> COMPACT
        compact_briefing = self.km.retrieve_pre_task_context(
            capability="mediation",
            task="bootstrap_mediation",
            max_token_budget=300
        )
        compact_telem = compact_briefing["budget_telemetry"]
        self.assertEqual(compact_telem["compression_mode"], "COMPACT")
        # In compact mode, exemplars must be omitted to conserve tokens
        self.assertEqual(len(compact_briefing.get("exemplars", [])), 0)

        # Standard budget -> STANDARD
        std_briefing = self.km.retrieve_pre_task_context(
            capability="mediation",
            task="bootstrap_mediation",
            max_token_budget=800
        )
        std_telem = std_briefing["budget_telemetry"]
        self.assertEqual(std_telem["compression_mode"], "STANDARD")

    # -------------------------------------------------------------------------
    # 4. Priority Hierarchy & Floor Invariant
    # -------------------------------------------------------------------------
    def test_04_priority_hierarchy_and_pitfall_floor(self):
        """Under tight budget, Anti-Patterns are prioritized and top pitfall is preserved."""
        # Constrained budget: 200 tokens
        briefing = self.km.retrieve_pre_task_context(
            capability="mediation",
            task="bootstrap_mediation",
            max_token_budget=200
        )
        # Floor invariant: top anti-pattern must be preserved
        anti_patterns = briefing.get("anti_patterns", [])
        self.assertGreaterEqual(len(anti_patterns), 1, "At least 1 anti-pattern must be preserved as safety floor")

        # Telemetry should record pruned items
        telem = briefing["budget_telemetry"]
        self.assertGreaterEqual(telem["items_pruned_by_budget"], 1)
        self.assertGreaterEqual(len(telem["pruned_details"]), 1)

    # -------------------------------------------------------------------------
    # 5. Execution Boundary Integration (Turn vs Subagent Dispatches)
    # -------------------------------------------------------------------------
    def test_05_execution_boundary_integration(self):
        """Boundary engine enforces 800 tokens for turns and 500 tokens for subagents."""
        # Turn pre-flight
        turn_data = self.boundary.retrieve_boundary_context(
            capability="mediation",
            task="bootstrap_mediation",
            max_token_budget=800
        )
        self.assertEqual(turn_data["max_token_budget"], 800)
        self.assertLessEqual(turn_data["budget_telemetry"]["estimated_tokens_used"], 800)

        # Formatted briefing must include budget badge
        formatted = self.boundary.format_boundary_briefing(turn_data)
        self.assertIn("[Budget: ~", formatted)
        self.assertIn("tokens", formatted)

        # Subagent dispatch enrichment
        subagent_spec = [{
            "Role": "Statistical Analyst",
            "TypeName": "statistics-agent",
            "Prompt": "Execute bootstrap mediation for hypothesis 1."
        }]
        enriched = self.boundary.enrich_subagent_dispatch(subagent_spec)
        self.assertEqual(len(enriched), 1)
        sa_prompt = enriched[0]["Prompt"]
        self.assertTrue(enriched[0].get("adaptive_context_bound"))
        self.assertIn("DETERMINISTIC ADAPTIVE CONTEXT", sa_prompt)
        self.assertIn("[Budget: ~", sa_prompt)

    # -------------------------------------------------------------------------
    # 6. CLI Tool --max-tokens Integration
    # -------------------------------------------------------------------------
    def test_06_cli_max_tokens_flag(self):
        """CLI tool retrieve_adaptive_context.py respects --max-tokens parameter."""
        # JSON mode with 350 tokens
        cmd_json = [
            sys.executable,
            self.cli_script,
            "--capability", "mediation",
            "--task", "bootstrap_mediation",
            "--max-tokens", "350",
            "--format", "json",
            "--base-dir", self.test_dir
        ]
        proc_json = subprocess.run(cmd_json, capture_output=True, text=True)
        self.assertEqual(proc_json.returncode, 0, f"CLI json failed: {proc_json.stderr}")
        data = json.loads(proc_json.stdout)
        self.assertIn("budget_telemetry", data)
        self.assertEqual(data["budget_telemetry"]["max_token_budget"], 350)
        self.assertLessEqual(data["budget_telemetry"]["estimated_tokens_used"], 350)

        # Markdown mode
        cmd_md = [
            sys.executable,
            self.cli_script,
            "--capability", "mediation",
            "--task", "bootstrap_mediation",
            "--max-tokens", "800",
            "--format", "markdown",
            "--base-dir", self.test_dir
        ]
        proc_md = subprocess.run(cmd_md, capture_output=True, text=True)
        self.assertEqual(proc_md.returncode, 0, f"CLI md failed: {proc_md.stderr}")
        self.assertIn("Active Learned Behavioral Context (MEDIATION)", proc_md.stdout)
        self.assertIn("[Budget: ~", proc_md.stdout)
        self.assertIn("Budget Telemetry & Quota Audit:", proc_md.stdout)

    # -------------------------------------------------------------------------
    # 7. Directive 18 Ceilings Verification
    # -------------------------------------------------------------------------
    def test_07_directive_18_compliance(self):
        """All implementation files must strictly observe Directive 18 ceilings."""
        files_to_check = [
            os.path.join(ROOT_DIR, ".agents", "scripts", "academic_context_token_budgeter.py"),
            os.path.join(ROOT_DIR, ".agents", "scripts", "academic_adaptive_context_boundary.py"),
            os.path.join(ROOT_DIR, ".agents", "skills", "academic-adaptive-context", "scripts", "retrieve_adaptive_context.py"),
            os.path.join(ROOT_DIR, ".agents", "skills", "academic-adaptive-context", "SKILL.md")
        ]

        for fpath in files_to_check:
            self.assertTrue(os.path.isfile(fpath), f"File {fpath} must exist")
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()

            self.assertLessEqual(
                len(lines), 500,
                f"{os.path.basename(fpath)} exceeds 500 lines limit ({len(lines)} lines)"
            )
            self.assertLessEqual(
                len(content.encode("utf-8")), 40000,
                f"{os.path.basename(fpath)} exceeds 40,000 bytes limit ({len(content.encode('utf-8'))} bytes)"
            )


if __name__ == "__main__":
    unittest.main()
