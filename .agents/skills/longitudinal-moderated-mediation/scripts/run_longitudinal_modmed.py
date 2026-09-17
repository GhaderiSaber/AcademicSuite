#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deterministic Longitudinal Moderated Mediation CLI Engine (Model 7 Longitudinal)
Wave 1: X (Predictor), W (Moderator)
Wave 2: M (Mediator), M1 control
Wave 3: Y (Outcome), Y1 control
"""

import os, sys, json, argparse

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

def run_analysis(data_path: str, output_path: str):
    df = pd.read_excel(data_path) if data_path.endswith('.xlsx') else pd.read_csv(data_path)
    n = len(df)

    # Required columns: x_t1, w_t1, m_t2, m_t1, y_t3, y_t1
    x = df['x_t1']
    w = df['w_t1']
    xw = x * w
    m2 = df['m_t2']
    m1 = df['m_t1']
    y3 = df['y_t3']
    y1 = df['y_t1']

    # 1. Mediator model: M2 ~ X1 + W1 + X1*W1 + M1
    X_med = pd.DataFrame({'const': 1, 'x_t1': x, 'w_t1': w, 'xw': xw, 'm_t1': m1})
    mod_med = sm.OLS(m2, X_med).fit()

    # 2. Outcome model: Y3 ~ M2 + X1 + Y1
    X_out = pd.DataFrame({'const': 1, 'm_t2': m2, 'x_t1': x, 'y_t1': y1})
    mod_out = sm.OLS(y3, X_out).fit()

    a1 = mod_med.params['x_t1']
    a3 = mod_med.params['xw']
    b1 = mod_out.params['m_t2']

    # Index of moderated mediation
    index_modmed = float(a3 * b1)

    # Bootstrap 5,000 for Index CI
    np.random.seed(42)
    boot_indices = []
    for _ in range(5000):
        idx = np.random.choice(n, size=n, replace=True)
        boot_df = df.iloc[idx]
        b_x = boot_df['x_t1']
        b_w = boot_df['w_t1']
        b_xw = b_x * b_w
        b_m2 = boot_df['m_t2']
        b_m1 = boot_df['m_t1']
        b_y3 = boot_df['y_t3']
        b_y1 = boot_df['y_t1']

        b_Xm = pd.DataFrame({'const': 1, 'x_t1': b_x, 'w_t1': b_w, 'xw': b_xw, 'm_t1': b_m1})
        m_fit = sm.OLS(b_m2, b_Xm).fit()
        b_Xy = pd.DataFrame({'const': 1, 'm_t2': b_m2, 'x_t1': b_x, 'y_t1': b_y1})
        y_fit = sm.OLS(b_y3, b_Xy).fit()
        boot_indices.append(m_fit.params['xw'] * y_fit.params['m_t2'])

    boot_indices = np.array(boot_indices)
    ci_lower = float(np.percentile(boot_indices, 2.5))
    ci_upper = float(np.percentile(boot_indices, 97.5))

    results = {
        "model_type": "Longitudinal Moderated Mediation (Wave 1 -> Wave 2 -> Wave 3)",
        "sample_size": n,
        "mediator_model": {
            "r_squared": round(float(mod_med.rsquared), 4),
            "f_stat": round(float(mod_med.fvalue), 3),
            "p_value": round(float(mod_med.f_pvalue), 4),
            "interaction_coeff_a3": round(float(a3), 4),
            "interaction_p_value": round(float(mod_med.pvalues['xw']), 4)
        },
        "outcome_model": {
            "r_squared": round(float(mod_out.rsquared), 4),
            "f_stat": round(float(mod_out.fvalue), 3),
            "p_value": round(float(mod_out.f_pvalue), 4),
            "b1_coeff": round(float(b1), 4),
            "b1_p_value": round(float(mod_out.pvalues['m_t2']), 4)
        },
        "moderated_mediation_index": {
            "index": round(index_modmed, 4),
            "bootstrap_samples": 5000,
            "ci_95_lower": round(ci_lower, 4),
            "ci_95_upper": round(ci_upper, 4),
            "significant": bool(ci_lower > 0 or ci_upper < 0)
        },
        "verdict": "SUPPORTED" if (ci_lower > 0 or ci_upper < 0) else "NOT_SUPPORTED"
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"Longitudinal Mod-Med results saved to {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    run_analysis(args.data, args.output)
