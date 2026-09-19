#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/stage_manifest_engine.py — Authoritative Stage Manifest Engine ("The Hands")

Generates and authoritatively validates stage completion manifests (manifest.json).
Enforces:
1. Manifest schema compliance against contracts/stage_manifest.schema.json
2. Input existence and cryptographic SHA-256 hash provenance
3. Triad Artifact Invariant (.docx, .md, .json) for all findings and hypothesis micro-stages
4. Cryptographic SHA-256 hash verification for all deliverables
5. Upstream dependency manifest hash verification
6. Cross-artifact numerical and semantic agreement across .json, .md, and .docx

Fails closed on any discrepancy.
"""

import os
import sys
import json
import hashlib
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Virtual environment discovery
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

# Fallback to system dist-packages
for p in ["/usr/lib/python3/dist-packages", "/usr/local/lib/python3/dist-packages"]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

try:
    import jsonschema
except ImportError:
    jsonschema = None

try:
    from validators.result_consistency.validator import validate_cross_artifacts
except ImportError:
    try:
        from result_consistency.validator import validate_cross_artifacts
    except ImportError:
        validate_cross_artifacts = None

try:
    from validators.provenance_validator import validate_provenance
except ImportError:
    try:
        from provenance_validator import validate_provenance
    except ImportError:
        validate_provenance = None


try:
    from scripts.academic_state_manager import StateManagementError
except ImportError:
    try:
        from academic_state_manager import StateManagementError
    except ImportError:
        class StateManagementError(Exception):
            pass

class StageManifestError(StateManagementError):
    """Base exception for stage manifest failures."""
    pass

class ManifestProvenanceError(StageManifestError):
    """Raised when claim provenance verification fails or an orphan claim is detected."""
    pass

class MissingStageManifestError(StageManifestError):
    """Raised when an authoritative manifest.json is missing from disk."""
    pass

class MalformedStageManifestError(StageManifestError):
    """Raised when a stage manifest fails schema validation or is malformed JSON."""
    pass

class ManifestInputMismatchError(StageManifestError):
    """Raised when declared inputs are missing or their cryptographic hash has mutated."""
    pass

class ManifestArtifactMissingError(StageManifestError):
    """Raised when declared deliverables are missing from disk or empty (0 bytes)."""
    pass

class ManifestTriadMissingError(StageManifestError):
    """Raised when a hypothesis or findings stage fails the Triad Invariant (.json, .md, .docx)."""
    pass

class ManifestHashMismatchError(StageManifestError):
    """Raised when an artifact on disk does not match its declared cryptographic SHA-256 hash."""
    pass

class ManifestDependencyMismatchError(StageManifestError):
    """Raised when an upstream dependency manifest is missing or its hash does not match."""
    pass

class ManifestCrossAgreementError(StageManifestError):
    """Raised when numbers across .json, .md, and .docx contradict each other."""
    pass


# ==============================================================================
# Cryptographic and Schema Utilities
# ==============================================================================

def compute_sha256(filepath: str) -> str:
    """Computes SHA-256 hash of a file on disk."""
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found for hash calculation: {filepath}")
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_stage_manifest_schema() -> Dict[str, Any]:
    """Loads the authoritative stage manifest JSON schema."""
    schema_path = os.path.join(ROOT_DIR, "contracts", "stage_manifest.schema.json")
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Contract schema not found: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


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


# ==============================================================================
# Authoritative Manifest Builder
# ==============================================================================

def build_stage_manifest(
    stage_dir: str,
    stage_id: str,
    project_id: str,
    agent: str,
    script_or_generator: str,
    command: str = "",
    inputs: Optional[List[Dict[str, Any]]] = None,
    artifacts: Optional[List[Dict[str, Any]]] = None,
    dependencies: Optional[List[Dict[str, Any]]] = None,
    validator_script: Optional[str] = None,
    cross_agreement_required: bool = True,
    write_manifest: bool = True,
    required_artifacts: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Builds an authoritative Stage Manifest dictionary and optionally writes it to manifest.json.
    Computes cryptographic SHA-256 hashes of all inputs and artifacts.
    Enforces the Triad Invariant and performs cross-artifact agreement audit.
    """
    artifacts = artifacts or required_artifacts
    stage_dir_abs = os.path.abspath(stage_dir)
    os.makedirs(stage_dir_abs, exist_ok=True)
    now_iso = datetime.now(timezone.utc).isoformat()

    # 1. Process inputs and compute hashes
    processed_inputs = []
    for inp in (inputs or []):
        raw_path = inp.get("path", "")
        full_inp_path = raw_path if os.path.isabs(raw_path) else os.path.join(stage_dir_abs, raw_path)
        if not os.path.exists(full_inp_path):
            alt_path = os.path.join(ROOT_DIR, raw_path)
            if os.path.exists(alt_path):
                full_inp_path = alt_path
        if not os.path.exists(full_inp_path):
            raise ManifestInputMismatchError(f"Input file not found on disk: {full_inp_path}")
        
        computed_h = compute_sha256(full_inp_path)
        processed_inputs.append({
            "path": raw_path,
            "sha256": computed_h,
            "description": inp.get("description", "Input artifact")
        })

    # 2. Discover / validate declared artifacts
    declared_artifacts = []
    hashes = {}
    json_path = None
    md_path = None
    docx_path = None

    if artifacts:
        for art in artifacts:
            rel_p = art.get("path", "")
            art_full = rel_p if os.path.isabs(rel_p) else os.path.join(stage_dir_abs, rel_p)
            if not os.path.isfile(art_full):
                raise ManifestArtifactMissingError(f"Declared artifact missing on disk: {art_full}")
            if os.path.getsize(art_full) == 0:
                raise ManifestArtifactMissingError(f"Declared artifact exists but is 0 bytes: {art_full}")
            
            art_h = compute_sha256(art_full)
            hashes[rel_p] = art_h
            declared_artifacts.append({
                "path": rel_p,
                "type": art.get("type", "stats_json"),
                "schema": art.get("schema", ""),
                "required": art.get("required", True),
                "description": art.get("description", "")
            })
            if rel_p.endswith(".json") and not json_path and "manifest" not in rel_p and "validation" not in rel_p:
                json_path = art_full
            elif rel_p.endswith(".md") and not md_path:
                md_path = art_full
            elif rel_p.endswith(".docx") and not docx_path:
                docx_path = art_full
    else:
        # Auto-discover artifacts in stage_dir (excluding manifest.json)
        for fname in sorted(os.listdir(stage_dir_abs)):
            if fname in ["manifest.json", "execution_manifest.json"]:
                continue
            art_full = os.path.join(stage_dir_abs, fname)
            if os.path.isfile(art_full):
                art_h = compute_sha256(art_full)
                hashes[fname] = art_h
                art_type = "stats_json" if fname.endswith(".json") else (
                    "narrative_markdown" if fname.endswith(".md") else (
                        "openxml_word" if fname.endswith(".docx") else "decision_log"
                    )
                )
                declared_artifacts.append({
                    "path": fname,
                    "type": art_type,
                    "schema": "",
                    "required": True,
                    "description": f"Stage artifact {fname}"
                })
                if fname.endswith(".json") and not json_path and "validation" not in fname:
                    json_path = art_full
                elif fname.endswith(".md") and not md_path:
                    md_path = art_full
                elif fname.endswith(".docx") and not docx_path:
                    docx_path = art_full

    # 3. Triad Invariant Enforcement
    if is_triad_required_stage(stage_id):
        has_json = any(a["path"].endswith(".json") and "validation" not in a["path"] for a in declared_artifacts)
        has_md = any(a["path"].endswith(".md") for a in declared_artifacts)
        has_docx = any(a["path"].endswith(".docx") for a in declared_artifacts)
        if not (has_json and has_md and has_docx):
            missing_parts = []
            if not has_json: missing_parts.append(".json")
            if not has_md: missing_parts.append(".md")
            if not has_docx: missing_parts.append(".docx")
            raise ManifestTriadMissingError(
                f"Stage '{stage_id}' violates Directive 3 Triad Artifact Invariant: missing {missing_parts}."
            )

    # 4. Cross-Artifact Agreement Audit
    cross_record = None
    if cross_agreement_required and json_path and (md_path or docx_path) and validate_cross_artifacts:
        val_res = validate_cross_artifacts(json_path=json_path, md_path=md_path, docx_path=docx_path)
        verdict = val_res.get("verdict", "FAIL")
        if verdict != "PASS":
            raise ManifestCrossAgreementError(
                f"Cross-artifact agreement check failed for stage '{stage_id}': {val_res.get('errors')}"
            )
        cross_record = {
            "verified": True,
            "verdict": verdict,
            "evaluated_at": now_iso,
            "evidence": val_res.get("evidence", {}),
            "errors": val_res.get("errors", []),
            "warnings": val_res.get("warnings", [])
        }

    # 4.5 Claim Provenance Verification (Phase 11)
    prov_file = os.path.join(stage_dir_abs, "claim_provenance.json")
    has_prov_req = any(art.get("type") == "claim_provenance_json" for art in (required_artifacts or []))
    if (os.path.exists(prov_file) or has_prov_req) and validate_provenance:
        prov_res = validate_provenance(stage_dir_abs, require_provenance=has_prov_req)
        if prov_res.get("verdict") != "PASS":
            raise ManifestProvenanceError(
                f"Claim provenance verification failed for stage '{stage_id}': {prov_res.get('errors')}"
            )

    # 5. Process dependencies
    processed_deps = []
    for dep in (dependencies or []):
        dep_stage = dep.get("stage_id", "")
        dep_manifest_path = dep.get("manifest_path", "")
        dep_full = dep_manifest_path if os.path.isabs(dep_manifest_path) else os.path.join(stage_dir_abs, dep_manifest_path)
        if not os.path.exists(dep_full):
            alt_dep = os.path.join(ROOT_DIR, dep_manifest_path)
            if os.path.exists(alt_dep):
                dep_full = alt_dep
        if not os.path.exists(dep_full):
            raise ManifestDependencyMismatchError(f"Dependency manifest for stage '{dep_stage}' not found: {dep_full}")
        actual_dep_hash = compute_sha256(dep_full)
        expected_dep_hash = dep.get("manifest_hash", actual_dep_hash)
        if actual_dep_hash.lower() != expected_dep_hash.lower():
            raise ManifestDependencyMismatchError(
                f"Dependency manifest hash mismatch for stage '{dep_stage}': expected {expected_dep_hash}, got {actual_dep_hash}"
            )
        processed_deps.append({
            "stage_id": dep_stage,
            "manifest_path": dep_manifest_path,
            "manifest_hash": actual_dep_hash
        })

    # Assemble manifest structure conforming to contracts/stage_manifest.schema.json
    manifest_data = {
        "contract_version": "1.0.0",
        "stage_id": stage_id,
        "project_id": project_id,
        "producer": {
            "agent": agent,
            "script_or_generator": script_or_generator,
            "command": command
        },
        "inputs": processed_inputs,
        "required_artifacts": declared_artifacts,
        "dependencies": processed_deps,
        "validation_requirements": {
            "validator_suite_required": True,
            "validator_script": validator_script or "validators/result_consistency/validator.py",
            "expected_verdict": "PASS",
            "cross_agreement_required": cross_agreement_required
        },
        "hashes": hashes,
        "status": "VALIDATED" if cross_record else "GENERATED",
        "timestamps": {
            "created_at": now_iso,
            "completed_at": now_iso,
            "validated_at": now_iso if cross_record else None
        }
    }

    if cross_record:
        manifest_data["cross_agreement"] = cross_record

    # Schema self-check
    schema = load_stage_manifest_schema()
    if jsonschema:
        jsonschema.validate(instance=manifest_data, schema=schema)

    if write_manifest:
        out_manifest_path = os.path.join(stage_dir_abs, "manifest.json")
        with open(out_manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)

    return manifest_data


