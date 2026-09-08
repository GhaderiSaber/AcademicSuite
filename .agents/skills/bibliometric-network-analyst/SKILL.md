---
name: bibliometric-network-analyst
description: VOSviewer and Bibliometrix science mapping, keyword co-occurrence, co-citation, and co-authorship network analysis engine. Computes Bradford's Law journal scattering, Lotka's Law author productivity, NetworkX centralities (Degree, Betweenness, Closeness), and Callon's 4-quadrant strategic diagram (Motor, Niche, Emerging/Declining, Basic Themes). Exports native VOSviewer files (.txt), dual 300-DPI publication plots (.png), 5-sheet Excel matrices (.xlsx), and defense-ready Chapter 2 Word reports (.docx) in Persian and English.
---

# `bibliometric-network-analyst` — Science Mapping & Network Analysis Engine (Skill #24)

`bibliometric-network-analyst` is the official academic science mapping and bibliometric network analysis engine of the **AcademicSuite**. It automates keyword co-occurrence networks, co-citation topologies, author collaboration graphs, and Callon's 4-quadrant strategic modeling for literature reviews, thesis Chapter 2 empirical backgrounds, and standalone bibliometric review papers adhering to VOSviewer and Bibliometrix standards.

---

## 1. When to Activate This Skill

Activate this skill whenever:
- The user requests **bibliometric analysis (تحلیل علم‌سنجی)** or **science mapping (ترسیم نقشه دانش)**.
- The user mentions **VOSviewer**, **Bibliometrix**, **CiteSpace**, or **keyword co-occurrence networks (شبکه هم‌رخدادی واژگان)**.
- The user wants to map **thematic clusters** using **Callon's Strategic Diagram (نمودار راهبردی کالون)** (Motor, Niche, Emerging/Declining, and Basic Themes).
- The user wants to evaluate **Bradford's Law (قانون بردفورد)** of journal scattering or **Lotka's Law (قانون لوتکا)** of author productivity.
- The user requests calculating network centrality metrics: **Degree Centrality**, **Betweenness Centrality (پل‌های مفهومی)**, and **Closeness Centrality**.
- The user needs to prepare a **VOSviewer dataset** (`vosviewer_map.txt` and `vosviewer_network.txt`) or high-resolution **300-DPI science mapping figures**.
- The user needs a publication-ready **Word report with OpenXML BiDi RTL** for Chapter 2 of their thesis or dissertation.

---

## 2. Core Bibliometric & Topological Capabilities

### 2.1. Classical Laws of Bibliometrics
1. **Bradford's Law of Journal Scattering**:
   - Sorts journals by article productivity and partitions the corpus into Zone 1 (Nuclear/Core ~33%), Zone 2 (Secondary ~33%), and Zone 3 (Peripheral ~33%).
   - Computes empirical Bradford multiplier $k = z_2 / z_1$.
2. **Lotka's Law of Author Productivity**:
   - Quantifies the distribution of scientific output across scholars ($y = C / x^n$).
   - Isolates Core Thought Leaders, Prolific Authors, and Occasional Contributors.
3. **Zipf's Law of Keyword Distribution**:
   - Evaluates frequency ranking of domain keywords and identifies dominant research frontiers.

### 2.2. Network Centrality & Topology (NetworkX)
- **Degree Centrality ($k_i$) & Total Link Strength ($w_i$)**: Local conceptual prominence and citation strength.
- **Betweenness Centrality ($C_B$)**: Identifies intellectual gatekeepers and conceptual bridges mediating disparate research subfields.
- **Closeness Centrality ($C_C$)**: Quantifies information diffusion speed across the discipline.
- **Modularity Community Detection ($Q$)**: Greedy modularity clustering identifying dense thematic paradigms.

### 2.3. Callon's 4-Quadrant Strategic Diagram
Evaluates thematic clusters on a two-dimensional Cartesian plane:
- **Callon's Centrality ($C$)**: External link strength $\sum e_{kh}$ ($k \in \text{Cluster}, h \notin \text{Cluster}$) reflecting contextual relevance.
- **Callon's Density ($D$)**: Internal cohesion $\frac{\sum e_{ij}}{N_c}$ ($i, j \in \text{Cluster}$) reflecting maturity and development.

