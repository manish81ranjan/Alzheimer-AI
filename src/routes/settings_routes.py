# backend/src/routes/settings_routes.py
import os
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.extensions import mongo

settings_bp = Blueprint("settings", __name__, url_prefix="/api/admin/settings")


def _to_objectid(x):
    from bson import ObjectId
    try:
        return ObjectId(str(x))
    except Exception:
        return None


def _get_uid_and_role():
    identity = get_jwt_identity()
    claims = get_jwt() or {}

    if isinstance(identity, dict):
        uid = identity.get("id")
        role = (identity.get("role") or claims.get("role") or "").lower()
        return uid, role

    return identity, (claims.get("role") or "").lower()


def _is_admin(uid, role_from_token):
    if (role_from_token or "").lower() == "admin":
        return True
    if str(uid) == "admin":
        return True

    oid = _to_objectid(uid)
    if not oid:
        return False
    user = mongo.db.users.find_one({"_id": oid})
    return bool(user and (user.get("role") or "").lower() == "admin")


def _get_flags_doc():
    doc = mongo.db.system.find_one({"_id": "flags"})
    if not doc:
        doc = {"_id": "flags", "maintenanceMode": False, "auditLogs": True}
        mongo.db.system.update_one({"_id": "flags"}, {"$set": doc}, upsert=True)
    return doc


@settings_bp.get("")
@jwt_required()
def get_settings():
    uid, role = _get_uid_and_role()
    if not _is_admin(uid, role):
        return jsonify({"message": "Admin only."}), 403

    flags = _get_flags_doc()

    return jsonify({
        "maintenanceMode": bool(flags.get("maintenanceMode", False)),
        "auditLogs": bool(flags.get("auditLogs", True)),
        "adminConfigured": bool((os.getenv("ADMIN_EMAIL") or "").strip()),
    }), 200


@settings_bp.patch("")
@jwt_required()
def update_settings():
    uid, role = _get_uid_and_role()
    if not _is_admin(uid, role):
        return jsonify({"message": "Admin only."}), 403

    data = request.get_json(silent=True) or {}
    updates = {}

    if "maintenanceMode" in data:
        updates["maintenanceMode"] = bool(data["maintenanceMode"])
    if "auditLogs" in data:
        updates["auditLogs"] = bool(data["auditLogs"])

    if not updates:
        return jsonify({"message": "No valid fields to update."}), 400

    mongo.db.system.update_one({"_id": "flags"}, {"$set": updates}, upsert=True)
    flags = _get_flags_doc()

    return jsonify({
        "maintenanceMode": bool(flags.get("maintenanceMode", False)),
        "auditLogs": bool(flags.get("auditLogs", True)),
    }), 200
