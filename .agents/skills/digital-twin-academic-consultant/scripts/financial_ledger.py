"""
financial_ledger.py — Academic Client Financial Ledger & Installment Accounting Engine

Manages:
1. Client project financial contracts (total contract amount in Tomans).
2. Standard 3-stage or custom milestone installment schedules:
   - Phase 1: پیش‌پرداخت شروع کار (Deposit / Kickoff) — 40%
   - Phase 2: تحویل میانی / فاز تحلیل داده‌ها (Midterm Analysis Delivery) — 30%
   - Phase 3: تسویه نهایی / تایید استاد راهنما و دفاع (Final Balance / Defense Approval) — 30%
3. Transaction tracking (payments, card-to-card, Sheba, tracking codes, timestamps, receipts).
4. Google Drive persistence in `financial_ledger.json` inside each client workspace.
5. Local aggregation cache in `userbot_storage/financial_ledgers.json`.
6. Modern 2026 Telegram container cards with visual progress bars and official Persian payment receipts.
"""

import os
import re
import json
import html
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

try:
    from telethon import Button
except ImportError:
    Button = None


def to_persian_digits(text: str) -> str:
    """Convert ASCII digits to authentic Persian digits (۰-۹)."""
    fa_digits = "۰۱۲۳۴۵۶۷۸۹"
    en_digits = "0123456789"
    trans = str.maketrans(en_digits, fa_digits)
    return str(text).translate(trans)


def format_toman(amount: int, lang: str = "fa") -> str:
    """Format integer into thousands-separated Persian formatted number."""
    if amount is None:
        return "۰" if lang == "fa" else "0"
    formatted = f"{amount:,}"
    if lang == "fa":
        return to_persian_digits(formatted)
    return formatted


