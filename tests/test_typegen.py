"""Tests."""
from mockapi.typegen import generate_types, infer_type

def test_infer_types():
    assert infer_type(42) == 'number'
    assert infer_type('hello') == 'string'
    assert infer_type(True) == 'boolean'
    assert infer_type(3.14) == 'number'
    assert infer_type([1,2]) == 'any[]'

def test_generate_types():
    data = {'users': [{'id': 1, 'name': 'Alice', 'active': True}]}
    ts = generate_types(data)
    assert 'export interface User' in ts
    assert 'id: number;' in ts
    assert 'name: string;' in ts
    assert 'active: boolean;' in ts
    assert 'UserList' in ts

def test_empty_collection():
    ts = generate_types({'items': []})
    assert 'interface' not in ts
