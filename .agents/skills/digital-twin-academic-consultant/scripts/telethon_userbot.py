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
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union

try:
    from telethon import TelegramClient, events, Button
    from telethon.tl.types import DocumentAttributeFilename, User, MessageService, MessageActionContactSignUp
except ImportError:
    TelegramClient = None
    events = None
    Button = None
    MessageService = None
    MessageActionContactSignUp = None

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
from userbot import (
    AdminCommandDispatcher,
    CallbackQueryDispatcher,
    InlineQueryDispatcher,
    setup_inbound_listeners,
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
        self.processed_proposals_file = os.path.join(self.storage_dir, "processed_proposals.json")
        self.processed_proposals: Dict[str, Any] = self._load_processed_proposals()
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

        # Modular command and query dispatchers
        self.admin_dispatcher = AdminCommandDispatcher(self)
        self.callback_dispatcher = CallbackQueryDispatcher(self)
        self.inline_dispatcher = InlineQueryDispatcher(self)

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

    def _load_processed_proposals(self) -> Dict[str, Any]:
        p_file = getattr(self, "processed_proposals_file", os.path.join(self.storage_dir, "processed_proposals.json"))
        if os.path.exists(p_file):
            try:
                with open(p_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[-] Error loading processed proposals: {e}")
        return {}

    def _save_processed_proposals(self):
        p_file = getattr(self, "processed_proposals_file", os.path.join(self.storage_dir, "processed_proposals.json"))
        try:
            with open(p_file, "w", encoding="utf-8") as f:
                json.dump(self.processed_proposals, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[-] Error saving processed proposals: {e}")

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
        effective_sender_id = sender_id or getattr(event, "sender_id", getattr(event, "chat_id", 0))

        # Deduplication Guard 1: Persistent registry
        file_key = f"{effective_sender_id}_{file_name}" if file_name else None
        text_hash = hashlib.sha256((raw_text or "").strip().encode("utf-8")).hexdigest()[:16]
        text_key = f"{effective_sender_id}_{text_hash}"
        dedup_key = file_key or text_key

        if dedup_key in self.processed_proposals:
            print(f"[*] Skipping duplicate proposal processing for {client_name} (Key: {dedup_key})")
            return

        # Deduplication Guard 2: Active in-memory pending quotes
        for qid, qentry in self.pending_quotes.items():
            if qentry.get("sender_id") == effective_sender_id:
                if file_name and qentry.get("file_name") == file_name:
                    print(f"[*] Quote {qid} is already pending for {client_name} ({file_name}). Skipping.")
                    return
                elif not file_name and qentry.get("text_hash") == text_hash:
                    print(f"[*] Quote {qid} is already pending for {client_name} (text). Skipping.")
                    return

        # 1. Provision standard 4-tier project folder in Google Drive
        project_paths = self.project_manager.provision_project(
            client_name=client_name,
            client_id=effective_sender_id,
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
            "sender_id": effective_sender_id,
            "sender_name": client_name,
            "file_name": file_name,
            "text_hash": text_hash,
            "dedup_key": dedup_key,
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
        client_link = format_client_mention_html(client_name, username=username, client_id=effective_sender_id)
        clean_path = clean_drive_display_path(project_dir)
        safe_fname = html.escape(file_name or "Direct chat message")

        header_lines = [
            "╭─ <b>📥 NEW RESEARCH PROPOSAL RECEIVED</b> ─────────────",
            f"│ 👤 <b>Client:</b> {client_link}  •  <code>#{effective_sender_id}</code>",
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
            client_id=effective_sender_id,
            client_name=client_name,
            parse_mode="html"
        )
        print(f"[+] Posted draft quote {quote_id} for {client_name} to Admin Desk via Assistant Bot.")
        print(f"[+] Project folder synced: {project_dir}")

        self.processed_proposals[dedup_key] = {
            "quote_id": quote_id,
            "sender_id": effective_sender_id,
            "client_name": client_name,
            "file_name": file_name,
            "processed_at": datetime.now().isoformat()
        }
        self._save_processed_proposals()

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
            await asyncio.sleep(900)

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

                # Ignore service messages or contact signed up notifications
                dlg_msg = dlg.message
                if dlg_msg is not None:
                    if (MessageService is not None and isinstance(dlg_msg, MessageService)) or getattr(dlg_msg, "action", None) is not None:
                        continue

                # STRICT 30-DAY INACTIVITY GUARD:
                # Never sync or pull dialogs whose latest interaction is older than 30 days.
                if dlg.date:
                    dlg_dt = dlg.date.replace(tzinfo=None)
                    if (datetime.now() - dlg_dt).days > 30:
                        continue

                existing_dir = self.project_manager.find_existing_project_by_client(
                    dlg.name, client_id=dlg.id, username=getattr(dlg.entity, "username", None)
                )

                needs_sync = False
                sync_reason = ""

                # Condition 1: Unread count > 0
                if dlg.unread_count > 0:
                    # If this contact does not have an existing project folder and is not VIP,
                    # require an affirmative academic signal (file or keywords) before auto-provisioning
                    is_vip = self.project_manager.is_vip_client(
                        dlg.name, client_id=dlg.id, username=getattr(dlg.entity, "username", None)
                    )
                    if not existing_dir and not is_vip:
                        msg_text = (dlg_msg.message or "") if dlg_msg else ""
                        fname, mtype, fsize, _ = resolve_media_details(dlg_msg) if dlg_msg else (None, None, 0, 0)
                        ext = os.path.splitext(fname)[1].lower() if fname else ""
                        has_academic_file = ext in [".docx", ".doc", ".pdf", ".sav", ".xlsx", ".xls", ".sps", ".spv", ".rar", ".zip", ".csv"]
                        has_academic_text = any(w in msg_text for w in [
                            "پروپوزال", "پایان‌نامه", "پایان نامه", "رساله", "مقاله", "تحلیل", "آماری",
                            "پرسشنامه", "فصل ۴", "فصل 4", "فصل چهارم", "فصل 5", "فصل پنجم", "فصل ۳",
                            "فصل 3", "فصل سوم", "استاد راهنما", "داور", "دفاع", "سمپل", "داده", "spss",
                            "pls", "amos", "sem", "لیزرل", "شبیه‌سازی", "فرضیه", "جامعه آماری",
                            "نمونه آماری", "تعرفه", "پیش‌فاکتور", "پیش فاکتور", "هزینه", "انجام میدید",
                            "انجام می‌دید", "مشاوره", "/scale"
                        ])
                        if not has_academic_file and not has_academic_text:
                            continue

                    needs_sync = True
                    sync_reason = f"{dlg.unread_count} unread"
                else:
                    # Condition 2: Offline delta check ONLY for existing academic projects on disk
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
                        f_key = f"{dlg.id}_{fname}"
                        m_key = f"{dlg.id}_{msg.id}_{fname}"
                        if f_key in self.processed_proposals or m_key in self.processed_proposals:
                            print(f"      [*] Skipping already-quoted file: {fname} from {client_name}")
                            continue

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
                            break
                        except Exception as err:
                            print(f"      [-] Error extracting proposal: {err}")

                # Check for long text proposal
                if len(txt) > 80 and any(w in txt for w in ["عنوان", "فرضیه", "پروپوزال", "جامعه", "نمونه", "متغیر"]):
                    t_hash = hashlib.sha256(txt.strip().encode("utf-8")).hexdigest()[:16]
                    t_key = f"{dlg.id}_{t_hash}"
                    m_key = f"{dlg.id}_{msg.id}_text"
                    if t_key in self.processed_proposals or m_key in self.processed_proposals:
                        continue
                    await self.handle_proposal_message(
                        msg, txt, client_name, sender_id=dlg.id, username=username, client_source=cl
                    )
                    found_proposal = True
                    break

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

        # 1. Admin Desk commands dispatcher
        @self.client.on(events.NewMessage(chats=admin_chats))
        async def admin_handler(event):
            await self.admin_dispatcher.dispatch(event)

        # Bot-specific event handlers (callback queries, inline queries, and admin desk commands)
        if self.bot_client:
            @self.bot_client.on(events.CallbackQuery)
            async def bot_callback_handler(event):
                await self.callback_dispatcher.dispatch(event)

            @self.bot_client.on(events.InlineQuery)
            async def bot_inline_handler(event):
                await self.inline_dispatcher.dispatch(event)

            if self.admin_desk_chat_id:
                @self.bot_client.on(events.NewMessage(chats=self.admin_desk_chat_id))
                async def bot_admin_handler(event):
                    await self.admin_dispatcher.dispatch(event)

        # 2. Client Inbound Messages (Private Chats) across personal accounts
        setup_inbound_listeners(self, me=me)

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
