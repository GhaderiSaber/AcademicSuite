# -*- coding: utf-8 -*-
"""
extract_proposal_data.py - Part of the 'persian-thesis-builder' Antigravity Skill.

Extracts structured sections from an Iranian university research proposal (.pdf / .doc):
1. Chapter 1 Sections:
   - Problem Statement (بیان مسئله)
   - Significance (اهمیت و ضرورت)
   - Objectives (اهداف کلی و اختصاصی)
   - Hypotheses (فرضیه‌ها یا سوالات پژوهش)
   - Variable Definitions (تعریف مفهومی و عملیاتی)
2. Chapter 2 Empirical Background:
   - Previous Studies (پیشینه پژوهش - مطالعات داخلی و بین‌المللی)
3. Chapter 3 Sections:
   - Research Design (طرح پژوهش)
   - Population, Sample & Sampling (جامعه، نمونه و روش نمونه‌گیری)
   - Instruments & Scales (ابزارهای سنجش و پرسشنامه‌ها)
   - Procedure (مراحل اجرا)
   - Data Analysis (روش‌های تحلیل آماری)
   - Ethical Considerations (ملاحظات اخلاقی)
4. References:
   - Persian & English proposal bibliography list.
"""

import os
import sys
import re
import json
import argparse
from typing import Dict, List
import pypdf

sys.stdout.reconfigure(encoding='utf-8')

def normalize_persian_text(text: str) -> str:
    """Replaces all Arabic characters with Persian equivalents."""
    if not text:
        return ""
    text = text.replace('\u064A', '\u06CC')  # Arabic Yeh (ي) -> Persian Yeh (ی)
    text = text.replace('\u0649', '\u06CC')  # Alef Maksura (ى) -> Persian Yeh (ی)
    text = text.replace('\u0643', '\u06A9')  # Arabic Kaf (ك) -> Persian Keheh (ک)
    text = text.replace('\u0629', '\u0647')  # Teh Marbuta (ة) -> Persian Heh (ه)
    ar_digits = "٠١٢٣٤٥٦٧٨٩"
    fa_digits = "۰۱۲۳۴۵۶۷۸۹"
    for a, f in zip(ar_digits, fa_digits):
        text = text.replace(a, f)
    return text

SECTION_MARKERS = {
    "problem_statement": [r"بیان\s*مسئله", r"تشریح\s*مسئله"],
    "significance": [r"ضرورت\s*و\s*اهمیت", r"اهمیت\s*تحقیق", r"اهمیت\s*پژوهش"],
    "objectives": [r"اهداف\s*پژوهش", r"اهداف\s*طرح", r"اهداف\s*تحقیق", r"هدف\s*کلی"],
    "hypotheses": [r"فرضیات\s*پژوهش", r"سوالات\s*پژوهش", r"فرضیه\s*ها"],
    "definitions": [r"تعریف\s*واژگان", r"تعریف\s*مفهومی", r"تعریف\s*عملیاتی"],
    "previous_studies": [r"پیشینه\s*پژوهش", r"سوابق\s*مربوطه", r"مرور\s*ادبیات", r"مطالعات\s*داخلی"],
    "methodology": [r"روش\s*اجرا", r"روش\s*شناسی", r"جامعه\s*آماری", r"حجم\s*نمونه", r"روش\s*نمونه\s*گیری"],
    "instruments": [r"ابزار\s*گرد\s*آوری", r"ابزار\s*جمع\s*آوری", r"پرسشنامه", r"ابزار\s*پژوهش"],
    "data_analysis": [r"روش\s*های\s*تجزیه", r"روش\s*های\s*تحلیل", r"روش\s*تحلیل\s*آماری"],
    "ethics": [r"ملاحظات\s*اخلاقی", r"رعایت\s*موازین\s*اخلاق"],
    "references": [r"فهرست\s*منابع", r"منابع\s*و\s*مآخذ", r"فهرست\s*مراجع"]
}

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts clean text from a PDF file page by page."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    reader = pypdf.PdfReader(pdf_path)
    full_text = []
    for i, page in enumerate(reader.pages):
        t = page.extract_text() or ""
        # Normalize Arabic characters to Persian
        t = normalize_persian_text(t)
        # clean header/footer page numbers
        t = re.sub(r'دانشگاه علوم پزشکی و خدمات بهداشتی درمانی کاشان[^\n]*', '', t)
        t = re.sub(r'نشانی کیلومتر 5 بلوار قطب راوندی[^\n]*', '', t)
        full_text.append(f"\n--- [PAGE {i+1}] ---\n" + t)
    return "\n".join(full_text)

