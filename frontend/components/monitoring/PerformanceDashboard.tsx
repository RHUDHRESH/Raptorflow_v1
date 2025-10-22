/**
 * Performance Dashboard Component
 * Displays real-time performance metrics and Web Vitals
 * Shows charts, trends, and health status
 */

'use client';

import React, { useEffect, useState, memo } from 'react';
import { getWebVitalsMonitor, CoreWebVitals, VITAL_THRESHOLDS } from '@/lib/web-vitals';
import { getMetricsCollector, MetricReport, AggregatedMetric } from '@/lib/performance-metrics';

interface DashboardState {
  vitals: CoreWebVitals;
  metrics: MetricReport | null;
  isExpanded: boolean;
}

/**
 * Vital Card Component - Displays individual vital with rating
 */
const VitalCard = memo(
  ({
    name,
    value,
    unit,
    threshold,
  }: {
    name: string;
    value?: number;
    unit: string;
    threshold: { good: number; poor: number };
  }) => {
    const getRating = (val?: number) => {
      if (!val) return 'unknown';
      if (val <= threshold.good) return 'good';
      if (val <= threshold.poor) return 'needs-improvement';
      return 'poor';
    };

    const getRatingColor = (rating: string) => {
      switch (rating) {
        case 'good':
          return 'text-green-600 bg-green-50';
        case 'needs-improvement':
          return 'text-yellow-600 bg-yellow-50';
        case 'poor':
          return 'text-red-600 bg-red-50';
        default:
          return 'text-gray-600 bg-gray-50';
      }
    };

    const rating = getRating(value);
    const ratingColor = getRatingColor(rating);

    return (
      <div className={`p-4 rounded-lg border border-[#D7C9AE] ${ratingColor}`}>
        <h3 className="text-sm font-semibold text-[#2D2D2D] mb-2">{name}</h3>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold">{value?.toFixed(value < 10 ? 2 : 0) || '—'}</span>
          <span className="text-xs text-[#2D2D2D]/60">{unit}</span>
        </div>
        <p className="text-xs mt-2 capitalize">{rating === 'unknown' ? 'Measuring...' : rating}</p>
      </div>
    );
  }
);

VitalCard.displayName = 'VitalCard';

/**
 * Metric Row Component - Shows aggregated metric stats
 */
