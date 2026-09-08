---
name: academic-drive-project-organizer
description: >-
  Automated project lifecycle manager and structural organizer for academic research projects
  across Google Drive ('My Work', 'Pending Works', 'Finished Works'). Audits directories for
  loose files, lock files, and fragmented folders, restructures project contents into a
  deterministic 4-tier taxonomy (01_raw_inputs, 02_analysis_code, 03_deliverables, 04_references_and_lit),
  cross-references Duzen milestones and payments into unified Master Project Catalogs (.xlsx and .md),
  provisions standardized new client folders with metadata, and safely manages lifecycle stage transitions
  with reversible undo manifests.
---

# Academic Drive Project Organizer & Lifecycle Manager (سامانه مدیریت و ساختاردهی پروژه‌های درایو)

This skill automates the organization, restructuring, lifecycle tracking, and financial reconciliation of client academic research projects across **Google Drive** (`Pending Works`, `My Work`, and `Finished Works`).

It bridges the gap between raw file storage in Google Drive and structured workflow management in **Duzen** (`duzen_backup_*.json`), enforcing a deterministic, defense-ready 4-tier taxonomy with safety-first defaults (dry-run mode and undo manifests).

---

## 1. When to Activate This Skill

Activate this skill when:
1. **Auditing Google Drive Folders**: Detecting loose files, temporary lock files (`~$*.docx`), and fragmented client folders across `Pending Works`, `My Work`, or `Finished Works`.
2. **Reorganizing a Client Project**: Tidying an unorganized project directory into standard subfolders (`01_raw_inputs`, `02_analysis_code`, `03_deliverables`, `04_references_and_lit`).
3. **Provisioning New Projects**: Instantiating a clean, standardized project directory for a new client with complete subfolders and `project_meta.json`.
4. **Synchronizing with Duzen**: Cross-referencing the latest Duzen backup (`duzen_backup_*.json`) with Google Drive folders to produce an updated `MASTER_PROJECT_CATALOG.xlsx` and `MASTER_PROJECT_CATALOG.md`.
5. **Lifecycle Stage Migrations**: Moving completed projects from `Pending Works` or `My Work` to `Finished Works`, or reopening projects safely.
6. **Undoing Accidental Changes**: Rolling back a reorganization using an automated `reorganize_manifest.json`.

---

## 2. Standard 4-Tier Project Taxonomy

Every client project folder adheres to the following deterministic structure:

```
[Client Name - Research Topic]/
├── project_meta.json              # Client name, status, timestamps, and schema version
├── reorganize_manifest.json       # (Optional) Reversible file action history for --undo
├── 01_raw_inputs/
│   ├── proposal.docx              # Approved student research proposal / topic
│   ├── Questionnaires / scales    # Measurement instruments, scoring guides
│   ├── survey_data.sav / .csv     # Raw, uncleaned SPSS or survey response datasets
│   └── screenshots / notes        # Initial communications, problem statements
├── 02_analysis_code/
│   ├── syntax.sps                 # SPSS transformation, cleaning, and analysis syntax
│   ├── model.splscb / .dim        # SmartPLS structural models & CB-SEM diagrams
│   ├── simulation.ipynb           # Jupyter or SimDat psychometric simulation code
│   └── script.r                   # R lavaan / psych analysis scripts
├── 03_deliverables/
│   ├── Chapter4_Results.docx      # Publication-ready Chapter 4 statistical report
│   ├── Chapter5_Discussion.docx   # Chapter 5 theoretical discussion report
│   ├── Defense_Presentation.pptx  # Slide deck with candidate speaker notes
│   ├── Final_Article.docx         # Peer-reviewed journal manuscript
│   └── drafts_archive/            # Timestamped intermediate drafts and revisions
└── 04_references_and_lit/
    ├── project_library.enl        # EndNote bibliographic database
    ├── citations.ris / .enw       # Exported citation bundles
    └── literature_pdfs/           # Full-text empirical articles and psychometric papers
```

---

## 3. Command Reference & Usage Examples

### 3.1 Audit Google Drive Operational Roots
```bash
# Audit Pending Works (default)
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --audit -o .agents/skills/academic-drive-project-organizer/references

# Audit all 3 Google Drive roots simultaneously (Pending, My Work, Finished)
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --audit-all -o .agents/skills/academic-drive-project-organizer/references
```

### 3.2 Tidy and Restructure a Project Folder
```bash
# Dry-run inspection (safely previews actions without moving files)
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --tidy --project "Aysan Shokri" --dir "/Users/saber/Library/CloudStorage/GoogleDrive-ghaderi.sabir@gmail.com/My Drive/My Work"

# Apply reorganization and clean temporary lock files (~$*)
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --tidy --project "Aysan Shokri" --dir "/Users/saber/Library/CloudStorage/GoogleDrive-ghaderi.sabir@gmail.com/My Drive/My Work" \
  --apply --clean-junk
```

### 3.3 Undo a Previous Reorganization
```bash
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --undo "/Users/saber/Library/CloudStorage/GoogleDrive-ghaderi.sabir@gmail.com/My Drive/My Work/Aysan Shokri/reorganize_manifest.json"
```

### 3.4 Provision a Standardized New Project Folder
```bash
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --new-project "Niloofar Kazemi" \
  --topic "Structural Equation Modeling of Academic Burnout" \
  --dir "/Users/saber/Library/CloudStorage/GoogleDrive-ghaderi.sabir@gmail.com/My Drive/Pending Works"
```

### 3.5 Cross-Reference and Sync with Duzen
```bash
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --sync-duzen -o .agents/skills/academic-drive-project-organizer/references
```
*Generates:*
- `MASTER_PROJECT_CATALOG.md`: Formatted Markdown table linking client names, Duzen status, prices in Tomans, steps, and Google Drive folders.
- `MASTER_PROJECT_CATALOG.xlsx`: Formatted multi-column Excel tracking workbook.

### 3.6 Transition Project Lifecycle Stages
```bash
# Move a completed project to Finished Works (dry-run)
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --move-project "Aysan Shokri" --to finished

# Execute move to Finished Works
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --move-project "Aysan Shokri" --to finished --apply
```

---

## 4. Safety-First Guarantees

1. **Dry-Run by Default**: All reorganization, tidying, and stage transitions execute in simulation mode unless `--apply` is explicitly passed.
2. **Never Overwrite**: If a file collision occurs during reorganization, `organize_drive_projects.py` renames the file with an `_reorg` suffix rather than overwriting existing data.
3. **Automated Manifests**: Every applied reorganization writes a timestamped `reorganize_manifest.json` recording original paths, enabling immediate `--undo`.
4. **Metadata Preservation**: Updates `project_meta.json` with stage history and timestamps on each transition.
