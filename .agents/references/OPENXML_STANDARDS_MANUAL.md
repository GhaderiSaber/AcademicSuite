# Persian Academic Typography & OpenXML Technical Specification

### Directive 5: Persian Academic Typography & OpenXML Standards
When assembling or editing Persian Word documents (`.docx`):

| Control Feature | Persian Requirement | OpenXML Implementation |
| :--- | :--- | :--- |
| **Text Direction (جهت متن / BiDi)** | Right-to-Left (RTL) | `<w:bidi w:val="1"/>` in paragraph properties (`<w:pPr>`), `<w:rtl w:val="1"/>` in text run properties (`<w:rPr>`), and `<w:bidiVisual/>` in table properties (`<w:tblPr>`). |
| **Text Alignment (تراز متن / Justification)** | Justified (both) | Substantive narrative text (paragraphs, literature reviews, descriptions, candidate answers, callouts) must enforce `paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY` / `<w:jc w:val="both"/>`. Centered for banners (`<w:jc w:val="center"/>`). For Right-aligned headings/labels: omit `<w:jc>` under `<w:bidi w:val="1"/>` to prevent Word's trailing-edge flip to Align Left, or set `<w:jc w:val="both"/>` for justified. |
| **Persian Font Binding & Complex-Script Attributes** | Genuine Persian Fonts | Binds `w:ascii`, `w:hAnsi`, `w:cs`, and `w:eastAsia` to genuine Persian fonts (`B Nazanin` or `B Titr`) with `w:hint="cs"`, `<w:szCs>`, and `<w:bCs>` to avoid fallback Arabic Naskh rendering in Microsoft Word for Windows. |

- **Mandatory True Persian Font Binding**:
  - When writing Persian text in Word (`.docx`), agents **MUST** strictly adhere to the following font hierarchy:
    - **Chapter Names ONLY** (e.g., Chapter 1, Chapter 2): `B Titr` (Centered, RTL).
    - **All Other Headings** (Headings 2 & 3, Sub-labels): `B Nazanin Bold`.
    - **Body Paragraphs, Descriptions & Callouts**: `B Nazanin` strictly at **14 pt** (Regular, Line Spacing 1.15–1.3, Justified).
    - **Pure Latin Numbers, English Terms & Statistical Symbols** ($M, SD, t, F, p, \beta, \text{RMSEA}$): `Times New Roman` (10–11 pt).
  - **OpenXML Persian Font Binding Protocol**:
    - For all Persian text runs, agents **MUST** set `w:ascii`, `w:hAnsi`, `w:cs`, and `w:eastAsia` to the designated Persian font (`B Nazanin` or `B Titr`), AND set `w:hint="cs"`.
    - **NEVER** bind `w:ascii="Times New Roman"` to Persian text runs; doing so causes Microsoft Word on Windows to render Persian characters using Times New Roman's Arabic Naskh fallback glyphs instead of genuine Persian typography.
    - Always inject `<w:rtl w:val="1"/>` into the run's `<w:rPr>` to force Right-to-Left script direction.
    - Always inject `<w:szCs w:val="{half_pts}"/>` and `<w:bCs w:val="1"/>` to guarantee that font size and bold weight are applied to complex-script Persian glyphs in Microsoft Word.
    - Explicitly set `run.font.name` to the Persian font name so Word's ribbon and font dropdown identify the active Persian font immediately.
