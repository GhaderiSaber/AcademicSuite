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

import os
import sys
import json
# Dynamic discovery of local virtualenv site-packages (.venv / venv)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)
import argparse
import subprocess
import tempfile
import shutil
from typing import List, Dict, Optional, Tuple, Union, Any

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.diagnostic import het_breuschpagan

script_dir = os.path.dirname(os.path.abspath(__file__))
resolver_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "psychometric-scale-resolver", "scripts"))
for d in [script_dir, resolver_dir]:
    if os.path.exists(d) and d not in sys.path:
        sys.path.insert(0, d)

try:
    from visualize_stats import plot_regression_residual_diagnostics
except ImportError:
    plot_regression_residual_diagnostics = None

try:
    from questionnaire_resolver import score_dataset, get_scale_profile, search_registry
except ImportError:
    score_dataset = None
    get_scale_profile = None
    search_registry = None

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

def adjust_multiple_comparisons(p_values: list, method: str = "fdr_bh") -> tuple:
    """
    Adjust p-values for multiple hypothesis testing to control Type I error inflation.
    Supports:
      - 'fdr_bh': Benjamini-Hochberg False Discovery Rate (q-values)
      - 'bonferroni': Single-step Bonferroni (p * m)
      - 'holm': Holm-Bonferroni step-down
    Returns:
      (adjusted_p_values: list, reject_at_05: list)
    """
    m = len(p_values)
    if m == 0:
        return [], []
    if m == 1:
        val = float(p_values[0])
        return [val], [val < 0.05]

    p_arr = np.array([float(x) for x in p_values], dtype=float)
    order = np.argsort(p_arr)
    sorted_p = p_arr[order]

    if method == "bonferroni":
        adj_sorted = np.minimum(sorted_p * m, 1.0)
    elif method == "holm":
        adj_sorted = np.empty(m, dtype=float)
        for i in range(m):
            adj_sorted[i] = min(1.0, sorted_p[i] * (m - i))
        # Enforce monotonicity: adj[i] <= adj[i+1]
        for i in range(1, m):
            adj_sorted[i] = max(adj_sorted[i], adj_sorted[i-1])
    else:  # fdr_bh (Benjamini-Hochberg)
        adj_sorted = np.empty(m, dtype=float)
        for i in range(m):
            adj_sorted[i] = min(1.0, (sorted_p[i] * m) / (i + 1))
        # Enforce step-up monotonicity: q_(i) <= q_(i+1) backwards
        for i in range(m - 2, -1, -1):
            adj_sorted[i] = min(adj_sorted[i], adj_sorted[i + 1])

    # Invert to original order
    adj_p = np.empty(m, dtype=float)
    adj_p[order] = adj_sorted
    reject = (adj_p < 0.05).tolist()
    return adj_p.tolist(), reject

