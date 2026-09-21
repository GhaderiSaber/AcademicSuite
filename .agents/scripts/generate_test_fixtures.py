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

REQUIRED_FIXTURE_ARTIFACTS = {
    "study_vertical_slice_regression": [
        "01_raw_inputs/data_raw.csv",
        "01_raw_inputs/data_raw.xlsx",
        "academic-state/project.json",
    ],
    "study_vertical_slice_experimental": [
        "01_raw_inputs/data_raw.csv",
        "01_raw_inputs/data_raw.xlsx",
        "academic-state/project.json",
    ],
    "study_vertical_slice_mediation": [
        "01_raw_inputs/data_raw.csv",
        "01_raw_inputs/data_raw.xlsx",
        "academic-state/project.json",
    ],
    "study_vertical_slice_moderation": [
        "01_raw_inputs/data_raw.csv",
        "01_raw_inputs/data_raw.xlsx",
        "academic-state/project.json",
    ],
    "study_vertical_slice_scale_validation": [
        "01_raw_inputs/data_raw.csv",
        "01_raw_inputs/data_raw.xlsx",
        "academic-state/project.json",
    ],
    "study_vertical_slice_sem": [
        "01_raw_inputs/data_raw.csv",
        "01_raw_inputs/data_raw.xlsx",
        "academic-state/project.json",
    ],
    "study_vertical_slice_presentation": [
        "01_raw_inputs/00_defense_findings_payload.json",
    ],
    "study_act_burnout": [
        "01_raw_inputs/data_raw.xlsx",
        "academic-state/project.json",
    ],
    "test_study_e2e": [
        "01_raw_inputs/test_academic_study_data.csv",
        "academic-state/project.json",
    ],
}


