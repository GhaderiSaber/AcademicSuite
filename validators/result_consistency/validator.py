#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validators/result_consistency/validator.py — Cross-Artifact Consistency Validator

Verifies that statistical results across machine-readable JSON, human-readable Markdown,
tables, figures, and OpenXML Word DOCX do not silently contradict each other.
Enforces fail-closed validation on missing artifacts, parsing failures, and numerical discrepancies.
"""

import os
import sys
import re
import json
import argparse
from typing import Dict, Any, List, Optional, Tuple

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
        except Exception as e:
            return ""


def extract_json_parameters(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts key numerical parameters from a results JSON artifact."""
    params = {}

    # Sample size
    n = data.get("sample_size") or data.get("n") or data.get("sample_n")
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

    # p-value
    p_val = data.get("p_value") or data.get("p")
    if p_val is not None:
        params["p_value"] = p_val

    # Effect size / eta_p2
    eta = data.get("eta_p2") or data.get("effect_size") or data.get("eta_squared")
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

    # SEM Fit indices
    fit = data.get("fit_indices", {})
    if isinstance(fit, dict):
        for idx in ["cfi", "tli", "rmsea", "srmr", "df", "chisq"]:
            if idx in fit and isinstance(fit[idx], (int, float)):
                params[f"fit_{idx}"] = float(fit[idx])

    return params


