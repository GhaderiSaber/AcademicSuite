# Deep Diagnostic: ONLYOFFICE vs MS Word Table RTL Support

## Background
The investigation aimed to determine why ONLYOFFICE displays OpenXML tables Left-to-Right despite the presence of a pure `<w:bidiVisual/>` tag in `w:tblPr`, and whether ONLYOFFICE has alternative syntax requirements or lacks support entirely.

## Investigation Steps
1. Investigated GitHub issues across `ONLYOFFICE/DesktopEditors` and `ONLYOFFICE/DocumentServer`.
2. Verified LibreOffice parsing of the provided `Chapter_4_Results.docx`.
3. Validated OpenXML specification handling across Word, LibreOffice, and ONLYOFFICE.

## Empirical Findings

### 1. ONLYOFFICE Support for `<w:bidiVisual/>`
ONLYOFFICE **does not currently support** table-level visual mirroring via the `<w:bidiVisual/>` OpenXML tag. It ignores the tag completely, resulting in Left-to-Right rendering of tables that are designed as Right-to-Left. 

### 2. Upstream Tracking
This is a known bug tracked upstream by ONLYOFFICE maintainers:
* **ONLYOFFICE/DocumentServer#3133 (Open)**: Tracks the missing RTL table orientation support. This is logged internally at ONLYOFFICE as **Bug 69579**.
* Several related issues in `DesktopEditors` (#2237, #2159, #1980) have all been **closed as duplicates** of #3133.

### 3. OpenXML Syntax Requirements
There is no "secret" or "alternative" OpenXML syntax required by ONLYOFFICE. The failure is purely an upstream rendering engine deficit. 

### 4. Cross-Platform Baseline Behavior
* **Microsoft Word**: Natively and correctly handles `<w:bidiVisual/>` to visually flip table column order (e.g. Column 1 appears on the right).
* **LibreOffice**: Successfully parses `<w:bidiVisual/>` and accurately renders tables Right-to-Left (verified via headless PDF conversion).

## Architectural Resolution & Recommendation
**Do not modify the document generation pipeline.** 
The generator should continue to rely entirely on `<w:bidiVisual/>`. Attempting to structurally reverse the columns in XML to "satisfy" ONLYOFFICE would break canonical compatibility with Microsoft Word, LibreOffice, and OpenXML standards. 

ONLYOFFICE users will experience inverted table columns until ONLYOFFICE Development patches Bug 69579 in a future release (v9.1+). This is entirely an upstream rendering defect.
