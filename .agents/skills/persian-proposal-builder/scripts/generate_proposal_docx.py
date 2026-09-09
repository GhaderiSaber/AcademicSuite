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
import re
import shutil
import zipfile
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
    """Add text run with explicit Persian and Latin font bindings and w:rtl."""
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
    rtl = OxmlElement('w:rtl')
    rPr.append(rtl)
    lang = OxmlElement('w:lang')
    lang.set(qn('w:val'), 'fa-IR')
    lang.set(qn('w:bidi'), 'fa-IR')
    rPr.append(lang)
    return run

def add_native_footnote_reference(paragraph, fn_id, font_name="B Nazanin"):
    """Adds native Word footnote reference element with Persian numeral styling and w:rtl."""
    run = paragraph.add_run()
    rPr = run._element.get_or_add_rPr()
    
    rStyle = OxmlElement('w:rStyle')
    rStyle.set(qn('w:val'), 'FootnoteReference')
    rPr.append(rStyle)
    
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)
    rPr.append(rFonts)
    
    rtl = OxmlElement('w:rtl')
    rPr.append(rtl)
    
    lang = OxmlElement('w:lang')
    lang.set(qn('w:val'), 'fa-IR')
    lang.set(qn('w:bidi'), 'fa-IR')
    rPr.append(lang)
    
    fnRef = OxmlElement('w:footnoteReference')
    fnRef.set(qn('w:id'), str(fn_id))
    run._element.append(fnRef)

def add_body_paragraph(doc, text, first_line_indent=0.35, line_spacing=1.35, space_after=6, font_fa='B Nazanin', font_size_pt=13):
    """
    Adds a justified Persian paragraph, parsing any [^ID] footnote markers seamlessly
    and normalizing quote placements to prevent BiDi wrapping glitches.
    """
    p = doc.add_paragraph()
    set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.JUSTIFY)
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.space_after = Pt(space_after)
    if first_line_indent > 0:
        p.paragraph_format.first_line_indent = Inches(first_line_indent)

    # Normalize quotes around footnote tokens: «...[^15]» -> «...»[^15]
    clean_text = re.sub(r'«([^»\n]+)\[\^(\d+)\]»', r'«\1»[^\2]', text)

    tokens = re.split(r'(\[\^\d+\])', clean_text)
    for token in tokens:
        if not token:
            continue
        m = re.match(r'\[\^(\d+)\]', token)
        if m:
            fn_id = int(m.group(1))
            add_native_footnote_reference(p, fn_id, font_name=font_fa)
        else:
            add_run(p, token, font_fa=font_fa, size=font_size_pt)
    return p

def add_section_heading(doc, text, level=2):
    """
    Adds standard academic section headings conforming to persian-thesis-builder:
    - Level 1: B Titr 16pt Bold, Right-aligned, space_before 24pt, space_after 14pt, Heading1, keepNext
    - Level 2: B Titr 14pt Bold, Right-aligned, space_before 14pt, space_after 6pt, Heading2, keepNext
    - Level 3: B Nazanin Bold 13pt Bold, Right-aligned, space_before 8pt, space_after 4pt, Heading3, keepNext
    - Level 4: B Nazanin Bold 12pt Bold, Right-aligned, space_before 6pt, space_after 2pt, Heading4, keepNext
    """
    p = doc.add_paragraph()
    set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.RIGHT)
    
    if level == 1:
        p.paragraph_format.space_before = Pt(24)
        p.paragraph_format.space_after = Pt(14)
        size = 16
        font = 'B Titr'
        style_val = "Heading1"
    elif level == 2:
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        size = 14
        font = 'B Titr'
        style_val = "Heading2"
    elif level == 3:
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        size = 13
        font = 'B Nazanin'
        style_val = "Heading3"
    else:
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        size = 12
        font = 'B Nazanin'
        style_val = "Heading4"
        
    pPr = p._p.get_or_add_pPr()
    # Enforce keepNext to prevent orphan headings at bottom of page
    keepNext = OxmlElement('w:keepNext')
    pPr.append(keepNext)
    # Enforce Word Navigation Pane Heading style
    pStyle = OxmlElement('w:pStyle')
    pStyle.set(qn('w:val'), style_val)
    pPr.append(pStyle)
    
    add_run(p, text, font_fa=font, size=size, bold=True)
    return p

