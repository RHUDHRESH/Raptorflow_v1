/**
 * ICP Editor Modal
 * Edit an Ideal Customer Profile (name, traits, pain points, behaviors)
 */

'use client';

import React, { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import Input from '@/components/ui/Input';
import Textarea from '@/components/ui/Textarea';
import Button from '@/components/ui/Button';

interface ICPEditorProps {
  isOpen: boolean;
  icp: {
    id: string;
    name: string;
    traits?: Record<string, string>;
    painPoints?: string[];
    behaviors?: string[];
  } | null;
  onClose: () => void;
  onSave: (icpId: string, updatedICP: any) => Promise<void>;
}

export default function ICPEditor({ isOpen, icp, onClose, onSave }: ICPEditorProps) {
  const [formData, setFormData] = useState({
    name: '',
    traits: {} as Record<string, string>,
    painPoints: [] as string[],
    behaviors: [] as string[],
  });
  const [painPointText, setPainPointText] = useState('');
  const [behaviorText, setBehaviorText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (icp) {
      setFormData({
        name: icp.name,
        traits: icp.traits || {},
        painPoints: icp.painPoints || [],
        behaviors: icp.behaviors || [],
      });
      setPainPointText('');
      setBehaviorText('');
      setError('');
    }
  }, [icp, isOpen]);

  const handleChange = (field: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const addPainPoint = () => {
    if (painPointText.trim()) {
      setFormData((prev) => ({
        ...prev,
        painPoints: [...prev.painPoints, painPointText.trim()],
      }));
      setPainPointText('');
    }
  };

  const removePainPoint = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      painPoints: prev.painPoints.filter((_, i) => i !== index),
    }));
  };

  const addBehavior = () => {
    if (behaviorText.trim()) {
      setFormData((prev) => ({
        ...prev,
        behaviors: [...prev.behaviors, behaviorText.trim()],
      }));
      setBehaviorText('');
    }
  };

  const removeBehavior = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      behaviors: prev.behaviors.filter((_, i) => i !== index),
    }));
  };

  const handleSave = async () => {
    if (!formData.name.trim()) {
      setError('ICP name is required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await onSave(icp!.id, formData);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save ICP');
    } finally {
      setLoading(false);
    }
  };

  if (!icp) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Edit Customer Profile">
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {/* Name */}
        <div>
          <label className="block text-sm font-medium text-[#2D2D2D] mb-2">
            Profile Name *
          </label>
          <Input
            type="text"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            placeholder="e.g., Enterprise SaaS CTO"
            className="w-full"
          />
        </div>

        {/* Pain Points */}
        <div>
          <label className="block text-sm font-medium text-[#2D2D2D] mb-2">
            Pain Points
          </label>
          <div className="flex gap-2 mb-2">
            <Input
              type="text"
              value={painPointText}
              onChange={(e) => setPainPointText(e.target.value)}
              placeholder="Add a pain point..."
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  addPainPoint();
                }
              }}
              className="flex-1"
            />
            <Button variant="secondary" onClick={addPainPoint} size="sm">
              Add
            </Button>
          </div>
          <div className="space-y-2">
            {formData.painPoints.map((point, i) => (
              <div
                key={i}
                className="flex items-center gap-2 p-2 bg-[#EAE0D2]/30 rounded-lg"
              >
                <span className="text-xs flex-1 text-[#2D2D2D]">{point}</span>
                <button
                  onClick={() => removePainPoint(i)}
                  className="text-red-600 hover:text-red-700 text-sm"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Behaviors */}
        <div>
          <label className="block text-sm font-medium text-[#2D2D2D] mb-2">
            Key Behaviors
          </label>
          <div className="flex gap-2 mb-2">
            <Input
              type="text"
              value={behaviorText}
              onChange={(e) => setBehaviorText(e.target.value)}
              placeholder="Add a behavior..."
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  addBehavior();
                }
              }}
              className="flex-1"
            />
            <Button variant="secondary" onClick={addBehavior} size="sm">
              Add
            </Button>
          </div>
          <div className="space-y-2">
            {formData.behaviors.map((behavior, i) => (
              <div
                key={i}
                className="flex items-center gap-2 p-2 bg-[#EAE0D2]/30 rounded-lg"
              >
                <span className="text-xs flex-1 text-[#2D2D2D]">{behavior}</span>
                <button
                  onClick={() => removeBehavior(i)}
                  className="text-red-600 hover:text-red-700 text-sm"
                >
                  ✕
                </button>
              </div>
            ))}
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
            {loading ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
