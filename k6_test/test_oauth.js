import http from 'k6/http';
import { check } from 'k6';
import { Trend } from 'k6/metrics';

// Custom metrics
let latencyTrend = new Trend('latency_ms');

export let options = {
  vus: 100,           // number of virtual users
  duration: '2m',   // total test duration
//   thresholds: {
//     'http_req_duration': ['p(95)<500'], // 95% of requests should be below 500ms
//   },
};

export default function () {
  const useOAuth = __ENV.OAUTH2 === 'true'; // read environment variable
  let url;
  let headers = {};

  if (useOAuth) {
    url = "http://localhost:4180/test/hello";
    const cookieValue = "djIuWDI5aGRYUm9NbDl3Y205NGVTMDFaR0l5WVRkbU9EaGlZekF6TXpZd01URXdaVEJqWTJabU5qaGlORGM0T0EuYlRLY0tLSjVxZTJKcV9XU0MzNU5tQQ==|1758083992|HphDf8u9_r6_DvQg3ER6iIYVxsjA4FPuloRNoDOZ47E=";

    const jar = http.cookieJar();
    jar.set(url, "_oauth2_proxy", cookieValue);
  } else {
    url = "http://localhost:8080/test/hello"; // direct service, no cookie
  }

  const res = http.get(url, { headers });

  // Track latency
  latencyTrend.add(res.timings.duration);

  check(res, {
    "status is 200": (r) => r.status === 200,
  });
}
