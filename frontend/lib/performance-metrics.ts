/**
 * Performance Metrics Collection System
 * Collects and aggregates custom performance metrics
 * Tracks component render times, API latencies, user interactions
 */

/**
 * Metric Event Interface
 */
export interface MetricEvent {
  id: string;
  name: string;
  type: 'component' | 'api' | 'interaction' | 'custom';
  value: number; // milliseconds or unitless
  timestamp: number;
  tags: Record<string, string>;
  metadata?: Record<string, any>;
}

/**
 * Aggregated Metric Interface
 */
export interface AggregatedMetric {
  name: string;
  type: string;
  count: number;
  min: number;
  max: number;
  mean: number;
  median: number;
  p95: number;
  p99: number;
  stdDev: number;
  lastUpdated: number;
}

/**
 * Metric Report Interface
 */
export interface MetricReport {
  timestamp: number;
  periodMs: number;
  totalEvents: number;
  metrics: Record<string, AggregatedMetric>;
  topSlow: MetricEvent[];
  topFrequent: Array<{ name: string; count: number }>;
}

/**
 * Performance Metrics Collector
 */
export class MetricsCollector {
  private events: MetricEvent[] = [];
  private maxEvents: number = 5000; // Keep last 5000 events
  private startTime: number = Date.now();
  private aggregateCache: Map<string, AggregatedMetric> = new Map();
  private cacheDirty: boolean = false;
  private listeners: Array<(event: MetricEvent) => void> = [];

  constructor(maxEvents: number = 5000) {
    this.maxEvents = maxEvents;
  }

  /**
   * Record a metric event
   */
  public recordMetric(
    name: string,
    value: number,
    type: 'component' | 'api' | 'interaction' | 'custom' = 'custom',
    tags: Record<string, string> = {},
    metadata?: Record<string, any>
  ): string {
    const id = this.generateId();
    const event: MetricEvent = {
      id,
      name,
      type,
      value,
      timestamp: Date.now(),
      tags,
      metadata,
    };

    this.events.push(event);

    // Maintain max size
    if (this.events.length > this.maxEvents) {
      this.events = this.events.slice(-this.maxEvents);
    }

    this.cacheDirty = true;
    this.notifyListeners(event);

    return id;
  }

  /**
   * Record component render time
   */
  public recordComponentRender(componentName: string, renderTime: number, tags?: Record<string, string>): void {
    this.recordMetric(`component:${componentName}`, renderTime, 'component', tags);
  }

  /**
   * Record API call latency
   */
  public recordApiCall(
    endpoint: string,
    duration: number,
    statusCode: number,
    tags?: Record<string, string>
  ): void {
    this.recordMetric(`api:${endpoint}`, duration, 'api', {
      statusCode: statusCode.toString(),
      ...tags,
    });
  }

  /**
   * Record user interaction
   */
  public recordInteraction(actionName: string, duration: number, tags?: Record<string, string>): void {
    this.recordMetric(`interaction:${actionName}`, duration, 'interaction', tags);
  }

  /**
   * Get all events
   */
  public getEvents(): MetricEvent[] {
    return [...this.events];
  }

  /**
   * Get events filtered by type
   */
  public getEventsByType(type: string): MetricEvent[] {
    return this.events.filter((event) => event.type === type || event.name.startsWith(type));
  }

  /**
   * Get events filtered by name pattern
   */
  public getEventsByName(pattern: string | RegExp): MetricEvent[] {
    const regex = typeof pattern === 'string' ? new RegExp(pattern) : pattern;
    return this.events.filter((event) => regex.test(event.name));
  }

  /**
   * Get aggregated metrics
   */
  public getAggregatedMetrics(): Record<string, AggregatedMetric> {
    if (!this.cacheDirty && this.aggregateCache.size > 0) {
      return Object.fromEntries(this.aggregateCache);
    }

    this.aggregateCache.clear();

    // Group events by name
    const grouped = new Map<string, MetricEvent[]>();
    this.events.forEach((event) => {
      if (!grouped.has(event.name)) {
        grouped.set(event.name, []);
      }
      grouped.get(event.name)!.push(event);
    });

    // Calculate aggregates for each group
    grouped.forEach((events, name) => {
      const values = events.map((e) => e.value).sort((a, b) => a - b);
      const mean = values.reduce((a, b) => a + b, 0) / values.length;
      const variance = values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / values.length;

      this.aggregateCache.set(name, {
        name,
        type: events[0]?.type || 'unknown',
        count: events.length,
        min: Math.min(...values),
        max: Math.max(...values),
        mean: Math.round(mean * 100) / 100,
        median: values[Math.floor(values.length / 2)],
        p95: values[Math.floor(values.length * 0.95)],
        p99: values[Math.floor(values.length * 0.99)],
        stdDev: Math.round(Math.sqrt(variance) * 100) / 100,
        lastUpdated: Date.now(),
      });
    });

    this.cacheDirty = false;
    return Object.fromEntries(this.aggregateCache);
  }

