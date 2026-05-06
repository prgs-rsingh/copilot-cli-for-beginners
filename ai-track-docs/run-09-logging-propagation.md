# Run-09: Consistent Logging Across book-app-project

## Mini Prompt
Add consistent logging/metrics across a folder; document how to validate.
Propagate logging/metric pattern across the folder.

---

## Current State Audit (Before)

| File | Logger? | Events logged |
|---|---|---|
| `books.py` | ✅ Yes | `collection.loaded`, `collection.add`, `collection.mark_read`, `collection.remove` |
| `logging_config.py` | ✅ Yes (defines it) | — |
| `book_app.py` | ❌ No | — |
| `utils.py` | ❌ No | — |
| `resilience.py` | ❌ No | — |

3 of 5 source modules had zero instrumentation. `book_app.py` is the CLI dispatcher — every command was invisible. `resilience.py` retry attempts and exhaustion were silent. `utils.py` year parse failures went untracked.

---

## Pattern Propagated

Established pattern (from `books.py`):
```python
from logging_config import get_logger
logger = get_logger(__name__)

logger.info("event.name", extra={"field": value, ...})
logger.warning("event.name", extra={"field": value})
logger.error("event.name", extra={"field": value})
```
All output: single-line JSON to stderr. Level: `LOG_LEVEL` env var (default `INFO`).
Event names: `<module>.<action>` dot-notation.

---

## Events Added

### `book_app.py` (3 events)

| Event | Level | Trigger | Fields |
|---|---|---|---|
| `app.command` | INFO | Every valid command dispatch | `command` |
| `app.error` | WARNING | ValueError during `handle_add` | `command`, `error` |
| `app.unknown_command` | WARNING | Unrecognised command | `command` |

### `utils.py` (2 events)

| Event | Level | Trigger | Fields |
|---|---|---|---|
| `year.parse_error` | WARNING | ValueError in `get_book_details` | `input`, `reason` |
| `year.parse_rejected` | INFO | Strict year guard fires | `year`, `limit`, `strict` |

### `resilience.py` (2 events)

| Event | Level | Trigger | Fields |
|---|---|---|---|
| `retry.attempt` | WARNING | Non-final retry fires | `fn`, `attempt`, `max`, `delay_s`, `error` |
| `retry.exhausted` | ERROR | All retries consumed | `fn`, `attempts`, `error` |

---

## Files Changed

| File | Change |
|---|---|
| `book_app.py` | Added `from logging_config import get_logger`; `logger = get_logger(__name__)`; 3 log events |
| `utils.py` | Added `from logging_config import get_logger`; `logger = get_logger(__name__)`; 2 log events |
| `resilience.py` | Added `from logging_config import get_logger`; `logger = get_logger(__name__)`; 2 log events in retry loop |
| `tests/test_logging.py` | New — 7 tests verifying all 7 events fire with correct levels and fields |

Also fixed: `fn.__name__` → `getattr(fn, "__name__", repr(fn))` in `resilience.py` to handle mock callables in tests.

---

## How to Validate

### Live log output
```bash
cd samples/book-app-project
LOG_LEVEL=INFO .venv/bin/python book_app.py list 2>&1
```

Expected output (stderr JSON + stdout CLI):
```json
{"timestamp": "2026-05-06T10:06:01.943891Z", "level": "INFO", "logger": "books", "event": "collection.loaded", "count": 5, "data_file": "data.json"}
{"timestamp": "2026-05-06T10:06:01.944208Z", "level": "INFO", "logger": "__main__", "event": "app.command", "command": "list"}
```

### Grep for specific events
```bash
LOG_LEVEL=INFO .venv/bin/python book_app.py list 2>&1 | grep '"event"'
# Expected: "event": "collection.loaded" and "event": "app.command"

# Test retry logging (simulate by running with LOG_LEVEL=DEBUG):
LOG_LEVEL=DEBUG .venv/bin/python book_app.py add 2>&1
# On a transient OSError, look for: "event": "retry.attempt"
```

### Filter to JSON only (stderr)
```bash
LOG_LEVEL=INFO .venv/bin/python book_app.py list 2>/tmp/app.log; cat /tmp/app.log | python -m json.tool
```

### Run the instrumentation test suite
```bash
.venv/bin/pytest tests/test_logging.py -v
# Expected: 7 passed
```

---

## Steps Run

| Step | Outcome |
|---|---|
| Committed `run-09-logging-propagation.md` as patch plan | ✅ |
| Audit: 3/5 source modules uninstrumented | ✅ |
| Propagated logger to `book_app.py` (3 events) | ✅ |
| Propagated logger to `utils.py` (2 events) | ✅ |
| Propagated logger to `resilience.py` (2 events) | ✅ |
| Fixed `fn.__name__` → `getattr(fn, "__name__", repr(fn))` | ✅ |
| Created `tests/test_logging.py` (7 tests) using `LogCapture` mock | ✅ |
| `pytest tests/test_logging.py` → 7 passed | ✅ |
| Full suite `pytest --cov` → **107 passed, 98%** | ✅ |
| Live log sample captured | ✅ |

