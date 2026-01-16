# Phase 1 — Consolidate Conversions

## Goal
Expand conversion capabilities, improve data transformation options, and add security hardening. Focus on features that solve real user problems like round-tripping data between formats.

---

## Status: In Progress

Started: January 2026

---

## Features

### 1. JSON Structure Transformations (Priority: P0)

#### 1.1 Flatten JSON
Convert nested JSON structures to flat key-value pairs suitable for CSV/tabular formats.

**Input:**
```json
{
  "id": 1,
  "user": {
    "name": "John",
    "address": {
      "city": "NYC"
    }
  },
  "tags": ["a", "b"]
}
```

**Output:**
```json
{
  "id": 1,
  "user.name": "John",
  "user.address.city": "NYC",
  "tags": "[\"a\", \"b\"]"
}
```

**Rules:**
- Nested objects → dot notation keys (`user.address.city`)
- Arrays → JSON string representation
- Primitive values remain unchanged

**Use case:** Prepare complex JSON for CSV export with predictable structure.

#### 1.2 Unflatten JSON
Restore nested JSON structures from flattened data (CSV → original JSON).

**Input:**
```json
{
  "id": 1,
  "user.name": "John",
  "user.address.city": "NYC",
  "tags": "[\"a\", \"b\"]"
}
```

**Output:**
```json
{
  "id": 1,
  "user": {
    "name": "John",
    "address": {
      "city": "NYC"
    }
  },
  "tags": ["a", "b"]
}
```

**Rules:**
- Split keys on `.` to rebuild nested structure
- Detect and parse JSON strings (starts with `[` or `{`)
- Handle edge cases: escaped dots, array indices

**Use case:** Restore original JSON structure after CSV round-trip.

#### 1.3 Implementation Notes

**Backend:**
- New utility: `backend/utils/json_transform.py`
  - `flatten_json(data: dict, separator: str = ".") -> dict`
  - `unflatten_json(data: dict, separator: str = ".") -> dict`
- New converter: `backend/converters/json_transform.py`
- New API endpoint: `POST /api/transform`
  - Parameters: `file`, `operation` (flatten/unflatten)

**Frontend:**
- Add transformation options when JSON is uploaded
- Preview shows before/after comparison
- Download transformed JSON

**Edge cases to handle:**
1. Keys containing dots (e.g., `"user.name"` as literal key)
   - Solution: Optional escape character or alternate separator
2. Array indices in paths (e.g., `tags.0`, `tags.1`)
   - Solution: Support `[0]` notation or keep arrays as JSON strings
3. Empty objects/arrays
4. Mixed types at same path level

---

### 2. New File Formats (Priority: P1)

#### 2.1 JSON Lines (.jsonl)
- One JSON object per line
- Common for streaming data, logs, ML datasets

**Read:** Parse each line as separate JSON object
**Write:** Output one object per line, no array wrapper

#### 2.2 TSV (Tab-Separated Values)
- Same as CSV but with tab delimiter
- Common for spreadsheet copy-paste

---

### 3. Delimiter Options (Priority: P1)

Add delimiter selector for CSV operations:
- Comma (default)
- Semicolon (European standard)
- Tab
- Pipe (`|`)

**UI:** Dropdown in conversion options when CSV is involved.

---

### 4. Security Hardening (Priority: P1)

Carry over from Phase 0 backlog:

#### 4.1 Rate Limiting
- 30 req/min for /api/preview
- 20 req/min for /api/convert
- 60 req/min for /api/health
- Use slowapi library

#### 4.2 Request Timeouts
- File upload: 30 seconds
- File processing: 60 seconds
- Total request: 120 seconds

#### 4.3 ZIP Bomb Protection (XLSX)
- Max compression ratio: 100:1
- Max entries: 1000 files
- Max individual entry: 100MB
- Max total uncompressed: 500MB

---

## API Changes

### New Endpoint: POST /api/transform

Transform JSON structure without format conversion.

**Request:**
```
POST /api/transform
Content-Type: multipart/form-data

Parameters:
- file: File (required) - JSON file to transform
- operation: string (required) - "flatten" or "unflatten"
- separator: string (optional, default: ".") - Key separator
```

**Response:**
```json
{
  "success": true,
  "data": { /* transformed JSON */ },
  "original_keys": 15,
  "transformed_keys": 42
}
```

Or direct file download if `?download=true` query param.

---

## Development Tasks

### Backend
- [ ] Implement `flatten_json()` utility function
- [ ] Implement `unflatten_json()` utility function
- [ ] Create `/api/transform` endpoint
- [ ] Add JSONL read support
- [ ] Add JSONL write support
- [ ] Add TSV support (read/write)
- [ ] Add delimiter selection to CSV converters
- [ ] Implement rate limiting with slowapi
- [ ] Implement request timeouts
- [ ] Implement ZIP bomb protection
- [ ] Tests for all new features

### Frontend
- [ ] Add "Transform JSON" option for JSON files
- [ ] Before/after preview for transformations
- [ ] Delimiter selector dropdown
- [ ] JSONL format support in UI
- [ ] Rate limit error handling (429 responses)

### Documentation
- [ ] Update SPECIFICATIONS.md with new endpoints
- [ ] Update CLAUDE.md with new features
- [ ] Add transformation examples to user guide

---

## "Done" Criteria for Phase 1

- [ ] I can flatten a nested JSON to dot-notation keys
- [ ] I can unflatten a CSV-exported JSON back to nested structure
- [ ] I can upload/download JSONL files
- [ ] I can choose CSV delimiter (comma, semicolon, tab, pipe)
- [ ] Rate limiting is active in production
- [ ] ZIP bomb protection is active for XLSX files
- [ ] All features have tests

---

## Out of Scope (Phase 1)

- SQL generation (Phase 2)
- Data cleaning operations (Phase 3)
- Multiple file operations (Phase 4)
- User registration/authentication
- API keys

---

## Technical Decisions

### Flatten/Unflatten Separator
Default: `.` (dot)

Rationale: Most common convention, matches pandas `json_normalize()` behavior.

Alternative considered: `__` (double underscore) - less ambiguous but less readable.

### JSON String Detection for Unflatten
Heuristic approach:
1. Check if string starts with `[` or `{`
2. Attempt `json.loads()`
3. If parse succeeds → use parsed value
4. If parse fails → keep as string

This handles 99% of cases from our own flatten output.

### Array Handling in Flatten
Keep arrays as JSON strings rather than indexed keys.

Rationale:
- Simpler round-trip (flatten → unflatten)
- Matches Phase 0 behavior
- Avoids sparse columns for variable-length arrays

---

## Dependencies

No new dependencies required. Existing stack sufficient:
- `json` (stdlib) - JSON parsing
- `pandas` - CSV/Excel handling
- `fastapi` - API framework

For rate limiting (when implemented):
- `slowapi` - Rate limiting middleware

---

## References

- Phase 0 completion: `doc/PHASE0.md`
- Full roadmap: `doc/ROADMAP.md`
- Technical specs: `doc/SPECIFICATIONS.md`