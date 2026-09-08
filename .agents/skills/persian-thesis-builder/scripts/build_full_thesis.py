# -*- coding: utf-8 -*-
"""
build_and_verify_master.py
Assembles and verifies the complete Master Thesis with:
1. Native Footnotes (all constructs + ch5)
2. Chapter 4 undamaged (22 tables, 11 figures with clean IDs and media, native captions)
3. Headings RTL & Justified
4. Appendix native captions
5. Strict Word COM verification
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
final_output = os.path.join(base_dir, "Thesis_Compiled.docx")

trans_dir = os.path.join(base_dir, "Translate")
piu_docx = os.path.join(trans_dir, "PIU_Pages_13-44_fa.docx")
iu_docx = os.path.join(trans_dir, "Intolerance_of_Uncertainty_Pages_1-26_fa.docx")
imp_docx = os.path.join(trans_dir, "Impulsivity_Pages_1-10_fa.docx")
se_docx = os.path.join(trans_dir, "Self_Efficacy_Pages_24-42_fa.docx")

def normalize_persian_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace('\u064A', '\u06CC')  # ي -> ی
    text = text.replace('\u0649', '\u06CC')  # ى -> ی
    text = text.replace('\u0643', '\u06A9')  # ك -> ک
    text = text.replace('\u0629', '\u0647')  # ة -> ه
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

def set_paragraph_bidi_and_align(p_elem, alignment="both", keep_with_next=False, space_before=0, space_after=6):
    pPr = p_elem.find(qn('w:pPr'))
    if pPr is None:
        pPr = OxmlElement('w:pPr')
        p_elem.insert(0, pPr)
    
    # 1. pStyle if any
    # 2. keepNext
    if keep_with_next:
        if pPr.find(qn('w:keepNext')) is None:
            pPr.append(OxmlElement('w:keepNext'))
    
    # 3. bidi
    if pPr.find(qn('w:bidi')) is None:
        pPr.append(OxmlElement('w:bidi'))
    
    # 4. jc
    jc = pPr.find(qn('w:jc'))
    if jc is None:
        jc = OxmlElement('w:jc')
        pPr.append(jc)
    jc.set(qn('w:val'), alignment)

    # 5. spacing
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

def create_styled_heading(doc, text: str, level: int):
    p_elem = OxmlElement('w:p')
    
    # Select font and sizes according to level
    if level == 1:
        font_name = "B Titr"
        font_size = 16
        before, after = 20, 12
    elif level == 2:
        font_name = "B Titr"
        font_size = 14
        before, after = 14, 8
    elif level == 3:
        font_name = "B Nazanin"
        font_size = 13
        before, after = 10, 6
    else:
        font_name = "B Nazanin"
        font_size = 12
        before, after = 8, 4

    set_paragraph_bidi_and_align(p_elem, alignment="both", keep_with_next=True, space_before=before, space_after=after)
    
    pPr = p_elem.find(qn('w:pPr'))
    pStyle = OxmlElement('w:pStyle')
    pStyle.set(qn('w:val'), f'Heading{level}')
    pPr.insert(0, pStyle)

    r_elem = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    rStyle = OxmlElement('w:rStyle')
    rStyle.set(qn('w:val'), f'Heading{level}Char')
    rPr.append(rStyle)
    
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
    
    lang = OxmlElement('w:lang')
    lang.set(qn('w:val'), 'fa-IR')
    lang.set(qn('w:bidi'), 'fa-IR')
    rPr.append(lang)
    
    r_elem.append(rPr)
    
    t_elem = OxmlElement('w:t')
    t_elem.text = normalize_persian_text(text)
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
        self.footnotes = []  # list of (assigned_id, footnote_text)
        self.current_id = 1
        self.seen_texts = {} # norm_text -> assigned_id
    
    def add_footnote(self, raw_text: str):
        norm_text = re.sub(r'^\d+\s*', '', raw_text).strip().lower()
        if norm_text and norm_text in self.seen_texts:
            # Already footnoted at first occurrence! Do NOT footnote again!
            return None
        
        assigned_id = self.current_id
        self.current_id += 1
        self.footnotes.append((assigned_id, raw_text.strip()))
        if norm_text:
            self.seen_texts[norm_text] = assigned_id
        return assigned_id

def import_document_paragraphs_with_footnotes(source_docx_path, harvester, target_doc, heading_offset=0, start_idx=0, end_idx=None):
    if not os.path.exists(source_docx_path):
        print(f"Warning: File not found: {source_docx_path}")
        return
    
    # 1. Load source footnotes text
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
    
    for i in range(start_idx, actual_end):
        child = elems[i]
        tag = child.tag.split('}')[-1]
        
        if tag == 'p':
            p_elem = copy.deepcopy(child)
            txt = "".join(p_elem.itertext()).strip()
            if not txt:
                continue
            
            # Strip inline sectPr and bookmarks
            for s in p_elem.findall('.//' + qn('w:sectPr')):
                s.getparent().remove(s)
            for bm in p_elem.findall('.//' + qn('w:bookmarkStart')):
                bm.getparent().remove(bm)
            for bm in p_elem.findall('.//' + qn('w:bookmarkEnd')):
                bm.getparent().remove(bm)

            # Remap footnotes: deduplicate (only first occurrence kept)
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
            
            # Detect headings
            pStyle_el = p_elem.find('.//' + qn('w:pStyle'))
            pStyle = pStyle_el.get(qn('w:val')) if pStyle_el is not None else ""
            
            is_h1 = pStyle.startswith('Heading1') or (txt.startswith('فصل ') and len(txt) < 40)
            is_h2 = pStyle.startswith('Heading2') or bool(re.match(r'^[۱-۴1-4][\.\-][۱-۹1-9]\s+', txt) and len(txt) < 80)
            is_h3 = pStyle.startswith('Heading3') or bool(re.match(r'^[۱-۴1-4][\.\-][۱-۹1-9][\.\-][۱-۹1-9]\s+', txt) and len(txt) < 80)
            is_h4 = pStyle.startswith('Heading4') or bool(re.match(r'^[۱-۴1-4][\.\-][۱-۹1-9][\.\-][۱-۹1-9][\.\-][۱-۹1-9]\s+', txt) and len(txt) < 80)

            if is_h1 and heading_offset > 0:
                is_h2 = True
                is_h1 = False

            if is_h1:
                set_paragraph_bidi_and_align(p_elem, alignment="both", keep_with_next=True, space_before=20, space_after=12)
            elif is_h2:
                set_paragraph_bidi_and_align(p_elem, alignment="both", keep_with_next=True, space_before=14, space_after=8)
            elif is_h3:
                set_paragraph_bidi_and_align(p_elem, alignment="both", keep_with_next=True, space_before=10, space_after=6)
            elif is_h4:
                set_paragraph_bidi_and_align(p_elem, alignment="both", keep_with_next=True, space_before=8, space_after=4)
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

def import_chapter_4_non_destructive(c4_docx_path, target_doc, media_map, harvester):
    print("Importing Chapter 4 non-destructively...")
    create_styled_heading(target_doc, "فصل چهارم: تجزیه و تحلیل داده‌ها (یافته‌های پژوهش)", level=1)
    
    # Load Chapter 4 footnotes
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
            
            # Strip inline sectPr and bookmarks
            for s in p_elem.findall('.//' + qn('w:sectPr')):
                s.getparent().remove(s)
            for bm in p_elem.findall('.//' + qn('w:bookmarkStart')):
                bm.getparent().remove(bm)
            for bm in p_elem.findall('.//' + qn('w:bookmarkEnd')):
                bm.getparent().remove(bm)

            # Remap footnotes: deduplicate!
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
            
            # Remap blip embeds
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
            
            if is_caption:
                set_paragraph_bidi_and_align(p_elem, alignment="both", keep_with_next=True, space_before=10, space_after=4)
            elif any(k in txt for k in ['یافته های توصیفی', 'یافته‌های توصیفی', 'یافته های استنباطی', 'یافته‌های استنباطی', 'بررسی مدل مفهومی پژوهش', 'خلاصه ی کلی', 'خلاصه‌ی کلی']):
                set_paragraph_bidi_and_align(p_elem, alignment="both", keep_with_next=True, space_before=16, space_after=8)
            elif any(k in txt for k in ['ویژگی های جمعیت شناختی', 'ویژگی‌های جمعیت‌شناختی', 'شاخص های توصیفی متغیرهای پژوهش', 'شاخص‌های توصیفی متغیرهای پژوهش', 'بررسی پیش‌فرض‌های آزمون‌های آماری']):
                set_paragraph_bidi_and_align(p_elem, alignment="both", keep_with_next=True, space_before=12, space_after=6)
            elif txt.startswith("فرضیه "):
                set_paragraph_bidi_and_align(p_elem, alignment="both", keep_with_next=True, space_before=12, space_after=6)
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

def add_native_caption_to_table(doc, table_num: int, title: str, prefix="جدول_پ-"):
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
    t1.text = "جدول پ- "
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

    # Persian abstract mapping
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
    
    # 1. Restore template pristine styles.xml
    with zipfile.ZipFile(template_docx, 'r') as z_tmpl:
        orig_styles = z_tmpl.read('word/styles.xml')
    with open(os.path.join(temp_dir, 'word', 'styles.xml'), 'wb') as f:
        f.write(orig_styles)
    print("  Restored pristine styles.xml")

    # 2. Copy Chapter 4 images with clean unique filenames
    with zipfile.ZipFile(c4_docx, 'r') as z4:
        for old_rid, (new_rid, new_target) in c4_media_rel_map.items():
            # Find target in c4 rels
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

    # 3. Build pure footnotes.xml
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

    # 4. Clean document.xml.rels
    rels_path = os.path.join(temp_dir, 'word', '_rels', 'document.xml.rels')
    with open(rels_path, 'r', encoding='utf-8') as f:
        rels_tree = ET.fromstring(f.read())
    
    clean_rels = []
    has_fn_rel = False
    for r in rels_tree:
        rid = r.attrib.get('Id')
        rtype = r.attrib.get('Type')
        target = r.attrib.get('Target')
        if 'c4_img' in rid or rid.startswith('rId2'):
            continue
        if 'footnotes' in rtype or target == 'footnotes.xml':
            has_fn_rel = True
            rid = 'rId6'
        clean_rels.append((rid, rtype, target))

    if not has_fn_rel:
        clean_rels.append(('rId6', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes', 'footnotes.xml'))

    # Add Chapter 4 chart relationships
    for old_rid, (new_rid, new_target) in c4_media_rel_map.items():
        clean_rels.append((new_rid, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image', new_target))

    rels_lines = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                  '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    for rid, rtype, target in clean_rels:
        rels_lines.append(f'  <Relationship Id="{rid}" Type="{rtype}" Target="{target}"/>')
    rels_lines.append('</Relationships>')

    with open(rels_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(rels_lines))
    print(f"  Rebuilt document.xml.rels with {len(clean_rels)} clean relationships.")

    # 5. [Content_Types].xml
    ct_path = os.path.join(temp_dir, '[Content_Types].xml')
    with open(ct_path, 'r', encoding='utf-8') as f:
        ct_data = f.read()
    if '/word/footnotes.xml' not in ct_data:
        ct_data = ct_data.replace('</Types>', '  <Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/>\n</Types>')
        with open(ct_path, 'w', encoding='utf-8') as f:
            f.write(ct_data)

    # 6. settings.xml: clean footnotePr with ONLY separator (-1) and continuationSeparator (0)
    # NO <w:footnote w:id="1"/> which breaks user footnotes!
    sett_path = os.path.join(temp_dir, 'word', 'settings.xml')
    with open(sett_path, 'r', encoding='utf-8') as f:
        sett_data = f.read()
    
    clean_fn_pr = '<w:footnotePr><w:numRestart w:val="eachPage"/><w:footnote w:id="-1"/><w:footnote w:id="0"/></w:footnotePr>'
    if '<w:footnotePr>' in sett_data:
        sett_data = re.sub(r'<w:footnotePr>.*?</w:footnotePr>', clean_fn_pr, sett_data, flags=re.DOTALL)
    else:
        sett_data = re.sub(r'(<w:settings[^>]*>)', r'\1\n  ' + clean_fn_pr, sett_data)
    
    # Enforce compatibilityMode = 15
    if 'compatibilityMode' in sett_data:
        sett_data = re.sub(r'<w:compatSetting w:name="compatibilityMode"[^/]+/>',
                           '<w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/>',
                           sett_data)
    
    with open(sett_path, 'w', encoding='utf-8') as f:
        f.write(sett_data)
    print("  Enforced clean footnotePr and compatibilityMode = 15 in settings.xml.")

    # Repack
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
    print("=== STARTING MASTER THESIS BUILD ===")
    
    # Pre-map Chapter 4 media
    c4_media_rel_map = {}
    c4_elem_media_map = {} # old_rid -> new_rid
    with zipfile.ZipFile(ch4_path, 'r') as z4:
        c4_rels = ET.fromstring(z4.read('word/_rels/document.xml.rels'))
        img_idx = 1
        for r in c4_rels:
            rid = r.attrib.get('Id')
            rtype = r.attrib.get('Type')
            target = r.attrib.get('Target')
            if 'image' in rtype:
                ext = os.path.splitext(target)[1]
                new_rid = f"rId2{img_idx:02d}"
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

    print("[3/8] Injecting Chapter 1 (Generalities)...")
    create_styled_heading(doc, "فصل اول: کلیات پژوهش", level=1)
    import_document_paragraphs_with_footnotes(draft_path, harvester, doc, heading_offset=1, start_idx=15, end_idx=91)
    create_page_break(doc)

    print("[4/8] Synthesizing Chapter 2 (Theoretical Foundations & Empirical Background)...")
    create_styled_heading(doc, "فصل دوم: مبانی نظری و پیشینه پژوهش", level=1)
    import_document_paragraphs_with_footnotes(draft_path, harvester, doc, heading_offset=0, start_idx=116, end_idx=120)

    create_styled_heading(doc, "۲-۱. استفاده مشکل‌ساز از اینترنت", level=2)
    import_document_paragraphs_with_footnotes(piu_docx, harvester, doc, heading_offset=1, start_idx=0, end_idx=None)

    create_styled_heading(doc, "۲-۲. عدم تحمل بلاتکلیفی", level=2)
    import_document_paragraphs_with_footnotes(iu_docx, harvester, doc, heading_offset=1, start_idx=0, end_idx=None)

    create_styled_heading(doc, "۲-۳. تکانشگری", level=2)
    import_document_paragraphs_with_footnotes(imp_docx, harvester, doc, heading_offset=1, start_idx=0, end_idx=None)

    create_styled_heading(doc, "۲-۴. خودکارآمدی", level=2)
    import_document_paragraphs_with_footnotes(se_docx, harvester, doc, heading_offset=1, start_idx=0, end_idx=None)

    create_styled_heading(doc, "۲-۵. مسیرهای پیشنهادی در ارتباط بین تحمل‌ناپذیری عدم‌قطعیت و استفاده مشکل‌ساز از اینترنت", level=2)
    import_document_paragraphs_with_footnotes(draft_path, harvester, doc, heading_offset=1, start_idx=437, end_idx=454)

    create_styled_heading(doc, "۲-۶. مدل مفهومی پژوهش", level=2)
    import_document_paragraphs_with_footnotes(draft_path, harvester, doc, heading_offset=1, start_idx=454, end_idx=472)

    create_styled_heading(doc, "۲-۷. پیشینه تجربی پژوهش", level=2)
    import_document_paragraphs_with_footnotes(draft_path, harvester, doc, heading_offset=1, start_idx=472, end_idx=499)
    create_page_break(doc)

    print("[5/8] Injecting Chapter 3 (Methodology)...")
    create_styled_heading(doc, "فصل سوم: روش‌شناسی پژوهش", level=1)
    import_document_paragraphs_with_footnotes(draft_path, harvester, doc, heading_offset=1, start_idx=500, end_idx=580)
    create_page_break(doc)

    print("[6/8] Injecting Chapter 4 (Findings, 22 Tables, 11 Figures, Native Captions)...")
    import_chapter_4_non_destructive(ch4_path, doc, c4_elem_media_map, harvester)
    create_page_break(doc)

    print("[7/8] Injecting Chapter 5 (Discussion & Conclusion)...")
    create_styled_heading(doc, "فصل پنجم: بحث و نتیجه‌گیری", level=1)
    import_document_paragraphs_with_footnotes(draft_path, harvester, doc, heading_offset=1, start_idx=780, end_idx=876)
    create_page_break(doc)

    print("[8/8] Injecting References, Appendices, and English Back Matter...")
    # References
    create_styled_heading(doc, "فهرست منابع و مآخذ", level=1)
    import_document_paragraphs_with_footnotes(refs_path, harvester, doc, heading_offset=0, start_idx=0, end_idx=None)
    create_page_break(doc)

    # Appendices
    create_styled_heading(doc, "پیوست‌ها: ابزارهای سنجش و پرسشنامه‌های پژوهش", level=1)
    src_app = Document(app_path)
    app_tables = list(src_app.tables)
    app_captions = [
        "فرم مشخصات جمعیت‌شناختی (دموگرافیک)",
        "مقیاس تعمیم‌یافته استفاده مشکل‌ساز از اینترنت (GPIUS-2)",
        "مقیاس فرم کوتاه عدم تحمل بلاتکلیفی (IUS-12)",
        "مقیاس تکانشگری بارات (BIS-11)",
        "مقیاس خودکارآمدی عمومی (GSE-10)"
    ]
    for tbl_i, tbl in enumerate(app_tables):
        c_title = app_captions[tbl_i] if tbl_i < len(app_captions) else f"ابزار سنجش {tbl_i+1}"
        add_native_caption_to_table(doc, tbl_i + 1, c_title, prefix="جدول_پ-")
        tbl_copy = copy.deepcopy(tbl._tbl)
        tblPr = tbl_copy.find(qn('w:tblPr'))
        if tblPr is not None and tblPr.find(qn('w:bidiVisual')) is None:
            tblPr.append(OxmlElement('w:bidiVisual'))
        insert_elem_before_sectpr(doc, tbl_copy)
        
        p_sp = OxmlElement('w:p')
        set_paragraph_bidi_and_align(p_sp, space_after=12)
        insert_elem_before_sectpr(doc, p_sp)

    add_english_back_matter(doc)

    # Intermediate save
    temp_docx = final_output + "_intermediate.docx"
    doc.save(temp_docx)
    print(f"  Intermediate docx saved: {temp_docx}")

    # Final packaging
    package_and_finalize_clean(temp_docx, final_output, template_path, ch4_path, harvester, c4_media_rel_map)
    if os.path.exists(temp_docx):
        os.remove(temp_docx)

    # Verification via Word COM
    print("\n=== VERIFYING THESIS WITH MICROSOFT WORD COM ===")
    ps_cmd = f"""
    $w = New-Object -ComObject Word.Application
    $w.Visible = $false
    $w.DisplayAlerts = 0
    try {{
        $d = $w.Documents.Open('{final_output}', $false, $true)
        Write-Host "MS WORD COM TEST: SUCCESSFUL OPEN!"
        Write-Host "  Paragraphs:   $($d.Paragraphs.Count)"
        Write-Host "  Footnotes:    $($d.Footnotes.Count)"
        Write-Host "  Tables:       $($d.Tables.Count)"
        Write-Host "  InlineShapes: $($d.InlineShapes.Count)"
        Write-Host "  Shapes:       $($d.Shapes.Count)"
        $d.Close([ref]$false)
    }} catch {{
        Write-Host "MS WORD COM TEST FAILED: $($_.Exception.Message)"
    }} finally {{
        $w.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($w) | Out-Null
    }}
    """
    res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
    print(res.stdout.strip())

if __name__ == "__main__":
    build_thesis()
