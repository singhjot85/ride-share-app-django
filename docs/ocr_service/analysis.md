# Phase 1 Analysis: Core Document OCR Service & CRM Integration

> **Feature:** Modular Document OCR Service & CRM CustomerIdentification Verification
> **Target Submodule:** `core-common-django-apps` (`core.apps.crm`)
> **Status:** Phase 1 (Approved by User via Roadmap) → Entering Phase 2 (Implementation)

---

## 1. Feature Purpose & Domain Scope

Migrate the OCR document processing engine from `backend/overrides/services/doc_ocr.py` into the `core-common-django-apps` submodule under `core.apps.crm`. The service extracts, validates, and classifies Indian KYC identity and vehicle documents (Aadhaar, Driving License, RC, PUC, Insurance) and binds cleanly to `CustomerIdentification`.

### Requirements & Scope Boundaries
- **In Scope**:
  1. Modularizing `doc_ocr.py` into `core.apps.crm.services.ocr`:
     - `validators.py`: Verhoeff checksum algorithm, Indian vehicle registration regexes, date normalizers.
     - `engine.py`: PDF validation (header, <=10 pages, <=10 MB, unencrypted), image rendering, Tesseract OCR invocation.
     - `parsers/`: Document-specific parsing for `aadhaar`, `driving_license`, `registration_certificate`, `puc`, `insurance`.
     - `sanitizer.py`: PII masking (masking UIDAI numbers, chassis tail, DL numbers).
     - `classifier.py`: Heuristic keyword weight auto-classification.
  2. Serializer & ViewSet file upload:
     - `CustomerIdentificationSerializer` accepts `document` (FileField) with PDF size/page validation.
     - `CustomerIdentificationViewSet` accepts `MultiPartParser` and `FormParser`.
     - Detail download action `download_file` to stream document securely.
  3. Celery background processing:
     - Celery Beat cron scheduled batch task: `process_unverified_identifications_cron` (queries `CustomerIdentification` records where `status = IdentityStatusChoices.PENDING` or `UNVERIFIED`).
     - Standalone processing helper `process_identification_record(identification: CustomerIdentification)`.
  4. Core unit test suite in `core/tests/crm/test_ocr.py` and `test_views.py`.
  5. Host project cleanup: removing temporary stubs from `overrides/`.
- **Out of Scope**:
  - Live third-party KYC aggregators (DigiLocker, Karza, Cashfree).
  - Escrow or payment processing.

---

## 2. Input / Output Contracts

### 2.1 File Upload Contract (`CustomerIdentificationSerializer`)
- **HTTP Method**: `POST` or `PUT` / `PATCH` to `/api/crm/v1/customers/{customer_pk}/identifications/`
- **Content-Type**: `multipart/form-data`
- **Request Fields**:
  - `type` (str, required): One of `IdentityTypeChoices` (`aadhaar`, `driving_license`, `registration_certificate`, `puc`, `insurance`, `pan`, `passport`, `voter_id`).
  - `document` (file, optional on update, required on upload): PDF file, <= 10 MB, <= 10 pages, unencrypted.
- **Initial State on Save**:
  - `status = IdentityStatusChoices.PENDING.value` (or `UNVERIFIED`).
  - `is_verified = False`
  - `verified_on = None`

### 2.2 Celery Beat Cron Batch Processing Contract
- **Task**: `core.apps.crm.tasks.process_unverified_identifications_cron`
- **Schedule**: Celery Beat cron (periodic).
- **Execution**:
  - Fetches batch of `CustomerIdentification.available_objects.filter(status=IdentityStatusChoices.PENDING, document__isnull=False)`.
  - For each identification:
    - Reads PDF bytes.
    - Runs `process_document(file_bytes, doc_type=instance.type)`.
    - If valid:
      - `status = IdentityStatusChoices.VERIFIED.value`
      - `is_verified = True`
      - `verified_on = timezone.now().date()`
      - `details = sanitized_result["data"]`
    - If invalid or OCR failed:
      - `status = IdentityStatusChoices.REJECTED.value`
      - `is_verified = False`
      - `details = {"error": sanitized_result.get("error_code")}`

---

## 3. Database & Query Discipline

- **N+1 Prevention**: Identification queries use `select_related("customer")`.
- **Soft Delete Awareness**: Query via `CustomerIdentification.available_objects` exclusively.
- **Atomic State Updates**: State transitions update specific fields: `instance.save(update_fields=["status", "is_verified", "verified_on", "details", "modified"])`.

---

## 4. Error Handling & Security

- **PDF Bomb Protection**: File size checked before reading; page count verified before rendering images.
- **PII Protection**: Full Aadhaar / DL numbers are NEVER written to logs or raw JSON fields; masked via `sanitizer.py`.
- **Dependency Fallback**: If `pytesseract` or `pymupdf` is missing in an environment without OCR extras, gracefully log a warning and mark status without crashing the process.
