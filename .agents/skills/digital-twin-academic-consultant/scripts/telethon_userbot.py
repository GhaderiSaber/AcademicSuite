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
    format_client_mention_html
)


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
        self.project_manager = ProjectDriveManager(self.config)
        self.admin_desk_chat_id = config.get("admin_desk_chat_id")

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

    async def scan_and_process_unread_messages(self, limit_dialogs: int = 100):
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
                if not latest_text and txt:
                    latest_text = txt

                # Check for proposal files
                if msg.file and hasattr(msg.file, "name") and msg.file.name:
                    fname = sanitize_filename(msg.file.name)
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

        summary_lines.append(
            "─────────────────────\n"
            "⚙️ <b>Commands:</b>\n"
            "• Rescan: <code>/unread</code>\n"
            "• Project Catalog: <code>/projects</code>"
        )
        report_text = "\n".join(summary_lines)

        buttons = None
        if Button is not None:
            buttons = [
                [Button.inline("🔄 Rescan Messages", b"cmd_unread"),
                 Button.inline("📂 Project Catalog", b"cmd_projects")]
            ]

        await self.send_to_desk(report_text, buttons=buttons, parse_mode="html")
        print(f"[+] Posted unread messages and project sync report to Admin Desk via Assistant Bot.")
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

            # List Google Drive projects: /projects or /list_projects
            if txt in ["/projects", "/list_projects"]:
                projs = self.project_manager.list_all_projects()
                if not projs:
                    await event.reply("📂 No project folders found in Google Drive.", parse_mode="html")
                    return
                lines = [f"📂 <b>Active Client Projects in Google Drive ({len(projs)} projects):</b>\n"]
                for p in projs:
                    cname = p.get("client_name_fa") or p.get("client_name") or p.get("folder_name")
                    fc = p.get("file_count", 0)
                    mc = p.get("message_count", 0)
                    st = p.get("status", "pending")
                    top = p.get("topic_fa") or p.get("topic") or "Registered"
                    clean_p = clean_drive_display_path(p['folder_path'])
                    lines.append(
                        f"• <b>{html.escape(cname)}</b> ({html.escape(st)})\n"
                        f"  ▫️ Topic: {html.escape(top[:45])}\n"
                        f"  ▫️ Stats: {mc} msgs | {fc} files\n"
                        f"  ▫️ Drive: <code>{html.escape(clean_p)}</code>\n"
                    )
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

        if self.bot_client:
            @self.bot_client.on(events.CallbackQuery)
            async def bot_callback_handler(event):
                data = (event.data or b"").decode("utf-8")
                if data.startswith("send_"):
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
                        lines = [f"📂 <b>Active Client Projects in Google Drive ({len(projs)} folders):</b>\n"]
                        for p in projs[:12]:
                            cname = p.get("client_name_fa") or p.get("client_name") or p.get("folder_name")
                            cpath = clean_drive_display_path(p['folder_path'])
                            st = p.get('status', 'pending')
                            lines.append(f"• <b>{html.escape(cname)}</b> ({html.escape(st)}) | <code>{html.escape(cpath)}</code>")
                        await self.send_to_desk("\n".join(lines), parse_mode="html")
                elif data == "cmd_unread":
                    await event.answer("🔍 Scanning client messages...")
                    await self.scan_and_process_unread_messages()

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
                print(f"[!] [{account_label}] New DM from client {client_name} (ID: {sender.id}): {msg_text[:60]}")

                # Check if contact is in the excluded non-academic contacts registry
                is_excluded = self.project_manager.is_ignored(client_name, sender.id, sender.username)
                has_doc = bool(event.message.file and getattr(event.message.file, "name", None))
                has_prop = bool(len(msg_text) > 80 and any(w in msg_text for w in ["عنوان", "فرضیه", "پروپوزال", "جامعه", "نمونه", "متغیر"]))

                if is_excluded and not has_doc and not has_prop:
                    # Silently skip casual message from excluded non-academic contact
                    return

                # Ensure client's Google Drive project folder is provisioned
                self.project_manager.provision_project(
                    client_name=client_name,
                    client_id=sender.id,
                    username=sender.username,
                    phone=sender.phone
                )

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

                # Check for attached document (.docx / .pdf / .txt / .xlsx / .sav)
                if event.message.file and event.message.file.name:
                    fname = sanitize_filename(event.message.file.name)
                    ext = os.path.splitext(fname)[1].lower()
                    print(f"[+] Client {client_name} sent attached file: {fname}. Saving directly to Google Drive project...")
                    try:
                        local_path = await self.project_manager.save_single_file(
                            msg=event.message,
                            client_name=client_name,
                            client_id=sender.id,
                            username=sender.username
                        )
                        if ext in [".docx", ".pdf", ".txt"]:
                            raw_content = extract_text_from_file(local_path)
                            await self.handle_proposal_message(
                                event, raw_content, client_name, file_name=fname, sender_id=sender.id, username=sender.username, client_source=client_inst
                            )
                            return
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
                                client_link = format_client_mention_html(client_name, username=sender.username, client_id=sender.id)
                                await self.send_to_desk(
                                    f"📋 <b>Scale Inquiry from {client_link}:</b>\n"
                                    f"<b>Query:</b> {html.escape(msg_text)}\n\n"
                                    f"<b>Prepared Persian Response:</b>\n{scale_info}",
                                    parse_mode="html"
                                )
                            return

        # Setup inbound listeners on both userbot accounts
        setup_inbound_listener(self.client, "Main Account (@GhaderiSaber)")
        if self.client2:
            setup_inbound_listener(self.client2, "Second Account (@SaberGhaderi)")

        if self.admin_desk_chat_id:
            desk_location = f"گروه کاری Academic Desk (ID: {self.admin_desk_chat_id})"
        else:
            desk_location = "پیام‌های ذخیره‌شده (Saved Messages)" if not me.bot else f"چت با اکانت صابر (ID: {self.admin_id})"
        print(f"[*] Telethon {'Userbot' if not me.bot else 'Bot'} is active & listening to incoming DMs on all accounts...")
        print(f"[*] Google Drive Operational Root: {self.project_manager.work_dir}")
        print(f"[*] Open {desk_location} to view real-time proposal alerts, approve quotes, or manage projects.")

        # Scan and report any existing unread messages from clients on startup
        await self.scan_and_process_unread_messages()

        gather_tasks = [self.client.run_until_disconnected()]
        if self.client2 and self.client2.is_connected():
            gather_tasks.append(self.client2.run_until_disconnected())
        if self.bot_client and self.bot_client.is_connected():
            gather_tasks.append(self.bot_client.run_until_disconnected())

        await asyncio.gather(*gather_tasks)


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
