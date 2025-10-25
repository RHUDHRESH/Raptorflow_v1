/**
 * Context Text Input Component
 * Text area for adding context with character counting
 */

'use client';

import React, { useState } from 'react';
import { Textarea } from '@/components/ui/Textarea';
import { Button } from '@/components/ui/Button';

interface ContextTextInputProps {
  onSubmit: (text: string) => Promise<void>;
  maxCharacters: number;
  characterCount: number;
  onCharacterCountChange: (count: number) => void;
}

export default function ContextTextInput({
  onSubmit,
  maxCharacters,
  characterCount,
  onCharacterCountChange,
}: ContextTextInputProps) {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (value: string) => {
    if (value.length <= maxCharacters) {
      setText(value);
      onCharacterCountChange(value.length);
    }
  };

  const handleSubmit = async () => {
    if (!text.trim()) return;

    setLoading(true);
    try {
      await onSubmit(text);
      setText('');
      onCharacterCountChange(0);
    } finally {
      setLoading(false);
    }
  };

  const percentage = (characterCount / maxCharacters) * 100;
  const isNearLimit = percentage > 80;

  return (
    <div className="flex flex-col gap-3 mb-4">
      <Textarea
        value={text}
        onChange={(e) => handleChange(e.target.value)}
        placeholder="Paste customer research, feedback, market analysis, or any context..."
        className="h-40"
        disabled={loading}
      />

      {/* Character Counter */}
      <div className="flex items-center justify-between">
        <span className={`text-xs ${isNearLimit ? 'text-red-600' : 'text-[#2D2D2D]/60'}`}>
          {characterCount.toLocaleString()} / {maxCharacters.toLocaleString()} characters
        </span>
        {/* Progress bar */}
        <div className="h-1 flex-1 ml-3 bg-[#D7C9AE] rounded-full overflow-hidden">
          <div
            className={`h-full transition-all ${
              isNearLimit ? 'bg-red-600' : 'bg-[#A68763]'
            }`}
            style={{ width: `${Math.min(percentage, 100)}%` }}
          />
        </div>
      </div>

      {/* Submit Button */}
      <Button
        variant="primary"
        onClick={handleSubmit}
        disabled={!text.trim() || loading}
        size="sm"
      >
        {loading ? 'Adding...' : 'Add Context'}
      </Button>
    </div>
  );
}
