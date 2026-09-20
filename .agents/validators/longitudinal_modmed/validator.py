#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validators/longitudinal_modmed/validator.py — Validates longitudinal moderated mediation outputs, sample sizes, and bootstrap CI bounds.
"""

import os
import sys
import json
import argparse

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)


def validate_longitudinal_modmed(input_path: str, **kwargs) -> dict:
    if not os.path.exists(input_path):
        return {
            "validator": "longitudinal_modmed",
            "verdict": "FAIL",
            "errors": [f"Input file not found: {input_path}"],
            "warnings": []
        }

    errors = []
    warnings = []

    # Dynamic rules injection
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if data.get("sample_size", 0) < 50:
            errors.append("Sample size too small for longitudinal modeling (N < 50).")

        idx_info = data.get("moderated_mediation_index", {})
        if idx_info.get("bootstrap_samples", 0) < 5000:
            errors.append("Bootstrap resamples must be >= 5,000.")

        if "ci_95_lower" not in idx_info or "ci_95_upper" not in idx_info:
            errors.append("Missing 95% bootstrap confidence intervals.")

        if data.get("verdict") not in ["SUPPORTED", "NOT_SUPPORTED"]:
            errors.append("Invalid model verdict status.")

    except Exception as e:
        errors.append(f"Validation parsing exception: {str(e)}")

    verdict = "FAIL" if errors else ("NEEDS_REVIEW" if warnings else "PASS")
    return {
        "validator": "longitudinal_modmed",
        "verdict": verdict,
        "errors": errors,
        "warnings": warnings,
        "file_audited": os.path.basename(input_path)
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Validates longitudinal moderated mediation outputs, sample sizes, and bootstrap CI bounds.")
    parser.add_argument('--input', required=True, help="Path to input artifact (.json, .xlsx, or .md)")
    args = parser.parse_args()

    result = validate_longitudinal_modmed(args.input)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["verdict"] == "PASS" else 1)
