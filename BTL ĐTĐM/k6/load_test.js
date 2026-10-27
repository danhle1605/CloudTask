// k6/load_test.js
// K6 Performance & Operational Benchmark Script for Topic 8 (PaaS vs IaaS)
//
// Usage:
//   k6 run -e TARGET_URL=https://cloudtask.onrender.com --out json=k6/results_paas.json k6/load_test.js
//   k6 run -e TARGET_URL=http://<VM_IP>:5000 --out json=k6/results_iaas.json k6/load_test.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

// Custom metrics to collect required thesis indicators
export const p95ResponseTrend = new Trend('custom_req_duration');
export const errorRate = new Rate('custom_error_rate');
export const healthCheckFails = new Counter('health_check_failures');

export const options = {
  stages: [
    { duration: '30s', target: 10 },  // Ramp-up to 10 virtual users
    { duration: '1m', target: 20 },   // Sustained load at 20 virtual users
    { duration: '30s', target: 0 },   // Ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<1500'], // 95% of requests must complete below 1.5s
    'custom_error_rate': ['rate<0.05'], // Error rate under 5%
  },
};

const BASE_URL = __ENV.TARGET_URL || 'http://localhost:5000';

export default function () {
  // 1. Health check readiness probe
  const readyRes = http.get(`${BASE_URL}/health/ready`);
  const readyOk = check(readyRes, {
    'health_ready status is 200': (r) => r.status === 200,
  });
  if (!readyOk) {
    healthCheckFails.add(1);
    errorRate.add(1);
  } else {
    errorRate.add(0);
  }
  p95ResponseTrend.add(readyRes.timings.duration);

  // 2. Health check liveness probe
  const liveRes = http.get(`${BASE_URL}/health/live`);
  check(liveRes, {
    'health_live status is 200': (r) => r.status === 200,
  });

  // 3. Public landing / Login page
  const loginRes = http.get(`${BASE_URL}/login`);
  const loginOk = check(loginRes, {
    'login page loaded': (r) => r.status === 200,
  });
  if (!loginOk) {
    errorRate.add(1);
  } else {
    errorRate.add(0);
  }
  p95ResponseTrend.add(loginRes.timings.duration);

  sleep(1);
}
