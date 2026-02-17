# backend/wsgi.py
"""
WSGI entrypoint for production (Render / Gunicorn).

Command example:
  gunicorn wsgi:app
"""

from app import create_app

app = create_app()
