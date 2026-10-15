# Ledger Beacon — invoice audit MVP

Local-first review of synthetic purchase orders, invoices, delivery notes and receipts. It validates uploads before extraction, preserves provenance, and presents mismatches for human review.

## Run the API

Windows PowerShell or Linux shell:

```sh
cd backend
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`; health check is `/health`.

## Run the UI

```sh
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. The UI only accepts PDF, XLSX and ZIP. Uploaded documents are held in memory in this MVP and must not contain real customer information.

## Verification

```sh
cd backend && python -m pytest && python -m ruff check .
cd frontend && npm ci && npm run lint && npm run typecheck && npm run build
```

OCR, persistence, authentication, and external integrations are explicitly deferred; OCR-only PDFs are reported as `OCR_REQUIRED`, never populated with invented values.
