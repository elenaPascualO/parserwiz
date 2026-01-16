# Phase 0 — MVP DataToolkit

## Goal
Launch a functional MVP to validate real demand for a JSON ↔ CSV ↔ Excel conversion tool.

---

## MVP Features

### Supported Conversions

| Input | Output | Priority |
|-------|--------|----------|
| JSON | CSV | P0 |
| JSON | Excel (.xlsx) | P0 |
| CSV | JSON | P0 |
| Excel (.xlsx, .xls) | JSON | P1 |

### Characteristics

- [x] **File upload**: drag & drop or file selector button
- [x] **Data preview**: show rows in HTML table
- [x] **Direct download**: converted file ready to download
- [x] **No registration**: completely anonymous usage
- [x] **No initial limits**: any (reasonable) size for now

---

## Technical Specifications

### JSON → CSV
- Input: Valid JSON (array of objects or object with array)
- Flatten first level of nesting
- First row = column names (JSON keys)
- Default delimiter: comma

### JSON → Excel
- Same process as CSV but generating .xlsx
- Single sheet named "Data"

### CSV → JSON
- First row = JSON keys
- Each following row = one object
- Output: array of objects
- Auto-detect delimiter (comma, semicolon, tab)

### Excel → JSON
- Read first sheet of file
- First row = keys
- Same output as CSV → JSON

---

## MVP UI/UX

