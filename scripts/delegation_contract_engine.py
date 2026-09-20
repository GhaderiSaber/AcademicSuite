#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/delegation_contract_engine.py — Formal Delegation Contract Engine (Phase 22)

Mandate:
Every delegated task in AcademicSuite must have a structured contract.
1. Task specification fields (10 mandatory):
   - task_id
   - parent_agent
   - worker_agent
   - objective
   - inputs
   - required_artifacts
   - acceptance_criteria
   - constraints
   - verification_method
   - deadline

2. Worker return fields (6 mandatory):
   - status (SUCCESS, FAILED, BLOCKED)
   - artifacts (list of produced files on disk)
   - evidence (exact test statistics, parameters, df, effect sizes)
   - validation (independent validation report summary and verdict)
   - warnings (operational warnings, anomalies encountered)
   - limitations (methodological/statistical limitations)

3. Prevents informal anti-patterns:
   - Academic-Orchestrator: "Analyze this." (REJECTED)
   - Worker: "Done." (REJECTED)
   - Academic-Orchestrator: "Great." (REJECTED without validator sign-off)

Workflow:
   Academic-Orchestrator
         ↓ (formal task contract)
       worker
         ↓ (formal evidence / return)
      validator (independent validation)
         ↓ (verdict)
   Academic-Orchestrator
"""

import os
import sys
import re
import json
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Union

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    import jsonschema
except ImportError:
    jsonschema = None

DELEGATION_SCHEMA_PATH = os.path.join(ROOT_DIR, "contracts", "delegation_contract.schema.json")
WORKER_RETURN_SCHEMA_PATH = os.path.join(ROOT_DIR, "contracts", "worker_return_payload.schema.json")

MANDATORY_TASK_FIELDS = [
    "task_id",
    "parent_agent",
    "worker_agent",
    "objective",
    "inputs",
    "required_artifacts",
    "acceptance_criteria",
    "constraints",
    "verification_method",
    "deadline"
]

MANDATORY_RETURN_FIELDS = [
    "status",
    "artifacts",
    "evidence",
    "validation",
    "warnings",
    "limitations"
]

VALID_STATUSES = ["SUCCESS", "FAILED", "BLOCKED"]
VALID_VERDICTS = ["PASS", "FAIL", "NEEDS_REVIEW", "BLOCKED"]

INFORMAL_TASK_PATTERNS = [
    r"^analyze\s+this\b",
    r"^do\s+this\b",
    r"^calculate\s+this\b",
    r"^run\s+(?:the\s+)?analysis\b",
    r"^run\s+the\s+stats\b",
    r"^please\s+analyze\b",
    r"^please\s+do\s+this\b",
    r"^handle\s+this\b",
    r"^look\s+at\s+this\b"
]

INFORMAL_RETURN_PATTERNS = [
    r"^done$",
    r"^completed$",
    r"^finished$",
    r"^all\s+done$",
    r"^ok$",
    r"^all\s+set$",
    r"^task\s+completed$"
]

INFORMAL_CLOSURE_PATTERNS = [
    r"^great$",
    r"^looks\s+good$",
    r"^perfect$",
    r"^awesome$",
    r"^good\s+job$",
    r"^approved$",
    r"^accepted$",
    r"^thanks$",
    r"^thank\s+you$"
]


class DelegationContractError(Exception):
    """Base error for delegation contract violations."""
    pass


class InvalidTaskContractError(DelegationContractError):
    """Raised when a task contract is missing required fields or has invalid structure."""
    pass


class InvalidWorkerReturnContractError(DelegationContractError):
    """Raised when a worker return payload violates the 6-field structured contract."""
    pass


class InformalDelegationError(DelegationContractError):
    """Raised when an agent attempts informal delegation (e.g. 'Analyze this')."""
    pass


class InformalWorkerReturnError(DelegationContractError):
    """Raised when a worker attempts an informal return (e.g. 'Done.')."""
    pass


class InformalClosureError(DelegationContractError):
    """Raised when an orchestrator attempts an informal closure (e.g. 'Great.') without validator verification."""
    pass


class ContractVerificationError(DelegationContractError):
    """Raised when contract verification fails."""
    pass


def create_delegation_contract(
    task_id: str,
    parent_agent: str,
    worker_agent: str,
    objective: str,
    inputs: List[Union[str, Dict[str, Any]]],
    required_artifacts: List[Union[str, Dict[str, Any]]],
    acceptance_criteria: List[str],
    constraints: List[str],
    verification_method: str,
    deadline: str,
    contract_version: str = "1.0.0",
    extra_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Constructs a formal 10-field DelegationContract dictionary.
    """
    contract: Dict[str, Any] = {
        "contract_version": contract_version,
        "task_id": str(task_id).strip(),
        "parent_agent": str(parent_agent).strip(),
        "worker_agent": str(worker_agent).strip(),
        "objective": str(objective).strip(),
        "inputs": list(inputs),
        "required_artifacts": list(required_artifacts),
        "acceptance_criteria": list(acceptance_criteria),
        "constraints": list(constraints),
        "verification_method": str(verification_method).strip(),
        "deadline": str(deadline).strip()
    }

    if extra_metadata:
        contract["metadata"] = extra_metadata

    validate_delegation_contract(contract, fail_closed=True)
    return contract


