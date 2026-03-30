import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

export function Input({ label, id, className = '', ...props }: InputProps) {
  const inputId = id ?? label.toLowerCase().replace(/\s+/g, '-');

  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={inputId} className="text-sm font-medium text-gray-800">
        {label}
      </label>
      <input
        id={inputId}
        className={`w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-200 ${className}`}
        {...props}
      />
    </div>
  );
}
