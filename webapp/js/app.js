/**
 * Saber Academic Suite — Telegram Mini App & Interactive Web Dashboard
 * Fully integrated with Telegram WebApp SDK, bilingual (EN/FA) engine,
 * live pricing calculator, and Google Drive Kanban project pipeline.
 */

(function () {
  'use strict';

  // --- Telegram WebApp SDK Integration ---
  const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
  if (tg) {
    tg.ready();
    try {
      tg.expand();
    } catch (e) {
      console.warn('Could not expand WebApp:', e);
    }
  }

  function triggerHaptic(type = 'light') {
    if (tg && tg.HapticFeedback) {
      if (type === 'light' || type === 'medium' || type === 'heavy') {
        tg.HapticFeedback.impactOccurred(type);
      } else if (type === 'success' || type === 'error' || type === 'warning') {
        tg.HapticFeedback.notificationOccurred(type);
      }
    }
  }

  // --- State & i18n Dictionaries ---
  const state = {
    currentLang: localStorage.getItem('academic_suite_lang') || 'en',
    currentTab: 'kanban',
    kanbanFilter: 'all',
    kanbanSearchQuery: '',
    scaleCategory: 'all',
    scaleSearchQuery: '',
    projects: window.ACADEMIC_PROJECTS || [],
    scales: window.ACADEMIC_SCALES || []
  };

  const i18n = {
    en: {
      app_title: 'Saber Academic Suite',
      app_subtitle: 'Thesis Consultancy & Project Operations Hub',
      tab_kanban: 'Project Pipeline',
      tab_calculator: 'Pricing Calculator',
      tab_scales: 'Scales Registry',
      tab_consultant: 'Consultant Profile',
      txt_drive_status: 'Google Drive: <b>Connected (My Work)</b>',
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
      opt_master: "Master's (M.A. / M.Sc.) — کارشناسی ارشد",
      opt_phd: 'Doctorate (Ph.D.) — دکتری تخصصی',
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
      scale_selected_toast: 'Scale selected for project calculation!'
    },
    fa: {
      app_title: 'سامانه مشاوره آماری و رساله صابر قادری',
      app_subtitle: 'مرکز مدیریت پروژه‌ها، برآورد آنلاین هزینه و بانک پرسشنامه‌ها',
      tab_kanban: 'میز پروژه‌ها',
      tab_calculator: 'محاسبه‌گر پیش‌فاکتور',
      tab_scales: 'بانک پرسشنامه‌ها',
      tab_consultant: 'پروفایل مشاور',
      txt_drive_status: 'گوگل درایو: <b>متصل (پروژه‌های فعال)</b>',
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
      scale_selected_toast: 'پرسشنامه برای محاسبه پژوهش انتخاب شد!'
    }
  };

  // --- UI Utilities ---
  function showToast(message, duration = 3000) {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toast-message');
    if (!toast || !toastMsg) return;
    toastMsg.textContent = message;
    toast.classList.remove('hidden');
    toast.classList.add('visible');
    setTimeout(() => {
      toast.classList.remove('visible');
      toast.classList.add('hidden');
    }, duration);
  }

  function formatNumber(num) {
    return Number(num).toLocaleString(state.currentLang === 'fa' ? 'fa-IR' : 'en-US');
  }

  // --- Language Switching ---
  function applyLanguage(lang) {
    state.currentLang = lang;
    localStorage.setItem('academic_suite_lang', lang);

    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'fa' ? 'rtl' : 'ltr';

    const langToggleBtn = document.getElementById('btn-lang-toggle');
    if (langToggleBtn) {
      if (lang === 'fa') {
        langToggleBtn.innerHTML = '<span class="lang-flag">🇬🇧</span><span class="lang-text">English</span>';
      } else {
        langToggleBtn.innerHTML = '<span class="lang-flag">🇮🇷</span><span class="lang-text">فارسی</span>';
      }
    }

    // Apply translations
    const dict = i18n[lang];
    document.querySelectorAll('[data-i18n]').forEach((el) => {
      const key = el.getAttribute('data-i18n');
      if (dict[key]) {
        el.textContent = dict[key];
      }
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (dict[key]) {
        el.setAttribute('placeholder', dict[key]);
      }
    });

    // Update dynamic texts
    const titleEl = document.getElementById('app-title');
    if (titleEl) titleEl.textContent = dict.app_title;
    const subTitleEl = document.getElementById('app-subtitle');
    if (subTitleEl) subTitleEl.textContent = dict.app_subtitle;
    const driveStatusEl = document.getElementById('txt-drive-status');
    if (driveStatusEl) driveStatusEl.innerHTML = dict.txt_drive_status;

    updateProjectBadge();
    renderKanban();
    updatePricing();
    renderScales();
  }

  function updateProjectBadge() {
    const badge = document.getElementById('badge-total-projects');
    if (!badge) return;
    const count = state.projects.length;
    const template = i18n[state.currentLang].badge_total_projects;
    badge.textContent = template.replace('{count}', formatNumber(count));
  }

  // --- Tab Navigation ---
  function initTabs() {
    const tabButtons = document.querySelectorAll('.nav-tab');
    tabButtons.forEach((btn) => {
      btn.addEventListener('click', () => {
        const tabId = btn.getAttribute('data-tab');
        if (!tabId || tabId === state.currentTab) return;

        triggerHaptic('light');
        state.currentTab = tabId;

        tabButtons.forEach((b) => {
          const isActive = b.getAttribute('data-tab') === tabId;
          b.classList.toggle('active', isActive);
          b.setAttribute('aria-selected', isActive ? 'true' : 'false');
        });

        document.querySelectorAll('.tab-pane').forEach((pane) => {
          pane.classList.toggle('active', pane.id === `tab-${tabId}`);
        });

        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    });
  }

  // --- Kanban Board Implementation ---
  function renderKanban() {
    const containers = {
      inquiry: document.getElementById('cards-inquiry'),
      pending: document.getElementById('cards-pending'),
      in_progress: document.getElementById('cards-in_progress'),
      finished: document.getElementById('cards-finished')
    };

    const counters = {
      inquiry: document.getElementById('count-inquiry'),
      pending: document.getElementById('count-pending'),
      in_progress: document.getElementById('count-in_progress'),
      finished: document.getElementById('count-finished')
    };

    if (!containers.inquiry) return;

    // Reset containers
    Object.values(containers).forEach((el) => {
      if (el) el.innerHTML = '';
    });

    const counts = { inquiry: 0, pending: 0, in_progress: 0, finished: 0 };
    const query = state.kanbanSearchQuery.trim().toLowerCase();

    state.projects.forEach((proj) => {
      // Status filter
      if (state.kanbanFilter !== 'all' && proj.status !== state.kanbanFilter) {
        return;
      }

      // Search filter
      if (query) {
        const matchName = (proj.client_name || '').toLowerCase().includes(query);
        const matchTopic = (proj.topic || '').toLowerCase().includes(query);
        const matchPath = (proj.folder_path || '').toLowerCase().includes(query);
        const matchId = (proj.id || '').toLowerCase().includes(query);
        if (!matchName && !matchTopic && !matchPath && !matchId) {
          return;
        }
      }

      const status = containers[proj.status] ? proj.status : 'inquiry';
      counts[status]++;

      const card = createProjectCard(proj);
      if (containers[status]) {
        containers[status].appendChild(card);
      }
    });

    // Update column counters
    Object.keys(counters).forEach((st) => {
      if (counters[st]) {
        counters[st].textContent = formatNumber(counts[st]);
      }
    });

    // Update filter chip "All" label
    const allChip = document.querySelector('.filter-chips .chip[data-filter="all"]');
    if (allChip) {
      allChip.textContent = `${i18n[state.currentLang].filter_all} (${formatNumber(state.projects.length)})`;
    }
  }

  function createProjectCard(proj) {
    const card = document.createElement('div');
    card.className = `kanban-card status-${proj.status}`;

    // Clean drive path: only show relative part like "My Work/..."
    const cleanPath = proj.folder_path ? proj.folder_path.replace(/^\/.*?Google Drive\//i, '') : 'My Work';

    // Telegram client link if applicable
    let clientMarkup = `<span class="card-client-name">${escapeHtml(proj.client_name)}</span>`;
    if (proj.client_name && proj.client_name.startsWith('Client_')) {
      const tgId = proj.client_name.replace('Client_', '');
      clientMarkup = `<a href="tg://user?id=${tgId}" class="card-client-name" style="color:#60a5fa; text-decoration:none;" title="Message Client in Telegram">👤 ${escapeHtml(proj.client_name)}</a>`;
    }

    card.innerHTML = `
      <div class="card-top">
        ${clientMarkup}
        <span class="card-id">${escapeHtml(proj.id)}</span>
      </div>
      <div class="card-topic" title="${escapeHtml(proj.topic || '')}">${escapeHtml(proj.topic || 'Academic Research Project')}</div>
      <div class="card-tags">
        <span class="card-tag highlight">${escapeHtml(proj.degree || 'Master')}</span>
        <span class="card-tag">${escapeHtml(proj.design || 'Empirical')}</span>
        <span class="card-tag">N=${formatNumber(proj.sample_size || 40)}</span>
      </div>
      <div class="card-bottom">
        <span class="card-drive-path" title="${escapeHtml(cleanPath)}">📁 ${escapeHtml(cleanPath)}</span>
        <div style="display:flex; gap:8px;">
          ${proj.file_count > 0 ? `<span>📄 ${formatNumber(proj.file_count)}</span>` : ''}
          ${proj.message_count > 0 ? `<span>💬 ${formatNumber(proj.message_count)}</span>` : ''}
        </div>
      </div>
    `;

    card.addEventListener('click', () => {
      triggerHaptic('light');
      showToast(`${proj.client_name}: ${proj.topic || 'Project details verified'}`);
    });

    return card;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function initKanbanControls() {
    const searchInput = document.getElementById('kanban-search');
    const clearBtn = document.getElementById('btn-clear-kanban-search');
    const filterChips = document.querySelectorAll('.filter-chips .chip');

    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        state.kanbanSearchQuery = e.target.value;
        if (clearBtn) {
          clearBtn.classList.toggle('hidden', !state.kanbanSearchQuery);
        }
        renderKanban();
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        state.kanbanSearchQuery = '';
        if (searchInput) searchInput.value = '';
        clearBtn.classList.add('hidden');
        renderKanban();
      });
    }

    filterChips.forEach((chip) => {
      chip.addEventListener('click', () => {
        triggerHaptic('light');
        filterChips.forEach((c) => c.classList.remove('active'));
        chip.classList.add('active');
        state.kanbanFilter = chip.getAttribute('data-filter') || 'all';
        renderKanban();
      });
    });
  }

  // --- Pricing Calculator Engine ---
  function updatePricing() {
    const degree = document.getElementById('calc-degree')?.value || 'master';
    const design = document.getElementById('calc-design')?.value || 'ancova';
    const sampleSize = parseInt(document.getElementById('calc-sample-size')?.value || '40', 10);
    const scalesCount = parseInt(document.getElementById('calc-scales-count')?.value || '2', 10);
    const isUrgent = !!document.getElementById('calc-urgent')?.checked;

    // Sliders badge updates
    const valSample = document.getElementById('val-sample-size');
    if (valSample) valSample.textContent = `N = ${formatNumber(sampleSize)}`;
    const valScales = document.getElementById('val-scales-count');
    if (valScales) {
      const scaleWord = state.currentLang === 'fa' ? 'پرسشنامه' : 'Scales';
      valScales.textContent = `${formatNumber(scalesCount)} ${scaleWord}`;
    }

    const isComplex = design === 'sem' || design === 'scale_val';

    // Pricing calculation based on proposal_price_estimator.py
    const services = {
      ch3: {
        checked: !!document.getElementById('svc-ch3')?.checked,
        price: isComplex ? 2500000 : 1500000,
        days: 3,
        name_en: 'Chapter 3: Methodology & G*Power',
        name_fa: 'فصل سوم: روش‌شناسی پژوهش و G*Power',
        badgeId: 'price-ch3'
      },
      sim: {
        checked: !!document.getElementById('svc-sim')?.checked,
        price: isComplex ? 2000000 : 1200000,
        days: 2,
        name_en: `SimDat Simulation (${scalesCount} scales, N=${sampleSize})`,
        name_fa: `شبیه‌سازی مونت‌کارلو (${scalesCount} مقیاس، ${sampleSize} نفر)`,
        badgeId: 'price-sim'
      },
      ch4: {
        checked: !!document.getElementById('svc-ch4')?.checked,
        price: design === 'regression' ? 2500000 : isComplex ? 3500000 : 3000000,
        days: isComplex ? 5 : design === 'regression' ? 3 : 4,
        name_en: 'Chapter 4: Statistical Findings & APA 7 Tables',
        name_fa: 'فصل چهارم: تحلیل آماری و جداول APA 7',
        badgeId: 'price-ch4'
      },
      ch5: {
        checked: !!document.getElementById('svc-ch5')?.checked,
        price: isComplex ? 3500000 : 2500000,
        days: 4,
        name_en: 'Chapter 5: Discussion & Mechanisms',
        name_fa: 'فصل پنجم: بحث، تبیین نظری و پیشینه',
        badgeId: 'price-ch5'
      },
      slides: {
        checked: !!document.getElementById('svc-slides')?.checked,
        price: 1200000,
        days: 2,
        name_en: 'Viva Voce Defense Slides Deck',
        name_fa: 'اسلایدهای دفاع ۱۶:۹ همراه با نوت گفتار',
        badgeId: 'price-slides'
      },
      audit: {
        checked: !!document.getElementById('svc-audit')?.checked,
        price: 1000000,
        days: 2,
        name_en: 'Comprehensive Thesis Integrity Audit',
        name_fa: 'ممیزی جامع و کنترل کیفیت رساله',
        badgeId: 'price-audit'
      }
    };

    // Update module price badges on the form
    const currency = state.currentLang === 'fa' ? 'تومان' : 'T';
    Object.keys(services).forEach((key) => {
      const svc = services[key];
      const badge = document.getElementById(svc.badgeId);
      if (badge) {
        badge.textContent = `${formatNumber(svc.price)} ${currency}`;
      }
    });

    // Calculate totals
    const selectedServices = Object.values(services).filter((s) => s.checked);
    let subtotal = selectedServices.reduce((sum, s) => sum + s.price, 0);
    let sequentialDays = selectedServices.reduce((sum, s) => sum + s.days, 0);

    // Urgency multiplier
    const urgencyMultiplier = isUrgent ? 1.4 : 1.0;
    let total = Math.round(subtotal * urgencyMultiplier);

    // Package discount (15% if 4 or more services selected)
    const hasDiscount = selectedServices.length >= 4;
    if (hasDiscount) {
      total = Math.round(total * 0.85);
    }

    // Realistic parallel days
    let workingDays = sequentialDays > 4 ? Math.max(sequentialDays - 3, 3) : sequentialDays;
    if (isUrgent) {
      workingDays = Math.min(workingDays, 2);
    }

    // Update Output Card DOM
    const priceDisplay = document.getElementById('quote-total-price');
    if (priceDisplay) {
      priceDisplay.textContent = `${formatNumber(total)} ${i18n[state.currentLang].price_unit}`;
    }

    const discountBadge = document.getElementById('quote-discount-badge');
    if (discountBadge) {
      if (hasDiscount) {
        discountBadge.textContent = i18n[state.currentLang].discount_badge_text;
        discountBadge.style.display = 'inline-block';
        discountBadge.style.background = 'rgba(16, 185, 129, 0.2)';
        discountBadge.style.color = '#34d399';
      } else {
        discountBadge.textContent = i18n[state.currentLang].no_discount_text;
        discountBadge.style.display = 'inline-block';
        discountBadge.style.background = 'rgba(255, 255, 255, 0.05)';
        discountBadge.style.color = '#94a3b8';
      }
    }

    const daysDisplay = document.getElementById('quote-total-days');
    if (daysDisplay) {
      daysDisplay.textContent = `${formatNumber(workingDays)} ${i18n[state.currentLang].days_suffix}`;
    }

    // Render Breakdown list
    const breakdownList = document.getElementById('quote-breakdown-list');
    if (breakdownList) {
      breakdownList.innerHTML = '';
      if (selectedServices.length === 0) {
        breakdownList.innerHTML = `<li class="summary-item" style="color:var(--text-muted);">${state.currentLang === 'fa' ? 'هیچ خدمتی انتخاب نشده است.' : 'No services selected.'}</li>`;
      } else {
        selectedServices.forEach((s) => {
          const li = document.createElement('li');
          li.className = 'summary-item';
          const name = state.currentLang === 'fa' ? s.name_fa : s.name_en;
          li.innerHTML = `
            <span>• ${escapeHtml(name)}</span>
            <b>${formatNumber(s.price)} ${currency}</b>
          `;
          breakdownList.appendChild(li);
        });
      }
    }

    // Save quotation payload for copy/send
    window.CURRENT_QUOTE = {
      total,
      workingDays,
      subtotal,
      hasDiscount,
      isUrgent,
      selectedCount: selectedServices.length,
      degree,
      design,
      sampleSize,
      scalesCount,
      services: selectedServices.map((s) => ({
        name: state.currentLang === 'fa' ? s.name_fa : s.name_en,
        price: s.price
      }))
    };
  }

  function initCalculatorListeners() {
    const inputs = [
      'calc-degree',
      'calc-design',
      'calc-sample-size',
      'calc-scales-count',
      'calc-urgent',
      'svc-ch3',
      'svc-sim',
      'svc-ch4',
      'svc-ch5',
      'svc-slides',
      'svc-audit'
    ];

    inputs.forEach((id) => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('input', () => {
          updatePricing();
        });
        el.addEventListener('change', () => {
          triggerHaptic('light');
          updatePricing();
        });
      }
    });

    const copyBtn = document.getElementById('btn-copy-quote');
    if (copyBtn) {
      copyBtn.addEventListener('click', () => {
        triggerHaptic('medium');
        copyQuotationCard();
      });
    }

    const sendBtn = document.getElementById('btn-send-quote');
    if (sendBtn) {
      sendBtn.addEventListener('click', () => {
        triggerHaptic('success');
        sendQuotationToTelegram();
      });
    }
  }

  function copyQuotationCard() {
    const q = window.CURRENT_QUOTE;
    if (!q) return;

    let text = '';
    if (state.currentLang === 'fa') {
      text = `🎓 *پیش‌فاکتور رسمی رساله و تحلیل آماری*
👨‍🏫 مشاور: صابر قادری (@GhaderiSaber)
───────────────────
📊 *مشخصات پژوهش:*
• طرح پژوهش: ${q.design}
• حجم نمونه: ${q.sampleSize} نفر
• تعداد پرسشنامه: ${q.scalesCount} عدد
───────────────────
📋 *خدمات انتخاب‌شده:*
${q.services.map((s) => `▫️ ${s.name} : ${formatNumber(s.price)} تومان`).join('\n')}
───────────────────
💰 *سرمایه‌گذاری کل:* ${formatNumber(q.total)} تومان
⏱ *زمان‌بندی تحویل:* ${q.workingDays} روز کاری
✨ با تضمین تایید در جلسه دفاع و اصلاحات رایگان استاد راهنما`;
    } else {
      text = `🎓 *Academic Thesis & Statistical Consultancy Quotation*
👨‍🏫 Consultant: Saber Ghaderi (@GhaderiSaber)
───────────────────
📊 *Research Parameters:*
• Study Design: ${q.design}
• Sample Size: N = ${q.sampleSize}
• Measurement Scales: ${q.scalesCount}
───────────────────
📋 *Selected Deliverable Modules:*
${q.services.map((s) => `▫️ ${s.name} : ${formatNumber(s.price)} Tomans`).join('\n')}
───────────────────
💰 *Total Investment:* ${formatNumber(q.total)} Tomans
⏱ *Turnaround:* ${q.workingDays} Business Days
✨ Includes defense viva guarantee and supervisor revisions`;
    }

    navigator.clipboard
      .writeText(text)
      .then(() => {
        showToast(i18n[state.currentLang].copied_toast);
      })
      .catch((err) => {
        console.error('Clipboard write failed:', err);
        showToast('Clipboard error! Check browser permissions.');
      });
  }

  function sendQuotationToTelegram() {
    const q = window.CURRENT_QUOTE;
    if (!q) return;

    // If inside native Telegram Mini App with sendData capability
    if (tg && tg.sendData) {
      tg.sendData(
        JSON.stringify({
          action: 'submit_quote',
          total: q.total,
          workingDays: q.workingDays,
          services_count: q.services.length
        })
      );
      showToast('Quotation sent to Telegram!');
      return;
    }

    // Standalone Web Browser: Direct Telegram link to @GhaderiSaber
    const msg =
      state.currentLang === 'fa'
        ? `سلام جناب قادری، پیش‌فاکتور طرح پژوهش من در مینی‌اپ محاسبه شد:\n• برآورد: ${formatNumber(q.total)} تومان (${q.workingDays} روز کاری)\n• طرح: ${q.design}\nلطفاً راهنمایی بفرمایید.`
        : `Hello Saber, I calculated my thesis project quotation via the Mini App:\n• Estimated Investment: ${formatNumber(q.total)} Tomans (${q.workingDays} business days)\n• Design: ${q.design}\nLooking forward to your guidance.`;

    const url = `https://t.me/GhaderiSaber?text=${encodeURIComponent(msg)}`;
    window.open(url, '_blank');
  }

  // --- Scales Registry Explorer ---
  function renderScales() {
    const container = document.getElementById('scales-container');
    if (!container) return;

    container.innerHTML = '';
    const query = state.scaleSearchQuery.trim().toLowerCase();

    const filtered = state.scales.filter((scale) => {
      if (state.scaleCategory !== 'all' && scale.category !== state.scaleCategory) {
        return false;
      }
      if (query) {
        const matchEn = (scale.name_en || '').toLowerCase().includes(query);
        const matchFa = (scale.name_fa || '').toLowerCase().includes(query);
        const matchAuthor = (scale.author || '').toLowerCase().includes(query);
        const matchSub = (scale.subscales || []).some((s) => s.toLowerCase().includes(query));
        if (!matchEn && !matchFa && !matchAuthor && !matchSub) {
          return false;
        }
      }
      return true;
    });

    if (filtered.length === 0) {
      container.innerHTML = `
        <div style="grid-column: 1/-1; text-align:center; padding: 40px; color:var(--text-muted);">
          🔍 ${state.currentLang === 'fa' ? 'هیچ پرسشنامه‌ای با این مشخصات یافت نشد.' : 'No questionnaires matched your search.'}
        </div>
      `;
      return;
    }

    filtered.forEach((scale) => {
      const card = document.createElement('div');
      card.className = 'scale-card';

      const subscalesMarkup = (scale.subscales || [])
        .map((s) => `<span class="subscale-tag">${escapeHtml(s)}</span>`)
        .join('');

      card.innerHTML = `
        <div>
          <div class="scale-header">
            <h4 class="scale-title-en">${escapeHtml(scale.name_en)}</h4>
            <span class="scale-badge-items">${formatNumber(scale.items_count)} ${state.currentLang === 'fa' ? 'گویه' : 'Items'}</span>
          </div>
          <div class="scale-title-fa">${escapeHtml(scale.name_fa)}</div>
          <div class="scale-author">👤 ${escapeHtml(scale.author || '')} | ${escapeHtml(scale.rating_scale || '')}</div>
          
          <div class="scale-subscales-list">
            <b>${state.currentLang === 'fa' ? 'خرده‌مقیاس‌ها و عوامل:' : 'Subscales & Factors:'}</b>
            <div class="scale-subscales-tags">${subscalesMarkup}</div>
          </div>
        </div>

        <button class="btn-select-scale">
          + ${i18n[state.currentLang].select_scale_btn}
        </button>
      `;

      const selectBtn = card.querySelector('.btn-select-scale');
      selectBtn.addEventListener('click', () => {
        triggerHaptic('medium');
        selectScaleForCalculator(scale);
      });

      container.appendChild(card);
    });
  }

  function selectScaleForCalculator(scale) {
    // Switch to calculator tab
    const calcTabBtn = document.querySelector('.nav-tab[data-tab="calculator"]');
    if (calcTabBtn) calcTabBtn.click();

    // Increment scales count slider if less than 8
    const scalesSlider = document.getElementById('calc-scales-count');
    if (scalesSlider) {
      const currentVal = parseInt(scalesSlider.value, 10);
      if (currentVal < 8) {
        scalesSlider.value = currentVal + 1;
        updatePricing();
      }
    }

    showToast(`${scale.name_en}: ${i18n[state.currentLang].scale_selected_toast}`);
  }

  function initScalesControls() {
    const searchInput = document.getElementById('scales-search');
    const clearBtn = document.getElementById('btn-clear-scale-search');
    const categoryChips = document.querySelectorAll('#scale-category-chips .chip');

    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        state.scaleSearchQuery = e.target.value;
        if (clearBtn) {
          clearBtn.classList.toggle('hidden', !state.scaleSearchQuery);
        }
        renderScales();
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        state.scaleSearchQuery = '';
        if (searchInput) searchInput.value = '';
        clearBtn.classList.add('hidden');
        renderScales();
      });
    }

    categoryChips.forEach((chip) => {
      chip.addEventListener('click', () => {
        triggerHaptic('light');
        categoryChips.forEach((c) => c.classList.remove('active'));
        chip.classList.add('active');
        state.scaleCategory = chip.getAttribute('data-cat') || 'all';
        renderScales();
      });
    });
  }

  // --- Dynamic API Fetch (Fallback & Progressive Enhancement) ---
  function fetchLiveProjects() {
    fetch('/api/projects')
      .then((res) => {
        if (!res.ok) throw new Error('API unavailable');
        return res.json();
      })
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          state.projects = data;
          updateProjectBadge();
          renderKanban();
        }
      })
      .catch(() => {
        // Quietly fallback to seed data
      });
  }

  // --- App Initialization ---
  function init() {
    initTabs();
    initKanbanControls();
    initCalculatorListeners();
    initScalesControls();

    // Language toggle
    const langBtn = document.getElementById('btn-lang-toggle');
    if (langBtn) {
      langBtn.addEventListener('click', () => {
        triggerHaptic('medium');
        const nextLang = state.currentLang === 'en' ? 'fa' : 'en';
        applyLanguage(nextLang);
      });
    }

    // Apply default language
    applyLanguage(state.currentLang);

    // Initial renders
    renderKanban();
    updatePricing();
    renderScales();

    // Attempt live API fetch
    fetchLiveProjects();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
