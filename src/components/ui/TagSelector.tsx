import React from 'react';

interface TagSelectorProps {
  label: string;
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
}

export function TagSelector({ label, options, selected, onChange }: TagSelectorProps) {
  const toggle = (option: string) => {
    if (selected.includes(option)) {
      onChange(selected.filter((s) => s !== option));
    } else {
      onChange([...selected, option]);
    }
  };

  return (
    <div className="flex flex-col gap-3">
      <span className="text-sm font-medium text-gray-800">{label}</span>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => {
          const active = selected.includes(option);
          return (
            <button
              key={option}
              type="button"
              onClick={() => toggle(option)}
              className={`rounded-full border px-4 py-1.5 text-sm font-medium transition-all focus:outline-none ${
                active
                  ? 'border-gray-900 bg-gray-900 text-white'
                  : 'border-gray-300 bg-white text-gray-700 hover:border-gray-500'
              }`}
            >
              {option}
            </button>
          );
        })}
      </div>
    </div>
  );
}
