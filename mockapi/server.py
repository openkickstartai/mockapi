"""Flask server."""
import json
import os
import re
from flask import Flask, request, jsonify

def create_app(datafile):
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
    db = {}
    counters = {}

    def load_db():
        nonlocal db, counters
        try:
            if os.path.exists(datafile):
                with open(datafile, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        db = json.loads(content)
                    else:
                        db = {}
            else:
                db = {}
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load database file {datafile}: {e}")
            db = {}
        
        # Initialize counters
        for col, items in db.items():
            if isinstance(items, list):
                counters[col] = max((i.get('id', 0) for i in items if isinstance(i, dict)), default=0)
            else:
                counters[col] = 0

    def save_db():
        try:
            os.makedirs(os.path.dirname(datafile), exist_ok=True)
            with open(datafile, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            print(f"Error saving database: {e}")
            return False
        return True

    def validate_collection_name(collection):
        if not collection or len(collection) > 50:
            return False
        return re.match(r'^[a-zA-Z0-9_-]+$', collection) is not None

    def validate_json_request():
        if not request.is_json:
            return None, (jsonify({'error': 'Content-Type must be application/json'}), 400)
        
        try:
            data = request.get_json(force=False)
            if data is None:
                return None, (jsonify({'error': 'Invalid or empty JSON'}), 400)
            
            if not isinstance(data, dict):
                return None, (jsonify({'error': 'JSON must be an object'}), 400)
                
            return data, None
        except Exception as e:
            return None, (jsonify({'error': f'JSON parsing error: {str(e)}'}), 400)

    def safe_int_param(value, default=None, min_val=None, max_val=None):
        try:
            result = int(value)
            if min_val is not None and result < min_val:
                return default
            if max_val is not None and result > max_val:
                return default
            return result
        except (ValueError, TypeError):
            return default

    load_db()

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({'error': 'Request entity too large'}), 413

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400

    @app.route('/<collection>', methods=['GET'])
    def list_items(collection):
        if not validate_collection_name(collection):
            return jsonify({'error': 'Invalid collection name'}), 400
            
        if collection not in db:
            return jsonify({'error': 'Collection not found'}), 404
            
        items = db[collection]
        if not isinstance(items, list):
            return jsonify({'error': 'Collection is not a list'}), 400
        
        # Create a copy to avoid modifying original
        filtered_items = items.copy()
        
        # Filtering
        for key, val in request.args.items():
            if key.startswith('_'): 
                continue
            if len(key) > 50:  # Prevent abuse
                continue
            filtered_items = [i for i in filtered_items if isinstance(i, dict) and str(i.get(key, '')) == val]
        
        # Pagination
        page = safe_int_param(request.args.get('_page'), min_val=1, max_val=1000)
        limit = safe_int_param(request.args.get('_limit', 10), default=10, min_val=1, max_val=100)
        
        if page:
            start = (page - 1) * limit
            filtered_items = filtered_items[start:start + limit]
        elif limit:
            filtered_items = filtered_items[:limit]
            
        return jsonify(filtered_items)

    @app.route('/<collection>/<int:item_id>', methods=['GET'])
    def get_item(collection, item_id):
        if not validate_collection_name(collection):
            return jsonify({'error': 'Invalid collection name'}), 400
            
        if collection not in db:
            return jsonify({'error': 'Collection not found'}), 404
            
        if not isinstance(db[collection], list):
            return jsonify({'error': 'Collection is not a list'}), 400
            
        for item in db[collection]:
            if isinstance(item, dict) and item.get('id') == item_id:
                return jsonify(item)
                
        return jsonify({'error': 'Item not found'}), 404

    @app.route('/<collection>', methods=['POST'])
    def create_item(collection):
        if not validate_collection_name(collection):
            return jsonify({'error': 'Invalid collection name'}), 400
            
        data, error_response = validate_json_request()
        if error_response:
            return error_response
            
        if collection not in db:
            db[collection] = []
            counters[collection] = 0
            
        if not isinstance(db[collection], list):
            return jsonify({'error': 'Collection is not a list'}), 400
            
        # Create new item
        counters[collection] += 1
        item = data.copy()
        item['id'] = counters[collection]
        
        db[collection].append(item)
        
        if not save_db():
            return jsonify({'error': 'Failed to save data'}), 500
            
        return jsonify(item), 201

    @app.route('/<collection>/<int:item_id>', methods=['PUT'])
    def update_item(collection, item_id):
        if not validate_collection_name(collection):
            return jsonify({'error': 'Invalid collection name'}), 400
            
        if collection not in db:
            return jsonify({'error': 'Collection not found'}), 404
            
        if not isinstance(db[collection], list):
            return jsonify({'error': 'Collection is not a list'}), 400
            
        data, error_response = validate_json_request()
        if error_response:
            return error_response
            
        for i, item in enumerate(db[collection]):
            if isinstance(item, dict) and item.get('id') == item_id:
                updated_item = data.copy()
                updated_item['id'] = item_id
                db[collection][i] = updated_item
                
                if not save_db():
                    return jsonify({'error': 'Failed to save data'}), 500
                    
                return jsonify(updated_item)
                
        return jsonify({'error': 'Item not found'}), 404

    @app.route('/<collection>/<int:item_id>', methods=['DELETE'])
    def delete_item(collection, item_id):
        if not validate_collection_name(collection):
            return jsonify({'error': 'Invalid collection name'}), 400
            
        if collection not in db:
            return jsonify({'error': 'Collection not found'}), 404
            
        if not isinstance(db[collection], list):
            return jsonify({'error': 'Collection is not a list'}), 400
            
        for i, item in enumerate(db[collection]):
            if isinstance(item, dict) and item.get('id') == item_id:
                deleted_item = db[collection].pop(i)
                
                if not save_db():
                    return jsonify({'error': 'Failed to save data'}), 500
                    
                return jsonify(deleted_item)
                
        return jsonify({'error': 'Item not found'}), 404

    return app

if __name__ == '__main__':
    import sys
    datafile = sys.argv[1] if len(sys.argv) > 1 else 'data.json'
    app = create_app(datafile)
    app.run(debug=True, host='0.0.0.0', port=5000)