# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DataToolkit is a web tool for conversion, cleaning, and manipulation of tabular data (JSON, CSV, Excel). Currently in Phase 0 (MVP) focusing on basic file conversions.

## Tech Stack

- **Backend**: Python 3.13+ / FastAPI
- **Frontend**: HTML + CSS + Vanilla JS (no frameworks)
- **Data Processing**: pandas, openpyxl, xlrd
- **Package Manager**: uv

## Common Commands

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn backend.main:app --reload --port 8000

# Run tests
uv run pytest tests/ -v

# Run single test file
uv run pytest tests/test_json_to_csv.py -v

# Format code
uv run ruff format backend/

# Lint code
uv run ruff check backend/

# Lint and auto-fix
uv run ruff check backend/ --fix
```

## Architecture

### Backend Structure
```
backend/
├── main.py                 # FastAPI app, main routes
├── config.py               # Configuration (max sizes, etc.)
├── converters/
│   ├── base.py             # Base converter class
│   ├── json_to_csv.py
│   ├── json_to_excel.py
│   ├── csv_to_json.py
│   ├── csv_to_excel.py
│   ├── excel_to_json.py
│   └── excel_to_csv.py
└── utils/
    ├── file_detection.py   # Detect file type
    └── validators.py       # Validate JSON, etc.
```

### API Endpoints
- `POST /api/convert` - Convert file (multipart file + output_format string)
- `POST /api/preview` - Preview file data with pagination (page, page_size params)
- `GET /api/health` - Health check

### Supported Conversions (Phase 0)
| Input | Output |
|-------|--------|
| JSON  | CSV, XLSX |
| CSV   | JSON, XLSX |
| XLSX/XLS | JSON, CSV |

## Code Conventions

### Python
- Always use type hints
- Docstrings: Google style
- Formatter/Linter: ruff

### JavaScript
- No semicolons
- `const` by default, `let` when necessary

### Git Commits
Format: `type: short description`

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Documentation

See `doc/` folder for detailed specifications:
- `ROADMAP.md` - Project phases and feature roadmap
- `PHASE0.md` - Current MVP specifications
- `STACK.md` - Technical stack details and commands
- 
## General Guidelines

1. **Plan first**: Think through the problem, read relevant files, and write a plan to `tasks/todo.md`
2. **Verify plan**: Check in with the user before beginning implementation
3. **Track progress**: Mark todo items as complete as you go
4. **Explain changes**: Provide high-level explanations of what you changed
5. **Keep it simple**: Every change should be as simple as possible, impacting minimal code
6. **Maintain requirements**: Always keep documentation in sync with code changes