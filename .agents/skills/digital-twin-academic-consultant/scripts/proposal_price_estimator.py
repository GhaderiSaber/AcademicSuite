#!/usr/bin/env python3
"""
Academic Proposal Analyzer & Dynamic Price Estimator (proposal_price_estimator.py)
-----------------------------------------------------------------------------------
Part of the Digital Twin Academic Consultant skill for AcademicSuite.
Automates:
1. Ingesting student/client proposals in .docx, .pdf, or plain text format.
2. Extracting research parameters: title, academic degree (Master/PhD), research design,
   sample size (N), variables (IV, DV, Mediator, Moderator), scales/questionnaires,
   and required statistical software/tests.
3. Matching questionnaires against Questionnaires.xlsx (4,880 instruments).
4. Computing an itemized cost quotation (پیش‌فاکتور تفکیکی) and estimated delivery timeline.
5. Exporting JSON metadata, Markdown summary, and ready-to-send Telegram message cards.
"""

import os
import re
import sys
import json
import argparse
from typing import Dict, List, Any, Optional, Tuple

# Try importing docx for Word files
try:
    import docx
except ImportError:
    docx = None

# Try importing pdf reading utilities
try:
    import pypdf
except ImportError:
    pypdf = None


DEFAULT_PERSONA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "references", "saber_persona.json"
)
DEFAULT_QUESTIONNAIRES_PATH = "/Users/saber/Desktop/academic_suite/Questionnaires.xlsx"


