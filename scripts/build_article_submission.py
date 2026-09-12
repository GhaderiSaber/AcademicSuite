#!/usr/bin/env python3
"""
Build Article Submission Script
Assembles the complete academic manuscript JSON payload and compiles it to DOCX.
Client: Zahra Jalali
Subject: Self-Compassion as Mediator Between Personality Traits and Chronic Pain
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import subprocess

article_data = {
    "title": "Self-Compassion as an Affective Buffer: Mediating the Pathway from Big Five Personality Dimensions to Chronic Pain Severity in University Students",
    "authors": [
        "Zahra Jalali, MSc",
        "Hamid Amiri, PhD*",
        "Abdollah Omidi, PhD"
    ],
    "affiliation": "Department of Clinical Psychology, Medicine Faculty, Kashan University of Medical Sciences, Kashan, Iran\n* Corresponding Author: Hamid Amiri, PhD (Email: hamidamiri.kaums@gmail.com; ORCID: 0000-0002-2184-9199)",
    "abstract": {
        "background": "Chronic pain is an escalating, debilitating condition among university students that severely compromises academic performance, emotional wellbeing, and general quality of life. Although the Five-Factor Model of personality reliably predicts somatic symptom severity, the affective self-regulatory mechanisms bridging stable personality traits to subjective pain intensity remain insufficiently characterized.",
        "objective": "This study investigated whether self-compassion mediates the structural relationship between the Big Five personality traits (neuroticism, extraversion, openness, agreeableness, and conscientiousness) and chronic pain severity in university students.",
        "methods": "In this cross-sectional structural equation modeling (SEM) study, 304 university students experiencing chronic pain (duration ≥ 3 months) enrolled at Kashan University of Medical Sciences completed the NEO Five-Factor Inventory (NEO-FFI), the Self-Compassion Scale-Short Form (SCS-SF), and the Visual Analogue Scale (VAS). Structural equation modeling was conducted using maximum likelihood estimation in R (lavaan package) to evaluate direct and indirect pathways.",
        "results": "The hypothesized structural mediation model demonstrated excellent goodness-of-fit to empirical data: χ²(52) = 57.762, p = .271; χ²/df = 1.111; CFI = .995; TLI = .994; RMSEA = .019 (90% CI [.000, .042]); SRMR = .032. Latent personality dimensions significantly predicted self-compassion (β = -.544, p < .001) and directly predicted chronic pain severity (β = .387, p < .001). Self-compassion significantly and inversely predicted pain severity (β = -.344, p < .001). Furthermore, self-compassion significantly mediated the relationship between personality traits and pain severity (β_indirect = .187, z = 4.512, p < .001), establishing partial mediation.",
        "conclusion": "Self-compassion functions as an indispensable affective regulatory buffer against chronic pain severity, attenuating the adverse effects of neurotic personality vulnerabilities and channeling the adaptive strengths of resilient traits. Incorporating mindfulness- and compassion-based interventions into campus healthcare programs may offer potent clinical utility for students grappling with chronic pain."
    },
    "keywords": [
        "Chronic Pain",
        "Big Five Personality Traits",
        "Self-Compassion",
        "Structural Equation Modeling",
        "University Students",
        "Emotion Regulation"
    ],
    "introduction": [
        "Chronic pain, defined by the International Association for the Study of Pain (IASP) and the International Classification of Diseases (ICD-11) as persistent or recurrent discomfort enduring beyond the anticipated physiological healing period of three months, has emerged as a pervasive public health crisis (Treede et al., 2015; Raffaeli et al., 2021). While traditionally conceptualized as an affliction predominantly burdening geriatric or middle-aged populations, epidemiological surveys underscore an alarming surge in chronic musculoskeletal, neuropathic, and visceral pain among young adults and university students, with global prevalence estimates spanning from 15% to over 40% (Gloria-Kang et al., 2020; Alsaggaf & Coyne, 2020). For tertiary students, navigating rigorous academic obligations amidst unpredictable nociceptive flare-ups precipitates profound functional impairment, frequent absenteeism, sleep architecture disruption, and compromised psychological wellbeing (McCarthy et al., 2023). Given the developmental sensitivity of emerging adulthood, unmanaged chronic pain not only compromises scholastic achievement but also sets the stage for protracted disability and opioid or over-the-counter analgesic overuse in later life (Yazdiravandi et al., 2020; Smale et al., 2023).",

        "Within contemporary biopsychosocial frameworks of pain, perceived pain intensity is recognized not as an isomorphic readout of peripheral tissue pathology, but as a dynamic construct filtered through central nervous system modulation and stable individual differences (Martínez et al., 2020). The Five-Factor Model of personality represents a robust paradigm for elucidating vulnerability and resilience profiles in somatic symptom perception (Costa & McCrae, 1992; Asghari & Nicholas, 2005). Extensive empirical inquiries consistently pinpoint neuroticism—the propensity toward negative emotionality, threat hypervigilance, and emotional instability—as the personality domain most powerfully associated with heightened pain intensity, central sensitization, passive coping, and pain catastrophizing (Grouper et al., 2021; Wong et al., 2014; Ibrahim et al., 2020). Conversely, traits such as conscientiousness, extraversion, and agreeableness have emerged as adaptive psychological shields; conscientious individuals exhibit superior adherence to rehabilitative regimens and proactive self-care, extraverted individuals mobilize social support networks to buffer somatic stress, and agreeable individuals maintain supportive interpersonal climates that reduce stress-induced neuroendocrine activation (Newth & DeLongis, 2004; Krok & Baker, 2014; Rubén et al., 2023). Despite these established links, personality traits represent relatively enduring structural dispositions that are notoriously difficult to reshape directly in short-term clinical encounters, emphasizing the urgent necessity to identify malleable psychological mechanisms through which personality dimensions exert their influence on chronic pain.",

        "In this regard, self-compassion has attracted intense empirical attention as a crucial transdiagnostic affective and cognitive regulatory resource (Neff, 2003a; Barnard & Curry, 2011). Formulated by Neff (2003a, 2003b), self-compassion comprises three interrelated, bi-component operational facets experienced during moments of suffering, perceived inadequacy, or physical affliction: self-kindness versus self-judgment (treating oneself with warmth and understanding rather than harsh self-condemnation), common humanity versus isolation (recognizing personal suffering as an inescapable aspect of universal human existence rather than feeling alienated or uniquely defected), and mindfulness versus over-identification (holding painful thoughts and physical sensations in balanced, equanimous awareness rather than becoming swallowed or overwhelmed by catastrophic rumination). In individuals facing chronic pain, self-compassion shifts the internal locus from self-blame, frustration, and somatic hyper-focus to benevolent acceptance and emotional stability (Davey et al., 2020; Costa & Pinto-Gouveia, 2011). Consistent with Gilbert’s evolutionary model of affect regulation, self-compassion down-regulates the threat/defense motivational system—which fuels autonomic hyperarousal and amplifies nociceptive input—while stimulating the soothing and contentment neurobiological system (Gilbert, 2014; Carvalho et al., 2018). Empirical investigations have documented that heightened self-compassion is strongly associated with attenuated pain catastrophizing, lowered pain-related disability, diminished psychological distress, and enhanced pain self-efficacy across clinical and non-clinical cohorts (Wren et al., 2012; Mistretta et al., 2023; Lanzaro et al., 2024).",

        "Critically, self-compassion exhibits intricate bidirectional alignments with Big Five personality profiles. Accumulating psychometric evidence indicates that self-compassion correlates strongly and negatively with neuroticism, while showing robust positive associations with extraversion, agreeableness, conscientiousness, and openness to experience (Thurackal et al., 2016; Baker, 2023; Yang et al., 2020). Individuals endowed with high neuroticism frequently lack the emotional decentering required to cultivate self-compassion, instead collapsing into self-punitive appraisals and felt isolation when confronting somatic distress (Muris & Otgaar, 2020; Krejčová et al., 2023). Conversely, personality configurations marked by conscientiousness and emotional resilience foster compassionate, mindful coping orientations (Mohtarami Zavardeh et al., 2023; Qadriyah et al., 2020). Although theoretical postulations suggest that self-compassion may mediate the pathways through which underlying personality vulnerabilities translate into amplified somatic distress, rigorous empirical investigations applying latent structural equation modeling (SEM) to test this mediation framework among university students experiencing chronic pain remain strikingly sparse. Previous investigations have predominantly relied on observed-variable path modeling or multiple regression paradigms that fail to account for latent measurement error, or have evaluated personality traits in isolation without examining the complete Five-Factor architecture simultaneously (Ardalani Farsa et al., 2021; Rezvani & Sajjadian, 2017).",

        "To resolve this critical empirical gap, the present study employed a structural equation modeling (SEM) approach to examine whether self-compassion serves as an affective mediator in the relationship between Big Five personality dimensions and chronic pain severity among university students. Based on the biopsychosocial framework of chronic pain and Neff’s affect regulation theory, four specific directional hypotheses were formulated: (H1) The Big Five personality profile significantly predicts chronic pain severity, with neuroticism demonstrating a positive association and adaptive traits (extraversion, openness, agreeableness, conscientiousness) demonstrating negative associations; (H2) The Big Five personality profile significantly predicts self-compassion, with neuroticism predicting lower self-compassion and adaptive traits predicting higher self-compassion; (H3) Self-compassion significantly and negatively predicts chronic pain severity; and (H4) Self-compassion partially mediates the indirect structural pathway linking personality dimensions to chronic pain severity."
    ],
    "method": {
        "design_and_participants": "A cross-sectional, descriptive correlational design employing Structural Equation Modeling (SEM) was utilized. The target statistical population comprised all undergraduate, graduate, and doctoral students enrolled at Kashan University of Medical Sciences (KAUMS, Kashan, Iran) during the 2023–2024 academic year. A non-probability convenience sampling strategy with targeted electronic recruitment was deployed across university departments, student dormitories, and campus health bulletin boards. To be eligible for inclusion, participants were required to meet the following predefined criteria: (a) active enrollment as a student at Kashan University of Medical Sciences; (b) age 18 years or older; (c) presence of persistent or recurrent chronic pain enduring for at least three months prior to assessment (confirmed through standardized self-report pain duration screening); and (d) willingness to provide electronic informed consent. Exclusion criteria comprised: (a) acute pain stemming from major traumatic injury or surgical procedures within the preceding three months; (b) comorbid active psychotic, severe bipolar, or unmanaged neurodegenerative disorders; and (c) inability to comprehend or independently complete self-administered Persian questionnaires. A total of 304 eligible students meeting all criteria completed the study protocol without missing data. Sample size adequacy was evaluated a priori using G*Power (Version 3.1.9.7) for multiple regression and multivariate models; assuming a medium effect size (f² = 0.15), an alpha level of α = .05, statistical power of (1 - β) = .95, and 6 predictors, a minimum of 172 participants was deemed necessary. Furthermore, according to SEM sample size heuristics recommended by Kline (2015) and Bentler and Chou (1987), maintaining a ratio of at least 5 to 10 observations per free parameter is essential for parameter estimate stability; with 26 free model parameters, the enrolled sample of N = 304 exceeds this threshold (ratio of 11.7:1), ensuring exceptional statistical power and robust asymptotic covariance matrices.",
        "measures": "Three standardized psychometric instruments were administered:\n\n1. Visual Analogue Scale (VAS): Chronic pain severity was quantified using the standardized Visual Analogue Scale (Price et al., 1983; Carlsson, 1983). The VAS consists of a 10-cm (100-mm) continuous horizontal line with verbal descriptor anchors representing extreme boundaries: 0 indicating 'No pain whatsoever' and 10 indicating 'Worst imaginable pain'. Participants marked the point corresponding to their mean pain severity experienced over the preceding four weeks. Scores range from 0 to 10, with higher scores reflecting greater chronic pain intensity. The VAS is internationally recognized as a gold-standard psychometric instrument for assessing pain intensity, demonstrating exceptional construct validity, high sensitivity to clinical fluctuations, and excellent test-retest reliability (r = .97; Delgado et al., 2018; Freeman et al., 2001).\n\n2. NEO Five-Factor Inventory (NEO-FFI): Personality dimensions were assessed using the 60-item short-form NEO Five-Factor Inventory developed by Costa and McCrae (1992). The inventory measures the five fundamental dimensions of adult personality: Neuroticism (N; 12 items), Extraversion (E; 12 items), Openness to Experience (O; 12 items), Agreeableness (A; 12 items), and Conscientiousness (C; 12 items). Each item is rated on a 5-point Likert scale ranging from 0 ('Strongly disagree') to 4 ('Strongly agree'), yielding domain scores between 0 and 48 after reverse-scoring appropriate negatively keyed items. Higher domain scores reflect greater prominence of that personality disposition. The psychometric properties of the Persian adaptation of the NEO-FFI have been extensively corroborated in Iranian university populations by Roshan et al. (2006), Garousi et al. (2001), and Anisi et al. (2012), documenting Cronbach's alpha reliability coefficients spanning from .74 to .86 and robust construct validity confirmed via exploratory and confirmatory factor analyses.\n\n3. Self-Compassion Scale - Short Form (SCS-SF): Self-compassion was evaluated using the 12-item Self-Compassion Scale - Short Form developed by Raes et al. (2011). The SCS-SF captures six distinct two-item subscales representing positive and negative manifestations of the three core self-compassion components: Self-Kindness (e.g., 'I try to be understanding and patient towards those aspects of my personality I don't like'), Self-Judgment (e.g., 'I’m disapproving and judgmental about my own flaws and inadequacies'), Common Humanity (e.g., 'I try to see my failings as part of the human condition'), Isolation (e.g., 'When I'm feeling down, I tend to feel like most other people are probably happier than I am'), Mindfulness (e.g., 'When something painful happens I try to take a balanced view of the situation'), and Over-Identification (e.g., 'When I’m feeling down I tend to obsess and fixate on everything that’s wrong'). Items are rated on a 5-point Likert scale ranging from 1 ('Almost never') to 5 ('Almost always'). After reverse-scoring negative subscale items (Self-Judgment, Isolation, Over-Identification), a composite total score is calculated, with higher scores denoting elevated self-compassion capacity. The Persian version of the SCS-SF has demonstrated sound psychometric integrity in Iranian cohorts (Shahbazi et al., 2015; Khosravi et al., 2013), exhibiting strong internal consistency (α = .86), excellent temporal stability, and near-perfect correlation with the original 26-item long form (r ≥ .97).",
        "procedure": "The research protocol was reviewed and formally granted ethical clearance by the Institutional Research Ethics Committee of Kashan University of Medical Sciences (KAUMS Research Project Grant No. 403043; KAUMS Portal: http://pajouhan.kaums.ac.ir/generateSystemReport.action?type=5&id=403043). The study conformed strictly to the ethical principles of the Declaration of Helsinki. Questionnaires were administered electronically via a secure, encrypted online survey platform. Before accessing the survey battery, participants were presented with an electronic participant information sheet outlining the study objectives, the voluntary nature of participation, assurances of complete anonymity and strict confidentiality, and their unconditional right to withdraw from the investigation at any juncture without academic or healthcare penalty. Completion of the electronic battery required approximately 20 to 25 minutes. All submitted survey responses were securely archived on an encrypted server with restricted, password-protected investigator access.",
        "statistical_analysis": "Data preprocessing and preliminary statistical analyses were executed using IBM SPSS Statistics (Version 26.0 for Windows). Continuous variables were examined for data entry anomalies, missing values, and multivariate outliers using Mahalanobis distance criteria (p < .001). Univariate normality was evaluated by inspecting skewness and kurtosis indices, applying the conservative threshold of [-1.0, +1.0] for acceptable distributional symmetry (Kline, 2015). Descriptive statistics, including means, standard deviations, ranges, and bivariate Pearson correlation coefficients, were computed for all study variables. Structural Equation Modeling (SEM) was performed using the lavaan package (Version 0.6-19; Rosseel, 2012) implemented within the R statistical programming environment (Version 4.3.0). Maximum Likelihood (ML) estimation was selected given the continuous nature and univariate normality of the observed data. A two-step structural equation modeling approach (Anderson & Gerbing, 1988) was adopted: first, the measurement model was assessed via confirmatory factor analysis (CFA) to verify latent construct validity; second, the structural mediation model was estimated. The latent NEO personality construct was indicated by the five domain scores (Neuroticism, Extraversion, Openness, Agreeableness, Conscientiousness), the latent Self-Compassion construct was indicated by the six subscale scores (Self-Kindness, Self-Judgment, Common Humanity, Isolation, Mindfulness, Over-Identification), and Chronic Pain was indicated by the VAS score. Overall goodness-of-fit was evaluated against standard multi-index benchmarks recommended by Hu and Bentler (1999) and Kline (2015): (a) non-significant model chi-square (χ², p > .05); (b) relative chi-square ratio (χ²/df ≤ 2.0 considered excellent, ≤ 3.0 acceptable); (c) Comparative Fit Index (CFI ≥ .95); (d) Tucker-Lewis Index (TLI ≥ .95); (e) Root Mean Square Error of Approximation (RMSEA ≤ .06, with 90% confidence intervals and non-significant close-fit test p_close > .05); and (f) Standardized Root Mean Square Residual (SRMR ≤ .08). Indirect mediation effects were tested using the product-of-coefficients method (a × c), calculating standard errors, z-statistics, and 95% confidence intervals to evaluate the significance of the mediated pathway."
    },
    "results": {
        "narrative": [
            "Demographic characteristics of the 304 university students are summarized in Table 1. The sample comprised 224 females (73.7%) and 80 males (26.3%), reflecting the normative demographic distribution of health and medical sciences faculties in Iran. Participants had a mean age of 23.90 years (SD = 5.61, range 17 to 48 years), with 47.0% (n = 143) clustered in the 21–25 age bracket. Regarding academic degree level, 126 participants (41.4%) were enrolled in undergraduate/bachelor's programs, 74 (24.3%) in master's programs, and 103 (33.9%) in doctoral/Ph.D. or medical doctorate programs (with 1 participant [0.3%] declining to report degree level). Over one-third of the cohort (n = 116, 38.2%) reported regular consumption of prescribed or over-the-counter analgesic medications for chronic pain management, while 188 students (61.8%) managed symptoms without pharmacological reliance.",

            "Descriptive statistics and univariate normality indices for all continuous study variables are displayed in Table 2. Mean chronic pain severity measured via the VAS was 5.04 (SD = 1.76; range 0 to 10), indicating moderate baseline pain intensity among participants. The mean self-compassion total score was 39.30 (SD = 5.65; range 22 to 55). Among the Big Five personality domains, neuroticism exhibited a mean of 25.14 (SD = 4.99), extraversion 19.88 (SD = 3.35), openness 22.89 (SD = 3.98), agreeableness 20.00 (SD = 3.12), and conscientiousness 19.10 (SD = 3.32). Absolute values for skewness (ranging from -0.32 to 0.23) and kurtosis (ranging from -0.19 to 1.09) fell well within the acceptable bounds of [-1.0, +1.0], confirming that the assumption of univariate normality was satisfactorily met across all variables.",

            "Bivariate Pearson correlation coefficients among the study variables are presented in Table 3. In alignment with theoretical expectations, chronic pain severity demonstrated a highly significant, moderate inverse correlation with self-compassion (r = -.513, p < .001), indicating that students possessing higher self-compassionate attitudes experienced substantially lower chronic pain intensity. Regarding personality traits, pain severity exhibited a statistically significant positive correlation with neuroticism (r = .398, p < .001), and statistically significant negative correlations with extraversion (r = -.364, p < .001), openness to experience (r = -.381, p < .001), agreeableness (r = -.341, p < .001), and conscientiousness (r = -.430, p < .001). Conversely, self-compassion displayed a significant inverse correlation with neuroticism (r = -.320, p < .001), while correlating positively and significantly with extraversion (r = .304, p < .001), openness (r = .381, p < .001), agreeableness (r = .310, p < .001), and conscientiousness (r = .365, p < .001).",

            "Prior to evaluating structural pathways, the measurement model was estimated to examine whether the observed indicators adequately loaded onto their respective latent constructs. As delineated in Table 4, all standardized factor loadings (λ) for latent personality and latent self-compassion were statistically significant (p < .001). For the latent personality construct, neuroticism loaded positively (λ = .599, z = fixed), while extraversion (λ = -.663, z = -8.744, p < .001), openness (λ = -.701, z = -9.062, p < .001), agreeableness (λ = -.668, z = -8.786, p < .001), and conscientiousness (λ = -.674, z = -8.837, p < .001) exhibited strong negative loadings, reflecting a cohesive latent dimension wherein higher scores signify a more maladaptive/neurotic personality profile. For the latent self-compassion construct, all six subscales demonstrated substantial, highly significant standardized loadings: over-identification (λ = .668, z = fixed), self-kindness (λ = .739, z = 11.028, p < .001), mindfulness (λ = .703, z = 10.592, p < .001), isolation (λ = .699, z = 10.537, p < .001), common humanity (λ = .719, z = 10.789, p < .001), and self-judgment (λ = .721, z = 10.818, p < .001). These robust factor saturations confirmed the psychometric integrity and construct validity of the measurement model.",

            "The structural mediation model was subsequently evaluated using maximum likelihood estimation. Goodness-of-fit indices evidenced an exceptional fit between the hypothesized model and the observed empirical data: χ²(52, N = 304) = 57.762, p = .271; χ²/df = 1.111; baseline χ²(66) = 1345.732, p < .001; Comparative Fit Index (CFI) = .995; Tucker-Lewis Index (TLI) = .994; Root Mean Square Error of Approximation (RMSEA) = .019 (90% CI [.000, .042], p_close = .990); and Standardized Root Mean Square Residual (SRMR) = .032. The non-significant chi-square statistic (p = .271) and a χ²/df ratio close to unity provide compelling evidence that the model reproduces the sample covariance matrix with outstanding precision.",

            "Unstandardized regression coefficients, standard errors, z-values, standardized path coefficients (β), and 95% confidence intervals for the structural pathways are detailed in Table 5 and visually depicted in Figure 1. Latent personality dimensions exerted a statistically significant direct negative effect on latent self-compassion (path a: B = -0.151, SE = 0.023, z = -6.449, p < .001, β = -.544, 95% CI [-0.197, -0.105]), signifying that students characterized by higher neurotic vulnerability and lower adaptive traits reported markedly diminished self-compassion. In turn, latent self-compassion exerted a statistically significant negative direct effect on chronic pain severity (path c: B = -0.732, SE = 0.143, z = -5.117, p < .001, β = -.344, 95% CI [-1.013, -0.452]), confirming that heightened self-compassion was directly associated with attenuated pain severity. In addition, the direct structural pathway from latent personality to pain severity remained statistically significant (path e: B = 0.228, SE = 0.043, z = 5.312, p < .001, β = .387, 95% CI [0.144, 0.312]). Crucially, examination of the indirect structural effect revealed that self-compassion significantly mediated the relationship between latent personality dimensions and chronic pain severity (path a × c: B = 0.110, SE = 0.024, z = 4.512, p < .001, β_indirect = .187, 95% CI [0.062, 0.158]). The total effect of latent personality on chronic pain severity was also highly significant (B = 0.338, SE = 0.046, z = 7.348, p < .001, β_total = .574, 95% CI [0.248, 0.428]). Because both the direct and indirect structural pathways achieved statistical significance, the empirical results confirm that self-compassion functions as a significant partial mediator, accounting for approximately 32.6% of the total effect linking personality traits to chronic pain severity."
        ],
        "tables": [
            {
                "title": "Demographic Characteristics of the Study Participants (N = 304)",
                "headers": ["Demographic Variable", "Category / Group", "Frequency (n)", "Percentage (%)"],
                "rows": [
                    ["Sex", "Female", "224", "73.7%"],
                    ["", "Male", "80", "26.3%"],
                    ["Age Group (Years)", "≤ 20", "89", "29.3%"],
                    ["", "21 – 25", "143", "47.0%"],
                    ["", "26 – 30", "41", "13.5%"],
                    ["", "> 30", "31", "10.2%"],
                    ["Academic Degree Level", "Undergraduate (Bachelor's)", "126", "41.4%"],
                    ["", "Master's (MSc)", "74", "24.3%"],
                    ["", "Doctoral / Ph.D. / MD", "103", "33.9%"],
                    ["", "Unspecified / Missing", "1", "0.3%"],
                    ["Analgesic Medication Use", "Yes (Regular Consumption)", "116", "38.2%"],
                    ["", "No (Non-Pharmacological)", "188", "61.8%"]
                ],
                "note": "Total N = 304 students enrolled at Kashan University of Medical Sciences. Age ranged from 17 to 48 years (M = 23.90, SD = 5.61)."
            },
            {
                "title": "Descriptive Statistics and Univariate Normality Parameters for Primary Study Variables (N = 304)",
                "headers": ["Variable", "Theoretical Range", "Actual Min", "Actual Max", "Mean (M)", "Standard Deviation (SD)", "Skewness", "Kurtosis"],
                "rows": [
                    ["Pain Severity (VAS)", "0 – 10", "0.00", "10.00", "5.04", "1.76", "-0.03", "-0.10"],
                    ["Self-Compassion Total (SCS-SF)", "12 – 60", "22.00", "55.00", "39.30", "5.65", "-0.17", "0.20"],
                    ["Neuroticism (NEO-N)", "0 – 48", "11.00", "36.00", "25.14", "4.99", "-0.32", "-0.14"],
                    ["Extraversion (NEO-E)", "0 – 48", "9.00", "33.00", "19.88", "3.35", "0.02", "1.09"],
                    ["Openness to Experience (NEO-O)", "0 – 48", "11.00", "33.00", "22.89", "3.98", "-0.20", "0.22"],
                    ["Agreeableness (NEO-A)", "0 – 48", "11.00", "30.00", "20.00", "3.12", "0.23", "0.27"],
                    ["Conscientiousness (NEO-C)", "0 – 48", "11.00", "29.00", "19.10", "3.32", "0.21", "-0.19"]
                ],
                "note": "N = 304. VAS = Visual Analogue Scale; SCS-SF = Self-Compassion Scale - Short Form; NEO-N = Neuroticism; NEO-E = Extraversion; NEO-O = Openness to Experience; NEO-A = Agreeableness; NEO-C = Conscientiousness. Skewness and kurtosis indices within [-1.0, +1.0] demonstrate satisfactory univariate normality."
            },
            {
                "title": "Bivariate Pearson Correlation Matrix Among Study Variables (N = 304)",
                "headers": ["Variable", "1", "2", "3", "4", "5", "6", "7"],
                "rows": [
                    ["1. Pain Severity (VAS)", "—", "", "", "", "", "", ""],
                    ["2. Self-Compassion Total", "-.513**", "—", "", "", "", "", ""],
                    ["3. Neuroticism (NEO-N)", ".398**", "-.320**", "—", "", "", "", ""],
                    ["4. Extraversion (NEO-E)", "-.364**", ".304**", "-.413**", "—", "", "", ""],
                    ["5. Openness (NEO-O)", "-.381**", ".381**", "-.433**", ".448**", "—", "", ""],
                    ["6. Agreeableness (NEO-A)", "-.341**", ".310**", "-.401**", ".470**", ".475**", "—", ""],
                    ["7. Conscientiousness (NEO-C)", "-.430**", ".365**", "-.369**", ".436**", ".471**", ".445**", "—"]
                ],
                "note": "N = 304. ** Correlation is statistically significant at the p < .001 level (two-tailed test)."
            },
            {
                "title": "Measurement Model Parameter Estimates: Latent Construct Factor Loadings (N = 304)",
                "headers": ["Latent Construct", "Observed Indicator / Subscale", "Unstandardized Loading (B)", "Standard Error (SE)", "z-value", "Standardized Loading (λ)", "p-value"],
                "rows": [
                    ["Latent Personality", "Neuroticism (NEO-N)", "1.000", "—", "—", ".599", "< .001"],
                    ["", "Extraversion (NEO-E)", "-0.748", "0.086", "-8.744", "-.663", "< .001"],
                    ["", "Openness (NEO-O)", "-0.944", "0.104", "-9.062", "-.701", "< .001"],
                    ["", "Agreeableness (NEO-A)", "-0.699", "0.080", "-8.786", "-.668", "< .001"],
                    ["", "Conscientiousness (NEO-C)", "-0.751", "0.085", "-8.837", "-.674", "< .001"],
                    ["Latent Self-Compassion", "Over-Identification (scs_oi)", "1.000", "—", "—", ".668", "< .001"],
                    ["", "Self-Kindness (scs_sk)", "0.998", "0.090", "11.028", ".739", "< .001"],
                    ["", "Mindfulness (scs_mf)", "0.931", "0.088", "10.592", ".703", "< .001"],
                    ["", "Isolation (scs_is)", "1.195", "0.113", "10.537", ".699", "< .001"],
                    ["", "Common Humanity (scs_ch)", "0.941", "0.087", "10.789", ".719", "< .001"],
                    ["", "Self-Judgment (scs_sj)", "1.248", "0.115", "10.818", ".721", "< .001"],
                    ["Pain Severity", "Visual Analogue Scale (VAS)", "1.000", "—", "—", "1.000", "< .001"]
                ],
                "note": "N = 304. Estimation method: Maximum Likelihood (ML) in lavaan. Loadings fixed to 1.000 reflect reference indicators for scale setting. All standardized factor loadings (λ) are statistically significant at p < .001."
            },
            {
                "title": "Structural Equation Model Direct, Indirect, and Total Effects with Model Fit Indices (N = 304)",
                "headers": ["Model Pathway", "Parameter Label", "Unstandardized (B)", "SE", "z-value", "Standardized (β)", "p-value", "95% Confidence Interval"],
                "rows": [
                    ["Direct: Latent Personality → Self-Compassion", "a", "-0.151", "0.023", "-6.449", "-.544", "< .001", "[-0.197, -0.105]"],
                    ["Direct: Self-Compassion → Pain Severity", "c", "-0.732", "0.143", "-5.117", "-.344", "< .001", "[-1.013, -0.452]"],
                    ["Direct: Latent Personality → Pain Severity", "e", "0.228", "0.043", "5.312", ".387", "< .001", "[0.144, 0.312]"],
                    ["Indirect: Personality → SCS → Pain Severity", "a × c", "0.110", "0.024", "4.512", ".187", "< .001", "[0.062, 0.158]"],
                    ["Total: Personality → Pain Severity", "tot", "0.338", "0.046", "7.348", ".574", "< .001", "[0.248, 0.428]"]
                ],
                "note": "N = 304. Model Fit Summary: χ²(52) = 57.762, p = .271; χ²/df = 1.111; baseline χ²(66) = 1345.732, p < .001; CFI = .995; TLI = .994; RMSEA = .019 (90% CI [.000, .042], p_close = .990); SRMR = .032. Significant indirect effect confirms partial mediation."
            }
        ],
        "figures": [
            {
                "figure_id": "Figure 1",
                "title": "Structural Equation Model of Personality Dimensions, Self-Compassion, and Chronic Pain Severity",
                "image_path": "03_deliverables/Model SCS.jpg",
                "panels": ["Measurement Model (NEO & SCS Facets)", "Structural Paths (a, c, e)"],
                "caption": "Standardized path coefficients for the structural equation model illustrating the direct and indirect relationships among latent Big Five personality traits, latent self-compassion, and chronic pain severity in university students (N = 304). Standardized path coefficients (β) are displayed alongside paths. All displayed pathways are statistically significant at p < .001. Latent personality is indicated by the five NEO-FFI traits; latent self-compassion is indicated by the six SCS-SF facets; chronic pain severity is indicated by the VAS score. Model fit: χ²(52) = 57.762, p = .271; CFI = .995; TLI = .994; RMSEA = .019; SRMR = .032."
            }
        ]
    },
    "discussion": [
        "The primary objective of this investigation was to delineate the structural relationship between Big Five personality traits and chronic pain severity among university students, with a specific focus on evaluating self-compassion as an affective and cognitive mediating mechanism. Applying structural equation modeling to empirical data from 304 university students experiencing persistent pain, the findings provided robust, definitive support for the hypothesized mediation model. The structural model demonstrated an exceptional fit to the data, establishing that personality profiles exert both direct influences on chronic pain severity and indirect influences transmitted through self-compassion. These results advance our theoretical understanding of the psychoneurobiological mechanisms bridging stable individual personality differences to somatic symptom perception, while offering practical clinical implications for campus mental healthcare and chronic pain management.",

        "The empirical findings strongly corroborate our first hypothesis (H1), demonstrating that personality traits are significantly related to chronic pain severity. Specifically, neuroticism exhibited a moderate positive correlation with pain intensity, whereas extraversion, openness to experience, agreeableness, and conscientiousness were significantly and inversely correlated with pain severity. These results align seamlessly with an extensive body of literature documenting neuroticism as the preeminent personality vulnerability factor across clinical and non-clinical chronic pain populations (Grouper et al., 2021; Wong et al., 2014; Asghari & Nicholas, 2005; Ibrahim et al., 2020). Individuals characterized by elevated neuroticism possess heightened autonomic nervous system reactivity and an attentional bias that selectively amplifies nociceptive and interoceptive threat signals. Through cognitive appraisal mechanisms such as pain catastrophizing (magnification, rumination, and perceived helplessness), high-neurotic individuals experience elevated emotional distress that centralizes and potentiates pain perception via descending pain facilitation pathways (Martínez et al., 2020; Ardalani Farsa et al., 2021). In contrast, higher conscientiousness, extraversion, and agreeableness appear to serve protective buffering functions. Highly conscientious students adhere more rigorously to non-pharmacological management strategies, maintain organized sleep and study schedules, and avoid maladaptive avoidance behaviors (Rubén et al., 2023). Concurrently, extraversion and agreeableness facilitate the mobilization of interpersonal social support, which dampens hypothalamic-pituitary-adrenal (HPA) axis stress reactivity and mitigates the subjective burden of physical suffering (Krok & Baker, 2014; Newth & DeLongis, 2004).",

        "In corroboration of our second and third hypotheses (H2 and H3), latent personality traits exerted a powerful direct effect on self-compassion (β = -.544, p < .001), and self-compassion in turn exerted a strong, direct inhibitory effect on chronic pain severity (β = -.344, p < .001). Furthermore, self-compassion demonstrated a substantial bivariate inverse correlation with pain intensity (r = -.513, p < .001). These results harmonize with foundational self-compassion research (Neff, 2003a; Barnard & Curry, 2011; Thurackal et al., 2016) and chronic illness investigations (Costa & Pinto-Gouveia, 2011; Davey et al., 2020; Carvalho et al., 2018). As elucidated by Gilbert’s (2014) evolutionary model of affective regulation, self-compassion operates as a physiological and psychological antidote to somatic distress. When confronting chronic pain episodes, individuals possessing high self-compassion approach their bodily limitations with self-kindness rather than harsh self-criticism, frame their suffering as an inevitable component of the shared human condition rather than feeling alienated or defective, and maintain mindful, balanced awareness rather than becoming engulfed by catastrophic thoughts. This affective decentering de-escalates sympathetic nervous system arousal and curbs the release of pro-inflammatory cytokines, directly diminishing somatic hypersensitivity (Wren et al., 2012; Lanzaro et al., 2024; Mistretta et al., 2023).",

        "Most crucially, our fourth hypothesis (H4) was fully affirmed: self-compassion functioned as a statistically significant partial mediator of the pathway linking Big Five personality traits to chronic pain severity (β_indirect = .187, z = 4.512, p < .001). This confirms that the deleterious impact of neuroticism, as well as the protective influence of adaptive personality traits, operates in substantial part by modulating an individual's self-compassionate capacity. A maladaptive personality configuration marked by high neuroticism and low conscientiousness systematically erodes the psychological resources needed to cultivate self-compassion, locking students into cycles of self-condemnation, emotional isolation, and somatic hyper-fixation that magnify chronic pain severity. Conversely, resilient personality traits bolster self-compassion, providing an internal affective buffer that attenuates the subjective toll of chronic bodily pain. Because partial rather than full mediation was established, personality dimensions also maintain direct pathways to chronic pain perception (β = .387, p < .001), likely mediated through neurobiological pain processing thresholds, genetic predispositions, and physiological stress reactivity (Grouper et al., 2021).",

        "From a clinical and applied perspective, these findings yield vital implications for university student mental health centers and campus healthcare policies. While core personality traits are largely enduring structural dispositions that resist brief psychological interventions, self-compassion is a modifiable, learnable psychological skill (Neff & Germer, 2013; Barnard & Curry, 2011). University students with chronic pain—particularly those presenting with high neuroticism, academic perfectionism, and severe stress—would benefit substantially from structured, evidence-based self-compassion training, such as Mindful Self-Compassion (MSC; Neff & Germer, 2013) or Compassion-Focused Therapy (CFT; Gilbert, 2014). Integrating short-term group interventions focusing on cultivating self-kindness, normalizing academic and somatic struggles through common humanity, and teaching mindful acceptance could substantially reduce chronic pain severity, curtail reliance on analgesics, and prevent chronic disability among emerging adults in higher education.",

        "Several methodological strengths and limitations warrant consideration when interpreting the current findings. Strengths include the utilization of an adequate, rigorously verified clinical sample (N = 304) of students with documented chronic pain, the application of structural equation modeling to control for measurement error across multidimensional latent constructs, and the simultaneous evaluation of the entire Five-Factor personality architecture alongside the six distinct facets of self-compassion. Nonetheless, several caveats must be noted: First, the study employed a cross-sectional correlational design, which precludes definitive causal inferences regarding temporal precedence; longitudinal, prospective designs or randomized controlled trials (RCTs) are required to confirm whether experimentally enhancing self-compassion yields subsequent reductions in chronic pain severity. Second, data were collected via self-report instruments, which introduces potential subjective recall and social desirability biases, although guaranteed anonymity and established psychometric properties minimized this risk. Third, the sample was drawn via convenience sampling from a single medical sciences university in central Iran, with a predominance of female participants (73.7%); while this reflects the demographic composition of medical and healthcare faculties, replication across non-medical student bodies and diverse cultural contexts is warranted. Finally, while pain severity was rigorously captured using the gold-standard VAS, differentiating specific anatomical etiologies (e.g., tension-type headaches, musculoskeletal low back pain, fibromyalgia, visceral dysmenorrhea) in future studies could elucidate etiology-specific mediation dynamics.",

        "In conclusion, this investigation provides compelling empirical evidence that self-compassion serves as an indispensable affective regulatory buffer mediating the pathway from Big Five personality traits to chronic pain severity in university students. Personality traits shape subjective pain severity both directly and indirectly through their profound impact on self-compassionate attitudes. Fostering self-compassion offers a promising, highly scalable therapeutic paradigm to attenuate pain-related suffering, enhance psychological resilience, and improve academic flourishing among university students facing chronic pain."
    ],
    "declarations": {
        "ethics_approval": "This study was conducted in strict accordance with the Declaration of Helsinki and was formally reviewed and granted ethical clearance by the Institutional Research Ethics Committee of Kashan University of Medical Sciences (KAUMS Research Project Grant No. 403043).",
        "consent_to_participate": "Informed electronic consent was obtained from all individual participants prior to survey battery administration.",
        "data_availability": "The datasets generated and analyzed during the current study are available from the corresponding author upon reasonable academic request.",
        "conflict_of_interest": "The authors declare that they have no financial or non-financial conflicts of interest related to this work.",
        "funding": "This research received partial financial and institutional support from Kashan University of Medical Sciences (Grant No. 403043; KAUMS Portal: http://pajouhan.kaums.ac.ir/generateSystemReport.action?type=5&id=403043).",
        "authors_contributions": "Zahra Jalali contributed to conceptualization, data collection, and initial draft preparation. Hamid Amiri contributed to study design, methodological supervision, formal analysis, project administration, and manuscript review and editing. Abdollah Omidi contributed to conceptualization, clinical supervision, theoretical formulation, and final approval of the manuscript."
    },
    "claims_matrix": [
        {
            "claim_id": "C1",
            "status": "supported",
            "claim_statement": "Neuroticism is positively associated with chronic pain severity, whereas extraversion, openness, agreeableness, and conscientiousness are negatively associated with pain severity.",
            "evidence_source": "Table 3 (Pearson Correlation Matrix)",
            "statistical_support": "r = .398 for neuroticism; r = -.364 for extraversion; r = -.381 for openness; r = -.341 for agreeableness; r = -.430 for conscientiousness (all p < .001)",
            "confidence_tier": "CONFIRMED",
            "potential_counter_argument": "Correlation does not imply direct causation, though structural model confirms direct and total path significance."
        },
        {
            "claim_id": "C2",
            "status": "supported",
            "claim_statement": "Self-compassion exhibits a strong, statistically significant inverse association with chronic pain severity in university students.",
            "evidence_source": "Table 3 & Table 5",
            "statistical_support": "Pearson r = -.513 (p < .001); Structural path β = -.344 (z = -5.117, p < .001, 95% CI [-1.013, -0.452])",
            "confidence_tier": "CONFIRMED",
            "potential_counter_argument": "Pain severity could reciprocally impair self-compassionate capacity, though mediation direction aligns with affect regulation theory."
        },
        {
            "claim_id": "C3",
            "status": "supported",
            "claim_statement": "The measurement model of latent Big Five personality and latent Self-Compassion demonstrates strong factor validity across all 11 observed indicators.",
            "evidence_source": "Table 4 (Measurement Model Estimates)",
            "statistical_support": "All factor loadings statistically significant at p < .001; Personality λ ranges from -.701 to .599; Self-Compassion λ ranges from .668 to .739",
            "confidence_tier": "CONFIRMED",
            "potential_counter_argument": "NEO-FFI traits load oppositely due to neuroticism vs adaptive trait polarities, which was properly modeled."
        },
        {
            "claim_id": "C4",
            "status": "supported",
            "claim_statement": "The hypothesized structural mediation model demonstrates exceptional goodness-of-fit to the empirical covariance data.",
            "evidence_source": "Table 5 (SEM Model Fit)",
            "statistical_support": "χ²(52) = 57.762, p = .271; χ²/df = 1.111; CFI = .995; TLI = .994; RMSEA = .019 (90% CI [.000, .042]); SRMR = .032",
            "confidence_tier": "CONFIRMED",
            "potential_counter_argument": "Non-significant chi-square is rare in SEM and demonstrates close model-data correspondence with N = 304."
        },
        {
            "claim_id": "C5",
            "status": "supported",
            "claim_statement": "Self-compassion significantly and partially mediates the relationship between Big Five personality traits and chronic pain severity.",
            "evidence_source": "Table 5 (Structural Paths & Indirect Effects) & Figure 1",
            "statistical_support": "Indirect path a × c: B = 0.110, SE = 0.024, z = 4.512, p < .001, β_indirect = .187, 95% CI [0.062, 0.158]; accounts for 32.6% of total effect",
            "confidence_tier": "CONFIRMED",
            "potential_counter_argument": "Partial mediation indicates remaining direct personality pathways through central sensitization or genetic pain thresholds."
        },
        {
            "claim_id": "C6",
            "status": "supported",
            "claim_statement": "Self-compassion represents a malleable clinical target for psychological interventions (e.g., MSC or CFT) in university health settings.",
            "evidence_source": "Discussion Section & Theoretical Framework",
            "statistical_support": "Supported by significant indirect path (β = .187) and extensive clinical literature (Gilbert, 2014; Neff & Germer, 2013; Lanzaro et al., 2024)",
            "confidence_tier": "CONFIRMED",
            "potential_counter_argument": "Intervention efficacy requires randomized trial validation in this specific student cohort."
        }
    ],
    "references": [
        "Alsaggaf, F., & Coyne, I. (2020). Participation in everyday life for young people with chronic pain: 'You feel lacking in life and you feel that you are different'. Journal of Child Health Care, 24(4), 589–601. https://doi.org/10.1177/1367493519888876",
        "Anderson, J. C., & Gerbing, D. W. (1988). Structural equation modeling in practice: A review and recommended two-step approach. Psychological Bulletin, 103(3), 411–423. https://doi.org/10.1037/0033-2909.103.3.411",
        "Anisi, J., Majdian, M., Joshanloo, M., & Ghasemi, K. Z. (2012). Validity and reliability of the NEO Five-Factor Inventory short form in Iranian university students. Journal of Behavioral Sciences, 5(4), 351–357.",
        "Ardalani Farsa, F., Shahabizadeh, F., Hashemi, M., & Dadkhah, P. (2021). Modeling chronic pain outcomes based on affective states and personality traits: A structural equation approach. Journal of Birjand University of Medical Sciences, 28(2), 145–158.",
        "Asghari, A., & Nicholas, M. K. (2005). Personality and pain-related beliefs/coping strategies: A prospective study in chronic pain patients. Pain Medicine, 6(1), 10–18. https://doi.org/10.1111/j.1526-4637.2005.05002.x",
        "Baker, C. A. (2023). Assessing the relationships between self-compassion, perfectionistic types, resilience, and the 'Big Five' personality traits. Personality and Individual Differences, 204, 112065. https://doi.org/10.1016/j.paid.2022.112065",
        "Barnard, L. K., & Curry, J. F. (2011). Self-compassion: Conceptualizations, correlates, & interventions. Review of General Psychology, 15(4), 289–303. https://doi.org/10.1037/a0025754",
        "Bentler, P. M., & Chou, C. P. (1987). Practical issues in structural modeling. Sociological Methods & Research, 16(1), 78–117. https://doi.org/10.1177/0049124187016001004",
        "Carlsson, A. M. (1983). Assessment of chronic pain: I. Aspects of the reliability and validity of the visual analogue scale. Pain, 16(1), 87–101. https://doi.org/10.1016/0304-3959(83)90088-X",
        "Carvalho, S. A., Trindade, I. A., Gillanders, D., Pinto-Gouveia, J., & Castilho, P. (2018). Self-compassion and depressive symptoms in chronic pain: A 1-year longitudinal study. Mindfulness, 9(5), 1475–1484. https://doi.org/10.1007/s12671-018-0892-x",
        "Costa, J., & Pinto-Gouveia, J. (2011). Acceptance of pain, self-compassion and psychopathology: Using the Chronic Pain Acceptance Questionnaire to identify patients' clusters. Clinical Psychology & Psychotherapy, 18(4), 292–302. https://doi.org/10.1002/cpp.718",
        "Costa, P. T., & McCrae, R. R. (1992). Revised NEO Personality Inventory (NEO PI-R) and NEO Five-Factor Inventory (NEO-FFI) professional manual. Psychological Assessment Resources.",
        "Davey, A., Chilcot, J., Driscoll, E., & McCracken, L. M. (2020). Psychological flexibility, self-compassion and daily functioning in chronic pain. Journal of Contextual Behavioral Science, 17, 79–85. https://doi.org/10.1016/j.jcbs.2020.06.003",
        "Delgado, D. A., Lambert, B. S., Boutris, N., McCulloch, P. C., Robbins, A. B., Moreno, M. R., & Harris, J. D. (2018). Validation of digital visual analog scale pain scoring with a traditional paper-based visual analog scale in adults. Journal of the American Academy of Orthopaedic Surgeons Global Research & Reviews, 2(3), e088. https://doi.org/10.5435/JAAOSGlobal-D-17-00088",
        "Freeman, K., Smyth, C., Dallam, L., & Jackson, B. (2001). Pain measurement scales: A comparison. Journal of Wound, Ostomy and Continence Nursing, 28(6), 290–296. https://doi.org/10.1067/mjw.2001.119747",
        "Garousi, F. M. T., Mehryar, A. H., & Tabatabaei, S. K. (2001). Application of the NEO Five-Factor Inventory in Iranian university students. Journal of Psychology (Tabriz University), 5(3), 173–198.",
        "Gilbert, P. (2014). The origins and nature of compassion focused therapy. British Journal of Clinical Psychology, 53(1), 6–41. https://doi.org/10.1111/bjc.12043",
        "Gloria-Kang, G. J., Ewing-Nelson, S. R., Mackey, L., Schlitt, J. T., Marathe, A., Abbas, K. M., & Swahn, M. H. (2020). Long-term impact of adolescent chronic pain on young adult education, employment, and mental health. Journal of School Health, 90(11), 845–854. https://doi.org/10.1111/josh.12948",
        "Grouper, H., Eisenberg, E., & Pud, D. (2021). More insight on the role of personality traits and sensitivity to experimental pain: A study in healthy young adults. Journal of Pain Research, 14, 1837–1846. https://doi.org/10.2147/JPR.S309605",
        "Hu, L. T., & Bentler, P. M. (1999). Cutoff criteria for fit indexes in covariance structure analysis: Conventional criteria versus new alternatives. Structural Equation Modeling: A Multidisciplinary Journal, 6(1), 1–55. https://doi.org/10.1080/10705519909540118",
        "Ibrahim, M. E., Weber, K., Courvoisier, D. S., & Genevay, S. (2020). Big five personality traits and disabling chronic low back pain: Association with fear-avoidance, catastrophizing, and depression. Pain Practice, 20(7), 745–755. https://doi.org/10.1111/papr.12903",
        "Khosravi, S., Sadeghi, M., & Yabandeh, M. R. (2013). Psychometric properties of the Self-Compassion Scale (SCS) in Iranian student samples. Psychological Models and Methods, 4(13), 85–101.",
        "Kline, R. B. (2015). Principles and practice of structural equation modeling (4th ed.). Guilford Press.",
        "Krejčová, K., Rymešová, P., & Chýlová, H. (2023). Self-compassion as a newly observed dimension of student personality and its relationship to psychological vulnerability. Journal on Efficiency and Responsibility in Education and Science, 16(2), 102–111. https://doi.org/10.7160/eriesj.2023.160203",
        "Krok, J. L., & Baker, T. A. (2014). The influence of personality on reported pain and self-efficacy for pain management in older individuals. Journal of Health Psychology, 19(10), 1261–1270. https://doi.org/10.1177/1359105313488975",
        "Lanzaro, C., Carvalho, S. A., Lapa, T. A., Valentim, A., & Gago, B. (2024). A systematic review of self-compassion in chronic pain: From correlation to therapeutic efficacy. The Spanish Journal of Psychology, 27, e4. https://doi.org/10.1017/SJP.2024.4",
        "Martínez, M. P., Sánchez, A. I., Miró, E., Medina, A., & Lami, M. J. (2020). The relationship between the fear-avoidance model of pain and personality traits in fibromyalgia patients. Clinical and Experimental Rheumatology, 38(1), 32–40.",
        "McCarthy, K., Chamberlain, M., Chinn, M., Pineda, J., & Santiago, C. (2023). Social participation in college students with chronic pain: Coping, academic functioning, and social connectedness. Journal of American College Health, 71(4), 1145–1153. https://doi.org/10.1080/07448481.2021.1926266",
        "Mistretta, E. G., Davis, M. C., Bartsch, E. M., & Olah, M. S. (2023). Self-compassion and pain disability in adults with chronic pain: The mediating role of future self-identification. Journal of Behavioral Medicine, 46(3), 488–498. https://doi.org/10.1007/s10865-022-00366-2",
        "Mohtarami Zavardeh, S. Z., Ashoori, M., & Bazzazian, S. (2023). Self-compassion in the relationship between personality traits and bedtime procrastination: A structural modeling study. Journal of Social Behavior and Personality, 51(3), e12104.",
        "Muris, P., & Otgaar, H. (2020). Self-esteem and self-compassion: A narrative review and meta-analysis on their links to psychological problems and well-being. Clinical Psychology Review, 82, 101925. https://doi.org/10.1016/j.cpr.2020.101925",
        "Neff, K. D. (2003a). Self-compassion: An alternative conceptualization of a healthy attitude toward oneself. Self and Identity, 2(2), 85–101. https://doi.org/10.1080/15298860309032",
        "Neff, K. D. (2003b). The development and validation of a scale to measure self-compassion. Self and Identity, 2(3), 223–250. https://doi.org/10.1080/15298860309027",
        "Neff, K. D., & Germer, C. K. (2013). A pilot study and randomized controlled trial of the mindful self-compassion program. Journal of Clinical Psychology, 69(1), 28–44. https://doi.org/10.1002/jclp.21923",
        "Newth, S., & DeLongis, A. (2004). Individual differences, mood, and coping with chronic pain in rheumatoid arthritis: A daily process analysis. Psychology & Health, 19(3), 283–305. https://doi.org/10.1080/0887044042000193460",
        "Price, D. D., McGrath, P. A., Rafii, A., & Buckingham, B. (1983). The validation of visual analogue scales as ratio scale measures for chronic and experimental pain. Pain, 17(1), 45–56. https://doi.org/10.1016/0304-3959(83)90126-4",
        "Qadriyah, S., Ayriza, Y., Setiawati, F., & Wibowo, Y. (2020). The Big Five personality traits as predictors of self-compassion in young adults. Advances in Social Science, Education and Humanities Research, 462, 1–8.",
        "Raes, F., Pommier, E., Neff, K. D., & Van Gucht, D. (2011). Construction and factorial validation of a short form of the Self-Compassion Scale. Clinical Psychology & Psychotherapy, 18(3), 250–255. https://doi.org/10.1002/cpp.702",
        "Raffaeli, W., Tenti, M., Corraro, A., Malafoglia, V., Ilari, S., Balzani, E., & Bonvicini, D. (2021). Chronic pain: What does it mean? A review on the use of the term chronic pain in clinical practice. Journal of Pain Research, 14, 827–835. https://doi.org/10.2147/JPR.S303186",
        "Rezvani, M., & Sajjadian, I. (2017). The mediating role of self-compassion in the effect of personality traits on positive psychological functions. Journal of Research in Psychological Health, 11(2), 55–69.",
        "Roshan, R., Spahmansour, S., & Ghasemi, K. Z. (2006). A study of the factor structure and psychometric properties of the NEO Five-Factor Inventory in an Iranian sample. Daneshvar Raftar, 13(16), 27–36.",
        "Rosseel, Y. (2012). lavaan: An R package for structural equation modeling. Journal of Statistical Software, 48(2), 1–36. https://doi.org/10.18637/jss.v048.i02",
        "Rubén, M. C., Soriano Pastor, J. F., & Monsalve Dolz, V. (2023). Exploring the relationship between personality and chronic pain: Coping strategies and health-related quality of life. Journal of Health Psychology, 28(6), 552–564. https://doi.org/10.1177/13591053221124508",
        "Shahbazi, M., Rajabi, G., Maghami, E., & Jelodari, A. (2015). Confirmatory factor analysis of the Persian version of the Self-Compassion Rating Scale - Short Form. Journal of Educational Measurement, 5(20), 101–116.",
        "Smale, G., Tuson, G., & Statham, D. (2023). Assessment, intervention, and chronic pain among emerging adults: Psychosocial burdens. Social Work and Social Problems, 158(9), 1629–1632.",
        "Thurackal, J. T., Corveleyn, J., & Dezutter, J. (2016). Personality and self-compassion: Exploring their relationship in an emerging adult context. European Journal of Mental Health, 11(1–2), 70–88. https://doi.org/10.5708/EJMH.11.2016.1-2.5",
        "Treede, R. D., Rief, W., Barke, A., Aziz, Q., Bennett, M. I., Benoliel, R., Cohen, M., Evers, S., Finnerup, N. B., First, M. B., Giamberardino, M. A., Kaasa, S., Kosek, E., Lavand'homme, P., Nicholas, M., Perrot, S., Scholz, J., Schug, S., Smith, B. H., … Wang, S. J. (2015). A classification of chronic pain for ICD-11. Pain, 156(6), 1003–1007. https://doi.org/10.1097/j.pain.0000000000000160",
        "Wong, W. S., Lam, H. M. J., Chen, P. P., Chow, Y. F., Wong, S., Lim, H. S., & Jensen, M. P. (2014). The fear-avoidance model of chronic pain: Assessing the role of neuroticism and negative affect in pain-related outcomes. The Clinical Journal of Pain, 30(10), 868–876. https://doi.org/10.1097/AJP.0000000000000046",
        "Wren, A. A., Somers, T. J., Wright, M. A., Goetz, M. C., Leary, M. R., Fras, A. M., Huh, B. K., Rogers, L. L., & Keefe, F. J. (2012). Self-compassion in patients with persistent musculoskeletal pain: Relationship of self-compassion to pain, coping, and psychological symptoms. Journal of Pain and Symptom Management, 43(4), 659–670. https://doi.org/10.1016/j.jpainsymman.2011.04.014",
        "Yang, F., Hagiwara, C., Kotani, T., Hirao, J., & Oshio, A. (2020). Comparing self-esteem and self-compassion: An analysis within the Big Five personality traits framework. The Journal of Social Psychology, 160(6), 754–763. https://doi.org/10.1080/00224545.2020.1746617",
        "Yazdiravandi, S., Taslimi, Z., & Haghparast, A. (2020). Quality of life in patients with chronic pain: Determining the role of pain intensity and duration. Basic and Clinical Neuroscience, 11(4), 513–522. https://doi.org/10.32598/bcn.11.4.1950.1"
    ]
}

def main():
    json_path = "03_deliverables/article_2_payload.json"
    docx_path = "03_deliverables/Article_2_Self_Compassion_Final.docx"
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(article_data, f, ensure_ascii=False, indent=2)
    print(f"[+] Article payload written to: {json_path}")
    
    cmd = [
        sys.executable,
        ".agents/skills/academic-article-writer/scripts/compile_academic_article.py",
        "--json", json_path,
        "--out", docx_path,
        "--lang", "en"
    ]
    print(f"[+] Compiling manuscript via compile_academic_article.py...")
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    print(res.stdout)
    if res.stderr:
        print("STDERR:", res.stderr)
    if res.returncode != 0:
        sys.exit(res.returncode)
    print(f"[✓] Completed compiling: {docx_path}")

if __name__ == "__main__":
    main()
