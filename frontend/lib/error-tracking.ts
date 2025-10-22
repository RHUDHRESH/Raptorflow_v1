/**
 * Error Tracking and Alerts Module
 * Captures, tracks, and reports application errors with context
 * Supports performance threshold alerts
 */

/**
 * Error Event Interface
 */
export interface ErrorEvent {
  id: string;
  message: string;
  stack?: string;
  type: 'error' | 'warning' | 'fatal';
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: number;
  context: ErrorContext;
  userId?: string;
  sessionId?: string;
}

/**
 * Error Context
 */
export interface ErrorContext {
  url: string;
  userAgent: string;
  viewport?: { width: number; height: number };
  memory?: number;
  vitals?: Record<string, number>;
  tags: Record<string, string>;
  breadcrumbs: BreadcrumbEvent[];
}

/**
 * Breadcrumb Event (for error context)
 */
export interface BreadcrumbEvent {
  message: string;
  type: 'user-action' | 'navigation' | 'api-call' | 'state-change' | 'custom';
  timestamp: number;
  data?: Record<string, any>;
}

/**
 * Alert Configuration
 */
export interface AlertConfig {
  id: string;
  name: string;
  type: 'performance' | 'error-rate' | 'custom';
  condition: (data: AlertData) => boolean;
  action: (alert: Alert) => Promise<void>;
  enabled: boolean;
  cooldownMs: number;
  lastTriggered?: number;
}

/**
 * Alert Data
 */
export interface AlertData {
  metric: string;
  value: number;
  threshold: number;
  timestamp: number;
}

/**
 * Alert Interface
 */
export interface Alert {
  id: string;
  configId: string;
  message: string;
  severity: 'warning' | 'error' | 'critical';
  timestamp: number;
  data: AlertData;
}

/**
 * Error Tracking Manager
 */
export class ErrorTracker {
  private errors: ErrorEvent[] = [];
  private breadcrumbs: BreadcrumbEvent[] = [];
  private maxErrors: number = 1000;
  private maxBreadcrumbs: number = 50;
  private errorListeners: Array<(error: ErrorEvent) => void> = [];
  private sessionId: string;
  private userId?: string;

  constructor(sessionId: string, userId?: string) {
    this.sessionId = sessionId;
    this.userId = userId;
    this.setupGlobalHandlers();
  }