  /**
   * Get metric report
   */
  public getReport(): MetricReport {
    const aggregated = this.getAggregatedMetrics();
    const duration = Date.now() - this.startTime;

    // Find top slow metrics
    const topSlow = [...this.events]
      .sort((a, b) => b.value - a.value)
      .slice(0, 5);

    // Find top frequent metrics
    const frequencies = new Map<string, number>();
    this.events.forEach((event) => {
      frequencies.set(event.name, (frequencies.get(event.name) || 0) + 1);
    });

    const topFrequent = Array.from(frequencies.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([name, count]) => ({ name, count }));

    return {
      timestamp: Date.now(),
      periodMs: duration,
      totalEvents: this.events.length,
      metrics: aggregated,
      topSlow,
      topFrequent,
    };
  }

  /**
   * Get percentile value for a metric
   */
  public getPercentile(name: string, percentile: number): number | null {
    const events = this.getEventsByName(name);
    if (events.length === 0) return null;

    const values = events.map((e) => e.value).sort((a, b) => a - b);
    const index = Math.floor((percentile / 100) * values.length);
    return values[index];
  }

  /**
   * Get average for a metric
   */
  public getAverage(name: string | RegExp): number | null {
    const events = this.getEventsByName(name);
    if (events.length === 0) return null;

    const sum = events.reduce((a, e) => a + e.value, 0);
    return Math.round((sum / events.length) * 100) / 100;
  }

  /**
   * Register listener for new metrics
   */
  public onMetric(listener: (event: MetricEvent) => void): () => void {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== listener);
    };
  }

  /**
   * Clear all metrics
   */
  public clear(): void {
    this.events = [];
    this.aggregateCache.clear();
    this.startTime = Date.now();
    this.cacheDirty = true;
  }

  /**
   * Export metrics as JSON
   */
  public export(): string {
    return JSON.stringify(
      {
        report: this.getReport(),
        rawEvents: this.events,
      },
      null,
      2
    );
  }

  /**
   * Send report to analytics endpoint
   */
  public async sendReport(endpoint: string): Promise<void> {
    try {
      const report = this.getReport();
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(report),
        keepalive: true,
      });

      if (!response.ok) {
        console.warn(`[Metrics] Failed to send report: ${response.statusText}`);
      }
    } catch (error) {
      console.warn('[Metrics] Failed to send report:', error);
    }
  }

  /**
   * Notify listeners
   */
  private notifyListeners(event: MetricEvent): void {
    this.listeners.forEach((listener) => {
      try {
        listener(event);
      } catch (error) {
        console.warn('[Metrics] Listener error:', error);
      }
    });
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `m-${Date.now()}-${Math.random().toString(36).substring(7)}`;
  }
}

/**
 * React Hook for performance timing
 */
export function usePerformanceMetric(name: string, enabled: boolean = true): {
  start: () => void;
  end: () => void;
  record: (duration: number) => void;
} {
  const startTimeRef = { current: 0 };

  return {
    start: () => {
      if (!enabled) return;
      startTimeRef.current = performance.now();
    },
    end: () => {
      if (!enabled || startTimeRef.current === 0) return;
      const duration = performance.now() - startTimeRef.current;
      getMetricsCollector().recordMetric(name, duration, 'custom');
    },
    record: (duration: number) => {
      if (!enabled) return;
      getMetricsCollector().recordMetric(name, duration, 'custom');
    },
  };
}

/**
 * Performance timer utility
 */
export class PerformanceTimer {
  private startTime: number = 0;
  private marks: Map<string, number> = new Map();

  start(): void {
    this.startTime = performance.now();
  }

  mark(label: string): void {
    this.marks.set(label, performance.now() - this.startTime);
  }

  end(label?: string): number {
    const duration = performance.now() - this.startTime;
    if (label) {
      this.marks.set(label, duration);
    }
    return Math.round(duration * 100) / 100;
  }

  getMarks(): Record<string, number> {
    return Object.fromEntries(this.marks);
  }

  reset(): void {
    this.startTime = 0;
    this.marks.clear();
  }
}

/**
 * Global metrics collector instance
 */
let globalCollector: MetricsCollector | null = null;

/**
 * Get or create global metrics collector
 */
export function getMetricsCollector(): MetricsCollector {
  if (!globalCollector) {
    globalCollector = new MetricsCollector();
  }
  return globalCollector;
}

/**
 * API fetch wrapper with metrics
 */
export async function fetchWithMetrics<T>(
  url: string,
  options?: RequestInit & { metricName?: string }
): Promise<T> {
  const metricName = options?.metricName || `api:${new URL(url, window.location.origin).pathname}`;
  const startTime = performance.now();

  try {
    const response = await fetch(url, options);
    const duration = performance.now() - startTime;

    getMetricsCollector().recordApiCall(metricName, duration, response.status);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return response.json() as Promise<T>;
  } catch (error) {
    const duration = performance.now() - startTime;
    getMetricsCollector().recordApiCall(metricName, duration, 0);
    throw error;
  }
}
