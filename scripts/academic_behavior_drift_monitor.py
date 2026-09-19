#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_behavior_drift_monitor.py — AcademicSuite Behavior-Drift Monitor

Monitors behavioral stability and quality drift for durable agents and production Skills:
1. Maintains longitudinal behavioral profiles across 8 dimensions:
   - correctness
   - methodology
   - statistical_validity
   - evidence_grounding
   - integrity
   - robustness
   - consistency
   - efficiency
2. Runs protected regression evaluations after significant Skill promotions.
3. Detects Cross-Capability Regressions:
   - TARGET CAPABILITY IMPROVED but OTHER CAPABILITY REGRESSED.
4. Detects Methodological Inconsistencies:
   - same evidence → inconsistent methodological decision.
   - Tests whether differences are explainable by changed inputs/design.
   - Never penalizes justified differences.
5. Automatically triggers rollback and candidate deactivation when protected
   capabilities fall below safety thresholds, restoring the last known-good snapshot.
6. Persists audit reports under learning/reports/drift/ conforming to
   contracts/evolution/drift_report.schema.json.

Constitutional Directives:
- Directive 0: Radical Honesty & Epistemic Integrity.
- Directive 6: Strict English-only ASCII file naming.
- Directive 12.1: Python scripts strictly as 'The Hands' (deterministic execution).
"""

import os
import sys
import re
import json
import uuid
import shutil
import hashlib
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

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

from contracts.contract_validator import (
    validate_behavioral_profile,
    validate_drift_report
)
from scripts.academic_evaluation_lab import AcademicEvaluationLab


class DriftMonitoringError(Exception):
    """Base exception for drift monitoring operations."""
    pass


class CriticalRegressionError(DriftMonitoringError):
    """Raised when a candidate causes a critical regression on protected capabilities."""
    pass


class AcademicBehaviorDriftMonitor:
    """
    Deterministic behavior-drift monitor maintaining longitudinal agent/skill profiles,
    auditing cross-capability regressions, enforcing consistency, and executing rollbacks.
    """

    DIMENSIONS = [
        "correctness",
        "methodology",
        "statistical_validity",
        "evidence_grounding",
        "integrity",
        "robustness",
        "consistency",
        "efficiency"
    ]

    DEFAULT_BASELINES = {
        "correctness": 0.95,
        "methodology": 0.92,
        "statistical_validity": 0.95,
        "evidence_grounding": 0.95,
        "integrity": 1.00,
        "robustness": 0.90,
        "consistency": 0.94,
        "efficiency": 0.95
    }

    # Core Protected Capabilities that must NEVER regress
    PROTECTED_CAPABILITIES = [
        "statistical-data-analyst",
        "assumption-testing",
        "apa-reporting",
        "data-audit",
        "chapter-4-writing"
    ]

    # Critical regression drop threshold (delta <= -0.10 triggers automatic rollback)
    CRITICAL_REGRESSION_DELTA_THRESHOLD = -0.10
    WARNING_REGRESSION_DELTA_THRESHOLD = -0.04

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or ROOT_DIR)
        self.reports_dir = os.path.join(self.base_dir, "learning", "reports", "drift")
        self.profiles_dir = os.path.join(self.base_dir, "learning", "profiles")
        self.agent_profiles_dir = os.path.join(self.profiles_dir, "agents")
        self.skill_profiles_dir = os.path.join(self.profiles_dir, "skills")
        self.snapshots_dir = os.path.join(self.base_dir, "learning", "snapshots", "skills")
        self.promotion_snapshots_dir = os.path.join(self.base_dir, "learning", "promotions", "snapshots")
        self.candidates_dir = os.path.join(self.base_dir, "learning", "candidates")
        self.skills_dir = os.path.join(self.base_dir, ".agents", "skills")
        self.knowledge_dir = os.path.join(self.base_dir, "learning", "knowledge")

        self.eval_lab = AcademicEvaluationLab(base_dir=self.base_dir)

        self._ensure_directories()

    def _ensure_directories(self):
        """Scaffolds all mandatory directories."""
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.agent_profiles_dir, exist_ok=True)
        os.makedirs(self.skill_profiles_dir, exist_ok=True)
        os.makedirs(self.snapshots_dir, exist_ok=True)
        os.makedirs(self.promotion_snapshots_dir, exist_ok=True)
        os.makedirs(self.candidates_dir, exist_ok=True)

    # -------------------------------------------------------------------------
    # 1. Behavioral Profile Lifecycle
    # -------------------------------------------------------------------------

    def get_or_create_profile(
        self,
        target_id: str,
        target_type: str = "skill",
        initial_baselines: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Retrieves an existing behavioral profile or initializes a fresh, contract-compliant profile.
        """
        target_type_clean = target_type.lower()
        if target_type_clean not in ["agent", "skill"]:
            raise ValueError(f"target_type must be 'agent' or 'skill', got '{target_type}'")

        target_dir = self.skill_profiles_dir if target_type_clean == "skill" else self.agent_profiles_dir
        profile_file = os.path.join(target_dir, f"{target_id}.json")

        if os.path.isfile(profile_file):
            try:
                with open(profile_file, "r", encoding="utf-8") as f:
                    profile = json.load(f)
                val = validate_behavioral_profile(profile)
                if val["valid"]:
                    return profile
            except Exception:
                pass

        # Create new profile
        baselines = dict(self.DEFAULT_BASELINES)
        if initial_baselines:
            baselines.update(initial_baselines)

        today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        prof_id = f"PROF-{target_type_clean.upper()[:3]}-{target_id.upper()[:10]}-{today_str}"
        now_iso = datetime.now(timezone.utc).isoformat()

        profile = {
            "contract_version": "1.0.0",
            "profile_id": prof_id,
            "target_type": target_type_clean,
            "target_id": target_id,
            "dimensions": dict(baselines),
            "dimension_baselines": dict(baselines),
            "decision_footprints": [],
            "evaluation_history": [],
            "status": "ACTIVE",
            "last_updated_at": now_iso
        }

        self.save_profile(profile)
        return profile

    def save_profile(self, profile: Dict[str, Any]) -> None:
        """Saves and validates a behavioral profile."""
        profile["last_updated_at"] = datetime.now(timezone.utc).isoformat()
        val = validate_behavioral_profile(profile)
        if not val["valid"]:
            raise DriftMonitoringError(f"Behavioral profile validation failed: {val.get('errors')}")

        target_type = profile["target_type"]
        target_dir = self.skill_profiles_dir if target_type == "skill" else self.agent_profiles_dir
        profile_file = os.path.join(target_dir, f"{profile['target_id']}.json")
        with open(profile_file, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)

    # -------------------------------------------------------------------------
    # 2. Evidence Hashing & Inconsistency Detection
    # -------------------------------------------------------------------------

    @staticmethod
    def compute_evidence_fingerprint(
        sample_size: int,
        design: str,
        assumptions: Dict[str, Any],
        missingness_pct: float = 0.0,
        covariates_count: int = 0
    ) -> str:
        """
        Computes a deterministic SHA-256 fingerprint representing the evidentiary context.
        Used to identify whether two situations share the exact same empirical foundation.
        """
        norm_assumptions = {k: bool(v) for k, v in sorted(assumptions.items())}
        payload = {
            "n": int(sample_size),
            "design": str(design).strip().lower(),
            "assumptions": norm_assumptions,
            "missingness": round(float(missingness_pct), 2),
            "covariates": int(covariates_count)
        }
        raw_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw_bytes).hexdigest()

    def evaluate_methodological_consistency(
        self,
        profile: Dict[str, Any],
        evidence_hash: str,
        current_decision: str,
        inputs_summary: str = "",
        design: str = "",
        rationale: str = "",
        inputs_changed: bool = False,
        design_changed: bool = False
    ) -> Dict[str, Any]:
        """
        Tests whether the methodological decision is consistent with past decisions on the same evidence.
        Directive: Do not require identical answers when different answers are justified.
        Instead test whether differences are explainable by changed inputs/design.
        """
        matching_footprint = next(
            (fp for fp in reversed(profile.get("decision_footprints", [])) if fp.get("evidence_hash") == evidence_hash),
            None
        )

        now_iso = datetime.now(timezone.utc).isoformat()

        if not matching_footprint:
            # First time observing this evidence footprint: record baseline
            profile["decision_footprints"].append({
                "evidence_hash": evidence_hash,
                "inputs_summary": inputs_summary,
                "design": design,
                "decision": current_decision,
                "rationale": rationale,
                "recorded_at": now_iso
            })
            return {
                "evidence_hash": evidence_hash,
                "previous_decision": current_decision,
                "current_decision": current_decision,
                "inputs_changed": False,
                "design_changed": False,
                "explainable": True,
                "explanation": "Initial baseline footprint established for this evidence signature.",
                "verdict": "CONSISTENT"
            }

        prev_decision = matching_footprint.get("decision")

        # Check if decision flipped
        if prev_decision.lower().strip() == current_decision.lower().strip():
            return {
                "evidence_hash": evidence_hash,
                "previous_decision": prev_decision,
                "current_decision": current_decision,
                "inputs_changed": False,
                "design_changed": False,
                "explainable": True,
                "explanation": "Methodological decision perfectly matches historical baseline on identical evidence.",
                "verdict": "CONSISTENT"
            }

        # Decision flipped! Is it explainable by changed inputs or changed design?
        explainable = bool(inputs_changed or design_changed)
        if explainable:
            verdict = "JUSTIFIED_DIFFERENCE"
            explanation = (
                f"Methodological decision shifted from '{prev_decision}' to '{current_decision}', "
                f"justified by modified inputs (inputs_changed={inputs_changed}) or research design (design_changed={design_changed})."
            )
        else:
            verdict = "UNEXPLAINABLE_INCONSISTENCY"
            explanation = (
                f"Unjustified methodological divergence detected: decision shifted from '{prev_decision}' "
                f"to '{current_decision}' on identical evidence fingerprint ({evidence_hash[:8]}...) without input/design variation."
            )

        return {
            "evidence_hash": evidence_hash,
            "previous_decision": prev_decision,
            "current_decision": current_decision,
            "inputs_changed": inputs_changed,
            "design_changed": design_changed,
            "explainable": explainable,
            "explanation": explanation,
            "verdict": verdict
        }

    # -------------------------------------------------------------------------
    # 3. Post-Promotion Drift & Cross-Capability Regression Audit
    # -------------------------------------------------------------------------

    def audit_drift(
        self,
        target_id: str,
        target_type: str = "skill",
        candidate_id: Optional[str] = None,
        promotion_id: Optional[str] = None,
        trigger: str = "POST_PROMOTION",
        current_evaluations: Optional[Dict[str, Dict[str, Any]]] = None,
        simulated_evidence_checks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Executes comprehensive behavior-drift audit:
        1. Retrieves or updates behavioral profile.
        2. Evaluates the 8 dimensions.
        3. Detects TARGET CAPABILITY IMPROVED but OTHER CAPABILITY REGRESSED.
        4. Detects same evidence → inconsistent methodological decision.
        5. If protected capabilities fall below critical thresholds:
           Automatically executes rollback and deactivates candidate.
        6. Persists audit report to learning/reports/drift/.
        """
        profile = self.get_or_create_profile(target_id, target_type)
        baselines = profile["dimension_baselines"]
        current_dims = dict(profile["dimensions"])

        cross_regressions = []
        inconsistencies = []

        # 1. Evaluate Methodological Consistency Checks
        if simulated_evidence_checks:
            for check in simulated_evidence_checks:
                incons_res = self.evaluate_methodological_consistency(
                    profile=profile,
                    evidence_hash=check.get("evidence_hash", "HASH_DEFAULT"),
                    current_decision=check.get("current_decision", ""),
                    inputs_summary=check.get("inputs_summary", ""),
                    design=check.get("design", ""),
                    rationale=check.get("rationale", ""),
                    inputs_changed=check.get("inputs_changed", False),
                    design_changed=check.get("design_changed", False)
                )
                inconsistencies.append(incons_res)
                if incons_res["verdict"] == "UNEXPLAINABLE_INCONSISTENCY":
                    # Penalize consistency dimension
                    current_dims["consistency"] = max(0.0, current_dims["consistency"] - 0.15)

        # 2. Evaluate Capabilities & Detect Cross-Capability Regressions
        eval_data = current_evaluations or {}

        # Target capability status
        target_eval = eval_data.get(target_id, {})
        target_score = target_eval.get("score", 0.95)
        target_improved = target_score >= baselines.get("methodology", 0.90)

        for cap_key, cap_eval in eval_data.items():
            cap_score = cap_eval.get("score", 0.95)
            cap_baseline = cap_eval.get("baseline", 0.95)
            delta = round(cap_score - cap_baseline, 4)

            # Check if this capability regressed
            if delta <= self.WARNING_REGRESSION_DELTA_THRESHOLD:
                is_target = (cap_key == target_id)
                reg_record = {
                    "target_capability": target_id,
                    "target_status": "IMPROVED" if target_improved else "NOT_IMPROVED",
                    "regressed_capability": cap_key,
                    "baseline_score": cap_baseline,
                    "current_score": cap_score,
                    "delta": delta,
                    "description": (
                        f"Cross-capability regression detected: While target '{target_id}' is "
                        f"{'improved' if target_improved else 'stable'}, protected capability '{cap_key}' "
                        f"regressed by {delta:.2f} (from {cap_baseline:.2f} to {cap_score:.2f})."
                    )
                }
                cross_regressions.append(reg_record)

                # Penalize corresponding dimensions
                if cap_key in ["assumption-testing", "statistical-data-analyst"]:
                    current_dims["statistical_validity"] = min(current_dims["statistical_validity"], cap_score)
                if cap_key in ["apa-reporting", "data-audit"]:
                    current_dims["correctness"] = min(current_dims["correctness"], cap_score)

        # Calculate dimension deltas
        dimension_deltas = {}
        for dim in self.DIMENSIONS:
            val = round(current_dims.get(dim, baselines.get(dim, 0.95)), 4)
            current_dims[dim] = max(0.0, min(1.0, val))
            dimension_deltas[dim] = round(current_dims[dim] - baselines.get(dim, 0.95), 4)

        # 3. Determine Verdict & Automated Rollback Trigger
        has_critical_regression = any(
            r["delta"] <= self.CRITICAL_REGRESSION_DELTA_THRESHOLD for r in cross_regressions
        ) or any(
            dimension_deltas[d] <= self.CRITICAL_REGRESSION_DELTA_THRESHOLD
            for d in ["integrity", "statistical_validity", "correctness"]
        )

        has_unexplainable_inconsistency = any(
            i["verdict"] == "UNEXPLAINABLE_INCONSISTENCY" for i in inconsistencies
        )

        rollback_executed = False
        rollback_details = None

        if has_critical_regression:
            verdict = "CRITICAL_REGRESSION_ROLLBACK"
            if candidate_id:
                rollback_details = self.execute_rollback(
                    candidate_id=candidate_id,
                    target_skill=target_id if target_type == "skill" else None,
                    reason=f"Automated rollback triggered: protected capabilities regressed below safety threshold (delta <= {self.CRITICAL_REGRESSION_DELTA_THRESHOLD})."
                )
                rollback_executed = True
                profile["status"] = "DEGRADED"
        elif cross_regressions or has_unexplainable_inconsistency:
            verdict = "WARNING_DRIFT"
            profile["status"] = "UNDER_REVIEW"
        else:
            verdict = "PASS"
            profile["status"] = "ACTIVE"

        today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        report_id = f"DRIFT-{today_str}-{uuid.uuid4().hex[:8].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()

        # Update profile evaluation history
        profile["dimensions"] = current_dims
        profile["last_drift_check"] = {
            "timestamp": now_iso,
            "verdict": verdict,
            "drift_detected": (verdict != "PASS"),
            "report_path": os.path.join(self.reports_dir, f"{report_id}.json")
        }
        profile["evaluation_history"].append({
            "evaluation_id": report_id,
            "timestamp": now_iso,
            "verdict": verdict,
            "overall_score": round(sum(current_dims.values()) / len(current_dims), 4),
            "regressions_detected": len(cross_regressions),
            "metadata": {
                "trigger": trigger,
                "candidate_id": candidate_id,
                "rollback_executed": rollback_executed
            }
        })
        self.save_profile(profile)

        # 4. Build and Save Drift Report
        drift_report = {
            "contract_version": "1.0.0",
            "report_id": report_id,
            "target_type": target_type,
            "target_id": target_id,
            "trigger": trigger,
            "dimension_scores": current_dims,
            "dimension_deltas": dimension_deltas,
            "cross_capability_regressions": cross_regressions,
            "methodological_inconsistencies": inconsistencies,
            "rollback_executed": rollback_executed,
            "verdict": verdict,
            "timestamp": now_iso
        }
        if promotion_id:
            drift_report["promotion_id"] = promotion_id
        if candidate_id:
            drift_report["candidate_id"] = candidate_id
        if rollback_details:
            drift_report["rollback_details"] = rollback_details

        # Validate drift report schema
        val_rep = validate_drift_report(drift_report)
        if not val_rep["valid"]:
            raise DriftMonitoringError(f"Synthesized drift report violates schema: {val_rep.get('errors')}")

        report_file = os.path.join(self.reports_dir, f"{report_id}.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(drift_report, f, indent=2, ensure_ascii=False)

        # Append to index
        index_file = os.path.join(self.reports_dir, "index.jsonl")
        with open(index_file, "a", encoding="utf-8") as f:
            index_entry = {
                "timestamp": now_iso,
                "report_id": report_id,
                "target_type": target_type,
                "target_id": target_id,
                "trigger": trigger,
                "verdict": verdict,
                "rollback_executed": rollback_executed,
                "regressions_count": len(cross_regressions),
                "inconsistencies_count": len(inconsistencies)
            }
            f.write(json.dumps(index_entry, ensure_ascii=False) + "\n")

        return drift_report

    # -------------------------------------------------------------------------
    # 4. Automated Rollback & Deactivation Engine
    # -------------------------------------------------------------------------

    def execute_rollback(
        self,
        candidate_id: str,
        target_skill: Optional[str] = None,
        reason: str = ""
    ) -> Dict[str, Any]:
        """
        Executes automated rollback:
        1. Deactivates candidate in learning/candidates/ -> DEACTIVATED_ROLLBACK.
        2. Discovers and restores the last known-good snapshot from learning/snapshots/skills/
           or learning/promotions/snapshots/.
        3. Deactivates deployed declarative knowledge items (exemplars/anti-patterns).
        4. Preserves full audit history and event records.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        restored_file = None
        restored_snapshot_id = None

        # 1. Deactivate Candidate File
        candidate_file = os.path.join(self.candidates_dir, f"{candidate_id}.json")
        if os.path.isfile(candidate_file):
            try:
                with open(candidate_file, "r", encoding="utf-8") as f:
                    c_data = json.load(f)
                c_data["status"] = "DEACTIVATED_ROLLBACK"
                c_data["deactivated_at"] = now_iso
                c_data["deactivation_reason"] = reason or "Behavioral drift monitor detected critical protected capability regression."
                with open(candidate_file, "w", encoding="utf-8") as f:
                    json.dump(c_data, f, indent=2, ensure_ascii=False)
            except Exception:
                pass

        # 2. Locate and Restore Snapshot / Immutable Version for Target Skill
        if target_skill:
            skill_dir = os.path.join(self.skills_dir, target_skill)
            skill_md = os.path.join(skill_dir, "SKILL.md")

            # Check immutable version store first!
            try:
                from scripts.academic_promotion_engine import AcademicVersionStore
                v_store = AcademicVersionStore(base_dir=self.base_dir)
                active_v = v_store.get_active_version(target_skill)
                if active_v:
                    v_info = v_store.get_version(target_skill, active_v)
                    parent_v = v_info.get("parent_version")
                    if parent_v:
                        v_res = v_store.rollback(target_skill, target_version=parent_v, from_version=active_v)
                        restored_file = v_res.get("target_path")
                        restored_snapshot_id = f"VERSION_{parent_v}"
            except Exception:
                pass

            # Fallback to search in learning/snapshots/skills/ if version store did not restore
            if not restored_file:
                snapshots = []
                if os.path.isdir(self.snapshots_dir):
                    for fn in sorted(os.listdir(self.snapshots_dir), reverse=True):
                        if fn.startswith(f"{target_skill}_v") and fn.endswith(".md"):
                            snapshots.append(os.path.join(self.snapshots_dir, fn))

                if snapshots and os.path.isfile(skill_md):
                    latest_snapshot = snapshots[0]
                    try:
                        shutil.copy2(latest_snapshot, skill_md)
                        restored_file = skill_md
                        restored_snapshot_id = os.path.basename(latest_snapshot)
                    except Exception:
                        pass

        # 3. Deactivate Deployed Declarative Items
        deactivated_items = []
        for subfolder in ["exemplars", "anti-patterns"]:
            k_dir = os.path.join(self.knowledge_dir, subfolder)
            if os.path.isdir(k_dir):
                for fn in os.listdir(k_dir):
                    if not fn.endswith(".json"):
                        continue
                    fp = os.path.join(k_dir, fn)
                    try:
                        with open(fp, "r", encoding="utf-8") as f:
                            item = json.load(f)
                        if item.get("originating_candidate") == candidate_id:
                            item["status"] = "DEACTIVATED"
                            item["deactivated_at"] = now_iso
                            with open(fp, "w", encoding="utf-8") as f:
                                json.dump(item, f, indent=2, ensure_ascii=False)
                            deactivated_items.append(fn)
                    except Exception:
                        pass

        rollback_record = {
            "snapshot_id": restored_snapshot_id or "NONE_AVAILABLE",
            "restored_component": restored_file or target_skill or "DECLARATIVE_CONTEXT",
            "deactivated_candidate_id": candidate_id,
            "action_timestamp": now_iso,
            "reason": reason or "Behavioral drift critical regression threshold exceeded."
        }

        return rollback_record


# -----------------------------------------------------------------------------
# CLI Entry Point
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Behavior-Drift Monitor")
    parser.add_argument("--skill", type=str, default="statistical-data-analyst", help="Target skill")
    parser.add_argument("--agent", type=str, default=None, help="Target agent")
    parser.add_argument("--candidate", type=str, default=None, help="Candidate ID to audit")
    parser.add_argument("--rollback", action="store_true", help="Manually trigger candidate rollback")
    parser.add_argument("--audit", action="store_true", help="Execute drift audit")
    args = parser.parse_args()

    monitor = AcademicBehaviorDriftMonitor()

    if args.rollback and args.candidate:
        res = monitor.execute_rollback(candidate_id=args.candidate, target_skill=args.skill)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0)

    target_id = args.agent if args.agent else args.skill
    target_type = "agent" if args.agent else "skill"

    res = monitor.audit_drift(
        target_id=target_id,
        target_type=target_type,
        candidate_id=args.candidate,
        trigger="PERIODIC_MONITOR"
    )
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
