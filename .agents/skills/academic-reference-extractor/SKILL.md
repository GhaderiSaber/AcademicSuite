---
name: academic-reference-extractor
description: >-
  Use this skill to extract bibliographic references cited in specific translated sections of
  academic papers, theses, dissertations, or books. Matches in-text citations or footnotes against
  the source document's bibliography, resolves missing or partial references, and generates EndNote
  (.enw), RIS (.ris), and formatted APA text (.txt) citation files containing exclusively the
  references for those translated sections.
---

# Academic Section Reference Extractor Skill

This skill guides the agent in extracting, filtering, and exporting bibliographic references corresponding **exclusively** to specific translated chapters or sections of an academic paper, book, or thesis.

It ensures that when translating a portion of a larger academic work (such as Chapter 1 of a dissertation), the user receives a clean, dedicated reference library containing only the works actually cited in that translated portion, rather than the entire 200–500 entry bibliography of the full book.

---

## 1. When to Use This Skill

Activate this skill when:
1. The user requests references, EndNote files, or citation exports for a **translated section or chapter**.
2. An academic translation was performed (e.g., using `persian-academic-translation`), and reference management files (`.enw`, `.ris`, `.txt`) are required for just that translated text.
3. The user needs to import citations from a specific chapter into reference managers like **EndNote**, **Zotero**, **Mendeley**, or **Citavi**.

---

## 2. Core Extraction Pipeline

```
  Translated Text / Footnotes
              │
              ▼
  [1. Citation Harvesting] ────────► List of (Author, Year) queries
                                           │
  Source Document Master Bib               │
              │                            ▼
              ▼                     [3. Matching Engine]
  [2. Reference Segmentation] ─────► - Author surname overlap
  - Parsed (YYYY) markers            - Multi-year handling
  - Clean entry boundaries           - Surname prefixes (van, de, Le)
                                     - Unicode / accent normalization
                                           │
                                           ▼
                                    [4. Gap Resolution]
                                     - Identify citations in text
                                       omitted from author's bib
                                     - Retrieve complete metadata
                                           │
                                           ▼
                               [5. Multi-Format Exporter]
                               ├── .enw (EndNote Import)
                               ├── .ris (Zotero / Mendeley)
                               └── .txt (Numbered APA List)
```

---

## 3. Detailed Step-by-Step Instructions

### Step 1: In-Text Citation Harvesting
Extract all in-text citations or footnotes appearing in the translated section:
- **From Footnotes**: If the translation used native footnotes or Markdown footnotes (`[^1]: Carleton et al., 2007`), collect the footnote definitions.
- **From Plain Text / Markdown**: Scan for author-date citations using regex:
  - Narrative: `Smith et al. (2020)`, `Lipshitz and Strauss (1997)`
  - Parenthetical: `(Smith et al., 2020)`, `(Van den Bos & Lind, 2002; Carleton, 2012)`
- **Multi-Year Citations**: Unpack multi-year citations into distinct query targets:
  - `Bordia et al., 2004a, 2004b` $\rightarrow$ `(Bordia, 2004a)` and `(Bordia, 2004b)`
  - `Knight, 1921, 2012` $\rightarrow$ `(Knight, 1921)` and `(Knight, 2012)`
  - `Lissek et al., 2005, 2009` $\rightarrow$ `(Lissek, 2005)` and `(Lissek, 2009)`

### Step 2: Source Bibliography Parsing
Extract and segment the master bibliography from the source document (PDF, Word, or text file):
1. **Locate Reference Section**: Find the starting page (usually headed "References" or "Bibliography").
2. **Detect Entry Boundaries**:
   - Primary delimiter: `(?<![/\w])\((\d{4}[a-z]?)\)(?:\.|\,|\s+[A-Z])`
   - Split entries where a capitalized author name follows the previous entry's DOI, URL, or final period.
3. **Clean Preceding Noise**: Remove stray letters or book chapter editor sections that may bleed into the start of a subsequent entry (see `clean_entry_start` in [extract_section_references.py](./scripts/extract_section_references.py)).

### Step 3: Robust Matching & Filtering
Match each harvested section citation against the segmented bibliography:
1. **Accent and Special Character Normalization**:
   - Normalize via `unicodedata.normalize('NFKD', text)` to map characters like `ê`, `é`, `ü` to base ASCII.
   - Replace any Unicode replacement characters (`\ufffd`).
2. **Name Normalization**:
   - Handle surname prefixes: `Van den Bos`, `Van der Heiden`, `de Finetti`, `Le Poire`.
   - Match on the main surname root (e.g. `bos`, `heiden`, `finetti`, `poire`).
3. **Scoring**:
   - Compute token overlap between citation author names and entry author names.
   - Require matching 4-digit publication year.
   - Collapse repeated citations of the same paper into a single record.

