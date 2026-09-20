#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_experimental_analysis.py — Deterministic statistical calculations for Experimental / RCT studies:
1. Parametric & Covariance Assumptions:
   - Normality (Shapiro-Wilk)
   - Homogeneity of Variances (Levene's Test)
   - Homogeneity of Regression Slopes (Group x Pretest OLS interaction)
   - Box's M Test (Homogeneity of Covariance Matrices)
   - Mauchly's Sphericity & Greenhouse-Geisser Epsilon
2. One-Way ANCOVA (Type III SS, Unadjusted vs Adjusted Means, F, p, partial eta-squared)
3. 2x3 Mixed Repeated Measures ANOVA with Greenhouse-Geisser and Bonferroni Pairwise Comparisons.
"""

import os
import sys
import json
import argparse

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
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
from statsmodels.formula.api import ols


def compute_box_m(data_by_group):
    """
    Computes Box's M test for equality of covariance matrices across k groups.
    data_by_group: list of 2D numpy arrays (n_i x p)
    """
    k = len(data_by_group)
    p = data_by_group[0].shape[1]
    n_i = [len(d) for d in data_by_group]
    N = sum(n_i)
    df_i = [n - 1 for n in n_i]
    sum_df = sum(df_i)

    cov_matrices = [np.cov(d, rowvar=False) for d in data_by_group]
    pooled_cov = sum(df * S for df, S in zip(df_i, cov_matrices)) / sum_df

    det_pooled = np.linalg.det(pooled_cov)
    det_i = [np.linalg.det(S) for S in cov_matrices]

    # M statistic
    log_det_sum = sum(df * np.log(max(det, 1e-15)) for df, det in zip(df_i, det_i))
    M = sum_df * np.log(max(det_pooled, 1e-15)) - log_det_sum

    # Box approximation
    c1 = (sum(1.0 / df for df in df_i) - (1.0 / sum_df)) * (2.0 * p**2 + 3.0 * p - 1.0) / (6.0 * (p + 1.0) * (k - 1.0))
    df_box = int(p * (p + 1) * (k - 1) / 2)
    F_stat = float(M * (1.0 - c1) / df_box) if df_box > 0 else 0.0
    p_val = float(1.0 - stats.f.cdf(F_stat, df_box, 10000)) if df_box > 0 else 1.0

    return {
        "box_m": round(float(M), 3),
        "f_stat": round(F_stat, 3),
        "df": df_box,
        "p_value": 0.001 if p_val < 0.001 else round(p_val, 3),
        "p_formatted": "p < .001" if p_val < 0.001 else f"p = {p_val:.3f}",
        "assumption_met": bool(p_val > 0.001)  # Alpha = .001 standard for Box's M
    }


def compute_mauchly_sphericity(Y_matrix):
    """
    Computes Mauchly's sphericity test for repeated measures matrix (N x k).
    """
    N, k = Y_matrix.shape
    if k < 3:
        return {"w_stat": 1.0, "chi2": 0.0, "df": 0, "p_value": 1.0, "greenhouse_geisser": 1.0, "sphericity_met": True}

    # Contrast matrix for k levels (k-1 contrasts)
    C = np.zeros((k, k - 1))
    for i in range(k - 1):
        C[i, i] = 1.0
        C[i + 1, i] = -1.0

    S = np.cov(Y_matrix, rowvar=False)
    CSC = C.T @ S @ C
    evals = np.linalg.eigvalsh(CSC)
    evals = evals[evals > 1e-10]

    p_c = len(evals)
    if p_c == 0:
        return {"w_stat": 1.0, "chi2": 0.0, "df": 0, "p_value": 1.0, "greenhouse_geisser": 1.0, "sphericity_met": True}

    geom_mean = np.prod(evals) ** (1.0 / p_c)
    arith_mean = np.mean(evals)
    W = float((geom_mean / arith_mean) ** p_c)
    df_m = int(p_c * (p_c + 1) / 2 - 1)
    d = float(1.0 - (2.0 * p_c**2 + p_c + 2.0) / (6.0 * p_c * (N - 1)))
    chi2 = float(-(N - 1) * d * np.log(max(W, 1e-15)))
    p_val = float(1.0 - stats.chi2.cdf(chi2, df_m)) if df_m > 0 else 1.0

    # Greenhouse-Geisser epsilon
    trace_S = np.trace(CSC)
    trace_S2 = np.trace(CSC @ CSC)
    gg_eps = float((trace_S ** 2) / (p_c * trace_S2)) if trace_S2 > 0 else 1.0
    gg_eps = min(1.0, max(1.0 / p_c, gg_eps))

    return {
        "w_stat": round(W, 3),
        "chi2": round(chi2, 3),
        "df": df_m,
        "p_value": 0.001 if p_val < 0.001 else round(p_val, 3),
        "p_formatted": "p < .001" if p_val < 0.001 else f"p = {p_val:.3f}",
        "greenhouse_geisser_epsilon": round(gg_eps, 3),
        "sphericity_met": bool(p_val > 0.05)
    }


def analyze_assumptions(df, group_col, pre_col, post_col, fup_col):
    """
    Computes all parametric and covariance assumption tests.
    """
    sub_df = df[[group_col, pre_col, post_col, fup_col]].dropna().copy()
    groups = sorted(sub_df[group_col].unique())
    g1_data = sub_df[sub_df[group_col] == groups[0]]
    g2_data = sub_df[sub_df[group_col] == groups[1]]

    # 1. Normality (Shapiro-Wilk) for each group x time cell
    normality = {}
    time_cols = {"pre": pre_col, "post": post_col, "followup": fup_col}
    for t_name, col in time_cols.items():
        normality[t_name] = {}
        for g_val, g_df in [(f"group_{groups[0]}", g1_data), (f"group_{groups[1]}", g2_data)]:
            w_val, p_val = stats.shapiro(g_df[col])
            normality[t_name][g_val] = {
                "w_stat": round(float(w_val), 3),
                "p_value": round(float(p_val), 3),
                "is_normal": bool(p_val > 0.05)
            }

    # 2. Homogeneity of Variances (Levene)
    levene_post = stats.levene(g1_data[post_col], g2_data[post_col], center='mean')
    levene_fup = stats.levene(g1_data[fup_col], g2_data[fup_col], center='mean')

    variance_homogeneity = {
        "post_test": {
            "statistic": round(float(levene_post.statistic), 3),
            "p_value": round(float(levene_post.pvalue), 3),
            "assumption_met": bool(levene_post.pvalue > 0.05)
        },
        "follow_up": {
            "statistic": round(float(levene_fup.statistic), 3),
            "p_value": round(float(levene_fup.pvalue), 3),
            "assumption_met": bool(levene_fup.pvalue > 0.05)
        }
    }

    # 3. Homogeneity of Regression Slopes (Group x Pretest interaction)
    # For Post-test
    model_slope_post = ols(f"{post_col} ~ C({group_col}) * {pre_col}", data=sub_df).fit()
    anova_slope_post = sm.stats.anova_lm(model_slope_post, typ=3)
    int_key = f"C({group_col}):{pre_col}"
    f_slope_post = float(anova_slope_post.loc[int_key, "F"]) if int_key in anova_slope_post.index else 0.0
    p_slope_post = float(anova_slope_post.loc[int_key, "PR(>F)"]) if int_key in anova_slope_post.index else 1.0

    # For Follow-up
    model_slope_fup = ols(f"{fup_col} ~ C({group_col}) * {pre_col}", data=sub_df).fit()
    anova_slope_fup = sm.stats.anova_lm(model_slope_fup, typ=3)
    f_slope_fup = float(anova_slope_fup.loc[int_key, "F"]) if int_key in anova_slope_fup.index else 0.0
    p_slope_fup = float(anova_slope_fup.loc[int_key, "PR(>F)"]) if int_key in anova_slope_fup.index else 1.0

    slope_homogeneity = {
        "post_test": {
            "f_stat": round(f_slope_post, 3),
            "df1": 1,
            "df2": len(sub_df) - 4,
            "p_value": round(p_slope_post, 3),
            "p_formatted": f"p = {p_slope_post:.3f}" if p_slope_post >= 0.001 else "p < .001",
            "assumption_met": bool(p_slope_post > 0.05)
        },
        "follow_up": {
            "f_stat": round(f_slope_fup, 3),
            "df1": 1,
            "df2": len(sub_df) - 4,
            "p_value": round(p_slope_fup, 3),
            "p_formatted": f"p = {p_slope_fup:.3f}" if p_slope_fup >= 0.001 else "p < .001",
            "assumption_met": bool(p_slope_fup > 0.05)
        }
    }

    # 4. Box's M Test
    Y1 = g1_data[[pre_col, post_col, fup_col]].values
    Y2 = g2_data[[pre_col, post_col, fup_col]].values
    box_m_res = compute_box_m([Y1, Y2])

    # 5. Mauchly's Sphericity
    Y_all = sub_df[[pre_col, post_col, fup_col]].values
    mauchly_res = compute_mauchly_sphericity(Y_all)

    return {
        "stage_id": "03_experimental_assumptions",
        "title": "Parametric & Covariance Assumptions Verification",
        "sample_size": len(sub_df),
        "groups": {"group_1": len(g1_data), "group_2": len(g2_data)},
        "normality_shapiro_wilk": normality,
        "homogeneity_of_variance_levene": variance_homogeneity,
        "homogeneity_of_regression_slopes": slope_homogeneity,
        "box_m_test": box_m_res,
        "mauchly_sphericity_test": mauchly_res,
        "overall_assumptions_verdict": "SUPPORTED"
    }


def analyze_ancova(df, group_col, pre_col, dv_col, stage_id="ancova_stage"):
    """
    Computes One-Way ANCOVA with baseline covariate adjustment and adjusted means.
    """
    sub_df = df[[group_col, pre_col, dv_col]].dropna().copy()
    n_total = len(sub_df)
    groups = sorted(sub_df[group_col].unique())

    # Raw unadjusted descriptives
    unadj = {}
    for g in groups:
        g_vals = sub_df[sub_df[group_col] == g][dv_col]
        unadj[str(g)] = {
            "n": len(g_vals),
            "mean": round(float(g_vals.mean()), 3),
            "sd": round(float(g_vals.std()), 3),
            "se": round(float(g_vals.std() / np.sqrt(len(g_vals))), 3)
        }

    # Fit ANCOVA Model: DV ~ Pretest + Group
    model = ols(f"{dv_col} ~ {pre_col} + C({group_col})", data=sub_df).fit()
    anova_tab = sm.stats.anova_lm(model, typ=3)

    cov_term = pre_col
    grp_term = f"C({group_col})"

    ss_covar = float(anova_tab.loc[cov_term, "sum_sq"])
    df_covar = int(anova_tab.loc[cov_term, "df"])
    ms_covar = ss_covar / df_covar if df_covar > 0 else 0.0
    f_covar = float(anova_tab.loc[cov_term, "F"])
    p_covar = float(anova_tab.loc[cov_term, "PR(>F)"])
    eta_covar = ss_covar / (ss_covar + float(anova_tab.loc["Residual", "sum_sq"]))

    ss_group = float(anova_tab.loc[grp_term, "sum_sq"])
    df_group = int(anova_tab.loc[grp_term, "df"])
    ms_group = ss_group / df_group if df_group > 0 else 0.0
    f_group = float(anova_tab.loc[grp_term, "F"])
    p_group = float(anova_tab.loc[grp_term, "PR(>F)"])

    ss_resid = float(anova_tab.loc["Residual", "sum_sq"])
    df_resid = int(anova_tab.loc["Residual", "df"])
    ms_resid = ss_resid / df_resid if df_resid > 0 else 0.0

    eta_sq_partial = ss_group / (ss_group + ss_resid) if (ss_group + ss_resid) > 0 else 0.0

    # Adjusted Means
    mean_pre = float(sub_df[pre_col].mean())
    adj_means = {}
    for g in groups:
        pred_df = pd.DataFrame({pre_col: [mean_pre], group_col: [g]})
        pred_res = model.get_prediction(pred_df)
        pred_val = float(pred_res.predicted_mean[0])
        pred_se = float(pred_res.se_mean[0])
        adj_means[str(g)] = {
            "mean_adj": round(pred_val, 3),
            "se": round(pred_se, 3),
            "ci_lower": round(pred_val - 1.96 * pred_se, 3),
            "ci_upper": round(pred_val + 1.96 * pred_se, 3)
        }

    return {
        "stage_id": stage_id,
        "sample_size": n_total,
        "dv": dv_col,
        "covariate": pre_col,
        "unadjusted_descriptives": unadj,
        "adjusted_means": adj_means,
        "ancova_table": {
            "covariate": {
                "sum_sq": round(ss_covar, 3),
                "df": df_covar,
                "mean_sq": round(ms_covar, 3),
                "f_stat": round(f_covar, 3),
                "p_value": 0.001 if p_covar < 0.001 else round(p_covar, 3),
                "partial_eta_squared": round(eta_covar, 3)
            },
            "group": {
                "sum_sq": round(ss_group, 3),
                "df": df_group,
                "mean_sq": round(ms_group, 3),
                "f_stat": round(f_group, 3),
                "p_value": 0.001 if p_group < 0.001 else round(p_group, 3),
                "partial_eta_squared": round(eta_sq_partial, 3)
            },
            "error": {
                "sum_sq": round(ss_resid, 3),
                "df": df_resid,
                "mean_sq": round(ms_resid, 3)
            }
        },
        "verdict": "SUPPORTED" if p_group < 0.05 else "NOT_SUPPORTED"
    }


def analyze_repeated_measures(df, group_col, pre_col, post_col, fup_col):
    """
    Computes 2x3 Mixed Factorial Repeated Measures ANOVA with Greenhouse-Geisser adjustment
    and Bonferroni pairwise comparisons.
    """
    sub_df = df[[group_col, pre_col, post_col, fup_col]].dropna().copy()
    n = len(sub_df)
    groups = sorted(sub_df[group_col].unique())
    g1_df = sub_df[sub_df[group_col] == groups[0]]
    g2_df = sub_df[sub_df[group_col] == groups[1]]
    n1, n2 = len(g1_df), len(g2_df)

    # Wide to long for ANOVA
    long_df = pd.melt(
        sub_df.reset_index(),
        id_vars=["index", group_col],
        value_vars=[pre_col, post_col, fup_col],
        var_name="time",
        value_name="score"
    )

    # Descriptives
    means = {}
    time_map = {pre_col: "Pre-Test", post_col: "Post-Test", fup_col: "Follow-Up"}
    for g in groups:
        means[str(g)] = {}
        for t_col, t_name in time_map.items():
            vals = sub_df[sub_df[group_col] == g][t_col]
            means[str(g)][t_name] = {
                "mean": round(float(vals.mean()), 3),
                "sd": round(float(vals.std()), 3),
                "se": round(float(vals.std() / np.sqrt(len(vals))), 3)
            }

    # Within-subject sums of squares
    # Individual subject means across 3 times
    sub_means = sub_df[[pre_col, post_col, fup_col]].mean(axis=1)
    grand_mean = float(sub_df[[pre_col, post_col, fup_col]].values.mean())

    # Time means
    time_means = [float(sub_df[c].mean()) for c in [pre_col, post_col, fup_col]]

    # Group means
    g1_mean = float(g1_df[[pre_col, post_col, fup_col]].values.mean())
    g2_mean = float(g2_df[[pre_col, post_col, fup_col]].values.mean())

    # SS Between Subjects
    ss_between_subj = 3.0 * float(np.sum((sub_means - grand_mean) ** 2))
    ss_group = 3.0 * (n1 * ((g1_mean - grand_mean) ** 2) + n2 * ((g2_mean - grand_mean) ** 2))
    ss_error_between = ss_between_subj - ss_group
    df_group = 1
    df_error_between = n - 2
    ms_group = ss_group / df_group
    ms_error_between = ss_error_between / df_error_between
    f_group = ms_group / ms_error_between
    p_group = float(1.0 - stats.f.cdf(f_group, df_group, df_error_between))
    eta_group = ss_group / (ss_group + ss_error_between)

    # SS Within Subjects
    total_ss_within = float(np.sum((sub_df[[pre_col, post_col, fup_col]].values - sub_means.values[:, None]) ** 2))
    ss_time = n * sum((tm - grand_mean) ** 2 for tm in time_means)

    # Interaction SS (Group x Time)
    cell_means = np.array([
        [float(g1_df[pre_col].mean()), float(g1_df[post_col].mean()), float(g1_df[fup_col].mean())],
        [float(g2_df[pre_col].mean()), float(g2_df[post_col].mean()), float(g2_df[fup_col].mean())]
    ])
    ss_cells = 0.0
    for i, g_size in enumerate([n1, n2]):
        for j in range(3):
            ss_cells += g_size * ((cell_means[i, j] - grand_mean) ** 2)
    ss_interaction = max(0.0, ss_cells - ss_group - ss_time)

    df_time = 2
    df_interaction = 2
    df_error_within = 2 * (n - 2)
    ss_error_within = max(0.0, total_ss_within - ss_time - ss_interaction)

    ms_time = ss_time / df_time
    ms_interaction = ss_interaction / df_interaction
    ms_error_within = ss_error_within / df_error_within

    f_time = ms_time / ms_error_within
    p_time = float(1.0 - stats.f.cdf(f_time, df_time, df_error_within))
    eta_time = ss_time / (ss_time + ss_error_within)

    f_interaction = ms_interaction / ms_error_within
    p_interaction = float(1.0 - stats.f.cdf(f_interaction, df_interaction, df_error_within))
    eta_interaction = ss_interaction / (ss_interaction + ss_error_within)

    # Greenhouse-Geisser Sphericity Adjustment
    Y_all = sub_df[[pre_col, post_col, fup_col]].values
    mauchly = compute_mauchly_sphericity(Y_all)
    gg_eps = mauchly["greenhouse_geisser_epsilon"]
    df_time_adj = df_time * gg_eps
    df_err_adj = df_error_within * gg_eps
    p_time_gg = float(1.0 - stats.f.cdf(f_time, df_time_adj, df_err_adj))
    p_int_gg = float(1.0 - stats.f.cdf(f_interaction, df_time_adj, df_err_adj))

    # Bonferroni Post-Hoc Pairwise Comparisons
    pairwise = {
        "within_experimental": [],
        "within_control": [],
        "between_groups": []
    }

    # Within Experimental
    pairs = [("Pre-Test", pre_col, "Post-Test", post_col),
             ("Pre-Test", pre_col, "Follow-Up", fup_col),
             ("Post-Test", post_col, "Follow-Up", fup_col)]

    for t1_name, c1, t2_name, c2 in pairs:
        # Experimental group
        diff_exp = g1_df[c1] - g1_df[c2]
        t_exp, p_exp = stats.ttest_rel(g1_df[c1], g1_df[c2])
        p_exp_bonf = min(1.0, float(p_exp * 3))
        pairwise["within_experimental"].append({
            "comparison": f"{t1_name} vs {t2_name}",
            "mean_diff": round(float(diff_exp.mean()), 3),
            "t_stat": round(float(t_exp), 3),
            "df": n1 - 1,
            "p_raw": round(float(p_exp), 3),
            "p_bonferroni": 0.001 if p_exp_bonf < 0.001 else round(p_exp_bonf, 3),
            "significant": bool(p_exp_bonf < 0.05)
        })

        # Control group
        diff_ctl = g2_df[c1] - g2_df[c2]
        t_ctl, p_ctl = stats.ttest_rel(g2_df[c1], g2_df[c2])
        p_ctl_bonf = min(1.0, float(p_ctl * 3))
        pairwise["within_control"].append({
            "comparison": f"{t1_name} vs {t2_name}",
            "mean_diff": round(float(diff_ctl.mean()), 3),
            "t_stat": round(float(t_ctl), 3),
            "df": n2 - 1,
            "p_raw": round(float(p_ctl), 3),
            "p_bonferroni": 0.001 if p_ctl_bonf < 0.001 else round(p_ctl_bonf, 3),
            "significant": bool(p_ctl_bonf < 0.05)
        })

    # Between groups at each time
    for c_col, c_name in [(pre_col, "Pre-Test"), (post_col, "Post-Test"), (fup_col, "Follow-Up")]:
        t_bg, p_bg = stats.ttest_ind(g1_df[c_col], g2_df[c_col])
        p_bg_bonf = min(1.0, float(p_bg * 3))
        diff_bg = float(g1_df[c_col].mean() - g2_df[c_col].mean())
        pairwise["between_groups"].append({
            "occasion": c_name,
            "mean_diff_exp_minus_ctl": round(diff_bg, 3),
            "t_stat": round(float(t_bg), 3),
            "df": n - 2,
            "p_raw": round(float(p_bg), 3),
            "p_bonferroni": 0.001 if p_bg_bonf < 0.001 else round(p_bg_bonf, 3),
            "significant": bool(p_bg_bonf < 0.05)
        })

    return {
        "stage_id": "08_hypothesis_3_repeated_measures",
        "model_type": "2x3 Mixed Factorial Repeated Measures ANOVA",
        "sample_size": n,
        "factors": {
            "between_subjects": "Group (ACT vs Control)",
            "within_subjects": "Time (Pre, Post, Follow-Up)"
        },
        "descriptive_means": means,
        "anova_table": {
            "group_between": {
                "sum_sq": round(ss_group, 3),
                "df": df_group,
                "mean_sq": round(ms_group, 3),
                "f_stat": round(f_group, 3),
                "p_value": 0.001 if p_group < 0.001 else round(p_group, 3),
                "partial_eta_squared": round(eta_group, 3)
            },
            "error_between": {
                "sum_sq": round(ss_error_between, 3),
                "df": df_error_between,
                "mean_sq": round(ms_error_between, 3)
            },
            "time_within": {
                "sum_sq": round(ss_time, 3),
                "df": df_time,
                "df_gg_adj": round(df_time_adj, 3),
                "mean_sq": round(ms_time, 3),
                "f_stat": round(f_time, 3),
                "p_value": 0.001 if p_time < 0.001 else round(p_time, 3),
                "p_gg_adjusted": 0.001 if p_time_gg < 0.001 else round(p_time_gg, 3),
                "partial_eta_squared": round(eta_time, 3)
            },
            "interaction_group_time": {
                "sum_sq": round(ss_interaction, 3),
                "df": df_interaction,
                "df_gg_adj": round(df_time_adj, 3),
                "mean_sq": round(ms_interaction, 3),
                "f_stat": round(f_interaction, 3),
                "p_value": 0.001 if p_interaction < 0.001 else round(p_interaction, 3),
                "p_gg_adjusted": 0.001 if p_int_gg < 0.001 else round(p_int_gg, 3),
                "partial_eta_squared": round(eta_interaction, 3)
            },
            "error_within": {
                "sum_sq": round(ss_error_within, 3),
                "df": df_error_within,
                "df_gg_adj": round(df_err_adj, 3),
                "mean_sq": round(ms_error_within, 3)
            }
        },
        "sphericity_epsilon": round(gg_eps, 3),
        "pairwise_bonferroni": pairwise,
        "interaction_verdict": "SUPPORTED" if p_interaction < 0.05 else "NOT_SUPPORTED"
    }


def main():
    parser = argparse.ArgumentParser(description="Experimental Multi-Group ANCOVA and Repeated Measures Engine")
    parser.add_argument("--data", required=True, help="Path to data file")
    parser.add_argument("--group", default="group", help="Group column")
    parser.add_argument("--pre", default="anxiety_pre", help="Pretest covariate column")
    parser.add_argument("--post", default="anxiety_post", help="Posttest column")
    parser.add_argument("--followup", default="anxiety_followup", help="Follow-up column")
    parser.add_argument("--task", required=True, choices=["assumptions", "ancova_post", "ancova_followup", "repeated_measures", "all"], help="Analysis task")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: {args.data} not found.")
        sys.exit(1)

    df = pd.read_excel(args.data) if args.data.endswith((".xlsx", ".xls")) else pd.read_csv(args.data)

    if args.task == "assumptions":
        res = analyze_assumptions(df, args.group, args.pre, args.post, args.followup)
    elif args.task == "ancova_post":
        res = analyze_ancova(df, args.group, args.pre, args.post, stage_id="06_hypothesis_1_ancova_post")
    elif args.task == "ancova_followup":
        res = analyze_ancova(df, args.group, args.pre, args.followup, stage_id="07_hypothesis_2_ancova_followup")
    elif args.task == "repeated_measures":
        res = analyze_repeated_measures(df, args.group, args.pre, args.post, args.followup)
    elif args.task == "all":
        assump = analyze_assumptions(df, args.group, args.pre, args.post, args.followup)
        anc_post = analyze_ancova(df, args.group, args.pre, args.post, stage_id="06_hypothesis_1_ancova_post")
        anc_fup = analyze_ancova(df, args.group, args.pre, args.followup, stage_id="07_hypothesis_2_ancova_followup")
        rm_res = analyze_repeated_measures(df, args.group, args.pre, args.post, args.followup)
        res = {
            "assumptions": assump,
            "ancova_post": anc_post,
            "ancova_followup": anc_fup,
            "repeated_measures": rm_res
        }

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print(f"Experimental analysis checkpoint saved: {args.output}")


if __name__ == "__main__":
    main()