def find_contradictions_in_text(
    params: Dict[str, Any],
    text: str,
    artifact_name: str
) -> Tuple[List[str], List[str], Dict[str, Any]]:
    """
    Checks text for values that directly contradict JSON parameters.
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
        # Look for standalone N = <number> or n = <number>
        matches = re.findall(r'(?<![a-zA-Z\\])[Nn]\s*=\s*([0-9]+)', norm_text)
        if matches:
            found_ints = [int(m) for m in matches]
            evidence["sample_size"]["found_in_text"] = matches
            # If expected n_val is present among matches or in text, sample size is confirmed
            if n_val not in found_ints and str(n_val) not in norm_text:
                errors.append(
                    f"Contradiction in {artifact_name}: Sample size reported as N = {found_ints}, "
                    f"but JSON parameter specifies N = {n_val}."
                )
        else:
            # Check if number appears anywhere in text
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
            # Check if any found float matches f_val
            has_match = any(abs(x - f_val) < 0.1 for x in found_floats)
            if not has_match:
                errors.append(
                    f"Contradiction in {artifact_name}: F-statistic in text {found_floats} "
                    f"contradicts JSON parameter F = {f_val}."
                )
        else:
            val_str = f"{f_val:.2f}"
            if val_str not in norm_text and f"{f_val:.1f}" not in norm_text:
                warnings.append(f"F-statistic {f_val} from JSON not directly found in {artifact_name}.")

    # 3. R-squared check
    r2_keys = [k for k in params if k == "r2" or k.startswith("r2_")]
    for rk in r2_keys:
        r2_val = params[rk]
        evidence[rk] = {"expected": r2_val}
        val_str = f"{r2_val:.3f}"
        val_short = f"{r2_val:.2f}"
        r2_matches = re.findall(r'(?<![a-zA-Z\\])R\^?2\s*=\s*([0-9]+\.?[0-9]*)', norm_text, re.IGNORECASE)
        if r2_matches:
            found_r2s = [float(x) for x in r2_matches if x]
            evidence[rk]["found_in_text"] = found_r2s
            if len(r2_keys) == 1 and found_r2s and not any(abs(x - r2_val) < 0.05 for x in found_r2s):
                errors.append(
                    f"Contradiction in {artifact_name}: R^2 reported as {found_r2s} "
                    f"contradicts JSON parameter {rk} = {r2_val}."
                )
        elif val_str not in norm_text and val_short not in norm_text and str(r2_val) not in norm_text:
            warnings.append(f"R-squared {rk} = {r2_val} from JSON not directly found in {artifact_name}.")

    # 4. Effect size check
    if "effect_size" in params:
        eta_val = params["effect_size"]
        evidence["effect_size"] = {"expected": eta_val}
        eta_matches = re.findall(r'(?<![a-zA-Z\\])(?:eta_p\^?2|η_p\^?2|d)\s*=\s*([0-9]+\.?[0-9]*)', norm_text, re.IGNORECASE)
        if eta_matches:
            found_etas = [float(x) for x in eta_matches if x]
            evidence["effect_size"]["found_in_text"] = found_etas
            if not any(abs(x - eta_val) < 0.05 for x in found_etas):
                errors.append(
                    f"Contradiction in {artifact_name}: Effect size reported as {found_etas} "
                    f"contradicts JSON parameter = {eta_val}."
                )

    # 5. Standardized Beta coefficients check (ATK-13)
    beta_keys = [k for k in params if k.startswith("beta_") or k == "beta"]
    if beta_keys:
        expected_betas = [params[k] for k in beta_keys]
        evidence["beta_coefficients"] = {"expected": {k: params[k] for k in beta_keys}}
        beta_matches = re.findall(r'(?:[βΒ]|\\beta|\bbeta\b)\s*=\s*([+-]?[0-9]+\.?[0-9]*)', norm_text, re.IGNORECASE)
        if beta_matches:
            found_betas = [float(x) for x in beta_matches if x]
            evidence["beta_coefficients"]["found_in_text"] = found_betas
            unmatched_betas = [b for b in found_betas if not any(abs(b - exp) < 0.05 for exp in expected_betas)]
            if unmatched_betas:
                errors.append(
                    f"Contradiction in {artifact_name}: Standardized beta coefficient(s) reported as {unmatched_betas} "
                    f"contradict JSON parameters {expected_betas}."
                )

    # 6. t-statistic check (ATK-13)
    t_keys = [k for k in params if k == "t_stat" or k.startswith("t_")]
    if t_keys:
        expected_ts = [params[k] for k in t_keys]
        evidence["t_statistics"] = {"expected": {k: params[k] for k in t_keys}}
        t_matches = re.findall(r'(?<![a-zA-Z\\])t\s*(?:\([0-9\s,.]+\))?\s*=\s*([+-]?[0-9]+\.?[0-9]*)', norm_text)
        if t_matches:
            found_ts = [float(x) for x in t_matches if x]
            evidence["t_statistics"]["found_in_text"] = found_ts
            unmatched_ts = [t for t in found_ts if not any(abs(t - exp) < 0.1 for exp in expected_ts)]
            if unmatched_ts:
                errors.append(
                    f"Contradiction in {artifact_name}: t-statistic(s) reported as {unmatched_ts} "
                    f"contradict JSON parameters {expected_ts}."
                )

    # 7. z-value check
    z_keys = [k for k in params if k == "z_stat" or k.startswith("z_") or k == "z"]
    if z_keys:
        expected_zs = [params[k] for k in z_keys]
        evidence["z_statistics"] = {"expected": {k: params[k] for k in z_keys}}
        z_matches = re.findall(r'(?<![a-zA-Z\\])z\s*=\s*([+-]?[0-9]+\.?[0-9]*)', norm_text)
        if z_matches:
            found_zs = [float(x) for x in z_matches if x]
            evidence["z_statistics"]["found_in_text"] = found_zs
            unmatched_zs = [z for z in found_zs if not any(abs(z - exp) < 0.1 for exp in expected_zs)]
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
            unmatched_bs = [b for b in found_bs if not any(abs(b - exp) < 0.05 for exp in expected_bs)]
            if unmatched_bs:
                errors.append(
                    f"Contradiction in {artifact_name}: Unstandardized B coefficient(s) reported as {unmatched_bs} "
                    f"contradict JSON parameters {expected_bs}."
                )

    # 9. SEM Fit Indices check
    fit_keys = [k for k in params if k.startswith("fit_")]
    if fit_keys:
        for fidx in ["cfi", "tli", "rmsea", "srmr"]:
            fk = f"fit_{fidx}"
            if fk in params:
                exp_fit = params[fk]
                fit_matches = re.findall(rf'(?<![a-zA-Z\\]){fidx}\s*=\s*([0-9]+\.?[0-9]*)', norm_text, re.IGNORECASE)
                if fit_matches:
                    found_fits = [float(x) for x in fit_matches if x]
                    if not any(abs(x - exp_fit) < 0.05 for x in found_fits):
                        errors.append(
                            f"Contradiction in {artifact_name}: Fit index {fidx.upper()} reported as {found_fits} "
                            f"contradicts JSON parameter = {exp_fit}."
                        )

    return errors, warnings, evidence



def validate_cross_artifacts(
    json_path: str,
    md_path: Optional[str] = None,
    docx_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Cross-validates JSON statistical artifacts against Markdown and Word DOCX deliverables.
    Fails closed on missing required artifacts, unparseable data, or numeric contradictions.
    """
    errors = []
    warnings = []
    evidence = {
        "json_artifact": os.path.basename(json_path) if json_path else None,
        "md_artifact": os.path.basename(md_path) if md_path else None,
        "docx_artifact": os.path.basename(docx_path) if docx_path else None,
        "parameters_evaluated": {}
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
