# Backlog — Exercise 12: Repo Findings

Items derived from code review of `samples/book-app-project/` during the Crawl track.
No external tracker is available; this file is the source of truth.

**Priority key:** P1 = should do soon · P2 = next sprint · P3 = nice-to-have

---

## ITEM-01 — Route `load_books` warning through the structured logger

**Priority:** P1  
**Code link:** [`books.py` line 85](../samples/book-app-project/books.py#L85)

### Finding

`load_books` uses a bare `print()` to report corrupted JSON:

```python
print("Warning: data.json is corrupted. Starting with empty collection.")
```

This leaks a warning onto **stdout** (the app's user-facing stream), bypasses the structured logger introduced in ex-09, and cannot be filtered or suppressed in tests.

### Acceptance Criteria

- [ ] Replace the `print()` call with `_log.warning(json.dumps({...}))` using the existing `_log` logger.
- [ ] The message appears on **stderr**, not stdout.
- [ ] Running `pytest tests/ -v` stays 12/12 green.
- [ ] With `BOOK_APP_LOG_LEVEL=WARNING python book_app.py`, a corrupted `data.json` produces a JSON line on stderr.

---

## ITEM-02 — Report remove outcome to the user in `handle_remove`

**Priority:** P1  
**Code link:** [`book_app.py` lines 44–49](../samples/book-app-project/book_app.py#L44)

### Finding

`handle_remove` ignores the `bool` returned by `collection.remove_book()` and always prints the ambiguous message `"Book removed if it existed."`:

```python
collection.remove_book(title)
print("\nBook removed if it existed.\n")
```

A student who misremembers a title gets no feedback that nothing happened — a confusing UX and a missed teaching moment about using return values.

### Acceptance Criteria

- [ ] `handle_remove` branches on the return value of `remove_book`.
- [ ] Prints `"'<title>' removed successfully."` on `True`.
- [ ] Prints `"No book titled '<title>' was found."` on `False`.
- [ ] Behaviour is manually verifiable by running `python book_app.py remove`.
- [ ] No new tests required (CLI layer); existing 12 tests stay green.

---

## ITEM-03 — Add CI workflow for the JavaScript sample app

**Priority:** P2  
**Code link:** [`.github/workflows/`](../.github/workflows/) · [`samples/book-app-project-js/`](../samples/book-app-project-js/)

### Finding

The Python sample has a GitHub Actions matrix (`python-tests.yml`) covering Python 3.10–3.13.  The JavaScript sample (`book-app-project-js/`) has no CI — its `node --test` suite runs only locally.

### Acceptance Criteria

- [ ] New workflow file `.github/workflows/js-tests.yml` created.
- [ ] Triggers on push/PR touching `samples/book-app-project-js/**`.
- [ ] Matrix: Node 18, 20, 22 on `ubuntu-latest`.
- [ ] Command: `npm test` inside `samples/book-app-project-js/`.
- [ ] `engines` field in `package.json` already constrains `>=18 <24` — workflow must respect this.
- [ ] Workflow completes green on the current test suite.

---

## ITEM-04 — Extract the `use_temp_data_file` fixture into `conftest.py`

**Priority:** P2  
**Code link:** [`tests/test_books.py` lines 10–14](../samples/book-app-project/tests/test_books.py#L10)

### Finding

The `use_temp_data_file` autouse fixture is defined inline in `test_books.py`.  The [test file conventions](build-test.md) already state: *"Fixtures and helpers stay in `conftest.py` (create if needed)."*  As the suite grows, any new test file would need to duplicate or import this fixture — which `conftest.py` handles automatically.

### Acceptance Criteria

- [ ] `samples/book-app-project/tests/conftest.py` created containing the `use_temp_data_file` fixture (moved verbatim, not copied).
- [ ] The fixture is removed from `test_books.py`.
- [ ] `pytest tests/ -v` stays 12/12 green with no changes to test logic.
- [ ] `conftest.py` has a one-line module docstring explaining its purpose.

---

## ITEM-05 — Add `find_by_year` query method and a matching test

**Priority:** P3  
**Code link:** [`books.py` — end of `BookCollection`](../samples/book-app-project/books.py) · [`extending-books.md`](extending-books.md)

### Finding

`BookCollection` exposes `find_by_author` but no equivalent year-based query.  The [extending guide](extending-books.md) already shows the pattern for adding new query methods and uses `find_by_year` as its example — but the method does not exist yet, making the guide's example unrunnable.

### Acceptance Criteria

- [ ] `find_by_author` is consistent with the docstring in [`extending-books.md`](extending-books.md).
- [ ] `BookCollection.find_by_year(year: int) -> List[Book]` added to `books.py` with a one-line docstring.
- [ ] Two tests added to `test_books.py`:
  - `test_find_by_year_returns_matching_books` — multiple books, only correct year returned.
  - `test_find_by_year_returns_empty_when_no_match` — year absent in collection.
- [ ] Perf baseline in [`perf-baseline.md`](perf-baseline.md) updated with a `find_by_year` row if the new method is slower than `find_by_author` by > 10 %.
- [ ] All existing 12 tests stay green.
