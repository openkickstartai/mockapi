"""Tests for full CRUD lifecycle on collection endpoints."""
import json


def test_list_collection(client):
    """GET /users should return all users."""
    resp = client.get("/users")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_get_single_resource(client):
    """GET /users/1 should return the user with id 1."""
    resp = client.get("/users/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == 1
    assert data["name"] == "Alice"


def test_get_nonexistent_resource(client):
    """GET /users/999 should return 404."""
    resp = client.get("/users/999")
    assert resp.status_code == 404


def test_create_resource(client):
    """POST /users should create a new user and return it."""
    new_user = {"name": "Charlie", "email": "charlie@example.com"}
    resp = client.post("/users", json=new_user)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Charlie"
    assert "id" in data

    # Verify it's actually in the list now
    resp2 = client.get("/users")
    users = resp2.get_json()
    names = [u["name"] for u in users]
    assert "Charlie" in names


def test_update_resource(client):
    """PUT /users/1 should update the user."""
    updated = {"name": "Alice Updated", "email": "alice_new@example.com"}
    resp = client.put("/users/1", json=updated)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Alice Updated"

    # Verify persistence
    resp2 = client.get("/users/1")
    assert resp2.get_json()["name"] == "Alice Updated"


def test_delete_resource(client):
    """DELETE /users/1 should remove the user."""
    resp = client.delete("/users/1")
    assert resp.status_code in (200, 204)

    # Verify it's gone
    resp2 = client.get("/users/1")
    assert resp2.status_code == 404


def test_filter_by_field(client):
    """GET /users?name=Alice should return only matching users."""
    resp = client.get("/users?name=Alice")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert all(u["name"] == "Alice" for u in data)


def test_filter_no_match(client):
    """Filtering with no matches should return empty list."""
    resp = client.get("/users?name=Nobody")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == []


def test_pagination(client):
    """GET /users?_page=1&_limit=1 should return one user."""
    resp = client.get("/users?_page=1&_limit=1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_multiple_collections(client):
    """Both /users and /posts should be available."""
    resp_users = client.get("/users")
    resp_posts = client.get("/posts")
    assert resp_users.status_code == 200
    assert resp_posts.status_code == 200
    assert len(resp_users.get_json()) == 2
    assert len(resp_posts.get_json()) == 2


def test_create_auto_increments_id(client):
    """POSTing two resources should get incrementing IDs."""
    user1 = {"name": "Dave", "email": "dave@example.com"}
    user2 = {"name": "Eve", "email": "eve@example.com"}
    resp1 = client.post("/users", json=user1)
    resp2 = client.post("/users", json=user2)
    id1 = resp1.get_json()["id"]
    id2 = resp2.get_json()["id"]
    assert id2 > id1
