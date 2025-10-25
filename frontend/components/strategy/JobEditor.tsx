/**
 * Job Editor Modal
 * Edit a Job-to-be-Done with Why, Circumstances, Forces, Anxieties
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Button } from '@/components/ui/Button';

interface JobEditorProps {
  isOpen: boolean;
  job: {
    id: string;
    why: string;
    circumstances: string;
    forces: string;
    anxieties: string;
  } | null;
  onClose: () => void;
  onSave: (jobId: string, updatedJob: any) => Promise<void>;
}

export default function JobEditor({ isOpen, job, onClose, onSave }: JobEditorProps) {
  const [formData, setFormData] = useState({
    why: '',
    circumstances: '',
    forces: '',
    anxieties: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (job) {
      setFormData({
        why: job.why,
        circumstances: job.circumstances,
        forces: job.forces,
        anxieties: job.anxieties,
      });
      setError('');
    }
  }, [job, isOpen]);

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSave = async () => {
    if (!formData.why.trim()) {
      setError('Job statement (Why) is required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await onSave(job!.id, formData);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save job');
    } finally {
      setLoading(false);
    }
  };

  if (!job) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Edit Job">
      <div className="space-y-4">
        {/* Why - Job Statement */}
        <div>
          <label className="block text-sm font-medium text-[#2D2D2D] mb-2">
            Why (Job Statement) *
          </label>
          <Textarea
            value={formData.why}
            onChange={(e) => handleChange('why', e.target.value)}
            placeholder="What is the customer trying to accomplish?"
            rows={3}
            className="w-full"
          />
          <p className="text-xs text-[#2D2D2D]/60 mt-1">
            The core job or goal the customer wants to accomplish
          </p>
        </div>

        {/* Circumstances - When/Where */}
        <div>
          <label className="block text-sm font-medium text-[#2D2D2D] mb-2">
            Circumstances (When/Where)
          </label>
          <Textarea
            value={formData.circumstances}
            onChange={(e) => handleChange('circumstances', e.target.value)}
            placeholder="When and where does this job occur? What triggers it?"
            rows={3}
            className="w-full"
          />
          <p className="text-xs text-[#2D2D2D]/60 mt-1">
            The situation or trigger that creates the need for this job
          </p>
        </div>

        {/* Forces - Drivers & Pushes */}
        <div>
          <label className="block text-sm font-medium text-[#2D2D2D] mb-2">
            Forces (Drivers & Pushes)
          </label>
          <Textarea
            value={formData.forces}
            onChange={(e) => handleChange('forces', e.target.value)}
            placeholder="What drives them toward this job? What motivates them?"
            rows={3}
            className="w-full"
          />
          <p className="text-xs text-[#2D2D2D]/60 mt-1">
            Emotional and functional drivers pushing them toward this job
          </p>
        </div>

        {/* Anxieties - Worries & Concerns */}
        <div>
          <label className="block text-sm font-medium text-[#2D2D2D] mb-2">
            Anxieties (Worries & Concerns)
          </label>
          <Textarea
            value={formData.anxieties}
            onChange={(e) => handleChange('anxieties', e.target.value)}
            placeholder="What worries or concerns do they have about this job?"
            rows={3}
            className="w-full"
          />
          <p className="text-xs text-[#2D2D2D]/60 mt-1">
            Fears, worries, and concerns that might hold them back
          </p>
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
