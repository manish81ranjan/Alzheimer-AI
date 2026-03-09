# # backend/src/middleware/__init__.py

# from .error_handler import register_error_handlers
# from .auth_middleware import admin_required, is_admin
# from .rate_limit import rate_limit

# __all__ = [
#     "register_error_handlers",
#     "admin_required",
#     "is_admin",
#     "rate_limit",
# ]


# backend/src/middleware/__init__.py
from .auth_middleware import admin_required
from .error_handler import register_error_handlers

__all__ = ["admin_required", "register_error_handlers"]
