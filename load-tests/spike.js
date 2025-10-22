/**
 * K6 Load Testing - Spike Test
 * Tests system behavior under sudden traffic spikes
 *
 * Run: k6 run spike.js
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';

/**
 * Test configuration - Spike pattern
 */
export const options = {
  stages: [
    { duration: '1m', target: 5 },     // Normal load: 5 users
    { duration: '30s', target: 100 },  // Spike: Jump to 100 users
    { duration: '1m', target: 100 },   // Stay at spike
    { duration: '30s', target: 5 },    // Back to normal: 5 users
    { duration: '1m', target: 0 },     // Wind down
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000', 'p(99)<2000'],  // Spike thresholds more lenient
    http_req_failed: ['rate<0.15'],                    // Allow 15% errors during spike
  },
};

/**
 * Main test function
 */
export default function () {
  const baseUrl = __ENV.BASE_URL || 'http://localhost:3000';

  group('Homepage under spike', () => {
    const response = http.get(`${baseUrl}/`);
    check(response, {
      'status is 200 or 503': (r) => r.status === 200 || r.status === 503,
      'load time reasonable': (r) => r.timings.duration < 5000,
    });
  });

  sleep(0.5);

  group('Strategy page under spike', () => {
    const response = http.get(`${baseUrl}/strategy/workspace`);
    check(response, {
      'status is 200 or 503': (r) => r.status === 200 || r.status === 503,
      'load time reasonable': (r) => r.timings.duration < 5000,
    });
  });

  sleep(0.5);

  group('API under spike', () => {
    const response = http.get(`${baseUrl}/api/workspaces`);
    check(response, {
      'API responds': (r) => r.status === 200 || r.status === 503,
      'API doesn\'t timeout': (r) => r.timings.duration < 10000,
    });
  });

  sleep(1);
}
