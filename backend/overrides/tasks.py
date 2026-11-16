import logging

from celery import shared_task

from overrides.models import (
    DocumentProcessingError,
    DocumentProcessingStatus,
    UploadedDocument,
)
from overrides.services.doc_ocr import (
    InvalidDocumentError,
    process_pdf,
    sanitize_result,
)

LOGGER = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_uploaded_document(self, document_id: str) -> None:
    try:
        document = UploadedDocument.available_objects.get(pk=document_id)
    except UploadedDocument.DoesNotExist:
        LOGGER.error("OCR document record %s was not found", document_id)
        return

    if document.status == DocumentProcessingStatus.COMPLETED:
        return

    document.status = DocumentProcessingStatus.PROCESSING
    document.error_code = ""
    document.save(update_fields=["status", "error_code", "modified"])

    try:
        if document.file.size > 10 * 1024 * 1024:
            raise InvalidDocumentError("invalid_pdf")
        with document.file.open("rb") as source_file:
            pdf = source_file.read()
        result = process_pdf(pdf, doc_type=document.document_type or None)
    except InvalidDocumentError:
        document.status = DocumentProcessingStatus.FAILED
        document.error_code = DocumentProcessingError.INVALID_PDF
        document.save(update_fields=["status", "error_code", "modified"])
        return
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            document.status = DocumentProcessingStatus.FAILED
            document.error_code = DocumentProcessingError.PROCESSING_FAILED
            document.save(update_fields=["status", "error_code", "modified"])
            LOGGER.error(
                "OCR failed for document %s after retries (exception=%s)",
                document.pk,
                type(exc).__name__,
            )
        raise

    sanitized = sanitize_result(result)
    if "error_code" in sanitized:
        document.status = DocumentProcessingStatus.FAILED
        document.error_code = sanitized["error_code"]
        document.result = {}
    else:
        document.status = DocumentProcessingStatus.COMPLETED
        document.document_type = sanitized["document_type"]
        document.result = {
            "document_type": sanitized["document_type"],
            "confidence": sanitized["confidence"],
            "data": sanitized["data"],
        }
        document.error_code = ""
    document.save(
        update_fields=[
            "status",
            "document_type",
            "result",
            "error_code",
            "modified",
        ]
    )
