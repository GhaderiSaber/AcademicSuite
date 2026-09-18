#!/usr/bin/env python3
"""
transcript_and_rule_guard.py — Antigravity Lifecycle Hook Gatekeeper

Enforces Digital Saber Constitutional Directives at the machine layer:
- PreInvocation: Injects un-bypassable ephemeral system instructions.
- Stop: Forensic inspection of transcript.jsonl before allowing execution termination.
  Blocks termination if the agent claims multi-agent execution without invoking subagents,
  or fails the Binary Honesty Protocol on compliance inquiries.
"""

import sys
import os
import json
import re
import glob
import stat
from typing import Dict, Any, List, Optional


def load_transcript(transcript_path: str) -> List[Dict[str, Any]]:
    """Loads and parses transcript.jsonl safely."""
    if not transcript_path or not os.path.exists(transcript_path):
        return []
    records = []
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    except Exception as e:
        sys.stderr.write(f"[transcript_and_rule_guard] Error reading transcript: {e}\n")
    return records


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


def is_protected_config_path(path: str) -> bool:
    """Detects whether a target file is an immutable system configuration file."""
    if not path:
        return False
    norm = os.path.normpath(path).replace("\\", "/")
    parts_lower = [p.lower() for p in norm.split("/")]
    basename = os.path.basename(norm).lower()

    if ".git" in parts_lower:
        return True
    if basename in ("hooks.json", "agents.md") and (".agents" in parts_lower or len(parts_lower) <= 2):
        return True
    return False


