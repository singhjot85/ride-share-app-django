from pathlib import Path

from core.config.settings.base import *  # noqa: F401

# ------------------
#  Custom Settings
# ------------------
PROJECT_NAME = "rideshare"
PROJECT_LABEL = "Ride Share"

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Path to /backend
APP_DIR = os.path.join(BASE_DIR, APP_NAME)  # Path to /backend/apps
PROJECT_TEMPLATES_DIR = BASE_DIR / "templates"
PROJECT_STATIC_DIR = BASE_DIR / "static"
PROJECT_MEDIA_DIR = BASE_DIR / "media"
MEDIA_ROOT = str(PROJECT_MEDIA_DIR)
MEDIA_URL = "/media/"

# -------------------------------------------------------
#   Host Project Django Specifics
# -------------------------------------------------------
ROOT_URLCONF = "config.urls"
PUBLIC_SCHEMA_URLCONF = "config.public_urls"

MIGRATION_MODULES = {
    app.rsplit(".", 1)[-1]: f"db_migrations.{app.rsplit('.', 1)[-1]}"
    for app in PROJECT_APPS
}

if "overrides" not in INSTALLED_APPS:
    INSTALLED_APPS = [*INSTALLED_APPS, "overrides"]


if str(PROJECT_TEMPLATES_DIR) not in TEMPLATES[0]["DIRS"]:
    TEMPLATES[0]["DIRS"] = [str(PROJECT_TEMPLATES_DIR), *TEMPLATES[0]["DIRS"]]
if str(PROJECT_TEMPLATES_DIR) not in TEMPLATES[1]["DIRS"]:
    TEMPLATES[1]["DIRS"] = [str(PROJECT_TEMPLATES_DIR), *TEMPLATES[1]["DIRS"]]

if str(PROJECT_STATIC_DIR) not in STATICFILES_DIRS:
    STATICFILES_DIRS = [str(PROJECT_STATIC_DIR), *STATICFILES_DIRS]
