# -*- coding: utf-8 -*-
"""
Post-Humanization Bidirectional Citation Reconciler & Concordance Auditor
Part of the 'academic-reference-extractor' and 'ai-academic-tone-polisher' Antigravity Skills.
Complies with AGENTS.md Rule 13 (Epistemic Honesty) and Rule 16 (EndNote Concordance).

Audits manuscripts following humanization, paraphrasing, or QuillBot condensation to detect:
1. Orphaned Bibliography Entries (in bibliography but citations dropped from text)
2. Phantom / Missing References (cited in text but omitted from bibliography)
3. Year or Spelling Discrepancies between narrative text and reference registry

Usage:
  python reconcile_post_humanization_citations.py \
      --manuscript "path/to/humanized_manuscript.docx" \
      --refs "path/to/master_references.json" \
      --out-report "citation_concordance_report.json" \
      --prune-orphans
"""

import os
import sys
import json
import re
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

def extract_text_from_source(source_path):
    """Extract raw text from .txt or .docx file."""
    ext = os.path.splitext(source_path)[1].lower()
    if ext == '.txt':
        with open(source_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    elif ext == '.docx':
        try:
            import docx
            doc = docx.Document(source_path)
            # Stop before References section if present to isolate manuscript body
            paragraphs = []
            for p in doc.paragraphs:
                if p.text.strip().lower() in ['references', 'منابع و مآخذ', 'فهرست منابع']:
                    break
                paragraphs.append(p.text)
            return "\n".join(paragraphs)
        except ImportError:
            print("[ERROR] python-docx is required to read .docx files. Install via pip.")
            sys.exit(1)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Use .docx or .txt.")

def extract_in_text_citations(text):
    """
    Extract all in-text citations from text body.
    Returns list of dicts: {'raw': str, 'author': str, 'year': str, 'type': 'parenthetical'|'narrative'}
    """
    citations = []
    
    # 1. Parenthetical patterns: (Author, 2020) or (Author1 & Author2, 2019; Author3 et al., 2021)
    parenthetical_re = re.compile(r'\((?:[A-Z\u00C0-\u017F][a-zA-Z\u00C0-\u017F\s&,-]+(?:et al\.)?,\s*\d{4}[a-z]?(?:;\s*)?)+\)')
    single_subcite_re = re.compile(r'([A-Z\u00C0-\u017F][a-zA-Z\u00C0-\u017F\s&,-]+(?:et al\.)?),\s*(\d{4}[a-z]?)')
    
    for m in parenthetical_re.finditer(text):
        target = m.group(0)
        for sm in single_subcite_re.finditer(target):
            auth = sm.group(1).strip()
            yr = sm.group(2).strip()
            first_sur = re.split(r'\s+(?:and|&)\s+|,|\s+et al', auth)[0].strip()
            citations.append({
                "raw": target,
                "subcite": f"{auth}, {yr}",
                "author_display": auth,
                "first_surname": first_sur,
                "year": yr,
                "type": "parenthetical"
            })
            
    # 2. Narrative patterns: Author et al. (2020) or Author & Author (2019)
    narrative_re = re.compile(r'([A-Z\u00C0-\u017F][a-zA-Z\u00C0-\u017F]+(?:\s*(?:and|&)\s*[A-Z\u00C0-\u017F][a-zA-Z\u00C0-\u017F]+|\s+et al\.)?)\s*\((\d{4}[a-z]?)\)')
    for m in narrative_re.finditer(text):
        auth = m.group(1).strip()
        yr = m.group(2).strip()
        first_sur = re.split(r'\s+(?:and|&)\s+|,|\s+et al', auth)[0].strip()
        citations.append({
            "raw": m.group(0),
            "subcite": f"{auth} ({yr})",
            "author_display": auth,
            "first_surname": first_sur,
            "year": yr,
            "type": "narrative"
        })
        
    return citations

def load_references_registry(refs_path):
    """Load reference registry from JSON or parse text."""
    ext = os.path.splitext(refs_path)[1].lower()
    if ext == '.json':
        with open(refs_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'references' in data:
                return data['references']
    elif ext in ['.txt', '.apa']:
        with open(refs_path, 'r', encoding='utf-8') as f:
            blocks = f.read().split('\n\n')
        entries = []
        rec = 1
        for b in blocks:
            b = b.strip()
            if not b or len(b) < 15 or b.lower() == 'references':
                continue
            m_yr = re.search(r'\((\d{4}[a-z]?)\)', b)
            year = m_yr.group(1) if m_yr else "2020"
            first_author = b.split(',')[0].strip() if ',' in b else b.split()[0]
            entries.append({
                "rec_num": rec,
                "first_author_surname": first_author,
                "year": year,
                "raw_apa": b
            })
            rec += 1
        return entries
    raise ValueError(f"Unsupported reference format: {ext}")

def reconcile(in_text_cites, references):
    """
    Perform bidirectional reconciliation between in-text citations and reference library.
    """
    matched_refs = []
    orphaned_refs = []
    cited_keys = set()

    for cite in in_text_cites:
        cited_keys.add((strip_accents(cite['first_surname']), str(cite['year'])[:4]))

    matched_registry_ids = set()

    for r in references:
        r_id = r.get('rec_num', r.get('id', id(r)))
        r_surname = strip_accents(r.get('first_author_surname', ''))
        r_year = str(r.get('year', ''))[:4]
        
        # Check direct match
        matched = False
        if (r_surname, r_year) in cited_keys:
            matched = True
        else:
            # Check secondary match (surname substring or author list)
            for c_sur, c_yr in cited_keys:
                if c_yr == r_year and (c_sur in r_surname or r_surname in c_sur):
                    matched = True
                    break

        if matched:
            matched_registry_ids.add(r_id)
            matched_refs.append(r)
        else:
            orphaned_refs.append(r)

    # Detect ungrounded/missing citations in text
    missing_citations = []
    for cite in in_text_cites:
        c_sur = strip_accents(cite['first_surname'])
        c_yr = str(cite['year'])[:4]
        found = False
        for r in references:
            r_surname = strip_accents(r.get('first_author_surname', ''))
            r_year = str(r.get('year', ''))[:4]
            if (c_sur in r_surname or r_surname in c_sur) and (c_yr == r_year):
                found = True
                break
        if not found:
            missing_citations.append(cite)

    total_refs = len(references)
    concordance_rate = (len(matched_refs) / total_refs * 100.0) if total_refs > 0 else 100.0

    return {
        "total_references_in_library": total_refs,
        "total_in_text_citations_found": len(in_text_cites),
        "concordant_references_count": len(matched_refs),
        "orphaned_references_count": len(orphaned_refs),
        "missing_in_text_citations_count": len(missing_citations),
        "concordance_percentage": round(concordance_rate, 2),
        "concordant_references": matched_refs,
        "orphaned_references": orphaned_refs,
        "missing_citations": missing_citations
    }

def main():
    parser = argparse.ArgumentParser(description="Post-Humanization Bidirectional Citation Reconciler")
    parser.add_argument("--manuscript", required=True, help="Path to manuscript (.docx or .txt)")
    parser.add_argument("--refs", required=True, help="Path to reference library (.json or .txt)")
    parser.add_argument("--out-report", default=None, help="Output path for JSON audit report")
    parser.add_argument("--prune-orphans", action="store_true", help="Export pruned 100 percent concordant references file")
    
    args = parser.parse_args()

    if not os.path.isfile(args.manuscript):
        print(f"[ERROR] Manuscript file not found: {args.manuscript}")
        sys.exit(1)
        
    if not os.path.isfile(args.refs):
        print(f"[ERROR] References file not found: {args.refs}")
        sys.exit(1)

    print(f"[*] Extracting in-text citations from: {args.manuscript}")
    text = extract_text_from_source(args.manuscript)
    cites = extract_in_text_citations(text)
    print(f"[+] Found {len(cites)} in-text citations in manuscript body.")

    print(f"[*] Loading master references from: {args.refs}")
    references = load_references_registry(args.refs)
    print(f"[+] Loaded {len(references)} bibliographic reference entries.")

    print("[*] Running bidirectional concordance reconciliation...")
    report = reconcile(cites, references)

    print("\n" + "="*70)
    print("📊 POST-HUMANIZATION CITATION CONCORDANCE AUDIT")
    print("="*70)
    print(f"• Total Library References:     {report['total_references_in_library']}")
    print(f"• In-Text Citations Discovered: {report['total_in_text_citations_found']}")
    print(f"• Concordant References:        {report['concordant_references_count']}")
    print(f"• Orphaned References (Pruned): {report['orphaned_references_count']}")
    print(f"• Missing/Phantom Citations:    {report['missing_in_text_citations_count']}")
    print(f"• Concordance Rate:             {report['concordance_percentage']}%")
    print("="*70)

    if report['orphaned_references']:
        print(f"\n[!] Detected {len(report['orphaned_references'])} Orphaned Bibliography Entries:")
        for o in report['orphaned_references'][:5]:
            print(f"    - {o.get('first_author_surname', 'Unknown')} ({o.get('year', '')}): {o.get('title', '')[:60]}...")
        if len(report['orphaned_references']) > 5:
            print(f"    ... and {len(report['orphaned_references']) - 5} more.")

    if report['missing_citations']:
        print(f"\n[!] Detected {len(report['missing_citations'])} Citations in Text Lacking Bibliography Entry:")
        for m in report['missing_citations']:
            print(f"    - {m['subcite']} in clause: '{m['raw'][:60]}'")

    # Save JSON Report
    if args.out_report:
        with open(args.out_report, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n[+] Saved full audit report to: {args.out_report}")

    # Prune orphans if requested
    if args.prune_orphans and report['orphaned_references']:
        base_name = os.path.splitext(args.refs)[0]
        pruned_path = f"{base_name}_concordant_pruned.json"
        with open(pruned_path, 'w', encoding='utf-8') as f:
            json.dump(report['concordant_references'], f, indent=2, ensure_ascii=False)
        print(f"[+] Exported 100% concordant pruned references to: {pruned_path}")

if __name__ == "__main__":
    main()
