# Contributing to mockapi

Thank you for your interest in contributing to mockapi! This guide will help you get started.

## Getting Started

### 1. Fork & Clone

```bash
git clone https://github.com/<your-username>/mockapi.git
cd mockapi
```

### 2. Set Up Development Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

Or use the Makefile:

```bash
make install
```

### 3. Run Tests

```bash
pytest -v
# or
make test
```

## How to Contribute

### Reporting Bugs

- Search existing issues first to avoid duplicates.
- Include steps to reproduce, expected vs actual behavior, and your environment info.

### Suggesting Features

- Open an issue with the `enhancement` label.
- Describe the use case and why it would benefit users.

### Submitting Code

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feat/my-feature
   # or
   git checkout -b fix/my-bugfix
   ```

2. **Write your code** with tests. We aim for good test coverage.

3. **Run the full test suite** before submitting:
   ```bash
   make test
   ```

4. **Commit with clear messages**:
   ```
   feat: add sorting support for collection endpoints
   fix: handle empty JSON file gracefully
   docs: add example for nested resource filtering
   ```

5. **Open a Pull Request** against `main`.

## Code Style

- Follow PEP 8.
- Use type hints where practical.
- Keep functions focused and small.
- Add docstrings to public functions.

## Project Structure

```
mockapi/
├── __init__.py      # Package init
├── cli.py           # CLI entry point (click commands)
├── server.py        # Flask app, route generation, CRUD logic
└── typegen.py       # TypeScript type generation from JSON schema
tests/
├── conftest.py      # Shared pytest fixtures (Flask test client, sample data)
├── test_server.py   # Server endpoint tests
├── test_typegen.py  # Type generation tests
└── test_cors.py     # CORS header tests
```

## Good First Issues

Look for issues labeled `good first issue` — these are scoped for newcomers.

Some ideas if no issues exist yet:
- Add `--host` and `--port` CLI options
- Add `_sort` and `_order` query parameters
- Add response delay simulation (`--delay`)
- Improve error messages for malformed JSON

## Questions?

Open an issue or start a discussion. We're happy to help!
