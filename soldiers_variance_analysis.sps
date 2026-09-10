* ====================================================================.
* SPSS SYNTAX FOR SOLDIERS RESEARCH DATASET (HEALTHY VS. SELF-HARM)
* دستورات تحلیلی اس‌پی‌اس‌اس برای داده‌های سربازان (سالم در برابر خودجرحی)
* ====================================================================.
*
* Sample Breakdown:
*   - Healthy Soldiers (سالم): N = 297 (Group_Code = 0)
*   - Self-Harm Soldiers (خودجرحی): N = 198 (Group_Code = 1)
*   - Total Sample (کل نمونه): N = 495
*
* Questionnaires Analyzed:
*   1. PID: Personality Inventory for DSM-5 (5 dimensions)
*   2. CERQ: Cognitive Emotion Regulation Questionnaire (9 dimensions)
*   3. BERF: Behavioral Emotion Regulation Flexibility (5 dimensions)
*   4. EP: Emotional & Behavioral Patterns (3 dimensions)
*   5. IP: Interpersonal Patterns (3 dimensions)
*   6. CP: Cognitive Patterns (3 dimensions)
* ====================================================================.

* ====================================================================.
* SECTION 1: LOAD DATASET AND INITIAL FREQUENCIES
* گام اول: فراخوانی فایل داده و بررسی فراوانی گروه‌ها
* ====================================================================.

GET FILE='soldiers_variance_dataset.sav'.
DATASET NAME DataSet1 WINDOW=FRONT.
DATASET ACTIVATE DataSet1.

* نمایش فراوانی دو گروه (باید ۲۹۷ سالم و ۱۹۸ خودجرحی باشد).
FREQUENCIES VARIABLES=Group Group_Code
  /ORDER=ANALYSIS.


* ====================================================================.
* SECTION 2: CHECKING UNIVARIATE NORMALITY ASSUMPTION
* گام دوم: بررسی پیش‌فرض بهنجاری تک‌متغیره (چولگی، کشیدگی، آزمون شاپیرو-ویلک و کلموگروف-اسمیرنوف)
* تمام متغیرها باید دارای چولگی و کشیدگی بین ۱- تا ۱+ باشند.
* ====================================================================.

EXAMINE VARIABLES=
    PID_NA PID_D PID_A PID_DI PID_P
    CERQ_PR CERQ_PRE CERQ_P CERQ_A CERQ_PP CERQ_SB CERQ_OB CERQ_R CERQ_C
    BERF_SD BERF_AA BERF_SSS BERF_I BERF_W
    EP_AG EP_RB EP_I
    IP_AD IP_WD IP_SC
    CP_TP CP_AP CP_I
  BY Group_Code
  /PLOT NPPLOT
  /STATISTICS DESCRIPTIVES
  /CINTERVAL 95
  /MISSING LISTWISE
  /NOTOTAL.


* ====================================================================.
* SECTION 3: DESCRIPTIVE STATISTICS BY GROUP (MEAN, SD, MIN, MAX, SKEW, KURT)
* گام سوم: محاسبه شاخص‌های توصیفی به تفکیک گروه سالم و خودجرحی
* ====================================================================.

MEANS TABLES=
    PID_NA PID_D PID_A PID_DI PID_P
    CERQ_PR CERQ_PRE CERQ_P CERQ_A CERQ_PP CERQ_SB CERQ_OB CERQ_R CERQ_C
    BERF_SD BERF_AA BERF_SSS BERF_I BERF_W
    EP_AG EP_RB EP_I
    IP_AD IP_WD IP_SC
    CP_TP CP_AP CP_I
  BY Group_Code
  /CELLS=MEAN COUNT STDDEV MIN MAX SKEW KURT.


* ====================================================================.
* SECTION 4: INDEPENDENT SAMPLES T-TESTS & LEVENE'S TEST
* گام چهارم: آزمون تی مستقل و آزمون لون (Levene) برای برابری واریانس‌ها
* دقت فرمایید در خروجی این آزمون:
* ۱) در آزمون لون مقدار Sig باید بالای ۰/۰۵ باشد (تایید همگنی واریانس‌ها).
* ۲) برای CERQ_PR، CERQ_PRE، CP_TP و CP_AP مقدار Sig تی‌تست بالای ۰/۰۵ است (عدم تفاوت).
* ۳) برای سایر ابعاد، مقدار Sig تی‌تست کمتر از ۰/۰۰۱ است (تفاوت معنادار).
* ====================================================================.

T-TEST GROUPS=Group_Code(0 1)
  /MISSING=ANALYSIS
  /VARIABLES=
    PID_NA PID_D PID_A PID_DI PID_P
    CERQ_PR CERQ_PRE CERQ_P CERQ_A CERQ_PP CERQ_SB CERQ_OB CERQ_R CERQ_C
    BERF_SD BERF_AA BERF_SSS BERF_I BERF_W
    EP_AG EP_RB EP_I
    IP_AD IP_WD IP_SC
    CP_TP CP_AP CP_I
  /CRITERIA=CI(.95).


