# Algorithmic Historiography & Main Path Analysis (MPA) Standards

This reference document defines the mathematical foundations, network traversal algorithms, citation scoring models, and visualization standards implemented in the **`citation-network-visualizer`** skill of the **AcademicSuite**.

---

## 1. Eugene Garfield's Algorithmic Historiography (HistCite Framework)

Algorithmic Historiography, pioneered by Eugene Garfield (Garfield et al., 2002, 2003), transforms unstructured citation indexes into chronological, genealogically ordered maps of scientific evolution.

In a scientific domain, research does not evolve in isolation; instead, newer publications cite foundational antecedent papers to establish legitimacy, methodology, or theoretical foundations. By ordering publications along a temporal vertical or horizontal axis and drawing directed citation arrows backwards to predecessor works, the intellectual genealogy and paradigm shifts of the discipline become visually self-evident.

---

## 2. Citation Scoring: Local vs. Global Impact

A critical distinction in algorithmic historiography is the difference between global citations (worldwide) and local citations (within the subfield):

### 2.1. Local Citation Score (LCS)
The Local Citation Score of document $i$ is the number of times it is cited strictly by other papers *within the analyzed corpus* $\mathcal{C}$:

$$\text{LCS}(i) = \sum_{j \in \mathcal{C}, j \ne i} A_{ji}$$

where $A_{ji} = 1$ if document $j$ cites document $i$, and $0$ otherwise.
- **Significance**: $\text{LCS}$ is the purest indicator of a paper's internal influence and foundational stature within that specific scientific debate. A paper with high $\text{LCS}$ is an indispensable cornerstone of the local paradigm.

### 2.2. Global Citation Score (GCS)
The Global Citation Score of document $i$ is the total citation count recorded across the entire Web of Science or Scopus database:

$$\text{GCS}(i) = \text{Total External Citations}$$

- **Significance**: Reflects broad interdisciplinary visibility across the whole of science.

### 2.3. LCS / GCS Ratio
$$\text{Ratio}(i) = \frac{\text{LCS}(i)}{\text{GCS}(i)}$$
- **High Ratio ($\ge 0.15$)**: The publication is highly domain-specific, representing a core intellectual anchor of the subfield.
- **Low Ratio ($< 0.05$)**: The publication has broad general appeal (e.g., a general statistical methodology or review paper) but fewer internal connections to the immediate local paradigm.

### 2.4. Local Cited References (LCR)
$$\text{LCR}(i) = \sum_{k \in \mathcal{C}, k \ne i} A_{ik}$$
The number of references in document $i$'s bibliography that belong to the local corpus $\mathcal{C}$. Measures how deeply rooted document $i$ is in the established local literature.

---

## 3. Direct Citation Graphs as Directed Acyclic Graphs (DAG)

A direct citation network is modeled as a directed graph $G = (V, E)$, where:
- $V$ is the set of $N$ publications.
- $E$ is the set of directed edges $(u, v)$ indicating that document $u$ is cited by document $v$, or in temporal flow: document $u$ historically precedes and influences document $v$ ($t_u \le t_v$).

Because time flows unidirectionally, a direct citation network is fundamentally a **Directed Acyclic Graph (DAG)**:
1. No cycles exist ($u \to v \to \dots \to u$ is impossible under strict chronological causality).
2. The graph can be **topologically sorted** such that for every directed edge $(u, v)$, $u$ appears before $v$ in the ordering.
3. Node classifications:
   - **Source Nodes ($S$)**: Documents with in-degree $0$ (earliest foundational papers, root ancestors).
   - **Sink Nodes ($T$)**: Documents with out-degree $0$ (most recent empirical publications, leaves).
   - **Intermediate Nodes**: Bridging publications carrying knowledge flow from sources to sinks.

---

## 4. Hummon & Doreian's Main Path Analysis (MPA)

Main Path Analysis (Hummon & Doreian, 1989; Batagelj, 2003; Liu & Lu, 2012) identifies the primary backbone trajectory of scientific progress through the citation DAG.

