---
name: citation-network-visualizer
description: Historical direct citation network and algorithmic historiography engine based on Eugene Garfield's HistCite framework and Hummon & Doreian's (1989) Main Path Analysis (MPA). Generates chronological citation graphs (chronomaps), calculates Local Citation Score (LCS) vs. Global Citation Score (GCS), Search Path Count (SPC) edge weights, and identifies the intellectual backbone trajectory across paradigm shifts. Exports publication-grade 300-DPI visual plots (.png), 5-sheet Excel matrices (.xlsx), and defense-ready Chapter 2 Word reports (.docx) in Persian and English.
---

# `citation-network-visualizer` — Algorithmic Historiography & Main Path Analysis Engine (Skill #25)

`citation-network-visualizer` is the official academic citation network and historiographical analysis engine of the **AcademicSuite**. It transforms direct citation links into chronological citation genealogies (HistCite chronomaps) and executes Hummon & Doreian's (1989) Main Path Analysis (MPA) using Search Path Count (SPC) to trace the evolutionary backbone of scientific disciplines, paradigm shifts, and theoretical branchings.

---

## 1. When to Activate This Skill

Activate this skill whenever:
- The user requests **direct citation network analysis (تحلیل شبکه استناد مستقیم)** or **algorithmic historiography (تاریخ‌نگاری الگوریتمی علم)**.
- The user mentions **HistCite**, **Main Path Analysis (تحلیل مسیر اصلی دانش)**, or **citation chronomaps (نگاشت زمانی استنادات)**.
- The user wants to trace the **historical intellectual trajectory** of a theory from root ancestors to modern frontiers.
- The user wants to compare **Local Citation Score (LCS)** against **Global Citation Score (GCS)** to isolate seminal cornerstones from interdisciplinary generalist papers.
- The user needs to compute **Search Path Count (SPC)** edge weights and identify **Global**, **Local**, or **Key-Route Main Paths**.
- The user needs a publication-ready **Word report with OpenXML BiDi RTL** for Chapter 2 of their thesis or a standalone bibliometric review paper.
- The user needs high-resolution **300-DPI timeline visualization figures** (`citation_chronomap.png` and `main_path_trajectory.png`).

---

## 2. Core Methodological & Topological Capabilities

### 2.1. Citation Scoring: Local vs. Global Impact
1. **Local Citation Score ($\text{LCS}$)**:
   - Quantifies citations received strictly within the specific scientific domain corpus ($\text{Out-Degree}$ in the knowledge flow DAG).
   - Serves as the purest metric of foundational stature and internal intellectual relevance.
2. **Global Citation Score ($\text{GCS}$)**:
   - Total citations recorded worldwide across Web of Science or Scopus.
3. **$\text{LCS} / \text{GCS}$ Ratio**:
   - High ratio ($\ge 0.15$) identifies core specialized cornerstones of the local paradigm.
   - Low ratio indicates broad multidisciplinary reach.
4. **Local Cited References ($\text{LCR}$)**:
   - Number of cited references belonging to the analyzed subfield ($\text{In-Degree}$ in the knowledge flow DAG).

### 2.2. Hummon & Doreian's Main Path Analysis (MPA)
- **Directed Acyclic Graph (DAG)**:
  - Causal temporal flow: Directed edge $(u, v)$ indicates foundational paper $u$ is cited by and historically precedes successor paper $v$ ($t_u \le t_v$).
- **Search Path Count ($\text{SPC}$)**:
  - Computed via topological dynamic programming:
    $$\text{SPC}(u, v) = N^-(u) \times N^+(v)$$
    where $N^-(u)$ is the count of paths from all root sources to $u$, and $N^+(v)$ is the count of paths from $v$ to all empirical sinks.
- **Main Path Traversal Options**:
  - **Global Main Path (`--main-path global`)**: Finds the end-to-end path maximizing total cumulative SPC weights.
  - **Local Main Path (`--main-path local`)**: Greedily traverses the highest-weight outgoing edge at each evolutionary milestone.
  - **Key-Route Main Path (`--main-path key-route`)**: Anchored around the global bottleneck edge with the highest overall SPC weight in the entire graph.

---

## 3. CLI Command Reference

The master CLI script is located at:
`.agents/skills/citation-network-visualizer/scripts/citation_visualizer_engine.py`

### Standard Global Main Path Analysis (Persian Thesis Mode):
```bash
python3 .agents/skills/citation-network-visualizer/scripts/citation_visualizer_engine.py \
  --input "citation_dataset.json" \
  --output-dir "./historiography_results" \
  --language fa \
  --main-path global
```

### English Review Article Mode (Local Main Path):
```bash
python3 .agents/skills/citation-network-visualizer/scripts/citation_visualizer_engine.py \
  --input "wos_citations.csv" \
  --output-dir "./chronomap_en" \
  --language en \
  --main-path local
```

### Key-Route Main Path Analysis:
```bash
python3 .agents/skills/citation-network-visualizer/scripts/citation_visualizer_engine.py \
  --input "citation_dataset.json" \
  --output-dir "./keyroute_output" \
  --language fa \
  --main-path key-route
```

### Default Built-in Psychological Lineage Benchmark:
```bash
python3 .agents/skills/citation-network-visualizer/scripts/citation_visualizer_engine.py \
  --output-dir "./citation_benchmark" \
  --language fa
```

---

## 4. Generated Multi-Modal Deliverables

Every execution produces five publication-grade artifacts:

1. **`گزارش_تحلیل_مسیر_اصلی_و_نگاشت_تاریخی_استنادات.docx`** (or `Historiographic_Citation_Network_Report.docx`):
   - Formatted in APA 7th Edition with native Right-to-Left (RTL) OpenXML BiDi and authentic Iranian academic typography (*B Titr*, *B Nazanin*, *Times New Roman*).
   - Contains: Executive Summary, Macro-structural DAG metrics, LCS vs. GCS ranking table, Main Path transition table with SPC weights, embedded 300-DPI figures, and Chapter 2 theoretical directives.
2. **`citation_chronomap.png` (300 DPI)**:
   - HistCite-style chronological citation network with time-layered horizontal axis, node sizing proportional to LCS, directional citation links, and Main Path highlighted in crimson.
3. **`main_path_trajectory.png` (300 DPI)**:
   - Isolated sequential Main Path timeline displaying pivotal milestone papers, transition SPC weights, and developmental steps.
4. **`citation_matrix.xlsx`**:
   - 5-sheet master Excel workbook:
     - Sheet 1: `Overview & Chronology`
     - Sheet 2: `LCS vs GCS Ranking`
     - Sheet 3: `Direct Citation Adjacency`
     - Sheet 4: `Main Path Trajectory`
     - Sheet 5: `Historical Lineages`
5. **`citation_summary.json`**:
   - Structured JSON schema containing all topological parameters, Main Path node sequences, and artifact links for orchestrator pipelines.

---

## 5. Input Data Format

The engine accepts JSON or CSV files. Each article record requires:
- `id`: Unique identifier (e.g., `"DOC_01"`).
- `title`: Manuscript title.
- `authors`: List of authors.
- `journal`: Publication source.
- `year`: Publication year ($t$).
- `citations`: Global Citation Score (GCS).
- `cited_doc_ids`: List of IDs within the dataset that this publication directly cites.
