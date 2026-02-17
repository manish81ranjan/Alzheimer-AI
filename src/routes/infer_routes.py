# # backend/src/routes/infer_routes.py
# """
# Inference Routes
# - POST /api/infer/<scan_id>  -> runs prediction and stores result in scan document
# - GET  /api/infer/<scan_id>/heatmap (optional placeholder)
# """

# from flask import Blueprint, jsonify, current_app
# from flask_jwt_extended import jwt_required, get_jwt_identity

# from src.extensions import mongo
# from src.ai.predict import run_prediction  # we will create this file next

# infer_bp = Blueprint("infer", __name__, url_prefix="/api/infer")


# def _to_objectid(x: str):
#     from bson import ObjectId
#     try:
#         return ObjectId(x)
#     except Exception:
#         return None


# @infer_bp.post("/<scan_id>")
# @jwt_required()
# def infer(scan_id):
#     """
#     POST /api/infer/:scanId
#     Returns: prediction object
#     """
#     uid = get_jwt_identity()

#     scan = mongo.db.scans.find_one({"_id": _to_objectid(scan_id), "userId": uid})
#     if not scan:
#         return jsonify({"message": "Scan not found."}), 404

#     image_path = scan.get("imagePath")
#     if not image_path:
#         return jsonify({"message": "Scan file missing on server."}), 500

#     # Run AI prediction (model + preprocessing)
#     pred = run_prediction(image_path=image_path, model_path=current_app.config["MODEL_PATH"])

#     # Optional: heatmap (later)
#     heatmap_url = pred.get("heatmapUrl", "")

#     # Store on scan document (so dashboard can show stage)
#     mongo.db.scans.update_one(
#         {"_id": _to_objectid(scan_id), "userId": uid},
#         {
#             "$set": {
#                 "stage": pred.get("stage", ""),
#                 "confidence": pred.get("confidence", None),
#                 "probs": pred.get("probs", None),
#                 "heatmapUrl": heatmap_url,
#             }
#         },
#     )

#     return jsonify({"scanId": scan_id, "prediction": pred}), 200


# @infer_bp.get("/<scan_id>/heatmap")
# @jwt_required()
# def heatmap(scan_id):
#     """
#     GET /api/infer/:scanId/heatmap
#     Placeholder: you can later implement Grad-CAM generation.
#     """
#     uid = get_jwt_identity()
#     scan = mongo.db.scans.find_one({"_id": _to_objectid(scan_id), "userId": uid})
#     if not scan:
#         return jsonify({"message": "Scan not found."}), 404

#     return jsonify({"heatmapUrl": scan.get("heatmapUrl", "")}), 200


# backend/src/routes/infer_routes.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.extensions import mongo
from src.db.collections import SCANS
from src.services.inference_service import run_inference_for_scan

infer_bp = Blueprint("infer", __name__, url_prefix="/api/infer")


def _to_objectid(x: str):
    from bson import ObjectId
    try:
        return ObjectId(x)
    except Exception:
        return None


@infer_bp.post("/<scan_id>")
@jwt_required()
def infer(scan_id):
    """
    POST /api/infer/:scanId
    Runs inference and saves result on scan record.
    """
    uid = get_jwt_identity()
    try:
        pred = run_inference_for_scan(user_id=uid, scan_id=scan_id)
        return jsonify({"scanId": scan_id, "prediction": pred}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": "Inference failed", "detail": str(e)}), 500


@infer_bp.get("/<scan_id>/heatmap")
@jwt_required()
def heatmap(scan_id):
    """
    GET /api/infer/:scanId/heatmap
    Returns heatmapUrl stored in scan record (if any).
    """
    uid = get_jwt_identity()
    scan = mongo.db[SCANS].find_one({"_id": _to_objectid(scan_id), "userId": uid})
    if not scan:
        return jsonify({"message": "Scan not found."}), 404

    return jsonify({"heatmapUrl": scan.get("heatmapUrl", "")}), 200
