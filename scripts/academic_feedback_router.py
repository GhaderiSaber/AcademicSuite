#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_feedback_router.py — Deterministic Feedback Routing Engine

Eliminates generic defaults (e.g., defaulting to statistics-agent) and guarantees that
every FeedbackRecord strictly contains:
- target_agent
- target_skill
- capability
- task
- stage

Authoritative 4-Tier Resolution Hierarchy:
1. Explicit metadata provided by caller.
2. Active state machine milestone/stage (RUNNING/VALIDATING/AWAITING_APPROVAL).
3. Forensic transcript inspection (most recent tool call / skill script).
4. Semantic domain mapping from user critique text.

Emits USER_FEEDBACK_DETECTED and routes directly to the target capability in the learning pipeline.
"""

import os
import sys
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.trajectory_engine import TrajectoryEngine, TrajectoryEventType


class UnresolvableFeedbackTargetError(Exception):
    """Raised when feedback cannot be routed to a verified capability without generic defaults."""
    pass


# Domain Capability and Agent Mappings
DOMAIN_CAPABILITY_MAP = {
    "WRITING_CORRECTION": {
        "target_agent": "academic-writer",
        "target_skill": "chapter-4-writing",
        "capability": "academic_writing",
        "default_task": "M4_CHAPTER4",
        "default_stage": "06_hypothesis_1"
    },
    "EVIDENCE_CORRECTION": {
        "target_agent": "literature-expert",
        "target_skill": "persian-literature-review-builder",
        "capability": "literature_synthesis",
        "default_task": "M2_LITERATURE",
        "default_stage": "02_literature_review"
    },
    "METHODOLOGY_CORRECTION": {
        "target_agent": "methodology-expert",
        "target_skill": "methodology-review",
        "capability": "research_methodology",
        "default_task": "M3_METHODOLOGY",
        "default_stage": "03_methodology"
    },
    "DATA_ANALYSIS_CORRECTION": {
        "target_agent": "data-curator",
        "target_skill": "data-audit",
        "capability": "data_curation",
        "default_task": "M1_DATA_CURATION",
        "default_stage": "00_data_curation"
    },
    "QUALITY_STYLE_CORRECTION": {
        "target_agent": "results-auditor",
        "target_skill": "apa-reporting",
        "capability": "apa_formatting",
        "default_task": "M9_STATISTICAL_QC",
        "default_stage": "09_statistical_qc"
    },
    "TYPOGRAPHY_CORRECTION": {
        "target_agent": "results-auditor",
        "target_skill": "apa-reporting",
        "capability": "typography_compliance",
        "default_task": "M10_TYPOGRAPHY_QC",
        "default_stage": "10_typography_qc"
    },
    "COMPLETENESS_CORRECTION": {
        "target_agent": "academic-orchestrator",
        "target_skill": "academic-suite-orchestrator",
        "capability": "workflow_orchestration",
        "default_task": "M11_OPENXML_ASSEMBLY",
        "default_stage": "11_openxml_assembly"
    },
    "PROCESS_CORRECTION": {
        "target_agent": "academic-orchestrator",
        "target_skill": "academic-suite-orchestrator",
        "capability": "stage_gate_orchestration",
        "default_task": "M11_OPENXML_ASSEMBLY",
        "default_stage": "11_openxml_assembly"
    },
    "RESEARCH_INTEGRITY_CORRECTION": {
        "target_agent": "validation-agent",
        "target_skill": "thesis-integrity-auditor",
        "capability": "research_integrity",
        "default_task": "M12_VIVA_SIMULATION",
        "default_stage": "12_viva_simulation"
    },
    "STATISTICAL_CORRECTION": {
        "target_agent": "statistics-agent",
        "target_skill": "statistical-data-analyst",
        "capability": "statistical_modeling",
        "default_task": "M7_HYPOTHESIS_TESTING",
        "default_stage": "06_hypothesis_1"
    }
}


class FeedbackRouter:
    """
    Deterministic Feedback Router ensuring zero generic defaults.
    """

    def __init__(self, state_dir: Optional[str] = None, project_root: Optional[str] = None):
        self.project_root = project_root or ROOT_DIR
        self.state_dir = state_dir or os.path.join(self.project_root, "state")
        self.trajectory_engine = TrajectoryEngine(state_dir=self.state_dir, project_root=self.project_root)

    def resolve_context(
        self,
        metadata: Optional[Dict[str, Any]] = None,
        user_text: str = "",
        transcript_path: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deterministically resolves target_agent, target_skill, capability, task, stage.
        NEVER uses generic default statistics-agent.
        """
        meta = metadata or {}

        # ---------------------------------------------------------------------
        # Tier 1: Explicit Caller Metadata
        # ---------------------------------------------------------------------
        target_agent = meta.get("target_agent")
        target_skill = meta.get("target_skill")
        capability = meta.get("capability")
        task = meta.get("task") or meta.get("milestone_id")
        stage = meta.get("stage") or meta.get("stage_id")
        project_id = meta.get("project_id", "academic_workspace")

        if target_agent and target_skill and capability and task and stage:
            return {
                "target_agent": target_agent,
                "target_skill": target_skill,
                "capability": capability,
                "task": task,
                "stage": stage,
                "project_id": project_id,
                "resolution_source": "EXPLICIT_METADATA"
            }

        # ---------------------------------------------------------------------
        # Tier 2: Active State Machine Inspection
        # ---------------------------------------------------------------------
        state_context = self._inspect_state_machine()
        if state_context:
            target_agent = target_agent or state_context.get("target_agent")
            target_skill = target_skill or state_context.get("target_skill")
            capability = capability or state_context.get("capability")
            task = task or state_context.get("task")
            stage = stage or state_context.get("stage")
            project_id = state_context.get("project_id", project_id)

            if target_agent and target_skill and capability and task and stage:
                return {
                    "target_agent": target_agent,
                    "target_skill": target_skill,
                    "capability": capability,
                    "task": task,
                    "stage": stage,
                    "project_id": project_id,
                    "resolution_source": "ACTIVE_STATE_MACHINE"
                }

        # ---------------------------------------------------------------------
        # Tier 3: Transcript Forensics (Recent Tool Calls)
        # ---------------------------------------------------------------------
        if transcript_path and os.path.isfile(transcript_path):
            transcript_context = self._inspect_transcript(transcript_path)
            if transcript_context:
                target_agent = target_agent or transcript_context.get("target_agent")
                target_skill = target_skill or transcript_context.get("target_skill")
                capability = capability or transcript_context.get("capability")
                task = task or transcript_context.get("task")
                stage = stage or transcript_context.get("stage")

                if target_agent and target_skill and capability and task and stage:
                    return {
                        "target_agent": target_agent,
                        "target_skill": target_skill,
                        "capability": capability,
                        "task": task,
                        "stage": stage,
                        "project_id": project_id,
                        "resolution_source": "TRANSCRIPT_FORENSICS"
                    }

        # ---------------------------------------------------------------------
        # Tier 4: Semantic Domain Mapping from User Critique Text / Category
        # ---------------------------------------------------------------------
        cat = category or self._classify_text_category(user_text)
        if cat and cat in DOMAIN_CAPABILITY_MAP:
            mapping = DOMAIN_CAPABILITY_MAP[cat]
            target_agent = target_agent or mapping["target_agent"]
            target_skill = target_skill or mapping["target_skill"]
            capability = capability or mapping["capability"]
            task = task or mapping["default_task"]
            stage = stage or mapping["default_stage"]

            return {
                "target_agent": target_agent,
                "target_skill": target_skill,
                "capability": capability,
                "task": task,
                "stage": stage,
                "project_id": project_id,
                "resolution_source": f"SEMANTIC_DOMAIN_MAPPING:{cat}"
            }

        # ---------------------------------------------------------------------
        # FAIL-CLOSED: Generic defaults are strictly prohibited
        # ---------------------------------------------------------------------
        raise UnresolvableFeedbackTargetError(
            f"Cannot route feedback without verified target capability. "
            f"User text: '{user_text[:80]}...'. "
            f"Generic defaults (e.g. statistics-agent) are strictly prohibited under Phase 16."
        )

    def _inspect_state_machine(self) -> Optional[Dict[str, Any]]:
        """Inspects state machine files for active milestone / stage."""
        candidates = [
            self.state_dir,
            os.path.join(self.project_root, "state"),
            os.path.join(self.project_root, "academic-state")
        ]
        for sdir in candidates:
            curr_file = os.path.join(sdir, "current_state.json")
            if os.path.isfile(curr_file):
                try:
                    with open(curr_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    milestones = data.get("milestones", {})
                    # Look for active milestone
                    for mid, mdata in milestones.items():
                        st = mdata.get("status", "")
                        if st in ["RUNNING", "VALIDATING", "AWAITING_APPROVAL", "READY"]:
                            agent = mdata.get("active_agent", "academic-orchestrator")
                            stage = mdata.get("current_stage", "active_stage")
                            cap = mdata.get("category") or mdata.get("capability") or "academic_research"
                            skill = mdata.get("skill") or self._skill_for_capability(cap)
                            return {
                                "task": mid,
                                "stage": stage,
                                "target_agent": agent,
                                "target_skill": skill,
                                "capability": cap,
                                "project_id": data.get("project_id", "academic_workspace")
                            }
                except Exception:
                    continue
        return None

    def _inspect_transcript(self, transcript_path: str) -> Optional[Dict[str, Any]]:
        """Extracts active capability and agent from recent tool calls in transcript.jsonl."""
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]
            for l in reversed(lines):
                rec = json.loads(l)
                if rec.get("type") == "PLANNER_RESPONSE":
                    tcs = rec.get("tool_calls", [])
                    for tc in reversed(tcs):
                        if not isinstance(tc, dict):
                            continue
                        t_name = tc.get("name", "")
                        t_args = tc.get("args", {})

                        if t_name == "run_command":
                            cmd = t_args.get("CommandLine", "")
                            m = re.search(r"\.agents/skills/([^/]+)/", cmd)
                            if m:
                                skill = m.group(1)
                                cap = skill.replace("-", "_")
                                agent = self._agent_for_skill(skill)
                                return {
                                    "target_agent": agent,
                                    "target_skill": skill,
                                    "capability": cap,
                                    "task": f"TASK_{cap.upper()}",
                                    "stage": f"stage_{skill}"
                                }

                        elif t_name == "invoke_subagent":
                            subagents = t_args.get("Subagents", [])
                            if subagents:
                                sa = subagents[-1]
                                agent = sa.get("TypeName", "academic-orchestrator")
                                return {
                                    "target_agent": agent,
                                    "target_skill": "academic-suite-orchestrator",
                                    "capability": "subagent_delegation",
                                    "task": "TASK_DELEGATION",
                                    "stage": "stage_delegation"
                                }

                        elif t_name in ["write_to_file", "replace_file_content"]:
                            target_f = t_args.get("TargetFile", "")
                            if "02_literature" in target_f:
                                return DOMAIN_CAPABILITY_MAP["EVIDENCE_CORRECTION"]
                            elif "06_hypothesis" in target_f or "chapter" in target_f:
                                return DOMAIN_CAPABILITY_MAP["WRITING_CORRECTION"]
        except Exception:
            pass
        return None

    def _classify_text_category(self, text: str) -> Optional[str]:
        """Infers feedback category from text patterns."""
        t_low = text.lower()
        if any(w in t_low for w in ["writing", "prose", "wording", "tone", "cliché", "robotic", "سطحی", "نگارش", "انشا"]):
            return "WRITING_CORRECTION"
        if any(w in t_low for w in ["citation", "reference", "source", "literature", "ارجاع", "منبع", "پیشینه"]):
            return "EVIDENCE_CORRECTION"
        if any(w in t_low for w in ["method", "design", "sampling", "power", "g*power", "روش", "طرح پژوهش", "نمونه‌گیری"]):
            return "METHODOLOGY_CORRECTION"
        if any(w in t_low for w in ["data", "cleaning", "outlier", "mcar", "missing", "داده", "پالایش", "پرت"]):
            return "DATA_ANALYSIS_CORRECTION"
        if any(w in t_low for w in ["table", "apa 7", "border", "leading zero", "italic", "جدول", "سه‌خطی", "ممیز"]):
            return "QUALITY_STYLE_CORRECTION"
        if any(w in t_low for w in ["statistic", "regression", "mediation", "sem", "anova", "آماری", "رگرسیون", "میانجی"]):
            return "STATISTICAL_CORRECTION"
        if any(w in t_low for w in ["integrity", "plagiarism", "irandoc", "فریب", "سرقت"]):
            return "RESEARCH_INTEGRITY_CORRECTION"
        if any(w in t_low for w in ["stage", "step", "halt", "wait", "confirm", "توقف", "مرحله"]):
            return "PROCESS_CORRECTION"
        return None

    def _skill_for_capability(self, cap: str) -> str:
        """Helper to map capability name to production skill."""
        for c_info in DOMAIN_CAPABILITY_MAP.values():
            if c_info["capability"] == cap:
                return c_info["target_skill"]
        return cap.replace("_", "-")

    def _agent_for_skill(self, skill: str) -> str:
        """Helper to map skill name to assigned agent."""
        for c_info in DOMAIN_CAPABILITY_MAP.values():
            if c_info["target_skill"] == skill:
                return c_info["target_agent"]
        if "stat" in skill or "regression" in skill or "mediation" in skill or "sem" in skill:
            return "statistics-agent"
        if "writ" in skill or "tone" in skill or "chapter" in skill:
            return "academic-writer"
        if "lit" in skill or "harvest" in skill:
            return "literature-expert"
        if "data" in skill:
            return "data-curator"
        return "academic-orchestrator"

    def emit_feedback_detected(
        self,
        feedback_record: Dict[str, Any],
        payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Emits USER_FEEDBACK_DETECTED event to TrajectoryEngine and state audit logs.
        """
        hook_payload = payload or {}
        event_details = {
            "feedback_id": feedback_record.get("feedback_id"),
            "target_agent": feedback_record.get("target_agent"),
            "target_skill": feedback_record.get("target_skill"),
            "capability": feedback_record.get("capability"),
            "task": feedback_record.get("task"),
            "stage": feedback_record.get("stage"),
            "correction": feedback_record.get("correction"),
            "desired_behavior": feedback_record.get("desired_behavior"),
            "scope": feedback_record.get("scope"),
            "severity": feedback_record.get("severity")
        }

        # 1. Trajectory Engine event
        self.trajectory_engine.record_event(
            event_type=TrajectoryEventType.USER_CORRECTION,
            payload=hook_payload,
            details=event_details,
            actor="user"
        )

        # 2. Activity Telemetry log
        act_dir = os.path.join(self.project_root, "learning", "telemetry")
        os.makedirs(act_dir, exist_ok=True)
        act_file = os.path.join(act_dir, "activity.jsonl")
        act_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "USER_FEEDBACK_DETECTED",
            "feedback_id": feedback_record.get("feedback_id"),
            "target_agent": feedback_record.get("target_agent"),
            "target_skill": feedback_record.get("target_skill"),
            "capability": feedback_record.get("capability"),
            "task": feedback_record.get("task"),
            "stage": feedback_record.get("stage")
        }
        with open(act_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(act_entry, ensure_ascii=False) + "\n")

        return act_entry


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Deterministic Feedback Router CLI")
    parser.add_argument("--text", type=str, required=True, help="User prompt text to analyze")
    parser.add_argument("--metadata", type=str, help="JSON metadata string")
    parser.add_argument("--transcript", type=str, help="Path to transcript.jsonl")
    args = parser.parse_args()

    router = FeedbackRouter()
    meta = json.loads(args.metadata) if args.metadata else {}
    res = router.resolve_context(metadata=meta, user_text=args.text, transcript_path=args.transcript)
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
