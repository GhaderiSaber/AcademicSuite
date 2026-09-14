#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_thesis_revision.py — Unit Tests for Thesis Revision & Examiner Rebuttal Pipeline
Validates:
  1. Comment Ingestion (Docx, Text, JSON, and Benchmark)
  2. 3-Tier Feedback Triage (Format / Stats / Theory)
  3. Deterministic Statistical Recalculation Linkage
  4. Polite Academic Rebuttal Synthesis & Typography Rules
  5. Committee Re-Defense Clearance Simulation
  6. OpenXML Response Table Word Document & BiDi RTL
  7. MultiAgentOrchestrator Task Packets & Schema Validation
  8. Full End-to-End Workflow Execution via DigitalSaber
"""

import os
import sys
import json
import zipfile
import unittest
import xml.etree.ElementTree as ET

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "skills", "academic-suite-orchestrator", "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "skills", "persian-thesis-revision-assistant", "scripts"))

from digital_saber import DigitalSaber
from revision_triage_engine import RevisionTriageEngine
from multi_agent_orchestrator import MultiAgentOrchestrator

AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")


class TestThesisRevisionSuite(unittest.TestCase):
    """Test suite for thesis revision and examiner feedback resolution pipeline."""

    @classmethod
    def setUpClass(cls):
        cls.decisions_dir = os.path.join(AGENTS_DIR, "memory", "decisions")
        cls.initial_decisions = set(os.listdir(cls.decisions_dir)) if os.path.exists(cls.decisions_dir) else set()
        cls.test_output_dir = os.path.join(ROOT_DIR, "output")
        os.makedirs(cls.test_output_dir, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        # Clean up newly generated test decision records
        if os.path.exists(cls.decisions_dir):
            current = set(os.listdir(cls.decisions_dir))
            for f in current - cls.initial_decisions:
                try:
                    os.remove(os.path.join(cls.decisions_dir, f))
                except Exception:
                    pass

    def setUp(self):
        self.engine = RevisionTriageEngine(workspace_root=ROOT_DIR)
        self.orchestrator = MultiAgentOrchestrator(workspace_root=ROOT_DIR)
        self.saber = DigitalSaber()

    def test_01_comment_ingestion_benchmark(self):
        """Validates that comment ingestion retrieves the 14 authentic benchmark comments."""
        comments = self.engine.ingest_comments(None)
        self.assertEqual(len(comments), 14, "Expected exactly 14 benchmark comments.")
        for c in comments:
            self.assertIn("id", c)
            self.assertIn("tier", c)
            self.assertIn("reviewer", c)
            self.assertIn("comment", c)
            self.assertIn("chapter", c)
            self.assertIn("page_target", c)

    def test_02_3tier_categorization(self):
        """Validates that comments are triaged into Tier 1 (Format), Tier 2 (Stats), and Tier 3 (Theory)."""
        raw = self.engine.ingest_comments(None)
        triaged = self.engine.triage_comments(raw)
        self.assertEqual(len(triaged), 14)

        t1 = [c for c in triaged if c["tier"] == "FORMAT"]
        t2 = [c for c in triaged if c["tier"] == "STATS"]
        t3 = [c for c in triaged if c["tier"] == "THEORY"]

        self.assertEqual(len(t1), 6, "Expected 6 Format comments.")
        self.assertEqual(len(t2), 4, "Expected 4 Stats comments.")
        self.assertEqual(len(t3), 4, "Expected 4 Theory comments.")

        # Check assigned subagents
        self.assertEqual(t1[0]["assigned_agent"], "results-auditor")
        self.assertEqual(t2[0]["assigned_agent"], "statistical-expert")
        self.assertEqual(t3[0]["assigned_agent"], "academic-writer")

    def test_03_deterministic_recalculation_linkage(self):
        """Validates deterministic linking of Tier 2 comments to stats_results.json."""
        raw = self.engine.ingest_comments(None)
        triaged = self.engine.triage_comments(raw)
        stats_path = os.path.join(self.test_output_dir, "stats_results.json")

        triaged_stats, audit = self.engine.recalculate_statistics(triaged, stats_path)

        self.assertTrue(audit["degrees_of_freedom_verified"])
        self.assertIn("slope_homogeneity", audit)
        slope = audit["slope_homogeneity"]
        self.assertTrue(slope["assumption_met"])
        self.assertIn("F(1, 56) = 0.58, p = .451", slope["formatted_apa"])

        # Check that MSAI verdict is normal empirical
        self.assertEqual(audit["msai_anomaly_verdict"], "NORMAL_EMPIRICAL")
        self.assertEqual(audit["msai_anomaly_index"], 0)

    def test_04_rebuttal_synthesis_and_etiquette(self):
        """Validates that academic rebuttals are courteous, cite exact pages, and preserve leading zeros."""
        raw = self.engine.ingest_comments(None)
        triaged = self.engine.triage_comments(raw)
        _, audit = self.engine.recalculate_statistics(triaged)
        resolved = self.engine.synthesize_rebuttals(triaged, audit, "رساله آزمایشی دکتری")

        self.assertEqual(len(resolved), 14)
        for c in resolved:
            self.assertEqual(c["status"], "RESOLVED")
            self.assertTrue(len(c["action_taken"]) > 20)
            self.assertTrue(len(c["location"]) > 2)

        # Comment 9 (slope homogeneity) must contain exact recalculated F and p values
        c9 = next(c for c in resolved if c["id"] == 9)
        self.assertIn("F(1, 56) = 0.58, p = .451", c9["action_taken"])
        self.assertIn("صفحه ۱۰۲، جدول ۴-۵", c9["location"])

        # Comment 3 (leading zero) must mention leading zero retention
        c3 = next(c for c in resolved if c["id"] == 3)
        self.assertIn("۰.۰۰۱ > p", c3["action_taken"])

    def test_05_committee_clearance_evaluation(self):
        """Validates that committee clearance calculates readiness >= 90% and approved verdict."""
        raw = self.engine.ingest_comments(None)
        triaged = self.engine.triage_comments(raw)
        _, audit = self.engine.recalculate_statistics(triaged)
        resolved = self.engine.synthesize_rebuttals(triaged, audit)

        clearance = self.engine.evaluate_committee_clearance(resolved)
        self.assertEqual(clearance["total_comments_reviewed"], 14)
        self.assertEqual(clearance["comments_resolved"], 14)
        self.assertEqual(clearance["resolution_rate_percent"], 100.0)
        self.assertGreaterEqual(clearance["readiness_score"], 95.0)
        self.assertEqual(clearance["clearance_verdict"], "APPROVED_FOR_SIGN_OFF")

    def test_06_openxml_response_table_document(self):
        """Validates that Revision_Response_Table.docx has proper OpenXML BiDi and APA 7 structure."""
        out_docx = os.path.join(self.test_output_dir, "test_Revision_Response_Table.docx")
        pipeline_res = self.engine.run_pipeline(output_dir=self.test_output_dir)
        target_docx = pipeline_res["artifacts_generated"]["rebuttal_table_docx"]

        self.assertTrue(os.path.exists(target_docx))
        self.assertGreater(os.path.getsize(target_docx), 1000)

        # Inspect OpenXML document structure
        with zipfile.ZipFile(target_docx, "r") as z:
            doc_xml = z.read("word/document.xml").decode("utf-8")
            # Must have w:bidiVisual on table
            self.assertIn("w:bidiVisual", doc_xml)
            # Must have w:bidi on paragraphs
            self.assertIn('w:bidi w:val="1"', doc_xml)
            # Zero vertical borders
            self.assertIn('w:left w:val="none"', doc_xml)
            self.assertIn('w:right w:val="none"', doc_xml)
            self.assertIn('w:insideV w:val="none"', doc_xml)

    def test_07_multiagent_orchestrator_packets(self):
        """Validates task packet generation and critique schema validation for thesis_revision."""
        roles = ["results-auditor", "statistical-auditor", "academic-writer", "final-judge"]
        for r in roles:
            packet = self.orchestrator.generate_task_packet("thesis_revision", r, context_dir="output")
            self.assertEqual(packet["workflow"], "thesis_revision")
            self.assertEqual(packet["target_role"], r)
            self.assertIn("role_title", packet)
            self.assertIn("mandate", packet)
            self.assertIn("artifacts_to_inspect", packet)
            self.assertGreater(len(packet["instructions"]), 0)
            self.assertIn("expected_return_schema", packet)

        # Validate schema validation
        valid_judge = {"verdict": "APPROVED_FOR_SIGN_OFF", "readiness_score": 99.0}
        ok, errs = self.orchestrator.validate_critique_payload("final-judge", valid_judge, workflow="thesis_revision")
        self.assertTrue(ok)
        self.assertEqual(len(errs), 0)

        invalid_judge = {"some_other_key": 123}
        ok, errs = self.orchestrator.validate_critique_payload("final-judge", invalid_judge, workflow="thesis_revision")
        self.assertFalse(ok)
        self.assertGreater(len(errs), 0)

    def test_08_end_to_end_saber_workflow_execution(self):
        """Validates full end-to-end execution of thesis_revision via DigitalSaber."""
        res = self.saber.run_workflow("thesis_revision", output_dir=self.test_output_dir)
        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["workflow"], "thesis_revision")
        self.assertEqual(res["execution_mode"], "ANTIGRAVITY_MULTI_AGENT")
        self.assertEqual(res["comments_resolved"], 14)
        self.assertGreaterEqual(res["readiness_score"], 90.0)
        self.assertTrue(res["decision_id"].startswith("dec_"))

        # Verify all 6 Directive 3 physical artifacts exist
        expected_artifacts = [
            "extracted_comments.json",
            "triaged_comments.json",
            "revision_stats_audit.json",
            "resolved_comments.json",
            "committee_clearance_report.json",
            "Revision_Response_Table.docx"
        ]
        for name in expected_artifacts:
            full_path = os.path.join(self.test_output_dir, name)
            self.assertTrue(os.path.exists(full_path), f"Missing artifact: {full_path}")
            self.assertGreater(os.path.getsize(full_path), 0, f"Empty artifact: {full_path}")


if __name__ == "__main__":
    unittest.main()
