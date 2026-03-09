# # backend/src/ai/model_loader.py
# """
# Model loader with caching (production-friendly).

# - Loads a TensorFlow/Keras model from .keras / .h5
# - Caches the loaded model in memory so it doesn't reload every request
# - Keeps imports lazy so backend can still run even if TF isn't installed yet
# """

# import os
# import threading
# from typing import Optional, Any

# _MODEL = None
# _MODEL_PATH = None
# _LOCK = threading.Lock()


# def get_model(model_path: str) -> Any:
#     """
#     Returns a cached model instance.
#     Reloads only if the path changes.
#     """
#     global _MODEL, _MODEL_PATH

#     model_path = os.path.abspath(model_path)

#     with _LOCK:
#         if _MODEL is not None and _MODEL_PATH == model_path:
#             return _MODEL

#         if not os.path.exists(model_path):
#             raise FileNotFoundError(f"Model file not found: {model_path}")

#         # Lazy import so the app doesn't crash if TF isn't installed yet
#         import tensorflow as tf  # noqa: F401

#         # compile=False => faster + avoids missing custom objects issues
#         loaded = tf.keras.models.load_model(model_path, compile=False)

#         _MODEL = loaded
#         _MODEL_PATH = model_path
#         return _MODEL


# def clear_model_cache() -> None:
#     """Force reload on next call."""
#     global _MODEL, _MODEL_PATH
#     with _LOCK:
#         _MODEL = None
#         _MODEL_PATH = None
"""
Model loader with caching.
Loads the model once and reuses it across requests.
"""

import os
import threading
from typing import Any

_MODEL = None
_MODEL_PATH = None
_LOCK = threading.Lock()


def get_model(model_path: str) -> Any:
    global _MODEL, _MODEL_PATH

    model_path = os.path.abspath(model_path)

    with _LOCK:
        if _MODEL is not None and _MODEL_PATH == model_path:
            return _MODEL

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        import tensorflow as tf

        loaded = tf.keras.models.load_model(model_path, compile=False)

        _MODEL = loaded
        _MODEL_PATH = model_path
        return _MODEL


def clear_model_cache() -> None:
    global _MODEL, _MODEL_PATH
    with _LOCK:
        _MODEL = None
        _MODEL_PATH = None