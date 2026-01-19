# Technical Stack — ParserWiz

## Summary

| Layer | Technology |
|-------|------------|
| Backend | Python 3.13+ / FastAPI |
| Frontend | HTML + CSS + Vanilla JS |
| Data Processing | pandas, openpyxl, xlrd |
| Package Manager | uv |
| Deploy | Railway / Render / Fly.io |
| Version Control | Git + GitHub |

---

## Backend

### Framework: FastAPI
- Async by default
- Automatic validation with Pydantic
- Auto-generated OpenAPI documentation
- Excellent performance

### Main Dependencies

```toml
# pyproject.toml

[project]
name = "data-toolkit"
version = "0.1.0"
description = "Web tool for conversion, cleaning, and manipulation of tabular data"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "python-multipart>=0.0.6",
    "pandas>=2.2.0",
    "openpyxl>=3.1.2",
    "xlrd>=2.0.1",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.26.0",
    "ruff>=0.2.0",
]
```

### Library Justification

| Library | Purpose |
|---------|---------|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `python-multipart` | File upload handling |
| `pandas` | CSV read/write, data manipulation |
| `openpyxl` | Excel read/write (.xlsx) |
| `xlrd` | Legacy Excel read (.xls) |

### Backend Structure

```
backend/
├── main.py                 # FastAPI app, main routes
├── config.py               # Configuration (max sizes, env detection, CORS)
├── converters/
│   ├── __init__.py
│   ├── base.py             # Base converter class
│   ├── json_to_csv.py
│   ├── json_to_excel.py
│   ├── csv_to_json.py
│   ├── csv_to_excel.py
│   ├── excel_to_json.py
│   └── excel_to_csv.py
└── utils/
    ├── __init__.py
    ├── file_detection.py   # Detect file type
    ├── validators.py       # Validate JSON, etc.
    └── security.py         # Security headers, filename sanitization
```

---

## Frontend

### Approach: Vanilla JS (no frameworks)

**Reasons:**
- Fast MVP without build tools setup
- Instant load (no bundle)
- Sufficient for initial functionality
- Easy to migrate to React/Vue later if needed

### Structure

```
frontend/
├── index.html      # Single page
├── styles.css      # Styles (or Tailwind CDN)
└── app.js          # Application logic
```

### Optional CDN Libraries

```html
<!-- Tailwind CSS (optional, for quick styling) -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- PapaParse (if you want to parse CSV in frontend) -->
<script src="https://unpkg.com/papaparse@5.4.1/papaparse.min.js"></script>
```

---

## API Design

### Main Endpoints

```
POST /api/convert
  - Input: file (multipart), output_format (string)
  - Output: converted file

POST /api/preview
  - Input: file (multipart)
  - Output: JSON with data preview

GET /api/health
  - Output: { "status": "ok" }
```

### Supported Formats (Phase 0)

| Input | Available Outputs |
|-------|-------------------|
| .json | .csv, .xlsx |
| .csv  | .json, .xlsx |
| .xlsx | .json, .csv |
| .xls  | .json, .csv |

### MIME Types

```python
MIME_TYPES = {
    "json": "application/json",
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xls": "application/vnd.ms-excel"
}
```

---

## Deploy

### Recommended Option: Railway

**Pros:**
- Generous free tier to start
- Automatic deploy from GitHub
- Easy configuration
- Native Python support

**Configuration:**
```toml
# railway.toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uv run uvicorn backend.main:app --host 0.0.0.0 --port $PORT"
```

> Note: Railway auto-detects `pyproject.toml` and installs uv. If issues arise, add a `nixpacks.toml`:
> ```toml
> [phases.setup]
> cmds = ["curl -LsSf https://astral.sh/uv/install.sh | sh"]
> ```

### Alternatives