def validate_delegation_contract(contract: Any, fail_closed: bool = False) -> Dict[str, Any]:
    """
    Validates a delegation contract against the 10 mandatory fields and schema.
    Returns {"valid": bool, "errors": List[str], "contract": Dict[str, Any]}.
    """
    errors: List[str] = []

    if isinstance(contract, str):
        informal, reason = detect_informal_delegation(contract)
        if informal:
            errors.append(reason)
            if fail_closed:
                raise InformalDelegationError(reason)
            return {"valid": False, "errors": errors, "contract": {"raw": contract}}
        try:
            contract = json.loads(contract)
        except Exception:
            err = "Delegation contract must be a JSON object or dictionary, not plain text."
            if fail_closed:
                raise InvalidTaskContractError(err)
            return {"valid": False, "errors": [err], "contract": {}}

    if not isinstance(contract, dict):
        err = f"Delegation contract must be a dictionary, got {type(contract).__name__}."
        if fail_closed:
            raise InvalidTaskContractError(err)
        return {"valid": False, "errors": [err], "contract": {}}

    # Check 10 mandatory fields
    for field in MANDATORY_TASK_FIELDS:
        val = contract.get(field)
        if val is None:
            errors.append(f"Missing mandatory contract field: '{field}'.")
        elif isinstance(val, (str, list, dict)) and len(val) == 0:
            errors.append(f"Mandatory contract field '{field}' cannot be empty.")

    # Validate inputs
    inputs = contract.get("inputs")
    if inputs is not None:
        if not isinstance(inputs, list):
            errors.append(f"Field 'inputs' must be a list, got {type(inputs).__name__}.")
        elif len(inputs) == 0:
            errors.append("Field 'inputs' must contain at least one input artifact or path.")

    # Validate required_artifacts
    artifacts = contract.get("required_artifacts")
    if artifacts is not None:
        if not isinstance(artifacts, list):
            errors.append(f"Field 'required_artifacts' must be a list, got {type(artifacts).__name__}.")
        elif len(artifacts) == 0:
            errors.append("Field 'required_artifacts' must contain at least one expected artifact.")

    # Validate acceptance_criteria
    criteria = contract.get("acceptance_criteria")
    if criteria is not None:
        if not isinstance(criteria, list):
            errors.append(f"Field 'acceptance_criteria' must be a list, got {type(criteria).__name__}.")
        elif len(criteria) == 0:
            errors.append("Field 'acceptance_criteria' must contain at least one verification criterion.")

    # Validate constraints
    constraints = contract.get("constraints")
    if constraints is not None:
        if not isinstance(constraints, list):
            errors.append(f"Field 'constraints' must be a list, got {type(constraints).__name__}.")
        elif len(constraints) == 0:
            errors.append("Field 'constraints' must contain at least one operational boundary.")

    # Validate objective
    obj = contract.get("objective")
    if obj and isinstance(obj, str) and len(obj.strip()) < 10:
        errors.append("Field 'objective' is too brief (must be >= 10 characters describing the task).")

    # JSON Schema validation
    if jsonschema and os.path.isfile(DELEGATION_SCHEMA_PATH) and not errors:
        try:
            with open(DELEGATION_SCHEMA_PATH, "r", encoding="utf-8") as sf:
                schema_data = json.load(sf)
            schema_payload = dict(contract)
            if "contract_version" not in schema_payload:
                schema_payload["contract_version"] = "1.0.0"
            jsonschema.validate(instance=schema_payload, schema=schema_data)
        except jsonschema.ValidationError as ve:
            errors.append(f"Schema validation failed against delegation_contract.schema.json: {ve.message}")
        except Exception:
            pass

    is_valid = (len(errors) == 0)
    if not is_valid and fail_closed:
        raise InvalidTaskContractError("; ".join(errors))

    return {
        "valid": is_valid,
        "errors": errors,
        "contract": contract
    }


