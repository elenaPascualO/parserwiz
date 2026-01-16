# DataToolkit — Technical Specifications

## 1. Overview

**Product Name:** DataToolkit
**Version:** 0.1.0 (Phase 0 - MVP)
**Purpose:** Web tool for conversion, cleaning, and manipulation of tabular data (JSON, CSV, Excel)

### 1.1 Vision
Provide a simple, fast, and privacy-focused tool for converting between common tabular data formats without requiring user registration or storing user data.

### 1.2 Current Status
Phase 0 (MVP) complete with basic file conversions. Pending deployment.

---

## 2. Functional Specifications

### 2.1 Supported File Formats

| Format | Extensions | Read | Write |
|--------|------------|------|-------|
| JSON | .json | Yes | Yes |
| CSV | .csv | Yes | Yes |
| Excel | .xlsx | Yes | Yes |
| Legacy Excel | .xls | Yes | No |

### 2.2 Supported Conversions

| Input | Output Options |
|-------|---------------|
| JSON | CSV, XLSX |
| CSV | JSON, XLSX |
| XLSX | JSON, CSV |
| XLS | JSON, CSV |

### 2.3 Core Features

#### File Upload
- Drag & drop support
- File selector button
- Single file at a time (Phase 0)

#### Data Preview
- Displays data in HTML table format
- Pagination support (configurable page size, max 100 rows per page)
- Shows column headers and row data
- Preserves data exactly as in file (strings remain strings)

#### File Conversion
- Direct download of converted file
- Automatic filename generation (original_name.new_extension)

#### User Experience
- No registration required
- Anonymous usage
- Loading indicators
- User-friendly error messages with specific details
- Privacy disclaimer in footer
- Feedback form (Discord webhook integration)

#### Complex JSON Handling
- Automatic complexity detection (threshold: >100 estimated rows from multiple arrays)
- Info screen explains detected complexity with "Next" button
- Tip explaining `_record_id` column (auto-added to link related records across tables)
- Tabbed preview to compare export options:
  - **Multi-file**: Accordion view showing each table (all collapsed by default)
  - **Single-file**: Compact view with arrays as JSON text columns
- Download uses the currently selected tab's export mode

#### Preview UX Enhancements
- Hover hint message above tables ("💡 Hover over cells to view full content")
- "Start Over" button (renamed from "Upload another file") for clearer reset action

#### Raw Editor for Malformed Files
- Shows raw text editor when JSON/CSV files fail to parse
- Displays parse error message inline (above editor)
- Line numbers for easy error location
- Users can edit content and retry parsing
- On success, proceeds to normal table preview
- Not available for Excel (binary format)

---

## 3. Technical Specifications

### 3.1 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│              HTML + CSS + Vanilla JavaScript                 │
│                    (No frameworks)                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              │
┌─────────────────────────────────────────────────────────────┐
│                        Backend                               │
│                   Python 3.13+ / FastAPI                     │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Routes    │  │  Converters │  │      Utilities      │  │
│  │  main.py    │  │  json_to_*  │  │  file_detection.py  │  │
│  │             │  │  csv_to_*   │  │  validators.py      │  │
│  │             │  │  excel_to_* │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Backend Framework | FastAPI | >=0.109.0 |
| ASGI Server | Uvicorn | >=0.27.0 |
| Data Processing | pandas | >=2.2.0 |
| Excel (modern) | openpyxl | >=3.1.2 |
| Excel (legacy) | xlrd | >=2.0.1 |
| Package Manager | uv | Latest |
| Python | Python | >=3.13 |

### 3.3 API Endpoints

#### Health Check
```
GET /api/health
Response: { "status": "ok" }
```

#### Analyze File (JSON Complexity)
```
POST /api/analyze
Content-Type: multipart/form-data

Parameters:
- file: File (required) - The file to analyze

Response:
{
  "is_complex": true,
  "estimated_rows": 272160,
  "arrays_found": [
    {"path": "artists", "count": 3},
    {"path": "tracks", "count": 6},
    {"path": "videos", "count": 4}
  ],
  "expansion_formula": "3 × 6 × 4 = 72"
}

Notes:
- Only meaningful for JSON files
- Non-JSON files return is_complex: false
- JSON is "complex" if it has 2+ arrays AND estimated_rows > 100
```

