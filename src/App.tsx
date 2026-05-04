import React from 'react';
import { useApp } from '@/contexts/AppContext';
import { LandingPage } from '@/pages/LandingPage';
import { BackgroundStep } from '@/pages/BackgroundStep';
import { PreferencesStep } from '@/pages/PreferencesStep';
import { Dashboard } from '@/pages/Dashboard';

export function App() {
  const { currentPage } = useApp();

  switch (currentPage) {
    case 'landing':
      return <LandingPage />;
    case 'step1':
      return <BackgroundStep />;
    case 'step2':
      return <PreferencesStep />;
    case 'dashboard':
      return <Dashboard />;
    default:
      return <LandingPage />;
  }
}
