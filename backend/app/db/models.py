from sqlalchemy import JSON, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class DocumentRecord(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    fields: Mapped[dict] = mapped_column(JSON, nullable=False)
    lines: Mapped[list] = mapped_column(JSON, nullable=False)
    provenance: Mapped[list] = mapped_column(JSON, nullable=False)


class AuditRecord(Base):
    __tablename__ = "audits"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    po_document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    target_document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    findings: Mapped[list] = mapped_column(JSON, nullable=False)
