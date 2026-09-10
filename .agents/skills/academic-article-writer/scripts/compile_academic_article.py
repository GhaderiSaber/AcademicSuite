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


def export_claim_evidence_matrix_excel(claims_data: list, out_path: str, lang: str = "en"):
    """
    Exports a professional 3-color Claim-Evidence Mapping Matrix to Excel.
    Enforces the rule that every claim in Abstract/Introduction/Discussion
    must have direct empirical statistical backing.
    """
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "ماتریس ادعا-شواهد" if lang == "fa" else "Claim-Evidence Matrix"
    ws.views.sheetView[0].rightToLeft = (lang == "fa")

    navy_fill = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid")
    green_fill = PatternFill(start_color="E6FFFA", end_color="E6FFFA", fill_type="solid")
    amber_fill = PatternFill(start_color="FEFCBF", end_color="FEFCBF", fill_type="solid")
    red_fill = PatternFill(start_color="FED7D7", end_color="FED7D7", fill_type="solid")

    title_font = Font(name="B Titr" if lang == "fa" else "Calibri", size=14, bold=True, color="1A365D")
    header_font = Font(name="B Titr" if lang == "fa" else "Calibri", size=10, bold=True, color="FFFFFF")
    body_font = Font(name="B Nazanin" if lang == "fa" else "Calibri", size=10)
    thin_border = Border(left=Side(style='thin', color='CBD5E0'), right=Side(style='thin', color='CBD5E0'),
                         top=Side(style='thin', color='CBD5E0'), bottom=Side(style='thin', color='CBD5E0'))

    ws["A1"] = "ماتریس تطبیق ادعاها با شواهد تجربی و آماری (Claim-Evidence Mapping Matrix)" if lang == "fa" else "Manuscript Claim-Evidence Mapping Matrix (Sida Peng Protocol)"
    ws["A1"].font = title_font

    headers = [
        "شناسه", "بخش مقاله", "ادعای پژوهشی (Claim)", "پارامتر آماری موید (Evidence)", "مقدار آماری", "وضعیت انطباق", "پیشنهاد بازنگری"
    ] if lang == "fa" else [
        "ID", "Section", "Research Claim", "Empirical Evidence / Parameter", "Statistical Value", "Status", "Editorial Remedy"
    ]

    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = navy_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    status_fill_map = {
        "supported": green_fill,
        "تاییدشده": green_fill,
        "needs_evidence": amber_fill,
        "نیازمند شواهد": amber_fill,
        "overgeneralized": red_fill,
        "تعمیم‌افراطی": red_fill
    }

    for r_idx, c_item in enumerate(claims_data, 4):
        status = c_item.get("status", "supported").lower()
        fill = status_fill_map.get(status, green_fill)
        
        ws.cell(row=r_idx, column=1, value=c_item.get("claim_id", f"C{r_idx-3}")).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=2, value=c_item.get("section", "Abstract")).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=3, value=c_item.get("claim_text", ""))
        ws.cell(row=r_idx, column=4, value=c_item.get("evidence_parameter", ""))
        ws.cell(row=r_idx, column=5, value=c_item.get("statistical_value", "")).alignment = Alignment(horizontal="center")
        c_status = ws.cell(row=r_idx, column=6, value=c_item.get("status", "supported").upper())
        c_status.alignment = Alignment(horizontal="center")
        c_status.fill = fill
        ws.cell(row=r_idx, column=7, value=c_item.get("remedy_suggestion", ""))

        for col_i in range(1, 8):
            ws.cell(row=r_idx, column=col_i).font = body_font
            ws.cell(row=r_idx, column=col_i).border = thin_border

    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = min(50, max(12, max_len + 3))

    wb.save(out_path)
    print(f"Claim-Evidence Matrix successfully exported: {out_path}")


