#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/generate_academic_benchmark_corpus.py — Benchmark Corpus Generator

Generates 18 authoritative academic behavioral benchmark datasets and case specifications:
Complies with Directive 6 (English filenames), Directive 9 (empirical decimal noise),
and Directive 18 (modular context budget, <= 500 lines).
"""

import os
import sys
import csv
import math
import random
import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from evals.benchmarks.benchmark_definitions import CASE_DEFINITIONS

BENCHMARKS_DIR = os.path.join(ROOT_DIR, "evals", "benchmarks")
DATASETS_DIR = os.path.join(BENCHMARKS_DIR, "datasets")
CASES_DIR = os.path.join(BENCHMARKS_DIR, "cases")
CATALOG_PATH = os.path.join(BENCHMARKS_DIR, "benchmark_catalog.json")

os.makedirs(DATASETS_DIR, exist_ok=True)
os.makedirs(CASES_DIR, exist_ok=True)

random.seed(42)


def calc_sha256(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def inject_noise(val: float, min_delta: float = 0.08, max_delta: float = 0.25) -> float:
    sign = random.choice([-1.0, 1.0])
    delta = random.uniform(min_delta, max_delta) * sign
    return round(val + delta, 2)


def write_csv(path: str, headers: List[str], rows: List[List[Any]]) -> str:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    return path


def gen_data_cleaning() -> str:
    path = os.path.join(DATASETS_DIR, "bm_data_cleaning_survey.csv")
    headers = ["id"] + [f"resilience_item_{i}" for i in range(1, 11)]
    rows = []
    for i in range(80):
        row = [f"SUBJ_{i+1:03d}"] + [random.choice([1, 2, 3, 4, 5]) for _ in range(10)]
        rows.append(row)
    rows[3][2] = 6
    rows[12][5] = -1
    return write_csv(path, headers, rows)


def gen_missing_data() -> str:
    path = os.path.join(DATASETS_DIR, "bm_missing_data_panel.csv")
    headers = ["participant_id", "burnout", "stress", "social_support", "coping_skills", "depression"]
    rows = []
    for i in range(120):
        b = inject_noise(random.gauss(24.5, 4.0)) if random.random() > 0.08 else ""
        s = inject_noise(random.gauss(18.2, 3.5)) if random.random() > 0.08 else ""
        sup = inject_noise(random.gauss(32.0, 5.0)) if random.random() > 0.08 else ""
        c = inject_noise(random.gauss(15.4, 2.8)) if random.random() > 0.08 else ""
        d = inject_noise(random.gauss(21.0, 4.2)) if random.random() > 0.08 else ""
        rows.append([f"ID_{i+1:03d}", b, s, sup, c, d])
    return write_csv(path, headers, rows)


def gen_outliers() -> str:
    path = os.path.join(DATASETS_DIR, "bm_outlier_multivariate.csv")
    headers = ["case_id", "working_memory", "processing_speed", "executive_function", "inhibition"]
    rows = []
    for i in range(100):
        wm = inject_noise(random.gauss(50.0, 8.0))
        ps = inject_noise(random.gauss(50.0, 7.5))
        ef = inject_noise(random.gauss(50.0, 8.5))
        inh = inject_noise(random.gauss(50.0, 7.0))
        rows.append([f"CASE_{i+1:03d}", wm, ps, ef, inh])
    rows[4][1] = 92.5
    rows[14][3] = 82.0
    rows[14][4] = 18.0
    return write_csv(path, headers, rows)


def gen_normality() -> str:
    path = os.path.join(DATASETS_DIR, "bm_normality_distribution.csv")
    headers = ["subject_id", "life_satisfaction", "ptsd_symptoms", "generalized_anxiety"]
    rows = []
    for i in range(90):
        rows.append([
            f"SUB_{i+1:03d}",
            inject_noise(random.gauss(25.0, 3.5)),
            inject_noise(random.expovariate(1.0 / 3.0) + 10.0),
            inject_noise(random.gauss(20.0, 4.0))
        ])
    return write_csv(path, headers, rows)


def gen_reliability() -> str:
    path = os.path.join(DATASETS_DIR, "bm_reliability_scale.csv")
    headers = ["resp_id"] + [f"dep_item_{i}" for i in range(1, 9)]
    rows = []
    for i in range(150):
        latent = random.gauss(0, 1)
        items = [int(min(5, max(1, round(3.0 + 0.8 * latent + random.gauss(0, 0.6))))) for _ in range(7)]
        items.append(random.choice([1, 2, 3, 4, 5]))
        rows.append([f"R_{i+1:03d}"] + items)
    return write_csv(path, headers, rows)


def gen_cfa() -> str:
    path = os.path.join(DATASETS_DIR, "bm_cfa_measurement.csv")
    headers = ["participant"] + [f"cf_{i}" for i in range(1, 5)] + [f"er_{i}" for i in range(1, 5)]
    rows = []
    for i in range(220):
        f1 = random.gauss(0, 1)
        f2 = 0.55 * f1 + math.sqrt(1 - 0.55**2) * random.gauss(0, 1)
        cf_vals = [inject_noise(lam * f1 + random.gauss(0, 0.5) + 4.0) for lam in [0.78, 0.82, 0.74, 0.69]]
        er_vals = [inject_noise(lam * f2 + random.gauss(0, 0.5) + 3.8) for lam in [0.80, 0.75, 0.85, 0.71]]
        rows.append([f"P_{i+1:03d}"] + cf_vals + er_vals)
    return write_csv(path, headers, rows)


def gen_sem() -> str:
    path = os.path.join(DATASETS_DIR, "bm_sem_structural.csv")
    headers = ["id"] + [f"stress_ind_{i}" for i in range(1, 4)] + [f"sleep_ind_{i}" for i in range(1, 4)] + [f"burnout_ind_{i}" for i in range(1, 4)]
    rows = []
    for i in range(250):
        xi = random.gauss(0, 1)
        eta1 = 0.50 * xi + math.sqrt(1 - 0.50**2) * random.gauss(0, 1)
        eta2 = -0.35 * xi + 0.40 * eta1 + random.gauss(0, 0.6)
        s_vals = [inject_noise(0.75 * xi + random.gauss(0, 0.5) + 5.0) for _ in range(3)]
        sl_vals = [inject_noise(0.80 * eta1 + random.gauss(0, 0.5) + 4.5) for _ in range(3)]
        b_vals = [inject_noise(0.78 * eta2 + random.gauss(0, 0.5) + 4.0) for _ in range(3)]
        rows.append([f"ID_{i+1:03d}"] + s_vals + sl_vals + b_vals)
    return write_csv(path, headers, rows)


def gen_mediation() -> str:
    path = os.path.join(DATASETS_DIR, "bm_mediation_process.csv")
    headers = ["id", "mindfulness", "rumination", "anxiety"]
    rows = []
    for i in range(180):
        x = inject_noise(random.gauss(50.0, 8.0))
        m = inject_noise(30.0 - 0.42 * (x - 50.0) + random.gauss(0, 5.0))
        y = inject_noise(45.0 - 0.25 * (x - 50.0) + 0.38 * (m - 30.0) + random.gauss(0, 4.5))
        rows.append([f"SUB_{i+1:03d}", x, m, y])
    return write_csv(path, headers, rows)


def gen_moderation() -> str:
    path = os.path.join(DATASETS_DIR, "bm_moderation_interaction.csv")
    headers = ["id", "work_stress", "social_support", "job_turnover"]
    rows = []
    for i in range(160):
        stress = inject_noise(random.gauss(40.0, 7.5))
        support = inject_noise(random.gauss(35.0, 6.0))
        c_str = stress - 40.0
        c_sup = support - 35.0
        turn = inject_noise(25.0 + 0.45 * c_str - 0.35 * c_sup - 0.04 * (c_str * c_sup) + random.gauss(0, 4.0))
        rows.append([f"EMP_{i+1:03d}", stress, support, turn])
    return write_csv(path, headers, rows)


def gen_longitudinal() -> str:
    path = os.path.join(DATASETS_DIR, "bm_longitudinal_panel.csv")
    headers = ["id", "T1_predictor", "T1_mediator", "T1_outcome", "T2_predictor", "T2_mediator", "T2_outcome", "T3_predictor", "T3_mediator", "T3_outcome"]
    rows = []
    for i in range(140):
        t1_x = inject_noise(random.gauss(20, 3))
        t1_m = inject_noise(random.gauss(15, 2.5))
        t1_y = inject_noise(random.gauss(25, 4))
        t2_x = inject_noise(0.60 * t1_x + random.gauss(8, 2))
        t2_m = inject_noise(0.55 * t1_m + 0.30 * t1_x + random.gauss(5, 2))
        t2_y = inject_noise(0.50 * t1_y + 0.25 * t1_m + random.gauss(8, 2.5))
        t3_x = inject_noise(0.62 * t2_x + random.gauss(7, 2))
        t3_m = inject_noise(0.58 * t2_m + 0.28 * t2_x + random.gauss(5, 2))
        t3_y = inject_noise(0.52 * t2_y + 0.32 * t2_m + random.gauss(7, 2.5))
        rows.append([f"PANEL_{i+1:03d}", t1_x, t1_m, t1_y, t2_x, t2_m, t2_y, t3_x, t3_m, t3_y])
    return write_csv(path, headers, rows)


def gen_rct() -> str:
    path = os.path.join(DATASETS_DIR, "bm_rct_efficacy.csv")
    headers = ["patient_id", "treatment_group", "pre_depression", "post_depression", "attrition_status"]
    rows = []
    for i in range(100):
        grp = "Intervention" if i < 50 else "Control"
        pre = inject_noise(random.gauss(32.0, 5.0))
        delta = random.uniform(7.0, 11.0) if grp == "Intervention" else random.uniform(0.5, 2.5)
        post = inject_noise(pre - delta)
        att = "Dropped" if i in [46, 47, 48, 49, 95, 96, 97, 98, 99] else "Completed"
        rows.append([f"PAT_{i+1:03d}", grp, pre, post, att])
    return write_csv(path, headers, rows)


def gen_ancova() -> str:
    path = os.path.join(DATASETS_DIR, "bm_ancova_prepost.csv")
    headers = ["id", "condition", "pre_test", "post_test"]
    rows = []
    for i in range(80):
        cond = "Treatment" if i < 40 else "Control"
        pre = inject_noise(random.gauss(20.0, 3.5))
        eff = 5.2 if cond == "Treatment" else 0.8
        post = inject_noise(15.0 + 0.65 * pre + eff + random.gauss(0, 2.0))
        rows.append([f"S_{i+1:03d}", cond, pre, post])
    return write_csv(path, headers, rows)


def gen_rm_anova() -> str:
    path = os.path.join(DATASETS_DIR, "bm_rm_anova_multitime.csv")
    headers = ["subject_id", "Time_1", "Time_2", "Time_3", "Time_4"]
    rows = []
    for i in range(60):
        b = random.gauss(40.0, 6.0)
        t1 = inject_noise(b + random.gauss(0, 2.0))
        t2 = inject_noise(b + 4.5 + random.gauss(0, 3.5))
        t3 = inject_noise(b + 8.2 + random.gauss(0, 5.0))
        t4 = inject_noise(b + 11.0 + random.gauss(0, 6.5))
        rows.append([f"SUB_{i+1:03d}", t1, t2, t3, t4])
    return write_csv(path, headers, rows)


def gen_mixed_models() -> str:
    path = os.path.join(DATASETS_DIR, "bm_mixed_models_nested.csv")
    headers = ["patient_id", "time_point", "outcome"]
    rows = []
    for p in range(50):
        p_id = f"PATIENT_{p+1:03d}"
        inter = random.gauss(25.0, 4.0)
        slp = random.gauss(-1.8, 0.5)
        for t in range(4):
            val = inject_noise(inter + slp * t + random.gauss(0, 1.5))
            rows.append([p_id, t, val])
    return write_csv(path, headers, rows)


def gen_network_analysis() -> str:
    path = os.path.join(DATASETS_DIR, "bm_network_symptoms.csv")
    cols = ["intrusive_thoughts", "nightmares", "hypervigilance", "avoidance", "emotional_numbing", "sleep_disturbance", "irritability"]
    headers = ["id"] + cols
    rows = []
    for i in range(200):
        vals = [int(min(5, max(1, round(random.gauss(3.0, 1.0))))) for _ in range(7)]
        rows.append([f"PT_{i+1:03d}"] + vals)
    return write_csv(path, headers, rows)


def gen_power_analysis() -> str:
    path = os.path.join(DATASETS_DIR, "bm_power_analysis_specs.csv")
    headers = ["scenario_id", "test_family", "effect_size_d", "alpha", "power_target", "expected_attrition_rate", "allocation_ratio"]
    rows = []
    for i in range(1, 21):
        rows.append([f"POWER_SCENARIO_{i:02d}", "t_test_independent_two_tailed", 0.50, 0.05, 0.80, 0.15, 1.0])
    return write_csv(path, headers, rows)


def gen_results_writing() -> str:
    path = os.path.join(DATASETS_DIR, "bm_results_writing_input.csv")
    headers = ["hypothesis_id", "test_type", "f_statistic", "df_between", "df_error", "p_value", "partial_eta_sq", "adj_mean_tx", "adj_mean_ctrl"]
    rows = []
    for i in range(1, 21):
        rows.append([f"H{i}", "ANCOVA", 14.82, 1, 77, 0.0002, 0.161, 18.42, 27.65])
    return write_csv(path, headers, rows)


def gen_discussion_writing() -> str:
    path = os.path.join(DATASETS_DIR, "bm_discussion_writing_input.csv")
    headers = ["study_id", "h1_status", "h2_status", "theoretical_framework", "target_window", "sample_n"]
    rows = []
    for i in range(1, 21):
        rows.append([f"STUDY_{i:02d}", "Confirmed", "Not Confirmed", "Attentional Control Theory", "2021-2026", 120])
    return write_csv(path, headers, rows)


DATASET_FACTORIES = {
    "DATA_CLEANING": (gen_data_cleaning, 80, "bm_data_cleaning_survey.csv"),
    "MISSING_DATA": (gen_missing_data, 120, "bm_missing_data_panel.csv"),
    "OUTLIERS": (gen_outliers, 100, "bm_outlier_multivariate.csv"),
    "NORMALITY": (gen_normality, 90, "bm_normality_distribution.csv"),
    "RELIABILITY": (gen_reliability, 150, "bm_reliability_scale.csv"),
    "CFA": (gen_cfa, 220, "bm_cfa_measurement.csv"),
    "SEM": (gen_sem, 250, "bm_sem_structural.csv"),
    "MEDIATION": (gen_mediation, 180, "bm_mediation_process.csv"),
    "MODERATION": (gen_moderation, 160, "bm_moderation_interaction.csv"),
    "LONGITUDINAL": (gen_longitudinal, 140, "bm_longitudinal_panel.csv"),
    "RCT": (gen_rct, 100, "bm_rct_efficacy.csv"),
    "ANCOVA": (gen_ancova, 80, "bm_ancova_prepost.csv"),
    "RM_ANOVA": (gen_rm_anova, 60, "bm_rm_anova_multitime.csv"),
    "MIXED_MODELS": (gen_mixed_models, 200, "bm_mixed_models_nested.csv"),
    "NETWORK_ANALYSIS": (gen_network_analysis, 200, "bm_network_symptoms.csv"),
    "POWER_ANALYSIS": (gen_power_analysis, 20, "bm_power_analysis_specs.csv"),
    "RESULTS_WRITING": (gen_results_writing, 20, "bm_results_writing_input.csv"),
    "DISCUSSION_WRITING": (gen_discussion_writing, 20, "bm_discussion_writing_input.csv")
}


def build_benchmark_case(family: str, dataset_rel_path: str, sha256_hash: str, sample_n: int) -> Dict[str, Any]:
    spec = CASE_DEFINITIONS[family]
    c_id = f"BM-{family.replace('_', '-')}-001"
    now_iso = datetime.now(timezone.utc).isoformat()
    return {
        "contract_version": "1.0.0",
        "case_id": c_id,
        "family": family,
        "title": spec["title"],
        "description": f"Authoritative academic behavioral benchmark case for {family}.",
        "research_question": spec["rq"],
        "design": spec["design"],
        "dataset": {
            "path": dataset_rel_path,
            "sha256": sha256_hash,
            "format": "csv",
            "sample_size": sample_n
        },
        "must_do": spec["must_do"],
        "must_not_do": spec["must_not_do"],
        "required_evidence": spec["required_evidence"],
        "target_capability": spec["target_capability"],
        "difficulty": "L3_EXPERT_BENCHMARK",
        "metadata": {
            "family_id": family,
            "generated_by": "scripts/generate_academic_benchmark_corpus.py",
            "directive_9_noise_injected": True
        },
        "created_at": now_iso
    }


def main():
    print("=================================================================")
    print("Generating 18 Academic Behavioral Benchmark Datasets & Cases")
    print("=================================================================")
    catalog = {
        "catalog_version": "1.0.0",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_families": len(DATASET_FACTORIES),
        "families": {}
    }

    for family, (fn, sample_n, fname) in DATASET_FACTORIES.items():
        fpath = fn()
        sha256_hash = calc_sha256(fpath)
        rel_dataset_path = os.path.relpath(fpath, ROOT_DIR)
        case_id = f"BM-{family.replace('_', '-')}-001"
        case_data = build_benchmark_case(family, rel_dataset_path, sha256_hash, sample_n)

        case_fname = f"bm_{family.lower()}.json"
        case_fpath = os.path.join(CASES_DIR, case_fname)
        with open(case_fpath, "w", encoding="utf-8") as f:
            json.dump(case_data, f, indent=2, ensure_ascii=False)

        catalog["families"][family] = {
            "case_id": case_id,
            "case_file": os.path.relpath(case_fpath, ROOT_DIR),
            "dataset_path": rel_dataset_path,
            "dataset_sha256": sha256_hash,
            "sample_size": sample_n,
            "target_capability": case_data["target_capability"]
        }
        print(f"[{family:18s}] Case: {case_id} | Dataset: {fname} (SHA256: {sha256_hash[:8]}...)")

    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    print("=================================================================")
    print(f"Corpus generation complete. 18 datasets and cases registered in {CATALOG_PATH}")


if __name__ == "__main__":
    main()
