# In-Text Citation Patterns & Matching Guidelines

This reference guide outlines common citation patterns found in academic documents and translation workflows, along with regular expressions and matching strategies.

---

## 1. Citation Variants in Academic Writing

| Pattern | Example | Extraction Strategy |
| :--- | :--- | :--- |
| **Single Author** | `(Carleton, 2012)` or `Carleton (2012)` | Author: `Carleton`, Year: `2012` |
| **Two Authors** | `(Lipshitz & Strauss, 1997)` or `Lipshitz & Strauss (1997)` | Authors: `Lipshitz`, `Strauss`, Year: `1997` |
| **Three+ Authors** | `(Bordia et al., 2004)` or `Bordia et al. (2004)` | Lead Author: `Bordia`, Year: `2004` |
| **Same Author, Multiple Years** | `(Bordia et al., 2004a, 2004b)` | Queries: `(Bordia, 2004a)`, `(Bordia, 2004b)` |
| **Historic / Reissued Works** | `(Knight, 1921, 2012)` | Queries: `(Knight, 1921)`, `(Knight, 2012)` |
| **Multiple Works in Multi-Study** | `(Lissek et al., 2005, 2009)` | Queries: `(Lissek, 2005)`, `(Lissek, 2009)` |
| **Corporate / Institutional** | `(American Psychiatric Association, 2013)` | Author: `American Psychiatric Association`, Year: `2013` |
| **Surnames with Prefixes (Dutch/French/Italian)** | `(van den Bos & Lind, 2002)`, `(van der Heiden et al., 2012)`, `(de Finetti, 1974)`, `(Le Poire & Burgoon, 1996)` | Match on main surname root (`bos`, `heiden`, `finetti`, `poire`) and full name prefix |
| **Accented Surnames** | `(Deschênes et al., 2012)` | Normalize Unicode (`NFKD`) to match both `Deschênes` and `Deschenes` |

---

## 2. Integration with `persian-academic-translation`

In translations performed using the `persian-academic-translation` skill:
- All in-text Latin references are recorded as footnotes:
  - In Markdown: `[^42]` with footnote definition `[^42]: Carleton et al., 2007`
  - In Python build arrays: `(42, "Carleton et al., 2007")`
- Footnotes provide a direct, pre-filtered catalog of citations that appeared exclusively in the translated sections.

---

## 3. Regular Expression Patterns

### Extracting Surnames and Years from Citations
```python
import re

# Match 4-digit years with optional letter suffix (e.g. 2004a)
YEAR_PATTERN = r'\b(19\d\d|20\d\d)[a-z]?\b'

# Extract author token list (excluding 'et al', 'and', '&')
AUTHOR_TOKEN_PATTERN = r'\b[a-zA-Z\u00C0-\u017F]{3,}\b'
STOP_WORDS = {'and', 'eds', 'the', 'van', 'den', 'der', 'des', 'for'}
```

### Segmenting Reference Entries in Bibliography
```python
# Match publication year in APA entries: (YYYY) or (YYYYa)
BIB_YEAR_PATTERN = r'(?<![/\w])\((\d{4}[a-z]?)\)(?:\.|\,|\s+[A-Z])'

# Match author start after previous entry's DOI or period
ENTRY_SPLIT_PATTERN = (
    r'(?:https?://[^\s]+|\.(?:\s+|$))([A-Z][a-zA-Z\-\'\s]+,\s+[A-Z\.]|'
    r'\bAmerican Psychiatric Association\b|\bVan den Bos\b|\bVan der Heiden\b)'
)
```
