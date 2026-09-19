#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_approval_engine.py — Deterministic Academic Approval Engine ("The Hands")

Implements Phase 13 architectural requirements:
"Make approval an actual state: AWAITING_APPROVAL"

Flow:
Stage execution completed & validation passed
      ↓
State Machine: STAGE_VALIDATING -> STAGE_AWAITING_APPROVAL
      ↓
Approval Record created: approval_id, stage_id, artifact_hash, validation_hash, decision: PENDING
      ↓
User approves (via CLI/API)
      ↓
Approval Event emitted (MILESTONE_APPROVED)
      ↓
State Transition: STAGE_AWAITING_APPROVAL -> STAGE_APPROVED
      ↓
Next Stage Unlocked: STAGE_LOCKED -> STAGE_READY
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
    from scripts.academic_state_manager import (
        StrictStateMachine,
        StageState,
        StateManagementError,
        MissingApprovalError,
        UnmetPrerequisiteError
    )
    AcademicStateManager = StrictStateMachine
except ImportError:
    try:
        from academic_state_manager import (
            StrictStateMachine,
            StageState,
            StateManagementError,
            MissingApprovalError,
            UnmetPrerequisiteError
        )
        AcademicStateManager = StrictStateMachine
    except ImportError:
        AcademicStateManager = None
        StrictStateMachine = None


class ApprovalError(Exception):
    """Base exception for approval engine failures."""
    pass


class ApprovalPrerequisiteError(ApprovalError):
    """Raised when approval prerequisites (e.g. passing validation report) are not met."""
    pass


class ApprovalTamperError(ApprovalError):
    """Raised when artifact or validation hashes mutate while awaiting approval."""
    pass


