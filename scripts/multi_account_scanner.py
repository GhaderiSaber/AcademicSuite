#!/usr/bin/env python3
"""
Multi-Account Telegram & Google Drive Scanner for Saber Ghaderi
--------------------------------------------------------------
Scans both connected accounts:
1. Account 1: @GhaderiSaber (+989143932354)
2. Account 2: @SaberGhaderi (+989142564775)

Collects read and unread client chats, archives attachments (.docx, .pdf, .sav, .xlsx),
analyzes proposals, provisions standard 4-tier Google Drive project folders,
and posts an executive report to the Academic Desk Telegram group.
"""

import os
import sys
import re
import asyncio
from datetime import datetime
from typing import Dict, List, Any

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SUITE_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SKILL_SCRIPTS = os.path.join(SUITE_ROOT, ".agents/skills/digital-twin-academic-consultant/scripts")
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)

import html
from telethon import TelegramClient, Button
from telethon.tl.types import User
from project_drive_manager import (
    ProjectDriveManager,
    sanitize_filename,
    clean_drive_display_path,
    format_client_mention_html
)
from proposal_price_estimator import (
    analyze_proposal_text,
    calculate_quotation,
    format_telegram_card,
    load_persona
)

# Configuration
CONFIG_PATH = os.path.join(SKILL_SCRIPTS, "telethon_config.json")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    import json
    CONFIG = json.load(f)

API_ID = CONFIG.get("api_id", 6)
API_HASH = CONFIG.get("api_hash", "eb06d4abfb49dc3eeb1aeb98ae0f581e")
PROXY = ("socks5", "127.0.0.1", 3066)
DESK_GROUP_ID = CONFIG.get("admin_desk_chat_id", -1004331808205)
BOT_TOKEN = CONFIG.get("bot_token", "8958161324:AAFAxyoZlfVbK8O4dT5xGHBgEqrQIeoidGA")

# Saber's own user IDs and service IDs to exclude from client lists
SELF_AND_SERVICE_IDS = {124911145, 6328062294, 777000}

ACCOUNTS = [
    {
        "id_tag": "acc1",
        "label": "Main Account (@GhaderiSaber)",
        "phone": "+989143932354",
        "session": os.path.join(SKILL_SCRIPTS, "saber_userbot")
    },
    {
        "id_tag": "acc2",
        "label": "Second Account (@SaberGhaderi)",
        "phone": "+989142564775",
        "session": os.path.join(SKILL_SCRIPTS, "saber_second_userbot")
    }
]

def extract_text_from_file(file_path: str) -> str:
    """Extract plain text from docx, pdf, or txt files."""
    if not os.path.exists(file_path):
        return ""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return ""
    elif ext == ".docx":
        try:
            import docx
            doc = docx.Document(file_path)
            # Extract both paragraph text and any embedded math / text
            texts = []
            for p in doc.paragraphs:
                pt = "".join([e.text or "" for e in p._p.iter() if e.tag.endswith("}t")])
                if pt.strip():
                    texts.append(pt.strip())
            return "\n".join(texts)
        except Exception:
            return ""
    elif ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            return "\n".join([page.extract_text() or "" for page in reader.pages])
        except Exception:
            return ""
    return ""


