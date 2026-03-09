# # backend/src/routes/report_routes.py
# from datetime import datetime
# from pathlib import Path

# from flask import Blueprint, jsonify, current_app, send_from_directory
# from flask_jwt_extended import jwt_required, get_jwt_identity

# from src.extensions import mongo

# report_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


# def _to_objectid(x: str):
#     from bson import ObjectId
#     try:
#         return ObjectId(x)
#     except Exception:
#         return None


# def _public_report(r: dict):
#     return {
#         "id": str(r.get("_id")),
#         "scanId": r.get("scanId"),
#         "userId": r.get("userId"),
#         "stage": r.get("stage"),
#         "confidence": r.get("confidence"),
#         "summary": r.get("summary"),
#         "createdAt": r.get("createdAt"),
#         "pdfUrl": r.get("pdfUrl", ""),
#     }


# @report_bp.get("")
# @jwt_required()
# def list_reports():
#     """
#     GET /api/reports
#     Returns: { reports: [...] }
#     """
#     uid = get_jwt_identity()
#     reports = list(
#         mongo.db.reports.find({"userId": uid}).sort("createdAt", -1).limit(50)
#     )
#     return jsonify({"reports": [_public_report(r) for r in reports]}), 200


# @report_bp.get("/<report_id>")
# @jwt_required()
# def get_report(report_id):
#     """
#     GET /api/reports/:id
#     """
#     uid = get_jwt_identity()
#     report = mongo.db.reports.find_one(
#         {"_id": _to_objectid(report_id), "userId": uid}
#     )
#     if not report:
#         return jsonify({"message": "Report not found."}), 404
#     return jsonify({"report": _public_report(report)}), 200


# @report_bp.post("/<scan_id>/generate")
# @jwt_required()
# def generate_report(scan_id):
#     """
#     POST /api/reports/:scanId/generate
#     Generates a simple clinical-style report from scan prediction.
#     """
#     uid = get_jwt_identity()
#     scan = mongo.db.scans.find_one({"_id": _to_objectid(scan_id), "userId": uid})
#     if not scan:
#         return jsonify({"message": "Scan not found."}), 404

#     stage = scan.get("stage") or "UNKNOWN"
#     confidence = scan.get("confidence")

#     summary = (
#         f"Findings suggest {stage.lower()} cognitive decline patterns. "
#         f"Model confidence: {confidence:.2f}."
#         if confidence is not None
#         else "Prediction pending. Run inference to generate report."
#     )

#     created_at = datetime.utcnow().isoformat()

#     # Placeholder PDF path (actual PDF generation can be added later)
#     report_dir = Path(current_app.config["REPORT_DIR"])
#     pdf_name = f"report_{scan_id}.pdf"
#     pdf_path = report_dir / pdf_name

#     # Create a dummy PDF file if not exists
#     if not pdf_path.exists():
#         pdf_path.write_bytes(b"%PDF-1.4\n% DEMNET MRI Report\n")

#     pdf_url = f"/static/reports/{pdf_name}"

#     doc = {
#         "userId": uid,
#         "scanId": str(scan_id),
#         "stage": stage,
#         "confidence": confidence,
#         "summary": summary,
#         "pdfUrl": pdf_url,
#         "createdAt": created_at,
#         "pdfPath": str(pdf_path),
#     }

#     ins = mongo.db.reports.insert_one(doc)
#     doc["_id"] = ins.inserted_id

#     return jsonify(
#         {"reportId": str(ins.inserted_id), "report": _public_report(doc)}
#     ), 201


# @report_bp.get("/<report_id>/pdf")
# @jwt_required()
# def download_pdf(report_id):
#     """
#     GET /api/reports/:id/pdf
#     Returns the PDF file.
#     """
#     uid = get_jwt_identity()
#     report = mongo.db.reports.find_one(
#         {"_id": _to_objectid(report_id), "userId": uid}
#     )
#     if not report:
#         return jsonify({"message": "Report not found."}), 404

#     pdf_path = Path(report.get("pdfPath", ""))
#     if not pdf_path.exists():
#         return jsonify({"message": "PDF not found."}), 404

#     return send_from_directory(
#         directory=pdf_path.parent,
#         path=pdf_path.name,
#         as_attachment=False,
#         mimetype="application/pdf",
#     )

# # backend/src/routes/report_routes.py
# from pathlib import Path

# from flask import Blueprint, jsonify, send_from_directory
# from flask_jwt_extended import jwt_required, get_jwt_identity

# from src.extensions import mongo
# from src.db.collections import REPORTS
# from src.services.report_service import generate_report_for_scan

# report_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


