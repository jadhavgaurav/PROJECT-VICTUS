"""
Authentication module for Project VICTUS
"""

from .routes import router
from .dependencies import get_current_user, get_optional_user
from .jwt import create_access_token, decode_access_token, verify_password, get_password_hash

__all__ = [
    "router",
    "get_current_user",
    "get_optional_user",
    "create_access_token",
    "decode_access_token",
    "verify_password",
    "get_password_hash",
]

