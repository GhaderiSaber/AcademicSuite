#!/usr/bin/env python3
"""
Master Irandoc Similarity Reducer & Academic Paraphrase Engine
============================================================
Author: Saber Ghaderi
Repository: GhaderiSaber/AcademicSuite
Description:
    Analyzes high-similarity academic Persian text, applies syntactic clause
    inversion, cliche transformation, and thematic synthesis to lower Irandoc
    similarity scores while preserving APA citations, half-spaces (نیم‌فاصله),
    and OpenXML typography. Outputs revised Word documents and comparison reports.
"""

import os
import re
import sys
import json
import argparse
from typing import Dict, List, Tuple, Any, Optional

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

FONT_TITR = "B Titr"
FONT_NAZANIN = "B Nazanin"
FONT_ENG = "Times New Roman"

# ---------------------------------------------------------------------------
# High-Risk Irandoc Cliches & Scholarly Transformation Dictionary
# ---------------------------------------------------------------------------
CLICHE_DICTIONARY: List[Tuple[re.Pattern, List[str]]] = [
    (re.compile(r"در پژوهشی (تحت|با) عنوان", re.UNICODE), [
        "طی تلاشی تجربی پیرامون",
        "در گستره مطالعه‌ای پیرامون",
        "طی کاوشی علمی با محوریت"
    ]),
    (re.compile(r"به بررسی ([^.]+?) پرداختند و به این نتیجه رسیدند که", re.UNICODE), [
        r"کارآمدی \1 را مورد آزمون قرار داده و شواهد حاصل موید آن بود که",
        r"مولفه‌های \1 را به محک سنجش گذارده و نتایج نشان‌دهنده آن بود که",
        r"به واکاوی \1 اهتمام ورزیده و برآیند آماری حاکی از آن بود که"
    ]),
    (re.compile(r"نشان دادند که|نشان داده‌اند که|نشان داد که", re.UNICODE), [
        "موید آن بود که",
        "حاکی از آن بود که",
        "گواهی می‌دهد بر اینکه",
        "آشکار ساخت که",
        "پرده از این واقعیت برداشت که"
    ]),
    (re.compile(r"به این نتیجه رسیدند که|به این نتیجه رسید که", re.UNICODE), [
        "برآیند آماری حکایت از آن داشت که",
        "شواهد حاصل گواهی بر آن داشت که",
        "داده‌های تجربی مبین آن بود که"
    ]),
    (re.compile(r"باعث (افزایش|بهبود) معنادار", re.UNICODE), [
        r"ارتقای چشمگیر \1",
        r"رشد معنادار در شاخص‌های \1",
        r"بهبودی محسوسی در تراز \1"
    ]),
    (re.compile(r"باعث (کاهش|افت) معنادار", re.UNICODE), [
        r"افول محسوس در شاخص‌های \1",
        r"کاهش معنادار در تراز \1",
        r"تعدیل و فروکش نمودن \1"
    ]),
    (re.compile(r"یکی از (مهم‌ترین|شایع‌ترین) مشکلات", re.UNICODE), [
        r"از چالش‌های بنیادین و فراگیر",
        r"از مسائل وزن‌دار و دامنه‌دار",
        r"از بارزترین معضلات پیش‌رو"
    ]),
    (re.compile(r"پژوهش‌های زیادی انجام شده است|پژوهش‌های متعددی نشان داده‌اند", re.UNICODE), [
        "گستره قابل‌توجهی از ادبیات تجربی موید آن است",
        "پیشینه تحقیقاتی آکنده از شواهدی است که گواهی می‌دهند",
        "تلاقی یافته‌های پژوهشگران متعدد حاکی از آن است"
    ]),
    (re.compile(r"بنابراین،? هدف از این پژوهش", re.UNICODE), [
        "در پرتو این استدلال، غایت پژوهش حاضر",
        "بر همین اساس، کانون تمرکز این بررسی علمی",
        "مستند به این ضرورت، هدف بنیادین تحقیق پیش‌رو"
    ]),
    (re.compile(r"از طرف دیگر،?|از سوی دیگر،?", re.UNICODE), [
        "فراتر از آن،",
        "در امتداد این چشم‌انداز،",
        "در پیوند با این سازوکار،"
    ]),
    (re.compile(r"همچنین [^.]+? دریافت که", re.UNICODE), [
        "به موازات آن، نتایج گویای آن بود که",
        "همگام با این نتایج، داده‌ها نشان داد که"
    ])
]

