# Walk Track Backlog

Epic: **book-app-project — Quality, Performance, and Operability hardening**

This document captures 5 improvements identified during the walk track (ex-01→11).
Each item is scoped to one PR. When GitHub Issues are available, convert each item
to an issue and link it here.

---

## Epic Description

The walk track established a baseline of architecture docs, coverage, contract tests,
a micro-optimization, secret scanning, structured logging, and advisory CI. These
backlog items address gaps discovered during that work: remaining coverage holes,
a latent O(n) lookup, a schema-drift risk, missing log operability features, and
the absence of a blocking lint gate.

**Relevant code paths:**
- Domain: `samples/book-app-project/books.py`
- Tests: `samples/book-app-project/tests/test_books.py`, `tests/test_contract.py`
- Observability: `samples/book-app-project/logging_config.py`
- CI: `.github/workflows/walk-evidence.yml`
- Contract fixture: `samples/book-app-project/tests/fixtures/golden_book.json`

---

## Item 1 — Cover `books.py` error paths to reach 100%

**Type**: Test improvement  
**Priority**: High — these are real failure modes (corrupt data file, disk full)  
**Effort**: Small (1 PR, ~2 new tests)

**Background**  
`books.py` is at 88% (8 lines uncovered). The gaps are:
- Lines 31-35: `JSONDecodeError` branch in `load_books()` — triggered by a corrupt `data.json`
- Line 51: `OSError` path in `save_books()` — triggered by a disk-full or permission error
- Lines 83-84: `logger.info` in `remove_book()` not-found branch

**Acceptance criteria**
- [ ] A test triggers the `JSONDecodeError` branch by writing invalid JSON to `DATA_FILE` and confirms the collection starts empty and a warning is printed to stdout
- [ ] A test triggers the `save_books()` `OSError` path (e.g., by making the data file read-only or monkeypatching `open`)
- [ ] `books.py` coverage reaches 100%
- [ ] All existing 9 tests continue to pass

**Linked paths**: `samples/book-app-project/books.py` lines 31-35, 51, 83-84  
**Verification**: `.venv/bin/pytest --cov=books --cov-report=term-missing` → `books.py  100%`

---

## Item 2 — Replace O(n) title lookup with O(1) dict index

**Type**: Performance  
**Priority**: Medium — currently acceptable; matters at scale (>1000 books)  
**Effort**: Small (1 PR, changes to `books.py` only)

**Background**  
`find_book_by_title()` and the dependent methods (`mark_as_read`, `remove_book`) scan
the full list linearly. Ex-06 hoisted the `.lower()` call but the O(n) scan remains.
Adding a `dict[str, Book]` index keyed on `title.lower()` reduces lookup to O(1)
at the cost of keeping the index in sync with `self.books`.

**Acceptance criteria**
- [ ] `BookCollection` maintains a `_title_index: dict[str, Book]` updated on every `add_book`, `remove_book`, and `load_books` call
- [ ] `find_book_by_title()` uses `self._title_index.get(title.lower())` instead of a loop
- [ ] Before/after benchmark (10k books, 5000 calls) shows measurable improvement and is included in the PR
- [ ] All 9 existing tests pass; `BOOK_SCHEMA` and contract tests are unaffected
- [ ] `books.py` coverage does not decrease from current 88%

**Linked paths**: `samples/book-app-project/books.py` — `find_book_by_title`, `add_book`, `remove_book`, `load_books`  
**Dependency**: None  
**Verification**: benchmark script from ex-06 re-run; pytest -v → 9+ passed

---

## Item 3 — Automated `BOOK_SCHEMA` drift detection

**Type**: Test / contract hardening  
**Priority**: Medium — silent drift risk: `Book` dataclass fields can change without updating `BOOK_SCHEMA`  
**Effort**: Tiny (1 PR, 1 new test, no new files)

**Background**  
`tests/test_contract.py` defines `BOOK_SCHEMA = {"title": str, "author": str, "year": int, "read": bool}`.
If a field is added or renamed in the `Book` dataclass (e.g., adding `genre: str`), the existing
contract tests continue to pass against stale data — they check saved JSON structure but
`BOOK_SCHEMA` itself is never validated against the live dataclass definition.

