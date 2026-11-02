from pathlib import Path

from core.config.settings.base import *  # noqa: F401

# -------------------------------------------------------
# Host Project Specifics
# -------------------------------------------------------
PROJECT_LABEL = "Load Share"
PROJECT_NAME = "load_share"
ROOT_URLCONF = "config.urls"
PUBLIC_SCHEMA_URLCONF = "config.public_urls"

PROJECT_MIGRATION_PATH = "db_migrations"
MIGRATION_MODULES = {
    app.rsplit(".", 1)[-1]: f"{PROJECT_MIGRATION_PATH}.{app.rsplit('.', 1)[-1]}"
    for app in PROJECT_APPS
}

if "overrides" not in INSTALLED_APPS:
    INSTALLED_APPS = [*INSTALLED_APPS, "overrides"]

# -------------------------------------------------------
# Host Project Templates & Static Assets
# -------------------------------------------------------
PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_TEMPLATES_DIR = PROJECT_DIR / "templates"
PROJECT_STATIC_DIR = PROJECT_DIR / "static"

if str(PROJECT_TEMPLATES_DIR) not in TEMPLATES[0]["DIRS"]:
    TEMPLATES[0]["DIRS"] = [str(PROJECT_TEMPLATES_DIR), *TEMPLATES[0]["DIRS"]]
if str(PROJECT_TEMPLATES_DIR) not in TEMPLATES[1]["DIRS"]:
    TEMPLATES[1]["DIRS"] = [str(PROJECT_TEMPLATES_DIR), *TEMPLATES[1]["DIRS"]]

if str(PROJECT_STATIC_DIR) not in STATICFILES_DIRS:
    STATICFILES_DIRS = [str(PROJECT_STATIC_DIR), *STATICFILES_DIRS]
