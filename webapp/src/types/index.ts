export type Language = 'en' | 'fa';

export type TabType = 'kanban' | 'calculator' | 'scales' | 'consultant';

export type ProjectStatus = 'inquiry' | 'pending' | 'in_progress' | 'finished';

export interface Project {
  id: string;
  client_name: string;
  status: ProjectStatus;
  file_count: number;
  message_count: number;
  folder_path: string;
  topic: string;
  degree: string;
  design: string;
  sample_size: number;
}

export interface Scale {
  name_en: string;
  name_fa: string;
  items_count: number;
  rating_scale: string;
  subscales: string[];
  category: string;
  author: string;
}

export type DegreeLevel = 'master' | 'phd';

export type ResearchDesign =
  | 'ancova'
  | 'sem'
  | 'regression'
  | 'scale_val'
  | 'qualitative';

export interface ServiceItem {
  id: 'ch3' | 'sim' | 'ch4' | 'ch5' | 'slides' | 'audit';
  name_en: string;
  name_fa: string;
  meta_en: string;
  meta_fa: string;
  price: number;
  days: number;
  selected: boolean;
}

export interface QuotationResult {
  total: number;
  subtotal: number;
  workingDays: number;
  hasDiscount: boolean;
  isUrgent: boolean;
  degree: DegreeLevel;
  design: ResearchDesign;
  sampleSize: number;
  scalesCount: number;
  services: { name: string; price: number }[];
}
