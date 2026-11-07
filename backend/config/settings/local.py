from core.config.settings.local import *  # noqa: F401

from config.settings.base import *  # noqa: F401

if DEBUG is True:
    ALLOWED_HOSTS = ["*"]

MEDIA_ROOT = str(PROJECT_MEDIA_DIR)
MEDIA_URL = "/media/"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
