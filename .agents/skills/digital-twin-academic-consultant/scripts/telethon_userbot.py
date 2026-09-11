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
import html
import asyncio
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    from telethon import TelegramClient, events, Button
    from telethon.tl.types import DocumentAttributeFilename, User
except ImportError:
    TelegramClient = None
    events = None
    Button = None

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

from project_drive_manager import (
    ProjectDriveManager,
    sanitize_filename,
    resolve_google_drive_work_dir,
    SUBFOLDERS,
    clean_drive_display_path,
    format_client_mention_html,
    resolve_media_details
)


DEFAULT_CONFIG_PATH = os.path.join(SCRIPT_DIR, "telethon_config.json")
DEFAULT_SESSION_NAME = os.path.join(SCRIPT_DIR, "saber_userbot")
DEFAULT_STORAGE_DIR = os.path.join(SCRIPT_DIR, "userbot_storage")


def is_valid_telegram_button_url(url: Optional[str]) -> bool:
    """Check if URL is valid for Telegram Button.url (must be external http/https or tg://, not localhost)."""
    if not url or not isinstance(url, str):
        return False
    u = url.strip().lower()
    if "localhost" in u or "127.0.0.1" in u:
        return False
    return u.startswith("https://") or u.startswith("http://") or u.startswith("tg://")


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