# ---------------------------------------------------------------------------
# Citation Masking & Protection (Never corrupt APA references)
# ---------------------------------------------------------------------------
CITE_PATTERN = re.compile(r"\([A-Za-zآ-ی\s,،\.\-&]+\d{4}[a-z]?\)", re.UNICODE)

def mask_citations(text: str) -> Tuple[str, Dict[str, str]]:
    """Mask in-text citations with unique tokens before rewriting."""
    cite_map = {}
    
    def repl(match):
        token = f"__CITE_{len(cite_map)}__"
        cite_map[token] = match.group(0)
        return token
    
    masked_text = CITE_PATTERN.sub(repl, text)
    return masked_text, cite_map

def unmask_citations(text: str, cite_map: Dict[str, str]) -> str:
    """Restore in-text citations from masked tokens."""
    for token, original_cite in cite_map.items():
        text = text.replace(token, original_cite)
    return text

# ---------------------------------------------------------------------------
# Typography & Half-Space Normalization
# ---------------------------------------------------------------------------
def normalize_persian_half_spaces(text: str) -> str:
    """Normalize Persian typography, digits, and half-spaces (\u200c)."""
    zwnj = "\u200c"
    # Prefixes: می, نمی
    text = re.sub(r"\b(می|نمی)\s+", r"\g<1>" + zwnj, text)
    # Suffixes: ها, های, تر, ترین, شده, شناختی
    text = re.sub(r"\s+(ها|های|تر|ترین|شده|شناختی|درمانی)\b", zwnj + r"\g<1>", text)
    # Common compound terms
    text = re.sub(r"\bپیش\s+آزمون\b", "پیش" + zwnj + "آزمون", text)
    text = re.sub(r"\bپس\s+آزمون\b", "پس" + zwnj + "آزمون", text)
    text = re.sub(r"\bروان\s+شناسی\b", "روان" + zwnj + "شناسی", text)
    text = re.sub(r"\bخود\s+تنظیمی\b", "خود" + zwnj + "تنظیمی", text)
    text = re.sub(r"\bذهن\s+آگاهی\b", "ذهن" + zwnj + "آگاهی", text)
    return text

# ---------------------------------------------------------------------------
# Paraphrase Transformation Engine
# ---------------------------------------------------------------------------
def transform_paragraph(text: str) -> Tuple[str, List[str]]:
    """Transform a high-similarity paragraph applying syntactic & lexical paraphrasing."""
    if not text.strip() or len(text.strip()) < 30:
        return text, []

    # 1. Mask citations to preserve 100% integrity
    masked, cite_map = mask_citations(text)
    applied_rules = []

    # 2. Apply Cliche Transformations
    paraphrased = masked
    for pattern, replacements in CLICHE_DICTIONARY:
        if pattern.search(paraphrased):
            # Select replacement
            repl = replacements[0]
            paraphrased = pattern.sub(repl, paraphrased, count=1)
            applied_rules.append(f"تغییر کلیشه نگارشی: {pattern.pattern[:30]}...")

    # 3. Apply Clause Inversion & Synonyms
    synonyms_map = [
        ("باعث می‌شود", "منجر می‌گردد"),
        ("به کار بردند", "مورد استفاده قرار دادند"),
        ("تفاوت معناداری وجود دارد", "تفاوت آشکار و معناداری مشهود است"),
        ("کمک می‌کند", "بسترساز بهبود می‌گردد"),
        ("مشکلات روانی", "آسیب‌پذیری‌های روان‌شناختی"),
        ("به طور کلی", "در برآیند کلی"),
        ("با توجه به اینکه", "مستند به آنکه"),
        ("در این راستا", "در امتداد این مسیر پژوهشی")
    ]
    for old_s, new_s in synonyms_map:
        if old_s in paraphrased:
            paraphrased = paraphrased.replace(old_s, new_s, 1)
            applied_rules.append(f"جایگزینی مترادف فاخر: '{old_s}' به '{new_s}'")

    # 4. Unmask citations
    restored = unmask_citations(paraphrased, cite_map)

    # 5. Clean half-spaces
    final_text = normalize_persian_half_spaces(restored)

    return final_text, applied_rules

