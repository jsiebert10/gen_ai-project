import React from 'react';

interface StatCardProps {
  icon: React.ReactNode;
  value: string;
  label: string;
  subtext: string;
}

export function StatCard({ icon, value, label, subtext }: StatCardProps) {
  return (
    <div className="flex flex-1 flex-col gap-3 rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <span className="text-gray-400">{icon}</span>
        <svg
          width="14"
          height="14"
          viewBox="0 0 14 14"
          fill="none"
          className="text-gray-300"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M2 12L12 2M12 2H5M12 2V9"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
      <div>
        <p className="text-3xl font-semibold text-gray-900">{value}</p>
        <p className="mt-0.5 text-sm text-gray-400">{label}</p>
      </div>
      <div className="mt-auto">
        <span className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-500">{subtext}</span>
      </div>
    </div>
  );
}
