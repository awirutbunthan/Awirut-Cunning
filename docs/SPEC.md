# Awirut-Cunning — MVP Product & Engineering Specification
Status: Proposed baseline, pending confirmation against legacy source files. Date: 2026-10-15.

## Context and scope
The repository README currently contains only its title. This is an initial implementation proposal for a **purchase-order, invoice, receipt and billing audit** application (based on the owner's previously discussed Ledger Beacon workflow); it is not evidence that the existing application or integrations are deployed here.

## MVP outcomes
1. Upload PO, invoice, delivery note, and receipt documents in PDF, XLSX and ZIP containers. Validate file extension, MIME, compressed size, extracted size and entry paths; reject ZIP traversal and ZIP bombs. Never execute uploaded content.
2. Extract PDF text; for image-only PDFs mark OCR_REQUIRED and provide a pluggable OCR adapter, not invented values.
3. Extract and normalize legal customer name, taxpayer ID, document number, date, line descriptions, quantity, price, VAT and grand total; retain raw source text and provenance (filename/page/sheet/row).
4. Match extracted invoice lines and totals against an authoritative PO; flag missing, inconsistent or low-confidence data, do not silently overwrite with a guessed value.
5. Present human review queue with differences and manual correction/audit log. Export a CSV summary in the first milestone; XLSX can follow.
6. Keep production secrets and customer documents outside version control; design for local operation first.

## Architecture baseline
- Backend: Python 3.12, FastAPI, Pydantic, SQLAlchemy with SQLite local dev database and Alembic migrations.
- Frontend: React, TypeScript and Vite; simple upload/review screen.
- Extraction layer: pdfplumber/PyMuPDF and openpyxl; ZIP through standard-library zipfile with hard limits.
- Tests: pytest for API, parsing, matching and security; frontend lint/typecheck/build and a minimal UI test.
- CI: GitHub Actions for backend tests and frontend checks, with locked dependencies where possible.
- Sample documents: synthetic fixtures only; no real customer data or tax identifiers.

## Repository layout
```
backend/
  app/
    api/
    core/
    db/
    domain/
    extractors/
    services/
    main.py
  tests/
  pyproject.toml
  alembic.ini
frontend/
  src/
  package.json
  tsconfig.json
  vite.config.ts
docs/
  SPEC.md
  ARCHITECTURE.md
  TEST_REPORT.md
.github/workflows/ci.yml
.env.example
.gitignore
README.md
```

## Initial API contract
- `GET /health` -> `{"status":"ok"}`
- `POST /api/documents` (multipart upload) -> document ID and queued/processed status.
- `GET /api/documents/{id}` -> document metadata, extracted fields and provenance.
- `POST /api/audits` (PO document ID and target document ID) -> discrepancies, confidence and status.
- `GET /api/audits/{id}` -> audit result.
- `GET /api/audits/{id}/export.csv` -> CSV.
Use validation schemas, error semantics, and deterministic IDs. Avoid misleading dummy audit results.

## Matching and arithmetic
- Normalize Thai/English Unicode whitespace, punctuation and company suffixes conservatively; preserve original names.
- Match legal name and taxpayer ID from actual PO source. Never fabricate customer identity or totals.
- Calculate line totals with Decimal and configurable VAT rules; compare to tolerance <= THB 0.01 for currency rounding.
- Surface quantity, unit price, subtotal, tax and grand-total mismatches as separate findings.
- Explicit manual-review state for absent, conflicting or OCR-dependent values.

## Security and privacy
- Limit total request bytes and file counts, ZIP nesting, entry count, and uncompressed bytes.
- Reject path traversal, symlinks and unsupported formats.
- Sanitize download filenames, escape UI content, log no raw sensitive files, never commit .env or uploads.
- Default CORS to localhost during development; require authorization before production exposure.
- No real Gmail/API credentials, external integrations or payment usage in initial milestone.

## Definition of Done — first code batch
- README documents exact installation and local startup on Windows and Linux.
- Backend `pytest` and formatting/static checks pass.
- Frontend `npm ci`, `npm run lint`, `npm run typecheck`, and `npm run build` pass.
- Integration tests cover /health, invalid uploads, one synthetic PO+invoice discrepancy, no-data/manual-review and unsafe ZIP.
- CI invokes the same commands; no untracked dependencies or secrets.
- `docs/TEST_REPORT.md` records commands, outcomes, defects, fixes, and remaining limits.
- Where OCR or integrations are not implemented, mark them openly as future scope instead of claiming completion.

## PM execution protocol
1. Inspect repository state and spec. Implement on `feat/mvp-foundation` (not main).
2. Commit coherent implementation; open a PR with changed-file summary.
3. Run all checks, capture command outputs and fix failures, repeat until green or documented blocker.
4. Review security, arithmetic and extraction correctness with synthetic fixtures.
5. Do not merge to main before validated PR review. Do not claim tests ran without runner logs.

## Milestone roadmap
M1 foundation/API/basic extraction/matching/CI; M2 scanned PDF OCR with quality checks; M3 XLSX billing ledger and reconciliation; M4 role-based access, integration connectors, deployment and monitoring.
