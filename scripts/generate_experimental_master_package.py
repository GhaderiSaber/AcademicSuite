#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_experimental_master_package.py — Compiles the consolidated multi-modal deliverable package
for the Experimental RCT Vertical Slice:
1. Experimental_Study_Report.docx (OpenXML APA 7 consolidated thesis chapter)
2. Experimental_Study_Report.md (Consolidated markdown report)
3. experimental_analysis_matrix.xlsx (6-sheet Excel matrix)
4. experimental_trajectory_plots.png (300-DPI publication figure)
"""

import os
import sys
import json

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

OUTPUTS_DIR = os.path.join(ROOT_DIR, "projects", "study_vertical_slice_experimental", "academic-state", "outputs")
PACKAGE_DIR = os.path.join(OUTPUTS_DIR, "08_master_package")


def set_p_rtl(p, justify=True):
    pPr = p._element.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    pPr.append(bidi)
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT


def add_p(doc, text, font_name="B Nazanin", size=13, bold=False, italic=False):
    p = doc.add_paragraph()
    set_p_rtl(p, justify=True)
    r = p.add_run(text)
    r.font.name = font_name
    r.font.size = Pt(size)
    r.bold = bold
    r.italic = italic
    rPr = r._element.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)
    rPr.append(rFonts)
    rtl = OxmlElement('w:rtl')
    rPr.append(rtl)
    return p


def add_heading(doc, text, level=1):
    p = doc.add_paragraph()
    set_p_rtl(p, justify=False)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p.add_run(text)
    font_name = "B Titr"
    size = 15 if level == 1 else 13
    r.font.name = font_name
    r.font.size = Pt(size)
    r.bold = True
    rPr = r._element.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)
    rPr.append(rFonts)
    rtl = OxmlElement('w:rtl')
    rPr.append(rtl)
    return p


def add_table_header(doc, caption_text):
    p = doc.add_paragraph()
    set_p_rtl(p, justify=False)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p.add_run(caption_text)
    r.font.name = "B Nazanin"
    r.bold = True
    r.font.size = Pt(11)


def add_table_note(doc, note_text):
    p = doc.add_paragraph()
    set_p_rtl(p, justify=True)
    r = p.add_run(note_text)
    r.font.name = "B Nazanin"
    r.font.size = Pt(10)
    r.italic = True


def populate_apa_table(doc, headers, rows_data):
    tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = tbl._tbl.tblPr
    bidiVisual = OxmlElement('w:bidiVisual')
    tblPr.append(bidiVisual)

    for c_idx, h in enumerate(headers):
        cell = tbl.rows[0].cells[c_idx]
        p = cell.paragraphs[0]
        set_p_rtl(p, justify=False)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "B Nazanin"
        r.bold = True
        r.font.size = Pt(10)

    for r_idx, row_values in enumerate(rows_data):
        for c_idx, val in enumerate(row_values):
            cell = tbl.rows[r_idx + 1].cells[c_idx]
            p = cell.paragraphs[0]
            set_p_rtl(p, justify=False)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(val))
            r.font.name = "Times New Roman" if any(char.isdigit() or char in ["-", ">", "<", "p", "r", "R", "F", "*", "/", "t", "β", "B", "%", "CI", "W", "η", "χ"] for char in str(val)) else "B Nazanin"
            r.font.size = Pt(10)

    return tbl


def build_master_docx(out_path):
    doc = Document()
    
    # Title
    add_heading(doc, "فصل چهارم: یافته‌های پژوهش (گزارش جامع طرح کارآزمایی بالینی مداخله ACT)", level=1)
    add_p(doc, "این گزارش نتایج آماری جامع آزمون اثربخشی درمان مبتنی بر پذیرش و تعهد (ACT) بر کاهش اضطراب و انعطاف‌ناپذیری روان‌شناختی در یک طرح پیش‌آزمون-پس‌آزمون با گروه کنترل و دوره پیگیری دو ماهه (۶۰ = N) را ارائه می‌دهد.")

    # 1. Demographics
    add_heading(doc, "۱. ویژگی‌های جمعیت‌شناختی و بررسی همتاسازی گروه‌ها", level=2)
    add_table_header(doc, "جدول ۱. مشخصات جمعیت‌شناختی آزمودنی‌ها به تفکیک گروه و آزمون‌های برابری خط پایه (۶۰ = N)")
    headers_demo = ["متغیر جمعیت‌شناختی", "طبقات / شاخص", "گروه آزمایش (ACT) (n=30)", "گروه گواه (کنترل) (n=30)", "کل نمونه (N=60)", "آزمون همتاسازی"]
    rows_demo = [
        ["جنسیت", "مرد", "۱۶ (۵۳.۳٪)", "۱۴ (۴۶.۷٪)", "۳۰ (۵۰.۰٪)", "χ²(1) = 0.067, p = 0.796 (همتا)"],
        ["جنسیت", "زن", "۱۴ (۴۶.۷٪)", "۱۶ (۵۳.۳٪)", "۳۰ (۵۰.۰٪)", "-"],
        ["سن (سال)", "میانگین (انحراف معیار)", "۳۸.۲۷ (۸.۵۱)", "۳۲.۹۳ (۹.۸۲)", "۳۵.۶۰ (۹.۵۰)", "t(58) = 2.248, p = 0.028"],
        ["تحصیلات", "کارشناسی", "۱۱ (۳۶.۷٪)", "۱۵ (۵۰.۰٪)", "۲۶ (۴۳.۳٪)", "χ²(2) = 1.726, p = 0.422 (همتا)"],
        ["تحصیلات", "کارشناسی ارشد", "۱۵ (۵۰.۰٪)", "۱۰ (۳۳.۳٪)", "۲۵ (۴۱.۷٪)", "-"],
        ["تحصیلات", "دکتری تخصصی", "۴ (۱۳.۳٪)", "۵ (۱۶.۷٪)", "۹ (۱۵.۰٪)", "-"]
    ]
    populate_apa_table(doc, headers_demo, rows_demo)
    add_table_note(doc, "یادداشت. عدم معناداری آزمون‌های کای‌دو نشان‌دهنده توزیع متوازن و همتاسازی اولیه متغیرهای جمعیت‌شناختی در دو گروه است.")

    # 2. Descriptives
    add_heading(doc, "۲. شاخص‌های توصیفی و پایایی ابزارهای پژوهش", level=2)
    add_table_header(doc, "جدول ۲. شاخص‌های توصیفی نمرات اضطراب و انعطاف‌ناپذیری در مراحل سنجش به تفکیک گروه (۶۰ = N)")
    headers_desc = ["متغیر پژوهش", "مرحله سنجش", "گروه آزمایش (ACT) (n=30)", "گروه گواه (کنترل) (n=30)", "کل نمونه (N=60)"]
    rows_desc = [
        ["اضطراب (BAI)", "پیش‌آزمون", "۳.۴۲۶ (۰.۵۶۳)", "۳.۴۶۶ (۰.۵۱۸)", "۳.۴۴۶ (۰.۵۳۷)"],
        ["اضطراب (BAI)", "پس‌آزمون", "۲.۳۰۱ (۰.۳۹۷)", "۳.۵۳۴ (۰.۵۵۴)", "۲.۹۱۸ (۰.۷۸۴)"],
        ["اضطراب (BAI)", "پیگیری (۲ ماهه)", "۲.۳۵۱ (۰.۴۱۱)", "۳.۴۴۴ (۰.۵۲۹)", "۲.۸۹۷ (۰.۷۲۴)"],
        ["انعطاف‌ناپذیری (AAQ-II)", "پیش‌آزمون", "۳.۶۸۶ (۰.۶۰۰)", "۳.۴۹۸ (۰.۶۱۲)", "۳.۵۹۲ (۰.۶۰۸)"],
        ["انعطاف‌ناپذیری (AAQ-II)", "پس‌آزمون", "۲.۲۳۶ (۰.۳۹۳)", "۳.۴۹۸ (۰.۶۴۲)", "۲.۸۶۷ (۰.۸۲۶)"],
        ["انعطاف‌ناپذیری (AAQ-II)", "پیگیری (۲ ماهه)", "۲.۲۵۶ (۰.۳۷۱)", "۳.۵۰۵ (۰.۶۲۲)", "۲.۸۸۱ (۰.۸۰۹)"]
    ]
    populate_apa_table(doc, headers_desc, rows_desc)
    add_table_note(doc, "یادداشت. مقیاس اضطراب (α = ۰.۸۲۹، ω = ۰.۸۳۴) و مقیاس انعطاف‌ناپذیری (α = ۰.۸۹۵، ω = ۰.۸۹۸) از پایایی عالی برخوردارند.")

    # 3. Assumptions
    add_heading(doc, "۳. ارزیابی پیش‌فرض‌های آماری مدل‌های کوواریانس و اندازه‌گیری مکرر", level=2)
    add_table_header(doc, "جدول ۳. خلاصه آزمون‌های پیش‌فرض پارامتریک و ماتریس کوواریانس (۶۰ = N)")
    headers_assump = ["شاخص پیش‌فرض", "آزمون آماری", "آماره آزمون", "درجه آزادی", "سطح معناداری (p)", "نتیجه احراز"]
    rows_assump = [
        ["نرمال بودن اضطراب", "شاپیرو-ویلک (مراحل سه‌گانه)", "W ∈ [۰.۹۴۹, ۰.۹۸۳]", "۳۰", "p > ۰.۰۵", "تأیید نرمال بودن"],
        ["همگنی واریانس پس‌آزمون", "آزمون لوین", "F = ۳.۳۸۷", "(۱ و ۵۸)", "۰.۰۷۱ = p", "برقراری همگنی"],
        ["همگنی واریانس پیگیری", "آزمون لوین", "F = ۲.۸۴۶", "(۱ و ۵۸)", "۰.۰۹۷ = p", "برقراری همگنی"],
        ["همگنی ماتریس‌های کوواریانس", "آزمون ام باکس (Box's M)", "M = ۱۱.۴۴۵", "۶", "۰.۰۹۵ = p", "برقراری همگنی"],
        ["کرویت ماکلی", "آزمون کرویت ماکلی", "W = ۰.۶۷۰", "۲", "۰.۰۰۱ > p", "تعدیل گرین‌هاوس (ε = ۰.۷۵۲)"]
    ]
    populate_apa_table(doc, headers_assump, rows_assump)

    # 4. Hypothesis 1
    add_heading(doc, "۴. آزمون فرضیه اول: تحلیل کوواریانس پس‌آزمون اضطراب", level=2)
    add_table_header(doc, "جدول ۴. تحلیل کوواریانس تک‌متغیره اثر مداخله بر پس‌آزمون اضطراب با کنترل پیش‌آزمون")
    headers_h1 = ["منبع تغییرات", "مجموع مجذورات (SS)", "درجه آزادی (df)", "میانگین مجذورات (MS)", "آماره F", "سطح معناداری (p)", "اندازه اثر (η²p)"]
    rows_h1 = [
        ["پیش‌آزمون (همپراش)", "۴.۷۷۰", "۱", "۴.۷۷۰", "۴۴.۱۱۷", "۰.۰۰۱ > p", "۰.۴۳۶"],
        ["گروه (مداخله ACT)", "۲۲.۵۴۵", "۱", "۲۲.۵۴۵", "۲۰۸.۵۲۱", "۰.۰۰۱ > p", "۰.۷۸۵"],
        ["خطا", "۶.۱۶۳", "۵۷", "۰.۱۰۸", "-", "-", "-"]
    ]
    populate_apa_table(doc, headers_h1, rows_h1)
    add_table_note(doc, "یادداشت. میانگین‌های تعدیل‌شده: گروه آزمایش = ۲.۳۱۴ (SE = ۰.۰۶۰) در برابر گروه کنترل = ۳.۵۲۱ (SE = ۰.۰۶۰).")

    # 5. Hypothesis 2
    add_heading(doc, "۵. آزمون فرضیه دوم: پایداری اثربخشی در دوره پیگیری دو ماهه", level=2)
    add_table_header(doc, "جدول ۵. تحلیل کوواریانس تک‌متغیره نمرات پیگیری اضطراب با کنترل پیش‌آزمون")
    rows_h2 = [
        ["پیش‌آزمون (همپراش)", "۳.۸۶۳", "۱", "۳.۸۶۳", "۲۹.۳۲۹", "۰.۰۰۱ > p", "۰.۳۴۰"],
        ["گروه (مداخله ACT)", "۱۷.۳۶۷", "۱", "۱۷.۳۶۷", "۱۳۱.۸۷۰", "۰.۰۰۱ > p", "۰.۶۹۸"],
        ["خطا", "۷.۵۰۷", "۵۷", "۰.۱۳۲", "-", "-", "-"]
    ]
    populate_apa_table(doc, headers_h1, rows_h2)
    add_table_note(doc, "یادداشت. میانگین‌های تعدیل‌شده پیگیری: گروه آزمایش = ۲.۳۶۲ (SE = ۰.۰۶۶) در برابر گروه کنترل = ۳.۴۳۳ (SE = ۰.۰۶۶).")

    # 6. Hypothesis 3
    add_heading(doc, "۶. آزمون فرضیه سوم: تحلیل اندازه‌گیری مکرر آمیخته (تعامل گروه × زمان)", level=2)
    add_table_header(doc, "جدول ۶. نتایج تحلیل واریانس با اندازه‌گیری‌های مکرر آمیخته با تعدیل گرین‌هاوس-گایسر")
    headers_rm = ["منبع تغییرات", "مجموع مجذورات (SS)", "درجه آزادی اصلی", "درجه آزادی تعدیل‌شده", "آماره F", "سطح معناداری (p)", "اندازه اثر (η²p)"]
    rows_rm = [
        ["عامل زمان (درون‌آزمودنی)", "۱۱.۹۴۲", "۲", "۱.۵۰۴", "۷۲.۰۱۰", "۰.۰۰۱ > p", "۰.۵۵۴"],
        ["تعامل: زمان × گروه", "۱۲.۷۸۱", "۲", "۱.۵۰۴", "۷۷.۰۷۱", "۰.۰۰۱ > p", "۰.۵۷۱"],
        ["عامل گروه (بین‌آزمودنی)", "۳۳.۵۳۸", "۱", "۱.۰۰۰", "۸۱.۷۱۵", "۰.۰۰۱ > p", "۰.۵۸۵"],
        ["خطای درون‌آزمودنی", "۹.۶۱۸", "۱۱۶", "۸۷.۲۳۲", "-", "-", "-"]
    ]
    populate_apa_table(doc, headers_rm, rows_rm)

    # 7. Master Summary
    add_heading(doc, "۷. ماتریس جامع تصمیم‌گیری پیرامون فرضیه‌های پژوهش", level=2)
    add_table_header(doc, "جدول ۷. ماتریس جمع‌بندی نهایی فرضیه‌های سه‌گانه کارآزمایی بالینی (۶۰ = N)")
    headers_sum = ["شماره", "فرضیه پژوهش", "مدل آزمون", "آماره F", "درجات آزادی", "سطح معناداری (p)", "اندازه اثر (η²p)", "نتیجه نهایی"]
    rows_sum = [
        ["۱", "اثربخشی ACT بر کاهش اضطراب پس‌آزمون", "ANCOVA", "۲۰۸.۵۲", "(۱ و ۵۷)", "۰.۰۰۱ > p", "۰.۷۸۵", "تأیید قاطع"],
        ["۲", "ماندگاری اثربخشی ACT در پیگیری ۲ ماهه", "ANCOVA", "۱۳۱.۸۷", "(۱ و ۵۷)", "۰.۰۰۱ > p", "۰.۶۹۸", "تأیید قاطع"],
        ["۳", "اثر تعاملی زمان و گروه بر روند بهبودی", "Mixed RM-ANOVA", "۷۶.۰۱", "(۱.۵۰ و ۸۷.۲۳)", "۰.۰۰۱ > p", "۰.۵۷۱", "تأیید قاطع"]
    ]
    populate_apa_table(doc, headers_sum, rows_sum)
    add_table_note(doc, "یادداشت. برآیند نتایج آماری نشان‌دهنده اثربخشی پایدار و معنادار بالینی مداخله ACT با توان آزمون ۱۰۰٪ است.")

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    doc.save(out_path)
    print(f"Master DOCX successfully generated: {out_path}")


def build_master_md(out_path):
    # Read micro-stage markdowns and concatenate
    md_files = [
        ("01_demographics.md", "## ۱. ویژگی‌های جمعیت‌شناختی و همتا بودن آزمودنی‌ها"),
        ("02_descriptives_and_reliability.md", "## ۲. شاخص‌های توصیفی و پایایی ابزارهای پژوهش"),
        ("03_experimental_assumptions.md", "## ۳. بررسی پیش‌فرض‌های آماری مدل‌های کوواریانس و اندازه‌گیری مکرر"),
        ("06_hypothesis_1_ancova_post.md", "## ۴. آزمون فرضیه اول: تحلیل کوواریانس تک‌متغیره پس‌آزمون"),
        ("07_hypothesis_2_ancova_followup.md", "## ۵. آزمون فرضیه دوم: تحلیل کوواریانس مرحله پیگیری دو ماهه"),
        ("08_hypothesis_3_repeated_measures.md", "## ۶. آزمون فرضیه سوم: تحلیل اندازه‌گیری‌های مکرر آمیخته ۲×۳"),
        ("09_chapter_summary.md", "## ۷. ماتریس جامع تصمیم‌گیری و جمع‌بندی فصل چهارم")
    ]

    content = [
        "# فصل چهارم: یافته‌های پژوهش",
        "## گزارش جامع کارآزمایی بالینی اثربخشی درمان مبتنی بر پذیرش و تعهد (ACT) با دوره پیگیری دو ماهه",
        "",
        "---",
        ""
    ]

    for fname, section_header in md_files:
        fpath = os.path.join(OUTPUTS_DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            content.append(section_header)
            content.append("")
            # Append body skipping top title if needed
            for line in lines:
                if not line.startswith("# "):
                    content.append(line.rstrip())
            content.append("")
            content.append("---")
            content.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content))
    print(f"Master MD successfully generated: {out_path}")


def build_excel_matrix(out_path):
    df_raw = pd.read_excel(os.path.join(OUTPUTS_DIR, "data_cleaned.xlsx"))
    
    writer = pd.ExcelWriter(out_path, engine='openpyxl')

    # Sheet 1: Hypotheses Matrix
    df_hyp = pd.DataFrame([
        {"Hypothesis": "H1: Post-Test Anxiety Reduction", "Model": "One-Way ANCOVA", "F_Stat": 208.52, "df": "1, 57", "p_val": "< .001", "Partial_Eta2": 0.785, "Verdict": "SUPPORTED"},
        {"Hypothesis": "H2: 2-Month Maintenance", "Model": "One-Way ANCOVA", "F_Stat": 131.87, "df": "1, 57", "p_val": "< .001", "Partial_Eta2": 0.698, "Verdict": "SUPPORTED"},
        {"Hypothesis": "H3: Time x Group Interaction", "Model": "2x3 Mixed RM-ANOVA", "F_Stat": 76.01, "df": "1.50, 87.23", "p_val": "< .001", "Partial_Eta2": 0.571, "Verdict": "SUPPORTED"}
    ])
    df_hyp.to_excel(writer, sheet_name='01_Hypotheses_Matrix', index=False)

    # Sheet 2: Demographics
    df_demo = pd.DataFrame([
        {"Variable": "Gender: Male", "Group_1_ACT": 16, "Group_2_Control": 14, "Total": 30, "Equivalence_Test": "Chi2 = 0.067, p = 0.796"},
        {"Variable": "Gender: Female", "Group_1_ACT": 14, "Group_2_Control": 16, "Total": 30, "Equivalence_Test": "Chi2 = 0.067, p = 0.796"},
        {"Variable": "Age (Mean ± SD)", "Group_1_ACT": "38.27 ± 8.51", "Group_2_Control": "32.93 ± 9.82", "Total": "35.60 ± 9.50", "Equivalence_Test": "t(58) = 2.248, p = 0.028"},
        {"Variable": "Education: Bachelor", "Group_1_ACT": 11, "Group_2_Control": 15, "Total": 26, "Equivalence_Test": "Chi2 = 1.726, p = 0.422"},
        {"Variable": "Education: Master", "Group_1_ACT": 15, "Group_2_Control": 10, "Total": 25, "Equivalence_Test": "Chi2 = 1.726, p = 0.422"},
        {"Variable": "Education: PhD", "Group_1_ACT": 4, "Group_2_Control": 5, "Total": 9, "Equivalence_Test": "Chi2 = 1.726, p = 0.422"}
    ])
    df_demo.to_excel(writer, sheet_name='02_Demographics', index=False)

    # Sheet 3: Descriptives
    df_desc = pd.DataFrame([
        {"Variable": "Anxiety Pre-Test", "Exp_Mean": 3.426, "Exp_SD": 0.563, "Ctl_Mean": 3.466, "Ctl_SD": 0.518, "Total_Mean": 3.446, "Total_SD": 0.537},
        {"Variable": "Anxiety Post-Test", "Exp_Mean": 2.301, "Exp_SD": 0.397, "Ctl_Mean": 3.534, "Ctl_SD": 0.554, "Total_Mean": 2.918, "Total_SD": 0.784},
        {"Variable": "Anxiety Follow-Up", "Exp_Mean": 2.351, "Exp_SD": 0.411, "Ctl_Mean": 3.444, "Ctl_SD": 0.529, "Total_Mean": 2.897, "Total_SD": 0.724},
        {"Variable": "Inflexibility Pre-Test", "Exp_Mean": 3.686, "Exp_SD": 0.600, "Ctl_Mean": 3.498, "Ctl_SD": 0.612, "Total_Mean": 3.592, "Total_SD": 0.608},
        {"Variable": "Inflexibility Post-Test", "Exp_Mean": 2.236, "Exp_SD": 0.393, "Ctl_Mean": 3.498, "Ctl_SD": 0.642, "Total_Mean": 2.867, "Total_SD": 0.826},
        {"Variable": "Inflexibility Follow-Up", "Exp_Mean": 2.256, "Exp_SD": 0.371, "Ctl_Mean": 3.505, "Ctl_SD": 0.622, "Total_Mean": 2.881, "Total_SD": 0.809}
    ])
    df_desc.to_excel(writer, sheet_name='03_Descriptives', index=False)

    # Sheet 4: Assumptions
    df_assump = pd.DataFrame([
        {"Assumption": "Normality (Shapiro-Wilk)", "Tested_On": "All 6 design cells", "Statistic_Range": "W = [0.949, 0.983]", "p_val_Range": "p = [0.155, 0.897]", "Verdict": "NORMAL"},
        {"Assumption": "Homogeneity of Variance (Levene)", "Tested_On": "Post-Test Anxiety", "Statistic_Range": "F(1, 58) = 3.387", "p_val_Range": "p = 0.071", "Verdict": "HOMOGENEOUS"},
        {"Assumption": "Homogeneity of Variance (Levene)", "Tested_On": "Follow-Up Anxiety", "Statistic_Range": "F(1, 58) = 2.846", "p_val_Range": "p = 0.097", "Verdict": "HOMOGENEOUS"},
        {"Assumption": "Box's M (Covariance Equality)", "Tested_On": "Multivariate RM-ANOVA", "Statistic_Range": "M = 11.445, F = 1.801", "p_val_Range": "p = 0.095", "Verdict": "EQUAL COVARIANCE"},
        {"Assumption": "Mauchly's Sphericity", "Tested_On": "Time Repeated Factor", "Statistic_Range": "W = 0.670, Chi2 = 23.239", "p_val_Range": "p < 0.001", "Verdict": "VIOLATED (GG epsilon = 0.752)"}
    ])
    df_assump.to_excel(writer, sheet_name='04_Assumptions', index=False)

    # Sheet 5: ANCOVA
    df_ancova = pd.DataFrame([
        {"Occasion": "Post-Test", "Source": "Covariate (Pre-Test)", "SS": 4.770, "df": 1, "MS": 4.770, "F": 44.117, "p": "< .001", "Partial_Eta2": 0.436},
        {"Occasion": "Post-Test", "Source": "Group (ACT Intervention)", "SS": 22.545, "df": 1, "MS": 22.545, "F": 208.521, "p": "< .001", "Partial_Eta2": 0.785},
        {"Occasion": "Post-Test", "Source": "Error", "SS": 6.163, "df": 57, "MS": 0.108, "F": "-", "p": "-", "Partial_Eta2": "-"},
        {"Occasion": "Follow-Up", "Source": "Covariate (Pre-Test)", "SS": 3.863, "df": 1, "MS": 3.863, "F": 29.329, "p": "< .001", "Partial_Eta2": 0.340},
        {"Occasion": "Follow-Up", "Source": "Group (ACT Intervention)", "SS": 17.367, "df": 1, "MS": 17.367, "F": 131.870, "p": "< .001", "Partial_Eta2": 0.698},
        {"Occasion": "Follow-Up", "Source": "Error", "SS": 7.507, "df": 57, "MS": 0.132, "F": "-", "p": "-", "Partial_Eta2": "-"}
    ])
    df_ancova.to_excel(writer, sheet_name='05_ANCOVA_Tables', index=False)

    # Sheet 6: Repeated Measures
    df_rm = pd.DataFrame([
        {"Effect": "Time (Within)", "SS": 11.942, "df_original": 2, "df_GG": 1.504, "MS": 7.940, "F": 72.010, "p": "< .001", "Partial_Eta2": 0.554},
        {"Effect": "Time x Group (Interaction)", "SS": 12.781, "df_original": 2, "df_GG": 1.504, "MS": 8.498, "F": 77.071, "p": "< .001", "Partial_Eta2": 0.571},
        {"Effect": "Group (Between)", "SS": 33.538, "df_original": 1, "df_GG": 1.000, "MS": 33.538, "F": 81.715, "p": "< .001", "Partial_Eta2": 0.585},
        {"Effect": "Error(Time)", "SS": 9.618, "df_original": 116, "df_GG": 87.232, "MS": 0.110, "F": "-", "p": "-", "Partial_Eta2": "-"}
    ])
    df_rm.to_excel(writer, sheet_name='06_Repeated_Measures', index=False)

    writer.close()
    print(f"Master Excel Matrix successfully generated: {out_path}")


def build_publication_plots(out_path):
    df = pd.read_excel(os.path.join(OUTPUTS_DIR, "data_cleaned.xlsx"))

    # Occasions
    occasions = ["Pre-Test", "Post-Test", "2-Month Follow-Up"]
    
    # Anxiety Means & SE
    exp_anx = [df[df['group']==1]['anxiety_pre'].mean(), df[df['group']==1]['anxiety_post'].mean(), df[df['group']==1]['anxiety_followup'].mean()]
    exp_anx_se = [df[df['group']==1]['anxiety_pre'].sem(), df[df['group']==1]['anxiety_post'].sem(), df[df['group']==1]['anxiety_followup'].sem()]
    
    ctl_anx = [df[df['group']==2]['anxiety_pre'].mean(), df[df['group']==2]['anxiety_post'].mean(), df[df['group']==2]['anxiety_followup'].mean()]
    ctl_anx_se = [df[df['group']==2]['anxiety_pre'].sem(), df[df['group']==2]['anxiety_post'].sem(), df[df['group']==2]['anxiety_followup'].sem()]

    # Inflexibility Means & SE
    exp_inf = [df[df['group']==1]['inflex_pre'].mean(), df[df['group']==1]['inflex_post'].mean(), df[df['group']==1]['inflex_followup'].mean()]
    exp_inf_se = [df[df['group']==1]['inflex_pre'].sem(), df[df['group']==1]['inflex_post'].sem(), df[df['group']==1]['inflex_followup'].sem()]
    
    ctl_inf = [df[df['group']==2]['inflex_pre'].mean(), df[df['group']==2]['inflex_post'].mean(), df[df['group']==2]['inflex_followup'].mean()]
    ctl_inf_se = [df[df['group']==2]['inflex_pre'].sem(), df[df['group']==2]['inflex_post'].sem(), df[df['group']==2]['inflex_followup'].sem()]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)

    # Panel 1: Anxiety Trajectory
    ax1.errorbar(occasions, exp_anx, yerr=exp_anx_se, fmt='-o', color='#1f77b4', linewidth=2.5, markersize=8, capsize=5, label='ACT Intervention (n=30)')
    ax1.errorbar(occasions, ctl_anx, yerr=ctl_anx_se, fmt='--s', color='#d62728', linewidth=2.5, markersize=8, capsize=5, label='Waitlist Control (n=30)')
    ax1.set_title('A: Anxiety Trajectory Across Occasions\n(BAI Composite Score)', fontsize=12, fontweight='bold', pad=12)
    ax1.set_ylabel('Mean Anxiety Score (1 to 5)', fontsize=11)
    ax1.set_ylim(1.8, 4.2)
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='upper right', frameon=True, shadow=True)

    # Annotate significant drop in Experimental
    ax1.annotate('Significant Drop\np < 0.001, d = 2.31', xy=(1, 2.301), xytext=(0.8, 2.7),
                 arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.2), fontsize=9, fontweight='bold')
    ax1.annotate('Maintained Effect\np = 1.000 (No Rebound)', xy=(2, 2.351), xytext=(1.5, 1.95),
                 arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.2), fontsize=9, fontweight='bold')

    # Panel 2: Inflexibility Trajectory
    ax2.errorbar(occasions, exp_inf, yerr=exp_inf_se, fmt='-o', color='#2ca02c', linewidth=2.5, markersize=8, capsize=5, label='ACT Intervention (n=30)')
    ax2.errorbar(occasions, ctl_inf, yerr=ctl_inf_se, fmt='--s', color='#ff7f0e', linewidth=2.5, markersize=8, capsize=5, label='Waitlist Control (n=30)')
    ax2.set_title('B: Psychological Inflexibility Trajectory\n(AAQ-II Composite Score)', fontsize=12, fontweight='bold', pad=12)
    ax2.set_ylabel('Mean Inflexibility Score (1 to 5)', fontsize=11)
    ax2.set_ylim(1.8, 4.2)
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='upper right', frameon=True, shadow=True)

    # Annotate significant drop in Inflexibility
    ax2.annotate('Cognitive Defusion\np < 0.001', xy=(1, 2.236), xytext=(0.8, 2.65),
                 arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.2), fontsize=9, fontweight='bold')

    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Publication Plot successfully generated: {out_path}")


def main():
    os.makedirs(PACKAGE_DIR, exist_ok=True)
    
    docx_path = os.path.join(PACKAGE_DIR, "Experimental_Study_Report.docx")
    md_path = os.path.join(PACKAGE_DIR, "Experimental_Study_Report.md")
    xlsx_path = os.path.join(PACKAGE_DIR, "experimental_analysis_matrix.xlsx")
    png_path = os.path.join(PACKAGE_DIR, "experimental_trajectory_plots.png")

    print("Compiling Master Consolidated Deliverable Package...")
    build_master_docx(docx_path)
    build_master_md(md_path)
    build_excel_matrix(xlsx_path)
    build_publication_plots(png_path)
    print("Master Deliverable Package compilation complete.")


if __name__ == '__main__':
    main()