  /**
   * Setup global error handlers
   */
  private setupGlobalHandlers(): void {
    if (typeof window === 'undefined') return;

    // Handle uncaught errors
    window.addEventListener('error', (event) => {
      this.captureError(
        event.message || 'Uncaught error',
        'error',
        'critical',
        event.error?.stack
      );
    });

    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      const message =
        event.reason instanceof Error ? event.reason.message : String(event.reason);
      this.captureError(message, 'error', 'critical', event.reason?.stack);
    });
  }

  /**
   * Capture and track an error
   */
  public captureError(
    message: string,
    type: 'error' | 'warning' | 'fatal' = 'error',
    severity: 'low' | 'medium' | 'high' | 'critical' = 'high',
    stack?: string
  ): string {
    const id = this.generateId();
    const error: ErrorEvent = {
      id,
      message,
      stack,
      type,
      severity,
      timestamp: Date.now(),
      context: this.buildErrorContext(),
      userId: this.userId,
      sessionId: this.sessionId,
    };

    this.errors.push(error);

    // Maintain max size
    if (this.errors.length > this.maxErrors) {
      this.errors = this.errors.slice(-this.maxErrors);
    }

    this.notifyListeners(error);
    return id;
  }

  /**
   * Add breadcrumb for error context
   */
  public addBreadcrumb(
    message: string,
    type: 'user-action' | 'navigation' | 'api-call' | 'state-change' | 'custom' = 'custom',
    data?: Record<string, any>
  ): void {
    const breadcrumb: BreadcrumbEvent = {
      message,
      type,
      timestamp: Date.now(),
      data,
    };

    this.breadcrumbs.push(breadcrumb);

    // Maintain max size (keep most recent)
    if (this.breadcrumbs.length > this.maxBreadcrumbs) {
      this.breadcrumbs = this.breadcrumbs.slice(-this.maxBreadcrumbs);
    }
  }

  /**
   * Get all errors
   */
  public getErrors(): ErrorEvent[] {
    return [...this.errors];
  }

  /**
   * Get errors by type
   */
  public getErrorsByType(type: string): ErrorEvent[] {
    return this.errors.filter((e) => e.type === type);
  }

  /**
   * Get errors by severity
   */
  public getErrorsBySeverity(severity: string): ErrorEvent[] {
    return this.errors.filter((e) => e.severity === severity);
  }

  /**
   * Get error summary
   */
  public getSummary(): {
    total: number;
    byType: Record<string, number>;
    bySeverity: Record<string, number>;
    recentErrors: ErrorEvent[];
  } {
    const byType: Record<string, number> = {};
    const bySeverity: Record<string, number> = {};

    this.errors.forEach((error) => {
      byType[error.type] = (byType[error.type] || 0) + 1;
      bySeverity[error.severity] = (bySeverity[error.severity] || 0) + 1;
    });

    return {
      total: this.errors.length,
      byType,
      bySeverity,
      recentErrors: this.errors.slice(-5),
    };
  }

  /**
   * Register listener for errors
   */
  public onError(listener: (error: ErrorEvent) => void): () => void {
    this.errorListeners.push(listener);
    return () => {
      this.errorListeners = this.errorListeners.filter((l) => l !== listener);
    };
  }

  /**
   * Export errors as JSON
   */
  public export(): string {
    return JSON.stringify(
      {
        summary: this.getSummary(),
        errors: this.errors,
        breadcrumbs: this.breadcrumbs,
      },
      null,
      2
    );
  }

  /**
   * Send errors to tracking endpoint
   */
  public async sendErrors(endpoint: string, limit: number = 10): Promise<void> {
    try {
      const recentErrors = this.errors.slice(-limit);
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          errors: recentErrors,
          summary: this.getSummary(),
          sessionId: this.sessionId,
        }),
        keepalive: true,
      });

      if (!response.ok) {
        console.warn(`[ErrorTracker] Failed to send errors: ${response.statusText}`);
      }
    } catch (error) {
      console.warn('[ErrorTracker] Failed to send errors:', error);
    }
  }

  /**
   * Clear all errors
   */
  public clear(): void {
    this.errors = [];
    this.breadcrumbs = [];
  }

  /**
   * Build error context
   */
  private buildErrorContext(): ErrorContext {
    const context: ErrorContext = {
      url: typeof window !== 'undefined' ? window.location.href : '',
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
      tags: {},
      breadcrumbs: [...this.breadcrumbs],
    };

    if (typeof window !== 'undefined') {
      context.viewport = {
        width: window.innerWidth,
        height: window.innerHeight,
      };
    }

    if (typeof navigator !== 'undefined' && (navigator as any).deviceMemory) {
      context.memory = (navigator as any).deviceMemory;
    }

    return context;
  }

  /**
   * Notify listeners
   */
  private notifyListeners(error: ErrorEvent): void {
    this.errorListeners.forEach((listener) => {
      try {
        listener(error);
      } catch (err) {
        console.warn('[ErrorTracker] Listener error:', err);
      }
    });
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `err-${Date.now()}-${Math.random().toString(36).substring(7)}`;
  }
}

/**
 * Alert Manager
 */
export class AlertManager {
  private alerts: Alert[] = [];
  private configs: Map<string, AlertConfig> = new Map();
  private alertListeners: Array<(alert: Alert) => void> = [];
  private maxAlerts: number = 100;

  /**
   * Register alert configuration
   */
  public registerAlert(config: AlertConfig): void {
    this.configs.set(config.id, config);
  }

