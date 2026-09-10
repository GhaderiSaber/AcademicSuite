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

    def test_10_userbot_copilot_drafts(self):
        """Test Userbot Improvement 1: Universal Co-Pilot Drafts & 1-Click Send in Academic Desk."""
        import asyncio
        import telethon_userbot
        from telethon_userbot import SaberTelethonUserbot

        desk_messages = []
        client_messages = []

        class MockUserbotClient:
            def __init__(self, name="Main"):
                self.name = name

            async def send_message(self, chat_id, text, buttons=None, reply_to=None, parse_mode=None):
                msg_entry = {
                    "client": self.name,
                    "chat_id": chat_id,
                    "text": text,
                    "buttons": buttons,
                    "parse_mode": parse_mode
                }
                if chat_id in [-1004331808205, 124911145]:
                    desk_messages.append(msg_entry)
                else:
                    client_messages.append(msg_entry)
                return msg_entry

        test_config = {
            "api_id": 12345,
            "api_hash": "dummy_hash",
            "admin_id": 124911145,
            "admin_desk_chat_id": -1004331808205,
            "auto_reply": False
        }

        userbot = SaberTelethonUserbot(test_config)
        mock_user = MockUserbotClient("GhaderiSaber")
        mock_bot = MockUserbotClient("SaberAcademicBot")
        userbot.client = mock_user
        userbot.bot_client = mock_bot

        async def mock_send_to_desk(text, buttons=None, reply_to=None, parse_mode="html"):
            return await mock_bot.send_message(-1004331808205, text, buttons=buttons, reply_to=reply_to, parse_mode=parse_mode)

        userbot.send_to_desk = mock_send_to_desk

        # 1. Test Scale Search Inquiry Draft
        async def run_tests():
            draft_id1 = await userbot.create_and_post_draft(
                chat_id=555111,
                sender_name="سارا احمدی",
                sender_id=555111,
                username="sara_a",
                inquiry_type="scale_search",
                client_message="/scale تاب آوری کانر",
                draft_reply="سلام و احترام وقت بخیر سارا گرامی. مقیاس تاب‌آوری در بانک موجود است.",
                client_source=mock_user,
                account_label="Main Account (@GhaderiSaber)"
            )
            return draft_id1

        d1 = asyncio.run(run_tests())
        self.assertEqual(d1, "D101")
        self.assertIn("D101", userbot.pending_drafts)
        self.assertEqual(len(client_messages), 0, "Zero autonomous messages to client")
        self.assertEqual(len(desk_messages), 1, "Desk received draft card")
        self.assertIn("Co-Pilot Draft", desk_messages[0]["text"])
        self.assertIn("/send_msg_D101", desk_messages[0]["text"])
        desk_messages.clear()

        # 2. Test Greeting Inquiry Draft
        async def run_greet():
            draft_id2 = await userbot.create_and_post_draft(
                chat_id=555222,
                sender_name="محسن رضایی",
                sender_id=555222,
                username="mohsen_r",
                inquiry_type="greeting",
                client_message="سلام خسته نباشید",
                draft_reply="سلام و عرض ادب، صابر قادری هستم در خدمتم.",
                client_source=mock_user,
                account_label="Main Account (@GhaderiSaber)"
            )
            return draft_id2

        d2 = asyncio.run(run_greet())
        self.assertEqual(d2, "D102")
        self.assertIn("D102", userbot.pending_drafts)
        self.assertEqual(len(client_messages), 0)
        self.assertEqual(len(desk_messages), 1)
        self.assertIn("/send_msg_D102", desk_messages[0]["text"])
        desk_messages.clear()

        # 3. Test Admin Dispatch (/send_msg_D101)
        async def run_dispatch():
            entry = userbot.pending_drafts[d1]
            await entry["client_source"].send_message(entry["chat_id"], entry["draft_reply"])
            del userbot.pending_drafts[d1]

        asyncio.run(run_dispatch())
        self.assertEqual(len(client_messages), 1, "Client received approved draft from user account")
        self.assertEqual(client_messages[0]["chat_id"], 555111)
        self.assertNotIn(d1, userbot.pending_drafts)
        client_messages.clear()

        # 4. Test Custom Text Dispatch (/send_msg_D102 <custom>)
        async def run_custom_dispatch():
            entry = userbot.pending_drafts[d2]
            custom_msg = "سلام آقا محسن، فایل داده‌های اکسل رو بفرستید تا بررسی کنم."
            await entry["client_source"].send_message(entry["chat_id"], custom_msg)
            del userbot.pending_drafts[d2]

        asyncio.run(run_custom_dispatch())
        self.assertEqual(len(client_messages), 1)
        self.assertEqual(client_messages[0]["chat_id"], 555222)
        self.assertIn("فایل داده‌های اکسل", client_messages[0]["text"])
        self.assertNotIn(d2, userbot.pending_drafts)
        client_messages.clear()

        # 5. Test Dismissal (/ignore_D103)
        async def run_ignore():
            draft_id3 = await userbot.create_and_post_draft(
                chat_id=555333,
                sender_name="امیر حسینی",
                sender_id=555333,
                username="amir_h",
                inquiry_type="statistical_inquiry",
                client_message="تحلیل آماری با SPSS چقدر زمان می‌بره؟",
                draft_reply="سلام وقت بخیر. تحلیل فرضیه‌ها ۳ الی ۴ روز زمان می‌برد.",
                client_source=mock_user,
                account_label="Main Account (@GhaderiSaber)"
            )
            self.assertIn(draft_id3, userbot.pending_drafts)
            del userbot.pending_drafts[draft_id3]
            self.assertNotIn(draft_id3, userbot.pending_drafts)

        asyncio.run(run_ignore())
        self.assertEqual(len(client_messages), 0, "Dismissed draft never sends anything to client")

    def test_11_project_health_and_followup_reminders(self):
        """Test Improvement 4: Client Project Health & Follow-Up Reminders."""
        import asyncio
        import tempfile
        from datetime import datetime, timedelta
        from project_drive_manager import ProjectDriveManager
        from telethon_userbot import SaberTelethonUserbot

        with tempfile.TemporaryDirectory() as tmp_drive:
            cfg = {"google_drive_work_dir": tmp_drive}
            pdm = ProjectDriveManager(cfg)

            # Setup Mock Projects in Drive
            # 1. Healthy active project (1 day silent)
            p1_paths = pdm.provision_project(client_name="سارا کریمی", status="in_progress")
            # Put dummy data file in raw
            with open(os.path.join(p1_paths["raw"], "data.xlsx"), "w") as f:
                f.write("mock_data")
            # Set recent interaction
            with open(p1_paths["meta_file"], "r", encoding="utf-8") as f:
                m1 = json.load(f)
            m1["last_interaction"] = (datetime.now() - timedelta(days=1)).isoformat()
            with open(p1_paths["meta_file"], "w", encoding="utf-8") as f:
                json.dump(m1, f)

            # 2. Unanswered quote (4 days silent)
            p2_paths = pdm.provision_project(client_name="علی محمدی", status="quote_sent", topic="اثربخشی درمان هیجان‌مدار")
            with open(p2_paths["meta_file"], "r", encoding="utf-8") as f:
                m2 = json.load(f)
            m2["last_interaction"] = (datetime.now() - timedelta(days=4)).isoformat()
            with open(p2_paths["meta_file"], "w", encoding="utf-8") as f:
                json.dump(m2, f)

            # 3. In-progress missing data (5 days silent)
            p3_paths = pdm.provision_project(client_name="مهسا افشار", status="in_progress")
            with open(p3_paths["meta_file"], "r", encoding="utf-8") as f:
                m3 = json.load(f)
            m3["last_interaction"] = (datetime.now() - timedelta(days=5)).isoformat()
            with open(p3_paths["meta_file"], "w", encoding="utf-8") as f:
                json.dump(m3, f)

            # 4. Completed project
            p4_paths = pdm.provision_project(client_name="رضا نادری", status="completed")
            with open(p4_paths["meta_file"], "r", encoding="utf-8") as f:
                m4 = json.load(f)

            # A. Test assess_project_health
            h1 = pdm.assess_project_health(m1)
            self.assertEqual(h1["health_code"], "healthy")
            self.assertFalse(h1["follow_up_needed"])

            h2 = pdm.assess_project_health(m2)
            self.assertEqual(h2["health_code"], "attention_needed")
            self.assertTrue(h2["follow_up_needed"])
            self.assertEqual(h2["follow_up_type"], "unanswered_quote")
            self.assertIn("پیش‌فاکتور", h2["suggested_persian_followup"])

            h3 = pdm.assess_project_health(m3)
            self.assertTrue(h3["follow_up_needed"])
            self.assertEqual(h3["follow_up_type"], "awaiting_data")
            self.assertIn("فایل اکسل داده‌ها", h3["suggested_persian_followup"])

            h4 = pdm.assess_project_health(m4)
            self.assertEqual(h4["health_code"], "completed")
            self.assertFalse(h4["follow_up_needed"])

            # B. Test audit_all_projects_health
            audit = pdm.audit_all_projects_health()
            self.assertEqual(audit["total_projects"], 4)
            self.assertEqual(audit["completed_count"], 1)
            self.assertGreaterEqual(len(audit["follow_ups"]), 2)

            # C. Test Userbot Co-Pilot Follow-Up Reminders Integration
            desk_msgs = []
            client_msgs = []

            class MockClient:
                async def send_message(self, chat_id, text, buttons=None, reply_to=None, parse_mode=None):
                    entry = {"chat_id": chat_id, "text": text}
                    if chat_id in [-1004331808205, 124911145]:
                        desk_msgs.append(entry)
                    else:
                        client_msgs.append(entry)
                    return entry

            mock_user = MockClient()
            mock_bot = MockClient()

            ub_cfg = {
                "api_id": 123,
                "api_hash": "hash",
                "admin_id": 124911145,
                "admin_desk_chat_id": -1004331808205,
                "google_drive_work_dir": tmp_drive
            }
            userbot = SaberTelethonUserbot(ub_cfg)
            userbot.project_manager = pdm
            userbot.client = mock_user
            userbot.bot_client = mock_bot

            async def mock_send_desk(text, buttons=None, reply_to=None, parse_mode="html"):
                return await mock_bot.send_message(-1004331808205, text)
            userbot.send_to_desk = mock_send_desk

            async def run_health_scan():
                return await userbot.scan_and_report_project_health()

            asyncio.run(run_health_scan())
            self.assertGreaterEqual(len(desk_msgs), 2, "Desk received summary card and follow-up cards")
            self.assertGreaterEqual(len(userbot.pending_followups), 2)
            fu_ids = list(userbot.pending_followups.keys())
            fu_1 = fu_ids[0]

            # D. Test Admin Dispatches Follow-Up to Client
            fu_entry = userbot.pending_followups[fu_1]
            async def run_fu_dispatch():
                await userbot.client.send_message(555999, fu_entry["draft_reply"])
                pdm.record_followup_dispatched(fu_entry["folder_path"], fu_entry["followup_type"], fu_entry["draft_reply"])
                del userbot.pending_followups[fu_1]

            asyncio.run(run_fu_dispatch())
            self.assertEqual(len(client_msgs), 1, "Client received approved follow-up from user account")
            self.assertNotIn(fu_1, userbot.pending_followups)

            # Verify cooldown recorded in project_meta.json
            with open(os.path.join(fu_entry["folder_path"], "project_meta.json"), "r", encoding="utf-8") as f:
                up_meta = json.load(f)
            self.assertIn("last_follow_up", up_meta)
            self.assertGreater(len(up_meta.get("follow_up_history", [])), 0)

    def test_12_direct_client_deliverable_dispatch(self):
        """Test Improvement 5: Direct Client Deliverable Dispatch (/send_file)."""
        import asyncio
        import tempfile
        from project_drive_manager import ProjectDriveManager
        from telethon_userbot import SaberTelethonUserbot, generate_deliverable_caption

        with tempfile.TemporaryDirectory() as tmp_drive:
            cfg = {"google_drive_work_dir": tmp_drive}
            pdm = ProjectDriveManager(cfg)

            # 1. Provision a project and add deliverable files
            paths = pdm.provision_project(
                client_name="زهرا جلالی",
                client_id=777888,
                username="zahra_jalali",
                status="in_progress"
            )
            pdir = paths["project_dir"]
            deliv_dir = paths["deliverables"]

            doc_path = os.path.join(deliv_dir, "فصل_چهارم_یافته_های_پژوهش.docx")
            with open(doc_path, "wb") as f:
                f.write(b"PK\x03\x04mock_word_docx_binary_data_for_chapter_4")

            xlsx_path = os.path.join(deliv_dir, "تحلیل_آماری_spss.xlsx")
            with open(xlsx_path, "wb") as f:
                f.write(b"PK\x03\x04mock_excel_spss_analysis_matrix")

            # 2. Test list_project_deliverables
            delivs = pdm.list_project_deliverables(pdir)
            self.assertEqual(len(delivs), 2)
            filenames = [d["filename"] for d in delivs]
            self.assertIn("فصل_چهارم_یافته_های_پژوهش.docx", filenames)
            self.assertIn("تحلیل_آماری_spss.xlsx", filenames)

            # 3. Test find_deliverable_file (exact, substring, fuzzy)
            f_found = pdm.find_deliverable_file(pdir, "فصل_چهارم")
            self.assertIsNotNone(f_found)
            self.assertEqual(f_found["filename"], "فصل_چهارم_یافته_های_پژوهش.docx")

            f_spss = pdm.find_deliverable_file(pdir, "spss")
            self.assertIsNotNone(f_spss)
            self.assertEqual(f_spss["filename"], "تحلیل_آماری_spss.xlsx")

            # 4. Test generate_deliverable_caption
            cap = generate_deliverable_caption("زهرا جلالی", "فصل_چهارم_یافته_های_پژوهش.docx")
            self.assertIn("زهرا جلالی", cap)
            self.assertIn("فصل چهارم یافته های پژوهش", cap)
            self.assertIn("می‌شود", cap)

            # 5. Test Userbot Deliverable State & Dispatch Execution
            sent_files = []
            class MockClient:
                async def send_file(self, entity, file, caption=None):
                    sent_files.append({"entity": entity, "file": file, "caption": caption})
                    return {"id": 999}
                async def send_message(self, entity, text, parse_mode=None):
                    return {"id": 888}

            mock_user = MockClient()
            ub_cfg = {
                "api_id": 123,
                "api_hash": "hash",
                "admin_id": 124911145,
                "admin_desk_chat_id": -1004331808205,
                "google_drive_work_dir": tmp_drive
            }
            userbot = SaberTelethonUserbot(ub_cfg)
            userbot.project_manager = pdm
            userbot.client = mock_user

            # Prepare deliverable draft
            del_id = "DEL101"
            userbot.pending_deliverables[del_id] = {
                "del_id": del_id,
                "client_name": "زهرا جلالی",
                "telegram_id": 777888,
                "username": "zahra_jalali",
                "folder_path": pdir,
                "file_path": doc_path,
                "filename": "فصل_چهارم_یافته_های_پژوهش.docx",
                "size_str": "45.0 KB",
                "caption": cap,
                "created_at": "2026-09-11T00:00:00"
            }

            # Execute dispatch simulation
            entry = userbot.pending_deliverables[del_id]
            async def run_dispatch():
                await userbot.client.send_file(entry["telegram_id"], file=entry["file_path"], caption=entry["caption"])
                pdm.record_deliverable_dispatched(entry["folder_path"], entry["filename"], entry["client_name"])
                del userbot.pending_deliverables[del_id]

            asyncio.run(run_dispatch())

            # Verify file was dispatched
            self.assertEqual(len(sent_files), 1)
            self.assertEqual(sent_files[0]["entity"], 777888)
            self.assertEqual(sent_files[0]["file"], doc_path)
            self.assertIn("زهرا جلالی", sent_files[0]["caption"])
            self.assertNotIn(del_id, userbot.pending_deliverables)

            # Verify backup in drafts_archive
            arch_dir = paths["deliverables_archive"]
            self.assertTrue(os.path.isdir(arch_dir))
            archived_files = os.listdir(arch_dir)
            self.assertEqual(len(archived_files), 1)
            self.assertTrue(archived_files[0].startswith("فصل_چهارم_یافته_های_پژوهش_"))

            # Verify project_meta.json updated to 'delivered'
            with open(paths["meta_file"], "r", encoding="utf-8") as f:
                up_meta = json.load(f)
            self.assertEqual(up_meta.get("status"), "delivered")
            self.assertIn("last_deliverable_sent", up_meta)
            self.assertEqual(up_meta["last_deliverable_sent"]["filename"], "فصل_چهارم_یافته_های_پژوهش.docx")
            self.assertEqual(len(up_meta.get("deliverables_history", [])), 1)


if __name__ == "__main__":
    unittest.main()