def create_worker_return(
    status: str,
    artifacts: List[Union[str, Dict[str, Any]]],
    evidence: Dict[str, Any],
    validation: Dict[str, Any],
    warnings: Optional[List[str]] = None,
    limitations: Optional[List[str]] = None,
    task_id: Optional[str] = None,
    worker_agent: Optional[str] = None
) -> Dict[str, Any]:
    """
    Constructs a formal 6-field WorkerReturn dictionary.
    """
    ret: Dict[str, Any] = {
        "status": str(status).strip().upper(),
        "artifacts": list(artifacts),
        "evidence": dict(evidence),
        "validation": dict(validation),
        "warnings": list(warnings if warnings is not None else []),
        "limitations": list(limitations if limitations is not None else [])
    }
    if task_id:
        ret["task_id"] = str(task_id).strip()
    if worker_agent:
        ret["worker_agent"] = str(worker_agent).strip()

    validate_worker_return(ret, fail_closed=True)
    return ret


def validate_worker_return(payload: Any, fail_closed: bool = False) -> Dict[str, Any]:
    """
    Validates a worker return against the 6 mandatory fields (status, artifacts, evidence, validation, warnings, limitations).
    Returns {"valid": bool, "errors": List[str], "payload": Dict[str, Any]}.
    """
    errors: List[str] = []

    # 1. Reject trivial string returns ('done', 'completed', etc.)
    if isinstance(payload, str):
        informal, reason = detect_informal_worker_return(payload)
        err_msg = reason if informal else f"Worker return must be a structured dictionary, got plain string: '{payload}'."
        if fail_closed:
            raise InformalWorkerReturnError(err_msg)
        return {"valid": False, "errors": [err_msg], "payload": {"raw": payload}}

    if not isinstance(payload, dict):
        err = f"Worker return payload must be a dictionary, got {type(payload).__name__}."
        if fail_closed:
            raise InvalidWorkerReturnContractError(err)
        return {"valid": False, "errors": [err], "payload": {}}

    # 2. Status
    status = payload.get("status")
    if not status:
        errors.append("Missing required field 'status'. Allowed values: SUCCESS, FAILED, BLOCKED.")
    else:
        st_norm = str(status).strip().upper()
        if st_norm not in VALID_STATUSES:
            errors.append(f"Invalid status '{status}'. Allowed values: SUCCESS, FAILED, BLOCKED.")

    # 3. Artifacts (or artifact)
    artifacts = payload.get("artifacts")
    if artifacts is None:
        artifacts = payload.get("artifact")
    if artifacts is None:
        artifacts = payload.get("produced_artifacts")
    if artifacts is None:
        errors.append("Missing required field 'artifacts'. Must be a non-empty list of produced deliverable paths.")
    elif isinstance(artifacts, (list, tuple)):
        if len(artifacts) == 0:
            errors.append("Field 'artifacts' cannot be an empty list. Must specify produced deliverable files on disk.")
    elif isinstance(artifacts, dict):
        if len(artifacts) == 0:
            errors.append("Field 'artifacts' cannot be an empty dict.")
    elif isinstance(artifacts, str):
        if not artifacts.strip():
            errors.append("Field 'artifacts' cannot be empty string.")
    else:
        errors.append(f"Field 'artifacts' must be a list, dict, or string path, got {type(artifacts).__name__}.")

    # 4. Evidence
    evidence = payload.get("evidence")
    if evidence is None:
        errors.append("Missing required field 'evidence'. Must be a non-empty dictionary containing exact computational test statistics.")
    elif not isinstance(evidence, dict):
        errors.append(f"Field 'evidence' must be a dictionary, got {type(evidence).__name__}.")
    elif len(evidence) == 0:
        errors.append("Field 'evidence' cannot be empty. Must report computational parameters (e.g. M, SD, t, F, df, p, effect size).")

    # 5. Validation
    validation = payload.get("validation")
    if validation is None:
        verdict = payload.get("validation_verdict")
        if verdict:
            validation = {"verdict": verdict}
        else:
            errors.append("Missing required field 'validation'. Must specify validation report details and verdict.")

    if validation is not None:
        if isinstance(validation, dict):
            verdict = validation.get("verdict", validation.get("overall_verdict"))
            if not verdict:
                errors.append("Field 'validation' must contain 'verdict' or 'overall_verdict' (e.g. 'PASS', 'FAIL').")
            elif str(verdict).upper() not in VALID_VERDICTS:
                errors.append(f"Invalid validation verdict '{verdict}'. Allowed: PASS, FAIL, NEEDS_REVIEW, BLOCKED.")
        elif isinstance(validation, str):
            if validation.upper() not in VALID_VERDICTS:
                errors.append(f"Invalid validation string '{validation}'. Expected PASS, FAIL, NEEDS_REVIEW, BLOCKED.")
        else:
            errors.append(f"Field 'validation' must be a dictionary or verdict string, got {type(validation).__name__}.")

    # 6. Warnings
    warnings = payload.get("warnings")
    if warnings is None:
        errors.append("Missing required field 'warnings'. Must be a list of strings (empty list [] if none).")
    elif not isinstance(warnings, (list, tuple)):
        errors.append(f"Field 'warnings' must be a list of strings, got {type(warnings).__name__}.")

    # 7. Limitations
    limitations = payload.get("limitations")
    if limitations is None:
        errors.append("Missing required field 'limitations'. Must be a list of strings (empty list [] if none).")
    elif not isinstance(limitations, (list, tuple)):
        errors.append(f"Field 'limitations' must be a list of strings, got {type(limitations).__name__}.")

    is_valid = (len(errors) == 0)
    if not is_valid and fail_closed:
        raise InvalidWorkerReturnContractError("; ".join(errors))

    return {
        "valid": is_valid,
        "errors": errors,
        "payload": payload
    }