# def _to_objectid(x: str):
#     from bson import ObjectId
#     try:
#         return ObjectId(x)
#     except Exception:
#         return None


# def _public_report(r: dict) -> dict:
#     return {
#         "id": str(r.get("_id")),
#         "scanId": r.get("scanId"),
#         "userId": r.get("userId"),
#         "stage": r.get("stage", ""),
#         "confidence": r.get("confidence", None),
#         "summary": r.get("summary", ""),
#         "createdAt": r.get("createdAt", ""),
#         "pdfUrl": r.get("pdfUrl", ""),
#     }


# @report_bp.get("")
# @jwt_required()
# def list_reports():
#     """
#     GET /api/reports
#     """
#     uid = get_jwt_identity()
#     reports = list(mongo.db[REPORTS].find({"userId": uid}).sort("createdAt", -1).limit(50))
#     return jsonify({"reports": [_public_report(r) for r in reports]}), 200


# @report_bp.get("/<report_id>")
# @jwt_required()
# def get_report(report_id):
#     """
#     GET /api/reports/:id
#     """
#     uid = get_jwt_identity()
#     r = mongo.db[REPORTS].find_one({"_id": _to_objectid(report_id), "userId": uid})
#     if not r:
#         return jsonify({"message": "Report not found."}), 404
#     return jsonify({"report": _public_report(r)}), 200


# @report_bp.post("/<scan_id>/generate")
# @jwt_required()
# def generate(scan_id):
#     """
#     POST /api/reports/:scanId/generate
#     """
#     # uid = get_jwt_identity()
#     identity = get_jwt_identity()
#     uid = identity["id"] if isinstance(identity, dict) else identity

#     try:
#         data = generate_report_for_scan(user_id=uid, scan_id=scan_id)
#         return jsonify(data), 201
#     except ValueError as e:
#         return jsonify({"message": str(e)}), 404
#     except Exception as e:
#         return jsonify({"message": "Failed to generate report", "detail": str(e)}), 500


# @report_bp.get("/<report_id>/pdf")
# @jwt_required()
# def pdf(report_id):
#     """
#     GET /api/reports/:id/pdf
#     """
#     uid = get_jwt_identity()
#     r = mongo.db[REPORTS].find_one({"_id": _to_objectid(report_id), "userId": uid})
#     if not r:
#         return jsonify({"message": "Report not found."}), 404

#     pdf_path = Path(r.get("pdfPath", ""))
#     if not pdf_path.exists():
#         return jsonify({"message": "PDF not found."}), 404

#     return send_from_directory(
#         directory=str(pdf_path.parent),
#         path=pdf_path.name,
#         as_attachment=False,
#         mimetype="application/pdf",
#     )
# from pathlib import Path

# from flask import Blueprint, jsonify, send_from_directory
# from flask_jwt_extended import jwt_required, get_jwt_identity

# from src.extensions import mongo
# from src.db.collections import REPORTS
# from src.services.report_service import generate_report_for_scan

# report_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


# def _to_objectid(x: str):
#     from bson import ObjectId
#     try:
#         return ObjectId(x)
#     except Exception:
#         return None


# def _uid():
#     """
#     Supports:
#       - old tokens: identity = "user_id"
#       - new tokens: identity = {"id": "...", "role": "..."}
#     """
#     identity = get_jwt_identity()
#     if isinstance(identity, dict):
#         return identity.get("id")
#     return identity


# def _public_report(r: dict) -> dict:
#     return {
#         "id": str(r.get("_id")),
#         "scanId": r.get("scanId", ""),
#         "userId": r.get("userId", ""),
#         "stage": r.get("stage", ""),
#         "confidence": r.get("confidence", None),
#         "summary": r.get("summary", ""),
#         "createdAt": r.get("createdAt", ""),
#         "pdfUrl": r.get("pdfUrl", ""),
#     }


# @report_bp.get("")
# @jwt_required()
# def list_reports():
#     """
#     GET /api/reports
#     """
#     uid = _uid()
#     if not uid:
#         return jsonify({"message": "Invalid token identity."}), 401

#     reports = list(
#         mongo.db[REPORTS]
#         .find({"userId": uid})
#         .sort("createdAt", -1)
#         .limit(50)
#     )

#     return jsonify({"reports": [_public_report(r) for r in reports]}), 200


# @report_bp.get("/<report_id>")
# @jwt_required()
# def get_report(report_id):
#     """
#     GET /api/reports/:id
#     """
#     uid = _uid()
#     if not uid:
#         return jsonify({"message": "Invalid token identity."}), 401

#     oid = _to_objectid(report_id)
#     if not oid:
#         return jsonify({"message": "Invalid report id."}), 400

