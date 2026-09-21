#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_agent_role_isolation.py — Unit Tests for Subagent Role Isolation & Context Targeting (Phase 43)

Verifies:
1. Stage 1 Hard Filtering Dimension 8: Agent Role Boundary Gate prunes mismatched specialist items.
2. Zero cross-agent context contamination: statistics-agent does not see academic-writer rules.
3. Role equivalence mappings: data-agent and data-curator share relevant items.
4. Universal item retention: Unbounded or "all" items remain visible across all agents.
5. Orchestrator pipeline-wide oversight: academic-orchestrator bypasses role pruning.
6. Human mentor codification with --agent / target_agent in principles, patterns, anti-patterns, lessons.
7. Natural language target agent detection (English & Persian).
8. Schema validity of knowledge_retrieval contract with agent pruning telemetry.
9. Adaptive context boundary subagent isolation.
"""

import os
import sys
import json
import shutil
import unittest
import tempfile

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

from scripts.academic_two_stage_retriever import AcademicTwoStageRetriever
from scripts.academic_knowledge_manager import AcademicKnowledgeManager
from scripts.academic_human_mentor import AcademicHumanMentor
from scripts.academic_adaptive_context_boundary import AcademicAdaptiveContextBoundary
from contracts.contract_validator import validate_knowledge_retrieval


class TestAgentRoleIsolation(unittest.TestCase):
    """Authoritative test suite for Subagent Role Isolation & Context Targeting."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_role_isolation_")
        self.km = AcademicKnowledgeManager(base_dir=self.test_dir)
        self.retriever = AcademicTwoStageRetriever(base_dir=self.test_dir)
        self.mentor = AcademicHumanMentor(base_dir=self.test_dir)
        self.boundary = AcademicAdaptiveContextBoundary(base_dir=self.test_dir)

    def tearDown(self):
        if os.path.isdir(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_agent_gate_hard_pruning_cross_contamination(self):
        """Specialist items targeting another agent must be fail-closed pruned in Stage 1."""
        items = [
            {
                "lesson_id": "LSN-WRITER-001",
                "desired_behavior": "Enforce strict Persian typography: omit w:jc under w:bidi.",
                "target_agent": "academic-writer",
                "target_agents": ["academic-writer"],
                "status": "VALIDATED",
                "confidence": 0.95
            },
            {
                "lesson_id": "LSN-STATS-001",
                "desired_behavior": "Execute 5,000 bootstrap resamples for Hayes PROCESS Model 4.",
                "target_agent": "statistics-agent",
                "target_agents": ["statistics-agent"],
                "status": "VALIDATED",
                "confidence": 0.95
            },
            {
                "lesson_id": "LSN-UNIV-001",
                "desired_behavior": "Never fabricate or hallucinate empirical numbers.",
                "status": "VALIDATED",
                "confidence": 0.99
            }
        ]

        # Query from statistics-agent perspective
        rec_stats = self.retriever.retrieve(
            items=items,
            query={"agent": "statistics-agent", "task": "run_analysis"}
        )
        val = validate_knowledge_retrieval(rec_stats)
        self.assertTrue(val["valid"], f"Contract validation failed: {val.get('errors')}")

        result_ids = [r["lesson_id"] for r in rec_stats["results"]]
        self.assertIn("LSN-STATS-001", result_ids, "statistics-agent must receive its targeted lesson.")
        self.assertIn("LSN-UNIV-001", result_ids, "statistics-agent must receive universal lessons.")
        self.assertNotIn("LSN-WRITER-001", result_ids, "statistics-agent MUST NOT see academic-writer lessons.")

        # Verify Stage 1 pruning telemetry
        self.assertEqual(rec_stats["stage_1_filtering"]["pruned_count"], 1)
        self.assertEqual(rec_stats["stage_1_filtering"]["pruned_by_dimension"]["agent"], 1)

    def test_02_academic_writer_isolation(self):
        """academic-writer must not receive statistics-agent computation rules."""
        items = [
            {
                "lesson_id": "LSN-WRITER-001",
                "desired_behavior": "Never use manual line breaks inside justified runs.",
                "target_agent": "academic-writer",
                "status": "VALIDATED",
                "confidence": 0.95
            },
            {
                "lesson_id": "LSN-STATS-001",
                "desired_behavior": "Invert covariance matrix using Moore-Penrose pseudoinverse.",
                "target_agent": "statistics-agent",
                "status": "VALIDATED",
                "confidence": 0.95
            }
        ]

        rec = self.retriever.retrieve(
            items=items,
            query={"agent": "academic-writer", "task": "draft_chapter"}
        )
        result_ids = [r["lesson_id"] for r in rec["results"]]
        self.assertIn("LSN-WRITER-001", result_ids)
        self.assertNotIn("LSN-STATS-001", result_ids)
        self.assertEqual(rec["stage_1_filtering"]["pruned_by_dimension"]["agent"], 1)

    def test_03_role_equivalence_matching(self):
        """Equivalent roles (data-agent <-> data-curator) share targeted items."""
        items = [
            {
                "lesson_id": "LSN-DATA-001",
                "desired_behavior": "Reverse code items using 4,880 validated questionnaire library.",
                "target_agent": "data-agent",
                "status": "VALIDATED",
                "confidence": 0.95
            }
        ]

        # Query as data-curator
        rec = self.retriever.retrieve(
            items=items,
            query={"agent": "data-curator", "task": "data_cleaning"}
        )
        result_ids = [r["lesson_id"] for r in rec["results"]]
        self.assertIn("LSN-DATA-001", result_ids, "data-curator must match data-agent targeted items via role equivalence.")
        self.assertEqual(rec["stage_1_filtering"]["pruned_count"], 0)

    def test_04_academic_orchestrator_pipeline_wide_oversight(self):
        """academic-orchestrator has pipeline-wide oversight and bypasses role pruning."""
        items = [
            {
                "lesson_id": "LSN-WRITER-001",
                "desired_behavior": "Use B Nazanin 13pt for Persian body text.",
                "target_agent": "academic-writer",
                "status": "VALIDATED",
                "confidence": 0.95
            },
            {
                "lesson_id": "LSN-STATS-001",
                "desired_behavior": "Report exact p-values to 3 decimal places.",
                "target_agent": "statistics-agent",
                "status": "VALIDATED",
                "confidence": 0.95
            },
            {
                "lesson_id": "LSN-DATA-001",
                "desired_behavior": "Screen univariate outliers using z > 3.29.",
                "target_agent": "data-agent",
                "status": "VALIDATED",
                "confidence": 0.95
            }
        ]

        rec = self.retriever.retrieve(
            items=items,
            query={"agent": "academic-orchestrator", "task": "pipeline_coordination"}
        )
        result_ids = [r["lesson_id"] for r in rec["results"]]
        self.assertIn("LSN-WRITER-001", result_ids)
        self.assertIn("LSN-STATS-001", result_ids)
        self.assertIn("LSN-DATA-001", result_ids)
        self.assertEqual(rec["stage_1_filtering"]["pruned_count"], 0)

    def test_05_human_mentor_teach_persists_agent_role(self):
        """AcademicHumanMentor.teach properly persists target_agent across principles, patterns, anti-patterns, and lessons."""
        # 1. Principle with agent
        p_res = self.mentor.teach(
            category="principle",
            statement="All statistical tables must strictly adhere to APA 7 3-line format.",
            capability="chapter4",
            agent="academic-writer"
        )
        self.assertEqual(p_res["agent"], "academic-writer")
        self.assertIn("- **Target Agent**: `academic-writer`", p_res["badge"])

        saved_p = self.km.get_item(p_res["item_id"])
        self.assertEqual(saved_p.get("target_agent"), "academic-writer")
        self.assertIn("academic-writer", saved_p.get("target_agents", []))
        self.assertIn("academic-writer", saved_p.get("applicability", {}).get("target_agents", []))

        # 2. Anti-pattern with agent
        ap_res = self.mentor.teach(
            category="anti_pattern",
            statement="Never calculate p-values in your head without script execution.",
            capability="mediation",
            agent="statistics-agent",
            defective_pattern="Mental hallucination of statistics",
            corrective_remedy="Execute deterministic script"
        )
        self.assertEqual(ap_res["agent"], "statistics-agent")
        saved_ap = self.km.get_item(ap_res["item_id"])
        self.assertEqual(saved_ap.get("target_agent"), "statistics-agent")
        self.assertIn("statistics-agent", saved_ap.get("target_agents", []))

        # 3. Lesson with agent
        l_res = self.mentor.teach(
            category="lesson",
            statement="Verify Little MCAR test p > .05 before mean imputation.",
            capability="data_cleaning",
            agent="data-agent"
        )
        self.assertEqual(l_res["agent"], "data-agent")
        saved_l = self.km.get_item(l_res["item_id"])
        self.assertEqual(saved_l.get("target_agent"), "data-agent")
        self.assertIn("data-agent", saved_l.get("target_agents", []))

    def test_06_natural_language_agent_detection(self):
        """teach_from_natural_language detects target agents from English and Persian phrasing."""
        # English detection
        res_en = self.mentor.teach_from_natural_language(
            "Remember that for academic-writer, headings must never have manual line breaks",
            scope="cross-project"
        )
        self.assertEqual(res_en.get("agent"), "academic-writer")

        # Persian detection
        res_fa = self.mentor.teach_from_natural_language(
            "یادت باشه برای تحلیلگر آمار همیشه باید فاصله اطمینان بوت‌استرپ ۹۵ درصد گزارش شود",
            scope="cross-project"
        )
        self.assertEqual(res_fa.get("agent"), "statistics-agent")

        # Direct agent name mention
        res_direct = self.mentor.teach_from_natural_language(
            "data-agent must screen straight-lining using variance thresholds",
            scope="cross-project"
        )
        self.assertEqual(res_direct.get("agent"), "data-agent")

    def test_07_adaptive_context_boundary_role_isolation(self):
        """AcademicAdaptiveContextBoundary retrieves role-isolated briefings for subagents."""
        # Populate items targeting different agents
        self.mentor.teach(
            category="principle",
            statement="Headings must omit w:jc under w:bidi in OpenXML documents.",
            capability="chapter4",
            agent="academic-writer"
        )
        self.mentor.teach(
            category="anti_pattern",
            statement="Never report p = .000; report p < .001.",
            capability="chapter4",
            agent="statistics-agent",
            defective_pattern="Reporting p = .000",
            corrective_remedy="Report p < .001"
        )

        # Retrieve for academic-writer
        ctx_writer = self.boundary.retrieve_boundary_context(
            capability="chapter4",
            agent="academic-writer"
        )
        rule_texts = [p.get("mandate", "") + p.get("defect", "") for p in ctx_writer["relevant_lessons"] + ctx_writer["known_pitfalls"]]
        briefing_writer = ctx_writer.get("formatted_briefing", "")
        # writer should not see statistics-agent anti-pattern in its briefing
        self.assertNotIn("p = .000", briefing_writer)

        # Retrieve for statistics-agent
        ctx_stats = self.boundary.retrieve_boundary_context(
            capability="chapter4",
            agent="statistics-agent"
        )
        briefing_stats = ctx_stats.get("formatted_briefing", "")
        # stats agent should see its anti-pattern and NOT writer OpenXML heading rule
        self.assertIn("p = .000", briefing_stats)
        self.assertNotIn("w:bidi", briefing_stats)


if __name__ == "__main__":
    unittest.main()