def format_delegation_prompt(contract: Union[Dict[str, Any], Any]) -> str:
    """
    Renders a formal 10-field DelegationContract into a markdown envelope for invoke_subagent.
    """
    if hasattr(contract, "to_dict"):
        c = contract.to_dict()
    else:
        c = dict(contract)

    # Normalize inputs and artifacts
    inputs_lines = []
    for inp in c.get("inputs", []):
        if isinstance(inp, dict):
            p = inp.get("path", "")
            desc = f" ({inp.get('description')})" if inp.get("description") else ""
            inputs_lines.append(f"  - `{p}`{desc}")
        else:
            inputs_lines.append(f"  - `{inp}`")

    artifacts_lines = []
    for art in c.get("required_artifacts", []):
        if isinstance(art, dict):
            p = art.get("path", "")
            fmt = f" [{art.get('format')}]" if art.get("format") else ""
            artifacts_lines.append(f"  - `{p}`{fmt}")
        else:
            artifacts_lines.append(f"  - `{art}`")

    criteria_lines = [f"  {idx+1}. {crit}" for idx, crit in enumerate(c.get("acceptance_criteria", []))]
    constraints_lines = [f"  - {con}" for con in c.get("constraints", [])]

    prompt = (
        f"### Contractual Delegation Envelope (Phase 22 Contract)\n"
        f"- **Contract Version**: {c.get('contract_version', '1.0.0')}\n"
        f"- **Task ID**: `{c.get('task_id')}`\n"
        f"- **Parent Agent**: `{c.get('parent_agent')}`\n"
        f"- **Worker Agent**: `{c.get('worker_agent')}`\n"
        f"- **Verification Method**: `{c.get('verification_method')}`\n"
        f"- **Deadline**: `{c.get('deadline')}`\n\n"
        f"#### Objective:\n"
        f"{c.get('objective')}\n\n"
        f"#### Required Inputs:\n"
        f"{chr(10).join(inputs_lines) if inputs_lines else '  - None'}\n\n"
        f"#### Required Artifacts (On Disk):\n"
        f"{chr(10).join(artifacts_lines) if artifacts_lines else '  - None'}\n\n"
        f"#### Acceptance Criteria:\n"
        f"{chr(10).join(criteria_lines) if criteria_lines else '  1. Complete analysis cleanly'}\n\n"
        f"#### Constraints & Operational Invariants:\n"
        f"{chr(10).join(constraints_lines) if constraints_lines else '  - Standard invariants'}\n\n"
        f"#### Mandatory Worker Return Structure (Phase 22):\n"
        f"On task completion, return a structured JSON or object containing the 6 mandatory fields:\n"
        f"1. `status`: SUCCESS | FAILED | BLOCKED\n"
        f"2. `artifacts`: list of produced files on disk\n"
        f"3. `evidence`: exact computational parameters, test statistics, and df\n"
        f"4. `validation`: validation summary and verdict (PASS/FAIL)\n"
        f"5. `warnings`: list of operational anomalies or warnings ([] if none)\n"
        f"6. `limitations`: list of methodological/statistical constraints ([] if none)\n"
        f"Strictly forbidden: trivial returns like 'done', 'completed', or unstructured text."
    )
    return prompt