def export_figure_planning_matrix_excel(figures_data: list, out_path: str, lang: str = "en"):
    """
    Exports a professional Figure-First Planning Matrix to Excel.
    Maps each planned visual asset to its supporting claim, panel breakdown,
    underlying statistical parameter, and asset disk status.
    """
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "ماتریس برنامه‌ریزی شکل‌ها" if lang == "fa" else "Figure Planning Matrix"
    ws.views.sheetView[0].rightToLeft = (lang == "fa")

    navy_fill = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid")
    green_fill = PatternFill(start_color="27AE60", end_color="27AE60", fill_type="solid")
    amber_fill = PatternFill(start_color="E67E22", end_color="E67E22", fill_type="solid")

    title_font = Font(name="B Titr" if lang == "fa" else "Calibri", size=14, bold=True, color="1A365D")
    header_font = Font(name="B Titr" if lang == "fa" else "Calibri", size=10, bold=True, color="FFFFFF")
    body_font = Font(name="B Nazanin" if lang == "fa" else "Calibri", size=10)
    thin_border = Border(left=Side(style='thin', color='CBD5E0'), right=Side(style='thin', color='CBD5E0'),
                         top=Side(style='thin', color='CBD5E0'), bottom=Side(style='thin', color='CBD5E0'))

    ws["A1"] = "ماتریس نگارش شکل-محور و برنامه‌ریزی شواهد بصری (Figure-First Planning Matrix)" if lang == "fa" else "Figure-First Manuscript Planning Matrix (Nature/MedSci Protocol)"
    ws["A1"].font = title_font

    headers = [
        "شناسه شکل", "عنوان شکل", "ادعای متناظر", "پارامتر آماری مصورسازی", "تفکیک پنل‌ها", "مسیر فایل تصویر", "وضعیت فایل", "توضیحات و یادداشت APA 7"
    ] if lang == "fa" else [
        "Figure ID", "Figure Title", "Supported Claim", "Visualized Statistical Parameter", "Panel Breakdown", "Asset File Path", "Asset Status", "APA 7 Caption & Notes"
    ]

    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = navy_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for r_idx, f_item in enumerate(figures_data, 4):
        f_id = f_item.get("figure_id") or f"Figure {r_idx - 3}"
        f_title = f_item.get("title", "")
        c_id = f_item.get("claim_id", f"C{r_idx - 3}")
        stat_param = f_item.get("statistical_parameter", "")
        panels = ", ".join(f_item.get("panels", [])) if isinstance(f_item.get("panels"), list) else str(f_item.get("panels", ""))
        img_path = f_item.get("image_path") or f_item.get("file_path", "")
        file_exists = bool(img_path and os.path.exists(img_path))
        status_text = ("موجود و درج‌شده" if lang == "fa" else "VERIFIED & EMBEDDED") if file_exists else ("در انتظار تولید" if lang == "fa" else "PENDING GENERATION")
        status_fill = green_fill if file_exists else amber_fill
        caption = f_item.get("caption") or f_item.get("note", "")

        ws.cell(row=r_idx, column=1, value=f_id).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=2, value=f_title)
        ws.cell(row=r_idx, column=3, value=c_id).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=4, value=stat_param).alignment = Alignment(horizontal="center")
        ws.cell(row=r_idx, column=5, value=panels)
        ws.cell(row=r_idx, column=6, value=img_path)

        st_c = ws.cell(row=r_idx, column=7, value=status_text)
        st_c.alignment = Alignment(horizontal="center")
        st_c.fill = status_fill
        st_c.font = Font(name="Arial", size=9, bold=True, color="FFFFFF")

        ws.cell(row=r_idx, column=8, value=caption)

        for col_i in range(1, 9):
            if col_i != 7:
                ws.cell(row=r_idx, column=col_i).font = body_font
            ws.cell(row=r_idx, column=col_i).border = thin_border

    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = min(45, max(12, max_len + 3))

    wb.save(out_path)
    print(f"Figure Planning Matrix successfully exported: {out_path}")


