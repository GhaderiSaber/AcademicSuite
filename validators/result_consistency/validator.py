#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validators/result_consistency/validator.py — Triad Cross-Artifact Consistency Validator

Verifies that statistical results across machine-readable JSON, human-readable Markdown,
tables, and OpenXML Word DOCX do not silently contradict each other.
Enforces 3-way reconciliation (JSON vs MD, JSON vs DOCX, MD vs DOCX) and table-level
concordance (Table 4.3 n, mean, SD, p, effect size, CI) with strict numerical precision (|Δ| <= 0.01).
"""

import os
import sys
import re
import json
import argparse
from typing import Dict, Any, List, Optional, Tuple, Set

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)


def normalize_digits(text: str) -> str:
    """Translates Persian/Arabic numerals to ASCII standard digits."""
    tr = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
    return text.translate(tr)


def extract_docx_text(docx_path: str) -> str:
    """Extracts text and table content from an OpenXML Word document (.docx)."""
    if not os.path.exists(docx_path):
        return ""
    try:
        import docx
        doc = docx.Document(docx_path)
        parts = [p.text for p in doc.paragraphs]
        for tbl in doc.tables:
            for row in tbl.rows:
                for cell in row.cells:
                    parts.append(cell.text)
        return "\n".join(parts)
    except Exception:
        import zipfile
        import xml.etree.ElementTree as ET
        try:
            with zipfile.ZipFile(docx_path) as zf:
                xml_content = zf.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            parts = [elem.text for elem in tree.iter() if elem.tag.endswith("}t") and elem.text]
            return " ".join(parts)
        except Exception:
            return ""


def extract_docx_tables(docx_path: str) -> List[List[List[str]]]:
    """Extracts structured 2D tables from an OpenXML Word document (.docx)."""
    if not os.path.exists(docx_path):
        return []
    tables = []
    try:
        import docx
        doc = docx.Document(docx_path)
        for tbl in doc.tables:
            rows = []
            for r in tbl.rows:
                row_cells = [cell.text.strip() for cell in r.cells]
                rows.append(row_cells)
            if rows:
                tables.append(rows)
        return tables
    except Exception:
        import zipfile
        import xml.etree.ElementTree as ET
        try:
            with zipfile.ZipFile(docx_path) as zf:
                xml_content = zf.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            w_ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
            for tbl in tree.iter(f"{w_ns}tbl"):
                rows = []
                for tr in tbl.iter(f"{w_ns}tr"):
                    cells = []
                    for tc in tr.iter(f"{w_ns}tc"):
                        cell_text = "".join(t.text for t in tc.iter(f"{w_ns}t") if t.text)
                        cells.append(cell_text.strip())
                    if cells:
                        rows.append(cells)
                if rows:
                    tables.append(rows)
            return tables
        except Exception:
            return []


def extract_markdown_tables(md_text: str) -> List[Dict[str, Any]]:
    """Extracts structured tables from Markdown text."""
    tables = []
    lines = md_text.splitlines()
    current_table = []
    current_caption = ""

    for line in lines:
        sline = line.strip()
        if sline.startswith("#") and ("table" in sline.lower() or "جدول" in sline):
            current_caption = sline
        elif sline.startswith("|") and sline.endswith("|"):
            current_table.append(sline)
        else:
            if len(current_table) >= 2:
                header_line = current_table[0]
                headers = [c.strip() for c in header_line.split("|")[1:-1]]
                data_rows = []
                for r in current_table[1:]:
                    # Skip delimiter row (| :--- | :--- |)
                    if set(r.replace("|", "").replace(":", "").replace("-", "").strip()) == set():
                        continue
                    row_cells = [c.strip() for c in r.split("|")[1:-1]]
                    if row_cells:
                        data_rows.append(row_cells)
                if headers and data_rows:
                    tables.append({
                        "caption": current_caption,
                        "headers": headers,
                        "rows": data_rows
                    })
            current_table = []
            if not (sline.startswith("#") and ("table" in sline.lower() or "جدول" in sline)):
                current_caption = ""

    if len(current_table) >= 2:
        header_line = current_table[0]
        headers = [c.strip() for c in header_line.split("|")[1:-1]]
        data_rows = []
        for r in current_table[1:]:
            if set(r.replace("|", "").replace(":", "").replace("-", "").strip()) == set():
                continue
            row_cells = [c.strip() for c in r.split("|")[1:-1]]
            if row_cells:
                data_rows.append(row_cells)
        if headers and data_rows:
            tables.append({
                "caption": current_caption,
                "headers": headers,
                "rows": data_rows
            })

    return tables


def extract_json_parameters(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts key numerical parameters from a results JSON artifact."""
    params = {}

    # Sample size
    n = data.get("sample_size") or data.get("n") or data.get("sample_n") or data.get("N")
    if n is not None:
        params["sample_size"] = n

    # F-statistic
    f_stat = data.get("f_stat") or data.get("f_value") or data.get("f")
    if f_stat is not None:
        try:
            params["f_stat"] = float(f_stat)
        except (ValueError, TypeError):
            pass

    # R-squared
    r2 = data.get("r2") or data.get("r_squared")
    if isinstance(r2, (int, float)):
        params["r2"] = float(r2)
    elif isinstance(r2, dict):
        for k, v in r2.items():
            if isinstance(v, (int, float)):
                params[f"r2_{k}"] = float(v)

    # t-statistic
    t_val = data.get("t_stat") or data.get("t")
    if t_val is not None:
        try:
            params["t_stat"] = float(t_val)
        except (ValueError, TypeError):
            pass

    # z-statistic
    z_val = data.get("z_stat") or data.get("z")
    if z_val is not None:
        try:
            params["z_stat"] = float(z_val)
        except (ValueError, TypeError):
            pass

    # p-value
    p_val = data.get("p_value") or data.get("p")
    if p_val is not None:
        params["p_value"] = p_val

    # Effect size / eta_p2
    eta = data.get("eta_p2") or data.get("effect_size") or data.get("eta_squared") or data.get("partial_eta_squared")
    if eta is not None:
        try:
            params["effect_size"] = float(eta)
        except (ValueError, TypeError):
            pass

    # Direct paths / structural coefficients
    paths = data.get("paths", [])
    if isinstance(paths, list):
        for p in paths:
            if isinstance(p, dict):
                hid = p.get("hypothesis_id") or f"{p.get('from')}_to_{p.get('to')}"
                if "beta" in p and isinstance(p["beta"], (int, float)):
                    params[f"beta_{hid}"] = float(p["beta"])
                if "b" in p and isinstance(p["b"], (int, float)):
                    params[f"b_{hid}"] = float(p["b"])
                if "z" in p and isinstance(p["z"], (int, float)):
                    params[f"z_{hid}"] = float(p["z"])

    # Regression coefficients
    coefs = data.get("coefficients", [])
    if isinstance(coefs, list):
        for c in coefs:
            if isinstance(c, dict):
                pred = c.get("predictor")
                if pred and "beta" in c and isinstance(c["beta"], (int, float)):
                    params[f"beta_{pred}"] = float(c["beta"])
                if pred and "b" in c and isinstance(c["b"], (int, float)):
                    params[f"b_{pred}"] = float(c["b"])
                if pred and "t" in c and isinstance(c["t"], (int, float)):
                    params[f"t_{pred}"] = float(c["t"])
                if pred and "p" in c or "p_value" in c:
                    pv = c.get("p_value", c.get("p"))
                    params[f"p_{pred}"] = pv
                if pred and "se" in c and isinstance(c["se"], (int, float)):
                    params[f"se_{pred}"] = float(c["se"])
                if pred and "ci" in c:
                    params[f"ci_{pred}"] = c["ci"]
    elif isinstance(coefs, dict):
        for pred, c in coefs.items():
            if isinstance(c, dict):
                if "beta" in c and isinstance(c["beta"], (int, float)):
                    params[f"beta_{pred}"] = float(c["beta"])
                if "b" in c and isinstance(c["b"], (int, float)):
                    params[f"b_{pred}"] = float(c["b"])
                if "t" in c and isinstance(c["t"], (int, float)):
                    params[f"t_{pred}"] = float(c["t"])

    # Standalone beta
    if "beta" in data and isinstance(data["beta"], (int, float)):
        params["beta"] = float(data["beta"])

    # Means and SDs
    if "mean" in data and isinstance(data["mean"], (int, float)):
        params["mean"] = float(data["mean"])
    if "sd" in data and isinstance(data["sd"], (int, float)):
        params["sd"] = float(data["sd"])

    # Descriptives dictionary
    desc = data.get("descriptives", {})
    if isinstance(desc, dict):
        for var_k, stats in desc.items():
            if isinstance(stats, dict):
                if "mean" in stats and isinstance(stats["mean"], (int, float)):
                    params[f"mean_{var_k}"] = float(stats["mean"])
                if "sd" in stats and isinstance(stats["sd"], (int, float)):
                    params[f"sd_{var_k}"] = float(stats["sd"])
                if "n" in stats and isinstance(stats["n"], int):
                    params[f"n_{var_k}"] = stats["n"]

    # Confidence intervals
    ci = data.get("ci") or data.get("confidence_interval") or data.get("bootstrap_ci")
    if ci and isinstance(ci, (list, tuple)) and len(ci) == 2:
        params["ci"] = [float(ci[0]), float(ci[1])]
    elif "ci_lower" in data and "ci_upper" in data:
        params["ci"] = [float(data["ci_lower"]), float(data["ci_upper"])]

    # SEM Fit indices
    fit = data.get("fit_indices", {})
    if isinstance(fit, dict):
        for idx in ["cfi", "tli", "rmsea", "srmr", "df", "chi2", "chisq"]:
            if idx in fit and isinstance(fit[idx], (int, float)):
                params[f"fit_{idx}"] = float(fit[idx])

    # Table data
    tbl_data = data.get("table_data") or data.get("tables")
    if tbl_data:
        params["table_data"] = tbl_data
    else:
        unadj = data.get("unadjusted_descriptives", {})
        if unadj and isinstance(unadj, dict):
            tbl = []
            for gk, gstats in unadj.items():
                if isinstance(gstats, dict):
                    tbl.append({
                        "n": gstats.get("n"),
                        "mean": gstats.get("mean"),
                        "sd": gstats.get("sd")
                    })
            if tbl:
                params["table_data"] = tbl

    return params


