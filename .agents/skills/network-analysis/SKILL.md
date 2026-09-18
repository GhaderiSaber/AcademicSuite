---
name: network-analysis
description: Construct and analyze bibliometric, keyword co-occurrence, and citation networks, computing Callon centrality-density coordinates and VOSviewer exports. Consolidated alias pointing to bibliometric-network-analyst and citation-network-visualizer.
---

# Network Analysis Skill (Consolidated Alias)

> [!NOTE]
> **Skill Consolidation Notice**:
> This capability has been consolidated into two comprehensive skills:
> 1. **`bibliometric-network-analyst`**: For science mapping, keyword co-occurrence, Callon centrality-density diagrams, Bradford/Lotka laws, and VOSviewer file exports.
> 2. **`citation-network-visualizer`**: For citation, co-citation, and bibliographic coupling network topology and 300-DPI publication graphs.

---

## 1. WHEN TO USE (Activation Criteria)
Activate this skill or its parent consolidated skills when:
- Conducting science mapping or keyword co-occurrence network analysis.
- Calculating Callon centrality and Callon density to classify thematic motor vs. isolated clusters.

## 2. PRIMARY ALTERNATIVES
- For bibliometric science mapping and VOSviewer maps $\to$ use `bibliometric-network-analyst`.
- For citation networks and graph metrics $\to$ use `citation-network-visualizer`.

## 3. DETERMINISTIC CLI RUNNER
Legacy CLI command retained for backward compatibility:
```bash
python3 .agents/skills/network-analysis/scripts/run_network_analysis.py \
  --corpus "harvested_papers.json" \
  --output "bibliometric_map.json"
```
