# 🔗 Frontend-Backend Integration & Feature Completion Guide

**Status:** INTEGRATION IN PROGRESS
**Goal:** Connect frontend to backend, implement all requested features, add pricing tier selector for dev mode
**Scope:** API integration, token saving, agent coordination, pricing UI

---

## 📋 Integration Checklist

### Phase 1: API Connection & Authentication (CRITICAL)
- [ ] Connect frontend auth to Supabase JWT backend
- [ ] Implement token refresh mechanism
- [ ] Setup API client with auth headers
- [ ] Handle auth errors and redirects

### Phase 2: Agent & Tool Integration
- [ ] Integrate all 7 core agents
- [ ] Connect analysis submission to orchestrator
- [ ] Stream results back to frontend
- [ ] Handle agent errors gracefully

### Phase 3: Token & Cost Tracking
- [ ] Display token usage in real-time
- [ ] Show estimated costs
- [ ] Implement budget warnings
- [ ] Block requests at budget limit

### Phase 4: Pricing Tier Feature (NEW)
- [ ] Add pricing tier selector in dev mode
- [ ] Show tier-specific features
- [ ] Enforce tier limits on frontend
- [ ] Track tier selection in session

### Phase 5: Feature Completeness
- [ ] Verify all requested features working
- [ ] Test error handling
- [ ] Validate data flow
- [ ] Performance optimization

---

## 🔧 STEP 1: Setup Frontend API Client

### 1.1 Create Enhanced API Client

```typescript
// lib/api-client.ts
import axios, { AxiosInstance, AxiosError } from 'axios';
import { AuthSession } from '@supabase/supabase-js';

interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
}

interface ApiResponse<T> {
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

class RaptorFlowAPI {
  private client: AxiosInstance;
  private session: AuthSession | null = null;

  constructor(config: ApiClientConfig) {
    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use((config) => {
      if (this.session?.access_token) {
        config.headers.Authorization = `Bearer ${this.session.access_token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiResponse<any>>) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - refresh token or redirect to login
          this.handleUnauthorized();
        }
        return Promise.reject(error);
      }
    );
  }

  setSession(session: AuthSession | null) {
    this.session = session;
  }

  private handleUnauthorized() {
    // Emit event for app to handle logout
    window.dispatchEvent(new CustomEvent('unauthorized'));
  }

  // ============ WORKSPACE ENDPOINTS ============

  async getWorkspaces() {
    const { data } = await this.client.get<ApiResponse<any>>('/api/v1/users/workspaces');
    return data;
  }

  async createWorkspace(name: string, description?: string) {
    const { data } = await this.client.post<ApiResponse<any>>('/api/v1/workspaces', {
      name,
      description,
    });
    return data;
  }

  async updateWorkspace(id: string, updates: any) {
    const { data } = await this.client.patch<ApiResponse<any>>(`/api/v1/workspaces/${id}`, updates);
    return data;
  }

  // ============ STRATEGY ENDPOINTS ============

  async createStrategy(workspaceId: string, name: string) {
    const { data } = await this.client.post<ApiResponse<any>>('/api/v1/strategies', {
      workspace_id: workspaceId,
      name,
    });
    return data;
  }

  async getStrategy(strategyId: string) {
    const { data } = await this.client.get<ApiResponse<any>>(`/api/v1/strategies/${strategyId}`);
    return data;
  }

  async updateStrategy(strategyId: string, updates: any) {
    const { data } = await this.client.patch<ApiResponse<any>>(
      `/api/v1/strategies/${strategyId}`,
      updates
    );
    return data;
  }

  // ============ CONTEXT ITEMS ENDPOINTS ============

  async addContextItem(strategyId: string, type: string, content: any) {
    const formData = new FormData();
    formData.append('type', type); // 'text', 'url', 'file'
    formData.append('content', content);

    const { data } = await this.client.post<ApiResponse<any>>(
      `/api/v1/strategies/${strategyId}/context-items`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return data;
  }

  async getContextItems(strategyId: string) {
    const { data } = await this.client.get<ApiResponse<any>>(
      `/api/v1/strategies/${strategyId}/context-items`
    );
    return data;
  }

  async deleteContextItem(strategyId: string, itemId: string) {
    const { data } = await this.client.delete<ApiResponse<any>>(
      `/api/v1/strategies/${strategyId}/context-items/${itemId}`
    );
    return data;
  }

  // ============ ANALYSIS ENDPOINTS ============

  async submitAnalysis(strategyId: string, payload: {
    aisasPosition: number;
    contextSummary: string;
    additionalNotes?: string;
  }) {
    const { data } = await this.client.post<ApiResponse<any>>(
      `/api/v1/strategies/${strategyId}/analysis`,
      payload
    );
    return data;
  }

  async getAnalysisResults(strategyId: string) {
    const { data } = await this.client.get<ApiResponse<any>>(
      `/api/v1/strategies/${strategyId}/analysis-results`
    );
    return data;
  }

  // ============ AGENT STREAMING ============

  async *streamAnalysis(strategyId: string) {
    const response = await this.client.get(
      `/api/v1/strategies/${strategyId}/analysis/stream`,
      {
        responseType: 'stream',
      }
    );

    const reader = response.data.getReader();
    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        const lines = text.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6));
              yield event;
            } catch (e) {
              // Invalid JSON, skip
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  // ============ TOKEN & COST TRACKING ============

  async getTokenUsage(strategyId?: string) {
    const url = strategyId
      ? `/api/v1/token-usage/${strategyId}`
      : '/api/v1/token-usage';

    const { data } = await this.client.get<ApiResponse<any>>(url);
    return data;
  }

  async getBudgetStatus() {
    const { data } = await this.client.get<ApiResponse<any>>('/api/v1/budget-status');
    return data;
  }

  // ============ SUBSCRIPTION ENDPOINTS ============

  async getSubscriptionTier() {
    const { data } = await this.client.get<ApiResponse<any>>('/api/v1/subscription/tier');
    return data;
  }

  async getFeatureFlags() {
    const { data } = await this.client.get<ApiResponse<any>>('/api/v1/features');
    return data;
  }

  // ============ PRICING TIER ENDPOINTS ============

  async setPricingTier(tier: 'basic' | 'pro' | 'enterprise') {
    const { data } = await this.client.post<ApiResponse<any>>('/api/v1/dev/set-tier', {
      tier,
    });
    return data;
  }

  async getCurrentTier() {
    const { data } = await this.client.get<ApiResponse<any>>('/api/v1/dev/current-tier');
    return data;
  }

  // ============ HEALTH CHECK ============

  async healthCheck() {
    const { data } = await this.client.get<ApiResponse<any>>('/api/v1/health');
    return data;
  }
}