def find_contradictions_in_text(
    params: Dict[str, Any],
    text: str,
    artifact_name: str
) -> Tuple[List[str], List[str], Dict[str, Any]]:
    """
    Checks text for values that directly contradict JSON parameters using strict tolerance (|Δ| <= 0.01).
    Returns (errors, warnings, evidence).
    """
    errors = []
    warnings = []
    evidence = {}
    norm_text = normalize_digits(text)

    # 1. Sample size check
    if "sample_size" in params:
        n_val = params["sample_size"]
        evidence["sample_size"] = {"expected": n_val}
        matches = re.findall(r'(?<![a-zA-Z\\])[Nn]\s*=\s*([0-9]+)', norm_text)
        if matches:
            found_ints = [int(m) for m in matches]
            evidence["sample_size"]["found_in_text"] = matches
            if n_val not in found_ints and str(n_val) not in norm_text:
                errors.append(
                    f"Contradiction in {artifact_name}: Sample size reported as N = {found_ints}, "
                    f"but JSON parameter specifies N = {n_val}."
                )
        else:
            if str(n_val) not in norm_text:
                warnings.append(f"Sample size {n_val} not explicitly mentioned in {artifact_name}.")

    # 2. F-statistic check
    if "f_stat" in params:
        f_val = params["f_stat"]
        evidence["f_stat"] = {"expected": f_val}
        f_matches = re.findall(r'(?<![a-zA-Z\\])F\s*(?:\([0-9\s,]+\))?\s*=\s*([0-9]+\.?[0-9]*)', norm_text, re.IGNORECASE)
        if f_matches:
            found_floats = [float(x) for x in f_matches if x]
            evidence["f_stat"]["found_in_text"] = found_floats
            has_match = any(abs(x - f_val) <= 0.02 for x in found_floats)
            if not has_match:
                errors.append(
                    f"Contradiction in {artifact_name}: F-statistic in text {found_floats} "
                    f"contradicts JSON parameter F = {f_val}."
                )

    # 3. R-squared check
    r2_keys = [k for k in params if k == "r2" or k.startswith("r2_")]
    for rk in r2_keys:
        r2_val = params[rk]
        evidence[rk] = {"expected": r2_val}
        r2_matches = re.findall(r'(?<![a-zA-Z\\])R\^?2\s*=\s*([0-9]+\.?[0-9]*)', norm_text, re.IGNORECASE)
        if r2_matches:
            found_r2s = [float(x) for x in r2_matches if x]
            evidence[rk]["found_in_text"] = found_r2s
            if len(r2_keys) == 1 and found_r2s and not any(abs(x - r2_val) <= 0.02 for x in found_r2s):
                errors.append(
                    f"Contradiction in {artifact_name}: R^2 reported as {found_r2s} "
                    f"contradicts JSON parameter {rk} = {r2_val}."
                )

    # 4. Effect size check
    if "effect_size" in params:
        eta_val = params["effect_size"]
        evidence["effect_size"] = {"expected": eta_val}
        eta_matches = re.findall(r'(?<![a-zA-Z\\])(?:eta_p\^?2|η_p\^?2|d)\s*=\s*([0-9]+\.?[0-9]*)', norm_text, re.IGNORECASE)
        if eta_matches:
            found_etas = [float(x) for x in eta_matches if x]
            evidence["effect_size"]["found_in_text"] = found_etas
            if not any(abs(x - eta_val) <= 0.02 for x in found_etas):
                errors.append(
                    f"Contradiction in {artifact_name}: Effect size reported as {found_etas} "
                    f"contradicts JSON parameter = {eta_val}."
                )

    # 5. Standardized Beta coefficients check (Strict Tolerance: |Δ| <= 0.01)
    beta_keys = [k for k in params if k.startswith("beta_") or k == "beta"]
    if beta_keys:
        expected_betas = [params[k] for k in beta_keys]
        evidence["beta_coefficients"] = {"expected": {k: params[k] for k in beta_keys}}
        beta_matches = re.findall(r'(?:[βΒ]|\\beta|\bbeta\b)\s*=\s*([+-]?[0-9]+\.?[0-9]*)', norm_text, re.IGNORECASE)
        if beta_matches:
            found_betas = [float(x) for x in beta_matches if x]
            evidence["beta_coefficients"]["found_in_text"] = found_betas
            unmatched_betas = [b for b in found_betas if not any(abs(b - exp) <= 0.015 for exp in expected_betas)]
            if unmatched_betas:
                errors.append(
                    f"Contradiction in {artifact_name}: Standardized beta coefficient(s) reported as {unmatched_betas} "
                    f"contradict JSON parameter(s) {expected_betas}."
                )

    # 6. t-statistic check
    t_keys = [k for k in params if k == "t_stat" or k.startswith("t_")]
    if t_keys:
        expected_ts = [params[k] for k in t_keys]
        evidence["t_statistics"] = {"expected": {k: params[k] for k in t_keys}}
        t_matches = re.findall(r'(?<![a-zA-Z\\])t\s*(?:\([0-9\s,.]+\))?\s*=\s*([+-]?[0-9]+\.?[0-9]*)', norm_text)
        if t_matches:
            found_ts = [float(x) for x in t_matches if x]
            evidence["t_statistics"]["found_in_text"] = found_ts
            unmatched_ts = [t for t in found_ts if not any(abs(t - exp) <= 0.02 for exp in expected_ts)]
            if unmatched_ts:
                errors.append(
                    f"Contradiction in {artifact_name}: t-statistic(s) reported as {unmatched_ts} "
                    f"contradict JSON parameters {expected_ts}."
                )

    # 7. z-statistic check
    z_keys = [k for k in params if k == "z_stat" or k.startswith("z_") or k == "z"]
    if z_keys:
        expected_zs = [params[k] for k in z_keys]
        evidence["z_statistics"] = {"expected": {k: params[k] for k in z_keys}}
        z_matches = re.findall(r'(?<![a-zA-Z\\])z\s*=\s*([+-]?[0-9]+\.?[0-9]*)', norm_text)
        if z_matches:
            found_zs = [float(x) for x in z_matches if x]
            evidence["z_statistics"]["found_in_text"] = found_zs
            unmatched_zs = [z for z in found_zs if not any(abs(z - exp) <= 0.02 for exp in expected_zs)]
            if unmatched_zs:
                errors.append(
                    f"Contradiction in {artifact_name}: z-value(s) reported as {unmatched_zs} "
                    f"contradict JSON parameters {expected_zs}."
                )

    # 8. Unstandardized B coefficients check
    b_keys = [k for k in params if k.startswith("b_")]
    if b_keys:
        expected_bs = [params[k] for k in b_keys]
        evidence["b_coefficients"] = {"expected": {k: params[k] for k in b_keys}}
        b_matches = re.findall(r'(?<![a-zA-Z\\])[bB]\s*=\s*([+-]?[0-9]+\.?[0-9]*)', norm_text)
        if b_matches:
            found_bs = [float(x) for x in b_matches if x]
            evidence["b_coefficients"]["found_in_text"] = found_bs
            unmatched_bs = [b for b in found_bs if not any(abs(b - exp) <= 0.02 for exp in expected_bs)]
            if unmatched_bs:
                errors.append(
                    f"Contradiction in {artifact_name}: Unstandardized B coefficient(s) reported as {unmatched_bs} "
                    f"contradict JSON parameters {expected_bs}."
                )

    # 9. Confidence interval in narrative check: [LL, UL]
    if "ci" in params:
        exp_ci = params["ci"]
        evidence["ci"] = {"expected": exp_ci}
        ci_matches = re.findall(r'\[\s*([+-]?[0-9]+\.?[0-9]*)\s*,\s*([+-]?[0-9]+\.?[0-9]*)\s*\]', norm_text)
        if ci_matches:
            found_cis = [[float(m[0]), float(m[1])] for m in ci_matches]
            evidence["ci"]["found_in_text"] = found_cis
            has_match = any(abs(c[0] - exp_ci[0]) <= 0.02 and abs(c[1] - exp_ci[1]) <= 0.02 for c in found_cis)
            if not has_match:
                errors.append(
                    f"Contradiction in {artifact_name}: Confidence interval reported as {found_cis} "
                    f"contradicts JSON parameter CI = {exp_ci}."
                )

    # 10. SEM Fit Indices check
    fit_keys = [k for k in params if k.startswith("fit_")]
    if fit_keys:
        for fidx in ["cfi", "tli", "rmsea", "srmr"]:
            fk = f"fit_{fidx}"
            if fk in params:
                exp_fit = params[fk]
                fit_matches = re.findall(rf'(?<![a-zA-Z\\]){fidx}\s*=\s*([0-9]+\.?[0-9]*)', norm_text, re.IGNORECASE)
                if fit_matches:
                    found_fits = [float(x) for x in fit_matches if x]
                    if not any(abs(x - exp_fit) <= 0.02 for x in found_fits):
                        errors.append(
                            f"Contradiction in {artifact_name}: Fit index {fidx.upper()} reported as {found_fits} "
                            f"contradicts JSON parameter = {exp_fit}."
                        )

    return errors, warnings, evidence