  /**
   * Check condition and trigger alert if needed
   */
  public async checkAndAlert(configId: string, data: AlertData): Promise<void> {
    const config = this.configs.get(configId);
    if (!config || !config.enabled) return;

    // Check cooldown
    if (config.lastTriggered && Date.now() - config.lastTriggered < config.cooldownMs) {
      return;
    }

    // Check condition
    if (!config.condition(data)) return;

    const alert: Alert = {
      id: this.generateId(),
      configId,
      message: `${config.name}: ${data.metric} = ${data.value.toFixed(2)} (threshold: ${data.threshold.toFixed(2)})`,
      severity: 'warning',
      timestamp: Date.now(),
      data,
    };

    this.alerts.push(alert);

    // Maintain max size
    if (this.alerts.length > this.maxAlerts) {
      this.alerts = this.alerts.slice(-this.maxAlerts);
    }

    // Execute action
    try {
      await config.action(alert);
      config.lastTriggered = Date.now();
    } catch (error) {
      console.warn('[AlertManager] Action failed:', error);
    }

    // Notify listeners
    this.notifyListeners(alert);
  }

  /**
   * Get all alerts
   */
  public getAlerts(): Alert[] {
    return [...this.alerts];
  }

  /**
   * Get recent alerts
   */
  public getRecentAlerts(limit: number = 10): Alert[] {
    return this.alerts.slice(-limit);
  }

  /**
   * Register listener for alerts
   */
  public onAlert(listener: (alert: Alert) => void): () => void {
    this.alertListeners.push(listener);
    return () => {
      this.alertListeners = this.alertListeners.filter((l) => l !== listener);
    };
  }

  /**
   * Clear alerts
   */
  public clear(): void {
    this.alerts = [];
  }

  /**
   * Notify listeners
   */
  private notifyListeners(alert: Alert): void {
    this.alertListeners.forEach((listener) => {
      try {
        listener(alert);
      } catch (error) {
        console.warn('[AlertManager] Listener error:', error);
      }
    });
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `alert-${Date.now()}-${Math.random().toString(36).substring(7)}`;
  }
}

/**
 * Global instances
 */
let globalErrorTracker: ErrorTracker | null = null;
let globalAlertManager: AlertManager | null = null;

/**
 * Initialize error tracking
 */
export function initializeErrorTracking(sessionId: string, userId?: string): ErrorTracker {
  globalErrorTracker = new ErrorTracker(sessionId, userId);
  return globalErrorTracker;
}

/**
 * Get or create error tracker
 */
export function getErrorTracker(): ErrorTracker {
  if (!globalErrorTracker) {
    globalErrorTracker = new ErrorTracker(`session-${Date.now()}`);
  }
  return globalErrorTracker;
}

/**
 * Get alert manager
 */
export function getAlertManager(): AlertManager {
  if (!globalAlertManager) {
    globalAlertManager = new AlertManager();
  }
  return globalAlertManager;
}

/**
 * Setup default performance alerts
 */
export function setupDefaultAlerts(): void {
  const alertManager = getAlertManager();

  // LCP Alert
  alertManager.registerAlert({
    id: 'lcp-alert',
    name: 'LCP Threshold Exceeded',
    type: 'performance',
    condition: (data) => data.value > 4000,
    action: async (alert) => {
      console.warn('[Alert]', alert.message);
    },
    enabled: true,
    cooldownMs: 5000,
  });

  // FID Alert
  alertManager.registerAlert({
    id: 'fid-alert',
    name: 'FID Threshold Exceeded',
    type: 'performance',
    condition: (data) => data.value > 300,
    action: async (alert) => {
      console.warn('[Alert]', alert.message);
    },
    enabled: true,
    cooldownMs: 5000,
  });

  // CLS Alert
  alertManager.registerAlert({
    id: 'cls-alert',
    name: 'CLS Threshold Exceeded',
    type: 'performance',
    condition: (data) => data.value > 0.25,
    action: async (alert) => {
      console.warn('[Alert]', alert.message);
    },
    enabled: true,
    cooldownMs: 5000,
  });

  // Error Rate Alert
  alertManager.registerAlert({
    id: 'error-rate-alert',
    name: 'High Error Rate',
    type: 'error-rate',
    condition: (data) => data.value > 5, // More than 5 errors in period
    action: async (alert) => {
      console.error('[Alert]', alert.message);
    },
    enabled: true,
    cooldownMs: 30000,
  });
}
