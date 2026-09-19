#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validators/run_all_validators.py — Master Unified Fail-Closed Validator Engine

Executes deterministic validation on stage artifacts, enforcing authoritative milestone
and stage artifact manifests, cross-artifact consistency, schema conformance,
and a strict 4-tier status taxonomy: UNKNOWN (or UNVERIFIED) / BLOCKED / FAIL / PASS.

Validator Philosophy (Phase 9):
"UNVERIFIED unless every required condition passes"

Sequential Gate Cascade:
- Gate 0: Manifest Existence (No manifest -> UNVERIFIED)
- Gate 1: Manifest Schema Validity (Schema invalid -> FAIL)
- Gate 2: Artifact Existence, Non-Empty, Hashes & Triad Invariant (Missing -> BLOCKED, Hash mismatch -> FAIL)
- Gate 3: Numerical Consistency (Invalid statistics -> FAIL, Zero numbers -> UNKNOWN)
- Gate 4: Narrative & Cross-Artifact Concordance (Clichés/Contradictions -> FAIL)
- Gate 5: Upstream Dependency Integrity (Missing dep -> BLOCKED, Hash mismatch -> FAIL)
- Gate 6: Composite Fail-Closed Verdict Resolution (PASS only if all gates pass with >= 1 positive evidence)
"""

import os
import sys
import json
import hashlib
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

# Fallback to system dist-packages
try:
    import jsonschema
except ImportError:
    for p in ["/usr/lib/python3/dist-packages", "/usr/local/lib/python3/dist-packages"]:
        if os.path.exists(p) and p not in sys.path:
            sys.path.append(p)
    try:
        import jsonschema
    except ImportError:
        jsonschema = None

import validators.manifest_registry as mr
from validators.reporting_consistency.validator import validate_reporting
from validators.numerical_consistency.validator import validate_numbers
from validators.data_integrity.validator import validate_data
from validators.statistical_assumptions.validator import validate_assumptions
from validators.result_consistency.validator import validate_cross_artifacts, validate_results
from validators.provenance_validator import validate_provenance


def compute_sha256(filepath: str) -> str:
    """Computes SHA-256 hash of a file on disk."""
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found for hash calculation: {filepath}")
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def is_triad_required_stage(stage_id: str) -> bool:
    """Determines whether a stage is required to produce the .json, .md, .docx Triad."""
    norm = stage_id.strip().lower()
    triad_indicators = [
        "hypothesis", "macro_model", "mediation", "moderation",
        "demographics", "descriptives", "assumptions", "bivariate", "summary",
        "cfa", "efa", "item_analysis", "construct_validity", "reliability",
        "irt_roc", "findings"
    ]
    return any(ind in norm for ind in triad_indicators) or norm.startswith("0") or norm.startswith("stage_")


def run_suite(
    stage_dir: str,
    stage_id: Optional[str] = None,
    milestone_id: Optional[str] = None,
    manifest: Optional[List[Dict[str, Any]]] = None,
    enforce_cross_artifacts: bool = True,
    require_manifest: bool = False
) -> Dict[str, Any]:
    """
    Executes fail-closed master validation against a stage directory or milestone.
    Returns a contract-compliant report conforming to contracts/validation_report.schema.json.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    report_id = f"VAL-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    report: Dict[str, Any] = {
        "contract_version": "1.0.0",
        "report_id": report_id,
        "suite": "Academic Suite Deterministic Validation Suite",
        "validator_name": "run_all_validators",
        "stage_directory": stage_dir,
        "timestamp": now_iso,
        "overall_verdict": "UNKNOWN",  # Strictly fail-closed initialization
        "evidence_summary": {
            "total_evidence_items_evaluated": 0,
            "total_checks_run": 0,
            "checks_passed": 0,
            "checks_failed": 0,
            "checks_blocked": 0,
            "checks_unknown": 0,
            "checks_unverified": 0
        },
        "target_artifacts": [],
        "results": [],
        "manifest_audit": {
            "required_artifacts": [],
            "present_artifacts": [],
            "missing_artifacts": [],
            "untracked_artifacts": []
        },
        "errors": [],
        "warnings": []
    }

    # ==========================================================================
    # Pre-Check: Directory Existence & Non-Empty Check
    # ==========================================================================
    if not stage_dir or not os.path.exists(stage_dir):
        err_msg = f"Stage directory not found: '{stage_dir}'"
        report["errors"].append(err_msg)
        report["overall_verdict"] = "BLOCKED"
        report["results"].append({
            "check_id": "CHK-DIR-EXISTS",
            "rule": "Stage directory must physically exist on disk",
            "verdict": "BLOCKED",
            "errors": [err_msg],
            "warnings": [],
            "evidence": {"stage_directory": stage_dir, "exists": False}
        })
        report["evidence_summary"]["total_checks_run"] = 1
        report["evidence_summary"]["checks_blocked"] = 1
        return report

    all_entries = os.listdir(stage_dir)
    files_on_disk = [f for f in all_entries if os.path.isfile(os.path.join(stage_dir, f))]

    if not files_on_disk:
        err_msg = f"Stage directory is empty (zero artifact files found): '{stage_dir}'"
        report["errors"].append(err_msg)
        report["overall_verdict"] = "BLOCKED"
        report["results"].append({
            "check_id": "CHK-DIR-NONEMPTY",
            "rule": "Stage directory must contain validated physical artifact files",
            "verdict": "BLOCKED",
            "errors": [err_msg],
            "warnings": [],
            "evidence": {"stage_directory": stage_dir, "files_count": 0}
        })
        report["evidence_summary"]["total_checks_run"] = 1
        report["evidence_summary"]["checks_blocked"] = 1
        return report

    # ==========================================================================
    # Pre-Check: Stage / Milestone Identification & Unknown Stage Check
    # ==========================================================================
    target_stages: Set[str] = set()

    if stage_id:
        if not mr.is_known_stage(stage_id):
            err_msg = f"Unknown or unregistered stage identifier: '{stage_id}'"
            report["errors"].append(err_msg)
            report["overall_verdict"] = "BLOCKED"
            report["results"].append({
                "check_id": "CHK-KNOWN-STAGE",
                "rule": "Stage must be canonically registered in AcademicSuite manifest registry",
                "verdict": "BLOCKED",
                "errors": [err_msg],
                "warnings": [],
                "evidence": {"stage_id": stage_id, "is_known": False}
            })
            report["evidence_summary"]["total_checks_run"] = 1
            report["evidence_summary"]["checks_blocked"] = 1
            return report
        target_stages.add(stage_id)

    if milestone_id:
        if not mr.is_known_milestone(milestone_id):
            err_msg = f"Unknown or unregistered milestone identifier: '{milestone_id}'"
            report["errors"].append(err_msg)
            report["overall_verdict"] = "BLOCKED"
            report["results"].append({
                "check_id": "CHK-KNOWN-MILESTONE",
                "rule": "Milestone must be canonically registered in AcademicSuite manifest registry",
                "verdict": "BLOCKED",
                "errors": [err_msg],
                "warnings": [],
                "evidence": {"milestone_id": milestone_id, "is_known": False}
            })
            report["evidence_summary"]["total_checks_run"] = 1
            report["evidence_summary"]["checks_blocked"] = 1
            return report

    # Auto-detect stages from filenames if not explicitly specified
    if not target_stages:
        for fname in files_on_disk:
            stem = os.path.splitext(fname)[0]
            # Check for unknown stage pattern in filename (e.g. 99_unknown_stage)
            if stem.startswith("99_") or "unknown" in stem.lower():
                err_msg = f"Unknown or unregistered stage detected in filename: '{fname}'"
                report["errors"].append(err_msg)
                report["overall_verdict"] = "BLOCKED"
                report["results"].append({
                    "check_id": "CHK-KNOWN-STAGE-FILE",
                    "rule": "Every stage artifact must belong to a canonically registered stage",
                    "verdict": "BLOCKED",
                    "errors": [err_msg],
                    "warnings": [],
                    "evidence": {"filename": fname, "stage_stem": stem, "is_known": False}
                })
                report["evidence_summary"]["total_checks_run"] = 1
                report["evidence_summary"]["checks_blocked"] = 1
                return report

            matched_stage = mr.resolve_stage_from_filename(fname)
            if matched_stage:
                target_stages.add(matched_stage)

    if not target_stages:
        # Fallback: check if directory name itself is a known stage
        dir_name = os.path.basename(os.path.abspath(stage_dir))
        if mr.is_known_stage(dir_name):
            target_stages.add(dir_name)
        else:
            err_msg = f"No recognized AcademicSuite stage identified in directory: '{stage_dir}'"
            report["errors"].append(err_msg)
            report["overall_verdict"] = "BLOCKED"
            report["results"].append({
                "check_id": "CHK-STAGE-IDENTIFICATION",
                "rule": "Validation suite must identify at least one canonically registered stage",
                "verdict": "BLOCKED",
                "errors": [err_msg],
                "warnings": [],
                "evidence": {"directory": stage_dir, "files": files_on_disk}
            })
            report["evidence_summary"]["total_checks_run"] = 1
            report["evidence_summary"]["checks_blocked"] = 1
            return report

    # ==========================================================================
    # Gate 0: Manifest Existence Check (Phase 9 Fail-Closed Gate)
    # ==========================================================================
    authoritative_manifest_path = os.path.join(stage_dir, "manifest.json")
    artifact_manifest_path = os.path.join(stage_dir, "artifact_manifest.json")
    manifest_data: Optional[Dict[str, Any]] = None
    custom_manifest_entries: Dict[str, Dict[str, Any]] = {}

    has_manifest_file = os.path.isfile(authoritative_manifest_path) or os.path.isfile(artifact_manifest_path)

    if require_manifest and not has_manifest_file:
        err_msg = f"No authoritative manifest.json found in '{stage_dir}'. Stage is UNVERIFIED."
        report["errors"].append(err_msg)
        report["overall_verdict"] = "UNVERIFIED"
        report["results"].append({
            "check_id": "CHK-MANIFEST-EXISTS",
            "rule": "Authoritative stage manifest (manifest.json) must physically exist on disk",
            "verdict": "UNVERIFIED",
            "errors": [err_msg],
            "warnings": [],
            "evidence": {"manifest_present": False, "stage_directory": stage_dir}
        })
        report["evidence_summary"]["total_checks_run"] = 1
        report["evidence_summary"]["checks_unverified"] = 1
        return report

    if os.path.isfile(authoritative_manifest_path):
        report["target_artifacts"].append(authoritative_manifest_path)
        try:
            with open(authoritative_manifest_path, "r", encoding="utf-8") as mf:
                manifest_data = json.load(mf)
            report["results"].append({
                "check_id": "CHK-MANIFEST-EXISTS",
                "rule": "Authoritative stage manifest (manifest.json) must physically exist on disk",
                "verdict": "PASS",
                "errors": [],
                "warnings": [],
                "evidence": {"manifest_file": "manifest.json", "stage_id": manifest_data.get("stage_id")}
            })
        except Exception as me:
            err_msg = f"Malformed manifest.json in '{stage_dir}': {str(me)}"
            report["errors"].append(err_msg)
            report["results"].append({
                "check_id": "CHK-MANIFEST-EXISTS",
                "rule": "Authoritative stage manifest (manifest.json) must be valid JSON",
                "verdict": "FAIL",
                "errors": [err_msg],
                "warnings": [],
                "evidence": {"manifest_file": "manifest.json", "corrupt": True}
            })

    elif os.path.isfile(artifact_manifest_path):
        report["target_artifacts"].append(artifact_manifest_path)
        try:
            with open(artifact_manifest_path, "r", encoding="utf-8") as mf:
                cdata = json.load(mf)
                entries = cdata if isinstance(cdata, list) else [cdata]
                for e in entries:
                    if isinstance(e, dict):
                        custom_manifest_entries[e.get("path") or e.get("artifact_id")] = e
            report["results"].append({
                "check_id": "CHK-MANIFEST-EXISTS",
                "rule": "Artifact manifest (artifact_manifest.json) must physically exist on disk",
                "verdict": "PASS",
                "errors": [],
                "warnings": [],
                "evidence": {"manifest_file": "artifact_manifest.json", "entries_count": len(custom_manifest_entries)}
            })
        except Exception as me:
            err_msg = f"Malformed artifact_manifest.json in '{stage_dir}': {str(me)}"
            report["errors"].append(err_msg)
            report["results"].append({
                "check_id": "CHK-MANIFEST-EXISTS",
                "rule": "Artifact manifest must be valid JSON",
                "verdict": "FAIL",
                "errors": [err_msg],
                "warnings": [],
                "evidence": {"manifest_file": "artifact_manifest.json", "corrupt": True}
            })

    # ==========================================================================
    # Gate 1: Manifest Schema Validation
    # ==========================================================================
    if manifest_data and isinstance(manifest_data, dict):
        schema_path = os.path.join(ROOT_DIR, "contracts", "stage_manifest.schema.json")
        if os.path.exists(schema_path) and jsonschema:
            try:
                with open(schema_path, "r", encoding="utf-8") as sf:
                    sch = json.load(sf)
                jsonschema.validate(instance=manifest_data, schema=sch)
                report["results"].append({
                    "check_id": "CHK-MANIFEST-SCHEMA",
                    "rule": "Stage manifest must conform to contracts/stage_manifest.schema.json",
                    "verdict": "PASS",
                    "errors": [],
                    "warnings": [],
                    "evidence": {"schema": "stage_manifest.schema.json", "valid": True}
                })
            except Exception as se:
                err_msg = f"Stage manifest failed schema validation: {str(se)}"
                report["errors"].append(err_msg)
                report["results"].append({
                    "check_id": "CHK-MANIFEST-SCHEMA",
                    "rule": "Stage manifest must conform to contracts/stage_manifest.schema.json",
                    "verdict": "FAIL",
                    "errors": [err_msg],
                    "warnings": [],
                    "evidence": {"schema": "stage_manifest.schema.json", "valid": False}
                })

    # ==========================================================================
    # Gate 2: Authoritative Artifact Manifest Resolution & Verification
    # ==========================================================================
    all_required_specs: List[Dict[str, Any]] = []
    if manifest:
        all_required_specs = manifest
    elif manifest_data and "required_artifacts" in manifest_data:
        for art in manifest_data["required_artifacts"]:
            all_required_specs.append({
                "artifact_id": art.get("path") or art.get("artifact_id", "ART_REQUIRED"),
                "type": art.get("type", "stats_json"),
                "filename_pattern": art.get("path"),
                "required": art.get("required", True),
                "schema": art.get("schema")
            })
    else:
        for stg in sorted(target_stages):
            stg_reqs = mr.get_required_artifacts_for_stage(stg)
            all_required_specs.extend(stg_reqs)

    # Triad Invariant Check for findings/hypothesis stages
    for stg in sorted(target_stages):
        if is_triad_required_stage(stg):
            has_json = any(f.endswith(".json") and "manifest" not in f and "validation" not in f for f in files_on_disk)
            has_md = any(f.endswith(".md") for f in files_on_disk)
            has_docx = any(f.endswith(".docx") for f in files_on_disk)
            if not (has_json and has_md and has_docx):
                missing_parts = []
                if not has_json: missing_parts.append(".json")
                if not has_md: missing_parts.append(".md")
                if not has_docx: missing_parts.append(".docx")
                err_msg = f"Stage '{stg}' violates Triad Artifact Invariant (Directive 3): missing {missing_parts}"
                report["errors"].append(err_msg)
                report["results"].append({
                    "check_id": f"CHK-TRIAD-{stg}",
                    "rule": "Every hypothesis and findings stage must generate a synchronized triad (.docx, .md, .json)",
                    "verdict": "BLOCKED",
                    "errors": [err_msg],
                    "warnings": [],
                    "evidence": {"stage_id": stg, "has_json": has_json, "has_md": has_md, "has_docx": has_docx}
                })

    # Verify each required artifact
    for spec in all_required_specs:
        spec_id = spec.get("artifact_id", "ART_REQUIRED")
        fname_pattern = spec.get("filename_pattern")
        expected_ext = spec.get("extension")
        art_type = spec.get("type", "")

        # Check artifact type validity
        if not mr.is_known_artifact_type(art_type):
            err_msg = f"Artifact specification '{spec_id}' defines unknown artifact type: '{art_type}'"
            report["errors"].append(err_msg)
            report["results"].append({
                "check_id": f"CHK-TYPE-{spec_id}",
                "rule": "Artifact types must be registered in AcademicArtifactManifestContract",
                "verdict": "BLOCKED",
                "errors": [err_msg],
                "warnings": [],
                "evidence": {"artifact_id": spec_id, "type": art_type}
            })
            continue

        report["manifest_audit"]["required_artifacts"].append({
            "artifact_id": spec_id,
            "type": art_type,
            "filename_pattern": fname_pattern,
            "required": spec.get("required", True)
        })

        # Locate candidate matching file
        matched_file = None
        if fname_pattern:
            for f in files_on_disk:
                if f.lower() == fname_pattern.lower() or os.path.basename(f).lower() == os.path.basename(fname_pattern).lower():
                    matched_file = os.path.join(stage_dir, f)
                    break
        elif expected_ext:
            candidates = [
                os.path.join(stage_dir, f) for f in files_on_disk if f.endswith(expected_ext)
            ]
            if len(target_stages) == 1 and candidates:
                matched_file = candidates[0]

        if not matched_file or not os.path.exists(matched_file):
            if spec.get("required", True):
                err_msg = f"Required artifact '{spec_id}' ({fname_pattern or expected_ext}) is missing from disk in '{stage_dir}'"
                report["errors"].append(err_msg)
                report["manifest_audit"]["missing_artifacts"].append(spec_id)
                report["results"].append({
                    "check_id": f"CHK-EXISTS-{spec_id}",
                    "rule": f"Required artifact '{spec_id}' must physically exist on disk",
                    "verdict": "BLOCKED",
                    "errors": [err_msg],
                    "warnings": [],
                    "evidence": {"artifact_id": spec_id, "expected": fname_pattern, "exists": False}
                })
            continue

        # File exists: verify non-empty and schema/hashes
        report["manifest_audit"]["present_artifacts"].append(os.path.basename(matched_file))
        report["target_artifacts"].append(matched_file)

        if os.path.getsize(matched_file) == 0:
            err_msg = f"Artifact '{spec_id}' exists but is 0 bytes (empty): {matched_file}"
            report["errors"].append(err_msg)
            report["results"].append({
                "check_id": f"CHK-NONZERO-{spec_id}",
                "rule": "Artifact must not be empty",
                "verdict": "FAIL",
                "errors": [err_msg],
                "warnings": [],
                "evidence": {"file": matched_file, "size_bytes": 0}
            })
            continue

        # Verify hash against manifest.json hashes if available
        if manifest_data and "hashes" in manifest_data:
            hashes_dict = manifest_data.get("hashes", {})
            rel_name = os.path.basename(matched_file)
            expected_h = hashes_dict.get(rel_name) or hashes_dict.get(fname_pattern) or hashes_dict.get(spec_id)
            if expected_h:
                actual_h = compute_sha256(matched_file)
                if actual_h.lower() != expected_h.lower():
                    err_msg = f"Cryptographic hash mismatch for '{rel_name}': manifest={expected_h}, disk={actual_h}"
                    report["errors"].append(err_msg)
                    report["results"].append({
                        "check_id": f"CHK-HASH-{spec_id}",
                        "rule": "Artifact cryptographic hash must match manifest hashes table",
                        "verdict": "FAIL",
                        "errors": [err_msg],
                        "warnings": [],
                        "evidence": {"file": rel_name, "expected": expected_h, "actual": actual_h}
                    })
                else:
                    report["results"].append({
                        "check_id": f"CHK-HASH-{spec_id}",
                        "rule": "Artifact cryptographic hash verified against manifest",
                        "verdict": "PASS",
                        "errors": [],
                        "warnings": [],
                        "evidence": {"file": rel_name, "hash_verified": True}
                    })

        # If custom manifest entry exists, verify complete manifest invariants (hash, schema, producer)
        custom_entry = custom_manifest_entries.get(os.path.basename(matched_file)) or custom_manifest_entries.get(spec_id)
        if custom_entry:
            ver_res = mr.verify_manifest_entry(custom_entry, stage_dir)
            if ver_res["verdict"] != "PASS":
                report["errors"].extend(ver_res["errors"])
                report["warnings"].extend(ver_res["warnings"])
                report["results"].append({
                    "check_id": f"CHK-MANIFEST-{spec_id}",
                    "rule": "Artifact must strictly satisfy manifest contract, hashes, and schemas",
                    "verdict": ver_res["verdict"],
                    "errors": ver_res["errors"],
                    "warnings": ver_res["warnings"],
                    "evidence": {"custom_manifest": custom_entry}
                })
            else:
                report["results"].append({
                    "check_id": f"CHK-MANIFEST-{spec_id}",
                    "rule": "Artifact manifest entry verified against disk file and cryptographic hash",
                    "verdict": "PASS",
                    "errors": [],
                    "warnings": [],
                    "evidence": {"hash_verified": True, "file": matched_file}
                })
        else:
            # Basic schema validation if JSON
            if matched_file.endswith(".json") and spec.get("schema"):
                schema_name = spec["schema"]
                schema_path = os.path.join(ROOT_DIR, "contracts", schema_name if schema_name.endswith(".json") else f"{schema_name}.schema.json")
                if os.path.exists(schema_path) and jsonschema:
                    try:
                        with open(matched_file, "r", encoding="utf-8") as jf:
                            inst = json.load(jf)
                        with open(schema_path, "r", encoding="utf-8") as sf:
                            sch = json.load(sf)
                        jsonschema.validate(instance=inst, schema=sch)
                        report["results"].append({
                            "check_id": f"CHK-SCHEMA-{spec_id}",
                            "rule": f"JSON artifact must satisfy schema '{schema_name}'",
                            "verdict": "PASS",
                            "errors": [],
                            "warnings": [],
                            "evidence": {"file": matched_file, "schema": schema_name, "valid": True}
                        })
                    except json.JSONDecodeError as jde:
                        err_msg = f"Malformed JSON in artifact '{matched_file}': {str(jde)}"
                        report["errors"].append(err_msg)
                        report["results"].append({
                            "check_id": f"CHK-SCHEMA-{spec_id}",
                            "rule": "JSON artifact must be well-formed JSON",
                            "verdict": "FAIL",
                            "errors": [err_msg],
                            "warnings": [],
                            "evidence": {"file": matched_file, "valid": False}
                        })
                    except Exception as se:
                        err_msg = f"Schema validation failed for '{matched_file}': {str(se)}"
                        report["errors"].append(err_msg)
                        report["results"].append({
                            "check_id": f"CHK-SCHEMA-{spec_id}",
                            "rule": f"JSON artifact must satisfy schema '{schema_name}'",
                            "verdict": "FAIL",
                            "errors": [err_msg],
                            "warnings": [],
                            "evidence": {"file": matched_file, "schema": schema_name, "valid": False}
                        })

    # Untracked files check
    present_basenames = set(report["manifest_audit"]["present_artifacts"])
    for f in files_on_disk:
        if f not in present_basenames and f not in ["manifest.json", "artifact_manifest.json"]:
            report["manifest_audit"]["untracked_artifacts"].append(f)

    # ==========================================================================
    # Gate 3: Numerical Consistency Execution
    # ==========================================================================
    json_files = [os.path.join(stage_dir, f) for f in files_on_disk if f.endswith(".json") and f not in ["manifest.json", "artifact_manifest.json"]]
    md_files = [os.path.join(stage_dir, f) for f in files_on_disk if f.endswith(".md")]
    docx_files = [os.path.join(stage_dir, f) for f in files_on_disk if f.endswith(".docx")]

    for json_path in json_files:
        bname = os.path.basename(json_path).lower()
        if "curation" not in bname and "data_audit" not in bname and "data_quality" not in bname and "assumption" not in bname:
            res = validate_numbers(json_path)
            report["target_artifacts"].append(json_path)
            c_verdict = res.get("verdict", "FAIL")
            report["results"].append({
                "check_id": f"CHK-NUMERICAL-{os.path.basename(json_path)}",
                "rule": "Numerical consistency and statistical parameter validity",
                "verdict": c_verdict,
                "errors": res.get("errors", []),
                "warnings": res.get("warnings", []),
                "evidence": {
                    "file": os.path.basename(json_path),
                    "sample_size": res.get("sample_size_audited"),
                    "evidence_items_audited": res.get("evidence_items_audited", 0)
                }
            })
            if res.get("errors"):
                report["errors"].extend(res["errors"])
            if res.get("warnings"):
                report["warnings"].extend(res["warnings"])

    # Data Integrity on Curation / Audit files
    for json_path in json_files:
        bname = os.path.basename(json_path).lower()
        if "curation" in bname or "data_audit" in bname or "data_quality" in bname:
            res = validate_data(json_path)
            report["target_artifacts"].append(json_path)
            c_verdict = res.get("verdict", "FAIL")
            report["results"].append({
                "check_id": f"CHK-DATA-{os.path.basename(json_path)}",
                "rule": "Data curation integrity, missingness rate <= 15%, and Little's MCAR",
                "verdict": c_verdict,
                "errors": res.get("errors", []),
                "warnings": res.get("warnings", []),
                "evidence": res.get("metrics", {"checked": True})
            })
            if res.get("errors"):
                report["errors"].extend(res["errors"])
            if res.get("warnings"):
                report["warnings"].extend(res["warnings"])

    # Statistical Assumptions on Assumption files
    for json_path in json_files:
        bname = os.path.basename(json_path).lower()
        if "assumption" in bname:
            res = validate_assumptions(json_path)
            report["target_artifacts"].append(json_path)
            c_verdict = res.get("verdict", "FAIL")
            report["results"].append({
                "check_id": f"CHK-ASSUMPTIONS-{os.path.basename(json_path)}",
                "rule": "Statistical assumptions verification (Levene's test, slope homogeneity, normality)",
                "verdict": c_verdict,
                "errors": res.get("errors", []),
                "warnings": res.get("warnings", []),
                "evidence": {"file": os.path.basename(json_path), "assumptions_checked": True}
            })
            if res.get("errors"):
                report["errors"].extend(res["errors"])
            if res.get("warnings"):
                report["warnings"].extend(res["warnings"])

    # ==========================================================================
    # Gate 4: Narrative & Cross-Artifact Concordance Execution
    # ==========================================================================
    # 1. Reporting Consistency on Markdown deliverables
    for md_path in md_files:
        res = validate_reporting(md_path)
        report["target_artifacts"].append(md_path)
        c_verdict = res.get("verdict", "FAIL")
        report["results"].append({
            "check_id": f"CHK-REPORTING-{os.path.basename(md_path)}",
            "rule": "Academic reporting consistency (no p=.000, Persian leading zero, no clichés, APA 7 tables)",
            "verdict": c_verdict,
            "errors": res.get("errors", []),
            "warnings": res.get("warnings", []),
            "evidence": {
                "file": os.path.basename(md_path),
                "checks_applied": ["no_p_000", "persian_leading_zero", "cliches", "3_table_standard", "sem_macro"]
            }
        })
        if res.get("errors"):
            report["errors"].extend(res["errors"])
        if res.get("warnings"):
            report["warnings"].extend(res["warnings"])

    # 2. Cross-Artifact Consistency (JSON vs MD vs DOCX)
    if enforce_cross_artifacts:
        for json_path in json_files:
            bname = os.path.basename(json_path).lower()
            if "curation" not in bname and "data_quality" not in bname:
                stem = os.path.splitext(json_path)[0]
                md_cand = stem + ".md"
                docx_cand = stem + ".docx"

                md_to_check = md_cand if os.path.exists(md_cand) else (md_files[0] if len(md_files) == 1 else None)
                docx_to_check = docx_cand if os.path.exists(docx_cand) else (docx_files[0] if len(docx_files) == 1 else None)

                res = validate_cross_artifacts(json_path, md_path=md_to_check, docx_path=docx_to_check)
                c_verdict = res.get("verdict", "FAIL")
                report["results"].append({
                    "check_id": f"CHK-CROSS-ARTIFACTS-{os.path.basename(json_path)}",
                    "rule": "Cross-artifact consistency across JSON, Markdown tables, and Word DOCX",
                    "verdict": c_verdict,
                    "errors": res.get("errors", []),
                    "warnings": res.get("warnings", []),
                    "evidence": res.get("evidence", {"checked": True})
                })
                if res.get("errors"):
                    report["errors"].extend(res["errors"])
                if res.get("warnings"):
                    report["warnings"].extend(res["warnings"])

    # 3. Claim Provenance & Evidence Layer Verification (Phase 11)
    prov_cand = os.path.join(stage_dir, "claim_provenance.json")
    has_prov_req = any(spec.get("type") == "claim_provenance_json" for spec in all_required_specs)
    if os.path.exists(prov_cand) or has_prov_req:
        res_prov = validate_provenance(stage_dir, require_provenance=has_prov_req)
        c_verdict = res_prov.get("verdict", "FAIL")
        report["results"].append({
            "check_id": "CHK-CLAIM-PROVENANCE",
            "rule": "Authoritative 5-link claim provenance (claim -> artifact -> statistic -> analysis -> data)",
            "verdict": c_verdict,
            "errors": res_prov.get("errors", []),
            "warnings": res_prov.get("warnings", []),
            "evidence": res_prov.get("evidence", {})
        })
        if res_prov.get("errors"):
            report["errors"].extend(res_prov["errors"])
        if res_prov.get("warnings"):
            report["warnings"].extend(res_prov["warnings"])

    # ==========================================================================
    # Gate 5: Upstream Dependency Verification
    # ==========================================================================
    if manifest_data and isinstance(manifest_data, dict) and "dependencies" in manifest_data:
        deps = manifest_data.get("dependencies", [])
        for dep in deps:
            dep_stage = dep.get("stage_id", "UNKNOWN_DEP")
            dep_path = dep.get("manifest_path", "")
            expected_hash = dep.get("manifest_hash", "")
            dep_full = dep_path if os.path.isabs(dep_path) else os.path.join(stage_dir, dep_path)
            if not os.path.exists(dep_full):
                alt = os.path.join(ROOT_DIR, dep_path)
                if os.path.exists(alt):
                    dep_full = alt

            if not os.path.exists(dep_full):
                err_msg = f"Prerequisite dependency manifest for '{dep_stage}' not found: {dep_full}"
                report["errors"].append(err_msg)
                report["results"].append({
                    "check_id": f"CHK-DEP-EXISTS-{dep_stage}",
                    "rule": f"Prerequisite dependency manifest for '{dep_stage}' must exist on disk",
                    "verdict": "BLOCKED",
                    "errors": [err_msg],
                    "warnings": [],
                    "evidence": {"dependency_stage": dep_stage, "expected_path": dep_path, "exists": False}
                })
            else:
                actual_hash = compute_sha256(dep_full)
                if expected_hash and actual_hash.lower() != expected_hash.lower():
                    err_msg = f"Dependency manifest hash mismatch for '{dep_stage}': expected {expected_hash}, got {actual_hash}"
                    report["errors"].append(err_msg)
                    report["results"].append({
                        "check_id": f"CHK-DEP-HASH-{dep_stage}",
                        "rule": f"Dependency manifest for '{dep_stage}' must match declared SHA-256 hash",
                        "verdict": "FAIL",
                        "errors": [err_msg],
                        "warnings": [],
                        "evidence": {"dependency_stage": dep_stage, "expected_hash": expected_hash, "actual_hash": actual_hash}
                    })
                else:
                    report["results"].append({
                        "check_id": f"CHK-DEP-HASH-{dep_stage}",
                        "rule": f"Dependency manifest for '{dep_stage}' verified against disk and cryptographic hash",
                        "verdict": "PASS",
                        "errors": [],
                        "warnings": [],
                        "evidence": {"dependency_stage": dep_stage, "hash_verified": True, "hash": actual_hash}
                    })

    # Deduplicate target_artifacts list
    report["target_artifacts"] = sorted(list(set(report["target_artifacts"])))

    # ==========================================================================
    # Gate 6: Composite Fail-Closed Verdict Calculation
    # ==========================================================================
    total_checks = len(report["results"])
    passed_checks = len([r for r in report["results"] if r["verdict"] == "PASS"])
    failed_checks = len([r for r in report["results"] if r["verdict"] == "FAIL"])
    blocked_checks = len([r for r in report["results"] if r["verdict"] == "BLOCKED"])
    unverified_checks = len([r for r in report["results"] if r["verdict"] in ["UNKNOWN", "UNVERIFIED", "INCOMPLETE"]])

    # Calculate distinct empirical evidence items evaluated
    evidence_count = 0
    for r in report["results"]:
        ev = r.get("evidence", {})
        if isinstance(ev, dict):
            evidence_count += max(1, len(ev))

    report["evidence_summary"]["total_checks_run"] = total_checks
    report["evidence_summary"]["checks_passed"] = passed_checks
    report["evidence_summary"]["checks_failed"] = failed_checks
    report["evidence_summary"]["checks_blocked"] = blocked_checks
    report["evidence_summary"]["checks_incomplete"] = unverified_checks
    report["evidence_summary"]["checks_unknown"] = unverified_checks
    report["evidence_summary"]["checks_unverified"] = unverified_checks
    report["evidence_summary"]["total_evidence_items_evaluated"] = evidence_count

    # Strict fail-closed verdict resolution (Phase 9 taxonomy)
    if blocked_checks > 0 or report["manifest_audit"]["missing_artifacts"]:
        report["overall_verdict"] = "BLOCKED"
    elif failed_checks > 0:
        report["overall_verdict"] = "FAIL"
    elif unverified_checks > 0:
        report["overall_verdict"] = "UNVERIFIED"
    elif total_checks == 0 or evidence_count == 0 or passed_checks == 0:
        report["overall_verdict"] = "UNVERIFIED"
    elif passed_checks == total_checks and total_checks > 0 and evidence_count >= 1:
        report["overall_verdict"] = "PASS"
    else:
        report["overall_verdict"] = "UNKNOWN"

    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="AcademicSuite Fail-Closed Deterministic Validation Suite")
    parser.add_argument('--stage-dir', required=True, help="Path to stage artifact directory")
    parser.add_argument('--stage-id', default=None, help="Explicit stage identifier")
    parser.add_argument('--milestone-id', default=None, help="Explicit milestone identifier")
    parser.add_argument('--require-manifest', action='store_true', help="Require authoritative manifest.json (Phase 9 fail-closed)")
    args = parser.parse_args()

    rep = run_suite(
        args.stage_dir,
        stage_id=args.stage_id,
        milestone_id=args.milestone_id,
        require_manifest=args.require_manifest
    )
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    sys.exit(0 if rep["overall_verdict"] == "PASS" else 1)
