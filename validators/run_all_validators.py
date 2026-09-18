#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validators/run_all_validators.py — Master Unified Fail-Closed Validator Engine

Executes deterministic validation on stage artifacts, enforcing authoritative milestone
and stage artifact manifests, cross-artifact consistency, schema conformance,
and a strict 5-tier status taxonomy: UNKNOWN / INCOMPLETE / BLOCKED / FAIL / PASS.

PASS is possible ONLY when all required checks explicitly succeed with affirmative evidence.
Missing directories, empty directories, unknown stages, missing required artifacts,
and incomplete validation fail closed.
"""

import os
import sys
import json
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


def run_suite(
    stage_dir: str,
    stage_id: Optional[str] = None,
    milestone_id: Optional[str] = None,
    manifest: Optional[List[Dict[str, Any]]] = None,
    enforce_cross_artifacts: bool = True
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
            "checks_incomplete": 0
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
    # Gate 1: Directory Existence & Non-Empty Check
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
    # Gate 2: Stage / Milestone Identification & Unknown Stage Check
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
    # Gate 3: Authoritative Artifact Manifest Resolution & Verification
    # ==========================================================================
    all_required_specs: List[Dict[str, Any]] = []
    if manifest:
        all_required_specs = manifest
    else:
        for stg in sorted(target_stages):
            stg_reqs = mr.get_required_artifacts_for_stage(stg)
            all_required_specs.extend(stg_reqs)

    # Check for custom artifact manifest file in directory
    manifest_file_path = os.path.join(stage_dir, "artifact_manifest.json")
    custom_manifest_entries: Dict[str, Dict[str, Any]] = {}
    if os.path.exists(manifest_file_path):
        try:
            with open(manifest_file_path, "r", encoding="utf-8") as mf:
                cdata = json.load(mf)
                entries = cdata if isinstance(cdata, list) else [cdata]
                for e in entries:
                    if isinstance(e, dict):
                        custom_manifest_entries[e.get("path") or e.get("artifact_id")] = e
        except Exception as me:
            report["errors"].append(f"Malformed artifact_manifest.json: {str(me)}")

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
                if f.lower() == fname_pattern.lower():
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
                            "rule": f"JSON artifact must be well-formed JSON",
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
        if f not in present_basenames and f != "artifact_manifest.json":
            report["manifest_audit"]["untracked_artifacts"].append(f)
            # An untracked file does NOT confer validity and does not satisfy missing manifest items

    # ==========================================================================
    # Gate 4: Deterministic Sub-Validators Execution
    # ==========================================================================
    json_files = [os.path.join(stage_dir, f) for f in files_on_disk if f.endswith(".json") and f != "artifact_manifest.json"]
    md_files = [os.path.join(stage_dir, f) for f in files_on_disk if f.endswith(".md")]
    docx_files = [os.path.join(stage_dir, f) for f in files_on_disk if f.endswith(".docx")]

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

    # 2. Numerical Consistency on JSON statistical outputs
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
                    "sample_size": res.get("sample_size_audited")
                }
            })
            if res.get("errors"):
                report["errors"].extend(res["errors"])
            if res.get("warnings"):
                report["warnings"].extend(res["warnings"])

    # 3. Data Integrity on Curation / Audit files
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

    # 4. Statistical Assumptions on Assumption files
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

    # 5. Cross-Artifact Consistency (JSON vs MD vs DOCX)
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

    # Deduplicate target_artifacts list
    report["target_artifacts"] = sorted(list(set(report["target_artifacts"])))

    # ==========================================================================
    # Gate 5: Composite Fail-Closed Verdict Calculation
    # ==========================================================================
    total_checks = len(report["results"])
    passed_checks = len([r for r in report["results"] if r["verdict"] == "PASS"])
    failed_checks = len([r for r in report["results"] if r["verdict"] == "FAIL"])
    blocked_checks = len([r for r in report["results"] if r["verdict"] == "BLOCKED"])
    incomplete_checks = len([r for r in report["results"] if r["verdict"] == "INCOMPLETE"])

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
    report["evidence_summary"]["checks_incomplete"] = incomplete_checks
    report["evidence_summary"]["total_evidence_items_evaluated"] = evidence_count

    # Strict fail-closed verdict resolution
    if blocked_checks > 0 or report["manifest_audit"]["missing_artifacts"]:
        report["overall_verdict"] = "BLOCKED"
    elif failed_checks > 0:
        report["overall_verdict"] = "FAIL"
    elif incomplete_checks > 0:
        report["overall_verdict"] = "INCOMPLETE"
    elif total_checks == 0 or evidence_count == 0:
        report["overall_verdict"] = "INCOMPLETE"
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
    args = parser.parse_args()

    rep = run_suite(args.stage_dir, stage_id=args.stage_id, milestone_id=args.milestone_id)
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    sys.exit(0 if rep["overall_verdict"] == "PASS" else 1)
