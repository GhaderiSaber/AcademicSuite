import React from 'react';
import { useLanguage } from '../hooks/useLanguage';
import { GraduationCap, Globe } from 'lucide-react';

interface HeaderProps {
  totalProjects: number;
}

export const Header: React.FC<HeaderProps> = ({ totalProjects }) => {
  const { lang, toggleLanguage, t, formatNumber } = useLanguage();

  return (
    <header className="flex flex-col md:flex-row justify-between items-center gap-4 p-4 mb-4 glass-panel bg-slate-900/70 border border-slate-700/40 rounded-2xl shadow-xl backdrop-blur-xl">
      <div className="flex items-center gap-3.5 w-full md:w-auto">
        <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/25 shrink-0 text-white">
          <GraduationCap className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-lg md:text-xl font-bold bg-gradient-to-r from-white via-indigo-100 to-indigo-300 bg-clip-text text-transparent">
            {t('app_title')}
          </h1>
          <p className="text-xs text-slate-400 font-medium">
            {t('app_subtitle')}
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3 w-full md:w-auto justify-between md:justify-end">
        {/* Google Drive Status Ribbon */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/80 border border-slate-700/50 text-xs text-slate-300">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="font-semibold text-emerald-400">Drive:</span>
          <span>My Work</span>
          <span className="bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded-full font-bold ml-1">
            {formatNumber(totalProjects)}
          </span>
        </div>

        {/* Language Switcher */}
        <button
          onClick={toggleLanguage}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 hover:bg-white/15 border border-white/10 transition-all text-xs font-semibold cursor-pointer active:scale-95"
          title="Switch Language / تغییر زبان"
        >
          <Globe className="w-3.5 h-3.5 text-indigo-400" />
          <span>{lang === 'fa' ? 'English' : 'فارسی'}</span>
          <span className="text-sm">{lang === 'fa' ? '🇬🇧' : '🇮🇷'}</span>
        </button>
      </div>
    </header>
  );
};
