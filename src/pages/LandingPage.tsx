import React from 'react';
import { useApp } from '@/contexts/AppContext';
import { Button } from '@/components/ui/Button';

const features = [
  {
    icon: (
      <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M11 2L3 7v5c0 4.418 3.358 8.165 8 9 4.642-.835 8-4.582 8-9V7l-8-5z"
          stroke="#9CA3AF"
          strokeWidth="1.5"
          strokeLinejoin="round"
        />
        <path
          d="M8 11l2 2 4-4"
          stroke="#9CA3AF"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
    title: 'Smart Matching',
    description: 'AI-matched U.S. master\'s programs based on your profile, interests, and goals.',
  },
  {
    icon: (
      <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="11" cy="11" r="9" stroke="#9CA3AF" strokeWidth="1.5" />
        <path
          d="M2 11h18M11 2C9 4.5 8 7.5 8 11s1 6.5 3 9M11 2c2 2.5 3 5.5 3 9s-1 6.5-3 9"
          stroke="#9CA3AF"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
      </svg>
    ),
    title: 'Visa Guidance',
    description: 'Step-by-step F-1 student visa roadmap tailored to studying in the USA.',
  },
  {
    icon: (
      <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M2 16l5-6 4 4 5-7 4 3"
          stroke="#9CA3AF"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
    title: 'Career Insights',
    description: 'Understand U.S. job markets, OPT/STEM OPT options, and salary expectations.',
  },
];

export function LandingPage() {
  const { navigateTo } = useApp();

  return (
    <div className="flex min-h-screen flex-col bg-white">
      {/* Hero */}
      <main className="flex flex-1 flex-col items-center justify-center px-6 py-20 text-center">
        {/* Badge */}
        <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-gray-200 bg-white px-4 py-2 text-sm text-gray-500 shadow-sm">
          <svg
            width="14"
            height="14"
            viewBox="0 0 14 14"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M7 1v2M7 11v2M1 7h2M11 7h2M2.929 2.929l1.414 1.414M9.657 9.657l1.414 1.414M11.071 2.929l-1.414 1.414M4.343 9.657l-1.414 1.414"
              stroke="currentColor"
              strokeWidth="1.25"
              strokeLinecap="round"
            />
          </svg>
          AI-powered education planning
        </div>

        {/* Headline */}
        <h1 className="mb-5 max-w-2xl text-5xl font-bold leading-tight tracking-tight text-gray-900">
          Plan your U.S. master's journey
          <br />
          with confidence
        </h1>

        {/* Subheadline */}
        <p className="mb-10 max-w-xl text-lg leading-relaxed text-gray-500">
          AIPathFinder helps international students discover the right U.S. master's programs,
          navigate the F-1 visa process, and build a clear career path — all in one place.
        </p>

        {/* CTA */}
        <Button onClick={() => navigateTo('step1')} className="px-8 py-4 text-base">
          Start Planning
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </Button>
      </main>

      {/* Feature Cards */}
      <section className="mx-auto mb-16 grid w-full max-w-5xl grid-cols-1 gap-4 px-6 sm:grid-cols-3">
        {features.map((f) => (
          <div
            key={f.title}
            className="flex flex-col gap-3 rounded-2xl border border-gray-100 bg-gray-50 p-6"
          >
            <div>{f.icon}</div>
            <h3 className="font-semibold text-gray-900">{f.title}</h3>
            <p className="text-sm leading-relaxed text-gray-400">{f.description}</p>
          </div>
        ))}
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 py-5 text-center text-sm text-gray-400">
        © 2026 AIPathFinder · Built for international students
      </footer>
    </div>
  );
}
