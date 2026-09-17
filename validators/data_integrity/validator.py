#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, json, argparse

# Virtualenv auto-discovery
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

def validate_data(report_path):
    if not os.path.exists(report_path):
        return {"verdict": "FAIL", "errors": [f"Curation report not found: {report_path}"]}

    with open(report_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    errors = []
    warnings = []

    missing_rate = data.get("missing_rate", 0.0)
    if missing_rate > 0.15:
        errors.append(f"Excessive missingness rate: {missing_rate * 100:.1f}% exceeds 15% threshold.")
    elif missing_rate > 0.05:
        warnings.append(f"Moderate missingness rate: {missing_rate * 100:.1f}%. Verify Little's MCAR.")

    mcar = data.get("mcar_test", {})
    if mcar.get("p_value", 1.0) <= 0.05 and missing_rate > 0.05:
        errors.append(f"Little's MCAR test failed (p = {mcar.get('p_value')}). Missingness is MAR/MNAR.")

    outliers = data.get("multivariate_outliers_flagged", [])
    if len(outliers) > 0:
        warnings.append(f"{len(outliers)} multivariate outliers flagged. Ensure exclusion is logged.")

    verdict = "FAIL" if errors else ("NEEDS_REVIEW" if warnings else "PASS")
    return {
        "validator": "data_integrity",
        "verdict": verdict,
        "errors": errors,
        "warnings": warnings,
        "metrics": {"missing_rate": missing_rate, "outliers_count": len(outliers)}
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Validate data integrity")
    parser.add_argument('--report', required=True, help="Path to curation report JSON")
    args = parser.parse_args()
    res = validate_data(args.report)
    print(json.dumps(res, indent=2))
    sys.exit(0 if res["verdict"] == "PASS" else 1)
