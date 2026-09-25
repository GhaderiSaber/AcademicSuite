#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/integrity_hooks.py — Class B: Integrity Hooks

Enforces artifact contracts, state machine consistency, and validation gating:
1. Artifact verification: Triad Artifact Invariant (.docx, .md, .json) and skill modularity ceilings.
2. State consistency: Prevents illegal transitions and unapproved state mutations.
3. Manifest verification: Ensures completed stages possess authoritative manifest.json matching disk files.
4. Post-analysis validation: Ensures validation reports evaluate to PASS before turn completion.
5. Epistemic honesty & compliance: Enforces Binary Honesty Protocol and Multi-Agent Truthfulness (Directive 0).

INVARIANT: Hooks are purely for interception, safety, and enforcement.
Hooks must NEVER act as the academic orchestrator.
"""

import os
import sys
import re
import glob
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from contracts.hook_identity_contract import resolve_transcript_path
except ImportError:
    try:
        from .contracts.hook_identity_contract import resolve_transcript_path
    except ImportError:
        def resolve_transcript_path(payload):
            return payload.get("transcriptPath") if isinstance(payload, dict) else None


def load_transcript(transcript_path: Optional[str]) -> List[Dict[str, Any]]:
    """Loads and parses transcript safely, preferring untruncated transcript_full.jsonl if present."""
    if not transcript_path:
        return []
    target_path = transcript_path
    if os.path.basename(transcript_path) == "transcript.jsonl":
        full_candidate = os.path.join(os.path.dirname(transcript_path), "transcript_full.jsonl")
        if os.path.isfile(full_candidate) and os.path.getsize(full_candidate) > 0:
            target_path = full_candidate
    if not os.path.exists(target_path):
        target_path = transcript_path
    if not os.path.exists(target_path):
        return []
    records = []
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    except Exception as e:
        sys.stderr.write(f"[integrity_hooks] Error reading transcript ({target_path}): {e}\n")
        if target_path != transcript_path and os.path.exists(transcript_path):
            try:
                with open(transcript_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            records.append(json.loads(line))
            except Exception:
                pass
    return records


class IntegrityHooks:
    """
    Class B: Integrity Hooks
    Responsible for enforcing artifact invariants, manifest validation, state consistency,
    and post-analysis validation reports without acting as an orchestrator.
    """

    @staticmethod
    def verify_artifacts(workspaces: List[str]) -> Tuple[bool, str]:
        """
        Enforces Triad Artifact Invariant (.docx, .md, .json) across active stage directories.
        """
        active_stage_dirs = []
        for ws in workspaces:
            for rel_root in ("projects", "03_deliverables", "."):
                p_dir = os.path.join(ws, rel_root)
                if os.path.exists(p_dir):
                    for root, dirs, files in os.walk(p_dir):
                        if any(re.search(r'^(?:\d+_)?[a-zA-Z0-9_-]+\.(?:docx|md|json)$', f) for f in files):
                            if any(re.search(r'(?:hypothesis|demographic|descriptive|assumption|correlation|model|curation|deliverable)', f, re.I) for f in files):
                                active_stage_dirs.append(root)

        for s_dir in set(active_stage_dirs):
            files = os.listdir(s_dir)
            stage_prefixes = set()
            for f in files:
                m = re.match(r'^(\d+_[a-zA-Z0-9_-]+)\.(?:docx|md|json)$', f)
                if m:
                    stage_prefixes.add(m.group(1))

            for pfx in stage_prefixes:
                has_docx = f"{pfx}.docx" in files
                has_md = f"{pfx}.md" in files
                has_json = f"{pfx}.json" in files
                missing = []
                if not has_docx: missing.append(f"{pfx}.docx")
                if not has_md: missing.append(f"{pfx}.md")
                if not has_json: missing.append(f"{pfx}.json")
                if missing and (has_docx or has_md or has_json):
                    return False, (
                        f"HARD HOOK ENFORCEMENT (Directive 3 - Triad Artifact Invariant): "
                        f"Stage '{pfx}' in '{s_dir}' has incomplete physical artifacts. Missing: {missing}. "
                        f"Every stage and individual hypothesis must generate a synchronized triad: .docx, .md, and .json."
                    )
        return True, ""

    @staticmethod
    def verify_manifests(workspaces: List[str]) -> Tuple[bool, str]:
        """
        Verifies that any stage with an authoritative manifest.json is consistent with disk deliverables.
        Fails closed on any parse error, non-dict content, or missing/empty artifacts.
        """
        for ws in workspaces:
            for root, dirs, files in os.walk(ws):
                if "manifest.json" in files:
                    m_path = os.path.join(root, "manifest.json")
                    try:
                        with open(m_path, "r", encoding="utf-8") as mf:
                            m_data = json.load(mf)
                    except Exception as e:
                        return False, f"HARD HOOK ENFORCEMENT (Manifest Verification): Failed to parse {m_path}: {e}. Verification failed closed."
                    if not isinstance(m_data, dict):
                        return False, (
                            f"HARD HOOK ENFORCEMENT (Manifest Verification): Manifest '{m_path}' "
                            f"must be a JSON object, got {type(m_data).__name__}. Verification failed closed."
                        )
                    # Check schema title / contract_version
                    if m_data.get("contract_version") and "artifacts" in m_data:
                        # Verify declared artifacts exist on disk
                        base_dir = root
                        artifacts = m_data.get("artifacts", [])
                        if not isinstance(artifacts, list):
                            return False, (
                                f"HARD HOOK ENFORCEMENT (Manifest Verification): Field 'artifacts' "
                                f"in manifest '{m_path}' must be a list. Verification failed closed."
                            )
                        for art in artifacts:
                            if not isinstance(art, dict):
                                return False, (
                                    f"HARD HOOK ENFORCEMENT (Manifest Verification): Artifact entry "
                                    f"in manifest '{m_path}' must be a JSON object. Verification failed closed."
                                )
                            a_path = art.get("path", "")
                            a_full = a_path if os.path.isabs(a_path) else os.path.join(base_dir, a_path)
                            if not os.path.exists(a_full) or os.path.getsize(a_full) == 0:
                                return False, (
                                    f"HARD HOOK ENFORCEMENT (Manifest Verification): Stage in '{root}' declares "
                                    f"artifact '{a_path}' in manifest.json, but it is missing or empty on disk."
                                )
        return True, ""

    @staticmethod
    def verify_missing_artifacts(workspaces: List[str]) -> Tuple[bool, str]:
        """
        Secondary Enforcement (Missing Artifact Guard):
        Detects missing artifacts across active stage directories and authoritative manifests.
        1. Checks Triad Artifact Invariant (.docx, .md, .json).
        2. Checks declared manifest deliverables exist and have non-zero size.
        """
        ok_triad, reason_triad = IntegrityHooks.verify_artifacts(workspaces)
        if not ok_triad:
            return False, reason_triad

        ok_manifest, reason_manifest = IntegrityHooks.verify_manifests(workspaces)
        if not ok_manifest:
            return False, reason_manifest

        return True, ""

    @staticmethod
    def verify_state_transitions(workspaces: List[str]) -> Tuple[bool, str]:
        """
        Secondary Enforcement (Invalid State Transition Guard):
        Detects invalid state transitions in workspace state directories.
        Validates that stage state records in current_state.json or events.jsonl obey
        STAGE_LEGAL_TRANSITIONS and explicit human approval gates.
        Fails closed on any malformed JSON, corrupted ledger, non-dict state, or illegal transition.
        """
        legal_transitions = {
            "STAGE_LOCKED": {"STAGE_READY", "STAGE_BLOCKED"},
            "STAGE_READY": {"STAGE_RUNNING", "STAGE_BLOCKED"},
            "STAGE_RUNNING": {"STAGE_VALIDATING", "STAGE_FAILED", "STAGE_BLOCKED"},
            "STAGE_VALIDATING": {"STAGE_AWAITING_APPROVAL", "STAGE_FAILED", "STAGE_BLOCKED"},
            "STAGE_AWAITING_APPROVAL": {"STAGE_APPROVED", "STAGE_REJECTED"},
            "STAGE_APPROVED": {"STAGE_RUNNING", "NEXT_STAGE"},  # Explicit iteration or advance to NEXT_STAGE
            "STAGE_REJECTED": {"STAGE_READY", "STAGE_LOCKED"},
            "STAGE_FAILED": {"STAGE_READY", "STAGE_BLOCKED"},
            "STAGE_BLOCKED": {"STAGE_READY", "STAGE_LOCKED"},
            "NEXT_STAGE": set(),
        }

        for ws in workspaces:
            for root, dirs, files in os.walk(ws):
                if "current_state.json" in files:
                    cs_path = os.path.join(root, "current_state.json")
                    try:
                        with open(cs_path, "r", encoding="utf-8") as f:
                            cs = json.load(f)
                    except Exception as e:
                        return False, (
                            f"HARD HOOK ENFORCEMENT (Invalid State Transition Guard): "
                            f"State ledger '{cs_path}' is malformed or unreadable: {e}. "
                            f"Verification failed closed."
                        )
                    if not isinstance(cs, dict):
                        return False, (
                            f"HARD HOOK ENFORCEMENT (Invalid State Transition Guard): "
                            f"State ledger '{cs_path}' must be a JSON object, got {type(cs).__name__}. "
                            f"Verification failed closed."
                        )

                    stages = cs.get("stages", {})
                    if not isinstance(stages, dict):
                        return False, (
                            f"HARD HOOK ENFORCEMENT (Invalid State Transition Guard): "
                            f"Field 'stages' in '{cs_path}' must be a JSON object, got {type(stages).__name__}. "
                            f"Verification failed closed."
                        )

                    approvals = []
                    appr_path = os.path.join(root, "approvals.json")
                    if os.path.exists(appr_path):
                        try:
                            with open(appr_path, "r", encoding="utf-8") as af:
                                appr_data = json.load(af)
                        except Exception as e:
                            return False, (
                                f"HARD HOOK ENFORCEMENT (Invalid State Transition Guard): "
                                f"Approvals ledger '{appr_path}' is malformed or unreadable: {e}. "
                                f"Verification failed closed."
                            )
                        if not isinstance(appr_data, dict):
                            return False, (
                                f"HARD HOOK ENFORCEMENT (Invalid State Transition Guard): "
                                f"Approvals ledger '{appr_path}' must be a JSON object, got {type(appr_data).__name__}. "
                                f"Verification failed closed."
                            )
                        approvals = appr_data.get("approvals", [])
                        if not isinstance(approvals, list):
                            return False, (
                                f"HARD HOOK ENFORCEMENT (Invalid State Transition Guard): "
                                f"Field 'approvals' in '{appr_path}' must be a list. "
                                f"Verification failed closed."
                            )

                    for stage_id, sdata in stages.items():
                        if not isinstance(sdata, dict):
                            return False, (
                                f"HARD HOOK ENFORCEMENT (Invalid State Transition Guard): "
                                f"Stage '{stage_id}' in '{cs_path}' must be a JSON object, got {type(sdata).__name__}. "
                                f"Verification failed closed."
                            )
                        history = sdata.get("history", [])
                        if not isinstance(history, list):
                            return False, (
                                f"HARD HOOK ENFORCEMENT (Invalid State Transition Guard): "
                                f"History for stage '{stage_id}' in '{cs_path}' must be a list. "
                                f"Verification failed closed."
                            )
                        for trn in history:
                            if not isinstance(trn, dict):
                                return False, (
                                    f"HARD HOOK ENFORCEMENT (Invalid State Transition Guard): "
                                    f"Transition entry in stage '{stage_id}' history in '{cs_path}' must be a JSON object. "
                                    f"Verification failed closed."
                                )
                            from_st = trn.get("from_state")
                            to_st = trn.get("to_state")
                            if from_st and to_st:
                                from_st_str = str(from_st).upper()
                                to_st_str = str(to_st).upper()
                                allowed = legal_transitions.get(from_st_str, set())
                                if to_st_str not in allowed:
                                    return False, (
                                        f"HARD HOOK ENFORCEMENT (Invalid State Transition Guard): "
                                        f"Stage '{stage_id}' in '{root}' recorded an illegal transition "
                                        f"from '{from_st_str}' to '{to_st_str}'. "
                                        f"Allowed transitions from {from_st_str}: {sorted(list(allowed))}."
                                    )

                        # Check unapproved STAGE_APPROVED
                        curr_status = str(sdata.get("status", "")).upper()
                        if curr_status == "STAGE_APPROVED" and os.path.exists(appr_path):
                            has_appr = any(
                                (a.get("stage_id") == stage_id or a.get("target_id") == stage_id)
                                for a in approvals if isinstance(a, dict)
                            )
                            if not has_appr:
                                return False, (
                                    f"HARD HOOK ENFORCEMENT (Invalid State Transition Guard): "
                                    f"Stage '{stage_id}' in '{root}' is marked 'STAGE_APPROVED' but lacks an "
                                    f"authoritative approval record in approvals.json. Explicit human approval is required."
                                )
        return True, ""

    @staticmethod
    def verify_worker_returns(workspaces: List[str]) -> Tuple[bool, str]:
        """
        Secondary Enforcement (Worker Return Invariant Guard - Phase 21):
        Verifies that worker subagent returns recorded in state or handoffs contain:
        artifact, evidence, status, validation (not simply 'done').
        """
        try:
            from validators.worker_return_validator import validate_worker_return_payload
        except ImportError:
            try:
                from worker_return_validator import validate_worker_return_payload
            except ImportError:
                validate_worker_return_payload = None

        if validate_worker_return_payload is None:
            return True, ""

        for ws in workspaces:
            for root, dirs, files in os.walk(ws):
                if "current_state.json" in files:
                    cs_path = os.path.join(root, "current_state.json")
                    try:
                        with open(cs_path, "r", encoding="utf-8") as f:
                            cs = json.load(f)
                    except Exception as e:
                        return False, (
                            f"HARD HOOK ENFORCEMENT (Worker Return Invariant Guard - Phase 21): "
                            f"State ledger '{cs_path}' is malformed or unreadable: {e}. "
                            f"Verification failed closed."
                        )
                    if not isinstance(cs, dict):
                        return False, (
                            f"HARD HOOK ENFORCEMENT (Worker Return Invariant Guard - Phase 21): "
                            f"State ledger '{cs_path}' must be a JSON object, got {type(cs).__name__}. "
                            f"Verification failed closed."
                        )
                    stages = cs.get("stages", {})
                    if not isinstance(stages, dict):
                        return False, (
                            f"HARD HOOK ENFORCEMENT (Worker Return Invariant Guard - Phase 21): "
                            f"Field 'stages' in '{cs_path}' must be a JSON object, got {type(stages).__name__}. "
                            f"Verification failed closed."
                        )
                    for stage_id, sdata in stages.items():
                        if not isinstance(sdata, dict):
                            return False, (
                                f"HARD HOOK ENFORCEMENT (Worker Return Invariant Guard - Phase 21): "
                                f"Stage '{stage_id}' in '{cs_path}' must be a JSON object, got {type(sdata).__name__}. "
                                f"Verification failed closed."
                            )
                        w_ret = sdata.get("worker_return")
                        if w_ret is not None:
                            try:
                                val_res = validate_worker_return_payload(w_ret)
                            except Exception as e:
                                return False, (
                                    f"HARD HOOK ENFORCEMENT (Worker Return Invariant Guard - Phase 21): "
                                    f"Stage '{stage_id}' in '{root}' worker return validation error: {e}. "
                                    f"Verification failed closed."
                                )
                            if not isinstance(val_res, dict) or not val_res.get("valid"):
                                err_msg = "; ".join(val_res.get("errors", ["Invalid worker return"])) if isinstance(val_res, dict) else "Unknown validation failure"
                                return False, (
                                    f"HARD HOOK ENFORCEMENT (Worker Return Invariant Guard - Phase 21): "
                                    f"Stage '{stage_id}' in '{root}' recorded an invalid worker return: {err_msg}"
                                )
                        history = sdata.get("history", [])
                        if not isinstance(history, list):
                            return False, (
                                f"HARD HOOK ENFORCEMENT (Worker Return Invariant Guard - Phase 21): "
                                f"History for stage '{stage_id}' in '{cs_path}' must be a list. "
                                f"Verification failed closed."
                            )
                        for trn in history:
                            if isinstance(trn, dict) and "worker_return" in trn:
                                hw_ret = trn["worker_return"]
                                try:
                                    val_res = validate_worker_return_payload(hw_ret)
                                except Exception as e:
                                    return False, (
                                        f"HARD HOOK ENFORCEMENT (Worker Return Invariant Guard - Phase 21): "
                                        f"Stage '{stage_id}' in '{root}' history worker return error: {e}. "
                                        f"Verification failed closed."
                                    )
                                if not isinstance(val_res, dict) or not val_res.get("valid"):
                                    err_msg = "; ".join(val_res.get("errors", ["Invalid worker return"])) if isinstance(val_res, dict) else "Unknown validation failure"
                                    return False, (
                                        f"HARD HOOK ENFORCEMENT (Worker Return Invariant Guard - Phase 21): "
                                        f"Stage '{stage_id}' in '{root}' history recorded an invalid worker return: {err_msg}"
                                    )
        return True, ""

    @staticmethod
    def verify_provenance(workspaces: List[str]) -> Tuple[bool, str]:
        """
        Secondary Enforcement (Invalid Provenance Guard):
        Detects invalid provenance across manifests, deliverables, and dependencies.
        Verifies input SHA-256 integrity, deliverable SHA-256 hash match, and dependency manifest hashes.
        """
        def compute_file_sha256(filepath: str) -> str:
            h = hashlib.sha256()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
            return h.hexdigest()

        for ws in workspaces:
            for root, dirs, files in os.walk(ws):
                if "manifest.json" in files:
                    m_path = os.path.join(root, "manifest.json")
                    try:
                        with open(m_path, "r", encoding="utf-8") as mf:
                            m_data = json.load(mf)
                    except Exception as e:
                        return False, (
                            f"HARD HOOK ENFORCEMENT (Invalid Provenance Guard): "
                            f"Manifest '{m_path}' is malformed or unreadable: {e}. "
                            f"Verification failed closed."
                        )
                    if not isinstance(m_data, dict):
                        return False, (
                            f"HARD HOOK ENFORCEMENT (Invalid Provenance Guard): "
                            f"Manifest '{m_path}' must be a JSON object, got {type(m_data).__name__}. "
                            f"Verification failed closed."
                        )

                    base_dir = root
                    stage_id = m_data.get("stage_id", os.path.basename(root))

                    try:
                        # 1. Inputs provenance verification
                        for inp in m_data.get("inputs", []):
                            if isinstance(inp, dict):
                                inp_rel = inp.get("path", "")
                                expected_hash = inp.get("sha256", "")
                                if inp_rel and expected_hash:
                                    inp_full = inp_rel if os.path.isabs(inp_rel) else os.path.join(base_dir, inp_rel)
                                    if not os.path.exists(inp_full):
                                        alt = os.path.join(ROOT_DIR, inp_rel)
                                        if os.path.exists(alt):
                                            inp_full = alt
                                    if os.path.exists(inp_full) and os.path.isfile(inp_full):
                                        actual_hash = compute_file_sha256(inp_full)
                                        if actual_hash.lower() != expected_hash.lower():
                                            return False, (
                                                f"HARD HOOK ENFORCEMENT (Invalid Provenance Guard): "
                                                f"Input artifact '{inp_rel}' declared in manifest for stage '{stage_id}' "
                                                f"hash mismatch. Expected {expected_hash}, got {actual_hash}. "
                                                f"Input data was mutated after stage declaration."
                                            )

                        # 2. Deliverable hashes verification
                        hashes = m_data.get("hashes", {})
                        if isinstance(hashes, dict):
                            for art_rel, expected_hash in hashes.items():
                                art_full = art_rel if os.path.isabs(art_rel) else os.path.join(base_dir, art_rel)
                                if not os.path.exists(art_full):
                                    alt = os.path.join(ROOT_DIR, art_rel)
                                    if os.path.exists(alt):
                                        art_full = alt
                                if os.path.exists(art_full) and os.path.isfile(art_full):
                                    actual_hash = compute_file_sha256(art_full)
                                    if actual_hash.lower() != expected_hash.lower():
                                        return False, (
                                            f"HARD HOOK ENFORCEMENT (Invalid Provenance Guard): "
                                            f"Deliverable artifact '{art_rel}' in stage '{stage_id}' "
                                            f"hash mismatch. Expected {expected_hash}, got {actual_hash}. "
                                            f"Artifact was mutated outside the declared generator."
                                        )

                        # 3. Dependencies manifest hash verification
                        for dep in m_data.get("dependencies", []):
                            if isinstance(dep, dict):
                                dep_stage = dep.get("stage_id", "")
                                dep_manifest_path = dep.get("manifest_path", "")
                                expected_dep_hash = dep.get("manifest_hash", "")
                                if dep_manifest_path and expected_dep_hash:
                                    dep_full = dep_manifest_path if os.path.isabs(dep_manifest_path) else os.path.join(base_dir, dep_manifest_path)
                                    if not os.path.exists(dep_full):
                                        alt = os.path.join(ROOT_DIR, dep_manifest_path)
                                        if os.path.exists(alt):
                                            dep_full = alt
                                    if os.path.exists(dep_full) and os.path.isfile(dep_full):
                                        actual_dep_hash = compute_file_sha256(dep_full)
                                        if actual_dep_hash.lower() != expected_dep_hash.lower():
                                            return False, (
                                                f"HARD HOOK ENFORCEMENT (Invalid Provenance Guard): "
                                                f"Dependency manifest for stage '{dep_stage}' hash mismatch. "
                                                f"Expected {expected_dep_hash}, got {actual_dep_hash}."
                                            )
                    except Exception as e:
                        return False, (
                            f"HARD HOOK ENFORCEMENT (Invalid Provenance Guard): "
                            f"Provenance verification failed in '{m_path}': {e}. "
                            f"Verification failed closed."
                        )
        return True, ""

    @staticmethod
    def verify_skill_modularity(workspaces: List[str]) -> Tuple[bool, str]:
        """
        Enforces Directive 18 (Skill Modularity Standard: max 500 lines, 40,000 bytes).
        """
        check_dirs = [os.path.join(ws, ".agents", "skills") for ws in workspaces]
        default_skills_dir = os.path.abspath(os.path.join(ROOT_DIR, ".agents", "skills"))
        if default_skills_dir not in check_dirs and os.path.exists(default_skills_dir):
            check_dirs.append(default_skills_dir)

        for s_dir in check_dirs:
            if os.path.exists(s_dir):
                guard_path = os.path.join(ROOT_DIR, ".agents", "verification", "skill_size_guard.py")
                if os.path.exists(guard_path):
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("skill_size_guard", guard_path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    res = mod.audit_skill_sizes(s_dir)
                    if not res.get("passed", True):
                        violation_details = "; ".join(
                            [f"{v.get('name', v.get('skill', 'unknown'))} ({v.get('line_count', '?')} lines, {v.get('byte_size', '?')} bytes)" for v in res["violations"]]
                        )
                        return False, (
                            f"CONSTITUTIONAL VIOLATION (Directive 18 - Skill Modularity Standard): "
                            f"The following skill(s) exceed single-view limits (max 500 lines, 40,000 bytes): "
                            f"{violation_details}. Modularize extended guidelines into 'references/' before proceeding."
                        )
        return True, ""

    @staticmethod
    def verify_post_analysis(workspaces: List[str]) -> Tuple[bool, str]:
        """
        Secondary Enforcement (Post-Analysis Validation Gate):
        Enforces Directive 22 (Fail-Closed Mechanical Validation Gate Invariant):
        PASS + checks_failed == 0 -> accept
        Everything else            -> reject (fail closed).

        A validation report is ONLY accepted if:
        1. It is a valid, readable JSON object.
        2. overall_verdict is strictly "PASS" (not FAIL, UNKNOWN, BLOCKED, INCOMPLETE, UNVERIFIED, missing, or empty).
        3. checks_failed is explicitly present (in evidence_summary or top-level) and equal to 0.
        4. checks_blocked is 0 (if present in evidence_summary).
        5. failed_checks list is empty (if present).
        6. All individual check results are PASS or SKIP (if results list is present).
        """
        active_stage_dirs = []
        for ws in workspaces:
            for rel_root in ("projects", "03_deliverables", "."):
                p_dir = os.path.join(ws, rel_root)
                if os.path.exists(p_dir):
                    for root, dirs, files in os.walk(p_dir):
                        if "validation_report.json" in files:
                            active_stage_dirs.append(root)

        for s_dir in set(active_stage_dirs):
            val_rep_path = os.path.join(s_dir, "validation_report.json")
            if os.path.exists(val_rep_path):
                try:
                    with open(val_rep_path, "r", encoding="utf-8") as f:
                        val_data = json.load(f)
                except Exception as e:
                    return False, (
                        f"HARD HOOK ENFORCEMENT (Post-Analysis Validation Gate): Validation report '{val_rep_path}' "
                        f"is malformed or unreadable: {e}. Verification failed closed."
                    )
                if not isinstance(val_data, dict):
                    return False, (
                        f"HARD HOOK ENFORCEMENT (Post-Analysis Validation Gate): Validation report '{val_rep_path}' "
                        f"must be a JSON object, got {type(val_data).__name__}. Verification failed closed."
                    )

                # 1. Overall verdict MUST be strictly PASS
                verdict = str(val_data.get("overall_verdict", val_data.get("verdict", ""))).strip().upper()
                if verdict != "PASS":
                    return False, (
                        f"HARD HOOK ENFORCEMENT (Post-Analysis Validation Gate): Stage artifacts in '{s_dir}' "
                        f"did not pass deterministic validation (overall_verdict: '{verdict or 'MISSING'}'). "
                        f"Strict contract requires overall_verdict == 'PASS' and checks_failed == 0."
                    )

                # 2. checks_failed MUST be explicitly present and equal to 0
                checks_failed = None
                if isinstance(val_data.get("evidence_summary"), dict):
                    checks_failed = val_data["evidence_summary"].get("checks_failed")
                if checks_failed is None and "checks_failed" in val_data:
                    checks_failed = val_data.get("checks_failed")

                if checks_failed is None:
                    return False, (
                        f"HARD HOOK ENFORCEMENT (Post-Analysis Validation Gate): Validation report '{val_rep_path}' "
                        f"is missing mandatory 'checks_failed' metric. "
                        f"Strict contract requires overall_verdict == 'PASS' and checks_failed == 0."
                    )

                if isinstance(checks_failed, bool) or not isinstance(checks_failed, (int, float)):
                    if isinstance(checks_failed, str) and checks_failed.isdigit():
                        checks_failed = int(checks_failed)
                    else:
                        return False, (
                            f"HARD HOOK ENFORCEMENT (Post-Analysis Validation Gate): Validation report '{val_rep_path}' "
                            f"has invalid non-numeric 'checks_failed' value ({checks_failed!r}). "
                            f"Strict contract requires overall_verdict == 'PASS' and checks_failed == 0."
                        )

                if int(checks_failed) != 0:
                    return False, (
                        f"HARD HOOK ENFORCEMENT (Post-Analysis Validation Gate): Stage artifacts in '{s_dir}' "
                        f"have failing validation checks (checks_failed: {int(checks_failed)}). "
                        f"Strict contract requires overall_verdict == 'PASS' and checks_failed == 0 before completing."
                    )

                # 3. checks_blocked must be 0 if present in evidence_summary
                if isinstance(val_data.get("evidence_summary"), dict):
                    checks_blocked = val_data["evidence_summary"].get("checks_blocked")
                    if checks_blocked is not None and not isinstance(checks_blocked, bool):
                        try:
                            if int(checks_blocked) != 0:
                                return False, (
                                    f"HARD HOOK ENFORCEMENT (Post-Analysis Validation Gate): Stage artifacts in '{s_dir}' "
                                    f"have blocked validation checks (checks_blocked: {int(checks_blocked)}). "
                                    f"Strict contract requires overall_verdict == 'PASS' and checks_failed == 0."
                                )
                        except (ValueError, TypeError):
                            pass

                # 4. failed_checks list must be empty if present
                failed_checks = val_data.get("failed_checks")
                if isinstance(failed_checks, list) and len(failed_checks) > 0:
                    return False, (
                        f"HARD HOOK ENFORCEMENT (Post-Analysis Validation Gate): Stage artifacts in '{s_dir}' "
                        f"recorded failed checks: {failed_checks}. "
                        f"Strict contract requires overall_verdict == 'PASS' and checks_failed == 0."
                    )

                # 5. Individual results verdicts must not be FAIL or BLOCKED
                results = val_data.get("results")
                if isinstance(results, list):
                    for r in results:
                        if isinstance(r, dict):
                            r_verdict = str(r.get("verdict", "")).strip().upper()
                            if r_verdict in ("FAIL", "BLOCKED", "UNKNOWN", "UNVERIFIED", "INCOMPLETE"):
                                return False, (
                                    f"HARD HOOK ENFORCEMENT (Post-Analysis Validation Gate): Stage artifacts in '{s_dir}' "
                                    f"contain non-passing check '{r.get('check_id', r.get('check', 'unknown'))}' "
                                    f"(verdict: '{r_verdict}'). "
                                    f"Strict contract requires overall_verdict == 'PASS' and checks_failed == 0."
                                )
        return True, ""

    @staticmethod
    def verify_binary_honesty(records: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Enforces Directive 0 (Binary Honesty Protocol: Starts with 'Yes' or 'No' on compliance questions).
        """
        if not records:
            return True, ""

        last_assistant_msg = ""
        last_user_msg = ""
        for r in reversed(records):
            stype = r.get("type")
            content = r.get("content", "")
            if not last_assistant_msg and stype == "PLANNER_RESPONSE" and content:
                last_assistant_msg = content.strip()
            elif not last_user_msg and stype == "USER_INPUT" and content:
                last_user_msg = content.strip()
            if last_assistant_msg and last_user_msg:
                break

        clean_user = re.sub(r"<[^>]+>", "", last_user_msg).strip()
        compliance_keywords = [
            "did you", "did the agent", "is the agent do correct", "did it follow",
            "fool me", "fooled me", "were the rules followed", "did you check",
            "did you use the workflow", "was the check performed"
        ]
        is_compliance_query = any(k in clean_user.lower() for k in compliance_keywords)

        if is_compliance_query and last_assistant_msg:
            cleaned_first_text = re.sub(r"^[#\*\s\>`_]+", "", last_assistant_msg)
            first_word = cleaned_first_text.split()[0].rstrip(".,:;!?*").capitalize() if cleaned_first_text.split() else ""
            if first_word not in ("Yes", "No"):
                return False, (
                    f"CONSTITUTIONAL VIOLATION (Directive 0 - Binary Honesty Protocol): The user asked a compliance "
                    f"or honesty question ('{clean_user[:60]}...'). Your response must begin with an unambiguous "
                    f"'Yes' or 'No' as the very first word. Got: '{first_word}'. You must revise your response immediately."
                )
        return True, ""

    @staticmethod
    def verify_multiagent_truthfulness(records: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Enforces Directive 0 & Directive 12.1: Prohibits claiming multi-agent execution if invoke_subagent was called 0 times.
        """
        if not records:
            return True, ""

        subagent_calls_count = 0
        for r in records:
            for tc in r.get("tool_calls", []):
                name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", str(tc))
                if name == "invoke_subagent":
                    subagent_calls_count += 1

        last_assistant_msg = ""
        for r in reversed(records):
            if r.get("type") == "PLANNER_RESPONSE" and r.get("content"):
                last_assistant_msg = r.get("content", "").strip()
                break

        claim_patterns = [
            r"we (?:have )?(?:successfully )?(?:executed|run|completed) (?:a )?(?:complete(?:,)?\s+)?multi[- ]agent",
            r"(?:successfully )?executed (?:an? )?(?:complete(?:,)?\s+)?(?:antigravity )?multi[- ]agent",
            r"multi[- ]agent workflow [\"']?\w+[\"']? completed",
            r"completed,? multi[- ]agent [a-zA-Z0-9_-]+ (?:empirical )?pipeline",
            r"subagents executed:\s*\[",
            r"subagents? (?:were|have been|are) (?:invoked|executed|run|deliberated|coordinated)",
            r"delegated to (?:our|the)? subagents?",
            r"subagent deliberation completed",
            r"orchestrated (?:the )?(?:14|15 )?subagents",
            r"autonomous agents? (?:executed|deliberated|coordinated)",
            r"multi[- ]agent team (?:has )?(?:completed|executed|deliberated|analyzed)",
            r"pipeline run by (?:the )?subagents",
            r"ساب[‌ ]?ایجنت[‌ ]?ها (?:اجرا|بررسی|فراخوانی)",
            r"فرایند چند[‌ ]?عاملی"
        ]
        asst_lower = last_assistant_msg.lower()
        claims_multiagent = any(re.search(pat, asst_lower) for pat in claim_patterns)
        is_negated_review = any(neg in asst_lower for neg in [
            "did not execute", "was not a multi-agent", "called exactly zero",
            "called 0 times", "never invoked", "bypassed the multi-agent",
            "no subagents were invoked", "zero subagents were invoked"
        ])

        if claims_multiagent and not is_negated_review and subagent_calls_count == 0:
            return False, (
                "CONSTITUTIONAL VIOLATION (Directive 0 & Directive 12): Your response claims a 'multi-agent' execution "
                "or subagent pipeline, but 'invoke_subagent' was called 0 times in this transcript! "
                "Workflows in interactive sessions must be orchestrated through Antigravity subagents. "
                "You must state factually that no subagents were invoked and correct your claim."
            )
        return True, ""

    @staticmethod
    def verify_conversational_language(records: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Enforces Directive 6 (English Primary Interaction):
        All conversational interactions, planning, coordination, and status reports with the user
        must be conducted strictly in English. Non-English (Persian) text is reserved exclusively
        for the content of academic deliverables on disk.
        """
        if not records:
            return True, ""

        last_assistant_msg = ""
        last_user_msg = ""
        for r in reversed(records):
            stype = r.get("type")
            content = r.get("content", "")
            if not last_assistant_msg and stype == "PLANNER_RESPONSE" and content:
                last_assistant_msg = content.strip()
            elif not last_user_msg and stype == "USER_INPUT" and content:
                last_user_msg = content.strip()
            if last_assistant_msg and last_user_msg:
                break

        if not last_assistant_msg:
            return True, ""

        # Exempt if user explicitly requested Persian translation or client message
        user_lower = last_user_msg.lower()
        persian_requested = any(kw in user_lower for kw in [
            "translate to persian", "translation to persian", "in persian", "به فارسی", "ترجمه",
            "telegram response", "client telegram", "client message", "متن پیام"
        ])
        if persian_requested:
            return True, ""

        persian_chars = len(re.findall(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]", last_assistant_msg))
        latin_chars = len(re.findall(r"[a-zA-Z]", last_assistant_msg))
        total_alpha = persian_chars + latin_chars

        if total_alpha > 0 and (persian_chars > 80 or (persian_chars > 30 and (persian_chars / total_alpha) > 0.25)):
            ratio = persian_chars / total_alpha
            return False, (
                "CONSTITUTIONAL VIOLATION (Directive 6 - English Primary Interaction): "
                f"Your response to the user was emitted predominantly in Persian ({persian_chars} Persian characters detected, "
                f"{ratio:.1%} of alphabetic content). "
                "Under Directive 6 and the Conversational Language Decoupling Invariant, all dialogue, "
                "planning, roadmap presentation, and coordination with the user MUST be conducted strictly in English. "
                "Persian is strictly reserved for the content of academic deliverables on disk. "
                "Please rewrite and emit your complete response in English."
            )

        return True, ""

    @staticmethod
    def verify_anti_shortcut_and_no_rush(records: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Enforces Directive 25 (Universal Anti-Shortcut, Zero-Fastpath, No-Rush & Proper Execution Invariant):
        1. Prohibits claiming or rationalizing fastpaths, shortpaths, shortcuts, or temporary bypasses.
        2. Prohibits rushing execution or prioritizing turn speed over thoroughness and correctness.
        3. Prohibits emitting placeholder stubs or cutting corners.
        """
        if not records:
            return True, ""

        last_user_idx = -1
        for idx, r in enumerate(records):
            if r.get("type") == "USER_INPUT":
                last_user_idx = idx

        active_records = records[last_user_idx + 1:] if last_user_idx >= 0 else records

        shortcut_patterns = [
            r"\b(?:taking|take|took|use|used|using)\s+(?:a\s+)?(?:shortcut|shortpath|short-path|fastpath|fast-path)\b",
            r"\b(?:quick|temporary)\s+(?:shortcut|bypass|stub|workaround)\b",
            r"\b(?:in\s+a\s+rush|rushing\s+to\s+(?:finish|complete|get\s+done))\b",
            r"\bskip(?:ping)?\s+(?:validation|tests|stages?|triads?)\s+to\s+(?:save\s+time|speed\s+up|rush)\b",
            r"\bplaceholder\s+implementation\s+for\s+now\b",
        ]

        negative_contexts = [
            "directive 25", "never", "prohibited", "forbidden", "banned", "anti-pattern",
            "zero shortcut", "zero permission", "no rush", "without shortcuts", "without rush",
            "violation", "do not rush", "cannot rush", "must not rush"
        ]

        for r in active_records:
            if r.get("type") == "PLANNER_RESPONSE":
                txt = (str(r.get("content") or "") + " " + str(r.get("thinking") or "")).lower()
                for pat in shortcut_patterns:
                    if re.search(pat, txt):
                        if not any(nc in txt for nc in negative_contexts):
                            return False, (
                                "CONSTITUTIONAL VIOLATION (Directive 25 - Universal Anti-Shortcut, Zero-Fastpath & No-Rush Invariant): "
                                "Fastpaths, shortpaths, shortcuts, stubs, and rushed execution are strictly forbidden across ALL agents. "
                                "There should be no rush in getting the job done. "
                                "The work must be executed properly, thoroughly, completely, and deterministically."
                            )
        return True, ""

    @staticmethod
    def verify_learning_pipeline_completion(records: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Enforces Directive 21 & Directive 21.1 (Mandatory Learning & Evolution Pipeline & Zero Fast-Path):
        1. Prohibits claiming an authorized 'fast-path' or postponing tool/skill evolution to 'occur later'.
        2. Affirmative Learning Gate on Critique: If user reported a defect/critique, the orchestrator
           MUST execute the full continuous learning cascade (trajectory-analyzer -> behavior-analyst ->
           knowledge-curator -> skill-evolver -> evaluation-agent) in the active turn.
        3. Premature Remediation Gate: Delivery workers ('academic-writer', 'statistics-agent', etc.)
           CANNOT be invoked or messaged before 'skill-evolver' or 'evaluation-agent' have run.
        """
        if not records:
            return True, ""

        # Find the index of the last USER_INPUT to isolate the active turn
        last_user_idx = -1
        user_content = ""
        for idx, r in enumerate(records):
            if r.get("type") == "USER_INPUT":
                last_user_idx = idx
                user_content = str(r.get("content", ""))

        active_records = records[last_user_idx + 1:] if last_user_idx >= 0 else records

        # 1. Check for 'fast-path' rationalization in assistant messages
        fast_path_patterns = [
            r"\bfast[- ]path\b",
            r"\bslower path\b",
            r"\bslow[- ]path\b",
            r"\bwill occur later\b",
            r"\bpostpone(?:d)? code mutation\b",
            r"\bcode mutation .* will occur later\b",
            r"\bcontext[- ]only updates to avoid conversational delays\b",
            r"\bfast[- ]track behavioral\b"
        ]
        for r in active_records:
            if r.get("type") == "PLANNER_RESPONSE":
                txt = (str(r.get("content") or "") + " " + str(r.get("thinking") or "")).lower()
                for pat in fast_path_patterns:
                    if re.search(pat, txt):
                        exemptions = [
                            "never use fast-path", "banned", "prohibited", "violation",
                            "zero 'fast-path'", "zero \"fast-path\"", "anti-pattern", "forbidden"
                        ]
                        if not any(ex in txt for ex in exemptions):
                            return False, (
                                "CONSTITUTIONAL VIOLATION (Directive 21.1 - Zero 'Fast-Path' Rationalization Invariant): "
                                "Rationalizing an authorized 'fast-path' for context-only updates while postponing code/skill "
                                "evolution ('slower path will occur later') is strictly prohibited and classified as intentional deception under Directive 0. "
                                "You CANNOT bypass 'skill-evolver' or 'evaluation-agent' or postpone code evolution. "
                                "You must invoke 'skill-evolver' and 'evaluation-agent' to evolve the canonical tools before completing this turn."
                            )

        delivery_workers = [
            "academic-writer", "statistics-agent", "data-agent", "psychometric-expert",
            "project-organizer", "qualitative-analyst", "intervention-designer"
        ]

        # 2. Track chronological subagent invocations and messages in active turn
        invoked_subagents = []
        for r in active_records:
            for call in r.get("tool_calls", []):
                call_name = call.get("name")
                if call_name == "invoke_subagent":
                    args = call.get("args", {})
                    subagents = args.get("Subagents", [])
                    if isinstance(subagents, str):
                        try:
                            subagents = json.loads(subagents)
                        except Exception:
                            subagents = []
                    if isinstance(subagents, list):
                        for sa in subagents:
                            if isinstance(sa, dict):
                                t_name = (sa.get("TypeName") or sa.get("Role") or "").lower().strip()
                                if t_name:
                                    invoked_subagents.append(t_name)
                elif call_name == "send_message":
                    args = call.get("args", {})
                    msg = str(args.get("Message", "")).lower()
                    for w in delivery_workers:
                        if w in msg:
                            invoked_subagents.append(w)
                    if any(kw in msg for kw in ("remediation", "task_id", "stage_", ".docx", ".md", "word/document.xml", "process_rec")):
                        if "academic-writer" not in invoked_subagents:
                            invoked_subagents.append("academic-writer")

        # Check if critique/correction triggered learning
        clean_user = re.sub(r"<[^>]+>", "", user_content).strip()
        critique_patterns = [
            r"\b(?:problem|error|bug|defect|issue|flaw|failure|discrepancy|mismatch)s?\b",
            r"\b(?:fix|wrong|incorrect|flawed|missing|redo|re-run|re-execute|reject|rejected)\b",
            r"\b(?:didn'?t|did\s+not)\s+(?:trigger|start|run|work|include|execute)\b",
            r"\b(?:there|it)\s+(?:isn'?t|is\s+not|wasn'?t|was\s+not|aren'?t|are\s+not)\b",
            r"\b(?:isn'?t|is\s+not|wasn'?t|was\s+not)\s+(?:the|what|any|working|correct)\b",
            r"\bnot\s+(?:working|correct|right|accurate)\b",
            r"اشتباه|اشتباهات|غلط|غلط‌ها|اصلاح|تصحیح|مجدد|تکرار|رد شد|نادرست|خطا|خطاها|مشکل|مشکلات|ایراد|ایرادات|نواقص|نقص|جا افتاده|حذف شده|وجود ندارد|نیست"
        ]
        is_user_critique = any(re.search(pat, clean_user, re.IGNORECASE) for pat in critique_patterns)

        # Check if premature remediation was attempted before evolution completed
        has_learning_started = any(
            any(k in sa for k in ("knowledge-curator", "trajectory-analyzer", "behavior-analyst"))
            for sa in invoked_subagents
        ) or is_user_critique

        if has_learning_started:
            eval_seen = False
            for sa in invoked_subagents:
                if "evaluation-agent" in sa:
                    eval_seen = True
                if any(w in sa for w in delivery_workers):
                    if not eval_seen:
                        return False, (
                            "CONSTITUTIONAL VIOLATION (Directive 21.1 - Premature Remediation Without Tool Evolution): "
                            f"Delivery worker '{sa}' was invoked or messaged before completing tool evolution via 'skill-evolver' and 'evaluation-agent'! "
                            "Under Directive 21.1, you are strictly prohibited from attempting deliverable remediation or authoring ad-hoc scripts "
                            "before the canonical skills and scripts have been permanently evolved and graduated on disk. "
                            "Invoke 'skill-evolver' and 'evaluation-agent' first."
                        )

        # 2a. Affirmative Learning Gate on Critique:
        # If user reported critique, the learning and evolution cascade MUST be invoked in this turn!
        if is_user_critique:
            has_diagnostic = any(
                any(k in sa for k in ("trajectory-analyzer", "behavior-analyst", "knowledge-curator"))
                for sa in invoked_subagents
            )
            has_evolution = any(
                any(ev in sa for ev in ("skill-evolver", "evaluation-agent"))
                for sa in invoked_subagents
            )
            if not has_diagnostic or not has_evolution:
                return False, (
                    "CONSTITUTIONAL VIOLATION (Directive 21 & Directive 21.1 - Uninvoked Learning Pipeline on Critique): "
                    f"The user reported a defect or critique ('{clean_user[:80]}...'), but the continuous learning cascade "
                    "was NOT executed in this turn! "
                    "Under Directive 21 and Directive 21.1, you are strictly prohibited from bypassing learning, attempting "
                    "ad-hoc direct fixes, or messaging workers without first running the full 5-stage cascade: "
                    "1. trajectory-analyzer, 2. behavior-analyst, 3. knowledge-curator, 4. skill-evolver, 5. evaluation-agent. "
                    "Please invoke 'trajectory-analyzer' now."
                )

        # 3. If knowledge-curator or skill-evolver was invoked, evolution & graduation MUST be completed
        has_kc = any("knowledge-curator" in sa for sa in invoked_subagents)
        has_se = any("skill-evolver" in sa for sa in invoked_subagents)
        has_ea = any("evaluation-agent" in sa for sa in invoked_subagents)

        if has_kc or has_se:
            if not has_se and not has_ea:
                return False, (
                    "CONSTITUTIONAL VIOLATION (Directive 21 - Continuous Learning & Evolution Pipeline Incomplete): "
                    "'knowledge-curator' was invoked to catalog a lesson, but the evolution subagents ('skill-evolver' and 'evaluation-agent') "
                    "were NOT invoked in this turn! "
                    "Under Directives 21 and 21.1, you MUST dispatch 'skill-evolver' to synthesize canonical tool/skill modifications "
                    "and 'evaluation-agent' to execute the deterministic graduation compiler ('python3 .agents/scripts/academic_graduation_compiler.py compile-lesson <path>') "
                    "before concluding this turn or initiating stage remediation. "
                    "Please invoke 'skill-evolver' now."
                )

            # Check if pending ungraduated lessons or staged candidates exist in active turn records
            pending_items = []
            seen_json_paths = set()
            for r in active_records:
                r_text = json.dumps(r, ensure_ascii=False)
                for m in re.findall(r'([^\s\'"\\,]+\.json)', r_text):
                    if any(k in m for k in ("lessons", "candidates", "anti-patterns", "principles", "LSN-", "CAND-", "AP-", "PRN-")):
                        m_clean = m.strip().strip("'\"")
                        if m_clean not in seen_json_paths and os.path.isfile(m_clean):
                            seen_json_paths.add(m_clean)
                            try:
                                with open(m_clean, "r", encoding="utf-8") as jf:
                                    jdata = json.load(jf)
                                if jdata.get("graduation_status") == "PENDING_GRADUATION":
                                    item_id = jdata.get("lesson_id") or os.path.basename(m_clean)
                                    pending_items.append((m_clean, item_id, "PENDING_GRADUATION"))
                                elif jdata.get("status") == "STAGED" and jdata.get("target_component"):
                                    item_id = jdata.get("candidate_id") or os.path.basename(m_clean)
                                    pending_items.append((m_clean, item_id, "STAGED"))
                            except Exception:
                                pass

            if pending_items:
                pending_desc = ", ".join(f"{item_id} ({status})" for _, item_id, status in pending_items)
                return False, (
                    "CONSTITUTIONAL VIOLATION (Directive 21 - Incomplete Invariant Graduation): "
                    f"Learning item(s) remain uncompiled on disk: {pending_desc}. "
                    "Staging a candidate JSON or cataloging a lesson alone does NOT mutate canonical skills. "
                    "Under Directive 21, you MUST dispatch 'evaluation-agent' to execute "
                    "'python3 .agents/scripts/academic_graduation_compiler.py compile-lesson <path>' (or compile-candidate) "
                    "to compile the verified rule into target SKILL.md/AGENTS.md files before concluding this turn. "
                    "Please invoke 'evaluation-agent' now."
                )

            if has_se and not has_ea:
                return False, (
                    "CONSTITUTIONAL VIOLATION (Directive 21 - Missing Evaluation & Graduation Step): "
                    "'skill-evolver' was invoked to synthesize candidate modifications, but 'evaluation-agent' was NOT invoked "
                    "to execute the deterministic graduation compiler! "
                    "Under Directive 21, you MUST dispatch 'evaluation-agent' to run "
                    "'python3 .agents/scripts/academic_graduation_compiler.py compile-candidate <path>' or 'compile-lesson <path>' "
                    "to mutate canonical skills on disk before concluding. "
                    "Please invoke 'evaluation-agent' now."
                )

        return True, ""

    @staticmethod
    def handle_stop(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for Stop integrity checks:
        1. Standalone Python orchestrator prohibition (Directive 12.1)
        2. Skill modularity / context budget limits (Directive 18)
        3. Triad Artifact Invariant (Directive 3)
        4. Manifest verification
        5. Post-analysis validation report checks
        6. Binary Honesty Protocol (Directive 0)
        7. Multi-Agent claim truthfulness (Directive 0)
        8. Learning & Evolution Pipeline Completion (Directive 21 & 21.1)
        """
        workspaces = payload.get("workspacePaths", [])

        # 1. Standalone Python Orchestrator Prohibition (Directive 12.1)
        for ws in workspaces:
            forbidden_file = os.path.join(ws, ".agents", "skills", "academic-suite-orchestrator", "scripts", "multi_agent_orchestrator.py")
            if os.path.exists(forbidden_file):
                msg = (
                    "CONSTITUTIONAL VIOLATION (Directive 12.1 - Sole Orchestrator Mandate): "
                    f"Forbidden file '{forbidden_file}' detected on disk. Standalone Python multi-agent "
                    "orchestrators are prohibited. Antigravity is the sole agent conductor. Delete this file immediately."
                )
                return {
                    "decision": "continue",
                    "reason": msg,
                    "message": msg
                }

        # 2. Skill Modularity (Directive 18)
        ok, reason = IntegrityHooks.verify_skill_modularity(workspaces)
        if not ok:
            return {"decision": "continue", "reason": reason, "message": reason}

        # 3. State Machine Consistency (Invalid State Transition Detection)
        ok, reason = IntegrityHooks.verify_state_transitions(workspaces)
        if not ok:
            return {"decision": "continue", "reason": reason, "message": reason}

        # 3.5 Worker Return Structure (Phase 21 Invariant)
        ok, reason = IntegrityHooks.verify_worker_returns(workspaces)
        if not ok:
            return {"decision": "continue", "reason": reason, "message": reason}

        # 4. Missing Artifacts Detection (Triad Invariant & Manifest Deliverables)
        ok, reason = IntegrityHooks.verify_missing_artifacts(workspaces)
        if not ok:
            return {"decision": "continue", "reason": reason, "message": reason}

        # 5. Provenance Integrity Detection (Input/Output Hashes & Dependencies)
        ok, reason = IntegrityHooks.verify_provenance(workspaces)
        if not ok:
            return {"decision": "continue", "reason": reason, "message": reason}

        # 6. Post-Analysis Validation Reports
        ok, reason = IntegrityHooks.verify_post_analysis(workspaces)
        if not ok:
            return {"decision": "continue", "reason": reason, "message": reason}

        # 7. Transcript Checks (Binary Honesty & Multi-Agent Claims)
        transcript_path = resolve_transcript_path(payload)
        records = load_transcript(transcript_path) if transcript_path else []
        if records:
            ok, reason = IntegrityHooks.verify_binary_honesty(records)
            if not ok:
                return {"decision": "continue", "reason": reason, "message": reason}

            ok, reason = IntegrityHooks.verify_multiagent_truthfulness(records)
            if not ok:
                return {"decision": "continue", "reason": reason, "message": reason}

            ok, reason = IntegrityHooks.verify_conversational_language(records)
            if not ok:
                return {"decision": "continue", "reason": reason, "message": reason}

            # 8. Anti-Shortcut, Zero-Fastpath & No-Rush Invariant (Directive 25)
            ok, reason = IntegrityHooks.verify_anti_shortcut_and_no_rush(records)
            if not ok:
                return {"decision": "continue", "reason": reason, "message": reason}

            # 9. Learning & Evolution Pipeline Completion (Directive 21 & 21.1)
            ok, reason = IntegrityHooks.verify_learning_pipeline_completion(records)
            if not ok:
                return {"decision": "continue", "reason": reason, "message": reason}

        return {"decision": "allow"}

    @staticmethod
    def handle_post_invocation(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Advisory verification after model tool turn:
        Injects advisory if active stage validation report is FAIL.
        """
        workspaces = payload.get("workspacePaths", [])
        inject_steps = []
        for ws in workspaces:
            for root, dirs, files in os.walk(ws):
                if "validation_report.json" in files:
                    v_path = os.path.join(root, "validation_report.json")
                    try:
                        with open(v_path, "r", encoding="utf-8") as vf:
                            v_data = json.load(vf)
                        if not isinstance(v_data, dict):
                            inject_steps.append({
                                "ephemeralMessage": (
                                    f"STAGE VERIFICATION ADVISORY: Validation report in '{root}' "
                                    f"is malformed (expected JSON object, got {type(v_data).__name__}). Please fix or regenerate."
                                )
                            })
                            break
                        verdict = str(v_data.get("overall_verdict", v_data.get("verdict", ""))).strip().upper()
                        checks_failed = None
                        if isinstance(v_data.get("evidence_summary"), dict):
                            checks_failed = v_data["evidence_summary"].get("checks_failed")
                        if checks_failed is None and "checks_failed" in v_data:
                            checks_failed = v_data.get("checks_failed")

                        is_zero = (
                            checks_failed is not None
                            and isinstance(checks_failed, (int, float))
                            and not isinstance(checks_failed, bool)
                            and int(checks_failed) == 0
                        )

                        if verdict != "PASS" or not is_zero:
                            inject_steps.append({
                                "ephemeralMessage": (
                                    f"STAGE VERIFICATION ADVISORY: Validation report in '{root}' "
                                    f"does not satisfy passing contract (overall_verdict: '{verdict or 'MISSING'}', "
                                    f"checks_failed: {checks_failed if checks_failed is not None else 'MISSING'}). "
                                    f"Contract strictly requires overall_verdict == 'PASS' and checks_failed == 0."
                                )
                            })
                            break
                    except Exception as e:
                        inject_steps.append({
                            "ephemeralMessage": (
                                f"STAGE VERIFICATION ADVISORY: Validation report in '{root}' "
                                f"is corrupted or unreadable: {e}. Please fix or regenerate."
                            )
                        })
                        break
        return {"injectSteps": inject_steps, "terminationBehavior": ""}


def main():
    import json
    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[integrity_hooks] Error parsing stdin JSON: {e}\n")

    event = payload.get("event", "Stop")
    if event == "PostInvocation":
        res = IntegrityHooks.handle_post_invocation(payload)
    else:
        res = IntegrityHooks.handle_stop(payload)
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
