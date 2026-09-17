#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compute descriptive statistics and demographic distributions.
"""
import argparse
import json
import os
import sys
import pandas as pd
import numpy as np

def run_descriptives(data_path, vars_list, output_path):
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        sys.exit(1)
        
    df = pd.read_excel(data_path) if data_path.endswith(('.xlsx', '.xls')) else pd.read_csv(data_path)
    
    selected_vars = [v.strip() for v in vars_list.split(',')] if vars_list else df.select_dtypes(include=[np.number]).columns.tolist()
    
    results = []
    for var in selected_vars:
        if var not in df.columns:
            continue
        s = df[var].dropna()
        n = len(s)
        mean = float(s.mean())
        sd = float(s.std())
        se = float(sd / np.sqrt(n)) if n > 0 else 0.0
        skew = float(s.skew())
        kurt = float(s.kurtosis())
        min_v = float(s.min())
        max_v = float(s.max())
        
        results.append({
            "variable": var,
            "n": n,
            "mean": round(mean, 2),
            "sd": round(sd, 2),
            "se": round(se, 2),
            "min": round(min_v, 2),
            "max": round(max_v, 2),
            "skewness": round(skew, 3),
            "kurtosis": round(kurt, 3),
            "normality_skew_status": "NORMAL" if abs(skew) <= 0.85 else "SLIGHT_ASYMMETRY" if abs(skew) <= 2.0 else "NON_NORMAL"
        })

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"descriptives": results}, f, indent=2)
    print(f"Descriptive statistics exported to {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Compute descriptive statistics")
    parser.add_argument('--data', required=True, help="Path to dataset")
    parser.add_argument('--vars', default="", help="Comma-separated variable names")
    parser.add_argument('--output', default="descriptives.json", help="Path to output JSON")
    args = parser.parse_args()
    run_descriptives(args.data, args.vars, args.output)
