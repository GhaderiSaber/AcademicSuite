#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
academic_correction_detector.py — Automatic Detection of Meaningful User Corrections

Recognizes when a user teaches or corrects the agent during ordinary conversation
without requiring explicit "/learn" or manual learning commands.

Captures corrections into:
    learning/experience/feedback/
        ├── <feedback-id>.json
        └── index.jsonl

Key Invariants:
1. Strictly distinguishes:
   - PROJECT_SPECIFIC: applies only to current study/thesis context.
   - REUSABLE_PROCEDURAL: actionable procedural guidance across multiple tasks.
   - POTENTIAL_GLOBAL_INVARIANT: system-level constitutional or methodological axioms.
2. Generates a feedback contract and an unpromoted generalization candidate.
   NEVER directly modifies Skills or production prompts.
3. Detects repeated corrections via normalized pattern signature hashes.
4. Records and tracks false positives for evaluation without history deletion.
"""

import os
import sys
import re
import json
import uuid
import hashlib
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

# Virtualenv auto-discovery shim
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

# Contract validation integration
try:
    from contracts.contract_validator import (
        validate_feedback,
        ContractValidationError
    )
except ImportError:
    validate_feedback = None
    ContractValidationError = Exception


# ==============================================================================
# Category Detection Rules & Patterns
# ==============================================================================

CATEGORY_PATTERNS: List[Tuple[str, str, List[str]]] = [
    (
        "RESEARCH_INTEGRITY_CORRECTION",
        "validation-agent",
        [
            r"doesn'?t match (?:the )?output",
            r"table doesn'?t match",
            r"numbers? don'?t match",
            r"never report a statistic that cannot be traced",
            r"cannot be traced to a reproducible",
            r"reproducible execution artifact",
            r"fabricat",
            r"unverified (?:numbers?|statistics?|values?)",
            r"p-hack",
            r"hallucinat",
            r"ارقام با خروجی همخوانی ندارند",
            r"داده‌سازی",
            r"تکرارپذیر نیست"
        ]
    ),
    (
        "DATA_ANALYSIS_CORRECTION",
        "data-curator",
        [
            r"forgot to check missingness",
            r"check missingness",
            r"missing data pattern",
            r"little'?s mcar",
            r"reverse[- ]cod",
            r"straight[- ]lining",
            r"screen (?:for )?outliers",
            r"outlier detection",
            r"mahalanobis",
            r"imput(?:ation|e)",
            r"فراموش کردی گمشدگی",
            r"داده‌های گمشده",
            r"کدگذاری معکوس",
            r"داده‌های پرت"
        ]
    ),
    (
        "METHODOLOGY_CORRECTION",
        "methodology-expert",
        [
            r"method is not appropriate",
            r"not appropriate here",
            r"don'?t say the treatment caused",
            r"unless the design supports it",
            r"threats? to internal validity",
            r"unmeasured confounding",
            r"quasi[- ]experimental",
            r"experimental design",
            r"control group",
            r"sampling bias",
            r"random assignment",
            r"g\*power",
            r"sample size",
            r"sampling",
            r"این روش مناسب نیست",
            r"نمی‌توانی ادعای علّی کنی",
            r"طرح تحقیق",
            r"گروه کنترل"
        ]
    ),
    (
        "STATISTICAL_CORRECTION",
        "statistics-agent",
        [
            r"need to compare these two models",
            r"compare (?:these )?(?:two )?models",
            r"verify the effect size",
            r"effect size is wrong",
            r"wrong estimator",
            r"use wlsmv",
            r"normality assumption",
            r"degrees of freedom mismatch",
            r"df does not match",
            r"multicollinearity",
            r"vif threshold",
            r"bca bootstrap",
            r"باید این دو مدل را مقایسه کنی",
            r"اندازه اثر را بررسی کن",
            r"برآوردگر اشتباه است",
            r"درجات آزادی"
        ]
    ),
    (
        "WRITING_CORRECTION",
        "academic-writer",
        [
            r"writing is too superficial",
            r"too superficial",
            r"use this exact wording",
            r"avoid cliché",
            r"robotic tone",
            r"flattery",
            r"expand on the (?:psychological )?mechanisms",
            r"in-depth discussion",
            r"نگارش بسیار سطحی است",
            r"از این عبارت دقیق استفاده کن",
            r"کلیشه‌ای",
            r"سازوکارهای روان‌شناختی را بسط بده"
        ]
    ),
    (
        "EVIDENCE_CORRECTION",
        "literature-expert",
        [
            r"where is the citation",
            r"reference doesn'?t support",
            r"ghost citation",
            r"citation needed",
            r"outdated literature",
            r"literature concordance",
            r"ارجاع کجاست",
            r"منبع این ادعا را ذکر کن",
            r"ادبیات پژوهش"
        ]
    ),
    (
        "COMPLETENESS_CORRECTION",
        "academic-orchestrator",
        [
            r"you forgot (?:to include )?(?:table|section|appendix|figure)",
            r"missing (?:the )?(?:table|section|demographic|limitations|implications)",
            r"incomplete deliverable",
            r"you left out",
            r"جدول .* را فراموش کردی",
            r"بخش محدودیت‌ها وجود ندارد",
            r"ناقص است"
        ]
    ),
    (
        "PROCESS_CORRECTION",
        "academic-orchestrator",
        [
            r"stop here before continuing",
            r"wait for (?:my )?confirmation",
            r"don'?t skip stages",
            r"run assumption check before",
            r"interactive stage-gate",
            r"قبل از ادامه توقف کن",
            r"منتظر تایید بمان",
            r"مراحل را رد نکن"
        ]
    ),
    (
        "QUALITY_STYLE_CORRECTION",
        "results-auditor",
        [
            r"leading zero",
            r"leading zeros in persian",
            r"three[- ]line table",
            r"apa 7 (?:table|format)",
            r"italicize statistical symbols",
            r"half[- ]space",
            r"نیم[- ]فاصله",
            r"صفر قبل از ممیز",
            r"جدول سه‌خطی"
        ]
    )
]

# Teaching and correction trigger markers
CORRECTION_TRIGGER_PATTERNS = [
    r"\byou (?:forgot|need to|should have|must|ought to|didn'?t)\b",
    r"\balways (?:report|use|include|check|calculate)\b",
    r"\bthis (?:is not|isn'?t|method is not|writing is too|table doesn'?t|result doesn'?t)\b",
    r"\bdon'?t (?:say|claim|use|omit|forget)\b",
    r"\bnever (?:report|use|claim|skip)\b",
    r"\bincorrect\b|\bwrong\b|\bflawed\b|\bmismatch\b",
    r"\brevise (?:this|the)\b|\bcorrect (?:this|the)\b",
    r"\b(?:use|write|replace with) this exact\b",
    r"\b(?:where is the citation|reference doesn'?t support|citation (?:needed|missing)|ghost citation)\b",
    r"فراموش کردی|باید|نباید|اشتباه است|نادرست است|اصلاح کن|دقت کن"
]

# Epistemic Methodological Blacklist (ATK-02 & ATK-14 Hardening: Experience is Evidence, Not Truth)
EPISTEMIC_METHODOLOGICAL_BLACKLIST = [
    (
        "SOBEL_MEDIATION_OVER_BOOTSTRAP",
        r"\b(?:sobel (?:test|z|formula)|never use bootstrap|only use sobel|use sobel instead)\b",
        "Sobel's test assumes normal distribution of the indirect effect (ab), which is severely flawed and underpowered. Modern methodological consensus (Preacher & Hayes 2004, 2008; Hayes 2018) mandates 5,000 bootstrap BCa resamples."
    ),
    (
        "POST_HOC_POWER_CALCULATION",
        r"\b(?:post[- ]hoc power|observed power|retrospective power|calculate power after non-significant)\b",
        "Post-hoc (observed) power is mathematically fallacious because it is a 1-to-1 transformation of the p-value and provides zero additional inferential information (Hoenig & Heisey, 2001; Levine & Ensom, 2001)."
    ),
    (
        "MEDIAN_SPLIT_DICHOTOMIZATION",
        r"\b(?:median split|dichotomiz(?:e|ation)|split continuous into (?:high|low))\b",
        "Dichotomizing continuous variables via median split discards statistical variance, loses up to 50% of statistical power, and inflates spurious interaction significance (MacCallum et al., 2002; Iacobucci et al., 2015)."
    ),
    (
        "STEPWISE_REGRESSION_FOR_EXPLANATION",
        r"\b(?:stepwise regression|automated variable selection|forward selection|backward elimination)\b",
        "Stepwise regression produces severe p-value inflation, biased parameter estimates, and fails under collinearity; prohibited for explanatory theory testing (Whittingham et al., 2006)."
    ),
    (
        "STRIP_LEADING_ZERO_IN_PERSIAN",
        r"\b(?:remove leading zero in persian|delete zero before decimal in persian|حذف صفر قبل از ممیز)\b",
        "Persian typography strictly mandates retaining the leading zero before decimals (۰.۰۰۱ > p, ۰.۰۵) under Directive 4."
    ),
    (
        "BLIND_LISTWISE_DELETION_ATTRITION",
        r"\b(?:always delete missing rows|just drop missing cases in longitudinal|complete case analysis for all)\b",
        "Complete-case listwise deletion under longitudinal attrition violates MAR assumptions and introduces severe selection bias."
    )
]

PROJECT_SPECIFIC_PATTERNS = [
    r"\bin this thesis\b",
    r"\bin my thesis\b",
    r"\bin this dissertation\b",
    r"\bfor this study\b",
    r"\bfor this project\b",
    r"\bfor the tehran sample\b",
    r"\bin table \d+-\d+ of (?:this|my)\b",
    r"\buse this exact wording in this\b",
    r"\bthis specific participant\b",
    r"\b(?:department|committee|faculty|institution|university|advisor|supervisor|hospital|clinic)\b",
    r"\b(?:wants|requires|mandates|rules? for|guidelines? for)\b",
    r"\b(?:purple|blue|green|red) (?:headers?|borders?|colors?)\b",
    r"\b(?:4|four|5|five) decimal places?\b",
    r"در این پایان[‌ ]?نامه|در این رساله|برای این پژوهش|در این مطالعه|دانشکده|کمیته|استاد راهنما|دستورالعمل دانشگاه"
]

GLOBAL_INVARIANT_PATTERNS = [
    r"\bnever report a statistic that cannot be traced\b",
    r"\breproducible execution artifact\b",
    r"\bdon'?t say the treatment caused this unless the design supports it\b",
    r"\bzero (?:hallucinations?|defensive rationalization)\b",
    r"\bnever (?:fabricate|hallucinate|claim causality without|bypass validation)\b",
    r"\balways strictly enforce\b",
    r"هیچ[‌ ]?گاه آماره‌ای که قابل ردیابی نیست گزارش نکن|بدون طرح آزمایشی ادعای علّی نکن"
]


def clean_text(text: str) -> str:
    """Removes HTML and XML tags and trims whitespace."""
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", "", text)
    return cleaned.strip()


class AcademicCorrectionDetector:
    """
    Non-intrusive detector of meaningful user corrections and teaching signals.
    Persists structured feedback and unpromoted generalization candidates.
    """

    def __init__(self, store_dir: Optional[str] = None, project_root: Optional[str] = None, base_dir: Optional[str] = None):
        self.project_root = project_root or base_dir or ROOT_DIR
        if store_dir:
            self.store_dir = os.path.abspath(store_dir)
        else:
            self.store_dir = os.path.join(self.project_root, "learning", "experience", "feedback")

        os.makedirs(self.store_dir, exist_ok=True)
        self.candidates_dir = os.path.join(self.store_dir, "candidates")
        os.makedirs(self.candidates_dir, exist_ok=True)
        self.index_file = os.path.join(self.store_dir, "index.jsonl")

    def detect_correction(
        self,
        user_text: str,
        assistant_context: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        current_agent: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Analyzes user text to determine if it constitutes an instructional correction.
        Returns a validated AcademicFeedbackContract dict with generalization candidate,
        or None if no correction is detected.
        """
        cleaned = clean_text(user_text)
        if len(cleaned) < 8:
            return None

        text_lower = cleaned.lower()
        meta = metadata or {}
        if current_agent:
            meta.setdefault("current_agent", current_agent)

        # 0. Check Epistemic Methodological Blacklist (ATK-02 & ATK-14 Hardening)
        for bl_code, bl_pattern, bl_reason in EPISTEMIC_METHODOLOGICAL_BLACKLIST:
            if re.search(bl_pattern, text_lower):
                now_iso = datetime.now(timezone.utc).isoformat()
                return {
                    "contract_version": "1.0.0",
                    "feedback_id": f"FDB-DISCREDITED-{uuid.uuid4().hex[:6].upper()}",
                    "is_correction": True,
                    "is_discredited_methodology": True,
                    "blacklist_code": bl_code,
                    "blacklist_reason": bl_reason,
                    "discredited_citation": bl_reason,
                    "source": {"origin": "HUMAN_SUPERVISOR", "identifier": meta.get("user_identifier", "User")},
                    "type": "DISCREDITED_METHODOLOGY_ATTEMPT",
                    "target_agent": "academic-challenger",
                    "target_skill": "methodology-review",
                    "capability": "research_methodology",
                    "task": meta.get("task") or meta.get("milestone_id") or "ACTIVE_MILESTONE",
                    "stage": meta.get("stage") or meta.get("stage_id") or "active_stage",
                    "correction": cleaned,
                    "desired_behavior": f"Do not use discredited methodology: {bl_reason}",
                    "scope": "DISCREDITED_REJECTED",
                    "severity": "CRITICAL",
                    "timestamp": now_iso,
                    "correction_statement": cleaned
                }

        # 0.1 Check conversational / rhetorical questions (ATK-12 Hardening)
        if cleaned.endswith("?") and not any(re.search(pat, text_lower) for pat in [r"\byou must\b", r"\byou should have\b", r"\bnever\b", r"\balways\b"]):
            return None
        if re.search(r"\b(?:don'?t you think|what do you think|is it possible|could it be)\b", text_lower):
            return None

        # 1. Check trigger markers
        has_trigger = any(re.search(pat, text_lower) for pat in CORRECTION_TRIGGER_PATTERNS)
        if not has_trigger:
            return None

        # 2. Categorization
        detected_category = "METHODOLOGY_CORRECTION"
        target_agent = "academic-orchestrator"
        matched = False

        for cat, agent_hint, patterns in CATEGORY_PATTERNS:
            if any(re.search(pat, text_lower) for pat in patterns):
                detected_category = cat
                target_agent = agent_hint
                matched = True
                break

        # 4. Deterministic Context Resolution via FeedbackRouter (Zero Generic Defaults)
        from scripts.academic_feedback_router import FeedbackRouter
        router = FeedbackRouter(
            state_dir=os.path.join(self.project_root, "state"),
            project_root=self.project_root
        )

        if not matched:
            inferred_cat = router._classify_text_category(cleaned)
            if inferred_cat:
                detected_category = inferred_cat
            else:
                detected_category = None

        # 3. Scope Resolution
        # Check Project-Specific vs Potential Global Invariant vs Reusable Procedural
        is_project_specific = any(re.search(pat, text_lower) for pat in PROJECT_SPECIFIC_PATTERNS)
        is_global_invariant = any(re.search(pat, text_lower) for pat in GLOBAL_INVARIANT_PATTERNS)

        if is_project_specific:
            resolved_scope = "PROJECT_SPECIFIC"
        elif is_global_invariant:
            resolved_scope = "POTENTIAL_GLOBAL_INVARIANT"
        else:
            resolved_scope = "REUSABLE_PROCEDURAL"

        meta = metadata or {}
        source_transcript = meta.get("source_transcript_path", "")
        resolved_ctx = router.resolve_context(
            metadata=meta,
            user_text=cleaned,
            transcript_path=source_transcript,
            category=detected_category
        )

        target_agent = resolved_ctx["target_agent"]
        target_skill = resolved_ctx["target_skill"]
        capability = resolved_ctx["capability"]
        task = resolved_ctx["task"]
        stage = resolved_ctx["stage"]
        project_id = resolved_ctx.get("project_id", meta.get("project_id", "academic_workspace"))

        # 5. Extract Desired Behavior & Correction statement
        correction_statement = cleaned
        desired_behavior = self._derive_desired_behavior(cleaned, detected_category, resolved_scope)

        # 6. Signature Hash for Repetition Tracking
        sig_raw = f"{detected_category}::{self._normalize_for_hash(cleaned)}"
        sig_hash = hashlib.sha256(sig_raw.encode("utf-8")).hexdigest()[:16]

        # Calculate repetition count from index
        prior_repetition_count = self._get_signature_repetition_count(sig_hash)
        current_repetition_count = prior_repetition_count + 1

        # IDs
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()
        date_str = now_dt.strftime("%Y%m%d")
        rand_suffix = uuid.uuid4().hex[:6].upper()

        feedback_id = f"FDB-{date_str}-{rand_suffix}"
        candidate_id = f"CAND-{date_str}-{sig_hash[:6].upper()}-{rand_suffix}"
        turn_index = meta.get("turn_index")

        feedback_payload = {
            "contract_version": "1.0.0",
            "feedback_id": feedback_id,
            "is_correction": True,
            "is_project_specific": is_project_specific,
            "source": {
                "origin": "HUMAN_SUPERVISOR",
                "identifier": meta.get("user_identifier", "GhaderiSaber")
            },
            "type": detected_category,
            "target_agent": target_agent,
            "target_skill": target_skill,
            "capability": capability,
            "task": task,
            "stage": stage,
            "correction": correction_statement,
            "desired_behavior": desired_behavior,
            "scope": resolved_scope,
            "severity": "CRITICAL" if resolved_scope == "POTENTIAL_GLOBAL_INVARIANT" else ("HIGH" if resolved_scope == "REUSABLE_PROCEDURAL" else "MEDIUM"),
            "timestamp": now_iso,
            "context": {
                "project_id": project_id,
                "milestone_id": task,
                "stage_id": stage,
                "capability": capability,
                "task": task,
                "stage": stage,
                "source_transcript_path": source_transcript,
                "turn_index": turn_index if isinstance(turn_index, int) else None,
                "related_artifact_paths": meta.get("related_artifact_paths", [])
            },
            "generalization_candidate": {
                "candidate_id": candidate_id,
                "suggested_rule": desired_behavior,
                "suggested_target_skill": target_skill,
                "scope": resolved_scope,
                "repetition_count": current_repetition_count,
                "signature_hash": sig_hash,
                "evaluation_status": "PENDING"
            }
        }

        # Clean null values in context
        if feedback_payload["context"]["turn_index"] is None:
            del feedback_payload["context"]["turn_index"]
        if not feedback_payload["context"]["source_transcript_path"]:
            del feedback_payload["context"]["source_transcript_path"]

        # Validate against schema
        if validate_feedback is not None:
            val_res = validate_feedback(feedback_payload)
            if not val_res.get("valid"):
                sys.stderr.write(f"[AcademicCorrectionDetector] Warning: Feedback validation failed: {val_res.get('error')}\n")

        return feedback_payload

    def record_feedback(self, feedback_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Persists the feedback record and updates index.jsonl."""
        feedback_id = feedback_payload["feedback_id"]
        out_path = os.path.join(self.store_dir, f"{feedback_id}.json")

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(feedback_payload, f, indent=2, ensure_ascii=False)

        # Append to index.jsonl
        candidate_info = feedback_payload.get("generalization_candidate", {})
        index_entry = {
            "feedback_id": feedback_id,
            "type": feedback_payload.get("type"),
            "scope": feedback_payload.get("scope"),
            "target_agent": feedback_payload.get("target_agent"),
            "target_skill": feedback_payload.get("target_skill"),
            "signature_hash": candidate_info.get("signature_hash"),
            "repetition_count": candidate_info.get("repetition_count", 1),
            "evaluation_status": candidate_info.get("evaluation_status", "PENDING"),
            "timestamp": feedback_payload.get("timestamp"),
            "filepath": os.path.relpath(out_path, self.project_root)
        }

        line = json.dumps(index_entry, ensure_ascii=False) + "\n"
        with open(self.index_file, "a", encoding="utf-8") as f:
            f.write(line)

        return {
            "status": "RECORDED",
            "feedback_id": feedback_id,
            "filepath": out_path,
            "repetition_count": candidate_info.get("repetition_count", 1),
            "scope": feedback_payload.get("scope")
        }

    def flag_false_positive(self, feedback_id: str, rationale: str) -> Dict[str, Any]:
        """
        Marks an existing feedback record as a false positive for later evaluation.
        Never deletes historical telemetry.
        """
        file_path = os.path.join(self.store_dir, f"{feedback_id}.json")
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Feedback record '{feedback_id}' not found at {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "generalization_candidate" in data:
            data["generalization_candidate"]["evaluation_status"] = "FLAGGED_FALSE_POSITIVE"
            data["generalization_candidate"]["flag_rationale"] = rationale

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Update index.jsonl entries
        self._rewrite_index_status(feedback_id, "FLAGGED_FALSE_POSITIVE")

        return {
            "status": "FLAGGED",
            "feedback_id": feedback_id,
            "evaluation_status": "FLAGGED_FALSE_POSITIVE",
            "rationale": rationale
        }

    def _rewrite_index_status(self, feedback_id: str, new_status: str) -> None:
        """Rewrites index.jsonl updating the evaluation_status for a feedback_id."""
        if not os.path.isfile(self.index_file):
            return
        lines = []
        with open(self.index_file, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if not line_str:
                    continue
                try:
                    entry = json.loads(line_str)
                    if entry.get("feedback_id") == feedback_id:
                        entry["evaluation_status"] = new_status
                    lines.append(json.dumps(entry, ensure_ascii=False) + "\n")
                except Exception:
                    lines.append(line)

        with open(self.index_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def scan_transcript(
        self,
        transcript_path: str,
        mark_recorded: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Parses transcript.jsonl, identifies meaningful user corrections,
        and optionally records new detections.
        """
        if not transcript_path or not os.path.isfile(transcript_path):
            return []

        recorded = []
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            sys.stderr.write(f"[AcademicCorrectionDetector] Error reading transcript: {e}\n")
            return []

        # Load existing index to avoid duplicate detections for the same turn
        existing_signatures = set()
        if os.path.isfile(self.index_file):
            with open(self.index_file, "r", encoding="utf-8") as idx:
                for line in idx:
                    try:
                        e = json.loads(line)
                        if e.get("signature_hash"):
                            existing_signatures.add(e["signature_hash"])
                    except Exception:
                        pass

        for idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                stype = record.get("type")
                source = record.get("source")
                content = record.get("content", "")

                if stype == "USER_INPUT" or source == "USER_EXPLICIT":
                    metadata = {
                        "source_transcript_path": transcript_path,
                        "turn_index": record.get("step_index", idx),
                        "user_identifier": "HumanUser"
                    }
                    detected = self.detect_correction(content, metadata=metadata)
                    if detected:
                        if mark_recorded:
                            rec_res = self.record_feedback(detected)
                            recorded.append(detected)
                        else:
                            recorded.append(detected)
            except Exception:
                continue

        return recorded

    def list_feedback(
        self,
        category: Optional[str] = None,
        scope: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Queries the feedback index file."""
        if not os.path.isfile(self.index_file):
            return []
        results = []
        with open(self.index_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if category and entry.get("type") != category:
                        continue
                    if scope and entry.get("scope") != scope:
                        continue
                    if status and entry.get("evaluation_status") != status:
                        continue
                    results.append(entry)
                except Exception:
                    continue
        return results

    def list_repeated_corrections(self, min_count: int = 2) -> List[Dict[str, Any]]:
        """Lists feedback patterns that have been repeated at least min_count times."""
        all_fb = self.list_feedback()
        hash_counts: Dict[str, List[Dict[str, Any]]] = {}
        for fb in all_fb:
            sh = fb.get("signature_hash")
            if sh:
                hash_counts.setdefault(sh, []).append(fb)

        repeated = []
        for sh, items in hash_counts.items():
            if len(items) >= min_count:
                repeated.append({
                    "signature_hash": sh,
                    "repetition_count": len(items),
                    "category": items[-1].get("type"),
                    "scope": items[-1].get("scope"),
                    "sample_feedback_id": items[-1].get("feedback_id"),
                    "all_feedback_ids": [it.get("feedback_id") for it in items]
                })
        return repeated

    def _get_signature_repetition_count(self, signature_hash: str) -> int:
        """Counts how many times this signature_hash appears in the index."""
        if not os.path.isfile(self.index_file):
            return 0
        count = 0
        with open(self.index_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line)
                    if e.get("signature_hash") == signature_hash:
                        count += 1
                except Exception:
                    pass
        return count

    def _normalize_for_hash(self, text: str) -> str:
        """Normalizes text for fuzzy signature hashing."""
        t = text.lower()
        t = re.sub(r"[^\w\s]", " ", t)
        words = [w for w in t.split() if len(w) > 2]
        return " ".join(words[:8])

    def _derive_desired_behavior(self, text: str, category: str, scope: str) -> str:
        """Extracts or derives formal desired behavior specification."""
        t_clean = text.strip().rstrip(".")
        if t_clean.lower().startswith("you forgot to"):
            action = t_clean[13:].strip()
            return f"Ensure to {action} during analytical execution."
        if t_clean.lower().startswith("you need to"):
            action = t_clean[11:].strip()
            return f"Always {action} prior to proceeding."
        if t_clean.lower().startswith("don't"):
            action = t_clean[5:].strip()
            return f"Do not {action}."
        if t_clean.lower().startswith("never"):
            return t_clean + "."
        return f"Standard compliance: {t_clean}."

    def _infer_skill(self, category: str) -> str:
        """Maps feedback category to corresponding production skill."""
        mapping = {
            "DATA_ANALYSIS_CORRECTION": "data-audit",
            "METHODOLOGY_CORRECTION": "methodology-review",
            "STATISTICAL_CORRECTION": "statistical-data-analyst",
            "WRITING_CORRECTION": "ai-academic-tone-polisher",
            "EVIDENCE_CORRECTION": "literature-harvester",
            "COMPLETENESS_CORRECTION": "chapter-4-writing",
            "PROCESS_CORRECTION": "academic-suite-orchestrator",
            "RESEARCH_INTEGRITY_CORRECTION": "thesis-integrity-auditor",
            "QUALITY_STYLE_CORRECTION": "apa-reporting"
        }
        return mapping.get(category, "academic-suite-orchestrator")


def main():
    parser = argparse.ArgumentParser(description="Academic User Correction Detector CLI")
    parser.add_argument("--text", type=str, help="Analyze user prompt text for corrections.")
    parser.add_argument("--scan-transcript", type=str, help="Scan a transcript.jsonl file.")
    parser.add_argument("--list", action="store_true", help="List detected feedback records.")
    parser.add_argument("--list-repeated", action="store_true", help="List repeated corrections.")
    parser.add_argument("--flag-fp", type=str, help="Feedback ID to flag as false positive.")
    parser.add_argument("--rationale", type=str, default="User statement was not a correction.", help="Rationale for false positive.")
    args = parser.parse_args()

    detector = AcademicCorrectionDetector()

    if args.text:
        res = detector.detect_correction(args.text)
        if res:
            rec = detector.record_feedback(res)
            print(json.dumps(rec, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"detected": False, "message": "No meaningful correction pattern detected."}, indent=2))

    elif args.scan_transcript:
        res = detector.scan_transcript(args.scan_transcript, mark_recorded=True)
        print(json.dumps({"scanned_count": len(res), "detected": res}, indent=2, ensure_ascii=False))

    elif args.list:
        items = detector.list_feedback()
        print(json.dumps(items, indent=2, ensure_ascii=False))

    elif args.list_repeated:
        items = detector.list_repeated_corrections()
        print(json.dumps(items, indent=2, ensure_ascii=False))

    elif args.flag_fp:
        flagged = detector.flag_false_positive(args.flag_fp, rationale=args.rationale)
        print(json.dumps(flagged, indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
