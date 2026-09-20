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

    def __init__(self, agents_dir: str = AGENTS_DIR, skills_dir: str = SKILLS_DIR):
        self.agents_dir = agents_dir
        self.skills_dir = skills_dir
        self.available_skills = get_available_skills(skills_dir)
        self.canonical_agents: Dict[str, Dict[str, Any]] = {}
        self.delegation_graph: Dict[str, List[str]] = {}
        self.issues: List[Dict[str, Any]] = []

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

        # Step 4: Overall verdict calculation
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


def main():
    parser = argparse.ArgumentParser(description="Antigravity Agent Integrity & Discovery Validator")
    parser.add_argument("--agents-dir", default=AGENTS_DIR, help="Path to .agents/agents directory")
    parser.add_argument("--skills-dir", default=SKILLS_DIR, help="Path to .agents/skills directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print detailed report")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    validator = AgentIntegrityValidator(agents_dir=args.agents_dir, skills_dir=args.skills_dir)
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
