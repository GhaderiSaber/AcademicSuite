# -*- coding: utf-8 -*-
"""
Global Helper Script for Persian Academic Translation (.docx)
Part of the 'persian-academic-translation' Antigravity Skill.

Generates Microsoft Word documents with:
- Right-to-Left (RTL) reading order (w:bidi in pPr) and Justified alignment (w:jc w:val="both")
- Consistent w:rtl on ALL text runs and footnote reference runs to prevent Bidi line breaking
- True native Word footnotes (w:footnoteReference & word/footnotes.xml)
- Persian numerals (۱، ۲، ۳...) in text and footnote citations
- Word 2013+ Modern Layout Mode (compatibilityMode = 15) to prevent legacy Compatibility Mode rendering bugs
- Standard Persian academic typography (B Nazanin / Tahoma, 13-14pt, 1.15 line spacing)
- Distinct bold headings & styled tables
"""

import os
import sys
import re
import shutil
import zipfile
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def set_paragraph_rtl(paragraph, justify=True):
    """Sets paragraph direction to Right-to-Left and defaults to Justified alignment."""
    pPr = paragraph._element.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    pPr.append(bidi)
    if justify:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    else:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT

def set_run_font(run, font_name="B Nazanin", font_size_pt=13, bold=False, italic=False, color_rgb=None):
    """
    Applies font, size, and CRITICAL w:rtl tag to ensure the run is recognized as RTL
    by Word's layout engine, preventing line breaks and run flipping around footnotes.
    """
    run.font.name = font_name
    run.font.size = Pt(font_size_pt)
    run.bold = bold
    run.italic = italic
    if color_rgb:
        run.font.color.rgb = RGBColor(*color_rgb)
    
    rPr = run._element.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)
    rPr.append(rFonts)

    # CRITICAL: Every Persian text run must have w:rtl to match footnote runs!
    rtl = OxmlElement('w:rtl')
    rPr.append(rtl)

    lang = OxmlElement('w:lang')
    lang.set(qn('w:val'), 'fa-IR')
    lang.set(qn('w:bidi'), 'fa-IR')
    rPr.append(lang)

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

def add_persian_paragraph_with_footnotes(doc, raw_text, default_font="B Nazanin", font_size_pt=13, space_after=6, justify=True):
    """
    Splits raw text on [^ID] markers, normalizes quote placement, and inserts native footnote references.
    Ensures seamless text flow across footnotes without artificial line breaks.
    """
    p = doc.add_paragraph()
    set_paragraph_rtl(p, justify=justify)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(space_after)

    # Normalize quotes around footnote tokens: «...[^15]» -> «...»[^15]
    clean_text = re.sub(r'«([^»\n]+)\[\^(\d+)\]»', r'«\1»[^\2]', raw_text)

    tokens = re.split(r'(\[\^\d+\])', clean_text)
    for token in tokens:
        if not token:
            continue
        m = re.match(r'\[\^(\d+)\]', token)
        if m:
            fn_id = int(m.group(1))
            add_native_footnote_reference(p, fn_id, font_name=default_font)
        else:
            # Parse markdown bold (**text**) and italic (*text*)
            md_pattern = re.compile(r'(\*\*[^*]+?\*\*|\*[^*]+?\*)')
            parts = md_pattern.split(token)
            for part in parts:
                if not part:
                    continue
                if part.startswith('**') and part.endswith('**') and len(part) >= 4:
                    run = p.add_run(part[2:-2])
                    set_run_font(run, font_name=default_font, font_size_pt=font_size_pt, bold=True)
                elif part.startswith('*') and part.endswith('*') and len(part) >= 2:
                    run = p.add_run(part[1:-1])
                    set_run_font(run, font_name=default_font, font_size_pt=font_size_pt, italic=True)
                else:
                    run = p.add_run(part)
                    set_run_font(run, font_name=default_font, font_size_pt=font_size_pt)
    return p

