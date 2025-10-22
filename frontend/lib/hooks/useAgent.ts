/**
 * useAgent Hook
 * Manages agent analysis streaming and event handling
 */

import { useCallback, useRef, useState, useEffect } from 'react';
import { apiClient, AgentEvent } from '@/lib/api-client';

interface UseAgentState {
  isRunning: boolean;
  events: AgentEvent[];
  error: string | null;
  progress: number; // 0-100
  currentAgent: string | null;
  currentStep: string | null;
}

interface UseAgentReturn extends UseAgentState {
  startAnalysis: (strategyId: string) => Promise<void>;
  cancel: () => void;
  clearEvents: () => void;
  getLastResult: () => AgentEvent | null;
  getEventsByType: (type: AgentEvent['type']) => AgentEvent[];
}

/**
 * useAgent hook
 * Handles agent analysis streaming and real-time updates
 */
export function useAgent(): UseAgentReturn {
  const [isRunning, setIsRunning] = useState(false);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);
  const eventCounterRef = useRef(0);

  /**
   * Start analysis and stream events
   */
  const startAnalysis = useCallback(
    async (strategyId: string) => {
      setIsRunning(true);
      setError(null);
      setEvents([]);
      setProgress(0);
      eventCounterRef.current = 0;

      try {
        // First, submit the analysis request
        const submitResponse = await apiClient.submitAnalysis(strategyId, {
          aisasPosition: 3,
          contextSummary: 'Analysis initiated',
        });

        if (submitResponse?.error) {
          throw new Error(submitResponse.error.message);
        }

        if (!submitResponse?.data?.analysis_id) {
          throw new Error('Failed to start analysis');
        }

        console.log('✓ Analysis started:', submitResponse.data.analysis_id);

        // Then, stream the events
        const eventGenerator = apiClient.streamAnalysis(strategyId);

        for await (const event of eventGenerator) {
          if (abortControllerRef.current?.signal.aborted) {
            console.log('Analysis cancelled');
            break;
          }

          // Add timestamp if missing
          const agentEvent: AgentEvent = {
            ...event,
            timestamp: event.timestamp || Date.now(),
          };

          // Update state
          setEvents((prev) => [...prev, agentEvent]);
          eventCounterRef.current++;

          // Update progress and current agent/step
          if (event.agent) {
            setCurrentAgent(event.agent);
          }
          if (event.step) {
            setCurrentStep(`Step ${event.step}`);
          }

          // Update progress (rough estimate)
          if (event.type === 'thinking' || event.type === 'progress') {
            setProgress((prev) => Math.min(prev + 5, 95));
          } else if (event.type === 'result') {
            setProgress(90);
          } else if (event.type === 'done') {
            setProgress(100);
          }

          // Handle errors
          if (event.type === 'error') {
            setError(event.data?.message || 'Analysis error');
          }

          // Handle completion
          if (event.type === 'done') {
            console.log('✓ Analysis completed');
            setIsRunning(false);
          }
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Analysis failed';
        console.error('❌ Analysis error:', message);
        setError(message);
        setIsRunning(false);
      }
    },
    []
  );

  /**
   * Cancel ongoing analysis
   */
  const cancel = useCallback(() => {
    abortControllerRef.current?.abort();
    setIsRunning(false);
    setError('Analysis cancelled by user');
    console.log('Analysis cancelled');
  }, []);

  /**
   * Clear event history
   */
  const clearEvents = useCallback(() => {
    setEvents([]);
    setProgress(0);
    setCurrentAgent(null);
    setCurrentStep(null);
    setError(null);
    eventCounterRef.current = 0;
  }, []);

  /**
   * Get the last event
   */
  const getLastResult = useCallback((): AgentEvent | null => {
    if (events.length === 0) return null;
    return events[events.length - 1];
  }, [events]);

  /**
   * Get all events of a specific type
   */
  const getEventsByType = useCallback(
    (type: AgentEvent['type']): AgentEvent[] => {
      return events.filter((event) => event.type === type);
    },
    [events]
  );

  // Initialize abort controller
  useEffect(() => {
    abortControllerRef.current = new AbortController();
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  return {
    isRunning,
    events,
    error,
    progress,
    currentAgent,
    currentStep,
    startAnalysis,
    cancel,
    clearEvents,
    getLastResult,
    getEventsByType,
  };
}

/**
 * Hook to get analysis summary from events
 */
export function useAnalysisSummary(events: AgentEvent[]) {
  const summary = {
    totalEvents: events.length,
    thinkingEvents: events.filter((e) => e.type === 'thinking').length,
    toolCalls: events.filter((e) => e.type === 'tool_call').length,
    resultEvents: events.filter((e) => e.type === 'result').length,
    errorCount: events.filter((e) => e.type === 'error').length,
    lastEvent: events[events.length - 1] || null,
    isComplete: events.some((e) => e.type === 'done'),
  };

  return summary;
}

/**
 * Hook to get formatted event display text
 */
export function useEventDisplay(events: AgentEvent[]) {
  const displayText = events
    .filter((e) => e.type === 'result' || e.type === 'thinking')
    .map((e) => {
      const text = typeof e.data === 'string' ? e.data : e.data?.text || '';
      return `[${e.agent || 'Agent'}] ${text}`;
    })
    .join('\n\n');

  return displayText;
}
