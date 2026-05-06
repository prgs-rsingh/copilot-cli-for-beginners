# Run-02: utils.py Coverage 41% → 100% (+59 pp)

## Mini Prompt
Identify a module with low coverage, add tests to raise it by at least 2%, and capture before/after metrics.

## Target Module
`samples/book-app-project/utils.py` — 41% before (24 missed statements)

## Out of Scope
- `samples/book-app-buggy/`, `samples/buggy-code/` — intentional bugs, do not touch
- `.venv/`, `__pycache__/`, all other modules

## Before Baseline
```
utils.py    41 stmts   24 missed   41%   6-11, 15, 45-55, 60-70
TOTAL      203 stmts   79 missed   61%
48 passed
```

## Uncovered Paths (by line range)

| Lines | Function | Why uncovered |
|---|---|---|
| 6-11 | `print_menu()` | Never called from any test |
| 15 | `get_user_choice()` | Calls `input()` — no test patches it |
| 45-55 | `get_book_details()` | Calls `input()` 3× — no test patches it; also has ValueError branch (line 53-54) |
| 60-70 | `show_books()` | Both branches (empty list + populated list) uncovered |

## Patch Plan

### Phase 1 — Write tests
Create `tests/test_utils.py` with 18 deterministic tests:
- `print_menu`: capsys assertions (3 tests)
- `get_user_choice`: monkeypatched input (2 tests)
- `get_book_details`: 3-input side_effect, blank year, invalid year, whitespace strip, strict-flag (5 tests)
- `show_books`: empty list, no-header check, header present, checkbox markers, title/author/year, numbering, mixed status (8 tests)

All tests use `capsys` and `monkeypatch` — no real I/O. `SimpleNamespace` used for Book objects.

Acceptance: `utils.py` ≥ 90%, all 48 existing tests still pass.

Phase 1 rollback: `rm samples/book-app-project/tests/test_utils.py`

---

## Steps Run

| Step | Outcome |
|---|---|
| Captured before baseline | 41%, 24 missed, 48 tests |
| Committed patch plan (`run-02-utils-coverage.md`) | ✅ |
| Created `tests/test_utils.py` — 18 tests across 4 test classes | ✅ |
| Ran `pytest tests/test_utils.py -v` | 18/18 passed ✅ |
| Ran full suite `pytest --cov` | 66 passed, utils.py 100%, TOTAL 73% ✅ |

---

## After Snapshot

```
utils.py   41 stmts    0 missed  100%
TOTAL     203 stmts   55 missed   73%
66 passed in 0.41s
```

---

## Measurable Outcome

| Metric | Before | After | Delta |
|---|---|---|---|
| `utils.py` coverage | 41% | **100%** | **+59 pp** |
| TOTAL coverage | 61% | **73%** | **+12 pp** |
| Test count | 48 | **66** | +18 |
| Regressions | — | **0** | — |

---

## Delegation Checklist

- [x] Patch plan created (scope, files, expected outcome)
- [x] File scope defined (`utils.py` + `tests/test_utils.py` only)
- [x] Diffs reviewed before committing (all 18 tests reviewed — deterministic, no flakiness)
- [x] Tests generated (18 new tests in `tests/test_utils.py`)
- [x] Tests run and passing (66/66)
- [x] Documentation updated (n/a — test-only change)
- [x] Evidence captured (before/after snapshots above)
- [x] Rollback plan documented (`rm tests/test_utils.py`)
- [x] Context file saved to `ai-track-docs/run-02-utils-coverage.md`

---

## Acceptance Results

| Checkpoint | Status | Verification |
|---|---|---|
| Coverage increased ≥ 2% in target module | ✅ Pass (+59 pp) | `pytest --cov=utils --cov-report=term-missing` → `utils.py 100%` |
| Before/after metrics captured | ✅ Pass | Snapshots above |
| No test regressions | ✅ Pass | 48 pre-existing tests all still pass (`66 passed`, 18 new) |
| Rollback steps included | ✅ Pass | `rm tests/test_utils.py` returns to 41% |

---

## PR Description

```markdown
## Title
GHCP -- Run: 02 utils.py Coverage 41% → 100% (+59 pp)

## Summary
- Target: `utils.py` — lowest coverage non-CLI module at 41% (24 uncovered statements).
- Patch plan: `ai-track-docs/run-02-utils-coverage.md`
- Added `tests/test_utils.py` — 18 deterministic tests across 4 classes:
  - `TestPrintMenu` (3): capsys assertions for menu output
  - `TestGetUserChoice` (2): monkeypatched `input()`
  - `TestGetBookDetails` (5): 3-input side_effect, blank/invalid year, whitespace, strict-flag
  - `TestShowBooks` (8): empty list, checkbox markers, title/author/year, numbering, mixed status
- All tests use `capsys` and `monkeypatch` — no real I/O, no flakiness.
- Files/paths touched: `samples/book-app-project/tests/test_utils.py` (new)

## Evidence
- Before: `utils.py` 41% (24 missed) | TOTAL 61% | 48 tests
- After:  `utils.py` **100%** (0 missed) | TOTAL **73%** | **66 tests**
- `pytest tests/test_utils.py -v` → 18 passed in 0.26s
- `pytest` (full suite) → **66 passed in 0.41s** — zero regressions
- Delegation checklist: completed ✅

## Risk & Rollback
- Risk: low — test-only change; no production code modified
- Rollback: `rm samples/book-app-project/tests/test_utils.py`
  Returns `utils.py` to 41% and suite to 48 tests; all other tests unaffected.

## Track
- Level: Run
- Exercise: 02
```
