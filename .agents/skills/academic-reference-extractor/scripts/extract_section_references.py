# -*- coding: utf-8 -*-
"""
Academic Section Reference Extractor & Multi-Format Exporter
Part of the 'academic-reference-extractor' Antigravity Skill.

Usage:
  python extract_section_references.py \
      --source-bib "path/to/full_bib.txt" \
      --citations "path/to/citations_or_footnotes.txt" \
      --output-dir "path/to/output_folder" \
      --prefix "Document_Section"
"""

import os
import sys
import re
import unicodedata
import argparse

def strip_accents(text):
    """Normalize text by converting accented and special characters to base ASCII."""
    if not text:
        return ""
    text = text.replace('\ufffd', 'e')
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8').lower()

def clean_entry_start(entry):
    """Strip stray publisher suffixes or previous book chapter lines preceding the real author."""
    entry = re.sub(r'^[A-Z]\s+(?=[A-Z][a-z])', '', entry).strip()
    m_yr = re.search(r'\(\d{4}[a-z]?\)', entry)
    if m_yr:
        auth_part = entry[:m_yr.start()]
        m_split = re.search(r'(?:https?://[^\s]+|Press\.|Guilford\.|Publisher\.|Author\.|\(Eds?\.?\)[^.]+?\.)\s+([A-Z][a-zA-Z\-\'\s]+,\s+[A-Z]\.)', auth_part)
        if m_split:
            entry = entry[m_split.start(1):].strip()
    return entry

def extract_bibliography_entries(raw_bib_text):
    """
    Parse a raw bibliography text block into individual APA/academic reference entries.
    """
    txt = re.sub(r'\n\s*\d+\s*\n', ' ', raw_bib_text)
    txt = re.sub(r'^\s*References\s*', '', txt.strip(), flags=re.IGNORECASE)

    # Detect publication years in parentheses: (YYYY) or (YYYYa)
    pattern = r'(?<![/\w])\((\d{4}[a-z]?)\)(?:\.|\,|\s+[A-Z])'
    year_matches = list(re.finditer(pattern, txt))

    entries = []
    for i in range(len(year_matches)):
        curr_ym = year_matches[i]
        if i == 0:
            entry_start = 0
        else:
            prev_ym = year_matches[i-1]
            between = txt[prev_ym.end():curr_ym.start()]
            # Find author start
            m = list(re.finditer(r'(?:https?://[^\s]+|\.(?:\s+|$))([A-Z][a-zA-Z\-\'\s]+,\s+[A-Z\.]|\bAmerican Psychiatric Association\b|\bVan den Bos\b|\bVan der Heiden\b|\bLe Poire\b|\bLissek\b|\bSarinopoulos\b|\bDeschenes\b)', between))
            if m:
                entry_start = prev_ym.end() + m[-1].start(1)
            else:
                m2 = list(re.finditer(r'([A-Z][a-zA-Z\-\'\s]+,\s+[A-Z\.]|\bAmerican Psychiatric Association\b|\bVan den Bos\b|\bVan der Heiden\b|\bLe Poire\b|\bLissek\b|\bSarinopoulos\b|\bDeschenes\b)', between))
                if m2:
                    entry_start = prev_ym.end() + m2[-1].start(1)
                else:
                    entry_start = prev_ym.end()

        if i < len(year_matches) - 1:
            next_ym = year_matches[i+1]
            between_next = txt[curr_ym.end():next_ym.start()]
            m_next = list(re.finditer(r'(?:https?://[^\s]+|\.(?:\s+|$))([A-Z][a-zA-Z\-\'\s]+,\s+[A-Z\.]|\bAmerican Psychiatric Association\b|\bVan den Bos\b|\bVan der Heiden\b|\bLe Poire\b|\bLissek\b|\bSarinopoulos\b|\bDeschenes\b)', between_next))
            if m_next:
                entry_end = curr_ym.end() + m_next[-1].start(1)
            else:
                m_next2 = list(re.finditer(r'([A-Z][a-zA-Z\-\'\s]+,\s+[A-Z\.]|\bAmerican Psychiatric Association\b|\bVan den Bos\b|\bVan der Heiden\b|\bLe Poire\b|\bLissek\b|\bSarinopoulos\b|\bDeschenes\b)', between_next))
                if m_next2:
                    entry_end = curr_ym.end() + m_next2[-1].start(1)
                else:
                    entry_end = curr_ym.end() + len(between_next) // 2
        else:
            entry_end = len(txt)

        raw_e = txt[entry_start:entry_end].strip()
        raw_e = re.sub(r'^\s*\d+\s+References\s*', '', raw_e, flags=re.IGNORECASE)
        raw_e = re.sub(r'^\s*[\.\s,]+', '', raw_e)
        raw_e = re.sub(r'\s{2,}', ' ', raw_e)
        if len(raw_e) > 20:
            entries.append(raw_e)

    # Refine and clean entries
    refined = []
    pending_prefix = ""
    for e in entries:
        e = clean_entry_start(e)
        if "finetti" in e.lower() and ("desch" in e.lower()):
            m_d = re.search(r'(Desch[^\s]+,\s+S\.\s*S\.,?)', e)
            if m_d:
                e1 = e[:m_d.start()].strip()
                pending_prefix = m_d.group(1).strip() + " "
                refined.append(clean_entry_start(e1))
                continue
        if pending_prefix:
            e = pending_prefix + e
            pending_prefix = ""
        if "grupe, d. w., mackiewicz" in e.lower() and "sarinopoulos" not in e.lower():
            e = "Sarinopoulos, I., " + e
        if "powers, a. s., mcclure" in e.lower() and "lissek" not in e.lower():
            e = "Lissek, S., " + e
        if "rabin, s. j., mcdowell" in e.lower() and "lissek" not in e.lower():
            e = "Lissek, S., " + e
        refined.append(clean_entry_start(e))

    return refined

