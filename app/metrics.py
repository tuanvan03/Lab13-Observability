from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

REQUEST_LATENCIES: list[int] = []
REQUEST_COSTS: list[float] = []
REQUEST_TOKENS_IN: list[int] = []
REQUEST_TOKENS_OUT: list[int] = []
ERRORS: Counter[str] = Counter()
TRAFFIC: int = 0          # successful requests only
TOTAL_REQUESTS: int = 0   # all requests (success + error)
QUALITY_SCORES: list[float] = []

# Per-interval lists — reset after each snapshot save
INTERVAL_LATENCIES: list[int] = []
INTERVAL_QUALITY: list[float] = []
INTERVAL_TOTAL: int = 0   # all requests in interval (success + error)

HISTORY_PATH = Path(os.getenv("METRICS_HISTORY_PATH", "data/metrics_history.jsonl"))


def record_request(latency_ms: int, cost_usd: float, tokens_in: int, tokens_out: int, quality_score: float) -> None:
    global TRAFFIC, TOTAL_REQUESTS, INTERVAL_TOTAL
    TRAFFIC += 1
    TOTAL_REQUESTS += 1
    INTERVAL_TOTAL += 1
    REQUEST_LATENCIES.append(latency_ms)
    INTERVAL_LATENCIES.append(latency_ms)
    REQUEST_COSTS.append(cost_usd)
    REQUEST_TOKENS_IN.append(tokens_in)
    REQUEST_TOKENS_OUT.append(tokens_out)
    QUALITY_SCORES.append(quality_score)
    INTERVAL_QUALITY.append(quality_score)


def record_error(error_type: str) -> None:
    global TOTAL_REQUESTS, INTERVAL_TOTAL
    TOTAL_REQUESTS += 1
    INTERVAL_TOTAL += 1
    ERRORS[error_type] += 1



def percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])



def snapshot() -> dict:
    return {
        "traffic": TRAFFIC,
        "total_requests": TOTAL_REQUESTS,
        "latency_p50": percentile(REQUEST_LATENCIES, 50),
        "latency_p95": percentile(REQUEST_LATENCIES, 95),
        "latency_p99": percentile(REQUEST_LATENCIES, 99),
        "avg_cost_usd": round(mean(REQUEST_COSTS), 4) if REQUEST_COSTS else 0.0,
        "total_cost_usd": round(sum(REQUEST_COSTS), 4),
        "tokens_in_total": sum(REQUEST_TOKENS_IN),
        "tokens_out_total": sum(REQUEST_TOKENS_OUT),
        "error_breakdown": dict(ERRORS),
        "quality_avg": round(mean(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0,
    }


def save_snapshot() -> None:
    global INTERVAL_LATENCIES, INTERVAL_QUALITY, INTERVAL_TOTAL
    snap = snapshot()
    snap["ts"] = datetime.now(timezone.utc).isoformat()
    # Per-interval (windowed) stats — reflect only the last 15s
    snap["latency_p50_win"] = percentile(INTERVAL_LATENCIES, 50) if INTERVAL_LATENCIES else None
    snap["latency_p95_win"] = percentile(INTERVAL_LATENCIES, 95) if INTERVAL_LATENCIES else None
    snap["latency_p99_win"] = percentile(INTERVAL_LATENCIES, 99) if INTERVAL_LATENCIES else None
    snap["quality_avg_win"] = round(mean(INTERVAL_QUALITY), 4) if INTERVAL_QUALITY else None
    snap["requests_in_interval"] = INTERVAL_TOTAL  # includes errors
    INTERVAL_LATENCIES = []
    INTERVAL_QUALITY = []
    INTERVAL_TOTAL = 0
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(snap) + "\n")


def load_history(minutes: int) -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    cutoff = datetime.now(timezone.utc).timestamp() - (minutes * 60)
    records = []
    for line in HISTORY_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
            ts = datetime.fromisoformat(rec["ts"]).timestamp()
            if ts >= cutoff:
                records.append(rec)
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
    return records
