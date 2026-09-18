#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/script_execution_guard.py — Universal Execution Guard for Standalone Statistical Scripts

Enforces P0 data safety and contract integrity across all standalone CLI statistical tools:
1. Mode Validation ('production', 'demo', 'test', 'dry_run')
2. Production Sample Data Blocking: Prevents sample/demo/synthetic data execution in production.
3. Dataset Provenance Verification: Computes cryptographic hashes and size.
4. AnalysisPlan Authorization Verification: If a plan is supplied, enforces status=='APPROVED'.
"""

import os
import sys
import json
import hashlib
from typing import Dict, Any, Optional

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


class ProductionSampleFallbackBlockedError(RuntimeError):
    """Raised when an attempt is made to process sample/synthetic data in production mode."""
    pass


class InvalidExecutionModeError(ValueError):
    """Raised when an unrecognized execution mode is provided."""
    pass


class UnauthorizedAnalysisPlanError(PermissionError):
    """Raised when an AnalysisPlan is not in APPROVED status."""
    pass


def compute_file_sha256(file_path: str) -> str:
    """Computes the SHA-256 hex digest of a physical file."""
    if not os.path.isfile(file_path):
        return ""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def is_sample_or_demo_data(file_path: str) -> bool:
    """Checks whether a dataset path indicates sample, demo, synthetic, or mock data."""
    if not file_path:
        return False
    norm = os.path.abspath(file_path).replace("\\", "/")
    filename = os.path.basename(norm).lower()

    # Path indicators
    if any(p in norm for p in ("/examples/", "/fixtures/", "/sample_data/", "/demo_data/")):
        return True

    # Filename indicators
    sample_prefixes = ("sample_", "demo_", "mock_", "dummy_", "fixture_", "synthetic_", "toy_")
    if any(filename.startswith(p) for p in sample_prefixes):
        return True
    if any(sub in filename for sub in ("_sample.", "_demo.", "_mock.", "_dummy.")):
        return True

    return False


def enforce_script_safety(
    dataset_path: str,
    mode: str = "production",
    plan_path: Optional[str] = None,
    require_approved_plan: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Validates dataset provenance and execution parameters before statistical computation.
    
    Args:
        dataset_path: Path to empirical dataset (.xlsx, .csv, .sav, .json).
        mode: Execution mode ('production', 'demo', 'test', 'dry_run').
        plan_path: Optional path to analysis_plan.json.

    Returns:
        Provenance dictionary with SHA-256, file size, and validated mode.

    Raises:
        InvalidExecutionModeError: If mode is not recognized.
        FileNotFoundError: If dataset does not exist.
        ProductionSampleFallbackBlockedError: If sample data is used in production.
        UnauthorizedAnalysisPlanError: If AnalysisPlan is not APPROVED.
    """
    valid_modes = {"production", "demo", "test", "dry_run"}
    norm_mode = (mode or "").strip().lower()
    if norm_mode not in valid_modes:
        raise InvalidExecutionModeError(
            f"Invalid execution mode '{mode}'. Must be one of: {sorted(valid_modes)}"
        )

    if not dataset_path or not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset path not found on disk: '{dataset_path}'")

    abs_dataset = os.path.abspath(dataset_path)

    # P0: Production Sample Data Blocking
    if norm_mode == "production" and is_sample_or_demo_data(abs_dataset):
        raise ProductionSampleFallbackBlockedError(
            f"CRITICAL SAFETY VIOLATION: Production execution attempted with sample/demo dataset '{abs_dataset}'. "
            f"Production mode strictly requires verified real empirical data on disk. Silent fallback is prohibited."
        )

    # P0: AnalysisPlan Authorization Gate
    if require_approved_plan is None:
        require_approved_plan = (norm_mode == "production")

    if require_approved_plan and not plan_path:
        raise UnauthorizedAnalysisPlanError(
            "CRITICAL SAFETY VIOLATION: Production execution strictly requires an approved AnalysisPlan (--plan). "
            "Bypassing the AnalysisPlan is prohibited in production mode."
        )

    if plan_path:
        if not os.path.exists(plan_path):
            raise FileNotFoundError(f"AnalysisPlan not found: '{plan_path}'")
        with open(plan_path, "r", encoding="utf-8") as pf:
            plan_data = json.load(pf)
        status = plan_data.get("status")
        if status != "APPROVED":
            raise UnauthorizedAnalysisPlanError(
                f"Unauthorized AnalysisPlan '{plan_data.get('plan_id', 'UNKNOWN')}': status is '{status}', "
                f"expected 'APPROVED'. Statistics agents may execute only approved plans."
            )

    return {
        "dataset_path": abs_dataset,
        "sha256": compute_file_sha256(abs_dataset),
        "file_size_bytes": os.path.getsize(abs_dataset),
        "execution_mode": norm_mode,
        "is_sample": is_sample_or_demo_data(abs_dataset),
        "plan_path": os.path.abspath(plan_path) if plan_path else None
    }