---

## Evidence

### Test run
```
tests/test_logging.py::TestBookAppLogging::test_known_command_emits_app_command  PASSED
tests/test_logging.py::TestBookAppLogging::test_unknown_command_emits_warning     PASSED
tests/test_logging.py::TestBookAppLogging::test_add_error_emits_app_error        PASSED
tests/test_logging.py::TestUtilsLogging::test_invalid_year_emits_parse_error      PASSED
tests/test_logging.py::TestUtilsLogging::test_strict_year_out_of_range_emits_parse_rejected PASSED
tests/test_logging.py::TestResilienceLogging::test_retry_attempt_logged_on_transient_failure PASSED
tests/test_logging.py::TestResilienceLogging::test_retry_exhausted_logged_after_all_retries_fail PASSED
7 passed
```

### Full suite
```
book_app.py        56      0   100%
books.py           85      5    94%   54-58
logging_config.py  22      0   100%
resilience.py      31      0   100%
utils.py           45      0   100%
TOTAL             239      5    98%
107 passed in 0.74s
```

### Live log sample (`LOG_LEVEL=INFO .venv/bin/python book_app.py list 2>&1`)
```json
{"timestamp": "2026-05-06T10:06:01.943891Z", "level": "INFO", "logger": "books", "event": "collection.loaded", "count": 5, "data_file": "data.json"}
{"timestamp": "2026-05-06T10:06:01.944208Z", "level": "INFO", "logger": "__main__", "event": "app.command", "command": "list"}
```

---

## After State

| File | Logger? | Events |
|---|---|---|
| `books.py` | ✅ | `collection.loaded`, `collection.add`, `collection.mark_read`, `collection.remove` |
| `book_app.py` | ✅ **added** | `app.command`, `app.error`, `app.unknown_command` |
| `utils.py` | ✅ **added** | `year.parse_error`, `year.parse_rejected` |
| `resilience.py` | ✅ **added** | `retry.attempt`, `retry.exhausted` |
| `logging_config.py` | ✅ | — |

---

## Delegation Checklist

- [x] Patch plan created (audit, events per module, scope)
- [x] Pattern propagated to all 3 uninstrumented files
- [x] Event names consistent (`<module>.<action>` dot-notation)
- [x] 7 new instrumentation tests (LogCapture mock approach)
- [x] Full suite passing (107/107, 98%)
- [x] Validation instructions documented (live log + grep + test suite)
- [x] Live log sample captured as evidence
- [x] Context file saved to `ai-track-docs/run-09-logging-propagation.md`

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| Logging added across multiple related files | ✅ 3 files: `book_app.py`, `utils.py`, `resilience.py` |
| Docs explain how to validate instrumentation | ✅ 4 validation methods above |
| Evidence of logs captured | ✅ Live JSON sample + test output |
| Pattern is consistent across the folder | ✅ Same `get_logger(__name__)` + dot-notation events in all 5 modules |

---

## PR Description

```markdown
## Title
GHCP -- Run: 09 Logging Propagation — Instrument book_app, utils, resilience

## Summary
Audited `samples/book-app-project/`: 3 of 5 source modules had zero logging.
Propagated the established `get_logger(__name__)` + JSON stderr pattern to all three.
Added 7 events total:
- `book_app.py`: `app.command` (INFO), `app.error` (WARNING), `app.unknown_command` (WARNING)
- `utils.py`: `year.parse_error` (WARNING), `year.parse_rejected` (INFO)
- `resilience.py`: `retry.attempt` (WARNING), `retry.exhausted` (ERROR)
Added `tests/test_logging.py` (7 tests) using `LogCapture` mock to verify each event.
Fixed `fn.__name__` → `getattr(fn, "__name__", repr(fn))` in resilience.py.
Patch plan: `ai-track-docs/run-09-logging-propagation.md`

## Evidence
- `pytest tests/test_logging.py` → **7 passed**
- Full suite → **107 passed, 98%** — zero regressions
- Live log: `LOG_LEVEL=INFO .venv/bin/python book_app.py list 2>&1`
  → JSON events from both `books` and `__main__` loggers

## Risk & Rollback
- Risk: very low — logging is additive; no behavior changes for valid inputs
- Rollback per file: remove `from logging_config import get_logger`, `logger = get_logger(...)`, and each `logger.*()` call

## Track
- Level: Run
- Exercise: 09
```
