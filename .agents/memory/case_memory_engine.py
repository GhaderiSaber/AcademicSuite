#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Digital Saber Case-Based Reasoning (CBR) Memory Engine
(موتور حافظه مبتنی بر پیشینه و پرونده‌های پژوهشی دیجیتال صابر)

Indexes, searches, and retrieves historical academic research precedents
to guide new methodological, statistical, and design decisions.
"""

import os
import sys
import json
import math
import argparse
import re
from collections import Counter
from typing import Dict, List, Any, Optional
from datetime import datetime

MEMORY_DIR = os.path.dirname(os.path.abspath(__file__))
CASES_DIR = os.path.join(MEMORY_DIR, "cases")


class CaseMemoryEngine:
    """Manages historical research case indexing, retrieval, and similarity matching."""

    def __init__(self, cases_dir: Optional[str] = None):
        self.cases_dir = cases_dir or CASES_DIR
        os.makedirs(self.cases_dir, exist_ok=True)
        self.cases: List[Dict[str, Any]] = []
        self.bm25_fields = ["topic", "design", "variables", "domain"]
        self.bm25_weights = {"topic": 0.40, "design": 0.25, "variables": 0.25, "domain": 0.10}
        self.doc_tokens: Dict[str, List[List[str]]] = {}
        self.tf: Dict[str, List[Counter]] = {}
        self.df: Dict[str, Counter] = {}
        self.doc_len: Dict[str, List[int]] = {}
        self.avg_doc_len: Dict[str, float] = {}
        self.idf: Dict[str, Dict[str, float]] = {}
        self._load_cases()

    def _load_cases(self):
        """Loads all JSON cases from the cases directory."""
        self.cases = []
        if not os.path.exists(self.cases_dir):
            return

        for fname in sorted(os.listdir(self.cases_dir)):
            if fname.endswith(".json"):
                fpath = os.path.join(self.cases_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            data["_file"] = fname
                            self.cases.append(data)
                except Exception as e:
                    print(f"Warning: Could not load case {fname}: {e}", file=sys.stderr)
        self._build_bm25_indices()

    def count(self) -> int:
        return len(self.cases)

    def add_case(self, case_data: Dict[str, Any], case_id: Optional[str] = None) -> str:
        """Adds and persists a new historical case."""
        cid = case_id or case_data.get("case_id") or f"case_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        case_data["case_id"] = cid
        case_data["created_at"] = case_data.get("created_at") or datetime.now().isoformat()

        fpath = os.path.join(self.cases_dir, f"{cid}.json")
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(case_data, f, ensure_ascii=False, indent=2)

        self._load_cases()
        return cid

    def reinforce_case(self, case_id: str, feedback_notes: str = "") -> Optional[Dict[str, Any]]:
        """Reinforces a case when human Saber validates the recommendation."""
        for c in self.cases:
            if c.get("case_id") == case_id:
                fname = c.get("_file") or f"{case_id}.json"
                fpath = os.path.join(self.cases_dir, fname)
                c["reinforcement_count"] = c.get("reinforcement_count", 0) + 1
                c["confidence_score"] = min(1.0, round(c.get("confidence_score", 0.90) + 0.02, 3))
                c["last_reinforced_at"] = datetime.now().isoformat()
                if feedback_notes:
                    notes = c.get("reinforcement_history", [])
                    notes.append({"timestamp": datetime.now().isoformat(), "note": feedback_notes})
                    c["reinforcement_history"] = notes
                save_data = {k: v for k, v in c.items() if k != "_file"}
                with open(fpath, "w", encoding="utf-8") as f:
                    json.dump(save_data, f, ensure_ascii=False, indent=2)
                self._load_cases()
                return c
        return None

    def _normalize_text(self, text: str) -> str:
        """Normalizes Persian and English text (half-spaces, Arabic chars, diacritics, punctuation)."""
        if not text:
            return ""
        t = str(text).lower()
        t = t.replace("\u200c", " ")
        replacements = {
            "ي": "ی", "ك": "ک", "ة": "ه", "ؤ": "و",
            "إ": "ا", "أ": "ا", "آ": "ا"
        }
        for k, v in replacements.items():
            t = t.replace(k, v)
        t = re.sub(r"[\u064b-\u065f\u0670]", "", t)
        t = re.sub(r"[\.\,\،\;\:\(\)\[\]\{\}\"\'\?\؟\!\-\_\/\\\|\+\=\*\&\^\%\$\#\@\~\`<>]", " ", t)
        return re.sub(r"\s+", " ", t).strip()

    def _tokenize_bm25(self, text: str) -> List[str]:
        """Tokenizes text preserving token frequency for BM25 calculation."""
        norm = self._normalize_text(text)
        return [w for w in norm.split() if len(w) > 1]

    def _build_bm25_indices(self):
        """Constructs multi-field inverted index and BM25 statistics."""
        self.doc_tokens = {fld: [] for fld in self.bm25_fields}
        self.tf = {fld: [] for fld in self.bm25_fields}
        self.df = {fld: Counter() for fld in self.bm25_fields}
        self.doc_len = {fld: [] for fld in self.bm25_fields}
        self.avg_doc_len = {fld: 0.0 for fld in self.bm25_fields}
        self.idf = {fld: {} for fld in self.bm25_fields}

        N = len(self.cases)
        if N == 0:
            return

        for case in self.cases:
            ftexts = {
                "topic": f"{case.get('topic', '')} {case.get('title_fa', '')} {case.get('title_en', '')}",
                "design": f"{case.get('design', '')} {case.get('methodology', '')} {case.get('statistical_analysis', '')}",
                "variables": " ".join([str(v) for v in case.get("variables", [])] + [str(m) for m in case.get("measures", [])] + [str(q) for q in case.get("questionnaires", [])]),
                "domain": f"{case.get('domain', '')} {case.get('population', '')}"
            }
            for fld in self.bm25_fields:
                toks = self._tokenize_bm25(ftexts[fld])
                self.doc_tokens[fld].append(toks)
                self.doc_len[fld].append(len(toks))
                c_tf = Counter(toks)
                self.tf[fld].append(c_tf)
                for term in c_tf.keys():
                    self.df[fld][term] += 1

        for fld in self.bm25_fields:
            self.avg_doc_len[fld] = sum(self.doc_len[fld]) / max(1, N)
            for term, term_df in self.df[fld].items():
                self.idf[fld][term] = math.log(1.0 + (N - term_df + 0.5) / (term_df + 0.5))

    def _tokenize(self, text: str) -> set:
        """Legacy linguistic tokenizer supporting Persian and English."""
        norm = self._normalize_text(text)
        return {w for w in norm.split() if len(w) > 1}

    def _calculate_similarity(self, query_tokens: set, case: Dict[str, Any], weights: Dict[str, float]) -> float:
        """Legacy multi-attribute Jaccard similarity between query and case."""
        score = 0.0
        title_text = f"{case.get('topic', '')} {case.get('title_fa', '')} {case.get('title_en', '')}"
        title_tokens = self._tokenize(title_text)
        if title_tokens and query_tokens:
            jaccard_title = len(query_tokens & title_tokens) / len(query_tokens | title_tokens)
            score += jaccard_title * weights.get("topic", 0.35)

        design_text = f"{case.get('design', '')} {case.get('methodology', '')} {case.get('statistical_analysis', '')}"
        design_tokens = self._tokenize(design_text)
        if design_tokens and query_tokens:
            jaccard_design = len(query_tokens & design_tokens) / len(query_tokens | design_tokens)
            score += jaccard_design * weights.get("design", 0.25)

        vars_list = case.get("variables", [])
        scales_list = case.get("measures", []) + case.get("questionnaires", [])
        var_text = " ".join([str(v) for v in vars_list] + [str(s) for s in scales_list])
        var_tokens = self._tokenize(var_text)
        if var_tokens and query_tokens:
            jaccard_var = len(query_tokens & var_tokens) / len(query_tokens | var_tokens)
            score += jaccard_var * weights.get("variables", 0.25)

        domain_text = f"{case.get('domain', '')} {case.get('population', '')}"
        domain_tokens = self._tokenize(domain_text)
        if domain_tokens and query_tokens:
            jaccard_domain = len(query_tokens & domain_tokens) / len(query_tokens | domain_tokens)
            score += jaccard_domain * weights.get("domain", 0.15)

        return score

    def _calculate_bm25_similarity(self, query: str, case_idx: int, k1: float = 1.2, b: float = 0.75) -> float:
        """Calculates multi-field BM25 similarity with subword matching and bounded [0.0, 1.0] scaling."""
        q_toks = self._tokenize_bm25(query)
        if not q_toks:
            return 0.0

        N = len(self.cases)
        if case_idx >= N:
            return 0.0

        case = self.cases[case_idx]
        norm_q = self._normalize_text(query)
        total_score = 0.0

        # Exact phrase bonus in topic or title
        topic_all = self._normalize_text(f"{case.get('topic', '')} {case.get('title_fa', '')} {case.get('title_en', '')}")
        if norm_q and norm_q in topic_all:
            total_score += 1.5

        for fld in self.bm25_fields:
            fld_score = 0.0
            fld_tf = self.tf[fld][case_idx]
            L = self.doc_len[fld][case_idx]
            avg_L = self.avg_doc_len[fld]

            for q in set(q_toks):
                count = fld_tf.get(q, 0)
                term_idf = self.idf[fld].get(q, 0.0)

                # Subword/substring fallback if exact term not present
                if count == 0:
                    sub_matches = sum(freq for t, freq in fld_tf.items() if (q in t or t in q) and min(len(q), len(t)) >= 3)
                    if sub_matches > 0:
                        count = sub_matches * 0.5
                        term_idf = math.log(1.0 + (N + 0.5) / (max(1, self.df[fld].get(q, 1)) + 0.5))

                if count > 0 and term_idf > 0:
                    num = count * (k1 + 1.0)
                    den = count + k1 * (1.0 - b + b * (L / max(1.0, avg_L)))
                    fld_score += term_idf * (num / den)

            total_score += self.bm25_weights.get(fld, 0.25) * fld_score

        # Map to bounded [0.0, 1.0] interval with smooth saturation curve
        return round(total_score / (total_score + 2.0), 4)

    def search_precedents(self, query: str, top_k: int = 3, filter_design: Optional[str] = None) -> List[Dict[str, Any]]:
        """Searches historical cases for the closest precedents using multi-field BM25."""
        if not self.cases:
            return []

        scored = []
        for idx, case in enumerate(self.cases):
            if filter_design:
                cdesign = case.get("design", "").lower()
                if filter_design.lower() not in cdesign:
                    continue

            sim = self._calculate_bm25_similarity(query, idx)
            scored.append({"case": case, "similarity_score": sim})

        scored.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored[:top_k]

    def adapt_precedent(self, target_scenario: Dict[str, Any], best_case: Dict[str, Any]) -> Dict[str, Any]:
        """Generates an adaptation guidance comparing new scenario with historical precedent."""
        c = best_case
        t = target_scenario

        adaptation = {
            "precedent_case_id": c.get("case_id"),
            "precedent_topic": c.get("topic"),
            "target_topic": t.get("topic"),
            "common_elements": [],
            "differences_requiring_adaptation": [],
            "recommended_analytical_path": c.get("statistical_analysis"),
            "precedent_decisions": c.get("decisions_made", []),
            "precedent_supervisor_challenges": c.get("supervisor_challenges", []),
            "defense_guidance": c.get("defense_guidance", "")
        }

        # Check sample size difference
        c_n = c.get("sample_size", 0)
        t_n = t.get("sample_size", 0)
        if t_n and c_n:
            if t_n < c_n * 0.7:
                adaptation["differences_requiring_adaptation"].append(
                    f"Target sample size (N={t_n}) is noticeably smaller than precedent (N={c_n}). Power analysis required; non-parametric fallback or bootstrap recommended."
                )
            elif t_n > c_n * 1.5:
                adaptation["differences_requiring_adaptation"].append(
                    f"Target sample size (N={t_n}) is substantially larger than precedent (N={c_n}). Watch for statistical significance of trivial effect sizes."
                )

        # Check design match
        c_des = c.get("design", "")
        t_des = t.get("design", "")
        if c_des and t_des:
            if c_des.lower() == t_des.lower():
                adaptation["common_elements"].append(f"Identical research design: {t_des}")
            else:
                adaptation["differences_requiring_adaptation"].append(
                    f"Design divergence: Precedent used '{c_des}', but target specifies '{t_des}'."
                )

        return adaptation


def main():
    parser = argparse.ArgumentParser(description="Digital Saber Case Memory Engine (CBR)")
    parser.add_argument("--query", "-q", type=str, help="Search query or research problem")
    parser.add_argument("--top-k", "-k", type=int, default=3, help="Number of precedents to retrieve")
    parser.add_argument("--design", type=str, help="Filter by research design (e.g. ancova, rct, sem, mediation)")
    parser.add_argument("--list-all", action="store_true", help="List all indexed cases")
    parser.add_argument("--case-id", type=str, help="Inspect specific case by ID")

    args = parser.parse_args()
    engine = CaseMemoryEngine()

    if args.list_all:
        print(f"\nIndexed Historical Cases ({engine.count()} total):")
        print("=" * 70)
        for c in engine.cases:
            print(f"• [{c.get('case_id')}] {c.get('topic')}")
            print(f"  Design: {c.get('design')} | N = {c.get('sample_size')} | Analysis: {c.get('statistical_analysis')}")
        print("=" * 70)
        return

    if args.case_id:
        match = next((c for c in engine.cases if c.get("case_id") == args.case_id), None)
        if match:
            print(json.dumps(match, ensure_ascii=False, indent=2))
        else:
            print(f"Error: Case '{args.case_id}' not found.", file=sys.stderr)
            sys.exit(1)
        return

    if args.query:
        results = engine.search_precedents(args.query, top_k=args.top_k, filter_design=args.design)
        print(f"\nTop Precedents for Query: '{args.query}'")
        print("=" * 70)
        for idx, res in enumerate(results, 1):
            c = res["case"]
            score = res["similarity_score"]
            print(f"{idx}. [{c.get('case_id')}] Similarity: {score:.3f}")
            print(f"   Topic: {c.get('topic')}")
            print(f"   Design: {c.get('design')} (N = {c.get('sample_size')})")
            print(f"   Analysis: {c.get('statistical_analysis')}")
            print(f"   Key Decisions: {', '.join(c.get('decisions_made', [])[:2])}")
            print("-" * 70)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
