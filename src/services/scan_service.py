# backend/src/services/scan_service.py
"""
Scan Service
- Upload & save scan metadata
- List/get/delete scans
- Update prediction results on scan record
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from werkzeug.utils import secure_filename

from src.extensions import mongo
from src.db.collections import SCANS

ALLOWED_EXT = {"png", "jpg", "jpeg", "webp"}


def _to_objectid(x: str):
    from bson import ObjectId
    try:
        return ObjectId(x)
    except Exception:
        return None


def _allowed(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXT


def _public_scan(s: dict) -> dict:
    return {
        "id": str(s.get("_id")),
        "userId": s.get("userId"),
        "fileName": s.get("fileName", ""),
        "imageUrl": s.get("imageUrl", ""),
        "createdAt": s.get("createdAt", ""),
        "stage": s.get("stage", ""),
        "confidence": s.get("confidence", None),
        "probs": s.get("probs", None),
        "heatmapUrl": s.get("heatmapUrl", ""),
    }


def list_scans(user_id: str, limit: int = 50) -> List[dict]:
    docs = list(mongo.db[SCANS].find({"userId": user_id}).sort("createdAt", -1).limit(limit))
    return [_public_scan(d) for d in docs]


def get_scan(user_id: str, scan_id: str) -> Optional[dict]:
    doc = mongo.db[SCANS].find_one({"_id": _to_objectid(scan_id), "userId": user_id})
    return _public_scan(doc) if doc else None


def delete_scan(user_id: str, scan_id: str) -> bool:
    doc = mongo.db[SCANS].find_one({"_id": _to_objectid(scan_id), "userId": user_id})
    if not doc:
        return False

    # best effort delete file
    try:
        p = doc.get("imagePath")
        if p:
            Path(p).unlink(missing_ok=True)
    except Exception:
        pass

    mongo.db[SCANS].delete_one({"_id": _to_objectid(scan_id), "userId": user_id})
    return True


def upload_scan(user_id: str, file_obj, upload_dir: Path) -> dict:
    """
    file_obj: werkzeug FileStorage
    upload_dir: absolute path (Config.UPLOAD_DIR)

    Returns:
      { scanId, scan }
    """
    if not file_obj or not getattr(file_obj, "filename", ""):
        raise ValueError("No file selected")

    if not _allowed(file_obj.filename):
        raise ValueError("Invalid file type")

    safe = secure_filename(file_obj.filename)
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    final_name = f"{user_id}_{stamp}_{safe}"

    upload_dir.mkdir(parents=True, exist_ok=True)
    abs_path = upload_dir / final_name
    file_obj.save(str(abs_path))

    image_url = f"/static/uploads/{final_name}"

    doc = {
        "userId": user_id,
        "fileName": safe,
        "imageUrl": image_url,
        "imagePath": str(abs_path),
        "createdAt": datetime.utcnow().isoformat(),
        "stage": "",
        "confidence": None,
        "probs": None,
        "heatmapUrl": "",
    }

    ins = mongo.db[SCANS].insert_one(doc)
    doc["_id"] = ins.inserted_id

    return {"scanId": str(ins.inserted_id), "scan": _public_scan(doc)}


def update_prediction(user_id: str, scan_id: str, pred: Dict) -> bool:
    """
    pred should contain:
      stage, confidence, probs, heatmapUrl (optional)
    """
    res = mongo.db[SCANS].update_one(
        {"_id": _to_objectid(scan_id), "userId": user_id},
        {
            "$set": {
                "stage": pred.get("stage", ""),
                "confidence": pred.get("confidence", None),
                "probs": pred.get("probs", None),
                "heatmapUrl": pred.get("heatmapUrl", ""),
            }
        },
    )
    return res.matched_count > 0
