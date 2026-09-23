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
try:
    from contracts.hook_identity_contract import resolve_transcript_path
except ImportError:
    try:
        from .contracts.hook_identity_contract import resolve_transcript_path
    except ImportError:
        def resolve_transcript_path(payload):
            return payload.get("transcriptPath") if isinstance(payload, dict) else None
try:
    from scripts.academic_context_token_budgeter import AcademicContextTokenBudgeter
except ImportError:
    from academic_context_token_budgeter import AcademicContextTokenBudgeter

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

# Canonical role fallback mappings ensuring specialist subagents always receive domain lessons
ROLE_DEFAULT_CAPABILITY_MAP: Dict[str, Dict[str, str]] = {
    "academic-writer": {"capability": "chapter4", "task": "chapter_4_drafting", "domain": "academic-writing"},
    "statistics-agent": {"capability": "SEM", "task": "structural_equation_modeling", "domain": "statistical-modeling"},
    "statistical-expert": {"capability": "SEM", "task": "structural_equation_modeling", "domain": "statistical-modeling"},
    "data-agent": {"capability": "data_cleaning", "task": "data_curation_screening", "domain": "data-curation"},
    "data-curator": {"capability": "data_cleaning", "task": "data_curation_screening", "domain": "data-curation"},
    "validation-agent": {"capability": "general_academic", "task": "adversarial_validation", "domain": "general-methodology"},
    "results-auditor": {"capability": "chapter4", "task": "apa_reporting", "domain": "academic-writing"},
    "statistical-auditor": {"capability": "SEM", "task": "statistical_audit", "domain": "statistical-modeling"},
    "psychometric-expert": {"capability": "psychometrics", "task": "scale_construct_validation", "domain": "psychometrics"},
    "methodology-expert": {"capability": "methodology", "task": "methodology_design", "domain": "research-methodology"},
    "research-agent": {"capability": "literature_review", "task": "literature_synthesis", "domain": "epistemic-literature"},
    "literature-expert": {"capability": "literature_review", "task": "literature_synthesis", "domain": "epistemic-literature"},
    "project-organizer": {"capability": "general_academic", "task": "project_organization", "domain": "general-methodology"},
    "academic-orchestrator": {"capability": "general_academic", "task": "general_task", "domain": "general-methodology"},
}


