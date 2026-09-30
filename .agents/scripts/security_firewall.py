#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/scripts/security_firewall.py — Antigravity 2.18.1 Mechanical Security Firewall

Deterministic, ultra-fast (<2ms) PreToolUse runtime safety guard:
1. Prevents catastrophic system destruction (rm -rf /, .git, .agents, fork bombs).
2. Enforces strict raw-data immutability (blocks deletion/modification of 01_raw_inputs/* and raw/*).
3. Enforces ASCII English-only filenames on newly generated files (Directive 6).
4. Subagent-friendly: Grants full operational freedom to subagents executing legitimate code,
   analysis scripts, and document generation tools.
"""

import sys
import os
import re
import json
from typing import Dict, Any, List, Tuple

# Raw dataset indicators
RAW_DATA_DIR_TOKENS = (
    "01_raw_inputs", "01_raw", "raw_inputs", "raw_data", "raw_dataset", "/raw/"
)
RAW_DATA_FILE_EXACT = (
    "raw.xlsx", "raw.csv", "raw.sav", "raw.tsv",
    "data_raw.xlsx", "data_raw.csv", "data_raw.sav",
    "dataset_raw.xlsx", "dataset_raw.csv", "dataset_raw.sav"
)
RAW_DATA_PREFIXES = ("raw_", "raw-")


def is_raw_data_target(path: str) -> bool:
    """Detects whether a file path points to an immutable raw dataset."""
    if not path:
        return False
    norm = os.path.normpath(path).replace("\\", "/")
    parts = norm.split("/")
    basename = os.path.basename(norm).lower()

    # Never block python, shell, or documentation files outside raw directories
    if basename.endswith((".py", ".sh", ".md", ".jsonl", ".yaml", ".yml")):
        # Only block if inside a dedicated raw directory
        return any(p.lower() in ("01_raw_inputs", "01_raw", "raw_inputs", "raw_data") for p in parts[:-1])

    # Check directory parts
    for p in parts[:-1]:
        p_lower = p.lower()
        if p_lower in ("01_raw_inputs", "01_raw", "raw_inputs", "raw_data", "raw_dataset"):
            return True
        if "raw_input" in p_lower or "raw_data" in p_lower:
            return True

    # Check file basename
    if basename in RAW_DATA_FILE_EXACT:
        return True
    if any(basename.startswith(pre) for pre in RAW_DATA_PREFIXES) and basename.endswith((".xlsx", ".csv", ".sav", ".tsv", ".dta")):
        return True
    if ("_raw." in basename or "-raw." in basename) and basename.endswith((".xlsx", ".csv", ".sav", ".tsv", ".dta")):
        return True

    return False


def is_destructive_raw_command(cmd: str) -> bool:
    """Detects shell operations that attempt to delete, overwrite, or mutate raw datasets."""
    if not cmd:
        return False
    raw_token = r'(?:raw_data|data_raw|01_raw_inputs|raw_inputs|raw_dataset|raw_file|/raw/|_raw\.[a-zA-Z0-9]+|raw\.[a-zA-Z0-9]+)'
    destructive_patterns = [
        rf'\brm\s+[^;&|]*{raw_token}[^;&|\s]*',
        rf'\bmv\s+[^;&|]*{raw_token}[^;&|\s]*',
        rf'(?:>|>>)\s*[\'"]?[^;&|\s]*{raw_token}[^;&|\s]*',
        rf'\b(?:truncate|sed\s+-i|perl\s+-i)\b.*{raw_token}',
        rf'\bcp\s+[^;&|]+\s+[^;&|]*{raw_token}[^;&|\s]*',
        rf'\bchmod\s+[^;&|]*(?:\+w|777|666|0777|0666)[^;&|]*{raw_token}',
        rf'\btee\s+(?:-a\s+)?[\'"]?[^;&|\s]*{raw_token}',
        rf'\btouch\s+[\'"]?[^;&|\s]*{raw_token}'
    ]
    return any(re.search(pat, cmd, re.IGNORECASE) for pat in destructive_patterns)


def is_catastrophic_system_command(cmd: str) -> Tuple[bool, str]:
    """Detects catastrophic system destruction patterns."""
    if not cmd:
        return False, ""

    if re.search(r'\brm\s+-(?:r|rf|fr)\s+(?:\.agents|\.git)\b', cmd):
        return True, "SECURITY VIOLATION: Destruction of repository control directories (.agents or .git) is strictly prohibited."

    if re.search(r'\brm\s+-(?:r|rf|fr)\s+/(?:\s|$|\*)', cmd):
        return True, "SECURITY VIOLATION: Root filesystem destruction command blocked."

    if re.search(r':\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:', cmd):
        return True, "SECURITY VIOLATION: Fork bomb pattern detected and blocked."

    if is_destructive_raw_command(cmd):
        return True, "HARD HOOK ENFORCEMENT (Raw-Data Immutability Guard): Command attempts to modify, overwrite, or delete raw data files. Raw datasets are strictly immutable."

    return False, ""


def is_ascii_filename(path: str) -> bool:
    """Verifies that the basename of a target file strictly contains ASCII English characters."""
    if not path:
        return True
    basename = os.path.basename(path)
    try:
        basename.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False


def extract_target_paths(args: Dict[str, Any]) -> List[str]:
    """Extracts target file paths from tool arguments."""
    paths = []
    for key in ("TargetFile", "file_path", "filePath", "target_file", "path", "target"):
        val = args.get(key)
        if isinstance(val, str) and val.strip():
            paths.append(val.strip())

    for list_key in ("files", "paths", "targets", "file_paths"):
        val = args.get(list_key)
        if isinstance(val, list):
            for item in val:
                if isinstance(item, str) and item.strip():
                    paths.append(item.strip())
                elif isinstance(item, dict):
                    p = item.get("path") or item.get("file_path") or item.get("TargetFile")
                    if isinstance(p, str) and p.strip():
                        paths.append(p.strip())
    return list(dict.fromkeys(paths))


def evaluate_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluates PreToolUse lifecycle event for security and raw data safety."""
    tool_call = payload.get("toolCall", {})
    tool_name = (tool_call.get("name") or "").strip()
    args = tool_call.get("args", {})

    # 1. Shell command checks
    if tool_name == "run_command":
        cmd = args.get("CommandLine", "")
        is_danger, reason = is_catastrophic_system_command(cmd)
        if is_danger:
            return {"decision": "deny", "reason": reason}
        return {"decision": "allow"}

    # 2. File mutation checks
    mutation_tools = (
        "write_to_file", "replace_file_content", "edit_file",
        "apply_diff", "multi_file_edit", "patch", "batch_replace",
        "multi_replace_file_content"
    )
    if tool_name in mutation_tools:
        targets = extract_target_paths(args)
        for t_path in targets:
            # Check raw data immutability
            if is_raw_data_target(t_path):
                return {
                    "decision": "deny",
                    "reason": f"HARD HOOK ENFORCEMENT (Raw-Data Immutability Guard): Target path '{t_path}' is an immutable raw dataset. Modifications are strictly forbidden."
                }
            # Check English-only ASCII filename standard
            if not is_ascii_filename(t_path):
                b_name = os.path.basename(t_path)
                return {
                    "decision": "deny",
                    "reason": f"CONSTITUTIONAL VIOLATION (Directive 6 - English-Only Filename Standard): Filename '{b_name}' contains non-ASCII characters. All filenames must use ASCII English [a-zA-Z0-9_.-]."
                }

    # Everything else is fully allowed
    return {"decision": "allow"}


def main():
    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception:
        pass

    result = evaluate_pre_tool_use(payload)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
