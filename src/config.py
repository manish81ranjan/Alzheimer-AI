# # backend/src/config.py
# import os
# from datetime import timedelta
# from pathlib import Path

# # Optional: load .env automatically in local dev
# try:
#     from dotenv import load_dotenv  # pip install python-dotenv
#     load_dotenv()
# except Exception:
#     pass


# class Config:
#     """
#     Central configuration for Flask app.

#     Required ENV:
#       - MONGO_URI
#       - JWT_SECRET_KEY
#     Optional ENV:
#       - FLASK_ENV=development
#       - CORS_ORIGINS=http://localhost:5173,https://your-frontend.com
#       - UPLOAD_DIR, PROCESSED_DIR, HEATMAP_DIR, REPORT_DIR
#       - MAX_CONTENT_LENGTH_MB=25
#     """

#     # -------------------- Core --------------------
#     ENV = os.getenv("FLASK_ENV", "development")
#     DEBUG = ENV == "development"

#     # -------------------- MongoDB --------------------
#     # MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/alzheimer_ai")
#     MONGO_URI = os.getenv("MONGO_URI")

#     # -------------------- JWT --------------------
#     # JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-super-secret")
#     JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")
#     JWT_ACCESS_TOKEN_EXPIRES = timedelta(
#         hours=int(os.getenv("JWT_EXPIRES_HOURS", "24"))
#     )

#     # -------------------- CORS --------------------
#     # Accept comma separated origins
#     _cors = os.getenv("CORS_ORIGINS", "http://localhost:5173")
#     CORS_ORIGINS = [x.strip() for x in _cors.split(",") if x.strip()]

#     # -------------------- Files / Static --------------------
#     # backend/
#     BASE_DIR = Path(__file__).resolve().parents[1]
#     # backend/static/
#     STATIC_DIR = BASE_DIR / "static"

#     UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", STATIC_DIR / "uploads"))
#     PROCESSED_DIR = Path(os.getenv("PROCESSED_DIR", STATIC_DIR / "processed"))
#     HEATMAP_DIR = Path(os.getenv("HEATMAP_DIR", STATIC_DIR / "heatmaps"))
#     REPORT_DIR = Path(os.getenv("REPORT_DIR", STATIC_DIR / "reports"))

#     # Create dirs at startup (safe)
#     for _p in [STATIC_DIR, UPLOAD_DIR, PROCESSED_DIR, HEATMAP_DIR, REPORT_DIR]:
#         _p.mkdir(parents=True, exist_ok=True)

#     # Upload limit
#     MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH_MB", "25")) * 1024 * 1024

#     # -------------------- Model path --------------------
#     # Place your trained model here: backend/src/ai/artifacts/demnet_model.keras (example)
#     MODEL_PATH = os.getenv(
#         "MODEL_PATH",
#         str((BASE_DIR / "src" / "ai" / "artifacts" / "demnet_model.keras").resolve()),
#     )

# # backend/src/config.py
# import os
# from datetime import timedelta
# from pathlib import Path

# # ✅ Load .env in local dev (safe on production)
# try:
#     from dotenv import load_dotenv  # pip install python-dotenv
#     load_dotenv()
# except Exception:
#     pass


# class Config:
#     """
#     Central configuration for Flask app.

#     Required ENV (production):
#       - MONGO_URI
#       - JWT_SECRET_KEY

#     Optional ENV:
#       - FLASK_ENV=development|production
#       - CORS_ORIGINS=http://localhost:5173,https://your-frontend.com OR *
#       - UPLOAD_DIR, PROCESSED_DIR, HEATMAP_DIR, REPORT_DIR
#       - MAX_CONTENT_LENGTH_MB=25
#       - GEMINI_API_KEY, GEMINI_MODEL
#       - MODEL_PATH
#     """

#     # -------------------- Core --------------------
#     ENV = os.getenv("FLASK_ENV", "development")
#     DEBUG = ENV == "development"

#     # -------------------- MongoDB --------------------
#     # In dev you can keep a fallback. In production you SHOULD set MONGO_URI.
#     MONGO_URI = os.getenv("MONGO_URI") or "mongodb://127.0.0.1:27017/alzheimer_ai"

#     # -------------------- JWT --------------------
#     JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")
#     JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_EXPIRES_HOURS", "24")))

#     # -------------------- CORS --------------------
#     # Accept comma-separated origins OR "*"
#     _cors = (os.getenv("CORS_ORIGINS") or "http://localhost:5173").strip()

