# # backend/src/routes/admin_routes.py
# from flask import Blueprint, jsonify, request
# from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
# from src.extensions import mongo

# admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


# def _to_objectid(x):
#     from bson import ObjectId
#     try:
#         return ObjectId(str(x))
#     except Exception:
#         return None


# def _get_uid_and_role():
#     """
#     ✅ New tokens:
#       identity = "admin" or "<user_id>" (string)
#       role is in claims via get_jwt()
#     ✅ Supports legacy tokens too (if identity dict exists)
#     """
#     identity = get_jwt_identity()
#     claims = get_jwt() or {}

#     if isinstance(identity, dict):
#         uid = identity.get("id")
#         role = (identity.get("role") or claims.get("role") or "").lower()
#         return uid, role

#     uid = identity
#     role = (claims.get("role") or "").lower()
#     return uid, role


# def _is_admin(uid, role_from_token):
#     # ✅ if token claim says admin, allow
#     if (role_from_token or "").lower() == "admin":
#         return True

#     # ✅ allow env-admin identity
#     if str(uid) == "admin":
#         return True

#     # fallback DB role check for real users
#     oid = _to_objectid(uid)
#     if not oid:
#         return False
#     user = mongo.db.users.find_one({"_id": oid})
#     return bool(user and (user.get("role") or "").lower() == "admin")


# def _public_user(u: dict):
#     return {
#         "id": str(u.get("_id")),
#         "name": u.get("name", ""),
#         "email": u.get("email", ""),
#         "role": u.get("role", "user"),
#         "createdAt": u.get("createdAt") or u.get("created_at") or "",
#     }


# def _public_scan(s: dict):
#     """
#     Flexible mapping for scans collection (supports common field names)
#     """
#     sid = str(s.get("_id"))
#     user_id = s.get("userId") or s.get("user_id") or s.get("uid") or s.get("user") or ""
#     stage = s.get("stage") or s.get("status") or s.get("label") or "Pending"
#     created = s.get("createdAt") or s.get("created_at") or s.get("timestamp") or ""
#     file_name = s.get("fileName") or s.get("filename") or s.get("image") or s.get("path") or ""

#     return {
#         "id": sid,
#         "userId": str(user_id),
#         "stage": str(stage),
#         "createdAt": created,
#         "fileName": str(file_name),
#     }


# @admin_bp.get("/analytics")
# @jwt_required()
# def analytics():
#     uid, role = _get_uid_and_role()
#     if not _is_admin(uid, role):
#         return jsonify({"message": "Admin only."}), 403

#     total_users = mongo.db.users.count_documents({})
#     total_scans = mongo.db.scans.count_documents({})
#     total_reports = mongo.db.reports.count_documents({})

#     pipeline = [
#         {"$match": {"stage": {"$ne": ""}}},
#         {"$group": {"_id": "$stage", "count": {"$sum": 1}}},
#         {"$sort": {"count": -1}},
#     ]
#     stage_dist = list(mongo.db.scans.aggregate(pipeline))

#     return jsonify({
#         "totals": {"users": total_users, "scans": total_scans, "reports": total_reports},
#         "stageDistribution": [{"stage": s["_id"], "count": s["count"]} for s in stage_dist],
#     }), 200


# @admin_bp.get("/users")
# @jwt_required()
# def list_users():
#     uid, role = _get_uid_and_role()
#     if not _is_admin(uid, role):
#         return jsonify({"message": "Admin only."}), 403

#     users = list(mongo.db.users.find({}).sort("_id", -1).limit(200))
#     return jsonify({"users": [_public_user(u) for u in users]}), 200


# @admin_bp.patch("/users/<user_id>/role")
# @jwt_required()
# def update_role(user_id):
#     uid, role = _get_uid_and_role()
#     if not _is_admin(uid, role):
#         return jsonify({"message": "Admin only."}), 403

#     # ✅ prevent changing ENV admin "admin"
#     if str(user_id) == "admin":
#         return jsonify({"message": "Cannot change env admin role."}), 400

