"""mockapi: Instant REST API from JSON.

A lightweight Python package that creates instant REST APIs from JSON data files.
Perfect for prototyping, testing, and mock data scenarios.

Features:
- Automatic REST endpoint generation from JSON files
- Support for CRUD operations
- Built-in data validation
- Configurable caching with expiration
- CLI interface for quick setup

Usage:
    Basic usage:
    >>> from mockapi import create_api
    >>> api = create_api('data.json')
    >>> api.run()
    
    CLI usage:
    $ mockapi serve data.json --port 8000
    
API Endpoints:
    GET /items - List all items
    GET /items/{id} - Get specific item
    POST /items - Create new item
    PUT /items/{id} - Update item
    DELETE /items/{id} - Delete item
"""
__version__ = "0.1.0"
