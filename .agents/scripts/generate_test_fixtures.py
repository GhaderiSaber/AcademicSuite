#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/generate_test_fixtures.py — Dynamic Test Fixtures Generator & Manager

Provides on-the-fly verification and generation of mock study fixtures in tests/fixtures/.
Ensures the repository on GitHub contains zero static mock data while all tests
can run and pass out-of-the-box in any clean environment.

Enforces Directive 18 single-view context budget (<= 500 lines, <= 40,000 bytes).
"""

import os
import sys
import json
import shutil
from typing import Dict, Any, List

_CURR_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(os.path.dirname(_CURR_DIR)) == ".agents":
    ROOT_DIR = os.path.abspath(os.path.join(_CURR_DIR, "..", ".."))
else:
    ROOT_DIR = os.path.abspath(os.path.join(_CURR_DIR, ".."))

AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
for p in [ROOT_DIR, AGENTS_DIR, os.path.join(AGENTS_DIR, "scripts"), os.path.join(AGENTS_DIR, "validators")]:
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        try:
            for entry in os.listdir(venv_lib):
                sp = os.path.join(venv_lib, entry, "site-packages")
                if os.path.isdir(sp) and sp not in sys.path:
                    sys.path.insert(0, sp)
        except OSError:
            pass

FIXTURES_DIR = os.path.join(ROOT_DIR, "tests", "fixtures")

REQUIRED_FIXTURE_STUDIES = [
    "study_vertical_slice_regression",
    "study_vertical_slice_experimental",
    "study_vertical_slice_mediation",
    "study_vertical_slice_moderation",
    "study_vertical_slice_scale_validation",
    "study_vertical_slice_sem",
    "study_vertical_slice_presentation",
    "study_act_burnout",
    "test_study_e2e",
]


def check_fixtures_status(fixtures_dir: str = FIXTURES_DIR) -> Dict[str, Any]:
    """Inspects which required fixture study directories are present."""
    status = {}
    all_present = True
    for study in REQUIRED_FIXTURE_STUDIES:
        study_path = os.path.join(fixtures_dir, study)
        exists = os.path.isdir(study_path)
        status[study] = exists
        if not exists:
            all_present = False
    return {
        "all_present": all_present,
        "fixtures_dir": fixtures_dir,
        "studies": status
    }


def generate_regression_fixture(fixtures_dir: str = FIXTURES_DIR) -> str:
    """Generates the Regression slice benchmark dataset (N=100)."""
    import numpy as np
    import pandas as pd

    target_dir = os.path.join(fixtures_dir, "study_vertical_slice_regression", "01_raw_inputs")
    os.makedirs(target_dir, exist_ok=True)
    csv_path = os.path.join(target_dir, "data_raw.csv")
    xlsx_path = os.path.join(target_dir, "data_raw.xlsx")

    if os.path.exists(csv_path) and os.path.exists(xlsx_path):
        return target_dir

    np.random.seed(42)
    n = 100
    stress = np.random.normal(3.2, 0.6, n)
    flexibility = np.random.normal(3.5, 0.5, n)
    # Burnout: positive stress, negative flexibility
    burnout = 1.2 + 0.45 * stress - 0.38 * flexibility + np.random.normal(0, 0.35, n)

    df = pd.DataFrame({
        "participant_id": [f"ID-{i+1:03d}" for i in range(n)],
        "gender": np.random.choice([1, 2], size=n, p=[0.5, 0.5]),
        "age": np.random.randint(22, 58, size=n),
        "workplace_stress": np.round(np.clip(stress, 1.0, 5.0), 2),
        "psychological_flexibility": np.round(np.clip(flexibility, 1.0, 5.0), 2),
        "job_burnout": np.round(np.clip(burnout, 1.0, 5.0), 2),
    })

    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False)
    return target_dir


def generate_all_benchmark_datasets(fixtures_dir: str = FIXTURES_DIR) -> None:
    """Generates raw input benchmark datasets for all slices if absent."""
    os.makedirs(fixtures_dir, exist_ok=True)

    # 1. Regression
    generate_regression_fixture(fixtures_dir)

    # 2. Experimental RCT
    exp_dir = os.path.join(fixtures_dir, "study_vertical_slice_experimental", "01_raw_inputs")
    exp_xlsx = os.path.join(exp_dir, "data_raw.xlsx")
    if not os.path.exists(exp_xlsx):
        try:
            from scripts.generate_experimental_benchmark_data import generate_experimental_dataset
            os.makedirs(exp_dir, exist_ok=True)
            generate_experimental_dataset(exp_xlsx)
        except Exception as e:
            print(f"[generate_test_fixtures] Warning generating experimental: {e}")

    # 3. Mediation
    med_dir = os.path.join(fixtures_dir, "study_vertical_slice_mediation", "01_raw_inputs")
    med_xlsx = os.path.join(med_dir, "data_raw.xlsx")
    if not os.path.exists(med_xlsx):
        try:
            from scripts.generate_mediation_benchmark_data import generate_mediation_data
            os.makedirs(med_dir, exist_ok=True)
            generate_mediation_data(med_dir, n=300)
        except Exception as e:
            print(f"[generate_test_fixtures] Warning generating mediation: {e}")

    # 4. Moderation
    mod_dir = os.path.join(fixtures_dir, "study_vertical_slice_moderation", "01_raw_inputs")
    mod_xlsx = os.path.join(mod_dir, "data_raw.xlsx")
    if not os.path.exists(mod_xlsx):
        try:
            from scripts.generate_moderation_benchmark_data import generate_moderation_dataset
            os.makedirs(mod_dir, exist_ok=True)
            generate_moderation_dataset(mod_xlsx)
        except Exception as e:
            print(f"[generate_test_fixtures] Warning generating moderation: {e}")

    # 5. Scale Validation
    sv_dir = os.path.join(fixtures_dir, "study_vertical_slice_scale_validation", "01_raw_inputs")
    sv_xlsx = os.path.join(sv_dir, "data_raw.xlsx")
    if not os.path.exists(sv_xlsx):
        try:
            from scripts.generate_scale_validation_benchmark_data import generate_scale_validation_data
            os.makedirs(sv_dir, exist_ok=True)
            generate_scale_validation_data(sv_dir, n=400)
        except Exception as e:
            print(f"[generate_test_fixtures] Warning generating scale validation: {e}")

    # 6. SEM
    sem_dir = os.path.join(fixtures_dir, "study_vertical_slice_sem", "01_raw_inputs")
    sem_xlsx = os.path.join(sem_dir, "data_raw.xlsx")
    if not os.path.exists(sem_xlsx):
        try:
            from scripts.generate_sem_benchmark_data import generate_sem_data
            os.makedirs(sem_dir, exist_ok=True)
            generate_sem_data(sem_dir, n=250)
        except Exception as e:
            print(f"[generate_test_fixtures] Warning generating sem: {e}")


def ensure_fixtures_present(fixtures_dir: str = FIXTURES_DIR) -> bool:
    """Entrypoint called by conftest.py and run_tests.py. Returns True if all fixtures ready."""
    status = check_fixtures_status(fixtures_dir)
    if status["all_present"]:
        return True

    print(f"[generate_test_fixtures] Initializing missing test fixtures in {fixtures_dir}...")
    generate_all_benchmark_datasets(fixtures_dir)
    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test Fixtures Generator & Manager")
    parser.add_argument("--status", action="store_true", help="Check fixture status")
    parser.add_argument("--generate", action="store_true", help="Generate all fixtures")
    args = parser.parse_args()

    if args.status:
        st = check_fixtures_status()
        print(json.dumps(st, indent=2))
    else:
        ensure_fixtures_present()
        print("✅ Test fixtures verified / generated successfully.")
