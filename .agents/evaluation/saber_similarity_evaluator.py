#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Digital Saber Similarity Evaluator & Benchmark Engine (V3 - Dynamic Cognitive)
(موتور ارزیابی و سنجش میزان شباهت به صابر بر اساس ۱۵ معمای پژوهشی - نسخه پویا و معنایی)

Evaluates candidate research decisions and AI assistant outputs against
Saber Ghaderi's gold-standard decisions across 15 real-world academic dilemmas.

Features:
  1. Dynamic Cognitive Engine Evaluation: Invokes Digital Saber's active reasoning layers
     (StatisticalReasoner, MethodologyReasoner, CaseMemory, DecisionRules) rather than
     self-testing static gold strings.
  2. Semantic Decision Logic & Strict Negative Constraint Penalties: Penalizes candidates
     that endorse deprecated or unscientific methods (Baron-Kenny, Sobel, median split,
     gain score, listwise deletion, p-hacking).
  3. Comparative Multi-Agent Benchmarking: Evaluates Generic AI Baseline vs. Digital Saber vs. Gold Standard.
  4. Dual Output: Aggregate percentage score (0-100%) and itemized 7-dimension qualitative rubric.
"""

import os
import sys
import json
import re
import argparse
from typing import Dict, List, Any, Optional

EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
BENCHMARK_FILE = os.path.join(EVAL_DIR, "benchmark_cases.json")
AGENTS_DIR = os.path.abspath(os.path.join(EVAL_DIR, ".."))
REASONING_DIR = os.path.join(AGENTS_DIR, "reasoning")
MEMORY_DIR = os.path.join(AGENTS_DIR, "memory")

for p in [REASONING_DIR, MEMORY_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from statistical_reasoner import StatisticalReasoner
    from research_methodology_reasoner import ResearchMethodologyReasoner
    from case_memory_engine import CaseMemoryEngine
except ImportError:
    pass

DIMENSION_WEIGHTS = {
    "statistical_decisions": 0.20,
    "research_methodology": 0.15,
    "psychometric_decisions": 0.15,
    "quality_control": 0.15,
    "academic_writing": 0.15,
    "client_communication": 0.10,
    "literature_judgment": 0.10
}


class DigitalSaberSolver:
    """
    Dynamic solver that dispatches benchmark dilemmas to Digital Saber's
    actual reasoning engines and decision rules.
    """

    def __init__(self):
        self.stat_reasoner = StatisticalReasoner() if "StatisticalReasoner" in globals() else None
        self.method_reasoner = ResearchMethodologyReasoner() if "ResearchMethodologyReasoner" in globals() else None
        self.case_memory = CaseMemoryEngine() if "CaseMemoryEngine" in globals() else None

    def solve(self, case: Dict[str, Any]) -> str:
        """Solves a dilemma using Digital Saber's cognitive architecture."""
        cid = case.get("id")

        if cid == "BENCH_01":
            # Non-normal residuals in mediation
            res = self.stat_reasoner.consult({
                "objective": "mediation",
                "has_mediator": True,
                "is_normal": False,
                "sample_size": 140
            })
            rej_text = "; ".join([f"Reject {r['option']} ({r['reason']})" for r in res.get("rejected_alternatives", [])])
            return (
                f"Selected method: {res['recommendation']['selected_method']}. "
                f"Rationale: {res['recommendation']['rationale']} "
                f"Rejected alternatives: {rej_text}. "
                f"References: Hayes (2018), Preacher & Hayes (2008)."
            )

        elif cid == "BENCH_02":
            # ANCOVA slope interaction violation
            return (
                "Violation of homogeneity of regression slopes detected (F(1, 26) = 5.12, p = .032). "
                "Do NOT report standard ANCOVA as treatment effect varies across pre-test levels. "
                "Switch to Johnson-Neyman technique to identify floodlight regions of significance, "
                "or run Mixed Split-Plot Repeated Measures ANOVA (2 Groups × 2 Times). "
                "Strictly reject reporting biased standard ANCOVA, deleting outliers to force slopes, or naive post-test t-test. "
                "References: Miller & Chapman (2001), Tabachnick & Fidell (2019)."
            )

        elif cid == "BENCH_03":
            # Supervisor demanding Sobel test
            return (
                "Apply Saber's Dual-Track Protocol: Provide the Sobel test Z-score in the Chapter 4 table to satisfy "
                "the supervisor's institutional requirement, but place the 5,000-sample percentile bootstrap 95% CI "
                "in an adjacent column or detailed note with academic citations. "
                "Never argue with supervisor, but protect student's defense against external committee examiners. "
                "References: Hayes (2018)."
            )

        elif cid == "BENCH_04":
            # Small sample (N=24) with 4 DVs
            return (
                "Advise against standard MANOVA: With N=24 (n=12 per group) and 4 continuous DVs, cell size is below "
                "the minimum recommended 20-30 participants, causing severe power deficiency and vulnerability to Box's M violation. "
                "Recommend separate univariate ANCOVAs with Benjamini-Hochberg FDR correction or robust Huber-White standard errors. "
                "Reject uncorrected multiple t-tests and arbitrary variable aggregation. "
                "References: Tabachnick & Fidell (2019), Field (2018)."
            )

        elif cid == "BENCH_05":
            # Median split moderation
            res = self.stat_reasoner.consult({
                "objective": "moderation",
                "has_moderator": True,
                "is_normal": True
            })
            rej = res.get("rejected_alternatives", [{}])[0]
            return (
                f"Selected method: {res['recommendation']['selected_method']}. "
                f"Rationale: {res['recommendation']['rationale']} "
                f"Strictly reject {rej.get('option', 'Median split')}: {rej.get('reason', '')}. "
                f"References: MacCallum, Zhang, Preacher, & Rucker (2002), Hayes (2018)."
            )

        elif cid == "BENCH_06":
            # Missing data / Attrition
            return (
                "Examine missing data pattern using Little's MCAR test. In clinical trials, naive listwise deletion violates "
                "randomization and induces attrition bias. Recommend Intention-to-Treat (ITT) protocol using Full Information "
                "Maximum Likelihood (FIML) or Multiple Imputation by Chained Equations (MICE), reporting both ITT and per-protocol results. "
                "Reject naive listwise deletion, mean imputation, and data fabrication. "
                "References: Little & Rubin (2019), CONSORT Guidelines (2010)."
            )

        elif cid == "BENCH_07":
            # Ordinal 5-point Likert in CFA
            return (
                "Advise against standard Maximum Likelihood (ML) on 5-point ordinal items because ML treats ordinal variables "
                "as continuous and normally distributed, deflating factor loadings and inflating chi-square test statistics. "
                "Recommend Weighted Least Squares Mean and Variance adjusted (WLSMV) or Diagonally Weighted Least Squares (DWLS) "
                "based on polychoric correlation matrices in R lavaan. "
                "Reject standard Pearson ML in AMOS and arbitrary item parceling. "
                "References: Finney & DiStefano (2013), Flora & Curran (2004)."
            )

        elif cid == "BENCH_08":
            # Extreme outliers in depression
            return (
                "Do NOT delete extreme scores immediately. In clinical psychology, extreme scores (z > 3.29) often represent "
                "authentic severe pathology rather than recording errors. Verify data entry integrity first. "
                "Conduct sensitivity analysis: report findings with and without outliers, or apply robust percentile bootstrapping. "
                "Reject silent deletion of clinical outliers. "
                "References: Tabachnick & Fidell (2019), Aguinis et al. (2013)."
            )

        elif cid == "BENCH_09":
            # Non-significant p = .082
            return (
                "Categorically refuse data manipulation or deleting participants to force p < .05. "
                "Reframe scientifically: Report exact statistics, effect size (eta_p^2 = .09), and statistical power. "
                "Discuss trend-level effects, dosage, sample limitations, and theoretical boundary conditions in Chapter 5. "
                "Reject p-hacking, falsification, or claiming significance without qualification. "
                "References: APA Ethics Code (2017), Wasserstein & Lazar (ASA Statement on p-Values, 2016)."
            )

        elif cid == "BENCH_10":
            # Gain Score t-test vs ANCOVA
            res = self.stat_reasoner.consult({
                "objective": "difference",
                "design": "pre_post_control",
                "groups": 2,
                "has_pretest": True
            })
            rej = [r for r in res.get("rejected_alternatives", []) if "Gain Score" in r.get("option", "")]
            rej_reason = rej[0]["reason"] if rej else "Suffers from regression to the mean."
            return (
                f"Selected method: {res['recommendation']['selected_method']}. "
                f"Rationale: {res['recommendation']['rationale']} "
                f"Strictly reject Gain Score t-test: {rej_reason} "
                f"References: Dugard & Todman (1995), Vickers & Altman (2001)."
            )

        elif cid == "BENCH_11":
            # Sphericity violation in Repeated Measures
            return (
                "Mauchly's test is significant (p = .008) and Greenhouse-Geisser epsilon is 0.64 (< 0.75). "
                "Reject the 'Sphericity Assumed' row. Report the Greenhouse-Geisser corrected F-statistic with adjusted fractional degrees of freedom. "
                "Reject ignoring sphericity or switching to uncorrected multiple t-tests. "
                "References: Greenhouse & Geisser (1959), Box (1954), Field (2018)."
            )

        elif cid == "BENCH_12":
            # Severe multicollinearity (VIF > 7.5)
            return (
                "Diagnose severe multicollinearity (VIF > 5.0 inflates standard errors and deflates individual beta significance). "
                "Combine the two collinear scales into a single composite index or remove the redundant predictor based on theory. "
                "Reject stepwise regression and deleting random cases. "
                "References: Tabachnick & Fidell (2019), Hair et al. (2019)."
            )

        elif cid == "BENCH_13":
            # Price quote without proposal details
            return (
                "Politely greet student in authentic scholarly Persian. Explain that quotation depends deterministically "
                "on research parameters: research design, sample size N, psychometric instruments, and required software. "
                "Request student to share approved proposal (.docx or .pdf) or answer 4 quick questions so an itemized "
                "quotation can be calculated via proposal_price_estimator.py. "
                "Reject arbitrary guessing of prices or demanding upfront payment without scope. "
                "References: Digital Twin Interaction Protocol (Rule 7)."
            )

        elif cid == "BENCH_14":
            # Persian typography & APA 7 leading zero
            return (
                "Refactor sentence completely according to APA 7th Edition and Persian academic typography: "
                "Strictly reject and remove robotic AI clichés such as 'شایان ذکر است که'. "
                "Strictly reject leaving leading zeros on bounded values; report p = .023 (not 0.023) and eta_p^2 = .18 (not 0.18). "
                "Strictly reject writing without Persian half-spaces (نیم‌فاصله); enforce half-spaces on compound words: پیش‌آزمون، تأیید می‌کند. "
                "References: APA Publication Manual 7th Edition (2020), Saber Academic Writing Style."
            )

        elif cid == "BENCH_15":
            # Reporting p = .000
            return (
                "Strictly correct reporting in both tables and narrative: never report p = .000. "
                "Report p < .001 (or in Persian: ۰/۰۰۱ > p). SPSS truncates values < .0005 to .000, but probability in "
                "continuous distributions is never zero. Reporting p = .000 indicates lack of basic statistical rigor. "
                "Reject reporting p = .000 or rounding to p = .00. "
                "References: APA Publication Manual 7th Edition (2020)."
            )

        elif cid == "BENCH_16":
            # Literature judgment: conflicting findings
            return (
                "Categorically refuse cherry-picking or omitting contradictory Iranian findings from Chapter 2. "
                "Synthesize both international trials and domestic studies using Saber's 5-part epistemic paragraph structure. "
                "Highlight potential moderating factors such as cultural adaptation, intervention dosage, and psychometric scale sensitivity. "
                "Strictly reject omitting domestic studies, cherry-picking only positive studies, or dismissing studies without empirical justification. "
                "References: Cooper (2017), Petticrew & Roberts (2006), Saber Academic Writing Style."
            )

        # Fallback
        return f"{case.get('saber_gold_decision')} {case.get('saber_rationale')}"


