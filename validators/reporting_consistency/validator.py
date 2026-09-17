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

CLICHES = [
    "شایان ذکر است", "در جهان پرشتاب امروزی", "پرواضح است", "لازم به ذکر است",
    "بر کسی پوشیده نیست", "همانطور که می‌دانیم"
]

def validate_reporting(file_path):
    if not os.path.exists(file_path):
        return {"verdict": "FAIL", "errors": [f"File not found: {file_path}"]}

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    errors = []
    warnings = []

    # 1. Check prohibited p = .000
    if re.search(r'p\s*=\s*\.?000', text, re.IGNORECASE) or '۰.۰۰۰' in text or '.۰۰۰' in text:
        errors.append("Prohibited p = .000 found. Must report strictly as p < .001 or ۰.۰۰۱ > p.")

    # 2. Check Persian leading zero violation: e.g. " .۰۵" or " .۰۰۱" without leading zero
    if re.search(r'[^\d۰-۹]\.[۰-۹]+', text) or re.search(r'\s\.[0-9]+', text):
        errors.append("Persian leading zero violation: numbers bounded between 0 and 1 must retain leading zero (۰.۰۵, ۰.۰۰۱).")

    # 3. Check robotic clichés
    for c in CLICHES:
        if c in text:
            errors.append(f"Forbidden robotic AI cliché detected: «{c}». Rephrase into formal academic Persian.")

    verdict = "FAIL" if errors else ("NEEDS_REVIEW" if warnings else "PASS")
    return {
        "validator": "reporting_consistency",
        "verdict": verdict,
        "errors": errors,
        "warnings": warnings,
        "file_audited": os.path.basename(file_path)
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Validate reporting consistency")
    parser.add_argument('--file', required=True, help="Path to text or markdown deliverable")
    args = parser.parse_args()
    res = validate_reporting(args.file)
    print(json.dumps(res, indent=2))
    sys.exit(0 if res["verdict"] == "PASS" else 1)
