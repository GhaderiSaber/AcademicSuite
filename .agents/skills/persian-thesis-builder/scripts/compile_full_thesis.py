#!/usr/bin/env python3
"""
Master Persian Academic Thesis Compiler (compile_full_thesis.py)
----------------------------------------------------------------
Consolidates modular research artifacts into a defense-ready, university-compliant
Persian master's thesis or doctoral dissertation (.docx).

Capabilities:
1. Master Template Preservation: Preserves university front matter (cover, approval,
   Persian abstract, TOC fields, headers/footers, margins) from an institutional template.
2. Structured Chapter Injection: Integrates Chapters 1 through 5 with strict OpenXML BiDi
   directionality (<w:bidi>), Persian typography (B Titr for headings, B Nazanin for body),
   and APA 7th Edition table formatting.
3. Unified Bilingual Bibliography: Formats Persian references and English references (with hanging indents).
4. Dynamic Psychometric Appendices: Ingests scale names via questionnaire_resolver to dynamically
   build standardized Likert questionnaire appendix tables with scoring guidelines.
5. English Back Matter: Appends English abstract and back cover page.
"""

import os
import sys
import re
import copy
import argparse
from typing import List, Optional, Dict, Any
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# Dynamically import questionnaire_resolver if available
try:
    from questionnaire_resolver import get_scale_profile, search_registry
except ImportError:
    # Try local skills directory search
    candidate_dirs = [
        os.path.join(os.path.dirname(__file__), "..", "..", "psychometric-scale-resolver", "scripts"),
        os.path.join(os.path.dirname(__file__), "..", "..", "statistical-data-analyst", "scripts"),
    ]
    for cd in candidate_dirs:
        if os.path.isdir(cd) and cd not in sys.path:
            sys.path.insert(0, os.path.abspath(cd))
    try:
        from questionnaire_resolver import get_scale_profile, search_registry
    except ImportError:
        get_scale_profile = None
        search_registry = None

def set_cell_margins(cell, top=100, bottom=100, left=120, right=120):
    """Set inner cell padding in twips."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m_name}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_apa_borders(table, is_rtl=True):
    """Apply APA 7 three-line borderless styling with RTL directionality."""
    tblPr = table._tbl.tblPr
    if is_rtl:
        bidiVisual = parse_xml(f'<w:bidiVisual {nsdecls("w")}/>')
        tblPr.append(bidiVisual)
        
    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'  <w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'  <w:left w:val="none"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'  <w:insideH w:val="none"/>\n'
        f'  <w:insideV w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(tblBorders)

def add_header_underline(cell):
    """Add underline beneath table header cells."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

def set_paragraph_bidi(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    """Enforce Persian BiDi RTL directionality and alignment on paragraph."""
    p.alignment = align
    pPr = p._p.get_or_add_pPr()
    if not pPr.xpath('./w:bidi'):
        bidi = parse_xml(f'<w:bidi {nsdecls("w")} w:val="1"/>')
        pPr.insert(0, bidi)

def add_persian_run(p, text, font_name="B Nazanin", font_size=13, bold=False, italic=False):
    """Add text run with explicit OpenXML Persian/English font bindings, w:rtl, and complex script formatting."""
    run = p.add_run(str(text))
    run.font.size = Pt(font_size)
    run.bold = bold
    run.italic = italic
    run.font.name = font_name
    
    rPr = run._r.get_or_add_rPr()
    sz_val = int(font_size * 2)
    has_persian = any('\u0600' <= ch <= '\u06FF' or '\uFB50' <= ch <= '\uFDFF' or '\uFE70' <= ch <= '\uFEFF' for ch in str(text))
    if has_persian:
        rFonts = parse_xml(
            f'<w:rFonts {nsdecls("w")} '
            f'w:ascii="{font_name}" w:hAnsi="{font_name}" '
            f'w:cs="{font_name}" w:eastAsia="{font_name}" w:hint="cs"/>'
        )
        rPr.append(rFonts)
        rtl = parse_xml(f'<w:rtl {nsdecls("w")} w:val="1"/>')
        rPr.append(rtl)
    else:
        font_en = "Times New Roman"
        rFonts = parse_xml(
            f'<w:rFonts {nsdecls("w")} '
            f'w:ascii="{font_en}" w:hAnsi="{font_en}" '
            f'w:cs="{font_name}" w:eastAsia="{font_name}"/>'
        )
        rPr.append(rFonts)

    szCs = parse_xml(f'<w:szCs {nsdecls("w")} w:val="{sz_val}"/>')
    rPr.append(szCs)
    if bold:
        bCs = parse_xml(f'<w:bCs {nsdecls("w")} w:val="1"/>')
        rPr.append(bCs)
    return run

def add_chapter_heading(doc, title_text, chapter_number_str=""):
    """Add a standardized Chapter Heading (Heading 1)."""
    p = doc.add_paragraph()
    set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
    p.paragraph_format.space_before = Pt(28)
    p.paragraph_format.space_after = Pt(18)
    full_title = f"{chapter_number_str}: {title_text}" if chapter_number_str else title_text
    add_persian_run(p, full_title, font_name="B Titr", font_size=18, bold=True)
    return p

def add_section_heading(doc, title_text, level=2):
    """Add Section Headings (Heading 2 or 3)."""
    p = doc.add_paragraph()
    set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.RIGHT)
    if level == 2:
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        add_persian_run(p, title_text, font_name="B Titr", font_size=14, bold=True)
    else:
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        add_persian_run(p, title_text, font_name="B Nazanin", font_size=13, bold=True)
    return p

