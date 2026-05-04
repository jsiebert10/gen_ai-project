import React from 'react';
import { useApp } from '@/contexts/AppContext';
import { PathwayAILogo } from '@/components/ui/PathwayAILogo';

export type DashboardTab = 'overview' | 'programs' | 'visa' | 'career' | 'test_prep';

interface DashboardSidebarProps {
  activeTab: DashboardTab;
  onTabChange: (tab: DashboardTab) => void;
}

const navItems: { id: DashboardTab; label: string; icon: React.ReactNode }[] = [
  {
    id: 'overview',
    label: 'Overview',
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <rect x="1" y="1" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5" />
        <rect x="9" y="1" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5" />
        <rect x="1" y="9" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5" />
        <rect x="9" y="9" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5" />
      </svg>
    ),
  },
  {
    id: 'programs',
    label: 'Programs',
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path d="M8 2L1 6l7 4 7-4-7-4zM1 10l7 4 7-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    id: 'visa',
    label: 'Visa',
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.5" />
        <path d="M1.5 8h13M8 1.5C6.5 3.5 5.5 5.5 5.5 8s1 4.5 2.5 6.5M8 1.5C9.5 3.5 10.5 5.5 10.5 8s-1 4.5-2.5 6.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    id: 'career',
    label: 'Career',
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path d="M1 12l4-4 3 3 4-5 3 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    id: 'test_prep',
    label: 'Test Prep',
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path d="M3 2h10a1 1 0 011 1v10a1 1 0 01-1 1H3a1 1 0 01-1-1V3a1 1 0 011-1z" stroke="currentColor" strokeWidth="1.5" />
        <path d="M5 6h6M5 9h4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    ),
  },
];

export function DashboardSidebar({ activeTab, onTabChange }: DashboardSidebarProps) {
  const { navigateTo } = useApp();

  return (
    <aside className="flex w-60 flex-col border-r border-gray-100 bg-white px-4 py-6">
      <div className="mb-8 px-2">
        <PathwayAILogo />
      </div>

      <nav className="flex flex-col gap-1">
        {navItems.map((item) => {
          const active = item.id === activeTab;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all focus:outline-none ${
                active ? 'bg-gray-900 text-white' : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              {item.icon}
              {item.label}
            </button>
          );
        })}
      </nav>

      <div className="mt-auto">
        <button
          onClick={() => navigateTo('landing')}
          className="flex items-center gap-2 px-3 py-2 text-sm text-gray-400 hover:text-gray-700 transition-colors focus:outline-none"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M10 12l-4-4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M6 8h8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
          Back to Home
        </button>
      </div>
    </aside>
  );
}