class AcademicFinancialLedger:
    """Manages client contracts, installment milestones, and transaction ledgers."""

    def __init__(self, work_dir: str, storage_dir: Optional[str] = None):
        self.work_dir = work_dir
        self.storage_dir = storage_dir or os.path.join(os.path.dirname(__file__), "userbot_storage")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.cache_file = os.path.join(self.storage_dir, "financial_ledgers.json")
        self.cache: Dict[str, Dict[str, Any]] = self._load_cache()

    def _load_cache(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[-] Error loading financial ledger cache: {e}")
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[-] Error saving financial ledger cache: {e}")

    def get_ledger_path(self, project_dir: str) -> str:
        return os.path.join(project_dir, "financial_ledger.json")

    def load_ledger(self, project_dir: str) -> Dict[str, Any]:
        """Load project ledger from Google Drive or initialize default."""
        ledger_path = self.get_ledger_path(project_dir)
        cname = os.path.basename(project_dir)

        if os.path.exists(ledger_path):
            try:
                with open(ledger_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._recalculate_ledger(data)
                    self.cache[cname] = data
                    self._save_cache()
                    return data
            except Exception as e:
                print(f"[-] Error reading {ledger_path}: {e}")

        # If cache has it
        if cname in self.cache:
            return self.cache[cname]

        # Initialize blank ledger
        default_data = {
            "client_name": cname,
            "project_dir": project_dir,
            "scope": "full_thesis",
            "contract_active": False,
            "total_contract_tomans": 0,
            "total_paid_tomans": 0,
            "balance_due_tomans": 0,
            "settlement_pct": 0,
            "status": "unpaid",  # unpaid, partially_paid, settled, overdue
            "installments": [],
            "transactions": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return default_data

    def save_ledger(self, project_dir: str, data: Dict[str, Any]):
        """Persist ledger to Google Drive workspace and update local cache."""
        self._recalculate_ledger(data)
        data["updated_at"] = datetime.now().isoformat()
        ledger_path = self.get_ledger_path(project_dir)
        cname = os.path.basename(project_dir)

        try:
            with open(ledger_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[-] Error writing {ledger_path}: {e}")

        self.cache[cname] = data
        self._save_cache()

    def initialize_contract(
        self,
        project_dir: str,
        total_tomans: int,
        client_name: Optional[str] = None,
        scope: str = "full_thesis",
        installment_count: int = 3
    ) -> Dict[str, Any]:
        """
        Initialize or update a contract with a standard academic installment plan.
        Standard 3-Stage:
          1. 40% Deposit / Kickoff
          2. 30% Midterm Analysis / Ch4 Delivery
          3. 30% Final Defense Approval & Sign-off
        """
        data = self.load_ledger(project_dir)
        cname = client_name or os.path.basename(project_dir)

        data["client_name"] = cname
        data["scope"] = scope
        data["contract_active"] = True
        data["total_contract_tomans"] = total_tomans

        # Build installments
        installments = []
        if installment_count == 1:
            installments.append({
                "id": "INST-1",
                "title_fa": "تسویه کامل یکجا",
                "title_en": "Single Lump-Sum Payment",
                "milestone": "شروع و تحویل پروژه",
                "pct": 100,
                "amount_tomans": total_tomans,
                "status": "pending",  # pending, paid, overdue
                "paid_amount": 0,
                "due_trigger": "شروع کار"
            })
        elif installment_count == 2:
            amt1 = int(round(total_tomans * 0.5))
            amt2 = total_tomans - amt1
            installments.append({
                "id": "INST-1",
                "title_fa": "قسط اول (پیش‌پرداخت شروع کار)",
                "title_en": "1st Installment (Deposit / Kickoff)",
                "milestone": "آغاز نگارش و تدوین طرح پژوهش",
                "pct": 50,
                "amount_tomans": amt1,
                "status": "pending",
                "paid_amount": 0,
                "due_trigger": "شروع کار"
            })
            installments.append({
                "id": "INST-2",
                "title_fa": "قسط دوم (تسویه نهایی تحویل کار)",
                "title_en": "2nd Installment (Final Delivery Balance)",
                "milestone": "تحویل پکیج نهایی و تایید استاد راهنما",
                "pct": 50,
                "amount_tomans": amt2,
                "status": "pending",
                "paid_amount": 0,
                "due_trigger": "تحویل نهایی"
            })
        else:
            # 3 installments (40% - 30% - 30%)
            amt1 = int(round(total_tomans * 0.4))
            amt2 = int(round(total_tomans * 0.3))
            amt3 = total_tomans - amt1 - amt2
            installments.append({
                "id": "INST-1",
                "title_fa": "قسط اول: پیش‌پرداخت شروع کار (۴۰٪)",
                "title_en": "1st Installment: Deposit & Kickoff (40%)",
                "milestone": "تعیین مقیاس‌ها و تدوین متدولوژی (فصل ۳)",
                "pct": 40,
                "amount_tomans": amt1,
                "status": "pending",
                "paid_amount": 0,
                "due_trigger": "شروع قرارداد"
            })
            installments.append({
                "id": "INST-2",
                "title_fa": "قسط دوم: تحویل تحلیل آماری فصل ۴ (۳۰٪)",
                "title_en": "2nd Installment: Statistical Analysis & Ch4 (30%)",
                "milestone": "تحویل داده‌های شبیه‌سازی و گزارش نتایج SPSS/SEM",
                "pct": 30,
                "amount_tomans": amt2,
                "status": "pending",
                "paid_amount": 0,
                "due_trigger": "تحویل فصل چهارم"
            })
            installments.append({
                "id": "INST-3",
                "title_fa": "قسط سوم: تسویه نهایی و تایید شورا (۳۰٪)",
                "title_en": "3rd Installment: Final Balance & Defense (30%)",
                "milestone": "تدوین بحث (فصل ۵)، رفع کامنت‌ها و تایید دفاع",
                "pct": 30,
                "amount_tomans": amt3,
                "status": "pending",
                "paid_amount": 0,
                "due_trigger": "تایید نهایی استاد راهنما"
            })

        data["installments"] = installments
        self.save_ledger(project_dir, data)
        return data

    def record_transaction(
        self,
        project_dir: str,
        amount_tomans: int,
        tracking_code: str = "",
        payment_method: str = "کارت به کارت",
        notes: str = "",
        payer_name: str = ""
    ) -> Dict[str, Any]:
        """
        Record a payment transaction, allocate to installments, and update balance.
        Returns the created transaction record with unique receipt_id.
        """
        data = self.load_ledger(project_dir)
        now = datetime.now()
        tx_count = len(data.get("transactions", [])) + 1
        receipt_id = f"REC-{now.strftime('%Y%m%d')}-{tx_count:02d}"

        tx_entry = {
            "receipt_id": receipt_id,
            "timestamp": now.isoformat(),
            "date_str": now.strftime("%Y-%m-%d %H:%M"),
            "amount_tomans": amount_tomans,
            "tracking_code": str(tracking_code).strip() if tracking_code else "ثبت دستی / کارت به کارت",
            "payment_method": payment_method,
            "payer_name": payer_name or data.get("client_name", "پژوهشگر"),
            "notes": notes,
            "verified": True
        }

        if "transactions" not in data:
            data["transactions"] = []
        data["transactions"].append(tx_entry)

        # Allocate payment across pending installments
        remaining_to_allocate = sum(tx["amount_tomans"] for tx in data["transactions"])
        for inst in data.get("installments", []):
            target_amt = inst["amount_tomans"]
            if remaining_to_allocate >= target_amt:
                inst["paid_amount"] = target_amt
                inst["status"] = "paid"
                remaining_to_allocate -= target_amt
            elif remaining_to_allocate > 0:
                inst["paid_amount"] = remaining_to_allocate
                inst["status"] = "partially_paid"
                remaining_to_allocate = 0
            else:
                inst["paid_amount"] = 0
                inst["status"] = "pending"

        self.save_ledger(project_dir, data)
        return tx_entry

    def _recalculate_ledger(self, data: Dict[str, Any]):
        """Recalculate total_paid, balance_due, and settlement_pct."""
        total_contract = data.get("total_contract_tomans", 0)
        transactions = data.get("transactions", [])
        total_paid = sum(t.get("amount_tomans", 0) for t in transactions)

        balance_due = max(0, total_contract - total_paid)
        settlement_pct = int(round((total_paid / total_contract) * 100)) if total_contract > 0 else (100 if total_paid > 0 else 0)

        data["total_paid_tomans"] = total_paid
        data["balance_due_tomans"] = balance_due
        data["settlement_pct"] = min(100, settlement_pct)

        if total_contract == 0 and total_paid == 0:
            data["status"] = "unpaid"
        elif total_paid >= total_contract and total_contract > 0:
            data["status"] = "settled"
        elif total_paid > 0:
            data["status"] = "partially_paid"
        else:
            data["status"] = "unpaid"

    def format_ledger_card(self, project_dir: str) -> Tuple[str, Optional[List]]:
        """
        Generate a modern 2026 Telegram container card showing contract status,
        installment progress bar, itemized breakdown, and recent transaction records.
        """
        data = self.load_ledger(project_dir)
        cname = data.get("client_name") or os.path.basename(project_dir)
        total_contract = data.get("total_contract_tomans", 0)
        total_paid = data.get("total_paid_tomans", 0)
        balance_due = data.get("balance_due_tomans", 0)
        pct = data.get("settlement_pct", 0)
        status = data.get("status", "unpaid")

        # Progress bar: 10 blocks
        filled = int(round(pct / 10))
        bar = "█" * filled + "░" * (10 - filled)

        status_badges = {
            "settled": "🟢 <b>تسویه کامل (Fully Settled)</b>",
            "partially_paid": "🟡 <b>در جریان اقساط (Partially Paid)</b>",
            "unpaid": "⚪ <b>بدون پرداخت / منتظر بیعانه (Unpaid)</b>",
            "overdue": "🔴 <b>دارای اقساط معوقه (Overdue)</b>"
        }
        status_str = status_badges.get(status, "🟡 در جریان")

        scope_labels = {
            "chapter4_only": "📊 تحلیل آماری فصل چهارم (Chapter 4 Only)",
            "proposal_only": "📑 تدوین پروپوزال (Proposal Only)",
            "full_thesis": "🎓 رساله / پایان‌نامه جامع (Full Thesis)",
            "supervisor_revisions": "📝 اصلاحات و بازنگری شورا (Revisions)"
        }
        scope_str = scope_labels.get(data.get("scope", "full_thesis"), "🎓 مشاوره پژوهشی")

        lines = [
            "╭─ 💳 <b>CLIENT FINANCIAL LEDGER</b> ─────────────────",
            f"│ 👤 <b>Client:</b> {html.escape(cname)}",
            f"│ 🎓 <b>Scope:</b> {scope_str}",
            f"│ 📊 <b>Settlement:</b> <code>[{bar}]</code> <b>{pct}%</b>",
            f"│ 🏷️ <b>Status:</b> {status_str}",
            "╰──────────────────────────────────────────────────",
            "",
            f"💰 <b>FINANCIAL CONTRACT OVERVIEW</b>",
            f"• <b>مبلغ کل قرارداد:</b> <code>{format_toman(total_contract)}</code> تومان",
            f"• <b>مجموع واریزی‌ها:</b> <code>{format_toman(total_paid)}</code> تومان",
            f"• <b>مانده مطالبات:</b> <code>{format_toman(balance_due)}</code> تومان",
            "",
            "📋 <b>MILESTONE INSTALLMENTS BREAKDOWN</b>",
            "<blockquote expandable>"
        ]

        installments = data.get("installments", [])
        if not installments:
            lines.append("<i>هیچ برنامه اقساطی فعالی ثبت نشده است. از دستور /contract برای ثبت استفاده فرمایید.</i>")
        else:
            for idx, inst in enumerate(installments, 1):
                i_status = inst.get("status", "pending")
                if i_status == "paid":
                    badge = "✅"
                elif i_status == "partially_paid":
                    badge = "🟡"
                else:
                    badge = "⏳"

                amt_str = format_toman(inst.get("amount_tomans", 0))
                paid_str = format_toman(inst.get("paid_amount", 0))
                title = inst.get("title_fa", f"قسط {idx}")
                due = inst.get("due_trigger", "")

                lines.append(f"├ {badge} <b>{title}</b>")
                lines.append(f"│  ▫️ مبلغ: <code>{amt_str}</code> ت (واریز: <code>{paid_str}</code> ت) • شرط: <i>{due}</i>")
            # fix last item tree branch
            if len(lines) > 0 and lines[-2].startswith("├"):
                lines[-2] = "└" + lines[-2][1:]

        lines.append("</blockquote>")

        # Transactions block
        txs = data.get("transactions", [])
        lines.append("")
        lines.append(f"🧾 <b>TRANSACTION HISTORY ({len(txs)} payments)</b>")
        lines.append("<blockquote expandable>")
        if not txs:
            lines.append("<i>هنوز تراکنشی در این پرونده ثبت نشده است.</i>")
        else:
            for t in reversed(txs[-5:]):  # show last 5
                rec_id = t.get("receipt_id", "REC")
                t_date = t.get("date_str", "")
                t_amt = format_toman(t.get("amount_tomans", 0))
                t_code = t.get("tracking_code", "")
                lines.append(f"• <b>{rec_id}</b> ({t_date}):")
                lines.append(f"  واریز <code>{t_amt}</code> تومان • کد پیگیری: <code>{t_code}</code>")
        lines.append("</blockquote>")

        card_html = "\n".join(lines)

        # Build interactive keyboard
        btns = None
        if Button is not None:
            clean_cname = cname.replace(" ", "_")[:20]
            btns = [
                [
                    Button.switch_inline("💳 Record Payment", f"/pay {cname} ", same_peer=True),
                    Button.inline("🧾 View Receipt", f"pay_receipt_{clean_cname}".encode("utf-8"))
                ],
                [
                    Button.inline("🔄 Refresh Ledger", f"pay_refresh_{clean_cname}".encode("utf-8")),
                    Button.switch_inline("📝 Update Contract", f"/contract {cname} ", same_peer=True)
                ]
            ]

        return card_html, btns

    def format_receipt_card(self, tx_entry: Dict[str, Any], project_dir: str) -> str:
        """
        Generate an official, elegant Persian payment receipt card for the client.
        Complies with Rule 4 Persian typography and Rule 3 APA/OpenXML standards.
        """
        data = self.load_ledger(project_dir)
        cname = data.get("client_name") or os.path.basename(project_dir)
        rec_id = tx_entry.get("receipt_id", "REC")
        t_date = tx_entry.get("date_str") or datetime.now().strftime("%Y-%m-%d %H:%M")
        t_amt = format_toman(tx_entry.get("amount_tomans", 0))
        t_code = tx_entry.get("tracking_code", "ثبت سیستمی")
        total_contract = format_toman(data.get("total_contract_tomans", 0))
        total_paid = format_toman(data.get("total_paid_tomans", 0))
        balance_due = format_toman(data.get("balance_due_tomans", 0))
        pct = data.get("settlement_pct", 0)

        receipt_html = (
            f"╭─ 🧾 <b>رسید رسمی دریافت وجه واریزی</b> ─────────────────\n"
            f"│ 🆔 <b>شماره رسید:</b> <code>{rec_id}</code>\n"
            f"│ 📅 <b>تاریخ و زمان:</b> <code>{t_date}</code>\n"
            f"│ 👤 <b>پژوهشگر گرامی:</b> {html.escape(cname)}\n"
            f"╰──────────────────────────────────────────────────\n\n"
            f"با سلام و احترام؛\n"
            f"بدین‌وسیله تایید می‌گردد مبلغ زیر با مشخصات درج‌شده دریافت و در پرونده پژوهشی شما ثبت گردید:\n\n"
            f"<blockquote expandable>\n"
            f"💵 <b>مبلغ واریز شده:</b> <code>{t_amt}</code> تومان\n"
            f"🔢 <b>شماره پیگیری / مرجع:</b> <code>{html.escape(str(t_code))}</code>\n"
            f"💳 <b>نحوه پرداخت:</b> {html.escape(tx_entry.get('payment_method', 'کارت به کارت'))}\n"
            f"</blockquote>\n\n"
            f"📊 <b>خلاصه وضعیت مالی پرونده پژوهش:</b>\n"
            f"• کل حق‌الزحمه قرارداد: <code>{total_contract}</code> تومان\n"
            f"• مجموع کل پرداختی‌ها: <code>{total_paid}</code> تومان (<b>{pct}٪</b> تسویه)\n"
            f"• مانده بدهی قرارداد: <code>{balance_due}</code> تومان\n\n"
            f"<i>تیم مشاوره و تحلیل آماری صابر قادری — موفقیت شما در جلسه دفاع تعهد علمی ماست.</i>"
        )
        return receipt_html

    def get_global_financial_summary(self) -> Dict[str, Any]:
        """
        Aggregate portfolio metrics across all projects in Google Drive.
        Returns total portfolio value, collections, pending receivables, and client breakdown.
        """
        total_portfolio = 0
        total_collected = 0
        total_receivables = 0
        settled_count = 0
        active_count = 0
        unpaid_count = 0
        overdue_clients = []

        # Scan work_dir if exists
        if os.path.exists(self.work_dir):
            for entry in os.listdir(self.work_dir):
                full_path = os.path.join(self.work_dir, entry)
                if os.path.isdir(full_path) and not entry.startswith((".", "0", "archive")):
                    # Load ledger
                    ld = self.load_ledger(full_path)
                    tc = ld.get("total_contract_tomans", 0)
                    tp = ld.get("total_paid_tomans", 0)
                    bd = ld.get("balance_due_tomans", 0)
                    status = ld.get("status", "unpaid")

                    total_portfolio += tc
                    total_collected += tp
                    total_receivables += bd

                    if status == "settled":
                        settled_count += 1
                    elif status == "partially_paid":
                        active_count += 1
                        # Check if any installment is overdue
                        for inst in ld.get("installments", []):
                            if inst.get("status") == "overdue":
                                overdue_clients.append({
                                    "client_name": entry,
                                    "installment": inst.get("title_fa", ""),
                                    "amount": inst.get("amount_tomans", 0)
                                })
                                break
                    else:
                        unpaid_count += 1

        return {
            "total_portfolio_tomans": total_portfolio,
            "total_collected_tomans": total_collected,
            "total_receivables_tomans": total_receivables,
            "settled_count": settled_count,
            "active_installment_count": active_count,
            "unpaid_count": unpaid_count,
            "overdue_count": len(overdue_clients),
            "overdue_clients": overdue_clients
        }

    def format_global_summary_card(self) -> str:
        """Format portfolio executive accounting summary for Topic 116."""
        summary = self.get_global_financial_summary()
        port = format_toman(summary["total_portfolio_tomans"])
        coll = format_toman(summary["total_collected_tomans"])
        rec = format_toman(summary["total_receivables_tomans"])
        pct_coll = int(round((summary["total_collected_tomans"] / summary["total_portfolio_tomans"] * 100))) if summary["total_portfolio_tomans"] > 0 else 0

        filled = int(round(pct_coll / 10))
        bar = "█" * filled + "░" * (10 - filled)

        lines = [
            "╭─ 💰 <b>EXECUTIVE FINANCIAL PORTFOLIO</b> ────────────",
            f"│ 📅 <b>Audit Date:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M')}</code>",
            f"│ 📈 <b>Collection Rate:</b> <code>[{bar}]</code> <b>{pct_coll}%</b>",
            f"│ 📁 <b>Active Client Contracts:</b> {summary['active_installment_count'] + summary['settled_count']}",
            "╰──────────────────────────────────────────────────",
            "",
            "💵 <b>FINANCIAL TOTALS (TOMANS)</b>",
            f"• <b>کل ارزش قراردادهای پرونده‌ها:</b> <code>{port}</code> تومان",
            f"• <b>مجموع وصولی‌های قطعی:</b> <code>{coll}</code> تومان",
            f"• <b>کل مطالبات در جریان (Receivables):</b> <code>{rec}</code> تومان",
            "",
            "📊 <b>CLIENT SETTLEMENT HEALTH</b>",
            f"• 🟢 تسویه کامل: <b>{summary['settled_count']}</b> پرونده",
            f"• 🟡 در جریان اقساط فعال: <b>{summary['active_installment_count']}</b> پرونده",
            f"• ⚪ بدون پرداخت اولیه: <b>{summary['unpaid_count']}</b> پرونده"
        ]

        if summary["overdue_clients"]:
            lines.append("")
            lines.append("⚠️ <b>اقساط نیازمند پیگیری و معوقه:</b>")
            lines.append("<blockquote expandable>")
            for oc in summary["overdue_clients"]:
                lines.append(f"• <b>{oc['client_name']}</b>: {oc['installment']} (<code>{format_toman(oc['amount'])}</code> ت)")
            lines.append("</blockquote>")

        return "\n".join(lines)