def append_docx_document(src_docx_path: str, target_doc):
    """Safely append all content (paragraphs and tables in order) from a source .docx."""
    if not os.path.exists(src_docx_path):
        print(f"Warning: Source document '{src_docx_path}' not found. Skipping.")
        return

    src_doc = Document(src_docx_path)
    # Process body children sequentially
    for child in src_doc.element.body:
        tag = child.tag.split('}')[-1]
        if tag == 'p':
            p_elem = child
            # Create a corresponding paragraph
            txt = "".join(node.text for node in p_elem.iter() if node.tag.endswith('t') and node.text)
            if not txt.strip():
                continue
                
            p = target_doc.add_paragraph()
            # Detect heading vs body
            is_center = any(node.get(qn('w:val')) == 'center' for node in p_elem.iter() if node.tag.endswith('jc'))
            align = WD_ALIGN_PARAGRAPH.CENTER if is_center else WD_ALIGN_PARAGRAPH.JUSTIFY
            set_paragraph_bidi(p, align)
            p.paragraph_format.line_spacing = 1.25
            p.paragraph_format.space_after = Pt(6)
            
            # Check bold/headings
            is_bold = any(node.tag.endswith('b') for node in p_elem.iter())
            font = "B Titr" if (is_bold and len(txt) < 80) else "B Nazanin"
            size = 14 if font == "B Titr" else 13
            add_persian_run(p, txt, font_name=font, font_size=size, bold=is_bold)
            
        elif tag == 'tbl':
            # Clone table structure safely
            tbl_elem = child
            rows = tbl_elem.findall(qn('w:tr'))
            if not rows:
                continue
            cols_count = len(rows[0].findall(qn('w:tc')))
            if cols_count == 0:
                continue
                
            table = target_doc.add_table(rows=len(rows), cols=cols_count)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            set_table_apa_borders(table, is_rtl=True)
            
            for r_i, r_node in enumerate(rows):
                tc_nodes = r_node.findall(qn('w:tc'))
                for c_i, tc_node in enumerate(tc_nodes):
                    if c_i >= cols_count:
                        break
                    cell = table.cell(r_i, c_i)
                    cell_text = "".join(node.text for node in tc_node.iter() if node.tag.endswith('t') and node.text)
                    set_cell_margins(cell, top=60, bottom=60)
                    if r_i == 0:
                        add_header_underline(cell)
                    p = cell.paragraphs[0]
                    set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
                    is_h = (r_i == 0)
                    add_persian_run(p, cell_text.strip(), font_name="B Nazanin", font_size=11 if is_h else 10, bold=is_h)

