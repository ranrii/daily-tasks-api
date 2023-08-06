from functools import wraps
import os
import dotenv
from flask import request, abort

dotenv.load_dotenv()


def key_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        provided_key = request.headers.get("api_key")
        stored_key = os.environ.get("API_KEY")
        if provided_key is not None and provided_key == stored_key:
            return function(*args, **kwargs)
        return abort(401, "Unauthorized")
    return wrapper
