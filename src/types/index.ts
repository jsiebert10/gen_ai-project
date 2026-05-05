export type Page = 'landing' | 'step1' | 'step2' | 'dashboard';

export interface UserProfile {
  fullName: string;
  undergraduateMajor: string;
  gpa: number;
  annualBudget: number;
  areasOfInterest: string[];
}

export const INITIAL_PROFILE: UserProfile = {
  fullName: '',
  undergraduateMajor: '',
  gpa: 3.5,
  annualBudget: 30000,
  areasOfInterest: [],
};

export interface InterestCategory {
  category: string;
  options: string[];
}

export const INTEREST_CATEGORIES: InterestCategory[] = [
  {
    category: 'Technology & Engineering',
    options: [
      'Artificial Intelligence',
      'Machine Learning',
      'Data Science',
      'Natural Language Processing',
      'Computer Vision',
      'Robotics',
      'Software Engineering',
      'Cybersecurity',
      'Cloud Computing',
      'Human-Computer Interaction',
      'Data Engineering',
      'Game Development',
      'Electrical Engineering',
      'Mechanical Engineering',
      'Civil & Structural Engineering',
      'Chemical Engineering',
      'Biomedical Engineering',
      'Aerospace Engineering',
      'Environmental Engineering',
      'Industrial & Systems Engineering',
    ],
  },
  {
    category: 'Medicine & Health',
    options: [
      'Public Health (MPH)',
      'Epidemiology',
      'Biostatistics',
      'Health Informatics',
      'Clinical Research & Trials',
      'Global Health',
      'Health Policy & Administration',
      'Translational Medicine',
      'Neuroscience',
      'Genetic Counseling',
      'Pharmaceutical Sciences',
      'Nutrition & Dietetics',
    ],
  },
  {
    category: 'Business & Finance',
    options: [
      'Business Analytics',
      'Finance',
      'Quantitative Finance',
      'Marketing Analytics',
      'Accounting',
      'Supply Chain & Operations',
      'Entrepreneurship & Innovation',
      'Management (MBA)',
      'International Business',
      'Real Estate Development',
    ],
  },
  {
    category: 'Sciences',
    options: [
      'Computational Biology',
      'Bioinformatics',
      'Biotechnology',
      'Microbiology & Immunology',
      'Biochemistry',
      'Materials Science',
      'Applied Mathematics',
      'Applied Statistics',
      'Environmental Science & Sustainability',
      'Atmospheric & Climate Science',
    ],
  },
  {
    category: 'Arts & Design',
    options: [
      'Graphic Design & Visual Communication',
      'Architecture (M.Arch)',
      'Urban Design',
      'Interior Architecture & Design',
      'Film & Media Studies',
      'Creative Writing (MFA)',
      'Music Composition & Technology',
      'Historic Preservation',
      'Museum Studies & Curatorial Practice',
      'Journalism & Digital Media',
    ],
  },
  {
    category: 'Social Sciences, Law & Policy',
    options: [
      'Clinical Psychology',
      'Industrial-Organizational Psychology',
      'International Affairs & Diplomacy',
      'Development Economics',
      'Educational Leadership',
      'Urban & Regional Planning',
      'Social Policy',
      'Public Policy & Administration',
      'Communication & Media Studies',
      'LLM / International Law',
      'Intellectual Property Law',
    ],
  },
];

export const INTEREST_OPTIONS: string[] = INTEREST_CATEGORIES.flatMap((c) => c.options);

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
