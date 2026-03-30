import React from 'react';

interface RangeSliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  formatValue?: (v: number) => string;
  onChange: (value: number) => void;
}

export function RangeSlider({
  label,
  value,
  min,
  max,
  step = 0.1,
  formatValue,
  onChange,
}: RangeSliderProps) {
  const display = formatValue ? formatValue(value) : String(value);
  const minLabel = formatValue ? formatValue(min) : String(min);
  const maxLabel = formatValue ? formatValue(max) : String(max);
  const pct = ((value - min) / (max - min)) * 100;

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-baseline gap-2">
        <span className="text-sm font-medium text-gray-800">{label}</span>
        <span className="text-sm text-gray-400">({display})</span>
      </div>
      <div className="relative">
        {/* Track background */}
        <div className="relative h-1.5 w-full rounded-full bg-gray-200">
          <div
            className="absolute left-0 top-0 h-full rounded-full bg-gray-900"
            style={{ width: `${pct}%` }}
          />
        </div>
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="absolute inset-0 h-full w-full cursor-pointer opacity-0"
          style={{ margin: 0 }}
        />
        {/* Thumb */}
        <div
          className="pointer-events-none absolute top-1/2 h-4 w-4 -translate-x-1/2 -translate-y-1/2 rounded-full bg-gray-900 shadow"
          style={{ left: `${pct}%` }}
        />
      </div>
      <div className="flex justify-between text-xs text-gray-400">
        <span>{minLabel}</span>
        <span>{maxLabel}</span>
      </div>
    </div>
  );
}
