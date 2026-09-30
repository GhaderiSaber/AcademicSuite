---
trigger: glob
globs: "*.docx, *.pptx, *.xml"
description: "Persian academic typography and presentation standards: Dual-slot font binding (B Nazanin body, B Titr headings, Times New Roman stats), native footnotes, RTL table properties, structured DOM parsing for OpenXML, defense presentation sobriety (zero emojis)."
---

# Persian Academic Typography & Presentation Specification (Directives 4.1, 5)

Technical and visual requirements for Microsoft Word (`.docx`) and PowerPoint (`.pptx`) deliverables.

## 1. Directive 5: Dual-Slot OpenXML Font Binding
- Every paragraph and run element in Persian Word documents must strictly bind both complex script and Latin font slots:
  - **Body text**: `B Nazanin` 13–14 pt for Persian (`<w:rFonts w:cs="B Nazanin"/>`), `Times New Roman` 11–12 pt for Latin.
  - **Headings**: `B Titr` 12–18 pt for Persian (`<w:rFonts w:cs="B Titr"/>`), bold Latin heading font.
  - **Statistical symbols**: `Times New Roman` italicized.
- Enforce RTL paragraph flow (`<w:bidi w:val="1"/>`).
- Justified alignment (`<w:jc w:val="both"/>`) for body text; omit `<w:jc>` for right-aligned RTL headings.
- Zero manual line breaks (`<w:br/>` or `\n`) inside justified text runs.

## 2. Structured DOM OpenXML Manipulation
- **Strictly ban regex string substitutions** (`re.sub`) on minified OpenXML (`word/document.xml`).
- All document updates must be performed using structured XML DOM parsing (`lxml` or `xml.etree.ElementTree`).
- Maintain valid XML hierarchy and namespace consistency (`http://schemas.openxmlformats.org/wordprocessingml/2006/main`).

## 3. Footnotes and Academic Transliteration
- Zero raw Latin words inside continuous Persian narrative prose.
- Foreign terms, author surnames, and technical jargon must be transliterated phonetically into Persian, accompanied by a true OpenXML footnote (`word/footnotes.xml` and `<w:footnoteReference>`) providing the original Latin spelling.

## 4. Directive 4.1: Presentation Visual Standards (PowerPoint)
- **Academic Sobriety**: Zero emojis. Zero English words in Persian defense presentation slides.
- DrawingML dual-slot font binding (`B Titr` for titles, `B Nazanin` for bullets, `Times New Roman` for stats).
- Decoupled LTR numbers and negative signs ($-0.32$).
- Native RTL SmartArt layout (`Reverse = 1`).
