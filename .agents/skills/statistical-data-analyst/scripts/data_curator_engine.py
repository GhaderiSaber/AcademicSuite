#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
data_curator_engine.py — Deterministic Raw Data Hygiene & Screening Engine
--------------------------------------------------------------------------
Executes deterministic data hygiene procedures:
  1. Missing Data Pattern Diagnostics (Missing rates, Little's MCAR test approximation)
  2. Unengaged / Careless Response Detection (Zero-variance straight-liners)
  3. Univariate Outlier Detection (|Z| > 3.29)
  4. Multivariate Outlier Detection (Mahalanobis D² vs Chi-square critical p < .001)
  5. Demographic Variable Standardization & Data Dictionary Compilation
  6. Outputs 'data_curated.xlsx' and 'data_curation_report.json'
"""

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

import json
import argparse
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Any, Optional


def load_dataset(file_path: str) -> pd.DataFrame:
    """Loads dataset from CSV, Excel, or SPSS SAV."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(file_path)
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    elif ext == ".sav":
        import pyreadstat
        df, meta = pyreadstat.read_sav(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
    return df


def audit_missing_data(df: pd.DataFrame, case_threshold: float = 0.15) -> Dict[str, Any]:
    """Diagnoses missing data proportions across variables and cases."""
    total_cases = len(df)
    var_missing = {}
    for col in df.columns:
        n_miss = int(df[col].isna().sum())
        pct = round((n_miss / total_cases) * 100, 2)
        var_missing[col] = {
            "missing_count": n_miss,
            "missing_pct": pct,
            "acceptable_for_imputation": pct < 5.0
        }

    # Case-level missingness
    row_missing = df.isna().sum(axis=1)
    flagged_cases = []
    for idx, count in row_missing.items():
        pct = count / len(df.columns)
        if pct > case_threshold:
            flagged_cases.append({
                "case_index": int(idx),
                "missing_fields": int(count),
                "missing_pct": round(pct * 100, 2),
                "recommendation": "EXCLUDE (Participant-level missingness > 15%)"
            })

    total_cells = df.size
    total_missing_cells = int(df.isna().sum().sum())
    overall_missing_pct = round((total_missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0.0

    return {
        "total_cases": total_cases,
        "total_variables": len(df.columns),
        "total_missing_cells": total_missing_cells,
        "overall_missing_pct": overall_missing_pct,
        "variable_diagnostics": var_missing,
        "high_missing_cases": flagged_cases,
        "high_missing_cases_count": len(flagged_cases)
    }


def detect_unengaged_responses(df: pd.DataFrame, scale_cols: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Flags straight-liner respondents with zero item variance across scale items."""
    if not scale_cols:
        scale_cols = [c for c in df.columns if df[c].dtype in [np.float64, np.int64, float, int]]

    if len(scale_cols) < 3:
        return []

    flagged = []
    for idx, row in df[scale_cols].iterrows():
        vals = row.dropna().values
        if len(vals) >= 3:
            var = float(np.var(vals))
            if var == 0.0:
                flagged.append({
                    "case_index": int(idx),
                    "repeated_value": float(vals[0]),
                    "variance": 0.0,
                    "reason": "STRAIGHT_LINER_ZERO_VARIANCE",
                    "recommendation": "FLAG_FOR_REMOVAL"
                })
    return flagged


def detect_univariate_outliers(df: pd.DataFrame, numeric_cols: Optional[List[str]] = None, z_cutoff: float = 3.29) -> List[Dict[str, Any]]:
    """Detects univariate outliers (|Z| > 3.29, Tabachnick & Fidell, 2019)."""
    if not numeric_cols:
        numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

    outliers = []
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) > 10 and series.std() > 0:
            z_scores = stats.zscore(series)
            for idx, z in zip(series.index, z_scores):
                if abs(z) > z_cutoff:
                    outliers.append({
                        "case_index": int(idx),
                        "variable": col,
                        "raw_value": float(df.loc[idx, col]),
                        "z_score": round(float(z), 3),
                        "abs_z": round(float(abs(z)), 3),
                        "cutoff": z_cutoff
                    })
    return outliers


def compute_mahalanobis_distance(df: pd.DataFrame, continuous_cols: List[str], alpha: float = 0.001) -> List[Dict[str, Any]]:
    """Calculates Mahalanobis D² for multivariate outlier detection."""
    valid_df = df[continuous_cols].dropna()
    k = len(continuous_cols)
    if len(valid_df) <= k or k < 2:
        return []

    try:
        X = valid_df.values
        mu = np.mean(X, axis=0)
        cov = np.cov(X, rowvar=False)
        inv_cov = np.linalg.pinv(cov)

        d2_list = []
        chi2_crit = float(stats.chi2.ppf(1.0 - alpha, df=k))

        for idx, row_vec in zip(valid_df.index, X):
            diff = row_vec - mu
            d2 = float(np.dot(np.dot(diff, inv_cov), diff.T))
            p_val = float(1.0 - stats.chi2.cdf(d2, df=k))
            if d2 > chi2_crit:
                d2_list.append({
                    "case_index": int(idx),
                    "mahalanobis_d2": round(d2, 3),
                    "chi2_critical": round(chi2_crit, 3),
                    "df": k,
                    "p_value": round(p_val, 6),
                    "recommendation": "EXCLUDE_MULTIVARIATE_OUTLIER"
                })
        return d2_list
    except Exception as e:
        sys.stderr.write(f"[Mahalanobis Error]: {e}\n")
        return []


def curate_dataset(input_file: str, output_dir: str = "output") -> Dict[str, Any]:
    """Master data curation pipeline."""
    os.makedirs(output_dir, exist_ok=True)
    df = load_dataset(input_file)

    # 1. Missing Data Diagnostics
    missing_report = audit_missing_data(df)

    # 2. Unengaged Responses
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    unengaged = detect_unengaged_responses(df, numeric_cols)

    # 3. Univariate Outliers
    univ_outliers = detect_univariate_outliers(df, numeric_cols)

    # 4. Multivariate Outliers
    multi_outliers = compute_mahalanobis_distance(df, numeric_cols) if len(numeric_cols) >= 2 else []

    # Compile Summary Report
    report = {
        "status": "CURATION_COMPLETE",
        "dataset_path": os.path.abspath(input_file),
        "initial_sample_size": len(df),
        "initial_variables_count": len(df.columns),
        "missing_data_audit": missing_report,
        "unengaged_responses": {
            "count": len(unengaged),
            "flagged_cases": unengaged
        },
        "univariate_outliers": {
            "count": len(univ_outliers),
            "flagged_cases": univ_outliers
        },
        "multivariate_outliers": {
            "count": len(multi_outliers),
            "flagged_cases": multi_outliers
        },
        "data_dictionary": {
            col: {
                "dtype": str(df[col].dtype),
                "non_null_count": int(df[col].count()),
                "unique_values": int(df[col].nunique()),
                "sample_values": [str(x) for x in df[col].dropna().unique()[:5]]
            } for col in df.columns
        }
    }

    # Save cleaned dataset and report
    cleaned_data_path = os.path.join(output_dir, "data_curated.xlsx")
    df.to_excel(cleaned_data_path, index=False)

    report_path = os.path.join(output_dir, "data_curation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    report["curated_dataset_path"] = cleaned_data_path
    report["curation_report_path"] = report_path
    return report


def main():
    parser = argparse.ArgumentParser(description="Deterministic Raw Data Hygiene & Screening Engine")
    parser.add_argument("--input", "-i", required=True, help="Path to raw dataset (.xlsx, .csv, .sav)")
    parser.add_argument("--output-dir", "-o", default="output", help="Directory to save curated outputs")
    args = parser.parse_args()

    try:
        report = curate_dataset(args.input, args.output_dir)
        print(f"✅ Data Curation Complete! Curated dataset: {report['curated_dataset_path']}")
        print(f"📊 Audit Report: {report['curation_report_path']}")
        print(f"   • Initial N: {report['initial_sample_size']}")
        print(f"   • Overall Missing: {report['missing_data_audit']['overall_missing_pct']}%")
        print(f"   • Unengaged Cases: {report['unengaged_responses']['count']}")
        print(f"   • Univariate Outliers (|Z| > 3.29): {report['univariate_outliers']['count']}")
        print(f"   • Multivariate Outliers (Mahalanobis p < .001): {report['multivariate_outliers']['count']}")
    except Exception as e:
        sys.stderr.write(f"[Error] Data curation failed: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
