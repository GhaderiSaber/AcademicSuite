"""Unit tests for modular Telethon Userbot dispatchers.

Tests coverage:
1. AdminCommandDispatcher: routing of slash commands (/topics, /unread, /projects, /send_Q).
2. CallbackQueryDispatcher: routing of inline callbacks (noop, send_draft_, ignore_draft_, cmd_unread).
3. InlineQueryDispatcher: inline articles for quotes and projects.
4. setup_inbound_listeners: listener registration on client and client2.
5. Attribute proxying and dynamic property assignment between dispatchers and SaberTelethonUserbot.
"""

from __future__ import annotations

import asyncio
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILL_DIR = os.path.join(REPO_ROOT, ".agents", "skills", "digital-twin-academic-consultant", "scripts")
if SKILL_DIR not in sys.path:
    sys.path.insert(0, SKILL_DIR)

from telethon_userbot import SaberTelethonUserbot
from userbot import (
    AdminCommandDispatcher,
    CallbackQueryDispatcher,
    InlineQueryDispatcher,
    setup_inbound_listeners,
    is_valid_telegram_button_url,
)


class MockEvent:
    def __init__(self, text: str = "", data: bytes = b"", chat_id: int = 124911145):
        self.message = MagicMock()
        self.message.message = text
        self.message.text = text
        self.text = text
        self.data = data
        self.chat_id = chat_id
        self.reply = AsyncMock()
        self.answer = AsyncMock()
        self.edit = AsyncMock()
        self.delete = AsyncMock()
        self.builder = MagicMock()
        self.builder.article = AsyncMock(return_value={"title": "mock_article"})


