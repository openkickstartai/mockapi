"""Tests."""
import json, os, tempfile
from mockapi.server import create_app

def _app():
    tmp = tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False)
    json.dump({'users': [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]}, tmp)
    tmp.flush()
    app = create_app(tmp.name)
    app.config['TESTING'] = True
    return app, tmp.name

def test_list():
    app, f = _app()
    with app.test_client() as c:
        r = c.get('/users')
        assert r.status_code == 200
        assert len(r.get_json()) == 2
    os.unlink(f)

def test_get_one():
    app, f = _app()
    with app.test_client() as c:
        r = c.get('/users/1')
        assert r.status_code == 200
        assert r.get_json()['name'] == 'Alice'
    os.unlink(f)

def test_create():
    app, f = _app()
    with app.test_client() as c:
        r = c.post('/users', json={'name': 'Charlie'})
        assert r.status_code == 201
        assert r.get_json()['id'] == 3
        r = c.get('/users')
        assert len(r.get_json()) == 3
    os.unlink(f)

def test_filter():
    app, f = _app()
    with app.test_client() as c:
        r = c.get('/users?name=Alice')
        data = r.get_json()
        assert len(data) == 1
        assert data[0]['name'] == 'Alice'
    os.unlink(f)

def test_404():
    app, f = _app()
    with app.test_client() as c:
        r = c.get('/nope')
        assert r.status_code == 404
    os.unlink(f)
