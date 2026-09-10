import React, { useState, useMemo } from 'react';
import { Project, ProjectStatus } from '../../types';
import { ProjectCard } from './ProjectCard';
import { useLanguage } from '../../hooks/useLanguage';
import { useTelegram } from '../../hooks/useTelegram';
import { Search, X, Clock, HelpCircle, Activity, CheckCircle } from 'lucide-react';

interface KanbanBoardProps {
  projects: Project[];
  onProjectSelect: (project: Project) => void;
}

export const KanbanBoard: React.FC<KanbanBoardProps> = ({ projects, onProjectSelect }) => {
  const { t, formatNumber } = useLanguage();
  const { haptic } = useTelegram();

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | ProjectStatus>('all');

  const filteredProjects = useMemo(() => {
    let result = projects;

    if (statusFilter !== 'all') {
      result = result.filter((p) => p.status === statusFilter);
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      result = result.filter(
        (p) =>
          p.client_name.toLowerCase().includes(q) ||
          p.topic.toLowerCase().includes(q) ||
          p.folder_path.toLowerCase().includes(q) ||
          p.id.toLowerCase().includes(q)
      );
    }

    return result;
  }, [projects, statusFilter, searchQuery]);

  const columns: {
    id: ProjectStatus;
    titleKey: any;
    color: string;
    badgeBg: string;
    icon: React.ReactNode;
  }[] = [
    {
      id: 'inquiry',
      titleKey: 'col_inquiry',
      color: 'text-amber-400',
      badgeBg: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
      icon: <HelpCircle className="w-4 h-4 text-amber-400" />,
    },
    {
      id: 'pending',
      titleKey: 'col_pending',
      color: 'text-orange-400',
      badgeBg: 'bg-orange-500/15 text-orange-300 border-orange-500/30',
      icon: <Clock className="w-4 h-4 text-orange-400" />,
    },
    {
      id: 'in_progress',
      titleKey: 'col_in_progress',
      color: 'text-sky-400',
      badgeBg: 'bg-sky-500/15 text-sky-300 border-sky-500/30',
      icon: <Activity className="w-4 h-4 text-sky-400" />,
    },
    {
      id: 'finished',
      titleKey: 'col_finished',
      color: 'text-emerald-400',
      badgeBg: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
      icon: <CheckCircle className="w-4 h-4 text-emerald-400" />,
    },
  ];

  const handleFilterClick = (filter: 'all' | ProjectStatus) => {
    haptic('light');
    setStatusFilter(filter);
  };

  return (
    <section className="space-y-4">
      {/* Controls Bar */}
      <div className="flex flex-col md:flex-row gap-3 justify-between items-stretch md:items-center p-3 rounded-xl glass-panel bg-slate-900/60 border border-slate-800">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t('search_projects')}
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

        {/* Filter Chips */}
        <div className="flex gap-1.5 overflow-x-auto pb-1 md:pb-0">
          <button
            onClick={() => handleFilterClick('all')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold cursor-pointer whitespace-nowrap transition-all ${
              statusFilter === 'all'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'bg-slate-800/70 text-slate-400 hover:bg-slate-800 hover:text-slate-200'
            }`}
          >
            {t('filter_all')} ({formatNumber(projects.length)})
          </button>
          {columns.map((col) => (
            <button
              key={col.id}
              onClick={() => handleFilterClick(col.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold cursor-pointer whitespace-nowrap transition-all ${
                statusFilter === col.id
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'bg-slate-800/70 text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              {t(`status_${col.id}` as any)}
            </button>
          ))}
        </div>
      </div>

      {/* Kanban Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {columns.map((col) => {
          const colProjects = filteredProjects.filter((p) => p.status === col.id);

          return (
            <div
              key={col.id}
              className="flex flex-col rounded-2xl glass-panel bg-slate-900/50 border border-slate-800/80 p-3 min-h-[450px]"
            >
              {/* Column Header */}
              <div className="flex justify-between items-center mb-3 pb-2.5 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  {col.icon}
                  <h3 className="text-xs md:text-sm font-bold text-slate-200">
                    {t(col.titleKey)}
                  </h3>
                </div>
                <span
                  className={`px-2 py-0.5 rounded-full text-xs font-bold border ${col.badgeBg}`}
                >
                  {formatNumber(colProjects.length)}
                </span>
              </div>

              {/* Cards Container */}
              <div className="flex flex-col gap-2.5 flex-1 overflow-y-auto max-h-[600px] pr-1">
                {colProjects.length === 0 ? (
                  <div className="flex-1 flex items-center justify-center text-center p-6 text-xs text-slate-500">
                    No projects in this stage.
                  </div>
                ) : (
                  colProjects.map((proj) => (
                    <ProjectCard
                      key={proj.id}
                      project={proj}
                      onSelect={onProjectSelect}
                    />
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
