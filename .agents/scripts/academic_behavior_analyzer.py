#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_behavior_analyzer.py — AcademicSuite Observable Behavior Analyzer

Analyzes agent execution trajectories and trigger events (User Feedback or QC Failure)
to produce a deterministic, schema-validated root-cause diagnosis based strictly on
observable events (tool calls, arguments, outputs, files written, validator errors).

Key Principles:
1. Zero Chain-of-Thought Hallucination:
   - Does NOT guess internal model thoughts or inspect private reasoning tokens.
   - Grounded entirely in observable trajectory events:
     TOOL_CALLED, TOOL_RETURNED, FILE_READ, FILE_WRITTEN, COMMAND_STARTED,
     COMMAND_FINISHED, AGENT_INVOKED, AGENT_RETURNED, VALIDATION_STARTED,
     VALIDATION_FAILED, USER_CORRECTION.
2. Dual Trigger Support:
   - USER_FEEDBACK (via USER_FEEDBACK_DETECTED / FeedbackRecord)
   - QC_FAILURE (via VALIDATION_FAILED / validation report)
3. Deterministic Failure Signature Categorization:
   - Maps observable discrepancies to domain failure modes (e.g. REPORTING_P_ZERO,
     MISSING_PERSIAN_LEADING_ZERO, DICHOTOMIZING_CONTINUOUS_VARIABLE, etc.).
4. Schema Validation:
   - Produces reports conforming to contracts/evolution/behavior_analysis.schema.json.
