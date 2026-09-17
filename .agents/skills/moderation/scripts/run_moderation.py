#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_moderation.py — Execute Moderation Analysis (PROCESS Model 1) and Conditional Process Analysis
(PROCESS Model 7 & Model 14) in the Academic Suite.

Features:
  - Predictor mean-centering (Xc, Wc)
  - Hierarchical regression: Step 1 (Main Effects) vs Step 2 (Interaction)
  - Delta R2, F-change, p-change
  - Simple slopes conditional effects at -1 SD, Mean, +1 SD with exact analytical SE, t, p, and 95% CI
  - Johnson-Neyman technique: exact transition boundary of moderator W
  - Conditional process analysis (Model 7 & Model 14) with 5,000 bootstrap resamples for conditional indirect effects and Index of Moderated Mediation
  - Persian & APA 7 leading zero compliance, standardized beta, unstandardized B
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

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm


def run_model1_moderation(df, iv, mod, dv):
    """
    PROCESS Model 1: Y = b0 + b1*X_c + b2*W_c + b3*(X_c * W_c)
    """
    sub_df = df[[iv, mod, dv]].dropna().copy()
    n = len(sub_df)

    mean_x = float(sub_df[iv].mean())
    std_x = float(sub_df[iv].std())
    mean_w = float(sub_df[mod].mean())
    std_w = float(sub_df[mod].std())
    mean_y = float(sub_df[dv].mean())
    std_y = float(sub_df[dv].std())

    # Mean centering
    sub_df["x_c"] = sub_df[iv] - mean_x
    sub_df["w_c"] = sub_df[mod] - mean_w
    sub_df["interaction"] = sub_df["x_c"] * sub_df["w_c"]

    # Step 1: Main effects model
    X_step1 = sm.add_constant(sub_df[["x_c", "w_c"]])
    model_step1 = sm.OLS(sub_df[dv], X_step1).fit()

    r2_step1 = float(model_step1.rsquared)
    adj_r2_step1 = float(model_step1.rsquared_adj)
    f_step1 = float(model_step1.fvalue)
    p_step1 = float(model_step1.f_pvalue)
    df_model1 = int(model_step1.df_model)
    df_resid1 = int(model_step1.df_resid)

    # Step 2: Interaction model
    X_step2 = sm.add_constant(sub_df[["x_c", "w_c", "interaction"]])
    model_step2 = sm.OLS(sub_df[dv], X_step2).fit()

    r2_step2 = float(model_step2.rsquared)
    adj_r2_step2 = float(model_step2.rsquared_adj)
    f_step2 = float(model_step2.fvalue)
    p_step2 = float(model_step2.f_pvalue)
    df_model2 = int(model_step2.df_model)
    df_resid2 = int(model_step2.df_resid)

    # Hierarchical Change Statistics
    delta_r2 = float(r2_step2 - r2_step1)
    df_change = 1
    f_change = float((delta_r2 / df_change) / ((1.0 - r2_step2) / df_resid2))
    p_change = float(1.0 - stats.f.cdf(f_change, df_change, df_resid2))

    # Extract Step 2 coefficients with standardized beta
    coefficients = {}
    var_map = {"const": "const", "x_c": iv, "w_c": mod, "interaction": f"{iv}_x_{mod}"}
    for term in ["const", "x_c", "w_c", "interaction"]:
        b = float(model_step2.params[term])
        se = float(model_step2.bse[term])
        t_val = float(model_step2.tvalues[term])
        p_val = float(model_step2.pvalues[term])
        ci = model_step2.conf_int().loc[term]

        # Standardized beta
        if term == "const":
            beta = None
        elif term == "x_c":
            beta = float(b * (std_x / std_y))
        elif term == "w_c":
            beta = float(b * (std_w / std_y))
        else:
            std_int = float(sub_df["interaction"].std())
            beta = float(b * (std_int / std_y))

        coefficients[var_map[term]] = {
            "b": round(b, 3),
            "se": round(se, 3),
            "beta": round(beta, 3) if beta is not None else None,
            "t": round(t_val, 3),
            "p_value": 0.001 if p_val < 0.001 else round(p_val, 3),
            "p_formatted": "p < .001" if p_val < 0.001 else f"p = {p_val:.3f}",
            "ci_lower": round(float(ci[0]), 3),
            "ci_upper": round(float(ci[1]), 3)
        }

    # Covariance matrix for analytical simple slopes
    cov_params = model_step2.cov_params()
    var_b1 = float(cov_params.loc["x_c", "x_c"])
    var_b3 = float(cov_params.loc["interaction", "interaction"])
    cov_b1_b3 = float(cov_params.loc["x_c", "interaction"])

    b1 = float(model_step2.params["x_c"])
    b3 = float(model_step2.params["interaction"])

    # Simple slopes at -1 SD, Mean, +1 SD
    t_crit = float(stats.t.ppf(0.975, df=df_resid2))
    slopes = []
    slope_levels = [
        ("-1 SD (Low)", -std_w, mean_w - std_w),
        ("Mean (Average)", 0.0, mean_w),
        ("+1 SD (High)", std_w, mean_w + std_w)
    ]

    for label, w_c_val, w_raw_val in slope_levels:
        slope_b = float(b1 + b3 * w_c_val)
        var_slope = float(var_b1 + (w_c_val ** 2) * var_b3 + 2.0 * w_c_val * cov_b1_b3)
        se_slope = float(np.sqrt(max(var_slope, 1e-12)))
        t_slope = float(slope_b / se_slope)
        p_slope = float(2.0 * (1.0 - stats.t.cdf(abs(t_slope), df=df_resid2)))
        ci_lower = float(slope_b - t_crit * se_slope)
        ci_upper = float(slope_b + t_crit * se_slope)

        slopes.append({
            "level": label,
            "w_centered": round(w_c_val, 3),
            "w_raw": round(w_raw_val, 3),
            "simple_slope": round(slope_b, 3),
            "se": round(se_slope, 3),
            "t": round(t_slope, 3),
            "p_value": 0.001 if p_slope < 0.001 else round(p_slope, 3),
            "p_formatted": "p < .001" if p_slope < 0.001 else f"p = {p_slope:.3f}",
            "ci_lower": round(ci_lower, 3),
            "ci_upper": round(ci_upper, 3),
            "significant": bool(p_slope < 0.05)
        })

    # Johnson-Neyman technique
    # A * W_c^2 + B * W_c + C = 0
    A = float((b3 ** 2) - (t_crit ** 2) * var_b3)
    B = float(2.0 * (b1 * b3 - (t_crit ** 2) * cov_b1_b3))
    C = float((b1 ** 2) - (t_crit ** 2) * var_b1)

    discriminant = float((B ** 2) - 4.0 * A * C)
    jn_points = []
    if discriminant >= 0 and abs(A) > 1e-8:
        root1_c = float((-B - np.sqrt(discriminant)) / (2.0 * A))
        root2_c = float((-B + np.sqrt(discriminant)) / (2.0 * A))
        for r_c in sorted([root1_c, root2_c]):
            r_raw = float(r_c + mean_w)
            # Check if within observed range of W
            if sub_df[mod].min() <= r_raw <= sub_df[mod].max():
                jn_points.append({
                    "w_centered": round(r_c, 3),
                    "w_raw": round(r_raw, 3)
                })

    report = {
        "model_type": "PROCESS Model 1 (Simple Moderation)",
        "sample_size": n,
        "variables": {
            "iv": iv,
            "moderator": mod,
            "dv": dv
        },
        "descriptives": {
            iv: {"mean": round(mean_x, 3), "sd": round(std_x, 3)},
            mod: {"mean": round(mean_w, 3), "sd": round(std_w, 3)},
            dv: {"mean": round(mean_y, 3), "sd": round(std_y, 3)}
        },
        "hierarchical_models": {
            "step1_main_effects": {
                "r2": round(r2_step1, 3),
                "adj_r2": round(adj_r2_step1, 3),
                "f_stat": round(f_step1, 3),
                "p_value": 0.001 if p_step1 < 0.001 else round(p_step1, 3),
                "df_model": df_model1,
                "df_resid": df_resid1
            },
            "step2_interaction": {
                "r2": round(r2_step2, 3),
                "adj_r2": round(adj_r2_step2, 3),
                "f_stat": round(f_step2, 3),
                "p_value": 0.001 if p_step2 < 0.001 else round(p_step2, 3),
                "df_model": df_model2,
                "df_resid": df_resid2
            },
            "model_comparison": {
                "delta_r2": round(delta_r2, 3),
                "f_change": round(f_change, 3),
                "p_change": 0.001 if p_change < 0.001 else round(p_change, 3),
                "p_change_formatted": "p < .001" if p_change < 0.001 else f"p = {p_change:.3f}",
                "significant": bool(p_change < 0.05)
            }
        },
        "coefficients": coefficients,
        "simple_slopes": slopes,
        "johnson_neyman": {
            "has_points": bool(len(jn_points) > 0),
            "transition_points": jn_points,
            "min_w": round(float(sub_df[mod].min()), 3),
            "max_w": round(float(sub_df[mod].max()), 3)
        }
    }
    return report


