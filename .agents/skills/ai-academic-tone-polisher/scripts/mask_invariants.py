#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entity Invariant Masking & Unmasking Engine
Part of Skill #22: ai-academic-tone-polisher
AcademicSuite — Digital Saber Cognitive Architecture

Guarantees 100% preservation of APA 7th Edition in-text citations,
statistical formulas, degrees of freedom, and mathematical symbols
during structural and cadence rewriting passes (Rules 2, 3, and 5).
"""

import re
from typing import Dict, Tuple, List


# Regex for APA 7 statistical expressions (English and Persian equivalents)
STAT_PATTERNS = [
    # Complex SEM model fit chains: χ²(52) = 57.762, p = .271; CFI = .995; RMSEA = .019
    r"[χxX]²\s*\(\s*\d+\s*(?:,\s*N\s*=\s*\d+)?\s*\)\s*=\s*[\d.]+\s*,\s*p\s*[<>=]\s*[\d.]+",
    r"[χxX]²\/df\s*=\s*[\d.]+",
    # F-tests: F(1, 58) = 14.25, p < .001, η_p² = .197 or F(1, 27) = 18.42
    r"[Ff]\s*\(\s*\d+\s*,\s*\d+\s*\)\s*=\s*[\d.]+\s*(?:,\s*p\s*[<>=]\s*[\d.]+)?(?:\s*,\s*(?:[η\\]?eta_p\^?2|η_p²|d|R²|R\^2)\s*=\s*[\d.]+)?",
    # t-tests: t(58) = 3.42, p = .001, d = 0.88
    r"[Tt]\s*\(\s*\d+\s*\)\s*=\s*-?[\d.]+\s*(?:,\s*p\s*[<>=]\s*[\d.]+)?(?:\s*,\s*d\s*=\s*[\d.]+)?",
    # Z-scores: z = 4.512, p < .001
    r"\bz\s*=\s*-?[\d.]+\s*(?:,\s*p\s*[<>=]\s*[\d.]+)?",
    # Path coefficients / Betas: β = -.544, p < .001 or B = -0.151, SE = 0.023
    r"(?:β|β_indirect|β_total|B)\s*=\s*-?[\d.]+\s*(?:,\s*SE\s*=\s*[\d.]+)?(?:\s*,\s*z\s*=\s*-?[\d.]+)?(?:\s*,\s*p\s*[<>=]\s*[\d.]+)?",
    # Pearson r / Correlations: r = -.513, p < .001
    r"\br\s*=\s*-?[\d.]+\s*(?:,\s*p\s*[<>=]\s*[\d.]+)?",
    # Descriptives: M = 24.50, SD = 4.12
    r"\bM\s*=\s*[\d.]+\s*,\s*SD\s*=\s*[\d.]+",
    # Standalone p-values: p < .001 or p = .024 or ۰/۰۰۱ > p
    r"\bp\s*[<>=]\s*\.?\d+",
    r"[۰-۹]+/[۰-۹]+\s*[><=]\s*p",
    # Fit indices: CFI = .995, TLI = .994, RMSEA = .019, SRMR = .032
    r"\b(?:CFI|TLI|RMSEA|SRMR|GFI|AGFI)\s*=\s*[\d.]+(?:\s*\([^)]+\))?",
    # Factor loadings: λ = .599, z = fixed or λ = -.663, z = -8.744
    r"(?:λ|lambda)\s*=\s*-?[\d.]+(?:\s*,\s*z\s*=\s*[^,)]+)?",
    # Confidence intervals: 95% CI [-0.197, -0.105] or 90% CI [.000, .042]
    r"(?:90%|95%|99%)\s*CI\s*\[\s*-?[\d.]+\s*,\s*-?[\d.]+\s*\]",
]

# Regex for APA 7 in-text citations
# Regex for APA 7 in-text citations
CITATION_PATTERNS = [
    # Standard English Parenthetical: (Beck et al., 2020), (Costa & McCrae, 1992; Kline, 2015), (Neff, 2003a, 2003b)
    r"\((?:(?:[A-Z][A-Za-z\-]+(?:\s*,\s*[A-Z][A-Za-z\-]+)*(?:\s*(?:&|and|, and)\s*[A-Z][A-Za-z\-]+|\s+et\s+al\.)?,\s*\d{4}[a-z]?(?:,\s*\d{4}[a-z]?)?(?:,\s*p\.\s*\d+)?)(?:\s*;\s*(?:[A-Z][A-Za-z\-]+(?:\s*,\s*[A-Z][A-Za-z\-]+)*(?:\s*(?:&|and|, and)\s*[A-Z][A-Za-z\-]+|\s+et\s+al\.)?,\s*\d{4}[a-z]?(?:,\s*\d{4}[a-z]?)?(?:,\s*p\.\s*\d+)?))*)\)",
    
    # English Narrative Citations: Costa and McCrae (1992), Neff (2003a, 2003b), Raes et al. (2011)
    r"\b[A-Z][A-Za-z\-]+(?:\s+(?:and|&)\s+[A-Z][A-Za-z\-]+|\s+et\s+al\.)?\s*\(\d{4}[a-z]?(?:,\s*\d{4}[a-z]?)?(?:,\s*p\.\s*\d+)?\)",
    
    # Persian Parenthetical Citations: (بک و همکاران، ۱۳۹۹)، (کاستا و مک‌کری، ۱۹۹۲)، (روشندل، ۱۴۰۰)
    r"\((?:[\u0600-\u06FF\s‌]+(?:\s+و\s+همکاران|\s+و\s+[\u0600-\u06FF\s‌]+)?،\s*[۰-۹]{4}[الف-ی]?(?:\s*;\s*[\u0600-\u06FF\s‌]+(?:\s+و\s+همکاران|\s+و\s+[\u0600-\u06FF\s‌]+)?،\s*[۰-۹]{4}[الف-ی]?)*)\)",
    
    # Persian Narrative Citations: بک و همکاران (۱۳۹۹)، کاستا و مک‌کری (۱۹۹۲)
    r"[\u0600-\u06FF\s‌]+(?:\s+و\s+همکاران|\s+و\s+[\u0600-\u06FF\s‌]+)?\s*\([۰-۹]{4}[الف-ی]?(?:,\s*[۰-۹]{4}[الف-ی]?)?\)",
]


def mask_invariants(text: str) -> Tuple[str, Dict[str, str]]:
    """
    Replaces all citations and statistical formulas with unique collision-proof tokens.
    Returns:
        masked_text: Text with tokens like __STAT_001__, __CIT_001__
        mask_dict: Dictionary mapping token -> original string
    """
    mask_dict: Dict[str, str] = {}
    masked_text = text

    stat_counter = 0
    cit_counter = 0

    # 1. Mask statistical patterns first (to avoid numbers inside stats being partially caught)
    for pat in STAT_PATTERNS:
        matches = list(re.finditer(pat, masked_text))
        # Process in reverse order to preserve string offsets
        for m in reversed(matches):
            orig_str = m.group(0)
            # Avoid re-masking tokens
            if orig_str.startswith("__"):
                continue
            stat_counter += 1
            token = f"__STAT_{stat_counter:03d}__"
            mask_dict[token] = orig_str
            start, end = m.span()
            masked_text = masked_text[:start] + token + masked_text[end:]

    # 2. Mask citations
    for pat in CITATION_PATTERNS:
        matches = list(re.finditer(pat, masked_text))
        for m in reversed(matches):
            orig_str = m.group(0)
            if orig_str.startswith("__"):
                continue
            cit_counter += 1
            token = f"__CIT_{cit_counter:03d}__"
            mask_dict[token] = orig_str
            start, end = m.span()
            masked_text = masked_text[:start] + token + masked_text[end:]

    return masked_text, mask_dict


def unmask_invariants(masked_text: str, mask_dict: Dict[str, str]) -> str:
    """
    Restores original citations and statistics from the mask dictionary.
    Replaces tokens in reverse-sorted key order to prevent partial token overlaps.
    """
    unmasked = masked_text
    # Sort keys by length descending to prevent __CIT_001__ being partially matched by __CIT_00__
    sorted_tokens = sorted(mask_dict.keys(), key=len, reverse=True)
    for token in sorted_tokens:
        orig = mask_dict[token]
        unmasked = unmasked.replace(token, orig)
    return unmasked


def audit_masking_fidelity(original_text: str, unmasked_text: str, mask_dict: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    Verifies that 100% of masked entities exist intact in the unmasked text.
    Returns:
        (is_perfect, list_of_missing_entities)
    """
    missing = []
    for token, orig in mask_dict.items():
        if orig not in unmasked_text:
            missing.append(f"Missing [{token}]: {orig}")
    return len(missing) == 0, missing


