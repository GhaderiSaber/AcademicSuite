#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validators/worker_return_validator.py — Worker Return Payload Validator

Phase 21: Enforces that worker subagents return a structured payload:
  1. artifact (files produced on disk)
  2. evidence (factual test statistics, parameters, degrees of freedom, effect sizes)
  3. status (machine-readable execution status: SUCCESS, FAILED, BLOCKED)
  4. validation (independent validation report summary or verdict)

Strictly forbids and rejects trivial string returns like 'done', 'completed', or unstructured text.
"""

import os
import sys
import json
from typing import Dict, Any, List, Tuple, Union, Optional

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    import jsonschema
except ImportError:
    jsonschema = None


SCHEMA_PATH = os.path.join(ROOT_DIR, 'contracts', 'worker_return_payload.schema.json')


class WorkerReturnValidationError(Exception):
    """Raised when a worker subagent return payload violates the structured return contract."""
    pass


def validate_worker_return_payload(
    payload: Any,
    fail_closed: bool = False
) -> Dict[str, Any]:
    """
    Validates a worker subagent return payload against the Phase 21 return contract.
    Returns a dictionary with validation results:
      - valid: bool
      - errors: List[str]
      - payload: Dict[str, Any]
    """
    errors: List[str] = []

    # 1. Reject trivial string returns ('done', 'completed', etc.)
    if isinstance(payload, str):
        cleaned = payload.strip().lower()
        err_msg = (
            f"TRIVIAL WORKER RETURN DETECTED: Worker returned plain string '{payload}'. "
            f"Under Phase 21, workers must return a structured payload containing: "
            f"'artifact', 'evidence', 'status', 'validation' (not simply 'done')."
        )
        if fail_closed:
            raise WorkerReturnValidationError(err_msg)
        return {"valid": False, "errors": [err_msg], "payload": {"raw": payload}}

    if not isinstance(payload, dict):
        err_msg = f"Worker return payload must be a dictionary, got {type(payload).__name__}."
        if fail_closed:
            raise WorkerReturnValidationError(err_msg)
        return {"valid": False, "errors": [err_msg], "payload": {}}

    # 2. Check for required field: status
    status = payload.get('status')
    if not status:
        errors.append("Missing required field 'status'. Allowed values: SUCCESS, FAILED, BLOCKED.")
    else:
        st_norm = str(status).strip().upper()
        if st_norm not in ["SUCCESS", "FAILED", "FAILURE", "BLOCKED"]:
            errors.append(f"Invalid status '{status}'. Allowed values: SUCCESS, FAILED, BLOCKED.")

    # 3. Check for required field: artifact or artifacts (Phase 21 & Phase 22)
    artifact = payload.get('artifact')
    if artifact is None:
        artifact = payload.get('artifacts')
    if artifact is None:
        artifact = payload.get('produced_artifacts')
    if artifact is None:
        errors.append("Missing required field 'artifacts' (or 'artifact'). Must be a non-empty list or object of produced files on disk.")

    if artifact is not None:
        if isinstance(artifact, (list, tuple)):
            if len(artifact) == 0:
                errors.append("Field 'artifacts' (or 'artifact') cannot be an empty list. Must contain at least one produced deliverable path.")
        elif isinstance(artifact, dict):
            if len(artifact) == 0:
                errors.append("Field 'artifacts' (or 'artifact') cannot be an empty object. Must specify produced deliverable files.")
        elif isinstance(artifact, str):
            if not artifact.strip():
                errors.append("Field 'artifacts' (or 'artifact') cannot be an empty string.")
        else:
            errors.append(f"Field 'artifacts' (or 'artifact') must be a list, dict, or string path, got {type(artifact).__name__}.")

    # 4. Check for required field: evidence
    evidence = payload.get('evidence')
    if evidence is None:
        errors.append("Missing required field 'evidence'. Must be a non-empty dictionary containing exact computational test statistics and parameters.")
    elif not isinstance(evidence, dict):
        errors.append(f"Field 'evidence' must be a dictionary, got {type(evidence).__name__}.")
    elif len(evidence) == 0:
        errors.append("Field 'evidence' cannot be empty. Must report computational parameters (e.g. M, SD, t, F, df, p, effect size).")

    # 5. Check for required field: validation
    validation = payload.get('validation')
    if validation is None:
        # Fallback check for validation_verdict
        verdict = payload.get('validation_verdict')
        if verdict:
            validation = {"verdict": verdict}
        else:
            errors.append("Missing required field 'validation'. Must specify validation report details and verdict.")

    if validation is not None:
        if isinstance(validation, dict):
            verdict = validation.get('verdict', validation.get('overall_verdict'))
            if not verdict:
                errors.append("Field 'validation' must contain a 'verdict' or 'overall_verdict' (e.g. 'PASS', 'FAIL').")
            elif str(verdict).upper() not in ["PASS", "FAIL", "NEEDS_REVIEW", "BLOCKED"]:
                errors.append(f"Invalid validation verdict '{verdict}'. Allowed: PASS, FAIL, NEEDS_REVIEW, BLOCKED.")
        elif isinstance(validation, str):
            if validation.upper() not in ["PASS", "FAIL", "NEEDS_REVIEW", "BLOCKED"]:
                errors.append(f"Invalid validation string '{validation}'. Expected PASS, FAIL, NEEDS_REVIEW, BLOCKED.")
        else:
            errors.append(f"Field 'validation' must be a dictionary or verdict string, got {type(validation).__name__}.")

    # 5.5 Check optional/Phase 22 fields: warnings and limitations
    if 'warnings' in payload and not isinstance(payload['warnings'], (list, tuple)):
        errors.append(f"Field 'warnings' must be a list of strings, got {type(payload['warnings']).__name__}.")
    if 'limitations' in payload and not isinstance(payload['limitations'], (list, tuple)):
        errors.append(f"Field 'limitations' must be a list of strings, got {type(payload['limitations']).__name__}.")

    # 6. JSON Schema validation
    if jsonschema and os.path.isfile(SCHEMA_PATH) and not errors:
        try:
            with open(SCHEMA_PATH, 'r', encoding='utf-8') as sf:
                schema_data = json.load(sf)
            # Normalize for schema validation if needed
            schema_payload = dict(payload)
            if 'artifact' not in schema_payload and 'produced_artifacts' in schema_payload:
                schema_payload['artifact'] = schema_payload['produced_artifacts']
            if isinstance(schema_payload.get('validation'), str):
                schema_payload['validation'] = {"verdict": schema_payload['validation']}
            if str(schema_payload.get('status')).upper() == 'FAILURE':
                schema_payload['status'] = 'FAILED'
            jsonschema.validate(instance=schema_payload, schema=schema_data)
        except jsonschema.ValidationError as ve:
            errors.append(f"Schema validation failed against worker_return_payload.schema.json: {ve.message}")
        except Exception as se:
            pass

    is_valid = (len(errors) == 0)
    if not is_valid and fail_closed:
        raise WorkerReturnValidationError("; ".join(errors))

    return {
        "valid": is_valid,
        "errors": errors,
        "payload": payload
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: worker_return_validator.py <payload.json | 'done'>")
        sys.exit(1)

    raw_arg = sys.argv[1]
    if os.path.isfile(raw_arg):
        with open(raw_arg, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        try:
            data = json.loads(raw_arg)
        except Exception:
            data = raw_arg

    res = validate_worker_return_payload(data)
    print(json.dumps(res, indent=2))
    sys.exit(0 if res["valid"] else 1)


if __name__ == '__main__':
    main()
