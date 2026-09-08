# Literature Harvesting & Academic Metadata Extraction Standards

This reference document defines the API protocols, query schemas, NLP extraction regexes, and citation formatting standards implemented in the **`literature-harvester`** skill of the **AcademicSuite**.

---

## 1. Multi-Database API & Retrieval Architecture

`literature-harvester` queries both international and Iranian academic databases to assemble a balanced corpus of empirical studies for thesis Chapter 2 (پیشینه تجربی) and systematic reviews:

```
                          [User Research Keywords]
           ("Acceptance and Commitment Therapy", "درمان مبتنی بر پذیرش و تعهد")
                                     │
       ┌─────────────────────────────┴─────────────────────────────┐
       ▼                                                           ▼
 [International Databases]                               [Iranian Repositories]
  ├── 1. PubMed / NCBI Entrez REST API                    ├── 4. SID.ir (جهاد دانشگاهی)
  ├── 2. CrossRef Works REST API                          ├── 5. Magiran (مگیران)
  └── 3. Semantic Scholar Graph API                       └── 6. Curated Empirical Matrix
       │                                                           │
       └─────────────────────────────┬─────────────────────────────┘
                                     ▼
                    [Abstract & Metadata Normalizer]
       ├── Title, Authors, Journal, Year (AD / Hijri Shamsi)
       └── DOI, URLs, Language Tagging
                                     │
                                     ▼
                   [NLP Empirical Parameter Extractor]
       ├── Sample Size (N) Extractor
       ├── Research Design Classifier (RCT, ANCOVA, Correlational, SEM)
       ├── Psychometric Instrument Detector (Scales & Questionnaires)
       └── Key Statistical Findings & Effect Direction
                                     │
       ┌─────────────────────────────┼─────────────────────────────┐
       ▼                             ▼                             ▼
[1. Chapter 2 Word Section]   [2. 4-Sheet Excel Matrix]    [3. EndNote / RIS File]
   - APA 7 Summary Table         - Master Overview            - Standard RIS format
   - Standard 5-Part Narrative   - Iranian Studies            - Direct Zotero/EndNote
   - OpenXML BiDi RTL            - International Studies        import
```

---

## 2. API Endpoints & Request Specifications

### 2.1. PubMed / NCBI Entrez E-Utilities
- **Base URL**: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`
- **Step 1: Search (`esearch.fcgi`)**:
  - Endpoint: `esearch.fcgi?db=pubmed&term={query}&retmode=json&retmax={limit}&sort=pub_date`
  - Returns: List of PubMed IDs (PMIDs).
- **Step 2: Summary (`esummary.fcgi`)**:
  - Endpoint: `esummary.fcgi?db=pubmed&id={id_list}&retmode=json`
  - Returns: Article title, authors, source journal, publication date, DOI.
- **Step 3: Fetch Abstract (`efetch.fcgi`)**:
  - Endpoint: `efetch.fcgi?db=pubmed&id={id_list}&retmode=xml`
  - Extracts `<AbstractText>` content.

### 2.2. CrossRef Works API
- **Base URL**: `https://api.crossref.org/works`
- **Parameters**: `?query={query}&rows={limit}&select=DOI,title,author,published,container-title,abstract`
- **Polite Header**: `User-Agent: AcademicSuite/1.0 (mailto:academic-suite@research.org)`

### 2.3. Semantic Scholar Graph API
- **Base URL**: `https://api.semanticscholar.org/graph/v1/paper/search`
- **Parameters**: `?query={query}&limit={limit}&fields=title,authors,year,abstract,venue,isOpenAccess,citationCount`

### 2.4. Iranian Academic Databases (SID & Magiran)
- **SID (Scientific Information Database - جهاد دانشگاهی)**:
  - Base URL: `https://www.sid.ir`
  - Schema: Persian title, Persian author list, Iranian scientific-research journal, abstract, keywords, publication year (هجری شمسی e.g., ۱۴۰۲).
- **Magiran (بانک اطلاعات نشریات کشور)**:
  - Base URL: `https://www.magiran.com`
  - Focus: Peer-reviewed psychology and educational journals (e.g., *روان‌شناسی بالینی و شخصیت*، *مطالعات روان‌شناختی*، *پژوهش‌های کاربردی روان‌شناختی*).

---

