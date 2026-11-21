"""
Document processing Celery tasks for LoadShare.

NOTE: Kept temporarily in overrides.services/tasks until service redesign and
migration to core (CRM CustomerIdentification) is completed.

TODO (Celery Beat Cron Migration): This task should NOT be manually triggered
via queue_task upon file upload. Once Celery Beat is implemented, document
scanning will be executed periodically by Beat at its configured cron schedule
to batch-process unverified identifications.
"""

import logging

from celery import shared_task
from django.db import models

LOGGER = logging.getLogger(__name__)


class DocumentProcessingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class DocumentProcessingError(models.TextChoices):
    NO_TEXT = "no_text", "No text could be extracted"
    UNKNOWN_DOCUMENT_TYPE = "unknown_document_type", "Unknown document type"
    INVALID_PDF = "invalid_pdf", "Invalid or unsupported PDF"
    PROCESSING_FAILED = "processing_failed", "Document processing failed"
    QUEUE_FAILED = "queue_failed", "OCR task could not be queued"


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_uploaded_document(self, document_id: str) -> None:
    """
    Temporary placeholder task for document OCR processing.

    To be redesigned and migrated to core.apps.crm for CustomerIdentification records.
    """
    LOGGER.info(
        "Document processing task invoked for document %s (migration to core pending)",
        document_id,
    )
