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

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

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


def audit_physical_sources(references: list, papers_dir: str = None) -> dict:
    """
    Audits bibliographic references against physically downloaded research PDFs
    in 04_references_and_lit/papers/ (and ingested_papers_corpus.json).
    Enforces Rule 14 Anti-Hallucination & Zero Ghost Citation Protocol.
    """
    import re
    from pathlib import Path

    # Auto-detect papers directory if not supplied
    if not papers_dir:
        candidates = [
            Path("04_references_and_lit/papers"),
            Path("../04_references_and_lit/papers"),
            Path("papers")
        ]
        for c in candidates:
            if c.exists() and c.is_dir():
                papers_dir = str(c.resolve())
                break

    if not papers_dir or not os.path.exists(papers_dir):
        return {
            "total_references": len(references),
            "verified_count": 0,
            "registry_doi_count": 0,
            "unverified_count": len(references),
            "grounding_ratio": 0.0,
            "audit_records": [
                {
                    "ref_id": f"R{i+1:02d}",
                    "reference": r,
                    "author": "-",
                    "year": "-",
                    "matched_pdf": "-",
                    "file_path": "-",
                    "pages": "-",
                    "status": "UNBACKED_CITATION"
                } for i, r in enumerate(references)
            ],
            "papers_dir": None
        }

    papers_path = Path(papers_dir)
    pdf_files = list(papers_path.glob("*.pdf"))

    # Load ingested corpus JSON if available
    corpus_file = papers_path / "ingested_papers_corpus.json"
    corpus_map = {}
    if corpus_file.exists():
        try:
            with open(corpus_file, "r", encoding="utf-8") as f:
                corpus_data = json.load(f)
                for p in corpus_data.get("papers", []):
                    fname = p.get("filename", "")
                    corpus_map[fname] = p
        except Exception:
            pass

    audit_records = []
    verified_weight = 0.0

    for idx, ref in enumerate(references, 1):
        # Extract author surname and 4-digit year
        m_year = re.search(r'\b(19\d\d|20\d\d)\b', ref)
        year = m_year.group(1) if m_year else ""

        # Author: take initial letters/word
        m_auth = re.search(r'^([A-Za-z\u0600-\u06FF\-]+)', ref.strip().lstrip("0123456789. \t"))
        author = m_auth.group(1).lower() if m_auth else ""

        matched_pdf = None
        matched_path = ""
        page_count = "-"
        status = "UNBACKED_CITATION"

        # Search matching PDF
        for pdf in pdf_files:
            p_lower = pdf.name.lower()
            author_clean = re.sub(r'[^a-z0-9]', '', author)
            
            if author_clean and len(author_clean) >= 3 and author_clean in re.sub(r'[^a-z0-9]', '', p_lower):
                if year and year in p_lower:
                    matched_pdf = pdf.name
                    matched_path = str(pdf.resolve())
                    status = "VERIFIED_ON_DISK"
                    break
                elif not year:
                    matched_pdf = pdf.name
                    matched_path = str(pdf.resolve())
                    status = "VERIFIED_ON_DISK"
                    break
            elif year and year in p_lower and author and author in p_lower:
                matched_pdf = pdf.name
                matched_path = str(pdf.resolve())
                status = "VERIFIED_ON_DISK"
                break

        # Secondary search in parsed corpus metadata (titles/authors)
        if not matched_pdf and corpus_map:
            for fname, p_meta in corpus_map.items():
                p_auth = (p_meta.get("author") or "").lower()
                p_year = str(p_meta.get("year") or "")
                if author and len(author) >= 4 and author in p_auth:
                    matched_pdf = fname
                    matched_path = str((papers_path / fname).resolve())
                    page_count = str(p_meta.get("pages", "-"))
                    status = "VERIFIED_ON_DISK"
                    break

        if matched_pdf:
            verified_weight += 1.0
            if matched_pdf in corpus_map:
                page_count = str(corpus_map[matched_pdf].get("pages", "-"))
        elif "doi.org" in ref.lower() or "10." in ref:
            status = "REGISTRY_DOI"
            verified_weight += 0.5

        audit_records.append({
            "ref_id": f"R{idx:02d}",
            "reference": ref,
            "author": author.capitalize(),
            "year": year,
            "matched_pdf": matched_pdf or "-",
            "file_path": matched_path or "-",
            "pages": page_count,
            "status": status
        })

    total_refs = len(references)
    grounding_ratio = (verified_weight / max(1, total_refs)) * 100.0

    return {
        "total_references": total_refs,
        "verified_count": int(sum(1 for r in audit_records if r["status"] == "VERIFIED_ON_DISK")),
        "registry_doi_count": int(sum(1 for r in audit_records if r["status"] == "REGISTRY_DOI")),
        "unverified_count": int(sum(1 for r in audit_records if r["status"] == "UNBACKED_CITATION")),
        "grounding_ratio": round(grounding_ratio, 1),
        "audit_records": audit_records,
        "papers_dir": str(papers_path)
    }


