#!/usr/bin/env python3
"""
Persian Research Proposal Word Generator (generate_proposal_docx.py)
-------------------------------------------------------------------
Generates standard Iranian graduate school Research Proposal Word documents (.docx)
with correct OpenXML RTL directionality and Persian typography (B Nazanin, B Titr).

Sections:
1. اطلاعات عمومی و عنوان طرح (General Info & Title)
2. بیان مسئله (Problem Statement)
3. اهمیت و ضرورت پژوهش (Significance & Necessity)
4. اهداف پژوهش (Objectives: General & Specific)
5. فرضیه‌ها و سؤالات پژوهش (Hypotheses / Questions)
6. تعاریف نظری و عملیاتی متغیرها (Definitions of Variables)
7. روش‌شناسی پژوهش (Methodology, Design, Population, Instruments, Statistical Plan)
8. ملاحظات اخلاقی (Ethical Considerations)
9. منابع و مآخذ (APA 7 References)
"""

import os
import sys
import json
import argparse
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_paragraph_bidi(p, align=WD_ALIGN_PARAGRAPH.RIGHT):
    """Enforce Persian BiDi RTL directionality on paragraph."""
    p.alignment = align
    pPr = p._p.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    bidi.set(qn('w:val'), '1')
    pPr.append(bidi)

def add_run(p, text, font_fa='B Nazanin', font_en='Times New Roman', size=13, bold=False, italic=False):
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

def add_section_heading(doc, text, level=2):
    p = doc.add_paragraph()
    set_paragraph_bidi(p)
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    size = 14 if level == 2 else 13
    font = 'B Titr' if level == 2 else 'B Nazanin'
    add_run(p, text, font_fa=font, size=size, bold=True)
    return p

def add_body_paragraph(doc, text):
    p = doc.add_paragraph()
    set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.JUSTIFY)
    p.paragraph_format.line_spacing = 1.25
    add_run(p, text)
    return p