def add_persian_markdown_table(doc, md_lines, caption=None):
    """
    Converts raw markdown table lines (| Col 1 | Col 2 |) into a native Word APA table (<w:tbl>)
    with shaded headers, cell borders, centered text, and full RTL layout.
    """
    rows_data = []
    for line in md_lines:
        line = line.strip()
        if not line or not line.startswith('|'):
            continue
        if re.match(r'^\|[\s\-:|]+\|$', line):
            continue
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if cells:
            rows_data.append(cells)
    
    if not rows_data:
        return None

    if caption:
        p_cap = doc.add_paragraph()
        set_paragraph_rtl(p_cap, justify=False)
        p_cap.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_cap.paragraph_format.space_before = Pt(12)
        p_cap.paragraph_format.space_after = Pt(4)
        run_cap = p_cap.add_run(caption)
        set_run_font(run_cap, font_name="B Nazanin", font_size_pt=11, bold=True)

    num_rows = len(rows_data)
    num_cols = max(len(r) for r in rows_data)
    tbl = doc.add_table(rows=num_rows, cols=num_cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    tblPr = tbl._tbl.tblPr
    if tblPr.find(qn('w:bidiVisual')) is None:
        tblPr.append(OxmlElement('w:bidiVisual'))

    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        '  <w:top w:val="single" w:sz="8" w:space="0" w:color="2B4C7E"/>\n'
        '  <w:bottom w:val="single" w:sz="8" w:space="0" w:color="2B4C7E"/>\n'
        '  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="D3D3D3"/>\n'
        '  <w:insideV w:val="none"/>\n'
        '  <w:left w:val="none"/>\n'
        '  <w:right w:val="none"/>\n'
        '</w:tblBorders>'
    )
    tblPr.append(tblBorders)

    for r_idx, row_data in enumerate(rows_data):
        row = tbl.rows[r_idx]
        is_header = (r_idx == 0)
        for c_idx, cell_text in enumerate(row_data):
            if c_idx < len(row.cells):
                cell = row.cells[c_idx]
                cell.text = cell_text
                tcPr = cell._tc.get_or_add_tcPr()
                if is_header:
                    shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="EBF1F5"/>')
                    tcPr.append(shd)
                
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                pPr = p._p.get_or_add_pPr()
                if pPr.find(qn('w:bidi')) is None:
                    pPr.append(OxmlElement('w:bidi'))
                for r in p.runs:
                    set_run_font(r, font_name="B Nazanin", font_size_pt=10, bold=is_header)

    p_sp = doc.add_paragraph()
    set_paragraph_rtl(p_sp, justify=False)
    p_sp.paragraph_format.space_after = Pt(12)
    return tbl

def pack_native_footnotes(base_docx_path, output_docx_path, footnotes_list):
    """
    Injects word/footnotes.xml and sets compatibilityMode = 15 in word/settings.xml.
    footnotes_list: list of tuples (id: int, latin_text: str)
    """
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
        safe_latin = latin.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
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
        set_data = re.sub(r'<w:compatSetting w:name="compatibilityMode"[^/]+/>', '<w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/>', set_data)
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(set_data)

    # 6. Re-pack into output docx (with fallback if locked)
    out_dir = os.path.dirname(output_docx_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    saved_path = output_docx_path
    try:
        if os.path.exists(output_docx_path):
            os.remove(output_docx_path)
        with zipfile.ZipFile(output_docx_path, 'w', zipfile.ZIP_DEFLATED) as z_out:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    full_f = os.path.join(root, file)
                    rel_f = os.path.relpath(full_f, temp_dir)
                    z_out.write(full_f, rel_f)
    except PermissionError:
        saved_path = output_docx_path.replace(".docx", "_fixed.docx")
        with zipfile.ZipFile(saved_path, 'w', zipfile.ZIP_DEFLATED) as z_out:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    full_f = os.path.join(root, file)
                    rel_f = os.path.relpath(full_f, temp_dir)
                    z_out.write(full_f, rel_f)
        print(f"Target docx was locked by Word. Saved to: {saved_path}")

    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"Native footnote Word document created: {saved_path}")
    return saved_path

if __name__ == "__main__":
    print("create_persian_docx.py ready.")