- **BiDi & OpenXML Directionality & Mandatory Text Justification**:
  - **Dual Control in Microsoft Word (Text Direction vs. Text Alignment)**:
    - Microsoft Word provides two distinct controls for text:
      1. **Text Direction (جهت متن / BiDi)**: Controls the reading flow, punctuation placement, and cursor movement. In Persian, **Text Direction MUST ALWAYS be Right-to-Left (RTL)**. In OpenXML, this requires injecting `<w:bidi w:val="1"/>` into `<w:pPr>`, `<w:rtl w:val="1"/>` into `<w:rPr>`, and `<w:bidiVisual/>` into `<w:tblPr>`. Setting alignment to Right while leaving text direction LTR is an error that breaks sentence-final dots, parentheses, and punctuation.
      2. **Text Alignment (تراز متن / Justification)**: In Persian, agents **MUST JUSTIFY all substantive narrative text** (`paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY` / `<w:jc w:val="both"/>`), including body paragraphs, descriptions, literature reviews, candidate speeches, callouts, and multi-line answers. Never leave Persian narrative text ragged on the left side.
      3. **The BiDi Alignment Inversion Rule (Architecture Learned from Proposal Skill)**:
         - Under Word's BiDi text engine, adding `<w:bidi w:val="1"/>` makes the paragraph's natural leading-edge alignment **RIGHT**.
         - If `<w:jc w:val="right"/>` is explicitly added to an RTL paragraph, Word treats `w:val="right"` as the trailing edge, causing Word on macOS/Windows and LibreOffice Writer to flip the alignment to **ALIGN LEFT (چپ‌چین)**! Symptoms include headings and captions aligned to the far left of the page in LibreOffice Writer, and the top ruler starting at 0 on the left.
         - **The Golden Rule for RTL Right-Aligned Text (Headings, Headers, Labels)**:
           - Enforce `<w:bidi w:val="1"/>` for RTL Direction.
           - **OMIT** `<w:jc>` entirely for Right Alignment so Word naturally and strictly aligns text to the RIGHT.
           - For Justified narrative text: emit `<w:jc w:val="both"/>`.
           - For Centered titles and banners: emit `<w:jc w:val="center"/>`.
           - For LTR English references: omit `<w:bidi>` and emit `<w:jc w:val="left"/>`.
      4. **Strict Child Element Sequencing (`CT_PPr`)**:
         - Under ISO/IEC 29500-1 / ECMA-376, child elements in `<w:pPr>` must strictly follow this exact order:
           `w:pStyle` $\to$ `w:keepNext` $\to$ `w:bidi` $\to$ `w:spacing` $\to$ `w:ind` $\to$ `w:jc`
      5. **Section-Level BiDi & Modern Word Compatibility**:
         - Every section in `<w:sectPr>` must contain `<w:bidi/>`. Missing this can cause physical left alignment issues.
         - In `word/settings.xml`, ensure `compatibilityMode = 15` (Word 2013+ modern BiDi layout engine).
         - In `word/styles.xml`, inject RTL directionality (`<w:bidi w:val="1"/>`, `<w:rtl/>`) and genuine Persian font definitions (`B Titr` / `B Nazanin`) into `Normal`, `Heading1`, `Heading2`, `Heading3`, `Heading4`, and `FootnoteReference`.
      6. **Language Proofing & Script Binding Tag**:
         - All Persian text runs must include `<w:lang w:val="fa-IR" w:bidi="fa-IR"/>` to guarantee correct Persian ligatures, vowel placement, and proofing without red squiggly lines or Arabic fallback rendering.
      7. Document default style (`Normal`): Must enforce `paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY` and `<w:bidi w:val="1"/>` with `<w:jc w:val="both"/>`.
  - Always enforce `<w:bidiVisual/>` on tables (`<w:tblPr>`).
  - Maintain Persian half-spaces (نیم‌فاصله: `\u200c`) in compound words (e.g., `می‌شود`, `پیش‌آزمون`, `یافته‌ها`, `روان‌شناختی`).
- **Mandatory Scholarly Prose (No Bulleted Narrative)**:
  - **Narrative Continuity**: All thesis findings and scholarly narratives must flow as continuous, cohesive academic paragraphs.
  - **Prohibition of Lists**: The use of bullet points (`•`), numbered breakdowns (`1.`), or hyphenated lists (`-`) is strictly prohibited in the narrative body. Presentation-style fragmentation fundamentally violates the formal register of a dissertation.
