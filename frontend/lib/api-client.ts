/**
 * RaptorFlow API Client
 * Handles all API communication with auth interceptors
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { AuthSession } from '@supabase/supabase-js';

// ============ TYPES ============

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

interface CreateStrategyPayload {
  workspace_id: string;
  name: string;
  description?: string;
}

interface UpdateStrategyPayload {
  name?: string;
  description?: string;
}

interface ContextItemPayload {
  type: 'text' | 'url' | 'file';
  content: string;
}

interface AnalysisPayload {
  aisasPosition: number;
  contextSummary: string;
  additionalNotes?: string;
}

interface AgentEvent {
  type: 'start' | 'thinking' | 'progress' | 'tool_call' | 'result' | 'error' | 'done';
  data: any;
  timestamp?: number;
  agent?: string;
  step?: number;
}

// ============ API CLIENT CLASS ============

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
    this.client.interceptors.request.use(
      (config) => {
        if (this.session?.access_token) {
          config.headers.Authorization = `Bearer ${this.session.access_token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiResponse<any>>) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - emit event for app to handle
          this.handleUnauthorized();
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Set the current auth session (JWT token)
   */
  setSession(session: AuthSession | null) {
    this.session = session;
  }

  /**
   * Handle unauthorized access
   */
  private handleUnauthorized() {
    // Emit event for app to handle logout
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('unauthorized'));
    }
  }

  // ============ WORKSPACE ENDPOINTS ============

  async getWorkspaces() {
    const response = await this.client.get<ApiResponse<any>>('/api/v1/users/workspaces');
    return response.data;
  }

  async createWorkspace(name: string, description?: string) {
    const response = await this.client.post<ApiResponse<any>>('/api/v1/workspaces', {
      name,
      description,
    });
    return response.data;
  }

  async getWorkspace(id: string) {
    const response = await this.client.get<ApiResponse<any>>(`/api/v1/workspaces/${id}`);
    return response.data;
  }

  async updateWorkspace(id: string, updates: any) {
    const response = await this.client.patch<ApiResponse<any>>(
      `/api/v1/workspaces/${id}`,
      updates
    );
    return response.data;
  }

  async deleteWorkspace(id: string) {
    const response = await this.client.delete<ApiResponse<any>>(`/api/v1/workspaces/${id}`);
    return response.data;
  }

  // ============ STRATEGY ENDPOINTS ============

  async createStrategy(payload: CreateStrategyPayload) {
    const response = await this.client.post<ApiResponse<any>>('/api/v1/strategies', payload);
    return response.data;
  }

  async getStrategy(strategyId: string) {
    const response = await this.client.get<ApiResponse<any>>(`/api/v1/strategies/${strategyId}`);
    return response.data;
  }

  async getStrategies(workspaceId?: string) {
    let url = '/api/v1/strategies';
    if (workspaceId) {
      url += `?workspace_id=${workspaceId}`;
    }
    const response = await this.client.get<ApiResponse<any>>(url);
    return response.data;
  }

  async updateStrategy(strategyId: string, updates: UpdateStrategyPayload) {
    const response = await this.client.patch<ApiResponse<any>>(
      `/api/v1/strategies/${strategyId}`,
      updates
    );
    return response.data;
  }

  async deleteStrategy(strategyId: string) {
    const response = await this.client.delete<ApiResponse<any>>(`/api/v1/strategies/${strategyId}`);
    return response.data;
  }

  // ============ CONTEXT ITEMS ENDPOINTS ============

  async addContextItem(strategyId: string, type: string, content: string) {
    const formData = new FormData();
    formData.append('type', type);
    formData.append('content', content);

    const response = await this.client.post<ApiResponse<any>>(
      `/api/v1/strategies/${strategyId}/context-items`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  async getContextItems(strategyId: string) {
    const response = await this.client.get<ApiResponse<any>>(
      `/api/v1/strategies/${strategyId}/context-items`
    );
    return response.data;
  }

  async deleteContextItem(strategyId: string, itemId: string) {
    const response = await this.client.delete<ApiResponse<any>>(
      `/api/v1/strategies/${strategyId}/context-items/${itemId}`
    );
    return response.data;
  }

  // ============ ANALYSIS ENDPOINTS ============

  async submitAnalysis(strategyId: string, payload: AnalysisPayload) {
    const response = await this.client.post<ApiResponse<any>>(
      `/api/v1/strategies/${strategyId}/analysis`,
      payload
    );
    return response.data;
  }

  async getAnalysisResults(strategyId: string) {
    const response = await this.client.get<ApiResponse<any>>(
      `/api/v1/strategies/${strategyId}/analysis-results`
    );
    return response.data;
  }

  async getAnalysisStatus(analysisId: string) {
    const response = await this.client.get<ApiResponse<any>>(
      `/api/v1/analysis/${analysisId}/status`
    );
    return response.data;
  }

  // ============ AGENT STREAMING ============

  /**
   * Stream analysis events from backend
   * Yields AgentEvent objects as they arrive
   */
  async *streamAnalysis(strategyId: string): AsyncGenerator<AgentEvent> {
    try {
      const response = await this.client.get(
        `/api/v1/strategies/${strategyId}/analysis/stream`,
        {
          responseType: 'stream',
          timeout: 120000, // 2 minute timeout for streaming
        }
      );

      // For browser environment
      if (response.data instanceof ReadableStream) {
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
                  const event = JSON.parse(line.slice(6)) as AgentEvent;
                  event.timestamp = event.timestamp || Date.now();
                  yield event;
                } catch (e) {
                  // Invalid JSON, skip
                  console.warn('Failed to parse SSE event:', line);
                }
              }
            }
          }
        } finally {
          reader.releaseLock();
        }
      }
    } catch (error) {
      console.error('Stream error:', error);
      throw error;
    }
  }

  // ============ TOKEN & COST TRACKING ============

  async getTokenUsage(strategyId?: string) {
    let url = '/api/v1/token-usage';
    if (strategyId) {
      url = `/api/v1/token-usage/${strategyId}`;
    }
    const response = await this.client.get<ApiResponse<any>>(url);
    return response.data;
  }

  async getBudgetStatus() {
    const response = await this.client.get<ApiResponse<any>>('/api/v1/budget-status');
    return response.data;
  }

  // ============ SUBSCRIPTION ENDPOINTS ============

  async getSubscriptionTier() {
    const response = await this.client.get<ApiResponse<any>>('/api/v1/subscription/tier');
    return response.data;
  }

  async getFeatureFlags() {
    const response = await this.client.get<ApiResponse<any>>('/api/v1/features');
    return response.data;
  }

  // ============ PRICING TIER ENDPOINTS (Dev Mode) ============

  /**
   * Set pricing tier for testing (dev mode only)
   */
  async setPricingTier(tier: 'basic' | 'pro' | 'enterprise') {
    const response = await this.client.post<ApiResponse<any>>('/api/v1/dev/set-tier', {
      tier,
    });
    return response.data;
  }

  /**
   * Get current pricing tier (dev mode)
   */
  async getCurrentTier() {
    const response = await this.client.get<ApiResponse<any>>('/api/v1/dev/current-tier');
    return response.data;
  }

  // ============ HEALTH CHECK ============

  async healthCheck() {
    const response = await this.client.get<ApiResponse<any>>('/api/v1/health');
    return response.data;
  }

  async checkDatabaseHealth() {
    const response = await this.client.get<ApiResponse<any>>('/api/v1/health/db');
    return response.data;
  }

  async checkRedisHealth() {
    const response = await this.client.get<ApiResponse<any>>('/api/v1/health/redis');
    return response.data;
  }
}

// ============ SINGLETON INSTANCE ============

export const apiClient = new RaptorFlowAPI({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
});

export default apiClient;

// ============ TYPE EXPORTS ============

export type { ApiResponse, ApiClientConfig, AgentEvent };