async def scan_single_account(acc_info: Dict[str, Any], drive_mgr: ProjectDriveManager, persona: Dict[str, Any]):
    """Scan one Telegram user account for both unread and recent client chats."""
    label = acc_info["label"]
    session_path = acc_info["session"]
    print(f"\n=======================================================")
    print(f"[*] Connecting to: {label}...")
    print(f"=======================================================")

    client = TelegramClient(session_path, API_ID, API_HASH, proxy=PROXY)
    await client.connect()

    if not await client.is_user_authorized():
        print(f"[-] Error: Account {label} is not authorized! Skipping.")
        await client.disconnect()
        return {"account": label, "error": "Not authorized", "clients": []}

    me = await client.get_me()
    print(f"[✓] Connected: {me.first_name} {me.last_name or ''} (@{me.username}) [ID: {me.id}]")

    print("[*] Retrieving dialogs (scanning up to 150 items)...")
    dialogs = await client.get_dialogs(limit=150)
    
    # Filter out non-user, self, bots, and ignored non-academic contacts
    ignored_reg = drive_mgr.load_ignored_registry()
    ignored_ids = set(ignored_reg.get("telegram_ids", []))
    ignored_usernames = set(ignored_reg.get("usernames", []))
    ignored_names = set(ignored_reg.get("folder_names", []))

    client_dialogs = [
        d for d in dialogs 
        if d.is_user and not d.entity.is_self and not d.entity.bot 
        and d.id not in SELF_AND_SERVICE_IDS
        and d.id not in ignored_ids
        and (getattr(d.entity, "username", "") or "").lstrip("@").lower() not in ignored_usernames
        and sanitize_filename(d.name) not in ignored_names
    ]

    print(f"[+] Found {len(client_dialogs)} real academic project conversation(s).")
    scanned_results = []

    for d in client_dialogs:
        cname = d.name or f"Client_{d.id}"
        uname = getattr(d.entity, "username", None)
        unread = d.unread_count
        unread_str = f"🔥 {unread} پیام جدید" if unread > 0 else "خوانده‌شده"

        print(f"\n  ➤ بررسی مراجع: {cname} (@{uname or 'بدون یوزرنیم'}) [{unread_str}]")

        # Collect unread message texts if any
        unread_messages = []
        if unread > 0:
            async for m in client.iter_messages(d.entity, limit=unread):
                if m.message:
                    unread_messages.append(m.message.strip())

        # Archive chat and download documents
        try:
            res = await drive_mgr.save_client_chat_and_files(
                client=client,
                entity=d.entity,
                client_name=cname,
                client_id=d.id,
                username=uname,
                limit_messages=max(unread + 25, 40),
                download_files=True
            )
            if res.get("skipped_non_project") or not res.get("project_dir"):
                print(f"    [-] مخاطب غیرپژوهشی نادیده گرفته شد.")
                continue

            p_dir = res["project_dir"]
            msg_count = res["messages_count"]
            file_count = res["files_count"]
            print(f"    [+] همگام‌سازی درایو: {p_dir}")
            print(f"    [+] پیام‌ها: {msg_count} | فایل‌های پیوست: {file_count}")

            # Check for proposals in raw inputs
            raw_dir = os.path.join(p_dir, "01_raw_inputs")
            detected_proposal = None
            for root, _, files in os.walk(raw_dir):
                for f in sorted(files):
                    ext = os.path.splitext(f)[1].lower()
                    if ext in [".docx", ".pdf", ".txt"] and not f.startswith("~$"):
                        fpath = os.path.join(root, f)
                        ftext = extract_text_from_file(fpath)
                        if len(ftext) > 80 and any(w in ftext for w in ["عنوان", "فرضیه", "پروپوزال", "جامعه", "نمونه", "متغیر", "فصل چهار"]):
                            print(f"    [📄] پروپوزال / رساله شناسایی شد در فایل: {f}")
                            an = analyze_proposal_text(ftext)
                            q = calculate_quotation(an, persona)
                            card = format_telegram_card(q)
                            detected_proposal = {
                                "file_name": f,
                                "analysis": an,
                                "quotation": q,
                                "card": card
                            }
                            # Save draft deliverable
                            draft_path = os.path.join(p_dir, "03_deliverables", "telegram_response_draft.md")
                            with open(draft_path, "w", encoding="utf-8") as df:
                                df.write(f"# پیش‌نویس پیش‌فاکتور - {cname}\n\n{card}\n")
                            break
                if detected_proposal:
                    break

            # If no proposal in files, check if unread text has a proposal inquiry
            if not detected_proposal and unread_messages:
                full_unread_text = "\n".join(unread_messages)
                if len(full_unread_text) > 80 and any(w in full_unread_text for w in ["عنوان", "فرضیه", "پروپوزال", "جامعه", "نمونه", "متغیر", "مدل"]):
                    an = analyze_proposal_text(full_unread_text)
                    q = calculate_quotation(an, persona)
                    card = format_telegram_card(q)
                    detected_proposal = {
                        "file_name": "متن پیام‌های ارسال‌شده",
                        "analysis": an,
                        "quotation": q,
                        "card": card
                    }
                    draft_path = os.path.join(p_dir, "03_deliverables", "telegram_response_draft.md")
                    with open(draft_path, "w", encoding="utf-8") as df:
                        df.write(f"# پیش‌نویس پیش‌فاکتور - {cname}\n\n{card}\n")

            scanned_results.append({
                "client_name": cname,
                "username": f"@{uname}" if uname else "نامشخص",
                "telegram_id": d.id,
                "unread_count": unread,
                "unread_messages": unread_messages,
                "project_dir": p_dir,
                "messages_count": msg_count,
                "files_count": file_count,
                "detected_proposal": detected_proposal
            })
        except Exception as err:
            print(f"    [-] خطا در بررسی مراجع {cname}: {err}")

    await client.disconnect()
    return {
        "account": label,
        "username": f"@{me.username}",
        "phone": f"+{me.phone}",
        "clients": scanned_results
    }