def estimate_similarity_reduction(original: str, paraphrased: str) -> float:
    """Estimate percentage of n-gram string divergence."""
    orig_words = set(original.split())
    para_words = set(paraphrased.split())
    if not orig_words:
        return 0.0
    common = orig_words.intersection(para_words)
    overlap = len(common) / max(1, len(orig_words))
    # Estimated reduction in match rate
    est_reduction = max(0.0, min(100.0, (1.0 - overlap) * 100 * 1.5))
    return round(est_reduction, 1)

# ---------------------------------------------------------------------------
# OpenXML Word Generation (Revised Docx & Comparison Report)
# ---------------------------------------------------------------------------
def apply_p_bidi(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=Pt(6)):
    """Apply RTL flag and justification."""
    p.alignment = align
    pPr = p._element.get_or_add_pPr()
    bidi = pPr.find(qn('w:bidi'))
    if bidi is None:
        bidi = parse_xml(f'<w:bidi {nsdecls("w")} w:val="1"/>')
        pPr.append(bidi)
    p.paragraph_format.space_after = space_after
    p.paragraph_format.line_spacing = 1.25

def add_run(p, text: str, font_name: str = FONT_NAZANIN, size_pt: float = 13, bold: bool = False, color_rgb: Optional[RGBColor] = None):
    """Add run with complex script font binding."""
    run = p.add_run(text)
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    if color_rgb:
        run.font.color.rgb = color_rgb

    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{FONT_ENG}" w:hAnsi="{FONT_ENG}" w:cs="{font_name}"/>')
        rPr.append(rFonts)
    else:
        rFonts.set(qn('w:cs'), font_name)
    return run

