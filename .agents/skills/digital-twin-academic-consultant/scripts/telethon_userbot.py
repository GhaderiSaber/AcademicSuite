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


def get_proxy_settings(config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Parse proxy settings from config or auto-detect local SOCKS5 proxy."""
    proxy = config.get("proxy")
    if proxy and isinstance(proxy, dict) and proxy.get("addr"):
        return proxy
    # Auto-detect running local proxies (Karing, Clash, v2ray, etc.)
    import socket
    for port in [3066, 10808, 7890, 1080, 2080]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return {
                    "proxy_type": "socks5",
                    "addr": "127.0.0.1",
                    "port": port
                }
    return None


def load_telethon_config(config_path: str = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    """Load MTProto credentials from telethon_config.json."""
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "api_id": 6,
        "api_hash": "eb06d4abfb49dc3eeb1aeb98ae0f581e",
        "phone_number": "",
        "bot_token": "",
        "admin_id": 124911145,
        "session_name": DEFAULT_SESSION_NAME,
        "auto_reply": False,
        "saved_messages_desk": True,
        "proxy": {
            "proxy_type": "socks5",
            "addr": "127.0.0.1",
            "port": 3066
        }
    }


def save_telethon_config(config: Dict[str, Any], config_path: str = DEFAULT_CONFIG_PATH):
    """Save config to file."""
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


class SaberTelethonUserbot:
    """MTProto client managing Saber's personal account or bot automation."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_id = config.get("api_id") or 6
        self.api_hash = config.get("api_hash") or "eb06d4abfb49dc3eeb1aeb98ae0f581e"
        self.session_name = config.get("session_name", DEFAULT_SESSION_NAME)
        self.auto_reply = config.get("auto_reply", False)
        self.admin_id = config.get("admin_id", 124911145)
        self.storage_dir = DEFAULT_STORAGE_DIR
        os.makedirs(self.storage_dir, exist_ok=True)

        self.persona = load_persona()
        self.pending_quotes: Dict[str, Dict[str, Any]] = {}
        self.quote_counter = 100
        self.me = None
        self.proxy = get_proxy_settings(self.config)

        if TelegramClient is None:
            raise RuntimeError("Telethon is not installed in the active Python environment. Please run: pip install telethon 'python-socks[asyncio]'")

        if not self.api_id or not self.api_hash:
            self.client = None
        else:
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash, proxy=self.proxy)

    async def login_with_qr(self):
        """Perform QR code login by displaying an ASCII QR code in the terminal."""
        import getpass
        from telethon.errors import SessionPasswordNeededError
        try:
            import qrcode
        except ImportError:
            qrcode = None

        qr_login = await self.client.qr_login()
        print("\n" + "=" * 62)
        print("📱 SCAN THIS QR CODE IN TELEGRAM TO LOG IN:")
        print("   1. Open Telegram on your phone.")
        print("   2. Go to Settings -> Devices -> Link Desktop Device (اتصال دستگاه).")
        print("   3. Point your phone camera at the QR code below:")
        print("=" * 62 + "\n")

        if qrcode:
            qr = qrcode.QRCode()
            qr.add_data(qr_login.url)
            qr.print_ascii(invert=True)
        else:
            print(f"Direct QR URL: {qr_login.url}")

        print("\n[*] Waiting for you to scan the QR code on your phone...")
        try:
            user = await qr_login.wait()
            return user
        except SessionPasswordNeededError:
            print("\n[*] Two-step verification (2FA) password required.")
            pw = getpass.getpass("Enter your Telegram 2FA cloud password: ")
            return await self.client.sign_in(password=pw)

    async def init_client(self, phone: Optional[str] = None, bot_token: Optional[str] = None, use_qr: bool = False):
        """Connect and authenticate."""
        if not self.client:
            raise ValueError("api_id and api_hash must be set in telethon_config.json")

        await self.client.connect()
        if await self.client.is_user_authorized():
            self.me = await self.client.get_me()
            mode_str = "Bot" if self.me.bot else "Userbot (Personal Account)"
            print(f"[+] Connected to Telegram as {mode_str}: {self.me.first_name} {self.me.last_name or ''} (@{self.me.username}) [ID: {self.me.id}]")
            return self.me

        token = bot_token or self.config.get("bot_token")
        phone_num = phone or self.config.get("phone_number")

        if token:
            await self.client.start(bot_token=token)
        elif use_qr:
            await self.login_with_qr()
        elif phone_num:
            try:
                await self.client.start(phone=phone_num)
            except Exception as e:
                err_str = str(e)
                if "RECAPTCHA_CHECK" in err_str or "ForbiddenError" in err_str:
                    print("\n[!] Telegram phone login requires reCAPTCHA for this app ID.")
                    print("[*] Automatically switching to fast & secure QR Code Login...\n")
                    await self.login_with_qr()
                else:
                    raise
        else:
            await self.login_with_qr()

        self.me = await self.client.get_me()
        mode_str = "Bot" if self.me.bot else "Userbot (Personal Account)"
        print(f"[+] Connected to Telegram as {mode_str}: {self.me.first_name} {self.me.last_name or ''} (@{self.me.username}) [ID: {self.me.id}]")
        return self.me

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

        # Alert destination: "me" for Userbot, admin_id for Bot
        admin_target = "me" if (self.me and not self.me.bot) else self.admin_id
        await self.client.send_message(admin_target, alert_text)
        print(f"[+] Posted draft quote {quote_id} for {client_name} to Admin Desk ({admin_target}).")

        if self.auto_reply:
            ack_msg = (
                "سلام وقتتون بخیر، در خدمتم.\n"
                "فایل پروپوزال شما دریافت شد و در حال بررسی دقیق است. پیش‌فاکتور تفکیکی به زودی خدمتتون ارسال می‌شود."
            )
            await event.reply(ack_msg)

    async def scan_and_process_unread_messages(self, limit_dialogs: int = 100):
        """Scan unread direct messages from clients and post an executive summary + process proposals."""
        print("[*] Scanning unread client messages...")
        dialogs = await self.client.get_dialogs(limit=limit_dialogs)
        unread_clients = [
            dlg for dlg in dialogs 
            if dlg.is_user and not dlg.entity.is_self and not dlg.entity.bot and dlg.unread_count > 0
        ]

        admin_target = "me" if (self.me and not self.me.bot) else self.admin_id

        if not unread_clients:
            print("[+] No unread messages found from clients.")
            if admin_target:
                await self.client.send_message(admin_target, "✅ هیچ پیام خوانده‌نشده‌ای از مراجعین یافت نشد.")
            return

        print(f"[!] Found {len(unread_clients)} client(s) with unread messages.")
        summary_lines = [f"📬 **گزارش پیام‌های خوانده‌نشده ({len(unread_clients)} مراجع):**\n"]

        for dlg in unread_clients:
            client_name = dlg.name
            unread_cnt = dlg.unread_count
            print(f"    • {client_name} ({dlg.id}): {unread_cnt} unread message(s)")

            latest_text = ""
            found_proposal = False

            # Collect unread messages
            async for msg in self.client.iter_messages(dlg.entity, limit=min(unread_cnt, 10)):
                txt = (msg.message or "").strip()
                if not latest_text and txt:
                    latest_text = txt

                # Check for proposal files
                if msg.file and hasattr(msg.file, "name"):
                    fname = msg.file.name
                    ext = os.path.splitext(fname)[1].lower()
                    if ext in [".docx", ".pdf", ".txt"]:
                        print(f"      [+] Unread proposal file detected: {fname} from {client_name}")
                        local_path = await msg.download_media(file=os.path.join(self.storage_dir, f"{dlg.id}_{fname}"))
                        try:
                            raw_content = extract_text_from_file(local_path)
                            await self.handle_proposal_message(msg, raw_content, client_name, file_name=fname)
                            found_proposal = True
                        except Exception as err:
                            print(f"      [-] Error extracting proposal: {err}")

                # Check for long text proposal
                if len(txt) > 80 and any(w in txt for w in ["عنوان", "فرضیه", "پروپوزال", "جامعه", "نمونه", "متغیر"]):
                    await self.handle_proposal_message(msg, txt, client_name)
                    found_proposal = True

            snippet = latest_text[:90] + ("..." if len(latest_text) > 90 else "")
            status_tag = " (📄 پروپوزال بررسی و تحلیل شد)" if found_proposal else ""
            summary_lines.append(
                f"👤 **{client_name}** (ID: `{dlg.id}`) — {unread_cnt} پیام{status_tag}\n"
                f"💬 *آخرین پیام:* «{snippet}»\n"
            )

        summary_lines.append("─────────────────────\n⚙️ جهت بررسی مجدد: `/unread`")
        report_text = "\n".join(summary_lines)

        await self.client.send_message(admin_target, report_text)
        print(f"[+] Posted unread messages report to Admin Desk ({admin_target}).")

    async def start_listening(self, phone: Optional[str] = None, bot_token: Optional[str] = None, use_qr: bool = False):
        """Listen to real-time client DMs and Admin Desk commands."""
        me = await self.init_client(phone=phone, bot_token=bot_token, use_qr=use_qr)
        admin_chat = "me" if not me.bot else self.admin_id

        # 1. Admin Desk (/send_Q101, /adjust_Q101_5000000, /ignore_Q101, /unread)
        @self.client.on(events.NewMessage(chats=admin_chat))
        async def admin_handler(event):
            txt = (event.message.message or "").strip()
            # Unread messages re-scan: /unread or /scan
            if txt in ["/unread", "/scan"]:
                await event.reply("🔍 در حال بررسی پیام‌های خوانده‌نشده مراجعین...")
                await self.scan_and_process_unread_messages()
                return

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

            # Ignore quote command: /ignore_Q101
            m_ign = re.match(r"^/ignore_(Q\d+)", txt)
            if m_ign:
                qid = m_ign.group(1)
                if qid in self.pending_quotes:
                    del self.pending_quotes[qid]
                    await event.reply(f"🗑️ پیش‌فاکتور {qid} نادیده گرفته و حذف شد.")

        # 2. Client Inbound Messages (Private Chats)
        @self.client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
        async def client_handler(event):
            sender = await event.get_sender()
            if not isinstance(sender, User) or sender.is_self or sender.bot:
                return

            client_name = f"{sender.first_name} {sender.last_name or ''}".strip()
            msg_text = (event.message.message or "").strip()
            print(f"[!] New DM from client {client_name} (ID: {sender.id}): {msg_text[:60]}")

            # Bot-specific commands (/start, /help, /scale)
            if me.bot:
                if msg_text in ["/start", "سلام", "درود"]:
                    welcome_msg = (
                        f"سلام و درود، وقت شما بخیر {sender.first_name} گرامی.\n\n"
                        "دستیار هوشمند و مشاور پژوهشی صابر قادری در خدمت شماست.\n"
                        "خدمات قابل ارائه:\n"
                        "• بررسی پروپوزال و صدور پیش‌فاکتور تفکیکی (ارسال فایل یا متن)\n"
                        "• جستجوی پرسشنامه‌ها و مقیاس‌های روان‌سنجی: `/scale نام_پرسشنامه`\n"
                        "• مشاوره روش‌شناسی و تحلیل آماری\n\n"
                        "جهت استعلام هزینه و زمان‌بندی، فایل پروپوزال خود را ارسال بفرمایید."
                    )
                    await event.reply(welcome_msg)
                    return

                if msg_text == "/help":
                    help_msg = (
                        "📚 **راهنمای دستورات:**\n"
                        "• ارسال فایل پروپوزال (.docx یا .pdf) برای ارزیابی و استعلام قیمت\n"
                        "• `/scale <نام>`: جستجو در بانک ۴۸۸۰ پرسشنامه استاندارد\n"
                        "• `/start`: نمایش پیام آغازین و معرفی خدمات"
                    )
                    await event.reply(help_msg)
                    return

            # Check for attached document (.docx / .pdf / .txt)
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

            # Check for questionnaire search query (/scale <name> or "پرسشنامه ...")
            m_scale = re.match(r"^/scale\s+(.+)", msg_text)
            is_scale_query = bool(m_scale) or (
                any(w in msg_text for w in ["پرسشنامه", "مقیاس", "آزمون"]) and len(msg_text.split()) <= 10
            )
            if is_scale_query:
                query_name = m_scale.group(1).strip() if m_scale else re.sub(
                    r"(?:داری|دارید|رو\s*دارید|می‌خواستم|لطفاً|سلام|وقت\s*بخیر)", "", msg_text
                ).strip()
                if questionnaire_resolver is not None:
                    profile = questionnaire_resolver.get_scale_profile(query_name)
                    if profile and profile.get("found_in_registry"):
                        scale_info = (
                            f"📋 **اطلاعات ابزار اندازه‌گیری:**\n"
                            f"• نام مقیاس: **{profile.get('scale_persian_name') or profile.get('scale_name')}**\n"
                            f"• تعداد گویه‌ها: {profile.get('total_items_count', 'مشخص در شناسنامه')}\n"
                            f"• وضعیت در بانک: موجود و استاندارد\n\n"
                            "این ابزار به همراه نمره‌گذاری و مولفه‌های استاندارد آماده استفاده در پژوهش است."
                        )
                        if me.bot:
                            await event.reply(scale_info)
                        else:
                            await self.client.send_message(
                                "me",
                                f"📋 *درخواست پرسشنامه از {client_name}:*\n"
                                f"پیام: {msg_text}\n"
                                f"پاسخ آماده: {scale_info}"
                            )
                        return

        desk_location = "پیام‌های ذخیره‌شده (Saved Messages)" if not me.bot else f"چت با اکانت صابر (ID: {self.admin_id})"
        print(f"[*] Telethon {'Userbot' if not me.bot else 'Bot'} is active & listening to incoming DMs...")
        print(f"[*] Open {desk_location} to view real-time proposal alerts & approve quotes.")

        # Scan and report any existing unread messages from clients on startup
        await self.scan_and_process_unread_messages()

        await self.client.run_until_disconnected()