def pack_native_footnotes(base_docx_path, output_docx_path, footnotes_list):
    """
    Injects word/footnotes.xml and sets compatibilityMode = 15 in word/settings.xml.
    footnotes_list: list of tuples (id: int, latin_text: str)
    """
    if not footnotes_list:
        if base_docx_path != output_docx_path:
            shutil.copy2(base_docx_path, output_docx_path)
        return output_docx_path

    temp_dir = base_docx_path + "_extracted"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)

    with zipfile.ZipFile(base_docx_path, 'r') as z_in:
        z_in.extractall(temp_dir)

    # 1. Update [Content_Types].xml
    ct_file = os.path.join(temp_dir, "[Content_Types].xml")
    with open(ct_file, 'r', encoding='utf-8') as f:
        ct_data = f.read()
    if '/word/footnotes.xml' not in ct_data:
        ct_data = ct_data.replace('</Types>', '  <Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/>\n</Types>')
        with open(ct_file, 'w', encoding='utf-8') as f:
            f.write(ct_data)

    # 2. Update word/_rels/document.xml.rels
    rels_file = os.path.join(temp_dir, "word", "_rels", "document.xml.rels")
    with open(rels_file, 'r', encoding='utf-8') as f:
        rels_data = f.read()
    if 'footnotes.xml' not in rels_data:
        rels_data = rels_data.replace('</Relationships>', '  <Relationship Id="rIdFootnotes" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes" Target="footnotes.xml"/>\n</Relationships>')
        with open(rels_file, 'w', encoding='utf-8') as f:
            f.write(rels_data)

    # 3. Update styles.xml: FootnoteReference style with Persian fonts and vertAlign
    styles_file = os.path.join(temp_dir, "word", "styles.xml")
    if os.path.exists(styles_file):
        with open(styles_file, 'r', encoding='utf-8') as f:
            styles_data = f.read()
        fn_style = """  <w:style w:type="character" w:styleId="FootnoteReference">
    <w:name w:val="footnote reference"/>
    <w:basedOn w:val="DefaultParagraphFont"/>
    <w:uiPriority w:val="99"/>
    <w:semiHidden/>
    <w:unhideWhenUsed/>
    <w:rPr>
      <w:rFonts w:ascii="B Nazanin" w:hAnsi="B Nazanin" w:cs="B Nazanin"/>
      <w:vertAlign w:val="superscript"/>
      <w:rtl/>
      <w:lang w:val="fa-IR" w:bidi="fa-IR"/>
    </w:rPr>
  </w:style>
"""
        if 'w:styleId="FootnoteReference"' not in styles_data:
            styles_data = styles_data.replace('</w:styles>', fn_style + '</w:styles>')
            with open(styles_file, 'w', encoding='utf-8') as f:
                f.write(styles_data)

    # 4. Create word/footnotes.xml
    fn_lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<w:footnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">',
        '  <w:footnote w:type="separator" w:id="-1">',
        '    <w:p>',
        '      <w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>',
        '      <w:r><w:separator/></w:r>',
        '    </w:p>',
        '  </w:footnote>',
        '  <w:footnote w:type="continuationSeparator" w:id="0">',
        '    <w:p>',
        '      <w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>',
        '      <w:r><w:continuationSeparator/></w:r>',
        '    </w:p>',
        '  </w:footnote>'
    ]

    for idx, latin in footnotes_list:
        safe_latin = str(latin).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        fn_lines.append(f'  <w:footnote w:id="{idx}">')
        fn_lines.append('    <w:p>')
        fn_lines.append('      <w:pPr>')
        fn_lines.append('        <w:pStyle w:val="FootnoteText"/>')
        fn_lines.append('        <w:jc w:val="left"/>')
        fn_lines.append('        <w:spacing w:after="30" w:line="240" w:lineRule="auto"/>')
        fn_lines.append('      </w:pPr>')
        fn_lines.append('      <w:r>')
        fn_lines.append('        <w:rPr>')
        fn_lines.append('          <w:rStyle w:val="FootnoteReference"/>')
        fn_lines.append('          <w:rFonts w:ascii="B Nazanin" w:hAnsi="B Nazanin" w:cs="B Nazanin"/>')
        fn_lines.append('          <w:rtl/>')
        fn_lines.append('          <w:lang w:val="fa-IR" w:bidi="fa-IR"/>')
        fn_lines.append('        </w:rPr>')
        fn_lines.append('        <w:footnoteRef/>')
        fn_lines.append('      </w:r>')
        fn_lines.append('      <w:r>')
        fn_lines.append('        <w:rPr>')
        fn_lines.append('          <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>')
        fn_lines.append('          <w:sz w:val="19"/>')
        fn_lines.append('          <w:szCs w:val="19"/>')
        fn_lines.append('        </w:rPr>')
        fn_lines.append(f'        <w:t xml:space="preserve"> {safe_latin}</w:t>')
        fn_lines.append('      </w:r>')
        fn_lines.append('    </w:p>')
        fn_lines.append('  </w:footnote>')

    fn_lines.append('</w:footnotes>')
    fn_xml_content = "\n".join(fn_lines)

    with open(os.path.join(temp_dir, "word", "footnotes.xml"), 'w', encoding='utf-8') as f:
        f.write(fn_xml_content)

    # 5. Update settings.xml: ensure compatibilityMode = 15 (Word 2013+ modern Bidi layout)
    settings_file = os.path.join(temp_dir, "word", "settings.xml")
    if os.path.exists(settings_file):
        with open(settings_file, 'r', encoding='utf-8') as f:
            set_data = f.read()
        set_data = re.sub(r'<w:compatSetting\s+w:name="compatibilityMode"[^>]*/>', '<w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/>', set_data)
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(set_data)

    # 6. Re-pack into output docx
    out_dir = os.path.dirname(output_docx_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    if os.path.exists(output_docx_path):
        os.remove(output_docx_path)
    with zipfile.ZipFile(output_docx_path, 'w', zipfile.ZIP_DEFLATED) as z_out:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                full_f = os.path.join(root, file)
                rel_f = os.path.relpath(full_f, temp_dir)
                z_out.write(full_f, rel_f)

    shutil.rmtree(temp_dir, ignore_errors=True)
    return output_docx_path

def build_proposal_document(data: dict, output_path: str):
    doc = docx.Document()
    
    # Set standard page margins (2.5 cm on all sides)
    for section in doc.sections:
        section.top_margin = Inches(0.98)
        section.bottom_margin = Inches(0.98)
        section.right_margin = Inches(1.18)
        section.left_margin = Inches(0.98)
        
    # --- Header / Title (Strictly RTL & Right-Aligned, clean academic header) ---
    p_header = doc.add_paragraph()
    set_paragraph_bidi(p_header, WD_ALIGN_PARAGRAPH.RIGHT)
    p_header.paragraph_format.space_before = Pt(8)
    p_header.paragraph_format.space_after = Pt(4)
    add_run(p_header, "طرح پژوهش پایان‌نامه کارشناسی ارشد / رساله دکتری (پروپوزال)", font_fa='B Nazanin', size=10.5, bold=False)
    
    title_fa = data.get("title", "عنوان پژوهش تعیین نشده است")
    p_title = doc.add_paragraph()
    set_paragraph_bidi(p_title, WD_ALIGN_PARAGRAPH.RIGHT)
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(12)
    pPr_t = p_title._p.get_or_add_pPr()
    keepNext_t = OxmlElement('w:keepNext')
    pPr_t.append(keepNext_t)
    pStyle_t = OxmlElement('w:pStyle')
    pStyle_t.set(qn('w:val'), 'Heading1')
    pPr_t.append(pStyle_t)
    add_run(p_title, f"عنوان طرح: {title_fa}", font_fa='B Titr', size=16, bold=True)
    
    # Metadata Block (Strictly RTL & Right-Aligned)
    meta = data.get("metadata", {})
    if meta:
        p_meta = doc.add_paragraph()
        set_paragraph_bidi(p_meta, WD_ALIGN_PARAGRAPH.RIGHT)
        p_meta.paragraph_format.space_after = Pt(14)
        meta_items = [
            f"دانشجو: {meta.get('student', 'نام دانشجو')}",
            f"استاد راهنما: {meta.get('supervisor', 'نام استاد راهنما')}",
            f"استاد مشاور: {meta.get('advisor', 'نام استاد مشاور')}",
            f"رشته و گرایش: {meta.get('field', 'روان‌شناسی')}"
        ]
        add_run(p_meta, " | ".join(meta_items), font_fa='B Nazanin', size=10, bold=False)
        
    # --- 1. Problem Statement ---
    add_section_heading(doc, "۱. بیان مسئله اساسی پژوهش (Problem Statement)", level=2)
    add_body_paragraph(doc, data.get("problem_statement", "متن بیان مسئله..."))
    
    # --- 2. Significance & Necessity ---
    add_section_heading(doc, "۲. اهمیت و ضرورت پژوهش (Significance & Necessity)", level=2)
    add_body_paragraph(doc, data.get("significance", "متن اهمیت و ضرورت پژوهش..."))
    
    # --- 3. Objectives ---
    add_section_heading(doc, "۳. اهداف پژوهش (Research Objectives)", level=2)
    obj_main = data.get("main_objective", "هدف کلی پژوهش...")
    p_mo = doc.add_paragraph()
    set_paragraph_bidi(p_mo)
    p_mo.paragraph_format.first_line_indent = Inches(0.35)
    p_mo.paragraph_format.space_after = Pt(4)
    add_run(p_mo, "هدف کلی: ", font_fa='B Nazanin', size=13, bold=True)
    add_run(p_mo, obj_main, font_fa='B Nazanin', size=13)
    
    specific_objs = data.get("specific_objectives", [])
    if specific_objs:
        p_so_title = doc.add_paragraph()
        set_paragraph_bidi(p_so_title)
        p_so_title.paragraph_format.first_line_indent = Inches(0.35)
        p_so_title.paragraph_format.space_before = Pt(4)
        p_so_title.paragraph_format.space_after = Pt(2)
        add_run(p_so_title, "اهداف اختصاصی پژوهش عبارت‌اند از:", font_fa='B Nazanin', size=13, bold=True)
        for idx, obj in enumerate(specific_objs):
            p_obj = doc.add_paragraph()
            set_paragraph_bidi(p_obj)
            p_obj.paragraph_format.left_indent = Inches(0.35)
            p_obj.paragraph_format.space_after = Pt(3)
            add_run(p_obj, f"{idx+1}. {obj}")
            
    # --- 4. Hypotheses or Questions ---
    add_section_heading(doc, "۴. فرضیه‌ها یا سؤالات پژوهش (Hypotheses & Questions)", level=2)
    hypotheses = data.get("hypotheses", [])
    for idx, hyp in enumerate(hypotheses):
        p_hyp = doc.add_paragraph()
        set_paragraph_bidi(p_hyp)
        p_hyp.paragraph_format.left_indent = Inches(0.35)
        p_hyp.paragraph_format.space_after = Pt(3)
        add_run(p_hyp, f"{idx+1}. {hyp}")
        
    # --- 5. Definitions ---
    add_section_heading(doc, "۵. تعاریف نظری و عملیاتی متغیرها (Conceptual & Operational Definitions)", level=2)
    definitions = data.get("definitions", {})
    for var_name, def_data in definitions.items():
        conceptual = def_data.get('conceptual', '').strip()
        operational = def_data.get('operational', '').strip()
        def_text = f"در این پژوهش، سازه «{var_name}» در دو سطح مفهومی و عملیاتی مورد تعریف قرار می‌گیرد. در بعد مفهومی، {conceptual} در بعد عملیاتی، {operational}"
        add_body_paragraph(doc, def_text)
        
    # --- 6. Methodology ---
    add_section_heading(doc, "۶. روش‌شناسی پژوهش (Research Methodology)", level=2)
    
    # 6.1 Design
    add_section_heading(doc, "۱-۶. طرح پژوهش و چارچوب روش‌شناختی", level=3)
    add_body_paragraph(doc, data.get("research_design", "طرح پژوهش حاضر..."))
    
    # 6.2 Population & Sampling
    add_section_heading(doc, "۲-۶. جامعه آماری، حجم نمونه و روش نمونه‌گیری", level=3)
    add_body_paragraph(doc, data.get("population_and_sampling", "جامعه آماری پژوهش شامل..."))
    
    # 6.3 Instruments
    add_section_heading(doc, "۳-۶. ابزارهای گردآوری اطلاعات", level=3)
    instruments = data.get("instruments", [])
    for inst in instruments:
        inst_desc = inst.get("description", "")
        inst_name = inst.get("name", "ابزار")
        if inst_desc:
            add_body_paragraph(doc, f"«{inst_name}»: {inst_desc}")
            
    # 6.4 Cross-Cultural Adaptation (if applicable)
    if "adaptation_protocol" in data:
        add_section_heading(doc, "۴-۶. پروتکل ترجمه و انطباق فرهنگی", level=3)
        add_body_paragraph(doc, data["adaptation_protocol"])

    # 6.5 Validity Protocol (if applicable)
    if "validity_protocol" in data:
        add_section_heading(doc, "۵-۶. روش احراز روایی ابزار", level=3)
        add_body_paragraph(doc, data["validity_protocol"])

    # 6.6 Reliability Protocol (if applicable)
    if "reliability_protocol" in data:
        add_section_heading(doc, "۶-۶. روش ارزیابی پایایی ابزار", level=3)
        add_body_paragraph(doc, data["reliability_protocol"])

    # 6.7 Procedure (if applicable)
    if "procedure" in data:
        add_section_heading(doc, "۷-۶. روش اجرا و فرآیند گردآوری داده‌ها", level=3)
        add_body_paragraph(doc, data["procedure"])
    
    # 6.8 Statistical Methods
    add_section_heading(doc, "۸-۶. روش‌های تجزیه‌وتحلیل داده‌ها", level=3)
    add_body_paragraph(doc, data.get("statistical_analysis_plan", "جهت تجزیه‌وتحلیل داده‌ها از آمار توصیفی و استنباطی..."))
    
    # --- 7. Ethical Considerations ---
    add_section_heading(doc, "۷. ملاحظات اخلاقی (Ethical Considerations)", level=2)
    ethics = data.get("ethical_considerations", (
        "در این پژوهش، تمامی موازین و کدهای اخلاقی حاکم بر پژوهش‌های علوم رفتاری و سلامت بر پایه بیانیه هلسینکی به دقت رعایت می‌گردد. "
        "پیش از آغاز فرآیند آزمون، فرم رضایت آگاهانه به صورت شفاف در اختیار شرکت‌کنندگان قرار گرفته و به آنان اطمینان داده می‌شود که مشارکت در مطالعه کاملاً داوطلبانه است. "
        "کلیه پاسخ‌نامه‌ها بدون نام و به صورت کاملاً محرمانه کدگذاری و نگهداری شده و آزمودنی‌ها در هر زمان مجاز به خروج اختیاری از پژوهش خواهند بود."
    ))
    add_body_paragraph(doc, ethics)
    
    # --- 8. References ---
    add_section_heading(doc, "۸. فهرست منابع و مآخذ (References - APA 7th Edition)", level=2)
    refs = data.get("references", [])
    for ref in refs:
        p_ref = doc.add_paragraph()
        set_paragraph_bidi(p_ref, WD_ALIGN_PARAGRAPH.LEFT if any(ord(c) < 128 for c in ref[:10]) else WD_ALIGN_PARAGRAPH.RIGHT)
        p_ref.paragraph_format.left_indent = Inches(0.3)
        p_ref.paragraph_format.first_line_indent = Inches(-0.3)
        p_ref.paragraph_format.space_after = Pt(4)
        add_run(p_ref, ref, font_fa='B Nazanin', font_en='Times New Roman', size=10)
        
    footnotes = data.get("footnotes", [])
    if footnotes:
        temp_base = output_path + ".tmp.docx"
        doc.save(temp_base)
        pack_native_footnotes(temp_base, output_path, footnotes)
        if os.path.exists(temp_base):
            os.remove(temp_base)
    else:
        doc.save(output_path)
    print(f"✅ Research Proposal Document successfully generated at: {output_path}")

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
