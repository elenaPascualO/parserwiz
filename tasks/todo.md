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

### Smart JSON Handling for Complex Structures (January 2026)

- [x] **Complexity analysis**: New `/api/analyze` endpoint to detect complex JSON before conversion
- [x] **Simplified UX flow**: Info message with "Next" button leads directly to preview with tabs
- [x] **`_record_id` explanation**: Tip in info screen explains the auto-generated column for linking records
- [x] **Preview with tabs**: Toggle between "Multi-file" and "Single-file" views to compare options
- [x] **Multi-table export**: Normalized output with one table per array
  - Excel: Multiple sheets linked by `_record_id`
  - CSV: ZIP file with multiple CSV files
- [x] **Single-row export**: Arrays kept as JSON strings in columns
- [x] **Updated preview/convert APIs**: Accept `export_mode` parameter
- [x] **Frontend integration**: Automatic analysis and tabbed preview for complex JSON

### Nested JSON Array Expansion (January 2026)

- [x] **Nested array expansion**: JSON with nested arrays now expands via Cartesian product instead of losing data
- [x] **Single object fix**: Single objects with multiple nested arrays preserve all fields (nested2.json: 4×7=28 rows)
- [x] **Array of objects fix**: Arrays with nested arrays fully expand (nested3.json: 41 rows total)
- [x] **Safety limit**: MAX_EXPANDED_ROWS=10000 prevents memory issues from large Cartesian products
- [x] **Tests**: 4 new tests (78 total tests passing)

### Frontend Features (January 2026)

- [x] **Privacy disclaimer**: Added footer text informing users files are processed in memory
- [x] **Feedback form**: Discord webhook integration for collecting user feedback
- [x] **Hover hint**: Added "💡 Hover over cells to view full content" message above preview tables
- [x] **Start Over button**: Renamed "Upload another file" to "Start Over" for clearer UX
- [x] **Accordion default collapsed**: Multi-table accordion now shows all tables collapsed by default

### Security Implementation (January 2026)

- [x] **Filename sanitization**: Prevents header injection via Content-Disposition
- [x] **Security headers middleware**: X-Frame-Options, X-Content-Type-Options, CSP, Referrer-Policy
- [x] **Production CORS**: Environment-based CORS configuration (ALLOWED_ORIGINS env var)
- [x] **Security tests**: 20 new tests for security features
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
