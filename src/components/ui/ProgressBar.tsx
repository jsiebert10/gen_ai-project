import React from 'react';

interface ProgressBarProps {
  totalSteps: number;
  currentStep: number; // 1-based
}

export function ProgressBar({ totalSteps, currentStep }: ProgressBarProps) {
  return (
    <div className="flex items-center gap-1.5">
      {Array.from({ length: totalSteps }).map((_, i) => (
        <div
          key={i}
          className={`h-1 w-8 rounded-full transition-colors ${
            i < currentStep ? 'bg-gray-900' : 'bg-gray-300'
          }`}
        />
      ))}
    </div>
  );
}
