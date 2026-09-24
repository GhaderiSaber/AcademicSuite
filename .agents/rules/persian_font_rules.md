# Persian Academic Typography & OpenXML Technical Specification (Directives 4, 4.1, 5)

Comprehensive OpenXML Word and PowerPoint typography specification across AcademicSuite deliverables.

---

## 1. Persian Font & Hierarchy Standards

| Document Element | Primary Persian Font | Latin / Stats Font | Size (pt) | Weight | Alignment & BiDi |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Document Title / Cover** | `B Titr` | — | 16–18 pt | Bold | Center (`<w:jc w:val="center"/>`) + RTL |
| **Heading 1 / Chapter Titles** | `B Titr` | — | 14–16 pt | Bold | Right (`<w:jc w:val="right"/>`) + RTL |
| **Headings 2 & 3** | `B Titr` / `B Nazanin Bold` | — | 12–13.5 pt | Bold | Right (`<w:jc w:val="right"/>`) + RTL |
| **Body Paragraphs** | `B Nazanin` | `Times New Roman` | 13–14 pt | Regular | Justified (`<w:jc w:val="both"/>`) + RTL |
| **Table Headers** | `B Titr` | `Times New Roman` | 10–11 pt | Bold | Center (`<w:jc w:val="center"/>`) |
| **Table Cells (Text)** | `B Nazanin` | — | 10–10.5 pt | Regular | Right / Justified |
| **Table Cells (Numbers / Stats)** | — | `Times New Roman` | 10–10.5 pt | Regular / Italic | Center + LTR (`rtl="0"`) |

---

## 2. Word OpenXML Binding Protocol (`.docx`)

### 2.1 Text Direction & Font Slots
- **Paragraph Direction**: `<w:bidi w:val="1"/>` in `<w:pPr>`.
- **Table Direction**: `<w:bidiVisual/>` in `<w:tblPr>`.
- **Dual Font Slot Binding**:
  ```python
  def set_run_fonts(run, cs_font='B Nazanin', size_pt=13, bold=False, italic=False, is_english=False):
      rPr = run._r.get_or_add_rPr()
      rFonts = rPr.get_or_add_rFonts()
      if is_english:
          run.font.name = 'Times New Roman'
          rFonts.set(qn('w:ascii'), 'Times New Roman')
          rFonts.set(qn('w:hAnsi'), 'Times New Roman')
          rFonts.set(qn('w:cs'), cs_font)
      else:
          run.font.name = cs_font
          rFonts.set(qn('w:ascii'), cs_font)
          rFonts.set(qn('w:hAnsi'), cs_font)
          rFonts.set(qn('w:cs'), cs_font)
          rFonts.set(qn('w:hint'), 'cs')
          rtl = OxmlElement('w:rtl')
          rtl.set(qn('w:val'), '1')
          rPr.append(rtl)
      if size_pt:
          run.font.size = Pt(size_pt)
          szCs = OxmlElement('w:szCs')
          szCs.set(qn('w:val'), str(int(size_pt * 2)))
          rPr.append(szCs)
      if bold:
          run.bold = True
          bCs = OxmlElement('w:bCs')
          bCs.set(qn('w:val'), '1')
          rPr.append(bCs)
  ```

### 2.2 Core Word Invariants
- **Zero Manual Breaks (`<w:br/>`)**: Never use manual breaks or `\n` in justified text runs. Every line, bullet, or block must be an independent `<w:p>` paragraph mark. [Enforcement: `academic_writer_guard.py`]
- **Native OpenXML Footnotes**: Footnotes must compile to native elements (`word/footnotes.xml` and `<w:footnoteReference>`), never simulated plain text. [Enforcement: `academic_writer_guard.py`]
- **Decoupled Negative Numbers**: Enforce LTR (`rtl="0"`) on numeric data cells so negative signs precede digits ($-0.32$).
- **Preserve Native OMML Math**: Preserve `<m:oMath>` equations; never overwrite formulas via naive text assignments.

---

## 3. PowerPoint DrawingML Protocol (`.pptx`)

### 3.1 Dual-Slot Font Binding (Missing Glyph Prevention)
```python
def set_pptx_font(run, font_name="B Nazanin", size_pt=14, bold=False):
    run.font.name = "Times New Roman"  # Protects Latin slot
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    rPr = run._r.get_or_add_rPr()
    rPr.set("lang", "fa-IR")
    cs = parse_xml(f'<a:cs xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" typeface="{font_name}"/>')
    rPr.append(cs)
```

### 3.2 Slide Typography & Visual Boundaries
- **Direction Controllers**: Enforce `rtlCol="1"` on `bodyPr` and `rtl="1"` on paragraph properties `<a:pPr>`.
- **Widescreen Legibility**: Headers $\ge 24$ pt Bold, body text $\ge 14$ pt Regular.
- **Zero Emojis**: Emojis are strictly prohibited in academic presentations and deliverables. [Enforcement: `persian_defense_presentation_builder`]
- **Zero Inline English in Persian Narrative**: Foreign author names transliterated phonetically to Persian with footnotes.
