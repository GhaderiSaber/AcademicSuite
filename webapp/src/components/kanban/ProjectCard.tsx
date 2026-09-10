import React from 'react';
import { Project } from '../../types';
import { useLanguage } from '../../hooks/useLanguage';
import { Folder, FileText, MessageSquare, ExternalLink } from 'lucide-react';

interface ProjectCardProps {
  project: Project;
  onSelect: (project: Project) => void;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({ project, onSelect }) => {
  const { formatNumber } = useLanguage();

  const cleanPath = project.folder_path
    ? project.folder_path.replace(/^\/.*?Google Drive\//i, '')
    : 'My Work';

  const statusBorderColors: Record<string, string> = {
    inquiry: 'border-l-4 border-l-amber-400',
    pending: 'border-l-4 border-l-orange-400',
    in_progress: 'border-l-4 border-l-indigo-400',
    finished: 'border-l-4 border-l-emerald-400',
  };

  const isClientTg = project.client_name.startsWith('Client_');
  const tgId = isClientTg ? project.client_name.replace('Client_', '') : null;

  return (
    <div
      onClick={() => onSelect(project)}
      className={`group p-3.5 rounded-xl bg-slate-900/65 hover:bg-slate-800/80 border border-slate-700/40 hover:border-indigo-500/40 transition-all duration-200 shadow-md hover:shadow-xl hover:-translate-y-0.5 cursor-pointer backdrop-blur-md ${
        statusBorderColors[project.status] || 'border-l-4 border-l-indigo-400'
      }`}
    >
      <div className="flex justify-between items-center mb-1.5">
        <div className="flex items-center gap-1.5">
          {isClientTg ? (
            <a
              href={`tg://user?id=${tgId}`}
              onClick={(e) => e.stopPropagation()}
              className="text-xs font-bold text-sky-400 hover:text-sky-300 flex items-center gap-1 transition-colors"
              title="Message in Telegram"
            >
              <span>{project.client_name}</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          ) : (
            <span className="text-xs font-bold text-slate-100 group-hover:text-indigo-200 transition-colors">
              {project.client_name}
            </span>
          )}
        </div>
        <span className="text-[10px] font-mono text-slate-500">{project.id}</span>
      </div>

      <p className="text-xs text-slate-300 line-clamp-2 mb-2.5 leading-relaxed">
        {project.topic || 'Academic Research & Statistical Analysis'}
      </p>

      <div className="flex flex-wrap gap-1.5 mb-3">
        <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-indigo-500/15 text-indigo-300 border border-indigo-500/20">
          {project.degree}
        </span>
        <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-300 border border-slate-700/60">
          {project.design}
        </span>
        <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-300 border border-slate-700/60">
          N={formatNumber(project.sample_size || 40)}
        </span>
      </div>

      <div className="flex justify-between items-center pt-2 border-t border-slate-800/80 text-[11px] text-slate-400">
        <div className="flex items-center gap-1 max-w-[150px] truncate font-mono text-slate-400" title={cleanPath}>
          <Folder className="w-3 h-3 text-slate-500 shrink-0" />
          <span className="truncate">{cleanPath}</span>
        </div>

        <div className="flex items-center gap-2">
          {project.file_count > 0 && (
            <span className="flex items-center gap-0.5 text-slate-400">
              <FileText className="w-3 h-3" />
              {formatNumber(project.file_count)}
            </span>
          )}
          {project.message_count > 0 && (
            <span className="flex items-center gap-0.5 text-slate-400">
              <MessageSquare className="w-3 h-3" />
              {formatNumber(project.message_count)}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