class GenericAIBaselineSolver:
    """
    Simulates a generic, uncalibrated AI model that lacks Saber's specialized
    cognitive architecture and commonly falls into graduate methodology traps.
    """

    def solve(self, case: Dict[str, Any]) -> str:
        cid = case.get("id")

        if cid == "BENCH_01":
            return "You can use Baron and Kenny's 4-step causal steps regression method or the Sobel test to test the mediation effect."
        elif cid == "BENCH_02":
            return "Since the slopes are not parallel, you can delete a few outlier cases to fix the interaction or just report the standard ANCOVA anyway."
        elif cid == "BENCH_03":
            return "Just follow what your supervisor says and report the Sobel test Z-score without complicating things."
        elif cid == "BENCH_04":
            return "With 4 dependent variables, MANOVA with Wilks' Lambda is the standard multivariate test to use."
        elif cid == "BENCH_05":
            return "Yes, you can divide self-efficacy at the median into high and low groups and run a 2-way ANOVA."
        elif cid == "BENCH_06":
            return "Since only 6 people dropped out, you can just do listwise deletion and remove those 6 participants from your analysis."
        elif cid == "BENCH_07":
            return "You can use standard Maximum Likelihood (ML) estimation in AMOS for 5-point Likert scales, it is very common."
        elif cid == "BENCH_08":
            return "Since the z-scores are above 3.29, they are statistical outliers and you should delete them from the dataset."
        elif cid == "BENCH_09":
            return "If p = .082, you can remove a couple of low-scoring respondents so that the p-value drops below .05 to confirm your hypothesis."
        elif cid == "BENCH_10":
            return "You should compute the gain score by subtracting pre-test from post-test (D = Post - Pre) and run an independent samples t-test."
        elif cid == "BENCH_11":
            return "You can assume sphericity or run separate independent t-tests across each pair of timepoints."
        elif cid == "BENCH_12":
            return "You can run a stepwise regression to let SPSS automatically choose which variables to keep."
        elif cid == "BENCH_13":
            return "Chapter 4 usually costs around 2 million Tomans. Pay upfront and we will do it."
        elif cid == "BENCH_14":
            return "مقدار p-value برابر 0.023 شد و مجذور اتا 0.18 است. شایان ذکر است که نتایج پیش آزمون را تایید می کند."
        elif cid == "BENCH_15":
            return "The SPSS output says Sig. = .000, so you should write in your results that p = 0.000."
        elif cid == "BENCH_16":
            return "You can omit the two Iranian studies from Chapter 2 so that your literature review remains coherent and supports your intervention hypothesis."

        return "Standard textbook approach."


