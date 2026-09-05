# Reference File Formats: EndNote (.enw), RIS (.ris), and APA Text (.txt)

This document provides specifications and tag mappings for bibliographic formats used by reference managers like EndNote, Zotero, Mendeley, and Citavi.

---

## 1. EndNote Tagged Format (`.enw`)

The `.enw` format consists of two-character tags preceded by `%` and followed by a space and the data value. Records are separated by blank lines.

### Standard Tag Mapping

| Tag | Field Name | Description | Example |
| :--- | :--- | :--- | :--- |
| `%0` | Reference Type | Document type identifier | `%0 Journal Article`, `%0 Book`, `%0 Book Section` |
| `%A` | Author | Author name (repeat `%A` for each author) | `%A Carleton, R. N.` |
| `%D` | Year | 4-digit publication year | `%D 2007` |
| `%T` | Title | Title of article or book | `%T Fearing the unknown: A short version of the IUS` |
| `%J` | Journal | Name of journal (for Journal Articles) | `%J Journal of Anxiety Disorders` |
| `%B` | Book Title | Title of book (for Book Sections/Chapters) | `%B Handbook of Social Studies in Health` |
| `%V` | Volume | Volume number | `%V 21` |
| `%N` | Issue | Issue / number | `%N 1` |
| `%P` | Pages | Page range | `%P 105-117` |
| `%R` | DOI | Digital Object Identifier | `%R 10.1016/j.janxdis.2006.03.014` |
| `%U` | URL | Link to online article / repository | `%U https://doi.org/10.1016/j.janxdis.2006.03.014` |

### Example `.enw` Record
```text
%0 Journal Article
%A Carleton, R. N.
%A Norton, M. P.
%A Asmundson, G. J.
%D 2007
%T Fearing the unknown: A short version of the Intolerance of Uncertainty Scale
%J Journal of Anxiety Disorders
%V 21
%N 1
%P 105-117
%R 10.1016/j.janxdis.2006.03.014
%U https://doi.org/10.1016/j.janxdis.2006.03.014
```

---

## 2. Research Information Systems Format (`.ris`)

The RIS format is a standardized tag format developed by Research Information Systems. Tags are two characters followed by two spaces, a hyphen, and a space (`TAG  - `). Each record MUST end with the end-of-record tag (`ER  - `).

### Standard Tag Mapping

| Tag | Field Name | Description | Example |
| :--- | :--- | :--- | :--- |
| `TY  -` | Type of Reference | `JOUR` (Journal), `BOOK` (Book), `CHAP` (Chapter) | `TY  - JOUR` |
| `AU  -` | Author | Author name (repeat for each author) | `AU  - Carleton, R. N.` |
| `PY  -` | Publication Year | 4-digit year | `PY  - 2007` |
| `TI  -` | Primary Title | Title of article or book | `TI  - Fearing the unknown` |
| `JO  -` | Journal Name | Full or abbreviated journal name | `JO  - Journal of Anxiety Disorders` |
| `T2  -` | Secondary Title | Book title when citing a chapter | `T2  - Handbook of Anxiety Disorders` |
| `VL  -` | Volume | Volume number | `VL  - 21` |
| `IS  -` | Issue | Issue number | `IS  - 1` |
| `SP  -` | Start Page | First page of range | `SP  - 105` |
| `EP  -` | End Page | Last page of range | `EP  - 117` |
| `DO  -` | DOI | Digital Object Identifier | `DO  - 10.1016/j.janxdis.2006.03.014` |
| `UR  -` | URL | Link to online publication | `UR  - https://doi.org/10.1016/j.janxdis.2006.03.014` |
| `ER  -` | End of Record | Required closing tag for each entry | `ER  - ` |

### Example `.ris` Record
```text
TY  - JOUR
AU  - Carleton, R. N.
AU  - Norton, M. P.
AU  - Asmundson, G. J.
PY  - 2007
TI  - Fearing the unknown: A short version of the Intolerance of Uncertainty Scale
JO  - Journal of Anxiety Disorders
VL  - 21
IS  - 1
SP  - 105
EP  - 117
DO  - 10.1016/j.janxdis.2006.03.014
UR  - https://doi.org/10.1016/j.janxdis.2006.03.014
ER  - 
```

---

## 3. Formatted APA 7th Reference List (`.txt`)

Plain text reference lists should adhere to the American Psychological Association (APA 7th Edition) conventions:

1. **Ordering**: Alphabetical by primary author's surname.
2. **Multiple works by the same author**: Chronological by publication year (oldest to newest). Same year works distinguished by `a`, `b`, `c`.
3. **Components**:
   - `Author(s). (Year). Title of article. Journal Name, Volume(Issue), Pages. DOI/URL`
4. **Numbering**: For clean reference indexing in plain text deliverables, each reference is preceded by its index number (`1.`, `2.`, `3.`).
