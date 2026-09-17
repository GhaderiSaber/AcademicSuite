#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compute Cronbach's alpha and McDonald's omega for psychometric scales.
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

def run_reliability(data_path, items_str, scale_name, output_path):
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        sys.exit(1)
        
    df = pd.read_excel(data_path) if data_path.endswith(('.xlsx', '.xls')) else pd.read_csv(data_path)
    item_cols = [c.strip() for c in items_str.split(',') if c.strip() in df.columns]
    
    if len(item_cols) < 2:
        print("Error: Reliability requires at least 2 items.")
        sys.exit(1)
        
    item_df = df[item_cols].dropna()
    k = len(item_cols)
    n = len(item_df)
    
    # Cronbach's Alpha
    item_vars = item_df.var(axis=0, ddof=1)
    total_var = item_df.sum(axis=1).var(ddof=1)
    alpha = (k / (k - 1)) * (1 - (item_vars.sum() / total_var)) if total_var > 0 else 0.0
    
    # McDonald's Omega approximation via single-factor loadings
    from sklearn.decomposition import FactorAnalysis
    fa = FactorAnalysis(n_components=1)
    fa.fit(item_df)
    loadings = fa.components_[0]
    u2 = 1 - loadings**2
    omega = (loadings.sum())**2 / ((loadings.sum())**2 + u2.sum()) if ((loadings.sum())**2 + u2.sum()) > 0 else alpha

    report = {
        "scale_name": scale_name,
        "n_items": k,
        "sample_size": n,
        "cronbach_alpha": round(float(alpha), 3),
        "mcdonald_omega": round(float(omega), 3),
        "benchmark_passed": bool(alpha >= 0.70 and omega >= 0.70),
        "status": "RELIABILITY_VERIFIED" if alpha >= 0.70 else "LOW_RELIABILITY"
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"Reliability analysis exported to {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Compute scale reliability")
    parser.add_argument('--data', required=True, help="Path to dataset")
    parser.add_argument('--items', required=True, help="Comma-separated item column names")
    parser.add_argument('--scale-name', default="Scale", help="Scale label")
    parser.add_argument('--output', default="reliability.json", help="Output JSON path")
    args = parser.parse_args()
    run_reliability(args.data, args.items, args.scale_name, args.output)
