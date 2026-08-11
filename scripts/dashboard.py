from __future__ import annotations

import argparse
import html
import json
import math
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from statistics import mean

REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"


def percentile(values: list[float], percent: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = (len(ordered) - 1) * percent / 100
    lower, upper = math.floor(rank), math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (rank - lower)


def load_records() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    records: list[dict] = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
            timestamp = datetime.fromisoformat(record["ts"].replace("Z", "+00:00"))
            record["_timestamp"] = timestamp
            records.append(record)
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
    if not records:
        return []
    newest = max(record["_timestamp"] for record in records)
    cutoff = newest - timedelta(minutes=60)
    return [record for record in records if record["_timestamp"] >= cutoff]


def panel(title: str, value: str, detail: str, threshold: str, healthy: bool) -> str:
    state = "healthy" if healthy else "breach"
    return f"""
    <section class="panel {state}">
      <div class="panel-head"><h2>{html.escape(title)}</h2><span>{state.upper()}</span></div>
      <div class="value">{html.escape(value)}</div>
      <div class="detail">{html.escape(detail)}</div>
      <div class="threshold">Threshold: {html.escape(threshold)}</div>
    </section>
    """


def render_dashboard() -> str:
    records = load_records()
    requests = [r for r in records if r.get("event") == "request_received"]
    responses = [r for r in records if r.get("event") == "response_sent"]
    failures = [r for r in records if r.get("event") == "request_failed"]
    latencies = [float(r.get("latency_ms", 0)) for r in responses]
    p50, p95, p99 = (percentile(latencies, p) for p in (50, 95, 99))
    error_rate = len(failures) / len(requests) * 100 if requests else 0.0
    cost = sum(float(r.get("cost_usd", 0)) for r in responses)
    tokens_in = sum(int(r.get("tokens_in", 0)) for r in responses)
    tokens_out = sum(int(r.get("tokens_out", 0)) for r in responses)
    quality_values = [float(r["quality_score"]) for r in responses if "quality_score" in r]
    quality = mean(quality_values) if quality_values else 0.0
    error_types: dict[str, int] = {}
    for record in failures:
        kind = str(record.get("error_type", "unknown"))
        error_types[kind] = error_types.get(kind, 0) + 1
    breakdown = ", ".join(f"{key}: {value}" for key, value in error_types.items()) or "No errors"

    panels = "".join(
        [
            panel("Latency percentiles", f"P95 {p95:.0f} ms", f"P50 {p50:.0f} ms · P99 {p99:.0f} ms", "P95 ≤ 3000 ms", p95 <= 3000),
            panel("Request traffic", f"{len(requests)} requests", f"{len(requests) / 60:.2f} requests/min", "rate ≥ 1 request/min", len(requests) / 60 >= 1),
            panel("Error rate and breakdown", f"{error_rate:.2f}%", breakdown, "error rate ≤ 2%", error_rate <= 2),
            panel("Cost over time", f"${cost:.4f}", f"Total across {len(responses)} responses", "total ≤ $2.50", cost <= 2.5),
            panel("Input and output tokens", f"{tokens_in + tokens_out:,} tokens", f"Input {tokens_in:,} · Output {tokens_out:,}", "total ≤ 50,000 tokens", tokens_in + tokens_out <= 50_000),
            panel("Quality proxy", f"{quality:.2f}", f"Mean across {len(quality_values)} responses", "mean ≥ 0.75", quality >= 0.75),
        ]
    )
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="30">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Day 13 AI Observability</title>
<style>
:root {{ color-scheme: dark; font-family: Inter, system-ui, sans-serif; background:#08111f; color:#e5edf8; }}
body {{ margin:0; padding:32px; background:radial-gradient(circle at top right,#173154,#08111f 45%); min-height:100vh; }}
header {{ display:flex; justify-content:space-between; align-items:end; margin-bottom:28px; }}
h1 {{ margin:0; font-size:30px; }} header p {{ color:#93a8c5; margin:7px 0 0; }}
.meta {{ text-align:right; color:#93a8c5; line-height:1.6; }}
.grid {{ display:grid; grid-template-columns:repeat(3,minmax(250px,1fr)); gap:18px; }}
.panel {{ background:#101d30; border:1px solid #29405f; border-radius:14px; padding:22px; box-shadow:0 12px 30px #0005; }}
.panel-head {{ display:flex; justify-content:space-between; gap:12px; align-items:center; }}
.panel h2 {{ font-size:15px; color:#b7c8df; margin:0; }}
.panel-head span {{ font-size:10px; letter-spacing:.08em; border-radius:99px; padding:5px 8px; }}
.healthy .panel-head span {{ background:#123f35; color:#5ee3b5; }} .breach .panel-head span {{ background:#51242a; color:#ff8d99; }}
.value {{ font-size:31px; font-weight:750; margin:25px 0 8px; }}
.detail {{ color:#9eb1ca; min-height:24px; }} .threshold {{ margin-top:22px; padding-top:14px; border-top:1px solid #29405f; font-size:12px; color:#7790ae; }}
footer {{ margin-top:24px; color:#7186a1; font-size:12px; }}
@media(max-width:900px) {{ .grid {{ grid-template-columns:1fr; }} header {{ align-items:start; flex-direction:column; }} .meta {{ text-align:left; margin-top:12px; }} }}
</style></head><body>
<header><div><h1>Day 13 AI Observability</h1><p>Runtime dashboard · source: data/logs.jsonl</p></div>
<div class="meta">Time range: last 60 minutes<br>Refresh: 30 seconds</div></header>
<main class="grid">{panels}</main>
<footer>{len(records)} log records in window · Generated {generated}</footer>
</body></html>"""


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        body = render_dashboard().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the Day 13 runtime dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    print(f"Dashboard: http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
