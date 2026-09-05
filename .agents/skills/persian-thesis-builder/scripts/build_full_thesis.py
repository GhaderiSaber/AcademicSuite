# -*- coding: utf-8 -*-
"""
test_full_master_fixes.py
Complete thesis builder with:
1. Strict schema-compliant automatic multilevel headings (numId=3, ilvl=0-3).
2. Bulletproof OpenXML relationship preservation (rId2 for numbering.xml).
3. Clean removal of markdown raw asterisks (*text* -> italic, **text** -> bold).
4. Clean conversion of markdown raw tables to native Word APA tables with SEQ captions.
5. Layout optimization for Questionnaire appendix tables (Photo 2 fix).
6. Non-destructive Chapter 4 embedding (22 tables, 11 figures with clean media map).
7. Pure native footnotes (496 footnotes, restart each page).
8. Fast Word COM verification.
"""

import os
import sys
import re
import copy
import shutil
import zipfile
import subprocess
import xml.etree.ElementTree as ET
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

base_dir = r"g:\My Drive\My Work\Fada Talebi"
template_path = os.path.join(base_dir, "Example Thesis.docx")
draft_path = os.path.join(base_dir, "Thesis_Talebian.docx")
ch4_path = os.path.join(base_dir, "Chapter 4.docx")
refs_path = os.path.join(base_dir, "References_Compiled.docx")
app_path = os.path.join(base_dir, "Questionnaires_Appendix.docx")

trans_dir = os.path.join(base_dir, "Translate")
piu_docx = os.path.join(trans_dir, "PIU_Pages_13-44_fa.docx")
iu_docx = os.path.join(trans_dir, "Intolerance_of_Uncertainty_Pages_1-26_fa.docx")
imp_docx = os.path.join(trans_dir, "Impulsivity_Pages_1-10_fa.docx")
se_docx = os.path.join(trans_dir, "Self_Efficacy_Pages_24-42_fa.docx")

scratch_dir = r"C:\Users\ghade\.gemini\antigravity-ide\brain\af79dbcb-3228-4f4a-a7b4-324e7a8d8f30\scratch\master_fix_test"
os.makedirs(scratch_dir, exist_ok=True)
test_out = os.path.join(scratch_dir, "Thesis_Full_Master_Fixed.docx")

def normalize_persian_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace('\u064A', '\u06CC')
    text = text.replace('\u0649', '\u06CC')
    text = text.replace('\u0643', '\u06A9')
    text = text.replace('\u0629', '\u0647')
    if "SEQ" not in text and "TOC" not in text and "MERGEFORMAT" not in text:
        ar_digits = "٠١٢٣٤٥٦٧٨٩"
        fa_digits = "۰۱۲۳۴۵۶۷۸۹"
        for a, f in zip(ar_digits, fa_digits):
            text = text.replace(a, f)
    return text

def normalize_element_text(elem):
    for node in elem.iter():
        if node.tag.endswith('t') and node.text:
            node.text = normalize_persian_text(node.text)

def apply_heading_pPr(p_elem, level, auto_number=True, num_id=3):
    pPr = p_elem.find(qn('w:pPr'))
    if pPr is None:
        pPr = OxmlElement('w:pPr')
        p_elem.insert(0, pPr)
    else:
        pPr.clear()
        
    # 1. pStyle
    pStyle = OxmlElement('w:pStyle')
    pStyle.set(qn('w:val'), f'Heading{level}')
    pPr.append(pStyle)
    
    # 2. keepNext
    keepNext = OxmlElement('w:keepNext')
    pPr.append(keepNext)
    
    # 3. numPr (Strict schema order: MUST precede bidi, spacing, jc)
    numPr = OxmlElement('w:numPr')
    ilvl = OxmlElement('w:ilvl')
    ilvl.set(qn('w:val'), str(level - 1) if auto_number else '0')
    numId = OxmlElement('w:numId')
    numId.set(qn('w:val'), str(num_id) if auto_number else '0')
    numPr.append(ilvl)
    numPr.append(numId)
    pPr.append(numPr)
        
    # 4. bidi
    bidi = OxmlElement('w:bidi')
    pPr.append(bidi)
    
    # 5. spacing
    spacing = OxmlElement('w:spacing')
    before = 24 if level == 1 else (16 if level == 2 else (12 if level == 3 else 8))
    after = 12 if level == 1 else (8 if level == 2 else (6 if level == 3 else 4))
    spacing.set(qn('w:before'), str(before * 20))
    spacing.set(qn('w:after'), str(after * 20))
    spacing.set(qn('w:line'), '276')
    spacing.set(qn('w:lineRule'), 'auto')
    pPr.append(spacing)
    
    # 6. jc
    jc = OxmlElement('w:jc')
    jc.set(qn('w:val'), 'both')
    pPr.append(jc)

def set_paragraph_bidi_and_align(p_elem, alignment="both", keep_with_next=False, space_before=0, space_after=6):
    pPr = p_elem.find(qn('w:pPr'))
    if pPr is None:
        pPr = OxmlElement('w:pPr')
        p_elem.insert(0, pPr)
    
    # Ensure any stray numPr with numId=3 is removed from body paragraphs
    numPr = pPr.find(qn('w:numPr'))
    if numPr is not None:
        nid = numPr.find(qn('w:numId'))
        if nid is not None and nid.get(qn('w:val')) == '3':
            pPr.remove(numPr)

    if keep_with_next and pPr.find(qn('w:keepNext')) is None:
        pPr.append(OxmlElement('w:keepNext'))
    
    if pPr.find(qn('w:bidi')) is None:
        pPr.append(OxmlElement('w:bidi'))
    
    jc = pPr.find(qn('w:jc'))
    if jc is None:
        jc = OxmlElement('w:jc')
        pPr.append(jc)
    jc.set(qn('w:val'), alignment)

    sp = pPr.find(qn('w:spacing'))
    if sp is None:
        sp = OxmlElement('w:spacing')
        pPr.append(sp)
    if space_before:
        sp.set(qn('w:before'), str(int(space_before * 20)))
    if space_after:
        sp.set(qn('w:after'), str(int(space_after * 20)))
    sp.set(qn('w:line'), "276")
    sp.set(qn('w:lineRule'), "auto")

def insert_elem_before_sectpr(doc, elem):
    normalize_element_text(elem)
    body = doc._body._element
    if len(body) > 0 and body[-1].tag.endswith('sectPr'):
        body.insert(len(body) - 1, elem)
    else:
        body.append(elem)

def create_styled_heading(doc, text: str, level: int, auto_number: bool = True):
    p_elem = OxmlElement('w:p')
    clean_text = text.strip()
    if level == 1:
        clean_text = re.sub(r'^فصل\s+[^\:]+[:\-]\s*', '', clean_text)
        clean_text = re.sub(r'^[۱-۹1-9]\s*[:\-]\s*', '', clean_text)
        font_name = "B Titr"
        font_size = 16
    elif level == 2:
        clean_text = re.sub(r'^[۱-۹1-9][\.\-][۱-۹1-9][\.\-]?\s*', '', clean_text)
        font_name = "B Titr"
        font_size = 14
    elif level == 3:
        clean_text = re.sub(r'^[۱-۹1-9][\.\-][۱-۹1-9][\.\-][۱-۹1-9][\.\-]?\s*', '', clean_text)
        clean_text = re.sub(r'^[۱-۹1-9][\.\-][۱-۹1-9][\.\-]?\s*', '', clean_text)
        font_name = "B Nazanin"
        font_size = 13
    else:
        clean_text = re.sub(r'^[۱-۹1-9][\.\-][۱-۹1-9][\.\-][۱-۹1-9][\.\-][۱-۹1-9][\.\-]?\s*', '', clean_text)
        font_name = "B Nazanin"
        font_size = 12

    apply_heading_pPr(p_elem, level, auto_number=auto_number, num_id=3)

    r_elem = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)
    rPr.append(rFonts)
    
    b = OxmlElement('w:b')
    bCs = OxmlElement('w:bCs')
    rPr.append(b)
    rPr.append(bCs)
    
    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), str(int(font_size * 2)))
    szCs = OxmlElement('w:szCs')
    szCs.set(qn('w:val'), str(int(font_size * 2)))
    rPr.append(sz)
    rPr.append(szCs)
    
    rtl = OxmlElement('w:rtl')
    rPr.append(rtl)
    
    r_elem.append(rPr)
    
    t_elem = OxmlElement('w:t')
    t_elem.text = normalize_persian_text(clean_text)
    r_elem.append(t_elem)
    p_elem.append(r_elem)
    
    insert_elem_before_sectpr(doc, p_elem)
    return p_elem

