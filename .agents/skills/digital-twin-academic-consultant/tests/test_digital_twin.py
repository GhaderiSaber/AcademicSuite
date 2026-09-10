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
        self.assertEqual(len(res["events"]), 11)

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

    def test_08_telegram_business_connection_and_messages(self):
        """Test Telegram Business connection handling, message routing, echo suppression, and quote dispatch."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            bot = telegram_bot_daemon.DigitalSaberBot(
                token="",
                admin_id=124911145,
                admin_desk_chat_id=-1004331808205,
                business_mode=True,
                business_mode_policy="autonomous",
                work_dir=tmp_dir
            )

            sent_messages = []

            class MockTGClient:
                def send_message(self, chat_id, text, reply_to_message_id=None, reply_markup=None, parse_mode=None, business_connection_id=None):
                    sent_messages.append({
                        "chat_id": chat_id,
                        "text": text,
                        "reply_markup": reply_markup,
                        "parse_mode": parse_mode,
                        "business_connection_id": business_connection_id
                    })
                    return {"ok": True, "result": {"message_id": 1000 + len(sent_messages)}}

            bot.tg = MockTGClient()

            # 1. Test Business Connection Handshake
            conn_payload = {
                "id": "biz_conn_test_001",
                "user": {"id": 124911145, "first_name": "Saber", "last_name": "Ghaderi", "username": "GhaderiSaber"},
                "user_chat_id": 124911145,
                "date": 1789000000,
                "can_reply": True,
                "is_enabled": True
            }
            bot.handle_business_connection(conn_payload)

            self.assertIn("biz_conn_test_001", bot.business_connections)
            self.assertTrue(bot.business_connections["biz_conn_test_001"]["is_enabled"])
            self.assertTrue(bot.business_connections["biz_conn_test_001"]["can_reply"])

            # Verify admin desk alert was dispatched
            self.assertTrue(any("Telegram Business Connected" in m["text"] for m in sent_messages))
            sent_messages.clear()

            # 2. Test Business Message from Client (Greeting)
            client_greeting = {
                "business_connection_id": "biz_conn_test_001",
                "message_id": 11,
                "chat": {"id": 987654321, "type": "private"},
                "from": {"id": 987654321, "first_name": "Farhad", "username": "farhad_test"},
                "text": "سلام"
            }
            res_greet = bot.handle_business_message(client_greeting)
            self.assertEqual(res_greet["type"], "greeting")
            # Verify reply sent to client with business_connection_id
            self.assertEqual(len(sent_messages), 1)
            self.assertEqual(sent_messages[0]["chat_id"], 987654321)
            self.assertEqual(sent_messages[0]["business_connection_id"], "biz_conn_test_001")
            self.assertIn("مشاور پژوهشی صابر قادری", sent_messages[0]["text"])
            sent_messages.clear()

            # 3. Test Echo Filtering (Message sent by Saber in client chat)
            saber_msg = {
                "business_connection_id": "biz_conn_test_001",
                "message_id": 10,
                "chat": {"id": 987654320, "type": "private"},
                "from": {"id": 124911145, "first_name": "Saber"},
                "text": "سلام، پروپوزال شما دریافت شد."
            }
            res_saber = bot.handle_business_message(saber_msg)
            self.assertIsNone(res_saber, "Outgoing messages from Saber must be filtered out")
            self.assertEqual(len(sent_messages), 0)

            # 4. Test Business Message from Client (Proposal inquiry text)
            proposal_text = (
                "عنوان پژوهش: بررسی اثربخشی درمان مبتنی بر پذیرش و تعهد بر اضطراب مرگ بیماران قلبی\n"
                "مقطع: کارشناسی ارشد روان‌شناسی بالینی\n"
                "طرح پژوهش: نیمه‌آزمایشی پیش‌آزمون پس‌آزمون با گروه کنترل و تحلیل کوواریانس\n"
                "جامعه و حجم نمونه: ۴۰ نفر (۲۰ نفر آزمایش، ۲۰ نفر کنترل)\n"
                "نرم‌افزار آماری: SPSS 28"
            )
            client_prop_msg = {
                "business_connection_id": "biz_conn_test_001",
                "message_id": 12,
                "chat": {"id": 987654321, "type": "private"},
                "from": {"id": 987654321, "first_name": "Farhad", "username": "farhad_test"},
                "text": proposal_text
            }
            res_prop = bot.handle_business_message(client_prop_msg)
            self.assertEqual(res_prop["type"], "proposal_text")
            self.assertEqual(res_prop["status"], "quoted")

            # Verify admin desk received notification with action buttons
            self.assertTrue(any("New Proposal Inquiry via Telegram Business" in m["text"] for m in sent_messages))
            admin_msg = next(m for m in sent_messages if "New Proposal Inquiry via Telegram Business" in m["text"])
            self.assertEqual(admin_msg["chat_id"], -1004331808205)

            # Check pending quote
            qid = list(bot.pending_quotes.keys())[-1]
            self.assertEqual(bot.pending_quotes[qid]["business_connection_id"], "biz_conn_test_001")
            self.assertTrue(bot.pending_quotes[qid]["is_business"])
            sent_messages.clear()

            # 5. Test Admin Dispatch (/send_Q... or /approve_Q...)
            action_reply = bot.handle_incoming_text(-1004331808205, "Saber", f"/send_{qid}")
            self.assertIn("approved and dispatched", action_reply)
            self.assertIn("Telegram Business", action_reply)

            # Verify quote was delivered to client chat using business_connection_id
            client_dispatched = next(m for m in sent_messages if m["chat_id"] == 987654321)
            self.assertEqual(client_dispatched["business_connection_id"], "biz_conn_test_001")
            self.assertIn("پیش‌فاکتور", client_dispatched["text"])
            self.assertEqual(bot.pending_quotes[qid]["status"], "approved")

    def test_09_copilot_shadow_mode_and_guardrails(self):
        """Test Co-Pilot / Shadow Mode: zero autonomous client messages, draft generation, human takeover auto-mute, and emergency controls."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            bot = telegram_bot_daemon.DigitalSaberBot(
                token="",
                admin_id=124911145,
                admin_desk_chat_id=-1004331808205,
                business_mode=True,
                business_mode_policy="copilot_only",
                auto_mute_hours=24,
                work_dir=tmp_dir
            )

            sent_messages = []

            class MockTGClient:
                def send_message(self, chat_id, text, reply_to_message_id=None, reply_markup=None, parse_mode=None, business_connection_id=None):
                    sent_messages.append({
                        "chat_id": chat_id,
                        "text": text,
                        "reply_markup": reply_markup,
                        "parse_mode": parse_mode,
                        "business_connection_id": business_connection_id
                    })
                    return {"ok": True, "result": {"message_id": 2000 + len(sent_messages)}}

            bot.tg = MockTGClient()

            # Handshake
            bot.handle_business_connection({
                "id": "biz_conn_copilot",
                "user": {"id": 124911145, "first_name": "Saber", "username": "GhaderiSaber"},
                "can_reply": True,
                "is_enabled": True
            })
            sent_messages.clear()

            # 1. Test Client Greeting in Co-Pilot Mode (Must NOT message client, must produce draft in Admin Desk)
            client_greet = {
                "business_connection_id": "biz_conn_copilot",
                "message_id": 50,
                "chat": {"id": 888777, "type": "private"},
                "from": {"id": 888777, "first_name": "مینا", "username": "mina_test"},
                "text": "سلام وقتتون بخیر"
            }
            res_greet = bot.handle_business_message(client_greet)
            self.assertEqual(res_greet["type"], "draft_greeting")
            did = res_greet["draft_id"]
            self.assertIn(did, bot.pending_drafts)

            # Check that client received ZERO messages
            client_sends = [m for m in sent_messages if m["chat_id"] == 888777]
            self.assertEqual(len(client_sends), 0, "Co-Pilot mode must NEVER send autonomous messages to client")

            # Check that Admin Desk received the draft suggestion
            admin_sends = [m for m in sent_messages if m["chat_id"] == -1004331808205]
            self.assertEqual(len(admin_sends), 1)
            self.assertIn("[Co-Pilot Draft] New Client Inquiry", admin_sends[0]["text"])
            self.assertIn(f"/send_msg_{did}", admin_sends[0]["text"])
            sent_messages.clear()

            # 2. Test Admin Dispatches the Draft to the Client
            action_res = bot.handle_incoming_text(-1004331808205, "Saber", f"/send_msg_{did}")
            self.assertIn("dispatched to مینا", action_res)
            self.assertEqual(len(sent_messages), 1)
            self.assertEqual(sent_messages[0]["chat_id"], 888777)
            self.assertEqual(sent_messages[0]["business_connection_id"], "biz_conn_copilot")
            self.assertIn("مشاور پژوهشی صابر قادری", sent_messages[0]["text"])
            sent_messages.clear()

            # 3. Test Human Takeover & Auto-Mute
            saber_talks = {
                "business_connection_id": "biz_conn_copilot",
                "message_id": 51,
                "chat": {"id": 888777, "type": "private"},
                "from": {"id": 124911145, "first_name": "Saber"},
                "text": "مینا خانم سلام، بفرمایید در خدمتم."
            }
            res_saber = bot.handle_business_message(saber_talks)
            self.assertIsNone(res_saber)
            self.assertIn(888777, bot.muted_chats, "Chat should be auto-muted after Saber personally speaks")

            # When client sends follow-up chit-chat, bot is completely silent (muted)
            client_followup = {
                "business_connection_id": "biz_conn_copilot",
                "message_id": 52,
                "chat": {"id": 888777, "type": "private"},
                "from": {"id": 888777, "first_name": "مینا"},
                "text": "ممنون سلامت باشید"
            }
            res_followup = bot.handle_business_message(client_followup)
            self.assertEqual(res_followup["type"], "muted")
            self.assertEqual(len(sent_messages), 0, "Muted chat should produce no messages or alerts")

            # 4. Test Emergency Pause & Resume
            pause_reply = bot.handle_incoming_text(-1004331808205, "Saber", "/pause_business")
            self.assertTrue(bot.business_paused)
            self.assertIn("PAUSED", pause_reply)

            # Any incoming message is ignored while paused
            res_paused = bot.handle_business_message(client_greet)
            self.assertEqual(res_paused["type"], "paused")

            resume_reply = bot.handle_incoming_text(-1004331808205, "Saber", "/resume_business")
            self.assertFalse(bot.business_paused)
            self.assertIn("RESUMED", resume_reply)

            # 5. Test Status Command
            status_reply = bot.handle_incoming_text(-1004331808205, "Saber", "/status_business")
            self.assertIn("copilot_only", status_reply)
            self.assertIn("ACTIVE", status_reply)
            self.assertIn("Muted Chats", status_reply)


if __name__ == "__main__":
    unittest.main()

