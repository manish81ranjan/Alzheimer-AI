# backend/src/db/indexes.py
"""
MongoDB indexes setup.

Run this ONCE at app startup or via a script to improve performance.
Safe to run multiple times (idempotent).
"""

# from src.extensions import mongo
# from src.db.collections import USERS, SCANS, REPORTS


# def create_indexes():
#     """
#     Call this after mongo.init_app(app)
#     Example:
#         from src.db.indexes import create_indexes
#         create_indexes()
#     """

#     # -------------------- USERS --------------------
#     mongo.db[USERS].create_index("email", unique=True)
#     mongo.db[USERS].create_index("role")

#     # -------------------- SCANS --------------------
#     mongo.db[SCANS].create_index("userId")
#     mongo.db[SCANS].create_index("createdAt")
#     mongo.db[SCANS].create_index("stage")

#     # -------------------- REPORTS --------------------
#     mongo.db[REPORTS].create_index("userId")
#     mongo.db[REPORTS].create_index("scanId")
#     mongo.db[REPORTS].create_index("createdAt")

#     print("✅ MongoDB indexes ensured")


from src.extensions import mongo
from src.db.collections import USERS, SCANS, REPORTS

def create_indexes():
    try:
        mongo.db[USERS].create_index("email", unique=True)
        mongo.db[USERS].create_index("role")

        mongo.db[SCANS].create_index("userId")
        mongo.db[SCANS].create_index("createdAt")
        mongo.db[SCANS].create_index("stage")

        mongo.db[REPORTS].create_index("userId")
        mongo.db[REPORTS].create_index("scanId")
        mongo.db[REPORTS].create_index("createdAt")

        print("✅ MongoDB indexes ensured")
    except Exception as e:
        print("⚠️ MongoDB auth/connect issue — skipping indexes")