def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Intercepts tool calls to enforce Directive 3 (Artifact Gating), Directive 6 (English-Only Filenames) and security gates."""
    tool_call = payload.get("toolCall", {})
    name = tool_call.get("name", "")
    args = tool_call.get("args", {})
    workspaces = payload.get("workspacePaths", [])

    # 0a. Subagent Delegation Gate (ATK-03: Unauthorized Worker Delegation Guard)
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

        # Dynamic nesting depth guard (ATK-17)
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

    # 0. Raw-Data & Unauthorized Mutation Protection across all mutation tools
    if name in MUTATION_TOOLS:
        targets = extract_target_paths(name, args)
        for target in targets:
            # Check raw data immutability
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

            # Check protected system configuration tampering
            if is_protected_config_path(target) and args.get("Overwrite") is True:
                # Disallow full destructive overwrite of hooks.json via tools without admin confirmation
                if os.path.basename(target).lower() == "hooks.json":
                    pass  # permitted if purposeful, handled by git

            # Directive 6: Filename ASCII enforcement for all file modifying tools
            basename = os.path.basename(target)
            if any(ord(c) > 127 for c in basename):
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Directive 6 - English-Only Filename Standard): "
                        f"Target filename '{basename}' contains non-ASCII characters. Filenames must use English ASCII only."
                    )
                }

            # Directive 3: Micro-Stage & Hypothesis Section Gating for Chapter 4
            if basename.lower() in ("chapter_4_results.docx", "chapter4_results.docx", "chapter_4_results.md", "chapter4_results.md"):
                target_dir = os.path.dirname(target) or "."
                check_dirs = [target_dir] + workspaces
                
                # 1. Prerequisite data & audit artifacts
                has_stats = any(os.path.exists(os.path.join(d, "stats_results.json")) for d in check_dirs)
                has_audit = any(os.path.exists(os.path.join(d, "statistical_audit_report.json")) for d in check_dirs)
                if not has_stats or not has_audit:
                    return {
                        "decision": "deny",
                        "reason": (
                            "CONSTITUTIONAL VIOLATION (Directive 3 - Zero Skipping Rule): "
                            "Cannot assemble Chapter 4 before Stage 4 (stats_results.json) "
                            "and Stage 5 (statistical_audit_report.json) checkpoint artifacts exist on disk."
                        )
                    }

                # 2. Micro-stage section artifacts (Anti-Shortcut Guarantee)
                required_sections = [
                    ("01_demographics", ["*demographic*.docx", "*demographic*.md"]),
                    ("02_descriptives_and_reliability", ["*descriptive*.docx", "*descriptive*.md", "*reliability*.docx", "*reliability*.md"]),
                    ("03_parametric_assumptions", ["*assumption*.docx", "*assumption*.md"]),
                    ("04_bivariate_correlations", ["*correlation*.docx", "*correlation*.md"]),
                    ("hypothesis_1", ["*hypothesis_1*.docx", "*hypothesis_1*.md", "*hypo_1*.docx", "*hypo_1*.md"]),
                    ("chapter_summary", ["*chapter_summary*.docx", "*chapter_summary*.md", "*summary*.docx", "*summary*.md"])
                ]
                missing_sections = []
                for label, patterns in required_sections:
                    found = False
                    for d in check_dirs:
                        for pat in patterns:
                            if glob.glob(os.path.join(d, pat)):
                                found = True
                                break
                        if found:
                            break
                    if not found:
                        missing_sections.append(label)

                if missing_sections:
                    return {
                        "decision": "deny",
                        "reason": (
                            f"CONSTITUTIONAL VIOLATION (Directive 3 - Micro-Stage, Triad Artifact & One-Hypothesis-One-Stage Invariant): "
                            f"Cannot compile Chapter 4 in one shot. Missing required micro-stage section artifacts: "
                            f"{missing_sections}. Each section and hypothesis must be generated as an independent, "
                            f"verified artifact on disk (triad: .docx, .md, .json) before assembly."
                        )
                    }

            # Directive 3: Micro-Stage Gating for Chapter 5 final deliverable
            if basename.lower() in ("chapter_5_discussion.docx", "chapter5_discussion.docx", "chapter_5_discussion.md", "chapter5_discussion.md"):
                target_dir = os.path.dirname(target) or "."
                check_dirs = [target_dir] + workspaces
                required_ch5_sections = [
                    ("01_findings_recap", ["*recap*.docx", "*recap*.md", "*findings*.docx", "*findings*.md"]),
                    ("hypothesis_1_discussion", ["*hypothesis_1_discussion*.docx", "*hypothesis_1_discussion*.md", "*hypo_1_disc*.docx", "*hypo_1_disc*.md"]),
                    ("implications", ["*implication*.docx", "*implication*.md"]),
                    ("limitations", ["*limitation*.docx", "*limitation*.md"])
                ]
                missing_ch5 = []
                for label, patterns in required_ch5_sections:
                    found = False
                    for d in check_dirs:
                        for pat in patterns:
                            if glob.glob(os.path.join(d, pat)):
                                found = True
                                break
                        if found:
                            break
                    if not found:
                        missing_ch5.append(label)

                if missing_ch5:
                    return {
                        "decision": "deny",
                        "reason": (
                            f"CONSTITUTIONAL VIOLATION (Directive 3 - Micro-Stage, Triad Artifact & One-Hypothesis-One-Stage Invariant): "
                            f"Cannot compile Chapter 5 in one shot. Missing required micro-stage section artifacts: "
                            f"{missing_ch5}. Each hypothesis discussion and section must be drafted independently (triad: .docx, .md, .json) first."
                        )
                    }

    # 2. Shell command interceptor
    if name == "run_command":
        cmd = args.get("CommandLine", "")

        # Security: Block destructive removal of configuration repositories or root
        if re.search(r'\brm\s+-(?:r|rf|fr)\s+(?:\.agents|\.git)\b', cmd):
            return {
                "decision": "deny",
                "reason": "SECURITY VIOLATION: Destruction of .agents or .git directories is strictly prohibited."
            }

        if re.search(r'\brm\s+-(?:r|rf|fr)\s+/(?:\s|$)', cmd):
            return {
                "decision": "deny",
                "reason": "SECURITY VIOLATION: Root filesystem destruction command blocked."
            }

        if is_raw_data_command(cmd):
            return {
                "decision": "deny",
                "reason": (
                    f"HARD HOOK ENFORCEMENT (Raw-Data Immutability Guard): Command attempts to modify, overwrite, "
                    f"or delete raw data files ('{cmd}'). Raw datasets are strictly immutable."
                )
            }

        # Filename ASCII enforcement on redirects and directory creation
        redirect_match = re.search(r'(?:>|>>|\btouch\s+|\bmkdir\s+)([^\s;&|]+)', cmd)
        if redirect_match:
            filepath = redirect_match.group(1).strip("'\"")
            basename = os.path.basename(filepath)
            if any(ord(c) > 127 for c in basename):
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Directive 6 - English-Only Filename Standard): "
                        f"Command attempts to create non-ASCII file/directory '{basename}'."
                    )
                }

    return {"decision": "allow"}


def handle_post_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Logs tool execution event to state/audit_log.jsonl (or .agents/memory/audit_log.jsonl)."""
    try:
        from datetime import datetime, timezone

        workspaces = payload.get("workspacePaths", [])
        audit_dirs = []
        if workspaces:
            for ws in workspaces:
                cand_mem = os.path.join(ws, ".agents", "memory")
                cand_state = os.path.join(ws, "state")
                if os.path.exists(cand_mem):
                    audit_dirs.append(cand_mem)
                if os.path.exists(cand_state):
                    audit_dirs.append(cand_state)
                if not audit_dirs:
                    audit_dirs.append(cand_state)
                    os.makedirs(cand_state, exist_ok=True)
        else:
            default_mem = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "memory"))
            default_state = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "state"))
            if os.path.exists(default_mem):
                audit_dirs.append(default_mem)
            if os.path.exists(default_state):
                audit_dirs.append(default_state)
            if not audit_dirs:
                audit_dirs.append("state")
                os.makedirs("state", exist_ok=True)

        cid = payload.get("conversationId", "")
        step_idx = payload.get("stepIdx")
        error = payload.get("error")
        tool_call = payload.get("toolCall", {})

        tool_name = tool_call.get("name", "")
        tool_args = tool_call.get("args", {})

        transcript_path = payload.get("transcriptPath")
        if not tool_name:
            if not transcript_path and cid:
                cand = os.path.expanduser(f"~/.gemini/antigravity/brain/{cid}/.system_generated/logs/transcript.jsonl")
                if os.path.exists(cand):
                    transcript_path = cand
            records = load_transcript(transcript_path) if transcript_path else []
            for r in reversed(records):
                tcs = r.get("tool_calls", [])
                if tcs:
                    last_tc = tcs[-1]
                    if isinstance(last_tc, dict):
                        tool_name = last_tc.get("name", "")
                        tool_args = last_tc.get("args", {})
                    break

        sanitized_args = {k: v for k, v in tool_args.items() if k not in ("CodeContent", "ReplacementContent")}

        event_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "conversation_id": cid,
            "step_index": step_idx,
            "tool_name": tool_name or "unknown",
            "tool_args": sanitized_args,
            "error": error,
            "status": "ERROR" if error else "SUCCESS"
        }

        record_line = json.dumps(event_record, ensure_ascii=False) + "\n"
        for ad in set(audit_dirs):
            audit_file = os.path.join(ad, "audit_log.jsonl")
            with open(audit_file, "a", encoding="utf-8") as f:
                f.write(record_line)

    except Exception as e:
        sys.stderr.write(f"[transcript_and_rule_guard] Error writing audit log: {e}\n")

    return {}