// Export singleton instance
export const apiClient = new RaptorFlowAPI({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
});

export default apiClient;
```

### 1.2 Create Auth Hook with Backend Sync

```typescript
// lib/hooks/useAuth.ts
import { useEffect, useState } from 'react';
import { useSupabaseClient, useSession } from '@supabase/auth-helpers-react';
import { apiClient } from '@/lib/api-client';
import { AuthSession } from '@supabase/supabase-js';

export function useAuth() {
  const supabase = useSupabaseClient();
  const session = useSession();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sync session with API client
  useEffect(() => {
    if (session) {
      apiClient.setSession(session);
    }
  }, [session]);

  // Listen for unauthorized events
  useEffect(() => {
    const handleUnauthorized = async () => {
      await supabase.auth.signOut();
      window.location.href = '/auth/login';
    };

    window.addEventListener('unauthorized', handleUnauthorized);
    return () => window.removeEventListener('unauthorized', handleUnauthorized);
  }, [supabase]);

  const signUp = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const { error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: `${window.location.origin}/auth/callback`,
        },
      });
      if (error) throw error;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign up failed');
    } finally {
      setIsLoading(false);
    }
  };

  const signIn = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      if (error) throw error;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign in failed');
    } finally {
      setIsLoading(false);
    }
  };

  const signOut = async () => {
    setIsLoading(true);
    try {
      await supabase.auth.signOut();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign out failed');
    } finally {
      setIsLoading(false);
    }
  };

  return {
    session,
    isLoading,
    error,
    signUp,
    signIn,
    signOut,
    isAuthenticated: !!session,
  };
}
```

---

## 🤖 STEP 2: Agent Integration & Real-time Streaming

### 2.1 Create Agent Service Hook

```typescript
// lib/hooks/useAgent.ts
import { useCallback, useRef, useState } from 'react';
import { apiClient } from '@/lib/api-client';

