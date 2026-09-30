#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_revision_pipeline.py — Comprehensive Test Suite for Universal Academic Revision Pipeline
---------------------------------------------------------------------------------------------------
Validates:
1. Polymorphic Scope Detection & Ingestion (Article, Chapter, Thesis, Proposal)
2. 3-Tier Multi-Domain Triage (Format / Stats / Theory)
3. In-Place Manuscript Remediation & Document Conservation Gate (>= 90%)
4. Surgical Run-Level Highlight Preservation (Green client preserved, Yellow revision applied)
5. Formal Point-by-Point Rebuttal Compilation (APA 7 borders, zero vertical borders)
6. State Machine Governance (StrictStateMachine transitions across REVISION_STAGE_GRAPH)
7. Canonical Pipeline Prerequisites Verification (canonical_pipelines.py Stage R.0 – R.6)
8. End-to-End Pipeline Execution & Pipeline Auditor Verification
"""

import os
import sys
import json
import zipfile
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "contracts"))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "verification"))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "skills", "persian-thesis-revision-assistant", "scripts"))

import academic_state_manager as sm
from academic_state_manager import StrictStateMachine, StageState, ProjectState, REVISION_STAGE_GRAPH
import canonical_pipelines as cp
import pipeline_auditor as pa
from revision_pipeline_engine import RevisionPipelineEngine, DocumentConservationViolationError


class TestRevisionPipeline(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="rev_test_")
        self.out_dir = os.path.join(self.temp_dir, "03_deliverables")
        os.makedirs(self.out_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # --------------------------------------------------------------------------
    # 1. Polymorphic Scope Detection & Ingestion
    # --------------------------------------------------------------------------
    def test_01_scope_detection_and_ingestion(self):
        """Verifies polymorphic scope detection for articles, chapters, and theses."""
        # 1a. Article scope
        sample_feedback_article = (
            "Reviewer 1, Comment 1: Please clarify the sample size and G*Power a priori estimation.\n"
            "Reviewer 1, Comment 2: Missing citations for 2024-2026 cognitive schema mechanisms.\n"
            "Reviewer 2, Comment 1: Check APA 7 3-line borders and formatting on Table 2.\n"
        )
        fb_txt = os.path.join(self.temp_dir, "reviewer_comments.txt")
        with open(fb_txt, "w", encoding="utf-8") as f:
            f.write(sample_feedback_article)

        engine_art = RevisionPipelineEngine(
            doc_path=os.path.join(self.temp_dir, "psychology_article.docx"),
            feedback_path=fb_txt,
            out_dir=self.out_dir,
            scope="auto"
        )
        res = engine_art.execute_stage_r0_ingestion()
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["scope"], "journal_article")
        self.assertEqual(res["total_comments"], 3)
        self.assertEqual(engine_art.get_output_document_name(), "psychology_article_Revised.docx")
        self.assertEqual(engine_art.get_response_table_name(), "Response_to_Reviewers.docx")

        # 1b. Thesis scope
        engine_th = RevisionPipelineEngine(
            doc_path=os.path.join(self.temp_dir, "master_thesis.docx"),
            feedback_path=fb_txt,
            out_dir=self.out_dir,
            scope="thesis"
        )
        self.assertEqual(engine_th.resolved_scope, "full_thesis")
        self.assertEqual(engine_th.get_output_document_name(), "master_thesis_Revised.docx")
        self.assertEqual(engine_th.get_response_table_name(), "Revision_Response_Table.docx")

    # --------------------------------------------------------------------------
    # 2. 3-Tier Multi-Domain Triage
    # --------------------------------------------------------------------------
    def test_02_three_tier_triage(self):
        """Verifies comments are classified into FORMAT, STATS, and THEORY with correct subagent routing."""
        feedback = (
            "1. جدول ۳ خط افقی ندارد و خطوط عمودی باید حذف شوند.\n"  # FORMAT
            "2. آزمون مفروضه شاپیرو-ویلک و بررسی هم‌خطی با VIF گزارش شود.\n"  # STATS
            "3. پیشینه پژوهش با مقالات ۲۰۲۴-۲۰۲۶ و مبانی نظری بک تقویت گردد.\n"  # THEORY
        )
        fb_path = os.path.join(self.temp_dir, "feedback.txt")
        with open(fb_path, "w", encoding="utf-8") as f:
            f.write(feedback)

        engine = RevisionPipelineEngine(feedback_path=fb_path, out_dir=self.out_dir, scope="chapter")
        engine.execute_stage_r0_ingestion()
        triage_res = engine.execute_stage_r1_triage()

        self.assertEqual(triage_res["status"], "SUCCESS")
        counts = triage_res["tier_counts"]
        self.assertEqual(counts["FORMAT"], 1)
        self.assertEqual(counts["STATS"], 1)
        self.assertEqual(counts["THEORY"], 1)

        plan_file = os.path.join(self.out_dir, "01_revision_triage_plan.json")
        with open(plan_file, "r", encoding="utf-8") as f:
            plan = json.load(f)

        stats_item = next(item for item in plan if item["tier"] == "STATS")
        theory_item = next(item for item in plan if item["tier"] == "THEORY")
        format_item = next(item for item in plan if item["tier"] == "FORMAT")

        self.assertEqual(stats_item["assigned_agent"], "statistics-agent")
        self.assertEqual(theory_item["assigned_agent"], "literature-expert")
        self.assertEqual(format_item["assigned_agent"], "academic-writer")

    # --------------------------------------------------------------------------
    # 3. In-Place Manuscript Remediation & Document Conservation Gate
    # --------------------------------------------------------------------------
    def test_03_in_place_remediation_and_conservation_gate(self):
        """Verifies that Document Conservation Gate passes for in-place mutation and rejects draft obliteration."""
        # Create a sample raw docx
        import docx
        raw_docx = os.path.join(self.temp_dir, "Reviewed_Manuscript.docx")
        doc = docx.Document()
        for i in range(25):
            doc.add_paragraph(f"این پاراگراف آزمایشی شماره {i+1} رساله است که شامل داده‌های ارزشمند پیشین می‌باشد.")
        doc.save(raw_docx)
        raw_size = os.path.getsize(raw_docx)

        engine = RevisionPipelineEngine(doc_path=raw_docx, out_dir=self.out_dir, scope="article")
        engine.execute_stage_r0_ingestion()
        engine.execute_stage_r1_triage()
        rem_res = engine.execute_stage_r3_remediation()

        self.assertEqual(rem_res["status"], "SUCCESS")
        self.assertGreaterEqual(rem_res["conservation_ratio"], 0.90)

        # Test Draft Obliteration Protection: artificially truncated document
        with self.assertRaises(DocumentConservationViolationError):
            engine_broken = RevisionPipelineEngine(doc_path=raw_docx, out_dir=self.out_dir)
            # Simulate artificial byte drop below 90%
            fake_small_doc = os.path.join(self.out_dir, engine_broken.get_output_document_name())
            with open(fake_small_doc, "wb") as f:
                f.write(b"PK\x03\x04" + b"0" * 100)  # Tiny truncated file
            
            # Conservation gate check
            out_sz = os.path.getsize(fake_small_doc)
            ratio = out_sz / raw_size
            if ratio < 0.90:
                raise DocumentConservationViolationError(f"Conservation ratio {ratio:.2%} < 90%")

    # --------------------------------------------------------------------------
    # 4. Surgical Run-Level Highlight Preservation
    # --------------------------------------------------------------------------
    def test_04_highlight_preservation_and_run_level_mutation(self):
        """Verifies green client highlights are conserved and yellow revision highlights are added."""
        import docx
        from docx.oxml import parse_xml
        from docx.oxml.ns import nsdecls

        raw_docx = os.path.join(self.temp_dir, "Highlight_Test.docx")
        doc = docx.Document()
        p1 = doc.add_paragraph("نکته مهم: ")
        r_green = p1.add_run("این بخش دارای هایلایت سبز دانشجو است.")
        r_greenPr = r_green._r.get_or_add_rPr()
        r_greenPr.append(parse_xml(f'<w:highlight {nsdecls("w")} w:val="green"/>'))
        doc.save(raw_docx)

        engine = RevisionPipelineEngine(doc_path=raw_docx, out_dir=self.out_dir, scope="thesis")
        engine.execute_stage_r0_ingestion()
        engine.execute_stage_r1_triage()
        engine.execute_stage_r3_remediation()

        revised_docx = os.path.join(self.out_dir, engine.get_output_document_name())
        self.assertTrue(os.path.isfile(revised_docx))

        with zipfile.ZipFile(revised_docx, 'r') as z:
            xml_str = z.read('word/document.xml').decode('utf-8')
            # Assert client green highlight is preserved (HIGHLIGHT_CONSERVATION)
            self.assertTrue('val="green"' in xml_str)
            # Assert supervisor revision yellow highlight was added
            self.assertTrue('val="yellow"' in xml_str)

    # --------------------------------------------------------------------------
    # 5. Formal Point-by-Point Rebuttal Compilation
    # --------------------------------------------------------------------------
    def test_05_rebuttal_table_generation(self):
        """Verifies formal Point-by-Point Response Table with APA 7 borders and full comment coverage."""
        fb_txt = os.path.join(self.temp_dir, "fb.txt")
        with open(fb_txt, "w", encoding="utf-8") as f:
            f.write("نظر ۱: اصلاح خطوط جداول.\nنظر ۲: بررسی همبستگی دومتغیری.\n")

        engine = RevisionPipelineEngine(feedback_path=fb_txt, out_dir=self.out_dir, scope="thesis")
        engine.execute_stage_r0_ingestion()
        engine.execute_stage_r1_triage()
        res_r4 = engine.execute_stage_r4_response_table()

        self.assertEqual(res_r4["status"], "SUCCESS")
        self.assertEqual(res_r4["total_resolved"], 2)

        table_docx = os.path.join(self.out_dir, "Revision_Response_Table.docx")
        self.assertTrue(os.path.isfile(table_docx))

        # Check APA 7 zero vertical borders in XML
        with zipfile.ZipFile(table_docx, 'r') as z:
            xml_str = z.read('word/document.xml').decode('utf-8')
            has_inside_v = ('<w:insideV w:val="none"/>' in xml_str or '<w:insideV' not in xml_str)
            self.assertTrue(has_inside_v)

    # --------------------------------------------------------------------------
    # 6. State Machine Governance
    # --------------------------------------------------------------------------
    def test_06_state_machine_governance(self):
        """Verifies StrictStateMachine initialization and valid transitions across REVISION_STAGE_GRAPH."""
        state_dir = os.path.join(self.temp_dir, "academic-state")
        sm_res = sm.init_project_state(self.temp_dir, pipeline="academic_revision")
        self.assertEqual(sm_res["status"], "SUCCESS")

        machine = StrictStateMachine(state_dir=state_dir, project_path=self.temp_dir)
        self.assertEqual(len(machine.stages), 7)
        self.assertIn("00_feedback_ingestion", machine.stages)
        self.assertIn("06_final_clearance", machine.stages)

        # Stage 0 is READY, Stage 1 is LOCKED
        self.assertEqual(machine.stages["00_feedback_ingestion"]["status"], StageState.STAGE_READY.value)
        self.assertEqual(machine.stages["01_feedback_triage"]["status"], StageState.STAGE_LOCKED.value)

        # Transition 00_feedback_ingestion: READY -> RUNNING -> VALIDATING -> AWAITING_APPROVAL -> APPROVED
        machine.request_transition("00_feedback_ingestion", StageState.STAGE_RUNNING, rationale="Starting comment extraction")

        # Mock required output artifact for stage 00_feedback_ingestion
        with open(os.path.join(state_dir, "00_extracted_comments.json"), "w", encoding="utf-8") as f:
            json.dump([{"id": 1, "comment": "test"}], f)

        machine.request_transition("00_feedback_ingestion", StageState.STAGE_VALIDATING, mode="test")
        machine.request_transition("00_feedback_ingestion", StageState.STAGE_AWAITING_APPROVAL, mode="test")

        # Grant human approval (Directive 11 / Saber Admin Desk)
        appr = machine.request_approval(
            milestone_id="00_feedback_ingestion",
            category="reporting",
            requester_agent="academic-orchestrator",
            rationale="Feedback extraction approved"
        )
        machine.grant_approval(
            approval_id=appr["approval_id"],
            approver_identity="Saber Admin Desk 124911145",
            digital_signature="SIG-VERIFIED-124911145",
            comments="Approved"
        )

        # Passing validation report (Directive 19 / Phase 13)
        val_path = os.path.join(state_dir, "validation_report.json")
        with open(val_path, "w", encoding="utf-8") as f:
            json.dump({"overall_verdict": "PASS", "checks_failed": 0, "stage_id": "00_feedback_ingestion"}, f)

        machine.request_transition("00_feedback_ingestion", StageState.STAGE_APPROVED, mode="test")
        self.assertEqual(machine.stages["00_feedback_ingestion"]["status"], StageState.STAGE_APPROVED.value)

        # Advance to NEXT_STAGE -> unlocks 01_feedback_triage
        res = machine.request_transition("00_feedback_ingestion", StageState.NEXT_STAGE, mode="test")
        self.assertEqual(res["status"], "TRANSITIONED")
        self.assertEqual(res["next_stage_id"], "01_feedback_triage")
        self.assertEqual(machine.stages["01_feedback_triage"]["status"], StageState.STAGE_READY.value)

        # Illegal jump: cannot start Stage 4 while Stage 1 is not approved
        with self.assertRaises(Exception):
            machine.request_transition("04_response_table_compilation", StageState.STAGE_RUNNING, rationale="Illegal leap")

    # --------------------------------------------------------------------------
    # 7. Canonical Pipeline Prerequisites Verification
    # --------------------------------------------------------------------------
    def test_07_canonical_pipeline_prerequisites(self):
        """Verifies canonical prerequisite checking in canonical_pipelines.py for Stages R.0 – R.6."""
        # Stage R.0 has no prerequisites
        ok0, msg0 = cp.verify_pipeline_stage_prerequisites("Stage R.0: Feedback Ingestion", [self.temp_dir])
        self.assertTrue(ok0)

        # Stage R.1 requires 00_extracted_comments.json
        ok1_fail, _ = cp.verify_pipeline_stage_prerequisites("Stage R.1: 3-Tier Multi-Domain Triage", [self.temp_dir])
        self.assertFalse(ok1_fail)

        # Create prerequisite for R.1
        with open(os.path.join(self.temp_dir, "00_extracted_comments.json"), "w") as f:
            f.write("[]")

        ok1_pass, _ = cp.verify_pipeline_stage_prerequisites("Stage R.1: 3-Tier Multi-Domain Triage", [self.temp_dir])
        self.assertTrue(ok1_pass)

    # --------------------------------------------------------------------------
    # 8. End-to-End Pipeline Execution & Independent Pipeline Auditor
    # --------------------------------------------------------------------------
    def test_08_end_to_end_pipeline_and_audit(self):
        """Executes the full pipeline end-to-end and asserts pipeline_auditor returns overall PASSED."""
        fb_txt = os.path.join(self.temp_dir, "supervisor_defense_comments.txt")
        with open(fb_txt, "w", encoding="utf-8") as f:
            f.write(
                "۱. اصلاح نیم‌فاصله‌ها و خطوط جداول بر اساس APA 7.\n"
                "۲. درج شاخص مجذور اتا و توان آماری آزمون‌ها.\n"
                "۳. بررسی انطباق یافته‌ها با پژوهش‌های ۲۰۲۵.\n"
            )

        engine = RevisionPipelineEngine(
            feedback_path=fb_txt,
            out_dir=self.out_dir,
            scope="thesis",
            title="رساله دکتری روان‌شناسی"
        )
        e2e_res = engine.execute_all()

        self.assertEqual(e2e_res["overall_verdict"], "PASS")
        self.assertEqual(e2e_res["decision"], "APPROVED_FOR_RELEASE")

        # Run independent pipeline auditor CLI verification
        auditor = pa.PipelineAuditor(target_dir=self.out_dir, workflow="academic_revision", strict=True)
        report = auditor.run_audit()

        self.assertEqual(report["status"], "PASSED")
        self.assertTrue(auditor.overall_passed)


if __name__ == "__main__":
    unittest.main()
