# CORS middleware for all responses
from functools import wraps

def cors_middleware(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        response = f(*args, **kwargs)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    return wrapper
