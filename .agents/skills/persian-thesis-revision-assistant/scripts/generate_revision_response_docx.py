#!/usr/bin/env python3
"""
Supervisor Revision Response Document Generator (generate_revision_response_docx.py)
------------------------------------------------------------------------------------
Generates the official Point-by-Point Response Table (جدول پاسخ به نظرات استاد راهنما و داوران)
in Microsoft Word (.docx) format with proper Iranian academic typography (B Nazanin, B Titr)
and OpenXML RTL bi-directional support.
"""

import os
import sys
import json
import argparse
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=100, bottom=100, left=120, right=120):
    """Set inner padding for table cell in twips."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m_name}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders_and_bidi(table):
    """Apply professional grid borders and RTL layout."""
    tblPr = table._tbl.tblPr
    bidiVisual = parse_xml(f'<w:bidiVisual {nsdecls("w")}/>')
    tblPr.append(bidiVisual)
    
    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'  <w:left w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'  <w:right w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="D3D3D3"/>\n'
        f'  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="D3D3D3"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(tblBorders)

def set_cell_shading(cell, color_hex="F2F2F2"):
    """Set cell background fill color."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)

def set_paragraph_bidi(p, align=WD_ALIGN_PARAGRAPH.RIGHT):
    """Enforce Persian BiDi RTL directionality on paragraph."""
    p.alignment = align
    pPr = p._p.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    bidi.set(qn('w:val'), '1')
    pPr.append(bidi)

def add_run(p, text, font_fa='B Nazanin', font_en='Times New Roman', size=12, bold=False, italic=False):
    """Add text run with explicit Persian and Latin font bindings."""
    run = p.add_run(text)
    run.font.name = font_fa
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    
    rPr = run._r.get_or_add_rPr()
    rFonts = parse_xml(
        f'<w:rFonts {nsdecls("w")} '
        f'w:ascii="{font_en}" w:hAnsi="{font_en}" '
        f'w:cs="{font_fa}" w:eastAsia="{font_fa}"/>'
    )
    rPr.append(rFonts)
    return run

