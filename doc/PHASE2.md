# Phase 2 — SQL Generator

## Goal
Add SQL generation capabilities to attract technical users (developers, DBAs, data analysts). Convert tabular data (CSV/Excel) into ready-to-use SQL statements for database imports.

---

## Status: Not Started

Target: Q1 2026

---

## Features

### 1. SQL INSERT Generation (Priority: P0)

Generate INSERT statements from tabular data.

**Input (CSV/Excel):**
| id | name | email | age |
|----|------|-------|-----|
| 1 | John | john@example.com | 28 |
| 2 | Jane | jane@example.com | 32 |

**Output:**
```sql
INSERT INTO users (id, name, email, age) VALUES (1, 'John', 'john@example.com', 28);
INSERT INTO users (id, name, email, age) VALUES (2, 'Jane', 'jane@example.com', 32);
```

**Options:**
- Table name (required, user input)
- Include column names (default: true)
- Batch size for multi-row INSERT (default: 1 row per statement)

---

### 2. CREATE TABLE Generation (Priority: P0)

Generate CREATE TABLE statement with automatic type inference.

**Output:**
```sql
CREATE TABLE users (
    id INTEGER,
    name VARCHAR(255),
    email VARCHAR(255),
    age INTEGER
);
```

**Type Inference Rules:**
| Data Pattern | SQL Type |
|--------------|----------|
| Integer numbers only | INTEGER |
| Decimal numbers | DECIMAL(10,2) |
| Boolean (true/false, 1/0) | BOOLEAN |
| ISO date (YYYY-MM-DD) | DATE |
| ISO datetime (YYYY-MM-DDTHH:MM:SS) | TIMESTAMP |
| Text (default) | VARCHAR(255) |
| Text > 255 chars | TEXT |
| NULL/empty values | nullable column |

---

### 3. SQL Dialect Support (Priority: P0)

Support multiple SQL dialects with syntax variations.

| Dialect | String Quote | Identifier Quote | Type Differences |
|---------|--------------|------------------|------------------|
| MySQL | `'single'` | `` `backtick` `` | INT, VARCHAR, DATETIME |
| PostgreSQL | `'single'` | `"double"` | INTEGER, VARCHAR, TIMESTAMP |
| SQLite | `'single'` | `"double"` | INTEGER, TEXT, REAL |
| SQL Server | `'single'` | `[brackets]` | INT, NVARCHAR, DATETIME2 |

**UI:** Dropdown selector, default MySQL.

---

### 4. Output Options (Priority: P1)

#### 4.1 Output Mode
- **INSERT only** - Just INSERT statements
- **CREATE + INSERT** - CREATE TABLE followed by INSERT statements
- **CREATE only** - Just the table definition

#### 4.2 Batch INSERT (Multi-row)
For better performance on large datasets:

```sql
INSERT INTO users (id, name, email, age) VALUES
    (1, 'John', 'john@example.com', 28),
    (2, 'Jane', 'jane@example.com', 32),
    (3, 'Bob', 'bob@example.com', 45);
```

**Batch sizes:** 1 (default), 10, 50, 100, 500, 1000

#### 4.3 NULL Handling
- Empty cells → `NULL`
- String "NULL" → `NULL`
- Option to treat empty as empty string `''` instead

---

### 5. Copy to Clipboard (Priority: P1)

One-click copy of generated SQL to clipboard.

**UI:**
- "Copy SQL" button next to download
- Visual feedback (button text changes to "Copied!")
- Works for preview and full output

---

## API Changes

### New Endpoint: POST /api/generate-sql

Generate SQL from uploaded file.

**Request:**
```
POST /api/generate-sql
Content-Type: multipart/form-data

Parameters:
- file: File (required) - CSV or Excel file
- table_name: string (required) - Target table name
- dialect: string (optional, default: "mysql") - mysql, postgresql, sqlite, sqlserver
- mode: string (optional, default: "insert") - insert, create, create_insert
- batch_size: int (optional, default: 1) - Rows per INSERT statement
- include_columns: bool (optional, default: true) - Include column names in INSERT
- null_empty: bool (optional, default: true) - Treat empty cells as NULL
```

**Response:**
```json
{
  "success": true,
  "sql": "INSERT INTO users ...",
  "dialect": "mysql",
  "row_count": 150,
  "column_count": 4,
  "columns": [
    {"name": "id", "inferred_type": "INTEGER"},
    {"name": "name", "inferred_type": "VARCHAR(255)"},
    {"name": "email", "inferred_type": "VARCHAR(255)"},
    {"name": "age", "inferred_type": "INTEGER"}
  ]
}
```

### New Endpoint: POST /api/sql-preview

Preview first N rows as SQL without generating full output.

**Request:**
```
POST /api/sql-preview
Content-Type: multipart/form-data

Parameters:
- file: File (required)
- table_name: string (required)
- dialect: string (optional, default: "mysql")
- mode: string (optional, default: "insert")
- preview_rows: int (optional, default: 5, max: 20)
```