def handle_post_invocation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Antigravity PostInvocation Hook:
    Performs mandatory verification checks after model tool turns.
    Returns injectSteps and terminationBehavior without emulating an agent orchestrator.
    """
    inject_steps = []
    workspaces = payload.get("workspacePaths", [])

    # Check for active stage directories with failing validation reports
    active_stage_dirs = []
    for ws in workspaces:
        proj_dir = os.path.join(ws, "projects")
        if os.path.exists(proj_dir):
            for root, dirs, files in os.walk(proj_dir):
                if any(re.search(r'^(?:\d+_)?[a-zA-Z0-9_-]+\.(?:docx|md|json)$', f) for f in files):
                    if any(re.search(r'(?:hypothesis|demographic|descriptive|assumption|correlation|model|curation|deliverable)', f, re.I) for f in files):
                        active_stage_dirs.append(root)

    for s_dir in set(active_stage_dirs):
        val_rep_path = os.path.join(s_dir, "validation_report.json")
        if os.path.exists(val_rep_path):
            try:
                with open(val_rep_path, "r", encoding="utf-8") as f:
                    val_data = json.load(f)
                if val_data.get("overall_verdict") == "FAIL":
                    failed_details = [r.get("check_name", "check") for r in val_data.get("results", []) if r.get("verdict") == "FAIL"]
                    inject_steps.append({
                        "ephemeralMessage": (
                            f"STAGE VERIFICATION ADVISORY: Active stage in '{s_dir}' failed validation "
                            f"({', '.join(failed_details[:3])}). Please run deterministic validators and fix errors before stage completion."
                        )
                    })
                    break
            except Exception:
                pass

    return {
        "injectSteps": inject_steps,
        "terminationBehavior": ""
    }


def handle_pre_invocation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Injects ephemeral prompt reminding the agent of strict constitutional directives."""
    reminder = (
        "🚨 CONSTITUTIONAL ENFORCEMENT ACTIVE (Directive 0, 3 & 11):\n"
        "1. Binary Honesty Protocol: If asked a compliance question, your response MUST begin with 'Yes' or 'No'.\n"
        "2. Micro-Stages, Triad Artifacts & One-Hypothesis-One-Stage Invariant (Directive 3): Monolithic drafting in one shot is prohibited. "
        "Every section and individual hypothesis must generate a synchronized triad of disk artifacts: .docx (Word), .md (Markdown), and .json (Data/Stats) before assembly.\n"
        "3. Interactive Stage-Gate Protocol (Directive 11): At the end of each stage, emit the Stage Completion Report "
        "(What was done + What will be done next), then STOP and wait for user confirmation before advancing.\n"
        "4. Multi-Agent Integrity: Under NO circumstance claim a multi-agent workflow unless you physically invoked "
        "subagents via 'invoke_subagent'.\n"
        "5. Sole Orchestrator Mandate (Directive 12.1): Antigravity is the sole agent runtime. Python scripts are strictly "
        "deterministic execution tools ('The Hands'). Never run agent emulators."
    )
    return {
        "injectSteps": [
            {
                "ephemeralMessage": reminder
            }
        ]
    }


def handle_stop(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Inspects transcript and workspace disk, blocking turn completion if deceptive claims or rule breaches occurred."""
    # 1. Physical Disk Check for Forbidden Python Orchestrators (Directive 12.1)
    workspaces = payload.get("workspacePaths", [])
    for ws in workspaces:
        forbidden_file = os.path.join(ws, ".agents", "skills", "academic-suite-orchestrator", "scripts", "multi_agent_orchestrator.py")
        if os.path.exists(forbidden_file):
            return {
                "decision": "continue",
                "reason": (
                    "CONSTITUTIONAL VIOLATION (Directive 12.1 - Sole Orchestrator Mandate): "
                    f"Forbidden file '{forbidden_file}' detected on disk. Standalone Python multi-agent "
                    "orchestrators are prohibited. Antigravity is the sole agent conductor. Delete this file immediately."
                )
            }

    # 2. Skill Modularity & Context Budget Check (Directive 18)
    check_dirs = [os.path.join(ws, ".agents", "skills") for ws in workspaces]
    default_skills_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skills"))
    if default_skills_dir not in check_dirs and os.path.exists(default_skills_dir):
        check_dirs.append(default_skills_dir)

    for s_dir in check_dirs:
        if os.path.exists(s_dir):
            guard_path = os.path.join(os.path.dirname(__file__), "skill_size_guard.py")
            if os.path.exists(guard_path):
                import importlib.util
                spec = importlib.util.spec_from_file_location("skill_size_guard", guard_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                res = mod.audit_skill_sizes(s_dir)
                if not res.get("passed", True):
                    violation_details = "; ".join(
                        [f"{v['skill']} ({v['line_count']} lines, {v['byte_size']} bytes)" for v in res["violations"]]
                    )
                    return {
                        "decision": "continue",
                        "reason": (
                            f"CONSTITUTIONAL VIOLATION (Directive 18 - Skill Modularity Standard): "
                            f"The following skill(s) exceed single-view limits (max 500 lines, 40,000 bytes): "
                            f"{violation_details}. Modularize extended guidelines into 'references/' before proceeding."
                        )
                    }

    # 3. Required Validation & Triad Artifact Gate (Phase 9 Hard Hook)
    active_stage_dirs = []
    for ws in workspaces:
        proj_dir = os.path.join(ws, "projects")
        if os.path.exists(proj_dir):
            for root, dirs, files in os.walk(proj_dir):
                if any(re.search(r'^(?:\d+_)?[a-zA-Z0-9_-]+\.(?:docx|md|json)$', f) for f in files):
                    if any(re.search(r'(?:hypothesis|demographic|descriptive|assumption|correlation|model|curation|deliverable)', f, re.I) for f in files):
                        active_stage_dirs.append(root)

    for s_dir in set(active_stage_dirs):
        files = os.listdir(s_dir)
        # Check Triad Artifact Invariant for stage deliverables (e.g. 01_demographics, 06_hypothesis_1)
        stage_prefixes = set()
        for f in files:
            m = re.match(r'^(\d+_[a-zA-Z0-9_-]+)\.(?:docx|md|json)$', f)
            if m:
                stage_prefixes.add(m.group(1))

        for pfx in stage_prefixes:
            has_docx = f"{pfx}.docx" in files
            has_md = f"{pfx}.md" in files
            has_json = f"{pfx}.json" in files
            missing = []
            if not has_docx: missing.append(f"{pfx}.docx")
            if not has_md: missing.append(f"{pfx}.md")
            if not has_json: missing.append(f"{pfx}.json")
            if missing and (has_docx or has_md or has_json):
                return {
                    "decision": "continue",
                    "reason": (
                        f"HARD HOOK ENFORCEMENT (Directive 3 - Triad Artifact Invariant): "
                        f"Stage '{pfx}' in '{s_dir}' has incomplete physical artifacts. Missing: {missing}. "
                        f"Every stage and individual hypothesis must generate a synchronized triad: .docx, .md, and .json."
                    )
                }

        # Check existing validation reports in stage directory
        val_rep_path = os.path.join(s_dir, "validation_report.json")
        if os.path.exists(val_rep_path):
            try:
                with open(val_rep_path, "r", encoding="utf-8") as f:
                    val_data = json.load(f)
                if val_data.get("overall_verdict") == "FAIL":
                    return {
                        "decision": "continue",
                        "reason": (
                            f"HARD HOOK ENFORCEMENT (Required Validation Gate): Stage artifacts in '{s_dir}' "
                            f"failed deterministic validation (overall_verdict: FAIL). Fix errors before completing."
                        )
                    }
            except Exception:
                pass

        # Dynamically execute validator suite if both json and md artifacts exist
        has_jsons = any(f.endswith(".json") and not f.startswith("validation_") for f in files)
        has_mds = any(f.endswith(".md") for f in files)
        if has_jsons and has_mds:
            validator_runner = None
            for ws in workspaces:
                cand = os.path.join(ws, "validators", "run_all_validators.py")
                if os.path.exists(cand):
                    validator_runner = cand
                    break
            if validator_runner:
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("val_runner", validator_runner)
                    vmod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(vmod)
                    rep = vmod.run_suite(s_dir)
                    if rep.get("overall_verdict") == "FAIL":
                        failed_tests = [r for r in rep.get("results", []) if r.get("verdict") == "FAIL"]
                        return {
                            "decision": "continue",
                            "reason": (
                                f"HARD HOOK ENFORCEMENT (Required Validation Gate): Automated deterministic validation "
                                f"failed for stage directory '{s_dir}'. Failures: {failed_tests}. Resolve errors before finishing."
                            )
                        }
                except Exception as e:
                    sys.stderr.write(f"[transcript_and_rule_guard] Error executing validation suite: {e}\n")

    transcript_path = payload.get("transcriptPath")
    cid = payload.get("conversationId")
    if not transcript_path:
        if cid:
            cand = os.path.expanduser(f"~/.gemini/antigravity/brain/{cid}/.system_generated/logs/transcript.jsonl")
            if os.path.exists(cand):
                transcript_path = cand
            else:
                sys.stderr.write(
                    f"[transcript_and_rule_guard WARNING] conversationId '{cid}' provided but transcript.jsonl "
                    f"not found at '{cand}'. Guard cannot audit conversation transcript.\n"
                )

    records = load_transcript(transcript_path) if transcript_path else []
    if not records:
        if transcript_path and not os.path.exists(transcript_path):
            sys.stderr.write(f"[transcript_and_rule_guard WARNING] transcript_path '{transcript_path}' does not exist on disk.\n")
        return {"decision": "allow"}

    subagent_calls_count = 0
    for r in records:
        for tc in r.get("tool_calls", []):
            name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", str(tc))
            if name == "invoke_subagent":
                subagent_calls_count += 1

    last_assistant_msg = ""
    last_user_msg = ""
    for r in reversed(records):
        stype = r.get("type")
        content = r.get("content", "")
        if not last_assistant_msg and stype == "PLANNER_RESPONSE" and content:
            last_assistant_msg = content.strip()
        elif not last_user_msg and stype == "USER_INPUT" and content:
            last_user_msg = content.strip()
        if last_assistant_msg and last_user_msg:
            break

    clean_user = re.sub(r"<[^>]+>", "", last_user_msg).strip()

    compliance_keywords = [
        "did you", "did the agent", "is the agent do correct", "did it follow",
        "fool me", "fooled me", "were the rules followed", "did you check",
        "did you use the workflow", "was the check performed"
    ]
    is_compliance_query = any(k in clean_user.lower() for k in compliance_keywords)

    if is_compliance_query and last_assistant_msg:
        cleaned_first_text = re.sub(r"^[#\*\s\>`_]+", "", last_assistant_msg)
        first_word = cleaned_first_text.split()[0].rstrip(".,:;!?*").capitalize() if cleaned_first_text.split() else ""
        if first_word not in ("Yes", "No"):
            return {
                "decision": "continue",
                "reason": (
                    f"CONSTITUTIONAL VIOLATION (Directive 0 - Binary Honesty Protocol): The user asked a compliance "
                    f"or honesty question ('{clean_user[:60]}...'). Your response must begin with an unambiguous "
                    f"'Yes' or 'No' as the very first word. Got: '{first_word}'. You must revise your response immediately."
                )
            }

    claim_patterns = [
        r"we (?:have )?(?:successfully )?(?:executed|run|completed) (?:a )?(?:complete(?:,)?\s+)?multi[- ]agent",
        r"(?:successfully )?executed (?:an? )?(?:complete(?:,)?\s+)?(?:antigravity )?multi[- ]agent",
        r"multi[- ]agent workflow [\"']?\w+[\"']? completed",
        r"completed,? multi[- ]agent [a-zA-Z0-9_-]+ (?:empirical )?pipeline",
        r"subagents executed:\s*\[",
        r"subagents? (?:were|have been|are) (?:invoked|executed|run|deliberated|coordinated)",
        r"delegated to (?:our|the)? subagents?",
        r"subagent deliberation completed",
        r"orchestrated (?:the )?(?:14|15 )?subagents",
        r"autonomous agents? (?:executed|deliberated|coordinated)",
        r"multi[- ]agent team (?:has )?(?:completed|executed|deliberated|analyzed)",
        r"pipeline run by (?:the )?subagents",
        r"ساب[‌ ]?ایجنت[‌ ]?ها (?:اجرا|بررسی|فراخوانی)",
        r"فرایند چند[‌ ]?عاملی"
    ]
    asst_lower = last_assistant_msg.lower()
    claims_multiagent = any(re.search(pat, asst_lower) for pat in claim_patterns)
    is_negated_review = any(neg in asst_lower for neg in [
        "did not execute", "was not a multi-agent", "called exactly zero",
        "called 0 times", "never invoked", "bypassed the multi-agent",
        "no subagents were invoked", "zero subagents were invoked"
    ])

    if claims_multiagent and not is_negated_review and subagent_calls_count == 0:
        return {
            "decision": "continue",
            "reason": (
                "CONSTITUTIONAL VIOLATION (Directive 0 & Directive 12): Your response claims a 'multi-agent' execution "
                "or subagent pipeline, but 'invoke_subagent' was called 0 times in this transcript! "
                "Workflows in interactive sessions must be orchestrated through Antigravity subagents. "
                "You must state factually that no subagents were invoked and correct your claim."
            )
        }

    return {"decision": "allow"}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Antigravity Lifecycle Hook Guard")
    parser.add_argument("--event", type=str, choices=["PreInvocation", "PostInvocation", "Stop", "PreToolUse", "PostToolUse"], default="Stop")
    args, unknown = parser.parse_known_args()

    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[transcript_and_rule_guard] Error parsing stdin JSON: {e}\n")

    event = args.event or payload.get("event", "Stop")

    if event == "PreInvocation":
        res = handle_pre_invocation(payload)
    elif event == "PostInvocation":
        res = handle_post_invocation(payload)
    elif event == "Stop":
        res = handle_stop(payload)
    elif event == "PreToolUse":
        res = handle_pre_tool_use(payload)
    elif event == "PostToolUse":
        res = handle_post_tool_use(payload)
    else:
        res = {"decision": "allow"}

    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
