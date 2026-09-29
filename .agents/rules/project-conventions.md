---
trigger: always_on
description: "Universal project conventions: APA 7th edition typography, Persian OpenXML standards, leading zero rule, and table borders."
---

# Project Conventions & Standards (Directives 4, 5, 6, 8)

1. **Directive 4 (Strict APA 7th Edition Typography)**:
   - Italicize Latin statistical symbols (*M, SD, t, F, p, r, R², β, B, z, SE, df, n, N*). Greek letters remain regular.
   - Means/SDs: 2 decimal places. $p$-values: Exactly 3 decimal places.
   - Persian leading zero standard: ALWAYS keep leading zero in Persian (`۰.۰۰۱ > p`, `۰.۰۵`).
   - APA 7 tables: Zero vertical borders, exactly 3 horizontal borders.
2. **Directive 5 (Persian OpenXML Standards & Orthography)**:
   - RTL paragraph direction via `<w:bidi w:val="1"/>` and table direction `<w:bidiVisual/>`.
   - Genuine font binding: `B Nazanin` (Body, 13-14pt), `B Titr` (Headings, 12-18pt), `Times New Roman` (Latin & statistics).
   - Zero manual breaks (`<w:br/>`) in justified text. Preserve native Word OMML math (`<m:oMath>`).
   - Standard Persian letters strictly required (`ی` `\u06CC`, `ک` `\u06A9`, `ه/ت`); Arabic glyphs (`ي` `\u064A`, `ك` `\u0643`, `ة` `\u0629`, and Arabic digits `٠-٩`) are mechanically prohibited.
3. **Directive 6 (Mandatory English-Only File Naming)**:
   - Every file, script, dataset, table, docx, pptx, or directory MUST be named strictly in ASCII English (`a-z`, `A-Z`, `0-9`, `_`, `-`, `.`). Zero Persian/non-ASCII filenames on disk.
4. **Directive 8 (Mandatory Git Lifecycle)**:
   - Automatically stage project modifications, create conventional semantic commit messages (`feat:`, `fix:`, `docs:`, `refactor:`), and keep working tree clean.
