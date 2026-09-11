#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Digital Saber Continuous Learning & Decision Calibration Engine
(موتور یادگیری پیوسته و کالیبراسیون تصمیمات دیجیتال صابر)

Transforms Digital Saber from a static expert system into a self-calibrating
intellect that learns from Human Saber's real-world research decisions:

The 8-Stage Closed-Loop Cycle:
  1. Ingest new research case / proposal / client inquiry
  2. Retrieve closest historical precedents from CaseMemoryEngine
  3. Generate multi-path candidate decisions (Saber modern, Supervisor orthodox, Conservative alternative)
  4. Apply Saber-style reasoning & constitution guardrails
  5. Make recommendation & journal with status PENDING_HUMAN_OUTCOME
  6. Record real-world outcome & Human Saber's final decision
  7. Compare AI recommendation against Human Saber's decision (compute congruence & detect divergence)
  8. Update knowledge base:
     - On Agreement: Reinforce precedent case confidence & weights
     - On Divergence: Automatically synthesize a new calibrated case in .agents/memory/cases/
       and update decision journal with learned heuristic so the twin never diverges on this nuance again.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

MEMORY_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_DIR = os.path.abspath(os.path.join(MEMORY_DIR, ".."))
REASONING_DIR = os.path.join(AGENTS_DIR, "reasoning")

