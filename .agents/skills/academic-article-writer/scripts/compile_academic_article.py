#!/usr/bin/env python3
"""
Academic Journal Article Compiler (compile_academic_article.py)
--------------------------------------------------------------
Compiles publication-ready academic manuscripts conforming to international IMRaD & APA 7th Edition standards.
Supports dual publishing tracks:
1. 'en': International English Journal Article (ISI / Scopus / Web of Science, Q1/Q2 standards).
2. 'fa': Iranian Scientific-Research Journal Article (علمی-پژوهشی / ISC) with academic Persian typography.
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

def set_apa_table_borders(table, is_rtl=False):
    """Apply APA 7 three-line borderless styling."""
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
    """Add underline under header row cells."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

def set_paragraph_bidi(p, align=WD_ALIGN_PARAGRAPH.RIGHT):
    """Enforce Persian BiDi RTL directionality on paragraph."""
    p.alignment = align
    pPr = p._p.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    bidi.set(qn('w:val'), '1')
    pPr.append(bidi)

def add_run(p, text, lang='fa', size=12, bold=False, italic=False):
    """Add run with appropriate font bindings based on language."""
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    
    font_fa = 'B Titr' if (bold and size >= 14) else 'B Nazanin'
    font_en = 'Times New Roman'
    
    if lang == 'fa':
        run.font.name = font_fa
        rPr = run._r.get_or_add_rPr()
        rFonts = parse_xml(
            f'<w:rFonts {nsdecls("w")} '
            f'w:ascii="{font_en}" w:hAnsi="{font_en}" '
            f'w:cs="{font_fa}" w:eastAsia="{font_fa}"/>'
        )
        rPr.append(rFonts)
    else:
        run.font.name = font_en
        
    return run

