import os
from pathlib import Path

from core.config.settings.test import *  # noqa: F401

<<<<<<< HEAD
from config.settings.base import MIGRATION_MODULES  # noqa: F401
=======
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
>>>>>>> 1fa502b ( Fixed the api's for the Document Uploading and providing the sanitized output)

TENANT_SCHEMA_NAME = "test_core"
