/**
 * TokenCounter Component
 * Displays token usage, costs, and budget status in real-time
 */

'use client';

import React, { useMemo } from 'react';
import {
  useTokenUsage,
  formatCost,
  formatTokens,
  getBudgetColor,
  getBudgetStatusText,
} from '@/lib/hooks/useTokenUsage';

interface TokenCounterProps {
  strategyId?: string;
  compact?: boolean; // Compact view for widgets
  showChart?: boolean; // Show visual budget breakdown
}

/**
 * Main TokenCounter component
 */
export function TokenCounter({
  strategyId,
  compact = false,
  showChart = true,
}: TokenCounterProps) {
  const { usage, isLoading, error, getDailyPercentage, getMonthlyPercentage } =
    useTokenUsage(strategyId);

  if (isLoading && !usage) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-6">
        <p className="text-center text-sm text-gray-600">Loading token usage...</p>
      </div>
    );
  }

  if (error && !usage) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4">
        <p className="text-sm font-medium text-red-900">Error loading token usage</p>
        <p className="mt-1 text-sm text-red-700">{error}</p>
      </div>
    );
  }

  if (!usage) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-6">
        <p className="text-center text-sm text-gray-600">No token usage data available</p>
      </div>
    );
  }

  const dailyPercentage = getDailyPercentage();
  const monthlyPercentage = getMonthlyPercentage();
  const dailyColor = getBudgetColor(dailyPercentage);
  const monthlyColor = getBudgetColor(monthlyPercentage);
  const dailyStatus = getBudgetStatusText(dailyPercentage, false);
  const monthlyStatus = getBudgetStatusText(monthlyPercentage, usage.budget_exceeded);

  if (compact) {
    return (
      <div className="space-y-3 rounded-lg border border-gray-200 bg-white p-4">
        <h3 className="text-sm font-semibold text-gray-900">Token Usage</h3>

        {/* Cost Summary */}
        <div className="space-y-1 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-gray-600">Estimated Cost</span>
            <span className="font-semibold text-gray-900">{formatCost(usage.estimated_cost)}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-600">Total Tokens</span>
            <span className="font-semibold text-gray-900">{formatTokens(usage.total_tokens)}</span>
          </div>
        </div>

        {/* Budget Status Indicator */}
        {usage.budget_warning && (
          <div className="rounded-md bg-yellow-50 p-2">
            <p className="text-xs font-medium text-yellow-900">⚠️ Budget Warning</p>
            <p className="text-xs text-yellow-700">{usage.estimated_cost.toFixed(2)}% of budget used</p>
          </div>
        )}

        {usage.budget_exceeded && (
          <div className="rounded-md bg-red-50 p-2">
            <p className="text-xs font-medium text-red-900">❌ Budget Exceeded</p>
            <p className="text-xs text-red-700">Please upgrade your plan or wait for reset</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="w-full space-y-6 rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      {/* Header */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Token & Cost Tracking</h2>
        <p className="mt-1 text-sm text-gray-600">Real-time usage monitoring and budget status</p>
      </div>

      {/* Cost Summary Cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-lg bg-gradient-to-br from-blue-50 to-blue-100 p-4">
          <p className="text-xs font-medium uppercase text-blue-700">Estimated Cost</p>
          <p className="mt-2 text-2xl font-bold text-blue-900">{formatCost(usage.estimated_cost)}</p>
          <p className="mt-1 text-xs text-blue-700">/month budget</p>
        </div>

        <div className="rounded-lg bg-gradient-to-br from-purple-50 to-purple-100 p-4">
          <p className="text-xs font-medium uppercase text-purple-700">Total Tokens</p>
          <p className="mt-2 text-2xl font-bold text-purple-900">{formatTokens(usage.total_tokens)}</p>
          <p className="mt-1 text-xs text-purple-700">{usage.calls_made} API calls</p>
        </div>

        <div className="rounded-lg bg-gradient-to-br from-green-50 to-green-100 p-4">
          <p className="text-xs font-medium uppercase text-green-700">Cache Hits</p>
          <p className="mt-2 text-2xl font-bold text-green-900">{usage.cache_hits}</p>
          <p className="mt-1 text-xs text-green-700">
            {usage.calls_made > 0
              ? Math.round((usage.cache_hits / usage.calls_made) * 100)
              : 0}
            % hit rate
          </p>
        </div>
      </div>

      {/* Daily Limit */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">Daily Limit</h3>
          <span
            className="inline-block rounded-full px-2 py-1 text-xs font-medium"
            style={{ backgroundColor: `${dailyColor}20`, color: dailyColor }}
          >
            {dailyStatus}
          </span>
        </div>
        <div className="space-y-1">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">
              {formatTokens(usage.daily_limit - usage.daily_remaining)} /{' '}
              {formatTokens(usage.daily_limit)}
            </span>
            <span className="font-semibold text-gray-900">{dailyPercentage}%</span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
            <div
              className="h-full transition-all duration-300"
              style={{
                width: `${dailyPercentage}%`,
                backgroundColor: dailyColor,
              }}
            />
          </div>
          <p className="text-xs text-gray-600">
            {formatTokens(usage.daily_remaining)} remaining
          </p>
        </div>
      </div>

      {/* Monthly Limit */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">Monthly Limit</h3>
          <span
            className="inline-block rounded-full px-2 py-1 text-xs font-medium"
            style={{ backgroundColor: `${monthlyColor}20`, color: monthlyColor }}
          >
            {monthlyStatus}
          </span>
        </div>
        <div className="space-y-1">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">
              {formatTokens(usage.monthly_limit - usage.monthly_remaining)} /{' '}
              {formatTokens(usage.monthly_limit)}
            </span>
            <span className="font-semibold text-gray-900">{monthlyPercentage}%</span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
            <div
              className="h-full transition-all duration-300"
              style={{
                width: `${monthlyPercentage}%`,
                backgroundColor: monthlyColor,
              }}
            />
          </div>
          <p className="text-xs text-gray-600">
            {formatTokens(usage.monthly_remaining)} remaining
          </p>
        </div>
      </div>

      {/* Agent Breakdown */}
      {usage.tokens_by_agent && Object.keys(usage.tokens_by_agent).length > 0 && (
        <div className="space-y-2 border-t border-gray-200 pt-4">
          <h3 className="text-sm font-semibold text-gray-900">Usage by Agent</h3>
          <div className="space-y-2">
            {Object.entries(usage.tokens_by_agent).map(([agent, tokens]) => {
              const cost = usage.cost_by_agent?.[agent] || 0;
              const percentage = ((tokens as number) / usage.total_tokens) * 100;
              return (
                <div key={agent} className="rounded-md bg-gray-50 p-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium text-gray-900">{agent}</span>
                    <span className="text-xs text-gray-600">
                      {formatTokens(tokens as number)} tokens • {formatCost(cost)}
                    </span>
                  </div>
                  <div className="mt-1 h-1 w-full overflow-hidden rounded-full bg-gray-200">
                    <div
                      className="h-full bg-blue-600"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <p className="mt-1 text-xs text-gray-600">{percentage.toFixed(1)}% of total</p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Budget Warnings */}
      {(usage.budget_warning || usage.budget_exceeded) && (
        <div
          className="rounded-lg border-l-4 p-4"
          style={{
            borderColor: usage.budget_exceeded ? '#ef4444' : '#f59e0b',
            backgroundColor: usage.budget_exceeded ? '#fef2f2' : '#fffbeb',
          }}
        >
          <p
            className="font-medium"
            style={{ color: usage.budget_exceeded ? '#991b1b' : '#92400e' }}
          >
            {usage.budget_exceeded ? '❌ Budget Exceeded' : '⚠️ Budget Warning'}
          </p>
          <p className="mt-1 text-sm" style={{ color: usage.budget_exceeded ? '#dc2626' : '#d97706' }}>
            {usage.budget_exceeded
              ? 'Your monthly token budget has been exceeded. Please upgrade your plan or wait for the monthly reset.'
              : `You have used ${monthlyPercentage}% of your monthly budget. Consider upgrading to a higher tier.`}
          </p>
        </div>
      )}

      {/* Info */}
      {!error && (
        <p className="text-xs text-gray-500">
          Last updated: {new Date().toLocaleTimeString()} • Auto-refresh every 5 seconds
        </p>
      )}
    </div>
  );
}

/**
 * Simple token display widget
 */
export function TokenWidget({ strategyId }: { strategyId?: string }) {
  const { usage } = useTokenUsage(strategyId);

  if (!usage) return null;

  return (
    <div className="flex items-center gap-2 rounded-md bg-gray-100 px-3 py-1 text-sm">
      <span className="font-medium text-gray-900">{formatTokens(usage.total_tokens)}</span>
      <span className="text-gray-600">•</span>
      <span className="text-gray-600">{formatCost(usage.estimated_cost)}</span>
    </div>
  );
}

/**
 * Budget indicator for header/navbar
 */
export function BudgetIndicator({ strategyId }: { strategyId?: string }) {
  const { usage, getMonthlyPercentage } = useTokenUsage(strategyId);

  if (!usage) return null;

  const percentage = getMonthlyPercentage();
  const status = getBudgetStatusText(percentage, usage.budget_exceeded);
  const color = getBudgetColor(percentage);

  return (
    <div
      className="flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium"
      style={{
        backgroundColor: `${color}20`,
        color: color,
      }}
    >
      <div className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
      {status}
    </div>
  );
}
