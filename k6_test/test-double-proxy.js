import http from 'k6/http';
import { check } from 'k6';
import { Trend } from 'k6/metrics';

// Custom metrics
let latencyTrend = new Trend('latency_ms');

export let options = {
  scenarios: {
    test_scenario: {
      executor: 'constant-arrival-rate',
      rate: 150,                  // number of requests
      timeUnit: '1s',          // per 1 seconds
      duration: '1m',           // total duration
      preAllocatedVUs: 150,       // VUs to allocate
      maxVUs: 150,               // max VUs allowed
    },
  },
};

export default function () {
  const scenario = __ENV.SCENARIO || "direct"; // "direct" or "proxy"
  let url;

  if (scenario === "proxy") {
    url = "http://localhost:8080/test-proxy/";
  } else {
    url = "http://localhost:8080/test/";
  }

  const res = http.get(url);

  latencyTrend.add(res.timings.duration);

  check(res, {
    "status is 200": (r) => r.status === 200,
  });
}
