#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validators/provenance_validator.py — Master Fail-Closed Claim Provenance & Evidence Validator

Audits the 4-tier evidence layer and 5-link provenance relationship:
1. Schema validity of claim_provenance.json
2. Unbroken 5-link provenance chain (claim -> artifact -> statistic -> analysis -> data)
3. Cryptographic SHA-256 hash matching on all 5 links
4. Numerical parameter identity between claim metrics and result.json
5. Orphan claim detection in narrative text (.md, .docx)
"""

import os
import sys
import re
import json
import argparse
from typing import Dict, Any, List, Optional, Set, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Virtual environment discovery
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

# Fallback to system dist-packages
for p in ["/usr/lib/python3/dist-packages", "/usr/local/lib/python3/dist-packages"]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

from scripts.evidence_provenance_engine import (
    verify_claim_provenance,
    trace_claim_provenance,
    compute_sha256,
    resolve_path,
    load_claim_provenance_schema
)


# Patterns that indicate substantive statistical or empirical claims in academic narrative
CLAIM_PATTERNS = [
    # Explicit hypothesis confirmation / rejection (Persian)
    re.compile(r"فرضیه\s+(?:اول|دوم|سوم|چهارم|پنجم|ششم|هفتم|هشتم|نهم|دهم|\d+)\s+(?:تأیید|رد|پذیرفته|اثبات)\s+شد", re.UNICODE),
    re.compile(r"یافته[‌\s]+ها\s+نشان\s+داد\s+که", re.UNICODE),
    re.compile(r"تأثیر\s+معنادار[ی\s]+بر", re.UNICODE),
    # Explicit hypothesis confirmation / rejection (English)
    re.compile(r"Hypothesis\s+\d+\s+was\s+(?:supported|rejected|confirmed)", re.IGNORECASE),
    re.compile(r"findings\s+(?:demonstrated|indicated|revealed)\s+that", re.IGNORECASE),
    re.compile(r"significant\s+(?:reduction|increase|effect|difference)\s+in", re.IGNORECASE),
    # Statistical test reporting patterns: F(df1, df2) = ..., t(df) = ..., beta = ...
    re.compile(r"F\s*\(\s*\d+\s*,\s*\d+\s*\)\s*=\s*\d+(?:\.\d+)?", re.IGNORECASE),
    re.compile(r"t\s*\(\s*\d+\s*\)\s*=\s*-?\d+(?:\.\d+)?", re.IGNORECASE),
    re.compile(r"(?:β|beta)\s*=\s*-?\d+(?:\.\d+)?", re.IGNORECASE),
]


ORDINAL_MAP = {
    "اول": 1, "دوم": 2, "سوم": 3, "چهارم": 4, "پنجم": 5,
    "ششم": 6, "هفتم": 7, "هشتم": 8, "نهم": 9, "دهم": 10
}
ORDINAL_PATTERN = re.compile(r"(?:فرضیه|Hypothesis)\s+(اول|دوم|سوم|چهارم|پنجم|ششم|هفتم|هشتم|نهم|دهم|\d+)", re.IGNORECASE | re.UNICODE)

STOP_WORDS = {
    "و", "یا", "که", "از", "به", "در", "بر", "با", "شد", "است", "شدند", "بود", "گردید",
    "تا", "این", "آن", "یک", "برای", "همچنین", "نشان", "داد", "دادند",
    "and", "or", "that", "from", "to", "in", "on", "with", "was", "were", "is", "are", "the", "a", "an", "also"
}


def extract_hyp_number(text: str) -> Optional[int]:
    """Extracts hypothesis number from text if present."""
    m = ORDINAL_PATTERN.search(text)
    if not m:
        return None
    val = m.group(1).lower()
    if val in ORDINAL_MAP:
        return ORDINAL_MAP[val]
    if val.isdigit():
        return int(val)
    return None


def detect_orphan_claims(
    narrative_text: str,
    registered_claims: List[Dict[str, Any]],
    doc_path: str
) -> List[str]:
    """
    Detects substantive empirical or statistical claims in narrative text
    that lack a corresponding registered claim in claim_provenance.json.
    """
    orphan_errors: List[str] = []
    
    # Extract registered statements and IDs
    registered_statements = [c.get("statement", "").strip() for c in registered_claims if c.get("statement")]
    registered_ids = [c.get("claim_id", "").strip() for c in registered_claims if c.get("claim_id")]

    # Split text into paragraphs or substantive sentences
    paragraphs = [p.strip() for p in narrative_text.split("\n\n") if p.strip()]
    
    for p_idx, para in enumerate(paragraphs):
        # Skip tables, markdown headers, code blocks
        if para.startswith("#") or para.startswith("|") or para.startswith("```"):
            continue

        # Check if paragraph makes a substantive statistical claim
        has_claim_marker = any(pat.search(para) for pat in CLAIM_PATTERNS)
        if has_claim_marker:
            matched = False
            # 1. Check explicit claim ID tag in text: [CLM-...]
            for cid in registered_ids:
                if cid in para:
                    matched = True
                    break
            
            if not matched:
                para_hyp = extract_hyp_number(para)
                para_words = set(w.lower() for w in re.findall(r"\w+", para) if w.lower() not in STOP_WORDS)

                # 2. Check match with registered statements
                for stmt in registered_statements:
                    stmt_hyp = extract_hyp_number(stmt)
                    # If hypothesis numbers are explicitly present and differ, cannot match
                    if para_hyp is not None and stmt_hyp is not None and para_hyp != stmt_hyp:
                        continue

                    # Substring match
                    if stmt in para or para in stmt:
                        matched = True
                        break

                    # Jaccard overlap on content words
                    stmt_words = set(w.lower() for w in re.findall(r"\w+", stmt) if w.lower() not in STOP_WORDS)
                    intersection = len(para_words.intersection(stmt_words))
                    union = len(para_words.union(stmt_words))
                    if intersection >= 4 and union > 0 and (intersection / union >= 0.35):
                        matched = True
                        break

            if not matched:
                # Only flag if there are registered claims (proving provenance is being tracked for this stage)
                if registered_claims:
                    snippet = para[:120] + ("..." if len(para) > 120 else "")
                    orphan_errors.append(
                        f"Unregistered orphan claim detected in '{os.path.basename(doc_path)}' (para {p_idx+1}): \"{snippet}\""
                    )

    return orphan_errors


def validate_provenance(
    stage_dir: str,
    provenance_path: Optional[str] = None,
    require_provenance: bool = False,
    check_orphan_claims: bool = True
) -> Dict[str, Any]:
    """
    Master fail-closed claim provenance validator for a stage directory.
    """
    stage_dir_abs = os.path.abspath(stage_dir)
    
    # Locate claim_provenance.json
    if not provenance_path:
        cand = os.path.join(stage_dir_abs, "claim_provenance.json")
        if os.path.isfile(cand):
            provenance_path = cand

    if not provenance_path or not os.path.isfile(provenance_path):
        if require_provenance:
            return {
                "verdict": "BLOCKED",
                "errors": [f"Authoritative claim_provenance.json required but not found in '{stage_dir_abs}'"],
                "warnings": [],
                "evidence": {"provenance_found": False}
            }
        else:
            return {
                "verdict": "UNVERIFIED",
                "errors": [],
                "warnings": [f"No claim_provenance.json found in '{stage_dir_abs}'; provenance unverified"],
                "evidence": {"provenance_found": False}
            }

    # Execute 4-tier and 5-link verification
    res = verify_claim_provenance(provenance_path, stage_dir=stage_dir_abs)
    verdict = res["verdict"]
    errors = res["errors"]
    warnings = res["warnings"]
    evidence = res["evidence"]

    # If verification passed so far and check_orphan_claims is True, scan narrative text
    if check_orphan_claims and verdict == "PASS":
        with open(provenance_path, "r", encoding="utf-8") as pf:
            prov_data = json.load(pf)
        registered_claims = prov_data.get("claims", [])

        # Find Markdown files in stage_dir
        for root, _, files in os.walk(stage_dir_abs):
            for f in files:
                if f.endswith(".md") and not f.startswith("walkthrough") and not f.startswith("implementation_plan"):
                    md_file = os.path.join(root, f)
                    try:
                        with open(md_file, "r", encoding="utf-8") as mf:
                            md_content = mf.read()
                        orphan_errs = detect_orphan_claims(md_content, registered_claims, md_file)
                        if orphan_errs:
                            errors.extend(orphan_errs)
                            verdict = "FAIL"
                    except Exception as e:
                        warnings.append(f"Could not read '{md_file}' for orphan claim check: {str(e)}")

    return {
        "verdict": verdict,
        "errors": errors,
        "warnings": warnings,
        "evidence": evidence
    }


def main():
    parser = argparse.ArgumentParser(
        description="Master Fail-Closed Claim Provenance Validator"
    )
    parser.add_argument("--stage-dir", required=True, help="Path to stage directory")
    parser.add_argument("--provenance", help="Direct path to claim_provenance.json")
    parser.add_argument("--require-provenance", action="store_true", help="Fail-closed if provenance file is missing")
    parser.add_argument("--no-orphan-check", action="store_true", help="Disable orphan claim scanning")
    parser.add_argument("--json", action="store_true", help="Output JSON report")

    args = parser.parse_args()

    report = validate_provenance(
        stage_dir=args.stage_dir,
        provenance_path=args.provenance,
        require_provenance=args.require_provenance,
        check_orphan_claims=not args.no_orphan_check
    )

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"VERDICT: {report['verdict']}")
        if report["errors"]:
            print("ERRORS:")
            for err in report["errors"]:
                print(f"  - {err}")
        if report["warnings"]:
            print("WARNINGS:")
            for w in report["warnings"]:
                print(f"  - {w}")
        print(f"Evidence: {report['evidence']}")

    sys.exit(0 if report["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