### 4.1. Search Path Count (SPC)
The Search Path Count algorithm quantifies the importance of each directed citation edge $(u, v)$ by counting the total number of paths from any source node to any sink node that traverse $(u, v)$.

Let:
- $N^-(u)$ be the total number of paths from all source nodes $s \in S$ to node $u$.
- $N^+(v)$ be the total number of paths from node $v$ to all sink nodes $t \in T$.

By topological independence, the total search path count for edge $(u, v)$ is:

$$\text{SPC}(u, v) = N^-(u) \times N^+(v)$$

#### Computation via Topological Dynamic Programming:
1. **Forward Pass (Topological Order)**:
   $$\forall u \in V: \quad N^-(u) = \begin{cases} 1 & \text{if } \text{In-Degree}(u) = 0 \\ \sum_{p \in \text{Pred}(u)} N^-(p) & \text{otherwise} \end{cases}$$
2. **Backward Pass (Reverse Topological Order)**:
   $$\forall v \in V: \quad N^+(v) = \begin{cases} 1 & \text{if } \text{Out-Degree}(v) = 0 \\ \sum_{s \in \text{Succ}(v)} N^+(s) & \text{otherwise} \end{cases}$$
3. **Edge Weight Assignment**:
   $$\text{Weight}(u, v) = N^-(u) \times N^+(v)$$

### 4.2. Main Path Traversal Algorithms

Once edge weights are computed, the principal intellectual trajectory can be extracted using three standard heuristics:

1. **Global Main Path (مسیر اصلی سراسری)**:
   - Finds the complete path from any source node $s \in S$ to any sink node $t \in T$ that maximizes the cumulative sum of edge weights:
     $$\text{Path}^* = \arg\max_{P \in \mathcal{P}(S, T)} \sum_{e \in P} \text{SPC}(e)$$
   - Represents the single most historically consequential evolutionary chain from inception to modern frontiers.

2. **Local Main Path (مسیر اصلی محلی)**:
   - Starts at the source node with the highest outgoing edge weight, and greedily chooses the successor edge with the largest SPC weight at each step until a sink node is reached.
   - Traces the immediate most influential local step taken by scholars at each historical juncture.

3. **Key-Route Main Path (مسیر اصلی کلیدی)**:
   - Anchors the analysis around the edge $(u^*, v^*)$ having the highest overall SPC weight across the entire network (the critical intellectual bottleneck).
   - Traces backward from $u^*$ to the most significant source and forward from $v^*$ to the most significant sink.

---

## 5. Topological Morphologies in Scientific Evolution

Main Path Analysis reveals three fundamental patterns of scientific evolution:

1. **Unilinear Progression (توالی خطی)**:
   - A single unbroken sequence of breakthroughs ($A \to B \to C \to D$). Indicates a unified paradigm accumulating empirical evidence.
2. **Branching / Divergence (انشعاب پارادایمی)**:
   - A node sends major paths to two or more distinct successors ($A \to B$ and $A \to C$). Indicates that a foundational theory branched into separate specialized subfields (e.g., ACT branching into chronic pain vs. workplace burnout).
3. **Convergence / Synthesis (همگرایی و سنتز مفهومی)**:
   - Multiple paths converge onto a single integrative publication ($B \to D$ and $C \to D$). Indicates cross-disciplinary synthesis unifying formerly separate theories.

---

## 6. Chronomap Visual Layout Guidelines (HistCite Style)

1. **Horizontal / Vertical Time Axis**:
   - Time ($Year$) must be strictly ordered along one primary axis (typically X-axis from left to right, or Y-axis top to bottom).
2. **Layered Dispersion within Year**:
   - Publications from the same year are spaced orthogonally to prevent overlapping labels.
3. **Node Sizing & Coloring**:
   - Node size is proportional to $\text{LCS}$ ($\text{Size} = \text{Base} + \text{LCS} \times \text{Factor}$).
   - Color indicates membership in the Main Path (e.g., vibrant crimson/gold) vs. context literature (slate blue).
4. **Directed Arrows**:
   - High-contrast arrows with curvature showing citation dependencies.
   - Highlighted Main Path edges with heavier line width.
