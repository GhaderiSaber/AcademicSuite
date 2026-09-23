#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_subagent_context_enrichment.py — Verification of Subagent Context Enrichment & Hook Bridge

Tests:
1. AcademicAdaptiveContextBoundary.enrich_subagent_dispatch injects both lessons and anti-patterns.
2. Token budgeter balances lessons and anti-patterns without squeezing lessons to zero.
3. Stringified JSON argument handling and idempotent double-enrichment prevention.
4. LearningHooks PreToolUse interceptor outputs valid overwrite payload.
5. HookDispatcher propagates overwrite payload to Antigravity runtime.
"""

import os
import sys
import json
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
for p in [ROOT_DIR, AGENTS_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from scripts.academic_adaptive_context_boundary import AcademicAdaptiveContextBoundary
from scripts.academic_context_token_budgeter import AcademicContextTokenBudgeter
from hooks.learning_hooks import LearningHooks
from hooks.hook_dispatcher import dispatch_event


class TestSubagentContextEnrichment(unittest.TestCase):
    """Authoritative test suite for subagent context enrichment at the dispatch boundary."""

    def setUp(self):
        self.boundary = AcademicAdaptiveContextBoundary()
        self.learning_hooks = LearningHooks()

    def test_01_academic_writer_enrichment_contains_lessons_and_pitfalls(self):
        """Dispatched academic-writer must receive both active lessons and anti-patterns."""
        subagents = [{
            "TypeName": "academic-writer",
            "Role": "Master Academic Writer",
            "Prompt": (
                "### Contractual Delegation Envelope\n"
                "- **Worker Agent**: academic-writer\n"
                "- **Objective**: Draft Chapter 4 regression findings and APA tables\n"
                "- **Verification Method**: validation-agent\n"
            )
        }]
        enriched = self.boundary.enrich_subagent_dispatch(subagents)
        self.assertEqual(len(enriched), 1)
        prompt = enriched[0]["Prompt"]

        self.assertIn("🧠 DETERMINISTIC ADAPTIVE CONTEXT", prompt)
        self.assertIn("⚠️ Known Pitfalls (Anti-Patterns to Avoid):", prompt)
        self.assertIn("💡 Relevant Active Lessons:", prompt)
        # Verify that lessons were actually retrieved rather than falling back to empty message
        self.assertNotIn("- No specialized lessons flagged. Standard pipeline rules apply.", prompt)
        self.assertIn("### Executable Task Assignment:", prompt)

    def test_02_statistics_agent_enrichment_contains_sem_lessons(self):
        """Dispatched statistics-agent for SEM must receive lavaan/SEM active lessons."""
        subagents = [{
            "TypeName": "statistics-agent",
            "Role": "Inferential Modeling Specialist",
            "Prompt": (
                "### Contractual Delegation Envelope\n"
                "- **Worker Agent**: statistics-agent\n"
                "- **Objective**: Run SEM structural equation modeling in R\n"
                "- **Verification Method**: statistical-auditor\n"
            )
        }]
        enriched = self.boundary.enrich_subagent_dispatch(subagents)
        self.assertEqual(len(enriched), 1)
        prompt = enriched[0]["Prompt"]

        self.assertIn("🧠 DETERMINISTIC ADAPTIVE CONTEXT", prompt)
        self.assertIn("Target Capability**: `SEM`", prompt)
        self.assertIn("💡 Relevant Active Lessons:", prompt)
        self.assertNotIn("- No specialized lessons flagged. Standard pipeline rules apply.", prompt)

    def test_03_validation_agent_enrichment(self):
        """Dispatched validation-agent must receive forensic table and audit context."""
        subagents = [{
            "TypeName": "validation-agent",
            "Role": "Independent Quality Assurance",
            "Prompt": (
                "### Contractual Delegation Envelope\n"
                "- **Worker Agent**: validation-agent\n"
                "- **Objective**: Audit Chapter 4 tables and check APA 7 compliance\n"
            )
        }]
        enriched = self.boundary.enrich_subagent_dispatch(subagents)
        self.assertEqual(len(enriched), 1)
        prompt = enriched[0]["Prompt"]

        self.assertIn("🧠 DETERMINISTIC ADAPTIVE CONTEXT", prompt)
        self.assertIn("💡 Relevant Active Lessons:", prompt)
        self.assertNotIn("- No specialized lessons flagged. Standard pipeline rules apply.", prompt)

    def test_04_stringified_json_arguments_handling(self):
        """Subagents passed as stringified JSON must be parsed and correctly enriched."""
        subagents_json = json.dumps([{
            "TypeName": "academic-writer",
            "Role": "Drafter",
            "Prompt": "Draft discussion for hypothesis 1"
        }])
        enriched = self.boundary.enrich_subagent_dispatch(subagents_json)
        self.assertIsInstance(enriched, str)
        parsed = json.loads(enriched)
        self.assertEqual(len(parsed), 1)
        self.assertIn("🧠 DETERMINISTIC ADAPTIVE CONTEXT", parsed[0]["Prompt"])

    def test_05_idempotent_enrichment_prevents_duplicate_headers(self):
        """Enriching an already enriched subagent prompt must not duplicate context."""
        subagents = [{
            "TypeName": "academic-writer",
            "Role": "Drafter",
            "Prompt": "Initial task prompt"
        }]
        first_pass = self.boundary.enrich_subagent_dispatch(subagents)
        second_pass = self.boundary.enrich_subagent_dispatch(first_pass)

        header = "🧠 DETERMINISTIC ADAPTIVE CONTEXT"
        self.assertEqual(second_pass[0]["Prompt"].count(header), 1)

    def test_06_learning_hooks_pre_tool_use_intercepts_invoke_subagent(self):
        """LearningHooks.handle_pre_tool_use must output allow decision with overwrite payload."""
        payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [{
                        "TypeName": "academic-writer",
                        "Role": "Writer",
                        "Prompt": "### Contractual Delegation Envelope\n- **Worker Agent**: academic-writer\n"
                    }]
                }
            },
            "agent_role": "academic-orchestrator"
        }
        res = self.learning_hooks.handle_pre_tool_use(payload)
        self.assertIsNotNone(res)
        self.assertEqual(res.get("decision"), "allow")
        self.assertIn("overwrite", res)
        self.assertIn("Subagents", res["overwrite"])

        enriched_subagents = res["overwrite"]["Subagents"]
        self.assertIn("🧠 DETERMINISTIC ADAPTIVE CONTEXT", enriched_subagents[0]["Prompt"])

    def test_07_hook_dispatcher_propagates_overwrite(self):
        """dispatch_event('PreToolUse') must propagate overwrite payload."""
        payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [{
                        "TypeName": "statistics-agent",
                        "Role": "Stats",
                        "Prompt": "Execute regression analysis"
                    }]
                }
            },
            "agent_role": "academic-orchestrator"
        }
        res = dispatch_event("PreToolUse", payload)
        self.assertIsNotNone(res)
        self.assertEqual(res.get("decision"), "allow")
        self.assertIn("overwrite", res)
        self.assertIn("Subagents", res["overwrite"])
        self.assertIn("🧠 DETERMINISTIC ADAPTIVE CONTEXT", res["overwrite"]["Subagents"][0]["Prompt"])

    def test_08_token_budgeter_preserves_both_categories(self):
        """Token budgeter knapsack and fair trimming must maintain lessons and anti-patterns."""
        budgeter = AcademicContextTokenBudgeter(default_budget=600)
        raw_context = {
            "lessons": [
                {"lesson_id": "LSN-TEST-1", "desired_behavior": "Enforce strict APA 7 headers", "generalization": "Always use APA headers", "confidence": 0.95},
                {"lesson_id": "LSN-TEST-2", "desired_behavior": "Enforce Persian leading zeros", "generalization": "Always keep zero", "confidence": 0.90}
            ],
            "anti_patterns": [
                {"anti_pattern_id": "AP-TEST-1", "defect": "Using clumsy Persian headers", "remedy": "Use standard Latin symbols", "confidence": 0.95},
                {"anti_pattern_id": "AP-TEST-2", "defect": "Omitting criterion column", "remedy": "Add criterion column", "confidence": 0.92},
                {"anti_pattern_id": "AP-TEST-3", "defect": "Verbose ANOVA labels", "remedy": "Simplify row labels", "confidence": 0.88}
            ],
            "contradictions": [],
            "exemplars": []
        }
        budgeted = budgeter.budget_context(
            raw_context=raw_context,
            max_token_budget=600,
            target_capability="CHAPTER4",
            task="chapter_4_drafting",
            agent="academic-writer"
        )
        self.assertGreaterEqual(len(budgeted["relevant_lessons"]), 1)
        self.assertGreaterEqual(len(budgeted["known_pitfalls"]), 1)
        self.assertLessEqual(budgeted["budget_telemetry"]["estimated_tokens_used"], 600)


if __name__ == "__main__":
    unittest.main()
