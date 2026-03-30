import React from 'react';
import { useApp } from '@/contexts/AppContext';
import { OnboardingHeader } from '@/components/layout/OnboardingHeader';
import { Input } from '@/components/ui/Input';
import { RangeSlider } from '@/components/ui/RangeSlider';
import { Button } from '@/components/ui/Button';
import { HelpButton } from '@/components/ui/HelpButton';

export function BackgroundStep() {
  const { profile, updateProfile, navigateTo } = useApp();

  const isValid =
    profile.fullName.trim().length > 0 && profile.undergraduateMajor.trim().length > 0;

  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      <OnboardingHeader currentStep={1} />

      <main className="flex flex-1 flex-col items-center px-6 py-12">
        <div className="w-full max-w-xl">
          <p className="mb-1 text-sm text-gray-400">Step 1 of 3</p>
          <h1 className="mb-8 text-3xl font-semibold text-gray-900">Your Background</h1>

          <div className="rounded-2xl border border-gray-100 bg-white p-8 shadow-sm">
            <div className="flex flex-col gap-6">
              <Input
                label="Full Name"
                placeholder="e.g. Priya Sharma"
                value={profile.fullName}
                onChange={(e) => updateProfile({ fullName: e.target.value })}
              />
              <Input
                label="Undergraduate Major"
                placeholder="e.g. Computer Science"
                value={profile.undergraduateMajor}
                onChange={(e) => updateProfile({ undergraduateMajor: e.target.value })}
              />
              <RangeSlider
                label="GPA"
                value={profile.gpa}
                min={1.0}
                max={4.0}
                step={0.1}
                formatValue={(v) => `${v.toFixed(1)} / 4.0`}
                onChange={(v) => updateProfile({ gpa: v })}
              />
            </div>
          </div>
        </div>
      </main>

      {/* Navigation */}
      <nav className="flex items-center justify-between border-t border-gray-100 bg-white px-8 py-5">
        <Button variant="ghost" onClick={() => navigateTo('landing')}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 4L6 8l4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Home
        </Button>
        <Button onClick={() => navigateTo('step2')} disabled={!isValid}>
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