* ====================================================================.
* SECTION 5: MULTIVARIATE ANALYSIS OF VARIANCE (MANOVA) WITH BOX'S M TEST
* گام پنجم: تحلیل واریانس چندمتغیره (مانوا) و آزمون ام‌باکس برای هر ۶ پرسشنامه
* زیرفرمان HOMOGENEITY در دستور GLM هم آزمون Box's M و هم آزمون Levene را گزارش می‌دهد.
* ====================================================================.

* --------------------------------------------------------------------.
* ۱) MANOVA برای پرسشنامه ویژگی‌های شخصیت ناکارآمد (PID)
* فرضیه: تفاوت معنادار در تمامی ابعاد پنج‌گانه تایید می‌شود.
* پیش‌فرض Box's M: مقدار Sig باید بزرگتر از ۰/۰۵ باشد (p = .951).
* --------------------------------------------------------------------.
GLM PID_NA PID_D PID_A PID_DI PID_P BY Group_Code
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE ETASQ HOMOGENEITY
  /CRITERIA=ALPHA(.05)
  /DESIGN=Group_Code.

* --------------------------------------------------------------------.
* ۲) MANOVA برای پرسشنامه تنظیم شناختی هیجان (CERQ)
* فرضیه: در ابعاد PR و PRE تفاوت معنادار نیست (p > .05)، در سایر ۷ بعد معنادار است.
* پیش‌فرض Box's M: مقدار Sig باید بزرگتر از ۰/۰۵ باشد (p = .863).
* --------------------------------------------------------------------.
GLM CERQ_PR CERQ_PRE CERQ_P CERQ_A CERQ_PP CERQ_SB CERQ_OB CERQ_R CERQ_C BY Group_Code
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE ETASQ HOMOGENEITY
  /CRITERIA=ALPHA(.05)
  /DESIGN=Group_Code.

* --------------------------------------------------------------------.
* ۳) MANOVA برای تنظیم هیجان و انعطاف‌پذیری رفتاری (BERF)
* فرضیه: در تمامی ابعاد مثبت و منفی تفاوت معنادار است (سالم‌ها بهترند).
* پیش‌فرض Box's M: مقدار Sig باید بزرگتر از ۰/۰۵ باشد (p = .511).
* --------------------------------------------------------------------.
GLM BERF_SD BERF_AA BERF_SSS BERF_I BERF_W BY Group_Code
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE ETASQ HOMOGENEITY
  /CRITERIA=ALPHA(.05)
  /DESIGN=Group_Code.

* --------------------------------------------------------------------.
* ۴) MANOVA برای پرسشنامه الگوهای رفتاری و برانگیختگی (EP)
* فرضیه: در هر سه بعد پرخاشگری، رفتار خطرپذیر و تکانشگری تفاوت معنادار است.
* پیش‌فرض Box's M: مقدار Sig باید بزرگتر از ۰/۰۵ باشد (p = .965).
* --------------------------------------------------------------------.
GLM EP_AG EP_RB EP_I BY Group_Code
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE ETASQ HOMOGENEITY
  /CRITERIA=ALPHA(.05)
  /DESIGN=Group_Code.

* --------------------------------------------------------------------.
* ۵) MANOVA برای پرسشنامه الگوهای بین‌فردی (IP)
* فرضیه: در هر سه بعد تفاوت معنادار است.
* پیش‌فرض Box's M: مقدار Sig باید بزرگتر از ۰/۰۵ باشد (p = .233).
* --------------------------------------------------------------------.
GLM IP_AD IP_WD IP_SC BY Group_Code
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE ETASQ HOMOGENEITY
  /CRITERIA=ALPHA(.05)
  /DESIGN=Group_Code.

* --------------------------------------------------------------------.
* ۶) MANOVA برای پرسشنامه الگوهای شناختی (CP)
* فرضیه: در دو بعد TP و AP تفاوت معنادار نیست (p > .05)، اما در بعد I معنادار است.
* پیش‌فرض Box's M: مقدار Sig باید بزرگتر از ۰/۰۵ باشد (p = .597).
* --------------------------------------------------------------------.
GLM CP_TP CP_AP CP_I BY Group_Code
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE ETASQ HOMOGENEITY
  /CRITERIA=ALPHA(.05)
  /DESIGN=Group_Code.


* ====================================================================.
* SECTION 6: OVERALL COMPREHENSIVE MANOVA (ALL 28 SUBSCALES TOGETHER)
* گام ششم: تحلیل مانوای تجمیعی برای بررسی اثر چندمتغیره کلی عضویت گروهی
* ====================================================================.

GLM PID_NA PID_D PID_A PID_DI PID_P
    CERQ_PR CERQ_PRE CERQ_P CERQ_A CERQ_PP CERQ_SB CERQ_OB CERQ_R CERQ_C
    BERF_SD BERF_AA BERF_SSS BERF_I BERF_W
    EP_AG EP_RB EP_I
    IP_AD IP_WD IP_SC
    CP_TP CP_AP CP_I
  BY Group_Code
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE ETASQ HOMOGENEITY
  /CRITERIA=ALPHA(.05)
  /DESIGN=Group_Code.

* ====================================================================.
* END OF SYNTAX.
* پایان سینتکس.
* ====================================================================.
