"""Flask server."""
import json
import os
from flask import Flask, request, jsonify

def create_app(datafile):
    app = Flask(__name__)
    db = {}
    counters = {}

    def load_db():
        nonlocal db, counters
        try:
            with open(datafile) as f:
                db = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            db = {}
        for col, items in db.items():
            if isinstance(items, list):
                counters[col] = max((i.get('id', 0) for i in items), default=0)

    def save_db():
        try:
            with open(datafile, 'w') as f:
                json.dump(db, f, indent=2)
        except IOError:
            pass

    def validate_json_request():
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        try:
            data = request.get_json(force=False)
            if data is None:
                return jsonify({'error': 'Invalid JSON'}), 400
            return data
        except Exception:
            return jsonify({'error': 'Invalid JSON'}), 400

    load_db()

    @app.route('/<collection>', methods=['GET'])
    def list_items(collection):
        if collection not in db:
            return jsonify({'error': 'not found'}), 404
        items = db[collection]
        # Filtering
        for key, val in request.args.items():
            if key.startswith('_'): continue
            items = [i for i in items if str(i.get(key, '')) == val]
        # Pagination
        page = request.args.get('_page', type=int)
        limit = request.args.get('_limit', 10, type=int)
        if page:
            start = (page - 1) * limit
            items = items[start:start + limit]
        return jsonify(items)

    @app.route('/<collection>/<int:item_id>', methods=['GET'])
    def get_item(collection, item_id):
        if collection not in db:
            return jsonify({'error': 'not found'}), 404
        for item in db[collection]:
            if item.get('id') == item_id:
                return jsonify(item)
        return jsonify({'error': 'not found'}), 404

    @app.route('/<collection>', methods=['POST'])
    def create_item(collection):
        if collection not in db:
            db[collection] = []
            counters[collection] = 0
        
        item = validate_json_request()
        if isinstance(item, tuple):  # Error response
            return item
        
        if not isinstance(item, dict):
            return jsonify({'error': 'Request body must be a JSON object'}), 400
        
        counters[collection] += 1
        item['id'] = counters[collection]
        db[collection].append(item)
        save_db()
        return jsonify(item), 201

    @app.route('/<collection>/<int:item_id>', methods=['PUT'])
    def update_item(collection, item_id):
        if collection not in db:
            return jsonify({'error': 'not found'}), 404
        
        data = validate_json_request()
        if isinstance(data, tuple):  # Error response
            return data
        
        if not isinstance(data, dict):
            return jsonify({'error': 'Request body must be a JSON object'}), 400
        
        for i, item in enumerate(db[collection]):
            if item.get('id') == item_id:
                data['id'] = item_id
                db[collection][i] = data
                save_db()
                return jsonify(data)
        return jsonify({'error': 'not found'}), 404

    @app.route('/<collection>/<int:item_id>', methods=['DELETE'])
    def delete_item(collection, item_id):
        if collection not in db:
            return jsonify({'error': 'not found'}), 404
        db[collection] = [i for i in db[collection] if i.get('id') != item_id]
        save_db()
        return jsonify({'deleted': True})

    return app
