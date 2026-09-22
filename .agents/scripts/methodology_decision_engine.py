#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/methodology_decision_engine.py — Deterministic Methodology Decision Engine ("The Hands")

Constitutional Invariant (Directive 12.1 & 19):
Python scripts are strictly deterministic tools ("The Hands").
Antigravity is the sole agent conductor. This script formulates, validates, and emits
authoritative Methodology Decision Records (MDR) conforming to
contracts/methodology_decision_record.schema.json.

The 8-Step Methodological Decision Ladder:
  1. Research Question
       ↓
  2. Design
       ↓
  3. Estimand
       ↓
  4. Candidate Methods
       ↓
  5. Assumptions
       ↓
  6. Method Selection & Refutation Matrix
       ↓
  7. Execution Specification (Execution Contract)
       ↓
  8. Statistical Executor (Deterministic "Hands")
"""

import os
import sys
import re
import json
import uuid
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Add repo root and contracts to path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.academic_task_router import derive_research_design
from contracts.contract_validator import validate_methodology_decision_record


class MethodologyDecisionEngine:
    """
    Deterministic engine that translates research inquiries into binding
    Methodology Decision Records with complete candidate evaluation,
    literature-backed refutations, and downstream execution contracts.
    """

    def __init__(self, repo_root: Optional[str] = None):
        self.repo_root = repo_root or ROOT_DIR

    def formulate_decision_record(
        self,
        research_question: str,
        project_id: str = "default_project",
        decided_by: str = "methodology-expert",
        status: str = "APPROVED"
    ) -> Dict[str, Any]:
        """
        Formulates a complete 8-step Methodology Decision Record (MDR).
        """
        q = research_question.strip()
        q_lower = q.lower()

        # Step 1 & 2: Derive Research Design
        raw_design = derive_research_design(q)
        study_type = raw_design.get("study_type", "RCT")
        if study_type not in ["RCT", "quasi_experimental", "experimental_unspecified", "correlational_structural", "scale_validation", "qualitative", "meta_analysis", "observational_survey", "observational", "cross_sectional", "longitudinal"]:
            study_type = "RCT" if "rct" in q_lower else ("quasi_experimental" if "intervention" in q_lower else "observational_survey")

        group_structure = raw_design.get("group_structure", "multi-group")
        if group_structure not in ["single-group", "multi-group", "factorial"]:
            group_structure = "multi-group"

        temporal_dynamics = raw_design.get("temporal_dynamics", "repeated measures")
        if temporal_dynamics not in ["single-point", "cross-sectional", "repeated measures", "longitudinal_panel"]:
            temporal_dynamics = "repeated measures" if "follow-up" in q_lower or "post-test" in q_lower else "cross-sectional"

        waves = raw_design.get("waves", "follow-up")
        if waves not in ["cross-sectional", "pre-post", "follow-up", "multi-wave"]:
            waves = "follow-up" if "follow-up" in q_lower or "month" in q_lower else "pre-post"

        factors = raw_design.get("factors", ["RCT", "multi-group", "repeated measures", "follow-up"])
        if not factors:
            factors = [study_type, group_structure, temporal_dynamics, waves]

        design_obj = {
            "study_type": study_type,
            "group_structure": group_structure,
            "temporal_dynamics": temporal_dynamics,
            "waves": waves,
            "factors": factors,
            "unit_of_analysis": "individual"
        }

        # Step 3: Estimand Definition
        outcomes = raw_design.get("outcomes", ["psychological_outcome"])
        primary_outcome = outcomes[0] if outcomes else "target_outcome"
        interventions = raw_design.get("interventions", ["Intervention"])
        primary_intervention = interventions[0] if interventions else "Active Treatment"

        if re.search(r'\bmediat', q_lower) or "indirect" in q_lower:
            estimand_type = "indirect_effect"
            targeted_param = f"Indirect effect (a * b) of {primary_intervention} on {primary_outcome} through psychological mediator"
            causal_contrast = f"{primary_intervention} vs. Control through mediator"
        elif "moderation" in q_lower or "interaction" in q_lower:
            estimand_type = "interaction_effect"
            targeted_param = f"Conditional moderation effect (interaction beta) across moderator levels"
            causal_contrast = f"{primary_intervention} effect moderated by conditional factor"
        elif study_type == "scale_validation":
            estimand_type = "factor_loading"
            targeted_param = "Standardized latent factor loadings (lambda), AVE, and composite reliability (omega)"
            causal_contrast = "Measurement model construct validity"
        elif study_type == "qualitative":
            estimand_type = "thematic_pattern"
            targeted_param = "Thematic pattern hierarchy and reflexive semantic code prevalence"
            causal_contrast = "Qualitative lived experiences"
        else:
            estimand_type = "ATE"
            targeted_param = f"Average Treatment Effect (ATE) of {primary_intervention} on {primary_outcome} across post-test and follow-up waves, controlling for baseline scores"
            causal_contrast = f"{primary_intervention} vs. Control"

        timepoints = ["pre-test", "post-test"]
        if waves == "follow-up":
            timepoints.append("two-month follow-up")

        estimand_obj = {
            "type": estimand_type,
            "targeted_parameter": targeted_param,
            "population": "Adult clinical and community behavioral sciences sample",
            "timepoints": timepoints,
            "causal_contrast": causal_contrast
        }

        # Step 4: Candidate Methods Evaluation
        # Step 5: Assumptions
        # Step 6: Method Selection & Refutations
        # Step 7: Required Inputs & Execution Contract
        if study_type in ("RCT", "quasi_experimental") or temporal_dynamics == "repeated measures":
            candidate_methods = [
                {
                    "method": "Mixed Split-Plot Repeated Measures ANOVA (Between Groups x Within Time)",
                    "family": "General Linear Model",
                    "pros": [
                        "Models Group x Time interaction explicitly across multi-wave follow-up",
                        "Partitions between-subject and within-subject error variances",
                        "Standard reporting across psychology and clinical behavioral sciences"
                    ],
                    "cons": [
                        "Requires sphericity assumption; sensitive to missing data across waves"
                    ],
                    "suitability": "highly_suitable"
                },
                {
                    "method": "Linear Mixed-Effects Models (LMM / Multilevel Growth Modeling)",
                    "family": "Mixed Models",
                    "pros": [
                        "Handles unbalanced wave missingness via full information maximum likelihood",
                        "Accommodates individual-specific random intercepts and slopes"
                    ],
                    "cons": [
                        "Requires larger sample sizes for stable variance component estimation"
                    ],
                    "suitability": "highly_suitable"
                },
                {
                    "method": "One-Way ANCOVA with Baseline Covariate at Each Discrete Post Wave",
                    "family": "General Linear Model",
                    "pros": [
                        "Maximizes statistical power for simple pre-post comparisons (Cohen, 1988)",
                        "Removes baseline variance from error term"
                    ],
                    "cons": [
                        "Does not model omnibus trajectory across follow-up in a single integrated test"
                    ],
                    "suitability": "conditionally_suitable"
                },
                {
                    "method": "Gain Score Independent Samples t-test (Post minus Pre)",
                    "family": "Classical Parametric Test",
                    "pros": ["Simple computation"],
                    "cons": [
                        "Violates regression to the mean (Lord's Paradox)",
                        "Substantially less powerful than ANCOVA when baseline and posttest are correlated (r > 0.5)"
                    ],
                    "suitability": "unsuitable"
                },
                {
                    "method": "Post-Test Only Independent Samples t-test / One-Way ANOVA",
                    "family": "Classical Parametric Test",
                    "pros": ["Trivially simple"],
                    "cons": [
                        "Discards baseline measurement entirely",
                        "Fails to control for pre-existing individual differences, inflating residual error variance"
                    ],
                    "suitability": "unsuitable"
                }
            ]

            assumptions = [
                {
                    "assumption": "Normality of Residuals",
                    "test_method": "Shapiro-Wilk test on studentized residuals and Kline (2016) absolute skewness (< 2.0) and kurtosis (< 7.0)",
                    "threshold": "Shapiro-Wilk p > .05 or Kline skewness < 2.0 / kurtosis < 7.0",
                    "action_on_violation": "Apply 5,000-sample percentile bootstrap standard errors or logarithmic transformation"
                },
                {
                    "assumption": "Homogeneity of Variance (Homoscedasticity)",
                    "test_method": "Levene's test of equality of error variances across groups",
                    "threshold": "Levene test p > .05",
                    "action_on_violation": "Report Welch's adjusted F or heteroscedasticity-consistent (HC3) standard errors"
                },
                {
                    "assumption": "Homogeneity of Regression Slopes (for Covariate adjustment)",
                    "test_method": "Group x Pretest baseline covariate interaction test",
                    "threshold": "Interaction term p > .05",
                    "action_on_violation": "Switch from standard ANCOVA to Johnson-Neyman floodlight significance regions or Mixed ANOVA"
                },
                {
                    "assumption": "Sphericity of Variance-Covariance Matrix",
                    "test_method": "Mauchly's W test of sphericity",
                    "threshold": "Mauchly W p > .05",
                    "action_on_violation": "Apply Greenhouse-Geisser adjustment if epsilon < 0.75; apply Huynh-Feldt adjustment if epsilon >= 0.75"
                },
                {
                    "assumption": "Missing Data Mechanism",
                    "test_method": "Little's Missing Completely at Random (MCAR) chi-square test",
                    "threshold": "Little's MCAR p > .05",
                    "action_on_violation": "If missingness rate <= 5%, use Expectation-Maximization (EM) imputation; if > 5%, use FIML in LMM"
                }
            ]

            selected_method = {
                "name": "Mixed Split-Plot Repeated Measures ANOVA with Baseline Covariate Verification",
                "family": "General Linear Model",
                "package_or_script": ".agents/skills/statistical-data-analyst/scripts/run_repeated_measures.py",
                "selection_justification": (
                    "The Mixed Split-Plot Repeated Measures ANOVA (2 Groups x 3 Waves: Pre, Post, 2-Month Follow-Up) "
                    "directly addresses the estimand by testing the primary Group x Time interaction effect. "
                    "It simultaneously partitions between-subject variance (intervention effect) and within-subject variance "
                    "(temporal trajectory and maintenance effect), adhering to Cohen (1988) and Tabachnick & Fidell (2019)."
                )
            }

            rejected_methods = [
                {
                    "method": "Gain Score Independent Samples t-test",
                    "reason": "Suffers from Lord's Paradox (Lord, 1967): change scores are negatively correlated with baseline measurements, conflating genuine intervention effects with statistical regression to the mean. Mathematically inferior to ANCOVA and repeated measures.",
                    "literature_citation": "Vickers, A. J., & Altman, D. G. (2001). Statistics notes: Analysing controlled trials with baseline and follow up measurements. BMJ, 323(7321), 1123-1124."
                },
                {
                    "method": "Post-Test Only One-Way ANOVA",
                    "reason": "Completely discards baseline information, leaving pre-existing group differences uncontrolled and dramatically inflating error variance, which results in a severe loss of statistical power.",
                    "literature_citation": "Cohen, J. (1988). Statistical power analysis for the behavioral sciences (2nd ed.). Lawrence Erlbaum Associates."
                },
                {
                    "method": "Unadjusted Multiple t-tests across Waves",
                    "reason": "Conducting separate independent t-tests at post-test and follow-up without familywise error control drastically inflates the Experimentwise Type I Error rate (alpha_inflated = 1 - (1 - .05)^k).",
                    "literature_citation": "Maxwell, S. E., & Delaney, H. D. (2004). Designing experiments and analyzing data: A model comparison perspective (2nd ed.). Psychology Press."
                }
            ]

            required_inputs = {
                "dataset_path": "projects/*/02_clean_and_scored/data_curated.xlsx",
                "independent_variable": "group",
                "dependent_variables": [
                    f"{primary_outcome}_post",
                    f"{primary_outcome}_fu"
                ],
                "covariates": [f"{primary_outcome}_pre"],
                "grouping_variable": "group",
                "time_variable": "wave",
                "subject_id_variable": "subject_id"
            }

            decision_rationale = (
                f"To rigorously evaluate whether {primary_intervention} affects {primary_outcome} across post-test "
                "and two-month follow-up, the research design requires an analytical framework that models both "
                "the between-group treatment difference and the temporal persistence of therapeutic gains. "
                "Mixed Repeated Measures ANOVA is selected as the primary inferential model because it isolates "
                "the critical Group x Time interaction while controlling for individual baseline variance. "
                "Alternative methods such as gain-score t-tests are rejected due to Lord's paradox (Vickers & Altman, 2001), "
                "and post-test only comparisons are rejected due to statistical power deflation."
            )

            execution_contract = {
                "assigned_executor": "statistics-agent",
                "engine": "python",
                "script": ".agents/skills/statistical-data-analyst/scripts/run_repeated_measures.py",
                "cli_command": (
                    "python3 scripts/statistical_pipeline_engine.py "
                    f"--plan academic-state/analysis_plan.json --mode PRODUCTION"
                ),
                "parameters": {
                    "alpha": 0.05,
                    "two_tailed": True,
                    "effect_size": "partial_eta_squared",
                    "post_hoc": "bonferroni",
                    "sphericity_violation_action": "greenhouse_geisser",
                    "normality_test": "shapiro_wilk",
                    "homogeneity_test": "levene"
                },
                "expected_triad_artifacts": {
                    "docx_path": "projects/*/03_deliverables/stage_06_hypothesis_1/06_hypothesis_1.docx",
                    "md_path": "projects/*/03_deliverables/stage_06_hypothesis_1/06_hypothesis_1.md",
                    "json_path": "projects/*/03_deliverables/stage_06_hypothesis_1/06_hypothesis_1.json"
                },
                "validation_gates": [
                    "sha256_provenance_recorded",
                    "raw_dataset_read_only_0444",
                    "shapiro_wilk_p_gt_05_or_kline_skew_kurt",
                    "levene_equality_verified",
                    "mauchly_sphericity_tested",
                    "greenhouse_geisser_applied_if_violated",
                    "triad_artifact_invariant"
                ]
            }

        elif re.search(r'\bmediat', q_lower) or estimand_type == "indirect_effect":
            candidate_methods = [
                {
                    "method": "Preacher & Hayes Nonparametric Percentile / BCa Bootstrap (PROCESS Model 4)",
                    "family": "Resampling-Based Path Analysis",
                    "pros": [
                        "Does not assume normal distribution of indirect effect product (a * b)",
                        "Provides robust, empirical 95% confidence intervals with high statistical power"
                    ],
                    "cons": ["Computationally intensive (5,000 resamples)"],
                    "suitability": "highly_suitable"
                },
                {
                    "method": "Baron & Kenny 4-Step Causal Steps Regression",
                    "family": "Stepwise Multiple Regression",
                    "pros": ["Historically recognized"],
                    "cons": [
                        "Severely deflated statistical power",
                        "Does not formally compute or test the indirect effect (a * b)"
                    ],
                    "suitability": "unsuitable"
                },
                {
                    "method": "Sobel Normal-Theory Test",
                    "family": "Asymptotic Normal Approximation",
                    "pros": ["Simple closed-form z-test calculation"],
                    "cons": [
                        "Assumes symmetric normal distribution for indirect effect, which is heavily skewed",
                        "Inflates Type II error rates in psychological samples"
                    ],
                    "suitability": "unsuitable"
                }
            ]

            assumptions = [
                {
                    "assumption": "Linearity of Structural Paths",
                    "test_method": "Standardized residual plots against fitted values",
                    "threshold": "No visible curvature or heteroscedastic fan pattern",
                    "action_on_violation": "Fit non-linear polynomial terms or apply power transformations"
                },
                {
                    "assumption": "Multicollinearity between Predictor and Mediator",
                    "test_method": "Variance Inflation Factor (VIF) and Tolerance",
                    "threshold": "VIF < 5.0, Tolerance > 0.20",
                    "action_on_violation": "Mean-center variables or re-examine construct redundancy"
                }
            ]

            selected_method = {
                "name": "Preacher & Hayes PROCESS Model 4 with 5,000 Bootstrap Resamples",
                "family": "Resampling-Based Path Analysis",
                "package_or_script": ".agents/skills/mediation/scripts/run_mediation.py",
                "selection_justification": (
                    "Hayes PROCESS Model 4 directly estimates the indirect mediation effect and constructs "
                    "95% bias-corrected accelerated (BCa) bootstrap confidence intervals across 5,000 iterations, "
                    "overcoming the severe power deficits and distributional violations of legacy methods."
                )
            }

            rejected_methods = [
                {
                    "method": "Baron & Kenny 4-Step Causal Steps Regression",
                    "reason": "Severely deflated statistical power; requires Step 1 (total effect c) to be significant, which erroneously blocks genuine mediation under suppression or small effect conditions (Hayes, 2018).",
                    "literature_citation": "Preacher, K. J., & Hayes, A. F. (2004). SPSS and SAS procedures for estimating indirect effects in simple mediation models. Behavior Research Methods, Instruments, & Computers, 36(4), 717-731."
                },
                {
                    "method": "Sobel Normal-Theory Test",
                    "reason": "Assumes the product of regression coefficients (a * b) follows a normal distribution. In empirical behavioral research, the product distribution is positively skewed and kurtotic, causing Sobel z-tests to suffer from severely deflated power and high Type II errors.",
                    "literature_citation": "Hayes, A. F. (2018). Introduction to mediation, moderation, and conditional process analysis: A regression-based approach (2nd ed.). Guilford Press."
                }
            ]

            required_inputs = {
                "dataset_path": "projects/*/02_clean_and_scored/data_curated.xlsx",
                "independent_variable": "X",
                "dependent_variables": ["Y"],
                "covariates": ["M"]
            }

            decision_rationale = (
                "Mediation analysis is grounded in modern resampling theory. Preacher & Hayes bootstrap methodology "
                "is selected because it provides asymmetric empirical confidence intervals for the indirect effect without "
                "relying on false normality assumptions. Baron & Kenny and Sobel approaches are formally rejected."
            )

            execution_contract = {
                "assigned_executor": "statistics-agent",
                "engine": "python",
                "script": ".agents/skills/mediation/scripts/run_mediation.py",
                "cli_command": "python3 .agents/skills/mediation/scripts/run_mediation.py --bootstrap 5000",
                "parameters": {"bootstrap_resamples": 5000, "confidence_level": 0.95, "ci_type": "bca"},
                "expected_triad_artifacts": {
                    "docx_path": "projects/*/03_deliverables/stage_07_mediation/07_mediation.docx",
                    "md_path": "projects/*/03_deliverables/stage_07_mediation/07_mediation.md",
                    "json_path": "projects/*/03_deliverables/stage_07_mediation/07_mediation.json"
                },
                "validation_gates": ["bootstrap_5000_verified", "triad_artifact_invariant"]
            }

        else:
            # General quantitative structural / regression fallback
            candidate_methods = [
                {
                    "method": "Ordinary Least Squares Multiple Regression with HC3 Standard Errors",
                    "family": "General Linear Model",
                    "pros": ["Direct parametric estimation", "Robust standard error correction"],
                    "cons": ["Requires continuous outcome"],
                    "suitability": "highly_suitable"
                },
                {
                    "method": "Stepwise Regression",
                    "family": "Data-Driven Variable Selection",
                    "pros": ["Automated"],
                    "cons": ["Severely inflates Type I error", "Capitalizes on chance"],
                    "suitability": "unsuitable"
                }
            ]

            assumptions = [
                {
                    "assumption": "Multicollinearity",
                    "test_method": "VIF and Tolerance",
                    "threshold": "VIF < 5.0",
                    "action_on_violation": "Ridge regression or dimension reduction"
                }
            ]

            selected_method = {
                "name": "Standard Multiple Regression with Robust Standard Errors",
                "family": "General Linear Model",
                "package_or_script": ".agents/skills/regression/scripts/run_regression.py",
                "selection_justification": "Provides unbiased parameter estimates with robust standard errors."
            }

            rejected_methods = [
                {
                    "method": "Stepwise Automated Regression",
                    "reason": "Stepwise selection inflates Type I error, produces biased parameter estimates, and capitalizes on sample-specific random noise.",
                    "literature_citation": "Thompson, B. (1995). Stepwise regression and stepwise discriminant analysis need not apply here: A guidelines editorial. Educational and Psychological Measurement, 55(4), 525-534."
                }
            ]

            required_inputs = {
                "dataset_path": "projects/*/02_clean_and_scored/data_curated.xlsx",
                "independent_variable": "predictors",
                "dependent_variables": [primary_outcome]
            }

            decision_rationale = "General linear modeling with robust standard errors selected to ensure parameter stability and defensible inference."

            execution_contract = {
                "assigned_executor": "statistics-agent",
                "engine": "python",
                "script": ".agents/skills/regression/scripts/run_regression.py",
                "cli_command": "python3 .agents/skills/regression/scripts/run_regression.py",
                "parameters": {"alpha": 0.05, "robust_se": "HC3"},
                "expected_triad_artifacts": {
                    "docx_path": "projects/*/03_deliverables/stage_06_hypothesis_1/06_hypothesis_1.docx",
                    "md_path": "projects/*/03_deliverables/stage_06_hypothesis_1/06_hypothesis_1.md",
                    "json_path": "projects/*/03_deliverables/stage_06_hypothesis_1/06_hypothesis_1.json"
                },
                "validation_gates": ["triad_artifact_invariant"]
            }

        record_id = f"MDR-2026-{uuid.uuid4().hex[:8].upper()}"
        created_at = datetime.now(timezone.utc).isoformat()

        record = {
            "contract_version": "1.0.0",
            "record_id": record_id,
            "project_id": project_id,
            "created_at": created_at,
            "decided_by": decided_by,
            "status": status,
            "research_question": q,
            "design": design_obj,
            "estimand": estimand_obj,
            "candidate_methods": candidate_methods,
            "assumptions": assumptions,
            "selected_method": selected_method,
            "rejected_methods": rejected_methods,
            "required_inputs": required_inputs,
            "decision_rationale": decision_rationale,
            "execution_contract": execution_contract
        }

        return record

    def validate_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Validates a decision record against the authoritative contract schema."""
        return validate_methodology_decision_record(record)


