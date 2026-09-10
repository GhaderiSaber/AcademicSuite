import React from 'react';
import { QuotationResult } from '../../types';
import { useLanguage } from '../../hooks/useLanguage';
import { useTelegram } from '../../hooks/useTelegram';
import { Sparkles, ShieldCheck, Copy, Send, Clock, Award } from 'lucide-react';

interface QuotationCardProps {
  quote: QuotationResult;
  onCopy: () => void;
  onSendToTelegram: () => void;
}

export const QuotationCard: React.FC<QuotationCardProps> = ({
  quote,
  onCopy,
  onSendToTelegram,
}) => {
  const { lang, t, formatNumber } = useLanguage();
  const { haptic } = useTelegram();

  return (
    <div className="flex flex-col justify-between p-5 rounded-2xl glass-panel bg-slate-900/75 border border-indigo-500/30 shadow-2xl backdrop-blur-xl relative overflow-hidden">
      {/* Decorative gradient blur */}
      <div className="absolute top-0 right-0 w-48 h-48 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      <div>
        <div className="flex items-center justify-between mb-4">
          <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
            Saber Ghaderi Consultancy
          </span>
          <Award className="w-5 h-5 text-indigo-400" />
        </div>

        <h3 className="text-base font-bold text-slate-100 mb-4">
          {t('quote_summary_title')}
        </h3>

        {/* Highlights Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-5">
          <div className="p-3.5 rounded-xl bg-slate-800/80 border border-slate-700/60 flex flex-col justify-center">
            <span className="text-[11px] text-slate-400 font-medium">
              {t('lbl_total_price')}
            </span>
            <span className="text-lg md:text-xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400 my-1">
              {formatNumber(quote.total)} {t('price_unit')}
            </span>
            {quote.hasDiscount ? (
              <span className="text-[10px] text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded w-fit border border-emerald-500/20">
                {t('discount_badge_text')}
              </span>
            ) : (
              <span className="text-[10px] text-slate-400 font-medium bg-slate-700/30 px-2 py-0.5 rounded w-fit">
                {t('no_discount_text')}
              </span>
            )}
          </div>

          <div className="p-3.5 rounded-xl bg-slate-800/80 border border-slate-700/60 flex flex-col justify-center">
            <span className="text-[11px] text-slate-400 font-medium flex items-center gap-1">
              <Clock className="w-3 h-3 text-cyan-400" />
              {t('lbl_total_days')}
            </span>
            <span className="text-lg md:text-xl font-bold text-slate-100 my-1">
              {formatNumber(quote.workingDays)} {t('days_suffix')}
            </span>
            <span className="text-[10px] text-slate-400">
              {t('parallel_timeline_note')}
            </span>
          </div>
        </div>

        {/* Breakdown List */}
        <div className="mb-5">
          <h4 className="text-xs font-bold text-slate-300 mb-2.5">
            {t('summary_breakdown')}
          </h4>
          <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
            {quote.services.length === 0 ? (
              <p className="text-xs text-slate-500 italic">No services selected.</p>
            ) : (
              quote.services.map((svc, idx) => (
                <div
                  key={idx}
                  className="flex justify-between items-center text-xs py-1.5 px-2.5 rounded-lg bg-slate-800/50 border border-slate-700/40 text-slate-300"
                >
                  <span className="truncate pr-2">• {svc.name}</span>
                  <span className="font-semibold text-slate-200 shrink-0 font-mono">
                    {formatNumber(svc.price)} {lang === 'fa' ? 'تومان' : 'T'}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Guarantees Box */}
        <div className="p-3 rounded-xl bg-indigo-950/20 border border-indigo-500/20 text-[11px] space-y-1.5 text-slate-300 mb-6">
          <div className="flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
            <span><b>APA 7th Edition:</b> Raw software outputs & standard tables</span>
          </div>
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span><b>Defense Guarantee:</b> Free revisions until full approval</span>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-2.5">
        <button
          onClick={() => {
            haptic('medium');
            onCopy();
          }}
          className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs transition-all cursor-pointer border border-slate-600/50 active:scale-95"
        >
          <Copy className="w-3.5 h-3.5 text-slate-400" />
          <span>{t('btn_copy_quote')}</span>
        </button>

        <button
          onClick={() => {
            haptic('success');
            onSendToTelegram();
          }}
          className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition-all cursor-pointer active:scale-95"
        >
          <Send className="w-3.5 h-3.5" />
          <span>{t('btn_send_telegram')}</span>
        </button>
      </div>
    </div>
  );
};
