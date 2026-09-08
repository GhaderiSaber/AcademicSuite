# Bibliometric Science Mapping & Callon's Strategic Diagram Standards

This reference document defines the mathematical models, network centrality algorithms, clustering heuristics, and VOSviewer file standards implemented in the **`bibliometric-network-analyst`** skill of the **AcademicSuite**.

---

## 1. Theoretical Laws of Bibliometrics

Bibliometric analysis in academic theses and peer-reviewed literature rests upon three classical empirical laws:

1. **Lotka's Law (Author Productivity)**:
   The frequency of authors $y$ making $x$ contributions is inversely proportional to $x^2$:
   $$y = \frac{C}{x^n} \quad (n \approx 2)$$
   A small elite core of scholars produces the majority of high-impact publications.
2. **Bradford's Law (Journal Scattering)**:
   When scientific journals are sorted by descending productivity for a given field, they can be divided into a core zone of highly productive journals and peripheral zones containing the same total number of articles:
   $$1 : n : n^2$$
   - **Zone 1 (Core)**: Nuclear journals holding $\approx 33\%$ of the literature.
   - **Zone 2**: Secondary journals holding $\approx 33\%$.
   - **Zone 3**: Broad peripheral journals holding $\approx 33\%$.
3. **Zipf's Law (Word Frequencies)**:
   The frequency $f$ of a keyword is inversely proportional to its rank $r$ in the frequency table:
   $$f(r) \propto \frac{1}{r^s} \quad (s \approx 1)$$

---

## 2. Co-Occurrence Normalization & Similarity Metrics

In keyword co-occurrence analysis, raw co-occurrence frequency $c_{ij}$ is normalized to eliminate the confounding effect of high marginal frequencies:

### 2.1. Association Strength (Van Eck & Waltman, 2009 - VOSviewer Standard)
$$s_{ij} = \frac{2m \cdot c_{ij}}{w_i \cdot w_j}$$
where:
- $c_{ij}$ is the number of co-occurrences of items $i$ and $j$.
- $w_i = \sum_{k} c_{ik}$ is the total link strength of item $i$.
- $m = \frac{1}{2} \sum_{i} w_i$ is the total number of edges in the network.

### 2.2. Salton's Cosine Equivalence Index (Callon et al., 1991)
$$\text{Equiv}_{ij} = \frac{c_{ij}^2}{c_i \cdot c_j}$$
where $c_i$ and $c_j$ are the total frequencies of items $i$ and $j$.

### 2.3. Jaccard Similarity Index
$$J_{ij} = \frac{c_{ij}}{c_i + c_j - c_{ij}}$$

---

## 3. Network Topology & Centrality Metrics

To quantify the structural role of keywords and authors in the intellectual network:

1. **Degree Centrality ($k_i$)**:
   The number of direct links incident upon node $i$:
   $$k_i = \sum_{j=1}^N A_{ij}$$
   Reflects local prominence and citation volume.
2. **Betweenness Centrality ($C_B(v)$)**:
   The fraction of all shortest paths between pairs of nodes that pass through node $v$:
   $$C_B(v) = \sum_{s \ne v \ne t} \frac{\sigma_{st}(v)}{\sigma_{st}}$$
   Nodes with high betweenness act as **intellectual bridges** mediating conceptual flow between distinct research paradigms.
3. **Closeness Centrality ($C_C(v)$)**:
   The reciprocal of the sum of the shortest path distances from node $v$ to all other nodes:
   $$C_C(v) = \frac{N - 1}{\sum_{u \ne v} d(v, u)}$$
   Reflects how quickly an idea spreads throughout the field.
4. **Modularity Community Detection ($Q$)**:
   Partitions the network into densely connected thematic clusters:
   $$Q = \frac{1}{2m} \sum_{ij} \left[ A_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)$$

---

## 4. Callon's Strategic Diagram (Cobo et al., 2011)

Callon's Strategic Diagram evaluates research clusters on a two-dimensional Cartesian plane:

$$\begin{aligned}
\text{Callon's Centrality (C)} &= 10 \times \sum e_{kh} \quad (k \in \text{Cluster}, h \notin \text{Cluster}) \\
\text{Callon's Density (D)} &= 100 \times \frac{\sum e_{ij}}{N_c} \quad (i, j \in \text{Cluster})
\end{aligned}$$

```
                Density (Internal Maturity / پیوستگی درونی)
                               ▲
             Quadrant II       │       Quadrant I
          Niche Themes         │      Motor Themes
      (مباحث تخصصی و حاشیه‌ای)    │     (موتورهای محرک پژوهش)
                               │
     ──────────────────────────┼──────────────────────────► Centrality
                               │    (External Importance / برجستگی بیرونی)
            Quadrant III       │       Quadrant IV
     Emerging/Declining Themes │      Basic Themes
     (مباحث نوظهور یا رو به زوال) │    (مفاهیم پایه و بنیادین)
                               │
```

### Interpretation of Quadrants:
1. **Quadrant I (Motor Themes / موتور محرک)**:
   - High Centrality, High Density.
   - Core research frontiers that are both internally mature and well-connected to the broader literature.
2. **Quadrant II (Niche / Highly Developed Themes / مباحث تخصصی و حاشیه‌ای)**:
   - Low Centrality, High Density.
   - Specialized research niches with strong internal cohesion but limited interaction with outside domains.
3. **Quadrant III (Emerging or Declining Themes / مباحث نوظهور یا رو به زوال)**:
   - Low Centrality, Low Density.
   - Weak internal links and peripheral position. Requires temporal citation analysis to distinguish emerging trends from dying topics.
4. **Quadrant IV (Basic and Transversal Themes / مفاهیم پایه و بین‌رشته‌ای)**:
   - High Centrality, Low Density.
   - Fundamental cross-cutting constructs (e.g., anxiety, methodology, depression) that underpin the entire field but lack dense internal specialization.

---

## 5. VOSviewer Native File Formats

`bibliometric-network-analyst` exports datasets in exact VOSviewer tab-delimited format:

### 5.1. Map File (`vosviewer_map.txt`):
```text
id	label	x	y	cluster	weight<Total link strength>	weight<Occurrences>
1	Acceptance and Commitment Therapy	0.245	-0.118	1	48	18
2	Psychological Flexibility	0.198	-0.082	1	42	15
3	Cognitive Reappraisal	-0.312	0.412	2	35	12
```

### 5.2. Network File (`vosviewer_network.txt`):
```text
source	target	strength
1	2	8
1	3	4
2	3	3
```
