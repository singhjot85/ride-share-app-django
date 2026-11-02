from config.settings.base import *  # noqa: F401

if DEBUG is True:
    ALLOWED_HOSTS = ["*"]
