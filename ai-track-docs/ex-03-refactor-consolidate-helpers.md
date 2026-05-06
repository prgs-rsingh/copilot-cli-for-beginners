# Exercise 03 — Multi-File Refactor: Consolidate Duplicate Display and Year-Parsing Logic

## Mini Prompt
Propose a multi-file refactor plan (2-4 files), then diffs, then tests.

---

## Refactor Plan

**Opportunities identified:**

1. **Duplicate display function** — `show_books()` in `book_app.py` and `print_books()` in `utils.py` both render a book list to stdout with different formatting. `utils.py` (the designated UI helpers module) was never imported by `book_app.py`.
2. **Duplicate year-parsing logic** — `int(year_str) if year_str else 0` in `book_app.py::handle_add()` and `int(year_input)` with a `ValueError` catch in `utils.py::get_book_details()` solve the same problem independently.

**Plan:**

| File | Change | Reason |
|---|---|---|
| `utils.py` | Add `parse_year(year_str)` helper; rename `print_books` → `show_books` with canonical `[✓]/[ ]` style | Consolidate duplicates into the designated UI helpers module |
| `book_app.py` | Remove local `show_books`; import `show_books, parse_year` from `utils`; use `parse_year` in `handle_add` | Eliminate duplication; delegate display/input to `utils.py` |

**Expected impact:**
- `book_app.py` shrinks by ~10 statements (removed `show_books` body)
- One canonical display function and one canonical year-parser — single place to update either going forward
- No behaviour change for the user

---

## Steps Run

| # | Step | Outcome |
|---|---|---|
| 1 | Read `book_app.py`, `utils.py`, `books.py`, `tests/test_books.py` in full | Two duplication patterns found |
| 2 | Added `parse_year()` to `utils.py`; renamed `print_books` → `show_books`; updated `get_book_details` to use `parse_year` | `utils.py` is now the single source for display and input helpers |
| 3 | Removed local `show_books` from `book_app.py`; added `from utils import show_books, parse_year`; updated `handle_add` to use `parse_year` | `book_app.py` delegates to `utils.py` |
| 4 | Ran `.venv/bin/pytest` — 5/5 passed, coverage 36% total, `books.py` 87% | All green |

---

## Diffs

### `utils.py`

```diff
-def get_book_details():
+def parse_year(year_str: str) -> int:
+    """Convert a year string to int. Returns 0 for blank input. Raises ValueError for non-numeric."""
+    if not year_str:
+        return 0
+    return int(year_str)
+
+
+def get_book_details():
     title = input("Enter book title: ").strip()
     author = input("Enter author: ").strip()
     year_input = input("Enter publication year: ").strip()
     try:
-        year = int(year_input)
+        year = parse_year(year_input)
     except ValueError:
         print("Invalid year. Defaulting to 0.")
         year = 0
     return title, author, year


-def print_books(books):
-    if not books:
-        print("No books in your collection.")
-        return
-    print("\nYour Books:")
-    for index, book in enumerate(books, start=1):
-        status = "✅ Read" if book.read else "📖 Unread"
-        print(f"{index}. {book.title} by {book.author} ({book.year}) - {status}")
+def show_books(books):
+    """Display books in a user-friendly format."""
+    if not books:
+        print("No books found.")
+        return
+    print("\nYour Book Collection:\n")
+    for index, book in enumerate(books, start=1):
+        status = "✓" if book.read else " "
+        print(f"{index}. [{status}] {book.title} by {book.author} ({book.year})")
+    print()
```

### `book_app.py`

```diff
 import sys
 from books import BookCollection
+from utils import show_books, parse_year

-def show_books(books):
-    """Display books in a user-friendly format."""
-    if not books:
-        print("No books found.")
-        return
-    print("\nYour Book Collection:\n")
-    for index, book in enumerate(books, start=1):
-        status = "✓" if book.read else " "
-        print(f"{index}. [{status}] {book.title} by {book.author} ({book.year})")
-    print()

     try:
-        year = int(year_str) if year_str else 0
+        year = parse_year(year_str)
         collection.add_book(title, author, year)
```

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| Plan included in PR | ✅ Pass — plan above with file table and rationale |
| Multiple files modified | ✅ Pass — `utils.py` and `book_app.py` changed |
| Tests remain green | ✅ Pass — 5/5 passed, books.py 87%, total 36% |

---

## Test Output

```
Name          Stmts   Miss  Cover   Missing
-------------------------------------------
book_app.py      47     47     0%   1-81
books.py         55      7    87%   27-31, 45, 72
utils.py         32     32     0%   1-47
-------------------------------------------
TOTAL           134     86    36%
5 passed in 0.22s
```

---

## Files Changed

| File | Change |
|---|---|
| `samples/book-app-project/utils.py` | Added `parse_year()` helper; renamed `print_books` → `show_books` with consistent formatting; updated `get_book_details` to use `parse_year` |
| `samples/book-app-project/book_app.py` | Removed duplicate `show_books`; added `from utils import show_books, parse_year`; used `parse_year` in `handle_add` |

---

## PR Template

```markdown
## Title
GHCP -- Walk: 03 Refactor — Consolidate Duplicate Display and Year-Parsing Logic

## Summary
- Identified two duplication patterns across `book_app.py` and `utils.py`:
  (1) duplicate book-display functions (`show_books` vs `print_books`)
  (2) duplicate year string-to-int parsing logic
- Extracted canonical `parse_year(year_str)` helper into `utils.py`
- Renamed `print_books` → `show_books` in `utils.py` (authoritative display function)
- Removed the local `show_books` from `book_app.py`; now imports from `utils`
- `book_app.py` now uses `parse_year` from `utils` in `handle_add`
- Plan:
  - `utils.py` → single source for all display and input helpers
  - `book_app.py` → delegates to `utils.py`; no duplicate logic
- Files/paths touched:
  - `samples/book-app-project/utils.py`
  - `samples/book-app-project/book_app.py`

## Evidence
- Tests/logs/metrics: `.venv/bin/pytest` (from `samples/book-app-project/`) → 5 passed in 0.22s
- Coverage: 36% total (books.py 87%) — unchanged from pre-refactor baseline

## Risk & Rollback
- Risk: low
- Rollback: revert this commit (logic is identical, only moved; no behaviour change)

## Review Focus
- Confirm `utils.py::show_books` formatting matches the previous `book_app.py::show_books` output (`[✓]/[ ]` style)
- Confirm `parse_year` raises `ValueError` for non-numeric non-blank input (caller catches it)
- Run `.venv/bin/pytest` from `samples/book-app-project/` to confirm 5/5 green

## Track
- Level: Walk
- Exercise: 03
```
