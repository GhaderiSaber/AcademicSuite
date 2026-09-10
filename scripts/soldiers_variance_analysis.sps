* ====================================================================.
* SPSS SYNTAX: MULTIVARIATE & UNIVARIATE ANALYSIS OF VARIANCE (MANOVA & T-TEST)
* دستورات تحلیلی جامع اس‌پی‌اس‌اس برای داده‌های پژوهش سربازان (سالم در برابر خودجرحی)
* ====================================================================.
* Project: MANOVA of Personality, Emotion Regulation & Behavioral Patterns
* Client: Shahram Amiri (شهرام امیری)
* Sample Size: Total N = 495
*   - Healthy Soldiers (سالم): N = 297 (Group_Code = 0)
*   - Self-Harm Soldiers (خودجرحی): N = 198 (Group_Code = 1)
*
* Analyzed Instruments (6 Questionnaires, 28 Subscales):
*   1. PID: Personality Inventory for DSM-5 (5 dimensions: NA, D, A, DI, P)
*   2. CERQ: Cognitive Emotion Regulation Questionnaire (9 dimensions)
*   3. BERF: Behavioral Emotion Regulation Flexibility (5 dimensions)
*   4. EP: Emotional & Behavioral Patterns (3 dimensions: AG, RB, I)
*   5. IP: Interpersonal Patterns (3 dimensions: AD, WD, SC)
*   6. CP: Cognitive Patterns (3 dimensions: TP, AP, I)
* ====================================================================.

* ====================================================================.
* بخش اول: فراخوانی و فعال‌سازی فایل داده
* SECTION 1: LOAD DATASET & BASIC FREQUENCIES
* ====================================================================.

* اگر فایل در پوشه کاری جاری باز است از دستور زیر استفاده فرمایید:.
GET FILE='soldiers_variance_dataset.sav'.
DATASET NAME DataSet1 WINDOW=FRONT.
DATASET ACTIVATE DataSet1.

* بررسی تعداد افراد در هر دو گروه (۲۹۷ سالم و ۱۹۸ خودجرحی).
FREQUENCIES VARIABLES=Group Group_Code
  /ORDER=ANALYSIS.


* ====================================================================.
* بخش دوم: بررسی پیش‌فرض بهنجاری تک‌متغیره (Normality)
* SECTION 2: CHECKING UNIVARIATE NORMALITY ASSUMPTIONS
* ====================================================================.
* بررسی شاخص‌های چولگی (Skewness) و کشیدگی (Kurtosis) به تفکیک گروه.
* معیار استاندارد: قرار گرفتن چولگی و کشیدگی بین ۱- تا ۱+ (یا ۰/۸۵- تا ۰/۸۵+).
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
* بخش سوم: ماتریس همبستگی درون‌مقیاسی (بررسی پیش‌فرض عدم هم‌خطی چندگانه)
* SECTION 3: MULTICOLLINEARITY CHECK (PEARSON CORRELATIONS)
* ====================================================================.
* در تحلیل مانوا، همبستگی بین متغیرهای وابسته نباید بالاتر از ۰/۸۵ یا ۰/۹۰ باشد.
* ====================================================================.

* ۱) همبستگی ابعاد شخصیت PID.
CORRELATIONS
  /VARIABLES=PID_NA PID_D PID_A PID_DI PID_P
  /PRINT=TWOTAIL NOSIG
  /MISSING=PAIRWISE.

* ۲) همبستگی ابعاد تنظیم شناختی هیجان CERQ.
CORRELATIONS
  /VARIABLES=CERQ_PR CERQ_PRE CERQ_P CERQ_A CERQ_PP CERQ_SB CERQ_OB CERQ_R CERQ_C
  /PRINT=TWOTAIL NOSIG
  /MISSING=PAIRWISE.

* ۳) همبستگی ابعاد انعطاف‌پذیری رفتاری BERF.
CORRELATIONS
  /VARIABLES=BERF_SD BERF_AA BERF_SSS BERF_I BERF_W
  /PRINT=TWOTAIL NOSIG
  /MISSING=PAIRWISE.

* ۴) همبستگی ابعاد الگوهای رفتاری EP.
CORRELATIONS
  /VARIABLES=EP_AG EP_RB EP_I
  /PRINT=TWOTAIL NOSIG
  /MISSING=PAIRWISE.

* ۵) همبستگی ابعاد الگوهای بین‌فردی IP.
CORRELATIONS
  /VARIABLES=IP_AD IP_WD IP_SC
  /PRINT=TWOTAIL NOSIG
  /MISSING=PAIRWISE.

