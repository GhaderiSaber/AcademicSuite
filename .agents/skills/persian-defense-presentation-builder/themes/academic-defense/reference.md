# Academic Defense — Style Reference
# تم جلسه دفاع دانشگاهی — راهنمای سبک و طراحی

Prestigious, scholarly, and authoritative. Designed specifically for graduate thesis and doctoral dissertation defenses in Psychology, Behavioral Sciences, and Humanities. Deep academic navy and charcoal backgrounds with crisp white readability, emerald confirmation accents, and gold accents. Generous whitespace, structured scientific hierarchies, and APA 7th Edition table alignments.

سبکی آکادمیک، فاخر و معتبر؛ طراحی‌شده اختصاصی برای جلسات دفاع پایان‌نامه‌های کارشناسی ارشد و رساله‌های دکتری در علوم رفتاری، روان‌شناسی و علوم انسانی. ترکیب سرمه‌ای دانشگاهی با نوشته‌های روشن، نشان‌های تایید زمردی، نمودارهای مسیر، و جداول بدون خط عمودی منطبق بر استاندارد APA 7.

Use canonical layout roles: `defense_cover`, `defense_committee`, `defense_problem`, `defense_gap`, `defense_callout`, `defense_divider`, `defense_framework`, `defense_methodology`, `defense_instruments`, `defense_intervention`, `defense_descriptive`, `defense_split`, `defense_spotlight`, `defense_table`, `defense_matrix`, `defense_discussion`, `defense_implications`, `defense_limitations`, `defense_closing`.

## Named Layout Variations
- `defense_cover` -> Academic Thesis Hero Cover
- `defense_committee` -> Committee and Board of Examiners Roster
- `defense_problem` -> Problem Statement Funnel
- `defense_gap` -> Research Gap & Necessity Matrix
- `defense_callout` -> Core Theoretical Premise & Thesis Proposition
- `defense_divider` -> Chapter Transition Divider
- `defense_framework` -> Conceptual Model & Theoretical Framework
- `defense_methodology` -> Research Design & Participant Flow
- `defense_instruments` -> Psychometric Instruments Validation Table
- `defense_intervention` -> Clinical Intervention Protocol Roadmap
- `defense_descriptive` -> Descriptive Statistics Matrix
- `defense_split` -> Two-Column Split Analysis
- `defense_spotlight` -> Result Spotlight & Hero Statistic
- `defense_table` -> APA 7 Inferential Statistical Table
- `defense_matrix` -> Hypothesis Testing & Verification Verdict Badges
- `defense_discussion` -> Theoretical Mechanism Discussion
- `defense_implications` -> Theoretical & Practical Implications
- `defense_limitations` -> Limitations & Future Recommendations
- `defense_closing` -> Defense Q&A Closing

---

## Colors / رنگ‌بندی

```css
:root {
    --bg:           #0B192C;   /* Deep Academic Navy / سرمه‌ای دانشگاهی */
    --bg-secondary: #1E3E62;   /* Medium Slate Navy for Cards / سرمه‌ای متالیک برای کارت‌ها */
    --bg-card:      rgba(30, 62, 98, 0.45); /* Translucent Card / پس‌زمینه نیمه‌شفاف کارت */
    --border-card:  rgba(255, 255, 255, 0.12); /* Subtle Glass Border / کادر ظریف شیشه‌ای */
    --text:         #F1F6F9;   /* Pure Scholarly White / سفید خوانا */
    --text-muted:   #9BA4B5;   /* Secondary Slate Gray / طوسی روشن برای متون فرعی */
    --accent:       #00ADB5;   /* Academic Cyan Accent / فیروزه‌ای آکادمیک برای تاکید */
    --accent-gold:  #F5A623;   /* Gold for Honors & Badges / طلایی برای نشان‌ها */
    --accent-green: #10B981;   /* Emerald for Accepted Hypotheses / سبز زمردی تایید فرضیه */
    --accent-red:   #EF4444;   /* Crimson for Rejected Hypotheses / قرمز برای عدم تایید */
    --rule:         rgba(255, 255, 255, 0.15); /* Divider / خط جداکننده */
}
```

---

## Typography / تایپوگرافی

```css
/* Persian & Latin Headings */
.ad-title {
    font-family: "Vazirmatn", "B Titr", "Inter", "Segoe UI", sans-serif;
    font-weight: 800;
    font-size: clamp(2rem, 4.2vw, 3.8rem);
    line-height: 1.25;
    letter-spacing: -0.01em;
    color: var(--text);
}

/* Body & Narratives */
.ad-body {
    font-family: "Vazirmatn", "B Nazanin", "Segoe UI", sans-serif;
    font-weight: 400;
    font-size: clamp(1rem, 1.6vw, 1.25rem);
    line-height: 1.8;
    color: var(--text);
}

/* Category Eyebrow Badge */
.ad-eyebrow {
    font-family: "Vazirmatn", "Inter", sans-serif;
    font-size: clamp(0.75rem, 1.1vw, 0.9rem);
    font-weight: 700;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    background: rgba(0, 173, 181, 0.15);
    padding: 0.35rem 0.85rem;
    border-radius: 9999px;
    display: inline-block;
    border: 1px solid rgba(0, 173, 181, 0.3);
}

/* Statistical Highlight Number */
.ad-stat {
    font-family: "Times New Roman", "Inter", serif;
    font-size: clamp(2.2rem, 5vw, 4.5rem);
    font-weight: 800;
    font-style: italic;
    color: var(--accent-gold);
    line-height: 1.1;
}
```

---

## Academic Components / مولفه‌های جلسه دفاع

1. **Committee Grid (اعضای هیئت داوران)**: Cards displaying Supervisor (استاد راهنما), Advisor (استاد مشاور), and Examiners (داوران داخلی و خارجی).
2. **Problem Statement Funnel (قیف بیان مسئله)**: 4 to 5 stepped layers narrowing from global burden to target research gap.
3. **Hypothesis Matrix (ماتریس آزمون فرضیه‌ها)**: Table or card grid with test statistic ($t, F, \beta$), $p$-value, effect size ($\eta_p^2, R^2$), and verification badge (`تأیید شد` / `رد شد`).
4. **APA 7 Statistical Table (جدول یافته‌های آماری)**: Borderless vertical lines, 3 horizontal borders, justified numbers in Times New Roman.
5. **Candidate Speaker Notes (یادداشت‌های ارائه شفاهی)**: Embedded in `data-notes` on 100% of slides.