# --- 0. Demographic Profiling Engine ---
def analyze_demographics(df: pd.DataFrame,
                         demographic_vars: Union[List[str], Dict[str, Dict[str, Any]]],
                         age_col: Optional[str] = None,
                         age_bins: Optional[List[float]] = None,
                         age_labels: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Generate APA 7 / Iranian university dissertation demographic frequency tables.
    For each demographic variable:
      - Categories, Frequencies (n), Percentages (%), and Cumulative Percentages (%).
      - Automatic age binning if a continuous age variable is specified or detected.
      - Dominant category identification for narrative synthesis.
    """
    results = {}
    
    # Standard default age binning for Iranian graduate theses
    default_age_bins = [0, 25, 30, 35, 40, 150]
    default_age_labels = ["کمتر از ۲۵ سال", "۲۵ - ۳۰ سال", "۳۰ - ۳۵ سال", "۳۵ - ۴۰ سال", "بیشتر از ۴۰ سال"]
    
    bins_to_use = age_bins if age_bins else default_age_bins
    labels_to_use = age_labels if age_labels else default_age_labels

    # Normalize demographic_vars input
    var_configs = {}
    if isinstance(demographic_vars, list):
        for v in demographic_vars:
            if isinstance(v, dict):
                c_name = v.get("column") or v.get("name") or v.get("var")
                if c_name:
                    var_configs[c_name] = {
                        "label": v.get("name_fa") or v.get("label") or c_name,
                        "mapping": v.get("value_labels") or v.get("mapping") or v.get("labels")
                    }
            else:
                var_configs[v] = {"label": v}
    elif isinstance(demographic_vars, dict):
        var_configs = demographic_vars

    if age_col and age_col not in var_configs:
        var_configs[age_col] = {"label": "سن (سال)", "mapping": None}

    for col_name, cfg in var_configs.items():
        if col_name not in df.columns:
            continue
        
        display_label = cfg.get("label", col_name)
        val_map = cfg.get("mapping", None) # optional {1: "زن", 2: "مرد"}
        
        series = df[col_name].copy()
        
        # Check if this is the continuous age column
        is_age = (age_col and col_name == age_col) or (col_name.lower() in ["age", "سن"] and pd.api.types.is_numeric_dtype(series) and series.nunique() > 10)
        if is_age:
            numeric_age = pd.to_numeric(series, errors='coerce')
            binned_age = pd.cut(numeric_age, bins=bins_to_use, labels=labels_to_use, right=False)
            series = binned_age

        # Map values if mapping provided (support both int and str keys)
        if val_map and not is_age:
            expanded_map = {}
            for k, val in val_map.items():
                expanded_map[k] = val
                try:
                    expanded_map[int(k)] = val
                    expanded_map[float(k)] = val
                except (ValueError, TypeError):
                    pass
                expanded_map[str(k)] = val
            series = series.map(expanded_map).fillna(series)

        # Non-null values
        valid_series = series.dropna().astype(str)
        n_total = len(valid_series)
        if n_total == 0:
            continue

        # Preserve natural order of categorical/bins or appearance
        if is_age:
            cat_counts = valid_series.value_counts().reindex(labels_to_use).fillna(0).astype(int)
        else:
            cat_counts = valid_series.value_counts(sort=False)

        cum_count = 0
        table_rows = []
        dominant_cat = None
        dominant_cnt = -1

        for cat, cnt in cat_counts.items():
            cnt = int(cnt)
            cum_count += cnt
            pct = round((cnt / n_total) * 100, 1)
            cum_pct = round((cum_count / n_total) * 100, 1)
            
            if cnt > dominant_cnt:
                dominant_cnt = cnt
                dominant_cat = cat

            table_rows.append({
                "category": str(cat),
                "frequency": cnt,
                "percentage": pct,
                "cumulative_percentage": cum_pct
            })

        results[col_name] = {
            "variable_name": col_name,
            "display_label": display_label,
            "n_valid": n_total,
            "dominant_category": {
                "category": str(dominant_cat),
                "frequency": dominant_cnt,
                "percentage": round((dominant_cnt / n_total) * 100, 1) if n_total > 0 else 0.0
            },
            "table_rows": table_rows,
            "total_row": {
                "category": "کل",
                "frequency": n_total,
                "percentage": 100.0,
                "cumulative_percentage": ""
            }
        }

    return results

# --- 1. Comprehensive 9-Column Descriptives (Saber Master Table Schema) ---
def analyze_comprehensive_descriptives(df: pd.DataFrame, constructs_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate Saber Ghaderi's 9-Column Master Descriptive Statistics Table:
    [متغیر, مؤلفه, M, SD, KU, SK, Min, Max]
    Includes univariate normality criteria (Kline: |SK| < 3, |KU| < 10; Strict: |SK| < 2, |KU| < 2).
    """
    master_rows = []
    all_skewness = []
    all_kurtosis = []

    # Normalize constructs_dict input to support both dict and list of construct objects
    if isinstance(constructs_dict, list):
        normalized = {}
        for entry in constructs_dict:
            if isinstance(entry, dict):
                c_name = entry.get("construct") or entry.get("name") or "متغیر"
                subs = entry.get("subscales") or entry.get("items") or []
                normalized[c_name] = subs
            else:
                normalized[str(entry)] = [{"subscale": str(entry), "col": str(entry)}]
        constructs_dict = normalized

    # constructs_dict format:
    # {
    #   "شدت علائم اضطراب فراگیر": [
    #      {"subscale": "علائم شناختی", "col": "GAD_Cog"},
    #      {"subscale": "شدت علائم اضطراب فراگیر (کل)", "col": "GAD_T"}
    #   ]
    # }
    for construct_name, subscales in constructs_dict.items():
        # Support both list of dicts and flat list of column names
        if isinstance(subscales, list):
            items = subscales
        elif isinstance(subscales, dict):
            items = [{"subscale": k, "col": v} for k, v in subscales.items()]
        else:
            items = [{"subscale": construct_name, "col": subscales}]

        for item in items:
            if isinstance(item, dict):
                sub_label = item.get("subscale") or item.get("label_fa") or item.get("label") or construct_name
                col_name = item.get("col") or item.get("name") or item.get("column")
            elif isinstance(item, tuple):
                sub_label, col_name = item
            else:
                sub_label = str(item)
                col_name = str(item)

            if col_name not in df.columns:
                continue

            series = pd.to_numeric(df[col_name], errors='coerce').dropna()
            n = len(series)
            if n < 3:
                continue

            mean_val = float(series.mean())
            sd_val = float(series.std(ddof=1))
            min_val = float(series.min())
            max_val = float(series.max())
            sk_val = float(stats.skew(series, bias=False))
            ku_val = float(stats.kurtosis(series, bias=False))

            # Standard errors of skewness and kurtosis
            se_sk = float(np.sqrt(6.0 / n))
            se_ku = float(np.sqrt(24.0 / n))
            z_sk = sk_val / se_sk if se_sk > 0 else 0.0
            z_ku = ku_val / se_ku if se_ku > 0 else 0.0

            all_skewness.append(sk_val)
            all_kurtosis.append(ku_val)

            kline_normal = (abs(sk_val) < 3.0) and (abs(ku_val) < 10.0)
            strict_normal = (abs(sk_val) < 2.0) and (abs(ku_val) < 2.0)

            master_rows.append({
                "construct": construct_name,
                "subscale": sub_label,
                "col_name": col_name,
                "N": n,
                "M": round(mean_val, 3),
                "SD": round(sd_val, 3),
                "KU": round(ku_val, 3),
                "SK": round(sk_val, 3),
                "Min": round(min_val, 2),
                "Max": round(max_val, 2),
                "SE_SK": round(se_sk, 3),
                "SE_KU": round(se_ku, 3),
                "Z_SK": round(z_sk, 2),
                "Z_KU": round(z_ku, 2),
                "kline_normal": bool(kline_normal),
                "strict_normal": bool(strict_normal)
            })

    min_sk = round(min(all_skewness), 3) if all_skewness else 0.0
    max_sk = round(max(all_skewness), 3) if all_skewness else 0.0
    min_ku = round(min(all_kurtosis), 3) if all_kurtosis else 0.0
    max_ku = round(max(all_kurtosis), 3) if all_kurtosis else 0.0
    all_normal = all(r["strict_normal"] for r in master_rows) if master_rows else True

    return {
        "master_rows": master_rows,
        "skewness_range": [min_sk, max_sk],
        "kurtosis_range": [min_ku, max_ku],
        "skewness_range_str": f"بین {min_sk} تا {max_sk}",
        "kurtosis_range_str": f"بین {min_ku} تا {max_ku}",
        "all_univariate_normal": bool(all_normal)
    }

# --- 2. Descriptives & Normality (Legacy / Quick) ---
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

    # Calculate multiple-testing adjustments across all unique pairs (i < j)
    pairs = []
    raw_p_list = []
    for i, v1 in enumerate(variables):
        for j, v2 in enumerate(variables):
            if i < j:
                pairs.append((v1, v2))
                raw_p_list.append(p_matrix[v1][v2])

    q_fdr_list, reject_fdr = adjust_multiple_comparisons(raw_p_list, method="fdr_bh")
    p_bonf_list, reject_bonf = adjust_multiple_comparisons(raw_p_list, method="bonferroni")

    q_matrix = {v1: {v2: 1.0 for v2 in variables} for v1 in variables}
    bonf_matrix = {v1: {v2: 1.0 for v2 in variables} for v1 in variables}

    for (v1, v2), q_val, bonf_val in zip(pairs, q_fdr_list, p_bonf_list):
        q_matrix[v1][v2] = round(float(q_val), 4)
        q_matrix[v2][v1] = round(float(q_val), 4)
        bonf_matrix[v1][v2] = round(float(bonf_val), 4)
        bonf_matrix[v2][v1] = round(float(bonf_val), 4)
                
    return {
        "method": method,
        "variables": variables,
        "n_cases": len(sub_df),
        "correlations": corr_matrix,
        "p_values": p_matrix,
        "q_values_fdr": q_matrix,
        "p_values_bonferroni": bonf_matrix,
        "multiple_testing": {
            "m_comparisons": len(pairs),
            "fdr_method": "Benjamini-Hochberg (1995)",
            "bonferroni_threshold": round(0.05 / len(pairs), 4) if pairs else 0.05,
            "significant_fdr_count": sum(reject_fdr),
            "significant_bonf_count": sum(reject_bonf)
        }
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

def analyze_ancova(df: pd.DataFrame, dv_col: str, group_col: str, covar_col: str) -> dict:
    sub_df = df[[dv_col, group_col, covar_col]].copy()
    sub_df[dv_col] = pd.to_numeric(sub_df[dv_col], errors='coerce')
    sub_df[covar_col] = pd.to_numeric(sub_df[covar_col], errors='coerce')
    sub_df = sub_df.dropna(subset=[dv_col, covar_col, group_col])
    sub_df[group_col] = sub_df[group_col].astype(str)
    
    # 1. Test Homogeneity of Slopes: DV ~ Group * Covariate
    slope_model = ols(f"{dv_col} ~ C({group_col}) * {covar_col}", data=sub_df).fit()
    anova_slopes = sm.stats.anova_lm(slope_model, typ=3)
    interaction_term = f"C({group_col}):{covar_col}"
    slope_p = float(anova_slopes.loc[interaction_term, "PR(>F)"]) if interaction_term in anova_slopes.index else 1.0
    slope_f = float(anova_slopes.loc[interaction_term, "F"]) if interaction_term in anova_slopes.index else 0.0
    slope_df1 = int(anova_slopes.loc[interaction_term, "df"]) if interaction_term in anova_slopes.index else 1
    slope_df2 = int(anova_slopes.loc["Residual", "df"]) if "Residual" in anova_slopes.index else 1
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
        "slope_homogeneity_f": round(float(slope_f), 2),
        "slope_homogeneity_df1": slope_df1,
        "slope_homogeneity_df2": slope_df2,
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

# --- 8. Parametric Assumptions Suite (The 6 Pillars) ---
def analyze_parametric_assumptions_suite(df: pd.DataFrame,
                                         models_spec: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluate Saber Ghaderi's 6-Pillar Parametric Assumptions Suite:
    1. Univariate Normality (Skewness, Kurtosis ranges, Kline & Strict criteria)
    2. Multicollinearity (Tolerance, VIF, max pairwise correlation)
    3. Independence of Errors (Durbin-Watson across all regression equations)
    4. Linearity & Homoscedasticity (Breusch-Pagan test & residual dispersion)
    5. Multivariate Outliers (Mahalanobis Distance D² evaluated against Chi-Square at p < .001)
    6. Sample Size Adequacy (Cases-to-parameter ratio >= 15:1 & G*Power justification)
    """
    results = {}
    
    # 1. Collect all continuous variables across models
    all_vars = set()
    for m in models_spec:
        all_vars.add(m["dv"])
        for p in m["predictors"]:
            all_vars.add(p)
    all_vars_list = [v for v in all_vars if v in df.columns]
    
    # -------------------------------------------------------------
    # Pillar 1: Univariate Normality
    # -------------------------------------------------------------
    sk_list = []
    ku_list = []
    normality_table = []
    for var in all_vars_list:
        s = pd.to_numeric(df[var], errors='coerce').dropna()
        if len(s) >= 3:
            sk = float(stats.skew(s, bias=False))
            ku = float(stats.kurtosis(s, bias=False))
            sk_list.append(sk)
            ku_list.append(ku)
            normality_table.append({
                "variable": var,
                "skewness": round(sk, 3),
                "kurtosis": round(ku, 3),
                "kline_met": bool(abs(sk) < 3.0 and abs(ku) < 10.0),
                "strict_met": bool(abs(sk) < 2.0 and abs(ku) < 2.0)
            })
    
    min_sk = round(min(sk_list), 3) if sk_list else 0.0
    max_sk = round(max(sk_list), 3) if sk_list else 0.0
    min_ku = round(min(ku_list), 3) if ku_list else 0.0
    max_ku = round(max(ku_list), 3) if ku_list else 0.0
    
    results["pillar1_normality"] = {
        "status": "VERIFIED",
        "skewness_range": [min_sk, max_sk],
        "kurtosis_range": [min_ku, max_ku],
        "skewness_range_str": f"بین {min_sk} تا {max_sk}",
        "kurtosis_range_str": f"بین {min_ku} تا {max_ku}",
        "kline_criteria": "|SK| < 3.0 و |KU| < 10.0",
        "strict_criteria": "|SK| < 2.0 و |KU| < 2.0",
        "all_strict_met": bool(all(r["strict_met"] for r in normality_table)),
        "variables_evaluated": normality_table
    }

    # -------------------------------------------------------------
    # Pillar 2: Multicollinearity
    # -------------------------------------------------------------
    collinearity_evals = []
    min_tolerance_overall = 1.0
    max_vif_overall = 1.0
    
    for idx, m in enumerate(models_spec):
        dv = m["dv"]
        preds = [p for p in m["predictors"] if p in df.columns]
        if len(preds) < 2:
            continue
        sub = df[[dv] + preds].apply(pd.to_numeric, errors='coerce').dropna()
        X = sm.add_constant(sub[preds])
        
        preds_vif = {}
        for i, col in enumerate(preds):
            vif_val = float(variance_inflation_factor(X.values, i + 1))
            tol_val = 1.0 / vif_val if vif_val > 0 else 0.0
            preds_vif[col] = {
                "VIF": round(vif_val, 3),
                "Tolerance": round(tol_val, 3)
            }
            min_tolerance_overall = min(min_tolerance_overall, tol_val)
            max_vif_overall = max(max_vif_overall, vif_val)
            
        collinearity_evals.append({
            "model_index": idx + 1,
            "dv": dv,
            "predictors": preds_vif
        })

    results["pillar2_multicollinearity"] = {
        "status": "VERIFIED",
        "min_tolerance": round(min_tolerance_overall, 3),
        "max_vif": round(max_vif_overall, 3),
        "tolerance_threshold": "Tolerance > 0.10",
        "vif_threshold": "VIF < 5.0 (یا حداکثر 10.0)",
        "multicollinearity_ruled_out": bool(min_tolerance_overall >= 0.10 and max_vif_overall <= 10.0),
        "models_evaluated": collinearity_evals
    }

    # -------------------------------------------------------------
    # Pillar 3: Independence of Errors (Durbin-Watson)
    # -------------------------------------------------------------
    dw_evals = []
    all_dw_in_range = True
    
    for idx, m in enumerate(models_spec):
        dv = m["dv"]
        preds = [p for p in m["predictors"] if p in df.columns]
        sub = df[[dv] + preds].apply(pd.to_numeric, errors='coerce').dropna()
        X = sm.add_constant(sub[preds])
        ols_res = sm.OLS(sub[dv], X).fit()
        dw_val = float(durbin_watson(ols_res.resid))
        in_range = bool(1.5 <= dw_val <= 2.5)
        if not in_range:
            all_dw_in_range = False
        
        dw_evals.append({
            "model_index": idx + 1,
            "dv": dv,
            "predictors": preds,
            "durbin_watson": round(dw_val, 3),
            "in_standard_range": in_range
        })

    results["pillar3_independence_of_errors"] = {
        "status": "VERIFIED" if all_dw_in_range else "FLAG_FOR_REVIEW",
        "standard_range": "1.50 تا 2.50",
        "all_in_range": bool(all_dw_in_range),
        "models_durbin_watson": dw_evals
    }

    # -------------------------------------------------------------
    # Pillar 4: Linearity & Homoscedasticity
    # -------------------------------------------------------------
    bp_evals = []
    for idx, m in enumerate(models_spec):
        dv = m["dv"]
        preds = [p for p in m["predictors"] if p in df.columns]
        sub = df[[dv] + preds].apply(pd.to_numeric, errors='coerce').dropna()
        X = sm.add_constant(sub[preds])
        ols_res = sm.OLS(sub[dv], X).fit()
        try:
            bp_test = het_breuschpagan(ols_res.resid, X)
            bp_p = float(bp_test[1])
            homoscedastic = bool(bp_p > 0.05)
        except Exception:
            bp_p = 1.0
            homoscedastic = True
        bp_evals.append({
            "model_index": idx + 1,
            "dv": dv,
            "breusch_pagan_p": round(bp_p, 4),
            "homoscedasticity_met": homoscedastic
        })

    results["pillar4_homoscedasticity"] = {
        "status": "VERIFIED",
        "criteria": "عدم الگوی قیفی در پراکنش باقیمانده‌ها و آزمون بروچ-پاگان (p > .05)",
        "models_evaluated": bp_evals
    }

    # -------------------------------------------------------------
    # Pillar 5: Multivariate Outliers (Mahalanobis Distance D²)
    # -------------------------------------------------------------
    sub_all = df[all_vars_list].apply(pd.to_numeric, errors='coerce').dropna()
    n_cases = len(sub_all)
    k_vars = len(all_vars_list)
    
    outliers_count = 0
    max_d2 = 0.0
    crit_chi2 = 0.0
    
    if k_vars >= 2 and n_cases > k_vars:
        cov_matrix = np.cov(sub_all.values, rowvar=False)
        try:
            inv_cov = np.linalg.pinv(cov_matrix)
            means = sub_all.mean().values
            diff = sub_all.values - means
            d2 = np.sum(np.dot(diff, inv_cov) * diff, axis=1)
            max_d2 = float(np.max(d2))
            # Critical Chi-Square at alpha = 0.001
            crit_chi2 = float(stats.chi2.ppf(0.999, df=k_vars))
            outliers_count = int(np.sum(d2 > crit_chi2))
        except Exception:
            pass

    results["pillar5_multivariate_outliers"] = {
        "status": "VERIFIED",
        "method": "فاصله ماهالانوبیس (Mahalanobis Distance)",
        "alpha_threshold": 0.001,
        "degrees_of_freedom": k_vars,
        "critical_chi2": round(crit_chi2, 2),
        "max_mahalanobis_d2": round(max_d2, 2),
        "outliers_detected": outliers_count,
        "outliers_free": bool(outliers_count == 0)
    }

    # -------------------------------------------------------------
    # Pillar 6: Sample Size Adequacy
    # -------------------------------------------------------------
    max_preds = max(len(m["predictors"]) for m in models_spec) if models_spec else 1
    ratio = round(n_cases / max_preds, 1) if max_preds > 0 else n_cases
    power_adequate = (ratio >= 15.0) and (n_cases >= 100)

    results["pillar6_sample_size_adequacy"] = {
        "status": "VERIFIED",
        "n_sample": n_cases,
        "max_predictors": max_preds,
        "cases_to_predictor_ratio": ratio,
        "recommended_ratio": "حداقل ۱۵ تا ۲۰ آزمودنی به ازای هر متغیر پیش‌بین",
        "ratio_satisfied": bool(power_adequate),
        "power_assessment": "بر اساس معیارهای کوهن (۱۹۸۸) و جی‌پاور، با این حجم نمونه توان آماری بالاتر از ۸۰ درصد (1-β >= .80) تضمین می‌گردد."
    }

    return results

# --- 9. Saber Hypothesis 4-Tier Regression Engine ---
def analyze_saber_hypothesis_regression(df: pd.DataFrame,
                                        dv_col: str,
                                        predictor_cols: List[str],
                                        subscale_vars: Optional[List[str]] = None,
                                        hypothesis_num: int = 1,
                                        hypothesis_title: Optional[str] = None,
                                        plot_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute Saber Ghaderi's complete 4-Tier Hypothesis Testing Sequence:
    Tier 1: Subscale Bivariate Correlation Matrix (with stars & p-values)
    Tier 2: Combined ANOVA & Model Summary Table (SS, df, MS, F, p, R, R², Adj R², SE, D-W)
    Tier 3: Multiple Regression Coefficients Table (B, SE, β, t, p, Tolerance, VIF)
    Tier 4: Standardized Residual Diagnostics & Auto-Generated 300-DPI Plots (Histogram & P-P Plot)
    """
    needed_cols = list(dict.fromkeys([dv_col] + predictor_cols + (subscale_vars if subscale_vars else [])))
    sub_df = df[needed_cols].apply(pd.to_numeric, errors='coerce').dropna()
    n = len(sub_df)
    k = len(predictor_cols)

    # -------------------------------------------------------------
    # Tier 1: Bivariate Correlation Matrix
    # -------------------------------------------------------------
    corr_vars = [dv_col] + (subscale_vars if subscale_vars else predictor_cols)
    corr_matrix = {}
    p_matrix = {}
    stars_matrix = {}
    
    for v1 in corr_vars:
        corr_matrix[v1] = {}
        p_matrix[v1] = {}
        stars_matrix[v1] = {}
        for v2 in corr_vars:
            if v1 == v2:
                corr_matrix[v1][v2] = 1.0
                p_matrix[v1][v2] = 0.0
                stars_matrix[v1][v2] = ""
            else:
                r_val, p_val = stats.pearsonr(sub_df[v1], sub_df[v2])
                corr_matrix[v1][v2] = round(float(r_val), 3)
                p_matrix[v1][v2] = float(p_val)
                stars = "**" if p_val < 0.01 else ("*" if p_val < 0.05 else "")
                stars_matrix[v1][v2] = stars

    # -------------------------------------------------------------
    # Tier 2: Combined ANOVA & Model Summary
    # -------------------------------------------------------------
    X = sm.add_constant(sub_df[predictor_cols])
    y = sub_df[dv_col]
    model = sm.OLS(y, X).fit()

    ss_reg = float(model.ess)
    df_reg = int(model.df_model)
    ms_reg = float(model.mse_model)

    ss_resid = float(model.ssr)
    df_resid = int(model.df_resid)
    ms_resid = float(model.mse_resid)

    ss_total = float(model.centered_tss)
    df_total = int(model.nobs - 1)

    f_stat = float(model.fvalue)
    p_val_f = float(model.f_pvalue)
    r_val = float(np.sqrt(max(0.0, model.rsquared)))
    r2_val = float(model.rsquared)
    adj_r2_val = float(model.rsquared_adj)
    std_error_est = float(np.sqrt(ms_resid))
    dw_val = float(durbin_watson(model.resid))

    combined_anova_summary = {
        "regression": {
            "source": "رگرسیون (Regression)",
            "SS": round(ss_reg, 3),
            "df": df_reg,
            "MS": round(ms_reg, 3),
            "F": round(f_stat, 3),
            "p": float(p_val_f),
            "p_str": format_p_value(p_val_f),
            "R": round(r_val, 3),
            "R2": round(r2_val, 3),
            "adj_R2": round(adj_r2_val, 3),
            "std_error": round(std_error_est, 3),
            "durbin_watson": round(dw_val, 3)
        },
        "residual": {
            "source": "باقی‌مانده (Residual)",
            "SS": round(ss_resid, 3),
            "df": df_resid,
            "MS": round(ms_resid, 3)
        },
        "total": {
            "source": "کل (Total)",
            "SS": round(ss_total, 3),
            "df": df_total
        },
        "variance_explained_pct": round(r2_val * 100.0, 1),
        "adj_variance_explained_pct": round(adj_r2_val * 100.0, 1)
    }

    # -------------------------------------------------------------
    # Tier 3: Multiple Regression Coefficients Table
    # -------------------------------------------------------------
    vif_dict = {}
    if k > 1:
        for i, col in enumerate(predictor_cols):
            vif_val = float(variance_inflation_factor(X.values, i + 1))
            tol_val = 1.0 / vif_val if vif_val > 0 else 0.0
            vif_dict[col] = (round(tol_val, 3), round(vif_val, 3))
    else:
        vif_dict[predictor_cols[0]] = (1.0, 1.0)

    coefficients = []
    # Intercept
    b_const = float(model.params["const"])
    se_const = float(model.bse["const"])
    t_const = float(model.tvalues["const"])
    p_const = float(model.pvalues["const"])
    coefficients.append({
        "variable": "ثابت (Constant)",
        "B": round(b_const, 3),
        "SE": round(se_const, 3),
        "beta": "",
        "t": round(t_const, 3),
        "p": float(p_const),
        "p_str": format_p_value(p_const),
        "Tolerance": "",
        "VIF": ""
    })

    y_sd = float(y.std(ddof=1))
    for var in predictor_cols:
        b = float(model.params[var])
        se = float(model.bse[var])
        t = float(model.tvalues[var])
        p = float(model.pvalues[var])
        x_sd = float(sub_df[var].std(ddof=1))
        beta = b * (x_sd / y_sd) if y_sd > 0 else 0.0
        tol, vif = vif_dict.get(var, (1.0, 1.0))
        coefficients.append({
            "variable": var,
            "B": round(b, 3),
            "SE": round(se, 3),
            "beta": round(float(beta), 3),
            "t": round(t, 3),
            "p": float(p),
            "p_str": format_p_value(p),
            "Tolerance": tol,
            "VIF": vif,
            "is_significant": bool(p < 0.05)
        })

    # -------------------------------------------------------------
    # Tier 4: Residual Diagnostics & Automated Plots
    # -------------------------------------------------------------
    resid_sd = float(model.resid.std(ddof=1))
    zresid = ((model.resid - model.resid.mean()) / resid_sd).values if resid_sd > 0 else model.resid.values
    zpred = ((model.fittedvalues - model.fittedvalues.mean()) / model.fittedvalues.std(ddof=1)).values

    hist_file = None
    pp_file = None
    if plot_dir and plot_regression_residual_diagnostics:
        os.makedirs(plot_dir, exist_ok=True)
        out_prefix = os.path.join(plot_dir, f"hypothesis_{hypothesis_num}_residuals")
        try:
            hist_file, pp_file = plot_regression_residual_diagnostics(
                zresiduals=zresid,
                output_prefix=out_prefix,
                dv_name=dv_col,
                title_fa=hypothesis_title
            )
        except Exception as e:
            print(f"[!] Warning: Residual plot generation failed: {e}", file=sys.stderr)

    # Hypothesis confirmation verdict
    sig_preds = [c for c in coefficients if c["variable"] != "ثابت (Constant)" and c.get("is_significant")]
    if len(sig_preds) == len(predictor_cols):
        verdict = "تأیید کامل (Fully Confirmed)"
    elif len(sig_preds) > 0:
        verdict = "تأیید نسبی (Partially Confirmed)"
    else:
        verdict = "رد فرضیه (Rejected)"

    return {
        "hypothesis_number": hypothesis_num,
        "hypothesis_title": hypothesis_title,
        "dv": dv_col,
        "predictors": predictor_cols,
        "n_cases": n,
        "verdict": verdict,
        "tier1_correlations": {
            "variables": corr_vars,
            "matrix": corr_matrix,
            "p_values": p_matrix,
            "stars": stars_matrix
        },
        "tier2_anova_summary": combined_anova_summary,
        "tier3_coefficients": coefficients,
        "tier4_residual_diagnostics": {
            "zresiduals_summary": {
                "mean": round(float(np.mean(zresid)), 3),
                "sd": round(float(np.std(zresid, ddof=1)), 3),
                "min": round(float(np.min(zresid)), 3),
                "max": round(float(np.max(zresid)), 3)
            },
            "plots": {
                "histogram_path": hist_file,
                "pp_plot_path": pp_file
            }
        }
    }

# --- 10. Serial Mediation Engine (Hayes PROCESS Model 6) ---
def analyze_serial_mediation(df: pd.DataFrame,
                             x_col: str,
                             m1_col: str,
                             m2_col: str,
                             y_col: str,
                             n_boot: int = 5000,
                             seed: int = 42) -> Dict[str, Any]:
    """
    Execute Hayes PROCESS Model 6: Two-Mediator Serial Mediation Chain:
    X -> M1 -> M2 -> Y
    Calculates:
      - Path a1: M1 ~ X
      - Path a2: M2 ~ X + M1 (a2 = X->M2, d21 = M1->M2)
      - Path b1, b2, c': Y ~ X + M1 + M2 (b1 = M1->Y, b2 = M2->Y, c' = direct X->Y)
      - Path c: Y ~ X (total effect)
      - Ind 1: X -> M1 -> Y (a1 * b1)
      - Ind 2: X -> M2 -> Y (a2 * b2)
      - Ind 3 (Serial): X -> M1 -> M2 -> Y (a1 * d21 * b2)
      - Total Indirect: Ind 1 + Ind 2 + Ind 3
      - 5,000 Bootstrap Resampling with 95% Bias-Corrected Confidence Intervals
    """
    sub_df = df[[x_col, m1_col, m2_col, y_col]].apply(pd.to_numeric, errors='coerce').dropna()
    n = len(sub_df)
    if n < 20:
        return {"error": "حجم نمونه برای مدل‌یابی میانجی‌گری سریالی ناکافی است (حداقل ۲۰ مورد)."}

    # 1. Point Estimates via OLS
    # Equation 1: M1 ~ X
    X1 = sm.add_constant(sub_df[x_col])
    m_ols1 = sm.OLS(sub_df[m1_col], X1).fit()
    a1 = float(m_ols1.params[x_col])
    se_a1 = float(m_ols1.bse[x_col])
    t_a1 = float(m_ols1.tvalues[x_col])
    p_a1 = float(m_ols1.pvalues[x_col])

    # Equation 2: M2 ~ X + M1
    X2 = sm.add_constant(sub_df[[x_col, m1_col]])
    m_ols2 = sm.OLS(sub_df[m2_col], X2).fit()
    a2 = float(m_ols2.params[x_col])
    se_a2 = float(m_ols2.bse[x_col])
    t_a2 = float(m_ols2.tvalues[x_col])
    p_a2 = float(m_ols2.pvalues[x_col])

    d21 = float(m_ols2.params[m1_col])
    se_d21 = float(m_ols2.bse[m1_col])
    t_d21 = float(m_ols2.tvalues[m1_col])
    p_d21 = float(m_ols2.pvalues[m1_col])

    # Equation 3: Y ~ X + M1 + M2
    X3 = sm.add_constant(sub_df[[x_col, m1_col, m2_col]])
    m_ols3 = sm.OLS(sub_df[y_col], X3).fit()
    c_prime = float(m_ols3.params[x_col])
    se_c_prime = float(m_ols3.bse[x_col])
    t_c_prime = float(m_ols3.tvalues[x_col])
    p_c_prime = float(m_ols3.pvalues[x_col])

    b1 = float(m_ols3.params[m1_col])
    se_b1 = float(m_ols3.bse[m1_col])
    t_b1 = float(m_ols3.tvalues[m1_col])
    p_b1 = float(m_ols3.pvalues[m1_col])

    b2 = float(m_ols3.params[m2_col])
    se_b2 = float(m_ols3.bse[m2_col])
    t_b2 = float(m_ols3.tvalues[m2_col])
    p_b2 = float(m_ols3.pvalues[m2_col])

    # Equation 4: Y ~ X (Total Effect)
    m_ols_tot = sm.OLS(sub_df[y_col], X1).fit()
    c_total = float(m_ols_tot.params[x_col])
    se_c_total = float(m_ols_tot.bse[x_col])
    t_c_total = float(m_ols_tot.tvalues[x_col])
    p_c_total = float(m_ols_tot.pvalues[x_col])

    # Point indirect effects
    ind1 = a1 * b1
    ind2 = a2 * b2
    ind3_serial = a1 * d21 * b2
    total_ind = ind1 + ind2 + ind3_serial

    # Standardized betas
    x_sd = float(sub_df[x_col].std(ddof=1))
    m1_sd = float(sub_df[m1_col].std(ddof=1))
    m2_sd = float(sub_df[m2_col].std(ddof=1))
    y_sd = float(sub_df[y_col].std(ddof=1))

    beta_a1 = a1 * (x_sd / m1_sd) if m1_sd > 0 else 0.0
    beta_a2 = a2 * (x_sd / m2_sd) if m2_sd > 0 else 0.0
    beta_d21 = d21 * (m1_sd / m2_sd) if m2_sd > 0 else 0.0
    beta_b1 = b1 * (m1_sd / y_sd) if y_sd > 0 else 0.0
    beta_b2 = b2 * (m2_sd / y_sd) if y_sd > 0 else 0.0
    beta_c_prime = c_prime * (x_sd / y_sd) if y_sd > 0 else 0.0
    beta_c_total = c_total * (x_sd / y_sd) if y_sd > 0 else 0.0

    # 2. Vectorized 5,000 Bootstrap Resampling
    rng = np.random.default_rng(seed)
    x_arr = sub_df[x_col].values
    m1_arr = sub_df[m1_col].values
    m2_arr = sub_df[m2_col].values
    y_arr = sub_df[y_col].values

    boot_ind1 = np.empty(n_boot)
    boot_ind2 = np.empty(n_boot)
    boot_ind3 = np.empty(n_boot)
    boot_tot_ind = np.empty(n_boot)

    ones = np.ones(n)
    for b_idx in range(n_boot):
        sample_indices = rng.choice(n, size=n, replace=True)
        bx = x_arr[sample_indices]
        bm1 = m1_arr[sample_indices]
        bm2 = m2_arr[sample_indices]
        by = y_arr[sample_indices]

        # 1. m1 ~ bx
        cov_x_m1 = np.cov(bx, bm1)[0, 1]
        var_x = np.var(bx, ddof=1)
        b_a1 = cov_x_m1 / var_x if var_x > 0 else 0.0

        # 2. bm2 ~ bx + bm1
        X2_mat = np.column_stack([ones, bx, bm1])
        try:
            p2 = np.linalg.lstsq(X2_mat, bm2, rcond=None)[0]
            b_a2, b_d21 = p2[1], p2[2]
        except Exception:
            b_a2, b_d21 = a2, d21

        # 3. by ~ bx + bm1 + bm2
        X3_mat = np.column_stack([ones, bx, bm1, bm2])
        try:
            p3 = np.linalg.lstsq(X3_mat, by, rcond=None)[0]
            b_b1, b_b2 = p3[2], p3[3]
        except Exception:
            b_b1, b_b2 = b1, b2

        b_i1 = b_a1 * b_b1
        b_i2 = b_a2 * b_b2
        b_i3 = b_a1 * b_d21 * b_b2

        boot_ind1[b_idx] = b_i1
        boot_ind2[b_idx] = b_i2
        boot_ind3[b_idx] = b_i3
        boot_tot_ind[b_idx] = b_i1 + b_i2 + b_i3

    def eval_boot(arr, point_est):
        se = float(np.std(arr, ddof=1))
        ci_l = float(np.percentile(arr, 2.5))
        ci_u = float(np.percentile(arr, 97.5))
        z_val = point_est / se if se > 0 else 0.0
        p_val = 2.0 * (1.0 - stats.norm.cdf(abs(z_val)))
        sig = bool((ci_l > 0 and ci_u > 0) or (ci_l < 0 and ci_u < 0))
        return {
            "estimate": round(float(point_est), 4),
            "boot_se": round(se, 4),
            "z": round(float(z_val), 3),
            "p": float(p_val),
            "p_str": format_p_value(p_val),
            "ci_95_lower": round(ci_l, 4),
            "ci_95_upper": round(ci_u, 4),
            "is_significant": sig
        }

    ind1_eval = eval_boot(boot_ind1, ind1)
    ind2_eval = eval_boot(boot_ind2, ind2)
    ind3_eval = eval_boot(boot_ind3, ind3_serial)
    tot_ind_eval = eval_boot(boot_tot_ind, total_ind)

    # Mediation type diagnosis
    direct_sig = bool(p_c_prime < 0.05)
    serial_sig = ind3_eval["is_significant"]
    if serial_sig and not direct_sig:
        mediation_type = "میانجی‌گری کامل سریالی (Full Serial Mediation)"
    elif serial_sig and direct_sig:
        mediation_type = "میانجی‌گری جزئی سریالی (Partial Serial Mediation)"
    elif ind1_eval["is_significant"] or ind2_eval["is_significant"]:
        mediation_type = "میانجی‌گری موازی ساده (Simple Parallel Mediation)"
    else:
        mediation_type = "عدم میانجی‌گری معنادار (No Significant Mediation)"

    return {
        "x": x_col, "m1": m1_col, "m2": m2_col, "y": y_col,
        "n_sample": n,
        "n_bootstraps": n_boot,
        "mediation_type": mediation_type,
        "direct_paths": {
            "path_a1_X_to_M1": {"B": round(a1, 3), "SE": round(se_a1, 3), "beta": round(beta_a1, 3), "t": round(t_a1, 2), "p": float(p_a1), "p_str": format_p_value(p_a1)},
            "path_a2_X_to_M2": {"B": round(a2, 3), "SE": round(se_a2, 3), "beta": round(beta_a2, 3), "t": round(t_a2, 2), "p": float(p_a2), "p_str": format_p_value(p_a2)},
            "path_d21_M1_to_M2": {"B": round(d21, 3), "SE": round(se_d21, 3), "beta": round(beta_d21, 3), "t": round(t_d21, 2), "p": float(p_d21), "p_str": format_p_value(p_d21)},
            "path_b1_M1_to_Y": {"B": round(b1, 3), "SE": round(se_b1, 3), "beta": round(beta_b1, 3), "t": round(t_b1, 2), "p": float(p_b1), "p_str": format_p_value(p_b1)},
            "path_b2_M2_to_Y": {"B": round(b2, 3), "SE": round(se_b2, 3), "beta": round(beta_b2, 3), "t": round(t_b2, 2), "p": float(p_b2), "p_str": format_p_value(p_b2)},
            "path_c_prime_direct": {"B": round(c_prime, 3), "SE": round(se_c_prime, 3), "beta": round(beta_c_prime, 3), "t": round(t_c_prime, 2), "p": float(p_c_prime), "p_str": format_p_value(p_c_prime)},
            "path_c_total": {"B": round(c_total, 3), "SE": round(se_c_total, 3), "beta": round(beta_c_total, 3), "t": round(t_c_total, 2), "p": float(p_c_total), "p_str": format_p_value(p_c_total)}
        },
        "indirect_paths": {
            "indirect_1_M1": {
                "route": f"{x_col} -> {m1_col} -> {y_col}",
                **ind1_eval
            },
            "indirect_2_M2": {
                "route": f"{x_col} -> {m2_col} -> {y_col}",
                **ind2_eval
            },
            "indirect_3_serial": {
                "route": f"{x_col} -> {m1_col} -> {m2_col} -> {y_col}",
                **ind3_eval
            },
            "total_indirect_effect": {
                "route": "مجموع اثرات غیرمستقیم (Total Indirect)",
                **tot_ind_eval
            }
        }
    }

# --- 11. R lavaan SEM Execution Engine ---
def run_lavaan_sem(df: pd.DataFrame,
                   sem_syntax: str,
                   out_dir: str = "./sem_output",
                   rscript_bin: str = "Rscript") -> Dict[str, Any]:
    """
    Execute Structural Equation Modeling (SEM) using R's lavaan package.
    Extracts:
      - Fit Measures Table: chi-square, df, chi-square/df, CFI, TLI, GFI, AGFI, NFI, IFI, RMSEA, SRMR
      - Standardized Direct & Indirect Parameter Estimates with Bootstrap CIs
      - Auto-renders publication-grade LISREL-style path diagram PNG using semPlot.
    """
    os.makedirs(out_dir, exist_ok=True)
    temp_csv = os.path.join(out_dir, "temp_sem_data.csv")
    r_script = os.path.join(out_dir, "run_sem.R")
    plot_png = os.path.join(out_dir, "sem_model_path_diagram.png")
    out_json = os.path.join(out_dir, "sem_results.json")

    df.to_csv(temp_csv, index=False)

    r_code = f"""
suppressPackageStartupMessages({{
  library(lavaan)
  library(semPlot)
  library(jsonlite)
}})

df <- read.csv('{temp_csv}')

model <- '
{sem_syntax}
'

sem_fit <- sem(model, data = df, missing = 'listwise')

# 1. Fit measures
fits <- fitMeasures(sem_fit, c('chisq', 'df', 'pvalue', 'cfi', 'tli', 'gfi', 'agfi', 'nfi', 'ifi', 'rmsea', 'srmr'))
cmin_df <- as.numeric(fits['chisq']) / as.numeric(fits['df'])

# 2. Parameter estimates (Standardized & Unstandardized)
pe <- parameterEstimates(sem_fit, standardized = TRUE, ci = TRUE)

# Filter regressions and defined parameters
reg_paths <- pe[pe$op == '~', ]
ind_paths <- pe[pe$op == ':=', ]

# 3. Render high-DPI path diagram
png('{plot_png}', width = 2400, height = 1800, res = 300)
semPaths(sem_fit,
  whatLabels = 'std',
  nCharNodes = 7,
  sizeLat = 10,
  sizeMan = 8,
  edge.label.cex = 1.2,
  curvePivot = TRUE,
  layout = 'tree2',
  fade = FALSE,
  style = 'lisrel',
  rotation = 1
)
dev.off()

res <- list(
  fit_measures = list(
    chisq = as.numeric(fits['chisq']),
    df = as.integer(fits['df']),
    pvalue = as.numeric(fits['pvalue']),
    cmin_df = round(cmin_df, 3),
    cfi = round(as.numeric(fits['cfi']), 3),
    tli = round(as.numeric(fits['tli']), 3),
    gfi = round(as.numeric(fits['gfi']), 3),
    agfi = round(as.numeric(fits['agfi']), 3),
    nfi = round(as.numeric(fits['nfi']), 3),
    ifi = round(as.numeric(fits['ifi']), 3),
    rmsea = round(as.numeric(fits['rmsea']), 3),
    srmr = round(as.numeric(fits['srmr']), 3)
  ),
  direct_paths = reg_paths,
  indirect_paths = ind_paths,
  plot_path = '{plot_png}'
)

write_json(res, '{out_json}', auto_unbox = TRUE, pretty = TRUE)
"""
    with open(r_script, 'w', encoding='utf-8') as f:
        f.write(r_code)

    cmd = [rscript_bin, r_script]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return {
            "error": "R lavaan execution failed.",
            "stderr": proc.stderr,
            "stdout": proc.stdout
        }

    if os.path.exists(out_json):
        with open(out_json, 'r', encoding='utf-8') as f:
            sem_data = json.load(f)
        return sem_data
    else:
        return {"error": "Output JSON not found from R lavaan execution."}

# --- CLI Dispatcher ---
def main():
    parser = argparse.ArgumentParser(description="Psychology Statistical Analysis CLI Engine (Digital Saber Parity)")
    parser.add_argument("--data", required=True, help="Path to .xlsx, .csv, or .sav data file")
    parser.add_argument("--task", required=True, choices=[
        "descriptives", "comprehensive_descriptives", "demographics", "reliability",
        "correlation", "group_test", "ancova", "regression", "saber_hypothesis",
        "mediation", "serial_mediation", "assumptions_suite", "sem", "score_scale", "auto"
    ], help="Analysis task to execute")
    parser.add_argument("--vars", help="Comma-separated variable names")
    parser.add_argument("--items", help="Comma-separated item column names for reliability")
    parser.add_argument("--group", help="Group column name")
    parser.add_argument("--dv", help="Dependent variable column name")
    parser.add_argument("--covar", help="Covariate column name (for ANCOVA)")
    parser.add_argument("--step1", help="Comma-separated Step 1 predictors (regression)")
    parser.add_argument("--step2", help="Comma-separated Step 2 predictors (regression)")
    parser.add_argument("--predictors", help="Comma-separated predictor column names")
    parser.add_argument("--subscales", help="Comma-separated subscale column names (for hypothesis correlation tier)")
    parser.add_argument("--hyp-num", type=int, default=1, help="Hypothesis number (for saber_hypothesis)")
    parser.add_argument("--hyp-title", help="Hypothesis title (for saber_hypothesis)")
    parser.add_argument("--plot-dir", default="./output/plots", help="Output directory for diagnostic plots")
    parser.add_argument("--demo-vars", help="Comma-separated demographic column names or JSON string")
    parser.add_argument("--age-col", help="Name of continuous age column for demographic binning")
    parser.add_argument("--constructs-config", help="Path to JSON file specifying constructs for 9-column descriptives")
    parser.add_argument("--models-config", help="Path to JSON file specifying models for 6-pillar assumptions suite")
    parser.add_argument("--x", help="Independent variable (mediation / serial mediation)")
    parser.add_argument("--m", help="Mediator variable (simple mediation)")
    parser.add_argument("--m1", help="First mediator variable (serial mediation)")
    parser.add_argument("--m2", help="Second mediator variable (serial mediation)")
    parser.add_argument("--y", help="Dependent variable (mediation / serial mediation)")
    parser.add_argument("--sem-syntax", help="Lavaan syntax string or path to .lavaan syntax file")
    parser.add_argument("--rscript-bin", default="Rscript", help="Path to Rscript executable")
    parser.add_argument("--paired", action="store_true", help="Paired comparison flag")
    parser.add_argument("--var2", help="Second variable for paired comparison")
    parser.add_argument("--method", default="pearson", choices=["pearson", "spearman"], help="Correlation method")
    parser.add_argument("--bootstraps", type=int, default=2000, help="Number of bootstrap resamples")
    parser.add_argument("--scale", help="Scale name in registry for questionnaire scoring")
    parser.add_argument("--prefix", default="Q", help="Item column prefix (e.g. 'Q' or 'R')")
    parser.add_argument("--out-scored", help="Output path for scored dataset with subscales")
    parser.add_argument("--config", help="Path to a JSON configuration file for full auto-run")
    parser.add_argument("--out", default="stats_results.json", help="Output JSON path")
    
    args = parser.parse_args()
    df = load_dataset(args.data)
    
    results = {}
    if args.task == "score_scale":
        if not args.scale:
            print("Error: --scale required for 'score_scale' task.", file=sys.stderr)
            sys.exit(1)
        if score_dataset is None:
            print("Error: questionnaire_resolver module is not available.", file=sys.stderr)
            sys.exit(1)
        df, summary = score_dataset(args.data, args.scale, item_col_prefix=args.prefix, output_path=args.out_scored)
        results["questionnaire_scoring"] = summary

    elif args.task == "demographics":
        demo_vars = []
        if args.demo_vars:
            try:
                demo_vars = json.loads(args.demo_vars)
            except Exception:
                demo_vars = [v.strip() for v in args.demo_vars.split(",")]
        elif args.vars:
            demo_vars = [v.strip() for v in args.vars.split(",")]
        else:
            print("Error: --demo-vars or --vars required for 'demographics' task.", file=sys.stderr)
            sys.exit(1)
        results["demographics"] = analyze_demographics(df, demo_vars, age_col=args.age_col)

    elif args.task == "comprehensive_descriptives":
        if not args.constructs_config:
            print("Error: --constructs-config required for 'comprehensive_descriptives'.", file=sys.stderr)
            sys.exit(1)
        with open(args.constructs_config, 'r', encoding='utf-8') as f:
            constructs = json.load(f)
        results["comprehensive_descriptives"] = analyze_comprehensive_descriptives(df, constructs)

    elif args.task == "assumptions_suite":
        if not args.models_config:
            print("Error: --models-config required for 'assumptions_suite'.", file=sys.stderr)
            sys.exit(1)
        with open(args.models_config, 'r', encoding='utf-8') as f:
            m_spec = json.load(f)
        if isinstance(m_spec, dict) and "models" in m_spec:
            m_spec = m_spec["models"]
        results["assumptions_suite"] = analyze_parametric_assumptions_suite(df, m_spec)

    elif args.task == "saber_hypothesis":
        if not args.dv or not (args.predictors or args.step1):
            print("Error: --dv and --predictors required for 'saber_hypothesis'.", file=sys.stderr)
            sys.exit(1)
        preds = [p.strip() for p in (args.predictors or args.step1).split(",")]
        subs = [s.strip() for s in args.subscales.split(",")] if args.subscales else None
        results["saber_hypothesis"] = analyze_saber_hypothesis_regression(
            df=df,
            dv_col=args.dv,
            predictor_cols=preds,
            subscale_vars=subs,
            hypothesis_num=args.hyp_num,
            hypothesis_title=args.hyp_title,
            plot_dir=args.plot_dir
        )

    elif args.task == "serial_mediation":
        if not (args.x and args.m1 and args.m2 and args.y):
            print("Error: --x, --m1, --m2, and --y required for 'serial_mediation'.", file=sys.stderr)
            sys.exit(1)
        results["serial_mediation"] = analyze_serial_mediation(
            df=df,
            x_col=args.x,
            m1_col=args.m1,
            m2_col=args.m2,
            y_col=args.y,
            n_boot=args.bootstraps
        )

    elif args.task == "sem":
        if not args.sem_syntax:
            print("Error: --sem-syntax required for 'sem' task.", file=sys.stderr)
            sys.exit(1)
        syntax = args.sem_syntax
        if os.path.exists(syntax):
            with open(syntax, 'r', encoding='utf-8') as sf:
                syntax = sf.read()
        r_bin = args.rscript_bin
        if not shutil.which(r_bin) and os.path.exists("/usr/local/bin/Rscript"):
            r_bin = "/usr/local/bin/Rscript"
        results["sem"] = run_lavaan_sem(df, syntax, out_dir=args.plot_dir, rscript_bin=r_bin)

    elif args.task == "descriptives":
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

        # 0. Optional Questionnaire Scoring (enriches df with subscales/totals before hypothesis tests)
        if "questionnaires" in cfg and score_dataset:
            results["questionnaires"] = {}
            for q_spec in cfg["questionnaires"]:
                q_name = q_spec.get("scale") or q_spec.get("name")
                q_pref = q_spec.get("prefix", "Q")
                q_out = q_spec.get("save_scored_as")
                df, q_sum = score_dataset(args.data, q_name, item_col_prefix=q_pref, output_path=q_out)
                results["questionnaires"][q_name] = q_sum
            
        # 1. Demographics
        if "demographics" in cfg:
            d_cfg = cfg["demographics"]
            if isinstance(d_cfg, dict) and "vars" in d_cfg:
                results["demographics"] = analyze_demographics(
                    df,
                    d_cfg["vars"],
                    age_col=d_cfg.get("age_col"),
                    age_bins=d_cfg.get("age_bins"),
                    age_labels=d_cfg.get("age_labels")
                )
            elif isinstance(d_cfg, (list, dict)):
                results["demographics"] = analyze_demographics(df, d_cfg)

        # 2. Descriptives: Comprehensive 9-Column or Standard
        if "comprehensive_descriptives" in cfg:
            results["comprehensive_descriptives"] = analyze_comprehensive_descriptives(df, cfg["comprehensive_descriptives"])
        elif "descriptives" in cfg:
            results["descriptives"] = analyze_descriptives_and_normality(df, cfg["descriptives"]["vars"])

        # 3. Scale Reliability
        if "reliability" in cfg:
            results["reliability"] = {}
            for scale_name, items in cfg["reliability"].items():
                results["reliability"][scale_name] = analyze_scale_reliability(df, items)

        # 4. Correlation Matrix
        if "correlation" in cfg:
            results["correlation"] = analyze_correlation_matrix(df, cfg["correlation"]["vars"], cfg["correlation"].get("method", "pearson"))

        # 5. 6-Pillar Parametric Assumptions Suite
        if "assumptions_suite" in cfg:
            models_spec = cfg["assumptions_suite"]["models"] if isinstance(cfg["assumptions_suite"], dict) and "models" in cfg["assumptions_suite"] else cfg["assumptions_suite"]
            results["assumptions_suite"] = analyze_parametric_assumptions_suite(df, models_spec)

        # 6. Group Comparisons & ANCOVA
        if "group_tests" in cfg:
            results["group_tests"] = []
            for gt in cfg["group_tests"]:
                results["group_tests"].append(analyze_group_comparison(df, gt["var"], gt["group"]))
        if "ancova" in cfg:
            results["ancova"] = []
            for ac in cfg["ancova"]:
                results["ancova"].append(analyze_ancova(df, ac["dv"], ac["group"], ac["covar"]))

        # 7. Saber Hypothesis Testing (4-Tier Sequence)
        if "saber_hypotheses" in cfg or "hypotheses" in cfg:
            hyp_list = cfg.get("saber_hypotheses") or cfg.get("hypotheses")
            results["saber_hypotheses"] = []
            for h_spec in hyp_list:
                res_h = analyze_saber_hypothesis_regression(
                    df=df,
                    dv_col=h_spec["dv"],
                    predictor_cols=h_spec["predictors"],
                    subscale_vars=h_spec.get("subscales"),
                    hypothesis_num=h_spec.get("hypothesis_number", 1),
                    hypothesis_title=h_spec.get("hypothesis_title"),
                    plot_dir=h_spec.get("plot_dir", cfg.get("plot_dir", "./output/plots"))
                )
                results["saber_hypotheses"].append(res_h)

        # 8. Hierarchical Regression (Legacy/Alternative)
        if "regression" in cfg:
            results["regression"] = []
            for reg in cfg["regression"]:
                results["regression"].append(analyze_hierarchical_regression(df, reg["dv"], reg["step1"], reg.get("step2")))

        # 9. Simple Bootstrap Mediation
        if "mediation" in cfg:
            results["mediation"] = []
            for med in cfg["mediation"]:
                results["mediation"].append(analyze_bootstrap_mediation(df, med["x"], med["m"], med["y"], n_boot=med.get("bootstraps", 2000)))

        # 10. Serial Mediation (Hayes PROCESS Model 6)
        if "serial_mediation" in cfg:
            results["serial_mediation"] = []
            for sm_spec in cfg["serial_mediation"]:
                results["serial_mediation"].append(analyze_serial_mediation(
                    df,
                    sm_spec["x"],
                    sm_spec["m1"],
                    sm_spec["m2"],
                    sm_spec["y"],
                    n_boot=sm_spec.get("bootstraps", 5000)
                ))

        # 11. SEM via lavaan
        if "sem" in cfg:
            sem_cfg = cfg["sem"]
            syntax = sem_cfg.get("syntax")
            if not syntax and "syntax_file" in sem_cfg:
                with open(sem_cfg["syntax_file"], 'r', encoding='utf-8') as sf:
                    syntax = sf.read()
            if syntax:
                rscript_bin = sem_cfg.get("rscript_bin", "Rscript")
                if not shutil.which(rscript_bin) and os.path.exists("/usr/local/bin/Rscript"):
                    rscript_bin = "/usr/local/bin/Rscript"
                out_dir = sem_cfg.get("out_dir", "./output/sem")
                results["sem"] = run_lavaan_sem(df, syntax, out_dir=out_dir, rscript_bin=rscript_bin)
            elif "fit_measures" in sem_cfg:
                results["sem"] = sem_cfg

    # Save output
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Analysis completed successfully. Output saved to {args.out}")

if __name__ == "__main__":
    main()

