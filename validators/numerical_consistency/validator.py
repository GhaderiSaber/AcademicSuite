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
        return {"verdict": "FAIL", "errors": [f"Stats file not found: {stats_path}"]}

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

    # Check sample size and df
    n = sample_n or data.get("sample_size") or data.get("n")
    if n and "fit_indices" in data:
        df_val = data["fit_indices"].get("df")
        if df_val and df_val <= 0:
            errors.append(f"Invalid SEM degrees of freedom: {df_val}")

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
            t_val = coef.get("t")
            p_val = coef.get("p_value")
            if p_val == "0" or p_val == ".000" or p_val == "0.000":
                errors.append(f"Prohibited p = .000 reported for predictor {coef.get('predictor')}. Must use p < .001.")

    verdict = "FAIL" if errors else ("NEEDS_REVIEW" if warnings else "PASS")
    return {
        "validator": "numerical_consistency",
        "verdict": verdict,
        "errors": errors,
        "warnings": warnings,
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
