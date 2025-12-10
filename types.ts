export enum AppRoute {
  DASHBOARD = 'dashboard',
  CAREER_COUNSELLOR = 'career_counsellor',
  TEXT_SUMMARIZER = 'text_summarizer',
  STOCK_PREDICTOR = 'stock_predictor',
  RESUME_OPTIMIZER = 'resume_optimizer'
}

export interface Message {
  id: string;
  role: 'user' | 'model';
  text: string;
  timestamp: Date;
}

export interface StockDataPoint {
  date: string;
  actual: number;
  predicted: number;
}

export interface SummaryResult {
  originalText: string;
  summary: string;
  wordCount: number;
  reductionPercentage: number;
}

export interface DesignConfig {
  layout: 'modern' | 'classic' | 'creative' | 'minimalist' | 'technical';
  colorAccent: string;
  fontPairing: 'serif' | 'sans' | 'mono';
}

export interface OptimizationResult {
  selectedResumeType: 'Software' | 'Core';
  designConfig: DesignConfig;
  content: {
    fullName: string;
    title: string;
    contactInfo: string;
    summary: string;
    skills: string[];
    experience: {
      role: string;
      company: string;
      duration: string;
      points: string[];
    }[];
    projects: {
      name: string;
      techStack: string;
      description: string;
    }[];
    education: {
      degree: string;
      institution: string;
      year: string;
    }[];
    // Dynamic sections that might appear based on content
    certifications?: string[];
    languages?: string[];
    achievements?: string[];
    extracurricular?: string[];
  };
}