"""
deliverable_dispatcher.py — Academic Client Deliverables Dispatch & Financial Gatekeeping Engine

Automates:
1. Scanning Google Drive `03_deliverables/` folders across active client projects.
2. Identifying newly completed or un-dispatched research files (.docx, .spv, .xlsx, .pptx).
3. Financial Gatekeeping: Queries `financial_ledger.json` to verify whether the milestone installment is settled or overdue.
4. Generating scholarly, context-aware Persian delivery manifests with student instructions.
5. Multi-file .zip bundling (e.g. bundling Chapter 4 .docx + SPSS .spv + Dataset .xlsx into a clean package).
6. Automatic milestone stage advancement in `milestone_tracker.py` and timestamped archiving in `03_deliverables/drafts_archive/`.
7. Modern 2026 Telegram box-drawing container cards with 1-click dispatch buttons.
"""

import os
import re
import json
import html
import shutil
import zipfile
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

try:
    from telethon import Button
except ImportError:
    Button = None

try:
    from financial_ledger import format_toman
except ImportError:
    def format_toman(amount, lang="fa"):
        return f"{amount:,}"


def clean_client_display_name(raw_name: str) -> str:
    """Clean client name for authentic Persian addressing."""
    display = raw_name.split("(")[0].strip()
    if display.startswith("@"):
        display = display.lstrip("@")
    return display or "پژوهشگر"


