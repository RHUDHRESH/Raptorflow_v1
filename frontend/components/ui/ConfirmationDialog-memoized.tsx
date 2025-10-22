/**
 * Confirmation Dialog Component - Memoized Version
 * Optimizations: React.memo with custom comparison, useCallback
 */

'use client';

import React, { memo, useCallback, useState } from 'react';
import Modal from './Modal';
import Button from './Button';

interface ConfirmationDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'danger' | 'warning' | 'info';
  loading?: boolean;
  onConfirm: () => void | Promise<void>;
  onCancel: () => void;
}

const TYPE_COLORS = {
  danger: { button: 'bg-red-600 hover:bg-red-700', border: 'border-red-200', bg: 'bg-red-50' },
  warning: { button: 'bg-yellow-600 hover:bg-yellow-700', border: 'border-yellow-200', bg: 'bg-yellow-50' },
  info: { button: 'bg-blue-600 hover:bg-blue-700', border: 'border-blue-200', bg: 'bg-blue-50' },
};

/**
 * Icon Display Component - Memoized
 */
const DialogIcon = memo(
  ({ type, bgClass }: { type: 'danger' | 'warning' | 'info'; bgClass: string }) => {
    const icons: Record<string, string> = {
      danger: '⚠',
      warning: '❗',
      info: 'ℹ',
    };

    return (
      <div className={`w-12 h-12 rounded-full ${bgClass} flex items-center justify-center mx-auto`}>
        <span className="text-xl font-bold">{icons[type]}</span>
      </div>
    );
  },
  (prevProps, nextProps) => {
    return prevProps.type === nextProps.type && prevProps.bgClass === nextProps.bgClass;
  }
);

DialogIcon.displayName = 'DialogIcon';

/**
 * Message Display Component - Memoized
 */
const DialogMessage = memo(
  ({ message }: { message: string }) => (
    <p className="text-center text-[#2D2D2D] text-sm">
      {message}
    </p>
  ),
  (prevProps, nextProps) => prevProps.message === nextProps.message
);

DialogMessage.displayName = 'DialogMessage';

/**
 * Action Buttons Component - Memoized
 */
const ActionButtons = memo(
  ({
    cancelText,
    confirmText,
    isLoading,
    buttonClass,
    onCancel,
    onConfirm,
  }: {
    cancelText: string;
    confirmText: string;
    isLoading: boolean;
    buttonClass: string;
    onCancel: () => void;
    onConfirm: () => void;
  }) => (
    <div className="flex gap-2 pt-4 border-t border-[#D7C9AE]">
      <Button
        variant="secondary"
        onClick={onCancel}
        disabled={isLoading}
        className="flex-1"
      >
        {cancelText}
      </Button>
      <button
        onClick={onConfirm}
        disabled={isLoading}
        className={`flex-1 px-4 py-2 rounded-lg font-medium text-white transition-colors ${buttonClass} disabled:opacity-50 disabled:cursor-not-allowed`}
      >
        {isLoading ? 'Confirming...' : confirmText}
      </button>
    </div>
  ),
  (prevProps, nextProps) => {
    return (
      prevProps.cancelText === nextProps.cancelText &&
      prevProps.confirmText === nextProps.confirmText &&
      prevProps.isLoading === nextProps.isLoading &&
      prevProps.buttonClass === nextProps.buttonClass &&
      prevProps.onCancel === nextProps.onCancel &&
      prevProps.onConfirm === nextProps.onConfirm
    );
  }
);

ActionButtons.displayName = 'ActionButtons';

/**
 * Main Confirmation Dialog Component - Memoized
 */
const ConfirmationDialogComponent = ({
  isOpen,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  type = 'warning',
  loading = false,
  onConfirm,
  onCancel,
}: ConfirmationDialogProps) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const colors = TYPE_COLORS[type];
  const isLoading = loading || isProcessing;

  // Memoized confirm handler
  const handleConfirm = useCallback(async () => {
    setIsProcessing(true);
    try {
      const result = onConfirm();
      if (result instanceof Promise) {
        await result;
      }
    } finally {
      setIsProcessing(false);
    }
  }, [onConfirm]);

  // Memoized cancel handler
  const handleCancel = useCallback(() => {
    onCancel();
  }, [onCancel]);

  return (
    <Modal isOpen={isOpen} onClose={handleCancel} title={title}>
      <div className="space-y-4">
        {/* Icon */}
        <DialogIcon type={type} bgClass={colors.bg} />

        {/* Message */}
        <DialogMessage message={message} />

        {/* Action Buttons */}
        <ActionButtons
          cancelText={cancelText}
          confirmText={confirmText}
          isLoading={isLoading}
          buttonClass={colors.button}
          onCancel={handleCancel}
          onConfirm={handleConfirm}
        />
      </div>
    </Modal>
  );
};

ConfirmationDialogComponent.displayName = 'ConfirmationDialog';

// Export memoized version with custom comparison
export default memo(ConfirmationDialogComponent, (prevProps, nextProps) => {
  return (
    prevProps.isOpen === nextProps.isOpen &&
    prevProps.title === nextProps.title &&
    prevProps.message === nextProps.message &&
    prevProps.confirmText === nextProps.confirmText &&
    prevProps.cancelText === nextProps.cancelText &&
    prevProps.type === nextProps.type &&
    prevProps.loading === nextProps.loading &&
    prevProps.onConfirm === nextProps.onConfirm &&
    prevProps.onCancel === nextProps.onCancel
  );
});
