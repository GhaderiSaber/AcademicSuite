#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean datasets, reverse-code items, and compute composite subscale scores.
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

import pandas as pd
import numpy as np

def clean_data(data_path, spec_path, output_data, output_log):
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        sys.exit(1)
        
    df = pd.read_excel(data_path) if data_path.endswith(('.xlsx', '.xls')) else pd.read_csv(data_path)
    
    spec = {}
    if spec_path and os.path.exists(spec_path):
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec = json.load(f)

    reversed_items = []
    scales = spec.get("scales", {})
    
    # Reverse coding: (max + min) - x
    for scale_name, scale_info in scales.items():
        min_val = scale_info.get("min", 1)
        max_val = scale_info.get("max", 5)
        for rev_col in scale_info.get("reverse_items", []):
            if rev_col in df.columns:
                df[rev_col] = (max_val + min_val) - df[rev_col]
                reversed_items.append(rev_col)
                
        # Subscale composite summation
        subscales = scale_info.get("subscales", {})
        for sub_name, items in subscales.items():
            valid_items = [c for c in items if c in df.columns]
            if valid_items:
                df[sub_name] = df[valid_items].sum(axis=1)

    os.makedirs(os.path.dirname(os.path.abspath(output_data)), exist_ok=True)
    if output_data.endswith('.csv'):
        df.to_csv(output_data, index=False)
    else:
        df.to_excel(output_data, index=False)

    log = {
        "source_data": data_path,
        "output_data": output_data,
        "reversed_items_count": len(reversed_items),
        "reversed_items": reversed_items,
        "computed_subscales": [s for sc in scales.values() for s in sc.get("subscales", {}).keys()],
        "status": "CLEANING_COMPLETE"
    }

    with open(output_log, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2)
    print(f"Cleaned dataset saved to {output_data}. Log saved to {output_log}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Clean data and score psychometric scales")
    parser.add_argument('--data', required=True, help="Path to raw dataset")
    parser.add_argument('--spec', required=True, help="Path to scale specification JSON")
    parser.add_argument('--output-data', default="data_cleaned.xlsx", help="Cleaned dataset output")
    parser.add_argument('--output-log', default="cleaning_log.json", help="Cleaning log output")
    args = parser.parse_args()
    clean_data(args.data, args.spec, args.output_data, args.output_log)