- **Zero Manual Line Breaks Policy (قاعده منع شکست دستی خط / Shift+Enter)**:
  - **NEVER use manual line breaks (`<w:br/>` / `\n` in run text)**.
  - **USE PARAGRAPH MARKS (`<w:p>`) EVERYWHERE**: Every distinct line, prompt, metadata entry, quote, bullet, or speaking script MUST be instantiated as an independent paragraph object (`doc.add_paragraph()` or `cell.add_paragraph()`).
  - **Why this is catastrophic in Justified text**: In Microsoft Word, when a paragraph is justified (`<w:jc w:val="both"/>`), Word treats a manual line break (`<w:br/>` / Shift+Enter) as an internal line continuation and forces the line to justify across the full margin width, creating absurdly wide gaps between characters and words. Only a true paragraph mark (`<w:p>`) signals the legitimate end of a paragraph block, allowing Word's justification engine to format the line naturally without distortion.
  - **Paragraph Spacing**: Control spacing between elements exclusively through paragraph formatting properties (`p.paragraph_format.space_before` and `space_after` in `Pt(...)`), never by inserting empty paragraphs containing manual line breaks.
- **Mandatory Table Standards (Font, Direction, Alignment & Paragraph Marks)**:
  - **Mandatory Table Placement Sequence (Narrative Precedes Table)**:
    - The canonical reporting sequence MUST strictly be:
      1. Heading
      2. Explanatory narrative introducing the statistical findings (in continuous prose)
      3. Table caption (non-bold)
      4. Table
      5. Table note
    - NEVER place explanatory text under the table instead of preceding the caption. The reader must be introduced to the findings before the data is presented.
  - **Table Fonts**:
    - **Font size for Table content and Table captions is strictly 12 pt**.
    - **Table Captions MUST be non-bold** (`B Nazanin` 12 pt Regular). Never apply `<w:b/>` to table captions.
    - **NO `B Titr` font anywhere in tables or captions**.
    - Table Headers, Category Labels, Table Data, and Narrative Content MUST all use `B Nazanin`.
    - Latin Terms, Symbols & English Metrics: `Times New Roman` (10–10.5 pt, Italic for statistical symbols $M, SD, t, F, p, \beta$).
  - **Table Directionality**:
    - Every table MUST have `<w:bidiVisual/>` injected into `<w:tblPr>` so column order renders strictly Right-to-Left.
    - Every single paragraph in every table cell MUST enforce RTL text direction (`<w:bidi w:val="1"/>` in `pPr` and `<w:rtl w:val="1"/>` in `rPr`).
  - **Table Text Alignment**:
    - Headers, status badges, and discrete codes/metrics: Centered (`<w:jc w:val="center"/>`).
    - Row labels and short descriptors: Right-aligned (`<w:jc w:val="right"/>`).
    - Substantive multi-line descriptions, speech scripts, and narrative cell content: **MUST BE JUSTIFIED** (`<w:jc w:val="both"/>`).
  - **Strict Paragraph Mark Policy in Tables (No Manual Line Breaks)**:
    - **NEVER use manual line breaks (`<w:br/>` / `\n`) inside table cells**.
    - Every bullet point, sub-item, speech segment, or distinct note within a table cell MUST be created as an independent paragraph object (`cell.add_paragraph()` / `<w:p>`).
    - Cell paragraph spacing MUST be regulated via `paragraph_format.space_before` and `space_after` in `Pt(...)`, never by inserting blank lines.
- **Mandatory Header & Heading Standards (Font, Direction, Alignment & Paragraph Marks)**:
  - **Header Fonts**:
    - **Chapter Names ONLY**: `B Titr` (Centered, RTL).
    - **All Other Headings** (Level 1, Level 2, Sub-labels, Callout Titles): `B Nazanin Bold` (Right-aligned, RTL).
  - **Header Directionality**:
    - All headers MUST enforce RTL text direction (`<w:bidi w:val="1"/>` in `pPr` and `<w:rtl w:val="1"/>` in `rPr`).
  - **Header Paragraph Marks**:
    - Every header, title, and subtitle MUST be instantiated as an independent paragraph object (`<w:p>`).
    - NEVER use manual line breaks (`<w:br/>` / `\n`) to break headers across lines.
    - Header spacing MUST be managed via `paragraph_format.space_before` and `space_after` in `Pt(...)`.
