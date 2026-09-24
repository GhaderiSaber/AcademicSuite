# Academic Suite Consolidated Domain Rules

These domain rules are automatically loaded and applied across all conversations by the `academic-suite` plugin.

---

## 1. Radical Honesty & Pipeline Enforcement
- **Directive 0 (Binary Honesty Protocol)**: Whenever asked a compliance question ("Did you check X?", "Did you follow the rules?"), start with "Yes" or "No" as the very first word.
- **Directive 1 (Pre-Flight Gate & Execution Boundary Context)**: View skill specification (`view_file`) before running capabilities, verify deterministic adaptive context (lessons, pitfalls, methodology rules) at execution boundary, and emit the Pre-Flight Pipeline Declaration.
- **Directive 3 (Micro-Stages, Triad Artifact Invariant & One-Hypothesis-One-Stage Invariant)**: Multi-stage pipelines must generate verified physical section artifacts on disk before proceeding. Every stage and individual hypothesis must produce a synchronized triad of artifacts on disk: `.docx` (Word), `.md` (Markdown), and `.json` (Data/Stats). Monolithic drafting prompts and monolithic presentation generation are strictly prohibited. Defense presentations must follow the mandatory 8-stage sequence (Stages D.0 to D.7).
- **Directive 3.1 (Chapter 5 Prose-Only Invariant)**: Chapter 5 (Discussion & Conclusion) must strictly contain **zero tables** (Markdown `|---|` or Word `<w:tbl>`). It is 100% continuous narrative prose, theoretical synthesis, and psychological mechanism explanation. All statistical, numerical, and summary tables belong exclusively in Chapter 4.
- **Directive 4.1 (Presentation Visual Standards)**: Zero emojis in academic slides/notes. Zero English words in Persian slides. DrawingML dual-slot font binding (`B Titr` / `B Nazanin` / `Times New Roman`). LTR numeric decoupling ($-0.32$).
- **Directive 7.1 (Academic Sobriety & Anti-Hyperbole)**: Zero tolerance for emotional padding, dramatic rhetoric, sensational adjectives, or hyperbolic phrasing to inflate word counts or narrative volume. Academic writing must remain strictly objective, neutral, sober, and fact-based regardless of length targets.
- **Directive 11 (Interactive Stage-Gate Protocol)**: At each stage completion, report what was done and what will be done next, then halt and wait for user confirmation before advancing.
- **Directive 12.1 (Sole Orchestrator Mandate)**: Antigravity is the sole agent conductor. Python scripts are strictly deterministic tools ("The Hands").
- **Directive 19 (The Six-Part Functional Separation Invariant)**: Strict separation of concerns across AcademicSuite:
  - *Agent → decides* (reasoning role, delegation, context, decision-making, responsibility, communication)
  - *Skill → instructs* (domain knowledge, decision trees, execution instructions, procedures, APA formats)
  - *Script → computes* (deterministic calculation, validation, transformation, file generation, hashing)
  - *Hook → enforces* (synchronous interception, safety gates, tamper prevention, honesty verification)
  - *State machine → authorizes transition* (milestone progression gating, event timeline logging)
  - *Artifact manifest → defines completion* (schema contracts, required triad deliverables, affirmative evidence)
- **Directive 20 (The Orchestrator Architectural Invariants)**:
  - *Orchestrator Non-Execution Invariant*: `academic-orchestrator` MUST NOT possess: `run_command`, `write_to_file`, `replace_file_content`, `edit_file`.
  - *Delegation Availability Invariant*: `academic-orchestrator` MUST possess: `invoke_subagent`.
- **Directive 21 (Proactive Human Mentorship & Dual-Track Immediate Graduation Protocol)**:
  - Direct human guidance (e.g. *"Remember that..."*, *"Learn this..."*) is immediately codified via `academic_human_mentor.py` into persistent schema-validated JSON (`.agents/learning/knowledge/`).
  - **Track 1 (Universal / Procedural Invariants)**: When guidance defines a permanent methodological or writing rule, the deterministic compiler ("The Hands" — `academic_graduation_compiler.py`) MUST immediately in the same turn graduate it into target `SKILL.md` (under Invariants) and/or `rules/AGENTS.md`, verify Directive 18 ceiling (< 500 lines), and commit/push to GitHub.
  - **Track 2 (Case-Specific / Scale Facts)**: Retained strictly as scoped episodic JSON in `learning/knowledge/` without polluting global rules.
  - Defaults to `scope: "cross-project"` (Shared Learning) to sync to GitHub and inform all future projects.
  - Deterministically prioritized and injected into pre-flight briefings.

---

## 2. Interaction & File Naming Standards (Universal Mandate)
- **Directive 6 (English Primary Interaction & English-Only Filenames)**:
  - Agents communicate, reason, plan, and report to the user strictly in **English**. Persian is reserved strictly for academic deliverables and client messages.
  - Every file, script, dataset, table, docx, pptx, or directory **MUST** be named strictly using English ASCII characters (`a-z`, `A-Z`, `0-9`, `_`, `-`, `.`). Zero Persian/non-ASCII filenames on disk.

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
- **Zero Inline Latin in Persian Text**: Running Persian narrative text must strictly contain zero Latin script words. Foreign author names must be transliterated phonetically to Persian (e.g. «اسمیت»), technical jargon translated to Persian, and the original English terminology/spelling placed strictly in footnotes.
- **Native OpenXML Word Footnotes**: Footnotes in Word `.docx` deliverables must be compiled as true native OpenXML elements (`word/footnotes.xml` and `<w:footnoteReference>`), never simulated as plain text paragraphs at the bottom of the document.
- **Zero Regex on OpenXML (DOM Parsing Invariant)**: Never use regex string substitution (`re.sub`) on minified OpenXML files (`word/document.xml`). Always use structured DOM tree parsing (`lxml` or `xml.etree.ElementTree`) and mechanically verify body paragraph counts (> 0) prior to deliverable release.

---

## 4. Git Lifecycle & Clean Working Tree
- **Directive 8 (Mandatory Git Lifecycle)**: Automatically stage changed files, create conventional semantic commit messages (`feat:`, `fix:`, `docs:`, `refactor:`), and keep the working tree clean.
- **Directive 23 (Clean Workspace Root Standard)**: Writing or dropping executable/analysis scripts (`.py`, `.sh`, `.R`, `.sps`, `.bash`) directly into repository or workspace root folders is strictly prohibited. Route scripts strictly to: (1) `<appDataDir>/brain/<conversation-id>/scratch/` or `/tmp/` for scratch scripts, (2) `02_analysis_code/` for project code, (3) `.agents/scripts/` for suite tools, (4) `tests/` for tests.

