r"""
scripts/curriculum_dataset_generator.py — Deterministic Physical Dataset & Design Synthesizer

Synthesizes real physical datasets on disk for AcademicSuite curriculum practice cases:
1. Conforms to Directive 9: Realistic decimal noise (\mu_emp = \mu_target + delta, delta ~ Uniform(+-0.08, +-0.25)).
2. Conforms to Directive 6: English-only ASCII filenames.
3. Conforms to mathematical sanity: N >= 15, positive variance, attrition <= 40%.
4. Computes cryptographic SHA256 of physical files.
5. Populates complete data_provenance, formal research design, expected invariants,
   expected pitfalls, and gold behavioral properties.
"""

import os
import csv
import math
import random
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class CurriculumDatasetGenerator:
    """Deterministic generator of physical curriculum datasets and research designs."""

    @staticmethod
    def _bounded_noise(target: float, min_delta: float = 0.08, max_delta: float = 0.25) -> float:
        """Injects bounded random decimal noise per Directive 9."""
        sign = random.choice([-1.0, 1.0])
        delta = random.uniform(min_delta, max_delta) * sign
        return round(target + delta, 2)

    @classmethod
    def generate(
        cls,
        case_id: str,
        ladder_code: str,
        level: int,
        is_writing: bool = False,
        base_dir: Optional[str] = None,
        synthetic_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates an actual physical CSV dataset on disk and returns its dataset,
        data_provenance, design, expected_invariants, expected_pitfalls, and
        gold_behavioral_properties contracts.
        """
        base = base_dir or ROOT_DIR
        target_dir = os.path.join(base, "learning", "evaluations", "curriculum", "datasets")
        os.makedirs(target_dir, exist_ok=True)

        filename = f"{case_id.lower().replace('-', '_')}.csv"
        file_path = os.path.join(target_dir, filename)
        rel_path = os.path.relpath(file_path, base)

        # Seed random with case_id for reproducible generation
        seed_val = int(hashlib.md5(case_id.encode("utf-8")).hexdigest()[:8], 16)
        random.seed(seed_val)

        if is_writing:
            return cls._generate_writing_case(file_path, rel_path, case_id, ladder_code, level, synthetic_params)
        else:
            return cls._generate_statistics_case(file_path, rel_path, case_id, ladder_code, level, synthetic_params)

    @classmethod
    def _generate_statistics_case(
        cls,
        abs_path: str,
        rel_path: str,
        case_id: str,
        code: str,
        level: int,
        params: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generates statistical dataset and behavioral properties for levels 1-10."""
        # 1. Dispatch level-specific data synthesis
        if level == 1:  # L01_TWO_GROUP
            n_per_group = 20
            rows = [["id", "group", "wellbeing_post"]]
            for i in range(1, n_per_group + 1):
                rows.append([f"T_{i:03d}", "Treatment", cls._bounded_noise(24.35 + random.gauss(0, 3.2))])
            for i in range(1, n_per_group + 1):
                rows.append([f"C_{i:03d}", "Control", cls._bounded_noise(19.80 + random.gauss(0, 3.1))])

            variables = [
                {"name": "id", "role": "identifier", "type": "categorical", "description": "Subject unique ID"},
                {"name": "group", "role": "independent_variable", "type": "categorical", "description": "Intervention vs Control arm"},
                {"name": "wellbeing_post", "role": "dependent_variable", "type": "numeric", "description": "Post-intervention psychological wellbeing"}
            ]
            design = {
                "design_type": "INDEPENDENT_SAMPLES_RCT",
                "independent_variables": ["group"],
                "dependent_variables": ["wellbeing_post"],
                "covariates": [],
                "factors": ["group"],
                "sample_allocation": "EQUAL"
            }
            invariants = [
                {"invariant_id": "INV-LEVENES-TEST-EVALUATED", "description": "Levene test for equality of variances evaluated before t-test inference", "verification_dimension": "STATISTICAL_RIGOR", "evaluation_rule": "levene_f_reported"},
                {"invariant_id": "INV-EFFECT-SIZE-REPORTED", "description": "Standardized effect size (Cohen's d or Hedges' g) calculated and reported", "verification_dimension": "STATISTICAL_RIGOR", "evaluation_rule": "cohens_d_present"},
                {"invariant_id": "INV-CONFIDENCE-INTERVAL-BOUNDED", "description": "95% confidence intervals reported for the mean difference", "verification_dimension": "STATISTICAL_RIGOR", "evaluation_rule": "ci_present"},
                {"invariant_id": "INV-PERSIAN-LEADING-ZERO", "description": "Persian reporting strictly retains leading zero (۰.۰۵, not .۰۵)", "verification_dimension": "APA_TYPOGRAPHY", "evaluation_rule": "persian_leading_zero"},
                {"invariant_id": "INV-APA-ITALICIZATION", "description": "Statistical symbols (t, p, d, M, SD) italicized", "verification_dimension": "APA_TYPOGRAPHY", "evaluation_rule": "apa_italicization"}
            ]
            pitfalls = [
                {"pitfall_id": "PIT-P-EQUALS-ZERO", "description": "Reporting p-value as .000 instead of p < .001 / ۰.۰۰۱ > p", "trigger_condition": "p_equals_zero_reported"},
                {"pitfall_id": "PIT-MISSING-EFFECT-SIZE", "description": "Reporting t-test without standardized effect size", "trigger_condition": "missing_effect_size"},
                {"pitfall_id": "PIT-OMITTING-LEVENES-TEST", "description": "Assuming equal variances without testing Levene's test", "trigger_condition": "missing_levene"}
            ]
            gold = [
                {"property_id": "PROP-ASSUMPTION-DIAGNOSTICS", "description": "Exhaustive reporting of Shapiro-Wilk normality and Levene homoscedasticity", "scoring_weight": 0.5},
                {"property_id": "PROP-SUBSTANTIVE-PRACTICAL-INTERPRETATION", "description": "Substantive clinical interpretation of Cohen's d magnitude", "scoring_weight": 0.5}
            ]

        elif level == 2:  # L02_PRE_POST
            n = 35
            rows = [["id", "group", "wellbeing_pre", "wellbeing_post"]]
            for i in range(1, n + 1):
                pre = cls._bounded_noise(18.5 + random.gauss(0, 3.0))
                post = cls._bounded_noise(pre + 4.8 + random.gauss(0, 2.1))
                rows.append([f"S_{i:03d}", "Intervention", pre, post])

            variables = [
                {"name": "id", "role": "identifier", "type": "categorical"},
                {"name": "group", "role": "factor", "type": "categorical"},
                {"name": "wellbeing_pre", "role": "covariate", "type": "numeric"},
                {"name": "wellbeing_post", "role": "dependent_variable", "type": "numeric"}
            ]
            design = {
                "design_type": "WITHIN_SUBJECT_PRE_POST",
                "independent_variables": ["time"],
                "dependent_variables": ["wellbeing_post"],
                "covariates": ["wellbeing_pre"],
                "factors": ["time"],
                "sample_allocation": "EQUAL"
            }
            invariants = [
                {"invariant_id": "INV-REPEATED-MEASURES-STRUCTURE", "description": "Within-subject paired structure recognized (paired t-test or RM-ANOVA)", "verification_dimension": "METHODOLOGICAL_INTEGRITY", "evaluation_rule": "paired_structure"},
                {"invariant_id": "INV-EFFECT-SIZE-REPORTED", "description": "Cohen's d_z or partial eta squared reported", "verification_dimension": "STATISTICAL_RIGOR", "evaluation_rule": "effect_size_present"},
                {"invariant_id": "INV-PERSIAN-LEADING-ZERO", "description": "Persian reporting retains leading zero (۰.۰۵)", "verification_dimension": "APA_TYPOGRAPHY", "evaluation_rule": "persian_leading_zero"}
            ]
            pitfalls = [
                {"pitfall_id": "PIT-TREATING-PAIRED-AS-INDEPENDENT", "description": "Executing independent samples t-test on paired pre-post observations", "trigger_condition": "unpaired_t_test_on_paired_data"},
                {"pitfall_id": "PIT-P-EQUALS-ZERO", "description": "Reporting p = .000", "trigger_condition": "p_equals_zero_reported"}
            ]
            gold = [
                {"property_id": "PROP-PRECISION-BOUNDED-ESTIMATES", "description": "Reporting 95% confidence intervals on mean gain score", "scoring_weight": 0.5},
                {"property_id": "PROP-SUBSTANTIVE-PRACTICAL-INTERPRETATION", "description": "Evaluating pre-to-post change in clinical terms", "scoring_weight": 0.5}
            ]

        elif level == 3:  # L03_THREE_GROUP_RM
            n_per = 20
            rows = [["id", "group", "depressive_pre", "depressive_post", "depressive_followup"]]
            for grp, pre_m, post_m, fu_m in [("CBT", 28.4, 17.2, 16.5), ("ACT", 28.1, 18.0, 17.1), ("Waitlist", 28.0, 26.8, 27.2)]:
                for i in range(1, n_per + 1):
                    pre = cls._bounded_noise(pre_m + random.gauss(0, 3.5))
                    post = cls._bounded_noise(post_m + random.gauss(0, 3.2))
                    fu = cls._bounded_noise(fu_m + random.gauss(0, 3.4))
                    rows.append([f"{grp}_{i:03d}", grp, pre, post, fu])

            variables = [
                {"name": "id", "role": "identifier", "type": "categorical"},
                {"name": "group", "role": "independent_variable", "type": "categorical"},
                {"name": "depressive_pre", "role": "covariate", "type": "numeric"},
                {"name": "depressive_post", "role": "dependent_variable", "type": "numeric"},
                {"name": "depressive_followup", "role": "dependent_variable", "type": "numeric"}
            ]
            design = {
                "design_type": "MIXED_REPEATED_MEASURES_3X3",
                "independent_variables": ["group", "time"],
                "dependent_variables": ["depressive_post", "depressive_followup"],
                "covariates": ["depressive_pre"],
                "factors": ["group", "time"],
                "sample_allocation": "EQUAL"
            }
            invariants = [
                {"invariant_id": "INV-SPHERICITY-VERIFIED", "description": "Mauchly's test of sphericity evaluated", "verification_dimension": "STATISTICAL_RIGOR", "evaluation_rule": "mauchly_w_reported"},
                {"invariant_id": "INV-INTERACTION-EFFECT-EVALUATED", "description": "Group x Time interaction effect explicitly tested", "verification_dimension": "METHODOLOGICAL_INTEGRITY", "evaluation_rule": "interaction_tested"},
                {"invariant_id": "INV-EFFECT-SIZE-REPORTED", "description": "Partial eta squared reported for main and interaction effects", "verification_dimension": "STATISTICAL_RIGOR", "evaluation_rule": "partial_eta_squared"}
            ]
            pitfalls = [
                {"pitfall_id": "PIT-OMITTING-MAUCHLY-SPHERICITY", "description": "Omitting Mauchly's test of sphericity in repeated measures", "trigger_condition": "missing_mauchly"},
                {"pitfall_id": "PIT-IGNORING-TIME-INTERACTION", "description": "Collapsing assessment waves without evaluating Group x Time interaction", "trigger_condition": "ignoring_interaction"}
            ]
            gold = [
                {"property_id": "PROP-MODEL-COMPARISON", "description": "Greenhouse-Geisser vs Huynh-Feldt epsilon corrections evaluated", "scoring_weight": 0.5},
                {"property_id": "PROP-POST-HOC-CONTRASTS", "description": "Simple main effects decomposed across groups with Bonferroni correction", "scoring_weight": 0.5}
            ]

        elif level == 4:  # L04_MISSING_FOLLOWUP
            n_per = 20
            rows = [["id", "group", "score_pre", "score_post", "score_followup"]]
            for grp, pre_m, post_m, fu_m in [("Intervention", 20.0, 32.0, 30.5), ("Control", 19.8, 21.0, 20.8)]:
                for i in range(1, n_per + 1):
                    pre = cls._bounded_noise(pre_m + random.gauss(0, 3.0))
                    post = cls._bounded_noise(post_m + random.gauss(0, 3.0))
                    # 25% missingness at followup
                    fu = "" if (i % 4 == 0) else cls._bounded_noise(fu_m + random.gauss(0, 3.2))
                    rows.append([f"{grp[:3]}_{i:03d}", grp, pre, post, fu])

            variables = [
                {"name": "id", "role": "identifier", "type": "categorical"},
                {"name": "group", "role": "independent_variable", "type": "categorical"},
                {"name": "score_pre", "role": "covariate", "type": "numeric"},
                {"name": "score_post", "role": "dependent_variable", "type": "numeric"},
                {"name": "score_followup", "role": "dependent_variable", "type": "numeric"}
            ]
            design = {
                "design_type": "LONGITUDINAL_ATTRITION_TRIAL",
                "independent_variables": ["group", "time"],
                "dependent_variables": ["score_post", "score_followup"],
                "covariates": ["score_pre"],
                "factors": ["group", "time"],
                "sample_allocation": "EQUAL"
            }
            invariants = [
                {"invariant_id": "INV-MISSINGNESS-DIAGNOSED", "description": "Missingness mechanism evaluated (Little's MCAR or attrition pattern)", "verification_dimension": "METHODOLOGICAL_INTEGRITY", "evaluation_rule": "missingness_evaluated"},
                {"invariant_id": "INV-ESTIMAND-FORMULATION", "description": "Target estimand formulated accounting for subject attrition", "verification_dimension": "STATISTICAL_RIGOR", "evaluation_rule": "estimand_defined"}
            ]
            pitfalls = [
                {"pitfall_id": "PIT-IGNORING-MISSINGNESS", "description": "Complete-case listwise deletion applied without missingness diagnosis", "trigger_condition": "unjustified_listwise_deletion"},
                {"pitfall_id": "PIT-P-EQUALS-ZERO", "description": "Reporting p = .000", "trigger_condition": "p_equals_zero_reported"}
            ]
            gold = [
                {"property_id": "PROP-SENSITIVITY-ANALYSIS", "description": "Sensitivity analysis comparing complete-case analysis against linear mixed model", "scoring_weight": 0.6},
                {"property_id": "PROP-ASSUMPTION-DIAGNOSTICS", "description": "Little's MCAR test reported with chi-square and p-value", "scoring_weight": 0.4}
            ]

        elif level == 5:  # L05_UNEQUAL_GROUPS
            rows = [["id", "group", "performance_score"]]
            cell_counts = [("Group_A", 60, 45.2, 4.0), ("Group_B", 25, 52.8, 6.5), ("Group_C", 18, 38.4, 7.8)]
            for grp, n_grp, mean_val, sd_val in cell_counts:
                for i in range(1, n_grp + 1):
                    rows.append([f"{grp}_{i:03d}", grp, cls._bounded_noise(mean_val + random.gauss(0, sd_val))])

            variables = [
                {"name": "id", "role": "identifier", "type": "categorical"},
                {"name": "group", "role": "independent_variable", "type": "categorical"},
                {"name": "performance_score", "role": "dependent_variable", "type": "numeric"}
            ]
            design = {
                "design_type": "UNBALANCED_FACTORIAL_ANOVA",
                "independent_variables": ["group"],
                "dependent_variables": ["performance_score"],
                "covariates": [],
                "factors": ["group"],
                "sample_allocation": "UNEQUAL"
            }
            invariants = [
                {"invariant_id": "INV-TYPE-III-SS", "description": "Type III sums of squares employed due to severe cell imbalance", "verification_dimension": "STATISTICAL_RIGOR", "evaluation_rule": "type_iii_ss"},
                {"invariant_id": "INV-ROBUST-VARIANCE-ADJUSTMENT", "description": "Welch's F or Brown-Forsythe evaluated under variance heterogeneity", "verification_dimension": "STATISTICAL_RIGOR", "evaluation_rule": "welch_f"}
            ]
            pitfalls = [
                {"pitfall_id": "PIT-TYPE-I-SS-UNDER-IMBALANCE", "description": "Using Type I sequential SS when sample cell sizes are unequal", "trigger_condition": "type_i_ss"},
                {"pitfall_id": "PIT-ASSUMING-EQUAL-VARIANCES", "description": "Assuming variance homogeneity despite severe sample size ratio disparity", "trigger_condition": "untested_variance"}
            ]
            gold = [
                {"property_id": "PROP-MODEL-COMPARISON", "description": "Comparing standard ANOVA F-test with Welch robust ANOVA", "scoring_weight": 0.5},
                {"property_id": "PROP-GAMES-HOWELL-POSTHOC", "description": "Applying Games-Howell post-hoc test suited for unequal variances", "scoring_weight": 0.5}
            ]

        elif level == 6:  # L06_BASELINE_IMBALANCE
            n_per = 25
            rows = [["id", "group", "pre_test_score", "post_test_score"]]
            # Treatment baseline mean ~18.2, Control baseline mean ~22.8 (baseline disparity)
            for i in range(1, n_per + 1):
                pre = cls._bounded_noise(18.2 + random.gauss(0, 3.2))
                post = cls._bounded_noise(28.5 + 0.65 * (pre - 18.2) + random.gauss(0, 2.4))
                rows.append([f"T_{i:03d}", "Treatment", pre, post])
            for i in range(1, n_per + 1):
                pre = cls._bounded_noise(22.8 + random.gauss(0, 3.1))
                post = cls._bounded_noise(23.4 + 0.65 * (pre - 22.8) + random.gauss(0, 2.5))
                rows.append([f"C_{i:03d}", "Control", pre, post])

            variables = [
                {"name": "id", "role": "identifier", "type": "categorical"},
                {"name": "group", "role": "independent_variable", "type": "categorical"},
                {"name": "pre_test_score", "role": "covariate", "type": "numeric"},
                {"name": "post_test_score", "role": "dependent_variable", "type": "numeric"}
            ]
            design = {
                "design_type": "PRE_POST_ANCOVA",
                "independent_variables": ["group"],
                "dependent_variables": ["post_test_score"],
                "covariates": ["pre_test_score"],
                "factors": ["group"],
                "sample_allocation": "EQUAL"
            }
            invariants = [
                {"invariant_id": "INV-HOMOGENEITY-OF-SLOPES-VERIFIED", "description": "Homogeneity of regression slopes tested (Group x Covariate interaction p > .05)", "verification_dimension": "METHODOLOGICAL_INTEGRITY", "evaluation_rule": "slopes_homogeneity"},
                {"invariant_id": "INV-BASELINE-COVARIATE-CONTROLLED", "description": "Baseline pre-test score included as covariate in general linear model", "verification_dimension": "STATISTICAL_RIGOR", "evaluation_rule": "covariate_controlled"},
                {"invariant_id": "INV-EFFECT-SIZE-REPORTED", "description": "Partial eta squared reported for ANCOVA treatment effect", "verification_dimension": "STATISTICAL_RIGOR", "evaluation_rule": "partial_eta_squared"},
                {"invariant_id": "INV-PERSIAN-LEADING-ZERO", "description": "Leading zero retained in Persian numbers (۰.۰۵)", "verification_dimension": "APA_TYPOGRAPHY", "evaluation_rule": "persian_leading_zero"}
            ]
            pitfalls = [
                {"pitfall_id": "PIT-OMITTING-SLOPE-HOMOGENEITY", "description": "Executing ANCOVA without verifying homogeneity of regression slopes", "trigger_condition": "missing_slope_homogeneity"},
                {"pitfall_id": "PIT-UNCONTROLLED-BASELINE-CONFOUNDING", "description": "Analyzing post-test scores via raw ANOVA ignoring significant baseline disparity", "trigger_condition": "ignoring_baseline_disparity"}
            ]
            gold = [
                {"property_id": "PROP-MODEL-COMPARISON", "description": "Explicit comparison of unadjusted ANOVA F-test vs covariate-adjusted ANCOVA", "scoring_weight": 0.5},
                {"property_id": "PROP-ADJUSTED-MEANS-REPORTED", "description": "Reporting adjusted marginal means (estimated marginal means) with standard errors", "scoring_weight": 0.5}
            ]

        elif level == 7:  # L07_MISSING_IMBALANCE_COV
            rows = [["id", "group", "baseline_covariate", "outcome_post", "outcome_followup"]]
            for grp, n_grp, pre_m, post_m, fu_m in [("Treatment", 45, 19.5, 31.0, 30.2), ("Control", 25, 22.0, 23.5, 23.0)]:
                for i in range(1, n_grp + 1):
                    pre = cls._bounded_noise(pre_m + random.gauss(0, 3.0))
                    post = cls._bounded_noise(post_m + 0.5 * (pre - pre_m) + random.gauss(0, 2.5))
                    fu = "" if (i % 5 == 0) else cls._bounded_noise(fu_m + 0.5 * (pre - pre_m) + random.gauss(0, 2.7))
                    rows.append([f"{grp[:3]}_{i:03d}", grp, pre, post, fu])

            variables = [
                {"name": "id", "role": "identifier", "type": "categorical"},
                {"name": "group", "role": "independent_variable", "type": "categorical"},
                {"name": "baseline_covariate", "role": "covariate", "type": "numeric"},
                {"name": "outcome_post", "role": "dependent_variable", "type": "numeric"},
                {"name": "outcome_followup", "role": "dependent_variable", "type": "numeric"}
            ]
            design = {
                "design_type": "UNBALANCED_LONGITUDINAL_ANCOVA",
                "independent_variables": ["group", "time"],
                "dependent_variables": ["outcome_post", "outcome_followup"],
                "covariates": ["baseline_covariate"],
                "factors": ["group", "time"],
                "sample_allocation": "UNEQUAL"
            }
            invariants = [
                {"invariant_id": "INV-CANDIDATE-MODEL-COMPARISON", "description": "Multiple candidate modeling approaches compared (e.g. repeated ANCOVA vs LMM)", "verification_dimension": "METHODOLOGICAL_INTEGRITY", "evaluation_rule": "model_comparison"},
                {"invariant_id": "INV-MISSINGNESS-DIAGNOSED", "description": "Attrition and missingness mechanism formally evaluated", "verification_dimension": "METHODOLOGICAL_INTEGRITY", "evaluation_rule": "missingness_evaluated"},
                {"invariant_id": "INV-ESTIMAND-FORMULATION", "description": "Explicit estimand definition", "verification_dimension": "STATISTICAL_RIGOR", "evaluation_rule": "estimand_defined"}
            ]
            pitfalls = [
                {"pitfall_id": "PIT-UNJUSTIFIED-MODEL-SELECTION", "description": "Selecting an analytic model without candidate model comparison", "trigger_condition": "unjustified_model_selection"}
            ]
            gold = [
                {"property_id": "PROP-AIC-BIC-COMPARISON", "description": "Comparing information criteria (AIC/BIC) across covariance specifications", "scoring_weight": 0.6},
                {"property_id": "PROP-PRECISION-BOUNDED-ESTIMATES", "description": "95% confidence intervals on fixed effects", "scoring_weight": 0.4}
            ]

        elif level == 8:  # L08_MULTIPLE_OUTCOMES
            n_per = 30
            rows = [["id", "group", "outcome_anxiety", "outcome_depression", "outcome_stress", "outcome_resilience", "outcome_sleep"]]
            for grp, an_m, dep_m, str_m, res_m, slp_m in [("Treatment", 14.2, 12.5, 15.0, 38.5, 24.2), ("Control", 19.8, 18.2, 21.4, 29.0, 18.5)]:
                for i in range(1, n_per + 1):
                    anx = cls._bounded_noise(an_m + random.gauss(0, 3.2))
                    dep = cls._bounded_noise(dep_m + 0.6 * (anx - an_m) + random.gauss(0, 2.5))
                    stres = cls._bounded_noise(str_m + 0.5 * (anx - an_m) + random.gauss(0, 2.8))
                    resil = cls._bounded_noise(res_m - 0.4 * (anx - an_m) + random.gauss(0, 3.5))
                    sleep = cls._bounded_noise(slp_m - 0.5 * (anx - an_m) + random.gauss(0, 3.0))
                    rows.append([f"{grp[:3]}_{i:03d}", grp, anx, dep, stres, resil, sleep])

            variables = [
                {"name": "id", "role": "identifier", "type": "categorical"},
                {"name": "group", "role": "independent_variable", "type": "categorical"},
                {"name": "outcome_anxiety", "role": "dependent_variable", "type": "numeric"},
                {"name": "outcome_depression", "role": "dependent_variable", "type": "numeric"},
                {"name": "outcome_stress", "role": "dependent_variable", "type": "numeric"},
                {"name": "outcome_resilience", "role": "dependent_variable", "type": "numeric"},
                {"name": "outcome_sleep", "role": "dependent_variable", "type": "numeric"}
            ]
            design = {
                "design_type": "MULTIVARIATE_MANOVA",
                "independent_variables": ["group"],
                "dependent_variables": ["outcome_anxiety", "outcome_depression", "outcome_stress", "outcome_resilience", "outcome_sleep"],
                "covariates": [],
                "factors": ["group"],
                "sample_allocation": "EQUAL"
            }
            invariants = [
                {"invariant_id": "INV-FAMILYWISE-ERROR-CONTROL", "description": "Control of familywise Type I error rate via MANOVA omnibus test or Bonferroni/Holm correction", "verification_dimension": "STATISTICAL_RIGOR", "evaluation_rule": "fwer_control"},
                {"invariant_id": "INV-MULTIVARIATE-CORRELATION", "description": "Multivariate intercorrelation structure of outcome measures reported", "verification_dimension": "STATISTICAL_RIGOR", "evaluation_rule": "correlation_reported"}
            ]
            pitfalls = [
                {"pitfall_id": "PIT-P-HACKING-OUTCOME-CHERRY-PICKING", "description": "Conducting multiple independent univariate t-tests without multiplicity adjustment", "trigger_condition": "unadjusted_multiple_testing"}
            ]
            gold = [
                {"property_id": "PROP-WILKS-LAMBDA-REPORTED", "description": "Multivariate omnibus Wilks' Lambda reported with exact F and partial eta squared", "scoring_weight": 0.5},
                {"property_id": "PROP-INTERCORRELATION-MATRIX", "description": "Correlation matrix across all 5 dependent measures documented", "scoring_weight": 0.5}
            ]

        elif level == 9:  # L09_COMPLEX_LONGITUDINAL
            n_tot = 50
            rows = [["id", "group", "wave_1", "wave_2", "wave_3", "wave_4", "wave_5"]]
            for i in range(1, n_tot + 1):
                grp = "Intervention" if i <= 25 else "Control"
                drift = -1.5 if grp == "Intervention" else 0.2
                w1 = cls._bounded_noise(30.0 + random.gauss(0, 3.5))
                w2 = cls._bounded_noise(w1 + drift + random.gauss(0, 1.8))
                w3 = cls._bounded_noise(w2 + drift + random.gauss(0, 1.8))
                w4 = cls._bounded_noise(w3 + drift + random.gauss(0, 1.8))
                w5 = cls._bounded_noise(w4 + drift + random.gauss(0, 1.8))
                rows.append([f"S_{i:03d}", grp, w1, w2, w3, w4, w5])

            variables = [
                {"name": "id", "role": "identifier", "type": "categorical"},
                {"name": "group", "role": "independent_variable", "type": "categorical"},
                {"name": "wave_1", "role": "covariate", "type": "numeric"},
                {"name": "wave_2", "role": "dependent_variable", "type": "numeric"},
                {"name": "wave_3", "role": "dependent_variable", "type": "numeric"},
                {"name": "wave_4", "role": "dependent_variable", "type": "numeric"},
                {"name": "wave_5", "role": "dependent_variable", "type": "numeric"}
            ]
            design = {
                "design_type": "FIVE_WAVE_LONGITUDINAL_PANEL",
                "independent_variables": ["group", "wave"],
                "dependent_variables": ["wave_2", "wave_3", "wave_4", "wave_5"],
                "covariates": ["wave_1"],
                "factors": ["group", "wave"],
                "sample_allocation": "EQUAL"
            }
            invariants = [
                {"invariant_id": "INV-COVARIANCE-STRUCTURE-COMPARISON", "description": "Candidate covariance structures compared (AR1 vs Toeplitz vs Unstructured)", "verification_dimension": "METHODOLOGICAL_INTEGRITY", "evaluation_rule": "covariance_comparison"},
                {"invariant_id": "INV-REPEATED-MEASURES-STRUCTURE", "description": "Autoregressive within-subject correlation modeled", "verification_dimension": "STATISTICAL_RIGOR", "evaluation_rule": "longitudinal_structure"}
            ]
            pitfalls = [
                {"pitfall_id": "PIT-COMPOUND-SYMMETRY-DEFAULT", "description": "Imposing compound symmetry assumption onto multi-wave panel data without testing", "trigger_condition": "untested_compound_symmetry"}
            ]
            gold = [
                {"property_id": "PROP-AIC-BIC-COMPARISON", "description": "Model selection table presenting AIC, BIC, and -2LL across covariance matrices", "scoring_weight": 0.6},
                {"property_id": "PROP-GROWTH-TRAJECTORY-ESTIMATION", "description": "Individual linear and quadratic growth trajectories modeled", "scoring_weight": 0.4}
            ]

        else:  # level 10: L10_AMBIGUOUS_DESIGN
            n_tot = 80
            rows = [["id", "treatment_exposure", "confounder_ses", "confounder_age", "outcome_health"]]
            for i in range(1, n_tot + 1):
                ses = cls._bounded_noise(random.gauss(50, 10))
                age = cls._bounded_noise(random.gauss(42, 12))
                # Propensity of exposure depends on SES and age
                prob_exp = 1.0 / (1.0 + math.exp(-(-2.0 + 0.04 * ses + 0.02 * age)))
                exposure = 1 if random.random() < prob_exp else 0
                outcome = cls._bounded_noise(35.0 + 4.5 * exposure + 0.35 * ses - 0.2 * age + random.gauss(0, 4.0))
                rows.append([f"P_{i:03d}", exposure, ses, age, outcome])

            variables = [
                {"name": "id", "role": "identifier", "type": "categorical"},
                {"name": "treatment_exposure", "role": "independent_variable", "type": "integer"},
                {"name": "confounder_ses", "role": "covariate", "type": "numeric"},
                {"name": "confounder_age", "role": "covariate", "type": "numeric"},
                {"name": "outcome_health", "role": "dependent_variable", "type": "numeric"}
            ]
            design = {
                "design_type": "OBSERVATIONAL_CROSS_SECTIONAL",
                "independent_variables": ["treatment_exposure"],
                "dependent_variables": ["outcome_health"],
                "covariates": ["confounder_ses", "confounder_age"],
                "factors": ["treatment_exposure"],
                "sample_allocation": "UNEQUAL"
            }
            invariants = [
                {"invariant_id": "INV-EPISTEMIC-HONESTY", "description": "Language strictly associative; zero causal claims in observational design", "verification_dimension": "METHODOLOGICAL_INTEGRITY", "evaluation_rule": "associative_language"},
                {"invariant_id": "INV-ESTIMAND-FORMULATION", "description": "Target estimand formulated with sensitivity bounds for unmeasured confounding", "verification_dimension": "STATISTICAL_RIGOR", "evaluation_rule": "estimand_defined"}
            ]
            pitfalls = [
                {"pitfall_id": "PIT-UNSUPPORTED-CAUSAL-LANGUAGE", "description": "Using causal verbs (causes, proves, اثر علی) in observational non-randomized study", "trigger_condition": "unsupported_causal_language"}
            ]
            gold = [
                {"property_id": "PROP-SENSITIVITY-ANALYSIS", "description": "E-value or sensitivity analysis for unmeasured confounding reported", "scoring_weight": 0.5},
                {"property_id": "PROP-PROPENSITY-SCORE-DISCUSSION", "description": "Propensity adjustment or selection bias mechanisms discussed", "scoring_weight": 0.5}
            ]

        # 2. Write CSV to disk
        with open(abs_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        # 3. Compute SHA256
        with open(abs_path, "rb") as f:
            sha256_hash = hashlib.sha256(f.read()).hexdigest()

        sample_size = len(rows) - 1

        dataset = {
            "path": rel_path,
            "sha256": sha256_hash,
            "format": "csv",
            "sample_size": sample_size,
            "variables": variables
        }

        provenance = {
            "source_type": "CALIBRATED_PSYCHOMETRIC_SIMULATION",
            "generator_script": "scripts/academic_curriculum_builder.py",
            "noise_injected": True,
            "dataset_sha256": sha256_hash,
            "generation_timestamp": datetime.now(timezone.utc).isoformat(),
            "parameters": {
                "level": level,
                "ladder_code": code,
                "sample_size": sample_size,
                "noise_bounds": [0.08, 0.25],
                **({"synthetic_parameters": params} if params else {})
            }
        }

        return {
            "dataset": dataset,
            "data_provenance": provenance,
            "design": design,
            "expected_invariants": invariants,
            "expected_pitfalls": pitfalls,
            "gold_behavioral_properties": gold
        }

    @classmethod
    def _generate_writing_case(
        cls,
        abs_path: str,
        rel_path: str,
        case_id: str,
        code: str,
        level: int,
        params: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generates writing benchmark dataset and behavioral invariants for levels 1-5."""
        # Create corresponding empirical reference dataset for writing interpretation
        n = 30
        rows = [["id", "group", "score", "pre_score"]]
        for i in range(1, n + 1):
            grp = "Treatment" if i <= 15 else "Control"
            pre = cls._bounded_noise(20.0 + random.gauss(0, 3.0))
            diff = 6.2 if grp == "Treatment" else 0.5
            post = cls._bounded_noise(pre + diff + random.gauss(0, 2.5))
            rows.append([f"W_{i:03d}", grp, post, pre])

        with open(abs_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        with open(abs_path, "rb") as f:
            sha256_hash = hashlib.sha256(f.read()).hexdigest()

        variables = [
            {"name": "id", "role": "identifier", "type": "categorical"},
            {"name": "group", "role": "independent_variable", "type": "categorical"},
            {"name": "score", "role": "dependent_variable", "type": "numeric"},
            {"name": "pre_score", "role": "covariate", "type": "numeric"}
        ]
        design = {
            "design_type": "EXPERIMENTAL_RCT_WRITING_BENCHMARK",
            "independent_variables": ["group"],
            "dependent_variables": ["score"],
            "covariates": ["pre_score"],
            "factors": ["group"],
            "sample_allocation": "EQUAL"
        }

        if level == 1:  # W01_BASIC_NARRATION
            invariants = [
                {"invariant_id": "INV-PERSIAN-LEADING-ZERO", "description": "Leading zero strictly retained in Persian statistical numbers (۰.۰۵, not .۰۵)", "verification_dimension": "APA_TYPOGRAPHY", "evaluation_rule": "persian_leading_zero"},
                {"invariant_id": "INV-APA-ITALICIZATION", "description": "Statistical symbols (F, t, p, M, SD) italicized in text", "verification_dimension": "APA_TYPOGRAPHY", "evaluation_rule": "apa_italicization"}
            ]
            pitfalls = [
                {"pitfall_id": "PIT-P-EQUALS-ZERO", "description": "Reporting p = .000 or ۰.۰۰۰", "trigger_condition": "p_equals_zero_reported"},
                {"pitfall_id": "PIT-MISSING-PERSIAN-LEADING-ZERO", "description": "Omitting leading zero in Persian (e.g. .۰۵)", "trigger_condition": "missing_leading_zero"}
            ]
            gold = [
                {"property_id": "PROP-HALF-SPACE-TYPOGRAPHY", "description": "Pristine Persian half-space typography observed", "scoring_weight": 0.5},
                {"property_id": "PROP-APA-THREE-LINE-TABLE", "description": "Results structured in APA 7 3-line table format", "scoring_weight": 0.5}
            ]
        elif level == 2:  # W02_EFFECT_SIZE_INTERPRETATION
            invariants = [
                {"invariant_id": "INV-EFFECT-SIZE-REPORTED", "description": "Effect size (Cohen's d or partial eta squared) reported", "verification_dimension": "STATISTICAL_RIGOR", "evaluation_rule": "effect_size_present"},
                {"invariant_id": "INV-SUBSTANTIVE-PRACTICAL-IMPORTANCE", "description": "Substantive clinical or practical significance interpreted beyond binary p-value", "verification_dimension": "REASONING_COHERENCE", "evaluation_rule": "practical_significance_interpreted"}
            ]
            pitfalls = [
                {"pitfall_id": "PIT-CONFLATING-SIGNIFICANCE-WITH-IMPORTANCE", "description": "Conflating statistical significance with substantive real-world importance", "trigger_condition": "significance_conflated"}
            ]
            gold = [
                {"property_id": "PROP-CLINICAL-BENCHMARKING", "description": "Benchmarking effect size against empirical literature standards", "scoring_weight": 0.5}
            ]
        elif level == 3:  # W03_CI_INTERPRETATION
            invariants = [
                {"invariant_id": "INV-CONFIDENCE-INTERVAL-BOUNDED", "description": "95% confidence intervals reported for parameters", "verification_dimension": "STATISTICAL_RIGOR", "evaluation_rule": "ci_present"},
                {"invariant_id": "INV-PRECISION-INTERPRETATION", "description": "Estimation precision interpreted based on CI width", "verification_dimension": "REASONING_COHERENCE", "evaluation_rule": "precision_interpreted"}
            ]
            pitfalls = [
                {"pitfall_id": "PIT-IGNORING-CONFIDENCE-INTERVAL", "description": "Omitting confidence intervals or ignoring estimate imprecision", "trigger_condition": "missing_ci"}
            ]
            gold = [
                {"property_id": "PROP-BOOTSTRAP-CI-REPORTING", "description": "Reporting BCa bootstrap confidence intervals", "scoring_weight": 0.5}
            ]
        elif level == 4:  # W04_CAUSAL_DISCIPLINE
            invariants = [
                {"invariant_id": "INV-ASSOCIATIVE-LANGUAGE-DISCIPLINE", "description": "Associative language strictly maintained; no causal claims without experimental manipulation", "verification_dimension": "METHODOLOGICAL_INTEGRITY", "evaluation_rule": "associative_language"},
                {"invariant_id": "INV-EPISTEMIC-HONESTY", "description": "Epistemic modesty avoiding claims of absolute empirical proof", "verification_dimension": "REASONING_COHERENCE", "evaluation_rule": "epistemic_modesty"}
            ]
            pitfalls = [
                {"pitfall_id": "PIT-UNSUPPORTED-CAUSAL-LANGUAGE", "description": "Using causal verbs (causes, proves, اثبات کرد, منجر به علیت شد)", "trigger_condition": "causal_language_in_correlational"}
            ]
            gold = [
                {"property_id": "PROP-ALTERNATIVE-EXPLANATIONS", "description": "Explicitly discussing third-variable or reverse causality explanations", "scoring_weight": 0.5}
            ]
        else:  # W05_CONTRADICTORY_RESULTS
            invariants = [
                {"invariant_id": "INV-HONEST-REPORTING-OF-NULLS", "description": "Non-significant findings (p > .05) reported candidly without defensive distortion", "verification_dimension": "REASONING_COHERENCE", "evaluation_rule": "honest_null_reporting"},
                {"invariant_id": "INV-POWER-LIMITATION-DISCUSSION", "description": "Statistical power limitations and theoretical implications evaluated for nulls", "verification_dimension": "METHODOLOGICAL_INTEGRITY", "evaluation_rule": "power_discussed"}
            ]
            pitfalls = [
                {"pitfall_id": "PIT-DEFENSIVE-RATIONALIZATION-OF-NULLS", "description": "Spinning or defensive rationalization of non-significant findings", "trigger_condition": "defensive_rationalization"},
                {"pitfall_id": "PIT-P-HACKING-JUSTIFICATION", "description": "Suggesting subgroup cherry-picking to achieve significance", "trigger_condition": "p_hacking"}
            ]
            gold = [
                {"property_id": "PROP-POSTHOC-POWER-OR-EQUIVALENCE", "description": "Addressing statistical power or equivalence bounds for non-significant effects", "scoring_weight": 0.5}
            ]

        dataset = {
            "path": rel_path,
            "sha256": sha256_hash,
            "format": "csv",
            "sample_size": n,
            "variables": variables
        }
        provenance = {
            "source_type": "EMPIRICAL_BENCHMARK",
            "generator_script": "scripts/academic_curriculum_builder.py",
            "noise_injected": True,
            "dataset_sha256": sha256_hash,
            "generation_timestamp": datetime.now(timezone.utc).isoformat(),
            "parameters": {
                "level": level,
                "ladder_code": code,
                "sample_size": n,
                **({"synthetic_parameters": params} if params else {})
            }
        }
        return {
            "dataset": dataset,
            "data_provenance": provenance,
            "design": design,
            "expected_invariants": invariants,
            "expected_pitfalls": pitfalls,
            "gold_behavioral_properties": gold
        }