def index_bibliography(entries):
    """Index reference entries by author tokens and year for rapid fuzzy matching."""
    bib_index = []
    for idx, entry in enumerate(entries):
        m_yr = re.search(r'\((\d{4}[a-z]?)\)', entry)
        year = m_yr.group(1).lower() if m_yr else ""
        authors_part = entry[:m_yr.start()] if m_yr else entry[:120]
        authors_part_norm = strip_accents(authors_part)
        words = set(re.findall(r'\b[a-z]{3,}\b', authors_part_norm))
        words = {w for w in words if w not in {"and", "eds", "for", "the"}}
        bib_index.append({
            "index": idx,
            "raw": entry,
            "year": year,
            "authors_part": authors_part_norm,
            "author_words": words
        })
    return bib_index

def match_section_citations(citation_list, bib_index):
    """
    Match a list of section citations/footnotes against the indexed bibliography.
    citation_list is a list of strings: e.g. ["Carleton et al., 2007", "Van den Bos & Lind, 2002"]
    """
    matched_entries = {}
    unmatched = []

    for fn_text in citation_list:
        clean_fn = re.sub(r'\[.*?\]', '', fn_text).strip()
        clean_fn_norm = strip_accents(clean_fn)

        years = re.findall(r'\b(19\d\d|20\d\d)[a-z]?\b', clean_fn_norm)
        fn_no_yr = re.sub(r'\b(19\d\d|20\d\d)[a-z]?\b', '', clean_fn_norm)
        fn_authors = set(re.findall(r'\b[a-z]{3,}\b', fn_no_yr))
        fn_authors = {w for w in fn_authors if w not in {"and", "al", "et", "the", "van", "den", "der", "des"}}

        target_years = years if years else [""]
        fn_found = False

        for ty in target_years:
            ty_num = ty[:4]
            best_match = None
            best_score = 0

            for b in bib_index:
                overlap = len(fn_authors.intersection(b["author_words"]))
                if overlap == 0:
                    for fa in fn_authors:
                        if fa in b["authors_part"]:
                            overlap += 1
                if overlap > 0:
                    yr_match = (ty_num == b["year"][:4]) if ty_num and b["year"] else (not ty_num)
                    if yr_match:
                        score = overlap * 10 + (3 if ty == b["year"] else 1)
                        if score > best_score:
                            best_score = score
                            best_match = b

            if best_match:
                matched_entries[best_match["index"]] = best_match["raw"]
                fn_found = True

        if not fn_found:
            unmatched.append(fn_text)

    return matched_entries, unmatched

