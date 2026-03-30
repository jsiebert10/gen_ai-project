import React from 'react';

export function HelpButton() {
  return (
    <button
      type="button"
      className="fixed bottom-6 right-6 flex h-9 w-9 items-center justify-center rounded-full border border-gray-200 bg-white text-sm font-medium text-gray-500 shadow-sm hover:bg-gray-50 focus:outline-none"
      aria-label="Help"
    >
      ?
    </button>
  );
}