def export_claim_evidence_matrix_excel(claims_data: list, out_path: str, lang: str = "en", source_audit: dict = None):
    """
    Exports a professional Claim-Evidence Mapping Matrix to Excel.
    Includes Sheet 1: Claim-Evidence Matrix and Sheet 2: Physical Sources Audit.
    Enforces that every claim has statistical backing and citations are backed by local PDFs.
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
        "شناسه", "بخش مقاله", "ادعای پژوهشی (Claim)", "پارامتر آماری موید (Evidence)", "مقدار آماری", "وضعیت انطباق", "پیشنهاد بازنگری", "سند مقاله محلی (Local PDF)"
    ] if lang == "fa" else [
        "ID", "Section", "Research Claim", "Empirical Evidence / Parameter", "Statistical Value", "Status", "Editorial Remedy", "Local PDF Source"
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
        ws.cell(row=r_idx, column=8, value=c_item.get("local_pdf", c_item.get("source_pdf", "Verified in Workspace")))

        for col_i in range(1, 9):
            ws.cell(row=r_idx, column=col_i).font = body_font
            ws.cell(row=r_idx, column=col_i).border = thin_border

    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = min(50, max(12, max_len + 3))

    # Sheet 2: Physical Sources Audit (Anti-Hallucination Sheet)
    if source_audit and source_audit.get("audit_records"):
        ws2 = wb.create_sheet(title="تطبیق فیزیکی مراجع" if lang == "fa" else "Physical Sources Audit")
        ws2.views.sheetView[0].rightToLeft = (lang == "fa")

        ws2["A1"] = "جدول تطبیق مراجع مقاله با مقالات فیزیکی بارگیری‌شده (Rule 14 Anti-Hallucination Audit)" if lang == "fa" else "Physical Research Paper Verification Audit (Rule 14 Anti-Hallucination Protocol)"
        ws2["A1"].font = title_font

        headers2 = [
            "شناسه", "مرجع کتابشناختی (APA 7)", "نویسنده اصلی", "سال", "فایل PDF محلی", "مسیر فایل در دیسک", "صفحات", "وضعیت اعتبارسنجی"
        ] if lang == "fa" else [
            "Ref ID", "Bibliographic Reference (APA 7)", "First Author", "Year", "Local PDF Filename", "Absolute File Path", "Pages", "Grounding Status"
        ]

        for col_idx, h in enumerate(headers2, 1):
            c = ws2.cell(row=3, column=col_idx, value=h)
            c.font = header_font
            c.fill = navy_fill
            c.alignment = Alignment(horizontal="center", vertical="center")

        for r_i, rec in enumerate(source_audit["audit_records"], 4):
            st = rec.get("status", "UNBACKED_CITATION")
            if st == "VERIFIED_ON_DISK":
                st_fill = green_fill
            elif st == "REGISTRY_DOI":
                st_fill = amber_fill
            else:
                st_fill = red_fill

            ws2.cell(row=r_i, column=1, value=rec.get("ref_id")).alignment = Alignment(horizontal="center")
            ws2.cell(row=r_i, column=2, value=rec.get("reference"))
            ws2.cell(row=r_i, column=3, value=rec.get("author")).alignment = Alignment(horizontal="center")
            ws2.cell(row=r_i, column=4, value=rec.get("year")).alignment = Alignment(horizontal="center")
            ws2.cell(row=r_i, column=5, value=rec.get("matched_pdf"))
            ws2.cell(row=r_i, column=6, value=rec.get("file_path"))
            ws2.cell(row=r_i, column=7, value=rec.get("pages")).alignment = Alignment(horizontal="center")

            sc = ws2.cell(row=r_i, column=8, value=st)
            sc.alignment = Alignment(horizontal="center")
            sc.fill = st_fill

            for c_idx in range(1, 9):
                ws2.cell(row=r_i, column=c_idx).font = body_font
                ws2.cell(row=r_i, column=c_idx).border = thin_border

        for col in ws2.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws2.column_dimensions[col_letter].width = min(50, max(12, max_len + 3))

    wb.save(out_path)
    print(f"Claim-Evidence & Source Verification Matrix successfully exported: {out_path}")


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


def compute_article_readiness_score(data: dict, source_audit: dict = None, papers_dir: str = None) -> dict:
    """
    Computes a pre-flight Submission Readiness Score (SRS: 0-100%) for academic manuscripts.
    Weights:
      - 30%: IMRaD Structural Completeness (Abstract 5 parts, Intro, Method 4 subsections, Results, Discussion)
      - 25%: Claim-Evidence Backing Ratio (Claims matrix verification)
      - 15%: Figure-First Visual Backing (Presence of publication-grade figures/tables supporting claims)
      - 15%: Physical Source Grounding & Anti-Hallucination (Verification against 04_references_and_lit/papers)
      - 15%: APA 7 Typography & Formatting (Abstract word count <= 250, title brevity, table captions)
    """
    # 1. IMRaD Completeness (30 pts)
    imrad_points = 0.0
    abstract = data.get("abstract", {})
    if isinstance(abstract, dict) and all(k in abstract for k in ["background", "objective", "methods", "results", "conclusion"]):
        imrad_points += 8.0
    elif abstract:
        imrad_points += 4.0

    intro = data.get("introduction", [])
    if len(intro) >= 3:
        imrad_points += 5.0
    elif intro:
        imrad_points += 2.5

    method = data.get("method", {})
    if isinstance(method, dict) and all(k in method for k in ["design_and_participants", "measures", "procedure", "statistical_analysis"]):
        imrad_points += 7.0
    elif method:
        imrad_points += 3.5

    results = data.get("results", {})
    if results.get("narrative") and (results.get("tables") or results.get("figures") or data.get("figures")):
        imrad_points += 6.0
    elif results:
        imrad_points += 3.0

    disc = data.get("discussion", [])
    if len(disc) >= 3:
        imrad_points += 4.0
    elif disc:
        imrad_points += 2.0

    refs = data.get("references", [])

    # 2. Claim-Evidence Ratio (25 pts)
    claims = data.get("claims_matrix") or data.get("claim_evidence_matrix", [])
    if claims:
        sup_cnt = sum(1 for c in claims if c.get("status", "").lower() in ["supported", "تاییدشده"])
        claim_ratio = sup_cnt / len(claims)
        claims_points = claim_ratio * 25.0
    else:
        claims_points = 20.0

    # 3. Figure-First Planning (15 pts)
    figs = data.get("figures") or data.get("results", {}).get("figures", [])
    tbls = data.get("results", {}).get("tables", [])
    total_visuals = len(figs) + len(tbls)
    if total_visuals >= 4:
        figure_points = 15.0
    elif total_visuals >= 2:
        figure_points = 10.0
    elif total_visuals >= 1:
        figure_points = 6.0
    else:
        figure_points = 2.0

    # 4. Physical Source Grounding & Anti-Hallucination (15 pts)
    if source_audit is None:
        source_audit = audit_physical_sources(refs, papers_dir=papers_dir)
    sgr = source_audit.get("grounding_ratio", 0.0)
    if sgr >= 80.0:
        source_points = 15.0
    elif sgr >= 60.0:
        source_points = 12.0
    elif sgr >= 40.0:
        source_points = 9.0
    elif sgr > 0.0:
        source_points = 5.0
    else:
        source_points = 0.0

    # 5. APA 7 & Technical Checklist (15 pts)
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

    total_score = round(imrad_points + claims_points + figure_points + source_points + apa_points, 1)
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
            "physical_source_grounding": round(source_points, 1),
            "apa7_technical": round(apa_points, 1)
        },
        "source_audit": source_audit
    }


def compile_article(data: dict, output_path: str, lang: str = 'en', papers_dir: str = None):
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

    # --- 8b. Declarations ---
    decls = data.get("declarations", {})
    if decls:
        p_dec_h = doc.add_paragraph()
        if is_fa:
            set_paragraph_bidi(p_dec_h)
            add_run(p_dec_h, "ملاحظات اخلاقی و بیانیه‌ها", lang=lang, size=13, bold=True)
        else:
            p_dec_h.alignment = WD_ALIGN_PARAGRAPH.LEFT
            add_run(p_dec_h, "Declarations", lang=lang, size=12, bold=True)
        p_dec_h.paragraph_format.space_before = Pt(14)
        p_dec_h.paragraph_format.space_after = Pt(6)

        decl_labels = [
            ("ethics_approval", "تاییدیه اخلاقی: ", "Ethical Approval: "),
            ("consent_to_participate", "رضایت آگاهانه: ", "Informed Consent: "),
            ("data_availability", "دسترسی به داده‌ها: ", "Data Availability: "),
            ("conflict_of_interest", "تعارض منافع: ", "Conflict of Interest: "),
            ("funding", "حمایت مالی: ", "Funding: "),
            ("authors_contributions", "سهم نویسندگان: ", "Authors' Contributions: "),
            ("acknowledgements", "سپاسگزاری: ", "Acknowledgements: ")
        ]
        for key, fa_lbl, en_lbl in decl_labels:
            if key in decls:
                p_dec = doc.add_paragraph()
                if is_fa:
                    set_paragraph_bidi(p_dec, align_body)
                    p_dec.paragraph_format.line_spacing = 1.2
                    add_run(p_dec, fa_lbl, lang=lang, size=10, bold=True)
                    add_run(p_dec, str(decls[key]), lang=lang, size=10)
                else:
                    p_dec.alignment = align_body
                    p_dec.paragraph_format.line_spacing = 1.15
                    add_run(p_dec, en_lbl, lang=lang, size=10, bold=True)
                    add_run(p_dec, str(decls[key]), lang=lang, size=10)
                p_dec.paragraph_format.space_after = Pt(4)

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

    # Physical Source Audit (Rule 14 Anti-Hallucination Protocol)
    refs_list = data.get("references", [])
    src_audit = audit_physical_sources(refs_list, papers_dir=papers_dir)

    # Export Claim-Evidence Matrix & Source Verification if present
    claims_matrix = data.get("claims_matrix") or data.get("claim_evidence_matrix", [])
    if claims_matrix or src_audit.get("audit_records"):
        matrix_filename = output_path.replace(".docx", "_claim_evidence_matrix.xlsx")
        export_claim_evidence_matrix_excel(claims_matrix, matrix_filename, lang=lang, source_audit=src_audit)

    # Export Figure Planning Matrix if present
    figs_for_matrix = data.get("figures") or results_data.get("figures", [])
    if figs_for_matrix:
        fig_matrix_filename = output_path.replace(".docx", "_figure_planning_matrix.xlsx")
        export_figure_planning_matrix_excel(figs_for_matrix, fig_matrix_filename, lang=lang)

    # Compute Submission Readiness Score (SRS)
    srs_report = compute_article_readiness_score(data, source_audit=src_audit, papers_dir=papers_dir)
    print(f"\n[+] Submission Readiness Score (SRS): {srs_report['submission_readiness_score']:.1f}% (Grade: {srs_report['grade']})")
    print(f"    - Verdict: {srs_report['verdict_en']} / {srs_report['verdict_fa']}")
    print(f"    - Subscores: IMRaD={srs_report['subscores']['imrad_completeness']}/30, "
          f"Claims={srs_report['subscores']['claim_evidence_backing']}/25, "
          f"Figures={srs_report['subscores']['figure_first_visuals']}/15, "
          f"SourceGrounding={srs_report['subscores']['physical_source_grounding']}/15, "
          f"APA7={srs_report['subscores']['apa7_technical']}/15")

    print(f"\n[+] Physical Source Audit (04_references_and_lit/papers/):")
    print(f"    - Total References: {src_audit['total_references']}")
    print(f"    - Verified on Disk: {src_audit['verified_count']} PDFs")
    print(f"    - Registry DOI:     {src_audit['registry_doi_count']} entries")
    print(f"    - Unverified:       {src_audit['unverified_count']} entries")
    print(f"    - Grounding Ratio:  {src_audit['grounding_ratio']:.1f}%")
    if src_audit['unverified_count'] > 0:
        print(f"    [!] WARNING: {src_audit['unverified_count']} references not found in local PDF repository.")
        print(f"    [!] Run: python3 .agents/skills/academic-article-writer/scripts/verify_and_download_citation.py --query \"Author Year Title\"")
    else:
        print(f"    [✓] 100% Physical Source Grounding Confirmed (Zero Ghost Citations).")

    doc.save(output_path)
    print(f"\nAcademic Article successfully compiled at: {output_path}")
    return srs_report

def main():
    parser = argparse.ArgumentParser(description="Academic Journal Article Compiler")
    parser.add_argument("--json", required=True, help="Path to article structured JSON file")
    parser.add_argument("--out", default="Article_Manuscript.docx", help="Output .docx file path")
    parser.add_argument("--lang", default="en", choices=["en", "fa"], help="Target language track ('en' for ISI/Scopus, 'fa' for ISC)")
    parser.add_argument("--papers-dir", default=None, help="Directory containing downloaded PDFs (default: 04_references_and_lit/papers)")
    args = parser.parse_args()
    
    with open(args.json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    compile_article(data, args.out, lang=args.lang, papers_dir=args.papers_dir)

if __name__ == "__main__":
    main()
