#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_eval_cases.py — Generates the canonical 8-domain evaluation benchmark test corpus
adhering strictly to the 8 constitutional fields:
INPUT, EXPECTED_ANALYSIS, EXPECTED_N, EXPECTED_VARIABLES, EXPECTED_KEY_STATISTICS,
EXPECTED_TABLES, EXPECTED_INTERPRETATION_CONSTRAINTS, and EXPECTED_VALIDATION.
"""

import os
import json
import jsonschema

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVALS_DIR = os.path.join(ROOT_DIR, "evals")

# Load schema
with open(os.path.join(EVALS_DIR, "eval_schema.json"), "r", encoding="utf-8") as f:
    SCHEMA = json.load(f)


CASES = [
    # 1. Descriptive
    {
        "test_id": "EVAL-DESC-01",
        "domain": "descriptive",
        "title": "Demographics and Longitudinal Repeated Measures Descriptives in Experimental RCT",
        "version_target": "Academic Suite v1 / v2 / v3",
        "INPUT": {
            "data_path": "evals/descriptive/data/descriptive_data.xlsx",
            "format": "xlsx",
            "sample_n": 60,
            "predictors": ["group", "gender", "age", "education"],
            "dependent_variable": "anxiety"
        },
        "EXPECTED_ANALYSIS": {
            "model_type": "Univariate and Longitudinal Central Tendency & Equivalence",
            "methodology": "Means, SDs, Skewness, Kurtosis, Independent t-test, Chi-square",
            "standard_applied": "APA 7th Edition Demographics & Descriptives Standard",
            "tool_script": ".agents/skills/descriptive-statistics/scripts/compute_descriptives.py"
        },
        "EXPECTED_N": 60,
        "EXPECTED_VARIABLES": [
            "gender",
            "age",
            "education",
            "anxiety_pre",
            "anxiety_post",
            "anxiety_followup"
        ],
        "EXPECTED_KEY_STATISTICS": {
            "sample_size": {"total": 60, "experimental": 30, "control": 30},
            "age": {"mean": 35.60, "sd": 9.50, "t_stat": 2.248, "p_value": 0.028},
            "gender_chi2": {"chi2": 0.067, "df": 1, "p_value": 0.796},
            "education_chi2": {"chi2": 1.726, "df": 2, "p_value": 0.422},
            "anxiety_pre": {"mean_exp": 3.426, "mean_ctl": 3.466, "tolerance": 0.010},
            "anxiety_post": {"mean_exp": 2.301, "mean_ctl": 3.534, "tolerance": 0.010},
            "anxiety_followup": {"mean_exp": 2.351, "mean_ctl": 3.444, "tolerance": 0.010}
        },
        "EXPECTED_TABLES": [
            {"table_number": 1, "title": "مشخصات جمعیت‌شناختی آزمودنی‌ها به تفکیک گروه و آزمون‌های برابری خط پایه", "columns": 6, "format": "APA 7"},
            {"table_number": 2, "title": "شاخص‌های توصیفی نمرات اضطراب و انعطاف‌ناپذیری روان‌شناختی در مراحل سنجش به تفکیک گروه", "columns": 5, "format": "APA 7"}
        ],
        "EXPECTED_INTERPRETATION_CONSTRAINTS": {
            "language": "Persian (Farsi)",
            "paragraph_structure": "5-Part Epistemic Formula",
            "leading_zero_persian": True,
            "table_placement": "Directly below explanatory narrative",
            "zero_citations_in_results": True,
            "zero_ai_cliches": True,
            "effect_size_reporting": False
        },
        "EXPECTED_VALIDATION": {
            "data_integrity": "PASS",
            "numerical_consistency": "PASS",
            "reporting_consistency": "PASS",
            "result_consistency": "PASS",
            "statistical_assumptions": "PASS",
            "state_schema_validation": "PASS"
        }
    },

    # 2. Reliability
    {
        "test_id": "EVAL-REL-01",
        "domain": "reliability",
        "title": "Scale Internal Consistency Reliability and Omega Estimation",
        "version_target": "Academic Suite v1 / v2 / v3",
        "INPUT": {
            "data_path": "evals/reliability/data/reliability_data.xlsx",
            "format": "xlsx",
            "sample_n": 450,
            "predictors": ["item_1", "item_2", "item_3", "item_4", "item_5"],
            "dependent_variable": "scale_composite"
        },
        "EXPECTED_ANALYSIS": {
            "model_type": "Classical Test Theory Internal Consistency",
            "methodology": "Cronbach's Alpha and McDonald's Omega",
            "standard_applied": "APA 7th Psychometric Reliability Standard",
            "tool_script": ".agents/skills/reliability-analysis/scripts/compute_reliability.py"
        },
        "EXPECTED_N": 450,
        "EXPECTED_VARIABLES": [
            "cyber_aggression",
            "cyber_victimization",
            "total_score"
        ],
        "EXPECTED_KEY_STATISTICS": {
            "cronbach_alpha": {
                "factor_1_aggression": {"value": 0.876, "tolerance": 0.005, "threshold_min": 0.70},
                "factor_2_victimization": {"value": 0.880, "tolerance": 0.005, "threshold_min": 0.70},
                "total_scale": {"value": 0.912, "tolerance": 0.005, "threshold_min": 0.80}
            },
            "mcdonald_omega": {
                "factor_1_aggression": {"value": 0.881, "tolerance": 0.005, "threshold_min": 0.70},
                "factor_2_victimization": {"value": 0.885, "tolerance": 0.005, "threshold_min": 0.70},
                "total_scale": {"value": 0.918, "tolerance": 0.005, "threshold_min": 0.80}
            },
            "test_retest_icc": {
                "subsample_n": 60,
                "interval_weeks": 4,
                "icc_value": 0.878,
                "tolerance": 0.010
            }
        },
        "EXPECTED_TABLES": [
            {"table_number": 1, "title": "ضرایب پایایی آلفای کرونباخ، امگای مک‌دونالد و بازآزمایی مقیاس به تفکیک خرده‌مقیاس‌ها", "columns": 6, "format": "APA 7"}
        ],
        "EXPECTED_INTERPRETATION_CONSTRAINTS": {
            "language": "Persian (Farsi)",
            "paragraph_structure": "5-Part Epistemic Formula",
            "leading_zero_persian": True,
            "table_placement": "Directly below explanatory narrative",
            "zero_citations_in_results": True,
            "zero_ai_cliches": True,
            "effect_size_reporting": False
        },
        "EXPECTED_VALIDATION": {
            "data_integrity": "PASS",
            "numerical_consistency": "PASS",
            "reporting_consistency": "PASS",
            "result_consistency": "PASS",
            "statistical_assumptions": "PASS",
            "state_schema_validation": "PASS"
        }
    },

    # 3. Regression
    {
        "test_id": "EVAL-REG-01",
        "domain": "regression",
        "title": "Multiple Linear OLS Regression Modeling (Digital Saber 3-Table Standard)",
        "version_target": "Academic Suite v1 / v2 / v3",
        "INPUT": {
            "data_path": "evals/regression/data/regression_data.xlsx",
            "format": "xlsx",
            "sample_n": 100,
            "predictors": ["workplace_stress", "psychological_flexibility"],
            "dependent_variable": "job_burnout"
        },
        "EXPECTED_ANALYSIS": {
            "model_type": "Multiple Linear OLS Regression",
            "methodology": "Simultaneous enter method with collinearity diagnostics",
            "standard_applied": "Digital Saber 3-Table Standard",
            "tool_script": ".agents/skills/regression/scripts/run_regression.py"
        },
        "EXPECTED_N": 100,
        "EXPECTED_VARIABLES": [
            "workplace_stress",
            "psychological_flexibility",
            "job_burnout"
        ],
        "EXPECTED_KEY_STATISTICS": {
            "r_squared": {"value": 0.448, "tolerance": 0.005},
            "adj_r_squared": {"value": 0.437, "tolerance": 0.005},
            "f_statistic": {"value": 39.40, "df1": 2, "df2": 97, "tolerance": 0.10, "p_value": "p < 0.001"},
            "coefficients": {
                "workplace_stress": {"beta": 0.478, "tolerance": 0.010, "t": 6.12, "p_value": "p < 0.001", "vif_max": 2.50},
                "psychological_flexibility": {"beta": -0.342, "tolerance": 0.010, "t": -4.38, "p_value": "p < 0.001", "vif_max": 2.50}
            },
            "collinearity": {
                "tolerance_min": 0.70,
                "vif_max": 1.40
            }
        },
        "EXPECTED_TABLES": [
            {"table_number": 1, "title": "ماتریس همبستگی پیرسون و شاخص‌های توصیفی متغیرهای پژوهش", "columns": 6, "format": "APA 7"},
            {"table_number": 2, "title": "خلاصه الگو و تحلیل واریانس رگرسیون چندگانه پیش‌بینی فرسودگی شغلی", "columns": 11, "format": "APA 7"},
            {"table_number": 3, "title": "ضرایب رگرسیون و شاخص‌های هم‌خطی متغیرهای پیش‌بین فرسودگی شغلی", "columns": 8, "format": "APA 7"}
        ],
        "EXPECTED_INTERPRETATION_CONSTRAINTS": {
            "language": "Persian (Farsi)",
            "paragraph_structure": "5-Part Epistemic Formula",
            "leading_zero_persian": True,
            "table_placement": "Directly below explanatory narrative",
            "zero_citations_in_results": True,
            "zero_ai_cliches": True,
            "effect_size_reporting": True
        },
        "EXPECTED_VALIDATION": {
            "data_integrity": "PASS",
            "numerical_consistency": "PASS",
            "reporting_consistency": "PASS",
            "result_consistency": "PASS",
            "statistical_assumptions": "PASS",
            "state_schema_validation": "PASS"
        }
    },

    # 4. Mediation
    {
        "test_id": "EVAL-MED-01",
        "domain": "mediation",
        "title": "Serial Two-Mediator Bootstrap Mediation (Hayes PROCESS Model 6)",
        "version_target": "Academic Suite v1 / v2 / v3",
        "INPUT": {
            "data_path": "evals/mediation/data/mediation_data.xlsx",
            "format": "xlsx",
            "sample_n": 300,
            "predictors": ["trans_leadership"],
            "mediators": ["psych_safety", "work_engagement"],
            "dependent_variable": "innovative_behavior"
        },
        "EXPECTED_ANALYSIS": {
            "model_type": "Serial Two-Mediator Mediation Model (PROCESS Model 6)",
            "methodology": "Ordinary Least Squares path modeling with 5,000 bootstrap resamples",
            "standard_applied": "Preacher & Hayes 95% BCa Confidence Interval Standard",
            "tool_script": ".agents/skills/mediation/scripts/run_mediation.py"
        },
        "EXPECTED_N": 300,
        "EXPECTED_VARIABLES": [
            "trans_leadership",
            "psych_safety",
            "work_engagement",
            "innovative_behavior"
        ],
        "EXPECTED_KEY_STATISTICS": {
            "direct_effect_c_prime": {"beta": 0.166, "tolerance": 0.010, "t": 2.76, "p_value": 0.006},
            "total_effect_c": {"beta": 0.608, "tolerance": 0.010, "t": 13.24, "p_value": "p < 0.001"},
            "indirect_effects": {
                "indirect_1_m1": {"point_estimate": 0.188, "boot_ci_lower": 0.124, "boot_ci_upper": 0.263, "significant": True},
                "indirect_2_m2": {"point_estimate": 0.165, "boot_ci_lower": 0.108, "boot_ci_upper": 0.231, "significant": True},
                "indirect_3_serial": {"point_estimate": 0.089, "boot_ci_lower": 0.048, "boot_ci_upper": 0.142, "significant": True},
                "total_indirect": {"point_estimate": 0.442, "boot_ci_lower": 0.334, "boot_ci_upper": 0.562, "significant": True}
            },
            "mediation_type": "Partial Serial Mediation"
        },
        "EXPECTED_TABLES": [
            {"table_number": 1, "title": "ضرایب مسیر مستقیم و مدل‌های رگرسیونی الگوی میانجی‌گری سریالی", "columns": 7, "format": "APA 7"},
            {"table_number": 2, "title": "برآورد اثرات غیرمستقیم و فواصل اطمینان بوت‌استراپ (۵۰۰۰ بار نمونه‌برداری مجدد)", "columns": 6, "format": "APA 7"}
        ],
        "EXPECTED_INTERPRETATION_CONSTRAINTS": {
            "language": "Persian (Farsi)",
            "paragraph_structure": "5-Part Epistemic Formula",
            "leading_zero_persian": True,
            "table_placement": "Directly below explanatory narrative",
            "zero_citations_in_results": True,
            "zero_ai_cliches": True,
            "effect_size_reporting": True
        },
        "EXPECTED_VALIDATION": {
            "data_integrity": "PASS",
            "numerical_consistency": "PASS",
            "reporting_consistency": "PASS",
            "result_consistency": "PASS",
            "statistical_assumptions": "PASS",
            "state_schema_validation": "PASS"
        }
    },

    # 5. CFA
    {
        "test_id": "EVAL-CFA-01",
        "domain": "cfa",
        "title": "Confirmatory Factor Analysis Measurement Model Evaluation",
        "version_target": "Academic Suite v1 / v2 / v3",
        "INPUT": {
            "data_path": "evals/cfa/data/cfa_data.xlsx",
            "format": "xlsx",
            "sample_n": 450,
            "model_spec": "aggression =~ item_1 + ... + item_10; victimization =~ item_11 + ... + item_20"
        },
        "EXPECTED_ANALYSIS": {
            "model_type": "Confirmatory Factor Analysis (CFA) Measurement Model",
            "methodology": "Maximum Likelihood / Robust estimation",
            "standard_applied": "Hu & Bentler (1999) 11-Pillar Fit Indices Standard",
            "tool_script": ".agents/skills/cfa/scripts/run_cfa.py"
        },
        "EXPECTED_N": 450,
        "EXPECTED_VARIABLES": [
            "cyber_aggression_items",
            "cyber_victimization_items"
        ],
        "EXPECTED_KEY_STATISTICS": {
            "fit_indices": {
                "chi2_df": {"value": 2.298, "tolerance": 0.05, "threshold_max": 3.0},
                "cfi": {"value": 0.948, "tolerance": 0.010, "threshold_min": 0.90},
                "tli": {"value": 0.942, "tolerance": 0.010, "threshold_min": 0.90},
                "rmsea": {"value": 0.054, "ci_lower": 0.047, "ci_upper": 0.061, "threshold_max": 0.08},
                "srmr": {"value": 0.048, "tolerance": 0.005, "threshold_max": 0.08}
            },
            "factor_loadings": {
                "minimum_loading": 0.65,
                "all_significant": True,
                "z_scores_min": 12.0
            },
            "construct_validity": {
                "factor_1_ave": {"value": 0.542, "threshold_min": 0.50},
                "factor_1_cr": {"value": 0.892, "threshold_min": 0.70},
                "factor_2_ave": {"value": 0.518, "threshold_min": 0.50},
                "factor_2_cr": {"value": 0.885, "threshold_min": 0.70}
            }
        },
        "EXPECTED_TABLES": [
            {"table_number": 1, "title": "بارهای عاملی استاندارد، خطای استاندارد و اعتبار سازه الگوی اندازه‌گیری", "columns": 7, "format": "APA 7"},
            {"table_number": 2, "title": "شاخص‌های برازش الگوی تحلیل عاملی تاییدی در مقایسه با معیارهای هو و بنتلر", "columns": 5, "format": "APA 7"}
        ],
        "EXPECTED_INTERPRETATION_CONSTRAINTS": {
            "language": "Persian (Farsi)",
            "paragraph_structure": "5-Part Epistemic Formula",
            "leading_zero_persian": True,
            "table_placement": "Directly below explanatory narrative",
            "zero_citations_in_results": True,
            "zero_ai_cliches": True,
            "effect_size_reporting": True
        },
        "EXPECTED_VALIDATION": {
            "data_integrity": "PASS",
            "numerical_consistency": "PASS",
            "reporting_consistency": "PASS",
            "result_consistency": "PASS",
            "statistical_assumptions": "PASS",
            "state_schema_validation": "PASS"
        }
    },

    # 6. SEM
    {
        "test_id": "EVAL-SEM-01",
        "domain": "sem",
        "title": "Macro Latent Structural Equation Modeling (SEM)",
        "version_target": "Academic Suite v1 / v2 / v3",
        "INPUT": {
            "data_path": "evals/sem/data/sem_data.xlsx",
            "format": "xlsx",
            "sample_n": 250,
            "model_spec": "projects/study_vertical_slice_sem/02_specs/sem_model_spec.txt"
        },
        "EXPECTED_ANALYSIS": {
            "model_type": "Full Latent Structural Equation Modeling",
            "methodology": "Two-step SEM (Anderson & Gerbing) with ML estimation",
            "standard_applied": "Digital Saber 11-Pillar SEM Standard",
            "tool_script": ".agents/skills/sem/scripts/run_sem.py"
        },
        "EXPECTED_N": 250,
        "EXPECTED_VARIABLES": [
            "mindfulness",
            "self_compassion",
            "psych_wellbeing"
        ],
        "EXPECTED_KEY_STATISTICS": {
            "macro_fit": {
                "cfi": {"value": 0.957, "tolerance": 0.010, "threshold_min": 0.95},
                "tli": {"value": 0.951, "tolerance": 0.010, "threshold_min": 0.95},
                "rmsea": {"value": 0.046, "tolerance": 0.005, "threshold_max": 0.06},
                "srmr": {"value": 0.042, "tolerance": 0.005, "threshold_max": 0.08}
            },
            "structural_paths": {
                "mindfulness_to_wellbeing": {"beta": 0.385, "tolerance": 0.010, "p_value": "p < 0.001"},
                "compassion_to_wellbeing": {"beta": 0.342, "tolerance": 0.010, "p_value": "p < 0.001"}
            }
        },
        "EXPECTED_TABLES": [
            {"table_number": 1, "title": "شاخص‌های برازش کلی مدل ساختاری در مقایسه با مقادیر بحرانی استاندارد", "columns": 5, "format": "APA 7"},
            {"table_number": 2, "title": "ضرایب مسیر مستقیم و پارامترهای ساختاری مدل مفهومی پژوهش", "columns": 7, "format": "APA 7"}
        ],
        "EXPECTED_INTERPRETATION_CONSTRAINTS": {
            "language": "Persian (Farsi)",
            "paragraph_structure": "5-Part Epistemic Formula",
            "leading_zero_persian": True,
            "table_placement": "Directly below explanatory narrative",
            "zero_citations_in_results": True,
            "zero_ai_cliches": True,
            "effect_size_reporting": True
        },
        "EXPECTED_VALIDATION": {
            "data_integrity": "PASS",
            "numerical_consistency": "PASS",
            "reporting_consistency": "PASS",
            "result_consistency": "PASS",
            "statistical_assumptions": "PASS",
            "state_schema_validation": "PASS"
        }
    },

    # 7. Network
    {
        "test_id": "EVAL-NET-01",
        "domain": "network",
        "title": "Bibliometric Co-occurrence and Callon Strategic Thematic Mapping",
        "version_target": "Academic Suite v1 / v2 / v3",
        "INPUT": {
            "data_path": "evals/network/data/bibliometric_corpus.csv",
            "format": "csv",
            "sample_n": 1250,
            "predictors": ["keywords", "authors", "citations"]
        },
        "EXPECTED_ANALYSIS": {
            "model_type": "Bibliometric Keyword Co-occurrence & Callon Diagram",
            "methodology": "Equivalence index, Louvain clustering, Callon centrality-density mapping",
            "standard_applied": "Callon (1991) Strategic Diagram Standard",
            "tool_script": ".agents/skills/network-analysis/scripts/run_network_analysis.py"
        },
        "EXPECTED_N": 1250,
        "EXPECTED_VARIABLES": [
            "core_themes",
            "emerging_methods",
            "specialized_niches"
        ],
        "EXPECTED_KEY_STATISTICS": {
            "network_topology": {
                "total_nodes": {"value": 64, "tolerance": 2},
                "total_edges": {"value": 192, "tolerance": 5}
            },
            "callon_quadrants": {
                "motor_themes_q1": {"centrality": 0.88, "density": 0.82, "status": "Core Themes"},
                "basic_transversal_q4": {"centrality": 0.74, "density": 0.35, "status": "Emerging Methods"},
                "highly_developed_q2": {"centrality": 0.28, "density": 0.79, "status": "Specialized Niches"}
            }
        },
        "EXPECTED_TABLES": [
            {"table_number": 1, "title": "مختصات تراکم و مرکزیت خوشه‌های موضوعی بر پایه نمودار راهبردی کالون", "columns": 5, "format": "APA 7"}
        ],
        "EXPECTED_INTERPRETATION_CONSTRAINTS": {
            "language": "Persian (Farsi)",
            "paragraph_structure": "Epistemic Callon Quadrant Interpretation",
            "leading_zero_persian": True,
            "table_placement": "Directly below explanatory narrative",
            "zero_citations_in_results": False,
            "zero_ai_cliches": True,
            "effect_size_reporting": False
        },
        "EXPECTED_VALIDATION": {
            "data_integrity": "PASS",
            "numerical_consistency": "PASS",
            "reporting_consistency": "PASS",
            "result_consistency": "PASS",
            "statistical_assumptions": "N/A",
            "state_schema_validation": "PASS"
        }
    },

    # 8. Writing
    {
        "test_id": "EVAL-WRIT-01",
        "domain": "writing",
        "title": "Master Chapter 4 Findings Triad Narrative Synthesis",
        "version_target": "Academic Suite v1 / v2 / v3",
        "INPUT": {
            "data_path": "evals/writing/data/stats_input.json",
            "format": "json",
            "sample_n": 100,
            "predictors": ["workplace_stress", "psychological_flexibility"],
            "dependent_variable": "job_burnout"
        },
        "EXPECTED_ANALYSIS": {
            "model_type": "Scholarly Chapter 4 Findings Narrative & Triad Generation",
            "methodology": "Saber 5-Part Epistemic Paragraph Formula with Natural Cadence",
            "standard_applied": "Digital Saber Academic Writing Standard & OpenXML Typography",
            "tool_script": ".agents/skills/chapter-4-writing/scripts/scaffold_chapter4_triad.py"
        },
        "EXPECTED_N": 100,
        "EXPECTED_VARIABLES": [
            "workplace_stress",
            "psychological_flexibility",
            "job_burnout"
        ],
        "EXPECTED_KEY_STATISTICS": {
            "reported_f": "39.40",
            "reported_p": "۰.۰۰۱ > p",
            "reported_r2": "۰.۴۴۸",
            "reported_beta_stress": "۰.۴۷۸",
            "reported_beta_flex": "-۰.۳۴۲"
        },
        "EXPECTED_TABLES": [
            {"table_number": 1, "title": "ماتریس همبستگی پیرسون و شاخص‌های توصیفی متغیرهای پژوهش", "columns": 6, "format": "APA 7"},
            {"table_number": 2, "title": "خلاصه الگو و تحلیل واریانس رگرسیون چندگانه پیش‌بینی فرسودگی شغلی", "columns": 11, "format": "APA 7"},
            {"table_number": 3, "title": "ضرایب رگرسیون و شاخص‌های هم‌خطی متغیرهای پیش‌بین فرسودگی شغلی", "columns": 8, "format": "APA 7"}
        ],
        "EXPECTED_INTERPRETATION_CONSTRAINTS": {
            "language": "Persian (Farsi)",
            "paragraph_structure": "5-Part Epistemic Formula",
            "leading_zero_persian": True,
            "table_placement": "Directly below explanatory narrative",
            "zero_citations_in_results": True,
            "zero_ai_cliches": True,
            "effect_size_reporting": True
        },
        "EXPECTED_VALIDATION": {
            "data_integrity": "PASS",
            "numerical_consistency": "PASS",
            "reporting_consistency": "PASS",
            "result_consistency": "PASS",
            "statistical_assumptions": "PASS",
            "state_schema_validation": "PASS"
        }
    }
]


def main():
    print(f"Generating {len(CASES)} canonical evaluation test cases...")
    for c in CASES:
        domain = c["domain"]
        test_id = c["test_id"].lower().replace("-", "_")
        target_path = os.path.join(EVALS_DIR, domain, f"case_{domain}_01.json")
        
        # Validate against schema
        jsonschema.validate(instance=c, schema=SCHEMA)
        
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(c, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Created & Validated: {target_path}")

    # Create dummy data for network and writing if not present
    net_corpus = os.path.join(EVALS_DIR, "network", "data", "bibliometric_corpus.csv")
    if not os.path.exists(net_corpus):
        with open(net_corpus, "w", encoding="utf-8") as f:
            f.write("record_id,title,authors,year,keywords,citations\n")
            for i in range(1, 101):
                f.write(f"R{i},Study on Behavioral Modeling {i},Author {i},2023,mindfulness;stress;burnout;wellbeing,{i*3}\n")
        print(f"  ✓ Created corpus fixture: {net_corpus}")

    stats_payload = os.path.join(EVALS_DIR, "writing", "data", "stats_input.json")
    if not os.path.exists(stats_payload):
        reg_stats = {
            "model_type": "Multiple Regression",
            "sample_n": 100,
            "f_stat": 39.40,
            "df1": 2,
            "df2": 97,
            "p_value": 0.001,
            "r_squared": 0.448,
            "adj_r_squared": 0.437,
            "coefficients": [
                {"variable": "workplace_stress", "beta": 0.478, "t": 6.12, "p": 0.001},
                {"variable": "psychological_flexibility", "beta": -0.342, "t": -4.38, "p": 0.001}
            ]
        }
        with open(stats_payload, "w", encoding="utf-8") as f:
            json.dump(reg_stats, f, indent=2)
        print(f"  ✓ Created stats payload fixture: {stats_payload}")

    print("\nAll 8 evaluation test cases generated and verified successfully.")


if __name__ == "__main__":
    main()
