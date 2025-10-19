'use client';

import { forwardRef } from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = '', ...props }, ref) => {
    return (
      <div className="space-y-2">
        {label && (
          <label className="block text-sm text-secondary">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={`prompt-bar ${error ? 'border-barley border-opacity-40' : ''} ${className}`}
          {...props}
        />
        {error && (
          <p className="text-sm text-barley">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
