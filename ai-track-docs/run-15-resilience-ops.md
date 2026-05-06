# Run-15 Patch Plan: Resilience — Deadline + load_books + Ops Runbook

## Mini Prompt
Add timeout/backoff helper and apply to 2-3 call paths with failure
tests and tuning docs. Apply pattern across a folder; update ops runbook.

---

## Current Call-Path Audit

| Call path | Retry? | Timeout? | Gap |
|---|---|---|---|
| `save_books()` | ✅ max_retries=3 | ❌ no deadline | No wall-time ceiling |
| `load_books()` | ❌ | ❌ | PermissionError propagates uncaught, crashes __init__ |
| `mark_as_read()` → `save_books()` | ✅ (via save_books) | ❌ | Inherited from save_books |
| `remove_book()` → `save_books()` | ✅ (via save_books) | ❌ | Inherited from save_books |

**Two gaps closed:**
1. `load_books()` — transient `PermissionError`/`OSError` (NFS lock, permission flush) now retried.
2. Both call sites now have `deadline=5.0` — wall-time budget prevents indefinite blocking.

---

## Changes

### Phase 1 — Add `deadline` parameter to `retry_with_backoff` (`resilience.py`)
New parameter `deadline: float | None = None` (seconds).  
If elapsed wall time ≥ deadline after a failure, raise `TimeoutError` immediately (do not sleep, do not retry further).  
New log event: `retry.deadline_exceeded` at WARNING.  
New guard-rail: `deadline <= 0` raises `ValueError` at decoration time.

### Phase 2 — Apply `@retry_with_backoff` to `load_books()` (`books.py`)
`@retry_with_backoff(exceptions=(OSError,), max_retries=3, initial_delay=0.1, backoff_factor=2.0, deadline=5.0)`  
OSErrors that escape the inner try (PermissionError, EAGAIN, etc.) are caught and retried.  
FileNotFoundError/JSONDecodeError continue to be handled inside the function body.

### Phase 3 — Add `deadline=5.0` to `save_books()` (`books.py`)
Updated existing decorator.

### Phase 4 — Add failure tests (`tests/test_resilience.py`)
Added `TestDeadlineParameter` (4 tests) and `TestLoadBooksResilience` (3 tests).

### Phase 5 — Create ops runbook (`samples/book-app-project/RUNBOOK.md`)
Covers: call-path registry, worst-case latency calc, log events, tuning guide,
diagnostic procedure, rollback instructions, local test commands.

---

## Files Changed

| File | Change |
|---|---|
| `samples/book-app-project/resilience.py` | Added `deadline` parameter + `retry.deadline_exceeded` event + new `deadline` guard-rail |
| `samples/book-app-project/books.py` | Added decorator to `load_books()`; added `deadline=5.0` to `save_books()` |
| `samples/book-app-project/tests/test_resilience.py` | Added `TestDeadlineParameter` (4 tests) and `TestLoadBooksResilience` (3 tests) |
| `samples/book-app-project/RUNBOOK.md` | Created — ops runbook |
| `ai-track-docs/run-15-resilience-ops.md` | This evidence file |

## Out of Scope

`samples/book-app-buggy/`, `samples/buggy-code/`, `.venv/`

---

## Evidence

### Before

| Metric | Value |
|---|---|
| Tests | 124 passing |
| Coverage | 98% |
| Ruff findings | 2 (PERF203 + E501 — intentional suppressions) |
| `load_books()` protection | None — PermissionError propagates uncaught |
| `save_books()` deadline | None — could block indefinitely |

### After

| Metric | Value |
|---|---|
| Tests | **131 passing** (+7) |
| Coverage | 98% (unchanged) |
| Ruff findings | **2** (same 2 intentional suppressions, no new findings) |
| `load_books()` protection | `@retry_with_backoff(max_retries=3, initial_delay=0.1, deadline=5.0)` |
| `save_books()` deadline | `deadline=5.0` added to existing decorator |
| New log event | `retry.deadline_exceeded` at WARNING |
| Ops runbook | `samples/book-app-project/RUNBOOK.md` (5 sections, tuning formulas) |

### New tests

| Test | What it verifies |
|---|---|
| `TestDeadlineParameter::test_deadline_exceeded_raises_timeout_error` | `TimeoutError` raised when elapsed ≥ deadline |
| `TestDeadlineParameter::test_deadline_not_exceeded_allows_retry` | Retries continue normally when elapsed < deadline |
| `TestDeadlineParameter::test_deadline_zero_or_negative_raises_value_error` | `deadline <= 0` rejected at decoration time |
| `TestDeadlineParameter::test_deadline_none_means_no_time_limit` | `deadline=None` default never triggers TimeoutError |
| `TestLoadBooksResilience::test_load_succeeds_after_one_transient_permission_error` | `load_books()` retries and recovers from single PermissionError |
| `TestLoadBooksResilience::test_load_raises_after_exhausting_retries` | `load_books()` re-raises after all retries exhausted |
| `TestLoadBooksResilience::test_file_not_found_still_gives_empty_collection` | FileNotFoundError still handled inside — no retry triggered |

---

## Rollback

```bash
git checkout HEAD -- samples/book-app-project/resilience.py
git checkout HEAD -- samples/book-app-project/books.py
git checkout HEAD -- samples/book-app-project/tests/test_resilience.py
rm -f samples/book-app-project/RUNBOOK.md
```