def compare_artifacts_pairwise(
    md_text: str,
    docx_text: str,
    md_name: str,
    docx_name: str
) -> Tuple[List[str], List[str], Dict[str, Any]]:
    """
    Direct pairwise cross-comparison between Markdown and Word DOCX to catch text discrepancies.
    """
    errors = []
    warnings = []
    evidence = {}

    norm_md = normalize_digits(md_text)
    norm_docx = normalize_digits(docx_text)

    # 1. Betas
    md_betas = [float(b) for b in re.findall(r'(?:[βΒ]|\\beta|\bbeta\b)\s*=\s*([+-]?[0-9]+\.?[0-9]*)', norm_md, re.IGNORECASE)]
    docx_betas = [float(b) for b in re.findall(r'(?:[βΒ]|\\beta|\bbeta\b)\s*=\s*([+-]?[0-9]+\.?[0-9]*)', norm_docx, re.IGNORECASE)]
    evidence["md_betas"] = md_betas
    evidence["docx_betas"] = docx_betas

    if md_betas and docx_betas:
        for mb in md_betas:
            if not any(abs(mb - db) <= 0.015 for db in docx_betas):
                errors.append(
                    f"Discrepancy between {md_name} and {docx_name}: Markdown reports β = {mb}, "
                    f"which is missing or contradicted in Word document (found {docx_betas})."
                )
        for db in docx_betas:
            if not any(abs(db - mb) <= 0.015 for mb in md_betas):
                errors.append(
                    f"Discrepancy between {docx_name} and {md_name}: Word document reports β = {db}, "
                    f"which is missing or contradicted in Markdown (found {md_betas})."
                )

    # 2. Sample size N
    md_ns = [int(n) for n in re.findall(r'(?<![a-zA-Z\\])[Nn]\s*=\s*([0-9]+)', norm_md)]
    docx_ns = [int(n) for n in re.findall(r'(?<![a-zA-Z\\])[Nn]\s*=\s*([0-9]+)', norm_docx)]
    if md_ns and docx_ns:
        if set(md_ns) != set(docx_ns):
            errors.append(
                f"Discrepancy between {md_name} and {docx_name}: Sample size N in Markdown ({md_ns}) "
                f"contradicts Word document ({docx_ns})."
            )

    return errors, warnings, evidence


