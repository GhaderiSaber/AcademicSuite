#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_experimental_benchmark_data.py — Generates realistic benchmark dataset for Randomized Controlled Trial
Pre-Post-Followup Repeated Measures and ANCOVA slice (N=60, 2 Groups x 3 Occasions).

Design:
  - Group 1: Experimental (ACT Intervention, n=30)
  - Group 2: Control (Waitlist, n=30)
  - Occasions: Pre-test, Post-test, 2-Month Follow-Up
Primary Outcome: Psychological Distress / Anxiety (anxiety_pre, anxiety_post, anxiety_followup)
Process Outcome: Psychological Inflexibility (inflex_pre, inflex_post, inflex_followup)
Enforces Directive 9: Realistic bounded empirical decimal noise, discrete Likert items (1-5), and baseline equivalence.
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


def generate_experimental_dataset(output_xlsx, output_csv=None, n_per_group=30, seed=42):
    np.random.seed(seed)
    n_total = n_per_group * 2

    # 1. Demographics
    participant_ids = [f"P{i:02d}" for i in range(1, n_total + 1)]
    group = np.array([1] * n_per_group + [2] * n_per_group)  # 1=Experimental (ACT), 2=Control
    gender = np.random.choice([1, 2], size=n_total, p=[0.45, 0.55])
    age = np.random.randint(22, 54, size=n_total)
    education = np.random.choice([1, 2, 3], size=n_total, p=[0.40, 0.45, 0.15])

    # 2. Correlated baseline trait levels for individuals
    # Baseline trait: mean 3.40, sd 0.50
    base_anx_trait = np.random.normal(3.40, 0.48, size=n_total)
    base_anx_trait = np.clip(base_anx_trait, 1.8, 4.8)

    base_inf_trait = np.random.normal(3.50, 0.50, size=n_total)
    base_inf_trait = np.clip(base_inf_trait, 1.8, 4.8)

    # 3. Trajectories across Pre, Post, Follow-up
    # Pre-test: Identical distribution across groups (baseline balance)
    anx_pre_latent = base_anx_trait + np.random.normal(0, 0.15, size=n_total)
    inf_pre_latent = base_inf_trait + np.random.normal(0, 0.15, size=n_total)

    # Post-test:
    # Experimental group (first 30): significant drop (effect ~ -1.25)
    # Control group (last 30): negligible fluctuation
    anx_post_latent = np.zeros(n_total)
    inf_post_latent = np.zeros(n_total)

    # ACT Group post
    anx_post_latent[:n_per_group] = (
        0.55 * anx_pre_latent[:n_per_group] + 0.35 + np.random.normal(0, 0.20, size=n_per_group)
    )  # Drops to ~2.15
    inf_post_latent[:n_per_group] = (
        0.50 * inf_pre_latent[:n_per_group] + 0.45 + np.random.normal(0, 0.20, size=n_per_group)
    )  # Drops to ~2.20

    # Control Group post
    anx_post_latent[n_per_group:] = (
        anx_pre_latent[n_per_group:] + np.random.normal(0.04, 0.18, size=n_per_group)
    )  # Remains ~3.42
    inf_post_latent[n_per_group:] = (
        inf_pre_latent[n_per_group:] + np.random.normal(0.02, 0.18, size=n_per_group)
    )  # Remains ~3.52

    # Follow-up (2-Month):
    # ACT Group: Maintenance of treatment gains (slight regression to mean +0.08)
    anx_fup_latent = np.zeros(n_total)
    inf_fup_latent = np.zeros(n_total)

    anx_fup_latent[:n_per_group] = (
        0.90 * anx_post_latent[:n_per_group] + 0.28 + np.random.normal(0, 0.18, size=n_per_group)
    )  # Stays ~2.22
    inf_fup_latent[:n_per_group] = (
        0.90 * inf_post_latent[:n_per_group] + 0.30 + np.random.normal(0, 0.18, size=n_per_group)
    )  # Stays ~2.28

    # Control Group follow-up:
    anx_fup_latent[n_per_group:] = (
        anx_pre_latent[n_per_group:] + np.random.normal(0.01, 0.20, size=n_per_group)
    )  # Stays ~3.40
    inf_fup_latent[n_per_group:] = (
        inf_pre_latent[n_per_group:] + np.random.normal(-0.02, 0.20, size=n_per_group)
    )  # Stays ~3.48

    # Clamp all continuous latents to valid 1-5 range
    for arr in [anx_pre_latent, anx_post_latent, anx_fup_latent, inf_pre_latent, inf_post_latent, inf_fup_latent]:
        np.clip(arr, 1.1, 4.9, out=arr)

    # 4. Generate discrete Likert items (1 to 5)
    def make_items(latent_scores, num_items=5):
        items = []
        for i in range(num_items):
            raw = np.round(latent_scores + np.random.normal(0, 0.40, size=len(latent_scores)))
            items.append(np.clip(raw, 1, 5).astype(int))
        return items

    anx_pre_items = make_items(anx_pre_latent, 5)
    anx_post_items = make_items(anx_post_latent, 5)
    anx_fup_items = make_items(anx_fup_latent, 5)

    inf_pre_items = make_items(inf_pre_latent, 5)
    inf_post_items = make_items(inf_post_latent, 5)
    inf_fup_items = make_items(inf_fup_latent, 5)

    # 5. Compute realistic composite scores with bounded empirical decimal noise (Directive 9)
    def make_composite(items, latent):
        mean_items = np.mean(items, axis=0)
        noise_sign = np.random.choice([-1, 1], size=len(latent))
        noise_mag = np.random.uniform(0.08, 0.20, size=len(latent))
        comp = np.round(mean_items + noise_sign * noise_mag * 0.25, 3)
        return np.clip(comp, 1.0, 5.0)

    anxiety_pre = make_composite(anx_pre_items, anx_pre_latent)
    anxiety_post = make_composite(anx_post_items, anx_post_latent)
    anxiety_followup = make_composite(anx_fup_items, anx_fup_latent)

    inflex_pre = make_composite(inf_pre_items, inf_pre_latent)
    inflex_post = make_composite(inf_post_items, inf_post_latent)
    inflex_followup = make_composite(inf_fup_items, inf_fup_latent)

    # Assemble DataFrame
    data_dict = {
        "participant_id": participant_ids,
        "group": group,
        "gender": gender,
        "age": age,
        "education": education,
    }

    # Add anxiety items
    for i in range(5):
        data_dict[f"anx_pre_{i+1}"] = anx_pre_items[i]
    for i in range(5):
        data_dict[f"anx_post_{i+1}"] = anx_post_items[i]
    for i in range(5):
        data_dict[f"anx_fup_{i+1}"] = anx_fup_items[i]

    # Add inflexibility items
    for i in range(5):
        data_dict[f"inf_pre_{i+1}"] = inf_pre_items[i]
    for i in range(5):
        data_dict[f"inf_post_{i+1}"] = inf_post_items[i]
    for i in range(5):
        data_dict[f"inf_fup_{i+1}"] = inf_fup_items[i]

    # Add composites
    data_dict["anxiety_pre"] = anxiety_pre
    data_dict["anxiety_post"] = anxiety_post
    data_dict["anxiety_followup"] = anxiety_followup

    data_dict["inflex_pre"] = inflex_pre
    data_dict["inflex_post"] = inflex_post
    data_dict["inflex_followup"] = inflex_followup

    df = pd.DataFrame(data_dict)

    os.makedirs(os.path.dirname(os.path.abspath(output_xlsx)), exist_ok=True)
    df.to_excel(output_xlsx, index=False)
    print(f"Generated experimental dataset with {len(df)} rows and {len(df.columns)} columns at {output_xlsx}")

    if output_csv:
        df.to_csv(output_csv, index=False)
        print(f"Exported CSV copy to {output_csv}")

    return df


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT_DIR, "tests", "fixtures", "study_vertical_slice_experimental", "01_raw_inputs")
    out_xlsx = os.path.join(out_dir, "data_raw.xlsx")
    out_csv = os.path.join(out_dir, "data_raw.csv")
    generate_experimental_dataset(out_xlsx, out_csv, n_per_group=30)
