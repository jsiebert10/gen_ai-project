export type Page = 'landing' | 'step1' | 'step2' | 'step3' | 'dashboard';

export interface UserProfile {
  // Step 1 — Background
  fullName: string;
  undergraduateMajor: string;
  gpa: number;

  // Step 2 — Goals & Preferences
  dreamCareer: string;
  targetCountries: string[];
  annualBudget: number;

  // Step 3 — Interests
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
  'AI/ML',
  'Data Science',
  'Software Engineering',
  'Product Management',
  'Finance',
  'Consulting',
  'UX Research',
  'Cybersecurity',
];
