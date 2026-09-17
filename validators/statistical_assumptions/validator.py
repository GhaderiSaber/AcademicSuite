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

def validate_assumptions(assumptions_path):
    if not os.path.exists(assumptions_path):
        return {"verdict": "FAIL", "errors": [f"Assumptions file not found: {assumptions_path}"]}

    with open(assumptions_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    errors = []
    warnings = []

    # 1. Levene's test
    levene = data.get("levene_test", {})
    if not levene.get("homogeneous", True):
        errors.append(f"Homogeneity of variance violated: Levene p = {levene.get('p_value')} <= .05. ANCOVA requires equal variances.")

    # 2. Slope homogeneity
    slope = data.get("slope_homogeneity", {})
    if slope and not slope.get("homogeneous", True):
        errors.append(f"Homogeneity of regression slopes violated: interaction p = {slope.get('p_value')} <= .05. ANCOVA is invalid; Johnson-Neyman required.")

    # 3. Normality
    norm = data.get("normality_shapiro", {})
    for g, res in norm.items():
        if not res.get("normal", True):
            warnings.append(f"Shapiro-Wilk normality violated in group {g} (p = {res.get('p_value')}). Verify skewness/kurtosis.")

    verdict = "FAIL" if errors else ("NEEDS_REVIEW" if warnings else "PASS")
    return {
        "validator": "statistical_assumptions",
        "verdict": verdict,
        "errors": errors,
        "warnings": warnings
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Validate statistical assumptions")
    parser.add_argument('--assumptions', required=True, help="Path to assumptions JSON")
    args = parser.parse_args()
    res = validate_assumptions(args.assumptions)
    print(json.dumps(res, indent=2))
    sys.exit(0 if res["verdict"] == "PASS" else 1)
