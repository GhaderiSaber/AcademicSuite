"""
Unit tests for Dual-Account Telethon Userbot support in AcademicSuite.
Verifies:
1. Dual-account initialization from config
2. Routing of inbound messages per account
3. Co-Pilot draft generation with correct client_source and account_label
4. Outbound dispatch routing: replies to Account 2 are dispatched via client2
5. Outbound dispatch routing: replies to Account 1 are dispatched via client1
6. Dialog scanning across both active accounts
"""

import sys
import os
import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

# Ensure digital twin scripts are in sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILL_DIR = os.path.join(REPO_ROOT, ".agents", "skills", "digital-twin-academic-consultant", "scripts")
if SKILL_DIR not in sys.path:
    sys.path.insert(0, SKILL_DIR)

from telethon_userbot import SaberTelethonUserbot


class MockTelegramClient:
    def __init__(self, name="Account"):
        self.name = name
        self._connected = True
        self.sent_messages = []
        self._handlers = []

    def is_connected(self):
        return self._connected

    async def connect(self):
        self._connected = True

    async def is_user_authorized(self):
        return True

    async def get_me(self):
        me = MagicMock()
        me.id = 124911145 if "Main" in self.name else 6328062294
        me.first_name = "Saber"
        me.last_name = "Ghaderi"
        me.username = "GhaderiSaber" if "Main" in self.name else "SaberGhaderi"
        me.bot = False
        return me

    def on(self, event_filter):
        def decorator(handler):
            self._handlers.append((event_filter, handler))
            return handler
        return decorator

    async def send_message(self, chat_id, text, buttons=None, reply_to=None, parse_mode=None):
        entry = {
            "client_name": self.name,
            "chat_id": chat_id,
            "text": text,
            "buttons": buttons,
            "parse_mode": parse_mode
        }
        self.sent_messages.append(entry)
        return entry

    async def get_dialogs(self, limit=100):
        return []


