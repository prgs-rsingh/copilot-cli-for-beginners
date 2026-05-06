# Run-03: Multi-File Refactor — Extract `prompt()` Helper + `test_book_app.py`

## Mini Prompt
Propose a multi-file refactor plan (2-4 files), then diffs, then tests.

## Opportunity

`book_app.py` contained 5 occurrences of `input(...).strip()` across 3 handlers; `utils.py` had 3 more. A single `prompt(label: str) -> str` helper eliminates all 8 call sites.

Secondary: `book_app.py` was at **0% coverage** (47 statements, all missed). Adding `tests/test_book_app.py` closes this gap.

## Files Changed

| File | Change |
|---|---|
| `utils.py` | Added `prompt(label: str) -> str`; updated `get_user_choice()` and `get_book_details()` to use it |
| `book_app.py` | Imported `prompt`; replaced `input(...).strip()` with `prompt(...)` in `handle_add`, `handle_remove`, `handle_find` |
| `tests/test_utils.py` | Added `TestPrompt` class (2 tests for `prompt()`) |
| `tests/test_book_app.py` | New — 17 tests covering all handlers, `show_help`, `main()` |

## Out of Scope
- `samples/book-app-buggy/`, `samples/buggy-code/` — intentional bugs, do not touch
- `books.py`, `resilience.py`, `logging_config.py` — not involved in this refactor
- `.venv/`, `__pycache__/`

---

## Before Baseline
```
book_app.py    47 stmts   47 missed    0%
utils.py       41 stmts    0 missed  100%
TOTAL         203 stmts   55 missed   73%
66 passed
```

## Steps Run

| Phase | Step | Outcome |
|---|---|---|
| Plan | Committed `run-03-multi-file-refactor.md` as patch plan | ✅ |
| 1 | `utils.py`: added `prompt()`, updated `get_user_choice()` and `get_book_details()` | ✅ |
| 2 | `book_app.py`: imported `prompt`, replaced 5× `input().strip()` in 3 handlers | ✅ |
| 3a | `tests/test_utils.py`: added `TestPrompt` (2 tests) | ✅ |
| 3b | `tests/test_book_app.py`: created (17 tests: handlers + show_help + main) | ✅ |
| Validate | `pytest tests/test_book_app.py tests/test_utils.py -v` → 37 passed | ✅ |
| Validate | Full suite `pytest --cov` → 85 passed, TOTAL 98% | ✅ |

## After Snapshot
```
book_app.py    47 stmts    0 missed  100%
utils.py       43 stmts    0 missed  100%   (43 = 41 + 2 for prompt())
TOTAL         205 stmts    5 missed   98%   (5 = books.py JSONDecodeError branch)
85 passed in 0.51s
```

---

## Measurable Outcome

| Metric | Before | After | Delta |
|---|---|---|---|
| `book_app.py` coverage | 0% | **100%** | **+100 pp** |
| `utils.py` coverage | 100% | **100%** | maintained |
| TOTAL coverage | 73% | **98%** | **+25 pp** |
| Test count | 66 | **85** | +19 |
| Regressions | — | **0** | — |
| `input().strip()` call sites | 8 | **0** | -8 (all use `prompt()`) |

---

## Delegation Checklist

- [x] Patch plan created (scope, files, expected outcome)
- [x] File scope defined (4 files: `utils.py`, `book_app.py`, `test_utils.py`, `test_book_app.py`)
- [x] Diffs reviewed before committing (each phase reviewed independently)
- [x] Tests generated (19 new tests)
- [x] Tests run and passing (85/85)
- [x] Documentation updated (n/a — refactor + test change)
- [x] Evidence captured (before/after snapshots above)
- [x] Rollback plan documented (per-phase below)
- [x] Context file saved to `ai-track-docs/run-03-multi-file-refactor.md`

---

## Acceptance Results

| Checkpoint | Status | Verification |
|---|---|---|
| Plan included | ✅ Pass | `ai-track-docs/run-03-multi-file-refactor.md` committed before code changes |
| Multiple files modified | ✅ Pass | 4 files: `utils.py`, `book_app.py`, `test_utils.py`, `test_book_app.py` |
| Tests remain green | ✅ Pass | `pytest` → 85 passed, 0 failures, 0 errors |

---

## Rollback

- Phase 1: revert `utils.py` (remove `prompt()`, restore `input().strip()` in `get_user_choice`/`get_book_details`)
- Phase 2: revert `book_app.py` (remove `prompt` import, restore `input(...).strip()` in 3 handlers)
- Phase 3: `rm tests/test_book_app.py` + revert `TestPrompt` from `test_utils.py`
- Full: `git revert <sha-range> --no-commit && git commit`

---

## PR Description

```markdown
## Title
GHCP -- Run: 03 Multi-File Refactor — Extract prompt() + Test book_app Handlers

## Summary
- Identified: 8 occurrences of `input(...).strip()` scattered across `utils.py` and `book_app.py`.
- Refactor: extracted `prompt(label: str) -> str` into `utils.py`; updated all 8 call sites.
- Secondary benefit: `book_app.py` was at 0% coverage; new `test_book_app.py` (17 tests) brings it to 100%.
- Patch plan: `ai-track-docs/run-03-multi-file-refactor.md`
- Files/paths touched:
  - `utils.py` — added `prompt()`, updated `get_user_choice()`, `get_book_details()`
  - `book_app.py` — imported `prompt`, replaced `input().strip()` in 3 handlers
  - `tests/test_utils.py` — added `TestPrompt` (2 new tests)
  - `tests/test_book_app.py` — new (17 tests: all handlers + show_help + main)

## Evidence
- Before: `book_app.py` 0% | `utils.py` 100% | TOTAL 73% | 66 tests
- After:  `book_app.py` **100%** | `utils.py` **100%** | TOTAL **98%** | **85 tests**
- `pytest` → **85 passed in 0.51s** — zero regressions
- Delegation checklist: completed ✅

## Risk & Rollback
- Risk: low — behavior identical (prompt() = input().strip()); all 66 pre-existing tests pass
- Rollback per-phase: revert utils.py → book_app.py → test files (in reverse order)
- Full rollback: `git revert <sha-range> --no-commit && git commit`

## Track
- Level: Run
- Exercise: 03
```
