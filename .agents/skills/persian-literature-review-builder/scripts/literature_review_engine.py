#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Literature Review & Chapter 2 Engine (موتور تدوین جامع فصل دوم: مبانی نظری و پیشینه پژوهش)
Specialized for psychology, counseling, behavioral sciences, and Iranian graduate theses.

Adheres strictly to:
- APA 7th Edition standards (In-text citations, table rules)
- Authentic Iranian university academic typography (B Titr, B Nazanin, Times New Roman)
- Full OpenXML BiDi RTL standards (<w:bidi w:val="1"/> and <w:bidiVisual/>)
- Multi-sheet Excel literature matrix export
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any, Optional

import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


# ==============================================================================
# OpenXML XML Helper Utilities for Word Documents
# ==============================================================================

def set_run_font(run, font_name: str = "B Nazanin", size_pt: float = 13, bold: bool = False, italic: bool = False, is_latin: bool = False):
    """Sets exact ASCII and Complex Script (CS) fonts for Arabic/Persian scripts."""
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size_pt)
    
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    
    if is_latin:
        rFonts.set(qn('w:ascii'), 'Times New Roman')
        rFonts.set(qn('w:hAnsi'), 'Times New Roman')
        rFonts.set(qn('w:cs'), font_name)
    else:
        rFonts.set(qn('w:ascii'), 'Times New Roman')
        rFonts.set(qn('w:hAnsi'), 'Times New Roman')
        rFonts.set(qn('w:cs'), font_name)
        
        # Add RTL marker
        rtl = rPr.find(qn('w:rtl'))
        if rtl is None:
            rtl = OxmlElement('w:rtl')
            rPr.append(rtl)


def set_p_bidi(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before: float = 0, space_after: float = 6, line_spacing: float = 1.25):
    """Enforces BiDi directionality, spacing, and alignment on paragraph level."""
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    
    pPr = p._p.get_or_add_pPr()
    bidi = pPr.find(qn('w:bidi'))
    if bidi is None:
        bidi = OxmlElement('w:bidi')
        pPr.append(bidi)


def set_table_bidi_and_center(table):
    """Enforces Right-to-Left visual layout and center alignment on table level."""
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = table._tbl.tblPr
    if tblPr.find(qn('w:bidiVisual')) is None:
        tblPr.append(OxmlElement('w:bidiVisual'))


def set_apa_table_borders(table):
    """Applies strict APA 7th Edition border rules: 3 horizontal lines, zero vertical lines."""
    tblPr = table._tbl.tblPr
    existing_borders = tblPr.find(qn('w:tblBorders'))
    if existing_borders is not None:
        tblPr.remove(existing_borders)
        
    borders_xml = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'  <w:insideH w:val="none"/>\n'
        f'  <w:left w:val="none"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'  <w:insideV w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(borders_xml)
    
    # Bottom underline for the header row
    if len(table.rows) > 0:
        for cell in table.rows[0].cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(
                f'<w:tcBorders {nsdecls("w")}>\n'
                f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
                f'</w:tcBorders>'
            )
            tcPr.append(tcBorders)


