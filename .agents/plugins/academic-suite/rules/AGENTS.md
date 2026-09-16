# Academic Suite Consolidated Domain Rules

These domain rules are automatically loaded and applied across all conversations by the `academic-suite` plugin.

---

## 1. Radical Honesty & Pipeline Enforcement
- **Directive 0 (Binary Honesty Protocol)**: Whenever asked a compliance question ("Did you check X?", "Did you follow the rules?"), start with "Yes" or "No" as the very first word.
- **Directive 1 (Pre-Flight Gate)**: View skill specification (`view_file`) before running capabilities and emit the Pre-Flight Pipeline Declaration.
- **Directive 3 (Zero Skipping)**: Multi-stage pipelines must generate verified physical checkpoint artifacts on disk before proceeding to the next stage.
- **Directive 12.1 (Sole Orchestrator Mandate)**: Antigravity is the sole agent conductor. Python scripts are strictly deterministic tools ("The Hands").

---

## 2. File Naming Standards (Universal Mandate)
- **Directive 6 (English-Only Filenames)**: Every file, script, dataset, table, docx, pptx, or directory **MUST** be named strictly using English ASCII characters (`a-z`, `A-Z`, `0-9`, `_`, `-`, `.`). Zero Persian/non-ASCII filenames on disk.

---

## 3. Persian Academic Typography & Font Standards
- **Font Bindings**:
  - Persian Body Text: `B Nazanin` (13–14 pt Regular)
  - Persian Headings: `B Titr` (12–18 pt Bold)
  - Latin Characters, Numbers & Statistics: `Times New Roman`
- **Directionality (BiDi)**:
  - Enforce RTL via `<w:bidi w:val="1"/>` in paragraph properties `<w:pPr>`.
  - In tables, enforce `<w:tblPr><w:bidiVisual/></w:tblPr>`.
  - Numeric cells must be decoupled to LTR (`rtl="0"`) with Latin font (`Times New Roman`) so negative signs precede numbers ($-0.32$).
- **Zero Manual Breaks**: Never use `<w:br/>` / `\n` in justified text. Use `<w:p>` paragraph marks.
- **Preserve Math**: Preserve native Word OMML math equations (`<m:oMath>`).

---

## 4. Git Lifecycle & Clean Working Tree
- **Directive 8 (Mandatory Git Lifecycle)**: Automatically stage changed files, create conventional semantic commit messages (`feat:`, `fix:`, `docs:`, `refactor:`), and keep the working tree clean.
