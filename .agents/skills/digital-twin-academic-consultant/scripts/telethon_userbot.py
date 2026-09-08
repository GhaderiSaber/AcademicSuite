#!/usr/bin/env python3
"""
Telethon MTProto Userbot - Digital Twin of Saber Ghaderi (telethon_userbot.py)
-----------------------------------------------------------------------------
Automates Saber's real personal Telegram account (@GhaderiSaber, ID: 124911145):
1. Runs directly as Saber's personal account (MTProto client) rather than a bot.
2. Directly crawls & exports actual client chats and proposals from Telegram servers
   without requiring manual Telegram Desktop JSON exports.
3. Listens in real-time to incoming client DMs (private chats).
4. Automatically detects proposals (.docx, .pdf, or text) and runs proposal_price_estimator.py.
5. Posts draft quotations to Saber's "Saved Messages" (me) for 1-tap review & approval.
6. Searches 4,880 psychometric questionnaires directly from Questionnaires.xlsx.
"""

import os
import re
import sys
import json
import asyncio
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    from telethon import TelegramClient, events
    from telethon.tl.types import DocumentAttributeFilename, User
except ImportError:
    TelegramClient = None
    events = None

# Local suite imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

try:
    from proposal_price_estimator import (
        analyze_proposal_text,
        calculate_quotation,
        format_telegram_card,
        extract_text_from_file,
        load_persona
    )
    from telegram_chat_analyzer import (
        analyze_chat_history,
        format_markdown_analysis
    )
except ImportError:
    pass

try:
    RESOLVER_SCRIPT_DIR = os.path.abspath(
        os.path.join(SCRIPT_DIR, "..", "..", "psychometric-scale-resolver", "scripts")
    )
    if os.path.isdir(RESOLVER_SCRIPT_DIR) and RESOLVER_SCRIPT_DIR not in sys.path:
        sys.path.insert(0, RESOLVER_SCRIPT_DIR)
    import questionnaire_resolver
except Exception:
    questionnaire_resolver = None


DEFAULT_CONFIG_PATH = os.path.join(SCRIPT_DIR, "telethon_config.json")
DEFAULT_SESSION_NAME = os.path.join(SCRIPT_DIR, "saber_userbot")
DEFAULT_STORAGE_DIR = os.path.join(SCRIPT_DIR, "userbot_storage")


def load_telethon_config(config_path: str = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    """Load MTProto credentials from telethon_config.json."""
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "api_id": 0,
        "api_hash": "",
        "phone_number": "",
        "session_name": DEFAULT_SESSION_NAME,
        "auto_reply": False,
        "saved_messages_desk": True
    }


def save_telethon_config(config: Dict[str, Any], config_path: str = DEFAULT_CONFIG_PATH):
    """Save config to file."""
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


