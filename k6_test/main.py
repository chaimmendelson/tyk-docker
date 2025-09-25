import json
import pandas as pd

# Paths to your k6 summary JSON files
direct_file = "direct.json"
proxy_file = "proxy.json"
output_excel = "k6_comparison.csv"

# Load JSON files
with open(direct_file, "r") as f:
    direct = json.load(f)

with open(proxy_file, "r") as f:
    proxy = json.load(f)

# Helper function to extract metrics
def extract_metrics(data):
    m = data["metrics"]
    return {
        "avg_latency": m["http_req_duration"]["avg"],
        "p90_latency": m["http_req_duration"]["p(90)"],
        "p95_latency": m["http_req_duration"]["p(95)"],
        "max_latency": m["http_req_duration"]["max"],
        "rps": m["http_reqs"]["rate"],
        "success_rate": m["checks"]["value"] * 100
    }

direct_metrics = extract_metrics(direct)
proxy_metrics = extract_metrics(proxy)

# Calculate differences
comparison = []
for key in direct_metrics:
    direct_val = direct_metrics[key]
    proxy_val = proxy_metrics[key]
    diff = proxy_val - direct_val
    pct = (diff / direct_val * 100) if direct_val != 0 else 0
    comparison.append({
        "Metric": key.replace("_", " ").title(),
        "Direct Backend": direct_val,
        "OAuth2 Proxy": proxy_val,
        "Difference": diff,
        "% Overhead": pct
    })

# Convert to DataFrame
df = pd.DataFrame(comparison)

# Save to Excel
df.to_csv(output_excel, index=False)
print(f"Comparison saved to {output_excel}")
