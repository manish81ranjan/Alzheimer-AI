# backend/src/db/collections.py
"""
Central place to keep MongoDB collection names.
This prevents typos across services/routes.
"""

USERS = "users"
SCANS = "scans"
REPORTS = "reports"
PREDICTIONS = "predictions"   # optional (if you later store separately)
PATIENTS = "patients"         # optional (if you add patient profiles)
ANALYTICS = "analytics"       # optional (if you store time-series metrics)