## 3. Automated NLP Parameter Extraction Patterns

Abstracts are parsed using specialized regular expressions to extract structured empirical parameters:

### 3.1. Sample Size ($N$) Extraction
- **English Patterns**:
  - `\b(?:n\s*=\s*|sample\s+of\s+|total\s+of\s+|participants\s*(?:\(n\s*=\s*|\s*=\s*))(\d{2,4})\b`
  - `(\d{2,4})\s+(?:patients|students|participants|individuals|subjects|teachers)\b`
- **Persian Patterns**:
  - `(?:نمونه‌ای\s+شامل|حجم\s+نمونه|تعداد)\s+(\d{2,4})\s+(?:نفر|شرکت‌کننده|دانش‌آموز|بیمار|معلم)`
  - `(\d{2,4})\s+(?:نفر|شرکت‌کننده|آزمودنی)\s+(?:به\s+عنوان\s+نمونه|انتخاب\s+شدند)`

### 3.2. Research Design Classification
- **Experimental / RCT (کارآزمایی بالینی و نیمه‌آزمایشی)**:
  - EN: `randomized controlled trial`, `quasi-experimental`, `pretest-posttest`, `control group`, `intervention`
  - FA: `نیمه‌آزمایشی`, `پیش‌آزمون-پس‌آزمون`, `گروه کنترل`, `کارآزمایی بالینی`, `مداخله`
- **Correlational / Predictive (همبستگی و رگرسیون)**:
  - EN: `correlational`, `cross-sectional`, `multiple regression`, `predictive`
  - FA: `همبستگی`, `توصیفی-همبستگی`, `رگرسیون چندگانه`, `مقطعی`
- **Structural Equation Modeling (معادلات ساختاری)**:
  - EN: `structural equation modeling`, `path analysis`, `mediation`, `moderation`
  - FA: `مدل‌یابی معادلات ساختاری`, `تحلیل مسیر`, `میانجی‌گری`, `تعدیل‌گری`

### 3.3. Psychometric Instrument Detection
- Scans abstract text against the **Questionnaire Registry (`Questionnaires.xlsx`)** (4,880 entries) and known acronyms:
  - `DASS-21`, `BDI-II`, `CFI`, `AAQ-II`, `CDRISC`, `PSWQ`, `GHQ-28`, `MSPSS`, `PANAS`, `MAAS`
  - FA: `پرسشنامه انعطاف‌پذیری شناختی`, `پرسشنامه پذیرش و عمل`, `پرسشنامه فرسودگی شغلی مسلش`, `مقیاس تاب‌آوری کانر-دیویدسون`

---

## 4. Standard 5-Part Iranian Reporting Formula for Chapter 2

Graduate schools and Iranian peer-reviewed journals require Chapter 2 empirical studies to be summarized using a uniform 5-part academic narrative:

$$\mathbf{Formula} = \text{[Author]} + \text{[Target Construct \& Sample]} + \text{[Methodology \& Design]} + \text{[Instruments]} + \text{[Key Empirical Findings]}$$

### Standard Iranian Template:
> «**[نویسنده/نویسندگان] ([سال])** در پژوهشی با عنوان «*[عنوان مقاله]*» بر روی **[حجم نمونه] نفر** از [جامعه آماری] به بررسی اثربخشی [متغیر مستقل] بر [متغیرهای وابسته] پرداختند. طرح پژوهش از نوع **[روش پژوهش]** همراه با [گروه آزمایش و کنترل] بود. برای سنجش متغیرها از **[ابزارهای اندازه‌گیری]** استفاده شد. نتایج حاصل از تحلیل [روش آماری] نشان داد که [یافته‌های آماری]؛ به طوری که [متغیر مستقل] توانست به طور معناداری موجب [افزایش/کاهش متغیر وابسته] گردد.»

---

## 5. Standard RIS Citation File Specification

Exported `.ris` files adhere to standard bibliographic formatting:

```text
TY  - JOUR
AU  - Author, A. A.
AU  - Author, B. B.
TI  - Title of the Harvested Empirical Study
JO  - Journal of Psychological Science
PY  - 2024
VL  - 18
IS  - 2
SP  - 145
EP  - 160
DO  - 10.1037/0000000
AB  - Structured abstract of the harvested paper...
ER  - 
```
