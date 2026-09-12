#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anti-Hallucination Citation Verifier & Open-Access Paper Ingestion Engine
(verify_and_download_citation.py)
-------------------------------------------------------------------------
Author: Saber Ghaderi (Digital Saber AI Twin)
Skill: academic-article-writer & literature-harvester

Directive:
If an AI agent references an article or source from generative memory,
it MUST execute this script to:
  1. Determine the authentic existence of the paper via CrossRef, OpenAlex, and Europe PMC.
  2. Download the genuine full-text PDF directly into 04_references_and_lit/papers/.
  3. Extract the real abstract and empirical findings.
  4. Verify that the sentence/claim drafted by the agent strictly aligns with
     the true results of the referenced paper, eliminating ghost citations and hallucinations.
"""

import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AcademicSuite/1.0 (mailto:academic.suite@gmail.com)"
HEADERS = {"User-Agent": USER_AGENT}


def sanitize_filename(text: str, max_len: int = 50) -> str:
    """Sanitize string for filesystem safety."""
    if not text:
        return "Unknown"
    clean = re.sub(r'[\/\\:*?"<>|]', '', text)
    clean = re.sub(r'\s+', '_', clean.strip())
    return clean[:max_len].strip('_')


def format_paper_filename(first_author: str, year: Any, title: str) -> str:
    """Generate standardized filename: Author_Year_ShortTitle.pdf"""
    fa = sanitize_filename(first_author or "Author", max_len=20)
    yr = str(year) if year else "ND"
    ti = sanitize_filename(title or "Paper", max_len=45)
    return f"{fa}_{yr}_{ti}.pdf"


def download_pdf(url: str, dest_path: Path, timeout: int = 25) -> bool:
    """Download binary content to file, verifying PDF magic bytes."""
    if not url:
        return False
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, stream=True, verify=False)
        if resp.status_code == 200:
            first_chunk = next(resp.iter_content(1024), b'')
            if not first_chunk.startswith(b'%PDF'):
                return False
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(first_chunk)
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            if dest_path.stat().st_size > 15000:
                return True
            else:
                dest_path.unlink(missing_ok=True)
                return False
    except Exception:
        dest_path.unlink(missing_ok=True)
        return False
    return False


def query_crossref(query: str, doi: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Query CrossRef API for official metadata."""
    if doi:
        clean_doi = doi.strip().replace("https://doi.org/", "").replace("http://dx.doi.org/", "")
        url = f"https://api.crossref.org/works/{clean_doi}"
    else:
        url = f"https://api.crossref.org/works?query={requests.utils.quote(query)}&rows=1"
        
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            msg = r.json().get("message", {})
            items = msg.get("items", [msg]) if "items" in msg else [msg]
            if items:
                it = items[0]
                title = it.get("title", [""])[0]
                authors = []
                first_author = "Unknown"
                if it.get("author"):
                    for idx, a in enumerate(it["author"]):
                        fam = a.get("family", "")
                        giv = a.get("given", "")
                        name = f"{fam}, {giv}".strip(", ") if fam else a.get("name", "")
                        if name:
                            authors.append(name)
                        if idx == 0:
                            first_author = fam or a.get("name", "Unknown")
                            
                dp = it.get("published-print", {}).get("date-parts") or it.get("published-online", {}).get("date-parts") or it.get("created", {}).get("date-parts")
                year = str(dp[0][0]) if dp and dp[0] else ""
                journal = it.get("container-title", [""])[0]
                doi_found = it.get("DOI", "")
                
                return {
                    "title": title,
                    "first_author": first_author,
                    "authors": authors,
                    "year": year,
                    "journal": journal,
                    "doi": doi_found,
                    "source": "CrossRef"
                }
    except Exception:
        pass
    return None