async def main():
    drive_mgr = ProjectDriveManager(CONFIG)
    persona = load_persona()
    print(f"[*] Google Drive Operational Root: {drive_mgr.work_dir}")

    # 1. Scan both accounts
    all_reports = []
    for acc in ACCOUNTS:
        rep = await scan_single_account(acc, drive_mgr, persona)
        all_reports.append(rep)

    # 2. Build consolidated Markdown Report
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    total_unread = 0
    total_proposals = 0
    total_synced_clients = 0
    urgent_clients = []
    proposal_clients = []

    for rep in all_reports:
        for c in rep.get("clients", []):
            total_synced_clients += 1
            if c["unread_count"] > 0:
                total_unread += c["unread_count"]
                urgent_clients.append((rep["account"], c))
            if c["detected_proposal"]:
                total_proposals += 1
                proposal_clients.append((rep["account"], c))

    md_lines = [
        f"# 📊 گزارش جامع پویش و همگام‌سازی دو اکانت تلگرام صابر قادری",
        f"**زمان پویش:** `{now_str}`  ",
        f"**مسیر عملیاتی گوگل درایو:** `{drive_mgr.work_dir}`  ",
        f"**تعداد کل مراجعین همگام‌شده:** `{total_synced_clients}` نفر  ",
        f"**کل پیام‌های خوانده‌نشده:** `{total_unread}` پیام  ",
        f"**پروپوزال‌های شناسایی و قیمت‌گذاری‌شده:** `{total_proposals}` مورد\n",
        "---"
    ]

    # Section 1: Urgent Unread Messages
    md_lines.append("\n## 🚨 پیام‌های خوانده‌نشده و نیازمند پاسخ فوری\n")
    if urgent_clients:
        md_lines.append("| اکانت | مراجع | شناسه | پیام‌های جدید | آخرین پیام / خواسته مراجع | مسیر درایو |")
        md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for acc_name, c in urgent_clients:
            last_msg = c["unread_messages"][0].replace("\n", " ") if c["unread_messages"] else "بدون متن"
            if len(last_msg) > 60:
                last_msg = last_msg[:57] + "..."
            md_lines.append(
                f"| **{acc_name}** | {c['client_name']} ({c['username']}) | `{c['telegram_id']}` | **{c['unread_count']}** | {last_msg} | [`پوشه پروژه`]({c['project_dir']}) |"
            )
    else:
        md_lines.append("✅ *هیچ پیام خوانده‌نشده‌ای در هیچ‌یک از دو اکانت وجود ندارد.*")

    # Section 2: Detected Proposals and Price Estimations
    md_lines.append("\n\n## 📄 پروژه‌ها و پروپوزال‌های شناسایی‌شده همراه با برآورد قیمت\n")
    if proposal_clients:
        md_lines.append("| مراجع | عنوان / فایل پروپوزال | طرح پژوهش | متغیرها | برآورد هزینه (تومان) | وضعیت پیش‌فاکتور |")
        md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for acc_name, c in proposal_clients:
            prop = c["detected_proposal"]
            fname = prop["file_name"]
            an = prop["analysis"]
            q = prop["quotation"]
            design = an.get("research_design", "نامشخص")
            vars_cnt = len(an.get("variables", []))
            vars_str = f"{vars_cnt} متغیر" if vars_cnt > 0 else "استخراج‌شده"
            price = q.get("total_price_formatted", "نامشخص")
            md_lines.append(
                f"| **{c['client_name']}** ({c['username']}) | `{fname}` | {design} | {vars_str} | **{price}** | [مشاهده پیش‌نویس]({os.path.join(c['project_dir'], '03_deliverables', 'telegram_response_draft.md')}) |"
            )
    else:
        md_lines.append("_هیچ پروپوزال جدیدی شناسایی نشد._")

    # Section 3: Detailed Breakdown by Account
    md_lines.append("\n\n## 📁 جزئیات کامل مراجعین به تفکیک اکانت")
    for rep in all_reports:
        acc_label = rep["account"]
        clients = rep.get("clients", [])
        md_lines.append(f"\n### 📱 {acc_label} ({rep.get('username', '')} | {rep.get('phone', '')})")
        if not clients:
            md_lines.append("_هیچ گفتگوی کاربری در این اکانت یافت نشد._\n")
            continue

        for c in clients:
            unread_cnt = c["unread_count"]
            unread_badge = f"🔴 **{unread_cnt} پیام جدید**" if unread_cnt > 0 else "🟢 به‌روز"
            prop_badge = ""
            if c["detected_proposal"]:
                q = c["detected_proposal"]["quotation"]
                price_str = q.get("total_price_formatted", "نامشخص")
                prop_badge = f" | 📄 **پروپوزال: {price_str}**"

            md_lines.append(f"#### 👤 {c['client_name']} ({c['username']} | ID: `{c['telegram_id']}`)")
            md_lines.append(f"- **وضعیت:** {unread_badge}{prop_badge}")
            md_lines.append(f"- **آمار:** {c['messages_count']} پیام آرشیو شده | {c['files_count']} فایل پیوست")
            md_lines.append(f"- **مسیر پوشه در گوگل درایو:**\n  `{c['project_dir']}`")
            if c["unread_messages"]:
                md_lines.append("- **پیام‌های جدید:**")
                for um in c["unread_messages"][:3]:
                    md_lines.append(f"  > {um}")
            if c["detected_proposal"]:
                md_lines.append(f"- **فایل طرح:** `{c['detected_proposal']['file_name']}`")
            md_lines.append("")

    report_path = os.path.join(SUITE_ROOT, "MULTI_ACCOUNT_SCAN_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"\n[+] Master scan report saved to: {report_path}")

    # 3. Post summary into Academic Desk group via Assistant Bot
    print("\n[*] Posting executive summary to Academic Desk group via @SaberAcademicBot...")
    bot_session = os.path.join(SKILL_SCRIPTS, "userbot_storage/bot_session")
    bot_client = TelegramClient(bot_session, API_ID, API_HASH, proxy=PROXY)
    await bot_client.start(bot_token=BOT_TOKEN)

    urgent_list_str = ""
    if urgent_clients:
        urgent_list_str = "\n🚨 <b>Unread Messages Requiring Attention:</b>\n"
        for acc_name, c in urgent_clients:
            um_snip = html.escape(c["unread_messages"][0][:50]) if c["unread_messages"] else "..."
            c_link = format_client_mention_html(c['client_name'], username=c.get('username'), client_id=c.get('telegram_id'))
            urgent_list_str += f"• {c_link} ({c['unread_count']} new): «{um_snip}»\n"

    clean_work_dir = clean_drive_display_path(drive_mgr.work_dir)
    desk_summary = (
        f"📊 <b>Multi-Account & Google Drive Sync Report:</b>\n\n"
        f"• Account 1: <b>@GhaderiSaber</b> (+989143932354)\n"
        f"• Account 2: <b>@SaberGhaderi</b> (+989142564775)\n"
        f"─────────────────────\n"
        f"👥 <b>Total Clients Synced:</b> {total_synced_clients}\n"
        f"📬 <b>Unread Messages:</b> {total_unread}\n"
        f"📄 <b>Proposals & Quotations:</b> {total_proposals}\n"
        f"{urgent_list_str}\n"
        f"📁 Google Drive: <code>{html.escape(clean_work_dir)}</code>\n"
        f"📄 Detailed Report: <code>MULTI_ACCOUNT_SCAN_REPORT.md</code>"
    )

    buttons = [
        [Button.inline("📂 Project Catalog", b"cmd_projects")],
        [Button.inline("🔄 Rescan Messages", b"cmd_unread")]
    ]

    try:
        sent = await bot_client.send_message(DESK_GROUP_ID, desk_summary, buttons=buttons, parse_mode="html")
        print(f"[+] Posted summary to Academic Desk! Message ID: {sent.id}")
    except Exception as e:
        print(f"[-] Could not post to desk group: {e}")

    await bot_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
