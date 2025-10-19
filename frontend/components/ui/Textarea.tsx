'use client';

import { forwardRef } from 'react';

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, className = '', ...props }, ref) => {
    return (
      <div className="space-y-2">
        {label && (
          <label className="block text-sm text-secondary">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          className={`w-full px-4 py-3 rounded-xl bg-[color:var(--panel)] border border-[color:var(--hairline)] 
            backdrop-blur-lg text-whiterock placeholder:text-[color:rgba(215,201,174,.6)]
            focus:shadow-focus transition-all duration-[220ms] resize-none
            ${error ? 'border-barley border-opacity-40' : ''} ${className}`}
          {...props}
        />
        {error && (
          <p className="text-sm text-barley">{error}</p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';
