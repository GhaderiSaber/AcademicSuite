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
# Dynamic discovery of local virtualenv site-packages (.venv / venv)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

import json
import html
import asyncio
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

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
from group_topics import TopicManager
from academic_inquiry_classifier import AcademicInquiryClassifier
from milestone_tracker import AcademicMilestoneTracker, milestone_tracker
from morning_briefing import AcademicMorningBriefing
from math_formatter import AcademicMathFormatter
from voice_transcriber import AcademicVoiceTranscriber
from financial_ledger import AcademicFinancialLedger, format_toman
from deliverable_dispatcher import AcademicDeliverableDispatcher


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
        self.topic_manager = TopicManager(self.config, storage_dir=self.storage_dir)
        self.classifier = AcademicInquiryClassifier(self.config)
        self.milestone_tracker = AcademicMilestoneTracker(self.project_manager.work_dir)
        self.financial_ledger = AcademicFinancialLedger(self.project_manager.work_dir, storage_dir=self.storage_dir)
        self.morning_briefing = AcademicMorningBriefing(self.project_manager, self.milestone_tracker, financial_ledger=self.financial_ledger, storage_dir=self.storage_dir)
        self.voice_transcriber = AcademicVoiceTranscriber(self.config)
        self.deliverable_dispatcher = AcademicDeliverableDispatcher(self.project_manager, self.financial_ledger, self.milestone_tracker)

        self.persona = load_persona()
        self.pending_quotes: Dict[str, Dict[str, Any]] = {}
        self.quote_counter = 100
        self.drafts_file = os.path.join(self.storage_dir, "pending_drafts.json")
        self.pending_drafts: Dict[str, Dict[str, Any]] = self._load_pending_drafts()
        existing_d = [int(k[1:]) for k in self.pending_drafts.keys() if k.startswith("D") and k[1:].isdigit()]
        self.draft_counter = max(existing_d) if existing_d else 100
        self.pending_followups: Dict[str, Dict[str, Any]] = {}
        self.followup_counter = 100
        self.pending_deliverables: Dict[str, Dict[str, Any]] = {}
        self.deliverable_counter = 100
        self.math_registry: Dict[str, Dict[str, Any]] = {}
        self.math_counter = 100
        self.voice_registry: Dict[str, Dict[str, Any]] = {}
        for k, v in self.pending_drafts.items():
            if "voice_digest" in v:
                self.voice_registry[k] = {
                    "client_name": v.get("sender_name", "Client"),
                    "voice_digest": v["voice_digest"],
                    "topic_key": "supervisor_reviews" if v.get("inquiry_type") == "supervisor_defense_question" else "drafts",
                }
        self.pending_payments: Dict[str, Dict[str, Any]] = {}
        self.payment_counter = 100
        self.me = None
        self.proxy = get_proxy_settings(self.config)

        if not self.api_id or not self.api_hash or TelegramClient is None:
            self.client = None
        else:
            s1_name = self.session_name
            if not os.path.isabs(s1_name):
                repo_p = os.path.join(ROOT_DIR, s1_name)
                script_p = os.path.join(SCRIPT_DIR, s1_name)
                s1_path = repo_p if os.path.exists(repo_p + ".session") else (script_p if os.path.exists(script_p + ".session") else repo_p)
            else:
                s1_path = s1_name
            self.client = TelegramClient(s1_path, self.api_id, self.api_hash, proxy=self.proxy)

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

        # Conversational burst debounce buffers: (account_label, sender_id) -> burst dict
        self.burst_buffers: Dict[Tuple[str, int], Dict[str, Any]] = {}
        self.burst_lock = asyncio.Lock()

    def _load_pending_drafts(self) -> Dict[str, Dict[str, Any]]:
        drafts_file = getattr(self, "drafts_file", os.path.join(self.storage_dir, "pending_drafts.json"))
        if os.path.exists(drafts_file):
            try:
                with open(drafts_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[-] Error loading pending drafts: {e}")
        return {}

    def _save_pending_drafts(self):
        drafts_file = getattr(self, "drafts_file", os.path.join(self.storage_dir, "pending_drafts.json"))
        try:
            clean_dict = {}
            for k, v in self.pending_drafts.items():
                clean_v = dict(v)
                clean_v.pop("client_source", None)
                clean_dict[k] = clean_v
            with open(drafts_file, "w", encoding="utf-8") as f:
                json.dump(clean_dict, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[-] Error saving pending drafts: {e}")

    def build_approval_keyboard(
        self,
        approve_label: str,
        approve_data: Union[str, bytes],
        edit_label: Optional[str] = None,
        edit_query: Optional[str] = None,
        dismiss_label: str = "🗑️ Dismiss",
        dismiss_data: Union[str, bytes] = b"cmd_close",
        approve_icon: Optional[int] = None,
        edit_icon: Optional[int] = None,
        dismiss_icon: Optional[int] = None
    ) -> Optional[List[List[Any]]]:
        """
        Build a 2026 Telegram 2-row styled action keyboard:
        Row 1: [ 🚀 Approve & Send ] (style="success" -> vibrant green pill)
        Row 2: [ ✏️ Edit & Reply ] (style="primary" -> vibrant blue pill) + [ 🗑️ Dismiss ] (style="danger" -> soft red pill)
        Supports optional Telegram custom emoji document IDs via icon parameter.
        """
        if Button is None:
            return None

        custom_icons = self.config.get("custom_emoji_icons", {}) if hasattr(self, "config") and isinstance(self.config, dict) else {}
        a_icon = approve_icon if approve_icon is not None else custom_icons.get("approve")
        e_icon = edit_icon if edit_icon is not None else custom_icons.get("edit")
        d_icon = dismiss_icon if dismiss_icon is not None else custom_icons.get("dismiss")

        data_bytes = approve_data.encode("utf-8") if isinstance(approve_data, str) else approve_data
        dismiss_bytes = dismiss_data.encode("utf-8") if isinstance(dismiss_data, str) else dismiss_data

        try:
            row1 = [Button.inline(approve_label, data_bytes, style="success", icon=a_icon)]
            row2 = []
            if edit_label and edit_query:
                row2.append(Button.switch_inline(edit_label, edit_query, same_peer=True, style="primary", icon=e_icon))
            row2.append(Button.inline(dismiss_label, dismiss_bytes, style="danger", icon=d_icon))
            return [row1, row2]
        except Exception:
            row1 = [Button.inline(approve_label, data_bytes)]
            row2 = []
            if edit_label and edit_query:
                row2.append(Button.switch_inline(edit_label, edit_query, same_peer=True))
            row2.append(Button.inline(dismiss_label, dismiss_bytes))
            return [row1, row2]

    def build_milestone_keyboard(self, project_dir: str, state: Dict[str, Any]) -> Optional[List[List[Any]]]:
        """
        Build a 2026 Telegram 2-row styled action keyboard for project milestone card:
        Row 1: [ 🚀 Advance Stage ({code}) ] (style="success" -> vibrant green pill)
        Row 2: [ 📁 Refresh from Drive ] (style="primary") + [ 🔀 Scope: {scope_short} ] (style="primary")
        """
        if Button is None:
            return None
        folder_name = os.path.basename(project_dir)
        stage_code = state.get("current_stage_code", "Next")
        scope_short = state.get("scope_short", "Scope")
        adv_data = f"ms_adv_{folder_name}".encode("utf-8")
        ref_data = f"ms_ref_{folder_name}".encode("utf-8")
        scp_data = f"ms_scp_{folder_name}".encode("utf-8")

        try:
            row1 = [Button.inline(f"🚀 Advance Stage ({stage_code})", adv_data, style="success")]
            row2 = [
                Button.inline("📁 Refresh from Drive", ref_data, style="primary"),
                Button.inline(f"🔀 Scope: {scope_short}", scp_data, style="primary")
            ]
            return [row1, row2]
        except Exception:
            row1 = [Button.inline(f"🚀 Advance Stage ({stage_code})", adv_data)]
            row2 = [
                Button.inline("📁 Refresh from Drive", ref_data),
                Button.inline(f"🔀 Scope: {scope_short}", scp_data)
            ]
            return [row1, row2]

    @property
    def admin_target(self):
        """Return the destination peer for admin desk notifications."""
        if self.admin_desk_chat_id:
            return self.admin_desk_chat_id
        return "me" if (self.me and not self.me.bot) else self.admin_id

    async def send_to_desk(
        self,
        text: str,
        buttons=None,
        reply_to=None,
        topic_key: Optional[str] = None,
        client_id: Optional[int] = None,
        client_name: Optional[str] = None,
        parse_mode: str = "html"
    ):
        """
        Send an alert/message to the Admin Desk in English with HTML formatting.
        Automatically routes to the appropriate Forum Topic thread:
        1. Dedicated VIP topic if client_id or client_name is registered as VIP.
        2. Functional topic if topic_key provided ('proposals', 'drafts', 'scales', 'health', 'system').
        3. reply_to if passed explicitly.
        If bot_client is available and admin_desk_chat_id is set, the message is sent
        by Academic Assistant Bot rather than Saber's personal account!
        """
        target_reply_to = reply_to
        if not target_reply_to and self.topic_manager:
            target_reply_to = self.topic_manager.resolve_topic_id(
                topic_key=topic_key,
                client_id=client_id,
                client_name=client_name
            )

        if self.bot_client and self.admin_desk_chat_id:
            try:
                if not self.bot_client.is_connected():
                    await self.bot_client.connect()
                return await self.bot_client.send_message(
                    self.admin_desk_chat_id,
                    text,
                    buttons=buttons,
                    reply_to=target_reply_to,
                    parse_mode=parse_mode
                )
            except Exception as e:
                print(f"[-] Bot send to desk error: {e}, falling back to user client...")
        return await self.client.send_message(
            self.admin_target,
            text,
            buttons=buttons,
            reply_to=target_reply_to,
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

        header_lines = [
            "╭─ <b>📥 NEW RESEARCH PROPOSAL RECEIVED</b> ─────────────",
            f"│ 👤 <b>Client:</b> {client_link}  •  <code>#{sender_id}</code>",
            f"│ 📄 <b>File / Source:</b> <code>{safe_fname}</code>",
            f"│ 📁 <b>Drive:</b> <code>{html.escape(clean_path)}</code>",
            f"│ 🆔 <b>Quotation ID:</b> <code>{quote_id}</code>",
            "╰──────────────────────────────────────────────────"
        ]

        alert_text = (
            f"{chr(10).join(header_lines)}\n\n"
            f"📊 <b>DETAILED PROPOSAL BREAKDOWN & QUOTATION</b>\n"
            f"<blockquote expandable>{quote_card_en}</blockquote>\n\n"
            f"<i>Tap button below to dispatch, or tap to copy command:</i> <code>/send_{quote_id}</code>"
        )

        buttons = self.build_approval_keyboard(
            approve_label=f"🚀 Approve & Send ({quote_id})",
            approve_data=f"send_{quote_id}",
            edit_label="✏️ Adjust Price",
            edit_query=f"/adjust_{quote_id}_",
            dismiss_label="🗑️ Dismiss",
            dismiss_data=f"ignore_{quote_id}"
        )

        await self.send_to_desk(
            alert_text,
            buttons=buttons,
            topic_key="proposals",
            client_id=sender_id,
            client_name=client_name,
            parse_mode="html"
        )
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
        account_label: str = "Main Account (@GhaderiSaber)",
        topic_key: Optional[str] = None,
        admin_notes: Optional[str] = None,
        engine: Optional[str] = None,
        thinking_points: Optional[List[str]] = None
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
            "thinking_points": thinking_points or [],
            "created_at": datetime.now().isoformat()
        }
        self._save_pending_drafts()

        client_link = format_client_mention_html(sender_name, username=username, client_id=sender_id)
        safe_draft = html.escape(draft_reply)

        category_titles = {
            "supervisor_defense_question": "🎓 SUPERVISOR DEFENSE DILEMMA",
            "supervisor_revision_feedback": "🎓 SUPERVISOR REVISION FEEDBACK",
            "quarterly_progress_report": "📋 QUARTERLY PROGRESS REPORT",
            "statistical_consulting": "📊 STATISTICAL CONSULTING",
            "statistical_inquiry": "📊 STATISTICAL ANALYSIS & INQUIRY",
            "scale_search": "🔬 PSYCHOMETRIC SCALE RESOLUTION",
            "scale_inquiry": "🔬 PSYCHOMETRIC SCALE INQUIRY",
            "friendly_personal": "💡 CASUAL CLIENT COMMUNICATION",
            "friendly_logistics": "💡 CLIENT LOGISTICS & COORDINATION",
            "defense_preparation": "🎓 DEFENSE PRESENTATION & VIVA VOCE",
            "progress_and_reports": "📋 PROGRESS & PORTAL DOCUMENTATION",
            "greeting": "👋 CLIENT INITIAL GREETING",
            "client_burst_inquiry": "💡 CO-PILOT ACADEMIC INQUIRY"
        }
        card_banner = category_titles.get(inquiry_type, "💡 CO-PILOT ACADEMIC INQUIRY")

        header_lines = [
            f"╭─ <b>{card_banner}</b> ─────────────",
            f"│ 👤 <b>Client:</b> {client_link}  •  <code>#{sender_id}</code>",
            f"│ 📱 <b>Routing:</b> <code>{html.escape(account_label)}</code>"
        ]
        if engine:
            header_lines.append(f"│ ⚡ <b>AI Engine:</b> <code>{html.escape(engine)}</code>")
        header_lines.append(f"│ 🆔 <b>Draft ID:</b> <code>{draft_id}</code>")
        header_lines.append("╰──────────────────────────────────────────────────")

        body_parts = ["\n".join(header_lines)]

        # Client message in expandable blockquote
        clean_msg = client_message.strip()
        body_parts.append(
            f"\n💬 <b>INCOMING CLIENT MESSAGE</b>\n"
            f"<blockquote expandable>«{html.escape(clean_msg)}»</blockquote>"
        )

        # AI Epistemic Assessment & Thinking Process
        if thinking_points and isinstance(thinking_points, list) and len(thinking_points) > 0:
            engine_label = engine or "Gemini 3.8 Flash"
            intent_line = f"├ 🎯 <b>Academic Intent:</b> <i>{html.escape(admin_notes)}</i>\n" if admin_notes else ""
            t_bullets = []
            for pt in thinking_points:
                clean_pt = pt.strip()
                if clean_pt.startswith("•") or clean_pt.startswith("-"):
                    clean_pt = clean_pt.lstrip("•-").strip()
                if ":" in clean_pt:
                    k, v = clean_pt.split(":", 1)
                    t_bullets.append(f"• <b>{html.escape(k.strip())}:</b> {html.escape(v.strip())}")
                else:
                    t_bullets.append(f"• {html.escape(clean_pt)}")
            body_parts.append(
                f"\n🧠 <b>AI EPISTEMIC REASONING PROCESS</b> (<code>{html.escape(engine_label)}</code>)\n"
                f"{intent_line}"
                f"<blockquote expandable>{chr(10).join(t_bullets)}</blockquote>"
            )
        elif admin_notes:
            body_parts.append(
                f"\n🧠 <b>AI RESEARCH TWIN SYNTHESIS</b>\n"
                f"├ 🎯 <b>Academic Intent:</b> <i>{html.escape(admin_notes)}</i>\n"
                f"└ ⚡ <b>Status:</b> Ready for 1-click dispatch"
            )

        # Suggested Persian Draft in expandable blockquote
        body_parts.append(
            f"\n📝 <b>SUGGESTED SCHOLAR RESPONSE DRAFT</b>\n"
            f"<blockquote expandable>{safe_draft}</blockquote>"
        )

        # Modern action guidance
        body_parts.append(
            f"\n<i>Tap button below to dispatch, or tap to copy command:</i> <code>/send_msg_{draft_id}</code>"
        )

        alert_text = "\n".join(body_parts)

        # Modern 2026 2-Row Styled Action Keyboard (Green / Blue / Red)
        buttons = self.build_approval_keyboard(
            approve_label=f"🚀 Approve & Send ({draft_id})",
            approve_data=f"send_draft_{draft_id}",
            edit_label="✏️ Edit & Reply",
            edit_query=f"/send_msg_{draft_id} ",
            dismiss_label="🗑️ Dismiss",
            dismiss_data=f"ignore_draft_{draft_id}"
        )

        # Determine target topic
        if not topic_key:
            if inquiry_type == "scale_search":
                target_topic = "scales"
            elif inquiry_type in [
                "supervisor_defense_question",
                "supervisor_revision_feedback",
                "quarterly_progress_report"
            ]:
                target_topic = "supervisor_reviews"
            else:
                target_topic = "drafts"
        else:
            target_topic = topic_key

        await self.send_to_desk(
            alert_text,
            buttons=buttons,
            topic_key=target_topic,
            client_id=sender_id,
            client_name=sender_name,
            parse_mode="html"
        )
        print(f"[+] Posted Co-Pilot draft {draft_id} ({inquiry_type}) for {sender_name} to topic '{target_topic}'.")
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
                [Button.inline("🔄 Refresh Health", b"cmd_health", style="primary"),
                 Button.inline("📂 Project Catalog", b"cmd_projects", style="primary"),
                 Button.inline("📦 Deliverables", b"cmd_deliverables", style="primary")],
                [Button.inline("❌ Dismiss Notice", b"cmd_close", style="danger")]
            ]

        await self.send_to_desk(summary_text, buttons=buttons, topic_key="health", parse_mode="html")

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

            header_lines = [
                f"╭─ <b>{badge} FOLLOW-UP REMINDER</b> ─────────────",
                f"│ 👤 <b>Client:</b> {client_link}  •  <code>#{cid}</code>",
                f"│ 📁 <b>Project:</b> <code>{html.escape(clean_p)}</code>",
                f"│ ⏰ <b>Silence:</b> <code>{days} days</code>",
                f"│ 💡 <b>Diagnosis:</b> <i>{html.escape(reason)}</i>",
                f"│ 🆔 <b>Follow-Up ID:</b> <code>{fu_id}</code>",
                "╰──────────────────────────────────────────────────"
            ]

            card_text = (
                f"{chr(10).join(header_lines)}\n\n"
                f"📝 <b>SUGGESTED PERSIAN FOLLOW-UP DRAFT</b>\n"
                f"<blockquote expandable>{safe_draft}</blockquote>\n\n"
                f"<i>Tap button below to dispatch, or tap to copy command:</i> <code>/send_fu_{fu_id}</code>"
            )

            card_btns = self.build_approval_keyboard(
                approve_label=f"🚀 Send Follow-Up ({fu_id})",
                approve_data=f"send_fu_{fu_id}",
                edit_label="✏️ Edit & Reply",
                edit_query=f"/send_msg_{cid} ",
                dismiss_label="🗑️ Dismiss",
                dismiss_data=f"ignore_fu_{fu_id}"
            )

            await self.send_to_desk(card_text, buttons=card_btns, topic_key="health", client_id=cid, client_name=cname, parse_mode="html")
            print(f"[+] Posted Follow-Up reminder {fu_id} for {cname} to Academic Desk.")

        return audit_res

    async def post_morning_executive_briefing(self, trigger_event: Optional[Any] = None):
        """Compile and post the daily morning executive briefing card to Topic 116 (Health)."""
        data = self.morning_briefing.compile_briefing_data(pending_quotes=self.pending_quotes)
        card = self.morning_briefing.format_briefing_card(data)
        buttons = self.morning_briefing.build_briefing_keyboard(data)
        await self.send_to_desk(
            card,
            buttons=buttons,
            topic_key="health",
            parse_mode="html"
        )
        self.morning_briefing.mark_fired_today()
        print(f"[+] Posted Morning Executive Briefing to Topic 116 (Health).")
        if trigger_event:
            await trigger_event.reply("🌅 Morning executive briefing posted to Topic 116!", parse_mode="html")

    async def _morning_briefing_scheduler_loop(self):
        """Autonomous background loop: checks time every 60s and posts briefing at target morning time."""
        briefing_time = self.config.get("morning_briefing_time", "08:30")
        while True:
            try:
                if self.morning_briefing.should_fire_today(target_time_str=briefing_time):
                    print(f"[*] Firing scheduled morning briefing ({briefing_time}) to Topic 116...")
                    await self.post_morning_executive_briefing()
            except Exception as e:
                print(f"[-] Error in morning briefing scheduler loop: {e}")
            await asyncio.sleep(60)

    async def _periodic_catchup_sync_loop(self):
        """Autonomous background loop: periodically checks all client dialogs to catch offline messages and deltas."""
        # Initial wait so startup scan finishes first
        await asyncio.sleep(180)
        while True:
            try:
                print("[*] Running periodic offline catch-up sync across client dialogs...")
                await self.scan_and_process_unread_messages(limit_dialogs=40)
            except Exception as e:
                print(f"[-] Error in periodic catch-up sync loop: {e}")
            await asyncio.sleep(300)

    async def generate_and_post_math_defense(
        self,
        test_type: str = "ancova",
        supervisor_dilemma_fa: Optional[str] = None,
        client_name: str = "پژوهشگر",
        trigger_event: Optional[Any] = None
    ) -> None:
        """
        Generate a 2026 Box-drawing Viva Voce Defense Card with native Telegram mathematical formatting
        (APA 7th, LaTeX blocks, oral defense script) and post it to Topic 122 (Supervisor Reviews & Defense).
        """
        if not AcademicMathFormatter:
            if trigger_event:
                await trigger_event.reply("❌ AcademicMathFormatter module not available.", parse_mode="html")
            return

        self.math_counter += 1
        card_id = f"M{self.math_counter}"

        tt = (test_type or "ancova").lower().strip()

        if tt in ["ancova", "anova", "covariance"]:
            dilemma = supervisor_dilemma_fa or "چرا به جای ANOVA ساده یا تی‌تست، از تحلیل کوواریانس (ANCOVA) استفاده کردید؟"
            f_data = AcademicMathFormatter.format_ancova(18.42, 1, 58, 0.0002, 0.24, lang="fa")
        elif tt in ["sem", "cfa", "structural"]:
            dilemma = supervisor_dilemma_fa or "چرا شاخص کای‌اسکوئر (χ²) معنادار شده و چطور ادعا می‌کنید برازش مدل ساختاری مطلوب است؟"
            f_data = AcademicMathFormatter.format_sem_fit(342.15, 185, 0.0001, 0.048, 0.952, 0.941, 0.039, lang="fa")
        elif tt in ["regression", "reg", "linear"]:
            dilemma = supervisor_dilemma_fa or "چگونه مفروضات رگرسیون خطی و خطر هم‌خطی چندگانه (Multicollinearity) را در مدل مهار کردید؟"
            f_data = AcademicMathFormatter.format_regression(
                "متغیر ملاک",
                [
                    {"name": "پیش‌بین اول", "beta": 0.42, "t": 4.12, "p": 0.0002},
                    {"name": "پیش‌بین دوم", "beta": 0.31, "t": 3.05, "p": 0.003}
                ],
                0.38, 0.36, 24.18, 2, 147, 0.0001, lang="fa"
            )
        elif tt in ["gpower", "sample", "power", "samplesize"]:
            dilemma = supervisor_dilemma_fa or "حجم نمونه ۶۴ نفری بر چه مبنای فرمولی انتخاب شد و آیا خطر خطای نوع دوم وجود ندارد؟"
            f_data = AcademicMathFormatter.format_gpower("ancova", 64, 0.05, 0.85, 0.25, lang="fa")
        elif tt in ["ttest", "t_test", "t"]:
            dilemma = supervisor_dilemma_fa or "آیا تفاوت میانگین گروه‌ها در پیش‌آزمون و پس‌آزمون دارای اندازه اثر معنادار است؟"
            f_data = AcademicMathFormatter.format_ttest(3.15, 48, 0.003, 0.64, (0.24, 0.98), test_type="independent", lang="fa")
        elif tt in ["mediation", "process", "bootstrap"]:
            dilemma = supervisor_dilemma_fa or "چرا به جای آزمون سوبل (Sobel) از روش بوت‌استرپ در تحلیل میانجی‌گری استفاده شد؟"
            f_data = AcademicMathFormatter.format_mediation(0.185, 0.045, (0.095, 0.284), predictor="X", mediator="M", outcome="Y", lang="fa")
        else:
            dilemma = supervisor_dilemma_fa or f"دفاعیه روش‌شناختی پیرامون {test_type}"
            f_data = AcademicMathFormatter.format_ancova(18.42, 1, 58, 0.0002, 0.24, lang="fa")

        self.math_registry[card_id] = {
            "card_id": card_id,
            "test_type": tt,
            "formula_data": f_data,
            "dilemma": dilemma,
            "client_name": client_name,
            "created_at": datetime.now().isoformat()
        }

        card_html, raw_btns = AcademicMathFormatter.build_defense_card(f_data, dilemma, client_name=client_name, card_id=card_id)

        telegram_btns = None
        if Button is not None and raw_btns:
            telegram_btns = []
            for row in raw_btns:
                r_list = []
                for b in row:
                    style = "primary"
                    if "apa" in b["callback_data"]:
                        style = "success"
                    elif "latex" in b["callback_data"]:
                        style = "primary"
                    try:
                        r_list.append(Button.inline(b["text"], b["callback_data"].encode("utf-8"), style=style))
                    except Exception:
                        r_list.append(Button.inline(b["text"], b["callback_data"].encode("utf-8")))
                telegram_btns.append(r_list)

        await self.send_to_desk(
            card_html,
            buttons=telegram_btns,
            topic_key="supervisor_reviews",
            client_name=client_name,
            parse_mode="html"
        )
        if trigger_event:
            await trigger_event.reply(f"🎓 Mathematical defense card <code>{card_id}</code> ({html.escape(tt.upper())}) posted to Topic 122 (Supervisor Reviews & Defense)!", parse_mode="html")

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
                if not dlg.is_user or dlg.entity.is_self or dlg.entity.bot:
                    continue
                if dlg.id in [124911145, 6328062294, 777000]:
                    continue

                # Ignore excluded non-academic contacts
                if self.project_manager.is_ignored(dlg.name, dlg.id, getattr(dlg.entity, "username", None)):
                    continue

                # STRICT 30-DAY INACTIVITY GUARD:
                # Never sync or pull dialogs whose latest interaction is older than 30 days.
                # Old unread messages from months or years ago must remain dormant in archive.
                if dlg.date:
                    dlg_dt = dlg.date.replace(tzinfo=None)
                    if (datetime.now() - dlg_dt).days > 30:
                        continue

                needs_sync = False
                sync_reason = ""

                # Condition 1: Unread count > 0
                if dlg.unread_count > 0:
                    needs_sync = True
                    sync_reason = f"{dlg.unread_count} unread"
                else:
                    # Condition 2: Offline delta check (Telegram has newer messages than local disk)
                    existing_dir = self.project_manager.find_existing_project_by_client(
                        dlg.name, client_id=dlg.id, username=getattr(dlg.entity, "username", None)
                    )
                    if existing_dir:
                        local_last_date = self.project_manager.get_project_latest_message_date(existing_dir)
                        if dlg.date and local_last_date:
                            dlg_dt = dlg.date.replace(tzinfo=None)
                            # If Telegram dialog date is newer than local date by > 5 seconds
                            if (dlg_dt - local_last_date).total_seconds() > 5:
                                needs_sync = True
                                sync_reason = f"offline catch-up (Telegram: {dlg_dt.strftime('%m-%d %H:%M')} > Local: {local_last_date.strftime('%m-%d %H:%M')})"
                        elif dlg.date and not local_last_date:
                            needs_sync = True
                            sync_reason = "missing local chat history"
                    elif dlg.date:
                        dlg_dt = dlg.date.replace(tzinfo=None)
                        if (datetime.now() - dlg_dt).days <= 30:
                            needs_sync = True
                            sync_reason = "active dialog without local folder"

                if needs_sync:
                    unread_clients.append((acc_lbl, cl, dlg, sync_reason))

        if not unread_clients:
            print("[+] All client dialogs are up to date (no unread or offline delta messages).")
            if trigger_event:
                now_str = datetime.now().strftime("%H:%M:%S")
                await trigger_event.answer(f"✅ All client dialogs are up to date! (Checked at {now_str})", alert=True)
            else:
                await self.send_to_desk("✅ No unread or offline delta client messages found.", topic_key="health", parse_mode="html")
            return

        print(f"[!] Found {len(unread_clients)} client(s) with unread or offline delta messages.")
        summary_lines = [f"📬 <b>Client Messages Sync ({len(unread_clients)} clients):</b>\n"]

        for acc_lbl, cl, dlg, sync_reason in unread_clients:
            client_name = dlg.name
            unread_cnt = dlg.unread_count
            user_entity = dlg.entity
            username = getattr(user_entity, "username", None)
            print(f"    • [{acc_lbl}] {client_name} ({dlg.id}): {sync_reason}")

            # Automatically archive chat and download unread/offline files into Google Drive project folder
            try:
                archive_res = await self.project_manager.save_client_chat_and_files(
                    client=cl,
                    entity=dlg.entity,
                    client_name=client_name,
                    client_id=dlg.id,
                    username=username,
                    limit_messages=max(unread_cnt + 20, 60),
                    download_files=True
                )
                project_dir = archive_res["project_dir"]
            except Exception as e:
                print(f"    [-] Failed to archive project for {client_name}: {e}")
                project_paths = self.project_manager.provision_project(client_name, client_id=dlg.id, username=username)
                project_dir = project_paths["root"]

            latest_text = ""
            found_proposal = False

            # Check recent messages for proposal files or text
            scan_depth = max(unread_cnt, 10)
            async for msg in cl.iter_messages(dlg.entity, limit=min(scan_depth, 25)):
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
            dash_row = [Button.inline("🔄 Rescan Messages", b"cmd_unread", style="primary"),
                        Button.inline("📂 Project Catalog", b"cmd_projects", style="primary"),
                        Button.inline("📦 Deliverables", b"cmd_deliverables", style="primary")]
            row2 = []
            if has_web_btn:
                row2.append(Button.url("📱 Open Web Dashboard", webapp_url))
            row2.append(Button.inline("❌ Dismiss Notice", b"cmd_close", style="danger"))
            buttons = [dash_row, row2]

    @staticmethod
    def _is_casual_or_acknowledgment(text: str) -> bool:
        """Check if conversational text is purely casual greetings/thanks/reactions without inquiry."""
        if not text or not text.strip():
            return True
        clean = re.sub(r"[\s\d.,!?:؛،\-_()（）*#@\/\\+\=~`\"\'«»|]+", "", text).strip()
        if not clean:
            return True
        casual_exact = {
            "ممنون", "خیلی ممنون", "مرسی", "دمت گرم", "تشکر", "سپاس", "سلامت باشید",
            "خدا قوت", "خداقوت", "باشه", "اوکی", "ok", "چشم", "دست شما درد نکنه",
            "دستت درد نکنه", "قربونت", "فدات", "ممنونم", "بسیار عالی", "عالی", "خخخ",
            "سلامتی", "همچنین", "خواهش میکنم", "زنده باشی", "مبارک باشه", "ممنون دستت درد نکنه",
            "خوبم", "قربانت", "فدای شما", "سلام صابر", "سلامتی صابر", "تو چه خبر", "خوشحالم که تو هم امیدواری"
        }
        if clean in casual_exact:
            return True
        words = text.strip().split()
        if len(words) <= 4:
            if any(term in text for term in ["خیلی ممنون", "دمت گرم", "ممنونم ازت", "دستت درد نکنه", "دست شما درد نکنه", "قربانت", "فدات", "سپاسگزارم"]):
                return True
        return False

    async def _process_client_burst(self, burst_key: Tuple[str, int], delay: int = 40):
        """
        Processes an aggregated conversational burst after `delay` seconds of silence from a client.
        Combines fragmented messages and media into ONE high-signal Co-Pilot draft / alert card.
        """
        try:
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            return

        async with self.burst_lock:
            buf = self.burst_buffers.pop(burst_key, None)

        if not buf:
            return

        account_label = buf["account_label"]
        client_name = buf["client_name"]
        sender_id = buf["sender_id"]
        username = buf["username"]
        client_inst = buf["client_inst"]
        chat_id = buf["chat_id"]
        messages = buf["messages"]
        files = buf["files"]

        # Combine text messages chronologically
        text_parts = [m["text"].strip() for m in messages if m.get("text") and m["text"].strip()]
        combined_text = "\n".join(text_parts).strip()
        last_event = messages[-1]["event"]

        # Check if entirely casual / acknowledgment without any attached media
        if not files and self._is_casual_or_acknowledgment(combined_text):
            print(f"[*] Burst from {client_name} ({len(messages)} msgs) is casual acknowledgment. Recorded to transcript, skipping desk card.")
            return

        # Check for proposal file (.docx, .pdf, .txt)
        proposal_file = None
        for f in files:
            ext = os.path.splitext(f["name"])[1].lower()
            if ext in [".docx", ".pdf", ".txt"] and f.get("local_path"):
                proposal_file = f
                break

        has_proposal_text = (len(combined_text) > 80 and any(w in combined_text for w in ["عنوان", "فرضیه", "پروپوزال", "جامعه", "نمونه", "متغیر"]))

        if proposal_file:
            print(f"[+] Processing debounced proposal file: {proposal_file['name']} from {client_name}")
            raw_content = extract_text_from_file(proposal_file["local_path"])
            if combined_text:
                raw_content = f"{raw_content}\n\n[توضیحات مراجع:]\n{combined_text}"
            await self.handle_proposal_message(
                last_event, raw_content, client_name, file_name=proposal_file["name"], sender_id=sender_id, username=username, client_source=client_inst
            )
            return
        elif has_proposal_text:
            print(f"[+] Processing debounced proposal text from {client_name}")
            await self.handle_proposal_message(
                last_event, combined_text, client_name, sender_id=sender_id, username=username, client_source=client_inst
            )
            return

        # Check for scale query
        m_scale = re.search(r"^/scale\s+(.+)", combined_text, re.MULTILINE)
        is_scale_query = bool(m_scale) or (
            any(w in combined_text for w in ["پرسشنامه", "مقیاس", "آزمون"]) and len(combined_text.split()) <= 12
        )
        if is_scale_query:
            query_name = m_scale.group(1).strip() if m_scale else re.sub(
                r"(?:داری|دارید|رو\s*دارید|می‌خواستم|لطفاً|سلام|وقت\s*بخیر)", "", combined_text
            ).strip()
            first_name = client_name.split()[0] if client_name else "پژوهشگر"
            if questionnaire_resolver is not None:
                profile = questionnaire_resolver.get_scale_profile(query_name)
                if profile and profile.get("found_in_registry"):
                    p_name = profile.get("scale_persian_name") or profile.get("scale_name")
                    n_items = profile.get("total_items_count", "مشخص در شناسنامه")
                    subscales = profile.get("subscales", [])
                    sub_text = "، ".join(subscales[:3]) if subscales else "تک‌عاملی"
                    scale_info = (
                        f"سلام و احترام، وقت شما بخیر {first_name} گرامی.\n"
                        f"پرسشنامه «{p_name}» ({n_items} گویه) با خرده‌مقیاس‌های استاندارد ({sub_text}) و شیوه نمره‌گذاری در بانک جامع مقیاس‌ها موجود است.\n"
                        "در صورت نیاز بفرمایید تا مشخصات فنی و فایل ابزار برای استفاده در پژوهش خدمتتون ارسال شود."
                    )
                else:
                    scale_info = (
                        f"سلام و احترام، وقت شما بخیر {first_name} گرامی.\n"
                        f"در مورد مقیاس «{query_name}»، مشخصات روان‌سنجی آن در حال بررسی در آرشیو پژوهشی است و اطلاعات تکمیلی به زودی خدمتتون ارسال می‌شود."
                    )
            else:
                scale_info = (
                    f"سلام و احترام، وقت شما بخیر {first_name} گرامی.\n"
                    f"پیام شما در خصوص مقیاس «{query_name}» دریافت شد. به زودی اطلاعات تکمیلی بررسی و خدمتتون ارسال می‌گردد."
                )

            await self.create_and_post_draft(
                chat_id=chat_id,
                sender_name=client_name,
                sender_id=sender_id,
                username=username,
                inquiry_type="scale_search",
                client_message=combined_text,
                draft_reply=scale_info,
                client_source=client_inst,
                account_label=account_label,
                admin_notes=f"Psychometric scale resolution for {query_name}",
                engine="Psychometric Registry (4,880 Scales)",
                thinking_points=[
                    f"Methodology: Standardized psychological measurement instrument lookup for «{query_name}».",
                    "Epistemic Rule: Multi-factor construct validity and Iranian psychometric normative scoring.",
                    "Consulting Strategy: Direct extraction from Questionnaires.xlsx master database with 1-click delivery."
                ]
            )
            return

        # Check if burst contains a student voice note
        voice_file = None
        for f in files:
            if f.get("type") == "voice" and f.get("local_path") and os.path.exists(f["local_path"]):
                voice_file = f
                break

        voice_digest = None
        if voice_file and self.voice_transcriber:
            print(f"[*] Auto-transcribing voice note {voice_file['name']} from {client_name}...")
            voice_digest = self.voice_transcriber.transcribe_and_digest(
                audio_path=voice_file["local_path"],
                client_name=client_name,
                is_vip=self.topic_manager.is_vip_client(sender_id) if hasattr(self.topic_manager, "is_vip_client") else False,
                duration=voice_file.get("duration", 0)
            )

        if voice_digest:
            v_transcript = voice_digest.get("transcript_fa", "")
            if v_transcript:
                try:
                    self.project_manager.append_message_to_history(
                        client_name=client_name,
                        client_id=sender_id,
                        username=username,
                        msg_id=messages[-1]["id"] if messages else 0,
                        sender_label=client_name,
                        sender_tag="Client (Voice Transcription)",
                        text=f"[متن صوت:] {v_transcript}",
                        file_name=voice_file["name"],
                        media_type="voice",
                        duration=voice_file.get("duration", 0)
                    )
                except Exception as err:
                    print(f"[-] Error appending voice transcript: {err}")

            if v_transcript:
                combined_text = f"{combined_text}\n\n[متن صوت:] {v_transcript}".strip() if combined_text else f"[متن صوت:] {v_transcript}"

            inquiry_type = voice_digest.get("inquiry_type", "supervisor_defense_question")
            draft_reply = voice_digest.get("suggested_draft_fa", "")
            target_topic = voice_digest.get("topic_key", "supervisor_reviews")
            admin_notes = f"Voice Note ({voice_file.get('duration', 0)}s): {voice_digest.get('core_dilemma_fa', '')}"
            thinking_points = voice_digest.get("thinking_points_en", [])
            engine = voice_digest.get("audio_model", "Gemini Audio")

            self.draft_counter += 1
            draft_id = f"D{self.draft_counter}"

            self.pending_drafts[draft_id] = {
                "draft_id": draft_id,
                "chat_id": chat_id,
                "sender_id": sender_id,
                "sender_name": client_name,
                "username": username,
                "inquiry_type": inquiry_type,
                "client_message": combined_text,
                "draft_reply": draft_reply,
                "client_source": client_inst or self.client,
                "account_label": account_label,
                "thinking_points": thinking_points,
                "voice_digest": voice_digest,
                "created_at": datetime.now().isoformat()
            }
            self._save_pending_drafts()
            self.voice_registry[draft_id] = {
                "client_name": client_name,
                "voice_digest": voice_digest,
                "topic_key": target_topic,
            }

            client_link = format_client_mention_html(client_name, username=username, client_id=sender_id)
            card_html, _ = self.voice_transcriber.build_voice_card(
                voice_digest=voice_digest,
                client_name=client_name,
                client_link=client_link,
                sender_id=sender_id,
                draft_id=draft_id,
                account_label=account_label
            )

            telegram_btns = self.build_approval_keyboard(
                approve_label=f"🚀 Approve & Send ({draft_id})",
                approve_data=f"send_draft_{draft_id}",
                edit_label="✏️ Edit & Reply",
                edit_query=f"/send_msg_{draft_id} ",
                dismiss_label="🗑️ Dismiss",
                dismiss_data=f"ignore_draft_{draft_id}"
            )
            if telegram_btns and len(telegram_btns) >= 2 and Button is not None:
                telegram_btns[1].insert(0, Button.inline("📝 Full Transcript", f"voice_transcript_{draft_id}".encode("utf-8")))

            await self.send_to_desk(
                card_html,
                buttons=telegram_btns,
                topic_key=target_topic,
                client_id=sender_id,
                client_name=client_name,
                parse_mode="html"
            )
            print(f"[+] Posted Voice Note Digest card for {client_name} ({draft_id}) to Topic {target_topic}")
            return

        # Check if burst is a financial payment or remittance notification
        pay_keywords = ["واریز", "فیش", "کارت به کارت", "واریزی", "انتقال دادم", "مبلغ", "شماره پیگیری", "شماره ارجاع", "کد پیگیری", "پایا", "ساتنا", "پرداخت کردم"]
        has_pay_keyword = any(k in combined_text for k in pay_keywords)

        if has_pay_keyword:
            cand_amount = 0
            m_mil = re.search(r"(\d+(?:\.\d+)?)\s*(?:میلیون|ملیون)", combined_text)
            if m_mil:
                cand_amount = int(float(m_mil.group(1)) * 1000000)
            else:
                fa_to_en = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
                clean_t = combined_text.translate(fa_to_en)
                m_dig = re.findall(r"\b(\d{1,3}(?:[,\s]\d{3})+|\d{6,9})\b", clean_t)
                for d in m_dig:
                    val = int(re.sub(r"[,\s]", "", d))
                    if 100000 <= val <= 200000000:
                        cand_amount = val
                        break

            clean_t = combined_text.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))
            m_track = re.search(r"(?:پیگیری|ارجاع|رهگیری|کد|شماره)\s*[:\-\s]*(\d{5,12})", clean_t)
            tracking_code = m_track.group(1) if m_track else ""

            matched_pdir = self.project_manager.find_existing_project_by_client(client_name, client_id=sender_id)
            if matched_pdir:
                ledger_data = self.financial_ledger.load_ledger(matched_pdir)
                tot_c = ledger_data.get("total_contract_tomans", 0)
                tot_p = ledger_data.get("total_paid_tomans", 0)
                bal = ledger_data.get("balance_due_tomans", 0)
                settled_pct = ledger_data.get("settlement_pct", 0)

                self.payment_counter += 1
                pid = f"PAY{self.payment_counter}"
                self.pending_payments[pid] = {
                    "pid": pid,
                    "client_name": client_name,
                    "sender_id": sender_id,
                    "chat_id": chat_id,
                    "project_dir": matched_pdir,
                    "detected_amount": cand_amount,
                    "tracking_code": tracking_code,
                    "client_message": combined_text,
                    "client_source": client_inst or self.client,
                    "created_at": datetime.now().isoformat()
                }

                cand_str = format_toman(cand_amount) if cand_amount > 0 else "نیاز به تایید دستی"
                tot_c_str = format_toman(tot_c)
                tot_p_str = format_toman(tot_p)
                bal_str = format_toman(bal)
                client_link = format_client_mention_html(client_name, username=username, client_id=sender_id)

                pay_card = (
                    f"╭─ 💳 <b>NEW PAYMENT NOTIFICATION</b> ────────────────\n"
                    f"│ 👤 <b>Client:</b> {client_link}\n"
                    f"│ 💵 <b>Detected Amount:</b> <code>{cand_str}</code> تومان\n"
                    f"│ 🔢 <b>Tracking / Ref:</b> <code>{tracking_code or 'فاقد کد صریح'}</code>\n"
                    f"│ 📊 <b>Ledger State:</b> <code>{tot_p_str} / {tot_c_str}</code> ت (<b>{settled_pct}%</b>)\n"
                    f"│ ⏳ <b>Current Balance:</b> <code>{bal_str}</code> تومان\n"
                    f"╰──────────────────────────────────────────────────\n\n"
                    f"💬 <b>Client Message:</b>\n"
                    f"<blockquote expandable>«{html.escape(combined_text)}»</blockquote>"
                )

                pay_btns = [
                    [Button.inline(f"✅ Confirm & Record ({pid})", f"pay_confirm_{pid}".encode("utf-8"), style="success")],
                    [
                        Button.switch_inline("✏️ Custom /pay", f"/pay {client_name} {cand_amount or ''} {tracking_code} ", same_peer=True),
                        Button.inline("🧾 View Ledger", f"pay_ledger_{client_name.replace(' ', '_')[:20]}".encode("utf-8"), style="primary")
                    ],
                    [Button.inline("🗑️ Dismiss", f"pay_dismiss_{pid}".encode("utf-8"), style="danger")]
                ] if Button is not None else None

                await self.send_to_desk(
                    pay_card,
                    buttons=pay_btns,
                    topic_key="health",
                    client_id=sender_id,
                    client_name=client_name,
                    parse_mode="html"
                )
                print(f"[+] Detected payment notification from {client_name} ({pid}), posted to Topic health")

        # Prepare summary of media attachments if any
        files_summary_lines = []
        if files:
            for f in files:
                mtype = f["type"]
                fname = f["name"]
                icon = "🎤" if mtype == "voice" else ("📷" if mtype == "photo" else "📹" if mtype == "video_note" else "📎")
                dur_lbl = f" ({f['duration']}s)" if f.get("duration") else ""
                files_summary_lines.append(f"{icon} <code>{html.escape(fname)}</code>{dur_lbl}")

        files_summary = "\n".join(files_summary_lines)

        # AI-Powered Academic Semantic Analysis via Gemini 3.8 (with automatic fallback)
        is_vip = self.topic_manager.is_vip_client(sender_id) if hasattr(self.topic_manager, "is_vip_client") else False
        analysis = self.classifier.analyze_inquiry(
            client_name=client_name,
            combined_text=combined_text,
            attached_files=files,
            is_vip=is_vip
        )

        inquiry_type = analysis.get("inquiry_type", "client_burst_inquiry")
        draft_reply = analysis.get("draft_reply")
        target_topic = analysis.get("topic_key", "drafts")
        admin_notes = analysis.get("admin_notes")
        thinking_points = analysis.get("thinking_points", [])
        engine = analysis.get("engine")

        client_msg_display = combined_text
        if files_summary:
            burst_note = f"📁 <b>{len(files)} attachment(s):</b>\n{files_summary}"
            client_msg_display = f"{client_msg_display}\n\n{burst_note}" if client_msg_display else burst_note

        await self.create_and_post_draft(
            chat_id=chat_id,
            sender_name=client_name,
            sender_id=sender_id,
            username=username,
            inquiry_type=inquiry_type,
            client_message=client_msg_display,
            draft_reply=draft_reply,
            client_source=client_inst,
            account_label=account_label,
            topic_key=target_topic,
            admin_notes=admin_notes,
            engine=engine,
            thinking_points=thinking_points
        )

    async def start_listening(self, phone: Optional[str] = None, bot_token: Optional[str] = None, use_qr: bool = False):
        """Listen to real-time client DMs and Admin Desk commands."""
        me = await self.init_client(phone=phone, bot_token=bot_token, use_qr=use_qr)
        admin_chats = []
        if self.admin_desk_chat_id:
            admin_chats.append(self.admin_desk_chat_id)
        admin_chats.append("me" if not me.bot else self.admin_id)

        # Synchronize and ensure Forum Topics in Academic Desk
        if self.client and self.admin_desk_chat_id:
            try:
                vip_reg = self.project_manager.load_vip_registry()
                await self.topic_manager.sync_and_ensure_topics(
                    self.client,
                    self.admin_desk_chat_id,
                    vip_clients=vip_reg.get("vip_clients", [])
                )
                print(f"[+] Academic Desk Forum Topics active: {len(self.topic_manager.topics.get('functional', {}))} functional, {len(self.topic_manager.topics.get('vip', {}))} VIP.")
            except Exception as e:
                print(f"[-] Topic synchronization warning: {e}")

        # 1. Admin Desk (/send_Q101, /adjust_Q101_5000000, /ignore_Q101, /unread, /projects, /save_project, /sync_projects, /topics, /make_vip)
        @self.client.on(events.NewMessage(chats=admin_chats))
        async def admin_handler(event):
            txt = (event.message.message or "").strip()

            # Forum Topics status: /topics or /topic_status
            if txt in ["/topics", "/topic_status"]:
                summary = self.topic_manager.format_topics_summary()
                await event.reply(summary, parse_mode="html")
                return

            # Refresh & sync topics: /sync_topics
            if txt in ["/sync_topics", "/refresh_topics"]:
                await event.reply("🔄 Synchronizing forum topics with Academic Desk...", parse_mode="html")
                vip_reg = self.project_manager.load_vip_registry()
                await self.topic_manager.sync_and_ensure_topics(
                    self.client,
                    self.admin_desk_chat_id,
                    vip_clients=vip_reg.get("vip_clients", [])
                )
                summary = self.topic_manager.format_topics_summary()
                await event.reply(f"✅ <b>Topics successfully synchronized:</b>\n\n{summary}", parse_mode="html")
                return

            # Promote client to VIP and create dedicated forum topic: /make_vip <client_name or id>
            m_vip = re.match(r"^/make_vip(?:\s+(.+))?", txt)
            if m_vip:
                q = (m_vip.group(1) or "").strip()
                if not q:
                    await event.reply("⚠️ Usage: <code>/make_vip &lt;client_name or telegram_id&gt;</code>", parse_mode="html")
                    return
                matched_id = int(q) if q.isdigit() else None
                matched_name = q if not q.isdigit() else f"Client {q}"
                if not matched_id:
                    for p in self.project_manager.list_all_projects():
                        if q.lower() in (p.get("client_name") or "").lower() or q.lower() in (p.get("client_name_fa") or "").lower():
                            matched_id = p.get("client_id")
                            matched_name = p.get("client_name_fa") or p.get("client_name")
                            break
                if not matched_id:
                    await event.reply(f"❌ Could not find client matching <code>{html.escape(q)}</code> with a known Telegram ID.", parse_mode="html")
                    return

                self.project_manager.add_vip_client(client_name=matched_name, telegram_id=matched_id)
                t_id = await self.topic_manager.create_vip_topic(self.client, self.admin_desk_chat_id, matched_name, matched_id)
                await event.reply(
                    f"⭐ <b>VIP Client Configured!</b>\n"
                    f"• <b>Client:</b> {html.escape(matched_name)} (ID: <code>{matched_id}</code>)\n"
                    f"• <b>Dedicated Forum Topic ID:</b> <code>{t_id}</code>\n"
                    f"All future messages and draft cards for this client will route to their dedicated topic thread.",
                    parse_mode="html"
                )
                return

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
                        btn = [[Button.inline("📂 Project Catalog", b"cmd_projects", style="primary"),
                                Button.inline("🔄 Rescan Messages", b"cmd_unread", style="primary")]]
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

            # Triage inactive projects: /triage or /triage_run [days]
            m_triage = re.match(r"^/triage(?:_(run|execute))?(?:\s+(\d+))?", txt)
            if m_triage:
                is_run = bool(m_triage.group(1))
                days_arg = int(m_triage.group(2)) if m_triage.group(2) else 30
                mode_str = "اجرای قطعی جابجایی" if is_run else "پیش‌نمایش (Dry Run)"
                await event.reply(f"🧹 <b>در حال غربالگری پروژه‌های غیرفعال ({mode_str} — آستانه: {days_arg} روز)...</b>", parse_mode="html")
                report = self.project_manager.triage_inactive_projects(inactivity_days=days_arg, dry_run=not is_run)

                resp_lines = [
                    f"🧹 <b>گزارش مدیریت چرخه عمر پروژه‌ها ({mode_str})</b>\n",
                    f"⏱ <b>آستانه عدم فعالیت:</b> {days_arg} روز",
                    f"🟢 <b>پروژه‌های فعال نگه‌داشته‌شده:</b> {len(report['active_retained'])} مورد",
                    f"📦 <b>انتقال به پوشه معلق (Pending Works):</b> {len(report['moved_to_pending'])} مورد",
                    f"🏁 <b>انتقال به پوشه خاتمه‌یافته (Finished Works):</b> {len(report['moved_to_finished'])} مورد",
                    f"⭐ <b>پروژه‌های معاف/VIP:</b> {len(report['pinned_exempt'])} مورد\n"
                ]
                if report['moved_to_pending']:
                    resp_lines.append("<b>نمونه پروژه‌های انتقال‌یافته به Pending Works:</b>")
                    for p in report['moved_to_pending'][:10]:
                        resp_lines.append(f"• <code>{p['folder']}</code> ({p['days_inactive']} روز)")
                    if len(report['moved_to_pending']) > 10:
                        resp_lines.append(f"• <i>... و {len(report['moved_to_pending']) - 10} پروژه دیگر</i>")

                if not is_run and (report['moved_to_pending'] or report['moved_to_finished']):
                    resp_lines.append("\n💡 <i>برای اجرای قطعی جابجایی، دستور <code>/triage_run</code> را ارسال فرمایید.</i>")
                elif is_run:
                    resp_lines.append("\n✅ <b>پوشه My Work با موفقیت پاکسازی و خلوت گردید.</b>")

                await event.reply("\n".join(resp_lines), parse_mode="html")
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

            # Morning Executive Briefing: /briefing or /morning
            if re.match(r"^/(?:briefing|morning)\b", txt):
                await self.post_morning_executive_briefing(trigger_event=event)
                return

            # Mathematical formula & defense command: /math [test_type] [optional client or dilemma] or /formula
            m_math = re.match(r"^/(?:math|formula)(?:\s+([^\s]+))?(?:\s+(.+))?", txt)
            if m_math:
                t_type = (m_math.group(1) or "").strip()
                extra = (m_math.group(2) or "").strip()
                if not t_type:
                    help_msg = (
                        "📐 <b>Digital Saber — Native Mathematical Formula Engine</b>\n\n"
                        "Generates APA 7th statistical test formulations, LaTeX code blocks, and viva voce oral defense scripts.\n\n"
                        "📌 <b>Available Statistical Test Families:</b>\n"
                        "• <code>/math ancova</code> — ANCOVA pre-test covariate & effect size (η<sub>p</sub>²)\n"
                        "• <code>/math sem</code> — SEM/CFA fit indices (χ², RMSEA, CFI, TLI, SRMR)\n"
                        "• <code>/math regression</code> — Multiple regression model (<i>R</i>², <i>F</i>, β, <i>t</i>)\n"
                        "• <code>/math gpower</code> — G*Power 3.1 sample size & non-centrality (λ = <i>f</i>² × <i>N</i>)\n"
                        "• <code>/math ttest</code> — Student's <i>t</i>-test & Cohen's <i>d</i>\n"
                        "• <code>/math mediation</code> — Hayes PROCESS 5,000 bootstrap BCa CI\n\n"
                        "👉 <i>Example:</i> <code>/math ancova چرا از آنکووا استفاده کردی؟</code>"
                    )
                    await event.reply(help_msg, parse_mode="html")
                    return

                await self.generate_and_post_math_defense(test_type=t_type, supervisor_dilemma_fa=extra or None, trigger_event=event)
                return

            # Voice transcription command: /transcribe [client_query] or /voice
            m_trans = re.match(r"^/(?:transcribe|voice)(?:\s+(.+))?", txt)
            if m_trans:
                c_query = (m_trans.group(1) or "").strip()
                if not c_query:
                    await event.reply(
                        "🎙️ <b>Digital Saber — Persian Voice Note Transcriber</b>\n\n"
                        "Transcribe and analyze any client voice note from Google Drive.\n"
                        "Usage: <code>/transcribe &lt;client_name&gt;</code>\n"
                        "Example: <code>/transcribe Zahra Jalali</code>",
                        parse_mode="html"
                    )
                    return
                clean_q = c_query.lstrip("@").lower()
                matched_pdir = self.project_manager.find_existing_project_by_client(clean_q)
                if not matched_pdir and clean_q.isdigit():
                    matched_pdir = self.project_manager.find_existing_project_by_client("Client", client_id=int(clean_q))
                if not matched_pdir:
                    projs = self.project_manager.list_all_projects()
                    for p in projs:
                        if clean_q in (p.get("client_name") or "").lower() or \
                           clean_q in (p.get("client_name_fa") or "").lower() or \
                           clean_q in (p.get("folder_name") or "").lower():
                            matched_pdir = p["folder_path"]
                            break
                if not matched_pdir:
                    await event.reply(f"❌ No project folder found for <code>{html.escape(c_query)}</code>.", parse_mode="html")
                    return

                raw_dir = os.path.join(matched_pdir, "01_raw_inputs")
                v_files = []
                if os.path.exists(raw_dir):
                    for fn in os.listdir(raw_dir):
                        if fn.lower().endswith((".oga", ".ogg", ".mp3", ".wav")):
                            f_path = os.path.join(raw_dir, fn)
                            v_files.append((f_path, os.path.getmtime(f_path)))
                v_files.sort(key=lambda x: x[1], reverse=True)

                if not v_files:
                    await event.reply(f"🎙️ No voice notes found in <code>01_raw_inputs/</code> for {os.path.basename(matched_pdir)}.", parse_mode="html")
                    return

                target_voice = v_files[0][0]
                await event.reply(f"⏳ Transcribing latest voice note (<code>{os.path.basename(target_voice)}</code>) via Gemini Audio...", parse_mode="html")

                cname = os.path.basename(matched_pdir)
                vd = self.voice_transcriber.transcribe_and_digest(target_voice, client_name=cname)
                if vd:
                    self.draft_counter += 1
                    draft_id = f"D{self.draft_counter}"
                    self.pending_drafts[draft_id] = {
                        "draft_id": draft_id,
                        "chat_id": event.chat_id,
                        "sender_id": 0,
                        "sender_name": cname,
                        "username": None,
                        "inquiry_type": vd.get("inquiry_type", "supervisor_defense_question"),
                        "client_message": vd.get("transcript_fa", ""),
                        "draft_reply": vd.get("suggested_draft_fa", ""),
                        "client_source": self.client,
                        "account_label": "Manual /transcribe",
                        "thinking_points": vd.get("thinking_points_en", []),
                        "voice_digest": vd,
                        "created_at": datetime.now().isoformat()
                    }
                    self._save_pending_drafts()
                    self.voice_registry[draft_id] = {
                        "client_name": cname,
                        "voice_digest": vd,
                        "topic_key": "drafts",
                    }
                    card_html, _ = self.voice_transcriber.build_voice_card(
                        voice_digest=vd,
                        client_name=cname,
                        client_link=cname,
                        sender_id=0,
                        draft_id=draft_id,
                        account_label="Manual Inspection"
                    )
                    btns = self.build_approval_keyboard(
                        approve_label=f"🚀 Approve & Send ({draft_id})",
                        approve_data=f"send_draft_{draft_id}",
                        edit_label="✏️ Edit & Reply",
                        edit_query=f"/send_msg_{draft_id} ",
                        dismiss_label="🗑️ Dismiss",
                        dismiss_data=f"ignore_draft_{draft_id}"
                    )
                    if btns and len(btns) >= 2 and Button is not None:
                        btns[1].insert(0, Button.inline("📝 Full Transcript", f"voice_transcript_{draft_id}".encode("utf-8")))

                    t_key = vd.get("topic_key", "supervisor_reviews")
                    await self.send_to_desk(card_html, buttons=btns, topic_key=t_key, parse_mode="html")
                    await event.reply(f"✅ Voice note digest card ({draft_id}) posted to Topic {t_key}!", parse_mode="html")
                else:
                    await event.reply(f"❌ Failed to transcribe voice note for {cname}.", parse_mode="html")
                return

            # Milestone & Progress tracker: /milestone [client_query] or /milestones or /progress
            m_ms = re.match(r"^/(?:milestone|milestones|progress)(?:\s+(.+))?", txt)
            if m_ms:
                c_query = (m_ms.group(1) or "").strip()
                if not c_query:
                    projs = self.project_manager.list_all_projects()
                    if not projs:
                        await event.reply("📋 No active projects found in Google Drive.", parse_mode="html")
                        return
                    lines = [f"📋 <b>Active Research Projects & Milestones ({len(projs)} clients):</b>\n"]
                    for p in projs[:12]:
                        p_dir = p["folder_path"]
                        state = self.milestone_tracker.evaluate_milestones(p_dir)
                        cname = state.get("client_name") or p.get("folder_name")
                        bar = state["progress_bar"]
                        pct = state["progress_pct"]
                        scope_badge = state["scope_badge"]
                        lines.append(
                            f"• <b>{html.escape(cname)}</b>: <code>[{bar}] {pct}%</code> ({scope_badge})\n"
                            f"  👉 View card: <code>/milestone {html.escape(os.path.basename(p_dir))}</code>"
                        )
                    if len(projs) > 12:
                        lines.append(f"\n<i>... and {len(projs) - 12} more projects. Use <code>/milestone &lt;client&gt;</code> to inspect.</i>")
                    await event.reply("\n".join(lines), parse_mode="html")
                    return
                else:
                    clean_q = c_query.lstrip("@").lower()
                    matched_pdir = self.project_manager.find_existing_project_by_client(clean_q)
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
                                break
                    if not matched_pdir:
                        await event.reply(f"❌ No project folder found for client <code>{html.escape(c_query)}</code>.", parse_mode="html")
                        return

                    state = self.milestone_tracker.evaluate_milestones(matched_pdir)
                    card = self.milestone_tracker.format_milestone_card(state)
                    btns = self.build_milestone_keyboard(matched_pdir, state)
                    await self.send_to_desk(
                        card,
                        buttons=btns,
                        topic_key="health",
                        client_id=state.get("client_id"),
                        client_name=state.get("client_name"),
                        parse_mode="html"
                    )
                    await event.reply("📋 Milestone card posted to Desk!", parse_mode="html")
                    return

            # Financial commands: /pay, /ledger, /invoice, /contract, /receipt, /finance
            m_pay = re.match(r"^/pay(?:\s+([^\s]+))?(?:\s+([^\s]+))?(?:\s+([^\s]+))?(?:\s+(.+))?", txt)
            if m_pay:
                c_query = (m_pay.group(1) or "").strip()
                amt_str = (m_pay.group(2) or "").strip()
                code_str = (m_pay.group(3) or "").strip()
                notes_str = (m_pay.group(4) or "").strip()

                if not c_query or not amt_str:
                    await event.reply(
                        "💳 <b>Digital Saber — Record Payment</b>\n\n"
                        "Usage: <code>/pay &lt;client_name&gt; &lt;amount_tomans&gt; [tracking_code] [notes]</code>\n"
                        "Example: <code>/pay Zahra 4000000 482910 قسط_اول</code>",
                        parse_mode="html"
                    )
                    return

                clean_q = c_query.lstrip("@").lower()
                matched_pdir = self.project_manager.find_existing_project_by_client(clean_q)
                if not matched_pdir and clean_q.isdigit():
                    matched_pdir = self.project_manager.find_existing_project_by_client("Client", client_id=int(clean_q))
                if not matched_pdir:
                    projs = self.project_manager.list_all_projects()
                    for p in projs:
                        if clean_q in (p.get("client_name") or "").lower() or \
                           clean_q in (p.get("client_name_fa") or "").lower() or \
                           clean_q in (p.get("folder_name") or "").lower():
                            matched_pdir = p["folder_path"]
                            break
                if not matched_pdir:
                    await event.reply(f"❌ No project folder found for <code>{html.escape(c_query)}</code>.", parse_mode="html")
                    return

                fa_to_en = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
                clean_amt = re.sub(r"[,\s]", "", amt_str.translate(fa_to_en))
                if not clean_amt.isdigit():
                    await event.reply("❌ Invalid amount. Please enter a valid number in Tomans.", parse_mode="html")
                    return
                amt_int = int(clean_amt)

                tx = self.financial_ledger.record_transaction(
                    matched_pdir,
                    amount_tomans=amt_int,
                    tracking_code=code_str,
                    notes=notes_str
                )
                rec_card = self.financial_ledger.format_receipt_card(tx, matched_pdir)
                cname = os.path.basename(matched_pdir)
                clean_cname = cname.replace(" ", "_")[:20]

                rec_btns = [
                    [Button.inline("🚀 Send Receipt to Client", f"pay_sendrec_{tx['receipt_id']}_{clean_cname}".encode("utf-8"), style="success")],
                    [Button.inline("💳 View Full Ledger", f"pay_ledger_{clean_cname}".encode("utf-8"), style="primary")]
                ] if Button is not None else None

                await self.send_to_desk(rec_card, buttons=rec_btns, topic_key="health", parse_mode="html")
                await event.reply(f"✅ Payment of {format_toman(amt_int)} Tomans recorded ({tx['receipt_id']})!", parse_mode="html")
                return

            m_ledger = re.match(r"^/(?:ledger|invoice)(?:\s+(.+))?", txt)
            if m_ledger:
                c_query = (m_ledger.group(1) or "").strip()
                if not c_query:
                    await event.reply(
                        "📊 <b>Client Financial Ledger</b>\n\n"
                        "Usage: <code>/ledger &lt;client_name&gt;</code>\n"
                        "Example: <code>/ledger Zahra Jalali</code>",
                        parse_mode="html"
                    )
                    return
                clean_q = c_query.lstrip("@").lower()
                matched_pdir = self.project_manager.find_existing_project_by_client(clean_q)
                if not matched_pdir and clean_q.isdigit():
                    matched_pdir = self.project_manager.find_existing_project_by_client("Client", client_id=int(clean_q))
                if not matched_pdir:
                    projs = self.project_manager.list_all_projects()
                    for p in projs:
                        if clean_q in (p.get("client_name") or "").lower() or \
                           clean_q in (p.get("client_name_fa") or "").lower() or \
                           clean_q in (p.get("folder_name") or "").lower():
                            matched_pdir = p["folder_path"]
                            break
                if not matched_pdir:
                    await event.reply(f"❌ No project folder found for <code>{html.escape(c_query)}</code>.", parse_mode="html")
                    return

                l_card, l_btns = self.financial_ledger.format_ledger_card(matched_pdir)
                await self.send_to_desk(l_card, buttons=l_btns, topic_key="health", parse_mode="html")
                await event.reply("💳 Financial ledger card posted to Topic Health!", parse_mode="html")
                return

            m_contract = re.match(r"^/contract(?:\s+([^\s]+))?(?:\s+([^\s]+))?(?:\s+(.+))?", txt)
            if m_contract:
                c_query = (m_contract.group(1) or "").strip()
                tot_str = (m_contract.group(2) or "").strip()
                scope_str = (m_contract.group(3) or "full_thesis").strip()

                if not c_query or not tot_str:
                    await event.reply(
                        "📝 <b>Initialize / Update Contract</b>\n\n"
                        "Usage: <code>/contract &lt;client_name&gt; &lt;total_tomans&gt; [scope]</code>\n"
                        "Example: <code>/contract Zahra 12000000 chapter4_only</code>",
                        parse_mode="html"
                    )
                    return

                clean_q = c_query.lstrip("@").lower()
                matched_pdir = self.project_manager.find_existing_project_by_client(clean_q)
                if not matched_pdir and clean_q.isdigit():
                    matched_pdir = self.project_manager.find_existing_project_by_client("Client", client_id=int(clean_q))
                if not matched_pdir:
                    projs = self.project_manager.list_all_projects()
                    for p in projs:
                        if clean_q in (p.get("client_name") or "").lower() or \
                           clean_q in (p.get("client_name_fa") or "").lower() or \
                           clean_q in (p.get("folder_name") or "").lower():
                            matched_pdir = p["folder_path"]
                            break
                if not matched_pdir:
                    await event.reply(f"❌ No project folder found for <code>{html.escape(c_query)}</code>.", parse_mode="html")
                    return

                fa_to_en = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
                clean_tot = re.sub(r"[,\s]", "", tot_str.translate(fa_to_en))
                if not clean_tot.isdigit():
                    await event.reply("❌ Invalid contract total amount.", parse_mode="html")
                    return
                tot_int = int(clean_tot)

                cname = os.path.basename(matched_pdir)
                self.financial_ledger.initialize_contract(
                    matched_pdir,
                    total_tomans=tot_int,
                    client_name=cname,
                    scope=scope_str,
                    installment_count=3
                )
                l_card, l_btns = self.financial_ledger.format_ledger_card(matched_pdir)
                await self.send_to_desk(l_card, buttons=l_btns, topic_key="health", parse_mode="html")
                await event.reply(f"✅ Contract initialized for {cname} ({format_toman(tot_int)} Toman)!", parse_mode="html")
                return

            m_receipt = re.match(r"^/receipt(?:\s+(.+))?", txt)
            if m_receipt:
                c_query = (m_receipt.group(1) or "").strip()
                if not c_query:
                    await event.reply("Usage: <code>/receipt &lt;client_name&gt;</code>", parse_mode="html")
                    return
                clean_q = c_query.lstrip("@").lower()
                matched_pdir = self.project_manager.find_existing_project_by_client(clean_q)
                if not matched_pdir:
                    projs = self.project_manager.list_all_projects()
                    for p in projs:
                        if clean_q in (p.get("client_name") or "").lower() or clean_q in (p.get("folder_name") or "").lower():
                            matched_pdir = p["folder_path"]
                            break
                if not matched_pdir:
                    await event.reply(f"❌ No project folder found for <code>{html.escape(c_query)}</code>.", parse_mode="html")
                    return

                ld = self.financial_ledger.load_ledger(matched_pdir)
                txs = ld.get("transactions", [])
                if not txs:
                    await event.reply("❌ No payment transactions recorded yet for this client.", parse_mode="html")
                    return

                rec_card = self.financial_ledger.format_receipt_card(txs[-1], matched_pdir)
                cname = os.path.basename(matched_pdir)
                clean_cname = cname.replace(" ", "_")[:20]
                rec_btns = [
                    [Button.inline("🚀 Send Receipt to Client", f"pay_sendrec_{txs[-1]['receipt_id']}_{clean_cname}".encode("utf-8"), style="success")],
                    [Button.inline("💳 View Full Ledger", f"pay_ledger_{clean_cname}".encode("utf-8"), style="primary")]
                ] if Button is not None else None
                await self.send_to_desk(rec_card, buttons=rec_btns, topic_key="health", parse_mode="html")
                await event.reply("🧾 Official receipt card posted to Topic Health!", parse_mode="html")
                return

            if txt.strip() in ["/finance", "/fin", "/financials"]:
                f_card = self.financial_ledger.format_global_summary_card()
                btns = [[Button.inline("🔄 Refresh Financials", b"cmd_finance", style="primary")]] if Button is not None else None
                await self.send_to_desk(f_card, buttons=btns, topic_key="health", parse_mode="html")
                await event.reply("💰 Executive financial portfolio card posted to Topic Health!", parse_mode="html")
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
                card_text, card_btns, caption_text = self.deliverable_dispatcher.format_dispatch_card(
                    del_id=del_id,
                    client_name=cname,
                    username=uname,
                    telegram_id=cid,
                    project_dir=matched_pdir,
                    chosen_file=chosen_file,
                    all_files=d_files if "d_files" in locals() else [chosen_file]
                )

                self.pending_deliverables[del_id] = {
                    "del_id": del_id,
                    "client_name": cname,
                    "telegram_id": cid,
                    "username": uname,
                    "folder_path": matched_pdir,
                    "file_path": chosen_file["file_path"],
                    "filename": chosen_file["filename"],
                    "size_str": chosen_file.get("size_str", "N/A"),
                    "caption": caption_text,
                    "all_files": d_files if "d_files" in locals() else [chosen_file],
                    "created_at": datetime.now().isoformat()
                }

                await self.send_to_desk(card_text, buttons=card_btns, topic_key="health", client_name=cname, parse_mode="html")
                print(f"[+] Prepared Deliverable dispatch card {del_id} for {cname}: {chosen_file['filename']}")
                return

            # Bundle all deliverables into .zip: /bundle <client_query>
            m_bundle = re.match(r"^/bundle(?:\s+(.+))?", txt)
            if m_bundle:
                c_query = (m_bundle.group(1) or "").strip()
                if not c_query:
                    await event.reply("📦 <b>Bundle Deliverables</b>\nUsage: <code>/bundle &lt;client_name&gt;</code>\nExample: <code>/bundle Zahra Jalali</code>", parse_mode="html")
                    return
                clean_q = c_query.lstrip("@").lower()
                matched_pdir = self.project_manager.find_existing_project_by_client(clean_q)
                if not matched_pdir:
                    projs = self.project_manager.list_all_projects()
                    for p in projs:
                        if clean_q in (p.get("client_name") or "").lower() or clean_q in (p.get("folder_name") or "").lower():
                            matched_pdir = p["folder_path"]
                            break
                if not matched_pdir:
                    await event.reply(f"❌ No project folder found for <code>{html.escape(c_query)}</code>.", parse_mode="html")
                    return

                d_files = self.project_manager.list_project_deliverables(matched_pdir)
                if not d_files:
                    await event.reply("📦 <code>03_deliverables/</code> is empty for this project.", parse_mode="html")
                    return

                file_paths = [f["file_path"] for f in d_files if not f["file_path"].endswith(".zip")]
                if not file_paths:
                    await event.reply("❌ No uncompressed files found to bundle.", parse_mode="html")
                    return

                zip_path = self.deliverable_dispatcher.bundle_deliverables_zip(matched_pdir, file_paths)
                z_size = os.path.getsize(zip_path)
                z_size_str = f"{z_size / (1024*1024):.1f} MB" if z_size > 1024*1024 else f"{z_size / 1024:.1f} KB"
                z_file_info = {
                    "filename": os.path.basename(zip_path),
                    "file_path": zip_path,
                    "size_str": z_size_str
                }

                self.deliverable_counter += 1
                del_id = f"DEL{self.deliverable_counter}"
                cname = os.path.basename(matched_pdir)
                card_text, card_btns, caption_text = self.deliverable_dispatcher.format_dispatch_card(
                    del_id=del_id,
                    client_name=cname,
                    username=None,
                    telegram_id=None,
                    project_dir=matched_pdir,
                    chosen_file=z_file_info,
                    all_files=[z_file_info]
                )

                self.pending_deliverables[del_id] = {
                    "del_id": del_id,
                    "client_name": cname,
                    "folder_path": matched_pdir,
                    "file_path": zip_path,
                    "filename": os.path.basename(zip_path),
                    "size_str": z_size_str,
                    "caption": caption_text,
                    "created_at": datetime.now().isoformat()
                }

                await self.send_to_desk(card_text, buttons=card_btns, topic_key="health", parse_mode="html")
                await event.reply(f"📦 Zipped {len(file_paths)} files into <code>{os.path.basename(zip_path)}</code> ({z_size_str}) and staged dispatch card ({del_id})!", parse_mode="html")
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
                now_str = datetime.now().strftime("%H:%M")

                if data == "noop":
                    await event.answer("ℹ️ This item has already been dispatched.", alert=False)
                    return

                if data.startswith("send_draft_"):
                    did = data.split("send_draft_")[1]
                    if did in self.pending_drafts:
                        entry = self.pending_drafts[did]
                        target_client = entry.get("client_source")
                        if not target_client:
                            if "Second Account" in entry.get("account_label", "") and self.client2:
                                target_client = self.client2
                            else:
                                target_client = self.client
                        await target_client.send_message(entry["chat_id"], entry["draft_reply"])
                        await event.answer(f"🚀 Response {did} dispatched to client!", alert=False)
                        try:
                            done_badge = [[Button.inline(f"✅ Dispatched ({did}) at {now_str}", b"noop", style="success")]] if Button is not None else None
                            await event.edit(
                                f"{event.message.text}\n\n✅ <b>Response was approved and dispatched to client at {now_str} via {entry.get('account_label', 'Personal Account')}.</b>",
                                buttons=done_badge,
                                parse_mode="html"
                            )
                        except Exception:
                            pass
                        del self.pending_drafts[did]
                        self._save_pending_drafts()
                    else:
                        await event.answer(f"❌ Draft ID {did} expired or not found.", alert=True)
                elif data.startswith("ignore_draft_"):
                    did = data.split("ignore_draft_")[1]
                    if did in self.pending_drafts:
                        cname = self.pending_drafts[did].get("sender_name", "Client")
                        del self.pending_drafts[did]
                        self._save_pending_drafts()
                        await event.answer("🗑️ Draft dismissed.", alert=False)
                        try:
                            tombstone = (
                                f"╭─ 🗑️ <b>DRAFT DISMISSED</b> ─────────────────────────\n"
                                f"│ 🆔 <b>Draft ID:</b> <code>{did}</code>  •  <code>{now_str}</code>\n"
                                f"│ 👤 <b>Client:</b> {html.escape(cname)}\n"
                                f"╰──────────────────────────────────────────────────"
                            )
                            await event.edit(tombstone, buttons=None, parse_mode="html")
                        except Exception:
                            pass
                    else:
                        await event.answer(f"❌ Draft ID {did} not found.", alert=True)
                elif data.startswith("voice_transcript_"):
                    did = data.split("voice_transcript_")[1]
                    entry = None
                    if did in self.voice_registry:
                        entry = self.voice_registry[did]
                    elif did in self.pending_drafts and "voice_digest" in self.pending_drafts[did]:
                        entry = {
                            "client_name": self.pending_drafts[did].get("sender_name", "Client"),
                            "voice_digest": self.pending_drafts[did]["voice_digest"],
                            "topic_key": self.pending_drafts[did].get("topic_key", "drafts"),
                        }
                    if entry and "voice_digest" in entry:
                        vd = entry["voice_digest"]
                        transcript = vd.get("transcript_fa", "")
                        cname = entry.get("client_name", "Client")
                        await event.answer("📝 Full transcript retrieved!", alert=False)
                        msg = (
                            f"📝 <b>Persian Voice Note Transcription</b>\n"
                            f"🆔 <code>{did}</code>  •  👤 <b>{html.escape(cname)}</b>\n\n"
                            f"<blockquote expandable>«{html.escape(transcript)}»</blockquote>"
                        )
                        t_key = entry.get("topic_key", "drafts")
                        await self.send_to_desk(msg, topic_key=t_key, parse_mode="html")
                    else:
                        await event.answer(f"❌ Voice transcript for {did} not found.", alert=True)
                elif data.startswith("send_fu_"):
                    fuid = data.split("send_fu_")[1]
                    if fuid in self.pending_followups:
                        entry = self.pending_followups[fuid]
                        target_dest = entry.get("telegram_id") or entry.get("username") or entry.get("client_name")
                        try:
                            await self.client.send_message(target_dest, entry["draft_reply"])
                            if entry.get("folder_path"):
                                self.project_manager.record_followup_dispatched(entry["folder_path"], entry["followup_type"], entry["draft_reply"])
                            await event.answer(f"🚀 Follow-up {fuid} dispatched to {entry['client_name']}!", alert=False)
                            try:
                                done_badge = [[Button.inline(f"✅ Dispatched ({fuid}) at {now_str}", b"noop", style="success")]] if Button is not None else None
                                await event.edit(
                                    f"{event.message.text}\n\n✅ <b>Follow-up reminder dispatched to client at {now_str} via Saber's personal account.</b>",
                                    buttons=done_badge,
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
                        cname = self.pending_followups[fuid].get("client_name", "Client")
                        del self.pending_followups[fuid]
                        await event.answer("🗑️ Follow-up reminder dismissed.", alert=False)
                        try:
                            tombstone = (
                                f"╭─ 🗑️ <b>FOLLOW-UP DISMISSED</b> ─────────────────────\n"
                                f"│ 🆔 <b>Follow-Up ID:</b> <code>{fuid}</code>  •  <code>{now_str}</code>\n"
                                f"│ 👤 <b>Client:</b> {html.escape(cname)}\n"
                                f"╰──────────────────────────────────────────────────"
                            )
                            await event.edit(tombstone, buttons=None, parse_mode="html")
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
                                try:
                                    self.milestone_tracker.advance_stage(entry["folder_path"])
                                except Exception:
                                    pass
                            await event.answer(f"🚀 Deliverable {entry['filename']} dispatched to {entry['client_name']}!", alert=False)
                            try:
                                done_badge = [[Button.inline(f"✅ Delivered ({del_id}) at {now_str}", b"noop", style="success")]] if Button is not None else None
                                await event.edit(
                                    f"{event.message.text}\n\n✅ <b>Deliverable file dispatched to client at {now_str} via Saber's personal account.</b>",
                                    buttons=done_badge,
                                    parse_mode="html"
                                )
                            except Exception:
                                pass
                            del self.pending_deliverables[del_id]
                        except Exception as e:
                            await event.answer(f"❌ Send failed: {e}", alert=True)
                    else:
                        await event.answer(f"❌ Deliverable ID {del_id} expired or not found.", alert=True)
                elif data.startswith("bundle_del_"):
                    del_id = data.split("bundle_del_")[1]
                    if del_id in self.pending_deliverables:
                        entry = self.pending_deliverables[del_id]
                        folder_p = entry.get("folder_path")
                        all_f = entry.get("all_files", [])
                        if not all_f and folder_p:
                            all_f = self.project_manager.list_project_deliverables(folder_p)

                        file_paths = [f["file_path"] for f in all_f if not f["file_path"].endswith(".zip")]
                        if not file_paths:
                            await event.answer("❌ No uncompressed files to bundle!", alert=True)
                            return

                        zip_path = self.deliverable_dispatcher.bundle_deliverables_zip(folder_p, file_paths)
                        target_dest = entry.get("telegram_id") or entry.get("username") or entry.get("client_name")
                        target_client = entry.get("client_source") or self.client

                        b_info = {"type_code": "bundled_package", "filename": os.path.basename(zip_path)}
                        b_caption = self.deliverable_dispatcher.generate_delivery_manifest_caption(entry["client_name"], b_info)

                        try:
                            try:
                                ent = await target_client.get_entity(target_dest)
                            except Exception:
                                ent = target_dest
                            await target_client.send_file(ent, file=zip_path, caption=b_caption)
                            if folder_p:
                                self.project_manager.record_deliverable_dispatched(folder_p, os.path.basename(zip_path), entry["client_name"])
                                try:
                                    self.milestone_tracker.advance_stage(folder_p)
                                except Exception:
                                    pass
                            await event.answer(f"📦 Bundled package dispatched to {entry['client_name']}!", alert=False)
                            try:
                                done_badge = [[Button.inline(f"✅ Bundled Package Sent at {now_str}", b"noop", style="success")]] if Button is not None else None
                                await event.edit(
                                    f"{event.message.text}\n\n✅ <b>Bundled deliverables package ({len(file_paths)} files) was zipped and dispatched to client at {now_str}.</b>",
                                    buttons=done_badge,
                                    parse_mode="html"
                                )
                            except Exception:
                                pass
                            del self.pending_deliverables[del_id]
                        except Exception as e:
                            await event.answer(f"❌ Send failed: {e}", alert=True)
                    else:
                        await event.answer(f"❌ Deliverable ID {del_id} expired.", alert=True)
                elif data.startswith("ignore_del_"):
                    del_id = data.split("ignore_del_")[1]
                    if del_id in self.pending_deliverables:
                        cname = self.pending_deliverables[del_id].get("client_name", "Client")
                        del self.pending_deliverables[del_id]
                        await event.answer("🗑️ Deliverable draft dismissed.", alert=False)
                        try:
                            tombstone = (
                                f"╭─ 🗑️ <b>DELIVERABLE DISMISSED</b> ───────────────────\n"
                                f"│ 🆔 <b>Deliverable ID:</b> <code>{del_id}</code>  •  <code>{now_str}</code>\n"
                                f"│ 👤 <b>Client:</b> {html.escape(cname)}\n"
                                f"╰──────────────────────────────────────────────────"
                            )
                            await event.edit(tombstone, buttons=None, parse_mode="html")
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
                        btn = [[Button.inline("❌ Close Catalog", b"cmd_close", style="danger")]] if Button is not None else None
                        await self.send_to_desk("\n".join(lines), buttons=btn, topic_key="system", parse_mode="html")
                elif data == "cmd_health":
                    await event.answer("🔍 Auditing project health...")
                    await self.scan_and_report_project_health(trigger_event=event)
                elif data.startswith("math_apa_"):
                    mid = data.split("math_apa_")[1]
                    if mid in self.math_registry:
                        entry = self.math_registry[mid]
                        raw_apa = entry["formula_data"].get("raw_apa", "")
                        await event.answer("📋 Copied APA 7 text!", alert=False)
                        msg = (
                            f"📋 <b>APA 7th Text Snippet (Ready for Thesis / Paper)</b>\n"
                            f"🆔 <code>{mid}</code> • 🔬 <code>{entry['test_type'].upper()}</code>\n\n"
                            f"<code>{html.escape(raw_apa)}</code>"
                        )
                        await self.send_to_desk(msg, topic_key="supervisor_reviews", parse_mode="html")
                    else:
                        await event.answer(f"❌ Formula ID {mid} not found.", alert=True)
                elif data.startswith("math_latex_"):
                    mid = data.split("math_latex_")[1]
                    if mid in self.math_registry:
                        entry = self.math_registry[mid]
                        latex_code = entry["formula_data"].get("latex", "")
                        await event.answer("📐 Copied LaTeX block!", alert=False)
                        msg = (
                            f"📐 <b>LaTeX Mathematical Environment</b>\n"
                            f"🆔 <code>{mid}</code> • 🔬 <code>{entry['test_type'].upper()}</code>\n\n"
                            f'<pre><code class="language-latex">{html.escape(latex_code)}</code></pre>'
                        )
                        await self.send_to_desk(msg, topic_key="supervisor_reviews", parse_mode="html")
                    else:
                        await event.answer(f"❌ Formula ID {mid} not found.", alert=True)
                elif data.startswith("math_speech_"):
                    mid = data.split("math_speech_")[1]
                    if mid in self.math_registry:
                        entry = self.math_registry[mid]
                        speech = entry["formula_data"].get("viva_defense_fa", "")
                        await event.answer("🎙️ Oral defense script retrieved!", alert=False)
                        msg = (
                            f"🎙️ <b>متن دفاع شفاهی دانشجو در جلسه شورا / پیش‌دفاع</b>\n"
                            f"🆔 <code>{mid}</code> • 👤 <code>{html.escape(entry['client_name'])}</code>\n\n"
                            f"<blockquote>{html.escape(speech)}</blockquote>"
                        )
                        await self.send_to_desk(msg, topic_key="supervisor_reviews", parse_mode="html")
                    else:
                        await event.answer(f"❌ Formula ID {mid} not found.", alert=True)
                elif data.startswith("send_"):
                    qid = data.split("send_")[1]
                    if qid in self.pending_quotes:
                        entry = self.pending_quotes[qid]
                        # Client receives Persian quote
                        card = format_telegram_card(entry["quote"], lang="fa")
                        target_client = entry.get("client_source") or self.client
                        await target_client.send_message(entry["chat_id"], card, parse_mode="html")
                        await event.answer(f"🚀 Quotation {qid} dispatched to client!", alert=False)
                        try:
                            done_badge = [[Button.inline(f"✅ Dispatched ({qid}) at {now_str}", b"noop", style="success")]] if Button is not None else None
                            await event.edit(
                                f"{event.message.text}\n\n✅ <b>Quotation was approved and dispatched to client at {now_str}.</b>",
                                buttons=done_badge,
                                parse_mode="html"
                            )
                        except Exception:
                            pass
                        del self.pending_quotes[qid]
                    else:
                        await event.answer(f"❌ Quotation ID {qid} expired or not found.", alert=True)
                elif data.startswith("ignore_"):
                    qid = data.split("ignore_")[1]
                    if qid in self.pending_quotes:
                        del self.pending_quotes[qid]
                        await event.answer("🗑️ Quotation dismissed.", alert=False)
                        try:
                            tombstone = (
                                f"╭─ 🗑️ <b>QUOTATION DISMISSED</b> ─────────────────────\n"
                                f"│ 🆔 <b>Quotation ID:</b> <code>{qid}</code>  •  <code>{now_str}</code>\n"
                                f"╰──────────────────────────────────────────────────"
                            )
                            await event.edit(tombstone, buttons=None, parse_mode="html")
                        except Exception:
                            pass
                    else:
                        await event.answer(f"❌ Quotation ID {qid} not found.", alert=True)
                elif data.startswith("ms_adv_"):
                    p_name = data.split("ms_adv_")[1]
                    p_dir = os.path.join(self.project_manager.work_dir, p_name)
                    if not os.path.exists(p_dir):
                        p_dir = self.project_manager.find_existing_project_by_client(p_name)
                    if p_dir and os.path.exists(p_dir):
                        new_state = self.milestone_tracker.advance_stage(p_dir)
                        card = self.milestone_tracker.format_milestone_card(new_state)
                        btns = self.build_milestone_keyboard(p_dir, new_state)
                        await event.answer(f"🚀 Advanced to {new_state['current_stage_code']} ({new_state['progress_pct']}%)!", alert=False)
                        try:
                            await event.edit(card, buttons=btns, parse_mode="html")
                        except Exception:
                            pass
                    else:
                        await event.answer("❌ Project directory not found.", alert=True)
                elif data.startswith("ms_ref_"):
                    p_name = data.split("ms_ref_")[1]
                    p_dir = os.path.join(self.project_manager.work_dir, p_name)
                    if not os.path.exists(p_dir):
                        p_dir = self.project_manager.find_existing_project_by_client(p_name)
                    if p_dir and os.path.exists(p_dir):
                        new_state = self.milestone_tracker.evaluate_milestones(p_dir)
                        card = self.milestone_tracker.format_milestone_card(new_state)
                        btns = self.build_milestone_keyboard(p_dir, new_state)
                        await event.answer(f"🔄 Milestones refreshed ({new_state['progress_pct']}% complete)", alert=False)
                        try:
                            await event.edit(card, buttons=btns, parse_mode="html")
                        except Exception:
                            pass
                    else:
                        await event.answer("❌ Project directory not found.", alert=True)
                elif data.startswith("ms_scp_"):
                    p_name = data.split("ms_scp_")[1]
                    p_dir = os.path.join(self.project_manager.work_dir, p_name)
                    if not os.path.exists(p_dir):
                        p_dir = self.project_manager.find_existing_project_by_client(p_name)
                    if p_dir and os.path.exists(p_dir):
                        new_state = self.milestone_tracker.cycle_scope(p_dir)
                        card = self.milestone_tracker.format_milestone_card(new_state)
                        btns = self.build_milestone_keyboard(p_dir, new_state)
                        await event.answer(f"🔀 Switched scope to {new_state['scope_short']}", alert=False)
                        try:
                            await event.edit(card, buttons=btns, parse_mode="html")
                        except Exception:
                            pass
                    else:
                        await event.answer("❌ Project directory not found.", alert=True)
                elif data == "cmd_briefing_refresh":
                    data_br = self.morning_briefing.compile_briefing_data(pending_quotes=self.pending_quotes)
                    card = self.morning_briefing.format_briefing_card(data_br)
                    btns = self.morning_briefing.build_briefing_keyboard(data_br)
                    await event.answer("🔄 Morning briefing refreshed!", alert=False)
                    try:
                        await event.edit(card, buttons=btns, parse_mode="html")
                    except Exception:
                        pass
                elif data == "cmd_briefing_followups":
                    await event.answer("⚡ Preparing follow-up drafts for stalled clients...", alert=False)
                    await self.scan_and_report_project_health(trigger_event=event)
                elif data == "cmd_deliverables":
                    await event.answer("📦 Inspecting ready deliverables...", alert=False)
                    projs = self.project_manager.list_all_projects()
                    ready_list = []
                    for p in projs:
                        d_files = self.project_manager.list_project_deliverables(p["folder_path"])
                        if d_files:
                            ready_list.append((p, d_files))
                    if ready_list:
                        lines = [f"📦 <b>Client Projects with Ready Deliverables ({len(ready_list)} clients):</b>\n"]
                        for p, dfs in ready_list[:12]:
                            cname = p.get("client_name_fa") or p.get("client_name") or p.get("folder_name")
                            files_str = ", ".join([f"<code>{f['filename']}</code>" for f in dfs[:2]])
                            if len(dfs) > 2:
                                files_str += f" (+{len(dfs)-2} more)"
                            lines.append(f"• <b>{html.escape(cname)}</b>: {files_str}")
                        btn = [[Button.inline("❌ Close", b"cmd_close", style="danger")]] if Button is not None else None
                        await self.send_to_desk("\n".join(lines), buttons=btn, topic_key="health", parse_mode="html")
                    else:
                        await event.answer("📦 No deliverables currently waiting in Drive.", alert=False)
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
                        btn = [[Button.inline("❌ Close Catalog", b"cmd_close", style="danger")]] if Button is not None else None
                        await self.send_to_desk("\n".join(lines), buttons=btn, topic_key="system", parse_mode="html")
                elif data == "cmd_unread":
                    await event.answer("🔍 Scanning client messages...")
                    await self.scan_and_process_unread_messages(trigger_event=event)
                elif data == "cmd_close":
                    try:
                        await event.delete()
                    except Exception:
                        pass
                elif data == "cmd_finance":
                    await event.answer("💰 Loading portfolio financial summary...", alert=False)
                    f_card = self.financial_ledger.format_global_summary_card()
                    btns = [[Button.inline("🔄 Refresh Financials", b"cmd_finance", style="primary")]] if Button is not None else None
                    try:
                        await event.edit(f_card, buttons=btns, parse_mode="html")
                    except Exception:
                        await self.send_to_desk(f_card, buttons=btns, topic_key="health", parse_mode="html")
                elif data.startswith("pay_confirm_"):
                    pid = data.split("pay_confirm_")[1]
                    if pid in self.pending_payments:
                        entry = self.pending_payments[pid]
                        amt = entry.get("detected_amount", 0)
                        if amt <= 0:
                            await event.answer("⚠️ Amount is 0 or invalid. Please use /pay to specify amount.", alert=True)
                        else:
                            tx = self.financial_ledger.record_transaction(
                                entry["project_dir"],
                                amount_tomans=amt,
                                tracking_code=entry.get("tracking_code", ""),
                                payer_name=entry.get("client_name", "")
                            )
                            await event.answer(f"✅ Recorded {format_toman(amt)} Tomans ({tx['receipt_id']})!", alert=False)
                            try:
                                done_badge = [[Button.inline(f"✅ Payment Recorded ({tx['receipt_id']}) at {now_str}", b"noop", style="success")]] if Button is not None else None
                                await event.edit(
                                    f"{event.message.text}\n\n✅ <b>Payment was verified and recorded in Google Drive at {now_str}.</b>",
                                    buttons=done_badge,
                                    parse_mode="html"
                                )
                            except Exception:
                                pass

                            rec_card = self.financial_ledger.format_receipt_card(tx, entry["project_dir"])
                            clean_cname = entry["client_name"].replace(" ", "_")[:20]
                            rec_btns = [
                                [Button.inline("🚀 Send Receipt to Client", f"pay_sendrec_{tx['receipt_id']}_{clean_cname}".encode("utf-8"), style="success")],
                                [Button.inline("💳 View Full Ledger", f"pay_ledger_{clean_cname}".encode("utf-8"), style="primary")]
                            ] if Button is not None else None
                            await self.send_to_desk(rec_card, buttons=rec_btns, topic_key="health", parse_mode="html")
                            del self.pending_payments[pid]
                    else:
                        await event.answer(f"❌ Payment notification {pid} expired or not found.", alert=True)
                elif data.startswith("pay_dismiss_"):
                    pid = data.split("pay_dismiss_")[1]
                    if pid in self.pending_payments:
                        del self.pending_payments[pid]
                        await event.answer("🗑️ Payment notification dismissed.", alert=False)
                        try:
                            await event.edit(f"╭─ 🗑️ <b>PAYMENT NOTIFICATION DISMISSED</b> ───\n│ 🆔 {pid} • {now_str}\n╰──────────────────────────────────────", buttons=None, parse_mode="html")
                        except Exception:
                            pass
                    else:
                        await event.answer("❌ Item expired.", alert=True)
                elif data.startswith("pay_ledger_"):
                    c_key = data.split("pay_ledger_")[1].replace("_", " ")
                    matched_pdir = self.project_manager.find_existing_project_by_client(c_key)
                    if matched_pdir:
                        l_card, l_btns = self.financial_ledger.format_ledger_card(matched_pdir)
                        await event.answer("💳 Loaded client financial ledger!", alert=False)
                        await self.send_to_desk(l_card, buttons=l_btns, topic_key="health", parse_mode="html")
                    else:
                        await event.answer("❌ Project directory not found.", alert=True)
                elif data.startswith("pay_refresh_"):
                    c_key = data.split("pay_refresh_")[1].replace("_", " ")
                    matched_pdir = self.project_manager.find_existing_project_by_client(c_key)
                    if matched_pdir:
                        l_card, l_btns = self.financial_ledger.format_ledger_card(matched_pdir)
                        await event.answer("🔄 Ledger refreshed!", alert=False)
                        try:
                            await event.edit(l_card, buttons=l_btns, parse_mode="html")
                        except Exception:
                            pass
                    else:
                        await event.answer("❌ Project not found.", alert=True)
                elif data.startswith("pay_sendrec_"):
                    parts = data.split("pay_sendrec_")[1].split("_", 1)
                    rec_id = parts[0]
                    c_key = parts[1].replace("_", " ") if len(parts) > 1 else ""
                    matched_pdir = self.project_manager.find_existing_project_by_client(c_key)
                    if matched_pdir:
                        ld = self.financial_ledger.load_ledger(matched_pdir)
                        matched_tx = None
                        for t in ld.get("transactions", []):
                            if t.get("receipt_id") == rec_id:
                                matched_tx = t
                                break
                        if not matched_tx and ld.get("transactions"):
                            matched_tx = ld["transactions"][-1]

                        if matched_tx:
                            rec_text = self.financial_ledger.format_receipt_card(matched_tx, matched_pdir)
                            p_meta = {}
                            meta_path = os.path.join(matched_pdir, "project_meta.json")
                            if os.path.exists(meta_path):
                                with open(meta_path, "r", encoding="utf-8") as f:
                                    p_meta = json.load(f)
                            target_dest = p_meta.get("telegram_id") or p_meta.get("telegram_username") or c_key
                            try:
                                await self.client.send_message(target_dest, rec_text, parse_mode="html")
                                await event.answer(f"🚀 Receipt {rec_id} dispatched to client!", alert=False)
                                try:
                                    done_btn = [[Button.inline(f"✅ Receipt Sent at {now_str}", b"noop", style="success")]] if Button is not None else None
                                    await event.edit(f"{event.message.text}\n\n✅ <b>Official receipt was sent to client via Telegram at {now_str}.</b>", buttons=done_btn, parse_mode="html")
                                except Exception:
                                    pass
                            except Exception as e:
                                await event.answer(f"❌ Failed to dispatch receipt: {e}", alert=True)
                        else:
                            await event.answer("❌ Receipt not found.", alert=True)
                    else:
                        await event.answer("❌ Project not found.", alert=True)

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

                # Send auto-restoration alert if project was awakened from Pending/Finished Works
                if paths.get("was_restored"):
                    days_dormant = paths.get("days_dormant", 30)
                    restored_card = (
                        f"🔄 <b>پروژه مراجع بازیابی و فعال شد</b>\n\n"
                        f"👤 <b>مراجع:</b> {format_client_mention_html(client_name, sender.id, sender.username)}\n"
                        f"📁 <b>پوشه پروژه:</b> <code>{clean_drive_display_path(paths['root'])}</code>\n"
                        f"⏳ <b>مدت عدم فعالیت:</b> {days_dormant} روز\n"
                        f"ℹ️ با دریافت پیام جدید، پوشه این مراجع به‌صورت خودکار از بایگانی به <code>My Work</code> بازگردانده شد."
                    )
                    try:
                        await self.send_to_desk(restored_card, parse_mode="html", topic_key="inquiries")
                    except Exception as e:
                        print(f"[-] Error sending restoration alert: {e}")

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

                # 1. Real-time file saving directly to 01_raw_inputs
                local_path = None
                if fname:
                    print(f"[+] Client {client_name} sent {mtype}: {fname}. Saving directly to Google Drive project...")
                    try:
                        local_path = await self.project_manager.save_single_file(
                            msg=event.message,
                            client_name=client_name,
                            client_id=sender.id,
                            username=sender.username
                        )
                    except Exception as err:
                        print(f"[-] Error saving incoming client file: {err}")

                # 2. Real-time transcript appending directly to Google Drive chat_transcript.md & chat_history.json
                try:
                    self.project_manager.append_message_to_history(
                        client_name=client_name,
                        client_id=sender.id,
                        username=sender.username,
                        msg_id=event.message.id,
                        sender_label=client_name,
                        sender_tag="Client",
                        text=msg_text,
                        file_name=fname,
                        media_type=mtype,
                        file_size=fsize,
                        duration=duration,
                        date_iso=event.message.date.isoformat() if event.message.date else None
                    )
                except Exception as err:
                    print(f"[-] Error appending to chat transcript: {err}")

                # 3. Buffer conversational burst for debounced, high-signal processing (40-second window)
                burst_key = (account_label, sender.id)
                async with self.burst_lock:
                    if burst_key in self.burst_buffers:
                        prev_task = self.burst_buffers[burst_key].get("task")
                        if prev_task and not prev_task.done():
                            prev_task.cancel()
                        buf = self.burst_buffers[burst_key]
                    else:
                        buf = {
                            "chat_id": event.chat_id,
                            "client_name": client_name,
                            "sender_id": sender.id,
                            "username": sender.username,
                            "account_label": account_label,
                            "client_inst": client_inst,
                            "messages": [],
                            "files": []
                        }
                        self.burst_buffers[burst_key] = buf

                    buf["messages"].append({
                        "id": event.message.id,
                        "text": msg_text,
                        "date": event.message.date,
                        "event": event
                    })
                    if fname:
                        buf["files"].append({
                            "name": fname,
                            "type": mtype,
                            "size": fsize,
                            "duration": duration,
                            "local_path": local_path
                        })

                    # Schedule single consolidated card after 40 seconds of client silence
                    buf["task"] = asyncio.create_task(self._process_client_burst(burst_key, delay=40))

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

        # Launch morning briefing autonomous background scheduler loop
        asyncio.create_task(self._morning_briefing_scheduler_loop())
        # Launch periodic offline catch-up sync loop (every 5 minutes)
        asyncio.create_task(self._periodic_catchup_sync_loop())

        while True:
            try:
                # Ensure all active clients are connected
                for cl_target, cl_label in [
                    (self.client, "Main Account"),
                    (self.client2, "Second Account"),
                    (self.bot_client, "Assistant Bot")
                ]:
                    if cl_target and not cl_target.is_connected():
                        try:
                            await cl_target.connect()
                        except Exception as conn_err:
                            print(f"[-] Reconnect error for {cl_label}: {conn_err}")

                tasks = []
                if self.client and self.client.is_connected():
                    tasks.append(asyncio.create_task(self.client.run_until_disconnected()))
                if self.client2 and self.client2.is_connected():
                    tasks.append(asyncio.create_task(self.client2.run_until_disconnected()))
                if self.bot_client and self.bot_client.is_connected():
                    tasks.append(asyncio.create_task(self.bot_client.run_until_disconnected()))

                if not tasks:
                    print("[-] No clients currently connected. Retrying in 5s...")
                    await asyncio.sleep(5)
                    continue

                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for p in pending:
                    p.cancel()

                print("[!] A Telegram client connection closed. Attempting auto-reconnect in 5s...")
                await asyncio.sleep(5)
            except (asyncio.CancelledError, KeyboardInterrupt):
                print("[*] Listener received stop signal. Shutting down cleanly...")
                break
            except (ConnectionError, OSError) as e:
                print(f"[!] Userbot connection interrupted: {e}. Attempting auto-reconnect in 5s...")
                await asyncio.sleep(5)
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
