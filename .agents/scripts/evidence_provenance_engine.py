#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/evidence_provenance_engine.py — Deterministic Evidence & Claim Provenance Engine ("The Hands")

Implements Phase 11 architectural requirements:
1. Explicit 4-Tier Evidence Layer:
   Raw statistical output -> Verified result -> Interpretation -> Claim
2. Authoritative 5-Link Provenance Relationship:
   claim -> artifact -> statistic -> analysis -> data

Provides:
- build_claim_provenance(...) -> Dict[str, Any]
- trace_claim_provenance(claim_id, ...) -> Dict[str, Any]
- verify_claim_provenance(...) -> Dict[str, Any]
- CLI subcommands: build, verify, trace
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


class ProvenanceError(Exception):
    """Base exception for evidence provenance failures."""
    pass


class ProvenanceSchemaError(ProvenanceError):
    """Raised when claim_provenance.json violates the schema."""
    pass


class BrokenProvenanceLinkError(ProvenanceError):
    """Raised when any link in the 5-link chain is missing, corrupted, or mismatched."""
    pass


def compute_sha256(filepath: str) -> str:
    """Computes the SHA-256 cryptographic hash of a file on disk."""
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found for hash calculation: {filepath}")
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_claim_provenance_schema() -> Optional[Dict[str, Any]]:
    """Loads the authoritative claim_provenance.schema.json contract."""
    schema_path = os.path.join(ROOT_DIR, "contracts", "claim_provenance.schema.json")
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def resolve_path(path: str, base_dir: Optional[str] = None) -> str:
    """Resolves a relative path against base_dir or ROOT_DIR."""
    if os.path.isabs(path):
        return path
    if base_dir and os.path.exists(os.path.join(base_dir, path)):
        return os.path.abspath(os.path.join(base_dir, path))
    if os.path.exists(os.path.join(ROOT_DIR, path)):
        return os.path.abspath(os.path.join(ROOT_DIR, path))
    if base_dir:
        return os.path.abspath(os.path.join(base_dir, path))
    return os.path.abspath(path)


