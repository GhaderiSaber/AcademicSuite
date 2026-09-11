#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Digital Saber Interactive Shell & Telegram Co-Pilot Bridge
(test_digital_saber_shell.py)
-------------------------------------------------------------------------
Validates:
1. Shell initialization, prompt rendering, and startup banner.
2. Command dispatch: /scale, /consult, /quote, /cases, /decisions, /audit, /copilot.
3. Natural language query fallback and case precedent retrieval.
4. Co-Pilot bridge status, quotation drafting, and admin approval actions.
5. CLI argument integration (--shell, --copilot-status, --copilot-sim).
"""

import os
import sys
import io
import unittest
import subprocess
from contextlib import redirect_stdout

# Add root directory to sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

SHARED_DIR = os.path.join(ROOT_DIR, ".agents", "shared")
if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)

COPILOT_DIR = os.path.join(ROOT_DIR, ".agents", "skills", "digital-twin-academic-consultant", "scripts")
if COPILOT_DIR not in sys.path:
    sys.path.insert(0, COPILOT_DIR)

from digital_saber import DigitalSaber
from digital_saber_shell import DigitalSaberShell
from copilot_bridge import TelegramCopilotBridge


class TestDigitalSaberShell(unittest.TestCase):
    """Test suite for Interactive Digital Saber Shell and Co-Pilot bridge."""

    @classmethod
    def setUpClass(cls):
        cls.saber = DigitalSaber()

    def setUp(self):
        self.shell = DigitalSaberShell(saber_instance=self.saber)

    def test_01_shell_initialization_and_banner(self):
        """Validates shell prompt and startup banner output."""
        self.assertIn("Saber", self.shell.prompt)
        f = io.StringIO()
        with redirect_stdout(f):
            self.shell.print_banner()
        out = f.getvalue()
        self.assertIn("DIGITAL SABER", out)
        self.assertIn("Memory:", out)
        self.assertIn("Available Commands:", out)

    def test_02_command_scale_search(self):
        """Tests /scale command searching Questionnaires.xlsx."""
        f = io.StringIO()
        with redirect_stdout(f):
            self.shell.do_scale("اضطراب کتل")
        out = f.getvalue()
        self.assertIn("Cattell Anxiety Scale", out)
        self.assertIn("نمره‌گذاری", out)

    def test_03_command_consult(self):
        """Tests /consult command for statistical advice and precedent matching."""
        f = io.StringIO()
        with redirect_stdout(f):
            self.shell.do_consult("اثربخشی درمان مبتنی بر پذیرش و تعهد بر فرسودگی شغلی با کنترل پیش‌آزمون")
        out = f.getvalue()
        self.assertIn("صابر قادری", out)
        self.assertIn("روش آماری پیشنهادی", out)
        self.assertIn("سابقه‌های مشابه در حافظه تجربی", out)

    def test_04_command_quote(self):
        """Tests /quote command extracting parameters and calculating pricing."""
        proposal_text = (
            "عنوان: پیش‌بینی تاب‌آوری بر اساس خودشفقت‌ورزی در دانشجویان\n"
            "طرح: همبستگی و رگرسیون چندگانه\n"
            "جامعه: ۲۴۰ نفر\n"
            "ابزارها: پرسشنامه تاب‌آوری کانر-دیویدسون و مقیاس شفقت خود نف"
        )
        f = io.StringIO()
        with redirect_stdout(f):
            self.shell.do_quote(proposal_text)
        out = f.getvalue()
        self.assertIn("پیش‌فاکتور تفکیکی", out)
        self.assertIn("کل سرمایه‌گذاری:", out)
        self.assertIn("تومان", out)
        self.assertIn("کارت تایید مدیریت", out)

    def test_05_command_cases_and_decisions(self):
        """Tests /cases list/search and /decisions inspection."""
        f_cases = io.StringIO()
        with redirect_stdout(f_cases):
            self.shell.do_cases("تئوری انتخاب")
        out_cases = f_cases.getvalue()
        self.assertIn("نتایج جستجو در پرونده‌های تاریخی", out_cases)
        self.assertIn("case_014", out_cases)

        f_dec = io.StringIO()
        with redirect_stdout(f_dec):
            self.shell.do_decisions("")
        out_dec = f_dec.getvalue()
        self.assertIn("دفتر ثبت تصمیمات تخصصی", out_dec)

    def test_06_command_audit(self):
        """Tests /audit on prose text detecting cliches or verifying clean academic prose."""
        clean_prose = "یافته‌های حاصل از آزمون تحلیل کوواریانس نشان داد که درمان اثربخش بوده است."
        f_audit = io.StringIO()
        with redirect_stdout(f_audit):
            self.shell.do_audit(clean_prose)
        out_audit = f_audit.getvalue()
        self.assertIn("ارزیابی سبک نگارش", out_audit)
        self.assertIn("امتیاز کیفیت نگارش", out_audit)

    def test_07_copilot_bridge_status_and_simulation(self):
        """Tests Co-Pilot bridge status retrieval and simulation."""
        bridge = TelegramCopilotBridge(self.saber)
        status = bridge.get_status()
        self.assertEqual(status["policy"], "copilot_only")
        self.assertEqual(status["admin_id"], 124911145)
        self.assertIn("ACTIVE", status["status"])

        sim_res = bridge.run_simulation()
        self.assertEqual(sim_res["status"], "success")
        self.assertGreaterEqual(len(sim_res["events"]), 5)

    def test_08_copilot_quote_draft_and_approval(self):
        """Tests proposal quotation drafting and admin approval workflow."""
        bridge = TelegramCopilotBridge(self.saber)
        record = bridge.draft_proposal_quote("عنوان: اثربخشی طرحواره‌درمانی بر اضطراب\nطرح: پیش‌آزمون پس‌آزمون\nنمونه: ۳۰ نفر")
        qid = record["quote_id"]
        self.assertTrue(qid.startswith("Q"))
        self.assertEqual(record["status"], "PENDING_ADMIN_APPROVAL")

        # Approve quote
        app_res = bridge.approve_quote(qid)
        self.assertEqual(app_res["status"], "success")
        self.assertIn("approved", app_res["message"].lower())

    def test_09_natural_language_fallback(self):
        """Tests free-form natural language query routing in default()."""
        f_nl = io.StringIO()
        with redirect_stdout(f_nl):
            self.shell.default("برای یک طرح شبه‌آزمایشی با ۲ گروه و پیش‌آزمون چه تحلیلی مناسب است؟")
        out_nl = f_nl.getvalue()
        self.assertIn("پاسخ تحلیلی صابر قادری", out_nl)
        self.assertIn("ANCOVA", out_nl)

    def test_10_cli_flags_execution(self):
        """Tests CLI flags via subprocess execution."""
        # Test --copilot-status
        res_status = subprocess.run(
            [sys.executable, "digital_saber.py", "--copilot-status"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True
        )
        self.assertEqual(res_status.returncode, 0)
        self.assertIn("TELEGRAM CO-PILOT STATUS", res_status.stdout)

        # Test --copilot-sim
        res_sim = subprocess.run(
            [sys.executable, "digital_saber.py", "--copilot-sim"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True
        )
        self.assertEqual(res_sim.returncode, 0)
        self.assertIn("Co-Pilot Simulation Result: success", res_sim.stdout)


if __name__ == "__main__":
    unittest.main()
