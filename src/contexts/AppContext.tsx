import React, { createContext, useContext, useState } from 'react';
import { Page, UserProfile, INITIAL_PROFILE, DashboardData } from '@/types';

interface AppContextValue {
  currentPage: Page;
  profile: UserProfile;
  dashboardData: DashboardData | null;
  navigateTo: (page: Page) => void;
  updateProfile: (updates: Partial<UserProfile>) => void;
  setDashboardData: (data: DashboardData) => void;
}

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [currentPage, setCurrentPage] = useState<Page>('landing');
  const [profile, setProfile] = useState<UserProfile>(INITIAL_PROFILE);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);

  const navigateTo = (page: Page) => setCurrentPage(page);
  const updateProfile = (updates: Partial<UserProfile>) =>
    setProfile((prev) => ({ ...prev, ...updates }));

  return (
    <AppContext.Provider value={{ currentPage, profile, dashboardData, navigateTo, updateProfile, setDashboardData }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used inside AppProvider');
  return ctx;
}
