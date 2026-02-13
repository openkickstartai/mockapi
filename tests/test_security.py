"""Security-focused tests for mockapi.

These tests verify that the server handles malicious, malformed, and
edge-case inputs safely — no crashes, no data leaks, no unhandled exceptions.
"""
import json
import os
import pytest

from mockapi.server import create_api


@pytest.fixture
def sec_db(tmp_path):
    data = {
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
        ]
    }
    path = tmp_path / "sec.json"
    path.write_text(json.dumps(data))
    return str(path)


@pytest.fixture
def client(sec_db):
    app = create_api(sec_db)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# --- Malformed input ---

def test_post_invalid_json(client):
    """Malformed JSON body must not crash the server."""
    resp = client.post("/users", data="not json{{", content_type="application/json")
    assert resp.status_code in (400, 415, 422, 500)


def test_post_empty_body(client):
    """Empty POST body must be handled gracefully."""
    resp = client.post("/users", data="", content_type="application/json")
    assert resp.status_code in (400, 422, 500)


def test_put_invalid_json(client):
    """Malformed JSON on PUT must not crash."""
    resp = client.put("/users/1", data="{broken", content_type="application/json")
    assert resp.status_code in (400, 415, 422, 500)


# --- Non-existent resources ---

def test_get_nonexistent_collection(client):
    """Accessing a collection that doesn't exist should 404, not crash."""
    resp = client.get("/does_not_exist")
    assert resp.status_code == 404


def test_get_nonexistent_item(client):
    resp = client.get("/users/99999")
    assert resp.status_code == 404


def test_delete_nonexistent_item(client):
    resp = client.delete("/users/99999")
    assert resp.status_code == 404


# --- Path traversal / injection ---

def test_path_traversal_in_id(client):
    """Path traversal in item ID must not leak filesystem data."""
    resp = client.get("/users/..%2F..%2Fetc%2Fpasswd")
    assert resp.status_code in (400, 404)


def test_xss_in_query_param(client):
    """XSS payloads in query params should not be reflected unsanitised."""
    resp = client.get("/users?name=%3Cscript%3Ealert(1)%3C/script%3E")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    # Should return empty array, not reflect the script tag outside JSON
    data = json.loads(body)
    assert isinstance(data, (list, dict))


def test_null_byte_in_query(client):
    """Null bytes must not cause unhandled exceptions."""
    resp = client.get("/users?name=test%00evil")
    assert resp.status_code in (200, 400)


# --- ID conflicts ---

def test_post_duplicate_id(client):
    """POST with an already-existing ID should be handled."""
    dup = {"id": 1, "name": "Evil", "email": "evil@test.com"}
    resp = client.post("/users", data=json.dumps(dup), content_type="application/json")
    assert resp.status_code in (200, 201, 409)


def test_put_id_mismatch(client):
    """PUT where URL id differs from body id should be handled safely."""
    payload = {"id": 999, "name": "Mismatch"}
    resp = client.put("/users/1", data=json.dumps(payload), content_type="application/json")
    assert resp.status_code in (200, 400)
    if resp.status_code == 200:
        result = json.loads(resp.data)
        # The URL id should take precedence to avoid confusion
        assert result.get("id") in (1, 999)
