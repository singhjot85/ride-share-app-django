import io
import os
import re
from datetime import datetime
from typing import Any

import pymupdf
import pytesseract
from PIL import Image

if os.getenv("TESSERACT_CMD"):
    pytesseract.pytesseract.tesseract_cmd = os.environ["TESSERACT_CMD"]

MAX_DOCUMENT_SIZE = 10 * 1024 * 1024
MAX_DOCUMENT_PAGES = 10
MIN_TEXT_CHARS = 40


class InvalidDocumentError(ValueError):
    """Raised when an uploaded file is not a supported PDF."""


def validate_pdf(pdf: bytes) -> None:
    if not pdf.startswith(b"%PDF-"):
        raise InvalidDocumentError("invalid_pdf")

    try:
        document = pymupdf.open(stream=pdf, filetype="pdf")
    except (pymupdf.FileDataError, pymupdf.EmptyFileError, ValueError) as exc:
        raise InvalidDocumentError("invalid_pdf") from exc

    try:
        if document.is_encrypted or not 1 <= document.page_count <= MAX_DOCUMENT_PAGES:
            raise InvalidDocumentError("invalid_pdf")
    finally:
        document.close()


def extract_text(pdf: bytes, dpi: int = 300, lang: str = "eng+hin") -> str:
    pages = []
    with pymupdf.open(stream=pdf, filetype="pdf") as document:
        for page in document:
            text = page.get_text("text").strip()
            if len(text) < MIN_TEXT_CHARS:
                pixmap = page.get_pixmap(dpi=dpi)
                image = Image.open(io.BytesIO(pixmap.tobytes("png"))).convert("L")
                try:
                    text = pytesseract.image_to_string(
                        image, lang=lang, config="--psm 6"
                    )
                except pytesseract.TesseractError:
                    text = pytesseract.image_to_string(
                        image, lang="eng", config="--psm 6"
                    )
            pages.append(text)
    return "\n".join(pages)


def clean_text(text: str) -> str:
    text = text.replace("\u00a0", " ").replace("|", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


_MONTHS = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()
_DATE_RE = re.compile(r"\b(\d{1,2})[\s/\-.](\d{1,2}|[A-Za-z]{3})[\s/\-.](\d{4})\b")


def norm_date(raw: str | None) -> str | None:
    if not raw:
        return None
    match = _DATE_RE.search(raw)
    if not match:
        return None
    day, month, year = match.groups()
    try:
        month_number = (
            int(month) if month.isdigit() else _MONTHS.index(month.upper()) + 1
        )
        return datetime(int(year), month_number, int(day)).date().isoformat()
    except ValueError:
        return None


def find_dates(text: str) -> list[str]:
    return [
        date
        for date in (norm_date(match.group(0)) for match in _DATE_RE.finditer(text))
        if date
    ]


def after_label(text: str, labels: list[str]) -> str | None:
    for label in labels:
        match = re.search(rf"{label}\s*[:\-.]?\s*([^\n]+)", text, re.I)
        if match:
            value = match.group(1).strip(" :-.")
            if value:
                return value
    return None


def clean_name(value: str | None) -> str | None:
    if not value:
        return None
    value = re.sub(r"[^A-Za-z .']", " ", value)
    value = re.sub(r"\s+", " ", value).strip().upper()
    return value or None


def mask_tail(value: str | None, keep: int = 4) -> str | None:
    if not value:
        return value
    if len(value) <= keep:
        return "X" * len(value)
    return "X" * (len(value) - keep) + value[-keep:]


_VERHOEFF_D = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
]
_VERHOEFF_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
]


def verhoeff_ok(number: str) -> bool:
    checksum = 0
    for index, character in enumerate(reversed(number)):
        checksum = _VERHOEFF_D[checksum][_VERHOEFF_P[index % 8][int(character)]]
    return checksum == 0


KEYWORDS = {
    "aadhaar": ["aadhaar", "aadhar", "uidai", "unique identification", "आधार", "vid"],
    "driving_license": [
        "driving licence",
        "driving license",
        "union of india",
        "cov",
        "dl no",
        "transport",
        "licence no",
        "date of first issue",
        "non-transport",
    ],
    "puc": [
        "pollution under control",
        "puc",
        "emission",
        "co %",
        "hc (ppm)",
        "pollution certificate",
    ],
    "registration_certificate": [
        "certificate of registration",
        "registration certificate",
        "registration no",
        "date of registration",
        "owner name",
        "regn",
        "maker",
        "chassis no",
    ],
    "insurance": [
        "insurance",
        "policy no",
        "policy number",
        "idv",
        "insured",
        "premium",
        "third party",
        "own damage",
        "insurer",
    ],
}