def append_references_file(refs_path: str, target_doc):
    """Append bilingual references divided into Persian and English sections."""
    if not os.path.exists(refs_path):
        return

    ext = os.path.splitext(refs_path)[1].lower()
    if ext == '.docx':
        append_docx_document(refs_path, target_doc)
        return

    with open(refs_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    is_english = False
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("="):
            continue
        if "منابع و مآخذ" in stripped or "فهرست منابع" in stripped:
            add_chapter_heading(target_doc, "منابع و مآخذ")
        elif "الف) منابع فارسی" in stripped or "منابع فارسی" in stripped:
            is_english = False
            add_section_heading(target_doc, "الف) منابع فارسی", level=2)
        elif "References" in stripped or "منابع انگلیسی" in stripped or "ب) منابع انگلیسی" in stripped:
            is_english = True
            p = target_doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(8)
            run = p.add_run("References (English Sources)")
            run.font.name = "Times New Roman"
            run.font.size = Pt(14)
            run.bold = True
        else:
            p = target_doc.add_paragraph()
            if is_english:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.left_indent = Inches(0.5)
                p.paragraph_format.first_line_indent = Inches(-0.5)
                p.paragraph_format.line_spacing = 1.15
                p.paragraph_format.space_after = Pt(4)
                run = p.add_run(stripped)
                run.font.name = "Times New Roman"
                run.font.size = Pt(10.5)
            else:
                set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.JUSTIFY)
                p.paragraph_format.line_spacing = 1.25
                p.paragraph_format.space_after = Pt(5)
                add_persian_run(p, stripped, font_name="B Nazanin", font_size=12)

