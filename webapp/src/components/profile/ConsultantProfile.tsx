import React from 'react';
import { useLanguage } from '../../hooks/useLanguage';
import { useTelegram } from '../../hooks/useTelegram';
import { MessageSquare, Send, Shield, CheckCircle } from 'lucide-react';

export const ConsultantProfile: React.FC = () => {
  const { lang, t } = useLanguage();
  const { haptic } = useTelegram();

  const competencies = [
    lang === 'fa'
      ? 'فرموله‌سازی فرضیات جهت‌دار و تعاریف مفهومی/عملیاتی (فصل ۱ و ۳)'
      : 'Formulating directional hypotheses & operational definitions (Chapters 1 & 3)',
    lang === 'fa'
      ? 'تعیین دقیق حجم نمونه و توان آزمون آماری با G*Power 3.1'
      : 'Determining exact statistical sample power & size with G*Power 3.1',
    lang === 'fa'
      ? 'دسترسی به بانک جامع ۴,۸۸۰ پرسشنامه استاندارد ایرانی و خارجی با نمره‌گذاری'
      : 'Access to master library of 4,880 validated questionnaires with scoring keys',
    lang === 'fa'
      ? 'آزمون‌های پیشرفته: ANCOVA، MANCOVA، اندازه‌گیری مکرر و تحلیل میانجی بوت‌استرپ'
      : 'Inferential statistics: ANCOVA, MANCOVA, Repeated Measures & bootstrap mediation',
    lang === 'fa'
      ? 'مدل‌یابی معادلات ساختاری (SEM / CFA) در AMOS و SmartPLS 4 و R lavaan'
      : 'Structural Equation Modeling (SEM / CFA) via AMOS, SmartPLS 4, and R lavaan',
    lang === 'fa'
      ? 'نگارش فصل پنجم و تبیین روان‌شناختی یافته‌ها متناسب با پیشینه روز دنیا'
      : 'Chapter 5 theoretical integration matching contemporary international literature',
  ];

  const badges = [
    '@GhaderiSaber',
    'SPSS 28',
    'AMOS 26',
    'SmartPLS 4',
    'R (lavaan)',
    'G*Power 3.1',
    'APA 7th Edition',
  ];

  return (
    <div className="p-6 rounded-2xl glass-panel bg-slate-900/65 border border-slate-800 shadow-2xl backdrop-blur-xl">
      {/* Profile Header */}
      <div className="flex flex-col sm:flex-row items-center sm:items-start gap-4 pb-6 border-b border-slate-800 text-center sm:text-left">
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center text-3xl shadow-xl shadow-indigo-500/20 shrink-0">
          👨‍🎓
        </div>
        <div className="space-y-1.5 flex-1">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <h2 className="text-xl font-bold text-slate-100">
              Saber Ghaderi (صابر قادری)
            </h2>
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 w-fit mx-auto sm:mx-0">
              Digital Twin Desk: 124911145
            </span>
          </div>
          <p className="text-xs text-slate-300 font-medium">
            Ph.D. Researcher in Psychology | Statistical & Psychometric Methodology Consultant
          </p>
          <div className="flex flex-wrap gap-1.5 pt-1 justify-center sm:justify-start">
            {badges.map((b, idx) => (
              <span
                key={idx}
                className="px-2.5 py-0.5 rounded-md text-[11px] font-mono bg-slate-800/90 text-slate-300 border border-slate-700/60"
              >
                {b}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Profile Body Columns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
        {/* Competencies */}
        <div>
          <h3 className="text-sm font-bold text-slate-200 mb-3 flex items-center gap-2">
            <Shield className="w-4 h-4 text-indigo-400" />
            <span>{t('profile_expertise_title')}</span>
          </h3>
          <ul className="space-y-2.5">
            {competencies.map((comp, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>{comp}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Contact & Telegram Card */}
        <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-200 mb-3 flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-cyan-400" />
              <span>{t('profile_contact_title')}</span>
            </h3>

            <div className="space-y-2 text-xs text-slate-300 mb-5">
              <div className="flex justify-between py-1.5 border-b border-slate-700/40">
                <span className="text-slate-400">Telegram Direct:</span>
                <a
                  href="https://t.me/GhaderiSaber"
                  target="_blank"
                  rel="noreferrer"
                  className="text-sky-400 font-bold hover:underline"
                >
                  @GhaderiSaber
                </a>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-700/40">
                <span className="text-slate-400">Assistant Bot:</span>
                <a
                  href="https://t.me/SaberAcademicBot"
                  target="_blank"
                  rel="noreferrer"
                  className="text-sky-400 font-bold hover:underline"
                >
                  @SaberAcademicBot
                </a>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-700/40">
                <span className="text-slate-400">Operational Cloud:</span>
                <span className="text-slate-200 font-mono">Google Drive (My Work)</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-400">Turnaround:</span>
                <span className="text-slate-200 font-medium">
                  2 to 8 Business Days (48h Express)
                </span>
              </div>
            </div>
          </div>

          <a
            href="https://t.me/GhaderiSaber"
            target="_blank"
            rel="noreferrer"
            onClick={() => haptic('medium')}
            className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition-all cursor-pointer active:scale-95"
          >
            <Send className="w-4 h-4" />
            <span>Send Direct Message (@GhaderiSaber)</span>
          </a>
        </div>
      </div>
    </div>
  );
};
