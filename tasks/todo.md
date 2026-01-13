# Tasks

## Current Sprint

_Phase 0 MVP - Complete_

## Backlog

- [ ] Deploy to Railway/Render/Fly.io
- [ ] Configure production HTTPS
- [ ] Add domain configuration

## Completed

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
  - POST /api/preview
  - POST /api/convert
- [x] Create tests with sample files (31 tests passing)
- [x] Build frontend/index.html (drag & drop, file selector)
- [x] Build frontend/styles.css (responsive, loading states)
- [x] Build frontend/app.js (API integration, file handling)

### Supported Conversions
| Input | Output |
|-------|--------|
| JSON  | CSV, XLSX |
| CSV   | JSON |
| XLSX/XLS | JSON |