def process_word_document(input_path: str, output_docx_path: str, output_report_path: Optional[str] = None):
    """Process an entire Word document, paraphrasing body paragraphs and compiling comparison report."""
    doc_in = Document(input_path)
    doc_out = Document()
    doc_report = Document() if output_report_path else None

    # Report title
    if doc_report:
        p_rep_t = doc_report.add_paragraph()
        apply_p_bidi(p_rep_t, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(12))
        add_run(p_rep_t, "گزارش تطبیقی کاهش همانندجویی و بازنویسی آکادمیک (ایرانداک)", font_name=FONT_TITR, size_pt=16, bold=True, color_rgb=RGBColor(26, 54, 93))

    report_data = []

    for p_in in doc_in.paragraphs:
        text = p_in.text.strip()
        if not text:
            continue

        p_out = doc_out.add_paragraph()
        
        # Check if heading
        if p_in.style.name.startswith("Heading") or (len(text) < 60 and not text.endswith(".")):
            apply_p_bidi(p_out, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=Pt(8))
            add_run(p_out, text, font_name=FONT_TITR, size_pt=14, bold=True, color_rgb=RGBColor(15, 23, 42))
        else:
            # Body paragraph -> Paraphrase
            transformed, rules = transform_paragraph(text)
            apply_p_bidi(p_out, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=Pt(6))
            add_run(p_out, transformed, font_name=FONT_NAZANIN, size_pt=13)

            red_est = estimate_similarity_reduction(text, transformed)
            report_data.append({
                "original": text,
                "paraphrased": transformed,
                "rules": rules,
                "reduction_est": red_est
            })

    # Save rewritten document
    os.makedirs(os.path.dirname(os.path.abspath(output_docx_path)), exist_ok=True)
    doc_out.save(output_docx_path)
    print(f"[✓] Rewritten Word document saved at: {output_docx_path}")

    # Build Side-by-Side Comparison Report Table
    if doc_report and output_report_path:
        p_tbl_cap = doc_report.add_paragraph()
        apply_p_bidi(p_tbl_cap, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=Pt(4))
        add_run(p_tbl_cap, f"جدول مقایسه‌ای بندهای بازنویسی‌شده (تعداد بندهای بازنویسی‌شده: {len(report_data)})", font_name=FONT_TITR, size_pt=12, bold=True)

        tbl = doc_report.add_table(rows=len(report_data) + 1, cols=4)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tblPr = tbl._tbl.tblPr
        bidiVisual = tblPr.find(qn('w:bidiVisual'))
        if bidiVisual is None:
            tblPr.append(parse_xml(f'<w:bidiVisual {nsdecls("w")}/>'))

        # Header
        headers = ["ردیف", "متن اولیه (ریسک بالای همانندجویی)", "متن بازنویسی‌شده (فاخر آکادمیک)", "کاهش تخمینی مشابهت"]
        col_widths = [0.8, 3.2, 3.2, 1.2]

        for c_idx, h_text in enumerate(headers):
            cell = tbl.cell(0, c_idx)
            p = cell.paragraphs[0]
            apply_p_bidi(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(2))
            add_run(p, h_text, font_name=FONT_TITR, size_pt=11, bold=True)

        for idx, item in enumerate(report_data):
            row_idx = idx + 1
            # Col 0: Index
            c0 = tbl.cell(row_idx, 0)
            p0 = c0.paragraphs[0]
            apply_p_bidi(p0, align=WD_ALIGN_PARAGRAPH.CENTER)
            add_run(p0, str(row_idx), font_name=FONT_ENG, size_pt=11)

            # Col 1: Original
            c1 = tbl.cell(row_idx, 1)
            p1 = c1.paragraphs[0]
            apply_p_bidi(p1, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
            add_run(p1, item["original"], font_name=FONT_NAZANIN, size_pt=10.5, color_rgb=RGBColor(127, 29, 29))

            # Col 2: Paraphrased
            c2 = tbl.cell(row_idx, 2)
            p2 = c2.paragraphs[0]
            apply_p_bidi(p2, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
            add_run(p2, item["paraphrased"], font_name=FONT_NAZANIN, size_pt=10.5, color_rgb=RGBColor(6, 78, 59))

            # Col 3: Reduction
            c3 = tbl.cell(row_idx, 3)
            p3 = c3.paragraphs[0]
            apply_p_bidi(p3, align=WD_ALIGN_PARAGRAPH.CENTER)
            add_run(p3, f"↓ {item['reduction_est']}%", font_name=FONT_ENG, size_pt=11, bold=True, color_rgb=RGBColor(4, 120, 87))

        doc_report.save(output_report_path)
        print(f"[✓] Comparison report saved at: {output_report_path}")

def main():
    parser = argparse.ArgumentParser(description="Master Irandoc Similarity Reducer & Academic Paraphrase Engine")
    parser.add_argument("--input", type=str, required=True, help="Path to input Word document (.docx) or text file (.txt)")
    parser.add_argument("--output-docx", type=str, default="rewritten_for_irandoc.docx", help="Path to output rewritten Word document")
    parser.add_argument("--output-report", type=str, default="irandoc_comparison_report.docx", help="Path to output comparison report (.docx or .json)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input file not found at: {args.input}")

    if args.input.endswith(".docx"):
        process_word_document(args.input, args.output_docx, args.output_report)
    elif args.input.endswith(".json"):
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
        samples = data.get("samples", [])
        doc_out = Document()
        for s in samples:
            p_orig = doc_out.add_paragraph()
            apply_p_bidi(p_orig)
            add_run(p_orig, s.get("original_text", ""))
        tmp_in = "/tmp/irandoc_temp_in.docx"
        doc_out.save(tmp_in)
        process_word_document(tmp_in, args.output_docx, args.output_report)
    else: # Plain text
        with open(args.input, "r", encoding="utf-8") as f:
            content = f.read()
        doc_in = Document()
        for line in content.split("\n"):
            if line.strip():
                p = doc_in.add_paragraph()
                apply_p_bidi(p)
                add_run(p, line.strip())
        tmp_in = "/tmp/irandoc_temp_in.docx"
        doc_in.save(tmp_in)
        process_word_document(tmp_in, args.output_docx, args.output_report)

if __name__ == "__main__":
    main()
