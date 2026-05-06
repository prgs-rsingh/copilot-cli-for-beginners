## Title
Copilot Track — Crawl: 15 Resilience

## Summary
- Added `_save_with_retry` helper and module-level constants (`SAVE_MAX_RETRIES=3`,
  `SAVE_RETRY_DELAY_S=0.1`) so `save_books` retries on `OSError` with fixed-interval
  backoff and raises `OSError` after exhaustion.
- Files touched: `samples/book-app-project/books.py`,
  `samples/book-app-project/tests/test_books.py`,
  `ai-track-docs/extending-books.md`.

## Test & Risk
- **Tests:** run with `pytest tests/ -v` from `samples/book-app-project/`; 16/16 passed.
  ```
  tests/test_books.py::test_add_book PASSED
  tests/test_books.py::test_mark_book_as_read PASSED
  tests/test_books.py::test_mark_book_as_read_invalid PASSED
  tests/test_books.py::test_remove_book PASSED
  tests/test_books.py::test_remove_book_invalid PASSED
  tests/test_books.py::test_find_by_author_returns_only_matching_books PASSED
  tests/test_books.py::test_add_book_rejects_invalid_input[-Orwell-1984-title] PASSED
  tests/test_books.py::test_add_book_rejects_invalid_input[  -Orwell-1984-title] PASSED
  tests/test_books.py::test_add_book_rejects_invalid_input[1984--1984-author] PASSED
  tests/test_books.py::test_add_book_rejects_invalid_input[1984-   -1984-author] PASSED
  tests/test_books.py::test_add_book_rejects_invalid_input[1984-Orwell-0-year] PASSED
  tests/test_books.py::test_add_book_rejects_invalid_input[1984-Orwell--5-year] PASSED
  tests/test_books.py::test_toggle_off_allows_duplicate_titles PASSED
  tests/test_books.py::test_toggle_on_rejects_duplicate_title PASSED
  tests/test_books.py::test_save_books_raises_ioerror_when_all_retries_fail PASSED
  tests/test_books.py::test_save_books_succeeds_after_transient_failure PASSED
  ============================== 16 passed in 0.10s ==============================
  ```
- **Risk:** low; rollback: `git revert acd96f6`.

## Track
- **Level:** crawl
- **Exercise:** 15-resilience
- **Evidence:**
  - `ai-track-docs/extending-books.md` — "Resilience: `save_books` Retry / Backoff"
    section documents constants, error message, retry log format, and monkeypatch
    override pattern.

## Acceptance

- [x] Resilience improvement implemented
- [x] Failure tests added and passing
- [x] Behavior documented
