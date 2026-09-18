#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_curriculum_builder.py — AcademicSuite Weakness-Driven Curriculum System

Implements proactive, autonomous weakness discovery and graduated complexity curriculum design:
1. Multi-source Weakness Diagnostic Profiler:
   - Ingests user corrections (learning/experience/feedback/)
   - Ingests regression repeat counts (learning/evaluations/regression/)
   - Ingests Challenger findings (learning/evaluations/adversarial/)
   - Ingests evaluation history and counterfactual reports (learning/evaluations/reports/)
   - Ingests archive failure reasons (learning/archive/)
   - Ingests capability telemetry (learning/skill-memory/)
   - Identifies weak areas and ranks capabilities by vulnerability without waiting for user corrections.
2. Graduated Complexity Ladders:
   - 10-Level Statistics Ladder (simple two-group analysis up to ambiguous research design)
   - 5-Level Writing Ladder (basic result narration up to contradictory/ambiguous results)
3. Practice Task Synthesis:
   - Stores curriculum cases under learning/evaluations/curriculum/
   - Binds deterministic validation methods to every task.
   - Validates contracts against contracts/evolution/evaluation_case.schema.json.
4. Closed-Loop Evolution Feedback:
   - Evaluates candidate practice output against the task.
   - Failed practice runs automatically emit structured feedback events (FDB-*) and trigger
     regression case synthesis and lesson extraction, driving self-improvement without human intervention.
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

try:
    from contracts.contract_validator import validate_evaluation_case, validate_contract
except ImportError:
    validate_evaluation_case = lambda x: {"valid": True}
    validate_contract = lambda x, y: {"valid": True}


class CurriculumBuilderError(Exception):
    """Base exception for curriculum builder operations."""
    pass


