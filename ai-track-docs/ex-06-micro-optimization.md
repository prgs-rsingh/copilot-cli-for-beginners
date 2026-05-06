# Exercise 06 — Micro-Optimization: Hoist Redundant .lower() Out of Search Loops

## Mini Prompt
Implement one micro-optimization with before/after evidence.

---

## Optimization Identified

**Target**: `books.py` — `find_book_by_title()` and `find_by_author()`

**Problem**: Both methods recompute `title.lower()` / `author.lower()` (the *search term*)
on every iteration of the loop. With N books, that is N redundant string allocations per call —
pure waste, since the search term is a constant within each call.

```python
# BEFORE — author.lower() recomputed for every book in the list
return [b for b in self.books if b.author.lower() == author.lower()]

# AFTER — author.lower() computed once, reused across all iterations
author_lower = author.lower()
return [b for b in self.books if b.author.lower() == author_lower]
```

The same pattern applies to `find_book_by_title`.

---

## Before/After Measurements

Benchmark: 10,000-book in-memory collection, `timeit` (stdlib), no disk I/O.

| Method | BEFORE (ms/call) | AFTER (ms/call) | Improvement |
|---|---|---|---|
| `find_book_by_title` (worst case, tail hit) | 0.5941 | 0.4206 | **−29%** |
| `find_by_author` (full scan, 5,000 matches) | 0.6280 | 0.4419 | **−30%** |

Benchmark command (run from `samples/book-app-project/`):
```bash
.venv/bin/python3 - <<'EOF'
import sys, timeit
sys.path.insert(0, '.')
from books import Book, BookCollection
bc = BookCollection.__new__(BookCollection)
bc.books = [Book(title=f"Book {i}", author="Same Author" if i % 2 == 0 else f"Author {i}", year=2000) for i in range(10_000)]
t1 = timeit.timeit(lambda: bc.find_book_by_title("Book 9999"), number=5000)
t2 = timeit.timeit(lambda: bc.find_by_author("Same Author"), number=2000)
print(f"find_book_by_title: {t1*1000/5000:.4f} ms/call")
print(f"find_by_author:     {t2*1000/2000:.4f} ms/call")
EOF
```

---

## Steps Run

| # | Step | Outcome |
|---|---|---|
| 1 | Read `books.py` in full; identified both search methods recomputing the search-term `.lower()` per iteration | 2 candidates found |
| 2 | Ran baseline benchmark (10k books, `timeit`, worst-case / full-scan) | `find_book_by_title` 0.5941 ms, `find_by_author` 0.6280 ms |
| 3 | Applied optimization: hoisted `title.lower()` and `author.lower()` into local variables before each loop | 2 lines changed in `books.py` |
| 4 | Ran after benchmark with same parameters | `find_book_by_title` 0.4206 ms (−29%), `find_by_author` 0.4419 ms (−30%) |
| 5 | Ran `.venv/bin/pytest -v` — 9/9 passed; `books.py` 86%, total 36% | All green |

---

## Why the Change Is Safe

1. **Pure behavioural equivalence**: `x.lower()` for the same string `x` always returns the same result. Calling it once vs N times is identical in output.
2. **No state mutation**: both methods are read-only; the optimization touches only local variable scoping.
3. **All existing tests pass**: 5 unit tests + 4 contract tests — including round-trip serialization and schema checks — remain green.
4. **Minimal diff**: 2 one-line additions; no control flow changes.

---

## Acceptance Results

| Checkpoint | Status |
|---|---|
| Optimization implemented | ✅ Pass — `title_lower` / `author_lower` hoisted in both search methods |
| Before/after evidence included | ✅ Pass — −29% and −30% on a 10k-book worst-case benchmark |
| No behaviour regression | ✅ Pass — 9/9 tests green, `books.py` 86% |

---

## Files Changed

| File | Change |
|---|---|
| `samples/book-app-project/books.py` | Hoisted `title_lower = title.lower()` before `find_book_by_title` loop; hoisted `author_lower = author.lower()` before `find_by_author` comprehension |

---

## PR Template

```markdown
## Title
GHCP -- Walk: 06 Micro-Optimization — Hoist Redundant .lower() Out of Search Loops

## Summary
- Identified `find_book_by_title` and `find_by_author` in `books.py` both recomputing
  the search-term `.lower()` on every loop iteration (N redundant allocations per call).
- Hoisted `title_lower = title.lower()` and `author_lower = author.lower()` to a local
  variable before each loop — pure behavioural equivalence, minimal diff.
- Plan: inline — single-file, 2-line change; no interface, schema, or test changes needed.
- Files/paths touched:
  - `samples/book-app-project/books.py`

## Evidence
- Benchmark (10,000-book collection, stdlib `timeit`, worst-case / full-scan):

  | Method | BEFORE | AFTER | Δ |
  |---|---|---|---|
  | `find_book_by_title` | 0.5941 ms/call | 0.4206 ms/call | −29% |
  | `find_by_author` | 0.6280 ms/call | 0.4419 ms/call | −30% |

- Tests/logs/metrics: `.venv/bin/pytest -v` → 9 passed in 0.29s
- Coverage: 36% total (books.py 86%)

## Risk & Rollback
- Risk: low — pure refactor, identical behaviour, confirmed by full test suite
- Rollback: revert this commit

## Review Focus
- Confirm `title_lower` / `author_lower` are scoped to the method (not class-level state)
- Verify the benchmark command in `ex-06-micro-optimization.md` is reproducible locally
- Run `.venv/bin/pytest -v` to confirm 9/9 green

## Track
- Level: Walk
- Exercise: 06
```
