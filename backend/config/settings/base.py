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

PROJECT_MIGRATION_PATH = "db_migrations"
MIGRATION_MODULES = {
    "configurations": f"{PROJECT_MIGRATION_PATH}.configurations",
    "crm": f"{PROJECT_MIGRATION_PATH}.crm",
    "integrations": f"{PROJECT_MIGRATION_PATH}.integrations",
    "integrations_email": f"{PROJECT_MIGRATION_PATH}.integrations_email",
    "integrations_sms": f"{PROJECT_MIGRATION_PATH}.integrations_sms",
    "invoices": f"{PROJECT_MIGRATION_PATH}.invoices",
    "tenants": f"{PROJECT_MIGRATION_PATH}.tenants",
    "users": f"{PROJECT_MIGRATION_PATH}.users",
}

if "overrides" not in INSTALLED_APPS:
    INSTALLED_APPS = [*INSTALLED_APPS, "overrides"]


if str(PROJECT_TEMPLATES_DIR) not in TEMPLATES[0]["DIRS"]:
    TEMPLATES[0]["DIRS"] = [str(PROJECT_TEMPLATES_DIR), *TEMPLATES[0]["DIRS"]]
if str(PROJECT_TEMPLATES_DIR) not in TEMPLATES[1]["DIRS"]:
    TEMPLATES[1]["DIRS"] = [str(PROJECT_TEMPLATES_DIR), *TEMPLATES[1]["DIRS"]]

if str(PROJECT_STATIC_DIR) not in STATICFILES_DIRS:
    STATICFILES_DIRS = [str(PROJECT_STATIC_DIR), *STATICFILES_DIRS]