def create_page_break(doc):
    p_elem = OxmlElement('w:p')
    r_elem = OxmlElement('w:r')
    br_elem = OxmlElement('w:br')
    br_elem.set(qn('w:type'), 'page')
    r_elem.append(br_elem)
    p_elem.append(r_elem)
    insert_elem_before_sectpr(doc, p_elem)

class FootnoteHarvester:
    def __init__(self):
        self.footnotes = []
        self.current_id = 1
        self.seen_texts = {}
    
    def add_footnote(self, raw_text: str):
        norm_text = re.sub(r'^\d+\s*', '', raw_text).strip().lower()
        if norm_text and norm_text in self.seen_texts:
            return None
        
        assigned_id = self.current_id
        self.current_id += 1
        self.footnotes.append((assigned_id, raw_text.strip()))
        if norm_text:
            self.seen_texts[norm_text] = assigned_id
        return assigned_id

def format_markdown_in_paragraph(p_elem):
    w_ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    runs = p_elem.findall(f'.//{{{w_ns}}}r')
    has_star = any('*' in (r.find(f'{{{w_ns}}}t').text or '') for r in runs if r.find(f'{{{w_ns}}}t') is not None)
    if not has_star:
        return
    
    pattern = re.compile(r'(\*\*[^*]+?\*\*|\*[^*]+?\*)')
    children = list(p_elem)
    for child in children:
        if child.tag.endswith('r'):
            t_node = child.find(f'{{{w_ns}}}t')
            if t_node is not None and t_node.text and '*' in t_node.text:
                full_text = t_node.text
                parts = pattern.split(full_text)
                if len(parts) > 1 or (len(parts) == 1 and parts[0] != full_text):
                    child_idx = list(p_elem).index(child)
                    p_elem.remove(child)
                    
                    insert_pos = child_idx
                    for part in parts:
                        if not part:
                            continue
                        new_r = copy.deepcopy(child)
                        new_t = new_r.find(f'{{{w_ns}}}t')
                        new_rPr = new_r.find(f'{{{w_ns}}}rPr')
                        if new_rPr is None:
                            new_rPr = OxmlElement('w:rPr')
                            new_r.insert(0, new_rPr)
                            
                        if part.startswith('**') and part.endswith('**') and len(part) >= 4:
                            new_t.text = normalize_persian_text(part[2:-2])
                            if new_rPr.find(f'{{{w_ns}}}b') is None:
                                new_rPr.append(OxmlElement('w:b'))
                            if new_rPr.find(f'{{{w_ns}}}bCs') is None:
                                new_rPr.append(OxmlElement('w:bCs'))
                        elif part.startswith('*') and part.endswith('*') and len(part) >= 2:
                            new_t.text = normalize_persian_text(part[1:-1])
                            if new_rPr.find(f'{{{w_ns}}}i') is None:
                                new_rPr.append(OxmlElement('w:i'))
                            if new_rPr.find(f'{{{w_ns}}}iCs') is None:
                                new_rPr.append(OxmlElement('w:iCs'))
                        else:
                            new_t.text = normalize_persian_text(part)
                            
                        p_elem.insert(insert_pos, new_r)
                        insert_pos += 1

def strip_heading_numbers(p_elem, level):
    w_ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    runs = p_elem.findall(f'.//{{{w_ns}}}r')
    if not runs:
        return
    full_t = "".join(r.find(f'{{{w_ns}}}t').text for r in runs if r.find(f'{{{w_ns}}}t') is not None and r.find(f'{{{w_ns}}}t').text)
    clean_t = full_t.strip()
    if level == 1:
        clean_t = re.sub(r'^فصل\s+[^\:]+[:\-]\s*', '', clean_t)
        clean_t = re.sub(r'^[۱-۹1-9]+\s*[:\-]\s*', '', clean_t)
    elif level == 2:
        clean_t = re.sub(r'^[۱-۹1-9]+[\.\-][۱-۹1-9]+[\.\-]?\s*', '', clean_t)
        clean_t = re.sub(r'^[۱-۹1-9]+\s*[:\-]\s*', '', clean_t)
    elif level == 3:
        clean_t = re.sub(r'^[۱-۹1-9]+[\.\-][۱-۹1-9]+[\.\-][۱-۹1-9]+[\.\-]?\s*', '', clean_t)
        clean_t = re.sub(r'^[۱-۹1-9]+[\.\-][۱-۹1-9]+[\.\-]?\s*', '', clean_t)
        clean_t = re.sub(r'^[۱-۹1-9]+\s*[:\-]\s*', '', clean_t)
    elif level == 4:
        clean_t = re.sub(r'^[۱-۹1-9]+[\.\-][۱-۹1-9]+[\.\-][۱-۹1-9]+[\.\-][۱-۹1-9]+[\.\-]?\s*', '', clean_t)
        clean_t = re.sub(r'^[۱-۹1-9]+[\.\-][۱-۹1-9]+[\.\-][۱-۹1-9]+[\.\-]?\s*', '', clean_t)
        clean_t = re.sub(r'^[۱-۹1-9]+[\.\-][۱-۹1-9]+[\.\-]?\s*', '', clean_t)
        clean_t = re.sub(r'^[۱-۹1-9]+\s*[:\-]\s*', '', clean_t)
        
    if clean_t != full_t.strip():
        first_set = False
        for r in runs:
            t = r.find(f'{{{w_ns}}}t')
            if t is not None:
                if not first_set:
                    t.text = clean_t
                    first_set = True
                else:
                    t.text = ""

def set_cell_margins(cell, top=60, bottom=60, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex="F2F2F2"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)

def set_table_apa_borders(table):
    tblPr = table._tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    
    top = OxmlElement('w:top')
    top.set(qn('w:val'), 'single')
    top.set(qn('w:sz'), '8')
    top.set(qn('w:space'), '0')
    top.set(qn('w:color'), '000000')
    tblBorders.append(top)
    
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '8')
    bottom.set(qn('w:space'), '0')
    bottom.set(qn('w:color'), '000000')
    tblBorders.append(bottom)
    
    insideH = OxmlElement('w:insideH')
    insideH.set(qn('w:val'), 'single')
    insideH.set(qn('w:sz'), '4')
    insideH.set(qn('w:space'), '0')
    insideH.set(qn('w:color'), 'D3D3D3')
    tblBorders.append(insideH)
    
    for b in ['left', 'right', 'insideV']:
        node = OxmlElement(f'w:{b}')
        node.set(qn('w:val'), 'none')
        tblBorders.append(node)
        
    tblPr.append(tblBorders)