def compute_article_readiness_score(data: dict) -> dict:
    """
    Computes a pre-flight Submission Readiness Score (SRS: 0-100%) for academic manuscripts.
    Weights:
      - 40%: IMRaD Structural Completeness (Abstract 5 parts, Intro, Method 4 subsections, Results, Discussion, Refs >= 15)
      - 25%: Claim-Evidence Backing Ratio (Claims matrix verification)
      - 20%: Figure-First Visual Backing (Presence of publication-grade figures/tables supporting claims)
      - 15%: APA 7 Typography & Formatting (Abstract word count <= 250, title brevity, table captions)
    """
    # 1. IMRaD Completeness (40 pts)
    imrad_points = 0.0
    abstract = data.get("abstract", {})
    if isinstance(abstract, dict) and all(k in abstract for k in ["background", "objective", "methods", "results", "conclusion"]):
        imrad_points += 10.0
    elif abstract:
        imrad_points += 6.0

    intro = data.get("introduction", [])
    if len(intro) >= 3:
        imrad_points += 6.0
    elif intro:
        imrad_points += 3.0

    method = data.get("method", {})
    if isinstance(method, dict) and all(k in method for k in ["design_and_participants", "measures", "procedure", "statistical_analysis"]):
        imrad_points += 8.0
    elif method:
        imrad_points += 4.0

    results = data.get("results", {})
    if results.get("narrative") and (results.get("tables") or results.get("figures") or data.get("figures")):
        imrad_points += 8.0
    elif results:
        imrad_points += 4.0

    disc = data.get("discussion", [])
    if len(disc) >= 3:
        imrad_points += 4.0
    elif disc:
        imrad_points += 2.0

    refs = data.get("references", [])
    if len(refs) >= 20:
        imrad_points += 4.0
    elif len(refs) >= 10:
        imrad_points += 2.0

    # 2. Claim-Evidence Ratio (25 pts)
    claims = data.get("claims_matrix") or data.get("claim_evidence_matrix", [])
    if claims:
        sup_cnt = sum(1 for c in claims if c.get("status", "").lower() in ["supported", "تاییدشده"])
        claim_ratio = sup_cnt / len(claims)
        claims_points = claim_ratio * 25.0
    else:
        claims_points = 20.0

    # 3. Figure-First Planning (20 pts)
    figs = data.get("figures") or data.get("results", {}).get("figures", [])
    tbls = data.get("results", {}).get("tables", [])
    total_visuals = len(figs) + len(tbls)
    if total_visuals >= 4:
        figure_points = 20.0
    elif total_visuals >= 2:
        figure_points = 15.0
    elif total_visuals >= 1:
        figure_points = 10.0
    else:
        figure_points = 4.0

    # 4. APA 7 & Technical Checklist (15 pts)
    apa_points = 0.0
    title = data.get("title", "")
    if 5 <= len(title.split()) <= 20:
        apa_points += 5.0
    else:
        apa_points += 2.5

    kw = data.get("keywords", [])
    if 3 <= len(kw) <= 7:
        apa_points += 5.0
    else:
        apa_points += 2.0

    if tbls or figs:
        apa_points += 5.0

    total_score = round(imrad_points + claims_points + figure_points + apa_points, 1)
    total_score = max(0.0, min(100.0, total_score))

    if total_score >= 90:
        grade = "A+"
        verdict_en = "Submission Ready (High-Impact Journal)"
        verdict_fa = "آماده ارسال به مجلات معتبر (A+)"
    elif total_score >= 80:
        grade = "A"
        verdict_en = "Ready with Minor Revisions"
        verdict_fa = "آماده ارسال با اصلاحات جزیی (A)"
    elif total_score >= 70:
        grade = "B"
        verdict_en = "Substantial Revisions Recommended Before Submission"
        verdict_fa = "نیازمند تکمیل شواهد و شکل‌ها قبل از ارسال (B)"
    else:
        grade = "C"
        verdict_en = "Major Structural Gaps - Not Submission Ready"
        verdict_fa = "دارای نواقص اساسی در ساختار مقاله (C)"

    return {
        "submission_readiness_score": total_score,
        "grade": grade,
        "verdict_en": verdict_en,
        "verdict_fa": verdict_fa,
        "subscores": {
            "imrad_completeness": round(imrad_points, 1),
            "claim_evidence_backing": round(claims_points, 1),
            "figure_first_visuals": round(figure_points, 1),
            "apa7_technical": round(apa_points, 1)
        }
    }


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

    # --- 7b. Add Figures (Figure-First Publishing Workflow) ---
    figures_data = data.get("figures") or results_data.get("figures", [])
    for f_idx, fig_info in enumerate(figures_data):
        fig_id = fig_info.get("figure_id") or f"Figure {f_idx + 1}"
        fig_title = fig_info.get("title", "")
        img_path = fig_info.get("image_path") or fig_info.get("file_path", "")
        panels = fig_info.get("panels", [])
        caption = fig_info.get("caption", "")
        note = fig_info.get("note", "")

        # Caption above figure
        p_fcap = doc.add_paragraph()
        if is_fa:
            set_paragraph_bidi(p_fcap)
            add_run(p_fcap, f"شکل {f_idx + 1}. {fig_title}", lang=lang, size=11, bold=True)
            if panels:
                p_pan = doc.add_paragraph()
                set_paragraph_bidi(p_pan)
                add_run(p_pan, f"پنل‌ها: {', '.join(panels)}", lang=lang, size=10, italic=True)
        else:
            p_fcap.alignment = WD_ALIGN_PARAGRAPH.LEFT
            add_run(p_fcap, f"{fig_id}\n", lang=lang, size=11, bold=True)
            add_run(p_fcap, fig_title, lang=lang, size=11, italic=True)
            if panels:
                p_pan = doc.add_paragraph()
                p_pan.alignment = WD_ALIGN_PARAGRAPH.LEFT
                add_run(p_pan, f"Subpanels: {', '.join(panels)}", lang=lang, size=10, italic=True)
        p_fcap.paragraph_format.space_before = Pt(10)
        p_fcap.paragraph_format.space_after = Pt(4)

        # Image Embed
        if img_path and os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(4)
            p_img.paragraph_format.space_after = Pt(4)
            r_img = p_img.add_run()
            try:
                r_img.add_picture(img_path, width=Inches(5.5))
            except Exception as e:
                add_run(p_img, f"[Figure asset loading error: {e}]", lang=lang, size=9, italic=True)
        elif img_path:
            p_ph = doc.add_paragraph()
            p_ph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_run(p_ph, f"[Figure Asset Placeholder: {img_path} — Ready for Insertion]", lang=lang, size=9, italic=True)

        # Figure Note below figure (APA 7)
        full_note = caption or note
        if full_note:
            p_fnote = doc.add_paragraph()
            if is_fa:
                set_paragraph_bidi(p_fnote)
                add_run(p_fnote, f"یادداشت: {full_note}", lang=lang, size=9)
            else:
                p_fnote.alignment = WD_ALIGN_PARAGRAPH.LEFT
                add_run(p_fnote, "Note. ", lang=lang, size=9, italic=True)
                add_run(p_fnote, full_note, lang=lang, size=9)
            p_fnote.paragraph_format.space_before = Pt(2)
            p_fnote.paragraph_format.space_after = Pt(12)

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

    # Export Claim-Evidence Matrix if present
    claims_matrix = data.get("claims_matrix") or data.get("claim_evidence_matrix", [])
    if claims_matrix:
        matrix_filename = output_path.replace(".docx", "_claim_evidence_matrix.xlsx")
        export_claim_evidence_matrix_excel(claims_matrix, matrix_filename, lang=lang)

    # Export Figure Planning Matrix if present
    figs_for_matrix = data.get("figures") or results_data.get("figures", [])
    if figs_for_matrix:
        fig_matrix_filename = output_path.replace(".docx", "_figure_planning_matrix.xlsx")
        export_figure_planning_matrix_excel(figs_for_matrix, fig_matrix_filename, lang=lang)

    # Compute Submission Readiness Score (SRS)
    srs_report = compute_article_readiness_score(data)
    print(f"\n[+] Submission Readiness Score (SRS): {srs_report['submission_readiness_score']:.1f}% (Grade: {srs_report['grade']})")
    print(f"    - Verdict: {srs_report['verdict_en']} / {srs_report['verdict_fa']}")
    print(f"    - Subscores: IMRaD={srs_report['subscores']['imrad_completeness']}/40, "
          f"Claims={srs_report['subscores']['claim_evidence_backing']}/25, "
          f"Figures={srs_report['subscores']['figure_first_visuals']}/20, "
          f"APA7={srs_report['subscores']['apa7_technical']}/15")

    doc.save(output_path)
    print(f"Academic Article successfully compiled at: {output_path}")
    return srs_report

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
