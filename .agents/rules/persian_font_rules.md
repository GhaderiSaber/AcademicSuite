# Persian Typography & Font Binding Standards for Documents

## 📌 Context & Directive
In academic and professional deliverables, documents written in Persian must display authentic Persian typography rather than defaulting to generic Latin or Arabic fallback fonts (such as Times New Roman Arabic fallback glyphs, Calibri, or Arial).

Whenever an AI agent generates, modifies, or inspects Microsoft Word documents (`.docx`), presentations (`.pptx`), or reports containing Persian text, the agent **MUST** enforce genuine Persian fonts and full OpenXML Right-to-Left (BiDi) binding.

---

## 🏛️ 1. Persian Font Hierarchy

| Document Element | Primary Persian Font | Size (pt) | Weight | Alignment |
| :--- | :--- | :--- | :--- | :--- |
| **Document Title / Cover** | `B Titr` | 16–18 pt | Bold | Center |
| **Heading 1 / Chapter Titles** | `B Titr` | 14–16 pt | Bold | Right / Center |
| **Headings 2 & 3** | `B Titr` or `B Nazanin Bold` | 12–13.5 pt | Bold | Right |
| **Body Paragraphs & Text** | `B Nazanin` | 12–13 pt | Regular | Justified (تراز کامل) |
| **Table Headers** | `B Titr` | 10–11 pt | Bold | Center |
| **Table Data / Cells** | `B Nazanin` | 10–10.5 pt | Regular / Bold for labels | Center / Right |
| **Callouts & Speaker Speeches** | `B Nazanin` | 11.5–12 pt | Regular | Justified |
| **Pure Latin Terms & Statistics** | `Times New Roman` | 10–11 pt | Italic for symbols ($M, SD, t, F, p$) | Inline / LTR |

---

## ⚙️ 2. OpenXML Technical Protocol in Word (`.docx`)

### 2.1 The Fallback Trap (`w:ascii="Times New Roman"`)
When writing Persian text into python-docx, naive code often sets:
```python
# ❌ INCORRECT: Causes Microsoft Word on Windows to render Persian text using Times New Roman Arabic fallback!
rFonts.set(qn('w:ascii'), 'Times New Roman')
rFonts.set(qn('w:cs'), 'B Nazanin')
```
In Microsoft Word on Windows, if `w:ascii` is set to `Times New Roman` without explicit complex-script binding, Word's font dropdown shows "Times New Roman" and may substitute genuine Persian glyphs with ugly fallback characters.

### 2.2 The Correct OpenXML Binding Protocol
For all Persian text runs, agents **MUST** execute:
```python
def set_run_fonts(run, cs_font='B Nazanin', size_pt=12, bold=False, italic=False, color_rgb=None, is_english=False):
    rPr = run._r.get_or_add_rPr()
    fa_font = cs_font if cs_font else 'B Nazanin'
    
    if is_english:
        run.font.name = 'Times New Roman'
        rFonts = rPr.get_or_add_rFonts()
        rFonts.set(qn('w:ascii'), 'Times New Roman')
        rFonts.set(qn('w:hAnsi'), 'Times New Roman')
        rFonts.set(qn('w:cs'), fa_font)
    else:
        # 1. Assign run.font.name so Word UI shows genuine Persian font
        run.font.name = fa_font
        rFonts = rPr.get_or_add_rFonts()
        
        # 2. Bind Persian font across ALL font slots
        rFonts.set(qn('w:ascii'), fa_font)
        rFonts.set(qn('w:hAnsi'), fa_font)
        rFonts.set(qn('w:cs'), fa_font)
        rFonts.set(qn('w:hint'), 'cs')
        
        # 3. Enforce Right-to-Left (RTL) run property
        if not rPr.findall(qn('w:rtl')):
            rtl = OxmlElement('w:rtl')
            rtl.set(qn('w:val'), '1')
            rPr.append(rtl)
            
    # 4. Complex script size (<w:szCs>) and bold (<w:bCs>)
    if size_pt is not None:
        run.font.size = Pt(size_pt)
        sz_val = str(int(size_pt * 2))
        szCs = OxmlElement('w:szCs')
        szCs.set(qn('w:val'), sz_val)
        rPr.append(szCs)
        
    if bold:
        run.bold = True
        bCs = OxmlElement('w:bCs')
        bCs.set(qn('w:val'), '1')
        rPr.append(bCs)
        
    if italic:
        run.font.italic = True
        iCs = OxmlElement('w:iCs')
        iCs.set(qn('w:val'), '1')
        rPr.append(iCs)
```

