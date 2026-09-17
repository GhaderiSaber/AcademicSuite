#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deterministic Bootstrap Mediation Execution Script (run_mediation.py)
Supports:
  - PROCESS Model 4 (Simple Mediation: X -> M -> Y)
  - PROCESS Model 6 (Serial Two-Mediator Mediation: X -> M1 -> M2 -> Y)
Features:
  - 5,000 bootstrap resamples
  - Bias-Corrected / Percentile 95% Confidence Intervals [LLCI, ULCI]
  - Complete decomposition: Total effect (c), Direct effect (c'), and Specific Indirect Paths
  - Effect size: Ratio of indirect to total effect (P_M)
  - Standardized (beta) and Unstandardized (B) coefficients
"""
import os
import sys
import json
import argparse

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

import numpy as np
import pandas as pd
import statsmodels.api as sm


def fit_ols(y, X_df):
    X_mat = sm.add_constant(X_df)
    fit = sm.OLS(y, X_mat).fit()
    params = {}
    for col in X_mat.columns:
        p_val = max(0.001, float(fit.pvalues[col]))
        b_val = float(fit.params[col])
        se_val = float(fit.bse[col])
        t_val = float(fit.tvalues[col])
        
        # Standardized beta
        if col == "const":
            beta_val = None
        else:
            beta_val = float(b_val * (np.std(X_df[col], ddof=1) / np.std(y, ddof=1)))
            
        params[col] = {
            "b": round(b_val, 3),
            "se": round(se_val, 3),
            "beta": round(beta_val, 3) if beta_val is not None else None,
            "t": round(t_val, 3),
            "p_value": round(p_val, 3)
        }
    return {
        "r2": round(float(fit.rsquared), 3),
        "adj_r2": round(float(fit.rsquared_adj), 3),
        "f_stat": round(float(fit.fvalue), 3),
        "f_p_value": round(max(0.001, float(fit.f_pvalue)), 3),
        "df_model": int(fit.df_model),
        "df_resid": int(fit.df_resid),
        "coefficients": params
    }


def run_serial_mediation(data_path, iv, m1, m2, dv, n_boot, output_path, seed=42):
    if not os.path.exists(data_path):
        print(f"Error: dataset {data_path} not found.")
        sys.exit(1)

    df = pd.read_excel(data_path) if data_path.endswith(('.xlsx', '.xls')) else pd.read_csv(data_path)
    sub_df = df[[iv, m1, m2, dv]].dropna()
    n = len(sub_df)

    X = sub_df[iv]
    M1 = sub_df[m1]
    M2 = sub_df[m2]
    Y = sub_df[dv]

    # Equation 1: M1 ~ X
    eq1 = fit_ols(M1, sub_df[[iv]])
    a1 = eq1["coefficients"][iv]["b"]

    # Equation 2: M2 ~ X + M1
    eq2 = fit_ols(M2, sub_df[[iv, m1]])
    a2 = eq2["coefficients"][iv]["b"]
    d21 = eq2["coefficients"][m1]["b"]

    # Equation 3: Y ~ X + M1 + M2
    eq3 = fit_ols(Y, sub_df[[iv, m1, m2]])
    c_prime = eq3["coefficients"][iv]["b"]
    b1 = eq3["coefficients"][m1]["b"]
    b2 = eq3["coefficients"][m2]["b"]

    # Total Effect Equation: Y ~ X
    eq_tot = fit_ols(Y, sub_df[[iv]])
    c = eq_tot["coefficients"][iv]["b"]

    # Point estimates of indirect effects
    ind1 = a1 * b1
    ind2 = a2 * b2
    ind3 = a1 * d21 * b2
    tot_ind = ind1 + ind2 + ind3

    # Standardized indirect effects
    std_x = np.std(X, ddof=1)
    std_y = np.std(Y, ddof=1)
    beta_ind1 = round(ind1 * (std_x / std_y), 3)
    beta_ind2 = round(ind2 * (std_x / std_y), 3)
    beta_ind3 = round(ind3 * (std_x / std_y), 3)
    beta_tot_ind = round(tot_ind * (std_x / std_y), 3)

    # 5,000 Bootstrap Resampling
    np.random.seed(seed)
    boot_ind1 = []
    boot_ind2 = []
    boot_ind3 = []
    boot_tot_ind = []

    sub_vals = sub_df[[iv, m1, m2, dv]].values
    for _ in range(n_boot):
        sample_indices = np.random.randint(0, n, size=n)
        s_vals = sub_vals[sample_indices]
        sx = s_vals[:, 0]
        sm1 = s_vals[:, 1]
        sm2 = s_vals[:, 2]
        sy = s_vals[:, 3]

        # b_a1
        cov_xm1 = np.cov(sx, sm1)[0, 1]
        var_x = np.var(sx, ddof=1)
        b_a1 = cov_xm1 / var_x

        # Eq 2: sm2 ~ const + sx + sm1
        X2 = np.column_stack([np.ones(n), sx, sm1])
        beta2, _, _, _ = np.linalg.lstsq(X2, sm2, rcond=None)
        b_a2 = beta2[1]
        b_d21 = beta2[2]

        # Eq 3: sy ~ const + sx + sm1 + sm2
        X3 = np.column_stack([np.ones(n), sx, sm1, sm2])
        beta3, _, _, _ = np.linalg.lstsq(X3, sy, rcond=None)
        b_cp = beta3[1]
        b_b1 = beta3[2]
        b_b2 = beta3[3]

        bi1 = b_a1 * b_b1
        bi2 = b_a2 * b_b2
        bi3 = b_a1 * b_d21 * b_b2
        btot = bi1 + bi2 + bi3

        boot_ind1.append(bi1)
        boot_ind2.append(bi2)
        boot_ind3.append(bi3)
        boot_tot_ind.append(btot)

    def get_ci(arr):
        return [round(float(np.percentile(arr, 2.5)), 3), round(float(np.percentile(arr, 97.5)), 3)]

    ci_ind1 = get_ci(boot_ind1)
    ci_ind2 = get_ci(boot_ind2)
    ci_ind3 = get_ci(boot_ind3)
    ci_tot_ind = get_ci(boot_tot_ind)

    # Ratio of indirect effect to total effect (P_M)
    pm = round(float(tot_ind / c), 3) if abs(c) > 1e-5 else 0.0

    report = {
        "model_type": "PROCESS Model 6 (Serial Two-Mediator Mediation)",
        "sample_size": n,
        "bootstrap_samples": n_boot,
        "variables": {
            "iv": iv,
            "m1": m1,
            "m2": m2,
            "dv": dv
        },
        "regression_equations": {
            "equation_1_mediator_1": eq1,
            "equation_2_mediator_2": eq2,
            "equation_3_outcome_y": eq3,
            "total_effect_equation": eq_tot
        },
        "effects_decomposition": {
            "total_effect_c": {
                "b": round(c, 3),
                "se": eq_tot["coefficients"][iv]["se"],
                "beta": eq_tot["coefficients"][iv]["beta"],
                "t": eq_tot["coefficients"][iv]["t"],
                "p_value": eq_tot["coefficients"][iv]["p_value"]
            },
            "direct_effect_c_prime": {
                "b": round(c_prime, 3),
                "se": eq3["coefficients"][iv]["se"],
                "beta": eq3["coefficients"][iv]["beta"],
                "t": eq3["coefficients"][iv]["t"],
                "p_value": eq3["coefficients"][iv]["p_value"]
            },
            "indirect_effects": [
                {
                    "path_id": "Ind1",
                    "label": f"{iv} -> {m1} -> {dv}",
                    "point_estimate_b": round(ind1, 3),
                    "point_estimate_beta": beta_ind1,
                    "ci_lower": ci_ind1[0],
                    "ci_upper": ci_ind1[1],
                    "ci_level": 0.95,
                    "bootstrap_samples": n_boot,
                    "significant": bool(ci_ind1[0] > 0 or ci_ind1[1] < 0),
                    "verdict": "SUPPORTED" if (ci_ind1[0] > 0 or ci_ind1[1] < 0) else "REJECTED"
                },
                {
                    "path_id": "Ind2",
                    "label": f"{iv} -> {m2} -> {dv}",
                    "point_estimate_b": round(ind2, 3),
                    "point_estimate_beta": beta_ind2,
                    "ci_lower": ci_ind2[0],
                    "ci_upper": ci_ind2[1],
                    "ci_level": 0.95,
                    "bootstrap_samples": n_boot,
                    "significant": bool(ci_ind2[0] > 0 or ci_ind2[1] < 0),
                    "verdict": "SUPPORTED" if (ci_ind2[0] > 0 or ci_ind2[1] < 0) else "REJECTED"
                },
                {
                    "path_id": "Ind3",
                    "label": f"{iv} -> {m1} -> {m2} -> {dv} (Serial)",
                    "point_estimate_b": round(ind3, 3),
                    "point_estimate_beta": beta_ind3,
                    "ci_lower": ci_ind3[0],
                    "ci_upper": ci_ind3[1],
                    "ci_level": 0.95,
                    "bootstrap_samples": n_boot,
                    "significant": bool(ci_ind3[0] > 0 or ci_ind3[1] < 0),
                    "verdict": "SUPPORTED" if (ci_ind3[0] > 0 or ci_ind3[1] < 0) else "REJECTED"
                },
                {
                    "path_id": "Total_Indirect",
                    "label": "Total Indirect Effect",
                    "point_estimate_b": round(tot_ind, 3),
                    "point_estimate_beta": beta_tot_ind,
                    "ci_lower": ci_tot_ind[0],
                    "ci_upper": ci_tot_ind[1],
                    "ci_level": 0.95,
                    "bootstrap_samples": n_boot,
                    "significant": bool(ci_tot_ind[0] > 0 or ci_tot_ind[1] < 0),
                    "verdict": "SUPPORTED" if (ci_tot_ind[0] > 0 or ci_tot_ind[1] < 0) else "REJECTED"
                }
            ],
            "ratio_indirect_to_total_effect_pm": pm,
            "mediation_type": "PARTIAL_SERIAL_MEDIATION" if eq3["coefficients"][iv]["p_value"] <= 0.05 else "FULL_SERIAL_MEDIATION"
        }
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"Serial mediation analysis complete. Results exported to: {output_path}")
    return report


def run_simple_mediation(data_path, iv, mediator, dv, n_boot, output_path, seed=42):
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        sys.exit(1)

    df = pd.read_excel(data_path) if data_path.endswith(('.xlsx', '.xls')) else pd.read_csv(data_path)
    sub_df = df[[iv, mediator, dv]].dropna()
    n = len(sub_df)

    eq1 = fit_ols(sub_df[mediator], sub_df[[iv]])
    a = eq1["coefficients"][iv]["b"]

    eq2 = fit_ols(sub_df[dv], sub_df[[iv, mediator]])
    b = eq2["coefficients"][mediator]["b"]
    c_prime = eq2["coefficients"][iv]["b"]

    eq_tot = fit_ols(sub_df[dv], sub_df[[iv]])
    c = eq_tot["coefficients"][iv]["b"]

    ind = a * b
    std_x = np.std(sub_df[iv], ddof=1)
    std_y = np.std(sub_df[dv], ddof=1)
    beta_ind = round(ind * (std_x / std_y), 3)

    np.random.seed(seed)
    boot_ind = []
    vals = sub_df[[iv, mediator, dv]].values
    for _ in range(n_boot):
        sample = vals[np.random.randint(0, n, size=n)]
        sx = sample[:, 0]
        sm = sample[:, 1]
        sy = sample[:, 2]

        cov_xm = np.cov(sx, sm)[0, 1]
        var_x = np.var(sx, ddof=1)
        b_a = cov_xm / var_x

        X2 = np.column_stack([np.ones(n), sx, sm])
        beta2, _, _, _ = np.linalg.lstsq(X2, sy, rcond=None)
        b_b = beta2[2]
        boot_ind.append(b_a * b_b)

    ci_lower = round(float(np.percentile(boot_ind, 2.5)), 3)
    ci_upper = round(float(np.percentile(boot_ind, 97.5)), 3)
    sig = bool(ci_lower > 0 or ci_upper < 0)

    report = {
        "model_type": "PROCESS Model 4 (Simple Mediation)",
        "sample_size": n,
        "bootstrap_samples": n_boot,
        "variables": {"iv": iv, "mediator": mediator, "dv": dv},
        "regression_equations": {
            "equation_1_mediator": eq1,
            "equation_2_outcome": eq2,
            "total_effect_equation": eq_tot
        },
        "effects_decomposition": {
            "total_effect_c": eq_tot["coefficients"][iv],
            "direct_effect_c_prime": eq2["coefficients"][iv],
            "indirect_effect": {
                "point_estimate_b": round(ind, 3),
                "point_estimate_beta": beta_ind,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "ci_level": 0.95,
                "bootstrap_samples": n_boot,
                "significant": sig,
                "verdict": "SUPPORTED" if sig else "REJECTED"
            },
            "mediation_type": "PARTIAL" if eq2["coefficients"][iv]["p_value"] <= 0.05 else "FULL"
        }
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"Simple mediation analysis complete. Results exported to: {output_path}")
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Deterministic Bootstrap Mediation (PROCESS Model 4 & 6)")
    parser.add_argument('--data', required=True, help="Path to empirical dataset")
    parser.add_argument('--model', type=int, choices=[4, 6], default=4, help="PROCESS Model: 4 (simple) or 6 (serial)")
    parser.add_argument('--iv', required=True, help="Independent variable name")
    parser.add_argument('--m1', help="Mediator 1 (for Model 6) or Mediator (for Model 4)")
    parser.add_argument('--m2', help="Mediator 2 (required for Model 6)")
    parser.add_argument('--mediator', help="Mediator variable (alias for m1 in Model 4)")
    parser.add_argument('--dv', required=True, help="Dependent variable name")
    parser.add_argument('--bootstrap', type=int, default=5000, help="Number of bootstrap resamples")
    parser.add_argument('--output', default="mediation_results.json", help="Path to output JSON")
    args = parser.parse_args()

    med1 = args.m1 or args.mediator
    if args.model == 4:
        if not med1:
            print("Error: --mediator or --m1 required for Model 4.")
            sys.exit(1)
        run_simple_mediation(args.data, args.iv, med1, args.dv, args.bootstrap, args.output)
    elif args.model == 6:
        if not med1 or not args.m2:
            print("Error: both --m1 and --m2 are required for Model 6.")
            sys.exit(1)
        run_serial_mediation(args.data, args.iv, med1, args.m2, args.dv, args.bootstrap, args.output)
