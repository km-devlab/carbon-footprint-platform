"""Integration tests for the HTTP API surface in app.main."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def valid_payload():
    return {
        "transport_type": "petrol_vehicle",
        "distance_km": 1000,
        "electricity_kwh": 300,
        "clean_energy_percentage": 0,
        "diet_type": "vegan",
    }


def test_health_check_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_home_dashboard_renders():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_calculate_with_valid_payload_returns_200(valid_payload):
    response = client.post("/api/v1/calculate", json=valid_payload)
    assert response.status_code == 200
    body = response.json()
    assert body["total_carbon_footprint_kg"] == 411.7
    assert set(body["breakdown"].keys()) == {"transport", "energy", "diet"}
    assert isinstance(body["actionable_insights"], list)


def test_calculate_rejects_unknown_transport_type(valid_payload):
    valid_payload["transport_type"] = "rocket_ship"
    response = client.post("/api/v1/calculate", json=valid_payload)
    assert response.status_code == 422
    assert "detail" in response.json()


def test_calculate_rejects_unknown_diet_type(valid_payload):
    valid_payload["diet_type"] = "carnivore_extreme"
    response = client.post("/api/v1/calculate", json=valid_payload)
    assert response.status_code == 422


def test_calculate_rejects_negative_distance(valid_payload):
    valid_payload["distance_km"] = -10
    response = client.post("/api/v1/calculate", json=valid_payload)
    assert response.status_code == 422


def test_calculate_rejects_out_of_range_distance(valid_payload):
    valid_payload["distance_km"] = 999_999
    response = client.post("/api/v1/calculate", json=valid_payload)
    assert response.status_code == 422


def test_calculate_rejects_out_of_range_percentage(valid_payload):
    valid_payload["clean_energy_percentage"] = 150
    response = client.post("/api/v1/calculate", json=valid_payload)
    assert response.status_code == 422


def test_calculate_rejects_nan_input(valid_payload):
    # Python's json module emits the non-standard `NaN` token for float('nan'),
    # which httpx's `json=` kwarg would silently pass through. Send raw bytes
    # so the literal token reaches the server exactly as a malicious client would send it.
    import json

    raw = json.dumps(valid_payload).replace('"distance_km": 1000', '"distance_km": NaN')
    response = client.post(
        "/api/v1/calculate", content=raw, headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422


def test_calculate_rejects_infinity_input(valid_payload):
    import json

    raw = json.dumps(valid_payload).replace('"electricity_kwh": 300', '"electricity_kwh": Infinity')
    response = client.post(
        "/api/v1/calculate", content=raw, headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422


def test_calculate_rejects_missing_field(valid_payload):
    del valid_payload["diet_type"]
    response = client.post("/api/v1/calculate", json=valid_payload)
    assert response.status_code == 422


def test_calculate_rejects_wrong_type(valid_payload):
    valid_payload["distance_km"] = "a lot"
    response = client.post("/api/v1/calculate", json=valid_payload)
    assert response.status_code == 422


def test_validation_error_does_not_leak_internals(valid_payload):
    """The sanitized error response should not expose Pydantic's raw internal error structure."""
    valid_payload["transport_type"] = "invalid"
    response = client.post("/api/v1/calculate", json=valid_payload)
    body = response.json()
    assert list(body.keys()) == ["detail"]
    assert isinstance(body["detail"], str)


def test_security_headers_present():
    response = client.get("/health")
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"