### 2.3 Document-Level Style Defaults
Always configure `doc.styles['Normal']` upon document initialization with RTL direction and Justified alignment:
```python
normal_style = doc.styles['Normal']
normal_style.font.name = 'B Nazanin'
normal_style.font.size = Pt(12)
normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

pPr_norm = normal_style._element.get_or_add_pPr()
bidi_norm = OxmlElement('w:bidi')
bidi_norm.set(qn('w:val'), '1')
pPr_norm.append(bidi_norm)

jc_norm = OxmlElement('w:jc')
jc_norm.set(qn('w:val'), 'both')
pPr_norm.append(jc_norm)

rPr_norm = normal_style._element.get_or_add_rPr()
rFonts_norm = OxmlElement('w:rFonts')
rFonts_norm.set(qn('w:ascii'), 'B Nazanin')
rFonts_norm.set(qn('w:hAnsi'), 'B Nazanin')
rFonts_norm.set(qn('w:cs'), 'B Nazanin')
rFonts_norm.set(qn('w:hint'), 'cs')
rPr_norm.append(rFonts_norm)

rtl_norm = OxmlElement('w:rtl')
rtl_norm.set(qn('w:val'), '1')
rPr_norm.append(rtl_norm)
```

### 2.4 Dual Control: Text Direction (BiDi) vs. Text Alignment (Justification)
Microsoft Word features two independent controls for text formatting:
1. **Text Direction (جهت متن / BiDi)**:
   - Sets reading order, punctuation behavior, and cursor navigation.
   - **MUST ALWAYS be Right-to-Left (RTL)** for Persian.
   - Inject `<w:bidi w:val="1"/>` into `<w:pPr>` and `<w:rtl w:val="1"/>` into `<w:rPr>`.
   - Never confuse Right-alignment with true RTL Text Direction! Leaving direction LTR breaks sentence-final periods, parentheses, and numerals.
2. **Text Alignment (تراز متن / Justification)**:
   - **MUST JUSTIFY all substantive Persian text** (`paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY` / `<w:jc w:val="both"/>`).
   - Body paragraphs, research descriptions, literature reviews, candidate speeches, callout texts, and multi-line answers must always be justified from both margins. Never leave Persian text ragged on the left.
   - Document/cover titles: Centered (`WD_ALIGN_PARAGRAPH.CENTER`) with RTL direction.
   - Section headings & short labels: Right-aligned (`WD_ALIGN_PARAGRAPH.RIGHT`) with RTL direction.
3. **Table Directionality**:
   - Tables: inject `<w:bidiVisual/>` into `<w:tblPr>` so column order starts from the right.
4. **Persian Typography**:
   - Maintain Persian zero-width non-joiners (نیم‌فاصله: `\u200c`) in compound words (e.g., `می‌شود`, `پیش‌آزمون`, `یافته‌ها`).

### 2.5 Zero Manual Line Breaks Policy (قاعده منع شکست دستی خط / Shift+Enter)
- **CRITICAL DIRECTIVE**: **NEVER USE MANUAL LINE BREAKS (`<w:br/>` / Shift+Enter / `\n` in text runs). USE PARAGRAPH MARKS (`<w:p>`) EVERYWHERE.**
- **Why this is catastrophic in Justified text**:
  In Microsoft Word, when a paragraph has Justified alignment (`<w:jc w:val="both"/>`), Word distributes spaces evenly across the entire line so that both left and right edges align with the margins. If a line ends with a manual line break (`<w:br/>`), Word treats it as an internal continuation line of the paragraph and forces the line to justify across the full margin width, creating absurdly wide gaps between characters and words. Only a true paragraph mark (`<w:p>`) signals the legitimate end of a paragraph block, allowing Word's justification engine to naturally format the final line unstretched.
