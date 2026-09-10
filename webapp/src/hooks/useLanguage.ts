import { useState, useEffect, useCallback } from 'react';
import { Language } from '../types';

export const DICTIONARY = {
  en: {
    app_title: 'Saber Academic Suite',
    app_subtitle: 'Thesis Consultancy & Project Operations Hub',
    tab_kanban: 'Project Pipeline',
    tab_calculator: 'Pricing Calculator',
    tab_scales: 'Scales Registry',
    tab_consultant: 'Consultant Profile',
    txt_drive_status: 'Google Drive: Connected (My Work)',
    badge_total_projects: '{count} Projects Active',
    search_projects: 'Search client name, topic, or path...',
    filter_all: 'All',
    status_inquiry: 'Inquiry',
    status_pending: 'Pending Quote',
    status_in_progress: 'In Progress',
    status_finished: 'Finished',
    col_inquiry: 'Inquiry & Intake',
    col_pending: 'Pending Approval',
    col_in_progress: 'Active Analysis & Writing',
    col_finished: 'Defense-Ready & Archived',
    calc_params_title: 'Research Study Parameters',
    lbl_degree: 'Academic Degree Level',
    opt_master: "Master's (M.A. / M.Sc.)",
    opt_phd: 'Doctorate (Ph.D.)',
    lbl_design: 'Methodology & Research Design',
    design_ancova: 'Quasi-Experimental (ANCOVA / Repeated Measures)',
    design_sem: 'Structural Equation Modeling (SEM / CFA - AMOS/PLS)',
    design_regression: 'Correlation & Multiple Hierarchical Regression',
    design_scale_val: 'Psychometric Validation (EFA / CFA / IRT)',
    design_qualitative: 'Qualitative Thematic Analysis (MAXQDA)',
    lbl_sample_size: 'Sample Size (N)',
    lbl_scales_count: 'Psychometric Questionnaires Count',
    lbl_urgent: 'Express Priority Delivery (48h)',
    desc_urgent: 'Fast-track pipeline with 1.4x urgency coefficient',
    lbl_select_services: 'Select Required Deliverable Modules:',
    svc_ch3_name: 'Chapter 3: Methodology & G*Power',
    svc_ch3_meta: 'Research design, instruments, sample power calculation',
    svc_sim_name: 'SimDat Psychometric Data Simulation',
    svc_sim_meta: 'Monte Carlo discrete Likert simulation with real factor covariance',
    svc_ch4_name: 'Chapter 4: Statistical Analysis & APA 7 Tables',
    svc_ch4_meta: 'Normality, inferential hypothesis testing, raw output files',
    svc_ch5_name: 'Chapter 5: Discussion & Theoretical Mechanisms',
    svc_ch5_meta: 'Findings integration, Iranian/foreign literature, limitations',
    svc_slides_name: 'Viva Voce Defense Slides Deck',
    svc_slides_meta: 'Widescreen 16:9 presentation with speaker script notes',
    svc_audit_name: 'Comprehensive Thesis Integrity Audit',
    svc_audit_meta: 'Hypothesis alignment, df verification, bidirectional citation check',
    quote_summary_title: 'Official Quotation & Schedule',
    lbl_total_price: 'Total Investment',
    lbl_total_days: 'Estimated Turnaround',
    parallel_timeline_note: 'With parallel analytical pipelines',
    summary_breakdown: 'Selected Services Breakdown:',
    btn_copy_quote: 'Copy Telegram Card',
    btn_send_telegram: 'Direct Inquiry to Saber',
    search_scales: 'Search across 4,880 instruments (e.g., resilience, Beck, schema, DASS)...',
    cat_all: 'All Instruments',
    profile_expertise_title: 'Core Competencies & Services',
    profile_contact_title: 'Direct Communication & Admin Desk',
    select_scale_btn: 'Select for Calculator',
    discount_badge_text: '15% Full Package Discount Applied',
    no_discount_text: 'Standard Pricing (Select 4+ for 15% off)',
    days_suffix: 'Business Days',
    price_unit: 'Tomans',
    copied_toast: 'Quotation card copied to clipboard!',
    scale_selected_toast: 'Scale selected for project calculation!',
    items_unit: 'Items',
    subscales_label: 'Subscales & Factors:',
    no_scales_found: 'No questionnaires matched your search.',
  },
  fa: {
    app_title: 'سامانه مشاوره آماری و رساله صابر قادری',
    app_subtitle: 'مرکز مدیریت پروژه‌ها، برآورد آنلاین هزینه و بانک پرسشنامه‌ها',
    tab_kanban: 'میز پروژه‌ها',
    tab_calculator: 'محاسبه‌گر پیش‌فاکتور',
    tab_scales: 'بانک پرسشنامه‌ها',
    tab_consultant: 'پروفایل مشاور',
    txt_drive_status: 'گوگل درایو: متصل (پروژه‌های فعال)',
    badge_total_projects: '{count} پروژه فعال',
    search_projects: 'جستجوی نام دانشجو، موضوع یا مسیر درایو...',
    filter_all: 'همه',
    status_inquiry: 'استعلام اولیه',
    status_pending: 'در انتظار تایید',
    status_in_progress: 'در حال انجام',
    status_finished: 'تکمیل‌شده و دفاع',
    col_inquiry: 'استعلام و بررسی اولیه',
    col_pending: 'پیش‌فاکتور و تایید نهایی',
    col_in_progress: 'تحلیل آماری و نگارش فعال',
    col_finished: 'آماده دفاع و آرشیو',
    calc_params_title: 'مشخصات طرح پژوهش و متغیرها',
    lbl_degree: 'مقطع تحصیلی',
    opt_master: 'کارشناسی ارشد (M.A. / M.Sc.)',
    opt_phd: 'دکتری تخصصی (Ph.D.)',
    lbl_design: 'روش‌شناسی و طرح پژوهش',
    design_ancova: 'شبه‌آزمایشی (تحلیل کوواریانس ANCOVA / اندازه‌گیری مکرر)',
    design_sem: 'مدل‌یابی معادلات ساختاری (SEM / CFA - ایموس/اسمارت‌پلی‌اس)',
    design_regression: 'همبستگی و رگرسیون چندگانه سلسله‌مراتبی',
    design_scale_val: 'روان‌سنجی و اعتبارسنجی مقیاس (EFA / CFA / IRT)',
    design_qualitative: 'پژوهش کیفی و تحلیل مضمون (مکس‌کیودا MAXQDA)',
    lbl_sample_size: 'حجم نمونه (N)',
    lbl_scales_count: 'تعداد پرسشنامه‌ها و مقیاس‌ها',
    lbl_urgent: 'تحویل فوری و ویژه (۴۸ ساعته)',
    desc_urgent: 'اولویت‌دهی بالا در خط کاری با ضریب فوریت ۱/۴',
    lbl_select_services: 'فصل‌ها و خدمات مورد نیاز را انتخاب کنید:',
    svc_ch3_name: 'فصل سوم: روش‌شناسی پژوهش و G*Power',
    svc_ch3_meta: 'طرح پژوهش، ابزارها، روایی/پایایی و محاسبه حجم نمونه',
    svc_sim_name: 'شبیه‌سازی داده‌های روان‌سنجی (SimDat)',
    svc_sim_meta: 'شبیه‌سازی مونت‌کارلو گسسته لیکرت با ماتریس کوواریانس دقیق',
    svc_ch4_name: 'فصل چهارم: تحلیل آماری و جداول APA 7',
    svc_ch4_meta: 'بررسی مفروضه‌ها، آزمون فرضیات، فایل‌های خروجی نرم‌افزاری',
    svc_ch5_name: 'فصل پنجم: بحث، تبیین نظری و نتیجه‌گیری',
    svc_ch5_meta: 'تبیین سازوکارهای روان‌شناختی، پیشینه ایرانی و خارجی، محدودیت‌ها',
    svc_slides_name: 'اسلایدهای حرفه‌ای جلسه دفاع',
    svc_slides_meta: 'پاورپوینت ۱۶:۹ با متن سناریو و گفتار دانشجو برای هر اسلاید',
    svc_audit_name: 'ممیزی جامع و کنترل کیفیت رساله',
    svc_audit_meta: 'هم‌ترازی فرضیه-یافته، کنترل درجات آزادی و تطبیق دوسویه رفرنس‌ها',
    quote_summary_title: 'پیش‌فاکتور رسمی و جدول زمان‌بندی',
    lbl_total_price: 'سرمایه‌گذاری کل',
    lbl_total_days: 'زمان‌بندی تحویل',
    parallel_timeline_note: 'با خطوط کاری موازی و مستقل',
    summary_breakdown: 'ریز خدمات انتخاب شده:',
    btn_copy_quote: 'کپی پیش‌فاکتور برای تلگرام',
    btn_send_telegram: 'ارسال مستقیم و مشاوره به صابر',
    search_scales: 'جستجو در ۴,۸۸۰ پرسشنامه (مانند تاب‌آوری، بک، طرحواره، اضطراب)...',
    cat_all: 'همه پرسشنامه‌ها',
    profile_expertise_title: 'تخصص‌ها و حوزه‌های مشاوره',
    profile_contact_title: 'راه‌های ارتباطی مستقیم',
    select_scale_btn: 'انتخاب برای محاسبه‌گر',
    discount_badge_text: '۱۵٪ تخفیف پکیج جامع رساله اعمال شد',
    no_discount_text: 'تعرفه استاندارد (با انتخاب ۴ خدمت مشمول ۱۵٪ تخفیف شوید)',
    days_suffix: 'روز کاری',
    price_unit: 'تومان',
    copied_toast: 'پیش‌فاکتور با موفقیت در کلیپ‌بورد کپی شد!',
    scale_selected_toast: 'پرسشنامه برای محاسبه پژوهش انتخاب شد!',
    items_unit: 'گویه',
    subscales_label: 'خرده‌مقیاس‌ها و عوامل:',
    no_scales_found: 'هیچ پرسشنامه‌ای با این مشخصات یافت نشد.',
  },
};

export type DictKey = keyof typeof DICTIONARY.en;

export function useLanguage() {
  const [lang, setLang] = useState<Language>(() => {
    return (localStorage.getItem('academic_suite_lang') as Language) || 'en';
  });

  useEffect(() => {
    localStorage.setItem('academic_suite_lang', lang);
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'fa' ? 'rtl' : 'ltr';
  }, [lang]);

  const toggleLanguage = useCallback(() => {
    setLang((prev) => (prev === 'en' ? 'fa' : 'en'));
  }, []);

  const t = useCallback(
    (key: DictKey, params?: Record<string, string | number>): string => {
      let str = DICTIONARY[lang][key] || DICTIONARY.en[key] || (key as string);
      if (params) {
        Object.entries(params).forEach(([k, v]) => {
          str = str.replace(new RegExp(`\\{${k}\\}`, 'g'), String(v));
        });
      }
      return str;
    },
    [lang]
  );

  const formatNumber = useCallback(
    (num: number): string => {
      return num.toLocaleString(lang === 'fa' ? 'fa-IR' : 'en-US');
    },
    [lang]
  );

  return { lang, setLang, toggleLanguage, t, formatNumber };
}
