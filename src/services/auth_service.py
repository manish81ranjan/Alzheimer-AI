# backend/src/services/auth_service.py
"""
Auth Service
- Business logic for register/login/me
- Routes should call these methods instead of touching DB directly
"""

from datetime import datetime
from flask_jwt_extended import create_access_token

from src.extensions import mongo, bcrypt
from src.db.collections import USERS


def _public_user(u: dict) -> dict:
    return {
        "id": str(u.get("_id")),
        "name": u.get("name", ""),
        "email": u.get("email", ""),
        "role": u.get("role", "user"),
        "createdAt": u.get("createdAt", ""),
    }


def register_user(name: str, email: str, password: str) -> dict:
    email = email.strip().lower()
    if mongo.db[USERS].find_one({"email": email}):
        raise ValueError("Email already registered")

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    user_doc = {
        "name": name.strip(),
        "email": email,
        "password": pw_hash,
        "role": "user",
        "createdAt": datetime.utcnow().isoformat(),
    }

    ins = mongo.db[USERS].insert_one(user_doc)
    user_doc["_id"] = ins.inserted_id

    token = create_access_token(identity=str(ins.inserted_id))
    return {"token": token, "user": _public_user(user_doc)}


def login_user(email: str, password: str) -> dict:
    email = email.strip().lower()
    user = mongo.db[USERS].find_one({"email": email})
    if not user:
        raise ValueError("Invalid credentials")

    if not bcrypt.check_password_hash(user.get("password", ""), password):
        raise ValueError("Invalid credentials")

    token = create_access_token(identity=str(user["_id"]))
    return {"token": token, "user": _public_user(user)}


def get_current_user(user_id: str) -> dict | None:
    from bson import ObjectId

    try:
        oid = ObjectId(user_id)
    except Exception:
        return None

    user = mongo.db[USERS].find_one({"_id": oid})
    return _public_user(user) if user else None
