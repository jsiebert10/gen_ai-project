export type Page = 'landing' | 'step1' | 'step2' | 'step3' | 'dashboard';

export interface UserProfile {
  fullName: string;
  undergraduateMajor: string;
  gpa: number;
  dreamCareer: string;
  targetCountries: string[];
  annualBudget: number;
  areasOfInterest: string[];
}

export const INITIAL_PROFILE: UserProfile = {
  fullName: '',
  undergraduateMajor: '',
  gpa: 3.5,
  dreamCareer: '',
  targetCountries: [],
  annualBudget: 30000,
  areasOfInterest: [],
};

export const COUNTRY_OPTIONS = ['USA', 'Canada', 'UK', 'Germany', 'Australia', 'Netherlands', 'Singapore'];

export const INTEREST_OPTIONS = [
  'AI/ML', 'Data Science', 'Software Engineering', 'Product Management',
  'Finance', 'Consulting', 'UX Research', 'Cybersecurity',
];

// ── Dashboard response types (match backend formatters.py output) ──────────

export interface DashboardStats {
  programs_matched: number;
  strong_matches: number;
  course_plan_semesters: number;
  visa_steps_total: number;
  visa_steps_completed: number;
  career_employment_rate: number;
}

export interface ProgramMatch {
  university: string;
  program: string;
  country: string;
  tuition_usd: number;
  match_score: number;
  reason: string;
}

export interface VisaData {
  visa_type: string;
  destination_country: string;
  required_documents: string[];
  processing_time: string;
  application_fee_usd: number;
  tips: string[];
  warning: string;
}

export interface CareerData {
  field: string;
  country: string;
  job_market_outlook: string;
  average_salary_usd: number;
  top_roles: string[];
  top_companies: string[];
  sponsorship_likelihood: string;
  in_demand_skills: string[];
  timeline_to_employment: string;
  insight: string;
}

export interface GapItem {
  exam: string;
  current_score: number | null;
  target_score: number;
  gap: number;
  status: string;
}

export interface CriticalPathItem {
  priority: number;
  exam: string;
  weeks_needed: number;
  reason: string;
}

export interface ExamResources {
  exam: string;
  recommendations: { name: string; url: string; type: string; best_for: string }[];
}

export interface TestPrepData {
  target_programs: { university: string; program: string; requirements: Record<string, unknown> }[];
  gap_analysis: GapItem[];
  critical_path: CriticalPathItem[];
  resources: ExamResources[];
  urgency_flag: boolean;
  summary: string;
}

export interface DashboardData {
  overview: {
    stats: DashboardStats;
    activity: { label: string; time: string }[];
  };
  programs: {
    query_summary: string;
    items: ProgramMatch[];
  };
  visa: VisaData;
  career: CareerData;
  test_prep: TestPrepData;
}