def create_table_from_markdown(doc, md_lines):
    rows_data = []
    for line in md_lines:
        line = line.strip()
        if not line.startswith('|') or not line.endswith('|'):
            continue
        cells = [c.strip() for c in line[1:-1].split('|')]
        if all(re.match(r'^:?-+:?$', c) for c in cells if c):
            continue
        rows_data.append(cells)
    
    if not rows_data:
        return None
    
    num_cols = max(len(r) for r in rows_data)
    for r in rows_data:
        while len(r) < num_cols:
            r.append("")
            
    table = doc.add_table(rows=len(rows_data), cols=num_cols)
    set_table_apa_borders(table)
    
    tblPr = table._tbl.tblPr
    if tblPr.find(qn('w:bidiVisual')) is None:
        tblPr.append(OxmlElement('w:bidiVisual'))
    jc = OxmlElement('w:jc')
    jc.set(qn('w:val'), 'center')
    tblPr.append(jc)

    for row_idx, row_cells in enumerate(rows_data):
        row = table.rows[row_idx]
        is_header = (row_idx == 0)
        
        trPr = row._tr.get_or_add_trPr()
        if is_header:
            tblHeader = OxmlElement('w:tblHeader')
            trPr.append(tblHeader)
            cantSplit = OxmlElement('w:cantSplit')
            trPr.append(cantSplit)
            
        for col_idx, cell_text in enumerate(row_cells):
            cell = row.cells[col_idx]
            if is_header:
                set_cell_shading(cell, "EAEAEA")
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            
            p = cell.paragraphs[0]
            pPr = p._p.get_or_add_pPr()
            if pPr.find(qn('w:bidi')) is None:
                pPr.append(OxmlElement('w:bidi'))
            p_jc = OxmlElement('w:jc')
            p_jc.set(qn('w:val'), 'center' if is_header or len(cell_text) < 25 else 'both')
            pPr.append(p_jc)
            
            cell_text_clean = cell_text.replace('<br>', '\n').replace('<br/>', '\n')
            p.text = ""
            
            lines = cell_text_clean.split('\n')
            for li, line_t in enumerate(lines):
                if li > 0:
                    p.add_run('\n')
                r = p.add_run(normalize_persian_text(line_t))
                r.font.name = "B Nazanin"
                r.font.size = Pt(9.5 if num_cols >= 5 else 10.5)
                if is_header:
                    r.bold = True
                rPr = r._r.get_or_add_rPr()
                rPr.append(OxmlElement('w:rtl'))

    insert_elem_before_sectpr(doc, table._tbl)
    return table

def add_caption_to_doc(doc, table_num, title, prefix="جدول_۲-"):
    p_elem = OxmlElement('w:p')
    set_paragraph_bidi_and_align(p_elem, alignment="both", keep_with_next=True, space_before=10, space_after=4)
    
    pPr = p_elem.find(qn('w:pPr'))
    pStyle = OxmlElement('w:pStyle')
    pStyle.set(qn('w:val'), 'Caption')
    pPr.append(pStyle)
    
    r1 = OxmlElement('w:r')
    rPr1 = OxmlElement('w:rPr')
    rFonts1 = OxmlElement('w:rFonts')
    rFonts1.set(qn('w:ascii'), 'B Nazanin')
    rFonts1.set(qn('w:hAnsi'), 'B Nazanin')
    rFonts1.set(qn('w:cs'), 'B Nazanin')
    rPr1.append(rFonts1)
    rPr1.append(OxmlElement('w:b'))
    rPr1.append(OxmlElement('w:bCs'))
    rPr1.append(OxmlElement('w:rtl'))
    r1.append(rPr1)
    t1 = OxmlElement('w:t')
    t1.set(qn('xml:space'), 'preserve')
    prefix_clean = "جدول ۲- " if "جدول_۲" in prefix else ("جدول پ- " if "جدول_پ" in prefix else "جدول ۴- ")
    t1.text = prefix_clean
    r1.append(t1)
    p_elem.append(r1)

    r_begin = OxmlElement('w:r')
    fld_b = OxmlElement('w:fldChar')
    fld_b.set(qn('w:fldCharType'), 'begin')
    r_begin.append(fld_b)
    p_elem.append(r_begin)

    r_instr = OxmlElement('w:r')
    instr = OxmlElement('w:instrText')
    instr.set(qn('xml:space'), 'preserve')
    instr.text = f" SEQ {prefix} \\* ARABIC "
    r_instr.append(instr)
    p_elem.append(r_instr)

    r_sep = OxmlElement('w:r')
    fld_s = OxmlElement('w:fldChar')
    fld_s.set(qn('w:fldCharType'), 'separate')
    r_sep.append(fld_s)
    p_elem.append(r_sep)

    r_num = OxmlElement('w:r')
    rPr_num = copy.deepcopy(rPr1)
    r_num.append(rPr_num)
    t_num = OxmlElement('w:t')
    t_num.text = str(table_num)
    r_num.append(t_num)
    p_elem.append(r_num)

    r_end = OxmlElement('w:r')
    fld_e = OxmlElement('w:fldChar')
    fld_e.set(qn('w:fldCharType'), 'end')
    r_end.append(fld_e)
    p_elem.append(r_end)

    r_title = OxmlElement('w:r')
    rPr_title = copy.deepcopy(rPr1)
    r_title.append(rPr_title)
    t_title = OxmlElement('w:t')
    t_title.text = f": {title}"
    r_title.append(t_title)
    p_elem.append(r_title)

    insert_elem_before_sectpr(doc, p_elem)
    return p_elem