- **Mandatory Persian Number & Decimal Typography Standards (قاعده استاندارد اعداد و اعشار در گزارش‌های فارسی)**:
  - **Standard Dot ('.') Representation**: In all Persian academic reports, theses, articles, proposals, and presentations, decimal numbers MUST be written in the standard dot (`.`) format: e.g., `۰.۰۰۱`, `۰.۰۵`, `۰.۸۵`, `۲.۵۰`, `۰.۴۰`, `۱.۱۱۸`, `۱۵.۲`.
  - **Never Remove Leading Zero in Persian (حفظ حتمی صفر قبل از ممیز در زبان فارسی)**:
    - In Persian, agents and authors **MUST NEVER** remove the leading zero before the dot:
      - **Correct**: `۰.۰۰۱`, `۰.۰۵`, `۰.۸۵`, `۰.۴۰`, `۰.۰۰۱ > p` (یا: `p < ۰.۰۰۱`).
      - **Strictly Prohibited**: `.۰۰۱`, `.۰۵`, `.۸۵`, `.۴۰`, `.۰۰۱ > p`.
    - Reporting numbers with 3 decimal places for $p$-values: always write `۰.۰۰۱` (never `.۰۰۱`).
  - **Prohibition of Inverted Slashes**: Never use forward slashes (`/`) or reversed fraction tricks (such as swapping digits `۰۰۱/۰`), as they confuse human readers, supervisors, and editing pipelines.

### Directive 5.1: Critical OpenXML Standard: Preservation of Native Word Math & OMML Formulas (`<m:oMath>`)
When inspecting, auditing, or modifying academic Word documents (`.docx`):
1. **The OMML Text Blindspot in python-docx**:
   - `paragraph.text` in `python-docx` **ONLY** reads standard `<w:t>` elements and completely ignores math text runs (`<m:t>`) embedded inside native Word equation objects (`<m:oMath>` / `<m:oMathPara>`).
   - Consequently, paragraphs containing native Word equations will falsely appear in `paragraph.text` as having empty parentheses `()` or missing numbers.
2. **Never Overwrite `paragraph.text` Naively**:
   - Executing `paragraph.text = "..."` replaces all child XML nodes and irrevocably deletes all `<m:oMath>` and `<m:oMathPara>` equation objects.
   - Any agent modifying a paragraph must first check whether it contains math elements:
     ```python
     has_math = any(elem.tag.endswith("}oMath") for elem in paragraph._p.iter())
     ```
3. **Mandatory Full Text Extraction Protocol**:
   - To inspect the true visible text of any paragraph including equations, always extract text from both `<w:t>` and `<m:t>`:
     ```python
     full_text = "".join([e.text or "" for e in paragraph._p.iter() if e.tag.endswith("}t")])
     ```
4. **Preservation of Word Drawings and Inline Images (`<w:drawing>` & `<a:blip>`)**:
   - Assigning `paragraph.text = "..."` replaces all child XML nodes and irrevocably deletes all `<w:drawing>`, `<w:pict>`, and inline shape objects embedded within that paragraph.
   - Any agent modifying a paragraph MUST first verify whether it contains drawing elements:
     ```python
     has_drawing = bool(paragraph._p.xpath('.//w:drawing') or paragraph._p.xpath('.//a:blip'))
     ```
   - If a paragraph contains a drawing, never overwrite `paragraph.text`. Modify only specific text runs or append sibling paragraphs.
   - Whenever a manuscript, proposal, or thesis references a Figure (e.g. `Figure 1`), the agent must NEVER leave a blank placeholder or text-only caption. The agent MUST physically embed the high-resolution image (≥ 300 DPI) centered on the page, preceded by the bold Figure number and italic title, and followed by the APA 7 Note.
5. **Mandatory Pre-Edit Backup**:
   - Before applying any programmatic edits or replacements to user documents (`.docx`), always save a timestamped backup copy to `drafts_archive/` or a pre-edit file.
