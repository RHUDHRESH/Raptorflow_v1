/**
 * useToast Hook
 * Manages toast notifications globally
 */

'use client';

import { useState, useCallback, useId } from 'react';

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string;
  duration?: number;
}

export function useToast() {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const id = useId();

  const addToast = useCallback(
    (
      message: string,
      options?: {
        type?: 'success' | 'error' | 'warning' | 'info';
        title?: string;
        duration?: number;
      }
    ) => {
      const toastId = `${id}-${Date.now()}`;
      const toast: ToastMessage = {
        id: toastId,
        type: options?.type || 'info',
        title: options?.title,
        message,
        duration: options?.duration !== undefined ? options.duration : 5000,
      };

      setToasts((prev) => [...prev, toast]);

      return toastId;
    },
    [id]
  );

  const removeToast = useCallback((toastId: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== toastId));
  }, []);

  const success = useCallback(
    (message: string, title?: string) =>
      addToast(message, { type: 'success', title }),
    [addToast]
  );

  const error = useCallback(
    (message: string, title?: string) =>
      addToast(message, { type: 'error', title }),
    [addToast]
  );

  const warning = useCallback(
    (message: string, title?: string) =>
      addToast(message, { type: 'warning', title }),
    [addToast]
  );

  const info = useCallback(
    (message: string, title?: string) =>
      addToast(message, { type: 'info', title }),
    [addToast]
  );

  return {
    toasts,
    addToast,
    removeToast,
    success,
    error,
    warning,
    info,
  };
}
