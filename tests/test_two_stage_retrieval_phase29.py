#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_two_stage_retrieval_phase29.py — Phase 29 Two-Stage Knowledge Retrieval Unit Tests

Verifies:
1. Stage 1 Hard Filtering: capability, domain, skill, task, failure_type, scope, status.
2. Zero Semantic Leakage: An academically inappropriate lesson is pruned in Stage 1
   regardless of how superficially similar words may appear.
3. Stage 2 Semantic Ranking: Multi-factor scoring across relevance, context_similarity,
   evidence_strength, recency, confidence, and contradiction.
4. Active contradiction penalty vs resolved clean state.
5. Full schema contract compliance against knowledge_retrieval.schema.json.
6. Directive 18 line and byte ceilings for scripts and skills.
"""

import os
import sys
import json
import shutil
import unittest
import tempfile
from datetime import datetime, timezone, timedelta

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
from contracts.contract_validator import validate_knowledge_retrieval


class TestTwoStageRetrievalPhase29(unittest.TestCase):
    """Authoritative test suite for Phase 29 Two-Stage Knowledge Retrieval Architecture."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_phase29_retrieval_")
        self.km = AcademicKnowledgeManager(base_dir=self.test_dir)
        self.retriever = AcademicTwoStageRetriever(base_dir=self.test_dir)

    def tearDown(self):
        if os.path.isdir(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_stage_1_hard_capability_filtering(self):
        """Candidates with conflicting capabilities must be hard-pruned in Stage 1."""
        items = [
            {
                "lesson_id": "LSN-SEM-001",
                "capability": "SEM",
                "desired_behavior": "Evaluate 11 Hu & Bentler goodness-of-fit indices.",
                "scope": "domain",
                "status": "VALIDATED"
            },
            {
                "lesson_id": "LSN-QUAL-001",
                "capability": "qualitative",
                "desired_behavior": "Conduct Braun & Clarke reflexive thematic analysis.",
                "scope": "domain",
                "status": "VALIDATED"
            },
            {
                "lesson_id": "LSN-CROSS-001",
                "desired_behavior": "Report exact p-values to three decimal places.",
                "tags": ["general_academic", "cross-capability"],
                "scope": "cross-project",
                "status": "VALIDATED"
            }
        ]

        query = {"capability": "SEM"}
        passed, meta = self.retriever.stage_1_hard_filter(items, query)
        passed_ids = [p["lesson_id"] for p in passed]

        self.assertIn("LSN-SEM-001", passed_ids)
        self.assertIn("LSN-CROSS-001", passed_ids)
        self.assertNotIn("LSN-QUAL-001", passed_ids, "Disparate capability must be pruned!")
        self.assertEqual(meta["pruned_by_dimension"]["capability"], 1)

    def test_02_stage_1_hard_domain_mutual_exclusion(self):
        """Quantitative and qualitative domains are mutually exclusive in Stage 1."""
        items = [
            {
                "knowledge_id": "PRN-QUANT-001",
                "domain": "quantitative",
                "statement": "Inferential statistics require verifying parametric normality.",
                "scope": "domain",
                "status": "ACCEPTED_ACTIVE"
            },
            {
                "knowledge_id": "PRN-QUAL-001",
                "domain": "qualitative",
                "statement": "Thematic analysis requires iterative reflexive open coding.",
                "scope": "domain",
                "status": "ACCEPTED_ACTIVE"
            }
        ]

        # Query with quantitative domain
        passed_quant, meta_quant = self.retriever.stage_1_hard_filter(items, {"domain": "quantitative"})
        self.assertEqual(len(passed_quant), 1)
        self.assertEqual(passed_quant[0]["knowledge_id"], "PRN-QUANT-001")
        self.assertEqual(meta_quant["pruned_by_dimension"]["domain"], 1)

        # Query with qualitative domain
        passed_qual, meta_qual = self.retriever.stage_1_hard_filter(items, {"domain": "qualitative"})
        self.assertEqual(len(passed_qual), 1)
        self.assertEqual(passed_qual[0]["knowledge_id"], "PRN-QUAL-001")
        self.assertEqual(meta_qual["pruned_by_dimension"]["domain"], 1)

    def test_03_stage_1_hard_skill_and_task_filtering(self):
        """Items incompatible with queried skill or task must be pruned in Stage 1."""
        items = [
            {
                "lesson_id": "LSN-MED-BOOT-001",
                "target_skill": "mediation",
                "task": "bootstrap_mediation",
                "desired_behavior": "Execute 5000 bootstrap resamples with 95% BCa CIs.",
                "scope": "domain",
                "status": "VALIDATED"
            },
            {
                "lesson_id": "LSN-TRANS-001",
                "target_skill": "persian-academic-translation",
                "task": "translate_abstract",
                "desired_behavior": "Translate psychological terms according to Academy standards.",
                "scope": "domain",
                "status": "VALIDATED"
            }
        ]

        query = {"skill": "mediation", "task": "bootstrap_mediation"}
        passed, meta = self.retriever.stage_1_hard_filter(items, query)
        passed_ids = [p["lesson_id"] for p in passed]

        self.assertIn("LSN-MED-BOOT-001", passed_ids)
        self.assertNotIn("LSN-TRANS-001", passed_ids)
        self.assertTrue(meta["pruned_by_dimension"]["skill"] >= 1 or meta["pruned_by_dimension"]["task"] >= 1)

    def test_04_stage_1_hard_scope_containment(self):
        """Project-scoped knowledge items must strictly quarantine to matching project ID."""
        items = [
            {
                "lesson_id": "LSN-PROJ-A",
                "scope": "project",
                "project_id": "Project_A",
                "desired_behavior": "Use specialized covariate scaling for Project A panel.",
                "status": "VALIDATED"
            },
            {
                "lesson_id": "LSN-GLOBAL",
                "scope": "cross-project",
                "desired_behavior": "Always decouple numeric table cells to LTR.",
                "status": "VALIDATED"
            }
        ]

        # Query for Project B
        passed_b, meta_b = self.retriever.stage_1_hard_filter(items, {"project_id": "Project_B"})
        self.assertEqual(len(passed_b), 1)
        self.assertEqual(passed_b[0]["lesson_id"], "LSN-GLOBAL")
        self.assertEqual(meta_b["pruned_by_dimension"]["scope"], 1)

        # Query without project
        passed_none, meta_none = self.retriever.stage_1_hard_filter(items, {})
        self.assertEqual(len(passed_none), 1)
        self.assertEqual(passed_none[0]["lesson_id"], "LSN-GLOBAL")

    def test_05_stage_1_failure_type_filtering(self):
        """Anti-patterns must match the specified failure defect category."""
        items = [
            {
                "anti_pattern_id": "AP-PZERO-001",
                "category": "statistical",
                "failure_type": "reporting_p_zero",
                "defective_pattern": "Reporting p = .000.",
                "status": "ACTIVE"
            },
            {
                "anti_pattern_id": "AP-SLOPE-001",
                "category": "methodological",
                "failure_type": "slope_heterogeneity",
                "defective_pattern": "Ignoring interaction between covariate and group in ANCOVA.",
                "status": "ACTIVE"
            }
        ]

        query = {"failure_type": "reporting_p_zero"}
        passed, meta = self.retriever.stage_1_hard_filter(items, query)
        self.assertEqual(len(passed), 1)
        self.assertEqual(passed[0]["anti_pattern_id"], "AP-PZERO-001")
        self.assertEqual(meta["pruned_by_dimension"]["failure_type"], 1)

    def test_06_semantic_leakage_prevented_core_principle(self):
        """
        CORE ARCHITECTURAL INVARIANT:
        An academically inappropriate lesson with HIGH lexical/word similarity
        must be hard-pruned in Stage 1 and CANNOT leak into Stage 2 ranking.
        """
        # A qualitative lesson engineered with words matching a quantitative SEM task
        deceptive_item = {
            "lesson_id": "LSN-QUAL-DECEPTIVE-001",
            "capability": "qualitative",
            "domain": "qualitative",
            "desired_behavior": "Examine structural equation modeling and regression path models through qualitative reflexive coding.",
            "statement": "Evaluate bootstrap mediation and latent structural model fit with thematic saturation.",
            "scope": "domain",
            "status": "VALIDATED",
            "confidence": 0.99
        }
        legitimate_item = {
            "lesson_id": "LSN-SEM-GENUINE-001",
            "capability": "SEM",
            "domain": "quantitative",
            "desired_behavior": "Report CFI, TLI, and RMSEA fit indices for latent structural equation model.",
            "scope": "domain",
            "status": "VALIDATED",
            "confidence": 0.85
        }

        query = {
            "capability": "SEM",
            "domain": "quantitative",
            "prompt_text": "Examine structural equation modeling and bootstrap mediation path models"
        }

        retrieval_res = self.retriever.retrieve(
            items=[deceptive_item, legitimate_item],
            query=query
        )

        results = retrieval_res["results"]
        result_ids = [r.get("lesson_id") for r in results]

        # Deceptive item must be pruned in Stage 1 despite containing exact query words
        self.assertNotIn("LSN-QUAL-DECEPTIVE-001", result_ids, "Semantic search must NOT leak inappropriate lesson!")
        self.assertIn("LSN-SEM-GENUINE-001", result_ids)
        self.assertEqual(retrieval_res["stage_1_filtering"]["pruned_count"], 1)

    def test_07_stage_2_multi_factor_ranking_breakdown(self):
        """Stage 2 must rank survivors using multi-factor scholarly weights."""
        older_time = (datetime(2026, 9, 19, 0, 0, 0, tzinfo=timezone.utc) - timedelta(days=90)).isoformat()
        newer_time = (datetime(2026, 9, 19, 0, 0, 0, tzinfo=timezone.utc) - timedelta(days=2)).isoformat()

        item_high = {
            "lesson_id": "LSN-HIGH-RANK",
            "capability": "mediation",
            "desired_behavior": "Execute Preacher & Hayes bootstrap mediation with 5000 resamples and 95% BCa CIs.",
            "confidence": 0.95,
            "confidence_evidence": {"evidence_strength": 0.95},
            "created_at": newer_time,
            "tags": ["bootstrap", "mediation", "bca"],
            "status": "VALIDATED",
            "scope": "domain"
        }
        item_low = {
            "lesson_id": "LSN-LOW-RANK",
            "capability": "mediation",
            "desired_behavior": "Check mediation paths.",
            "confidence": 0.40,
            "confidence_evidence": {"evidence_strength": 0.30},
            "created_at": older_time,
            "tags": ["general"],
            "status": "VALIDATED",
            "scope": "domain"
        }

        query = {
            "capability": "mediation",
            "prompt_text": "Run bootstrap mediation with 5000 resamples and BCa intervals",
            "tags": ["bootstrap", "mediation"]
        }

        retrieval_res = self.retriever.retrieve(
            items=[item_low, item_high],
            query=query
        )

        results = retrieval_res["results"]
        self.assertEqual(results[0]["lesson_id"], "LSN-HIGH-RANK")

        scores = retrieval_res["stage_2_ranking"]["candidates_scores"]
        high_score = next(s for s in scores if s["item_id"] == "LSN-HIGH-RANK")
        low_score = next(s for s in scores if s["item_id"] == "LSN-LOW-RANK")

        self.assertGreater(high_score["final_score"], low_score["final_score"])
        self.assertGreater(high_score["confidence_score"], low_score["confidence_score"])
        self.assertGreater(high_score["recency_score"], low_score["recency_score"])

    def test_08_contradiction_penalizes_active_conflicts(self):
        """Active/disputed contradictions must incur deductions in Stage 2 ranking."""
        disputed_item = {
            "lesson_id": "LSN-DISPUTED-001",
            "capability": "longitudinal-analysis",
            "desired_behavior": "Always use Repeated-Measures ANOVA for longitudinal pre-post designs.",
            "confidence": 0.80,
            "status": "VALIDATED",
            "scope": "domain"
        }
        clean_item = {
            "lesson_id": "LSN-CLEAN-001",
            "capability": "longitudinal-analysis",
            "desired_behavior": "Evaluate subject attrition and Mauchly sphericity before RM-ANOVA.",
            "confidence": 0.80,
            "status": "VALIDATED",
            "scope": "domain"
        }

        active_ctds = [
            {
                "contradiction_id": "CTD-001",
                "lesson_a_id": "LSN-DISPUTED-001",
                "status": "CONFLICT_DETECTED"
            }
        ]

        query = {"capability": "longitudinal-analysis"}
        retrieval_res = self.retriever.retrieve(
            items=[disputed_item, clean_item],
            query=query,
            active_contradictions=active_ctds
        )

        scores = retrieval_res["stage_2_ranking"]["candidates_scores"]
        disp_score = next(s for s in scores if s["item_id"] == "LSN-DISPUTED-001")
        clean_score = next(s for s in scores if s["item_id"] == "LSN-CLEAN-001")

        self.assertEqual(disp_score["contradiction_penalty"], 0.35)
        self.assertEqual(clean_score["contradiction_penalty"], 0.0)
        self.assertGreater(clean_score["final_score"], disp_score["final_score"])

    def test_09_full_schema_contract_compliance(self):
        """The complete retrieval payload must pass validation against knowledge_retrieval.schema.json."""
        item = {
            "lesson_id": "LSN-SCHEMA-001",
            "capability": "mediation",
            "desired_behavior": "Standard bootstrap mediation execution.",
            "confidence": 0.85,
            "status": "VALIDATED",
            "scope": "domain"
        }
        res = self.km.retrieve_two_stage(
            capability="mediation",
            prompt_text="Test schema compliance",
            item_types=["lesson"]
        )

        self.assertIn("contract_version", res)
        self.assertEqual(res["contract_version"], "1.0.0")
        self.assertIn("stage_1_filtering", res)
        self.assertIn("stage_2_ranking", res)
        self.assertIn("results", res)

        val = validate_knowledge_retrieval(res)
        self.assertTrue(val["valid"], f"Schema validation errors: {val.get('errors')}")

    def test_10_directive_18_ceilings(self):
        """Retriever engine and SKILL.md must strictly observe Directive 18 line and byte limits."""
        cand = os.path.join(ROOT_DIR, ".agents", "scripts", "academic_two_stage_retriever.py")
        script_path = cand if os.path.isfile(cand) else os.path.join(ROOT_DIR, "scripts", "academic_two_stage_retriever.py")
        skill_path = os.path.join(ROOT_DIR, ".agents", "skills", "academic-adaptive-context", "SKILL.md")

        for p in [script_path, skill_path]:
            with open(p, "r", encoding="utf-8") as f:
                content = f.read()
            lines = content.splitlines()
            self.assertLessEqual(len(lines), 500, f"{p} exceeds 500 lines ({len(lines)} lines)")
            self.assertLessEqual(len(content.encode("utf-8")), 40000, f"{p} exceeds 40,000 bytes ({len(content.encode('utf-8'))} bytes)")


if __name__ == "__main__":
    unittest.main()
