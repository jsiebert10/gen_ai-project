import React, { useState } from 'react';
import { useApp } from '@/contexts/AppContext';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { StatCard } from '@/components/ui/StatCard';
import { HelpButton } from '@/components/ui/HelpButton';

type DashboardTab = 'overview' | 'programs' | 'visa' | 'career';

const recentActivity = [
  { label: 'Profile completed', time: 'Just now' },
  { label: '12 programs matched', time: '1 min ago' },
  { label: 'Visa checklist generated', time: '2 min ago' },
  { label: 'Career report ready', time: '3 min ago' },
];

const statCards = [
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M9 2L2 6.5v4C2 14 5.134 17.165 9 18c3.866-.835 7-4 7-7.5v-4L9 2z"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        />
        <path
          d="M6 9l2 2 4-4"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
    value: '12',
    label: 'Recommended Programs',
    subtext: '3 strong matches',
  },
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="14" height="14" rx="2" stroke="currentColor" strokeWidth="1.5" />
        <path d="M2 7h14M7 2v14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    ),
    value: '4 semesters',
    label: 'Course Strategy',
    subtext: 'Optimized plan ready',
  },
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="9" cy="9" r="7" stroke="currentColor" strokeWidth="1.5" />
        <path
          d="M2 9h14M9 2C7 4.5 6 6.5 6 9s1 4.5 3 7M9 2c2 2.5 3 4.5 3 7s-1 4.5-3 7"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
      </svg>
    ),
    value: '6 steps',
    label: 'Visa Roadmap',
    subtext: '2 completed',
  },
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M2 14l4-5 3 3 4-6 3 2.5"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
    value: '85%',
    label: 'Career Outlook',
    subtext: 'Employment rate',
  },
];

function getInitials(name: string): string {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join('');
}

function OverviewPanel() {
  return (
    <div className="flex flex-col gap-6">
      {/* Stat cards */}
      <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
        {statCards.map((card) => (
          <StatCard key={card.label} {...card} />
        ))}
      </div>

      {/* Recent Activity */}
      <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-base font-semibold text-gray-900">Recent Activity</h2>
        <div className="flex flex-col divide-y divide-gray-50">
          {recentActivity.map((item) => (
            <div key={item.label} className="flex items-center justify-between py-3.5">
              <div className="flex items-center gap-3">
                <span className="h-1.5 w-1.5 rounded-full bg-gray-400" />
                <span className="text-sm text-gray-700">{item.label}</span>
              </div>
              <span className="text-sm text-gray-400">{item.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function PlaceholderPanel({ title }: { title: string }) {
  return (
    <div className="flex h-64 items-center justify-center rounded-2xl border border-dashed border-gray-200 bg-white text-sm text-gray-400">
      {title} panel — content coming soon
    </div>
  );
}

export function Dashboard() {
  const { profile } = useApp();
  const [activeTab, setActiveTab] = useState<DashboardTab>('overview');
  const initials = getInitials(profile.fullName || 'User');

  const panels: Record<DashboardTab, React.ReactNode> = {
    overview: <OverviewPanel />,
    programs: <PlaceholderPanel title="Programs" />,
    visa: <PlaceholderPanel title="Visa" />,
    career: <PlaceholderPanel title="Career" />,
  };

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <DashboardSidebar activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="flex flex-1 flex-col overflow-auto">
        {/* Top bar */}
        <header className="flex items-center justify-between border-b border-gray-100 bg-white px-8 py-4">
          <h1 className="text-xl font-semibold text-gray-900">Dashboard</h1>
          <div
            className="flex h-9 w-9 items-center justify-center rounded-full bg-gray-200 text-sm font-semibold text-gray-600"
            title={profile.fullName}
          >
            {initials}
          </div>
        </header>

        <main className="flex-1 p-8">{panels[activeTab]}</main>
      </div>

      <HelpButton />
    </div>
  );
}