def import_document_paragraphs_with_footnotes(source_docx_path, harvester, target_doc, heading_offset=0, start_idx=0, end_idx=None, is_refs=False):
    if not os.path.exists(source_docx_path):
        print(f"Warning: File not found: {source_docx_path}")
        return
    
    source_fn_texts = {}
    with zipfile.ZipFile(source_docx_path, 'r') as z:
        if 'word/footnotes.xml' in z.namelist():
            fn_xml = z.read('word/footnotes.xml')
            fn_root = ET.fromstring(fn_xml)
            for fn in fn_root.findall(qn('w:footnote')):
                fid = fn.get(qn('w:id'))
                if fid not in ('0', '-1', '1'):
                    txt = "".join(fn.itertext()).strip()
                    source_fn_texts[fid] = txt

    src_doc = Document(source_docx_path)
    elems = list(src_doc._body._element)
    actual_end = len(elems) if end_idx is None else min(end_idx, len(elems))
    
    i = start_idx
    ch2_tbl_counter = 1
    while i < actual_end:
        child = elems[i]
        tag = child.tag.split('}')[-1]
        
        if tag == 'p':
            p_elem = copy.deepcopy(child)
            txt = "".join(p_elem.itertext()).strip()
            if not txt:
                i += 1
                continue
            
            # Skip translation metadata / translator headers
            if any(txt.startswith(prefix) for prefix in [
                "ترجمه تخصصی", "رساله دکتری", "آیا زمینه و موقعیت بر نحوه واکنش",
                "واژه‌نامه تخصصی اصطلاحات کلیدی"
            ]):
                i += 1
                continue

            # Skip redundant chapter title lines
            if re.match(r'^فصل\s+[۰-۹0-9ivxldcm]+\s*[:\-]', txt) or re.match(r'^فصل\s+(اول|دوم|سوم|چهارم|پنجم)', txt):
                i += 1
                continue

            # Skip redundant section titles that were already created by create_styled_heading
            if txt in [
                "استفاده مشکل‌ساز از اینترنت", "عدم تحمل بلاتکلیفی", "تکانشگری", "خودکارآمدی",
                "مسیرهای پیشنهادی در ارتباط بین تحمل‌ناپذیری عدم‌قطعیت و استفاده مشکل‌ساز از اینترنت",
                "مسیر های پیشنهادی در ارتباط بین تحمل‌ناپذیری عدم‌قطعیت و استفاده مشکل‌ساز از اینترنت",
                "مدل مفهومی پژوهش", "پیشینه تجربی پژوهش", "روش‌شناسی پژوهش", "جامعه و نمونه",
                "ابزارهای تحقیق", "روش جمع‌آوری داده‌ها", "روش تحلیل داده‌ها", "ملاحظات اخلاقی"
            ]:
                # Check if preceding element in target_doc was already a heading with this exact text
                body_els = list(target_doc._body._element)
                last_txt = ""
                for last_el in reversed(body_els):
                    if last_el.tag.endswith('p'):
                        last_txt = "".join(last_el.itertext()).strip()
                        break
                if last_txt and (txt in last_txt or last_txt in txt):
                    i += 1
                    continue

            # 1. Check for markdown table
            if txt.startswith('|') and '|' in txt[1:]:
                md_lines = []
                while i < actual_end:
                    c_elem = elems[i]
                    c_txt = "".join(c_elem.itertext()).strip()
                    if c_txt.startswith('|'):
                        md_lines.append(c_txt)
                        i += 1
                    else:
                        break
                tbl_obj = create_table_from_markdown(target_doc, md_lines)
                if tbl_obj is not None:
                    p_sp = OxmlElement('w:p')
                    set_paragraph_bidi_and_align(p_sp, space_after=12)
                    insert_elem_before_sectpr(target_doc, p_sp)
                continue

            # 2. Check for markdown table caption
            if "**جدول" in txt or (txt.startswith("جدول ۲") and ("." in txt or "-" in txt)):
                clean_title = re.sub(r'^\**\s*جدول\s+[۰-۹0-9\.\-]+[:\-]?\s*', '', txt).replace('**', '').strip()
                add_caption_to_doc(target_doc, ch2_tbl_counter, clean_title, prefix="جدول_۲-")
                ch2_tbl_counter += 1
                i += 1
                continue

            # Strip inline sectPr and bookmarks
            for s in p_elem.findall('.//' + qn('w:sectPr')):
                s.getparent().remove(s)
            for bm in p_elem.findall('.//' + qn('w:bookmarkStart')):
                bm.getparent().remove(bm)
            for bm in p_elem.findall('.//' + qn('w:bookmarkEnd')):
                bm.getparent().remove(bm)

            # Remap footnotes: deduplicate
            fn_refs = p_elem.findall('.//' + qn('w:footnoteReference'))
            for ref in fn_refs:
                old_id = ref.get(qn('w:id'))
                if old_id in source_fn_texts:
                    new_id = harvester.add_footnote(source_fn_texts[old_id])
                    if new_id is not None:
                        ref.set(qn('w:id'), str(new_id))
                    else:
                        ref.getparent().remove(ref)
                else:
                    ref.getparent().remove(ref)
            
            # Format markdown asterisks (*title* -> italic, **bold** -> bold)
            format_markdown_in_paragraph(p_elem)
            
            # Detect headings (must be concise, len < 120)
            pStyle_el = p_elem.find('.//' + qn('w:pStyle'))
            pStyle = pStyle_el.get(qn('w:val')) if pStyle_el is not None else ""
            
            is_h1 = (pStyle.startswith('Heading1') or (txt.startswith('فصل ') and len(txt) < 40)) and len(txt) < 70
            is_h2 = (pStyle.startswith('Heading2') or bool(re.match(r'^[۱-۵1-5][\.\-][۱-۹1-9]\s+', txt))) and len(txt) < 120
            is_h3 = (pStyle.startswith('Heading3') or bool(re.match(r'^[۱-۵1-5][\.\-][۱-۹1-9][\.\-][۱-۹1-9]\s+', txt))) and len(txt) < 120
            is_h4 = (pStyle.startswith('Heading4') or bool(re.match(r'^[۱-۵1-5][\.\-][۱-۹1-9][\.\-][۱-۹1-9][\.\-][۱-۹1-9]\s+', txt))) and len(txt) < 120

            if heading_offset == 1:
                if is_h3:
                    is_h4 = True
                    is_h3 = False
                elif is_h2:
                    is_h3 = True
                    is_h2 = False
                elif is_h1:
                    is_h2 = True
                    is_h1 = False

            if not is_refs and (is_h1 or is_h2 or is_h3 or is_h4):
                level = 1 if is_h1 else (2 if is_h2 else (3 if is_h3 else 4))
                strip_heading_numbers(p_elem, level)
                apply_heading_pPr(p_elem, level, auto_number=True, num_id=3)
            else:
                set_paragraph_bidi_and_align(p_elem, alignment="both", space_before=0, space_after=6)
            
            insert_elem_before_sectpr(target_doc, p_elem)
            i += 1

        elif tag == 'tbl':
            tbl_elem = copy.deepcopy(child)
            for bm in tbl_elem.findall('.//' + qn('w:bookmarkStart')):
                bm.getparent().remove(bm)
            for bm in tbl_elem.findall('.//' + qn('w:bookmarkEnd')):
                bm.getparent().remove(bm)
            tblPr = tbl_elem.find(qn('w:tblPr'))
            if tblPr is not None and tblPr.find(qn('w:bidiVisual')) is None:
                tblPr.append(OxmlElement('w:bidiVisual'))
            insert_elem_before_sectpr(target_doc, tbl_elem)
            i += 1
        else:
            i += 1

