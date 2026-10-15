from app.domain.models import Audit, Document

documents: dict[str, Document] = {}
audits: dict[str, Audit] = {}


def reset() -> None:
    documents.clear()
    audits.clear()
