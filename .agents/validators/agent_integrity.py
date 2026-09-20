#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validators/agent_integrity.py — Automated Agent Integrity & Antigravity Compatibility Validator

Validates all agents in .agents/agents/ against authoritative Antigravity 2.0+ specifications:
1.  file_location: Discovered at .agents/agents/<name>/agent.md or <name>.md, folder matches name.
2.  yaml_validity: Valid YAML frontmatter between '---' markers.
3.  required_name: Lowercase ASCII kebab-case name present.
4.  required_description: Non-empty, informative description present.
5.  unique_name: Zero duplicate names across discovered agents.
6.  discoverability: Canonical files exist, readable, and non-empty.
7.  valid_tool_names: All tools match canonical Antigravity tool whitelist.
8.  valid_skill_references: All referenced skills resolve to on-disk SKILL.md or built-ins.
9.  valid_mcp_references: MCP servers resolve to configured servers.
10. no_circular_dependency: Directed delegation graph (agents: [...]) is a valid DAG.
11. no_duplicate_canonical_agent: Symlinks resolve cleanly to their canonical targets.
12. correct_mainAgent_subagent_semantics: Any agent referenced in delegation must have subagent: true.
13. no_unsupported_policies: Rejection of commandExecutionPolicy / command_execution_policy in frontmatter.
"""

import os
import sys
import re
import json
import argparse
from typing import Dict, Any, List, Set, Optional, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.agents.capability_policy import (
    load_capability_policy,
    get_all_policy_agents,
    validate_agent_against_policy,
    validate_policy_schema,
    classify_execution_capabilities,
    DEFAULT_POLICY_PATH,
)
from scripts.orchestrator_invariants import (
    FORBIDDEN_ORCHESTRATOR_TOOLS,
    REQUIRED_ORCHESTRATOR_TOOLS,
)

AGENTS_DIR = os.path.join(ROOT_DIR, ".agents", "agents")
SKILLS_DIR = os.path.join(ROOT_DIR, ".agents", "skills")

# Canonical Antigravity Tool Whitelist
CANONICAL_ANTIGRAVITY_TOOLS: Set[str] = {
    # Filesystem
    "view_file",
    "write_to_file",
    "replace_file_content",
    "list_dir",
    "grep_search",
    "find_by_name",
    # Execution & Process
    "run_command",
    "manage_task",
    "schedule",
    # Subagent & Orchestration
    "invoke_subagent",
    "manage_subagents",
    "send_message",
    "define_subagent",
    # Interaction & Web
    "ask_question",
    "read_url_content",
    "search_web",
    "generate_image",
    # MCP Tools
    "call_mcp_tool",
    "list_resources",
    "read_resource",
}

# Built-in Antigravity Skills mounted by default
BUILTIN_ANTIGRAVITY_SKILLS: Set[str] = {
    "agy-customizations",
    "antigravity_guide",
    "generative_ui",
    "migrate-workflows",
    "google-antigravity-sdk",
}

# Known Built-in or Configured MCP Servers
KNOWN_MCP_SERVERS: Set[str] = {
    "codebase-memory-mcp",
    "github",
    "posthog",
    "postman",
}


def parse_yaml_frontmatter(content: str) -> Tuple[Optional[Dict[str, Any]], Optional[str], Optional[str]]:
    """
    Parses YAML frontmatter between '---' fences.
    Returns (frontmatter_dict, raw_body, error_message).
    """
    if not content.startswith("---"):
        return None, None, "File does not start with YAML frontmatter marker '---'"

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, None, "Malformed frontmatter: missing closing '---' marker"

    raw_yaml = parts[1]
    body = parts[2]

    # Minimal zero-dependency YAML parser fallback if PyYAML is not installed
    try:
        import yaml
        try:
            fm = yaml.safe_load(raw_yaml)
            if not isinstance(fm, dict):
                return None, None, "Frontmatter does not evaluate to a YAML mapping (dict)"
            return fm, body, None
        except Exception as e:
            return None, None, f"YAML parsing error: {e}"
    except ImportError:
        # Fallback simple parser for essential key-value pairs
        fm = {}
        current_list_key = None
        for line in raw_yaml.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue
            if line_str.startswith("- ") and current_list_key:
                val = line_str[2:].strip().strip("\"'")
                fm.setdefault(current_list_key, []).append(val)
                continue
            if ":" in line_str:
                k, v = line_str.split(":", 1)
                k = k.strip()
                v = v.strip()
                if not v:
                    current_list_key = k
                    fm[k] = []
                else:
                    current_list_key = None
                    if v.lower() == "true":
                        fm[k] = True
                    elif v.lower() == "false":
                        fm[k] = False
                    elif v.isdigit():
                        fm[k] = int(v)
                    else:
                        fm[k] = v.strip("\"'")
        return fm, body, None


def get_available_skills(skills_dir: str = SKILLS_DIR) -> Set[str]:
    """Returns set of all valid skill identifiers available to agents."""
    skills = set(BUILTIN_ANTIGRAVITY_SKILLS)
    if os.path.isdir(skills_dir):
        for entry in os.listdir(skills_dir):
            entry_path = os.path.join(skills_dir, entry)
            if os.path.isdir(entry_path) and os.path.isfile(os.path.join(entry_path, "SKILL.md")):
                skills.add(entry)
    return skills


def detect_cycles_in_delegation(graph: Dict[str, List[str]]) -> Optional[List[str]]:
    """
    Detects circular dependencies in the subagent delegation graph.
    Returns cycle path as list if found, else None.
    """
    visited: Set[str] = set()
    rec_stack: List[str] = []

    def dfs(node: str) -> Optional[List[str]]:
        visited.add(node)
        rec_stack.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                cycle = dfs(neighbor)
                if cycle:
                    return cycle
            elif neighbor in rec_stack:
                cycle_start = rec_stack.index(neighbor)
                return rec_stack[cycle_start:] + [neighbor]
        rec_stack.pop()
        return None

    for node in sorted(graph.keys()):
        if node not in visited:
            cycle = dfs(node)
            if cycle:
                return cycle
    return None


class AgentIntegrityValidator:
    """Master validation engine for AcademicSuite Antigravity Agent Specifications."""

    def __init__(
        self,
        agents_dir: str = AGENTS_DIR,
        skills_dir: str = SKILLS_DIR,
        policy_path: Optional[str] = None,
        enforce_capability_policy: Optional[bool] = None,
    ):
        self.agents_dir = agents_dir
        self.skills_dir = skills_dir
        self.policy_path = policy_path
        if enforce_capability_policy is not None:
            self.enforce_capability_policy = enforce_capability_policy
        else:
            self.enforce_capability_policy = (
                policy_path is not None or os.path.abspath(agents_dir) == os.path.abspath(AGENTS_DIR)
            )
        self.available_skills = get_available_skills(skills_dir)
        self.canonical_agents: Dict[str, Dict[str, Any]] = {}
        self.delegation_graph: Dict[str, List[str]] = {}
        self.issues: List[Dict[str, Any]] = []
        self.policy: Optional[Dict[str, Any]] = None

    def _get_policy(self) -> Optional[Dict[str, Any]]:
        """Safely loads or returns cached capability policy."""
        if self.policy is None and load_capability_policy is not None:
            try:
                self.policy = load_capability_policy(self.policy_path)
            except Exception:
                self.policy = None
        return self.policy

    def run_validation(self) -> Dict[str, Any]:
        """
        Executes full validation across all discovered agents.
        Returns validation summary dictionary.
        """
        self.issues.clear()
        self.canonical_agents.clear()
        self.delegation_graph.clear()

        if not os.path.isdir(self.agents_dir):
            return {
                "overall_verdict": "FAIL",
                "agents_validated": 0,
                "total_issues": 1,
                "issues": [{"severity": "FATAL", "check": "file_location", "message": f"Agents directory does not exist: {self.agents_dir}"}],
            }

        # Step 1: Discover all directory-based canonical agents
        entries = sorted(os.listdir(self.agents_dir))
        for entry in entries:
            entry_path = os.path.join(self.agents_dir, entry)
            if os.path.isdir(entry_path):
                self._validate_agent_directory(entry, entry_path)

        # Step 2: Validate symlinks and check for duplicate canonical agents
        for entry in entries:
            entry_path = os.path.join(self.agents_dir, entry)
            if os.path.islink(entry_path):
                self._validate_agent_symlink(entry, entry_path)

        # Step 3: Graph-level validation (cycles & delegation semantics)
        self._validate_delegation_graph()

        # Step 4: Capability boundaries validation (Phase 13)
        self._validate_capability_boundaries()

        # Step 5: Machine-checkable capability policy validation (Phase 12 SSOT)
        if self.enforce_capability_policy:
            self._validate_capability_policy()

        # Step 6: Overall verdict calculation
        fatal_count = sum(1 for i in self.issues if i.get("severity") in ("ERROR", "FATAL"))
        warning_count = sum(1 for i in self.issues if i.get("severity") == "WARNING")

        overall_verdict = "PASS" if fatal_count == 0 else "FAIL"

        return {
            "overall_verdict": overall_verdict,
            "agents_validated": len(self.canonical_agents),
            "total_issues": len(self.issues),
            "errors": fatal_count,
            "warnings": warning_count,
            "issues": self.issues,
            "canonical_agents": sorted(list(self.canonical_agents.keys())),
        }

    def _add_issue(self, agent_name: str, check_name: str, message: str, severity: str = "ERROR"):
        self.issues.append({
            "agent": agent_name,
            "check": check_name,
            "severity": severity,
            "message": message,
        })

    def _validate_agent_directory(self, folder_name: str, folder_path: str):
        agent_file = os.path.join(folder_path, "agent.md")
        if not os.path.isfile(agent_file):
            self._add_issue(folder_name, "discoverability", f"Missing canonical agent.md in {folder_path}")
            return

        # Read content
        try:
            with open(agent_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self._add_issue(folder_name, "discoverability", f"Cannot read agent.md: {e}")
            return

        if len(content.strip()) < 20:
            self._add_issue(folder_name, "discoverability", f"agent.md is empty or too short ({len(content)} bytes)")
            return

        fm, body, parse_err = parse_yaml_frontmatter(content)
        if parse_err:
            self._add_issue(folder_name, "yaml_validity", f"Frontmatter parse error: {parse_err}")
            return

        # Check unsupported frontmatter policies
        if "commandExecutionPolicy" in fm or "command_execution_policy" in fm:
            self._add_issue(
                folder_name,
                "no_unsupported_policies",
                "Unsupported field 'commandExecutionPolicy' detected. Causes Antigravity IDE discovery to silently drop agent."
            )

        # Check required name
        name = fm.get("name")
        if not name:
            self._add_issue(folder_name, "required_name", "Missing required 'name' field in frontmatter")
            return

        if not isinstance(name, str) or not re.match(r"^[a-z0-9_-]+$", name):
            self._add_issue(folder_name, "required_name", f"Invalid name format '{name}'. Must be lowercase kebab-case.")

        if name != folder_name:
            self._add_issue(folder_name, "file_location", f"Name '{name}' in frontmatter does not match directory name '{folder_name}'")

        if name in self.canonical_agents:
            self._add_issue(name, "unique_name", f"Duplicate canonical agent name '{name}' detected")
        else:
            self.canonical_agents[name] = fm

        # Check required description
        desc = fm.get("description")
        if not desc:
            self._add_issue(name, "required_description", "Missing required 'description' field in frontmatter")
        elif not isinstance(desc, str) or len(desc.strip()) < 10:
            self._add_issue(name, "required_description", f"Description is too short or invalid: '{desc}'")

        # Check tools whitelist
        tools = fm.get("tools", [])
        if not isinstance(tools, list):
            self._add_issue(name, "valid_tool_names", "Field 'tools' must be a list of strings")
        else:
            for tool in tools:
                if tool not in CANONICAL_ANTIGRAVITY_TOOLS:
                    self._add_issue(name, "valid_tool_names", f"Invalid or misspelled tool name: '{tool}'. Causes subagent execution errors.")

        # Check skill references
        skills = fm.get("skills", [])
        if not isinstance(skills, list):
            self._add_issue(name, "valid_skill_references", "Field 'skills' must be a list of strings")
        else:
            for skill in skills:
                if skill not in self.available_skills:
                    self._add_issue(name, "valid_skill_references", f"Referenced skill '{skill}' does not exist in .agents/skills/ or built-ins")

        # Check MCP references
        mcp_servers = fm.get("mcpServers", [])
        if not isinstance(mcp_servers, list):
            self._add_issue(name, "valid_mcp_references", "Field 'mcpServers' must be a list of strings")
        else:
            for srv in mcp_servers:
                if srv not in KNOWN_MCP_SERVERS:
                    self._add_issue(name, "valid_mcp_references", f"Unknown MCP server '{srv}'", severity="WARNING")

        # Record delegation graph
        delegated_agents = fm.get("agents", [])
        if isinstance(delegated_agents, list):
            self.delegation_graph[name] = list(delegated_agents)

    def _validate_agent_symlink(self, symlink_name: str, symlink_path: str):
        """Verifies that symlinks point directly to the matching canonical agent.md."""
        target = os.readlink(symlink_path)
        base_name = symlink_name[:-3] if symlink_name.endswith(".md") else symlink_name
        expected_target = f"{base_name}/agent.md"

        if target != expected_target:
            self._add_issue(
                base_name,
                "no_duplicate_canonical_agent",
                f"Symlink '{symlink_name}' points to '{target}' instead of expected '{expected_target}'"
            )
        if not os.path.exists(symlink_path):
            self._add_issue(base_name, "discoverability", f"Broken symlink '{symlink_path}' -> '{target}'")

    def _validate_delegation_graph(self):
        """Validates acyclicity and mainAgent/subagent semantics across the delegation network."""
        # 1. Circular dependency check
        cycle = detect_cycles_in_delegation(self.delegation_graph)
        if cycle:
            cycle_str = " -> ".join(cycle)
            self._add_issue(cycle[0], "no_circular_dependency", f"Circular delegation detected: {cycle_str}")

        # 2. MainAgent / Subagent semantics check
        for parent_name, children in self.delegation_graph.items():
            for child_name in children:
                if child_name not in self.canonical_agents:
                    self._add_issue(
                        parent_name,
                        "correct_mainAgent_subagent_semantics",
                        f"Parent '{parent_name}' delegates to unknown agent '{child_name}'"
                    )
                    continue

                child_fm = self.canonical_agents[child_name]
                child_is_subagent = child_fm.get("subagent", True)
                if child_is_subagent is False:
                    self._add_issue(
                        child_name,
                        "correct_mainAgent_subagent_semantics",
                        f"Agent '{child_name}' is referenced in '{parent_name}' delegation list but has 'subagent: false'. Antigravity will block invoke_subagent."
                    )

        # 3. Canonical MainAgent entry point check (Phase 11)
        # When academic-orchestrator is present, it must be the sole mainAgent (mainAgent=True, subagent=True).
        # All other agents must have mainAgent=False and subagent=True.
        if "academic-orchestrator" in self.canonical_agents:
            orch_fm = self.canonical_agents["academic-orchestrator"]
            if not orch_fm.get("mainAgent"):
                self._add_issue(
                    "academic-orchestrator",
                    "canonical_mainAgent_entry_point",
                    "academic-orchestrator must have 'mainAgent: true' as the canonical production entry point."
                )
            if not orch_fm.get("subagent"):
                self._add_issue(
                    "academic-orchestrator",
                    "canonical_mainAgent_entry_point",
                    "academic-orchestrator must have 'subagent: true'."
                )

            for name, fm in self.canonical_agents.items():
                if name != "academic-orchestrator" and fm.get("mainAgent") is True:
                    self._add_issue(
                        name,
                        "canonical_mainAgent_entry_point",
                        f"Specialist agent '{name}' has 'mainAgent: true'. In production AcademicSuite, "
                        f"only 'academic-orchestrator' may hold 'mainAgent: true'. All specialists must have 'mainAgent: false'."
                    )

    def _validate_capability_boundaries(self):
        """
        Phase 13: Capability Boundaries Validator.
        Enforces least-privilege operational constraints:
        1. Academic-Orchestrator: NO run_command, NO write_to_file, NO edit_file, NO replace_file_content, YES invoke_subagent.
        2. Execution Workers: run_command allowed and required.
        3. Read-Only Agents: no write tools (write_to_file, replace_file_content, edit_file), no execution (run_command).
        4. Auditors: no execution (run_command) unless explicitly justified in capability policy.
        """
        policy = self._get_policy()

        known_execution_workers = {
            "data-agent", "data-curator", "statistics-agent", "psychometric-expert",
            "longitudinal-modmed-expert", "qualitative-analyst", "meta-analyst",
            "evaluation-agent", "validation-agent", "statistical-auditor",
            "research-agent", "literature-expert", "academic-writer",
        }
        known_read_only_agents = {
            "academic-orchestrator", "behavior-analyst", "trajectory-analyzer",
        }
        known_auditors = {
            "results-auditor", "evidence-auditor", "academic-challenger",
            "final-judge", "journal-strategist", "statistical-auditor",
        }

        # 1. Academic-Orchestrator Checks: Permanent Architectural Invariants (Phase 26)
        if "academic-orchestrator" in self.canonical_agents:
            orch_fm = self.canonical_agents["academic-orchestrator"]
            orch_tools = set(orch_fm.get("tools", []))

            # Law 1: Orchestrator Non-Execution Invariant
            for forbidden_tool in sorted(FORBIDDEN_ORCHESTRATOR_TOOLS):
                if forbidden_tool in orch_tools:
                    self._add_issue(
                        "academic-orchestrator",
                        "orchestrator_non_execution_invariant",
                        f"[Orchestrator Non-Execution Invariant] academic-orchestrator MUST NOT possess '{forbidden_tool}'."
                    )

            # Law 2: Delegation Availability Invariant
            for required_tool in sorted(REQUIRED_ORCHESTRATOR_TOOLS):
                if required_tool not in orch_tools:
                    self._add_issue(
                        "academic-orchestrator",
                        "delegation_availability_invariant",
                        f"[Delegation Availability Invariant] academic-orchestrator MUST possess '{required_tool}' to delegate execution to specialist subagents."
                    )

        # 2. Execution Workers: run_command allowed and required
        for agent_name, fm in self.canonical_agents.items():
            is_worker = False
            if policy and agent_name in policy.get("agents", {}):
                spec = policy["agents"][agent_name]
                if spec.get("role") in ("execution_worker", "writing_worker") or spec.get("can_execute_code"):
                    is_worker = True
            elif agent_name in known_execution_workers:
                is_worker = True

            if is_worker:
                tools = set(fm.get("tools", []))
                if "run_command" not in tools:
                    self._add_issue(
                        agent_name,
                        "execution_workers_capabilities",
                        f"Execution worker '{agent_name}' must declare 'run_command' to perform deterministic computation."
                    )

        # 3. Read-Only Agents: no write, no execution
        for agent_name, fm in self.canonical_agents.items():
            is_read_only = False
            if policy and agent_name in policy.get("agents", {}):
                spec = policy["agents"][agent_name]
                if not spec.get("can_write_files", True) and not spec.get("can_execute_code", True):
                    is_read_only = True
            elif agent_name in known_read_only_agents:
                is_read_only = True

            if is_read_only:
                tools = set(fm.get("tools", []))
                write_tools = {"write_to_file", "replace_file_content", "edit_file"}
                illegal_write = write_tools & tools
                if illegal_write:
                    self._add_issue(
                        agent_name,
                        "read_only_agents_capabilities",
                        f"Read-only agent '{agent_name}' must NOT declare file writing tools: {sorted(illegal_write)}"
                    )
                if "run_command" in tools:
                    self._add_issue(
                        agent_name,
                        "read_only_agents_capabilities",
                        f"Read-only agent '{agent_name}' must NOT declare 'run_command'. Execution is forbidden."
                    )

        # 4. Auditors: no execution unless explicitly justified
        for agent_name, fm in self.canonical_agents.items():
            is_auditor = False
            if policy and agent_name in policy.get("agents", {}):
                spec = policy["agents"][agent_name]
                if spec.get("role") in ("auditor", "critic") or "Critic" in spec.get("tier", "") or agent_name.endswith(("-auditor", "-challenger")) or agent_name == "final-judge":
                    is_auditor = True
            elif agent_name in known_auditors or agent_name.endswith(("-auditor", "-challenger")) or agent_name == "final-judge":
                is_auditor = True

            if is_auditor:
                tools = set(fm.get("tools", []))
                if "run_command" in tools:
                    has_justification = False
                    if policy and agent_name in policy.get("agents", {}):
                        spec = policy["agents"][agent_name]
                        if spec.get("execution_justification"):
                            has_justification = True

                    if not has_justification:
                        self._add_issue(
                            agent_name,
                            "auditors_capabilities",
                            f"Auditor '{agent_name}' must NOT declare 'run_command' unless explicitly justified in capability policy."
                        )

    def _validate_capability_policy(self):
        """Validates canonical agents against contracts/agents/agent_capabilities.yaml SSOT."""
        try:
            policy = load_capability_policy(self.policy_path)
        except Exception as e:
            self._add_issue(
                "workspace",
                "capability_policy",
                f"Failed to load agent capability policy: {e}",
                severity="FATAL"
            )
            return

        # 1. Validate policy internal schema
        schema_issues = validate_policy_schema(policy)
        for issue in schema_issues:
            self._add_issue("capability_policy", "policy_schema", issue, severity="FATAL")

        # 2. Check coverage: all policy agents exist on disk & all disk agents in policy
        policy_agents = set(get_all_policy_agents(policy))
        canonical_names = set(self.canonical_agents.keys())

        for missing in sorted(policy_agents - canonical_names):
            self._add_issue(
                missing,
                "capability_policy_coverage",
                f"Agent '{missing}' is declared in capability policy SSOT but missing from canonical agents on disk"
            )

        for unreg in sorted(canonical_names - policy_agents):
            self._add_issue(
                unreg,
                "capability_policy_coverage",
                f"Agent '{unreg}' exists on disk but is not registered in capability policy SSOT"
            )

        # 3. Validate each canonical agent against its policy specification
        for name, fm in sorted(self.canonical_agents.items()):
            if name in policy_agents:
                agent_issues = validate_agent_against_policy(name, fm, policy)
                for issue in agent_issues:
                    self._add_issue(name, "capability_policy", issue)


class AgentCapabilityValidator(AgentIntegrityValidator):
    """
    Phase 13/18: Specialized Agent Capability Validator.
    Inherits all Antigravity integrity and discovery checks from AgentIntegrityValidator
    and enforces the full suite of least-privilege capability boundaries, explicitly
    distinguishing DIRECT EXECUTION from INDIRECT EXECUTION.
    """
    def __init__(
        self,
        agents_dir: str = AGENTS_DIR,
        skills_dir: str = SKILLS_DIR,
        policy_path: Optional[str] = None,
        enforce_capability_policy: bool = True,
    ):
        super().__init__(
            agents_dir=agents_dir,
            skills_dir=skills_dir,
            policy_path=policy_path,
            enforce_capability_policy=enforce_capability_policy,
        )

    def run_validation(self) -> Dict[str, Any]:
        result = super().run_validation()
        policy = self._get_policy()

        taxonomy = {
            "direct_executors": [],
            "non_executors": [],
            "indirect_vectors_status": {
                "call_mcp_tool": "BLOCKED for non-executors (mechanically guarded in hooks)",
                "define_subagent": "BLOCKED for orchestrator and non-executors (mechanically guarded in hooks)",
                "manage_task": "BLOCKED send_input for non-executors (mechanically guarded in hooks)",
                "schedule": "BLOCKED for orchestrator and non-executors (mechanically guarded in hooks)",
                "batch_runner_skills": "BLOCKED for non-executors",
            },
        }

        for name, fm in sorted(self.canonical_agents.items()):
            classification = classify_execution_capabilities(name, fm, policy)
            if classification["can_execute_code"]:
                taxonomy["direct_executors"].append({
                    "name": name,
                    "scope": classification["execution_scope"],
                    "direct_tools": classification["direct_execution"],
                })
            else:
                agent_spec = policy.get("agents", {}).get(name, {}) if policy else {}
                taxonomy["non_executors"].append({
                    "name": name,
                    "role": agent_spec.get("role", "unknown"),
                    "direct_tools": classification["direct_execution"],
                    "indirect_tools": classification["indirect_tools"],
                    "indirect_skills": classification["indirect_skills"],
                })

        result["execution_taxonomy"] = taxonomy
        return result


def main():
    parser = argparse.ArgumentParser(description="Antigravity Agent Integrity & Discovery Validator")
    parser.add_argument("--agents-dir", default=AGENTS_DIR, help="Path to .agents/agents directory")
    parser.add_argument("--skills-dir", default=SKILLS_DIR, help="Path to .agents/skills directory")
    parser.add_argument("--policy-path", default=None, help="Path to agent capability policy YAML")
    parser.add_argument("--no-policy", action="store_true", help="Disable capability policy enforcement")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print detailed report")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    enforce_policy = False if args.no_policy else None
    validator = AgentIntegrityValidator(
        agents_dir=args.agents_dir,
        skills_dir=args.skills_dir,
        policy_path=args.policy_path,
        enforce_capability_policy=enforce_policy,
    )
    result = validator.run_validation()

    if args.json:
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["overall_verdict"] == "PASS" else 1)

    print("=" * 70)
    print("🔍 Antigravity Agent Integrity & Compatibility Validator")
    print("=" * 70)
    print(f"Directory:        {args.agents_dir}")
    print(f"Agents Scanned:   {result['agents_validated']}")
    print(f"Errors:           {result['errors']}")
    print(f"Warnings:         {result['warnings']}")
    print(f"Overall Verdict:  {result['overall_verdict']}")
    print("=" * 70)

    if result["issues"]:
        print("\nIssues Identified:")
        for issue in result["issues"]:
            prefix = "❌" if issue["severity"] in ("ERROR", "FATAL") else "⚠️"
            print(f"  {prefix} [{issue['severity']}] {issue['agent']}: ({issue['check']}) {issue['message']}")
        print()

    if result["overall_verdict"] == "PASS":
        print("✅ ALL AGENTS VALIDATED: 100% Antigravity discovery and tool contracts satisfied.")
        sys.exit(0)
    else:
        print("❌ INTEGRITY VALIDATION FAILED: See errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