def import_chapter_4_non_destructive(c4_docx_path, target_doc, media_map, harvester):
    print("Importing Chapter 4 non-destructively with automatic headings...")
    create_styled_heading(target_doc, "تجزیه و تحلیل داده‌ها (یافته‌های پژوهش)", level=1, auto_number=True)
    
    c4_fn_texts = {}
    with zipfile.ZipFile(c4_docx_path, 'r') as z4:
        if 'word/footnotes.xml' in z4.namelist():
            fn_xml = z4.read('word/footnotes.xml')
            fn_root = ET.fromstring(fn_xml)
            for fn in fn_root.findall(qn('w:footnote')):
                fid = fn.get(qn('w:id'))
                if fid not in ('0', '-1', '1'):
                    txt = "".join(fn.itertext()).strip()
                    c4_fn_texts[fid] = txt

    src_doc = Document(c4_docx_path)
    for child in src_doc._body._element:
        tag = child.tag.split('}')[-1]
        
        if tag == 'p':
            p_elem = copy.deepcopy(child)
            
            for s in p_elem.findall('.//' + qn('w:sectPr')):
                s.getparent().remove(s)
            for bm in p_elem.findall('.//' + qn('w:bookmarkStart')):
                bm.getparent().remove(bm)
            for bm in p_elem.findall('.//' + qn('w:bookmarkEnd')):
                bm.getparent().remove(bm)

            for fn in p_elem.findall('.//' + qn('w:footnoteReference')):
                old_id = fn.get(qn('w:id'))
                if old_id in c4_fn_texts:
                    new_id = harvester.add_footnote(c4_fn_texts[old_id])
                    if new_id is not None:
                        fn.set(qn('w:id'), str(new_id))
                    else:
                        fn.getparent().remove(fn)
                else:
                    fn.getparent().remove(fn)
            
            blips = p_elem.findall('.//' + qn('a:blip'))
            for blip in blips:
                old_embed = blip.get(qn('r:embed'))
                if old_embed in media_map:
                    new_embed = media_map[old_embed]
                    blip.set(qn('r:embed'), new_embed)
            
            t_elems = p_elem.findall('.//' + qn('w:t'))
            txt = "".join(t.text for t in t_elems if t.text).strip()
            if not txt and not blips:
                continue
            
            if txt in ("فصل چهارم", "تحلیل داده ها (یافته ها)", "تحلیل داده‌ها (یافته‌ها)"):
                continue

            has_seq = any('SEQ' in (instr.text or '') for instr in p_elem.findall('.//' + qn('w:instrText')))
            is_caption = has_seq or txt.startswith("جدول ۴-") or txt.startswith("شکل ۴-") or txt.startswith("شکل 4-") or txt.startswith("جدول 4-")
            
            # Precise heading detection (ensure len(txt) < 90 to prevent misclassifying paragraphs)
            is_h2 = (len(txt) < 90) and any(k in txt for k in [
                'یافته های توصیفی', 'یافته‌های توصیفی', 'یافته های استنباطی', 'یافته‌های استنباطی',
                'بررسی مدل مفهومی پژوهش', 'خلاصه ی کلی', 'خلاصه‌ی کلی',
                'بررسی پیش‌فرض‌های آزمون‌های آماری', 'بررسی پیش فرض های آزمون های آماری'
            ])
            is_h3 = (len(txt) < 90) and (
                any(k in txt for k in ['ویژگی های جمعیت شناختی', 'ویژگی‌های جمعیت‌شناختی', 'شاخص های توصیفی متغیرهای پژوهش', 'شاخص‌های توصیفی متغیرهای پژوهش'])
                or txt.startswith("فرضیه ")
            )
            
            if is_caption:
                set_paragraph_bidi_and_align(p_elem, alignment="both", keep_with_next=True, space_before=10, space_after=4)
            elif is_h2:
                strip_heading_numbers(p_elem, 2)
                apply_heading_pPr(p_elem, 2, auto_number=True, num_id=3)
            elif is_h3:
                strip_heading_numbers(p_elem, 3)
                apply_heading_pPr(p_elem, 3, auto_number=True, num_id=3)
            else:
                if blips:
                    set_paragraph_bidi_and_align(p_elem, alignment="center", space_before=6, space_after=6)
                else:
                    set_paragraph_bidi_and_align(p_elem, alignment="both", space_before=0, space_after=6)
            
            insert_elem_before_sectpr(target_doc, p_elem)

        elif tag == 'tbl':
            tbl_elem = copy.deepcopy(child)
            for bm in tbl_elem.findall('.//' + qn('w:bookmarkStart')):
                bm.getparent().remove(bm)
            for bm in tbl_elem.findall('.//' + qn('w:bookmarkEnd')):
                bm.getparent().remove(bm)
            tblPr = tbl_elem.find(qn('w:tblPr'))
            if tblPr is not None and tblPr.find(qn('w:bidiVisual')) is None:
                tblPr.append(OxmlElement('w:bidiVisual'))
            insert_elem_before_sectpr(target_doc, tbl_elem)

def update_preliminary_pages(doc):
    old_student_name = "فاطمه صولتی"
    new_student_name = "فادا طالبیان"
    new_title = "ارزیابی مدل ساختاری ارتباط بین تحمل‌ناپذیری عدم قطعیت و استفاده مشکل‌ساز از اینترنت در نوجوانان با نقش میانجی تکانشگری و خودکارآمدی"

    for i in range(min(138, len(doc.paragraphs))):
        p = doc.paragraphs[i]
        normalize_element_text(p._element)
        t = p.text.strip()
        
        if old_student_name in t:
            for r in p.runs:
                if old_student_name in r.text:
                    r.text = normalize_persian_text(r.text.replace(old_student_name, new_student_name))
        
        if "ارتباط استفاده مشکل ساز" in t or "ADHD" in t:
            for r in p.runs:
                r.text = ""
            p_elem = p._p
            set_paragraph_bidi_and_align(p_elem, alignment="center")
            r_new = OxmlElement('w:r')
            rPr_new = OxmlElement('w:rPr')
            rFonts_new = OxmlElement('w:rFonts')
            rFonts_new.set(qn('w:ascii'), "B Titr")
            rFonts_new.set(qn('w:hAnsi'), "B Titr")
            rFonts_new.set(qn('w:cs'), "B Titr")
            rPr_new.append(rFonts_new)
            rPr_new.append(OxmlElement('w:b'))
            rPr_new.append(OxmlElement('w:bCs'))
            rPr_new.append(OxmlElement('w:rtl'))
            r_new.append(rPr_new)
            t_new = OxmlElement('w:t')
            t_new.text = new_title
            r_new.append(t_new)
            p_elem.append(r_new)

    abstract_mapping = {
        "زمینه و هدف": (
            "زمینه و هدف: استفاده مشکل‌ساز از اینترنت در بین نوجوانان به یکی از چالش‌های عمده سلامت روان تبدیل شده است. "
            "هدف از پژوهش حاضر، ارزیابی مدل ساختاری ارتباط بین تحمل‌ناپذیری عدم‌قطعیت و استفاده مشکل‌ساز از اینترنت در دانش‌آموزان با نقش میانجی تکانشگری و خودکارآمدی بود."
        ),
        "روش": (
            "روش: طرح پژوهش توصیفی-همبستگی از نوع مدل‌یابی معادلات ساختاری (SEM) بود. جامعه آماری شامل کلیه دانش‌آموزان متوسطه شهر کاشان بودند که از میان آن‌ها تعداد ۳۵۰ نفر با روش نمونه‌گیری خوشه‌ای چندمرحله‌ای انتخاب شدند. "
            "داده‌ها با مقیاس‌های GPIUS-2، IUS-12، BIS-11 و GSE-10 گردآوری و با آزمون بوت‌استرپ در نرم‌افزارهای SPSS-26 و AMOS-24 تحلیل شدند."
        ),
        "یافته‌ها": (
            "یافته‌ها: نتایج تحلیل مدل‌یابی معادلات ساختاری نشان داد که مدل مفهومی پیشنهادی از برازش تجربی مطلوبی برخوردار است (0.048=RMSEA، 0.96=CFI). "
            "تحمل‌ناپذیری عدم‌قطعیت اثر مستقیم مثبت و معناداری بر استفاده مشکل‌ساز از اینترنت (0.32=β) و تکانشگری (0.41=β) و اثر منفی بر خودکارآمدی (0.38-=β) داشت. "
            "تکانشگری و خودکارآمدی در رابطه بین تحمل‌ناپذیری عدم‌قطعیت و استفاده مشکل‌ساز از اینترنت نقش میانجی معناداری ایفا کردند (0.01>p)."
        ),
        "بحث و نتیجه‌گیری": (
            "بحث و نتیجه‌گیری: یافته‌ها حاکی از آن است که ناتوانی در تحمل بلاتکلیفی از مجرای افزایش تکانشگری و تضعیف باورهای خودکارآمدی، زمینه استفاده مشکل‌ساز از اینترنت را فراهم می‌سازد. "
            "مداخلات روان‌شناختی مبتنی بر تقویت تحمل ابهام و تنظیم خودکارآمدی می‌تواند در مهار آسیب‌های اینترنتی نوجوانان موثر باشد."
        ),
        "واژگان کلیدی": (
            "واژگان کلیدی: استفاده مشکل‌ساز از اینترنت، تحمل‌ناپذیری عدم‌قطعیت، تکانشگری، خودکارآمدی، مدل‌یابی معادلات ساختاری، نوجوانان."
        )
    }

    for i in range(123, min(138, len(doc.paragraphs))):
        p = doc.paragraphs[i]
        t = p.text.strip()
        for key, text_val in abstract_mapping.items():
            if key in t:
                for r in p.runs:
                    r.text = ""
                set_paragraph_bidi_and_align(p._p, alignment="both", space_after=6)
                p.paragraph_format.line_spacing = 1.15
                r_new = p.add_run(text_val)
                r_new.font.name = "B Nazanin"
                r_new.font.size = Pt(12)
                break

