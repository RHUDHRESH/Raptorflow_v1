/**
 * Context Intake Panel
 * Left pane component for adding and managing context items
 * Supports: text input, file upload, URL input, metadata tagging
 */

'use client';

import React, { useState } from 'react';
import { useContextItems } from '@/hooks/useContextItems';
import ContextTextInput from './ContextTextInput';
import ContextFileUpload from './ContextFileUpload';
import ContextURLInput from './ContextURLInput';
import ContextItemsList from './ContextItemsList';
import { Button } from '@/components/ui/Button';

interface ContextIntakePanelProps {
  workspace: any;
}

export default function ContextIntakePanel({ workspace }: ContextIntakePanelProps) {
  const [activeInputType, setActiveInputType] = useState<'text' | 'file' | 'url' | 'none'>('text');
  const [characterCount, setCharacterCount] = useState(0);
  const { contextItems, addItem, deleteItem, loading } = useContextItems(workspace?.id);

  const MAX_CHARACTERS = 50000;

  const handleTextSubmit = async (text: string) => {
    await addItem({
      itemType: 'text',
      content: text,
    });
    setCharacterCount(0);
    setActiveInputType('none');
  };

  return (
    <div className="p-4 flex flex-col h-full">
      {/* Input Type Tabs */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setActiveInputType('text')}
          className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeInputType === 'text'
              ? 'bg-[#A68763] text-white'
              : 'bg-[#EAE0D2] text-[#2D2D2D] hover:bg-[#D7C9AE]'
          }`}
        >
          Text
        </button>
        <button
          onClick={() => setActiveInputType('file')}
          className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeInputType === 'file'
              ? 'bg-[#A68763] text-white'
              : 'bg-[#EAE0D2] text-[#2D2D2D] hover:bg-[#D7C9AE]'
          }`}
        >
          File
        </button>
        <button
          onClick={() => setActiveInputType('url')}
          className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeInputType === 'url'
              ? 'bg-[#A68763] text-white'
              : 'bg-[#EAE0D2] text-[#2D2D2D] hover:bg-[#D7C9AE]'
          }`}
        >
          Link
        </button>
      </div>

      {/* Input Sections */}
      {activeInputType === 'text' && (
        <ContextTextInput
          onSubmit={handleTextSubmit}
          maxCharacters={MAX_CHARACTERS}
          characterCount={characterCount}
          onCharacterCountChange={setCharacterCount}
        />
      )}

      {activeInputType === 'file' && (
        <ContextFileUpload
          workspaceId={workspace?.id}
          onUploadComplete={() => setActiveInputType('none')}
        />
      )}

      {activeInputType === 'url' && (
        <ContextURLInput
          onSubmit={async (url) => {
            await addItem({
              itemType: 'url',
              content: url,
            });
            setActiveInputType('none');
          }}
        />
      )}

      {/* Context Items List */}
      <div className="mt-6 pt-4 border-t border-[#D7C9AE]">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-[#2D2D2D]">
            Items Added ({contextItems.length})
          </h3>
          {contextItems.length > 0 && (
            <Button
              variant="tertiary"
              size="sm"
              onClick={() => {
                // Clear all items
                contextItems.forEach((item) => deleteItem(item.id));
              }}
            >
              Clear All
            </Button>
          )}
        </div>
        <div className="flex-1 overflow-auto">
          <ContextItemsList
            items={contextItems}
            onDelete={deleteItem}
            loading={loading}
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-6 pt-4 border-t border-[#D7C9AE] flex gap-2">
        <Button
          variant="primary"
          disabled={contextItems.length === 0}
          className="flex-1"
        >
          Lock Jobs
        </Button>
        <Button
          variant="secondary"
          className="flex-1"
        >
          Analyze
        </Button>
      </div>
    </div>
  );
}
