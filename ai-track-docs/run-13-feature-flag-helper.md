# Run-13: Feature Flag Helper — BOOK_APP_STRICT_REMOVE

## Mini Prompt
Add a safety switch/flag for a higher-risk behavior change and validate
ON/OFF. Introduce a flag helper pattern across a module; add telemetry
if available.

---

## Problem

`handle_remove()` always printed the hedged message "Book removed if it existed."
regardless of whether the book was found — a UX gap identified as BL-04.
Changing the message is a higher-risk behavior change because scripts or learners
may assert on that exact string. A feature flag lets it be adopted incrementally.

Additionally, the flag evaluation logic was duplicated: `_strict_year_enabled()`
inline-repeated `os.environ.get(...).lower() in (...)`. Extracting a shared
`_flag_enabled()` helper gives a single place to add telemetry and ensures all
flags follow the same convention.

---

## Flag Helper Pattern

### Naming convention
`BOOK_APP_<FEATURE>` — all uppercase, underscore-separated, `BOOK_APP_` prefix.

### Truthy values
`1`, `true`, `yes` (case-insensitive). All other values (including unset) = OFF.

### Implementation (`utils.py`)

```python
_BOOK_APP_TRUTHY = frozenset({"1", "true", "yes"})
_logged_flags: set[str] = set()   # dedup: emit telemetry once per flag per process

def _flag_enabled(env_var: str) -> bool:
    result = os.environ.get(env_var, "").lower() in _BOOK_APP_TRUTHY
    if result and env_var not in _logged_flags:
        _logged_flags.add(env_var)
        logger.info("flag.active", extra={"flag": env_var})
    return result
```

**Telemetry**: `flag.active` INFO event emitted **once per flag per process lifetime**
when the flag is ON. Silent when OFF.

---

## Flags

| Flag | Default | Behavior when ON |
|---|---|---|
| `BOOK_APP_STRICT_YEAR` | OFF | `parse_year()` enforces `[1, current_year]` range |
| `BOOK_APP_STRICT_REMOVE` | OFF (**new**) | `handle_remove()` prints precise success/failure message |

---

## Files Changed

| File | Change |
|---|---|
| `utils.py` | Added `_BOOK_APP_TRUTHY`, `_logged_flags`, `_flag_enabled()`; refactored `_strict_year_enabled()`; added `_strict_remove_enabled()` |
| `book_app.py` | Import `_strict_remove_enabled`; updated `handle_remove()` to branch on flag |
| `tests/test_feature_flags.py` | Added `LogCapture`, `collection_with_book` fixture, `TestStrictRemoveOff` (2), `TestStrictRemoveOn` (7), `TestFlagTelemetry` (3) = 12 new tests |

---

## ON/OFF Behavior Validation

### FLAG OFF (default — `BOOK_APP_STRICT_REMOVE` unset)

```
$ echo "Dune" | LOG_LEVEL=INFO python book_app.py remove

Remove a Book
Enter the title of the book to remove:
Book removed if it existed.

stderr (log):
{"event": "collection.loaded", "count": 5, ...}
{"event": "app.command", "command": "remove"}
{"event": "collection.remove", "title": "Dune", "result": "success", ...}
# No flag.active event — flag is OFF, telemetry is silent
```

### FLAG ON (`BOOK_APP_STRICT_REMOVE=1`)

**Remove found book:**
```
$ echo "Dune" | LOG_LEVEL=INFO BOOK_APP_STRICT_REMOVE=1 python book_app.py remove

Remove a Book
Enter the title of the book to remove:
Book removed successfully.          ← precise success message

stderr (log):
{"event": "collection.loaded", ...}
{"event": "app.command", "command": "remove"}
{"event": "collection.remove", "title": "Dune", "result": "success", ...}
{"event": "flag.active", "flag": "BOOK_APP_STRICT_REMOVE"}  ← telemetry
```

**Remove not-found book:**
```
$ echo "Nonexistent" | LOG_LEVEL=INFO BOOK_APP_STRICT_REMOVE=1 python book_app.py remove

Remove a Book
Enter the title of the book to remove:
No book found with that title.      ← precise failure message

stderr (log):
{"event": "collection.remove", "title": "Nonexistent", "result": "not_found"}
{"event": "flag.active", "flag": "BOOK_APP_STRICT_REMOVE"}
```

---

## Steps Run

| Step | Outcome |
|---|---|
| Committed `run-13-feature-flag-helper.md` as patch plan | ✅ |
| Phase 1: Extracted `_flag_enabled()` + `_strict_remove_enabled()` in `utils.py` | ✅ |
| Phase 2: Updated `handle_remove()` in `book_app.py` | ✅ |
| Phase 3: Added 12 new tests to `test_feature_flags.py` | ✅ |
| Fixed I001: `_strict_remove_enabled` sort order in imports | ✅ |
| `ruff check` → All checks passed | ✅ |
| `pytest tests/test_feature_flags.py` → 42 passed | ✅ |
| Full suite → **124 passed, 98%** | ✅ |
| Live ON/OFF evidence captured | ✅ |

