# backend/src/db/mongo.py
"""
MongoDB helper utilities.

This module:
- Centralizes access to MongoDB
- Provides safe ObjectId conversion
- Keeps DB logic out of routes/services
"""

from typing import Optional
from bson import ObjectId
from flask import current_app

from src.extensions import mongo


def get_db():
    """
    Returns the active MongoDB database instance.
    Usage:
        db = get_db()
        db.users.find_one(...)
    """
    return mongo.db


def to_objectid(value: str) -> Optional[ObjectId]:
    """
    Safely convert string to ObjectId.
    Returns None if invalid.
    """
    try:
        return ObjectId(value)
    except Exception:
        return None


def is_valid_objectid(value: str) -> bool:
    """
    Check if a string is a valid ObjectId.
    """
    try:
        ObjectId(value)
        return True
    except Exception:
        return False