| Quadrant | Centrality | Density | Classification | Iranian Scientific Role |
| :---: | :---: | :---: | :---: | :---: |
| **Quadrant I** | High | High | **Motor Themes** | موتورهای محرک پژوهش و جبهه‌های اصلی |
| **Quadrant II** | Low | High | **Niche Themes** | مباحث تخصصی، حاشیه‌ای و تکامل‌یافته |
| **Quadrant III** | Low | Low | **Emerging/Declining Themes** | مباحث نوظهور، خلاءهای پژوهشی یا رو به زوال |
| **Quadrant IV** | High | Low | **Basic & Transversal Themes** | مفاهیم پایه، بین‌رشته‌ای و ساختاری |

---

## 3. CLI Command Reference

The master CLI script is located at:
`.agents/skills/bibliometric-network-analyst/scripts/bibliometric_engine.py`

### Standard Keyword Co-Occurrence Analysis (Persian Thesis Mode):
```bash
python3 .agents/skills/bibliometric-network-analyst/scripts/bibliometric_engine.py \
  --input "literature_corpus.json" \
  --output-dir "./bibliometric_results" \
  --language fa \
  --min-freq 1 \
  --top-n 30
```

### English Journal Paper Mode:
```bash
python3 .agents/skills/bibliometric-network-analyst/scripts/bibliometric_engine.py \
  --input "scopus_export.csv" \
  --output-dir "./biblio_en_output" \
  --language en \
  --min-freq 2 \
  --top-n 40
```

### Analysis from RIS Citation Files:
```bash
python3 .agents/skills/bibliometric-network-analyst/scripts/bibliometric_engine.py \
  --input "endnote_library.ris" \
  --output-dir "./biblio_ris_results" \
  --language fa
```

### Default Built-in Psychological Benchmark:
```bash
python3 .agents/skills/bibliometric-network-analyst/scripts/bibliometric_engine.py \
  --output-dir "./biblio_benchmark" \
  --language fa
```

---

## 4. Generated Multi-Modal Deliverables

Every execution produces five interconnected artifacts:

1. **`گزارش_تحلیل_علم‌سنجی_و_ترسیم_نقشه_دانش.docx`** (or `Bibliometric_Science_Mapping_Report.docx`):
   - Formatted in APA 7th Edition style with native Right-to-Left (RTL) OpenXML BiDi and authentic Iranian academic typography (*B Titr*, *B Nazanin*, *Times New Roman*).
   - Contains: Executive Summary, Bradford Zone Table, Lotka Productivity Table, Keyword Centrality Table, Callon Cluster Quadrant Table, embedded 300-DPI visual figures, and Chapter 2 theoretical implications.
2. **`bibliometric_network_map.png` (300 DPI)**:
   - Publication-grade force-directed network knowledge map with colored modularity clusters, weighted co-occurrence edges, and transparent label bounding boxes.
3. **`thematic_strategic_map.png` (300 DPI)**:
   - Callon's 4-Quadrant Strategic Diagram with median centrality and density crosshairs, bubble sizes proportional to cluster size, and bilingual quadrant annotations.
4. **`vosviewer_map.txt` & `vosviewer_network.txt`**:
   - Native VOSviewer files with normalized coordinates ($x, y$), cluster IDs, occurrence weights, and total link strengths ready for direct drag-and-drop into VOSviewer software.
5. **`bibliometric_matrix.xlsx`**:
   - 5-sheet master Excel workbook:
     - Sheet 1: `Overview & Top Papers`
     - Sheet 2: `Keyword Centrality`
     - Sheet 3: `Adjacency Matrix`
     - Sheet 4: `Author Collaboration`
     - Sheet 5: `Thematic Clusters`
6. **`bibliometric_summary.json`**:
   - Structured JSON schema containing all numerical graph metrics, cluster coordinates, and artifact references for downstream pipeline orchestration.

---

## 5. Input Data Formats

The engine natively ingests three primary data formats:
- **JSON**: Direct list of article objects with `{id, title, authors, journal, year, citations, keywords}`.
- **CSV**: Scopus or Web of Science CSV exports containing `Title`, `Authors`, `Source title`, `Year`, `Cited by`, and `Author Keywords`.
- **RIS**: EndNote / Zotero citation files containing tags `TI`, `AU`, `JO`, `PY`, and `KW`.
