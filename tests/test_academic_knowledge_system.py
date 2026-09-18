#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_knowledge_system.py — Comprehensive Tests for Persistent Knowledge & Skill Memory

Verifies:
1. Directory layout and .gitkeep presence across knowledge categories and capability memories.
2. Storing, validating, and indexing principles, patterns, anti-patterns, and exemplars.
3. Explicit relational graph with 7 relationship types, inverse traversal, and edge indexing.
4. Versioning, lineage, and superseding mechanism.
5. Strict scope containment (project, domain, cross-project, global-in-project).
6. Contradiction management and paradigm dispute tracking.
7. Capability-isolated skill memory accumulation across 8 core capabilities.
8. Multi-criteria retrieval engine and relevance scoring.
9. Pre-task retrieval briefing (lessons + anti-patterns + exemplars + principles).
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.academic_knowledge_manager import (
    AcademicKnowledgeManager,
    ContractValidationError
)


class TestAcademicKnowledgeSystem(unittest.TestCase):
    """Authoritative test suite for the AcademicSuite Persistent Knowledge & Capability Memory System."""

    def setUp(self):
        """Create isolated temporary directory for testing knowledge operations."""
        self.test_dir = tempfile.mkdtemp(prefix="academic_knowledge_test_")
        self.km = AcademicKnowledgeManager(base_dir=self.test_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        if os.path.isdir(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_knowledge_and_skill_memory_directory_layout(self):
        """Verify that all mandated knowledge categories and capability stores are created with .gitkeep."""
        repo_km = AcademicKnowledgeManager(base_dir=ROOT_DIR)

        # Knowledge categories
        self.assertTrue(os.path.isdir(repo_km.lessons_dir))
        self.assertTrue(os.path.isdir(repo_km.patterns_dir))
        self.assertTrue(os.path.isdir(repo_km.anti_patterns_dir))
        self.assertTrue(os.path.isdir(repo_km.principles_dir))
        self.assertTrue(os.path.isdir(repo_km.exemplars_dir))

        # Gitkeeps in repository
        for d in [repo_km.patterns_dir, repo_km.anti_patterns_dir, repo_km.principles_dir, repo_km.exemplars_dir]:
            gk = os.path.join(d, ".gitkeep")
            self.assertTrue(os.path.isfile(gk), f".gitkeep missing in {d}")

        # Canonical capabilities
        for cap in AcademicKnowledgeManager.CANONICAL_CAPABILITIES:
            cap_dir = os.path.join(repo_km.skill_memory_dir, cap)
            self.assertTrue(os.path.isdir(cap_dir), f"Capability directory missing for {cap}")
            gk = os.path.join(cap_dir, ".gitkeep")
            self.assertTrue(os.path.isfile(gk), f".gitkeep missing in capability {cap}")

    def test_02_store_and_validate_all_knowledge_types(self):
        """Verify storing principles, patterns, anti-patterns, and exemplars against contract schemas."""
        # 1. Store Principle
        prn_id = self.km.add_principle({
            "statement": "When testing mediation, indirect effect standard errors must be computed via 5,000 percentile bootstrap resamples.",
            "scope": "domain",
            "domain": "mediation",
            "tags": ["mediation", "bootstrap", "indirect_effect"],
            "applicability": {
                "criteria": ["continuous or categorical mediation", "sample size N >= 50"],
                "target_skills": ["mediation", "sem"]
            }
        })
        self.assertTrue(prn_id.startswith("PRN-"))
        item = self.km.get_item(prn_id)
        self.assertIsNotNone(item)
        self.assertEqual(item["item_type"], "principle")
        self.assertEqual(item["status"], "ACCEPTED_ACTIVE")

        # 2. Store Pattern
        ptr_id = self.km.add_pattern({
            "statement": "Standard Chapter 4 workflow: verify parametric assumptions before reporting ANCOVA test statistics.",
            "scope": "cross-project",
            "tags": ["chapter4", "workflow", "ancova", "assumptions"],
            "applicability": {
                "criteria": ["experimental pre-post design"],
                "target_skills": ["assumption-testing", "chapter-4-writing"]
            }
        })
        self.assertTrue(ptr_id.startswith("PTR-"))
        ptr_item = self.km.get_item(ptr_id)
        self.assertIsNotNone(ptr_item)
        self.assertEqual(ptr_item["item_type"], "pattern")

        # 3. Store Anti-Pattern
        ap_id = self.km.add_anti_pattern({
            "category": "statistical",
            "defective_pattern": "Dichotomizing continuous moderator variables via median split prior to 2x2 ANOVA.",
            "why_defective": "Reduces statistical power by up to 50% and inflates spurious interaction significance.",
            "observed_symptoms": ["Median split performed on Likert scale", "Loss of variance"],
            "corrective_remedy": "Continuous moderation using Hayes PROCESS Model 1 with mean-centering.",
            "detection_heuristic": {
                "trigger_rule": "Check regression syntax for split or dichotomized moderators."
            }
        })
        self.assertTrue(ap_id.startswith("AP-"))
        ap_item = self.km.get_item(ap_id)
        self.assertIsNotNone(ap_item)
        self.assertEqual(ap_item["category"], "statistical")

        # 4. Store Exemplar
        exm_id = self.km.add_exemplar({
            "domain": "mediation",
            "task_type": "bootstrap_mediation",
            "input_specification": {
                "dataset_description": "Cleaned ACT burnout dataset N=120",
                "sample_size": 120,
                "variables": ["ACT_intervention", "psychological_flexibility", "burnout_post"]
            },
            "gold_standard_artifacts": [
                {
                    "path": "deliverables/mediation_table.docx",
                    "sha256": "1566197905886a890378220ad078003a5848aae3d77cb49da330fc614caff3da",
                    "format": "docx"
                }
            ],
            "why_exemplary": "Includes 5,000 BCa bootstrap confidence intervals and decoupled LTR numbers."
        })
        self.assertTrue(exm_id.startswith("EXM-"))
        exm_item = self.km.get_item(exm_id)
        self.assertIsNotNone(exm_item)
        self.assertEqual(exm_item["domain"], "mediation")

        # 5. Rejection on invalid contract
        with self.assertRaises(ContractValidationError):
            self.km.add_anti_pattern({
                "category": "INVALID_CATEGORY_NAME",
                "defective_pattern": "short"
            })

    def test_03_explicit_relationship_graph(self):
        """Verify the 7 mandatory relationship types, edge indexing, and inverse relationships."""
        prn_id = self.km.add_principle({
            "statement": "Homogeneity of regression slopes is a strict prerequisite for ANCOVA validity.",
            "scope": "domain"
        })
        ap_id = self.km.add_anti_pattern({
            "category": "methodological",
            "defective_pattern": "Executing ANCOVA when Treatment x Pre-test covariate interaction is significant.",
            "why_defective": "Violates regression slope parallelism, invalidating adjusted group means.",
            "observed_symptoms": ["Interaction term Group x Covariate has p < .05"],
            "corrective_remedy": "Use Johnson-Neyman floodlight probing or repeated measures ANOVA.",
            "detection_heuristic": {"trigger_rule": "Homogeneity of slopes test p < .05"}
        })

        # Link AP caused_by PRN violation
        linked = self.km.link_items(ap_id, prn_id, "caused_by", "Slope violation invalidates ANCOVA premise")
        self.assertTrue(linked)

        # Retrieve outgoing and incoming
        out_rels = self.km.get_relationships(ap_id)
        self.assertTrue(any(r["related_id"] == prn_id and r["relation_type"] == "caused_by" for r in out_rels))

        in_rels = self.km.get_relationships(prn_id)
        self.assertTrue(any(r["related_id"] == ap_id and r["relation_type"] == "causes" for r in in_rels))

        # Test invalid relationship rejected
        with self.assertRaises(ValueError):
            self.km.link_items(prn_id, ap_id, "INVALID_RELATION_NAME")

    def test_04_versioning_and_superseding(self):
        """Verify updating knowledge produces new version, sets SUPERSEDED status, and maintains lineage."""
        old_id = self.km.add_principle({
            "statement": "Baron & Kenny causal steps method should be evaluated for mediation testing.",
            "scope": "domain",
            "version": "1.0.0"
        })
        old_item = self.km.get_item(old_id)
        self.assertEqual(old_item["status"], "ACCEPTED_ACTIVE")

        # Supersede with Hayes bootstrap
        new_id = self.km.supersede_item(
            old_id=old_id,
            new_item_data={
                "statement": "Hayes PROCESS bootstrap mediation supersedes Baron & Kenny causal steps.",
                "scope": "domain",
                "item_type": "principle"
            },
            rationale="Baron & Kenny exhibits severe Type II power loss and fails to test ab directly."
        )

        # Check old item is SUPERSEDED
        updated_old = self.km.get_item(old_id)
        self.assertEqual(updated_old["status"], "SUPERSEDED")

        # Check new item version
        new_item = self.km.get_item(new_id)
        self.assertEqual(new_item["status"], "ACCEPTED_ACTIVE")
        self.assertEqual(new_item["version"], "1.1.0")

        # Check graph relationships
        rels = self.km.get_relationships(new_id)
        self.assertTrue(any(r["related_id"] == old_id and r["relation_type"] == "supersedes" for r in rels))

    def test_05_scope_containment_and_quarantine(self):
        """Verify that project-specific knowledge never leaks to queries from other projects."""
        proj_prn_id = self.km.add_principle({
            "statement": "In Project Study_ACT, variable flex_tot must be transformed via log10 due to skewness.",
            "scope": "project",
            "project_id": "study_act_burnout"
        })
        cross_prn_id = self.km.add_principle({
            "statement": "Across all projects, skewness exceeding |2.0| warrants non-parametric or robust estimators.",
            "scope": "cross-project"
        })

        # 1. Query within target project -> both items retrieved
        res_matching = self.km.query(project_id="study_act_burnout")
        ids_matching = [r.get("knowledge_id") for r in res_matching]
        self.assertIn(proj_prn_id, ids_matching)
        self.assertIn(cross_prn_id, ids_matching)

        # 2. Query from different project -> project-specific item is quarantined
        res_other = self.km.query(project_id="other_project_cbt")
        ids_other = [r.get("knowledge_id") for r in res_other]
        self.assertNotIn(proj_prn_id, ids_other, "Project-specific rule must NOT leak to another project!")
        self.assertIn(cross_prn_id, ids_other)

        # 3. Query without project -> project-specific item is quarantined
        res_none = self.km.query(project_id=None)
        ids_none = [r.get("knowledge_id") for r in res_none]
        self.assertNotIn(proj_prn_id, ids_none, "Project-specific rule must NOT leak into un-scoped query!")
        self.assertIn(cross_prn_id, ids_none)

    def test_06_contradiction_management(self):
        """Verify representation and retrieval of competing paradigms via contradicts links."""
        p1_id = self.km.add_principle({
            "statement": "Modern mediation requires bootstrap confidence intervals of the indirect effect ab.",
            "scope": "domain",
            "contradictions": [
                {
                    "competing_approach": "Baron & Kenny (1986) 4-step regression approach",
                    "rejection_rationale": "High Type II error rate; does not directly test ab product distribution."
                }
            ]
        })
        p2_id = self.km.add_principle({
            "statement": "Legacy Baron & Kenny regression method requires significant step 1 (c path).",
            "scope": "domain"
        })

        self.km.link_items(p1_id, p2_id, "contradicts", "Methodological paradigm contradiction")

        contras = self.km.get_contradictions(p1_id)
        self.assertTrue(len(contras) >= 2)
        has_internal = any(c.get("type") == "internal_paradigm_rejection" for c in contras)
        has_relational = any(c.get("type") == "relational_contradiction" and c.get("related_id") == p2_id for c in contras)
        self.assertTrue(has_internal)
        self.assertTrue(has_relational)

    def test_07_capability_skill_memory_accumulation(self):
        """Verify capability-isolated skill memory accumulation across 8 core capabilities."""
        # 1. Record events for mediation capability
        self.km.record_capability_event("mediation", "successful_examples", {"exemplar_id": "EXM-MED-001"})
        self.km.record_capability_event("mediation", "lessons", "LSN-MED-001")
        self.km.record_capability_event("mediation", "anti_patterns", "AP-STAT-MEDIAN-SPLIT-001")
        self.km.record_capability_event("mediation", "failures", {
            "experience_id": "EXP-MED-002",
            "defect_type": "BOOTSTRAP_FAILURE",
            "summary": "Sample size under 30 caused non-convergence."
        })

        med_mem = self.km.get_capability_memory("mediation")
        self.assertIsNotNone(med_mem)
        self.assertEqual(med_mem["capability"], "mediation")
        self.assertEqual(med_mem["success_count"], 1)
        self.assertEqual(med_mem["failure_count"], 1)
        self.assertEqual(med_mem["total_invocations"], 4)
        self.assertIn("LSN-MED-001", med_mem["lessons"])
        self.assertIn("AP-STAT-MEDIAN-SPLIT-001", med_mem["anti_patterns"])

        # 2. Check SEM capability remains isolated
        sem_mem = self.km.get_capability_memory("SEM")
        self.assertIsNone(sem_mem, "SEM capability memory must be empty before any events are recorded")

        # Record event for SEM
        self.km.record_capability_event("SEM", "successful_examples", {"exemplar_id": "EXM-SEM-001"})
        sem_mem_updated = self.km.get_capability_memory("SEM")
        self.assertIsNotNone(sem_mem_updated)
        self.assertEqual(sem_mem_updated["success_count"], 1)
        self.assertEqual(len(sem_mem_updated["lessons"]), 0, "SEM must not inherit mediation lessons")

    def test_08_multi_criteria_query_and_relevance_ranking(self):
        """Verify query rankings prioritize exact capability, skill, task, and tag matches."""
        # Add high relevance item
        high_id = self.km.add_principle({
            "statement": "Bootstrap mediation requires 5,000 resamples for percentile BCa confidence intervals.",
            "scope": "domain",
            "domain": "mediation",
            "tags": ["mediation", "bootstrap", "process"],
            "applicability": {
                "criteria": ["mediation analysis"],
                "target_skills": ["mediation"]
            }
        })
        # Add low relevance item
        low_id = self.km.add_principle({
            "statement": "Qualitative thematic analysis requires 6 phases per Braun & Clarke.",
            "scope": "domain",
            "domain": "qualitative",
            "tags": ["qualitative", "themes"],
            "applicability": {
                "criteria": ["thematic analysis"],
                "target_skills": ["qualitative-data-analyst"]
            }
        })

        results = self.km.query(
            capability="mediation",
            skill="mediation",
            tags=["bootstrap"]
        )
        self.assertTrue(len(results) >= 1)
        self.assertEqual(results[0]["knowledge_id"], high_id)

    def test_09_pre_task_context_retrieval(self):
        """Verify pre-task context retrieval bundles lessons, anti-patterns, exemplars, and principles."""
        # Seed knowledge
        self.km.add_principle({
            "statement": "Always test normality, linearity, and multicollinearity before estimating mediation models.",
            "scope": "cross-project",
            "domain": "mediation",
            "tags": ["mediation", "assumptions"]
        })
        self.km.add_anti_pattern({
            "category": "statistical",
            "defective_pattern": "Assuming indirect effect is normally distributed and reporting Sobel z-test.",
            "why_defective": "Indirect effect ab is a product of two distributions and heavily non-normal.",
            "observed_symptoms": ["Reporting Sobel test z p-value in small samples"],
            "corrective_remedy": "Report Preacher & Hayes bootstrap 95% BCa intervals.",
            "detection_heuristic": {"trigger_rule": "Sobel test in mediation report"}
        })
        self.km.add_exemplar({
            "domain": "mediation",
            "task_type": "bootstrap_mediation",
            "input_specification": {
                "dataset_description": "Mock research panel N=150",
                "sample_size": 150,
                "variables": ["X", "M", "Y"]
            },
            "gold_standard_artifacts": [
                {
                    "path": "evals/mediation/gold.docx",
                    "sha256": "1566197905886a890378220ad078003a5848aae3d77cb49da330fc614caff3da",
                    "format": "docx"
                }
            ],
            "why_exemplary": "Complete APA 7 reporting with bootstrap BCa intervals."
        })
        self.km.record_capability_event("mediation", "successful_examples", {"exemplar_id": "EXM-001"})

        # Retrieve briefing
        briefing = self.km.retrieve_pre_task_context(
            task="bootstrap_mediation",
            capability="mediation",
            skill="mediation",
            tags=["mediation", "bootstrap"]
        )

        self.assertIn("query_context", briefing)
        self.assertEqual(briefing["query_context"]["capability"], "mediation")
        self.assertIn("principles", briefing)
        self.assertIn("anti_patterns", briefing)
        self.assertIn("exemplars", briefing)
        self.assertIn("capability_summary", briefing)

        self.assertTrue(len(briefing["principles"]) >= 1)
        self.assertTrue(len(briefing["anti_patterns"]) >= 1)
        self.assertTrue(len(briefing["exemplars"]) >= 1)
        self.assertEqual(briefing["capability_summary"]["total_invocations"], 1)


if __name__ == "__main__":
    unittest.main()
