# Run-12: Improvement Backlog — book-app-project Subsystem

**Generated**: 2026-05-06  
**Subsystem**: `samples/book-app-project/`  
**Tracker access**: None — committed as structured document per run-track convention.

No tracker available. All items documented here. At least one item (BL-01) includes a full delegation patch plan.

---

## Prioritised Backlog

| ID | Title | Priority | Effort | Good First Task? |
|---|---|---|---|---|
| BL-01 | Convert `load_books` validation warnings from `print()` to `logger.warning()` | High | S | ✅ Yes |
| BL-02 | Cover `JSONDecodeError` branch in `load_books` (books.py:54-58) | High | S | ✅ Yes |
| BL-03 | Remove repeated `logger.info("app.command")` in `main()` dispatch branches | Medium | S | ✅ Yes |
| BL-04 | Surface remove success/failure to user in `handle_remove()` | Medium | S | ✅ Yes |
| BL-05 | Migrate `open()` to `pathlib.Path.open()` (resolve PTH123 suppression) | Low | M | ⚠️ Requires care |

---

## BL-01 · Convert validation warnings from `print()` to `logger.warning()`

**Priority**: High  
**Effort**: S  
**Good first task**: Yes

### Problem

`load_books()` in `books.py` emits three data-quality warnings via `print()` to **stdout**:

```python
# books.py:41
print("Warning: skipping non-dict record in data.json")  # noqa: T201
# books.py:44
print(f"Warning: skipping record with unexpected field(s) {sorted(unexpected)} in data.json")  # noqa: T201
# books.py:48
print(f"Warning: skipping record missing required field(s) {sorted(missing)} in data.json")  # noqa: T201
```

These bypass the structured logging pipeline established in Run-08/09. They:
- Cannot be suppressed with `LOG_LEVEL`
- Do not appear in log aggregators
- Mix into CLI stdout (which is reserved for user-facing output)
- Cannot be tested with the `LogCapture` mock pattern

The `JSONDecodeError` warning on `books.py:57` has a `# intentional` comment explaining it must stay on stdout — that one is **excluded** from this item.

### Acceptance Criteria

- [ ] Replace all three `print("Warning: ...")` calls in `load_books()` with `logger.warning("collection.load_skip", extra={...})`
- [ ] Remove the `# noqa: T201` suppression comments on those three lines
- [ ] Each `logger.warning` call includes at least: `{"reason": str, "record_index": int}` (index in the source list)
- [ ] Add tests in `tests/test_logging.py` (or `tests/test_books.py`) asserting the three events fire with the correct reason field when a malformed data file is loaded
- [ ] `ruff check books.py` → clean (no T201 suppressions remaining for these lines)
- [ ] `pytest` → all existing tests pass; ≥3 new tests added

### Code Links

- `samples/book-app-project/books.py` lines 41, 44, 48 (the three `print()` warnings)
- `samples/book-app-project/tests/test_logging.py` (add new `TestBooksLoadSkip` class)

### Rollback

Remove the three new `logger.warning()` calls; restore original `print()` calls and `# noqa: T201` comments.

---

## BL-02 · Cover `JSONDecodeError` branch in `load_books` (books.py:54-58)

**Priority**: High  
**Effort**: S  
**Good first task**: Yes

### Problem

Coverage gap identified in Run-11. `books.py` lines 54-58 are the `except json.JSONDecodeError` handler:

```python
# books.py:56-58
except json.JSONDecodeError:
    print("Warning: data.json is corrupted. Starting with empty collection.")  # noqa: T201
    self.books = []
```

These 5 statements are never executed by any test. If a future refactor accidentally breaks this branch (e.g., swallows the exception silently or raises instead), no test would catch it.

### Acceptance Criteria

- [ ] Add a test in `tests/test_books.py` or `tests/test_security.py` that writes invalid JSON to the `DATA_FILE` path, constructs a `BookCollection`, and asserts `len(books) == 0`
- [ ] Test name: `test_corrupted_json_gives_empty_collection`
- [ ] Coverage for `books.py` lines 54-58: all statements covered
- [ ] Overall coverage: ≥ 98% (must not regress)
- [ ] `pytest` → all tests pass

### Code Links

- `samples/book-app-project/books.py` lines 54-58
- `samples/book-app-project/tests/test_books.py` (add test here)

### Rollback

Delete the new test. Coverage will return to 94% for `books.py` — acceptable.

---

## BL-03 · Remove repeated `logger.info("app.command")` in `main()` dispatch

**Priority**: Medium  
**Effort**: S  
**Good first task**: Yes

### Problem

`main()` in `book_app.py` repeats an identical `logger.info("app.command", extra={"command": command})` in each `if/elif` branch:

```python
# book_app.py:67-88 — five identical log calls
if command == "list":
    logger.info("app.command", extra={"command": command})   # ← repeated
    handle_list()
elif command == "add":
    logger.info("app.command", extra={"command": command})   # ← repeated
    handle_add()
# ... and so on for remove, find, help
```

The log event fires before each handler, which means the log call can be hoisted above the dispatch block — one call instead of five. This reduces the chance of a future branch forgetting the log event.

### Acceptance Criteria

- [ ] Single `logger.info("app.command", extra={"command": command})` call placed before the `if/elif` chain — but only for recognised commands (not for the `else` / unknown branch)
- [ ] The `else` branch still logs `logger.warning("app.unknown_command", ...)` as before
- [ ] All 5 per-branch `logger.info("app.command")` calls removed
- [ ] `tests/test_logging.py::TestBookAppLogging::test_known_command_emits_app_command` still passes
- [ ] `pytest` → all 107 tests pass

### Code Links

- `samples/book-app-project/book_app.py` lines 67-88

### Rollback

Revert to per-branch log calls by restoring the original `main()` body.

---

## BL-04 · Surface remove success/failure to user in `handle_remove()`

**Priority**: Medium  
**Effort**: S  
**Good first task**: Yes

### Problem

`handle_remove()` in `book_app.py` ignores the `bool` return value from `collection.remove_book()`:

```python
# book_app.py:35-38
def handle_remove():
    print("\nRemove a Book\n")
    title = prompt("Enter the title of the book to remove: ")
    collection.remove_book(title)                   # return value discarded
    print("\nBook removed if it existed.\n")        # ambiguous — always printed
```

The message "Book removed if it existed." is intentionally hedged, but this is poor UX — the user cannot tell whether their book was found and removed or never existed. `collection.remove_book()` already returns `True`/`False`.

### Acceptance Criteria

- [ ] Capture the return value: `removed = collection.remove_book(title)`
- [ ] Print `"\nBook removed successfully.\n"` if `removed is True`
- [ ] Print `"\nNo book found with that title.\n"` if `removed is False`
- [ ] Add or update a test in `tests/test_book_app.py` covering both branches
- [ ] `pytest` → all tests pass

### Code Links

- `samples/book-app-project/book_app.py` lines 35-38 (`handle_remove`)
- `samples/book-app-project/tests/test_book_app.py` (update existing remove test)

### Rollback

Revert `handle_remove()` to single `print("\nBook removed if it existed.\n")`.

---

## BL-05 · Migrate `open()` to `pathlib.Path.open()` (resolve PTH123 suppression)

**Priority**: Low  
**Effort**: M  
**Good first task**: ⚠️ Requires care (two locations, atomic write pattern must be preserved)

### Problem

Two `open()` calls in `books.py` are suppressed with `# noqa: PTH123`:

```python
# books.py:37
with open(DATA_FILE) as f:  # noqa: PTH123 -- pathlib migration is a separate backlog item
# books.py:78
with open(tmp_path, "w") as f:  # noqa: PTH123 -- pathlib migration is a separate backlog item
```

These were deferred at the time of writing (Run-08 comment says "backlog.md item 1"). The modern Python idiom is `Path(DATA_FILE).open()`. Migrating removes the suppressions and aligns with `UP` ruff rules.

### Acceptance Criteria

- [ ] `DATA_FILE` type changed from `str` to `pathlib.Path` (or keep as `str` and convert at point of use — document choice)
- [ ] `open(DATA_FILE)` → `Path(DATA_FILE).open()`
- [ ] `open(tmp_path, "w")` → `Path(tmp_path).open("w")` (preserve atomic write pattern: write to `.tmp`, then `Path(tmp_path).replace(Path(DATA_FILE))`)
- [ ] Remove both `# noqa: PTH123` comments and the `# backlog item` references
- [ ] `ruff check books.py` → no PTH123 findings
- [ ] All atomic write tests in `tests/test_security.py::TestAtomicWrite` still pass
- [ ] `pytest` → all 107 tests pass

### Code Links

- `samples/book-app-project/books.py` lines 37, 78 (both `open()` calls)
- `samples/book-app-project/tests/test_security.py::TestAtomicWrite` (verify after migration)

### Rollback

Restore `open(DATA_FILE)` and `open(tmp_path, "w")` calls; re-add `# noqa: PTH123` comments.

---

## Delegation Patch Plan: BL-01

This item is selected as the **good first delegation task** because:
- Scope is tightly bounded to 3 lines in one function
- Pattern is established (`LogCapture` in `test_logging.py`)
- No behaviour changes — only output channel changes (stdout → logger)
- Rollback is trivial

### Delegate Prompt

