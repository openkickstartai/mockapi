# mockapi

> Instant REST API from a JSON file. Zero code, full CRUD, filtering, pagination, hot-reload.

mockapi turns any JSON file into a fully functional REST API server in seconds. Perfect for frontend prototyping, integration testing, and demos.

## Features

- **Zero config** — point at a JSON file, get a REST API
- **Full CRUD** — GET, POST, PUT, DELETE on every collection
- **Filtering** — `?name=Alice&role=admin`
- **Pagination** — `?_page=1&_limit=10`
- **CORS enabled** — works with any frontend dev server
- **Hot-reload** — edit `db.json` and changes appear instantly
- **TypeScript types** — auto-generate TS interfaces from your data

## Install

```bash
git clone https://github.com/openkickstartai/mockapi.git
cd mockapi && pip install -e .
```

For development (includes test dependencies):

```bash
pip install -e ".[dev]"
```

## Quick Start

```bash
# 1. Create a data file
cat > db.json << 'EOF'
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

# 2. Start the server
mockapi serve db.json
```

## API Endpoints

For each top-level key in your JSON file, you get:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | List all users |
| GET | `/users/1` | Get user by ID |
| POST | `/users` | Create a new user |
| PUT | `/users/1` | Update user by ID |
| DELETE | `/users/1` | Delete user by ID |

### Filtering

```bash
# Filter by field value
curl http://localhost:5000/users?name=Alice

# Multiple filters (AND logic)
curl http://localhost:5000/posts?userId=1&title=Hello
```

### Pagination

```bash
# Get page 1 with 10 items per page
curl http://localhost:5000/users?_page=1&_limit=10
```

## Testing

```bash
pytest -v

# With coverage
pytest --cov=mockapi -v
```

## Project Structure

```
mockapi/
├── __init__.py      # Package init
├── cli.py           # CLI entry point (click)
├── server.py        # Flask app, route generation, CRUD
└── typegen.py       # TypeScript type generation
tests/
├── conftest.py      # Shared fixtures (test client, sample data)
├── test_server.py   # Server endpoint tests
├── test_typegen.py  # Type generation tests
├── test_cors.py     # CORS header tests
└── test_crud.py     # Full CRUD lifecycle tests
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT
