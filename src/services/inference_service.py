# # backend/src/services/inference_service.py
# """
# Inference Service
# - Runs model prediction for a scan
# - Updates scan record with stage/confidence/probs/heatmapUrl

# Uses:
#   - src.ai.predict.run_prediction (currently mock, replace later with real model)
#   - src.services.scan_service.update_prediction
# """

# from flask import current_app

# from src.extensions import mongo
# from src.db.collections import SCANS
# from src.services.scan_service import update_prediction
# from src.ai.predict import run_prediction


# def _to_objectid(x: str):
#     from bson import ObjectId
#     try:
#         return ObjectId(x)
#     except Exception:
#         return None


# def run_inference_for_scan(user_id: str, scan_id: str) -> dict:
#     """
#     Returns prediction dict:
#       {stage, confidence, probs, model, version, heatmapUrl}
#     """
#     scan = mongo.db[SCANS].find_one({"_id": _to_objectid(scan_id), "userId": user_id})
#     if not scan:
#         raise ValueError("Scan not found")

#     image_path = scan.get("imagePath")
#     if not image_path:
#         raise RuntimeError("Scan file missing on server")

#     model_path = current_app.config.get("MODEL_PATH", "")

#     pred = run_prediction(image_path=image_path, model_path=model_path)

#     # Persist on scan record
#     ok = update_prediction(user_id=user_id, scan_id=scan_id, pred=pred)
#     if not ok:
#         raise RuntimeError("Failed to update scan prediction")

#     return pred
# from flask import current_app

# from src.models.scan_model import get_raw_scan_by_id, update_prediction
# from src.ai.predict import run_prediction


# def run_inference_for_scan(user_id: str, scan_id: str) -> dict:
#     """
#     Finds a scan, runs real model inference, stores result on scan.
#     """
#     scan = get_raw_scan_by_id(user_id=user_id, scan_id=scan_id)
#     if not scan:
#         raise ValueError("Scan not found")

#     image_path = scan.get("imagePath")
#     if not image_path:
#         raise RuntimeError("Scan file missing on server")

#     model_path = current_app.config.get("MODEL_PATH", "")
#     if not model_path:
#         raise RuntimeError("MODEL_PATH is not configured")

#     pred = run_prediction(image_path=image_path, model_path=model_path)

#     ok = update_prediction(user_id=user_id, scan_id=scan_id, pred=pred)
#     if not ok:
#         raise RuntimeError("Failed to update scan prediction")

#     return pred
# from flask import current_app

# from src.models.scan_model import get_raw_scan_by_id, update_prediction
# from src.ai.predict import run_prediction
# from src.ai.gradcam import generate_gradcam


# def run_inference_for_scan(user_id: str, scan_id: str) -> dict:
#     """
#     Finds a scan, runs model inference, generates Grad-CAM, stores result on scan.
#     """
#     scan = get_raw_scan_by_id(user_id=user_id, scan_id=scan_id)
#     if not scan:
#         raise ValueError("Scan not found")

#     image_path = scan.get("imagePath")
#     if not image_path:
#         raise RuntimeError("Scan file missing on server")

#     model_path = current_app.config.get("MODEL_PATH", "")
#     if not model_path:
#         raise RuntimeError("MODEL_PATH is not configured")

#     pred = run_prediction(image_path=image_path, model_path=model_path)

#     # map predicted stage to index
#     class_order = ["ND", "VMD", "MID", "MOD"]
#     pred_index = class_order.index(pred["stage"]) if pred["stage"] in class_order else None

#     try:
#         heatmap_url = generate_gradcam(
#             image_path=image_path,
#             model_path=model_path,
#             pred_index=pred_index,
#         )
#     except Exception as e:
#         print("[GRADCAM_ERROR]", str(e))
#         heatmap_url = ""

#     pred["heatmapUrl"] = heatmap_url

#     ok = update_prediction(user_id=user_id, scan_id=scan_id, pred=pred)
#     if not ok:
#         raise RuntimeError("Failed to update scan prediction")

#     return pred

from flask import current_app

from src.models.scan_model import get_raw_scan_by_id, update_prediction
from src.ai.predict import run_prediction
from src.ai.gradcam import generate_gradcam


def run_inference_for_scan(user_id: str, scan_id: str) -> dict:
    """
    Finds a scan, runs model inference, generates Grad-CAM, stores result on scan.
    """
    scan = get_raw_scan_by_id(user_id=user_id, scan_id=scan_id)
    if not scan:
        raise ValueError("Scan not found")

    image_path = scan.get("imagePath")
    if not image_path:
        raise RuntimeError("Scan file missing on server")

    model_path = current_app.config.get("MODEL_PATH", "")
    if not model_path:
        raise RuntimeError("MODEL_PATH is not configured")

    pred = run_prediction(image_path=image_path, model_path=model_path)

    class_order = ["ND", "VMD", "MID", "MOD"]
    pred_index = class_order.index(pred["stage"]) if pred.get("stage") in class_order else None

    try:
        heatmap_url = generate_gradcam(
            image_path=image_path,
            model_path=model_path,
            pred_index=pred_index,
        )
    except Exception as e:
        print("[GRADCAM_ERROR]", str(e))
        heatmap_url = ""

    pred["heatmapUrl"] = heatmap_url

    ok = update_prediction(user_id=user_id, scan_id=scan_id, pred=pred)
    if not ok:
        raise RuntimeError("Failed to update scan prediction")

    return pred