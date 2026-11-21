# Document OCR Service

Agent context and architecture documentation for the KYC and vehicle document OCR service migrated to `core.apps.crm`.

## Overview

The document OCR service parses uploaded identification PDFs (Aadhaar, Driving License, Registration Certificate, PUC, and Insurance) to extract metadata, perform checksum verification, mask sensitive PII, and mark KYC records as verified.

## Architectural Guidelines & Celery Beat Scheduling

> **TODO:** Document scanning is designed as a **Celery Beat cron-scheduled batch task** (`process_unverified_identifications_cron`), **not** a per-upload manual trigger.
> Once Celery Beat is configured and active in the host environment, background processing of pending records will run periodically at its configured cron schedule (e.g., every 5 minutes), instead of invoking a manual `queue_task` on every upload.

## Component Layout in Core Submodule

- Package: `backend/core-common-django-apps/core/apps/crm/services/ocr/`
  - `engine.py`: Text extraction (PyMuPDF digital text first, Tesseract OCR fallback at 300 DPI).
  - `classifier.py`: Heuristic keyword classification when document type is ambiguous.
  - `validators.py`: Checksum validation (Verhoeff for Aadhaar, regex patterns for RC/DL/Dates).
  - `sanitizer.py`: Text normalization and PII masking (`XXXXXXXX<last4>`).
  - `parsers/`: Parsers for `aadhaar`, `license`, `puc`, `insurance`, and `rc`.
- Tasks: `backend/core-common-django-apps/core/apps/crm/tasks.py`
  - `process_unverified_identifications_cron`: Celery Beat batch processor.
  - `process_customer_identification_ocr`: Task for individual record processing.
- Serializers & Views: `backend/core-common-django-apps/core/apps/crm/api/`
  - `CustomerIdentificationSerializer`: Enforces <= 10MB PDF uploads and sets status to `pending`.
  - `CustomerIdentificationViewSet`: Supports multipart uploads and raw file streaming via `download/`.

## Associated Documents

- [roadmap.md](file:///Users/gurjotsingh/Documents/ride-share-app-django/docs/ocr_service/roadmap.md): Complete phase-by-phase implementation and verification roadmap.
- [core-migration-ocr-service.md](file:///Users/gurjotsingh/Documents/ride-share-app-django/docs/ocr_service/core-migration-ocr-service.md): Architectural spec and schema mapping for moving from host overrides to core.
- [analysis.md](file:///Users/gurjotsingh/Documents/ride-share-app-django/docs/ocr_service/analysis.md): Four-phase lifecycle analysis for the OCR migration.
