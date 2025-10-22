/**
 * Context Items List Component
 * Displays list of added context items with delete option
 */

'use client';

import React from 'react';
import { ContextItem } from '@/hooks/useContextItems';

interface ContextItemsListProps {
  items: ContextItem[];
  onDelete: (id: string) => Promise<void>;
  loading: boolean;
}

const ITEM_TYPE_ICONS: Record<string, string> = {
  text: '📝',
  file_image: '🖼️',
  file_pdf: '📄',
  file_video: '🎬',
  file_audio: '🎵',
  url: '🔗',
};

const ITEM_TYPE_LABELS: Record<string, string> = {
  text: 'Text',
  file_image: 'Image',
  file_pdf: 'PDF',
  file_video: 'Video',
  file_audio: 'Audio',
  url: 'URL',
};

export default function ContextItemsList({
  items,
  onDelete,
  loading,
}: ContextItemsListProps) {
  if (items.length === 0) {
    return (
      <div className="text-center py-8 text-[#2D2D2D]/60">
        <p className="text-sm">No context items yet</p>
        <p className="text-xs mt-1">Add text, files, or links above</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {items.map((item) => (
        <div
          key={item.id}
          className="p-3 bg-[#EAE0D2]/30 rounded-lg border border-[#D7C9AE] hover:border-[#A68763] transition-colors group"
        >
          <div className="flex items-start gap-2">
            <span className="text-lg">{ITEM_TYPE_ICONS[item.itemType]}</span>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-[#2D2D2D]">
                {ITEM_TYPE_LABELS[item.itemType]}
              </p>
              {item.extractedText && (
                <p className="text-xs text-[#2D2D2D]/70 line-clamp-2 mt-1">
                  {item.extractedText}
                </p>
              )}
              {item.topics && item.topics.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {item.topics.slice(0, 2).map((topic, i) => (
                    <span
                      key={i}
                      className="text-xs bg-[#A68763]/10 text-[#A68763] px-2 py-1 rounded"
                    >
                      {topic}
                    </span>
                  ))}
                  {item.topics.length > 2 && (
                    <span className="text-xs text-[#2D2D2D]/60">
                      +{item.topics.length - 2}
                    </span>
                  )}
                </div>
              )}
            </div>
            <button
              onClick={() => onDelete(item.id)}
              disabled={loading}
              className="text-red-600 hover:text-red-700 opacity-0 group-hover:opacity-100 transition-opacity text-sm disabled:opacity-50"
              title="Delete item"
            >
              ✕
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
