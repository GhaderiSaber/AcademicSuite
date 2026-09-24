#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/contracts/delegation_envelope_parser.py

Deterministic parser and validator for Contractual Delegation Envelopes (CDE).
Used by academic-orchestrator and dedicated hooks to ensure inter-agent task delegation
is rigorous, structured, and auditable rather than informal and unconstrained.

Enforces:
1. Presence of a structured Contractual Delegation Envelope in invoke_subagent prompts.
2. Required fields: task_id, worker_agent, inputs/input_artifacts, required_artifacts/expected_triad, objective/target_script.
3. Concrete input and output file specifications (Directive 3 Triad Artifact Invariant).
"""

import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple, Union


REQUIRED_ENVELOPE_KEYS = {
    "task_id",
    "worker_agent",
    "inputs",
    "required_artifacts"
}

ALTERNATIVE_KEY_MAP = {
    "target_worker": "worker_agent",
    "worker": "worker_agent",
    "input_artifacts": "inputs",
    "expected_triad": "required_artifacts",
    "expected_artifacts": "required_artifacts",
    "deliverables": "required_artifacts",
    "target_script": "objective",
    "instructions": "objective",
    "description": "objective"
}


def extract_envelope_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Extracts a JSON object from prompt text.
    Looks for fenced code blocks (```json ... ```) or standalone JSON objects.
    """
    if not text or not isinstance(text, str):
        return None

    # 1. Search for fenced json block
    json_block_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', text, re.IGNORECASE)
    if json_block_match:
        try:
            return json.loads(json_block_match.group(1))
        except Exception:
            pass

    # 2. Search for bare JSON object with task_id or worker_agent
    start_idx = text.find("{")
    while start_idx != -1:
        depth = 0
        for i in range(start_idx, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[start_idx : i + 1]
                    try:
                        parsed = json.loads(candidate)
                        if isinstance(parsed, dict) and any(k in parsed for k in ("task_id", "worker_agent", "target_worker", "objective")):
                            return parsed
                    except Exception:
                        pass
                    break
        start_idx = text.find("{", start_idx + 1)

    # 3. Try parsing entire text directly if it is pure JSON
    trimmed = text.strip()
    if trimmed.startswith("{") and trimmed.endswith("}"):
        try:
            parsed = json.loads(trimmed)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

    return None


def normalize_envelope(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes alternative envelope key names into canonical fields."""
    norm = dict(data)
    for alt_k, canon_k in ALTERNATIVE_KEY_MAP.items():
        if alt_k in norm and canon_k not in norm:
            norm[canon_k] = norm[alt_k]
    return norm


def validate_delegation_prompt(prompt: str, expected_worker: Optional[str] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Validates that a delegation prompt contains a valid Contractual Delegation Envelope.
    Returns:
        (is_valid, reason, normalized_envelope_dict)
    """
    if not prompt or not isinstance(prompt, str):
        return False, "Delegation prompt is empty or not a string.", None

    envelope = extract_envelope_json(prompt)
    if not envelope:
        return False, (
            "CONSTITUTIONAL VIOLATION (Directive 19 / Directive 12): "
            "Subagent delegation prompt is missing a structured Contractual Delegation Envelope (CDE). "
            "Informal or vague natural-language delegation is strictly prohibited. "
            "You MUST embed a fenced JSON block (```json { ... } ```) containing: "
            "'task_id', 'worker_agent', 'objective' (or 'target_script'), 'inputs', and 'required_artifacts' (or 'expected_triad')."
        ), None

    norm = normalize_envelope(envelope)

    missing_fields = []
    for k in ("task_id", "worker_agent", "inputs", "required_artifacts"):
        if k not in norm or not norm[k]:
            missing_fields.append(k)

    if missing_fields:
        return False, (
            f"CONSTITUTIONAL VIOLATION (Directive 19 - Delegation Contract Incomplete): "
            f"Contractual Delegation Envelope is missing required fields: {missing_fields}. "
            f"Every delegated task must define explicit inputs and expected deliverables."
        ), norm

    # Worker mismatch check
    if expected_worker:
        delegated_worker = str(norm.get("worker_agent", "")).strip().lower()
        exp_worker_lower = str(expected_worker).strip().lower()
        if delegated_worker and exp_worker_lower and delegated_worker != exp_worker_lower:
            return False, (
                f"DELEGATION MISMATCH: Contract specifies worker_agent='{norm.get('worker_agent')}', "
                f"but target subagent is '{expected_worker}'."
            ), norm

    # Check inputs is non-empty list
    inputs = norm.get("inputs")
    if not isinstance(inputs, list) or len(inputs) == 0:
        return False, (
            "CONSTITUTIONAL VIOLATION: 'inputs' must be a non-empty list of file paths or input specifications."
        ), norm

    # Check required_artifacts is non-empty list
    req_art = norm.get("required_artifacts")
    if not isinstance(req_art, list) or len(req_art) == 0:
        return False, (
            "CONSTITUTIONAL VIOLATION: 'required_artifacts' must be a non-empty list of expected deliverables."
        ), norm

    return True, "Delegation envelope is valid.", norm


def build_delegation_envelope(
    task_id: str,
    worker_agent: str,
    objective: str,
    inputs: List[Union[str, Dict[str, Any]]],
    required_artifacts: List[Union[str, Dict[str, Any]]],
    stage_name: Optional[str] = None,
    target_script: Optional[str] = None,
    acceptance_criteria: Optional[List[str]] = None,
    constraints: Optional[List[str]] = None,
    preamble: Optional[str] = None
) -> str:
    """Builds a formatted delegation prompt string with embedded CDE."""
    envelope = {
        "contract_version": "1.0.0",
        "task_id": task_id,
        "worker_agent": worker_agent,
        "objective": objective,
        "inputs": inputs,
        "required_artifacts": required_artifacts
    }
    if stage_name:
        envelope["stage"] = stage_name
    if target_script:
        envelope["target_script"] = target_script
    if acceptance_criteria:
        envelope["acceptance_criteria"] = acceptance_criteria
    if constraints:
        envelope["constraints"] = constraints

    header = preamble or f"Execute {stage_name or task_id} according to the following formal contract:"
    json_str = json.dumps(envelope, indent=2, ensure_ascii=False)
    return f"{header}\n\n### 📋 Contractual Delegation Envelope\n```json\n{json_str}\n```\n"


if __name__ == "__main__":
    test_prompt = """
    Execute Stage 4.6:
    ```json
    {
      "task_id": "TSK-CH4-H1",
      "worker_agent": "statistics-agent",
      "objective": "Execute linear regression",
      "inputs": ["02_analysis_code/cleaned_data.xlsx"],
      "required_artifacts": [
        "03_deliverables/06_hypothesis_1.docx",
        "03_deliverables/06_hypothesis_1.md",
        "03_deliverables/06_hypothesis_1.json"
      ]
    }
    ```
    """
    valid, reason, env = validate_delegation_prompt(test_prompt, expected_worker="statistics-agent")
    print(f"Valid: {valid}, Reason: {reason}")
