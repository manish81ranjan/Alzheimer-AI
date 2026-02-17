# backend/src/utils/image_utils.py
"""
Lightweight image utilities.

Purpose:
- Basic image validation
- Safe image loading
- NO heavy ML dependencies (no TensorFlow / OpenCV required)

This keeps backend stable even without AI stack installed.
"""

from pathlib import Path
from typing import Tuple, Optional

from PIL import Image


ALLOWED_FORMATS = {"PNG", "JPEG", "JPG", "WEBP"}


def is_image_file(path: str | Path) -> bool:
    """
    Check whether a file is a valid image by attempting to open it.
    """
    try:
        with Image.open(path) as img:
            return img.format.upper() in ALLOWED_FORMATS
    except Exception:
        return False


def get_image_size(path: str | Path) -> Optional[Tuple[int, int]]:
    """
    Return (width, height) of image.
    """
    try:
        with Image.open(path) as img:
            return img.size
    except Exception:
        return None


def load_image_rgb(path: str | Path) -> Image.Image:
    """
    Load image and convert to RGB.
    Useful for later ML preprocessing.
    """
    with Image.open(path) as img:
        return img.convert("RGB")
