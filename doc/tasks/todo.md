# Tasks

## Current Phase: Phase 1 — Consolidate Conversions

### Sprint: JSON Transformations (P0)

- [ ] Implement `flatten_json()` utility function
- [ ] Implement `unflatten_json()` utility function
- [ ] Create `/api/transform` endpoint
- [ ] Add transformation UI for JSON files
- [ ] Tests for flatten/unflatten

### Backlog: New Formats (P1)

- [ ] JSONL read support
- [ ] JSONL write support
- [ ] TSV read/write support
- [ ] Delimiter selector for CSV operations

### Backlog: Security Hardening (P1)

- [ ] Implement rate limiting with slowapi
- [ ] Implement request timeouts
- [ ] Implement ZIP bomb protection for XLSX

### Backlog: Deployment

- [ ] Deploy to Railway/Render/Fly.io
- [ ] Configure production HTTPS
- [ ] Add custom domain

---

## Phase 0 Summary (Complete)

Phase 0 (MVP) completed January 2026 with 91 tests passing.

**Delivered:**
- All 6 core conversions (JSON, CSV, Excel bidirectional)
- Data preview with pagination
- Nested JSON handling (Cartesian expansion, multi-table, single-row)
- Raw editor for malformed files
- Smart JSON complexity detection
- Security: filename sanitization, headers, CORS
- Privacy disclaimer and feedback form
- Responsive UI
- PWA support (installable on mobile devices)

See `doc/PHASE0.md` for full details.
