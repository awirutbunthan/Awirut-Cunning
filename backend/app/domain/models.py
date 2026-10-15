from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal

DocumentKind = Literal["po", "invoice", "delivery_note", "receipt", "unknown"]


@dataclass
class LineItem:
    description: str
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    total: Decimal | None = None
    provenance: dict[str, int | str] = field(default_factory=dict)


@dataclass
class Document:
    id: str
    filename: str
    content_type: str
    kind: DocumentKind
    status: str
    raw_text: str
    fields: dict[str, str | None]
    lines: list[LineItem]
    provenance: list[dict[str, int | str]]


@dataclass
class Finding:
    code: str
    field: str
    message: str
    expected: str | None
    actual: str | None


@dataclass
class Audit:
    id: str
    po_document_id: str
    target_document_id: str
    status: str
    confidence: float
    findings: list[Finding]
