import json
import os
from typing import Dict

from src.config import Config

DEFAULT_LABELS = {
    "0": "ND",
    "1": "VMD",
    "2": "MID",
    "3": "MOD",
}


def get_class_map() -> Dict[str, str]:
    path = Config.CLASS_MAP_PATH

    if path and os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}

            if isinstance(data, list):
                return {str(i): str(v) for i, v in enumerate(data)}
        except Exception:
            pass

    return DEFAULT_LABELS