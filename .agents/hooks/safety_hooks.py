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

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HOOKS_DIR, "..", ".."))
AGENTS_DIR = os.path.abspath(os.path.join(HOOKS_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

try:
    from hook_seen import emit_hook_seen
except ImportError:
    from .hook_seen import emit_hook_seen
try:
    from contracts.canonical_tools import ALL_MUTATION_TOOLS as _ALL_MUTATION_TOOLS
    MUTATION_TOOLS = tuple(sorted(_ALL_MUTATION_TOOLS))
except ImportError:
    MUTATION_TOOLS = (
        "write_to_file",
        "replace_file_content",
        "multi_replace_file_content",
        "apply_diff",
        "edit_file",
        "multi_file_edit",
        "batch_replace",
        "patch",
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


def is_state_ledger_command(cmd: str, caller: str = "") -> Tuple[bool, str]:
    """
    Detects whether a bash command attempts to bypass state ledger immutability
    or execute unauthorized state mutations via run_command.
    """
    if not cmd:
        return False, ""

    state_tokens = (
        "current_state.json",
        "events.jsonl",
        "approvals.json",
        "approval_request.json",
        "decisions.json",
        "artifacts.json",
        "pitfalls.jsonl",
    )

    # 1. Direct file mutation via shell redirection or manipulation tools
    redirection_pattern = rf'(?:>|>>)\s*[\'"]?[^;&|\s]*(?:{"|".join(re.escape(t) for t in state_tokens)})'
    if re.search(redirection_pattern, cmd, re.IGNORECASE):
        return True, (
            "CONSTITUTIONAL VIOLATION (Invalid State Transition Guard): "
            "State ledger files ('current_state.json', 'events.jsonl', 'approvals.json') "
            "cannot be modified via run_command. State transitions must be authorized "
            "and executed through StrictStateMachine."
        )

    file_ops_pattern = (
        rf'\b(?:rm|mv|cp|truncate|sed\s+-i|perl\s+-i|tee(?:\s+-a)?|touch)\b.*'
        rf'(?:{"|".join(re.escape(t) for t in state_tokens)}|academic-state|academic_state)'
    )
    if re.search(file_ops_pattern, cmd, re.IGNORECASE):
        return True, (
            "CONSTITUTIONAL VIOLATION (Invalid State Transition Guard): "
            "State ledger files ('current_state.json', 'events.jsonl', 'approvals.json') "
            "cannot be modified via run_command. State transitions must be authorized "
            "and executed through StrictStateMachine."
        )

    # 2. Permission tampering on state directory or state files
    chmod_pattern = (
        rf'\b(?:chmod|chown)\b.*'
        rf'(?:{"|".join(re.escape(t) for t in state_tokens)}|academic-state|academic_state|\bstate\b)'
    )
    if re.search(chmod_pattern, cmd, re.IGNORECASE):
        return True, (
            "CONSTITUTIONAL VIOLATION (Invalid State Transition Guard): "
            "Tampering with state ledger permissions via chmod/chown is strictly forbidden. "
            "State ledgers are protected by OS least-privilege permissions."
        )

    # 3. Inline script execution (Python/Node/Perl) targeting state ledger files
    inline_py_state = (
        rf'python3?\s+-c\s+.*'
        rf'(?:{"|".join(re.escape(t) for t in state_tokens)}|academic-state|academic_state)'
    )
    if re.search(inline_py_state, cmd, re.IGNORECASE):
        return True, (
            "CONSTITUTIONAL VIOLATION (Invalid State Transition Guard): "
            "State ledger files ('current_state.json', 'events.jsonl', 'approvals.json') "
            "cannot be modified via run_command. State transitions must be authorized "
            "and executed through StrictStateMachine."
        )

    inline_open_write = (
        rf'open\s*\([^)]*(?:{"|".join(re.escape(t) for t in state_tokens)})[^)]*[\'"][wWaA+]'
    )
    if re.search(inline_open_write, cmd, re.IGNORECASE):
        return True, (
            "CONSTITUTIONAL VIOLATION (Invalid State Transition Guard): "
            "State ledger files ('current_state.json', 'events.jsonl', 'approvals.json') "
            "cannot be modified via run_command. State transitions must be authorized "
            "and executed through StrictStateMachine."
        )

    # 4. Worker Agent State CLI Execution Guard (Directive 19 / Separation of Concerns)
    # Execution workers must not directly invoke state manager CLI to set stages or request transitions
    worker_agents = {
        "statistics-agent", "data-agent", "academic-writer",
        "data-curator", "research-agent", "psychometric-expert"
    }
    if any(w in caller for w in worker_agents):
        if "academic_state_manager.py" in cmd:
            if any(action in cmd for action in ("set_stage", "set-stage", "request_transition", "request-transition")):
                return True, (
                    f"CONSTITUTIONAL VIOLATION (Directive 19 - Invalid State Transition Guard): "
                    f"Worker agent '{caller}' is forbidden from invoking state manager CLI directly. "
                    f"State transitions must be managed through authorized state machine workflows."
                )

    return False, ""


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

    is_state_violation, state_reason = is_state_ledger_command(cmd)
    if is_state_violation:
        return True, state_reason

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


def check_caller_policy(caller: str, tool_name: str, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Validates explicit caller against canonical capability policy SSOT
    (contracts/agents/agent_capabilities.yaml) if caller is explicitly provided.
    Returns denial dict if tool is forbidden for this agent, else None.
    """
    if not caller:
        return None
    try:
        from contracts.agents.capability_policy import load_capability_policy
        policy = load_capability_policy()
        agents = policy.get("agents", {})
        target = None
        for a in agents:
            if a == caller or a in caller:
                target = a
                break
        if not target:
            return None

        spec = agents[target]

        # 1. Delegation Check (Worker & Advisory Delegation Guard)
        if tool_name == "invoke_subagent" and not spec.get("can_delegate", True):
            if target == "digital-saber":
                return {
                    "decision": "deny",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Directive 12 - Digital Saber Delegation Bypass Guard): "
                        "Digital Saber is an advisory cognitive twin and is strictly forbidden from delegating to subagents. "
                        "All academic multi-agent orchestration must pass through academic-orchestrator."
                    )
                }
            return {
                "decision": "deny",
                "reason": (
                    f"CONSTITUTIONAL VIOLATION (Directive 12 - Worker Delegation Guard): "
                    f"Specialist worker subagent '{caller}' is forbidden from invoking secondary subagents. "
                    f"Multi-agent invocation is strictly reserved for Tier 1 orchestrator."
                )
            }

        # 2. Mutation Tools Check (Orchestrator Code Guard / Read-Only Guard)
        if tool_name in MUTATION_TOOLS and not spec.get("can_write_files", True):
            if "academic-orchestrator" in target:
                return {
                    "decision": "deny",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Directive 12.1 / Directive 19 / Phase 18 Zero-Hands Contract / Orchestrator Code Guard): "
                        "Academic-Orchestrator is strictly managerial and forbidden from writing or modifying files directly. "
                        "File generation, document drafting, and mutations must be delegated to specialist workers."
                    )
                }
            elif "test-orchestrator" in target:
                return {
                    "decision": "deny",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Directive 12.1 / Directive 19 / Phase 18 Zero-Hands Contract / Orchestrator Code Guard): "
                        "test-orchestrator is strictly managerial and forbidden from writing or modifying files directly. "
                        "File generation, document drafting, and mutations must be delegated to specialist workers."
                    )
                }
            elif "digital-saber" in target:
                return {
                    "decision": "deny",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Directive 12 / Directive 19 / Digital Saber Advisory Guard): "
                        "Digital Saber is an advisory cognitive twin and is forbidden from writing or modifying files directly."
                    )
                }
            else:
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Read-Only Agent Guard): "
                        f"Agent '{caller}' is read-only and forbidden from mutating files directly."
                    )
                }

        # 3. Direct Execution Check (run_command)
        if tool_name == "run_command" and not spec.get("can_execute_code", True):
            if target == "academic-orchestrator":
                return {
                    "decision": "deny",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Directive 2 / Directive 12.1 / Phase 3-4 Orchestrator Zero-Hands Contract): "
                        "Academic-Orchestrator is strictly forbidden from executing shell commands or code directly. "
                        "All execution and statistical analysis must be delegated to specialist workers (e.g. statistics-agent) via invoke_subagent."
                    )
                }
            elif target == "test-orchestrator":
                return {
                    "decision": "deny",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Orchestrator Non-Execution Invariant): "
                        "test-orchestrator is strictly forbidden from executing shell commands or code directly. "
                        "All computation must be delegated to specialist workers via invoke_subagent."
                    )
                }
            elif target == "digital-saber":
                return {
                    "decision": "deny",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Directive 2 / Directive 12 / Digital Saber Non-Execution Invariant): "
                        "Digital Saber is an advisory cognitive twin and is strictly forbidden from executing shell commands or code directly. "
                        "All execution and statistical analysis must be delegated through academic-orchestrator to specialist workers."
                    )
                }
            else:
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Non-Executing Authority Guard): "
                        f"Agent '{caller}' lacks execution privileges and is forbidden from executing shell commands directly. "
                        f"Computation must be delegated to authorized execution workers."
                    )
                }

        # 4. Indirect Execution Checks
        if tool_name == "define_subagent" and not spec.get("can_execute_code", True):
            return {
                "decision": "deny",
                "reason": (
                    f"CONSTITUTIONAL VIOLATION (Phase 18 - Indirect Execution Guard): "
                    f"Agent '{caller}' is forbidden from dynamically defining proxy subagents via define_subagent. "
                    f"Multi-agent delegation must use canonical, pre-configured subagents."
                )
            }

        if tool_name == "manage_task" and (args.get("Action") or "").lower() == "send_input" and not spec.get("can_execute_code", True):
            return {
                "decision": "deny",
                "reason": (
                    f"CONSTITUTIONAL VIOLATION (Phase 18 - Indirect Execution Guard): "
                    f"Agent '{caller}' is forbidden from injecting shell input into background tasks via manage_task."
                )
            }

        if tool_name == "schedule" and not spec.get("can_execute_code", True):
            return {
                "decision": "deny",
                "reason": (
                    f"CONSTITUTIONAL VIOLATION (Phase 18 - Indirect Execution Guard): "
                    f"Agent '{caller}' lacks execution privileges and is forbidden from scheduling background execution tasks."
                )
            }

        if tool_name == "call_mcp_tool":
            server_name = (args.get("ServerName") or "").lower()
            tool_mcp_name = (args.get("ToolName") or "").lower()
            if not spec.get("can_execute_code", True):
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Phase 18 - Indirect Execution Guard): "
                        f"Agent '{caller}' lacks execution privileges and is strictly forbidden from executing MCP tools ('{server_name}/{tool_mcp_name}')."
                    )
                }
            high_risk_mcp_tools = {
                "exec", "execute_sql", "deploy_edge_function",
                "apply_migration", "actions_run_trigger"
            }
            if tool_mcp_name in high_risk_mcp_tools:
                authorized_executors = {"statistics-agent", "data-agent", "research-agent"}
                if target not in authorized_executors:
                    return {
                        "decision": "deny",
                        "reason": (
                            f"CONSTITUTIONAL VIOLATION (Phase 18 - Indirect Execution Guard): "
                            f"Indirect code/shell/database execution via MCP tool '{server_name}/{tool_mcp_name}' is forbidden for '{caller}'."
                        )
                    }

    except Exception as e:
        sys.stderr.write(f"[safety_hooks] Policy check notice: {e}\n")
    return None


class SafetyHooks:
    """
    Class A: Safety Hooks
    Responsible for intercepting tool calls before execution to enforce safety invariants:
    tool -> target resource -> safety policy.
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
        emit_hook_seen(payload, event="PreToolUse")
        tool_call = payload.get("toolCall", {})
        name = tool_call.get("name", "")
        args = tool_call.get("args", {})
        workspaces = payload.get("workspacePaths", [])

        caller = (
            payload.get("agentName") or
            payload.get("agentRole") or
            payload.get("agent") or
            payload.get("caller") or ""
        ).lower().strip()

        # Secondary Enforcement: Check canonical capability policy if explicit caller provided
        if caller:
            policy_denial = check_caller_policy(caller, name, args)
            if policy_denial:
                return policy_denial

        # 1. Subagent Delegation Gate (Depth Guard & Formal Contract Check)
        if name == "invoke_subagent":
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

            # Phase 22: Formal Delegation Contract Check (Zero Informal Shortcuts)
            # Academic-Orchestrator cannot invoke subagents with informal prompts like 'Analyze this.'
            subagents = args.get("Subagents", [])
            prompts_to_check = []
            if isinstance(subagents, list):
                for sub in subagents:
                    if isinstance(sub, dict) and "Prompt" in sub:
                        prompts_to_check.append(sub["Prompt"])
            if "Prompt" in args:
                prompts_to_check.append(args["Prompt"])

            for p_text in prompts_to_check:
                if isinstance(p_text, str):
                    try:
                        from scripts.delegation_contract_engine import detect_informal_delegation
                    except ImportError:
                        try:
                            from delegation_contract_engine import detect_informal_delegation
                        except ImportError:
                            detect_informal_delegation = None

                    if detect_informal_delegation is not None:
                        is_informal, informal_reason = detect_informal_delegation(p_text)
                        if is_informal:
                            return {
                                "decision": "deny",
                                "reason": f"CONSTITUTIONAL VIOLATION (Phase 22 - Delegation Contract Invariant): {informal_reason}"
                            }

        # 2. Raw-Data, Outside-Workspace & State Ledger Guard on Mutation Tools (tool -> target resource -> safety policy)
        if name in MUTATION_TOOLS:
            targets = extract_target_paths(name, args)

            for target in targets:
                # State Ledger Immutability Guard (Invalid State Transition Guard)
                target_norm = os.path.normpath(target).replace("\\", "/")
                target_base = os.path.basename(target_norm)
                state_filenames = (
                    "current_state.json", "events.jsonl", "approvals.json",
                    "approval_request.json", "decisions.json", "project.json",
                    "artifacts.json", "pitfalls.jsonl"
                )
                if any(target_norm.endswith(f"/{d}/{f}") or target_norm.endswith(f"{d}/{f}") for d in ("state", "academic-state", ".agents/state") for f in state_filenames) or target_base in state_filenames:
                    if "state_manager" not in caller and "developer" not in caller and "main" not in caller:
                        return {
                            "decision": "deny",
                            "reason": (
                                f"CONSTITUTIONAL VIOLATION (Invalid State Transition Guard): "
                                f"Direct file modification of state ledger '{target_base}' is forbidden. "
                                f"State transitions must be authorized and executed through StrictStateMachine."
                            )
                        }

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

        # 3. Dangerous Shell Command & Orchestrator Direct Execution Protection
        if name == "run_command":
            cmd = args.get("CommandLine", "")

            # State Ledger Immutability Guard (run_command bypass protection)
            is_state_violation, state_reason = is_state_ledger_command(cmd, caller)
            if is_state_violation:
                return {
                    "decision": "deny",
                    "reason": state_reason
                }

            # State Transition via CLI Guard: block invalid set_stage in production mode
            if "academic_state_manager.py" in cmd:
                if "set_stage" in cmd and "--mode production" in cmd:
                    return {
                        "decision": "deny",
                        "reason": (
                            "CONSTITUTIONAL VIOLATION (Invalid State Transition Guard): "
                            "Direct stage mutation via set_stage is blocked in production mode. "
                            "Stage transitions must use formal request_transition."
                        )
                    }

            # Academic Writer Execution Boundary Guard (Directive 12 / Phase 10 Invariant):
            # academic-writer may execute ONLY declared document-generation / formatting workflows,
            # NOT independent statistical analysis, data cleaning, or psychometrics.
            if "academic-writer" in caller:
                # Step 1: Detect shell control and chaining operators
                # (;, &&, ||, |, &, `, $(), ${}, \n, \r)
                if any(op in cmd for op in (";", "&&", "||", "|", "`", "$(", "${", "\n", "\r")):
                    return {
                        "decision": "deny",
                        "reason": (
                            "CONSTITUTIONAL VIOLATION (Directive 12 / Phase 10 - Academic Writer Execution Guard): "
                            "Shell chaining, piping, backgrounding, or command substitution is strictly forbidden for academic-writer. "
                            "Commands must be single, unchained document-generation invocations."
                        )
                    }

                # Step 2: Safe tokenization with shlex
                try:
                    import shlex
                    tokens = shlex.split(cmd)
                except Exception as e:
                    return {
                        "decision": "deny",
                        "reason": (
                            f"CONSTITUTIONAL VIOLATION (Directive 12 / Phase 10 - Academic Writer Execution Guard): "
                            f"Malformed command string could not be safely tokenized: {e}"
                        )
                    }

                if not tokens:
                    return {
                        "decision": "deny",
                        "reason": "CONSTITUTIONAL VIOLATION: Empty command."
                    }

                # Step 3: Unconditionally forbid inline code execution (-c) and module execution (-m, -i)
                if any(t == "-c" or t.startswith("-c") for t in tokens):
                    return {
                        "decision": "deny",
                        "reason": (
                            "CONSTITUTIONAL VIOLATION (Directive 12 / Phase 10 - Academic Writer Execution Guard): "
                            "Inline code execution (-c) is strictly forbidden for academic-writer. "
                            "Academic-Writer cannot execute arbitrary inline Python or shell code. "
                            "Use the dedicated document generation interface (scripts/academic_docgen.py) or authorized document scripts."
                        )
                    }

                if any(t in ("-m", "-i") for t in tokens):
                    return {
                        "decision": "deny",
                        "reason": (
                            "CONSTITUTIONAL VIOLATION (Directive 12 / Phase 10 - Academic Writer Execution Guard): "
                            "Python module execution (-m) or interactive mode (-i) is forbidden for academic-writer."
                        )
                    }

                # Step 4: Tokenized executable verification
                raw_bin = tokens[0]
                bin_base = os.path.basename(raw_bin).lower()

                # Case A: Python script execution
                if bin_base in ("python", "python3", "py"):
                    if len(tokens) < 2:
                        return {
                            "decision": "deny",
                            "reason": (
                                "CONSTITUTIONAL VIOLATION (Directive 12 / Phase 10 - Academic Writer Execution Guard): "
                                "Python must be invoked with an explicit authorized document script."
                            )
                        }

                    target_script = tokens[1].replace("\\", "/")
                    norm_script = os.path.normpath(target_script).replace("\\", "/")
                    script_base = os.path.basename(norm_script).lower()

                    # Dedicated docgen CLI interface (scripts/academic_docgen.py)
                    if script_base == "academic_docgen.py":
                        allowed_subcommands = {
                            "render-docx",
                            "render-markdown",
                            "scaffold-triad",
                            "compile-thesis",
                            "compile-presentation",
                            "scaffold-apa-tables",
                            "polish-tone",
                        }
                        subcmd = tokens[2] if len(tokens) > 2 else ""
                        if subcmd not in allowed_subcommands:
                            return {
                                "decision": "deny",
                                "reason": (
                                    f"CONSTITUTIONAL VIOLATION (Directive 12 / Phase 10 - Academic Writer Execution Guard): "
                                    f"Unauthorized academic_docgen subcommand '{subcmd}'. "
                                    f"Permitted subcommands: {sorted(allowed_subcommands)}"
                                )
                            }
                        # Allowed docgen invocation!
                    else:
                        # Legacy standalone document scripts
                        allowed_writing_skills = {
                            "chapter-4-writing",
                            "persian-literature-review-builder",
                            "persian-discussion-builder",
                            "persian-thesis-builder",
                            "persian-thesis-revision-assistant",
                            "persian-proposal-builder",
                            "academic-article-writer",
                            "ai-academic-tone-polisher",
                            "apa-reporting",
                            "psychological-intervention-protocol-builder",
                            "journal-submission-assistant",
                            "persian-defense-presentation-builder",
                            "academic-reference-extractor",
                            "academic-adaptive-context",
                        }
                        allowed_explicit_scripts = {
                            "scaffold_chapter4_triad.py",
                            "compile_full_thesis.py",
                            "scaffold_apa_tables.py",
                            "tone_polisher_engine.py",
                            "compile_defense_presentation.py",
                            "structured_docx_generator.py",
                            "persian_docx_engine.py",
                            "build_hypothesis_triad_docx.py",
                        }
                        statistical_indicators = (
                            "regression", "mediation", "moderation", "sem", "cfa", "efa",
                            "assumption", "statistical", "stats", "data_cleaning", "data-cleaning",
                            "clean_and_score", "data_audit", "data-audit", "audit_dataset",
                            "descriptive", "longitudinal", "modmed", "meta_analyst", "meta-analyst",
                            "gpower", "sample_size", "psychometric", "scale_validator",
                            "data_simulator", "scale_resolver", "reliability", "qualitative",
                            "ancova", "anova", "ttest", "correlation", "factor_analysis"
                        )

                        if any(stat_kw in norm_script.lower() for stat_kw in statistical_indicators):
                            return {
                                "decision": "deny",
                                "reason": (
                                    f"CONSTITUTIONAL VIOLATION (Directive 12 / Phase 10 - Academic Writer Execution Guard): "
                                    f"Academic-Writer cannot execute statistical script '{target_script}'. "
                                    f"Delegate computation to statistics-agent or data-agent."
                                )
                            }

                        if "/skills/" in norm_script or norm_script.startswith("skills/"):
                            skill_part = (
                                norm_script.split("/skills/")[1].split("/")[0]
                                if "/skills/" in norm_script
                                else norm_script.split("skills/")[1].split("/")[0]
                            )
                            if skill_part not in allowed_writing_skills:
                                return {
                                    "decision": "deny",
                                    "reason": (
                                        f"CONSTITUTIONAL VIOLATION (Directive 12 / Phase 10 - Academic Writer Execution Guard): "
                                        f"Academic-Writer run_command privilege is strictly confined to declared document-generation "
                                        f"and formatting workflows. Target script '{target_script}' belongs to skill '{skill_part}', "
                                        f"which is outside declared writing skills. Delegate statistical work to statistics-agent."
                                    )
                                }
                        else:
                            allowed_doc_patterns = (
                                "test",
                                "structured_docx_generator.py",
                                "openxml_docx_engine.py",
                                "persian_docx_engine.py",
                                "scaffold_",
                                "build_",
                                "render_",
                                "export_",
                                "format_",
                                "academic_docgen.py",
                                "doc",
                                "docx",
                                "pptx",
                                "slide",
                                "brief"
                            )
                            if script_base not in allowed_explicit_scripts and not any(pat in script_base for pat in allowed_doc_patterns):
                                return {
                                    "decision": "deny",
                                    "reason": (
                                        f"CONSTITUTIONAL VIOLATION (Directive 12 / Phase 10 - Academic Writer Execution Guard): "
                                        f"Academic-Writer script execution is confined to declared document-generation tools. "
                                        f"Script '{target_script}' is not an authorized document-generation utility."
                                    )
                                }

                # Case B: Approved non-Python document utilities
                elif bin_base in ("pandoc", "soffice", "mkdir", "cp"):
                    pass  # Allowed document utilities

                # Case C: All other binaries are strictly forbidden
                else:
                    return {
                        "decision": "deny",
                        "reason": (
                            f"CONSTITUTIONAL VIOLATION (Directive 12 / Phase 10 - Academic Writer Execution Guard): "
                            f"Binary '{raw_bin}' is strictly forbidden for academic-writer. "
                            f"Only Python document generation scripts and document utilities (pandoc, soffice, mkdir, cp) are permitted."
                        )
                    }

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

        # 4. Indirect Execution Prevention: Dynamic Subagent Elevation Guard (define_subagent)
        if name == "define_subagent":
            if args.get("enable_write_tools") or args.get("enable_subagent_tools"):
                return {
                    "decision": "deny",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Phase 18 - Indirect Execution Guard): "
                        "Dynamic elevation of write or subagent privileges via define_subagent is strictly prohibited."
                    )
                }

        # 5. Worker Return Payload & Formal Closure Guard (send_message / Phase 21 & Phase 22)
        if name == "send_message":
            msg = args.get("Message", "")
            if isinstance(msg, str):
                try:
                    from scripts.delegation_contract_engine import detect_informal_worker_return, detect_informal_closure
                except ImportError:
                    try:
                        from delegation_contract_engine import detect_informal_worker_return, detect_informal_closure
                    except ImportError:
                        detect_informal_worker_return = None
                        detect_informal_closure = None

                # 5a. Orchestrator Closure Guard (Anti-Pattern: Orchestrator -> 'Great.')
                if "academic-orchestrator" in caller and detect_informal_closure is not None:
                    is_closure, closure_reason = detect_informal_closure(msg)
                    if is_closure:
                        return {
                            "decision": "deny",
                            "reason": f"CONSTITUTIONAL VIOLATION (Phase 22 - Formal Delegation Contract Invariant): {closure_reason}"
                        }

                # 5b. Worker Return Invariant Guard (rejects 'done', 'completed', 'finished', etc.)
                if detect_informal_worker_return is not None:
                    is_inf_ret, ret_reason = detect_informal_worker_return(msg)
                    if is_inf_ret:
                        return {
                            "decision": "deny",
                            "reason": (
                                f"CONSTITUTIONAL VIOLATION (Phase 21-22 - Worker Return Invariant): "
                                f"Worker subagents cannot return simply '{msg}'. Return payloads must be structured "
                                f"and contain: 'artifact', 'evidence', 'status', 'validation'. Details: {ret_reason}"
                            )
                        }

                # General informal closure fallback
                if detect_informal_closure is not None:
                    is_closure, closure_reason = detect_informal_closure(msg)
                    if is_closure:
                        return {
                            "decision": "deny",
                            "reason": f"CONSTITUTIONAL VIOLATION (Phase 22 - Formal Delegation Contract Invariant): {closure_reason}"
                        }

        return {"decision": "allow"}

    @staticmethod
    def check_unauthorized_tool_attempt(payload: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Secondary Enforcement (Unauthorized Tool Attempt Guard):
        Checks whether a tool call violates agent capability boundaries, direct/indirect
        execution policies, or workspace safety invariants.
        Returns (is_unauthorized, reason).
        """
        res = SafetyHooks.handle_pre_tool_use(payload)
        if res.get("decision") == "deny":
            return True, res.get("reason", "Unauthorized tool call")
        return False, ""



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
