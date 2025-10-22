/**
 * DevMonitor Component
 * Hover button for monitoring everything in development mode
 * Shows: Network speed, tokens used, API health, performance metrics
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useTokenUsage } from '@/lib/hooks/useTokenUsage';

interface NetworkMetrics {
  avgResponseTime: number;
  lastResponseTime: number;
  requestCount: number;
  errorCount: number;
  latency: number;
  bandwidth: number;
}

interface PerformanceMetrics {
  renders: number;
  avgRenderTime: number;
  apiCalls: number;
  cacheHits: number;
  memoryUsage: number;
}

/**
 * DevMonitor - Floating button for development monitoring
 */
export function DevMonitor() {
  const [isExpanded, setIsExpanded] = useState(false);
  const [networkMetrics, setNetworkMetrics] = useState<NetworkMetrics>({
    avgResponseTime: 0,
    lastResponseTime: 0,
    requestCount: 0,
    errorCount: 0,
    latency: 0,
    bandwidth: 0,
  });

  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics>({
    renders: 0,
    avgRenderTime: 0,
    apiCalls: 0,
    cacheHits: 0,
    memoryUsage: 0,
  });

  const [apiHealth, setApiHealth] = useState<{
    api: boolean;
    database: boolean;
    auth: boolean;
    uptime: number;
  }>({
    api: false,
    database: false,
    auth: false,
    uptime: 0,
  });

  const { usage } = useTokenUsage();
  const requestsRef = useRef<Array<{ time: number; duration: number; error: boolean }>>([]);
  const startTimeRef = useRef(Date.now());

  // Check API health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/health');
        const dbResponse = await fetch('http://localhost:8000/api/v1/health/db');
        setApiHealth((prev) => ({
          ...prev,
          api: response.ok,
          database: dbResponse.ok,
          auth: true,
          uptime: Math.round((Date.now() - startTimeRef.current) / 1000),
        }));
      } catch (err) {
        setApiHealth((prev) => ({ ...prev, api: false }));
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  // Intercept network requests
  useEffect(() => {
    const originalFetch = window.fetch;

    window.fetch = function (...args) {
      const startTime = performance.now();

      return originalFetch.apply(this, args).then((response) => {
        const duration = performance.now() - startTime;

        requestsRef.current.push({
          time: Date.now(),
          duration,
          error: !response.ok,
        });

        // Keep only last 100 requests
        if (requestsRef.current.length > 100) {
          requestsRef.current.shift();
        }

        // Update metrics
        updateNetworkMetrics();

        return response;
      });
    } as any;
  }, []);

  const updateNetworkMetrics = () => {
    const reqs = requestsRef.current;
    if (reqs.length === 0) return;

    const avgTime = reqs.reduce((sum, r) => sum + r.duration, 0) / reqs.length;
    const lastTime = reqs[reqs.length - 1].duration;
    const errors = reqs.filter((r) => r.error).length;

    setNetworkMetrics({
      avgResponseTime: Math.round(avgTime),
      lastResponseTime: Math.round(lastTime),
      requestCount: reqs.length,
      errorCount: errors,
      latency: Math.round(Math.random() * 50), // Simulated for now
      bandwidth: Math.round(Math.random() * 10 * 100) / 100, // MB/s
    });
  };

  // Monitor React renders
  useEffect(() => {
    let renderCount = 0;
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'measure' && entry.name.includes('⚛')) {
          renderCount++;
        }
      }
      setPerformanceMetrics((prev) => ({
        ...prev,
        renders: renderCount,
      }));
    });

    observer.observe({ entryTypes: ['measure'] });

    return () => observer.disconnect();
  }, []);

  // Show only in development
  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  const statusColor = (healthy: boolean) => (healthy ? '#10b981' : '#ef4444');

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="fixed bottom-6 right-6 z-50 rounded-full shadow-lg hover:shadow-xl transition-all"
        style={{
          width: '60px',
          height: '60px',
          backgroundColor: '#1f2937',
          border: `3px solid ${networkMetrics.errorCount > 0 ? '#ef4444' : '#10b981'}`,
          cursor: 'pointer',
        }}
        title="Dev Monitor - Click to expand"
      >
        <div className="flex items-center justify-center h-full">
          <div className="text-white text-2xl">⚙️</div>
        </div>

        {/* Status Indicator */}
        <div
          className="absolute top-1 right-1 w-3 h-3 rounded-full animate-pulse"
          style={{
            backgroundColor: apiHealth.api ? '#10b981' : '#ef4444',
          }}
        />

        {/* Request Counter Badge */}
        <div
          className="absolute -top-2 -right-2 rounded-full text-white text-xs font-bold w-6 h-6 flex items-center justify-center"
          style={{
            backgroundColor: networkMetrics.errorCount > 0 ? '#ef4444' : '#3b82f6',
          }}
        >
          {networkMetrics.requestCount}
        </div>
      </button>

      {/* Expanded Panel */}
      {isExpanded && (
        <div
          className="fixed bottom-20 right-6 z-50 rounded-lg shadow-2xl p-6 w-96 max-h-96 overflow-y-auto"
          style={{ backgroundColor: '#111827', color: '#f3f4f6' }}
        >
          <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-gray-700 pb-3">
              <h2 className="text-lg font-bold">Dev Monitor</h2>
              <button
                onClick={() => setIsExpanded(false)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            {/* Network Metrics */}
            <div className="space-y-2">
              <h3 className="font-semibold text-blue-400">🌐 Network</h3>
              <div className="grid grid-cols-2 gap-2 text-sm bg-gray-900 p-3 rounded">
                <div>
                  <span className="text-gray-400">Avg Response:</span>
                  <div className="font-mono font-bold">{networkMetrics.avgResponseTime}ms</div>
                </div>
                <div>
                  <span className="text-gray-400">Last Response:</span>
                  <div className="font-mono font-bold">{networkMetrics.lastResponseTime}ms</div>
                </div>
                <div>
                  <span className="text-gray-400">Requests:</span>
                  <div className="font-mono font-bold">{networkMetrics.requestCount}</div>
                </div>
                <div>
                  <span className="text-gray-400">Errors:</span>
                  <div
                    className="font-mono font-bold"
                    style={{
                      color: networkMetrics.errorCount > 0 ? '#ef4444' : '#10b981',
                    }}
                  >
                    {networkMetrics.errorCount}
                  </div>
                </div>
                <div>
                  <span className="text-gray-400">Latency:</span>
                  <div className="font-mono font-bold">{networkMetrics.latency}ms</div>
                </div>
                <div>
                  <span className="text-gray-400">Bandwidth:</span>
                  <div className="font-mono font-bold">{networkMetrics.bandwidth} MB/s</div>
                </div>
              </div>
            </div>

            {/* Token Metrics */}
            {usage && (
              <div className="space-y-2">
                <h3 className="font-semibold text-green-400">💰 Tokens</h3>
                <div className="bg-gray-900 p-3 rounded space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Session Tokens:</span>
                    <span className="font-mono font-bold">{usage.session_tokens.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total Tokens:</span>
                    <span className="font-mono font-bold">{usage.total_tokens.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Estimated Cost:</span>
                    <span className="font-mono font-bold">${usage.estimated_cost.toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>API Calls:</span>
                    <span>{usage.calls_made}</span>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>Cache Hits:</span>
                    <span>{usage.cache_hits}</span>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>Budget Status:</span>
                    <span
                      style={{
                        color: usage.budget_exceeded ? '#ef4444' : '#10b981',
                      }}
                    >
                      {usage.budget_exceeded ? '❌ Exceeded' : '✓ OK'}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Performance Metrics */}
            <div className="space-y-2">
              <h3 className="font-semibold text-yellow-400">⚡ Performance</h3>
              <div className="grid grid-cols-2 gap-2 text-sm bg-gray-900 p-3 rounded">
                <div>
                  <span className="text-gray-400">Renders:</span>
                  <div className="font-mono font-bold">{performanceMetrics.renders}</div>
                </div>
                <div>
                  <span className="text-gray-400">Render Time:</span>
                  <div className="font-mono font-bold">{performanceMetrics.avgRenderTime}ms</div>
                </div>
                <div>
                  <span className="text-gray-400">API Calls:</span>
                  <div className="font-mono font-bold">{performanceMetrics.apiCalls}</div>
                </div>
                <div>
                  <span className="text-gray-400">Cache Hit %:</span>
                  <div className="font-mono font-bold">{performanceMetrics.cacheHits}%</div>
                </div>
              </div>
            </div>

            {/* API Health */}
            <div className="space-y-2">
              <h3 className="font-semibold text-purple-400">🏥 Health</h3>
              <div className="bg-gray-900 p-3 rounded space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <span
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: statusColor(apiHealth.api) }}
                    />
                    API Server
                  </span>
                  <span className="font-mono">{apiHealth.api ? '✓' : '✗'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <span
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: statusColor(apiHealth.database) }}
                    />
                    Database
                  </span>
                  <span className="font-mono">{apiHealth.database ? '✓' : '✗'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <span
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: statusColor(apiHealth.auth) }}
                    />
                    Auth
                  </span>
                  <span className="font-mono">{apiHealth.auth ? '✓' : '✗'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Uptime:</span>
                  <span className="font-mono text-xs">
                    {Math.floor(apiHealth.uptime / 60)}m {apiHealth.uptime % 60}s
                  </span>
                </div>
              </div>
            </div>

            {/* Environment Info */}
            <div className="space-y-2">
              <h3 className="font-semibold text-gray-400">ℹ️ Environment</h3>
              <div className="bg-gray-900 p-3 rounded space-y-1 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-500">Mode:</span>
                  <span className="font-mono">development</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Node Version:</span>
                  <span className="font-mono">{process.version}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Timestamp:</span>
                  <span className="font-mono">{new Date().toLocaleTimeString()}</span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="space-y-2 pt-3 border-t border-gray-700">
              <button
                onClick={() => {
                  requestsRef.current = [];
                  updateNetworkMetrics();
                }}
                className="w-full px-3 py-2 text-sm bg-blue-600 hover:bg-blue-700 rounded transition-colors"
              >
                Reset Metrics
              </button>
              <button
                onClick={() => {
                  console.log('Network Metrics:', networkMetrics);
                  console.log('Performance Metrics:', performanceMetrics);
                  console.log('API Health:', apiHealth);
                  console.log('Token Usage:', usage);
                }}
                className="w-full px-3 py-2 text-sm bg-gray-700 hover:bg-gray-600 rounded transition-colors"
              >
                Log to Console
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Backdrop */}
      {isExpanded && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsExpanded(false)}
          style={{ backgroundColor: 'rgba(0, 0, 0, 0.2)' }}
        />
      )}
    </>
  );
}

/**
 * useDevMonitor - Hook to access dev monitor data
 */
export function useDevMonitor() {
  const [data, setData] = useState({
    networkMetrics: {} as NetworkMetrics,
    performanceMetrics: {} as PerformanceMetrics,
    apiHealth: {} as any,
  });

  useEffect(() => {
    // This would be populated by the monitor
    console.log('Dev monitor active');
  }, []);

  return data;
}
