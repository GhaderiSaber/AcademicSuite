#!/usr/bin/env python3
"""
Digital Twin Academic Consultant - Telegram Bot Daemon (telegram_bot_daemon.py)
-------------------------------------------------------------------------------
Automated Telegram bot daemon representing Saber Ghaderi for academic consulting:
1. Greets clients politely and professionally in Saber's authentic voice.
2. Accepts student proposals (.docx, .pdf, or text) and triggers proposal_price_estimator.py.
3. Provides an Admin Review Desk (forwarding draft quotes to Saber at 124911145 for review/adjustment).
4. Handles questionnaire search requests via psychometric-scale-resolver (Questionnaires.xlsx).
5. Answers common methodology and statistical questions from calibrated FAQs.
6. Telegram Mini App (WebApp) integration with inline keyboard launch buttons.
7. SOCKS5 proxy support for regions where Telegram API is restricted.
8. Includes --test-mode to run end-to-end simulated scenarios offline.
"""

import os
import re
import sys
import time
import json
import html
import socket
import ssl
import argparse
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# SOCKS5 proxy support (PySocks) — essential for Iran
try:
    import socks
    HAS_PYSOCKS = True
except ImportError:
    HAS_PYSOCKS = False

# Try importing questionnaire resolver
try:
    RESOLVER_SCRIPT_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "psychometric-scale-resolver", "scripts")
    )
    if os.path.isdir(RESOLVER_SCRIPT_DIR) and RESOLVER_SCRIPT_DIR not in sys.path:
        sys.path.insert(0, RESOLVER_SCRIPT_DIR)
    import questionnaire_resolver
except Exception:
    questionnaire_resolver = None

try:
    from project_drive_manager import (
        ProjectDriveManager,
        sanitize_filename,
        clean_drive_display_path,
        format_client_mention_html
    )
except ImportError:
    ProjectDriveManager = None

# Import proposal price estimator
try:
    from proposal_price_estimator import (
        analyze_proposal_text,
        calculate_quotation,
        format_telegram_card,
        extract_text_from_file,
        load_persona
    )
except ImportError:
    # Direct import fallback
    sys.path.insert(0, os.path.dirname(__file__))
    from proposal_price_estimator import (
        analyze_proposal_text,
        calculate_quotation,
        format_telegram_card,
        extract_text_from_file,
        load_persona
    )

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "bot_config.json")
DEFAULT_PERSONA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "references", "saber_persona.json"
)


