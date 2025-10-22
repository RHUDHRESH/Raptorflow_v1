/**
 * Confirmation Dialog Component
 * Modal for confirming potentially destructive actions
 */

'use client';

import React from 'react';
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

export default function ConfirmationDialog({
  isOpen,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  type = 'warning',
  loading = false,
  onConfirm,
  onCancel,
}: ConfirmationDialogProps) {
  const colors = TYPE_COLORS[type];

  const handleConfirm = async () => {
    const result = onConfirm();
    if (result instanceof Promise) {
      await result;
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onCancel} title={title}>
      <div className="space-y-4">
        {/* Icon */}
        <div className={`w-12 h-12 rounded-full ${colors.bg} flex items-center justify-center mx-auto`}>
          {type === 'danger' && '⚠'}
          {type === 'warning' && '❗'}
          {type === 'info' && 'ℹ'}
        </div>

        {/* Message */}
        <p className="text-center text-[#2D2D2D] text-sm">
          {message}
        </p>

        {/* Action Buttons */}
        <div className="flex gap-2 pt-4 border-t border-[#D7C9AE]">
          <Button
            variant="secondary"
            onClick={onCancel}
            disabled={loading}
            className="flex-1"
          >
            {cancelText}
          </Button>
          <button
            onClick={handleConfirm}
            disabled={loading}
            className={`flex-1 px-4 py-2 rounded-lg font-medium text-white transition-colors ${colors.button} disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {loading ? 'Confirming...' : confirmText}
          </button>
        </div>
      </div>
    </Modal>
  );
}
