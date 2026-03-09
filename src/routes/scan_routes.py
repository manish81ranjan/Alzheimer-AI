# # backend/src/routes/scan_routes.py
# import os
# from datetime import datetime
# from pathlib import Path

# from flask import Blueprint, request, jsonify, current_app
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from werkzeug.utils import secure_filename

# from src.extensions import mongo

# scan_bp = Blueprint("scans", __name__, url_prefix="/api/scans")

# ALLOWED_EXT = {"png", "jpg", "jpeg", "webp"}


# def _to_objectid(x: str):
#     from bson import ObjectId
#     try:
#         return ObjectId(x)
#     except Exception:
#         return None


# def _allowed(filename: str):
#     if "." not in filename:
#         return False
#     ext = filename.rsplit(".", 1)[1].lower()
#     return ext in ALLOWED_EXT


# def _uid():
#     """
#     Supports:
#       - old tokens: identity = "user_id"
#       - new tokens: identity = {"id": "...", "role": "..."}
#     Always returns a string user id.
#     """
#     identity = get_jwt_identity()
#     if isinstance(identity, dict):
#         return identity.get("id")
#     return identity


# def _public_scan(s: dict):
#     return {
#         "id": str(s.get("_id")),
#         "userId": s.get("userId", ""),
#         "fileName": s.get("fileName", ""),
#         "imageUrl": s.get("imageUrl", ""),
#         "createdAt": s.get("createdAt", ""),
#         "stage": s.get("stage", ""),
#         "confidence": s.get("confidence", None),
#         "probs": s.get("probs", None),
#         "heatmapUrl": s.get("heatmapUrl", ""),
#     }


# @scan_bp.get("")
# @jwt_required()
# def list_scans():
#     """
#     GET /api/scans
#     Returns: { scans: [...] }
#     """
#     uid = _uid()
#     if not uid:
#         return jsonify({"message": "Invalid token identity."}), 401

#     scans = list(
#         mongo.db.scans.find({"userId": uid}).sort("createdAt", -1).limit(50)
#     )
#     return jsonify({"scans": [_public_scan(s) for s in scans]}), 200


# @scan_bp.get("/<scan_id>")
# @jwt_required()
# def get_scan(scan_id):
#     """
#     GET /api/scans/:id
#     """
#     uid = _uid()
#     if not uid:
#         return jsonify({"message": "Invalid token identity."}), 401

#     scan = mongo.db.scans.find_one({"_id": _to_objectid(scan_id), "userId": uid})
#     if not scan:
#         return jsonify({"message": "Scan not found."}), 404

#     return jsonify({"scan": _public_scan(scan)}), 200


# @scan_bp.delete("/<scan_id>")
# @jwt_required()
# def delete_scan(scan_id):
#     """
#     DELETE /api/scans/:id
#     """
#     uid = _uid()
#     if not uid:
#         return jsonify({"message": "Invalid token identity."}), 401

#     scan = mongo.db.scans.find_one({"_id": _to_objectid(scan_id), "userId": uid})
#     if not scan:
#         return jsonify({"message": "Scan not found."}), 404

#     # best-effort file delete
#     try:
#         image_path = scan.get("imagePath")
#         if image_path and os.path.exists(image_path):
#             os.remove(image_path)
#     except Exception:
#         pass

#     mongo.db.scans.delete_one({"_id": _to_objectid(scan_id), "userId": uid})
#     return jsonify({"success": True}), 200


# @scan_bp.post("/upload")
# @jwt_required()
# def upload_scan():
#     """
#     POST /api/scans/upload (multipart/form-data)
#     FormData: file=<image>
#     Returns: { scanId, scan }
#     """
#     uid = _uid()
#     if not uid:
#         return jsonify({"message": "Invalid token identity."}), 401

#     if "file" not in request.files:
#         return jsonify({"message": "file is required."}), 400

#     f = request.files["file"]
#     if not f or f.filename == "":
#         return jsonify({"message": "No file selected."}), 400

#     if not _allowed(f.filename):
#         return jsonify({"message": "Invalid file type."}), 400

#     # Save file
#     upload_dir = Path(current_app.config["UPLOAD_DIR"])
#     upload_dir.mkdir(parents=True, exist_ok=True)

