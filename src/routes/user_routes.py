# # backend/src/routes/user_routes.py
# """
# User Routes
# - GET    /api/users/me        -> current user profile
# - PATCH  /api/users/me        -> update own profile (name/email)
# - GET    /api/users/<id>      -> (admin) get any user
# """

# from flask import Blueprint, jsonify, request
# from flask_jwt_extended import jwt_required, get_jwt_identity

# from src.extensions import mongo
# from src.middleware.auth_middleware import admin_required

# user_bp = Blueprint("users", __name__, url_prefix="/api/users")


# def _to_objectid(x: str):
#     from bson import ObjectId
#     try:
#         return ObjectId(x)
#     except Exception:
#         return None


# def _public_user(u: dict):
#     return {
#         "id": str(u.get("_id")),
#         "name": u.get("name", ""),
#         "email": u.get("email", ""),
#         "role": u.get("role", "user"),
#         "createdAt": u.get("createdAt", ""),
#     }


# def _get_uid_from_identity():
#     """
#     Supports both:
#       - old tokens: identity = "userid"
#       - new tokens: identity = {"id": "...", "role": "..."}
#     """
#     identity = get_jwt_identity()
#     if isinstance(identity, dict):
#         return identity.get("id")
#     return identity


# @user_bp.get("/me")
# @jwt_required()
# def get_me():
#     """
#     GET /api/users/me
#     Returns current logged-in user profile
#     """
#     uid = _get_uid_from_identity()
#     user = mongo.db.users.find_one({"_id": _to_objectid(uid)})
#     if not user:
#         return jsonify({"message": "User not found."}), 404

#     return jsonify({"user": _public_user(user)}), 200


# @user_bp.patch("/me")
# @jwt_required()
# def update_me():
#     """
#     PATCH /api/users/me
#     Body: { name?, email? }
#     """
#     uid = _get_uid_from_identity()
#     data = request.get_json(silent=True) or {}

#     update = {}
#     if "name" in data and isinstance(data["name"], str):
#         update["name"] = data["name"].strip()
#     if "email" in data and isinstance(data["email"], str):
#         update["email"] = data["email"].strip().lower()

#     if not update:
#         return jsonify({"message": "Nothing to update."}), 400

#     # Email uniqueness check
#     if "email" in update:
#         exists = mongo.db.users.find_one(
#             {"email": update["email"], "_id": {"$ne": _to_objectid(uid)}}
#         )
#         if exists:
#             return jsonify({"message": "Email already in use."}), 409

#     res = mongo.db.users.update_one(
#         {"_id": _to_objectid(uid)},
#         {"$set": update},
#     )

#     if res.matched_count == 0:
#         return jsonify({"message": "User not found."}), 404

#     user = mongo.db.users.find_one({"_id": _to_objectid(uid)})
#     return jsonify({"user": _public_user(user)}), 200


# @user_bp.get("/<user_id>")
# @jwt_required()
# @admin_required
# def get_user_by_id(user_id):
#     """
#     GET /api/users/:id
#     Admin only
#     """
#     user = mongo.db.users.find_one({"_id": _to_objectid(user_id)})
#     if not user:
#         return jsonify({"message": "User not found."}), 404

#     return jsonify({"user": _public_user(user)}), 200

# @user_bp.delete("/me")
# @jwt_required()
# def delete_me():
#     """
#     DELETE /api/users/me
#     Deletes current user account (and related scans/reports optionally)
#     """
#     uid = _get_uid_from_identity()

#     # ✅ Safety: prevent deleting ENV admin identity
#     if str(uid) == "admin":
#         return jsonify({"message": "ENV admin cannot be deleted."}), 403

#     oid = _to_objectid(uid)
#     if not oid:
#         return jsonify({"message": "Invalid user id."}), 400

#     # Optional: delete related user data (recommended)
#     mongo.db.scans.delete_many({"userId": str(uid)})
#     mongo.db.reports.delete_many({"userId": str(uid)})

#     res = mongo.db.users.delete_one({"_id": oid})
#     if res.deleted_count == 0:
#         return jsonify({"message": "User not found."}), 404

#     return jsonify({"success": True, "message": "Account deleted."}), 200

# # backend/src/routes/user_routes.py
# """
# User Routes
# - GET    /api/users/me        -> current user profile
# - PATCH  /api/users/me        -> update own profile (name/email)
# - DELETE /api/users/me        -> delete own account (danger)
# - GET    /api/users/<id>      -> (admin) get any user
# """

# from flask import Blueprint, jsonify, request
# from flask_jwt_extended import jwt_required, get_jwt_identity

# from src.extensions import mongo
# from src.middleware.auth_middleware import admin_required

# user_bp = Blueprint("users", __name__, url_prefix="/api/users")


