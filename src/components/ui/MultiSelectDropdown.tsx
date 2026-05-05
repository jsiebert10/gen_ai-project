import React, { useState, useRef, useEffect } from 'react';
import { InterestCategory } from '@/types';

interface MultiSelectDropdownProps {
  label: string;
  categories: InterestCategory[];
  selected: string[];
  onChange: (selected: string[]) => void;
}

export function MultiSelectDropdown({ label, categories, selected, onChange }: MultiSelectDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const toggle = (option: string) => {
    if (selected.includes(option)) {
      onChange(selected.filter((s) => s !== option));
    } else {
      onChange([...selected, option]);
    }
  };

  const filteredCategories = categories
    .map((cat) => ({
      ...cat,
      options: cat.options.filter((opt) =>
        opt.toLowerCase().includes(search.toLowerCase())
      ),
    }))
    .filter((cat) => cat.options.length > 0);

  return (
    <div className="flex flex-col gap-3" ref={containerRef}>
      <span className="text-sm font-medium text-gray-800">{label}</span>

      {selected.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {selected.map((item) => (
            <span
              key={item}
              className="inline-flex items-center gap-1.5 rounded-full border border-gray-900 bg-gray-900 px-3 py-1 text-sm font-medium text-white"
            >
              {item}
              <button
                type="button"
                onClick={() => toggle(item)}
                className="ml-0.5 text-gray-300 hover:text-white focus:outline-none"
              >
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path d="M3 3l6 6M9 3l-6 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
              </button>
            </span>
          ))}
        </div>
      )}

      <div className="relative">
        <input
          type="text"
          placeholder="Search fields of study..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            if (!isOpen) setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:border-gray-500 focus:outline-none"
        />
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d={isOpen ? 'M4 10l4-4 4 4' : 'M4 6l4 4 4-4'}
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>

      {isOpen && (
        <div className="max-h-64 overflow-y-auto rounded-xl border border-gray-200 bg-white shadow-lg">
          {filteredCategories.length === 0 ? (
            <p className="px-4 py-3 text-sm text-gray-400">No matching fields found</p>
          ) : (
            filteredCategories.map((cat) => (
              <div key={cat.category}>
                <div className="sticky top-0 bg-gray-50 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
                  {cat.category}
                </div>
                {cat.options.map((option) => {
                  const active = selected.includes(option);
                  return (
                    <button
                      key={option}
                      type="button"
                      onClick={() => toggle(option)}
                      className={`flex w-full items-center justify-between px-4 py-2.5 text-sm transition-colors hover:bg-gray-50 ${
                        active ? 'font-medium text-gray-900' : 'text-gray-700'
                      }`}
                    >
                      {option}
                      {active && (
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                          <path d="M3 8l3.5 3.5L13 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      )}
                    </button>
                  );
                })}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
