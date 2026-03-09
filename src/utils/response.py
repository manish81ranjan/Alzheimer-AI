# backend/src/utils/response.py
from flask import jsonify


def ok(data=None, status: int = 200):
    """
    Standard success response:
      ok({"x": 1}) -> {"success": True, "data": {...}}
    """
    payload = {"success": True}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status


def fail(message: str = "Something went wrong", status: int = 400, **extra):
    """
    Standard error response:
      fail("Bad request", 400) -> {"success": False, "message": "..."}
    """
    payload = {"success": False, "message": message}
    if extra:
        payload.update(extra)
    return jsonify(payload), status