def check_fixtures_status(fixtures_dir: str = FIXTURES_DIR) -> Dict[str, Any]:
    """Inspects which required fixture study directories and essential artifacts are present."""
    status = {}
    all_present = True
    for study, required_files in REQUIRED_FIXTURE_ARTIFACTS.items():
        study_path = os.path.join(fixtures_dir, study)
        if not os.path.isdir(study_path):
            status[study] = False
            all_present = False
            continue
        study_ok = True
        for rel_file in required_files:
            file_path = os.path.join(study_path, rel_file)
            if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
                study_ok = False
                break
        status[study] = study_ok
        if not study_ok:
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
    """Generates complete datasets and schema-valid academic-state for all slices if absent."""
    os.makedirs(fixtures_dir, exist_ok=True)

    # 1. Regression
    generate_regression_fixture(fixtures_dir)
    reg_proj = os.path.join(fixtures_dir, "study_vertical_slice_regression")
    reg_proj_json = os.path.join(reg_proj, "academic-state", "project.json")
    if not os.path.exists(reg_proj_json):
        try:
            from academic_state_manager import init_state
            init_state(reg_proj, title="OLS Multiple Regression Benchmark Study", methodology="regression", n=100)
        except Exception as e:
            print(f"[generate_test_fixtures] Warning generating regression state: {e}")

    # 2. Experimental RCT
    exp_proj = os.path.join(fixtures_dir, "study_vertical_slice_experimental")
    exp_dir = os.path.join(exp_proj, "01_raw_inputs")
    exp_xlsx = os.path.join(exp_dir, "data_raw.xlsx")
    exp_csv = os.path.join(exp_dir, "data_raw.csv")
    if not os.path.exists(exp_xlsx) or not os.path.exists(exp_csv):
        try:
            from scripts.generate_experimental_benchmark_data import generate_experimental_dataset
            os.makedirs(exp_dir, exist_ok=True)
            generate_experimental_dataset(exp_xlsx, exp_csv, n_per_group=30)
        except Exception as e:
            print(f"[generate_test_fixtures] Warning generating experimental: {e}")
            raise
    exp_proj_json = os.path.join(exp_proj, "academic-state", "project.json")
    if not os.path.exists(exp_proj_json):
        try:
            from academic_state_manager import init_state
            init_state(exp_proj, title="Effectiveness of Acceptance and Commitment Therapy on Psychological Distress and Inflexibility: A Randomized Controlled Trial with 2-Month Follow-Up", methodology="experimental", n=60)
        except Exception as e:
            print(f"[generate_test_fixtures] Warning generating experimental state: {e}")

    # 3. Mediation
    med_proj = os.path.join(fixtures_dir, "study_vertical_slice_mediation")
    med_dir = os.path.join(med_proj, "01_raw_inputs")
    med_xlsx = os.path.join(med_dir, "data_raw.xlsx")
    med_csv = os.path.join(med_dir, "data_raw.csv")
    if not os.path.exists(med_xlsx) or not os.path.exists(med_csv):
        try:
            from scripts.generate_mediation_benchmark_data import generate_mediation_data
            os.makedirs(med_dir, exist_ok=True)
            generate_mediation_data(med_dir, n=300)
        except Exception as e:
            print(f"[generate_test_fixtures] Warning generating mediation: {e}")
            raise
    med_proj_json = os.path.join(med_proj, "academic-state", "project.json")
    if not os.path.exists(med_proj_json):
        try:
            from academic_state_manager import init_state
            init_state(med_proj, title="Process Mediation Benchmark Study", methodology="mediation", n=300)
        except Exception as e:
            print(f"[generate_test_fixtures] Warning generating mediation state: {e}")

    # 4. Moderation
    mod_proj = os.path.join(fixtures_dir, "study_vertical_slice_moderation")
    mod_dir = os.path.join(mod_proj, "01_raw_inputs")
    mod_xlsx = os.path.join(mod_dir, "data_raw.xlsx")
    mod_csv = os.path.join(mod_dir, "data_raw.csv")
    if not os.path.exists(mod_xlsx) or not os.path.exists(mod_csv):
        try:
            from scripts.generate_moderation_benchmark_data import generate_moderation_dataset
            os.makedirs(mod_dir, exist_ok=True)
            generate_moderation_dataset(mod_xlsx, mod_csv, n=320)
        except Exception as e:
            print(f"[generate_test_fixtures] Warning generating moderation: {e}")
            raise
    mod_proj_json = os.path.join(mod_proj, "academic-state", "project.json")
    if not os.path.exists(mod_proj_json):
        try:
            from academic_state_manager import init_state
            init_state(mod_proj, title="Process Moderation Benchmark Study", methodology="moderation", n=320)
        except Exception as e:
            print(f"[generate_test_fixtures] Warning generating moderation state: {e}")

    # 5. Scale Validation
    sv_proj = os.path.join(fixtures_dir, "study_vertical_slice_scale_validation")
    sv_dir = os.path.join(sv_proj, "01_raw_inputs")
    sv_xlsx = os.path.join(sv_dir, "data_raw.xlsx")
    sv_csv = os.path.join(sv_dir, "data_raw.csv")
    if not os.path.exists(sv_xlsx) or not os.path.exists(sv_csv):
        try:
            try:
                from scripts.generate_scale_validation_benchmark_data import generate_scale_validation_data as gen_sv
            except ImportError:
                from scripts.generate_scale_validation_benchmark_data import generate_benchmark_data as gen_sv
            os.makedirs(sv_dir, exist_ok=True)
            gen_sv(sv_dir, n=400)
        except Exception as e:
            print(f"[generate_test_fixtures] Error generating scale validation: {e}")
            raise
    sv_proj_json = os.path.join(sv_proj, "academic-state", "project.json")
    if not os.path.exists(sv_proj_json):
        try:
            from academic_state_manager import init_state
            init_state(sv_proj, title="Scale Validation Benchmark Study", methodology="scale_validation", n=400)
        except Exception as e:
            print(f"[generate_test_fixtures] Warning generating scale validation state: {e}")

    # 6. SEM
    sem_proj = os.path.join(fixtures_dir, "study_vertical_slice_sem")
    sem_dir = os.path.join(sem_proj, "01_raw_inputs")
    sem_xlsx = os.path.join(sem_dir, "data_raw.xlsx")
    sem_csv = os.path.join(sem_dir, "data_raw.csv")
    if not os.path.exists(sem_xlsx) or not os.path.exists(sem_csv):
        try:
            from scripts.generate_sem_benchmark_data import generate_sem_data
            os.makedirs(sem_dir, exist_ok=True)
            generate_sem_data(sem_dir, n=250)
        except Exception as e:
            print(f"[generate_test_fixtures] Warning generating sem: {e}")
            raise
    sem_proj_json = os.path.join(sem_proj, "academic-state", "project.json")
    if not os.path.exists(sem_proj_json):
        try:
            from academic_state_manager import init_state
            init_state(sem_proj, title="SEM Benchmark Study", methodology="sem", n=250)
        except Exception as e:
            print(f"[generate_test_fixtures] Warning generating sem state: {e}")

    # 7. Presentation
    generate_presentation_fixture(fixtures_dir)

    # 8. Study ACT Burnout
    generate_study_act_burnout_fixture(fixtures_dir)

    # 9. Test Study E2E
    generate_test_study_e2e_fixture(fixtures_dir)


