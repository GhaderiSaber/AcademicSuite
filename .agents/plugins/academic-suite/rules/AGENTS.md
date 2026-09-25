# Academic Suite Consolidated Domain Rules

These domain rules are automatically loaded and applied across all conversations by the `academic-suite` plugin. Each directive acts as a lean feedforward steering constraint backed by deterministic mechanical lifecycle hooks.

---

## 1. Radical Honesty & Pipeline Enforcement
- **Directive 0 (Binary Honesty Protocol & Anti-Deception)**: Compliance queries MUST begin with an unambiguous "Yes" or "No" as the very first word. Strict factual truth in logs; zero rationalization. Multi-agent execution claims strictly require physical `invoke_subagent` calls. [Enforcement: `Stop` hook / `transcript_and_rule_guard.py`]
- **Lesson (LSN-2026-DOM-PARSING-FOR-OPENXML-MODIFICATION-001)**: Strictly ban regex string substitutions on minified XML. Mandate structured XML DOM parsing via lxml or ElementTree for all OpenXML modifications. Mandate mechanical body paragraph count verification (> 0) before release. [Enforcement: dynamic_invariant_guard.py (LSN-2026-DOM-PARSING-FOR-OPENXML-MODIFICATION-001)]
- **Directive 2 (Deterministic Calculation Invariant)**: Zero mental arithmetic or hallucinated statistics in memory. Compute via bundled deterministic Python/R CLI scripts on real datasets. [Enforcement: `Stop` hook / `statistics_agent_guard.py`]
- **Directive 3 (Artifact-Gated Stages & Triad Invariant)**: Zero skipping stages. Every micro-stage and hypothesis stage MUST produce a synchronized on-disk triad: `.docx` (Word), `.md` (Markdown), and `.json` (Data/Stats). Monolithic drafting prompts are strictly prohibited. Defense presentations follow the 8-stage sequence (D.0–D.7). [Enforcement: `Stop` hook / `academic_orchestrator_guard.py`]
- **Directive 3.1 (Chapter 5 Prose-Only Invariant)**: Chapter 5 (Discussion & Conclusion) must strictly contain **zero tables** (Markdown `|---|` or Word `<w:tbl>`). 100% continuous narrative prose and theoretical synthesis. All tables belong exclusively in Chapter 4. [Enforcement: `Stop` hook / `academic_writer_guard.py` DOM parser]
- **Directive 4.1 (Presentation Visual Standards & Academic Sobriety)**: Zero emojis in academic deliverables/slides. Zero English words in Persian slides. DrawingML dual-slot font binding (`B Titr` / `B Nazanin` / `Times New Roman`). LTR numeric decoupling ($-0.32$). SmartArt RTL (`Reverse = 1`). [Enforcement: `Stop` hook / `persian_defense_presentation_builder`]
- **Directive 7.1 (Academic Sobriety & Anti-Hyperbole)**: Zero tolerance for emotional padding, dramatic rhetoric, sensational adjectives, or hyperbolic phrasing. Academic writing must remain strictly objective, neutral, sober, and fact-based. [Enforcement: `Stop` hook / `academic_writer_guard.py`]
- **Directive 11 (Interactive Stage-Gate Protocol)**: Emit Stage Completion Report (what was done, what is next) and HALT for user confirmation before advancing. Autonomous multi-stage runaway in a single turn is prohibited. [Enforcement: `Stop` hook / `academic_orchestrator_guard.py`]
- **Directive 12.1 (Sole Orchestrator Mandate)**: Antigravity is the sole agent conductor via `invoke_subagent`. Standalone Python dispatch loops or agent emulators are strictly prohibited. [Enforcement: `Stop` hook / `transcript_and_rule_guard.py`]
- **Directive 19 (The Six-Part Functional Separation Invariant)**: Agent decides | Skill instructs | Script computes | Hook enforces | State machine authorizes | Artifact manifest defines. [Enforcement: Architecture contract]
- **Directive 20 (The Orchestrator Architectural Invariants)**: `academic-orchestrator` possesses `invoke_subagent` and strictly lacks execution tools (`run_command`, `write_to_file`, `replace_file_content`, `edit_file`). Pure conductor. [Enforcement: `PreToolUse` hook / `academic_orchestrator_guard.py`]
- **Directive 21 (Proactive Human Mentorship & Dual-Track Immediate Graduation)**: Human mentor guidance immediately codified into `.agents/learning/knowledge/`. Universal procedural invariants graduated in the same turn into `SKILL.md` / `rules/AGENTS.md` via `academic_graduation_compiler.py`. [Enforcement: `academic_graduation_compiler.py`]
- **Directive 22 (Fail-Closed Mechanical Validation Gate Invariant)**: Reject verbal "PASS"; require verified physical `validation_report.json` on disk with `overall_verdict == "PASS"` and `checks_failed == 0`. [Enforcement: `Stop` hook / `validation_agent_guard.py`]

