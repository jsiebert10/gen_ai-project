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
      'Civil Engineering',
      'Chemical Engineering',
      'Biomedical Engineering',
      'Aerospace Engineering',
      'Environmental Engineering',
      'Industrial Engineering',
    ],
  },
  {
    category: 'Medicine & Health',
    options: [
      'Medicine (MD/Clinical)',
      'Public Health',
      'Epidemiology',
      'Biostatistics',
      'Health Informatics',
      'Clinical Research',
      'Nursing',
      'Pharmacy',
      'Neuroscience',
      'Health Administration',
      'Nutrition Science',
      'Genetic Counseling',
    ],
  },
  {
    category: 'Business & Finance',
    options: [
      'Business Analytics',
      'Finance',
      'Quantitative Finance',
      'Marketing',
      'Accounting',
      'Supply Chain Management',
      'Entrepreneurship',
      'Management',
      'International Business',
      'Real Estate',
    ],
  },
  {
    category: 'Sciences',
    options: [
      'Biology',
      'Chemistry',
      'Physics',
      'Mathematics',
      'Statistics',
      'Environmental Science',
      'Biotechnology',
      'Microbiology',
      'Biochemistry',
    ],
  },
  {
    category: 'Arts & Humanities',
    options: [
      'Fine Arts',
      'Graphic Design',
      'Film Studies',
      'Music',
      'Creative Writing',
      'Journalism',
      'Linguistics',
      'Philosophy',
      'History',
      'Architecture',
      'Interior Design',
    ],
  },
  {
    category: 'Social Sciences & Law',
    options: [
      'Psychology',
      'Sociology',
      'Political Science',
      'Economics',
      'International Relations',
      'Education',
      'Social Work',
      'Urban Planning',
      'Public Policy',
      'Communication Studies',
      'Law (LLM)',
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