#### Preview File
```
POST /api/preview
Content-Type: multipart/form-data

Parameters:
- file: File (required) - The file to preview
- page: int (optional, default: 1) - Page number (1-indexed)
- page_size: int (optional, default: 500, max: 100) - Rows per page
- export_mode: string (optional, default: "normal") - JSON export mode
  - "normal": Standard Cartesian product expansion
  - "multi_table": Multiple tables, one per array
  - "single_row": Arrays kept as JSON strings

Response:
{
  "columns": ["col1", "col2", ...],
  "rows": [["val1", "val2", ...], ...],
  "total_rows": 1500,
  "detected_type": "json",
  "current_page": 1,
  "total_pages": 15,
  "page_size": 100,
  "table_info": {"main": 1, "artists": 3, "tracks": 6},  // multi_table only
  "preview_table": "main"  // multi_table only
}

Errors:
- 400: Invalid file, unsupported format, or malformed content
```

#### Convert File
```
POST /api/convert
Content-Type: multipart/form-data

Parameters:
- file: File (required) - The file to convert
- output_format: string (required) - Target format (csv, xlsx, json)
- export_mode: string (optional, default: "normal") - JSON export mode
  - "normal": Standard Cartesian product expansion
  - "multi_table": Multiple tables (Excel: sheets, CSV: ZIP)
  - "single_row": Arrays kept as JSON strings

Response:
- Binary file download with appropriate Content-Type
- Content-Disposition header with filename
- For multi_table + CSV: Returns ZIP file (application/zip)

Errors:
- 400: Invalid file, unsupported conversion, or conversion failure
```

### 3.4 MIME Types

| Format | MIME Type |
|--------|-----------|
| JSON | application/json |
| CSV | text/csv |
| XLSX | application/vnd.openxmlformats-officedocument.spreadsheetml.sheet |
| XLS | application/vnd.ms-excel |

### 3.5 File Detection

Files are detected by:
1. **Magic bytes** (priority for binary formats):
   - XLSX: `PK\x03\x04` (ZIP format)
   - XLS: `\xd0\xcf\x11\xe0` (OLE format)
2. **Content analysis** (for text formats):
   - JSON: Valid JSON starting with `[` or `{`
   - CSV: Consistent delimiter pattern across lines
3. **File extension** (fallback)

### 3.6 Conversion Details

#### JSON → CSV
- Input: Array of objects or single object
- **Nested array expansion**: Arrays of objects expand via Cartesian product (denormalization)
  - Example: Object with 4 batters × 7 toppings = 28 rows
  - Scalar fields repeat in each row
  - Nested object keys use dot notation (e.g., `batters.batter.id`)
- **Safety limit**: MAX_EXPANDED_ROWS (10000) prevents memory issues
- First row = column names (JSON keys with dot notation for nested)
- Delimiter: comma

#### JSON → Excel
- Same processing as CSV
- Single sheet named "Data"

#### CSV → JSON
- First row treated as keys
- Each subsequent row becomes an object
- Output: Array of objects
- Auto-detects delimiter (comma, semicolon, tab)

#### Excel → JSON
- Reads first sheet only
- First row treated as keys
- Same output format as CSV → JSON

#### CSV → Excel
- Preserves data structure
- Single sheet named "Data"

#### Excel → CSV
- Reads first sheet
- Outputs with comma delimiter

---

## 4. Configuration

### 4.1 Current Settings (config.py)

| Setting | Value | Description |
|---------|-------|-------------|
| MAX_FILE_SIZE | 10 MB | Maximum upload file size |
| PREVIEW_ROWS | 500 | Default rows in preview |
| MAX_EXPANDED_ROWS | 10000 | Max rows from nested JSON expansion |
| COMPLEX_JSON_THRESHOLD | 100 | Threshold for complex JSON detection |
| ALLOWED_EXTENSIONS | .json, .csv, .xlsx, .xls | Accepted file types |

### 4.2 CORS Origins (Development)

```
http://localhost:8000
http://localhost:3000
http://127.0.0.1:8000
http://localhost:63342  (JetBrains IDE)
http://127.0.0.1:63342
http://localhost:5500   (VS Code Live Server)
http://127.0.0.1:5500
```

---

