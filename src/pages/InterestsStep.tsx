import React, { useState } from 'react';
import { useApp } from '@/contexts/AppContext';
import { OnboardingHeader } from '@/components/layout/OnboardingHeader';
import { TagSelector } from '@/components/ui/TagSelector';
import { Button } from '@/components/ui/Button';
import { HelpButton } from '@/components/ui/HelpButton';
import { INTEREST_OPTIONS, DashboardData } from '@/types';

export function InterestsStep() {
  const { profile, updateProfile, navigateTo, setDashboardData } = useApp();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isValid = profile.areasOfInterest.length > 0;

  const handleViewDashboard = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/dashboard', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profile),
      });
      if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        throw new Error(detail?.detail || `Server error ${response.status}`);
      }
      const data: DashboardData = await response.json();
      setDashboardData(data);
      navigateTo('dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

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

          {error && (
            <p className="mt-4 rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-600">
              {error}
            </p>
          )}

          {isLoading && (
            <p className="mt-4 text-center text-sm text-gray-500">
              Running AI analysis — this takes about 20–30 seconds...
            </p>
          )}
        </div>
      </main>

      <nav className="flex items-center justify-between border-t border-gray-100 bg-white px-8 py-5">
        <Button variant="ghost" onClick={() => navigateTo('step2')} disabled={isLoading}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M10 4L6 8l4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Back
        </Button>
        <Button onClick={handleViewDashboard} disabled={!isValid || isLoading}>
          {isLoading ? 'Analyzing...' : 'View Dashboard'}
          {!isLoading && (
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          )}
        </Button>
      </nav>

      <HelpButton />
    </div>
  );
}
