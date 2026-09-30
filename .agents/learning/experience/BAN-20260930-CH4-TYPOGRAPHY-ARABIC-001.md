# Causal Root-Cause Analysis: BAN-20260930-CH4-TYPOGRAPHY-ARABIC-001

## 1. Observable Defect Diagnosis
**Failure Signatures:** `OPENXML_ARABIC_FALLBACK`, `UNTRANSLITERATED_INLINE_LATIN`, `FORBIDDEN_AI_CLICHE`, `REPORTING_OR_TYPOGRAPHY_DEFECT`

### A. OpenXML Arabic Fallback
The `compile_full_chapter4_from_md.py` script fails to adhere to the strict OpenXML font binding specification for Persian text. Specifically, in `add_bidi_run`, it injects:
`<w:rFonts w:ascii="B Nazanin" w:hAnsi="B Nazanin" w:cs="B Nazanin"/>`
It systematically omits `w:eastAsia` and `w:hint="cs"`. Without `w:hint="cs"`, Microsoft Word defaults to Arabic Naskh fallback fonts for complex scripts instead of rendering genuine Persian typography.

### B. Un-transliterated Inline Latin
Acronyms like `(IUS-12)` and `(SCI-16)` are present in `Chapter_4_Results.md` but are swept into `B Nazanin` by the compiler instead of being explicitly tokenized and rendered in `Times New Roman`.

### C. AI Clichés
The markdown draft contains classic generative AI clichés and filler transitions (e.g., "در این راستا", "شایان ذکر است", "درک مکانیسم‌های...") which violate the formal academic register.

### D. Numeral Inconsistencies
Despite the strict Persian Numeral rule, the text and tables exhibit a mixture of Persian decimal typography (`۰.۰۰۱`) and raw Latin floats (`18.0`, `60.0`, `9.79` in Table 4-6).

## 2. Prescribed Counterfactual Behavior
1. **Compiler Refactoring**: Update `compile_full_chapter4_from_md.py` to correctly format `w:rFonts`:
   `<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:cs="{font}" w:eastAsia="{font}" w:hint="cs"/>`
2. **Regex Font Isolation**: Implement a regex pass in the compiler that detects inline Latin text `[A-Za-z0-9\-\.]+` and explicitly binds it to `Times New Roman`.
3. **Drafting Constraints**: Enforce strict anti-cliché prompts during the generation of the Markdown to block robotic filler phrases.
4. **Numeral Normalization**: Apply a strict Persian digit conversion function across the entire Markdown output before compilation, ensuring numbers like `18.0` become `۱۸.۰`.