def compute_sha256(filepath: str) -> str:
    """Computes SHA-256 cryptographic hash of a file on disk."""
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found for hash calculation: {filepath}")
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_approval_schema() -> Optional[Dict[str, Any]]:
    """Loads contracts/approval_record.schema.json."""
    schema_path = os.path.join(ROOT_DIR, "contracts", "approval_record.schema.json")
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def request_stage_approval(
    stage_id: str,
    state_dir: str,
    artifact_path: Optional[str] = None,
    validation_report_path: Optional[str] = None,
    project_id: Optional[str] = None,
    requester_agent: str = "academic-orchestrator",
    rationale: str = "Stage execution and validation complete; awaiting human gate approval."
) -> Dict[str, Any]:
    """
    Initiates formal human approval for a stage:
    1. Validates passing validation report
    2. Computes artifact_hash and validation_hash
    3. Transitions stage state: STAGE_VALIDATING -> STAGE_AWAITING_APPROVAL
    4. Writes approval_request.json and updates approvals.json
    """
    state_dir_abs = os.path.abspath(state_dir)
    os.makedirs(state_dir_abs, exist_ok=True)
    now_iso = datetime.now(timezone.utc).isoformat()

    # 1. Locate and verify passing validation report
    val_path = validation_report_path
    if not val_path:
        candidates = [
            os.path.join(state_dir_abs, "validation_report.json"),
            os.path.join(state_dir_abs, f"{stage_id}_validation.json"),
            os.path.join(state_dir_abs, "stages", stage_id, "validation_report.json")
        ]
        for c in candidates:
            if os.path.isfile(c):
                val_path = c
                break

    if not val_path or not os.path.isfile(val_path):
        raise ApprovalPrerequisiteError(
            f"Cannot request approval for stage '{stage_id}': no validation_report.json found on disk."
        )

    with open(val_path, "r", encoding="utf-8") as vf:
        val_data = json.load(vf)
    verdict = str(val_data.get("overall_verdict", val_data.get("verdict", ""))).strip().upper()
    if verdict != "PASS":
        raise ApprovalPrerequisiteError(
            f"Cannot request approval for stage '{stage_id}': validation report '{os.path.basename(val_path)}' "
            f"verdict is '{verdict}' (must be 'PASS')."
        )

    validation_hash = compute_sha256(val_path)

    # 2. Locate primary artifact or manifest
    art_path = artifact_path
    if not art_path:
        candidates = [
            os.path.join(state_dir_abs, "manifest.json"),
            os.path.join(state_dir_abs, f"{stage_id}.json"),
            os.path.join(state_dir_abs, f"{stage_id}.md"),
            os.path.join(state_dir_abs, "stages", stage_id, "manifest.json")
        ]
        for c in candidates:
            if os.path.isfile(c):
                art_path = c
                break

    if not art_path or not os.path.isfile(art_path):
        raise ApprovalPrerequisiteError(
            f"Cannot request approval for stage '{stage_id}': primary deliverable or manifest not found on disk."
        )

    artifact_hash = compute_sha256(art_path)

    # 3. Initialize AcademicStateManager and transition to STAGE_AWAITING_APPROVAL
    if AcademicStateManager is not None:
        sm = AcademicStateManager(state_dir=state_dir_abs, project_id=project_id)
        if stage_id not in sm.stages:
            sm.register_stage(
                stage_id=stage_id,
                title=f"Stage {stage_id}",
                initial_status=StageState.STAGE_VALIDATING.value
            )
        current_status = sm.stages[stage_id]["status"]
        if current_status == StageState.STAGE_RUNNING.value:
            sm.request_transition(
                target_type="STAGE",
                target_id=stage_id,
                target_state="STAGE_VALIDATING",
                actor=requester_agent,
                rationale="Execution completed; validating before approval request."
            )
            current_status = StageState.STAGE_VALIDATING.value

        if current_status == StageState.STAGE_VALIDATING.value:
            sm.request_transition(
                target_type="STAGE",
                target_id=stage_id,
                target_state="STAGE_AWAITING_APPROVAL",
                actor=requester_agent,
                rationale=rationale
            )
        elif current_status != StageState.STAGE_AWAITING_APPROVAL.value:
            raise StateManagementError(
                f"Cannot request approval for stage '{stage_id}': current state is '{current_status}' "
                f"(expected STAGE_VALIDATING or STAGE_AWAITING_APPROVAL)."
            )

    approval_id = f"APP-{stage_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    approval_record: Dict[str, Any] = {
        "contract_version": "1.0.0",
        "approval_id": approval_id,
        "stage_id": stage_id,
        "project_id": project_id or (sm.project_id if AcademicStateManager else "project"),
        "artifact_path": os.path.relpath(art_path, state_dir_abs),
        "artifact_hash": artifact_hash,
        "validation_report_path": os.path.relpath(val_path, state_dir_abs),
        "validation_hash": validation_hash,
        "requested_at": now_iso,
        "approved_by": None,
        "approved_at": None,
        "decision": "PENDING",
        "status": "PENDING",
        "is_approved": False,
        "comments": "",
        "target_artifacts": [os.path.relpath(art_path, state_dir_abs), os.path.relpath(val_path, state_dir_abs)]
    }

    # Validate against schema
    schema = load_approval_schema()
    if schema and jsonschema:
        try:
            jsonschema.validate(instance=approval_record, schema=schema)
        except Exception as se:
            raise ApprovalError(f"Approval record failed schema validation: {str(se)}")

    # Write approval_request.json to stage_dir
    req_file = os.path.join(state_dir_abs, "approval_request.json")
    with open(req_file, "w", encoding="utf-8") as rf:
        json.dump(approval_record, rf, indent=2, ensure_ascii=False)

    # Register in approvals.json
    appr_json_path = os.path.join(state_dir_abs, "approvals.json")
    apprs_data = {"approvals": []}
    if os.path.isfile(appr_json_path):
        try:
            with open(appr_json_path, "r", encoding="utf-8") as af:
                apprs_data = json.load(af)
        except Exception:
            apprs_data = {"approvals": []}
    apprs_data.setdefault("approvals", []).append(approval_record)
    with open(appr_json_path, "w", encoding="utf-8") as af:
        json.dump(apprs_data, af, indent=2, ensure_ascii=False)

    return approval_record