**Response:**
```json
{
  "success": true,
  "preview_sql": "CREATE TABLE users (...); INSERT INTO users ...",
  "total_rows": 1500,
  "columns": [...],
  "warnings": ["Column 'date' has mixed formats, using VARCHAR"]
}
```

---

## Backend Implementation

### New Files

```
backend/
├── generators/
│   ├── __init__.py
│   ├── base.py               # Base SQL generator class
│   ├── sql_generator.py      # Main generator logic
│   └── dialects/
│       ├── __init__.py
│       ├── mysql.py
│       ├── postgresql.py
│       ├── sqlite.py
│       └── sqlserver.py
└── utils/
    └── type_inference.py     # Column type detection
```

### Core Classes

```python
# backend/generators/base.py
class SQLDialect:
    """Base class for SQL dialects."""
    name: str
    string_quote: str = "'"
    identifier_quote: str = '"'

    def quote_identifier(self, name: str) -> str: ...
    def quote_string(self, value: str) -> str: ...
    def get_type(self, inferred_type: str) -> str: ...

# backend/generators/sql_generator.py
class SQLGenerator:
    """Generate SQL from tabular data."""

    def __init__(self, dialect: SQLDialect): ...
    def infer_types(self, df: pd.DataFrame) -> list[ColumnInfo]: ...
    def generate_create(self, table_name: str, columns: list) -> str: ...
    def generate_inserts(self, table_name: str, df: pd.DataFrame, batch_size: int) -> str: ...
```

### Type Inference Logic

```python
# backend/utils/type_inference.py
def infer_column_type(series: pd.Series) -> str:
    """
    Infer SQL type from pandas Series.

    Priority:
    1. Check for all nulls → VARCHAR(255) nullable
    2. Check for integers (no decimals)
    3. Check for floats/decimals
    4. Check for booleans
    5. Check for dates (ISO format)
    6. Check for datetimes
    7. Default to VARCHAR with max length detection
    """
```

---

## Frontend Implementation

### UI Flow

1. User uploads CSV/Excel file
2. Standard table preview shown
3. User clicks "Generate SQL" (new button alongside CSV/Excel options)
4. SQL Options panel appears:
   - Table name input (required)
   - Dialect dropdown
   - Output mode radio buttons
   - Advanced options (collapsible)
5. Click "Generate" shows SQL preview
6. User can:
   - Copy to clipboard
   - Download as .sql file
   - Adjust options and regenerate

### UI Mockup

```
┌─────────────────────────────────────────────────────────────┐
│  📄 data.csv (2.3 KB)                                       │
│                                                             │
│  Preview:                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ id  │ name  │ email              │ age             │   │
│  │ 1   │ John  │ john@example.com   │ 28              │   │
│  │ 2   │ Jane  │ jane@example.com   │ 32              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Convert to:  [CSV]  [Excel]  [JSON]  [SQL ▼]              │
│                                                             │
│  ┌─ SQL Options ────────────────────────────────────────┐  │
│  │                                                       │  │
│  │  Table name: [users____________]                      │  │
│  │                                                       │  │
│  │  Dialect:    [MySQL ▼]                                │  │
│  │                                                       │  │
│  │  Output:     ○ INSERT only                            │  │
│  │              ● CREATE TABLE + INSERT                  │  │
│  │              ○ CREATE TABLE only                      │  │
│  │                                                       │  │
│  │  ▶ Advanced options                                   │  │
│  │                                                       │  │
│  │  [Generate SQL]                                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─ Generated SQL ──────────────────────────────────────┐  │
│  │ CREATE TABLE users (                                  │  │
│  │     id INTEGER,                                       │  │
│  │     name VARCHAR(255),                                │  │
│  │     email VARCHAR(255),                               │  │
│  │     age INTEGER                                       │  │
│  │ );                                                    │  │
│  │                                                       │  │
│  │ INSERT INTO users (id, name, email, age) VALUES ...   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  [Copy SQL]  [Download .sql]                                │
│                                                             │
│  [Start Over]                                               │
└─────────────────────────────────────────────────────────────┘
```

### Advanced Options (Collapsed by Default)

- Batch size: [1 ▼] rows per INSERT
- Include column names: [✓]
- Treat empty as NULL: [✓]
- Quote identifiers: [✓] (for reserved words)

---

## Development Tasks

### Backend
- [ ] Create `backend/generators/` module structure
- [ ] Implement base `SQLDialect` class
- [ ] Implement MySQL dialect
- [ ] Implement PostgreSQL dialect
- [ ] Implement SQLite dialect
- [ ] Implement SQL Server dialect
- [ ] Implement `type_inference.py` utility
- [ ] Implement `SQLGenerator` class
- [ ] Create `/api/generate-sql` endpoint
- [ ] Create `/api/sql-preview` endpoint
- [ ] Add SQL escaping for special characters
- [ ] Add reserved word handling
- [ ] Tests for type inference (edge cases)
- [ ] Tests for each dialect
- [ ] Tests for API endpoints
- [ ] Tests for SQL injection prevention