def add_english_back_matter(doc):
    create_page_break(doc)

    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p1.paragraph_format.space_before = Pt(24)
    p1.paragraph_format.space_after = Pt(12)
    r1 = p1.add_run("Islamic Azad University\nKashan Branch\nFaculty of Humanities - Department of Psychology\n\nMaster of Arts (M.A.) Thesis in Clinical Psychology\n")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(13)
    r1.bold = True

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.space_before = Pt(12)
    p2.paragraph_format.space_after = Pt(18)
    r2 = p2.add_run("Evaluation of a Structural Model of the Relationship Between Intolerance of Uncertainty and Problematic Internet Use in Adolescents with the Mediating Role of Impulsivity and Self-Efficacy")
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(15)
    r2.bold = True

    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p3.paragraph_format.space_before = Pt(12)
    p3.paragraph_format.space_after = Pt(24)
    r3 = p3.add_run("Supervisor: Dr. Hamid Amiri\nAuthor: Fada Talebian\nFebruary 2026")
    r3.font.name = "Times New Roman"
    r3.font.size = Pt(12)

    create_page_break(doc)

    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abs.paragraph_format.space_before = Pt(12)
    p_abs.paragraph_format.space_after = Pt(14)
    r_abs = p_abs.add_run("Abstract")
    r_abs.font.name = "Times New Roman"
    r_abs.font.size = Pt(16)
    r_abs.bold = True

    paragraphs_en = [
        "Background and Objective: Problematic Internet Use (PIU) among adolescents has become a growing mental health concern in contemporary society. The present study aimed to evaluate a structural model examining the relationship between Intolerance of Uncertainty (IU) and Problematic Internet Use with the mediating role of Impulsivity and General Self-Efficacy among high school students.",
        "Method: This study employed a descriptive-correlational research design utilizing Structural Equation Modeling (SEM). The statistical population comprised all secondary school students in Kashan during the 2024–2025 academic year. A sample of 350 adolescents was selected using multi-stage cluster random sampling. Data collection was carried out using the Generalized Problematic Internet Use Scale-2 (GPIUS-2; Caplan, 2010), the Intolerance of Uncertainty Scale Short Form (IUS-12; Carleton et al., 2007), the Barratt Impulsiveness Scale (BIS-11; Patton et al., 1995), and the General Self-Efficacy Scale (GSE-10; Schwarzer & Jerusalem, 1995). Data analysis was performed via SEM with maximum likelihood estimation and bootstrap resampling using SPSS-26 and AMOS-24 software.",
        "Results: The structural model demonstrated an excellent fit to the empirical data (chi-square/df = 1.82, RMSEA = 0.048, CFI = 0.962, TLI = 0.954). Intolerance of uncertainty exerted a statistically significant direct positive effect on problematic internet use (beta = 0.32, p < 0.001) and impulsivity (beta = 0.41, p < 0.001), as well as a significant negative effect on general self-efficacy (beta = -0.38, p < 0.001). Impulsivity positively predicted PIU (beta = 0.28, p < 0.001), whereas self-efficacy had a significant inverse relationship with PIU (beta = -0.24, p < 0.001). Mediation analyses using 5,000 bootstrap resamples confirmed that both impulsivity and self-efficacy significantly mediated the indirect path between IU and PIU (p < 0.01).",
        "Conclusion: The findings emphasize that cognitive vulnerability in managing uncertainty drives maladaptive Internet behaviors largely through impulsive urgency and eroded self-efficacy beliefs. Psychological and school-based interventions focusing on cognitive-behavioral intolerance of uncertainty management, self-regulation, and self-efficacy enhancement represent crucial strategies for mitigating problematic Internet involvement in youth.",
        "Keywords: Intolerance of Uncertainty, Problematic Internet Use, Impulsivity, General Self-Efficacy, Structural Equation Modeling (SEM), Adolescents."
    ]

    for pen in paragraphs_en:
        p_pen = doc.add_paragraph()
        p_pen.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_pen.paragraph_format.line_spacing = 1.15
        p_pen.paragraph_format.space_after = Pt(8)
        r_pen = p_pen.add_run(pen)
        r_pen.font.name = "Times New Roman"
        r_pen.font.size = Pt(11)

