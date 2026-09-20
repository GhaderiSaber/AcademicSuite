#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_moderation_benchmark_data.py — Generates realistic benchmark dataset for Moderation (PROCESS Model 1)
and Conditional Process Analysis (PROCESS Model 7) in the Academic Suite.

Sample Size: N = 320
Instruments:
  1. Job Demands (dem_1 to dem_5) -> job_demands
  2. Psychological Capital (cap_1 to cap_5) -> psy_capital (Moderator)
  3. Emotional Exhaustion (exh_1 to exh_5) -> emotional_exhaustion (Mediator)
  4. Turnover Intention (turn_1 to turn_5) -> turnover_intention (Outcome)
Demographics: gender, age, education, tenure_years
Enforces Directive 9: Realistic bounded empirical decimal noise delta ~ Uniform(+-0.08, +-0.22).
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


def generate_moderation_dataset(output_xlsx, output_csv=None, n=320, seed=42):
    np.random.seed(seed)

    # 1. Demographics
    participant_ids = [f"P{i:03d}" for i in range(1, n + 1)]
    gender = np.random.choice([1, 2], size=n, p=[0.48, 0.52])  # 1=Male, 2=Female
    age = np.random.randint(23, 58, size=n)
    education = np.random.choice([1, 2, 3], size=n, p=[0.40, 0.45, 0.15])  # 1=BSc, 2=MSc, 3=PhD
    tenure_years = np.clip(np.round((age - 22) * np.random.uniform(0.3, 0.8)), 1, 30).astype(int)

    # 2. Latent continuous variables
    # X: Job Demands
    x_latent = np.random.normal(loc=3.25, scale=0.65, size=n)
    x_latent = np.clip(x_latent, 1.2, 4.8)

    # W: Psychological Capital (Moderator)
    w_latent = np.random.normal(loc=3.45, scale=0.60, size=n)
    w_latent = np.clip(w_latent, 1.2, 4.8)

    # Centered predictors
    x_c = x_latent - np.mean(x_latent)
    w_c = w_latent - np.mean(w_latent)
    interaction_term = x_c * w_c

    # M: Emotional Exhaustion (Model 1 Dependent Variable / Model 7 Mediator)
    # Buffering effect of PsyCap: Higher PsyCap dampens the harmful effect of Job Demands
    m_latent = 2.90 + 0.44 * x_c - 0.38 * w_c - 0.38 * interaction_term + np.random.normal(0, 0.38, size=n)
    m_latent = np.clip(m_latent, 1.2, 4.8)

    # Y: Turnover Intention (Model 7 Outcome Variable)
    y_latent = 1.80 + 0.42 * (m_latent - np.mean(m_latent)) + 0.22 * x_c + np.random.normal(0, 0.45, size=n)
    y_latent = np.clip(y_latent, 1.2, 4.8)

    # 3. Simulate discrete 5-point Likert items (1 to 5) for each scale
    def generate_items(latent_scores, num_items=5):
        items = []
        for i in range(num_items):
            noise = np.random.normal(0, 0.45, size=len(latent_scores))
            raw = np.round(latent_scores + noise)
            clamped = np.clip(raw, 1, 5).astype(int)
            items.append(clamped)
        return items

    dem_items = generate_items(x_latent, 5)
    cap_items = generate_items(w_latent, 5)
    exh_items = generate_items(m_latent, 5)
    turn_items = generate_items(y_latent, 5)

    # 4. Compute realistic composite scores with bounded empirical decimal noise (Directive 9)
    def make_composite(items, target_latent):
        mean_items = np.mean(items, axis=0)
        # Inject bounded empirical noise delta ~ Uniform(+-0.08, +-0.22)
        noise_sign = np.random.choice([-1, 1], size=len(target_latent))
        noise_mag = np.random.uniform(0.08, 0.22, size=len(target_latent))
        noisy_comp = np.round(mean_items + noise_sign * noise_mag * 0.25, 3)
        return np.clip(noisy_comp, 1.0, 5.0)

    job_demands_comp = make_composite(dem_items, x_latent)
    psy_capital_comp = make_composite(cap_items, w_latent)
    emotional_exh_comp = make_composite(exh_items, m_latent)
    turnover_intent_comp = make_composite(turn_items, y_latent)

    # Build DataFrame
    data_dict = {
        "participant_id": participant_ids,
        "gender": gender,
        "age": age,
        "education": education,
        "tenure_years": tenure_years,
    }

    for i in range(5):
        data_dict[f"dem_{i+1}"] = dem_items[i]
    for i in range(5):
        data_dict[f"cap_{i+1}"] = cap_items[i]
    for i in range(5):
        data_dict[f"exh_{i+1}"] = exh_items[i]
    for i in range(5):
        data_dict[f"turn_{i+1}"] = turn_items[i]

    data_dict["job_demands"] = job_demands_comp
    data_dict["psy_capital"] = psy_capital_comp
    data_dict["emotional_exhaustion"] = emotional_exh_comp
    data_dict["turnover_intention"] = turnover_intent_comp

    df = pd.DataFrame(data_dict)

    os.makedirs(os.path.dirname(os.path.abspath(output_xlsx)), exist_ok=True)
    df.to_excel(output_xlsx, index=False)
    print(f"Generated benchmark dataset with {len(df)} rows and {len(df.columns)} columns at {output_xlsx}")

    if output_csv:
        df.to_csv(output_csv, index=False)
        print(f"Exported CSV copy to {output_csv}")

    return df


if __name__ == "__main__":
    out_xlsx = os.path.join(ROOT_DIR, "projects", "study_vertical_slice_moderation", "01_raw_inputs", "data_raw.xlsx")
    out_csv = os.path.join(ROOT_DIR, "projects", "study_vertical_slice_moderation", "01_raw_inputs", "data_raw.csv")
    generate_moderation_dataset(out_xlsx, out_csv, n=320)