class TelegramApiClient:
    """Lightweight Telegram Bot API client with SOCKS5 proxy support."""

    def __init__(self, token: str, proxy: Optional[Dict[str, Any]] = None):
        self.token = token.strip()
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.file_base_url = f"https://api.telegram.org/file/bot{self.token}"
        self.opener: Optional[urllib.request.OpenerDirector] = None
        self._setup_proxy(proxy)

    def _setup_proxy(self, proxy: Optional[Dict[str, Any]] = None):
        """Configure SOCKS5 or HTTP proxy for Telegram API connectivity."""
        if not proxy:
            return

        proxy_type = (proxy.get("proxy_type") or "").lower()
        addr = proxy.get("addr", "127.0.0.1")
        port = int(proxy.get("port", 1080))

        if proxy_type in ("socks5", "socks4") and HAS_PYSOCKS:
            # Store proxy config for per-request socket creation
            self._socks_proxy = {
                "type": socks.SOCKS5 if proxy_type == "socks5" else socks.SOCKS4,
                "addr": addr,
                "port": port,
                "username": proxy.get("username"),
                "password": proxy.get("password"),
            }
            # Create SSL context that accepts self-signed certs (common in Iran VPN setups)
            self._ssl_ctx = ssl.create_default_context()
            self._ssl_ctx.check_hostname = False
            self._ssl_ctx.verify_mode = ssl.CERT_NONE
            print(f"[Proxy] SOCKS5 proxy enabled: {addr}:{port}")
        elif proxy_type in ("http", "https"):
            proxy_url = f"http://{addr}:{port}"
            # For HTTP proxies, also disable SSL verification
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE
            handler = urllib.request.ProxyHandler({
                "http": proxy_url,
                "https": proxy_url
            })
            https_handler = urllib.request.HTTPSHandler(context=ssl_ctx)
            self.opener = urllib.request.build_opener(handler, https_handler)
            print(f"[Proxy] HTTP proxy enabled: {proxy_url}")
        elif proxy_type in ("socks5", "socks4") and not HAS_PYSOCKS:
            print(f"[Proxy] WARNING: PySocks not installed. Install with: pip install PySocks")
            print(f"[Proxy] Attempting direct connection without proxy...")

    def _socks_request(self, url: str, data: Optional[bytes] = None, headers: Optional[Dict[str, str]] = None) -> bytes:
        """Make an HTTP request through SOCKS5 proxy with proper SSL handling."""
        import re as _re
        m = _re.match(r"https://([^/:]+)(:\d+)?(/.*)?", url)
        if not m:
            raise ValueError(f"Invalid HTTPS URL: {url}")
        host = m.group(1)
        port = int(m.group(2)[1:]) if m.group(2) else 443
        path = m.group(3) or "/"

        s = socks.socksocket()
        s.set_proxy(
            self._socks_proxy["type"],
            self._socks_proxy["addr"],
            self._socks_proxy["port"],
            username=self._socks_proxy.get("username"),
            password=self._socks_proxy.get("password"),
        )
        s.settimeout(35)
        s.connect((host, port))
        ss = self._ssl_ctx.wrap_socket(s, server_hostname=host)

        method = "POST" if data else "GET"
        req_headers = f"{method} {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n"
        if headers:
            for k, v in headers.items():
                req_headers += f"{k}: {v}\r\n"
        if data:
            req_headers += f"Content-Length: {len(data)}\r\n"
        req_headers += "\r\n"

        ss.sendall(req_headers.encode() + (data or b""))
        response = b""
        while True:
            chunk = ss.recv(8192)
            if not chunk:
                break
            response += chunk
        ss.close()

        # Parse HTTP response: skip headers, handle chunked
        header_end = response.find(b"\r\n\r\n")
        if header_end == -1:
            return response
        headers_raw = response[:header_end].decode("utf-8", errors="replace").lower()
        body = response[header_end + 4:]

        if "transfer-encoding: chunked" in headers_raw:
            # Decode chunked transfer encoding
            decoded = b""
            while body:
                crlf = body.find(b"\r\n")
                if crlf == -1:
                    break
                chunk_size = int(body[:crlf], 16)
                if chunk_size == 0:
                    break
                decoded += body[crlf + 2: crlf + 2 + chunk_size]
                body = body[crlf + 2 + chunk_size + 2:]
            return decoded
        return body

    def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/{method}"
        try:
            # Use raw SOCKS5 socket for regions where urllib can't handle the proxy SSL
            if hasattr(self, "_socks_proxy"):
                data = json.dumps(params).encode("utf-8") if params else None
                headers = {"Content-Type": "application/json"} if data else None
                body = self._socks_request(url, data=data, headers=headers)
                result = json.loads(body.decode("utf-8"))
                if result.get("ok"):
                    return result
                else:
                    print(f"[Telegram API Error] {result.get('description')}")
                    return None

            # Standard urllib path (direct or HTTP proxy)
            if params:
                data = json.dumps(params).encode("utf-8")
                req = urllib.request.Request(
                    url, data=data, headers={"Content-Type": "application/json"}
                )
            else:
                req = urllib.request.Request(url)

            if self.opener:
                resp = self.opener.open(req, timeout=35)
            else:
                resp = urllib.request.urlopen(req, timeout=35)

            with resp:
                result = json.loads(resp.read().decode("utf-8"))
                if result.get("ok"):
                    return result
                else:
                    print(f"[Telegram API Error] {result.get('description')}")
                    return None
        except Exception as e:
            print(f"[HTTP Error] {method}: {e}")
            return None

    def send_message(
        self, chat_id: int, text: str,
        parse_mode: str = "Markdown",
        reply_markup: Optional[Dict[str, Any]] = None,
        business_connection_id: Optional[str] = None
    ) -> bool:
        payload: Dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if business_connection_id:
            payload["business_connection_id"] = business_connection_id
        if reply_markup:
            payload["reply_markup"] = reply_markup
        res = self.send_request("sendMessage", payload)
        return res is not None

    def get_updates(self, offset: int = 0, timeout: int = 25) -> List[Dict[str, Any]]:
        payload = {
            "offset": offset,
            "timeout": timeout,
            "allowed_updates": [
                "message",
                "edited_message",
                "callback_query",
                "inline_query",
                "business_connection",
                "business_message",
                "edited_business_message",
                "deleted_business_messages"
            ]
        }
        res = self.send_request("getUpdates", payload)
        if res and "result" in res:
            return res["result"]
        return []

    def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        res = self.send_request("getFile", {"file_id": file_id})
        if res and "result" in res:
            return res["result"]
        return None

    def download_file(self, file_path: str, dest_path: str) -> bool:
        url = f"{self.file_base_url}/{file_path}"
        try:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            if hasattr(self, "_socks_proxy"):
                body = self._socks_request(url)
                with open(dest_path, "wb") as f:
                    f.write(body)
            elif self.opener:
                resp = self.opener.open(url, timeout=60)
                with resp, open(dest_path, "wb") as f:
                    f.write(resp.read())
            else:
                resp = urllib.request.urlopen(url, timeout=60)
                with resp, open(dest_path, "wb") as f:
                    f.write(resp.read())
            return True
        except Exception as e:
            print(f"[Download Error] {file_path}: {e}")
            return False

    def set_chat_menu_button(self, webapp_url: str, text: str = "📊 Dashboard") -> bool:
        """Set the bot's menu button to open the WebApp."""
        payload = {
            "menu_button": {
                "type": "web_app",
                "text": text,
                "web_app": {"url": webapp_url}
            }
        }
        res = self.send_request("setChatMenuButton", payload)
        return res is not None

    def set_default_menu_button(self) -> bool:
        """Reset menu button to the default commands menu."""
        payload = {"menu_button": {"type": "commands"}}
        res = self.send_request("setChatMenuButton", payload)
        return res is not None

    def set_bot_commands(self, commands: List[Dict[str, str]]) -> bool:
        """Register bot commands for the Telegram menu."""
        payload = {"commands": commands}
        res = self.send_request("setMyCommands", payload)
        return res is not None

    def get_me(self) -> Optional[Dict[str, Any]]:
        """Verify bot token and get bot info."""
        res = self.send_request("getMe")
        if res and "result" in res:
            return res["result"]
        return None