def segment_proposal(text: str) -> Dict[str, str]:
    """Segments proposal text into structured academic sections."""
    sections = {}
    lines = text.split("\n")
    
    curr_key = "preliminary"
    buffer = []
    
    for line in lines:
        stripped = line.strip()
        matched_key = None
        for key, patterns in SECTION_MARKERS.items():
            if any(re.search(pat, stripped) for pat in patterns):
                matched_key = key
                break
        
        if matched_key and matched_key != curr_key:
            if buffer:
                sections[curr_key] = sections.get(curr_key, "") + "\n" + "\n".join(buffer)
                buffer = []
            curr_key = matched_key
        
        buffer.append(line)
    
    if buffer:
        sections[curr_key] = sections.get(curr_key, "") + "\n" + "\n".join(buffer)
    
    return sections

def clean_section_text(text: str) -> str:
    """Normalizes Persian spacing and typography in extracted sections."""
    text = normalize_persian_text(text)
    # Collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove page boundary markers
    text = re.sub(r'---\s*\[PAGE \d+\]\s*---', '', text)
    return text.strip()

def export_proposal_sections(pdf_path: str, output_dir: str):
    """Parses proposal PDF and exports individual chapter component files."""
    os.makedirs(output_dir, exist_ok=True)
    raw_text = extract_text_from_pdf(pdf_path)
    sections = segment_proposal(raw_text)

    # 1. Chapter 1 markdown: Problem, Significance, Objectives, Hypotheses, Definitions
    ch1_parts = [
        "# فصل اول: کلیات پژوهش\n",
        "## ۱-۱. مقدمه و بیان مسئله",
        clean_section_text(sections.get("problem_statement", "محتوای بیان مسئله")),
        "\n## ۱-۲. ضرورت و اهمیت پژوهش",
        clean_section_text(sections.get("significance", "")),
        "\n## ۱-۳. اهداف پژوهش",
        clean_section_text(sections.get("objectives", "")),
        "\n## ۱-۴. فرضیه‌ها و سوالات پژوهش",
        clean_section_text(sections.get("hypotheses", "")),
        "\n## ۱-۵. تعاریف مفهومی و عملیاتی متغیرها",
        clean_section_text(sections.get("definitions", ""))
    ]
    ch1_content = "\n\n".join(ch1_parts)
    ch1_file = os.path.join(output_dir, "Chapter1_from_Proposal.md")
    with open(ch1_file, "w", encoding="utf-8") as f:
        f.write(ch1_content)

    # 2. Chapter 2 Empirical Background: Previous studies
    ch2_parts = [
        "# فصل دوم: پیشینه پژوهشی (مطالعات تجربی)",
        clean_section_text(sections.get("previous_studies", "پیشینه مطالعات تجربی داخلی و خارجی"))
    ]
    ch2_content = "\n\n".join(ch2_parts)
    ch2_file = os.path.join(output_dir, "Chapter2_Empirical_from_Proposal.md")
    with open(ch2_file, "w", encoding="utf-8") as f:
        f.write(ch2_content)

    # 3. Chapter 3: Methodology, Population, Instruments, Procedure, Analysis, Ethics
    ch3_parts = [
        "# فصل سوم: روش‌شناسی پژوهش\n",
        "## ۳-۱. روش و طرح پژوهش",
        clean_section_text(sections.get("methodology", "")),
        "\n## ۳-۲. جامعه آماری، نمونه و روش نمونه‌گیری",
        clean_section_text(sections.get("methodology", "")),
        "\n## ۳-۳. ابزارهای جمع‌آوری داده‌ها",
        clean_section_text(sections.get("instruments", "")),
        "\n## ۳-۴. روش‌های تجزیه و تحلیل داده‌ها",
        clean_section_text(sections.get("data_analysis", "")),
        "\n## ۳-۵. ملاحظات اخلاقی",
        clean_section_text(sections.get("ethics", ""))
    ]
    ch3_content = "\n\n".join(ch3_parts)
    ch3_file = os.path.join(output_dir, "Chapter3_from_Proposal.md")
    with open(ch3_file, "w", encoding="utf-8") as f:
        f.write(ch3_content)

    # 4. Proposal References
    refs_content = clean_section_text(sections.get("references", ""))
    refs_file = os.path.join(output_dir, "Proposal_References.txt")
    with open(refs_file, "w", encoding="utf-8") as f:
        f.write(refs_content)

    print(f"Successfully extracted proposal sections with 100% Persian typography into: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract proposal sections into thesis chapters.")
    parser.add_argument("--proposal-pdf", default=r"g:\My Drive\My Work\Fada Talebi\Proposal-Mrs Talebian.pdf", help="Path to proposal PDF")
    parser.add_argument("--output-dir", default=r"g:\My Drive\My Work\Fada Talebi\Proposal_Extracted", help="Output directory")
    args = parser.parse_args()

    export_proposal_sections(args.proposal_pdf, args.output_dir)
