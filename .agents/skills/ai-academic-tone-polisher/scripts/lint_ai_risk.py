#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deterministic AI Risk & Academic Cadence Linter
Part of Skill #22: ai-academic-tone-polisher
AcademicSuite — Digital Saber Cognitive Architecture

Performs comprehensive diagnostic scanning of manuscripts for:
  1. Sentence Burstiness Coefficient of Variation (CV = σ / μ)
  2. Transition-Marker Density
  3. Conversational Rhetorical Question Openers
  4. Formulaic Ordinal Enumerations (First, Second, Third, Finally)
  5. Section-Level Repetitive Templates (Measures & Discussion Limitations)
  6. 38 English & Persian AI Cliches & Translationese Markers
"""

import os
import sys
import re
import json
import argparse
from typing import Dict, List, Tuple, Any
import numpy as np


# ------------------------------------------------------------------------------
# 1. AI MARKER CATALOGS (ENGLISH & PERSIAN)
# ------------------------------------------------------------------------------

AI_CLICHES_EN = [
    # Top dead giveaway tropes
    (r"\bplays?\s+a\s+(?:crucial|pivotal|vital|key|central)\s+role\b", "Translationese Cliche: plays a crucial role", "MAJOR"),
    (r"\bdelv(?:e|es|ing|ed)\s+into\b", "ChatGPT Signature: delve into", "CRITICAL"),
    (r"\b(?:serves?|stands?)\s+as\s+a\s+testament\s+to\b", "Hyperbolic AI Trope: testament to", "CRITICAL"),
    (r"\bmultifaceted\s+(?:tapestry|landscape|nature|dimensions?)\b", "Flowery LLM Metaphor: multifaceted tapestry", "CRITICAL"),
    (r"\bsheds?\s+light\s+on\b", "Conversational AI Metaphor: sheds light on", "MAJOR"),
    (r"\bpaves?\s+the\s+way\s+for\b", "Conversational AI Metaphor: paves the way", "MAJOR"),
    (r"\bfosters?\s+a\s+deeper\s+understanding\b", "Formulaic Transition: fosters deeper understanding", "MAJOR"),
    (r"\bintricate\s+(?:dance|web|dynamics?|nature)\b", "Flowery LLM Metaphor: intricate dance/web", "CRITICAL"),
    (r"\bseamlessly\s+(?:integrat(?:e|es|ed|ing)|blend(?:s|ed|ing))\b", "AI Adverb Cliché: seamlessly", "MAJOR"),
    (r"\bgarnered\s+(?:significant|considerable|widespread)\s+attention\b", "Passive Cliché: garnered attention", "MAJOR"),
    (r"\bcompelling\s+evidence\b", "Dramatic AI Trope: compelling evidence", "MINOR"),
    (r"\bit\s+is\s+(?:important|crucial|worth\s+noting|essential)\s+to\s+(?:note|remember|highlight)\s+that\b", "Didactic Throat-Clearing", "MAJOR"),
    (r"\bnotably[,\s]+", "Overused AI Transition: notably", "MINOR"),
    (r"\bmoreover[,\s]+", "Overused AI Transition: moreover", "MINOR"),
    (r"\bfurthermore[,\s]+", "Overused AI Transition: furthermore", "MINOR"),
    (r"\bin\s+this\s+regard[,\s]+", "Mechanical Transition: in this regard", "MAJOR"),
    (r"\bin\s+essence[,\s]+", "Formulaic Wrap-Up: in essence", "MAJOR"),
    (r"\b(?:in\s+conclusion|to\s+sum\s+up)[,\s]+", "High-School Transition: in conclusion", "MAJOR"),
    (r"\bacts?\s+as\s+an\s+effective\s+factor\b", "Translationese Calque: acts as an effective factor", "MAJOR"),
    (r"\bquiet,\s+daily\s+(?:crisis|struggle)\b", "Formulaic Essay Hook: quiet daily struggle", "MAJOR"),
    (r"\bvital\s+psychological\s+shock\s+absorber\b", "Overused Metaphor: psychological shock absorber", "MAJOR"),
    (r"\bcollides?\s+directly\s+with\b", "Dramatic AI Calque: collides directly with", "MINOR"),
]

AI_CLICHES_FA = [
    (r"شایان\s+ذکر\s+است\s+که", "حشو کلیشه‌ای هوش مصنوعی: شایان ذکر است که", "CRITICAL"),
    (r"در\s+این\s+راستا[،,]?", "پیوند مکانیکی: در این راستا", "MAJOR"),
    (r"به\s+طور\s+کلی\s+می‌?توان\s+گفت\s+که", "تعمیم مبهم و غیرقاطع: به طور کلی می‌توان گفت", "MAJOR"),
    (r"این\s+امر\s+نشان‌?دهنده\s+آن\s+است\s+که", "گرته‌برداری نامناسب: این امر نشان‌دهنده آن است که", "MAJOR"),
    (r"همان‌?طور\s+که\s+می‌?دانیم[،,]?", "عبارت عامیانه و فاقد استناد: همان‌طور که می‌دانیم", "CRITICAL"),
    (r"نقش\s+بسیار\s+مهمی\s+ایفا\s+می‌?کند", "گرته‌برداری انگلیسی: نقش بسیار مهمی ایفا می‌کند", "MAJOR"),
    (r"لازم\s+به\s+یادآوری\s+است\s+که", "حشو تعلیمی: لازم به یادآوری است", "MAJOR"),
    (r"از\s+این\s+رو[،,]?", "توالی زنجیره‌ای علت و معلولی", "MINOR"),
    (r"بدین\s+ترتیب[،,]?", "توالی زنجیره‌ای ساده", "MINOR"),
    (r"به\s+عنوان\s+یک\s+عامل\s+موثر\s+عمل\s+می‌?کند", "ترجمه تحت‌اللفظی acts as effective factor", "MAJOR"),
    (r"پژوهشگران\s+به\s+این\s+نتیجه\s+رسیدند\s+که", "گزارشگری عامیانه شواهد", "MAJOR"),
    (r"تاثیرات\s+مثبت\s+زیادی\s+بر", "فرمول‌بندی کیفی مبهم", "MAJOR"),
    (r"همسو\s+و\s+منطبق\s+می‌?باشد", "حشو قبیح و خطای فعل می‌باشد", "MAJOR"),
    (r"کمک\s+می‌?کند\s+تا", "فعل عامیانه به جای واژگان روان‌شناختی", "MINOR"),
    (r"در\s+جهان\s+پرشتاب\s+امروز", "مقدمه کلیشه‌ای و ژورنالیستی", "CRITICAL"),
]

# Structural Trigger Patterns
RHETORICAL_QUESTION_PATTERN = r"(?i)(?:^|[.!?]\s+)(?:why|how|what)\s+(?:do|does|can|explains?|leads?|is|are)\b[^.?!]{10,120}\?"
ORDINAL_ENUMERATION_PATTERN = r"(?i)\b(?:first|second|third|fourth|finally)[,\s]+.*?\b(?:second|third|fourth|finally)[,\s]+"
FOUR_POINT_LIMITATIONS_KEYWORDS = ["cross-sectional", "self-report", "convenience", "generaliz"]


# ------------------------------------------------------------------------------
# 2. LINTER CORE ENGINE
# ------------------------------------------------------------------------------

class AIRiskLinter:
    """Evaluates text burstiness, structural regularity, and AI marker footprint."""

    def __init__(self, lang: str = "en"):
        self.lang = lang.lower()

    def split_sentences(self, text: str) -> List[str]:
        """Splits text into valid sentences, preserving punctuation boundaries."""
        # Clean extra whitespace
        cleaned = re.sub(r'\s+', ' ', text).strip()
        # Split on sentence ending punctuation followed by space or quote
        raw_sents = re.split(r'(?<=[.!?؟])\s+', cleaned)
        valid = [s.strip() for s in raw_sents if len(s.strip()) > 3]
        return valid

    def analyze_cadence(self, sentences: List[str]) -> Dict[str, Any]:
        """Calculates mean, std, CV, and sentence length distribution."""
        if not sentences:
            return {"count": 0, "mean_len": 0.0, "std_len": 0.0, "cv": 0.0, "distribution": []}

        lengths = [len(s.split()) for s in sentences]
        mean_l = float(np.mean(lengths))
        std_l = float(np.std(lengths))
        cv = std_l / mean_l if mean_l > 0 else 0.0

        return {
            "count": len(sentences),
            "mean_len": round(mean_l, 2),
            "std_len": round(std_l, 2),
            "cv": round(cv, 3),
            "lengths": lengths,
            "min_len": min(lengths),
            "max_len": max(lengths),
        }

    def scan_cliches(self, text: str) -> List[Dict[str, Any]]:
        """Finds all cataloged AI clichés in text."""
        findings = []
        catalogs = []
        if self.lang in ("en", "auto"):
            catalogs.extend(AI_CLICHES_EN)
        if self.lang in ("fa", "auto"):
            catalogs.extend(AI_CLICHES_FA)

        for pat, desc, severity in catalogs:
            matches = list(re.finditer(pat, text, re.IGNORECASE))
            for m in matches:
                findings.append({
                    "matched_text": m.group(0),
                    "description": desc,
                    "severity": severity,
                    "start": m.start(),
                    "end": m.end()
                })
        return findings

    def scan_structural_triggers(self, text: str, sentences: List[str]) -> List[Dict[str, Any]]:
        """Detects rhetorical questions, ordinal lists, and limitation templates."""
        triggers = []

        # 1. Rhetorical Question Openers
        rq_matches = list(re.finditer(RHETORICAL_QUESTION_PATTERN, text))
        for m in rq_matches:
            triggers.append({
                "type": "RHETORICAL_QUESTION",
                "severity": "CRITICAL",
                "matched_text": m.group(0).strip(),
                "rationale": "Conversational rhetorical question used as paragraph transition; dead giveaway of conversational LLMs."
            })

        # 2. Formulaic Ordinal Enumeration
        ordinal_matches = list(re.finditer(ORDINAL_ENUMERATION_PATTERN, text))
        for m in ordinal_matches:
            triggers.append({
                "type": "ORDINAL_ENUMERATION",
                "severity": "MAJOR",
                "matched_text": m.group(0)[:80] + "...",
                "rationale": "Mechanical enumeration (First, Second, Third, Finally); creates predictable transformer attention weights."
            })

        # 3. Four-point limitations cluster check (evaluated within individual paragraphs)
        paragraphs = [p for p in text.split("\n\n") if len(p.strip()) > 30] or [text]
        for p in paragraphs:
            p_lower = p.lower()
            matched_limits = [k for k in FOUR_POINT_LIMITATIONS_KEYWORDS if k in p_lower]
            if len(matched_limits) >= 3:
                triggers.append({
                    "type": "LIMITATIONS_TEMPLATE",
                    "severity": "MAJOR",
                    "matched_text": f"Found limitation cluster: {matched_limits}",
                    "rationale": "Standard 4-point limitation template (cross-sectional -> self-report -> convenience sample); heavily trained in AI discriminators."
                })
                break

        return triggers

    def calculate_transition_density(self, sentences: List[str]) -> float:
        """Calculates percentage of sentences starting with generic connective signposts."""
        if not sentences:
            return 0.0
        pattern = r"^(?:moreover|furthermore|additionally|in\s+addition|consequently|notably|specifically|in\s+contrast|on\s+the\s+other\s+hand|however|subsequently|در\s+این\s+راستا|از\s+این\s+رو|علاوه\s+بر\s+این)[,\s]"
        count = 0
        for s in sentences:
            if re.search(pattern, s.strip(), re.IGNORECASE):
                count += 1
        return round(count / len(sentences), 3)

    def evaluate(self, text: str) -> Dict[str, Any]:
        """Runs the complete multi-signal diagnostic audit."""
        sentences = self.split_sentences(text)
        cadence = self.analyze_cadence(sentences)
        cliches = self.scan_cliches(text)
        structural = self.scan_structural_triggers(text, sentences)
        trans_density = self.calculate_transition_density(sentences)

        # Compute Composite AI Footprint Score (0 - 100%)
        # 1. Cadence Penalty: Target CV >= 0.65
        cv = cadence.get("cv", 0.0)
        if cv >= 0.65:
            cadence_penalty = 0.0
        elif cv >= 0.50:
            cadence_penalty = (0.65 - cv) * 60.0  # up to 9 pts
        elif cv >= 0.35:
            cadence_penalty = 10.0 + (0.50 - cv) * 120.0  # up to 28 pts
        else:
            cadence_penalty = 35.0  # severely robotic

        # 2. Transition Density Penalty: Target <= 12%
        if trans_density <= 0.12:
            trans_penalty = 0.0
        else:
            trans_penalty = min(20.0, (trans_density - 0.12) * 100.0)

        # 3. Structural Trigger Penalties
        struct_penalty = 0.0
        for st in structural:
            if st["severity"] == "CRITICAL":
                struct_penalty += 15.0
            elif st["severity"] == "MAJOR":
                struct_penalty += 8.0

        # 4. Cliché Penalties
        cliche_penalty = 0.0
        for c in cliches:
            if c["severity"] == "CRITICAL":
                cliche_penalty += 10.0
            elif c["severity"] == "MAJOR":
                cliche_penalty += 5.0
            else:
                cliche_penalty += 2.0

        composite_risk = min(100.0, cadence_penalty + trans_penalty + struct_penalty + cliche_penalty)
        composite_risk = round(composite_risk, 1)

        # Editorial Grade
        if composite_risk <= 15.0:
            grade = "A+ (Human Natural / Clear)"
            verdict = "PASSED"
        elif composite_risk <= 30.0:
            grade = "A (Low Risk / Acceptable)"
            verdict = "PASSED_WITH_NOTE"
        elif composite_risk <= 55.0:
            grade = "B (Moderate Risk / AI Polished Footprint)"
            verdict = "FLAG_FOR_REVIEW"
        else:
            grade = "C (Severe Risk / High QuillBot/Turnitin Vulnerability)"
            verdict = "REJECTED"

        return {
            "verdict": verdict,
            "grade": grade,
            "composite_risk_score": composite_risk,
            "cadence": cadence,
            "transition_density": trans_density,
            "cliche_count": len(cliches),
            "cliches": cliches,
            "structural_triggers": structural,
            "total_words": sum(cadence.get("lengths", [])),
            "sentence_count": cadence.get("count", 0),
        }


# ------------------------------------------------------------------------------
# 3. CLI AND INPUT HANDLING
# ------------------------------------------------------------------------------

def extract_text_from_file(filepath: str) -> str:
    """Extracts text content from .py, .txt, .md, or .json files."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    ext = os.path.splitext(filepath)[1].lower()
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # If it's a python script containing article dicts/lists, extract strings
    if ext == ".py":
        # Extract quoted strings of academic text
        string_matches = re.findall(r'["\']{1,3}(.*?)["\']{1,3}', content, re.DOTALL)
        academic_paras = [s.strip() for s in string_matches if len(s.split()) >= 15]
        return "\n\n".join(academic_paras)

    return content


