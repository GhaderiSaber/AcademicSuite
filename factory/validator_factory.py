#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
factory/validator_factory.py — Autonomous Validator Scaffolding Factory

Generates deterministic, institutional quality-control validators in validators/
with standard CLI flags, error/warning taxonomy, and standard exit codes (0 = PASS, 1 = FAIL).
"""

import os
import sys
from typing import Dict, Any, List, Optional

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VALIDATORS_DIR = os.path.join(ROOT_DIR, "validators")


VALIDATOR_TEMPLATE = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validators/{name}/validator.py — {description}
"""

import os
import sys
import json
import argparse

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)


def validate_{name}(input_path: str, **kwargs) -> dict:
    if not os.path.exists(input_path):
        return {{
            "validator": "{name}",
            "verdict": "FAIL",
            "errors": [f"Input file not found: {{input_path}}"],
            "warnings": []
        }}

    errors = []
    warnings = []

    # Dynamic rules injection
{rule_checks}

    verdict = "FAIL" if errors else ("NEEDS_REVIEW" if warnings else "PASS")
    return {{
        "validator": "{name}",
        "verdict": verdict,
        "errors": errors,
        "warnings": warnings,
        "file_audited": os.path.basename(input_path)
    }}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="{description}")
    parser.add_argument('--input', required=True, help="Path to input artifact (.json, .xlsx, or .md)")
    args = parser.parse_args()

    result = validate_{name}(args.input)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["verdict"] == "PASS" else 1)
'''


def create_validator(
    name: str,
    description: str,
    custom_logic: Optional[str] = None,
    target_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Creates and writes a verified deterministic validator script in validators/<name>/validator.py.
    """
    base_val_dir = target_dir or VALIDATORS_DIR
    val_dir = os.path.join(base_val_dir, name)
    os.makedirs(val_dir, exist_ok=True)
    val_file = os.path.join(val_dir, "validator.py")

    default_rules = """    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            errors.append("Root payload must be a JSON object.")
    except Exception as e:
        errors.append(f"JSON parsing error: {str(e)}")"""

    rule_checks = custom_logic or default_rules

    code = VALIDATOR_TEMPLATE.format(
        name=name,
        description=description,
        rule_checks=rule_checks
    )

    with open(val_file, "w", encoding="utf-8") as f:
        f.write(code)

    return {
        "status": "SUCCESS",
        "validator_name": name,
        "file_path": val_file,
        "size_bytes": len(code.encode("utf-8"))
    }
