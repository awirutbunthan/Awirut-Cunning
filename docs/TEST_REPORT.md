# MVP test report

Date: 2026-10-15 (Asia/Bangkok)
Branch: `feat/mvp-foundation`

## Executed checks

| Command | Result | Evidence |
| --- | --- | --- |
| `python -m pytest -q` (in `backend`) | PASS | 5 passed in 0.81s |
| `python -m ruff check .` (in `backend`) | PASS | `All checks passed!` |
| `python -m alembic upgrade head` (in `backend`) | PASS | Initial SQLite migration applied |
| `npm ci` (in `frontend`) | PASS | 183 packages installed; 0 vulnerabilities reported by npm audit |
| `npm run lint` (in `frontend`) | PASS | ESLint exited 0 |
| `npm run typecheck` (in `frontend`) | PASS | TypeScript exited 0 |
| `npm run test` (in `frontend`) | PASS | 1 Vitest UI test passed |
| `npm run build` (in `frontend`) | PASS | Vite production build completed |
| GitHub Actions CI run #4 | PASS | Backend and frontend jobs completed successfully after the SQLite revision |

After adding SQLite persistence, direct storage verification (`save_document` then `get_document`) passed. A repeat API-suite run on this Windows runner could not complete because the runner began refusing local socket access (the same restriction prevented a temporary Uvicorn health probe). GitHub Actions CI run #4 subsequently passed its backend and frontend jobs, providing the authoritative Linux integration recheck for this persistence-only revision.

## Coverage exercised

- Health endpoint responds with `{"status":"ok"}`.
- Synthetic PO and invoice XLSX files produce a deterministic total mismatch and CSV audit export.
- Missing fields produce an explicit `MANUAL_REVIEW` result.
- Invalid file types and ZIP path traversal are rejected.
- The UI test verifies that the upload control is present and limited to PDF, XLSX, and ZIP.

## Defects found and fixed during verification

1. Editable Python installation initially failed because automatic package discovery considered the migration directory a second top-level package. Package discovery is now restricted to `app*`.
2. The unconstrained FastAPI resolver selected a current FastAPI/Starlette combination that caused the API test client to hang on this runner. Runtime and test dependencies are pinned to a compatible set.
3. Frontend typecheck initially failed because React declarations were not declared. `@types/react`, `@types/react-dom`, and Vite client types were added.
4. The first persistence revision accidentally shadowed API handler names with storage functions, causing recursive lookups. Storage imports are now aliased and SQLite persistence is verified directly.

## Remaining limitations

- OCR is deliberately not implemented. Image-only PDFs are marked `OCR_REQUIRED`.
- The parser supports conservative label and pipe-delimited synthetic layouts; production document templates need extension and test fixtures.
- Authentication, durable audit-log storage, XLSX export, and third-party integrations are future milestones.
