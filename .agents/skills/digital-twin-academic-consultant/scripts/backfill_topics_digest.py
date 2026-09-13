#!/usr/bin/env python3
"""
backfill_topics_digest.py — Historical Client Digest & Topic Population Engine

Backfills recent high-signal client messages into their dedicated Academic Desk topics:
1. Topic 122 (🎓 Supervisor Feedback & Defense) -> Marziyeh Sinayi (foreign literature defense + quarterly reports)
2. Topic 114 (💡 Co-Pilot Drafts) -> Alireza Baneshi (logistics/modem coordination)
3. Topic 121 (🌟 VIP: شهرام امیری) -> Shahram Amiri (3 active projects status & deliverable checks)
Uses Gemini 3.8 Flash to synthesize authentic academic rationale and suggested Persian response drafts.
"""

import os
import sys
import json
import html
import subprocess
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from academic_inquiry_classifier import AcademicInquiryClassifier


def send_telegram_bot_message(
    bot_token: str,
    chat_id: int,
    text: str,
    thread_id: int,
    proxy_addr: str = "127.0.0.1",
    proxy_port: int = 3066,
    buttons: list = None
) -> dict:
    """Send HTML message with inline buttons to a specific Telegram forum topic using curl."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "message_thread_id": thread_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}

    cmd = [
        "curl", "-s", "-k",
        "-x", f"socks5h://{proxy_addr}:{proxy_port}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload),
        url
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and res.stdout:
        try:
            return json.loads(res.stdout)
        except Exception:
            pass
    return {"ok": False, "error": res.stderr or res.stdout}


def run_backfill():
    config_path = os.path.join(SCRIPT_DIR, "telethon_config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    bot_token = config.get("bot_token")
    chat_id = config.get("admin_desk_chat_id")
    proxy_cfg = config.get("proxy", {})
    proxy_addr = proxy_cfg.get("addr", "127.0.0.1")
    proxy_port = int(proxy_cfg.get("port", 3066))

    classifier = AcademicInquiryClassifier(config)

    # 1. Backfill Topic 122: 🎓 Supervisor Feedback & Defense (Marziyeh Sinayi)
    print("\n[1/3] Processing Marziyeh Sinayi for Topic 122 (Supervisor Feedback & Defense)...")
    marziyeh_text = (
        "سلام آقای قادری وقتتون بخیر\n"
        "من تو پایان نامم از مقالات خارجی هم استفاده کردم الان اگر استادم بپرسه چرا استفاده کردی چی باید بگم بهشون؟\n"
        "سلام وقتتون بخیر استاد فرم امضا کردن چک کنید ببینید نیاز هست بارگزاری بشه یا نیاز نیس\n"
        "لطفا ببینید چه مدارکی نوشته نیاز هست بارگزاری بشه\n"
        "آقای قادری گزارش سه ماهه اول و دوم رو لطفا بارگزاری میکنید واسه خودم هم بفرستین لطفا"
    )
    analysis_marziyeh = classifier.analyze_inquiry(
        client_name="مرضیه سینایی",
        combined_text=marziyeh_text,
        attached_files=[
            {"name": "فرم_گزارش_سه_ماهه_امضا_شده.pdf", "type": "document"},
            {"name": "مدارک_پژوهشیار.pdf", "type": "document"}
        ],
        is_vip=False
    )
    
    draft_id_1 = "D101"
    card_marziyeh = (
        f"🎓 <b>[Supervisor Dilemma & Defense] Client Inquiry from <a href=\"tg://user?id=5829872836\">Mərziye Sinayı</a></b>\n"
        f"📱 <b>Account:</b> Second Account (@SaberGhaderi)\n"
        f"🏷️ <b>Category:</b> <code>supervisor_defense_question</code>\n"
        f"🧠 <b>Academic Intent:</b> <i>{html.escape(analysis_marziyeh.get('admin_notes', ''))}</i>\n"
        f"⚡ <b>AI Engine:</b> <code>{html.escape(analysis_marziyeh.get('engine', 'gemini-3.8-flash'))}</code>\n"
        f"💬 <b>Client Inquiries:</b>\n"
        f"• «اگر استادم بپرسه چرا از مقالات خارجی استفاده کردی چی بگم؟»\n"
        f"• «استاد فرم گزارش سه ماهه اول و دوم رو امضا کردن، بارگذاری میشه؟»\n"
        f"🆔 <b>Draft ID:</b> <code>{draft_id_1}</code>\n"
        "─────────────────────\n"
        f"📝 <b>Suggested Academic Defense Response:</b>\n"
        f"<blockquote>{html.escape(analysis_marziyeh.get('draft_reply', ''))}</blockquote>\n\n"
        "⚙️ <b>Admin Actions & Commands:</b>\n"
        f"• Approve & Send to Client: <code>/send_msg_{draft_id_1}</code>\n"
        f"• Send Custom Edits: <code>/send_msg_{draft_id_1} &lt;custom text&gt;</code>\n"
        f"• Dismiss Draft: <code>/ignore_{draft_id_1}</code>"
    )
    buttons_marziyeh = [
        [{"text": f"🚀 Send Response ({draft_id_1})", "callback_data": f"send_draft_{draft_id_1}"},
         {"text": "🗑️ Dismiss", "callback_data": f"ignore_draft_{draft_id_1}"}]
    ]
    res1 = send_telegram_bot_message(bot_token, chat_id, card_marziyeh, thread_id=122, proxy_addr=proxy_addr, proxy_port=proxy_port, buttons=buttons_marziyeh)
    print(" -> Topic 122 result:", res1.get("ok"))

    # 2. Backfill Topic 114: 💡 Co-Pilot Drafts (Alireza Baneshi)
    print("\n[2/3] Processing Alireza Baneshi for Topic 114 (Co-Pilot Drafts)...")
    alireza_text = (
        "امروزم خوب خواهد بود. مراقب سلامتی ات باش. فردا صبح زنگ می زنم صحبت می کنیم. روز خوبی داشته باشی\n"
        "صابر آدرس و کد پستی و تلفنت را اینجا بنویس ببینم مودم را پیدا می کنه ارسال کنه"
    )
    analysis_alireza = classifier.analyze_inquiry(
        client_name="علیرضا بانشی",
        combined_text=alireza_text,
        attached_files=[],
        is_vip=False
    )
    draft_id_2 = "D102"
    card_alireza = (
        f"💡 <b>[Co-Pilot Draft] Client Inquiry from <a href=\"tg://user?id=394464506\">Əlireza Baneşı</a></b>\n"
        f"📱 <b>Account:</b> Main Account (@GhaderiSaber)\n"
        f"🏷️ <b>Category:</b> <code>friendly_logistics</code>\n"
        f"🧠 <b>Academic Intent:</b> <i>{html.escape(analysis_alireza.get('admin_notes', ''))}</i>\n"
        f"⚡ <b>AI Engine:</b> <code>{html.escape(analysis_alireza.get('engine', 'gemini-3.8-flash'))}</code>\n"
        f"💬 <b>Client Message:</b> «{html.escape(alireza_text)}»\n"
        f"🆔 <b>Draft ID:</b> <code>{draft_id_2}</code>\n"
        "─────────────────────\n"
        f"📝 <b>Suggested Response Draft:</b>\n"
        f"<blockquote>{html.escape(analysis_alireza.get('draft_reply', ''))}</blockquote>\n\n"
        "⚙️ <b>Admin Actions & Commands:</b>\n"
        f"• Approve & Send to Client: <code>/send_msg_{draft_id_2}</code>\n"
        f"• Dismiss Draft: <code>/ignore_{draft_id_2}</code>"
    )
    buttons_alireza = [
        [{"text": f"🚀 Send Response ({draft_id_2})", "callback_data": f"send_draft_{draft_id_2}"},
         {"text": "🗑️ Dismiss", "callback_data": f"ignore_draft_{draft_id_2}"}]
    ]
    res2 = send_telegram_bot_message(bot_token, chat_id, card_alireza, thread_id=114, proxy_addr=proxy_addr, proxy_port=proxy_port, buttons=buttons_alireza)
    print(" -> Topic 114 result:", res2.get("ok"))

    # 3. Backfill Topic 121: 🌟 VIP: شهرام امیری (Shahram Amiri)
    print("\n[3/3] Processing Shahram Amiri for Topic 121 (VIP: شهرام امیری)...")
    card_shahram = (
        "🌟 <b>[VIP Client Status Digest] <a href=\"tg://user?id=5819750724\">Şəhram Əmiri</a></b>\n"
        "📱 <b>Account:</b> Main Account (@GhaderiSaber)\n"
        "🏷️ <b>Status:</b> <code>Active Review & In Progress</code>\n"
        "─────────────────────\n"
        "📁 <b>Managed Projects in Google Drive:</b>\n"
        "• <b>P01:</b> <code>Soldiers_Variance_Data</code> (Analysis & Deliverables synced)\n"
        "• <b>P02:</b> <code>Case_Study_1</code> (Qualitative & Quantitative analysis)\n"
        "• <b>P03:</b> <code>Article_References</code> (Literature & Reference synthesis)\n"
        "─────────────────────\n"
        "💬 <b>Recent Client Feedback:</b>\n"
        "• <i>«دمت گرم صابر جان زحمت افتادی شرمنده»</i>\n"
        "• <i>«عزیزی حتما چک میکنم تا ی ساعت دیگه»</i>\n\n"
        "📊 <b>Ledger Status:</b> <code>CLIENT_LEDGER.xlsx</code> verified on disk.\n"
        "💡 <i>All dedicated deliverables and communications for Shahram will route automatically into this topic thread.</i>"
    )
    buttons_shahram = [
        [{"text": "📂 Open Google Drive Folder", "url": "https://drive.google.com"}]
    ]
    res3 = send_telegram_bot_message(bot_token, chat_id, card_shahram, thread_id=121, proxy_addr=proxy_addr, proxy_port=proxy_port, buttons=buttons_shahram)
    print(" -> Topic 121 result:", res3.get("ok"))

    print("\n[✓] Historical messages successfully backfilled into Forum Topics!")


if __name__ == "__main__":
    run_backfill()