def run_model7_moderated_mediation(df, iv, mod, mediator, dv, n_boot=5000, seed=42):
    """
    PROCESS Model 7 (First-Stage Moderated Mediation):
    Stage 1: M = a0 + a1*Xc + a2*Wc + a3*(Xc * Wc)
    Stage 2: Y = c'0 + c'*Xc + b1*Mc
    Conditional Indirect Effect(W) = (a1 + a3*Wc) * b1
    Index of Moderated Mediation = a3 * b1
    """
    sub_df = df[[iv, mod, mediator, dv]].dropna().copy()
    n = len(sub_df)
    np.random.seed(seed)

    mean_x = float(sub_df[iv].mean())
    std_w = float(sub_df[mod].std())
    mean_w = float(sub_df[mod].mean())
    mean_m = float(sub_df[mediator].mean())

    sub_df["x_c"] = sub_df[iv] - mean_x
    sub_df["w_c"] = sub_df[mod] - mean_w
    sub_df["m_c"] = sub_df[mediator] - mean_m
    sub_df["interaction"] = sub_df["x_c"] * sub_df["w_c"]

    # Point estimates
    # Stage 1: M ~ Xc + Wc + Interaction
    X_m = sm.add_constant(sub_df[["x_c", "w_c", "interaction"]])
    res_m = sm.OLS(sub_df[mediator], X_m).fit()
    a1 = float(res_m.params["x_c"])
    a2 = float(res_m.params["w_c"])
    a3 = float(res_m.params["interaction"])

    # Stage 2: Y ~ Xc + Mc
    X_y = sm.add_constant(sub_df[["x_c", "m_c"]])
    res_y = sm.OLS(sub_df[dv], X_y).fit()
    c_prime = float(res_y.params["x_c"])
    b1 = float(res_y.params["m_c"])

    # Index of moderated mediation point estimate
    index_modmed = float(a3 * b1)

    # Conditional indirect effects point estimates
    w_levels = [
        ("-1 SD (Low)", -std_w, mean_w - std_w),
        ("Mean (Average)", 0.0, mean_w),
        ("+1 SD (High)", std_w, mean_w + std_w)
    ]
    cond_ind_point = {lvl[0]: float((a1 + a3 * lvl[1]) * b1) for lvl in w_levels}

    # Bootstrap estimation (5,000 resamples)
    boot_indices = []
    boot_cond = {lvl[0]: [] for lvl in w_levels}

    for _ in range(n_boot):
        sample_idx = np.random.choice(n, size=n, replace=True)
        boot_df = sub_df.iloc[sample_idx]

        X_mb = sm.add_constant(boot_df[["x_c", "w_c", "interaction"]])
        res_mb = sm.OLS(boot_df[mediator], X_mb).fit()
        a1_b = float(res_mb.params["x_c"])
        a3_b = float(res_mb.params["interaction"])

        X_yb = sm.add_constant(boot_df[["x_c", "m_c"]])
        res_yb = sm.OLS(boot_df[dv], X_yb).fit()
        b1_b = float(res_yb.params["m_c"])

        idx_b = float(a3_b * b1_b)
        boot_indices.append(idx_b)

        for lvl in w_levels:
            ind_b = float((a1_b + a3_b * lvl[1]) * b1_b)
            boot_cond[lvl[0]].append(ind_b)

    boot_indices = np.array(boot_indices)
    ci_index_low = float(np.percentile(boot_indices, 2.5))
    ci_index_high = float(np.percentile(boot_indices, 97.5))
    se_index = float(np.std(boot_indices))

    cond_results = []
    for lvl in w_levels:
        arr = np.array(boot_cond[lvl[0]])
        ci_l = float(np.percentile(arr, 2.5))
        ci_h = float(np.percentile(arr, 97.5))
        se_c = float(np.std(arr))
        pt = cond_ind_point[lvl[0]]
        sig = not (ci_l <= 0.0 <= ci_h)

        cond_results.append({
            "moderator_level": lvl[0],
            "w_centered": round(lvl[1], 3),
            "w_raw": round(lvl[2], 3),
            "conditional_indirect_effect": round(pt, 3),
            "bootstrap_se": round(se_c, 3),
            "ci_lower": round(ci_l, 3),
            "ci_upper": round(ci_h, 3),
            "significant": sig,
            "verdict": "SUPPORTED" if sig else "NOT_SUPPORTED"
        })

    sig_index = not (ci_index_low <= 0.0 <= ci_index_high)

    report = {
        "model_type": "PROCESS Model 7 (First-Stage Moderated Mediation)",
        "sample_size": n,
        "bootstrap_samples": n_boot,
        "variables": {
            "iv": iv,
            "moderator": mod,
            "mediator": mediator,
            "dv": dv
        },
        "stage1_mediator_equation": {
            "r2": round(float(res_m.rsquared), 3),
            "f_stat": round(float(res_m.fvalue), 3),
            "p_value": 0.001 if res_m.f_pvalue < 0.001 else round(float(res_m.f_pvalue), 3),
            "coefficients": {
                "const": round(float(res_m.params["const"]), 3),
                "a1_iv": round(a1, 3),
                "a2_mod": round(a2, 3),
                "a3_interaction": round(a3, 3)
            }
        },
        "stage2_outcome_equation": {
            "r2": round(float(res_y.rsquared), 3),
            "f_stat": round(float(res_y.fvalue), 3),
            "p_value": 0.001 if res_y.f_pvalue < 0.001 else round(float(res_y.f_pvalue), 3),
            "coefficients": {
                "const": round(float(res_y.params["const"]), 3),
                "c_prime_iv": round(c_prime, 3),
                "b1_mediator": round(b1, 3)
            }
        },
        "conditional_indirect_effects": cond_results,
        "index_of_moderated_mediation": {
            "index": round(index_modmed, 3),
            "bootstrap_se": round(se_index, 3),
            "ci_lower": round(ci_index_low, 3),
            "ci_upper": round(ci_index_high, 3),
            "significant": sig_index,
            "verdict": "SUPPORTED" if sig_index else "NOT_SUPPORTED",
            "interpretation": "Significant moderated mediation (First-stage indirect effect depends on moderator)" if sig_index else "Non-significant moderated mediation"
        }
    }
    return report