class AcademicDeliverableDispatcher:
    """Coordinates deliverable detection, financial clearance, and Telegram dispatch."""

    def __init__(self, project_manager, financial_ledger, milestone_tracker):
        self.pm = project_manager
        self.fl = financial_ledger
        self.mt = milestone_tracker

    def scan_pending_deliverables(self, project_dir: str) -> List[Dict[str, Any]]:
        """
        Scan and return deliverables with enriched academic classification.
        Filters out internal drafts and temporary files.
        """
        if not self.pm:
            return []
        raw_files = self.pm.list_project_deliverables(project_dir)
        enriched = []
        for f in raw_files:
            type_info = self.classify_deliverable_type(f["filename"])
            enriched.append({
                **f,
                "type_info": type_info
            })
        return enriched

    def classify_deliverable_type(self, filename: str) -> Dict[str, str]:
        """
        Classify deliverable file by academic artifact category and file extension.
        Returns code, title_fa, title_en, icon, and matching milestone code.
        """
        fn = filename.lower()
        base, ext = os.path.splitext(fn)

        if ext == ".spv" or "output" in fn or "نتایج" in fn or "خروجی" in fn:
            return {
                "type_code": "spss_output",
                "title_fa": "فایل خروجی نرم‌افزار SPSS (.spv)",
                "title_en": "SPSS Statistical Output File (.spv)",
                "icon": "📊",
                "milestone_stage": "S2",
                "financial_phase": 2
            }
        elif ext in [".xlsx", ".xls", ".sav", ".csv"] or "data" in fn or "داده" in fn or "matrix" in fn:
            return {
                "type_code": "data_file",
                "title_fa": "ماتریس داده‌ها و شبیه‌سازی آماری (.xlsx / .sav)",
                "title_en": "Empirical Dataset & Simulation Matrix",
                "icon": "📈",
                "milestone_stage": "S1",
                "financial_phase": 2
            }
        elif "پاسخ" in fn or "داور" in fn or "rebuttal" in fn or "revision" in fn:
            return {
                "type_code": "rebuttal_table",
                "title_fa": "جدول پاسخ به نظرات اساتید راهنما و داوران",
                "title_en": "Point-by-Point Supervisor Rebuttal Table",
                "icon": "📝",
                "milestone_stage": "R4",
                "financial_phase": 3
            }
        elif "فصل_چهارم" in fn or "فصل ۴" in fn or "chapter_4" in fn or "results" in fn or "یافته" in fn:
            return {
                "type_code": "chapter_4_results",
                "title_fa": "گزارش نهایی یافته‌های آماری و جداول APA 7 (فصل چهارم)",
                "title_en": "Chapter 4: Statistical Findings & APA 7 Tables",
                "icon": "🔬",
                "milestone_stage": "S5",
                "financial_phase": 2
            }
        elif "پروپوزال" in fn or "proposal" in fn or "طرح" in fn:
            return {
                "type_code": "proposal",
                "title_fa": "طرح تحقیق و پروپوزال دانشگاهی (فصول ۱ تا ۳)",
                "title_en": "Academic Research Proposal & Methodology",
                "icon": "📑",
                "milestone_stage": "P5",
                "financial_phase": 1
            }
        elif "فصل_سوم" in fn or "فصل ۳" in fn or "chapter_3" in fn or "method" in fn or "روش" in fn:
            return {
                "type_code": "chapter_3_methodology",
                "title_fa": "روش‌شناسی پژوهش و مدل‌سازی توان G*Power (فصل سوم)",
                "title_en": "Chapter 3: Methodology & G*Power Power Modeling",
                "icon": "📐",
                "milestone_stage": "M3",
                "financial_phase": 1
            }
        elif "فصل_پنجم" in fn or "فصل ۵" in fn or "chapter_5" in fn or "discussion" in fn or "بحث" in fn:
            return {
                "type_code": "chapter_5_discussion",
                "title_fa": "بحث و نتیجه‌گیری و تبیین روان‌شناختی (فصل پنجم)",
                "title_en": "Chapter 5: Theoretical Discussion & Implications",
                "icon": "💡",
                "milestone_stage": "M5",
                "financial_phase": 3
            }
        elif ext in [".pptx", ".ppt"] or "slide" in fn or "دفاع" in fn or "defense" in fn:
            return {
                "type_code": "presentation_slides",
                "title_fa": "اسلایدهای جامع جلسه دفاع پایان‌نامه (.pptx)",
                "title_en": "Comprehensive Defense Presentation Slides (.pptx)",
                "icon": "📽️",
                "milestone_stage": "M5",
                "financial_phase": 3
            }
        elif ext == ".zip":
            return {
                "type_code": "bundled_package",
                "title_fa": "پکیج جامع فایل‌های تحویلی پروژه (.zip)",
                "title_en": "Bundled Deliverables Project Archive (.zip)",
                "icon": "📦",
                "milestone_stage": "S5",
                "financial_phase": 2
            }
        else:
            return {
                "type_code": "general_document",
                "title_fa": f"سند نهایی تحویلی ({ext})",
                "title_en": f"Deliverable Document ({ext})",
                "icon": "📄",
                "milestone_stage": "S5",
                "financial_phase": 2
            }

    def check_financial_gate(self, project_dir: str, target_phase: int = 2) -> Dict[str, Any]:
        """
        Check whether the client's financial installment for this phase is cleared.
        Phase 1: Deposit (40%)
        Phase 2: Midterm Analysis Delivery (30%) -> Total 70% required
        Phase 3: Final Defense (30%) -> Total 100% required
        """
        if not self.fl:
            return {
                "gate_passed": True,
                "badge": "⚪ نامشخص",
                "status_str": "سیستم مالی متصل نیست",
                "balance_due": 0
            }

        ld = self.fl.load_ledger(project_dir)
        tot_c = ld.get("total_contract_tomans", 0)
        tot_p = ld.get("total_paid_tomans", 0)
        bal = ld.get("balance_due_tomans", 0)
        pct = ld.get("settlement_pct", 0)

        # Thresholds
        req_pct = 40 if target_phase == 1 else (70 if target_phase == 2 else 100)
        req_amount = int(round(tot_c * (req_pct / 100.0)))

        if tot_c == 0:
            return {
                "gate_passed": True,
                "badge": "⚪ فاقد قرارداد مالی صریح",
                "status_str": "مبلغ قرارداد صفر یا ثبت نشده است.",
                "balance_due": 0,
                "paid_amount": tot_p,
                "settled_pct": 100
            }

        if tot_p >= req_amount:
            return {
                "gate_passed": True,
                "badge": f"🟢 تسویه مرحله {target_phase} ({pct}٪ پرداخت شده)",
                "status_str": f"قسط مرحله با موفقیت تسویه گردیده است ({format_toman(tot_p)} از {format_toman(tot_c)} ت).",
                "balance_due": bal,
                "paid_amount": tot_p,
                "settled_pct": pct
            }
        else:
            shortfall = req_amount - tot_p
            return {
                "gate_passed": False,
                "badge": f"⚠️ قسط مرحله {target_phase} تسویه نشده! ({pct}٪ پرداخت)",
                "status_str": f"کسری وجه برای این مرحله: <b>{format_toman(shortfall)}</b> تومان (کل مانده: {format_toman(bal)} ت).",
                "balance_due": bal,
                "shortfall": shortfall,
                "paid_amount": tot_p,
                "settled_pct": pct
            }

    def generate_delivery_manifest_caption(
        self,
        client_name: str,
        deliverable_info: Dict[str, Any],
        all_deliverables: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generate an authentic, high-context Persian delivery caption for the student.
        Adheres to Rule 4 Persian typography (نیم‌فاصله) and scholarly tone.
        """
        d_name = html.escape(clean_client_display_name(client_name))
        t_code = deliverable_info.get("type_code", "general_document")
        fn = html.escape(deliverable_info.get("filename", ""))

        lines = [
            f"سلام و احترام وقت شما بخیر {d_name} گرامی؛",
            ""
        ]

        if t_code == "chapter_4_results":
            lines.extend([
                f"فایل نهایی گزارش تحلیل آماری (فصل چهارم) با عنوان «{fn}» به همراه جداول منطبق با راهنمای APA 7th Edition خدمت شما تقدیم می‌گردد.",
                "",
                "📌 <b>نکات مهم جهت ارائه به اساتید محترم:</b>",
                "• کلیه مفروضه‌های آزمون (نرمال بودن، همگنی واریانس‌ها، خطی بودن) به دقت کنترل و مستند شده‌اند.",
                "• نتایج خروجی نرم‌افزار به صورت تفکیکی در جداول گزارش شده و در متن با اندازه اثر (Effect Size) تبیین گردیده است.",
                "• در صورت ارائه هرگونه نظر، کامنت یا سوال از سوی اساتید راهنما یا مشاور، با کمال میل جهت دفاع و پاسخگویی در کنارتان هستیم."
            ])
        elif t_code == "spss_output":
            lines.extend([
                f"فایل خام خروجی پردازش‌های آماری نرم‌افزار SPSS با پسوند (.spv) تقدیم حضورتان می‌شود.",
                "این فایل حاوی کلیه لاگ‌ها، جداول تفصیلی و سینتکس‌های محاسباتی است که در صورت درخواست استاد راهنما می‌توانید مستقیماً در نرم‌افزار SPSS باز و ارائه فرمایید."
            ])
        elif t_code == "data_file":
            lines.extend([
                f"ماتریس نهایی داده‌های پژوهش به همراه ساختار کدگذاری متغیرها و کلید نمره‌گذاری مقیاس‌ها تقدیم می‌گردد.",
                "داده‌ها از نظر غربالگری خطاهای ثبت، داده‌های مفقود و نرمال‌سازی به طور کامل بازبینی و مرتب شده‌اند."
            ])
        elif t_code == "rebuttal_table":
            lines.extend([
                f"جدول پاسخ به نظرات اساتید محترم راهنما و داوران شورا («{fn}») با ساختار سه ستونی استاندارد آماده و خدمتتان ارسال گردید.",
                "کلیه ابهامات و کامنت‌های مطرح‌شده با استناد به منابع بین‌المللی متدولوژی و رفرنس‌های جدید مستندسازی شده‌اند."
            ])
        elif t_code == "proposal":
            lines.extend([
                f"طرح تحقیق دانشگاهی (پروپوزال جامع) حاوی بیان مسئله به روش هرم وارونه، متدولوژی، ابزارهای اندازه‌گیری استاندارد و تعیین دقیق حجم نمونه با G*Power خدمتتان تقدیم می‌گردد."
            ])
        elif t_code == "bundled_package":
            lines.extend([
                f"پکیج جامع فایل‌های نهایی تحویلی پروژه («{fn}») شامل گزارش نتایج فصل چهارم، خروجی‌های معتبر نرم‌افزاری و فایل‌های اکسل به پیوست تقدیم می‌گردد."
            ])
        else:
            lines.extend([
                f"فایل نهایی «{fn}» خدمتتون تقدیم می‌شود. لطفاً بررسی بفرمایید؛ در صورت نیاز به هرگونه بررسی، اصلاح و پشتیبانی علمی با کمال میل در خدمتتون هستیم."
            ])

        lines.extend([
            "",
            "با آرزوی موفقیت و درخشش شما در جلسه دفاع / شورا 🌸",
            "<i>تیم مشاوره و تحلیل آماری صابر قادری</i>"
        ])
        return "\n".join(lines)

    def bundle_deliverables_zip(self, project_dir: str, file_paths: List[str], bundle_name: Optional[str] = None) -> str:
        """
        Bundle multiple deliverable files into a single clean .zip archive in 03_deliverables/.
        Returns the absolute path to the generated .zip file.
        """
        deliv_dir = os.path.join(project_dir, "03_deliverables")
        os.makedirs(deliv_dir, exist_ok=True)
        cname = os.path.basename(project_dir)
        ts = datetime.now().strftime("%Y%m%d")
        zip_filename = bundle_name or f"{cname}_Deliverables_Package_{ts}.zip"
        zip_path = os.path.join(deliv_dir, zip_filename)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for fp in file_paths:
                if os.path.exists(fp) and not fp.endswith(".zip"):
                    arcname = os.path.basename(fp)
                    zipf.write(fp, arcname=arcname)

        return zip_path

    def format_dispatch_card(
        self,
        del_id: str,
        client_name: str,
        username: Optional[str],
        telegram_id: Optional[int],
        project_dir: str,
        chosen_file: Dict[str, Any],
        all_files: List[Dict[str, Any]]
    ) -> Tuple[str, Optional[List]]:
        """
        Format a modern 2026 Telegram container card with file metadata,
        financial gatekeeper status, expandable Persian caption, and styled action keyboard.
        """
        classified = self.classify_deliverable_type(chosen_file["filename"])
        fin_gate = self.check_financial_gate(project_dir, target_phase=classified["financial_phase"])

        client_link = html.escape(client_name)
        if username:
            client_link = f"<a href=\"https://t.me/{username.lstrip('@')}\">{html.escape(client_name)}</a>"
        elif telegram_id:
            client_link = f"<a href=\"tg://user?id={telegram_id}\">{html.escape(client_name)}</a>"

        deliv_payload = {
            **classified,
            "filename": chosen_file.get("filename", "")
        }
        caption_text = self.generate_delivery_manifest_caption(client_name, deliv_payload, all_deliverables=all_files)

        header_lines = [
            "╭─ 📦 <b>CLIENT DELIVERABLE DISPATCH READY</b> ─────────",
            f"│ 👤 <b>Client:</b> {client_link}  •  <code>#{telegram_id or 'ID'}</code>",
            f"│ 📄 <b>File:</b> <code>{html.escape(chosen_file['filename'])}</code> ({chosen_file.get('size_str', 'N/A')})",
            f"│ 🏷️ <b>Category:</b> {classified['icon']} {classified['title_fa']}",
            f"│ 💳 <b>Financial Gate:</b> {fin_gate['badge']}",
            f"│ 🆔 <b>Dispatch ID:</b> <code>{del_id}</code>",
            "╰──────────────────────────────────────────────────"
        ]

        card_text = (
            f"{chr(10).join(header_lines)}\n\n"
            f"<b>Financial Gate Details:</b>\n"
            f"▫️ {fin_gate['status_str']}\n\n"
            f"📝 <b>AUTOGENERATED PERSIAN DELIVERY MANIFEST</b>\n"
            f"<blockquote expandable>{caption_text}</blockquote>\n\n"
            f"<i>Tap below to dispatch file directly to client chat:</i>"
        )

        # Build 2-row action keyboard
        btns = None
        if Button is not None:
            row1 = [Button.inline(f"🚀 Dispatch File ({del_id})", f"send_del_{del_id}".encode("utf-8"), style="success")]
            if len(all_files) > 1:
                row2 = [
                    Button.inline(f"📦 Bundle Zip All ({len(all_files)} files)", f"bundle_del_{del_id}".encode("utf-8"), style="primary"),
                    Button.switch_inline("✏️ Custom Caption", f"/send_del_{del_id} ", same_peer=True)
                ]
            else:
                row2 = [
                    Button.switch_inline("✏️ Custom Caption", f"/send_del_{del_id} ", same_peer=True),
                    Button.inline("🗑️ Dismiss", f"ignore_del_{del_id}".encode("utf-8"), style="danger")
                ]
            row3 = [Button.inline("🗑️ Dismiss", f"ignore_del_{del_id}".encode("utf-8"), style="danger")] if len(all_files) > 1 else None
            btns = [row1, row2]
            if row3:
                btns.append(row3)

        return card_text, btns, caption_text
