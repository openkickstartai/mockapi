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
        with open(datafile) as f:
            db = json.load(f)
        for col, items in db.items():
            if isinstance(items, list):
                counters[col] = max((i.get('id', 0) for i in items), default=0)

    def save_db():
        with open(datafile, 'w') as f:
            json.dump(db, f, indent=2)

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
        item = request.get_json()
        counters[collection] += 1
        item['id'] = counters[collection]
        db[collection].append(item)
        save_db()
        return jsonify(item), 201

    @app.route('/<collection>/<int:item_id>', methods=['PUT'])
    def update_item(collection, item_id):
        if collection not in db:
            return jsonify({'error': 'not found'}), 404
        data = request.get_json()
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
