# # backend/src/routes/auth_routes.py
# from flask import Blueprint, request, jsonify
# # from flask_jwt_extended import create_access_token
# import os
# from src.extensions import mongo, bcrypt
# from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# def _public_user(u: dict):
#     return {
#         "id": str(u.get("_id")) if u.get("_id") else str(u.get("id", "")),
#         "name": u.get("name", ""),
#         "email": u.get("email", ""),
#         "role": u.get("role", "user"),
#         "createdAt": u.get("createdAt", ""),
#     }

# @auth_bp.post("/login")
# def login():
#     data = request.get_json(silent=True) or {}
#     email = (data.get("email") or "").strip().lower()
#     password = data.get("password") or ""

#     if not email or not password:
#         return jsonify({"message": "Email and password are required."}), 400

#     # ✅ ENV admin login
#     admin_email = (os.getenv("ADMIN_EMAIL") or "").strip().lower()
#     admin_password = os.getenv("ADMIN_PASSWORD") or ""

#     if admin_email and admin_password and email == admin_email and password == admin_password:
#         # ✅ IMPORTANT: identity MUST BE STRING
#         token = create_access_token(
#             identity="admin",
#             additional_claims={"role": "admin", "email": admin_email}
#         )
#         admin_user = {"id": "admin", "name": "Admin", "email": admin_email, "role": "admin"}
#         return jsonify({"token": token, "user": admin_user}), 200

#     # Normal user login
#     user = mongo.db.users.find_one({"email": email})
#     if not user:
#         return jsonify({"message": "Invalid credentials."}), 401

#     if not bcrypt.check_password_hash(user.get("password", ""), password):
#         return jsonify({"message": "Invalid credentials."}), 401

#     uid = str(user["_id"])
#     role = (user.get("role") or "user").lower()

#     # ✅ identity MUST BE STRING
#     token = create_access_token(
#         identity=uid,
#         additional_claims={"role": role, "email": user.get("email", "")}
#     )

#     return jsonify({"token": token, "user": _public_user(user)}), 200

# # backend/src/routes/auth_routes.py
# from flask import Blueprint, request, jsonify
# import os

# from flask_jwt_extended import (
#     create_access_token,
#     jwt_required,
#     get_jwt_identity,
# )

# from src.extensions import mongo, bcrypt

# auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# def _to_objectid(x):
#     from bson import ObjectId
#     try:
#         return ObjectId(str(x))
#     except Exception:
#         return None


# def _public_user(u: dict):
#     return {
#         "id": str(u.get("_id")) if u.get("_id") else str(u.get("id", "")),
#         "name": u.get("name", ""),
#         "email": u.get("email", ""),
#         "role": u.get("role", "user"),
#         "createdAt": u.get("createdAt", ""),
#     }


# @auth_bp.post("/login")
# def login():
#     data = request.get_json(silent=True) or {}
#     email = (data.get("email") or "").strip().lower()
#     password = data.get("password") or ""

#     if not email or not password:
#         return jsonify({"message": "Email and password are required."}), 400

#     # ✅ ENV admin login
#     admin_email = (os.getenv("ADMIN_EMAIL") or "").strip().lower()
#     admin_password = os.getenv("ADMIN_PASSWORD") or ""

#     if admin_email and admin_password and email == admin_email and password == admin_password:
#         # ✅ IMPORTANT: identity MUST BE STRING
#         token = create_access_token(
#             identity="admin",
#             additional_claims={"role": "admin", "email": admin_email},
#         )
#         admin_user = {
#             "id": "admin",
#             "name": "Admin",
#             "email": admin_email,
#             "role": "admin",
#         }
#         return jsonify({"token": token, "user": admin_user}), 200

#     # Normal user login
#     user = mongo.db.users.find_one({"email": email})
#     if not user:
#         return jsonify({"message": "Invalid credentials."}), 401

#     if not bcrypt.check_password_hash(user.get("password", ""), password):
#         return jsonify({"message": "Invalid credentials."}), 401

#     uid = str(user["_id"])
#     role = (user.get("role") or "user").lower()

#     # ✅ identity MUST BE STRING
#     token = create_access_token(
#         identity=uid,
#         additional_claims={"role": role, "email": user.get("email", "")},
#     )

#     return jsonify({"token": token, "user": _public_user(user)}), 200


# @auth_bp.post("/change-password")
# @jwt_required()
# def change_password():
#     """
#     POST /api/auth/change-password
#     Body: { currentPassword, newPassword }
#     """
#     uid = get_jwt_identity()

#     # ✅ ENV admin is not stored in DB, so don't allow change here
#     if str(uid) == "admin":
#         return jsonify({"message": "ENV admin password can't be changed here."}), 403

#     data = request.get_json(silent=True) or {}
#     current_password = data.get("currentPassword") or ""
#     new_password = data.get("newPassword") or ""

