import os
from pathlib import Path

from core.config.settings.base import *  # noqa: F401
from core.libraries.app_resolver import resolve_apps

from .base_models import *  # noqa: F401, F403

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

# Resolve installed, shared, and tenant apps using the core app resolver
RESOLVED_APPS = resolve_apps(
    project_apps=[*PROJECT_APPS, "overrides"],
    public_apps=DJANGO_TENANT_PUBLIC_APPS,
    tenant_apps=DJANGO_TENANT_PRIVATE_APPS,
    override_map=APP_OVERRIDE_MAP,
)

INSTALLED_APPS = RESOLVED_APPS.installed_apps
SHARED_APPS = RESOLVED_APPS.shared_apps
TENANT_APPS = RESOLVED_APPS.tenant_apps
DJANGO_TENANT_PUBLIC_APPS = SHARED_APPS
DJANGO_TENANT_PRIVATE_APPS = TENANT_APPS

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

# -------------------------------------------------------
# Host Project Templates & Static Assets
# -------------------------------------------------------
PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
PRIVATE_DOCUMENT_ROOT = Path(
    os.getenv("PRIVATE_DOCUMENT_ROOT", str(PROJECT_DIR / "private_documents"))
)

if str(PROJECT_TEMPLATES_DIR) not in TEMPLATES[0]["DIRS"]:
    TEMPLATES[0]["DIRS"] = [str(PROJECT_TEMPLATES_DIR), *TEMPLATES[0]["DIRS"]]
if str(PROJECT_TEMPLATES_DIR) not in TEMPLATES[1]["DIRS"]:
    TEMPLATES[1]["DIRS"] = [str(PROJECT_TEMPLATES_DIR), *TEMPLATES[1]["DIRS"]]

if str(PROJECT_STATIC_DIR) not in STATICFILES_DIRS:
    STATICFILES_DIRS = [str(PROJECT_STATIC_DIR), *STATICFILES_DIRS]
