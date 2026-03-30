import React, { createContext, useContext, useState } from 'react';
import { Page, UserProfile, INITIAL_PROFILE } from '@/types';

interface AppContextValue {
  currentPage: Page;
  profile: UserProfile;
  navigateTo: (page: Page) => void;
  updateProfile: (updates: Partial<UserProfile>) => void;
}

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [currentPage, setCurrentPage] = useState<Page>('landing');
  const [profile, setProfile] = useState<UserProfile>(INITIAL_PROFILE);

  const navigateTo = (page: Page) => setCurrentPage(page);

  const updateProfile = (updates: Partial<UserProfile>) =>
    setProfile((prev) => ({ ...prev, ...updates }));

  return (
    <AppContext.Provider value={{ currentPage, profile, navigateTo, updateProfile }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used inside AppProvider');
  return ctx;
}
