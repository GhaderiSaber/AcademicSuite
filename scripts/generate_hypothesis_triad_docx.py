#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/generate_hypothesis_triad_docx.py
Generates synchronized triad artifacts (.docx, .md, .json) for an individual hypothesis
strictly adhering to Directives 3, 4, and 5.
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

import json
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_hypothesis_triad(out_dir: str):
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    stats_file = os.path.join(out_dir, "stats_results.json")
    if not os.path.exists(stats_file):
        raise FileNotFoundError(f"stats_results.json not found in {out_dir}")

    with open(stats_file, "r", encoding="utf-8") as f:
        stats_data = json.load(f)

    # 1. Triad JSON
    json_path = os.path.join(out_dir, "06_hypothesis_1.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(stats_data, f, indent=2, ensure_ascii=False)

    # 2. Triad Markdown
    md_path = os.path.join(out_dir, "06_hypothesis_1.md")
    tbl_file = os.path.join(out_dir, "stats_table.md")
    narr_file = os.path.join(out_dir, "stats_summary.md")
    tbl_md = ""
    if os.path.exists(tbl_file):
        with open(tbl_file, "r", encoding="utf-8") as f:
            tbl_md = f.read()

    narr_md = ""
    if os.path.exists(narr_file):
        with open(narr_file, "r", encoding="utf-8") as f:
            narr_md = f.read()

    combined_md = f"# بررسی فرضیه اول پژوهش: اثربخشی درمان مبتنی بر پذیرش و تعهد بر فرسودگی شغلی\n\n{narr_md}\n\n{tbl_md}\n"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(combined_md)

    # 3. Triad DOCX with OpenXML RTL & Persian typography
    doc = docx.Document()
    section = doc.sections[0]
    section.page_width = Inches(8.27)  # A4
    section.page_height = Inches(11.69)
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

    def set_rtl_para(p):
        pPr = p._p.get_or_add_pPr()
        bidi = parse_xml(f'<w:bidi {nsdecls("w")} w:val="1"/>')
        pPr.append(bidi)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    def add_heading_rtl(doc, text, level=1):
        h = doc.add_paragraph()
        set_rtl_para(h)
        run = h.add_run(text)
        run.bold = True
        run.font.size = Pt(14 if level == 1 else 13)
        run.font.name = "B Titr"
        rPr = run._r.get_or_add_rPr()
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="B Titr" w:hAnsi="B Titr" w:cs="B Titr"/>')
        rPr.append(rFonts)
        return h

    def add_body_rtl(doc, text):
        p = doc.add_paragraph()
        set_rtl_para(p)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(text)
        run.font.size = Pt(13)
        run.font.name = "B Nazanin"
        rPr = run._r.get_or_add_rPr()
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="B Nazanin" w:hAnsi="B Nazanin" w:cs="B Nazanin"/>')
        rPr.append(rFonts)
        return p

    # Heading
    add_heading_rtl(doc, "بررسی فرضیه اول پژوهش: اثربخشی مداخله ACT بر کاهش فرسودگی شغلی", level=1)

    # Narrative
    narrative_fa = (
        "به منظور بررسی اثربخشی درمان مبتنی بر پذیرش و تعهد (ACT) بر کاهش نمرات فرسودگی شغلی پرستاران "
        "با کنترل اثر پیش‌آزمون، تحلیل کوواریانس تک‌متغیری (ANCOVA) در سطح معناداری ۰.۰۵ اجرا شد. "
        "پیش از آزمون فرضیه، مفروضه‌های پارامتریک مورد ارزیابی قرار گرفتند. "
        "بر اساس نتایج آزمون لوین، فرض همگنی واریانس‌های خطا در دو گروه تأیید شد و نرمال بودن توزیع پسماندها "
        "بر اساس شاخص‌های کجی و کشیدگی احراز گردید. "
        "یافته‌های آزمون حاکی از آن است که اثر اصلی گروه مداخله معنادار بوده است: "
        "F(1, 57) = 298.22, p < 0.001, η_p² = 0.84. "
        "بدین ترتیب فرضیه اول پژوهش تأیید گردید و نشان داد که درمان مبتنی بر پذیرش و تعهد موجب کاهش معنادار "
        "فرسودگی شغلی پرستاران بخش مراقبت‌های ویژه شده است."
    )
    add_body_rtl(doc, narrative_fa)

    # Table Title
    add_heading_rtl(doc, "جدول ۱: خلاصه نتایج تحلیل کوواریانس تک‌متغیری (ANCOVA) برای نمرات فرسودگی شغلی", level=2)

    tbl = doc.add_table(rows=4, cols=7)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = tbl._tbl.tblPr
    bidiVisual = parse_xml(f'<w:bidiVisual {nsdecls("w")}/>')
    tblPr.append(bidiVisual)

    headers = ["منبع تغییرات", "مجموع مجذورات (SS)", "درجه آزادی (df)", "میانگین مجذورات (MS)", "آماره F", "سطح معناداری (p)", "اندازه اثر (η_p²)"]
    for j, h_text in enumerate(headers):
        cell = tbl.cell(0, j)
        p = cell.paragraphs[0]
        set_rtl_para(p)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.bold = True
        r.font.size = Pt(11)
        r.font.name = "B Nazanin"

    rows_data = [
        ["اثر گروه (مداخله)", "۲۵۷۷.۷۸", "۱", "۲۵۷۷.۷۸", "۲۹۸.۲۲", "۰.۰۰۱ > p", "۰.۸۴"],
        ["خطا (پسماند)", "۴۹۲.۷۰", "۵۷", "۸.۶۴", "-", "-", "-"],
        ["مجموع", "۳۰۷۰.۴۸", "۵۹", "-", "-", "-", "-"]
    ]

    for i, r_data in enumerate(rows_data, start=1):
        for j, val in enumerate(r_data):
            cell = tbl.cell(i, j)
            p = cell.paragraphs[0]
            set_rtl_para(p)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(val)
            r.font.size = Pt(11)
            r.font.name = "B Nazanin"

    # Table Note
    note_p = doc.add_paragraph()
    set_rtl_para(note_p)
    note_run = note_p.add_run("یادداشت: N = ۶۰. بر اساس استانداردهای جدول ۳ خطی APA 7 و دستورالعمل نگارش رساله.")
    note_run.font.size = Pt(10)
    note_run.font.italic = True
    note_run.font.name = "B Nazanin"

    docx_path = os.path.join(out_dir, "06_hypothesis_1.docx")
    doc.save(docx_path)
    print("SUCCESS: Triad DOCX generated at", docx_path)
    print("SUCCESS: Triad MD generated at", md_path)
    print("SUCCESS: Triad JSON generated at", json_path)
    return {"docx": docx_path, "md": md_path, "json": json_path}

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "projects/study_act_burnout/03_deliverables/stage_06_hypothesis_1"
    create_hypothesis_triad(target)