# def _to_objectid(x: str):
#     from bson import ObjectId
#     try:
#         return ObjectId(str(x))
#     except Exception:
#         return None


# def _public_user(u: dict):
#     return {
#         "id": str(u.get("_id")),
#         "name": u.get("name", ""),
#         "email": u.get("email", ""),
#         "role": u.get("role", "user"),
#         "createdAt": u.get("createdAt", ""),
#     }


# def _get_uid_from_identity():
#     """
#     Supports:
#       - tokens with identity = "userid"
#       - legacy tokens with identity = {"id": "...", "role": "..."}
#     """
#     identity = get_jwt_identity()
#     if isinstance(identity, dict):
#         return identity.get("id")
#     return identity


# @user_bp.get("/me")
# @jwt_required()
# def get_me():
#     uid = _get_uid_from_identity()

#     # ENV admin isn't stored in DB users collection
#     if str(uid) == "admin":
#         return jsonify({
#             "user": {"id": "admin", "name": "Admin", "email": "—", "role": "admin", "createdAt": ""}
#         }), 200

#     oid = _to_objectid(uid)
#     if not oid:
#         return jsonify({"message": "Invalid user id."}), 400

#     user = mongo.db.users.find_one({"_id": oid})
#     if not user:
#         return jsonify({"message": "User not found."}), 404

#     return jsonify({"user": _public_user(user)}), 200


# @user_bp.patch("/me")
# @jwt_required()
# def update_me():
#     uid = _get_uid_from_identity()

#     # Safety: don't mutate ENV admin through DB endpoint
#     if str(uid) == "admin":
#         return jsonify({"message": "ENV admin profile can't be updated here."}), 403

#     oid = _to_objectid(uid)
#     if not oid:
#         return jsonify({"message": "Invalid user id."}), 400

#     data = request.get_json(silent=True) or {}

#     update = {}
#     if isinstance(data.get("name"), str):
#         update["name"] = data["name"].strip()
#     if isinstance(data.get("email"), str):
#         update["email"] = data["email"].strip().lower()

#     # Remove empty updates
#     update = {k: v for k, v in update.items() if v}

#     if not update:
#         return jsonify({"message": "Nothing to update."}), 400

#     # Email uniqueness check
#     if "email" in update:
#         exists = mongo.db.users.find_one(
#             {"email": update["email"], "_id": {"$ne": oid}}
#         )
#         if exists:
#             return jsonify({"message": "Email already in use."}), 409

#     res = mongo.db.users.update_one({"_id": oid}, {"$set": update})
#     if res.matched_count == 0:
#         return jsonify({"message": "User not found."}), 404

#     user = mongo.db.users.find_one({"_id": oid})
#     return jsonify({"user": _public_user(user)}), 200


# @user_bp.delete("/me")
# @jwt_required()
# def delete_me():
#     uid = _get_uid_from_identity()

#     # Safety: prevent deleting ENV admin identity
#     if str(uid) == "admin":
#         return jsonify({"message": "ENV admin cannot be deleted."}), 403

#     oid = _to_objectid(uid)
#     if not oid:
#         return jsonify({"message": "Invalid user id."}), 400

#     # Delete related user data (recommended)
#     mongo.db.scans.delete_many({"userId": str(uid)})
#     mongo.db.reports.delete_many({"userId": str(uid)})

#     res = mongo.db.users.delete_one({"_id": oid})
#     if res.deleted_count == 0:
#         return jsonify({"message": "User not found."}), 404

#     return jsonify({"success": True, "message": "Account deleted."}), 200


# @user_bp.get("/<user_id>")
# @jwt_required()
# @admin_required
# def get_user_by_id(user_id):
#     oid = _to_objectid(user_id)
#     if not oid:
#         return jsonify({"message": "Invalid user id."}), 400

#     user = mongo.db.users.find_one({"_id": oid})
#     if not user:
#         return jsonify({"message": "User not found."}), 404

#     return jsonify({"user": _public_user(user)}), 200

