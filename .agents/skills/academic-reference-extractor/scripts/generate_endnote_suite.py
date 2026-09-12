# -*- coding: utf-8 -*-
"""
EndNote 360° Publishing Suite Generator
Part of the 'academic-reference-extractor' and 'academic-article-writer' Antigravity Skills.
Complies with AGENTS.md Rule 16 (Mandatory EndNote Citation Compatibility).

Generates:
1. EndNote Import Library (.enw)
2. Universal RIS Library (.ris)
3. Word Document with Live Dynamic Cite-While-You-Write (CWYW) Fields (ADDIN EN.CITE & ADDIN EN.REFLIST)
4. Word Document with Unformatted Temporary Citations ({Author, Year #RecNum})

Usage:
  python generate_endnote_suite.py \
      --docx "path/to/manuscript.docx" \
      --refs "path/to/references.json" \
      --out-dir "path/to/output_dir" \
      --prefix "Manuscript_Article"
"""

import os
import sys
import json
import re
import html
import copy
import zipfile
import argparse
import unicodedata

def strip_accents(text):
    """Normalize diacritics and accents for robust author surname matching."""
    if not text:
        return ""
    text = str(text).replace('\ufffd', 'e')
    result = []
    for ch in unicodedata.normalize('NFKD', text):
        if unicodedata.combining(ch):
            continue
        result.append(ch)
    return "".join(result).strip().lower()

def parse_apa_entry(raw_entry, rec_num=1):
    """Fallback parser for raw APA text into structured reference dictionary."""
    raw = " ".join(raw_entry.strip().split())
    doi_match = re.search(r'(?:https?://doi\.org/|doi:\s*)(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)', raw, re.I)
    doi = doi_match.group(1) if doi_match else ""
    
    # Year
    year_match = re.search(r'\((\d{4}[a-z]?)\)', raw)
    year = year_match.group(1) if year_match else "2020"
    
    # Authors
    if year_match:
        auth_part = raw[:year_match.start()].strip().rstrip('.')
    else:
        auth_part = "Anonymous"
    
    authors = [a.strip() for a in re.split(r',\s*&|\band\b|&', auth_part) if a.strip()]
    if not authors:
        authors = ["Anonymous"]
    
    first_author_surname = authors[0].split(',')[0].strip() if authors else "Anonymous"
    
    # Title and Journal
    post_year = raw[year_match.end():].strip().lstrip('. ') if year_match else raw
    parts = post_year.split('. ')
    title = parts[0] if len(parts) > 0 else "Untitled"
    journal = parts[1] if len(parts) > 1 else ""
    
    # Clean journal of volume/pages
    vol_match = re.search(r'(\d+)(?:\((\d+)\))?,\s*([\d–-]+)', journal)
    volume, issue, pages = "", "", ""
    if vol_match:
        volume = vol_match.group(1)
        issue = vol_match.group(2) or ""
        pages = vol_match.group(3) or ""
        journal = journal[:vol_match.start()].strip().rstrip(',')
        
    return {
        "rec_num": rec_num,
        "first_author_surname": first_author_surname,
        "authors": authors,
        "year": year,
        "title": title,
        "journal": journal or "Academic Journal",
        "volume": volume,
        "issue": issue,
        "pages": pages,
        "doi": doi,
        "ref_type": "Journal Article",
        "raw_apa": raw
    }

