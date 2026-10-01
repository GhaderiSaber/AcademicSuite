#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/fix_chapter4_docx.py — Fixes OpenXML typography and table structure in Chapter 4 Results docx.
"""

import os
import sys
import zipfile
import shutil
import tempfile
import xml.etree.ElementTree as ET

NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
}
ET.register_namespace('w', NS['w'])

def clean_text(elem: ET.Element) -> str:
    texts = []
    for node in elem.iter():
        if node.tag.endswith('}t') and node.text:
            texts.append(node.text)
    return "".join(texts)

def fix_chapter4_docx(docx_path: str):
    if not os.path.exists(docx_path):
        print(f"Error: {docx_path} not found")
        return False

    temp_dir = tempfile.mkdtemp(prefix="docx_fix_")
    try:
        # Extract docx
        with zipfile.ZipFile(docx_path, 'r') as z:
            z.extractall(temp_dir)

        doc_xml_path = os.path.join(temp_dir, 'word', 'document.xml')
        if not os.path.exists(doc_xml_path):
            print("Error: word/document.xml not found")
            return False

        tree = ET.parse(doc_xml_path)
        root = tree.getroot()

        # 1. Fix Table bidiVisual order and English leakage
        tables = root.findall('.//w:tbl', NS)
        print(f"Found {len(tables)} tables")

        replacements = {
            'Constant': 'مقدار ثابت',
            'Adj': 'تعدیل‌شده',
            'Chi': 'خی',
            'Square': 'دو',
            'Skewness': 'چولگی',
            'Kurtosis': 'کشیدگی',
        }

        for idx, tbl in enumerate(tables, start=1):
            tblPr = tbl.find('w:tblPr', NS)
            if tblPr is not None:
                tbl_text = clean_text(tbl)
                has_persian = any('\u0600' <= c <= '\u06FF' for c in tbl_text)
                
                # Check bidiVisual
                bidi = tblPr.find('w:bidiVisual', NS)
                tblW = tblPr.find('w:tblW', NS)
                
                if has_persian:
                    if bidi is not None:
                        tblPr.remove(bidi)
                    else:
                        bidi = ET.Element(f"{{{NS['w']}}}bidiVisual")
                    
                    # Insert bidiVisual before tblW
                    if tblW is not None:
                        tblW_idx = list(tblPr).index(tblW)
                        tblPr.insert(tblW_idx, bidi)
                    else:
                        tblPr.insert(0, bidi)

            # Check cells for English leakage
            for tr in tbl.findall('.//w:tr', NS):
                for tc in tr.findall('w:tc', NS):
                    for t in tc.findall('.//w:t', NS):
                        if t.text:
                            txt = t.text
                            for eng, per in replacements.items():
                                if eng in txt:
                                    txt = txt.replace(eng, per)
                            t.text = txt

        # 2. Fix paragraph justification and bidi alignment inversion
        paragraphs = root.findall('.//w:p', NS)
        print(f"Found {len(paragraphs)} paragraphs")

        for p_idx, p in enumerate(paragraphs, start=1):
            p_text = clean_text(p).strip()
            if not p_text:
                continue

            has_persian = any('\u0600' <= c <= '\u06FF' for c in p_text)
            pPr = p.find('w:pPr', NS)
            if pPr is None:
                pPr = ET.Element(f"{{{NS['w']}}}pPr")
                p.insert(0, pPr)

            bidi = pPr.find('w:bidi', NS)
            jc = pPr.find('w:jc', NS)
            jc_val = jc.attrib.get(f"{{{NS['w']}}}val") if jc is not None else None

            # Substantive narrative Persian text (> 80 characters) MUST BE JUSTIFIED
            if has_persian and len(p_text) > 80:
                if jc is None:
                    jc = ET.Element(f"{{{NS['w']}}}jc", {f"{{{NS['w']}}}val": "both"})
                    pPr.append(jc)
                elif jc_val != 'both':
                    jc.attrib[f"{{{NS['w']}}}val"] = "both"

            # BiDi Alignment Inversion: Right-aligned headings under <w:bidi> must OMIT <w:jc>
            if bidi is not None and jc is not None:
                if jc.attrib.get(f"{{{NS['w']}}}val") == 'right':
                    pPr.remove(jc)

        # Save document.xml
        tree.write(doc_xml_path, xml_declaration=True, encoding='utf-8')

        # Re-pack docx
        backup_path = docx_path + ".bak"
        if not os.path.exists(backup_path):
            shutil.copy2(docx_path, backup_path)

        with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as z_out:
            for root_dir, _, files in os.walk(temp_dir):
                for f in files:
                    full_p = os.path.join(root_dir, f)
                    rel_p = os.path.relpath(full_p, temp_dir)
                    z_out.write(full_p, rel_p)

        print(f"Successfully fixed {docx_path}")
        return True
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "/home/saber-ghaderi/My Work/Mohtasham Valiyanpur/03_deliverables/Chapter_4_Results.docx"
    fix_chapter4_docx(target)
