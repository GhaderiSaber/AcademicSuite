#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Digital Saber — Professional AI Research Twin & Cognitive Command Interface
(دیجیتال صابر: دوقلوی هوشمند پژوهشی و سیستم جامع مشاوره و تصمیم‌گیری صابر قادری)

Unified master entry point integrating the 5 cognitive layers:
  1. Identity & Research Constitution
  2. Case-Based Memory & Decision Journal
  3. Epistemic & Statistical Reasoning Engines
  4. Specialized Skill Execution (27 Skills)
  5. Multi-Signal Quality Control & Defense Committee Simulation
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
IDENTITY_DIR = os.path.join(AGENTS_DIR, "identity")
MEMORY_DIR = os.path.join(AGENTS_DIR, "memory")
REASONING_DIR = os.path.join(AGENTS_DIR, "reasoning")
VERIFICATION_DIR = os.path.join(AGENTS_DIR, "verification")
EVAL_DIR = os.path.join(AGENTS_DIR, "evaluation")

# Add paths to sys.path
for p in [MEMORY_DIR, REASONING_DIR, VERIFICATION_DIR, EVAL_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from case_memory_engine import CaseMemoryEngine
    from decision_journal_engine import DecisionJournalEngine
    from statistical_reasoner import StatisticalReasoner
    from epistemic_literature_reasoner import EpistemicLiteratureReasoner
    from research_methodology_reasoner import ResearchMethodologyReasoner
    from writing_reasoner import AcademicWritingReasoner
    from multi_signal_anomaly_detector import MultiSignalAnomalyDetector
    from defense_committee_simulator import DefenseCommitteeSimulator
    from saber_similarity_evaluator import SaberSimilarityEvaluator
except ImportError as e:
    print(f"Warning: Module import failed: {e}", file=sys.stderr)


class DigitalSaber:
    """Master controller for the Digital Saber cognitive architecture."""

    def __init__(self):
        self.case_memory = CaseMemoryEngine()
        self.decision_journal = DecisionJournalEngine()
        self.stat_reasoner = StatisticalReasoner()
        self.lit_reasoner = EpistemicLiteratureReasoner()
        self.method_reasoner = ResearchMethodologyReasoner()
        self.writing_reasoner = AcademicWritingReasoner()
        self.anomaly_detector = MultiSignalAnomalyDetector()
        self.defense_sim = DefenseCommitteeSimulator()
        self.evaluator = SaberSimilarityEvaluator()

    def show_identity(self):
        """Displays Saber's Core Research Constitution & Philosophy."""
        const_path = os.path.join(IDENTITY_DIR, "SABER_RESEARCH_CONSTITUTION.md")
        phil_path = os.path.join(IDENTITY_DIR, "SABER_STATISTICAL_PHILOSOPHY.md")
        print("\n" + "=" * 80)
        print("🧠 DIGITAL SABER: CORE RESEARCH CONSTITUTION & PHILOSOPHY")
        print("=" * 80)
        if os.path.exists(const_path):
            with open(const_path, "r", encoding="utf-8") as f:
                lines = f.readlines()[:35]
                print("".join(lines))
        print("\n" + "-" * 80)
        print("Detailed Identity & Philosophy Files:")
        for doc in ["SABER_RESEARCH_CONSTITUTION.md", "SABER_STATISTICAL_PHILOSOPHY.md",
                    "SABER_ACADEMIC_WRITING_STYLE.md", "SABER_DECISION_RULES.md",
                    "SABER_QUALITY_STANDARDS.md"]:
            print(f" • .agents/identity/{doc}")
        print("=" * 80)

    def consult(self, query_or_file: str):
        """Runs the 3-stage statistical consultant."""
        profile = None
        if os.path.exists(query_or_file):
            with open(query_or_file, "r", encoding="utf-8") as f:
                profile = json.load(f)
        else:
            profile = {
                "topic": query_or_file,
                "objective": "difference",
                "design": "pre_post_control",
                "groups": 2,
                "sample_size": 30,
                "has_pretest": True,
                "is_normal": True
            }

        res = self.stat_reasoner.consult(profile)
        print("\n" + "=" * 80)
        print("🎓 DIGITAL SABER STATISTICAL CONSULTATION (STAGE A)")
        print("=" * 80)
        print(f"Topic:            {profile.get('topic')}")
        print(f"Selected Method:  {res['recommendation']['selected_method']}")
        print(f"Persian Method:   {res['recommendation']['method_fa']}")
        print(f"\nMethodological Rationale:\n  {res['recommendation']['rationale']}")
        print("\nExplicitly Rejected Alternatives:")
        for r in res["rejected_alternatives"]:
            print(f"  ❌ {r['option']}")
            print(f"     Reason: {r['reason']}")
        print("\nVerification Checklist:")
        for p in res["prerequisites_to_verify"]:
            print(f"  ✓ {p}")
        print("=" * 80)

    def query_precedents(self, query: str, top_k: int = 3):
        """Finds closest precedents in Case Memory."""
        results = self.case_memory.search_precedents(query, top_k=top_k)
        print("\n" + "=" * 80)
        print(f"📚 DIGITAL SABER CASE MEMORY PRECEDENTS (Query: '{query}')")
        print("=" * 80)
        for idx, res in enumerate(results, 1):
            c = res["case"]
            score = res["similarity_score"]
            print(f"[{idx}] {c.get('case_id')} | Match: {score:.3f}")
            print(f"    Topic:    {c.get('topic')}")
            print(f"    Design:   {c.get('design')} (N = {c.get('sample_size')})")
            print(f"    Analysis: {c.get('statistical_analysis')}")
            print(f"    Decisions: {', '.join(c.get('decisions_made', [])[:2])}")
            print("-" * 80)

    def evaluate_literature_claim(self, claim_text: str):
        """Evaluates epistemic strength of literature supporting a claim."""
        payload = {
            "claim_statement": claim_text,
            "supporting_studies": [
                {"citation": "Recent High-Impact RCT", "design": "rct", "sample_size": 120, "measurement_tool": "validated", "year": 2022}
            ],
            "contradicting_studies": []
        }
        res = self.lit_reasoner.evaluate_claim(payload)
        print("\n" + "=" * 80)
        print(f"🔬 DIGITAL SABER EPISTEMIC CLAIM EVALUATION")
        print("=" * 80)
        print(f"Claim:    {claim_text}")
        print(f"Verdict:  [{res['epistemic_verdict']}]")
        print(f"Details:  {res['rationale_fa']}")
        print(f"Ch 2:     {res['chapter2_guidance']}")
        print(f"Ch 5:     {res['chapter5_guidance']}")
        print("=" * 80)

    def run_multi_signal_audit(self, payload_file: Optional[str] = None):
        """Runs the upgraded multi-signal anomaly audit."""
        payload = {}
        if payload_file and os.path.exists(payload_file):
            with open(payload_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
        else:
            payload = {
                "tests": [{"test_id": "T1", "method": "ancova", "partial_eta_squared": 0.42}],
                "descriptives": {
                    "groups": [{"name": "Exp", "mean": 38.4, "sd": 2.1}, {"name": "Ctrl", "mean": 22.1, "sd": 2.4}],
                    "skewness": [0.12, -0.08]
                },
                "reliability": {"DV": 0.88}
            }

        res = self.anomaly_detector.evaluate_payload(payload)
        print("\n" + "=" * 80)
        print("🛡️ DIGITAL SABER MULTI-SIGNAL ANOMALY AUDIT")
        print("=" * 80)
        print(f"Verdict:        [{res['verdict']}]")
        print(f"Verdict (FA):   {res['verdict_fa']}")
        print(f"Anomaly Index:  {res['anomaly_index']} / 100")
        print(f"Active Signals: {res['active_signals_count']}")
        for s in res["signals"]:
            print(f"  🚩 [{s['signal_id']}] {s['title']}")
            print(f"     Details: {s['description']}")
            print(f"     Defense Advice: {s['defense_context']}")
        print(f"Advice: {res['defense_readiness_advice']}")
        print("=" * 80)

    def simulate_defense(self, topic: str):
        """Simulates oral defense viva voce examination."""
        prof = {"title": topic, "design": "ancova", "sample_size": 30, "iv": "مداخله روان‌شناختی", "dv": "نشانه‌های بالینی"}
        res = self.defense_sim.generate_defense_cross_examination(prof)
        print("\n" + "=" * 80)
        print(f"🎯 DIGITAL SABER DEFENSE COMMITTEE SIMULATION: {topic}")
        print("=" * 80)
        for idx, c in enumerate(res["challenges"], 1):
            print(f"[{idx}] {c['examiner_role']}:")
            print(f"    ❓ سوال داور: {c['challenge_fa']}")
            print(f"    💬 پاسخ مستدل دانشجو: {c['model_answer_fa']}")
            print(f"    📚 رفرنس پشتیبان: {c['apa7_evidence']}")
            print("-" * 80)

    def run_benchmark(self):
        """Runs the Saber Similarity Score evaluation benchmark."""
        res = self.evaluator.evaluate_all()
        print("\n" + "=" * 80)
        print("🏆 DIGITAL SABER SIMILARITY BENCHMARK REPORT")
        print("=" * 80)
        print(f"📊 Aggregate Saber Similarity Score: {res['aggregate_saber_similarity_score']}%")
        print(f"🏅 Overall Congruence Verdict:     {res['overall_verdict']}")
        print(f"📋 Total Dilemmas Evaluated:       {res['total_benchmark_cases_evaluated']} cases")
        print("-" * 80)
        print("ITEMIZED QUALITATIVE RUBRIC ACROSS 7 CORE DIMENSIONS:")
        print(f"{'Dimension':<25} | {'Weight':<6} | {'Score':<6} | {'Qualitative Assessment Status'}")
        print("-" * 80)
        for r in res["itemized_qualitative_rubric"]:
            print(f"{r['dimension']:<25} | {r['weight_percent']:>4}% | {r['average_score']:>5}% | {r['status']}")
        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Digital Saber — Professional AI Research Twin Master CLI")
    parser.add_argument("--identity", action="store_true", help="Display Saber Research Constitution & Philosophy")
    parser.add_argument("--consult", type=str, help="Run 3-stage statistical consultation on a topic or JSON profile")
    parser.add_argument("--cbr", type=str, help="Search Case Memory for historical research precedents")
    parser.add_argument("--epistemic", type=str, help="Evaluate evidence strength for an academic claim")
    parser.add_argument("--audit", type=str, nargs="?", const="default", help="Run multi-signal anomaly audit on JSON payload")
    parser.add_argument("--defense-sim", type=str, help="Simulate thesis defense viva voce examination")
    parser.add_argument("--benchmark", action="store_true", help="Run Saber Similarity Benchmark (both % and rubric)")

    args = parser.parse_args()
    saber = DigitalSaber()

    if args.identity:
        saber.show_identity()
    elif args.consult:
        saber.consult(args.consult)
    elif args.cbr:
        saber.query_precedents(args.cbr)
    elif args.epistemic:
        saber.evaluate_literature_claim(args.epistemic)
    elif args.audit:
        saber.run_multi_signal_audit(None if args.audit == "default" else args.audit)
    elif args.defense_sim:
        saber.simulate_defense(args.defense_sim)
    elif args.benchmark or len(sys.argv) == 1:
        saber.run_benchmark()


if __name__ == "__main__":
    main()
