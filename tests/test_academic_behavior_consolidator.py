#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_behavior_consolidator.py — Unit Tests for Periodic Behavioral Consolidator

Verifies:
1. Active lesson ingestion strictly filters out SUPERSEDED, RETIRED_OBSOLETE, and REJECTED lessons.
2. Duplicate detection identifies and clusters repeated or semantically equivalent lessons.
3. Contradiction detection identifies methodological tensions, NEVER silently overwrites,
   and generates validated Contradiction Records with contextual applicability conditions.
4. Generalization elevates empirical lessons to DOMAIN_WIDE / CROSS_PROJECT_UNIVERSAL scope.
5. Merging preserves strict provenance lineage (merged <- source lessons <- experiences <- evaluations)
   and transitions sources to SUPERSEDED.
6. Obsolete lesson detection transitions superseded/absorbed lessons to RETIRED_OBSOLETE with audit reasons.
7. Canonical skill update creates rollback snapshots and strictly enforces Directive 18 ceilings (< 500 lines).
8. Active learning context remains bounded, deduplicated, and conflict-free in downstream retrieval.
"""

import os
import sys
import json
import uuid
import shutil
import tempfile
import unittest
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.academic_behavior_consolidator import AcademicBehaviorConsolidator
from scripts.academic_knowledge_manager import AcademicKnowledgeManager
from contracts.contract_validator import validate_contradiction_record, validate_lesson


class TestAcademicBehaviorConsolidator(unittest.TestCase):
    """Authoritative test suite for the Academic Behavior Consolidator."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_consolidator_test_")
        self.consolidator = AcademicBehaviorConsolidator(base_dir=self.temp_dir)
        self.km = self.consolidator.knowledge_manager

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_sample_lesson(
        self,
        lesson_id: str,
        desired_behavior: str,
        status: str = "VALIDATED",
        source_exp: str = "EXP-001",
        skills: list = None,
        applicability: list = None,
        exclusions: list = None
    ) -> dict:
        """Helper to create and write a valid lesson to disk."""
        lesson = {
            "contract_version": "1.0.0",
            "lesson_id": lesson_id,
            "lesson_type": "WHAT_NOT_TO_DO",
            "trigger_source": "USER_FEEDBACK",
            "source_experience_id": source_exp,
            "diagnosis": {
                "what_happened": f"Defect in {lesson_id}",
                "behavior_caused_outcome": "Agent omitted check",
                "what_should_have_happened": desired_behavior,
                "rationale_why": "Rigorous standards"
            },
            "applicability_conditions": applicability or ["Empirical quantitative analysis"],
            "exclusions": exclusions or ["Exploratory informal notes"],
            "desired_behavior": desired_behavior,
            "generalization": desired_behavior,
            "scope": "PROJECT_SPECIFIC",
            "confidence": 0.92,
            "evidence": {
                "metric_or_check": "CHECK_PASSED",
                "observed_value": "Failure observed",
                "threshold_value": "Zero errors",
                "supporting_report_ids": ["EVAL-001"],
                "supporting_artifact_paths": []
            },
            "related_skills": skills or ["statistical-data-analyst"],
            "is_active_behavior": True,
            "status": status,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        val = validate_lesson(lesson)
        if not val["valid"]:
            raise ValueError(f"Invalid mock lesson {lesson_id}: {val.get('errors')}")

        fp = os.path.join(self.consolidator.lessons_dir, f"{lesson_id}.json")
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(lesson, f, indent=2, ensure_ascii=False)
        return lesson

    # -------------------------------------------------------------------------
    # Test 1: Ingestion Filter
    # -------------------------------------------------------------------------
    def test_01_ingest_active_lessons_filters_superseded_and_retired(self):
        """Verifies superseded, retired, and rejected lessons are excluded from active set."""
        l1 = self._create_sample_lesson("LSN-001", "Always verify Mauchly sphericity.", status="VALIDATED")
        l2 = self._create_sample_lesson("LSN-002", "Legacy sphericity rule.", status="SUPERSEDED")
        l3 = self._create_sample_lesson("LSN-003", "Obsolete formatting rule.", status="RETIRED_OBSOLETE")
        l4 = self._create_sample_lesson("LSN-004", "Rejected rule.", status="REJECTED")

        active = self.consolidator.ingest_active_lessons()
        active_ids = [l["lesson_id"] for l in active]

        self.assertIn("LSN-001", active_ids)
        self.assertNotIn("LSN-002", active_ids)
        self.assertNotIn("LSN-003", active_ids)
        self.assertNotIn("LSN-004", active_ids)
        self.assertEqual(len(active), 1)

    # -------------------------------------------------------------------------
    # Test 2: Duplicate Detection
    # -------------------------------------------------------------------------
    def test_02_duplicate_detection_groups_identical_and_near_duplicate_lessons(self):
        """Verifies duplicate / near-duplicate lessons are clustered together."""
        l1 = self._create_sample_lesson(
            "LSN-DUP-01",
            "Always report degrees of freedom and exact test statistics for all ANOVA models."
        )
        l2 = self._create_sample_lesson(
            "LSN-DUP-02",
            "Always report degrees of freedom and test statistics for ANOVA analyses."
        )
        l3 = self._create_sample_lesson(
            "LSN-DISTINCT-01",
            "Apply Little MCAR test before running structural equation models."
        )

        clusters = self.consolidator.detect_duplicates([l1, l2, l3], similarity_threshold=0.50)
        self.assertEqual(len(clusters), 1)
        clustered_ids = [l["lesson_id"] for l in clusters[0]["lessons"]]
        self.assertIn("LSN-DUP-01", clustered_ids)
        self.assertIn("LSN-DUP-02", clustered_ids)
        self.assertNotIn("LSN-DISTINCT-01", clustered_ids)

    # -------------------------------------------------------------------------
    # Test 3: Contradiction Detection & Non-Overwriting Reconciliation
    # -------------------------------------------------------------------------
    def test_03_contradiction_detection_creates_reconciliation_record_and_never_overwrites(self):
        """
        Verifies that contradictory lessons (RM-ANOVA vs LMM) are detected,
        NEVER silently overwritten, and generate a validated Contradiction Record
        with explicit applicability conditions.
        """
        l_rm = self._create_sample_lesson(
            "LSN-RM-01",
            "For longitudinal repeated measurements, always execute repeated-measures ANOVA assuming sphericity."
        )
        l_lmm = self._create_sample_lesson(
            "LSN-LMM-01",
            "For longitudinal repeated measurements, use linear mixed models LMM instead of repeated-measures ANOVA."
        )

        contradictions = self.consolidator.detect_contradictions([l_rm, l_lmm], record_to_disk=True)
        self.assertEqual(len(contradictions), 1)

        ctd = contradictions[0]
        self.assertEqual(ctd["conflict_type"], "MODEL_SPECIFICATION_CONFLICT")
        # Phase 27: Initial stage is strictly CONFLICT_DETECTED (never auto-resolved)
        self.assertEqual(ctd["stage"], "CONFLICT_DETECTED")
        self.assertEqual(ctd["status"], "CONFLICT_DETECTED")

        # Now advance through the 6-stage lifecycle via reconcile_contradiction_pipeline
        resolved_ctd = self.consolidator.reconcile_contradiction_pipeline(
            contradiction_id=ctd["contradiction_id"],
            assumptions_a=["Assumes sphericity", "Requires balanced complete designs without missing waves"],
            assumptions_b=["Robust to sphericity violations", "Accommodates missing at random data and unequal intervals"],
            root_cause="Different statistical trade-offs: RM-ANOVA is exact for balanced data; LMM handles unbalanced longitudinal data",
            evidence_for_a=["Kirk (2013) Experimental Design", "Tabachnick & Fidell (2019)"],
            evidence_for_b=["Gelman & Hill (2006)", "Singer & Willett (2003)"],
            condition_for_a="Complete cases, strict sphericity (Mauchly p > .05), balanced repeated intervals",
            condition_for_b="Missing waves, severe sphericity violation (epsilon < .75), unbalanced observations",
            test_result={
                "test_suite_id": "TEST-METHODOLOGY-RM-LMM-01",
                "independent_verdict": "PASS",
                "evaluator": "AcademicIndependentEvaluator"
            }
        )

        self.assertEqual(resolved_ctd["stage"], "RESOLVED")
        self.assertEqual(resolved_ctd["status"], "RESOLVED")
        self.assertEqual(resolved_ctd["reconciliation_strategy"], "CONTEXTUAL_DISAMBIGUATION")
        self.assertIn("condition_for_a", resolved_ctd["applicability_conditions"])
        self.assertIn("condition_for_b", resolved_ctd["applicability_conditions"])

        # Verify neither file was overwritten
        with open(os.path.join(self.consolidator.lessons_dir, "LSN-RM-01.json"), "r", encoding="utf-8") as f:
            data_rm = json.load(f)
        with open(os.path.join(self.consolidator.lessons_dir, "LSN-LMM-01.json"), "r", encoding="utf-8") as f:
            data_lmm = json.load(f)

        self.assertEqual(data_rm["lesson_id"], "LSN-RM-01")
        self.assertEqual(data_lmm["lesson_id"], "LSN-LMM-01")

        # Verify contradiction record saved to disk and valid
        ctd_file = os.path.join(self.consolidator.contradictions_dir, f"{ctd['contradiction_id']}.json")
        self.assertTrue(os.path.isfile(ctd_file))
        val_res = validate_contradiction_record(resolved_ctd)
        self.assertTrue(val_res["valid"])

    # -------------------------------------------------------------------------
    # Test 4: Generalization Scope Elevation
    # -------------------------------------------------------------------------
    def test_04_generalization_elevates_scope_with_evidence(self):
        """Verifies multi-experience clusters form GENERALIZATION_CANDIDATE, and require heterogeneous validation for universal."""
        l1 = self._create_sample_lesson("LSN-GEN-01", "Report confidence intervals for effect sizes.", source_exp="EXP-A")
        l2 = self._create_sample_lesson("LSN-GEN-02", "Report confidence intervals for effect sizes.", source_exp="EXP-B")

        # 2 experiences in local context form GENERALIZATION_CANDIDATE (never premature universal)
        gen_result = self.consolidator.generalize_lessons([l1, l2])
        self.assertEqual(gen_result["scope"], "DOMAIN_WIDE")
        self.assertEqual(gen_result["generalization_stage"], "GENERALIZATION_CANDIDATE")
        self.assertIn("Consolidated Methodological Principle", gen_result["statement"])
        # Phase 26: Candidate has evidence-derived confidence based on unvalidated prior
        self.assertIn("confidence_evidence", gen_result)
        self.assertGreater(gen_result["confidence"], 0.05)

        # With heterogeneous cross-context and cross-domain validation, elevates to CROSS_PROJECT_UNIVERSAL
        ctx_evals = [
            {"context_id": "C1", "design": "2_group_rct", "verdict": "PASS"},
            {"context_id": "C2", "design": "3_group_factorial", "verdict": "PASS"}
        ]
        dom_evals = [
            {"domain": "clinical_trials", "verdict": "PASS"},
            {"domain": "psychometrics", "verdict": "PASS"}
        ]
        gen_promoted = self.consolidator.generalize_lessons([l1, l2], context_evaluations=ctx_evals, domain_evaluations=dom_evals)
        self.assertEqual(gen_promoted["scope"], "CROSS_PROJECT_UNIVERSAL")
        self.assertEqual(gen_promoted["generalization_stage"], "PROMOTED_PRINCIPLE")
        # Evidence-derived confidence reaches high levels with empirical validation
        self.assertGreater(gen_promoted["confidence"], 0.80)
        self.assertGreater(gen_promoted["confidence"], gen_result["confidence"])

    # -------------------------------------------------------------------------
    # Test 5: Merging with Strict Provenance Lineage
    # -------------------------------------------------------------------------
    def test_05_merge_lessons_preserves_strict_provenance_lineage(self):
        """Verifies merged lesson retains provenance pointers and marks sources as SUPERSEDED."""
        l1 = self._create_sample_lesson("LSN-SRC-01", "Verify Levene test for equality of variance.", source_exp="EXP-01")
        l2 = self._create_sample_lesson("LSN-SRC-02", "Check Levene variance homogeneity before ANOVA.", source_exp="EXP-02")

        merged = self.consolidator.merge_lessons([l1, l2], dry_run=False)

        self.assertTrue(merged["lesson_id"].startswith("LSN-CONSOLIDATED-"))
        prov = merged.get("provenance", {})
        self.assertEqual(prov["source_lessons"], ["LSN-SRC-01", "LSN-SRC-02"])
        self.assertEqual(prov["source_experiences"], ["EXP-01", "EXP-02"])

        # Check sources are updated to SUPERSEDED on disk
        with open(os.path.join(self.consolidator.lessons_dir, "LSN-SRC-01.json"), "r", encoding="utf-8") as f:
            src1 = json.load(f)
        with open(os.path.join(self.consolidator.lessons_dir, "LSN-SRC-02.json"), "r", encoding="utf-8") as f:
            src2 = json.load(f)

        self.assertEqual(src1["status"], "SUPERSEDED")
        self.assertEqual(src1["superseded_by"], merged["lesson_id"])
        self.assertEqual(src2["status"], "SUPERSEDED")
        self.assertEqual(src2["superseded_by"], merged["lesson_id"])

    # -------------------------------------------------------------------------
    # Test 6: Obsolete Lesson Detection & Retirement
    # -------------------------------------------------------------------------
    def test_06_obsolete_lesson_detection_marks_retired(self):
        """Verifies obsolete lessons transition to RETIRED_OBSOLETE and remain on disk."""
        l1 = self._create_sample_lesson("LSN-OBS-01", "Rule to retire.")
        retired = self.consolidator.detect_obsolete_lessons(
            lessons=[l1],
            merged_source_ids={"LSN-OBS-01"},
            dry_run=False
        )

        self.assertEqual(len(retired), 1)
        self.assertEqual(retired[0]["status"], "RETIRED_OBSOLETE")
        self.assertIn("obsolete_reason", retired[0])

        # Verify disk file is preserved with RETIRED_OBSOLETE status
        fp = os.path.join(self.consolidator.lessons_dir, "LSN-OBS-01.json")
        self.assertTrue(os.path.isfile(fp))
        with open(fp, "r", encoding="utf-8") as f:
            disk_data = json.load(f)
        self.assertEqual(disk_data["status"], "RETIRED_OBSOLETE")

    # -------------------------------------------------------------------------
    # Test 7: Canonical Skill Update & Directive 18 Compliance
    # -------------------------------------------------------------------------
    def test_07_canonical_skill_update_enforces_directive_18_and_snapshots(self):
        """Verifies skill updates create rollback snapshots and enforce < 500 lines."""
        mock_skill_dir = os.path.join(self.consolidator.skills_dir, "mock-skill")
        os.makedirs(mock_skill_dir, exist_ok=True)
        skill_path = os.path.join(mock_skill_dir, "SKILL.md")

        with open(skill_path, "w", encoding="utf-8") as f:
            f.write("# Mock Skill\n\nInitial instructions for statistical reporting.\n")

        mock_consolidated = [{
            "lesson_id": "LSN-CONSOLIDATED-TEST-001",
            "desired_behavior": "Always report exact p-values (۰.۰۵ > p).",
            "related_skills": ["mock-skill"]
        }]

        res = self.consolidator.update_canonical_skill(
            skill="mock-skill",
            consolidated_lessons=mock_consolidated,
            dry_run=False
        )

        self.assertEqual(res["status"], "UPDATED")
        self.assertTrue(res["directive_18_compliant"])
        self.assertLessEqual(res["updated_lines"], 500)

        # Verify snapshot created
        snapshots = os.listdir(self.consolidator.snapshots_dir)
        self.assertTrue(any(s.startswith("mock-skill_v") for s in snapshots))

    # -------------------------------------------------------------------------
    # Test 8: Active Learning Context Remains Bounded
    # -------------------------------------------------------------------------
    def test_08_active_learning_context_remains_bounded(self):
        """
        End-to-end integration test: running periodic consolidation bounds the active
        context, resolves contradictions, and filters out superseded clutter.
        """
        # Seed 4 duplicate lessons and 2 contradictory lessons
        for i in range(1, 4):
            self._create_sample_lesson(
                f"LSN-CLUTTER-0{i}",
                "Always verify parametric assumptions before running multiple regression.",
                source_exp=f"EXP-C{i}",
                skills=["statistical-data-analyst"]
            )

        self._create_sample_lesson(
            "LSN-CONFLICT-A",
            "For longitudinal repeated measurements, always execute repeated-measures ANOVA assuming sphericity.",
            skills=["statistical-data-analyst"]
        )
        self._create_sample_lesson(
            "LSN-CONFLICT-B",
            "For longitudinal repeated measurements, use linear mixed models LMM instead of repeated-measures ANOVA.",
            skills=["statistical-data-analyst"]
        )

        # Run end-to-end periodic consolidation
        report = self.consolidator.run_periodic_consolidation(target_skill="statistical-data-analyst", dry_run=False)
        self.assertEqual(report["status"], "CONSOLIDATION_COMPLETED")
        self.assertGreater(len(report["merged_lesson_ids"]), 0)
        self.assertGreater(len(report["contradiction_ids"]), 0)

        # Active lessons discovered should now be bounded (duplicates replaced by 1 consolidated lesson)
        active_after = self.consolidator.ingest_active_lessons(skill="statistical-data-analyst")
        active_ids = [l["lesson_id"] for l in active_after]

        # The clutter source lessons must NOT be in active lessons
        self.assertNotIn("LSN-CLUTTER-01", active_ids)
        self.assertNotIn("LSN-CLUTTER-02", active_ids)
        self.assertNotIn("LSN-CLUTTER-03", active_ids)

        # The consolidated lesson must be active
        self.assertTrue(any(lid.startswith("LSN-CONSOLIDATED-") for lid in active_ids))

        # Query knowledge items through KnowledgeManager: active filtering verified
        km_active = self.consolidator.knowledge_manager.query(
            item_types=["lesson"],
            capability="statistical-data-analyst"
        )
        km_ids = [item.get("lesson_id") or item.get("knowledge_id") for item in km_active]
        self.assertNotIn("LSN-CLUTTER-01", km_ids)
        self.assertNotIn("LSN-CLUTTER-02", km_ids)


if __name__ == "__main__":
    unittest.main()
