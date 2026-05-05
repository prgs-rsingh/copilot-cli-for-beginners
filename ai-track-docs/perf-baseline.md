# Performance Baseline — `books.py`

Micro-benchmark results for the core lookup methods in
`samples/book-app-project/books.py`.

## How to Reproduce

```bash
cd samples/book-app-project
python bench_books.py
```

`bench_books.py` uses Python's `timeit` module (7 independent repetitions × 10 000
calls each) so the OS scheduler and garbage collector have limited impact on any
single measurement.  Numbers are reported in **microseconds (µs) per call**.

---

## Baseline Results

**Date:** 2026-05-05  
**Environment:** Python 3.13.7 · macOS (darwin) · Apple Silicon (arm64)  
**Collection size:** 1 000 books

| Method | Scenario | min µs | mean µs | max µs | stdev µs |
|--------|----------|-------:|--------:|-------:|---------:|
| `find_book_by_title` | HIT — target is the last item (worst-case linear scan) | 57.09 | 57.52 | 59.24 | 0.78 |
| `find_book_by_title` | MISS — title not in collection (full scan) | 55.99 | 57.02 | 57.53 | 0.50 |
| `find_by_author` | Full scan, returns all matches | 58.61 | 60.59 | 62.31 | 1.23 |

> All three methods are **O(N)** linear scans over `self.books`.  For a
> collection of 1 000 books the mean call cost is ≈ 57–61 µs — well within
> interactive response budget (< 1 ms).

---

## Variance Notes

| Observation | Explanation |
|-------------|-------------|
| HIT and MISS times are nearly identical (~57 µs) | The `next()` generator short-circuits on a HIT, but the overhead of 999 `.lower()` comparisons dominates; the savings from stopping one item early are negligible at N = 1 000. |
| `find_by_author` is ~3 µs slower than `find_book_by_title` | It builds and returns a **list** of all matches rather than stopping at the first; list allocation adds a small constant overhead. |
| stdev ≤ 1.23 µs across all methods | Low variance confirms the results are stable and not dominated by GC pauses or OS scheduling noise. |
| Results are arm64-specific | x86-64 machines will show different absolute numbers; the relative ordering of methods should be the same. |

---

## Regression Threshold

Re-run `bench_books.py` after significant changes to `BookCollection`.  Flag a
regression if **mean µs increases by more than 20 %** from this baseline for
the same N.

| Method | Baseline mean | Regression threshold (> +20 %) |
|--------|--------------|-------------------------------|
| `find_book_by_title` HIT  | 57.52 µs | > 69 µs |
| `find_book_by_title` MISS | 57.02 µs | > 68 µs |
| `find_by_author`          | 60.59 µs | > 73 µs |

---

## When to Re-Baseline

- After changing the lookup implementation (e.g., swapping the list for a dict index).
- After adding new fields to `Book` that affect `asdict` / serialisation cost.
- When the Python version is upgraded.
- When the target hardware changes.
