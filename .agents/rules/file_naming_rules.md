# File Naming & Directory Structure Specification (Directives 6, 23)

Universal filesystem naming conventions and routing standards across AcademicSuite.

---

## 1. Naming Contracts

- **Directive 6 (Mandatory English ASCII Filenames)**: Every file, script, dataset, table, docx, pptx, or directory MUST be named strictly in ASCII English (`^[a-zA-Z0-9_.-]+$`). Zero non-ASCII or Persian characters on disk. [Enforcement: `safety_hooks.py` / `PreToolUse`]
- **Content vs. Filename Separation**: Internal deliverable text is in authentic Persian; physical filenames on disk remain strictly ASCII English.
- **Directive 23 (Clean Workspace Root Standard)**: Writing or dropping executable/analysis scripts (`.py`, `.sh`, `.R`, `.sps`) directly into the repository root is prohibited. Scripts must route strictly to:
  1. Temporary scratch directory (`<artifactDir>/scratch/`)
  2. `02_analysis_code/`
  3. `.agents/scripts/` or `.agents/skills/<skill>/scripts/`
  4. `tests/` [Enforcement: `safety_hooks.py` / `PreToolUse`]

---

## 2. Standard Casing Taxonomy

| File Category | Standard Casing | Valid Example |
| :--- | :--- | :--- |
| **Python / Shell Scripts** | `snake_case` | `calculate_sem_fit.py` |
| **Deliverables (.docx / .pptx)** | `Title_Case_With_Underscores` | `Client_Defense_Brief.docx` |
| **Data Matrices & JSON Triads** | `snake_case` | `stats_results.json` |
| **4-Tier Academic Taxonomy** | `Numbered_Prefix` | `01_raw_inputs/`, `02_analysis_code/`, `03_deliverables/`, `04_references_and_lit/` |

---

## 3. Remediation Protocol
Encountering non-ASCII files: (1) rename to descriptive English ASCII; (2) update references; (3) assert zero non-ASCII paths.
