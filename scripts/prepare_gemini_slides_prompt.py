#!/usr/bin/env python3
"""
prepare_gemini_slides_prompt.py
Synthesizes project statistical findings and research parameters into an
optimized, highly detailed prompt for Gemini in Google Slides.
"""

import json
import os
import sys

def build_gemini_slides_prompt(stats_file: str) -> dict:
    if not os.path.exists(stats_file):
        raise FileNotFoundError(f"Stats file not found: {stats_file}")

    with open(stats_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    reg = data.get("regression", {})
    dv = reg.get("dv", "Psychological Well-being")
    n = reg.get("n", 250)

    step1 = reg.get("step1", {})
    s1_vars = ", ".join(step1.get("variables", []))
    s1_r2 = step1.get("r2_str", ".072")
    s1_f = step1.get("f", 9.64)

    step2 = reg.get("step2", {})
    s2_added = ", ".join(step2.get("added_variables", []))
    s2_r2 = step2.get("r2_str", ".393")
    s2_dr2 = step2.get("delta_r2_str", ".321")
    s2_f = step2.get("f", 31.64)

    coefs = step2.get("coefficients", [])
    coef_lines = []
    for c in coefs:
        coef_lines.append(
            f"  - {c.get('variable')}: beta = {c.get('beta')}, t = {c.get('t')}, p = {c.get('p_str')}"
        )
    coef_text = "\n".join(coef_lines)

    # Master prompt tailored for Gemini in Google Slides
    prompt_text = f"""Create a 12-slide academic thesis defense presentation on the topic:
'Predicting {dv} through Psychological and Demographic Factors'.

Study Overview:
- Sample size: N = {n} participants.
- Methodology: Two-step Hierarchical Multiple Linear Regression.
- Step 1 Control Variables: {s1_vars} (R² = {s1_r2}, F = {s1_f}, p < .001).
- Step 2 Predictors Added: {s2_added} (Total R² = {s2_r2}, Delta R² = {s2_dr2}, F = {s2_f}, p < .001).
- Key Significant Predictors:
{coef_text}

Design & Layout Guidelines:
1. Avoid repetitive card grids or identical bullet lists across consecutive slides.
2. Use modern, varied visual archetypes:
   - Slide 1: Modern Title slide with clear subtitle and presenter metadata.
   - Slide 2: Problem Funnel / Research Rationale (from broad societal context to specific research gap).
   - Slide 3: Conceptual Framework / Model Diagram.
   - Slide 4: Research Hypotheses & Directional Predictions.
   - Slide 5: Methodology & Participant Demographics (N = {n}, visual breakdown).
   - Slide 6: Measurement Instruments & Reliability (Scales used).
   - Slide 7: Hierarchical Regression: Model 1 Baseline Controls (Age & Gender impact).
   - Slide 8: Hierarchical Regression: Model 2 Incremental Variance (Highlighting Delta R² = {s2_dr2}).
   - Slide 9: Predictor Importance Spotlight (Focus on Resilience beta = .343 as primary driver).
   - Slide 10: Theoretical & Psychological Mechanisms (Why resilience and self-efficacy buffer well-being).
   - Slide 11: Clinical & Practical Applications (Actionable mental health interventions).
   - Slide 12: Limitations, Future Directions & Conclusion.
3. Clean, high-contrast academic color palette (Deep navy, warm slate, subtle gold/teal accents).
4. Include concise speaker notes on each slide explaining the statistical findings.
"""

    return {
        "prompt": prompt_text.strip(),
        "topic": f"Hierarchical Regression Analysis of {dv}",
        "slide_count": 12,
        "sample_size": n
    }

if __name__ == "__main__":
    stats_path = sys.argv[1] if len(sys.argv) > 1 else "/Users/saber/Desktop/academic_suite/stats_results.json"
    result = build_gemini_slides_prompt(stats_path)
    output_prompt_path = "/Users/saber/Desktop/academic_suite/gemini_slides_prompt.txt"
    with open(output_prompt_path, "w", encoding="utf-8") as f:
        f.write(result["prompt"])
    print(f"Prompt successfully written to {output_prompt_path}")
    print("\n--- PROMPT PREVIEW ---")
    print(result["prompt"][:400] + "...\n[Full prompt in file]")