def generate_deliverable_caption(client_name: str, filename: str) -> str:
    """Generate scholarly, authentic Persian delivery caption with half-spaces."""
    # Clean client name (remove parenthetical ID, username, or English tags)
    display_name = client_name.split("(")[0].strip()
    if display_name.startswith("@"):
        display_name = display_name.lstrip("@")
    if not display_name:
        display_name = "مراجع"
    base_name, _ = os.path.splitext(filename)
    clean_base = base_name.replace("_", " ").strip()
    return (
        f"سلام و احترام، وقت شما بخیر {display_name} گرامی.\n\n"
        f"فایل نهایی «{clean_base}» خدمتتون تقدیم می‌شود. لطفاً بررسی بفرمایید؛ "
        "در صورت وجود هرگونه نظر، اصلاح یا بازخورد از سوی اساتید محترم، با کمال میل در خدمتتون هستم."
    )


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
        self.project_manager = ProjectDriveManager(self.config)
        self.admin_desk_chat_id = config.get("admin_desk_chat_id")

        self.persona = load_persona()
        self.pending_quotes: Dict[str, Dict[str, Any]] = {}
        self.quote_counter = 100
        self.pending_drafts: Dict[str, Dict[str, Any]] = {}
        self.draft_counter = 100
        self.pending_followups: Dict[str, Dict[str, Any]] = {}
        self.followup_counter = 100
        self.pending_deliverables: Dict[str, Dict[str, Any]] = {}
        self.deliverable_counter = 100
        self.me = None
        self.proxy = get_proxy_settings(self.config)

        if not self.api_id or not self.api_hash or TelegramClient is None:
            self.client = None
        else:
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash, proxy=self.proxy)

        # Second personal userbot account (optional)
        self.second_account_config = config.get("second_account")
        if self.second_account_config and self.api_id and self.api_hash and TelegramClient is not None:
            s2_name = self.second_account_config.get("session_name", "saber_second_userbot")
            s2_path = s2_name if os.path.isabs(s2_name) else os.path.join(SCRIPT_DIR, s2_name)
            self.client2 = TelegramClient(s2_path, self.api_id, self.api_hash, proxy=self.proxy)
        else:
            self.client2 = None
        self.me2 = None

        self.bot_token = config.get("bot_token")
        if TelegramClient is not None and self.bot_token and self.api_id and self.api_hash:
            bot_session_path = os.path.join(self.storage_dir, "bot_session")
            self.bot_client = TelegramClient(bot_session_path, self.api_id, self.api_hash, proxy=self.proxy)
        else:
            self.bot_client = None

    @property
    def admin_target(self):
        """Return the destination peer for admin desk notifications."""
        if self.admin_desk_chat_id:
            return self.admin_desk_chat_id
        return "me" if (self.me and not self.me.bot) else self.admin_id

    async def send_to_desk(self, text: str, buttons=None, reply_to=None, parse_mode: str = "html"):
        """
        Send an alert/message to the Admin Desk in English with HTML formatting.
        If bot_client is available and admin_desk_chat_id is set, the message is sent
        by Academic Assistant Bot rather than Saber's personal account!
        """
        if self.bot_client and self.admin_desk_chat_id:
            try:
                if not self.bot_client.is_connected():
                    await self.bot_client.connect()
                return await self.bot_client.send_message(
                    self.admin_desk_chat_id,
                    text,
                    buttons=buttons,
                    reply_to=reply_to,
                    parse_mode=parse_mode
                )
            except Exception as e:
                print(f"[-] Bot send to desk error: {e}, falling back to user client...")
        return await self.client.send_message(
            self.admin_target,
            text,
            buttons=buttons,
            reply_to=reply_to,
            parse_mode=parse_mode
        )

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
        if not await self.client.is_user_authorized():
            phone_num = phone or self.config.get("phone_number")
            if use_qr or not phone_num:
                await self.login_with_qr()
            else:
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

        self.me = await self.client.get_me()
        mode_str = "Bot" if self.me.bot else "Userbot (Personal Account)"
        print(f"[+] Connected to Telegram as {mode_str}: {self.me.first_name} {self.me.last_name or ''} (@{self.me.username}) [ID: {self.me.id}]")

        # Initialize Second Account client if configured
        if self.client2:
            try:
                await self.client2.connect()
                if await self.client2.is_user_authorized():
                    self.me2 = await self.client2.get_me()
                    print(f"[+] Connected to Second Account: {self.me2.first_name} {self.me2.last_name or ''} (@{self.me2.username}) [ID: {self.me2.id}]")
                else:
                    print("[-] Second account is not authorized. Please run scripts/login_second_account.sh")
            except Exception as e:
                print(f"[-] Could not connect Second Account: {e}")

        # Initialize Assistant Bot client if configured
        b_token = bot_token or self.bot_token
        if self.bot_client and b_token:
            try:
                if not self.bot_client.is_connected():
                    await self.bot_client.connect()
                if not await self.bot_client.is_user_authorized():
                    await self.bot_client.start(bot_token=b_token)
                me_bot = await self.bot_client.get_me()
                print(f"[+] Connected to Assistant Bot: {me_bot.first_name} (@{me_bot.username}) [ID: {me_bot.id}]")
            except Exception as e:
                print(f"[-] Could not connect Assistant Bot: {e}")

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

    async def handle_proposal_message(
        self,
        event,
        raw_text: str,
        client_name: str,
        file_name: Optional[str] = None,
        sender_id: Optional[int] = None,
        username: Optional[str] = None,
        client_source=None
    ):
        """Process proposal received in private chat, provision Google Drive project folder, and post to Saved Messages."""
        # 1. Provision standard 4-tier project folder in Google Drive
        project_paths = self.project_manager.provision_project(
            client_name=client_name,
            client_id=sender_id,
            username=username,
            status="proposal_received"
        )
        project_dir = project_paths["root"]

        # 2. Analyze proposal text & calculate quotation
        analysis = analyze_proposal_text(raw_text)
        quote = calculate_quotation(analysis, self.persona)

        self.quote_counter += 1
        quote_id = f"Q{self.quote_counter}"

        self.pending_quotes[quote_id] = {
            "chat_id": event.chat_id,
            "sender_name": client_name,
            "quote": quote,
            "event": event,
            "project_dir": project_dir,
            "client_source": client_source or self.client,
            "created_at": datetime.now().isoformat()
        }

        # 3. Format Telegram quotation cards (English for desk, Persian for client draft)
        quote_card_fa = format_telegram_card(quote, lang="fa")
        quote_card_en = format_telegram_card(quote, lang="en")

        # 4. Save quotation and draft response inside project deliverables (Persian for client)
        draft_deliverable = os.path.join(project_paths["deliverables"], "telegram_response_draft.md")
        with open(draft_deliverable, "w", encoding="utf-8") as f:
            f.write(f"# پیش‌نویس پیش‌فاکتور و پاسخ به مراجع ({client_name})\n\n{quote_card_fa}\n")

        # 5. Notify Saber via Academic Desk in English with clean path & clickable user link
        client_link = format_client_mention_html(client_name, username=username, client_id=sender_id)
        clean_path = clean_drive_display_path(project_dir)
        safe_fname = html.escape(file_name or "Direct chat message")

        alert_text = (
            f"🔔 <b>New Proposal Received from Client:</b> {client_link}\n"
            f"📄 <b>File / Source:</b> <code>{safe_fname}</code>\n"
            f"📁 <b>Google Drive:</b> <code>{html.escape(clean_path)}</code>\n"
            f"🆔 <b>Quotation ID:</b> <code>{quote_id}</code>\n"
            "─────────────────────\n"
            f"{quote_card_en}\n\n"
            "⚙️ <b>Admin Actions & Commands:</b>\n"
            f"• Approve & Send to Client: <code>/send_{quote_id}</code>\n"
            f"• Adjust Price & Send: <code>/adjust_{quote_id}_&lt;amount&gt;</code>\n"
            f"• Dismiss: <code>/ignore_{quote_id}</code>"
        )

        buttons = None
        if Button is not None:
            buttons = [
                [Button.inline(f"🚀 Approve & Send ({quote_id})", f"send_{quote_id}".encode()),
                 Button.inline("🗑️ Dismiss", f"ignore_{quote_id}".encode())]
            ]

        await self.send_to_desk(alert_text, buttons=buttons, parse_mode="html")
        print(f"[+] Posted draft quote {quote_id} for {client_name} to Admin Desk via Assistant Bot.")
        print(f"[+] Project folder synced: {project_dir}")

        if self.auto_reply:
            ack_msg = (
                "سلام وقتتون بخیر، در خدمتم.\n"
                "فایل پروپوزال شما دریافت شد و در حال بررسی دقیق است. پیش‌فاکتور تفکیکی به زودی خدمتتون ارسال می‌شود."
            )
            await event.reply(ack_msg)

    async def create_and_post_draft(
        self,
        chat_id: int,
        sender_name: str,
        sender_id: int,
        username: Optional[str],
        inquiry_type: str,
        client_message: str,
        draft_reply: str,
        client_source: Any = None,
        account_label: str = "Main Account (@GhaderiSaber)"
    ) -> str:
        """
        Create a Co-Pilot draft recommendation and post it to Academic Desk with 1-click dispatch buttons.
        Zero autonomous messages are sent to the client.
        """
        self.draft_counter += 1
        draft_id = f"D{self.draft_counter}"

        self.pending_drafts[draft_id] = {
            "draft_id": draft_id,
            "chat_id": chat_id,
            "sender_id": sender_id,
            "sender_name": sender_name,
            "username": username,
            "inquiry_type": inquiry_type,
            "client_message": client_message,
            "draft_reply": draft_reply,
            "client_source": client_source or self.client,
            "account_label": account_label,
            "created_at": datetime.now().isoformat()
        }

        client_link = format_client_mention_html(sender_name, username=username, client_id=sender_id)
        snippet = html.escape(client_message[:140] + ("..." if len(client_message) > 140 else ""))
        safe_draft = html.escape(draft_reply)

        alert_text = (
            f"💡 <b>[Co-Pilot Draft] Client Inquiry from {client_link}</b>\n"
            f"📱 <b>Account:</b> {html.escape(account_label)}\n"
            f"🏷️ <b>Category:</b> <code>{inquiry_type}</code>\n"
            f"💬 <b>Client Message:</b> «{snippet}»\n"
            f"🆔 <b>Draft ID:</b> <code>{draft_id}</code>\n"
            "─────────────────────\n"
            f"📝 <b>Suggested Persian Draft:</b>\n"
            f"<blockquote>{safe_draft}</blockquote>\n\n"
            "⚙️ <b>Admin Actions & Commands:</b>\n"
            f"• Approve & Send to Client: <code>/send_msg_{draft_id}</code>\n"
            f"• Send Custom Edits: <code>/send_msg_{draft_id} &lt;custom text&gt;</code>\n"
            f"• Dismiss Draft: <code>/ignore_{draft_id}</code>"
        )

        buttons = None
        if Button is not None:
            buttons = [
                [Button.inline(f"🚀 Send Response ({draft_id})", f"send_draft_{draft_id}".encode()),
                 Button.inline("🗑️ Dismiss", f"ignore_draft_{draft_id}".encode())]
            ]

        await self.send_to_desk(alert_text, buttons=buttons, parse_mode="html")
        print(f"[+] Posted Co-Pilot draft {draft_id} ({inquiry_type}) for {sender_name} to Academic Desk.")
        return draft_id

    async def scan_and_report_project_health(self, trigger_event: Optional[Any] = None) -> Dict[str, Any]:
        """
        Scan all managed client projects in Google Drive, assess project health,
        identify clients requiring follow-ups, and post actionable cards to Academic Desk.
        """
        print("[*] Auditing client projects health across Google Drive...")
        audit_res = self.project_manager.audit_all_projects_health()
        total = audit_res["total_projects"]
        healthy = audit_res["healthy_count"]
        attention = audit_res["attention_count"]
        stalled = audit_res["stalled_count"]
        completed = audit_res["completed_count"]
        follow_ups = audit_res["follow_ups"]

        # 1. Post Overview Summary Card to Academic Desk
        summary_lines = [
            "📊 <b>Client Projects Health & Follow-Up Audit</b>\n",
            f"• <b>Total Managed Projects:</b> {total}",
            f"• 🟢 <b>Healthy / Active:</b> {healthy}",
            f"• 🟡 <b>Attention Needed:</b> {attention}",
            f"• 🔴 <b>Stalled / Dormant:</b> {stalled}",
            f"• ⚪ <b>Completed:</b> {completed}\n",
            f"🔔 <b>Actionable Follow-Up Reminders:</b> {len(follow_ups)} clients requiring attention"
        ]

        if stalled > 0 or attention > 0:
            summary_lines.append("\n⚠️ <b>Top Projects Requiring Attention:</b>")
            for item in (follow_ups[:4]):
                cname = item["client_name"]
                days = item["days_silent"]
                badge = item["health_badge"]
                summary_lines.append(f"• {badge} <b>{html.escape(cname)}</b>: {days} days silent (<i>{html.escape(item['reason'])}</i>)")

        summary_lines.append(
            "\n─────────────────────\n"
            "⚙️ <b>Commands:</b>\n"
            "• Refresh Health: <code>/health</code>\n"
            "• Project Catalog: <code>/projects</code>\n"
            "• Deliverables: <code>/deliverables</code>"
        )
        summary_text = "\n".join(summary_lines)

        buttons = None
        if Button is not None:
            buttons = [
                [Button.inline("🔄 Refresh Health", b"cmd_health"),
                 Button.inline("📂 Project Catalog", b"cmd_projects"),
                 Button.inline("📦 Deliverables", b"cmd_deliverables")],
                [Button.inline("❌ Dismiss Notice", b"cmd_close")]
            ]

        await self.send_to_desk(summary_text, buttons=buttons, parse_mode="html")

        # 2. Post individual 1-Click actionable Follow-Up cards for the top candidates
        for item in follow_ups[:5]:
            self.followup_counter += 1
            fu_id = f"F{self.followup_counter}"

            cname = item["client_name"]
            uname = item.get("telegram_username")
            cid = item.get("telegram_id")
            pdir = item.get("folder_path", "")
            badge = item.get("health_badge", "🟡")
            days = item.get("days_silent", 0)
            reason = item.get("reason", "")
            fu_type = item.get("follow_up_type", "followup")
            draft_text = item.get("suggested_persian_followup", "")

            self.pending_followups[fu_id] = {
                "fu_id": fu_id,
                "client_name": cname,
                "telegram_id": cid,
                "username": uname,
                "folder_path": pdir,
                "followup_type": fu_type,
                "draft_reply": draft_text,
                "created_at": datetime.now().isoformat()
            }

            client_link = format_client_mention_html(cname, username=uname, client_id=cid)
            clean_p = clean_drive_display_path(pdir)
            safe_draft = html.escape(draft_text)

            card_text = (
                f"{badge} <b>[Follow-Up Reminder ({fu_id})] {client_link}</b>\n"
                f"📁 <b>Project:</b> <code>{html.escape(clean_p)}</code>\n"
                f"⏰ <b>Silence Duration:</b> <code>{days} days</code>\n"
                f"💡 <b>Diagnosis:</b> <i>{html.escape(reason)}</i>\n"
                "─────────────────────\n"
                f"📝 <b>Suggested Persian Follow-Up:</b>\n"
                f"<blockquote>{safe_draft}</blockquote>\n\n"
                "⚙️ <b>Actions & Commands:</b>\n"
                f"• Approve & Send to Client: <code>/send_fu_{fu_id}</code>\n"
                f"• Send Custom Edits: <code>/send_fu_{fu_id} &lt;custom text&gt;</code>\n"
                f"• Dismiss Reminder: <code>/ignore_fu_{fu_id}</code>"
            )

            card_btns = None
            if Button is not None:
                card_btns = [
                    [Button.inline(f"🚀 Send Follow-Up ({fu_id})", f"send_fu_{fu_id}".encode()),
                     Button.inline("🗑️ Dismiss", f"ignore_fu_{fu_id}".encode())]
                ]

            await self.send_to_desk(card_text, buttons=card_btns, parse_mode="html")
            print(f"[+] Posted Follow-Up reminder {fu_id} for {cname} to Academic Desk.")

        return audit_res

    async def scan_and_process_unread_messages(self, limit_dialogs: int = 100, trigger_event: Optional[Any] = None):
        """
        Scan unread direct messages from clients:
        1. Automatically provisions or updates project folders in Google Drive 'My Work'.
        2. Downloads incoming documents/scales into 01_raw_inputs/.
        3. Persists chat_history.json, chat_transcript.md, and client_profile.md.
        4. Detects proposals and prepares quotations.
        5. Posts an executive summary to Saved Messages with Google Drive links.
        """
        print("[*] Scanning unread client messages and synchronizing Google Drive project folders across accounts...")
        active_scan_clients = [("Main Account (@GhaderiSaber)", self.client)]
        if self.client2 and self.client2.is_connected():
            active_scan_clients.append(("Second Account (@SaberGhaderi)", self.client2))

        unread_clients = []
        for acc_lbl, cl in active_scan_clients:
            dialogs = await cl.get_dialogs(limit=limit_dialogs)
            for dlg in dialogs:
                if (dlg.is_user and not dlg.entity.is_self and not dlg.entity.bot and 
                    dlg.id not in [124911145, 6328062294, 777000] and dlg.unread_count > 0):
                    unread_clients.append((acc_lbl, cl, dlg))

        if not unread_clients:
            print("[+] No unread messages found from clients.")
            if trigger_event:
                now_str = datetime.now().strftime("%H:%M:%S")
                await trigger_event.answer(f"✅ All client dialogs are up to date! (Checked at {now_str})", alert=True)
            else:
                await self.send_to_desk("✅ No unread client messages found.", parse_mode="html")
            return

        print(f"[!] Found {len(unread_clients)} client(s) with unread messages.")
        summary_lines = [f"📬 <b>Unread Client Messages & Project Sync ({len(unread_clients)} clients):</b>\n"]

        for acc_lbl, cl, dlg in unread_clients:
            client_name = dlg.name
            unread_cnt = dlg.unread_count
            user_entity = dlg.entity
            username = getattr(user_entity, "username", None)
            print(f"    • [{acc_lbl}] {client_name} ({dlg.id}): {unread_cnt} unread message(s)")

            # Automatically archive chat and download unread files into Google Drive project folder
            try:
                archive_res = await self.project_manager.save_client_chat_and_files(
                    client=cl,
                    entity=dlg.entity,
                    client_name=client_name,
                    client_id=dlg.id,
                    username=username,
                    limit_messages=max(unread_cnt + 20, 50),
                    download_files=True
                )
                project_dir = archive_res["project_dir"]
            except Exception as e:
                print(f"    [-] Failed to archive project for {client_name}: {e}")
                project_paths = self.project_manager.provision_project(client_name, client_id=dlg.id, username=username)
                project_dir = project_paths["root"]

            latest_text = ""
            found_proposal = False

            # Check unread messages for proposal files or text
            async for msg in cl.iter_messages(dlg.entity, limit=min(unread_cnt, 15)):
                txt = (msg.message or "").strip()
                if not latest_text:
                    if txt:
                        latest_text = txt
                    else:
                        m_fn, m_type, _, m_dur = resolve_media_details(msg)
                        if m_type == "voice":
                            dur_lbl = f" - {m_dur}s" if m_dur else ""
                            latest_text = f"🎤 [پیام صوتی / Voice Note{dur_lbl}]"
                        elif m_type == "photo":
                            latest_text = "📷 [تصویر / Photo]"
                        elif m_type == "video_note":
                            dur_lbl = f" - {m_dur}s" if m_dur else ""
                            latest_text = f"📹 [پیام ویدیویی / Video Note{dur_lbl}]"
                        elif m_fn:
                            latest_text = f"📎 [{m_fn}]"

                # Check for proposal files
                fn_detail, mt_detail, _, _ = resolve_media_details(msg)
                if fn_detail and mt_detail == "document":
                    fname = fn_detail
                    ext = os.path.splitext(fname)[1].lower()
                    if ext in [".docx", ".pdf", ".txt"]:
                        print(f"      [+] Unread proposal file detected: {fname} from {client_name}")
                        local_path = os.path.join(project_dir, "01_raw_inputs", fname)
                        if not os.path.exists(local_path):
                            try:
                                local_path = await msg.download_media(file=local_path)
                            except Exception:
                                local_path = await msg.download_media(file=os.path.join(self.storage_dir, f"{dlg.id}_{fname}"))
                        try:
                            raw_content = extract_text_from_file(local_path)
                            await self.handle_proposal_message(
                                msg, raw_content, client_name, file_name=fname, sender_id=dlg.id, username=username, client_source=cl
                            )
                            found_proposal = True
                        except Exception as err:
                            print(f"      [-] Error extracting proposal: {err}")

                # Check for long text proposal
                if len(txt) > 80 and any(w in txt for w in ["عنوان", "فرضیه", "پروپوزال", "جامعه", "نمونه", "متغیر"]):
                    await self.handle_proposal_message(
                        msg, txt, client_name, sender_id=dlg.id, username=username, client_source=cl
                    )
                    found_proposal = True

            clean_pdir = clean_drive_display_path(project_dir)
            client_link = format_client_mention_html(client_name, username=username, client_id=dlg.id)
            snippet = html.escape(latest_text[:90] + ("..." if len(latest_text) > 90 else ""))
            status_tag = " <i>(📄 Proposal Analyzed)</i>" if found_proposal else ""
            summary_lines.append(
                f"📱 <b>{html.escape(acc_lbl)}</b>\n"
                f"👤 {client_link}\n"
                f"📁 <b>Google Drive:</b> <code>{html.escape(clean_pdir)}</code>\n"
                f"💬 <b>Latest Message ({unread_cnt} new):</b> «{snippet}»{status_tag}\n"
            )

        webapp_url = self.config.get("webapp_url", "")
        has_web_btn = is_valid_telegram_button_url(webapp_url)
        dash_display = webapp_url if has_web_btn else "http://localhost:8080"

        summary_lines.append(
            "─────────────────────\n"
            "⚙️ <b>Commands:</b>\n"
            "• Rescan: <code>/unread</code>\n"
            "• Project Catalog: <code>/projects</code>\n"
            "• Deliverables: <code>/deliverables</code>\n"
            f"• Web Dashboard: <code>{dash_display}</code>"
        )
        report_text = "\n".join(summary_lines)

        buttons = None
        if Button is not None:
            dash_row = [Button.inline("🔄 Rescan Messages", b"cmd_unread"),
                        Button.inline("📂 Project Catalog", b"cmd_projects"),
                        Button.inline("📦 Deliverables", b"cmd_deliverables")]
            row2 = []
            if has_web_btn:
                row2.append(Button.url("📱 Open Web Dashboard", webapp_url))
            row2.append(Button.inline("❌ Dismiss Notice", b"cmd_close"))
            buttons = [dash_row, row2]

        await self.send_to_desk(report_text, buttons=buttons, parse_mode="html")
        print(f"[+] Posted unread messages and project sync report to Admin Desk via Assistant Bot.")


    async def start_listening(self, phone: Optional[str] = None, bot_token: Optional[str] = None, use_qr: bool = False):
        """Listen to real-time client DMs and Admin Desk commands."""
        me = await self.init_client(phone=phone, bot_token=bot_token, use_qr=use_qr)
        admin_chats = []
        if self.admin_desk_chat_id:
            admin_chats.append(self.admin_desk_chat_id)
        admin_chats.append("me" if not me.bot else self.admin_id)

        # 1. Admin Desk (/send_Q101, /adjust_Q101_5000000, /ignore_Q101, /unread, /projects, /save_project, /sync_projects)
        @self.client.on(events.NewMessage(chats=admin_chats))
        async def admin_handler(event):
            txt = (event.message.message or "").strip()

            # Unread messages re-scan: /unread or /scan
            if txt in ["/unread", "/scan"]:
                await event.reply("🔍 Scanning unread client messages and synchronizing Google Drive projects...", parse_mode="html")
                await self.scan_and_process_unread_messages()
                return

            # WebApp / Mini App Dashboard: /webapp or /dashboard
            if txt in ["/webapp", "/dashboard", "/app"]:
                projs = self.project_manager.list_all_projects()
                webapp_url = self.config.get("webapp_url", "")
                has_web_btn = is_valid_telegram_button_url(webapp_url)
                dash_url_display = webapp_url if has_web_btn else "http://localhost:8080"
                dash_text = (
                    f"📱 <b>Saber Academic Suite — Mini App & Dashboard</b>\n\n"
                    f"• <b>Live Projects:</b> {len(projs)} active client projects\n"
                    f"• <b>Web Dashboard URL:</b> <code>{dash_url_display}</code>\n"
                    f"• <b>Features:</b> Visual Kanban pipeline, live pricing calculator, psychometric scales explorer"
                )
                btn = None
                if Button is not None:
                    if has_web_btn:
                        btn = [[Button.url("📱 Open Mini App Dashboard", webapp_url)]]
                    else:
                        btn = [[Button.inline("📂 Project Catalog", b"cmd_projects"),
                                Button.inline("🔄 Rescan Messages", b"cmd_unread")]]
                await event.reply(dash_text, buttons=btn, parse_mode="html")
                return

            # List Google Drive projects: /projects or /list_projects [query]
            m_proj = re.match(r"^/(?:projects|list_projects)(?:\s+(.+))?", txt)
            if m_proj:
                filter_term = (m_proj.group(1) or "").strip().lower()
                projs = self.project_manager.list_all_projects()
                if filter_term:
                    projs = [p for p in projs if filter_term in (p.get("client_name") or "").lower() 
                             or filter_term in (p.get("client_name_fa") or "").lower()
                             or filter_term in (p.get("folder_name") or "").lower()]
                if not projs:
                    await event.reply("📂 No matching project folders found in Google Drive.", parse_mode="html")
                    return
                header = f"📂 <b>Client Projects in Google Drive ({len(projs)} found):</b>\n" if filter_term else f"📂 <b>Active Client Projects in Google Drive ({len(projs)} projects):</b>\n"
                lines = [header]
                display_limit = 20 if not filter_term else len(projs)
                for p in projs[:display_limit]:
                    cname = p.get("client_name_fa") or p.get("client_name") or p.get("folder_name")
                    fc = p.get("file_count", 0)
                    mc = p.get("message_count", 0)
                    st = p.get("status", "pending")
                    clean_p = clean_drive_display_path(p['folder_path'])
                    lines.append(
                        f"• <b>{html.escape(cname)}</b> (<i>{html.escape(st)}</i>) | {mc} msgs, {fc} files\n"
                        f"  ▫️ <code>{html.escape(clean_p)}</code>"
                    )
                if len(projs) > display_limit:
                    lines.append(f"\n<i>... and {len(projs) - display_limit} more projects. Use <code>/projects &lt;name&gt;</code> to filter.</i>")
                await event.reply("\n".join(lines), parse_mode="html")
                return

            # Manual Save / Archive Project: /save_project <name_or_id>
            m_save = re.match(r"^/(?:save_project|archive_project)(?:\s+(.+))?", txt)
            if m_save:
                target = m_save.group(1).strip() if m_save.group(1) else None
                if not target:
                    await event.reply("⚠️ Please specify client name, username, or Telegram ID:\nExample: <code>/save_project @username</code>", parse_mode="html")
                    return

                await event.reply(f"🔍 Searching chat and archiving project folder in Google Drive for: <code>{html.escape(target)}</code>...", parse_mode="html")
                target_dialog = None
                dialogs = await self.client.get_dialogs(limit=100)
                clean_target = target.lstrip("@").lower()

                for dlg in dialogs:
                    if not dlg.is_user or dlg.entity.is_self or dlg.entity.bot:
                        continue
                    uname = (getattr(dlg.entity, "username", None) or "").lower()
                    dname = (dlg.name or "").lower()
                    did_str = str(dlg.id)

                    if clean_target == uname or clean_target in dname or clean_target == did_str:
                        target_dialog = dlg
                        break

                if not target_dialog:
                    try:
                        ent = await self.client.get_entity(target)
                        client_name = f"{getattr(ent, 'first_name', '')} {getattr(ent, 'last_name', '') or ''}".strip() or str(ent.id)
                        res = await self.project_manager.save_client_chat_and_files(
                            client=self.client,
                            entity=ent,
                            client_name=client_name,
                            client_id=ent.id,
                            username=getattr(ent, "username", None),
                            limit_messages=200,
                            download_files=True
                        )
                        clean_p = clean_drive_display_path(res['project_dir'])
                        await event.reply(
                            f"✅ <b>Project synchronized in Google Drive:</b>\n"
                            f"👤 Client: <b>{html.escape(client_name)}</b>\n"
                            f"📁 Drive Folder: <code>{html.escape(clean_p)}</code>\n"
                            f"📊 Stats: {res['messages_count']} messages | {res['files_count']} files",
                            parse_mode="html"
                        )
                        return
                    except Exception as err:
                        await event.reply(f"❌ Client with identifier <code>{html.escape(target)}</code> not found: {err}", parse_mode="html")
                        return

                res = await self.project_manager.save_client_chat_and_files(
                    client=self.client,
                    entity=target_dialog.entity,
                    client_name=target_dialog.name,
                    client_id=target_dialog.id,
                    username=getattr(target_dialog.entity, "username", None),
                    limit_messages=200,
                    download_files=True
                )
                clean_p = clean_drive_display_path(res['project_dir'])
                await event.reply(
                    f"✅ <b>Project synchronized in Google Drive:</b>\n"
                    f"👤 Client: <b>{html.escape(target_dialog.name)}</b>\n"
                    f"📁 Drive Folder: <code>{html.escape(clean_p)}</code>\n"
                    f"📊 Stats: {res['messages_count']} messages | {res['files_count']} files",
                    parse_mode="html"
                )
                return

            # Sync all recent projects: /sync_projects
            if txt in ["/sync_projects", "/sync_all"]:
                await event.reply("🔄 Synchronizing and provisioning Google Drive project folders for recent clients...", parse_mode="html")
                dialogs = await self.client.get_dialogs(limit=30)
                client_dialogs = [d for d in dialogs if d.is_user and not d.entity.is_self and not d.entity.bot]
                synced_count = 0
                for cd in client_dialogs:
                    try:
                        await self.project_manager.save_client_chat_and_files(
                            client=self.client,
                            entity=cd.entity,
                            client_name=cd.name,
                            client_id=cd.id,
                            username=getattr(cd.entity, "username", None),
                            limit_messages=60,
                            download_files=True
                        )
                        synced_count += 1
                    except Exception as e:
                        print(f"[-] Error syncing dialog {cd.name}: {e}")

                await event.reply(
                    f"✅ Synchronization complete. {synced_count} client project folders updated in Google Drive.\n"
                    "Use <code>/projects</code> to view the catalog.",
                    parse_mode="html"
                )
                return

            # Send quote command: /send_Q101
            m_send = re.match(r"^/send_(Q\d+)", txt)
            if m_send:
                qid = m_send.group(1)
                if qid in self.pending_quotes:
                    entry = self.pending_quotes[qid]
                    # Client message is authentic Persian with clean HTML
                    card = format_telegram_card(entry["quote"], lang="fa")
                    target_client = entry.get("client_source") or self.client
                    await target_client.send_message(entry["chat_id"], card, parse_mode="html")
                    await event.reply(f"✅ Quotation {qid} was successfully dispatched to {entry['sender_name']}.", parse_mode="html")
                    del self.pending_quotes[qid]
                else:
                    await event.reply(f"❌ Quotation ID {qid} not found.", parse_mode="html")

            # Adjust price command: /adjust_Q101_8500000
            m_adj = re.match(r"^/adjust_(Q\d+)_(\d+)", txt)
            if m_adj:
                qid = m_adj.group(1)
                new_price = int(m_adj.group(2))
                if qid in self.pending_quotes:
                    entry = self.pending_quotes[qid]
                    entry["quote"]["total_price_tomans"] = new_price
                    entry["quote"]["total_price_formatted"] = f"{new_price:,.0f} تومان"
                    # Client message is authentic Persian with clean HTML
                    card = format_telegram_card(entry["quote"], lang="fa")
                    target_client = entry.get("client_source") or self.client
                    await target_client.send_message(entry["chat_id"], card, parse_mode="html")
                    await event.reply(f"✅ Quotation {qid} adjusted to {new_price:,.0f} Tomans and dispatched to {entry['sender_name']}.", parse_mode="html")
                    del self.pending_quotes[qid]
                else:
                    await event.reply(f"❌ Quotation ID {qid} not found.", parse_mode="html")

            # Ignore quote command: /ignore_Q101
            m_ign = re.match(r"^/ignore_(Q\d+)", txt)
            if m_ign:
                qid = m_ign.group(1)
                if qid in self.pending_quotes:
                    del self.pending_quotes[qid]
                    await event.reply(f"🗑️ Quotation {qid} was dismissed.", parse_mode="html")

            # Send co-pilot draft command: /send_msg_D101 or /send_msg_D101 <custom text>
            m_draft = re.match(r"^/send_msg_(D\d+)(?:\s+(.+))?", txt, flags=re.DOTALL)
            if m_draft:
                did = m_draft.group(1)
                custom_text = (m_draft.group(2) or "").strip()
                if did in self.pending_drafts:
                    entry = self.pending_drafts[did]
                    msg_to_send = custom_text if custom_text else entry["draft_reply"]
                    target_client = entry.get("client_source") or self.client
                    await target_client.send_message(entry["chat_id"], msg_to_send)
                    await event.reply(
                        f"✅ Response {did} was successfully dispatched to {entry['sender_name']} via {entry['account_label']}.",
                        parse_mode="html"
                    )
                    del self.pending_drafts[did]
                else:
                    await event.reply(f"❌ Draft ID {did} not found or already sent.", parse_mode="html")
                return

            # Ignore co-pilot draft command: /ignore_D101
            m_ign_draft = re.match(r"^/ignore_(D\d+)", txt)
            if m_ign_draft:
                did = m_ign_draft.group(1)
                if did in self.pending_drafts:
                    cname = self.pending_drafts[did]["sender_name"]
                    del self.pending_drafts[did]
                    await event.reply(f"🗑️ Draft {did} for {cname} was dismissed.", parse_mode="html")
                else:
                    await event.reply(f"❌ Draft ID {did} not found.", parse_mode="html")
                return

            # Health check & Follow-Up Reminders command: /health, /reminders, /followup
            if txt in ["/health", "/reminders", "/followup", "/project_health"]:
                await event.reply("🔍 Auditing project health and scanning for follow-up reminders...", parse_mode="html")
                await self.scan_and_report_project_health(trigger_event=event)
                return

            # Send follow-up command: /send_fu_F101 or /send_fu_F101 <custom text>
            m_fu = re.match(r"^/send_fu_(F\d+)(?:\s+(.+))?", txt, flags=re.DOTALL)
            if m_fu:
                fuid = m_fu.group(1)
                custom_text = (m_fu.group(2) or "").strip()
                if fuid in self.pending_followups:
                    entry = self.pending_followups[fuid]
                    msg_to_send = custom_text if custom_text else entry["draft_reply"]
                    target_dest = entry.get("telegram_id") or entry.get("username") or entry.get("client_name")
                    try:
                        await self.client.send_message(target_dest, msg_to_send)
                        if entry.get("folder_path"):
                            self.project_manager.record_followup_dispatched(entry["folder_path"], entry["followup_type"], msg_to_send)
                        await event.reply(
                            f"✅ Follow-up {fuid} was successfully dispatched to <b>{entry['client_name']}</b> via Saber's personal account.",
                            parse_mode="html"
                        )
                        del self.pending_followups[fuid]
                    except Exception as send_err:
                        await event.reply(f"❌ Failed to send follow-up {fuid}: {send_err}", parse_mode="html")
                else:
                    await event.reply(f"❌ Follow-up ID {fuid} not found or already sent.", parse_mode="html")
                return

            # Ignore follow-up command: /ignore_fu_F101
            m_ign_fu = re.match(r"^/ignore_fu_(F\d+)", txt)
            if m_ign_fu:
                fuid = m_ign_fu.group(1)
                if fuid in self.pending_followups:
                    cname = self.pending_followups[fuid]["client_name"]
                    del self.pending_followups[fuid]
                    await event.reply(f"🗑️ Follow-up reminder {fuid} for {cname} was dismissed.", parse_mode="html")
                else:
                    await event.reply(f"❌ Follow-up ID {fuid} not found.", parse_mode="html")
                return

            # Deliverables inspection command: /deliverables [client_query] or /files [client_query]
            m_deliv = re.match(r"^/(?:deliverables|files)(?:\s+(.+))?", txt)
            if m_deliv:
                c_query = (m_deliv.group(1) or "").strip()
                if not c_query:
                    # Overview of all projects with deliverables
                    projs = self.project_manager.list_all_projects()
                    ready_list = []
                    for p in projs:
                        d_files = self.project_manager.list_project_deliverables(p["folder_path"])
                        if d_files:
                            ready_list.append((p, d_files))
                    if not ready_list:
                        await event.reply("📦 No completed deliverables currently waiting in Google Drive <code>03_deliverables/</code>.", parse_mode="html")
                        return
                    lines = [f"📦 <b>Client Projects with Ready Deliverables ({len(ready_list)} clients):</b>\n"]
                    for p, dfs in ready_list[:15]:
                        cname = p.get("client_name_fa") or p.get("client_name") or p.get("folder_name")
                        files_str = ", ".join([f"<code>{f['filename']}</code> ({f['size_str']})" for f in dfs[:3]])
                        if len(dfs) > 3:
                            files_str += f" and {len(dfs)-3} more"
                        lines.append(
                            f"• <b>{html.escape(cname)}</b> ({len(dfs)} files):\n"
                            f"  ▫️ {files_str}\n"
                            f"  👉 <code>/deliverables {html.escape(cname)}</code>"
                        )
                    await event.reply("\n".join(lines), parse_mode="html")
                    return
                else:
                    # Find project for specific client
                    clean_q = c_query.lstrip("@").lower()
                    matched_pdir = self.project_manager.find_existing_project_by_client(clean_q)
                    target_meta = {}
                    if not matched_pdir and clean_q.isdigit():
                        matched_pdir = self.project_manager.find_existing_project_by_client("Client", client_id=int(clean_q))
                    if not matched_pdir:
                        projs = self.project_manager.list_all_projects()
                        for p in projs:
                            if clean_q in (p.get("client_name") or "").lower() or \
                               clean_q in (p.get("client_name_fa") or "").lower() or \
                               clean_q in (p.get("folder_name") or "").lower() or \
                               clean_q in (p.get("username") or "").lower():
                                matched_pdir = p["folder_path"]
                                target_meta = p
                                break
                    if not matched_pdir:
                        await event.reply(f"❌ No project folder found for client <code>{html.escape(c_query)}</code>.", parse_mode="html")
                        return

                    if not target_meta and os.path.exists(os.path.join(matched_pdir, "project_meta.json")):
                        try:
                            with open(os.path.join(matched_pdir, "project_meta.json"), "r", encoding="utf-8") as f:
                                target_meta = json.load(f)
                        except Exception:
                            pass

                    cname = target_meta.get("client_name_fa") or target_meta.get("client_name") or os.path.basename(matched_pdir)
                    d_files = self.project_manager.list_project_deliverables(matched_pdir)
                    clean_p = clean_drive_display_path(matched_pdir)
                    if not d_files:
                        await event.reply(
                            f"📦 Project folder found for <b>{html.escape(cname)}</b>, but <code>03_deliverables/</code> is empty.\n"
                            f"📁 Folder: <code>{html.escape(clean_p)}</code>",
                            parse_mode="html"
                        )
                        return

                    lines = [
                        f"📦 <b>Deliverables for {html.escape(cname)} ({len(d_files)} files):</b>",
                        f"📁 <code>{html.escape(clean_p)}</code>\n"
                    ]
                    for idx, df in enumerate(d_files[:10], start=1):
                        lines.append(
                            f"{idx}. 📄 <b>{html.escape(df['filename'])}</b>\n"
                            f"   ▫️ Size: <code>{df['size_str']}</code> | Modified: <code>{df['modified_at']}</code>\n"
                            f"   👉 Dispatch draft: <code>/send_file {html.escape(cname)} {html.escape(df['filename'])}</code>"
                        )
                    await event.reply("\n".join(lines), parse_mode="html")
                    return

            # Prepare deliverable dispatch: /send_file <client_query> [filename_query]
            m_send_file = re.match(r"^/(?:send_file|deliver)(?:\s+([^\s]+))?(?:\s+(.+))?", txt)
            if m_send_file and not txt.startswith("/send_del_"):
                c_query = (m_send_file.group(1) or "").strip()
                file_query = (m_send_file.group(2) or "").strip()
                if not c_query:
                    await event.reply(
                        "⚠️ Please specify client identifier and optional filename:\n"
                        "Example: <code>/send_file @username</code> or <code>/send_file Zahra فصل_چهارم</code>",
                        parse_mode="html"
                    )
                    return

                clean_q = c_query.lstrip("@").lower()
                matched_pdir = self.project_manager.find_existing_project_by_client(clean_q)
                target_meta = {}
                if not matched_pdir and clean_q.isdigit():
                    matched_pdir = self.project_manager.find_existing_project_by_client("Client", client_id=int(clean_q))
                if not matched_pdir:
                    projs = self.project_manager.list_all_projects()
                    for p in projs:
                        if clean_q in (p.get("client_name") or "").lower() or \
                           clean_q in (p.get("client_name_fa") or "").lower() or \
                           clean_q in (p.get("folder_name") or "").lower() or \
                           clean_q in (p.get("username") or "").lower():
                            matched_pdir = p["folder_path"]
                            target_meta = p
                            break
                if not matched_pdir:
                    await event.reply(f"❌ No project folder found for client <code>{html.escape(c_query)}</code>.", parse_mode="html")
                    return

                if not target_meta and os.path.exists(os.path.join(matched_pdir, "project_meta.json")):
                    try:
                        with open(os.path.join(matched_pdir, "project_meta.json"), "r", encoding="utf-8") as f:
                            target_meta = json.load(f)
                    except Exception:
                        pass

                cname = target_meta.get("client_name_fa") or target_meta.get("client_name") or os.path.basename(matched_pdir)
                cid = target_meta.get("telegram_id")
                uname = target_meta.get("telegram_username") or target_meta.get("username")

                # Locate deliverable file
                if file_query:
                    chosen_file = self.project_manager.find_deliverable_file(matched_pdir, file_query)
                    if not chosen_file:
                        await event.reply(f"❌ File matching <code>{html.escape(file_query)}</code> not found in <code>03_deliverables/</code> for <b>{html.escape(cname)}</b>.", parse_mode="html")
                        return
                else:
                    d_files = self.project_manager.list_project_deliverables(matched_pdir)
                    if not d_files:
                        await event.reply(f"📦 <code>03_deliverables/</code> is empty for <b>{html.escape(cname)}</b>.", parse_mode="html")
                        return
                    if len(d_files) == 1:
                        chosen_file = d_files[0]
                    else:
                        files_str = "\n".join([f"• <code>{f['filename']}</code> — <code>/send_file {html.escape(c_query)} {html.escape(f['filename'])}</code>" for f in d_files[:10]])
                        await event.reply(
                            f"📦 Multiple deliverables found for <b>{html.escape(cname)}</b>. Please specify which file to send:\n\n{files_str}",
                            parse_mode="html"
                        )
                        return

                self.deliverable_counter += 1
                del_id = f"DEL{self.deliverable_counter}"
                caption_text = generate_deliverable_caption(cname, chosen_file["filename"])

                self.pending_deliverables[del_id] = {
                    "del_id": del_id,
                    "client_name": cname,
                    "telegram_id": cid,
                    "username": uname,
                    "folder_path": matched_pdir,
                    "file_path": chosen_file["file_path"],
                    "filename": chosen_file["filename"],
                    "size_str": chosen_file["size_str"],
                    "caption": caption_text,
                    "created_at": datetime.now().isoformat()
                }

                client_link = format_client_mention_html(cname, username=uname, client_id=cid)
                clean_p = clean_drive_display_path(matched_pdir)
                safe_cap = html.escape(caption_text)

                card_text = (
                    f"📦 <b>[Deliverable Dispatch Draft ({del_id})] {client_link}</b>\n"
                    f"📁 <b>Project:</b> <code>{html.escape(clean_p)}</code>\n"
                    f"📄 <b>File:</b> <code>{html.escape(chosen_file['filename'])}</code> ({chosen_file['size_str']})\n"
                    "─────────────────────\n"
                    "📝 <b>Persian Delivery Caption:</b>\n"
                    f"<blockquote>{safe_cap}</blockquote>\n\n"
                    "⚙️ <b>Actions & Commands:</b>\n"
                    f"• Approve & Send File: <code>/send_del_{del_id}</code>\n"
                    f"• Send with Custom Caption: <code>/send_del_{del_id} &lt;custom caption&gt;</code>\n"
                    f"• Dismiss Delivery: <code>/ignore_del_{del_id}</code>"
                )

                card_btns = None
                if Button is not None:
                    card_btns = [
                        [Button.inline(f"🚀 Send Deliverable ({del_id})", f"send_del_{del_id}".encode()),
                         Button.inline("🗑️ Dismiss", f"ignore_del_{del_id}".encode())]
                    ]

                await self.send_to_desk(card_text, buttons=card_btns, parse_mode="html")
                print(f"[+] Prepared Deliverable draft card {del_id} for {cname}: {chosen_file['filename']}")
                return

            # Approve & Send deliverable file: /send_del_DEL101 or /send_del_DEL101 <custom caption>
            m_send_del = re.match(r"^/send_del_(DEL\d+)(?:\s+(.+))?", txt, flags=re.DOTALL)
            if m_send_del:
                del_id = m_send_del.group(1)
                custom_caption = (m_send_del.group(2) or "").strip()
                if del_id in self.pending_deliverables:
                    entry = self.pending_deliverables[del_id]
                    caption_to_send = custom_caption if custom_caption else entry["caption"]
                    target_dest = entry.get("telegram_id")
                    if target_dest is None:
                        if entry.get("username"):
                            target_dest = entry["username"].lstrip("@")
                        else:
                            target_dest = entry.get("client_name")
                    elif isinstance(target_dest, str) and target_dest.isdigit():
                        target_dest = int(target_dest)

                    file_path = entry["file_path"]
                    if not os.path.exists(file_path):
                        await event.reply(f"❌ Deliverable file not found on disk: <code>{html.escape(file_path)}</code>", parse_mode="html")
                        return

                    target_client = entry.get("client_source") or self.client
                    try:
                        try:
                            ent = await target_client.get_entity(target_dest)
                        except Exception:
                            ent = target_dest
                        await target_client.send_file(ent, file=file_path, caption=caption_to_send)
                        if entry.get("folder_path"):
                            self.project_manager.record_deliverable_dispatched(
                                entry["folder_path"],
                                entry["filename"],
                                entry["client_name"]
                            )
                        await event.reply(
                            f"✅ Deliverable <b>{html.escape(entry['filename'])}</b> was successfully dispatched to <b>{html.escape(entry['client_name'])}</b> via Saber's personal account and archived in drafts_archive.",
                            parse_mode="html"
                        )
                        del self.pending_deliverables[del_id]
                    except Exception as send_err:
                        await event.reply(f"❌ Failed to send deliverable {del_id}: {send_err}", parse_mode="html")
                else:
                    await event.reply(f"❌ Deliverable ID {del_id} not found or already sent.", parse_mode="html")
                return

            # Ignore deliverable draft: /ignore_del_DEL101
            m_ign_del = re.match(r"^/ignore_del_(DEL\d+)", txt)
            if m_ign_del:
                del_id = m_ign_del.group(1)
                if del_id in self.pending_deliverables:
                    cname = self.pending_deliverables[del_id]["client_name"]
                    del self.pending_deliverables[del_id]
                    await event.reply(f"🗑️ Deliverable draft {del_id} for {cname} was dismissed.", parse_mode="html")
                else:
                    await event.reply(f"❌ Deliverable ID {del_id} not found.", parse_mode="html")
                return

        if self.bot_client:
            @self.bot_client.on(events.CallbackQuery)
            async def bot_callback_handler(event):
                data = (event.data or b"").decode("utf-8")
                if data.startswith("send_draft_"):
                    did = data.split("send_draft_")[1]
                    if did in self.pending_drafts:
                        entry = self.pending_drafts[did]
                        target_client = entry.get("client_source") or self.client
                        await target_client.send_message(entry["chat_id"], entry["draft_reply"])
                        await event.answer(f"✅ Response {did} dispatched to client!", alert=True)
                        try:
                            await event.edit(
                                f"{event.message.text}\n\n✅ <b>Response was approved and dispatched to client via {entry['account_label']}.</b>",
                                buttons=None,
                                parse_mode="html"
                            )
                        except Exception:
                            pass
                        del self.pending_drafts[did]
                    else:
                        await event.answer(f"❌ Draft ID {did} expired or not found.", alert=True)
                elif data.startswith("ignore_draft_"):
                    did = data.split("ignore_draft_")[1]
                    if did in self.pending_drafts:
                        del self.pending_drafts[did]
                        await event.answer("🗑️ Draft dismissed.", alert=True)
                        try:
                            await event.edit(
                                f"{event.message.text}\n\n🗑️ <b>This draft recommendation was dismissed.</b>",
                                buttons=None,
                                parse_mode="html"
                            )
                        except Exception:
                            pass
                    else:
                        await event.answer(f"❌ Draft ID {did} not found.", alert=True)
                elif data.startswith("send_fu_"):
                    fuid = data.split("send_fu_")[1]
                    if fuid in self.pending_followups:
                        entry = self.pending_followups[fuid]
                        target_dest = entry.get("telegram_id") or entry.get("username") or entry.get("client_name")
                        try:
                            await self.client.send_message(target_dest, entry["draft_reply"])
                            if entry.get("folder_path"):
                                self.project_manager.record_followup_dispatched(entry["folder_path"], entry["followup_type"], entry["draft_reply"])
                            await event.answer(f"✅ Follow-up {fuid} dispatched to {entry['client_name']}!", alert=True)
                            try:
                                await event.edit(
                                    f"{event.message.text}\n\n✅ <b>Follow-up was approved and dispatched to client via Saber's personal account.</b>",
                                    buttons=None,
                                    parse_mode="html"
                                )
                            except Exception:
                                pass
                            del self.pending_followups[fuid]
                        except Exception as e:
                            await event.answer(f"❌ Send failed: {e}", alert=True)
                    else:
                        await event.answer(f"❌ Follow-up ID {fuid} expired or not found.", alert=True)
                elif data.startswith("ignore_fu_"):
                    fuid = data.split("ignore_fu_")[1]
                    if fuid in self.pending_followups:
                        del self.pending_followups[fuid]
                        await event.answer("🗑️ Follow-up reminder dismissed.", alert=True)
                        try:
                            await event.edit(
                                f"{event.message.text}\n\n🗑️ <b>This follow-up reminder was dismissed.</b>",
                                buttons=None,
                                parse_mode="html"
                            )
                        except Exception:
                            pass
                    else:
                        await event.answer(f"❌ Follow-up ID {fuid} not found.", alert=True)
                elif data.startswith("send_del_"):
                    del_id = data.split("send_del_")[1]
                    if del_id in self.pending_deliverables:
                        entry = self.pending_deliverables[del_id]
                        target_dest = entry.get("telegram_id")
                        if target_dest is None:
                            if entry.get("username"):
                                target_dest = entry["username"].lstrip("@")
                            else:
                                target_dest = entry.get("client_name")
                        elif isinstance(target_dest, str) and target_dest.isdigit():
                            target_dest = int(target_dest)

                        file_path = entry["file_path"]
                        if not os.path.exists(file_path):
                            await event.answer("❌ File not found on disk!", alert=True)
                            return

                        target_client = entry.get("client_source") or self.client
                        try:
                            try:
                                ent = await target_client.get_entity(target_dest)
                            except Exception:
                                ent = target_dest
                            await target_client.send_file(ent, file=file_path, caption=entry["caption"])
                            if entry.get("folder_path"):
                                self.project_manager.record_deliverable_dispatched(
                                    entry["folder_path"],
                                    entry["filename"],
                                    entry["client_name"]
                                )
                            await event.answer(f"✅ Deliverable {entry['filename']} dispatched to {entry['client_name']}!", alert=True)
                            try:
                                await event.edit(
                                    f"{event.message.text}\n\n✅ <b>Deliverable was approved and dispatched to client via Saber's personal account.</b>",
                                    buttons=None,
                                    parse_mode="html"
                                )
                            except Exception:
                                pass
                            del self.pending_deliverables[del_id]
                        except Exception as e:
                            await event.answer(f"❌ Send failed: {e}", alert=True)
                    else:
                        await event.answer(f"❌ Deliverable ID {del_id} expired or not found.", alert=True)
                elif data.startswith("ignore_del_"):
                    del_id = data.split("ignore_del_")[1]
                    if del_id in self.pending_deliverables:
                        del self.pending_deliverables[del_id]
                        await event.answer("🗑️ Deliverable draft dismissed.", alert=True)
                        try:
                            await event.edit(
                                f"{event.message.text}\n\n🗑️ <b>This deliverable dispatch draft was dismissed.</b>",
                                buttons=None,
                                parse_mode="html"
                            )
                        except Exception:
                            pass
                    else:
                        await event.answer(f"❌ Deliverable ID {del_id} not found.", alert=True)
                elif data == "cmd_deliverables":
                    projs = self.project_manager.list_all_projects()
                    ready_list = []
                    for p in projs:
                        d_files = self.project_manager.list_project_deliverables(p["folder_path"])
                        if d_files:
                            ready_list.append((p, d_files))
                    if not ready_list:
                        await event.answer("📦 No deliverables currently waiting in Google Drive.", alert=True)
                    else:
                        await event.answer(f"Found {len(ready_list)} clients with ready deliverables.")
                        lines = [f"📦 <b>Client Projects with Ready Deliverables ({len(ready_list)} clients):</b>\n"]
                        for p, dfs in ready_list[:15]:
                            cname = p.get("client_name_fa") or p.get("client_name") or p.get("folder_name")
                            files_str = ", ".join([f"<code>{f['filename']}</code> ({f['size_str']})" for f in dfs[:3]])
                            if len(dfs) > 3:
                                files_str += f" and {len(dfs)-3} more"
                            lines.append(
                                f"• <b>{html.escape(cname)}</b> ({len(dfs)} files):\n"
                                f"  ▫️ {files_str}\n"
                                f"  👉 <code>/deliverables {html.escape(cname)}</code>"
                            )
                        btn = [[Button.inline("❌ Close Catalog", b"cmd_close")]] if Button is not None else None
                        await self.send_to_desk("\n".join(lines), buttons=btn, parse_mode="html")
                elif data == "cmd_health":
                    await event.answer("🔍 Auditing project health...")
                    await self.scan_and_report_project_health(trigger_event=event)
                elif data.startswith("send_"):
                    qid = data.split("send_")[1]
                    if qid in self.pending_quotes:
                        entry = self.pending_quotes[qid]
                        # Client receives Persian quote
                        card = format_telegram_card(entry["quote"], lang="fa")
                        target_client = entry.get("client_source") or self.client
                        await target_client.send_message(entry["chat_id"], card, parse_mode="html")
                        await event.answer(f"✅ Quotation {qid} dispatched to client!", alert=True)
                        try:
                            await event.edit(f"{event.message.text}\n\n✅ <b>Quotation was approved and dispatched to client.</b>", buttons=None, parse_mode="html")
                        except Exception:
                            pass
                        del self.pending_quotes[qid]
                    else:
                        await event.answer(f"❌ Quotation ID {qid} expired or not found.", alert=True)
                elif data.startswith("ignore_"):
                    qid = data.split("ignore_")[1]
                    if qid in self.pending_quotes:
                        del self.pending_quotes[qid]
                        await event.answer("🗑️ Quotation dismissed.", alert=True)
                        try:
                            await event.edit(f"{event.message.text}\n\n🗑️ <b>This quotation was dismissed.</b>", buttons=None, parse_mode="html")
                        except Exception:
                            pass
                    else:
                        await event.answer(f"❌ Quotation ID {qid} not found.", alert=True)
                elif data == "cmd_projects":
                    projs = self.project_manager.list_all_projects()
                    await event.answer(f"Found {len(projs)} active projects in Google Drive.")
                    if projs:
                        lines = [f"📂 <b>Active Client Projects in Google Drive ({len(projs)} projects):</b>\n"]
                        for p in projs[:15]:
                            cname = p.get("client_name_fa") or p.get("client_name") or p.get("folder_name")
                            cpath = clean_drive_display_path(p['folder_path'])
                            st = p.get('status', 'pending')
                            lines.append(f"• <b>{html.escape(cname)}</b> (<i>{html.escape(st)}</i>) | <code>{html.escape(cpath)}</code>")
                        if len(projs) > 15:
                            lines.append(f"\n<i>... and {len(projs) - 15} more projects in Google Drive. Use <code>/projects &lt;name&gt;</code> to filter.</i>")
                        btn = [[Button.inline("❌ Close Catalog", b"cmd_close")]] if Button is not None else None
                        await self.send_to_desk("\n".join(lines), buttons=btn, parse_mode="html")
                elif data == "cmd_unread":
                    await event.answer("🔍 Scanning client messages...")
                    await self.scan_and_process_unread_messages(trigger_event=event)
                elif data == "cmd_close":
                    try:
                        await event.delete()
                    except Exception:
                        pass

            @self.bot_client.on(events.InlineQuery)
            async def bot_inline_handler(event):
                query = (event.text or "").strip()
                builder = event.builder
                results = []

                # 1. Questionnaire / Scale lookup: "@SaberAcademicBot scale <name>"
                scale_query = re.sub(r"^(?:scale|پرسشنامه|مقیاس)\s+", "", query, flags=re.IGNORECASE).strip()
                if questionnaire_resolver and scale_query:
                    profile = questionnaire_resolver.get_scale_profile(scale_query)
                    if profile and profile.get("found_in_registry"):
                        p_name = profile.get("scale_persian_name") or profile.get("scale_name")
                        n_items = profile.get("total_items_count", "N/A")
                        subscales = profile.get("subscales", [])
                        sub_text = "\n".join([f"  ▫️ {s}" for s in subscales[:4]]) if subscales else "تک‌عاملی"
                        card_fa = (
                            f"📋 <b>شناسنامه ابزار: {html.escape(p_name)}</b>\n\n"
                            f"• <b>تعداد گویه‌ها:</b> {n_items}\n"
                            f"• <b>نمره‌گذاری:</b> طیف لیکرت استاندارد\n"
                            f"• <b>مولفه‌ها / خرده‌مقیاس‌ها:</b>\n{sub_text}\n\n"
                            f"✅ <i>موجود در بانک ۴,۸۸۰ پرسشنامه استاندارد آماده اجرا.</i>"
                        )
                        results.append(
                            await builder.article(
                                title=f"Scale: {p_name}",
                                description=f"{n_items} items | Ready for research",
                                text=card_fa,
                                parse_mode="html"
                            )
                        )

                # 2. Quotation quick template: "@SaberAcademicBot quote"
                if not query or any(w in query.lower() for w in ["quote", "price", "قیمت", "تعرفه"]):
                    sample_quote = calculate_quotation(
                        analyze_proposal_text("عنوان: تحلیل آماری فصل چهارم و پنجم پایان‌نامه کارشناسی ارشد\nطرح: همبستگی و رگرسیون\nنمونه: ۲۰۰ نفر"),
                        self.persona
                    )
                    card_fa = format_telegram_card(sample_quote, lang="fa")
                    results.append(
                        await builder.article(
                            title="Academic Thesis Quotation Template",
                            description="Standard APA 7 Chapter 3-5 pricing & delivery timeline",
                            text=card_fa,
                            parse_mode="html"
                        )
                    )

                # 3. Google Drive Projects: "@SaberAcademicBot projects"
                if not query or any(w in query.lower() for w in ["projects", "drive", "پروژه"]):
                    projs = self.project_manager.list_all_projects()
                    top_projs = projs[:8]
                    lines = [f"📂 <b>Active Client Projects ({len(projs)} registered):</b>\n"]
                    for p in top_projs:
                        cname = p.get("client_name_fa") or p.get("client_name") or p.get("folder_name")
                        st = p.get("status", "pending")
                        cpath = clean_drive_display_path(p["folder_path"])
                        lines.append(f"• <b>{html.escape(cname)}</b> (<i>{st}</i>) | <code>{html.escape(cpath)}</code>")
                    results.append(
                        await builder.article(
                            title=f"Google Drive Projects ({len(projs)} active)",
                            description="View current client project folders & statuses",
                            text="\n".join(lines),
                            parse_mode="html"
                        )
                    )

                if results:
                    await event.answer(results, cache_time=5)

            if self.admin_desk_chat_id:
                @self.bot_client.on(events.NewMessage(chats=self.admin_desk_chat_id))
                async def bot_admin_handler(event):
                    await admin_handler(event)

        # 2. Client Inbound Messages (Private Chats) across both personal accounts
        def setup_inbound_listener(client_inst, account_label):
            @client_inst.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
            async def client_handler(event):
                sender = await event.get_sender()
                if not isinstance(sender, User) or sender.is_self or sender.bot:
                    return
                if sender.id in [124911145, 6328062294, 777000]:
                    return

                client_name = f"{sender.first_name} {sender.last_name or ''}".strip()
                msg_text = (event.message.message or "").strip()

                # Resolve media details (documents, voice notes, photos, excluding stickers)
                fname, mtype, fsize, duration = resolve_media_details(event.message)

                # Terminal log preview
                if msg_text:
                    preview = msg_text[:60]
                elif mtype == "voice":
                    preview = f"[Voice Note: {duration}s]"
                elif mtype == "photo":
                    preview = "[Photo]"
                elif mtype == "video_note":
                    preview = f"[Video Note: {duration}s]"
                elif fname:
                    preview = f"[File: {fname}]"
                else:
                    preview = "[Sticker/Reaction]"

                print(f"[!] [{account_label}] New DM from client {client_name} (ID: {sender.id}): {preview}")

                # Check if contact is in the excluded non-academic contacts registry
                is_excluded = self.project_manager.is_ignored(client_name, sender.id, sender.username)
                has_doc = bool(fname and mtype in ["document", "voice", "photo", "video_note"])
                has_prop = bool(len(msg_text) > 80 and any(w in msg_text for w in ["عنوان", "فرضیه", "پروپوزال", "جامعه", "نمونه", "متغیر"]))

                if is_excluded and not has_doc and not has_prop:
                    # Silently skip casual message from excluded non-academic contact
                    return

                # Ensure client's Google Drive project folder is provisioned
                paths = self.project_manager.provision_project(
                    client_name=client_name,
                    client_id=sender.id,
                    username=sender.username,
                    phone=sender.phone
                )

                # Bot-specific commands (/start, /help, /dashboard, /webapp, /scale)
                if me.bot:
                    webapp_url = self.config.get("webapp_url", "")
                    has_web_btn = is_valid_telegram_button_url(webapp_url)

                    if msg_text in ["/webapp", "/dashboard", "داشبورد", "پنل"]:
                        dash_url = webapp_url if has_web_btn else "http://localhost:8080"
                        dashboard_msg = (
                            "🎓 **سامانه هوشمند و داشبورد تعاملی صابر قادری**\n\n"
                            "برای مشاهده وضعیت پروژه‌ها، محاسبه آنلاین پیش‌فاکتور تفکیکی، و جستجو در بانک ۴,۸۸۰ پرسشنامه استاندارد:\n\n"
                            f"🌐 آدرس پنل وب: `{dash_url}`\n\n"
                            "📌 *امکانات:*\n"
                            "• میز کار و پیگیری مراحل پروژه (Kanban Board)\n"
                            "• محاسبه‌گر آنلاین تعرفه فصل‌های ۳، ۴، ۵ و اسلایدهای دفاع\n"
                            "• شناسنامه مقیاس‌ها و عوامل پرسشنامه‌ها\n"
                            "• پشتیبانی دو زبانه (فارسی / انگلیسی)"
                        )
                        btn = [[Button.url("🚀 باز کردن داشبورد", webapp_url)]] if (Button is not None and has_web_btn) else None
                        await event.reply(dashboard_msg, buttons=btn)
                        return

                    if msg_text in ["/start", "سلام", "درود"]:
                        welcome_msg = (
                            f"سلام و درود، وقت شما بخیر {sender.first_name} گرامی.\n\n"
                            "دستیار هوشمند و مشاور پژوهشی صابر قادری در خدمت شماست.\n"
                            "خدمات قابل ارائه:\n"
                            "• بررسی پروپوزال و صدور پیش‌فاکتور تفکیکی (ارسال فایل یا متن)\n"
                            "• داشبورد و محاسبه‌گر آنلاین هزینه: `/dashboard`\n"
                            "• جستجوی پرسشنامه‌ها و مقیاس‌های روان‌سنجی: `/scale نام_پرسشنامه`\n"
                            "• مشاوره روش‌شناسی و تحلیل آماری\n\n"
                            "جهت استعلام هزینه و زمان‌بندی، فایل پروپوزال خود را ارسال بفرمایید یا داشبورد را باز کنید."
                        )
                        btn = [[Button.url("📱 ورود به داشبورد تعاملی", webapp_url)]] if (Button is not None and has_web_btn) else None
                        await event.reply(welcome_msg, buttons=btn)
                        return

                    if msg_text == "/help":
                        help_msg = (
                            "📚 **راهنمای دستورات:**\n"
                            "• `/dashboard`: باز کردن داشبورد تعاملی و محاسبه‌گر پیش‌فاکتور\n"
                            "• ارسال فایل پروپوزال (.docx یا .pdf) برای ارزیابی و استعلام قیمت\n"
                            "• `/scale <نام>`: جستجو در بانک ۴۸۸۰ پرسشنامه استاندارد\n"
                            "• `/start`: نمایش پیام آغازین و معرفی خدمات"
                        )
                        btn = [[Button.url("📱 ورود به داشبورد تعاملی", webapp_url)]] if (Button is not None and has_web_btn) else None
                        await event.reply(help_msg, buttons=btn)
                        return

                # Check for attached media (documents, voice notes, photos)
                if fname:
                    print(f"[+] Client {client_name} sent {mtype}: {fname}. Saving directly to Google Drive project...")
                    try:
                        local_path = await self.project_manager.save_single_file(
                            msg=event.message,
                            client_name=client_name,
                            client_id=sender.id,
                            username=sender.username
                        )
                        ext = os.path.splitext(fname)[1].lower()
                        if ext in [".docx", ".pdf", ".txt"]:
                            raw_content = extract_text_from_file(local_path)
                            await self.handle_proposal_message(
                                event, raw_content, client_name, file_name=fname, sender_id=sender.id, username=sender.username, client_source=client_inst
                            )
                            return
                        elif mtype in ["voice", "photo", "video_note"]:
                            # Notify Admin Desk about incoming voice or photo
                            clean_p = clean_drive_display_path(local_path)
                            client_link = format_client_mention_html(client_name, username=sender.username, client_id=sender.id)
                            icon = "🎤" if mtype == "voice" else ("📷" if mtype == "photo" else "📹")
                            type_title = "Voice Note" if mtype == "voice" else ("Photo" if mtype == "photo" else "Video Note")
                            dur_label = f" ({duration}s)" if duration else ""
                            await self.send_to_desk(
                                f"{icon} <b>New {type_title}{dur_label} from {client_link}</b>\n"
                                f"📁 <b>Saved to:</b> <code>{html.escape(clean_p)}</code>\n"
                                f"📱 <b>Account:</b> {html.escape(account_label)}",
                                parse_mode="html"
                            )
                    except Exception as err:
                        print(f"[-] Error saving incoming client file: {err}")

                # Check if long text proposal
                if len(msg_text) > 80 and any(w in msg_text for w in ["عنوان", "فرضیه", "پروپوزال", "جامعه", "نمونه", "متغیر"]):
                    await self.handle_proposal_message(
                        event, msg_text, client_name, sender_id=sender.id, username=sender.username, client_source=client_inst
                    )
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
                            p_name = profile.get("scale_persian_name") or profile.get("scale_name")
                            n_items = profile.get("total_items_count", "مشخص در شناسنامه")
                            subscales = profile.get("subscales", [])
                            sub_text = "، ".join(subscales[:3]) if subscales else "تک‌عاملی"
                            scale_info = (
                                f"سلام و احترام، وقت شما بخیر {sender.first_name} گرامی.\n"
                                f"پرسشنامه «{p_name}» ({n_items} گویه) با خرده‌مقیاس‌های استاندارد ({sub_text}) و شیوه نمره‌گذاری در بانک جامع مقیاس‌ها موجود است.\n"
                                "در صورت نیاز بفرمایید تا مشخصات فنی و فایل ابزار برای استفاده در پژوهش خدمتتون ارسال شود."
                            )
                        else:
                            scale_info = (
                                f"سلام و احترام، وقت شما بخیر {sender.first_name} گرامی.\n"
                                f"در مورد مقیاس «{query_name}»، نسخه و مشخصات روان‌سنجی آن در حال بررسی در آرشیو پژوهشی است و اطلاعات تکمیلی به زودی خدمتتون ارسال می‌شود."
                            )
                    else:
                        scale_info = (
                            f"سلام و احترام، وقت شما بخیر {sender.first_name} گرامی.\n"
                            f"پیام شما در خصوص مقیاس «{query_name}» دریافت شد. به زودی اطلاعات تکمیلی بررسی و خدمتتون ارسال می‌گردد."
                        )

                    if me.bot:
                        await event.reply(scale_info)
                    else:
                        await self.create_and_post_draft(
                            chat_id=event.chat_id,
                            sender_name=client_name,
                            sender_id=sender.id,
                            username=sender.username,
                            inquiry_type="scale_search",
                            client_message=msg_text,
                            draft_reply=scale_info,
                            client_source=client_inst,
                            account_label=account_label
                        )
                    return

                # Check for greeting or first contact
                greeting_words = ["سلام", "درود", "خسته نباشید", "وقت بخیر", "صبح بخیر", "عصر بخیر", "شب بخیر", "عرض ادب", "سلام علیکم"]
                is_greeting = any(w in msg_text for w in greeting_words) and len(msg_text.split()) <= 7
                if is_greeting:
                    greet_draft = (
                        f"سلام و عرض ادب، وقت شما بخیر {sender.first_name} گرامی.\n"
                        "صابر قادری هستم، در خدمتم؛ لطفاً بفرمایید موضوع پژوهش، عنوان پایان‌نامه یا فایلی که مدنظرتون هست مربوط به چه موضوعی است تا دقیقاً راهنمایی‌تون کنم."
                    )
                    if me.bot:
                        await event.reply(greet_draft)
                    else:
                        await self.create_and_post_draft(
                            chat_id=event.chat_id,
                            sender_name=client_name,
                            sender_id=sender.id,
                            username=sender.username,
                            inquiry_type="greeting",
                            client_message=msg_text,
                            draft_reply=greet_draft,
                            client_source=client_inst,
                            account_label=account_label
                        )
                    return

                # Check for statistical or methodology inquiry
                stats_keywords = [
                    "تحلیل", "آماری", "فصل چهار", "فصل ۴", "فصل پنجم", "فصل ۵", "spss", "pls", "amos", "smartpls",
                    "پایان‌نامه", "رساله", "روان‌سنجی", "کواریانس", "رگرسیون", "حجم نمونه", "جی‌پاور", "gpower"
                ]
                is_stats = any(w in msg_text.lower() for w in stats_keywords)
                if is_stats:
                    stats_draft = (
                        f"سلام و درود، وقت شما بخیر {sender.first_name} گرامی.\n"
                        "تحلیل‌های آماری، آزمون فرضیه‌ها و نگارش کامل فصل چهارم و پنجم بر اساس استانداردهای APA ویرایش هفتم و خروجی‌های معتبر نرم‌افزاری انجام می‌شود.\n"
                        "جهت بررسی دقیق‌تر و ارائه زمان‌بندی و هزینه، لطفاً فایل پروپوزال یا جدول متغیرها و فرضیه‌های خود را ارسال بفرمایید."
                    )
                    if me.bot:
                        await event.reply(stats_draft)
                    else:
                        await self.create_and_post_draft(
                            chat_id=event.chat_id,
                            sender_name=client_name,
                            sender_id=sender.id,
                            username=sender.username,
                            inquiry_type="statistical_inquiry",
                            client_message=msg_text,
                            draft_reply=stats_draft,
                            client_source=client_inst,
                            account_label=account_label
                        )
                    return

                # General client inquiry (fallback for non-empty text)
                if msg_text and len(msg_text.strip()) >= 2:
                    general_draft = (
                        f"سلام و احترام، وقت شما بخیر {sender.first_name} گرامی.\n"
                        "پیام شما دریافت شد. در خدمتم؛ بفرمایید در رابطه با چه بخشی از کار پژوهشی نیاز به راهنمایی و همکاری دارید؟"
                    )
                    if me.bot:
                        await event.reply(general_draft)
                    else:
                        await self.create_and_post_draft(
                            chat_id=event.chat_id,
                            sender_name=client_name,
                            sender_id=sender.id,
                            username=sender.username,
                            inquiry_type="general_inquiry",
                            client_message=msg_text,
                            draft_reply=general_draft,
                            client_source=client_inst,
                            account_label=account_label
                        )
                    return

        # Setup inbound listeners on both userbot accounts
        setup_inbound_listener(self.client, "Main Account (@GhaderiSaber)")
        if self.client2:
            setup_inbound_listener(self.client2, "Second Account (@SaberGhaderi)")

        if self.admin_desk_chat_id:
            desk_location = f"Academic Desk Group (ID: {self.admin_desk_chat_id})"
        else:
            desk_location = "Saved Messages" if not me.bot else f"Saber Private Chat (ID: {self.admin_id})"
        print(f"[*] Telethon {'Userbot' if not me.bot else 'Bot'} is active & listening to incoming DMs on all accounts...")
        print(f"[*] Google Drive Operational Root: {self.project_manager.work_dir}")
        print(f"[*] Open {desk_location} to view real-time proposal alerts, approve quotes, or manage projects.")

        # Scan and report any existing unread messages from clients on startup
        await self.scan_and_process_unread_messages()

        while True:
            try:
                gather_tasks = [self.client.run_until_disconnected()]
                if self.client2 and self.client2.is_connected():
                    gather_tasks.append(self.client2.run_until_disconnected())
                if self.bot_client and self.bot_client.is_connected():
                    gather_tasks.append(self.bot_client.run_until_disconnected())

                await asyncio.gather(*gather_tasks)
                break
            except (ConnectionError, OSError, asyncio.CancelledError) as e:
                print(f"[!] Userbot connection interrupted: {e}. Attempting auto-reconnect in 5s...")
                await asyncio.sleep(5)
                for cl_target in [self.client, self.client2, self.bot_client]:
                    if cl_target and not cl_target.is_connected():
                        try:
                            await cl_target.connect()
                        except Exception as rec_err:
                            print(f"[-] Reconnect error for client: {rec_err}")
            except Exception as e:
                print(f"[-] Unexpected error in listening loop: {e}. Retrying in 5s...")
                await asyncio.sleep(5)


