#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, json, argparse, re

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

def validate_results(json_path, md_path):
    if not os.path.exists(json_path):
        return {"verdict": "FAIL", "errors": [f"JSON artifact missing: {json_path}"]}
    if not os.path.exists(md_path):
        return {"verdict": "FAIL", "errors": [f"Markdown artifact missing: {md_path}"]}

    with open(json_path, 'r', encoding='utf-8') as f:
        stats = json.load(f)
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    errors = []
    warnings = []

    # Check key stats presence in text
    f_stat = stats.get("f_stat")
    if f_stat and str(f_stat) not in md_text:
        warnings.append(f"F-statistic {f_stat} from JSON not directly found in Markdown text.")

    r2 = stats.get("r2")
    if r2 and str(r2) not in md_text:
        warnings.append(f"R-squared {r2} from JSON not directly found in Markdown text.")

    verdict = "FAIL" if errors else ("NEEDS_REVIEW" if warnings else "PASS")
    return {
        "validator": "result_consistency",
        "verdict": verdict,
        "errors": errors,
        "warnings": warnings,
        "artifacts_checked": [os.path.basename(json_path), os.path.basename(md_path)]
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Validate result consistency")
    parser.add_argument('--json', required=True, help="Path to JSON stats artifact")
    parser.add_argument('--md', required=True, help="Path to Markdown artifact")
    args = parser.parse_args()
    res = validate_results(args.json, args.md)
    print(json.dumps(res, indent=2))
    sys.exit(0 if res["verdict"] == "PASS" else 1)
