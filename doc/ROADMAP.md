# ParserWiz — General Roadmap

## Vision
Web tool for conversion, cleaning, and manipulation of tabular data (JSON, CSV, Excel). Start simple, grow with features that deliver real value.

---

## Phase 0 — MVP (Complete)
**Goal:** Minimum functional product to validate demand.

### Core Conversions
- [x] JSON → CSV
- [x] JSON → Excel (.xlsx)
- [x] CSV → JSON
- [x] CSV → Excel (.xlsx)
- [x] Excel → JSON
- [x] Excel → CSV

### Features
- [x] Data preview with pagination
- [x] Nested JSON array expansion (Cartesian product)
- [x] Smart JSON handling (multi-table export, single-row export)
- [x] Raw editor for malformed files
- [x] Basic and functional UI
- [x] Privacy disclaimer
- [x] Feedback form (Discord webhook)

### Security (P0)
- [x] Filename sanitization
- [x] Security headers middleware
- [x] Production CORS configuration

**Status:** Complete. 78 tests passing. Deployed pending.

---

## Phase 1 — Consolidate Conversions (Current)
**Goal:** Expand transformations, cover more use cases, security hardening.

See `doc/PHASE1.md` for detailed specifications.

### JSON Transformations (New)
- [ ] Flatten JSON (nested → dot notation)
- [ ] Unflatten JSON (dot notation → nested)

### New Formats
- [ ] JSON Lines (.jsonl) read/write
- [ ] TSV (tab-separated) read/write
- [ ] Delimiter selector (comma, semicolon, tab, pipe)

### Security Hardening (P1)
- [ ] Rate limiting (slowapi)
- [ ] Request timeouts
- [ ] ZIP bomb protection for XLSX

### Carried from Phase 0
- [x] Nested JSON support (flatten structures)
- [x] .xls format (legacy Excel)
- [x] UX improvements: drag & drop, progress bar
- [x] User-friendly error handling

---

## Phase 2 — SQL Generator
**Goal:** Attract technical audience (developers, analysts).

- [ ] CSV/Excel → INSERT statements
- [ ] CSV/Excel → CREATE TABLE + INSERTs
- [ ] Dialect selector: MySQL, PostgreSQL, SQLite, SQL Server
- [ ] Automatic type detection (INT, VARCHAR, DATE, etc.)
- [ ] Option: include column names or not
- [ ] Copy to clipboard

---

## Phase 3 — Data Cleaning
**Goal:** Solve real problems, increase retention.

- [ ] Remove completely empty rows
- [ ] Remove duplicate rows
- [ ] Trim whitespace (leading, trailing, multiple)
- [ ] Standardize dates (detect source format → target format)
- [ ] Standardize text (UPPER, lower, Capitalize)
- [ ] Before/after preview for each operation
- [ ] Undo last operation

---

## Phase 4 — Advanced Operations
**Goal:** Differentiation, features that Excel doesn't do easily.

- [ ] Merge multiple files into one
- [ ] Compare two files (visual diff: added, deleted, modified rows)
- [ ] Split column (e.g., "full name" → "first name" + "last name")
- [ ] Merge columns
- [ ] Filter rows by simple condition
- [ ] Bulk rename columns
- [ ] Reorder columns with drag & drop

---

## Phase 5 — Public API
**Goal:** B2B monetization, automation.

- [ ] Documented REST API (OpenAPI/Swagger)
- [ ] Endpoints for all conversions
- [ ] API key authentication
- [ ] Rate limiting by plan
- [ ] Usage dashboard for users
- [ ] Plans: Free (100 req/day), Pro (10k req/day), Enterprise

---

## Phase 6 — Integrations (Future)
**Goal:** Expand ecosystem.

- [ ] Google Sheets integration (import/export)
- [ ] Webhooks (receive data → process → return)
- [ ] Zapier / Make integration
- [ ] CLI tool (npm/pip)
- [ ] VS Code extension
- [ ] Background processing for large files

---

## Monetization Model

| Phase | Strategy |
|-------|----------|
| 0-2 | 100% free. Priority: traction and SEO |
| 3+ | Size limit: 5MB free, more requires account |
| 4+ | Advanced features only for registered users |
| 5+ | Paid API: volume-based plans |
| 6+ | Enterprise plans with SLA |

---

## Key Metrics to Track

- Conversions performed per day
- Most used conversion types
- Average file size
- Return rate (users who come back)
- Traffic sources (SEO, direct, referral)
- Most frequent errors

---

## Development Principles

1. **Simplicity first** — Every feature must work without explanation
2. **Speed** — Conversions must be instant for small files
3. **Privacy** — Don't store user data longer than necessary
4. **Fast iteration** — Launch, measure, adjust
