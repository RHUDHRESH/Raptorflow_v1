/**
 * K6 Load Testing - Stress Test
 * Tests system limits and breaking point
 *
 * Run: k6 run stress.js
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';

/**
 * Test configuration - Stress pattern
 */
export const options = {
  stages: [
    { duration: '2m', target: 10 },    // Normal: 10 users
    { duration: '5m', target: 100 },   // Stress: 10->100 users
    { duration: '5m', target: 200 },   // More stress: 100->200 users
    { duration: '5m', target: 300 },   // Peak stress: 200->300 users
    { duration: '3m', target: 0 },     // Ramp down: 300->0 users
  ],
  thresholds: {
    http_req_duration: ['p(99)<3000'],  // Very lenient during stress
    http_req_failed: ['rate<0.3'],      // Allow 30% failures at peak
  },
};

/**
 * Main test function
 */
export default function () {
  const baseUrl = __ENV.BASE_URL || 'http://localhost:3000';

  // Test different endpoints to distribute load
  const endpoints = [
    '/',
    '/strategy/workspace',
    '/api/workspaces',
    '/api/jobs',
  ];

  const randomEndpoint = endpoints[Math.floor(Math.random() * endpoints.length)];

  group(`Stress test - ${randomEndpoint}`, () => {
    const response = http.get(`${baseUrl}${randomEndpoint}`);
    check(response, {
      'status is 200': (r) => r.status === 200,
      'response time < 5s': (r) => r.timings.duration < 5000,
    });
  });

  // Simulate user think time, decrease as load increases
  const thinkTime = Math.max(0.5, 2 - __VU / 100);
  sleep(thinkTime);
}
