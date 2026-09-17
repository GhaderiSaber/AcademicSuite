#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Execute multiple linear regression and collinearity diagnostics.
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
import statsmodels.api as sm

def run_regression(data_path, dv, ivs_str, output_path):
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        sys.exit(1)
        
    df = pd.read_excel(data_path) if data_path.endswith(('.xlsx', '.xls')) else pd.read_csv(data_path)
    ivs = [iv.strip() for iv in ivs_str.split(',') if iv.strip() in df.columns]
    
    sub_df = df[[dv] + ivs].dropna()
    y = sub_df[dv]
    X = sm.add_constant(sub_df[ivs])
    
    model = sm.OLS(y, X).fit()
    
    # Calculate standardized coefficients (beta)
    y_std = (y - y.mean()) / y.std()
    X_std = (sub_df[ivs] - sub_df[ivs].mean()) / sub_df[ivs].std()
    model_std = sm.OLS(y_std, X_std).fit()
    
    coef_table = []
    for iv in ivs:
        b = float(model.params[iv])
        se = float(model.bse[iv])
        beta = float(model_std.params[iv])
        t_val = float(model.tvalues[iv])
        p_val = float(model.pvalues[iv])
        coef_table.append({
            "predictor": iv,
            "b": round(b, 3),
            "se": round(se, 3),
            "beta": round(beta, 3),
            "t": round(t_val, 3),
            "p_value": "< .001" if p_val < 0.001 else str(round(p_val, 3))
        })

    report = {
        "dv": dv,
        "n": len(sub_df),
        "r2": round(float(model.rsquared), 3),
        "adj_r2": round(float(model.rsquared_adj), 3),
        "f_stat": round(float(model.fvalue), 3),
        "f_pvalue": "< .001" if model.f_pvalue < 0.001 else str(round(float(model.f_pvalue), 3)),
        "coefficients": coef_table
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"Regression model results saved to {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Multiple regression analysis")
    parser.add_argument('--data', required=True, help="Path to dataset")
    parser.add_argument('--dv', required=True, help="Dependent variable")
    parser.add_argument('--ivs', required=True, help="Comma-separated independent variables")
    parser.add_argument('--output', default="regression_results.json", help="Output JSON path")
    args = parser.parse_args()
    run_regression(args.data, args.dv, args.ivs, args.output)
