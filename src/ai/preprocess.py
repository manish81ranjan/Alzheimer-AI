# backend/src/ai/preprocess.py
"""
Image preprocessing for inference.

Default pipeline (safe for most CNN models):
- load image (png/jpg/jpeg)
- convert to RGB
- resize to (IMG_SIZE, IMG_SIZE)
- scale to [0, 1]
- add batch dimension

If your trained model expects grayscale or different normalization,
change it here only.
"""

import os
from typing import Tuple
import numpy as np
from PIL import Image

DEFAULT_IMG_SIZE = int(os.getenv("IMG_SIZE", "224"))


def load_image(image_path: str) -> Image.Image:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    img = Image.open(image_path)

    # Some files may be grayscale or RGBA -> normalize to RGB
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def preprocess_image(
    image_path: str,
    img_size: int = DEFAULT_IMG_SIZE,
) -> np.ndarray:
    """
    Returns: np array shape (1, img_size, img_size, 3)
    """
    img = load_image(image_path)

    # Resize (you can choose Image.BILINEAR / BICUBIC too)
    img = img.resize((img_size, img_size))

    arr = np.asarray(img, dtype=np.float32)

    # Normalize
    arr = arr / 255.0

    # Add batch
    arr = np.expand_dims(arr, axis=0)
    return arr


def softmax(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32)
    x = x - np.max(x, axis=-1, keepdims=True)
    ex = np.exp(x)
    return ex / np.sum(ex, axis=-1, keepdims=True)
