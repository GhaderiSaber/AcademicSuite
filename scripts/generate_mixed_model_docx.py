#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/generate_mixed_model_docx.py — APA 7 Mixed Model DOCX Generator (Phase 27)

Generates Chapter 4 APA 7th Edition Word (.docx) document reporting linear mixed model findings,
along with synchronized Markdown (.md) and JSON (.json) triad deliverables.

Executors: academic-writer ("The Hands")
Prohibited: academic-orchestrator
"""

import os
import sys
import json
import argparse
from typing import Dict, Any
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn


def apply_table_borders(table):
    """Applies strict APA 7th Edition 3-line borders (top, header bottom, table bottom)."""
    tblPr = table._tbl.tblPr
    borders_xml = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'  <w:left w:val="none"/>\n'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'  <w:insideH w:val="none"/>\n'
        f'  <w:insideV w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(borders_xml)


def generate_mixed_model_triad(
    results_json_path: str,
    output_docx_path: str
) -> Dict[str, str]:
    """
    Generates the synchronized triad on disk:
    1. .docx (Word document)
    2. .md (Markdown narrative)
    3. .json (Stats data)
    """
    if not os.path.isfile(results_json_path):
        raise FileNotFoundError(f"Results JSON artifact missing: {results_json_path}")

    with open(results_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    base_path, _ = os.path.splitext(output_docx_path)
    output_md_path = f"{base_path}.md"
    output_json_path = f"{base_path}.json"

    # 1. Generate DOCX
    doc = docx.Document()

    # Title
    p_title = doc.add_paragraph()
    r_title = p_title.add_run("فصل چهارم: یافته‌های پژوهش — مدل‌سازی اثرات آمیخته خطی")
    r_title.bold = True
    r_title.font.name = "B Titr"
    r_title.font.size = Pt(14)
    p_title.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # Introductory Narrative
    p_intro = doc.add_paragraph()
    fit = data.get("fit", {})
    r_intro = p_intro.add_run(
        f"برای آزمون اثرات متغیرهای پیش‌بین بر متغیر وابسته در طول زمان با ساختار داده‌های طولی، "
        f"از مدل خطی اثرات آمیخته (LMM) استفاده شد. حجم نمونه شامل {fit.get('nobs', 0)} مشاهده "
        f"در قالب {fit.get('ngroups', 0)} خوشه/فرد بود (AIC = {fit.get('aic', 0)}, BIC = {fit.get('bic', 0)})."
    )
    r_intro.font.name = "B Nazanin"
    r_intro.font.size = Pt(12)
    p_intro.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Table Title
    p_tbl_title = doc.add_paragraph()
    r_tbl_title = p_tbl_title.add_run("جدول ۱. ضرایب اثرات ثابت و مؤلفه‌های واریانس اثرات تصادفی در مدل LMM")
    r_tbl_title.bold = True
    r_tbl_title.font.name = "B Titr"
    r_tbl_title.font.size = Pt(11)
    p_tbl_title.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # Table
    fixed_effects = data.get("fixed_effects", [])
    table = doc.add_table(rows=1 + len(fixed_effects), cols=5)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    apply_table_borders(table)

    headers = ["پارامتر", "ضریب (B)", "خطای استاندارد (SE)", "آماره t", "سطح معناداری (p)"]
    for col_idx, h in enumerate(headers):
        cell = table.cell(0, col_idx)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.name = "B Titr" if col_idx == 0 else "Times New Roman"
        r.font.size = Pt(10)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    for row_idx, fe in enumerate(fixed_effects, start=1):
        table.cell(row_idx, 0).paragraphs[0].add_run(fe["parameter"])
        table.cell(row_idx, 1).paragraphs[0].add_run(f"{fe['estimate']:.2f}")
        table.cell(row_idx, 2).paragraphs[0].add_run(f"{fe['std_error']:.2f}")
        table.cell(row_idx, 3).paragraphs[0].add_run(f"{fe['statistic']:.2f}")
        p_val_str = "< ۰.۰۰۱" if fe["p_value"] < 0.001 else f"{fe['p_value']:.3f}"
        table.cell(row_idx, 4).paragraphs[0].add_run(p_val_str)

    # Note
    re = data.get("random_effects", {})
    p_note = doc.add_paragraph()
    r_note = p_note.add_run(
        f"یادداشت: همبستگی درون‌طبقه‌ای (ICC) برابر با {re.get('icc', 0):.2f} "
        f"و واریانس بین‌فردی برابر با {re.get('between_group_variance', 0):.2f} است."
    )
    r_note.font.name = "B Nazanin"
    r_note.font.size = Pt(10)

    # Ensure parent dir exists
    docx_dir = os.path.dirname(os.path.abspath(output_docx_path))
    if docx_dir and not os.path.exists(docx_dir):
        os.makedirs(docx_dir, exist_ok=True)

    doc.save(output_docx_path)

    # 2. Generate Markdown narrative
    md_content = (
        f"# فصل چهارم: یافته‌های پژوهش — مدل‌سازی اثرات آمیخته خطی\n\n"
        f"برای آزمون اثرات متغیرهای پیش‌بین در طول زمان، مدل LMM برازش شد (N = {fit.get('nobs')}, "
        f"AIC = {fit.get('aic')}, BIC = {fit.get('bic')}).\n\n"
        f"### جدول ۱. ضرایب اثرات ثابت مدل LMM\n\n"
        f"| پارامتر | B | SE | t | p |\n"
        f"| :--- | :---: | :---: | :---: | :---: |\n"
    )
    for fe in fixed_effects:
        p_str = "< .001" if fe["p_value"] < 0.001 else f"{fe['p_value']:.3f}"
        md_content += f"| {fe['parameter']} | {fe['estimate']:.2f} | {fe['std_error']:.2f} | {fe['statistic']:.2f} | {p_str} |\n"

    md_content += f"\n*یادداشت*: ICC = {re.get('icc'):.2f}, واریانس بین‌فردی = {re.get('between_group_variance'):.2f}.\n"

    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # 3. Synchronize JSON artifact
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return {
        "docx": output_docx_path,
        "md": output_md_path,
        "json": output_json_path
    }


def main():
    parser = argparse.ArgumentParser(description="Generate Mixed Model APA 7 DOCX Triad")
    parser.add_argument("--input", required=True, help="Path to input mixed model results JSON")
    parser.add_argument("--output", required=True, help="Path to output DOCX document")
    args = parser.parse_args()

    paths = generate_mixed_model_triad(args.input, args.output)
    print(f"✅ Generated Triad: DOCX={paths['docx']}, MD={paths['md']}, JSON={paths['json']}")


if __name__ == "__main__":
    main()