## 5. Error Handling

### 5.1 Validation Errors

| Error | Message |
|-------|---------|
| File too large | "File too large. Maximum size is 10MB." |
| Empty file | "File is empty." |
| Invalid extension | "Invalid file type. Allowed types: .csv, .json, .xls, .xlsx" |
| Undetectable type | "Could not detect file type" |
| Invalid conversion | "Cannot convert {type} to {format}. Allowed: {options}" |

### 5.2 Format-Specific Errors

| Format | Error Details |
|--------|---------------|
| JSON | Line and column number of syntax errors |
| CSV | Encoding issues, parsing errors with row context |
| Excel | Corruption, password protection, wrong format |

---

## 6. Security Specifications

### 6.1 Deployment Context

| Aspect | Configuration |
|--------|---------------|
| Environment | Cloud PaaS (Railway/Render/Fly.io) |
| Security Level | Comprehensive |
| Access Scope | Fully public |

**Note:** Cloud PaaS provides baseline security (HTTPS termination, basic DDoS protection). Application-level security implemented below.

### 6.2 Security Measures Summary

| Category | Measure | Status | Priority |
|----------|---------|--------|----------|
| Input Validation | File size limit (10MB) | ✅ Implemented | P0 |
| Input Validation | Extension allowlist | ✅ Implemented | P0 |
| Input Validation | Magic byte detection | ✅ Implemented | P0 |
| Input Validation | Empty file rejection | ✅ Implemented | P0 |
| Input Validation | Filename sanitization | ✅ Implemented | P0 |
| Headers | Security headers middleware | ✅ Implemented | P0 |
| Headers | Production CORS | ✅ Implemented | P0 |
| Rate Limiting | Request throttling | 🔲 Planned | P1 |
| DoS Protection | Request timeouts | 🔲 Planned | P1 |
| DoS Protection | ZIP bomb protection | 🔲 Planned | P1 |

### 6.3 Input Validation

#### 6.3.1 File Size Limit
- **Limit:** 10 MB maximum
- **Enforcement:** Checked before processing
- **Response:** HTTP 400 with clear error message

#### 6.3.2 File Type Validation
- **Allowed extensions:** .json, .csv, .xlsx, .xls
- **Content detection:** Magic bytes for binary formats, content analysis for text
- **Dual validation:** Extension AND content must match expected types

#### 6.3.3 Filename Sanitization
**Requirement:** Sanitize filenames in Content-Disposition headers to prevent header injection.

