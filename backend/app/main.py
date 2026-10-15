import csv
from io import StringIO
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from app.services.extraction import extract, infer_kind
from app.services.matching import compare
from app.services.security import validate_upload
from app.services.storage import (
    get_audit as load_audit,
)
from app.services.storage import (
    get_document as load_document,
)
from app.services.storage import (
    save_audit,
    save_document,
)

app = FastAPI(title="Ledger Beacon API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
class AuditRequest(BaseModel):
    po_document_id: str
    target_document_id: str


def document_payload(document):
    return {
        "id": document.id,
        "filename": document.filename,
        "kind": document.kind,
        "status": document.status,
        "fields": document.fields,
        "lines": [
            {
                **line.__dict__,
                "quantity": str(line.quantity) if line.quantity is not None else None,
                "unit_price": str(line.unit_price) if line.unit_price is not None else None,
                "total": str(line.total) if line.total is not None else None,
            }
            for line in document.lines
        ],
        "provenance": document.provenance,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/documents", status_code=201)
async def upload_document(file: UploadFile = File(...)):
    data = await file.read()
    extension = validate_upload(file.filename or "", file.content_type, data)
    raw_text, fields, lines, provenance, extract_status = extract(
        data, extension, file.filename or ""
    )
    from app.domain.models import Document

    document = Document(
        str(uuid4()),
        file.filename or "",
        file.content_type or "",
        infer_kind(file.filename or ""),
        extract_status,
        raw_text,
        fields,
        lines,
        provenance,
    )
    save_document(document)
    return document_payload(document)


@app.get("/api/documents/{document_id}")
def get_document(document_id: str):
    document = load_document(document_id)
    if document is None:
        raise HTTPException(404, "Document not found")
    return document_payload(document)


@app.post("/api/audits", status_code=201)
def create_audit(request: AuditRequest):
    po, target = load_document(request.po_document_id), load_document(request.target_document_id)
    if po is None or target is None:
        raise HTTPException(404, "Document not found")
    audit = compare(po, target, str(uuid4()))
    save_audit(audit)
    return audit_payload(audit)


def audit_payload(audit):
    return {
        "id": audit.id,
        "po_document_id": audit.po_document_id,
        "target_document_id": audit.target_document_id,
        "status": audit.status,
        "confidence": audit.confidence,
        "findings": [finding.__dict__ for finding in audit.findings],
    }


@app.get("/api/audits/{audit_id}")
def get_audit(audit_id: str):
    audit = load_audit(audit_id)
    if audit is None:
        raise HTTPException(404, "Audit not found")
    return audit_payload(audit)


@app.get("/api/audits/{audit_id}/export.csv")
def export_audit(audit_id: str):
    audit = load_audit(audit_id)
    if audit is None:
        raise HTTPException(404, "Audit not found")
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["code", "field", "message", "expected", "actual"])
    for finding in audit.findings:
        writer.writerow(
            [finding.code, finding.field, finding.message, finding.expected, finding.actual]
        )
    return Response(
        output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="audit-{audit.id}.csv"'},
    )
