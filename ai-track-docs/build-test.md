# Build & Test Reference

Instructions for running the course tooling and the Python sample application locally.

---

## Prerequisites

| Tool | Minimum version | Install |
|------|----------------|---------|
| Python | 3.10 | [python.org](https://python.org) |
| Node.js | 18 LTS | [nodejs.org](https://nodejs.org) |
| npm | bundled with Node | — |
| pytest | latest | `pip install pytest` |
| GitHub CLI (`gh`) | 2.40+ | `brew install gh` / [cli.github.com](https://cli.github.com) |

---

## Course Tooling (npm)

The root `package.json` drives demo generation and chapter header automation.

```bash
# Install dependencies
npm install

# Full release build (generates demo GIFs from .tape files)
npm run release

# CI-only build (chapter headers only, no VHS required)
npm run release:ci
```

### Individual scripts

| Script | What it does |
|--------|-------------|
| `npm run generate:headers` | Generates chapter banner images |
| `npm run scan:demos` | Lists all `.tape` files found in chapter `images/` dirs |
| `npm run create:tapes` | Scaffolds missing tape files |
| `npm run generate:vhs` | Runs VHS to render `.tape` → `.gif` |
| `npm run verify:gifs` | Confirms all expected GIFs were produced |

> **Note:** `npm run generate:vhs` requires [VHS](https://github.com/charmbracelet/vhs) to be installed (`brew install vhs`).

---

## Python Sample App (`samples/book-app-project/`)

### Setup

```bash
cd samples/book-app-project
pip install -e ".[dev]"        # install the package + dev extras
# or, if pyproject.toml has no extras:
pip install pytest
```

### Run the app

```bash
python book_app.py
```

### Run tests

```bash
# From the sample root
pytest tests/

# Verbose output
pytest tests/ -v

# Single test file
pytest tests/test_books.py -v
```

### Test file conventions

- Test files live in `samples/book-app-project/tests/`.
- File names follow the `test_*.py` pattern.
- Fixtures and helpers stay in `conftest.py` (create if needed).

### Current tests (`tests/test_books.py`)

| Test | Module | What it verifies |
|------|--------|-----------------|
| `test_add_book` | `BookCollection` | A new book is appended and its fields are correct |
| `test_mark_book_as_read` | `BookCollection` | `mark_as_read` sets `read=True` for an existing book |
| `test_mark_book_as_read_invalid` | `BookCollection` | `mark_as_read` returns `False` for an unknown title |
| `test_remove_book` | `BookCollection` | `remove_book` deletes an existing book and returns `True` |
| `test_remove_book_invalid` | `BookCollection` | `remove_book` returns `False` for an unknown title |
| `test_find_by_author_returns_only_matching_books` | `BookCollection` | `find_by_author` returns only books matching the given author (added 2026-05-05) |

All tests use the `use_temp_data_file` autouse fixture, which redirects `DATA_FILE` to a temporary path so tests are fully isolated and deterministic.

---

## C# Sample App (`samples/book-app-project-cs/`)

```bash
cd samples/book-app-project-cs
dotnet build
dotnet test Tests/
```

## JavaScript Sample App (`samples/book-app-project-js/`)

```bash
cd samples/book-app-project-js
npm install
npm test
```

---

## Intentional Bug Samples

The following directories contain **deliberate bugs** used in course exercises. Do **not** run tests against them expecting them to pass, and do **not** fix them:

- `samples/book-app-buggy/`
- `samples/buggy-code/`

---

## CI

### Python tests (GitHub Actions)

**Workflow:** [`.github/workflows/python-tests.yml`](../.github/workflows/python-tests.yml)

Triggers on every push or pull request that touches `samples/book-app-project/**`
or the workflow file itself.  Also runnable manually via **Actions → Python Tests
→ Run workflow**.

| Matrix | Value |
|--------|-------|
| Runners | `ubuntu-latest` |
| Python versions | 3.10, 3.11, 3.12, 3.13 |
| Command | `pytest tests/ -v --tb=short` |

The workflow installs only `pytest>=9.0,<10` — no VHS or Node required — so it
completes in under 30 seconds.

### Course asset generation (existing workflow)

The `generate-demos.yml.bak` workflow runs `npm run release:ci` (chapter
headers).  Full demo GIF generation is performed locally by maintainers before
release.  See [CONTRIBUTING.md](../CONTRIBUTING.md) for the release checklist.

---

## Local Test Script

[`scripts/run-tests.sh`](../scripts/run-tests.sh) provides a single-command way to
run the full Python test suite without manually managing a virtual environment.

```bash
# Run all tests (creates .venv automatically if missing)
bash scripts/run-tests.sh

# Verbose output
bash scripts/run-tests.sh -v

# Filter by keyword
bash scripts/run-tests.sh -k add_book

# Any extra argument is forwarded to pytest
bash scripts/run-tests.sh --tb=long -x
```

The script:
1. Checks that Python 3.10+ is on `PATH`.
2. Creates `samples/book-app-project/.venv` if it does not already exist.
3. Installs `pytest>=9.0,<10` into the venv.
4. Runs `pytest tests/` from inside `samples/book-app-project/`, forwarding
   any arguments you pass.