#     data = request.get_json(silent=True) or {}
#     new_role = (data.get("role") or "").strip().lower()
#     if new_role not in {"user", "admin"}:
#         return jsonify({"message": "role must be 'user' or 'admin'"}), 400

#     oid = _to_objectid(user_id)
#     if not oid:
#         return jsonify({"message": "Invalid user id"}), 400

#     res = mongo.db.users.update_one({"_id": oid}, {"$set": {"role": new_role}})
#     if res.matched_count == 0:
#         return jsonify({"message": "User not found."}), 404

#     return jsonify({"success": True, "userId": user_id, "role": new_role}), 200


# @admin_bp.get("/scans")
# @jwt_required()
# def admin_scans():
#     """
#     GET /api/admin/scans?limit=20&skip=0
#     Admin-only list of recent scans
#     """
#     uid, role = _get_uid_and_role()
#     if not _is_admin(uid, role):
#         return jsonify({"message": "Admin only."}), 403

#     def _int(v, default):
#         try:
#             return max(int(v), 0)
#         except Exception:
#             return default

#     limit = _int(request.args.get("limit", 20), 20)
#     skip = _int(request.args.get("skip", 0), 0)
#     limit = min(limit, 200)

#     # Sort safely even if your docs use created_at instead of createdAt
#     cursor = (
#         mongo.db.scans.find({})
#         .sort([("createdAt", -1), ("created_at", -1), ("_id", -1)])
#         .skip(skip)
#         .limit(limit)
#     )
#     scans = list(cursor)
#     total = mongo.db.scans.count_documents({})

#     return jsonify({
#         "scans": [_public_scan(s) for s in scans],
#         "page": {"skip": skip, "limit": limit, "total": total}
#     }), 200


from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.extensions import mongo

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _to_objectid(x):
    from bson import ObjectId
    try:
        return ObjectId(str(x))
    except Exception:
        return None


def _get_uid_and_role():
    """
    ✅ New tokens:
      identity = "admin" or "<user_id>" (string)
      role is in claims via get_jwt()
    ✅ Supports legacy tokens too (if identity dict exists)
    """
    identity = get_jwt_identity()
    claims = get_jwt() or {}

    if isinstance(identity, dict):
        uid = identity.get("id")
        role = (identity.get("role") or claims.get("role") or "").lower()
        return uid, role

    uid = identity
    role = (claims.get("role") or "").lower()
    return uid, role


def _is_admin(uid, role_from_token):
    # ✅ if token claim says admin, allow
    if (role_from_token or "").lower() == "admin":
        return True

    # ✅ allow env-admin identity
    if str(uid) == "admin":
        return True

    # fallback DB role check for real users
    oid = _to_objectid(uid)
    if not oid:
        return False
    user = mongo.db.users.find_one({"_id": oid})
    return bool(user and (user.get("role") or "").lower() == "admin")


def _public_user(u: dict):
    return {
        "id": str(u.get("_id")),
        "name": u.get("name", ""),
        "email": u.get("email", ""),
        "role": u.get("role", "user"),
        "createdAt": u.get("createdAt") or u.get("created_at") or "",
    }


def _public_scan(s: dict):
    """
    Flexible mapping for scans collection (supports common field names)
    """
    sid = str(s.get("_id"))
    user_id = s.get("userId") or s.get("user_id") or s.get("uid") or s.get("user") or ""
    stage = s.get("stage") or s.get("status") or s.get("label") or "Pending"
    created = s.get("createdAt") or s.get("created_at") or s.get("timestamp") or ""
    file_name = s.get("fileName") or s.get("filename") or s.get("image") or s.get("path") or ""

    return {
        "id": sid,
        "userId": str(user_id),
        "stage": str(stage),
        "createdAt": created,
        "fileName": str(file_name),
    }


