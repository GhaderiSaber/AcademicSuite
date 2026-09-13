# Rule: Mandatory English-Only File & Directory Naming Convention
**Scope:** Universal across all agents, workflows, skills, scripts, deliverables, and artifacts.
**Directive:** All created, generated, compiled, exported, or refactored files and directories MUST be named in English ASCII characters only.

---

## 1. Core Rule & Directive

Every AI agent operating in this repository **MUST** strictly name all newly created, generated, compiled, exported, or refactored files and directories using **English ASCII characters only**.

- **Permitted Characters:** Standard English letters (`a-z`, `A-Z`), numbers (`0-9`), hyphens (`-`), underscores (`_`), and standard file extensions (e.g., `.docx`, `.pptx`, `.xlsx`, `.py`, `.md`, `.json`, `.pdf`).
- **Strict Prohibition Against Non-ASCII / Persian Names:**
  - Agents must **NEVER** create, save, or rename any file or directory with Persian, Arabic, or non-ASCII characters (e.g., never create `ارزیابی_مدل_ساختاری.pptx`, `پایان‌نامه_مرضیه.docx`, or `فصل_چهارم.xlsx`).
  - Never use Persian spaces or half-spaces (نیم‌فاصله `\u200c`) in filenames.

---

## 2. Standard Casing & Naming Patterns

| File Category | Standard Casing Pattern | Examples |
| :--- | :--- | :--- |
| **Python / Shell Scripts** | `snake_case` | `build_client_defense_brief.py`, `calculate_sem_fit.py` |
| **Formal Client Deliverables** | `Title_Case_With_Underscores` | `Client_Defense_Presentation_Brief.docx`, `Evaluating_Childhood_Trauma_Presentation.pptx` |
| **Data Matrices & Results** | `snake_case` | `stats_results.json`, `mediation_bootstrap_matrix.xlsx` |
| **Documentation & Guidelines** | `UPPER_CASE.md` or `Title_Case.md` | `AGENTS.md`, `README.md`, `Client_Defense_Presentation_Brief.md` |
| **Directories & Folders** | `snake_case` or `Numbered_Prefix` | `01_raw_inputs/`, `03_deliverables/presentation/`, `drafts_archive/` |

---

## 3. Technical Rationale & Integrity Safeguards

1. **Cross-Platform Sync & Cloud Resilience:**
   - Non-ASCII/Persian characters frequently cause filename encoding corruption between Windows (CP1252 / CP1256 / UTF-16), macOS, Linux, and cloud synchronization agents (Google Drive, OneDrive, GitHub).
2. **Terminal & CLI Pipeline Stability:**
   - Shell commands (`run_command`), Python scripts, and batch processors often encounter `UnicodeEncodeError` when reading or writing paths with non-ASCII characters in standard console environments.
3. **OpenXML, Office & Hyperlink Preservation:**
   - Word (`.docx`) and PowerPoint (`.pptx`) relationship files (`_rels`) and embedded media packages can suffer XML validation failures or broken hyperlinks when referencing non-ASCII filenames.

---

## 4. Content Language vs. Filename Separation

- **Deliverable Content:** The internal textual content of Persian theses, proposals, slides, client briefs, and questionnaires remains in authentic, scholarly Persian with full OpenXML `<w:bidi>` directionality, Persian fonts (`B Nazanin`, `B Titr`), and APA 7th Edition formatting.
- **Physical Filename:** The physical filename on disk must **ALWAYS** be 100% English.

---

## 5. Remediation Protocol

Whenever an agent encounters an existing file or client upload with a Persian or non-English filename:
1. Systematically rename the file to a clean, descriptive English name.
2. Update all script references, imports, and documentation links.
3. Verify that zero non-ASCII filenames remain in the active workspace.
