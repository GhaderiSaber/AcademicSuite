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

HOOKS_DIR = os.path.dirname(os.path.realpath(__file__))
AGENTS_DIR = os.path.dirname(HOOKS_DIR)
ROOT_DIR = os.path.dirname(AGENTS_DIR)
for p in (ROOT_DIR, AGENTS_DIR, HOOKS_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from contracts.hook_identity_contract import (
        resolve_transcript_path,
        resolve_hook_identity,
        is_learning_subagent,
        is_auditor_agent,
        LEARNING_SUBAGENTS,
    )
    from contracts.critique_detection_contract import is_meaningful_user_critique, extract_clean_user_message
    from contracts.current_work_resolver import (
        resolve_current_work_stage_dirs,
        get_current_work_validation_reports,
        is_validation_report_for_current_work,
    )
except ImportError:
    try:
        from .contracts.hook_identity_contract import (
            resolve_transcript_path,
            resolve_hook_identity,
            is_learning_subagent,
            is_auditor_agent,
            LEARNING_SUBAGENTS,
        )
        from .contracts.critique_detection_contract import is_meaningful_user_critique, extract_clean_user_message
        from .contracts.current_work_resolver import (
            resolve_current_work_stage_dirs,
            get_current_work_validation_reports,
            is_validation_report_for_current_work,
        )
    except ImportError:
        def resolve_transcript_path(payload):
            return payload.get("transcriptPath") if isinstance(payload, dict) else None
        def resolve_hook_identity(payload):
            return None
        def is_meaningful_user_critique(user_text, **kw):
            return False, None
        def extract_clean_user_message(raw_text):
            return re.sub(r"<[^>]+>", "", str(raw_text)).strip()
        def resolve_current_work_stage_dirs(*args, **kwargs):
            return []
        def get_current_work_validation_reports(*args, **kwargs):
            return []
        def is_validation_report_for_current_work(*args, **kwargs):
            return True
        LEARNING_SUBAGENTS = (
            "behavior-analyst", "curriculum-builder", "evaluation-agent",
            "knowledge-curator", "skill-evolver", "trajectory-analyzer",
        )
        def is_learning_subagent(caller):
            if not caller:
                return False
            c = str(caller).lower().strip()
            return any(k in c for k in LEARNING_SUBAGENTS)
        def is_auditor_agent(caller):
            if not caller:
                return False
            c = str(caller).lower().strip()
            return any(k in c for k in ("validation", "auditor", "challenger", "judge", "inspector"))



def resolve_caller(payload: Dict[str, Any]) -> str:
    """Resolves caller identity from Antigravity lifecycle hook payloads."""
    caller = ""
    if resolve_hook_identity:
        try:
            ident = resolve_hook_identity(payload)
            if ident:
                if ident.is_main_developer:
                    return "default"
                if ident.agent_name and ident.agent_name != "unknown":
                    return ident.agent_name.lower().strip()
        except Exception:
            pass
    if not caller:
        sub_desc = payload.get("subagentDescriptor") or {}
        if isinstance(sub_desc, dict):
            caller = sub_desc.get("typeName") or sub_desc.get("role") or ""
    if not caller:
        caller = (
            payload.get("agent_name") or
            payload.get("agentName") or
            payload.get("agent") or
            payload.get("caller") or
            payload.get("role") or
            payload.get("agentRole") or ""
        )
    return str(caller).lower().strip()


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


def is_data_analysis_stage(stage_or_file: str, stage_dir: Optional[str] = None) -> bool:
    """
    Determines whether a stage or artifact represents a pure computational data analysis stage
    (Phases 4A, 4B, 4C) that outputs only structured data payloads (.json, .xlsx, .png)
    and strictly does NOT require or produce narrative prose (.docx, .md).
    """
    if not stage_or_file or not isinstance(stage_or_file, str):
        return False
    norm = os.path.basename(stage_or_file).strip().lower()
    stem = os.path.splitext(norm)[0]

    if "payload" in stem:
        return True

    if re.search(r'(?:^|[_\-.])(?:phase\s*4[abc]|stage[_\-]?4[abc]|4[abc][_\-.])', stem):
        return True

    data_indicators = [
        "curation", "data_quality", "data_audit", "clean_data", "data_cleaned",
        "passport", "assumptions_report", "model_payload", "data_engineering",
        "screening", "matrix", "frequencies", "descriptive", "simulation",
        "normality", "collinearity", "power_analysis", "stats_results"
    ]
    if any(ind in stem for ind in data_indicators):
        return True

    # Check on-disk evidence if stage_dir is available or if stage_or_file is an absolute path
    target_dir = stage_dir if (stage_dir and os.path.isdir(stage_dir)) else (
        os.path.dirname(stage_or_file) if os.path.isabs(stage_or_file) and os.path.isdir(os.path.dirname(stage_or_file)) else None
    )
    if target_dir and os.path.isdir(target_dir):
        files = os.listdir(target_dir)
        # If a corresponding _payload file exists for this stem
        if f"{stem}_payload.json" in files or f"{stem}_payload" in files:
            return True
        # If neither .docx nor .md exists on disk for this stem, check if .json has valid JSON data
        json_file = f"{stem}.json"
        has_text_draft = f"{stem}.md" in files or f"{stem}.docx" in files
        if not has_text_draft and json_file in files:
            try:
                with open(os.path.join(target_dir, json_file), "r", encoding="utf-8") as jf:
                    jdata = json.load(jf)
                if isinstance(jdata, (dict, list)):
                    return True
            except Exception:
                pass

    return False


def is_narrative_stage(stage_or_file: str, stage_dir: Optional[str] = None) -> bool:
    """
    Determines whether a stage represents a pure narrative / text / scoping / qualitative stage
    (e.g., literature review, theoretical background, qualitative themes, discussion prose)
    that legitimately exists as Markdown (.md) without requiring a numerical data payload (.json).
    """
    if not stage_or_file or not isinstance(stage_or_file, str):
        return False
    norm = os.path.basename(stage_or_file).strip().lower()
    stem = os.path.splitext(norm)[0]

    narrative_indicators = [
        "literature", "theory", "theoretical", "problem_statement",
        "background", "scoping", "qualitative", "interview", "thematic",
        "protocol", "manual", "intro", "introduction", "discussion",
        "synthesis", "overview", "rebuttal", "response"
    ]
    if any(ind in stem for ind in narrative_indicators):
        return True

    target_dir = stage_dir if (stage_dir and os.path.isdir(stage_dir)) else (
        os.path.dirname(stage_or_file) if os.path.isabs(stage_or_file) and os.path.isdir(os.path.dirname(stage_or_file)) else None
    )
    if target_dir and os.path.isdir(target_dir):
        files = os.listdir(target_dir)
        has_md = f"{stem}.md" in files
        has_json = f"{stem}.json" in files or f"{stem}_payload.json" in files
        has_docx = f"{stem}.docx" in files
        if has_md and not has_json and not has_docx:
            return True

    return False


class IntegrityHooks:
    """
    Class B: Integrity Hooks
    Responsible for enforcing artifact invariants, manifest validation, state consistency,
    and post-analysis validation reports without acting as an orchestrator.
    """

    @staticmethod
    def verify_artifacts(workspaces: List[str]) -> Tuple[bool, str]:
        """
        Enforces Option B (Two-Tier Drafting Architecture):
        1. Pure computational data analysis stages (Phases 4A, 4B, 4C) require strictly .json data payloads.
        2. Chapter consolidation milestones (e.g., Chapter_4_Results, scale_validation_report, master_package)
           strictly require Chapter Monograph deliverables (.docx OpenXML Word document + .md Markdown).
        3. Micro-stage empirical findings & hypotheses (Tier 1) require the Dyad (.json statistical anchor +
           .md scholarly narrative). Generating an intermediate .docx is optional and non-blocking.
        """
        active_stage_dirs = []
        exclude_dirs = {".git", ".agents", ".venv", "node_modules", "archive", "tests", "evals"}
        for ws in workspaces:
            for rel_root in ("projects", "03_deliverables", "."):
                p_dir = os.path.join(ws, rel_root)
                if os.path.exists(p_dir):
                    for root, dirs, files in os.walk(p_dir):
                        dirs[:] = [d for d in dirs if d not in exclude_dirs]
                        rel_from_ws = os.path.relpath(root, ws).replace("\\", "/")
                        if any(seg.startswith(".") and seg not in (".", "..") for seg in rel_from_ws.split("/")):
                            continue
                        if any(re.search(r'^(?:\d+_)?[a-zA-Z0-9_-]+\.(?:docx|md|json)$', f) for f in files):
                            if any(re.search(r'(?:hypothesis|demographic|descriptive|assumption|correlation|model|curation|deliverable|chapter|summary|monograph)', f, re.I) for f in files):
                                active_stage_dirs.append(root)

        for s_dir in set(active_stage_dirs):
            files = os.listdir(s_dir)
            stage_prefixes = set()
            for f in files:
                m = re.match(r'^(\d+_[a-zA-Z0-9_-]+)\.(?:docx|md|json)$', f)
                if m:
                    stage_prefixes.add(m.group(1))
                else:
                    m2 = re.match(r'^([a-zA-Z0-9_-]+)\.(?:docx|md|json)$', f)
                    if m2:
                        stem = m2.group(1)
                        if any(k in stem.lower() for k in ["chapter", "scale_validation", "master_package", "monograph", "defense_brief"]):
                            stage_prefixes.add(stem)

            # Check if directory has an authoritative manifest
            m_path = os.path.join(s_dir, "manifest.json")
            manifest_declares_monograph = False
            manifest_is_data_stage = False
            if os.path.exists(m_path):
                try:
                    with open(m_path, "r", encoding="utf-8") as mf:
                        m_obj = json.load(mf)
                    if isinstance(m_obj, dict):
                        st_type = m_obj.get("stage_type", "").lower()
                        if st_type in ("data_analysis", "computational_payload", "data_curation"):
                            manifest_is_data_stage = True
                        reqs = m_obj.get("required_artifacts", [])
                        exts = {os.path.splitext(r.get("path", ""))[1].lower() for r in reqs if isinstance(r, dict) and r.get("required", True)}
                        if ".docx" in exts and ".md" in exts:
                            manifest_declares_monograph = True
                except Exception:
                    pass

            for pfx in stage_prefixes:
                has_docx = f"{pfx}.docx" in files
                has_md = f"{pfx}.md" in files
                has_json = f"{pfx}.json" in files

                # Determine whether this prefix or directory represents a data analysis payload stage
                is_data_stage = (
                    manifest_is_data_stage or
                    is_data_analysis_stage(pfx, stage_dir=s_dir) or
                    is_data_analysis_stage(os.path.basename(s_dir), stage_dir=s_dir)
                ) and not manifest_declares_monograph

                if is_data_stage:
                    # Data analysis stages strictly require non-empty .json payload, but NOT .docx or .md
                    has_matching_json = has_json or f"{pfx}_payload.json" in files or (pfx.endswith("_payload") and f"{pfx[:-8]}.json" in files)
                    if not has_matching_json:
                        return False, (
                            f"HARD HOOK ENFORCEMENT (Data Analysis Payload Invariant): "
                            f"Stage '{pfx}' in '{s_dir}' is missing required data payload file: '{pfx}.json'."
                        )
                    continue

                # Check if this represents a chapter monograph assembly milestone
                norm_pfx = pfx.lower()
                is_monograph = (
                    manifest_declares_monograph or
                    any(k in norm_pfx for k in ["chapter_", "chapter4", "scale_validation_report", "master_package", "monograph", "defense_brief"])
                )

                if is_monograph:
                    missing = []
                    if not has_docx: missing.append(f"{pfx}.docx")
                    if not has_md: missing.append(f"{pfx}.md")
                    if missing and (has_docx or has_md):
                        return False, (
                            f"HARD HOOK ENFORCEMENT (Directive 3 - Chapter Monograph Invariant): "
                            f"Chapter consolidation milestone '{pfx}' in '{s_dir}' is missing required master deliverables. Missing: {missing}. "
                            f"Chapter consolidation milestones strictly require both OpenXML Word (.docx) and Markdown (.md)."
                        )
                    continue

                # Check if this represents a pure narrative / qualitative / literature stage (.md only)
                is_narrative = (
                    is_narrative_stage(pfx, stage_dir=s_dir) or
                    is_narrative_stage(os.path.basename(s_dir), stage_dir=s_dir) or
                    (has_md and not has_json and not has_docx)
                )
                if is_narrative:
                    if not has_md:
                        return False, (
                            f"HARD HOOK ENFORCEMENT (Directive 3 - Narrative Stage Invariant): "
                            f"Narrative stage '{pfx}' in '{s_dir}' is missing required Markdown narrative file: '{pfx}.md'."
                        )
                    continue

                # Otherwise: Tier 1 Micro-Stage (Hypothesis / Section Findings)
                # Enforces Dyad (.json statistical anchor + .md scholarly narrative)
                # Intermediate .docx is optional and permitted, but its absence does NOT fail
                missing = []
                if not has_json: missing.append(f"{pfx}.json")
                if not has_md: missing.append(f"{pfx}.md")
                if missing and (has_md or has_json or has_docx):
                    return False, (
                        f"HARD HOOK ENFORCEMENT (Directive 3 - Triad Artifact Invariant / Micro-Stage Dyad Invariant): "
                        f"Stage '{pfx}' in '{s_dir}' has incomplete physical artifacts. Missing: {missing}. "
                        f"Micro-stages require a synchronized dyad: structured data (.json) and scholarly narrative (.md)."
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
                            if not os.path.exists(a_full):
                                alt = os.path.join(ROOT_DIR, a_path)
                                if os.path.exists(alt):
                                    a_full = alt
                            if not os.path.exists(a_full) or os.path.getsize(a_full) == 0:
                                return False, (
                                    f"HARD HOOK ENFORCEMENT (Manifest Verification): Stage in '{root}' declares "
                                    f"artifact '{a_path}' in manifest.json, but it is missing or empty on disk."
                                )
        return True, ""

    @staticmethod
    def verify_missing_artifacts(workspaces: List[str], caller: str = "") -> Tuple[bool, str]:
        """
        Secondary Enforcement (Missing Artifact Guard):
        Detects missing artifacts across active stage directories and authoritative manifests.
        1. Checks Triad Artifact Invariant (.docx, .md, .json).
        2. Checks declared manifest deliverables exist and have non-zero size.

        EXEMPTION FOR LEARNING SUBAGENTS, AUDITORS, AND MAIN DEVELOPER:
        Learning subagents (benchmarking/evaluation) and quality auditors do not author
        thesis deliverables and must not be blocked by incomplete chapter deliverables on disk.
        """
        caller_clean = (caller or "").lower().strip()
        if is_learning_subagent(caller_clean) or is_auditor_agent(caller_clean) or caller_clean in (
            "default", "main", "developer", "coding", "cli-developer", "ide-developer"
        ):
            return True, ""

        ok_triad, reason_triad = IntegrityHooks.verify_artifacts(workspaces)
        if not ok_triad:
            return False, reason_triad

        ok_manifest, reason_manifest = IntegrityHooks.verify_manifests(workspaces)
        if not ok_manifest:
            return False, reason_manifest

        return True, ""

    @staticmethod
    def verify_state_transitions(workspaces: List[str], caller: str = "") -> Tuple[bool, str]:
        """
        Secondary Enforcement (Invalid State Transition Guard):
        Detects invalid state transitions in workspace state directories.
        Validates that stage state records in current_state.json or events.jsonl obey
        STAGE_LEGAL_TRANSITIONS and explicit human approval gates.
        Fails closed on any malformed JSON, corrupted ledger, non-dict state, or illegal transition.
        """
        caller_clean = (caller or "").lower().strip()
        if is_learning_subagent(caller_clean) or is_auditor_agent(caller_clean) or caller_clean in (
            "default", "main", "developer", "coding", "cli-developer", "ide-developer"
        ):
            return True, ""
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
    def verify_worker_returns(workspaces: List[str], caller: str = "") -> Tuple[bool, str]:
        """
        Secondary Enforcement (Worker Return Invariant Guard - Phase 21):
        Verifies that worker subagent returns recorded in state or handoffs contain:
        artifact, evidence, status, validation (not simply 'done').
        """
        caller_clean = (caller or "").lower().strip()
        if is_learning_subagent(caller_clean) or is_auditor_agent(caller_clean) or caller_clean in (
            "default", "main", "developer", "coding", "cli-developer", "ide-developer"
        ):
            return True, ""
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
    def verify_provenance(workspaces: List[str], caller: str = "") -> Tuple[bool, str]:
        """
        Secondary Enforcement (Invalid Provenance Guard):
        Detects invalid provenance across manifests, deliverables, and dependencies.
        Verifies input SHA-256 integrity, deliverable SHA-256 hash match, and dependency manifest hashes.
        """
        caller_clean = (caller or "").lower().strip()
        if is_learning_subagent(caller_clean) or is_auditor_agent(caller_clean) or caller_clean in (
            "default", "main", "developer", "coding", "cli-developer", "ide-developer"
        ):
            return True, ""
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
    def verify_post_analysis(workspaces: List[str], caller: str = "", payload: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Secondary Enforcement (Post-Analysis Validation Gate):
        Enforces Directive 22 (Fail-Closed Mechanical Validation Gate Invariant):
        PASS + checks_failed == 0 -> accept
        Everything else            -> reject (fail closed).

        CURRENT WORK ISOLATION:
        Only analyzes validation_report.json files belonging to the CURRENT WORK stage(s).
        Unrelated validation reports in other stages or projects across the workspace are strictly ignored.
        If the current work did not touch any deliverable stage, verification passes without blocking.

        A validation report is ONLY accepted if:
        1. It is a valid, readable JSON object.
        2. overall_verdict is strictly "PASS" (not FAIL, UNKNOWN, BLOCKED, INCOMPLETE, UNVERIFIED, missing, or empty).
        3. checks_failed is explicitly present (in evidence_summary or top-level) and equal to 0.
        4. checks_blocked is 0 (if present in evidence_summary).
        5. failed_checks list is empty (if present).
        6. All individual check results are PASS or SKIP (if results list is present).

        EXEMPTION FOR AUDITOR AGENTS & MAIN DEVELOPER:
        Auditor subagents (validation-agent, results-auditor, statistical-auditor,
        evidence-auditor, academic-challenger, final-judge, thesis-integrity-auditor)
        audit deliverables and produce defect dossiers. When an auditor records a
        legitimate FAIL report on disk, it MUST NOT be blocked from concluding its turn
        to report findings to the orchestrator or user.
        Similarly, Track 1 Main Developer is exempt from academic delivery gates.
        """
        caller_clean = (caller or "").lower().strip()
        if is_learning_subagent(caller_clean) or is_auditor_agent(caller_clean) or caller_clean in (
            "default", "main", "developer", "coding", "cli-developer", "ide-developer"
        ):
            return True, ""

        active_stage_dirs = resolve_current_work_stage_dirs(
            workspaces=workspaces,
            payload=payload,
            caller=caller
        )

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
                            if r_verdict in ("FAIL", "BLOCKED"):
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
    def detect_validation_failure(
        active_records: Optional[List[Dict[str, Any]]] = None,
        workspaces: Optional[List[str]] = None,
        records: Optional[List[Dict[str, Any]]] = None,
        payload: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Tuple[bool, str]:
        recs = active_records if active_records is not None else (records or [])
        # 1. Transcript records check
        for rec in reversed(recs):
            t = rec.get("type", "")
            src = rec.get("source", "")
            if t in ("EPHEMERAL_MESSAGE",) or src in ("SYSTEM_SDK",):
                continue
            content = str(rec.get("content", ""))
            if "File Path: `file:///" in content or "Total Lines:" in content:
                continue
            if content.strip().startswith('{"File":') and '"LineNumber":' in content:
                continue

            if any(k in content.lower() for k in ("validation_report.json", "overall_verdict", "checks_failed", "validation cascade", "validation audit")):
                has_fail = (
                    re.search(r'\boverall_verdict[\'":\s]+fail\b', content, re.IGNORECASE)
                    or re.search(r'\bverdict[\'":\s]+fail\b', content, re.IGNORECASE)
                    or re.search(r'\boverall_verdict\s+of\s+\*?\*?fail\*?\*?', content, re.IGNORECASE)
                    or re.search(r'checks_failed[\'":\s]+[1-9]\d*', content, re.IGNORECASE)
                    or ("STAGE VERIFICATION ADVISORY" in content and "FAIL" in content)
                )
                has_pass = (
                    re.search(r'\boverall_verdict[\'":\s]+pass\b', content, re.IGNORECASE)
                    or re.search(r'\boverall_verdict\s+of\s+\*?\*?pass\*?\*?', content, re.IGNORECASE)
                ) and re.search(r'checks_failed[\'":\s]+0\b', content, re.IGNORECASE)

                if has_pass:
                    return False, ""
                if has_fail:
                    summary = "Validation failed: overall_verdict is FAIL"
                    m_failed = re.search(r'(\d+)\s+total\s+`?checks_failed`?|checks_failed[\'":\s]+(\d+)', content, re.IGNORECASE)
                    if m_failed:
                        num = m_failed.group(1) or m_failed.group(2)
                        summary = f"Validation failed ({num} checks failed, overall_verdict: FAIL)"
                    return True, summary

        # 2. Disk check strictly scoped to CURRENT WORK stage directories
        ws_list = workspaces or []
        cand_paths = []
        active_stage_dirs = resolve_current_work_stage_dirs(
            workspaces=ws_list,
            records=recs,
            payload=payload
        )
        for sdir in active_stage_dirs:
            cp = os.path.join(sdir, "validation_report.json")
            if os.path.isfile(cp):
                cand_paths.append(cp)

        for cp in cand_paths:
            if os.path.exists(cp):
                try:
                    with open(cp, "r", encoding="utf-8") as vf:
                        v_data = json.load(vf)
                    verdict = str(v_data.get("overall_verdict", "")).strip().upper()
                    ev_sum = v_data.get("evidence_summary", {})
                    checks_failed = ev_sum.get("checks_failed", v_data.get("checks_failed", 0))
                    if verdict == "FAIL" or (isinstance(checks_failed, int) and checks_failed > 0):
                        summary = f"Validation report '{os.path.basename(cp)}' in '{os.path.basename(os.path.dirname(cp))}' overall_verdict is FAIL ({checks_failed} checks failed)"
                        return True, summary
                except Exception:
                    pass
        return False, ""

    @staticmethod
    def verify_learning_pipeline_completion(records: List[Dict[str, Any]], workspaces: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Enforces Directive 21 & Directive 21.1 (Mandatory Learning & Evolution Pipeline & Zero Fast-Path):
        1. Prohibits claiming an authorized 'fast-path' or postponing tool/skill evolution to 'occur later'.
        2. Affirmative Learning Gate on Critique or Validation Failure: If user reported a defect/critique
           or validator issued FAIL, the orchestrator MUST execute the full continuous learning cascade
           (trajectory-analyzer -> behavior-analyst -> knowledge-curator -> skill-evolver -> evaluation-agent) in the active turn.
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

        # Check if critique/correction or validation failure triggered learning
        clean_user = extract_clean_user_message(user_content)
        is_user_critique, _ = is_meaningful_user_critique(
            clean_user,
            is_subagent=False,
            caller="academic-orchestrator"
        )
        is_val_failure, val_summary = IntegrityHooks.detect_validation_failure(active_records, workspaces)
        # Check if defect was already learned across the conversation (Remediation Phase)
        learning_already_completed = False
        latest_eval_idx = -1
        for idx, r in enumerate(records):
            content = str(r.get("content", ""))
            has_eval_agent = False
            for tc in r.get("tool_calls", []):
                if (tc.get("name") or "").lower() == "invoke_subagent":
                    tc_str = json.dumps(tc.get("args", {})) if isinstance(tc.get("args"), dict) else str(tc)
                    if any(k in tc_str.lower() for k in ("evaluation-agent", "candidate evaluator")):
                        has_eval_agent = True
                    subs = tc.get("args", {}).get("Subagents", [])
                    if isinstance(subs, str):
                        try: subs = json.loads(subs, strict=False)
                        except Exception: subs = []
                    for s in (subs if isinstance(subs, list) else []):
                        if isinstance(s, dict) and any(k in (s.get("TypeName") or s.get("Role") or "").lower() for k in ("evaluation-agent", "candidate evaluator")):
                            has_eval_agent = True
                            break

            if not has_eval_agent and (r.get("source") == "SUBAGENT" or "[Message]" in content or r.get("type") in ("SYSTEM_MESSAGE", "GENERIC", "PLANNER_RESPONSE")):
                if any(k in content.lower() for k in ("evaluation-agent", "candidate evaluator")):
                    if any(ev in content.lower() for ev in ("eval-", "overall_verdict", "evaluation report", "graduated", "compiled candidate", "acceptance criteria")):
                        has_eval_agent = True

            if has_eval_agent:
                latest_eval_idx = idx

        if latest_eval_idx >= 0:
            new_defect_after_eval = False
            for idx in range(latest_eval_idx + 1, len(records)):
                r = records[idx]
                t = r.get("type", "")
                src = r.get("source", "")
                content = str(r.get("content", ""))
                if t == "USER_INPUT":
                    cl = extract_clean_user_message(content)
                    is_c, _ = is_meaningful_user_critique(cl, is_subagent=False, caller="academic-orchestrator")
                    if is_c:
                        new_defect_after_eval = True
                        break
                if t not in ("EPHEMERAL_MESSAGE",) and src not in ("SYSTEM_SDK",):
                    if "File Path: `file:///" not in content and "Total Lines:" not in content:
                        if any(k in content.lower() for k in ("validation_report.json", "overall_verdict", "checks_failed")):
                            if re.search(r'\boverall_verdict[\'":\s]+fail\b', content, re.IGNORECASE):
                                is_arp = any(k in content.lower() for k in (
                                    "correction required (academic-writer",
                                    "correction required: academic-writer",
                                    "actionable repair prescription",
                                    "re-generate",
                                    "recompile"
                                ))
                                if not is_arp:
                                    new_defect_after_eval = True
                                    break
            if not new_defect_after_eval:
                cand_dir = os.path.join(ROOT_DIR, ".agents", "learning", "candidates")
                has_pending = False
                if os.path.isdir(cand_dir):
                    for cf in os.listdir(cand_dir):
                        if cf.endswith(".json") and not cf.startswith("."):
                            try:
                                with open(os.path.join(cand_dir, cf), "r", encoding="utf-8") as fc:
                                    cd = json.load(fc)
                                if str(cd.get("status", "")).upper() in ("STAGED", "EVALUATED", "EVALUATION_PASSED") and str(cd.get("graduation_status", "")).upper() != "GRADUATED":
                                    has_pending = True
                                    break
                            except Exception:
                                pass
                if not has_pending:
                    learning_already_completed = True

        # Check if premature remediation was attempted before evolution completed
        has_learning_started = (any(
            any(k in sa for k in ("knowledge-curator", "trajectory-analyzer", "behavior-analyst"))
            for sa in invoked_subagents
        ) or is_user_critique or is_val_failure) and not learning_already_completed

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

        # 2a. Affirmative Learning Gate on Critique or Validation Failure:
        # If user reported critique or validation failed, the learning and evolution cascade MUST be invoked in this turn!
        if (is_user_critique or is_val_failure) and not learning_already_completed:
            trigger_label = "Critique" if is_user_critique else "Validation Failure"
            trigger_detail = clean_user if is_user_critique else val_summary
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
                    f"CONSTITUTIONAL VIOLATION (Directive 21 & Directive 21.1 - Uninvoked Learning Pipeline on {trigger_label}): "
                    f"A defect was detected ('{trigger_detail[:80]}...'), but the continuous learning cascade "
                    "was NOT executed in this turn! "
                    "Under Directive 21, Directive 21.1, and AP-2026-PATCHING-WITHOUT-LEARNING, you are strictly prohibited from bypassing learning, attempting "
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
                        target_file = m_clean
                        if not os.path.isfile(target_file):
                            alt = os.path.join(ROOT_DIR, m_clean.lstrip("/\\"))
                            if os.path.isfile(alt):
                                target_file = alt
                        if m_clean not in seen_json_paths and os.path.isfile(target_file):
                            seen_json_paths.add(m_clean)
                            try:
                                with open(target_file, "r", encoding="utf-8") as jf:
                                    jdata = json.load(jf)
                                if jdata.get("graduation_status") == "PENDING_GRADUATION":
                                    item_id = jdata.get("lesson_id") or os.path.basename(m_clean)
                                    pending_items.append((target_file, item_id, "PENDING_GRADUATION"))
                                elif jdata.get("status") == "STAGED" and jdata.get("target_component"):
                                    item_id = jdata.get("candidate_id") or os.path.basename(m_clean)
                                    pending_items.append((target_file, item_id, "STAGED"))
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
        caller = resolve_caller(payload)
        caller_clean = (caller or "").lower().strip()

        # Auditor agents (validation-agent, results-auditor, etc.) and learning subagents
        # are exempt from stop gates so they can report findings or benchmark diagnostics.
        if is_auditor_agent(caller_clean) or is_learning_subagent(caller_clean):
            return {"decision": "allow"}

        # 1. Post-Analysis Validation Reports (strictly scoped to current work)
        # Blocks ANY agent or delivery subagent if the current work stage validation report fails.
        ok, reason = IntegrityHooks.verify_post_analysis(workspaces, caller=caller, payload=payload)
        if not ok:
            return {"decision": "continue", "reason": reason}

        # 2. Specialist workers and subagents terminate cleanly once post-analysis passes,
        # without being subjected to orchestrator-level transcript / learning checks.
        is_subagent_call = (
            payload.get("isSubagent") or
            payload.get("parentConversationId") or
            payload.get("is_subagent") or
            (caller and caller_clean not in ("academic-orchestrator", "default", "main"))
        )
        if is_subagent_call:
            return {"decision": "allow"}

        # 3. Standalone Python Orchestrator Prohibition (Directive 12.1)
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
                    "reason": msg
                }

        # 4. Skill Modularity (Directive 18)
        ok, reason = IntegrityHooks.verify_skill_modularity(workspaces)
        if not ok:
            return {"decision": "continue", "reason": reason}

        # 5. State Machine Consistency (Invalid State Transition Detection)
        ok, reason = IntegrityHooks.verify_state_transitions(workspaces, caller=caller)
        if not ok:
            return {"decision": "continue", "reason": reason}

        # 6. Worker Return Structure (Phase 21 Invariant)
        ok, reason = IntegrityHooks.verify_worker_returns(workspaces, caller=caller)
        if not ok:
            return {"decision": "continue", "reason": reason}

        # 7. Missing Artifacts Detection (Triad Invariant & Manifest Deliverables)
        ok, reason = IntegrityHooks.verify_missing_artifacts(workspaces, caller=caller)
        if not ok:
            return {"decision": "continue", "reason": reason}

        # 8. Provenance Integrity Detection (Input/Output Hashes & Dependencies)
        ok, reason = IntegrityHooks.verify_provenance(workspaces, caller=caller)
        if not ok:
            return {"decision": "continue", "reason": reason}

        # 7. Transcript Checks (Binary Honesty & Multi-Agent Claims)
        transcript_path = resolve_transcript_path(payload)
        records = load_transcript(transcript_path) if transcript_path else []
        if records:
            ok, reason = IntegrityHooks.verify_binary_honesty(records)
            if not ok:
                return {"decision": "continue", "reason": reason}

            ok, reason = IntegrityHooks.verify_multiagent_truthfulness(records)
            if not ok:
                return {"decision": "continue", "reason": reason}

            ok, reason = IntegrityHooks.verify_conversational_language(records)
            if not ok:
                return {"decision": "continue", "reason": reason}

            # 8. Anti-Shortcut, Zero-Fastpath & No-Rush Invariant (Directive 25)
            ok, reason = IntegrityHooks.verify_anti_shortcut_and_no_rush(records)
            if not ok:
                return {"decision": "continue", "reason": reason}

            # 9. Learning & Evolution Pipeline Completion (Directive 21 & 21.1)
            ok, reason = IntegrityHooks.verify_learning_pipeline_completion(records, workspaces=workspaces)
            if not ok:
                return {"decision": "continue", "reason": reason}

        return {"decision": "allow"}

    @staticmethod
    def handle_post_invocation(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Advisory verification after model tool turn:
        Injects advisory if active stage validation report is FAIL.
        Strictly scoped to the CURRENT WORK stage(s); ignores unrelated stages.
        Suppressed for auditor agents and main developer.
        """
        caller = resolve_caller(payload)
        caller_clean = caller.lower().strip()
        is_auditor = any(k in caller_clean for k in (
            "validation", "auditor", "challenger", "judge", "inspector"
        ))
        is_main_dev = caller_clean in (
            "default", "main", "developer", "coding", "cli-developer", "ide-developer"
        )
        if is_auditor or is_main_dev:
            return {"injectSteps": [], "terminationBehavior": ""}

        workspaces = payload.get("workspacePaths", [])
        inject_steps = []
        active_stage_dirs = resolve_current_work_stage_dirs(
            workspaces=workspaces,
            payload=payload,
            caller=caller
        )
        for root in active_stage_dirs:
            v_path = os.path.join(root, "validation_report.json")
            if os.path.isfile(v_path):
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
