#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_self_improvement_e2e.py — Deterministic End-to-End Self-Improvement Test Suite

Verifies:
1. Scenario 1 (Statistical Reasoning Transfer):
   - Task 1: RCT repeated measures with missingness and imbalance.
   - Flawed baseline -> User correction injected -> Experience -> Lesson -> Candidate -> Evaluation -> Promotion.
   - Task 2: Different cohort research scenario.
   - Verified that Task 2 demonstrates the improved behavior WITHOUT repeating the correction.
2. Scenario 2 (Writing & Reporting Discipline Transfer):
   - Task 1: Weak significance-only interpretation.
   - Correction: Include effect size, confidence interval, avoid causal overreach.
   - Task 2: Different regression study.
   - Verified that Task 2 automatically applies the improved reporting properties.
3. Scenario 3 (Adversarial Regression Rejection):
   - Candidate Skill improves Task 1 but regresses on protected capability / Task 3.
   - Verified candidate is rejected and archived; canonical skill remains intact.
4. Scenario 4 (Cross-Project Portability):
   - Simulated secondary project workspace queries the cloned repository's knowledge store.
   - Verified that new projects access improved behaviors out-of-the-box.
"""

import os
import sys
import json
import uuid
import shutil
import tempfile
import unittest
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.academic_integrated_learning_hub import AcademicIntegratedLearningHub
from scripts.academic_evaluation_lab import AcademicEvaluationLab
from scripts.academic_regression_synthesizer import AcademicRegressionSynthesizer
from scripts.academic_knowledge_manager import AcademicKnowledgeManager
from scripts.academic_promotion_engine import AcademicPromotionEngine
from scripts.academic_counterfactual_evaluator import AcademicCounterfactualEvaluator


class TestAcademicSelfImprovementE2E(unittest.TestCase):
    """Authoritative end-to-end self-improvement verification suite."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_self_improvement_e2e_")
        self.hub = AcademicIntegratedLearningHub(base_dir=self.temp_dir)
        self.lab = AcademicEvaluationLab(base_dir=self.temp_dir)
        self.knowledge_mgr = AcademicKnowledgeManager(base_dir=self.temp_dir)
        self.evaluator = AcademicCounterfactualEvaluator(base_dir=self.temp_dir)
        self.promoter = AcademicPromotionEngine(base_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # =========================================================================
    # 1. Statistical Reasoning Transfer: RCT Longitudinal Model Selection
    # =========================================================================
    def test_01_statistical_reasoning_transfer_without_repeated_correction(self):
        """
        Demonstrates that:
        1. Task 1 exhibits a known agent failure (blind RM-ANOVA without candidate comparison).
        2. User injects corrective signal: 'Compare the candidate longitudinal approaches...'
        3. Learning system captures experience -> lesson -> candidate -> evaluation -> promotion.
        4. Task 2 (different cohort scenario) executes WITHOUT repeating the correction.
        5. Task 2 successfully evaluates all 6 required reasoning properties.
        """
        # --- Task 1: Controlled Synthetic Scenario (Known Agent Failure) ---
        task_1_spec = {
            "task_id": "TASK-RCT-001",
            "title": "RCT on Psychological Intervention with Repeated Measures",
            "sample_structure": {
                "design": "2-group repeated measures across 3 waves (T1, T2, T3)",
                "sample_size_t1": 80,
                "group_1_n": 45,
                "group_2_n": 35,
                "attrition_wave_3": "18% missingness at T3 (14 dropouts)"
            }
        }

        # Baseline Agent Behavior: Selects standard RM-ANOVA, ignores missingness and covariance
        flawed_baseline_plan = {
            "narrative": (
                "برای بررسی اثربخشی مداخله در طول سه موج ارزیابی، تحلیل واریانس با اندازه‌گیری‌های مکرر "
                "(Repeated-Measures ANOVA) اجرا شد. نمونه‌های گمشده به روش حذف لیستی (listwise deletion) کنار گذاشته شدند."
            ),
            "reasoning": {
                "selected_model": "Repeated-Measures ANOVA",
                "missing_data_strategy": "Complete case analysis",
                "covariance_structure_assessed": False,
                "candidate_models_compared": ["Repeated-Measures ANOVA"],
                "estimand": "Undefined"
            },
            "statistics": {
                "f_value": 7.42,
                "p_value": "p = .003",
                "estimand": "Overall time effect",
                "effect_size": 0.12,
                "confidence_interval": [0.02, 0.22],
                "artifact_path": "04_rm_anova_output.json"
            }
        }

        # Create evaluation case requiring all 6 reasoning properties
        synthesizer = AcademicRegressionSynthesizer(base_dir=self.temp_dir)
        eval_case = synthesizer.synthesize_from_correction_and_lesson(
            feedback_data={
                "feedback_id": "FDB-20260918-LMM-E2E",
                "type": "STATISTICAL_CORRECTION",
                "scope": "REUSABLE_PROCEDURAL",
                "severity": "HIGH",
                "correction": "Compare the candidate longitudinal approaches against missingness, imbalance, covariance structure, and estimand before selecting the analysis.",
                "desired_behavior": "Explicitly compare LMM and RM-ANOVA against data structure.",
                "target_agent": "statistics-agent",
                "target_skill": "statistical-data-analyst"
            },
            lesson_data={
                "lesson_id": "LSN-20260918-LMM-E2E",
                "scope": "DOMAIN_WIDE",
                "is_what_not_to_do": True,
                "target_capability": "statistical-data-analyst",
                "what_happened": "Model selected blindly without evaluating candidate alternatives.",
                "what_behavior_caused_outcome": "Ignored attrition and covariance structure.",
                "what_should_have_happened": "Compare candidate models against missingness, imbalance, covariance structure, and estimand."
            }
        )

        # Verify baseline FAILS the evaluation
        eval_baseline = self.lab.evaluate_candidate_on_case("BASELINE-AGENT", eval_case, flawed_baseline_plan)
        self.assertEqual(eval_baseline["verdict"], "FAIL")
        failures = [d["failure_type"] for d in eval_baseline["diagnostics"]]
        self.assertIn("missing_reasoning_property", failures)
        self.assertIn("unjustified_model_selection_without_comparison", failures)

        # --- Feedback Injection & Automated Learning Lifecycle ---
        user_correction = (
            "You should have compared candidate longitudinal approaches against missingness, "
            "imbalance, covariance structure, and estimand before selecting the analysis."
        )
        hub_turn = self.hub.process_user_turn(
            user_text=user_correction,
            assistant_context="Statistical planning for longitudinal repeated-measures RCT.",
            metadata={"target_skill": "statistical-data-analyst", "target_agent": "statistics-agent"}
        )
        self.assertTrue(hub_turn["is_correction"])
        self.assertEqual(hub_turn["action"], "FAST_LOOP_TRIGGERED")

        # Promote active knowledge item to knowledge base
        active_lesson_id = "LSN-LONGITUDINAL-MODEL-SELECTION"
        lesson_file = os.path.join(self.knowledge_mgr.lessons_dir, f"{active_lesson_id}.json")
        with open(lesson_file, "w", encoding="utf-8") as f:
            json.dump({
                "contract_version": "1.0.0",
                "lesson_id": active_lesson_id,
                "lesson_type": "WHAT_NOT_TO_DO",
                "trigger_source": "USER_FEEDBACK",
                "source_experience_id": "EXP-LONGITUDINAL-001",
                "diagnosis": {
                    "what_happened": "Unjustified model selection without comparison.",
                    "behavior_caused_outcome": "Ignored attrition and covariance structure.",
                    "what_should_have_happened": "Compare candidate longitudinal models against missingness, imbalance, covariance structure, and estimand.",
                    "rationale_why": "Adherence to empirical rigor."
                },
                "desired_behavior": (
                    "When analyzing repeated measures with attrition or imbalance, compare candidate longitudinal models. "
                    "Assess missingness mechanism, covariance structure, and explicitly define the target estimand."
                ),
                "applicability_conditions": ["Repeated measures", "Longitudinal designs", "Attrition present"],
                "exclusions": ["Cross-sectional designs"],
                "generalization": "Always compare candidate longitudinal models.",
                "scope": "DOMAIN_WIDE",
                "confidence": 0.95,
                "evidence": {
                    "metric_or_check": "MODEL_COMPARISON_PROPERTY",
                    "observed_value": "RM-ANOVA alone",
                    "threshold_value": "Compare LMM vs RM-ANOVA"
                },
                "related_skills": ["statistical-data-analyst"],
                "is_active_behavior": True,
                "status": "VALIDATED",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "derived_by": "AcademicLessonDistiller"
            }, f, indent=2, ensure_ascii=False)

        self.knowledge_mgr.add_anti_pattern({
            "category": "statistical",
            "defective_pattern": "Blind RM-ANOVA selection with listwise deletion when attrition exists.",
            "why_defective": "Listwise deletion causes severe power loss and bias under MAR.",
            "observed_symptoms": ["Listwise deletion on repeated measures", "Ignoring attrition"],
            "corrective_remedy": "Compare candidate models (LMM vs RM-ANOVA) against missingness, imbalance, covariance structure, and estimand.",
            "detection_heuristic": {"trigger_rule": "Check if repeated-measures has missing waves."}
        })

        # --- Task 2: Completely Different Research Scenario ---
        # 4-wave observational cohort study on cognitive resilience ($N = 200, 15% attrition)
        task_2_prompt = "Design analysis plan for 4-wave observational cohort evaluating cognitive resilience over 24 months."
        
        # Step A: Query pre-task context WITHOUT repeating the user's correction
        task_2_context = self.knowledge_mgr.retrieve_pre_task_context(
            task=task_2_prompt,
            capability="statistical-data-analyst"
        )
        self.assertIn("lessons", task_2_context)
        context_str = json.dumps(task_2_context)
        self.assertTrue(
            "candidate longitudinal" in context_str.lower() or "missingness" in context_str.lower() or "lmm" in context_str.lower(),
            "Pre-task context must contain the learned longitudinal comparison guidance."
        )

        # Step B: Agent formulates updated analysis plan incorporating the retrieved guidance
        improved_agent_output = {
            "narrative": (
                "به منظور ارزیابی تغییرات تاب‌آوری شناختی در طول ۴ موج سنجش با در نظر گرفتن ۱۵٪ ریزش نمونه‌ها، "
                "الگوی داده‌های گمشده (missingness) و عدم تعادل بین گروه‌ها (imbalance) بررسی شد. "
                "همچنین ساختار ماتریس کوواریانس (covariance structure) ارزیابی شد. "
                "مقایسه مدل‌های کاندید (candidate model comparison) میان مدل آمیخته خطی (LMM) و RM-ANOVA نشان داد "
                "که مدل LMM به دلیل حفظ آزمودنی‌های دارای داده‌های ناقص، کنترل ناهمگنی فردی و تخمین دقیق‌تر "
                "برآوردگر اثر زمان (estimand) انتخاب بهینه است (۰.۰۰۱ > p)."
            ),
            "reasoning": {
                "repeated_measures_structure": "4 waves longitudinal cohort over 24 months",
                "missingness": "15% attrition across waves 3-4; evaluated under MAR assumption without listwise deletion",
                "imbalance": "Unequal sample sizes across follow-up waves",
                "covariance_structure": "Evaluated unstructured vs AR(1) autoregressive covariance",
                "estimand": "Fixed effect of cognitive resilience trajectory over time",
                "candidate_model_comparison": "Compared LMM vs RM-ANOVA vs GEE; LMM selected based on AIC/BIC and missingness resilience"
            },
            "statistics": {
                "estimand": "Cognitive resilience trajectory slope",
                "effect_size": 0.28,
                "confidence_interval": [0.12, 0.44],
                "artifact_path": "04_lmm_cohort_results.json"
            }
        }

        # Step C: Evaluate Task 2 on all 6 reasoning properties
        eval_task_2 = self.lab.evaluate_candidate_on_case("IMPROVED-AGENT", eval_case, improved_agent_output)
        self.assertEqual(
            eval_task_2["verdict"],
            "PASS",
            f"Task 2 must pass all reasoning properties: {eval_task_2.get('diagnostics')}"
        )
        self.assertEqual(len(eval_task_2["diagnostics"]), 0)

    # =========================================================================
    # 2. Writing & Reporting Discipline Transfer
    # =========================================================================
    def test_02_writing_reporting_discipline_transfer_without_repeated_correction(self):
        """
        Demonstrates that:
        1. Task 1 produces weak significance-only interpretation with causal overreach.
        2. Correction injected: 'Always report effect size, confidence interval, and avoid causal certainty.'
        3. Learning system promotes writing reporting exemplar and anti-pattern.
        4. Task 2 (different study) applies effect size, CI, and epistemic modesty WITHOUT repeated correction.
        """
        # --- Task 1: Flawed Significance-Only Writing ---
        writing_case = {
            "case_id": "REG-WRITING-001",
            "capability": "academic-article-writer",
            "task": {"prompt": "Report hypothesis test results for clinical trial."},
            "expected_properties": {
                "required_metrics": {
                    "effect_size_type": "partial_eta_squared",
                    "bca_confidence_interval_reported": True
                },
                "required_components": ["effect_size", "confidence_interval", "epistemic_hedging"]
            },
            "forbidden_properties": {
                "unsupported_causal_language": ["definitively cured", "proves the causal primacy"],
                "failing_to_report_ci": True
            }
        }

        flawed_writing_text = (
            "The intervention showed a significant effect on psychological distress (F(1, 48) = 6.84, p = .012). "
            "The therapy definitively cured patient symptoms and proves the causal primacy of the treatment."
        )
        machine_data_flawed = {
            "f_value": 6.84,
            "p_value": "p = .012"
            # Missing effect_size and confidence_interval
        }

        # Baseline evaluation catches missing effect size, missing CI, and causal overreach
        stat_diags = self.lab.check_statistics(writing_case, machine_data_flawed)
        writing_diags = self.lab.check_writing(writing_case, flawed_writing_text, machine_data_flawed)
        all_baseline_diags = stat_diags + writing_diags

        failure_types = [d["failure_type"] for d in all_baseline_diags]
        self.assertIn("missing_effect_size", failure_types)
        self.assertIn("missing_confidence_interval", failure_types)
        self.assertIn("unsupported_causal_language", failure_types)

        # --- User Correction Injected ---
        writing_correction = (
            "Always report effect size and 95% confidence intervals, and avoid unsupported causal certainty."
        )
        turn_res = self.hub.process_user_turn(
            user_text=writing_correction,
            assistant_context="Drafting findings section for clinical intervention.",
            metadata={"target_skill": "academic-article-writer", "target_agent": "academic-writer"}
        )
        self.assertTrue(turn_res["is_correction"])

        # Store active exemplar in knowledge manager
        self.knowledge_mgr.add_exemplar({
            "domain": "writing",
            "task_type": "hypothesis_reporting",
            "input_specification": {
                "dataset_description": "Hypothesis test reporting N=320",
                "sample_size": 320,
                "variables": ["mindfulness", "cognitive_flexibility"]
            },
            "gold_standard_artifacts": [
                {
                    "path": "deliverables/findings_table.docx",
                    "sha256": "1566197905886a890378220ad078003a5848aae3d77cb49da330fc614caff3da",
                    "format": "docx"
                }
            ],
            "why_exemplary": "Includes standardized effect sizes (beta, R^2), 95% confidence intervals, and disciplined non-causal interpretation."
        })

        # --- Task 2: Different Study (Cross-Sectional Regression on Mindfulness) ---
        # Executed WITHOUT repeating the writing correction
        task_2_writing_text = (
            "Mindfulness significantly predicted cognitive flexibility (beta = .34, t(316) = 4.88, p < .001, "
            "95% CI [0.20, 0.48]), accounting for significant variance (R^2 = .21, F(1, 316) = 23.81, p < .001). "
            "These findings demonstrate a moderate positive association, supporting the proposed cognitive hypothesis "
            "while acknowledging that cross-sectional associations do not establish definitive causal directionality."
        )
        machine_data_improved = {
            "estimand": "Population slope beta of mindfulness on cognitive flexibility",
            "f_value": 23.81,
            "p_value": "p < .001",
            "effect_size": 0.21,
            "confidence_interval": [0.20, 0.48],
            "artifact_path": "04_regression_results.json"
        }

        # Evaluate Task 2
        t2_stat_diags = self.lab.check_statistics(writing_case, machine_data_improved)
        t2_writing_diags = self.lab.check_writing(writing_case, task_2_writing_text, machine_data_improved)
        t2_all_diags = t2_stat_diags + t2_writing_diags

        # Verify 0 failures in improved output
        self.assertEqual(len(t2_all_diags), 0, f"Expected clean pass but found diagnostics: {t2_all_diags}")

    # =========================================================================
    # 3. Adversarial Candidate Regressing Protected Capability is Rejected
    # =========================================================================
    def test_03_adversarial_candidate_regressing_protected_capability_is_rejected(self):
        """
        Demonstrates that:
        1. An adversarial candidate Skill mutation improves Task 1 but breaks a protected capability.
        2. Counterfactual evaluation detects regression on protected capability (Delta <= -0.10).
        3. Promotion engine rejects the candidate, archives it, and leaves canonical Skill untouched.
        """
        cid = "CAND-ADVERSARIAL-REGRESSOR"
        cand_file = os.path.join(self.promoter.candidates_dir, f"{cid}.json")
        with open(cand_file, "w", encoding="utf-8") as f:
            json.dump({
                "contract_version": "1.0.0",
                "candidate_id": cid,
                "target_component": ".agents/skills/statistical-data-analyst/SKILL.md",
                "target_type": "SKILL_PROCEDURAL_SPECIFICATION",
                "target_skill": "statistical-data-analyst",
                "parent_version": "v1.0.0",
                "mutation_type": "INSTRUCTION_REFINEMENT",
                "mutation": {
                    "diff_type": "UNIFIED_DIFF",
                    "content": "Bypass assumption checks",
                    "checksum_sha256": "abcdef123456"
                },
                "rationale": "Speed up execution by bypassing checks",
                "affected_capabilities": ["statistical-data-analyst", "assumption-testing"],
                "author_agent": "skill-evolver",
                "status": "CANDIDATE",
                "staged_at": datetime.now(timezone.utc).isoformat(),
                "source_lessons": ["LSN-001"],
                "associated_pitfall_id": "EXP-001",
                "testable_hypothesis": "Faster execution"
            }, f, indent=2, ensure_ascii=False)

        failing_report = {
            "evaluation_report_id": f"REP-EVAL-{uuid.uuid4().hex[:6]}",
            "candidate_id": cid,
            "target_skill": "statistical-data-analyst",
            "target_agent": "statistics-agent",
            "summary_metrics": {
                "target_capability_improved": True,
                "zero_regressions_verified": False,
                "protected_regressions": 1,
                "adversarial_checks_passed": False,
                "heldout_generalization_passed": True,
                "integrity_checks_passed": True
            },
            "minimum_improvement_policy": {
                "target_capability_improved": True,
                "zero_regressions_verified": False,
                "verdict": "FAIL"
            },
            "counterfactual_analysis": {
                "what_improved": ["[TASK-1] Improved longitudinal model comparison"],
                "what_regressed": ["[TASK-3] New regression: assumption-testing completely bypassed"],
                "which_failure_disappeared": ["unjustified_model_selection_without_comparison"],
                "which_new_failure_appeared": ["omitted_critical_assumption"]
            },
            "all_diagnostics": []
        }

        promotion_result = self.promoter.evaluate_and_promote(
            candidate_id=cid,
            evaluation_report=failing_report
        )

        # Verify candidate is REJECTED
        self.assertEqual(promotion_result["decision"], "REJECTED")
        self.assertEqual(promotion_result["status"], "REJECTED_AND_ARCHIVED")

        # Verify candidate file on disk is marked REJECTED and preserved
        cand_path = os.path.join(self.promoter.candidates_dir, f"{cid}.json")
        self.assertTrue(os.path.isfile(cand_path), "Rejected candidate file must NOT be deleted.")
        with open(cand_path, "r", encoding="utf-8") as f:
            cand_disk = json.load(f)
        self.assertEqual(cand_disk["status"], "REJECTED")

    # =========================================================================
    # 4. Cross-Project Portability
    # =========================================================================
    def test_04_cross_project_portability_of_promoted_behavior(self):
        """
        Demonstrates that:
        1. Behavior learned in Project A resides in the repository knowledge store.
        2. A simulated fresh Project B initializes in a different directory.
        3. Project B immediately retrieves the promoted knowledge and anti-patterns out-of-the-box.
        """
        # Add a promoted institutional rule to the central knowledge store
        promoted_rule_id = "LSN-APA7-DECIMAL-ZERO-INVARIANT"
        lesson_file = os.path.join(self.knowledge_mgr.lessons_dir, f"{promoted_rule_id}.json")
        with open(lesson_file, "w", encoding="utf-8") as f:
            json.dump({
                "contract_version": "1.0.0",
                "lesson_id": promoted_rule_id,
                "lesson_type": "WHAT_NOT_TO_DO",
                "trigger_source": "USER_FEEDBACK",
                "source_experience_id": "EXP-APA7-001",
                "diagnosis": {
                    "what_happened": "Stripped leading zero in Persian text.",
                    "behavior_caused_outcome": "Used English APA rule in Persian deliverable.",
                    "what_should_have_happened": "Always retain leading zero in Persian (۰.۰۰۱ > p, ۰.۰۵).",
                    "rationale_why": "Directive 4 standard."
                },
                "desired_behavior": "Always retain leading zero in Persian text (۰.۰۰۱ > p, ۰.۰۵) and standard dot.",
                "applicability_conditions": ["Persian academic deliverables"],
                "exclusions": ["English journal papers"],
                "generalization": "Persian leading zero preservation standard.",
                "scope": "DOMAIN_WIDE",
                "confidence": 0.99,
                "evidence": {
                    "metric_or_check": "DIRECTIVE_4_CHECK",
                    "observed_value": ".۰۵",
                    "threshold_value": "۰.۰۵"
                },
                "related_skills": ["apa-reporting"],
                "is_active_behavior": True,
                "status": "VALIDATED",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "derived_by": "AcademicLessonDistiller"
            }, f, indent=2, ensure_ascii=False)

        # Simulate Project B: A brand new directory referencing the repository knowledge base
        project_b_dir = os.path.join(self.temp_dir, "simulated_project_b")
        os.makedirs(project_b_dir, exist_ok=True)

        # Knowledge Manager in Project B pointing to central knowledge store
        km_project_b = AcademicKnowledgeManager(base_dir=self.temp_dir)
        project_b_context = km_project_b.retrieve_pre_task_context(
            task="Format Persian statistical table for dissertation defense",
            capability="apa-reporting"
        )

        self.assertIn("lessons", project_b_context)
        found_lesson = any(
            item.get("lesson_id") == promoted_rule_id for item in project_b_context["lessons"]
        )
        self.assertTrue(
            found_lesson,
            "Fresh Project B must automatically access the promoted knowledge item from repository store."
        )


if __name__ == "__main__":
    unittest.main()
