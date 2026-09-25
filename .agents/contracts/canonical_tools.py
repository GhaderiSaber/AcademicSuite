#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
contracts/canonical_tools.py — Single Source of Truth for Antigravity Tool Taxonomy & Lifecycle Hook Matchers

Authoritative catalog of:
1. Canonical Antigravity Tools (supported natively in current Antigravity environment)
2. Tool Semantic Classifications (Read, Mutation, Direct Execution, Indirect Execution, Delegation, etc.)
3. Defensive / Legacy / Alias Tools (for fail-closed interception of legacy/hallucinated names)
4. Hook Interception Surface & Matcher Generation for .agents/hooks.json
"""

import os
import json
from typing import Set, Tuple, List, Dict, Any, Optional

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# ==============================================================================
# 1. Canonical Antigravity Tools (Current Environment)
# ==============================================================================

CANONICAL_FILE_READ_TOOLS: Set[str] = {
    "view_file",
    "list_dir",
    "grep_search",
    "find_by_name",
}

CANONICAL_FILE_MUTATION_TOOLS: Set[str] = {
    "write_to_file",
    "replace_file_content",
    "multi_replace_file_content",
}

CANONICAL_DIRECT_EXECUTION_TOOLS: Set[str] = {
    "run_command",
}

CANONICAL_INDIRECT_EXECUTION_TOOLS: Set[str] = {
    "call_mcp_tool",
    "define_subagent",
    "manage_task",
    "schedule",
}

CANONICAL_DELEGATION_TOOLS: Set[str] = {
    "invoke_subagent",
    "manage_subagents",
    "send_message",
    "define_subagent",
}

CANONICAL_INTERACTION_TOOLS: Set[str] = {
    "ask_question",
}

CANONICAL_WEB_MEDIA_TOOLS: Set[str] = {
    "read_url_content",
    "search_web",
    "generate_image",
}

CANONICAL_MCP_RESOURCE_TOOLS: Set[str] = {
    "list_resources",
    "read_resource",
}

# The complete, authoritative set of 21 canonical tools supported by Antigravity
CANONICAL_ANTIGRAVITY_TOOLS: Set[str] = (
    CANONICAL_FILE_READ_TOOLS
    | CANONICAL_FILE_MUTATION_TOOLS
    | CANONICAL_DIRECT_EXECUTION_TOOLS
    | CANONICAL_INDIRECT_EXECUTION_TOOLS
    | CANONICAL_DELEGATION_TOOLS
    | CANONICAL_INTERACTION_TOOLS
    | CANONICAL_WEB_MEDIA_TOOLS
    | CANONICAL_MCP_RESOURCE_TOOLS
)

# ==============================================================================
# 2. Defensive / Legacy / Alias Tools (Fail-Closed Guard Interception)
# ==============================================================================

# Tools not present in official Antigravity standard, but intercepted defensively
# if hallucinated by models or passed from external wrappers
LEGACY_OR_ALIAS_MUTATION_TOOLS: Set[str] = {
    "apply_diff",
    "edit_file",
    "multi_file_edit",
    "batch_replace",
    "patch",
}

# Consolidated mutation tool surface for safety hooks (raw data guard, state ledger guard, etc.)
ALL_MUTATION_TOOLS: Set[str] = CANONICAL_FILE_MUTATION_TOOLS | LEGACY_OR_ALIAS_MUTATION_TOOLS

# ==============================================================================
# 3. Lifecycle Hook Interception Surface (.agents/hooks.json)
# ==============================================================================

# Tools that MUST trigger PreToolUse and PostToolUse lifecycle hooks
HOOK_INTERCEPTED_TOOLS: Set[str] = (
    ALL_MUTATION_TOOLS
    | CANONICAL_DIRECT_EXECUTION_TOOLS
    | CANONICAL_INDIRECT_EXECUTION_TOOLS
    | {"invoke_subagent", "manage_subagents", "send_message"}
    | {"view_file", "read_resource", "read_url_content"}
)


def generate_hook_matcher() -> str:
    """Generates the authoritative regex matcher string for .agents/hooks.json."""
    return "|".join(sorted(HOOK_INTERCEPTED_TOOLS))


def get_hooks_json_path(base_dir: Optional[str] = None) -> str:
    """Returns the resolved path to .agents/hooks.json."""
    root = base_dir or ROOT_DIR
    return os.path.join(root, ".agents", "hooks.json")


def validate_hooks_json(hooks_json_path: Optional[str] = None) -> Tuple[bool, List[str]]:
    """
    Validates that .agents/hooks.json matchers are 100% in sync with generate_hook_matcher().
    Returns (is_valid, list_of_discrepancies).
    """
    path = hooks_json_path or get_hooks_json_path()
    if not os.path.isfile(path):
        return False, [f"hooks.json not found at: {path}"]

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return False, [f"Failed to parse hooks.json: {e}"]

    guard = data.get("track2-academic-orchestrator-guard") or data.get("constitutional-guard", {})
    expected_matcher = generate_hook_matcher()
    expected_tools = set(expected_matcher.split("|"))
    issues = []

    for event in ("PreToolUse", "PostToolUse"):
        configs = guard.get(event, [])
        if not configs:
            issues.append(f"Missing '{event}' configuration in guard")
            continue
        matcher = configs[0].get("matcher", "")
        actual_tools = set(matcher.split("|")) if matcher else set()
        
        missing = expected_tools - actual_tools
        extra = actual_tools - expected_tools
        if missing:
            issues.append(f"{event} matcher missing tools: {sorted(missing)}")
        if extra:
            issues.append(f"{event} matcher has unrecognized extra tools: {sorted(extra)}")

    return len(issues) == 0, issues


def sync_hooks_json(hooks_json_path: Optional[str] = None) -> bool:
    """
    Regenerates and synchronizes PreToolUse and PostToolUse matchers in .agents/hooks.json
    using the canonical tool vocabulary. Preserves formatting.
    """
    path = hooks_json_path or get_hooks_json_path()
    if not os.path.isfile(path):
        return False

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    matcher = generate_hook_matcher()
    target_keys = [k for k in ("track2-academic-orchestrator-guard", "constitutional-guard") if k in data]
    if not target_keys:
        target_keys = ["track2-academic-orchestrator-guard"]

    for key in target_keys:
        guard = data.setdefault(key, {})
        for event in ("PreToolUse", "PostToolUse"):
            configs = guard.setdefault(event, [{}])
            if configs and isinstance(configs, list):
                configs[0]["matcher"] = matcher

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return True
