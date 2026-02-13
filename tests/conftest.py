"""Shared pytest fixtures for mockapi tests."""
import json
import os
import tempfile

import pytest

from mockapi.server import create_app


SAMPLE_DB = {
    "users": [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
    ],
    "posts": [
        {"id": 1, "title": "Hello", "userId": 1},
        {"id": 2, "title": "World", "userId": 2},
    ],
}


@pytest.fixture
def db_path(tmp_path):
    """Create a temporary JSON database file and return its path."""
    db_file = tmp_path / "db.json"
    db_file.write_text(json.dumps(SAMPLE_DB, indent=2))
    return str(db_file)


@pytest.fixture
def app(db_path):
    """Create a Flask application configured for testing."""
    application = create_app(db_path)
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    """Create a Flask test client."""
    return app.test_client()


@pytest.fixture
def sample_db():
    """Return a copy of the sample database dict for assertions."""
    return json.loads(json.dumps(SAMPLE_DB))
