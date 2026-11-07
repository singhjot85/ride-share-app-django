"""
Production settings for the LoadShare host application.

Inherits base host settings and overrides storage with Cloudflare R2
from core.config.settings.production.
"""

from core.config.settings.production import (  # noqa: F401
    CLOUDFLARE_R2_ACCESS_KEY_ID,
    CLOUDFLARE_R2_ACCOUNT_ID,
    CLOUDFLARE_R2_BUCKET_NAME,
    CLOUDFLARE_R2_CUSTOM_DOMAIN,
    CLOUDFLARE_R2_ENDPOINT_URL,
    CLOUDFLARE_R2_SECRET_ACCESS_KEY,
    DEBUG,
    MEDIA_URL,
    STORAGES,
)

from config.settings.base import *  # noqa: F401
