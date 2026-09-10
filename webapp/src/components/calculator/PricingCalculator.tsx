import React, { useState, useMemo } from 'react';
import { DegreeLevel, ResearchDesign, QuotationResult } from '../../types';
import { QuotationCard } from './QuotationCard';
import { useLanguage } from '../../hooks/useLanguage';
import { useTelegram } from '../../hooks/useTelegram';
import { Settings, Zap, CheckSquare, Square } from 'lucide-react';

interface PricingCalculatorProps {
  onShowToast: (msg: string) => void;
  initialScalesCount?: number;
}

export const PricingCalculator: React.FC<PricingCalculatorProps> = ({
  onShowToast,
  initialScalesCount = 2,
}) => {
  const { lang, t, formatNumber } = useLanguage();
  const { tg, isTelegramWebApp, sendData, haptic } = useTelegram();

  const [degree, setDegree] = useState<DegreeLevel>('master');
  const [design, setDesign] = useState<ResearchDesign>('ancova');
  const [sampleSize, setSampleSize] = useState<number>(40);
  const [scalesCount, setScalesCount] = useState<number>(initialScalesCount);
  const [isUrgent, setIsUrgent] = useState<boolean>(false);

  // Selected services state
  const [selectedServices, setSelectedServices] = useState<Record<string, boolean>>({
    ch3: true,
    sim: true,
    ch4: true,
    ch5: true,
    slides: false,
    audit: true,
  });

  const isComplex = design === 'sem' || design === 'scale_val';

  // Dynamic modules pricing calculation
  const servicesConfig = useMemo(() => {
    return [
      {
        id: 'ch3',
        name_en: 'Chapter 3: Methodology & G*Power',
        name_fa: 'فصل سوم: روش‌شناسی پژوهش و G*Power',
        meta_en: 'Research design, instruments, sample power calculation',
        meta_fa: 'طرح پژوهش، ابزارها، روایی/پایایی و محاسبه حجم نمونه',
        price: isComplex ? 2500000 : 1500000,
        days: 3,
      },
      {
        id: 'sim',
        name_en: `SimDat Simulation (${scalesCount} scales, N=${sampleSize})`,
        name_fa: `شبیه‌سازی داده‌های روان‌سنجی (${scalesCount} مقیاس، ${sampleSize} نفر)`,
        meta_en: 'Monte Carlo discrete Likert simulation with real covariance',
        meta_fa: 'شبیه‌سازی مونت‌کارلو گسسته لیکرت با ماتریس کوواریانس دقیق',
        price: isComplex ? 2000000 : 1200000,
        days: 2,
      },
      {
        id: 'ch4',
        name_en: 'Chapter 4: Statistical Analysis & APA 7 Tables',
        name_fa: 'فصل چهارم: تحلیل آماری و جداول APA 7',
        meta_en: 'Normality, inferential hypothesis testing, raw output files',
        meta_fa: 'بررسی مفروضه‌ها، آزمون فرضیات، فایل‌های خروجی نرم‌افزاری',
        price: design === 'regression' ? 2500000 : isComplex ? 3500000 : 3000000,
        days: isComplex ? 5 : design === 'regression' ? 3 : 4,
      },
      {
        id: 'ch5',
        name_en: 'Chapter 5: Discussion & Theoretical Integration',
        name_fa: 'فصل پنجم: بحث، تبیین نظری و پیشینه',
        meta_en: 'Findings integration, literature comparison, limitations',
        meta_fa: 'تبیین سازوکارهای روان‌شناختی، پیشینه ایرانی و خارجی',
        price: isComplex ? 3500000 : 2500000,
        days: 4,
      },
      {
        id: 'slides',
        name_en: 'Viva Voce Defense Slides Deck',
        name_fa: 'اسلایدهای حرفه‌ای جلسه دفاع',
        meta_en: 'Widescreen 16:9 presentation with speaker script notes',
        meta_fa: 'پاورپوینت ۱۶:۹ همراه با نوت سناریو و گفتار دانشجو',
        price: 1200000,
        days: 2,
      },
      {
        id: 'audit',
        name_en: 'Comprehensive Thesis Integrity Audit',
        name_fa: 'ممیزی جامع و کنترل کیفیت رساله',
        meta_en: 'Hypothesis alignment, df verification, citation audit',
        meta_fa: 'هم‌ترازی فرضیه-یافته، کنترل درجات آزادی و رفرنس‌ها',
        price: 1000000,
        days: 2,
      },
    ];
  }, [isComplex, design, sampleSize, scalesCount]);

  // Overall quotation computation
  const quoteResult: QuotationResult = useMemo(() => {
    const active = servicesConfig.filter((s) => selectedServices[s.id]);
    const subtotal = active.reduce((acc, curr) => acc + curr.price, 0);
    const seqDays = active.reduce((acc, curr) => acc + curr.days, 0);

    const hasDiscount = active.length >= 4;
    const urgencyMultiplier = isUrgent ? 1.4 : 1.0;

    let total = Math.round(subtotal * urgencyMultiplier);
    if (hasDiscount) {
      total = Math.round(total * 0.85);
    }

    let workingDays = seqDays > 4 ? Math.max(seqDays - 3, 3) : seqDays;
    if (isUrgent) {
      workingDays = Math.min(workingDays, 2);
    }

    return {
      total,
      subtotal,
      workingDays,
      hasDiscount,
      isUrgent,
      degree,
      design,
      sampleSize,
      scalesCount,
      services: active.map((s) => ({
        name: lang === 'fa' ? s.name_fa : s.name_en,
        price: s.price,
      })),
    };
  }, [servicesConfig, selectedServices, isUrgent, degree, design, sampleSize, scalesCount, lang]);

  const toggleService = (id: string) => {
    haptic('light');
    setSelectedServices((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const copyQuoteToClipboard = () => {
    let text = '';
    if (lang === 'fa') {
      text = `🎓 *پیش‌فاکتور رسمی رساله و تحلیل آماری*
👨‍🏫 مشاور: صابر قادری (@GhaderiSaber)
───────────────────
📊 *مشخصات پژوهش:*
• مقطع: ${degree === 'phd' ? 'دکتری تخصصی' : 'کارشناسی ارشد'}
• طرح پژوهش: ${design}
• حجم نمونه: ${quoteResult.sampleSize} نفر
• تعداد پرسشنامه: ${quoteResult.scalesCount} عدد
───────────────────
📋 *خدمات انتخاب‌شده:*
${quoteResult.services.map((s) => `▫️ ${s.name} : ${formatNumber(s.price)} تومان`).join('\n')}
───────────────────
💰 *سرمایه‌گذاری کل:* ${formatNumber(quoteResult.total)} تومان
⏱ *زمان‌بندی تحویل:* ${quoteResult.workingDays} روز کاری
✨ با تضمین تایید در جلسه دفاع و اصلاحات رایگان استاد راهنما`;
    } else {
      text = `🎓 *Academic Thesis & Statistical Consultancy Quotation*
👨‍🏫 Consultant: Saber Ghaderi (@GhaderiSaber)
───────────────────
📊 *Research Parameters:*
• Academic Level: ${degree === 'phd' ? 'Doctorate (Ph.D.)' : "Master's (M.A./M.Sc.)"}
• Study Design: ${design}
• Sample Size: N = ${quoteResult.sampleSize}
• Measurement Scales: ${quoteResult.scalesCount}
───────────────────
📋 *Selected Deliverable Modules:*
${quoteResult.services.map((s) => `▫️ ${s.name} : ${formatNumber(s.price)} Tomans`).join('\n')}
───────────────────
💰 *Total Investment:* ${formatNumber(quoteResult.total)} Tomans
⏱ *Turnaround:* ${quoteResult.workingDays} Business Days
✨ Includes defense viva guarantee and supervisor revisions`;
    }

    navigator.clipboard
      .writeText(text)
      .then(() => {
        onShowToast(t('copied_toast'));
      })
      .catch((err) => {
        console.error('Clipboard error:', err);
        onShowToast('Could not copy to clipboard');
      });
  };

  const sendQuotationToTelegram = () => {
    if (isTelegramWebApp && tg?.sendData) {
      sendData({
        action: 'submit_quote',
        total: quoteResult.total,
        workingDays: quoteResult.workingDays,
        services_count: quoteResult.services.length,
      });
      onShowToast('Quotation submitted via Telegram WebApp!');
      return;
    }

    // Direct Telegram link fallback
    const msg =
      lang === 'fa'
        ? `سلام جناب قادری، پیش‌فاکتور طرح پژوهش من در مینی‌اپ محاسبه شد:\n• برآورد: ${formatNumber(quoteResult.total)} تومان (${quoteResult.workingDays} روز کاری)\n• طرح: ${design}\nلطفاً راهنمایی بفرمایید.`
        : `Hello Saber, I calculated my thesis project quotation via the Mini App:\n• Estimated Investment: ${formatNumber(quoteResult.total)} Tomans (${quoteResult.workingDays} business days)\n• Design: ${design}\nLooking forward to your guidance.`;

    const url = `https://t.me/GhaderiSaber?text=${encodeURIComponent(msg)}`;
    window.open(url, '_blank');
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      {/* Parameters & Modules Form (Col 7) */}
      <div className="lg:col-span-7 p-5 rounded-2xl glass-panel bg-slate-900/60 border border-slate-800 space-y-5">
        <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
          <Settings className="w-5 h-5 text-indigo-400" />
          <h3 className="text-sm md:text-base font-bold text-slate-100">
            {t('calc_params_title')}
          </h3>
        </div>

        {/* Degree & Design dropdowns */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              {t('lbl_degree')}
            </label>
            <select
              value={degree}
              onChange={(e) => {
                haptic('light');
                setDegree(e.target.value as DegreeLevel);
              }}
              className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 cursor-pointer"
            >
              <option value="master">{t('opt_master')}</option>
              <option value="phd">{t('opt_phd')}</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              {t('lbl_design')}
            </label>
            <select
              value={design}
              onChange={(e) => {
                haptic('light');
                setDesign(e.target.value as ResearchDesign);
              }}
              className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 cursor-pointer truncate"
            >
              <option value="ancova">{t('design_ancova')}</option>
              <option value="sem">{t('design_sem')}</option>
              <option value="regression">{t('design_regression')}</option>
              <option value="scale_val">{t('design_scale_val')}</option>
              <option value="qualitative">{t('design_qualitative')}</option>
            </select>
          </div>
        </div>

        {/* Sample Size Slider */}
        <div>
          <div className="flex justify-between items-center mb-1 text-xs">
            <span className="font-semibold text-slate-300">{t('lbl_sample_size')}</span>
            <span className="font-mono font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
              N = {formatNumber(sampleSize)}
            </span>
          </div>
          <input
            type="range"
            min="15"
            max="600"
            step="5"
            value={sampleSize}
            onChange={(e) => setSampleSize(parseInt(e.target.value, 10))}
            className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
          />
          <div className="flex justify-between text-[10px] text-slate-500 px-0.5 mt-1">
            <span>15</span>
            <span>100</span>
            <span>250</span>
            <span>400</span>
            <span>600</span>
          </div>
        </div>

        {/* Scales Count Slider */}
        <div>
          <div className="flex justify-between items-center mb-1 text-xs">
            <span className="font-semibold text-slate-300">{t('lbl_scales_count')}</span>
            <span className="font-mono font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
              {formatNumber(scalesCount)} {lang === 'fa' ? 'پرسشنامه' : 'Scales'}
            </span>
          </div>
          <input
            type="range"
            min="1"
            max="8"
            step="1"
            value={scalesCount}
            onChange={(e) => setScalesCount(parseInt(e.target.value, 10))}
            className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
          />
        </div>

        {/* Express Priority Toggle */}
        <div
          onClick={() => {
            haptic('light');
            setIsUrgent(!isUrgent);
          }}
          className={`flex items-center justify-between p-3 rounded-xl border transition-all cursor-pointer ${
            isUrgent
              ? 'bg-amber-500/10 border-amber-500/40 shadow-lg shadow-amber-500/10'
              : 'bg-slate-800/60 border-slate-700/60 hover:bg-slate-800'
          }`}
        >
          <div className="flex items-center gap-2.5">
            <div className={`p-1.5 rounded-lg ${isUrgent ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-700 text-slate-400'}`}>
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-100">{t('lbl_urgent')}</p>
              <p className="text-[11px] text-slate-400">{t('desc_urgent')}</p>
            </div>
          </div>
          <div className={`w-9 h-5 rounded-full p-0.5 transition-colors ${isUrgent ? 'bg-amber-500' : 'bg-slate-700'}`}>
            <div className={`w-4 h-4 rounded-full bg-white transition-transform ${isUrgent ? 'translate-x-4' : 'translate-x-0'}`} />
          </div>
        </div>

        {/* Service Checkboxes */}
        <div className="space-y-2 pt-2">
          <label className="block text-xs font-bold text-slate-300">
            {t('lbl_select_services')}
          </label>
          <div className="space-y-2">
            {servicesConfig.map((svc) => {
              const isChecked = Boolean(selectedServices[svc.id]);
              return (
                <div
                  key={svc.id}
                  onClick={() => toggleService(svc.id)}
                  className={`flex items-center justify-between p-3 rounded-xl border transition-all cursor-pointer ${
                    isChecked
                      ? 'bg-slate-800/90 border-indigo-500/40 shadow-sm'
                      : 'bg-slate-800/30 border-slate-800 opacity-65 hover:opacity-100'
                  }`}
                >
                  <div className="flex items-start gap-2.5 max-w-[70%]">
                    {isChecked ? (
                      <CheckSquare className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                    ) : (
                      <Square className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
                    )}
                    <div>
                      <div className="text-xs font-semibold text-slate-200">
                        {lang === 'fa' ? svc.name_fa : svc.name_en}
                      </div>
                      <div className="text-[11px] text-slate-400 leading-tight">
                        {lang === 'fa' ? svc.meta_fa : svc.meta_en}
                      </div>
                    </div>
                  </div>

                  <span className="text-xs font-mono font-bold text-indigo-300 bg-indigo-500/10 px-2.5 py-1 rounded-lg border border-indigo-500/20 whitespace-nowrap">
                    {formatNumber(svc.price)} {lang === 'fa' ? 'تومان' : 'T'}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Live Quote Output Card (Col 5) */}
      <div className="lg:col-span-5">
        <div className="sticky top-4">
          <QuotationCard
            quote={quoteResult}
            onCopy={copyQuoteToClipboard}
            onSendToTelegram={sendQuotationToTelegram}
          />
        </div>
      </div>
    </div>
  );
};
