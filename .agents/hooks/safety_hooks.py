#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/safety_hooks.py — Class A: Safety Hooks

Enforces execution interception and protection:
1. Raw-data protection: Blocks writes and destructive shell commands targeting raw datasets.
2. Dangerous command protection: Blocks destructive bash commands (rm -rf .agents, .git, root /, etc.).
3. Outside-workspace protection: Validates workspace confinement and English-only ASCII filenames (Directive 6).
4. Subagent delegation guard: Blocks unauthorized secondary subagent invocations and excessive nesting depth.

INVARIANT: Hooks are purely for interception, safety, and enforcement.
Hooks must NEVER act as the academic orchestrator.
"""

import os
import sys
import re
import stat
from typing import Dict, Any, List, Optional, Tuple

MUTATION_TOOLS = (
    "write_to_file",
    "replace_file_content",
    "apply_diff",
    "edit_file",
    "multi_file_edit",
    "batch_replace",
    "patch"
)


def extract_target_paths(tool_name: str, args: Dict[str, Any]) -> List[str]:
    """Extracts all file paths targeted for mutation across various tool signatures."""
    paths = []
    # 1. Standard single-file keys
    for key in ("TargetFile", "file_path", "filePath", "target_file", "path", "target"):
        val = args.get(key)
        if val and isinstance(val, str):
            paths.append(val)

    # 2. Multi-file or batch list keys
    for list_key in ("files", "paths", "targets", "file_paths"):
        val = args.get(list_key)
        if isinstance(val, list):
            for item in val:
                if isinstance(item, str):
                    paths.append(item)
                elif isinstance(item, dict):
                    p = item.get("path") or item.get("file_path") or item.get("TargetFile") or item.get("target")
                    if p and isinstance(p, str):
                        paths.append(p)

    return list(dict.fromkeys(paths))


def is_raw_data_path(path: str) -> bool:
    """Detects whether a file path points to an immutable raw dataset or directory."""
    if not path:
        return False
    norm = os.path.normpath(path).replace("\\", "/")
    parts = norm.split("/")
    basename = os.path.basename(norm).lower()

    # Check directory hierarchy
    for p in parts[:-1]:
        p_lower = p.lower()
        if p_lower in ("raw", "raw_data", "raw_inputs", "01_raw_inputs", "01_raw", "raw-data", "raw_dataset"):
            return True
        if "raw_input" in p_lower or "raw_data" in p_lower or "raw_dataset" in p_lower:
            return True

    # Check filename (only for dataset files, not code or markdown outside raw dirs)
    if basename.endswith((".py", ".sh", ".md", ".yaml", ".yml", ".jsonl")):
        return False

    raw_prefixes = ("raw_", "raw-")
    raw_exact = (
        "raw.xlsx", "raw.csv", "raw.sav", "raw.tsv",
        "data_raw.xlsx", "data_raw.csv", "data_raw.sav",
        "dataset_raw.xlsx", "dataset_raw.csv", "dataset_raw.sav"
    )
    if basename in raw_exact:
        return True
    if any(basename.startswith(pre) for pre in raw_prefixes):
        return True
    if "_raw." in basename or "-raw." in basename:
        return True
    if "raw_data." in basename or "raw-data." in basename:
        return True

    return False


def is_raw_data_command(cmd: str) -> bool:
    """Detects whether a bash command attempts to modify, overwrite, or delete raw data."""
    if not cmd:
        return False
    raw_token = r'(?:raw_data|data_raw|01_raw_inputs|raw_inputs|raw_dataset|raw_file|/raw/|_raw\.[a-zA-Z0-9]+|raw\.[a-zA-Z0-9]+)'
    patterns = [
        rf'\brm\s+[^;&|]*{raw_token}[^;&|\s]*',
        rf'\bmv\s+[^;&|]*{raw_token}[^;&|\s]*',
        rf'(?:>|>>)\s*[\'"]?[^;&|\s]*{raw_token}[^;&|\s]*',
        rf'\b(?:truncate|sed\s+-i|perl\s+-i)\b.*{raw_token}',
        rf'\bcp\s+[^;&|]+\s+[^;&|]*{raw_token}[^;&|\s]*',
        rf'\bchmod\s+[^;&|]*(?:\+w|777|666|0777|0666)[^;&|]*{raw_token}',
        rf'\btee\s+(?:-a\s+)?[\'"]?[^;&|\s]*{raw_token}',
        rf'\btouch\s+[\'"]?[^;&|\s]*{raw_token}'
    ]
    return any(re.search(pat, cmd, re.IGNORECASE) for pat in patterns)


def is_dangerous_command(cmd: str) -> Tuple[bool, str]:
    """Detects destructive system commands or security breaches."""
    if not cmd:
        return False, ""

    if re.search(r'\brm\s+-(?:r|rf|fr)\s+(?:\.agents|\.git)\b', cmd):
        return True, "SECURITY VIOLATION: Destruction of .agents or .git directories is strictly prohibited."

    if re.search(r'\brm\s+-(?:r|rf|fr)\s+/(?:\s|$)', cmd):
        return True, "SECURITY VIOLATION: Root filesystem destruction command blocked."

    if re.search(r':\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:', cmd):
        return True, "SECURITY VIOLATION: Fork bomb pattern detected and blocked."

    if is_raw_data_command(cmd):
        return True, (
            f"HARD HOOK ENFORCEMENT (Raw-Data Immutability Guard): Command attempts to modify, "
            f"overwrite, or delete raw data files ('{cmd}'). Raw datasets are strictly immutable."
        )

    return False, ""


def is_outside_workspace(path: str, workspaces: List[str]) -> bool:
    """Detects whether a target path is outside the authorized workspace boundaries."""
    if not path or not workspaces:
        return False
    abs_target = os.path.abspath(path)
    for ws in workspaces:
        abs_ws = os.path.abspath(ws)
        if abs_target == abs_ws or abs_target.startswith(abs_ws + os.sep):
            return False
    return True


def is_ascii_filename(path: str) -> bool:
    """Enforces Directive 6: English-only ASCII filenames."""
    if not path:
        return True
    basename = os.path.basename(path)
    return not any(ord(c) > 127 for c in basename)


class SafetyHooks:
    """
    Class A: Safety Hooks
    Responsible for intercepting tool calls before execution to enforce safety invariants.
    """

    @staticmethod
    def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for PreToolUse safety checks:
        1. Subagent delegation guard (worker agents cannot invoke subagents, max depth < 3)
        2. Raw-data protection across mutation tools
        3. Outside-workspace protection & ASCII filename standard (Directive 6)
        4. Dangerous shell command interception
        """
        tool_call = payload.get("toolCall", {})
        name = tool_call.get("name", "")
        args = tool_call.get("args", {})
        workspaces = payload.get("workspacePaths", [])

        # 1. Subagent Delegation Gate (Worker Delegation Guard & Depth Guard)
        if name == "invoke_subagent":
            caller = (
                payload.get("agentName") or
                payload.get("agentRole") or
                payload.get("agent") or
                payload.get("caller") or ""
            ).lower()
            unauthorized_workers = {
                "academic-writer",
                "evidence-auditor",
                "final-judge",
                "statistics-agent",
                "data-agent",
                "data-curator",
                "results-auditor",
                "statistical-auditor",
                "psychometric-expert",
                "qualitative-analyst",
                "meta-analyst",
                "literature-expert",
                "research-agent",
            }
            for w in unauthorized_workers:
                if w in caller:
                    return {
                        "decision": "deny",
                        "reason": (
                            f"CONSTITUTIONAL VIOLATION (Directive 12 - Worker Delegation Guard): "
                            f"Specialist worker subagent '{caller}' is forbidden from invoking secondary subagents. "
                            f"Multi-agent invocation is strictly reserved for Tier 1 orchestrator."
                        )
                    }

            depth = payload.get("depth") or payload.get("subagentDepth") or len(payload.get("parentConversationIds", []))
            if isinstance(depth, int) and depth >= 3:
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Directive 12 - Excessive Nesting Guard): "
                        f"Dynamic subagent delegation depth ({depth} >= 3) exceeds the maximum allowed nesting ceiling. "
                        f"Flatten workflow into Tier 1 orchestration."
                    )
                }

        # 2. Raw-Data & Outside-Workspace Protection on Mutation Tools
        if name in MUTATION_TOOLS:
            targets = extract_target_paths(name, args)
            for target in targets:
                # Raw data immutability
                if is_raw_data_path(target):
                    if os.path.exists(target):
                        try:
                            os.chmod(target, stat.S_IREAD if sys.platform == "win32" else 0o444)
                        except Exception:
                            pass
                    return {
                        "decision": "deny",
                        "reason": (
                            f"HARD HOOK ENFORCEMENT (Raw-Data Immutability Guard): Modification of raw dataset file '{target}' "
                            f"is strictly prohibited. Raw datasets are immutable. Transform data into "
                            f"separate analytical/cleaned files (e.g., 'data_cleaned.xlsx', 'data_scored.xlsx') instead."
                        )
                    }

                # English-only ASCII filenames (Directive 6)
                if not is_ascii_filename(target):
                    basename = os.path.basename(target)
                    return {
                        "decision": "deny",
                        "reason": (
                            f"CONSTITUTIONAL VIOLATION (Directive 6 - English-Only Filename Standard): "
                            f"Target filename '{basename}' contains non-ASCII characters. Filenames must use English ASCII only."
                        )
                    }

                # Outside-workspace protection (when workspaces declared and path is absolute)
                if workspaces and os.path.isabs(target):
                    if is_outside_workspace(target, workspaces):
                        # Allow system temp or benign scratch paths if needed, otherwise block
                        if not target.startswith("/tmp") and not ".gemini/antigravity" in target:
                            return {
                                "decision": "deny",
                                "reason": (
                                    f"HARD HOOK ENFORCEMENT (Outside-Workspace Guard): Target path '{target}' "
                                    f"is outside declared workspace directories: {workspaces}."
                                )
                            }

        # 3. Dangerous Shell Command Protection
        if name == "run_command":
            cmd = args.get("CommandLine", "")
            is_danger, reason = is_dangerous_command(cmd)
            if is_danger:
                return {
                    "decision": "deny",
                    "reason": reason
                }

            # English-only ASCII filename on redirects and mkdir
            redirect_match = re.search(r'(?:>|>>|\btouch\s+|\bmkdir\s+)([^\s;&|]+)', cmd)
            if redirect_match:
                filepath = redirect_match.group(1).strip("'\"")
                if not is_ascii_filename(filepath):
                    basename = os.path.basename(filepath)
                    return {
                        "decision": "deny",
                        "reason": (
                            f"CONSTITUTIONAL VIOLATION (Directive 6 - English-Only Filename Standard): "
                            f"Command attempts to create non-ASCII file/directory '{basename}'."
                        )
                    }

        return {"decision": "allow"}


def main():
    import json
    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[safety_hooks] Error parsing stdin JSON: {e}\n")

    res = SafetyHooks.handle_pre_tool_use(payload)
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
