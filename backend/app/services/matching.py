import re
from decimal import Decimal

from app.domain.models import Audit, Document, Finding

TOLERANCE = Decimal("0.01")


def normalize_name(value: str | None) -> str:
    if not value:
        return ""
    value = re.sub(r"[.,()]", " ", value.casefold())
    value = re.sub(r"\b(co|company|limited|ltd|บริษัท|จำกัด)\b", " ", value)
    return " ".join(value.split())


def compare(po: Document, target: Document, audit_id: str) -> Audit:
    findings: list[Finding] = []
    for field in ("taxpayer_id", "legal_name"):
        expected, actual = po.fields.get(field), target.fields.get(field)
        if not expected or not actual:
            findings.append(
                Finding(
                    "MISSING_DATA", field, "Manual review required: value absent.", expected, actual
                )
            )
        elif (normalize_name(expected) if field == "legal_name" else expected.replace("-", "")) != (
            normalize_name(actual) if field == "legal_name" else actual.replace("-", "")
        ):
            findings.append(
                Finding("MISMATCH", field, "Value differs from purchase order.", expected, actual)
            )
    po_total = (
        Decimal(po.fields["grand_total"].replace(",", "")) if po.fields.get("grand_total") else None
    )
    target_total = (
        Decimal(target.fields["grand_total"].replace(",", ""))
        if target.fields.get("grand_total")
        else None
    )
    if po_total is None or target_total is None:
        findings.append(
            Finding(
                "MISSING_DATA",
                "grand_total",
                "Manual review required: total absent.",
                str(po_total) if po_total is not None else None,
                str(target_total) if target_total is not None else None,
            )
        )
    elif abs(po_total - target_total) > TOLERANCE:
        findings.append(
            Finding(
                "MISMATCH",
                "grand_total",
                "Grand total differs beyond THB 0.01.",
                str(po_total),
                str(target_total),
            )
        )
    if po.status != "PROCESSED" or target.status != "PROCESSED":
        findings.append(
            Finding(
                "MANUAL_REVIEW", "extraction", "OCR or extraction review is required.", None, None
            )
        )
    confidence = max(0.0, 1.0 - (len(findings) * 0.2))
    return Audit(
        audit_id, po.id, target.id, "MANUAL_REVIEW" if findings else "MATCHED", confidence, findings
    )
