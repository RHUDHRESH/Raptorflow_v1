/**
 * useTokenUsage Hook
 * Manages token usage tracking and cost display
 */

import { useEffect, useState, useCallback } from 'react';
import { apiClient } from '@/lib/api-client';

export interface TokenUsageData {
  session_tokens: number;
  total_tokens: number;
  estimated_cost: number;
  calls_made: number;
  cache_hits: number;
  daily_limit: number;
  monthly_limit: number;
  daily_remaining: number;
  monthly_remaining: number;
  budget_exceeded: boolean;
  budget_warning: boolean;
  tokens_by_agent?: Record<string, number>;
  cost_by_agent?: Record<string, number>;
}

interface UseTokenUsageReturn {
  usage: TokenUsageData | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  getDailyPercentage: () => number;
  getMonthlyPercentage: () => number;
  getEstimatedTokensUntilBudget: () => number;
  getEstimatedTimeUntilBudget: () => string;
}

/**
 * useTokenUsage hook
 * Fetches and tracks token usage in real-time
 */
export function useTokenUsage(strategyId?: string, autoRefetch = true): UseTokenUsageReturn {
  const [usage, setUsage] = useState<TokenUsageData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch token usage from backend
   */
  const fetchUsage = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.getTokenUsage(strategyId);

      if (response?.error) {
        throw new Error(response.error.message);
      }

      if (response?.data) {
        // Ensure all fields exist
        const usageData: TokenUsageData = {
          session_tokens: response.data.session_tokens || 0,
          total_tokens: response.data.total_tokens || 0,
          estimated_cost: response.data.estimated_cost || 0,
          calls_made: response.data.calls_made || 0,
          cache_hits: response.data.cache_hits || 0,
          daily_limit: response.data.daily_limit || 50000,
          monthly_limit: response.data.monthly_limit || 1000000,
          daily_remaining: response.data.daily_remaining || 50000,
          monthly_remaining: response.data.monthly_remaining || 1000000,
          budget_exceeded: response.data.budget_exceeded || false,
          budget_warning: (response.data.estimated_cost || 0) > 12,
          tokens_by_agent: response.data.tokens_by_agent || {},
          cost_by_agent: response.data.cost_by_agent || {},
        };
        setUsage(usageData);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch token usage';
      setError(message);
      console.error('Token usage error:', message);
    } finally {
      setIsLoading(false);
    }
  }, [strategyId]);

  /**
   * Auto-refresh token usage every 5 seconds
   */
  useEffect(() => {
    // Initial fetch
    fetchUsage();

    if (!autoRefetch) return;

    // Refresh every 5 seconds
    const interval = setInterval(fetchUsage, 5000);

    return () => clearInterval(interval);
  }, [strategyId, autoRefetch, fetchUsage]);

  /**
   * Get daily usage percentage
   */
  const getDailyPercentage = useCallback(() => {
    if (!usage) return 0;
    const used = usage.daily_limit - usage.daily_remaining;
    return Math.round((used / usage.daily_limit) * 100);
  }, [usage]);

  /**
   * Get monthly usage percentage
   */
  const getMonthlyPercentage = useCallback(() => {
    if (!usage) return 0;
    const used = usage.monthly_limit - usage.monthly_remaining;
    return Math.round((used / usage.monthly_limit) * 100);
  }, [usage]);

  /**
   * Estimate tokens remaining until budget exhausted
   */
  const getEstimatedTokensUntilBudget = useCallback(() => {
    if (!usage) return 0;
    // At $15/month budget with ~$0.001 per 1000 tokens
    // Each remaining dollar = ~1000 tokens
    const dollarRemaining = Math.max(0, 15 - usage.estimated_cost);
    return Math.round(dollarRemaining * 1000);
  }, [usage]);

  /**
   * Estimate time until budget is exceeded (based on current usage rate)
   */
  const getEstimatedTimeUntilBudget = useCallback(() => {
    if (!usage || usage.calls_made === 0) return 'Unknown';

    const tokensRemaining = getEstimatedTokensUntilBudget();
    const avgTokensPerCall = Math.round(usage.total_tokens / usage.calls_made);

    if (avgTokensPerCall === 0) return 'Unknown';

    const callsRemaining = Math.floor(tokensRemaining / avgTokensPerCall);

    if (callsRemaining < 1) return 'Budget exceeded';
    if (callsRemaining < 5) return `~${callsRemaining} call${callsRemaining === 1 ? '' : 's'}`;
    if (callsRemaining < 50) return `~${Math.round(callsRemaining / 5)} hours`;
    if (callsRemaining < 500) return `~${Math.round(callsRemaining / 100)} days`;

    return 'Plenty of budget';
  }, [usage, getEstimatedTokensUntilBudget]);

  return {
    usage,
    isLoading,
    error,
    refetch: fetchUsage,
    getDailyPercentage,
    getMonthlyPercentage,
    getEstimatedTokensUntilBudget,
    getEstimatedTimeUntilBudget,
  };
}

/**
 * Hook to get budget status
 */
export function useBudgetStatus() {
  const [budgetStatus, setBudgetStatus] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchBudgetStatus = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.getBudgetStatus();

      if (response?.error) {
        throw new Error(response.error.message);
      }

      setBudgetStatus(response?.data || null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch budget status';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchBudgetStatus();

    // Refresh every 30 seconds
    const interval = setInterval(fetchBudgetStatus, 30000);

    return () => clearInterval(interval);
  }, [fetchBudgetStatus]);

  return {
    budgetStatus,
    isLoading,
    error,
    refetch: fetchBudgetStatus,
  };
}

/**
 * Utility to format cost as currency
 */
export function formatCost(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}

/**
 * Utility to format token count with commas
 */
export function formatTokens(count: number): string {
  return count.toLocaleString();
}

/**
 * Utility to get color for budget warning
 */
export function getBudgetColor(percentage: number): string {
  if (percentage > 90) return '#ef4444'; // red
  if (percentage > 70) return '#f97316'; // orange
  if (percentage > 50) return '#eab308'; // yellow
  return '#22c55e'; // green
}

/**
 * Utility to get budget status text
 */
export function getBudgetStatusText(percentage: number, exceeded: boolean): string {
  if (exceeded) return 'Budget Exceeded';
  if (percentage > 90) return 'Critical';
  if (percentage > 70) return 'High';
  if (percentage > 50) return 'Medium';
  return 'Low';
}