def parse_record_fields(entry):
    """Extract author, year, title, journal, volume, issue, pages, DOI, URL from APA string."""
    m_yr = re.search(r'\((\d{4}[a-z]?)\)[\.\,]?', entry)
    if m_yr:
        year = m_yr.group(1)
        authors_raw = entry[:m_yr.start()].strip()
        rest = entry[m_yr.end():].strip()
    else:
        year = ""
        authors_raw = ""
        rest = entry

    authors_raw = re.sub(r'&\s*', '', authors_raw)
    authors = []
    if "American Psychiatric Association" in authors_raw:
        authors = ["American Psychiatric Association"]
    else:
        found_auths = re.findall(r'([A-Z][a-zA-Z\-\'\s]+,\s+[A-Z\.\s]+)', authors_raw + ",")
        for a in found_auths:
            a_clean = a.strip().rstrip(',').strip()
            if len(a_clean) > 2 and a_clean not in authors:
                authors.append(a_clean)
        if not authors and authors_raw:
            authors = [authors_raw]

    doi = ""
    url = ""
    m_doi = re.search(r'https?://(?:dx\.)?doi\.org/([^\s]+)', rest)
    if m_doi:
        doi = m_doi.group(1).rstrip('.')
        url = m_doi.group(0).rstrip('.')
        rest_clean = rest[:m_doi.start()].strip()
    else:
        m_url = re.search(r'https?://[^\s]+', rest)
        if m_url:
            url = m_url.group(0).rstrip('.')
            rest_clean = rest[:m_url.start()].strip()
        else:
            rest_clean = rest

    parts = re.split(r'(?<=[.?!])\s+', rest_clean, maxsplit=1)
    if len(parts) >= 2:
        title = parts[0].rstrip('.').strip()
        source = parts[1].strip()
    else:
        title = rest_clean.rstrip('.').strip()
        source = ""

    journal = ""
    volume = ""
    issue = ""
    pages = ""
    ref_type_enw = "Journal Article"
    ref_type_ris = "JOUR"

    if source.startswith("In ") or "Advances in" in source or "(Ed" in source:
        ref_type_enw = "Book Section"
        ref_type_ris = "CHAP"
        journal = source.rstrip('.').strip()
    elif "Press" in source or "Publisher" in source or "Author." in source:
        ref_type_enw = "Book"
        ref_type_ris = "BOOK"
        journal = source.rstrip('.').strip()
    else:
        m_src = re.search(r'([A-Za-z\s&,:\-]+?),\s*(\d+)(?:\((\d+)\))?,\s*([\d\-]+)', source)
        if m_src:
            journal = m_src.group(1).strip()
            volume = m_src.group(2)
            issue = m_src.group(3) or ""
            pages = m_src.group(4)
        else:
            journal = source.rstrip('.').strip()

    return {
        "raw": entry,
        "ref_type_enw": ref_type_enw,
        "ref_type_ris": ref_type_ris,
        "authors": authors,
        "year": year,
        "title": title,
        "journal": journal,
        "volume": volume,
        "issue": issue,
        "pages": pages,
        "doi": doi,
        "url": url
    }

def export_enw(records, output_path):
    """Export records to EndNote Tagged (.enw) format."""
    enw_lines = []
    for r in records:
        item = [f"%0 {r['ref_type_enw']}"]
        for a in r['authors']:
            item.append(f"%A {a}")
        if r['year']:
            item.append(f"%D {r['year']}")
        if r['title']:
            item.append(f"%T {r['title']}")
        if r['journal']:
            if r['ref_type_enw'] == "Journal Article":
                item.append(f"%J {r['journal']}")
            else:
                item.append(f"%B {r['journal']}")
        if r['volume']:
            item.append(f"%V {r['volume']}")
        if r['issue']:
            item.append(f"%N {r['issue']}")
        if r['pages']:
            item.append(f"%P {r['pages']}")
        if r['doi']:
            item.append(f"%R {r['doi']}")
        if r['url']:
            item.append(f"%U {r['url']}")
        enw_lines.append("\n".join(item))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(enw_lines) + "\n")

def export_ris(records, output_path):
    """Export records to Research Information Systems (.ris) format."""
    ris_lines = []
    for r in records:
        item = [f"TY  - {r['ref_type_ris']}"]
        for a in r['authors']:
            item.append(f"AU  - {a}")
        if r['year']:
            item.append(f"PY  - {r['year']}")
        if r['title']:
            item.append(f"TI  - {r['title']}")
        if r['journal']:
            if r['ref_type_ris'] == "JOUR":
                item.append(f"JO  - {r['journal']}")
            else:
                item.append(f"T2  - {r['journal']}")
        if r['volume']:
            item.append(f"VL  - {r['volume']}")
        if r['issue']:
            item.append(f"IS  - {r['issue']}")
        if r['pages']:
            if '-' in r['pages']:
                p1, p2 = r['pages'].split('-', 1)
                item.append(f"SP  - {p1}")
                item.append(f"EP  - {p2}")
            else:
                item.append(f"SP  - {r['pages']}")
        if r['doi']:
            item.append(f"DO  - {r['doi']}")
        if r['url']:
            item.append(f"UR  - {r['url']}")
        item.append("ER  - ")
        ris_lines.append("\n".join(item))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(ris_lines) + "\n")

def export_txt(entries, output_path, title_header="SECTION REFERENCES"):
    """Export formatted APA reference list (.txt)."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"{title_header}\n")
        f.write(f"Total Unique References: {len(entries)}\n")
        f.write(f"=" * 70 + "\n\n")
        for i, e in enumerate(entries, 1):
            f.write(f"{i}. {e}\n\n")
