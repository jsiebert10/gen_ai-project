import React from 'react';
import { useApp } from '@/contexts/AppContext';
import { LandingPage } from '@/pages/LandingPage';
import { BackgroundStep } from '@/pages/BackgroundStep';
import { GoalsStep } from '@/pages/GoalsStep';
import { InterestsStep } from '@/pages/InterestsStep';
import { Dashboard } from '@/pages/Dashboard';

export function App() {
  const { currentPage } = useApp();

  switch (currentPage) {
    case 'landing':
      return <LandingPage />;
    case 'step1':
      return <BackgroundStep />;
    case 'step2':
      return <GoalsStep />;
    case 'step3':
      return <InterestsStep />;
    case 'dashboard':
      return <Dashboard />;
    default:
      return <LandingPage />;
  }
}