| Platform | Pros | Cons |
|----------|------|------|
| Render | Simple, free tier | Cold starts on free |
| Fly.io | Fast, edge locations | More configuration |
| Vercel | Excellent for frontend | Limited backend |
| DigitalOcean App Platform | Predictable | Costs from the start |

---

## Local Development

### Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with Homebrew
brew install uv
```

### Initial Setup

```bash
# Clone repo
git clone <repo-url>
cd parserwiz

# Initialize project with uv (creates pyproject.toml)
uv init

# Add dependencies
uv add fastapi "uvicorn[standard]" python-multipart pandas openpyxl xlrd

# Add dev dependencies
uv add --dev pytest pytest-asyncio httpx ruff

# Run server (uv auto-creates venv and syncs deps)
uv run uvicorn backend.main:app --reload --port 8000
```

### uv Commands Cheatsheet

```bash
# Add a package
uv add <package>

# Add dev dependency
uv add --dev <package>

# Remove a package
uv remove <package>

# Sync dependencies (install from pyproject.toml)
uv sync

# Run a command in the virtual environment
uv run <command>

# Run Python directly
uv run python script.py

# Update all dependencies
uv lock --upgrade
```

### Environment Variables

```bash
# .env (development)
ENVIRONMENT=development
MAX_FILE_SIZE_MB=10
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

---

## Testing

### Framework: pytest

Dev dependencies are already defined in `pyproject.toml` under `[tool.uv.dev-dependencies]`.

```bash
# Install dev dependencies
uv sync

# Run tests
uv run pytest tests/ -v

# Run tests with coverage
uv run pytest tests/ -v --cov=backend
```

### Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── test_json_to_csv.py
├── test_json_to_excel.py
├── test_csv_to_json.py
├── test_excel_to_json.py
├── test_api.py           # Endpoint tests
├── test_security.py      # Security tests (headers, sanitization)
└── sample_files/
    ├── simple.json
    ├── nested.json
    ├── simple.csv
    └── simple.xlsx
```

### Run Tests

```bash
pytest tests/ -v
```

---

## Code Conventions

### Python
- Formatter: `ruff format`
- Linter: `ruff check`
- Type hints: Yes, always use them
- Docstrings: Google style

### JavaScript
- No semicolons (modern style)
- `const` by default, `let` when necessary
- Descriptive names

### Git
- Commits in English
- Format: `type: short description`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

```bash
# Examples
feat: add JSON to CSV converter
fix: handle empty files gracefully
docs: update API documentation
```

---

## Security (Implemented P0)

- [x] Validate file type (magic bytes + content analysis)
- [x] Limit file size (10MB, configurable via MAX_FILE_SIZE_MB)
- [x] Don't store files after conversion (in-memory only)
- [x] Sanitize filename in download (header injection prevention)
- [x] CORS configured correctly (env-based for production)
- [x] Security headers (X-Frame-Options, CSP, X-Content-Type-Options)
- [ ] Basic rate limiting (P1 - planned)
- [ ] Request timeouts (P1 - planned)
- [ ] ZIP bomb protection (P1 - planned)

See `doc/SPECIFICATIONS.md` Section 6 for full security specifications.

---

## Monitoring (Future)

| Tool | Purpose |
|------|---------|
| Plausible / Umami | Privacy-focused analytics |
| Sentry | Error tracking |
| UptimeRobot | Uptime monitoring |

---

## Useful Commands for Claude Code

```bash
# Create initial project structure
mkdir -p backend/converters backend/utils frontend tests/sample_files

# Initialize project with uv
uv init

# Add all dependencies at once
uv add fastapi "uvicorn[standard]" python-multipart pandas openpyxl xlrd

# Add dev dependencies
uv add --dev pytest pytest-asyncio httpx ruff

# Run server in development
uv run uvicorn backend.main:app --reload

# Run tests
uv run pytest tests/ -v

# Format code
uv run ruff format backend/

# Lint
uv run ruff check backend/

# Lint and fix
uv run ruff check backend/ --fix
```
