/**
 * Toast Notification Component
 * Displays temporary notifications (success, error, warning, info)
 */

'use client';

import React, { useEffect, useState } from 'react';

export interface ToastProps {
  id?: string;
  type?: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string;
  duration?: number; // milliseconds, 0 = never auto-close
  onClose?: () => void;
}

const TOAST_ICONS = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ',
};

const TOAST_COLORS = {
  success: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700', icon: 'text-green-600' },
  error: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', icon: 'text-red-600' },
  warning: { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-700', icon: 'text-yellow-600' },
  info: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700', icon: 'text-blue-600' },
};

export default function Toast({
  id = 'toast',
  type = 'info',
  title,
  message,
  duration = 5000,
  onClose,
}: ToastProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (duration === 0) return;

    const timer = setTimeout(() => {
      setIsVisible(false);
      onClose?.();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  if (!isVisible) return null;

  const colors = TOAST_COLORS[type];
  const icon = TOAST_ICONS[type];

  return (
    <div
      className={`${colors.bg} border ${colors.border} rounded-lg p-4 shadow-lg animate-in fade-in slide-in-from-right-10 duration-300`}
      role="alert"
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <span className={`text-lg font-bold ${colors.icon} flex-shrink-0`}>
          {icon}
        </span>

        {/* Content */}
        <div className="flex-1">
          {title && (
            <p className={`font-medium text-sm ${colors.text}`}>
              {title}
            </p>
          )}
          <p className={`text-sm ${colors.text} ${title ? 'mt-1' : ''}`}>
            {message}
          </p>
        </div>

        {/* Close Button */}
        <button
          onClick={() => {
            setIsVisible(false);
            onClose?.();
          }}
          className={`text-xl font-bold ${colors.text} hover:opacity-70 flex-shrink-0`}
          aria-label="Close notification"
        >
          ✕
        </button>
      </div>
    </div>
  );
}
