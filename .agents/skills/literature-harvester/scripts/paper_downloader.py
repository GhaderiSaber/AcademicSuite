#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AcademicSuite Automated Open-Access Paper Downloader (paper_downloader.py)
-------------------------------------------------------------------------
Automated retrieval and downloading of legal, full-text Open Access academic PDFs
from Europe PMC, PubMed Central (PMC), and Unpaywall.

Saves full-text PDFs directly to the project's literature repository
(e.g., 04_references_and_lit/papers/) with clean, standardized filenames:
    Author_Year_ShortTitle.pdf

Author: Saber Ghaderi (Digital Saber AI Twin)
License: MIT
"""

import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Any

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Initialize robust SSL context with certifi fallback
def get_ssl_context() -> ssl.SSLContext:
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        try:
            return ssl.create_default_context()
        except Exception:
            return ssl._create_unverified_context()

SSL_CONTEXT = get_ssl_context()
DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AcademicSuite/1.0"


def sanitize_filename(text: str, max_len: int = 50) -> str:
    """Sanitize string for filesystem safety."""
    if not text:
        return "Unknown"
    # Remove unwanted punctuation
    clean = re.sub(r'[\/\\:*?"<>|]', '', text)
    clean = re.sub(r'\s+', '_', clean.strip())
    return clean[:max_len].strip('_')


def format_paper_filename(author: str, year: Any, title: str) -> str:
    """Generate standardized filename: Author_Year_ShortTitle.pdf."""
    first_author = "Author"
    if author:
        # Extract surname from first author
        parts = re.split(r'[,;\s]+', str(author).strip())
        if parts:
            first_author = parts[0]
            
    yr_str = str(year) if year else "ND"
    title_slug = sanitize_filename(title or "Paper", max_len=45)
    first_author = sanitize_filename(first_author, max_len=20)
    
    return f"{first_author}_{yr_str}_{title_slug}.pdf"


def download_file_stream(url: str, dest_path: Path, timeout: int = 25) -> bool:
    """Download binary content to file, verifying PDF magic bytes."""
    req = urllib.request.Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
    try:
        with urllib.request.urlopen(req, context=SSL_CONTEXT, timeout=timeout) as resp:
            # Check content length if available
            data = resp.read()
            if len(data) < 1000:  # Too small to be a genuine research PDF
                return False
            if not data.startswith(b"%PDF"):
                return False
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(data)
            return True
    except Exception as e:
        return False


class OpenAccessPaperDownloader:
    """Master orchestrator for discovering and downloading open-access papers."""

    def __init__(self, out_dir: str = "./04_references_and_lit/papers"):
        self.out_dir = Path(out_dir).resolve()
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def search_europe_pmc(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search Europe PMC for open-access papers matching query."""
        oa_query = f"({query}) AND OPEN_ACCESS:y"
        encoded = urllib.parse.quote(oa_query)
        url = (
            f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
            f"query={encoded}&format=json&resultType=core&pageSize={limit}"
        )
        req = urllib.request.Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
        results = []
        try:
            with urllib.request.urlopen(req, context=SSL_CONTEXT, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))
                items = data.get("resultList", {}).get("result", [])
                for item in items:
                    title = item.get("title", "").strip().rstrip(".")
                    authors = item.get("authorString", "")
                    year = item.get("pubYear", "")
                    journal = item.get("journalTitle", "")
                    doi = item.get("doi", "")
                    pmcid = item.get("pmcid", "")
                    abstract = item.get("abstractText", "")
                    
                    # Direct PDF render URL if PMCID exists
                    pdf_url = None
                    if pmcid:
                        pdf_url = f"https://europepmc.org/articles/{pmcid}?pdf=render"
                    else:
                        # Inspect fullTextUrlList
                        urls = item.get("fullTextUrlList", {}).get("fullTextUrl", [])
                        for u in urls:
                            if u.get("documentStyle") == "pdf":
                                pdf_url = u.get("url")
                                break

                    results.append({
                        "id": item.get("id"),
                        "title": title,
                        "authors": authors,
                        "year": year,
                        "journal": journal,
                        "doi": doi,
                        "pmcid": pmcid,
                        "abstract": abstract,
                        "pdf_url": pdf_url,
                        "source": "Europe PMC",
                    })
        except Exception as e:
            sys.stderr.write(f"[OpenAccessDownloader] Europe PMC query error: {e}\n")

        return results

    def fetch_unpaywall_pdf_url(self, doi: str, email: str = "academic.suite@gmail.com") -> Optional[str]:
        """Fetch free legal OA PDF URL from Unpaywall given a DOI."""
        if not doi:
            return None
        clean_doi = doi.strip().lower()
        url = f"https://api.unpaywall.org/v2/{clean_doi}?email={email}"
        req = urllib.request.Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
        try:
            with urllib.request.urlopen(req, context=SSL_CONTEXT, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))
                if data.get("is_oa"):
                    best = data.get("best_oa_location") or {}
                    return best.get("url_for_pdf")
        except Exception:
            pass
        return None

    def download_papers(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search and download papers into the output directory."""
        print(f"\n=======================================================")
        print(f" AcademicSuite Automated Open-Access Paper Downloader ")
        print(f"=======================================================")
        print(f"[*] Query: '{query}'")
        print(f"[*] Target Directory: {self.out_dir}")
        print(f"[*] Requested Limit: {limit} papers\n")

        candidates = self.search_europe_pmc(query, limit=limit * 2)
        if not candidates:
            print("[!] No candidate open-access papers found via Europe PMC.")
            return []

        print(f"[*] Discovered {len(candidates)} candidate open-access records. Attempting download...\n")

        downloaded_records = []
        for cand in candidates:
            if len(downloaded_records) >= limit:
                break

            title = cand["title"]
            author = cand["authors"]
            year = cand["year"]
            doi = cand["doi"]
            pdf_url = cand.get("pdf_url")

            # Fallback to Unpaywall if Europe PMC direct render is missing
            if not pdf_url and doi:
                pdf_url = self.fetch_unpaywall_pdf_url(doi)

            if not pdf_url:
                continue

            filename = format_paper_filename(author, year, title)
            dest_file = self.out_dir / filename

            # Check if file already exists
            if dest_file.exists() and dest_file.stat().st_size > 1000:
                print(f"  [EXISTS] {filename} ({dest_file.stat().st_size // 1024} KB)")
                cand["local_path"] = str(dest_file.resolve())
                cand["filename"] = filename
                cand["file_size_kb"] = dest_file.stat().st_size // 1024
                downloaded_records.append(cand)
                continue

            print(f"  [DOWNLOADING] {title[:65]}...")
            success = download_file_stream(pdf_url, dest_file)
            if success:
                size_kb = dest_file.stat().st_size // 1024
                print(f"    --> Saved: {filename} ({size_kb} KB)")
                cand["local_path"] = str(dest_file.resolve())
                cand["filename"] = filename
                cand["file_size_kb"] = size_kb
                downloaded_records.append(cand)
                time.sleep(0.5)  # Respectful pacing
            else:
                print(f"    --> [FAILED] Could not retrieve PDF from {pdf_url[:50]}")

        # Export manifest
        manifest_path = self.out_dir / "downloaded_papers_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump({
                "query": query,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_downloaded": len(downloaded_records),
                "papers": downloaded_records
            }, f, ensure_ascii=False, indent=2)

        print(f"\n[+] Successfully downloaded {len(downloaded_records)} papers into:")
        print(f"    {self.out_dir}")
        print(f"[+] Manifest written to: {manifest_path}\n")

        return downloaded_records


def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Automated Open-Access Paper Downloader")
    parser.add_argument("--query", type=str, required=True, help="Search query (e.g., 'self-compassion chronic pain')")
    parser.add_argument("--out-dir", type=str, default="./04_references_and_lit/papers", help="Output directory for PDFs")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of papers to download")
    args = parser.parse_args()

    downloader = OpenAccessPaperDownloader(out_dir=args.out_dir)
    downloader.download_papers(query=args.query, limit=args.limit)


if __name__ == "__main__":
    main()
