/**
 * Avatar Editor Modal
 * Edit ICP avatar with style and color selection
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

interface AvatarEditorProps {
  isOpen: boolean;
  icpId: string | null;
  currentColor: string;
  currentType: string;
  onClose: () => void;
  onSave: (icpId: string, avatarType: string, avatarColor: string) => Promise<void>;
}

const AVATAR_STYLES = [
  { type: 'icon', label: '👤 Icon', description: 'Simple icon avatar' },
  { type: 'icon_letter', label: 'A🔤 Icon + Letter', description: 'Icon with first letter' },
  { type: 'frame', label: '🖼️ Frame', description: 'Framed avatar' },
];

const PRESET_COLORS = [
  '#A68763',  // Barleycorn
  '#D7C9AE',  // Akaroa
  '#2D2D2D',  // Mineshaft
  '#EAE0D2',  // White Rock
  '#8B7355',  // Brown variant
  '#D4A574',  // Gold variant
  '#6B5B4F',  // Dark brown
  '#C9A375',  // Light brown
];

export default function AvatarEditor({
  isOpen,
  icpId,
  currentColor,
  currentType,
  onClose,
  onSave,
}: AvatarEditorProps) {
  const [selectedType, setSelectedType] = useState(currentType || 'icon');
  const [selectedColor, setSelectedColor] = useState(currentColor || '#A68763');
  const [customColor, setCustomColor] = useState(currentColor || '#A68763');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      setSelectedType(currentType || 'icon');
      setSelectedColor(currentColor || '#A68763');
      setCustomColor(currentColor || '#A68763');
      setError('');
    }
  }, [isOpen, currentType, currentColor]);

  const handleColorSelect = (color: string) => {
    setSelectedColor(color);
    setCustomColor(color);
  };

  const handleCustomColorChange = (color: string) => {
    setCustomColor(color);
    setSelectedColor(color);
  };

  const handleSave = async () => {
    if (!icpId) return;

    setLoading(true);
    setError('');

    try {
      await onSave(icpId, selectedType, selectedColor);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save avatar');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Edit Avatar">
      <div className="space-y-6">
        {/* Preview */}
        <div className="flex justify-center">
          <div
            className="w-24 h-24 rounded-full flex items-center justify-center text-4xl shadow-lg"
            style={{ backgroundColor: selectedColor }}
          >
            👤
          </div>
        </div>

        {/* Avatar Style Selection */}
        <div>
          <label className="block text-sm font-medium text-[#2D2D2D] mb-3">
            Avatar Style
          </label>
          <div className="grid grid-cols-1 gap-2">
            {AVATAR_STYLES.map((style) => (
              <button
                key={style.type}
                onClick={() => setSelectedType(style.type)}
                className={`p-3 rounded-lg border-2 text-left transition-colors ${
                  selectedType === style.type
                    ? 'border-[#A68763] bg-[#A68763]/5'
                    : 'border-[#D7C9AE] hover:border-[#A68763]'
                }`}
              >
                <p className="font-medium text-[#2D2D2D]">{style.label}</p>
                <p className="text-xs text-[#2D2D2D]/60 mt-1">{style.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Color Selection */}
        <div>
          <label className="block text-sm font-medium text-[#2D2D2D] mb-3">
            Avatar Color
          </label>

          {/* Preset Colors */}
          <div className="grid grid-cols-4 gap-2 mb-4">
            {PRESET_COLORS.map((color) => (
              <button
                key={color}
                onClick={() => handleColorSelect(color)}
                className={`w-full aspect-square rounded-lg border-2 transition-all ${
                  selectedColor === color
                    ? 'border-[#2D2D2D] ring-2 ring-[#A68763]'
                    : 'border-[#D7C9AE] hover:border-[#A68763]'
                }`}
                style={{ backgroundColor: color }}
                title={color}
              />
            ))}
          </div>

          {/* Custom Color */}
          <div className="flex gap-2">
            <Input
              type="color"
              value={customColor}
              onChange={(e) => handleCustomColorChange(e.target.value)}
              className="h-10 w-16 p-1"
            />
            <Input
              type="text"
              value={customColor}
              onChange={(e) => handleCustomColorChange(e.target.value)}
              placeholder="#A68763"
              className="flex-1"
            />
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2 pt-4 border-t border-[#D7C9AE]">
          <Button
            variant="secondary"
            onClick={onClose}
            disabled={loading}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSave}
            disabled={loading}
            className="flex-1"
          >
            {loading ? 'Saving...' : 'Save Avatar'}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