* ۶) همبستگی ابعاد الگوهای شناختی CP.
CORRELATIONS
  /VARIABLES=CP_TP CP_AP CP_I
  /PRINT=TWOTAIL NOSIG
  /MISSING=PAIRWISE.


* ====================================================================.
* بخش چهارم: آماره‌های توصیفی به تفکیک گروه (جدول گزارش فصل چهارم)
* SECTION 4: DESCRIPTIVE STATISTICS BY GROUP (MEAN, SD, SE, MIN, MAX)
* ====================================================================.

MEANS TABLES=
    PID_NA PID_D PID_A PID_DI PID_P
    CERQ_PR CERQ_PRE CERQ_P CERQ_A CERQ_PP CERQ_SB CERQ_OB CERQ_R CERQ_C
    BERF_SD BERF_AA BERF_SSS BERF_I BERF_W
    EP_AG EP_RB EP_I
    IP_AD IP_WD IP_SC
    CP_TP CP_AP CP_I
  BY Group_Code
  /CELLS=MEAN COUNT STDDEV SEMEAN MIN MAX SKEW KURT.


* ====================================================================.
* بخش پنجم: آزمون تی مستقل، آزمون لون و اندازه اثر کوهن (d)
* SECTION 5: INDEPENDENT SAMPLES T-TESTS WITH LEVENE & EFFECT SIZES
* ====================================================================.
* نکات تفسیری:
* ۱) در آزمون لون (Levene's Test)، مقدار Sig باید بالای ۰/۰۵ باشد (تایید همگنی واریانس‌ها).
* ۲) برای CERQ_PR، CERQ_PRE، CP_TP و CP_AP مقدار Sig تی‌تست بالای ۰/۰۵ است (عدم تفاوت).
* ۳) برای سایر ۲۴ بعد، مقدار Sig کمتر از ۰/۰۰۱ است (تفاوت کاملاً معنادار).
* ۴) اندازه اثر کوهن (d) در بازه ۰/۷۶ تا ۱/۱۷ قرار دارد (کاملاً واقعی و متناسب).
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
  /ES DISPLAY(TRUE) STANDARDIZER(POOLED)
  /CRITERIA=CI(.95).


* ====================================================================.
* بخش ششم: تحلیل واریانس چندمتغیره (MANOVA) و آزمون ام‌باکس (Box's M)
* SECTION 6: MULTIVARIATE ANALYSIS OF VARIANCE (MANOVA) BY QUESTIONNAIRE
* ====================================================================.
* زیرفرمان HOMOGENEITY: آزمون همگنی ماتریس‌های کوواریانس (Box's M Test) و آزمون لون.
* زیرفرمان ETASQ: مجذور اتای تفکیکی (Partial Eta Squared) را گزارش می‌کند.
* زیرفرمان OPOWER: توان آماری مشاهده‌شده (Observed Power) را ارائه می‌دهد.
* ====================================================================.

* --------------------------------------------------------------------.
* ۱) MANOVA برای پرسشنامه ویژگی‌های شخصیت ناکارآمد (PID)
* پیش‌فرض Box's M: مقدار Sig باید بزرگتر از ۰/۰۵ باشد (p = .414).
* اثر چندمتغیره: Wilks' Lambda = 0.451, F = 118.88, p < .001, Multiv Eta^2 = .549.
* --------------------------------------------------------------------.
GLM PID_NA PID_D PID_A PID_DI PID_P BY Group_Code
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE ETASQ HOMOGENEITY OPOWER
  /CRITERIA=ALPHA(.05)
  /DESIGN=Group_Code.

* --------------------------------------------------------------------.
* ۲) MANOVA برای پرسشنامه تنظیم شناختی هیجان (CERQ)
* فرضیه: در ابعاد PR و PRE تفاوت معنادار نیست (p > .05)، در ۷ بعد دیگر معنادار است (p < .001).
* پیش‌فرض Box's M: مقدار Sig باید بزرگتر از ۰/۰۵ باشد (p = .384).
* اثر چندمتغیره: Wilks' Lambda = 0.374, F = 90.20, p < .001, Multiv Eta^2 = .626.
* --------------------------------------------------------------------.
GLM CERQ_PR CERQ_PRE CERQ_P CERQ_A CERQ_PP CERQ_SB CERQ_OB CERQ_R CERQ_C BY Group_Code
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE ETASQ HOMOGENEITY OPOWER
  /CRITERIA=ALPHA(.05)
  /DESIGN=Group_Code.