---
- **Anti-pattern (AP-2026-NAIVE-LENGTH-REFERENCE-PARSING)**: Implement robust structural parsing using regex patterns that match specific citation components (e.g., publication year in parentheses, DOI links, standard APA 7 formatting) or use a dedicated reference parser rather than character count. [Enforcement: dynamic_invariant_guard.py (AP-2026-NAIVE-LENGTH-REFERENCE-PARSING)]
## 2. Interaction & File Naming Standards (Universal Mandate)
- **Directive 6 (English Primary Interaction & English-Only Filenames)**:
  - Agents communicate, reason, plan, and report strictly in **English**. Persian is reserved strictly for academic deliverable content.
  - Every file, script, dataset, table, docx, pptx, or directory **MUST** be named strictly using English ASCII characters (`^[a-zA-Z0-9_.-]+$`). Zero non-ASCII filenames on disk. [Enforcement: `PreToolUse` hook / `safety_hooks.py`]

---

## 3. Persian Academic Typography & Font Standards
- **Font Bindings**: Persian Body Text: `B Nazanin` (13–14 pt Regular); Persian Headings: `B Titr` (12–18 pt Bold); Latin Characters, Numbers & Statistics: `Times New Roman`.
- **Directionality (BiDi)**: Enforce RTL via `<w:bidi w:val="1"/>` in paragraph properties `<w:pPr>`. In tables, enforce `<w:tblPr><w:bidiVisual/></w:tblPr>`. Numeric cells decoupled to LTR (`rtl="0"`) with Latin font (`Times New Roman`) so negative signs precede numbers ($-0.32$).
- **Zero Manual Breaks**: Never use `<w:br/>` / `\n` in justified text. Use `<w:p>` paragraph marks.
- **Preserve Math**: Preserve native Word OMML math equations (`<m:oMath>`).
- **Zero Inline Latin in Persian Text**: Running Persian narrative text must strictly contain zero Latin script words. Foreign author names must be transliterated phonetically to Persian (e.g. «اسمیت»), technical jargon translated to Persian, and the original English terminology placed strictly in footnotes.
- **Native OpenXML Word Footnotes**: Footnotes in Word `.docx` deliverables must be compiled as true native OpenXML elements (`word/footnotes.xml` and `<w:footnoteReference>`), never simulated as plain text paragraphs at document bottom.
- **Zero Regex on OpenXML (DOM Parsing Invariant)**: Never use regex string substitution (`re.sub`) on minified OpenXML files (`word/document.xml`). Always use structured DOM tree parsing (`lxml` or `xml.etree.ElementTree`) and mechanically verify body paragraph counts (> 0) prior to deliverable release. [Enforcement: `PreToolUse` & `Stop` hooks / `academic_writer_guard.py`]

---

## 4. Git Lifecycle & Clean Working Tree
- **Directive 8 (Mandatory Git Lifecycle)**: Automatically stage changed files, create conventional semantic commit messages (`feat:`, `fix:`, `docs:`, `refactor:`), and keep the working tree clean. [Enforcement: Session completion invariant]
- **Directive 23 (Clean Workspace Root Standard)**: Writing or dropping executable/analysis scripts (`.py`, `.sh`, `.R`, `.sps`, `.bash`) directly into repository or workspace root folders is strictly prohibited. Route scripts strictly to: (1) scratch directory, (2) `02_analysis_code/`, (3) `.agents/scripts/`, (4) `tests/`. [Enforcement: `PreToolUse` hook / `safety_hooks.py`]
- **Directive 24 (Main Agent Repository Codification Boundary & Non-Interference Invariant)**: The Main Agent (Track 1) is strictly responsible for repository infrastructure, pipeline codification, compiler and hook maintenance, and test harnesses. The Main Agent must NEVER manually evolve skills (`SKILL.md` or skill scripts) or manually modify `.agents/hooks/rules/enforced_invariants.json`. Evolution of skills, agents, and creation of mechanical rules is strictly the exclusive domain of the autonomous continuous learning pipeline (`trajectory-analyzer` -> `behavior-analyst` -> `knowledge-curator` -> `skill-evolver` -> `evaluation-agent` -> `academic_graduation_compiler.py`). When defects or critiques arise, the Main Agent must ensure the learning pipeline executes and graduates candidates properly, rather than manually intervening. [Enforcement: `PreToolUse` hook / `safety_hooks.py`]
