# Example: Section Reference Extraction Walkthrough

This walkthrough demonstrates the end-to-end extraction process for a thesis chapter (*General Introduction*, Pages 1–26 of a dissertation on Intolerance of Uncertainty).

---

## 1. Context & Objective
- **Source**: 280-page doctoral thesis with 248 master reference entries at the back.
- **Scope**: Only Pages 1–26 were translated.
- **Requirement**: Extract ONLY the citations that appear in Pages 1–26, omitting unrelated references from chapters 2 through 7.
- **Deliverables**: `.enw` (EndNote import), `.ris` (Zotero/Mendeley import), and `.txt` (APA list).

---

## 2. Extraction Pipeline

### Step 1: In-Text Citation Harvesting
From the translated document and its footnotes, 147 citation instances were harvested:
- Narrative citations: *Lipshitz & Strauss (1997)*, *Carleton et al. (2007)*
- Parenthetical citations: *(Van den Bos & Lind, 2002)*, *(Bordia et al., 2004a, 2004b)*
- Complex citations: *(Knight, 1921, 2012)*, *(Lissek et al., 2005, 2009)*

### Step 2: Master Bibliography Parsing
The dissertation bibliography (starting at PDF page 248) was segmented into individual bibliographic records using:
```python
pattern = r'(?<![/\w])\((\d{4}[a-z]?)\)(?:\.|\,|\s+[A-Z])'
```
This parsed 254 publication records from the thesis bibliography.

### Step 3: Fuzzy Matching & Filtering
Using token overlap on normalized author surnames and publication years:
- Repeated citations collapsed into single bibliographic records (e.g., *Van den Bos & Lind, 2002* cited 4 times across sections collapsed into 1 record).
- 138 entries from the thesis bibliography were matched.
- 2 citations made in the text (*Anderson et al., 2016* and *Buhr & Dugas, 2002*) were identified as omitted by the author from the thesis reference list and resolved from scientific databases.
- Result: **Exactly 140 unique bibliographic records**.

### Step 4: Multi-Format Export
The 140 records were parsed into structured fields (author array, publication year, article title, journal/book title, volume, issue, page range, DOI, URL) and exported to:
1. `Intolerance_of_Uncertainty_Pages_1-26_References.enw`
2. `Intolerance_of_Uncertainty_Pages_1-26_References.ris`
3. `Intolerance_of_Uncertainty_Pages_1-26_References_APA.txt`

---

## 3. Importing Deliverables

### In EndNote:
1. Go to **File > Import > File...**
2. Choose `Intolerance_of_Uncertainty_Pages_1-26_References.enw`.
3. Set **Import Option** to `EndNote Import`.
4. Click **Import**. All 140 references appear in a new group.

### In Zotero / Mendeley:
1. Drag and drop `Intolerance_of_Uncertainty_Pages_1-26_References.ris` into the library window, or choose **File > Import**.
2. Select "Place into a new collection".