> In `samples/book-app-project/books.py`, the `load_books()` method emits three
> data-quality warnings via `print()` to stdout (lines 41, 44, 48). Replace each
> one with a structured `logger.warning("collection.load_skip", extra={...})` call.
>
> Each call must include at least:
> - `"reason"`: a short string — `"non_dict_record"`, `"unexpected_fields"`, or `"missing_required_fields"`
> - `"skipped_fields"` or `"missing_fields"` where applicable (the sorted list already computed)
>
> Remove the `# noqa: T201` suppressions from those three lines only (leave the
> `JSONDecodeError` print on line 57 — it has a different rationale).
>
> Then add a `TestBooksLoadSkip` class to `tests/test_logging.py` with three tests:
> - `test_non_dict_record_emits_warning`
> - `test_unexpected_field_emits_warning`
> - `test_missing_required_field_emits_warning`
>
> Each test must use `monkeypatch` to set `books.DATA_FILE` to a temp file, write
> a crafted JSON list to it, construct a `BookCollection()`, and assert the
> `LogCapture` mock (monkeypatched onto `books.logger`) received a
> `"collection.load_skip"` event with the correct `"reason"` value.
>
> Acceptance: `ruff check books.py` clean (no T201); `pytest` → all existing 107
> tests pass + 3 new tests.

### Execution Phases

| Phase | Action | Acceptance |
|---|---|---|
| 1 | Replace 3 `print()` warnings with `logger.warning("collection.load_skip", extra={...})` in `books.py` | `ruff check books.py` clean |
| 2 | Add `TestBooksLoadSkip` to `test_logging.py` with 3 tests | `pytest tests/test_logging.py` → 10 passed (was 7) |
| 3 | Full suite regression check | `pytest --cov` → ≥107 passed, ≥98% |

### Phase 1 Preview (diff)

```diff
-                    if not isinstance(record, dict):
-                        print("Warning: skipping non-dict record in data.json")  # noqa: T201
-                        continue
+                    if not isinstance(record, dict):
+                        logger.warning(
+                            "collection.load_skip",
+                            extra={"reason": "non_dict_record"},
+                        )
+                        continue

-                    unexpected = set(record.keys()) - _BOOK_ALLOWED_FIELDS
-                    if unexpected:
-                        print(f"Warning: skipping record with unexpected field(s) {sorted(unexpected)} in data.json")  # noqa: T201
-                        continue
+                    unexpected = set(record.keys()) - _BOOK_ALLOWED_FIELDS
+                    if unexpected:
+                        logger.warning(
+                            "collection.load_skip",
+                            extra={"reason": "unexpected_fields", "skipped_fields": sorted(unexpected)},
+                        )
+                        continue

-                    if not _BOOK_REQUIRED_FIELDS.issubset(record.keys()):
-                        missing = _BOOK_REQUIRED_FIELDS - set(record.keys())
-                        print(f"Warning: skipping record missing required field(s) {sorted(missing)} in data.json")  # noqa: T201
-                        continue
+                    if not _BOOK_REQUIRED_FIELDS.issubset(record.keys()):
+                        missing = _BOOK_REQUIRED_FIELDS - set(record.keys())
+                        logger.warning(
+                            "collection.load_skip",
+                            extra={"reason": "missing_required_fields", "missing_fields": sorted(missing)},
+                        )
+                        continue
```

### Rollback

```bash
git checkout HEAD -- samples/book-app-project/books.py
git checkout HEAD -- samples/book-app-project/tests/test_logging.py
```

---

## Acceptance Checklist

- [x] 5 actionable backlog items created (BL-01 through BL-05)
- [x] Acceptance criteria included for each item
- [x] Linked to specific file paths and line numbers
- [x] Committed as structured document (`ai-track-docs/run-12-backlog.md`)
- [x] BL-01 includes a full delegation patch plan with delegate prompt, phases, diff preview, and rollback
- [x] At least 3 items are good first tasks (BL-01, BL-02, BL-03, BL-04)
- [x] Priority and effort estimated for each item

---

## PR Description

```markdown
## Title
GHCP -- Run: 12 Backlog Generation — 5 Improvement Issues for book-app-project

## Summary
Analysed `samples/book-app-project/` subsystem and generated 5 prioritised
improvement backlog items with acceptance criteria, code links, and effort estimates.

| ID | Title | Priority |
|---|---|---|
| BL-01 | Convert load_books warnings from print() to logger.warning() | High |
| BL-02 | Cover JSONDecodeError branch (books.py:54-58) | High |
| BL-03 | Hoist repeated app.command log call in main() dispatch | Medium |
| BL-04 | Surface remove success/failure in handle_remove() | Medium |
| BL-05 | Migrate open() to pathlib.Path.open() (PTH123) | Low |

BL-01 includes a full delegation patch plan (delegate prompt, execution phases,
diff preview, rollback commands).

No tracker access — backlog committed to `ai-track-docs/run-12-backlog.md`.

## Track
- Level: Run
- Exercise: 12
```
