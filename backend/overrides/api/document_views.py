import logging

from core.utils.tasks import queue_task
from django.http import FileResponse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from overrides.api.serializers import UploadedDocumentSerializer
from overrides.models import (
    DocumentProcessingError,
    DocumentProcessingStatus,
    UploadedDocument,
)

LOGGER = logging.getLogger(__name__)


class DocumentQueueError(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Document processing could not be queued."
    default_code = "document_queue_failed"


class UploadedDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = UploadedDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ["get", "post"]

    def get_queryset(self):
        queryset = UploadedDocument.available_objects.select_related("customer")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(customer__user=self.request.user)

    @action(detail=True, methods=["get"], url_path="file", url_name="file")
    def download_file(self, request, *args, **kwargs):
        document = self.get_object()
        return FileResponse(
            document.file.open("rb"),
            as_attachment=True,
            filename=f"{document.pk}.pdf",
            content_type="application/pdf",
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()
        try:
            queue_task(
                task="overrides.tasks.process_uploaded_document",
                task_kwargs={"document_id": str(document.pk)},
                idempotency_key=str(document.pk),
            )
        except Exception as exc:
            UploadedDocument.available_objects.filter(pk=document.pk).update(
                status=DocumentProcessingStatus.FAILED,
                error_code=DocumentProcessingError.QUEUE_FAILED,
            )
            LOGGER.error(
                "Could not queue document OCR for %s (exception=%s)",
                document.pk,
                type(exc).__name__,
            )
            raise DocumentQueueError(
                detail={
                    "detail": "Document processing could not be queued.",
                    "document_id": str(document.pk),
                }
            ) from exc

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
