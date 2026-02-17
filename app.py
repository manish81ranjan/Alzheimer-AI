# # backend/app.py
# import os
# from flask import Flask, jsonify, request
# from flask_cors import CORS

# from src.config import Config
# from src.extensions import mongo, bcrypt, jwt

# # Blueprints
# from src.routes.health_routes import health_bp
# from src.routes.auth_routes import auth_bp
# from src.routes.user_routes import user_bp
# from src.routes.scan_routes import scan_bp
# from src.routes.infer_routes import infer_bp
# from src.routes.report_routes import report_bp
# from src.routes.admin_routes import admin_bp
# from src.routes.settings_routes import settings_bp

# from src.db.indexes import create_indexes
# from src.middleware.error_handler import register_error_handlers
# from src.routes.chatbot_routes import chatbot_bp

# def create_app():
#     app = Flask(
#         __name__,
#         static_folder="static",      # backend/static
#         static_url_path="/static"    # URL: /static/...
#     )

#     # Load config
#     app.config.from_object(Config)

#     # ✅ CORS: allow Vite dev server + optional env origins
#     cors_origins = app.config.get(
#         "CORS_ORIGINS",
#         [
#             "http://localhost:5173",
#             "http://127.0.0.1:5173",
#         ],
#     )

#     # If someone sets "*" in config, allow all (dev use)
#     if cors_origins == "*" or cors_origins == ["*"]:
#         cors_origins = "*"

#     CORS(
#         app,
#         resources={r"/api/*": {"origins": cors_origins}},
#         supports_credentials=True,
#         allow_headers=["Content-Type", "Authorization"],
#         methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
#     )

#     # ✅ FIX: Always answer preflight OPTIONS (prevents "Network Error" in browser)
#     @app.before_request
#     def handle_options():
#         if request.method == "OPTIONS":
#             return "", 200

#     # Init extensions
#     mongo.init_app(app)
#     bcrypt.init_app(app)
#     jwt.init_app(app)

#     # Error handlers
#     register_error_handlers(app)

#     # Create indexes inside app context
#     with app.app_context():
#         create_indexes()

#     # Register blueprints
#     app.register_blueprint(health_bp)
#     app.register_blueprint(auth_bp)
#     app.register_blueprint(user_bp)
#     app.register_blueprint(scan_bp)
#     app.register_blueprint(infer_bp)
#     app.register_blueprint(report_bp)
#     app.register_blueprint(admin_bp)
#     app.register_blueprint(settings_bp)
#     app.register_blueprint(chatbot_bp)
#     # Root
#     @app.get("/")
#     def root():
#         return jsonify(
#             {
#                 "message": "Backend running 🚀",
#                 "health": "/api/health",
#             }
#         ), 200

#     return app


# if __name__ == "__main__":
#     app = create_app()
#     port = int(os.getenv("PORT", 5000))
#     app.run(host="0.0.0.0", port=port, debug=True)

# backend/app.py
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

from src.config import Config
from src.extensions import mongo, bcrypt, jwt

# Blueprints
from src.routes.health_routes import health_bp
from src.routes.auth_routes import auth_bp
from src.routes.user_routes import user_bp
from src.routes.scan_routes import scan_bp
from src.routes.infer_routes import infer_bp
from src.routes.report_routes import report_bp
from src.routes.admin_routes import admin_bp
from src.routes.settings_routes import settings_bp
from src.routes.chatbot_routes import chatbot_bp

from src.db.indexes import create_indexes
from src.middleware.error_handler import register_error_handlers


def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="/static",
    )

    # Load config
    app.config.from_object(Config)

    # CORS
    cors_origins = app.config.get(
        "CORS_ORIGINS",
        [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
    )

    if cors_origins == "*" or cors_origins == ["*"]:
        cors_origins = "*"

    CORS(
        app,
        resources={r"/api/*": {"origins": cors_origins}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    # Preflight fix
    @app.before_request
    def handle_options():
        if request.method == "OPTIONS":
            return "", 200

    # Init extensions
    mongo.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Error handlers
    register_error_handlers(app)

    # DB indexes
    with app.app_context():
        create_indexes()

    # Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(scan_bp)
    app.register_blueprint(infer_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(chatbot_bp)

    @app.get("/")
    def root():
        return jsonify(
            {
                "message": "Backend running 🚀",
                "health": "/api/health",
            }
        ), 200

    return app


# ✅ REQUIRED for Gunicorn / Render
app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
