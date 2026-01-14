# Tasks

## Current Sprint

_Security Implementation (P0) - Complete_

## Backlog

- [ ] Deploy to Railway/Render/Fly.io
- [ ] Configure production HTTPS
- [ ] Add domain configuration
- [ ] Implement rate limiting (P1 security)
- [ ] Implement request timeouts (P1 security)
- [ ] Implement ZIP bomb protection for XLSX (P1 security)

## Completed

### Security Implementation (January 2026)

- [x] **Filename sanitization**: Prevents header injection via Content-Disposition
- [x] **Security headers middleware**: X-Frame-Options, X-Content-Type-Options, CSP, Referrer-Policy
- [x] **Production CORS**: Environment-based CORS configuration (ALLOWED_ORIGINS env var)
- [x] **Security tests**: 20 new tests for security features (74 total tests)
- [x] **Specifications document**: Created comprehensive doc/SPECIFICATIONS.md

### Phase 0 Improvements (January 2026)

- [x] **Pagination for large files**: Added Previous/Next buttons with page indicator, backend support for page/page_size params
- [x] **Preserve data exactly as in file**: Preview reads all data as strings, preserving leading zeroes (e.g., "007")
- [x] **CSV → Excel conversion**: New converter to convert CSV files to .xlsx format
- [x] **Excel → CSV conversion**: New converter to convert .xlsx/.xls files to CSV format
- [x] **Improved error messages**: Detailed errors for malformed JSON (line/column), CSV (encoding, parsing), and Excel (corrupted, format)
- [x] Updated documentation (PHASE0.md, CLAUDE.md)

### Phase 0 MVP Implementation

- [x] Configure dependencies in pyproject.toml (FastAPI, pandas, openpyxl, xlrd, pytest)
- [x] Create backend directory structure (converters/, utils/)
- [x] Implement backend/config.py (MIME types, allowed extensions, CORS)
- [x] Implement backend/utils/file_detection.py (auto-detect JSON, CSV, Excel)
- [x] Implement backend/utils/validators.py (file validation)
- [x] Implement backend/converters/base.py (abstract base class)
- [x] Implement backend/converters/json_to_csv.py (with JSON flattening)
- [x] Implement backend/converters/json_to_excel.py
- [x] Implement backend/converters/csv_to_json.py (with delimiter auto-detection)
- [x] Implement backend/converters/excel_to_json.py
- [x] Implement API endpoints in backend/main.py:
  - GET /api/health
  - POST /api/preview (with pagination)
  - POST /api/convert
- [x] Create tests with sample files (43 tests passing)
- [x] Build frontend/index.html (drag & drop, file selector, pagination)
- [x] Build frontend/styles.css (responsive, loading states, pagination controls)
- [x] Build frontend/app.js (API integration, file handling, pagination)

### Supported Conversions
| Input | Output |
|-------|--------|
| JSON  | CSV, XLSX |
| CSV   | JSON, XLSX |
| XLSX/XLS | JSON, CSV |
