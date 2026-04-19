

# from flask import Blueprint, jsonify
# from flask_jwt_extended import jwt_required, get_jwt_identity

# from src.models.scan_model import get_scan_by_id
# from src.services.inference_service import run_inference_for_scan

# infer_bp = Blueprint("infer", __name__, url_prefix="/api/infer")


# def _uid():
#     identity = get_jwt_identity()
#     if isinstance(identity, dict):
#         return identity.get("id")
#     return identity


# @infer_bp.post("/<scan_id>")
# @jwt_required()
# def infer(scan_id):
#     uid = _uid()
#     if not uid:
#         return jsonify({"message": "Invalid token identity."}), 401

#     try:
#         pred = run_inference_for_scan(user_id=uid, scan_id=scan_id)
#         scan = get_scan_by_id(uid, scan_id)

#         return jsonify({
#             "success": True,
#             "scanId": scan_id,
#             "prediction": pred,
#             "scan": scan,
#         }), 200

#     except ValueError as e:
#         return jsonify({"message": str(e)}), 404

#     except Exception as e:
#         return jsonify({
#             "message": "Inference failed",
#             "detail": str(e),
#         }), 500


# @infer_bp.get("/<scan_id>/heatmap")
# @jwt_required()
# def heatmap(scan_id):
#     uid = _uid()
#     if not uid:
#         return jsonify({"message": "Invalid token identity."}), 401

#     scan = get_scan_by_id(uid, scan_id)
#     if not scan:
#         return jsonify({"message": "Scan not found."}), 404

#     return jsonify({"heatmapUrl": scan.get("heatmapUrl", "")}), 200

# from flask import Blueprint, jsonify
# from flask_jwt_extended import jwt_required, get_jwt_identity

# from src.models.scan_model import get_scan_by_id
# from src.services.inference_service import run_inference_for_scan

# infer_bp = Blueprint("infer", __name__, url_prefix="/api/infer")


# def _uid():
#     identity = get_jwt_identity()
#     if isinstance(identity, dict):
#         return identity.get("id")
#     return identity


# @infer_bp.post("/<scan_id>")
# @jwt_required()
# def infer(scan_id):
#     uid = _uid()

#     if not uid:
#         return jsonify({"message": "Invalid token identity"}), 401

#     try:
#         prediction = run_inference_for_scan(
#             user_id=uid,
#             scan_id=scan_id
#         )

#         scan = get_scan_by_id(uid, scan_id)

#         return jsonify({
#             "success": True,
#             "scanId": scan_id,
#             "prediction": prediction,
#             "scan": scan,
#         }), 200

#     except ValueError as e:
#         return jsonify({"message": str(e)}), 404

#     except Exception as e:
#         return jsonify({
#             "message": "Inference failed",
#             "detail": str(e),
#         }), 500


# @infer_bp.get("/<scan_id>/heatmap")
# @jwt_required()
# def heatmap(scan_id):
#     uid = _uid()

#     if not uid:
#         return jsonify({"message": "Invalid token identity"}), 401

#     scan = get_scan_by_id(uid, scan_id)

#     if not scan:
#         return jsonify({"message": "Scan not found"}), 404

#     return jsonify({
#         "heatmapUrl": scan.get("heatmapUrl", "")
#     }), 200

# ============================================
# FILE 3: src/routes/infer.py
# FINAL FIXED
# ============================================

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.models.scan_model import get_scan_by_id
from src.services.inference_service import run_inference_for_scan

infer_bp = Blueprint("infer", __name__, url_prefix="/api/infer")


def _uid():
    identity = get_jwt_identity()

    if isinstance(identity, dict):
        return identity.get("id")

    return identity


@infer_bp.post("/<scan_id>")
@jwt_required()
def infer(scan_id):
    uid = _uid()

    if not uid:
        return jsonify({"message": "Invalid token"}), 401

    try:
        scan = get_scan_by_id(uid, scan_id)

        if not scan:
            return jsonify({"message": "Scan not found"}), 404

        prediction = run_inference_for_scan(uid, scan_id)

        return jsonify({
            "success": True,
            "scanId": scan_id,
            "prediction": prediction,
            "scan": scan
        }), 200

    except ValueError as e:
        return jsonify({
            "message": str(e)
        }), 400

    except Exception as e:
        print("🔥 Inference Error:", str(e))

        return jsonify({
            "message": "Inference failed",
            "detail": str(e)
        }), 500


@infer_bp.get("/<scan_id>/heatmap")
@jwt_required()
def heatmap(scan_id):
    uid = _uid()

    if not uid:
        return jsonify({"message": "Invalid token"}), 401

    scan = get_scan_by_id(uid, scan_id)

    if not scan:
        return jsonify({"message": "Scan not found"}), 404

    return jsonify({
        "heatmapUrl": scan.get("heatmapUrl", "")
    }), 200
