"""
Base model registry and app override mappings for the host application.
"""

from core.config.settings.base_models import *

# Host Application Model Settings
USERS_APP = "apps.users"
AUTH_USER_MODEL = "users.User"

# Global application override mapping
APP_OVERRIDE_MAP: dict[str, str] = {
    **globals().get("APP_OVERRIDE_MAP", {}),
    "users": USERS_APP,
}
