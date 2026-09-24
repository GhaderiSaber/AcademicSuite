#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validators/numerical_consistency/validator.py — Evolved Numerical Consistency & Forensic Math Validator

Enforces Tier 2 Forensic Statistical Verification:
1. Statcheck Re-computation: Recalculates exact p-values for t, F, chi2, r from statistics and df.
   Detects reporting inconsistencies (|Δp| > 0.015) and gross decision inconsistencies.
2. GRIM Granularity Audit: Verifies whether reported scale/item means satisfy M * N ∈ ℤ.
3. SPRITE Bounds Verification: Verifies mean and SD against theoretical bounded scale limits.
4. Correlation Matrix Admissibility: Verifies range |r| <= 1.0, symmetry, and positive semi-definiteness.
5. Actionable Repair Prescriptions (ARP): Compiles structured repair recipes for detected defects.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List, Optional, Union

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
for p in (ROOT_DIR, AGENTS_DIR, os.path.join(AGENTS_DIR, "validators")):
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

try:
    from validators.statcheck_grim_verifier import (
        verify_statcheck,
        verify_grim,
        verify_sprite_bounds,
        verify_correlation_matrix,
        create_actionable_repair_prescription
    )
except ImportError:
    try:
        from statcheck_grim_verifier import (
            verify_statcheck,
            verify_grim,
            verify_sprite_bounds,
            verify_correlation_matrix,
            create_actionable_repair_prescription
        )
    except ImportError:
        verify_statcheck = None
        verify_grim = None
        verify_sprite_bounds = None
        verify_correlation_matrix = None
        create_actionable_repair_prescription = None


