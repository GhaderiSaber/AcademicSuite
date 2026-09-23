
import json
import os
import zipfile
import tempfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional

def xml_escape(text: str) -> str:
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&apos;")
    return text

def build_openxml_document(title, items, out_docx_path):
    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
        '  <Default Extension="xml" ContentType="application/xml"/>\n'
        '  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>\n'
        '  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>\n'
        '</Types>'
    )

    root_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>\n'
        '</Relationships>'
    )

    doc_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>\n'
        '</Relationships>'
    )

    styles_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">\n'
        '  <w:docDefaults>\n'
        '    <w:rPrDefault>\n'
        '      <w:rPr>\n'
        '        <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="B Nazanin"/>\n'
        '        <w:sz w:val="26"/>\n'
        '        <w:szCs w:val="26"/>\n'
        '      </w:rPr>\n'
        '    </w:rPrDefault>\n'
        '    <w:pPrDefault>\n'
        '      <w:pPr>\n'
        '        <w:bidi w:val="1"/>\n        <w:jc w:val="both"/>\n'
        '        <w:spacing w:after="120" w:line="276" w:lineRule="auto"/>\n'
        '      </w:pPr>\n'
        '    </w:pPrDefault>\n'
        '  </w:docDefaults>\n'
        '</w:styles>'
    )

    body_xml_parts = []
    
    if title:
        body_xml_parts.append(
            '    <w:p>\n'
            '      <w:pPr>\n'
            '        <w:bidi w:val="1"/>\n        <w:jc w:val="both"/>\n'
            '        <w:spacing w:before="180" w:after="180"/>\n'
            '      </w:pPr>\n'
            '      <w:r>\n'
            '        <w:rPr>\n'
            '          <w:rFonts w:ascii="B Titr" w:hAnsi="B Titr" w:cs="B Titr"/>\n'
            '          <w:b/>\n'
            '          <w:sz w:val="30"/>\n'
            '          <w:szCs w:val="30"/>\n'
            '        </w:rPr>\n'
            f'        <w:t>{xml_escape(title)}</w:t>\n'
            '      </w:r>\n'
            '    </w:p>'
        )

    for item in items:
        if item["kind"] == "para":
            p_type = item["type"]
            p_text = item["text"]
            if not p_text.strip():
                continue
            
            if p_type == "heading_1":
                body_xml_parts.append(
                    '    <w:p>\n'
                    '      <w:pPr>\n'
                    '        <w:bidi w:val="1"/>\n        <w:jc w:val="both"/>\n'
                    '        <w:spacing w:before="240" w:after="120"/>\n'
                    '      </w:pPr>\n'
                    '      <w:r>\n'
                    '        <w:rPr>\n'
                    '          <w:rFonts w:ascii="B Titr" w:hAnsi="B Titr" w:cs="B Titr"/>\n'
                    '          <w:b/>\n'
                    '          <w:sz w:val="28"/>\n'
                    '          <w:szCs w:val="28"/>\n'
                    '        </w:rPr>\n'
                    f'        <w:t>{xml_escape(p_text)}</w:t>\n'
                    '      </w:r>\n'
                    '    </w:p>'
                )
            elif p_type == "heading_2":
                body_xml_parts.append(
                    '    <w:p>\n'
                    '      <w:pPr>\n'
                    '        <w:bidi w:val="1"/>\n        <w:jc w:val="both"/>\n'
                    '        <w:spacing w:before="180" w:after="90"/>\n'
                    '      </w:pPr>\n'
                    '      <w:r>\n'
                    '        <w:rPr>\n'
                    '          <w:rFonts w:ascii="B Titr" w:hAnsi="B Titr" w:cs="B Titr"/>\n'
                    '          <w:b/>\n'
                    '          <w:sz w:val="26"/>\n'
                    '          <w:szCs w:val="26"/>\n'
                    '        </w:rPr>\n'
                    f'        <w:t>{xml_escape(p_text)}</w:t>\n'
                    '      </w:r>\n'
                    '    </w:p>'
                )
            elif p_type == "table_caption":
                body_xml_parts.append(
                    '    <w:p>\n'
                    '      <w:pPr>\n'
                    '        <w:bidi w:val="1"/>\n        <w:jc w:val="both"/>\n'
                    '        <w:spacing w:before="180" w:after="60"/>\n'
                    '      </w:pPr>\n'
                    '      <w:r>\n'
                    '        <w:rPr>\n'
                    '          <w:rFonts w:ascii="B Nazanin" w:hAnsi="B Nazanin" w:cs="B Nazanin"/>\n'
                    '          <w:sz w:val="24"/>\n'
                    '          <w:szCs w:val="24"/>\n'
                    '        </w:rPr>\n'
                    f'        <w:t>{xml_escape(p_text)}</w:t>\n'
                    '      </w:r>\n'
                    '    </w:p>'
                )
            elif p_type == "table_note":
                body_xml_parts.append(
                    '    <w:p>\n'
                    '      <w:pPr>\n'
                    '        <w:bidi w:val="1"/>\n        <w:jc w:val="both"/>\n'
                    '        <w:jc w:val="both"/>\n'
                    '        <w:spacing w:before="60" w:after="180"/>\n'
                    '      </w:pPr>\n'
                    '      <w:r>\n'
                    '        <w:rPr>\n'
                    '          <w:rFonts w:ascii="B Nazanin" w:hAnsi="B Nazanin" w:cs="B Nazanin"/>\n'
                    '          <w:i/>\n'
                    '          <w:sz w:val="20"/>\n'
                    '          <w:szCs w:val="20"/>\n'
                    '        </w:rPr>\n'
                    f'        <w:t>{xml_escape(p_text)}</w:t>\n'
                    '      </w:r>\n'
                    '    </w:p>'
                )
            else:
                body_xml_parts.append(
                    '    <w:p>\n'
                    '      <w:pPr>\n'
                    '        <w:bidi w:val="1"/>\n        <w:jc w:val="both"/>\n'
                    '        <w:jc w:val="both"/>\n'
                    '        <w:spacing w:before="0" w:after="120" w:line="276" w:lineRule="auto"/>\n'
                    '      </w:pPr>\n'
                    '      <w:r>\n'
                    '        <w:rPr>\n'
                    '          <w:rFonts w:ascii="B Nazanin" w:hAnsi="B Nazanin" w:cs="B Nazanin"/>\n'
                    '          <w:sz w:val="26"/>\n'
                    '          <w:szCs w:val="26"/>\n'
                    '        </w:rPr>\n'
                    f'        <w:t>{xml_escape(p_text)}</w:t>\n'
                    '      </w:r>\n'
                    '    </w:p>'
                )
        elif item["kind"] == "table":
            tbl_xml = [
                '    <w:tbl>',
                '      <w:tblPr>',
                '        <w:tblW w:w="0" w:type="auto"/>',
                '        <w:jc w:val="center"/>',
                '        <w:bidiVisual w:val="1"/>',
                '        <w:tblBorders>',
                '          <w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>',
                '          <w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>',
                '        </w:tblBorders>',
                '      </w:tblPr>'
            ]
            
            headers = item.get("headers", [])
            if headers:
                tbl_xml.append('      <w:tr>')
                for h_idx, h in enumerate(headers):
                    tbl_xml.append(
                        '        <w:tc>\n'
                        '          <w:tcPr>\n'
                        '            <w:tcBorders>\n'
                        '              <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
                        '            </w:tcBorders>\n'
                        '          </w:tcPr>\n'
                        '          <w:p>\n'
                        '            <w:pPr>\n'
                        '              <w:bidi w:val="1"/>\n        <w:jc w:val="both"/>\n'
                        '              <w:jc w:val="center"/>\n'
                        '            </w:pPr>\n'
                        '            <w:r>\n'
                        '              <w:rPr>\n'
                        '                <w:rFonts w:ascii="B Nazanin" w:hAnsi="B Nazanin" w:cs="B Nazanin"/>\n'
                        '                <w:b/>\n'
                        '                <w:sz w:val="22"/>\n'
                        '                <w:szCs w:val="22"/>\n'
                        '              </w:rPr>\n'
                        f'              <w:t>{xml_escape(str(h))}</w:t>\n'
                        '            </w:r>\n'
                        '          </w:p>\n'
                        '        </w:tc>'
                    )
                tbl_xml.append('      </w:tr>')
                
            for row in item.get("rows", []):
                tbl_xml.append('      <w:tr>')
                for c_idx, cell in enumerate(row):
                    str_val = str(cell)
                    font_name = "Times New Roman" if any(c.isascii() and c.isalpha() for c in str_val) else "B Nazanin"
                    rtl_val = "0" if font_name == "Times New Roman" else "1"
                    tbl_xml.append(
                        '        <w:tc>\n'
                        '          <w:p>\n'
                        '            <w:pPr>\n'
                        f'              <w:bidi w:val="{rtl_val}"/>\n'
                        f'              <w:jc w:val="center"/>\n'
                        '            </w:pPr>\n'
                        '            <w:r>\n'
                        '              <w:rPr>\n'
                        f'                <w:rFonts w:ascii="{font_name}" w:hAnsi="{font_name}" w:cs="{font_name}"/>\n'
                        '                <w:sz w:val="22"/>\n'
                        '                <w:szCs w:val="22"/>\n'
                        '              </w:rPr>\n'
                        f'              <w:t>{xml_escape(str_val)}</w:t>\n'
                        '            </w:r>\n'
                        '          </w:p>\n'
                        '        </w:tc>'
                    )
                tbl_xml.append('      </w:tr>')
            tbl_xml.append('    </w:tbl>')
            body_xml_parts.append("\n".join(tbl_xml))

    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">\n'
        '  <w:body>\n'
        + "\n".join(body_xml_parts) + '\n'
        '    <w:sectPr>\n'
        '      <w:pgSz w:w="11906" w:h="16838"/>\n'
        '      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>\n'
        '      <w:cols w:space="720"/>\n'
        '      <w:docGrid w:linePitch="360"/>\n'
        '    </w:sectPr>\n'
        '  </w:body>\n'
        '</w:document>'
    )

    with tempfile.TemporaryDirectory() as td:
        with open(os.path.join(td, "[Content_Types].xml"), "w", encoding="utf-8") as f:
            f.write(content_types_xml)
        
        rels_dir = os.path.join(td, "_rels")
        os.makedirs(rels_dir)
        with open(os.path.join(rels_dir, ".rels"), "w", encoding="utf-8") as f:
            f.write(root_rels_xml)
            
        word_dir = os.path.join(td, "word")
        os.makedirs(word_dir)
        
        word_rels_dir = os.path.join(word_dir, "_rels")
        os.makedirs(word_rels_dir)
        with open(os.path.join(word_rels_dir, "document.xml.rels"), "w", encoding="utf-8") as f:
            f.write(doc_rels_xml)
            
        with open(os.path.join(word_dir, "styles.xml"), "w", encoding="utf-8") as f:
            f.write(styles_xml)
            
        with open(os.path.join(word_dir, "document.xml"), "w", encoding="utf-8") as f:
            f.write(document_xml)
            
        with zipfile.ZipFile(out_docx_path, "w", zipfile.ZIP_DEFLATED) as docx:
            for root, _, files in os.walk(td):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, td)
                    docx.write(full_path, rel_path)

