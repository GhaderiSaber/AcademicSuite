#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Defense Committee Viva Voce Card Generator (generate_defense_card_docx.py)
--------------------------------------------------------------------------
Generates official Microsoft Word (.docx) Viva Voce preparation booklets:
- Committee Examiner Profiles & Defense Readiness Index
- Anticipated Examiner Challenges in Academic Persian
- High-scoring Model Student Responses with APA 7 Evidence & Methodological Justifications
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from typing import Dict, Any, Optional

VERIF_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_DIR = os.path.abspath(os.path.join(VERIF_DIR, ".."))
SHARED_DIR = os.path.join(AGENTS_DIR, "shared")

if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)

from openxml_artifact_engine import OpenXMLArtifactEngine


def build_defense_card_document(defense_data: Dict[str, Any], output_path: str) -> str:
    """Compiles the thesis defense committee preparation booklet docx."""
    engine = OpenXMLArtifactEngine()
    doc = docx.Document()

    # Standard margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.right_margin = Inches(1.18)
        section.left_margin = Inches(1.0)

    topic = defense_data.get("topic") or defense_data.get("project_title") or "پژوهش دانشگاهی علوم رفتاری"
    readiness_score = defense_data.get("readiness_score", 96.0)
    challenges = defense_data.get("challenges") or [
        {
            "examiner_role": "متخصص روش‌شناسی و آمار (Methodology Expert)",
            "challenge_fa": "چرا به جای تحلیل کوواریانس (ANCOVA)، از آزمون t مستقل روی نمرات تفاضلی (Gain Scores) استفاده نکردید؟",
            "model_answer_fa": (
                "با تشکر از تذکر دقیق استاد محترم؛ استفاده از نمرات تفاضلی به دلیل پدیده رگرسیون به میانگین (Regression toward the mean) "
                "و عدم کنترل خطای اندازه‌گیری پیش‌آزمون در مطالعات نیمه‌آزمایشی دچار سوگیری سیستماتیک می‌شود. بر اساس هاوک و مک‌لین (1975) "
                "و لرد (1967)، تحلیل کوواریانس با مدل‌سازی واریانس خطای پیش‌آزمون، توان آماری را تا ۳۰ درصد ارتقا می‌دهد."
            ),
            "apa7_evidence": "Huck & McLean (1975); Lord's Paradox (Lord, 1967); Hayes (2018)"
        },
        {
            "examiner_role": "داور خارجی (External Examiner)",
            "challenge_fa": "آیا حجم نمونه شما (۳۴ نفر) برای آزمون‌های پیشرفته چندمتغیری و اندازه‌گیری مکرر کفایت آماری داشته است؟",
            "model_answer_fa": (
                "کاملاً متین است؛ حجم نمونه بر پایه تحلیل توان پیش‌آزمون (A-Priori Power Analysis) در نرم‌افزار G*Power 3.1 با اندازه اثر "
                "متوسط f = 0.28، سطح آلفای ۰/۰۵ و توان آماری ۰/۸۵ تعیین گردید که حداقل نمونه ۲۸ نفر محاسبه شد و با احتساب ریزش ۱۵ درصدی "
                "به ۳۴ نفر افزایش یافت."
            ),
            "apa7_evidence": "Faul, Erdfelder, Lang, & Buchner (2007); Cohen (1988)"
        },
        {
            "examiner_role": "داور داخلی (Internal Examiner)",
            "challenge_fa": "مکانیسم دقیق روان‌شناختی درمان شما که منجر به کاهش فرسودگی شغلی گردیده چیست؟ آیا کاهش ناشی از گسلش بوده یا پذیرش؟",
            "model_answer_fa": (
                "مطابق با مدل شش‌ضلعی انعطاف‌پذیری روان‌شناختی هیز (2019)، فرایند گسلش شناختی با شکستن درآمیختگی افکار ناکارآمد شغلی و "
                "پذیرش تجربی با متوقف ساختن اجتناب تجربه‌ای، موجب کاهش نشخوار فکری و در نتیجه تقلیل فرسودگی عاطفی شده است."
            ),
            "apa7_evidence": "Hayes, Strosahl, & Wilson (2019); McCracken & Vowles (2014)"
        },
        {
            "examiner_role": "استاد راهنما (Supervisor Review)",
            "challenge_fa": "چگونه پایایی دستاوردهای درمانی را در بلندمدت و فاز پیگیری ارزیابی کرده‌اید؟",
            "model_answer_fa": (
                "به‌منظور بررسی ماندگاری اثر، ارزیابی پیگیری ۲ ماهه اجرا گردید و آزمون مقایسه‌های تعقیبی بنفرونی نشان داد که تفاوت مرحله "
                "پس‌آزمون با پیگیری معنادار نبوده (p = .412)، که حاکی از تثبیت کامل مهارت‌های درمانی در رفتار آزمودنی‌هاست."
            ),
            "apa7_evidence": "Greenhouse & Geisser (1959); Field (2018)"
        }
    ]

    # 1. Document Title
    p_title = doc.add_paragraph()
    engine.set_strict_pPr(p_title, jc_val='center', space_before=16, space_after=8)
    engine.add_styled_run(p_title, "کارت راهنمای جامع جلسه دفاع و سوالات داوران", font_fa='B Titr', size=17, bold=True, color="1B365D")

    p_sub = doc.add_paragraph()
    engine.set_strict_pPr(p_sub, jc_val='center', space_before=0, space_after=18)
    engine.add_styled_run(p_sub, "شبیه‌ساز سناریوهای داوری، سوالات چالشی و الگوهای پاسخ مستدل (Viva Voce Simulator)", font_fa='B Titr', size=12, bold=False, color="4A5568")

    # 2. Executive Readiness Card
    tbl_card = doc.add_table(rows=3, cols=2)
    tbl_card.alignment = WD_TABLE_ALIGNMENT.CENTER
    engine.style_apa_table(tbl_card, col_widths=[4.5, 2.0])

    card_items = [
        ("عنوان پژوهش / رساله دفاع:", topic),
        ("شاخص آمادگی دفاعی (Readiness Index):", f"{readiness_score:.1f}% [سطح عالی / آمادگی کامل دفاع]"),
        ("تعداد سناریوهای پیش‌بینی‌شده:", f"{len(challenges)} چالش اصلی در متدولوژی، آمار و تبیین نظری")
    ]

    for idx, (label, val) in enumerate(card_items):
        row_cells = tbl_card.rows[idx].cells
        p_lbl = row_cells[1].paragraphs[0]
        engine.set_strict_pPr(p_lbl, jc_val='both')
        engine.add_styled_run(p_lbl, label, font_fa='B Nazanin', size=11, bold=True)

        p_val = row_cells[0].paragraphs[0]
        engine.set_strict_pPr(p_val, jc_val='both')
        val_color = "007A3D" if "%" in val else "1A202C"
        engine.add_styled_run(p_val, val, font_fa='B Nazanin', size=11, bold=False, color=val_color)

    # 3. Detailed Challenges & Responses
    p_h = doc.add_paragraph()
    engine.set_strict_pPr(p_h, space_before=20, space_after=10)
    engine.add_styled_run(p_h, "سناریوهای شبیه‌سازی‌شده هیئت داوران به همراه مدل پاسخ‌های مستدل", font_fa='B Titr', size=14, bold=True, color="1B365D")

    for idx, c in enumerate(challenges, 1):
        # Examiner header box
        p_role = doc.add_paragraph()
        engine.set_strict_pPr(p_role, space_before=14, space_after=4)
        engine.add_styled_run(p_role, f"چالش شماره {idx} — نقش داور: ", font_fa='B Titr', size=12, bold=True, color="1B365D")
        engine.add_styled_run(p_role, c["examiner_role"], font_fa='B Nazanin', size=12, bold=True, color="2B6CB0")

        # Question
        p_q = doc.add_paragraph()
        engine.set_strict_pPr(p_q, jc_val='both', space_before=2, space_after=4)
        engine.add_styled_run(p_q, "❓ سوال احتمالی داور: ", font_fa='B Nazanin', size=11, bold=True, color="C53030")
        engine.add_styled_run(p_q, c["challenge_fa"], font_fa='B Nazanin', size=11, bold=False)

        # Model Answer
        p_ans = doc.add_paragraph()
        engine.set_strict_pPr(p_ans, jc_val='both', space_before=2, space_after=4)
        engine.add_styled_run(p_ans, "💬 مدل پاسخ مستدل دانشجو: ", font_fa='B Nazanin', size=11, bold=True, color="007A3D")
        engine.add_styled_run(p_ans, c["model_answer_fa"], font_fa='B Nazanin', size=11, bold=False)

        # Evidence
        p_ev = doc.add_paragraph()
        engine.set_strict_pPr(p_ev, jc_val='both', space_before=2, space_after=10)
        engine.add_styled_run(p_ev, "📚 شواهد و رفرنس‌های APA 7: ", font_fa='B Nazanin', size=10, bold=True, color="4A5568")
        engine.add_styled_run(p_ev, c["apa7_evidence"], font_en='Times New Roman', size=10, bold=False, italic=True)

    # Save document
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc.save(output_path)
    return output_path


if __name__ == "__main__":
    test_out = os.path.join(AGENTS_DIR, "output", "Defense_Viva_Card_and_Questions.docx")
    build_defense_card_document({}, test_out)
    print(f"Defense card created at {test_out}")