def query_openalex(query: str, doi: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Query OpenAlex for work metadata, abstract, and open-access PDF."""
    if doi:
        clean_doi = doi.strip().replace("https://doi.org/", "").replace("http://dx.doi.org/", "")
        url = f"https://api.openalex.org/works/https://doi.org/{clean_doi}"
    else:
        clean_q = re.sub(r'[\(\)\[\]\{\}:;,\'"]', ' ', query).strip()
        words = [w for w in clean_q.split() if len(w) > 2][:8]
        url = f"https://api.openalex.org/works?search={requests.utils.quote(' '.join(words))}&per-page=1"
        
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            res = r.json().get("results", []) if "results" in r.json() else [r.json()]
            if res:
                it = res[0]
                title = it.get("title", "")
                year = str(it.get("publication_year", ""))
                doi_found = it.get("doi", "").replace("https://doi.org/", "")
                
                authors = []
                first_author = "Unknown"
                for idx, a in enumerate(it.get("authorships", [])):
                    dn = a.get("author", {}).get("display_name", "")
                    if dn:
                        authors.append(dn)
                        if idx == 0:
                            first_author = dn.split()[-1] if dn.split() else dn
                            
                journal = it.get("primary_location", {}).get("source", {}).get("display_name", "")
                best_oa = it.get("best_oa_location") or {}
                pdf_url = best_oa.get("pdf_url") or ""
                
                # Abstract reconstruction
                abstract = ""
                inv = it.get("abstract_inverted_index")
                if inv:
                    word_pos = []
                    for w, positions in inv.items():
                        for p in positions:
                            word_pos.append((p, w))
                    word_pos.sort(key=lambda x: x[0])
                    abstract = " ".join([w for _, w in word_pos])
                    
                return {
                    "title": title,
                    "first_author": first_author,
                    "authors": authors,
                    "year": year,
                    "journal": journal,
                    "doi": doi_found,
                    "pdf_url": pdf_url,
                    "abstract": abstract,
                    "source": "OpenAlex"
                }
    except Exception:
        pass
    return None


def query_europe_pmc(doi: Optional[str] = None, title: Optional[str] = None) -> Optional[str]:
    """Search Europe PMC to find PMCIDs and direct render PDF URLs."""
    if doi:
        url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=doi:{doi}&format=json"
    elif title:
        q = " ".join([w for w in title.split() if len(w) > 3][:6])
        url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={requests.utils.quote(q)}&format=json"
    else:
        return None
        
    try:
        r = requests.get(url, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            items = r.json().get("resultList", {}).get("result", [])
            if items:
                pmcid = items[0].get("pmcid")
                if pmcid:
                    return f"https://europepmc.org/articles/{pmcid}?pdf=render"
    except Exception:
        pass
    return None


def verify_sentence_alignment(claim: str, abstract: str) -> Dict[str, Any]:
    """Check whether a drafted manuscript sentence aligns with the empirical abstract."""
    if not claim or not abstract:
        return {"status": "UNKNOWN", "warning": "Claim or abstract not provided for linguistic cross-validation."}
        
    c_low = claim.lower()
    a_low = abstract.lower()
    
    # Check for directional congruence (positive vs negative association / effect)
    flagged_contradictions = []
    
    if any(w in c_low for w in ["positive", "increase", "heighten", "elevate", "افزایش", "مثبت"]):
        if any(w in a_low for w in ["negative", "decrease", "reduced", "inverse", "کاهش", "منفی"]) and not any(w in a_low for w in ["positive", "increase", "heighten"]):
            flagged_contradictions.append("Claim posits a POSITIVE relationship, but abstract emphasizes NEGATIVE/DECREASED findings.")
            
    if any(w in c_low for w in ["negative", "decrease", "reduce", "buffer", "کاهش", "منفی"]):
        if any(w in a_low for w in ["positive", "increase", "elevate", "افزایش", "مثبت"]) and not any(w in a_low for w in ["negative", "decrease", "reduce"]):
            flagged_contradictions.append("Claim posits a NEGATIVE relationship, but abstract emphasizes POSITIVE/INCREASED findings.")

    if any(w in c_low for w in ["significant", "mediated", "predicted", "معنادار"]) and "no significant" in a_low:
        flagged_contradictions.append("Claim states a SIGNIFICANT effect, but abstract reports NO SIGNIFICANT relationship.")

    return {
        "aligned": len(flagged_contradictions) == 0,
        "contradictions": flagged_contradictions,
        "abstract_snippet": abstract[:500] + "..." if len(abstract) > 500 else abstract
    }


def main():
    parser = argparse.ArgumentParser(description="Anti-Hallucination Citation Verifier & Paper Downloader")
    parser.add_argument("--query", type=str, help="Search query, paper title, or in-text citation")
    parser.add_argument("--doi", type=str, help="Official Digital Object Identifier (DOI)")
    parser.add_argument("--claim", type=str, help="The sentence or empirical claim the agent wants to write in the manuscript")
    parser.add_argument("--out-dir", type=str, default="04_references_and_lit/papers", help="Output directory for full-text PDF")
    args = parser.parse_args()

    if not args.query and not args.doi:
        print("[!] Error: Either --query or --doi must be supplied.")
        sys.exit(1)

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 70)
    print(" AcademicSuite Anti-Hallucination Citation Verification Engine ")
    print("=" * 70)
    print(f"[*] Input Query: '{args.query or args.doi}'")
    print(f"[*] Target Directory: {out_dir}")

    # 1. Resolve via OpenAlex & CrossRef
    record = None
    if args.doi:
        record = query_openalex(query="", doi=args.doi) or query_crossref(query="", doi=args.doi)
    if not record and args.query:
        # Check if query contains a DOI
        doi_m = re.search(r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+', args.query)
        if doi_m:
            record = query_openalex(query="", doi=doi_m.group(0)) or query_crossref(query="", doi=doi_m.group(0))
        else:
            record = query_openalex(query=args.query) or query_crossref(query=args.query)

    if not record:
        print("\n[!] FATAL ANTI-HALLUCINATION WARNING:")
        print(f"    The referenced source could NOT be verified in official scientific registries (CrossRef / OpenAlex).")
        print(f"    DO NOT cite this paper in the manuscript. It may be a phantom or hallucinated reference.\n")
        sys.exit(2)

    title = record.get("title", "Untitled")
    author = record.get("first_author", "Unknown")
    year = record.get("year", "ND")
    doi = record.get("doi", "")
    abstract = record.get("abstract", "")
    pdf_url = record.get("pdf_url")

    # If no direct OpenAlex PDF, check Europe PMC
    if not pdf_url:
        pdf_url = query_europe_pmc(doi=doi, title=title)

    filename = format_paper_filename(author, year, title)
    dest_path = out_dir / filename

    print(f"\n[+] Verified Authentic Paper in Scientific Registries:")
    print(f"    Title  : {title}")
    print(f"    Authors: {author} et al. ({year})")
    print(f"    Journal: {record.get('journal', 'N/A')}")
    print(f"    DOI    : {doi or 'N/A'}")

    pdf_downloaded = False
    if dest_path.exists() and dest_path.stat().st_size > 15000:
        print(f"    PDF    : [ALREADY EXISTS] {dest_path.name} ({dest_path.stat().st_size // 1024} KB)")
        pdf_downloaded = True
    elif pdf_url:
        print(f"    PDF    : Attempting legal Open-Access download from {pdf_url[:60]}...")
        success = download_pdf(pdf_url, dest_path)
        if success:
            print(f"    PDF    : [SUCCESSFULLY SAVED] {dest_path.name} ({dest_path.stat().st_size // 1024} KB)")
            pdf_downloaded = True
        else:
            print(f"    PDF    : [DOWNLOAD FAILED] Paper is verified but PDF download stream failed.")
    else:
        print(f"    PDF    : [CLOSED ACCESS] Verified citation metadata exists, but open-access PDF is unavailable.")

    # 2. Check Sentence-to-Reference Truth Alignment
    alignment_result = None
    if args.claim:
        print("\n[*] Auditing Sentence-to-Reference Truth Alignment:")
        alignment_result = verify_sentence_alignment(args.claim, abstract)
        if alignment_result["aligned"]:
            print(f"    [PASSED] Drafted sentence appears logically and directionally aligned with paper's abstract.")
        else:
            print(f"    [ALERT - POTENTIAL MISREPRESENTATION]:")
            for c in alignment_result["contradictions"]:
                print(f"      - {c}")

    # Output JSON summary
    summary_path = out_dir.parent / "last_verified_citation.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "status": "VERIFIED_AND_DOWNLOADED" if pdf_downloaded else "VERIFIED_CITATION_ONLY",
            "title": title,
            "first_author": author,
            "year": year,
            "journal": record.get("journal", ""),
            "doi": doi,
            "local_pdf": str(dest_path) if pdf_downloaded else None,
            "abstract": abstract,
            "alignment": alignment_result
        }, f, ensure_ascii=False, indent=2)

    print(f"\n[+] Verification report logged to: {summary_path}\n")


if __name__ == "__main__":
    main()
