

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

#     class_order = ["ND", "VMD", "MID", "MOD"]
#     pred_index = class_order.index(pred["stage"]) if pred.get("stage") in class_order else None

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
# import numpy as np
# from PIL import Image

# from src.config import Config
# from src.models.scan_model import get_scan_by_id, update_scan_prediction

# # Lazy load model (VERY IMPORTANT)
# MODEL = None

# CLASS_NAMES = ["ND", "VMD", "MID", "MOD"]


# def get_model():
#     global MODEL

#     if MODEL is None:
#         try:
#             from tensorflow.keras.models import load_model
#             MODEL = load_model(Config.MODEL_PATH)
#             print("✅ Model loaded successfully")
#         except Exception as e:
#             print("❌ Model load failed:", str(e))
#             raise RuntimeError("Model not available")

#     return MODEL


# def preprocess_image(path):
#     img = Image.open(path).convert("RGB")
#     img = img.resize((Config.IMG_SIZE, Config.IMG_SIZE))
#     arr = np.array(img) / 255.0
#     arr = np.expand_dims(arr, axis=0)
#     return arr


# def run_inference_for_scan(user_id, scan_id):
#     scan = get_scan_by_id(user_id, scan_id)

#     if not scan:
#         raise ValueError("Scan not found")

#     file_path = scan.get("filePath")

#     if not file_path:
#         raise ValueError("Scan file path missing")

#     # preprocess
#     x = preprocess_image(file_path)

#     # load model (lazy)
#     model = get_model()

#     # predict
#     preds = model.predict(x)[0]
#     idx = int(np.argmax(preds))

#     result = {
#         "label": CLASS_NAMES[idx],
#         "confidence": float(preds[idx]),
#         "probs": preds.tolist(),
#     }

#     # save prediction in DB
#     update_scan_prediction(user_id, scan_id, result)

#     return result


# import numpy as np
# from PIL import Image

# from src.config import Config
# from src.models.scan_model import get_scan_by_id, update_prediction

# MODEL = None

# CLASS_NAMES = [
#     "ND",
#     "VMD",
#     "MID",
#     "MOD"
# ]


# def get_model():
#     global MODEL

#     if MODEL is None:
#         try:
#             from tensorflow.keras.models import load_model

#             MODEL = load_model(Config.MODEL_PATH)
#             print("Model loaded successfully")

#         except Exception as e:
#             print("Model load failed:", str(e))
#             raise RuntimeError("Model file not available")

#     return MODEL


# def preprocess_image(path):
#     img = Image.open(path).convert("RGB")
#     img = img.resize((Config.IMG_SIZE, Config.IMG_SIZE))

#     arr = np.array(img).astype("float32") / 255.0
#     arr = np.expand_dims(arr, axis=0)

#     return arr


# def run_inference_for_scan(user_id, scan_id):
#     scan = get_scan_by_id(user_id, scan_id)

#     if not scan:
#         raise ValueError("Scan not found")

#     file_path = scan.get("imagePath")

#     if not file_path:
#         raise ValueError("Image path missing")

#     x = preprocess_image(file_path)

#     model = get_model()

#     preds = model.predict(x, verbose=0)[0]
#     idx = int(np.argmax(preds))

#     result = {
#         "stage": CLASS_NAMES[idx],
#         "confidence": float(preds[idx]),
#         "probs": preds.tolist(),
#         "model": Config.MODEL_NAME,
#         "version": Config.MODEL_VERSION
#     }

#     update_prediction(user_id, scan_id, result)

#     return result



# ============================================
# FILE 2: src/services/inference_service.py
# FINAL FIXED
# ============================================

import os
import numpy as np
from PIL import Image

from src.config import Config
from src.models.scan_model import get_scan_by_id, update_prediction

MODEL = None

CLASS_NAMES = [
    "ND",
    "VMD",
    "MID",
    "MOD"
]


def get_model():
    global MODEL

    if MODEL is None:
        try:
            from tensorflow.keras.models import load_model

            model_path = os.path.abspath(Config.MODEL_PATH)

            print("Loading model:", model_path)

            if not os.path.exists(model_path):
                raise RuntimeError("Model file not found")

            MODEL = load_model(model_path)
            print("✅ Model loaded successfully")

        except Exception as e:
            print("❌ Model load failed:", str(e))
            raise RuntimeError("Unable to load model")

    return MODEL


def preprocess_image(path):
    abs_path = os.path.abspath(path)

    print("Reading image:", abs_path)

    if not os.path.exists(abs_path):
        raise RuntimeError("Image file not found")

    img = Image.open(abs_path).convert("RGB")
    img = img.resize((Config.IMG_SIZE, Config.IMG_SIZE))

    arr = np.array(img).astype("float32") / 255.0
    arr = np.expand_dims(arr, axis=0)

    return arr


def run_inference_for_scan(user_id, scan_id):
    scan = get_scan_by_id(user_id, scan_id)

    if not scan:
        raise ValueError("Scan not found")

    file_path = scan.get("imagePath")

    if not file_path:
        raise ValueError("Image path missing")

    x = preprocess_image(file_path)

    model = get_model()

    preds = model.predict(x, verbose=0)[0]
    idx = int(np.argmax(preds))

    result = {
        "stage": CLASS_NAMES[idx],
        "confidence": float(preds[idx]),
        "probs": preds.tolist(),
        "model": Config.MODEL_NAME,
        "version": Config.MODEL_VERSION
    }

    update_prediction(user_id, scan_id, result)

    return result