class DigitalSaberBot:
    """Digital Twin of Saber Ghaderi for Telegram with WebApp and Business Mode integration."""

    def __init__(
        self,
        token: str = "",
        admin_id: int = 124911145,
        admin_desk_chat_id: Optional[int] = -1004331808205,
        business_mode: bool = True,
        auto_quote: bool = False,
        work_dir: Optional[str] = None,
        webapp_url: str = "",
        proxy: Optional[Dict[str, Any]] = None
    ):
        self.token = token
        self.admin_id = admin_id
        self.admin_desk_chat_id = admin_desk_chat_id
        self.business_mode = business_mode
        self.auto_quote = auto_quote
        self.webapp_url = webapp_url
        self.work_dir = work_dir or os.path.join(os.path.dirname(__file__), "bot_storage")
        os.makedirs(self.work_dir, exist_ok=True)
        
        self.persona = load_persona()
        self.tg = TelegramApiClient(self.token, proxy=proxy) if self.token else None
        self.pending_quotes: Dict[str, Dict[str, Any]] = {}
        self.quote_counter = 100
        self.running = True
        self.project_manager = ProjectDriveManager() if ProjectDriveManager else None
        self.business_connections_path = os.path.join(self.work_dir, "business_connections.json")
        self.business_connections: Dict[str, Dict[str, Any]] = self._load_business_connections()

    def _load_business_connections(self) -> Dict[str, Any]:
        if os.path.exists(self.business_connections_path):
            try:
                with open(self.business_connections_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_business_connections(self):
        try:
            with open(self.business_connections_path, "w", encoding="utf-8") as f:
                json.dump(self.business_connections, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[-] Error saving business connections: {e}")

    def handle_business_connection(self, conn: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Telegram Business connection handshake, updates, and disconnections."""
        conn_id = conn.get("id", "")
        user = conn.get("user", {})
        user_id = user.get("id")
        user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "Saber Ghaderi"
        username = user.get("username", "")
        is_enabled = conn.get("is_enabled", False)
        can_reply = conn.get("can_reply", False)

        entry = {
            "id": conn_id,
            "user_id": user_id,
            "user_name": user_name,
            "username": username,
            "is_enabled": is_enabled,
            "can_reply": can_reply,
            "updated_at": datetime.now().isoformat()
        }
        self.business_connections[conn_id] = entry
        self._save_business_connections()

        status_str = "ENABLED & ACTIVE" if is_enabled else "DISABLED"
        print(f"[Business] Connection {conn_id}: {user_name} (@{username}) -> {status_str} (Can reply: {can_reply})")

        desk_target = self.admin_desk_chat_id or self.admin_id
        if self.tg and desk_target:
            if is_enabled:
                alert = (
                    f"🤝 <b>Telegram Business Connected!</b>\n\n"
                    f"• <b>Account:</b> {html.escape(user_name)} (@{html.escape(username)})\n"
                    f"• <b>Connection ID:</b> <code>{conn_id}</code>\n"
                    f"• <b>Can Reply:</b> {'Yes (Active)' if can_reply else 'No (Read-only)'}\n\n"
                    f"<i>The bot is now authorized to assist clients in Saber's 1-on-1 private chats.</i>"
                )
            else:
                alert = (
                    f"⚠️ <b>Telegram Business Disconnected</b>\n"
                    f"Connection with {html.escape(user_name)} was removed or deactivated."
                )
            self.tg.send_message(desk_target, alert, parse_mode="HTML")

        return entry

    def handle_business_message(self, b_msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming messages inside connected business 1-on-1 chats."""
        conn_id = b_msg.get("business_connection_id", "")
        chat = b_msg.get("chat", {})
        chat_id = chat.get("id")
        sender = b_msg.get("from", {})
        sender_id = sender.get("id")
        sender_name = f"{sender.get('first_name', '')} {sender.get('last_name', '')}".strip() or "پژوهشگر"
        username = sender.get("username")
        msg_text = (b_msg.get("text") or "").strip()

        # Check if message was sent by the business account owner (Saber)
        conn_info = self.business_connections.get(conn_id, {})
        owner_id = conn_info.get("user_id") or self.admin_id
        if sender_id == owner_id:
            # Outgoing message from Saber inside client chat - ignore to avoid self-reply loop
            return None

        print(f"[Business DM] From {sender_name} (ID: {sender_id}): {msg_text[:60]}")

        # Ensure client project folder is provisioned in Google Drive
        if self.project_manager:
            try:
                self.project_manager.provision_project(
                    client_name=sender_name,
                    client_id=sender_id,
                    username=username
                )
            except Exception as e:
                print(f"[-] Drive provisioning error: {e}")

        desk_target = self.admin_desk_chat_id or self.admin_id

        # 1. Handle Document Upload (.docx, .pdf, .sav, .xlsx)
        doc = b_msg.get("document")
        if doc and chat_id:
            file_id = doc.get("file_id")
            file_name = doc.get("file_name", "proposal.docx")
            print(f"[Business DM] Client document received: {file_name} from {sender_name}")
            local_dest = os.path.join(self.work_dir, f"{chat_id}_{file_name}")
            if self.tg:
                file_info = self.tg.get_file_info(file_id)
                if file_info and "file_path" in file_info:
                    if self.tg.download_file(file_info["file_path"], local_dest):
                        reply, pending = self.handle_proposal_submission(
                            chat_id, sender_name, file_path=local_dest
                        )
                        if pending:
                            qid = list(self.pending_quotes.keys())[-1]
                            self.pending_quotes[qid]["business_connection_id"] = conn_id
                            self.pending_quotes[qid]["is_business"] = True
                            adm_card = format_telegram_card(pending["quote"], include_admin_actions=True, quote_id=qid, lang="en")
                            adm_notice = (
                                f"🔔 <b>New Proposal via Telegram Business:</b>\n"
                                f"👤 <b>Client:</b> {html.escape(sender_name)} (@{username or 'none'})\n"
                                f"💬 <i>Received directly in Saber's 1-on-1 private chat</i>\n\n"
                                f"{adm_card}"
                            )
                            self.tg.send_message(desk_target, adm_notice, parse_mode="HTML")
                        return {"type": "document", "status": "processed", "file": file_name}
            return {"type": "document", "status": "received"}

        # 2. Check for proposal text (lengthy text with thesis keywords)
        if len(msg_text) > 80 and any(w in msg_text for w in ["عنوان", "فرضیه", "پروپوزال", "جامعه", "نمونه", "متغیر"]):
            reply, pending = self.handle_proposal_submission(chat_id, sender_name, text_content=msg_text)
            if pending:
                qid = list(self.pending_quotes.keys())[-1]
                self.pending_quotes[qid]["business_connection_id"] = conn_id
                self.pending_quotes[qid]["is_business"] = True
                adm_card = format_telegram_card(pending["quote"], include_admin_actions=True, quote_id=qid, lang="en")
                adm_notice = (
                    f"🔔 <b>New Proposal Inquiry via Telegram Business:</b>\n"
                    f"👤 <b>Client:</b> {html.escape(sender_name)} (@{username or 'none'})\n"
                    f"💬 <i>Received directly in Saber's 1-on-1 private chat</i>\n\n"
                    f"{adm_card}"
                )
                if self.tg and desk_target:
                    self.tg.send_message(desk_target, adm_notice, parse_mode="HTML")
            return {"type": "proposal_text", "status": "quoted"}

        # 3. Check for questionnaire / scale search (/scale <name>)
        m_scale = re.match(r"^/scale\s+(.+)", msg_text)
        if m_scale:
            query = m_scale.group(1).strip()
            scale_reply = self.handle_questionnaire_search(query)
            if self.tg and conn_info.get("can_reply", True):
                self.tg.send_message(chat_id, scale_reply, business_connection_id=conn_id)
            return {"type": "scale_search", "query": query}

        # 4. Standard consultation greeting on first message or /start
        if msg_text in ["/start", "سلام", "درود"]:
            welcome = (
                f"سلام و درود، وقت شما بخیر {sender.get('first_name', '')} گرامی.\n\n"
                "دستیار هوشمند و مشاور پژوهشی صابر قادری در خدمت شماست.\n"
                "در صورت تمایل به استعلام هزینه و زمان‌بندی، فایل پروپوزال (`.docx` یا `.pdf`) خود را ارسال بفرمایید."
            )
            if self.tg and conn_info.get("can_reply", True):
                self.tg.send_message(chat_id, welcome, business_connection_id=conn_id)
            return {"type": "greeting", "status": "sent"}

        return {"type": "text", "status": "received"}

    def setup_bot_commands_and_menu(self):
        """Register bot commands and set WebApp menu button on startup."""
        if not self.tg:
            return

        # Verify bot identity
        me = self.tg.get_me()
        if me:
            print(f"[Bot] Authenticated as @{me.get('username', '?')} (ID: {me.get('id')})")
        else:
            print("[Bot] WARNING: Could not verify bot token. Check your token and proxy.")
            return

        # Register slash commands
        commands = [
            {"command": "start", "description": "شروع و معرفی خدمات مشاوره"},
            {"command": "help", "description": "راهنمای دستورات و امکانات ربات"},
            {"command": "scale", "description": "جستجوی پرسشنامه در بانک ۴,۸۸۰ مقیاس"},
            {"command": "quote", "description": "درخواست پیش‌فاکتور هزینه و زمان‌بندی"},
            {"command": "dashboard", "description": "مشاهده داشبورد و وضعیت پروژه‌ها"},
        ]
        if self.tg.set_bot_commands(commands):
            print(f"[Bot] Registered {len(commands)} slash commands.")

        # Set WebApp menu button if URL is configured
        if self.webapp_url:
            if self.tg.set_chat_menu_button(self.webapp_url, text="📊 Dashboard"):
                print(f"[Bot] Menu button set to WebApp: {self.webapp_url}")
            else:
                print("[Bot] WARNING: Failed to set menu button.")
        else:
            # Set default commands menu if no webapp URL
            self.tg.set_default_menu_button()
            print("[Bot] No webapp_url configured. Using default commands menu.")
            print("[Bot] To enable WebApp, set 'webapp_url' in bot_config.json to your public HTTPS URL.")

    def _build_start_reply_markup(self) -> Optional[Dict[str, Any]]:
        """Build inline keyboard for /start with WebApp button."""
        buttons = []

        # WebApp launch button (only if URL configured)
        if self.webapp_url:
            buttons.append([{
                "text": "📊 باز کردن داشبورد پروژه‌ها",
                "web_app": {"url": self.webapp_url}
            }])

        # Quick action buttons
        buttons.append([
            {"text": "📋 جستجوی پرسشنامه", "callback_data": "action_scale_search"},
            {"text": "💰 استعلام هزینه", "callback_data": "action_quote"},
        ])
        buttons.append([
            {"text": "📞 ارتباط مستقیم با صابر قادری", "url": "https://t.me/GhaderiSaber"},
        ])

        return {"inline_keyboard": buttons}

    def generate_welcome_message(self, user_first_name: str = "پژوهشگر گرامی") -> str:
        """Create greeting message explaining capabilities (HTML format)."""
        msg = (
            f"سلام و درود، {html.escape(user_first_name)} وقتتون بخیر.\n"
            "من دستیار هوشمند و همزاد تخصصی <b>صابر قادری</b> هستم؛ پژوهشگر دکتری روان‌شناسی، متخصص متدولوژی، روان‌سنجی و تحلیل‌های آماری پیشرفته.\n\n"
            "✨ <b>خدمات تخصصی قابل ارائه:</b>\n"
            "1. 📊 <b>بررسی پروپوزال و استعلام هزینه:</b> ارسال فایل پروپوزال (<code>.docx</code> یا <code>.pdf</code>) جهت دریافت پیش‌فاکتور تفکیکی و زمان‌بندی دقیق.\n"
            "2. 📋 <b>بانک پرسشنامه‌ها:</b> جستجوی فوری ۴,۸۸۰ آزمون روان‌شناختی همراه با کلید نمره‌گذاری و روایی/پایایی با دستور /scale.\n"
            "3. 🔬 <b>مشاوره روش‌شناسی و آماری:</b> پاسخ به پرسش‌های آماری (AMOS، SPSS، SmartPLS، G*Power، تحلیل فرضیات و مدل‌یابی).\n"
            "4. 📝 <b>ویرایش و کاهش همانندجویی:</b> بازنویسی علمی و کاهش درصد سمیم‌نور و ایران‌داک.\n\n"
            "💡 برای شروع، می‌توانید فایل پروپوزال یا سوال تخصصی‌تون رو مستقیماً ارسال بفرمایید یا دستور /help رو لمس کنید."
        )
        return msg

    def handle_questionnaire_search(self, query: str) -> str:
        """Search questionnaire database using psychometric-scale-resolver."""
        if not query.strip():
            return "لطفاً نام پرسشنامه یا مقیاس مورد نظرتون رو وارد کنید:\nمثال: `/scale تاب‌آوری کانر`"

        clean_query = query.strip()
        # Clean leading words
        clean_query = re.sub(r"^(?:پرسشنامه|مقیاس|آزمون|تست)\s+", "", clean_query).strip()

        if questionnaire_resolver is not None:
            try:
                # Try variations: original, space-normalized, individual words
                candidate_queries = [
                    clean_query,
                    clean_query.replace("\u200c", " "),
                    clean_query.replace(" ", "\u200c")
                ]
                # Add individual words longer than 2 chars
                words = [w for w in clean_query.replace("\u200c", " ").split() if len(w) > 2]
                if len(words) > 1:
                    candidate_queries.append(" ".join(words[:2]))
                    candidate_queries.extend(words)

                profile = None
                for cand in candidate_queries:
                    p = questionnaire_resolver.get_scale_profile(cand)
                    if p and p.get("found_in_registry"):
                        profile = p
                        break

                if profile and profile.get("found_in_registry"):
                    lines = []
                    lines.append(f"📋 *اطلاعات ابزار اندازه‌گیری در بانک جامع:*")
                    lines.append(f"▫️ **نام مقیاس:** {profile.get('scale_name')}")
                    if profile.get("scale_persian_name"):
                        lines.append(f"▫️ **نام فارسی:** {profile.get('scale_persian_name')}")
                    if profile.get("abbreviation"):
                        lines.append(f"▫️ **اختصار:** {profile.get('abbreviation')}")
                    lines.append(f"▫️ **تعداد کل گویه‌ها:** {profile.get('total_items_count', 'مشخص در راهنما')}")
                    lines.append(f"▫️ **شیوه نمره‌گذاری:** {profile.get('scoring_method', 'طیف لیکرت')}")
                    
                    if profile.get("all_reverse_items"):
                        lines.append(f"▫️ **گویه‌های نمره‌گذاری معکوس:** {', '.join(map(str, profile['all_reverse_items']))}")

                    subs = profile.get("subscales", [])
                    if subs:
                        lines.append("\n🧩 *خرده‌مقیاس‌ها و مولفه‌ها:*")
                        for s in subs[:6]:
                            sub_name = s.get("subscale_name", "")
                            items_cnt = len(s.get("items_parsed", []))
                            lines.append(f"  • {sub_name} ({items_cnt} گویه)")
                        if len(subs) > 6:
                            lines.append(f"  • و {len(subs) - 6} مولفه دیگر...")

                    lines.append("\n✅ این ابزار در آرشیو مقیاس‌های استاندارد موجود است. در صورت نیاز به فایل کامل یا کلید نمره‌گذاری در خدمتم.")
                    return "\n".join(lines)
            except Exception as e:
                print(f"[Resolver Error] {e}")

        # Fallback response
        return (
            f"🔍 درخواست جستجوی مقیاس «{clean_query}» ثبت شد.\n"
            "این پرسشنامه در حال استعلام از مخزن اصلی ابزارهای استاندارد می‌باشد. "
            "به زودی مشخصات، تعداد گویه‌ها و شیوه نمره‌گذاری توسط صابر قادری خدمتتون تقدیم می‌شود."
        )

    def handle_proposal_submission(
        self,
        chat_id: int,
        sender_name: str,
        file_path: Optional[str] = None,
        text_content: Optional[str] = None
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Process proposal and generate quote."""
        raw_text = ""
        if file_path and os.path.exists(file_path):
            raw_text = extract_text_from_file(file_path)
        elif text_content:
            raw_text = text_content

        if not raw_text or len(raw_text.strip()) < 30:
            return (
                "متن یا فایل ارسال‌شده کوتاه است. لطفاً فایل پروپوزال کامل یا حداقل شامل «عنوان، فرضیه‌ها، جامعه و ابزارها» را ارسال فرمایید.",
                None
            )

        analysis = analyze_proposal_text(raw_text)
        quote = calculate_quotation(analysis, self.persona)

        self.quote_counter += 1
        quote_id = f"Q{self.quote_counter}"

        self.pending_quotes[quote_id] = {
            "chat_id": chat_id,
            "sender_name": sender_name,
            "quote": quote,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }

        # Client receipt message
        client_msg = (
            "✅ *پروپوزال شما با موفقیت دریافت شد.*\n"
            f"📌 **عنوان شناسایی‌شده:** {quote['title']}\n"
            f"🔬 **طرح پژوهش:** {quote['design_title_fa']}\n"
            f"👥 **حجم نمونه برآوردی:** N = {quote['sample_size']}\n\n"
            "⏳ پیش‌فاکتور تفکیکی و برنامه زمان‌بندی توسط مهندس صابر قادری در حال بررسی نهایی است و به زودی خدمتتون ارسال می‌شود."
        )

        return client_msg, self.pending_quotes[quote_id]

    def handle_admin_action(self, admin_chat_id: int, command_text: str) -> str:
        """Handle Saber's approval or adjustment of quotes."""
        valid_admins = [self.admin_id]
        if self.admin_desk_chat_id:
            valid_admins.append(self.admin_desk_chat_id)
        if admin_chat_id not in valid_admins:
            return "Unauthorized access. Admin privileges required."

        # Approve: /approve_Q101 or /send_Q101
        m_app = re.match(r"^/(?:approve|send)_(Q\d+)", command_text)
        if m_app:
            qid = m_app.group(1)
            if qid in self.pending_quotes:
                item = self.pending_quotes[qid]
                client_chat_id = item["chat_id"]
                conn_id = item.get("business_connection_id")
                tg_card = format_telegram_card(item["quote"], lang="fa")
                
                # Send to client if live
                if self.tg:
                    self.tg.send_message(
                        client_chat_id,
                        tg_card,
                        parse_mode="HTML",
                        business_connection_id=conn_id
                    )
                
                item["status"] = "approved"
                channel_str = " (via Telegram Business)" if conn_id else ""
                return f"✅ Quotation {qid} approved and dispatched to {item['sender_name']}{channel_str}."
            return f"Quotation {qid} not found."

        # Adjust: /adjust_Q101_8500000
        m_adj = re.match(r"^/adjust_(Q\d+)_(\d+)", command_text)
        if m_adj:
            qid = m_adj.group(1)
            new_price = int(m_adj.group(2))
            if qid in self.pending_quotes:
                item = self.pending_quotes[qid]
                conn_id = item.get("business_connection_id")
                item["quote"]["total_price_tomans"] = new_price
                item["quote"]["total_price_formatted"] = f"{new_price:,.0f} تومان"
                client_chat_id = item["chat_id"]
                tg_card = format_telegram_card(item["quote"], lang="fa")
                
                if self.tg:
                    self.tg.send_message(
                        client_chat_id,
                        tg_card,
                        parse_mode="HTML",
                        business_connection_id=conn_id
                    )
                
                item["status"] = "approved_adjusted"
                channel_str = " (via Telegram Business)" if conn_id else ""
                return f"✅ Quotation {qid} adjusted to {new_price:,.0f} Tomans and dispatched to {item['sender_name']}{channel_str}."
            return f"Quotation {qid} not found."

        # Reject / Ignore
        m_rej = re.match(r"^/(?:reject|ignore)_(Q\d+)", command_text)
        if m_rej:
            qid = m_rej.group(1)
            if qid in self.pending_quotes:
                self.pending_quotes[qid]["status"] = "rejected"
                return f"❌ Quotation {qid} dismissed."
            return f"Quotation {qid} not found."

        return "Invalid command. Format: <code>/approve_Q101</code>, <code>/send_Q101</code>, or <code>/adjust_Q101_8000000</code>"

    def handle_incoming_text(self, chat_id: int, sender_name: str, text: str) -> str:
        """Route and answer text queries."""
        clean = text.strip()

        # Admin commands
        valid_admins = [self.admin_id]
        if self.admin_desk_chat_id:
            valid_admins.append(self.admin_desk_chat_id)
        if chat_id in valid_admins and clean.startswith(("/approve_", "/send_", "/adjust_", "/reject_", "/ignore_")):
            return self.handle_admin_action(chat_id, clean)

        # Standard commands & greetings
        greeting_words = ["/start", "سلام", "درود", "صبح بخیر", "عصر بخیر", "شب بخیر", "وقت بخیر"]
        if clean in ["/start", "/help"] or (len(clean.split()) <= 4 and any(clean.startswith(gw) or clean == gw for gw in greeting_words)):
            welcome = self.generate_welcome_message(sender_name)
            # Send with inline keyboard (WebApp button + quick actions)
            markup = self._build_start_reply_markup()
            if self.tg and markup:
                self.tg.send_message(chat_id, welcome, parse_mode="HTML", reply_markup=markup)
                return "__SENT__"  # Signal that message was already sent
            return welcome

        # Dashboard / WebApp command
        if clean in ["/dashboard", "/webapp"]:
            if self.webapp_url:
                markup = {"inline_keyboard": [[
                    {"text": "📊 باز کردن داشبورد", "web_app": {"url": self.webapp_url}}
                ]]}
                if self.tg:
                    self.tg.send_message(
                        chat_id,
                        "🖥 برای مشاهده وضعیت پروژه‌ها، محاسبه‌گر هزینه و بانک پرسشنامه‌ها دکمه زیر را لمس کنید:",
                        reply_markup=markup
                    )
                    return "__SENT__"
                return "برای مشاهده داشبورد، از دکمه منوی ربات استفاده کنید."
            return "داشبورد هنوز فعال نشده است. لطفاً با صابر قادری تماس بگیرید: @GhaderiSaber"

        # Quote request command
        if clean in ["/quote", "/price", "/estimate"]:
            return (
                "📌 **درخواست پیش‌فاکتور و استعلام هزینه:**\n\n"
                "لطفاً فایل پروپوزال خود را (`.docx` یا `.pdf`) ارسال فرمایید، یا اطلاعات زیر را به صورت متنی ارسال کنید:\n\n"
                "• **عنوان پژوهش**\n"
                "• **مقطع تحصیلی** (ارشد / دکتری)\n"
                "• **طرح پژوهش** (شبه‌آزمایشی، همبستگی، SEM و...)\n"
                "• **حجم نمونه و جامعه آماری**\n"
                "• **ابزارهای اندازه‌گیری** (نام پرسشنامه‌ها)\n\n"
                "پس از دریافت، پیش‌فاکتور تفکیکی همراه با زمان‌بندی خدمتتون تقدیم می‌شود."
            )

        if clean.startswith(("/scale", "/questionnaire")):
            query = re.sub(r"^/(?:scale|questionnaire)", "", clean).strip()
            return self.handle_questionnaire_search(query)

        # Check if user asks for questionnaire in natural language
        if any(w in clean for w in ["پرسشنامه", "مقیاس", "آزمون"]) and len(clean.split()) <= 10:
            query = re.sub(r"(?:داری|دارید|رو\s*دارید|می‌خواستم|لطفاً|سلام|وقت\s*بخیر)", "", clean).strip()
            return self.handle_questionnaire_search(query)

        # Check if text is a proposal description (lengthy text with title/hypothesis)
        if len(clean) > 80 and any(w in clean for w in ["عنوان", "فرضیه", "پروپوزال", "جامعه", "نمونه", "متغیر"]):
            resp, pending = self.handle_proposal_submission(chat_id, sender_name, text_content=clean)
            # Forward draft to admin
            if pending:
                qid = list(self.pending_quotes.keys())[-1]
                admin_card = format_telegram_card(pending["quote"], include_admin_actions=True, quote_id=qid, lang="en")
                admin_notice = (
                    f"🔔 <b>New Quotation Request from {html.escape(sender_name)} (ID: {qid}):</b>\n\n"
                    f"{admin_card}"
                )
                if self.tg and self.admin_id:
                    self.tg.send_message(self.admin_id, admin_notice, parse_mode="HTML")
            return resp

        # FAQ & Consulting logic
        # Check calibrated FAQs
        faqs = self.persona.get("calibrated_faqs", [])
        for f in faqs:
            q_keywords = [w for w in f.get("client_question", "").split() if len(w) > 3]
            if len(q_keywords) >= 2 and sum(1 for kw in q_keywords if kw in clean) >= 2:
                return f"{self.persona.get('tone_and_style', {}).get('greetings', ['سلام وقتتون بخیر'])[0]}\n\n{f.get('saber_reply')}\n\n{self.persona.get('tone_and_style', {}).get('sign_offs', ['در خدمتم'])[0]}"

        # Methodology / software advice
        if any(w in clean for w in ["نرم‌افزار", "spss", "amos", "smartpls", "کدوم نرم‌افزار", "تفاوت amos و pls"]):
            return (
                "سلام وقتتون بخیر.\n"
                "انتخاب نرم‌افزار آماری به صورت مستقیم به طرح پژوهش و حجم نمونه بستگی دارد:\n"
                "• **AMOS و Lisrel:** برای مدل‌های کوواریانس‌محور (CB-SEM) با هدف تایید نظریه و حجم نمونه‌های بالای ۲۰۰ نفر.\n"
                "• **SmartPLS 4:** برای مدل‌های واریانس‌محور (PLS-SEM)، مدل‌های پیچیده با متغیرهای درجه‌دوم و حجم نمونه کمتر یا داده‌های غیرنرمال.\n"
                "• **SPSS 28:** برای تحلیل‌های توصیفی، رگرسیون خطی، آزمون‌های t، تحلیل واریانس و کوواریانس (ANOVA/ANCOVA).\n\n"
                "در صورت ارسال مدل مفهومی یا فرضیات، نرم‌افزار بهینه را خدمتتون مشخص می‌کنم."
            )

        # Default helpful consultation response
        return (
            "سلام وقتتون بخیر، در خدمتم.\n"
            "پیام شما بررسی شد. در صورت تمایل به دریافت پیش‌فاکتور هزینه و زمان‌بندی، لطفاً فایل یا عنوان و فرضیات پروپوزال را ارسال فرمایید. "
            "همچنین در صورت نیاز به هرگونه مشاوره آماری، طراحی ابزار یا آزمون فرضیات در خدمتم."
        )

    def run_test_simulation(self) -> Dict[str, Any]:
        """Run complete end-to-end simulated scenarios offline."""
        print("=== Digital Twin Saber: Test Simulation Mode ===")
        events = []

        # Scenario 1: Client greeting
        res1 = self.handle_incoming_text(chat_id=1001, sender_name="سارا کریمی", text="سلام وقت بخیر")
        print(f"\n[Test 1: Greeting]\n{res1[:120]}...")
        events.append({"step": "greeting", "output": res1})

        # Scenario 2: Questionnaire search
        res2 = self.handle_incoming_text(chat_id=1001, sender_name="سارا کریمی", text="/scale تاب‌آوری کانر")
        print(f"\n[Test 2: Scale Search]\n{res2[:180]}...")
        events.append({"step": "scale_search", "output": res2})

        # Scenario 3: Proposal submission
        sample_proposal = (
            "عنوان: بررسی اثربخشی درمان مبتنی بر شفقت خود بر اضطراب مرگ و کیفیت زندگی سالمندان\n"
            "طرح پژوهش: نیمه‌آزمایشی با پیش‌آزمون، پس‌آزمون و پیگیری با گروه کنترل\n"
            "حجم نمونه: ۳۰ نفر (۱۵ آزمایش، ۱۵ کنترل)\n"
            "ابزارها: مقیاس اضطراب مرگ تمپلر و پرسشنامه کیفیت زندگی WHOQOL-BREF\n"
            "تحلیل آماری: تحلیل کوواریانس تک‌متغیره و چندمتغیره در نرم‌افزار SPSS 28"
        )
        res3, pending = self.handle_proposal_submission(chat_id=1001, sender_name="سارا کریمی", text_content=sample_proposal)
        print(f"\n[Test 3: Proposal Submission & Quotation]\nClient notice: {res3}\n")
        
        qid = list(self.pending_quotes.keys())[-1]
        admin_card = format_telegram_card(pending["quote"], include_admin_actions=True, quote_id=qid)
        print(f"[Admin Approval Card for Saber (ID: {self.admin_id})]:\n{admin_card}")
        events.append({"step": "proposal_submission", "quote_id": qid, "quote": pending["quote"]})

        # Scenario 4: Admin approval command
        res4 = self.handle_incoming_text(chat_id=self.admin_id, sender_name="Saber Ghaderi", text=f"/approve_{qid}")
        print(f"\n[Test 4: Admin Approval Command]\n{res4}")
        events.append({"step": "admin_approval", "output": res4})

        # Scenario 5: Statistical consulting FAQ
        res5 = self.handle_incoming_text(chat_id=1002, sender_name="محمد نوری", text="تفاوت amos و pls چیه برای پایان‌نامه‌ام؟")
        print(f"\n[Test 5: Stats Consulting]\n{res5[:160]}...")
        events.append({"step": "stats_consulting", "output": res5})

        # Scenario 6: Telegram Business Connection & Business Message
        test_conn = {
            "id": "conn_test_999",
            "user": {"id": self.admin_id, "first_name": "Saber", "last_name": "Ghaderi", "username": "GhaderiSaber"},
            "is_enabled": True,
            "can_reply": True
        }
        res_conn = self.handle_business_connection(test_conn)
        print(f"\n[Test 6: Telegram Business Connection]\nConnection Registered: {res_conn['id']} ({res_conn['user_name']})")
        events.append({"step": "business_connection", "output": res_conn})

        test_bmsg = {
            "business_connection_id": "conn_test_999",
            "chat": {"id": 2002, "type": "private"},
            "from": {"id": 2002, "first_name": "علی", "last_name": "رضایی", "username": "ali_rezaei"},
            "text": "عنوان: پیش‌بینی اشتیاق شغلی بر اساس تاب‌آوری و شفقت خود در کادر درمان\nطرح: همبستگی و رگرسیون چندگانه\nجامعه: ۲۵۰ نفر\nابزار: مقیاس اشتیاق شوفلی و تاب‌آوری کانر",
            "date": 1720000000
        }
        res_bmsg = self.handle_business_message(test_bmsg)
        print(f"[Test 6b: Telegram Business Message]\nProposal processed from client Ali Rezaei: {res_bmsg}")
        events.append({"step": "business_message", "output": res_bmsg})

        print("\n✅ All 6 simulation tests executed successfully!")
        return {"status": "success", "events": events}

    def start_polling(self):
        """Start long-polling daemon loop."""
        if not self.tg:
            print("[-] Telegram Bot Token is not configured. Run with --test-mode or set token in config.")
            return

        # Setup commands and menu button on startup
        self.setup_bot_commands_and_menu()

        print(f"[*] Digital Twin Saber Bot started. Admin ID: {self.admin_id}")
        if self.webapp_url:
            print(f"[*] WebApp URL: {self.webapp_url}")
        else:
            print("[*] WebApp URL not configured. Set 'webapp_url' in bot_config.json for Mini App integration.")
        print(f"[*] Listening for updates via long-polling...")
        offset = 0

        while self.running:
            try:
                updates = self.tg.get_updates(offset=offset)
                for update in updates:
                    update_id = update.get("update_id", 0)
                    offset = max(offset, update_id + 1)

                    # 1. Handle Business Connection update
                    b_conn = update.get("business_connection")
                    if b_conn:
                        self.handle_business_connection(b_conn)
                        continue

                    # 2. Handle Business Message update
                    b_msg = update.get("business_message")
                    if b_msg:
                        self.handle_business_message(b_msg)
                        continue

                    # 3. Handle callback queries (inline button presses)
                    callback_query = update.get("callback_query")
                    if callback_query:
                        cb_data = callback_query.get("data", "")
                        cb_chat = callback_query.get("message", {}).get("chat", {})
                        cb_chat_id = cb_chat.get("id")
                        cb_sender = callback_query.get("from", {})
                        cb_name = cb_sender.get("first_name", "پژوهشگر")

                        # Answer the callback to remove loading spinner
                        self.tg.send_request("answerCallbackQuery", {
                            "callback_query_id": callback_query.get("id")
                        })

                        if cb_data == "action_scale_search" and cb_chat_id:
                            self.tg.send_message(
                                cb_chat_id,
                                "📋 نام پرسشنامه یا مقیاس مورد نظرتون رو ارسال کنید:\n"
                                "مثال: `/scale تاب‌آوری کانر` یا `/scale Beck Depression`"
                            )
                        elif cb_data == "action_quote" and cb_chat_id:
                            reply = self.handle_incoming_text(cb_chat_id, cb_name, "/quote")
                            if reply != "__SENT__":
                                self.tg.send_message(cb_chat_id, reply)
                        continue

                    message = update.get("message", {})
                    chat = message.get("chat", {})
                    chat_id = chat.get("id")
                    sender = message.get("from", {})
                    sender_name = sender.get("first_name", "پژوهشگر")

                    # Handle Document Upload
                    doc = message.get("document")
                    if doc and chat_id:
                        file_id = doc.get("file_id")
                        file_name = doc.get("file_name", "proposal.docx")
                        print(f"[+] Received document: {file_name} from {sender_name} ({chat_id})")
                        
                        # Get file path
                        file_info = self.tg.get_file_info(file_id)
                        if file_info and "file_path" in file_info:
                            local_dest = os.path.join(self.work_dir, f"{chat_id}_{file_name}")
                            if self.tg.download_file(file_info["file_path"], local_dest):
                                reply, pending = self.handle_proposal_submission(
                                    chat_id, sender_name, file_path=local_dest
                                )
                                self.tg.send_message(chat_id, reply)
                                if pending and self.admin_id:
                                    qid = list(self.pending_quotes.keys())[-1]
                                    adm_card = format_telegram_card(pending["quote"], include_admin_actions=True, quote_id=qid, lang="en")
                                    self.tg.send_message(self.admin_id, f"🔔 <b>New Proposal from {html.escape(sender_name)}:</b>\n\n{adm_card}", parse_mode="HTML")
                            else:
                                self.tg.send_message(chat_id, "خطا در دانلود فایل. لطفاً مجدداً ارسال فرمایید.")

                    # Handle Text Message
                    text = message.get("text")
                    if text and chat_id:
                        reply = self.handle_incoming_text(chat_id, sender_name, text)
                        if reply != "__SENT__":  # Skip if already sent with inline keyboard
                            self.tg.send_message(chat_id, reply)

            except Exception as e:
                print(f"[Polling Error] {e}")
                time.sleep(3.0)

            time.sleep(1.0)


def main():
    parser = argparse.ArgumentParser(description="Digital Twin Academic Consultant - Telegram Bot Daemon")
    parser.add_argument("--token", "-t", type=str, default="", help="Telegram Bot API Token from @BotFather")
    parser.add_argument("--admin-id", type=int, default=124911145, help="Saber's Telegram User ID (default: 124911145)")
    parser.add_argument("--auto-quote", action="store_true", help="Send quotations automatically without admin review")
    parser.add_argument("--test-mode", action="store_true", help="Run offline simulation test of all bot features")
    parser.add_argument("--webapp-url", type=str, default="", help="Public HTTPS URL for Telegram Mini App")
    parser.add_argument("--config", "-c", type=str, default=DEFAULT_CONFIG_PATH, help="Path to bot_config.json")

    args = parser.parse_args()

    token = args.token
    admin_id = args.admin_id
    webapp_url = args.webapp_url
    proxy_cfg = None

    admin_desk_chat_id = -1004331808205
    business_mode = True

    # Load from config if present
    if os.path.exists(args.config):
        try:
            with open(args.config, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                token = token or cfg.get("bot_token", "")
                admin_id = admin_id or cfg.get("admin_id", 124911145)
                admin_desk_chat_id = cfg.get("admin_desk_chat_id", admin_desk_chat_id)
                business_mode = cfg.get("business_mode", True)
                webapp_url = webapp_url or cfg.get("webapp_url", "")
                proxy_cfg = cfg.get("proxy")
        except Exception:
            pass

    bot = DigitalSaberBot(
        token=token,
        admin_id=admin_id,
        admin_desk_chat_id=admin_desk_chat_id,
        business_mode=business_mode,
        auto_quote=args.auto_quote,
        webapp_url=webapp_url,
        proxy=proxy_cfg
    )

    if args.test_mode or not token:
        bot.run_test_simulation()
    else:
        bot.start_polling()


if __name__ == "__main__":
    main()
