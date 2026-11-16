import os
from pathlib import Path

from core.config.settings.test import *  # noqa: F401

from config.settings.base import MIGRATION_MODULES  # noqa: F401

TENANT_SCHEMA_NAME = "test_core"
ROOT_URLCONF = "config.urls"

if "overrides" not in PROJECT_APPS:
    PROJECT_APPS = [*PROJECT_APPS, "overrides"]
if "overrides" not in INSTALLED_APPS:
    INSTALLED_APPS = [*INSTALLED_APPS, "overrides"]

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
PRIVATE_DOCUMENT_ROOT = Path(
    os.getenv("PRIVATE_DOCUMENT_ROOT", str(PROJECT_DIR / "private_documents"))
)

PROJECT_MIGRATION_PATH = "backend.db_migrations"
MIGRATION_MODULES = {
    app.rsplit(".", 1)[-1]: f"{PROJECT_MIGRATION_PATH}.{app.rsplit('.', 1)[-1]}"
    for app in PROJECT_APPS
}
