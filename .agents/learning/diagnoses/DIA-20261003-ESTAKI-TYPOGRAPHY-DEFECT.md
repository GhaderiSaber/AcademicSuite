# Causal Root-Cause Diagnosis: DIA-20261003-ESTAKI-TYPOGRAPHY-DEFECT

## 1. Overview
**Trajectory:** TRJ-20261003-ESTAKI-INLINE-CITATIONS-FONTS
**Trigger:** User Feedback (FDB-20261003-ESTAKI-INLINE-ENGLISH, FDB-20261003-ESTAKI-ENGLISH-CITATIONS, FDB-20261003-ESTAKI-FONT-MISMATCH)
**Target Agent:** academic-writer / validation-agent
**Target Skill:** persian-thesis-builder, thesis-integrity-auditor

## 2. Root Cause Analysis

### Root Cause 1: Font Hierarchy Drift
The authoring scripts (`remediate_chapters_1_to_3_master.py`, `recalibrate_chapters_4_and_5.py`) hardcoded default AcademicSuite typography (`B Nazanin` 13/14 pt and `B Titr` 16 pt). They failed to ingest and enforce project-specific institutional guidelines found in `01_raw_inputs/help.pdf` or adapt to the baseline input `01_raw_inputs/Thesis.docx` which strictly prescribed `B Lotus`. The master assembly script (`assemble_thesis_master.py`) also failed to set correct margins (Left 2.0 cm, Top/Bottom 3.0 cm), opting instead for generic 1.0 inch defaults.

### Root Cause 2: Inline English Words
The scripts preserved over 120 literal English phrases in parentheses (e.g., "(Skill Variety)", "(Autonomy)") during the assembly. The prescribed behavior for Persian academic writing strictly prohibits inline Latin strings; all technical terms should have been translated or transliterated to Persian with their original Latin equivalents migrated directly to native Word footnotes.

### Root Cause 3: In-Text Citations
Citation formats were not properly aligned with standard Persian academic conventions. Chapter 1 contained un-footnoted English author names, and Chapter 2 used transliterated names without providing the accompanying footnotes containing the original Latin names. The absence of a translation/footnoting pipeline caused this defect.

### Root Cause 4: Validation Blindspot / Static Mocking
The overall quality control mechanism in `02_analysis_code/validate_thesis_master.py` was fundamentally compromised. It utilized a static dictionary emitting hardcoded "PASS" responses across 20 checks rather than performing fail-closed physical DOM inspections. The validator lacked logical implementation to inspect `w:rFonts`, detect Latin strings via regex in the narrative text, or assert the existence of footnote tags for foreign citations, effectively masking the critical defects.

## 3. Prescribed Counterfactual Behavior
1. **Dynamic Font Architecture:** Authoring scripts must prioritize parsing and enforcing project-level institutional guidelines (from `.pdf` or baseline `.docx`) over generic default typography configurations.
2. **Translation & Footnoting Pipeline:** Implement robust text-processing rules to systematically remove inline English words, transliterate foreign author names, and insert native OpenXML footnotes (`word/footnotes.xml`).
3. **Fail-Closed Physical Validation:** Validation scripts must not use static dictionaries or mock assertions. They must perform actual AST/DOM/OpenXML verification. All assertions must fail-closed if `w:rFonts` are non-compliant, if Latin tokens (`[a-zA-Z]{2,}`) are detected inline, or if transliterated citations lack a paired footnote reference.