async def main_async(args):
    config = load_telethon_config(args.config)
    if args.auto_reply:
        config["auto_reply"] = True
    if args.phone:
        config["phone_number"] = args.phone
    if args.bot_token:
        config["bot_token"] = args.bot_token
    if args.drive_dir:
        config["google_drive_work_dir"] = args.drive_dir

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

    if args.list_projects:
        projects = userbot.project_manager.list_all_projects()
        print(f"\n📂 Managed Client Projects on Google Drive ({len(projects)} total):")
        print("=" * 70)
        for p in projects:
            cname = p.get("client_name_fa") or p.get("client_name") or p.get("folder_name")
            print(f"• {cname} | Status: {p.get('status')} | Files: {p.get('file_count', 0)}")
            print(f"  Path: {p['folder_path']}")
        return

    if args.save_project:
        await userbot.init_client(phone=args.phone, bot_token=args.bot_token, use_qr=args.qr)
        target = args.save_project.strip()
        print(f"[*] Looking for client: {target}...")
        ent = await userbot.client.get_entity(target)
        cname = f"{getattr(ent, 'first_name', '')} {getattr(ent, 'last_name', '') or ''}".strip() or str(ent.id)
        res = await userbot.project_manager.save_client_chat_and_files(
            client=userbot.client,
            entity=ent,
            client_name=cname,
            client_id=ent.id,
            username=getattr(ent, "username", None),
            limit_messages=200,
            download_files=True
        )
        print(f"[+] Saved project to: {res['project_dir']}")
        print(f"[+] Messages: {res['messages_count']}, Files: {res['files_count']}")
        return

    if args.sync_all_projects:
        await userbot.init_client(phone=args.phone, bot_token=args.bot_token, use_qr=args.qr)
        print("[*] Synchronizing all recent client chats to Google Drive...")
        dialogs = await userbot.client.get_dialogs(limit=40)
        client_dialogs = [d for d in dialogs if d.is_user and not d.entity.is_self and not d.entity.bot]
        for cd in client_dialogs:
            try:
                await userbot.project_manager.save_client_chat_and_files(
                    client=userbot.client,
                    entity=cd.entity,
                    client_name=cd.name,
                    client_id=cd.id,
                    username=getattr(cd.entity, "username", None),
                    limit_messages=80,
                    download_files=True
                )
            except Exception as e:
                print(f"[-] Error: {cd.name}: {e}")
        print("[+] All recent projects synchronized.")
        return

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
    parser = argparse.ArgumentParser(description="Telethon MTProto Client & Google Drive Project Manager for Saber Ghaderi")
    parser.add_argument("--config", "-c", type=str, default=DEFAULT_CONFIG_PATH, help="Path to telethon_config.json")
    parser.add_argument("--phone", "-p", type=str, default=None, help="Phone number with country code (e.g., +98912XXXXXXX)")
    parser.add_argument("--bot-token", "-b", type=str, default=None, help="Telegram Bot Token from @BotFather")
    parser.add_argument("--qr", action="store_true", help="Log in by scanning a QR code in Telegram (bypasses reCAPTCHA & SMS)")
    parser.add_argument("--drive-dir", type=str, default=None, help="Custom Google Drive 'My Work' operational directory")
    parser.add_argument("--scan-unread", action="store_true", help="Scan unread messages, sync Drive projects, and report to Saved Messages")
    parser.add_argument("--crawl-chats", action="store_true", help="Crawl real Telegram client chats to calibrate persona & FAQs")
    parser.add_argument("--save-project", type=str, default=None, help="Archive and provision Google Drive project for specific client ID or username")
    parser.add_argument("--sync-all-projects", action="store_true", help="Crawl and provision Google Drive projects for all recent client chats")
    parser.add_argument("--list-projects", action="store_true", help="List all managed client projects in Google Drive")
    parser.add_argument("--listen", action="store_true", help="Run real-time listener for incoming client DMs")
    parser.add_argument("--auto-reply", action="store_true", help="Enable automatic replies to clients")

    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
