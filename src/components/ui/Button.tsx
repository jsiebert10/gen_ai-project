import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost';
  children: React.ReactNode;
}

export function Button({ variant = 'primary', className = '', children, ...props }: ButtonProps) {
  const base = 'inline-flex items-center gap-2 font-medium transition-all focus:outline-none';

  const variants = {
    primary:
      'bg-gray-900 text-white rounded-full px-6 py-3 hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed',
    ghost:
      'text-gray-500 hover:text-gray-900 bg-transparent px-0 py-0 disabled:opacity-40',
  };

  return (
    <button className={`${base} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}
