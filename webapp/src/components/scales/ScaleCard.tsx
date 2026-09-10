import React from 'react';
import { Scale } from '../../types';
import { useLanguage } from '../../hooks/useLanguage';
import { useTelegram } from '../../hooks/useTelegram';
import { PlusCircle, Layers } from 'lucide-react';

interface ScaleCardProps {
  scale: Scale;
  onSelect: (scale: Scale) => void;
}

export const ScaleCard: React.FC<ScaleCardProps> = ({ scale, onSelect }) => {
  const { t, formatNumber } = useLanguage();
  const { haptic } = useTelegram();

  return (
    <div className="flex flex-col justify-between p-4 rounded-2xl glass-card bg-slate-900/60 border border-slate-700/40 hover:border-indigo-500/40 transition-all duration-200 hover:-translate-y-1 hover:shadow-xl group">
      <div>
        <div className="flex justify-between items-start gap-2 mb-1.5">
          <h4 className="text-xs md:text-sm font-bold text-slate-100 group-hover:text-indigo-200 transition-colors">
            {scale.name_en}
          </h4>
          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-cyan-500/15 text-cyan-300 border border-cyan-500/20 whitespace-nowrap shrink-0">
            {formatNumber(scale.items_count)} {t('items_unit')}
          </span>
        </div>

        <div className="text-xs text-indigo-300 font-medium mb-1.5">
          {scale.name_fa}
        </div>

        <div className="text-[11px] text-slate-400 mb-3">
          👤 {scale.author} | {scale.rating_scale}
        </div>

        {/* Subscales */}
        {scale.subscales && scale.subscales.length > 0 && (
          <div className="p-2.5 rounded-xl bg-slate-800/40 border border-slate-700/30 mb-4">
            <div className="flex items-center gap-1 text-[11px] font-semibold text-slate-300 mb-1.5">
              <Layers className="w-3 h-3 text-slate-400" />
              <span>{t('subscales_label')}</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {scale.subscales.map((sub, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 rounded text-[10px] bg-white/5 border border-white/5 text-slate-300"
                >
                  {sub}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      <button
        onClick={() => {
          haptic('medium');
          onSelect(scale);
        }}
        className="w-full flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl bg-indigo-600/15 hover:bg-indigo-600 text-indigo-300 hover:text-white border border-indigo-500/30 text-xs font-semibold transition-all cursor-pointer active:scale-95"
      >
        <PlusCircle className="w-3.5 h-3.5" />
        <span>{t('select_scale_btn')}</span>
      </button>
    </div>
  );
};
