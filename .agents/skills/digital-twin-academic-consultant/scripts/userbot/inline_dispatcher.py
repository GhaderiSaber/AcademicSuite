"""Inline query dispatcher for Telegram bot."""

from __future__ import annotations

import html
import os
import re
import sys
from typing import Any, List, Optional

USERBOT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.abspath(os.path.join(USERBOT_DIR, ".."))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from telethon import events

try:
    RESOLVER_SCRIPT_DIR = os.path.abspath(
        os.path.join(SCRIPTS_DIR, "..", "..", "psychometric-scale-resolver", "scripts")
    )
    if os.path.isdir(RESOLVER_SCRIPT_DIR) and RESOLVER_SCRIPT_DIR not in sys.path:
        sys.path.insert(0, RESOLVER_SCRIPT_DIR)
    import questionnaire_resolver
except Exception:
    questionnaire_resolver = None

try:
    from proposal_price_estimator import (
        analyze_proposal_text,
        calculate_quotation,
        format_telegram_card,
    )
except ImportError:
    analyze_proposal_text = None
    calculate_quotation = None
    format_telegram_card = None

from project_drive_manager import clean_drive_display_path


class InlineQueryDispatcher:
    """Dispatches Telegram inline queries for scale lookups, quotes, and Drive projects."""

    def __init__(self, bot: Any):
        self.bot = bot

    def __getattr__(self, name: str) -> Any:
        return getattr(self.bot, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "bot":
            super().__setattr__(name, value)
        else:
            setattr(self.bot, name, value)

    async def dispatch(self, event: Any) -> None:
        """Handle inline query event."""
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
            if calculate_quotation and analyze_proposal_text and format_telegram_card:
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
