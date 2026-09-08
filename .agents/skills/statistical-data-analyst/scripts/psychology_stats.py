#!/usr/bin/env python3
"""
Psychology Statistical Analysis Engine (psychology_stats.py)
-------------------------------------------------------------
A deterministic statistical calculation CLI for psychological and behavioral data.
Supports Excel (.xlsx), CSV (.csv), and SPSS (.sav) data formats.

Capabilities:
1. Descriptives & Normality (Mean, SD, Skewness, Kurtosis, Shapiro-Wilk)
2. Scale Reliability (Cronbach's Alpha, Item-Total Correlations, Alpha-if-deleted)
3. Correlation Analysis (Pearson & Spearman matrices with p-values)
4. Group Comparisons (Independent & Paired t-test, Cohen's d, Levene's, Mann-Whitney U)
5. One-Way ANCOVA (Baseline covariate adjustment, slope homogeneity, partial eta-squared)
6. Multiple & Hierarchical Regression (R², Delta R², beta, t, p, Collinearity VIF)
7. Bootstrap Mediation (Path a, b, c, c', indirect effect with 95% bootstrap CI)
"""

import sys
import os
import json
import argparse
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.outliers_influence import variance_inflation_factor

def load_dataset(file_path: str) -> pd.DataFrame:
    """Load dataset from .xlsx, .csv, or .sav."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at {file_path}")
    
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.csv':
        return pd.read_csv(file_path)
    elif ext in ['.xlsx', '.xls']:
        return pd.read_excel(file_path)
    elif ext == '.sav':
        try:
            import pyreadstat
            df, meta = pyreadstat.read_sav(file_path)
            return df
        except ImportError:
            raise ImportError(
                "SPSS (.sav) file detected, but 'pyreadstat' is not installed. "
                "Please run 'pip install pyreadstat' or export your dataset to Excel (.xlsx) / CSV."
            )
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Use .xlsx, .csv, or .sav")

def format_p_value(p: float) -> str:
    """APA 7 rule for p-values: omit leading zero, 3 decimal places, or < .001."""
    if p < 0.001:
        return "< .001"
    formatted = f"{p:.3f}"
    return formatted[1:] if formatted.startswith('0') else formatted

# --- 1. Descriptives & Normality ---
def analyze_descriptives_and_normality(df: pd.DataFrame, variables: list) -> dict:
    results = {}
    for var in variables:
        if var not in df.columns:
            continue
        series = pd.to_numeric(df[var], errors='coerce').dropna()
        n = len(series)
        if n < 3:
            continue
        mean_val = float(series.mean())
        sd_val = float(series.std(ddof=1))
        median_val = float(series.median())
        min_val = float(series.min())
        max_val = float(series.max())
        skew_val = float(stats.skew(series, bias=False))
        kurt_val = float(stats.kurtosis(series, bias=False))
        
        # Shapiro-Wilk Test (sample size <= 5000)
        if n <= 5000:
            sw_stat, sw_p = stats.shapiro(series)
        else:
            # Fallback to Kolmogorov-Smirnov for very large samples
            sw_stat, sw_p = stats.kstest(series, 'norm', args=(mean_val, sd_val))
        
        is_normal = (abs(skew_val) <= 2.0) and (abs(kurt_val) <= 2.0) and (sw_p > 0.05)
        
        results[var] = {
            "N": n,
            "mean": round(mean_val, 2),
            "sd": round(sd_val, 2),
            "median": round(median_val, 2),
            "min": round(min_val, 2),
            "max": round(max_val, 2),
            "skewness": round(skew_val, 2),
            "kurtosis": round(kurt_val, 2),
            "shapiro_w": round(float(sw_stat), 3),
            "shapiro_p": float(sw_p),
            "shapiro_p_str": format_p_value(float(sw_p)),
            "is_normal": bool(is_normal)
        }
    return results

# --- 2. Scale Reliability (Cronbach's Alpha) ---
def analyze_scale_reliability(df: pd.DataFrame, item_cols: list) -> dict:
    sub_df = df[item_cols].apply(pd.to_numeric, errors='coerce').dropna()
    k = len(item_cols)
    n = len(sub_df)
    if k < 2 or n < 3:
        return {"error": "Insufficient items or observations for reliability analysis."}
    
    item_vars = sub_df.var(axis=0, ddof=1)
    total_scores = sub_df.sum(axis=1)
    total_var = total_scores.var(ddof=1)
    
    # Overall Cronbach's Alpha
    if total_var == 0:
        overall_alpha = 0.0
    else:
        overall_alpha = (k / (k - 1)) * (1 - (item_vars.sum() / total_var))
    
    # Item-Deleted Alpha & Item-Total Correlation
    item_diagnostics = []
    for col in item_cols:
        remaining_cols = [c for c in item_cols if c != col]
        rem_df = sub_df[remaining_cols]
        rem_sum = rem_df.sum(axis=1)
        rem_k = len(remaining_cols)
        rem_item_vars = rem_df.var(axis=0, ddof=1).sum()
        rem_total_var = rem_sum.var(ddof=1)
        
        alpha_if_del = (rem_k / (rem_k - 1)) * (1 - (rem_item_vars / rem_total_var)) if rem_total_var > 0 else 0.0
        corr_with_total = stats.pearsonr(sub_df[col], rem_sum)[0]
        
        item_diagnostics.append({
            "item": col,
            "mean": round(float(sub_df[col].mean()), 2),
            "sd": round(float(sub_df[col].std(ddof=1)), 2),
            "item_total_corr": round(float(corr_with_total), 3),
            "alpha_if_deleted": round(float(alpha_if_del), 3)
        })
    
    return {
        "n_items": k,
        "n_cases": n,
        "cronbach_alpha": round(float(overall_alpha), 3),
        "cronbach_alpha_str": f"{overall_alpha:.3f}"[1:] if 0 <= overall_alpha <= 1 else f"{overall_alpha:.3f}",
        "item_diagnostics": item_diagnostics
    }

# --- 3. Correlation Matrix ---
def analyze_correlation_matrix(df: pd.DataFrame, variables: list, method: str = 'pearson') -> dict:
    sub_df = df[variables].apply(pd.to_numeric, errors='coerce').dropna()
    corr_matrix = {}
    p_matrix = {}
    
    for v1 in variables:
        corr_matrix[v1] = {}
        p_matrix[v1] = {}
        for v2 in variables:
            if v1 == v2:
                corr_matrix[v1][v2] = 1.0
                p_matrix[v1][v2] = 1.0
            else:
                if method == 'spearman':
                    r_val, p_val = stats.spearmanr(sub_df[v1], sub_df[v2])
                else:
                    r_val, p_val = stats.pearsonr(sub_df[v1], sub_df[v2])
                corr_matrix[v1][v2] = round(float(r_val), 3)
                p_matrix[v1][v2] = float(p_val)
                
    return {
        "method": method,
        "variables": variables,
        "n_cases": len(sub_df),
        "correlations": corr_matrix,
        "p_values": p_matrix
    }

# --- 4. Group Comparisons (t-test / Mann-Whitney) ---
def analyze_group_comparison(df: pd.DataFrame, var_col: str, group_col: str, paired: bool = False, var2_col: str = None) -> dict:
    if paired:
        # Paired t-test
        s1 = pd.to_numeric(df[var_col], errors='coerce')
        s2 = pd.to_numeric(df[var2_col], errors='coerce')
        valid = pd.concat([s1, s2], axis=1).dropna()
        x1 = valid.iloc[:, 0]
        x2 = valid.iloc[:, 1]
        diff = x1 - x2
        t_stat, p_val = stats.ttest_rel(x1, x2)
        sw_stat, sw_p = stats.shapiro(diff)
        w_stat, w_p = stats.wilcoxon(x1, x2)
        
        diff_sd = diff.std(ddof=1)
        cohen_d = float(diff.mean() / diff_sd) if diff_sd > 0 else 0.0
        
        return {
            "design": "paired",
            "var1": var_col,
            "var2": var2_col,
            "mean1": round(float(x1.mean()), 2),
            "sd1": round(float(x1.std(ddof=1)), 2),
            "mean2": round(float(x2.mean()), 2),
            "sd2": round(float(x2.std(ddof=1)), 2),
            "t": round(float(t_stat), 2),
            "df": len(valid) - 1,
            "p": float(p_val),
            "p_str": format_p_value(float(p_val)),
            "cohen_d": round(cohen_d, 2),
            "normality_diff_p": float(sw_p),
            "wilcoxon_stat": round(float(w_stat), 2),
            "wilcoxon_p": float(w_p),
            "wilcoxon_p_str": format_p_value(float(w_p))
        }
    else:
        # Independent samples comparison
        clean = df[[var_col, group_col]].dropna()
        groups = clean[group_col].unique()
        if len(groups) != 2:
            return {"error": f"Group variable must have exactly 2 groups. Found: {list(groups)}"}
        
        g1_data = pd.to_numeric(clean[clean[group_col] == groups[0]][var_col], errors='coerce').dropna()
        g2_data = pd.to_numeric(clean[clean[group_col] == groups[1]][var_col], errors='coerce').dropna()
        
        n1, n2 = len(g1_data), len(g2_data)
        m1, m2 = float(g1_data.mean()), float(g2_data.mean())
        sd1, sd2 = float(g1_data.std(ddof=1)), float(g2_data.std(ddof=1))
        
        # Levene's Test
        levene_stat, levene_p = stats.levene(g1_data, g2_data)
        equal_var = (levene_p > 0.05)
        
        # t-test
        t_stat, p_val = stats.ttest_ind(g1_data, g2_data, equal_var=equal_var)
        df_val = (n1 + n2 - 2) if equal_var else round(float(stats.ttest_ind(g1_data, g2_data, equal_var=False).df), 1)
        
        # Cohen's d (pooled)
        pooled_sd = np.sqrt(((n1 - 1) * (sd1**2) + (n2 - 1) * (sd2**2)) / (n1 + n2 - 2))
        cohen_d = (m1 - m2) / pooled_sd if pooled_sd > 0 else 0.0
        
        # Mann-Whitney U fallback
        u_stat, u_p = stats.mannwhitneyu(g1_data, g2_data, alternative='two-sided')
        
        return {
            "design": "independent",
            "variable": var_col,
            "group_variable": group_col,
            "groups": [str(groups[0]), str(groups[1])],
            "n1": n1, "mean1": round(m1, 2), "sd1": round(sd1, 2),
            "n2": n2, "mean2": round(m2, 2), "sd2": round(sd2, 2),
            "levene_f": round(float(levene_stat), 2),
            "levene_p": float(levene_p),
            "levene_p_str": format_p_value(float(levene_p)),
            "equal_var_assumed": bool(equal_var),
            "t": round(float(t_stat), 2),
            "df": df_val,
            "p": float(p_val),
            "p_str": format_p_value(float(p_val)),
            "cohen_d": round(float(cohen_d), 2),
            "mann_whitney_u": round(float(u_stat), 2),
            "mann_whitney_p": float(u_p),
            "mann_whitney_p_str": format_p_value(float(u_p))
        }

# --- 5. One-Way ANCOVA (Intervention Studies) ---
def analyze_ancova(df: pd.DataFrame, dv_col: str, group_col: str, covar_col: str) -> dict:
    sub_df = df[[dv_col, group_col, covar_col]].apply(pd.to_numeric, errors='coerce').dropna()
    sub_df[group_col] = sub_df[group_col].astype(str)
    
    # 1. Test Homogeneity of Slopes: DV ~ Group * Covariate
    slope_model = ols(f"{dv_col} ~ C({group_col}) * {covar_col}", data=sub_df).fit()
    anova_slopes = sm.stats.anova_lm(slope_model, typ=3)
    interaction_term = f"C({group_col}):{covar_col}"
    slope_p = float(anova_slopes.loc[interaction_term, "PR(>F)"]) if interaction_term in anova_slopes.index else 1.0
    slope_homogeneity_met = (slope_p > 0.05)
    
    # 2. Fit Standard ANCOVA Model: DV ~ Covariate + Group
    ancova_model = ols(f"{dv_col} ~ {covar_col} + C({group_col})", data=sub_df).fit()
    anova_table = sm.stats.anova_lm(ancova_model, typ=3)
    
    group_term = f"C({group_col})"
    ss_group = float(anova_table.loc[group_term, "sum_sq"])
    df_group = int(anova_table.loc[group_term, "df"])
    f_group = float(anova_table.loc[group_term, "F"])
    p_group = float(anova_table.loc[group_term, "PR(>F)"])
    
    ss_resid = float(anova_table.loc["Residual", "sum_sq"])
    df_resid = int(anova_table.loc["Residual", "df"])
    
    # Partial eta-squared: SS_effect / (SS_effect + SS_residual)
    eta_sq_partial = ss_group / (ss_group + ss_resid) if (ss_group + ss_resid) > 0 else 0.0
    
    # Group adjusted means
    mean_covar = sub_df[covar_col].mean()
    group_levels = sub_df[group_col].unique()
    adjusted_means = {}
    for grp in group_levels:
        pred_val = ancova_model.predict(pd.DataFrame({covar_col: [mean_covar], group_col: [grp]}))[0]
        adjusted_means[grp] = round(float(pred_val), 2)
        
    return {
        "dv": dv_col,
        "group_var": group_col,
        "covariate": covar_col,
        "n_total": len(sub_df),
        "slope_homogeneity_p": float(slope_p),
        "slope_homogeneity_p_str": format_p_value(float(slope_p)),
        "slope_homogeneity_met": bool(slope_homogeneity_met),
        "f_stat": round(f_group, 2),
        "df_between": df_group,
        "df_within": df_resid,
        "p": float(p_group),
        "p_str": format_p_value(float(p_group)),
        "partial_eta_squared": round(float(eta_sq_partial), 3),
        "partial_eta_squared_str": f"{eta_sq_partial:.3f}"[1:] if 0 <= eta_sq_partial <= 1 else f"{eta_sq_partial:.3f}",
        "adjusted_means": adjusted_means
    }

# --- 6. Hierarchical Multiple Regression ---
def analyze_hierarchical_regression(df: pd.DataFrame, dv_col: str, step1_vars: list, step2_vars: list = None) -> dict:
    all_vars = [dv_col] + step1_vars + (step2_vars if step2_vars else [])
    sub_df = df[all_vars].apply(pd.to_numeric, errors='coerce').dropna()
    n = len(sub_df)
    
    # Step 1
    X1 = sm.add_constant(sub_df[step1_vars])
    y = sub_df[dv_col]
    model1 = sm.OLS(y, X1).fit()
    r2_1 = float(model1.rsquared)
    f1 = float(model1.fvalue)
    p1 = float(model1.f_pvalue)
    
    coeffs1 = []
    for var in step1_vars:
        b = float(model1.params[var])
        se = float(model1.bse[var])
        t = float(model1.tvalues[var])
        p = float(model1.pvalues[var])
        beta = b * (sub_df[var].std() / y.std()) if y.std() > 0 else 0.0
        coeffs1.append({
            "variable": var, "B": round(b, 3), "SE": round(se, 3),
            "beta": round(float(beta), 3), "t": round(t, 2), "p": float(p),
            "p_str": format_p_value(p)
        })
        
    res = {
        "dv": dv_col,
        "n": n,
        "step1": {
            "variables": step1_vars,
            "r2": round(r2_1, 3),
            "r2_str": f"{r2_1:.3f}"[1:],
            "f": round(f1, 2),
            "df1": len(step1_vars),
            "df2": n - len(step1_vars) - 1,
            "p": float(p1),
            "p_str": format_p_value(p1),
            "coefficients": coeffs1
        }
    }
    
    # Step 2 (if specified)
    if step2_vars:
        combined_vars = step1_vars + step2_vars
        X2 = sm.add_constant(sub_df[combined_vars])
        model2 = sm.OLS(y, X2).fit()
        r2_2 = float(model2.rsquared)
        f2 = float(model2.fvalue)
        p2 = float(model2.f_pvalue)
        
        delta_r2 = r2_2 - r2_1
        delta_f = ((delta_r2) / len(step2_vars)) / ((1 - r2_2) / (n - len(combined_vars) - 1)) if (1 - r2_2) > 0 else 0.0
        delta_p = stats.f.sf(delta_f, len(step2_vars), n - len(combined_vars) - 1)
        
        # Collinearity VIF for final model
        vif_data = {}
        for i, col in enumerate(combined_vars):
            vif_data[col] = round(float(variance_inflation_factor(X2.values, i + 1)), 2)
            
        coeffs2 = []
        for var in combined_vars:
            b = float(model2.params[var])
            se = float(model2.bse[var])
            t = float(model2.tvalues[var])
            p = float(model2.pvalues[var])
            beta = b * (sub_df[var].std() / y.std()) if y.std() > 0 else 0.0
            coeffs2.append({
                "variable": var, "B": round(b, 3), "SE": round(se, 3),
                "beta": round(float(beta), 3), "t": round(t, 2), "p": float(p),
                "p_str": format_p_value(p), "VIF": vif_data[var]
            })
            
        res["step2"] = {
            "added_variables": step2_vars,
            "r2": round(r2_2, 3),
            "r2_str": f"{r2_2:.3f}"[1:],
            "f": round(f2, 2),
            "df1": len(combined_vars),
            "df2": n - len(combined_vars) - 1,
            "p": float(p2),
            "p_str": format_p_value(p2),
            "delta_r2": round(delta_r2, 3),
            "delta_r2_str": f"{delta_r2:.3f}"[1:],
            "delta_f": round(float(delta_f), 2),
            "delta_p": float(delta_p),
            "delta_p_str": format_p_value(float(delta_p)),
            "coefficients": coeffs2
        }
        
    return res

# --- 7. Bootstrap Mediation (PROCESS Model 4) ---
def analyze_bootstrap_mediation(df: pd.DataFrame, x_col: str, m_col: str, y_col: str, n_boot: int = 2000, seed: int = 42) -> dict:
    sub_df = df[[x_col, m_col, y_col]].apply(pd.to_numeric, errors='coerce').dropna()
    n = len(sub_df)
    
    # Path a: M ~ X
    Xa = sm.add_constant(sub_df[x_col])
    model_a = sm.OLS(sub_df[m_col], Xa).fit()
    path_a = float(model_a.params[x_col])
    se_a = float(model_a.bse[x_col])
    t_a = float(model_a.tvalues[x_col])
    p_a = float(model_a.pvalues[x_col])
    
    # Path b & c': Y ~ X + M
    Xb = sm.add_constant(sub_df[[x_col, m_col]])
    model_b = sm.OLS(sub_df[y_col], Xb).fit()
    path_b = float(model_b.params[m_col])
    se_b = float(model_b.bse[m_col])
    t_b = float(model_b.tvalues[m_col])
    p_b = float(model_b.pvalues[m_col])
    
    path_c_prime = float(model_b.params[x_col])
    se_c_prime = float(model_b.bse[x_col])
    t_c_prime = float(model_b.tvalues[x_col])
    p_c_prime = float(model_b.pvalues[x_col])
    
    # Path c (Total): Y ~ X
    Xc = sm.add_constant(sub_df[x_col])
    model_c = sm.OLS(sub_df[y_col], Xc).fit()
    path_c = float(model_c.params[x_col])
    se_c = float(model_c.bse[x_col])
    t_c = float(model_c.tvalues[x_col])
    p_c = float(model_c.pvalues[x_col])
    
    indirect_point = path_a * path_b
    
    # Bootstrapping indirect effect
    rng = np.random.default_rng(seed)
    boot_effects = []
    x_vals = sub_df[x_col].values
    m_vals = sub_df[m_col].values
    y_vals = sub_df[y_col].values
    
    for _ in range(n_boot):
        idx = rng.choice(n, size=n, replace=True)
        bx, bm, by = x_vals[idx], m_vals[idx], y_vals[idx]
        
        # quick OLS for a
        cov_xm = np.cov(bx, bm)[0, 1]
        var_x = np.var(bx, ddof=1)
        b_a = cov_xm / var_x if var_x > 0 else 0.0
        
        # OLS for b in Y ~ X + M
        X_mat = np.column_stack([np.ones(n), bx, bm])
        try:
            params = np.linalg.lstsq(X_mat, by, rcond=None)[0]
            b_b = params[2]
            boot_effects.append(b_a * b_b)
        except np.linalg.LinAlgError:
            continue
            
    boot_effects = np.array(boot_effects)
    ci_lower = float(np.percentile(boot_effects, 2.5))
    ci_upper = float(np.percentile(boot_effects, 97.5))
    is_significant = (ci_lower > 0 and ci_upper > 0) or (ci_lower < 0 and ci_upper < 0)
    
    return {
        "x": x_col, "m": m_col, "y": y_col, "n": n, "n_boot": n_boot,
        "path_a": {"B": round(path_a, 3), "SE": round(se_a, 3), "t": round(t_a, 2), "p": float(p_a), "p_str": format_p_value(p_a)},
        "path_b": {"B": round(path_b, 3), "SE": round(se_b, 3), "t": round(t_b, 2), "p": float(p_b), "p_str": format_p_value(p_b)},
        "path_c_total": {"B": round(path_c, 3), "SE": round(se_c, 3), "t": round(t_c, 2), "p": float(p_c), "p_str": format_p_value(p_c)},
        "path_c_prime_direct": {"B": round(path_c_prime, 3), "SE": round(se_c_prime, 3), "t": round(t_c_prime, 2), "p": float(p_c_prime), "p_str": format_p_value(p_c_prime)},
        "indirect_effect": {
            "estimate": round(float(indirect_point), 3),
            "boot_se": round(float(boot_effects.std()), 3),
            "ci_95_lower": round(ci_lower, 3),
            "ci_95_upper": round(ci_upper, 3),
            "is_significant": bool(is_significant)
        }
    }

# --- CLI Dispatcher ---
def main():
    parser = argparse.ArgumentParser(description="Psychology Statistical Analysis CLI Engine")
    parser.add_argument("--data", required=True, help="Path to .xlsx, .csv, or .sav data file")
    parser.add_argument("--task", required=True, choices=["descriptives", "reliability", "correlation", "group_test", "ancova", "regression", "mediation", "auto"], help="Analysis task to execute")
    parser.add_argument("--vars", help="Comma-separated variable names")
    parser.add_argument("--items", help="Comma-separated item column names for reliability")
    parser.add_argument("--group", help="Group column name")
    parser.add_argument("--dv", help="Dependent variable column name")
    parser.add_argument("--covar", help="Covariate column name (for ANCOVA)")
    parser.add_argument("--step1", help="Comma-separated Step 1 predictors (regression)")
    parser.add_argument("--step2", help="Comma-separated Step 2 predictors (regression)")
    parser.add_argument("--x", help="Independent variable (mediation)")
    parser.add_argument("--m", help="Mediator variable (mediation)")
    parser.add_argument("--y", help="Dependent variable (mediation)")
    parser.add_argument("--paired", action="store_true", help="Paired comparison flag")
    parser.add_argument("--var2", help="Second variable for paired comparison")
    parser.add_argument("--method", default="pearson", choices=["pearson", "spearman"], help="Correlation method")
    parser.add_argument("--bootstraps", type=int, default=2000, help="Number of bootstrap resamples")
    parser.add_argument("--config", help="Path to a JSON configuration file for full auto-run")
    parser.add_argument("--out", default="stats_results.json", help="Output JSON path")
    
    args = parser.parse_args()
    df = load_dataset(args.data)
    
    results = {}
    if args.task == "descriptives":
        var_list = [v.strip() for v in args.vars.split(",")]
        results["descriptives"] = analyze_descriptives_and_normality(df, var_list)
        
    elif args.task == "reliability":
        item_list = [v.strip() for v in args.items.split(",")]
        results["reliability"] = analyze_scale_reliability(df, item_list)
        
    elif args.task == "correlation":
        var_list = [v.strip() for v in args.vars.split(",")]
        results["correlation"] = analyze_correlation_matrix(df, var_list, method=args.method)
        
    elif args.task == "group_test":
        results["group_test"] = analyze_group_comparison(df, args.vars, args.group, paired=args.paired, var2_col=args.var2)
        
    elif args.task == "ancova":
        results["ancova"] = analyze_ancova(df, args.dv, args.group, args.covar)
        
    elif args.task == "regression":
        s1 = [v.strip() for v in args.step1.split(",")]
        s2 = [v.strip() for v in args.step2.split(",")] if args.step2 else None
        results["regression"] = analyze_hierarchical_regression(df, args.dv, s1, s2)
        
    elif args.task == "mediation":
        results["mediation"] = analyze_bootstrap_mediation(df, args.x, args.m, args.y, n_boot=args.bootstraps)
        
    elif args.task == "auto":
        if not args.config:
            print("Error: --config required for 'auto' task.", file=sys.stderr)
            sys.exit(1)
        with open(args.config, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            
        if "descriptives" in cfg:
            results["descriptives"] = analyze_descriptives_and_normality(df, cfg["descriptives"]["vars"])
        if "reliability" in cfg:
            results["reliability"] = {}
            for scale_name, items in cfg["reliability"].items():
                results["reliability"][scale_name] = analyze_scale_reliability(df, items)
        if "correlation" in cfg:
            results["correlation"] = analyze_correlation_matrix(df, cfg["correlation"]["vars"], cfg["correlation"].get("method", "pearson"))
        if "group_tests" in cfg:
            results["group_tests"] = []
            for gt in cfg["group_tests"]:
                results["group_tests"].append(analyze_group_comparison(df, gt["var"], gt["group"]))
        if "ancova" in cfg:
            results["ancova"] = []
            for ac in cfg["ancova"]:
                results["ancova"].append(analyze_ancova(df, ac["dv"], ac["group"], ac["covar"]))
        if "regression" in cfg:
            results["regression"] = []
            for reg in cfg["regression"]:
                results["regression"].append(analyze_hierarchical_regression(df, reg["dv"], reg["step1"], reg.get("step2")))
        if "mediation" in cfg:
            results["mediation"] = []
            for med in cfg["mediation"]:
                results["mediation"].append(analyze_bootstrap_mediation(df, med["x"], med["m"], med["y"], n_boot=med.get("bootstraps", 2000)))

    # Save output
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Analysis completed successfully. Output saved to {args.out}")

if __name__ == "__main__":
    main()