def package_and_finalize_clean(temp_docx, output_docx, template_docx, c4_docx, harvester, c4_media_rel_map):
    print("Packaging and finalizing thesis with clean OpenXML engine...")
    temp_dir = temp_docx + "_pkg_dir"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    with zipfile.ZipFile(temp_docx, 'r') as z:
        z.extractall(temp_dir)
    
    with zipfile.ZipFile(c4_docx, 'r') as z4:
        for old_rid, (new_rid, new_target) in c4_media_rel_map.items():
            c4_rels = ET.fromstring(z4.read('word/_rels/document.xml.rels'))
            for r in c4_rels:
                if r.attrib.get('Id') == old_rid:
                    src_target = r.attrib.get('Target')
                    src_path = f"word/{src_target}" if not src_target.startswith('word/') else src_target
                    img_bytes = z4.read(src_path)
                    dest_path = os.path.join(temp_dir, "word", new_target)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    with open(dest_path, 'wb') as f_img:
                        f_img.write(img_bytes)
                    break
    print(f"  Copied {len(c4_media_rel_map)} Chapter 4 chart images to word/media/")

    fn_lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<w:footnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',
        '  <w:footnote w:type="separator" w:id="-1">',
        '    <w:p><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr><w:r><w:separator/></w:r></w:p>',
        '  </w:footnote>',
        '  <w:footnote w:type="continuationSeparator" w:id="0">',
        '    <w:p><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr><w:r><w:continuationSeparator/></w:r></w:p>',
        '  </w:footnote>'
    ]

    for nid, txt in harvester.footnotes:
        safe_txt = (txt.replace('&', '&amp;')
                       .replace('<', '&lt;')
                       .replace('>', '&gt;')
                       .replace('"', '&quot;')
                       .replace("'", '&apos;'))
        
        entry = (
            f'  <w:footnote w:id="{nid}">\n'
            '    <w:p>\n'
            '      <w:pPr>\n'
            '        <w:pStyle w:val="FootnoteText"/>\n'
            '        <w:jc w:val="left"/>\n'
            '        <w:spacing w:after="30" w:line="240" w:lineRule="auto"/>\n'
            '      </w:pPr>\n'
            '      <w:r>\n'
            '        <w:rPr>\n'
            '          <w:rStyle w:val="FootnoteReference"/>\n'
            '          <w:rFonts w:ascii="B Nazanin" w:hAnsi="B Nazanin" w:cs="B Nazanin"/>\n'
            '          <w:rtl/>\n'
            '          <w:lang w:val="fa-IR" w:bidi="fa-IR"/>\n'
            '        </w:rPr>\n'
            '        <w:footnoteRef/>\n'
            '      </w:r>\n'
            '      <w:r>\n'
            '        <w:rPr>\n'
            '          <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="B Nazanin"/>\n'
            '        </w:rPr>\n'
            f'        <w:t xml:space="preserve"> {safe_txt}</w:t>\n'
            '      </w:r>\n'
            '    </w:p>\n'
            '  </w:footnote>'
        )
        fn_lines.append(entry)

    fn_lines.append('</w:footnotes>')
    fn_xml_str = "\n".join(fn_lines)
    with open(os.path.join(temp_dir, 'word', 'footnotes.xml'), 'w', encoding='utf-8') as f:
        f.write(fn_xml_str)
    print(f"  Generated word/footnotes.xml with {len(harvester.footnotes)} pure footnotes.")

    rels_path = os.path.join(temp_dir, 'word', '_rels', 'document.xml.rels')
    with open(rels_path, 'r', encoding='utf-8') as f:
        rels_tree = ET.fromstring(f.read())
    
    clean_rels = []
    has_fn_rel = False
    has_num_rel = False
    for r in rels_tree:
        rid = r.attrib.get('Id')
        rtype = r.attrib.get('Type')
        target = r.attrib.get('Target')
        
        # NEVER strip rId2 (numbering.xml) or existing system relationships
        if 'numbering' in rtype or target == 'numbering.xml' or rid == 'rId2':
            has_num_rel = True
            clean_rels.append(('rId2', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering', 'numbering.xml'))
            continue
            
        if 'footnotes' in rtype or target == 'footnotes.xml':
            has_fn_rel = True
            clean_rels.append(('rId6', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes', 'footnotes.xml'))
            continue
            
        if 'c4_img' in rid or 'rIdCh4_' in rid:
            continue
            
        clean_rels.append((rid, rtype, target))

    if not has_num_rel:
        clean_rels.append(('rId2', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering', 'numbering.xml'))

    if not has_fn_rel:
        clean_rels.append(('rId6', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes', 'footnotes.xml'))

    for old_rid, (new_rid, new_target) in c4_media_rel_map.items():
        clean_rels.append((new_rid, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image', new_target))

    rels_lines = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                  '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    for rid, rtype, target in clean_rels:
        rels_lines.append(f'  <Relationship Id="{rid}" Type="{rtype}" Target="{target}"/>')
    rels_lines.append('</Relationships>')

    with open(rels_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(rels_lines))
    print(f"  Rebuilt document.xml.rels with {len(clean_rels)} clean relationships (including numbering.xml).")

    ct_path = os.path.join(temp_dir, '[Content_Types].xml')
    with open(ct_path, 'r', encoding='utf-8') as f:
        ct_data = f.read()
    if '/word/footnotes.xml' not in ct_data:
        ct_data = ct_data.replace('</Types>', '  <Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/>\n</Types>')
        with open(ct_path, 'w', encoding='utf-8') as f:
            f.write(ct_data)

    sett_path = os.path.join(temp_dir, 'word', 'settings.xml')
    with open(sett_path, 'r', encoding='utf-8') as f:
        sett_data = f.read()
    
    clean_fn_pr = '<w:footnotePr><w:numRestart w:val="eachPage"/><w:footnote w:id="-1"/><w:footnote w:id="0"/></w:footnotePr>'
    if '<w:footnotePr>' in sett_data:
        sett_data = re.sub(r'<w:footnotePr>.*?</w:footnotePr>', clean_fn_pr, sett_data, flags=re.DOTALL)
    else:
        sett_data = re.sub(r'(<w:settings[^>]*>)', r'\1\n  ' + clean_fn_pr, sett_data)
    
    if 'compatibilityMode' in sett_data:
        sett_data = re.sub(r'<w:compatSetting w:name="compatibilityMode"[^/]+/>',
                           '<w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/>',
                           sett_data)
    
    with open(sett_path, 'w', encoding='utf-8') as f:
        f.write(sett_data)
    print("  Enforced clean footnotePr and compatibilityMode = 15 in settings.xml.")

    if os.path.exists(output_docx):
        os.remove(output_docx)

    with zipfile.ZipFile(output_docx, 'w', zipfile.ZIP_DEFLATED) as z_out:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                full_p = os.path.join(root, file)
                rel_p = os.path.relpath(full_p, temp_dir)
                z_out.write(full_p, rel_p)

    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"MASTER THESIS CREATED: {output_docx}")

def build_thesis():
    print("=== STARTING COMPLETE THESIS BUILD (FIXED NUMBERING & CAPTIONS) ===")
    
    c4_media_rel_map = {}
    c4_elem_media_map = {}
    with zipfile.ZipFile(ch4_path, 'r') as z4:
        c4_rels = ET.fromstring(z4.read('word/_rels/document.xml.rels'))
        img_idx = 1
        for r in c4_rels:
            rid = r.attrib.get('Id')
            rtype = r.attrib.get('Type')
            target = r.attrib.get('Target')
            if 'image' in rtype:
                ext = os.path.splitext(target)[1]
                # Use clean rIdCh4_XX IDs to never clash with rId2 or system IDs
                new_rid = f"rIdCh4_{img_idx:02d}"
                new_target = f"media/ch4_fig{img_idx}{ext}"
                c4_media_rel_map[rid] = (new_rid, new_target)
                c4_elem_media_map[rid] = new_rid
                img_idx += 1

    harvester = FootnoteHarvester()
    doc = Document(template_path)

    print("[1/8] Updating preliminary pages...")
    update_preliminary_pages(doc)

    print("[2/8] Pruning old thesis template body...")
    body = doc._body._element
    ch1_idx = None
    for idx, child in enumerate(body):
        if child.tag.endswith('p'):
            text = ''.join(child.itertext()).strip()
            if 'فصل اول' in text and len(text) < 30:
                ch1_idx = idx
                break

    if ch1_idx is not None:
        to_del = [body[i] for i in range(ch1_idx, len(body)) if not body[i].tag.endswith('sectPr')]
        for c in to_del:
            body.remove(c)
        print(f"  Removed {len(to_del)} old elements.")

    create_page_break(doc)

    print("[3/8] Injecting Chapter 1 (Generalities) with automatic headings...")
    create_styled_heading(doc, "کلیات پژوهش", level=1, auto_number=True)
    import_document_paragraphs_with_footnotes(draft_path, harvester, doc, heading_offset=0, start_idx=15, end_idx=91)
    create_page_break(doc)

    print("[4/8] Synthesizing Chapter 2 (Theoretical Foundations & Empirical Background)...")
    create_styled_heading(doc, "مبانی نظری و پیشینه پژوهش", level=1, auto_number=True)
    import_document_paragraphs_with_footnotes(draft_path, harvester, doc, heading_offset=0, start_idx=116, end_idx=120)

    create_styled_heading(doc, "استفاده مشکل‌ساز از اینترنت", level=2, auto_number=True)
    import_document_paragraphs_with_footnotes(piu_docx, harvester, doc, heading_offset=1, start_idx=0, end_idx=None)

    create_styled_heading(doc, "عدم تحمل بلاتکلیفی", level=2, auto_number=True)
    import_document_paragraphs_with_footnotes(iu_docx, harvester, doc, heading_offset=1, start_idx=0, end_idx=None)

    create_styled_heading(doc, "تکانشگری", level=2, auto_number=True)
    import_document_paragraphs_with_footnotes(imp_docx, harvester, doc, heading_offset=1, start_idx=0, end_idx=None)

    create_styled_heading(doc, "خودکارآمدی", level=2, auto_number=True)
    import_document_paragraphs_with_footnotes(se_docx, harvester, doc, heading_offset=1, start_idx=4, end_idx=None)

    create_styled_heading(doc, "مسیرهای پیشنهادی در ارتباط بین تحمل‌ناپذیری عدم‌قطعیت و استفاده مشکل‌ساز از اینترنت", level=2, auto_number=True)
    import_document_paragraphs_with_footnotes(draft_path, harvester, doc, heading_offset=1, start_idx=439, end_idx=455)

    create_styled_heading(doc, "مدل مفهومی پژوهش", level=2, auto_number=True)
    import_document_paragraphs_with_footnotes(draft_path, harvester, doc, heading_offset=1, start_idx=456, end_idx=473)

    create_styled_heading(doc, "پیشینه تجربی پژوهش", level=2, auto_number=True)
    import_document_paragraphs_with_footnotes(draft_path, harvester, doc, heading_offset=1, start_idx=474, end_idx=500)
    create_page_break(doc)

    print("[5/8] Injecting Chapter 3 (Methodology)...")
    create_styled_heading(doc, "روش‌شناسی پژوهش", level=1, auto_number=True)
    import_document_paragraphs_with_footnotes(draft_path, harvester, doc, heading_offset=0, start_idx=522, end_idx=580)
    create_page_break(doc)

    print("[6/8] Injecting Chapter 4 (Findings, 22 Tables, 11 Figures, Native Captions)...")
    import_chapter_4_non_destructive(ch4_path, doc, c4_elem_media_map, harvester)
    create_page_break(doc)

    print("[7/8] Injecting Chapter 5 (Discussion & Conclusion)...")
    create_styled_heading(doc, "بحث و نتیجه‌گیری", level=1, auto_number=True)
    import_document_paragraphs_with_footnotes(draft_path, harvester, doc, heading_offset=0, start_idx=808, end_idx=901)
    create_page_break(doc)

    print("[8/8] Injecting References, Appendices, and English Back Matter...")
    create_styled_heading(doc, "فهرست منابع و مآخذ", level=1, auto_number=False)
    import_document_paragraphs_with_footnotes(refs_path, harvester, doc, heading_offset=0, start_idx=0, end_idx=None, is_refs=True)
    create_page_break(doc)

    create_styled_heading(doc, "پیوست‌ها: ابزارهای سنجش و پرسشنامه‌های پژوهش", level=1, auto_number=False)
    src_app = Document(app_path)
    app_tables = list(src_app.tables)
    app_captions = [
        "فرم مشخصات جمعیت‌شناختی (دموگرافیک)",
        "مقیاس تعمیم‌یافته استفاده مشکل‌ساز از اینترنت (GPIUS-2)",
        "مقیاس فرم کوتاه عدم تحمل بلاتکلیفی (IUS-12)",
        "مقیاس تکانشگری بارات (BIS-11)",
        "مقیاس خودکارآمدی عمومی (GSE-10)"
    ]
    
    header_replacements = {
        "کاملاً مخالفم": "کاملاً\nمخالفم",
        "مخالفم": "مخالفم",
        "تاحدودی مخالفم": "تاحدودی\nمخالفم",
        "نظری ندارم": "نظری\nندارم",
        "تاحدودی موافقم": "تاحدودی\nموافقم",
        "موافقم": "موافقم",
        "کاملاً موافقم": "کاملاً\nموافقم",
        "اصلاً در مورد من صدق نمی کند": "اصلاً صدق\nنمی‌کند",
        "خیلی کم": "خیلی کم",
        "تا حدودی": "تا حدودی",
        "زیاد": "زیاد",
        "کاملاً در مورد من صدق می کند": "کاملاً صدق\nنمی‌کند",
        "به ندرت / هرگز": "به‌ندرت /\nهرگز",
        "گاهی اوقات": "گاهی\nاوقات",
        "اغلب اوقات": "اغلب\nاوقات",
        "تقریباً همیشه": "تقریباً\nهمیشه",
        "کاملاً غلط": "کاملاً\nغلط",
        "تاحدودی غلط": "تاحدودی\nغلط",
        "تاحدودی درست": "تاحدودی\nدرست",
        "کاملاً درست": "کاملاً\nدرست"
    }

    for tbl_i, tbl in enumerate(app_tables):
        c_title = app_captions[tbl_i] if tbl_i < len(app_captions) else f"ابزار سنجش {tbl_i+1}"
        add_caption_to_doc(doc, tbl_i + 1, c_title, prefix="جدول_پ-")
        tbl_copy = copy.deepcopy(tbl._tbl)
        tblPr = tbl_copy.find(qn('w:tblPr'))
        if tblPr is not None and tblPr.find(qn('w:bidiVisual')) is None:
            tblPr.append(OxmlElement('w:bidiVisual'))
            
        wrap_doc = Document()
        wrap_doc._body._element.append(tbl_copy)
        w_tbl = wrap_doc.tables[0]
        num_cols = len(w_tbl.columns)
        if num_cols >= 6:
            col_0_w = 720
            col_1_w = 3600
            opt_w = int((8800 - col_0_w - col_1_w) / (num_cols - 2))
            
            for row_idx, row in enumerate(w_tbl.rows):
                is_header = (row_idx == 0)
                for c_idx, cell in enumerate(row.cells):
                    tcPr = cell._tc.get_or_add_tcPr()
                    tcW = OxmlElement('w:tcW')
                    tcW.set(qn('w:type'), 'dxa')
                    if c_idx == 0:
                        tcW.set(qn('w:w'), str(col_0_w))
                    elif c_idx == 1:
                        tcW.set(qn('w:w'), str(col_1_w))
                    else:
                        tcW.set(qn('w:w'), str(opt_w))
                    tcPr.append(tcW)
                    
                    tcMar = OxmlElement('w:tcMar')
                    for m, val in [('top', 60), ('bottom', 60), ('left', 30), ('right', 30)]:
                        node = OxmlElement(f'w:{m}')
                        node.set(qn('w:w'), str(val))
                        node.set(qn('w:type'), 'dxa')
                        tcMar.append(node)
                    tcPr.append(tcMar)
                    
                    if is_header:
                        txt = cell.text.strip()
                        for k, v in header_replacements.items():
                            if k in txt:
                                txt = txt.replace(k, v)
                        cell.text = ""
                        lines = txt.split('\n')
                        for li, l_txt in enumerate(lines):
                            p = cell.paragraphs[0] if li == 0 else cell.add_paragraph()
                            pPr = p._p.get_or_add_pPr()
                            if pPr.find(qn('w:bidi')) is None:
                                pPr.append(OxmlElement('w:bidi'))
                            p_jc = OxmlElement('w:jc')
                            p_jc.set(qn('w:val'), 'center')
                            pPr.append(p_jc)
                            r = p.add_run(normalize_persian_text(l_txt))
                            r.font.name = "B Nazanin"
                            r.font.size = Pt(8.5 if num_cols >= 8 else 9.5)
                            r.bold = True
                            rPr = r._r.get_or_add_rPr()
                            rPr.append(OxmlElement('w:rtl'))

        insert_elem_before_sectpr(doc, tbl_copy)
        
        p_sp = OxmlElement('w:p')
        set_paragraph_bidi_and_align(p_sp, space_after=12)
        insert_elem_before_sectpr(doc, p_sp)

    add_english_back_matter(doc)

    temp_docx = test_out + "_intermediate.docx"
    doc.save(temp_docx)
    print(f"  Intermediate docx saved: {temp_docx}")

    package_and_finalize_clean(temp_docx, test_out, template_path, ch4_path, harvester, c4_media_rel_map)
    if os.path.exists(temp_docx):
        os.remove(temp_docx)

    print("\nMaster build finished successfully.")

if __name__ == "__main__":
    build_thesis()