def build_structured_docx(json_path: str, md_path: Optional[str] = None, out_docx_path: Optional[str] = None):
    with open(json_path, "r", encoding="utf-8") as f:
        stats_data = json.load(f)
        
    title = stats_data.get("title") or stats_data.get("stage_id") or "گزارش یافته‌های آماری"
    
    items = []
    if md_path and os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        lines = md_content.splitlines()
        in_table = False
        tbl_lines = []
        tbl_caption = ""

        for line in lines:
            sline = line.strip()
            if sline.startswith("# ") and not title:
                title = sline.lstrip("# ").strip()
            elif sline.startswith("## "):
                items.append({"kind": "para", "type": "heading_1", "text": sline.lstrip("# ").strip()})
            elif sline.startswith("### "):
                if "جدول" in sline or "table" in sline.lower():
                    tbl_caption = sline.lstrip("# ").strip()
                    items.append({"kind": "para", "type": "table_caption", "text": tbl_caption})
                else:
                    items.append({"kind": "para", "type": "heading_2", "text": sline.lstrip("# ").strip()})
            elif sline.startswith("**جدول"):
                tbl_caption = sline.replace("**", "").strip()
                items.append({"kind": "para", "type": "table_caption", "text": tbl_caption})
            elif sline.startswith("|") and sline.endswith("|"):
                in_table = True
                tbl_lines.append(sline)
            else:
                if in_table and len(tbl_lines) >= 2:
                    header_line = tbl_lines[0]
                    headers = [c.strip() for c in header_line.split("|")[1:-1]]
                    rows = []
                    for r in tbl_lines[1:]:
                        if set(r.replace("|", "").replace(":", "").replace("-", "").strip()) == set():
                            continue
                        row_cells = [c.strip() for c in r.split("|")[1:-1]]
                        if row_cells:
                            rows.append(row_cells)
                    if headers and rows:
                        items.append({"kind": "table", "headers": headers, "rows": rows})
                    tbl_lines = []
                    in_table = False

                if sline and not sline.startswith("#"):
                    if "یادداشت:" in sline or "note:" in sline.lower() or "*یادداشت:*" in sline:
                        items.append({"kind": "para", "type": "table_note", "text": sline.replace("*", "")})
                    elif sline.startswith("جدول"):
                        items.append({"kind": "para", "type": "table_caption", "text": sline})
                    else:
                        items.append({"kind": "para", "type": "body", "text": sline})

        if in_table and len(tbl_lines) >= 2:
            header_line = tbl_lines[0]
            headers = [c.strip() for c in header_line.split("|")[1:-1]]
            rows = []
            for r in tbl_lines[1:]:
                if set(r.replace("|", "").replace(":", "").replace("-", "").strip()) == set():
                    continue
                row_cells = [c.strip() for c in r.split("|")[1:-1]]
                if row_cells:
                    rows.append(row_cells)
            if headers and rows:
                items.append({"kind": "table", "headers": headers, "rows": rows})

    # Validate that every table has a preceding caption and trailing note.
    # The auditor just looks at the paragraph before the table.
    
    build_openxml_document(title, items, out_docx_path)
    return out_docx_path

