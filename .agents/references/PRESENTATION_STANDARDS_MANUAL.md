# PRESENTATION_STANDARDS_MANUAL.md — Academic Defense Presentation Standards

This manual provides the technical specifications, DrawingML XML structures, and COM automation requirements for Persian academic defense presentations (`.pptx` and HTML slides).

---

## 1. Directionality & Typography Rules
1. **Academic Tone Sobriety**:
   - Zero emojis in slides, cards, or notes.
   - Zero English words in Persian slides (use «مسیرهای مستقیم»، «یافته آماری»، «سازوکارهای تبیین نظری»).
   - Latin characters permitted strictly for statistical notation (*M, SD, t, F, p, β, z*) and fit indices ($\chi^2/df, \text{RMSEA}, \text{CFI}, \text{TLI}, \text{SRMR}$) in `Times New Roman` italic.
2. **Fit Indices Acronym Non-Reversal**:
   - In PowerPoint DrawingML BiDi text, Latin statistical acronyms must NEVER be inside `lang="fa-IR"`.
   - Emit as a decoupled Left-to-Right run (`lang="en-US"` in `Times New Roman` with zero complex script tags) to prevent character/word reversal.
3. **Negative Number Decoupling**:
   - In table numeric cells, enforce LTR paragraph semantics (`rtl="0"`) and `lang="en-US"` so minus signs precede numbers ($-0.32$, not $0.32-$).

---

## 2. DrawingML Dual-Slot Font Binding (Box Prevention)
In PowerPoint DrawingML (`.pptx`), traditional Persian fonts lack ASCII/Latin glyphs. If assigned to `<a:latin>`, English text renders as square boxes (`□□□`).
Always bind font slots independently:
```xml
<a:rPr lang="fa-IR">
  <a:cs typeface="B Nazanin"/>
  <a:latin typeface="Times New Roman"/>
  <a:ea typeface="B Nazanin"/>
</a:rPr>
```

---

## 3. Widescreen Legibility Scale (16:9)
- **Slide Header Title**: 24–28 pt Bold (`B Titr`)
- **Slide Subtitle**: 13–14 pt Regular (`B Nazanin`)
- **Card / Container Titles**: 16–18 pt Bold (`B Titr`)
- **Body Narrative / Bullets**: 14–15 pt Regular (`B Nazanin`) — never below 14 pt in widescreen.
- **Table Cell Text**: 12–14 pt.

---

## 4. Native PowerPoint SmartArt & Automatic Motion
1. **Mandatory RTL Reversal**: When generating process flows, set `SmartArt.Reverse = 1` so arrows point Right-to-Left ($\leftarrow$).
2. **Font Binding in SmartArt**: All text nodes must bind to `node.TextFrame2.TextRange.Font.Name = "B Titr"` or `"B Nazanin"`.
3. **Automatic Transitions & Animations**:
   - Set Fade transitions: `SlideShowTransition.EntryEffect = 3844`, duration 0.5s.
   - Entrance animations must trigger automatically (`msoAnimTriggerAfterPrevious` or `msoAnimTriggerWithPrevious`).
4. **3D Shape Elevation & Beveling**: Apply `ThreeD.BevelTopType = 4`, `ThreeD.Depth = 6` to focal statistical plaques.
5. **Zero-Overlap Mini-Table Policy**: For variance accounted for (VAF) and effect decomposition, use a 2-column DrawingML mini-table with alternating fills instead of freeform floating progress bars.
