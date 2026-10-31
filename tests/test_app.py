from app import app


def test_health_endpoint():
    with app.test_client() as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "UP"}


def test_version_endpoint():
    with app.test_client() as client:
        response = client.get("/version")

    assert response.status_code == 200
    assert response.get_json() == {"version": "1.0.1"}


def test_environment_endpoint():
    with app.test_client() as client:
        response = client.get("/environment")

    assert response.status_code == 200
    assert response.get_json() == {"environment": "development"}


def test_metrics_endpoint_exposes_required_metrics():
    with app.test_client() as client:
        client.get("/health")
        response = client.get("/metrics")

    metrics_text = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "# TYPE http_requests_total counter" in metrics_text
    assert "# TYPE http_request_duration_seconds histogram" in metrics_text
    assert "# TYPE app_info gauge" in metrics_text
    assert 'http_requests_total{endpoint="/health",method="GET",status="200"}' in metrics_text


def test_simulate_error_respects_fault_injection_switch(monkeypatch):
    monkeypatch.delenv("ENABLE_FAULT_INJECTION", raising=False)

    with app.test_client() as client:
        disabled_response = client.get("/simulate-error")

        monkeypatch.setenv("ENABLE_FAULT_INJECTION", "true")
        enabled_response = client.get("/simulate-error")

    assert disabled_response.status_code == 404
    assert enabled_response.status_code == 500
    assert enabled_response.get_json() == {"error": "Simulated fault"}