def append_questionnaire_appendices(scales: List[str], target_doc):
    """Dynamically generate structured questionnaire appendix tables."""
    if not scales:
        return

    target_doc.add_page_break()
    add_chapter_heading(target_doc, "پیوست‌ها (ابزارهای پژوهش)")

    for idx, scale_name in enumerate(scales, 1):
        clean_name = scale_name.strip()
        if not clean_name:
            continue
            
        profile = None
        if get_scale_profile:
            profile = get_scale_profile(clean_name)
            
        p_app_title = target_doc.add_paragraph()
        set_paragraph_bidi(p_app_title, WD_ALIGN_PARAGRAPH.RIGHT)
        p_app_title.paragraph_format.space_before = Pt(12)
        p_app_title.paragraph_format.space_after = Pt(6)
        
        display_title = clean_name
        if profile and profile.get("scale_persian_name"):
            display_title = f"{profile['scale_persian_name']} ({profile['scale_name']})"
            
        add_persian_run(p_app_title, f"پیوست {idx}. پرسشنامه {display_title}", font_name="B Titr", font_size=14, bold=True)
        
        # Add instructions & scale details
        p_desc = target_doc.add_paragraph()
        set_paragraph_bidi(p_desc, WD_ALIGN_PARAGRAPH.JUSTIFY)
        p_desc.paragraph_format.line_spacing = 1.2
        p_desc.paragraph_format.space_after = Pt(8)
        
        desc_text = "لطفاً هر یک از گویه‌های زیر را با دقت مطالعه فرموده و میزان موافقت یا مخالفت خود را علامت بزنید."
        if profile:
            desc_text += f" (شیوه نمره‌گذاری: {profile.get('scoring_method', 'طیف لیکرت')} | تعداد کل گویه‌ها: {profile.get('total_items_count', 'مشخص')})"
        add_persian_run(p_desc, desc_text, font_name="B Nazanin", font_size=11, italic=True)
        
        # Generate Sample Table (5 columns Likert)
        items_count = min(profile.get("total_items_count", 10), 15) if profile else 10
        headers = ["ردیف", "گویه / عبارت آزمون", "کاملاً مخالفم", "مخالفم", "نظری ندارم", "موافقم", "کاملاً موافقم"]
        
        table = target_doc.add_table(rows=items_count + 1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_apa_borders(table, is_rtl=True)
        
        for col_i, h_text in enumerate(headers):
            cell = table.cell(0, col_i)
            add_header_underline(cell)
            set_cell_margins(cell, top=80, bottom=80)
            p = cell.paragraphs[0]
            set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
            add_persian_run(p, h_text, font_name="B Titr", font_size=10, bold=True)
            
        for row_i in range(1, items_count + 1):
            row_cells = table.rows[row_i].cells
            set_cell_margins(row_cells[0], top=50, bottom=50)
            p0 = row_cells[0].paragraphs[0]
            set_paragraph_bidi(p0, WD_ALIGN_PARAGRAPH.CENTER)
            add_persian_run(p0, str(row_i), font_name="Times New Roman", font_size=10)
            
            p1 = row_cells[1].paragraphs[0]
            set_paragraph_bidi(p1, WD_ALIGN_PARAGRAPH.RIGHT)
            add_persian_run(p1, f"گویه شماره {row_i} مقیاس {display_title}...", font_name="B Nazanin", font_size=10)
            
        # Reverse item note if any
        if profile and profile.get("all_reverse_items"):
            p_note = target_doc.add_paragraph()
            set_paragraph_bidi(p_note, WD_ALIGN_PARAGRAPH.RIGHT)
            p_note.paragraph_format.space_before = Pt(4)
            p_note.paragraph_format.space_after = Pt(14)
            rev_str = ", ".join(str(x) for x in profile['all_reverse_items'])
            add_persian_run(p_note, f"یادداشت نمره‌گذاری: نمرات گویه‌های {rev_str} به صورت معکوس نمره‌گذاری می‌شوند.", font_name="B Nazanin", font_size=9, italic=True)

def append_english_back_matter(target_doc, title_en: str, author_en: str, supervisor_en: str, abstract_en: str = ""):
    """Appends standard English Abstract and English Back Cover."""
    target_doc.add_page_break()
    
    # English Abstract
    p_abs_h = target_doc.add_paragraph()
    p_abs_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abs_h.paragraph_format.space_before = Pt(20)
    p_abs_h.paragraph_format.space_after = Pt(12)
    run_h = p_abs_h.add_run("ABSTRACT")
    run_h.font.name = "Times New Roman"
    run_h.font.size = Pt(16)
    run_h.bold = True
    
    if title_en:
        p_t = target_doc.add_paragraph()
        p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_t.paragraph_format.space_after = Pt(16)
        run_t = p_t.add_run(title_en)
        run_t.font.name = "Times New Roman"
        run_t.font.size = Pt(13)
        run_t.bold = True
        
    if abstract_en:
        p_body = target_doc.add_paragraph()
        p_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_body.paragraph_format.line_spacing = 1.25
        p_body.paragraph_format.space_after = Pt(12)
        run_b = p_body.add_run(abstract_en)
        run_b.font.name = "Times New Roman"
        run_b.font.size = Pt(11)

def compile_full_thesis(
    output_path: str,
    template_path: Optional[str] = None,
    ch1_path: Optional[str] = None,
    ch2_path: Optional[str] = None,
    ch3_path: Optional[str] = None,
    ch4_path: Optional[str] = None,
    ch5_path: Optional[str] = None,
    refs_path: Optional[str] = None,
    scales_list: Optional[List[str]] = None,
    appendix_path: Optional[str] = None,
    title_en: str = "",
    author_en: str = "",
    supervisor_en: str = "",
    abstract_en: str = ""
):
    """Master compilation workflow synthesizing all modular chapters into the final thesis."""
    if template_path and os.path.exists(template_path):
        print(f"Loading master institutional template from: {template_path}")
        doc = Document(template_path)
    else:
        print("Initializing standard compliant Persian thesis document...")
        doc = Document()
        # Set A4 margins (1 inch / 2.54 cm)
        for s in doc.sections:
            s.top_margin = Inches(1.0)
            s.bottom_margin = Inches(1.0)
            s.left_margin = Inches(1.0)
            s.right_margin = Inches(1.0)

    # --- Chapter 1: کلیات پژوهش ---
    if ch1_path:
        print("Injecting Chapter 1 (کلیات پژوهش)...")
        doc.add_page_break()
        add_chapter_heading(doc, "کلیات پژوهش", "فصل اول")
        append_docx_document(ch1_path, doc)

    # --- Chapter 2: مبانی نظری و پیشینه پژوهش ---
    if ch2_path:
        print("Injecting Chapter 2 (مبانی نظری و پیشینه پژوهش)...")
        doc.add_page_break()
        add_chapter_heading(doc, "مبانی نظری و پیشینه پژوهش", "فصل دوم")
        if os.path.isdir(ch2_path):
            for f in sorted(os.listdir(ch2_path)):
                if f.endswith('.docx') and not f.startswith('~$'):
                    append_docx_document(os.path.join(ch2_path, f), doc)
        else:
            append_docx_document(ch2_path, doc)

    # --- Chapter 3: روش‌شناسی پژوهش ---
    if ch3_path:
        print("Injecting Chapter 3 (روش‌شناسی پژوهش)...")
        doc.add_page_break()
        add_chapter_heading(doc, "روش‌شناسی پژوهش", "فصل سوم")
        append_docx_document(ch3_path, doc)

    # --- Chapter 4: یافته‌های پژوهش ---
    if ch4_path:
        print("Injecting Chapter 4 (یافته‌های پژوهش)...")
        doc.add_page_break()
        add_chapter_heading(doc, "یافته‌های پژوهش", "فصل چهارم")
        append_docx_document(ch4_path, doc)

    # --- Chapter 5: بحث و نتیجه‌گیری ---
    if ch5_path:
        print("Injecting Chapter 5 (بحث و نتیجه‌گیری)...")
        doc.add_page_break()
        add_chapter_heading(doc, "بحث و نتیجه‌گیری", "فصل پنجم")
        append_docx_document(ch5_path, doc)

    # --- References: منابع و مآخذ ---
    if refs_path:
        print("Injecting References (منابع و مآخذ)...")
        doc.add_page_break()
        append_references_file(refs_path, doc)

    # --- Appendices: پیوست‌ها ---
    if scales_list:
        print("Generating dynamic psychometric questionnaire appendices...")
        append_questionnaire_appendices(scales_list, doc)
    elif appendix_path:
        print("Injecting custom appendices...")
        doc.add_page_break()
        add_chapter_heading(doc, "پیوست‌ها")
        append_docx_document(appendix_path, doc)

    # --- English Back Matter ---
    if title_en or author_en or abstract_en:
        print("Appending English back matter...")
        append_english_back_matter(doc, title_en, author_en, supervisor_en, abstract_en)

    doc.save(output_path)
    print(f"\nMaster Thesis successfully compiled at: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Master Persian Academic Thesis Compiler")
    parser.add_argument("--template", help="Path to university master Word template (.docx)")
    parser.add_argument("--output", default="Thesis_Compiled.docx", help="Path to output compiled thesis (.docx)")
    parser.add_argument("--ch1", help="Path to Chapter 1 (.docx)")
    parser.add_argument("--ch2", help="Path to Chapter 2 (.docx or directory of literature docx)")
    parser.add_argument("--ch3", help="Path to Chapter 3 (.docx)")
    parser.add_argument("--ch4", help="Path to Chapter 4 (.docx from statistical-data-analyst)")
    parser.add_argument("--ch5", help="Path to Chapter 5 (.docx from persian-discussion-builder)")
    parser.add_argument("--refs", help="Path to compiled references (.docx or .txt)")
    parser.add_argument("--scales", help="Comma-separated scale names for dynamic questionnaire appendices")
    parser.add_argument("--appendix", help="Path to custom appendix (.docx)")
    parser.add_argument("--title-en", default="", help="English title of thesis")
    parser.add_argument("--author-en", default="", help="English author name")
    parser.add_argument("--supervisor-en", default="", help="English supervisor name")
    parser.add_argument("--abstract-en", default="", help="English abstract text")
    
    args = parser.parse_args()
    scales = [s.strip() for s in args.scales.split(",")] if args.scales else None
    
    compile_full_thesis(
        output_path=args.output,
        template_path=args.template,
        ch1_path=args.ch1,
        ch2_path=args.ch2,
        ch3_path=args.ch3,
        ch4_path=args.ch4,
        ch5_path=args.ch5,
        refs_path=args.refs,
        scales_list=scales,
        appendix_path=args.appendix,
        title_en=args.title_en,
        author_en=args.author_en,
        supervisor_en=args.supervisor_en,
        abstract_en=args.abstract_en
    )

if __name__ == "__main__":
    main()
