def test_cors_on_404(client):
    resp = client.get("/nonexistent")
    assert resp.status_code == 404
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"