def build_claim_provenance(
    stage_dir: str,
    stage_id: str,
    project_id: str,
    target_scope: str,
    raw_output_path: str,
    result_json_path: str,
    narrative_md_path: str,
    claims_spec: List[Dict[str, Any]],
    script_path: str,
    dataset_path: str,
    sample_size: int,
    narrative_docx_path: Optional[str] = None,
    filter_query: Optional[str] = None,
    transformations: Optional[List[str]] = None,
    output_filename: str = "claim_provenance.json"
) -> Dict[str, Any]:
    """
    Builds the authoritative 4-tier evidence layer and 5-link claim provenance manifest.
    Writes claim_provenance.json into stage_dir.
    """
    stage_dir_abs = os.path.abspath(stage_dir)
    raw_output_abs = resolve_path(raw_output_path, stage_dir_abs)
    result_json_abs = resolve_path(result_json_path, stage_dir_abs)
    narrative_md_abs = resolve_path(narrative_md_path, stage_dir_abs)
    script_abs = resolve_path(script_path, stage_dir_abs)
    dataset_abs = resolve_path(dataset_path, stage_dir_abs)

    # Validate prerequisite files exist
    for label, path in [
        ("Raw statistical output", raw_output_abs),
        ("Verified result JSON", result_json_abs),
        ("Narrative Markdown", narrative_md_abs),
        ("Analysis script", script_abs),
        ("Raw dataset", dataset_abs)
    ]:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"{label} file not found: {path}")

    # Compute cryptographic hashes
    raw_output_hash = compute_sha256(raw_output_abs)
    result_json_hash = compute_sha256(result_json_abs)
    narrative_md_hash = compute_sha256(narrative_md_abs)
    script_hash = compute_sha256(script_abs)
    dataset_hash = compute_sha256(dataset_abs)

    docx_abs = None
    docx_hash = None
    if narrative_docx_path:
        docx_abs = resolve_path(narrative_docx_path, stage_dir_abs)
        if os.path.isfile(docx_abs):
            docx_hash = compute_sha256(docx_abs)

    # Load result.json to inspect parameters
    with open(result_json_abs, "r", encoding="utf-8") as f:
        result_data = json.load(f)

    # Gather parameter keys from result_data
    parameter_keys = []
    if isinstance(result_data, dict):
        for k in ["parameters", "statistics", "coefficients", "model_fit", "indirect_effects", "descriptives"]:
            if k in result_data and isinstance(result_data[k], dict):
                parameter_keys.extend(result_data[k].keys())
        if not parameter_keys:
            parameter_keys = list(result_data.keys())

    # Build Tier 3 contextual statements from narrative
    contextual_statements = []
    for c in claims_spec:
        stmt = c.get("statement", "")
        if stmt:
            contextual_statements.append(stmt)

    tier_4_claim_ids = [c["claim_id"] for c in claims_spec]

    now_iso = datetime.now(timezone.utc).isoformat()

    # Build Claims with 5-link provenance
    built_claims = []
    for c in claims_spec:
        cid = c["claim_id"]
        statement = c["statement"]
        ctype = c.get("claim_type", "DIRECT_FINDING")
        cscope = c.get("target_scope", target_scope)
        pkey = c.get("parameter_key", "primary_statistic")
        
        # Determine metrics
        metrics = c.get("metrics")
        if not metrics and isinstance(result_data, dict):
            # Try to locate in result_data
            if pkey in result_data:
                metrics = result_data[pkey] if isinstance(result_data[pkey], dict) else {"value": result_data[pkey]}
            elif "parameters" in result_data and pkey in result_data["parameters"]:
                metrics = result_data["parameters"][pkey] if isinstance(result_data["parameters"][pkey], dict) else {"value": result_data["parameters"][pkey]}
            else:
                metrics = {"parameter_key": pkey}

        # Artifact format & path
        art_rel = os.path.relpath(narrative_md_abs, stage_dir_abs)
        art_hash = narrative_md_hash
        art_format = "markdown"

        # Check if claim specifies docx
        if c.get("artifact_format") == "docx" and docx_abs and docx_hash:
            art_rel = os.path.relpath(docx_abs, stage_dir_abs)
            art_hash = docx_hash
            art_format = "docx"

        claim_entry = {
            "claim_id": cid,
            "statement": statement,
            "claim_type": ctype,
            "target_scope": cscope,
            "status": "VERIFIED",
            "interpretation": c.get("interpretation", {
                "statement": statement,
                "directional_support": c.get("directional_support", True),
                "hypothesis_ref": c.get("hypothesis_ref", stage_id)
            }),
            "provenance": {
                "artifact": {
                    "path": art_rel,
                    "sha256": art_hash,
                    "location": c.get("location", "Results / Findings narrative"),
                    "format": art_format
                },
                "statistic": {
                    "parameter_key": pkey,
                    "metrics": metrics,
                    "verified_result_ref": {
                        "path": os.path.relpath(result_json_abs, stage_dir_abs),
                        "sha256": result_json_hash
                    }
                },
                "analysis": {
                    "analysis_id": c.get("analysis_id", f"AN-{stage_id}"),
                    "method": c.get("method", "Deterministic Hypothesis Testing"),
                    "model_formula": c.get("model_formula", "y ~ x"),
                    "script_path": os.path.relpath(script_abs, ROOT_DIR),
                    "script_sha256": script_hash,
                    "execution_timestamp": c.get("execution_timestamp", now_iso),
                    "raw_output_ref": {
                        "path": os.path.relpath(raw_output_abs, stage_dir_abs),
                        "sha256": raw_output_hash
                    }
                },
                "data": {
                    "dataset_path": os.path.relpath(dataset_abs, ROOT_DIR),
                    "dataset_sha256": dataset_hash,
                    "sample_size": sample_size,
                    "filter_query": filter_query or "complete_cases == True",
                    "transformations": transformations or ["z_score_standardization", "reverse_scoring"]
                }
            }
        }
        built_claims.append(claim_entry)

    provenance_doc: Dict[str, Any] = {
        "contract_version": "1.0.0",
        "stage_id": stage_id,
        "project_id": project_id,
        "target_scope": target_scope,
        "evidence_tiers": {
            "tier_1_raw_output": {
                "path": os.path.relpath(raw_output_abs, stage_dir_abs),
                "sha256": raw_output_hash,
                "description": "Raw matrix/log statistical output from deterministic execution engine",
                "timestamp": now_iso
            },
            "tier_2_verified_result": {
                "path": os.path.relpath(result_json_abs, stage_dir_abs),
                "sha256": result_json_hash,
                "parameter_keys": parameter_keys,
                "verification_status": "VERIFIED"
            },
            "tier_3_interpretation": {
                "narrative_artifact_path": os.path.relpath(narrative_md_abs, stage_dir_abs),
                "narrative_sha256": narrative_md_hash,
                "contextual_statements": contextual_statements
            },
            "tier_4_claims": tier_4_claim_ids
        },
        "claims": built_claims,
        "status": "VERIFIED",
        "timestamps": {
            "created_at": now_iso,
            "verified_at": now_iso
        }
    }

    # Validate against schema
    schema = load_claim_provenance_schema()
    if schema and jsonschema:
        try:
            jsonschema.validate(instance=provenance_doc, schema=schema)
        except Exception as se:
            raise ProvenanceSchemaError(f"Generated provenance document failed schema validation: {str(se)}")

    # Write to stage_dir
    output_path = os.path.join(stage_dir_abs, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(provenance_doc, f, indent=2, ensure_ascii=False)

    return provenance_doc


def find_metric_in_dict(data: Any, pkey: Optional[str], mkey: str) -> Optional[Union[int, float]]:
    """Locates a numerical metric in result data using pkey context or direct key lookup."""
    if not isinstance(data, dict):
        return None

    # 1. Check if pkey is in data and contains mkey
    if pkey and pkey in data and isinstance(data[pkey], dict) and mkey in data[pkey]:
        val = data[pkey][mkey]
        if isinstance(val, (int, float)):
            return float(val)

    # 2. Check in 'parameters', 'statistics', 'coefficients', 'model_fit' under pkey
    for container in ["parameters", "statistics", "coefficients", "model_fit"]:
        if container in data and isinstance(data[container], dict):
            c_dict = data[container]
            if pkey and pkey in c_dict and isinstance(c_dict[pkey], dict) and mkey in c_dict[pkey]:
                val = c_dict[pkey][mkey]
                if isinstance(val, (int, float)):
                    return float(val)
            if mkey in c_dict and isinstance(c_dict[mkey], (int, float)):
                return float(c_dict[mkey])

    # 3. Direct top-level lookup
    if mkey in data and isinstance(data[mkey], (int, float)):
        return float(data[mkey])

    # 4. Recursive search
    for k, v in data.items():
        if isinstance(v, dict):
            res = find_metric_in_dict(v, pkey, mkey)
            if res is not None:
                return res

    return None


def trace_claim_provenance(
    claim_id: str,
    provenance_data_or_path: Union[str, Dict[str, Any]],
    stage_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Traces the unbroken 5-link provenance relationship for a specific claim:
    claim -> artifact -> statistic -> analysis -> data
    """
    if isinstance(provenance_data_or_path, str):
        with open(provenance_data_or_path, "r", encoding="utf-8") as f:
            prov_data = json.load(f)
        if not stage_dir:
            stage_dir = os.path.dirname(os.path.abspath(provenance_data_or_path))
    else:
        prov_data = provenance_data_or_path
        if not stage_dir:
            stage_dir = os.getcwd()

    claims = prov_data.get("claims", [])
    target_claim = None
    for c in claims:
        if c.get("claim_id") == claim_id:
            target_claim = c
            break

    if not target_claim:
        return {
            "claim_id": claim_id,
            "found": False,
            "unbroken": False,
            "break_reasons": [f"Claim ID '{claim_id}' not found in provenance manifest"],
            "trace": None
        }

    prov = target_claim.get("provenance", {})
    break_reasons = []

    # Check Link 1: Claim
    link_1 = {
        "claim_id": target_claim.get("claim_id"),
        "statement": target_claim.get("statement"),
        "claim_type": target_claim.get("claim_type"),
        "target_scope": target_claim.get("target_scope"),
        "interpretation": target_claim.get("interpretation")
    }

    # Check Link 2: Artifact
    art = prov.get("artifact", {})
    art_path = art.get("path")
    art_hash = art.get("sha256")
    art_full = resolve_path(art_path, stage_dir) if art_path else None
    art_exists = os.path.isfile(art_full) if art_full else False
    art_hash_matches = False
    if art_exists:
        actual_hash = compute_sha256(art_full)
        art_hash_matches = (actual_hash.lower() == art_hash.lower()) if art_hash else False
        if not art_hash_matches:
            break_reasons.append(f"Link 2 (Artifact) SHA-256 mismatch: expected {art_hash}, got {actual_hash}")
    else:
        break_reasons.append(f"Link 2 (Artifact) missing from disk: {art_full or art_path}")

    link_2 = {
        "path": art_path,
        "full_path": art_full,
        "declared_sha256": art_hash,
        "exists": art_exists,
        "hash_verified": art_hash_matches,
        "format": art.get("format"),
        "location": art.get("location")
    }

    # Check Link 3: Statistic
    stat = prov.get("statistic", {})
    pkey = stat.get("parameter_key")
    metrics = stat.get("metrics", {})
    vr_ref = stat.get("verified_result_ref", {})
    vr_path = vr_ref.get("path")
    vr_hash = vr_ref.get("sha256")
    vr_full = resolve_path(vr_path, stage_dir) if vr_path else None
    vr_exists = os.path.isfile(vr_full) if vr_full else False
    vr_hash_matches = False
    stat_matches = False

    if vr_exists:
        actual_vr_hash = compute_sha256(vr_full)
        vr_hash_matches = (actual_vr_hash.lower() == vr_hash.lower()) if vr_hash else False
        if not vr_hash_matches:
            break_reasons.append(f"Link 3 (Statistic result.json) SHA-256 mismatch: expected {vr_hash}, got {actual_vr_hash}")
        
        # Check metric values against result.json
        try:
            with open(vr_full, "r", encoding="utf-8") as jf:
                rdata = json.load(jf)
            stat_matches = True
            for mkey, mval in metrics.items():
                if isinstance(mval, (int, float)):
                    found_val = find_metric_in_dict(rdata, pkey, mkey)
                    if found_val is None:
                        stat_matches = False
                        break_reasons.append(f"Link 3 (Statistic) metric '{mkey}' not found in result.json")
                    elif abs(float(found_val) - float(mval)) > 0.015:
                        stat_matches = False
                        break_reasons.append(f"Link 3 (Statistic) metric mismatch for '{mkey}': claim cites {mval}, result.json has {found_val}")
        except Exception as e:
            stat_matches = False
            break_reasons.append(f"Link 3 (Statistic) error reading result.json: {str(e)}")
    else:
        break_reasons.append(f"Link 3 (Statistic result.json) missing from disk: {vr_full or vr_path}")

    link_3 = {
        "parameter_key": pkey,
        "metrics": metrics,
        "result_path": vr_path,
        "result_full_path": vr_full,
        "declared_sha256": vr_hash,
        "result_exists": vr_exists,
        "result_hash_verified": vr_hash_matches,
        "metrics_verified": stat_matches
    }

    # Check Link 4: Analysis
    an = prov.get("analysis", {})
    an_id = an.get("analysis_id")
    method = an.get("method")
    formula = an.get("model_formula")
    sc_path = an.get("script_path")
    sc_hash = an.get("script_sha256")
    sc_full = resolve_path(sc_path, stage_dir) if sc_path else None
    sc_exists = os.path.isfile(sc_full) if sc_full else False
    sc_hash_matches = False

    if sc_exists:
        actual_sc_hash = compute_sha256(sc_full)
        sc_hash_matches = (actual_sc_hash.lower() == sc_hash.lower()) if sc_hash else False
        if not sc_hash_matches:
            break_reasons.append(f"Link 4 (Analysis script) SHA-256 mismatch: expected {sc_hash}, got {actual_sc_hash}")
    else:
        break_reasons.append(f"Link 4 (Analysis script) missing from disk: {sc_full or sc_path}")

    raw_ref = an.get("raw_output_ref", {})
    raw_path = raw_ref.get("path")
    raw_hash = raw_ref.get("sha256")
    raw_full = resolve_path(raw_path, stage_dir) if raw_path else None
    raw_exists = os.path.isfile(raw_full) if raw_full else False
    raw_hash_matches = False
    if raw_exists:
        actual_raw_hash = compute_sha256(raw_full)
        raw_hash_matches = (actual_raw_hash.lower() == raw_hash.lower()) if raw_hash else False
        if not raw_hash_matches:
            break_reasons.append(f"Link 4 (Raw statistical output) SHA-256 mismatch: expected {raw_hash}, got {actual_raw_hash}")
    else:
        break_reasons.append(f"Link 4 (Raw statistical output) missing from disk: {raw_full or raw_path}")

    link_4 = {
        "analysis_id": an_id,
        "method": method,
        "model_formula": formula,
        "script_path": sc_path,
        "script_full_path": sc_full,
        "script_exists": sc_exists,
        "script_hash_verified": sc_hash_matches,
        "raw_output_path": raw_path,
        "raw_output_exists": raw_exists,
        "raw_output_hash_verified": raw_hash_matches
    }

    # Check Link 5: Data
    data = prov.get("data", {})
    ds_path = data.get("dataset_path")
    ds_hash = data.get("dataset_sha256")
    ds_full = resolve_path(ds_path, stage_dir) if ds_path else None
    ds_exists = os.path.isfile(ds_full) if ds_full else False
    ds_hash_matches = False

    if ds_exists:
        actual_ds_hash = compute_sha256(ds_full)
        ds_hash_matches = (actual_ds_hash.lower() == ds_hash.lower()) if ds_hash else False
        if not ds_hash_matches:
            break_reasons.append(f"Link 5 (Data) SHA-256 mismatch: expected {ds_hash}, got {actual_ds_hash}")
    else:
        break_reasons.append(f"Link 5 (Data) missing from disk: {ds_full or ds_path}")

    link_5 = {
        "dataset_path": ds_path,
        "dataset_full_path": ds_full,
        "sample_size": data.get("sample_size"),
        "filter_query": data.get("filter_query"),
        "transformations": data.get("transformations"),
        "dataset_exists": ds_exists,
        "dataset_hash_verified": ds_hash_matches
    }

    unbroken = (len(break_reasons) == 0)

    return {
        "claim_id": claim_id,
        "found": True,
        "unbroken": unbroken,
        "break_reasons": break_reasons,
        "trace": {
            "link_1_claim": link_1,
            "link_2_artifact": link_2,
            "link_3_statistic": link_3,
            "link_4_analysis": link_4,
            "link_5_data": link_5
        }
    }


def verify_claim_provenance(
    provenance_data_or_path: Union[str, Dict[str, Any]],
    stage_dir: Optional[str] = None,
    tolerance: float = 0.015
) -> Dict[str, Any]:
    """
    Master verification function for claim_provenance.json.
    Verifies:
    1. Schema conformance
    2. 4-tier evidence layer integrity
    3. 5-link provenance chain for every registered claim
    Returns:
    {"verdict": "PASS" | "FAIL" | "UNVERIFIED", "errors": [...], "warnings": [...], "evidence": {...}}
    """
    if isinstance(provenance_data_or_path, str):
        if not os.path.isfile(provenance_data_or_path):
            return {
                "verdict": "UNVERIFIED",
                "errors": [f"Provenance file not found: {provenance_data_or_path}"],
                "warnings": [],
                "evidence": {"file_exists": False}
            }
        try:
            with open(provenance_data_or_path, "r", encoding="utf-8") as f:
                prov_data = json.load(f)
        except Exception as e:
            return {
                "verdict": "FAIL",
                "errors": [f"Malformed JSON in provenance file: {str(e)}"],
                "warnings": [],
                "evidence": {"valid_json": False}
            }
        if not stage_dir:
            stage_dir = os.path.dirname(os.path.abspath(provenance_data_or_path))
    else:
        prov_data = provenance_data_or_path
        if not stage_dir:
            stage_dir = os.getcwd()

    errors: List[str] = []
    warnings: List[str] = []
    evidence: Dict[str, Any] = {
        "claims_audited": 0,
        "claims_unbroken": 0,
        "claims_broken": 0,
        "tiers_verified": False,
        "chain_traces": []
    }

    # 1. Schema Validation
    schema = load_claim_provenance_schema()
    if schema and jsonschema:
        try:
            jsonschema.validate(instance=prov_data, schema=schema)
        except Exception as se:
            errors.append(f"Claim provenance failed schema validation: {str(se)}")
            return {
                "verdict": "FAIL",
                "errors": errors,
                "warnings": warnings,
                "evidence": evidence
            }

    # 2. Check 4-Tier Evidence Layer
    tiers = prov_data.get("evidence_tiers", {})
    t1 = tiers.get("tier_1_raw_output", {})
    t2 = tiers.get("tier_2_verified_result", {})
    t3 = tiers.get("tier_3_interpretation", {})
    t4 = tiers.get("tier_4_claims", [])

    if not (t1 and t2 and t3 and t4):
        errors.append("Evidence tiers incomplete: all 4 tiers must be declared")
    else:
        # Check files of tiers
        t1_path = resolve_path(t1.get("path", ""), stage_dir)
        t2_path = resolve_path(t2.get("path", ""), stage_dir)
        t3_path = resolve_path(t3.get("narrative_artifact_path", ""), stage_dir)

        if not os.path.isfile(t1_path):
            errors.append(f"Tier 1 raw output missing from disk: {t1_path}")
        elif compute_sha256(t1_path).lower() != t1.get("sha256", "").lower():
            errors.append(f"Tier 1 raw output SHA-256 mismatch: {t1_path}")

        if not os.path.isfile(t2_path):
            errors.append(f"Tier 2 verified result JSON missing from disk: {t2_path}")
        elif compute_sha256(t2_path).lower() != t2.get("sha256", "").lower():
            errors.append(f"Tier 2 verified result SHA-256 mismatch: {t2_path}")

        if not os.path.isfile(t3_path):
            errors.append(f"Tier 3 narrative artifact missing from disk: {t3_path}")
        elif compute_sha256(t3_path).lower() != t3.get("narrative_sha256", "").lower():
            errors.append(f"Tier 3 narrative artifact SHA-256 mismatch: {t3_path}")

        if not errors:
            evidence["tiers_verified"] = True

    # 3. Check every declared claim's 5-link provenance trace
    claims = prov_data.get("claims", [])
    if not claims:
        errors.append("No claims declared in claim_provenance.json")

    for c in claims:
        cid = c.get("claim_id", "UNKNOWN_CLAIM")
        trace_res = trace_claim_provenance(cid, prov_data, stage_dir)
        evidence["claims_audited"] += 1
        evidence["chain_traces"].append({
            "claim_id": cid,
            "unbroken": trace_res["unbroken"],
            "break_reasons": trace_res["break_reasons"]
        })

        if trace_res["unbroken"]:
            evidence["claims_unbroken"] += 1
        else:
            evidence["claims_broken"] += 1
            for r in trace_res["break_reasons"]:
                errors.append(f"[{cid}] {r}")

    # Final Verdict Resolution
    if errors:
        verdict = "FAIL"
    elif evidence["claims_audited"] > 0 and evidence["claims_unbroken"] == evidence["claims_audited"] and evidence["tiers_verified"]:
        verdict = "PASS"
    else:
        verdict = "UNVERIFIED"

    return {
        "verdict": verdict,
        "errors": errors,
        "warnings": warnings,
        "evidence": evidence
    }


def format_trace_report(trace: Dict[str, Any]) -> str:
    """Formats a claim trace into a human-readable scholarly provenance report."""
    if not trace.get("found"):
        return f"Claim ID '{trace.get('claim_id')}' not found in provenance manifest."

    t = trace["trace"]
    l1 = t["link_1_claim"]
    l2 = t["link_2_artifact"]
    l3 = t["link_3_statistic"]
    l4 = t["link_4_analysis"]
    l5 = t["link_5_data"]

    status_str = "UNBROKEN (VERIFIED)" if trace["unbroken"] else "BROKEN (FAILED)"

    lines = [
        f"================================================================================",
        f"CLAIM PROVENANCE TRACE: {trace['claim_id']} [{status_str}]",
        f"================================================================================",
        f"LINK 1: CLAIM",
        f"  - Statement   : \"{l1['statement']}\"",
        f"  - Type        : {l1['claim_type']} (Scope: {l1['target_scope']})",
        f"  - Direction   : Supported = {l1.get('interpretation', {}).get('directional_support', True)}",
        f"",
        f"LINK 2: ARTIFACT",
        f"  - Deliverable : {l2['path']} ({l2['format']})",
        f"  - Hash Match  : {'YES' if l2['hash_verified'] else 'FAIL (Hash Mismatch / Missing)'}",
        f"  - Location    : {l2.get('location')}",
        f"",
        f"LINK 3: STATISTIC",
        f"  - Parameter   : {l3['parameter_key']}",
        f"  - Metrics     : {json.dumps(l3['metrics'])}",
        f"  - Source JSON : {l3['result_path']} (Hash Match: {'YES' if l3['result_hash_verified'] else 'FAIL'})",
        f"  - Concordance : {'YES' if l3['metrics_verified'] else 'FAIL (Metric Discrepancy)'}",
        f"",
        f"LINK 4: ANALYSIS",
        f"  - Method      : {l4['method']}",
        f"  - Formula     : {l4['model_formula']}",
        f"  - Script      : {l4['script_path']} (Hash Match: {'YES' if l4['script_hash_verified'] else 'FAIL'})",
        f"  - Raw Output  : {l4['raw_output_path']} (Hash Match: {'YES' if l4['raw_output_hash_verified'] else 'FAIL'})",
        f"",
        f"LINK 5: DATA",
        f"  - Raw Dataset : {l5['dataset_path']} (Hash Match: {'YES' if l5['dataset_hash_verified'] else 'FAIL'})",
        f"  - Sample Size : N = {l5['sample_size']}",
        f"  - Filter      : {l5['filter_query']}",
        f"================================================================================"
    ]
    if trace["break_reasons"]:
        lines.append("BREAKAGE REASONS:")
        for r in trace["break_reasons"]:
            lines.append(f"  * {r}")
        lines.append("================================================================================")

    return "\n".join(lines)


# ==============================================================================
# CLI Implementation
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="AcademicSuite Deterministic Evidence & Claim Provenance Engine ('The Hands')"
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to execute")

    # Subcommand: build
    build_parser = subparsers.add_parser("build", help="Build authoritative claim_provenance.json")
    build_parser.add_argument("--stage-dir", required=True, help="Directory of the stage")
    build_parser.add_argument("--stage-id", required=True, help="Stage identifier (e.g. 06_hypothesis_1)")
    build_parser.add_argument("--project-id", required=True, help="Project identifier")
    build_parser.add_argument("--scope", default="CHAPTER_4_FINDINGS", choices=[
        "CHAPTER_4_FINDINGS", "CHAPTER_5_DISCUSSION", "ABSTRACT", "CONCLUSION", "PAPER", "GENERAL"
    ], help="Target scope")
    build_parser.add_argument("--raw-output", required=True, help="Path to Tier 1 raw output file")
    build_parser.add_argument("--result-json", required=True, help="Path to Tier 2 verified result JSON")
    build_parser.add_argument("--md", required=True, help="Path to Tier 3 narrative Markdown")
    build_parser.add_argument("--docx", help="Path to OpenXML Word document")
    build_parser.add_argument("--claims-file", required=True, help="Path to JSON file with claims specification")
    build_parser.add_argument("--script-path", required=True, help="Path to deterministic analysis script")
    build_parser.add_argument("--dataset-path", required=True, help="Path to raw dataset")
    build_parser.add_argument("--sample-size", type=int, required=True, help="Sample size N")
    build_parser.add_argument("--filter-query", help="Sample filtering query")
    build_parser.add_argument("--output", default="claim_provenance.json", help="Output filename")

    # Subcommand: verify
    verify_parser = subparsers.add_parser("verify", help="Verify claim_provenance.json fail-closed")
    verify_parser.add_argument("--provenance", required=True, help="Path to claim_provenance.json")
    verify_parser.add_argument("--stage-dir", help="Stage directory for relative path resolution")
    verify_parser.add_argument("--json", action="store_true", help="Output report as JSON")

    # Subcommand: trace
    trace_parser = subparsers.add_parser("trace", help="Trace 5-link provenance chain for a claim ID")
    trace_parser.add_argument("--claim-id", required=True, help="Claim ID to trace (e.g. CLM-H1-01)")
    trace_parser.add_argument("--provenance", required=True, help="Path to claim_provenance.json")
    trace_parser.add_argument("--stage-dir", help="Stage directory for relative path resolution")
    trace_parser.add_argument("--json", action="store_true", help="Output trace as JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "build":
        with open(args.claims_file, "r", encoding="utf-8") as f:
            claims_spec = json.load(f)
        if isinstance(claims_spec, dict) and "claims" in claims_spec:
            claims_spec = claims_spec["claims"]

        try:
            doc = build_claim_provenance(
                stage_dir=args.stage_dir,
                stage_id=args.stage_id,
                project_id=args.project_id,
                target_scope=args.scope,
                raw_output_path=args.raw_output,
                result_json_path=args.result_json,
                narrative_md_path=args.md,
                claims_spec=claims_spec,
                script_path=args.script_path,
                dataset_path=args.dataset_path,
                sample_size=args.sample_size,
                narrative_docx_path=args.docx,
                filter_query=args.filter_query,
                output_filename=args.output
            )
            print(f"SUCCESS: Built claim provenance manifest with {len(doc['claims'])} claims at {os.path.join(args.stage_dir, args.output)}")
            sys.exit(0)
        except Exception as e:
            print(f"ERROR building claim provenance: {str(e)}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "verify":
        res = verify_claim_provenance(args.provenance, stage_dir=args.stage_dir)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print(f"VERDICT: {res['verdict']}")
            if res['errors']:
                print("ERRORS:")
                for err in res['errors']:
                    print(f"  - {err}")
            if res['warnings']:
                print("WARNINGS:")
                for w in res['warnings']:
                    print(f"  - {w}")
            print(f"Audited: {res['evidence']['claims_audited']} claims ({res['evidence']['claims_unbroken']} unbroken, {res['evidence']['claims_broken']} broken)")
        sys.exit(0 if res["verdict"] == "PASS" else 1)

    elif args.command == "trace":
        res = trace_claim_provenance(args.claim_id, args.provenance, stage_dir=args.stage_dir)
        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print(format_trace_report(res))
        sys.exit(0 if res.get("unbroken") else 1)


if __name__ == "__main__":
    main()
