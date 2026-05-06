# Exercise 15 — Resilience: `retry_with_backoff` on `save_books`

## Mini Prompt
Add timeout/backoff/resilience helper for 1-2 call sites with failure tests and tuning doc.

---

## Call Site Identified

**`BookCollection.save_books()`** — `samples/book-app-project/books.py`

The book-app has no external HTTP or database calls; `save_books()` is the most critical
I/O call site. An `OSError` (disk full, permissions flush delay, network filesystem blip)
currently propagates silently with no retry. A transient failure loses the entire write.

---

## Design

**Module**: `samples/book-app-project/resilience.py` (stdlib only, no new deps)  
**Pattern**: decorator factory `retry_with_backoff(max_retries, initial_delay, backoff_factor, exceptions)`  
**Applied to**: `BookCollection.save_books()` via `@retry_with_backoff(...)`

Default tuning for `save_books()`:
- `max_retries=3` — 3 total attempts
- `initial_delay=0.05` — 50 ms before 2nd attempt
- `backoff_factor=2.0` — exponential (50 ms → 100 ms)
- `exceptions=(OSError,)` — retries only on OS-level I/O errors

Worst-case added latency: **150 ms** (50 ms + 100 ms before the 3rd attempt raises).

---

## Steps Run

| # | Step | Outcome |
|---|---|---|
| 1 | Identified `save_books()` as the critical unprotected I/O call site | No HTTP/DB calls exist; local file I/O is the boundary |
| 2 | Created `resilience.py` with `retry_with_backoff` decorator factory; stdlib only | Done |
| 3 | Added parameter guard-rails (ValueError for invalid tuning at decoration time) | Done |
| 4 | Applied `@retry_with_backoff(max_retries=3, initial_delay=0.05, backoff_factor=2.0)` to `save_books()` | Done |
| 5 | Created `tests/test_resilience.py` — 14 tests: unit (7), parameter validation (4), integration (3) | Done |
| 6 | `pytest tests/test_resilience.py -v` → 14/14 passed | ✅ |
| 7 | Full suite → 48 passed, `resilience.py` 100% coverage, TOTAL 55% → **61%** | ✅ |

---

## Tuning Parameters

| Parameter | Default | Range | Notes |
|---|---|---|---|
| `max_retries` | `3` | 1–5 | `1` = no retries (first failure raises immediately) |
| `initial_delay` | `0.05` | 0.01–2.0 | Seconds before 2nd attempt. Use 0.5–2.0 for remote APIs |
| `backoff_factor` | `2.0` | 1.0–4.0 | `1.0` = constant interval; `2.0` = exponential |
| `exceptions` | `(OSError,)` | any | Narrow to known-transient exceptions only |

**Worst-case wait formula** (time before final attempt raises):

$$\text{total wait} = d_0 \cdot \frac{b^{n-1} - 1}{b - 1}$$

where $d_0$ = `initial_delay`, $b$ = `backoff_factor`, $n$ = `max_retries`.

With defaults: $0.05 \cdot \frac{2^2 - 1}{2 - 1} = 0.15\text{ s}$

---

## Rollback Guidance

**To remove retry from `save_books` only**: delete the 4-line decorator block above the method:
```python
# Remove these 4 lines:
@retry_with_backoff(max_retries=3, initial_delay=0.05, backoff_factor=2.0, exceptions=(OSError,))
```
`save_books` works without the decorator. No other code changes needed.

**To remove the module entirely**: delete `resilience.py`, remove the import from `books.py`,
and remove the decorator. `tests/test_resilience.py` can also be deleted.

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| Resilience improvement applied | ✅ Pass — `save_books()` has `@retry_with_backoff(max_retries=3, ...)` |
| Failure tests passing | ✅ Pass — 14/14: transient recovery, exhaustion raise, backoff timing, integration |
| Tuning/rollback guidance documented | ✅ Pass — table above + formula + rollback steps |

---

## Evidence