def build_proposal_document(data: dict, output_path: str):
    doc = docx.Document()
    
    # Set standard page margins (3 cm right, 2.5 cm others)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.right_margin = Inches(1.18)
        section.left_margin = Inches(1.0)
        
    # --- Header / Title ---
    p_header = doc.add_paragraph()
    set_paragraph_bidi(p_header, WD_ALIGN_PARAGRAPH.CENTER)
    p_header.paragraph_format.space_before = Pt(12)
    p_header.paragraph_format.space_after = Pt(6)
    add_run(p_header, "طرح پژوهش پایان‌نامه کارشناسی ارشد / رساله دکتری (پروپوزال)", font_fa='B Titr', size=16, bold=True)
    
    title_fa = data.get("title", "عنوان پژوهش تعیین نشده است")
    p_title = doc.add_paragraph()
    set_paragraph_bidi(p_title, WD_ALIGN_PARAGRAPH.CENTER)
    p_title.paragraph_format.space_before = Pt(8)
    p_title.paragraph_format.space_after = Pt(20)
    add_run(p_title, f"عنوان: {title_fa}", font_fa='B Titr', size=14, bold=True)
    
    # Metadata Block
    meta = data.get("metadata", {})
    if meta:
        p_meta = doc.add_paragraph()
        set_paragraph_bidi(p_meta, WD_ALIGN_PARAGRAPH.RIGHT)
        p_meta.paragraph_format.space_after = Pt(16)
        meta_items = [
            f"دانشجو: {meta.get('student', 'نام دانشجو')}",
            f"استاد راهنما: {meta.get('supervisor', 'نام استاد راهنما')}",
            f"استاد مشاور: {meta.get('advisor', 'نام استاد مشاور')}",
            f"رشته و گرایش: {meta.get('field', 'روان‌شناسی')}"
        ]
        add_run(p_meta, " | ".join(meta_items), font_fa='B Nazanin', size=11, bold=True)
        
    # --- 1. Problem Statement ---
    add_section_heading(doc, "۱. بیان مسئله اساسی پژوهش", level=2)
    add_body_paragraph(doc, data.get("problem_statement", "متن بیان مسئله..."))
    
    # --- 2. Significance & Necessity ---
    add_section_heading(doc, "۲. اهمیت و ضرورت پژوهش", level=2)
    add_body_paragraph(doc, data.get("significance", "متن اهمیت و ضرورت پژوهش..."))
    
    # --- 3. Objectives ---
    add_section_heading(doc, "۳. اهداف پژوهش", level=2)
    obj_main = data.get("main_objective", "هدف کلی پژوهش...")
    p_mo = doc.add_paragraph()
    set_paragraph_bidi(p_mo)
    add_run(p_mo, f"هدف کلی: {obj_main}", font_fa='B Nazanin', size=13, bold=True)
    
    specific_objs = data.get("specific_objectives", [])
    if specific_objs:
        p_so_title = doc.add_paragraph()
        set_paragraph_bidi(p_so_title)
        add_run(p_so_title, "اهداف اختصاصی:", font_fa='B Nazanin', size=13, bold=True)
        for idx, obj in enumerate(specific_objs):
            p_obj = doc.add_paragraph()
            set_paragraph_bidi(p_obj)
            p_obj.paragraph_format.left_indent = Inches(0.2)
            add_run(p_obj, f"{idx+1}. {obj}")
            
    # --- 4. Hypotheses or Questions ---
    add_section_heading(doc, "۴. فرضیه‌ها یا سؤالات پژوهش", level=2)
    hypotheses = data.get("hypotheses", [])
    for idx, hyp in enumerate(hypotheses):
        p_hyp = doc.add_paragraph()
        set_paragraph_bidi(p_hyp)
        p_hyp.paragraph_format.left_indent = Inches(0.2)
        add_run(p_hyp, f"{idx+1}. {hyp}")
        
    # --- 5. Definitions ---
    add_section_heading(doc, "۵. تعاریف نظری و عملیاتی متغیرها", level=2)
    definitions = data.get("definitions", {})
    for var_name, def_data in definitions.items():
        p_var = doc.add_paragraph()
        set_paragraph_bidi(p_var)
        add_run(p_var, f"• متغیر {var_name}:", font_fa='B Nazanin', size=13, bold=True)
        
        p_th = doc.add_paragraph()
        set_paragraph_bidi(p_th)
        p_th.paragraph_format.left_indent = Inches(0.2)
        add_run(p_th, f"- تعریف نظری: {def_data.get('conceptual', '')}")
        
        p_op = doc.add_paragraph()
        set_paragraph_bidi(p_op)
        p_op.paragraph_format.left_indent = Inches(0.2)
        add_run(p_op, f"- تعریف عملیاتی: {def_data.get('operational', '')}")
        
    # --- 6. Methodology ---
    add_section_heading(doc, "۶. روش‌شناسی پژوهش", level=2)
    
    # 6.1 Design
    add_section_heading(doc, "۱-۶. طرح پژوهش", level=3)
    add_body_paragraph(doc, data.get("research_design", "طرح پژوهش حاضر..."))
    
    # 6.2 Population & Sampling
    add_section_heading(doc, "۲-۶. جامعه آماری، حجم نمونه و روش نمونه‌گیری", level=3)
    add_body_paragraph(doc, data.get("population_and_sampling", "جامعه آماری پژوهش شامل..."))
    
    # 6.3 Instruments
    add_section_heading(doc, "۳-۶. ابزارهای گردآوری داده‌ها", level=3)
    instruments = data.get("instruments", [])
    for inst in instruments:
        p_inst = doc.add_paragraph()
        set_paragraph_bidi(p_inst)
        add_run(p_inst, f"• {inst.get('name', 'ابزار')}:", font_fa='B Nazanin', size=13, bold=True)
        add_body_paragraph(doc, inst.get("description", ""))
        
    # 6.4 Procedure
    add_section_heading(doc, "۴-۶. روش اجرا و پروتکل مداخله", level=3)
    add_body_paragraph(doc, data.get("procedure", "نحوه اجرای پژوهش و گردآوری داده‌ها..."))
    
    # 6.5 Statistical Methods
    add_section_heading(doc, "۵-۶. روش‌های تجزیه‌وتحلیل داده‌ها", level=3)
    add_body_paragraph(doc, data.get("statistical_analysis_plan", "جهت تجزیه‌وتحلیل داده‌ها از آمار توصیفی و استنباطی..."))
    
    # --- 7. Ethical Considerations ---
    add_section_heading(doc, "۷. ملاحظات اخلاقی", level=2)
    ethics = data.get("ethical_considerations", (
        "در این پژوهش، تمامی موازین و کدهای اخلاقی حاکم بر پژوهش‌های علوم انسانی و رفتاری رعایت گردید. "
        "پیش از آغاز گردآوری داده‌ها، اهداف پژوهش برای شرکت‌کنندگان تشریح شد و رضایت آگاهانه و کتبی از آنان اخذ گردید. "
        "همچنین به آزمودنی‌ها اطمینان داده شد که اطلاعات حاصل به‌صورت کاملاً محرمانه و بدون ذکر نام نگهداری خواهد شد "
        "و آنان در هر مرحله از پژوهش حق انصراف اختیاری خواهند داشت."
    ))
    add_body_paragraph(doc, ethics)
    
    # --- 8. References ---
    add_section_heading(doc, "۸. منابع و مآخذ", level=2)
    refs = data.get("references", [])
    for ref in refs:
        p_ref = doc.add_paragraph()
        set_paragraph_bidi(p_ref)
        p_ref.paragraph_format.left_indent = Inches(0.2)
        add_run(p_ref, ref)
        
    doc.save(output_path)
    print(f"Research Proposal Document successfully generated at: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Persian Research Proposal Word Generator")
    parser.add_argument("--json", required=True, help="Path to proposal JSON content")
    parser.add_argument("--out", default="پروپوزال_طرح_پژوهش.docx", help="Output .docx file path")
    args = parser.parse_args()
    
    with open(args.json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    build_proposal_document(data, args.out)

if __name__ == "__main__":
    main()
