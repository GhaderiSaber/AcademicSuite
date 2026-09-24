#!/usr/bin/env python3
"""
inject_openxml_footnotes.py — Standardized Native OpenXML Word Footnote Injector & Verifier.

Converts markdown-style footnote markers ([^1], [^2], ...) inside a Word .docx document
into genuine native OpenXML footnotes (word/footnotes.xml, [Content_Types].xml,
word/_rels/document.xml.rels, and styles.xml) via structured DOM ElementTree parsing.

Enforces:
- Zero Regex on minified document.xml (DOM Parsing Invariant)
- Persian typography standards (B Nazanin reference, Times New Roman Latin terms)
- Verification check on paragraph retention (prevents document body obliteration)
- Automatic SHA-256 updating of stage triad .json metadata
"""

import sys
import os
import shutil
import zipfile
import hashlib
import json
import re
import copy
import argparse
import xml.etree.ElementTree as ET
from typing import List, Tuple, Dict, Any, Optional

NAMESPACES = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
}
ET.register_namespace('w', NAMESPACES['w'])
ET.register_namespace('r', NAMESPACES['r'])


class OpenXMLFootnoteInjector:
    """Standardized native OpenXML footnote injector and verifier."""

    @staticmethod
    def extract_footnotes_from_markdown(md_path: str) -> List[Tuple[int, str]]:
        """Extract [^N]: Text definitions from a Markdown document."""
        if not os.path.exists(md_path):
            raise FileNotFoundError(f"Markdown file not found: {md_path}")

        footnotes = []
        with open(md_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        pattern = re.compile(r'^\[\^(\d+)\]:\s*(.+)$')
        for line in lines:
            m = pattern.match(line.strip())
            if m:
                fn_id = int(m.group(1))
                fn_text = m.group(2).strip()
                footnotes.append((fn_id, fn_text))

        # Sort by footnote ID
        footnotes.sort(key=lambda x: x[0])
        return footnotes

    @staticmethod
    def extract_footnotes_from_json(json_path: str) -> List[Tuple[int, str]]:
        """Extract footnotes from a JSON file (list of dicts, list of tuples, or dict of id->text)."""
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        footnotes = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    fn_id = int(item.get('id', item.get('index', 0)))
                    fn_text = item.get('text', item.get('latin', item.get('content', ''))).strip()
                    footnotes.append((fn_id, fn_text))
                elif isinstance(item, (list, tuple)) and len(item) >= 2:
                    footnotes.append((int(item[0]), str(item[1]).strip()))
        elif isinstance(data, dict):
            # Check if there is a 'footnotes' key
            fn_dict = data.get('footnotes', data)
            if isinstance(fn_dict, dict):
                for k, v in fn_dict.items():
                    if str(k).isdigit():
                        footnotes.append((int(k), str(v).strip()))
                    elif isinstance(v, dict) and 'id' in v:
                        footnotes.append((int(v['id']), str(v.get('text', '')).strip()))

        footnotes.sort(key=lambda x: x[0])
        return footnotes

    @classmethod
    def inject(cls,
               docx_path: str,
               footnotes: List[Tuple[int, str]],
               output_docx_path: Optional[str] = None,
               update_json_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Injects native OpenXML footnotes into docx_path and writes to output_docx_path.
        If output_docx_path is None, updates docx_path in-place atomically.
        """
        if not os.path.exists(docx_path):
            raise FileNotFoundError(f"DOCX file not found: {docx_path}")

        if not footnotes:
            raise ValueError("No footnotes provided for injection.")

        target_out = output_docx_path or docx_path
        temp_dir = f"{docx_path}_dom_fn_tmp"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

        try:
            with zipfile.ZipFile(docx_path, 'r') as z_in:
                z_in.extractall(temp_dir)

            doc_xml_file = os.path.join(temp_dir, "word", "document.xml")
            if not os.path.exists(doc_xml_file):
                raise RuntimeError("Invalid DOCX: missing word/document.xml")

            tree = ET.parse(doc_xml_file)
            root = tree.getroot()
            body = root.find('w:body', NAMESPACES)
            if body is None:
                raise RuntimeError("Invalid DOCX: missing w:body in document.xml")

            # 1. Clean up trailing footnote definitions (e.g. paragraphs starting with [^N]:)
            fn_ids_set = {str(fn[0]) for fn in footnotes}
            for p in list(body.findall('w:p', NAMESPACES)):
                p_text = "".join(node.text for node in p.findall('.//w:t', NAMESPACES) if node.text)
                if re.match(r'^\[\^\d+\]:', p_text.strip()):
                    body.remove(p)

            # Verify body still has paragraphs
            remaining_paragraphs = body.findall('w:p', NAMESPACES)
            if not remaining_paragraphs:
                raise RuntimeError("CRITICAL ERROR: Zero body paragraphs remain after footnote cleanup.")

            # 2. Replace [^N] occurrences with native OpenXML footnote references
            replaced_count = 0
            for p in remaining_paragraphs:
                runs = list(p)
                new_runs = []
                p_modified = False

                for r_node in runs:
                    if r_node.tag != f"{{{NAMESPACES['w']}}}r":
                        new_runs.append(r_node)
                        continue

                    t_nodes = r_node.findall('w:t', NAMESPACES)
                    if not t_nodes:
                        new_runs.append(r_node)
                        continue

                    r_text = "".join(t.text for t in t_nodes if t.text)
                    matches = list(re.finditer(r'\[\^(\d+)\]', r_text))
                    if not matches:
                        new_runs.append(r_node)
                        continue

                    p_modified = True
                    rPr = r_node.find('w:rPr', NAMESPACES)
                    last_idx = 0

                    for match in matches:
                        fn_id = match.group(1)
                        start_idx = match.start()
                        end_idx = match.end()

                        # Text before marker
                        if start_idx > last_idx:
                            txt_before = r_text[last_idx:start_idx]
                            r_before = ET.Element(f"{{{NAMESPACES['w']}}}r")
                            if rPr is not None:
                                r_before.append(copy.deepcopy(rPr))
                            t_before = ET.SubElement(r_before, f"{{{NAMESPACES['w']}}}t")
                            t_before.text = txt_before
                            if " " in txt_before:
                                t_before.set("xml:space", "preserve")
                            new_runs.append(r_before)

                        # Footnote reference run
                        r_fn = ET.Element(f"{{{NAMESPACES['w']}}}r")
                        rPr_fn = ET.SubElement(r_fn, f"{{{NAMESPACES['w']}}}rPr")

                        rStyle = ET.SubElement(rPr_fn, f"{{{NAMESPACES['w']}}}rStyle")
                        rStyle.set(f"{{{NAMESPACES['w']}}}val", "FootnoteReference")

                        rFonts = ET.SubElement(rPr_fn, f"{{{NAMESPACES['w']}}}rFonts")
                        rFonts.set(f"{{{NAMESPACES['w']}}}ascii", "B Nazanin")
                        rFonts.set(f"{{{NAMESPACES['w']}}}hAnsi", "B Nazanin")
                        rFonts.set(f"{{{NAMESPACES['w']}}}cs", "B Nazanin")

                        vertAlign = ET.SubElement(rPr_fn, f"{{{NAMESPACES['w']}}}vertAlign")
                        vertAlign.set(f"{{{NAMESPACES['w']}}}val", "superscript")

                        rtl = ET.SubElement(rPr_fn, f"{{{NAMESPACES['w']}}}rtl")

                        fnRef = ET.SubElement(r_fn, f"{{{NAMESPACES['w']}}}footnoteReference")
                        fnRef.set(f"{{{NAMESPACES['w']}}}id", fn_id)

                        new_runs.append(r_fn)
                        replaced_count += 1
                        last_idx = end_idx

                    # Text after marker
                    if last_idx < len(r_text):
                        txt_after = r_text[last_idx:]
                        r_after = ET.Element(f"{{{NAMESPACES['w']}}}r")
                        if rPr is not None:
                            r_after.append(copy.deepcopy(rPr))
                        t_after = ET.SubElement(r_after, f"{{{NAMESPACES['w']}}}t")
                        t_after.text = txt_after
                        if " " in txt_after:
                            t_after.set("xml:space", "preserve")
                        new_runs.append(r_after)

                if p_modified:
                    pPr = p.find('w:pPr', NAMESPACES)
                    p.clear()
                    if pPr is not None:
                        p.append(pPr)
                    for nr in new_runs:
                        p.append(nr)

            tree.write(doc_xml_file, encoding='utf-8', xml_declaration=True)

            # 3. Update [Content_Types].xml
            ct_file = os.path.join(temp_dir, "[Content_Types].xml")
            with open(ct_file, 'r', encoding='utf-8') as f:
                ct_data = f.read()
            if '/word/footnotes.xml' not in ct_data:
                ct_override = '  <Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/>\n</Types>'
                ct_data = ct_data.replace('</Types>', ct_override)
                with open(ct_file, 'w', encoding='utf-8') as f:
                    f.write(ct_data)

            # 4. Update word/_rels/document.xml.rels
            rels_file = os.path.join(temp_dir, "word", "_rels", "document.xml.rels")
            with open(rels_file, 'r', encoding='utf-8') as f:
                rels_data = f.read()
            if 'footnotes.xml' not in rels_data:
                rel_entry = '  <Relationship Id="rIdFootnotes" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes" Target="footnotes.xml"/>\n</Relationships>'
                rels_data = rels_data.replace('</Relationships>', rel_entry)
                with open(rels_file, 'w', encoding='utf-8') as f:
                    f.write(rels_data)

            # 5. Update styles.xml for FootnoteReference style
            styles_file = os.path.join(temp_dir, "word", "styles.xml")
            if os.path.exists(styles_file):
                with open(styles_file, 'r', encoding='utf-8') as f:
                    styles_data = f.read()
                if 'w:styleId="FootnoteReference"' not in styles_data:
                    fn_style = (
                        '  <w:style w:type="character" w:styleId="FootnoteReference">\n'
                        '    <w:name w:val="footnote reference"/>\n'
                        '    <w:basedOn w:val="DefaultParagraphFont"/>\n'
                        '    <w:uiPriority w:val="99"/>\n'
                        '    <w:semiHidden/>\n'
                        '    <w:unhideWhenUsed/>\n'
                        '    <w:rPr>\n'
                        '      <w:rFonts w:ascii="B Nazanin" w:hAnsi="B Nazanin" w:cs="B Nazanin"/>\n'
                        '      <w:vertAlign w:val="superscript"/>\n'
                        '      <w:rtl/>\n'
                        '      <w:lang w:val="fa-IR" w:bidi="fa-IR"/>\n'
                        '    </w:rPr>\n'
                        '  </w:style>\n'
                        '</w:styles>'
                    )
                    styles_data = styles_data.replace('</w:styles>', fn_style)
                    with open(styles_file, 'w', encoding='utf-8') as f:
                        f.write(styles_data)

            # 6. Generate word/footnotes.xml
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

            for idx, text_val in footnotes:
                safe_val = text_val.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                fn_lines.append(f'  <w:footnote w:id="{idx}">')
                fn_lines.append('    <w:p>')
                fn_lines.append('      <w:pPr>')
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
                fn_lines.append('          <w:sz w:val="20"/>')
                fn_lines.append('          <w:szCs w:val="20"/>')
                fn_lines.append('        </w:rPr>')
                fn_lines.append(f'        <w:t xml:space="preserve"> {safe_val}</w:t>')
                fn_lines.append('      </w:r>')
                fn_lines.append('    </w:p>')
                fn_lines.append('  </w:footnote>')

            fn_lines.append('</w:footnotes>')
            fn_xml_content = "\n".join(fn_lines)

            with open(os.path.join(temp_dir, "word", "footnotes.xml"), 'w', encoding='utf-8') as f:
                f.write(fn_xml_content)

            # 7. Repack Zip
            tmp_out_docx = target_out + ".tmp.docx"
            if os.path.exists(tmp_out_docx):
                os.remove(tmp_out_docx)

            with zipfile.ZipFile(tmp_out_docx, 'w', zipfile.ZIP_DEFLATED) as z_out:
                for root_dir, _, files in os.walk(temp_dir):
                    for file in files:
                        full_f = os.path.join(root_dir, file)
                        rel_f = os.path.relpath(full_f, temp_dir)
                        z_out.write(full_f, rel_f)

            if os.path.exists(target_out):
                os.remove(target_out)
            os.rename(tmp_out_docx, target_out)

            # 8. Compute sha256 hash
            with open(target_out, "rb") as f:
                sha256_hash = hashlib.sha256(f.read()).hexdigest()

            # 9. Optionally update stage JSON
            if update_json_path and os.path.exists(update_json_path):
                with open(update_json_path, 'r', encoding='utf-8') as f:
                    stage_json = json.load(f)
                stage_json['docx_sha256'] = sha256_hash
                stage_json['footnote_count'] = len(footnotes)
                with open(update_json_path, 'w', encoding='utf-8') as f:
                    json.dump(stage_json, f, ensure_ascii=False, indent=2)

            return {
                "success": True,
                "output_path": target_out,
                "footnotes_injected": len(footnotes),
                "marker_occurrences_replaced": replaced_count,
                "remaining_paragraphs": len(remaining_paragraphs),
                "sha256": sha256_hash
            }

        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    @classmethod
    def verify(cls, docx_path: str, expected_footnote_count: Optional[int] = None) -> Dict[str, Any]:
        """
        Forensically verifies a DOCX file for native OpenXML footnotes and document integrity.
        """
        import docx

        if not os.path.exists(docx_path):
            return {"valid": False, "error": f"File not found: {docx_path}"}

        try:
            doc = docx.Document(docx_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            paragraph_count = len(paragraphs)
            word_count = sum(len(p.split()) for p in paragraphs)

            with zipfile.ZipFile(docx_path, 'r') as z:
                namelist = z.namelist()
                has_footnotes_xml = 'word/footnotes.xml' in namelist
                has_content_type = False
                if '[Content_Types].xml' in namelist:
                    ct_content = z.read('[Content_Types].xml').decode('utf-8', errors='ignore')
                    has_content_type = '/word/footnotes.xml' in ct_content

                has_relationship = False
                if 'word/_rels/document.xml.rels' in namelist:
                    rels_content = z.read('word/_rels/document.xml.rels').decode('utf-8', errors='ignore')
                    has_relationship = 'footnotes.xml' in rels_content

                footnote_ids = []
                if has_footnotes_xml:
                    fn_xml = z.read('word/footnotes.xml')
                    tree = ET.fromstring(fn_xml)
                    fns = tree.findall('.//w:footnote', NAMESPACES)
                    for fn in fns:
                        f_id = fn.get(f"{{{NAMESPACES['w']}}}id")
                        if f_id not in ('-1', '0') and f_id is not None:
                            footnote_ids.append(f_id)

                # Check references in document.xml
                doc_refs = []
                if 'word/document.xml' in namelist:
                    doc_tree = ET.fromstring(z.read('word/document.xml'))
                    for ref in doc_tree.findall('.//w:footnoteReference', NAMESPACES):
                        ref_id = ref.get(f"{{{NAMESPACES['w']}}}id")
                        if ref_id:
                            doc_refs.append(ref_id)

            passed = (
                paragraph_count > 0 and
                has_footnotes_xml and
                has_content_type and
                has_relationship and
                len(footnote_ids) > 0 and
                (expected_footnote_count is None or len(footnote_ids) == expected_footnote_count)
            )

            return {
                "valid": passed,
                "paragraph_count": paragraph_count,
                "word_count": word_count,
                "has_footnotes_xml": has_footnotes_xml,
                "has_content_type_override": has_content_type,
                "has_document_relationship": has_relationship,
                "footnote_count": len(footnote_ids),
                "footnote_ids": footnote_ids,
                "in_text_references_count": len(doc_refs),
                "references_match_definitions": set(footnote_ids) == set(doc_refs)
            }

        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }


def main():
    parser = argparse.ArgumentParser(description="Standardized OpenXML Native Footnote Injector & Verifier")
    parser.add_argument("--docx", required=True, help="Target Word DOCX file")
    parser.add_argument("--output", default=None, help="Output Word DOCX file (defaults to in-place update)")
    parser.add_argument("--md", default=None, help="Path to markdown draft file to auto-extract footnotes from")
    parser.add_argument("--footnotes-json", default=None, help="Path to JSON file containing footnotes")
    parser.add_argument("--update-json", default=None, help="Path to stage JSON metadata to update docx_sha256")
    parser.add_argument("--verify", action="store_true", help="Run forensic verification after injection")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing docx without modifying")
    parser.add_argument("--report-path", default=None, help="Optional path to write verification report JSON")

    args = parser.parse_args()

    if args.verify_only:
        report = OpenXMLFootnoteInjector.verify(args.docx)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        if args.report_path:
            with open(args.report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        sys.exit(0 if report.get("valid") else 1)

    footnotes = []
    if args.md:
        footnotes = OpenXMLFootnoteInjector.extract_footnotes_from_markdown(args.md)
    elif args.footnotes_json:
        footnotes = OpenXMLFootnoteInjector.extract_footnotes_from_json(args.footnotes_json)
    else:
        # Check if an .md file with the same name exists in the same folder
        candidate_md = os.path.splitext(args.docx)[0] + ".md"
        draft_md = os.path.join(os.path.dirname(args.docx), "draft.md")
        if os.path.exists(candidate_md):
            footnotes = OpenXMLFootnoteInjector.extract_footnotes_from_markdown(candidate_md)
        elif os.path.exists(draft_md):
            footnotes = OpenXMLFootnoteInjector.extract_footnotes_from_markdown(draft_md)

    if not footnotes:
        print("Error: No footnotes found via --md, --footnotes-json, or companion markdown file.", file=sys.stderr)
        sys.exit(1)

    result = OpenXMLFootnoteInjector.inject(
        docx_path=args.docx,
        footnotes=footnotes,
        output_docx_path=args.output,
        update_json_path=args.update_json
    )
    print(f"Footnotes injected successfully: {result['footnotes_injected']} footnotes, {result['marker_occurrences_replaced']} references replaced.")

    if args.verify:
        target_docx = args.output or args.docx
        v_report = OpenXMLFootnoteInjector.verify(target_docx, expected_footnote_count=len(footnotes))
        print("Verification Report:")
        print(json.dumps(v_report, indent=2, ensure_ascii=False))
        if args.report_path:
            with open(args.report_path, 'w', encoding='utf-8') as f:
                json.dump(v_report, f, indent=2, ensure_ascii=False)
        if not v_report.get("valid"):
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