- **Implementation Standards**:
  1. Never concatenate lines with `\n` inside `p.add_run("Line 1\nLine 2")`. Every line, prompt, metadata entry, quote, bullet, or speaking script MUST be instantiated as an independent paragraph object (`doc.add_paragraph()` or `cell.add_paragraph()`).
  2. Spacing between elements must be controlled exclusively through paragraph formatting properties (`p.paragraph_format.space_before = Pt(...)`, `p.paragraph_format.space_after = Pt(...)`), never by inserting empty paragraphs containing `\n` or manual breaks.
  3. Every paragraph MUST receive explicit RTL direction (`set_rtl(p, align=...)`) and appropriate alignment (`both` for substantive text, `right` for headers, `center` for titles).

### 2.6 Table Formatting Protocol (Font, Direction, Alignment & Paragraph Marks)
1. **Fonts in Tables**:
   - Column & Row Headers / Category Labels: `B Titr` (10–11 pt Bold, Centered or Right-aligned).
   - Data / Body Cells: `B Nazanin` (10–10.5 pt Regular, Line Spacing 1.15–1.2).
   - Latin Terms & Statistical Symbols: `Times New Roman` (10–10.5 pt, Italic for $M, SD, t, F, p, \beta$).
   - Full OpenXML binding (`w:ascii`, `w:hAnsi`, `w:cs` set to Persian font name, `w:hint="cs"`, `<w:rtl w:val="1"/>`, `<w:szCs>`, `<w:bCs>`).
2. **Direction & Alignment in Tables**:
   - Always inject `<w:bidiVisual/>` into `<w:tblPr>` so column order starts Right-to-Left.
   - Inject `<w:bidi w:val="1"/>` into `<w:pPr>` and `<w:rtl w:val="1"/>` into `<w:rPr>` for EVERY paragraph in EVERY table cell.
   - Headers: Center (`center`) or Right (`right`) alignment.
   - Narrative & Multi-line cell text: **MUST BE JUSTIFIED** (`<w:jc w:val="both"/>`).
   - Short status badges / numeric codes: Center (`center`) alignment.
3. **Paragraph Marks in Tables (Zero Manual Line Breaks)**:
   - **NEVER use manual line breaks (`<w:br/>` / `\n`) inside table cells**.
   - Every bullet item, script paragraph, note, cue, or sub-entry inside a cell MUST be created as an independent paragraph object (`cell.add_paragraph()` / `<w:p>`).
   - Spacing between cell paragraphs must be regulated via `p.paragraph_format.space_after = Pt(...)`.

### 2.7 Header & Heading Protocol (Font, Direction & Paragraph Marks)
1. **Fonts in Headings**:
   - Document Title / Cover Header: `B Titr` (16–18 pt Bold, Centered).
   - Level 1 Section / Chapter Headings: `B Titr` (14–16 pt Bold, Right-aligned).
   - Level 2 & 3 Headings (Slide Titles, Question Headings, Rule Titles): `B Titr` (12–13.5 pt Bold, Right-aligned).
   - Section Sub-labels, Question Prompts & Callout Titles: `B Titr` (10.5–11.5 pt Bold, Right-aligned).
2. **Direction & Alignment in Headings**:
   - All headings MUST enforce RTL text direction (`<w:bidi w:val="1"/>` in `pPr` and `<w:rtl w:val="1"/>` in `rPr`).
   - Cover/Document Titles: Centered (`center`) with RTL.
   - Section/Slide/Question Headings: Right-aligned (`right`) with RTL.
3. **Paragraph Marks in Headings**:
   - Every heading, title, and subtitle MUST be its own independent paragraph object (`<w:p>`).
   - NEVER use manual line breaks (`<w:br/>` / `\n`) inside headings.
   - Spacing above and below headings must be controlled via `p.paragraph_format.space_before` and `space_after` in `Pt(...)`.