def format_human_mdr(record: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 80)
    lines.append("ACADEMIC SUITE METHODOLOGY DECISION RECORD (MDR)")
    lines.append("Authoritative 8-Step Methodological Decision Ladder")
    lines.append("=" * 80)
    lines.append(f"Record ID:   {record.get('record_id')}")
    lines.append(f"Decided By:  {record.get('decided_by')} | Status: {record.get('status')}")
    lines.append(f"Created At:  {record.get('created_at')}")
    lines.append("")

    lines.append("-" * 80)
    lines.append("1. RESEARCH QUESTION")
    lines.append("-" * 80)
    lines.append(f"  {record.get('research_question')}")
    lines.append("")

    design = record.get("design", {})
    lines.append("-" * 80)
    lines.append("2. EMPIRICAL RESEARCH DESIGN")
    lines.append("-" * 80)
    lines.append(f"  Study Type:        {design.get('study_type')}")
    lines.append(f"  Group Structure:   {design.get('group_structure')}")
    lines.append(f"  Temporal Dynamics: {design.get('temporal_dynamics')}")
    lines.append(f"  Waves:             {design.get('waves')}")
    lines.append(f"  Design Factors:    {', '.join(design.get('factors', []))}")
    lines.append("")

    estimand = record.get("estimand", {})
    lines.append("-" * 80)
    lines.append("3. ESTIMAND DEFINITION")
    lines.append("-" * 80)
    lines.append(f"  Estimand Type:      {estimand.get('type')}")
    lines.append(f"  Targeted Parameter: {estimand.get('targeted_parameter')}")
    lines.append(f"  Timepoints:         {', '.join(estimand.get('timepoints', []))}")
    lines.append(f"  Causal Contrast:    {estimand.get('causal_contrast')}")
    lines.append("")

    lines.append("-" * 80)
    lines.append("4. CANDIDATE METHODS EVALUATION")
    lines.append("-" * 80)
    for idx, cm in enumerate(record.get("candidate_methods", []), 1):
        suit = cm.get('suitability', '').upper()
        lines.append(f"  [{idx}] {cm.get('method')} ({cm.get('family')}) — [{suit}]")
        for pro in cm.get("pros", []):
            lines.append(f"      + Pro: {pro}")
        for con in cm.get("cons", []):
            lines.append(f"      - Con: {con}")
    lines.append("")

    lines.append("-" * 80)
    lines.append("5. ASSUMPTION DIAGNOSTICS CHECKLIST")
    lines.append("-" * 80)
    for a in record.get("assumptions", []):
        lines.append(f"  • {a.get('assumption')}:")
        lines.append(f"      Test: {a.get('test_method')}")
        lines.append(f"      Threshold: {a.get('threshold')}")
        lines.append(f"      Violation Action: {a.get('action_on_violation')}")
    lines.append("")

    sel = record.get("selected_method", {})
    lines.append("-" * 80)
    lines.append("6. METHOD SELECTION & SCIENTIFIC REFUTATIONS")
    lines.append("-" * 80)
    lines.append(f"  SELECTED METHOD: {sel.get('name')}")
    lines.append(f"  Family:          {sel.get('family')}")
    lines.append(f"  Script/Package:  {sel.get('package_or_script')}")
    lines.append(f"  Justification:   {sel.get('selection_justification')}")
    lines.append("")
    lines.append("  REJECTED METHODS (FORMAL REFUTATION MATRIX):")
    for rm in record.get("rejected_methods", []):
        lines.append(f"    ❌ {rm.get('method')}")
        lines.append(f"       Reason:   {rm.get('reason')}")
        lines.append(f"       Citation: {rm.get('literature_citation')}")
    lines.append("")

    lines.append("-" * 80)
    lines.append("7. DECISION RATIONALE")
    lines.append("-" * 80)
    lines.append(f"  {record.get('decision_rationale')}")
    lines.append("")

    ec = record.get("execution_contract", {})
    lines.append("-" * 80)
    lines.append("8. DOWNSTREAM EXECUTION CONTRACT ('The Hands')")
    lines.append("-" * 80)
    lines.append(f"  Assigned Executor: {ec.get('assigned_executor')}")
    lines.append(f"  Script:            {ec.get('script')}")
    lines.append(f"  CLI Command:       {ec.get('cli_command')}")
    lines.append(f"  Parameters:        {json.dumps(ec.get('parameters', {}))}")
    lines.append(f"  Validation Gates:  {', '.join(ec.get('validation_gates', []))}")
    lines.append("=" * 80)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="AcademicSuite Methodology Decision Engine — Formulates and validates binding Methodology Decision Records."
    )
    parser.add_argument("--prompt", "-p", type=str, required=True, help="Research question or analytical inquiry.")
    parser.add_argument("--project-id", type=str, default="default_project", help="Project identifier.")
    parser.add_argument("--output", "-o", type=str, help="Path to write the resulting MDR JSON file.")
    parser.add_argument("--json", action="store_true", help="Output raw JSON to stdout.")
    parser.add_argument("--validate", action="store_true", default=True, help="Validate against contract schema.")

    args = parser.parse_args()

    engine = MethodologyDecisionEngine()
    record = engine.formulate_decision_record(
        research_question=args.prompt,
        project_id=args.project_id
    )

    if args.validate:
        verdict = engine.validate_record(record)
        if not verdict.get("valid", False):
            print(f"Contract Schema Validation FAILED: {verdict.get('errors')}", file=sys.stderr)
            sys.exit(1)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)

    if args.json:
        print(json.dumps(record, indent=2, ensure_ascii=False))
    else:
        print(format_human_mdr(record))


if __name__ == "__main__":
    main()
