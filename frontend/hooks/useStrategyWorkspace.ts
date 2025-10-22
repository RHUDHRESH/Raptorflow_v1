/**
 * useStrategyWorkspace Hook
 * Manages strategy workspace state and API interactions
 */

'use client';

import { useState, useEffect } from 'react';

interface Workspace {
  id: string;
  businessId: string;
  name: string;
  status: 'context_intake' | 'analyzing' | 'ready_for_moves';
  contextProcessed: boolean;
  jtbdsExtracted: boolean;
  icpsBuilt: boolean;
  channelsMapped: boolean;
  explanationsGenerated: boolean;
  createdAt: string;
  updatedAt: string;
}

export function useStrategyWorkspace(workspaceId: string) {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWorkspace = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/strategy/${workspaceId}`);

        if (!response.ok) {
          throw new Error(`Failed to fetch workspace: ${response.statusText}`);
        }

        const data = await response.json();
        setWorkspace(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load workspace');
        setWorkspace(null);
      } finally {
        setLoading(false);
      }
    };

    if (workspaceId) {
      fetchWorkspace();
    }
  }, [workspaceId]);

  return { workspace, loading, error };
}
