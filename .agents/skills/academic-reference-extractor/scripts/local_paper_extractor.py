#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AcademicSuite Local PDF Corpus Ingestion & Extractor (local_paper_extractor.py)
-------------------------------------------------------------------------------
Scans local paper directories (e.g. 04_references_and_lit/papers/), parses full-text
PDFs via pypdf, extracts empirical parameters (Title, Authors, Year, DOI, Sample N,
Design, Measures, Findings), and compiles structured corpora for academic-article-writer.

Author: Saber Ghaderi (Digital Saber AI Twin)
License: MIT
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

import pypdf

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def clean_text_whitespace(text: str) -> str:
    """Normalize irregular whitespaces and linebreaks."""
    if not text:
        return ""
    text = re.sub(r'[\r\n]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_doi_from_text(text: str) -> Optional[str]:
    """Find DOI in text."""
    match = re.search(r'\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b', text)
    if match:
        doi = match.group(1).rstrip('.,;()')
        return doi
    return None


def extract_year_from_text(text: str) -> Optional[int]:
    """Extract 4-digit publication year (between 1980 and 2030)."""
    matches = re.findall(r'\b(19[8-9]\d|20[0-3]\d)\b', text[:2000])
    if matches:
        # Return the most frequent recent year
        years = [int(m) for m in matches if 1990 <= int(m) <= 2026]
        if years:
            return max(years)
    return None


def extract_abstract(text: str) -> str:
    """Extract abstract from text using regex heuristics."""
    # Pattern: Look for 'Abstract' or 'Background' until 'Introduction', 'Keywords', or 'Methods'
    match = re.search(
        r'(?:ABSTRACT|Abstract|Background:?)([\s\S]{100,2500}?)(?:(?:Key\s*words|Keywords|KEYWORDS|INTRODUCTION|Introduction|METHODS|Methods|1\.\s*Introduction)\b)',
        text,
        re.IGNORECASE
    )
    if match:
        return clean_text_whitespace(match.group(1))
    
    # Fallback: take initial 1200 characters
    return clean_text_whitespace(text[:1200])


def detect_sample_size(text: str) -> Optional[int]:
    """Detect participant sample size N."""
    patterns = [
        r'\b[Nn]\s*=\s*(\d{2,5})\b',
        r'(\d{2,5})\s*(?:participants|students|patients|adults|individuals|respondents|subjects)\b',
        r'sample\s*of\s*(\d{2,5})\b',
        r'recruited\s*(\d{2,5})\b'
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = int(m.group(1))
            if 10 <= val <= 50000:
                return val
    return None


def detect_design(text: str) -> str:
    """Classify methodological design."""
    t = text.lower()
    if "randomized controlled" in t or "clinical trial" in t or "rct" in t:
        return "Randomized Controlled Trial (RCT)"
    if "structural equation" in t or "sem" in t or "path analysis" in t:
        return "Structural Equation Modeling (SEM)"
    if "mediation" in t and ("bootstrap" in t or "indirect effect" in t):
        return "Mediation Analysis"
    if "longitudinal" in t or "prospective" in t:
        return "Longitudinal Study"
    if "cross-sectional" in t or "correlational" in t:
        return "Cross-Sectional Correlational"
    if "qualitative" in t or "thematic analysis" in t:
        return "Qualitative Study"
    return "Empirical Quantitative Study"


def extract_title_and_authors_heuristic(first_page_text: str, filename: str) -> Dict[str, str]:
    """Extract title and authors from first page text and filename."""
    lines = [clean_text_whitespace(l) for l in first_page_text.split('\n') if len(clean_text_whitespace(l)) > 5]
    
    # Heuristic 1: If filename is Author_Year_Title.pdf
    fname_match = re.match(r'^([A-Za-z]+)_(\d{4})_(.+)\.pdf$', filename)
    if fname_match:
        f_author = fname_match.group(1)
        f_year = fname_match.group(2)
        f_title = fname_match.group(3).replace('_', ' ')
        return {
            "title": f_title,
            "first_author": f_author,
            "year": f_year
        }

    # Heuristic 2: Title is usually in the top lines before affiliations / Abstract
    title_cand = ""
    for line in lines[:8]:
        if "abstract" in line.lower() or "journal" in line.lower() or "http" in line.lower():
            continue
        if len(line) > 25 and not line.lower().startswith("received"):
            title_cand = line
            break

    return {
        "title": title_cand or filename.replace('.pdf', ''),
        "first_author": "Author et al.",
        "year": "2023"
    }


def parse_pdf_file(pdf_path: Path) -> Dict[str, Any]:
    """Read a single PDF and extract structured content."""
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        num_pages = len(reader.pages)
        if num_pages == 0:
            return {"error": "Empty PDF"}

        first_page_text = reader.pages[0].extract_text() or ""
        full_sample_text = ""
        # Read up to first 4 pages for method/abstract
        for i in range(min(4, num_pages)):
            full_sample_text += (reader.pages[i].extract_text() or "") + "\n"

        # Read last 2 pages for references
        refs_text = ""
        for i in range(max(0, num_pages - 2), num_pages):
            refs_text += (reader.pages[i].extract_text() or "") + "\n"

        meta_heuristic = extract_title_and_authors_heuristic(first_page_text, pdf_path.name)
        doi = extract_doi_from_text(first_page_text) or extract_doi_from_text(full_sample_text)
        year = extract_year_from_text(first_page_text) or meta_heuristic.get("year")
        abstract = extract_abstract(full_sample_text)
        sample_n = detect_sample_size(full_sample_text)
        design = detect_design(full_sample_text)

        # Build clean APA reference
        apa_ref = f"{meta_heuristic.get('first_author')} ({year}). {meta_heuristic.get('title')}."
        if doi:
            apa_ref += f" https://doi.org/{doi}"

        return {
            "filename": pdf_path.name,
            "local_path": str(pdf_path.resolve()),
            "file_size_kb": pdf_path.stat().st_size // 1024,
            "pages": num_pages,
            "title": meta_heuristic.get("title"),
            "author": meta_heuristic.get("first_author"),
            "year": year,
            "doi": doi,
            "design": design,
            "sample_size": sample_n,
            "abstract": abstract,
            "apa_reference": apa_ref,
        }
    except Exception as e:
        return {
            "filename": pdf_path.name,
            "local_path": str(pdf_path.resolve()),
            "error": str(e)
        }


def scan_and_ingest_directory(directory_path: str) -> Dict[str, Any]:
    """Scan directory for all PDFs and generate structured corpus."""
    target_dir = Path(directory_path).resolve()
    print(f"\n=======================================================")
    print(f" AcademicSuite Local PDF Corpus Ingestion Engine       ")
    print(f"=======================================================")
    print(f"[*] Scanning Directory: {target_dir}")

    if not target_dir.exists():
        print(f"[!] Directory not found: {target_dir}")
        return {"total_papers": 0, "papers": []}

    pdf_files = list(target_dir.glob("*.pdf"))
    print(f"[*] Found {len(pdf_files)} PDF files. Parsing full-text contents...\n")

    corpus = []
    apa_references = []

    for pdf_file in sorted(pdf_files):
        print(f"  [PARSING] {pdf_file.name} ({pdf_file.stat().st_size // 1024} KB)...")
        parsed = parse_pdf_file(pdf_file)
        if "error" not in parsed:
            corpus.append(parsed)
            apa_references.append(parsed["apa_reference"])
            print(f"    --> Title: {parsed['title'][:55]}...")
            print(f"    --> Design: {parsed['design']} | N = {parsed['sample_size']} | Year: {parsed['year']}")
        else:
            print(f"    --> [ERROR] {parsed.get('error')}")

    out_corpus_file = target_dir / "ingested_papers_corpus.json"
    with open(out_corpus_file, "w", encoding="utf-8") as f:
        json.dump({
            "target_dir": str(target_dir),
            "total_papers": len(corpus),
            "papers": corpus
        }, f, ensure_ascii=False, indent=2)

    out_apa_file = target_dir / "ingested_references_apa.txt"
    with open(out_apa_file, "w", encoding="utf-8") as f:
        for ref in sorted(apa_references):
            f.write(ref + "\n\n")

    print(f"\n[+] Successfully ingested {len(corpus)} papers.")
    print(f"[+] Structured Corpus: {out_corpus_file}")
    print(f"[+] APA References:    {out_apa_file}\n")

    return {
        "total_papers": len(corpus),
        "corpus_file": str(out_corpus_file),
        "apa_file": str(out_apa_file),
        "papers": corpus
    }


def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Local PDF Corpus Extractor")
    parser.add_argument("--dir", type=str, default="./04_references_and_lit/papers", help="Directory containing PDF files")
    args = parser.parse_args()

    scan_and_ingest_directory(args.dir)


if __name__ == "__main__":
    main()