def print_cli_report(res: Dict[str, Any]):
    """Prints a structured academic audit report to stdout."""
    print("=" * 80)
    print("🔬 ACADEMIC AI RISK & CADENCE LINTER REPORT (Skill #22)")
    print("=" * 80)
    print(f"VERDICT:               {res['verdict']}")
    print(f"EDITORIAL GRADE:       {res['grade']}")
    print(f"COMPOSITE RISK SCORE:  {res['composite_risk_score']}%  (Target: < 20%)")
    print("-" * 80)
    
    cad = res["cadence"]
    print("📊 CADENCE & BURSTINESS METRICS:")
    print(f" • Sentences:           {cad['count']}")
    print(f" • Total Words:         {res['total_words']}")
    print(f" • Mean Length (μ):     {cad['mean_len']} words")
    print(f" • Std Deviation (σ):   {cad['std_len']}")
    print(f" • Burstiness (CV):     {cad['cv']}  " + ("✅ (Human Natural)" if cad['cv'] >= 0.65 else "⚠️ (Low Burstiness — AI Risk)" if cad['cv'] < 0.50 else "🟡 (Moderate)"))
    print(f" • Transition Density:  {res['transition_density'] * 100:.1f}%  " + ("✅ (Natural)" if res['transition_density'] <= 0.12 else "⚠️ (High Connective Density)"))
    print("-" * 80)

    structs = res["structural_triggers"]
    print(f"🚨 STRUCTURAL TRIGGERS ({len(structs)} found):")
    if not structs:
        print(" • None detected. (Excellent structural variety)")
    else:
        for s in structs:
            print(f" • [{s['severity']}] {s['type']}: {s['matched_text'][:70]}...")
            print(f"   ↳ {s['rationale']}")
    print("-" * 80)

    cliches = res["cliches"]
    print(f"⚠️ AI CLICHES & SYNTHETIC TROPES ({len(cliches)} found):")
    if not cliches:
        print(" • None detected. (Clean academic vocabulary)")
    else:
        for c in cliches[:10]:
            print(f" • [{c['severity']}] \"{c['matched_text']}\" — {c['description']}")
        if len(cliches) > 10:
            print(f"   ... and {len(cliches) - 10} more markers.")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="AI Risk and Academic Cadence Linter")
    parser.add_argument("--text", type=str, help="Text string to evaluate")
    parser.add_argument("--file", type=str, help="Path to file to evaluate (.py, .txt, .md, .json)")
    parser.add_argument("--lang", type=str, default="auto", choices=["auto", "en", "fa"], help="Language mode")
    parser.add_argument("--out", type=str, help="Path to export output JSON report")
    args = parser.parse_args()

    if args.text:
        text = args.text
    elif args.file:
        text = extract_text_from_file(args.file)
    else:
        # Default test string
        text = (
            "Why do two young adults with comparable bodily discomfort experience vastly different degrees of suffering? "
            "Pain is rarely just physical. For college students, persistent bodily discomfort presents a quiet, daily struggle. "
            "Self-compassion plays a crucial role in mitigating this burden. "
            "Our investigation was guided by four specific hypotheses: First, neuroticism will predict higher pain. "
            "Second, self-compassion will predict lower pain. Third, conscientiousness will buffer distress. "
            "Finally, self-compassion will mediate the relationship."
        )

    linter = AIRiskLinter(lang=args.lang)
    results = linter.evaluate(text)
    print_cli_report(results)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n[+] Results successfully exported to: {args.out}")


if __name__ == "__main__":
    main()
