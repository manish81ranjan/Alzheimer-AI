# # backend/src/ai/predict.py
# """
# Prediction pipeline (minimal, API-ready).

# This file provides:
#   run_prediction(image_path, model_path) -> dict

# Right now it returns a MOCK prediction so your full-stack works immediately.
# Later, when you add your real TensorFlow/Keras model, you only replace the
# `mock_predict()` part with real inference.

# Frontend expects:
#   {
#     "stage": "ND|VMD|MID|MOD",
#     "confidence": 0.0-1.0,
#     "probs": {"ND":..., "VMD":..., "MID":..., "MOD":...},
#     "model": "DEMNET-Lite",
#     "version": "v1.0",
#     "heatmapUrl": "" (optional)
#   }
# """

# import random
# from typing import Dict


# CLASSES = ["ND", "VMD", "MID", "MOD"]


# def run_prediction(image_path: str, model_path: str) -> Dict:
#     # -------------------- MOCK PREDICTION --------------------
#     # Replace this block later with:
#     #  - load model (cached)
#     #  - preprocess image
#     #  - run model.predict
#     #  - build probs + stage + confidence
#     return mock_predict()


# def mock_predict() -> Dict:
#     # generate probabilities that sum to 1
#     raw = [random.random() for _ in CLASSES]
#     s = sum(raw)
#     probs = {c: (v / s) for c, v in zip(CLASSES, raw)}

#     # top class
#     stage = max(probs, key=probs.get)
#     confidence = float(probs[stage])

#     return {
#         "stage": stage,
#         "confidence": round(confidence, 4),
#         "probs": {k: round(v, 4) for k, v in probs.items()},
#         "model": "DEMNET-Lite",
#         "version": "v1.0",
#         "heatmapUrl": "",
#     }


# # backend/src/ai/predict.py
# """
# Prediction pipeline (MOCK, API-ready).

# We are intentionally NOT implementing:
# - model_loader.py
# - preprocess.py
# - gradcam.py
# - labels.py
# - demnet_lite_arch.py

# This module ONLY returns a mocked prediction so frontend + backend integration
# works end-to-end (upload -> infer -> report) without ML dependencies.

# Frontend expects:
#   {
#     "stage": "ND|VMD|MID|MOD",
#     "confidence": 0.0-1.0,
#     "probs": {"ND":..., "VMD":..., "MID":..., "MOD":...},
#     "model": "DEMNET-Lite",
#     "version": "v1.0",
#     "heatmapUrl": ""
#   }
# """

# from __future__ import annotations
# import random
# from typing import Dict, Optional

# CLASSES = ["ND", "VMD", "MID", "MOD"]


# def run_prediction(image_path: str, model_path: str, seed: Optional[int] = None) -> Dict:
#     """
#     Returns a mock prediction.

#     Args:
#       image_path: path to uploaded MRI image (not used in mock)
#       model_path: path to model file (not used in mock)
#       seed: set to an int for deterministic output (useful for testing)

#     NOTE:
#       We keep these args to match future real inference signature.
#     """
#     return mock_predict(seed=seed)


# def mock_predict(seed: Optional[int] = None) -> Dict:
#     """
#     Mock prediction generator.
#     - Produces probs that sum to 1
#     - Ensures valid class labels
#     - Returns consistent frontend fields
#     """
#     rng = random.Random(seed) if seed is not None else random

#     # Generate random scores and normalize
#     raw = [rng.random() for _ in CLASSES]
#     total = sum(raw) or 1.0
#     probs = {cls: (val / total) for cls, val in zip(CLASSES, raw)}

#     # Choose top class
#     stage = max(probs, key=probs.get)
#     confidence = float(probs[stage])

#     # Round only for response (store full precision if you want later)
#     probs_rounded = {k: round(v, 4) for k, v in probs.items()}

#     # Fix rounding drift (optional): ensure sum==1.0000 visually
#     # Adjust the top class by the drift.
#     drift = round(1.0 - sum(probs_rounded.values()), 4)
#     probs_rounded[stage] = round(probs_rounded[stage] + drift, 4)

#     # Confidence should match top prob after rounding drift adjustment
#     confidence = float(probs_rounded[stage])

#     return {
#         "stage": stage,
#         "confidence": round(confidence, 4),
#         "probs": probs_rounded,
#         "model": "DEMNET-Lite",
#         "version": "v1.0",
#         "heatmapUrl": "",
#     }


# backend/src/ai/predict.py
"""
Prediction pipeline (REAL inference).

Provides:
  run_prediction(image_path, model_path) -> dict

Frontend expects:
  {
    "stage": "ND|VMD|MID|MOD",
    "confidence": 0.0-1.0,
    "probs": {"ND":..., "VMD":..., "MID":..., "MOD":...},
    "model": "DEMNET-Lite",
    "version": "v1.0",
    "heatmapUrl": "" (optional)
  }
"""

import os
from typing import Dict
import numpy as np

from .model_loader import get_model
from .preprocess import preprocess_image, softmax

# Your project classes (keep this stable for frontend)
CLASSES = ["ND", "VMD", "MID", "MOD"]

MODEL_NAME = os.getenv("MODEL_NAME", "DEMNET-Lite")
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0")


def run_prediction(image_path: str, model_path: str) -> Dict:
    """
    Run real inference:
    - load model (cached)
    - preprocess image
    - model.predict
    - build probs + stage + confidence
    """
    model = get_model(model_path)

    x = preprocess_image(image_path)

    # Predict (supports Keras models)
    # output could be:
    # - (1,4) probabilities
    # - (1,4) logits
    # - (1,1,4) weird shapes -> flatten safely
    y = model.predict(x, verbose=0)

    y = np.asarray(y)

    # Flatten to (4,)
    y = y.reshape(-1)

    if y.shape[0] != len(CLASSES):
        raise ValueError(
            f"Model output shape mismatch. Expected {len(CLASSES)} values, got {y.shape[0]}"
        )

    # If values do not sum near 1, treat as logits and softmax
    s = float(np.sum(y))
    if not (0.98 <= s <= 1.02):
        probs_arr = softmax(y)
    else:
        probs_arr = y

    probs_arr = probs_arr.astype(np.float32)

    probs = {c: float(p) for c, p in zip(CLASSES, probs_arr)}
    stage = max(probs, key=probs.get)
    confidence = float(probs[stage])

    return {
        "stage": stage,
        "confidence": round(confidence, 4),
        "probs": {k: round(v, 4) for k, v in probs.items()},
        "model": MODEL_NAME,
        "version": MODEL_VERSION,
        "heatmapUrl": "",
    }