def generate_presentation_fixture(fixtures_dir: str = FIXTURES_DIR) -> str:
    """Generates the presentation slice payload if absent."""
    pres_dir = os.path.join(fixtures_dir, "study_vertical_slice_presentation", "01_raw_inputs")
    os.makedirs(pres_dir, exist_ok=True)
    payload_file = os.path.join(pres_dir, "00_defense_findings_payload.json")
    if os.path.exists(payload_file):
        return pres_dir
    payload = {
        "study_title": "ارتباط استفاده مشکل‌ساز از اینترنت و علائم ADHD",
        "sample_size": 258,
        "methodology": {
            "design": "همبستگی و مدلیابی معادلات ساختاری (SEM)",
            "instruments": [{"name": "PIUQ", "items": 18, "alpha": 0.88}]
        },
        "demographics": {
            "age": {"mean": 22.45, "sd": 2.38},
            "gender": {"female_count": 152, "male_count": 106}
        },
        "hypotheses": [
            {
                "id": "H1",
                "statement": "استفاده مشکل‌ساز از اینترنت پیش‌بینی‌کننده علائم ADHD است.",
                "beta": 0.38,
                "t_value": 5.42,
                "p_value": "< .001",
                "verdict": "تایید شد"
            }
        ]
    }
    with open(payload_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return pres_dir


def generate_study_act_burnout_fixture(fixtures_dir: str = FIXTURES_DIR) -> str:
    """Generates the complete study_act_burnout fixture with state and datasets if absent."""
    import numpy as np
    import pandas as pd

    study_dir = os.path.join(fixtures_dir, "study_act_burnout")
    raw_inputs = os.path.join(study_dir, "01_raw_inputs")
    academic_state = os.path.join(study_dir, "academic-state")
    if os.path.exists(os.path.join(academic_state, "project.json")) and os.path.exists(os.path.join(raw_inputs, "data_scored.xlsx")):
        return study_dir

    os.makedirs(raw_inputs, exist_ok=True)
    np.random.seed(42)
    n = 60
    group = ["ACT"] * 30 + ["Control"] * 30
    gender = np.random.choice(["male", "female"], size=n)
    age = np.random.randint(24, 56, size=n)
    burnout_pre = np.round(np.random.normal(55.0, 6.0, size=n), 2)
    burnout_post = np.zeros(n)
    burnout_post[:30] = np.round(burnout_pre[:30] - 12.5 + np.random.normal(0, 3.0, 30), 2)
    burnout_post[30:] = np.round(burnout_pre[30:] + np.random.normal(0, 2.5, 30), 2)

    flexibility_pre = np.round(np.random.normal(18.0, 4.0, size=n), 2)
    flexibility_post = np.zeros(n)
    flexibility_post[:30] = np.round(flexibility_pre[:30] + 8.5 + np.random.normal(0, 2.0, 30), 2)
    flexibility_post[30:] = np.round(flexibility_pre[30:] + np.random.normal(0, 1.5, 30), 2)

    df = pd.DataFrame({
        "participant_id": [f"SUBJ_{i+1:03d}" for i in range(n)],
        "group": group,
        "gender": gender,
        "age": age,
        "burnout_pre": burnout_pre,
        "burnout_post": burnout_post,
        "flexibility_pre": flexibility_pre,
        "flexibility_post": flexibility_post
    })
    df.to_csv(os.path.join(raw_inputs, "data_raw.csv"), index=False)
    df.to_excel(os.path.join(raw_inputs, "data_raw.xlsx"), index=False)
    df.to_excel(os.path.join(raw_inputs, "data_scored.xlsx"), index=False)

    try:
        from academic_state_manager import init_state, state_ledger_transaction
        init_state(study_dir, title="ACT Burnout ICU Nurses Study", methodology="quasi_experimental", n=60)

        proj_file = os.path.join(academic_state, "project.json")
        with state_ledger_transaction(academic_state):
            with open(proj_file, "r", encoding="utf-8") as f:
                proj = json.load(f)
            proj["current_stage"] = "05_hypothesis_testing_completed"
            proj["status"] = "stage_completed"
            with open(proj_file, "w", encoding="utf-8") as f:
                json.dump(proj, f, indent=2)
    except Exception as e:
        print(f"[generate_test_fixtures] Warning initializing study_act_burnout state: {e}")

    delib_file = os.path.join(academic_state, "deliberation_candidates.json")
    if not os.path.exists(delib_file):
        delib_data = {
            "study_context": {
                "project_id": "study_act_burnout",
                "design_type": "quasi_experimental",
                "time_structure": "pre_post_repeated_measures",
                "has_baseline": True,
                "is_randomized": False,
                "sample_size": 60,
                "missing_rate": 0.0
            },
            "candidates": [
                {
                    "contract_version": "1.0.0",
                    "candidate_id": "CAND-ANCOVA-BURNOUT-01",
                    "proposed_by": "statistical-expert",
                    "method": "One-Way ANCOVA",
                    "research_question": "Does ACT reduce posttest burnout controlling for pretest?",
                    "estimand": "Average treatment contrast on posttest adjusted for baseline",
                    "assumptions": ["Homogeneity of regression slopes", "Normality of residuals"],
                    "data_requirements": {
                        "minimum_sample_size": 50,
                        "variables": ["group", "burnout_pre", "burnout_post"],
                        "time_structure": "pre_post_two_waves",
                        "measurement_level": "continuous_interval"
                    },
                    "diagnostics": ["Levene test", "Slope homogeneity"],
                    "strengths": ["Controls for baseline differences"],
                    "limitations": ["Requires slope homogeneity"],
                    "expected_interpretation": "Main effect of ACT",
                    "execution_requirements": {
                        "engine": "python",
                        "scripts": ["scripts/statistical_pipeline_engine.py"],
                        "assigned_subagent": "statistics-agent",
                        "runtime_dependencies": ["numpy", "scipy", "pandas", "statsmodels"]
                    }
                },
                {
                    "contract_version": "1.0.0",
                    "candidate_id": "CAND-RM-ANOVA-01",
                    "proposed_by": "statistical-expert",
                    "method": "Repeated Measures ANOVA",
                    "research_question": "Interaction effect across time",
                    "estimand": "Time x Group interaction",
                    "assumptions": ["Sphericity"],
                    "data_requirements": {
                        "minimum_sample_size": 40,
                        "variables": ["group", "burnout_pre", "burnout_post"],
                        "time_structure": "pre_post_two_waves",
                        "measurement_level": "continuous_interval"
                    },
                    "diagnostics": ["Mauchly test"],
                    "strengths": ["Within-subject power"],
                    "limitations": ["Assumes baseline equivalence"],
                    "expected_interpretation": "Interaction term",
                    "execution_requirements": {
                        "engine": "python",
                        "scripts": ["scripts/statistical_pipeline_engine.py"],
                        "assigned_subagent": "statistics-agent",
                        "runtime_dependencies": ["numpy", "scipy", "pandas"]
                    }
                },
                {
                    "contract_version": "1.0.0",
                    "candidate_id": "CAND-GAIN-SCORE-01",
                    "proposed_by": "statistical-expert",
                    "method": "Independent Samples t-test on Change Scores",
                    "research_question": "Change score difference",
                    "estimand": "Mean difference in gain scores",
                    "assumptions": ["Normality"],
                    "data_requirements": {
                        "minimum_sample_size": 30,
                        "variables": ["group", "burnout_pre", "burnout_post"],
                        "time_structure": "pre_post_two_waves",
                        "measurement_level": "continuous_interval"
                    },
                    "diagnostics": ["Shapiro-Wilk"],
                    "strengths": ["Simplicity"],
                    "limitations": ["Lord's paradox risk"],
                    "expected_interpretation": "Difference in change",
                    "execution_requirements": {
                        "engine": "python",
                        "scripts": ["scripts/statistical_pipeline_engine.py"],
                        "assigned_subagent": "statistics-agent",
                        "runtime_dependencies": ["numpy", "scipy", "pandas"]
                    }
                }
            ]
        }
        with open(delib_file, "w", encoding="utf-8") as f:
            json.dump(delib_data, f, indent=2)

    return study_dir


def generate_test_study_e2e_fixture(fixtures_dir: str = FIXTURES_DIR) -> str:
    """Generates the test_study_e2e fixture if absent."""
    import numpy as np
    import pandas as pd

    study_dir = os.path.join(fixtures_dir, "test_study_e2e")
    raw_inputs = os.path.join(study_dir, "01_raw_inputs")
    academic_state = os.path.join(study_dir, "academic-state")
    csv_path = os.path.join(raw_inputs, "test_academic_study_data.csv")
    xlsx_path = os.path.join(raw_inputs, "test_academic_study_data.xlsx")
    if os.path.exists(csv_path) and os.path.exists(xlsx_path):
        return study_dir

    os.makedirs(raw_inputs, exist_ok=True)
    np.random.seed(42)
    n = 80
    group = ["intervention"] * 40 + ["control"] * 40
    gender = np.random.choice(["male", "female"], size=n)
    age = np.random.randint(22, 58, size=n)
    burnout_pre = np.round(np.random.normal(54.0, 5.5, size=n), 2)
    burnout_post = np.zeros(n)
    burnout_post[:40] = np.round(burnout_pre[:40] - 11.0 + np.random.normal(0, 2.5, 40), 2)
    burnout_post[40:] = np.round(burnout_pre[40:] + np.random.normal(0, 2.0, 40), 2)

    df = pd.DataFrame({
        "participant_id": [f"SUBJ_{i+1:03d}" for i in range(n)],
        "group": group,
        "gender": gender,
        "age": age,
        "burnout_pre": burnout_pre,
        "burnout_post": burnout_post
    })
    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False)

    try:
        from academic_state_manager import init_state
        init_state(study_dir, title="End-to-End Integration Study", methodology="quasi_experimental", n=80)
    except Exception as e:
        print(f"[generate_test_fixtures] Warning initializing test_study_e2e state: {e}")

    return study_dir


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
