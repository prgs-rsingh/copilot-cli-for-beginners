"""Micro-benchmark for BookCollection lookup methods.

Run from the samples/book-app-project/ directory:
    python bench_books.py

Results are printed to stdout.  Numbers are microseconds (µs) per call.
"""
import timeit
import statistics
import sys
import os
import json
import tempfile

import books as bk

# Redirect DATA_FILE so the benchmark never touches the real data.json
tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
json.dump([], tmp)
tmp.close()
bk.DATA_FILE = tmp.name

# Build an in-memory collection of N books (no disk I/O during timing).
N = 1_000
col = bk.BookCollection()
for i in range(N):
    col.books.append(bk.Book(title=f"Book {i}", author=f"Author {i % 10}", year=2000 + (i % 100)))
col.save_books()


def bench(fn, *args, repeat=7, number=10_000):
    """Return per-call times in µs across `repeat` independent runs."""
    raw = timeit.repeat(lambda: fn(*args), repeat=repeat, number=number)
    return [t / number * 1e6 for t in raw]


def report(label, times):
    print(f"{label}")
    print(
        f"  n={len(times)} runs × 10 000 calls | "
        f"min={min(times):.2f}  mean={statistics.mean(times):.2f}  "
        f"max={max(times):.2f}  stdev={statistics.stdev(times):.2f}  (µs/call)"
    )


# Worst-case hit: target is the last item (generator scans all N before match).
hit_times = bench(col.find_book_by_title, f"Book {N - 1}")
# Miss: target absent, generator scans entire list.
miss_times = bench(col.find_book_by_title, "Nonexistent")
# find_by_author always scans full list.
author_times = bench(col.find_by_author, "Author 0")

print(f"\n=== BookCollection micro-benchmark  (N={N} books) ===\n")
report(f"find_book_by_title  HIT  (worst-case, last of {N})", hit_times)
report(f"find_book_by_title  MISS (not found, full scan of {N})", miss_times)
report(f"find_by_author           (full scan of {N})", author_times)
print(f"\nPython {sys.version.split()[0]} | platform: {sys.platform}")

os.unlink(tmp.name)