"""

import os
import sys
import re
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

from contracts.contract_validator import validate_behavior_analysis


class BehaviorAnalysisError(Exception):
    """Base exception for behavior analysis errors."""
    pass


class PrivateCoTDetectedError(BehaviorAnalysisError):
    """Raised when private chain-of-thought keys are detected in trajectory or triggers."""
    pass


FORBIDDEN_COT_KEYS = {
    "chain_of_thought",
    "thinking",
    "internal_monologue",
    "scratchpad",
    "reasoning_tokens"
}


def sanitize_observable_only(obj: Any) -> Any:
    """Recursively checks and asserts that no private chain-of-thought tokens exist."""
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if k in FORBIDDEN_COT_KEYS:
                raise PrivateCoTDetectedError(
                    f"Forbidden private chain-of-thought key detected: '{k}'. "
                    f"Behavior analysis must strictly inspect observable actions and outputs."
                )
            cleaned[k] = sanitize_observable_only(v)
        return cleaned
    elif isinstance(obj, list):
        return [sanitize_observable_only(elem) for elem in obj]
    return obj


# Known domain failure signatures and observable regex / keyword indicators
FAILURE_SIGNATURE_RULES = [
    {
        "signature": "REPORTING_P_ZERO",
        "patterns": [r"\bp\s*=\s*\.?000\b", r"p\s*=\s*0\.000", r"p_equals_point_zero_zero_zero", r"zero p-value"],
        "diagnosis": "Reported p-value as exactly zero (p = .000), violating APA 7 / Persian reporting standards requiring p < .001 or ۰.۰۰۱ > p.",
        "prescribed": "Enforce strict p-value formatting: if software outputs .000, report strictly as 'p < .001' in English and '۰.۰۰۱ > p' in Persian."
    },
    {
        "signature": "MISSING_PERSIAN_LEADING_ZERO",
        "patterns": [r"missing_persian_leading_zero", r"(?<!\d)\.0[0-9]", r"حفظ صفر قبل از ممیز", r"بدون صفر قبل"],
        "diagnosis": "Omitted leading zero in Persian statistical text (e.g. writing .05 instead of ۰.۰۵), violating Persian academic typography.",
        "prescribed": "Preserve leading zero in Persian text (always write ۰.۰۵, ۰.۰۰۱); never drop zero before decimal dot in Persian."
    },
    {
        "signature": "MISSING_OMML_MATH",
        "patterns": [r"missing_omml_math", r"plain text equation", r"non-omml", r"omml_math_preserved.*false"],
        "diagnosis": "Output Word document contains plain text mathematical equations instead of native Word OMML (<m:oMath>) structures.",
        "prescribed": "Preserve Word OMML math equations by extracting text via elem.tag.endswith('}t') and avoiding paragraph.text overwrites."
    },
    {
        "signature": "DICHOTOMIZING_CONTINUOUS_VARIABLE",
        "patterns": [r"median_split", r"dichotomiz", r"median split", r"artificial dichotomization"],
        "diagnosis": "Dichotomized a continuous moderator via median split, causing severe loss of statistical power and variance deflation.",
        "prescribed": "Use continuous moderation modeling (PROCESS Model 1) with mean-centering, simple slopes at -1 SD/Mean/+1 SD, and Johnson-Neyman regions."
    },
    {
        "signature": "UNJUSTIFIED_MODEL_SELECTION",
        "patterns": [r"unjustified_model_selection", r"model_selection_without_comparison", r"lmm vs rm-anova", r"baron & kenny"],
        "diagnosis": "Selected statistical model without explicit empirical comparison against superior alternatives (e.g. RM-ANOVA vs LMM, Baron & Kenny vs bootstrap).",
        "prescribed": "Conduct explicit comparative model diagnostics (missingness patterns, covariance structures, bootstrap confidence intervals) before model selection."
    },
    {
        "signature": "SYNTHETIC_INTEGERS_IN_PRODUCTION",
        "patterns": [r"synthetic_integers", r"whole_integer_means", r"unrealistic decimal noise", r"integer mean"],
        "diagnosis": "Generated synthetic psychometric means as whole integers, violating Directive 9 realistic decimal noise injection.",
        "prescribed": "Inject bounded random empirical decimal noise into simulated means (mu_empirical = mu_target + delta, delta ~ Uniform(±0.08, ±0.25))."
    },
    {
        "signature": "VIOLATED_ASSUMPTION_IGNORED",
        "patterns": [r"homogeneity_of_slopes", r"mauchly", r"shapiro-wilk", r"levene", r"assumption_violation_ignored"],
        "diagnosis": "Proceeded with parametric inferential tests without checking or after violating core assumptions (e.g. slope homogeneity in ANCOVA).",
        "prescribed": "Execute mandatory parametric assumption verification sequence prior to reporting inferential tests."
    },
    {
        "signature": "UNENGAGED_RESPONSE_IGNORED",
        "patterns": [r"straight-lining", r"unengaged_response", r"zero variance response", r"careless_responding"],
        "diagnosis": "Failed to screen or filter unengaged or straight-lining responses before psychometric aggregation.",
        "prescribed": "Execute data quality audit screening for invariant responses, Little's MCAR missingness patterns, and Mahalanobis D2 outliers."
    },
    {
        "signature": "FORBIDDEN_AI_CLICHE",
        "patterns": [r"شایان ذکر است", r"لازم به ذکر است", r"پرواضح است", r"delve into", r"tapestry of"],
        "diagnosis": "Used forbidden robotic AI cliché in Persian academic narrative, violating authentic scholarly tone standards.",
        "prescribed": "Eliminate formulaic robotic AI clichés and enforce scholarly Persian cadence and formal register."
    }
]


class AcademicBehaviorAnalyzer:
    """
    Analyzes observable trajectory actions and trigger events to produce
    a structured, schema-compliant BehaviorAnalysisReport.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or ROOT_DIR)
        cand_learning = os.path.join(self.base_dir, ".agents", "learning")
        learning_base = cand_learning if os.path.isdir(cand_learning) else os.path.join(self.base_dir, "learning")
        self.analysis_dir = os.path.join(learning_base, "analysis")
        os.makedirs(self.analysis_dir, exist_ok=True)

    def analyze(
        self,
        trajectory_data: Dict[str, Any],
        trigger_type: str,
        trigger_payload: Dict[str, Any],
        trigger_event_id: Optional[str] = None,
        existing_skill_content: Optional[str] = None,
        relevant_knowledge: Optional[List[Dict[str, Any]]] = None,
        target_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes root-cause diagnosis on observable trajectory and trigger.

        Args:
            trajectory_data: Trajectory dictionary containing ordered_actions, tool_usages, outputs, etc.
            trigger_type: Either "USER_FEEDBACK" or "QC_FAILURE".
            trigger_payload: FeedbackRecord dict or validation failure dict.
            trigger_event_id: Optional event ID pointer.
            existing_skill_content: Optional raw content of target SKILL.md or agent.md.
            relevant_knowledge: Optional list of retrieved lessons, anti-patterns, or exemplars.

        Returns:
            Validated BehaviorAnalysisReport dict.
        """
        # 1. Enforce observable-only invariant (Zero CoT)
        sanitize_observable_only(trajectory_data)
        sanitize_observable_only(trigger_payload)

        norm_trigger_type = trigger_type.upper().strip()
        if norm_trigger_type not in ["USER_FEEDBACK", "QC_FAILURE"]:
            raise BehaviorAnalysisError(f"Invalid trigger_type '{trigger_type}'. Must be 'USER_FEEDBACK' or 'QC_FAILURE'.")

        # 2. Extract target metadata
        target_agent = (
            trigger_payload.get("target_agent")
            or trajectory_data.get("agent")
            or "statistics-agent"
        )
        target_skill = (
            trigger_payload.get("target_skill")
            or trajectory_data.get("skill")
            or "statistical-data-analyst"
        )
        capability = (
            trigger_payload.get("capability")
            or trigger_payload.get("target_capability")
            or target_skill
        )
        task_context = {
            "task_id": trigger_payload.get("task") or trajectory_data.get("task_id", "TASK_UNKNOWN"),
            "stage_id": trigger_payload.get("stage") or trajectory_data.get("stage_id", "STAGE_UNKNOWN"),
            "milestone_id": trigger_payload.get("milestone_id") or trajectory_data.get("milestone_id", "M_UNKNOWN"),
            "prompt": trigger_payload.get("prompt") or trajectory_data.get("prompt", "")
        }

        traj_id = trajectory_data.get("trajectory_id") or f"TRJ-{uuid.uuid4().hex[:8].upper()}"
        evt_id = trigger_event_id or trigger_payload.get("event_id") or trigger_payload.get("feedback_id") or f"EVT-{uuid.uuid4().hex[:8].upper()}"

        # 3. Locate observable failure step
        failure_step, failure_sig, diagnosis, prescribed = self._diagnose_observable_defect(
            trajectory_data=trajectory_data,
            trigger_type=norm_trigger_type,
            trigger_payload=trigger_payload
        )

        # 4. Perform candidate gap diagnosis across the 7 categories
        candidate_diagnosis = self._diagnose_candidate_gap(
            trajectory_data=trajectory_data,
            trigger_type=norm_trigger_type,
            trigger_payload=trigger_payload,
            failure_step=failure_step,
            failure_sig=failure_sig,
            diagnosis=diagnosis,
            prescribed=prescribed,
            existing_skill_content=existing_skill_content,
            relevant_knowledge=relevant_knowledge or [],
            target_category=target_category
        )

        analysis_id = f"BAN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()

        report = {
            "contract_version": "1.0.0",
            "analysis_id": analysis_id,
            "trigger_type": norm_trigger_type,
            "trigger_event_id": evt_id,
            "target_agent": target_agent,
            "target_skill": target_skill,
            "capability": capability,
            "task_context": task_context,
            "trajectory_id": traj_id,
            "observable_failure_step": failure_step,
            "failure_signature": failure_sig,
            "root_cause_diagnosis": diagnosis,
            "prescribed_behavior": prescribed,
            "created_at": now_iso,
            "metadata": {
                "analyzed_by": "AcademicBehaviorAnalyzer",
                "trajectory_step_count": len(trajectory_data.get("ordered_actions", [])),
                "candidate_diagnosis": candidate_diagnosis
            }
        }

        # 5. Schema validation
        val = validate_behavior_analysis(report)
        if not val.get("valid"):
            raise BehaviorAnalysisError(f"BehaviorAnalysisReport failed schema validation: {val.get('errors')}")

        # 6. Persist to disk
        out_path = os.path.join(self.analysis_dir, f"{analysis_id}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report

    def _diagnose_observable_defect(
        self,
        trajectory_data: Dict[str, Any],
        trigger_type: str,
        trigger_payload: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], str, str, str]:
        """
        Pinpoints the observable action where the defect occurred and determines
        the failure signature, diagnosis, and prescribed behavior.
        """
        actions = trajectory_data.get("ordered_actions", [])

        # Aggregate text signals from trigger
        trigger_text = ""
        if trigger_type == "USER_FEEDBACK":
            trigger_text = f"{trigger_payload.get('correction', '')} {trigger_payload.get('desired_behavior', '')} {trigger_payload.get('feedback_text', '')}"
        else:  # QC_FAILURE
            errors = trigger_payload.get("errors", [])
            failed_assertions = trigger_payload.get("failed_assertions", [])
            summary = trigger_payload.get("summary", "")
            trigger_text = f"{summary} {' '.join(errors)} {' '.join(failed_assertions)}"

        # Search for known failure signature
        detected_rule = None
        for rule in FAILURE_SIGNATURE_RULES:
            for pat in rule["patterns"]:
                if re.search(pat, trigger_text, re.IGNORECASE):
                    detected_rule = rule
                    break
            if detected_rule:
                break

        # Fallback signature if no specific rule matched
        if not detected_rule:
            detected_rule = {
                "signature": "GENERAL_METHODOLOGICAL_DEFECT",
                "diagnosis": f"Observable defect identified from trigger: {trigger_text[:120].strip() or 'Defect in task execution.'}",
                "prescribed": "Adhere strictly to domain guidelines and verify task requirements against evaluation checklist."
            }

        # Locate specific step in trajectory
        matched_step = None
        if actions:
            # Check actions in reverse (most recent first) for matching output, command, or error
            for act in reversed(actions):
                act_str = json.dumps(act, ensure_ascii=False).lower()
                for pat in detected_rule.get("patterns", []):
                    if re.search(pat, act_str, re.IGNORECASE):
                        matched_step = act
                        break
                if matched_step:
                    break

            # If no step matched specifically, pick the last action as the manifestation point
            if not matched_step:
                matched_step = actions[-1]

        if not matched_step:
            failure_step = {
                "step_number": 1,
                "action_type": "OBSERVED_DEFECT",
                "tool_name": "unknown",
                "command_or_input": trigger_payload.get("task", "task_execution"),
                "output_or_error": trigger_text[:200],
                "description": f"Observable defect manifested during task execution: {detected_rule['signature']}"
            }
        else:
            failure_step = {
                "step_number": matched_step.get("step_number", 1),
                "action_type": matched_step.get("action_type", "TOOL_CALLED"),
                "tool_name": matched_step.get("tool_name") or matched_step.get("actor", "agent"),
                "command_or_input": matched_step.get("observable_input") or matched_step.get("command", {}),
                "output_or_error": matched_step.get("observable_output") or matched_step.get("error", trigger_text[:200]),
                "description": matched_step.get("description") or f"Action exhibited defect signature: {detected_rule['signature']}"
            }

        return failure_step, detected_rule["signature"], detected_rule["diagnosis"], detected_rule["prescribed"]

    def _diagnose_candidate_gap(
        self,
        trajectory_data: Dict[str, Any],
        trigger_type: str,
        trigger_payload: Dict[str, Any],
        failure_step: Dict[str, Any],
        failure_sig: str,
        diagnosis: str,
        prescribed: str,
        existing_skill_content: Optional[str] = None,
        relevant_knowledge: Optional[List[Dict[str, Any]]] = None,
        target_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes a candidate gap diagnosis mapping the observable failure to one of the 7 target categories:
        1. agent instruction
        2. Skill
        3. decision tree
        4. verification rule
        5. delegation rule
        6. retrieval rule
        7. exception rule
        """
        # Aggregate text signals
        trigger_text = ""
        if trigger_type == "USER_FEEDBACK":
            trigger_text = f"{trigger_payload.get('correction', '')} {trigger_payload.get('desired_behavior', '')} {trigger_payload.get('feedback_text', '')}"
        else:
            errors = trigger_payload.get("errors", [])
            failed_assertions = trigger_payload.get("failed_assertions", [])
            summary = trigger_payload.get("summary", "")
            trigger_text = f"{summary} {' '.join(errors)} {' '.join(failed_assertions)}"

        lower_text = trigger_text.lower()
        lower_sig = failure_sig.lower()

        # Categorize into the 7 target modification categories (if not explicitly overridden)
        resolved_category = target_category
        if not resolved_category:
            if any(w in lower_text or w in lower_sig for w in ["unjustified_model", "model_selection", "decision tree", "lmm vs rm-anova", "baron & kenny", "model comparison", "which model"]):
                resolved_category = "decision tree"
            elif any(w in lower_text or w in lower_sig for w in ["p_zero", "reporting_p", "leading_zero", "omml", "verification", "pre-flight", "check", "violated_assumption", "slope", "normality", "levene", "mauchly"]):
                resolved_category = "verification rule"
            elif any(w in lower_text or w in lower_sig for w in ["delegate", "delegation", "subagent", "role", "orchestrator", "handoff"]):
                resolved_category = "delegation rule"
            elif any(w in lower_text or w in lower_sig for w in ["retrieval", "retrieve", "context", "questionnaire", "scale key", "scoring key", "exemplar", "citation"]):
                resolved_category = "retrieval rule"
            elif any(w in lower_text or w in lower_sig for w in ["unengaged", "straight-lining", "synthetic_integer", "missingness", "mcar", "outlier", "exception", "dropout", "attrition", "boundary"]):
                resolved_category = "exception rule"
            elif any(w in lower_text or w in lower_sig for w in ["cliche", "tone", "persona", "academic register", "half-space", "prompt"]):
                resolved_category = "agent instruction"
            else:
                resolved_category = "Skill"

        # Inspect existing skill content to identify affected section
        affected_section = "General Procedures"
        if existing_skill_content:
            headings = re.findall(r"^#{1,3}\s+(.+)$", existing_skill_content, re.MULTILINE)
            for h in headings:
                h_lower = h.lower()
                if resolved_category == "decision tree" and any(k in h_lower for k in ["decision", "selection", "model"]):
                    affected_section = h
                    break
                elif resolved_category == "verification rule" and any(k in h_lower for k in ["verification", "check", "reporting", "standards"]):
                    affected_section = h
                    break
                elif resolved_category == "delegation rule" and any(k in h_lower for k in ["delegation", "roles", "subagent"]):
                    affected_section = h
                    break
                elif resolved_category == "retrieval rule" and any(k in h_lower for k in ["retrieval", "context", "inputs", "references"]):
                    affected_section = h
                    break
                elif resolved_category == "exception rule" and any(k in h_lower for k in ["exception", "assumptions", "missing", "data", "quality"]):
                    affected_section = h
                    break
                elif resolved_category == "agent instruction" and any(k in h_lower for k in ["identity", "tone", "constitution", "directives"]):
                    affected_section = h
                    break
            if affected_section == "General Procedures" and headings:
                for h in headings:
                    if any(k in h.lower() for k in ["procedure", "workflow", "execution", "directive", "instruction"]):
                        affected_section = h
                        break

        # Incorporate relevant knowledge items
        knowledge_lessons = []
        if relevant_knowledge:
            for item in relevant_knowledge:
                item_desc = item.get("what_happened") or item.get("statement") or item.get("name") or ""
                if item_desc:
                    knowledge_lessons.append(item_desc)

        counterfactual = (
            f"Instead of {failure_step.get('action_type', 'action')} causing '{failure_sig}', "
            f"the execution should have followed '{prescribed}'."
        )

        # Formulate conditional resolution: WHEN X -> A, WHEN Y -> B, EXCEPT Z -> C (Phase 24)
        conditional_resolution = (
            f"WHEN standard baseline assumptions hold → use primary approach ({prescribed}); "
            f"WHEN complex data structures (multi-wave/missingness) present → use robust alternative; "
            f"EXCEPT when {failure_sig} or boundary violation occurs → use alternative remediation."
        )

        return {
            "target_category": resolved_category,
            "diagnosed_gap": f"Missing or ambiguous {resolved_category} in '{affected_section}': {diagnosis}",
            "affected_section": affected_section,
            "prescribed_behavior": prescribed,
            "proposed_resolution": conditional_resolution,
            "counterfactual": counterfactual,
            "evidence_sources": [
                f"Observable Failure: {failure_sig}",
                f"Observed Step: Step {failure_step.get('step_number', 1)} ({failure_step.get('tool_name', 'tool')})",
                f"Trigger Diagnostic: {trigger_text[:120].strip()}"
            ] + knowledge_lessons[:3]
        }


if __name__ == "__main__":
    analyzer = AcademicBehaviorAnalyzer()
    sample_traj = {
        "trajectory_id": "TRJ-DEMO-001",
        "agent": "statistics-agent",
        "skill": "statistical-data-analyst",
        "ordered_actions": [
            {
                "step_number": 1,
                "action_type": "TOOL_CALLED",
                "actor": "statistics-agent",
                "tool_name": "run_command",
                "observable_input": {"command": "python3 run_ancova.py"},
                "observable_output": {"result": "F = 5.23, p = .000"},
                "description": "Executed ANCOVA without checking slope homogeneity."
            }
        ]
    }
    sample_trigger = {
        "feedback_id": "FDB-DEMO-001",
        "target_agent": "statistics-agent",
        "target_skill": "statistical-data-analyst",
        "capability": "ancova",
        "task": "hypothesis_1",
        "stage": "06_hypothesis_1",
        "correction": "You reported p = .000 which is forbidden, and did not check homogeneity of slopes.",
        "desired_behavior": "Report p < .001 (or ۰.۰۰۱ > p) and verify regression slope homogeneity."
    }
    res = analyzer.analyze(
        trajectory_data=sample_traj,
        trigger_type="USER_FEEDBACK",
        trigger_payload=sample_trigger
    )
    print(json.dumps(res, indent=2, ensure_ascii=False))
