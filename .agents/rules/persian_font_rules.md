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
