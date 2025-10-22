/**
 * useContextItems Hook
 * Manages context items for a strategy workspace
 */

'use client';

import { useState, useEffect, useCallback } from 'react';

export interface ContextItem {
  id: string;
  itemType: 'text' | 'file_image' | 'file_pdf' | 'file_video' | 'file_audio' | 'url';
  source: 'user_input' | 'uploaded_file' | 'web_link' | 'transcription';
  extractedText?: string;
  topics?: string[];
  entities?: string[];
  keywords?: string[];
  sentiment?: 'positive' | 'neutral' | 'negative';
  createdAt: string;
}

export function useContextItems(workspaceId: string) {
  const [contextItems, setContextItems] = useState<ContextItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch context items
  useEffect(() => {
    const fetchItems = async () => {
      if (!workspaceId) return;

      try {
        setLoading(true);
        const response = await fetch(`/api/strategy/${workspaceId}/context`);

        if (!response.ok) {
          throw new Error('Failed to fetch context items');
        }

        const data = await response.json();
        setContextItems(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load context items');
      } finally {
        setLoading(false);
      }
    };

    fetchItems();
  }, [workspaceId]);

  // Add context item
  const addItem = useCallback(
    async (item: { itemType: string; content: string }) => {
      if (!workspaceId) return;

      try {
        let endpoint = '';
        let body = {};

        if (item.itemType === 'text') {
          endpoint = `${workspaceId}/context/add-text`;
          body = { item_type: 'text', content: item.content };
        } else if (item.itemType === 'url') {
          endpoint = `${workspaceId}/context/add-link`;
          body = { item_type: 'url', content: item.content };
        }

        const response = await fetch(`/api/strategy/${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });

        if (!response.ok) {
          throw new Error('Failed to add context item');
        }

        const newItem = await response.json();
        setContextItems((prev) => [...prev, newItem]);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to add context item');
        throw err;
      }
    },
    [workspaceId]
  );

  // Delete context item
  const deleteItem = useCallback(
    async (itemId: string) => {
      if (!workspaceId) return;

      try {
        const response = await fetch(`/api/strategy/${workspaceId}/context/${itemId}`, {
          method: 'DELETE',
        });

        if (!response.ok) {
          throw new Error('Failed to delete context item');
        }

        setContextItems((prev) => prev.filter((item) => item.id !== itemId));
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete context item');
        throw err;
      }
    },
    [workspaceId]
  );

  return {
    contextItems,
    loading,
    error,
    addItem,
    deleteItem,
  };
}