class AcademicAdaptiveContextBoundary:
    """
    Deterministic engine executing context retrieval at the execution boundary.
    Guarantees that relevant lessons, known pitfalls, and applicable methodology rules
    are retrieved and bound before cognitive execution begins.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or ROOT_DIR)
        self.km = AcademicKnowledgeManager(base_dir=self.base_dir)
        self.budgeter = AcademicContextTokenBudgeter()

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

        # 0. Delegation Envelope Recognition: Extract worker agent from contract if present
        if "contractual delegation envelope" in clean_text or "contract version" in clean_text:
            worker_match = re.search(r"worker agent\s*[:*]+\s*`?([a-zA-Z0-9_-]+)`?", clean_text)
            if worker_match and not meta.get("agent"):
                meta["agent"] = worker_match.group(1).lower().strip()

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

        # 2. Match against role default capability if agent is explicitly provided
        req_agent = str(meta.get("agent") or "").lower().strip()
        if req_agent:
            for r_key, r_val in ROLE_DEFAULT_CAPABILITY_MAP.items():
                if r_key == req_agent or r_key in req_agent or req_agent in r_key:
                    return {
                        "capability": r_val["capability"],
                        "task": meta.get("task", r_val["task"]),
                        "primary_agent": req_agent,
                        "domain": r_val["domain"],
                        "project_id": meta.get("project_id")
                    }

        # 3. General Academic Task Fallback if academic keywords detected
        academic_keywords = [
            "hypothesis", "variable", "scale", "dataset", "table", "apa", "p-value",
            "effect size", "thesis", "dissertation", "lesson", "knowledge", "anti-pattern",
            "audit", "findings", "results", "simulation", "simulated", "proposal", "methodology",
            "subagent", "agent", "shahram", "chapter", "r-lavaan", "spss", "excel", "questionnaire"
        ]
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
        limit_per_category: int = 3,
        max_token_budget: Optional[int] = 800
    ) -> Dict[str, Any]:
        """
        Deterministically queries knowledge store and packages context into the 4-part contract:
        1. relevant_lessons
        2. known_pitfalls
        3. applicable_methodology_rules
        4. calibrated_defaults
        Utilizes Phase 29 Two-Stage Retrieval and Phase 41 Dynamic Context Token Budgeting.
        """
        raw_context = self.km.retrieve_pre_task_context(
            capability=capability,
            task=task or "general_task",
            agent=agent,
            domain=domain,
            failure_types=[failure_type] if failure_type else None,
            project_id=project_id,
            limit_per_category=limit_per_category,
            task_description=prompt_text,
            max_token_budget=max_token_budget
        )

        lessons = raw_context.get("lessons", [])
        anti_patterns = raw_context.get("anti_patterns", [])
        contradictions = raw_context.get("contradictions", [])
        exemplars = raw_context.get("exemplars", [])
        cap_sum = raw_context.get("capability_summary", {})
        calibrated_defaults = cap_sum.get("calibrated_parameter_defaults", {}) if cap_sum else {}
        budget_telem = raw_context.get("budget_telemetry", {})

        # Format 4-part boundary payload
        boundary_payload = {
            "contract_version": "1.0.0",
            "target_capability": capability,
            "task": task or "general_task",
            "agent": agent or "academic-orchestrator",
            "project_id": project_id or "cross-project",
            "max_token_budget": max_token_budget,
            "budget_telemetry": budget_telem,
            "relevant_lessons": [
                {
                    "lesson_id": l.get("lesson_id", "LSN"),
                    "mandate": l.get("desired_behavior") or l.get("mandate", ""),
                    "generalization": l.get("generalization", ""),
                    "confidence": l.get("confidence", 0.50)
                }
                for l in lessons
            ],
            "known_pitfalls": [
                {
                    "anti_pattern_id": ap.get("anti_pattern_id", "AP"),
                    "defect": ap.get("defective_pattern") or ap.get("defect", ""),
                    "remedy": ap.get("corrective_remedy") or ap.get("remedy", "")
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
            ],
            "formatted_briefing": raw_context.get("formatted_briefing", "")
        }

        return boundary_payload

    def format_boundary_briefing(self, payload: Dict[str, Any]) -> str:
        """
        Renders the 4-part boundary payload into an authoritative Markdown briefing.
        Seated directly in immediate agent context window before execution.
        """
        if payload.get("formatted_briefing"):
            return payload["formatted_briefing"]

        cap = payload.get("target_capability", "General")
        task = payload.get("task", "general_task")
        agent = payload.get("agent", "academic-orchestrator")
        proj = payload.get("project_id", "cross-project")
        budget = payload.get("max_token_budget", 800)

        budgeted = self.budgeter.budget_context(
            raw_context={
                "lessons": payload.get("relevant_lessons", []),
                "anti_patterns": payload.get("known_pitfalls", []),
                "contradictions": payload.get("applicable_methodology_rules", []),
                "exemplars": payload.get("exemplars", []),
                "capability_summary": {"calibrated_parameter_defaults": payload.get("calibrated_defaults", {})}
            },
            max_token_budget=budget,
            target_capability=cap,
            task=task,
            agent=agent,
            project_id=proj
        )
        return budgeted["formatted_briefing"]

    def retrieve_for_turn(self, hook_payload: Dict[str, Any]) -> Optional[str]:
        """
        Executes turn-level context retrieval at the PreInvocation execution boundary.
        Inspects the incoming turn, detects academic intent, and returns formatted briefing.
        """
        cid = hook_payload.get("conversationId")
        transcript_path = resolve_transcript_path(hook_payload)

        last_user_msg = (
            hook_payload.get("userPrompt")
            or hook_payload.get("userMessage")
            or hook_payload.get("prompt")
            or hook_payload.get("message")
            or ""
        )
        if not last_user_msg and transcript_path and os.path.isfile(transcript_path):
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

        agent_name = (
            hook_payload.get("agentName")
            or hook_payload.get("agentRole")
            or hook_payload.get("agent")
            or ""
        ).strip()

        clean_user = re.sub(r"<[^>]+>", "", last_user_msg).strip()
        intent = self.detect_task_intent(clean_user, metadata={"conversation_id": cid, "agent": agent_name})
        if not intent:
            return None

        boundary_data = self.retrieve_boundary_context(
            capability=intent["capability"],
            task=intent.get("task"),
            agent=intent.get("primary_agent"),
            domain=intent.get("domain"),
            project_id=intent.get("project_id"),
            prompt_text=clean_user,
            max_token_budget=self.budgeter.DEFAULT_TOKEN_BUDGET
        )

        return self.format_boundary_briefing(boundary_data)

    def enrich_subagent_dispatch(self, subagents: Any) -> Any:
        """
        Enriches subagent dispatch payloads with role-specific boundary context.
        Ensures dispatched subagents have lessons and pitfalls embedded before execution.
        Supports subagents as List[Dict] or serialized JSON str.
        """
        if not subagents:
            return subagents

        is_stringified = False
        parsed_subagents = subagents
        if isinstance(subagents, str):
            try:
                parsed_subagents = json.loads(subagents)
                is_stringified = True
            except Exception:
                return subagents

        if not isinstance(parsed_subagents, list):
            return subagents

        enriched = []
        for sa in parsed_subagents:
            if not isinstance(sa, dict):
                enriched.append(sa)
                continue

            sa_copy = dict(sa)
            role = str(sa_copy.get("Role", "")).strip()
            type_name = str(sa_copy.get("TypeName", "")).strip()
            prompt = str(sa_copy.get("Prompt", "")).strip()

            # Prevent double-enrichment if already bound
            if sa_copy.get("adaptive_context_bound") or "DETERMINISTIC ADAPTIVE CONTEXT" in prompt or "Active Learned Behavioral Context" in prompt:
                enriched.append(sa_copy)
                continue

            # Detect intent from subagent role and prompt
            intent = self.detect_task_intent(f"{role} {type_name} {prompt}", metadata={"agent": type_name or role})
            if not intent:
                clean_type = (type_name or role or "").lower().strip()
                fallback = None
                for k, v in ROLE_DEFAULT_CAPABILITY_MAP.items():
                    if k == clean_type or k in clean_type or clean_type in k:
                        fallback = v
                        break
                if fallback:
                    intent = {
                        "capability": fallback["capability"],
                        "task": fallback["task"],
                        "primary_agent": type_name or role,
                        "domain": fallback["domain"],
                        "project_id": None
                    }
                else:
                    intent = {
                        "capability": "general_academic",
                        "task": "subagent_execution",
                        "primary_agent": type_name or role,
                        "domain": "general-methodology",
                        "project_id": None
                    }

            cap = intent["capability"]
            task = intent.get("task", "subagent_execution")

            b_data = self.retrieve_boundary_context(
                capability=cap,
                task=task,
                agent=type_name or role,
                domain=intent.get("domain"),
                prompt_text=prompt,
                max_token_budget=self.budgeter.SUBAGENT_TOKEN_BUDGET
            )
            briefing = self.format_boundary_briefing(b_data)

            if briefing and briefing.strip():
                sa_copy["Prompt"] = f"{briefing.strip()}\n\n---\n### Executable Task Assignment:\n{prompt}"
                sa_copy["adaptive_context_bound"] = True

            enriched.append(sa_copy)

        if is_stringified:
            return json.dumps(enriched, ensure_ascii=False)
        return enriched