@admin_bp.get("/analytics")
@jwt_required()
def analytics():
    uid, role = _get_uid_and_role()
    if not _is_admin(uid, role):
        return jsonify({"message": "Admin only."}), 403

    total_users = mongo.db.users.count_documents({})
    total_scans = mongo.db.scans.count_documents({})
    total_reports = mongo.db.reports.count_documents({})

    pipeline = [
        {"$match": {"stage": {"$ne": ""}}},
        {"$group": {"_id": "$stage", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    stage_dist = list(mongo.db.scans.aggregate(pipeline))

    return jsonify({
        "totals": {"users": total_users, "scans": total_scans, "reports": total_reports},
        "stageDistribution": [{"stage": s["_id"], "count": s["count"]} for s in stage_dist],
    }), 200


@admin_bp.get("/users")
@jwt_required()
def list_users():
    uid, role = _get_uid_and_role()
    if not _is_admin(uid, role):
        return jsonify({"message": "Admin only."}), 403

    users = list(mongo.db.users.find({}).sort("_id", -1).limit(200))
    return jsonify({"users": [_public_user(u) for u in users]}), 200


@admin_bp.patch("/users/<user_id>/role")
@jwt_required()
def update_role(user_id):
    uid, role = _get_uid_and_role()
    if not _is_admin(uid, role):
        return jsonify({"message": "Admin only."}), 403

    # ✅ prevent changing ENV admin "admin"
    if str(user_id) == "admin":
        return jsonify({"message": "Cannot change env admin role."}), 400

    data = request.get_json(silent=True) or {}
    new_role = (data.get("role") or "").strip().lower()
    if new_role not in {"user", "admin"}:
        return jsonify({"message": "role must be 'user' or 'admin'"}), 400

    oid = _to_objectid(user_id)
    if not oid:
        return jsonify({"message": "Invalid user id"}), 400

    res = mongo.db.users.update_one({"_id": oid}, {"$set": {"role": new_role}})
    if res.matched_count == 0:
        return jsonify({"message": "User not found."}), 404

    return jsonify({"success": True, "userId": user_id, "role": new_role}), 200


@admin_bp.get("/scans")
@jwt_required()
def admin_scans():
    """
    GET /api/admin/scans?limit=20&skip=0
    Admin-only list of recent scans
    """
    uid, role = _get_uid_and_role()
    if not _is_admin(uid, role):
        return jsonify({"message": "Admin only."}), 403

    def _int(v, default):
        try:
            return max(int(v), 0)
        except Exception:
            return default

    limit = _int(request.args.get("limit", 20), 20)
    skip = _int(request.args.get("skip", 0), 0)
    limit = min(limit, 200)

    cursor = (
        mongo.db.scans.find({})
        .sort([("createdAt", -1), ("created_at", -1), ("_id", -1)])
        .skip(skip)
        .limit(limit)
    )
    scans = list(cursor)
    total = mongo.db.scans.count_documents({})

    return jsonify({
        "scans": [_public_scan(s) for s in scans],
        "page": {"skip": skip, "limit": limit, "total": total}
    }), 200


# ✅ FIXED DELETE USER ENDPOINT (NO admin_required decorator)
@admin_bp.delete("/users/<user_id>")
@jwt_required()
def delete_user(user_id):
    uid, role = _get_uid_and_role()
    if not _is_admin(uid, role):
        return jsonify({"message": "Admin only."}), 403

    # ❌ block ENV admin
    if str(user_id) == "admin":
        return jsonify({"message": "ENV admin cannot be deleted."}), 403

    oid = _to_objectid(user_id)
    if not oid:
        return jsonify({"message": "Invalid user id."}), 400

    # ✅ delete related user data
    mongo.db.scans.delete_many({"userId": str(user_id)})
    mongo.db.reports.delete_many({"userId": str(user_id)})

    res = mongo.db.users.delete_one({"_id": oid})
    if res.deleted_count == 0:
        return jsonify({"message": "User not found."}), 404

    return jsonify({"success": True, "message": "User deleted."}), 200
