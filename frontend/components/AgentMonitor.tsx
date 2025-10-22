/**
 * AgentMonitor Component
 * Displays real-time agent analysis progress and event log
 */

'use client';

import React, { useMemo } from 'react';
import { useAgent, useAnalysisSummary, useEventDisplay } from '@/lib/hooks/useAgent';

interface AgentMonitorProps {
  strategyId: string;
  onAnalysisComplete?: () => void;
  compact?: boolean; // Compact view without event log
}

/**
 * Main AgentMonitor component
 */
export function AgentMonitor({
  strategyId,
  onAnalysisComplete,
  compact = false,
}: AgentMonitorProps) {
  const {
    isRunning,
    events,
    error,
    progress,
    currentAgent,
    currentStep,
    startAnalysis,
    cancel,
    clearEvents,
  } = useAgent();

  const summary = useAnalysisSummary(events);
  const displayText = useEventDisplay(events);

  // Get color for progress bar based on percentage
  const getProgressColor = (pct: number) => {
    if (pct >= 90) return '#10b981'; // green
    if (pct >= 70) return '#3b82f6'; // blue
    if (pct >= 40) return '#f59e0b'; // amber
    return '#ef4444'; // red
  };

  const handleStartAnalysis = async () => {
    clearEvents();
    try {
      await startAnalysis(strategyId);
      onAnalysisComplete?.();
    } catch (err) {
      console.error('Failed to start analysis:', err);
    }
  };

  return (
    <div className="w-full space-y-4 rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Agent Monitor</h2>
          <p className="mt-1 text-sm text-gray-600">
            {isRunning ? 'Analysis in progress...' : 'Ready to analyze'}
          </p>
        </div>
        <div className="flex gap-2">
          {isRunning && (
            <button
              onClick={cancel}
              className="rounded-md bg-red-50 px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-100"
            >
              Cancel
            </button>
          )}
          {!isRunning && events.length > 0 && (
            <button
              onClick={clearEvents}
              className="rounded-md bg-gray-50 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
            >
              Clear
            </button>
          )}
          {!isRunning && (
            <button
              onClick={handleStartAnalysis}
              disabled={!strategyId}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              Start Analysis
            </button>
          )}
        </div>
      </div>

      {/* Progress Section */}
      {(isRunning || events.length > 0) && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Progress</span>
            <span className="text-sm text-gray-600">{progress}%</span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
            <div
              className="h-full transition-all duration-300 ease-out"
              style={{
                width: `${progress}%`,
                backgroundColor: getProgressColor(progress),
              }}
            />
          </div>
        </div>
      )}

      {/* Current Status */}
      {isRunning && (
        <div className="space-y-2 rounded-md bg-blue-50 p-3">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-blue-600 animate-pulse" />
            <span className="text-sm font-medium text-blue-900">
              {currentAgent && currentStep ? `${currentAgent} • ${currentStep}` : 'Initializing...'}
            </span>
          </div>
          {currentAgent && (
            <p className="text-xs text-blue-800">
              Agent: <span className="font-semibold">{currentAgent}</span>
            </p>
          )}
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="rounded-md bg-red-50 p-3">
          <p className="text-sm font-medium text-red-900">Error</p>
          <p className="mt-1 text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Summary Stats */}
      {events.length > 0 && (
        <div className="grid grid-cols-4 gap-2 text-center text-sm">
          <div className="rounded-md bg-gray-50 p-2">
            <p className="font-semibold text-gray-900">{summary.totalEvents}</p>
            <p className="text-xs text-gray-600">Events</p>
          </div>
          <div className="rounded-md bg-gray-50 p-2">
            <p className="font-semibold text-gray-900">{summary.thinkingEvents}</p>
            <p className="text-xs text-gray-600">Thinking</p>
          </div>
          <div className="rounded-md bg-gray-50 p-2">
            <p className="font-semibold text-gray-900">{summary.toolCalls}</p>
            <p className="text-xs text-gray-600">Tools</p>
          </div>
          <div className="rounded-md bg-gray-50 p-2">
            <p className="font-semibold text-gray-900">{summary.errorCount}</p>
            <p className="text-xs text-gray-600">Errors</p>
          </div>
        </div>
      )}

      {/* Event Log (not shown in compact mode) */}
      {!compact && events.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-gray-900">Event Log</h3>
          <div className="max-h-64 overflow-y-auto rounded-md bg-gray-50 p-3">
            <div className="space-y-2 font-mono text-xs text-gray-700 whitespace-pre-wrap">
              {displayText || (
                <p className="text-gray-500 italic">No displayable events yet...</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Completion Message */}
      {!isRunning && summary.isComplete && events.length > 0 && (
        <div className="rounded-md bg-green-50 p-3">
          <p className="text-sm font-medium text-green-900">✓ Analysis Complete</p>
          <p className="mt-1 text-xs text-green-700">
            Processed {summary.totalEvents} events in {summary.thinkingEvents} thinking steps
          </p>
        </div>
      )}
    </div>
  );
}

/**
 * Compact Agent Monitor for sidebar or widget display
 */
export function AgentMonitorCompact({ strategyId }: { strategyId: string }) {
  const { isRunning, progress, currentAgent, events } = useAgent();

  const summary = useAnalysisSummary(events);

  return (
    <div className="space-y-2 rounded-lg border border-gray-200 bg-white p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900">Agent Status</h3>
        {isRunning && <div className="h-2 w-2 rounded-full bg-blue-600 animate-pulse" />}
      </div>

      {isRunning ? (
        <>
          <p className="text-xs text-gray-600">{currentAgent || 'Initializing...'}</p>
          <div className="h-1 w-full overflow-hidden rounded-full bg-gray-200">
            <div
              className="h-full bg-blue-600 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-gray-500">{progress}% complete</p>
        </>
      ) : summary.isComplete && events.length > 0 ? (
        <p className="text-xs text-green-700">✓ Analysis complete ({summary.totalEvents} events)</p>
      ) : (
        <p className="text-xs text-gray-500">No active analysis</p>
      )}
    </div>
  );
}

/**
 * Event List Component for detailed event view
 */
export function EventList({ events }: { events: any[] }) {
  const eventsByType = useMemo(() => {
    const grouped: Record<string, any[]> = {};
    events.forEach((event) => {
      if (!grouped[event.type]) {
        grouped[event.type] = [];
      }
      grouped[event.type].push(event);
    });
    return grouped;
  }, [events]);

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'start':
        return '▶️';
      case 'thinking':
        return '💭';
      case 'progress':
        return '⏳';
      case 'tool_call':
        return '🔧';
      case 'result':
        return '✓';
      case 'error':
        return '❌';
      case 'done':
        return '🏁';
      default:
        return '•';
    }
  };

  return (
    <div className="space-y-2">
      {Object.entries(eventsByType).map(([type, typeEvents]) => (
        <div key={type} className="rounded-md bg-gray-50 p-2">
          <div className="text-xs font-semibold text-gray-700">
            {getEventIcon(type)} {type.toUpperCase()} ({typeEvents.length})
          </div>
          <div className="mt-1 space-y-1 text-xs text-gray-600">
            {typeEvents.slice(0, 3).map((event, idx) => (
              <div key={idx} className="truncate text-gray-600">
                {typeof event.data === 'string'
                  ? event.data.slice(0, 100)
                  : JSON.stringify(event.data).slice(0, 100)}
              </div>
            ))}
            {typeEvents.length > 3 && (
              <div className="italic text-gray-500">+{typeEvents.length - 3} more</div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