**Acceptance criteria**
- [ ] A new test `test_book_schema_matches_dataclass` uses `dataclasses.fields(Book)` to get the live field names and types and asserts they match `BOOK_SCHEMA` exactly (same keys, same types)
- [ ] Test fails if a field is added to `Book` without updating `BOOK_SCHEMA` (demonstrate with a temporary mutation)
- [ ] Test added to `tests/test_contract.py` — no new files needed
- [ ] All 10 tests (9 existing + 1 new) pass

**Linked paths**: `samples/book-app-project/tests/test_contract.py` — `BOOK_SCHEMA`; `samples/book-app-project/books.py` — `Book` dataclass  
**Dependency**: None  
**Verification**: `pytest tests/test_contract.py -v` → 5/5 passed

---

## Item 4 — Log rotation and optional file output in `logging_config.py`

**Type**: Operability  
**Priority**: Low-Medium — required for any multi-session use beyond a single terminal  
**Effort**: Small (1 PR, changes to `logging_config.py` only)

**Background**  
`logging_config.py` always writes to `stderr`. In practice users want:
1. A log file that persists across sessions (`LOG_FILE=book-app.log`)
2. Rotation so the file doesn't grow unboundedly (`LOG_MAX_BYTES`, `LOG_BACKUP_COUNT`)

`LOG_FILE` should remain unset by default so existing behaviour (stderr only) is unchanged.

**Acceptance criteria**
- [ ] `get_logger()` reads `LOG_FILE` env var; if set, attaches a `RotatingFileHandler` writing JSON to that path
- [ ] `LOG_MAX_BYTES` (default 1 MB) and `LOG_BACKUP_COUNT` (default 3) are configurable via env vars
- [ ] When `LOG_FILE` is unset, behaviour is identical to current (stderr only, no file created)
- [ ] `logging_config.py` coverage remains at 100%
- [ ] Verification command documented in `CONTRIBUTING.md` (or a docstring): `LOG_FILE=app.log python book_app.py list`

**Linked paths**: `samples/book-app-project/logging_config.py`; `CONTRIBUTING.md` (doc update)  
**Dependency**: None  
**Verification**: `LOG_FILE=/tmp/test.log python book_app.py list && cat /tmp/test.log` → JSON line visible

---

## Item 5 — Add blocking `ruff` lint step to CI

**Type**: CI / code quality  
**Priority**: Medium — walk-evidence.yml is advisory only; there is no blocking quality gate  
**Effort**: Small (1 PR, CI config + `pyproject.toml` ruff config)

**Background**  
`.github/workflows/walk-evidence.yml` is non-blocking by design. The repo has no required
quality gate. Adding `ruff` as a blocking check (`continue-on-error: false`) on PRs ensures
style and basic correctness issues are caught before merge without requiring manual enforcement.

**Acceptance criteria**
- [ ] `ruff` added to `pyproject.toml` `[tool.ruff]` with `line-length = 120` and `select = ["E", "F", "W"]`
- [ ] A new job `lint` in `.github/workflows/walk-evidence.yml` (or a separate `lint.yml`) runs `ruff check samples/book-app-project/` with `continue-on-error: false`
- [ ] `ruff check` passes on the current codebase with zero violations before the PR is opened
- [ ] The lint job is added to branch protection required checks (document the Settings path)
- [ ] Any pre-existing lint violations are fixed in the same PR

**Linked paths**: `samples/book-app-project/pyproject.toml`; `.github/workflows/walk-evidence.yml` or new `lint.yml`  
**Dependency**: Item 1 (cover error paths first to avoid lint fixes invalidating coverage)  
**Verification**: `ruff check samples/book-app-project/` → `All checks passed.`

---

## Dependencies

```
Item 3 (schema drift)   — no dependencies
Item 4 (log rotation)   — no dependencies
Item 1 (coverage 100%)  — no dependencies
Item 2 (O(1) lookup)    — best after Item 1 (coverage baseline secured)
Item 5 (lint CI gate)   — best after Item 1 (avoid lint fixes breaking coverage)
```

**Suggested order**: 3 → 4 → 1 → 2 → 5

---

## Links

| Resource | Path |
|---|---|
| Domain module | `samples/book-app-project/books.py` |
| Contract tests | `samples/book-app-project/tests/test_contract.py` |
| Logging config | `samples/book-app-project/logging_config.py` |
| CI workflow | `.github/workflows/walk-evidence.yml` |
| Architecture doc | `ai-track-docs/architecture.md` |
| Walk onboarding | `ai-track-docs/onboarding-walk.md` |
| Security notes | `SECURITY.md` |
