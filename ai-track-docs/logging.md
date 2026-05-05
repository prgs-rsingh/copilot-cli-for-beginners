# Structured Logging — `books.py`

Structured JSON logs are emitted to **stderr** by the three mutating operations
in `samples/book-app-project/books.py`: `add_book`, `mark_as_read`, and
`remove_book`.

---

## Log Format

Each log line is a single JSON object on stderr:

```json
{"op": "add_book", "status": "ok", "elapsed_ms": 1.23, "title": "Dune", "author": "Frank Herbert", "year": 1965}
{"op": "mark_as_read", "status": "not_found", "elapsed_ms": 0.04, "title": "Unknown Book"}
{"op": "remove_book", "status": "ok", "elapsed_ms": 0.89, "title": "Dune"}
```

### Fields

| Field | Type | Always present | Description |
|-------|------|:--------------:|-------------|
| `op` | string | ✓ | Operation name: `add_book`, `mark_as_read`, `remove_book` |
| `status` | string | ✓ | `ok` — succeeded; `not_found` — title not in collection |
| `elapsed_ms` | number | ✓ | Wall-clock duration of the operation in milliseconds (2 d.p.) |
| `title` | string | ✓ | Book title passed to the operation |
| `author` | string | `add_book` only | Author passed to `add_book` |
| `year` | integer | `add_book` only | Year passed to `add_book` |

---

## Controlling Log Verbosity

Logs are silenced by default (`WARNING` level).  Set `BOOK_APP_LOG_LEVEL` to
`INFO` or `DEBUG` to enable them.

```bash
# Enable structured logs
BOOK_APP_LOG_LEVEL=INFO python book_app.py add

# Disable (default behaviour)
python book_app.py add
```

The logger name is `book_app`.  When embedding the module in a larger app you
can configure it through the standard `logging` hierarchy:

```python
import logging
logging.getLogger("book_app").setLevel(logging.INFO)
```

---

## Viewing Logs

Because logs go to **stderr** and the CLI's user-facing output goes to
**stdout**, you can separate them cleanly:

```bash
# See only logs (suppress CLI output)
BOOK_APP_LOG_LEVEL=INFO python book_app.py add 2>&1 1>/dev/null

# See only CLI output (suppress logs)
BOOK_APP_LOG_LEVEL=INFO python book_app.py add 2>/dev/null

# Capture logs to a file while still seeing CLI output
BOOK_APP_LOG_LEVEL=INFO python book_app.py add 2>ops.log

# Pretty-print logs with jq (requires jq)
BOOK_APP_LOG_LEVEL=INFO python book_app.py add 2>&1 1>/dev/null | jq .

# Filter only failures
BOOK_APP_LOG_LEVEL=INFO python book_app.py add 2>&1 | grep '"status":"not_found"' | jq .
```

---

## Instrumented Code Paths

| Method | Logged events |
|--------|--------------|
| `BookCollection.add_book` | One `ok` line after successful persist |
| `BookCollection.mark_as_read` | `ok` on success; `not_found` when title absent |
| `BookCollection.remove_book` | `ok` on success; `not_found` when title absent |

Read-only methods (`list_books`, `find_book_by_title`, `find_by_author`) are
**not** logged — they carry no side effects and would add noise without value.

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| stderr, not stdout | Keeps log lines out of any piped CLI output |
| stdlib `logging` only | No new dependencies; respects the existing `pyproject.toml` constraint |
| `BOOK_APP_LOG_LEVEL` env var | Standard 12-factor app pattern; silenced by default so beginners aren't surprised |
| JSON lines (not pretty-print) | Machine-readable; `jq`-friendly; one line = one event for `grep` |
| `elapsed_ms` on every line | Lets you spot slow `save_books()` calls without a separate profiler |