class InvariantMasker:
    """Class interface for masking and unmasking invariants."""
    def mask(self, text: str) -> Tuple[str, Dict[str, str]]:
        return mask_invariants(text)

    def unmask(self, masked_text: str, mask_dict: Dict[str, str]) -> str:
        return unmask_invariants(masked_text, mask_dict)

    def audit_fidelity(self, original_text: str, unmasked_text: str, mask_dict: Dict[str, str]) -> Tuple[bool, List[str]]:
        return audit_masking_fidelity(original_text, unmasked_text, mask_dict)



if __name__ == "__main__":
    sample = (
        "Pain is rarely just physical (Treede et al., 2015; McCarthy et al., 2023). "
        "According to Costa and McCrae (1992), neuroticism strongly predicted higher pain severity "
        "(β = -.544, p < .001). Model fit was robust: χ²(52) = 57.762, p = .271; CFI = .995; "
        "RMSEA = .019 (90% CI [.000, .042]). In Persian: بک و همکاران (۱۳۹۹) دریافتند که ۰/۰۰۱ > p."
    )
    print("--- Original ---")
    print(sample)
    
    masked, m_dict = mask_invariants(sample)
    print("\n--- Masked Text ---")
    print(masked)
    print(f"\nMasked {len(m_dict)} entities: {list(m_dict.keys())}")
    
    unmasked = unmask_invariants(masked, m_dict)
    print("\n--- Unmasked Text ---")
    print(unmasked)
    
    ok, errs = audit_masking_fidelity(sample, unmasked, m_dict)
    print(f"\nAudit Fidelity Perfect? {ok}")
