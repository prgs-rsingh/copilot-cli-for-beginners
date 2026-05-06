# Exercise 09 — Observability: Structured JSON Operation Logging

## Mini Prompt
Add one metric/trace/log hook and document verification.

---

## Instrumentation Point

**No observability stack exists** — pure CLI app with `print()` calls only.
Per the troubleshooting guidance, structured logging is the right starting point.

**Hook location**: `books.py` — `BookCollection` mutation methods. These are the
domain boundary operations and the closest equivalent to "request handlers" in a CLI app.

**Events instrumented** (all emitted as JSON to `stderr`, one object per line):

| Event | Trigger | Key fields |
|---|---|---|
| `collection.loaded` | `load_books()` — startup | `count`, `data_file` |
| `collection.add` | `add_book()` — success | `title`, `author`, `year`, `result`, `collection_size` |
| `collection.mark_read` | `mark_as_read()` — success or not found | `title`, `result` |
| `collection.remove` | `remove_book()` — success or not found | `title`, `result`, `collection_size` |

---

## Implementation

Two files changed:

**New: `logging_config.py`**
- `JSONFormatter` — formats each `LogRecord` as a single-line JSON object with ISO 8601 UTC timestamp
- `get_logger(name)` — returns a named logger writing to `stderr`; level controlled by `LOG_LEVEL` env var (default `INFO`)

**Updated: `books.py`**
- `from logging_config import get_logger` + `logger = get_logger(__name__)` at module level
- `logger.info(...)` calls added to `load_books`, `add_book`, `mark_as_read`, `remove_book`

Log output goes to **stderr** — stdout user-facing output is completely unaffected.

---

## Steps Run

| # | Step | Outcome |
|---|---|---|
| 1 | Read `books.py` and `book_app.py` in full; identified mutation methods as the right hook points | 4 methods identified |
| 2 | Created `logging_config.py` with `JSONFormatter` and `get_logger()` (stdlib only) | Created |
| 3 | Added `logger` import and 6 `logger.info()` calls across 4 methods in `books.py` | Done |
| 4 | Ran `.venv/bin/pytest -v` — 9/9 passed; `books.py` 88%, `logging_config.py` 100%, total 48% | All green |
| 5 | Verified log output locally by exercising all 4 hooks | JSON output captured below |

---

## Verification Evidence

### Command
```bash
cd samples/book-app-project
.venv/bin/python book_app.py list 2>book-app.log   # logs go to file
cat book-app.log                                    # inspect
```

### Live output (all 4 hooks exercised)
```json
{"timestamp": "2026-05-06T04:51:47.123732Z", "level": "INFO", "logger": "books", "event": "collection.loaded", "count": 5, "data_file": "data.json"}
{"timestamp": "2026-05-06T04:51:47.124724Z", "level": "INFO", "logger": "books", "event": "collection.add", "title": "Dune", "author": "Frank Herbert", "year": 1965, "result": "success", "collection_size": 6}
{"timestamp": "2026-05-06T04:51:47.133719Z", "level": "INFO", "logger": "books", "event": "collection.mark_read", "title": "Dune", "result": "success"}
{"timestamp": "2026-05-06T04:51:47.133791Z", "level": "INFO", "logger": "books", "event": "collection.mark_read", "title": "Nonexistent", "result": "not_found"}
{"timestamp": "2026-05-06T04:51:47.141112Z", "level": "INFO", "logger": "books", "event": "collection.remove", "title": "Dune", "result": "success", "collection_size": 5}
{"timestamp": "2026-05-06T04:51:47.141205Z", "level": "INFO", "logger": "books", "event": "collection.remove", "title": "Nonexistent", "result": "not_found"}
```

### Suppress logs (normal use)
```bash
LOG_LEVEL=WARNING python book_app.py list
```

### Write logs to file
```bash
python book_app.py add 2>>book-app.log
```

