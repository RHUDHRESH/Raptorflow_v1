const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  // Business
  createBusiness: async (data: any) => {
    const response = await fetch(`${API_BASE}/api/intake`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  // Research
  runResearch: async (businessId: string) => {
    const response = await fetch(`${API_BASE}/api/research/${businessId}`, {
      method: 'POST'
    });
    return response.json();
  },

  getResearch: async (businessId: string) => {
    const response = await fetch(`${API_BASE}/api/research/${businessId}`);
    return response.json();
  },

  // Positioning
  generatePositioning: async (businessId: string) => {
    const response = await fetch(`${API_BASE}/api/positioning/${businessId}`, {
      method: 'POST'
    });
    return response.json();
  },

  selectPositioning: async (businessId: string, optionIndex: number) => {
    const response = await fetch(`${API_BASE}/api/positioning/${businessId}/select`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ option_index: optionIndex })
    });
    return response.json();
  },

  // ICPs
  generateIcps: async (businessId: string) => {
    const response = await fetch(`${API_BASE}/api/icps/${businessId}`, {
      method: 'POST'
    });
    return response.json();
  },

  getIcps: async (businessId: string) => {
    const response = await fetch(`${API_BASE}/api/icps/${businessId}`);
    return response.json();
  },

  // Strategy
  generateStrategy: async (businessId: string) => {
    const response = await fetch(`${API_BASE}/api/strategy/${businessId}`, {
      method: 'POST'
    });
    return response.json();
  },

  // Moves
  createMove: async (businessId: string, data: any) => {
    const response = await fetch(`${API_BASE}/api/moves?business_id=${businessId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  },

  getMoves: async (businessId: string) => {
    const response = await fetch(`${API_BASE}/api/moves/business/${businessId}`);
    return response.json();
  },

  // Analytics
  measurePerformance: async (moveId: string, metrics: any) => {
    const response = await fetch(`${API_BASE}/api/analytics/measure`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ move_id: moveId, metrics })
    });
    return response.json();
  }
};