const MetricRow = memo(
  ({ metric, name }: { metric: AggregatedMetric; name: string }) => (
    <div className="py-2 border-b border-[#D7C9AE]/30 last:border-0">
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm font-medium text-[#2D2D2D]">{name}</span>
        <span className="text-xs text-[#A68763] font-semibold">{metric.count} calls</span>
      </div>
      <div className="flex items-center gap-4 text-xs text-[#2D2D2D]/70">
        <div>
          <span className="font-semibold">Min:</span> {metric.min.toFixed(2)}ms
        </div>
        <div>
          <span className="font-semibold">Avg:</span> {metric.mean.toFixed(2)}ms
        </div>
        <div>
          <span className="font-semibold">Max:</span> {metric.max.toFixed(2)}ms
        </div>
        <div>
          <span className="font-semibold">P95:</span> {metric.p95.toFixed(2)}ms
        </div>
      </div>
    </div>
  )
);

MetricRow.displayName = 'MetricRow';

/**
 * Main Performance Dashboard Component
 */
const PerformanceDashboardComponent = () => {
  const [state, setState] = useState<DashboardState>({
    vitals: {},
    metrics: null,
    isExpanded: false,
  });

  const vitalsMonitor = getWebVitalsMonitor();
  const metricsCollector = getMetricsCollector();

  useEffect(() => {
    // Subscribe to vital changes
    const unsubscribe = vitalsMonitor.onMetrics((metrics) => {
      setState((prev) => ({
        ...prev,
        vitals: metrics.vitals,
      }));
    });

    // Update metrics every 5 seconds
    const metricsInterval = setInterval(() => {
      const report = metricsCollector.getReport();
      setState((prev) => ({
        ...prev,
        metrics: report,
      }));
    }, 5000);

    // Initial update
    const initial = metricsCollector.getReport();
    setState((prev) => ({
      ...prev,
      metrics: initial,
      vitals: vitalsMonitor.getVitals(),
    }));

    return () => {
      unsubscribe?.();
      clearInterval(metricsInterval);
    };
  }, []);

  const apiMetrics = state.metrics?.metrics
    ? Object.entries(state.metrics.metrics)
        .filter(([name]) => name.startsWith('api:'))
        .slice(0, 5)
    : [];

  const componentMetrics = state.metrics?.metrics
    ? Object.entries(state.metrics.metrics)
        .filter(([name]) => name.startsWith('component:'))
        .slice(0, 5)
    : [];

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Minimized View */}
      {!state.isExpanded && (
        <button
          onClick={() => setState((prev) => ({ ...prev, isExpanded: true }))}
          className="px-4 py-2 bg-[#A68763] text-white rounded-lg shadow-lg hover:bg-[#A68763]/90 transition-colors font-medium text-sm"
        >
          📊 Performance
        </button>
      )}

      {/* Expanded View */}
      {state.isExpanded && (
        <div className="w-96 max-h-[90vh] overflow-y-auto bg-white rounded-lg shadow-2xl border border-[#D7C9AE] flex flex-col">
          {/* Header */}
          <div className="sticky top-0 bg-gradient-to-r from-[#A68763] to-[#8B6F47] text-white p-4 flex items-center justify-between">
            <h2 className="font-bold">Performance Monitor</h2>
            <button
              onClick={() => setState((prev) => ({ ...prev, isExpanded: false }))}
              className="text-xl hover:opacity-70 transition-opacity"
            >
              ✕
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {/* Core Web Vitals Section */}
            <div>
              <h3 className="text-sm font-semibold text-[#2D2D2D] mb-3">Core Web Vitals</h3>
              <div className="grid grid-cols-2 gap-2">
                <VitalCard
                  name="LCP"
                  value={state.vitals.LCP}
                  unit="ms"
                  threshold={VITAL_THRESHOLDS.LCP}
                />
                <VitalCard
                  name="FID"
                  value={state.vitals.FID}
                  unit="ms"
                  threshold={VITAL_THRESHOLDS.FID}
                />
                <VitalCard
                  name="CLS"
                  value={state.vitals.CLS}
                  unit=""
                  threshold={VITAL_THRESHOLDS.CLS}
                />
                <VitalCard
                  name="FCP"
                  value={state.vitals.FCP}
                  unit="ms"
                  threshold={VITAL_THRESHOLDS.FCP}
                />
              </div>
            </div>

            {/* API Metrics Section */}
            {apiMetrics.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-[#2D2D2D] mb-3">API Performance</h3>
                <div className="bg-gray-50 rounded-lg p-3 space-y-2">
                  {apiMetrics.map(([name, metric]) => (
                    <MetricRow
                      key={name}
                      name={name.replace('api:', '')}
                      metric={metric as AggregatedMetric}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Component Metrics Section */}
            {componentMetrics.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-[#2D2D2D] mb-3">Component Renders</h3>
                <div className="bg-gray-50 rounded-lg p-3 space-y-2">
                  {componentMetrics.map(([name, metric]) => (
                    <MetricRow
                      key={name}
                      name={name.replace('component:', '')}
                      metric={metric as AggregatedMetric}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Summary Stats */}
            {state.metrics && (
              <div className="bg-[#EAE0D2] rounded-lg p-3">
                <h3 className="text-sm font-semibold text-[#2D2D2D] mb-2">Session Summary</h3>
                <div className="grid grid-cols-2 gap-2 text-xs text-[#2D2D2D]/70">
                  <div>
                    <span className="font-semibold">Total Events:</span>
                    {state.metrics.totalEvents}
                  </div>
                  <div>
                    <span className="font-semibold">Duration:</span>
                    {(state.metrics.periodMs / 1000).toFixed(1)}s
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="sticky bottom-0 bg-gray-50 border-t border-[#D7C9AE] p-3 flex gap-2">
            <button
              onClick={() => metricsCollector.clear()}
              className="flex-1 px-3 py-1 text-xs bg-[#D7C9AE] text-[#2D2D2D] rounded hover:bg-[#D7C9AE]/80 transition-colors"
            >
              Clear
            </button>
            <button
              onClick={() => {
                const json = metricsCollector.export();
                const blob = new Blob([json], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `metrics-${Date.now()}.json`;
                a.click();
                URL.revokeObjectURL(url);
              }}
              className="flex-1 px-3 py-1 text-xs bg-[#A68763] text-white rounded hover:bg-[#A68763]/90 transition-colors"
            >
              Export
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

PerformanceDashboardComponent.displayName = 'PerformanceDashboard';

export default memo(PerformanceDashboardComponent);