#     if not current_password or not new_password:
#         return jsonify({"message": "Both currentPassword and newPassword are required."}), 400

#     if len(new_password) < 6:
#         return jsonify({"message": "New password must be at least 6 characters."}), 400

#     oid = _to_objectid(uid)
#     if not oid:
#         return jsonify({"message": "Invalid user id."}), 400

#     user = mongo.db.users.find_one({"_id": oid})
#     if not user:
#         return jsonify({"message": "User not found."}), 404

#     # verify current password
#     if not bcrypt.check_password_hash(user.get("password", ""), current_password):
#         return jsonify({"message": "Current password is incorrect."}), 401

#     # set new password hash
#     new_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
#     mongo.db.users.update_one({"_id": oid}, {"$set": {"password": new_hash}})

#     return jsonify({"success": True, "message": "Password updated."}), 200
# backend/src/routes/auth_routes.py
from flask import Blueprint, request, jsonify
import os
from datetime import datetime, timezone

from src.extensions import mongo, bcrypt
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _public_user(u: dict):
    return {
        "id": str(u.get("_id")) if u.get("_id") else str(u.get("id", "")),
        "name": u.get("name", ""),
        "email": u.get("email", ""),
        "role": (u.get("role") or "user"),
        "createdAt": u.get("createdAt", ""),
        "lastLoginAt": u.get("lastLoginAt", ""),
    }


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"message": "Name, email and password are required."}), 400
    if len(password) < 6:
        return jsonify({"message": "Password must be at least 6 characters."}), 400

    exists = mongo.db.users.find_one({"email": email})
    if exists:
        return jsonify({"message": "Email already in use."}), 409

    now = datetime.now(timezone.utc).isoformat()

    doc = {
        "name": name,
        "email": email,
        "password": bcrypt.generate_password_hash(password).decode("utf-8"),
        "role": "user",
        "createdAt": now,
        "lastLoginAt": now,
    }

    res = mongo.db.users.insert_one(doc)
    doc["_id"] = res.inserted_id

    token = create_access_token(
        identity=str(doc["_id"]),
        additional_claims={"role": "user", "email": email},
    )

    return jsonify({"token": token, "user": _public_user(doc)}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    login_as = (data.get("loginAs") or "user").strip().lower()  # ✅ NEW

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400
    if login_as not in ("user", "admin"):
        return jsonify({"message": "Invalid loginAs value."}), 400

    # ✅ ENV admin login (fixed one)
    admin_email = (os.getenv("ADMIN_EMAIL") or "").strip().lower()
    admin_password = os.getenv("ADMIN_PASSWORD") or ""

    # If user selects USER but enters ENV admin creds → block (forces correct tab)
    if login_as == "user" and admin_email and admin_password:
        if email == admin_email and password == admin_password:
            return jsonify({"message": "Please use Admin login option for admin account."}), 403

    # If user selects ADMIN: allow ONLY admin accounts
    if login_as == "admin":
        # 1) ENV admin check
        if admin_email and admin_password and email == admin_email and password == admin_password:
            token = create_access_token(
                identity="admin",
                additional_claims={"role": "admin", "email": admin_email},
            )
            admin_user = {
                "id": "admin",
                "name": "Admin",
                "email": admin_email,
                "role": "admin",
                "createdAt": "",
                "lastLoginAt": datetime.now(timezone.utc).isoformat(),
            }
            return jsonify({"token": token, "user": admin_user}), 200

        # 2) DB admin check (optional if you ever store admins in DB)
        user = mongo.db.users.find_one({"email": email})
        if not user:
            return jsonify({"message": "Admin credentials are invalid."}), 401

        role = (user.get("role") or "user").lower()
        if role != "admin":
            return jsonify({"message": "This account is not an admin."}), 403

        if not bcrypt.check_password_hash(user.get("password", ""), password):
            return jsonify({"message": "Admin credentials are invalid."}), 401

        mongo.db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"lastLoginAt": datetime.now(timezone.utc).isoformat()}},
        )

        token = create_access_token(
            identity=str(user["_id"]),
            additional_claims={"role": "admin", "email": user.get("email", "")},
        )
        return jsonify({"token": token, "user": _public_user(user)}), 200

    # ✅ USER login (only normal registered users)
    user = mongo.db.users.find_one({"email": email})
    if not user:
        return jsonify({"message": "Invalid credentials."}), 401

    role = (user.get("role") or "user").lower()
    if role == "admin":
        return jsonify({"message": "Please use Admin login option for admin account."}), 403

    if not bcrypt.check_password_hash(user.get("password", ""), password):
        return jsonify({"message": "Invalid credentials."}), 401

    mongo.db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"lastLoginAt": datetime.now(timezone.utc).isoformat()}},
    )

    token = create_access_token(
        identity=str(user["_id"]),
        additional_claims={"role": "user", "email": user.get("email", "")},
    )

    return jsonify({"token": token, "user": _public_user(user)}), 200
