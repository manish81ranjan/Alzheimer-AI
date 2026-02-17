# backend/src/utils/file_utils.py
"""
File & path helpers.
Used for uploads, reports, heatmaps, etc.
"""

from pathlib import Path
from werkzeug.utils import secure_filename


def safe_filename(filename: str) -> str:
    """
    Normalize filename to a safe value.
    """
    return secure_filename(filename or "")


def ensure_dir(path: Path) -> Path:
    """
    Ensure directory exists and return it.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def file_size_ok(file_obj, max_bytes: int) -> bool:
    """
    Check file size without reading entire file into memory.
    """
    try:
        pos = file_obj.stream.tell()
        file_obj.stream.seek(0, 2)  # end
        size = file_obj.stream.tell()
        file_obj.stream.seek(pos)
        return size <= max_bytes
    except Exception:
        # If size can't be determined, allow (or choose to deny)
        return True


def build_static_url(static_subdir: str, filename: str) -> str:
    """
    Build a public URL under /static.
    Example:
      build_static_url("uploads", "x.png") -> /static/uploads/x.png
    """
    return f"/static/{static_subdir.strip('/')}/{filename}"