def detect_informal_delegation(text: str) -> Tuple[bool, str]:
    """
    Detects if a delegation prompt is an informal anti-pattern like 'Analyze this.'
    Returns (is_informal, reason).
    """
    if not text or not isinstance(text, str):
        return True, "Delegation task is empty or not a string."

    stripped = text.strip()
    lowered = stripped.lower()

    for pat in INFORMAL_TASK_PATTERNS:
        if re.search(pat, lowered):
            return True, (
                f"INFORMAL DELEGATION BLOCKED: Task starts with informal phrase matching '{pat}'. "
                f"Under Phase 22, the Academic-Orchestrator cannot simply say 'Analyze this.' "
                f"Every delegated task must define a formal DelegationContract specifying: "
                f"task_id, parent_agent, worker_agent, objective, inputs, required_artifacts, "
                f"acceptance_criteria, constraints, verification_method, and deadline."
            )

    return False, ""


def detect_informal_worker_return(payload: Any) -> Tuple[bool, str]:
    """
    Detects if a worker return is an informal anti-pattern like 'Done.'
    Returns (is_informal, reason).
    """
    if isinstance(payload, str):
        cleaned = re.sub(r"[!.,\s]+$", "", payload.strip().lower())
        for pat in INFORMAL_RETURN_PATTERNS:
            if re.search(pat, cleaned):
                return True, (
                    f"INFORMAL WORKER RETURN BLOCKED: Worker returned trivial string '{payload}'. "
                    f"Under Phase 22, workers must return a structured payload with 6 fields: "
                    f"'status', 'artifacts', 'evidence', 'validation', 'warnings', 'limitations'."
                )

    return False, ""


def detect_informal_closure(message: str) -> Tuple[bool, str]:
    """
    Detects if an orchestrator message is an informal closure like 'Great.'
    Returns (is_informal, reason).
    """
    if not message or not isinstance(message, str):
        return False, ""

    cleaned = re.sub(r"[!.,\s]+$", "", message.strip().lower())
    for pat in INFORMAL_CLOSURE_PATTERNS:
        if re.search(pat, cleaned):
            return True, (
                f"INFORMAL ORCHESTRATOR CLOSURE BLOCKED: Orchestrator attempted informal closure '{message}'. "
                f"Under Phase 22, the Orchestrator cannot accept worker output with 'Great.' "
                f"Workflow progression requires formal validator verification and structured state transition."
            )

    return False, ""