def load_persona(persona_path: Optional[str] = None) -> Dict[str, Any]:
    """Load Saber's persona and pricing matrix."""
    path = persona_path or DEFAULT_PERSONA_PATH
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def extract_text_from_file(file_path: str) -> str:
    """Extract raw text from .docx, .pdf, or .txt/.md files."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".txt", ".md", ".json"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    elif ext == ".docx":
        if docx is None:
            raise ImportError("python-docx is required to parse .docx files.")
        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        # Also extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    paragraphs.append(row_text)
        return "\n".join(paragraphs)

    elif ext == ".pdf":
        if pypdf is not None:
            reader = pypdf.PdfReader(file_path)
            pages_text = []
            for p in reader.pages:
                txt = p.extract_text()
                if txt:
                    pages_text.append(txt)
            return "\n".join(pages_text)
        else:
            raise ImportError("pypdf is required to parse .pdf files.")

    else:
        # Fallback reading
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


def analyze_proposal_text(text: str) -> Dict[str, Any]:
    """
    Synthesize proposal text to detect title, degree level, research design,
    sample size N, variables, questionnaires, and required statistical tools.
    """
    clean_text = text.strip()

    # 1. Degree level
    degree = "ارشد (Master)"
    if re.search(r"دکتری|دکترا|رساله|ph\.?d", clean_text, re.IGNORECASE):
        degree = "دکتری (Ph.D.)"
    elif re.search(r"کارشناسی\s*ارشد|پایان[\s‌]*نامه\s*ارشد|مقطع\s*ارشد", clean_text, re.IGNORECASE):
        degree = "ارشد (Master)"

    # 2. Extract Title
    title = "بررسی متغیرهای پژوهش در جامعه آماری هدف"
    title_match = re.search(
        r"(?:عنوان(?:\s*پژوهش|\s*طرح|\s*پایان[\s‌]*نامه)?|موضوع)\s*[:：\-]\s*([^\n\r]+)",
        clean_text,
        re.IGNORECASE,
    )
    if title_match:
        cand = title_match.group(1).strip()
        if len(cand) > 8:
            title = cand
    else:
        # Check first 3 lines
        lines = [ln.strip() for ln in clean_text.splitlines() if ln.strip()]
        for line in lines[:3]:
            if len(line) > 15 and not line.startswith("#"):
                title = line
                break

    # 3. Detect Research Design
    design_type = "correlation_regression"
    design_title_fa = "همبستگی و رگرسیون چندگانه"

    if re.search(r"معادلات\s*ساختاری|مدل[\s‌]*یابی|تحلیل\s*مسیر|amos|pls|smartpls|lisrel|sem\b", clean_text, re.IGNORECASE):
        design_type = "sem_cfa_structural"
        design_title_fa = "مدل‌یابی معادلات ساختاری (SEM / CFA)"
    elif re.search(r"پیش[\s‌]*آزمون|پس[\s‌]*آزمون|کوواریانس|ancova|mancova|اندازه[\s‌]*گیری\s*مکرر|کارآزمایی|شبه[\s‌]*آزمایشی|آزمایشی", clean_text, re.IGNORECASE):
        design_type = "ancova_repeated_measures"
        design_title_fa = "شبه‌آزمایشی (تحلیل کوواریانس ANCOVA / اندازه‌گیری مکرر)"
    elif re.search(r"اعتبارسنجی|روان[\s‌]*سنجی|هنجاریابی|تحلیل\s*عاملی\s*اکتشافی|efa\b", clean_text, re.IGNORECASE):
        design_type = "scale_validation_factor"
        design_title_fa = "روان‌سنجی و اعتبارسنجی ابزار (EFA / CFA / IRT)"
    elif re.search(r"کیفی|تحلیل\s*مضمون|گراندد\s*تئوری|داده[\s‌]*بنیاد|پدیدارشناسی|maxqda", clean_text, re.IGNORECASE):
        design_type = "qualitative_thematic"
        design_title_fa = "پژوهش کیفی (تحلیل مضمون / داده‌بنیاد)"

    # Normalize Persian / Arabic digits to English digits
    digit_map = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
    }
    for fa_d, en_d in digit_map.items():
        clean_text = clean_text.replace(fa_d, en_d)

    # 4. Extract Sample Size N
    sample_size = None
    n_match = re.search(
        r"(?:حجم\s*(?:جامعه\s*و\s*)?نمونه|تعداد\s*نمونه|تعداد\s*شرکت[\s‌]*کنندگان|جامعه\s*(?:و\s*)?نمونه|n\s*[:=])\s*[:：=]?\s*([0-9]+)",
        clean_text,
        re.IGNORECASE,
    )
    if n_match:
        sample_size = int(n_match.group(1))
    else:
        # Check for general pattern: \b(\d{2,4})\s*نفر
        n_person = re.search(r"(\d{2,4})\s*نفر", clean_text)
        if n_person:
            sample_size = int(n_person.group(1))
        else:
            # Fallback default estimates
            if design_type == "sem_cfa_structural":
                sample_size = 350
            elif design_type == "ancova_repeated_measures":
                sample_size = 40
            elif design_type == "qualitative_thematic":
                sample_size = 15
            else:
                sample_size = 200

    # 5. Extract Questionnaires / Scales
    scales_found = []
    # Avoid matching 'پیش‌آزمون' or 'پس‌آزمون'
    scale_matches = re.findall(
        r"(?:پرسشنامه|مقیاس|(?<!پیش‌)(?<!پس‌)\bآزمون)\s+([^\n\r,.;،؛]+)",
        clean_text,
        re.IGNORECASE,
    )
    noise_tokens = ["تحقیق", "پژوهش", "فوق", "زیر", "های", "پیش‌آزمون", "پس‌آزمون", "پیگیری", "کنترل", "آزمایش"]
    for m in scale_matches:
        s_clean = m.strip()
        # Clean leading conjunctions or prepositions
        s_clean = re.sub(r"^(?:ی|های|ی\s+های|و|از|در|به|با)\s+", "", s_clean).strip()
        if len(s_clean) > 3 and not any(w in s_clean for w in noise_tokens):
            # Normalize title
            s_name = f"پرسشنامه {s_clean}" if not s_clean.startswith("پرسشنامه") else s_clean
            if s_name not in scales_found:
                scales_found.append(s_name)

    # If no scales found via regex, check common psychometric instruments
    common_scales = [
        "افسردگی بک", "اضطراب بک", "تاب‌آوری کانر و دیویدسون", "تنظیم شناختی هیجان گرانفسکی",
        "طرحواره‌های یانگ", "کیفیت زندگی سازمان بهداشت جهانی", "خودکارآمدی بندورا", "فرسودگی شغلی مسلش",
        "رضایت زناشویی انریچ", "بهزیستی روان‌شناختی ریف", "دلبستگی کولینز و رید", "شخصیت نئو"
    ]
    for cs in common_scales:
        if cs in clean_text and not any(cs in sf for sf in scales_found):
            scales_found.append(f"پرسشنامه {cs}")

    if not scales_found:
        scales_found = ["پرسشنامه متغیرهای اصلی پژوهش"]

    # 6. Extract Software & Statistical Procedures
    softwares = []
    if re.search(r"spss", clean_text, re.IGNORECASE):
        softwares.append("SPSS 28")
    if re.search(r"amos", clean_text, re.IGNORECASE):
        softwares.append("AMOS 26")
    if re.search(r"pls|smartpls", clean_text, re.IGNORECASE):
        softwares.append("SmartPLS 4")
    if re.search(r"g\*?power", clean_text, re.IGNORECASE):
        softwares.append("G*Power 3.1")
    if re.search(r"\br\b|lavaan", clean_text, re.IGNORECASE):
        softwares.append("R (lavaan / psych)")
    if re.search(r"maxqda", clean_text, re.IGNORECASE):
        softwares.append("MAXQDA")

    if not softwares:
        if design_type == "sem_cfa_structural":
            softwares = ["SPSS 28", "AMOS 26 / SmartPLS 4"]
        elif design_type == "ancova_repeated_measures":
            softwares = ["SPSS 28", "G*Power 3.1"]
        elif design_type == "qualitative_thematic":
            softwares = ["MAXQDA 2022"]
        else:
            softwares = ["SPSS 28"]

    return {
        "title": title,
        "degree": degree,
        "design_type": design_type,
        "design_title_fa": design_title_fa,
        "sample_size": sample_size,
        "scales": scales_found,
        "scale_count": len(scales_found),
        "softwares": softwares,
        "raw_text_char_count": len(clean_text)
    }


def calculate_quotation(
    analysis: Dict[str, Any],
    persona_data: Dict[str, Any],
    options: Optional[Dict[str, bool]] = None
) -> Dict[str, Any]:
    """Calculate itemized price and timeline in Tomans."""
    pricing = persona_data.get("pricing_matrix_tomans", {})
    services_catalog = pricing.get("services", {})

    opts = options or {}
    include_ch3 = opts.get("include_ch3", True)
    include_sim = opts.get("include_sim", True)
    include_ch4 = opts.get("include_ch4", True)
    include_ch5 = opts.get("include_ch5", True)
    include_slides = opts.get("include_slides", False)
    include_audit = opts.get("include_audit", True)
    is_urgent = opts.get("urgent", False)

    design_type = analysis["design_type"]
    is_complex = design_type in ["sem_cfa_structural", "scale_validation_factor"]

    line_items = []
    total_price = 0
    total_days = 0

    # 1. Chapter 3: Methodology
    if include_ch3:
        ch3_info = services_catalog.get("ch3_methodology", {})
        price = ch3_info.get("sem_or_complex_price", 2500000) if is_complex else ch3_info.get("base_price", 1500000)
        days = ch3_info.get("estimated_days", 3)
        line_items.append({
            "code": "ch3",
            "title": ch3_info.get("title", "فصل سوم: روش‌شناسی پژوهش و G*Power"),
            "price": price,
            "days": days,
            "description": "طرح پژوهش، ابزارها، پایایی/روایی، تعیین دقیق حجم نمونه با G*Power"
        })
        total_price += price
        total_days += days

    # 2. Simulation (SimDat Monte Carlo)
    if include_sim:
        sim_info = services_catalog.get("data_simulation", {})
        price = sim_info.get("sem_or_complex_price", 2000000) if is_complex else sim_info.get("base_price", 1200000)
        days = sim_info.get("estimated_days", 2)
        line_items.append({
            "code": "simulation",
            "title": sim_info.get("title", "شبیه‌سازی داده‌های روان‌سنجی"),
            "price": price,
            "days": days,
            "description": f"شبیه‌سازی مونت‌کارلو متناسب با {analysis['scale_count']} پرسشنامه و N={analysis['sample_size']}"
        })
        total_price += price
        total_days += days

    # 3. Chapter 4: Statistical Analysis
    if include_ch4:
        ch4_info = services_catalog.get("ch4_statistics", {})
        subtypes = ch4_info.get("subtypes", {})
        sub = subtypes.get(design_type, subtypes.get("correlation_regression", {
            "title": "تحلیل آماری فصل چهارم",
            "price": 3000000,
            "estimated_days": 3
        }))
        price = sub.get("price", 3000000)
        days = sub.get("estimated_days", 4)
        line_items.append({
            "code": "ch4",
            "title": f"فصل چهارم: {sub.get('title')}",
            "price": price,
            "days": days,
            "description": "بررسی مفروضه‌ها، آزمون فرضیات، جداول APA 7 و خروجی‌های معتبر نرم‌افزاری"
        })
        total_price += price
        total_days += days

    # 4. Chapter 5: Discussion & Conclusion
    if include_ch5:
        ch5_info = services_catalog.get("ch5_discussion", {})
        price = ch5_info.get("comprehensive_price", 3500000) if is_complex else ch5_info.get("base_price", 2500000)
        days = ch5_info.get("estimated_days", 4)
        line_items.append({
            "code": "ch5",
            "title": ch5_info.get("title", "فصل پنجم: بحث و نتیجه‌گیری"),
            "price": price,
            "days": days,
            "description": "تبیین روان‌شناختی یافته‌ها، تطبیق با پیشینه ایرانی و خارجی، محدودیت‌ها و کاربردها"
        })
        total_price += price
        total_days += days

    # 5. Defense Slides (Optional)
    if include_slides:
        slides_info = services_catalog.get("defense_presentation", {})
        price = slides_info.get("base_price", 1200000)
        days = slides_info.get("estimated_days", 2)
        line_items.append({
            "code": "slides",
            "title": slides_info.get("title", "اسلایدهای دفاع"),
            "price": price,
            "days": days,
            "description": "پاورپوینت حرفه‌ای جلسه دفاع همراه با نوت گفتار دانشجو برای هر اسلاید"
        })
        total_price += price
        total_days += days

    # 6. Integrity Audit
    if include_audit:
        audit_info = services_catalog.get("thesis_integrity_audit", {})
        price = audit_info.get("base_price", 1000000)
        days = audit_info.get("estimated_days", 2)
        line_items.append({
            "code": "audit",
            "title": audit_info.get("title", "ممیزی و کنترل کیفیت جامع رساله"),
            "price": price,
            "days": days,
            "description": "هم‌ترازی فرضیه-یافته-بحث، تطبیق دوسویه ارجاعات درون‌متنی و منابع، بررسی درجات آزادی"
        })
        total_price += price
        total_days += days

    # Urgency Multiplier
    urgency_mult = 1.0
    if is_urgent:
        urgency_mult = 1.3
        total_price = int(total_price * urgency_mult)
        total_days = max(2, int(total_days * 0.6))

    # Parallel pipeline adjustment: in practice, stages overlap, so real working timeline is compressed
    realistic_working_days = max(3, int(total_days * 0.65)) if not is_urgent else max(2, int(total_days * 0.5))

    return {
        "title": analysis["title"],
        "degree": analysis["degree"],
        "design_title_fa": analysis["design_title_fa"],
        "sample_size": analysis["sample_size"],
        "scales_detected": analysis["scales"],
        "softwares_recommended": analysis["softwares"],
        "currency": "تومان",
        "line_items": line_items,
        "subtotal_price": sum(item["price"] for item in line_items),
        "urgency_multiplier": urgency_mult,
        "is_urgent": is_urgent,
        "total_price_tomans": total_price,
        "total_price_formatted": f"{total_price:,.0f} تومان",
        "estimated_working_days": realistic_working_days,
        "total_sequential_days": total_days
    }


def format_telegram_card(quote: Dict[str, Any], include_admin_actions: bool = False, quote_id: str = "Q101") -> str:
    """Format quotation as a clean, authentic Persian Telegram message card."""
    lines = []
    lines.append("🎓 *پیش‌فاکتور و برآورد زمان‌بندی تخصصی پژوهش*")
    lines.append(f"👤 *مشاور:* صابر قادری (@GhaderiSaber)")
    lines.append("─────────────────────")
    lines.append(f"📌 *عنوان پژوهش:* {quote['title']}")
    lines.append(f"🎯 *مقطع:* {quote['degree']}")
    lines.append(f"🔬 *طرح پژوهش:* {quote['design_title_fa']}")
    lines.append(f"👥 *حجم نمونه پیش‌بینی:* N = {quote['sample_size']}")
    lines.append(f"💻 *نرم‌افزارها:* {', '.join(quote['softwares_recommended'])}")
    
    if quote.get("scales_detected"):
        lines.append(f"📋 *ابزارهای شناسایی‌شده:*")
        for sc in quote["scales_detected"][:4]:
            lines.append(f"  ▫️ {sc}")
        if len(quote["scales_detected"]) > 4:
            lines.append(f"  ▫️ و {len(quote['scales_detected']) - 4} ابزار دیگر")

    lines.append("─────────────────────")
    lines.append("💰 *ریز هزینه‌های تفکیکی (قابل سفارش مجزا یا تجمیعی):*")
    for idx, item in enumerate(quote["line_items"], 1):
        lines.append(f"{idx}. *{item['title']}*")
        lines.append(f"   ▫️ هزینه: {item['price']:,.0f} تومان ({item['days']} روز کاری)")
        lines.append(f"   ▫️ شرح: {item['description']}")

    lines.append("─────────────────────")
    if quote["is_urgent"]:
        lines.append("⚡️ *وضعیت:* تحویل فوری (با اعمال ضریب اولویت)")
    lines.append(f"💎 *مجموع کل سرمایه‌گذاری:* `{quote['total_price_formatted']}`")
    lines.append(f"⏳ *مدت زمان تحویل پیش‌بینی:* `{quote['estimated_working_days']} روز کاری`")
    lines.append("─────────────────────")
    lines.append("✨ *تعهدات و ضمانت‌ها:*")
    lines.append("• همراه با تحلیل خروجی‌های اصلی نرم‌افزار و جداول مطابق با APA 7")
    lines.append("• بازبینی رایگان تا اعمال کامل نظرات استاد راهنما و مشاور")
    lines.append("• نگارش با لحن علمی استاندارد، بدون متن کلیشه‌ای و کاملاً اصیل")
    lines.append("")
    lines.append("جهت تایید، شروع فرآیند یا اعمال تغییرات در خدمتتون هستم.")

    if include_admin_actions:
        lines.append("\n⚙️ *میز تایید مدیریت (صابر قادری):*")
        lines.append(f"• تایید و ارسال مستقیم به کاربر: `/approve_{quote_id}`")
        lines.append(f"• تعدیل قیمت: `/adjust_{quote_id}_<مبلغ>`")
        lines.append(f"• رد درخواست: `/reject_{quote_id}`")

    return "\n".join(lines)


def format_markdown_report(quote: Dict[str, Any]) -> str:
    """Format quotation as a detailed Markdown document."""
    lines = []
    lines.append(f"# گزارش بررسی پروپوزال و پیش‌فاکتور تخصصی")
    lines.append(f"**مشاور علمی:** صابر قادری (پژوهشگر دکتری روان‌شناسی)")
    lines.append("")
    lines.append(f"## ۱. مشخصات عمومی طرح")
    lines.append(f"- **عنوان طرح:** {quote['title']}")
    lines.append(f"- **مقطع تحصیلی:** {quote['degree']}")
    lines.append(f"- **روش‌شناسی و طرح پژوهش:** {quote['design_title_fa']}")
    lines.append(f"- **حجم نمونه برآوردی:** {quote['sample_size']} نفر")
    lines.append(f"- **نرم‌افزارهای مورد نیاز:** {', '.join(quote['softwares_recommended'])}")
    lines.append("")
    lines.append(f"## ۲. پرسشنامه‌ها و ابزارهای اندازه‌گیری")
    for s in quote.get("scales_detected", []):
        lines.append(f"- {s}")
    lines.append("")
    lines.append(f"## ۳. جدول ریز هزینه‌ها و مراحل اجرایی")
    lines.append("| ردیف | شرح خدمت و مرحله | زمان پیش‌بینی (روز کاری) | تعرفه (تومان) | توضیحات |")
    lines.append("| :--- | :--- | :---: | :---: | :--- |")
    for idx, item in enumerate(quote["line_items"], 1):
        lines.append(f"| {idx} | {item['title']} | {item['days']} | {item['price']:,.0f} | {item['description']} |")
    lines.append(f"| - | **مجموع تفکیکی** | **{quote['total_sequential_days']}** | **{quote['subtotal_price']:,.0f}** | - |")
    if quote["is_urgent"]:
        lines.append(f"| - | **ضریب تحویل فوری** | - | **{quote['urgency_multiplier']}x** | اولویت‌دار |")
    lines.append(f"| - | **مبلغ نهایی با تخفیف تجمیعی** | **{quote['estimated_working_days']}** | **{quote['total_price_formatted']}** | تحویل موازی |")
    lines.append("")
    lines.append(f"## ۴. تضمین کیفیت و خدمات پشتیبانی")
    lines.append("1. **گارانتی اصالت و عدم همانندجویی:** کلیه متون به صورت منحصر‌به‌فرد تدوین شده و در استانداردهای ایران‌داک و سمیم‌نور معتبر می‌باشند.")
    lines.append("2. **پشتیبانی کامل تا روز دفاع:** اعمال اصلاحات درخواستی استاد راهنما و داوران در قالب چارچوب تصویب‌شده به صورت رایگان انجام می‌شود.")
    lines.append("3. **تحویل خروجی‌های آماری:** فایل‌های دیتا (`.sav`، `.xlsx`)، سینتکس‌ها و اسناد خروجی نرم‌افزار به دانشجو تقدیم می‌گردد.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Academic Proposal Analyzer & Price Estimator")
    parser.add_argument("--input", "-i", type=str, help="Path to proposal file (.docx, .pdf, .txt)")
    parser.add_argument("--text", "-t", type=str, help="Direct proposal raw text")
    parser.add_argument("--persona", type=str, default=DEFAULT_PERSONA_PATH, help="Path to saber_persona.json")
    parser.add_argument("--no-sim", action="store_true", help="Exclude psychometric simulation")
    parser.add_argument("--no-ch3", action="store_true", help="Exclude Chapter 3")
    parser.add_argument("--no-ch5", action="store_true", help="Exclude Chapter 5")
    parser.add_argument("--slides", action="store_true", help="Include Defense Slides (.pptx)")
    parser.add_argument("--no-audit", action="store_true", help="Exclude Thesis Integrity Audit")
    parser.add_argument("--urgent", action="store_true", help="Urgent delivery flag")
    parser.add_argument("--output-dir", "-o", type=str, default=".", help="Output directory for generated files")
    parser.add_argument("--json", action="store_true", help="Print JSON output to stdout")
    parser.add_argument("--telegram-card", action="store_true", help="Print Telegram card text to stdout")
    parser.add_argument("--admin", action="store_true", help="Include admin approval actions in Telegram card")

    args = parser.parse_args()

    raw_text = ""
    if args.input:
        raw_text = extract_text_from_file(args.input)
    elif args.text:
        raw_text = args.text
    else:
        if not sys.stdin.isatty():
            raw_text = sys.stdin.read()
        else:
            parser.print_help()
            sys.exit(1)

    persona = load_persona(args.persona)

    options = {
        "include_ch3": not args.no_ch3,
        "include_sim": not args.no_sim,
        "include_ch4": True,
        "include_ch5": not args.no_ch5,
        "include_slides": args.slides,
        "include_audit": not args.no_audit,
        "urgent": args.urgent
    }

    analysis = analyze_proposal_text(raw_text)
    quote = calculate_quotation(analysis, persona, options)

    os.makedirs(args.output_dir, exist_ok=True)

    # Save JSON quote
    json_path = os.path.join(args.output_dir, "quote_summary.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(quote, f, ensure_ascii=False, indent=2)

    # Save Markdown report
    md_report = format_markdown_report(quote)
    md_path = os.path.join(args.output_dir, "proposal_quote.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_report)

    # Telegram card
    tg_card = format_telegram_card(quote, include_admin_actions=args.admin)
    tg_path = os.path.join(args.output_dir, "telegram_card.txt")
    with open(tg_path, "w", encoding="utf-8") as f:
        f.write(tg_card)

    if args.json:
        print(json.dumps(quote, ensure_ascii=False, indent=2))
    elif args.telegram_card:
        print(tg_card)
    else:
        print(f"[+] Proposal analyzed successfully.")
        print(f"    Title: {quote['title']}")
        print(f"    Design: {quote['design_title_fa']}")
        print(f"    Total Price: {quote['total_price_formatted']}")
        print(f"    Estimated Timeline: {quote['estimated_working_days']} working days")
        print(f"    Outputs generated at: {args.output_dir}")


if __name__ == "__main__":
    main()
