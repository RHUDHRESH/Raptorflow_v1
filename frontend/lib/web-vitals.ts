/**
 * Web Vitals Tracking Module
 * Tracks Core Web Vitals metrics for performance monitoring
 * Supports LCP, FID, CLS, TTFB, and FCP
 */

/**
 * Core Web Vitals Interface
 */
export interface CoreWebVitals {
  LCP?: number; // Largest Contentful Paint (milliseconds)
  FID?: number; // First Input Delay (milliseconds)
  CLS?: number; // Cumulative Layout Shift (unitless)
  TTFB?: number; // Time to First Byte (milliseconds)
  FCP?: number; // First Contentful Paint (milliseconds)
}

/**
 * Vital Entry Interface
 */
export interface VitalEntry {
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  delta: number;
  id: string;
  entries: PerformanceEntry[];
  navigationType?: string;
}

/**
 * Metrics Collection Interface
 */
export interface MetricsCollection {
  timestamp: number;
  vitals: CoreWebVitals;
  customMetrics: Record<string, number>;
  sessionId: string;
  deviceInfo: DeviceInfo;
}

/**
 * Device Information
 */
export interface DeviceInfo {
  userAgent: string;
  deviceType: 'mobile' | 'tablet' | 'desktop';
  connection?: string;
  memory?: number;
  hardwareConcurrency?: number;
}

/**
 * Thresholds for rating classification
 */
export const VITAL_THRESHOLDS = {
  LCP: { good: 2500, poor: 4000 }, // milliseconds
  FID: { good: 100, poor: 300 }, // milliseconds
  CLS: { good: 0.1, poor: 0.25 }, // unitless
  TTFB: { good: 600, poor: 1800 }, // milliseconds
  FCP: { good: 1800, poor: 3000 }, // milliseconds
};

/**
 * Performance Monitoring Class
 * Manages Web Vitals collection and reporting
 */
export class WebVitalsMonitor {
  private vitals: CoreWebVitals = {};
  private customMetrics: Map<string, number> = new Map();
  private callbacks: Array<(metrics: MetricsCollection) => void> = [];
  private sessionId: string = '';
  private deviceInfo: DeviceInfo;
  private observerIds: Set<string> = new Set();

  constructor() {
    this.sessionId = this.generateSessionId();
    this.deviceInfo = this.getDeviceInfo();
    this.initializeObservers();
  }

  /**
   * Initialize performance observers for Web Vitals
   */
  private initializeObservers(): void {
    // Only run in browser environment
    if (typeof window === 'undefined') return;

    try {
      // Observe Largest Contentful Paint (LCP)
      this.observeLCP();

      // Observe First Input Delay (FID)
      this.observeFID();

      // Observe Cumulative Layout Shift (CLS)
      this.observeCLS();

      // Observe First Contentful Paint (FCP)
      this.observeFCP();

      // Observe Time to First Byte (TTFB)
      this.observeTTFB();
    } catch (error) {
      console.warn('[WebVitals] Failed to initialize observers:', error);
    }
  }

