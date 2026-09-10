import React from 'react';
import { TabType } from '../types';
import { useLanguage } from '../hooks/useLanguage';
import { useTelegram } from '../hooks/useTelegram';
import { LayoutDashboard, Calculator, BookOpen, UserCheck } from 'lucide-react';

interface TabNavigationProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

export const TabNavigation: React.FC<TabNavigationProps> = ({ activeTab, onTabChange }) => {
  const { t } = useLanguage();
  const { haptic } = useTelegram();

  const tabs: { id: TabType; labelKey: any; icon: React.ReactNode }[] = [
    { id: 'kanban', labelKey: 'tab_kanban', icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: 'calculator', labelKey: 'tab_calculator', icon: <Calculator className="w-4 h-4" /> },
    { id: 'scales', labelKey: 'tab_scales', icon: <BookOpen className="w-4 h-4" /> },
    { id: 'consultant', labelKey: 'tab_consultant', icon: <UserCheck className="w-4 h-4" /> },
  ];

  const handleSelect = (tab: TabType) => {
    haptic('light');
    onTabChange(tab);
  };

  return (
    <nav className="flex gap-2 p-1.5 mb-6 glass-panel bg-slate-900/60 border border-slate-800 rounded-xl overflow-x-auto">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => handleSelect(tab.id)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs md:text-sm font-semibold transition-all whitespace-nowrap cursor-pointer flex-1 justify-center ${
              isActive
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            {tab.icon}
            <span>{t(tab.labelKey)}</span>
          </button>
        );
      })}
    </nav>
  );
};
