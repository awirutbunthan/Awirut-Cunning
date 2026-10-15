# Architecture

Ledger Beacon is a local-first FastAPI and React application. The API keeps document metadata in an in-memory repository for the initial milestone; the supplied SQLite migration sketch reserves the persistence boundary for the next milestone.

Uploads are bounded before parsing. ZIP archives are checked for traversal, symlinks, entry count, decompressed size, and compression ratio. PDF and XLSX parsing retain source provenance. OCR-only PDFs become `OCR_REQUIRED`; missing or inconsistent extracted values lead to `MANUAL_REVIEW`, never guessed output.

The React UI is intentionally a small upload/review entry point. It communicates with the local API only. No credentials, uploaded files, or external service integrations are committed to this repository.