  /**
   * Observe Largest Contentful Paint (LCP)
   * Measures when the largest content element is painted
   */
  private observeLCP(): void {
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1] as any;
        this.vitals.LCP = Math.round(lastEntry.renderTime || lastEntry.loadTime);
        this.notifyCallbacks();
      });

      observer.observe({ entryTypes: ['largest-contentful-paint'], buffered: true });
      this.observerIds.add('lcp');
    } catch (error) {
      console.warn('[WebVitals] LCP observer failed:', error);
    }
  }

  /**
   * Observe First Input Delay (FID)
   * Measures delay between user input and response
   */
  private observeFID(): void {
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const firstEntry = entries[0] as any;
        this.vitals.FID = Math.round(firstEntry.processingDuration);
        this.notifyCallbacks();
      });

      observer.observe({ entryTypes: ['first-input'], buffered: true });
      this.observerIds.add('fid');
    } catch (error) {
      console.warn('[WebVitals] FID observer failed:', error);
    }
  }

  /**
   * Observe Cumulative Layout Shift (CLS)
   * Measures unexpected layout shifts during page lifecycle
   */
  private observeCLS(): void {
    try {
      let clsValue = 0;
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value;
          }
        }
        this.vitals.CLS = Math.round(clsValue * 10000) / 10000; // Round to 4 decimals
        this.notifyCallbacks();
      });

      observer.observe({ entryTypes: ['layout-shift'], buffered: true });
      this.observerIds.add('cls');
    } catch (error) {
      console.warn('[WebVitals] CLS observer failed:', error);
    }
  }

  /**
   * Observe First Contentful Paint (FCP)
   * Measures when first content is painted on screen
   */
  private observeFCP(): void {
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const fcpEntry = entries.find((entry) => entry.name === 'first-contentful-paint');
        if (fcpEntry) {
          this.vitals.FCP = Math.round(fcpEntry.startTime);
          this.notifyCallbacks();
        }
      });

      observer.observe({ entryTypes: ['paint'], buffered: true });
      this.observerIds.add('fcp');
    } catch (error) {
      console.warn('[WebVitals] FCP observer failed:', error);
    }
  }

  /**
   * Observe Time to First Byte (TTFB)
   * Measures time from request start to first byte received
   */
  private observeTTFB(): void {
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const navigationEntry = entries[0] as PerformanceNavigationTiming;
        if (navigationEntry.responseStart > 0) {
          this.vitals.TTFB = Math.round(navigationEntry.responseStart);
          this.notifyCallbacks();
        }
      });

      observer.observe({ entryTypes: ['navigation'], buffered: true });
      this.observerIds.add('ttfb');
    } catch (error) {
      console.warn('[WebVitals] TTFB observer failed:', error);
    }
  }

  /**
   * Record a custom metric
   */
  public recordMetric(name: string, value: number): void {
    this.customMetrics.set(name, value);
    this.notifyCallbacks();
  }

  /**
   * Register a callback for metrics updates
   */
  public onMetrics(callback: (metrics: MetricsCollection) => void): void {
    this.callbacks.push(callback);
  }

  /**
   * Get current vitals
   */
  public getVitals(): CoreWebVitals {
    return { ...this.vitals };
  }

  /**
   * Get custom metrics
   */
  public getCustomMetrics(): Record<string, number> {
    const metrics: Record<string, number> = {};
    this.customMetrics.forEach((value, key) => {
      metrics[key] = value;
    });
    return metrics;
  }

  /**
   * Get all collected metrics
   */
  public getMetrics(): MetricsCollection {
    return {
      timestamp: Date.now(),
      vitals: this.getVitals(),
      customMetrics: this.getCustomMetrics(),
      sessionId: this.sessionId,
      deviceInfo: this.deviceInfo,
    };
  }

  /**
   * Get rating for a vital
   */
  public getVitalRating(vital: keyof CoreWebVitals, value?: number): 'good' | 'needs-improvement' | 'poor' {
    const actualValue = value ?? this.vitals[vital];
    if (actualValue === undefined) return 'needs-improvement';

    const thresholds = VITAL_THRESHOLDS[vital as keyof typeof VITAL_THRESHOLDS];
    if (!thresholds) return 'needs-improvement';

    if (actualValue <= thresholds.good) return 'good';
    if (actualValue <= thresholds.poor) return 'needs-improvement';
    return 'poor';
  }

  /**
   * Get summary of all vitals with ratings
   */
  public getSummary(): Record<string, { value?: number; rating: string }> {
    const summary: Record<string, { value?: number; rating: string }> = {};

    Object.keys(this.vitals).forEach((vital) => {
      const key = vital as keyof CoreWebVitals;
      const value = this.vitals[key];
      summary[vital] = {
        value,
        rating: this.getVitalRating(key, value),
      };
    });

    return summary;
  }

  /**
   * Export metrics as JSON
   */
  public exportMetrics(): string {
    return JSON.stringify(this.getMetrics(), null, 2);
  }

  /**
   * Send metrics to analytics endpoint
   */
  public async sendMetrics(endpoint: string): Promise<void> {
    try {
      const metrics = this.getMetrics();
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(metrics),
        keepalive: true, // Ensure delivery even if page unloads
      });

      if (!response.ok) {
        console.warn(`[WebVitals] Failed to send metrics: ${response.statusText}`);
      }
    } catch (error) {
      console.warn('[WebVitals] Failed to send metrics:', error);
    }
  }

  /**
   * Cleanup observers (call on component unmount if needed)
   */
  public dispose(): void {
    this.callbacks = [];
    this.customMetrics.clear();
  }

  /**
   * Notify all registered callbacks
   */
  private notifyCallbacks(): void {
    const metrics = this.getMetrics();
    this.callbacks.forEach((callback) => {
      try {
        callback(metrics);
      } catch (error) {
        console.warn('[WebVitals] Callback error:', error);
      }
    });
  }

  /**
   * Generate unique session ID
   */
  private generateSessionId(): string {
    return `${Date.now()}-${Math.random().toString(36).substring(7)}`;
  }

  /**
   * Get device information
   */
  private getDeviceInfo(): DeviceInfo {
    if (typeof window === 'undefined') {
      return {
        userAgent: '',
        deviceType: 'desktop',
      };
    }

    const userAgent = navigator.userAgent;
    const isMobile = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(
      userAgent.toLowerCase()
    );
    const isTablet = /ipad|android(?!.*mobile)/i.test(userAgent.toLowerCase());

    return {
      userAgent,
      deviceType: isTablet ? 'tablet' : isMobile ? 'mobile' : 'desktop',
      connection: (navigator as any).connection?.effectiveType || undefined,
      memory: (navigator as any).deviceMemory || undefined,
      hardwareConcurrency: (navigator as any).hardwareConcurrency || undefined,
    };
  }
}

/**
 * Global instance
 */
let globalMonitor: WebVitalsMonitor | null = null;

/**
 * Get or create global monitor instance
 */
export function getWebVitalsMonitor(): WebVitalsMonitor {
  if (typeof window !== 'undefined' && !globalMonitor) {
    globalMonitor = new WebVitalsMonitor();
  }
  return globalMonitor || new WebVitalsMonitor();
}

/**
 * Utility function to check if vitals meet target thresholds
 */
export function checkVitalsHealth(vitals: CoreWebVitals): { healthy: boolean; issues: string[] } {
  const issues: string[] = [];

  if (vitals.LCP && vitals.LCP > VITAL_THRESHOLDS.LCP.poor) {
    issues.push(`LCP ${vitals.LCP}ms exceeds poor threshold`);
  }

  if (vitals.FID && vitals.FID > VITAL_THRESHOLDS.FID.poor) {
    issues.push(`FID ${vitals.FID}ms exceeds poor threshold`);
  }

  if (vitals.CLS && vitals.CLS > VITAL_THRESHOLDS.CLS.poor) {
    issues.push(`CLS ${vitals.CLS} exceeds poor threshold`);
  }

  return {
    healthy: issues.length === 0,
    issues,
  };
}
