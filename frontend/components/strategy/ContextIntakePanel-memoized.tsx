/**
 * Context Intake Panel - Memoized Version
 * Left pane component for adding and managing context items
 * Optimizations: React.memo, useCallback, memoized child components
 */

'use client';

import React, { useState, useCallback, memo, useMemo } from 'react';
import { useContextItems } from '@/hooks/useContextItems';
import ContextTextInput from './ContextTextInput';
import ContextFileUpload from './ContextFileUpload';
import ContextURLInput from './ContextURLInput';
import ContextItemsList from './ContextItemsList';
import { Button } from '@/components/ui/Button';

interface ContextIntakePanelProps {
  workspace: any;
}

const MAX_CHARACTERS = 50000;

/**
 * Tab Button Component - Memoized
 */
const TabButton = memo(
  ({
    label,
    isActive,
    onClick,
  }: {
    label: string;
    isActive: boolean;
    onClick: () => void;
  }) => (
    <button
      onClick={onClick}
      className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
        isActive
          ? 'bg-[#A68763] text-white'
          : 'bg-[#EAE0D2] text-[#2D2D2D] hover:bg-[#D7C9AE]'
      }`}
    >
      {label}
    </button>
  ),
  (prevProps, nextProps) => {
    return (
      prevProps.label === nextProps.label &&
      prevProps.isActive === nextProps.isActive &&
      prevProps.onClick === nextProps.onClick
    );
  }
);

TabButton.displayName = 'TabButton';

/**
 * Character Counter Component - Memoized
 */
const CharacterCounter = memo(
  ({ count, max }: { count: number; max: number }) => {
    const percentage = (count / max) * 100;
    const isCritical = percentage > 80;

    return (
      <div className="mt-2">
        <div className="flex justify-between text-xs text-[#2D2D2D]/60 mb-1">
          <span>{count.toLocaleString()} / {max.toLocaleString()} characters</span>
          <span>{percentage.toFixed(0)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${
              isCritical ? 'bg-red-500' : 'bg-[#A68763]'
            }`}
            style={{ width: `${Math.min(percentage, 100)}%` }}
          />
        </div>
      </div>
    );
  },
  (prevProps, nextProps) => {
    return prevProps.count === nextProps.count && prevProps.max === nextProps.max;
  }
);

CharacterCounter.displayName = 'CharacterCounter';

/**
 * Input Area Component - Memoized
 */
const InputArea = memo(
  ({
    activeInputType,
    characterCount,
    onTextSubmit,
    onCharacterChange,
    loading,
  }: {
    activeInputType: string;
    characterCount: number;
    onTextSubmit: (text: string) => Promise<void>;
    onCharacterChange: (count: number) => void;
    loading: boolean;
  }) => {
    return (
      <>
        {activeInputType === 'text' && (
          <>
            <ContextTextInput
              onSubmit={onTextSubmit}
              maxCharacters={MAX_CHARACTERS}
              onCharacterChange={onCharacterChange}
              loading={loading}
            />
            <CharacterCounter count={characterCount} max={MAX_CHARACTERS} />
          </>
        )}

        {activeInputType === 'file' && (
          <ContextFileUpload
            onUpload={async (fileData) => {
              // Handle file upload
            }}
            loading={loading}
          />
        )}

        {activeInputType === 'url' && (
          <ContextURLInput
            onSubmit={async (url) => {
              // Handle URL submission
            }}
            loading={loading}
          />
        )}
      </>
    );
  },
  (prevProps, nextProps) => {
    return (
      prevProps.activeInputType === nextProps.activeInputType &&
      prevProps.characterCount === nextProps.characterCount &&
      prevProps.onTextSubmit === nextProps.onTextSubmit &&
      prevProps.onCharacterChange === nextProps.onCharacterChange &&
      prevProps.loading === nextProps.loading
    );
  }
);

InputArea.displayName = 'InputArea';

/**
 * Control Buttons Component - Memoized
 */
const ControlButtons = memo(
  ({ onAnalyze, isLoading }: { onAnalyze: () => void; isLoading: boolean }) => (
    <div className="flex gap-2 mt-4">
      <button
        onClick={onAnalyze}
        disabled={isLoading}
        className="flex-1 px-4 py-2 bg-[#A68763] text-white rounded-lg hover:bg-[#A68763]/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? 'Analyzing...' : 'Analyze'}
      </button>
      <button
        onClick={() => {}}
        className="flex-1 px-4 py-2 bg-[#D7C9AE] text-[#2D2D2D] rounded-lg hover:bg-[#D7C9AE]/80 transition-colors"
      >
        Lock Jobs
      </button>
    </div>
  ),
  (prevProps, nextProps) => {
    return (
      prevProps.onAnalyze === nextProps.onAnalyze &&
      prevProps.isLoading === nextProps.isLoading
    );
  }
);

ControlButtons.displayName = 'ControlButtons';

/**
 * Main ContextIntakePanel Component - Memoized
 */
const ContextIntakePanelComponent = ({
  workspace,
}: ContextIntakePanelProps) => {
  const [activeInputType, setActiveInputType] = useState<'text' | 'file' | 'url' | 'none'>('text');
  const [characterCount, setCharacterCount] = useState(0);
  const { contextItems, addItem, deleteItem, loading } = useContextItems(workspace?.id);

  // Memoized callbacks
  const handleTextSubmit = useCallback(
    async (text: string) => {
      await addItem({
        itemType: 'text',
        content: text,
      });
      setCharacterCount(0);
      setActiveInputType('none');
    },
    [addItem]
  );

  const handleCharacterChange = useCallback((count: number) => {
    setCharacterCount(count);
  }, []);

  const handleDeleteItem = useCallback(
    (itemId: string) => {
      deleteItem(itemId);
    },
    [deleteItem]
  );

  const handleAnalyze = useCallback(() => {
    // Trigger analysis
    console.log('Analysis triggered');
  }, []);

  const handleTabChange = useCallback((type: 'text' | 'file' | 'url' | 'none') => {
    setActiveInputType(type);
  }, []);

  // Memoize tab buttons
  const tabButtons = useMemo(
    () => (
      <div className="flex gap-2 mb-4">
        {(['text', 'file', 'url'] as const).map((type) => (
          <TabButton
            key={type}
            label={type.charAt(0).toUpperCase() + type.slice(1)}
            isActive={activeInputType === type}
            onClick={() => handleTabChange(type)}
          />
        ))}
      </div>
    ),
    [activeInputType, handleTabChange]
  );

  return (
    <div className="p-4 flex flex-col h-full">
      {/* Input Type Tabs */}
      {tabButtons}

      {/* Input Area */}
      <div className="flex-1 overflow-auto mb-4">
        <InputArea
          activeInputType={activeInputType}
          characterCount={characterCount}
          onTextSubmit={handleTextSubmit}
          onCharacterChange={handleCharacterChange}
          loading={loading}
        />
      </div>

      {/* Context Items List */}
      <div className="max-h-64 overflow-auto mb-4 border-t border-[#D7C9AE] pt-4">
        <h3 className="text-sm font-semibold text-[#2D2D2D] mb-2">
          Items ({contextItems?.length || 0})
        </h3>
        <ContextItemsList items={contextItems || []} onDelete={handleDeleteItem} />
      </div>

      {/* Control Buttons */}
      <ControlButtons onAnalyze={handleAnalyze} isLoading={loading} />
    </div>
  );
};

ContextIntakePanelComponent.displayName = 'ContextIntakePanel';

export default memo(ContextIntakePanelComponent);
