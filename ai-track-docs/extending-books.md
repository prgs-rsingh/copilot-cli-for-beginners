# Extending `books.py`

A short guide for adding new fields or behaviour to the `Book` / `BookCollection` module in `samples/book-app-project/`.

---

## Module at a Glance

| Symbol | Role |
|--------|------|
| `Book` | `@dataclass` — one row of the collection |
| `BookCollection` | Holds `List[Book]`; reads/writes `DATA_FILE` (JSON) |
| `DATA_FILE` | Module-level constant; override via `monkeypatch` in tests |

Persistence is intentionally simple: every mutating operation serialises the entire list back to `DATA_FILE` via `json.dump`.

---

## Adding a New Field to `Book`

1. **Add the field** to the `Book` dataclass in `books.py`:

   ```python
   @dataclass
   class Book:
       title: str
       author: str
       year: int
       read: bool = False
       genre: str = ""          # ← new field; give it a default so old JSON still loads
   ```

   Fields with defaults must come after fields without defaults — Python's dataclass rules.

2. **Existing JSON files** load fine because `Book(**b)` will use the default for any key not present in the stored dict.

3. **Add a test** that constructs a `Book` with and without the new field to confirm the default works:

   ```python
   def test_book_genre_defaults_to_empty_string():
       book = Book(title="Dune", author="Frank Herbert", year=1965)
       assert book.genre == ""
   ```

---

## Adding a New Query Method to `BookCollection`

Pattern — mirror the existing `find_by_author` style:

```python
def find_by_year(self, year: int) -> List[Book]:
    """Return all books published in *year*."""
    return [b for b in self.books if b.year == year]
```

Test checklist:
- Empty result when no book matches.
- Correct subset returned when multiple books match.
- Method does **not** mutate `self.books` (no `save_books()` call needed).

---

## Adding a New Mutating Method

Pattern — mirror `mark_as_read` / `remove_book`:

```python
def mark_as_unread(self, title: str) -> bool:
    """Reset the read flag.  Returns False if title not found."""
    book = self.find_book_by_title(title)
    if book:
        book.read = False
        self.save_books()   # ← always persist after mutation
        return True
    return False
```

Key rules:
- Always call `find_book_by_title` for lookup — keeps case-insensitivity in one place.
- Always call `self.save_books()` after changing state.
- Return `bool` (success/failure) so callers can branch without exceptions.

Test checklist:
- Returns `True` and state is changed for a known title.
- Returns `False` and state is unchanged for an unknown title.

---

## Changing the Persistence Back-end

All I/O is contained in two methods: `load_books` and `save_books`.  To swap JSON for SQLite, YAML, or a remote API, only those two methods need to change — the rest of the class is unaffected.

When replacing persistence, update the `use_temp_data_file` fixture in `tests/test_books.py` to match the new storage mechanism so tests remain isolated.

---

## Feature Toggles

`BookCollection` exposes constructor-level toggles that change behaviour without
altering the public method signatures.  Toggles default to `False` so existing
code is unaffected.

### `no_duplicates` — duplicate-title guard

| State | Behaviour |
|-------|-----------|
| `False` (default) | `add_book` silently allows multiple books with the same title |
| `True` | `add_book` raises `ValueError("a book titled '…' already exists")` on a case-insensitive title match |

```python
# OFF (default) — duplicates allowed
col = BookCollection()
col.add_book("Dune", "Herbert", 1965)
col.add_book("Dune", "Herbert", 1965)  # OK — two entries

# ON — duplicates rejected
strict = BookCollection(no_duplicates=True)
strict.add_book("Dune", "Herbert", 1965)
strict.add_book("dune", "Other", 2000)  # raises ValueError
```

**Adding a new toggle:** follow the same pattern — add a `bool` keyword argument
to `__init__`, store it as `self.<toggle_name>`, and guard the relevant method
with an `if self.<toggle_name>:` block.  Write two tests: one for `OFF` (default
behaviour preserved) and one for `ON` (new behaviour active).

---

## Resilience: `save_books` Retry / Backoff

`save_books` delegates all file I/O to the private `_save_with_retry` helper.
On an `OSError` it retries up to `SAVE_MAX_RETRIES` additional times, sleeping
`SAVE_RETRY_DELAY_S` seconds between attempts.

| Constant | Default | Meaning |
|----------|---------|---------|
| `SAVE_MAX_RETRIES` | `3` | Extra attempts after the first failure |
| `SAVE_RETRY_DELAY_S` | `0.1` | Fixed delay in seconds between retries |

After all attempts are exhausted, the helper raises:

```
OSError: save_books failed after N attempt(s)
```

chained from the original `OSError`.  Each failed attempt also logs a structured
warning line (see `logging.md`):

```json
{"op": "save_books", "status": "retry", "attempt": 1, "max": 2, "error": "…"}
```

### Overriding constants in tests

Both constants are module-level, so `monkeypatch.setattr` controls them without
touching function signatures:

```python
monkeypatch.setattr("books.SAVE_MAX_RETRIES", 1)   # only one extra attempt
monkeypatch.setattr("books.SAVE_RETRY_DELAY_S", 0.0)  # no sleep in tests
```

### What triggers / does not trigger a retry

| Condition | Retried? |
|-----------|---------|
| `OSError` (disk full, permission denied, …) | Yes |
| `ValueError`, `TypeError`, etc. | No — propagates immediately |

---

## Running Tests After Any Change

```bash
cd samples/book-app-project
pytest tests/ -v
```

All existing tests must stay green.  Add new tests for each new method, field, or toggle following the conventions in `tests/test_books.py`.