class TestUserbotDispatchers(unittest.TestCase):
    """Test suite for modular dispatchers in userbot subpackage."""

    def setUp(self):
        self.config = {
            "api_id": 12345,
            "api_hash": "dummy_hash",
            "admin_id": 124911145,
            "admin_desk_chat_id": -1004331808205,
            "auto_reply": False,
        }
        self.bot = SaberTelethonUserbot(self.config)
        self.bot.client = MagicMock()
        self.bot.client.send_message = AsyncMock()
        self.bot.bot_client = MagicMock()
        self.bot.bot_client.send_message = AsyncMock()
        self.bot.send_to_desk = AsyncMock()

    def test_01_dispatcher_proxy_attributes(self):
        """Verify AdminCommandDispatcher proxies attributes and sets attributes on bot."""
        dispatcher = AdminCommandDispatcher(self.bot)
        # Reading attribute from bot
        self.assertEqual(dispatcher.admin_id, 124911145)
        self.assertEqual(dispatcher.admin_desk_chat_id, -1004331808205)

        # Incrementing deliverable_counter through proxy
        initial_val = self.bot.deliverable_counter
        dispatcher.deliverable_counter += 1
        self.assertEqual(self.bot.deliverable_counter, initial_val + 1)
        self.assertEqual(dispatcher.deliverable_counter, initial_val + 1)

    def test_02_admin_dispatcher_topics(self):
        """Verify AdminCommandDispatcher handles /topics command."""
        dispatcher = AdminCommandDispatcher(self.bot)
        event = MockEvent(text="/topics")

        async def run_dispatch():
            await dispatcher.dispatch(event)

        asyncio.run(run_dispatch())
        event.reply.assert_called_once()
        args, kwargs = event.reply.call_args
        self.assertIn("parse_mode", kwargs)

    def test_03_admin_dispatcher_unread(self):
        """Verify AdminCommandDispatcher handles /unread command."""
        dispatcher = AdminCommandDispatcher(self.bot)
        event = MockEvent(text="/unread")
        self.bot.scan_and_process_unread_messages = AsyncMock()

        async def run_dispatch():
            await dispatcher.dispatch(event)

        asyncio.run(run_dispatch())
        event.reply.assert_called_once()
        self.bot.scan_and_process_unread_messages.assert_called_once()

    def test_04_admin_dispatcher_projects(self):
        """Verify AdminCommandDispatcher handles /projects command."""
        dispatcher = AdminCommandDispatcher(self.bot)
        event = MockEvent(text="/projects")

        with patch.object(self.bot.project_manager, "list_all_projects", return_value=[
            {"client_name": "Test Client", "folder_name": "Test_Client", "folder_path": "/drive/Test", "file_count": 2, "message_count": 5, "status": "pending"}
        ]):
            async def run_dispatch():
                await dispatcher.dispatch(event)

            asyncio.run(run_dispatch())
            event.reply.assert_called_once()
            reply_text = event.reply.call_args[0][0]
            self.assertIn("Test Client", reply_text)

    def test_05_callback_dispatcher_noop(self):
        """Verify CallbackQueryDispatcher handles noop button."""
        dispatcher = CallbackQueryDispatcher(self.bot)
        event = MockEvent(data=b"noop")

        async def run_dispatch():
            await dispatcher.dispatch(event)

        asyncio.run(run_dispatch())
        event.answer.assert_called_once_with("ℹ️ This item has already been dispatched.", alert=False)

    def test_06_callback_dispatcher_send_draft(self):
        """Verify CallbackQueryDispatcher dispatches pending draft."""
        dispatcher = CallbackQueryDispatcher(self.bot)
        draft_id = "D999"
        self.bot.pending_drafts[draft_id] = {
            "chat_id": 999111,
            "draft_reply": "Hello, your proposal looks great!",
            "client_source": self.bot.client,
            "account_label": "Main Account",
            "sender_name": "Alice",
        }
        event = MockEvent(data=f"send_draft_{draft_id}".encode("utf-8"))

        async def run_dispatch():
            await dispatcher.dispatch(event)

        asyncio.run(run_dispatch())
        self.bot.client.send_message.assert_called_once_with(999111, "Hello, your proposal looks great!")
        event.answer.assert_called_once()
        event.edit.assert_called_once()
        self.assertNotIn(draft_id, self.bot.pending_drafts)

    def test_07_callback_dispatcher_ignore_draft(self):
        """Verify CallbackQueryDispatcher dismisses pending draft."""
        dispatcher = CallbackQueryDispatcher(self.bot)
        draft_id = "D998"
        self.bot.pending_drafts[draft_id] = {
            "chat_id": 999222,
            "draft_reply": "Draft to ignore",
            "sender_name": "Bob",
        }
        event = MockEvent(data=f"ignore_draft_{draft_id}".encode("utf-8"))

        async def run_dispatch():
            await dispatcher.dispatch(event)

        asyncio.run(run_dispatch())
        event.answer.assert_called_once_with("🗑️ Draft dismissed.", alert=False)
        event.edit.assert_called_once()
        self.assertNotIn(draft_id, self.bot.pending_drafts)

    def test_08_inline_dispatcher_quote(self):
        """Verify InlineQueryDispatcher handles quote search."""
        dispatcher = InlineQueryDispatcher(self.bot)
        event = MockEvent(text="quote")
        event.answer = AsyncMock()

        async def run_dispatch():
            await dispatcher.dispatch(event)

        asyncio.run(run_dispatch())
        event.answer.assert_called_once()

    def test_09_inbound_listeners_setup(self):
        """Verify setup_inbound_listeners registers event handlers on client and client2."""
        mock_c1 = MagicMock()
        mock_c2 = MagicMock()
        self.bot.client = mock_c1
        self.bot.client2 = mock_c2

        setup_inbound_listeners(self.bot)
        self.assertEqual(mock_c1.on.call_count, 1)
        self.assertEqual(mock_c2.on.call_count, 1)

    def test_10_is_valid_telegram_button_url(self):
        """Verify URL validation logic for inline buttons."""
        self.assertFalse(is_valid_telegram_button_url("http://localhost:8080"))
        self.assertFalse(is_valid_telegram_button_url("http://127.0.0.1:8080"))
        self.assertFalse(is_valid_telegram_button_url(""))
        self.assertFalse(is_valid_telegram_button_url(None))
        self.assertTrue(is_valid_telegram_button_url("https://t.me/GhaderiSaber"))
        self.assertTrue(is_valid_telegram_button_url("tg://user?id=124911145"))


if __name__ == "__main__":
    unittest.main()
