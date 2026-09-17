#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify parametric assumptions for GLM and ANCOVA models.
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
from scipy import stats

def check_assumptions(data_path, dv, group_col, cov_col, output_path):
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        sys.exit(1)
        
    df = pd.read_excel(data_path) if data_path.endswith(('.xlsx', '.xls')) else pd.read_csv(data_path)
    
    # 1. Normality across groups
    normality = {}
    groups = df[group_col].dropna().unique()
    for g in groups:
        sub_s = df[df[group_col] == g][dv].dropna()
        if len(sub_s) >= 3:
            w, p = stats.shapiro(sub_s)
            normality[str(g)] = {"w": round(float(w), 3), "p_value": round(float(p), 4), "normal": bool(p > 0.05)}
            
    # 2. Levene's test for homogeneity of variance
    group_data = [df[df[group_col] == g][dv].dropna().values for g in groups]
    stat_l, p_l = stats.levene(*group_data)
    
    # 3. Slope homogeneity (Group x Covariate interaction)
    slope_homogeneity = {}
    if cov_col and cov_col in df.columns:
        import statsmodels.api as sm
        from statsmodels.formula.api import ols
        formula = f"{dv} ~ C({group_col}) * {cov_col}"
        model = ols(formula, data=df).fit()
        table = sm.stats.anova_lm(model, typ=2)
        inter_row = f"C({group_col}):{cov_col}"
        if inter_row in table.index:
            f_val = float(table.loc[inter_row, 'F'])
            p_val = float(table.loc[inter_row, 'PR(>F)'])
            slope_homogeneity = {
                "f_stat": round(f_val, 3),
                "p_value": round(p_val, 4),
                "homogeneous": bool(p_val > 0.05)
            }

    report = {
        "dv": dv,
        "group_col": group_col,
        "covariate": cov_col,
        "normality_shapiro": normality,
        "levene_test": {
            "f_stat": round(float(stat_l), 3),
            "p_value": round(float(p_l), 4),
            "homogeneous": bool(p_l > 0.05)
        },
        "slope_homogeneity": slope_homogeneity,
        "overall_status": "ASSUMPTIONS_MET" if p_l > 0.05 and slope_homogeneity.get("homogeneous", True) else "ASSUMPTIONS_VIOLATED"
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"Assumption verification report saved to {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Verify parametric assumptions")
    parser.add_argument('--data', required=True, help="Path to dataset")
    parser.add_argument('--dv', required=True, help="Dependent variable")
    parser.add_argument('--group', required=True, help="Group variable")
    parser.add_argument('--covariate', default="", help="Covariate variable")
    parser.add_argument('--output', default="assumptions.json", help="Output JSON path")
    args = parser.parse_args()
    check_assumptions(args.data, args.dv, args.group, args.covariate, args.output)
