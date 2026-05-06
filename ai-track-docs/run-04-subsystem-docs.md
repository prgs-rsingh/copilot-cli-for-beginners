# Run-04: Subsystem Docs Refresh — book-app-project README

## Mini Prompt
Create or refresh subsystem docs and extension guidance with risk notes.
Docs must be updated with code in the same PR (doc-with-code).

## Target Subsystem
`samples/book-app-project/` — the Python CLI book collection app used throughout all chapters.

---

## Audit Findings (Before)

| Finding | Stale State | Real State |
|---|---|---|
| Test files listed | `tests/test_books.py` only | 6 test files, 85 tests, 98% coverage |
| Modules listed | 4 files (missing `resilience.py`, `logging_config.py`) | 6 source modules |
| Input validation claim | "weak in some areas" | `BOOK_APP_STRICT_YEAR` feature flag implemented |
| Environment variables | None documented | `BOOK_APP_STRICT_YEAR`, `LOG_LEVEL` both in use |
| Extension guidance | None | None — gap |
| Risk notes | None | None — gap |
| Architecture link | Missing | `ai-track-docs/architecture.md` exists |
| Test command | `python -m pytest tests/` (no venv note) | `.venv/bin/pytest` preferred |
| `print_menu()` "Mark book as read" | Undocumented gap | No `mark` CLI command in `book_app.py` |

## Files Changed

| File | Change |
|---|---|
| `samples/book-app-project/README.md` | Full refresh — see sections below |

## Out of Scope
- Source code — docs-only change
- `samples/book-app-buggy/`, `samples/buggy-code/` — intentional bugs, do not touch

---

## What Was Added to README

### Module Map
All 6 source modules listed with purpose and key exports.
Link to `ai-track-docs/architecture.md` for the import graph.

### Test Suite Table
All 6 test files listed with what each tests.
Coverage noted: **98% / 85 tests**.

### Running the App + Tests
Added `source .venv/bin/activate` prerequisite.
Added coverage report variant.

### Environment Variables Table
| Variable | Default | Valid values | Effect |
|---|---|---|---|
| `BOOK_APP_STRICT_YEAR` | _(unset)_ | `1`, `true`, `yes` | Year range validation in `parse_year()` |
| `LOG_LEVEL` | `WARNING` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | Structured JSON logger level |

### Extension Guidance
- How to add a new CLI command (4-step pattern with code example)
- How to add a new module (5-step pattern, includes `gen:arch` reminder)
- How to tune/remove `@retry_with_backoff`

### Risk Notes Table
6 risks documented with location and mitigation:

| Risk | Location |
|---|---|
| JSON corruption | `books.py:load_books()` |
| Transient I/O failures / retry exhaustion | `books.py:save_books()` |
| Feature flag year range | `utils.py:parse_year()` |
| `mark` command gap | `utils.py:print_menu()` vs `book_app.py` |
| `DATA_FILE` path coupling | `books.py` line 9 |
| No input sanitization on title/author | `book_app.py`, `utils.py` |

---

## Steps Run

| Step | Outcome |
|---|---|
| Audit README against 6 source modules + 6 test files | 9 gaps identified |
| Committed `run-04-subsystem-docs.md` as patch plan | ✅ |
| Replaced `samples/book-app-project/README.md` | ✅ |
| Ran `pytest --cov` | ✅ 85 passed, 98%, no regressions |

---

## After Snapshot
```
TOTAL  205 stmts  5 missed  98%
85 passed in 0.49s
```

---

## Delegation Checklist

- [x] Patch plan created (scope, audit findings, expected outcome)
- [x] File scope defined (1 file: `README.md`)
- [x] Subsystem docs reference real file paths (all 6 modules, all 6 test files)
- [x] Extension guidance included (new command, new module, retry tuning)
- [x] Risk notes included (6 risks with location + mitigation)
- [x] Tests run and passing (85/85, no regressions)
- [x] Evidence captured (audit table + before/after)
- [x] Context file saved to `ai-track-docs/run-04-subsystem-docs.md`

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| Subsystem documentation updated | ✅ `samples/book-app-project/README.md` fully refreshed |
| Docs reference real file paths | ✅ All 6 modules and 6 test files by real path |
| Risk notes included | ✅ 6 risks with location and mitigation |
| Code and doc changes in same PR | ✅ Docs-only change (no source code changes needed) |
| All tests still pass | ✅ 85 passed, 98% |

---

## PR Description

```markdown
## Title
GHCP -- Run: 04 Subsystem Docs Refresh — book-app-project README

## Summary
Audited `samples/book-app-project/README.md` against real code; found 9 gaps.
Replaced the entire README with accurate, current docs including:
- Module Map (all 6 source modules with purpose + key exports)
- Test Suite table (all 6 test files, 98% coverage note)
- Environment Variables table (`BOOK_APP_STRICT_YEAR`, `LOG_LEVEL`)
- Extension Guidance (add command / add module / tune retry)
- Risk Notes (6 risks: JSON corruption, retry exhaustion, feature flag, mark gap, path coupling, no sanitization)
- Link to `ai-track-docs/architecture.md`
- Corrected test commands (venv-aware)
Patch plan: `ai-track-docs/run-04-subsystem-docs.md`

## Evidence
- 9 audit gaps identified and documented in patch plan
- Before: stale README with 1 test file listed, no env vars, no risk notes
- After: accurate README, all 6 modules/tests, env vars, extension guidance, 6 risk notes
- `pytest` → **85 passed, 98%** — zero regressions (docs-only change)

## Risk & Rollback
- Risk: none — docs-only change; no source code modified
- Rollback: `git revert <sha>` restores old README

## Track
- Level: Run
- Exercise: 04
```