export interface AgentEvent {
  type: 'start' | 'thinking' | 'progress' | 'tool_call' | 'result' | 'error' | 'done';
  data: any;
  timestamp: number;
}

export function useAgent() {
  const [isRunning, setIsRunning] = useState(false);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const startAnalysis = useCallback(
    async (strategyId: string) => {
      setIsRunning(true);
      setError(null);
      setEvents([]);
      abortControllerRef.current = new AbortController();

      try {
        // Start the analysis
        const response = await apiClient.submitAnalysis(strategyId, {
          aisasPosition: 3,
          contextSummary: 'Analysis started',
        });

        if (response?.error) {
          throw new Error(response.error.message);
        }

        // Stream events from server
        const eventGenerator = apiClient.streamAnalysis(strategyId);

        for await (const event of eventGenerator) {
          if (abortControllerRef.current?.signal.aborted) {
            break;
          }

          const agentEvent: AgentEvent = {
            ...event,
            timestamp: Date.now(),
          };

          setEvents((prev) => [...prev, agentEvent]);

          // Update UI based on event type
          switch (event.type) {
            case 'error':
              setError(event.data.message);
              break;
            case 'done':
              setIsRunning(false);
              break;
          }
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Analysis failed';
        setError(message);
        setIsRunning(false);
      }
    },
    []
  );

  const cancel = useCallback(() => {
    abortControllerRef.current?.abort();
    setIsRunning(false);
  }, []);

  return {
    isRunning,
    events,
    error,
    startAnalysis,
    cancel,
  };
}
```

### 2.2 Agent Visualization Component

```typescript
// components/AgentMonitor.tsx
import { useAgent, AgentEvent } from '@/lib/hooks/useAgent';
import { useEffect, useState } from 'react';

export function AgentMonitor({ strategyId }: { strategyId: string }) {
  const { isRunning, events, error, startAnalysis, cancel } = useAgent();
  const [displayText, setDisplayText] = useState('');

  useEffect(() => {
    const latestEvent = events[events.length - 1];
    if (latestEvent?.type === 'result' || latestEvent?.type === 'thinking') {
      setDisplayText(latestEvent.data?.text || '');
    }
  }, [events]);

  return (
    <div className="agent-monitor bg-slate-900 rounded-lg p-6 border border-slate-700">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-white">
          🤖 Agent Processing
        </h3>
        {isRunning && (
          <button
            onClick={cancel}
            className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded"
          >
            Cancel
          </button>
        )}
      </div>

      {/* Progress Indicator */}
      <div className="mb-4 space-y-2">
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              isRunning ? 'bg-green-500 animate-pulse' : 'bg-slate-500'
            }`}
          />
          <span className="text-sm text-slate-400">
            {isRunning ? 'Processing...' : 'Ready'}
          </span>
        </div>
      </div>

      {/* Token Usage */}
      <div className="mb-4 text-xs text-slate-400">
        Events: {events.length}
      </div>

      {/* Display Area */}
      <div className="bg-slate-800 rounded p-4 min-h-[200px] max-h-[400px] overflow-y-auto">
        {error && (
          <div className="text-red-500 text-sm mb-4">Error: {error}</div>
        )}

        {displayText && (
          <div className="text-slate-200 text-sm whitespace-pre-wrap font-mono">
            {displayText}
          </div>
        )}

        {!displayText && !isRunning && events.length === 0 && (
          <div className="text-slate-500 text-sm">
            Click "Analyze" to start agent processing...
          </div>
        )}
      </div>

      {/* Event Log */}
      <div className="mt-4 max-h-[200px] overflow-y-auto border-t border-slate-700 pt-4">
        <div className="text-xs text-slate-500 space-y-1">
          {events.map((event, idx) => (
            <div key={idx} className="flex gap-2">
              <span className="text-slate-600">[{event.type}]</span>
              <span className="text-slate-400">
                {typeof event.data === 'string'
                  ? event.data
                  : JSON.stringify(event.data).slice(0, 50)}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Action Button */}
      {!isRunning && (
        <button
          onClick={() => startAnalysis(strategyId)}
          className="mt-4 w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-medium"
        >
          Start Analysis
        </button>
      )}
    </div>
  );
}
```

---

## 💰 STEP 3: Token & Cost Tracking Display

### 3.1 Token Usage Hook

```typescript
// lib/hooks/useTokenUsage.ts
import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';

export interface TokenUsageData {
  session_tokens: number;
  total_tokens: number;
  estimated_cost: number;
  calls_made: number;
  cache_hits: number;
  daily_limit: number;
  monthly_limit: number;
  daily_remaining: number;
  monthly_remaining: number;
  budget_exceeded: boolean;
}

export function useTokenUsage(strategyId?: string) {
  const [usage, setUsage] = useState<TokenUsageData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchUsage = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.getTokenUsage(strategyId);
      if (response?.data) {
        setUsage(response.data);
      } else if (response?.error) {
        setError(response.error.message);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch usage');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsage();
    // Refresh every 5 seconds
    const interval = setInterval(fetchUsage, 5000);
    return () => clearInterval(interval);
  }, [strategyId]);

  return { usage, isLoading, error, refetch: fetchUsage };
}
```

### 3.2 Token Display Component

```typescript
// components/TokenCounter.tsx
import { useTokenUsage } from '@/lib/hooks/useTokenUsage';

export function TokenCounter({ strategyId }: { strategyId: string }) {
  const { usage, isLoading } = useTokenUsage(strategyId);

  if (!usage) return null;

  const tokenPercentage = (usage.total_tokens / usage.monthly_limit) * 100;
  const costPercentage = (usage.estimated_cost / 15) * 100; // $15 monthly limit

  return (
    <div className="token-counter bg-slate-800 rounded-lg p-4 border border-slate-700">
      <h3 className="text-sm font-semibold text-white mb-3">📊 Token Usage</h3>

      {/* Token Count */}
      <div className="space-y-2 mb-4">
        <div className="flex justify-between text-xs">
          <span className="text-slate-400">Tokens Used</span>
          <span className="text-white font-mono">
            {usage.total_tokens.toLocaleString()} / {usage.monthly_limit.toLocaleString()}
          </span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
          <div
            className={`h-full ${
              tokenPercentage > 80
                ? 'bg-red-500'
                : tokenPercentage > 50
                ? 'bg-yellow-500'
                : 'bg-green-500'
            }`}
            style={{ width: `${Math.min(tokenPercentage, 100)}%` }}
          />
        </div>
      </div>

      {/* Cost Tracking */}
      <div className="space-y-2 mb-4">
        <div className="flex justify-between text-xs">
          <span className="text-slate-400">Estimated Cost</span>
          <span className="text-white font-mono">
            ${usage.estimated_cost.toFixed(2)} / $15.00
          </span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
          <div
            className={`h-full ${
              costPercentage > 80 ? 'bg-red-500' : 'bg-blue-500'
            }`}
            style={{ width: `${Math.min(costPercentage, 100)}%` }}
          />
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="bg-slate-700 rounded p-2">
          <div className="text-slate-400 text-xs">Calls</div>
          <div className="text-white font-semibold">{usage.calls_made}</div>
        </div>
        <div className="bg-slate-700 rounded p-2">
          <div className="text-slate-400 text-xs">Cache Hits</div>
          <div className="text-white font-semibold">{usage.cache_hits}</div>
        </div>
        <div className="bg-slate-700 rounded p-2">
          <div className="text-slate-400 text-xs">Today Remaining</div>
          <div className="text-white font-semibold">${usage.daily_remaining.toFixed(2)}</div>
        </div>
        <div className="bg-slate-700 rounded p-2">
          <div className="text-slate-400 text-xs">This Month</div>
          <div className="text-white font-semibold">${usage.monthly_remaining.toFixed(2)}</div>
        </div>
      </div>

      {/* Budget Warning */}
      {usage.budget_exceeded && (
        <div className="mt-3 p-2 bg-red-500/10 border border-red-500 rounded text-xs text-red-400">
          ⚠️ Monthly budget limit reached. Upgrade to continue.
        </div>
      )}
    </div>
  );
}
```

---

## 💳 STEP 4: Pricing Tier Selector (Dev Mode Feature)

### 4.1 Create Tier Selector Hook

```typescript
// lib/hooks/usePricingTier.ts
import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api-client';

export type PricingTier = 'basic' | 'pro' | 'enterprise';

export interface TierFeatures {
  maxIcps: number;
  maxMoves: number;
  features: string[];
  monthlyPrice: number;
}

export const TIER_CONFIG: Record<PricingTier, TierFeatures> = {
  basic: {
    maxIcps: 3,
    maxMoves: 5,
    features: ['Positioning', 'Basic ICPs', 'Content Calendar'],
    monthlyPrice: 2000,
  },
  pro: {
    maxIcps: 6,
    maxMoves: 15,
    features: [
      'Positioning',
      'Advanced ICPs',
      'Content Calendar',
      'Trend Monitoring',
      'Strategy Layer',
    ],
    monthlyPrice: 3500,
  },
  enterprise: {
    maxIcps: 9,
    maxMoves: 999,
    features: [
      'Everything in Pro',
      'Knowledge Graph',
      'White-label',
      'Custom Integrations',
      'Dedicated Support',
    ],
    monthlyPrice: 5000,
  },
};

export function usePricingTier() {
  const [currentTier, setCurrentTier] = useState<PricingTier>('basic');
  const [isLoading, setIsLoading] = useState(false);

  const fetchCurrentTier = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.getCurrentTier();
      if (response?.data?.tier) {
        setCurrentTier(response.data.tier);
      }
    } catch (err) {
      console.error('Failed to fetch tier:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const setTier = async (tier: PricingTier) => {
    setIsLoading(true);
    try {
      const response = await apiClient.setPricingTier(tier);
      if (response?.data?.tier) {
        setCurrentTier(response.data.tier);
      }
    } catch (err) {
      console.error('Failed to set tier:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      fetchCurrentTier();
    }
  }, []);

  return {
    currentTier,
    setTier,
    isLoading,
    features: TIER_CONFIG[currentTier],
  };
}
```

### 4.2 Tier Selector Component

```typescript
// components/PricingTierSelector.tsx
import { usePricingTier, TIER_CONFIG, PricingTier } from '@/lib/hooks/usePricingTier';
import { useState } from 'react';

export function PricingTierSelector() {
  const { currentTier, setTier, isLoading, features } = usePricingTier();
  const [showDetails, setShowDetails] = useState(false);

  if (process.env.NODE_ENV !== 'development') {
    return null; // Only show in dev mode
  }

  const tiers: PricingTier[] = ['basic', 'pro', 'enterprise'];

  return (
    <div className="pricing-tier-selector bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-white">
          💳 Dev Mode: Pricing Tier
        </h3>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-xs text-slate-400 hover:text-white"
        >
          {showDetails ? 'Hide' : 'Show'} Details
        </button>
      </div>

      {/* Tier Selector */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        {tiers.map((tier) => (
          <button
            key={tier}
            onClick={() => setTier(tier)}
            disabled={isLoading}
            className={`p-3 rounded-lg border-2 transition-all ${
              currentTier === tier
                ? 'border-blue-500 bg-blue-500/10 text-white'
                : 'border-slate-600 bg-slate-700 text-slate-300 hover:border-slate-500'
            } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <div className="font-semibold capitalize">{tier}</div>
            <div className="text-xs text-slate-400">
              ${TIER_CONFIG[tier].monthlyPrice}
            </div>
          </button>
        ))}
      </div>

      {/* Current Tier Info */}
      <div className="bg-slate-700 rounded-lg p-4 mb-4">
        <h4 className="text-sm font-semibold text-white mb-2">Current Tier: {currentTier}</h4>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <span className="text-slate-400">Max ICPs:</span>
            <span className="text-white ml-2 font-semibold">{features.maxIcps}</span>
          </div>
          <div>
            <span className="text-slate-400">Max Moves:</span>
            <span className="text-white ml-2 font-semibold">{features.maxMoves}</span>
          </div>
        </div>
      </div>

      {/* Features List (if showing details) */}
      {showDetails && (
        <div className="bg-slate-700 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-white mb-2">Available Features</h4>
          <ul className="space-y-1">
            {features.features.map((feature, idx) => (
              <li key={idx} className="text-sm text-slate-300 flex items-center gap-2">
                <span className="text-green-500">✓</span>
                {feature}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

### 4.3 Integration in Dashboard

```typescript
// pages/dashboard.tsx
import { PricingTierSelector } from '@/components/PricingTierSelector';
import { TokenCounter } from '@/components/TokenCounter';
import { AgentMonitor } from '@/components/AgentMonitor';

export default function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Dev Mode Features */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PricingTierSelector />
        <TokenCounter strategyId={strategyId} />
      </div>

      {/* Agent Monitor */}
      <AgentMonitor strategyId={strategyId} />

      {/* Rest of dashboard... */}
    </div>
  );
}
```

---

## 🔌 STEP 5: Backend API Endpoints Setup

### 5.1 Create Missing Endpoints

```python
# backend/app/api/v1/endpoints/strategy.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.models import User, StrategyWorkspace, StrategyContextItem
from app.core.database import get_db

router = APIRouter(prefix="/strategies", tags=["strategies"])

@router.post("")
async def create_strategy(
    name: str,
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new strategy"""
    try:
        strategy = StrategyWorkspace(
            name=name,
            workspace_id=workspace_id,
            created_by_id=current_user.id
        )
        db.add(strategy)
        await db.commit()
        await db.refresh(strategy)
        return strategy
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{strategy_id}")
async def get_strategy(
    strategy_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get strategy details"""
    strategy = await db.get(StrategyWorkspace, strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy

@router.post("/{strategy_id}/context-items")
async def add_context_item(
    strategy_id: str,
    type: str,  # 'text', 'url', 'file'
    content: str | UploadFile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add context item to strategy"""
    strategy = await db.get(StrategyWorkspace, strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    # Process file if needed
    if type == "file" and isinstance(content, UploadFile):
        # Handle file upload - extract text, process with NLP
        file_content = await content.read()
        # ... process file ...

    context_item = StrategyContextItem(
        strategy_id=strategy_id,
        type=type,
        content=content if isinstance(content, str) else str(file_content),
        created_by_id=current_user.id
    )
    db.add(context_item)
    await db.commit()
    await db.refresh(context_item)
    return context_item

@router.get("/{strategy_id}/context-items")
async def get_context_items(
    strategy_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all context items for strategy"""
    # Query context items
    items = await db.execute(
        select(StrategyContextItem).where(
            StrategyContextItem.strategy_id == strategy_id
        )
    )
    return items.scalars().all()

@router.post("/{strategy_id}/analysis")
async def submit_analysis(
    strategy_id: str,
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit analysis request to agents"""
    strategy = await db.get(StrategyWorkspace, strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    # Create analysis job and queue
    analysis_job = AnalysisJob(
        strategy_id=strategy_id,
        created_by_id=current_user.id,
        aisas_position=payload.get('aisasPosition'),
        context_summary=payload.get('contextSummary')
    )
    db.add(analysis_job)
    await db.commit()

    # Start orchestrator agent
    from app.agents.orchestrator import OrchestratorAgent
    agent = OrchestratorAgent()
    # Queue analysis task

    return {"analysis_id": analysis_job.id, "status": "queued"}

@router.get("/{strategy_id}/analysis/stream")
async def stream_analysis(
    strategy_id: str,
    current_user: User = Depends(get_current_user)
):
    """Stream analysis results with Server-Sent Events"""
    from fastapi.responses import StreamingResponse

    async def generate():
        # Stream events from agent processing
        agent_events = get_agent_stream(strategy_id)
        async for event in agent_events:
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/{strategy_id}/analysis-results")
async def get_analysis_results(
    strategy_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analysis results"""
    # Query completed analysis
    results = await db.execute(
        select(AnalysisResult).where(
            AnalysisResult.strategy_id == strategy_id
        ).order_by(AnalysisResult.created_at.desc())
    )
    return results.scalars().all()
```

### 5.2 Token Usage Endpoints

```python
# backend/app/api/v1/endpoints/tokens.py
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.models import User
from app.shared.token_counter import TokenCounter

router = APIRouter(prefix="/token-usage", tags=["tokens"])

@router.get("")
async def get_token_usage(
    current_user: User = Depends(get_current_user)
):
    """Get current token usage for user"""
    counter = TokenCounter()
    usage = counter.get_user_stats(current_user.id)

    return {
        "data": {
            "session_tokens": usage.get('session_tokens', 0),
            "total_tokens": usage.get('total_tokens', 0),
            "estimated_cost": usage.get('estimated_cost', 0),
            "calls_made": usage.get('calls_made', 0),
            "cache_hits": usage.get('cache_hits', 0),
            "daily_limit": 50000,  # tokens
            "monthly_limit": 1000000,
            "daily_remaining": max(0, 50000 - usage.get('daily_tokens', 0)),
            "monthly_remaining": max(0, 1000000 - usage.get('monthly_tokens', 0)),
            "budget_exceeded": usage.get('budget_exceeded', False)
        }
    }

@router.get("/{strategy_id}")
async def get_strategy_token_usage(
    strategy_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get token usage for specific strategy"""
    counter = TokenCounter()
    usage = counter.get_strategy_stats(strategy_id)

    return {
        "data": {
            "strategy_id": strategy_id,
            "total_tokens": usage.get('total_tokens', 0),
            "estimated_cost": usage.get('estimated_cost', 0),
            "calls_made": usage.get('calls_made', 0),
            "breakdown": usage.get('breakdown', {})
        }
    }

@router.get("/budget-status")
async def get_budget_status(
    current_user: User = Depends(get_current_user)
):
    """Get current budget status"""
    from app.middleware.budget_controller import BudgetController

    controller = BudgetController()
    status = controller.get_user_budget_status(current_user.id)

    return {"data": status}
```

### 5.3 Pricing Tier Endpoints (Dev Mode)

```python
# backend/app/api/v1/endpoints/dev.py
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.models import User
import os

router = APIRouter(prefix="/dev", tags=["development"])

# Dev mode tier storage (in-memory for demo)
_dev_tiers = {}

@router.post("/set-tier")
async def set_dev_tier(
    tier: str,
    current_user: User = Depends(get_current_user)
):
    """Set pricing tier for development/testing"""
    if os.getenv("EXECUTION_MODE") != "dev":
        raise HTTPException(status_code=403, detail="Only available in dev mode")

    if tier not in ["basic", "pro", "enterprise"]:
        raise HTTPException(status_code=400, detail="Invalid tier")

    _dev_tiers[current_user.id] = tier

    tier_config = {
        "basic": {"max_icps": 3, "max_moves": 5},
        "pro": {"max_icps": 6, "max_moves": 15},
        "enterprise": {"max_icps": 9, "max_moves": 999}
    }

    return {
        "data": {
            "tier": tier,
            "config": tier_config[tier],
            "message": f"Tier set to {tier} for testing"
        }
    }

@router.get("/current-tier")
async def get_dev_tier(
    current_user: User = Depends(get_current_user)
):
    """Get current dev tier"""
    if os.getenv("EXECUTION_MODE") != "dev":
        raise HTTPException(status_code=403, detail="Only available in dev mode")

    tier = _dev_tiers.get(current_user.id, "basic")

    return {
        "data": {
            "tier": tier,
            "dev_mode": True
        }
    }
```

---

## 📝 STEP 6: Integration Testing

### 6.1 Create Integration Tests

```typescript
// __tests__/integration/api.test.ts
import { apiClient } from '@/lib/api-client';
import { AuthSession } from '@supabase/supabase-js';

describe('RaptorFlow API Integration', () => {
  let session: AuthSession;
  let workspaceId: string;
  let strategyId: string;

  beforeAll(async () => {
    // Setup: Get auth session
    session = await getTestSession();
    apiClient.setSession(session);
  });

  describe('Workspace Operations', () => {
    it('should create a workspace', async () => {
      const response = await apiClient.createWorkspace('Test Workspace');
      expect(response.data).toBeDefined();
      expect(response.data.name).toBe('Test Workspace');
      workspaceId = response.data.id;
    });

    it('should get workspaces', async () => {
      const response = await apiClient.getWorkspaces();
      expect(Array.isArray(response.data)).toBe(true);
      expect(response.data.length).toBeGreaterThan(0);
    });
  });

  describe('Strategy Operations', () => {
    it('should create a strategy', async () => {
      const response = await apiClient.createStrategy(
        workspaceId,
        'Test Strategy'
      );
      expect(response.data).toBeDefined();
      strategyId = response.data.id;
    });

    it('should get strategy', async () => {
      const response = await apiClient.getStrategy(strategyId);
      expect(response.data.id).toBe(strategyId);
    });
  });

  describe('Context Items', () => {
    it('should add text context item', async () => {
      const response = await apiClient.addContextItem(
        strategyId,
        'text',
        'Test context content'
      );
      expect(response.data).toBeDefined();
    });

    it('should get context items', async () => {
      const response = await apiClient.getContextItems(strategyId);
      expect(Array.isArray(response.data)).toBe(true);
    });
  });

  describe('Analysis', () => {
    it('should submit analysis', async () => {
      const response = await apiClient.submitAnalysis(strategyId, {
        aisasPosition: 3,
        contextSummary: 'Test analysis'
      });
      expect(response.data.analysis_id).toBeDefined();
      expect(response.data.status).toBe('queued');
    });
  });

  describe('Token Tracking', () => {
    it('should get token usage', async () => {
      const response = await apiClient.getTokenUsage(strategyId);
      expect(response.data).toBeDefined();
      expect(response.data.total_tokens).toBeGreaterThanOrEqual(0);
    });

    it('should get budget status', async () => {
      const response = await apiClient.getBudgetStatus();
      expect(response.data).toBeDefined();
      expect(response.data.monthly_remaining).toBeLessThanOrEqual(15);
    });
  });

  describe('Pricing Tier (Dev Mode)', () => {
    it('should set pricing tier', async () => {
      const response = await apiClient.setPricingTier('pro');
      expect(response.data.tier).toBe('pro');
    });

    it('should get current tier', async () => {
      const response = await apiClient.getCurrentTier();
      expect(response.data.tier).toBeDefined();
    });
  });
});
```

---

## ✅ IMPLEMENTATION CHECKLIST

```
FRONTEND-BACKEND INTEGRATION CHECKLIST:

API CLIENT
☐ API client with auth interceptors created
☐ All endpoints implemented
☐ Error handling in place
☐ Timeout configuration

AUTHENTICATION
☐ Supabase JWT integration
☐ Token refresh mechanism
☐ Unauthorized handling
☐ Session persistence

AGENTS & STREAMING
☐ Agent service hook created
☐ Real-time event streaming
☐ Progress indication
☐ Error display

TOKEN TRACKING
☐ Token usage hook
☐ Token counter display
☐ Cost tracking
☐ Budget warnings

PRICING TIER (Dev Mode)
☐ Tier selector component
☐ Tier persistence
☐ Feature limiting
☐ Tier switching
☐ Dev mode check

BACKEND ENDPOINTS
☐ Workspace endpoints
☐ Strategy endpoints
☐ Context item endpoints
☐ Analysis endpoints
☐ Token tracking endpoints
☐ Pricing tier endpoints (dev)
☐ SSE/WebSocket streaming

DATABASE
☐ Strategy workspace models
☐ Context item models
☐ Analysis job models
☐ Token ledger models

TESTING
☐ Integration tests created
☐ All endpoints tested
☐ Error scenarios covered
☐ Performance validated

DOCUMENTATION
☐ API documentation
☐ Integration guide
☐ Component documentation
☐ Setup instructions
```

---

## 🚀 NEXT STEPS

1. **Implement API Client** (~/lib/api-client.ts)
2. **Create Auth Hook** (~/lib/hooks/useAuth.ts)
3. **Setup Agent Service** (~/lib/hooks/useAgent.ts)
4. **Add Token Tracking** (~/lib/hooks/useTokenUsage.ts)
5. **Create Tier Selector** (~/lib/hooks/usePricingTier.ts)
6. **Build Components** (~/components/*)
7. **Create Backend Endpoints** (~/backend/app/api/v1/*)
8. **Run Integration Tests**
9. **Deploy and Validate**

---

**Status: READY FOR IMPLEMENTATION** ✅
