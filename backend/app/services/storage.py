from decimal import Decimal

from sqlalchemy import delete

from app.db.database import SessionLocal, create_tables
from app.db.models import AuditRecord, DocumentRecord
from app.domain.models import Audit, Document, Finding, LineItem


def _line_payload(line: LineItem) -> dict:
    return {
        "description": line.description,
        "quantity": str(line.quantity) if line.quantity is not None else None,
        "unit_price": str(line.unit_price) if line.unit_price is not None else None,
        "total": str(line.total) if line.total is not None else None,
        "provenance": line.provenance,
    }


def _document(record: DocumentRecord) -> Document:
    lines = [
        LineItem(
            item["description"],
            Decimal(item["quantity"]) if item["quantity"] else None,
            Decimal(item["unit_price"]) if item["unit_price"] else None,
            Decimal(item["total"]) if item["total"] else None,
            item["provenance"],
        )
        for item in record.lines
    ]
    return Document(
        record.id,
        record.filename,
        record.content_type,
        record.kind,
        record.status,
        record.raw_text,
        record.fields,
        lines,
        record.provenance,
    )


def save_document(document: Document) -> None:
    create_tables()
    with SessionLocal.begin() as session:
        session.merge(
            DocumentRecord(
                id=document.id,
                filename=document.filename,
                content_type=document.content_type,
                kind=document.kind,
                status=document.status,
                raw_text=document.raw_text,
                fields=document.fields,
                lines=[_line_payload(line) for line in document.lines],
                provenance=document.provenance,
            )
        )


def get_document(document_id: str) -> Document | None:
    with SessionLocal() as session:
        record = session.get(DocumentRecord, document_id)
        return _document(record) if record else None


def save_audit(audit: Audit) -> None:
    with SessionLocal.begin() as session:
        session.merge(
            AuditRecord(
                id=audit.id,
                po_document_id=audit.po_document_id,
                target_document_id=audit.target_document_id,
                status=audit.status,
                confidence=audit.confidence,
                findings=[finding.__dict__ for finding in audit.findings],
            )
        )


def get_audit(audit_id: str) -> Audit | None:
    with SessionLocal() as session:
        record = session.get(AuditRecord, audit_id)
        if record is None:
            return None
        return Audit(
            record.id,
            record.po_document_id,
            record.target_document_id,
            record.status,
            record.confidence,
            [Finding(**item) for item in record.findings],
        )


def reset() -> None:
    create_tables()
    with SessionLocal.begin() as session:
        session.execute(delete(AuditRecord))
        session.execute(delete(DocumentRecord))
