#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_hypothesis_1_triad_docx.py — Compiles OpenXML Word deliverable for Hypothesis 1.
Strictly enforces the 3-Table Standard for Relationship / Regression Hypotheses:
  - Table 1: Bivariate Correlation Matrix & Descriptives
  - Table 2: Combined Model Summary & ANOVA Table
  - Table 3: Regression Coefficients & Collinearity Diagnostics (Tolerance, VIF)
"""
import os
import sys

# Virtualenv auto-discovery shim
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


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
    size = 14 if level == 1 else 13
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
            r = p.add_run(val)
            r.font.name = "Times New Roman" if any(char.isdigit() or char in ["-", ">", "<", "p", "r", "R", "F", "*"] for char in val) else "B Nazanin"
            r.font.size = Pt(10)

    return tbl


def build_docx(out_path):
    doc = Document()

    add_heading(doc, "آزمون فرضیه اول: پیش‌بینی فرسودگی شغلی بر اساس استرس شغلی و انعطاف‌پذیری روان‌شناختی", level=1)

    add_heading(doc, "۱. بیان فرضیه و صورت‌بندی مدل پژوهش", level=2)
    add_p(doc, "فرضیه اول پژوهش بیان می‌دارد که «استرس شغلی و انعطاف‌پذیری روان‌شناختی به طور همزمان فرسودگی شغلی کارکنان را پیش‌بینی می‌کنند». به منظور آزمون این فرضیه و تعیین سهم واریانس تبیین‌شده متغیر ملاک توسط متغیرهای پیش‌بین، از الگوی رگرسیون خطی چندگانه به شیوه همزمان (Enter) استفاده شد. پیش از انجام تحلیل، رعایت کامل استاندارد سه‌جدولی آزمون فرضیات رابطه‌ای در دستور کار قرار گرفت.")

    add_heading(doc, "۲. تحلیل همبستگی‌های دو متغیره و مشخصه‌های توصیفی", level=2)
    add_p(doc, "نخستین گام در تحلیل رگرسیون، بررسی همبستگی‌های مرتبه صفر پیرسون میان متغیرهای پیش‌بین و متغیر ملاک به منظور ارزیابی روابط خطی اولیه و وارسی هم‌خطی شدید است. در جدول ۱، مقادیر میانگین، انحراف استاندارد و ماتریس همبستگی پیرسون بین متغیرهای پژوهش گزارش شده است.")

    # --- TABLE 1: BIVARIATE CORRELATION MATRIX ---
    add_table_header(doc, "جدول ۱. ماتریس همبستگی پیرسون و شاخص‌های توصیفی متغیرهای پژوهش (۱۰۰ = N)")
    headers1 = ["متغیرها", "میانگین", "انحراف استاندارد", "۱", "۲", "۳"]
    rows1 = [
        ["۱. فرسودگی شغلی", "۳.۱۷", "۰.۶۷", "۱", "—", "—"],
        ["۲. استرس شغلی", "۳.۳۶", "۰.۶۷", "۰.۵۵***", "۱", "—"],
        ["۳. انعطاف‌پذیری روان‌شناختی", "۳.۳۶", "۰.۶۳", "۰.۴۶-***", "۰.۲۷-**", "۱"]
    ]
    populate_apa_table(doc, headers1, rows1)
    add_table_note(doc, "یادداشت. ۰.۰۱ > **p، ۰.۰۰۱ > ***p.")

    add_p(doc, "همان‌گونه که در جدول ۱ مشاهده می‌شود، استرس شغلی با فرسودگی شغلی دارای همبستگی مثبت و معنادار (۰.۰۰۱ > p ،۰.۵۵ = r) است. در مقابل، انعطاف‌پذیری روان‌شناختی با فرسودگی شغلی رابطه منفی و معناداری نشان می‌دهد (۰.۰۰۱ > p ،۰.۴۶- = r). همچنین همبستگی میان دو متغیر پیش‌بین برابر با ۰.۲۷- محاسبه شد که نشان‌دهنده استقلال مفهومی سازه‌ها و عدم هم‌پوشانی هم‌خطی چندگانه بحرانی میان آن‌هاست.")

    add_heading(doc, "۳. خلاصه مدل رگرسیون و تحلیل واریانس (ANOVA)", level=2)
    add_p(doc, "به منظور بررسی معناداری کلی مدل رگرسیون و تعیین نسبت واریانس تبیین‌شده فرسودگی شغلی توسط دو متغیر پیش‌بین، آزمون تحلیل واریانس رگرسیون محاسبه شد. جدول ۲ خلاصه مدل رگرسیون و نتایج تحلیل واریانس را نشان می‌دهد.")

    # --- TABLE 2: COMBINED ANOVA & MODEL SUMMARY ---
    add_table_header(doc, "جدول ۲. خلاصه مدل رگرسیون چندگانه و تحلیل واریانس (ANOVA) پیش‌بینی فرسودگی شغلی (۱۰۰ = N)")
    headers2 = ["منبع تغییرات", "مجموع مجذورات (SS)", "درجه آزادی (df)", "میانگین مجذورات (MS)", "F", "سطح معناداری (p)", "R", "R²", "R² تعدیل‌شده", "خطای معیار", "دوربین-واتسون"]
    rows2 = [
        ["رگرسیون", "۱۸.۷۰۸", "۲", "۹.۳۵۴", "34.389", "۰.۰۰۱ > p", "۰.۶۴۴", "0.415", "۰.۴۰۳", "۰.۵۲۲", "۲.۱۱۵"],
        ["باقی‌مانده", "۲۶.۳۸۵", "۹۷", "۰.۲۷۲", "—", "—", "—", "—", "—", "—", "—"],
        ["کل", "۴۵.۰۹۲", "۹۹", "—", "—", "—", "—", "—", "—", "—", "—"]
    ]
    populate_apa_table(doc, headers2, rows2)
    add_table_note(doc, "یادداشت. متغیر ملاک: فرسودگی شغلی. متغیرهای پیش‌بین: استرس شغلی، انعطاف‌پذیری روان‌شناختی.")

    add_p(doc, "یافته‌های مندرج در جدول ۲ نشان می‌دهد که مدل رگرسیونی کلی با اطمینان ۹۹ درصد از لحاظ آماری معنادار است (34.389 = (۹۷ ،۲)F، ۰.۰۰۱ > p). ضریب همبستگی چندگانه برابر با ۰.۶۴۴ و ضریب تعیین برابر با 0.415 به دست آمد؛ بدین معنا که ۴۱.۵ درصد از کل واریانس و تغییرات فرسودگی شغلی کارکنان توسط مجموعه متغیرهای استرس شغلی و انعطاف‌پذیری روان‌شناختی تبیین می‌گردد. مقدار آماره دوربین-واتسون (۲.۱۱۵) در دامنه مطلوب بین ۱.۵ تا ۲.۵ قرار دارد که حاکی از استقلال خطاهای برآورد و فقدان خودهمبستگی باقیمانده‌ها است.")

    add_heading(doc, "۴. ضرایب رگرسیون و شاخص‌های هم‌خطی", level=2)
    add_p(doc, "به منظور ارزیابی سهم اختصاصی هر یک از متغیرهای پیش‌بین در پیش‌بینی فرسودگی شغلی، ضرایب غیراستاندارد (B)، خطای معیار (SE)، ضرایب استاندارد (β)، مقدار آماره t، فاصله اطمینان ۹۵ درصد و شاخص‌های هم‌خطی (Tolerance و VIF) در جدول ۳ گزارش شده است.")

    # --- TABLE 3: REGRESSION COEFFICIENTS & COLLINEARITY ---
    add_table_header(doc, "جدول ۳. ضرایب رگرسیون چندگانه و شاخص‌های هم‌خطی متغیرهای پیش‌بین فرسودگی شغلی (۱۰۰ = N)")
    headers3 = ["متغیرهای مدل", "B", "SE", "β", "t", "سطح معناداری (p)", "فاصله اطمینان ۹۵٪", "تولرانس", "VIF"]
    rows3 = [
        ["مقدار ثابت", "۲.۸۲۴", "۰.۴۴۹", "—", "۶.۲۸۹", "۰.۰۰۱ > p", "[۱.۹۳۳ ، ۳.۷۱۵]", "—", "—"],
        ["استرس شغلی", "۰.۴۶۶", "۰.۰۸۱", "۰.۴۶۴", "۵.۷۵۶", "۰.۰۰۱ > p", "[۰.۳۰۵ ، ۰.۶۲۷]", "۰.۹۲۹", "۱.۰۷۶"],
        ["انعطاف‌پذیری روان‌شناختی", "۰.۳۶۲-", "۰.۰۸۶", "۰.۳۴۰-", "۴.۲۲۴-", "۰.۰۰۱ > p", "[۰.۵۳۲- ، ۰.۱۹۲-]", "۰.۹۲۹", "۱.۰۷۶"]
    ]
    populate_apa_table(doc, headers3, rows3)
    add_table_note(doc, "یادداشت. متغیر ملاک: فرسودگی شغلی.")

    add_p(doc, "نتایج جدول ۳ نشان می‌دهد که استرس شغلی با ضریب استاندارد ۰.۴۶۴ و آماره ۵.۷۵۶ = t در سطح ۰.۰۰۱ > p به صورت مثبت و معنادار فرسودگی شغلی را پیش‌بینی می‌کند. همچنین انعطاف‌پذیری روان‌شناختی با ضریب استاندارد ۰.۳۴۰- و آماره ۴.۲۲۴- = t در سطح ۰.۰۰۱ > p به صورت منفی و معنادار قادر به پیش‌بینی فرسودگی شغلی است. شاخص‌های تولرانس (۰.۹۲۹) و VIF (۱.۰۷۶) برای هر دو متغیر در وضعیت کاملاً بهنجار قرار داشته و عدم وجود هم‌خطی چندگانه را تصدیق می‌نمایند.")

    add_heading(doc, "۵. نتیجه‌گیری آماری فرضیه", level=2)
    add_p(doc, "با توجه به معناداری کلی مدل رگرسیون در جدول تحلیل واریانس و معناداری انفرادی ضرایب رگرسیون استاندارد در جهت مورد انتظار، فرضیه اول پژوهش مبنی بر پیش‌بینی معنادار فرسودگی شغلی توسط استرس شغلی و انعطاف‌پذیری روان‌شناختی با اطمینان ۹۹ درصد تأیید می‌گردد.")

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    doc.save(out_path)
    print(f"Saved 3-Table Standard DOCX artifact: {out_path}")


if __name__ == "__main__":
    out_docx = sys.argv[1] if len(sys.argv) > 1 else "06_hypothesis_1_regression.docx"
    build_docx(out_docx)
