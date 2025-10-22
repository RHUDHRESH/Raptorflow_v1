/**
 * K6 Load Testing - Baseline Performance Test
 * Tests basic page load and API response times
 *
 * Run: k6 run baseline.js
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';

/**
 * Test configuration
 */
export const options = {
  stages: [
    { duration: '2m', target: 10 },   // Warm up: 0->10 users
    { duration: '5m', target: 50 },   // Ramp up: 10->50 users
    { duration: '5m', target: 50 },   // Stay: 50 users
    { duration: '2m', target: 0 },    // Ramp down: 50->0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],  // 95% under 500ms, 99% under 1s
    http_req_failed: ['rate<0.1'],                    // Error rate < 10%
  },
};

/**
 * Setup: Run once before test
 */
export function setup() {
  console.log('Starting baseline performance test...');
  return { startTime: new Date() };
}

/**
 * Main test function
 */
export default function (data) {
  const baseUrl = __ENV.BASE_URL || 'http://localhost:3000';

  group('Homepage Load', () => {
    const response = http.get(`${baseUrl}/`);
    check(response, {
      'homepage status is 200': (r) => r.status === 200,
      'homepage load time < 3s': (r) => r.timings.duration < 3000,
      'homepage has content': (r) => r.body.length > 1000,
    });
  });

  sleep(1);

  group('Strategy Page Load', () => {
    const response = http.get(`${baseUrl}/strategy/workspace`);
    check(response, {
      'strategy page status is 200': (r) => r.status === 200,
      'strategy page load time < 3s': (r) => r.timings.duration < 3000,
      'strategy page has content': (r) => r.body.length > 1000,
    });
  });

  sleep(1);

  group('API Endpoint Performance', () => {
    // Test a typical API endpoint
    const apiResponse = http.get(`${baseUrl}/api/workspaces`);
    check(apiResponse, {
      'API status is 200': (r) => r.status === 200,
      'API response time < 500ms': (r) => r.timings.duration < 500,
      'API returns JSON': (r) => r.headers['Content-Type'].includes('application/json'),
    });

    // Test API error handling
    const errorResponse = http.get(`${baseUrl}/api/nonexistent`);
    check(errorResponse, {
      'Error endpoint returns 404': (r) => r.status === 404,
    });
  });

  sleep(2);
}

/**
 * Teardown: Run once after test
 */
export function teardown(data) {
  console.log('Baseline test completed');
  console.log(`Test duration: ${new Date() - new Date(data.startTime)} ms`);
}