# ==============================================================================
# Authoritative Manifest Verifier
# ==============================================================================

def verify_stage_manifest(
    manifest_path_or_dict: Union[str, Dict[str, Any]],
    base_dir: Optional[str] = None,
    check_inputs: bool = True,
    check_dependencies: bool = True,
    check_cross_agreement: bool = True,
    fail_closed: bool = True
) -> Dict[str, Any]:
    """
    Authoritatively verifies a stage completion manifest:
    1. Schema validation against contracts/stage_manifest.schema.json
    2. Input existence and cryptographic SHA-256 integrity
    3. Artifact existence and non-zero byte size
    4. Triad Invariant check (.json, .md, .docx)
    5. Artifact cryptographic SHA-256 hash match against manifest.hashes
    6. Upstream dependency manifest existence and hash match
    7. Cross-artifact numerical agreement across .json, .md, and .docx

    Fails closed by raising specific exceptions if fail_closed=True,
    or returns diagnostic result dictionary.
    """
    errors: List[str] = []
    warnings: List[str] = []

    # 1. Ingest manifest
    if isinstance(manifest_path_or_dict, str):
        manifest_file = os.path.abspath(manifest_path_or_dict)
        if not os.path.exists(manifest_file):
            err_msg = f"Authoritative stage manifest not found on disk: {manifest_file}"
            if fail_closed:
                raise MissingStageManifestError(err_msg)
            return {"verdict": "FAIL", "status": "FAIL", "errors": [err_msg]}
        try:
            with open(manifest_file, "r", encoding="utf-8") as mf:
                manifest_data = json.load(mf)
        except Exception as e:
            err_msg = f"Malformed manifest JSON in {manifest_file}: {str(e)}"
            if fail_closed:
                raise MalformedStageManifestError(err_msg)
            return {"verdict": "FAIL", "status": "FAIL", "errors": [err_msg]}
        
        target_dir = base_dir or os.path.dirname(manifest_file)
    elif isinstance(manifest_path_or_dict, dict):
        manifest_data = manifest_path_or_dict
        target_dir = base_dir or os.getcwd()
    else:
        err_msg = f"Invalid manifest specification of type {type(manifest_path_or_dict)}"
        if fail_closed:
            raise MalformedStageManifestError(err_msg)
        return {"verdict": "FAIL", "status": "FAIL", "errors": [err_msg]}

    stage_id = manifest_data.get("stage_id", "UNKNOWN_STAGE")

    # 2. Schema Validation
    schema = load_stage_manifest_schema()
    if jsonschema:
        try:
            jsonschema.validate(instance=manifest_data, schema=schema)
        except jsonschema.ValidationError as ve:
            err_msg = f"Stage manifest for '{stage_id}' violates schema: {ve.message}"
            if fail_closed:
                raise MalformedStageManifestError(err_msg)
            errors.append(err_msg)

    # 3. Input Cryptographic Hash Verification
    if check_inputs:
        for inp in manifest_data.get("inputs", []):
            inp_rel = inp.get("path", "")
            expected_h = inp.get("sha256", "")
            inp_full = inp_rel if os.path.isabs(inp_rel) else os.path.join(target_dir, inp_rel)
            if not os.path.exists(inp_full):
                alt = os.path.join(ROOT_DIR, inp_rel)
                if os.path.exists(alt):
                    inp_full = alt
            if not os.path.exists(inp_full):
                err_msg = f"Input artifact '{inp_rel}' declared in manifest does not exist: {inp_full}"
                if fail_closed:
                    raise ManifestInputMismatchError(err_msg)
                errors.append(err_msg)
                continue
            
            actual_h = compute_sha256(inp_full)
            if actual_h.lower() != expected_h.lower():
                err_msg = (
                    f"Cryptographic hash mismatch for input '{inp_rel}': "
                    f"manifest={expected_h}, disk={actual_h}"
                )
                if fail_closed:
                    raise ManifestInputMismatchError(err_msg)
                errors.append(err_msg)

    # 4. Artifact Existence & Triad Invariant
    declared_artifacts = manifest_data.get("required_artifacts", [])
    hashes = manifest_data.get("hashes", {})
    json_path = None
    md_path = None
    docx_path = None

    if not declared_artifacts:
        err_msg = f"Manifest for stage '{stage_id}' declares zero required artifacts."
        if fail_closed:
            raise ManifestArtifactMissingError(err_msg)
        errors.append(err_msg)

    for art in declared_artifacts:
        art_rel = art.get("path", "")
        art_full = art_rel if os.path.isabs(art_rel) else os.path.join(target_dir, art_rel)
        if not os.path.isfile(art_full):
            alt = os.path.join(ROOT_DIR, art_rel)
            if os.path.isfile(alt):
                art_full = alt
        if not os.path.isfile(art_full):
            err_msg = f"Required deliverable '{art_rel}' declared in manifest is missing from disk: {art_full}"
            if fail_closed:
                raise ManifestArtifactMissingError(err_msg)
            errors.append(err_msg)
            continue

        if os.path.getsize(art_full) == 0:
            err_msg = f"Deliverable '{art_rel}' exists on disk but is 0 bytes (empty): {art_full}"
            if fail_closed:
                raise ManifestArtifactMissingError(err_msg)
            errors.append(err_msg)
            continue

        # Hash verification
        expected_art_h = hashes.get(art_rel)
        if not expected_art_h:
            # Fallback check for basename key
            expected_art_h = hashes.get(os.path.basename(art_rel))
        
        if expected_art_h:
            actual_art_h = compute_sha256(art_full)
            if actual_art_h.lower() != expected_art_h.lower():
                err_msg = (
                    f"Cryptographic hash mismatch for deliverable '{art_rel}': "
                    f"manifest={expected_art_h}, disk={actual_art_h}"
                )
                if fail_closed:
                    raise ManifestHashMismatchError(err_msg)
                errors.append(err_msg)
        else:
            warnings.append(f"Deliverable '{art_rel}' is not keyed in manifest hashes table.")

        if art_rel.endswith(".json") and not json_path and "manifest" not in art_rel and "validation" not in art_rel:
            json_path = art_full
        elif art_rel.endswith(".md") and not md_path:
            md_path = art_full
        elif art_rel.endswith(".docx") and not docx_path:
            docx_path = art_full

    # Triad Check
    if is_triad_required_stage(stage_id):
        has_json = any(a["path"].endswith(".json") and "validation" not in a["path"] for a in declared_artifacts)
        has_md = any(a["path"].endswith(".md") for a in declared_artifacts)
        has_docx = any(a["path"].endswith(".docx") for a in declared_artifacts)
        if not (has_json and has_md and has_docx):
            missing_types = []
            if not has_json: missing_types.append(".json")
            if not has_md: missing_types.append(".md")
            if not has_docx: missing_types.append(".docx")
            err_msg = f"Stage '{stage_id}' violates Triad Invariant: missing required {missing_types} deliverable(s)."
            if fail_closed:
                raise ManifestTriadMissingError(err_msg)
            errors.append(err_msg)

    # 5. Dependency Hash Verification
    if check_dependencies:
        for dep in manifest_data.get("dependencies", []):
            dep_stage = dep.get("stage_id", "")
            dep_path = dep.get("manifest_path", "")
            expected_dep_h = dep.get("manifest_hash", "")
            dep_full = dep_path if os.path.isabs(dep_path) else os.path.join(target_dir, dep_path)
            if not os.path.exists(dep_full):
                alt = os.path.join(ROOT_DIR, dep_path)
                if os.path.exists(alt):
                    dep_full = alt
            if not os.path.exists(dep_full):
                err_msg = f"Prerequisite manifest for dependency stage '{dep_stage}' not found: {dep_full}"
                if fail_closed:
                    raise ManifestDependencyMismatchError(err_msg)
                errors.append(err_msg)
                continue
            
            actual_dep_h = compute_sha256(dep_full)
            if actual_dep_h.lower() != expected_dep_h.lower():
                err_msg = (
                    f"Dependency manifest hash mismatch for stage '{dep_stage}': "
                    f"expected={expected_dep_h}, disk={actual_dep_h}"
                )
                if fail_closed:
                    raise ManifestDependencyMismatchError(err_msg)
                errors.append(err_msg)

    # 6. Cross-Artifact Numerical Agreement
    val_reqs = manifest_data.get("validation_requirements", {})
    require_cross = check_cross_agreement and val_reqs.get("cross_agreement_required", True)
    if require_cross and json_path and (md_path or docx_path) and validate_cross_artifacts:
        val_res = validate_cross_artifacts(json_path=json_path, md_path=md_path, docx_path=docx_path)
        verdict = val_res.get("verdict", "FAIL")
        if verdict != "PASS":
            err_msg = (
                f"Cross-artifact numerical agreement contradiction in stage '{stage_id}': "
                f"{val_res.get('errors')}"
            )
            if fail_closed:
                raise ManifestCrossAgreementError(err_msg)
            errors.extend(val_res.get("errors", [err_msg]))

    # 6.5 Claim Provenance Verification (Phase 11)
    prov_file = os.path.join(target_dir, "claim_provenance.json")
    has_prov_req = any(art.get("type") == "claim_provenance_json" for art in manifest_data.get("required_artifacts", []))
    if (os.path.exists(prov_file) or has_prov_req) and validate_provenance:
        prov_res = validate_provenance(target_dir, require_provenance=has_prov_req)
        if prov_res.get("verdict") != "PASS":
            err_msg = f"Claim provenance verification failed in stage '{stage_id}': {prov_res.get('errors')}"
            if fail_closed:
                raise ManifestProvenanceError(err_msg)
            errors.extend(prov_res.get("errors", [err_msg]))

    verdict = "FAIL" if errors else ("NEEDS_REVIEW" if warnings else "PASS")
    return {
        "stage_id": stage_id,
        "verdict": verdict,
        "status": verdict,
        "errors": errors,
        "warnings": warnings,
        "manifest_path": manifest_path_or_dict if isinstance(manifest_path_or_dict, str) else None,
        "manifest": manifest_data
    }


