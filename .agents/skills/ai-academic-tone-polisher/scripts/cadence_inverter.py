#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cadence & Burstiness Inverter Tool
Part of Skill #22: ai-academic-tone-polisher
AcademicSuite — Digital Saber Cognitive Architecture

Analyzes paragraph-level sentence cadence, identifies synthetic
length clustering (homogeneous 18-24 word sentences), and provides
targeted recommendations for periodic fusion (em-dashes, semicolons)
and staccato assertions to drive CV >= 0.70.
"""

import re
import numpy as np
from typing import Dict, List, Tuple, Any


def split_sentences(text: str) -> List[str]:
    """Splits paragraph text into sentences."""
    cleaned = re.sub(r'\s+', ' ', text).strip()
    raw_sents = re.split(r'(?<=[.!?؟])\s+', cleaned)
    return [s.strip() for s in raw_sents if len(s.strip()) > 3]


def diagnose_paragraph_cadence(para_text: str, para_index: int = 1) -> Dict[str, Any]:
    """Evaluates the sentence rhythm and identifies monotony clusters in a paragraph."""
    sents = split_sentences(para_text)
    if not sents:
        return {"index": para_index, "sentences": 0, "cv": 0.0, "status": "EMPTY"}

    lens = [len(s.split()) for s in sents]
    mean_l = float(np.mean(lens))
    std_l = float(np.std(lens))
    cv = std_l / mean_l if mean_l > 0 else 0.0

    # Identify monotone clusters (consecutive sentences with lengths between 16 and 26 words)
    monotone_clusters = []
    current_cluster = []
    for i, l in enumerate(lens):
        if 16 <= l <= 26:
            current_cluster.append((i, l))
        else:
            if len(current_cluster) >= 3:
                monotone_clusters.append(current_cluster)
            current_cluster = []
    if len(current_cluster) >= 3:
        monotone_clusters.append(current_cluster)

    # Status grading
    if cv >= 0.70:
        status = "EXCELLENT (Human Scholarly Cadence)"
    elif cv >= 0.55:
        status = "ACCEPTABLE (Moderate Cadence)"
    elif cv >= 0.40:
        status = "UNIFORM (Typical AI Cadence)"
    else:
        status = "CRITICAL_HOMOGENEITY (High AI Detector Flag)"

    recommendations = []
    if cv < 0.65:
        recommendations.append("Fuse two consecutive mid-length sentences using an em-dash (—), semicolon (;), or participial clause to create an analytical periodic sentence (> 35 words).")
        recommendations.append("Introduce a short, assertive thesis statement (5-8 words) at the beginning or pivot of the paragraph.")

    return {
        "index": para_index,
        "sentences": len(sents),
        "lengths": lens,
        "mean_len": round(mean_l, 1),
        "std_len": round(std_l, 1),
        "cv": round(cv, 3),
        "status": status,
        "monotone_clusters": len(monotone_clusters),
        "recommendations": recommendations,
        "sentence_preview": [f"S{idx+1} ({l}w): {sents[idx][:60]}..." for idx, l in enumerate(lens)]
    }


def simulate_cadence_after_edit(simulated_lengths: List[int]) -> Dict[str, Any]:
    """Calculates projected burstiness metrics given a proposed set of sentence lengths."""
    mean_l = float(np.mean(simulated_lengths))
    std_l = float(np.std(simulated_lengths))
    cv = std_l / mean_l if mean_l > 0 else 0.0
    return {
        "count": len(simulated_lengths),
        "lengths": simulated_lengths,
        "mean_len": round(mean_l, 1),
        "std_len": round(std_l, 1),
        "cv": round(cv, 3),
        "meets_target": cv >= 0.70,
        "rating": "HUMAN_NATURAL" if cv >= 0.70 else "NEEDS_MORE_VARIATION"
    }


class CadenceInverter:
    """Class interface for paragraph cadence diagnosis and burstiness optimization."""
    def analyze_paragraph(self, text: str, index: int = 1) -> Dict[str, Any]:
        diag = diagnose_paragraph_cadence(text, index)
        diag["sentence_count"] = diag.get("sentences", 0)
        return diag

    def simulate_edit(self, proposed_lengths: List[int]) -> Dict[str, Any]:
        return simulate_cadence_after_edit(proposed_lengths)


if __name__ == "__main__":
    # Test on a classic AI paragraph
    sample_para = (
        "Why do two students with similar physiological complaints experience vastly different levels of suffering? "
        "Modern biopsychosocial models emphasize that pain severity is not a direct readout of peripheral tissue damage. "
        "Rather, it is continuously shaped by cognitive appraisals, affective states, and enduring personality traits. "
        "The Five-Factor Model offers a valuable lens for understanding these individual differences. "
        "Among the Big Five dimensions, neuroticism consistently emerges as the strongest psychological risk factor for chronic pain."
    )
    diag = diagnose_paragraph_cadence(sample_para, 1)
    print("=== Paragraph Diagnosis ===")
    print(f"Sentences: {diag['sentences']} | Mean: {diag['mean_len']} | Std: {diag['std_len']} | CV: {diag['cv']}")
    print(f"Status: {diag['status']}")
    print(f"Monotone Clusters: {diag['monotone_clusters']}")
    for r in diag['recommendations']:
        print(f" • Rec: {r}")

    # Simulate proposed human cadence: [7, 42, 14, 48, 8]
    sim = simulate_cadence_after_edit([7, 42, 14, 48, 8])
    print("\n=== Simulated Human Cadence ===")
    print(f"Lengths: {sim['lengths']} | Mean: {sim['mean_len']} | CV: {sim['cv']} | Target Met: {sim['meets_target']}")
