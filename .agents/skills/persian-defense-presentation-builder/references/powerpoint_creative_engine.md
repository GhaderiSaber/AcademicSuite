# PowerPoint Advanced Creative Engine Reference

In high-stakes Master's and PhD defense presentations where faculty demand advanced visual fidelity, deep hypothesis coverage, and supervisor template compliance, activate the **PowerPoint Advanced Creative Engine** via headless COM automation (`win32com.client`) or automated Python-pptx scripting.

---

## 1. Dedicated Hypothesis Architecture (Results & Discussion Chapters)

For complex structural equation models (SEM) and mediation designs, presentations expand to **~40 dedicated widescreen slides**:

### Chapter 4 (Results: Slides 21–26)
- **Slides 21–25 (Direct Paths H1 to H5)**:
  - Split layout featuring a **3D-elevated focal KPI badge** on the left (`x = 0.6 in`, `w = 3.6 in`, `h = 5.65 in`).
  - An RTL SmartArt process flow on the top-right (`x = 4.5 in`, `y = 1.45 in`, `w = 5.7 in`).
  - An empirical structural interpretation card below (`y = 3.0 in`, `h = 4.1 in`).
- **Slide 26 (Mediation & VAF: H6 & H7)**:
  - Top 7-column bootstrap summary table (5,000 resamples, 95% CI).
  - Bottom-right analytical interpretation card.
  - Bottom-left structured APA mini-table for VAF decomposition.

### Chapter 5 (Discussion: Slides 27–33)
- **Slides 27–33 (Dedicated Discussion H1 to H7)**:
  - Top full-width SmartArt mechanism banner (`x = 0.6 in`, `y = 1.4 in`, `w = 9.6 in`, `h = 1.25 in`).
  - Dual deep containers below (`y = 2.8 in`, `h = 4.3 in`):
    - **Right Container**: Theoretical & Psychological Mechanisms.
    - **Left Container**: Literature Concordance & Clinical Implications.

---

## 2. Native PowerPoint SmartArt with Persian RTL & Genuine Font Binding

Standard Python-pptx cannot generate native SmartArt. Inject it via PowerPoint COM automation:

```python
import win32com.client

powerpoint = win32com.client.Dispatch("PowerPoint.Application")
pres = powerpoint.Presentations.Open(pptx_abs_path, WithWindow=False)

# Locate Basic Process layout
basic_process_layout = None
for i in range(1, powerpoint.SmartArtLayouts.Count + 1):
    if powerpoint.SmartArtLayouts.Item(i).Name == "Basic Process":
        basic_process_layout = powerpoint.SmartArtLayouts.Item(i)
        break

# Inject SmartArt shape
sa_shape = slide.Shapes.AddSmartArt(basic_process_layout, left_pts, top_pts, width_pts, height_pts)
sa = sa_shape.SmartArt

# CRITICAL MANDATE 1: Reverse=1 flips arrow direction to Right-to-Left (Persian reading order)
sa.Reverse = 1

# CRITICAL MANDATE 2: Genuine Persian Font Binding on SmartArt Nodes
for n_idx, txt in enumerate(nodes_text):
    if n_idx < sa.AllNodes.Count:
        node = sa.AllNodes.Item(n_idx + 1)
        node.TextFrame2.TextRange.Text = txt
        node.TextFrame2.TextRange.Font.Name = "B Titr"  # Prevent default Calibri Latin fallback
```

---

## 3. Table Cells BiDi Direction & Genuine Persian Font Binding

Tables must maintain pure BiDi stability across all cells:
1. **Container & Paragraph RTL**: Every cell must enforce RTL text frame (`bodyPr.set("rtlCol", "1")`) and paragraph RTL (`pPr.set("rtl", "1")`, `pPr.set("algn", "r")`).
2. **Persian Typography**: Bind Persian cell text runs to `B Nazanin` (body, 11–13 pt) or `B Titr` (headers, 12–14 pt Bold).
3. **Numeric Decoupling**: For numbers and statistical values ($M, SD, \beta, t, F, p$), decouple paragraph semantics to LTR (`rtl="0"`) and font to `Times New Roman` so minus signs precede numbers ($-0.32$, never $0.32-$).

---

## 4. Automatic Slide Transitions & Automatic Entrance Animations

All motion effects must trigger **automatically** to maintain a polished, professional cadence during the defense:

```python
# 1. Automatic SlideShow Transitions
for s in pres.Slides:
    s.SlideShowTransition.EntryEffect = 3844  # ppEffectFade
    s.SlideShowTransition.Duration = 0.5

# 2. Automatic Sequence Entrance Animations on Focal Elements
eff = slide.TimeLine.MainSequence.AddEffect(sa_shape, 10, 0, 1)  # 10 = ppEffectFade
eff.Timing.TriggerType = 3  # msoAnimTriggerAfterPrevious (Triggers automatically after slide entrance)
eff.Timing.Duration = 0.4
```

---

## 5. 3D Shape Beveling & Modern Depth Elevation

Enhance focal KPI summary cards with subtle 3D physical elevation:

```python
for shp in slide.Shapes:
    if shp.HasTextFrame and "شاخص‌های آماری" in shp.TextFrame.TextRange.Text:
        shp.ThreeD.BevelTopType = 4  # msoBevelCircle
        shp.ThreeD.BevelTopDepth = 4
        shp.ThreeD.Depth = 6
```

---

## 6. Zero-Overlap VAF Decomposition Mini-Tables

Never draw freeform floating shapes or progress bars over text containers. Use a clean DrawingML 2-column mini-table:

```python
from pptx.util import Inches

# Place 2-column table cleanly inside the card container
vaf_table_shape = slide.shapes.add_table(5, 2, Inches(0.72), Inches(4.20), Inches(4.26), Inches(2.70))
vaf_table = vaf_table_shape.table
vaf_table.columns[0].width = Inches(2.80)
vaf_table.columns[1].width = Inches(1.46)

# Header
format_table_cell(vaf_table.cell(0, 0), "سازوکار اثر در الگوی ساختاری", COLOR_PRIMARY_BLUE, font_name="B Titr", font_size=11.5, is_bold=True)
format_table_cell(vaf_table.cell(0, 1), "سهم تبیین / وضعیت", COLOR_PRIMARY_BLUE, font_name="B Titr", font_size=11.5, is_bold=True)

# Data Rows with Decoupled LTR Percentages & RTL Descriptions
# Alternating row backgrounds (COLOR_INACTIVE_BG / COLOR_WHITE)
```
