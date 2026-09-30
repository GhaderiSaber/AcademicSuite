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
    from contracts.hook_identity_contract import is_main_agent_developer, is_learning_subagent, is_auditor_agent
except ImportError:
    try:
        from .contracts.hook_identity_contract import is_main_agent_developer, is_learning_subagent, is_auditor_agent
    except ImportError:
        def is_main_agent_developer(payload):
            caller = (payload.get("agentName") or payload.get("caller") or "").lower().strip()
            return caller in ("main", "default", "antigravity", "developer")

        def is_learning_subagent(caller):
            if not caller:
                return False
            c = str(caller).lower().strip()
            return any(k in c for k in ("behavior-analyst", "curriculum-builder", "evaluation-agent", "knowledge-curator", "skill-evolver", "trajectory-analyzer"))

        def is_auditor_agent(caller):
            if not caller:
                return False
            c = str(caller).lower().strip()
            return any(k in c for k in ("validation", "auditor", "challenger", "judge", "inspector"))



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

    SKILL_TO_AGENT: Dict[str, str] = {
        "chapter-4-writing": "academic-writer",
        "chapter-5-writing": "academic-writer",
        "persian-thesis-builder": "academic-writer",
        "persian-thesis-revision-assistant": "academic-writer",
        "academic-article-writer": "academic-writer",
        "apa-reporting": "academic-writer",
        "persian-discussion-builder": "academic-writer",
        "persian-literature-review-builder": "academic-writer",
        "persian-proposal-builder": "academic-writer",
        "statistical-data-analyst": "statistics-agent",
        "data-audit": "data-agent",
        "data-cleaning": "data-agent",
        "academic-reference-extractor": "academic-writer",
        "thesis-integrity-auditor": "validation-agent",
    }

    CANONICAL_RULE_TARGETS: Dict[str, List[str]] = {
        # Group 1: Manuscript & Document Authoring (Prose, Typography, Tables, OpenXML)
        "AP-2026-BOLD-TABLE-CAPTION-AND-UNJUSTIFIED-NARRATIVE": ["academic-writer"],
        "AP-2026-CHAPTER-BOUNDARY-VIOLATION": ["academic-writer"],
        "AP-2026-CHAPTER4-PREMATURE-INTERPRETATION-AND-HYPERBOLE": ["academic-writer"],
        "AP-2026-DRAFT-OBLITERATION-REPLACEMENT": ["academic-writer"],
        "AP-2026-DUAL-SAMPLE-OR-HARNESSED-TERMINOLOGY-LEAK": ["academic-writer"],
        "AP-2026-METADATA-LEAK-IN-TABLE-NOTES": ["academic-writer"],
        "AP-2026-OPENXML-NUMPR-LITERAL-PREFIX-HALLUCINATION": ["academic-writer"],
        "AP-2026-PHONETIC-BETA-AND-UNSPACED-FOOTNOTE": ["academic-writer"],
        "AP-2026-RAW-MARKDOWN-IN-DOCX-DUMP": ["academic-writer"],
        "AP-2026-SILENT-REGEX-DOCX-FAILURE": ["academic-writer"],
        "AP-2026-STUB-TABLE-INTRODUCTION": ["academic-writer"],
        "AP-2026-TABLE-VERTICAL-BORDER-PERSIAN-ZERO": ["academic-writer"],
        "AP-2026-WRITER-JSON-MUTATION": ["academic-writer"],
        "AP-2026-ZERO-TEMPLATE-DYNAMIC-NARRATION": ["academic-writer"],
        "CAN-20260929-PROP-REV-002": ["academic-writer"],
        "CAND-2026-APA-SINGLE-SAMPLE-INVARIANT": ["academic-writer"],
        "CAND-2026-CH4-DYNAMIC-NARRATION": ["academic-writer"],
        "CAND-2026-CH4-ZERO-INTERPRETATION": ["academic-writer"],
        "CAND-2026-DOCUMENT-CONSERVATION-IN-PLACE-REVISION": ["academic-writer"],
        "CAND-2026-DOCX-AST-PARSER-AND-CHAPTER4-FRAMING-001": ["academic-writer"],
        "CAND-2026-DOCX-AST-PARSER-AND-CHAPTER4-FRAMING-001-B": ["academic-writer"],
        "CAND-2026-EXHAUSTIVE-SUPERVISOR-REVISION-AUDIT": ["academic-writer"],
        "CAND-2026-GLOBAL-TABLE-DOCX-STANDARDS-001": ["academic-writer"],
        "CAND-2026-LANGUAGE-TRACK-AWARE-TYPOGRAPHY": ["academic-writer"],
        "CAND-2026-ONLYOFFICE-STRICT-RTL-TABLE-001": ["academic-writer"],
        "CAND-2026-SURGICAL-RUN-LEVEL-MUTATION": ["academic-writer"],
        "CAND-2026-TABLE-BORDER-PERSIAN-ZERO": ["academic-writer"],
        "CAND-20260930-BIDI-ALIGNMENT-AND-TBLPR-002": ["academic-writer"],
        "LSN-2026-APA7-TABLE-FORMATTING-INVARIANTS": ["academic-writer"],
        "LSN-2026-CHAPTER-5-PROSE-ONLY-INVARIANT-001": ["academic-writer"],
        "LSN-2026-CHAPTER4-PREMATURE-INTERPRETATION-AND-HYPERBOLE": ["academic-writer"],
        "LSN-2026-DOM-PARSING-FOR-OPENXML-MODIFICATION-001": ["academic-writer"],
        "LSN-2026-EXPLICIT-RIGHT-ALIGNMENT-AND-INLINE-MARKDOWN-PARSING-001": ["academic-writer"],
        "LSN-2026-FORMATTING-AND-FILTERING-FAILURE-001": ["academic-writer"],

        # Group 2: Bibliographic Management & Citation Extraction
        "AP-2026-NAIVE-LENGTH-REFERENCE-PARSING": ["academic-writer", "research-agent"],
        "LSN-2026-NAIVE-LENGTH-REFERENCE-EXTRACTION": ["academic-writer", "research-agent"],
        "LSN-2026-PERMISSIVE-VALIDATOR-BLINDSPOT-001": ["academic-writer", "research-agent"],
        "LSN-2026-STRUCTURAL-REFERENCE-PARSING-001": ["academic-writer", "research-agent"],

        # Group 3: Statistical Modeling, SEM, & Analysis Syntax
        "AP-2026-MANIFEST-PATH-LABELED-AS-SEM": ["statistics-agent"],
        "CAND-2026-DIAGRAM-CEX-AND-UNLINK-001": ["statistics-agent"],
        "CAND-2026-SEM-SINGLE-INDICATOR-001": ["statistics-agent"],
        "CAND-20260927-SEM-REG-001": ["statistics-agent"],
        "LSN-2026-WRITER-READ-ONLY-JSON-MANDATE": ["statistics-agent"],

        # Group 4: Joint Analytical & Narrative Delivery (Regression Tables & Triad JSON)
        "AP-2026-MISSING-TRIAD-JSON-001": ["academic-writer", "statistics-agent"],
        "CAND-2026-CH4-SINGLE-SAMPLE-INVARIANT": ["academic-writer", "statistics-agent"],
        "CAND-2026-DISAGGREGATED-HYPOTHESIS-JSON-001": ["academic-writer", "statistics-agent"],
        "LSN-2026-LANGUAGE-TRACK-AWARE-TYPOGRAPHY": ["academic-writer", "statistics-agent"],
        "LSN-2026-VALIDATOR-THREE-TABLE-FAIL-CLOSED-001": ["academic-writer", "statistics-agent"],

        # Group 5: Data Screening & Demographic Statistics
        "CAND-2026-DATA-AUDIT-SINGLE-SAMPLE-INVARIANT": ["data-agent", "statistics-agent"],
        "CAND-2026-EXHAUSTIVE-DEMOGRAPHICS-001": ["academic-writer", "data-agent", "statistics-agent"],
        "AP-2026-DISCORDANT-HARNESSED-SAMPLE-SIZE": ["academic-writer", "data-agent", "statistics-agent"],

        # Group 6: Pipeline Orchestration & Validation Decontamination
        "AP-2026-COPY-WITHOUT-UNLINK-CONTAMINATION": ["academic-orchestrator", "statistics-agent"],
        "AP-2026-DECOUPLED-PAYLOAD-TRIAD-FRAGMENTATION": ["academic-orchestrator"],
        "AP-2026-LEGACY-VAL-ISOLATION": ["academic-orchestrator"],
        "AP-2026-REGRESSION-TABLE-OVERAPPLICATION-TO-SEM": ["academic-orchestrator", "statistics-agent"],
        "AP-2026-SUBDIRECTORY-VALIDATION-QUARANTINE-FAILURE": ["academic-orchestrator"],
        "CAND-2026-ATOMIC-TRIAD-CH4-001": ["academic-orchestrator", "statistics-agent"],
        "CAND-2026-ATOMIC-TRIAD-ORCH-001": ["academic-orchestrator"],
        "CAND-2026-EVAL-DECONTAMINATION-001": ["academic-orchestrator"],
        "CAND-2026-LEGACY-VAL-ISOLATION-001": ["academic-orchestrator"],
        "CAND-2026-LEGACY-VAL-PHYSICAL-CLEAN-001": ["academic-orchestrator"],
        "CAND-2026-MECHANICAL-GRADUATION-DECONTAMINATION-001": ["academic-orchestrator"],
        "CAND-2026-METHODOLOGY-AWARE-VALIDATION-BRANCHING": ["academic-orchestrator", "statistics-agent"],
        "CAND-2026-PHYSICAL-DECONTAMINATION-001": ["academic-orchestrator"],
        "CAND-20260927-CHAPTER4-WRITING-001": ["academic-orchestrator"],
        "CAND-20260927-THESIS-INTEGRITY-001": ["academic-orchestrator"],
        "LSN-2026-LEGACY-VALIDATION-REPORT-DEACTIVATION": ["academic-orchestrator"],
    }

    @classmethod
    def normalize_target_agents(
        cls,
        target_agents: Optional[List[str]],
        file_pattern: Optional[str] = None,
        target_skills: Optional[List[str]] = None,
        statement: Optional[str] = None,
        rule_id: Optional[str] = None
    ) -> List[str]:
        """
        Normalizes target_agents to explicit, canonical academic workers.
        Translates legacy skill names, strips unassociated auditors from authoring rules,
        and excludes continuous learning subagents from academic delivery gates.
        """
        if rule_id and rule_id in cls.CANONICAL_RULE_TARGETS:
            return sorted(list(cls.CANONICAL_RULE_TARGETS[rule_id]))

        raw = [a.strip() for a in (target_agents or []) if a and a.strip()]

        # Translate legacy skill names to canonical agent names
        translated = []
        for a in raw:
            if a in cls.SKILL_TO_AGENT:
                translated.append(cls.SKILL_TO_AGENT[a])
            else:
                translated.append(a)

        # Exclude continuous learning subagents from delivery rules
        filtered = [
            a for a in translated
            if a not in (
                "evaluation-agent", "skill-evolver", "behavior-analyst",
                "knowledge-curator", "trajectory-analyzer", "curriculum-builder"
            )
        ]

        fp = (file_pattern or "").lower()
        stmt = (statement or "").lower()
        skills = [s.lower() for s in (target_skills or [])]

        is_authoring_rule = any(ext in fp for ext in ("docx", "doc", "md", "txt", "r", "py")) and "validation_report" not in fp
        if is_authoring_rule:
            # Exclude auditors from deliverable authoring rules
            filtered = [
                a for a in filtered
                if a not in ("validation-agent", "results-auditor", "statistical-auditor", "evidence-auditor", "academic-challenger", "final-judge")
            ]

        # If explicit, valid agents remain and '*' is not present, return them
        clean_explicit = [a for a in filtered if a != "*"]
        if clean_explicit and "*" not in filtered:
            return sorted(list(set(clean_explicit)))

        # Infer canonical delivery agents from file_pattern, statement, and skills
        agents = set(clean_explicit)

        is_doc = (
            any(ext in fp for ext in ("docx", "doc", "md", "txt"))
            or any(k in fp for k in ("chapter", "discussion", "proposal", "defense", "deliverable"))
            or any(k in stmt for k in ("table", "bidi", "font", "openxml", "docx", "heading", "typography", "footnote", "prose"))
        )
        is_stats = (
            any(ext in fp for ext in ("r", "rmd", "sps"))
            or any(k in fp for k in ("sem", "spss", "stat", "regression", "mediation", "cfa"))
            or any(k in stmt for k in ("sem", "latent", "indicator", "parceling", "regression", "lavaan", "f-test"))
        )
        is_data = (
            any(k in fp for k in ("data", "audit", "clean", "dataset", "curat"))
            or any(k in stmt for k in ("dual-sample", "data audit", "demographic", "sample size"))
        )
        is_orch = (
            any(k in fp for k in ("validation_report", "legacy_validation", "manifest"))
            or any(k in stmt for k in ("premature global validation", "legacy validation", "decontamination", "triad synthesis", "orchestrat"))
            or any(any(k in s for k in ("orchestrat", "pipeline")) for s in skills)
        )
        is_ref = (
            any(k in fp for k in ("reference", "bibliography", "bib"))
            or any(k in stmt for k in ("reference", "bibliography", "citation", "endnote"))
        )

        if is_ref:
            agents.update(["academic-writer", "research-agent"])
        if is_doc:
            agents.add("academic-writer")
        if is_stats:
            agents.add("statistics-agent")
        if is_data:
            agents.update(["data-agent", "statistics-agent"])
        if is_orch:
            agents.add("academic-orchestrator")

        if not agents:
            agents.update(["academic-writer", "statistics-agent", "data-agent"])

        # Incorporate skill mappings
        for s in skills:
            if any(k in s for k in ("write", "discussion", "builder", "apa", "thesis", "docx", "table")):
                agents.add("academic-writer")
            if any(k in s for k in ("stat", "sem", "cfa", "regression", "mediation")):
                agents.add("statistics-agent")
            if any(k in s for k in ("data", "audit", "cleaning")):
                agents.add("data-agent")

        return sorted(list(agents))

    @classmethod
    def normalize_all_invariants(cls, base_dir: Optional[str] = None) -> int:
        """Normalizes target_agents across all active invariants in enforced_invariants.json."""
        target_path = INVARIANTS_FILE
        if base_dir:
            target_path = os.path.join(base_dir, ".agents", "hooks", "rules", "enforced_invariants.json")
        if not os.path.isfile(target_path):
            return 0

        with open(target_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        invariants = raw_data.get("invariants", {})
        updated_count = 0
        for item_id, rule in invariants.items():
            targets = rule.get("target_agents", [])
            normalized = cls.normalize_target_agents(
                targets,
                file_pattern=rule.get("file_pattern"),
                target_skills=rule.get("target_skills"),
                statement=rule.get("statement"),
                rule_id=item_id
            )
            if normalized != targets:
                rule["target_agents"] = normalized
                rule["updated_at"] = datetime.now(timezone.utc).isoformat()
                updated_count += 1

        if updated_count > 0:
            raw_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(raw_data, f, indent=2, ensure_ascii=False)
            cls._cached_mtime = os.path.getmtime(target_path)
            cls._cached_invariants = invariants

        return updated_count

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

        normalized_targets = cls.normalize_target_agents(
            target_agents,
            file_pattern=file_pattern,
            target_skills=target_skills,
            statement=statement,
            rule_id=item_id
        )

        invariants = raw_data.get("invariants", {})
        rule_entry = {
            "item_id": item_id,
            "category": category,
            "statement": statement,
            "target_agents": normalized_targets,
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
        if not caller_clean:
            sub_desc = payload.get("subagentDescriptor") or {}
            if isinstance(sub_desc, dict):
                caller_clean = (sub_desc.get("typeName") or sub_desc.get("role") or "").strip().lower()

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
            if is_learning_subagent(caller_clean) and caller_clean not in target_agents:
                continue
            if "*" not in target_agents and caller_clean and caller_clean not in target_agents:
                if caller_clean not in ("academic-agent", "academic", "unknown", "specialist", "subagent"):
                    continue

            # Tool name matching
            tool_match = rule.get("tool_match", "")
            if tool_match and not re.search(tool_match, tool_name, re.IGNORECASE):
                continue

            # File pattern matching
            file_pattern = rule.get("file_pattern", "")
            if file_pattern:
                if not target_file or not re.search(file_pattern, target_file, re.IGNORECASE):
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
                if pattern:
                    full_haystack = f"{content} {json.dumps(args)}"
                    if not re.search(pattern, full_haystack, re.IGNORECASE):
                        continue
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
        if not caller_clean:
            sub_desc = payload.get("subagentDescriptor") or {}
            if isinstance(sub_desc, dict):
                caller_clean = (sub_desc.get("typeName") or sub_desc.get("role") or "").strip().lower()

        # Learning subagents (benchmarking/evaluation) and quality auditor subagents (audit reporting)
        # do not author thesis deliverables in 03_deliverables/ and must never be blocked by deliverable defects.
        if is_learning_subagent(caller_clean) or is_auditor_agent(caller_clean):
            return {"decision": "allow"}

        invariants = cls.load_invariants()
        if not invariants:
            return {"decision": "allow"}

        cand_dirs = []
        for k in ("deliverables_path", "deliverables_dir", "stage_dir"):
            val = payload.get(k)
            if val and os.path.isdir(str(val)):
                cand_p = os.path.abspath(str(val))
                if cand_p not in cand_dirs:
                    cand_dirs.append(cand_p)

        if not cand_dirs:
            workspaces = payload.get("workspacePaths", [ROOT_DIR]) or [ROOT_DIR]
            for ws in workspaces:
                if ws and os.path.isdir(ws):
                    cand = os.path.join(ws, "03_deliverables")
                    if os.path.isdir(cand) and cand not in cand_dirs:
                        cand_dirs.append(cand)

            cwd_cand = os.path.join(os.getcwd(), "03_deliverables")
            if os.path.isdir(cwd_cand) and cwd_cand not in cand_dirs:
                cand_dirs.append(cwd_cand)

        if not cand_dirs:
            return {"decision": "allow"}

        for rule_id, rule in invariants.items():
            if not rule.get("enabled", True):
                continue

            event = rule.get("event", "Stop")
            if event not in ("Stop", "Both", "*"):
                continue

            target_agents = [a.lower().strip() for a in rule.get("target_agents", [])]
            if is_learning_subagent(caller_clean) and caller_clean not in target_agents:
                continue
            if "*" not in target_agents and caller_clean and caller_clean not in target_agents:
                if caller_clean not in ("academic-agent", "academic", "unknown", "specialist", "subagent"):
                    continue

            file_pattern = rule.get("file_pattern", "")
            check_type = rule.get("check_type", "")
            pattern = rule.get("pattern", "")
            v_msg = rule.get("violation_message") or rule.get("statement") or "Mechanical integrity defect detected."
            remedy = rule.get("remedy", "")

            # Scan files matching file_pattern across all discovered deliverable directories
            for d_dir in cand_dirs:
                for root_p, _, files in os.walk(d_dir):
                    for fname in files:
                        full_p = os.path.join(root_p, fname)
                        if file_pattern and not re.search(file_pattern, full_p, re.IGNORECASE):
                            continue

                        # Validation reports are audit logs, exempt from narrative content bans unless explicitly targeted
                        if fname.lower() == "validation_report.json" and "validation_report" not in file_pattern.lower():
                            continue

                        # OpenXML (.docx) deep inspection
                        if full_p.lower().endswith(".docx"):
                            try:
                                with zipfile.ZipFile(full_p, "r") as zf:
                                    if "word/document.xml" in zf.namelist():
                                        xml_bytes = zf.read("word/document.xml")
                                        xml_content = xml_bytes.decode("utf-8", errors="replace")

                                        # DOM table check (Directive 3.1 & openxml_dom_ban)
                                        is_ch5_prose_rule = (
                                            rule_id == "LSN-2026-CHAPTER-5-PROSE-ONLY-INVARIANT-001"
                                            or "chapter-5" in rule_id.lower()
                                            or "prose-only" in rule_id.lower()
                                        )
                                        if check_type == "openxml_dom_ban" or is_ch5_prose_rule:
                                            root_xml = ET.fromstring(xml_bytes)
                                            tbls = [e for e in root_xml.iter() if e.tag.endswith("}tbl") or e.tag == "tbl"]
                                            if tbls and (check_type == "openxml_dom_ban" or is_ch5_prose_rule):
                                                return {
                                                    "decision": "continue",
                                                    "reason": (
                                                        f"MECHANICAL INTEGRITY DEFECT (Learned Invariant {rule_id}):\n"
                                                        f"Word deliverable '{os.path.basename(full_p)}' contains {len(tbls)} prohibited Word table(s).\n"
                                                        f"{v_msg}\n"
                                                        f"Remedy: {remedy}"
                                                    )
                                                }

                                        # Regex check on OpenXML markup / text runs
                                        if check_type in ("regex_ban", "markdown_table_ban") and pattern:
                                            if re.search(pattern, xml_content, re.MULTILINE):
                                                return {
                                                    "decision": "continue",
                                                    "reason": (
                                                        f"MECHANICAL INTEGRITY DEFECT (Learned Invariant {rule_id}):\n"
                                                        f"Word deliverable '{os.path.basename(full_p)}' matches prohibited pattern '{pattern}'.\n"
                                                        f"{v_msg}\n"
                                                        f"Remedy: {remedy}"
                                                    )
                                                }

                                        # Substring check on OpenXML markup
                                        elif check_type == "substring_ban" and pattern:
                                            if pattern in xml_content:
                                                return {
                                                    "decision": "continue",
                                                    "reason": (
                                                        f"MECHANICAL INTEGRITY DEFECT (Learned Invariant {rule_id}):\n"
                                                        f"Word deliverable '{os.path.basename(full_p)}' contains prohibited substring '{pattern}'.\n"
                                                        f"{v_msg}\n"
                                                        f"Remedy: {remedy}"
                                                    )
                                                }
                            except Exception:
                                pass

                        # Text, Markdown, JSON, HTML, and script deliverable inspection
                        elif full_p.lower().endswith((".md", ".txt", ".json", ".xml", ".html", ".r", ".py")):
                            try:
                                with open(full_p, "r", encoding="utf-8") as f:
                                    f_content = f.read()

                                if check_type in ("regex_ban", "markdown_table_ban") and pattern:
                                    if re.search(pattern, f_content, re.MULTILINE):
                                        return {
                                            "decision": "continue",
                                            "reason": (
                                                f"MECHANICAL INTEGRITY DEFECT (Learned Invariant {rule_id}):\n"
                                                f"File '{os.path.basename(full_p)}' matches prohibited pattern '{pattern}'.\n"
                                                f"{v_msg}\n"
                                                f"Remedy: {remedy}"
                                            )
                                        }

                                elif check_type == "substring_ban" and pattern:
                                    if pattern in f_content:
                                        return {
                                            "decision": "continue",
                                            "reason": (
                                                f"MECHANICAL INTEGRITY DEFECT (Learned Invariant {rule_id}):\n"
                                                f"File '{os.path.basename(full_p)}' contains prohibited substring '{pattern}'.\n"
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