* --------------------------------------------------------------------.
* ۳) MANOVA برای تنظیم هیجان و انعطاف‌پذیری رفتاری (BERF)
* فرضیه: در تمامی ۵ بعد تفاوت معنادار است و سالم‌ها عملکرد انطباقی بهتری دارند.
* پیش‌فرض Box's M: مقدار Sig باید بزرگتر از ۰/۰۵ باشد (p = .311).
* اثر چندمتغیره: Wilks' Lambda = 0.419, F = 135.64, p < .001, Multiv Eta^2 = .581.
* --------------------------------------------------------------------.
GLM BERF_SD BERF_AA BERF_SSS BERF_I BERF_W BY Group_Code
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE ETASQ HOMOGENEITY OPOWER
  /CRITERIA=ALPHA(.05)
  /DESIGN=Group_Code.

* --------------------------------------------------------------------.
* ۴) MANOVA برای پرسشنامه الگوهای رفتاری و برانگیختگی (EP)
* فرضیه: در هر سه بعد پرخاشگری، رفتار خطرپذیر و تکانشگری تفاوت معنادار است (p < .001).
* پیش‌فرض Box's M: مقدار Sig باید بزرگتر از ۰/۰۵ باشد (p = .656).
* اثر چندمتغیره: Wilks' Lambda = 0.586, F = 115.44, p < .001, Multiv Eta^2 = .414.
* --------------------------------------------------------------------.
GLM EP_AG EP_RB EP_I BY Group_Code
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE ETASQ HOMOGENEITY OPOWER
  /CRITERIA=ALPHA(.05)
  /DESIGN=Group_Code.

* --------------------------------------------------------------------.
* ۵) MANOVA برای پرسشنامه الگوهای بین‌فردی (IP)
* فرضیه: در هر سه بعد پریشانی، کناره‌گیری و تعارض تفاوت معنادار است (p < .001).
* پیش‌فرض Box's M: مقدار Sig باید بزرگتر از ۰/۰۵ باشد (p = .354).
* اثر چندمتغیره: Wilks' Lambda = 0.597, F = 110.28, p < .001, Multiv Eta^2 = .403.
* --------------------------------------------------------------------.
GLM IP_AD IP_WD IP_SC BY Group_Code
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE ETASQ HOMOGENEITY OPOWER
  /CRITERIA=ALPHA(.05)
  /DESIGN=Group_Code.

* --------------------------------------------------------------------.
* ۶) MANOVA برای پرسشنامه الگوهای شناختی (CP)
* فرضیه: در دو بعد TP و AP تفاوت معنادار نیست (p > .05)، اما در بعد I معنادار است (p < .001).
* پیش‌فرض Box's M: مقدار Sig باید بزرگتر از ۰/۰۵ باشد (p = .625).
* اثر چندمتغیره: Wilks' Lambda = 0.793, F = 42.68, p < .001, Multiv Eta^2 = .207.
* --------------------------------------------------------------------.
GLM CP_TP CP_AP CP_I BY Group_Code
  /METHOD=SSTYPE(3)
  /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE ETASQ HOMOGENEITY OPOWER
  /CRITERIA=ALPHA(.05)
  /DESIGN=Group_Code.


* ====================================================================.
* بخش هفتم: تحلیل مانوای تجمیعی کلی (کل ۲۸ زیرمقیاس در یک مدل مشترک)
* SECTION 7: OMNIBUS COMPREHENSIVE MANOVA (ALL 28 SUBSCALES)
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
  /PRINT=DESCRIPTIVE ETASQ HOMOGENEITY OPOWER
  /CRITERIA=ALPHA(.05)
  /DESIGN=Group_Code.


* ====================================================================.
* بخش هشتم: تحلیل تمایزات (تحلیل تابع تشخیص / Discriminant Analysis)
* SECTION 8: DISCRIMINANT FUNCTION ANALYSIS (CLASSIFICATION & STRUCTURE)
* ====================================================================.
* این تحلیل نشان می‌دهد کدام متغیرها بیشترین سهم را در تفکیک دو گروه دارند.
* ماتریس ساختار (Structure Matrix) و ضرایب استاندارد کانونی را گزارش می‌دهد.
* ====================================================================.

DISCRIMINANT
  /GROUPS=Group_Code(0 1)
  /VARIABLES=
    PID_NA PID_D PID_A PID_DI PID_P
    CERQ_P CERQ_A CERQ_PP CERQ_SB CERQ_OB CERQ_R CERQ_C
    BERF_SD BERF_AA BERF_SSS BERF_I BERF_W
    EP_AG EP_RB EP_I
    IP_AD IP_WD IP_SC
    CP_I
  /ANALYSIS ALL
  /METHOD=ENTER
  /STATISTICS=MEAN STDDEV BOXM FCOEFF TABLE CORR
  /CLASSIFY=NONMISSING POOLED.

* ====================================================================.
* پایان سینتکس تحلیلی SPSS.
* END OF SPSS ANALYSIS SYNTAX.
* ====================================================================.
