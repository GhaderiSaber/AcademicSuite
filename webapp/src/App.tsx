import React, { useState, useEffect } from 'react';
import { TabType, Project, Scale } from './types';
import { SEED_PROJECTS, SEED_SCALES } from './data/seedData';
import { Header } from './components/Header';
import { TabNavigation } from './components/TabNavigation';
import { KanbanBoard } from './components/kanban/KanbanBoard';
import { PricingCalculator } from './components/calculator/PricingCalculator';
import { ScalesExplorer } from './components/scales/ScalesExplorer';
import { ConsultantProfile } from './components/profile/ConsultantProfile';
import { Toast } from './components/Toast';
import { useLanguage } from './hooks/useLanguage';

export const App: React.FC = () => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState<TabType>('kanban');
  const [projects, setProjects] = useState<Project[]>(SEED_PROJECTS);
  const [scales] = useState<Scale[]>(SEED_SCALES);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [scalesCountInCalc, setScalesCountInCalc] = useState<number>(2);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 3000);
  };

  // Attempt live API fetch for projects
  useEffect(() => {
    fetch('/api/projects')
      .then((res) => {
        if (!res.ok) throw new Error('API unavailable');
        return res.json();
      })
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          setProjects(data);
        }
      })
      .catch(() => {
        // Quietly fallback to seed data
      });
  }, []);

  const handleScaleSelectForCalc = (scale: Scale) => {
    setScalesCountInCalc((prev) => Math.min(prev + 1, 8));
    setActiveTab('calculator');
    showToast(`${scale.name_en}: ${t('scale_selected_toast')}`);
  };

  const handleProjectSelect = (project: Project) => {
    showToast(`${project.client_name}: ${project.topic}`);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-4 md:py-6 flex flex-col min-h-screen">
      {/* Top Header */}
      <Header totalProjects={projects.length} />

      {/* Main Tab Navigation */}
      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Active Tab Panel */}
      <main className="flex-1">
        {activeTab === 'kanban' && (
          <KanbanBoard
            projects={projects}
            onProjectSelect={handleProjectSelect}
          />
        )}

        {activeTab === 'calculator' && (
          <PricingCalculator
            onShowToast={showToast}
            initialScalesCount={scalesCountInCalc}
          />
        )}

        {activeTab === 'scales' && (
          <ScalesExplorer
            scales={scales}
            onScaleSelect={handleScaleSelectForCalc}
          />
        )}

        {activeTab === 'consultant' && <ConsultantProfile />}
      </main>

      {/* Footer */}
      <footer className="mt-12 py-4 border-t border-slate-800 text-center text-xs text-slate-500 flex flex-col sm:flex-row justify-between items-center gap-2">
        <span>Saber Academic Suite &copy; 2026. All rights reserved.</span>
        <span className="font-mono text-[11px]">v2.0 • React 19 + TypeScript + Tailwind v4</span>
      </footer>

      {/* Popover Toast Alert */}
      <Toast message={toastMessage} />
    </div>
  );
};

export default App;
