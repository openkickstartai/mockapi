import pytest
from mockapi.validate import validate_db


def test_valid_db():
    data = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
    }
    assert validate_db(data) == []


def test_empty_db():
    issues = validate_db({})
    assert len(issues) == 1
    assert "empty" in issues[0].lower()


def test_not_a_dict():
    issues = validate_db([1, 2, 3])
    assert len(issues) == 1
    assert "object" in issues[0].lower()


def test_collection_not_array():
    issues = validate_db({"users": "not a list"})
    assert len(issues) == 1
    assert "not an array" in issues[0]


def test_duplicate_ids():
    data = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 1, "name": "Bob"},
        ]
    }
    issues = validate_db(data)
    assert any("duplicate" in i.lower() for i in issues)


def test_missing_id_field():
    data = {
        "users": [
            {"name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
    }
    issues = validate_db(data)
    assert any("without 'id'" in i for i in issues)


def test_empty_collection():
    data = {"users": []}
    issues = validate_db(data)
    assert any("empty" in i.lower() for i in issues)


def test_mixed_types():
    data = {
        "items": [
            {"id": 1, "value": 100},
            {"id": 2, "value": "text"},
        ]
    }
    issues = validate_db(data)
    assert any("mixed types" in i for i in issues)


def test_nullable_fields_not_flagged():
    """Fields with None mixed with a consistent type should not be flagged."""
    data = {
        "users": [
            {"id": 1, "name": "Alice", "email": None},
            {"id": 2, "name": "Bob", "email": "bob@test.com"},
        ]
    }
    issues = validate_db(data)
    assert not any("email" in i for i in issues)


def test_multiple_collections_independent():
    """Issues in one collection should not affect another."""
    data = {
        "users": [
            {"id": 1, "name": "Alice"},
        ],
        "posts": [
            {"id": 1, "title": "Hello", "userId": 1},
            {"id": 1, "title": "Dupe", "userId": 2},
        ],
    }
    issues = validate_db(data)
    assert any("posts" in i and "duplicate" in i.lower() for i in issues)
    assert not any("users" in i and "duplicate" in i.lower() for i in issues)
