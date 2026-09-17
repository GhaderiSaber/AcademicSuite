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
    if re.search(r'p\s*=\s*0?\.000', text, re.IGNORECASE) or re.search(r'p\s*=\s*۰?\.۰۰۰', text) or re.search(r'۰?\.۰۰۰\s*=\s*p', text):
        errors.append("Prohibited p = .000 found. Must report strictly as p < .001 or ۰.۰۰۱ > p.")

    # 2. Check Persian leading zero violation: e.g. " .۰۵" or " .۰۰۱" without leading zero
    if re.search(r'[^\d۰-۹]\.[۰-۹]+', text) or re.search(r'\s\.[0-9]+', text):
        errors.append("Persian leading zero violation: numbers bounded between 0 and 1 must retain leading zero (۰.۰۵, ۰.۰۰۱).")

    # 3. Check robotic clichés
    for c in CLICHES:
        if c in text:
            errors.append(f"Forbidden robotic AI cliché detected: «{c}». Rephrase into formal academic Persian.")

    # 4. Check 3-Table Standard for Regression / Relationship Hypotheses
    is_regression_hypothesis = (
        ("رگرسیون خطی" in text or "multiple regression" in text.lower() or "رگرسیون چندگانه" in text) and
        ("فرضیه" in text or "hypothesis" in text.lower()) and
        ("جدول" in text or "table" in text.lower()) and
        not any(k in text.lower() for k in ["معادلات ساختاری", "sem", "مسیر ساختاری", "ساختاری", "path analysis", "میانجی"])
    )
    if is_regression_hypothesis:
        has_t1 = "جدول ۱" in text or "Table 1" in text
        has_t2 = "جدول ۲" in text or "Table 2" in text
        has_t3 = "جدول ۳" in text or "Table 3" in text
        if not (has_t1 and has_t2 and has_t3):
            errors.append(
                "Violation of 3-Table Standard for Regression Hypotheses: "
                "Must provide exactly 3 distinct tables: "
                "Table 1 (Correlation Matrix), Table 2 (Model Summary & ANOVA), and Table 3 (Coefficients & Collinearity)."
            )

    # 5. Check SEM Macro Reporting Standard (Table A Fit Indices, Table C Direct Paths, Table D Indirect Paths)
    is_sem_macro = (
        ("معادلات ساختاری" in text or "sem" in text.lower()) and
        ("کلان" in text or "macro" in text.lower()) and
        ("برازش" in text or "fit" in text.lower())
    )
    if is_sem_macro:
        has_fit = any(k in text for k in ["جدول الف", "Table A", "شاخص‌های برازش", "Goodness-of-Fit"])
        has_direct = any(k in text for k in ["جدول ج", "Table C", "مسیرهای مستقیم", "Direct Paths"])
        if not has_fit:
            errors.append("SEM Macro Reporting violation: Table A (Goodness-of-Fit indices) is missing.")
        if not has_direct:
            errors.append("SEM Macro Reporting violation: Table C (Direct structural paths) is missing.")

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