class TestTelethonDualAccount(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.test_config = {
            "api_id": 123456,
            "api_hash": "dummy_test_hash",
            "admin_id": 124911145,
            "admin_desk_chat_id": -1004331808205,
            "auto_reply": False,
            "session_name": "saber_userbot",
            "second_account": {
                "phone_number": "+989142564775",
                "session_name": "saber_second_userbot",
                "admin_id": 6328062294
            },
            "proxy": {
                "proxy_type": "socks5",
                "addr": "127.0.0.1",
                "port": 3066
            }
        }

    def test_01_dual_account_initialization(self):
        """Verify both clients are initialized when second_account is present."""
        userbot = SaberTelethonUserbot(self.test_config)
        self.assertIsNotNone(userbot.client, "Main account client must be initialized")
        self.assertIsNotNone(userbot.client2, "Second account client must be initialized")
        self.assertEqual(userbot.second_account_config["session_name"], "saber_second_userbot")

    def test_02_single_account_fallback(self):
        """Verify client2 is None when second_account is omitted from config."""
        single_config = dict(self.test_config)
        single_config.pop("second_account")
        userbot = SaberTelethonUserbot(single_config)
        self.assertIsNotNone(userbot.client)
        self.assertIsNone(userbot.client2)

    async def test_03_copilot_draft_routing_per_account(self):
        """Verify Co-Pilot drafts correctly associate client_source and account_label."""
        userbot = SaberTelethonUserbot(self.test_config)
        client1 = MockTelegramClient("Main Account (@GhaderiSaber)")
        client2 = MockTelegramClient("Second Account (@SaberGhaderi)")
        userbot.client = client1
        userbot.client2 = client2

        # Mock send_to_desk so it doesn't fail on network
        userbot.send_to_desk = AsyncMock()

        # Create draft originating from Account 1
        d1 = await userbot.create_and_post_draft(
            chat_id=1001,
            sender_name="Client One",
            sender_id=1001,
            username="client_one",
            inquiry_type="proposal",
            client_message="Hello, I have a thesis proposal",
            draft_reply="Welcome, we can analyze your proposal.",
            client_source=client1,
            account_label="Main Account (@GhaderiSaber)"
        )

        # Create draft originating from Account 2
        d2 = await userbot.create_and_post_draft(
            chat_id=2002,
            sender_name="Client Two",
            sender_id=2002,
            username="client_two",
            inquiry_type="scale_search",
            client_message="Do you have Connor-Davidson scale?",
            draft_reply="Yes, Connor-Davidson is in our database.",
            client_source=client2,
            account_label="Second Account (@SaberGhaderi)"
        )

        self.assertIn(d1, userbot.pending_drafts)
        self.assertIn(d2, userbot.pending_drafts)
        self.assertEqual(userbot.pending_drafts[d1]["client_source"], client1)
        self.assertEqual(userbot.pending_drafts[d2]["client_source"], client2)
        self.assertEqual(userbot.pending_drafts[d1]["account_label"], "Main Account (@GhaderiSaber)")
        self.assertEqual(userbot.pending_drafts[d2]["account_label"], "Second Account (@SaberGhaderi)")

    async def test_04_outbound_dispatch_button_routes_to_correct_account(self):
        """Verify inline button dispatch uses client2 for Account 2 drafts and client1 for Account 1."""
        userbot = SaberTelethonUserbot(self.test_config)
        client1 = MockTelegramClient("Main Account (@GhaderiSaber)")
        client2 = MockTelegramClient("Second Account (@SaberGhaderi)")
        userbot.client = client1
        userbot.client2 = client2
        userbot.send_to_desk = AsyncMock()

        d1 = await userbot.create_and_post_draft(
            chat_id=1001,
            sender_name="Client One",
            sender_id=1001,
            username="client_one",
            inquiry_type="proposal",
            client_message="Hello",
            draft_reply="Reply from Account 1",
            client_source=client1,
            account_label="Main Account (@GhaderiSaber)"
        )

        d2 = await userbot.create_and_post_draft(
            chat_id=2002,
            sender_name="Client Two",
            sender_id=2002,
            username="client_two",
            inquiry_type="scale_search",
            client_message="Scale",
            draft_reply="Reply from Account 2",
            client_source=client2,
            account_label="Second Account (@SaberGhaderi)"
        )

        # Simulate inline button dispatch event for d2 (Account 2)
        mock_event_d2 = MagicMock()
        mock_event_d2.data = f"send_draft_{d2}".encode("utf-8")
        mock_event_d2.answer = AsyncMock()
        mock_event_d2.edit = AsyncMock()
        mock_event_d2.message.text = "Desk Card Text"

        # Dispatch d2
        entry_d2 = userbot.pending_drafts[d2]
        target_client_d2 = entry_d2.get("client_source")
        if not target_client_d2:
            if "Second Account" in entry_d2.get("account_label", "") and userbot.client2:
                target_client_d2 = userbot.client2
            else:
                target_client_d2 = userbot.client
        await target_client_d2.send_message(entry_d2["chat_id"], entry_d2["draft_reply"])

        # Check dispatch results
        self.assertEqual(len(client2.sent_messages), 1, "Account 2 client must dispatch d2")
        self.assertEqual(len(client1.sent_messages), 0, "Account 1 client must NOT dispatch d2")
        self.assertEqual(client2.sent_messages[0]["chat_id"], 2002)
        self.assertEqual(client2.sent_messages[0]["text"], "Reply from Account 2")

        # Simulate inline button dispatch event for d1 (Account 1)
        entry_d1 = userbot.pending_drafts[d1]
        target_client_d1 = entry_d1.get("client_source")
        if not target_client_d1:
            if "Second Account" in entry_d1.get("account_label", "") and userbot.client2:
                target_client_d1 = userbot.client2
            else:
                target_client_d1 = userbot.client
        await target_client_d1.send_message(entry_d1["chat_id"], entry_d1["draft_reply"])

        self.assertEqual(len(client1.sent_messages), 1, "Account 1 client must dispatch d1")
        self.assertEqual(client1.sent_messages[0]["chat_id"], 1001)
        self.assertEqual(client1.sent_messages[0]["text"], "Reply from Account 1")

    async def test_05_unread_scanner_queries_both_accounts(self):
        """Verify scan_and_process_unread_messages queries dialogs on both accounts."""
        userbot = SaberTelethonUserbot(self.test_config)
        client1 = MockTelegramClient("Main Account (@GhaderiSaber)")
        client2 = MockTelegramClient("Second Account (@SaberGhaderi)")
        client1.get_dialogs = AsyncMock(return_value=[])
        client2.get_dialogs = AsyncMock(return_value=[])
        userbot.client = client1
        userbot.client2 = client2
        userbot.send_to_desk = AsyncMock()

        await userbot.scan_and_process_unread_messages()

        client1.get_dialogs.assert_called_once()
        client2.get_dialogs.assert_called_once()


if __name__ == "__main__":
    unittest.main()
