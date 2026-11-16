from django.conf import settings
from django.db import models

from core.utils.models import BaseModel
from overrides.storage import PrivateDocumentStorage


def document_upload_path(instance: "UploadedDocument", filename: str) -> str:
    return f"document-ocr/{instance.customer_id}/{instance.pk}.pdf"


class DocumentType(models.TextChoices):
    AADHAAR = "aadhaar", "Aadhaar"
    DRIVING_LICENSE = "driving_license", "Driving License"
    PUC = "puc", "PUC Certificate"
    INSURANCE = "insurance", "Vehicle Insurance"
    REGISTRATION_CERTIFICATE = "registration_certificate", "Registration Certificate"


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


class UploadedDocument(BaseModel):
    customer = models.ForeignKey(
        settings.CRM_CUSTOMER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_documents",
    )
    file = models.FileField(
        storage=PrivateDocumentStorage(),
        upload_to=document_upload_path,
    )
    document_type = models.CharField(
        max_length=32,
        choices=DocumentType.choices,
        blank=True,
        default="",
    )
    status = models.CharField(
        max_length=16,
        choices=DocumentProcessingStatus.choices,
        default=DocumentProcessingStatus.PENDING,
    )
    result = models.JSONField(default=dict, blank=True)
    error_code = models.CharField(
        max_length=32,
        choices=DocumentProcessingError.choices,
        blank=True,
        default="",
    )

    class Meta:
        ordering = ("-created", "-pk")

    def __str__(self) -> str:
        return f"Document {self.pk} ({self.status})"
