/**
 * Context File Upload Component
 * Drag-drop zone for uploading files (images, PDFs, videos, audio)
 */

'use client';

import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/Button';

interface ContextFileUploadProps {
  workspaceId: string;
  onUploadComplete: () => void;
}

export default function ContextFileUpload({
  workspaceId,
  onUploadComplete,
}: ContextFileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    await handleFiles(e.dataTransfer.files);
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      await handleFiles(e.target.files);
    }
  };

  const handleFiles = async (files: FileList) => {
    if (!files.length) return;

    setLoading(true);
    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`/api/strategy/${workspaceId}/context/upload-file`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Failed to upload ${file.name}`);
        }
      }
      onUploadComplete();
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="flex flex-col gap-3 mb-4">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragging
            ? 'border-[#A68763] bg-[#A68763]/5'
            : 'border-[#D7C9AE] hover:bg-[#EAE0D2]'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileSelect}
          className="hidden"
          accept="image/*,.pdf,video/*,audio/*"
          disabled={loading}
        />

        <div className="text-4xl mb-2">📁</div>
        <p className="text-[#2D2D2D] font-medium mb-1">
          {loading ? 'Uploading...' : 'Drag files here or click to browse'}
        </p>
        <p className="text-sm text-[#2D2D2D]/60">
          Supports: images, PDFs, videos, audio files
        </p>
      </div>

      {loading && (
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#A68763] mx-auto"></div>
          <p className="text-sm text-[#2D2D2D]/60 mt-2">Processing files...</p>
        </div>
      )}
    </div>
  );
}