### Frontend
- [ ] Add "SQL" button to conversion options
- [ ] Create SQL options panel component
- [ ] Table name input with validation
- [ ] Dialect selector dropdown
- [ ] Output mode radio buttons
- [ ] Advanced options collapsible section
- [ ] SQL preview display with syntax highlighting
- [ ] Copy to clipboard functionality
- [ ] Download as .sql file
- [ ] Loading states during generation
- [ ] Error handling for invalid table names

### Documentation
- [ ] Update SPEC.md with SQL endpoints
- [ ] Update CLAUDE.md with new commands
- [ ] Update ROADMAP.md to mark Phase 2 in progress
- [ ] Add SQL generation examples to user guide

---

## "Done" Criteria for Phase 2

- [ ] I can upload CSV and generate INSERT statements
- [ ] I can upload Excel and generate INSERT statements
- [ ] I can generate CREATE TABLE with inferred types
- [ ] I can select between MySQL, PostgreSQL, SQLite, SQL Server
- [ ] Generated SQL is valid and executable
- [ ] I can copy generated SQL to clipboard
- [ ] I can download SQL as .sql file
- [ ] Type inference correctly handles: integers, decimals, dates, booleans, text
- [ ] Reserved SQL words are properly quoted
- [ ] All features have tests (target: 95%+ coverage for generators)

---

## Out of Scope (Phase 2)

- UPDATE/DELETE statements
- ALTER TABLE statements
- Foreign key relationships
- Index generation
- Stored procedures
- Database connection/execution
- Schema import from existing database
- Data cleaning (Phase 3)
- Multiple file operations (Phase 4)

---

## Technical Decisions

### Type Inference Strategy
**Approach:** Sample-based inference with fallback to VARCHAR.

1. Sample up to 1000 rows for type detection
2. If >90% of non-null values match a type → use that type
3. If mixed types → fallback to VARCHAR/TEXT
4. Always allow NULL unless explicitly told otherwise

**Rationale:** Conservative approach prevents data loss. Users can always manually adjust types.

### Identifier Quoting
**Approach:** Quote all identifiers by default.

**Rationale:** Prevents issues with:
- Reserved words (ORDER, SELECT, TABLE)
- Spaces in column names
- Special characters
- Case sensitivity differences between dialects

### Batch INSERT Limits
**Max batch size:** 1000 rows

**Rationale:**
- MySQL: max_allowed_packet typically 16MB
- PostgreSQL: no hard limit but large statements are slower
- SQLite: SQLITE_MAX_COMPOUND_SELECT default 500
- Practical sweet spot for performance vs. readability

### SQL Injection Prevention
Even though we're generating SQL (not executing), we still escape values:
- Single quotes → doubled (`'` → `''`)
- Backslashes escaped for MySQL
- Null bytes removed

**Rationale:** Users may copy-paste into tools that execute directly.

---

## Edge Cases

### 1. Empty File
- Error: "File contains no data rows"

### 2. Column Names with Special Characters
- Quote identifiers: `[Column Name!]` or `` `Column Name!` ``
- Replace truly invalid characters with underscore

### 3. Very Long Text Values
- Infer as TEXT instead of VARCHAR
- Warn if > 65535 chars (MySQL TEXT limit)

### 4. Mixed Numeric Formats
- "1,234" vs "1.234" (thousands separator confusion)
- Default to VARCHAR, add warning

### 5. Date Format Ambiguity
- "01/02/03" → Could be Jan 2, Feb 1, or year 2003
- Only recognize unambiguous ISO format (YYYY-MM-DD)
- Otherwise treat as VARCHAR with warning

### 6. Boolean Detection
- Recognize: true/false, TRUE/FALSE, 1/0, yes/no, Y/N
- Must be consistent across column

### 7. Reserved Words as Column Names
- Always quote: SELECT, TABLE, ORDER, INDEX, KEY, etc.
- Maintain list per dialect

---

## Dependencies

Existing dependencies sufficient:
- `pandas` - Data handling
- `fastapi` - API framework

No new dependencies required.

---

## Security Considerations

### Input Validation
- Table name: alphanumeric + underscore only, max 64 chars
- Batch size: validated range 1-1000
- Dialect: whitelist validation

### Output Safety
- All string values properly escaped
- No direct database execution (output only)
- SQL comments stripped from output to prevent injection via data

---

## Performance Considerations

### Large Files
- Preview limited to first 20 rows
- Full generation streams output for files > 10MB
- Client-side: virtualized display for large SQL output

### Memory Usage
- Process in chunks of 10,000 rows
- Don't load entire SQL string in memory for large files

---

## SEO Integration

After Phase 2 completion:
- Create `/csv-to-sql` landing page
- Create `/excel-to-sql` landing page
- Target keywords: "csv to sql insert", "excel to sql generator online"
- Blog post: "How to Generate SQL INSERT Statements from Excel"

See `doc/SEO.md` for full SEO strategy.

---

## References

- Phase 0 (complete): `doc/PHASE0.md`
- Phase 1 (in progress): `doc/PHASE1.md`
- Full roadmap: `doc/ROADMAP.md`
- Technical specs: `doc/SPEC.md`
- SEO strategy: `doc/SEO.md`
