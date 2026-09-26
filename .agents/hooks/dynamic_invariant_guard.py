#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/dynamic_invariant_guard.py — Dynamic Mechanical Invariant Guard Engine

Constitutional Invariant (Directives 18, 19, 21, 22):
- Directive 19: Skill instructs, Hook enforces.
- Directive 21: Dual-Track Ingestion — lessons graduate into mechanical hook rules.
- Directive 22: Fail-Closed Mechanical Validation Gate.

Evaluates dynamically registered mechanical invariant rules from
`.agents/hooks/rules/enforced_invariants.json` during PreToolUse and Stop lifecycle events.
Guarantees that learned invariants are mechanically enforced across subagents,
preventing behavioral drift and defect recurrence.
"""

import os
import sys
import re
import json
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HOOKS_DIR, "..", ".."))
RULES_DIR = os.path.join(HOOKS_DIR, "rules")
INVARIANTS_FILE = os.path.join(RULES_DIR, "enforced_invariants.json")

for p in (ROOT_DIR, os.path.join(ROOT_DIR, ".agents")):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from contracts.hook_identity_contract import is_main_agent_developer
except ImportError:
    try:
        from .contracts.hook_identity_contract import is_main_agent_developer
    except ImportError:
        def is_main_agent_developer(payload):
            caller = (payload.get("agentName") or payload.get("caller") or "").lower().strip()
            return caller in ("main", "default", "antigravity", "developer")


class DynamicInvariantGuard:
    """Deterministic evaluation engine for learned mechanical invariant rules."""

    _cached_mtime: float = 0.0
    _cached_invariants: Dict[str, Any] = {}

    @classmethod
    def load_invariants(cls, base_dir: Optional[str] = None) -> Dict[str, Any]:
        """Loads and caches active mechanical invariants from disk."""
        target_path = INVARIANTS_FILE
        if base_dir:
            cand = os.path.join(base_dir, ".agents", "hooks", "rules", "enforced_invariants.json")
            if os.path.isfile(cand):
                target_path = cand

        if not os.path.isfile(target_path):
            return {}

        try:
            mtime = os.path.getmtime(target_path)
            if mtime != cls._cached_mtime:
                with open(target_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cls._cached_invariants = data.get("invariants", {})
                cls._cached_mtime = mtime
            return cls._cached_invariants
        except Exception as e:
            sys.stderr.write(f"[dynamic_invariant_guard] Error loading invariants: {e}\n")
            return cls._cached_invariants

    @classmethod
    def register_invariant(
        cls,
        item_id: str,
        category: str,
        statement: str,
        target_agents: Optional[List[str]] = None,
        target_skills: Optional[List[str]] = None,
        event: str = "PreToolUse",
        tool_match: str = "write_to_file|replace_file_content|patch|edit_file",
        file_pattern: str = ".*\\.(?:md|docx|txt)",
        check_type: str = "regex_ban",
        pattern: str = "",
        violation_message: str = "",
        remedy: str = "",
        base_dir: Optional[str] = None
    ) -> bool:
        """Compiles and registers an active mechanical invariant rule on disk."""
        target_path = INVARIANTS_FILE
        if base_dir:
            target_path = os.path.join(base_dir, ".agents", "hooks", "rules", "enforced_invariants.json")

        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        raw_data = {"contract_version": "1.0.0", "updated_at": "", "invariants": {}}
        if os.path.isfile(target_path):
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
            except Exception:
                pass

        invariants = raw_data.get("invariants", {})
        rule_entry = {
            "item_id": item_id,
            "category": category,
            "statement": statement,
            "target_agents": target_agents or ["*"],
            "target_skills": target_skills or [],
            "event": event,
            "tool_match": tool_match,
            "file_pattern": file_pattern,
            "check_type": check_type,
            "pattern": pattern,
            "violation_message": violation_message or statement,
            "remedy": remedy,
            "enabled": True,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        invariants[item_id] = rule_entry
        raw_data["invariants"] = invariants
        raw_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        try:
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(raw_data, f, indent=2, ensure_ascii=False)
            cls._cached_mtime = os.path.getmtime(target_path)
            cls._cached_invariants = invariants
            return True
        except Exception as e:
            sys.stderr.write(f"[dynamic_invariant_guard] Error writing invariant {item_id}: {e}\n")
            return False

    @staticmethod
    def _extract_content(args: Dict[str, Any]) -> str:
        """Extracts text content being modified across multiple tool signatures."""
        content = args.get("CodeContent") or args.get("ReplacementContent") or args.get("content") or ""
        if not content and "TargetContent" in args:
            content = str(args.get("TargetContent", ""))
        return str(content)

    @staticmethod
    def _extract_target_file(args: Dict[str, Any]) -> str:
        return str(args.get("TargetFile") or args.get("AbsolutePath") or args.get("file_path") or args.get("path") or "")

    @classmethod
    def evaluate_pre_tool_use(cls, caller: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates active mechanical rules during PreToolUse."""
        if is_main_agent_developer(payload) or payload.get("track") == 1:
            return {"decision": "allow"}

        tool_call = payload.get("toolCall", {})
        tool_name = (tool_call.get("name") or payload.get("tool_name") or "").strip().lower()
        args = tool_call.get("args") or payload.get("args") or {}
        caller_clean = (caller or payload.get("agentName") or payload.get("agent") or "").strip().lower()

        target_file = cls._extract_target_file(args)
        content = cls._extract_content(args)

        base_dir = payload.get("base_dir") or (payload.get("workspacePaths", [None])[0] if payload.get("workspacePaths") else None)
        if not base_dir and target_file:
            cur = os.path.dirname(os.path.abspath(target_file))
            while cur and cur != "/":
                if os.path.isdir(os.path.join(cur, ".agents")):
                    base_dir = cur
                    break
                cur = os.path.dirname(cur)

        invariants = cls.load_invariants(base_dir=base_dir)
        if not invariants:
            return {"decision": "allow"}

        for rule_id, rule in invariants.items():
            if not rule.get("enabled", True):
                continue

            event = rule.get("event", "PreToolUse")
            if event not in ("PreToolUse", "Both", "*"):
                continue

            # Agent target filtering
            target_agents = [a.lower().strip() for a in rule.get("target_agents", [])]
            if "*" not in target_agents and caller_clean and caller_clean not in target_agents:
                continue

            # Tool name matching
            tool_match = rule.get("tool_match", "")
            if tool_match and not re.search(tool_match, tool_name, re.IGNORECASE):
                continue

            # File pattern matching
            file_pattern = rule.get("file_pattern", "")
            if file_pattern and target_file and not re.search(file_pattern, target_file, re.IGNORECASE):
                continue

            # Check evaluation
            check_type = rule.get("check_type", "regex_ban")
            pattern = rule.get("pattern", "")
            v_msg = rule.get("violation_message") or rule.get("statement") or "Constitutional invariant violated."
            remedy = rule.get("remedy", "")

            if check_type == "regex_ban" and pattern and content:
                try:
                    if re.search(pattern, content, re.MULTILINE):
                        return {
                            "decision": "deny",
                            "reason": (
                                f"CONSTITUTIONAL VIOLATION (Learned Invariant {rule_id}):\n"
                                f"{v_msg}\n"
                                f"Remedy: {remedy}" if remedy else f"CONSTITUTIONAL VIOLATION ({rule_id}): {v_msg}"
                            )
                        }
                except Exception as e_rx:
                    sys.stderr.write(f"[dynamic_invariant_guard] Regex evaluation error ({rule_id}): {e_rx}\n")

            elif check_type == "substring_ban" and pattern and content:
                if pattern in content:
                    return {
                        "decision": "deny",
                        "reason": (
                            f"CONSTITUTIONAL VIOLATION (Learned Invariant {rule_id}):\n"
                            f"{v_msg}\n"
                            f"Remedy: {remedy}" if remedy else f"CONSTITUTIONAL VIOLATION ({rule_id}): {v_msg}"
                        )
                    }

            elif check_type == "tool_ban":
                return {
                    "decision": "deny",
                    "reason": f"CONSTITUTIONAL VIOLATION ({rule_id}): Tool '{tool_name}' is forbidden for agent '{caller_clean}'. {v_msg}"
                }

        return {"decision": "allow"}

    @classmethod
    def evaluate_stop(cls, caller: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates active mechanical rules on generated deliverables during Stop."""
        if is_main_agent_developer(payload) or payload.get("track") == 1:
            return {"decision": "allow"}

        caller_clean = (caller or payload.get("agentName") or payload.get("agent") or "").strip().lower()
        invariants = cls.load_invariants()
        if not invariants:
            return {"decision": "allow"}

        workspaces = payload.get("workspacePaths", [ROOT_DIR])
        base_ws = workspaces[0] if workspaces and os.path.isdir(workspaces[0]) else ROOT_DIR

        # Identify candidate deliverables in workspace
        deliverables_dir = os.path.join(base_ws, "03_deliverables")
        if not os.path.isdir(deliverables_dir):
            return {"decision": "allow"}

        for rule_id, rule in invariants.items():
            if not rule.get("enabled", True):
                continue

            event = rule.get("event", "Stop")
            if event not in ("Stop", "Both", "*"):
                continue

            target_agents = [a.lower().strip() for a in rule.get("target_agents", [])]
            if "*" not in target_agents and caller_clean and caller_clean not in target_agents:
                continue

            file_pattern = rule.get("file_pattern", "")
            check_type = rule.get("check_type", "")
            pattern = rule.get("pattern", "")
            v_msg = rule.get("violation_message") or rule.get("statement") or "Mechanical integrity defect detected."
            remedy = rule.get("remedy", "")

            # Scan files matching file_pattern in 03_deliverables
            for root_p, _, files in os.walk(deliverables_dir):
                for fname in files:
                    full_p = os.path.join(root_p, fname)
                    if file_pattern and not re.search(file_pattern, full_p, re.IGNORECASE):
                        continue

                    # DOM check for OpenXML tables
                    if check_type == "openxml_dom_ban" and full_p.lower().endswith(".docx"):
                        try:
                            with zipfile.ZipFile(full_p, "r") as zf:
                                if "word/document.xml" in zf.namelist():
                                    root_xml = ET.fromstring(zf.read("word/document.xml"))
                                    tbls = [e for e in root_xml.iter() if e.tag.endswith("}tbl") or e.tag == "tbl"]
                                    if tbls:
                                        return {
                                            "decision": "continue",
                                            "reason": (
                                                f"MECHANICAL INTEGRITY DEFECT (Learned Invariant {rule_id}):\n"
                                                f"File '{os.path.basename(full_p)}' contains {len(tbls)} prohibited Word table(s).\n"
                                                f"{v_msg}\n"
                                                f"Remedy: {remedy}"
                                            )
                                        }
                        except Exception:
                            pass

                    # Regex check on text deliverables
                    elif check_type in ("regex_ban", "markdown_table_ban") and full_p.lower().endswith((".md", ".txt")):
                        try:
                            with open(full_p, "r", encoding="utf-8") as f:
                                f_content = f.read()
                            if pattern and re.search(pattern, f_content, re.MULTILINE):
                                return {
                                    "decision": "continue",
                                    "reason": (
                                        f"MECHANICAL INTEGRITY DEFECT (Learned Invariant {rule_id}):\n"
                                        f"File '{os.path.basename(full_p)}' matches prohibited pattern '{pattern}'.\n"
                                        f"{v_msg}\n"
                                        f"Remedy: {remedy}"
                                    )
                                }
                        except Exception:
                            pass

        return {"decision": "allow"}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Dynamic Mechanical Invariant Guard CLI")
    parser.add_argument("--list", action="store_true", help="List all registered mechanical invariants")
    parser.add_argument("--agent", default="", help="Filter invariants by target agent")
    args = parser.parse_args()

    invariants = DynamicInvariantGuard.load_invariants()
    if args.list:
        print(f"Registered Invariants ({len(invariants)} total):")
        for k, v in invariants.items():
            if not args.agent or args.agent in v.get("target_agents", []):
                print(f"- [{k}] ({v.get('category')}): {v.get('statement')[:80]}")
                print(f"  Check: {v.get('check_type')} | Pattern: {v.get('pattern')} | Agents: {v.get('target_agents')}")


if __name__ == "__main__":
    main()
