#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validators/statcheck_grim_verifier.py — Pure Python Forensic Statistical & Granularity Verifier

Forensic Meta-Science Verification Suite:
1. Statcheck Re-computation: Recomputes p-values from test statistics (t, F, chi2, r, z)
   and degrees of freedom (df1, df2) via scipy.stats.
   Detects Reporting Inconsistencies (|Δp| > 0.01) and Gross Decision Inconsistencies
   (reported p <= .05 but recomputed p > .05, or vice-versa).
2. GRIM (Granularity-Related Inconsistency of Means) Test:
   Verifies whether reported means on discrete integer scales are mathematically
   possible for sample size N (Brown & Heathers, 2017).
3. SPRITE & Range Bounds Verification:
   Verifies that reported standard deviations and means on bounded Likert scales
   do not exceed maximum theoretical variance: Var_max = (max - M)(M - min).
4. Correlation Matrix Mathematical Admissibility:
   Verifies range |r| <= 1.0, symmetry, unit diagonal, and positive semi-definiteness
   (eigenvalues >= -ε).
5. Actionable Repair Prescription (ARP) Generation:
   Transforms statistical defects into structured repair recipes for responsible agents.
"""

import os
import sys
import math
from typing import Dict, Any, List, Optional, Tuple, Union

try:
    import scipy.stats as stats
except ImportError:
    stats = None

try:
    import numpy as np
except ImportError:
    np = None


def compute_recalculated_p(
    test_type: str,
    stat_value: float,
    df1: float,
    df2: Optional[float] = None
) -> Optional[float]:
    """
    Recomputes exact two-tailed (or distribution standard) p-value using scipy.stats.
    Returns None if scipy is unavailable or inputs are invalid.
    """
    if stats is None:
        return None

    try:
        norm_type = test_type.strip().lower()
        stat_val = float(stat_value)
        d1 = float(df1)

        if norm_type in ("t", "t_test", "t_stat"):
            if d1 <= 0:
                return None
            return float(stats.t.sf(abs(stat_val), df=d1) * 2.0)

        elif norm_type in ("f", "f_test", "f_stat", "anova", "ancova"):
            if d1 <= 0 or df2 is None or float(df2) <= 0:
                return None
            d2 = float(df2)
            if stat_val < 0:
                return None
            return float(stats.f.sf(stat_val, dfn=d1, dfd=d2))

        elif norm_type in ("chi2", "chisq", "chi_square", "x2"):
            if d1 <= 0 or stat_val < 0:
                return None
            return float(stats.chi2.sf(stat_val, df=d1))

        elif norm_type in ("r", "pearson_r", "spearman_rho", "correlation"):
            # d1 is sample size N, or df = N - 2
            n = d1 if d1 > 2 else d1 + 2
            df_corr = n - 2
            if df_corr <= 0 or abs(stat_val) >= 1.0:
                if abs(stat_val) == 1.0:
                    return 0.0
                return None
            # t = r * sqrt((N - 2) / (1 - r^2))
            t_equiv = stat_val * math.sqrt(df_corr / (1.0 - (stat_val ** 2)))
            return float(stats.t.sf(abs(t_equiv), df=df_corr) * 2.0)

        elif norm_type in ("z", "z_score"):
            return float(stats.norm.sf(abs(stat_val)) * 2.0)

        return None
    except Exception:
        return None


def verify_statcheck(
    test_type: str,
    stat_value: float,
    df1: float,
    df2: Optional[float] = None,
    reported_p: Optional[Union[float, str]] = None,
    alpha: float = 0.05,
    tolerance: float = 0.015
) -> Dict[str, Any]:
    """
    Forensic Statcheck consistency audit.
    Evaluates whether reported p-value agrees with recomputed p-value.
    Identifies REPORTING_ERROR vs GROSS_DECISION_ERROR.
    """
    recomputed_p = compute_recalculated_p(test_type, stat_value, df1, df2)

    rep_p_float: Optional[float] = None
    rep_p_operator: str = "="

    if reported_p is not None:
        if isinstance(reported_p, (int, float)):
            rep_p_float = float(reported_p)
        elif isinstance(reported_p, str):
            clean_p = reported_p.strip()
            if clean_p.startswith("<"):
                rep_p_operator = "<"
                clean_p = clean_p[1:].strip()
            elif clean_p.startswith(">"):
                rep_p_operator = ">"
                clean_p = clean_p[1:].strip()
            elif clean_p.startswith("="):
                clean_p = clean_p[1:].strip()

            try:
                rep_p_float = float(clean_p)
            except ValueError:
                rep_p_float = None

    if recomputed_p is None:
        return {
            "test_type": test_type,
            "stat_value": stat_value,
            "df1": df1,
            "df2": df2,
            "reported_p": reported_p,
            "recomputed_p": None,
            "verdict": "UNKNOWN",
            "is_consistent": False,
            "is_decision_inconsistency": False,
            "severity": "UNKNOWN",
            "message": "Could not recompute p-value (invalid inputs or missing scipy)."
        }

    if rep_p_float is None:
        return {
            "test_type": test_type,
            "stat_value": stat_value,
            "df1": df1,
            "df2": df2,
            "reported_p": None,
            "recomputed_p": round(recomputed_p, 4),
            "verdict": "UNVERIFIED",
            "is_consistent": True,
            "is_decision_inconsistency": False,
            "severity": "NONE",
            "message": f"Recomputed p = {recomputed_p:.4f} (no reported p provided to compare)."
        }

    # Evaluate consistency based on operator
    is_consistent = False
    discrepancy = abs(rep_p_float - recomputed_p)

    if rep_p_operator == "<":
        # e.g. p < .001 -> recomputed_p must be <= 0.001 + tolerance
        is_consistent = (recomputed_p <= rep_p_float + tolerance)
    elif rep_p_operator == ">":
        # e.g. p > .05 -> recomputed_p must be >= 0.05 - tolerance
        is_consistent = (recomputed_p >= rep_p_float - tolerance)
    else:
        # exact match within tolerance (standard rounding tolerance)
        is_consistent = (discrepancy <= tolerance)

    # Evaluate decision inconsistency (significance threshold crossing)
    # Decision error occurs if:
    # 1. Reported significant (<= alpha) but recomputed non-significant (> alpha + tolerance)
    # 2. Reported non-significant (> alpha) but recomputed significant (<= alpha - tolerance)
    reported_sig = (rep_p_float <= alpha) if rep_p_operator != ">" else False
    recomputed_sig = (recomputed_p <= alpha)

    is_decision_inconsistency = False
    if reported_sig != recomputed_sig and discrepancy > tolerance:
        is_decision_inconsistency = True

    severity = "NONE"
    verdict = "PASS"
    message = f"Statistical recomputation confirmed: stat={stat_value}, df=({df1}{f', {df2}' if df2 else ''}), recomputed p={recomputed_p:.4f} matches reported {reported_p}."

    if is_decision_inconsistency:
        severity = "CRITICAL"
        verdict = "FAIL"
        message = (
            f"GROSS DECISION INCONSISTENCY: Reported p {rep_p_operator} {rep_p_float:.3f} "
            f"({'SIGNIFICANT' if reported_sig else 'NON-SIGNIFICANT'}) contradicts "
            f"recomputed p = {recomputed_p:.4f} ({'SIGNIFICANT' if recomputed_sig else 'NON-SIGNIFICANT'}) "
            f"for {test_type}({df1}{f', {df2}' if df2 else ''}) = {stat_value}."
        )
    elif not is_consistent:
        severity = "REPORTING_ERROR"
        verdict = "FAIL"
        message = (
            f"REPORTING INCONSISTENCY: Reported p {rep_p_operator} {rep_p_float:.3f} "
            f"deviates from recomputed p = {recomputed_p:.4f} (|Δ| = {discrepancy:.4f} > {tolerance}) "
            f"for {test_type}({df1}{f', {df2}' if df2 else ''}) = {stat_value}."
        )

    return {
        "test_type": test_type,
        "stat_value": stat_value,
        "df1": df1,
        "df2": df2,
        "reported_p": reported_p,
        "reported_p_numeric": rep_p_float,
        "recomputed_p": round(recomputed_p, 4),
        "discrepancy": round(discrepancy, 4),
        "is_consistent": is_consistent,
        "is_decision_inconsistency": is_decision_inconsistency,
        "severity": severity,
        "verdict": verdict,
        "message": message
    }


def verify_grim(
    mean: float,
    n: int,
    items_count: int = 1,
    decimals: Optional[int] = None
) -> Dict[str, Any]:
    """
    GRIM (Granularity-Related Inconsistency of Means) Test.
    Verifies whether a reported mean on an integer Likert/item scale is mathematically possible.
    Reference: Brown & Heathers (2017).
    """
    if n <= 0 or items_count <= 0:
        return {
            "grim_consistent": False,
            "verdict": "BLOCKED",
            "message": f"Invalid sample size N={n} or items_count={items_count} for GRIM test."
        }

    # Determine decimal places if not supplied
    str_mean = str(mean)
    if decimals is None:
        if "." in str_mean:
            decimals = len(str_mean.split(".")[1])
        else:
            decimals = 2

    # Effective N is N * items_count (if items are summed then averaged)
    effective_n = n * items_count

    # The sum of integer points must be an integer S
    # S / effective_n rounds to mean
    # Tolerance for D decimal places is 0.5 * 10^-D + 1e-6
    tolerance = 0.5 * (10 ** (-decimals)) + 1e-6

    # Product of mean and effective_n
    prod = mean * effective_n
    nearest_int = round(prod)
    reconstructed_mean = nearest_int / effective_n
    diff = abs(reconstructed_mean - mean)

    is_consistent = (diff <= tolerance)

    lower_cand = math.floor(prod) / effective_n
    upper_cand = math.ceil(prod) / effective_n

    verdict = "PASS" if is_consistent else "FAIL"
    severity = "NONE" if is_consistent else "CRITICAL"
    message = (
        f"GRIM verified: Mean {mean:.{decimals}f} is mathematically possible for N={n} (effective N={effective_n})."
        if is_consistent else
        f"GRIM TEST FAILED: Mean {mean:.{decimals}f} is MATHEMATICALLY IMPOSSIBLE for N={n} (items={items_count}). "
        f"Nearest possible means are {lower_cand:.{decimals}f} (sum={math.floor(prod)}) and {upper_cand:.{decimals}f} (sum={math.ceil(prod)})."
    )

    return {
        "grim_consistent": is_consistent,
        "verdict": verdict,
        "severity": severity,
        "mean": mean,
        "n": n,
        "items_count": items_count,
        "effective_n": effective_n,
        "decimals": decimals,
        "discrepancy": round(diff, 6),
        "nearest_possible_means": [round(lower_cand, decimals), round(upper_cand, decimals)],
        "message": message
    }


def verify_sprite_bounds(
    mean: float,
    sd: float,
    scale_min: float = 1.0,
    scale_max: float = 5.0
) -> Dict[str, Any]:
    """
    SPRITE Boundary & Variance Verification.
    Verifies that mean lies within [scale_min, scale_max] and standard deviation
    does not exceed the theoretical maximum possible variance on a bounded scale.
    Var_max = (scale_max - M) * (M - scale_min).
    """
    errors = []
    warnings = []

    if mean < scale_min or mean > scale_max:
        errors.append(f"Mean {mean:.3f} is outside bounded scale range [{scale_min}, {scale_max}].")

    if sd < 0:
        errors.append(f"Standard deviation {sd:.3f} cannot be negative.")

    # Maximum variance on bounded interval [min, max] with given mean M
    max_variance = max(0.0, (scale_max - mean) * (mean - scale_min))
    max_sd = math.sqrt(max_variance)

    if sd > max_sd + 0.01:
        errors.append(
            f"Reported SD {sd:.3f} exceeds maximum theoretical SD {max_sd:.3f} "
            f"for Mean {mean:.3f} on scale [{scale_min}, {scale_max}]."
        )

    verdict = "FAIL" if errors else "PASS"
    severity = "CRITICAL" if errors else "NONE"

    return {
        "sprite_consistent": (len(errors) == 0),
        "verdict": verdict,
        "severity": severity,
        "mean": mean,
        "sd": sd,
        "scale_min": scale_min,
        "scale_max": scale_max,
        "max_possible_sd": round(max_sd, 4),
        "errors": errors,
        "warnings": warnings,
        "message": "SPRITE bounds verified." if not errors else "; ".join(errors)
    }


def verify_correlation_matrix(
    matrix: List[List[float]],
    labels: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Verifies correlation matrix mathematical admissibility:
    1. Range: |r_ij| <= 1.0
    2. Diagonal: r_ii == 1.0
    3. Symmetry: r_ij == r_ji
    4. Positive Semi-Definiteness: all eigenvalues >= -1e-4
    """
    errors = []
    warnings = []
    dim = len(matrix)

    if dim == 0:
        return {
            "matrix_valid": False,
            "verdict": "BLOCKED",
            "errors": ["Correlation matrix is empty."],
            "warnings": []
        }

    # Verify square dimensions
    for row_idx, row in enumerate(matrix):
        if len(row) != dim:
            errors.append(f"Row {row_idx} length {len(row)} does not match matrix dimension {dim}.")

    if errors:
        return {
            "matrix_valid": False,
            "verdict": "FAIL",
            "errors": errors,
            "warnings": []
        }

    # Verify unit diagonal and range
    for i in range(dim):
        diag_val = matrix[i][i]
        if abs(diag_val - 1.0) > 0.02:
            errors.append(f"Diagonal element at ({i},{i}) is {diag_val}, expected 1.0.")

        for j in range(i + 1, dim):
            r_ij = matrix[i][j]
            r_ji = matrix[j][i]

            if abs(r_ij) > 1.001:
                errors.append(f"Correlation at ({i},{j}) = {r_ij} exceeds absolute bounds [-1.0, 1.0].")

            if abs(r_ij - r_ji) > 0.02:
                errors.append(f"Asymmetric correlation matrix: r({i},{j})={r_ij} != r({j},{i})={r_ji}.")

    # Positive Semi-Definiteness check via eigenvalues
    is_psd = True
    min_eig = 1.0
    if np is not None and not errors:
        try:
            arr = np.array(matrix, dtype=float)
            eigvals = np.linalg.eigvalsh(arr)
            min_eig = float(np.min(eigvals))
            if min_eig < -1e-3:
                is_psd = False
                errors.append(
                    f"Correlation matrix is NOT positive semi-definite (minimum eigenvalue = {min_eig:.4f} < 0). "
                    f"Pairwise correlations are mathematically contradictory."
                )
        except Exception as ex:
            warnings.append(f"Could not compute matrix eigenvalues: {str(ex)}")

    verdict = "FAIL" if errors else "PASS"
    return {
        "matrix_valid": (len(errors) == 0),
        "verdict": verdict,
        "dimension": dim,
        "is_symmetric": not any("Asymmetric" in e for e in errors),
        "is_psd": is_psd,
        "min_eigenvalue": round(min_eig, 4),
        "errors": errors,
        "warnings": warnings,
        "message": "Correlation matrix mathematically admissible." if not errors else "; ".join(errors)
    }


def create_actionable_repair_prescription(
    prescription_id: str,
    tier: int,
    defect_type: str,
    severity: str,
    target_artifact: str,
    responsible_agent: str,
    remedy_instruction: str,
    target_key_or_line: Optional[str] = None,
    automated_fixable: bool = False,
    affected_downstream_stages: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Constructs a contract-compliant Actionable Repair Prescription (ARP) dictionary.
    """
    return {
        "prescription_id": prescription_id,
        "tier": tier,
        "defect_type": defect_type,
        "severity": severity,
        "target_artifact": target_artifact,
        "target_key_or_line": target_key_or_line,
        "responsible_agent": responsible_agent,
        "remedy_instruction": remedy_instruction,
        "automated_fixable": automated_fixable,
        "affected_downstream_stages": affected_downstream_stages or [],
        "status": "OPEN"
    }
