#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate realistic empirical benchmark dataset for SEM vertical slice (N=250).
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

def generate_sem_data(output_dir, n=250, seed=42):
    np.random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)
    
    # Latent true scores
    latent_mind = np.random.normal(3.5, 0.65, n)
    latent_flex = 0.52 * latent_mind + np.random.normal(1.6, 0.50, n)
    latent_well = 0.34 * latent_flex + 0.38 * latent_mind + np.random.normal(1.1, 0.45, n)
    
    data = {
        "participant_id": [f"SUB-{i+1:03d}" for i in range(n)],
        "gender": np.random.choice([1, 2], size=n, p=[0.48, 0.52]),
        "age": np.random.randint(23, 58, size=n),
        "education": np.random.choice([1, 2, 3], size=n, p=[0.35, 0.50, 0.15]),
        "tenure_years": np.random.randint(1, 25, size=n)
    }
    
    # 5 indicators for Workplace Mindfulness
    for i in range(1, 6):
        item_vals = np.clip(np.round(latent_mind + np.random.normal(0, 0.55, n)), 1, 5).astype(int)
        data[f"mind_{i}"] = item_vals
        
    # 5 indicators for Psychological Flexibility
    for i in range(1, 6):
        item_vals = np.clip(np.round(latent_flex + np.random.normal(0, 0.55, n)), 1, 5).astype(int)
        data[f"flex_{i}"] = item_vals
        
    # 5 indicators for Occupational Well-being
    for i in range(1, 6):
        item_vals = np.clip(np.round(latent_well + np.random.normal(0, 0.55, n)), 1, 5).astype(int)
        data[f"well_{i}"] = item_vals
        
    df = pd.DataFrame(data)
    
    # Composite scores with bounded empirical decimal noise (Directive 9)
    mind_items = [f"mind_{i}" for i in range(1, 6)]
    flex_items = [f"flex_{i}" for i in range(1, 6)]
    well_items = [f"well_{i}" for i in range(1, 6)]
    
    noise_mind = np.random.uniform(0.08, 0.22, n) * np.random.choice([-1, 1], n)
    noise_flex = np.random.uniform(0.08, 0.22, n) * np.random.choice([-1, 1], n)
    noise_well = np.random.uniform(0.08, 0.22, n) * np.random.choice([-1, 1], n)
    
    df["mindfulness"] = np.clip(np.round(df[mind_items].mean(axis=1) + noise_mind, 2), 1.0, 5.0)
    df["psychological_flexibility"] = np.clip(np.round(df[flex_items].mean(axis=1) + noise_flex, 2), 1.0, 5.0)
    df["occupational_wellbeing"] = np.clip(np.round(df[well_items].mean(axis=1) + noise_well, 2), 1.0, 5.0)
    
    xlsx_path = os.path.join(output_dir, "data_raw.xlsx")
    csv_path = os.path.join(output_dir, "data_raw.csv")
    
    df.to_excel(xlsx_path, index=False)
    df.to_csv(csv_path, index=False)
    print(f"Generated {n} records. Saved to:\n  - {xlsx_path}\n  - {csv_path}")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT_DIR, "tests", "fixtures", "study_vertical_slice_sem", "01_raw_inputs")
    generate_sem_data(out)