def build_response_document(data: dict, output_path: str):
    doc = docx.Document()
    
    # Page setup (A4 Landscape or Portrait - standard portrait with 2.5cm margins)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        
    # Title
    p_title = doc.add_paragraph()
    set_paragraph_bidi(p_title, WD_ALIGN_PARAGRAPH.CENTER)
    p_title.paragraph_format.space_before = Pt(16)
    p_title.paragraph_format.space_after = Pt(8)
    add_run(p_title, "گزارش اقدامات و جدول پاسخ به نظرات استاد راهنما، مشاور و داوران محترم", font_fa='B Titr', size=15, bold=True)
    
    # Thesis details
    title_thesis = data.get("thesis_title", "عنوان رساله / پایان‌نامه")
    student_name = data.get("student_name", "نام دانشجو")
    supervisor_name = data.get("supervisor_name", "استاد راهنما")
    
    p_meta = doc.add_paragraph()
    set_paragraph_bidi(p_meta, WD_ALIGN_PARAGRAPH.CENTER)
    p_meta.paragraph_format.space_after = Pt(14)
    meta_text = f"عنوان رساله: {title_thesis} | نگارش: {student_name} | استاد راهنما: {supervisor_name}"
    add_run(p_meta, meta_text, font_fa='B Nazanin', size=11, bold=True)
    
    # Intro
    p_intro = doc.add_paragraph()
    set_paragraph_bidi(p_intro, WD_ALIGN_PARAGRAPH.JUSTIFY)
    p_intro.paragraph_format.line_spacing = 1.25
    p_intro.paragraph_format.space_after = Pt(12)
    intro_text = (
        "با سلام و احترام، بدین‌وسیله مراتب سپاس و قدردانی صمیمانه خود را از دقت نظر، راهنمایی‌های ارزشمند و "
        "نکات موشکافانه اساتید گران‌قدر ابراز می‌دارم. کلیه نظرات و اصلاحات مدنظر با کمال دقت و وسواس علمی مورد "
        "بررسی قرار گرفت و تغییرات لازم در متن رساله اعمال گردید. جدول زیر شرح تفصیلی اقدامات صورت‌گرفته به تفکیک هریک از نظرات را ارائه می‌نماید."
    )
    add_run(p_intro, intro_text, size=11)
    
    # Table Setup
    items = data.get("comments", [])
    tbl = doc.add_table(rows=len(items) + 1, cols=4)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders_and_bidi(tbl)
    
    # Column widths (relative)
    # Total width ~ 6.5 inches: Col 0: 0.5 in, Col 1: 2.2 in, Col 2: 2.6 in, Col 3: 1.2 in
    col_widths = [Inches(0.6), Inches(2.2), Inches(2.5), Inches(1.2)]
    
    headers = ["ردیف", "نام استاد و نظر / تذکر ارائه شده", "اقدام انجام‌شده و پاسخ دانشجو", "محل اصلاح در متن"]
    for c_idx, h_text in enumerate(headers):
        cell = tbl.cell(0, c_idx)
        set_cell_margins(cell, top=120, bottom=120)
        set_cell_shading(cell, "EAEAEA")
        p = cell.paragraphs[0]
        set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
        add_run(p, h_text, font_fa='B Nazanin', size=11, bold=True)
        
    for r_idx, item in enumerate(items):
        row_cells = tbl.rows[r_idx + 1].cells
        
        # Row number
        set_cell_margins(row_cells[0], top=80, bottom=80)
        p0 = row_cells[0].paragraphs[0]
        set_paragraph_bidi(p0, WD_ALIGN_PARAGRAPH.CENTER)
        add_run(p0, str(r_idx + 1), size=11)
        
        # Supervisor Comment
        set_cell_margins(row_cells[1], top=80, bottom=80)
        p1 = row_cells[1].paragraphs[0]
        set_paragraph_bidi(p1, WD_ALIGN_PARAGRAPH.JUSTIFY)
        author = item.get("author", "استاد")
        comment = item.get("comment", "")
        add_run(p1, f"[{author}]: ", size=10, bold=True)
        add_run(p1, comment, size=10)
        
        # Action Taken
        set_cell_margins(row_cells[2], top=80, bottom=80)
        p2 = row_cells[2].paragraphs[0]
        set_paragraph_bidi(p2, WD_ALIGN_PARAGRAPH.JUSTIFY)
        action = item.get("action_taken", "اصلاحات مطابق نظر استاد اعمال شد.")
        add_run(p2, action, size=10)
        
        # Location
        set_cell_margins(row_cells[3], top=80, bottom=80)
        p3 = row_cells[3].paragraphs[0]
        set_paragraph_bidi(p3, WD_ALIGN_PARAGRAPH.CENTER)
        loc = item.get("location", "متن رساله")
        add_run(p3, loc, size=10)
        
    # Outro
    p_outro = doc.add_paragraph()
    set_paragraph_bidi(p_outro, WD_ALIGN_PARAGRAPH.JUSTIFY)
    p_outro.paragraph_format.space_before = Pt(14)
    add_run(p_outro, 
        "امید است اصلاحات صورت‌گرفته توانسته باشد استانداردهای علمی مدنظر اساتید محترم را برآورده سازد. "
        "پیشاپیش از حسن نظر و راهنمایی‌های تکمیلی شما سپاسگزارم.", size=11)
        
    doc.save(output_path)
    print(f"Revision Response Document generated at: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Supervisor Revision Response Document Generator")
    parser.add_argument("--json", required=True, help="Path to JSON file with resolved comments")
    parser.add_argument("--out", default="Revision_Response_Table.docx", help="Output .docx file path")
    args = parser.parse_args()
    
    with open(args.json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # If the json is just a list, wrap in dict
    if isinstance(data, list):
        data = {
            "thesis_title": "رساله پژوهشی",
            "student_name": "دانشجو",
            "supervisor_name": "استاد راهنما",
            "comments": data
        }
        
    build_response_document(data, args.out)

if __name__ == "__main__":
    main()