#     safe = secure_filename(f.filename)
#     stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
#     final_name = f"{uid}_{stamp}_{safe}"
#     abs_path = upload_dir / final_name
#     f.save(str(abs_path))

#     image_url = f"/static/uploads/{final_name}"

#     doc = {
#         "userId": uid,
#         "fileName": safe,
#         "imageUrl": image_url,
#         "imagePath": str(abs_path),
#         "createdAt": datetime.utcnow().isoformat(),
#         "stage": "",
#         "confidence": None,
#         "probs": None,
#         "heatmapUrl": "",
#     }

#     ins = mongo.db.scans.insert_one(doc)
#     doc["_id"] = ins.inserted_id

#     return jsonify({"scanId": str(ins.inserted_id), "scan": _public_scan(doc)}), 201

import os
from datetime import datetime
from pathlib import Path

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.models.scan_model import (
    create_scan,
    list_scans_by_user,
    get_scan_by_id,
    get_raw_scan_by_id,
    delete_scan_by_id,
)
from src.utils.file_utils import safe_filename, file_size_ok, build_static_url

scan_bp = Blueprint("scans", __name__, url_prefix="/api/scans")

ALLOWED_EXT = {"png", "jpg", "jpeg", "webp"}


def _allowed(filename: str):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXT


def _uid():
    """
    Supports:
      - old tokens: identity = "user_id"
      - new tokens: identity = {"id": "...", "role": "..."}
    """
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return identity.get("id")
    return identity


@scan_bp.get("")
@jwt_required()
def list_scans():
    uid = _uid()
    if not uid:
        return jsonify({"message": "Invalid token identity."}), 401

    scans = list_scans_by_user(uid, limit=50)
    return jsonify({"scans": scans}), 200


@scan_bp.get("/<scan_id>")
@jwt_required()
def get_scan(scan_id):
    uid = _uid()
    if not uid:
        return jsonify({"message": "Invalid token identity."}), 401

    scan = get_scan_by_id(uid, scan_id)
    if not scan:
        return jsonify({"message": "Scan not found."}), 404

    return jsonify({"scan": scan}), 200


@scan_bp.delete("/<scan_id>")
@jwt_required()
def delete_scan(scan_id):
    uid = _uid()
    if not uid:
        return jsonify({"message": "Invalid token identity."}), 401

    raw_scan = get_raw_scan_by_id(uid, scan_id)
    if not raw_scan:
        return jsonify({"message": "Scan not found."}), 404

    try:
        image_path = raw_scan.get("imagePath")
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
    except Exception:
        pass

    deleted = delete_scan_by_id(uid, scan_id)
    if not deleted:
        return jsonify({"message": "Scan not found."}), 404

    return jsonify({"success": True}), 200


@scan_bp.post("/upload")
@jwt_required()
def upload_scan():
    """
    POST /api/scans/upload
    multipart/form-data
    FormData: file=<image>

    Returns:
      { scanId, scan }
    """
    uid = _uid()
    if not uid:
        return jsonify({"message": "Invalid token identity."}), 401

    if "file" not in request.files:
        return jsonify({"message": "file is required."}), 400

    f = request.files["file"]
    if not f or f.filename == "":
        return jsonify({"message": "No file selected."}), 400

    if not _allowed(f.filename):
        return jsonify({"message": "Invalid file type. Allowed: png, jpg, jpeg, webp"}), 400

    max_bytes = int(current_app.config.get("MAX_CONTENT_LENGTH", 25 * 1024 * 1024))
    if not file_size_ok(f, max_bytes):
        return jsonify({"message": "File too large."}), 400

    upload_dir = Path(current_app.config["UPLOAD_DIR"])
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_name = safe_filename(f.filename)
    if not original_name:
        return jsonify({"message": "Invalid filename."}), 400

    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    final_name = f"{uid}_{stamp}_{original_name}"

    abs_path = upload_dir / final_name
    f.save(str(abs_path))

    image_url = build_static_url("uploads", final_name)

    scan = create_scan(
        {
            "userId": uid,
            "fileName": original_name,
            "imageUrl": image_url,
            "imagePath": str(abs_path),
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat(),
            "stage": "",
            "confidence": None,
            "probs": None,
            "model": "",
            "version": "",
            "heatmapUrl": "",
        }
    )

    return jsonify({"scanId": scan["id"], "scan": scan}), 201