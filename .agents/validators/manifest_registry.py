#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validators/manifest_registry.py — Authoritative Milestone & Stage Manifest Registry

Maintains canonical milestone, stage, and artifact type definitions.
Provides strict manifest resolution and verification rules to enforce fail-closed validation.
"""

import os
import sys
import re
import json
import hashlib
from typing import Dict, Any, List, Optional, Set, Tuple

_CURR_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(os.path.dirname(_CURR_DIR)) == ".agents":
    ROOT_DIR = os.path.abspath(os.path.join(_CURR_DIR, "..", ".."))
else:
    ROOT_DIR = os.path.abspath(os.path.join(_CURR_DIR, ".."))

AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
CONTRACTS_DIR = os.path.join(AGENTS_DIR, "contracts") if os.path.isdir(os.path.join(AGENTS_DIR, "contracts")) else os.path.join(ROOT_DIR, "contracts")

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


# ==============================================================================
# Canonical Enums & Registries
# ==============================================================================

KNOWN_MILESTONES: Set[str] = {
    "M0_INGESTION",
    "M1_PROPOSAL",
    "M2_LITERATURE_REVIEW",
    "M3_DATA_CURATION",
    "M4_DESCRIPTIVES_RELIABILITY",
    "M5_PARAMETRIC_ASSUMPTIONS",
    "M6_MODEL_DELIBERATION",
    "M7_HYPOTHESIS_TESTING",
    "M8_DISCUSSION",
    "M9_DEFENSE",
}

KNOWN_ARTIFACT_TYPES: Set[str] = {
    "data_cleaned",
    "data_quality_report",
    "stats_json",
    "narrative_markdown",
    "openxml_word",
    "presentation_deck",
    "validation_report",
    "decision_log",
    "diagram_png",
    "manifest_json",
    "claim_provenance_json",
    "interpretation_contract_json",
}

# Mapping of standard stage prefixes/slugs to milestones
STAGE_TO_MILESTONE_MAP: Dict[str, str] = {
    "00_data_curation": "M0_INGESTION",
    "01_proposal": "M1_PROPOSAL",
    "02_lit_review": "M2_LITERATURE_REVIEW",
    "01_demographics": "M3_DATA_CURATION",
    "03_data_cleaning": "M3_DATA_CURATION",
    "02_descriptives_and_reliability": "M4_DESCRIPTIVES_RELIABILITY",
    "03_parametric_assumptions": "M5_PARAMETRIC_ASSUMPTIONS",
    "03_experimental_assumptions": "M5_PARAMETRIC_ASSUMPTIONS",
    "04_bivariate_correlations": "M5_PARAMETRIC_ASSUMPTIONS",
    "05_macro_model": "M6_MODEL_DELIBERATION",
    "04_statistical_deliberation": "M6_MODEL_DELIBERATION",
    "06_hypothesis_1": "M7_HYPOTHESIS_TESTING",
    "07_hypothesis_2": "M7_HYPOTHESIS_TESTING",
    "08_hypothesis_3": "M7_HYPOTHESIS_TESTING",
    "09_chapter_summary": "M7_HYPOTHESIS_TESTING",
    "10_defense_brief": "M7_HYPOTHESIS_TESTING",
    "01_findings_recap": "M8_DISCUSSION",
    "01_defense_storyboard": "M9_DEFENSE",
    # Scale validation specialized micro-stages
    "01_content_validity": "M7_HYPOTHESIS_TESTING",
    "02_item_analysis": "M7_HYPOTHESIS_TESTING",
    "03_efa_results": "M7_HYPOTHESIS_TESTING",
    "04_cfa_results": "M7_HYPOTHESIS_TESTING",
    "05_construct_validity": "M7_HYPOTHESIS_TESTING",
    "06_reliability_inv": "M7_HYPOTHESIS_TESTING",
    "07_irt_roc": "M7_HYPOTHESIS_TESTING",
    "08_master_package": "M7_HYPOTHESIS_TESTING",
    "09_defense_brief": "M7_HYPOTHESIS_TESTING",
    "scale_validation_report": "M7_HYPOTHESIS_TESTING",
    # Specialized analysis stages
    "05_mediation_macro": "M7_HYPOTHESIS_TESTING",
    "05_moderation_macro": "M7_HYPOTHESIS_TESTING",
}

# Recognized canonical stage prefixes / pattern matchers
KNOWN_STAGE_PATTERNS = [
    r"^00_data_curation.*",
    r"^01_proposal.*",
    r"^02_lit_review.*",
    r"^01_demographics.*",
    r"^03_data_cleaning.*",
    r"^02_descriptives_and_reliability.*",
    r"^03_parametric_assumptions.*",
    r"^03_experimental_assumptions.*",
    r"^04_bivariate_correlations.*",
    r"^04_statistical_deliberation.*",
    r"^05_macro_model.*",
    r"^05_mediation_macro.*",
    r"^05_moderation_macro.*",
    r"^06_hypothesis_1.*",
    r"^07_hypothesis_2.*",
    r"^08_hypothesis_3.*",
    r"^09_chapter_summary.*",
    r"^10_defense_brief.*",
    r"^01_findings_recap.*",
    r"^01_defense_storyboard.*",
    r"^01_content_validity.*",
    r"^02_item_analysis.*",
    r"^03_efa_results.*",
    r"^04_cfa_results.*",
    r"^05_construct_validity.*",
    r"^06_reliability_inv.*",
    r"^07_irt_roc.*",
    r"^08_master_package.*",
    r"^09_defense_brief.*",
    r"^scale_validation_report.*",
]


# ==============================================================================
# Helper Functions: Known Entities
# ==============================================================================

def is_known_milestone(milestone_id: str) -> bool:
    """Verifies whether a milestone identifier is canonically registered."""
    return milestone_id in KNOWN_MILESTONES


def is_known_artifact_type(artifact_type: str) -> bool:
    """Verifies whether an artifact type is canonically registered."""
    return artifact_type in KNOWN_ARTIFACT_TYPES


def is_known_stage(stage_id: str) -> bool:
    """Verifies whether a stage identifier matches any canonical stage pattern."""
    if not stage_id or not isinstance(stage_id, str):
        return False
    norm = stage_id.strip().lower()
    if norm in STAGE_TO_MILESTONE_MAP:
        return True
    for pat in KNOWN_STAGE_PATTERNS:
        if re.match(pat, norm):
            return True
    return False


def resolve_stage_from_filename(filename: str) -> Optional[str]:
    """Extracts and normalizes the stage ID from a filename."""
    base = os.path.basename(filename)
    stem = os.path.splitext(base)[0].lower()
    for prefix in sorted(STAGE_TO_MILESTONE_MAP.keys(), key=len, reverse=True):
        if stem.startswith(prefix) or stem == prefix:
            return stem
    for pat in KNOWN_STAGE_PATTERNS:
        if re.match(pat, stem):
            return stem
    return None


# ==============================================================================
# Authoritative Artifact Requirements
# ==============================================================================

def get_required_artifacts_for_stage(stage_stem: str) -> List[Dict[str, Any]]:
    """
    Returns the authoritative list of required artifact specifications for a stage.
    Every hypothesis and finding stage enforces the Triad Artifact Invariant (.json, .md, .docx).
    """
    norm = stage_stem.strip().lower()

    # Assembled Master Deliverables (DOCX + MD, JSON resides in micro-stages)
    if "scale_validation_report" in norm or "chapter_" in norm or "master_package" in norm:
        return [
            {
                "artifact_id": f"ART-{norm.upper()}-MD",
                "type": "narrative_markdown",
                "extension": ".md",
                "filename_pattern": f"{norm}.md",
                "required": True,
                "schema": "",
                "description": f"Assembled master Markdown deliverable for {norm}"
            },
            {
                "artifact_id": f"ART-{norm.upper()}-DOCX",
                "type": "openxml_word",
                "extension": ".docx",
                "filename_pattern": f"{norm}.docx",
                "required": True,
                "schema": "",
                "description": f"Assembled master OpenXML Word deliverable for {norm}"
            }
        ]

    # Hypothesis, Findings, or Scale Validation Micro-Stages -> TRIAD INVARIANT
    triad_stages = [
        "hypothesis", "macro_model", "mediation_macro", "moderation_macro",
        "demographics", "descriptives", "assumptions", "bivariate", "summary",
        "brief", "content_validity", "item_analysis", "efa_results", "cfa_results",
        "construct_validity", "reliability_inv", "irt_roc"
    ]

    is_triad = any(k in norm for k in triad_stages) or re.match(r"^\d\d_.*", norm)

    if is_triad:
        return [
            {
                "artifact_id": f"ART-{norm.upper()}-JSON",
                "type": "stats_json",
                "extension": ".json",
                "filename_pattern": f"{norm}.json",
                "required": True,
                "schema": "stats_results.schema.json",
                "description": f"Structured numerical statistical parameters for {norm}"
            },
            {
                "artifact_id": f"ART-{norm.upper()}-MD",
                "type": "narrative_markdown",
                "extension": ".md",
                "filename_pattern": f"{norm}.md",
                "required": True,
                "schema": "",
                "description": f"Scholarly narrative and APA 7 Markdown tables for {norm}"
            },
            {
                "artifact_id": f"ART-{norm.upper()}-DOCX",
                "type": "openxml_word",
                "extension": ".docx",
                "filename_pattern": f"{norm}.docx",
                "required": True,
                "schema": "",
                "description": f"Institutional OpenXML Word document for {norm}"
            }
        ]

    # Deliberation stage
    if "deliberation" in norm:
        return [
            {
                "artifact_id": "ART-DELIBERATION-PLAN",
                "type": "decision_log",
                "extension": ".json",
                "filename_pattern": "analysis_plan.json",
                "required": True,
                "schema": "analysis_plan.schema.json",
                "description": "Synthesized and validated analysis plan artifact"
            }
        ]

    # Ingestion stage
    if "ingestion" in norm or "curation" in norm:
        return [
            {
                "artifact_id": "ART-DATA-QUALITY-REPORT",
                "type": "data_quality_report",
                "extension": ".json",
                "filename_pattern": f"{norm}.json",
                "required": True,
                "schema": "data_quality.schema.json",
                "description": "Data audit, missingness, and outlier screening report"
            },
            {
                "artifact_id": "ART-DATA-CURATION-MD",
                "type": "narrative_markdown",
                "extension": ".md",
                "filename_pattern": f"{norm}.md",
                "required": True,
                "schema": "",
                "description": "Data curation narrative documentation"
            },
            {
                "artifact_id": "ART-DATA-CURATION-DOCX",
                "type": "openxml_word",
                "extension": ".docx",
                "filename_pattern": f"{norm}.docx",
                "required": True,
                "schema": "",
                "description": "OpenXML Word data curation chapter section"
            }
        ]

    # Fallback to Triad for any other recognized stage
    return [
        {
            "artifact_id": f"ART-{norm.upper()}-JSON",
            "type": "stats_json",
            "extension": ".json",
            "filename_pattern": f"{norm}.json",
            "required": True,
            "schema": "",
            "description": f"Numerical data for {norm}"
        },
        {
            "artifact_id": f"ART-{norm.upper()}-MD",
            "type": "narrative_markdown",
            "extension": ".md",
            "filename_pattern": f"{norm}.md",
            "required": True,
            "schema": "",
            "description": f"Markdown narrative for {norm}"
        },
        {
            "artifact_id": f"ART-{norm.upper()}-DOCX",
            "type": "openxml_word",
            "extension": ".docx",
            "filename_pattern": f"{norm}.docx",
            "required": True,
            "schema": "",
            "description": f"OpenXML Word document for {norm}"
        }
    ]


# ==============================================================================
# Artifact Manifest Verification Engine
# ==============================================================================

def compute_sha256(filepath: str) -> str:
    """Computes SHA-256 hash of a file on disk."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_manifest_entry(
    entry: Dict[str, Any],
    base_dir: str
) -> Dict[str, Any]:
    """
    Verifies a single artifact manifest entry:
    - existence
    - type validity
    - schema
    - producer
    - hash / provenance
    - dependencies
    """
    errors = []
    warnings = []
    status = "PASS"

    art_id = entry.get("artifact_id", "UNKNOWN_ART")
    art_type = entry.get("type", "")
    art_path = entry.get("path", "")

    # 1. Type validation
    if not is_known_artifact_type(art_type):
        errors.append(f"Artifact '{art_id}' specifies unknown artifact type: '{art_type}'.")
        return {
            "artifact_id": art_id,
            "verdict": "BLOCKED",
            "status": "BLOCKED",
            "errors": errors,
            "warnings": warnings,
            "checked_path": art_path
        }

    # 2. Existence validation
    full_path = art_path if os.path.isabs(art_path) else os.path.join(base_dir, art_path)
    if not os.path.exists(full_path):
        errors.append(f"Required artifact '{art_id}' missing from disk: {full_path}")
        return {
            "artifact_id": art_id,
            "verdict": "BLOCKED",
            "status": "BLOCKED",
            "errors": errors,
            "warnings": warnings,
            "checked_path": full_path
        }

    # Check non-empty
    if os.path.getsize(full_path) == 0:
        errors.append(f"Artifact '{art_id}' exists but is 0 bytes (empty): {full_path}")
        return {
            "artifact_id": art_id,
            "verdict": "FAIL",
            "status": "FAIL",
            "errors": errors,
            "warnings": warnings,
            "checked_path": full_path
        }

    # 3. Hash validation where applicable
    expected_hash = entry.get("hash")
    expected_hash_val = None
    if isinstance(expected_hash, dict):
        expected_hash_val = expected_hash.get("value")
    elif isinstance(expected_hash, str) and expected_hash:
        expected_hash_val = expected_hash

    if expected_hash_val:
        actual_hash = compute_sha256(full_path)
        if actual_hash.lower() != expected_hash_val.lower():
            errors.append(
                f"Cryptographic hash mismatch for artifact '{art_id}': "
                f"manifest={expected_hash_val}, disk={actual_hash}"
            )
            status = "FAIL"

    # 4. Schema validation for JSON artifacts
    schema_spec = entry.get("schema")
    if schema_spec and full_path.endswith(".json"):
        try:
            with open(full_path, "r", encoding="utf-8") as jf:
                instance = json.load(jf)

            schema_file = schema_spec if schema_spec.endswith(".json") else f"{schema_spec}.schema.json"
            schema_path = os.path.join(CONTRACTS_DIR, schema_file)
            if not os.path.exists(schema_path):
                schema_path = os.path.join(CONTRACTS_DIR, schema_spec)

            if os.path.exists(schema_path) and jsonschema:
                with open(schema_path, "r", encoding="utf-8") as sf:
                    schema_data = json.load(sf)
                jsonschema.validate(instance=instance, schema=schema_data)
            elif not os.path.exists(schema_path):
                warnings.append(f"Schema file not found on disk for '{schema_spec}': {schema_path}")
        except json.JSONDecodeError as jde:
            errors.append(f"Malformed JSON in artifact '{art_id}': {str(jde)}")
            status = "FAIL"
        except Exception as se:
            if jsonschema and isinstance(se, jsonschema.ValidationError):
                errors.append(f"Schema validation failed for artifact '{art_id}': {se.message}")
                status = "FAIL"
            else:
                errors.append(f"Error validating schema for artifact '{art_id}': {str(se)}")
                status = "FAIL"

    # 5. Producer verification
    producer = entry.get("producer")
    if producer is not None:
        if not isinstance(producer, dict) or "agent" not in producer:
            errors.append(f"Artifact '{art_id}' producer must be an object specifying 'agent'.")
            status = "FAIL"

    # 6. Dependencies verification
    deps = entry.get("dependencies", [])
    for dep in deps:
        if isinstance(dep, dict):
            dep_path = dep.get("path")
            if dep_path:
                full_dep = dep_path if os.path.isabs(dep_path) else os.path.join(base_dir, dep_path)
                if not os.path.exists(full_dep):
                    errors.append(f"Declared dependency missing for '{art_id}': {full_dep}")
                    status = "BLOCKED"
                elif dep.get("hash_at_consumption"):
                    actual_dep_hash = compute_sha256(full_dep)
                    if actual_dep_hash.lower() != dep["hash_at_consumption"].lower():
                        errors.append(
                            f"Dependency hash mismatch for '{art_id}' dependency '{dep.get('artifact_id', dep_path)}': "
                            f"expected={dep['hash_at_consumption']}, actual={actual_dep_hash}"
                        )
                        status = "FAIL"

    verdict = "FAIL" if any("mismatch" in e or "Schema" in e or "Malformed" in e or "empty" in e for e in errors) else (
        "BLOCKED" if errors else ("NEEDS_REVIEW" if warnings else "PASS")
    )

    return {
        "artifact_id": art_id,
        "verdict": verdict,
        "status": verdict,
        "errors": errors,
        "warnings": warnings,
        "checked_path": full_path
    }
