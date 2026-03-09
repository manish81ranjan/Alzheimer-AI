# backend/src/utils/validators.py
"""
Request & data validation helpers.
Keep routes/services clean by validating inputs here.
"""

import re
from typing import Iterable

# -------------------- Email --------------------
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def is_valid_email(email: str) -> bool:
    if not isinstance(email, str):
        return False
    return bool(_EMAIL_RE.match(email.strip()))


# -------------------- Password --------------------
def is_strong_password(password: str, min_len: int = 6) -> bool:
    """
    Basic password check (length only).
    You can extend with digits/symbols later.
    """
    if not isinstance(password, str):
        return False
    return len(password) >= min_len


# -------------------- Files --------------------
def allowed_extension(filename: str, allowed: Iterable[str]) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in set(a.lower() for a in allowed)


# -------------------- Pagination --------------------
def clamp_int(value, default: int, min_v: int, max_v: int) -> int:
    try:
        v = int(value)
    except Exception:
        return default
    return max(min_v, min(max_v, v))
