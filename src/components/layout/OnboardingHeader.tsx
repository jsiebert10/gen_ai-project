import React from 'react';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { PathwayAILogo } from '@/components/ui/PathwayAILogo';

interface OnboardingHeaderProps {
  currentStep: number;
  totalSteps?: number;
}

export function OnboardingHeader({ currentStep, totalSteps = 3 }: OnboardingHeaderProps) {
  return (
    <header className="flex items-center justify-between border-b border-gray-100 bg-white px-8 py-4">
      <PathwayAILogo />
      <ProgressBar totalSteps={totalSteps} currentStep={currentStep} />
    </header>
  );
}
