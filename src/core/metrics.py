"""Prometheus-compatible metrics definitions."""
from __future__ import annotations

from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter(
    "agent_api_requests_total",
    "Total number of API requests received.",
    ["endpoint", "method"],
)

REQUEST_LATENCY = Histogram(
    "agent_api_request_duration_seconds",
    "Request duration in seconds.",
    ["endpoint"],
)

AGENT_COUNT = Gauge(
    "agent_registered_total",
    "Number of currently registered agents.",
)

TASK_SUCCESS_COUNT = Counter(
    "agent_task_success_total",
    "Number of successfully completed tasks.",
    ["agent_type"],
)

TASK_FAILURE_COUNT = Counter(
    "agent_task_failure_total",
    "Number of failed tasks.",
    ["agent_type"],
)
