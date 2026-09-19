#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
evals/benchmarks/benchmark_definitions.py — Benchmark Case Specifications

Authoritative definitions of must_do, must_not_do, and required_evidence across
all 18 academic behavioral benchmark families.
"""

from typing import Dict, Any

CASE_DEFINITIONS: Dict[str, Any] = {
    "DATA_CLEANING": {
        "title": "Psychometric Survey Screening, Reverse-Coding, and Composite Aggregation",
        "rq": "Are multi-item psychological scales appropriately screened for range violations, reverse-coded, and aggregated into reliable composite indicators?",
        "design": {"design_type": "CROSS_SECTIONAL_SURVEY", "scales": ["Resilience"], "items": 10, "reverse_items": [4, 7, 10]},
        "target_capability": "data-cleaning",
        "must_do": [
            {"action_id": "MUST-CLEAN-01", "description": "Identify and reverse-code negatively phrased items 4, 7, and 10 using formula: 6 - x.", "category": "METHODOLOGICAL_REQUIREMENT", "verification_rule": "check_reversed_columns_computed"},
            {"action_id": "MUST-CLEAN-02", "description": "Screen for invalid response values outside 1-5 Likert range.", "category": "ASSUMPTION_CHECK", "verification_rule": "check_range_screening_reported"},
            {"action_id": "MUST-CLEAN-03", "description": "Compute verified composite total score preserving transparent audit log.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_composite_score_calculated"}
        ],
        "must_not_do": [
            {"pitfall_id": "NOT-CLEAN-01", "description": "Sum or average raw items without reverse-coding negative indicators.", "severity": "CRITICAL", "detection_rule": "detect_unreversed_aggregation"},
            {"pitfall_id": "NOT-CLEAN-02", "description": "Destructively overwrite original raw survey columns without audit trail.", "severity": "MAJOR", "detection_rule": "detect_destructive_in_place_overwrite"}
        ],
        "required_evidence": [
            {"evidence_id": "EVID-CLEAN-01", "description": "Transformation audit log mapping raw items to reverse-coded items.", "evidence_type": "ARTIFACT_FILE", "verification_method": "FILE_EXISTS", "file_pattern": ".*clean.*audit.*json"},
            {"evidence_id": "EVID-CLEAN-02", "description": "Cleaned dataset with verified SHA256 and composite scores.", "evidence_type": "ARTIFACT_FILE", "verification_method": "HASH_VERIFIED"}
        ]
    },
    "MISSING_DATA": {
        "title": "Missing Data Mechanism Diagnosis via Little's MCAR and Principled Imputation",
        "rq": "Does the missingness mechanism conform to MCAR, and what principled handling preserves unbiased parameter estimation?",
        "design": {"design_type": "OBSERVATIONAL_PANEL", "variables": ["burnout", "stress", "social_support", "coping_skills", "depression"]},
        "target_capability": "data-audit",
        "must_do": [
            {"action_id": "MUST-MISS-01", "description": "Calculate missingness percentage per variable and per subject.", "category": "METHODOLOGICAL_REQUIREMENT", "verification_rule": "check_missingness_rates_reported"},
            {"action_id": "MUST-MISS-02", "description": "Execute Little's MCAR test (chi2, df, p-value).", "category": "ASSUMPTION_CHECK", "verification_rule": "check_littles_mcar_executed"},
            {"action_id": "MUST-MISS-03", "description": "Apply modern FIML or multiple imputation (MICE) under MAR assumption.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_principled_handling_used"}
        ],
        "must_not_do": [
            {"pitfall_id": "NOT-MISS-01", "description": "Use naive mean imputation which severely deflates standard errors.", "severity": "CRITICAL", "detection_rule": "detect_mean_imputation"},
            {"pitfall_id": "NOT-MISS-02", "description": "Perform default listwise deletion when missingness exceeds 5% without testing MCAR.", "severity": "CRITICAL", "detection_rule": "detect_untested_listwise_deletion"}
        ],
        "required_evidence": [
            {"evidence_id": "EVID-MISS-01", "description": "Little's MCAR test statistics report.", "evidence_type": "DIAGNOSTIC_METRIC", "verification_method": "EXACT_MATCH", "metric_key": "littles_mcar_p"},
            {"evidence_id": "EVID-MISS-02", "description": "Missing pattern summary table.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"}
        ]
    },
    "OUTLIERS": {
        "title": "Multivariate Outlier Screening via Mahalanobis D2 and Cook's Influence Sensitivity",
        "rq": "Are multivariate outliers present in cognitive performance indices, and do they exert disproportionate influence on parameter estimates?",
        "design": {"design_type": "MULTIVARIATE_CROSS_SECTIONAL", "dimensions": 4},
        "target_capability": "data-audit",
        "must_do": [
            {"action_id": "MUST-OUT-01", "description": "Compute Mahalanobis distance D2 for all cases against chi2 distribution at p < .001.", "category": "ASSUMPTION_CHECK", "verification_rule": "check_mahalanobis_computed"},
            {"action_id": "MUST-OUT-02", "description": "Evaluate Cook's distance to determine parameter leverage.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_cooks_distance_evaluated"},
            {"action_id": "MUST-OUT-03", "description": "Conduct sensitivity analysis comparing models with and without influential cases.", "category": "METHODOLOGICAL_REQUIREMENT", "verification_rule": "check_sensitivity_analysis"}
        ],
        "must_not_do": [
            {"pitfall_id": "NOT-OUT-01", "description": "Silently delete extreme cases without reporting D2, df, and p-values.", "severity": "CRITICAL", "detection_rule": "detect_undocumented_deletion"},
            {"pitfall_id": "NOT-OUT-02", "description": "Rely solely on univariate inspection for multivariate models.", "severity": "MAJOR", "detection_rule": "detect_solely_univariate_screening"}
        ],
        "required_evidence": [
            {"evidence_id": "EVID-OUT-01", "description": "Mahalanobis D2 diagnostic table with critical cutoff.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"},
            {"evidence_id": "EVID-OUT-02", "description": "Sensitivity comparison table.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"}
        ]
    },
    "NORMALITY": {
        "title": "Parametric Univariate and Multivariate Normality Verification",
        "rq": "Do psychological outcome distributions satisfy parametric univariate and multivariate normality assumptions?",
        "design": {"design_type": "PARAMETRIC_ASSUMPTION_SUITE", "variables": ["life_satisfaction", "ptsd_symptoms", "generalized_anxiety"]},
        "target_capability": "assumption-testing",
        "must_do": [
            {"action_id": "MUST-NORM-01", "description": "Report univariate skewness, kurtosis, and Shapiro-Wilk W test with exact p-values.", "category": "ASSUMPTION_CHECK", "verification_rule": "check_shapiro_wilk_reported"},
            {"action_id": "MUST-NORM-02", "description": "Evaluate Mardia's multivariate skewness and kurtosis for multivariate modeling.", "category": "ASSUMPTION_CHECK", "verification_rule": "check_mardias_multivariate_reported"},
            {"action_id": "MUST-NORM-03", "description": "Preserve Persian leading zeros and recommend robust estimator (MLR/bootstrap) when violated.", "category": "REPORTING_STANDARD", "verification_rule": "check_robust_recommendation"}
        ],
        "must_not_do": [
            {"pitfall_id": "NOT-NORM-01", "description": "Report p = .000 for normality tests.", "severity": "CRITICAL", "detection_rule": "detect_p_equals_zero"},
            {"pitfall_id": "NOT-NORM-02", "description": "Proceed with standard parametric tests without robust corrections when normality fails.", "severity": "MAJOR", "detection_rule": "detect_uncorrected_normality_failure"}
        ],
        "required_evidence": [
            {"evidence_id": "EVID-NORM-01", "description": "Normality summary table with skewness, kurtosis, and Shapiro-Wilk p.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"},
            {"evidence_id": "EVID-NORM-02", "description": "Mardia's multivariate coefficient.", "evidence_type": "NUMERICAL_STATISTIC", "verification_method": "VALUE_IN_RANGE", "metric_key": "mardias_kurtosis"}
        ]
    },
    "RELIABILITY": {
        "title": "Psychometric Internal Consistency and McDonald's Omega Evaluation",
        "rq": "Does the depression inventory exhibit adequate internal consistency, and which items degrade scale coherence?",
        "design": {"design_type": "SCALE_RELIABILITY_ANALYSIS", "scale_name": "Depression Inventory", "items_count": 8},
        "target_capability": "reliability-analysis",
        "must_do": [
            {"action_id": "MUST-REL-01", "description": "Calculate Cronbach's alpha with 95% confidence interval.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_alpha_ci_reported"},
            {"action_id": "MUST-REL-02", "description": "Compute McDonald's omega as superior metric under tau-equivalence violations.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_omega_calculated"},
            {"action_id": "MUST-REL-03", "description": "Inspect corrected item-total correlations and alpha-if-item-deleted.", "category": "METHODOLOGICAL_REQUIREMENT", "verification_rule": "check_item_total_correlations"}
        ],
        "must_not_do": [
            {"pitfall_id": "NOT-REL-01", "description": "Compute single omnibus alpha across multi-dimensional scale without subscale breakdown.", "severity": "MAJOR", "detection_rule": "detect_omnibus_multidim_alpha"},
            {"pitfall_id": "NOT-REL-02", "description": "Retain item with negative or near-zero item-total correlation without diagnostic discussion.", "severity": "MAJOR", "detection_rule": "detect_unflagged_bad_item"}
        ],
        "required_evidence": [
            {"evidence_id": "EVID-REL-01", "description": "Scale reliability summary table reporting alpha and omega.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"},
            {"evidence_id": "EVID-REL-02", "description": "Item-total statistics table.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"}
        ]
    },
    "CFA": {
        "title": "Confirmatory Factor Analysis, Construct Reliability, and HTMT Discriminant Validity",
        "rq": "Does the 2-factor measurement model show construct validity, convergent validity, and adequate fit to empirical data?",
        "design": {"design_type": "CONFIRMATORY_FACTOR_ANALYSIS", "factors": ["CognitiveFlexibility", "EmotionalRegulation"], "indicators": 8},
        "target_capability": "cfa",
        "must_do": [
            {"action_id": "MUST-CFA-01", "description": "Report standardized factor loadings (lambda >= .50, p < .001).", "category": "STATISTICAL_RIGOR", "verification_rule": "check_factor_loadings"},
            {"action_id": "MUST-CFA-02", "description": "Calculate Average Variance Extracted (AVE >= .50) and Composite Reliability (CR >= .70).", "category": "STATISTICAL_RIGOR", "verification_rule": "check_ave_cr_calculated"},
            {"action_id": "MUST-CFA-03", "description": "Evaluate 11 Hu & Bentler (1999) fit indices (chi2/df, CFI >= .90, RMSEA <= .08, SRMR <= .08).", "category": "METHODOLOGICAL_REQUIREMENT", "verification_rule": "check_hu_bentler_fit"}
        ],
        "must_not_do": [
            {"pitfall_id": "NOT-CFA-01", "description": "Add post-hoc error covariances between different factors solely to improve fit indices.", "severity": "CRITICAL", "detection_rule": "detect_cross_factor_error_covariances"},
            {"pitfall_id": "NOT-CFA-02", "description": "Claim convergent validity when AVE < .50 or CR < .70.", "severity": "CRITICAL", "detection_rule": "detect_unwarranted_convergent_claim"}
        ],
        "required_evidence": [
            {"evidence_id": "EVID-CFA-01", "description": "Standardized factor loadings table.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"},
            {"evidence_id": "EVID-CFA-02", "description": "Construct validity matrix (AVE, CR, Cronbach alpha).", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"},
            {"evidence_id": "EVID-CFA-03", "description": "Hu & Bentler fit index table.", "evidence_type": "MODEL_FIT_INDEX", "verification_method": "FILE_EXISTS"}
        ]
    },
    "SEM": {
        "title": "Structural Equation Modeling with Anderson-Gerbing Two-Step Protocol",
        "rq": "Does perceived stress predict academic burnout directly and indirectly through sleep quality in university students?",
        "design": {"design_type": "STRUCTURAL_EQUATION_MODELING", "exogenous": "PerceivedStress", "endogenous": ["SleepQuality", "AcademicBurnout"]},
        "target_capability": "sem",
        "must_do": [
            {"action_id": "MUST-SEM-01", "description": "Validate measurement model prior to testing structural paths (Anderson & Gerbing 2-step).", "category": "METHODOLOGICAL_REQUIREMENT", "verification_rule": "check_two_step_approach"},
            {"action_id": "MUST-SEM-02", "description": "Report unstandardized B, standardized beta, SE, z, p, and R2 for endogenous constructs.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_path_coefficients_reported"},
            {"action_id": "MUST-SEM-03", "description": "Report complete fit indices (chi2, df, p, CFI, TLI, RMSEA, SRMR).", "category": "REPORTING_STANDARD", "verification_rule": "check_sem_fit_indices"}
        ],
        "must_not_do": [
            {"pitfall_id": "NOT-SEM-01", "description": "Report only standardized path coefficients without unstandardized B and SE.", "severity": "MAJOR", "detection_rule": "detect_missing_unstandardized_paths"},
            {"pitfall_id": "NOT-SEM-02", "description": "Make definitive causal claims from cross-sectional observational SEM data.", "severity": "CRITICAL", "detection_rule": "detect_causal_overreach"}
        ],
        "required_evidence": [
            {"evidence_id": "EVID-SEM-01", "description": "Structural paths regression table.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"},
            {"evidence_id": "EVID-SEM-02", "description": "Hypothesis decision matrix detailing confirmation status.", "evidence_type": "ARTIFACT_FILE", "verification_method": "FILE_EXISTS"}
        ]
    },
    "MEDIATION": {
        "title": "Preacher & Hayes Bootstrap Mediation Analysis with 5,000 Resamples",
        "rq": "Does rumination mediate the relationship between dispositional mindfulness and generalized anxiety?",
        "design": {"design_type": "BOOTSTRAP_MEDIATION_PROCESS_MODEL_4", "iv": "mindfulness", "mediator": "rumination", "dv": "anxiety"},
        "target_capability": "mediation",
        "must_do": [
            {"action_id": "MUST-MED-01", "description": "Execute non-parametric bootstrap estimation with at least 5,000 resamples.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_bootstrap_resamples_gte_5000"},
            {"action_id": "MUST-MED-02", "description": "Report 95% bias-corrected and accelerated (BCa) confidence intervals for indirect effect.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_bca_confidence_interval"},
            {"action_id": "MUST-MED-03", "description": "Report constituent paths: a (IV->Med), b (Med->DV), c (total), and c' (direct).", "category": "REPORTING_STANDARD", "verification_rule": "check_constituent_paths_reported"}
        ],
        "must_not_do": [
            {"pitfall_id": "NOT-MED-01", "description": "Rely on obsolete Baron & Kenny causal steps or Sobel test assumption of normality.", "severity": "CRITICAL", "detection_rule": "detect_baron_kenny_steps"},
            {"pitfall_id": "NOT-MED-02", "description": "Claim mediation when the 95% bootstrap confidence interval contains zero.", "severity": "CRITICAL", "detection_rule": "detect_mediation_with_zero_ci"}
        ],
        "required_evidence": [
            {"evidence_id": "EVID-MED-01", "description": "Bootstrap indirect effect table with 95% BCa CI.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"},
            {"evidence_id": "EVID-MED-02", "description": "Dedicated hypothesis triad deliverables (.docx, .md, .json).", "evidence_type": "TRIAD_DELIVERABLE", "verification_method": "TRIAD_SYNCHRONIZED"}
        ]
    },
    "MODERATION": {
        "title": "Moderated Regression Analysis with Mean-Centering and Simple Slopes",
        "rq": "Does social support buffer the detrimental impact of work stress on employee turnover intention?",
        "design": {"design_type": "MODERATION_INTERACTION_PROCESS_MODEL_1", "predictor": "work_stress", "moderator": "social_support", "outcome": "job_turnover"},
        "target_capability": "moderation",
        "must_do": [
            {"action_id": "MUST-MOD-01", "description": "Mean-center predictor and moderator variables prior to forming product term.", "category": "METHODOLOGICAL_REQUIREMENT", "verification_rule": "check_mean_centering_applied"},
            {"action_id": "MUST-MOD-02", "description": "Evaluate delta R2 and interaction F-change significance.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_delta_r2_f_change"},
            {"action_id": "MUST-MOD-03", "description": "Probe interaction with simple slopes at -1 SD, Mean, +1 SD and Johnson-Neyman technique.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_simple_slopes_and_jn"}
        ],
        "must_not_do": [
            {"pitfall_id": "NOT-MOD-01", "description": "Dichotomize continuous moderators into artificial median splits.", "severity": "CRITICAL", "detection_rule": "detect_median_split_dichotomization"},
            {"pitfall_id": "NOT-MOD-02", "description": "Interpret main effects without conditioning in the presence of significant interaction.", "severity": "MAJOR", "detection_rule": "detect_unconditioned_main_effects"}
        ],
        "required_evidence": [
            {"evidence_id": "EVID-MOD-01", "description": "Hierarchical moderation model comparison table with delta R2.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"},
            {"evidence_id": "EVID-MOD-02", "description": "Simple slopes conditional effects table.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"}
        ]
    },
    "LONGITUDINAL": {
        "title": "Three-Wave Longitudinal Autoregressive and Cross-Lagged Panel Modeling",
        "rq": "Do cross-lagged reciprocal effects exist between psychological symptoms across three waves after controlling for autoregressive stabilities?",
        "design": {"design_type": "LONGITUDINAL_CROSS_LAGGED_PANEL", "waves": 3, "constructs": ["predictor", "mediator", "outcome"]},
        "target_capability": "longitudinal-moderated-mediation",
        "must_do": [
            {"action_id": "MUST-LONG-01", "description": "Model autoregressive stability paths (T1->T2, T2->T3) for all constructs.", "category": "METHODOLOGICAL_REQUIREMENT", "verification_rule": "check_autoregressive_controls"},
            {"action_id": "MUST-LONG-02", "description": "Estimate cross-lagged structural paths controlling for prior levels.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_cross_lagged_paths"},
            {"action_id": "MUST-LONG-03", "description": "Test longitudinal measurement invariance across measurement waves.", "category": "ASSUMPTION_CHECK", "verification_rule": "check_longitudinal_invariance"}
        ],
        "must_not_do": [
            {"pitfall_id": "NOT-LONG-01", "description": "Omit autoregressive baseline paths leading to inflated cross-lagged estimates.", "severity": "CRITICAL", "detection_rule": "detect_omitted_autoregressive_paths"},
            {"pitfall_id": "NOT-LONG-02", "description": "Conflate cross-sectional mediation with true longitudinal mediation.", "severity": "CRITICAL", "detection_rule": "detect_cross_sectional_conflation"}
        ],
        "required_evidence": [
            {"evidence_id": "EVID-LONG-01", "description": "Cross-lagged structural path parameters table.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"},
            {"evidence_id": "EVID-LONG-02", "description": "Longitudinal measurement invariance comparison table.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"}
        ]
    },
    "RCT": {
        "title": "Randomized Controlled Trial Efficacy Evaluation with CONSORT Accounting and Intent-to-Treat",
        "rq": "Does the active psychological intervention demonstrate superior efficacy over control on depression symptoms in an RCT design?",
        "design": {"design_type": "PRE_POST_RCT", "arms": ["Intervention", "Control"], "measurement": ["pre_depression", "post_depression"]},
        "target_capability": "statistical-data-analyst",
        "must_do": [
            {"action_id": "MUST-RCT-01", "description": "Verify baseline equivalence across experimental arms at pre-test.", "category": "ASSUMPTION_CHECK", "verification_rule": "check_baseline_equivalence"},
            {"action_id": "MUST-RCT-02", "description": "Evaluate Group x Time interaction effect with partial eta2.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_group_by_time_interaction"},
            {"action_id": "MUST-RCT-03", "description": "Report standardized between-group Cohen's d with 95% CI and CONSORT flow.", "category": "REPORTING_STANDARD", "verification_rule": "check_cohens_d_ci_and_consort"}
        ],
        "must_not_do": [
            {"pitfall_id": "NOT-RCT-01", "description": "Compare independent within-group pre-post tests and claim efficacy (Difference in Significance Fallacy).", "severity": "CRITICAL", "detection_rule": "detect_difference_in_significance_fallacy"},
            {"pitfall_id": "NOT-RCT-02", "description": "Conceal participant attrition without Intent-to-Treat (ITT) or sensitivity reporting.", "severity": "CRITICAL", "detection_rule": "detect_undisclosed_attrition"}
        ],
        "required_evidence": [
            {"evidence_id": "EVID-RCT-01", "description": "Baseline equivalence and interaction ANOVA table.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"},
            {"evidence_id": "EVID-RCT-02", "description": "CONSORT sample flow metrics.", "evidence_type": "DIAGNOSTIC_METRIC", "verification_method": "EXACT_MATCH", "metric_key": "consort_analyzed_n"}
        ]
    },
    "ANCOVA": {
        "title": "One-Way ANCOVA with Homogeneity of Slopes Assumption and Adjusted Marginal Means",
        "rq": "Does the treatment effect on post-intervention wellbeing remain statistically significant after adjusting for pre-test baseline scores?",
        "design": {"design_type": "ANCOVA_COVARIATE_PRE_POST", "factors": ["condition"], "covariates": ["pre_test"], "dv": "post_test"},
        "target_capability": "statistical-data-analyst",
        "must_do": [
            {"action_id": "MUST-ANC-01", "description": "Test mandatory assumption of homogeneity of regression slopes (condition x pre_test, p > .05).", "category": "ASSUMPTION_CHECK", "verification_rule": "check_slopes_homogeneity_tested"},
            {"action_id": "MUST-ANC-02", "description": "Report covariate-adjusted marginal means (Madj) and SE alongside raw unadjusted means.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_adjusted_means_reported"},
            {"action_id": "MUST-ANC-03", "description": "Report exact F, df, p-value, and partial eta-squared effect size.", "category": "REPORTING_STANDARD", "verification_rule": "check_ancova_f_df_p_eta"}
        ],
        "must_not_do": [
            {"pitfall_id": "NOT-ANC-01", "description": "Run standard ANCOVA when homogeneity of slopes is violated without using moderation/Johnson-Neyman.", "severity": "CRITICAL", "detection_rule": "detect_ignored_slope_violation"},
            {"pitfall_id": "NOT-ANC-02", "description": "Report only raw unadjusted group means instead of covariate-adjusted marginal means.", "severity": "MAJOR", "detection_rule": "detect_missing_adjusted_means"}
        ],
        "required_evidence": [
            {"evidence_id": "EVID-ANC-01", "description": "Homogeneity of regression slopes test table.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"},
            {"evidence_id": "EVID-ANC-02", "description": "ANCOVA summary table with adjusted means and partial eta2.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"}
        ]
    },
    "RM_ANOVA": {
        "title": "Repeated Measures ANOVA with Mauchly's Sphericity and Epsilon Corrections",
        "rq": "Does cognitive performance change significantly across four repeated time points, and does sphericity hold?",
        "design": {"design_type": "ONE_WAY_REPEATED_MEASURES", "levels": 4, "time_points": ["Time_1", "Time_2", "Time_3", "Time_4"]},
        "target_capability": "statistical-data-analyst",
        "must_do": [
            {"action_id": "MUST-RMA-01", "description": "Test Mauchly's test of sphericity (W, chi2, df, p).", "category": "ASSUMPTION_CHECK", "verification_rule": "check_mauchlys_sphericity_tested"},
            {"action_id": "MUST-RMA-02", "description": "Apply Greenhouse-Geisser or Huynh-Feldt epsilon correction when sphericity is violated (p < .05).", "category": "STATISTICAL_RIGOR", "verification_rule": "check_epsilon_correction_applied"},
            {"action_id": "MUST-RMA-03", "description": "Report pairwise time contrasts with Bonferroni alpha adjustment.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_bonferroni_posthoc"}
        ],
        "must_not_do": [
            {"pitfall_id": "NOT-RMA-01", "description": "Report uncorrected sphericity-assumed F and df when Mauchly's test is violated.", "severity": "CRITICAL", "detection_rule": "detect_uncorrected_sphericity_violation"},
            {"pitfall_id": "NOT-RMA-02", "description": "Treat repeated within-subjects observations as independent between-subjects data.", "severity": "CRITICAL", "detection_rule": "detect_independence_assumption_error"}
        ],
        "required_evidence": [
            {"evidence_id": "EVID-RMA-01", "description": "Mauchly's sphericity and epsilon statistics table.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"},
            {"evidence_id": "EVID-RMA-02", "description": "Repeated measures ANOVA table with corrected df.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"}
        ]
    },
    "MIXED_MODELS": {
        "title": "Linear Mixed-Effects Modeling for Hierarchically Nested Longitudinal Data",
        "rq": "How do patient trajectories evolve over time while accounting for subject-level clustering and random slopes?",
        "design": {"design_type": "LINEAR_MIXED_EFFECTS", "nesting": "time_point nested within patient_id", "clusters": 50},
        "target_capability": "statistical-data-analyst",
        "must_do": [
            {"action_id": "MUST-MIX-01", "description": "Calculate Intraclass Correlation Coefficient (ICC) from null unconditional model.", "category": "ASSUMPTION_CHECK", "verification_rule": "check_null_model_icc"},
            {"action_id": "MUST-MIX-02", "description": "Compare Null vs Random Intercept vs Random Slope models via Likelihood Ratio Test (-2LL diff) and AIC/BIC.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_model_progression_lrt"},
            {"action_id": "MUST-MIX-03", "description": "Report fixed effects estimates with SE, t, df (Satterthwaite/Kenward-Roger), and random variance components.", "category": "REPORTING_STANDARD", "verification_rule": "check_fixed_and_random_parameters"}
        ],
        "must_not_do": [
            {"pitfall_id": "NOT-MIX-01", "description": "Default to standard OLS regression ignoring clustering and violating error independence.", "severity": "CRITICAL", "detection_rule": "detect_ignored_nesting_ols"},
            {"pitfall_id": "NOT-MIX-02", "description": "Compare models with different fixed effects using REML instead of ML.", "severity": "MAJOR", "detection_rule": "detect_reml_fixed_comparison"}
        ],
        "required_evidence": [
            {"evidence_id": "EVID-MIX-01", "description": "Model comparison table (Null vs Random Intercept vs Random Slope) with AIC/BIC.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"},
            {"evidence_id": "EVID-MIX-02", "description": "Fixed and random effects parameter estimates table.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"}
        ]
    },
    "NETWORK_ANALYSIS": {
        "title": "Psychometric Symptom Network Estimation via EBICglasso and Centrality Stability",
        "rq": "What is the structural network architecture of PTSD symptoms, and which nodes possess high bridge centrality?",
        "design": {"design_type": "REGULARIZED_PSYCHOMETRIC_NETWORK", "nodes": 7, "estimator": "EBICglasso"},
        "target_capability": "bibliometric-network-analyst",
        "must_do": [
            {"action_id": "MUST-NET-01", "description": "Estimate regularized partial correlation network using EBICglasso.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_ebicglasso_used"},
            {"action_id": "MUST-NET-02", "description": "Compute node centrality indices: Strength / Expected Influence, Betweenness, Closeness.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_centrality_indices"},
            {"action_id": "MUST-NET-03", "description": "Perform bootstrap stability check of centrality indices (CS-coefficient >= .25).", "category": "ASSUMPTION_CHECK", "verification_rule": "check_cs_coefficient_stability"}
        ],
        "must_not_do": [
            {"pitfall_id": "NOT-NET-01", "description": "Estimate raw unregularized Pearson correlation network with dense spurious edges.", "severity": "CRITICAL", "detection_rule": "detect_unregularized_dense_network"},
            {"pitfall_id": "NOT-NET-02", "description": "Interpret Betweenness and Closeness without confirming CS-stability >= .25.", "severity": "MAJOR", "detection_rule": "detect_unstable_centrality_interpretation"}
        ],
        "required_evidence": [
            {"evidence_id": "EVID-NET-01", "description": "Node centrality metrics summary table.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"},
            {"evidence_id": "EVID-NET-02", "description": "Bootstrap correlation stability CS-coefficient report.", "evidence_type": "DIAGNOSTIC_METRIC", "verification_method": "VALUE_IN_RANGE", "metric_key": "cs_coefficient"}
        ]
    },
    "POWER_ANALYSIS": {
        "title": "A Priori Statistical Power Analysis and Enrolled Sample Sizing via G*Power",
        "rq": "What minimum sample size is required to achieve statistical power of 1 - beta = .80 at alpha = .05 for an independent samples t-test with attrition adjustment?",
        "design": {"design_type": "A_PRIORI_POWER_PLANNING", "test_family": "t_test_independent", "effect_size_d": 0.50, "alpha": 0.05, "power": 0.80},
        "target_capability": "gpower-sample-size-calculator",
        "must_do": [
            {"action_id": "MUST-POW-01", "description": "State statistical test family, exact test, effect size justification, alpha, and power target.", "category": "METHODOLOGICAL_REQUIREMENT", "verification_rule": "check_power_parameters_specified"},
            {"action_id": "MUST-POW-02", "description": "Calculate exact required sample size (N = 128 total, 64 per group) for d = 0.50.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_required_sample_n"},
            {"action_id": "MUST-POW-03", "description": "Account for expected 15% attrition to compute required enrolled sample size (N_enrolled = 152).", "category": "METHODOLOGICAL_REQUIREMENT", "verification_rule": "check_attrition_sample_inflation"}
        ],
        "must_not_do": [
            {"pitfall_id": "NOT-POW-01", "description": "Execute post-hoc power analysis based on observed sample p-value (Observed Power Fallacy).", "severity": "CRITICAL", "detection_rule": "detect_observed_power_fallacy"},
            {"pitfall_id": "NOT-POW-02", "description": "Arbitrarily assume a huge effect size (d = 0.80) to rationalize an underpowered convenience sample.", "severity": "MAJOR", "detection_rule": "detect_unjustified_huge_effect_size"}
        ],
        "required_evidence": [
            {"evidence_id": "EVID-POW-01", "description": "Power analysis parameter specifications table.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"},
            {"evidence_id": "EVID-POW-02", "description": "Required enrolled sample size calculation.", "evidence_type": "NUMERICAL_STATISTIC", "verification_method": "EXACT_MATCH", "metric_key": "enrolled_sample_size"}
        ]
    },
    "RESULTS_WRITING": {
        "title": "APA 7th Edition Empirical Results Drafting with Persian Typography Standards",
        "rq": "Are ANCOVA empirical findings drafted following Saber's 5-part epistemic structure, Persian leading zeros, and zero ghost citations?",
        "design": {"design_type": "CHAPTER_4_EMPIRICAL_REPORTING", "test": "ANCOVA", "f": 14.82, "p": 0.0002, "eta_p2": 0.161},
        "target_capability": "chapter-4-writing",
        "must_do": [
            {"action_id": "MUST-RES-01", "description": "Adhere to Saber's 5-part epistemic paragraph structure (Hypothesis -> Test -> Stats -> Interpretation -> Table).", "category": "REPORTING_STANDARD", "verification_rule": "check_5_part_epistemic_structure"},
            {"action_id": "MUST-RES-02", "description": "Preserve Persian leading zeros (۰.۰۰۱, ۰.۰۵, ۰.۱۶) and report p < ۰.۰۰۱ instead of p = .000.", "category": "REPORTING_STANDARD", "verification_rule": "check_persian_leading_zero"},
            {"action_id": "MUST-RES-03", "description": "Generate synchronized triad of artifacts on disk (.docx, .md, .json) per Directive 3.", "category": "PROCEDURAL_COMPLIANCE", "verification_rule": "check_triad_artifacts_produced"}
        ],
        "must_not_do": [
            {"pitfall_id": "NOT-RES-01", "description": "Report p = .000 or omit leading zeros in Persian (.۰۰۱).", "severity": "CRITICAL", "detection_rule": "detect_p_equals_zero_or_missing_persian_zero"},
            {"pitfall_id": "NOT-RES-02", "description": "Include external literature citations in Chapter 4 empirical results narrative.", "severity": "CRITICAL", "detection_rule": "detect_citations_in_results"},
            {"pitfall_id": "NOT-RES-03", "description": "Use robotic AI cliches like 'شایان ذکر است که'.", "severity": "MAJOR", "detection_rule": "detect_ai_cliches"}
        ],
        "required_evidence": [
            {"evidence_id": "EVID-RES-01", "description": "Synchronized triad artifacts on disk (.docx, .md, .json).", "evidence_type": "TRIAD_DELIVERABLE", "verification_method": "TRIAD_SYNCHRONIZED"},
            {"evidence_id": "EVID-RES-02", "description": "APA 7 3-line table with decoupled LTR numbers.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"}
        ]
    },
    "DISCUSSION_WRITING": {
        "title": "Scholarly Chapter 5 Discussion Synthesis with Theoretical Mechanisms and Authentic Limitations",
        "rq": "Does the discussion synthesize confirmed and non-significant findings with psychological mechanisms, literature concordance, and authentic limitations?",
        "design": {"design_type": "CHAPTER_5_DISCUSSION_SYNTHESIS", "findings": ["H1_Confirmed_Mediation", "H2_Not_Confirmed_Direct"]},
        "target_capability": "persian-discussion-builder",
        "must_do": [
            {"action_id": "MUST-DISC-01", "description": "Recap findings conceptually without redundant repetition of raw F, t, and p numbers.", "category": "REPORTING_STANDARD", "verification_rule": "check_conceptual_recap_without_raw_stats"},
            {"action_id": "MUST-DISC-02", "description": "Articulate theoretical mechanisms (Attentional Control Theory) explaining why findings emerged.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_theoretical_mechanisms_articulated"},
            {"action_id": "MUST-DISC-03", "description": "Situate in recent literature (2021-2026 window) citing both concordant and discordant studies.", "category": "METHODOLOGICAL_REQUIREMENT", "verification_rule": "check_literature_concordance_discordance"},
            {"action_id": "MUST-DISC-04", "description": "Candidly discuss non-significant findings without defensive rationalization, and articulate authentic limitations.", "category": "STATISTICAL_RIGOR", "verification_rule": "check_candid_non_significant_discussion"}
        ],
        "must_not_do": [
            {"pitfall_id": "NOT-DISC-01", "description": "Repeat raw statistical test statistics (F = 14.82, p = .0002) in Chapter 5 prose.", "severity": "MAJOR", "detection_rule": "detect_raw_stats_in_discussion"},
            {"pitfall_id": "NOT-DISC-02", "description": "Invent ghost citations or cite sources outside the reference library.", "severity": "CRITICAL", "detection_rule": "detect_ghost_citations"},
            {"pitfall_id": "NOT-DISC-03", "description": "Sugarcoat non-significant findings by claiming a 'trend towards significance'.", "severity": "CRITICAL", "detection_rule": "detect_sugarcoated_non_significant"}
        ],
        "required_evidence": [
            {"evidence_id": "EVID-DISC-01", "description": "Discussion chapter triad (.docx, .md, .json).", "evidence_type": "TRIAD_DELIVERABLE", "verification_method": "TRIAD_SYNCHRONIZED"},
            {"evidence_id": "EVID-DISC-02", "description": "Literature concordance/divergence comparison matrix.", "evidence_type": "REPORTING_TABLE", "verification_method": "FILE_EXISTS"}
        ]
    }
}