#     r = mongo.db[REPORTS].find_one({"_id": oid, "userId": uid})
#     if not r:
#         return jsonify({"message": "Report not found."}), 404

#     return jsonify({"report": _public_report(r)}), 200


# @report_bp.post("/<scan_id>/generate")
# @jwt_required()
# def generate(scan_id):
#     """
#     POST /api/reports/:scanId/generate
#     """
#     uid = _uid()
#     if not uid:
#         return jsonify({"message": "Invalid token identity."}), 401

#     try:
#         data = generate_report_for_scan(user_id=uid, scan_id=scan_id)

#         return jsonify({
#             "success": True,
#             **data,
#         }), 201

#     except ValueError as e:
#         return jsonify({"message": str(e)}), 404

#     except Exception as e:
#         return jsonify({
#             "message": "Failed to generate report",
#             "detail": str(e)
#         }), 500


# @report_bp.get("/<report_id>/pdf")
# def pdf(report_id):
#     """
#     GET /api/reports/:id/pdf

#     Public route so browser window.open() can load the PDF directly.
#     """
#     oid = _to_objectid(report_id)
#     if not oid:
#         return jsonify({"message": "Invalid report id."}), 400

#     r = mongo.db[REPORTS].find_one({"_id": oid})
#     if not r:
#         return jsonify({"message": "Report not found."}), 404

#     pdf_path_raw = r.get("pdfPath", "")
#     if not pdf_path_raw:
#         return jsonify({"message": "PDF path missing."}), 404

#     pdf_path = Path(pdf_path_raw)
#     if not pdf_path.exists():
#         return jsonify({"message": "PDF not found."}), 404

#     return send_from_directory(
#         directory=str(pdf_path.parent.resolve()),
#         path=pdf_path.name,
#         as_attachment=False,
#         mimetype="application/pdf",
#     )

from pathlib import Path

from flask import Blueprint, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.extensions import mongo
from src.db.collections import REPORTS
from src.services.report_service import generate_report_for_scan

report_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


def _to_objectid(x: str):
    from bson import ObjectId
    try:
        return ObjectId(x)
    except Exception:
        return None


def _uid():
    identity = get_jwt_identity()
    if isinstance(identity, dict):
        return identity.get("id")
    return identity


def _public_report(r: dict) -> dict:
    return {
        "id": str(r.get("_id")),
        "scanId": r.get("scanId", ""),
        "userId": r.get("userId", ""),
        "stage": r.get("stage", ""),
        "confidence": r.get("confidence", None),
        "summary": r.get("summary", ""),
        "createdAt": r.get("createdAt", ""),
        "pdfUrl": r.get("pdfUrl", ""),
    }


@report_bp.get("")
@jwt_required()
def list_reports():
    uid = _uid()
    if not uid:
        return jsonify({"message": "Invalid token identity."}), 401

    reports = list(
        mongo.db[REPORTS].find({"userId": uid}).sort("createdAt", -1).limit(50)
    )
    return jsonify({"reports": [_public_report(r) for r in reports]}), 200


@report_bp.get("/<report_id>")
@jwt_required()
def get_report(report_id):
    uid = _uid()
    if not uid:
        return jsonify({"message": "Invalid token identity."}), 401

    oid = _to_objectid(report_id)
    if not oid:
        return jsonify({"message": "Invalid report id."}), 400

    r = mongo.db[REPORTS].find_one({"_id": oid, "userId": uid})
    if not r:
        return jsonify({"message": "Report not found."}), 404

    return jsonify({"report": _public_report(r)}), 200


@report_bp.post("/<scan_id>/generate")
@jwt_required()
def generate(scan_id):
    uid = _uid()
    if not uid:
        return jsonify({"message": "Invalid token identity."}), 401

    try:
        data = generate_report_for_scan(user_id=uid, scan_id=scan_id)
        return jsonify({"success": True, **data}), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({
            "message": "Failed to generate report",
            "detail": str(e)
        }), 500


@report_bp.get("/<report_id>/pdf")
def pdf(report_id):
    oid = _to_objectid(report_id)
    if not oid:
        return jsonify({"message": "Invalid report id."}), 400

    r = mongo.db[REPORTS].find_one({"_id": oid})
    if not r:
        return jsonify({"message": "Report not found."}), 404

    pdf_path_raw = r.get("pdfPath", "")
    if not pdf_path_raw:
        return jsonify({"message": "PDF path missing."}), 404

    pdf_path = Path(pdf_path_raw)
    if not pdf_path.exists():
        return jsonify({"message": "PDF not found."}), 404

    return send_from_directory(
        directory=str(pdf_path.parent.resolve()),
        path=pdf_path.name,
        as_attachment=False,
        mimetype="application/pdf",
    )