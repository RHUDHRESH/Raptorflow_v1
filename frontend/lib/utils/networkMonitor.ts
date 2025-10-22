/**
 * Network Monitor Utility
 * Tracks network performance, speed, and latency
 */

export interface NetworkMetric {
  url: string;
  method: string;
  duration: number;
  status: number;
  timestamp: number;
  size?: number;
  error?: string;
}

export interface NetworkStats {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  minResponseTime: number;
  maxResponseTime: number;
  p95ResponseTime: number;
  p99ResponseTime: number;
  networkSpeed: string; // 'fast' | 'slow' | 'moderate'
  estimatedBandwidth: number; // MB/s
  totalDataTransferred: number; // bytes
}

class NetworkMonitor {
  private metrics: NetworkMetric[] = [];
  private maxMetrics = 500;
  private startTime = Date.now();
  private debug = process.env.NODE_ENV === 'development';

  constructor() {
    this.interceptFetch();
  }

  /**
   * Intercept fetch calls
   */
  private interceptFetch() {
    const originalFetch = window.fetch;

    window.fetch = (...args: any[]): Promise<Response> => {
      const [resource, config] = args;
      const url = typeof resource === 'string' ? resource : resource.url;
      const method = (config?.method || 'GET').toUpperCase();
      const startTime = performance.now();

      return originalFetch.apply(window, args).then((response) => {
        const duration = performance.now() - startTime;
        const status = response.status;

        // Clone response to get size
        const clonedResponse = response.clone();
        clonedResponse.blob().then((blob) => {
          this.recordMetric({
            url,
            method,
            duration: Math.round(duration),
            status,
            timestamp: Date.now(),
            size: blob.size,
          });
        });

        return response;
      });
    };
  }

  /**
   * Record a network metric
   */
  public recordMetric(metric: NetworkMetric) {
    this.metrics.push(metric);

    // Keep only latest metrics
    if (this.metrics.length > this.maxMetrics) {
      this.metrics = this.metrics.slice(-this.maxMetrics);
    }

    if (this.debug) {
      console.log(`[Network] ${metric.method} ${metric.url}: ${metric.duration}ms (${metric.status})`);
    }
  }

  /**
   * Get current network statistics
   */
  public getStats(): NetworkStats {
    const total = this.metrics.length;
    const successful = this.metrics.filter((m) => m.status >= 200 && m.status < 300).length;
    const failed = this.metrics.filter((m) => m.status >= 400).length;

    const times = this.metrics.map((m) => m.duration).sort((a, b) => a - b);
    const avg = total > 0 ? Math.round(times.reduce((a, b) => a + b, 0) / total) : 0;
    const min = total > 0 ? times[0] : 0;
    const max = total > 0 ? times[times.length - 1] : 0;

    // Calculate percentiles
    const p95Index = Math.ceil((95 / 100) * times.length) - 1;
    const p99Index = Math.ceil((99 / 100) * times.length) - 1;
    const p95 = times[Math.max(0, p95Index)] || 0;
    const p99 = times[Math.max(0, p99Index)] || 0;

    // Determine network speed
    let networkSpeed: 'fast' | 'slow' | 'moderate' = 'moderate';
    if (avg < 100) networkSpeed = 'fast';
    if (avg > 500) networkSpeed = 'slow';

    // Estimate bandwidth (simplified)
    const totalSize = this.metrics.reduce((sum, m) => sum + (m.size || 0), 0);
    const totalDuration = this.metrics.reduce((sum, m) => sum + m.duration, 0);
    const estimatedBandwidth =
      totalDuration > 0 ? (totalSize / (totalDuration / 1000)) / (1024 * 1024) : 0;

    return {
      totalRequests: total,
      successfulRequests: successful,
      failedRequests: failed,
      averageResponseTime: avg,
      minResponseTime: min,
      maxResponseTime: max,
      p95ResponseTime: p95,
      p99ResponseTime: p99,
      networkSpeed,
      estimatedBandwidth: Math.round(estimatedBandwidth * 100) / 100,
      totalDataTransferred: totalSize,
    };
  }

  /**
   * Get metrics by endpoint pattern
   */
  public getMetricsByEndpoint(pattern: string): NetworkMetric[] {
    const regex = new RegExp(pattern);
    return this.metrics.filter((m) => regex.test(m.url));
  }

  /**
   * Get metrics by method
   */
  public getMetricsByMethod(method: string): NetworkMetric[] {
    return this.metrics.filter((m) => m.method === method.toUpperCase());
  }

  /**
   * Get slow requests (above threshold)
   */
  public getSlowRequests(threshold: number = 500): NetworkMetric[] {
    return this.metrics.filter((m) => m.duration > threshold);
  }

  /**
   * Get failed requests
   */
  public getFailedRequests(): NetworkMetric[] {
    return this.metrics.filter((m) => m.status >= 400 || m.error);
  }

  /**
   * Get recent requests
   */
  public getRecentRequests(count: number = 10): NetworkMetric[] {
    return this.metrics.slice(-count);
  }

  /**
   * Clear all metrics
   */
  public clear() {
    this.metrics = [];
  }

  /**
   * Export metrics as JSON
   */
  public exportMetrics(): string {
    return JSON.stringify(
      {
        stats: this.getStats(),
        metrics: this.metrics,
        exportTime: new Date().toISOString(),
      },
      null,
      2
    );
  }

  /**
   * Log statistics to console
   */
  public logStats() {
    const stats = this.getStats();
    console.group('📊 Network Statistics');
    console.table({
      'Total Requests': stats.totalRequests,
      'Successful Requests': stats.successfulRequests,
      'Failed Requests': stats.failedRequests,
      'Average Response Time': `${stats.averageResponseTime}ms`,
      'Min Response Time': `${stats.minResponseTime}ms`,
      'Max Response Time': `${stats.maxResponseTime}ms`,
      'P95 Response Time': `${stats.p95ResponseTime}ms`,
      'P99 Response Time': `${stats.p99ResponseTime}ms`,
      'Network Speed': stats.networkSpeed,
      'Estimated Bandwidth': `${stats.estimatedBandwidth} MB/s`,
      'Total Data': `${(stats.totalDataTransferred / 1024 / 1024).toFixed(2)} MB`,
    });
    console.groupEnd();
  }

  /**
   * Get all metrics
   */
  public getAllMetrics(): NetworkMetric[] {
    return [...this.metrics];
  }
}

// Create singleton instance
export const networkMonitor = new NetworkMonitor();

// Export types
export type { NetworkMetric, NetworkStats };
