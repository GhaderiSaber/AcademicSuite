#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, json, argparse

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

def validate_numbers(stats_path, sample_n=None):
    if not os.path.exists(stats_path):
        return {
            "validator": "numerical_consistency",
            "verdict": "BLOCKED",
            "status": "BLOCKED",
            "errors": [f"Stats file not found: {stats_path}"],
            "warnings": [],
            "sample_size_audited": None
        }

    try:
        with open(stats_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return {
            "validator": "numerical_consistency",
            "verdict": "FAIL",
            "status": "FAIL",
            "errors": [f"Malformed JSON artifact '{stats_path}': {str(e)}"],
            "warnings": [],
            "sample_size_audited": None
        }

    errors = []
    warnings = []
    evidence_items = []

    # Check sample size and df
    n = sample_n or data.get("sample_size") or data.get("n")
    if n is not None:
        evidence_items.append("sample_size")
    if "fit_indices" in data:
        evidence_items.append("fit_indices")
        if isinstance(data["fit_indices"], dict):
            df_val = data["fit_indices"].get("df")
            if df_val is not None and df_val <= 0:
                errors.append(f"Invalid SEM degrees of freedom: {df_val}")
            for idx_k in ["cfi", "tli", "rmsea", "srmr", "chi2"]:
                if idx_k in data["fit_indices"]:
                    evidence_items.append(f"fit_{idx_k}")

    # Check regression/ANCOVA parameters if present
    coefs = data.get("coefficients", [])
    if isinstance(coefs, dict):
        coef_list = list(coefs.values()) if all(isinstance(v, dict) for v in coefs.values()) else [coefs]
    elif isinstance(coefs, list):
        coef_list = coefs
    else:
        coef_list = []

    for coef in coef_list:
        if isinstance(coef, dict):
            evidence_items.append(f"coef_{coef.get('predictor', 'unknown')}")
            t_val = coef.get("t")
            p_val = coef.get("p_value")
            if p_val == "0" or p_val == ".000" or p_val == "0.000":
                errors.append(f"Prohibited p = .000 reported for predictor {coef.get('predictor')}. Must use p < .001.")

    # Check other statistical parameters
    for stat_k in ["f_stat", "f_value", "r2", "r_squared", "eta_p2", "effect_size", "paths"]:
        if stat_k in data:
            evidence_items.append(stat_k)

    if errors:
        verdict = "FAIL"
    elif not evidence_items:
        verdict = "UNKNOWN"
    else:
        verdict = "PASS"

    return {
        "validator": "numerical_consistency",
        "verdict": verdict,
        "status": verdict,
        "errors": errors,
        "warnings": warnings,
        "evidence_items_audited": len(evidence_items),
        "sample_size_audited": n
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Validate numerical consistency")
    parser.add_argument('--stats', required=True, help="Path to stats JSON")
    parser.add_argument('--n', type=int, default=None, help="Sample size N")
    args = parser.parse_args()
    res = validate_numbers(args.stats, args.n)
    print(json.dumps(res, indent=2))
    sys.exit(0 if res["verdict"] == "PASS" else 1)