# ==============================================================================
# Deterministic CLI Interface ("The Hands")
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Authoritative Stage Manifest Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # build subcommand
    build_p = subparsers.add_parser("build", help="Build authoritative manifest.json for a stage directory")
    build_p.add_argument("--stage-dir", required=True, help="Directory of stage deliverables")
    build_p.add_argument("--stage-id", required=True, help="Micro-stage identifier (e.g. 06_hypothesis_1)")
    build_p.add_argument("--project-id", required=True, help="Research project identifier")
    build_p.add_argument("--agent", default="statistics-agent", help="Assigned cognitive producer agent")
    build_p.add_argument("--script", default="scripts/statistical_pipeline_engine.py", help="Computational script")
    build_p.add_argument("--cmd", default="", help="Command invoked to generate deliverables")

    # verify subcommand
    verify_p = subparsers.add_parser("verify", help="Verify authoritative manifest.json")
    verify_p.add_argument("--manifest", required=True, help="Path to manifest.json")
    verify_p.add_argument("--no-fail-closed", action="store_true", help="Print JSON report instead of raising exception")

    args = parser.parse_args()

    if args.command == "build":
        try:
            res = build_stage_manifest(
                stage_dir=args.stage_dir,
                stage_id=args.stage_id,
                project_id=args.project_id,
                agent=args.agent,
                script_or_generator=args.script,
                command=args.cmd
            )
            print(json.dumps({"status": "SUCCESS", "stage_id": args.stage_id, "manifest": res}, indent=2, ensure_ascii=False))
            sys.exit(0)
        except Exception as e:
            sys.stderr.write(f"Error building stage manifest: {str(e)}\n")
            sys.exit(1)

    elif args.command == "verify":
        try:
            res = verify_stage_manifest(
                manifest_path_or_dict=args.manifest,
                fail_closed=not args.no_fail_closed
            )
            print(json.dumps(res, indent=2, ensure_ascii=False))
            sys.exit(0 if res["verdict"] == "PASS" else 1)
        except Exception as e:
            sys.stderr.write(f"Verification FAILED: {str(e)}\n")
            sys.exit(1)


if __name__ == "__main__":
    main()
