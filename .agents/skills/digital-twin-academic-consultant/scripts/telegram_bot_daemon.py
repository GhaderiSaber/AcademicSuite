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
6. Zero mandatory external pip dependencies (built on Python standard library).
7. Includes --test-mode to run end-to-end simulated scenarios offline.
"""

import os
import re
import sys
import time
import json
import html
import argparse
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

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
    """Lightweight Telegram Bot API client using standard library."""

    def __init__(self, token: str):
        self.token = token.strip()
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.file_base_url = f"https://api.telegram.org/file/bot{self.token}"

    def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/{method}"
        try:
            if params:
                data = json.dumps(params).encode("utf-8")
                req = urllib.request.Request(
                    url, data=data, headers={"Content-Type": "application/json"}
                )
            else:
                req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=35) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if result.get("ok"):
                    return result
                else:
                    print(f"[Telegram API Error] {result.get('description')}")
                    return None
        except Exception as e:
            print(f"[HTTP Error] {method}: {e}")
            return None

    def send_message(self, chat_id: int, text: str, parse_mode: str = "Markdown", reply_markup: Optional[Dict[str, Any]] = None) -> bool:
        payload: Dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        res = self.send_request("sendMessage", payload)
        return res is not None

    def get_updates(self, offset: int = 0, timeout: int = 25) -> List[Dict[str, Any]]:
        payload = {
            "offset": offset,
            "timeout": timeout,
            "allowed_updates": ["message", "callback_query"]
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
            with urllib.request.urlopen(url, timeout=60) as resp, open(dest_path, "wb") as f:
                f.write(resp.read())
            return True
        except Exception as e:
            print(f"[Download Error] {file_path}: {e}")
            return False


class DigitalSaberBot:
    """Digital Twin of Saber Ghaderi for Telegram."""

    def __init__(
        self,
        token: str = "",
        admin_id: int = 124911145,
        auto_quote: bool = False,
        work_dir: Optional[str] = None
    ):
        self.token = token
        self.admin_id = admin_id
        self.auto_quote = auto_quote
        self.work_dir = work_dir or os.path.join(os.path.dirname(__file__), "bot_storage")
        os.makedirs(self.work_dir, exist_ok=True)
        
        self.persona = load_persona()
        self.tg = TelegramApiClient(self.token) if self.token else None
        self.pending_quotes: Dict[str, Dict[str, Any]] = {}
        self.quote_counter = 100
        self.running = True

    def generate_welcome_message(self, user_first_name: str = "پژوهشگر گرامی") -> str:
        """Create greeting message explaining capabilities."""
        msg = (
            f"سلام و درود، {user_first_name} وقتتون بخیر.\n"
            "من دستیار هوشمند و همزاد تخصصی **صابر قادری** هستم؛ پژوهشگر دکتری روان‌شناسی، متخصص متدولوژی، روان‌سنجی و تحلیل‌های آماری پیشرفته.\n\n"
            "✨ **خدمات تخصصی قابل ارائه:**\n"
            "1. 📊 **بررسی پروپوزال و استعلام هزینه:** ارسال فایل پروپوزال (`.docx` یا `.pdf`) جهت دریافت پیش‌فاکتور تفکیکی و زمان‌بندی دقیق.\n"
            "2. 📋 **بانک پرسشنامه‌ها:** جستجوی فوری ۴,۸۸۰ آزمون روان‌شناختی همراه با کلید نمره‌گذاری و روایی/پایایی با دستور `/scale`.\n"
            "3. 🔬 **مشاوره روش‌شناسی و آماری:** پاسخ به پرسش‌های آماری (AMOS، SPSS، SmartPLS، G*Power، تحلیل فرضیات و مدل‌یابی).\n"
            "4. 📝 **ویرایش و کاهش همانندجویی:** بازنویسی علمی و کاهش درصد سمیم‌نور و ایران‌داک.\n\n"
            "💡 برای شروع، می‌توانید فایل پروپوزال یا سوال تخصصی‌تون رو مستقیماً ارسال بفرمایید یا دستور `/help` رو لمس کنید."
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
        if admin_chat_id != self.admin_id:
            return "Unauthorized access. Admin privileges required."

        # Approve: /approve_Q101
        m_app = re.match(r"^/approve_(Q\d+)", command_text)
        if m_app:
            qid = m_app.group(1)
            if qid in self.pending_quotes:
                item = self.pending_quotes[qid]
                client_chat_id = item["chat_id"]
                tg_card = format_telegram_card(item["quote"], lang="fa")
                
                # Send to client if live
                if self.tg:
                    self.tg.send_message(client_chat_id, tg_card, parse_mode="HTML")
                
                item["status"] = "approved"
                return f"✅ Quotation {qid} approved and dispatched to {item['sender_name']}."
            return f"Quotation {qid} not found."

        # Adjust: /adjust_Q101_8500000
        m_adj = re.match(r"^/adjust_(Q\d+)_(\d+)", command_text)
        if m_adj:
            qid = m_adj.group(1)
            new_price = int(m_adj.group(2))
            if qid in self.pending_quotes:
                item = self.pending_quotes[qid]
                item["quote"]["total_price_tomans"] = new_price
                item["quote"]["total_price_formatted"] = f"{new_price:,.0f} تومان"
                client_chat_id = item["chat_id"]
                tg_card = format_telegram_card(item["quote"], lang="fa")
                
                if self.tg:
                    self.tg.send_message(client_chat_id, tg_card, parse_mode="HTML")
                
                item["status"] = "approved_adjusted"
                return f"✅ Quotation {qid} adjusted to {new_price:,.0f} Tomans and dispatched to {item['sender_name']}."
            return f"Quotation {qid} not found."

        return "Invalid command. Format: <code>/approve_Q101</code> or <code>/adjust_Q101_8000000</code>"

    def handle_incoming_text(self, chat_id: int, sender_name: str, text: str) -> str:
        """Route and answer text queries."""
        clean = text.strip()

        # Admin commands
        if chat_id == self.admin_id and clean.startswith(("/approve_", "/adjust_", "/reject_")):
            return self.handle_admin_action(chat_id, clean)

        # Standard commands & greetings
        greeting_words = ["/start", "سلام", "درود", "صبح بخیر", "عصر بخیر", "شب بخیر", "وقت بخیر"]
        if clean in ["/start", "/help"] or (len(clean.split()) <= 4 and any(clean.startswith(gw) or clean == gw for gw in greeting_words)):
            return self.generate_welcome_message(sender_name)

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

        print("\n✅ All 5 simulation tests executed successfully!")
        return {"status": "success", "events": events}

    def start_polling(self):
        """Start long-polling daemon loop."""
        if not self.tg:
            print("[-] Telegram Bot Token is not configured. Run with --test-mode or set token in config.")
            return

        print(f"[*] Digital Twin Saber Bot started. Admin ID: {self.admin_id}")
        offset = 0

        while self.running:
            try:
                updates = self.tg.get_updates(offset=offset)
                for update in updates:
                    update_id = update.get("update_id", 0)
                    offset = max(offset, update_id + 1)

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
    parser.add_argument("--config", "-c", type=str, default=DEFAULT_CONFIG_PATH, help="Path to bot_config.json")

    args = parser.parse_args()

    token = args.token
    admin_id = args.admin_id

    # Load from config if present
    if os.path.exists(args.config):
        try:
            with open(args.config, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                token = token or cfg.get("bot_token", "")
                admin_id = admin_id or cfg.get("admin_id", 124911145)
        except Exception:
            pass

    bot = DigitalSaberBot(
        token=token,
        admin_id=admin_id,
        auto_quote=args.auto_quote
    )

    if args.test_mode or not token:
        bot.run_test_simulation()
    else:
        bot.start_polling()


if __name__ == "__main__":
    main()
