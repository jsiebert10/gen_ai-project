import React from 'react';
import { useApp } from '@/contexts/AppContext';
import { OnboardingHeader } from '@/components/layout/OnboardingHeader';
import { TagSelector } from '@/components/ui/TagSelector';
import { Button } from '@/components/ui/Button';
import { HelpButton } from '@/components/ui/HelpButton';
import { INTEREST_OPTIONS } from '@/types';

export function InterestsStep() {
  const { profile, updateProfile, navigateTo } = useApp();

  const isValid = profile.areasOfInterest.length > 0;

  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      <OnboardingHeader currentStep={3} />

      <main className="flex flex-1 flex-col items-center px-6 py-12">
        <div className="w-full max-w-xl">
          <p className="mb-1 text-sm text-gray-400">Step 3 of 3</p>
          <h1 className="mb-8 text-3xl font-semibold text-gray-900">Interests</h1>

          <div className="rounded-2xl border border-gray-100 bg-white p-8 shadow-sm">
            <TagSelector
              label="Areas of Interest"
              options={INTEREST_OPTIONS}
              selected={profile.areasOfInterest}
              onChange={(v) => updateProfile({ areasOfInterest: v })}
            />
          </div>
        </div>
      </main>

      <nav className="flex items-center justify-between border-t border-gray-100 bg-white px-8 py-5">
        <Button variant="ghost" onClick={() => navigateTo('step2')}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 4L6 8l4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Back
        </Button>
        <Button onClick={() => navigateTo('dashboard')} disabled={!isValid}>
          View Dashboard
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </Button>
      </nav>

      <HelpButton />
    </div>
  );
}
