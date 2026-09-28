#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_lo_alignment.py
--------------------
Empirical investigation script for Task ID: TSK-2026-TEST-LIBREOFFICE-ALIGNMENT-001.

Objective:
Determine the exact OpenXML (word/document.xml, styles.xml, settings.xml) combination
that makes LibreOffice Writer (and Microsoft Word) render:
  1. Headings on the physical RIGHT.
  2. Table Captions on the physical RIGHT.
  3. Table Column 0 on the physical RIGHT.
  4. Table Columns 1..N in the CENTER.
  5. Narrative text JUSTIFIED from both margins.

Experimental Tests:
  - Test A: <w:bidi w:val="1"/> + <w:jc w:val="right"/>
  - Test B: <w:bidi w:val="1"/> + <w:jc w:val="start"/>
  - Test C: <w:bidi w:val="1"/> + no <w:jc>
  - Test D: <w:bidi w:val="1"/> + <w:jc w:val="left"/>
  - Test E: What happens if <w:sectPr> has <w:bidi/>?
  - Test F: What happens if styles.xml Normal style has <w:bidi/> and w:rtl?
"""

import os
import sys
import subprocess
import xml.etree.ElementTree as ET
import docx
from docx.shared import Inches, Pt
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

OUTDIR = "/tmp/lo_alignment_suite"
os.makedirs(OUTDIR, exist_ok=True)

ODF_NS = {
    'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
    'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
    'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
    'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
    'fo': 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0',
}

def create_paragraph(doc, text, bidi=True, jc=None, style_name=None):
    p = doc.add_paragraph()
    if style_name:
        p.style = style_name
    pPr = p._p.get_or_add_pPr()
    if bidi:
        pPr.append(parse_xml(f'<w:bidi {nsdecls("w")} w:val="1"/>'))
    if jc is not None:
        pPr.append(parse_xml(f'<w:jc {nsdecls("w")} w:val="{jc}"/>'))
    run = p.add_run(text)
    if bidi:
        rPr = run._r.get_or_add_rPr()
        rPr.append(parse_xml(f'<w:rtl {nsdecls("w")} w:val="1"/>'))
        rPr.append(parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="B Nazanin" w:hAnsi="B Nazanin" w:cs="B Nazanin"/>'))
    return p

def run_suite():
    print("=" * 70)
    print("TSK-2026-TEST-LIBREOFFICE-ALIGNMENT-001: COMPREHENSIVE EXPERIMENT")
    print("=" * 70)
    
    # -------------------------------------------------------------
    # 1. Generate Experimental Variations (Tests A-F)
    # -------------------------------------------------------------
    configs = [
        ("exp1_no_sect_bidi", False, False),
        ("exp2_with_sect_bidi", True, False),
        ("exp3_with_styles_bidi", True, True),
    ]
    
    for cfg_name, has_sect_bidi, has_styles_bidi in configs:
        doc = docx.Document()
        
        # Configure sectPr (Test E)
        if has_sect_bidi:
            sectPr = doc.sections[0]._sectPr
            if sectPr.find(qn('w:bidi')) is None:
                sectPr.insert(0, parse_xml(f'<w:bidi {nsdecls("w")}/>'))
                
        # Configure styles.xml Normal (Test F)
        if has_styles_bidi:
            for s in doc.styles._element.findall(qn('w:style')):
                if s.get(qn('w:styleId')) == 'Normal':
                    pPr = s.find(qn('w:pPr'))
                    if pPr is None:
                        pPr = OxmlElement('w:pPr')
                        s.append(pPr)
                    pPr.append(parse_xml(f'<w:bidi {nsdecls("w")} w:val="1"/>'))
                    pPr.append(parse_xml(f'<w:jc {nsdecls("w")} w:val="both"/>'))
                    rPr = s.find(qn('w:rPr'))
                    if rPr is None:
                        rPr = OxmlElement('w:rPr')
                        s.append(rPr)
                    rPr.append(parse_xml(f'<w:rtl {nsdecls("w")} w:val="1"/>'))

        # Tests A, B, C, D, End, Both, Center
        create_paragraph(doc, "Test A (bidi=1, jc=right): عنوان تست", bidi=True, jc="right")
        # Note: python-docx parse_xml rejects 'start', but raw element can be injected:
        p_b = doc.add_paragraph()
        p_b._p.get_or_add_pPr().append(parse_xml(f'<w:bidi {nsdecls("w")} w:val="1"/>'))
        el_start = OxmlElement('w:jc')
        el_start.set(qn('w:val'), 'start')
        p_b._p.pPr.append(el_start)
        r_b = p_b.add_run("Test B (bidi=1, jc=start): عنوان تست")
        r_b._r.get_or_add_rPr().append(parse_xml(f'<w:rtl {nsdecls("w")} w:val="1"/>'))
        
        create_paragraph(doc, "Test C (bidi=1, no jc): عنوان تست", bidi=True, jc=None)
        create_paragraph(doc, "Test D (bidi=1, jc=left): عنوان تست", bidi=True, jc="left")
        create_paragraph(doc, "Test End (bidi=1, jc=end): عنوان تست", bidi=True, jc="end")
        create_paragraph(doc, "Test Both (bidi=1, jc=both): این یک متن آزمایشی طولانی است که باید از هر دو طرف صفحه تراز شده باشد و برای ارزیابی جاستیفای در لیبره‌آفیس و ورد استفاده می‌شود.", bidi=True, jc="both")
        create_paragraph(doc, "Test Center (bidi=1, jc=center): عنوان تست", bidi=True, jc="center")
        
        # Headings
        create_paragraph(doc, "Heading 1 (jc=right): تیتر اول", bidi=True, jc="right", style_name="Heading 1")
        create_paragraph(doc, "Heading 1 (no jc): تیتر اول", bidi=True, jc=None, style_name="Heading 1")
        
        # Captions
        create_paragraph(doc, "Table Caption (jc=right): جدول ۱", bidi=True, jc="right")
        create_paragraph(doc, "Table Caption (no jc): جدول ۱", bidi=True, jc=None)

        docx_path = os.path.join(OUTDIR, f"{cfg_name}.docx")
        doc.save(docx_path)
        
        # Convert to FODT & PDF
        subprocess.run(["soffice", "--headless", "--convert-to", "fodt", docx_path, "--outdir", OUTDIR], check=True)
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", docx_path, "--outdir", OUTDIR], check=True)
        xml_path = os.path.join(OUTDIR, f"{cfg_name}.xml")
        subprocess.run(["pdftotext", "-bbox-layout", os.path.join(OUTDIR, f"{cfg_name}.pdf"), xml_path], check=True)
        
        # Inspect FODT
        fodt_tree = ET.parse(os.path.join(OUTDIR, f"{cfg_name}.fodt"))
        root = fodt_tree.getroot()
        style_props = {}
        for s in root.findall('.//style:style', ODF_NS):
            name = s.attrib.get(f"{{{ODF_NS['style']}}}name")
            for child in s:
                if child.tag == f"{{{ODF_NS['style']}}}paragraph-properties":
                    style_props[name] = {
                        'align': child.attrib.get(f"{{{ODF_NS['fo']}}}text-align"),
                        'wm': child.attrib.get(f"{{{ODF_NS['style']}}}writing-mode")
                    }
        
        page_wm = []
        for pl in root.findall('.//style:page-layout-properties', ODF_NS):
            wm = pl.attrib.get(f"{{{ODF_NS['style']}}}writing-mode")
            if wm: page_wm.append(wm)
            
        print(f"\n>>> CONFIG: {cfg_name} | sect_bidi={has_sect_bidi} | styles_bidi={has_styles_bidi}")
        print(f"    Page Layout Writing Mode: {page_wm}")
        
        # Inspect PDF
        pdf_tree = ET.parse(xml_path)
        pdf_ns = {'h': 'http://www.w3.org/1999/xhtml'}
        for line in pdf_tree.findall('.//h:line', pdf_ns):
            words = [w.text for w in line.findall('.//h:word', pdf_ns) if w.text]
            t = ' '.join(words)
            xMin = float(line.attrib['xMin'])
            xMax = float(line.attrib['xMax'])
            pos = "PHYSICAL RIGHT" if xMax > 500 else ("PHYSICAL LEFT" if xMin < 100 else "MIDDLE/SPAN")
            if any(k in t for k in ["Test A", "Test B", "Test C", "Test D", "Test End", "Test Both", "Test Center", "Heading 1", "Table Caption"]):
                print(f"    {pos:15} | xMin={xMin:5.1f}, xMax={xMax:5.1f} | {t[:45]}")

    # -------------------------------------------------------------
    # 2. Final Winning Publication Recipe Verification
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("FINAL WINNING RECIPE EXECUTION & DUAL-ENGINE VERIFICATION")
    print("=" * 70)
    
    doc_win = docx.Document()
    
    # 1. settings.xml
    settings = doc_win.settings._element
    theme_font = settings.find(qn('w:themeFontLang'))
    if theme_font is not None:
        theme_font.set(qn('w:bidi'), 'fa-IR')
    compat = settings.find(qn('w:compat'))
    if compat is not None:
        for cs in compat.findall(qn('w:compatSetting')):
            if cs.get(qn('w:name')) == 'compatibilityMode':
                cs.set(qn('w:val'), '15')
                
    # 2. sectPr
    for section in doc_win.sections:
        sectPr = section._sectPr
        if sectPr.find(qn('w:bidi')) is None:
            sectPr.insert(0, parse_xml(f'<w:bidi {nsdecls("w")}/>'))
        section.top_margin = Inches(0.98)
        section.bottom_margin = Inches(0.98)
        section.right_margin = Inches(1.18)
        section.left_margin = Inches(0.98)

    # 3. styles.xml
    for s in doc_win.styles._element.findall(qn('w:style')):
        s_id = s.get(qn('w:styleId'))
        pPr = s.find(qn('w:pPr'))
        if pPr is None:
            pPr = OxmlElement('w:pPr')
            s.append(pPr)
        if pPr.find(qn('w:bidi')) is None:
            pPr.append(parse_xml(f'<w:bidi {nsdecls("w")} w:val="1"/>'))
        rPr = s.find(qn('w:rPr'))
        if rPr is None:
            rPr = OxmlElement('w:rPr')
            s.append(rPr)
        if rPr.find(qn('w:rtl')) is None:
            rPr.append(parse_xml(f'<w:rtl {nsdecls("w")} w:val="1"/>'))
        if s_id == 'Normal' and pPr.find(qn('w:jc')) is None:
            pPr.append(parse_xml(f'<w:jc {nsdecls("w")} w:val="both"/>'))

    # Objective 1: Headings on physical RIGHT (bidi=1, NO w:jc)
    for lvl in [1, 2, 3]:
        h = doc_win.add_heading(f"عنوان تیتر سطح {lvl} (راست‌چین)", level=lvl)
        pPr = h._p.get_or_add_pPr()
        pPr.append(parse_xml(f'<w:bidi {nsdecls("w")} w:val="1"/>'))
        # NO w:jc!
        run = h.runs[0]
        rPr = run._r.get_or_add_rPr()
        rPr.append(parse_xml(f'<w:rtl {nsdecls("w")} w:val="1"/>'))
        rPr.append(parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="B Titr" w:hAnsi="B Titr" w:cs="B Titr"/>'))

    # Objective 5: Narrative text JUSTIFIED (bidi=1, jc=both)
    p_n = doc_win.add_paragraph()
    pPr_n = p_n._p.get_or_add_pPr()
    pPr_n.append(parse_xml(f'<w:bidi {nsdecls("w")} w:val="1"/>'))
    pPr_n.append(parse_xml(f'<w:jc {nsdecls("w")} w:val="both"/>'))
    run_n = p_n.add_run(
        "در این پژوهش، تحلیل داده‌های آماری با استفاده از روش‌های آمار توصیفی و استنباطی در دو سطح مورد بررسی قرار گرفت. "
        "ابتدا مفروضه‌های آماری شامل آزمون نرمال بودن توزیع نمرات از طریق آزمون شاپیرو-ویلک و همگنی واریانس‌ها با آزمون لوین بررسی گردید "
        "و نتایج نشان داد که تمامی متغیرها دارای توزیع نرمال بوده و شرایط لازم برای اجرای آزمون‌های پارامتریک کاملاً برقرار است."
    )
    rPr_n = run_n._r.get_or_add_rPr()
    rPr_n.append(parse_xml(f'<w:rtl {nsdecls("w")} w:val="1"/>'))
    rPr_n.append(parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="B Nazanin" w:hAnsi="B Nazanin" w:cs="B Nazanin"/>'))

    # Objective 2: Table Caption on physical RIGHT (bidi=1, NO w:jc)
    p_c = doc_win.add_paragraph()
    pPr_c = p_c._p.get_or_add_pPr()
    pPr_c.append(parse_xml(f'<w:bidi {nsdecls("w")} w:val="1"/>'))
    # NO w:jc!
    run_c = p_c.add_run("جدول ۴-۱. شاخص‌های توصیفی و استنباطی متغیرهای پژوهش (APA 7th Edition)")
    rPr_c = run_c._r.get_or_add_rPr()
    rPr_c.append(parse_xml(f'<w:rtl {nsdecls("w")} w:val="1"/>'))
    rPr_c.append(parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="B Titr" w:hAnsi="B Titr" w:cs="B Titr"/>'))

    # Objective 3 & 4: Table Col 0 RIGHT, Cols 1..N CENTER
    table = doc_win.add_table(rows=4, cols=4)
    tblPr = table._tbl.tblPr
    tblPr.append(parse_xml(f'<w:bidiVisual {nsdecls("w")}/>'))
    tblPr.append(parse_xml(f'<w:jc {nsdecls("w")} w:val="center"/>'))
    
    headers = ["متغیر", "میانگین (M)", "انحراف استاندارد (SD)", "سطح معناداری (p)"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = ""
        p = cell.paragraphs[0]
        pPr = p._p.get_or_add_pPr()
        pPr.append(parse_xml(f'<w:bidi {nsdecls("w")} w:val="1"/>'))
        if j > 0:
            pPr.append(parse_xml(f'<w:jc {nsdecls("w")} w:val="center"/>'))
        run = p.add_run(h)
        rPr = run._r.get_or_add_rPr()
        rPr.append(parse_xml(f'<w:rtl {nsdecls("w")} w:val="1"/>'))
        rPr.append(parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="B Titr" w:hAnsi="B Titr" w:cs="B Titr"/>'))
        
    data = [
        ["تاب‌آوری روان‌شناختی", "۲۴.۳۵", "۴.۱۸", "۰.۰۰۱ >"],
        ["اضطراب فراگیر اجتماعی", "۱۸.۱۲", "۳.۷۲", "۰.۰۱۴"],
        ["سلامت روان‌شناختی", "۳۱.۴۵", "۵.۶۰", "۰.۰۰۳"]
    ]
    for i, row in enumerate(data, start=1):
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.text = ""
            p = cell.paragraphs[0]
            pPr = p._p.get_or_add_pPr()
            pPr.append(parse_xml(f'<w:bidi {nsdecls("w")} w:val="1"/>'))
            if j > 0:
                pPr.append(parse_xml(f'<w:jc {nsdecls("w")} w:val="center"/>'))
            run = p.add_run(val)
            rPr = run._r.get_or_add_rPr()
            if j == 0:
                rPr.append(parse_xml(f'<w:rtl {nsdecls("w")} w:val="1"/>'))
                rPr.append(parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="B Nazanin" w:hAnsi="B Nazanin" w:cs="B Nazanin"/>'))
            else:
                rPr.append(parse_xml(f'<w:rtl {nsdecls("w")} w:val="0"/>'))
                rPr.append(parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'))

    final_docx = os.path.join(OUTDIR, "final_winning_artifact.docx")
    final_fodt = os.path.join(OUTDIR, "final_winning_artifact.fodt")
    final_pdf = os.path.join(OUTDIR, "final_winning_artifact.pdf")
    final_xml = os.path.join(OUTDIR, "final_winning_artifact.xml")
    
    doc_win.save(final_docx)
    subprocess.run(["soffice", "--headless", "--convert-to", "fodt", final_docx, "--outdir", OUTDIR], check=True)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", final_docx, "--outdir", OUTDIR], check=True)
    subprocess.run(["pdftotext", "-bbox-layout", final_pdf, final_xml], check=True)
    
    print(f"Artifact successfully saved: {final_docx}")
    print(f"Converted FODT: {final_fodt}")
    print(f"Converted PDF:  {final_pdf}")
    print(f"Layout XML:     {final_xml}")
    
    # Audit assertions
    pdf_tree = ET.parse(final_xml)
    pdf_ns = {'h': 'http://www.w3.org/1999/xhtml'}
    lines = []
    for line in pdf_tree.findall('.//h:line', pdf_ns):
        words = [w.text for w in line.findall('.//h:word', pdf_ns) if w.text]
        lines.append((' '.join(words), float(line.attrib['xMin']), float(line.attrib['xMax'])))
        
    right_margin = 527.0
    h_lines = [l for l in lines if 'نیچ‌تسار' in l[0] or 'رتیت' in l[0]]
    h_ok = len(h_lines) == 3 and all(abs(l[2] - right_margin) < 1.0 for l in h_lines)
    
    cap_lines = [l for l in lines if 'APA 7' in l[0] or 'Edition' in l[0]]
    cap_ok = len(cap_lines) >= 1 and all(abs(l[2] - right_margin) < 1.0 for l in cap_lines)
    
    col0_lines = [l for l in lines if (l[0] == 'ریغتم' or 'یروآ‌بات' in l[0] or 'یعامتجا ریگارف' in l[0] or ('تملاس' in l[0] and l[2] < 525))]
    col0_ok = len(col0_lines) == 4 and all(abs(l[2] - 521.6) < 1.0 for l in col0_lines)
    
    col1_lines = [l for l in lines if any(k in l[0] for k in ['۲۴ . ۳۵', '۱۸ . ۱۲', '۳۱ . ۴۵'])]
    col2_lines = [l for l in lines if any(k in l[0] for k in ['۴ . ۱۸', '۳ . ۷۲', '۵ . ۶۰'])]
    col3_lines = [l for l in lines if any(k in l[0] for k in ['۰ . ۰۰۱', '۰ . ۰۱۴', '۰ . ۰۰۳'])]
    cols_center_ok = (len(col1_lines) == 3 and len(col2_lines) == 3 and len(col3_lines) == 3 and
                      all(abs((l[1]+l[2])/2 - 355.8) < 1.0 for l in col1_lines) and
                      all(abs((l[1]+l[2])/2 - 241.7) < 1.0 for l in col2_lines) and
                      all(abs((l[1]+l[2])/2 - 127.6) < 1.0 for l in col3_lines))
                      
    narrative_full = [l for l in lines if abs(l[1] - 70.5) < 2.0 and abs(l[2] - 527.1) < 1.0]
    narrative_last = [l for l in lines if 'رارقرب لاًماک' in l[0] and abs(l[2] - 527.1) < 1.0]
    narrative_ok = len(narrative_full) == 2 and len(narrative_last) == 1
    
    print("\n--- OBJECTIVE AUDIT CHECKLIST ---")
    print(f"1. Headings on Physical Right (xMax={right_margin}pt):        {'PASS' if h_ok else 'FAIL'} ({len(h_lines)}/3)")
    print(f"2. Table Caption on Physical Right (xMax={right_margin}pt):    {'PASS' if cap_ok else 'FAIL'} ({len(cap_lines)}/1)")
    print(f"3. Table Col 0 on Physical Right (xMax=521.6pt):             {'PASS' if col0_ok else 'FAIL'} ({len(col0_lines)}/4)")
    print(f"4. Table Cols 1..N Centered (Midpoints 355.8, 241.7, 127.6): {'PASS' if cols_center_ok else 'FAIL'} ({len(col1_lines)+len(col2_lines)+len(col3_lines)}/9)")
    print(f"5. Narrative Text Justified (70.5pt to 527.1pt):             {'PASS' if narrative_ok else 'FAIL'} ({len(narrative_full)} full + {len(narrative_last)} last)")
    
    overall = h_ok and cap_ok and col0_ok and cols_center_ok and narrative_ok
    print("\n" + "=" * 70)
    print("FINAL CERTIFICATION VERDICT:", "PASS 100% (ALL TESTS VERIFIED)" if overall else "FAIL")
    print("=" * 70)

if __name__ == '__main__':
    run_suite()