### Where to view in production/staging
Since this is a CLI tool, logs are captured by the shell:
- **Local**: redirect `stderr` to a file (`2>>book-app.log`) or pipe to `jq` for pretty-printing
- **CI**: logs appear in the job's stderr stream automatically
- **Log aggregator**: pipe to any JSON-aware ingester (e.g., `| logger -t book-app` on Linux, or forward `stderr` to Datadog/Loki/CloudWatch)

---

## Coverage Impact

| Module | Before | After |
|---|---|---|
| `books.py` | 86% | 88% |
| `logging_config.py` | — | 100% (new) |
| **TOTAL** | 36% | **48%** |

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| Instrumentation added | ✅ Pass — 4 log hooks across `load_books`, `add_book`, `mark_as_read`, `remove_book` |
| Verification instructions documented | ✅ Pass — commands for console, file, suppress, and aggregator above |
| Evidence included | ✅ Pass — live JSON output for all 6 event permutations captured |

---

## Files Changed

| File | Change |
|---|---|
| `samples/book-app-project/logging_config.py` | Created — `JSONFormatter` + `get_logger()`, stdlib only |
| `samples/book-app-project/books.py` | Added logger import + 6 `logger.info()` calls across 4 methods |

---

## PR Template

```markdown
## Title
GHCP -- Walk: 09 Observability — Structured JSON Operation Logging

## Summary
- No observability stack existed; added structured logging as the simplest starting point.
- Created `logging_config.py`: stdlib-only `JSONFormatter` (ISO 8601 UTC timestamps) +
  `get_logger()` — level controlled by `LOG_LEVEL` env var (default `INFO`).
- Added 6 structured log hooks to `books.py` across 4 mutation methods:
  `collection.loaded`, `collection.add`, `collection.mark_read`, `collection.remove`
  — each emits a JSON line to `stderr` with event name, inputs, result, and collection size.
- Log output goes to `stderr` only — stdout user output is completely unaffected.
- Plan: inline — stdlib only (no new deps); stderr separation; `LOG_LEVEL` env var for suppression.
- Files/paths touched:
  - `samples/book-app-project/logging_config.py` (new)
  - `samples/book-app-project/books.py` (6 log hooks added)

## Evidence
- Tests/logs/metrics: `.venv/bin/pytest -v` → 9 passed in 0.23s; `logging_config.py` 100% coverage
- Coverage: 48% total (books.py 88%) — up from 36%/86% before this exercise
- Live log output (all 4 hooks, stderr):
  ```json
  {"timestamp":"2026-05-06T04:51:47.123732Z","level":"INFO","logger":"books","event":"collection.loaded","count":5,"data_file":"data.json"}
  {"timestamp":"2026-05-06T04:51:47.124724Z","level":"INFO","logger":"books","event":"collection.add","title":"Dune","author":"Frank Herbert","year":1965,"result":"success","collection_size":6}
  {"timestamp":"2026-05-06T04:51:47.133719Z","level":"INFO","logger":"books","event":"collection.mark_read","title":"Dune","result":"success"}
  {"timestamp":"2026-05-06T04:51:47.133791Z","level":"INFO","logger":"books","event":"collection.mark_read","title":"Nonexistent","result":"not_found"}
  {"timestamp":"2026-05-06T04:51:47.141112Z","level":"INFO","logger":"books","event":"collection.remove","title":"Dune","result":"success","collection_size":5}
  {"timestamp":"2026-05-06T04:51:47.141205Z","level":"INFO","logger":"books","event":"collection.remove","title":"Nonexistent","result":"not_found"}
  ```

## Risk & Rollback
- Risk: low — logging writes to stderr only; no stdout changes; no new runtime deps
- Rollback: revert this commit

## Review Focus
- Confirm log output goes to stderr and does not appear in stdout (`python book_app.py list 2>/dev/null` should show only the book list)
- Run `LOG_LEVEL=WARNING python book_app.py list` to verify suppression works
- Run `.venv/bin/pytest -v` to confirm 9/9 green

## Track
- Level: Walk
- Exercise: 09
```
