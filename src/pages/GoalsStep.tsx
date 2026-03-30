import React from 'react';
import { useApp } from '@/contexts/AppContext';
import { OnboardingHeader } from '@/components/layout/OnboardingHeader';
import { Input } from '@/components/ui/Input';
import { RangeSlider } from '@/components/ui/RangeSlider';
import { TagSelector } from '@/components/ui/TagSelector';
import { Button } from '@/components/ui/Button';
import { HelpButton } from '@/components/ui/HelpButton';
import { COUNTRY_OPTIONS } from '@/types';

function formatBudget(v: number): string {
  if (v >= 1000) return `$${(v / 1000).toFixed(0)}k`;
  return `$${v}`;
}

export function GoalsStep() {
  const { profile, updateProfile, navigateTo } = useApp();

  const isValid =
    profile.dreamCareer.trim().length > 0 && profile.targetCountries.length > 0;

  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      <OnboardingHeader currentStep={2} />

      <main className="flex flex-1 flex-col items-center px-6 py-12">
        <div className="w-full max-w-xl">
          <p className="mb-1 text-sm text-gray-400">Step 2 of 3</p>
          <h1 className="mb-8 text-3xl font-semibold text-gray-900">Goals &amp; Preferences</h1>

          <div className="rounded-2xl border border-gray-100 bg-white p-8 shadow-sm">
            <div className="flex flex-col gap-6">
              <Input
                label="Dream Career"
                placeholder="e.g. Machine Learning Engineer"
                value={profile.dreamCareer}
                onChange={(e) => updateProfile({ dreamCareer: e.target.value })}
              />
              <TagSelector
                label="Target Countries"
                options={COUNTRY_OPTIONS}
                selected={profile.targetCountries}
                onChange={(v) => updateProfile({ targetCountries: v })}
              />
              <RangeSlider
                label="Annual Budget"
                value={profile.annualBudget}
                min={5000}
                max={80000}
                step={1000}
                formatValue={formatBudget}
                onChange={(v) => updateProfile({ annualBudget: v })}
              />
            </div>
          </div>
        </div>
      </main>

      <nav className="flex items-center justify-between border-t border-gray-100 bg-white px-8 py-5">
        <Button variant="ghost" onClick={() => navigateTo('step1')}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 4L6 8l4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Back
        </Button>
        <Button onClick={() => navigateTo('step3')} disabled={!isValid}>
          Continue
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </Button>
      </nav>

      <HelpButton />
    </div>
  );
}