### Main Screen
```
┌─────────────────────────────────────────────┐
│  🔄 DataToolkit                             │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │                                     │   │
│  │   Drop your file here              │   │
│  │   JSON, CSV or Excel               │   │
│  │                                     │   │
│  │   [Select file]                    │   │
│  │                                     │   │
│  └─────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

### After File Upload
```
┌─────────────────────────────────────────────┐
│  📄 file.json (2.3 KB)                      │
│                                             │
│  Preview:                                   │
│  ┌─────────────────────────────────────┐   │
│  │ col1  │ col2   │ col3              │   │
│  │ val1  │ val2   │ val3              │   │
│  │ ...   │ ...    │ ...               │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Convert to:                                │
│  [CSV]  [Excel]                             │
│                                             │
│  [Upload another file]                      │
└─────────────────────────────────────────────┘
```

---

## File Structure

```
datatoolkit/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── converters/
│   │   ├── __init__.py
│   │   ├── json_to_csv.py
│   │   ├── json_to_excel.py
│   │   ├── csv_to_json.py
│   │   └── excel_to_json.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── file_detection.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── tests/
│   ├── test_converters.py
│   └── sample_files/
│       ├── sample.json
│       ├── sample.csv
│       └── sample.xlsx
├── README.md
├── ROADMAP.md
├── PHASE0.md
└── STACK.md
```

---

## API Endpoints

### POST /convert
Single endpoint for all conversions.

**Request:**
- `file`: file to convert (multipart/form-data)
- `output_format`: desired format (`csv`, `xlsx`, `json`)

**Response:**
- Converted file for download
- Appropriate Content-Type

### POST /preview
Get file preview without converting.

**Request:**
- `file`: file to preview

**Response:**
```json
{
  "columns": ["col1", "col2", "col3"],
  "rows": [
    ["val1", "val2", "val3"],
    ["val4", "val5", "val6"]
  ],
  "total_rows": 150,
  "detected_type": "json"
}
```

---

## Development Tasks

### Backend
- [x] Setup FastAPI project
- [x] Implement json_to_csv.py
- [x] Implement json_to_excel.py
- [x] Implement csv_to_json.py
- [x] Implement excel_to_json.py
- [x] Implement automatic file type detection
- [x] Implement /convert endpoint
- [x] Implement /preview endpoint
- [x] Basic tests for each converter (74 tests passing)
- [x] Error handling (invalid file, malformed JSON, etc.)

### Frontend
- [x] Basic HTML structure
- [x] Clean and minimalist CSS styles
- [x] JS: file drag & drop
- [x] JS: call /preview and display table
- [x] JS: call /convert and trigger download
- [x] Loading states (spinner)
- [x] User-friendly error messages

### DevOps
- [x] Setup Git repository
- [ ] Configure deploy on Railway/Render/Fly.io
- [ ] Domain (custom domain)
- [ ] HTTPS

---

## "Done" Criteria for Phase 0

- [x] I can upload a JSON and download CSV
- [x] I can upload a JSON and download Excel
- [x] I can upload a CSV and download JSON
- [x] I can upload an Excel and download JSON
- [x] I see a preview of my data before converting
- [ ] The web is deployed and publicly accessible
- [x] Works on mobile (basic responsive)
- [x] No obvious errors in console

---

## Out of Scope (Phase 0)

- User registration
- Size limits
- Multiple files at once
- Delimiter selection
- Advanced analytics
- Documented public API

---

## Improvements Completed

Issues identified during usage that have been addressed:

### Frontend / Preview

- [x] **Pagination for large files**: Added Previous/Next pagination controls with page indicator. Users can navigate through all data rows (10 per page by default, max 100).
- [x] **Preserve data exactly as in file**: Preview now reads all data as strings, preserving leading zeroes (e.g., "007" stays "007").
- [x] **Hover hint**: Added "💡 Hover over cells to view full content" message above preview tables
- [x] **Start Over button**: Renamed "Upload another file" to "Start Over" for clearer UX

### New Conversions

- [x] **CSV → Excel**: Convert CSV files to .xlsx format
- [x] **Excel → CSV**: Convert .xlsx/.xls files to CSV format

### Error Handling

- [x] **Show detailed errors for malformed files**: Improved error messages with specific details:
  - JSON: Shows line and column number of syntax errors
  - CSV: Explains encoding issues, parsing errors with row context
  - Excel: Explains if file is corrupted, password-protected, or wrong format

### Security (P0)

- [x] **Filename sanitization**: Prevents header injection via Content-Disposition
- [x] **Security headers middleware**: X-Frame-Options, X-Content-Type-Options, CSP
- [x] **Production CORS**: Environment-based CORS configuration
- [x] **Security tests**: 20 tests covering security features

See `doc/SPECIFICATIONS.md` for full security specifications.

### Nested JSON Support (January 2026)

- [x] **Nested array expansion**: JSON with nested arrays (like batters + toppings) now expands via Cartesian product
- [x] **Single object support**: Single objects with multiple nested arrays preserve all fields
- [x] **Safety limit**: MAX_EXPANDED_ROWS=10000 prevents memory issues from large expansions

### Raw Editor for Malformed Files (January 2026)

- [x] **Raw text editor**: When JSON or CSV files fail to parse, users see a raw text editor instead of an error toast
- [x] **Inline error display**: Parse error message shown above the editor with line/column info
- [x] **Line numbers**: Editor displays line numbers for easy error location
- [x] **Retry functionality**: Users can edit the content and retry parsing without re-uploading
- [x] **Seamless flow**: Once fixed, the file proceeds to the normal table preview

### Smart JSON Handling for Complex Structures (January 2026)

- [x] **Automatic complexity detection**: Analyzes JSON structure to detect multiple arrays that would cause Cartesian explosion
- [x] **Simplified UX flow**: When complex JSON detected (>100 estimated rows), shows info message with "Next" button
- [x] **`_record_id` explanation**: Info screen includes tip explaining the auto-generated column that links related records across tables
- [x] **Tabbed preview**: Users compare both export options side-by-side:
  - **Multi-file tab**: Preview of normalized tables (all collapsed by default)
  - **Single-file tab**: Preview with arrays as JSON text columns
- [x] **Multi-sheet Excel export**: Complex JSON exports to multiple sheets linked by `_record_id`
- [x] **Multi-CSV ZIP export**: Complex JSON exports to ZIP containing multiple CSV files
- [x] **New /api/analyze endpoint**: Pre-analyze JSON complexity before conversion
- [x] **Updated convert/preview**: Accept `export_mode` parameter (normal, multi_table, single_row)
