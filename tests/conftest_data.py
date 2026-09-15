# -*- coding: utf-8 -*-
"""
conftest_data.py — Shared Micro-Fixtures for Academic Suite Test Suite
"""

import numpy as np
import pandas as pd

def get_sample_two_group_df(seed=42):
    """
    Returns a controlled synthetic dataframe with 60 participants (30 control, 30 intervention):
    - group: 'control' or 'intervention'
    - pre_test: continuous covariate (M ~ 20, SD ~ 4)
    - post_test: continuous DV showing intervention effect (intervention M ~ 28, control M ~ 21)
    """
    np.random.seed(seed)
    n_per_group = 30
    
    pre_ctrl = np.random.normal(20.0, 3.5, n_per_group)
    post_ctrl = pre_ctrl * 0.6 + np.random.normal(9.0, 2.5, n_per_group)
    
    pre_int = np.random.normal(20.5, 3.5, n_per_group)
    # Intervention gains ~7 points
    post_int = pre_int * 0.6 + np.random.normal(16.0, 2.5, n_per_group)
    
    df = pd.DataFrame({
        "subject_id": [f"SUB_{i+1:03d}" for i in range(n_per_group * 2)],
        "group": ["control"] * n_per_group + ["intervention"] * n_per_group,
        "pre_test": np.concatenate([pre_ctrl, pre_int]),
        "post_test": np.concatenate([post_ctrl, post_int])
    })
    return df


def get_sample_scale_items_df(seed=42):
    """
    Returns a dataframe of 100 respondents with 5 correlated Likert items (1 to 5):
    Underlying single latent factor with known reliability alpha ~ 0.82.
    """
    np.random.seed(seed)
    n = 100
    latent = np.random.normal(0, 1, n)
    
    items = {}
    for i in range(1, 6):
        # Continuous item with factor loading 0.70
        cont = 0.70 * latent + np.random.normal(0, np.sqrt(1 - 0.70**2), n)
        # Scale to 1-5 Likert
        likert = np.clip(np.round(cont * 0.8 + 3.0), 1, 5).astype(int)
        items[f"item_{i}"] = likert
        
    return pd.DataFrame(items)


def get_authentic_msai_payload():
    """Returns an authentic, non-anomalous audit payload."""
    return {
        "tests": [
            {
                "test_id": "T01_ANCOVA",
                "test_name": "ANCOVA post-test comparison",
                "partial_eta_squared": 0.18,
                "cohen_d": 0.65,
                "p_value": 0.008
            }
        ],
        "descriptives": {
            "groups": [
                {"name": "control", "mean": 21.45, "sd": 4.12},
                {"name": "intervention", "mean": 27.80, "sd": 4.35}
            ],
            "skewness": [0.35, -0.22, 0.41],
            "kurtosis": [-0.15, 0.08, -0.32]
        },
        "reliability": {
            "cognitive_flexibility": 0.84,
            "emotional_regulation": 0.88
        },
        "narrative_discrepancies": []
    }


def get_anomalous_msai_payload():
    """Returns an anomalous audit payload triggering multiple MSAI signals."""
    return {
        "tests": [
            {
                "test_id": "T01_FABRICATED",
                "test_name": "Extreme effect comparison",
                "partial_eta_squared": 0.72,  # SIG_01: Astronomical effect (> .45)
                "cohen_d": 3.10,               # SIG_01: Cohen's d > 2.0
                "p_value": 0.000001
            }
        ],
        "descriptives": {
            "groups": [
                {"name": "control", "mean": 12.00, "sd": 0.60},       # SIG_02: Variance deflation SD/M < 0.08
                {"name": "intervention", "mean": 35.00, "sd": 0.75}    # SIG_03: Near-zero overlap
            ],
            "skewness": [0.001, -0.002, 0.003],  # SIG_06: Suspicious normality clustering |Skew| < 0.02
            "kurtosis": [0.001, 0.002, -0.001]
        },
        "reliability": {
            "suspicious_scale": 0.992  # SIG_04: Excessive reliability (alpha > 0.97)
        },
        "narrative_discrepancies": [
            "Narrative reports p = .014 while Table 4 reports p = .142."  # SIG_10: Narrative mismatch
        ]
    }
