from unittest.mock import patch

import pymupdf
import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from core.apps.crm import get_customer_identification_model, get_customer_model
from overrides.models import DocumentProcessingStatus, UploadedDocument
from overrides.services.doc_ocr import (
    InvalidDocumentError,
    process_pdf,
    sanitize_result,
    validate_pdf,
)

Customer = get_customer_model()
CustomerIdentification = get_customer_identification_model()
User = get_user_model()


@pytest.fixture
def private_document_storage(tmp_path):
    with override_settings(PRIVATE_DOCUMENT_ROOT=tmp_path):
        yield tmp_path


@pytest.fixture
def owner(db):
    user = User.objects.create_user(username="document-owner", password="test-pass")
    return Customer.available_objects.create(first_name="Owner", user=user)


def make_pdf(text="Driving Licence"):
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


def upload_file(content=None, name="document.pdf"):
    return SimpleUploadedFile(
        name,
        content or make_pdf(),
        content_type="application/pdf",
    )


def test_sanitized_result_masks_identifiers_and_omits_personal_fields():
    result = sanitize_result(
        {
            "status": "ok",
            "document_type": "insurance",
            "confidence": 0.8,
            "data": {
                "policy_number": "POLICY12345",
                "vehicle_number": "MH12AB1234",
                "chassis_number": "CHASSIS123456789",
                "engine_number": "ENGINE123456",
                "insured_name": "A Person",
                "address": "A Private Address",
                "valid_to": "2030-01-01",
            },
            "raw_text": "private text",
        }
    )

    assert result["data"]["policy_number"] == "XXXXXXX2345"
    assert result["data"]["vehicle_number"] == "XXXXXX1234"
    assert result["data"]["chassis_number"] == "XXXXXXXXXXXX6789"
    assert result["data"]["engine_number"] == "XXXXXXXX3456"
    assert result["data"]["valid_to"] == "2030-01-01"
    assert "insured_name" not in result["data"]
    assert "address" not in result["data"]
    assert "raw_text" not in result


def test_sanitized_result_reduces_date_of_birth_to_year():
    result = sanitize_result(
        {
            "status": "ok",
            "document_type": "driving_license",
            "confidence": 0.5,
            "data": {"dob": "1980-04-03", "name": "A Person"},
        }
    )

    assert result["data"]["dob"] == 1980
    assert "name" not in result["data"]


def test_process_pdf_extracts_text_layer_without_returning_raw_text():
    pdf = make_pdf(
        "Driving Licence\nName: A Person\nDL No: MH12 2010 1234567\n"
        "Date of Issue: 01/01/2020"
    )

    result = process_pdf(pdf)
    sanitized = sanitize_result(result)

    assert result["document_type"] == "driving_license"
    assert "raw_text" not in result
    assert sanitized["data"]["license_number"].endswith("4567")
    assert sanitized["data"]["date_of_issue"] == "2020-01-01"
    assert "name" not in sanitized["data"]


def test_process_pdf_uses_ocr_when_pdf_has_no_text_layer():
    document = pymupdf.open()
    document.new_page()
    pdf = document.tobytes()
    document.close()

    with patch(
        "overrides.services.doc_ocr.pytesseract.image_to_string",
        return_value="Driving Licence\nDL No: MH12 2010 1234567",
    ) as image_to_string:
        result = process_pdf(pdf)

    image_to_string.assert_called_once()
    assert image_to_string.call_args.kwargs["lang"] == "eng+hin"
    assert result["document_type"] == "driving_license"
    assert result["data"]["license_number"].endswith("4567")


def test_validate_pdf_rejects_non_pdf_and_too_many_pages():
    with pytest.raises(InvalidDocumentError):
        validate_pdf(b"not a pdf")

    document = pymupdf.open()
    for _ in range(11):
        document.new_page()
    content = document.tobytes()
    document.close()

    with pytest.raises(InvalidDocumentError):
        validate_pdf(content)


def test_upload_queues_ocr_and_returns_accepted_status(owner, private_document_storage):
    client = APIClient()
    client.force_authenticate(owner.user)
    upload_url = reverse("document-upload-list")

    with patch("overrides.api.document_views.queue_task") as queue_task:
        response = client.post(
            upload_url,
            {
                "customer": str(owner.pk),
                "document_type": "driving_license",
                "source_file": upload_file(),
            },
            format="multipart",
        )

    assert response.status_code == 202
    assert response.data["status"] == DocumentProcessingStatus.PENDING
    assert "source_file" not in response.data
    queue_task.assert_called_once()
    assert queue_task.call_args.kwargs["task_kwargs"] == {
        "document_id": str(response.data["id"])
    }


def test_queue_failure_is_visible_as_service_unavailable_and_failed_record(
    owner, private_document_storage
):
    client = APIClient()
    client.force_authenticate(owner.user)

    with patch(
        "overrides.api.document_views.queue_task",
        side_effect=RuntimeError("broker unavailable"),
    ):
        response = client.post(
            reverse("document-upload-list"),
            {
                "customer": str(owner.pk),
                "source_file": upload_file(),
            },
            format="multipart",
        )

    assert response.status_code == 503
    document = UploadedDocument.available_objects.get(
        pk=response.data["document_id"]
    )
    assert document.status == DocumentProcessingStatus.FAILED
    assert document.error_code == "queue_failed"


