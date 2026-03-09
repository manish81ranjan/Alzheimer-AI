from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()

        claims = get_jwt() or {}
        role = (claims.get("role") or "").lower()

        if role != "admin":
            return jsonify({"success": False, "message": "Admin access required"}), 403

        return fn(*args, **kwargs)

    return wrapper