def compile_article(data: dict, output_path: str, lang: str = 'en'):
    doc = docx.Document()
    is_fa = (lang == 'fa')
    
    # Page setup (Standard A4 with 1-inch / 2.54cm margins)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        
    align_center = WD_ALIGN_PARAGRAPH.CENTER
    align_body = WD_ALIGN_PARAGRAPH.JUSTIFY if is_fa else WD_ALIGN_PARAGRAPH.LEFT
    
    # --- 1. Title ---
    p_title = doc.add_paragraph()
    if is_fa:
        set_paragraph_bidi(p_title, align_center)
    else:
        p_title.alignment = align_center
    p_title.paragraph_format.space_before = Pt(20)
    p_title.paragraph_format.space_after = Pt(12)
    add_run(p_title, data.get("title", "Article Title"), lang=lang, size=16, bold=True)
    
    # --- 2. Authors & Affiliations ---
    p_auth = doc.add_paragraph()
    if is_fa:
        set_paragraph_bidi(p_auth, align_center)
    else:
        p_auth.alignment = align_center
    p_auth.paragraph_format.space_after = Pt(6)
    authors_str = ", ".join(data.get("authors", ["Author Name"]))
    add_run(p_auth, authors_str, lang=lang, size=12, bold=True)
    
    p_affil = doc.add_paragraph()
    if is_fa:
        set_paragraph_bidi(p_affil, align_center)
    else:
        p_affil.alignment = align_center
    p_affil.paragraph_format.space_after = Pt(20)
    affil_str = data.get("affiliation", "Department of Psychology, University")
    add_run(p_affil, affil_str, lang=lang, size=10, italic=True)
    
    # --- 3. Structured Abstract ---
    p_abs_h = doc.add_paragraph()
    if is_fa:
        set_paragraph_bidi(p_abs_h, WD_ALIGN_PARAGRAPH.RIGHT)
        add_run(p_abs_h, "چکیده", lang=lang, size=13, bold=True)
    else:
        p_abs_h.alignment = WD_ALIGN_PARAGRAPH.LEFT
        add_run(p_abs_h, "Abstract", lang=lang, size=12, bold=True)
    p_abs_h.paragraph_format.space_after = Pt(4)
    
    abstract_dict = data.get("abstract", {})
    if isinstance(abstract_dict, dict):
        p_abs = doc.add_paragraph()
        if is_fa:
            set_paragraph_bidi(p_abs, align_body)
            p_abs.paragraph_format.line_spacing = 1.2
            for part_key, part_title in [
                ("background", "مقدمه: "),
                ("objective", "هدف: "),
                ("methods", "روش: "),
                ("results", "یافته‌ها: "),
                ("conclusion", "نتیجه‌گیری: ")
            ]:
                if part_key in abstract_dict:
                    add_run(p_abs, part_title, lang=lang, size=11, bold=True)
                    add_run(p_abs, f"{abstract_dict[part_key]} ", lang=lang, size=11)
        else:
            p_abs.alignment = align_body
            p_abs.paragraph_format.line_spacing = 1.15
            for part_key, part_title in [
                ("background", "Background: "),
                ("objective", "Objective: "),
                ("methods", "Methods: "),
                ("results", "Results: "),
                ("conclusion", "Conclusion: ")
            ]:
                if part_key in abstract_dict:
                    add_run(p_abs, part_title, lang=lang, size=11, bold=True)
                    add_run(p_abs, f"{abstract_dict[part_key]} ", lang=lang, size=11)
    else:
        p_abs = doc.add_paragraph()
        if is_fa:
            set_paragraph_bidi(p_abs, align_body)
        else:
            p_abs.alignment = align_body
        add_run(p_abs, str(abstract_dict), lang=lang, size=11)
        
    p_abs.paragraph_format.space_after = Pt(8)
    
    # Keywords
    p_kw = doc.add_paragraph()
    if is_fa:
        set_paragraph_bidi(p_kw, WD_ALIGN_PARAGRAPH.RIGHT)
        add_run(p_kw, "کلیدواژه‌ها: ", lang=lang, size=11, bold=True)
    else:
        p_kw.alignment = WD_ALIGN_PARAGRAPH.LEFT
        add_run(p_kw, "Keywords: ", lang=lang, size=11, bold=True, italic=True)
    keywords_str = "; ".join(data.get("keywords", []))
    add_run(p_kw, keywords_str, lang=lang, size=11)
    p_kw.paragraph_format.space_after = Pt(20)
    
    # --- 4. Section Helper ---
    def add_section(title_fa, title_en, content_paragraphs):
        p_h = doc.add_paragraph()
        title = title_fa if is_fa else title_en
        if is_fa:
            set_paragraph_bidi(p_h)
            add_run(p_h, title, lang=lang, size=14, bold=True)
        else:
            p_h.alignment = WD_ALIGN_PARAGRAPH.LEFT
            add_run(p_h, title, lang=lang, size=13, bold=True)
        p_h.paragraph_format.space_before = Pt(14)
        p_h.paragraph_format.space_after = Pt(6)
        
        for c_text in content_paragraphs:
            p_body = doc.add_paragraph()
            if is_fa:
                set_paragraph_bidi(p_body, align_body)
                p_body.paragraph_format.line_spacing = 1.25
                add_run(p_body, c_text, lang=lang, size=12)
            else:
                p_body.alignment = align_body
                p_body.paragraph_format.line_spacing = 1.5
                add_run(p_body, c_text, lang=lang, size=12)
            p_body.paragraph_format.space_after = Pt(6)

    # --- 5. Introduction ---
    intro_paragraphs = data.get("introduction", [
        "Mental health issues in adolescents pose significant societal and individual burdens...",
        "Theoretical models suggest that cognitive appraisals mediate the relationship between stress and functioning...",
        "Despite existing literature, few studies have examined these specific mediation mechanisms...",
        "The present study investigated the efficacy of mindfulness training and tested directional hypotheses."
    ])
    add_section("۱. مقدمه", "1. Introduction", intro_paragraphs)

    # --- 6. Method ---
    method_data = data.get("method", {})
    method_paragraphs = [
        f"{'طرح پژوهش و شرکت‌کنندگان: ' if is_fa else 'Design and Participants: '}{method_data.get('design_and_participants', '')}",
        f"{'ابزارهای گردآوری داده‌ها: ' if is_fa else 'Measures: '}{method_data.get('measures', '')}",
        f"{'روش اجرا و ملاحظات اخلاقی: ' if is_fa else 'Procedure and Ethical Considerations: '}{method_data.get('procedure', '')}",
        f"{'روش‌های تجزیه‌وتحلیل داده‌ها: ' if is_fa else 'Statistical Analysis Plan: '}{method_data.get('statistical_analysis', '')}"
    ]
    add_section("۲. روش پژوهش", "2. Method", method_paragraphs)

    # --- 7. Results ---
    results_data = data.get("results", {})
    results_paragraphs = results_data.get("narrative", [
        "Preliminary analyses verified univariate normality via skewness, kurtosis, and the Shapiro-Wilk test.",
        "Primary hypothesis testing via One-Way ANCOVA indicated statistically significant intervention efficacy."
    ])
    add_section("۳. یافته‌ها", "3. Results", results_paragraphs)
    
    # Add Tables if present in data
    tables_data = results_data.get("tables", [])
    for t_idx, tbl_info in enumerate(tables_data):
        p_tcap = doc.add_paragraph()
        if is_fa:
            set_paragraph_bidi(p_tcap)
            add_run(p_tcap, f"جدول {t_idx+1}. {tbl_info.get('title', '')}", lang=lang, size=11, bold=True)
        else:
            p_tcap.alignment = WD_ALIGN_PARAGRAPH.LEFT
            add_run(p_tcap, f"Table {t_idx+1}\n", lang=lang, size=11, bold=True)
            add_run(p_tcap, tbl_info.get('title', ''), lang=lang, size=11, italic=True)
        p_tcap.paragraph_format.space_before = Pt(8)
        p_tcap.paragraph_format.space_after = Pt(4)
        
        headers = tbl_info.get("headers", [])
        rows = tbl_info.get("rows", [])
        
        table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_apa_table_borders(table, is_rtl=is_fa)
        
        # Headers
        for col_i, h_text in enumerate(headers):
            cell = table.cell(0, col_i)
            add_header_underline(cell)
            set_cell_margins(cell, top=100, bottom=100)
            p = cell.paragraphs[0]
            if is_fa:
                set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_run(p, h_text, lang=lang, size=10, bold=True)
            
        # Rows
        for r_i, r_vals in enumerate(rows):
            row_cells = table.rows[r_i + 1].cells
            for c_i, val_str in enumerate(r_vals):
                cell = row_cells[c_i]
                set_cell_margins(cell, top=60, bottom=60)
                p = cell.paragraphs[0]
                if is_fa:
                    set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                add_run(p, str(val_str), lang=lang, size=10)
                
        # Note
        note = tbl_info.get("note", "")
        if note:
            p_note = doc.add_paragraph()
            if is_fa:
                set_paragraph_bidi(p_note)
            else:
                p_note.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p_note.paragraph_format.space_before = Pt(4)
            p_note.paragraph_format.space_after = Pt(12)
            add_run(p_note, f"{'یادداشت: ' if is_fa else 'Note. '}{note}", lang=lang, size=9)

    # --- 8. Discussion ---
    discussion_paragraphs = data.get("discussion", [
        "This study investigated the effectiveness of mindfulness in reducing academic anxiety and increasing resilience.",
        "The findings support the theoretical model of emotion regulation and cognitive decentering...",
        "Clinical implications include designing school-based intervention modules...",
        "Limitations include reliance on self-report instruments and convenience sampling.",
        "In conclusion, mindfulness-based interventions represent a robust approach for adolescent mental health."
    ])
    add_section("۴. بحث و نتیجه‌گیری", "4. Discussion and Conclusion", discussion_paragraphs)

    # --- 9. References ---
    p_ref_h = doc.add_paragraph()
    if is_fa:
        set_paragraph_bidi(p_ref_h)
        add_run(p_ref_h, "منابع", lang=lang, size=14, bold=True)
    else:
        p_ref_h.alignment = WD_ALIGN_PARAGRAPH.LEFT
        add_run(p_ref_h, "References", lang=lang, size=13, bold=True)
    p_ref_h.paragraph_format.space_before = Pt(16)
    p_ref_h.paragraph_format.space_after = Pt(8)
    
    for ref_str in data.get("references", []):
        p_ref = doc.add_paragraph()
        if is_fa:
            set_paragraph_bidi(p_ref, align_body)
        else:
            p_ref.alignment = align_body
            p_ref.paragraph_format.left_indent = Inches(0.5)
            p_ref.paragraph_format.first_line_indent = Inches(-0.5)
        p_ref.paragraph_format.space_after = Pt(4)
        add_run(p_ref, ref_str, lang=lang, size=10)

    doc.save(output_path)
    print(f"Academic Article successfully compiled at: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Academic Journal Article Compiler")
    parser.add_argument("--json", required=True, help="Path to article structured JSON file")
    parser.add_argument("--out", default="Article_Manuscript.docx", help="Output .docx file path")
    parser.add_argument("--lang", default="en", choices=["en", "fa"], help="Target language track ('en' for ISI/Scopus, 'fa' for ISC)")
    args = parser.parse_args()
    
    with open(args.json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    compile_article(data, args.out, lang=args.lang)

if __name__ == "__main__":
    main()
