# backend/src/extensions.py
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

"""
Centralized Flask extensions.
Imported once and initialized in app factory.
"""

mongo = PyMongo()
bcrypt = Bcrypt()
jwt = JWTManager()
