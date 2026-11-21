import os
import shutil

import pytest
from core.tests.conftest import (  # noqa: F401
    django_db_setup,
    public_schema,
    tenant_schema,
)
from django.conf import settings

tenant_schema_name = getattr(settings, "TENANT_SCHEMA_NAME", "test_schema")


@pytest.fixture(autouse=True)
def cleanup_media():
    """
    Ensure files uploaded to storage during tests in the tenant schema are deleted after each test.
    """
    yield
    media_root = getattr(settings, "MEDIA_ROOT", None)
    if media_root:
        test_media_dir = os.path.join(media_root, tenant_schema_name)
        if os.path.exists(test_media_dir):
            shutil.rmtree(test_media_dir, ignore_errors=True)
