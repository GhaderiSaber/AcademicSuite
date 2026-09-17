#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate realistic empirical benchmark dataset for Serial Mediation (PROCESS Model 6) slice (N=300).
Constructs:
  X: Transformational Leadership
  M1: Psychological Safety
  M2: Work Engagement
  Y: Innovative Work Behavior
Enforces Directive 9: Realistic bounded empirical decimal noise on composites, discrete integers on Likert items.
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

def generate_mediation_data(output_dir, n=300, seed=42):
    np.random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)
    
    # Latent true scores with serial structural pathways:
    # X -> M1 (a1 = 0.52)
    # X -> M2 (a2 = 0.28), M1 -> M2 (d21 = 0.44)
    # X -> Y (c' = 0.22), M1 -> Y (b1 = 0.26), M2 -> Y (b2 = 0.38)
    latent_x = np.random.normal(3.6, 0.65, n)
    latent_m1 = 0.52 * latent_x + np.random.normal(1.5, 0.48, n)
    latent_m2 = 0.28 * latent_x + 0.44 * latent_m1 + np.random.normal(0.9, 0.42, n)
    latent_y = 0.22 * latent_x + 0.26 * latent_m1 + 0.38 * latent_m2 + np.random.normal(0.6, 0.40, n)
    
    data = {
        "participant_id": [f"EMP-{i+1:03d}" for i in range(n)],
        "gender": np.random.choice([1, 2], size=n, p=[0.55, 0.45]),
        "age": np.random.randint(24, 60, size=n),
        "education": np.random.choice([1, 2, 3], size=n, p=[0.30, 0.55, 0.15]),
        "tenure_years": np.random.randint(1, 28, size=n)
    }
    
    # 5 items for X (Transformational Leadership)
    for i in range(1, 6):
        data[f"lead_{i}"] = np.clip(np.round(latent_x + np.random.normal(0, 0.52, n)), 1, 5).astype(int)
        
    # 5 items for M1 (Psychological Safety)
    for i in range(1, 6):
        data[f"safe_{i}"] = np.clip(np.round(latent_m1 + np.random.normal(0, 0.50, n)), 1, 5).astype(int)
        
    # 5 items for M2 (Work Engagement)
    for i in range(1, 6):
        data[f"eng_{i}"] = np.clip(np.round(latent_m2 + np.random.normal(0, 0.48, n)), 1, 5).astype(int)
        
    # 5 items for Y (Innovative Work Behavior)
    for i in range(1, 6):
        data[f"innov_{i}"] = np.clip(np.round(latent_y + np.random.normal(0, 0.48, n)), 1, 5).astype(int)
        
    df = pd.DataFrame(data)
    
    # Injected bounded empirical decimal noise on composite variables (Directive 9)
    lead_items = [f"lead_{i}" for i in range(1, 6)]
    safe_items = [f"safe_{i}" for i in range(1, 6)]
    eng_items = [f"eng_{i}" for i in range(1, 6)]
    innov_items = [f"innov_{i}" for i in range(1, 6)]
    
    noise_x = np.random.uniform(0.08, 0.22, n) * np.random.choice([-1, 1], n)
    noise_m1 = np.random.uniform(0.08, 0.22, n) * np.random.choice([-1, 1], n)
    noise_m2 = np.random.uniform(0.08, 0.22, n) * np.random.choice([-1, 1], n)
    noise_y = np.random.uniform(0.08, 0.22, n) * np.random.choice([-1, 1], n)
    
    df["trans_leadership"] = np.clip(np.round(df[lead_items].mean(axis=1) + noise_x, 2), 1.0, 5.0)
    df["psych_safety"] = np.clip(np.round(df[safe_items].mean(axis=1) + noise_m1, 2), 1.0, 5.0)
    df["work_engagement"] = np.clip(np.round(df[eng_items].mean(axis=1) + noise_m2, 2), 1.0, 5.0)
    df["innovative_behavior"] = np.clip(np.round(df[innov_items].mean(axis=1) + noise_y, 2), 1.0, 5.0)
    
    xlsx_path = os.path.join(output_dir, "data_raw.xlsx")
    csv_path = os.path.join(output_dir, "data_raw.csv")
    
    df.to_excel(xlsx_path, index=False)
    df.to_csv(csv_path, index=False)
    print(f"Generated {n} records. Saved to:\n  - {xlsx_path}\n  - {csv_path}")

if __name__ == "__main__":
    out = os.path.join(ROOT_DIR, "projects", "study_vertical_slice_mediation", "01_raw_inputs")
    generate_mediation_data(out)