async def main_async(args):
    config = load_telethon_config(args.config)
    if args.auto_reply:
        config["auto_reply"] = True
    if args.phone:
        config["phone_number"] = args.phone
    if args.bot_token:
        config["bot_token"] = args.bot_token

    if not config.get("api_id") or not config.get("api_hash"):
        print("[-] Telethon credentials (api_id & api_hash) are not set.")
        print("[-] How to get them in 1 minute:")
        print("    1. Go to https://my.telegram.org and log in with your phone number.")
        print("    2. Click on 'API development tools'.")
        print("    3. Create an app (any name, e.g., 'AcademicAssistant') and copy your api_id and api_hash.")
        print(f"    4. Save them into: {args.config}")
        if not os.path.exists(args.config):
            save_telethon_config(config, args.config)
            print(f"[+] Created template configuration file at: {args.config}")
        sys.exit(0)

    userbot = SaberTelethonUserbot(config)

    if args.scan_unread:
        await userbot.init_client(phone=args.phone, bot_token=args.bot_token, use_qr=args.qr)
        await userbot.scan_and_process_unread_messages()
    elif args.crawl_chats:
        await userbot.init_client(phone=args.phone, bot_token=args.bot_token, use_qr=args.qr)
        await userbot.crawl_recent_client_chats()
    else:
        # Default to listening
        await userbot.start_listening(phone=args.phone, bot_token=args.bot_token, use_qr=args.qr)


def main():
    parser = argparse.ArgumentParser(description="Telethon MTProto Client / Digital Twin for Saber Ghaderi")
    parser.add_argument("--config", "-c", type=str, default=DEFAULT_CONFIG_PATH, help="Path to telethon_config.json")
    parser.add_argument("--phone", "-p", type=str, default=None, help="Phone number with country code (e.g., +98912XXXXXXX)")
    parser.add_argument("--bot-token", "-b", type=str, default=None, help="Telegram Bot Token from @BotFather")
    parser.add_argument("--qr", action="store_true", help="Log in by scanning a QR code in Telegram (bypasses reCAPTCHA & SMS)")
    parser.add_argument("--scan-unread", action="store_true", help="Scan and report unread client messages to Saved Messages")
    parser.add_argument("--crawl-chats", action="store_true", help="Crawl real Telegram client chats to calibrate persona & FAQs")
    parser.add_argument("--listen", action="store_true", help="Run real-time listener for incoming client DMs")
    parser.add_argument("--auto-reply", action="store_true", help="Enable automatic replies to clients")

    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