### Step 4: Gap Resolution (Omitted In-Text Citations)
In many academic theses and published books, authors occasionally cite works in the body text that they inadvertently left out of the final references section.
- Flag any citation query that has 0 matches against the source bibliography.
- Check whether it is a genuine publication cited in-text (e.g., secondary review papers, classic scales).
- Retrieve full metadata (title, journal, volume, pages, DOI) from academic sources (Crossref, PubMed, Google Scholar) and integrate the complete record into the section export.

### Step 5: Multi-Format Reference Export
Deliver the filtered section references in three universal formats, saved in the user's project folder:

1. **EndNote Import File (`.enw`)**:
   - Tagged format with `%0`, `%A`, `%D`, `%T`, `%J`/`%B`, `%V`, `%N`, `%P`, `%R`, `%U`.
   - Ready for double-click import into Thomson Reuters / Clarivate EndNote.
2. **Universal RIS File (`.ris`)**:
   - Standard tags `TY  -`, `AU  -`, `PY  -`, `TI  -`, `JO  -`, `VL  -`, `IS  -`, `SP  -`, `EP  -`, `DO  -`, `UR  -`, `ER  -`.
   - Supported by Zotero, Mendeley, Citavi, Paperpile, and RefWorks.
3. **Formatted Text File (`.txt`) with Citation Style Profiles**:
   - Clean, numbered reference list formatted according to international or Iranian national citation standards:
     * **`apa7`** (Default): APA 7th Edition standards.
     * **`tehran_univ`**: University of Tehran style guide (شیوه‌نامه دانشگاه تهران) with explicit «صص» prefixes and Latin journal volume designations.
     * **`irandoc`**: Irandoc thesis repository standard (شیوه‌نامه ایرانداک).
     * **`farhangestan`**: Academy of Persian Language & Literature standards (اعداد فارسی، گیومه برای عناوین و نیم‌فاصله‌های مصوب).
   - **Zero Raw Markdown Asterisks**: When exporting or inserting references into Word documents (`.docx`), never leave literal asterisks (`*Journal Name*`) in the output. Render journal and book titles with native Word italic runs (`<w:i>`).
   - **Bilingual References Support**: When compiling theses or bilingual documents, partition references into Persian references (الف) منابع فارسی sorted by Persian alphabet) and English references (ب) منابع انگلیسی sorted A–Z).

---

## 4. National Academic Citation Profiles & CLI Usage

The automated reference extractor provides a unified CLI engine supporting both Western and Iranian citation profiles:

```bash
# Standard APA 7 extraction (creates .enw, .ris, and _apa7.txt):
python3 .agents/skills/academic-reference-extractor/scripts/extract_section_references.py \
  --source-bib "full_bibliography.txt" \
  --citations "in_text_citations.txt" \
  --output-dir "./chapter_references" \
  --prefix "Chapter1_References" \
  --style apa7

# University of Tehran Thesis & Article Profile:
python3 .agents/skills/academic-reference-extractor/scripts/extract_section_references.py \
  --source-bib "full_bibliography.txt" \
  --citations "in_text_citations.txt" \
  --output-dir "./chapter_references" \
  --prefix "Chapter1_References" \
  --style tehran_univ

# Irandoc National Thesis Repository Profile:
python3 .agents/skills/academic-reference-extractor/scripts/extract_section_references.py \
  --source-bib "full_bibliography.txt" \
  --citations "in_text_citations.txt" \
  --output-dir "./chapter_references" \
  --prefix "Chapter1_References" \
  --style irandoc

# Farhangestan Standards (Persian Numerals & Half-Spaces):
python3 .agents/skills/academic-reference-extractor/scripts/extract_section_references.py \
  --source-bib "full_bibliography.txt" \
  --citations "in_text_citations.txt" \
  --output-dir "./chapter_references" \
  --prefix "Chapter1_References" \
  --style farhangestan
```

---

## 5. Deliverable File Naming Convention

Place generated files directly in the user's project directory with descriptive names:
- `[Document_Name]_[Section_Name]_References.enw`
- `[Document_Name]_[Section_Name]_References.ris`
- `[Document_Name]_[Section_Name]_References_[style].txt`

*Example*:
- `Intolerance_of_Uncertainty_Pages_1-26_References.enw`
- `Intolerance_of_Uncertainty_Pages_1-26_References.ris`
- `Intolerance_of_Uncertainty_Pages_1-26_References_tehran_univ.txt`

---

## 6. Supporting Resources

- [extract_section_references.py](./scripts/extract_section_references.py): Production Python script for parsing, matching, and generating `.enw`, `.ris`, and `.txt` files across APA 7 and Iranian profiles.
- [enw_ris_formats.md](./references/enw_ris_formats.md): Field specifications and tag definitions for EndNote and RIS formats.
- [citation_patterns.md](./references/citation_patterns.md): Regex patterns and common in-text citation variants.
- [sample_workflow.md](./examples/sample_workflow.md): Complete walkthrough of section reference extraction for a dissertation chapter.
