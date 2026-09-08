---
name: persian-proposal-builder
description: >-
  Expert academic research proposal (طرح تحقیق / پروپوزال) and methodology drafting skill for Iranian master's
  and doctoral students in Psychology, Counseling, and Behavioral Sciences. Guides formulating clear titles,
  structuring the problem statement (بیان مسئله) via the inverted-triangle model, formulating directional hypotheses,
  defining conceptual and operational definitions, designing rigorous methodologies (G*Power sample size,
  validated Persian instruments, statistical analysis plans), and compiling defense-ready Word (.docx) proposal documents.
---

# Persian Research Proposal Builder Skill (نگارش پروپوزال و طرح پژوهش)

This skill guides the agent in drafting defense-ready, high-acceptance **graduate research proposals (پروپوزال طرح پژوهش)** for Master's theses and Ph.D. dissertations in Psychology, Counseling, Educational Sciences, and Behavioral Health.

It conforms strictly to the standards of the Iranian Ministry of Science, Ministry of Health, and Islamic Azad University research councils, producing structured proposals that seamlessly feed into **Chapter 1 (کلیات پژوهش)** and **Chapter 3 (روش‌شناسی پژوهش)** of the master thesis compiler.

---

## 1. When to Activate This Skill

Activate this skill when:
1. The user asks to write, refine, or review a **graduate research proposal (پروپوزال / طرح تحقیق)**.
2. The user needs help formulating **hypotheses (فرضیه‌ها)**, **objectives (اهداف)**, or **conceptual and operational definitions (تعاریف نظری و عملیاتی)**.
3. The user needs to draft **Chapter 1 (کلیات پژوهش)** or **Chapter 3 (روش‌شناسی پژوهش)** of a thesis.
4. The user needs sample size calculation logic (G*Power or Krejcie-Morgan) and selection of standardized Persian psychometric instruments.

---

## 2. Proposal Architecture & Key Components

The proposal follows the standard Iranian university template:

| Section | Title in Persian | Purpose & Core Content |
| :--- | :--- | :--- |
| **Header** | **اطلاعات عمومی طرح** | Exact title (Persian & English), Student, Supervisor, and Advisor details. |
| **Section 1** | **بیان مسئله اساسی** | Inverted Triangle: Context $\to$ Construct definitions $\to$ Pathology/Prevalence in Iran $\to$ Research gap $\to$ Study purpose. |
| **Section 2** | **اهمیت و ضرورت** | Theoretical necessity (deepening scientific literature) and Practical necessity (applications for clinics, schools, organizations). |
| **Section 3** | **اهداف پژوهش** | General objective (هدف کلی) + Specific objectives (اهداف اختصاصی/ویژه). |
| **Section 4** | **فرضیه‌ها و سؤالات** | Directional hypotheses (فرضیه‌های جهت‌دار) for all direct, comparative, and mediation pathways. |
| **Section 5** | **تعاریف نظری و عملیاتی** | **نظری**: Citation of original theorist. **عملیاتی**: Specific questionnaire score and scoring range. |
| **Section 6** | **روش‌شناسی پژوهش** | Research design, Target population, Sampling (G*Power / Krejcie-Morgan), Psychometric instruments with Iranian validity/reliability, Execution procedure, and Statistical analysis plan. |
| **Section 7** | **ملاحظات اخلاقی** | Informed consent, confidentiality, right to withdraw, ethics code compliance. |
| **Section 8** | **منابع و مآخذ** | APA 7th Edition bilingual bibliography (Persian and English). |

---

## 3. Methodological Design Guardrails

### A. Title Formulation Rules
- Must include the **Independent Variable(s)**, **Mediator/Moderator** (if any), **Dependent Variable(s)**, and the **Target Population**.
- Example: «اثربخشی درمان مبتنی بر پذیرش و تعهد (ACT) بر انعطاف‌پذیری روان‌شناختی و اضطراب مرگ در بیماران مبتلا به سرطان پستان»

### B. Sample Size Determination
- **Correlational / SEM**: Minimum $N = 200–350$ (or 10–20 participants per observed variable).
- **Experimental / Interventions**: Minimum 15–20 participants per group (Experimental vs. Control) calculated via G*Power ($\alpha = .05$, Power $= .80$, medium effect size $f = .25$).

### C. Instrument Reporting Standard
For every questionnaire selected, the proposal must state:
1. Full name, author, and year of origin.
2. Number of items and Likert response scale (e.g., 5-point Likert from 1 = Strongly Disagree to 5 = Strongly Agree).
3. Subscale dimensions.
4. Reliability (Cronbach's $\alpha$) and validity in original and Iranian standardization studies.

---

## 4. Execution Workflow

1. **Intake Research Variables**:
   Gather the research topic, independent/dependent variables, target population, and proposed intervention or correlational design.
2. **Consult Reference Guides**:
   - Read [proposal_structure_guide.md](file:///Users/saber/Desktop/AntigravitySkills/.agents/skills/persian-proposal-builder/references/proposal_structure_guide.md) for structural standards.
3. **Formulate Proposal Content JSON**:
   Prepare a structured JSON containing problem statement, significance, objectives, hypotheses, definitions, instruments, and sampling.
4. **Generate Word Document**:
   Run the document generation script:
   ```bash
   python3 .agents/skills/persian-proposal-builder/scripts/generate_proposal_docx.py \
     --json "proposal_input.json" \
     --out "پروپوزال_طرح_پژوهش.docx"
   ```
5. **Quality Review**:
   Verify Persian typography (*B Titr* for headings, *B Nazanin* 13 pt for body text, 1.25 line spacing, RTL OpenXML flags).