def load_references(refs_path):
    """Load references from JSON, RIS, ENW, or plain text APA bibliography."""
    ext = os.path.splitext(refs_path)[1].lower()
    
    if ext == '.json':
        with open(refs_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                for i, r in enumerate(data):
                    if 'rec_num' not in r:
                        r['rec_num'] = i + 1
                    if 'first_author_surname' not in r and 'authors' in r and r['authors']:
                        r['first_author_surname'] = r['authors'][0].split(',')[0].strip()
                    if 'first_author_surname' not in r and 'first_author' in r:
                        r['first_author_surname'] = r['first_author']
                return data
            elif isinstance(data, dict) and 'references' in data:
                return data['references']
                
    elif ext in ['.txt', '.apa']:
        with open(refs_path, 'r', encoding='utf-8') as f:
            lines = f.read().split('\n\n')
        entries = []
        rec_num = 1
        for block in lines:
            block = block.strip()
            if not block or len(block) < 20 or block.lower() == 'references':
                continue
            entries.append(parse_apa_entry(block, rec_num))
            rec_num += 1
        return entries

    elif ext == '.ris':
        with open(refs_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        records = content.split('ER  -')
        entries = []
        rec_num = 1
        for rec in records:
            rec = rec.strip()
            if not rec:
                continue
            item = {"rec_num": rec_num, "authors": [], "ref_type": "Journal Article"}
            for line in rec.split('\n'):
                line = line.strip()
                if line.startswith('TI  - ') or line.startswith('T1  - '):
                    item['title'] = line[6:].strip()
                elif line.startswith('AU  - ') or line.startswith('A1  - '):
                    item['authors'].append(line[6:].strip())
                elif line.startswith('PY  - ') or line.startswith('Y1  - '):
                    item['year'] = line[6:10].strip()
                elif line.startswith('JO  - ') or line.startswith('JF  - ') or line.startswith('T2  - '):
                    item['journal'] = line[6:].strip()
                elif line.startswith('VL  - '):
                    item['volume'] = line[6:].strip()
                elif line.startswith('IS  - '):
                    item['issue'] = line[6:].strip()
                elif line.startswith('SP  - '):
                    item['pages'] = line[6:].strip()
                elif line.startswith('DO  - '):
                    item['doi'] = line[6:].strip()
            if item.get('authors'):
                item['first_author_surname'] = item['authors'][0].split(',')[0].strip()
            else:
                item['first_author_surname'] = "Anonymous"
            item['year'] = item.get('year', '2020')
            item['title'] = item.get('title', 'Untitled')
            item['journal'] = item.get('journal', 'Academic Journal')
            item['pages'] = item.get('pages', '')
            item['volume'] = item.get('volume', '')
            item['issue'] = item.get('issue', '')
            item['doi'] = item.get('doi', '')
            entries.append(item)
            rec_num += 1
        return entries
        
    raise ValueError(f"Unsupported reference format: {ext}. Please provide .json, .txt, or .ris.")

def export_enw(references, out_path):
    """Export references into standard EndNote import format (.enw)."""
    lines = []
    for r in references:
        lines.append(f"%0 {r.get('ref_type', 'Journal Article')}")
        lines.append(f"%T {r.get('title', '')}")
        for author in r.get('authors', []):
            lines.append(f"%A {author}")
        lines.append(f"%D {r.get('year', '')}")
        lines.append(f"%J {r.get('journal', '')}")
        if r.get('volume'):
            lines.append(f"%V {r.get('volume')}")
        if r.get('issue'):
            lines.append(f"%N {r.get('issue')}")
        if r.get('pages'):
            lines.append(f"%P {r.get('pages')}")
        if r.get('doi'):
            lines.append(f"%R {r.get('doi')}")
            lines.append(f"%U https://doi.org/{r.get('doi')}")
        lines.append(f"%M {r.get('rec_num', '')}")
        lines.append("")  # Blank line separator
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

def export_ris(references, out_path):
    """Export references into standard Universal RIS format (.ris)."""
    lines = []
    for r in references:
        lines.append("TY  - JOUR")
        lines.append(f"TI  - {r.get('title', '')}")
        for author in r.get('authors', []):
            lines.append(f"AU  - {author}")
        lines.append(f"PY  - {r.get('year', '')}")
        lines.append(f"JO  - {r.get('journal', '')}")
        if r.get('volume'):
            lines.append(f"VL  - {r.get('volume')}")
        if r.get('issue'):
            lines.append(f"IS  - {r.get('issue')}")
        if r.get('pages'):
            parts = r.get('pages', '').split('–')
            if len(parts) == 2:
                lines.append(f"SP  - {parts[0].strip()}")
                lines.append(f"EP  - {parts[1].strip()}")
            else:
                lines.append(f"SP  - {r.get('pages')}")
        if r.get('doi'):
            lines.append(f"DO  - {r.get('doi')}")
            lines.append(f"UR  - https://doi.org/{r.get('doi')}")
        lines.append(f"ID  - {r.get('rec_num', '')}")
        lines.append("ER  - ")
        lines.append("")
        
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

def find_matching_entry(author_query, year_query, registry):
    """Find a reference entry by author surname and year, tolerant of accents and suffixes."""
    norm_aq = strip_accents(author_query)
    norm_y = str(year_query)[:4]
    
    # Priority 1: Exact surname and year match
    for r in registry:
        r_author = strip_accents(r.get('first_author_surname', ''))
        if norm_aq in r_author and str(r.get('year', ''))[:4] == norm_y:
            return r
            
    # Priority 2: Surname in any author name and year match
    for r in registry:
        if str(r.get('year', ''))[:4] == norm_y:
            for a in r.get('authors', []):
                if norm_aq in strip_accents(a):
                    return r
                    
    # Priority 3: Surname match only
    for r in registry:
        r_author = strip_accents(r.get('first_author_surname', ''))
        if norm_aq in r_author:
            return r
            
    return None

def make_en_cite_xml(entries, display_text):
    """Generate Word complex field instruction XML for EndNote CWYW."""
    cites_xml = []
    for entry in entries:
        author_elem = entry.get('first_author_surname', 'Anonymous')
        year_elem = entry.get('year', '2020')
        rec_num = entry.get('rec_num', 1)
        authors_xml = ''.join([f'<author>{html.escape(a)}</author>' for a in entry.get('authors', [author_elem])])
        
        cite_str = (
            f'<Cite>'
            f'<Author>{html.escape(author_elem)}</Author>'
            f'<Year>{year_elem}</Year>'
            f'<RecNum>{rec_num}</RecNum>'
            f'<DisplayText>{html.escape(display_text)}</DisplayText>'
            f'<record>'
            f'<rec-number>{rec_num}</rec-number>'
            f'<foreign-keys><key app="EN" db-id="z5xsxpa9vw9eafeatwtxpwpgvzzfzpweevz2" timestamp="1747307359">{rec_num}</key></foreign-keys>'
            f'<ref-type name="{html.escape(entry.get("ref_type", "Journal Article"))}">17</ref-type>'
            f'<contributors><authors>{authors_xml}</authors></contributors>'
            f'<titles><title>{html.escape(entry.get("title", ""))}</title>'
            f'<secondary-title>{html.escape(entry.get("journal", ""))}</secondary-title></titles>'
            f'<periodical><full-title>{html.escape(entry.get("journal", ""))}</full-title></periodical>'
            f'<pages>{html.escape(entry.get("pages", ""))}</pages>'
            f'<volume>{html.escape(str(entry.get("volume", "")))}</volume>'
            f'<number>{html.escape(str(entry.get("issue", "")))}</number>'
            f'<dates><year>{year_elem}</year></dates>'
            f'<electronic-resource-num>{html.escape(entry.get("doi", ""))}</electronic-resource-num>'
            f'<urls><related-urls><url>https://doi.org/{html.escape(entry.get("doi", ""))}</url></related-urls></urls>'
            f'</record>'
            f'</Cite>'
        )
        cites_xml.append(cite_str)
    return f'<EndNote>{" ".join(cites_xml)}</EndNote>'

def process_docx_endnote_suite(docx_path, registry, out_unformatted_path, out_cwyw_path):
    """
    Scans a Word document for APA citations, maps to registry entries,
    and generates both Unformatted and CWYW OpenXML documents.
    """
    try:
        import docx
    except ImportError:
        print("[ERROR] python-docx is required. Install via: pip install python-docx")
        sys.exit(1)

    doc = docx.Document(docx_path)
    
    # Locate References section boundary
    ref_idx = len(doc.paragraphs)
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip().lower() in ['references', 'منابع و مآخذ', 'فهرست منابع']:
            ref_idx = i
            break
            
    # Regular expressions for parenthetical and narrative citations
    parenthetical_re = re.compile(r'\((?:[A-Z\u00C0-\u017F][a-zA-Z\u00C0-\u017F\s&,-]+(?:et al\.)?,\s*\d{4}[a-z]?(?:;\s*)?)+\)')
    single_subcite_re = re.compile(r'([A-Z\u00C0-\u017F][a-zA-Z\u00C0-\u017F\s&,-]+(?:et al\.)?),\s*(\d{4}[a-z]?)')
    narrative_re = re.compile(r'([A-Z\u00C0-\u017F][a-zA-Z\u00C0-\u017F]+(?:\s*(?:and|&)\s*[A-Z\u00C0-\u017F][a-zA-Z\u00C0-\u017F]+|\s+et al\.)?)\s*\((\d{4}[a-z]?)\)')

    # Build mapping rules
    rules = []
    seen_targets = set()

    for p in doc.paragraphs[:ref_idx]:
        p_text = p.text
        
        # 1. Parenthetical matches
        for m in parenthetical_re.finditer(p_text):
            target = m.group(0)
            if target in seen_targets:
                continue
            
            # Extract subcitations
            entries = []
            unf_parts = []
            sub_matches = list(single_subcite_re.finditer(target))
            if sub_matches:
                for sm in sub_matches:
                    auth = sm.group(1).strip()
                    yr = sm.group(2).strip()
                    first_sur = re.split(r'\s+(?:and|&)\s+|,|\s+et al', auth)[0].strip()
                    entry = find_matching_entry(first_sur, yr, registry)
                    if entry:
                        entries.append(entry)
                        unf_parts.append(f"{auth}, {yr} #{entry['rec_num']}")
                
                if entries:
                    seen_targets.add(target)
                    unf_tag = "{" + "; ".join(unf_parts) + "}"
                    rules.append((target, entries, unf_tag, target))

        # 2. Narrative matches
        for m in narrative_re.finditer(p_text):
            target = m.group(0)
            if target in seen_targets:
                continue
                
            auth = m.group(1).strip()
            yr = m.group(2).strip()
            first_sur = re.split(r'\s+(?:and|&)\s+|,|\s+et al', auth)[0].strip()
            entry = find_matching_entry(first_sur, yr, registry)
            if entry:
                seen_targets.add(target)
                unf_tag = f"{auth} {{{auth}, {yr} #{entry['rec_num']}}}"
                rules.append((target, [entry], unf_tag, target))

    print(f"[*] Discovered {len(rules)} distinct in-text citation patterns mapped to EndNote registry.")

    # 1. Generate Unformatted Document
    doc_unf = docx.Document(docx_path)
    applied_unf = 0
    for p_idx in range(min(ref_idx, len(doc_unf.paragraphs))):
        p = doc_unf.paragraphs[p_idx]
        
        # Preserve drawing invariant: do not touch text if paragraph contains inline shapes
        if bool(p._p.xpath('.//w:drawing') or p._p.xpath('.//a:blip')):
            continue
            
        text = p.text
        for target, entries, unf_tag, cwyw_disp in rules:
            if target in text:
                text = text.replace(target, unf_tag)
                applied_unf += 1
        p.text = text
        
    doc_unf.save(out_unformatted_path)
    print(f"[+] Exported Unformatted DOCX: {out_unformatted_path} (Replaced {applied_unf} citation instances)")

    # 2. Generate CWYW Document using OpenXML Field Injection
    with zipfile.ZipFile(docx_path, 'r') as zin, zipfile.ZipFile(out_cwyw_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            buffer = zin.read(item.filename)
            if item.filename == 'word/document.xml':
                xml_content = buffer.decode('utf-8')
                for target, entries, unf_tag, cwyw_disp in rules:
                    en_xml = make_en_cite_xml(entries, cwyw_disp)
                    escaped_en = html.escape(en_xml, quote=True)
                    field_xml = (
                        f'<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
                        f'<w:r><w:instrText xml:space="preserve"> ADDIN EN.CITE {escaped_en} </w:instrText></w:r>'
                        f'<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
                        f'<w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="24"/></w:rPr>'
                        f'<w:t>{html.escape(target)}</w:t></w:r>'
                        f'<w:r><w:fldChar w:fldCharType="end"/></w:r>'
                    )
                    xml_target = html.escape(target)
                    if xml_target in xml_content:
                        xml_content = xml_content.replace(xml_target, field_xml, 1)
                    elif target in xml_content:
                        xml_content = xml_content.replace(target, field_xml, 1)

                # Inject ADDIN EN.REFLIST at References header
                ref_marker = '<w:t>References</w:t>'
                if ref_marker in xml_content:
                    reflist_xml = (
                        '<w:t>References</w:t></w:r></w:p>'
                        '<w:p><w:r><w:fldChar w:fldCharType="begin"/></w:r>'
                        '<w:r><w:instrText xml:space="preserve"> ADDIN EN.REFLIST </w:instrText></w:r>'
                        '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t></w:t>'
                    )
                    xml_content = xml_content.replace(ref_marker, reflist_xml, 1)
                    
                buffer = xml_content.encode('utf-8')
            zout.writestr(item, buffer)

    print(f"[+] Exported Live CWYW DOCX: {out_cwyw_path} (Active ADDIN EN.CITE fields embedded)")

def main():
    parser = argparse.ArgumentParser(description="EndNote 360° Publishing Suite Generator")
    parser.add_argument("--docx", required=True, help="Path to input .docx manuscript")
    parser.add_argument("--refs", required=True, help="Path to references (.json, .ris, .enw, or .txt)")
    parser.add_argument("--out-dir", default=None, help="Output directory (default: same as --docx)")
    parser.add_argument("--prefix", default=None, help="File prefix for outputs (default: based on docx name)")
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.docx):
        print(f"[ERROR] Manuscript file not found: {args.docx}")
        sys.exit(1)
        
    if not os.path.isfile(args.refs):
        print(f"[ERROR] References file not found: {args.refs}")
        sys.exit(1)
        
    out_dir = args.out_dir or os.path.dirname(os.path.abspath(args.docx))
    os.makedirs(out_dir, exist_ok=True)
    
    base_prefix = args.prefix or os.path.splitext(os.path.basename(args.docx))[0]
    # Strip any trailing _EndNote suffixes if re-running
    base_prefix = re.sub(r'_(?:EndNote_CWYW|EndNote_Unformatted|Clean)$', '', base_prefix)

    # 1. Load & Normalize References
    print(f"[*] Ingesting references from: {args.refs}")
    references = load_references(args.refs)
    print(f"[+] Loaded {len(references)} bibliographic references.")
    
    # 2. Export Libraries (.enw and .ris)
    enw_path = os.path.join(out_dir, f"EndNote_Library_{base_prefix}.enw")
    ris_path = os.path.join(out_dir, f"EndNote_Library_{base_prefix}.ris")
    export_enw(references, enw_path)
    export_ris(references, ris_path)
    print(f"[+] Exported EndNote Import Library: {enw_path}")
    print(f"[+] Exported Universal RIS Library: {ris_path}")
    
    # 3. Export Word Suite (Unformatted & CWYW)
    unformatted_docx = os.path.join(out_dir, f"{base_prefix}_EndNote_Unformatted.docx")
    cwyw_docx = os.path.join(out_dir, f"{base_prefix}_EndNote_CWYW.docx")
    
    print(f"[*] Processing Word document citations: {args.docx}")
    process_docx_endnote_suite(args.docx, references, unformatted_docx, cwyw_docx)
    
    print("\n" + "="*70)
    print("✨ ENDNOTE 360° PUBLISHING SUITE GENERATION COMPLETE")
    print(f"• EndNote Library:     {enw_path}")
    print(f"• RIS Library:         {ris_path}")
    print(f"• CWYW Document:       {cwyw_docx}")
    print(f"• Unformatted Doc:     {unformatted_docx}")
    print("="*70)

if __name__ == "__main__":
    main()
