# Book Collection App

A Python CLI app for managing a personal book collection — add, remove, list, and find books. Used throughout the GitHub Copilot CLI course as the primary hands-on example.

> **Note for learners:** This README was intentionally rough at the start of the course. It has been refreshed here as a doc-with-code exercise (Run-04). Compare the git history to see what changed and why.

---

## Module Map

| File | Purpose | Key Exports |
|---|---|---|
| `book_app.py` | CLI entry point — `main()` dispatches commands | `main`, `handle_list`, `handle_add`, `handle_remove`, `handle_find`, `show_help` |
| `books.py` | Core domain — `Book` dataclass + `BookCollection` CRUD + JSON persistence | `Book`, `BookCollection` |
| `utils.py` | UI helpers — menu, prompts, year parsing, display | `prompt`, `parse_year`, `get_book_details`, `show_books`, `print_menu` |
| `resilience.py` | `retry_with_backoff` decorator — exponential backoff for transient I/O failures | `retry_with_backoff` |
| `logging_config.py` | Structured JSON logging to stderr, level controlled by `LOG_LEVEL` env var | `get_logger` |
| `data.json` | Persistent book store (JSON array of `{title, author, year, read}` objects) | — |

Architecture diagram with import graph: [`ai-track-docs/architecture.md`](../../ai-track-docs/architecture.md)

---

## Test Suite

| Test file | What it tests |
|---|---|
| `tests/test_books.py` | `BookCollection` CRUD operations |
| `tests/test_contract.py` | JSON schema + golden fixture |
| `tests/test_feature_flags.py` | `BOOK_APP_STRICT_YEAR` off/on matrix |
| `tests/test_resilience.py` | Retry logic, parameter validation, `save_books` integration |
| `tests/test_utils.py` | All util functions including `prompt()` |
| `tests/test_book_app.py` | All handlers, `show_help`, `main()` dispatch |

Current coverage: **98%** (85 tests). See `htmlcov/index.html` after running tests.

---

## Running the App

```bash
# Activate the virtual environment first
source .venv/bin/activate

python book_app.py list
python book_app.py add
python book_app.py remove
python book_app.py find
python book_app.py help
```

---

## Running Tests

```bash
# Using the project venv (recommended)
.venv/bin/pytest

# Or with system Python if venv is activated
python -m pytest tests/

# With coverage report
.venv/bin/pytest --cov=. --cov-report=term-missing
```

---

## Environment Variables

| Variable | Default | Valid values | Effect |
|---|---|---|---|
| `BOOK_APP_STRICT_YEAR` | _(unset)_ | `1`, `true`, `yes` (case-insensitive) | When set, `parse_year()` rejects years outside `[1, current_year]` and raises `ValueError` |
| `LOG_LEVEL` | `WARNING` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | Sets the log level for the structured JSON logger in `logging_config.py` |

Example:

```bash
BOOK_APP_STRICT_YEAR=1 python book_app.py add
LOG_LEVEL=DEBUG python book_app.py list
```

---

## Extension Guidance

### Adding a new CLI command

1. **Add a handler** in `book_app.py`:

   ```python
   def handle_mark():
       title = prompt("Title to mark as read: ")
       success = collection.mark_as_read(title)
       print("Marked as read." if success else "Book not found.")
   ```

2. **Wire it in `main()`**:

   ```python
   elif command == "mark":
       handle_mark()
   ```

3. **Update `show_help()`** with the new command description.

4. **Add tests** in `tests/test_book_app.py` following the existing `TestHandle*` pattern — monkeypatch `book_app.prompt` and `book_app.collection`.

### Adding a new module

1. Create `your_module.py` in `samples/book-app-project/`.
2. Add a `get_logger(__name__)` call at module level (see `books.py` for the pattern).
3. Import from the module using a plain import (no package prefix needed — the app runs from this directory).
4. Add `tests/test_your_module.py`; follow the existing `TestClassName` grouping pattern.
5. Run `npm run gen:arch` from the repo root to regenerate the architecture diagram.

### Modifying JSON persistence

`BookCollection.save_books()` is decorated with `@retry_with_backoff`. Tune parameters in `books.py`:

```python
@retry_with_backoff(max_retries=3, initial_delay=0.05, backoff_factor=2.0, exceptions=(OSError,))
def save_books(self) -> None: ...
```

To remove retry behaviour entirely, delete the decorator line — the method works without it.

---

## Risk Notes

| Risk | Location | Mitigation |
|---|---|---|
| **JSON corruption** | `books.py:load_books()` | `JSONDecodeError` is caught; app starts with an empty collection and prints a warning. Back up `data.json` before bulk edits. |
| **Transient I/O failures** | `books.py:save_books()` | `@retry_with_backoff` retries up to 3×. Worst-case wait: 150 ms. If all retries fail, the exception propagates — the collection stays in memory but is not persisted. |
| **Feature flag year range** | `utils.py:parse_year()` | `BOOK_APP_STRICT_YEAR=1` rejects years < 1 or > current year. Books with `year=0` (blank input default) are always accepted. |
| **`mark` command gap** | `utils.py:print_menu()` vs `book_app.py` | `print_menu()` lists "Mark book as read" as option 3, but no `mark` CLI command exists in `book_app.py`. Known gap — tracked in the course backlog. |
| **`DATA_FILE` path coupling** | `books.py` line 9 | `DATA_FILE = "data.json"` is relative to the working directory. Run the app from `samples/book-app-project/` or the file will not be found. Tests override this via `monkeypatch`. |
| **No input sanitization on title/author** | `book_app.py`, `utils.py` | `prompt()` strips whitespace only. Duplicate titles and empty strings are accepted. |

---

## Notes

- Python 3.10+ required (uses `X | Y` union type syntax and `list[T]` generics)
- Not production-ready — intended as a learning sample
- See `pyproject.toml` for pytest, coverage, and ruff lint configuration