def set_cell_margins(cell, top: int = 100, bottom: int = 100, left: int = 140, right: int = 140):
    """Sets internal padding for a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>\n'
        f'  <w:top w:w="{top}" w:type="dxa"/>\n'
        f'  <w:bottom w:w="{bottom}" w:type="dxa"/>\n'
        f'  <w:left w:w="{left}" w:type="dxa"/>\n'
        f'  <w:right w:w="{right}" w:type="dxa"/>\n'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


# ==============================================================================
# Chapter 2 Document Compiler
# ==============================================================================

class Chapter2Compiler:
    """Builds defense-ready Chapter 2 Word documents adhering to Iranian university guidelines."""

    def __init__(self, payload: Dict[str, Any], lang: str = "fa"):
        self.payload = payload
        self.lang = lang
        self.doc = docx.Document()
        self._configure_document_geometry()

    def _configure_document_geometry(self):
        """Sets standard Iranian academic thesis margins (Right: 3cm, Left: 2.5cm, Top/Bottom: 2.5cm)."""
        sections = self.doc.sections
        for s in sections:
            s.top_margin = Inches(0.98)      # 2.5 cm
            s.bottom_margin = Inches(0.98)   # 2.5 cm
            s.right_margin = Inches(1.18)    # 3.0 cm (Binding margin for Persian RTL)
            s.left_margin = Inches(0.98)     # 2.5 cm

    def add_chapter_heading(self, text: str):
        """Adds centered Chapter 1 heading."""
        p = self.doc.add_paragraph()
        set_p_bidi(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=18)
        run = p.add_run(text)
        set_run_font(run, font_name="B Titr", size_pt=16, bold=True)

    def add_heading_2(self, text: str):
        """Adds Heading 2 for major chapter sections (B Titr 14pt Bold)."""
        p = self.doc.add_paragraph()
        set_p_bidi(p, align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=14, space_after=6)
        run = p.add_run(text)
        set_run_font(run, font_name="B Titr", size_pt=14, bold=True)

    def add_heading_3(self, text: str):
        """Adds Heading 3 for sub-sections (B Titr 12pt Bold or B Nazanin 13pt Bold)."""
        p = self.doc.add_paragraph()
        set_p_bidi(p, align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=10, space_after=4)
        run = p.add_run(text)
        set_run_font(run, font_name="B Titr", size_pt=12, bold=True)

    def add_body_paragraph(self, text: str):
        """Adds standard thesis body paragraph with Iranian typography."""
        p = self.doc.add_paragraph()
        set_p_bidi(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6, line_spacing=1.25)
        run = p.add_run(text)
        set_run_font(run, font_name="B Nazanin", size_pt=13, bold=False)

    def add_table_caption(self, caption_text: str):
        """Adds APA 7 table caption above the table."""
        p = self.doc.add_paragraph()
        set_p_bidi(p, align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=12, space_after=4)
        run = p.add_run(caption_text)
        set_run_font(run, font_name="B Nazanin", size_pt=11.5, bold=True)

    def build_empirical_summary_table(self, iranian_studies: List[Dict], international_studies: List[Dict]):
        """Generates the formal APA 7th Edition empirical literature summary table."""
        self.add_table_caption("جدول ۲-۱: خلاصه پیشینه پژوهش‌های تجربی داخلی و خارجی مرتبط با متغیرهای پژوهش")

        # Merge studies with origin tag
        all_studies = []
        for s in iranian_studies:
            s_copy = dict(s)
            s_copy["origin"] = "داخلی"
            all_studies.append(s_copy)
        for s in international_studies:
            s_copy = dict(s)
            s_copy["origin"] = "خارجی"
            all_studies.append(s_copy)

        headers = ["ردیف", "پژوهشگر(ان) و سال", "جامعه و نمونه", "روش و ابزار", "متغیرها", "یافته‌های کلیدی"]
        table = self.doc.add_table(rows=len(all_studies) + 1, cols=len(headers))
        set_table_bidi_and_center(table)

        # Header Row
        hdr_row = table.rows[0]
        hdr_bg = "F0F4F8"
        for i, title in enumerate(headers):
            cell = hdr_row.cells[i]
            set_cell_margins(cell, top=120, bottom=120, left=100, right=100)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hdr_bg}"/>')
            cell._tc.get_or_add_tcPr().append(shading)

            p = cell.paragraphs[0]
            set_p_bidi(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=0)
            run = p.add_run(title)
            set_run_font(run, font_name="B Titr", size_pt=10.5, bold=True)

        # Populate Data Rows
        for r_idx, study in enumerate(all_studies, start=1):
            row = table.rows[r_idx]
            
            # Row numbering in Persian
            row_vals = [
                str(r_idx),
                f"{study.get('authors', '')} ({study.get('year', '')})",
                study.get('sample', ''),
                study.get('methodology', ''),
                study.get('variables', ''),
                study.get('key_findings', '')
            ]

            for c_idx, val in enumerate(row_vals):
                cell = row.cells[c_idx]
                set_cell_margins(cell, top=80, bottom=80, left=90, right=90)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                p = cell.paragraphs[0]
                align = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else (WD_ALIGN_PARAGRAPH.RIGHT if c_idx != 1 else WD_ALIGN_PARAGRAPH.CENTER)
                set_p_bidi(p, align=align, space_before=0, space_after=0)
                run = p.add_run(val)
                set_run_font(run, font_name="B Nazanin", size_pt=10, bold=(c_idx == 0))

        set_apa_table_borders(table)

        # Space after table
        p_after = self.doc.add_paragraph()
        set_p_bidi(p_after, space_before=0, space_after=12)

    def compile(self, output_path: str):
        """Executes the full Chapter 2 synthesis pipeline."""
        # 1. Chapter Title
        ch_title = self.payload.get("chapter_title", "فصل دوم: مبانی نظری و پیشینه پژوهش")
        self.add_chapter_heading(ch_title)

        # 2. Introduction
        self.add_heading_2("۲-۱. مقدمه")
        intro_text = self.payload.get("introduction", "")
        if intro_text:
            self.add_body_paragraph(intro_text)

        # 3. Section 1: Theoretical Foundations
        self.add_heading_2("۲-۲. مبانی نظری متغیرهای پژوهش")
        theoretical_sections = self.payload.get("theoretical_sections", [])
        for sec in theoretical_sections:
            sec_num = sec.get("section_number", "")
            v_name = sec.get("variable_name", "")
            v_en = sec.get("variable_name_en", "")
            heading_title = f"{sec_num}. مبانی نظری {v_name}" + (f" ({v_en})" if v_en else "")
            self.add_heading_3(heading_title)

            for p_text in sec.get("content_paragraphs", []):
                self.add_body_paragraph(p_text)

        # Theoretical Integration
        theor_integ = self.payload.get("theoretical_integration", "")
        if theor_integ:
            self.add_heading_3("۲-۲-۶. تبیین نظری پیوند و روابط متقابل میان متغیرها")
            self.add_body_paragraph(theor_integ)

        # 4. Section 2: Empirical Research Background
        self.add_heading_2("۲-۳. پیشینه تجربی پژوهش")
        
        # International Studies
        intl_studies = self.payload.get("international_studies", [])
        if intl_studies:
            self.add_heading_3("۲-۳-۱. پیشینه پژوهش‌های خارجی")
            for idx, st in enumerate(intl_studies, start=1):
                p_text = (
                    f"{idx}. {st.get('authors', '')} ({st.get('year', '')}) در پژوهشی با عنوان «{st.get('title', '')}» "
                    f"به بررسی روابط میان {st.get('variables', '')} پرداختند. این پژوهش بر روی {st.get('sample', '')} "
                    f"با استفاده از روش {st.get('methodology', '')} انجام شد. "
                    f"یافته‌های این مطالعه نشان داد که {st.get('key_findings', '')}"
                )
                self.add_body_paragraph(p_text)

        # Iranian Studies
        iranian_studies = self.payload.get("iranian_studies", [])
        if iranian_studies:
            self.add_heading_3("۲-۳-۲. پیشینه پژوهش‌های داخلی")
            for idx, st in enumerate(iranian_studies, start=1):
                p_text = (
                    f"{idx}. {st.get('authors', '')} ({st.get('year', '')}) در مطالعه‌ای با عنوان «{st.get('title', '')}» "
                    f"به سنجش {st.get('variables', '')} پرداختند. جامعه و گروه نمونه این پژوهش شامل {st.get('sample', '')} بود "
                    f"که با روش {st.get('methodology', '')} مورد ارزیابی قرار گرفتند. "
                    f"نتایج حاکی از آن بود که {st.get('key_findings', '')}"
                )
                self.add_body_paragraph(p_text)

        # Empirical Summary Table
        if iranian_studies or intl_studies:
            self.build_empirical_summary_table(iranian_studies, intl_studies)

        # 5. Section 3: Synthesis, Research Gap & Conceptual Model
        self.add_heading_2("۲-۴. جمع‌بندی پیشینه پژوهش و شناسایی شکاف پژوهشی")
        res_gap = self.payload.get("research_gap", "")
        if res_gap:
            self.add_body_paragraph(res_gap)

        self.add_heading_2("۲-۵. مدل مفهومی و فرضیات پژوهش")
        conc_model = self.payload.get("conceptual_model", "")
        if conc_model:
            self.add_body_paragraph(conc_model)

        # Save Word document
        self.doc.save(output_path)
        print(f"[SUCCESS] Compiled Defense-Ready Chapter 2: {output_path}")


# ==============================================================================
# Excel Literature Matrix Generator
# ==============================================================================

class ExcelMatrixGenerator:
    """Generates an executive 3-sheet Excel workbook mapping all reviewed literature."""

    def __init__(self, payload: Dict[str, Any]):
        self.payload = payload
        self.wb = openpyxl.Workbook()

    def generate(self, output_path: str):
        # Sheet 1: Overview & Metrics
        ws_overview = self.wb.active
        ws_overview.title = "Overview & Metrics"
        ws_overview.views.sheetView[0].rightToLeft = True

        title_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        title_font = Font(name="B Titr", size=14, bold=True, color="FFFFFF")
        hdr_fill = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
        hdr_font = Font(name="B Titr", size=11, bold=True, color="FFFFFF")
        regular_font = Font(name="B Nazanin", size=11)
        bold_font = Font(name="B Nazanin", size=11, bold=True)
        thin_border = Border(
            left=Side(style='thin', color='D9D9D9'),
            right=Side(style='thin', color='D9D9D9'),
            top=Side(style='thin', color='D9D9D9'),
            bottom=Side(style='thin', color='D9D9D9')
        )

        ws_overview.merge_cells("A1:D1")
        ws_overview["A1"] = "ماتریس جامع مدیریت پیشینه و مبانی نظری فصل دوم پایان‌نامه"
        ws_overview["A1"].fill = title_fill
        ws_overview["A1"].font = title_font
        ws_overview["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws_overview.row_dimensions[1].height = 40

        overview_data = [
            ("عنوان پژوهش", self.payload.get("study_title", "")),
            ("عنوان لاتین", self.payload.get("study_title_en", "")),
            ("تعداد متغیرهای مبانی نظری", len(self.payload.get("theoretical_sections", []))),
            ("تعداد پژوهش‌های خارجی بررسی‌شده", len(self.payload.get("international_studies", []))),
            ("تعداد پژوهش‌های داخلی بررسی‌شده", len(self.payload.get("iranian_studies", []))),
            ("مجموع کل پیشینه‌های تجربی", len(self.payload.get("international_studies", [])) + len(self.payload.get("iranian_studies", []))),
            ("وضعیت تبیین شکاف پژوهشی", "تکمیل و تدوین‌شده"),
            ("وضعیت تدوین مدل مفهومی", "استخراج‌شده بر پایه نظریه‌های مرجع")
        ]

        for r_idx, (k, v) in enumerate(overview_data, start=3):
            ws_overview[f"A{r_idx}"] = k
            ws_overview[f"A{r_idx}"].font = bold_font
            ws_overview[f"A{r_idx}"].fill = PatternFill(start_color="F2F4F7", end_color="F2F4F7", fill_type="solid")
            ws_overview[f"A{r_idx}"].border = thin_border

            ws_overview.merge_cells(f"B{r_idx}:D{r_idx}")
            ws_overview[f"B{r_idx}"] = str(v)
            ws_overview[f"B{r_idx}"].font = regular_font
            ws_overview[f"B{r_idx}"].border = thin_border
            ws_overview.row_dimensions[r_idx].height = 24

        # Sheet 2: International Studies
        self._populate_studies_sheet("International Studies", self.payload.get("international_studies", []), is_iranian=False)

        # Sheet 3: Iranian Studies
        self._populate_studies_sheet("Iranian Studies", self.payload.get("iranian_studies", []), is_iranian=True)

        # Auto-fit columns across all sheets
        for ws in self.wb.worksheets:
            for col in ws.columns:
                col_letter = get_column_letter(col[0].column)
                max_len = max(len(str(cell.value or '')) for cell in col)
                ws.column_dimensions[col_letter].width = min(max(max_len + 4, 14), 50)

        self.wb.save(output_path)
        print(f"[SUCCESS] Exported Literature Matrix Excel: {output_path}")

    def _populate_studies_sheet(self, sheet_name: str, studies: List[Dict], is_iranian: bool):
        ws = self.wb.create_sheet(title=sheet_name)
        ws.views.sheetView[0].rightToLeft = True

        hdr_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        hdr_font = Font(name="B Titr", size=11, bold=True, color="FFFFFF")
        regular_font = Font(name="B Nazanin", size=10.5)
        thin_border = Border(
            left=Side(style='thin', color='D9D9D9'),
            right=Side(style='thin', color='D9D9D9'),
            top=Side(style='thin', color='D9D9D9'),
            bottom=Side(style='thin', color='D9D9D9')
        )

        headers = ["ردیف", "پژوهشگر(ان)", "سال", "عنوان مقاله/پژوهش", "جامعه و نمونه", "روش و ابزار", "متغیرها", "یافته‌های کلیدی"]
        for c_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=c_idx, value=h)
            cell.fill = hdr_fill
            cell.font = hdr_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
        ws.row_dimensions[1].height = 28

        for r_idx, s in enumerate(studies, start=2):
            vals = [
                r_idx - 1,
                s.get("authors", ""),
                s.get("year", ""),
                s.get("title", ""),
                s.get("sample", ""),
                s.get("methodology", ""),
                s.get("variables", ""),
                s.get("key_findings", "")
            ]
            for c_idx, v in enumerate(vals, start=1):
                cell = ws.cell(row=r_idx, column=c_idx, value=v)
                cell.font = regular_font
                cell.border = thin_border
                align_h = "center" if c_idx in [1, 3] else "right"
                cell.alignment = Alignment(horizontal=align_h, vertical="center", wrap_text=(c_idx in [4, 8]))
            ws.row_dimensions[r_idx].height = 36


# ==============================================================================
# Main CLI Orchestration Entry Point
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Persian Literature Review & Chapter 2 Engine")
    parser.add_argument("--json", required=True, help="Path to structured Chapter 2 payload JSON")
    parser.add_argument("--out-dir", required=True, help="Output directory for generated artifacts")
    parser.add_argument("--lang", default="fa", choices=["fa", "en"], help="Target language (default: fa)")
    args = parser.parse_args()

    if not os.path.exists(args.json):
        print(f"[ERROR] Payload JSON not found at: {args.json}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.out_dir, exist_ok=True)

    with open(args.json, "r", encoding="utf-8") as f:
        payload = json.load(f)

    print("======================================================================")
    print(" PERSIAN LITERATURE REVIEW & CHAPTER 2 ENGINE")
    print(f" Study Title: {payload.get('study_title', '')}")
    print(f" Output Directory: {args.out_dir}")
    print("======================================================================")

    # 1. Compile Word Chapter 2 Document
    docx_filename = "Chapter_2_Literature_Review.docx"
    docx_path = os.path.join(args.out_dir, docx_filename)
    compiler = Chapter2Compiler(payload, lang=args.lang)
    compiler.compile(docx_path)

    # 2. Export Literature Matrix Excel
    xlsx_path = os.path.join(args.out_dir, "empirical_literature_matrix.xlsx")
    excel_gen = ExcelMatrixGenerator(payload)
    excel_gen.generate(xlsx_path)

    # 3. Export Summary JSON
    summary_data = {
        "study_title": payload.get("study_title", ""),
        "study_title_en": payload.get("study_title_en", ""),
        "theoretical_variables_count": len(payload.get("theoretical_sections", [])),
        "international_studies_count": len(payload.get("international_studies", [])),
        "iranian_studies_count": len(payload.get("iranian_studies", [])),
        "total_empirical_studies_reviewed": len(payload.get("international_studies", [])) + len(payload.get("iranian_studies", [])),
        "research_gap_identified": bool(payload.get("research_gap")),
        "conceptual_model_formulated": bool(payload.get("conceptual_model")),
        "artifacts": {
            "chapter2_word": docx_path,
            "literature_matrix_excel": xlsx_path
        }
    }
    summary_path = os.path.join(args.out_dir, "literature_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    print(f"[SUCCESS] Exported Literature Summary: {summary_path}")

    print("\n======================================================================")
    print(" CHAPTER 2 SYNTHESIS COMPLETED SUCCESSFULLY")
    print(f" - Theoretical Foundations: {len(payload.get('theoretical_sections', []))} variables")
    print(f" - International Empirical Studies: {len(payload.get('international_studies', []))} studies")
    print(f" - Iranian Empirical Studies: {len(payload.get('iranian_studies', []))} studies")
    print(f" - Table 2-1: APA 7 Empirical Summary Table Embedded")
    print(f" - Research Gap & Conceptual Model: Fully integrated")
    print("======================================================================")


if __name__ == "__main__":
    main()
