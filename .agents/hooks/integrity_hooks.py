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


def load_transcript(transcript_path: Optional[str]) -> List[Dict[str, Any]]:
    """Loads and parses transcript.jsonl safely."""
    if not transcript_path or not os.path.exists(transcript_path):
        return []
    records = []
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    except Exception as e:
        sys.stderr.write(f"[integrity_hooks] Error reading transcript: {e}\n")
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
        """
        for ws in workspaces:
            for root, dirs, files in os.walk(ws):
                if "manifest.json" in files:
                    m_path = os.path.join(root, "manifest.json")
                    try:
                        with open(m_path, "r", encoding="utf-8") as mf:
                            m_data = json.load(mf)
                        # Check schema title / contract_version
                        if m_data.get("contract_version") and "artifacts" in m_data:
                            # Verify declared artifacts exist on disk
                            base_dir = root
                            for art in m_data.get("artifacts", []):
                                a_path = art.get("path", "")
                                a_full = a_path if os.path.isabs(a_path) else os.path.join(base_dir, a_path)
                                if not os.path.exists(a_full) or os.path.getsize(a_full) == 0:
                                    return False, (
                                        f"HARD HOOK ENFORCEMENT (Manifest Verification): Stage in '{root}' declares "
                                        f"artifact '{a_path}' in manifest.json, but it is missing or empty on disk."
                                    )
                    except Exception as e:
                        return False, f"HARD HOOK ENFORCEMENT (Manifest Verification): Failed to parse {m_path}: {e}"
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
                        stages = cs.get("stages", {})
                        approvals = []
                        appr_path = os.path.join(root, "approvals.json")
                        if os.path.exists(appr_path):
                            try:
                                with open(appr_path, "r", encoding="utf-8") as af:
                                    approvals = json.load(af).get("approvals", [])
                            except Exception:
                                approvals = []

                        for stage_id, sdata in stages.items():
                            if not isinstance(sdata, dict):
                                continue
                            history = sdata.get("history", [])
                            for trn in history:
                                if not isinstance(trn, dict):
                                    continue
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
                    except Exception:
                        pass
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
                        stages = cs.get("stages", {})
                        for stage_id, sdata in stages.items():
                            if not isinstance(sdata, dict):
                                continue
                            w_ret = sdata.get("worker_return")
                            if w_ret is not None:
                                val_res = validate_worker_return_payload(w_ret)
                                if not val_res.get("valid"):
                                    err_msg = "; ".join(val_res.get("errors", ["Invalid worker return"]))
                                    return False, (
                                        f"HARD HOOK ENFORCEMENT (Worker Return Invariant Guard - Phase 21): "
                                        f"Stage '{stage_id}' in '{root}' recorded an invalid worker return: {err_msg}"
                                    )
                            for trn in sdata.get("history", []):
                                if isinstance(trn, dict) and "worker_return" in trn:
                                    hw_ret = trn["worker_return"]
                                    val_res = validate_worker_return_payload(hw_ret)
                                    if not val_res.get("valid"):
                                        err_msg = "; ".join(val_res.get("errors", ["Invalid worker return"]))
                                        return False, (
                                            f"HARD HOOK ENFORCEMENT (Worker Return Invariant Guard - Phase 21): "
                                            f"Stage '{stage_id}' in '{root}' history recorded an invalid worker return: {err_msg}"
                                        )
                    except Exception:
                        pass
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
                        base_dir = root
                        stage_id = m_data.get("stage_id", os.path.basename(root))

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
                    except Exception:
                        pass
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
        Verifies that any completed stage has a passing validation report (overall_verdict: PASS).
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
                    verdict = str(val_data.get("overall_verdict", val_data.get("verdict", ""))).strip().upper()
                    if verdict == "FAIL":
                        return False, (
                            f"HARD HOOK ENFORCEMENT (Post-Analysis Validation Gate): Stage artifacts in '{s_dir}' "
                            f"failed deterministic validation (overall_verdict: FAIL). Fix errors before completing."
                        )
                except Exception:
                    pass
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
        """
        workspaces = payload.get("workspacePaths", [])

        # 1. Standalone Python Orchestrator Prohibition (Directive 12.1)
        for ws in workspaces:
            forbidden_file = os.path.join(ws, ".agents", "skills", "academic-suite-orchestrator", "scripts", "multi_agent_orchestrator.py")
            if os.path.exists(forbidden_file):
                return {
                    "decision": "continue",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Directive 12.1 - Sole Orchestrator Mandate): "
                        f"Forbidden file '{forbidden_file}' detected on disk. Standalone Python multi-agent "
                        "orchestrators are prohibited. Antigravity is the sole agent conductor. Delete this file immediately."
                    )
                }

        # 2. Skill Modularity (Directive 18)
        ok, reason = IntegrityHooks.verify_skill_modularity(workspaces)
        if not ok:
            return {"decision": "continue", "reason": reason}

        # 3. State Machine Consistency (Invalid State Transition Detection)
        ok, reason = IntegrityHooks.verify_state_transitions(workspaces)
        if not ok:
            return {"decision": "continue", "reason": reason}

        # 3.5 Worker Return Structure (Phase 21 Invariant)
        ok, reason = IntegrityHooks.verify_worker_returns(workspaces)
        if not ok:
            return {"decision": "continue", "reason": reason}

        # 4. Missing Artifacts Detection (Triad Invariant & Manifest Deliverables)
        ok, reason = IntegrityHooks.verify_missing_artifacts(workspaces)
        if not ok:
            return {"decision": "continue", "reason": reason}

        # 5. Provenance Integrity Detection (Input/Output Hashes & Dependencies)
        ok, reason = IntegrityHooks.verify_provenance(workspaces)
        if not ok:
            return {"decision": "continue", "reason": reason}

        # 6. Post-Analysis Validation Reports
        ok, reason = IntegrityHooks.verify_post_analysis(workspaces)
        if not ok:
            return {"decision": "continue", "reason": reason}

        # 7. Transcript Checks (Binary Honesty & Multi-Agent Claims)
        transcript_path = payload.get("transcriptPath")
        cid = payload.get("conversationId")
        if not transcript_path and cid:
            cand = os.path.expanduser(f"~/.gemini/antigravity/brain/{cid}/.system_generated/logs/transcript.jsonl")
            if os.path.exists(cand):
                transcript_path = cand

        records = load_transcript(transcript_path) if transcript_path else []
        if records:
            ok, reason = IntegrityHooks.verify_binary_honesty(records)
            if not ok:
                return {"decision": "continue", "reason": reason}

            ok, reason = IntegrityHooks.verify_multiagent_truthfulness(records)
            if not ok:
                return {"decision": "continue", "reason": reason}

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
                        if v_data.get("overall_verdict") == "FAIL":
                            inject_steps.append({
                                "ephemeralMessage": (
                                    f"STAGE VERIFICATION ADVISORY: Validation report in '{root}' "
                                    f"has overall_verdict: FAIL. Please run deterministic validators and resolve errors."
                                )
                            })
                            break
                    except Exception:
                        pass
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
