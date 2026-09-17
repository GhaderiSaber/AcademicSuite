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
from scipy.stats import pearsonr
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.outliers_influence import variance_inflation_factor


def run_regression(data_path, dv, ivs_str, output_path):
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        sys.exit(1)
        
    df = pd.read_excel(data_path) if data_path.endswith(('.xlsx', '.xls')) else pd.read_csv(data_path)
    ivs = [iv.strip() for iv in ivs_str.split(',') if iv.strip() in df.columns]
    
    all_vars = [dv] + ivs
    sub_df = df[all_vars].dropna()
    n = len(sub_df)
    y = sub_df[dv]
    X = sm.add_constant(sub_df[ivs])
    
    model = sm.OLS(y, X).fit()
    conf_ints = model.conf_int()
    
    # 1. Table 1: Bivariate Correlation Matrix & Descriptives
    t1_descriptives = []
    for var in all_vars:
        s = sub_df[var]
        t1_descriptives.append({
            "variable": var,
            "mean": round(float(s.mean()), 2),
            "sd": round(float(s.std()), 2)
        })

    matrix_rows = []
    for i, var1 in enumerate(all_vars):
        row_vals = []
        for j, var2 in enumerate(all_vars):
            if i == j:
                row_vals.append({"r": 1.0, "p": 1.0, "display": "1"})
            elif j > i:
                row_vals.append({"r": None, "p": None, "display": "-"})
            else:
                r_val, p_val = pearsonr(sub_df[var1], sub_df[var2])
                stars = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
                row_vals.append({
                    "r": round(float(r_val), 3),
                    "p": round(float(p_val), 3),
                    "p_display": "< .001" if p_val < 0.001 else str(round(float(p_val), 3)),
                    "display": f"{round(float(r_val), 2)}{stars}"
                })
        matrix_rows.append({
            "variable": var1,
            "order": i + 1,
            "correlations": row_vals
        })

    table_1 = {
        "title": "Bivariate Correlation Matrix & Descriptives",
        "title_persian": "ماتریس همبستگی پیرسون و شاخص‌های توصیفی متغیرهای پژوهش",
        "variables": all_vars,
        "sample_size": n,
        "descriptives": t1_descriptives,
        "correlation_matrix": matrix_rows
    }

    # 2. Table 2: Model Summary & ANOVA Table
    dw_stat = float(durbin_watson(model.resid))
    r_val = float(np.sqrt(model.rsquared))
    r2_val = float(model.rsquared)
    adj_r2_val = float(model.rsquared_adj)
    se_est = float(np.sqrt(model.mse_resid))
    
    ss_reg = float(model.ess)
    df_reg = int(model.df_model)
    ms_reg = float(model.mse_model)
    
    ss_res = float(model.ssr)
    df_res = int(model.df_resid)
    ms_res = float(model.mse_resid)
    
    ss_tot = ss_reg + ss_res
    df_tot = df_reg + df_res
    
    f_stat = float(model.fvalue)
    f_pval = float(model.f_pvalue)

    table_2 = {
        "title": "Model Summary & ANOVA",
        "title_persian": "خلاصه مدل رگرسیون و تحلیل واریانس (ANOVA)",
        "model_summary": {
            "r": round(r_val, 3),
            "r2": round(r2_val, 3),
            "adj_r2": round(adj_r2_val, 3),
            "se_est": round(se_est, 3),
            "durbin_watson": round(dw_stat, 3)
        },
        "anova": {
            "regression": {
                "source": "رگرسیون",
                "ss": round(ss_reg, 3),
                "df": df_reg,
                "ms": round(ms_reg, 3),
                "f": round(f_stat, 3),
                "p_value": "< .001" if f_pval < 0.001 else str(round(f_pval, 3))
            },
            "residual": {
                "source": "باقی‌مانده",
                "ss": round(ss_res, 3),
                "df": df_res,
                "ms": round(ms_res, 3)
            },
            "total": {
                "source": "کل",
                "ss": round(ss_tot, 3),
                "df": df_tot
            }
        }
    }

    # 3. Table 3: Regression Coefficients & Collinearity Diagnostics
    y_std = (y - y.mean()) / y.std()
    X_std = (sub_df[ivs] - sub_df[ivs].mean()) / sub_df[ivs].std()
    model_std = sm.OLS(y_std, X_std).fit()
    
    # Constant
    b_const = float(model.params["const"])
    se_const = float(model.bse["const"])
    t_const = float(model.tvalues["const"])
    p_const = float(model.pvalues["const"])
    ll_const = float(conf_ints.loc["const", 0])
    ul_const = float(conf_ints.loc["const", 1])

    coef_table = [{
        "predictor": "Constant",
        "predictor_persian": "مقدار ثابت",
        "b": round(b_const, 3),
        "se": round(se_const, 3),
        "beta": None,
        "t": round(t_const, 3),
        "p_value": "< .001" if p_const < 0.001 else str(round(p_const, 3)),
        "ci_lower": round(ll_const, 3),
        "ci_upper": round(ul_const, 3),
        "tolerance": None,
        "vif": None
    }]

    for idx, iv in enumerate(ivs, 1):
        b = float(model.params[iv])
        se = float(model.bse[iv])
        beta = float(model_std.params[iv])
        t_val = float(model.tvalues[iv])
        p_val = float(model.pvalues[iv])
        ll = float(conf_ints.loc[iv, 0])
        ul = float(conf_ints.loc[iv, 1])
        
        # Collinearity
        vif_val = float(variance_inflation_factor(X.values, idx))
        tol_val = float(1.0 / vif_val) if vif_val > 0 else 1.0

        coef_table.append({
            "predictor": iv,
            "predictor_persian": iv,
            "b": round(b, 3),
            "se": round(se, 3),
            "beta": round(beta, 3),
            "t": round(t_val, 3),
            "p_value": "< .001" if p_val < 0.001 else str(round(p_val, 3)),
            "ci_lower": round(ll, 3),
            "ci_upper": round(ul, 3),
            "tolerance": round(tol_val, 3),
            "vif": round(vif_val, 3)
        })

    table_3 = {
        "title": "Regression Coefficients & Collinearity Diagnostics",
        "title_persian": "ضرایب رگرسیون چندگانه و شاخص‌های هم‌خطی",
        "coefficients": coef_table
    }

    report = {
        "dv": dv,
        "ivs": ivs,
        "n": n,
        "three_table_standard": True,
        "table_1_correlations": table_1,
        "table_2_model_summary_anova": table_2,
        "table_3_coefficients": table_3,
        "r2": round(r2_val, 3),
        "adj_r2": round(adj_r2_val, 3),
        "f_stat": round(f_stat, 3),
        "f_pvalue": "< .001" if f_pval < 0.001 else str(round(f_pval, 3)),
        "coefficients": coef_table[1:]  # Exclude constant for backward compatibility
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"Regression model results (3-Table Standard) saved to {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Multiple regression analysis")
    parser.add_argument('--data', required=True, help="Path to dataset")
    parser.add_argument('--dv', required=True, help="Dependent variable")
    parser.add_argument('--ivs', required=True, help="Comma-separated independent variables")
    parser.add_argument('--output', default="regression_results.json", help="Output JSON path")
    args = parser.parse_args()
    run_regression(args.data, args.dv, args.ivs, args.output)
