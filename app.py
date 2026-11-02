import json
import logging
import os
import sys
import time
from datetime import datetime, timezone

from flask import Flask, Response, g, jsonify, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)


APP_VERSION = "1.0.1"

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests.",
    ["method", "endpoint", "status"],
)
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["endpoint"],
)
APP_INFO = Gauge(
    "app_info",
    "Application information.",
    ["version", "environment"],
)


def get_environment():
    return os.getenv("ENVIRONMENT", "development")


def fault_injection_enabled():
    return os.getenv("ENABLE_FAULT_INJECTION", "false").strip().lower() == "true"


def configure_logger():
    logger = logging.getLogger("system_health_dashboard")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

    return logger


logger = configure_logger()
app = Flask(__name__)


@app.before_request
def start_request_metrics():
    g.request_started_at = time.perf_counter()
    g.request_log_level = logging.INFO
    g.request_log_message = "Request completed"


@app.after_request
def record_request(response):
    endpoint = request.path
    duration = time.perf_counter() - g.request_started_at
    status = str(response.status_code)

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status=status,
    ).inc()
    REQUEST_DURATION.labels(endpoint=endpoint).observe(duration)

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "level": logging.getLevelName(g.request_log_level),
        "message": g.request_log_message,
        "endpoint": endpoint,
        "method": request.method,
        "status": response.status_code,
        "environment": get_environment(),
    }
    logger.log(g.request_log_level, json.dumps(log_entry, separators=(",", ":")))

    return response


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "UP"}), 200


@app.route("/version", methods=["GET"])
def version():
    return jsonify({"version": APP_VERSION}), 200


@app.route("/environment", methods=["GET"])
def environment():
    return jsonify({"environment": get_environment()}), 200


@app.route("/metrics", methods=["GET"])
def metrics():
    APP_INFO.labels(version=APP_VERSION, environment=get_environment()).set(1)
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/simulate-error", methods=["GET"])
def simulate_error():
    if not fault_injection_enabled():
        return jsonify({"error": "Fault injection is disabled"}), 404

    g.request_log_level = logging.ERROR
    g.request_log_message = "Simulated application fault"
    return jsonify({"error": "Simulated fault"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