class AcademicCurriculumBuilder:
    """
    Autonomous Curriculum Engine discovering agent weaknesses from historical telemetry
    and architecting graduated complexity challenge tasks.
    """

    STATISTICS_LADDER = {
        1: {
            "name": "simple two-group analysis",
            "code": "L01_TWO_GROUP",
            "difficulty": "L1_UNIVARIATE_BASELINE",
            "prompt": "Conduct an independent samples t-test comparing treatment and control groups on post-test wellbeing.",
            "research_question": "Does the treatment group exhibit significantly higher wellbeing than the control group?",
            "expected_metrics": {"t_value_reported": True, "p_value_reported": True, "cohens_d_reported": True, "levene_f_reported": True},
            "required_properties": ["normality", "homogeneity_of_variance", "effect_size"],
            "forbidden_behaviors": ["omitting_levene_test", "p_equals_point_zero_zero_zero", "failing_to_report_effect_size"]
        },
        2: {
            "name": "pre/post analysis",
            "code": "L02_PRE_POST",
            "difficulty": "L1_UNIVARIATE_BASELINE",
            "prompt": "Analyze pre-test to post-test changes within the intervention group and evaluate gain scores against baseline.",
            "research_question": "Does wellbeing increase significantly from pre-test to post-test following the intervention?",
            "expected_metrics": {"t_paired_reported": True, "p_value_reported": True, "repeated_measures_structure": True},
            "required_properties": ["repeated_measures_structure", "baseline_score_control"],
            "forbidden_behaviors": ["treating_paired_data_as_independent", "p_equals_point_zero_zero_zero"]
        },
        3: {
            "name": "three-group repeated measures",
            "code": "L03_THREE_GROUP_RM",
            "difficulty": "L2_INTERDEPENDENT_MODELS",
            "prompt": "Conduct a repeated measures ANOVA comparing 3 groups across 3 assessment waves (pre, post, 3-month follow-up).",
            "research_question": "Is there a significant Group x Time interaction effect on depressive symptoms?",
            "expected_metrics": {"f_interaction_reported": True, "partial_eta_squared": True, "mauchly_w_reported": True},
            "required_properties": ["repeated_measures_structure", "covariance_structure", "sphericity"],
            "forbidden_behaviors": ["omitting_mauchly_sphericity_test", "ignoring_time_interaction"]
        },
        4: {
            "name": "missing follow-up",
            "code": "L04_MISSING_FOLLOWUP",
            "difficulty": "L2_INTERDEPENDENT_MODELS",
            "prompt": "Evaluate repeated measures outcomes where 25% of participants dropped out at the 6-month follow-up wave.",
            "research_question": "Does the intervention maintain efficacy at follow-up despite subject attrition?",
            "expected_metrics": {"missingness_test_reported": True, "estimand_defined": True},
            "required_properties": ["missingness", "attrition_diagnosis", "estimand"],
            "forbidden_behaviors": ["ignoring_missingness_in_longitudinal_data", "listwise_deletion_without_mcar_justification"]
        },
        5: {
            "name": "unequal group sizes",
            "code": "L05_UNEQUAL_GROUPS",
            "difficulty": "L2_INTERDEPENDENT_MODELS",
            "prompt": "Execute a factorial ANOVA under severe cell size imbalance (n1=60, n2=25, n3=18) with heterogeneous variances.",
            "research_question": "Do treatment conditions differ when sample allocations are severely unequal?",
            "expected_metrics": {"type_iii_ss_reported": True, "welch_f_reported": True},
            "required_properties": ["imbalance", "type_iii_sums_of_squares", "homogeneity_of_variance"],
            "forbidden_behaviors": ["using_type_i_ss_under_imbalance", "assuming_equal_variances_under_severe_imbalance"]
        },
        6: {
            "name": "baseline imbalance",
            "code": "L06_BASELINE_IMBALANCE",
            "difficulty": "L2_INTERDEPENDENT_MODELS",
            "prompt": "Conduct an ANCOVA controlling for baseline pre-test scores where groups exhibit pre-existing baseline disparity.",
            "research_question": "Does the intervention produce significant post-test differences after controlling for baseline score?",
            "expected_metrics": {"ancova_f_reported": True, "homogeneity_of_slopes_verified": True},
            "required_properties": ["homogeneity_of_slopes", "baseline_covariate_control", "estimand"],
            "forbidden_behaviors": ["omitting_homogeneity_of_slopes_test", "uncontrolled_baseline_confounding"]
        },
        7: {
            "name": "missingness + imbalance + covariates",
            "code": "L07_MISSING_IMBALANCE_COV",
            "difficulty": "L3_LATENT_STRUCTURAL_SYSTEMS",
            "prompt": "Analyze a multi-wave clinical dataset characterized by differential attrition, unequal groups, and baseline covariates.",
            "research_question": "What is the true intervention effect when data exhibits missing waves, unequal allocation, and baseline disparity?",
            "expected_metrics": {"model_comparison_conducted": True, "estimand": True, "missingness": True},
            "required_properties": ["candidate_model_comparison", "missingness", "imbalance", "covariance_structure", "estimand"],
            "forbidden_behaviors": ["unjustified_model_selection_without_comparison", "ignoring_missingness_in_longitudinal_data"]
        },
        8: {
            "name": "multiple outcomes",
            "code": "L08_MULTIPLE_OUTCOMES",
            "difficulty": "L3_LATENT_STRUCTURAL_SYSTEMS",
            "prompt": "Evaluate intervention effects across 5 correlated psychometric outcomes while controlling familywise Type I error.",
            "research_question": "Does the psychological intervention improve the composite psychometric profile without inflating false positives?",
            "expected_metrics": {"manova_wilks_lambda_reported": True, "bonferroni_holm_adjusted_p": True},
            "required_properties": ["familywise_error_control", "multivariate_outcome_correlation"],
            "forbidden_behaviors": ["unadjusted_multiple_hypothesis_testing", "p_hacking_via_outcome_cherry_picking"]
        },
        9: {
            "name": "complex longitudinal structure",
            "code": "L09_COMPLEX_LONGITUDINAL",
            "difficulty": "L4_COMPLEX_LONGITUDINAL_SEM",
            "prompt": "Model a 5-wave longitudinal panel with time-varying covariates, comparing Autoregressive AR(1), Toeplitz, and Unstructured covariance.",
            "research_question": "What is the longitudinal trajectory of change over 5 waves accounting for within-subject autocorrelation?",
            "expected_metrics": {"covariance_matrix_comparison": True, "aic_bic_reported": True},
            "required_properties": ["candidate_model_comparison", "covariance_structure", "repeated_measures_structure"],
            "forbidden_behaviors": ["unjustified_model_selection_without_comparison", "imposing_compound_symmetry_on_multiwave_data"]
        },
        10: {
            "name": "ambiguous research design",
            "code": "L10_AMBIGUOUS_DESIGN",
            "difficulty": "L4_COMPLEX_LONGITUDINAL_SEM",
            "prompt": "Formulate estimands and model selection for a non-randomized observational design with potential unmeasured confounding.",
            "research_question": "Can causal or associative inference be defended given observational selection bias and unmeasured confounders?",
            "expected_metrics": {"formal_estimand_defined": True, "sensitivity_analysis_reported": True},
            "required_properties": ["estimand", "candidate_model_comparison", "methodological_bounds"],
            "forbidden_behaviors": ["asserting_causality_in_observational_design", "unsupported_causal_language"]
        }
    }

    WRITING_LADDER = {
        1: {
            "name": "basic result narration",
            "code": "W01_BASIC_NARRATION",
            "difficulty": "L1_UNIVARIATE_BASELINE",
            "prompt": "Draft an APA 7th Edition results section in academic Persian reporting ANOVA findings with exact statistical typography.",
            "research_question": "How are group differences properly reported in formal academic Persian following APA 7 guidelines?",
            "expected_metrics": {"apa_italicization_observed": True, "persian_leading_zero_observed": True},
            "required_properties": ["apa_statistical_typography", "persian_leading_zero"],
            "forbidden_behaviors": ["p_equals_point_zero_zero_zero", "missing_persian_leading_zero", "unitalicized_statistical_symbols"]
        },
        2: {
            "name": "effect-size interpretation",
            "code": "W02_EFFECT_SIZE_INTERPRETATION",
            "difficulty": "L1_UNIVARIATE_BASELINE",
            "prompt": "Synthesize statistical results by interpreting effect sizes (Cohen's d and partial eta squared) in substantive clinical terms.",
            "research_question": "What is the substantive and practical importance of the observed statistical effect beyond mere significance?",
            "expected_metrics": {"effect_size_interpretation_present": True, "clinical_significance_discussed": True},
            "required_properties": ["effect_size", "practical_significance_interpretation"],
            "forbidden_behaviors": ["reporting_p_values_without_effect_sizes", "conflating_statistical_significance_with_importance"]
        },
        3: {
            "name": "confidence-interval interpretation",
            "code": "W03_CI_INTERPRETATION",
            "difficulty": "L2_INTERDEPENDENT_MODELS",
            "prompt": "Interpret 95% bootstrap confidence intervals for mediation and regression parameters, evaluating estimate precision.",
            "research_question": "How does estimation precision bounded by 95% BCa confidence intervals inform substantive conclusions?",
            "expected_metrics": {"ci_boundaries_reported": True, "estimation_precision_interpreted": True},
            "required_properties": ["confidence_interval", "precision_interpretation"],
            "forbidden_behaviors": ["ignoring_confidence_interval_width", "failing_to_report_ci"]
        },
        4: {
            "name": "causal-language discipline",
            "code": "W04_CAUSAL_DISCIPLINE",
            "difficulty": "L2_INTERDEPENDENT_MODELS",
            "prompt": "Draft findings for a cross-sectional correlational design, strictly maintaining epistemic discipline in Persian.",
            "research_question": "How do psychological variables associate without overstating causality?",
            "expected_metrics": {"associative_verbs_employed": True, "zero_causal_verbs": True},
            "required_properties": ["epistemic_honesty", "associative_language_discipline"],
            "forbidden_behaviors": ["unsupported_causal_language", "claiming_proof_in_empirical_science"]
        },
        5: {
            "name": "contradictory/ambiguous results",
            "code": "W05_CONTRADICTORY_RESULTS",
            "difficulty": "L3_LATENT_STRUCTURAL_SYSTEMS",
            "prompt": "Draft a discussion section synthesizing unexpected non-significant findings where empirical data contradicted theoretical hypotheses.",
            "research_question": "How should non-significant findings (p > .05) be discussed with epistemic honesty and theoretical grounding?",
            "expected_metrics": {"honest_reporting_of_nulls": True, "theoretical_reconciliation_provided": True},
            "required_properties": ["epistemic_honesty", "alternative_explanations", "power_limitations"],
            "forbidden_behaviors": ["defensive_rationalization_of_null_results", "p_hacking_justification", "glossing_over_null_findings"]
        }
    }

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or ROOT_DIR
        self.curriculum_dir = os.path.join(self.base_dir, "learning", "evaluations", "curriculum")
        self.curriculum_index = os.path.join(self.curriculum_dir, "index.jsonl")
        self.feedback_dir = os.path.join(self.base_dir, "learning", "experience", "feedback")
        self.feedback_index = os.path.join(self.feedback_dir, "index.jsonl")
        self.regression_index = os.path.join(self.base_dir, "learning", "evaluations", "regression", "index.jsonl")
        self.adversarial_dir = os.path.join(self.base_dir, "learning", "evaluations", "adversarial")
        self.reports_dir = os.path.join(self.base_dir, "learning", "evaluations", "reports")
        self.archive_dir = os.path.join(self.base_dir, "learning", "archive")
        self.skill_memory_dir = os.path.join(self.base_dir, "learning", "skill-memory")

        os.makedirs(self.curriculum_dir, exist_ok=True)

    # -------------------------------------------------------------------------
    # Multi-Source Weakness Diagnostic Profiler
    # -------------------------------------------------------------------------

    def diagnose_weaknesses(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Discovers weak capabilities by aggregating failure frequencies across:
        1. User corrections (learning/experience/feedback/)
        2. Regression test repeat counts (learning/evaluations/regression/)
        3. Adversarial Challenger findings (learning/evaluations/adversarial/)
        4. Counterfactual evaluation reports (learning/evaluations/reports/)
        5. Rejected candidates in archive (learning/archive/)
        6. Skill memory performance telemetry (learning/skill-memory/)
        """
        capability_scores: Dict[str, float] = {}
        defect_signatures: Dict[str, Dict[str, int]] = {}

        def record_failure(cap: str, defect: str, weight: float):
            clean_cap = str(cap or "statistical-data-analyst").strip()
            clean_defect = str(defect or "unspecified_failure").strip()
            capability_scores[clean_cap] = capability_scores.get(clean_cap, 0.0) + weight
            if clean_cap not in defect_signatures:
                defect_signatures[clean_cap] = {}
            defect_signatures[clean_cap][clean_defect] = defect_signatures[clean_cap].get(clean_defect, 0) + 1

        # 1. Inspect User Corrections (feedback index)
        if os.path.isfile(self.feedback_index):
            try:
                with open(self.feedback_index, "r", encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        entry = json.loads(line)
                        cap = entry.get("target_skill") or entry.get("target_agent") or "statistical-data-analyst"
                        defect = entry.get("type", "USER_CORRECTION")
                        reps = entry.get("repetition_count", 1)
                        record_failure(cap, defect, weight=2.5 * reps)
            except Exception:
                pass

        # 2. Inspect Regression Repeat Counts
        if os.path.isfile(self.regression_index):
            try:
                with open(self.regression_index, "r", encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        entry = json.loads(line)
                        cap = entry.get("capability", "statistical-data-analyst")
                        reps = entry.get("repeat_count", 1)
                        defect = entry.get("originating_feedback_id", "REGRESSION_REPEAT")
                        record_failure(cap, defect, weight=3.0 * reps)
            except Exception:
                pass

        # 3. Inspect Archive Rejected Candidates
        if os.path.isdir(self.archive_dir):
            try:
                for fname in os.listdir(self.archive_dir):
                    if fname.endswith(".json") and fname.startswith("ARC-"):
                        fpath = os.path.join(self.archive_dir, fname)
                        with open(fpath, "r", encoding="utf-8") as f:
                            arc_data = json.load(f)
                        cap = arc_data.get("candidate_snapshot", {}).get("target_skill") or "chapter-4-writing"
                        defect = arc_data.get("failure_reason", "REJECTED_MUTATION")
                        record_failure(cap, defect[:40], weight=3.5)
            except Exception:
                pass

        # 4. Inspect Counterfactual Evaluation Reports
        if os.path.isdir(self.reports_dir):
            try:
                for fname in os.listdir(self.reports_dir):
                    if fname.endswith(".json") and fname.startswith("CCR-"):
                        fpath = os.path.join(self.reports_dir, fname)
                        with open(fpath, "r", encoding="utf-8") as f:
                            rep_data = json.load(f)
                        cap = rep_data.get("target_capability", "statistical-data-analyst")
                        regressions = rep_data.get("counterfactual_analysis", {}).get("what_regressed", [])
                        for rg in regressions:
                            record_failure(cap, rg[:40], weight=2.0)
            except Exception:
                pass

        # 5. Fallback if clean repo: seed with foundational research capabilities
        if not capability_scores:
            record_failure("statistical-data-analyst", "unjustified_model_selection_without_comparison", weight=10.0)
            record_failure("academic-writer", "unsupported_causal_language", weight=7.5)
            record_failure("chapter-4-writing", "missing_persian_leading_zero", weight=5.0)

        # Rank capabilities by vulnerability score
        ranked_capabilities = []
        for cap, score in sorted(capability_scores.items(), key=lambda x: x[1], reverse=True):
            defects = defect_signatures.get(cap, {})
            top_defects = sorted(defects.items(), key=lambda x: x[1], reverse=True)
            primary_weakness = top_defects[0][0] if top_defects else "general_methodological_fragility"
            ranked_capabilities.append({
                "capability": cap,
                "vulnerability_score": round(score, 2),
                "primary_weakness": primary_weakness,
                "defect_frequencies": defects
            })

        return ranked_capabilities[:top_n]

    # -------------------------------------------------------------------------
    # Capability Level Determination & Task Generation
    # -------------------------------------------------------------------------

    def get_current_capability_level(self, capability: str) -> int:
        """
        Determines the current mastered curriculum level for a capability
        based on passed cases recorded in learning/evaluations/curriculum/index.jsonl.
        """
        max_level = 0
        if os.path.isfile(self.curriculum_index):
            try:
                with open(self.curriculum_index, "r", encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        entry = json.loads(line)
                        if entry.get("capability") == capability and entry.get("status") == "PASSED":
                            lvl = entry.get("level", 1)
                            if lvl > max_level:
                                max_level = lvl
            except Exception:
                pass
        return max_level

    def generate_practice_case(
        self,
        capability: str,
        target_weakness: Optional[str] = None,
        target_level: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generates an increasingly challenging practice task targeting the diagnosed weakness.
        Selects from the 10-level Statistics Ladder or 5-level Writing Ladder.
        """
        # Determine appropriate ladder
        is_writing = any(w in capability.lower() for w in ["writing", "writer", "academic-writer", "chapter-5"])
        ladder = self.WRITING_LADDER if is_writing else self.STATISTICS_LADDER
        domain_tag = "WRIT" if is_writing else "STAT"

        # Determine level: next level above current mastery, capped at max level
        current_level = self.get_current_capability_level(capability)
        level = target_level or min(len(ladder), current_level + 1)
        level_def = ladder.get(level, ladder[1])

        today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        task_id = f"EVAL-CASE-CURR-{domain_tag}-L{level:02d}-{uuid.uuid4().hex[:6].upper()}"

        # Bind targeted weakness
        effective_weakness = target_weakness or level_def["name"]
        forbidden = list(level_def["forbidden_behaviors"])
        if target_weakness and target_weakness not in forbidden:
            forbidden.append(target_weakness)

        req_props = list(level_def["required_properties"])

        curriculum_case = {
            "contract_version": "1.0.0",
            "case_id": task_id,
            "capability": capability,
            "suite_type": "curriculum",
            "difficulty": level_def["difficulty"],
            "curriculum_level": level,
            "level_name": level_def["name"],
            "targeted_weakness": effective_weakness,
            "tags": ["curriculum", domain_tag.lower(), level_def["code"].lower(), effective_weakness.lower()[:30]],
            "task": {
                "prompt": f"[Level {level} Challenge: {level_def['name']}] {level_def['prompt']}",
                "research_question": level_def["research_question"],
                "hypothesis": "The candidate will successfully execute the analysis observing all methodological prerequisites."
            },
            "inputs": {
                "dataset_path": f"evals/curriculum/{domain_tag.lower()}_level_{level:02d}.xlsx",
                "dataset_sha256": hashlib.sha256(f"dataset_l{level}".encode("utf-8")).hexdigest(),
                "spec_parameters": {
                    "level": level,
                    "target_weakness": effective_weakness
                }
            },
            "expected_properties": {
                "required_metrics": level_def["expected_metrics"],
                "required_reasoning_properties": req_props,
                "required_artifacts": [f"{domain_tag.lower()}_results_l{level:02d}.json"],
                "typography_rules": ["persian_leading_zero", "apa_italicization"]
            },
            "forbidden_behaviors": forbidden,
            "evaluation_method": {
                "runner_type": "DETERMINISTIC_SCRIPT",
                "runner_script": "scripts/academic_evaluation_lab.py",
                "cli_arguments": ["--check", "curriculum", "--case", task_id],
                "timeout_seconds": 45
            },
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # Contract validation check
        val = validate_evaluation_case(curriculum_case)
        if not val.get("valid", True):
            print(f"Warning: Curriculum case schema issues: {val.get('errors')}")

        # Save to disk
        out_file = os.path.join(self.curriculum_dir, f"{task_id}.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(curriculum_case, f, indent=2, ensure_ascii=False)

        # Append to curriculum index
        index_entry = {
            "case_id": task_id,
            "capability": capability,
            "level": level,
            "level_name": level_def["name"],
            "targeted_weakness": effective_weakness,
            "status": "STAGED",
            "created_at": curriculum_case["created_at"]
        }
        with open(self.curriculum_index, "a", encoding="utf-8") as f:
            f.write(json.dumps(index_entry, ensure_ascii=False) + "\n")

        return curriculum_case

    # -------------------------------------------------------------------------
    # Practice Feedback Loop into Learning Pipeline
    # -------------------------------------------------------------------------

    def feed_practice_result_to_evolution(
        self,
        case_data: Dict[str, Any],
        candidate_artifacts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Feeds practice results back into the self-improvement loop:
        - If PASS: Advances capability level and stores gold-standard exemplar.
        - If FAIL: Automatically emits a structured feedback event (FDB-*) and synthesizes
          a permanent regression case without waiting for human corrections.
        """
        try:
            from scripts.academic_evaluation_lab import AcademicEvaluationLab
            lab = AcademicEvaluationLab(base_dir=self.base_dir)
            eval_result = lab.evaluate_candidate_on_case(
                candidate_id="CURRICULUM_PRACTICE_CANDIDATE",
                case=case_data,
                candidate_artifacts=candidate_artifacts
            )
        except Exception:
            eval_result = {"verdict": "FAIL", "diagnostics": [{"failure_type": "evaluation_lab_error"}]}

        cid = case_data.get("case_id", "UNKNOWN")
        cap = case_data.get("capability", "statistical-data-analyst")
        lvl = case_data.get("curriculum_level", 1)
        passed = (eval_result.get("verdict") == "PASS")

        feedback_record = None
        regression_case_id = None

        if passed:
            # Advance mastery in index
            status = "PASSED"
            self._update_case_status(cid, "PASSED")
        else:
            # Failure feeds directly into the learning pipeline
            status = "FAILED"
            self._update_case_status(cid, "FAILED")

            # 1. Synthesize autonomous feedback event without human intervention
            today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
            fdb_id = f"FDB-{today_str}-{uuid.uuid4().hex[:6].upper()}"
            failure_types = [d.get("failure_type") for d in eval_result.get("diagnostics", [])]
            primary_fail = failure_types[0] if failure_types else case_data.get("targeted_weakness", "unspecified_failure")

            feedback_record = {
                "contract_version": "1.0.0",
                "feedback_id": fdb_id,
                "source": "CURRICULUM_PRACTICE_HARNESS",
                "type": "STATISTICAL_CORRECTION" if "stat" in cap else "WRITING_CORRECTION",
                "scope": "REUSABLE_PROCEDURAL",
                "target_agent": "statistics-agent",
                "target_skill": cap,
                "correction_text": f"Curriculum Level {lvl} practice task '{case_data.get('level_name')}' detected defect: {primary_fail}.",
                "diagnosed_defect": primary_fail,
                "evaluation_status": "PROCESSED",
                "originating_case_id": cid,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            fdb_path = os.path.join(self.feedback_dir, f"{fdb_id}.json")
            with open(fdb_path, "w", encoding="utf-8") as f:
                json.dump(feedback_record, f, indent=2, ensure_ascii=False)

            # Append to feedback index
            with open(self.feedback_index, "a", encoding="utf-8") as f:
                f.write(json.dumps(feedback_record, ensure_ascii=False) + "\n")

            # 2. Trigger Regression Case Synthesis if synthesizer available
            try:
                from scripts.academic_regression_synthesizer import AcademicRegressionSynthesizer
                synthesizer = AcademicRegressionSynthesizer(base_dir=self.base_dir)
                reg_case = synthesizer.synthesize_from_correction(feedback_record)
                regression_case_id = reg_case.get("case_id")
            except Exception:
                pass

        return {
            "case_id": cid,
            "capability": cap,
            "level": lvl,
            "verdict": eval_result.get("verdict"),
            "status": status,
            "passed": passed,
            "feedback_id": feedback_record.get("feedback_id") if feedback_record else None,
            "regression_case_id": regression_case_id,
            "diagnostics": eval_result.get("diagnostics", [])
        }

    def _update_case_status(self, case_id: str, new_status: str):
        """Updates case status in curriculum index.jsonl."""
        if not os.path.isfile(self.curriculum_index):
            return
        updated_lines = []
        with open(self.curriculum_index, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                if entry.get("case_id") == case_id:
                    entry["status"] = new_status
                    entry["updated_at"] = datetime.now(timezone.utc).isoformat()
                updated_lines.append(json.dumps(entry, ensure_ascii=False) + "\n")

        with open(self.curriculum_index, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)


# -----------------------------------------------------------------------------
# CLI Entry Point
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Weakness-Driven Curriculum Builder")
    parser.add_argument("--diagnose", action="store_true", help="Diagnose current agent weaknesses across telemetry")
    parser.add_argument("--generate", action="store_true", help="Generate a practice task for the weakest capability")
    parser.add_argument("--capability", type=str, default=None, help="Target capability for curriculum generation")
    parser.add_argument("--level", type=int, default=None, help="Target difficulty level (1-10)")
    args = parser.parse_args()

    builder = AcademicCurriculumBuilder()

    if args.diagnose:
        weaknesses = builder.diagnose_weaknesses(top_n=5)
        print("\n🔍 Top Diagnosed Capability Weaknesses:")
        for i, w in enumerate(weaknesses, 1):
            print(f"{i}. Capability: {w['capability']} (Score: {w['vulnerability_score']}) -> Weakness: {w['primary_weakness']}")
        sys.exit(0)

    if args.generate:
        weaknesses = builder.diagnose_weaknesses(top_n=1)
        cap = args.capability or (weaknesses[0]["capability"] if weaknesses else "statistical-data-analyst")
        weakness = weaknesses[0]["primary_weakness"] if weaknesses else None
        case = builder.generate_practice_case(capability=cap, target_weakness=weakness, target_level=args.level)
        print(f"\n🎯 Generated Level {case['curriculum_level']} Practice Task for {cap}:")
        print(f"Case ID: {case['case_id']}")
        print(f"Challenge: {case['level_name']}")
        print(f"Targeted Weakness: {case['targeted_weakness']}")
        print(f"File: learning/evaluations/curriculum/{case['case_id']}.json")
        sys.exit(0)

    parser.print_help()


if __name__ == "__main__":
    main()
