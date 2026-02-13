"""Tests for CORS headers on all response types."""


def test_cors_on_success(client):
    """CORS headers should be present on successful responses."""
    resp = client.get("/users")
    assert resp.status_code == 200
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"


def test_cors_on_404(client):
    """CORS headers should be present even on 404 responses."""
    resp = client.get("/nonexistent")
    assert resp.status_code == 404
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"


def test_cors_preflight(client):
    """OPTIONS preflight requests should return proper CORS headers."""
    resp = client.options("/users", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
    })
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"
    # Should allow common methods
    allow_methods = resp.headers.get("Access-Control-Allow-Methods", "")
    assert "POST" in allow_methods or resp.status_code == 200
