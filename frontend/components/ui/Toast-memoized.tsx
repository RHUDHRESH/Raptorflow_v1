/**
 * Toast Notification Component - Memoized Version
 * Optimizations: React.memo with custom comparison, useEffect cleanup
 */

'use client';

import React, { useEffect, useState, memo } from 'react';

export interface ToastProps {
  id?: string;
  type?: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string;
  duration?: number;
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

/**
 * Close Button Component - Memoized
 */
const CloseButton = memo(
  ({ text, onClick }: { text: string; onClick: () => void }) => (
    <button
      onClick={onClick}
      className={`text-xl font-bold ${text} hover:opacity-70 flex-shrink-0`}
      aria-label="Close notification"
    >
      ✕
    </button>
  ),
  (prevProps, nextProps) => {
    return (
      prevProps.text === nextProps.text &&
      prevProps.onClick === nextProps.onClick
    );
  }
);

CloseButton.displayName = 'CloseButton';

/**
 * Icon Component - Memoized
 */
const ToastIcon = memo(
  ({ type, iconColor }: { type: 'success' | 'error' | 'warning' | 'info'; iconColor: string }) => {
    const icon = TOAST_ICONS[type];
    return (
      <span className={`text-lg font-bold ${iconColor} flex-shrink-0`}>
        {icon}
      </span>
    );
  },
  (prevProps, nextProps) => {
    return (
      prevProps.type === nextProps.type &&
      prevProps.iconColor === nextProps.iconColor
    );
  }
);

ToastIcon.displayName = 'ToastIcon';

/**
 * Content Component - Memoized
 */
const ToastContent = memo(
  ({
    title,
    message,
    textColor,
  }: {
    title?: string;
    message: string;
    textColor: string;
  }) => (
    <div className="flex-1">
      {title && (
        <p className={`font-medium text-sm ${textColor}`}>
          {title}
        </p>
      )}
      <p className={`text-sm ${textColor} ${title ? 'mt-1' : ''}`}>
        {message}
      </p>
    </div>
  ),
  (prevProps, nextProps) => {
    return (
      prevProps.title === nextProps.title &&
      prevProps.message === nextProps.message &&
      prevProps.textColor === nextProps.textColor
    );
  }
);

ToastContent.displayName = 'ToastContent';

/**
 * Main Toast Component - Memoized
 */
const ToastComponent = ({
  id = 'toast',
  type = 'info',
  title,
  message,
  duration = 5000,
  onClose,
}: ToastProps) => {
  const [isVisible, setIsVisible] = useState(true);

  // Handle auto-close
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

  const handleClose = () => {
    setIsVisible(false);
    onClose?.();
  };

  return (
    <div
      className={`${colors.bg} border ${colors.border} rounded-lg p-4 shadow-lg animate-in fade-in slide-in-from-right-10 duration-300`}
      role="alert"
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <ToastIcon type={type} iconColor={colors.icon} />

        {/* Content */}
        <ToastContent title={title} message={message} textColor={colors.text} />

        {/* Close Button */}
        <CloseButton text={colors.text} onClick={handleClose} />
      </div>
    </div>
  );
};

ToastComponent.displayName = 'Toast';

// Memoize with custom comparison
export default memo(ToastComponent, (prevProps, nextProps) => {
  return (
    prevProps.id === nextProps.id &&
    prevProps.type === nextProps.type &&
    prevProps.title === nextProps.title &&
    prevProps.message === nextProps.message &&
    prevProps.duration === nextProps.duration &&
    prevProps.onClose === nextProps.onClose
  );
});