#     if _cors == "*" or _cors.lower() == "all":
#         CORS_ORIGINS = "*"  # allow all (dev only)
#     else:
#         CORS_ORIGINS = [x.strip() for x in _cors.split(",") if x.strip()]

#     # -------------------- Files / Static --------------------
#     # backend/
#     BASE_DIR = Path(__file__).resolve().parents[1]
#     # backend/static/
#     STATIC_DIR = BASE_DIR / "static"

#     UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(STATIC_DIR / "uploads")))
#     PROCESSED_DIR = Path(os.getenv("PROCESSED_DIR", str(STATIC_DIR / "processed")))
#     HEATMAP_DIR = Path(os.getenv("HEATMAP_DIR", str(STATIC_DIR / "heatmaps")))
#     REPORT_DIR = Path(os.getenv("REPORT_DIR", str(STATIC_DIR / "reports")))

#     # Create dirs at startup (safe)
#     for _p in [STATIC_DIR, UPLOAD_DIR, PROCESSED_DIR, HEATMAP_DIR, REPORT_DIR]:
#         _p.mkdir(parents=True, exist_ok=True)

#     # Upload limit
#     MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH_MB", "25")) * 1024 * 1024

#     # -------------------- AI Model --------------------
#     MODEL_PATH = os.getenv(
#         "MODEL_PATH",
#         str((BASE_DIR / "src" / "ai" / "artifacts" / "demnet_model.keras").resolve()),
#     )

#     # -------------------- Gemini (Chatbot) --------------------
#     GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
#     GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

#     # -------------------- Optional Strict Checks --------------------
#     # If you want production to fail fast when env missing:
#     if ENV == "production":
#         if not os.getenv("MONGO_URI"):
#             raise RuntimeError("Missing required ENV: MONGO_URI")
#         if not os.getenv("JWT_SECRET_KEY"):
#             raise RuntimeError("Missing required ENV: JWT_SECRET_KEY")
# import os
# from datetime import timedelta
# from pathlib import Path

# try:
#     from dotenv import load_dotenv
#     load_dotenv()
# except Exception:
#     pass


# class Config:
#     """
#     Central configuration for Flask app.
#     Localhost + Render friendly.
#     """

#     # -------------------- Core --------------------
#     ENV = os.getenv("FLASK_ENV", "development")
#     DEBUG = ENV == "development"

#     # -------------------- Paths --------------------
#     # backend/src/config.py -> parents[1] = backend/
#     BASE_DIR = Path(__file__).resolve().parents[1]
#     ROOT_DIR = BASE_DIR.parent

#     # IMPORTANT:
#     # Your real static files are in backend/src/static
#     STATIC_DIR = BASE_DIR / "src" / "static"

#     UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(STATIC_DIR / "uploads")))
#     PROCESSED_DIR = Path(os.getenv("PROCESSED_DIR", str(STATIC_DIR / "processed")))
#     HEATMAP_DIR = Path(os.getenv("HEATMAP_DIR", str(STATIC_DIR / "heatmaps")))
#     REPORT_DIR = Path(os.getenv("REPORT_DIR", str(STATIC_DIR / "reports")))

#     # create folders safely
#     for _p in [STATIC_DIR, UPLOAD_DIR, PROCESSED_DIR, HEATMAP_DIR, REPORT_DIR]:
#         _p.mkdir(parents=True, exist_ok=True)

#     # -------------------- MongoDB --------------------
#     MONGO_URI = os.getenv("MONGO_URI") or "mongodb://127.0.0.1:27017/alzheimer_ai"

#     # -------------------- JWT --------------------
#     JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")
#     JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_EXPIRES_HOURS", "24")))

#     # -------------------- CORS --------------------
#     _cors = (
#         os.getenv("CORS_ORIGINS")
#         or "http://localhost:5173,http://127.0.0.1:5173"
#     ).strip()

#     if _cors == "*" or _cors.lower() == "all":
#         CORS_ORIGINS = "*"
#     else:
#         CORS_ORIGINS = [x.strip() for x in _cors.split(",") if x.strip()]

#     # -------------------- Upload limit --------------------
#     MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH_MB", "25")) * 1024 * 1024

