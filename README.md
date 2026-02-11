# mockapi

Instant REST API from a JSON file.

## Install

```bash
git clone https://github.com/openkickstartai/mockapi.git
cd mockapi && pip install -e .
```

## Usage

```bash
# Create a data file
cat > db.json << EOF
{
  "users": [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
  ],
  "posts": [
    {"id": 1, "title": "Hello", "userId": 1}
  ]
}
EOF

# Start server
mockapi serve db.json

# Now you have:
# GET    /users
# GET    /users/1
# POST   /users
# PUT    /users/1
# DELETE /users/1
# GET    /users?name=Alice  (filtering)
# GET    /users?_page=1&_limit=10  (pagination)
```

## Testing

```bash
pytest -v
```
