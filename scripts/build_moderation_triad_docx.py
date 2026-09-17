#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_moderation_triad_docx.py — Compiles OpenXML Word deliverables for Moderation (Model 1)
and Conditional Process Analysis (Model 7).
Supports:
  1. 'macro' -> Stage 4.5: Macro Moderation Model (Hierarchical Regression Step 1 vs Step 2 & Delta R2)
  2. 'interaction' -> Stage 4.6.1: Hypothesis 1 Testing (Interaction Effect X * W)
  3. 'slopes' -> Stage 4.6.2: Simple Slopes & Johnson-Neyman Significance Regions
  4. 'modmed' -> Stage 4.7.1: First-Stage Moderated Mediation & Index of Moderated Mediation (Model 7)
Enforces APA 7th Edition 3-line borders, B Nazanin/B Titr/Times New Roman,
<w:bidiVisual/>, and decoupled LTR numbers.
"""

import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

from docx import Document
from docx.shared import Pt
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
            r.font.name = "Times New Roman" if any(char.isdigit() or char in ["-", ">", "<", "p", "r", "R", "F", "*", "/", "t", "β", "B", "%", "CI"] for char in val) else "B Nazanin"
            r.font.size = Pt(10)

    return tbl


def build_macro_moderation_docx(out_path):
    doc = Document()
    add_heading(doc, "تحلیل تعدیل‌گری سلسله‌مراتبی مدل ۱ هیز: نقش سرمایه روان‌شناختی در رابطه مطالبات شغلی و فرسودگی هیجانی", level=1)

    add_heading(doc, "۱. بیان الگوی تعدیل‌گری و روش‌شناسی تحلیل سلسله‌مراتبی", level=2)
    add_p(doc, "به منظور بررسی فرضیه تعدیل‌گری سرمایه روان‌شناختی (متغیر تعدیل‌کننده) بر شدت رابطه میان مطالبات شغلی (متغیر پیش‌بین) و فرسودگی هیجانی (متغیر ملاک)، از رگرسیون خطی سلسله‌مراتبی دو مرحله‌ای مطابق با الگوی شماره ۱ پردازش هیز (۲۰۱۸) استفاده شد. جهت جلوگیری از هم‌خطی چندگانه تصنعی، متغیرهای پیش‌بین و تعدیل‌کننده پیش از محاسبه حاصل‌ضرب تعاملی، میانگین‌مرکز (Mean-Centered) شدند.")

    add_heading(doc, "۲. خلاصه مدل‌های رگرسیونی و آزمون تغییر ضریب تعیین (ΔR²)", level=2)
    add_p(doc, "در جدول ۱، شاخص‌های کلی مدل‌های رگرسیونی در گام ۱ (اثرات اصلی) و گام ۲ (ورود اثر تعاملی) به همراه آماره تغییر F گزارش شده است.")

    add_table_header(doc, "جدول ۱. خلاصه مدل‌های رگرسیونی سلسله‌مراتبی و آماره‌های تغییر مدل تعدیل‌گری (۳۲۰ = N)")
    headers1 = ["مدل / گام", "متغیرهای وارد شده", "R", "R²", "تعدیل‌شده R²", "خطای معیار", "تغییر R²", "آماره تغییر F", "درجه آزادی ۱", "درجه آزادی ۲", "سطح معناداری تغییر"]
    rows1 = [
        ["گام ۱ (اثرات اصلی)", "مطالبات شغلی، سرمایه روان‌شناختی", "۰.۵۷۷", "۰.۳۳۳", "۰.۳۲۹", "۰.۴۸۱", "۰.۳۳۳", "۷۹.۰۷", "۲", "۳۱۷", "۰.۰۰۱ > p"],
        ["گام ۲ (اثر تعاملی)", "مطالبات × سرمایه روان‌شناختی", "۰.۶۰۱", "۰.۳۶۱", "۰.۳۵۵", "۰.۴۷۲", "۰.۰۲۸", "۱۴.۰۰", "۱", "۳۱۶", "۰.۰۰۱ > p"]
    ]
    populate_apa_table(doc, headers1, rows1)
    add_table_note(doc, "یادداشت. متغیر ملاک: فرسودگی هیجانی. متغیرها پیش از ایجاد جمله تعاملی میانگین‌مرکز شده‌اند.")

    add_p(doc, "همان‌گونه که در جدول ۱ ملاحظه می‌شود، ورود مؤلفه تعاملی در گام دوم منجر به افزایش معنادار ضریب تعیین به میزان ۲.۸ درصد گردیده است (۰.۰۲۸ = ΔR²، ۱۴.۰۰ = تغییر F، ۰.۰۰۱ > p). این یافته حاکی از آن است که اثر تعاملی مطالبات شغلی و سرمایه روان‌شناختی سهم تبیینی منحصر‌به‌فرد و معناداری در پیش‌بینی فرسودگی هیجانی کارکنان دارد و اثر تعدیل‌گری مدل ۱ از لحاظ تجربی تأیید می‌گردد.")

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    doc.save(out_path)
    print(f"Saved Macro Moderation DOCX artifact: {out_path}")


def build_interaction_docx(out_path):
    doc = Document()
    add_heading(doc, "آزمون فرضیه ۱: اثر تعدیل‌کننده سرمایه روان‌شناختی در رابطه میان مطالبات شغلی و فرسودگی هیجانی", level=1)

    add_heading(doc, "۱. بیان فرضیه و ضرایب رگرسیونی مدل تعاملی", level=2)
    add_p(doc, "فرضیه ۱ تصریح می‌دارد که «سرمایه روان‌شناختی رابطه مستقیم میان مطالبات شغلی و فرسودگی هیجانی کارکنان را تعدیل می‌کند؛ به‌گونه‌ای که در سطوح بالاتر سرمایه روان‌شناختی، شدت تأثیر مطالبات شغلی بر فرسودگی کاهش می‌یابد». جدول ۱ ضرایب رگرسیونی گام دوم را نشان می‌دهد.")

    add_table_header(doc, "جدول ۱. ضرایب رگرسیونی مدل تعاملی پیش‌بینی فرسودگی هیجانی (۳۲۰ = N)")
    headers = ["متغیر پیش‌بین", "B", "SE", "β", "t", "سطح معناداری (p)", "کران پایین ۹۵٪ CI", "کران بالا ۹۵٪ CI"]
    rows = [
        ["عرض از مبدأ (ثابت)", "۲.۹۱۰", "۰.۰۲۶", "-", "۱۱۰.۲۹", "۰.۰۰۱ > p", "۲.۸۵۸", "۲.۹۶۲"],
        ["مطالبات شغلی (مرکز‌شده)", "۰.۳۵۷", "۰.۰۴۰", "۰.۴۰۲", "۸.۹۳", "۰.۰۰۱ > p", "۰.۲۷۸", "۰.۴۳۵"],
        ["سرمایه روان‌شناختی (مرکز‌شده)", "-۰.۳۷۳", "۰.۰۳۹", "-۰.۴۳۲", "-۹.۵۸", "۰.۰۰۱ > p", "-۰.۴۵۰", "-۰.۲۹۷"],
        ["اثر تعاملی (مطالبات × سرمایه)", "-۰.۲۲۲", "۰.۰۵۹", "-۰.۱۶۹", "-۳.۷۴", "۰.۰۰۱ > p", "-۰.۳۳۹", "-۰.۱۰۵"]
    ]
    populate_apa_table(doc, headers, rows)
    add_table_note(doc, "یادداشت. متغیر ملاک: فرسودگی هیجانی. ضریب منفی تعامل حاکی از نقش تعدیل‌کننده ضربه‌گیر (Buffering Effect) است.")

    add_p(doc, "یافته‌های جدول ۱ نشان می‌دهد ضریب رگرسیونی اثر تعاملی میان مطالبات شغلی و سرمایه روان‌شناختی منفی و از لحاظ آماری در سطح خطای یک‌هزارم کاملاً معنادار است (۰.۲۲۲- = B، ۰.۱۶۹- = β، ۳.۷۴- = t، ۰.۰۰۱ > p، فاصله اطمینان ۹۵ درصد [۰.۱۰۵- ، ۰.۳۳۹-]). با توجه به منفی بودن جهت ضریب تعاملی، سرمایه روان‌شناختی به عنوان یک منبع محافظتی و ضربه‌گیر عمل نموده و آسیب‌زایی مطالبات شغلی را به شکل معناداری مهار می‌سازد؛ بنابراین فرضیه ۱ با اطمینان ۹۹ درصد تأیید تجربی گردید.")

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    doc.save(out_path)
    print(f"Saved Interaction DOCX artifact: {out_path}")


def build_slopes_docx(out_path):
    doc = Document()
    add_heading(doc, "تحلیل شیب‌های ساده و منطقه معناداری جانسون-نیمن", level=1)

    add_heading(doc, "۱. آزمون شیب‌های ساده در سطوح مختلف تعدیل‌کننده (-1 SD, Mean, +1 SD)", level=2)
    add_p(doc, "جهت کالبدشکافی ماهیت اثر تعاملی، شیب‌های ساده خط اثر مطالبات شغلی بر فرسودگی هیجانی در سه سطح استاندارد سرمایه روان‌شناختی مشتمل بر سطح پایین (یک انحراف معیار پایین‌تر از میانگین)، سطح متوسط (میانگین) و سطح بالا (یک انحراف معیار بالاتر از میانگین) به روش ایکن و وست (۱۹۹۱) محاسبه و با خطای معیار تحلیلی ماتریس کوواریانس آزمون شد.")

    add_table_header(doc, "جدول ۱. تحلیل شیب‌های ساده اثر مطالبات شغلی بر فرسودگی هیجانی در سطوح مختلف سرمایه روان‌شناختی (۳۲۰ = N)")
    headers = ["سطح سرمایه روان‌شناختی", "مقدار خام تعدیل‌کننده (W)", "مقدار مرکز‌شده (Wc)", "شیب ساده (B)", "خطای معیار (SE)", "آماره t", "سطح معناداری (p)", "کران پایین ۹۵٪ CI", "کران بالا ۹۵٪ CI", "نتیجه آزمون"]
    rows = [
        ["سطح پایین (SD ۱-)", "۲.۷۱۶", "-۰.۶۷۹", "۰.۵۰۸", "۰.۰۵۸", "۸.۷۶", "۰.۰۰۱ > p", "۰.۳۹۴", "۰.۶۲۲", "تأیید معناداری (اثر قوی)"],
        ["سطح متوسط (میانگین)", "۳.۳۹۶", "۰.۰۰۰", "۰.۳۵۷", "۰.۰۴۰", "۸.۹۳", "۰.۰۰۱ > p", "۰.۲۷۸", "۰.۴۳۵", "تأیید معناداری (اثر متوسط)"],
        ["سطح بالا (SD ۱+)", "۴.۰۷۵", "۰.۶۷۹", "۰.۲۰۶", "۰.۰۵۶", "۳.۷۱", "۰.۰۰۱ > p", "۰.۰۹۷", "۰.۳۱۵", "تأیید معناداری (اثر تعدیل‌شده)"]
    ]
    populate_apa_table(doc, headers, rows)
    add_table_note(doc, "یادداشت. خطای معیار شیب‌های ساده با فرمول تحلیلی ماتریس کوواریانس ضرایب محاسبه شد.")

    add_heading(doc, "۲. دامنه معناداری بر اساس تکنیک جانسون-نیمن (Johnson-Neyman Technique)", level=2)
    add_p(doc, "علاوه بر سطوح قراردادی انحراف معیار، از تکنیک جانسون-نیمن جهت شناسایی مرز دقیق تغییر معناداری رابطه استفاده شد. یافته‌ها نشان داد که نقطه مرزی تغییر معناداری در نمره خام ۴.۳۸۵ سرمایه روان‌شناختی واقع است. برای نمرات کمتر از ۴.۳۸۵، اثر افزایشی مطالبات شغلی بر فرسودگی هیجانی کاملاً معنادار است، اما در نمرات بالاتر از ۴.۳۸۵، سرمایه روان‌شناختی اثر زیان‌بار مطالبات شغلی را به طور کامل خنثی ساخته و رابطه را غیرمعنادار می‌سازد.")

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    doc.save(out_path)
    print(f"Saved Simple Slopes DOCX artifact: {out_path}")


def build_modmed_docx(out_path):
    doc = Document()
    add_heading(doc, "تحلیل فرآیند مشروط مدل ۷ هیز: الگوی میانجی‌گری تعدیل‌شده مرحله اول", level=1)

    add_heading(doc, "۱. بیان الگوی میانجی‌گری تعدیل‌شده مرحله اول (Model 7)", level=2)
    add_p(doc, "در این تحلیل، سازوکار فرآیند مشروط (Conditional Process Analysis) ارزیابی شد که در آن سرمایه روان‌شناختی به عنوان تعدیل‌کننده مرحله اول (مسیر مطالبات شغلی به فرسودگی هیجانی) و فرسودگی هیجانی به عنوان متغیر میانجی پیش‌بینی تمایل به ترک خدمت عمل می‌کنند. این آزمون با روش بازنمونه‌گیری بوت‌استراپ با ۵۰۰۰ مرتبه نمونه‌گیری مجدد و فاصله اطمینان ۹۵ درصد انجام گرفت.")

    add_table_header(doc, "جدول ۱. اثرات غیرمستقیم مشروط و شاخص میانجی‌گری تعدیل‌شده (۵۰۰۰ نوبت بوت‌استراپ، ۳۲۰ = N)")
    headers = ["سطح تعدیل‌کننده (سرمایه روان‌شناختی)", "مقدار خام تعدیل‌کننده", "اثر غیرمستقیم مشروط (B)", "خطای معیار بوت‌استراپ", "کران پایین ۹۵٪ CI", "کران بالا ۹۵٪ CI", "نتیجه آزمون تجربی"]
    rows = [
        ["سطح پایین (SD ۱-)", "۲.۷۱۶", "۰.۱۶۵", "۰.۰۲۷", "۰.۱۱۷", "۰.۲۲۲", "معنادار (تأیید میانجی‌گری)"],
        ["سطح متوسط (میانگین)", "۳.۳۹۶", "۰.۱۱۶", "۰.۰۲۰", "۰.۰۸۰", "۰.۱۵۸", "معنادار (تأیید میانجی‌گری)"],
        ["سطح بالا (SD ۱+)", "۴.۰۷۵", "۰.۰۶۷", "۰.۰۲۰", "۰.۰۳۰", "۰.۱۱۱", "معنادار (تأیید میانجی‌گری)"],
        ["شاخص میانجی‌گری تعدیل‌شده (Index)", "-", "-۰.۰۷۲", "۰.۰۲۰", "-۰.۱۱۶", "-۰.۰۳۸", "معنادار (تأیید فرآیند مشروط)"]
    ]
    populate_apa_table(doc, headers, rows)
    add_table_note(doc, "یادداشت. فواصل اطمینان بر مبنای ۵۰۰۰ مرتبه بازنمونه‌گیری بوت‌استراپ محاسبه شد. عدم شمول صفر در فاصله اطمینان شاخص میانجی‌گری تعدیل‌شده حاکی از مشروط بودن معنادار اثر غیرمستقیم است.")

    add_p(doc, "نتایج جدول ۱ مؤید آن است که شاخص میانجی‌گری تعدیل‌شده برابر با ۰.۰۷۲- = Index با خطای معیار ۰.۰۲۰ است و فاصله اطمینان ۹۵ درصد بوت‌استراپ [۰.۰۳۸- ، ۰.۱۱۶-] عدد صفر را در بر نمی‌گیرد. این یافته دلالت بر آن دارد که اثر غیرمستقیم مطالبات شغلی بر تمایل به ترک خدمت از طریق فرسودگی هیجانی، به شکل معناداری تابع میزان سرمایه روان‌شناختی است؛ به طوری که در افراد دارای سرمایه روان‌شناختی بالا، انتقال آسیب‌زای مطالبات به تمایل به ترک خدمت بیش از ۵۰ درصد تضعیف می‌گردد.")

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    doc.save(out_path)
    print(f"Saved Moderated Mediation DOCX artifact: {out_path}")

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    doc.save(out_path)
    print(f"Saved Moderated Mediation DOCX artifact: {out_path}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "macro"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "output.docx"
    if mode == "macro":
        build_macro_moderation_docx(out_path)
    elif mode == "interaction":
        build_interaction_docx(out_path)
    elif mode == "slopes":
        build_slopes_docx(out_path)
    elif mode == "modmed":
        build_modmed_docx(out_path)
    else:
        print(f"Unknown mode: {mode}")