#     # -------------------- AI / ML --------------------
#     # Prefer env, otherwise use repo-root ml/artifacts
#     MODEL_PATH = os.getenv(
#     "MODEL_PATH",
#     str((ROOT_DIR / "ml" / "artifacts" / "best_demnet_model (1).keras").resolve()),
#     )

#     CLASS_MAP_PATH = os.getenv(
#     "CLASS_MAP_PATH",
#     str((ROOT_DIR / "ml" / "artifacts" / "class_map.json").resolve()),
#     )

#     METRICS_PATH = os.getenv(
#     "METRICS_PATH",
#     str((ROOT_DIR / "ml" / "artifacts" / "metrics.json").resolve()),
#     )

#     IMG_SIZE = int(os.getenv("IMG_SIZE", "224"))
#     MODEL_NAME = os.getenv("MODEL_NAME", "DEMNET-Lite")
#     MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0")

#     # -------------------- Gemini --------------------
#     GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
#     GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

#     # -------------------- Production strict checks --------------------
#     if ENV == "production":
#         if not os.getenv("MONGO_URI"):
#             raise RuntimeError("Missing required ENV: MONGO_URI")
#         if not os.getenv("JWT_SECRET_KEY"):
#             raise RuntimeError("Missing required ENV: JWT_SECRET_KEY")


import os
from datetime import timedelta
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


class Config:
    """
    Central configuration for Flask app.
    Works for localhost and Render deployment.
    """

    # -------------------- Core --------------------
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = ENV == "development"

    # -------------------- Paths --------------------
    # backend/src/config.py
    BASE_DIR = Path(__file__).resolve().parents[1]     # backend/
    ROOT_DIR = BASE_DIR.parent                         # project root

    # backend/src/static
    STATIC_DIR = BASE_DIR / "src" / "static"

    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(STATIC_DIR / "uploads")))
    PROCESSED_DIR = Path(os.getenv("PROCESSED_DIR", str(STATIC_DIR / "processed")))
    HEATMAP_DIR = Path(os.getenv("HEATMAP_DIR", str(STATIC_DIR / "heatmaps")))
    REPORT_DIR = Path(os.getenv("REPORT_DIR", str(STATIC_DIR / "reports")))

    # Create directories automatically
    for _p in [STATIC_DIR, UPLOAD_DIR, PROCESSED_DIR, HEATMAP_DIR, REPORT_DIR]:
        _p.mkdir(parents=True, exist_ok=True)

    # -------------------- MongoDB --------------------
    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb://127.0.0.1:27017/alzheimer_ai"
    )

    # -------------------- JWT --------------------
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.getenv("JWT_EXPIRES_HOURS", "24"))
    )

    # -------------------- CORS --------------------
    _cors = (
        os.getenv("CORS_ORIGINS")
        or "http://localhost:5173,http://127.0.0.1:5173"
    ).strip()

    if _cors == "*" or _cors.lower() == "all":
        CORS_ORIGINS = "*"
    else:
        CORS_ORIGINS = [x.strip() for x in _cors.split(",") if x.strip()]

    # -------------------- Upload limit --------------------
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH_MB", "25")) * 1024 * 1024

    # -------------------- AI / ML --------------------
    # IMPORTANT: model stored in project-root/ml/artifacts/

    MODEL_PATH = os.getenv(
        "MODEL_PATH",
        str((ROOT_DIR / "ml" / "artifacts" / "best_demnet_model (1).keras").resolve()),
    )

    CLASS_MAP_PATH = os.getenv(
        "CLASS_MAP_PATH",
        str((ROOT_DIR / "ml" / "artifacts" / "class_map.json").resolve()),
    )

    METRICS_PATH = os.getenv(
        "METRICS_PATH",
        str((ROOT_DIR / "ml" / "artifacts" / "metrics.json").resolve()),
    )

    IMG_SIZE = int(os.getenv("IMG_SIZE", "128"))

    MODEL_NAME = os.getenv("MODEL_NAME", "DEMNET-Lite")
    MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0")

    # -------------------- Gemini --------------------
    GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()

    GEMINI_MODEL = os.getenv(
        "GEMINI_MODEL",
        "gemini-1.5-flash"
    )

    # -------------------- Production checks --------------------
    if ENV == "production":
        if not os.getenv("MONGO_URI"):
            raise RuntimeError("Missing required ENV: MONGO_URI")

        if not os.getenv("JWT_SECRET_KEY"):
            raise RuntimeError("Missing required ENV: JWT_SECRET_KEY")