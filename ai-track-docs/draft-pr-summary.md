# Draft PR Summary

> Ready to paste into GitHub. Replace `<branch>` with the actual PR URL after opening.

---

## Title

```
Copilot Track — Crawl: ex-00–09 book-app-project hardening
```

---

## Summary

Applied 9 incremental Crawl-track exercises to `samples/book-app-project/books.py` and its surrounding infrastructure: new tests, a readability refactor, docstrings, input validation, a micro-benchmark, dependency pinning, secret hygiene, structured logging, and CI setup. No chapter content or intentional-bug samples were modified.

**Files/paths touched:**
- `samples/book-app-project/` — `books.py`, `tests/test_books.py`, `pyproject.toml`, `bench_books.py`
- `samples/book-app-project-js/package.json`
- `samples/src/api/auth.js`
- `.gitignore`, `SECURITY.md`
- `.github/workflows/python-tests.yml`
- `scripts/run-tests.sh`
- `ai-track-docs/` — `build-test.md`, `extending-books.md`, `dependencies.md`, `perf-baseline.md`, `logging.md`, `SYSTEM-OVERVIEW.md`

---

## Review Focus

Reviewers should spend the most time here:

1. **`books.py` — `add_book` validation** — first hard boundary in this codebase. Confirm the guards (blank/whitespace title or author, non-positive year) are not overly restrictive for beginner exercises. The `use_temp_data_file` fixture ensures 6 new negative tests are fully isolated.

2. **`books.py` — structured logging** — logs are off by default (`WARNING`). Confirm no log line leaks sensitive data (only `title`, `author`, `year`, `op`, `status`, `elapsed_ms` are emitted — no passwords or keys).

3. **`.github/workflows/python-tests.yml`** — matrix covers Python 3.10–3.13. Confirm the `paths:` filter fires only on `samples/book-app-project/**` and won't trigger on unrelated chapter edits.

4. **`samples/src/api/auth.js` — JWT_SECRET** — hardcoded string replaced with `process.env.JWT_SECRET` + startup guard. Verify no chapter README cites the old literal `'your-secret-key'` as a teaching example.

5. **`.gitignore` additions** — new patterns include `.venv/`, `*.pem`, `*.key`, `*.p12`, `*_credentials.json`. Confirm nothing in the tracked tree accidentally matches.

---

## Test & Risk

**Tests:** run with `bash scripts/run-tests.sh -v`; output:

```
collected 12 items

tests/test_books.py::test_add_book PASSED                                [  8%]
tests/test_books.py::test_mark_book_as_read PASSED                       [ 16%]
tests/test_books.py::test_mark_book_as_read_invalid PASSED               [ 25%]
tests/test_books.py::test_remove_book PASSED                             [ 33%]
tests/test_books.py::test_remove_book_invalid PASSED                     [ 41%]
tests/test_books.py::test_find_by_author_returns_only_matching_books PASSED [ 50%]
tests/test_books.py::test_add_book_rejects_invalid_input[...] PASSED ×6  [100%]

12 passed in 0.08s
```

**Risk: low.** All changes are additive or isolated fixes; no shared infrastructure altered.

**Rollback by commit:**

| Exercise | SHA | Rollback |
|----------|-----|---------|
| Validation + negative tests | `41f8719` | `git revert 41f8719` |
| Secret hygiene | `dd05acc` | `git revert dd05acc` |
| Structured logging | `62b33b6` | `git revert 62b33b6` |
| CI workflow | `ece7a10` | `git revert ece7a10` or delete `python-tests.yml` |
| All others (docs, refactor, bench) | — | Safe to revert individually; `pytest tests/ -v` is the signal |

---

## Track

- **Level:** crawl
- **Exercise:** ex-00 through ex-09
- **Evidence:**
  - Test output: 12/12 passed (above)
  - Perf baseline: [perf-baseline.md](perf-baseline.md) — mean ≈ 57–61 µs/call, stdev ≤ 1.23 µs
  - Structured log spec: [logging.md](logging.md)
  - Dependency policy: [dependencies.md](dependencies.md)
  - Extending guide: [extending-books.md](extending-books.md)
  - CI matrix: `.github/workflows/python-tests.yml` (Python 3.10–3.13, `ubuntu-latest`)
  - Full review/rollback detail: [SYSTEM-OVERVIEW.md](SYSTEM-OVERVIEW.md) → "PR Summary" section

---

## Proposed Commit Message Improvements

| Current (branch) | Improved (conventional commits) |
|------------------|--------------------------------|
| `exercise-0` | `chore(ai-track): initialise SYSTEM-OVERVIEW and ai-track-docs` |
| `exercise-2` | `test(books): add test_find_by_author_returns_only_matching_books` |
| `ex-3-tiny-refactor` | `refactor(books): replace find_book_by_title loop with next() generator` |
| `exercise-4-doc-sync` | `docs(books): add docstrings and extending-books guide` |
| `ex-5-min-validation-negative-test` | `feat(books): validate add_book inputs; add parametrized negative tests` |
| `ex-6-performance-baseline` | `perf(books): add bench_books.py and record perf baseline` |
| `ex-7-deps` + `ex-7-deps2` | `chore(deps): pin pytest and Node engines; add dependencies.md` |
| `ex8-secret-hygiene` | `fix(security): remove hardcoded JWT_SECRET; harden .gitignore` |
| `ex-9-structured-logging` | `feat(books): add structured JSON logs to mutation paths` |
| `ex-9-ci-baseline` | `ci: add python-tests workflow and scripts/run-tests.sh` |

Format: `<type>(<scope>): <imperative summary>` — ≤ 72 chars, no trailing period.
