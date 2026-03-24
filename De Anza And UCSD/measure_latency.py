"""
Measure average latency of main API endpoints.
"""

import time
import statistics

import requests

BASE_URL = "http://localhost:8000"

# Endpoints to measure; you can modify this list as needed.
ENDPOINTS = [
    "/",  # root (HTML or JSON)
    "/stats?format=json",
    "/departments?format=json",
    "/professors?format=json&limit=20",
    "/search?q=math&format=json&limit=20",
]

# Number of times to call each endpoint
RUNS = 30


def measure(endpoint: str, runs: int = RUNS):
    """Measure latency (in ms) for a single endpoint."""
    latencies = []
    url = f"{BASE_URL}{endpoint}"
    for _ in range(runs):
        start = time.perf_counter()
        try:
            r = requests.get(url, timeout=10)
            end = time.perf_counter()
        except requests.RequestException:
            # On network/timeout error, skip this sample
            continue

        if r.status_code == 200:
            latencies.append((end - start) * 1000.0)  # convert to ms

    return latencies


def main():
    print(f"Measuring latency against base URL: {BASE_URL}")
    print(f"Each endpoint will be called {RUNS} times.\n")

    for ep in ENDPOINTS:
        lats = measure(ep)
        if not lats:
            print(f"{ep:40s} 无成功请求（请确认服务器已启动、URL 正确）")
            continue

        avg = statistics.mean(lats)

        # Guard against too few samples for quantiles
        if len(lats) >= 20:
            p95 = statistics.quantiles(lats, n=100)[94]
        else:
            p95 = max(lats)

        print(
            f"{ep:40s} 平均延迟: {avg:7.2f} ms, "
            f"P95: {p95:7.2f} ms, 样本数: {len(lats)}"
        )


if __name__ == "__main__":
    main()




