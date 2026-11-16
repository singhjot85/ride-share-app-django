# Document Upload and OCR API

This API lets an authenticated mobile client upload a customer document PDF, check asynchronous OCR status, and retrieve sanitized extracted fields.

## Base URL and authentication

Prefix every path with the API host for the selected environment. For local development, the host may be `http://localhost:8000`.

All endpoints require authentication. Mobile clients should send the JWT access token:

```http
Authorization: Bearer <access_token>
```

Use the trailing slash on every endpoint. Some mobile HTTP clients do not replay multipart requests after a slash-redirect.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/overrides/v1/document-uploads/` | Upload one PDF. Returns `202 Accepted` and a document record. |
| `GET` | `/api/overrides/v1/document-uploads/` | List the signed-in user's documents. Staff can list all documents. |
| `GET` | `/api/overrides/v1/document-uploads/{id}/` | Read a document's processing status and sanitized result. |
| `GET` | `/api/overrides/v1/document-uploads/{id}/file/` | Download the original PDF as `application/pdf`. |

Non-staff users can only upload for, list, and retrieve documents associated with CRM customers linked to their account. The customer UUID and uploaded document ID are different IDs. Requests for another user's document return `404`.

## Upload a document

### Request

Send `multipart/form-data`:

| Field | Type | Required | Values / constraints |
|---|---|---:|---|
| `customer` | string | Yes | UUID of a CRM customer linked to the signed-in account. |
| `source_file` | file | Yes | PDF only; maximum 10 MB and 10 pages. Encrypted PDFs are rejected. |
| `document_type` | string | No | `aadhaar`, `driving_license`, `puc`, `insurance`, or `registration_certificate`. Omit or send empty to classify automatically. |

Example:

```bash
curl --request POST \
  'http://localhost:8000/api/overrides/v1/document-uploads/' \
  --header 'Authorization: Bearer <access_token>' \
  --form 'customer=<crm_customer_uuid>' \
  --form 'document_type=driving_license' \
  --form 'source_file=@driving_licence.pdf;type=application/pdf'
```

For mobile clients, let the HTTP library generate the multipart boundary; do not set `Content-Type: multipart/form-data` manually.

### Successful response

HTTP `202 Accepted` means the file was accepted and OCR has been queued. Save the returned `id` and use it to poll the detail endpoint.

```json
{
  "id": "11111111-1111-4111-8111-111111111111",
  "customer": "22222222-2222-4222-8222-222222222222",
  "document_type": "driving_license",
  "status": "pending",
  "result": {},
  "error_code": "",
  "created": "2026-01-15T10:00:00Z",
  "modified": "2026-01-15T10:00:00Z"
}
```

`source_file` is write-only and is never included in the JSON response.

## Check processing status

Poll `GET /api/overrides/v1/document-uploads/{id}/` every few seconds until the status is terminal (`completed` or `failed`). There is no fixed processing-time guarantee.

### In progress

The status is initially `pending`, then may become `processing`. `result` remains empty until the task finishes.

```json
{
  "id": "11111111-1111-4111-8111-111111111111",
  "customer": "22222222-2222-4222-8222-222222222222",
  "document_type": "driving_license",
  "status": "processing",
  "result": {},
  "error_code": "",
  "created": "2026-01-15T10:00:00Z",
  "modified": "2026-01-15T10:00:01Z"
}
```

### OCR completed

When `status` is `completed`, `result` contains the detected/provided type, a confidence heuristic, and the sanitized data.

```json
{
  "id": "11111111-1111-4111-8111-111111111111",
  "customer": "22222222-2222-4222-8222-222222222222",
  "document_type": "driving_license",
  "status": "completed",
  "result": {
    "document_type": "driving_license",
    "confidence": 0.75,
    "data": {
      "license_number": "XXXXXXXXXXXX2345",
      "dob": 2003,
      "date_of_issue": "2021-06-15",
      "valid_upto_non_transport": "2041-06-14",
      "valid_upto_transport": "2024-06-14",
      "vehicle_classes": ["LMV", "MCWG"],
      "state_code": "PB"
    }
  },
  "error_code": "",
  "created": "2026-01-15T10:00:00Z",
  "modified": "2026-01-15T10:00:03Z"
}
```

`result.data` fields vary by `document_type`. These are the fields currently returned; a value may be `null` if it was not extracted.

| `document_type` | `result.data` fields |
|---|---|
| `aadhaar` | `aadhaar_number`, `aadhaar_checksum_valid`, `year_of_birth` |
| `driving_license` | `license_number`, `dob` (year), `date_of_issue`, `valid_upto_non_transport`, `valid_upto_transport`, `vehicle_classes`, `state_code` |
| `puc` | `vehicle_number`, `certificate_number`, `test_date`, `valid_upto`, `fuel_type`, `co_percent`, `hc_ppm`, `smoke_density`, `result` |
| `insurance` | `policy_number`, `insurer`, `policy_type`, `vehicle_number`, `chassis_number`, `engine_number`, `valid_from`, `valid_to`, `idv`, `total_premium` |
| `registration_certificate` | `registration_number`, `date_of_registration`, `registration_valid_upto`, `vehicle_class`, `maker`, `model`, `fuel_type`, `colour`, `manufacture_date`, `chassis_number`, `engine_number` |

Date fields are ISO `YYYY-MM-DD` unless noted; `manufacture_date` may be `MM/YYYY`. `dob` and `year_of_birth` are integer years. `confidence` is the fraction of parser fields populated, not a statistical OCR confidence score.

Names, addresses, and raw OCR text are not returned. Aadhaar, license, policy, vehicle, certificate, chassis, and engine identifiers are masked.

### OCR failed

When `status` is `failed`, inspect `error_code`; `result` is empty.

| `error_code` | Meaning |
|---|---|
| `no_text` | No usable text could be extracted. |
| `unknown_document_type` | The document type could not be identified. |
| `invalid_pdf` | The uploaded PDF is invalid or unsupported. |
| `processing_failed` | OCR processing failed after retries. |
| `queue_failed` | The task could not be queued. |

## List uploaded documents

`GET /api/overrides/v1/document-uploads/` returns a JSON array, not a paginated object. Each array item has the same fields as the detail response. The list is limited to documents for customers linked to the signed-in user (staff can list all).

## Download the original PDF

`GET /api/overrides/v1/document-uploads/{id}/file/` returns the original PDF bytes with content type `application/pdf`. Only the owning user or staff can download it. This endpoint does not return JSON.

## HTTP errors

| HTTP status | Meaning |
|---:|---|
| `400 Bad Request` | Required field missing/invalid, customer not linked to the user, unsupported/encrypted PDF, file over 10 MB, or more than 10 pages. The response includes field-level JSON errors. |
| `401 Unauthorized` | Missing or invalid authentication. |
| `404 Not Found` | Document does not exist or is not visible to this account. |
| `503 Service Unavailable` | File was saved but the OCR task could not be queued. The response includes the created `document_id`; that record is marked failed. |

Example `503` response:

```json
{
  "detail": "Document processing could not be queued.",
  "document_id": "11111111-1111-4111-8111-111111111111"
}
```

## Storage and privacy

Files are stored privately and are not exposed through public media URLs. They are retained for authorized review. Configure `PRIVATE_DOCUMENT_ROOT` to a persistent private volume in production. OCR runs asynchronously in a Celery worker using local Tesseract with English and Hindi language data.
