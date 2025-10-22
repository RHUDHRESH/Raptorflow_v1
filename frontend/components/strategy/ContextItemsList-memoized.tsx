/**
 * Context Items List - Memoized Version
 * Optimizations: React.memo for list items, useCallback for handlers
 * Prevents O(n) re-renders when updating individual items
 */

'use client';

import React, { memo, useCallback } from 'react';

interface ContextItem {
  id: string;
  type: string;
  content: string;
  topics?: string[];
  createdAt?: string;
}

interface ContextItemsListProps {
  items: ContextItem[];
  onDelete: (itemId: string) => void;
}

const ITEM_TYPE_ICONS: Record<string, string> = {
  text: '📝',
  file_image: '🖼️',
  file_pdf: '📄',
  file_video: '🎬',
  file_audio: '🎵',
  url: '🔗',
};

/**
 * Topic Badge Component - Memoized
 */
const TopicBadge = memo(
  ({ topic }: { topic: string }) => (
    <span className="inline-block px-2 py-1 text-xs bg-[#A68763]/10 text-[#A68763] rounded">
      {topic}
    </span>
  ),
  (prevProps, nextProps) => prevProps.topic === nextProps.topic
);

TopicBadge.displayName = 'TopicBadge';

/**
 * Individual Context Item Component - Heavily Memoized
 * Only re-renders if id, type, or callback changes
 */
const ContextItemComponent = memo(
  ({
    item,
    onDelete,
  }: {
    item: ContextItem;
    onDelete: (itemId: string) => void;
  }) => {
    const icon = ITEM_TYPE_ICONS[item.type] || '📋';
    const preview = item.content?.substring(0, 100) || '';
    const topics = item.topics?.slice(0, 2) || [];

    const handleDelete = useCallback(() => {
      onDelete(item.id);
    }, [item.id, onDelete]);

    return (
      <div className="p-3 bg-gray-50 rounded-lg border border-[#D7C9AE] hover:bg-gray-100 transition-colors group">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            {/* Header with icon and type */}
            <div className="flex items-center gap-2 mb-2">
              <span className="text-lg flex-shrink-0">{icon}</span>
              <span className="text-xs font-semibold text-[#A68763] uppercase">
                {item.type.replace(/_/g, ' ')}
              </span>
            </div>

            {/* Content preview */}
            <p className="text-sm text-[#2D2D2D] line-clamp-2 break-words">
              {preview}
              {item.content && item.content.length > 100 ? '...' : ''}
            </p>

            {/* Topics */}
            {topics.length > 0 && (
              <div className="flex gap-1 flex-wrap mt-2">
                {topics.map((topic) => (
                  <TopicBadge key={topic} topic={topic} />
                ))}
              </div>
            )}
          </div>

          {/* Delete button */}
          <button
            onClick={handleDelete}
            className="opacity-0 group-hover:opacity-100 p-1 text-red-600 hover:bg-red-50 rounded transition-all flex-shrink-0"
            aria-label={`Delete ${item.type}`}
          >
            ✕
          </button>
        </div>
      </div>
    );
  },
  (prevProps, nextProps) => {
    // Custom comparison: only re-render if item ID or callback changes
    return (
      prevProps.item.id === nextProps.item.id &&
      prevProps.item.type === nextProps.item.type &&
      prevProps.item.content === nextProps.item.content &&
      prevProps.item.topics?.length === nextProps.item.topics?.length &&
      prevProps.onDelete === nextProps.onDelete
    );
  }
);

ContextItemComponent.displayName = 'ContextItem';

/**
 * Empty State Component - Memoized
 */
const EmptyState = memo(() => (
  <div className="text-center py-8 text-[#2D2D2D]/60">
    <p className="text-sm">No context items yet</p>
    <p className="text-xs mt-1">Start by adding text, files, or links above</p>
  </div>
));

EmptyState.displayName = 'EmptyState';

/**
 * Main Context Items List Component - Memoized
 */
const ContextItemsListComponent = ({
  items,
  onDelete,
}: ContextItemsListProps) => {
  // Memoize callback to maintain reference stability
  const memoizedOnDelete = useCallback(
    (itemId: string) => {
      onDelete(itemId);
    },
    [onDelete]
  );

  if (!items || items.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="space-y-2">
      {items.map((item) => (
        <ContextItemComponent
          key={item.id}
          item={item}
          onDelete={memoizedOnDelete}
        />
      ))}
    </div>
  );
};

ContextItemsListComponent.displayName = 'ContextItemsList';

// Export memoized version
export default memo(ContextItemsListComponent, (prevProps, nextProps) => {
  // Only re-render if items array length or onDelete callback changes
  return (
    prevProps.items?.length === nextProps.items?.length &&
    prevProps.items?.every((item, idx) => item.id === nextProps.items?.[idx]?.id) &&
    prevProps.onDelete === nextProps.onDelete
  );
});
