/**
 * Token Tracker Utility
 * Tracks token usage per request and overall
 */

export interface TokenMetric {
  timestamp: number;
  tokensUsed: number;
  cost: number;
  agent?: string;
  endpoint?: string;
  status?: number;
}

export interface TokenStats {
  sessionTokens: number;
  totalTokens: number;
  sessionCost: number;
  totalCost: number;
  averageTokensPerRequest: number;
  averageCostPerRequest: number;
  totalRequests: number;
  requestsWithTokenTracking: number;
}

class TokenTracker {
  private metrics: TokenMetric[] = [];
  private maxMetrics = 1000;
  private tokensPerThousand = 0.001; // $0.001 per 1000 tokens
  private debug = process.env.NODE_ENV === 'development';
  private sessionStartTime = Date.now();

  /**
   * Record token usage for a request
   */
  public recordTokens(tokens: number, cost?: number, agent?: string, endpoint?: string) {
    const metric: TokenMetric = {
      timestamp: Date.now(),
      tokensUsed: tokens,
      cost: cost || tokens * this.tokensPerThousand,
      agent,
      endpoint,
    };

    this.metrics.push(metric);

    if (this.metrics.length > this.maxMetrics) {
      this.metrics = this.metrics.slice(-this.maxMetrics);
    }

    if (this.debug) {
      console.log(
        `[Tokens] ${tokens} tokens, $${metric.cost.toFixed(6)}${agent ? ` (${agent})` : ''}`
      );
    }

    return metric;
  }

  /**
   * Record tokens from API response header
   */
  public recordFromResponse(response: Response, agent?: string) {
    // Check for token usage header
    const tokensHeader = response.headers.get('X-Tokens-Used');
    const costHeader = response.headers.get('X-Cost-USD');

    if (tokensHeader) {
      const tokens = parseInt(tokensHeader, 10);
      const cost = costHeader ? parseFloat(costHeader) : tokens * this.tokensPerThousand;

      return this.recordTokens(tokens, cost, agent, response.url);
    }

    return null;
  }

  /**
   * Get current token statistics
   */
  public getStats(): TokenStats {
    const total = this.metrics.length;
    const totalTokens = this.metrics.reduce((sum, m) => sum + m.tokensUsed, 0);
    const totalCost = this.metrics.reduce((sum, m) => sum + m.cost, 0);

    // Session metrics (tokens in current session)
    const sessionStartMs = this.sessionStartTime;
    const sessionMetrics = this.metrics.filter((m) => m.timestamp >= sessionStartMs);
    const sessionTokens = sessionMetrics.reduce((sum, m) => sum + m.tokensUsed, 0);
    const sessionCost = sessionMetrics.reduce((sum, m) => sum + m.cost, 0);

    return {
      sessionTokens,
      totalTokens,
      sessionCost,
      totalCost,
      averageTokensPerRequest: total > 0 ? Math.round(totalTokens / total) : 0,
      averageCostPerRequest: total > 0 ? totalCost / total : 0,
      totalRequests: total,
      requestsWithTokenTracking: this.metrics.length,
    };
  }

  /**
   * Get tokens by agent
   */
  public getTokensByAgent(): Record<string, { tokens: number; cost: number; count: number }> {
    const byAgent: Record<string, { tokens: number; cost: number; count: number }> = {};

    this.metrics.forEach((m) => {
      if (!m.agent) return;

      if (!byAgent[m.agent]) {
        byAgent[m.agent] = { tokens: 0, cost: 0, count: 0 };
      }

      byAgent[m.agent].tokens += m.tokensUsed;
      byAgent[m.agent].cost += m.cost;
      byAgent[m.agent].count += 1;
    });

    return byAgent;
  }

  /**
   * Get tokens by endpoint
   */
  public getTokensByEndpoint(): Record<string, { tokens: number; cost: number; count: number }> {
    const byEndpoint: Record<string, { tokens: number; cost: number; count: number }> = {};

    this.metrics.forEach((m) => {
      if (!m.endpoint) return;

      const endpoint = new URL(m.endpoint).pathname;
      if (!byEndpoint[endpoint]) {
        byEndpoint[endpoint] = { tokens: 0, cost: 0, count: 0 };
      }

      byEndpoint[endpoint].tokens += m.tokensUsed;
      byEndpoint[endpoint].cost += m.cost;
      byEndpoint[endpoint].count += 1;
    });

    return byEndpoint;
  }

  /**
   * Get expensive requests (above threshold)
   */
  public getExpensiveRequests(threshold: number = 1.0): TokenMetric[] {
    return this.metrics.filter((m) => m.cost > threshold);
  }

  /**
   * Get recent tokens
   */
  public getRecentTokens(count: number = 10): TokenMetric[] {
    return this.metrics.slice(-count);
  }

  /**
   * Get session duration in seconds
   */
  public getSessionDuration(): number {
    return Math.round((Date.now() - this.sessionStartTime) / 1000);
  }

  /**
   * Reset session metrics
   */
  public resetSession() {
    this.sessionStartTime = Date.now();
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
        byAgent: this.getTokensByAgent(),
        byEndpoint: this.getTokensByEndpoint(),
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
    const byAgent = this.getTokensByAgent();

    console.group('💰 Token Usage Statistics');
    console.table({
      'Session Tokens': stats.sessionTokens.toLocaleString(),
      'Session Cost': `$${stats.sessionCost.toFixed(4)}`,
      'Total Tokens': stats.totalTokens.toLocaleString(),
      'Total Cost': `$${stats.totalCost.toFixed(4)}`,
      'Average Per Request': `${stats.averageTokensPerRequest.toLocaleString()} tokens`,
      'Requests Tracked': stats.requestsWithTokenTracking,
    });

    if (Object.keys(byAgent).length > 0) {
      console.group('By Agent:');
      Object.entries(byAgent).forEach(([agent, data]) => {
        console.log(
          `  ${agent}: ${data.tokens.toLocaleString()} tokens, $${data.cost.toFixed(4)} (${data.count} requests)`
        );
      });
      console.groupEnd();
    }

    console.groupEnd();
  }

  /**
   * Get all metrics
   */
  public getAllMetrics(): TokenMetric[] {
    return [...this.metrics];
  }

  /**
   * Format cost as currency
   */
  public formatCost(cost: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(cost);
  }

  /**
   * Get budget status
   */
  public getBudgetStatus(monthlyBudget: number = 15) {
    const stats = this.getStats();
    const used = stats.totalCost;
    const remaining = Math.max(0, monthlyBudget - used);
    const percentage = (used / monthlyBudget) * 100;

    return {
      monthlyBudget,
      used,
      remaining,
      percentage: Math.round(percentage),
      status: remaining <= 0 ? 'exceeded' : percentage >= 80 ? 'warning' : 'ok',
    };
  }

  /**
   * Set cost per token (for different pricing models)
   */
  public setCostPerToken(costPerThousand: number) {
    this.tokensPerThousand = costPerThousand;
  }
}

// Create singleton instance
export const tokenTracker = new TokenTracker();

// Export types
export type { TokenMetric, TokenStats };