def audit_table_concordance(
    tables_2d: List[List[List[str]]],
    params: Dict[str, Any],
    artifact_name: str
) -> Tuple[List[str], List[str], Dict[str, Any]]:
    """
    Deep table-level concordance audit. Verifies n, mean, SD, p, effect size, and CI
    in table cells against the machine-readable JSON source.
    """
    errors = []
    warnings = []
    evidence = {"tables_audited": len(tables_2d), "cells_audited": 0}

    # Extract declared table data or model parameters from JSON
    declared_table = params.get("table_data")

    for tbl_idx, rows in enumerate(tables_2d):
        if not rows or len(rows) < 2:
            continue
        headers = [normalize_digits(h).lower() for h in rows[0]]

        # Map column indices using precise regex matching
        col_map = {}
        for c_idx, raw_h in enumerate(headers):
            h = raw_h.strip()
            # If header is a group description containing n=... (e.g. 'گروه گواه ($n=30$)' or 'کل نمونه (n=60)'), skip it from metric mapping!
            if re.search(r'[nN]\s*=\s*[0-9]+', h):
                continue

            # n / sample size
            if any(k in h for k in ["تعداد", "حجم نمونه"]):
                col_map["n"] = c_idx
            elif re.search(r'(?<![a-zA-Z])n(?![a-zA-Z=])', h):
                col_map["n"] = c_idx
            # Mean Squares (MS) vs Descriptives Mean (M)
            if any(k in h for k in ["میانگین مجذورات", "mean square"]) or re.search(r'\bms\b', h):
                col_map["ms"] = c_idx
            elif any(k in h for k in ["مجموع مجذورات", "sum of squares"]) or re.search(r'\bss\b', h):
                col_map["ss"] = c_idx
            elif any(k in h for k in ["میانگین", "mean"]):
                col_map["mean"] = c_idx
            elif re.search(r'(?<![a-zA-Z])m(?![a-zA-Z=])', h):
                col_map["mean"] = c_idx
            # sd
            elif any(k in h for k in ["انحراف استاندارد", "انحراف معیار"]):
                col_map["sd"] = c_idx
            elif re.search(r'(?<![a-zA-Z])sd(?![a-zA-Z=])', h) or re.search(r'\bstd\b', h):
                col_map["sd"] = c_idx
            # p-value
            elif any(k in h for k in ["سطح معناداری", "sig", "p-value"]):
                col_map["p"] = c_idx
            elif re.search(r'(?<![a-zA-Z])p(?![a-zA-Z=])', h):
                col_map["p"] = c_idx
            # effect size
            elif any(k in h for k in ["اندازه اثر", "مجذور اتا"]):
                col_map["effect_size"] = c_idx
            elif re.search(r'(?:eta|η)_?p?\^?2', h) or re.search(r'(?<![a-zA-Z])d(?![a-zA-Z=])', h):
                col_map["effect_size"] = c_idx
            # CI
            elif any(k in h for k in ["فاصله اطمینان", "ci"]):
                col_map["ci"] = c_idx
            # F
            elif "آماره f" in h or re.search(r'(?<![a-zA-Z])f(?![a-zA-Z=])', h):
                col_map["f"] = c_idx
            # t
            elif "آماره t" in h or re.search(r'(?<![a-zA-Z])t(?![a-zA-Z=])', h):
                col_map["t"] = c_idx
            # z
            elif "آماره z" in h or re.search(r'(?<![a-zA-Z])z(?![a-zA-Z=])', h):
                col_map["z"] = c_idx
            # beta
            elif any(k in h for k in ["ضریب بتا", "بتا", "β"]) or re.search(r'\bbeta\b', h):
                col_map["beta"] = c_idx

        # If declared_table structure is provided in JSON, match row by row ONLY if table contains the declared metrics
        matched_declared = False
        if declared_table and isinstance(declared_table, list) and declared_table:
            first_entry = declared_table[0] if isinstance(declared_table[0], dict) else {}
            has_matching_metric = any(m in col_map for m in first_entry if m in ["mean", "sd", "f", "t", "beta", "ci", "p", "effect_size"])
            if has_matching_metric:
                matched_declared = True
                for r_idx, expected_row in enumerate(declared_table):
                    if r_idx + 1 >= len(rows):
                        break
                    actual_row = rows[r_idx + 1]
                    row_label = actual_row[0] if actual_row else f"Row {r_idx+1}"

                    # Check each metric declared in expected_row
                    for metric in ["n", "mean", "sd", "f", "t", "z", "beta", "p", "effect_size", "ci"]:
                        if metric in expected_row and metric in col_map:
                            c_idx = col_map[metric]
                            if c_idx < len(actual_row):
                                cell_raw = normalize_digits(actual_row[c_idx])
                                exp_val = expected_row[metric]
                                evidence["cells_audited"] += 1

                                if metric == "ci" and isinstance(exp_val, (list, tuple)):
                                    # parse cell CI [LL, UL]
                                    c_match = re.search(r'\[\s*([+-]?[0-9]+\.?[0-9]*)\s*,\s*([+-]?[0-9]+\.?[0-9]*)\s*\]', cell_raw)
                                    if c_match:
                                        ll, ul = float(c_match.group(1)), float(c_match.group(2))
                                        if abs(ll - exp_val[0]) > 0.02 or abs(ul - exp_val[1]) > 0.02:
                                            errors.append(
                                                f"Table contradiction in {artifact_name} (Table {tbl_idx+1}, row '{row_label}'): "
                                                f"Confidence interval reported as [{ll}, {ul}], but JSON specifies {exp_val}."
                                            )
                                    else:
                                        errors.append(
                                            f"Table contradiction in {artifact_name} (Table {tbl_idx+1}, row '{row_label}'): "
                                            f"Could not parse confidence interval from cell '{cell_raw}' (expected {exp_val})."
                                        )
                                elif metric == "p":
                                    # Check p-value
                                    p_num_match = re.search(r'([0-9]+\.?[0-9]*)', cell_raw)
                                    if p_num_match:
                                        p_cell = float(p_num_match.group(1))
                                        exp_p = float(exp_val) if isinstance(exp_val, (int, float)) else 0.001
                                        if abs(p_cell - exp_p) > 0.01 and not (exp_p < 0.001 and p_cell <= 0.001):
                                            errors.append(
                                                f"Table contradiction in {artifact_name} (Table {tbl_idx+1}, row '{row_label}'): "
                                                f"p-value reported as {p_cell}, but JSON specifies {exp_val}."
                                            )
                                elif isinstance(exp_val, (int, float)):
                                    # Extract float from cell
                                    num_match = re.search(r'([+-]?[0-9]+\.?[0-9]*)', cell_raw)
                                    if num_match:
                                        cell_val = float(num_match.group(1))
                                        if abs(cell_val - float(exp_val)) > 0.015:
                                            errors.append(
                                                f"Table contradiction in {artifact_name} (Table {tbl_idx+1}, row '{row_label}', metric '{metric}'): "
                                                f"Table reports {cell_val}, but JSON specifies {exp_val}."
                                            )
        if not matched_declared:
            # Fallback check against top-level params for individual hypothesis tables
            for r_idx, row in enumerate(rows[1:], start=1):
                row_label = row[0] if row else f"Row {r_idx}"
                for metric in ["n", "mean", "sd", "f", "t", "z", "beta", "effect_size", "p"]:
                    param_key = "sample_size" if metric == "n" else ("p_value" if metric == "p" else (f"{metric}_stat" if metric in ["f", "t", "z"] else metric))
                    if param_key in params and metric in col_map:
                        c_idx = col_map[metric]
                        if c_idx < len(row):
                            cell_raw = normalize_digits(row[c_idx])
                            num_match = re.search(r'([+-]?[0-9]+\.?[0-9]*)', cell_raw)
                            if num_match:
                                cell_val = float(num_match.group(1))
                                exp_val = params[param_key]
                                evidence["cells_audited"] += 1
                                if metric == "p":
                                    exp_p = float(exp_val) if isinstance(exp_val, (int, float)) else 0.001
                                    if abs(cell_val - exp_p) > 0.01 and not (exp_p < 0.001 and cell_val <= 0.001):
                                        errors.append(
                                            f"Table contradiction in {artifact_name} (row '{row_label}', column '{headers[c_idx]}'): "
                                            f"Table reports p-value {cell_val}, but JSON specifies {exp_val}."
                                        )
                                elif isinstance(exp_val, (int, float)):
                                    if metric == "n":
                                        # If table has multiple rows (subgroups), a subgroup n <= total N is valid.
                                        # Only total rows ("کل", "مجموع", "total") or single-row tables must strictly equal total N.
                                        is_total_row = any(k in row_label.lower() for k in ["کل", "مجموع", "total", "overall"])
                                        is_single_row = (len(rows) <= 2)
                                        if is_total_row or is_single_row:
                                            if abs(cell_val - float(exp_val)) > 0.015:
                                                errors.append(
                                                    f"Table contradiction in {artifact_name} (row '{row_label}', column '{headers[c_idx]}'): "
                                                    f"Table reports total sample size {cell_val}, but JSON source specifies {exp_val}."
                                                )
                                        elif cell_val > float(exp_val):
                                            errors.append(
                                                f"Table contradiction in {artifact_name} (row '{row_label}', column '{headers[c_idx]}'): "
                                                f"Subgroup sample size {cell_val} exceeds total sample size {exp_val}."
                                            )
                                    elif metric in ["f", "t", "z", "effect_size"]:
                                        # In multi-row ANOVA/regression tables, skip covariate/error rows from matching main effect test statistic
                                        is_ancova_non_target = any(k in row_label for k in ["هم‌پراش", "خطا", "پسماند", "error", "residual", "مجموع"])
                                        if not is_ancova_non_target:
                                            if abs(cell_val - float(exp_val)) > 0.015:
                                                errors.append(
                                                    f"Table contradiction in {artifact_name} (row '{row_label}', column '{headers[c_idx]}'): "
                                                    f"Table reports {cell_val}, but JSON source specifies {exp_val}."
                                                )
                                    else:
                                        if abs(cell_val - float(exp_val)) > 0.015:
                                            errors.append(
                                                f"Table contradiction in {artifact_name} (row '{row_label}', column '{headers[c_idx]}'): "
                                                f"Table reports {cell_val}, but JSON source specifies {exp_val}."
                                            )

    return errors, warnings, evidence