for p in [MEMORY_DIR, REASONING_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from case_memory_engine import CaseMemoryEngine
    from decision_journal_engine import DecisionJournalEngine
    from statistical_reasoner import StatisticalReasoner
    from research_methodology_reasoner import ResearchMethodologyReasoner
except ImportError as e:
    print(f"Warning: Import failure in continuous learning engine: {e}", file=sys.stderr)


class ContinuousLearningEngine:
    """Orchestrates closed-loop decision making, human feedback ingestion, and knowledge calibration."""

    def __init__(self, cases_dir: Optional[str] = None, decisions_dir: Optional[str] = None):
        self.case_memory = CaseMemoryEngine(cases_dir=cases_dir)
        self.decision_journal = DecisionJournalEngine(decisions_dir=decisions_dir)
        self.stat_reasoner = StatisticalReasoner()
        self.method_reasoner = ResearchMethodologyReasoner()

    # =========================================================================
    # STAGES 1-5: INGESTION, RETRIEVAL, CANDIDATE GENERATION, REASONING, RECOMMENDATION
    # =========================================================================
    def process_new_case(self, case_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes stages 1 to 5 of the learning cycle:
          1. Ingests case
          2. Retrieves precedents
          3. Generates 3 candidate paths
          4. Applies Saber reasoning
          5. Journals recommendation with PENDING_HUMAN_OUTCOME
        """
        title = case_spec.get("title", case_spec.get("topic", "پژوهش روان‌شناختی"))
        design = case_spec.get("design", "pre_post_control")
        variables = case_spec.get("variables", [])
        sample_size = int(case_spec.get("sample_size", 30))
        objective = case_spec.get("objective", "difference")
        has_pretest = bool(case_spec.get("has_pretest", True))
        has_mediator = bool(case_spec.get("has_mediator", False) or "میانجی" in title)
        has_moderator = bool(case_spec.get("has_moderator", False) or "تعدیل" in title)

        # Stage 2: Retrieve similar Saber cases
        query_text = f"{title} {design} {' '.join(str(v) for v in variables)}"
        precedents = self.case_memory.search_precedents(query_text, top_k=3)
        precedent_ids = [p["case"].get("case_id") for p in precedents]

        # Stage 3: Generate multi-path candidate decisions
        candidates = []

        if has_mediator:
            candidates.append({
                "path_id": "PATH_A_SABER_OPTIMAL",
                "name": "Hayes PROCESS Model 4 (Percentile Bootstrap Mediation)",
                "type": "modern_psychometric",
                "approach": "5,000-sample percentile bootstrap confidence intervals",
                "pros": "Robust against non-normal indirect effects (ab product); superior power; APA 7 compliant",
                "cons": "Requires specialized SPSS PROCESS macro or R lavaan",
                "saber_verdict": "RECOMMENDED"
            })
            candidates.append({
                "path_id": "PATH_B_ORTHODOX_SUPERVISOR",
                "name": "Baron & Kenny Causal Steps / Normal Sobel Test",
                "type": "traditional_supervisor",
                "approach": "4-step regression equations and Sobel Z-statistic",
                "pros": "Familiar to traditional faculty members",
                "cons": "Severely low power; assumes normal ab product distribution; deprecated in modern literature",
                "saber_verdict": "REJECTED_OR_DUAL_TRACK"
            })
            candidates.append({
                "path_id": "PATH_C_STRUCTURAL_EQUATION",
                "name": "Full Structural Equation Modeling (SEM with Latent Variables)",
                "type": "conservative_latent",
                "approach": "AMOS / Lisrel full measurement and structural model",
                "pros": "Controls for measurement error in constructs",
                "cons": "Requires large sample size (N ≥ 200); overparameterized for small samples",
                "saber_verdict": "VIABLE_IF_SAMPLE_SUFFICIENT"
            })

        elif has_moderator:
            candidates.append({
                "path_id": "PATH_A_SABER_OPTIMAL",
                "name": "Hayes PROCESS Model 1 (Continuous Moderation with Mean-Centering)",
                "type": "modern_psychometric",
                "approach": "Continuous regression interaction with Johnson-Neyman floodlight probing",
                "pros": "Preserves 100% of variance; avoids artificial group boundaries; high power",
                "cons": "Slightly more complex interpretation than simple ANOVA",
                "saber_verdict": "RECOMMENDED"
            })
            candidates.append({
                "path_id": "PATH_B_ORTHODOX_SUPERVISOR",
                "name": "Median Split followed by 2-Way ANOVA",
                "type": "traditional_supervisor",
                "approach": "Dichotomize moderator at median into high/low groups",
                "pros": "Simple 2x2 table familiar to older supervisors",
                "cons": "Discards 35-50% statistical power; inflates Type I errors; deprecated by MacCallum et al. (2002)",
                "saber_verdict": "STRICTLY_REJECTED"
            })
            candidates.append({
                "path_id": "PATH_C_SUBGROUP_REGRESSION",
                "name": "Subgroup Linear Regression",
                "type": "alternative",
                "approach": "Run regression within high and low subgroups separately",
                "pros": "Avoids interaction term complexity",
                "cons": "Cannot statistically compare slopes between groups",
                "saber_verdict": "REJECTED"
            })

        elif "pre_post" in design or has_pretest:
            candidates.append({
                "path_id": "PATH_A_SABER_OPTIMAL",
                "name": "One-Way Analysis of Covariance (ANCOVA) with Baseline Control",
                "type": "modern_psychometric",
                "approach": "Pre-test as covariate, post-test as DV, group as factor",
                "pros": "Removes baseline error variance; adjusts for pre-test differences; superior power",
                "cons": "Requires homogeneity of regression slopes assumption",
                "saber_verdict": "RECOMMENDED"
            })
            candidates.append({
                "path_id": "PATH_B_ORTHODOX_SUPERVISOR",
                "name": "Gain Score Independent Samples t-test (D = Post - Pre)",
                "type": "traditional_supervisor",
                "approach": "Subtract pre from post scores and compare group means",
                "pros": "Very intuitive calculation",
                "cons": "Vulnerable to regression to the mean; implicitly fixes regression slope to 1.0; low power",
                "saber_verdict": "STRICTLY_REJECTED"
            })
            candidates.append({
                "path_id": "PATH_C_SPLIT_PLOT_ANOVA",
                "name": "Mixed Split-Plot Repeated Measures ANOVA (2 Groups × 2 Times)",
                "type": "robust_alternative",
                "approach": "Evaluate Time × Group interaction effect",
                "pros": "Robust fallback if regression slopes are non-parallel",
                "cons": "Reports identical interaction p-value to gain score in 2x2 design",
                "saber_verdict": "VIABLE_CONTINGENCY"
            })

        else:
            candidates.append({
                "path_id": "PATH_A_SABER_OPTIMAL",
                "name": "Hierarchical Linear Regression / Independent Parametric Analysis",
                "type": "modern_psychometric",
                "approach": "Parametric test with comprehensive assumption verification",
                "pros": "Maximum statistical power under normal distributions",
                "cons": "Vulnerable to assumption violations",
                "saber_verdict": "RECOMMENDED"
            })
            candidates.append({
                "path_id": "PATH_B_ORTHODOX_SUPERVISOR",
                "name": "Stepwise Multiple Regression",
                "type": "traditional_supervisor",
                "approach": "Automated variable entry based on statistical significance",
                "pros": "Completely automated in SPSS",
                "cons": "Capitalizes on sampling error; invalidates p-values; theoretically unsound",
                "saber_verdict": "STRICTLY_REJECTED"
            })
            candidates.append({
                "path_id": "PATH_C_NONPARAMETRIC",
                "name": "Robust Bootstrap or Non-Parametric Rank-Order Test",
                "type": "conservative_alternative",
                "approach": "Bootstrapped standard errors or Mann-Whitney / Kruskal-Wallis",
                "pros": "Zero distributional assumptions",
                "cons": "Slightly reduced power if normality holds",
                "saber_verdict": "VIABLE_CONTINGENCY"
            })

        # Stage 4: Apply Saber-style reasoning
        stat_consult = self.stat_reasoner.consult(case_spec)
        primary_choice = next((c for c in candidates if c["saber_verdict"] == "RECOMMENDED"), candidates[0])

        rejected_for_journal = [
            {"option": c["name"], "verdict": "REJECTED", "reason": c["cons"]}
            for c in candidates if "REJECTED" in c["saber_verdict"]
        ]

        # Stage 5: Make recommendation & record in Decision Journal
        recommendation_payload = {
            "selected_method": primary_choice["name"],
            "method_fa": stat_consult["recommendation"].get("method_fa", ""),
            "rationale": stat_consult["recommendation"].get("rationale", primary_choice["pros"]),
            "candidates_evaluated": candidates,
            "rejected_alternatives": stat_consult.get("rejected_alternatives", rejected_for_journal),
            "prerequisites": stat_consult.get("prerequisites_to_verify", []),
            "precedents_referenced": precedent_ids
        }

        did = self.decision_journal.log_decision(
            decision_type="methodological_selection",
            project_title=title,
            context=f"Autonomous candidate generation and evaluation for design '{design}', N={sample_size}.",
            selected_option=primary_choice["name"],
            rationale=recommendation_payload["rationale"],
            alternatives_considered=rejected_for_journal,
            confidence=0.95,
            human_gate_required=True,
            human_gate_approved=False
        )

        # Mark as pending outcome in journal
        self.decision_journal.update_decision(did, {
            "learning_cycle_stage": "PENDING_HUMAN_OUTCOME",
            "case_spec": case_spec,
            "precedent_ids": precedent_ids,
            "candidates": candidates
        })

        return {
            "decision_id": did,
            "project_title": title,
            "learning_stage": "RECOMMENDATION_GENERATED",
            "recommendation": recommendation_payload,
            "precedents_retrieved": [
                {
                    "case_id": p["case"].get("case_id"),
                    "similarity": p["similarity_score"],
                    "topic": p["case"].get("topic"),
                    "design": p["case"].get("design"),
                    "analysis": p["case"].get("statistical_analysis")
                }
                for p in precedents
            ]
        }

    # =========================================================================
    # STAGES 6-8: OUTCOME RECORDING, COMPARISON, KNOWLEDGE BASE UPDATE
    # =========================================================================
    def record_human_outcome(self,
                             decision_id: str,
                             human_decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes stages 6 to 8 of the learning cycle:
          6. Ingests human Saber's decision and real-world outcome
          7. Compares AI recommendation against human Saber decision
          8. Updates knowledge base (reinforces precedent or synthesizes new calibrated case)
        """
        # Find the decision record
        dec_record = next((d for d in self.decision_journal.decisions if d.get("decision_id") == decision_id), None)
        if not dec_record:
            return {"error": f"Decision {decision_id} not found in journal"}

        action = human_decision.get("action", "AGREE").upper()
        human_chosen_method = human_decision.get("chosen_method", dec_record.get("selected_option"))
        divergence_notes = human_decision.get("divergence_rationale", human_decision.get("notes", ""))
        supervisor_accepted = bool(human_decision.get("supervisor_accepted", True))
        lessons_learned = human_decision.get("lessons_learned", divergence_notes)

        # Stage 7: Compare AI recommendation vs Human Saber decision
        ai_recommendation = dec_record.get("selected_option", "")
        is_exact_match = (action == "AGREE") or (human_chosen_method.lower() in ai_recommendation.lower())
        is_adjusted = (action == "ADJUST")
        is_override = (action == "OVERRIDE") or (not is_exact_match and not is_adjusted)

        if is_exact_match:
            congruence_score = 1.0
            alignment_status = "PERFECT_CONGRUENCE (AGREED)"
        elif is_adjusted:
            congruence_score = 0.75
            alignment_status = "PARTIAL_ADJUSTMENT (REFINED)"
        else:
            congruence_score = 0.35
            alignment_status = "DIVERGENCE_OBSERVED (OVERRIDDEN)"

        precedent_ids = dec_record.get("precedent_ids", [])
        knowledge_update_action = {}

        # Stage 8: Update knowledge base
        if is_exact_match:
            # Reinforce precedent cases
            reinforced_cases = []
            for pid in precedent_ids:
                updated = self.case_memory.reinforce_case(
                    case_id=pid,
                    feedback_notes=f"Reinforced by Human Saber validation in decision {decision_id} ({dec_record.get('project_title')})."
                )
                if updated:
                    reinforced_cases.append(pid)

            knowledge_update_action = {
                "type": "REINFORCEMENT",
                "details": f"Reinforced confidence for precedent cases: {', '.join(reinforced_cases)}",
                "reinforced_case_ids": reinforced_cases
            }

        else:
            # Human Saber made an adjustment or divergence!
            # Automatically synthesize a new case into .agents/memory/cases/
            case_spec = dec_record.get("case_spec", {})
            title = dec_record.get("project_title", "پژوهش کالیبره‌شده")
            new_case_id = f"case_learned_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            new_case_data = {
                "case_id": new_case_id,
                "topic": title,
                "title_fa": title,
                "domain": case_spec.get("domain", "روان‌شناسی و مشاوره"),
                "population": case_spec.get("population", "عمومی"),
                "sample_size": case_spec.get("sample_size", 30),
                "design": case_spec.get("design", "semi_experimental"),
                "variables": case_spec.get("variables", []),
                "measures": case_spec.get("measures", []),
                "statistical_analysis": human_chosen_method,
                "decisions_made": [
                    f"Human Saber Selected: {human_chosen_method}",
                    f"AI Initial Suggestion: {ai_recommendation}",
                    f"Divergence Reason: {divergence_notes}"
                ],
                "lessons_learned": lessons_learned,
                "supervisor_outcome": "ACCEPTED" if supervisor_accepted else "REVISED",
                "calibration_source": "human_saber_feedback_loop",
                "congruence_with_initial_ai": congruence_score,
                "confidence_score": 0.98,
                "reinforcement_count": 1,
                "created_at": datetime.now().isoformat()
            }

            created_cid = self.case_memory.add_case(new_case_data, case_id=new_case_id)
            knowledge_update_action = {
                "type": "NEW_CASE_SYNTHESIZED",
                "details": f"Created new calibrated precedent case {created_cid} to encode Human Saber's refined decision rules.",
                "new_case_id": created_cid,
                "divergence_rationale": divergence_notes
            }

        # Update decision journal with final validated outcome
        self.decision_journal.update_decision(decision_id, {
            "learning_cycle_stage": "CALIBRATED_WITH_OUTCOME",
            "human_gate_approved": True,
            "approved_by": "GhaderiSaber (124911145)",
            "human_decision": human_decision,
            "alignment_status": alignment_status,
            "congruence_score": congruence_score,
            "knowledge_update": knowledge_update_action,
            "outcome_recorded_at": datetime.now().isoformat()
        })

        return {
            "decision_id": decision_id,
            "project_title": dec_record.get("project_title"),
            "alignment_status": alignment_status,
            "congruence_score": congruence_score,
            "human_decision": human_decision,
            "knowledge_update": knowledge_update_action
        }

    # =========================================================================
    # ANALYTICS & METRICS
    # =========================================================================
    def get_learning_stats(self) -> Dict[str, Any]:
        """Calculates continuous learning metrics and calibration history."""
        total_decisions = len(self.decision_journal.decisions)
        calibrated = [d for d in self.decision_journal.decisions if d.get("learning_cycle_stage") == "CALIBRATED_WITH_OUTCOME"]
        pending = [d for d in self.decision_journal.decisions if d.get("learning_cycle_stage") == "PENDING_HUMAN_OUTCOME"]

        congruence_scores = [d.get("congruence_score", 1.0) for d in calibrated]
        avg_congruence = round(sum(congruence_scores) / len(congruence_scores), 3) if congruence_scores else 1.0

        learned_cases = [c for c in self.case_memory.cases if "learned" in c.get("case_id", "") or c.get("calibration_source") == "human_saber_feedback_loop"]

        return {
            "total_historical_cases_in_memory": self.case_memory.count(),
            "newly_synthesized_learned_cases": len(learned_cases),
            "total_decisions_journaled": total_decisions,
            "pending_human_outcomes": len(pending),
            "calibrated_decisions_count": len(calibrated),
            "human_saber_congruence_rate": round(avg_congruence * 100, 1),
            "status": "CONTINUOUS_LEARNING_ACTIVE"
        }


def main():
    parser = argparse.ArgumentParser(description="Digital Saber Continuous Learning & Calibration Engine")
    parser.add_argument("--demo-cycle", action="store_true", help="Run full 8-step learning simulation")
    parser.add_argument("--stats", action="store_true", help="View continuous learning metrics")
    parser.add_argument("--json-case", type=str, help="Ingest a new case from JSON file")

    args = parser.parse_args()
    engine = ContinuousLearningEngine()

    if args.stats or len(sys.argv) == 1:
        stats = engine.get_learning_stats()
        print("\n" + "=" * 80)
        print("🧠 DIGITAL SABER CONTINUOUS LEARNING & CALIBRATION METRICS")
        print("=" * 80)
        print(f"📚 Total Cases in Memory:          {stats['total_historical_cases_in_memory']}")
        print(f"🌱 Cases Synthesized via Learning: {stats['newly_synthesized_learned_cases']}")
        print(f"📋 Total Decisions Journaled:      {stats['total_decisions_journaled']}")
        print(f"⏳ Pending Human Outcomes:         {stats['pending_human_outcomes']}")
        print(f"🎯 Calibrated Decisions:           {stats['calibrated_decisions_count']}")
        print(f"🤝 Human Saber Congruence Rate:    {stats['human_saber_congruence_rate']}%")
        print(f"⚡ Learning Engine Status:         {stats['status']}")
        print("=" * 80)
        return

    if args.demo_cycle:
        print("\n" + "=" * 80)
        print("🚀 SIMULATING 8-STEP CONTINUOUS LEARNING CYCLE")
        print("=" * 80)

        # Step 1-5: Process new case
        new_case = {
            "title": "اثربخشی واقعیت‌درمانی بر رفتارهای خودآسیب‌رسان و تاب‌آوری نوجوانان کانون اصلاح و تربیت",
            "objective": "difference",
            "design": "quasi_experimental_pre_post_control",
            "groups": 2,
            "sample_size": 28,
            "has_pretest": True,
            "variables": ["واقعیت درمانی", "رفتارهای خودآسیب‌رسان", "تاب‌آوری"],
            "measures": ["DSHI", "CD-RISC"]
        }

        print(f"\n[Stage 1-5] Ingesting New Case: {new_case['title']}")
        recom = engine.process_new_case(new_case)
        did = recom["decision_id"]
        print(f"Generated Decision ID: {did}")
        print(f"Selected Method:      {recom['recommendation']['selected_method']}")
        print(f"Precedents Used:      {[p['case_id'] for p in recom['precedents_retrieved']]}")

        # Step 6-8: Record human feedback (Divergence simulation where Human Saber advises Split-Plot due to slope interaction)
        print("\n[Stage 6-8] Ingesting Human Saber Decision (Refinement: Supervisor slope concern)...")
        human_feedback = {
            "action": "ADJUST",
            "chosen_method": "Johnson-Neyman Floodlight Technique + Split-Plot Repeated Measures ANOVA",
            "supervisor_accepted": True,
            "divergence_rationale": "Pre-test group variance difference indicated regression slope interaction; Johnson-Neyman preserves clinical interpretability across baseline severity.",
            "lessons_learned": "When youth delinquent samples show pre-test variance heterogeneity, prepare Johnson-Neyman floodlight contingency alongside ANCOVA."
        }

        outcome = engine.record_human_outcome(did, human_feedback)
        print(f"Alignment Status:  {outcome['alignment_status']}")
        print(f"Congruence Score:  {outcome['congruence_score'] * 100}%")
        print(f"Knowledge Update:  {outcome['knowledge_update']['type']} -> {outcome['knowledge_update']['details']}")
        print("=" * 80)


if __name__ == "__main__":
    main()
