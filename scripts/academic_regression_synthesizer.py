#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_regression_synthesizer.py — Correction to Lesson to Regression Test Engine

Implements the automated learning pipeline:
    CORRECTION ──▶ LESSON ──▶ REGRESSION TEST

Whenever the learning system detects a high-confidence reusable failure:
1. Distills the underlying failure into a formal Lesson.
2. Synthesizes a candidate evaluation case testing correct reasoning properties
   (e.g., repeated-measures structure, missingness, imbalance, covariance structure, estimand,
   candidate model comparison) without hard-coding answers unless evidence genuinely requires one.
3. Stores candidate cases under `learning/evaluations/regression/`.
4. References originating lesson, experience, capability, expected and forbidden behaviors.
5. Manages lifecycle:
   - status: "candidate" (unvalidated initial proposal)
   - status: "validated" (permanent regression asset after lab verification)
   - status: "retired" (only upon explicit justification, never deleted)
6. Accumulates repeated mistakes into an institutionalized, growing regression suite.
"""

import os
import sys
import json
import uuid
import hashlib
import argparse
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

from contracts.contract_validator import (
    validate_evaluation_case,
    validate_feedback,
    validate_lesson
)


class RegressionSynthesisError(Exception):
    """Base exception for regression case synthesis failures."""
    pass


class AcademicRegressionSynthesizer:
    """Automated engine for synthesizing regression test cases from lessons and user corrections."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or ROOT_DIR)
        self.regression_dir = os.path.join(self.base_dir, "learning", "evaluations", "regression")
        self.index_file = os.path.join(self.regression_dir, "index.jsonl")
        self.experience_dir = os.path.join(self.base_dir, "learning", "experience")
        self.feedback_dir = os.path.join(self.base_dir, "learning", "experience", "feedback")
        self.lessons_dir = os.path.join(self.base_dir, "learning", "knowledge", "lessons")

        os.makedirs(self.regression_dir, exist_ok=True)

    def is_high_confidence_reusable_failure(
        self,
        feedback_data: Optional[Dict[str, Any]],
        lesson_data: Optional[Dict[str, Any]]
    ) -> Tuple[bool, str]:
        """
        Determines whether a correction/lesson qualifies as a high-confidence reusable failure.
        Rejects project-specific corrections and non-failure signals.
        """
        if feedback_data:
            scope = feedback_data.get("scope", "REUSABLE_PROCEDURAL")
            if scope == "PROJECT_SPECIFIC":
                return False, "Project-specific feedback does not generate regression tests."
            severity = feedback_data.get("severity", "MEDIUM")
            if severity not in ["MEDIUM", "HIGH", "BLOCKING"]:
                return False, f"Feedback severity '{severity}' below threshold."

        if lesson_data:
            scope = lesson_data.get("scope", "DOMAIN_WIDE")
            if scope == "PROJECT_SPECIFIC":
                return False, "Project-specific lessons do not generate regression tests."
            if not lesson_data.get("is_what_not_to_do", True):
                return False, "Positive exemplars (what worked well) do not produce regression defect tests."

        return True, "High-confidence reusable failure qualified."

    def extract_reasoning_requirements(
        self,
        text_corpus: str,
        capability: str
    ) -> Dict[str, Any]:
        """
        Extracts methodological reasoning properties, expected behavior, and forbidden behaviors.
        Guarantees that tests verify reasoning properties rather than hard-coding single answers.
        """
        lower = text_corpus.lower()

        # Domain 1: Longitudinal & Repeated-Measures Model Selection (The LMM vs RM-ANOVA Invariant)
        if any(w in lower for w in ["lmm", "mixed model", "repeated-measures", "rm-anova", "longitudinal", "تکرارسنجش"]):
            return {
                "capability": "statistical-data-analyst",
                "required_reasoning_properties": [
                    "repeated_measures_structure",
                    "missingness",
                    "imbalance",
                    "covariance_structure",
                    "estimand",
                    "candidate_model_comparison"
                ],
                "expected_behavior": (
                    "Before selecting an analytical model for repeated-measures or longitudinal data, "
                    "explicitly compare candidate models (e.g. Linear Mixed Models vs. Repeated-Measures ANOVA) "
                    "against study design, missingness patterns, group/cell imbalance, covariance structures, "
                    "and target estimand. Do not adopt a default model without comparative evaluation."
                ),
                "forbidden_behaviors": [
                    "unjustified_model_selection_without_comparison",
                    "ignoring_missingness_in_longitudinal_data"
                ],
                "task": {
                    "prompt": (
                        "Analyze the longitudinal treatment study comparing ACT and Control across 3 waves. "
                        "Evaluate whether Linear Mixed Models (LMM) or Repeated-Measures ANOVA (RM-ANOVA) "
                        "is the appropriate analytical framework by explicitly examining study design, missingness, "
                        "sample balance, covariance structures, and target estimand."
                    ),
                    "research_question": "Does ACT intervention lead to steeper reductions in burnout across waves compared to control?",
                    "hypothesis": "Participants in ACT will exhibit statistically significant burnout reductions across waves compared to control."
                },
                "spec_parameters": {
                    "design": "3_wave_longitudinal",
                    "candidate_models": ["Linear Mixed Model (LMM)", "Repeated-Measures ANOVA (RM-ANOVA)"],
                    "repeated_variable": "timepoint",
                    "id_variable": "subject_id",
                    "dv": "burnout",
                    "group": "condition"
                },
                "difficulty": "L2_INTERDEPENDENT_MODELS",
                "tags": ["longitudinal", "model_comparison", "lmm", "repeated_measures_anova", "missingness", "covariance"]
            }

        # Domain 2: ANCOVA & Regression Slope Homogeneity
        elif any(w in lower for w in ["slope", "ancova", "covariate", "همگونی شیب"]):
            return {
                "capability": "chapter4",
                "required_reasoning_properties": [
                    "homogeneity_of_slopes",
                    "covariate_measurement_error",
                    "linear_relationship",
                    "estimand"
                ],
                "expected_behavior": (
                    "Verify the homogeneity of regression slopes (treatment-by-covariate interaction p > .05) "
                    "before interpreting ANCOVA treatment effects."
                ),
                "forbidden_behaviors": [
                    "omitting_homogeneity_of_slopes_test",
                    "interpreting_ancova_under_slope_heterogeneity"
                ],
                "task": {
                    "prompt": "Evaluate whether baseline covariate violates regression slope homogeneity across conditions before reporting ANCOVA.",
                    "research_question": "Does ACT intervention reduce post-test burnout after adjusting for baseline scores?",
                    "hypothesis": "ACT will show significantly lower post-intervention burnout after adjusting for baseline scores."
                },
                "spec_parameters": {
                    "dv": "burnout_post",
                    "group": "condition",
                    "covariate": "burnout_pre"
                },
                "difficulty": "L2_INTERDEPENDENT_MODELS",
                "tags": ["ancova", "homogeneity_of_slopes", "covariate_adjustment"]
            }

        # Domain 3: Continuous Moderator Preservation (Avoiding Median Splits)
        elif any(w in lower for w in ["median split", "dichotomiz", "moderator", "تعدیل‌گر"]):
            return {
                "capability": "moderation",
                "required_reasoning_properties": [
                    "continuous_moderator_preservation",
                    "simple_slopes",
                    "johnson_neyman",
                    "power_loss_avoidance"
                ],
                "expected_behavior": (
                    "Maintain continuous moderators on their continuous metric using regression interaction terms; "
                    "strictly avoid artificial dichotomization or median splits."
                ),
                "forbidden_behaviors": [
                    "median_split_moderator",
                    "dichotomizing_continuous_variable"
                ],
                "task": {
                    "prompt": "Test whether psychological flexibility moderates the effect of job stress on burnout using continuous interaction modeling.",
                    "research_question": "Does psychological flexibility buffer the impact of job stress on burnout?",
                    "hypothesis": "Psychological flexibility will attenuate the positive relationship between stress and burnout."
                },
                "spec_parameters": {
                    "x": "job_stress",
                    "m": "psych_flexibility",
                    "y": "burnout"
                },
                "difficulty": "L4_ADVERSARIAL_EDGE_CASES",
                "tags": ["moderation", "continuous_moderator", "median_split_prevention"]
            }

        # Domain 4: Missingness Diagnostics (Little's MCAR)
        elif any(w in lower for w in ["missingness", "missing data", "mcar", "گمشده"]):
            return {
                "capability": "data-audit",
                "required_reasoning_properties": [
                    "missingness_pattern",
                    "little_mcar_test",
                    "imputation_strategy",
                    "attrition_bias"
                ],
                "expected_behavior": (
                    "Formally inspect missing data patterns, report Little's MCAR test, and justify handling methods."
                ),
                "forbidden_behaviors": [
                    "unjustified_listwise_deletion",
                    "ignoring_missingness_patterns"
                ],
                "task": {
                    "prompt": "Diagnose missingness patterns in psychometric dataset and report Little's MCAR test before downstream modeling.",
                    "research_question": "Are item missingness patterns completely at random (MCAR)?",
                    "hypothesis": "Missingness will conform to MCAR (p > .05) or require full information maximum likelihood."
                },
                "spec_parameters": {
                    "variables": ["item1", "item2", "item3", "item4"]
                },
                "difficulty": "L1_UNIVARIATE_BASELINE",
                "tags": ["data_audit", "missingness", "littles_mcar"]
            }

        # Domain 5: Observational Causality & Causal Language Guard
        elif any(w in lower for w in ["causal", "cause", "prove", "observational", "علت", "اثبات"]):
            return {
                "capability": "academic-writer",
                "required_reasoning_properties": [
                    "study_design_type",
                    "associative_language",
                    "causal_language_guard",
                    "confounding"
                ],
                "expected_behavior": (
                    "Strictly adhere to associative terminology (associated, predicted, accounted for) in observational designs, "
                    "refraining from asserting direct causality or proof."
                ),
                "forbidden_behaviors": [
                    "unsupported_causal_assertions",
                    "claiming_proof_in_observational_design"
                ],
                "task": {
                    "prompt": "Draft findings narrative for cross-sectional regression analysis without unwarranted causal assertions.",
                    "research_question": "Does perceived stress predict burnout in observational sample?",
                    "hypothesis": "Perceived stress will be positively associated with burnout."
                },
                "spec_parameters": {
                    "design_type": "cross_sectional_correlational"
                },
                "difficulty": "L1_UNIVARIATE_BASELINE",
                "tags": ["writing", "causal_language_guard", "observational_design"]
            }

        # Fallback General Methodological Invariant
        else:
            words = [w for w in lower.split() if len(w) > 4 and w not in ["should", "would", "could", "before", "after"]]
            key_props = [f"{w}_evaluation" for w in words[:4]] if words else ["methodological_prerequisite_check"]
            return {
                "capability": capability or "statistical-data-analyst",
                "required_reasoning_properties": key_props,
                "expected_behavior": f"Ensure thorough methodological compliance and verification of {', '.join(key_props)}.",
                "forbidden_behaviors": ["unverified_methodological_shortcut"],
                "task": {
                    "prompt": f"Execute analytical task verifying {', '.join(key_props)}.",
                    "research_question": "Does analytical modeling satisfy rigorous methodological standards?",
                    "hypothesis": "Analytical procedures will strictly adhere to verified methodological prerequisites."
                },
                "spec_parameters": {"check_domain": "general_methodology"},
                "difficulty": "L2_INTERDEPENDENT_MODELS",
                "tags": ["methodology", "regression_test"]
            }

    def synthesize_from_correction_and_lesson(
        self,
        feedback_data: Dict[str, Any],
        lesson_data: Dict[str, Any],
        experience_data: Optional[Dict[str, Any]] = None,
        record_to_disk: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Synthesizes a candidate regression evaluation case from a high-confidence reusable failure.
        Guarantees that repeated mistakes accumulate into the permanent regression suite.
        """
        # 1. Gate: High-Confidence Reusable Failure Check
        qualified, reason = self.is_high_confidence_reusable_failure(feedback_data, lesson_data)
        if not qualified:
            return None

        # 2. Extract Reasoning Requirements
        corpus = (
            feedback_data.get("correction", "") + " " +
            feedback_data.get("desired_behavior", "") + " " +
            lesson_data.get("what_happened", "") + " " +
            lesson_data.get("what_behavior_caused_outcome", "") + " " +
            lesson_data.get("what_should_have_happened", "")
        )
        target_cap = lesson_data.get("target_capability") or feedback_data.get("target_skill", "statistical-data-analyst")
        domain_spec = self.extract_reasoning_requirements(corpus, target_cap)

        # 3. Compute Deterministic Pattern Signature Hash
        sig_str = f"{domain_spec['capability']}::{'_'.join(sorted(domain_spec['required_reasoning_properties']))}"
        sig_hash = hashlib.sha256(sig_str.encode("utf-8")).hexdigest()[:8].upper()

        # 4. Check for Existing Case for this Failure Signature
        existing_case = self._find_case_by_signature(domain_spec["capability"], domain_spec["required_reasoning_properties"])
        if existing_case:
            # Accumulate repeat mistake!
            return self.accumulate_repeated_mistake(
                case_id=existing_case["case_id"],
                feedback_data=feedback_data,
                lesson_data=lesson_data
            )

        # 5. Build New Evaluation Case Candidate
        cap_slug = domain_spec["capability"].replace("-", "_").upper()[:12]
        case_id = f"EVAL-CASE-REG-{cap_slug}-{sig_hash}"
        now_iso = datetime.now(timezone.utc).isoformat()

        exp_id = (
            (experience_data and experience_data.get("experience_id")) or
            feedback_data.get("context", {}).get("experience_id") or
            lesson_data.get("originating_experience_id") or
            "EXP-UNKNOWN"
        )
        fdb_id = feedback_data.get("feedback_id", "FDB-UNKNOWN")
        lsn_id = lesson_data.get("lesson_id", "LSN-UNKNOWN")

        case_data = {
            "contract_version": "1.0.0",
            "case_id": case_id,
            "capability": domain_spec["capability"],
            "suite_type": "regression",
            "difficulty": domain_spec["difficulty"],
            "tags": domain_spec["tags"],
            "task": domain_spec["task"],
            "inputs": {
                "dataset_path": f"evals/regression/data_{sig_hash.lower()}.xlsx",
                "dataset_sha256": hashlib.sha256(sig_str.encode("utf-8")).hexdigest(),
                "spec_parameters": domain_spec["spec_parameters"]
            },
            "expected_properties": {
                "required_metrics": {
                    "reasoning_properties_evaluated": True
                },
                "required_reasoning_properties": domain_spec["required_reasoning_properties"],
                "required_artifacts": [
                    "03_model_comparison.json",
                    "03_model_comparison.md"
                ],
                "typography_rules": [
                    "persian_leading_zero"
                ]
            },
            "forbidden_behaviors": domain_spec["forbidden_behaviors"],
            "evaluation_method": {
                "runner_type": "DETERMINISTIC_SCRIPT",
                "runner_script": "scripts/academic_evaluation_lab.py",
                "cli_arguments": ["--suite", "regression", "--case", case_id],
                "timeout_seconds": 30
            },
            "created_at": now_iso,
            "originating_lesson_id": lsn_id,
            "originating_experience_id": exp_id,
            "originating_feedback_id": fdb_id,
            "status": "candidate",
            "expected_behavior": domain_spec["expected_behavior"],
            "forbidden_behavior": domain_spec["forbidden_behaviors"][0] if domain_spec["forbidden_behaviors"] else "flawed_behavior",
            "repeat_count": 1,
            "last_seen_at": now_iso
        }

        # 6. Validate Contract
        val_res = validate_evaluation_case(case_data)
        if not val_res["valid"]:
            raise RegressionSynthesisError(f"Synthesized case violates contract: {val_res.get('errors')}")

        # 7. Record to Disk
        if record_to_disk:
            fp = os.path.join(self.regression_dir, f"{case_id}.json")
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(case_data, f, indent=2, ensure_ascii=False)
            self._append_index(case_data)

        return case_data

    def validate_candidate_case(self, case_id: str) -> Dict[str, Any]:
        """
        Validates a candidate case using deterministic evaluation against both a flawed baseline
        and a compliant candidate. Promotes status to 'validated' upon success.
        """
        fp = os.path.join(self.regression_dir, f"{case_id}.json")
        if not os.path.isfile(fp):
            raise RegressionSynthesisError(f"Case '{case_id}' not found at {fp}")

        with open(fp, "r", encoding="utf-8") as f:
            case_data = json.load(f)

        from scripts.academic_evaluation_lab import AcademicEvaluationLab
        lab = AcademicEvaluationLab(base_dir=self.base_dir)

        # 1. Test Flawed Baseline (Must Fail and catch the specific mistake)
        flawed_artifacts = {
            "narrative": "مدل تحلیل واریانس بدون مقایسه با سایر مدل‌ها اجرا شد و نتیجه به دست آمد.",
            "statistics": {"f_value": 5.4, "p_value": "p = .023"}
        }
        flawed_result = lab.evaluate_candidate_on_case("CAND-FLAWED-BASELINE", case_data, flawed_artifacts)
        if flawed_result["verdict"] != "FAIL":
            raise RegressionSynthesisError(
                f"Candidate case '{case_id}' failed validation: flawed baseline was NOT caught (verdict={flawed_result['verdict']})."
            )

        # 2. Test Compliant Candidate (Must Pass all required reasoning properties)
        req_props = case_data.get("expected_properties", {}).get("required_reasoning_properties", [])
        compliant_reasoning = {prop: f"Formally analyzed and verified {prop}" for prop in req_props}
        compliant_artifacts = {
            "narrative": "مقایسه مدل‌ها نشان داد که ساختار داده‌های تکرارسنجش و مقادیر گمشده بررسی شدند (۰.۰۵ > p).",
            "reasoning": compliant_reasoning,
            "model_comparison": {"lmm_vs_anova": "LMM selected due to missing waves and covariance structure"},
            "statistics": {
                "estimand": "Fixed treatment effect across waves",
                "effect_size": 0.25,
                "confidence_interval": [0.10, 0.40],
                "artifact_path": "03_model_comparison.json",
                "is_synthetic": True,
                "data_mode": "simulation"
            }
        }
        compliant_result = lab.evaluate_candidate_on_case("CAND-COMPLIANT-VERIFIED", case_data, compliant_artifacts)
        if compliant_result["verdict"] != "PASS":
            raise RegressionSynthesisError(
                f"Candidate case '{case_id}' failed validation: compliant candidate failed checks -> {compliant_result['diagnostics']}"
            )

        # 3. Promote Status to 'validated'
        now_iso = datetime.now(timezone.utc).isoformat()
        case_data["status"] = "validated"
        case_data["validation_evidence"] = {
            "validated_at": now_iso,
            "validator": "AcademicEvaluationLab",
            "flawed_baseline_detected": True,
            "compliant_candidate_passed": True,
            "verified_reasoning_properties": req_props
        }

        with open(fp, "w", encoding="utf-8") as f:
            json.dump(case_data, f, indent=2, ensure_ascii=False)

        self._append_index(case_data)
        return case_data

    def accumulate_repeated_mistake(
        self,
        case_id: str,
        feedback_data: Optional[Dict[str, Any]] = None,
        lesson_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Increments repeat count and updates last_seen_at when a known mistake recurs.
        Guarantees that repeated mistakes accumulate into an institutionalized asset.
        """
        fp = os.path.join(self.regression_dir, f"{case_id}.json")
        if not os.path.isfile(fp):
            raise RegressionSynthesisError(f"Case '{case_id}' not found at {fp}")

        with open(fp, "r", encoding="utf-8") as f:
            case_data = json.load(f)

        case_data["repeat_count"] = case_data.get("repeat_count", 1) + 1
        case_data["last_seen_at"] = datetime.now(timezone.utc).isoformat()

        with open(fp, "w", encoding="utf-8") as f:
            json.dump(case_data, f, indent=2, ensure_ascii=False)

        self._append_index(case_data)
        return case_data

    def retire_case(self, case_id: str, retirement_reason: str) -> Dict[str, Any]:
        """
        Explicitly retires a regression test case with justification.
        Crucial: Old cases are NEVER deleted from disk; they remain preserved and auditable.
        """
        if not retirement_reason or len(retirement_reason.strip()) < 10:
            raise RegressionSynthesisError("Explicit, detailed retirement reason required to retire regression cases.")

        fp = os.path.join(self.regression_dir, f"{case_id}.json")
        if not os.path.isfile(fp):
            raise RegressionSynthesisError(f"Case '{case_id}' not found at {fp}")

        with open(fp, "r", encoding="utf-8") as f:
            case_data = json.load(f)

        case_data["status"] = "retired"
        case_data["retirement_reason"] = retirement_reason.strip()

        with open(fp, "w", encoding="utf-8") as f:
            json.dump(case_data, f, indent=2, ensure_ascii=False)

        self._append_index(case_data)
        return case_data

    def load_cases(
        self,
        include_candidates: bool = True,
        include_retired: bool = False
    ) -> List[Dict[str, Any]]:
        """Loads regression cases with status filtering."""
        cases = []
        for fn in sorted(os.listdir(self.regression_dir)):
            if fn.endswith(".json") and not fn.startswith("index"):
                fp = os.path.join(self.regression_dir, fn)
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        c = json.load(f)
                    st = c.get("status", "validated")
                    if not include_candidates and st == "candidate":
                        continue
                    if not include_retired and st == "retired":
                        continue
                    cases.append(c)
                except Exception:
                    continue
        return cases

    def _find_case_by_signature(self, capability: str, reasoning_props: List[str]) -> Optional[Dict[str, Any]]:
        """Searches existing regression cases for a matching capability and reasoning properties set."""
        props_set = set(p.lower() for p in reasoning_props)
        for c in self.load_cases(include_candidates=True, include_retired=True):
            if c.get("capability", "").lower() == capability.lower():
                c_props = set(p.lower() for p in c.get("expected_properties", {}).get("required_reasoning_properties", []))
                if props_set == c_props or props_set.issubset(c_props):
                    return c
        return None

    def _append_index(self, case_data: Dict[str, Any]):
        """Appends index entry to index.jsonl."""
        entry = {
            "case_id": case_data.get("case_id"),
            "capability": case_data.get("capability"),
            "status": case_data.get("status"),
            "repeat_count": case_data.get("repeat_count", 1),
            "originating_lesson_id": case_data.get("originating_lesson_id"),
            "originating_feedback_id": case_data.get("originating_feedback_id"),
            "last_seen_at": case_data.get("last_seen_at"),
            "created_at": case_data.get("created_at")
        }
        with open(self.index_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Regression Test Synthesizer")
    parser.add_argument("--synthesize-test", action="store_true", help="Run synthesis demonstration on LMM vs ANOVA correction")
    parser.add_argument("--validate-case", help="Validate a candidate case ID")
    parser.add_argument("--retire-case", help="Retire a case ID")
    parser.add_argument("--reason", help="Retirement justification")
    args = parser.parse_args()

    synthesizer = AcademicRegressionSynthesizer()

    if args.synthesize_test:
        sample_feedback = {
            "feedback_id": "FDB-20260918-DEMO01",
            "type": "METHODOLOGY_CORRECTION",
            "scope": "REUSABLE_PROCEDURAL",
            "severity": "HIGH",
            "correction": "You should have compared LMM with repeated-measures ANOVA.",
            "desired_behavior": "Before selecting a longitudinal model, compare LMM against RM-ANOVA.",
            "target_agent": "statistics-agent",
            "target_skill": "statistical-data-analyst"
        }
        sample_lesson = {
            "lesson_id": "LSN-20260918-DEMO01",
            "scope": "DOMAIN_WIDE",
            "is_what_not_to_do": True,
            "target_capability": "statistical-data-analyst",
            "what_happened": "Repeated-measures ANOVA was used despite missing waves across timepoints.",
            "what_behavior_caused_outcome": "Selected RM-ANOVA blindly without comparing against LMM.",
            "what_should_have_happened": "Evaluate repeated-measures structure, missingness, imbalance, covariance structure, and estimand."
        }
        res = synthesizer.synthesize_from_correction_and_lesson(sample_feedback, sample_lesson)
        print("Synthesized candidate case:")
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.validate_case:
        validated = synthesizer.validate_candidate_case(args.validate_case)
        print(f"Case '{args.validate_case}' successfully validated and promoted to permanent regression suite.")

    elif args.retire_case:
        if not args.reason:
            print("Error: --reason required to retire a case.", file=sys.stderr)
            sys.exit(1)
        retired = synthesizer.retire_case(args.retire_case, args.reason)
        print(f"Case '{args.retire_case}' marked as retired: {args.reason}")


if __name__ == "__main__":
    main()
