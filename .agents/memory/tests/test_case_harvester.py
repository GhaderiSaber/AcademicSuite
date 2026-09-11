#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Digital Saber Google Drive Case Harvester & Case Memory Expansion
"""

import os
import sys
import unittest
import tempfile
import shutil
import json

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.abspath(os.path.join(TESTS_DIR, ".."))
AGENTS_DIR = os.path.abspath(os.path.join(MEMORY_DIR, ".."))
ROOT_DIR = os.path.abspath(os.path.join(AGENTS_DIR, ".."))

for p in [ROOT_DIR, MEMORY_DIR, AGENTS_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from case_harvester import DriveCaseHarvester, HISTORICAL_DRIVE_PROJECTS
from case_memory_engine import CaseMemoryEngine
from digital_saber import DigitalSaber


class TestCaseHarvester(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.cases_dir = os.path.join(self.test_dir, "cases")
        os.makedirs(self.cases_dir, exist_ok=True)
        self.harvester = DriveCaseHarvester(cases_dir=self.cases_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_01_registry_schema_completeness(self):
        """Validates that every historical drive project strictly adheres to the precedent schema."""
        self.assertGreaterEqual(len(HISTORICAL_DRIVE_PROJECTS), 9)
        required_fields = [
            "case_id", "topic", "title_fa", "title_en", "client", "domain",
            "population", "design", "sample_size", "variables", "measures",
            "statistical_analysis", "assumptions_encountered", "decisions_made",
            "supervisor_challenges", "defense_guidance", "final_verdict",
            "confidence_score", "reinforcement_count"
        ]
        for cid, data in HISTORICAL_DRIVE_PROJECTS.items():
            self.assertEqual(cid, data["case_id"], f"Case ID mismatch for {cid}")
            for field in required_fields:
                self.assertIn(field, data, f"Missing field '{field}' in case {cid}")
            self.assertIsInstance(data["variables"], list, f"'variables' must be list in {cid}")
            self.assertIsInstance(data["measures"], list, f"'measures' must be list in {cid}")
            self.assertIsInstance(data["assumptions_encountered"], list, f"'assumptions_encountered' must be list in {cid}")
            self.assertIsInstance(data["decisions_made"], list, f"'decisions_made' must be list in {cid}")
            self.assertGreaterEqual(data["sample_size"], 10, f"Sample size too small in {cid}")
            self.assertGreater(data["confidence_score"], 0.90, f"Confidence score must be high in {cid}")

    def test_02_isolated_ingestion(self):
        """Tests ingestion of cases into an isolated directory."""
        res = self.harvester.ingest_precedents()
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["cases_ingested_count"], len(HISTORICAL_DRIVE_PROJECTS))

        # Check that files were created
        for cid in HISTORICAL_DRIVE_PROJECTS:
            fpath = os.path.join(self.cases_dir, f"{cid}.json")
            self.assertTrue(os.path.exists(fpath), f"File {fpath} does not exist")
            with open(fpath, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            self.assertEqual(loaded["case_id"], cid)
            self.assertEqual(loaded["source_system"], "GoogleDrive_FinishedWorks")
            self.assertIn("harvested_at", loaded)

    def test_03_active_case_memory_count(self):
        """Validates that real repository case memory has at least 23 precedent cases."""
        engine = CaseMemoryEngine()
        self.assertGreaterEqual(engine.count(), 23, "Active case memory should contain at least 23 cases")

    def test_04_cbr_retrieval_precision_anita_montazeri(self):
        """Checks retrieval of Anita Montazeri Choice Theory case."""
        engine = CaseMemoryEngine()
        results = engine.search_precedents("تئوری انتخاب گلاسر بهزیستی روانشناختی آنیتا منتظری", top_k=3)
        self.assertTrue(len(results) > 0)
        top_case_id = results[0]["case"]["case_id"]
        self.assertEqual(top_case_id, "case_014_anita_montazeri_choice_theory_wellbeing")

    def test_05_cbr_retrieval_precision_ailin_ghasemi(self):
        """Checks retrieval of Ailin Ghasemi Schema Therapy eating disorder case."""
        engine = CaseMemoryEngine()
        results = engine.search_precedents("طرحواره‌درمانی ذهنیت‌ها فقدان کنترل خوردن اضافه وزن آیلین قاسمی", top_k=3)
        self.assertTrue(len(results) > 0)
        top_case_id = results[0]["case"]["case_id"]
        self.assertEqual(top_case_id, "case_015_ailin_ghasemi_schema_eating_disorder")

    def test_06_cbr_retrieval_precision_stanford_binet(self):
        """Checks retrieval of Stanford-Binet IRT & DIF psychometric standardization case."""
        engine = CaseMemoryEngine()
        results = engine.search_precedents("هوشبهر استنفورد بینه روانسنجی هنجاریابی کارکرد افتراقی سوال DIF", top_k=3)
        self.assertTrue(len(results) > 0)
        top_case_id = results[0]["case"]["case_id"]
        self.assertEqual(top_case_id, "case_021_stanford_binet_psychometrics_irt_dif")

    def test_07_cbr_retrieval_precision_multigroup_sem(self):
        """Checks retrieval of Baghereyan Multigroup SEM case."""
        engine = CaseMemoryEngine()
        results = engine.search_precedents("معادلات ساختاری چندگروهی هم‌ارزی جنسیتی باقریان سبک‌های تصمیم‌گیری", top_k=3)
        self.assertTrue(len(results) > 0)
        top_case_id = results[0]["case"]["case_id"]
        self.assertEqual(top_case_id, "case_020_baghereyan_decision_making_multigroup_sem")

    def test_08_digital_saber_harvest_integration(self):
        """Tests that DigitalSaber.harvest_drive_cases executes cleanly."""
        saber = DigitalSaber()
        # Ingest single case should run without exception
        saber.harvest_drive_cases("case_014_anita_montazeri_choice_theory_wellbeing")
        self.assertGreaterEqual(saber.case_memory.count(), 23)


if __name__ == "__main__":
    unittest.main()