**Implementation:**
- Remove or replace characters: `\r`, `\n`, `"`, `\`, `/`, `\0`
- Limit filename length to 255 characters
- Use RFC 5987 encoding for non-ASCII characters
- Fallback to generic name if sanitization fails

**Example:**
```
Input:  "file\nX-Injected: evil.csv"
Output: "file_X-Injected_evil.csv"
```

### 6.4 Security Headers

All responses must include the following headers:

| Header | Value | Purpose |
|--------|-------|---------|
| X-Content-Type-Options | nosniff | Prevent MIME-type sniffing |
| X-Frame-Options | DENY | Prevent clickjacking |
| X-XSS-Protection | 1; mode=block | XSS filter (legacy browsers) |
| Referrer-Policy | strict-origin-when-cross-origin | Limit referrer information |
| Permissions-Policy | geolocation=(), microphone=(), camera=() | Disable unnecessary APIs |

**Content-Security-Policy (for HTML responses):**
```
default-src 'self';
script-src 'self';
style-src 'self' 'unsafe-inline';
img-src 'self' data:;
font-src 'self';
connect-src 'self';
frame-ancestors 'none';
base-uri 'self';
form-action 'self';
```

### 6.5 CORS Configuration

#### Development
```python
CORS_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    # IDE origins...
]
```

#### Production
```python
CORS_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
# Or use environment variable: ALLOWED_ORIGINS
```

**Configuration:**
- `allow_credentials`: False (no cookies needed)
- `allow_methods`: ["GET", "POST", "OPTIONS"]
- `allow_headers`: ["Content-Type"]

### 6.6 Rate Limiting

**Strategy:** Token bucket algorithm using slowapi (built on limits library)

| Endpoint | Limit | Window | Scope |
|----------|-------|--------|-------|
| /api/preview | 30 requests | 1 minute | Per IP |
| /api/convert | 20 requests | 1 minute | Per IP |
| /api/health | 60 requests | 1 minute | Per IP |
| Global | 100 requests | 1 minute | Per IP |

**Responses:**
- HTTP 429 Too Many Requests
- `Retry-After` header with seconds until reset
- JSON body: `{"detail": "Rate limit exceeded. Try again in X seconds."}`

**Headers (informational):**
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp of reset

### 6.7 Request Timeouts

| Operation | Timeout | Rationale |
|-----------|---------|-----------|
| File upload | 30 seconds | Large files on slow connections |
| File processing | 60 seconds | Complex conversions |
| Total request | 120 seconds | Maximum total time |

**Implementation:** Uvicorn timeout configuration + application-level timeout middleware

### 6.8 ZIP Bomb Protection (XLSX Files)

XLSX files are ZIP archives that could contain malicious compression ratios.

**Protections:**
1. **Compression ratio limit:** Max 100:1 (10MB file = max 1GB uncompressed)
2. **Entry count limit:** Max 1000 files in archive
3. **Individual entry size limit:** 100MB per entry
4. **Total uncompressed limit:** 500MB total

**Implementation:** Validate ZIP structure before passing to openpyxl

### 6.9 Data Handling

#### No Data Retention
- Files processed entirely in memory
- No temporary files written to disk
- No caching of user data
- Converted content returned immediately and discarded

#### Memory Limits
- Maximum file size (10MB) limits memory usage
- Single file processing (no concurrent file accumulation)
- Garbage collection after each request

### 6.10 Error Handling Security

**Principles:**
- Never expose stack traces in production
- Generic error messages for unexpected errors
- Specific messages only for validation errors
- Log detailed errors server-side only

**Production error response:**
```json
{
  "detail": "An error occurred processing your file. Please try again."
}
```

### 6.11 Logging (Informational)

**What to log:**
- Rate limit violations (IP, endpoint, timestamp)
- File validation failures (type, size, reason)
- Conversion errors (input type, output type, error category)

**What NOT to log:**
- File contents
- Full file names (truncate to 50 chars)
- IP addresses in GDPR regions (configurable)

### 6.12 Security Checklist

Pre-deployment security verification:

- [x] Filename sanitization implemented and tested
- [x] Security headers middleware active
- [x] Production CORS origins configured (via ALLOWED_ORIGINS env var)
- [ ] Rate limiting enabled (P1 - planned)
- [ ] Request timeouts configured (P1 - planned)
- [ ] ZIP bomb protection active (P1 - planned)
- [ ] Error messages reviewed (no stack traces)
- [ ] HTTPS enforced (platform level)
- [ ] Dependencies scanned for vulnerabilities

---

## 7. Testing Specifications

### 7.1 Test Coverage

- **Unit tests:** Each converter has dedicated tests
- **API tests:** Endpoint integration tests
- **Security tests:** Filename sanitization, security headers
- **Current status:** 78 tests passing

### 7.2 Test Files

Sample files in `tests/sample_files/`:
- simple.json, nested.json, nested2.json, nested3.json
- simple.csv
- simple.xlsx

---

## 8. Deployment Specifications

### 8.1 Requirements

- Python 3.13+
- uv package manager
- HTTPS certificate (production)

### 8.2 Recommended Platform

Railway (or alternatives: Render, Fly.io)

### 8.3 Environment Variables (Production)

```
ENVIRONMENT=production
MAX_FILE_SIZE_MB=10
ALLOWED_ORIGINS=https://yourdomain.com
```

---

## 9. Future Roadmap Reference

See `doc/ROADMAP.md` for planned features:
- Phase 1: More conversions (JSONL, TSV, delimiters)
- Phase 2: SQL generator
- Phase 3: Data cleaning
- Phase 4: Advanced operations
- Phase 5: Public API
- Phase 6: Integrations

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2025-01 | Initial specifications document |
| 0.1.1 | 2026-01 | Added raw editor for malformed JSON/CSV files |
| 0.1.2 | 2026-01 | Added smart JSON handling with export modes and /api/analyze endpoint |
| 0.1.3 | 2026-01 | Simplified complex JSON UX: info screen + tabbed preview instead of selection dialog |