---

## Test Evidence

```
tests/test_feature_flags.py::TestStrictRemoveOff::test_found_book_prints_hedged_message    PASSED
tests/test_feature_flags.py::TestStrictRemoveOff::test_missing_book_prints_hedged_message  PASSED
tests/test_feature_flags.py::TestStrictRemoveOn::test_found_book_prints_success            PASSED
tests/test_feature_flags.py::TestStrictRemoveOn::test_missing_book_prints_not_found        PASSED
tests/test_feature_flags.py::TestStrictRemoveOn::test_flag_truthy_values[1]                PASSED
tests/test_feature_flags.py::TestStrictRemoveOn::test_flag_truthy_values[true]             PASSED
tests/test_feature_flags.py::TestStrictRemoveOn::test_flag_truthy_values[yes]              PASSED
tests/test_feature_flags.py::TestStrictRemoveOn::test_flag_falsy_values_give_hedged_message[0]      PASSED
tests/test_feature_flags.py::TestStrictRemoveOn::test_flag_falsy_values_give_hedged_message[false]  PASSED
tests/test_feature_flags.py::TestFlagTelemetry::test_flag_active_emits_telemetry_when_on   PASSED
tests/test_feature_flags.py::TestFlagTelemetry::test_flag_active_not_emitted_when_off      PASSED
tests/test_feature_flags.py::TestFlagTelemetry::test_flag_active_emitted_only_once_per_process  PASSED
42 passed (feature flags module total)
```

Full suite:
```
book_app.py        60      0   100%
books.py           85      5    94%   54-58
logging_config.py  22      0   100%
resilience.py      31      0   100%
utils.py           55      0   100%
TOTAL             253      5    98%
124 passed in 0.59s
```

---

## Documentation

### How to enable
```bash
BOOK_APP_STRICT_REMOVE=1 python book_app.py remove
```

### How to confirm flag is active
```bash
LOG_LEVEL=INFO BOOK_APP_STRICT_REMOVE=1 python book_app.py remove 2>&1 | grep flag.active
# → {"event": "flag.active", "flag": "BOOK_APP_STRICT_REMOVE", ...}
```

### Rollback
```bash
# Option 1: unset the env var (flag returns to default OFF)
unset BOOK_APP_STRICT_REMOVE

# Option 2: revert code changes
git checkout HEAD -- samples/book-app-project/utils.py
git checkout HEAD -- samples/book-app-project/book_app.py
git checkout HEAD -- samples/book-app-project/tests/test_feature_flags.py
```

---

## Acceptance Checklist

- [x] Flag helper pattern implemented — `_flag_enabled(env_var)` in `utils.py`
- [x] ON/OFF behavior validated with evidence — live log samples above
- [x] Documentation updated — flag name, truthy values, how to confirm, rollback
- [x] Rollback path identified — unset env var (code-free rollback) or `git checkout`
- [x] Telemetry added — `flag.active` INFO event via existing `get_logger` infrastructure; deduplicated to once per process

---

## PR Description

```markdown
## Title
GHCP -- Run: 13 Feature Flag Helper — BOOK_APP_STRICT_REMOVE + telemetry

## Summary
Introduced a shared `_flag_enabled(env_var)` helper in `utils.py` to standardise
all `BOOK_APP_*` feature flag evaluation. Refactored existing `_strict_year_enabled()`
to delegate to it.

**New flag: `BOOK_APP_STRICT_REMOVE`**
When ON, `handle_remove()` surfaces precise success/failure feedback instead of
the hedged "Book removed if it existed." message (delivers BL-04 safely).

**Telemetry:**
- `flag.active` INFO event emitted once per flag per process when ON
- Silent when OFF — no log noise in default mode
- Visible via: `LOG_LEVEL=INFO python book_app.py remove 2>&1 | grep flag.active`

## Evidence
- FLAG OFF: prints "Book removed if it existed." (unchanged)
- FLAG ON (found): prints "Book removed successfully." + `flag.active` in log
- FLAG ON (not found): prints "No book found with that title." + `flag.active` in log
- 12 new tests (TestStrictRemoveOff, TestStrictRemoveOn, TestFlagTelemetry)
- Full suite: **124 passed, 98%** — zero regressions
- ruff: All checks passed

## Rollback
`unset BOOK_APP_STRICT_REMOVE` — no code change needed (default is OFF)

## Track
- Level: Run
- Exercise: 13
```
