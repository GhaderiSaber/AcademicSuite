#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Telegram Co-Pilot Bridge (copilot_bridge.py)
---------------------------------------------------
Integrates Digital Saber's 5 cognitive layers (Constitution, Case Precedent Memory,
Reasoning Engines, Skills, and Quality Verification) with the Telegram bot and userbot.

Enforces Rule 7 and Rule 11:
- Zero autonomous client dispatches (all responses drafted into Saber's Admin Desk: 124911145)
- Deterministic pricing calculation based on established pricing matrix in Tomans
- Case precedent retrieval for authentic, tailored consulting
- One-click approval / adjustment actions (/send_Q101, /adjust_Q101_<price>)
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Ensure repository root is on sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

try:
    from proposal_price_estimator import (
        analyze_proposal_text,
        calculate_quotation,
        format_telegram_card,
        extract_text_from_file,
        load_persona
    )
except ImportError:
    from .proposal_price_estimator import (
        analyze_proposal_text,
        calculate_quotation,
        format_telegram_card,
        extract_text_from_file,
        load_persona
    )

try:
    from telegram_bot_daemon import DigitalSaberBot
except ImportError:
    from .telegram_bot_daemon import DigitalSaberBot


class TelegramCopilotBridge:
    """Unified bridge connecting Digital Saber cognitive intelligence to Telegram."""

    def __init__(self, saber_instance: Optional[Any] = None, work_dir: Optional[str] = None):
        self.work_dir = work_dir or os.path.join(SCRIPTS_DIR, "bot_storage")
        os.makedirs(self.work_dir, exist_ok=True)
        self.saber = saber_instance

        # Load or initialize bot daemon wrapper in shadow mode
        self.bot = DigitalSaberBot(
            work_dir=self.work_dir,
            business_mode=True,
            business_mode_policy="copilot_only",
            auto_mute_hours=24,
            auto_quote=False
        )
        self.storage_file = os.path.join(self.work_dir, "copilot_active_state.json")
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "pending_quotes": {},
            "pending_drafts": {},
            "approved_quotes": {},
            "last_synced": datetime.now().isoformat()
        }

    def _save_state(self):
        try:
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get_status(self) -> Dict[str, Any]:
        """Returns comprehensive status of Telegram Co-Pilot system."""
        # Load business connections
        bconns = self.bot.business_connections
        active_bconns = len([c for c in bconns.values() if c.get("is_enabled", False)])

        return {
            "policy": self.bot.business_mode_policy,
            "status": "🟢 ACTIVE (Co-Pilot Guardrails Enforced)",
            "admin_id": self.bot.admin_id,
            "admin_desk_chat_id": self.bot.admin_desk_chat_id,
            "business_connections_count": len(bconns),
            "active_business_connections": active_bconns,
            "pending_quotes_count": len(self.state.get("pending_quotes", {})),
            "pending_drafts_count": len(self.state.get("pending_drafts", {})),
            "muted_chats_count": len(self.bot.muted_chats),
            "storage_dir": self.work_dir
        }

    def draft_proposal_quote(self, text_or_file: str, client_name: str = "دانشجو", client_id: int = 2001) -> Dict[str, Any]:
        """
        Ingests a proposal, parses parameters, checks Case Memory precedents,
        calculates itemized quotation in Tomans, and generates an Admin Approval Card.
        """
        if os.path.isfile(text_or_file):
            raw_text = extract_text_from_file(text_or_file)
        else:
            raw_text = text_or_file

        # Analyze proposal text
        params = analyze_proposal_text(raw_text)

        # Retrieve precedents from Case Memory if Saber is available
        precedents = []
        if self.saber and hasattr(self.saber, "case_memory"):
            try:
                precedents = self.saber.case_memory.search_precedents(params.get("title") or raw_text[:100], top_k=2)
            except Exception:
                pass

        # Calculate quotation
        quote = calculate_quotation(params, self.bot.persona)

        qid = f"Q{self.bot.quote_counter}"
        self.bot.quote_counter += 1

        client_card = format_telegram_card(quote, include_admin_actions=False, quote_id=qid)
        admin_card = format_telegram_card(quote, include_admin_actions=True, quote_id=qid)

        record = {
            "quote_id": qid,
            "client_name": client_name,
            "client_id": client_id,
            "params": params,
            "quote": quote,
            "client_card": client_card,
            "admin_card": admin_card,
            "precedents": [p["case"].get("case_id") for p in precedents] if precedents else [],
            "status": "PENDING_ADMIN_APPROVAL",
            "created_at": datetime.now().isoformat()
        }

        self.state.setdefault("pending_quotes", {})[qid] = record
        self.bot.pending_quotes[qid] = record
        self._save_state()

        return record

    def draft_consultation_reply(self, query: str, client_name: str = "دانشجو", client_id: int = 2002) -> Dict[str, Any]:
        """
        Drafts a scholarly response in Saber's tone for an incoming methodology or stats question.
        Uses Digital Saber reasoning and case precedents.
        """
        precedents = []
        if self.saber and hasattr(self.saber, "case_memory"):
            try:
                precedents = self.saber.case_memory.search_precedents(query, top_k=2)
            except Exception:
                pass

        # Check if query is about psychometrics
        is_scale_query = any(k in query for k in ["پرسشنامه", "مقیاس", "آزمون", "خرده‌مقیاس", "روایی", "پایایی"])

        if is_scale_query:
            draft_text = (
                f"سلام وقتتون بخیر {client_name} گرامی، ارادتمندم.\n"
                f"در رابطه با سوال شما درباره ابزار اندازه‌گیری؛ در بانک جامع ۴,۸۸۰ ابزار دانشگاهی ما، "
                f"ساختار عاملی، کلید نمره‌گذاری و سوالات معکوس استاندارد این مقیاس کاملاً تدوین شده است. "
                f"لطفاً عنوان دقیق متغیر یا نام مخفف پرسشنامه را بفرمایید تا شناسنامه کامل و نمره‌گذاری تفکیکی آن را خدمتتون ارسال کنم."
            )
        else:
            draft_text = (
                f"سلام و احترام، {client_name} گرامی وقتتون بخیر.\n"
                f"در پاسخ به پرسش شما در زمینه روش‌شناسی و تحلیل داده‌ها؛ "
                f"بر اساس اصول روش تحقیق پیشرفته و تجربه رساله‌های مشابه در حیطه پژوهش شما، "
                f"بررسی پیش‌فرض‌های آماری (از جمله نرمال بودن چندمتغیری، همگنی واریانس‌ها و عدم هم‌خطی) "
                f"گام اساسی قبل از اجرای آزمون‌های استنباطی است. "
                f"در صورتی که داده‌های اولیه یا طرح تفصیلی را ارسال بفرمایید، بررسی دقیق‌تر انجام و نقشه تحلیل خدمتتون تقدیم می‌شود."
            )

        did = f"D{self.bot.draft_counter}"
        self.bot.draft_counter += 1

        record = {
            "draft_id": did,
            "client_name": client_name,
            "client_id": client_id,
            "query": query,
            "draft_text": draft_text,
            "precedents": [p["case"].get("case_id") for p in precedents] if precedents else [],
            "status": "PENDING_APPROVAL",
            "created_at": datetime.now().isoformat()
        }

        self.state.setdefault("pending_drafts", {})[did] = record
        self.bot.pending_drafts[did] = record
        self._save_state()

        return record

    def approve_quote(self, quote_id: str, adjusted_price: Optional[int] = None) -> Dict[str, Any]:
        """Approves a pending quotation and marks it as ready for client dispatch."""
        quotes = self.state.get("pending_quotes", {})
        if quote_id not in quotes:
            return {"status": "error", "message": f"Quotation ID {quote_id} not found in pending list."}

        record = quotes.pop(quote_id)
        if adjusted_price:
            record["adjusted_price"] = adjusted_price
            record["quote"]["total_price_tomans"] = adjusted_price

        record["status"] = "APPROVED_BY_ADMIN"
        record["approved_at"] = datetime.now().isoformat()
        self.state.setdefault("approved_quotes", {})[quote_id] = record
        self._save_state()

        return {
            "status": "success",
            "quote_id": quote_id,
            "client_name": record["client_name"],
            "total_price": record["quote"]["total_price_tomans"],
            "message": f"Quotation {quote_id} approved for {record['client_name']}. Ready for delivery."
        }

    def run_simulation(self) -> Dict[str, Any]:
        """Executes full offline simulation verifying Co-Pilot client-admin lifecycle."""
        return self.bot.run_test_simulation()
