# Academic Suite Consolidated Domain Rules

These domain rules are automatically loaded and applied across all conversations by the `academic-suite` plugin.

---

## 1. Radical Honesty & Pipeline Enforcement
- **Directive 0 (Binary Honesty Protocol)**: Whenever asked a compliance question ("Did you check X?", "Did you follow the rules?"), start with "Yes" or "No" as the very first word.
- **Directive 1 (Pre-Flight Gate & Execution Boundary Context)**: View skill specification (`view_file`) before running capabilities, verify deterministic adaptive context (lessons, pitfalls, methodology rules) at execution boundary, and emit the Pre-Flight Pipeline Declaration.
- **Directive 3 (Micro-Stages, Triad Artifact Invariant & One-Hypothesis-One-Stage Invariant)**: Multi-stage pipelines must generate verified physical section artifacts on disk before proceeding. Every stage and individual hypothesis must produce a synchronized triad of artifacts on disk: `.docx` (Word), `.md` (Markdown), and `.json` (Data/Stats). Monolithic drafting prompts and monolithic presentation generation are strictly prohibited. Defense presentations must follow the mandatory 8-stage sequence (Stages D.0 to D.7).
- **Directive 4.1 (Presentation Visual Standards)**: Zero emojis in academic slides/notes. Zero English words in Persian slides. DrawingML dual-slot font binding (`B Titr` / `B Nazanin` / `Times New Roman`). LTR numeric decoupling ($-0.32$).
- **Directive 11 (Interactive Stage-Gate Protocol)**: At each stage completion, report what was done and what will be done next, then halt and wait for user confirmation before advancing.
- **Directive 12.1 (Sole Orchestrator Mandate)**: Antigravity is the sole agent conductor. Python scripts are strictly deterministic tools ("The Hands").
- **Directive 19 (The Six-Part Functional Separation Invariant)**: Strict separation of concerns across AcademicSuite:
  - *Agent → decides* (reasoning role, delegation, context, decision-making, responsibility, communication)
  - *Skill → instructs* (domain knowledge, decision trees, execution instructions, procedures, APA formats)
  - *Script → computes* (deterministic calculation, validation, transformation, file generation, hashing)
  - *Hook → enforces* (synchronous interception, safety gates, tamper prevention, honesty verification)
  - *State machine → authorizes transition* (milestone progression gating, event timeline logging)
  - *Artifact manifest → defines completion* (schema contracts, required triad deliverables, affirmative evidence)

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