# backend/src/routes/user_routes.py
"""
User Routes
- GET    /api/users/me           -> current user profile
- PATCH  /api/users/me           -> update own profile (name/email)
- PATCH  /api/users/me/password  -> change own password
- DELETE /api/users/me           -> delete own account (danger)
- GET    /api/users/<id>         -> (admin) get any user
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.extensions import mongo, bcrypt
from src.middleware.auth_middleware import admin_required

user_bp = Blueprint("users", __name__, url_prefix="/api/users")


def _to_objectid(x: str):
    from bson import ObjectId
    try:
        return ObjectId(str(x))
    except Exception:
        return None


def _public_user(u: dict):
    return {
        "id": str(u.get("_id")),
        "name": u.get("name", ""),
        "email": u.get("email", ""),
        "role": u.get("role", "user"),
        "createdAt": u.get("createdAt", ""),
    }


def _get_uid_from_identity():
    """
    Supports:
      - identity = "userid"
      - legacy identity = {"id": "...", "role": "..."}
    """
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return identity.get("id")
    return identity


@user_bp.get("/me")
@jwt_required()
def get_me():
    uid = _get_uid_from_identity()

    # ENV admin isn't stored in DB users collection
    if str(uid) == "admin":
        return jsonify({
            "user": {
                "id": "admin",
                "name": "Admin",
                "email": "—",
                "role": "admin",
                "createdAt": ""
            }
        }), 200

    oid = _to_objectid(uid)
    if not oid:
        return jsonify({"message": "Invalid user id."}), 400

    user = mongo.db.users.find_one({"_id": oid})
    if not user:
        return jsonify({"message": "User not found."}), 404

    return jsonify({"user": _public_user(user)}), 200


@user_bp.patch("/me")
@jwt_required()
def update_me():
    uid = _get_uid_from_identity()

    # Safety: don't mutate ENV admin through DB endpoint
    if str(uid) == "admin":
        return jsonify({"message": "ENV admin profile can't be updated here."}), 403

    oid = _to_objectid(uid)
    if not oid:
        return jsonify({"message": "Invalid user id."}), 400

    data = request.get_json(silent=True) or {}

    update = {}
    if isinstance(data.get("name"), str):
        update["name"] = data["name"].strip()
    if isinstance(data.get("email"), str):
        update["email"] = data["email"].strip().lower()

    # Remove empty updates
    update = {k: v for k, v in update.items() if v}

    if not update:
        return jsonify({"message": "Nothing to update."}), 400

    # Email uniqueness check
    if "email" in update:
        exists = mongo.db.users.find_one({"email": update["email"], "_id": {"$ne": oid}})
        if exists:
            return jsonify({"message": "Email already in use."}), 409

    res = mongo.db.users.update_one({"_id": oid}, {"$set": update})
    if res.matched_count == 0:
        return jsonify({"message": "User not found."}), 404

    user = mongo.db.users.find_one({"_id": oid})
    return jsonify({"user": _public_user(user)}), 200


@user_bp.patch("/me/password")
@jwt_required()
def change_my_password():
    """
    PATCH /api/users/me/password
    Body: { currentPassword, newPassword }
    """
    uid = _get_uid_from_identity()

    # ENV admin has password in ENV, not in DB
    if str(uid) == "admin":
        return jsonify({"message": "ENV admin password can't be changed here."}), 403

    oid = _to_objectid(uid)
    if not oid:
        return jsonify({"message": "Invalid user id."}), 400

    data = request.get_json(silent=True) or {}
    current_password = data.get("currentPassword") or ""
    new_password = data.get("newPassword") or ""

    if not current_password or not new_password:
        return jsonify({"message": "Current and new password are required."}), 400

    if len(new_password) < 6:
        return jsonify({"message": "New password must be at least 6 characters."}), 400

    user = mongo.db.users.find_one({"_id": oid})
    if not user:
        return jsonify({"message": "User not found."}), 404

    # Verify current password
    if not bcrypt.check_password_hash(user.get("password", ""), current_password):
        return jsonify({"message": "Current password is incorrect."}), 401

    # Save new password hash
    hashed = bcrypt.generate_password_hash(new_password)
    if isinstance(hashed, (bytes, bytearray)):
        hashed = hashed.decode("utf-8")

    mongo.db.users.update_one({"_id": oid}, {"$set": {"password": hashed}})

    return jsonify({"success": True, "message": "Password updated."}), 200


@user_bp.delete("/me")
@jwt_required()
def delete_me():
    uid = _get_uid_from_identity()

    # Safety: prevent deleting ENV admin identity
    if str(uid) == "admin":
        return jsonify({"message": "ENV admin cannot be deleted."}), 403

    oid = _to_objectid(uid)
    if not oid:
        return jsonify({"message": "Invalid user id."}), 400

    # Delete related user data (recommended)
    mongo.db.scans.delete_many({"userId": str(uid)})
    mongo.db.reports.delete_many({"userId": str(uid)})

    res = mongo.db.users.delete_one({"_id": oid})
    if res.deleted_count == 0:
        return jsonify({"message": "User not found."}), 404

    return jsonify({"success": True, "message": "Account deleted."}), 200


@user_bp.get("/<user_id>")
@jwt_required()
@admin_required
def get_user_by_id(user_id):
    oid = _to_objectid(user_id)
    if not oid:
        return jsonify({"message": "Invalid user id."}), 400

    user = mongo.db.users.find_one({"_id": oid})
    if not user:
        return jsonify({"message": "User not found."}), 404

    return jsonify({"user": _public_user(user)}), 200
