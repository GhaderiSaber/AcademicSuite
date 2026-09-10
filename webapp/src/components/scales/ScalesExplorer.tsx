import React, { useState, useMemo } from 'react';
import { Scale } from '../../types';
import { ScaleCard } from './ScaleCard';
import { useLanguage } from '../../hooks/useLanguage';
import { useTelegram } from '../../hooks/useTelegram';
import { Search, X } from 'lucide-react';

interface ScalesExplorerProps {
  scales: Scale[];
  onScaleSelect: (scale: Scale) => void;
}

export const ScalesExplorer: React.FC<ScalesExplorerProps> = ({ scales, onScaleSelect }) => {
  const { lang, t } = useLanguage();
  const { haptic } = useTelegram();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { id: 'all', label_en: 'All Instruments', label_fa: 'همه پرسشنامه‌ها' },
    { id: 'resilience', label_en: 'Resilience', label_fa: 'تاب‌آوری' },
    { id: 'depression', label_en: 'Depression', label_fa: 'افسردگی' },
    { id: 'anxiety', label_en: 'Anxiety', label_fa: 'اضطراب' },
    { id: 'emotion', label_en: 'Emotion Reg', label_fa: 'تنظیم هیجان' },
    { id: 'schema', label_en: 'Schema', label_fa: 'طرحواره' },
    { id: 'compassion', label_en: 'Self-Compassion', label_fa: 'شفقت خود' },
    { id: 'marital', label_en: 'Marital', label_fa: 'زناشویی' },
  ];

  const filteredScales = useMemo(() => {
    let result = scales;

    if (selectedCategory !== 'all') {
      result = result.filter((s) => s.category === selectedCategory);
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      result = result.filter(
        (s) =>
          s.name_en.toLowerCase().includes(q) ||
          s.name_fa.toLowerCase().includes(q) ||
          s.author.toLowerCase().includes(q) ||
          s.subscales.some((sub) => sub.toLowerCase().includes(q))
      );
    }

    return result;
  }, [scales, selectedCategory, searchQuery]);

  return (
    <section className="space-y-4">
      {/* Search & Filter Bar */}
      <div className="flex flex-col md:flex-row gap-3 justify-between items-stretch md:items-center p-3 rounded-xl glass-panel bg-slate-900/60 border border-slate-800">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t('search_scales')}
            className="w-full pl-10 pr-9 py-2 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs md:text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Category Chips */}
        <div className="flex gap-1.5 overflow-x-auto pb-1 md:pb-0">
          {categories.map((cat) => {
            const isActive = selectedCategory === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => {
                  haptic('light');
                  setSelectedCategory(cat.id);
                }}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold cursor-pointer whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-cyan-600 text-white shadow-md shadow-cyan-600/30'
                    : 'bg-slate-800/70 text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                }`}
              >
                {lang === 'fa' ? cat.label_fa : cat.label_en}
              </button>
            );
          })}
        </div>
      </div>

      {/* Scales Cards Grid */}
      {filteredScales.length === 0 ? (
        <div className="text-center p-12 glass-panel bg-slate-900/40 rounded-2xl border border-slate-800 text-slate-400 text-sm">
          {t('no_scales_found')}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredScales.map((scale, idx) => (
            <ScaleCard
              key={idx}
              scale={scale}
              onSelect={onScaleSelect}
            />
          ))}
        </div>
      )}
    </section>
  );
};
