# backend/src/routes/health_routes.py
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__, url_prefix="/api/health")

@health_bp.get("")
def health_check():
    return jsonify({
        "status": "ok",
        "service": "alzheimer-ai-backend"
    }), 200
