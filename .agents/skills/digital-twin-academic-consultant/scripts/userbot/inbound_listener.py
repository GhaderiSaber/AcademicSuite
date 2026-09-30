"""Inbound message listener with conversational debouncing for Telethon Userbot."""

from __future__ import annotations

import asyncio
import os
import sys
from typing import Any, Optional

USERBOT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.abspath(os.path.join(USERBOT_DIR, ".."))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from telethon import events

try:
    from telethon.tl.types import User, MessageService
except ImportError:
    User = None
    MessageService = None

try:
    from telethon.tl.custom import Button
except ImportError:
    Button = None

from project_drive_manager import (
    clean_drive_display_path,
    format_client_mention_html,
    resolve_media_details,
)
from userbot.utils import is_valid_telegram_button_url


def setup_inbound_listeners(bot: Any, me: Any = None) -> None:
    """Setup inbound message listeners on personal accounts with 40s debouncing."""
    effective_me = me or getattr(bot, "me", None)

    def setup_inbound_listener(client_inst: Any, account_label: str) -> None:
        @client_inst.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
        async def client_handler(event: Any) -> None:
            # 1. Ignore Telegram service messages
            if (MessageService is not None and isinstance(event.message, MessageService)) or getattr(event.message, "action", None) is not None:
                return

            sender = await event.get_sender()
            if User is not None and not isinstance(sender, User):
                return
            if getattr(sender, "is_self", False) or getattr(sender, "bot", False):
                return
            if getattr(sender, "id", None) in [124911145, 6328062294, 777000]:
                return

            client_name = f"{getattr(sender, 'first_name', '')} {getattr(sender, 'last_name', '') or ''}".strip()
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

            print(f"[!] [{account_label}] New DM from contact {client_name} (ID: {sender.id}): {preview}")

            # Check if contact is in the excluded non-academic contacts registry
            is_excluded = bot.project_manager.is_ignored(client_name, sender.id, sender.username)
            if is_excluded:
                print(f"[-] Ignoring message from excluded personal contact {client_name} ({sender.id})")
                return

            # Check whether an academic project already exists on disk or if client is VIP
            existing_dir = bot.project_manager.find_existing_project_by_client(
                client_name, client_id=sender.id, username=sender.username
            )
            is_vip = bot.project_manager.is_vip_client(
                client_name, client_id=sender.id, username=sender.username
            )

            # For contacts without an existing project or VIP status, require an affirmative academic signal
            if not existing_dir and not is_vip:
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
                    print(f"[*] Skipping folder provisioning for non-academic / unverified contact {client_name} ({sender.id})")
                    return

            # Ensure client's Google Drive project folder is provisioned
            paths = bot.project_manager.provision_project(
                client_name=client_name,
                client_id=sender.id,
                username=sender.username,
                phone=getattr(sender, "phone", None)
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
                    await bot.send_to_desk(restored_card, parse_mode="html", topic_key="inquiries")
                except Exception as e:
                    print(f"[-] Error sending restoration alert: {e}")

            # Bot-specific commands (/start, /help, /dashboard, /webapp, /scale)
            if effective_me and getattr(effective_me, "bot", False):
                webapp_url = bot.config.get("webapp_url", "")
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
                        f"سلام و درود، وقت شما بخیر {getattr(sender, 'first_name', '')} گرامی.\n\n"
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
                    local_path = await bot.project_manager.save_single_file(
                        msg=event.message,
                        client_name=client_name,
                        client_id=sender.id,
                        username=sender.username
                    )
                except Exception as err:
                    print(f"[-] Error saving incoming client file: {err}")

            # 2. Real-time transcript appending directly to Google Drive chat_transcript.md & chat_history.json
            try:
                bot.project_manager.append_message_to_history(
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
            async with bot.burst_lock:
                if burst_key in bot.burst_buffers:
                    prev_task = bot.burst_buffers[burst_key].get("task")
                    if prev_task and not prev_task.done():
                        prev_task.cancel()
                    buf = bot.burst_buffers[burst_key]
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
                    bot.burst_buffers[burst_key] = buf

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
                buf["task"] = asyncio.create_task(bot._process_client_burst(burst_key, delay=40))

    if bot.client:
        setup_inbound_listener(bot.client, "Main Account (@GhaderiSaber)")
    if getattr(bot, "client2", None):
        setup_inbound_listener(bot.client2, "Second Account (@SaberGhaderi)")