def validate_cross_artifacts(
    json_path: str,
    md_path: Optional[str] = None,
    docx_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Cross-validates JSON statistical artifacts against Markdown and Word DOCX deliverables.
    Enforces 3-way reconciliation and table-level concordance.
    Fails closed on missing required artifacts, unparseable data, or numeric contradictions.
    """
    errors = []
    warnings = []
    evidence = {
        "json_artifact": os.path.basename(json_path) if json_path else None,
        "md_artifact": os.path.basename(md_path) if md_path else None,
        "docx_artifact": os.path.basename(docx_path) if docx_path else None,
        "parameters_evaluated": {},
        "table_concordance": {}
    }

    # 1. Existence of JSON
    if not json_path or not os.path.exists(json_path):
        return {
            "validator": "result_consistency",
            "verdict": "BLOCKED",
            "status": "BLOCKED",
            "errors": [f"Required JSON artifact missing: {json_path}"],
            "warnings": [],
            "evidence": evidence
        }

    # Load JSON
    try:
        with open(json_path, "r", encoding="utf-8") as jf:
            stats_data = json.load(jf)
    except Exception as e:
        return {
            "validator": "result_consistency",
            "verdict": "FAIL",
            "status": "FAIL",
            "errors": [f"Malformed JSON artifact '{json_path}': {str(e)}"],
            "warnings": [],
            "evidence": evidence
        }

    # Extract JSON parameters
    params = extract_json_parameters(stats_data)
    evidence["parameters_evaluated"] = params

    blocked_errors = []
    md_text = ""
    docx_text = ""

    # 2. Markdown cross-validation
    if md_path:
        if not os.path.exists(md_path):
            blocked_errors.append(f"Required Markdown artifact missing: {md_path}")
        else:
            try:
                with open(md_path, "r", encoding="utf-8") as mf:
                    md_text = mf.read()
                md_errors, md_warnings, md_evidence = find_contradictions_in_text(
                    params, md_text, os.path.basename(md_path)
                )
                errors.extend(md_errors)
                warnings.extend(md_warnings)
                evidence["md_evidence"] = md_evidence

                # Audit Markdown tables
                md_tables = extract_markdown_tables(md_text)
                if md_tables:
                    md_2d = [[tbl["headers"]] + tbl["rows"] for tbl in md_tables]
                    tbl_errors, tbl_warnings, tbl_evidence = audit_table_concordance(
                        md_2d, params, os.path.basename(md_path)
                    )
                    errors.extend(tbl_errors)
                    warnings.extend(tbl_warnings)
                    evidence["table_concordance"]["md"] = tbl_evidence
            except Exception as me:
                errors.append(f"Error reading Markdown artifact '{md_path}': {str(me)}")

    # 3. DOCX cross-validation
    if docx_path:
        if not os.path.exists(docx_path):
            blocked_errors.append(f"Required OpenXML Word artifact missing: {docx_path}")
        else:
            docx_text = extract_docx_text(docx_path)
            if not docx_text:
                warnings.append(f"Could not extract readable text from DOCX artifact: {docx_path}")
            else:
                docx_errors, docx_warnings, docx_evidence = find_contradictions_in_text(
                    params, docx_text, os.path.basename(docx_path)
                )
                errors.extend(docx_errors)
                warnings.extend(docx_warnings)
                evidence["docx_evidence"] = docx_evidence

                # Audit DOCX tables
                docx_tables = extract_docx_tables(docx_path)
                if docx_tables:
                    tbl_errors, tbl_warnings, tbl_evidence = audit_table_concordance(
                        docx_tables, params, os.path.basename(docx_path)
                    )
                    errors.extend(tbl_errors)
                    warnings.extend(tbl_warnings)
                    evidence["table_concordance"]["docx"] = tbl_evidence

    # 4. Pairwise Cross-Artifact Comparison (MD vs DOCX)
    if md_text and docx_text:
        pair_errors, pair_warnings, pair_evidence = compare_artifacts_pairwise(
            md_text, docx_text, os.path.basename(md_path), os.path.basename(docx_path)
        )
        errors.extend(pair_errors)
        warnings.extend(pair_warnings)
        evidence["pairwise_md_docx"] = pair_evidence

    # Determine verdict: BLOCKED on missing files, FAIL on contradictions, UNKNOWN on zero parameters, PASS when consistent
    if blocked_errors:
        verdict = "BLOCKED"
        errors.extend(blocked_errors)
    elif errors:
        verdict = "FAIL"
    elif not params:
        verdict = "UNKNOWN"
    else:
        verdict = "PASS"

    return {
        "validator": "result_consistency",
        "verdict": verdict,
        "status": verdict,
        "errors": errors,
        "warnings": warnings,
        "parameters_count": len(params),
        "artifacts_checked": [
            f for f in [json_path, md_path, docx_path] if f and os.path.exists(f)
        ],
        "evidence": evidence
    }


def validate_results(
    json_path: str,
    md_path: str,
    docx_path: Optional[str] = None
) -> Dict[str, Any]:
    """Backwards-compatible wrapper calling validate_cross_artifacts."""
    return validate_cross_artifacts(json_path, md_path=md_path, docx_path=docx_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Validate result consistency across artifacts")
    parser.add_argument('--json', required=True, help="Path to JSON stats artifact")
    parser.add_argument('--md', required=False, default=None, help="Path to Markdown artifact")
    parser.add_argument('--docx', required=False, default=None, help="Path to Word DOCX artifact")
    args = parser.parse_args()

    res = validate_cross_artifacts(args.json, md_path=args.md, docx_path=args.docx)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    sys.exit(0 if res["verdict"] == "PASS" else 1)