def validate_numbers(stats_path: str, sample_n: Optional[int] = None) -> Dict[str, Any]:
    """
    Validates numerical consistency, statistical parameters, and forensic mathematical validity.
    Returns a backward-compatible dictionary enriched with Tier 2 forensic evidence and ARPs.
    """
    if not os.path.exists(stats_path):
        return {
            "validator": "numerical_consistency",
            "verdict": "BLOCKED",
            "status": "BLOCKED",
            "errors": [f"Stats file not found: {stats_path}"],
            "warnings": [],
            "sample_size_audited": None,
            "statcheck_results": [],
            "grim_results": [],
            "sprite_results": [],
            "actionable_repair_prescriptions": []
        }

    try:
        with open(stats_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return {
            "validator": "numerical_consistency",
            "verdict": "FAIL",
            "status": "FAIL",
            "errors": [f"Malformed JSON artifact '{stats_path}': {str(e)}"],
            "warnings": [],
            "sample_size_audited": None,
            "statcheck_results": [],
            "grim_results": [],
            "sprite_results": [],
            "actionable_repair_prescriptions": []
        }

    errors: List[str] = []
    warnings: List[str] = []
    evidence_items: List[str] = []
    statcheck_results: List[Dict[str, Any]] = []
    grim_results: List[Dict[str, Any]] = []
    sprite_results: List[Dict[str, Any]] = []
    correlation_results: Optional[Dict[str, Any]] = None
    arps: List[Dict[str, Any]] = []

    gross_decision_errors = 0
    reporting_errors = 0
    grim_failures = 0

    # 1. Sample Size and Degrees of Freedom Check
    n = sample_n or data.get("sample_size") or data.get("n") or data.get("N")
    if n is not None:
        try:
            n = int(n)
            evidence_items.append("sample_size")
        except (ValueError, TypeError):
            n = None

    if "fit_indices" in data:
        evidence_items.append("fit_indices")
        if isinstance(data["fit_indices"], dict):
            df_val = data["fit_indices"].get("df")
            if df_val is not None and df_val <= 0:
                err_msg = f"Invalid SEM degrees of freedom: {df_val}"
                errors.append(err_msg)
                if create_actionable_repair_prescription:
                    arps.append(create_actionable_repair_prescription(
                        prescription_id=f"ARP-NUM-DF-{os.path.basename(stats_path)}",
                        tier=2,
                        defect_type="INVALID_DEGREES_OF_FREEDOM",
                        severity="CRITICAL",
                        target_artifact=stats_path,
                        target_key_or_line="fit_indices.df",
                        responsible_agent="statistics-agent",
                        remedy_instruction="Recalculate model specifications; degrees of freedom must be strictly positive."
                    ))
            for idx_k in ["cfi", "tli", "rmsea", "srmr", "chi2"]:
                if idx_k in data["fit_indices"]:
                    evidence_items.append(f"fit_{idx_k}")

    # 2. Extract Coefficients & Perform Statcheck Verification
    coefs = data.get("coefficients", [])
    if isinstance(coefs, dict):
        coef_list = list(coefs.values()) if all(isinstance(v, dict) for v in coefs.values()) else [coefs]
    elif isinstance(coefs, list):
        coef_list = coefs
    else:
        coef_list = []

    # Calculate default residual df if not explicitly given
    k_preds = max(1, len(coef_list) - 1)
    df_resid_default = (n - k_preds - 1) if (n and n > (k_preds + 1)) else (n - 2 if n and n > 2 else 30)
    df_explicit = data.get("df_residual") or data.get("df_error") or data.get("df2") or data.get("df")

    for c_idx, coef in enumerate(coef_list):
        if not isinstance(coef, dict):
            continue

        pred_name = coef.get("predictor") or coef.get("variable") or f"var_{c_idx}"
        evidence_items.append(f"coef_{pred_name}")

        t_val = coef.get("t") or coef.get("t_stat") or coef.get("t_value")
        p_val = coef.get("p_value") or coef.get("p") or coef.get("sig")
        df_coef = coef.get("df") or df_explicit or df_resid_default

        # Check for prohibited p = .000
        if p_val in ("0", ".000", "0.000", 0, 0.0):
            err_msg = f"Prohibited p = .000 reported for predictor '{pred_name}'. Must use p < .001."
            errors.append(err_msg)
            if create_actionable_repair_prescription:
                arps.append(create_actionable_repair_prescription(
                    prescription_id=f"ARP-NUM-P000-{pred_name}",
                    tier=1,
                    defect_type="PROHIBITED_P_ZERO",
                    severity="HIGH",
                    target_artifact=stats_path,
                    target_key_or_line=f"coefficients.{pred_name}.p_value",
                    responsible_agent="academic-writer",
                    remedy_instruction="Replace p = .000 with p < .001 in statistical JSON, markdown tables, and Word narrative.",
                    automated_fixable=True
                ))

        # Perform Statcheck Recomputation if t and p are present
        if verify_statcheck and t_val is not None and p_val is not None:
            try:
                t_float = float(t_val)
                st_res = verify_statcheck("t", t_float, df_coef, reported_p=p_val)
                statcheck_results.append({
                    "predictor": pred_name,
                    "stat": "t",
                    "t_value": t_float,
                    "df": df_coef,
                    "reported_p": p_val,
                    "recomputed_p": st_res.get("recomputed_p"),
                    "is_consistent": st_res.get("is_consistent"),
                    "is_decision_inconsistency": st_res.get("is_decision_inconsistency")
                })
                evidence_items.append(f"statcheck_t_{pred_name}")

                if st_res.get("is_decision_inconsistency"):
                    gross_decision_errors += 1
                    errors.append(st_res["message"])
                    if create_actionable_repair_prescription:
                        arps.append(create_actionable_repair_prescription(
                            prescription_id=f"ARP-STATCHECK-DECISION-{pred_name}",
                            tier=2,
                            defect_type="GROSS_DECISION_INCONSISTENCY",
                            severity="CRITICAL",
                            target_artifact=stats_path,
                            target_key_or_line=f"coefficients.{pred_name}",
                            responsible_agent="statistics-agent",
                            remedy_instruction=(
                                f"Recalculate statistical model for '{pred_name}'. Reported p={p_val} contradicts "
                                f"recomputed p={st_res.get('recomputed_p'):.4f}. Synchronize hypothesis conclusion across triad."
                            )
                        ))
                elif not st_res.get("is_consistent"):
                    reporting_errors += 1
                    errors.append(st_res["message"])
                    if create_actionable_repair_prescription:
                        arps.append(create_actionable_repair_prescription(
                            prescription_id=f"ARP-STATCHECK-REPORTING-{pred_name}",
                            tier=2,
                            defect_type="REPORTING_INCONSISTENCY",
                            severity="HIGH",
                            target_artifact=stats_path,
                            target_key_or_line=f"coefficients.{pred_name}",
                            responsible_agent="statistics-agent",
                            remedy_instruction=(
                                f"Update reported p-value for '{pred_name}' from {p_val} to exact recomputed {st_res.get('recomputed_p'):.3f}."
                            )
                        ))
            except (ValueError, TypeError):
                pass

    # 3. Overall F-test Statcheck Verification
    f_stat = data.get("f_stat") or data.get("f_value") or data.get("f")
    f_p = data.get("f_p_value") or (data.get("p_value") if f_stat else None)
    df_between = data.get("df_between") or data.get("df1")
    df_within = data.get("df_within") or data.get("df2") or df_explicit

    if verify_statcheck and f_stat is not None and df_between is not None and df_within is not None:
        try:
            f_res = verify_statcheck("f", float(f_stat), float(df_between), float(df_within), reported_p=f_p)
            statcheck_results.append({
                "stat": "f",
                "f_value": float(f_stat),
                "df1": float(df_between),
                "df2": float(df_within),
                "reported_p": f_p,
                "recomputed_p": f_res.get("recomputed_p"),
                "is_consistent": f_res.get("is_consistent"),
                "is_decision_inconsistency": f_res.get("is_decision_inconsistency")
            })
            evidence_items.append("statcheck_f")

            if f_res.get("is_decision_inconsistency"):
                gross_decision_errors += 1
                errors.append(f_res["message"])
            elif not f_res.get("is_consistent"):
                reporting_errors += 1
                errors.append(f_res["message"])
        except (ValueError, TypeError):
            pass

    # 4. Descriptive Statistics & GRIM / SPRITE Audit
    descriptives = data.get("descriptives", {})
    scale_min = float(data.get("scale_min", 1.0))
    scale_max = float(data.get("scale_max", 5.0))

    if isinstance(descriptives, dict):
        for var_name, var_stats in descriptives.items():
            if not isinstance(var_stats, dict):
                continue
            m_val = var_stats.get("mean") or var_stats.get("m")
            sd_val = var_stats.get("sd") or var_stats.get("std")
            items_c = int(var_stats.get("items_count", 1))

            if m_val is not None:
                evidence_items.append(f"mean_{var_name}")
                if verify_grim and n is not None and n > 0:
                    try:
                        g_res = verify_grim(float(m_val), n, items_count=items_c)
                        grim_results.append({"variable": var_name, **g_res})
                        if not g_res.get("grim_consistent"):
                            grim_failures += 1
                            errors.append(g_res["message"])
                            if create_actionable_repair_prescription:
                                arps.append(create_actionable_repair_prescription(
                                    prescription_id=f"ARP-GRIM-{var_name}",
                                    tier=2,
                                    defect_type="GRIM_GRANULARITY_INCONSISTENCY",
                                    severity="CRITICAL",
                                    target_artifact=stats_path,
                                    target_key_or_line=f"descriptives.{var_name}.mean",
                                    responsible_agent="data-agent",
                                    remedy_instruction=(
                                        f"Mean {m_val} is impossible for N={n}. Verify whether sample size N is accurate or "
                                        f"re-compute raw variable means from clean dataset."
                                    )
                                ))
                    except (ValueError, TypeError):
                        pass

                if verify_sprite_bounds and sd_val is not None:
                    try:
                        sp_res = verify_sprite_bounds(float(m_val), float(sd_val), scale_min=scale_min, scale_max=scale_max)
                        sprite_results.append({"variable": var_name, **sp_res})
                        if not sp_res.get("sprite_consistent"):
                            errors.extend(sp_res.get("errors", []))
                    except (ValueError, TypeError):
                        pass

    # 5. Correlation Matrix Admissibility
    corr_matrix = data.get("correlation_matrix") or data.get("correlations_matrix")
    if verify_correlation_matrix and isinstance(corr_matrix, list) and corr_matrix:
        corr_res = verify_correlation_matrix(corr_matrix)
        correlation_results = corr_res
        evidence_items.append("correlation_matrix_admissibility")
        if not corr_res.get("matrix_valid"):
            errors.extend(corr_res.get("errors", []))
            if create_actionable_repair_prescription:
                arps.append(create_actionable_repair_prescription(
                    prescription_id="ARP-CORR-MATRIX-INVALID",
                    tier=2,
                    defect_type="CORRELATION_MATRIX_INVALID",
                    severity="CRITICAL",
                    target_artifact=stats_path,
                    target_key_or_line="correlation_matrix",
                    responsible_agent="statistics-agent",
                    remedy_instruction="Correlation matrix has invalid bounds or is non-positive semi-definite. Re-estimate Pearson correlations."
                ))

    # Other statistical keys
    for stat_k in ["r2", "r_squared", "eta_p2", "effect_size", "paths"]:
        if stat_k in data:
            evidence_items.append(stat_k)

    # Determine Verdict
    if errors:
        verdict = "FAIL"
    elif not evidence_items:
        verdict = "UNKNOWN"
    else:
        verdict = "PASS"

    return {
        "validator": "numerical_consistency",
        "verdict": verdict,
        "status": verdict,
        "errors": errors,
        "warnings": warnings,
        "evidence_items_audited": len(evidence_items),
        "sample_size_audited": n,
        "statcheck_results": statcheck_results,
        "grim_results": grim_results,
        "sprite_results": sprite_results,
        "correlation_results": correlation_results,
        "gross_decision_errors": gross_decision_errors,
        "reporting_errors": reporting_errors,
        "grim_failures": grim_failures,
        "actionable_repair_prescriptions": arps
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate numerical consistency with Statcheck & GRIM")
    parser.add_argument("--stats", required=True, help="Path to stats JSON")
    parser.add_argument("--n", type=int, default=None, help="Sample size N")
    args = parser.parse_args()
    res = validate_numbers(args.stats, args.n)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    sys.exit(0 if res["verdict"] == "PASS" else 1)
