import http from 'k6/http';
import { check } from 'k6';
import { Counter } from 'k6/metrics';

// Chạy:  docker compose run --rm k6 run -e TARGET=http://haproxy:8081 -e URL_PATH=/api/hello /scripts/load.js
const TARGET = __ENV.TARGET || 'http://haproxy:8081';
const URL_PATH = __ENV.URL_PATH || '/api/hello';
const RATE = parseInt(__ENV.RATE || '50');          // request/giây
const DURATION = __ENV.DURATION || '60s';

export const options = {
  scenarios: {
    steady: {
      executor: 'constant-arrival-rate',            // bắn đều theo rps, KHÔNG đợi request trước xong
      rate: RATE, timeUnit: '1s', duration: DURATION,
      preAllocatedVUs: 50, maxVUs: 300,
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.05'],
    http_req_duration: ['p(95)<1000'],
  },
};

// Đếm số request mỗi bản sao phục vụ
const hit = { api1: new Counter('hit_api1'), api2: new Counter('hit_api2'), api3: new Counter('hit_api3') };
const errors = new Counter('app_errors');

export default function () {
  const res = http.get(`${TARGET}${URL_PATH}`, {
    headers: { 'X-Request-ID': `k6-${__VU}-${__ITER}` },
    timeout: '10s',
  });
  const ok = check(res, { 'status 200': (r) => r.status === 200 });
  if (!ok) { errors.add(1); return; }
  const who = res.headers['X-Served-By'];
  if (hit[who]) hit[who].add(1);
}
