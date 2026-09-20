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

try:
    from hook_seen import emit_hook_seen
except ImportError:
    from .hook_seen import emit_hook_seen

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
        emit_hook_seen(payload, event="PreToolUse")
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
                "test-worker",
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

        # 2. Raw-Data, Outside-Workspace & Orchestrator Code Guard on Mutation Tools
        if name in MUTATION_TOOLS:
            caller = (
                payload.get("agentName") or
                payload.get("agentRole") or
                payload.get("agent") or
                payload.get("caller") or ""
            ).lower()
            targets = extract_target_paths(name, args)

            # Orchestrator Mutation Guard (Phase 13, 17, 18 Zero-Hands Contract):
            # academic-orchestrator and test-orchestrator have no write/mutation privileges and cannot write or modify ANY files directly.
            if "academic-orchestrator" in caller:
                return {
                    "decision": "deny",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Directive 12.1 / Directive 19 / Phase 18 Zero-Hands Contract / Orchestrator Code Guard): "
                        "Academic-Orchestrator is strictly managerial and forbidden from writing or modifying files directly. "
                        "File generation, document drafting, and mutations must be delegated to specialist workers."
                    )
                }
            if "test-orchestrator" in caller:
                return {
                    "decision": "deny",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Directive 12.1 / Directive 19 / Phase 18 Zero-Hands Contract / Orchestrator Code Guard): "
                        "test-orchestrator is strictly managerial and forbidden from writing or modifying files directly. "
                        "File generation, document drafting, and mutations must be delegated to specialist workers."
                    )
                }

            read_only_callers = {
                "behavior-analyst",
                "curriculum-builder",
                "knowledge-curator",
                "skill-evolver",
                "trajectory-analyzer",
            }
            if any(roc in caller for roc in read_only_callers):
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Read-Only Agent Guard): "
                        f"Agent '{caller}' is read-only and forbidden from mutating files directly."
                    )
                }

            for target in targets:
                # State Ledger Immutability Guard (Invalid State Transition Guard)
                target_norm = os.path.normpath(target).replace("\\", "/")
                if any(target_norm.endswith(f"/{d}/{f}") or target_norm.endswith(f"{d}/{f}") for d in ("state", "academic-state") for f in ("current_state.json", "events.jsonl", "approvals.json")):
                    if "state_manager" not in caller and "developer" not in caller and "main" not in caller:
                        return {
                            "decision": "deny",
                            "reason": (
                                f"CONSTITUTIONAL VIOLATION (Invalid State Transition Guard): "
                                f"Direct file modification of state ledger '{os.path.basename(target)}' is forbidden. "
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
            caller = (
                payload.get("agentName") or
                payload.get("agentRole") or
                payload.get("agent") or
                payload.get("caller") or ""
            ).lower()
            cmd = args.get("CommandLine", "")

            # Direct Execution Guard (Layer 4 Secondary Enforcement for Non-Executors):
            non_executing_callers = {
                "academic-orchestrator",
                "test-orchestrator",
                "methodology-expert",
                "statistical-expert",
                "results-auditor",
                "final-judge",
                "evidence-auditor",
                "academic-challenger",
                "journal-strategist",
                "intervention-designer",
                "behavior-analyst",
                "curriculum-builder",
                "knowledge-curator",
                "skill-evolver",
                "trajectory-analyzer",
            }
            for nec in non_executing_callers:
                if nec in caller:
                    if nec == "academic-orchestrator":
                        return {
                            "decision": "deny",
                            "reason": (
                                "CONSTITUTIONAL VIOLATION (Directive 2 / Directive 12.1 / Phase 3-4 Orchestrator Zero-Hands Contract): "
                                "Academic-Orchestrator is strictly forbidden from executing shell commands or code directly. "
                                "All execution and statistical analysis must be delegated to specialist workers (e.g. statistics-agent) via invoke_subagent."
                            )
                        }
                    elif nec == "test-orchestrator":
                        return {
                            "decision": "deny",
                            "reason": (
                                "CONSTITUTIONAL VIOLATION (Orchestrator Non-Execution Invariant): "
                                "test-orchestrator is strictly forbidden from executing shell commands or code directly. "
                                "All computation must be delegated to specialist workers via invoke_subagent."
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
                # 1. Block R execution
                if re.search(r'\b(?:Rscript|R)\s+', cmd):
                    return {
                        "decision": "deny",
                        "reason": (
                            "CONSTITUTIONAL VIOLATION (Directive 12 / Phase 10 - Academic Writer Execution Guard): "
                            "Academic-Writer is strictly forbidden from executing R scripts or commands. "
                            "Statistical computing must be delegated to statistics-agent."
                        )
                    }

                # 2. Block inline statistical calculations via python -c
                if re.search(r'python3?\s+-c\s+["\'].*(?:pandas|pingouin|scipy|statsmodels|sklearn|semopy|factor_analyzer).*["\']', cmd, re.IGNORECASE):
                    return {
                        "decision": "deny",
                        "reason": (
                            "CONSTITUTIONAL VIOLATION (Directive 12 / Phase 10 - Academic Writer Execution Guard): "
                            "Academic-Writer is strictly forbidden from executing inline statistical calculations directly. "
                            "Statistical computation must be delegated to statistics-agent or data-agent."
                        )
                    }

                # 3. Check any python script execution
                py_matches = list(re.finditer(r'python3?(?:\s+-[a-zA-Z0-9]+)*\s+([^\s;&|]+\.py)', cmd))
                if py_matches:
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
                    statistical_indicators = (
                        "regression", "mediation", "moderation", "sem", "cfa", "efa",
                        "assumption", "statistical", "stats", "data_cleaning", "data-cleaning",
                        "clean_and_score", "data_audit", "data-audit", "audit_dataset",
                        "descriptive", "longitudinal", "modmed", "meta_analyst", "meta-analyst",
                        "gpower", "sample_size", "psychometric", "scale_validator",
                        "data_simulator", "scale_resolver", "reliability", "qualitative",
                        "ancova", "anova", "ttest", "correlation", "factor_analysis"
                    )

                    for py_match in py_matches:
                        script_path = py_match.group(1).replace("\\", "/")
                        norm_path = os.path.normpath(script_path).replace("\\", "/")

                        if "/skills/" in norm_path or norm_path.startswith("skills/"):
                            skill_part = (
                                norm_path.split("/skills/")[1].split("/")[0]
                                if "/skills/" in norm_path
                                else norm_path.split("skills/")[1].split("/")[0]
                            )
                            if skill_part not in allowed_writing_skills:
                                return {
                                    "decision": "deny",
                                    "reason": (
                                        f"CONSTITUTIONAL VIOLATION (Directive 12 / Phase 10 - Academic Writer Execution Guard): "
                                        f"Academic-Writer run_command privilege is strictly confined to declared document-generation "
                                        f"and formatting workflows. Target script '{script_path}' belongs to skill '{skill_part}', "
                                        f"which is outside declared writing skills. Delegate statistical work to statistics-agent."
                                    )
                                }
                        else:
                            basename = os.path.basename(norm_path).lower()
                            if any(stat_kw in norm_path.lower() for stat_kw in statistical_indicators):
                                return {
                                    "decision": "deny",
                                    "reason": (
                                        f"CONSTITUTIONAL VIOLATION (Directive 12 / Phase 10 - Academic Writer Execution Guard): "
                                        f"Academic-Writer cannot execute statistical script '{script_path}'. "
                                        f"Delegate computation to statistics-agent or data-agent."
                                    )
                                }
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
                                "doc",
                                "docx",
                                "pptx",
                                "slide",
                                "brief"
                            )
                            if not any(pat in basename for pat in allowed_doc_patterns):
                                return {
                                    "decision": "deny",
                                    "reason": (
                                        f"CONSTITUTIONAL VIOLATION (Directive 12 / Phase 10 - Academic Writer Execution Guard): "
                                        f"Academic-Writer script execution is confined to declared document-generation tools. "
                                        f"Script '{script_path}' is not an authorized document-generation utility."
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

        # 4. Indirect Execution Prevention: MCP Tool Gate (Phase 18)
        if name == "call_mcp_tool":
            caller = (
                payload.get("agentName") or
                payload.get("agentRole") or
                payload.get("agent") or
                payload.get("caller") or ""
            ).lower()
            server_name = (args.get("ServerName") or "").lower()
            tool_name = (args.get("ToolName") or "").lower()

            non_executing_callers = {
                "academic-orchestrator",
                "methodology-expert",
                "statistical-expert",
                "results-auditor",
                "academic-challenger",
                "final-judge",
                "evidence-auditor",
                "journal-strategist",
            }
            if any(nec in caller for nec in non_executing_callers):
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Phase 18 - Indirect Execution Guard): "
                        f"Agent '{caller}' lacks execution privileges and is strictly forbidden from executing MCP tools ('{server_name}/{tool_name}')."
                    )
                }

            high_risk_mcp_tools = {
                "exec", "execute_sql", "deploy_edge_function",
                "apply_migration", "actions_run_trigger"
            }
            if tool_name in high_risk_mcp_tools:
                authorized_executors = {"statistics-agent", "data-agent", "research-agent"}
                if not any(ae in caller for ae in authorized_executors):
                    return {
                        "decision": "deny",
                        "reason": (
                            f"CONSTITUTIONAL VIOLATION (Phase 18 - Indirect Execution Guard): "
                            f"Indirect code/shell/database execution via MCP tool '{server_name}/{tool_name}' is forbidden for '{caller}'."
                        )
                    }

        # 5. Indirect Execution Prevention: Subagent Proxy Creation Gate (define_subagent)
        if name == "define_subagent":
            caller = (
                payload.get("agentName") or
                payload.get("agentRole") or
                payload.get("agent") or
                payload.get("caller") or ""
            ).lower()
            if "academic-orchestrator" in caller or any(role in caller for role in ["auditor", "expert", "challenger", "judge"]):
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Phase 18 - Indirect Execution Guard): "
                        f"Agent '{caller}' is forbidden from dynamically defining proxy subagents via define_subagent. "
                        f"Multi-agent delegation must use canonical, pre-configured subagents."
                    )
                }
            if args.get("enable_write_tools") or args.get("enable_subagent_tools"):
                return {
                    "decision": "deny",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Phase 18 - Indirect Execution Guard): "
                        "Dynamic elevation of write or subagent privileges via define_subagent is strictly prohibited."
                    )
                }

        # 6. Indirect Execution Prevention: Background Process Injection Gate (manage_task)
        if name == "manage_task":
            caller = (
                payload.get("agentName") or
                payload.get("agentRole") or
                payload.get("agent") or
                payload.get("caller") or ""
            ).lower()
            action = (args.get("Action") or "").lower()
            if action == "send_input":
                if "academic-orchestrator" in caller or any(role in caller for role in ["auditor", "expert", "challenger", "judge"]):
                    return {
                        "decision": "deny",
                        "reason": (
                            f"CONSTITUTIONAL VIOLATION (Phase 18 - Indirect Execution Guard): "
                            f"Agent '{caller}' is forbidden from injecting shell input into background tasks via manage_task."
                        )
                    }

        # 7. Indirect Execution Prevention: Scheduled Execution Gate (schedule)
        if name == "schedule":
            caller = (
                payload.get("agentName") or
                payload.get("agentRole") or
                payload.get("agent") or
                payload.get("caller") or ""
            ).lower()
            non_executing_callers = {
                "academic-orchestrator",
                "methodology-expert",
                "statistical-expert",
                "results-auditor",
                "academic-challenger",
                "final-judge",
                "evidence-auditor",
                "journal-strategist",
                "intervention-designer",
                "behavior-analyst",
                "curriculum-builder",
                "knowledge-curator",
                "skill-evolver",
                "trajectory-analyzer",
            }
            if any(nec in caller for nec in non_executing_callers):
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Phase 18 - Indirect Execution Guard): "
                        f"Agent '{caller}' lacks execution privileges and is forbidden from scheduling background execution tasks."
                    )
                }

        # 8. Worker Return Payload & Formal Closure Guard (send_message / Phase 21 & Phase 22)
        if name == "send_message":
            caller = (
                payload.get("agentName") or
                payload.get("agentRole") or
                payload.get("agent") or
                payload.get("caller") or ""
            ).lower()
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

                # 8a. Orchestrator Closure Guard (Anti-Pattern: Orchestrator -> 'Great.')
                if "academic-orchestrator" in caller and detect_informal_closure is not None:
                    is_closure, closure_reason = detect_informal_closure(msg)
                    if is_closure:
                        return {
                            "decision": "deny",
                            "reason": f"CONSTITUTIONAL VIOLATION (Phase 22 - Formal Delegation Contract Invariant): {closure_reason}"
                        }

                # 8b. Worker Return Invariant Guard (rejects 'done', 'completed', 'finished', etc.)
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
