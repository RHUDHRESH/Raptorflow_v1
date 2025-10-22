/**
 * K6 Load Testing - Realistic User Workflow
 * Simulates actual user behavior: login -> navigate -> analyze
 *
 * Run: k6 run workflow.js
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Counter, Trend, Gauge, Rate } from 'k6/metrics';

/**
 * Custom metrics
 */
const workflowDuration = new Trend('workflow_duration');
const loginRate = new Rate('login_success');
const analysisRate = new Rate('analysis_success');
const activeUsers = new Gauge('active_users');

/**
 * Test configuration
 */
export const options = {
  stages: [
    { duration: '2m', target: 20 },   // Warm up: 20 users
    { duration: '10m', target: 50 },  // Ramp up: 50 users
    { duration: '5m', target: 50 },   // Sustain: 50 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    'workflow_duration': ['p(95)<8000'],   // 95% of workflows complete in 8s
    'login_success': ['rate>0.95'],        // 95%+ successful logins
    'analysis_success': ['rate>0.90'],     // 90%+ successful analysis
    'http_req_duration': ['p(95)<1000'],
  },
};

/**
 * Setup
 */
export function setup() {
  return {
    baseUrl: __ENV.BASE_URL || 'http://localhost:3000',
  };
}

/**
 * Main test - User workflow
 */
export default function (data) {
  const { baseUrl } = data;
  const workflowStart = new Date();
  activeUsers.add(__VU);

  // Step 1: Login
  group('01 Login', () => {
    const loginResponse = http.post(`${baseUrl}/api/auth/login`, {
      email: `user${__VU}@example.com`,
      password: 'TestPassword123!',
    });

    const loginSuccess = check(loginResponse, {
      'login status is 200': (r) => r.status === 200,
      'login response has token': (r) => r.body.includes('token'),
    });

    loginRate.add(loginSuccess);
  });

  sleep(1);

  // Step 2: Navigate to workspace
  group('02 Load Workspace', () => {
    const workspaceResponse = http.get(`${baseUrl}/api/workspaces`);
    check(workspaceResponse, {
      'workspaces load status 200': (r) => r.status === 200,
      'workspaces load time < 500ms': (r) => r.timings.duration < 500,
    });
  });

  sleep(2);

  // Step 3: Get strategy data
  group('03 Load Strategy', () => {
    const strategyResponse = http.get(`${baseUrl}/api/strategies/${__VU}`);
    check(strategyResponse, {
      'strategy load status is 200 or 404': (r) => r.status === 200 || r.status === 404,
      'strategy load time < 1s': (r) => r.timings.duration < 1000,
    });
  });

  sleep(1);

  // Step 4: Submit analysis request
  group('04 Submit Analysis', () => {
    const analysisPayload = {
      workspaceId: `workspace-${__VU}`,
      contextItems: [
        {
          type: 'text',
          content: `Market analysis for user ${__VU}`,
        },
      ],
      aisasPosition: 3,
    };

    const analysisResponse = http.post(
      `${baseUrl}/api/analysis`,
      JSON.stringify(analysisPayload),
      {
        headers: { 'Content-Type': 'application/json' },
      }
    );

    const analysisSuccess = check(analysisResponse, {
      'analysis status is 200': (r) => r.status === 200,
      'analysis response time < 2s': (r) => r.timings.duration < 2000,
      'analysis returns results': (r) => r.body.length > 100,
    });

    analysisRate.add(analysisSuccess);
  });

  sleep(2);

  // Step 5: Get results
  group('05 Fetch Results', () => {
    const resultsResponse = http.get(`${baseUrl}/api/analysis/${__VU}/results`);
    check(resultsResponse, {
      'results status is 200 or 404': (r) => r.status === 200 || r.status === 404,
      'results load time < 1s': (r) => r.timings.duration < 1000,
    });
  });

  sleep(1);

  // Record workflow duration
  const workflowEnd = new Date();
  const duration = workflowEnd - workflowStart;
  workflowDuration.add(duration);
}

/**
 * Teardown
 */
export function teardown(data) {
  console.log('Workflow test completed');
}