def classify(text: str) -> str:
    lowercase_text = text.lower()
    scores = {
        document_type: sum(lowercase_text.count(word) for word in words)
        for document_type, words in KEYWORDS.items()
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unknown"


_VEHICLE_RE = re.compile(
    r"\b([A-Z]{2})[\s-]?(\d{1,2})[\s-]?([A-Z]{1,3})[\s-]?(\d{4})\b"
)
_BH_VEHICLE_RE = re.compile(r"\b(\d{2})\s?BH\s?(\d{4})\s?([A-Z]{1,2})\b")
_DL_RE = re.compile(r"\b([A-Z]{2})[\s-]?(\d{2})[\s-]?((?:19|20)\d{2})[\s-]?(\d{7})\b")


def find_vehicle_no(text: str) -> str | None:
    uppercase_text = text.upper()
    match = _VEHICLE_RE.search(uppercase_text)
    if match:
        return "".join(match.groups())
    match = _BH_VEHICLE_RE.search(uppercase_text)
    return "".join(match.groups()) if match else None


def parse_aadhaar(text: str, mask: bool) -> dict[str, Any]:
    no_vid = re.sub(r"\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b", " ", text)
    numbers = [
        re.sub(r"\s", "", number)
        for number in re.findall(r"\b\d{4}\s\d{4}\s\d{4}\b", no_vid)
    ]
    numbers = numbers or re.findall(r"\b\d{12}\b", no_vid)
    number = next((value for value in numbers if value[0] in "23456789"), None)
    output: dict[str, Any] = {
        "aadhaar_number": (mask_tail(number) if mask else number) if number else None,
        "aadhaar_checksum_valid": verhoeff_ok(number) if number else None,
    }

    dob = re.search(
        r"(?:DOB|D\.O\.B|Date of Birth|जन्म)[^\d]{0,15}(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{4})",
        text,
        re.I,
    )
    output["dob"] = norm_date(dob.group(1)) if dob else None
    if not output["dob"]:
        year_of_birth = re.search(
            r"(?:Year of Birth|YOB)\s*[:\-]?\s*(\d{4})", text, re.I
        )
        output["year_of_birth"] = int(year_of_birth.group(1)) if year_of_birth else None

    gender = re.search(r"\b(MALE|FEMALE|TRANSGENDER)\b", text, re.I)
    output["gender"] = gender.group(1).upper() if gender else None
    name = None
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for index, line in enumerate(lines):
        if re.search(r"DOB|Date of Birth|Year of Birth|जन्म", line, re.I) and index:
            candidate = clean_name(lines[index - 1])
            if (
                candidate
                and len(candidate) > 2
                and not re.search(r"GOVERNMENT|INDIA|AADHAAR", candidate)
            ):
                name = candidate
                break
    output["name"] = name
    return output


def parse_license(text: str, mask: bool) -> dict[str, Any]:
    uppercase_text = text.upper()
    match = _DL_RE.search(uppercase_text)
    license_number = "".join(match.groups()) if match else None
    formatted_number = (
        f"{match.group(1)}{match.group(2)} {match.group(3)}{match.group(4)}"
        if match
        else None
    )
    dob = re.search(
        r"(?:DOB|DATE OF BIRTH)[^\d]{0,15}(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{4})",
        uppercase_text,
    )
    issue = re.search(
        r"(?:DATE OF (?:FIRST )?ISSUE|DOI|ISSUE DATE)[^\d]{0,15}(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{4})",
        uppercase_text,
    )
    valid_non_transport = re.search(
        r"(?:VALID(?:ITY)?\s*\(?NT\)?|NON[- ]?TRANSPORT)[^\d]{0,20}(?:TILL|UPTO|TO)?[^\d]{0,10}(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{4})",
        uppercase_text,
    )
    valid_transport = re.search(
        r"(?:VALID(?:ITY)?\s*\(?TR\)?|\bTRANSPORT\b)[^\d]{0,20}(?:TILL|UPTO|TO)?[^\d]{0,10}(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{4})",
        uppercase_text,
    )
    blood = re.search(
        r"BLOOD\s*GROUP\s*[:\-]?\s*(AB|A|B|O)\s*([+-]|POS(?:ITIVE)?|NEG(?:ATIVE)?)",
        uppercase_text,
    )
    classes = re.findall(
        r"\b(MCWG|MCWOG|LMV(?:-NT|-TR)?|HMV|HGMV|HPMV|TRANS|LMV|MGV|FVG|TRCTR|M\.?CYCL)\b",
        uppercase_text,
    )

    output: dict[str, Any] = {
        "license_number": (
            mask_tail(formatted_number, 4)
            if mask and formatted_number
            else formatted_number
        ),
        "name": clean_name(after_label(text, [r"\bName"])),
        "guardian_name": clean_name(
            after_label(
                text, [r"S/?D/?W\s*of", r"Son/Daughter/Wife of", r"Father'?s? Name"]
            )
        ),
        "dob": norm_date(dob.group(1)) if dob else None,
        "date_of_issue": norm_date(issue.group(1)) if issue else None,
        "valid_upto_non_transport": (
            norm_date(valid_non_transport.group(1)) if valid_non_transport else None
        ),
        "valid_upto_transport": (
            norm_date(valid_transport.group(1)) if valid_transport else None
        ),
        "blood_group": (
            blood.group(1)
            + (
                "+"
                if blood.group(2) in ("+", "POS") or blood.group(2).startswith("P")
                else "-"
            )
            if blood
            else None
        ),
        "vehicle_classes": sorted(set(classes)),
        "address": clean_text(after_label(text, [r"Address", r"\bAdd\b"]) or "")
        or None,
        "pin_code": (
            re.search(r"\b[1-9]\d{5}\b", text).group(0)
            if re.search(r"\b[1-9]\d{5}\b", text)
            else None
        ),
        "state_code": license_number[:2] if license_number else None,
    }
    if not output["dob"]:
        dates = sorted(find_dates(text))
        output["dob"] = dates[0] if dates else None
    return output


def parse_puc(text: str, mask: bool) -> dict[str, Any]:
    uppercase_text = text.upper()
    certificate = re.search(
        r"(?:CERTIFICATE|CERT\.?|SL\.?)[ \t]*(?:NO\.?|NUMBER)[ \t]*[:\-]?[ \t]*([A-Z0-9/\-]{6,25})",
        uppercase_text,
    )
    valid = re.search(
        r"VALID\s*(?:UP\s*TO|UPTO|TILL|UNTIL)[^\d]{0,10}(\d{1,2}[/\-.\s][\dA-Z]{1,3}[/\-.\s]\d{4})",
        uppercase_text,
    )
    tested = re.search(
        r"(?:DATE OF TEST|TEST DATE|TESTED ON|DATE)[^\d]{0,10}(\d{1,2}[/\-.\s][\dA-Z]{1,3}[/\-.\s]\d{4})",
        uppercase_text,
    )
    co = re.search(r"\bCO\b[^\d\n]{0,15}(\d+(?:\.\d+)?)", uppercase_text)
    hc = re.search(r"\bHC\b[^\d\n]{0,15}(\d+(?:\.\d+)?)", uppercase_text)
    smoke = re.search(
        r"(?:HSU|SMOKE DENSITY|K\s*VALUE)[^\d\n]{0,15}(\d+(?:\.\d+)?)",
        uppercase_text,
    )
    result = (
        "PASS"
        if re.search(r"\bPASS(?:ED)?\b", uppercase_text)
        else "FAIL"
        if re.search(r"\bFAIL(?:ED)?\b", uppercase_text)
        else None
    )
    fuel = re.search(r"\b(PETROL|DIESEL|CNG|LPG|ELECTRIC)\b", uppercase_text)
    return {
        "vehicle_number": find_vehicle_no(text),
        "certificate_number": certificate.group(1) if certificate else None,
        "test_date": norm_date(tested.group(1)) if tested else None,
        "valid_upto": norm_date(valid.group(1)) if valid else None,
        "fuel_type": fuel.group(1) if fuel else None,
        "co_percent": float(co.group(1)) if co else None,
        "hc_ppm": float(hc.group(1)) if hc else None,
        "smoke_density": float(smoke.group(1)) if smoke else None,
        "result": result,
    }


def parse_insurance(text: str, mask: bool) -> dict[str, Any]:
    uppercase_text = text.upper()
    policy = re.search(
        r"POLICY\s*(?:NO\.?|NUMBER|#)\s*[:\-]?\s*([A-Z0-9/\-]{6,30})",
        uppercase_text,
    )
    valid_from = re.search(
        r"(?:FROM|START(?:S)?(?: DATE)?|INCEPTION)[^\d]{0,15}(\d{1,2}[/\-.\s][\dA-Z]{1,3}[/\-.\s]\d{4})",
        uppercase_text,
    )
    valid_to = re.search(
        r"(?:TO|EXPIR(?:Y|ES)(?: DATE)?|VALID (?:UP)?TO|END DATE|MIDNIGHT OF)[^\d]{0,15}(\d{1,2}[/\-.\s][\dA-Z]{1,3}[/\-.\s]\d{4})",
        uppercase_text,
    )
    idv = re.search(r"IDV[^\d]{0,25}([\d,]+(?:\.\d+)?)", uppercase_text)
    premium = re.search(
        r"(?:TOTAL\s*)?PREMIUM[^\d]{0,25}([\d,]+(?:\.\d+)?)", uppercase_text
    )
    chassis = re.search(
        r"CHASSIS\s*(?:NO\.?|NUMBER)?\s*[:\-]?\s*([A-Z0-9]{10,20})",
        uppercase_text,
    )
    engine = re.search(
        r"ENGINE\s*(?:NO\.?|NUMBER)?\s*[:\-]?\s*([A-Z0-9]{6,20})",
        uppercase_text,
    )
    insurer = re.search(
        r"([A-Z][A-Z &.]{3,40}(?:GENERAL INSURANCE|INSURANCE CO(?:MPANY)?\.?(?: LTD\.?| LIMITED)?|ASSURANCE))",
        uppercase_text,
    )
    if "COMPREHENSIVE" in uppercase_text or "PACKAGE" in uppercase_text:
        policy_type = "COMPREHENSIVE"
    elif re.search(r"THIRD[\s-]*PARTY|LIABILITY ONLY", uppercase_text):
        policy_type = "THIRD_PARTY"
    else:
        policy_type = None

    def numeric_value(match: re.Match[str] | None) -> float | None:
        return float(match.group(1).replace(",", "")) if match else None

    return {
        "policy_number": policy.group(1) if policy else None,
        "insurer": re.sub(r"\s+", " ", insurer.group(1)).strip() if insurer else None,
        "policy_type": policy_type,
        "insured_name": clean_name(
            after_label(text, [r"Insured(?: Name)?", r"Name of (?:the )?Insured"])
        ),
        "vehicle_number": find_vehicle_no(text),
        "chassis_number": chassis.group(1) if chassis else None,
        "engine_number": engine.group(1) if engine else None,
        "valid_from": norm_date(valid_from.group(1)) if valid_from else None,
        "valid_to": norm_date(valid_to.group(1)) if valid_to else None,
        "idv": numeric_value(idv),
        "total_premium": numeric_value(premium),
    }


def parse_rc(text: str, mask: bool) -> dict[str, Any]:
    uppercase_text = text.upper()
    date_pattern = r"(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{4})"
    registration_date = re.search(
        r"DATE OF REGISTRATION[^\d]{0,10}" + date_pattern, uppercase_text
    )
    valid = re.search(
        r"VALID\s*(?:UP\s*TO|UPTO|TILL)[^\d]{0,10}" + date_pattern, uppercase_text
    )
    manufacture = re.search(r"MFG[^\d\n]{0,20}(\d{2}/\d{4}|\d{4})", uppercase_text)
    chassis = re.search(
        r"CHASSIS\s*(?:NO\.?|NUMBER)?\s*[:\-]?\s*([A-Z0-9]{10,20})",
        uppercase_text,
    )
    engine = re.search(
        r"ENGINE\s*(?:NO\.?|NUMBER)\s*[:\-]?\s*([A-Z0-9]{6,20})",
        uppercase_text,
    )
    fuel = re.search(r"\b(PETROL|DIESEL|CNG|LPG|ELECTRIC)\b", uppercase_text)

    def uppercase(value: str | None) -> str | None:
        return re.sub(r"\s+", " ", value).strip().upper() if value else None

    return {
        "registration_number": find_vehicle_no(text),
        "owner_name": clean_name(after_label(text, [r"Owner(?:'s)? Name"])),
        "guardian_name": clean_name(
            after_label(text, [r"S/?W/?D\s*of", r"Son/Wife/Daughter of"])
        ),
        "address": uppercase(after_label(text, [r"Address"])),
        "date_of_registration": (
            norm_date(registration_date.group(1)) if registration_date else None
        ),
        "registration_valid_upto": norm_date(valid.group(1)) if valid else None,
        "vehicle_class": uppercase(after_label(text, [r"Vehicle Class"])),
        "maker": uppercase(after_label(text, [r"Maker"])),
        "model": uppercase(after_label(text, [r"Model"])),
        "fuel_type": fuel.group(1) if fuel else None,
        "colour": uppercase(after_label(text, [r"Colou?r"])),
        "manufacture_date": manufacture.group(1) if manufacture else None,
        "chassis_number": chassis.group(1) if chassis else None,
        "engine_number": engine.group(1) if engine else None,
    }


PARSERS = {
    "aadhaar": parse_aadhaar,
    "driving_license": parse_license,
    "puc": parse_puc,
    "insurance": parse_insurance,
    "registration_certificate": parse_rc,
}

SAFE_RESULT_FIELDS = {
    "aadhaar": {"aadhaar_number", "aadhaar_checksum_valid", "year_of_birth"},
    "driving_license": {
        "license_number",
        "dob",
        "date_of_issue",
        "valid_upto_non_transport",
        "valid_upto_transport",
        "vehicle_classes",
        "state_code",
    },
    "puc": {
        "vehicle_number",
        "certificate_number",
        "test_date",
        "valid_upto",
        "fuel_type",
        "co_percent",
        "hc_ppm",
        "smoke_density",
        "result",
    },
    "insurance": {
        "policy_number",
        "insurer",
        "policy_type",
        "vehicle_number",
        "chassis_number",
        "engine_number",
        "valid_from",
        "valid_to",
        "idv",
        "total_premium",
    },
    "registration_certificate": {
        "registration_number",
        "date_of_registration",
        "registration_valid_upto",
        "vehicle_class",
        "maker",
        "model",
        "fuel_type",
        "colour",
        "manufacture_date",
        "chassis_number",
        "engine_number",
    },
}

MASKED_RESULT_FIELDS = {
    "aadhaar": {"aadhaar_number"},
    "driving_license": {"license_number"},
    "puc": {"vehicle_number", "certificate_number"},
    "insurance": {"policy_number", "vehicle_number", "chassis_number", "engine_number"},
    "registration_certificate": {
        "registration_number",
        "chassis_number",
        "engine_number",
    },
}


def sanitize_result(result: dict[str, Any]) -> dict[str, Any]:
    document_type = result.get("document_type")
    if result.get("status") != "ok" or document_type not in SAFE_RESULT_FIELDS:
        error = result.get("error")
        error_code = (
            "unknown_document_type"
            if document_type == "unknown" or "identify" in str(error).lower()
            else "no_text"
        )
        return {"error_code": error_code}

    source_data = result.get("data") or {}
    data = {}
    for field in SAFE_RESULT_FIELDS[document_type]:
        value = source_data.get(field)
        if field == "dob" and value:
            value = value[:4]
        if field in MASKED_RESULT_FIELDS[document_type] and value:
            value = mask_tail(str(value))
        data[field] = value

    if document_type in ("aadhaar", "driving_license"):
        year = source_data.get("year_of_birth")
        if not year and source_data.get("dob"):
            year = int(source_data["dob"][:4])
        if document_type == "aadhaar":
            data["year_of_birth"] = year
        else:
            data["dob"] = year

    return {
        "document_type": document_type,
        "confidence": result.get("confidence"),
        "data": data,
    }


def process_pdf(
    pdf: bytes,
    doc_type: str | None = None,
    mask_pii: bool = True,
) -> dict[str, Any]:
    validate_pdf(pdf)
    text = clean_text(extract_text(pdf))
    if not text:
        return {"status": "error", "error": "no_text"}

    document_type = doc_type or classify(text)
    if document_type not in PARSERS:
        return {
            "status": "error",
            "error": "unknown_document_type",
            "document_type": "unknown",
        }

    data = PARSERS[document_type](text, mask_pii)
    filled = sum(value not in (None, "", [], False) for value in data.values())
    return {
        "status": "ok",
        "document_type": document_type,
        "confidence": round(filled / len(data), 2),
        "data": data,
    }