class SaberTelethonUserbot:
    """MTProto client managing Saber's personal account automation."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_id = config.get("api_id")
        self.api_hash = config.get("api_hash")
        self.session_name = config.get("session_name", DEFAULT_SESSION_NAME)
        self.auto_reply = config.get("auto_reply", False)
        self.storage_dir = DEFAULT_STORAGE_DIR
        os.makedirs(self.storage_dir, exist_ok=True)

        self.persona = load_persona()
        self.pending_quotes: Dict[str, Dict[str, Any]] = {}
        self.quote_counter = 100

        if not self.api_id or not self.api_hash:
            self.client = None
        else:
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)

    async def init_client(self):
        """Connect and authenticate."""
        if not self.client:
            raise ValueError("api_id and api_hash must be set in telethon_config.json")
        await self.client.start(phone=self.config.get("phone_number"))
        me = await self.client.get_me()
        print(f"[+] Connected to Telegram as: {me.first_name} {me.last_name or ''} (@{me.username}) [ID: {me.id}]")
        return me

    async def crawl_recent_client_chats(self, limit_dialogs: int = 40, limit_messages: int = 100) -> Dict[str, Any]:
        """
        Directly download actual chat history with clients to calibrate persona,
        bypassing the need for manual JSON exports in Telegram Desktop.
        """
        print(f"[*] Crawling recent client dialogs (limit={limit_dialogs})...")
        me = await self.client.get_me()
        all_parsed_messages = []

        dialogs = await self.client.get_dialogs(limit=limit_dialogs)
        for dlg in dialogs:
            # Only personal direct chats (not channels or groups)
            if not dlg.is_user or dlg.entity.is_self or dlg.entity.bot:
                continue

            user_name = dlg.name
            user_id = dlg.id
            print(f"    Scanning chat with client: {user_name} ({user_id})...")

            async for msg in self.client.iter_messages(dlg.entity, limit=limit_messages):
                msg_entry = {
                    "id": msg.id,
                    "date": msg.date.isoformat() if msg.date else None,
                    "from_id": f"user{msg.sender_id}" if msg.sender_id else "",
                    "from": "Saber Ghaderi" if msg.sender_id == me.id else user_name,
                    "text": msg.message or "",
                    "type": "message"
                }
                if msg.file and hasattr(msg.file, "name"):
                    msg_entry["file_name"] = msg.file.name
                    msg_entry["media_type"] = "document"

                all_parsed_messages.append(msg_entry)

        # Feed extracted messages directly into telegram_chat_analyzer
        analysis = analyze_chat_history(all_parsed_messages, saber_id=me.id)
        
        out_json = os.path.join(self.storage_dir, "live_chat_analysis.json")
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)

        out_md = os.path.join(self.storage_dir, "live_chat_summary.md")
        with open(out_md, "w", encoding="utf-8") as f:
            f.write(format_markdown_analysis(analysis))

        print(f"[+] Successfully extracted {len(all_parsed_messages)} messages across client chats.")
        print(f"[+] Extracted {analysis['summary']['qa_threads_extracted']} Q&A pairs and {analysis['summary']['pricing_quotes_detected']} pricing discussions.")
        print(f"[+] Output written to: {out_md}")
        return analysis

    async def handle_proposal_message(self, event, raw_text: str, client_name: str, file_name: Optional[str] = None):
        """Process proposal received in private chat and post to Saved Messages."""
        analysis = analyze_proposal_text(raw_text)
        quote = calculate_quotation(analysis, self.persona)

        self.quote_counter += 1
        quote_id = f"Q{self.quote_counter}"

        self.pending_quotes[quote_id] = {
            "chat_id": event.chat_id,
            "sender_name": client_name,
            "quote": quote,
            "event": event,
            "created_at": datetime.now().isoformat()
        }

        # Format Telegram quotation card
        quote_card = format_telegram_card(quote)

        # Notify Saber via "Saved Messages" (me)
        alert_text = (
            f"🔔 *دریافت پروپوزال جدید از مراجع:* **{client_name}**\n"
            f"📁 *فایل/متن:* {file_name or 'متن پیام'}\n"
            f"🆔 *شناسه پیش‌فاکتور:* `{quote_id}`\n"
            "─────────────────────\n"
            f"{quote_card}\n\n"
            "⚙️ **دستورات تایید و اقدام:**\n"
            f"• ارسال مستقیم به مراجع: `/send_{quote_id}`\n"
            f"• تعدیل مبلغ و ارسال: `/adjust_{quote_id}_<مبلغ>`\n"
            f"• نادیده گرفتن: `/ignore_{quote_id}`"
        )

        # Send to Saber's Saved Messages
        await self.client.send_message("me", alert_text)
        print(f"[+] Posted draft quote {quote_id} for {client_name} to Saved Messages.")

        if self.auto_reply:
            ack_msg = (
                "سلام وقتتون بخیر، در خدمتم.\n"
                "فایل پروپوزال شما دریافت شد و در حال بررسی دقیق است. پیش‌فاکتور تفکیکی به زودی خدمتتون ارسال می‌شود."
            )
            await event.reply(ack_msg)

    async def start_listening(self):
        """Listen to real-time client DMs and Saved Messages admin commands."""
        me = await self.init_client()

        # 1. Admin Desk in "Saved Messages" (me)
        @self.client.on(events.NewMessage(chats="me"))
        async def admin_handler(event):
            txt = (event.message.message or "").strip()
            # Send quote command: /send_Q101
            m_send = re.match(r"^/send_(Q\d+)", txt)
            if m_send:
                qid = m_send.group(1)
                if qid in self.pending_quotes:
                    entry = self.pending_quotes[qid]
                    card = format_telegram_card(entry["quote"])
                    await self.client.send_message(entry["chat_id"], card)
                    await event.reply(f"✅ پیش‌فاکتور {qid} با موفقیت به {entry['sender_name']} ارسال شد.")
                    del self.pending_quotes[qid]
                else:
                    await event.reply(f"❌ شناسه {qid} یافت نشد.")

            # Adjust price command: /adjust_Q101_8500000
            m_adj = re.match(r"^/adjust_(Q\d+)_(\d+)", txt)
            if m_adj:
                qid = m_adj.group(1)
                new_price = int(m_adj.group(2))
                if qid in self.pending_quotes:
                    entry = self.pending_quotes[qid]
                    entry["quote"]["total_price_tomans"] = new_price
                    entry["quote"]["total_price_formatted"] = f"{new_price:,.0f} تومان"
                    card = format_telegram_card(entry["quote"])
                    await self.client.send_message(entry["chat_id"], card)
                    await event.reply(f"✅ پیش‌فاکتور {qid} با مبلغ {new_price:,.0f} تومان به {entry['sender_name']} ارسال شد.")
                    del self.pending_quotes[qid]
                else:
                    await event.reply(f"❌ شناسه {qid} یافت نشد.")

        # 2. Client Inbound Messages (Private Chats)
        @self.client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
        async def client_handler(event):
            sender = await event.get_sender()
            if not isinstance(sender, User) or sender.is_self or sender.bot:
                return

            client_name = f"{sender.first_name} {sender.last_name or ''}".strip()
            msg_text = event.message.message or ""
            print(f"[!] New DM from client {client_name} (ID: {sender.id}): {msg_text[:60]}")

            # Check for attached document (.docx / .pdf)
            if event.message.file and event.message.file.name:
                fname = event.message.file.name
                ext = os.path.splitext(fname)[1].lower()
                if ext in [".docx", ".pdf", ".txt"]:
                    print(f"[+] Downloading proposal file: {fname}...")
                    local_path = await event.download_media(file=os.path.join(self.storage_dir, f"{sender.id}_{fname}"))
                    try:
                        raw_content = extract_text_from_file(local_path)
                        await self.handle_proposal_message(event, raw_content, client_name, file_name=fname)
                    except Exception as err:
                        print(f"[-] Error extracting proposal: {err}")
                    return

            # Check if long text proposal
            if len(msg_text) > 80 and any(w in msg_text for w in ["عنوان", "فرضیه", "پروپوزال", "جامعه", "نمونه", "متغیر"]):
                await self.handle_proposal_message(event, msg_text, client_name)
                return

            # Check for questionnaire search query
            if any(w in msg_text for w in ["پرسشنامه", "مقیاس", "آزمون"]) and len(msg_text.split()) <= 10:
                q_clean = re.sub(r"(?:داری|دارید|رو\s*دارید|می‌خواستم|لطفاً|سلام|وقت\s*بخیر)", "", msg_text).strip()
                if questionnaire_resolver is not None:
                    profile = questionnaire_resolver.get_scale_profile(q_clean)
                    if profile and profile.get("found_in_registry"):
                        scale_info = (
                            f"سلام وقت بخیر.\n"
                            f"پرسشنامه «{profile.get('scale_persian_name') or profile.get('scale_name')}» "
                            f"با {profile.get('total_items_count', '')} گویه و مولفه‌های استاندارد در بانک ابزارها موجود است."
                        )
                        # Notify Saved Messages or reply
                        await self.client.send_message(
                            "me",
                            f"📋 *درخواست پرسشنامه از {client_name}:*\n"
                            f"پیام: {msg_text}\n"
                            f"پاسخ آماده: {scale_info}\n"
                            f"جهت ارسال به کاربر: به پیام ریپلای کنید یا بفرستید."
                        )

        print("[*] Telethon Userbot is active & listening to incoming client DMs...")
        print("[*] Open your Telegram 'Saved Messages' (پیام‌های ذخیره‌شده) to view real-time proposal alerts & approve quotes.")
        await self.client.run_until_disconnected()


def main():
    parser = argparse.ArgumentParser(description="Telethon MTProto Userbot for Saber Ghaderi")
    parser.add_argument("--config", "-c", type=str, default=DEFAULT_CONFIG_PATH, help="Path to telethon_config.json")
    parser.add_argument("--crawl-chats", action="store_true", help="Crawl real Telegram client chats to calibrate persona & FAQs")
    parser.add_argument("--listen", action="store_true", help="Run real-time listener for incoming client DMs")
    parser.add_argument("--auto-reply", action="store_true", help="Enable automatic replies to clients")

    args = parser.parse_args()

    config = load_telethon_config(args.config)
    if args.auto_reply:
        config["auto_reply"] = True

    if not config.get("api_id") or not config.get("api_hash"):
        print("[-] Telethon credentials (api_id & api_hash) are not set.")
        print("[-] How to get them in 1 minute:")
        print("    1. Go to https://my.telegram.org and log in with your phone number.")
        print("    2. Click on 'API development tools'.")
        print("    3. Create an app (any name, e.g., 'AcademicAssistant') and copy your api_id and api_hash.")
        print(f"    4. Save them into: {args.config}")
        # Save a template config if not existing
        if not os.path.exists(args.config):
            save_telethon_config(config, args.config)
            print(f"[+] Created template configuration file at: {args.config}")
        sys.exit(0)

    userbot = SaberTelethonUserbot(config)

    loop = asyncio.get_event_loop()
    if args.crawl_chats:
        loop.run_until_complete(userbot.init_client())
        loop.run_until_complete(userbot.crawl_recent_client_chats())
    else:
        # Default to listening
        loop.run_until_complete(userbot.start_listening())


if __name__ == "__main__":
    main()