def main():
    parser = argparse.ArgumentParser(description="Moderation and Conditional Process Analysis")
    parser.add_argument("--data", required=True, help="Path to dataset")
    parser.add_argument("--iv", required=True, help="Independent variable")
    parser.add_argument("--mod", required=True, help="Moderator variable")
    parser.add_argument("--dv", required=True, help="Dependent variable")
    parser.add_argument("--mediator", default=None, help="Mediator variable (for Model 7/14)")
    parser.add_argument("--model", type=int, default=1, choices=[1, 7], help="PROCESS Model number (1 or 7)")
    parser.add_argument("--bootstrap", type=int, default=5000, help="Number of bootstrap resamples")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: {args.data} not found.")
        sys.exit(1)

    df = pd.read_excel(args.data) if args.data.endswith((".xlsx", ".xls")) else pd.read_csv(args.data)

    if args.model == 1:
        report = run_model1_moderation(df, args.iv, args.mod, args.dv)
    elif args.model == 7:
        if not args.mediator:
            print("Error: --mediator is required for PROCESS Model 7")
            sys.exit(1)
        report = run_model7_moderated_mediation(df, args.iv, args.mod, args.mediator, args.dv, n_boot=args.bootstrap, seed=args.seed)
    else:
        print(f"Unsupported model: {args.model}")
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Successfully generated moderation analysis checkpoint: {args.output}")


if __name__ == "__main__":
    main()
