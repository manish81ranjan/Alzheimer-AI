# backend/src/services/inference_service.py
"""
Inference Service
- Runs model prediction for a scan
- Updates scan record with stage/confidence/probs/heatmapUrl

Uses:
  - src.ai.predict.run_prediction (currently mock, replace later with real model)
  - src.services.scan_service.update_prediction
"""

from flask import current_app

from src.extensions import mongo
from src.db.collections import SCANS
from src.services.scan_service import update_prediction
from src.ai.predict import run_prediction


def _to_objectid(x: str):
    from bson import ObjectId
    try:
        return ObjectId(x)
    except Exception:
        return None


def run_inference_for_scan(user_id: str, scan_id: str) -> dict:
    """
    Returns prediction dict:
      {stage, confidence, probs, model, version, heatmapUrl}
    """
    scan = mongo.db[SCANS].find_one({"_id": _to_objectid(scan_id), "userId": user_id})
    if not scan:
        raise ValueError("Scan not found")

    image_path = scan.get("imagePath")
    if not image_path:
        raise RuntimeError("Scan file missing on server")

    model_path = current_app.config.get("MODEL_PATH", "")

    pred = run_prediction(image_path=image_path, model_path=model_path)

    # Persist on scan record
    ok = update_prediction(user_id=user_id, scan_id=scan_id, pred=pred)
    if not ok:
        raise RuntimeError("Failed to update scan prediction")

    return pred