def approve_stage(
    approval_id: str,
    approved_by: str,
    state_dir: str,
    comments: str = "Stage deliverables and validation report approved.",
    digital_signature: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes explicit human approval:
    1. Verifies approval record exists and is PENDING
    2. Validates artifact_hash and validation_hash have not mutated (tamper check)
    3. Sets decision = 'APPROVED', status = 'GRANTED', is_approved = True
    4. Transitions stage state: STAGE_AWAITING_APPROVAL -> STAGE_APPROVED
    5. Unlocks downstream dependent stages: STAGE_LOCKED -> STAGE_READY
    6. Emits MILESTONE_APPROVED and NEXT_STAGE_UNLOCKED events
    """
    state_dir_abs = os.path.abspath(state_dir)
    appr_json_path = os.path.join(state_dir_abs, "approvals.json")
    req_file = os.path.join(state_dir_abs, "approval_request.json")

    # Load approval record
    target_record = None
    apprs_data = {"approvals": []}
    if os.path.isfile(appr_json_path):
        with open(appr_json_path, "r", encoding="utf-8") as af:
            apprs_data = json.load(af)
        for a in apprs_data.get("approvals", []):
            if a.get("approval_id") == approval_id:
                target_record = a
                break

    if not target_record and os.path.isfile(req_file):
        with open(req_file, "r", encoding="utf-8") as rf:
            rec = json.load(rf)
            if rec.get("approval_id") == approval_id:
                target_record = rec
                apprs_data.setdefault("approvals", []).append(target_record)

    if not target_record:
        raise ApprovalError(f"Approval ID '{approval_id}' not found in state directory '{state_dir_abs}'.")

    if target_record.get("decision") == "APPROVED":
        raise ApprovalError(f"Approval '{approval_id}' has already been approved.")

    stage_id = target_record.get("stage_id", "")

    # Cryptographic Tamper Check: verify artifact and validation report on disk
    art_path = target_record.get("artifact_path", "")
    art_full = art_path if os.path.isabs(art_path) else os.path.join(state_dir_abs, art_path)
    if not os.path.isfile(art_full):
        raise ApprovalTamperError(f"Primary artifact missing from disk: {art_full}")
    current_art_hash = compute_sha256(art_full)
    if current_art_hash.lower() != target_record.get("artifact_hash", "").lower():
        raise ApprovalTamperError(
            f"Tamper detected: Artifact '{art_path}' hash mutated while awaiting approval. "
            f"Expected {target_record.get('artifact_hash')}, got {current_art_hash}."
        )

    val_path = target_record.get("validation_report_path", "")
    val_full = val_path if os.path.isabs(val_path) else os.path.join(state_dir_abs, val_path)
    if not os.path.isfile(val_full):
        raise ApprovalTamperError(f"Validation report missing from disk: {val_full}")
    current_val_hash = compute_sha256(val_full)
    if current_val_hash.lower() != target_record.get("validation_hash", "").lower():
        raise ApprovalTamperError(
            f"Tamper detected: Validation report '{val_path}' hash mutated while awaiting approval. "
            f"Expected {target_record.get('validation_hash')}, got {current_val_hash}."
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    sig = digital_signature or f"SIG-{approved_by}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    # Update approval record
    target_record["decision"] = "APPROVED"
    target_record["status"] = "GRANTED"
    target_record["is_approved"] = True
    target_record["approved_by"] = approved_by
    target_record["approved_at"] = now_iso
    target_record["comments"] = comments
    target_record["digital_signature"] = sig

    # Save to disk
    with open(appr_json_path, "w", encoding="utf-8") as af:
        json.dump(apprs_data, af, indent=2, ensure_ascii=False)
    if os.path.isfile(req_file):
        with open(req_file, "w", encoding="utf-8") as rf:
            json.dump(target_record, rf, indent=2, ensure_ascii=False)

    # State Machine Transition: STAGE_AWAITING_APPROVAL -> STAGE_APPROVED
    unlocked_stages = []
    if AcademicStateManager is not None:
        sm = AcademicStateManager(state_dir=state_dir_abs)
        # Register in state manager's approvals
        sm.approvals = [a for a in sm.approvals if a.get("approval_id") != approval_id]
        sm.approvals.append(target_record)
        sm.save_all()

        sm.request_transition(
            target_type="STAGE",
            target_id=stage_id,
            target_state="STAGE_APPROVED",
            actor=approved_by,
            rationale=comments,
            authorization=target_record
        )

        # Inspect unlocked stages
        for s_id, s_data in sm.stages.items():
            if s_data.get("status") == StageState.STAGE_READY.value and s_id != stage_id:
                unlocked_stages.append(s_id)

    return {
        "approval_id": approval_id,
        "stage_id": stage_id,
        "decision": "APPROVED",
        "approved_by": approved_by,
        "approved_at": now_iso,
        "unlocked_stages": unlocked_stages,
        "approval_record": target_record
    }


def reject_stage(
    approval_id: str,
    rejected_by: str,
    state_dir: str,
    comments: str = "Stage rejected by human reviewer."
) -> Dict[str, Any]:
    """
    Executes explicit human rejection:
    1. Sets decision = 'REJECTED', status = 'REJECTED', is_approved = False
    2. Transitions stage state: STAGE_AWAITING_APPROVAL -> STAGE_REJECTED
    3. Downstream stages remain STAGE_LOCKED
    4. Emits MILESTONE_REJECTED event
    """
    state_dir_abs = os.path.abspath(state_dir)
    appr_json_path = os.path.join(state_dir_abs, "approvals.json")
    req_file = os.path.join(state_dir_abs, "approval_request.json")

    target_record = None
    apprs_data = {"approvals": []}
    if os.path.isfile(appr_json_path):
        with open(appr_json_path, "r", encoding="utf-8") as af:
            apprs_data = json.load(af)
        for a in apprs_data.get("approvals", []):
            if a.get("approval_id") == approval_id:
                target_record = a
                break

    if not target_record and os.path.isfile(req_file):
        with open(req_file, "r", encoding="utf-8") as rf:
            rec = json.load(rf)
            if rec.get("approval_id") == approval_id:
                target_record = rec
                apprs_data.setdefault("approvals", []).append(target_record)

    if not target_record:
        raise ApprovalError(f"Approval ID '{approval_id}' not found in state directory '{state_dir_abs}'.")

    stage_id = target_record.get("stage_id", "")
    now_iso = datetime.now(timezone.utc).isoformat()

    target_record["decision"] = "REJECTED"
    target_record["status"] = "REJECTED"
    target_record["is_approved"] = False
    target_record["approved_by"] = rejected_by
    target_record["approved_at"] = now_iso
    target_record["comments"] = comments

    with open(appr_json_path, "w", encoding="utf-8") as af:
        json.dump(apprs_data, af, indent=2, ensure_ascii=False)
    if os.path.isfile(req_file):
        with open(req_file, "w", encoding="utf-8") as rf:
            json.dump(target_record, rf, indent=2, ensure_ascii=False)

    if AcademicStateManager is not None:
        sm = AcademicStateManager(state_dir=state_dir_abs)
        sm.approvals = [a for a in sm.approvals if a.get("approval_id") != approval_id]
        sm.approvals.append(target_record)
        sm.save_all()

        sm.request_transition(
            target_type="STAGE",
            target_id=stage_id,
            target_state="STAGE_REJECTED",
            actor=rejected_by,
            rationale=comments,
            authorization=target_record
        )

    return {
        "approval_id": approval_id,
        "stage_id": stage_id,
        "decision": "REJECTED",
        "rejected_by": rejected_by,
        "rejected_at": now_iso,
        "approval_record": target_record
    }


def get_approval_status(state_dir: str, stage_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lists all approval records in state directory."""
    state_dir_abs = os.path.abspath(state_dir)
    appr_json_path = os.path.join(state_dir_abs, "approvals.json")
    records = []
    if os.path.isfile(appr_json_path):
        with open(appr_json_path, "r", encoding="utf-8") as af:
            apprs_data = json.load(af)
            records = apprs_data.get("approvals", [])
    if stage_id:
        records = [r for r in records if r.get("stage_id") == stage_id]
    return records


# ==============================================================================
# CLI Implementation
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="AcademicSuite Deterministic Approval Engine ('The Hands')"
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to execute")

    # request
    req_parser = subparsers.add_parser("request", help="Request human approval for a stage")
    req_parser.add_argument("--stage-id", required=True)
    req_parser.add_argument("--state-dir", required=True)
    req_parser.add_argument("--artifact", help="Path to primary artifact or manifest")
    req_parser.add_argument("--validation", help="Path to validation_report.json")
    req_parser.add_argument("--project-id", help="Project identifier")
    req_parser.add_argument("--agent", default="academic-orchestrator", help="Requester agent")
    req_parser.add_argument("--rationale", default="Stage complete; awaiting human gate.")

    # approve
    app_parser = subparsers.add_parser("approve", help="Grant human approval for a stage")
    app_parser.add_argument("--approval-id", required=True)
    app_parser.add_argument("--approved-by", required=True)
    app_parser.add_argument("--state-dir", required=True)
    app_parser.add_argument("--comments", default="Explicit approval granted.")
    app_parser.add_argument("--signature", help="Optional digital signature / ack")

    # reject
    rej_parser = subparsers.add_parser("reject", help="Reject a stage approval request")
    rej_parser.add_argument("--approval-id", required=True)
    rej_parser.add_argument("--rejected-by", required=True)
    rej_parser.add_argument("--state-dir", required=True)
    rej_parser.add_argument("--comments", default="Stage rejected.")

    # status
    stat_parser = subparsers.add_parser("status", help="Inspect approval records")
    stat_parser.add_argument("--state-dir", required=True)
    stat_parser.add_argument("--stage-id", help="Filter by stage ID")
    stat_parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "request":
        try:
            rec = request_stage_approval(
                stage_id=args.stage_id,
                state_dir=args.state_dir,
                artifact_path=args.artifact,
                validation_report_path=args.validation,
                project_id=args.project_id,
                requester_agent=args.agent,
                rationale=args.rationale
            )
            print(f"SUCCESS: Approval requested [ID: {rec['approval_id']}] for stage '{args.stage_id}'. "
                  f"State transitioned to STAGE_AWAITING_APPROVAL. Downstream stages remain locked.")
            sys.exit(0)
        except Exception as e:
            print(f"ERROR: {str(e)}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "approve":
        try:
            res = approve_stage(
                approval_id=args.approval_id,
                approved_by=args.approved_by,
                state_dir=args.state_dir,
                comments=args.comments,
                digital_signature=args.signature
            )
            print(f"SUCCESS: Approval '{args.approval_id}' GRANTED by '{args.approved_by}'. "
                  f"Stage '{res['stage_id']}' transitioned to STAGE_APPROVED. "
                  f"Unlocked stages: {res['unlocked_stages']}")
            sys.exit(0)
        except Exception as e:
            print(f"ERROR: {str(e)}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "reject":
        try:
            res = reject_stage(
                approval_id=args.approval_id,
                rejected_by=args.rejected_by,
                state_dir=args.state_dir,
                comments=args.comments
            )
            print(f"SUCCESS: Approval '{args.approval_id}' REJECTED by '{args.rejected_by}'. "
                  f"Stage '{res['stage_id']}' transitioned to STAGE_REJECTED.")
            sys.exit(0)
        except Exception as e:
            print(f"ERROR: {str(e)}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "status":
        records = get_approval_status(state_dir=args.state_dir, stage_id=args.stage_id)
        if args.json:
            print(json.dumps(records, indent=2, ensure_ascii=False))
        else:
            print(f"Found {len(records)} approval records:")
            for r in records:
                print(f"  * [{r.get('decision', 'PENDING')}] {r.get('approval_id')} (Stage: {r.get('stage_id')}) "
                      f"Requested: {r.get('requested_at')} ApprovedBy: {r.get('approved_by')}")
        sys.exit(0)


if __name__ == "__main__":
    main()
