import React from 'react';

export function PathwayAILogo() {
  return (
    <div className="flex items-center gap-2">
      {/* Spark / asterisk icon */}
      <svg
        width="20"
        height="20"
        viewBox="0 0 20 20"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="text-gray-900"
      >
        <path
          d="M10 2v4M10 14v4M2 10h4M14 10h4M4.343 4.343l2.829 2.829M12.828 12.828l2.829 2.829M15.657 4.343l-2.829 2.829M7.172 12.828l-2.829 2.829"
          stroke="currentColor"
          strokeWidth="1.75"
          strokeLinecap="round"
        />
      </svg>
      <span className="text-base font-semibold text-gray-900">PathwayAI</span>
    </div>
  );
}
