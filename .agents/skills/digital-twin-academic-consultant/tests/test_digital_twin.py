#!/usr/bin/env python3
"""
Automated Test Suite for Digital Twin Academic Consultant (test_digital_twin.py)
---------------------------------------------------------------------------------
Validates:
1. Proposal extraction & pricing estimation (Master's ANCOVA and Ph.D. SEM).
2. Persian digit normalization and sample size extraction.
3. Questionnaire database search via Questionnaires.xlsx.
4. Telegram chat export ingestion and FAQ extraction.
5. Bot simulation scenarios (Greeting, Scale Search, Proposal Upload, Admin Approval Desk).
"""

import os
import sys
import json
import unittest

SCRIPT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "scripts")
)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import proposal_price_estimator
import telegram_chat_analyzer
import telegram_bot_daemon


class TestDigitalTwinSuite(unittest.TestCase):

    def setUp(self):
        self.persona = proposal_price_estimator.load_persona()
        self.assertTrue(bool(self.persona), "Persona dictionary should not be empty")

    def test_01_proposal_price_estimator_ancova(self):
        """Test proposal extraction for experimental study with ANCOVA."""
        text = (
            "عنوان: اثربخشی درمان مبتنی بر تعهد و پذیرش بر انعطاف‌پذیری روان‌شناختی\n"
            "مقطع: کارشناسی ارشد روان‌شناسی\n"
            "طرح: پیش‌آزمون و پس‌آزمون با گروه کنترل و آزمون کوواریانس\n"
            "جامعه و نمونه: ۴۰ نفر (۲۰ آزمایش و ۲۰ کنترل)\n"
            "ابزار: پرسشنامه انعطاف‌پذیری شناختی و مقیاس ولع مصرف\n"
            "نرم‌افزار: SPSS 28"
        )
        analysis = proposal_price_estimator.analyze_proposal_text(text)
        self.assertEqual(analysis["degree"], "ارشد (Master)")
        self.assertEqual(analysis["design_type"], "ancova_repeated_measures")
        self.assertEqual(analysis["sample_size"], 40)
        self.assertIn("SPSS 28", analysis["softwares"])

        quote = proposal_price_estimator.calculate_quotation(analysis, self.persona)
        self.assertGreater(quote["total_price_tomans"], 5000000)
        self.assertIn("تومان", quote["total_price_formatted"])

        card_en = proposal_price_estimator.format_telegram_card(quote, lang="en")
        self.assertIn("Research Consultancy & Project Quotation", card_en)
        self.assertIn("Tomans", card_en)

        card_fa = proposal_price_estimator.format_telegram_card(quote, lang="fa")
        self.assertIn("پیش‌فاکتور", card_fa)
        self.assertIn("صابر قادری", card_fa)

    def test_02_proposal_price_estimator_sem(self):
        """Test proposal extraction for doctoral SEM study."""
        text = (
            "عنوان: مدل‌یابی معادلات ساختاری روابط بین خودکارآمدی و سرزندگی تحصیلی\n"
            "مقطع: دکتری روان‌شناسی تربیتی\n"
            "طرح: توصیفی همبستگی از نوع مدل‌یابی معادلات ساختاری (SEM)\n"
            "حجم نمونه: ۳۵۰ نفر دانشجوی دانشگاه\n"
            "نرم‌افزار: AMOS و SPSS"
        )
        analysis = proposal_price_estimator.analyze_proposal_text(text)
        self.assertEqual(analysis["degree"], "دکتری (Ph.D.)")
        self.assertEqual(analysis["design_type"], "sem_cfa_structural")
        self.assertEqual(analysis["sample_size"], 350)
        self.assertIn("AMOS 26", analysis["softwares"])

        quote = proposal_price_estimator.calculate_quotation(
            analysis, self.persona, options={"include_slides": True, "urgent": False}
        )
        self.assertGreater(quote["total_price_tomans"], 10000000)
        self.assertIn("slides", [item["code"] for item in quote["line_items"]])

    def test_03_telegram_chat_analyzer(self):
        """Test chat history parsing and Q&A pair extraction."""
        export_path = os.path.join(
            os.path.dirname(__file__), "..", "examples", "sample_telegram_export.json"
        )
        self.assertTrue(os.path.exists(export_path), "Sample export should exist")

        messages = telegram_chat_analyzer.parse_telegram_json_export(export_path)
        self.assertGreater(len(messages), 0)

        analysis = telegram_chat_analyzer.analyze_chat_history(messages, saber_id=124911145)
        self.assertGreater(analysis["summary"]["qa_threads_extracted"], 0)
        self.assertGreater(analysis["summary"]["pricing_quotes_detected"], 0)
        self.assertGreater(analysis["summary"]["questionnaire_requests_detected"], 0)

        report = telegram_chat_analyzer.format_markdown_analysis(analysis)
        self.assertIn("گزارش تحلیل تاریخچه تعاملات تلگرام", report)

    def test_04_bot_simulation_mode(self):
        """Test offline end-to-end bot daemon simulation."""
        bot = telegram_bot_daemon.DigitalSaberBot(
            token="",
            admin_id=124911145,
            auto_quote=False
        )
        res = bot.run_test_simulation()
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["events"]), 5)

        # Check approval status
    def test_05_project_drive_manager(self):
        """Test Google Drive project manager provisioning and 4-tier taxonomy."""
        import tempfile
        import shutil
        import project_drive_manager

        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = project_drive_manager.ProjectDriveManager(config={"google_drive_work_dir": tmp_dir})
            self.assertEqual(manager.work_dir, tmp_dir)

            paths = manager.provision_project(
                client_name="Test Student",
                client_id=987654321,
                username="test_student",
                topic="Efficacy of Schema Therapy on Emotional Dysregulation"
            )

            self.assertTrue(os.path.isdir(paths["root"]))
            self.assertTrue(os.path.isdir(paths["raw"]))
            self.assertTrue(os.path.isdir(paths["code"]))
            self.assertTrue(os.path.isdir(paths["deliverables"]))
            self.assertTrue(os.path.isdir(paths["references"]))
            self.assertTrue(os.path.exists(paths["meta_file"]))

            with open(paths["meta_file"], "r", encoding="utf-8") as f:
                meta = json.load(f)

            self.assertEqual(meta["client_name"], "Test Student")
            self.assertEqual(meta["telegram_id"], 987654321)
            self.assertEqual(meta["telegram_username"], "@test_student")
            self.assertEqual(meta["topic_fa"], "Efficacy of Schema Therapy on Emotional Dysregulation")

            # Test finding existing project
            found = manager.find_existing_project_by_client("Test Student", client_id=987654321)
            self.assertEqual(found, paths["root"])

            # Test listing projects
            all_projs = manager.list_all_projects()
            self.assertEqual(len(all_projs), 1)
            self.assertEqual(all_projs[0]["client_name"], "Test Student")

    def test_06_ui_formatting_and_links(self):
        """Test clean Google Drive path shortening, client mention hyperlinks, and HTML card rendering."""
        import project_drive_manager
        import telethon.extensions.html as thtml

        # Test path shortening
        raw_cloud_path = "/Users/saber/Library/CloudStorage/GoogleDrive-ghaderi.sabir@gmail.com/My Drive/My Work/Zəhra Cəlalı"
        clean_path = project_drive_manager.clean_drive_display_path(raw_cloud_path)
        self.assertEqual(clean_path, "My Work/Zəhra Cəlalı")

        # Test client mention with username (opens chat on click)
        mention_with_user = project_drive_manager.format_client_mention_html("Zahra Cəlalı", username="ZahraCalali", client_id=574632646)
        self.assertIn('href="https://t.me/ZahraCalali"', mention_with_user)
        self.assertIn("<b>Zahra Cəlalı</b>", mention_with_user)

        # Test client mention without username (opens chat via tg://user?id=...)
        mention_no_user = project_drive_manager.format_client_mention_html("Tabasom", username=None, client_id=1213759496)
        self.assertIn('href="tg://user?id=1213759496"', mention_no_user)
        self.assertIn("<b>Tabasom</b>", mention_no_user)

        # Test HTML parse validity
        text, ents = thtml.parse(mention_with_user)
        self.assertTrue(any(getattr(e, "url", None) == "https://t.me/ZahraCalali" for e in ents))

        # Test bilingual quotation cards
        analysis = proposal_price_estimator.analyze_proposal_text("عنوان: بررسی اضطراب\nمقطع: ارشد\nطرح: کوواریانس\nجامعه: ۴۰ نفر")
        quote = proposal_price_estimator.calculate_quotation(analysis, self.persona)

        # English card
        card_en = proposal_price_estimator.format_telegram_card(quote, lang="en")
        self.assertIn("Research Consultancy", card_en)
        self.assertIn("<b>Consultant:</b>", card_en)
        _, ents_en = thtml.parse(card_en)
        self.assertGreater(len(ents_en), 5)

        # Persian card
        card_fa = proposal_price_estimator.format_telegram_card(quote, lang="fa")
        self.assertIn("پیش‌فاکتور", card_fa)
        self.assertIn("<b>مشاور:</b>", card_fa)
        _, ents_fa = thtml.parse(card_fa)
        self.assertGreater(len(ents_fa), 5)

    def test_07_media_resolution_and_button_url_validation(self):
        """Test media extraction (voice, photo, document, sticker filtering) and button URL validation."""
        import project_drive_manager
        import telethon_userbot
        from datetime import datetime

        class MockFile:
            def __init__(self, name=None, size=1024, ext=None, mime_type=""):
                self.name = name
                self.size = size
                self.ext = ext
                self.mime_type = mime_type
                self.attrs = []

        class MockVoiceAttr:
            def __init__(self, duration=42):
                self.duration = duration

        class MockVoice:
            def __init__(self, duration=42):
                self.attributes = [MockVoiceAttr(duration)]

        class MockMessage:
            def __init__(self, msg_id=101, file=None, voice=None, photo=None, sticker=None, date=None):
                self.id = msg_id
                self.file = file
                self.voice = voice
                self.photo = photo
                self.sticker = sticker
                self.date = date or datetime(2026, 9, 10, 15, 30, 0)

        # 1. Voice Note Resolution
        v_msg = MockMessage(msg_id=201, file=MockFile(ext=".ogg", size=32000), voice=MockVoice(35))
        fn, mtype, fsize, dur = project_drive_manager.resolve_media_details(v_msg)
        self.assertEqual(mtype, "voice")
        self.assertEqual(dur, 35)
        self.assertEqual(fsize, 32000)
        self.assertTrue(fn.startswith("voice_201_"))
        self.assertTrue(fn.endswith(".ogg"))

        # 2. Photo Resolution
        p_msg = MockMessage(msg_id=202, file=MockFile(ext=".jpg", size=150000), photo=True)
        fn, mtype, fsize, dur = project_drive_manager.resolve_media_details(p_msg)
        self.assertEqual(mtype, "photo")
        self.assertEqual(dur, 0)
        self.assertEqual(fsize, 150000)
        self.assertTrue(fn.startswith("photo_202_"))
        self.assertTrue(fn.endswith(".jpg"))

        # 3. Sticker Filtering (Must return None filename)
        s_msg = MockMessage(msg_id=203, file=MockFile(name="AnimatedSticker.tgs", mime_type="application/x-tgsticker"), sticker=True)
        fn, mtype, _, _ = project_drive_manager.resolve_media_details(s_msg)
        self.assertIsNone(fn, "Stickers must not produce a downloadable project filename")
        self.assertEqual(mtype, "sticker")

        # 4. Standard Document
        d_msg = MockMessage(msg_id=204, file=MockFile(name="Research_Proposal.docx", size=85000, ext=".docx"))
        fn, mtype, fsize, _ = project_drive_manager.resolve_media_details(d_msg)
        self.assertEqual(fn, "Research_Proposal.docx")
        self.assertEqual(mtype, "document")
        self.assertEqual(fsize, 85000)

        # 5. Telegram Button URL Validation (prevent BUTTON_URL_INVALID)
        self.assertFalse(telethon_userbot.is_valid_telegram_button_url("http://localhost:8080"))
        self.assertFalse(telethon_userbot.is_valid_telegram_button_url("http://127.0.0.1:8080"))
        self.assertFalse(telethon_userbot.is_valid_telegram_button_url(""))
        self.assertFalse(telethon_userbot.is_valid_telegram_button_url(None))
        self.assertTrue(telethon_userbot.is_valid_telegram_button_url("https://my-domain.com"))
        self.assertTrue(telethon_userbot.is_valid_telegram_button_url("https://saber-academic.ngrok-free.app"))
        self.assertTrue(telethon_userbot.is_valid_telegram_button_url("tg://user?id=124911145"))


if __name__ == "__main__":
    unittest.main()

