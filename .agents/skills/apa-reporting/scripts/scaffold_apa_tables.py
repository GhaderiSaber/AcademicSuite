#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scaffold APA 7th edition 3-line tables and format statistical numbers.
"""
import argparse
import json
import os
import sys
# Dynamic discovery of local virtualenv site-packages (.venv / venv)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)


def scaffold_tables(input_json, output_md):
    if not os.path.exists(input_json):
        print(f"Error: {input_json} not found.")
        sys.exit(1)
        
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Convert dictionary to APA 7 markdown table
    lines = [
        "### جدول: یافته‌های آماری (APA 7th Edition)",
        "",
        "| شاخص / متغیر | میانگین (*M*) | انحراف استاندارد (*SD*) | آماره آزمون | سطح معناداری (*p*) |",
        "|:---|:---:|:---:|:---:|:---:|"
    ]

    for item in data.get("descriptives", []):
        var = item.get("variable", "Var")
        m = str(item.get("mean", "0.00"))
        sd = str(item.get("sd", "0.00"))
        lines.append(f"| {var} | {m} | {sd} | — | — |")

    lines.append("")
    lines.append("*یادداشت.* سطح معناداری در سطح ۰.۰۵ ارزیابی شده است. اعداد با صفر قبل از ممیز گزارش شده‌اند.")

    os.makedirs(os.path.dirname(os.path.abspath(output_md)), exist_ok=True)
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"APA 7 table scaffolded to {output_md}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scaffold APA 7 tables")
    parser.add_argument('--input', required=True, help="Path to statistical results JSON")
    parser.add_argument('--output', default="apa7_table.md", help="Path to output Markdown")
    args = parser.parse_args()
    scaffold_tables(args.input, args.output)