def test_upload_rejects_customer_owned_by_another_user(owner, private_document_storage):
    other_user = User.objects.create_user(
        username="other-document-owner", password="test-pass"
    )
    other_customer = Customer.available_objects.create(
        first_name="Other", user=other_user
    )
    client = APIClient()
    client.force_authenticate(owner.user)

    response = client.post(
        reverse("document-upload-list"),
        {
            "customer": str(other_customer.pk),
            "source_file": upload_file(),
        },
        format="multipart",
    )

    assert response.status_code == 400
    assert "customer" in response.data


def test_document_list_includes_only_the_authenticated_users_documents(
    owner, private_document_storage
):
    own_document = UploadedDocument.objects.create(
        customer=owner,
        file=upload_file(),
    )
    other_user = User.objects.create_user(
        username="other-list-owner", password="test-password"
    )
    other_customer = Customer.available_objects.create(
        first_name="Other", user=other_user
    )
    UploadedDocument.objects.create(customer=other_customer, file=upload_file())

    client = APIClient()
    client.force_authenticate(owner.user)
    response = client.get(reverse("document-upload-list"))

    assert response.status_code == 200
    assert [item["id"] for item in response.data] == [str(own_document.pk)]
    assert "source_file" not in response.data[0]


def test_crm_identification_list_is_scoped_to_authenticated_users_customers(owner):
    own_identification = CustomerIdentification.objects.create(
        customer=owner,
        identity_type="driving_license",
        identity_number="DL-OWNER-1234",
    )
    other_user = User.objects.create_user(
        username="other-identification-owner", password="test-password"
    )
    other_customer = Customer.available_objects.create(
        first_name="Other", user=other_user
    )
    CustomerIdentification.objects.create(
        customer=other_customer,
        identity_type="aadhaar",
        identity_number="OTHER-IDENTIFICATION",
    )

    client = APIClient()
    client.force_authenticate(owner.user)
    response = client.get("/api/crm/v1/customer-identifications/")

    assert response.status_code == 200
    assert [item["id"] for item in response.data] == [str(own_identification.pk)]
    assert response.data[0]["identity_number"] == "DL-OWNER-1234"


def test_crm_identification_list_requires_authentication():
    response = APIClient().get("/api/crm/v1/customer-identifications/")

    assert response.status_code in (401, 403)


def test_document_result_is_only_visible_to_owning_customer(
    owner, private_document_storage
):
    document = UploadedDocument.objects.create(
        customer=owner,
        file=upload_file(),
        status=DocumentProcessingStatus.COMPLETED,
        result={"document_type": "aadhaar", "data": {"aadhaar_number": "XXXXXXXX1234"}},
    )
    other_user = User.objects.create_user(
        username="unrelated-document-owner", password="test-pass"
    )
    client = APIClient()
    client.force_authenticate(other_user)

    response = client.get(reverse("document-upload-detail", args=[document.pk]))

    assert response.status_code == 404


def test_original_pdf_is_downloadable_only_by_its_owner(owner, private_document_storage):
    document = UploadedDocument.objects.create(customer=owner, file=upload_file())
    owner_client = APIClient()
    owner_client.force_authenticate(owner.user)

    response = owner_client.get(
        reverse("document-upload-file", args=[document.pk])
    )

    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert b"%PDF-" in b"".join(response.streaming_content)

    other_user = User.objects.create_user(
        username="other-file-owner", password="test-pass"
    )
    other_client = APIClient()
    other_client.force_authenticate(other_user)
    forbidden_response = other_client.get(
        reverse("document-upload-file", args=[document.pk])
    )

    assert forbidden_response.status_code == 404


def test_processing_task_persists_only_sanitized_result(owner, private_document_storage):
    document = UploadedDocument.objects.create(
        customer=owner,
        file=upload_file(),
        document_type="driving_license",
    )
    ocr_result = {
        "status": "ok",
        "document_type": "driving_license",
        "confidence": 0.75,
        "data": {
            "license_number": "XXXXXXXXXXXX1234",
            "name": "A Person",
            "guardian_name": "Another Person",
            "dob": "1980-04-03",
            "address": "Private address",
            "pin_code": "400001",
            "date_of_issue": "2020-01-01",
        },
        "raw_text": "private OCR text",
    }

    with patch("overrides.tasks.process_pdf", return_value=ocr_result):
        from overrides.tasks import process_uploaded_document

        process_uploaded_document.run(str(document.pk))

    document.refresh_from_db()
    assert document.status == DocumentProcessingStatus.COMPLETED
    assert document.result["data"]["license_number"].endswith("1234")
    assert document.result["data"]["dob"] == 1980
    assert document.result["data"]["date_of_issue"] == "2020-01-01"
    assert "name" not in document.result["data"]
    assert "address" not in document.result["data"]
    assert "pin_code" not in document.result["data"]
    assert "raw_text" not in document.result
