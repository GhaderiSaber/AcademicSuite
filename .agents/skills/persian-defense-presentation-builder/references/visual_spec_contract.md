# Visual Specification Contract

Before PowerPoint or HTML rendering, every slide exists as a structured visual specification within `BRIEF.json`. This intermediate representation decouples slide semantics from physical layout rendering.

---

## Slide Specification Schema

```json
{
  "slide_id": "s16",
  "size": "16:9",
  "background": "light",
  "section": "یافته‌ها",
  "title": "دو مسیر میانجی هر دو معنادار هستند",
  "message": "اثر غیرمستقیم از هر دو مسیر آگاهی هیجانی و احساس انسجام عبور می‌کند.",
  "layout_family": "mediation_diagram",
  "elements": [
    {
      "type": "node",
      "id": "trauma",
      "label": "ترومای دوران کودکی"
    },
    {
      "type": "node",
      "id": "ea",
      "label": "آگاهی هیجانی"
    },
    {
      "type": "node",
      "id": "soc",
      "label": "احساس انسجام"
    },
    {
      "type": "node",
      "id": "risk",
      "label": "رفتارهای پرخطر"
    },
    {
      "type": "path",
      "from": "trauma",
      "to": "ea",
      "label": "β = −0.50"
    },
    {
      "type": "path",
      "from": "trauma",
      "to": "soc",
      "label": "β = −0.59"
    },
    {
      "type": "path",
      "from": "ea",
      "to": "risk",
      "label": "β = −0.44"
    },
    {
      "type": "path",
      "from": "soc",
      "to": "risk",
      "label": "β = −0.40"
    },
    {
      "type": "kpi",
      "label": "Total indirect",
      "value": "β = 0.456"
    }
  ],
  "source_refs": ["chapter4/table23", "chapter4/table24"]
}
```

---

## Core Layout Families
- `big_idea`: Single dominant statement with supporting badge.
- `funnel`: Multi-stage problem or sampling narrowing.
- `comparison_table`: Side-by-side or multi-column instrument/variable breakdown.
- `method_process`: Horizontal step-by-step procedural flow.
- `result_spotlight`: Dominant focal statistic paired with structured interpretation.
- `mediation_diagram`: Structural equation path model with bootstrap indices.
- `mechanism_banner`: Full-width process flow banner paired with dual deep containers.