```
pytest tests/test_resilience.py -v  →  14 passed in 0.60s
pytest (full suite)                 →  48 passed in 0.45s

Coverage:
  resilience.py:    27 stmts, 0 missed  → 100%
  books.py:         66 stmts, 8 missed  →  88%
  logging_config.py: 22 stmts, 0 missed → 100%
  TOTAL: 61%  (up from 55%)
```

---

## Files Changed

| File | Change |
|---|---|
| `samples/book-app-project/resilience.py` | New — `retry_with_backoff` decorator factory with tuning doc and guard-rails |
| `samples/book-app-project/books.py` | Import `retry_with_backoff`; apply to `save_books()` with 4-line documented block |
| `samples/book-app-project/tests/test_resilience.py` | New — 14 failure tests (unit + parameter validation + integration) |
| `ai-track-docs/onboarding-walk.md` | Exercise log updated with ex-15 |

---

## PR Template

```markdown
## Title
GHCP -- Walk: 15 Resilience — retry_with_backoff on save_books + Failure Tests

## Summary
- No external HTTP/DB calls in book-app; applied resilience to `save_books()` — the
  critical local I/O call site (OSError on disk full / permissions loses the write).
- Created `resilience.py`: `retry_with_backoff` decorator factory (stdlib only, no new deps).
  - 3 attempts, 50 ms → 100 ms exponential backoff, retries only `OSError`.
  - Guard-rails: `ValueError` at decoration time for invalid tuning values.
  - Worst-case added latency: **150 ms** before final raise.
- Applied `@retry_with_backoff(max_retries=3, initial_delay=0.05, backoff_factor=2.0)` to
  `BookCollection.save_books()` in `books.py`.
- Added 14 failure tests in `tests/test_resilience.py`:
  - Unit: success path, retry-then-succeed, exhaustion raise, non-matching exception, backoff sequence, functools.wraps
  - Parameter validation: ValueError on invalid max_retries / initial_delay / backoff_factor
  - Integration: save_books recovers from 1 transient OSError, raises after 3, sleep count verified
- Coverage: 55% → **61%** | `resilience.py` **100%** | 48 total tests.
- Files/paths touched:
  - `samples/book-app-project/resilience.py` (new)
  - `samples/book-app-project/books.py` (import + decorator on save_books)
  - `samples/book-app-project/tests/test_resilience.py` (new)
  - `ai-track-docs/onboarding-walk.md` (ex-15 added)

## Evidence
- `pytest tests/test_resilience.py -v` → **14 passed in 0.60s**
- `pytest` (full suite) → **48 passed in 0.45s**
- `resilience.py`: 100% | `books.py`: 88% | TOTAL: **61%**

## Risk & Rollback
- Risk: low — decorator wraps save_books without touching logic; existing 34 tests unaffected
- Rollback call site: delete 4-line `@retry_with_backoff(...)` block above `save_books`
- Rollback module: `git revert <this-sha>` removes resilience.py, import, and decorator
- Added latency: max 150 ms on disk failure (not on success path — zero overhead on happy path)

## Review Focus
1. **`resilience.py` guard-rails** — `ValueError` is raised at *decoration* time (when the
   decorator is applied) not at call time. Verify `retry_with_backoff(max_retries=0)` raises
   immediately when `books.py` is imported, not on first `save_books()` call.
2. **`exceptions=(OSError,)` scope** — confirm `ValueError` and `json.JSONDecodeError` are NOT
   in the exceptions tuple; only `OSError` retries (non-OS errors propagate immediately).
3. **Test isolation** — every `TestSaveBooksResilience` test patches `resilience.time.sleep`
   to suppress real waits; verify no test introduces actual sleep latency (CI must stay fast).
4. **Integration test `test_save_succeeds_after_one_transient_oserror`** — `flaky_open` counts
   `mode == "w"` calls only; read-mode opens (load_books fixture) must not be counted.
5. **Decorator preserves method binding** — `@retry_with_backoff` uses `@wraps(fn)` and accepts
   `*args, **kwargs`; verify `self` is still passed correctly to `save_books`.

## Track
- Level: Walk
- Exercise: 15
```
