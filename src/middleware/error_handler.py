# backend/src/middleware/error_handler.py
"""
Global error handling middleware.

- Converts exceptions to clean JSON
- Prevents ugly HTML error pages
- Keeps frontend error handling consistent
"""

from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        return (
            jsonify(
                {
                    "success": False,
                    "message": e.description,
                    "status": e.code,
                }
            ),
            e.code,
        )

    @app.errorhandler(Exception)
    def handle_exception(e: Exception):
        # In production, don't leak internals
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Internal server error",
                    "detail": str(e),
                    "status": 500,
                }
            ),
            500,
        )
