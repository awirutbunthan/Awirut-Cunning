-- Initial local-development schema; migrations will be managed with Alembic in M2.
CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, filename TEXT NOT NULL, status TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audits (id TEXT PRIMARY KEY, po_document_id TEXT NOT NULL, target_document_id TEXT NOT NULL, status TEXT NOT NULL);
