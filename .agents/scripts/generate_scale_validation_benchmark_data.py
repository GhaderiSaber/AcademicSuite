#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_scale_validation_benchmark_data.py — Benchmark Dataset Generator for Scale Validation

Generates realistic Likert responses (N=450, 20 items across 2 factors: Cyber-Aggression
and Cyber-Victimization) for the Persian CAV-S psychometric validation study.
Adheres to Directive 9 (bounded decimal noise on composites, discrete integers 1-5 on items).
"""

import os
import sys

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


def generate_benchmark_data(out_dir: str, n: int = 450, seed: int = 42):
    np.random.seed(seed)
    os.makedirs(out_dir, exist_ok=True)

    # 1. Latent factors generation (r = 0.42 between Aggression and Victimization)
    cov_matrix = np.array([
        [1.0, 0.42],
        [0.42, 1.0]
    ])
    latents = np.random.multivariate_normal(mean=[0, 0], cov=cov_matrix, size=n)
    eta_agg = latents[:, 0]
    eta_vic = latents[:, 1]

    # Target factor loadings (from sample payload)
    loadings_agg = [0.78, 0.82, 0.74, 0.68, 0.79, 0.71, 0.69, 0.65, 0.84, 0.77]
    loadings_vic = [0.81, 0.76, 0.67, 0.79, 0.72, 0.66, 0.80, 0.73, 0.83, 0.75]

    data = {}
    data["participant_id"] = np.arange(1, n + 1)
    # Balanced gender: 225 female (1), 225 male (2)
    gender = np.array([1] * (n // 2) + [2] * (n - n // 2))
    np.random.shuffle(gender)
    data["gender"] = gender
    data["age"] = np.random.randint(13, 19, size=n)

    # Factor 1 items: cav_1 to cav_10
    agg_items = []
    for i, lam in enumerate(loadings_agg):
        col_name = f"cav_{i+1}"
        err_var = 1.0 - lam**2
        continuous = lam * eta_agg + np.random.normal(0, np.sqrt(err_var), size=n)
        # Bounded empirical shift per Directive 9
        shift = np.random.uniform(-0.15, 0.15)
        continuous += shift
        # Map to discrete 1-5 Likert
        discrete = np.clip(np.round(2.0 + continuous * 0.85), 1, 5).astype(int)
        data[col_name] = discrete
        agg_items.append(col_name)

    # Factor 2 items: cav_11 to cav_20
    vic_items = []
    for i, lam in enumerate(loadings_vic):
        col_name = f"cav_{i+11}"
        err_var = 1.0 - lam**2
        continuous = lam * eta_vic + np.random.normal(0, np.sqrt(err_var), size=n)
        shift = np.random.uniform(-0.15, 0.15)
        continuous += shift
        discrete = np.clip(np.round(2.2 + continuous * 0.90), 1, 5).astype(int)
        data[col_name] = discrete
        vic_items.append(col_name)

    df = pd.DataFrame(data)

    # Composite scores
    df["aggression_total"] = df[agg_items].sum(axis=1)
    df["victimization_total"] = df[vic_items].sum(axis=1)
    df["scale_total"] = df["aggression_total"] + df["victimization_total"]

    # Retest score for first 60 participants (r ~ 0.88, ICC ~ 0.878)
    retest_scores = df["scale_total"].copy()
    noise = np.random.normal(0, 3.8, size=n)
    retest_scores = np.clip(np.round(retest_scores + noise), 20, 100).astype(int)
    # Mask out participants > 60
    retest_col = [retest_scores[i] if i < 60 else np.nan for i in range(n)]
    df["retest_total"] = retest_col

    # Gold standard clinical criterion (0 = non-clinical, 1 = clinical risk)
    # Calibrated so AUC ~ 0.87, optimal cut-off ~ 48.0
    prob_clinical = 1.0 / (1.0 + np.exp(-0.18 * (df["scale_total"] - 48.0)))
    df["clinical_criterion"] = (np.random.uniform(0, 1, size=n) < prob_clinical).astype(int)

    # Export to Excel and CSV
    xlsx_path = os.path.join(out_dir, "data_raw.xlsx")
    csv_path = os.path.join(out_dir, "data_raw.csv")
    df.to_excel(xlsx_path, index=False)
    df.to_csv(csv_path, index=False)

    print(f"Generated benchmark dataset: N={n}, 20 items, demographics, retest (n=60), clinical criterion.")
    print(f"Saved: {xlsx_path} and {csv_path}")
    print(f"Mean Scale Total: {df['scale_total'].mean():.2f} (SD={df['scale_total'].std():.2f})")
    print(f"Mean Aggression: {df['aggression_total'].mean():.2f}, Mean Victimization: {df['victimization_total'].mean():.2f}")
    return xlsx_path, csv_path


if __name__ == "__main__":
    out_directory = os.path.join(ROOT_DIR, "projects", "study_vertical_slice_scale_validation", "01_raw_inputs")
    generate_benchmark_data(out_directory, n=450)
