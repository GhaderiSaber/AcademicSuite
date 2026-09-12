---
name: literature-harvester
description: Automated multi-database academic literature search engine, empirical parameter extractor, and Chapter 2 empirical background compiler. Queries PubMed / NCBI Entrez, CrossRef, Semantic Scholar, and Iranian databases (SID.ir & Magiran). Automatically extracts participant sample sizes (N), research designs (RCT, ANCOVA, SEM), and psychometric instruments from abstracts. Generates defense-ready Chapter 2 Word reports (.docx) with APA 7 empirical tables and 5-part narrative formulas, 4-sheet Excel matrices (.xlsx), and standard RIS citation files (.ris) for EndNote and Zotero.
---

# `literature-harvester` — Multi-Database Literature Harvester & Extractor (Skill #23)

`literature-harvester` is the automated literature retrieval, parameter extraction, and empirical background synthesis engine of the **AcademicSuite**. It bridges the gap between academic research discovery and thesis writing by automatically searching international (PubMed, CrossRef, Semantic Scholar) and Iranian (SID, Magiran) scientific repositories, extracting structured empirical metadata, and compiling defense-ready Chapter 2 literature review documents.

---

## 1. When to Activate This Skill

Activate this skill whenever:
- The user asks to **search or harvest academic papers** on a research topic (*"Find recent studies on ACT therapy and teacher burnout in Iranian and foreign journals"*).
- The user needs an **empirical background matrix** or summary table for Chapter 2 of their thesis or dissertation (جدول پیشینه پژوهش‌های داخلی و خارجی برای فصل دوم).
- The user wants to **extract sample sizes ($N$), methodologies, and psychometric instruments** from abstracts without manual reading.
- The user requests generating an **EndNote or Zotero citation file (`.ris`)** for a specific literature search query.
- The user wants to automatically synthesize empirical findings using the **standard 5-part Iranian reporting formula** (*«نویسنده (سال) در پژوهشی با عنوان... بر روی N نفر...»*).
- Downstream piping into [persian-literature-review-builder](file:///Users/saber/Desktop/academic_suite/.agents/skills/persian-literature-review-builder/SKILL.md) or [systematic-review-meta-analyst](file:///Users/saber/Desktop/academic_suite/.agents/skills/systematic-review-meta-analyst/SKILL.md).

---

## 2. Databases & Scientific Repositories Supported

1. **PubMed / NCBI Entrez REST API**:
   - Real-time querying of biomedical and clinical psychology trials via E-utilities (`esearch`, `esummary`, `efetch`).
2. **CrossRef Works API**:
   - Retrieves peer-reviewed DOI metadata across Elsevier, Springer, Wiley, Taylor & Francis, and APA PsycNet.
3. **Semantic Scholar Academic Graph API**:
   - Open access paper metadata, abstracts, and citation counts.
4. **Iranian Databases (SID.ir & Magiran)**:
   - Structured parsing of Iranian scientific-research journals (نشریات علمی-پژوهشی وزارت علوم و بهداشت) with Solar Hijri years (۱۳۹۹–۱۴۰۳) and Persian author names.
5. **High-Impact Curated Corpus**:
   - Built-in resilient benchmark library ensuring uninterrupted operation during network latency, timeouts, or IP filtering.

---

## 3. CLI Command Reference

### Standard Search (Persian Query - Balanced Iranian & Foreign Corpus):
```bash
python3 .agents/skills/literature-harvester/scripts/harvester_engine.py \
  --query "درمان مبتنی بر پذیرش و تعهد انعطاف‌پذیری روان‌شناختی فرسودگی شغلی" \
  --out-dir "./harvested_literature" \
  --limit 10 \
  --lang fa
```

### English Search (PubMed / CrossRef Priority):
```bash
python3 .agents/skills/literature-harvester/scripts/harvester_engine.py \
  --query "cognitive reappraisal emotion regulation mindfulness depression" \
  --out-dir "./harvested_literature_en" \
  --limit 10 \
  --lang en
```

### Automated Open-Access Full-Text PDF Downloader:
```bash
# Standalone paper downloader:
python3 .agents/skills/literature-harvester/scripts/paper_downloader.py \
  --query "self-compassion chronic pain university students" \
  --out-dir "./04_references_and_lit/papers" \
  --limit 10

# Direct harvest with simultaneous PDF download:
python3 .agents/skills/literature-harvester/scripts/harvester_engine.py \
  --query "acceptance commitment therapy chronic pain" \
  --out-dir "./harvested_act" \
  --limit 10 \
  --download-pdf \
  --papers-dir "./04_references_and_lit/papers" \
  --lang en
```

### Run via JSON Search Payload:
```bash
python3 .agents/skills/literature-harvester/scripts/harvester_engine.py \
  --json .agents/skills/literature-harvester/examples/sample_harvest_query.json \
  --sample act_psychological_flexibility_fa \
  --out-dir "./harvested_act" \
  --lang fa
```

---

## 4. Multi-Modal Deliverables Generated

1. **`گزارش_جامع_پیشینه_پژوهش_استخراج‌شده.docx` / `Harvested_Literature_Review.docx`**:
   - Native Right-to-Left OpenXML BiDi Word report with *B Titr*, *B Nazanin*, and *Times New Roman*.
   - **Section 1**: Standard APA 7 Empirical Summary Table (Author, Year, Title, Population & Sample N, Instruments, Findings).
   - **Section 2**: Comprehensive 5-Part Academic Narrative Synthesis ready to paste directly into Chapter 2 of the thesis.
2. **`harvested_empirical_studies.xlsx`**:
   - 4 dedicated worksheets:
     - `Master Empirical Matrix`: Unified overview of all harvested studies.
     - `Iranian Studies (SID)`: Domestic Iranian research with solar hijri years.
     - `International Studies (PubMed)`: Global trials with DOIs and international citations.
     - `Citations & Identifiers`: Formatted APA references.
3. **`harvested_citations.ris`**:
   - Standard bibliographic RIS format compatible with EndNote, Zotero, Mendeley, and RefWorks.
4. **`harvested_studies.json`**:
   - Machine-readable structured ledger compatible with `persian-literature-review-builder`.
