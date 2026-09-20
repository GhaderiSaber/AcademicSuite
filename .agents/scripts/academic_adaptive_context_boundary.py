#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_adaptive_context_boundary.py — Deterministic Execution Boundary Context Engine

Governs Phase 28: Guarantees that adaptive context retrieval happens deterministically
at the execution boundary rather than relying on voluntary agent memory.

Pipeline Invariant:
Academic task begins
       ↓
context retrieval
       ↓
relevant lessons
       ↓
known pitfalls
       ↓
applicable methodology rules
       ↓
agent execution

Key Boundaries:
1. Turn Execution Boundary (PreInvocation Hook): Intercepts turns before LLM execution,
   detects academic task intent, and injects context into ephemeral messages.
2. Delegation Boundary (PreToolUse Hook): Intercepts invoke_subagent, enriching subagent
   prompts with specialist lessons, pitfalls, and methodology rules.
3. Anti-Dump Invariant: Non-academic turns (git operations, trivial greetings) bypass retrieval.
"""

import os
import sys
import re
import json
from typing import Dict, Any, List, Optional, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.academic_knowledge_manager import AcademicKnowledgeManager

# Canonical mapping from keyword patterns to capability, default task, and primary agent
ACADEMIC_CAPABILITY_SIGNATURES: List[Dict[str, Any]] = [
    {
        "capability": "mediation",
        "patterns": [r"\bmediation\b", r"\bindirect effect\b", r"\bsobel\b", r"\bpreacher\b", r"\bbootstrap mediation\b", r"\bbca\b"],
        "default_task": "bootstrap_mediation",
        "primary_agent": "statistics-agent",
        "domain": "statistical-modeling"
    },
    {
        "capability": "moderation",
        "patterns": [r"\bmoderation\b", r"\binteraction effect\b", r"\bsimple slopes\b", r"\bjohnson[- ]neyman\b", r"\bmean[- ]center\b"],
        "default_task": "moderation_interaction",
        "primary_agent": "statistics-agent",
        "domain": "statistical-modeling"
    },
    {
        "capability": "longitudinal-analysis",
        "patterns": [r"\brepeated[- ]measures\b", r"\brm[- ]anova\b", r"\blongitudinal\b", r"\blinear mixed model\b", r"\blmm\b", r"\bsphericity\b", r"\bmauchly\b"],
        "default_task": "repeated_measures_modeling",
        "primary_agent": "statistics-agent",
        "domain": "longitudinal-design"
    },
    {
        "capability": "SEM",
        "patterns": [r"\bsem\b", r"\bstructural equation\b", r"\bpath analysis\b", r"\blatent variable\b", r"\bmodel fit\b", r"\bfit indices\b"],
        "default_task": "structural_equation_modeling",
        "primary_agent": "statistics-agent",
        "domain": "structural-equation-modeling"
    },
    {
        "capability": "psychometrics",
        "patterns": [r"\bcfa\b", r"\bconfirmatory factor\b", r"\bscale validation\b", r"\bcvr\b", r"\bcvi\b", r"\bitem analysis\b", r"\bave\b", r"\bomega\b", r"\bcronbach\b"],
        "default_task": "scale_construct_validation",
        "primary_agent": "psychometric-expert",
        "domain": "psychometrics"
    },
    {
        "capability": "methodology",
        "patterns": [r"\bg\*?power\b", r"\bsample size\b", r"\bpower analysis\b", r"\bchapter\s*3\b", r"\bmethodology\b", r"روش تحقیق", r"فصل\s*سوم"],
        "default_task": "methodology_design",
        "primary_agent": "methodology-expert",
        "domain": "research-methodology"
    },
    {
        "capability": "ancova",
        "patterns": [r"\bancova\b", r"\bcovariate\b", r"\bhomogeneity of regression\b", r"\badjusted mean\b"],
        "default_task": "ancova_modeling",
        "primary_agent": "statistics-agent",
        "domain": "experimental-design"
    },
    {
        "capability": "regression",
        "patterns": [r"\bmultiple regression\b", r"\bhierarchical regression\b", r"\bstepwise regression\b", r"\bcollinearity\b", r"\bvif\b"],
        "default_task": "multiple_regression",
        "primary_agent": "statistics-agent",
        "domain": "statistical-modeling"
    },
    {
        "capability": "data_cleaning",
        "patterns": [r"\bclean(?:ing)? data\b", r"\breverse[- ]code\b", r"\bmissing data\b", r"\blittle'?s? mcar\b", r"\bunengaged\b", r"\bmahalanobis\b"],
        "default_task": "data_curation_screening",
        "primary_agent": "data-curator",
        "domain": "data-curation"
    },
    {
        "capability": "chapter4",
        "patterns": [r"\bchapter\s*4\b", r"\bresults chapter\b", r"\bfindings chapter\b", r"فصل\s*چهارم", r"یافته‌ها"],
        "default_task": "chapter_4_drafting",
        "primary_agent": "academic-writer",
        "domain": "academic-writing"
    },
    {
        "capability": "chapter5",
        "patterns": [r"\bchapter\s*5\b", r"\bdiscussion chapter\b", r"\bconclusions?\b", r"فصل\s*پنجم", r"بحث و نتیجه‌گیری"],
        "default_task": "chapter_5_drafting",
        "primary_agent": "academic-writer",
        "domain": "academic-writing"
    },
    {
        "capability": "literature_review",
        "patterns": [r"\bchapter\s*2\b", r"\bliterature review\b", r"\btheoretical framework\b", r"پیشینه پژوهش", r"فصل\s*دوم"],
        "default_task": "literature_synthesis",
        "primary_agent": "literature-expert",
        "domain": "epistemic-literature"
    },
    {
        "capability": "proposal",
        "patterns": [r"\bproposal\b", r"\bresearch proposal\b", r"طرح تحقیق", r"پروپوزال"],
        "default_task": "proposal_drafting",
        "primary_agent": "academic-writer",
        "domain": "proposal-development"
    }
]

# Patterns that indicate purely non-academic execution turns (Bypass Anti-Dump)
BYPASS_PATTERNS: List[str] = [
    r"^\s*git\s+(?:status|commit|push|add|diff|checkout|branch|log)\b",
    r"^\s*(?:clean\s+working\s+tree|git\s+lifecycle)\b",
    r"^\s*(?:hello|hi|hey|thanks|thank\s+you|ok|okay|yes|proceed|continue|agree|approved)\b",
    r"^\s*(?:view_file|read_file|ls|pwd|whoami)\b"
]


class AcademicAdaptiveContextBoundary:
    """
    Deterministic engine executing context retrieval at the execution boundary.
    Guarantees that relevant lessons, known pitfalls, and applicable methodology rules
    are retrieved and bound before cognitive execution begins.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or ROOT_DIR)
        self.km = AcademicKnowledgeManager(base_dir=self.base_dir)

    def is_bypass_turn(self, text: str) -> bool:
        """Determines if the text matches pure operational or trivial conversational bypass."""
        if not text or not text.strip():
            return True
        clean = text.strip().lower()
        if len(clean) < 4:
            return True
        for pat in BYPASS_PATTERNS:
            if re.search(pat, clean):
                return True
        return False

    def detect_task_intent(self, prompt_text: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Deterministically maps prompt text and context metadata to implicated capability,
        task, primary agent, and domain. Returns None if non-academic turn.
        """
        if self.is_bypass_turn(prompt_text):
            return None

        clean_text = prompt_text.lower()
        meta = metadata or {}
        explicit_cap = meta.get("capability")

        # 1. Match against known academic signatures
        for sig in ACADEMIC_CAPABILITY_SIGNATURES:
            if explicit_cap and explicit_cap.lower() == sig["capability"].lower():
                return {
                    "capability": sig["capability"],
                    "task": meta.get("task", sig["default_task"]),
                    "primary_agent": meta.get("agent", sig["primary_agent"]),
                    "domain": sig["domain"],
                    "project_id": meta.get("project_id")
                }

            for pat in sig["patterns"]:
                if re.search(pat, clean_text):
                    return {
                        "capability": sig["capability"],
                        "task": meta.get("task", sig["default_task"]),
                        "primary_agent": meta.get("agent", sig["primary_agent"]),
                        "domain": sig["domain"],
                        "project_id": meta.get("project_id")
                    }

        # 2. General Academic Task Fallback if academic keywords detected
        academic_keywords = ["hypothesis", "variable", "scale", "dataset", "table", "apa", "p-value", "effect size", "thesis", "dissertation"]
        if any(w in clean_text for w in academic_keywords):
            return {
                "capability": "general_academic",
                "task": meta.get("task", "general_task"),
                "primary_agent": meta.get("agent", "academic-orchestrator"),
                "domain": "general-methodology",
                "project_id": meta.get("project_id")
            }

        return None

    def retrieve_boundary_context(
        self,
        capability: str,
        task: Optional[str] = None,
        agent: Optional[str] = None,
        domain: Optional[str] = None,
        project_id: Optional[str] = None,
        prompt_text: Optional[str] = None,
        failure_type: Optional[str] = None,
        limit_per_category: int = 3
    ) -> Dict[str, Any]:
        """
        Deterministically queries knowledge store and packages context into the 4-part contract:
        1. relevant_lessons
        2. known_pitfalls
        3. applicable_methodology_rules
        4. calibrated_defaults
        Utilizes Phase 29 Two-Stage Retrieval (Stage 1 Hard Filtering -> Stage 2 Semantic Ranking).
        """
        raw_context = self.km.retrieve_pre_task_context(
            capability=capability,
            task=task or "general_task",
            agent=agent,
            domain=domain,
            failure_types=[failure_type] if failure_type else None,
            project_id=project_id,
            limit_per_category=limit_per_category,
            task_description=prompt_text
        )

        lessons = raw_context.get("lessons", [])
        anti_patterns = raw_context.get("anti_patterns", [])
        contradictions = raw_context.get("contradictions", [])
        exemplars = raw_context.get("exemplars", [])
        cap_sum = raw_context.get("capability_summary", {})
        calibrated_defaults = cap_sum.get("calibrated_parameter_defaults", {}) if cap_sum else {}

        # Format 4-part boundary payload
        boundary_payload = {
            "contract_version": "1.0.0",
            "target_capability": capability,
            "task": task or "general_task",
            "agent": agent or "academic-orchestrator",
            "project_id": project_id or "cross-project",
            "relevant_lessons": [
                {
                    "lesson_id": l.get("lesson_id", "LSN"),
                    "mandate": l.get("desired_behavior", ""),
                    "generalization": l.get("generalization", ""),
                    "confidence": l.get("confidence", 0.50)
                }
                for l in lessons
            ],
            "known_pitfalls": [
                {
                    "anti_pattern_id": ap.get("anti_pattern_id", "AP"),
                    "defect": ap.get("defective_pattern", ""),
                    "remedy": ap.get("corrective_remedy", "")
                }
                for ap in anti_patterns
            ],
            "applicable_methodology_rules": [
                {
                    "contradiction_id": c.get("contradiction_id", "CTD"),
                    "conflict_type": c.get("conflict_type", ""),
                    "description": c.get("description", ""),
                    "applicability_conditions": c.get("applicability_conditions") or c.get("identified_conditions", {})
                }
                for c in contradictions
            ],
            "calibrated_defaults": calibrated_defaults,
            "exemplars": [
                {
                    "exemplar_id": ex.get("exemplar_id", "EXM"),
                    "task_type": ex.get("task_type", ""),
                    "why_exemplary": ex.get("why_exemplary", "")
                }
                for ex in exemplars
            ]
        }

        return boundary_payload

    def format_boundary_briefing(self, payload: Dict[str, Any]) -> str:
        """
        Renders the 4-part boundary payload into an authoritative Markdown briefing.
        Seated directly in immediate agent context window before execution.
        """
        cap = payload.get("target_capability", "General").upper()
        task = payload.get("task", "general_task")
        agent = payload.get("agent", "academic-orchestrator")
        proj = payload.get("project_id", "cross-project")

        lines = [
            f"🧠 DETERMINISTIC ADAPTIVE CONTEXT (BOUND AT EXECUTION BOUNDARY)",
            f"- **Target Capability**: `{cap}` | **Task**: `{task}` | **Agent**: `{agent}` | **Project**: `{proj}`",
            ""
        ]

        # 1. Known Pitfalls (Anti-Patterns to Avoid)
        pitfalls = payload.get("known_pitfalls", [])
        lines.append("⚠️ Known Pitfalls (Anti-Patterns to Avoid):")
        if pitfalls:
            for p in pitfalls:
                lines.append(f"- [{p.get('anti_pattern_id')}] Avoid: {p.get('defect')}")
                if p.get("remedy"):
                    lines.append(f"  Approved Remedy: {p.get('remedy')}")
        else:
            lines.append("- None cataloged for this capability. Enforce standard APA 7 & OpenXML rigor.")
        lines.append("")

        # 2. Relevant Lessons
        lessons = payload.get("relevant_lessons", [])
        lines.append("💡 Relevant Active Lessons:")
        if lessons:
            for l in lessons:
                lines.append(f"- [{l.get('lesson_id')}] Mandate: {l.get('mandate')}")
                if l.get("generalization"):
                    lines.append(f"  Generalization: {l.get('generalization')}")
        else:
            lines.append("- No specialized lessons flagged. Standard pipeline rules apply.")
        lines.append("")

        # 3. Applicable Methodology Rules & Reconciled Contradictions
        rules = payload.get("applicable_methodology_rules", [])
        lines.append("⚖️ Applicable Methodology Rules & Boundary Conditions:")
        if rules:
            for r in rules:
                lines.append(f"- [{r.get('contradiction_id')}] {r.get('conflict_type')}: {r.get('description')}")
                conds = r.get("applicability_conditions", {})
                if conds.get("condition_for_a"):
                    lines.append(f"  Condition A: {conds.get('condition_for_a')}")
                if conds.get("condition_for_b"):
                    lines.append(f"  Condition B: {conds.get('condition_for_b')}")
        else:
            lines.append("- No conflicting paradigms active. Follow primary statistical decision tree.")
        lines.append("")

        # 4. Calibrated Operational Defaults
        defaults = payload.get("calibrated_defaults", {})
        if defaults:
            lines.append(f"🎯 Calibrated Defaults: `{json.dumps(defaults)}`")
            lines.append("")

        return "\n".join(lines)

    def retrieve_for_turn(self, hook_payload: Dict[str, Any]) -> Optional[str]:
        """
        Executes turn-level context retrieval at the PreInvocation execution boundary.
        Inspects the incoming turn, detects academic intent, and returns formatted briefing.
        """
        transcript_path = hook_payload.get("transcriptPath")
        cid = hook_payload.get("conversationId")
        if not transcript_path and cid:
            cand = os.path.expanduser(f"~/.gemini/antigravity/brain/{cid}/.system_generated/logs/transcript.jsonl")
            if os.path.exists(cand):
                transcript_path = cand

        last_user_msg = ""
        if transcript_path and os.path.isfile(transcript_path):
            try:
                with open(transcript_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            rec = json.loads(line)
                            if rec.get("type") == "USER_INPUT" and rec.get("content"):
                                last_user_msg = rec.get("content", "").strip()
            except Exception:
                pass

        clean_user = re.sub(r"<[^>]+>", "", last_user_msg).strip()
        intent = self.detect_task_intent(clean_user, metadata={"conversation_id": cid})
        if not intent:
            return None

        boundary_data = self.retrieve_boundary_context(
            capability=intent["capability"],
            task=intent.get("task"),
            agent=intent.get("primary_agent"),
            domain=intent.get("domain"),
            project_id=intent.get("project_id"),
            prompt_text=clean_user
        )

        return self.format_boundary_briefing(boundary_data)

    def enrich_subagent_dispatch(self, subagents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enriches subagent dispatch payloads with role-specific boundary context.
        Ensures dispatched subagents have lessons and pitfalls embedded before execution.
        """
        enriched = []
        for sa in subagents:
            sa_copy = dict(sa)
            role = sa_copy.get("Role", "")
            type_name = sa_copy.get("TypeName", "")
            prompt = sa_copy.get("Prompt", "")

            # Detect intent from subagent role and prompt
            intent = self.detect_task_intent(f"{role} {type_name} {prompt}")
            cap = intent["capability"] if intent else type_name or role or "general"
            task = intent["task"] if intent else "subagent_execution"

            b_data = self.retrieve_boundary_context(
                capability=cap,
                task=task,
                agent=type_name or role,
                domain=intent.get("domain") if intent else None,
                prompt_text=prompt
            )
            briefing = self.format_boundary_briefing(b_data)

            # Prepend briefing into subagent prompt
            sa_copy["Prompt"] = f"{briefing}\n\n---\n### Executable Task Assignment:\n{prompt}"
            sa_copy["adaptive_context_bound"] = True
            enriched.append(sa_copy)

        return enriched
