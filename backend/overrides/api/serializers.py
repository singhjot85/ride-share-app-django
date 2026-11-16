from rest_framework import serializers

from core.apps.crm import get_customer_model
from overrides.models import UploadedDocument
from overrides.services.doc_ocr import (
    MAX_DOCUMENT_SIZE,
    InvalidDocumentError,
    validate_pdf,
)

Customer = get_customer_model()


class UploadedDocumentSerializer(serializers.ModelSerializer):
    source_file = serializers.FileField(write_only=True)

    class Meta:
        model = UploadedDocument
        fields = (
            "id",
            "customer",
            "source_file",
            "document_type",
            "status",
            "result",
            "error_code",
            "created",
            "modified",
        )
        read_only_fields = ("id", "status", "result", "error_code", "created", "modified")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated and not request.user.is_staff:
            self.fields["customer"].queryset = Customer.available_objects.filter(
                user=request.user
            )
        else:
            self.fields["customer"].queryset = Customer.available_objects.all()

    def validate_source_file(self, source_file):
        if source_file.size > MAX_DOCUMENT_SIZE:
            raise serializers.ValidationError(
                "The PDF must be no larger than 10 MB."
            )
        try:
            validate_pdf(source_file.read())
        except InvalidDocumentError as exc:
            raise serializers.ValidationError(
                "Upload a valid, unencrypted PDF with no more than 10 pages."
            ) from exc
        finally:
            source_file.seek(0)
        return source_file

    def create(self, validated_data):
        source_file = validated_data.pop("source_file")
        return UploadedDocument.objects.create(file=source_file, **validated_data)