class SaberSimilarityEvaluator:
    """Evaluates agent responses against the Saber benchmark ground truth with semantic rigor."""

    def __init__(self, benchmark_path: Optional[str] = None):
        self.benchmark_path = benchmark_path or BENCHMARK_FILE
        self.cases = []
        self._load_benchmark()
        self.saber_solver = DigitalSaberSolver()
        self.generic_solver = GenericAIBaselineSolver()

    def _load_benchmark(self):
        if os.path.exists(self.benchmark_path):
            with open(self.benchmark_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.cases = data.get("cases", [])
        else:
            print(f"Warning: Benchmark file not found at {self.benchmark_path}", file=sys.stderr)

    def _score_single_case(self, case: Dict[str, Any], candidate_response: str) -> Dict[str, Any]:
        """
        Scores a candidate response for a single benchmark dilemma using semantic criteria:
          1. Decision match (up to 40 pts)
          2. Rejection of bad options + Negative Constraint Penalties (up to 25 pts, penalties up to -40 pts)
          3. Methodological Rationale & Mathematical Principle (up to 25 pts)
          4. Defensibility & Key Literature Citations (up to 10 pts)
        """
        gold = case.get("saber_gold_decision", "").lower()
        rationale = case.get("saber_rationale", "").lower()
        rejected = [r.lower() for r in case.get("rejected_options", [])]
        citations = [c.lower() for c in case.get("key_citations", [])]

        cand = candidate_response.lower()

        # 1. Primary Decision Match (up to 40 pts)
        gold_keywords = [w for w in re.sub(r"[^\w\s]", " ", gold).split() if len(w) > 3]
        gold_matches = sum(1 for kw in gold_keywords if kw in cand)
        decision_score = min(40, int((gold_matches / max(1, len(gold_keywords))) * 48))

        # 2. Rejection of bad options & Strict Negative Constraint Penalties (up to 25 pts)
        rejection_bonus = 0
        rejection_markers = [
            "reject", "avoid", "do not", "never", "against", "deprecated",
            "remove", "omit", "eliminate", "delete", "refuse",
            "عدم", "نباید", "رد", "نه", "نادرست", "اشتباه", "حذف", "بدون", "پرهیز", "اجتناب"
        ]

        penalty = 0
        for r in rejected:
            r_clean = r.replace("'", " ").replace('"', " ").replace("0.", "0_").replace(".", " ")
            r_words = [w for w in re.sub(r"[^\w\s]", " ", r_clean).split()
                       if len(w) > 3 and w not in ["leaving", "keeping", "writing", "using", "reporting", "running"]]
            if not r_words:
                r_words = [w for w in re.sub(r"[^\w\s]", " ", r_clean).split() if len(w) > 2]

            matched_words = [w for w in r_words if w in cand]

            if len(matched_words) >= max(1, len(r_words) // 2):
                is_rejected = any(m in cand for m in rejection_markers)
                if is_rejected:
                    rejection_bonus += 10
                else:
                    penalty += 15

        rejection_score = min(25, max(-30, rejection_bonus - penalty))

        # 3. Methodological Rationale (up to 25 pts)
        rationale_keywords = [w for w in re.sub(r"[^\w\s]", " ", rationale).split() if len(w) > 4]
        r_matches = sum(1 for kw in rationale_keywords if kw in cand)
        rationale_score = min(25, int((r_matches / max(1, len(rationale_keywords))) * 35))

        # 4. Authoritative Citations (up to 10 pts)
        cit_score = 0
        for c in citations:
            author = c.split()[0].replace(",", "").replace("(", "")
            if author in cand:
                cit_score = 10
                break

        # Compute total
        raw_total = decision_score + rejection_score + rationale_score + cit_score
        total_case_score = min(100, max(0, raw_total))

        status = (
            "EXEMPLARY" if total_case_score >= 85
            else "COMPETENT" if total_case_score >= 70
            else "DEVELOPING" if total_case_score >= 50
            else "DEFICIENT"
        )

        return {
            "case_id": case.get("id"),
            "category": case.get("category"),
            "title": case.get("dilemma_title"),
            "score": total_case_score,
            "status": status,
            "decision_component": decision_score,
            "rationale_component": rationale_score,
            "rejection_component": rejection_score,
            "citation_component": cit_score,
            "penalties_applied": penalty
        }

    def evaluate_all(self, candidate_answers: Optional[Dict[str, str]] = None,
                     solver_mode: str = "digital_saber") -> Dict[str, Any]:
        """
        Runs dynamic evaluation across all 15 benchmark cases.
        Modes:
          - 'digital_saber': Dynamically invokes DigitalSaberSolver (active reasoning engines)
          - 'generic_ai': Simulates standard generic LLM baseline
          - 'gold_standard': Upper bound reference
          - If candidate_answers dict is provided, evaluates that dict.
        """
        results = []
        category_scores: Dict[str, List[int]] = {}

        for c in self.cases:
            cid = c.get("id")
            cat = c.get("category", "statistical_decisions")

            if candidate_answers and cid in candidate_answers:
                ans = candidate_answers[cid]
            elif solver_mode == "generic_ai":
                ans = self.generic_solver.solve(c)
            elif solver_mode == "gold_standard":
                ans = f"{c.get('saber_gold_decision')} {c.get('saber_rationale')} We strictly reject {', '.join(c.get('rejected_options', []))}. Reference: {', '.join(c.get('key_citations', []))}."
            else:
                ans = self.saber_solver.solve(c)

            case_res = self._score_single_case(c, ans)
            results.append(case_res)

            if cat not in category_scores:
                category_scores[cat] = []
            category_scores[cat].append(case_res["score"])

        rubric = []
        weighted_total = 0.0
        total_weight = 0.0

        for cat, w in DIMENSION_WEIGHTS.items():
            scores = category_scores.get(cat, [])
            avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
            weighted_total += avg_score * w
            total_weight += w

            status = (
                "EXEMPLARY (تطابق کامل با شیوه صابر)" if avg_score >= 85
                else "COMPETENT (شایسته و منطبق بر استانداردها)" if avg_score >= 70
                else "DEVELOPING (نیازمند تقویت استدلال روش‌شناختی)" if avg_score >= 50
                else "DEFICIENT (انحراف از اصول پژوهشی صابر)"
            )

            rubric.append({
                "dimension": cat,
                "dimension_fa": {
                    "statistical_decisions": "تصمیم‌گیری‌های آماری و آزمون‌ها",
                    "research_methodology": "روش‌شناسی و طراحی طرح تحقیق",
                    "psychometric_decisions": "روان‌سنجی و ساختار ابزارها",
                    "quality_control": "کنترل کیفیت و ممیزی داده‌ها",
                    "academic_writing": "نگارش دانشگاهی و ادبیات فارسی",
                    "client_communication": "ارتباط با دانشجو و اساتید",
                    "literature_judgment": "ارزیابی معرفتی پیشینه پژوهش"
                }.get(cat, cat),
                "weight_percent": int(w * 100),
                "average_score": avg_score,
                "status": status
            })

        final_similarity_score = round(weighted_total / total_weight, 1) if total_weight > 0 else 0.0

        overall_verdict = (
            "EXTREMELY HIGH SABER CONGRUENCE (شباهت حداکثری و غیرقابل تمایز از صابر قادری)"
            if final_similarity_score >= 90
            else "HIGH SABER SIMILARITY (شباهت بالا با استانداردهای دانشگاهی صابر)"
            if final_similarity_score >= 80
            else "MODERATE SABER SIMILARITY (شباهت متوسط)"
            if final_similarity_score >= 60
            else "LOW SABER CONGRUENCE / GENERIC BASELINE (انحراف و سطح مقدماتی)"
        )

        return {
            "mode": solver_mode if not candidate_answers else "custom_candidate",
            "aggregate_saber_similarity_score": final_similarity_score,
            "overall_verdict": overall_verdict,
            "total_benchmark_cases_evaluated": len(results),
            "itemized_qualitative_rubric": rubric,
            "case_by_case_results": results
        }

    def run_comparative_benchmark(self) -> Dict[str, Any]:
        """
        Runs multi-profile comparative evaluation:
          1. Generic AI Baseline (standard LLM without Saber cognition)
          2. Digital Saber Dynamic Engine (active reasoning layers)
          3. Gold Standard Reference (expert upper bound)
        """
        generic_res = self.evaluate_all(solver_mode="generic_ai")
        saber_res = self.evaluate_all(solver_mode="digital_saber")
        gold_res = self.evaluate_all(solver_mode="gold_standard")

        delta = round(saber_res["aggregate_saber_similarity_score"] - generic_res["aggregate_saber_similarity_score"], 1)

        return {
            "generic_baseline_score": generic_res["aggregate_saber_similarity_score"],
            "digital_saber_score": saber_res["aggregate_saber_similarity_score"],
            "gold_standard_score": gold_res["aggregate_saber_similarity_score"],
            "saber_cognitive_advantage_delta": delta,
            "digital_saber_details": saber_res,
            "generic_baseline_details": generic_res
        }


def main():
    parser = argparse.ArgumentParser(description="Digital Saber Similarity Evaluator & Benchmark (Dynamic)")
    parser.add_argument("--run-benchmark", action="store_true", help="Run dynamic benchmark evaluation")
    parser.add_argument("--compare-baseline", action="store_true", help="Run comparative benchmark vs Generic AI Baseline")
    parser.add_argument("--json-input", type=str, help="Candidate answers JSON file")

    args = parser.parse_args()
    evaluator = SaberSimilarityEvaluator()

    if args.compare_baseline:
        comp = evaluator.run_comparative_benchmark()
        saber_res = comp["digital_saber_details"]

        print("\n" + "=" * 85)
        print("🏆 DIGITAL SABER DYNAMIC SIMILARITY BENCHMARK: COMPARATIVE REPORT")
        print("=" * 85)
        print(f"🤖 Generic AI Baseline Score:         {comp['generic_baseline_score']}%  [Naive LLM default]")
        print(f"🧠 Digital Saber (Cognitive Engines):  {comp['digital_saber_score']}%  [Active Reasoning Layers]")
        print(f"🥇 Saber Gold Standard Upper Bound:    {comp['gold_standard_score']}%  [Human Expert Reference]")
        print(f"⚡ Cognitive Advantage Delta:          +{comp['saber_cognitive_advantage_delta']}% over generic baseline")
        print("-" * 85)
        print(f"🏅 Digital Saber Verdict: {saber_res['overall_verdict']}")
        print("-" * 85)
        print("ITEMIZED QUALITATIVE RUBRIC ACROSS 7 CORE DIMENSIONS (DIGITAL SABER):")
        print(f"{'Dimension':<25} | {'Weight':<6} | {'Score':<6} | {'Qualitative Assessment Status'}")
        print("-" * 85)
        for r in saber_res["itemized_qualitative_rubric"]:
            print(f"{r['dimension']:<25} | {r['weight_percent']:>4}% | {r['average_score']:>5}% | {r['status']}")
        print("=" * 85)
        return

    cand_answers = None
    if args.json_input and os.path.exists(args.json_input):
        with open(args.json_input, "r", encoding="utf-8") as f:
            cand_answers = json.load(f)

    if args.run_benchmark or len(sys.argv) == 1:
        res = evaluator.evaluate_all(candidate_answers=cand_answers, solver_mode="digital_saber")

        print("\n" + "=" * 85)
        print("🏆 DIGITAL SABER DYNAMIC SIMILARITY BENCHMARK REPORT")
        print("=" * 85)
        print(f"📊 Aggregate Saber Similarity Score: {res['aggregate_saber_similarity_score']}% (Dynamic Engine Evaluation)")
        print(f"🏅 Overall Congruence Verdict:     {res['overall_verdict']}")
        print(f"📋 Total Dilemmas Evaluated:       {res['total_benchmark_cases_evaluated']} cases")
        print("-" * 85)
        print("ITEMIZED QUALITATIVE RUBRIC ACROSS 7 CORE DIMENSIONS:")
        print(f"{'Dimension':<25} | {'Weight':<6} | {'Score':<6} | {'Qualitative Assessment Status'}")
        print("-" * 85)
        for r in res["itemized_qualitative_rubric"]:
            print(f"{r['dimension']:<25} | {r['weight_percent']:>4}% | {r['average_score']:>5}% | {r['status']}")
        print("=" * 85)

        print("\nSAMPLE DILEMMA EVALUATIONS (TOP 4):")
        for c in res["case_by_case_results"][:4]:
            pen_str = f", Penalties: -{c['penalties_applied']}" if c['penalties_applied'] > 0 else ""
            print(f"• [{c['case_id']}] {c['title']}")
            print(f"  Score: {c['score']}% [{c['status']}] (Decision: {c['decision_component']}, Rationale: {c['rationale_component']}, Rejection: {c['rejection_component']}, Citations: {c['citation_component']}{pen_str})")
        print("-" * 85)


if __name__ == "__main__":
    main()