def execute_contract_verification(
    contract: Dict[str, Any],
    worker_return: Dict[str, Any],
    validator_report: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Executes formal contract verification:
    Academic-Orchestrator -> formal task -> worker -> formal evidence -> validator -> Academic-Orchestrator
    """
    # 1. Validate contract
    contract_val = validate_delegation_contract(contract, fail_closed=False)
    if not contract_val["valid"]:
        return {
            "verified": False,
            "errors": [f"Contract validation failure: {'; '.join(contract_val['errors'])}"],
            "verdict": "REJECTED"
        }

    # 2. Validate worker return
    return_val = validate_worker_return(worker_return, fail_closed=False)
    if not return_val["valid"]:
        return {
            "verified": False,
            "errors": [f"Worker return validation failure: {'; '.join(return_val['errors'])}"],
            "verdict": "REJECTED"
        }

    errors: List[str] = []

    # 3. Check status
    st = worker_return.get("status", "").upper()
    if st != "SUCCESS":
        errors.append(f"Worker status is not SUCCESS (got '{st}').")

    # 4. Check required artifacts produced
    req_artifacts = contract.get("required_artifacts", [])
    prod_artifacts = worker_return.get("artifacts", [])
    prod_paths = set()
    for art in prod_artifacts:
        if isinstance(art, dict):
            prod_paths.add(art.get("path", ""))
        else:
            prod_paths.add(str(art))

    for req in req_artifacts:
        req_p = req.get("path", "") if isinstance(req, dict) else str(req)
        req_base = os.path.basename(req_p)
        matched = any(req_p in p or req_base == os.path.basename(p) for p in prod_paths)
        if not matched:
            errors.append(f"Missing required artifact '{req_p}' in worker return.")

    # 5. Check validator report
    v_report = validator_report or worker_return.get("validation", {})
    verdict = v_report.get("verdict") or v_report.get("overall_verdict")
    if not verdict or str(verdict).upper() != "PASS":
        errors.append(f"Validator report verdict is not PASS (got '{verdict}').")

    is_verified = (len(errors) == 0)
    return {
        "verified": is_verified,
        "task_id": contract.get("task_id"),
        "parent_agent": contract.get("parent_agent"),
        "worker_agent": contract.get("worker_agent"),
        "verification_method": contract.get("verification_method"),
        "verdict": "APPROVED" if is_verified else "REJECTED",
        "errors": errors,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Formal Delegation Contract Engine (Phase 22)")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    p_vc = subparsers.add_parser("validate-contract", help="Validate a delegation contract JSON file")
    p_vc.add_argument("contract_file", help="Path to contract JSON file")

    p_vr = subparsers.add_parser("validate-return", help="Validate a worker return JSON file")
    p_vr.add_argument("return_file", help="Path to worker return JSON file")

    p_fp = subparsers.add_parser("format-prompt", help="Format a contract JSON file into an agent prompt")
    p_fp.add_argument("contract_file", help="Path to contract JSON file")

    p_ver = subparsers.add_parser("verify", help="Verify contract completion against worker return and validator")
    p_ver.add_argument("--contract", required=True, help="Path to contract JSON file")
    p_ver.add_argument("--return", required=True, dest="return_file", help="Path to worker return JSON file")
    p_ver.add_argument("--validator", required=False, help="Path to validator report JSON file")

    args = parser.parse_args()

    if args.subcommand == "validate-contract":
        with open(args.contract_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        res = validate_delegation_contract(data)
        print(json.dumps(res, indent=2))
        sys.exit(0 if res["valid"] else 1)

    elif args.subcommand == "validate-return":
        with open(args.return_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        res = validate_worker_return(data)
        print(json.dumps(res, indent=2))
        sys.exit(0 if res["valid"] else 1)

    elif args.subcommand == "format-prompt":
        with open(args.contract_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(format_delegation_prompt(data))

    elif args.subcommand == "verify":
        with open(args.contract, "r", encoding="utf-8") as f:
            contract_data = json.load(f)
        with open(args.return_file, "r", encoding="utf-8") as f:
            return_data = json.load(f)
        validator_data = None
        if args.validator and os.path.exists(args.validator):
            with open(args.validator, "r", encoding="utf-8") as f:
                validator_data = json.load(f)
        res = execute_contract_verification(contract_data, return_data, validator_data)
        print(json.dumps(res, indent=2))
        sys.exit(0 if res["verified"] else 1)


if __name__ == "__main__":
    main()
